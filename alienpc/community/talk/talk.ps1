<#
talk.ps1 - the talk-lane launcher. U3 (MAX block item 4) built it; U3c (MAX block item 6, Derrick 12:20 CT Oct 29:
"keep them separate, but I want the 2nd Sydney to have full access and authority same as main chat") makes it
full-access. The tone word for the lane name lives only in the persona file, never in this script (item 4's tone
scan enforces that), so this header says "the talk lane".

Access now equals the main chat's: this starts pi the way a plain interactive pi starts, so it loads normal
extension discovery (every package in settings.json, which for this box is pi-permission-system, pi-subagents,
pi-mobile, pi-memory, rpiv-todo, cc-safety-net), the same skills trees, the same MCP servers, the
same prompt templates and themes, the same AGENTS.md context from the same working directory, the same default
tools, and the SAME permission policy as the main chat: no PI_PERMISSION_SYSTEM_POLICY_AGENT_DIR override, so
pi-permission-system reads the user-level policy file the main chat reads (external_directory default deny with the
named allows; the secret denies read:*/.env, read:C:/AI/secrets/*, *.key, *.pem, *rclone*, */sessions/*).

It is still a separate chat. The talk-only additions are exactly two:
  1. --append-system-prompt <the talk persona file>  - tone and look live in that one file and nowhere else.
  2. its own --session-dir                            - the loop's and the main chat's sessions stay untouched.
Same --provider, --model, working directory and settings as the loop and the main chat. This script edits no config
file and writes no settings key.

What U3c REMOVES from the U3 lane: -ne (extension discovery OFF) and the forced forge-policy permission dir. The
lane can now edit files, write memory, run git, call subagents, use skills and request a render - the same
authority as the main chat - under the same permission denials.
-Restricted reproduces the pre-U3c lane exactly (-ne -e pi-permission-system -e pi-mobile plus
PI_PERMISSION_SYSTEM_POLICY_AGENT_DIR = the loop's forge-policy dir) so an A/B run of the same task is one switch.

Kept by U3c (Derrick's keep list): the youth guard and fictional-adults-only rule stay in the persona and in the
box's own checks; the GPU lock stays one render at a time across both chats - before sending anything this launcher
runs C:\AI\director\scripts\gpu_guard.ps1, the render side's own read-only guard (one rule, one implementation),
and it NEVER takes C:\AI\locks\gpu-render.lock and never calls gpu_lock.ps1, so a chat turn never fires an LLM
request into a render window; while that window is busy this lane queues (bounded wait), and -NoWait refuses
instead. A lane that renders must go through the render path that takes the lock, never around it. No secrets: the
same secret-shaped reads are denied as in the main chat.

Usage:
  .\talk.ps1 "one message"        # one turn, prints the answer, exit code = pi's
  .\talk.ps1                      # interactive chat in this terminal
  .\talk.ps1 -DryRun "x"          # print the argv that would run (persona contents are not echoed), run nothing
  .\talk.ps1 "x" -NoWait          # refuse (exit 3) instead of queueing while the GPU window is busy
  .\talk.ps1 "x" -Restricted      # the old U3 lane: extension discovery OFF, forge-policy permissions (A/B)
Switches: -PersonaFile -SessionDir -LoopDir -Provider -Model -PermExt -MobileExt -GuardPs1 -GpuLockPath -Waits
          -WaitSec -NoWait -DryRun -Restricted
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
  [switch]$DryRun,
  [switch]$Restricted          # U3c A/B: run the pre-U3c restricted lane exactly as U3 built it
)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $LoopDir                     # context parity: the loop's AGENTS.md loads from its cwd
New-Item -ItemType Directory -Force $SessionDir | Out-Null
$log = Join-Path $PSScriptRoot 'talk.log'
function Log($m) { $l = "$(Get-Date -Format s) $m"; Add-Content -LiteralPath $log -Value $l -Encoding UTF8; Write-Host $l }

if (-not (Test-Path -LiteralPath $PersonaFile)) { Log "ABORT: persona file is missing: $PersonaFile"; exit 4 }
if ($Restricted) {
  foreach ($x in @($PermExt, $MobileExt)) {
    if (-not (Test-Path -LiteralPath $x)) { Log "ABORT: extension path is missing: $x"; exit 4 }
  }
}
# Permissions (U3c): the default lane inherits the parent environment, so pi-permission-system reads the same
# user-level policy file the main chat reads - same rules, same secret denies. -Restricted restores the loop's
# forge-policy dir the way U3 did, for an A/B run. This script writes no config file; an env var is scoped to it.
if ($Restricted) {
  $env:PI_PERMISSION_SYSTEM_POLICY_AGENT_DIR = 'C:\Users\derek\.pi\forge-policy'
} else {
  Remove-Item -LiteralPath 'Env:PI_PERMISSION_SYSTEM_POLICY_AGENT_DIR' -Force -EA SilentlyContinue
}

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
if ($Restricted) {
  $a += @('-ne', '-e', $PermExt, '-e', $MobileExt)                  # the old U3 lane: discovery OFF, two pins
}
# full-access mode adds nothing here: plain discovery loads the same extensions, skills, MCP and tools as main chat
if ($Message) { $a += @($Message) }

if ($DryRun) {
  $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $PersonaFile).Hash.Substring(0, 8)
  $bytes = (Get-Item -LiteralPath $PersonaFile).Length
  $shown = $a | ForEach-Object { if ($_ -eq $persona) { '<persona {0} B sha8 {1}>' -f $bytes, $hash } else { $_ } }
  Log "DRYRUN access=$(if ($Restricted) { 'restricted' } else { 'fullaccess' }) gpu_wait=$gpuWait lock_taken=no argv: pi $($shown -join ' ')"
  exit 0
}

& pi @a
$rc = $LASTEXITCODE
Log "talk rc=$rc mode=$(if ($Message) { 'print' } else { 'interactive' }) access=$(if ($Restricted) { 'restricted' } else { 'fullaccess' }) gpu_wait=$gpuWait lock_taken=no"
exit $rc
