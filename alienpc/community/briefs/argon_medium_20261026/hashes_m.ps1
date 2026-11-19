param([string]$Out)
$n='C:\AI\community\briefs\argon_medium_20261026'
$paths = @('C:\AI\community\scripts\tests\test_p6_review.py','C:\Users\derek\.pi\forge-policy\pi-permissions.jsonc','C:\AI\community\scripts\comm.py','C:\Users\derek\.pi\agent\settings.json','C:\AI\director\config\pi\settings.json','C:\AI\director\config\llama-swap.yaml','C:\Users\derek\5slock\ralph-community\ralph.ps1','C:\Users\derek\5slock\ralph-community\fix_plan.md')
$paths += Get-ChildItem C:\Users\derek\.pi,C:\Users\derek\5slock\ralph-community,C:\AI\director\config -Recurse -Depth 3 -Filter mcp.json -EA 0 | % FullName
$r = foreach($p in $paths){ if(Test-Path $p){ "$p|$((Get-Item $p).LastWriteTime.ToString('o'))|$((Get-FileHash $p -Algorithm SHA256).Hash)" } else { "$p|MISSING|" } }
$r += "ralph-community HEAD: $(git -C C:\Users\derek\5slock\ralph-community rev-parse --short HEAD)"
$r += "director HEAD: $(git -C C:\AI\director rev-parse --short HEAD)"
$r += "community HEAD: $(git -C C:\AI\community rev-parse --short HEAD)"
$r += "taken: $(Get-Date -Format o)"
$r | Out-File -Encoding utf8 "$n\$Out"; $r
