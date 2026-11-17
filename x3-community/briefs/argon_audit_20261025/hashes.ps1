param([string]$Out)
$b='C:\AI\community\briefs\argon_audit_20261025'
$paths = (Get-Content "$b\pre_snapshot_v2.txt" | ? { $_ -match '^[A-Z]:\\.*\|' } | % { ($_ -split '\|')[0] }) + 'C:\AI\director\config\pi\settings.json'
$r = foreach($p in $paths){ if(Test-Path $p){ $i=Get-Item $p; "$p|$($i.LastWriteTime.ToString('o'))|$((Get-FileHash $p -Algorithm SHA256).Hash)" } else { "$p|MISSING|" } }
$r += "ralph-community HEAD: $(git -C C:\Users\derek\5slock\ralph-community rev-parse --short HEAD)"
$r += "director HEAD: $(git -C C:\AI\director rev-parse --short HEAD)"
$r += "community HEAD: $(git -C C:\AI\community rev-parse --short HEAD)"
$r += "taken: $(Get-Date -Format o)"
$r | Out-File -Encoding utf8 "$b\$Out"; $r
