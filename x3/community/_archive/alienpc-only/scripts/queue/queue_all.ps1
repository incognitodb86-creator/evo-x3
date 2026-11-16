<#
queue_all.ps1 - queue scripts for the APPROVED tests that have not run yet, in plan order.
  .\queue_all.ps1                 dry run of every not-yet-run phase (no lock, no ComfyUI, no counter bump)
  .\queue_all.ps1 -Phase2 -Go     submit ONLY the named phase(s); -Go with no phase switch does nothing
Already run, so not in the list: klein_explicit gate + N + N8 (runs\2026-10-31_klein_explicit_0010), FLUX Phase 1 (flux_p1_20261030).
Switches (plan: brain 40_projects/flux2-overnight/plans/2026-10-30-flux-full-replan.md; Klein plan 2a58aef):
  -Phase2 -Phase3 -Phase4 -Phase5 -Phase7 -Deliver   FLUX replan (queue_flux_replan.py; 4, 5, 7, Deliver print their gaps)
  -Storyboard                                        FLUX Phase 6 (queue_storyboard.py, ready arms)
  -KleinK | -KleinK0                                 Klein K (SNOFS v1.4) after the gate check passes; K0 if it failed
  -KleinN12                                          Klein N12 (after K/K0)
#>
param([switch]$Go, [switch]$Phase2, [switch]$Phase3, [switch]$Phase4, [switch]$Phase5, [switch]$Phase7, [switch]$Deliver,
      [switch]$Storyboard, [switch]$KleinK, [switch]$KleinK0, [switch]$KleinN12)
$ErrorActionPreference = 'Stop'
$py = 'C:\AI\director\.venv\Scripts\python.exe'
if (-not (Test-Path $py)) { $py = 'python' }
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$kleinRun = 'C:\AI\community\runs\2026-10-31_klein_explicit_0010'
$all = [ordered]@{
  KleinK     = @{ name = 'Klein K (SNOFS v1.4; gate check first)'; args = @("$here\queue_klein_explicit.py", '--phase', 'k', '--run-dir', $kleinRun) }
  KleinK0    = @{ name = 'Klein K0 (gate failed)';               args = @("$here\queue_klein_explicit.py", '--phase', 'k', '--k0', '--run-dir', $kleinRun) }
  KleinN12   = @{ name = 'Klein N12';                            args = @("$here\queue_klein_explicit.py", '--phase', 'n12', '--run-dir', $kleinRun) }
  Phase2     = @{ name = 'FLUX Phase 2 settings arms';           args = @("$here\queue_flux_replan.py", '--phase', '2') }
  Phase3     = @{ name = 'FLUX Phase 3 crop/angle + mask';       args = @("$here\queue_flux_replan.py", '--phase', '3') }
  Phase4     = @{ name = 'FLUX Phase 4 face refine (cond.)';     args = @("$here\queue_flux_replan.py", '--phase', '4') }
  Phase5     = @{ name = 'FLUX Phase 5 pose';                    args = @("$here\queue_flux_replan.py", '--phase', '5') }
  Storyboard = @{ name = 'FLUX Phase 6 storyboard (ready arms)'; args = @("$here\queue_storyboard.py") }
  Phase7     = @{ name = 'FLUX Phase 7 community workflows';     args = @("$here\queue_flux_replan.py", '--phase', '7') }
  Deliver    = @{ name = 'FLUX deliverable set';                 args = @("$here\queue_flux_replan.py", '--phase', 'deliver') }
}
$named = @($all.Keys | Where-Object { (Get-Variable $_ -ValueOnly).IsPresent })
if ($Go -and $named.Count -eq 0) { Write-Host 'Nothing submitted: -Go needs at least one phase switch (see header).'; exit 2 }
if ($named.Count -eq 0) { $named = @($all.Keys | Where-Object { $_ -ne 'KleinK0' }) }
$flag = if ($Go) { '--go' } else { '--dry-run' }
$rcAll = 0
foreach ($k in $named) {
  $t = $all[$k]
  Write-Host "=== $($t.name) $flag"
  & $py @($t.args + $flag)
  if ($LASTEXITCODE -ne 0) { $rcAll = $LASTEXITCODE; Write-Host "rc=$LASTEXITCODE for $($t.name)" }
}
exit $rcAll
