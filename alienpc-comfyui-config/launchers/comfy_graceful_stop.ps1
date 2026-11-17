# ALI-156 (G5): queue-aware cmdStop for llama-swap's comfyui_auto.
# llama-swap runs cmdStop on a swap/unload; the old cmdStop was a plain taskkill that killed renders mid-job.
# This waits while ComfyUI's own /queue (ComfyUI server route) shows running or pending jobs, up to MaxWaitSec,
# then does the same taskkill as before. llama-swap's model unloadTimeout must be > MaxWaitSec.
# Usage (llama-swap.yaml): cmdStop: 'powershell -NoProfile -ExecutionPolicy Bypass -File C:\AI\director\scripts\comfy_graceful_stop.ps1 -ProcId ${PID} -Port ${PORT}'
param([Parameter(Mandatory)][int]$ProcId, [string]$Port = '', [int]$MaxWaitSec = 1800, [int]$PollSec = 10, [switch]$WhatIfKill,
      [string]$LockFile = 'C:\AI\locks\gpu-render.lock', [string]$CollectedFile = 'C:\AI\locks\gpu-render.collected',
      [string]$LogFile = 'C:\AI\director\logs\comfy-graceful-stop.log')
$log = $LogFile
function L($m){ "$(Get-Date -f 'yyyy-MM-dd HH:mm:ss') CT pid=$ProcId $m" | Add-Content $log }

# Record initial process creation time for stale-PID recycling protection (Raymond Chen, Old New Thing)
$recordedCreationTime = $null
$initProc = Get-CimInstance Win32_Process -Filter "ProcessId=$ProcId" -EA SilentlyContinue
if ($initProc) { $recordedCreationTime = $initProc.CreationDate }

if ($Port -notmatch '^\d+$') {  # ${PORT} not substituted: find the listener in the process tree (venv launcher -> child)
  $ids = @($ProcId) + @(Get-CimInstance Win32_Process -Filter "ParentProcessId=$ProcId" -EA SilentlyContinue | % ProcessId)
  $Port = (Get-NetTCPConnection -State Listen -EA SilentlyContinue | ? { $ids -contains $_.OwningProcess } | Select -First 1).LocalPort
}

# Discussion #962: wait until ComfyUI queue_remaining is 0 before stopping
$t0 = Get-Date; $waited = $false
while ($Port) {
  $busy = $null
  try {
    $p = Invoke-RestMethod "http://127.0.0.1:$Port/prompt" -TimeoutSec 5
    if ($p.exec_info -and ($p.exec_info.PSObject.Properties.Name -contains 'queue_remaining')) {
      $busy = [int]$p.exec_info.queue_remaining
    }
  } catch { }
  if ($null -eq $busy) {
    try {
      $q = Invoke-RestMethod "http://127.0.0.1:$Port/queue" -TimeoutSec 5
      $busy = @($q.queue_running).Count + @($q.queue_pending).Count
    } catch {
      L "port $Port not answering, stop now"
      break
    }
  }
  if ($busy -eq 0) { break }
  if (((Get-Date) - $t0).TotalSeconds -ge $MaxWaitSec) { L "cap ${MaxWaitSec}s reached with $busy job(s), stop anyway"; break }
  if (-not $waited) { L "render queue busy ($busy job(s)) on :$Port, waiting"; $waited = $true }
  Start-Sleep $PollSec
}
# (c) 2026-11-02 (brief 2026-11-02-2010): an empty queue is not "collected". On 2026-11-02 13:59:46 this stopped
# comfyui_auto after the queue drained but before run_queue read /history, so the batch re-rendered all 3 clips.
# Now also wait while a RENDER DRIVER (lock note run_queue / run_graph_job) holds gpu-render.lock with a live PID, until
# that driver writes gpu-render.collected with its PID (comm.mark_collected, right before its own unload) or releases
# the lock. Other lock holders (VLM judge, benches) are not waited on: they may be the reason for the swap.
function RenderLockPid {
  if (-not (Test-Path -LiteralPath $LockFile)) { return 0 }
  $raw = [IO.File]::ReadAllText($LockFile)
  if ($raw -notmatch '^\s*(\d+)\s+\S+\s+(run_queue|run_graph_job)') { return 0 }
  $lp = [int]$Matches[1]
  if (-not (Get-Process -Id $lp -EA SilentlyContinue)) { return 0 }
  if ((Test-Path -LiteralPath $CollectedFile) -and ([IO.File]::ReadAllText($CollectedFile) -match '^\s*(\d+)') -and ([int]$Matches[1] -eq $lp)) { return 0 }
  return $lp
}
$lw = $false
while ($true) {
  $lp = RenderLockPid
  if ($lp -eq 0) { break }
  if (((Get-Date) - $t0).TotalSeconds -ge $MaxWaitSec) { L "cap ${MaxWaitSec}s reached while render driver pid $lp holds the GPU lock uncollected, stop anyway"; break }
  if (-not $lw) { L "render driver pid $lp holds gpu-render.lock and has not collected, waiting"; $lw = $true }
  Start-Sleep $PollSec
}

# Discussion #962: POST /api/free to release ComfyUI VRAM and model weights
if ($Port) {
  $freeBody = '{"unload_models": true, "free_memory": true}'
  try {
    Invoke-RestMethod "http://127.0.0.1:$Port/api/free" -Method Post -Body $freeBody -ContentType "application/json" -TimeoutSec 5 | Out-Null
    L "POST /api/free sent to :$Port"
  } catch {
    try {
      Invoke-RestMethod "http://127.0.0.1:$Port/free" -Method Post -Body $freeBody -ContentType "application/json" -TimeoutSec 5 | Out-Null
      L "POST /free sent to :$Port"
    } catch { }
  }
}

L ("stop after {0:N0}s (port={1})" -f ((Get-Date) - $t0).TotalSeconds, $Port)
if ($WhatIfKill) { L "WhatIf: taskkill /T /F /PID $ProcId"; exit 0 }

# FIX 2 / 3e: verify PID is still alive, creation time matches recorded one, and is a ComfyUI python process before taskkill
$targetPids = @()
$procs = @(Get-CimInstance Win32_Process -Filter "ProcessId=$ProcId" -EA SilentlyContinue)
if ($procs.Count -gt 0) {
  $p0 = $procs[0]
  if ($recordedCreationTime -and ($p0.CreationDate -ne $recordedCreationTime)) {
    L "pid $ProcId creation time mismatch (recorded: $recordedCreationTime, current: $($p0.CreationDate)), PID was recycled; not killing $ProcId"
  } else {
    $tree = @($p0) + @(Get-CimInstance Win32_Process -Filter "ParentProcessId=$ProcId" -EA SilentlyContinue)
    $isComfy = $false
    foreach ($p in $tree) {
      $cmd = $p.CommandLine
      if ($cmd -and ($cmd -like '*main.py*') -and (($cmd -like '*ComfyUI*') -or ($Port -and ($cmd -like "*--port $Port*")))) {
        $isComfy = $true; break
      }
    }
    if ($isComfy) {
      $targetPids += $ProcId
    } else {
      L "pid $ProcId is not a ComfyUI process, not killing"
    }
  }
}

# Also check if a ComfyUI listener process is still active on $Port (e.g. child orphaned after launcher exit or PID reuse)
if ($Port -match '^\d+$') {
  $portNum = [int]$Port
  $listener = Get-NetTCPConnection -LocalPort $portNum -State Listen -EA SilentlyContinue | Select-Object -First 1
  if ($listener -and $listener.OwningProcess) {
    $lpid = [int]$listener.OwningProcess
    if ($targetPids -notcontains $lpid) {
      $lproc = Get-CimInstance Win32_Process -Filter "ProcessId=$lpid" -EA SilentlyContinue
      if ($lproc) {
        $lcmd = $lproc.CommandLine
        if ($lcmd -and ($lcmd -like '*main.py*') -and (($lcmd -like '*ComfyUI*') -or ($lcmd -like "*--port $Port*"))) {
          L "found active ComfyUI listener pid $lpid on :$Port; targeting for stop"
          $targetPids += $lpid
        }
      }
    }
  }
}

if ($targetPids.Count -eq 0) {
  if ($procs.Count -eq 0) {
    L "pid $ProcId is already terminated (no active ComfyUI listener on port '$Port')"
  }
  exit 0
}

foreach ($tpid in ($targetPids | Select-Object -Unique)) {
  if (Get-Process -Id $tpid -EA SilentlyContinue) {
    L "taskkill /T /F /PID $tpid"
    taskkill /T /F /PID $tpid | Out-Null
  }
}
exit 0
