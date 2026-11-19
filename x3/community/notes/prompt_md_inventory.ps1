# Inventory of every PROMPT*.md on the box (read-only): size, mtime, its rule ids, and who pins it.
$files = @(
  'C:\Users\derek\5slock\ralph-community\PROMPT.md',
  'C:\Users\derek\5slock\ralph-community\notes\rules-snapshots-2026-10-25\PROMPT-pre-RULES.md',
  'C:\Users\derek\5slock\ralph\PROMPT.md',
  'C:\Users\derek\5slock\ralph-forgeup\PROMPT.md',
  'C:\Users\derek\5slock\loop1017\PROMPT.md',
  'C:\Users\derek\5slock\ali147\PROMPT_ali147.md',
  'C:\AI\community\archive\2026-10-23-prereset\PROMPT.md'
)
foreach ($f in $files) {
  if (-not (Test-Path -LiteralPath $f)) { "MISSING $f"; continue }
  $i = Get-Item -LiteralPath $f
  $lines = @(Get-Content -LiteralPath $f)
  $ids = @($lines | Where-Object { $_ -match '^\s*\d+[a-z]?\.' } | ForEach-Object { ($_ -replace '^\s*','') -replace '^(\d+[a-z]?)\..*','$1' })
  "=== $f"
  "    bytes=$($i.Length) lines=$($lines.Count) mtime=$($i.LastWriteTime.ToString('yyyy-MM-dd HH:mm')) sha8=$((Get-FileHash -Algorithm SHA256 -LiteralPath $f).Hash.Substring(0,8))"
  "    L1: " + $lines[0].Substring(0, [Math]::Min(130, $lines[0].Length))
  "    rule ids: " + ($ids -join ' ')
  ""
}
"=== permission rules naming PROMPT.md (the deny that blocked the first pass)"
Select-String -Path 'C:\Users\derek\.pi\agent\pi-permissions.jsonc' -Pattern 'PROMPT' | ForEach-Object { "  line $($_.LineNumber): $($_.Line.Trim())" }
"=== the ralph.ps1 argv that loads it"
Select-String -Path 'C:\Users\derek\5slock\ralph-community\ralph.ps1' -Pattern 'PROMPT\.md' | ForEach-Object { "  line $($_.LineNumber): $($_.Line.Trim())" }
