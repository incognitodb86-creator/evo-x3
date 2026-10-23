# forgeopen (d): simulated deny. Loads PassLog from the live ralph.ps1 (AST) and runs it on a fake session file; temp log paths, no live logs touched.
$r = 'C:\Users\derek\5slock\ralph-community\ralph.ps1'; $tk=$null; $er=$null
$ast = [System.Management.Automation.Language.Parser]::ParseFile($r,[ref]$tk,[ref]$er)
$fn = $ast.FindAll({ param($x) $x -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $x.Name -eq 'PassLog' }, $true) | Select-Object -First 1
if(-not $fn){ 'PassLog not found'; exit 1 }
$d = Join-Path $env:TEMP "passlog_test"; New-Item -ItemType Directory -Force $d | Out-Null
$ActLog = "$d\forge_actions.log"; $DenyLogF = "$d\denies.log"; Remove-Item $ActLog,$DenyLogF -ErrorAction SilentlyContinue
$sess = "$d\fake.jsonl"
@(
 '{"type":"message","timestamp":"2026-10-23T19:00:00.000Z","message":{"role":"assistant","content":[{"type":"toolCall","id":"c1","name":"read","arguments":{"path":"D:/Apps/finance-app/.env"}},{"type":"toolCall","id":"c2","name":"bash","arguments":{"command":"ls C:/AI/community"}}]}}',
 '{"type":"message","timestamp":"2026-10-23T19:00:01.000Z","message":{"role":"toolResult","toolCallId":"c1","toolName":"read","content":[{"type":"text","text":"Blocked by headless guard [secret]: secrets are the one thing Forge never reads"}],"isError":true}}',
 '{"type":"message","timestamp":"2026-10-23T19:00:02.000Z","message":{"role":"toolResult","toolCallId":"c2","toolName":"bash","content":[{"type":"text","text":"notes runs scripts"}],"isError":false}}',
 '{"type":"compaction","timestamp":"2026-10-23T19:00:03.000Z","summary":"earlier: Blocked by headless guard [secret] (quoted again, must not count)"}'
) | Set-Content -Encoding utf8 $sess
. ([scriptblock]::Create($fn.Extent.Text))
$k = PassLog $sess 'TEST'
"deny count = $k (want 1)"
"--- denies.log"; Get-Content $DenyLogF
"--- forge_actions.log"; Get-Content $ActLog
if($k -eq 1 -and (Get-Content $DenyLogF | Select-String 'rule=headless-guard secret' -Quiet) -and @(Get-Content $ActLog).Count -eq 2){ 'PASSLOG TEST OK' } else { 'PASSLOG TEST FAIL'; exit 1 }
