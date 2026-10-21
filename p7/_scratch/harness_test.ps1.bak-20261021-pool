# Offline test of the P7 harness functions in ralph.ps1 (no pi, no GPU, no llama-swap, no ComfyUI). GuardWait/RunProc are stubbed.
$ErrorActionPreference = 'Stop'
$K='C:\Users\derek\5slock\ralph-community'; $t=$null; $e=$null
$ast=[System.Management.Automation.Language.Parser]::ParseFile("$K\ralph.ps1",[ref]$t,[ref]$e)
foreach($f in $ast.FindAll({$args[0] -is [System.Management.Automation.Language.FunctionDefinitionAst]},$true)){ . ([scriptblock]::Create($f.Extent.Text)) }
$T = Join-Path $env:TEMP ("p7harness_" + (Get-Date -f 'HHmmss')); New-Item -ItemType Directory -Force $T | Out-Null
$C='C:\AI\community'; $L="$T\logs"; $Snap="$T\wfsnap"; $P7="$T\p7"; $Req="$P7\JOB_REQUEST.json"; $Jobs="$P7\jobs"; $Revs="$P7\reviews"; $Budget="$L\p7_budget.json"
$LSU='http://127.0.0.1:9'; $CPy='C:\fake\python.exe'; $Rev="$C\scripts\p6_review.py"; $BQ="$C\scripts\batch_queue.py"; $Guard='C:\AI\director\scripts\gpu_guard.ps1'
$GpuCapMin=360; $JobMax=16; $Enc=New-Object Text.UTF8Encoding $false; $script:JobStop=$false; $py='C:\Program Files\Python312\python.exe'
New-Item -ItemType Directory -Force $L,$Jobs,$Revs | Out-Null
$Prot=@("$P7\KNOBS.md",$Budget); [IO.File]::WriteAllText("$P7\KNOBS.md","rules",$Enc)
function Log($m){ "$(Get-Date -f s) $m" | Add-Content "$L\ralph.log" }
function GuardWait { $true }
$script:calls=@(); function RunProc($exe,[string[]]$argv,$id,$min){ $script:calls += ,@($exe,($argv -join ' '),$min); 0 }
$pass=0; $fail=0; function Check($name,$cond){ if($cond){ $script:pass++; "PASS $name" } else { $script:fail++; "FAIL $name" } }
function Req($obj){ [IO.File]::WriteAllText($Req, ($obj | ConvertTo-Json -Depth 6), $Enc) }
function Res($id){ [IO.File]::ReadAllText("$Jobs\$id.result.json") | ConvertFrom-Json }

# 1 protection: snapshot -> tamper -> restore + violation; new file in jobs -> violation
$s = ProtSnapshot '01'; [IO.File]::WriteAllText("$P7\KNOBS.md","tampered",$Enc); [IO.File]::WriteAllText("$Jobs\fake.result.json","{}",$Enc)
$v = @(ProtCheck $s)
Check 'prot restores tampered KNOBS.md' ([IO.File]::ReadAllText("$P7\KNOBS.md") -eq 'rules')
Check 'prot reports 2 violations' ($v.Count -eq 2)
Move-Item "$Jobs\fake.result.json" "$T\fake.result.json"
# 2 budget fail-closed
[IO.File]::WriteAllText($Budget,"not json",$Enc); Check 'corrupt budget = cap used' ([double](BudgetGet).used_min -ge 360)
[IO.File]::WriteAllText($Budget,'{"used_min": 10, "jobs": 1}',$Enc); BudgetAdd 5.3; Check 'budget adds' ([double](BudgetGet).used_min -eq 15.3)
# 3 malformed request
Req @{ request_id='x'; jobs=@() }; RunJobs '02'; Check 'zero jobs refused' ((Test-Path "$Jobs\request_iter02.result.json") -and -not (Test-Path $Req))
# 4 bad id / unknown kind / bad review
Req @{ request_id='x'; jobs=@(@{kind='render'; id='../evil'}, @{kind='paint'; id='p7_ht_kind'}, @{kind='review'; id='p7_ht_rev'; pairs=@('p6_x:seg2=..\bad')}) }; RunJobs '03'
Check 'bad id has no result' (-not (Test-Path "$Jobs\..\evil.result.json"))
Check 'unknown kind refused' ((Res 'p7_ht_kind').note -match 'unknown kind')
Check 'bad pair refused' ((Res 'p7_ht_rev').note -match 'refused')
# 5 review ok path builds the right argv
Req @{ request_id='x'; jobs=@(@{kind='review'; id='p7_ht_rank'; preset='p6'}, @{kind='review'; id='p7_ht_cmp'; pairs=@('p6_1min_ab05:seg2=p7_ht_probe:seg2')}) }; $script:calls=@(); RunJobs '04'
Check 'preset argv' ($script:calls[0][1] -match 'rank --preset p6 --judge qwen3vl_judge --out C:\\AI\\community\\runs\\P6_RANKING')
Check 'compare argv' ($script:calls[1][1] -match 'compare --judge qwen3vl_judge --out .*p7_ht_cmp\\review --pair p6_1min_ab05:seg2=p7_ht_probe:seg2')
Check 'review without json = ok false' (-not (Res 'p7_ht_cmp').ok)
# 6 render: checkshots rejects a bad shot list, accepts a good one; prompt reuse copies parent prompts; budget refusal
$id='p7_harnesstest_probe'; $sh="$C\shots\$id.json"
$base = [IO.File]::ReadAllText("$C\shots\p6_1min_ab05.json") | ConvertFrom-Json; $seg = @($base)[1]; $seg.id = "${id}_seg2"; $seg.antiburn = 0.7
[IO.File]::WriteAllText($sh, (ConvertTo-Json @($seg) -Depth 5), $Enc)
Req @{ request_id='x'; jobs=@(@{kind='render'; id=$id; stitch=$false; reuse_prompts=@(@{src_run='p6_1min_ab05'; src_id='p6_1min_ab05_seg2'; dst_id="${id}_seg2"})}) }; $script:calls=@(); RunJobs '05'
$r = Res $id
Check 'render ran via ComfyUI venv batch_queue --no-upload --no-stitch' ($script:calls.Count -eq 1 -and $script:calls[0][0] -eq 'C:\fake\python.exe' -and $script:calls[0][1] -match 'batch_queue\.py .*p7_harnesstest_probe --no-upload --no-stitch')
Check 'render timeout 40 min for 1 shot' ($script:calls[0][2] -eq 40)
Check 'prompts reused (2 txt + 2 json)' ($r.note -match 'prompts_reused=4')
Check 'no results.json -> ok false' (-not $r.ok)
$copied = @(Get-ChildItem "$C\runs\$id\prompts" -File | % Name) -join ','; "  copied: $copied"
$bad = @($seg) | % { $x = $_.PSObject.Copy(); $x.steps = 30; $x }; $id2='p7_harnesstest_bad'; $bad[0].id = "${id2}_seg2"
[IO.File]::WriteAllText("$C\shots\$id2.json", (ConvertTo-Json @($bad) -Depth 5), $Enc)
Req @{ request_id='x'; jobs=@(@{kind='render'; id=$id2}) }; RunJobs '06'; Check 'checkshots rejects steps 30' ((Res $id2).note -match 'checkshots BAD: .*steps')
[IO.File]::WriteAllText($Budget,'{"used_min": 400, "jobs": 3}',$Enc); Req @{ request_id='x'; jobs=@(@{kind='review'; id='p7_ht_budget'; preset='p6'}) }; RunJobs '07'
Check 'budget refusal' ((Res 'p7_ht_budget').refused -eq 'budget')
# cleanup: move (not delete) the test artefacts out of the live folders
New-Item -ItemType Directory -Force C:\AI\community\p7\_scratch\harnesstest | Out-Null
foreach($p in "$C\shots\$id.json","$C\shots\$id2.json","$C\runs\$id"){ if(Test-Path $p){ Move-Item $p ("C:\AI\community\p7\_scratch\harnesstest\" + (Split-Path $p -Leaf) + "_" + (Get-Date -f HHmmss)) } }
"RESULT pass=$pass fail=$fail tmp=$T"
