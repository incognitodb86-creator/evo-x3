# EV1 call-site test (ALI-179, CPU only, no GPU, no network, no render, no loop run).
# Three layers, each with a self-destruct probe so no check is vacuous:
#   A parse: ralph.ps1 and scripts\max_event.ps1 parse with 0 errors (the EV1 check).
#   B static: ralph.ps1 dot-sources the helper and carries all 6 emit sites (p7_job_end, gpu_cap_refused,
#     stop_ralph, iteration_timeout, guard_request, loop_stop).
#   C live sandbox: Stop-Ralph and JobResult are extracted VERBATIM from ralph.ps1 by AST and run with their
#     paths redirected to a temp folder (env pair unset = local-only, so no network), proving the emit fires
#     from the real harness code, not from a copy of it.
#   PROBE: the same scan + the same live JobResult run against a clone of ralph.ps1 with the p7_job_end line
#     deleted - the scan MUST report that site missing and NO event may fire there. If the probe passes, the
#     test is worthless and fails loudly.
# Exit 0 = all pass, 1 = a check failed.
$ErrorActionPreference = 'Stop'
$C = 'C:\AI\community'
$Ralph = 'C:\Users\derek\5slock\ralph-community\ralph.ps1'
$Helper = "$C\scripts\max_event.ps1"
$Need = @('p7_job_end', 'gpu_cap_refused', 'stop_ralph', 'iteration_timeout', 'guard_request', 'loop_stop')
$fails = @()
function Chk($name, $cond){ if($cond){ "PASS $name" } else { $script:fails += $name; "FAIL $name" } }
function ParseErrs($path){
  $t = $null; $e = $null
  $null = [System.Management.Automation.Language.Parser]::ParseInput([IO.File]::ReadAllText($path), [ref]$t, [ref]$e)
  @($e)
}
function MissingSites($text){ @($Need | Where-Object { $text -notmatch ("Send-MaxEvent -Event '" + [regex]::Escape($_) + "'") }) }
function GetFn($ast, $name){ @($ast.FindAll({ param($a) $a -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $a.Name -eq $name }, $true)) }

$src = [IO.File]::ReadAllText($Ralph)
$ast = [System.Management.Automation.Language.Parser]::ParseInput($src, [ref]$null, [ref]$null)

# --- A parse
Chk 'ralph.ps1 parses with 0 errors' (@(ParseErrs $Ralph).Count -eq 0)
Chk 'scripts\max_event.ps1 parses with 0 errors' (@(ParseErrs $Helper).Count -eq 0)
Chk 'notes\ev1_test.ps1 parses with 0 errors' (@(ParseErrs "$C\notes\ev1_test.ps1").Count -eq 0)

# --- B static sites
$miss = MissingSites $src
Chk "all 6 emit sites present (missing: $($miss -join ','))" ($miss.Count -eq 0)
Chk 'ralph.ps1 dot-sources the helper' ($src -match 'max_event\.ps1')
Chk 'ralph.ps1 emits from RunJobs iteration id' ($src -match 'JobIter')

# --- C live sandbox (real function text out of ralph.ps1, redirected paths, env pair left unset)
$tmp = Join-Path $env:TEMP ('ev1-sites-' + (New-Guid).Guid)
New-Item -ItemType Directory -Force "$tmp\jobs" | Out-Null
$K = $tmp; $Jobs = "$tmp\jobs"; $GpuCapMin = 615; $i = '99'; $script:JobIter = '99'
$Enc = New-Object Text.UTF8Encoding $false
function Log($m){ Add-Content -LiteralPath "$tmp\sandbox.log" -Value "$(Get-Date -f s) $m" -Encoding UTF8 }
function WriteJson($path, $obj){ [IO.File]::WriteAllText($path, ($obj | ConvertTo-Json -Depth 6), $Enc) }
function BudgetGet { [pscustomobject]@{ used_min = 1.0; jobs = 1 } }
. $Helper
$script:MaxEvLog = "$tmp\events.log"
foreach($nm in 'Stop-Ralph', 'JobResult'){
  $f = GetFn $ast $nm
  Chk "ralph.ps1 defines $nm" ($f.Count -eq 1)
  if($f.Count -eq 1){ Invoke-Expression $f[0].Extent.Text }
}
JobResult 'ev1_sites_s99999' @{ ok = $true; note = 'sandbox job end (CPU, no render)' }
Stop-Ralph 'ev1 sandbox stop (test only, not the real loop)'
$ev = @(Get-Content -LiteralPath "$tmp\events.log" -ErrorAction SilentlyContinue)
$job = @($ev | Where-Object { $_ -match '"event":"p7_job_end"' -and $_ -match 'ev1_sites_s99999' -and $_ -match '"ok":true' })
$stp = @($ev | Where-Object { $_ -match '"event":"stop_ralph"' -and $_ -match 'ev1 sandbox stop' })
Chk 'real JobResult text emits p7_job_end (ok=true, id, note)' ($job.Count -eq 1)
Chk 'real JobResult text wrote result.json in the sandbox' (Test-Path -LiteralPath "$tmp\jobs\ev1_sites_s99999.result.json")
Chk 'real Stop-Ralph text emits stop_ralph' ($stp.Count -eq 1)
Chk 'real Stop-Ralph text wrote the sandbox STOP_RALPH' (Test-Path -LiteralPath "$tmp\STOP_RALPH")
Chk 'sandbox events.log lines are the 6-key JSON' (@($ev | Where-Object { $o = $_ | ConvertFrom-Json; (@($o.PSObject.Properties.Name | Sort-Object) -join ',') -eq 'event,id,iter,note,ok,ts' }).Count -eq $ev.Count)
Chk 'local-only path made no network attempt (no post-failed line)' (-not ($ev -match 'post-failed'))

# --- PROBE: a clone of ralph.ps1 with the p7_job_end emit removed must FAIL the scan and emit nothing
$probe = $src -replace "[^\r\n]*Send-MaxEvent -Event 'p7_job_end'[^\r\n]*", ''
$pcp = "$tmp\ralph_probe.ps1"
[IO.File]::WriteAllText($pcp, $probe, $Enc)
$pm = MissingSites ([IO.File]::ReadAllText($pcp))
Chk 'PROBE scan reports exactly the removed site (p7_job_end)' (@($pm) -join ',' -eq 'p7_job_end')
$past = [System.Management.Automation.Language.Parser]::ParseInput($probe, [ref]$null, [ref]$null)
$pf = GetFn $past 'JobResult'
Chk 'PROBE clone still defines JobResult' ($pf.Count -eq 1)
if($pf.Count -eq 1){ Invoke-Expression $pf[0].Extent.Text }
JobResult 'ev1_probe_s99998' @{ ok = $true; note = 'probe job end, must emit nothing' }
$ev2 = @(Get-Content -LiteralPath "$tmp\events.log" -ErrorAction SilentlyContinue)
Chk 'PROBE JobResult fired NO p7_job_end (the C check can fail)' (@($ev2 | Where-Object { $_ -match 'ev1_probe_s99998' }).Count -eq 0)
Chk 'PROBE clone wrote its result.json (only the emit is gone)' (Test-Path -LiteralPath "$tmp\jobs\ev1_probe_s99998.result.json")
Chk 'PROBE clone parses clean (the removal is text-only)' (@(ParseErrs $pcp).Count -eq 0)

Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue
if($fails.Count){ "EV1_SITES_TEST FAIL: " + ($fails -join ' | '); exit 1 }
"EV1_SITES_TEST PASS sites=6 probe_caught=1 sandbox_events=$($ev.Count)"
exit 0
