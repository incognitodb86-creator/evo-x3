<#
talk.ps1 - the talk-only launcher (MAX block item 4 / U3 of C:\AI\community\notes\2026-10-29-forge-cleanup-plan.md).

Starts a pi chat session that differs from the loop in exactly three ways:
  1. --append-system-prompt <the talk persona file>  - tone lives in that one file and nowhere else.
  2. its own --session-dir                            - the loop's own sessions dir is untouched.
  3. -ne -e pi-permission-system -e pi-mobile          - extension discovery is OFF, so pi-memory is OFF and this
                                                        session cannot write the loop daily logs; the permission
                                                        system stays loaded, so secret-shaped reads are denied.
Everything else is the loop's own entry: same --provider, same --model, same working directory, so the same
AGENTS.md context loads. This script edits no config file.

GPU rule (one rule, one implementation): before sending anything it runs C:\AI\director\scripts\gpu_guard.ps1,
the same read-only guard the render side uses. It NEVER takes C:\AI\locks\gpu-render.lock and never calls
gpu_lock.ps1. While that window is busy this lane queues (bounded wait) and sends nothing; -NoWait refuses
instead. One-shot turns are guarded per turn; an interactive session is guarded at start, and the persona file
tells the session never to take the lock.

Usage:
  .\talk.ps1 "one message"        # one turn, prints the answer, exit code = pi's
  .\talk.ps1                      # interactive chat in this terminal
  .\talk.ps1 -DryRun "x"          # print the argv that would run (persona contents are not echoed), run nothing
  .\talk.ps1 "x" -NoWait          # refuse (exit 3) instead of queueing while the GPU window is busy
Switches: -PersonaFile -SessionDir -Provider -Model -PermExt -MobileExt -GuardPs1 -GpuLockPath -Waits -WaitSec
#>
param(
  [string]$Message = '',
  [string]$PersonaFile = 'C:\Users\derek\5slock\ralph-community\talk\talk-persona.md',
  [string]$SessionDir  = 'C:\Users\derek\5slock\ralph-community\talk\sessions',
  [string]$LoopDir     = 'C:\Users\derek\5slock\ralph-community',
  [string]$Provider    = 'llama-swap',
  [string]$Model       = 'coding_swift15_iq3s_esp',   # the loop's entry: same llama-swap slot, same context
  [string]$PermExt     = 'C:\Users\derek\.pi\agent\npm\node_modules\pi-permission-system',
  [string]$MobileExt   = 'C:\Users\derek\.pi\agent\npm\node_modules\pi-mobile',
  [string]$GuardPs1    = 'C:\AI\director\scripts\gpu_guard.ps1',
  [string]$GpuLockPath = 'C:\AI\locks\gpu-render.lock',
  [int]$Waits = 30,
  [int]$WaitSec = 120,
  [switch]$NoWait,
  [switch]$DryRun
)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $LoopDir                     # context parity: the loop's AGENTS.md loads from its cwd
New-Item -ItemType Directory -Force $SessionDir | Out-Null
$log = Join-Path $PSScriptRoot 'talk.log'
function Log($m) { $l = "$(Get-Date -Format s) $m"; Add-Content -LiteralPath $log -Value $l -Encoding UTF8; Write-Host $l }

if (-not (Test-Path -LiteralPath $PersonaFile)) { Log "ABORT: persona file is missing: $PersonaFile"; exit 4 }
foreach ($x in @($PermExt, $MobileExt)) {
  if (-not (Test-Path -LiteralPath $x)) { Log "ABORT: extension path is missing: $x"; exit 4 }
}
# pi-permission-system reads its policy from this dir; the loop's passes set the same one, so a talk turn sees the
# same "allow by default, deny secrets" rule. Setting an env var is not a config edit; this script writes no config.
$env:PI_PERMISSION_SYSTEM_POLICY_AGENT_DIR = 'C:\Users\derek\.pi\forge-policy'

# The render window outranks a chat turn. Ask the guard, never take the lock, queue while it is held.
$gpuWait = 0; $busy = ''
while ($true) {
  $g = @(& powershell -NoProfile -ExecutionPolicy Bypass -File $GuardPs1 -LockFile $GpuLockPath 2>&1)
  $busy = if ($LASTEXITCODE -eq 0) { '' } else { ($g -join ' ') }
  if (-not $busy) { break }
  if ($NoWait) { Log "GPU_BUSY: $busy - turn not sent (-NoWait). This launcher never takes the lock."; exit 3 }
  if ($gpuWait -ge $Waits) { Log "GPU_DEFERRED: the render window outlasted $Waits waits ($busy); turn not sent, lock never taken"; exit 3 }
  Log "GPU_BUSY queues this turn ($busy); waited $gpuWait of $Waits - the render owns the GPU, this lane does not take the lock"
  Start-Sleep -Seconds $WaitSec; $gpuWait++
}

$persona = Get-Content -Raw -LiteralPath $PersonaFile
# Native argument quoting: PowerShell 5.1 builds the command line for pi naively, and a persona containing a double
# quote, backtick, dollar sign or backslash comes through word-split into chat messages (observed 2026-10-29:
# the model received its brief as user turns and the system prompt got nothing). Refuse rather than run that.
$bad = @([char]34, [char]96, '$', '\') | Where-Object { $persona.Contains($_) }
if ($bad) { Log ('ABORT: the persona file has characters that break native argv quoting: ' + ($bad -join ' ') + ' - rewrite them as plain text'); exit 4 }
$a = @()
if ($Message) { $a += @('--print') }                                  # one-shot: process the prompt and exit
$a += @('--provider', $Provider, '--model', $Model)                  # identical to ralph.ps1's entry
$a += @('--session-dir', $SessionDir)                                # talk's own session dir
$a += @('--append-system-prompt', $persona)                          # tone, from the one persona file
$a += @('-ne', '-e', $PermExt, '-e', $MobileExt)                    # pi-memory OFF; permissions and mobile ON
if ($Message) { $a += @($Message) }

if ($DryRun) {
  $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $PersonaFile).Hash.Substring(0, 8)
  $bytes = (Get-Item -LiteralPath $PersonaFile).Length
  $shown = $a | ForEach-Object { if ($_ -eq $persona) { '<persona {0} B sha8 {1}>' -f $bytes, $hash } else { $_ } }
  Log "DRYRUN gpu_wait=$gpuWait lock_taken=no argv: pi $($shown -join ' ')"
  exit 0
}

& pi @a
$rc = $LASTEXITCODE
Log "talk rc=$rc mode=$(if ($Message) { 'print' } else { 'interactive' }) gpu_wait=$gpuWait lock_taken=no"
exit $rc
