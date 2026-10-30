<#
u3c_run.ps1 - MAX block item 6 (U3c) side-by-side runner, on Max's brief (Derrick's go 5:29 PM CT Oct 29).
One task, two sides, byte-identical task text, same model and provider, same permission policy (the lane's
full-access mode removes the loop's PI_PERMISSION_SYSTEM_POLICY_AGENT_DIR override, so both sides read the
user-level policy), no GPU and no render in any task.

  side=main : pi --print --provider llama-swap --model <same> @<taskfile>   from C:\Users\derek\forge
              = a plain main-chat one-shot: no persona, default (main-chat) session dir, default tools.
  side=lane : talk.ps1 -Message '@<taskfile>'                               = the talk lane: same model entry,
              its own session dir, plus --append-system-prompt <the persona file> and nothing else.

The task text is read from task<N>.txt, {TARGET} is substituted per side (each side edits its own file), and the
per-side prompt is passed as @path: pi expands @path for the prompt argument (this is ralph.ps1's own mechanism),
which keeps argv free of quotes - the defect item 4 found in the first lane run.
#>
param(
  [Parameter(Mandatory)][int]$Task,
  [ValidateSet('main', 'lane', 'both')][string]$Side = 'both',
  [string]$Dir = 'C:\AI\community\notes\_u3c',
  [string]$Launch = 'C:\AI\community\talk\talk.ps1',
  [string]$MainCwd = 'C:\Users\derek\forge',
  [string]$Provider = 'llama-swap',
  [string]$Model = 'coding_swift15_iq3s_esp'
)
$ErrorActionPreference = 'Stop'
$new = Get-Content -Raw -LiteralPath (Join-Path $Dir "task$Task.txt")
function RunSide([string]$side) {
  $target = Join-Path $Dir ("{0}_taskB_target.txt" -f $(if ($side -eq 'lane') { 'sydney' } else { 'forge' }))
  $prompt = $new.Replace('{TARGET}', ($target -replace '\\', '/'))
  if ($prompt -ne $new -and -not (Test-Path -LiteralPath $target)) { throw "task target is missing: $target" }
  $pf = Join-Path $Dir ("task{0}_{1}.prompt.txt" -f $Task, $side)
  [IO.File]::WriteAllText($pf, $prompt)                       # same bytes on both sides except {TARGET}
  $out = Join-Path $Dir ("out_task{0}_{1}.txt" -f $Task, $side)
  $t0 = Get-Date
  if ($side -eq 'lane') {
    & powershell -NoProfile -ExecutionPolicy Bypass -File $Launch -Message "@$pf" *> $out
  }
  else {
    Push-Location -LiteralPath $MainCwd
    try { & pi --print --provider $Provider --model $Model "@$pf" *> $out } finally { Pop-Location }
  }
  $rc = $LASTEXITCODE
  $line = "task=$Task side=$side rc=$rc elapsed_s=$([int]((Get-Date) - $t0).TotalSeconds) out_bytes=$((Get-Item $out).Length) out=$out"
  Add-Content -LiteralPath (Join-Path $Dir 'manifest.txt') -Value $line -Encoding UTF8
  Write-Host $line
}
foreach ($s in @($Side)) { RunSide $s }
