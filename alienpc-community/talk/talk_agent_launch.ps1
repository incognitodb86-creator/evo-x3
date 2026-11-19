# talk_agent_launch.ps1 - relaunch the talk-lane agent (the Sydney persona chat) in its own pane.
# Reproduces the argv that pane wG:p1 was running, read from herdr pane process-info on 2026-10-29 12:33 CT:
#   node <pi cli.js> --remote --provider llama-swap --model coding_swift15_iq3s_esp
#        --append-system-prompt <the talk persona file>
# The persona is passed as a path, so the agent loads whatever the persona file says at start time.
# Nothing here edits config; nothing here touches the GPU lock.
param(
  [string]$PersonaFile = 'C:\Users\derek\5slock\ralph-community\talk\talk-persona.md',
  [string]$Cwd         = 'C:\Users\derek\sydney',
  [string]$Provider    = 'llama-swap',
  [string]$Model       = 'coding_swift15_iq3s_esp',
  [string]$Cli         = 'C:\Users\derek\AppData\Roaming\npm\node_modules\@earendil-works\pi-coding-agent\dist\bundle\cli.js'
)
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $PersonaFile)) { Write-Host "persona file missing: $PersonaFile"; exit 4 }
if (-not (Test-Path -LiteralPath $Cli))         { Write-Host "pi cli missing: $Cli"; exit 4 }
Set-Location -LiteralPath $Cwd
& node $Cli --remote --provider $Provider --model $Model --append-system-prompt $PersonaFile
exit $LASTEXITCODE
