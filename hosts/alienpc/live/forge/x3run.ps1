# x3run.ps1 - run one bash command on the EVO-X3 over SSH (key auth, non-interactive).
# Usage: powershell -NoProfile -File C:\Users\derek\forge\x3run.ps1 '<bash>'
#        powershell -NoProfile -File C:\Users\derek\forge\x3run.ps1 -AsDerek '<bash>'   (user derekboone; use sudo -n inside when root is needed)
# Same ssh call as C:\Users\derek\gufo\x3.ps1 (x3 / x3d). Prints only the remote output; exit code is the remote command's.
# Quoting: Windows PowerShell 5.1 drops embedded double quotes when it launches powershell.exe -File, so the bash string is
# recovered from this process's raw command line (double quotes, single quotes, $ and pipes pass through intact).
param(
    [switch]$AsDerek,
    [Parameter(ValueFromRemainingArguments = $true)][string[]]$Rest
)
$ErrorActionPreference = 'Stop'
$cmd = ($Rest -join ' ')
try {
    $raw = (Get-CimInstance Win32_Process -Filter "ProcessId=$PID").CommandLine
    $m = [regex]::Match($raw, '(?i)x3run\.ps1"?\s*(.*)$', 'Singleline')
    if ($m.Success) {
        $tail = $m.Groups[1].Value.Trim()
        $tail = [regex]::Replace($tail, '(?i)^-AsDerek\s*', '')
        if ($tail.Length -ge 2 -and $tail.StartsWith('"') -and $tail.EndsWith('"')) {
            $inner = $tail.Substring(1, $tail.Length - 2)
            if ($inner.Contains('\"')) { $inner = $inner.Replace('\"', '"') }
            $tail = $inner
        }
        if ($tail.Length -gt 0) { $cmd = $tail }
    }
} catch { }
if ([string]::IsNullOrWhiteSpace($cmd)) { Write-Error 'x3run: no command given'; exit 2 }
$user = if ($AsDerek) { 'derekboone' } else { 'evo' }
$key  = Join-Path $env:USERPROFILE '.ssh\x3_alienpc_ed25519'
$b64  = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes(($cmd -replace "`r", "")))
& ssh -i $key -o BatchMode=yes -o IdentitiesOnly=yes -o ConnectTimeout=15 -o ServerAliveInterval=30 "$user@evo-x3-1.tailf242b2.ts.net" "echo $b64 | base64 -d | bash"
exit $LASTEXITCODE