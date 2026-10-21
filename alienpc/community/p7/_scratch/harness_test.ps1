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
Req @{ request_id='x'; jobs=@(@{kind='review'; id='p7_ht_rank'; preset='p6'}, @{kind='review'; id='p7_ht_cmp'; pairs=@('p6_1min_ab05:seg2=p7_ht_probe:seg2')}) }; $script:calls=@(); $rrSave = ${function:ReuseRanking}; ${function:ReuseRanking} = { $null }; RunJobs '04'; ${function:ReuseRanking} = $rrSave   # pool-20261021: hermetic - a live runs\P6_RANKING.json < 18 h old would otherwise be reused (no p6_review call)
Check 'preset argv' ($script:calls[0][1] -match 'rank --preset p6 --judge qwen3vl_judge --out C:\\AI\\community\\runs\\P6_RANKING')
Check 'compare argv' ($script:calls[1][1] -match 'compare --judge qwen3vl_judge --out .*p7_ht_cmp\\review --pair p6_1min_ab05:seg2=p7_ht_probe:seg2')
Check 'review without json = ok false' (-not (Res 'p7_ht_cmp').ok)
# 6 render: checkshots rejects a bad shot list, accepts a good one; prompt reuse copies parent prompts; budget refusal
$id='p7_harnesstest_probe'; $sh="$C\shots\$id.json"
# pool-20261021: the probe is built from the POOL template; reuse from the D15 parent is skipped, reuse from a POOL run works
$base = [IO.File]::ReadAllText("$C\shots\pool_parents\p6_1min_cuts_ab05.json") | ConvertFrom-Json; $seg = @($base)[1]; $seg.id = "${id}_seg2"; $seg.antiburn = 0.7
[IO.File]::WriteAllText($sh, (ConvertTo-Json @($seg) -Depth 5), $Enc)
Req @{ request_id='x'; jobs=@(@{kind='render'; id=$id; stitch=$false; reuse_prompts=@(@{src_run='p6_1min_cuts_ab05'; src_id='p6_1min_cuts_ab05_seg2'; dst_id="${id}_seg2"})}) }; $script:calls=@(); RunJobs '05'
$r = Res $id
Check 'render ran via ComfyUI venv batch_queue --no-upload --no-stitch' ($script:calls.Count -eq 1 -and $script:calls[0][0] -eq 'C:\fake\python.exe' -and $script:calls[0][1] -match 'batch_queue\.py .*p7_harnesstest_probe --no-upload --no-stitch')
Check 'render timeout 40 min for 1 shot' ($script:calls[0][2] -eq 40)
Check 'pool: reuse from the D15 parent skipped (fresh prompts)' (($r.note -match 'prompts_reused=0') -and ($r.note -match 'reuse skipped .*p6_1min_cuts_ab05/p6_1min_cuts_ab05_seg2'))
Check 'no results.json -> ok false' (-not $r.ok)
$copied = @(Get-ChildItem "$C\runs\$id\prompts" -File | % Name) -join ','; "  copied: $copied"
$ps='p7_harnesstest_poolsrc'; $pseg = $seg.PSObject.Copy(); $pseg.id = "${ps}_seg2"; [IO.File]::WriteAllText("$C\shots\$ps.json", (ConvertTo-Json @($pseg) -Depth 5), $Enc)
New-Item -ItemType Directory -Force "$C\runs\$ps\prompts" | Out-Null; foreach($n in "${ps}_seg2_c0_long_r2v.txt","${ps}_seg2_c0_long_r2v.txt.json","${ps}_seg2_c1_long_cont.txt","${ps}_seg2_c1_long_cont.txt.json"){ [IO.File]::WriteAllText("$C\runs\$ps\prompts\$n", 'x', $Enc) }
$id3='p7_harnesstest_poolreuse'; $s3 = $seg.PSObject.Copy(); $s3.id = "${id3}_seg2"; [IO.File]::WriteAllText("$C\shots\$id3.json", (ConvertTo-Json @($s3) -Depth 5), $Enc)
Req @{ request_id='x'; jobs=@(@{kind='render'; id=$id3; stitch=$false; reuse_prompts=@(@{src_run=$ps; src_id="${ps}_seg2"; dst_id="${id3}_seg2"})}) }; RunJobs '05b'
Check 'pool: prompts reused from a POOL run (2 txt + 2 json)' ((Res $id3).note -match 'prompts_reused=4' -and (Res $id3).note -notmatch 'reuse skipped')
$id4='p7_harnesstest_d15'; $dd = [IO.File]::ReadAllText("$C\shots\p6_1min_cuts_ab05.json") | ConvertFrom-Json; $d15 = @($dd)[1]; $d15.id = "${id4}_seg2"
[IO.File]::WriteAllText("$C\shots\$id4.json", (ConvertTo-Json @($d15) -Depth 5), $Enc); Req @{ request_id='x'; jobs=@(@{kind='render'; id=$id4}) }; $script:calls=@(); RunJobs '05c'
Check 'pool: a D15 shot list is refused before any render' (((Res $id4).note -match 'checkshots BAD: .*must be POOL') -and $script:calls.Count -eq 0)
Check 'pool: PoolRun true for the POOL template copy, false for the D15 parent' ((PoolRun $ps) -and -not (PoolRun 'p6_1min_cuts_ab05'))
$bad = @($seg) | % { $x = $_.PSObject.Copy(); $x.steps = 30; $x }; $id2='p7_harnesstest_bad'; $bad[0].id = "${id2}_seg2"
[IO.File]::WriteAllText("$C\shots\$id2.json", (ConvertTo-Json @($bad) -Depth 5), $Enc)
Req @{ request_id='x'; jobs=@(@{kind='render'; id=$id2}) }; RunJobs '06'; Check 'checkshots rejects steps 30' ((Res $id2).note -match 'checkshots BAD: .*steps')
[IO.File]::WriteAllText($Budget,'{"used_min": 400, "jobs": 3}',$Enc); Req @{ request_id='x'; jobs=@(@{kind='review'; id='p7_ht_budget'; preset='p6'}) }; RunJobs '07'
Check 'budget refusal' ((Res 'p7_ht_budget').refused -eq 'budget')
# cleanup: move (not delete) the test artefacts out of the live folders
New-Item -ItemType Directory -Force C:\AI\community\p7\_scratch\harnesstest | Out-Null
foreach($p in "$C\shots\$id.json","$C\shots\$id2.json","$C\runs\$id","$C\shots\$ps.json","$C\runs\$ps","$C\shots\$id3.json","$C\runs\$id3","$C\shots\$id4.json","$C\runs\$id4"){ if(Test-Path $p){ Move-Item $p ("C:\AI\community\p7\_scratch\harnesstest\" + (Split-Path $p -Leaf) + "_" + (Get-Date -f HHmmss)) } }
"RESULT pass=$pass fail=$fail tmp=$T"
