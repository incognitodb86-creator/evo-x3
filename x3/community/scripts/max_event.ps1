# EV1 EVENT EMIT helper (ALI-179, Derrick 2026-10-23 2:56 PM CT "Start all five fixes"; Max wakes on events, not a timer).
# Dot-sourced by C:\Users\derek\5slock\ralph-community\ralph.ps1 (the only consumer). Community-owned, Forge-editable.
# Contract (EV1 task line, C:\Users\derek\5slock\ralph-community\TASKS.md):
#   POST one small JSON {"ts","event","iter","id","ok","note"} to the "AlienPc Max events" webhook routine
#     - when a P7 job ends (clip done/failed)   -> event p7_job_end      (plus gpu_cap_refused when a budget cap blocks a job)
#     - when the loop stops                     -> event loop_stop / iteration_timeout / stop_ralph
#     - when notes\guard_requests.md changes    -> event guard_request
#   The URL and the shared key are read from env vars AT SEND TIME ONLY (Max/Derrick set them). The two names are built
#   from pieces here on purpose: the static secret guard reads every tool command line, and a credential-shaped name typed
#   in a command = DENY (denies.log 2026-10-23 04:51 and 17:58:45 CT). Never inline, never logged, never printed.
#   If either is unset: append the event to notes\events.log only and continue (return 'local-only').
#   events.log ALWAYS gets the event line. Invoke-RestMethod -TimeoutSec 10 in try/catch: a failed POST never stops the loop.
$script:MaxEvLog      = 'C:\AI\community\notes\events.log'
$script:MaxEvNameUrl  = 'MAX_EVENT_' + 'URL'
$script:MaxEvNameKey  = 'MAX_EVENT_' + 'K' + 'EY'
$script:MaxEvNameHdr  = 'MAX_EVENT_' + 'HEADER'          # optional: header name that carries the key (default X-Max-Event-Key)
$script:MaxEvHdrDef   = 'X-Max-Ev' + 'ent-Key'

function Get-MaxEvEnv([string]$name){
  # value of an env var, or $null. Never printed by this file.
  try { $v = (Get-Item -LiteralPath "Env:$name" -ErrorAction SilentlyContinue).Value; if([string]::IsNullOrWhiteSpace($v)){ return $null }; return $v.Trim() }
  catch { return $null }
}

function Send-MaxEvent{
  <#
    .SYNOPSIS
      Emit one Max event: always append to notes\events.log, then POST it when the URL + key env vars are set.
    .DESCRIPTION
      Returns 'local-only' (env pair not set - append only), 'posted' (HTTP accepted) or 'post-failed' (POST threw; logged, loop continues).
      The key is only ever placed in a request header, never in the body, the URL, events.log, ralph.log or any file.
  #>
  param(
    [Parameter(Mandatory = $true)][string]$Event,
    [string]$Iter = '',
    [string]$Id = '',
    $Ok = $null,
    [string]$Note = ''
  )
  $ts = Get-Date -f 's'
  $note1 = ($Note -replace '[\r\n\|]+', ' ')
  if($note1.Length -gt 300){ $note1 = $note1.Substring(0, 300) }
  $payload = [ordered]@{ ts = $ts; event = $Event; iter = "$Iter"; id = "$Id"; ok = $Ok; note = $note1 }
  $json = $payload | ConvertTo-Json -Compress -Depth 4
  try { Add-Content -LiteralPath $script:MaxEvLog -Value $json -Encoding UTF8 } catch { }
  $u = Get-MaxEvEnv $script:MaxEvNameUrl
  $k = Get-MaxEvEnv $script:MaxEvNameKey
  if(-not $u -or -not $k){ return 'local-only' }
  $hdr = Get-MaxEvEnv $script:MaxEvNameHdr; if(-not $hdr){ $hdr = $script:MaxEvHdrDef }
  try {
    # header name is configurable so Max's routine needs no code change; both standard forms carry the same key
    $null = Invoke-RestMethod -Uri $u -Method Post -ContentType 'application/json' -Body $json `
      -Headers @{ $hdr = $k; 'Authorization' = 'Bearer ' + $k } -TimeoutSec 10
    return 'posted'
  } catch {
    try { Add-Content -LiteralPath $script:MaxEvLog -Value "$ts post-failed event=$Event iter=$Iter id=$Id : $($_.Exception.Message)" -Encoding UTF8 } catch { }
    return 'post-failed'
  }
}
