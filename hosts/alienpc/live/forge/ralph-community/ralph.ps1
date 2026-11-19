# Plain capped Ralph loop for Forge. Runs pi on PROMPT.md, repeats, stops at -Max cap.
# Forge owns this file.
# Usage: .\ralph.ps1 [-Max 10] [-Model coding_swift15_iq3s] [-Section <heading>] [-GpuWaits 30] [-GpuWaitSec 120] [-GpuLockPath <lock>] [-IterationTimeoutSec 7200] [-CommandOverride <cmd>] [-LogPath <path>] [-Root <dir>]
param(
  [int]$Max = 10,
  [string]$Model = 'coding_swift15_iq3s',
  [string]$Section = '',         # 2026-11-14: work only items under "## <Section>" heading and stop when none remain open; empty = current behavior
  [int]$GpuWaits = 30,
  [int]$GpuWaitSec = 120,
  [string]$GpuLockPath = 'C:\AI\locks\gpu-render.lock',
  [int]$IterationTimeoutSec = 7200,
  [string]$CommandOverride = '',
  [string]$Root = $PSScriptRoot,  # 2026-11-05 Derrick 9:21 AM CT: loop root (PROMPT.md, fix_plan.md, logs, notes, ralph.lock); C:\AI\render for the render loop
  [string]$PromptFile = '',       # 2026-11-05 Cleanup U5: default $Root\PROMPT.md
  [string]$LogPath = '',
  [int]$PassLimitSec = 3600,  # 2026-11-02 (Derrick Q2 answer): per-pass cap 60 min (was 1500s / 25 min); effective cap = min(this, IterationTimeoutSec)
  [int]$LockPollSec = 2        # (b) 2026-11-02: GPU-lock check cadence DURING a pass (was: only at pass start)
   ,[string]$MemoryRoot = ''     # 2026-11-08 Derek GO (Sydney chat review 2026-11-07, ask 5): opt-in. Empty = today's shared brain memory (unchanged default). A path = pi-memory for every pass is rooted there, so a review of private lane transcripts never lands in fleet-visible memory.
   ,[switch]$NoSnapshot = $false
   ,[string[]]$SnapshotTargets = @('C:\AI\community|skills', 'C:\AI\render|AGENTS.md', 'C:\AI\fleet-brain|20_skills')
)
$K = [IO.Path]::GetFullPath($Root).TrimEnd('\'); Set-Location $K
$day = Get-Date -Format yyyyMMdd
$logDir = if ($LogPath) { Split-Path -Parent ([IO.Path]::GetFullPath($LogPath)) } elseif ($CommandOverride) { Join-Path $env:TEMP "ralph_override_$PID" } else { "$K\logs" }
New-Item -ItemType Directory -Force "$K\logs", "$K\sessions", "$K\notes", $logDir | Out-Null
$idx = if ($LogPath) { [IO.Path]::GetFullPath($LogPath) } else { "$logDir\ralph.log" }
$run = "$logDir\ralph-$day-$PID.log"   # index only: one line per event; full output goes to per-iteration files
function Log($m) { $l = "$(Get-Date -Format s) $m"; Add-Content -LiteralPath $idx -Value $l -Encoding UTF8; Add-Content -LiteralPath $run -Value $l -Encoding UTF8; Write-Host $l }
# Max Architect 2 2026-10-31 (Derrick 6:48 PM CT, audit F6/F13): model key self-load + single-instance lock
$env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User')

$env:PYTHONUTF8 = '1'; $env:PYTHONIOENCODING = 'utf-8'

if (-not $CommandOverride) {
  if (-not $env:LLAMA_SWAP_KEY) { $env:LLAMA_SWAP_KEY = [Environment]::GetEnvironmentVariable('LLAMA_SWAP_KEY','User') }
  if (-not $env:LLAMA_SWAP_KEY) { Log 'NO_KEY - LLAMA_SWAP_KEY missing at process and User scope; loop not started'; exit 3 }
}
$lock = "$K\logs\ralph.lock"
if (Test-Path -LiteralPath $lock) {
  $lp = ([IO.File]::ReadAllText($lock)).Trim()
  if ($lp -match '^\d+$' -and [int]$lp -ne $PID -and (Get-Process -Id ([int]$lp) -EA SilentlyContinue)) { Log "ALREADY_RUNNING pid $lp - second loop not started"; exit 4 }
  Log "stale ralph.lock (pid $lp not alive) - taking it"
}
Set-Content -LiteralPath $lock -Value $PID -Encoding ASCII
$prevItem = $null; $stall = 0; $stopReason = ''


# Forge busy rule / GPU lock rule
function GpuBusy {   # gpu_guard.ps1's lock rule, same semantics on purpose (one rule, one implementation)
  if (-not (Test-Path -LiteralPath $GpuLockPath)) { return '' }
  $raw = [IO.File]::ReadAllText($GpuLockPath)
  if ($raw -match '(\d+)') {
    if (Get-Process -Id ([int]$Matches[1]) -EA SilentlyContinue) { return "lock held by live pid $($Matches[1])" }
    return ''   # a dead PID is a stale lock: ignored exactly as gpu_guard.ps1 does, so it never blocks a render forever
  }
  return "lock $GpuLockPath present without a pid"
}
# (b) 2026-11-02 (brief 2026-11-02-2010, Derek GO 8:19 PM CT): the pass start check was not enough - on 2026-11-02 the L5
# launch pass kept calling the LLM through llama-swap for ~45 min after its own detached run_queue took the lock, and each
# call swapped comfyui_auto out. Now the lock is checked every $LockPollSec s while pi runs; when a lock appears whose PID is
# NOT inside this pass's process tree (a detached render, WMI parent), the pass ends at once so pi sends no further request.
# A lock held by a pi child (a non-detached render pi is waiting on) does not end the pass: pi is blocked, not calling.
function LockPid {
  if (-not (Test-Path -LiteralPath $GpuLockPath)) { return 0 }
  $raw = [IO.File]::ReadAllText($GpuLockPath)
  if ($raw -match '(\d+)') { return [int]$Matches[1] }
  return -1
}
function InTree([int]$Child, [int]$Root) {
  $cur = $Child
  for ($n = 0; $n -lt 32 -and $cur -gt 0; $n++) {
    if ($cur -eq $Root) { return $true }
    $p = Get-CimInstance Win32_Process -Filter "ProcessId=$cur" -EA SilentlyContinue
    if (-not $p) { return $false }
    $cur = [int]$p.ParentProcessId
  }
  return $false
}

function Invoke-StartupSnapshot([string]$Sec, [string[]]$Targets) {
  $secLabel = if ($Sec) { $Sec.Trim() } else { 'all' }
  $ts = Get-Date -Format 'yyyy-MM-ddTHH:mm:ss'
  foreach ($entry in $Targets) {
    if (-not $entry -or $entry -notmatch '\|') { continue }
    $parts = $entry -split '\|', 2
    $repoPath = $parts[0]; $relPath = $parts[1]
    try {
      if (-not (Test-Path -LiteralPath $repoPath)) { Log "SNAPSHOT skip missing repo $repoPath"; continue }
      $dirty = @(& git -C $repoPath status --porcelain -- $relPath 2>$null)
      if ($dirty.Count -gt 0) {
        & git -C $repoPath add -- $relPath | Out-Null
        if ($LASTEXITCODE -ne 0) { Log "SNAPSHOT warn git add failed $repoPath ($relPath)"; continue }
        & git -C $repoPath commit --only $relPath -m "snapshot before ralph $secLabel $ts" | Out-Null
        if ($LASTEXITCODE -eq 0) {
          $newSha = (& git -C $repoPath rev-parse --short HEAD 2>$null)
          Log "SNAPSHOT committed $repoPath ($relPath) sha=$newSha"
        } else {
          $curSha = (& git -C $repoPath rev-parse --short HEAD 2>$null)
          Log "SNAPSHOT commit_skipped_or_failed $repoPath ($relPath) head=$curSha"
        }
      } else {
        $curSha = (& git -C $repoPath rev-parse --short HEAD 2>$null)
        Log "SNAPSHOT clean $repoPath ($relPath) head=$curSha"
      }
    } catch {
      Log "SNAPSHOT error $repoPath ($relPath): $($_.Exception.Message)"
    }
  }
}

if (-not $NoSnapshot) { Invoke-StartupSnapshot -Sec $Section -Targets $SnapshotTargets }

function Get-TopOpenItem([string]$PlanPath, [string]$Sec = '') {
  # Skip - [x], - [PARTIAL], - [BLOCKED], and any - [ ] item whose indented sub-bullets already record PARTIAL or BLOCKED.
  # When -Sec is given, scan only items under that "## <Sec>" heading until the next "## " heading.
  $lines = @(Get-Content -LiteralPath $PlanPath -Encoding UTF8 -EA SilentlyContinue)
  $startIdx = 0
  $endIdx = $lines.Count
  if ($Sec) {
    $secTrim = $Sec.Trim()
    $pat = '^\s*##\s+' + [regex]::Escape($secTrim) + '(?:\s|\(|$)'
    $found = $false
    for ($k = 0; $k -lt $lines.Count; $k++) {
      if (-not $found) {
        if ($lines[$k] -match $pat) { $found = $true; $startIdx = $k + 1 }
      } elseif ($lines[$k] -match '^\s*##\s+') {
        $endIdx = $k; break
      }
    }
    if (-not $found) { return $null }
  }
  for ($idx = $startIdx; $idx -lt $endIdx; $idx++) {
    if ($lines[$idx] -match '^\s*- \[ \]') {
      $blocked = $false
      for ($j = $idx + 1; $j -lt $endIdx; $j++) {
        if ($lines[$j] -match '^\s*-\s*\[') { break }
        if ($lines[$j] -match '^\s*#') { break }
        if ($lines[$j] -match '^\s+-\s*(PARTIAL|BLOCKED)\b') { $blocked = $true; break }
      }
      if (-not $blocked) { return $lines[$idx] }
    }
  }
  return $null
}

for ($i = 1; $i -le $Max; $i++) {
  Log "iter $i of $Max start"
  $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User')
  # the render window is the one thing that outranks a pass: defer, bounded, and never fire an LLM request into it
  $gpuWait = 0; $busy = GpuBusy
  while ($busy -and $gpuWait -lt $GpuWaits) {
    if ($gpuWait -eq 0 -or ($gpuWait % 5) -eq 0) { Log "iter $i : GPU_BUSY defers the pass ($busy) - no LLM request while a render runs; waited $gpuWait of $GpuWaits" }
    Start-Sleep -Seconds $GpuWaitSec; $gpuWait++; $busy = GpuBusy
  }
  if ($busy) { Log "iter $i : GPU_DEFERRED - the render window outlasted $GpuWaits waits ($busy); skipping this pass, no LLM request"; continue }
  if ($gpuWait -gt 0) { Log "iter $i : GPU_CLEAR after $gpuWait waits" }
  $busyFlag = [int][bool]$busy

  $iterLogPath = "$logDir\iter-$day-{0:d2}.log" -f $i
  $iterLogTmp = "$logDir\iter-$day-{0:d2}.tmp.log" -f $i
  if (Test-Path -LiteralPath $iterLogTmp) { Remove-Item -LiteralPath $iterLogTmp -Force -EA SilentlyContinue }

  $cmdStr = if ($CommandOverride) { $CommandOverride } else {
$effectivePromptFile = if ($PromptFile) { [IO.Path]::GetFullPath($PromptFile) } else { "$K\PROMPT.md" }
    "pi --print --provider llama-swap --model $Model --no-session `"@$effectivePromptFile`""
  }

  # P-F2 shared fleet memory (GAP1, brief 2026-10-31-1050-max-gap-fixes): this pass's pi reads/writes the brain's shared memory folder.
  # Process scope on purpose - NOT a User/Machine env var, NOT settings.json - so Sydney's talk session stays on pi-memory off and
  # nothing of hers is ever written to 25_memory (25_memory/README.md rule 1). Authority: Derrick 9:48 AM CT; Max's words, GAP1.
  $env:PI_MEMORY_DIR = if ($MemoryRoot) { [IO.Path]::GetFullPath($MemoryRoot) } else { 'C:\AI\fleet-brain\25_memory\shared' }
  Log "iter $i : PI_MEMORY_DIR=$env:PI_MEMORY_DIR (process scope, this pass only)"
  $psi = [System.Diagnostics.ProcessStartInfo]::new()
  $psi.FileName = "cmd.exe"
  $sectionNote = if ($Section) { " Work ONLY items under section '## $Section'." } else { '' }
  if (-not $CommandOverride) { $psi.Arguments = "/c $cmdStr ""Loop root is $K\. Relative paths in PROMPT.md (fix_plan.md, notes\, logs\) mean $K\ (read and update $K\fix_plan.md, NOT $([IO.Path]::GetDirectoryName($effectivePromptFile))\fix_plan.md).$sectionNote"" > `"$iterLogTmp`" 2>&1" } else { $psi.Arguments = "/c $cmdStr > `"$iterLogTmp`" 2>&1" }
  $psi.WorkingDirectory = $K
  $psi.UseShellExecute = $false
  $psi.CreateNoWindow = $true

  # Max 12:20: heartbeat + progress-line guard (Derrick 12:17 item 5)
  $hb = "$K\notes\heartbeat.txt"; $prog = "$K\notes\progress.md"
  $topItem = Get-TopOpenItem "$K\fix_plan.md" $Section
  if ($topItem) { $topItem = $topItem.Trim(); if ($topItem.Length -gt 90) { $topItem = $topItem.Substring(0,90) } } else { $topItem = '(none)' }
  if ($topItem -eq '(none)') { $secMsg = if ($Section) { " in section '$Section'" } else { '' }; Log "iter $i : PLAN_COMPLETE - no open item$secMsg, loop stopped"; "iter=$i max=$Max done=true reason=plan_complete section=$Section" | Set-Content -LiteralPath "$logDir\DONE.txt" -Encoding UTF8; $stopReason = 'plan_complete'; break }  # F4
  $progBefore = if (Test-Path -LiteralPath $prog) { (Get-Item -LiteralPath $prog).LastWriteTimeUtc } else { [datetime]::MinValue }
  $passCap = [Math]::Min($PassLimitSec, $IterationTimeoutSec)
  "$(Get-Date -Format s) iter=$i state=start cap=${passCap}s item=$topItem" | Set-Content -LiteralPath $hb -Encoding UTF8
  if ($topItem -match '^- \[ \] \[render\]') { $psi.WorkingDirectory = 'C:\AI\render'; if (-not $CommandOverride) { $psi.Arguments = "/c $cmdStr ""Loop root is $K\. Relative paths in PROMPT.md (fix_plan.md, notes\, logs\) mean $K\ (read and update $K\fix_plan.md, NOT $([IO.Path]::GetDirectoryName($effectivePromptFile))\fix_plan.md).$sectionNote"" > `"$iterLogTmp`" 2>&1" }; Log "iter $i : [render] item - cwd C:\AI\render" }  # 2026-11-05 Derrick: render rules load only from C:\AI\render\AGENTS.md
  # [render] tag: remove this line once no [render] items are left in ralph-community\fix_plan.md (new render items go to C:\AI\render via -Root; Derrick 2026-11-05 9:21 AM CT)
  $proc = [System.Diagnostics.Process]::Start($psi)
  $deadline = (Get-Date).AddSeconds($passCap); $timedOut = $false; $lockEnd = ''
  while (-not $proc.WaitForExit($LockPollSec * 1000)) {
    $b = GpuBusy
    if ($b) { $lp = LockPid; if ($lp -le 0 -or -not (InTree $lp $proc.Id)) { $lockEnd = $b; break } }
    if ((Get-Date) -ge $deadline) { $timedOut = $true; break }
  }

  if ($lockEnd) {
    Log "iter $i : GPU_LOCK_MIDPASS ($lockEnd) - render window opened outside this pass; ending the pass now (pi tree PID $($proc.Id)) so no LLM request reaches llama-swap while the lock is held"
    & taskkill /PID $proc.Id /T /F | Out-Null
    $proc.WaitForExit(3000) | Out-Null
    $piRc = 125
  } elseif ($timedOut) {
    Log "iter $i : ITERATION_TIMEOUT after ${passCap}s - killing process tree PID $($proc.Id)..."
    & taskkill /PID $proc.Id /T /F | Out-Null
    $proc.WaitForExit(3000)
    $piRc = 124
  } else {
    $piRc = $proc.ExitCode
  }

  if (Test-Path -LiteralPath $iterLogTmp) {
    Move-Item -LiteralPath $iterLogTmp -Destination $iterLogPath -Force -EA SilentlyContinue
  }

  if ($piRc -ne 0) {
    Log "iter $i : PI_NONZERO rc=$piRc - pass text in $iterLogPath"
  } else {
    Log "iter $i : pass complete rc=0"
  }

  $sha = (& git -C $K rev-parse --short HEAD 2>$null)
  $progAfter = if (Test-Path -LiteralPath $prog) { (Get-Item -LiteralPath $prog).LastWriteTimeUtc } else { [datetime]::MinValue }
  if ($progAfter -le $progBefore) { Add-Content -LiteralPath $prog -Encoding UTF8 -Value "- $(Get-Date -Format s) [ralph.ps1 auto] iter $i rc=$piRc head=$sha item: $topItem (model wrote no progress line)"; Log "iter $i : progress line written by harness" }
  "$(Get-Date -Format s) iter=$i state=end rc=$piRc head=$sha item=$topItem" | Set-Content -LiteralPath $hb -Encoding UTF8
  "iter=$i max=$Max pi_rc=$piRc gpu_wait=$gpuWait gpu_busy=$busyFlag" | Set-Content -LiteralPath "$logDir\DONE.txt" -Encoding UTF8
  # F5: stop when the same item is still the top open item after two passes in a row (no progress)
  $afterItem = Get-TopOpenItem "$K\fix_plan.md" $Section
  if ($afterItem) { $afterItem = $afterItem.Trim(); if ($afterItem.Length -gt 90) { $afterItem = $afterItem.Substring(0,90) } } else { $afterItem = '(none)' }
  if ($afterItem -ne '(none)' -and $afterItem -eq $topItem) { $stall++ } else { $stall = 0 }
  $prevItem = $topItem
  if ($stall -ge 2) { Log "iter $i : NO_PROGRESS on same item twice - stopped ($topItem)"; "iter=$i max=$Max done=true reason=no_progress" | Set-Content -LiteralPath "$logDir\DONE.txt" -Encoding UTF8; $stopReason = 'no_progress'; break }
  Start-Sleep -Seconds 2
}
if (-not $stopReason) {
  Log "max iterations ($Max) reached - loop stopped at cap"
  "iter=$Max max=$Max done=true" | Set-Content -LiteralPath "$logDir\DONE.txt" -Encoding UTF8
}
Remove-Item -LiteralPath $lock -Force -EA SilentlyContinue
exit 0
