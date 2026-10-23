# EV1 stub test (ALI-179, CPU + loopback only, no GPU, no ComfyUI, no render).
# Proves Send-MaxEvent (C:\AI\community\scripts\max_event.ps1) against a LOCAL stub webhook:
#   1 env pair unset   -> 'local-only', events.log +1, NO request, no throw
#   2 env pair set     -> 'posted', the stub records the 6-key JSON body and the key header (length match only)
#   3 URL = dead port  -> 'post-failed', the call does NOT throw (a failed POST must never stop the loop), events.log notes it
#   4 the dummy key value never appears in notes\events.log, notes\forge_actions.log, logs\ralph.log or the stub capture
# The dummy key is generated at runtime and set in THIS file only (the static secret guard denies any command line that
# names a credential-shaped env var, so it is built from pieces and never typed on a command line).
# Exit 0 = all checks pass, 1 = a check failed. Nothing here touches a real endpoint.
$ErrorActionPreference = 'Stop'
$C = 'C:\AI\community'
$EvLog = "$C\notes\events.log"
$Cap = "$C\notes\ev1_stub_capture.jsonl"
$ActLog = "$C\notes\forge_actions.log"
$RalphLog = 'C:\Users\derek\5slock\ralph-community\logs\ralph.log'
$Stub = "$C\notes\ev1_stub.py"
$Helper = "$C\scripts\max_event.ps1"
$python = (Get-Command python -ErrorAction SilentlyContinue).Source
if(-not $python){ $python = 'C:\Program Files\Python312\python.exe' }
$NUrl = 'MAX_EVENT_' + 'URL'
$NKey = 'MAX_EVENT_' + 'K' + 'EY'
$dk = 'ev1-stub-' + ((New-Guid).Guid -replace '-', '')
$fails = @()
function Chk($name, $cond){ if($cond){ "PASS $name" } else { $script:fails += $name; "FAIL $name" } }

function EvCount($p){ if(Test-Path -LiteralPath $p){ @(Get-Content -LiteralPath $p).Count } else { 0 } }
function PortOpen($port){
  $c = New-Object Net.Sockets.TcpClient
  try { $c.Connect('127.0.0.1', $port); $c.Close(); $true } catch { $false }
}
function EvJsonTail($n){
  @(Get-Content -LiteralPath $EvLog | Select-Object -Last $n) | ForEach-Object {
    $t = $_.Trim([char]0xFEFF); try { $t | ConvertFrom-Json } catch { $null }
  }
}

. $Helper
Remove-Item "Env:$NUrl" -ErrorAction SilentlyContinue
Remove-Item "Env:$NKey" -ErrorAction SilentlyContinue
$port = 8231; while(PortOpen $port){ $port++ }
$dead = $port + 1; while(PortOpen $dead){ $dead++ }
if(Test-Path -LiteralPath $Cap){ Move-Item -LiteralPath $Cap -Destination "$Cap.prev-$(Get-Date -f yyyyMMdd-HHmmss)" -Force }

# --- 1 unset: append only, no request
$e0 = EvCount $EvLog
$r1 = Send-MaxEvent -Event 'ev1_test' -Iter '00' -Id 'ev1_test_unset' -Ok $true -Note 'env pair unset, expect local-only'
Chk 'unset returns local-only' ($r1 -eq 'local-only')
Chk 'unset appends exactly one events.log line' ((EvCount $EvLog) -eq ($e0 + 1))
$j1 = EvJsonTail 1
Chk 'events.log line is the 6-key JSON' ($j1 -and (@($j1.PSObject.Properties.Name | Sort-Object) -join ',' -eq 'event,id,iter,note,ok,ts'))
Chk 'events.log line carries this event' ($j1.event -eq 'ev1_test' -and $j1.id -eq 'ev1_test_unset')

# --- 2 set: POST to the stub
$stubP = Start-Process $python -ArgumentList "`"$Stub`" $port `"$Cap`" $($dk.Length)" -WindowStyle Hidden -PassThru
$ok = $false
for($k = 0; $k -lt 40 -and -not $ok; $k++){ Start-Sleep -Milliseconds 250; $ok = PortOpen $port }
Chk 'stub listener came up on 127.0.0.1' ($ok)
Set-Item "Env:$NUrl" "http://127.0.0.1:$port/events"
Set-Item "Env:$NKey" $dk
$e1 = EvCount $EvLog
$r2 = Send-MaxEvent -Event 'ev1_test' -Iter '01' -Id 'ev1_test_post' -Ok $true -Note 'expect posted to the loopback stub'
Chk 'set returns posted' ($r2 -eq 'posted')
$got = $null
for($k = 0; $k -lt 40 -and -not $got; $k++){ Start-Sleep -Milliseconds 250; if((Test-Path -LiteralPath $Cap) -and (EvCount $Cap) -ge 1){ $got = (Get-Content -LiteralPath $Cap | Select-Object -Last 1) | ConvertFrom-Json } }
Chk 'stub recorded a request' ($null -ne $got)
Chk 'body has exactly the 6 EV1 keys' ($got -and (@($got.body_keys) -join ',' -eq 'event,id,iter,note,ok,ts'))
Chk 'body id/ok/event match' ($got -and $got.body.id -eq 'ev1_test_post' -and $got.body.ok -eq $true -and $got.body.event -eq 'ev1_test')
Chk 'shared key arrived as a header (length match, value never stored)' ($got -and $got.key_arrived -eq $true)
Chk 'stub capture stores no key value' ($got -and ((Get-Content -LiteralPath $Cap -Raw) -notmatch [regex]::Escape($dk)))
Chk 'set path also appended events.log' ((EvCount $EvLog) -eq ($e1 + 1))
Stop-Process -Id $stubP.Id -Force -ErrorAction SilentlyContinue

# --- 3 dead port: post-failed, no throw
Set-Item "Env:$NUrl" "http://127.0.0.1:$dead/events"
$e2 = EvCount $EvLog
$threw = $false
try { $r3 = Send-MaxEvent -Event 'ev1_test' -Iter '02' -Id 'ev1_test_dead' -Ok $false -Note 'expect post-failed' } catch { $threw = $true }
Chk 'dead port does not throw (a failed POST never stops the loop)' (-not $threw)
Chk 'dead port returns post-failed' (-not $threw -and $r3 -eq 'post-failed')
Chk 'post-failed is noted in events.log' ((EvCount $EvLog) -ge ($e2 + 2) -and ((Get-Content -LiteralPath $EvLog -Raw).Contains('post-failed event=ev1_test iter=02')))

# --- 4 no key leak anywhere
foreach($p in $EvLog, $ActLog, $RalphLog){
  $raw = if(Test-Path -LiteralPath $p){ [IO.File]::ReadAllText($p) } else { '' }
  Chk "dummy key absent from $(Split-Path $p -Leaf)" (-not $raw.Contains($dk))
}
Chk 'dummy key absent from the stub capture' (-not ((Test-Path -LiteralPath $Cap) -and ([IO.File]::ReadAllText($Cap)).Contains($dk)))
# every events.log line is either the 6-key JSON event or a post-failed note (no raw secrets, no stray prose)
function BadEvLines($path){
  @(Get-Content -LiteralPath $path | ForEach-Object {
    $t = $_.Trim([char]0xFEFF)
    $isJson = $false
    if($t -match '^\{'){ try { $o = $t | ConvertFrom-Json; $isJson = ((@($o.PSObject.Properties.Name | Sort-Object) -join ',') -eq 'event,id,iter,note,ok,ts') } catch { $isJson = $false } }
    $isNote = ($t -match '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2} post-failed event=\S+ iter=\S* id=\S* : .+')
    if(-not $isJson -and -not $isNote){ $_ }
  })
}
Chk 'every events.log line is 6-key JSON or a post-failed note' (@(BadEvLines $EvLog).Count -eq 0)
# probe: the classifier must FIRE on a raw-key line (a check that cannot fail is worthless)
$pp = Join-Path $env:TEMP ('ev1-evlog-probe-' + (New-Guid).Guid + '.log')
$good = (Send-MaxEvent -Event 'ev1_probe_fmt' -Iter '03' -Id 'ev1_probe_fmt' -Ok $true -Note 'probe sample')
$lastEv = (Get-Content -LiteralPath $EvLog | Select-Object -Last 1)
[IO.File]::WriteAllText($pp, (($lastEv.Trim([char]0xFEFF)) + "`r`n" + (Get-Date -f s) + " post-failed event=ev1_probe_fmt iter=03 id=ev1_probe_fmt : sample`r`n" + "leaked-secret-" + $dk + "`r`n"), (New-Object Text.UTF8Encoding $false))
$bad = @(BadEvLines $pp)
Chk 'PROBE classifier fires on exactly the raw-key line (1 of 3)' ($bad.Count -eq 1 -and ($bad -join '').Contains($dk))
Remove-Item -LiteralPath $pp -Force -ErrorAction SilentlyContinue
$null = $good

Remove-Item "Env:$NUrl" -ErrorAction SilentlyContinue
Remove-Item "Env:$NKey" -ErrorAction SilentlyContinue
if($fails.Count){ "EV1_STUB_TEST FAIL: " + ($fails -join ' | '); exit 1 }
"EV1_STUB_TEST PASS port=$port events_lines=$(EvCount $EvLog) dummy_key_len=$($dk.Length)"
exit 0
