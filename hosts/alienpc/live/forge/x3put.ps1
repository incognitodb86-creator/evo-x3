# x3put.ps1 - push a local text file to the EVO-X3 over the same SSH route as x3run.ps1.
# Usage: powershell -NoProfile -File C:\Users\derek\forge\x3put.ps1 <local-file> <remote-path>
#   remote path: absolute ('/home/evo/AI/forge/records/U58/PLAN.md') or '~'-relative ('~/AI/forge/x.md').
# Two MSYS (Git bash) quoting traps on this box are handled:
#   1. a slash-leading argument of a Windows program is rewritten to '<git-install-dir>/...'. The prefix is
#      not fixed (this session: 'C:/Program Files/Git', other sessions: a scoop .../install path), and the
#      rewrite happens at powershell.exe startup, so no script text can undo it. Therefore the destination
#      is NOT passed as a slash-leading argument: give it in colon form, e.g.
#        home:evo:AI:forge:records:U58:PLAN.md   -> $HOME/AI/forge/records/U58/PLAN.md
#        47home:evo:AI:forge:x.md                -> /home/evo/AI/forge/x.md (leading '47' = octal '/')
#      and it is rebuilt on the far side with tr.
#   2. a literal '/' inside the script text sent to the far shell gets the same rewrite, so the script
#      never contains a slash: commands are built in bash from $HOME + the decoded destination, and the
#      payload (base64 - its alphabet has no '/') is written through a quoted here-doc. Commands go in as
#      `ssh host bash -s` + stdin. The result is verified by decoding the file back on the far side.
param(
    [Parameter(Mandatory = $true, Position = 0)][string]$LocalPath,
    [Parameter(Mandatory = $true, Position = 1)][string]$RemoteColonPath
)
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $LocalPath)) { Write-Error "x3put: no such local file: $LocalPath"; exit 2 }
if ($RemoteColonPath -notmatch '^(47)?[A-Za-z0-9._-]+(:[A-Za-z0-9._-]+)+$') {
    Write-Error "x3put: remote path must be colon form: 'home:evo:AI:forge:x.md' (under the login home) or '47home:evo:AI:forge:x.md' (absolute)"; exit 2
}
$bytes = [IO.File]::ReadAllBytes((Resolve-Path -LiteralPath $LocalPath).ProviderPath)
$payload = [Convert]::ToBase64String($bytes)
if ($payload.Length -gt 100000) { Write-Error "x3put: payload too large for one command ($($bytes.Length) bytes)"; exit 2 }
$lines = New-Object System.Collections.Generic.List[string]
$lines.Add('set -e')
$lines.Add("enc='$RemoteColonPath'")
$lines.Add('p=$(printf "%s" "$enc" | sed "s^47^:^; s^:^x^g")')   # ':' -> 'x' (no slash in the script text at all)
$lines.Add('dst=$(printf "%s" "$p" | sed "s^x^/^g")')             # every 'x' separator -> '/'
$lines.Add('case "$dst" in /*) ;; *) echo "x3put: bad destination: $dst"; exit 2;; esac')
$lines.Add('mkdir -p "$(dirname "$dst")"')
$lines.Add('cat > "$dst" <<' + "'X3EOF'")
$lines.Add($payload)
$lines.Add('X3EOF')
# decode the payload in place when the destination is a .py/.sh script, so it can be run directly
if ($LocalPath -match '\.(py|sh)$') {
  $lines.add('tmpd=$(mktemp); base64 -d < "$dst" > "$tmpd" && mv "$tmpd" "$dst"')
}
$lines.Add('got=$(base64 -d < "$dst" | wc -c)')
if ($bytes.Length -le 200) { $lines.Add('head -3 "$dst"') }
$lines.Add('test "$got" -eq ' + $bytes.Length + ' && echo "x3put OK: $dst ($got bytes verified)"')
$key = Join-Path $env:USERPROFILE '.ssh\x3_alienpc_ed25519'
Write-Output ($lines -join "`n") | & ssh -i $key -o BatchMode=yes -o IdentitiesOnly=yes -o ConnectTimeout=15 -o ServerAliveInterval=30 "evo@evo-x3-1.tailf242b2.ts.net" "bash -s"
exit $LASTEXITCODE
