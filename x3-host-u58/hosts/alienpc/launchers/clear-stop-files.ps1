# clear-stop-files.ps1 - remove a loop stop file, ONE AT A TIME, only after showing you what is in it. ALI-150 v2 (finding F11).
# The old version deleted STOP_CHAIN with one click and no word. A stop file is often deliberate: ralph.ps1 writes
# STOP_RALPH with a reason when a step fails, agents write them, overnight_chain.ps1 uses C:\AI\locks\STOP_CHAIN.
# This script asks Y/N for every file. The default (just press Enter) is KEEP. STOP_CHAIN is never removed
# without an explicit Y for that exact file. Nothing is deleted silently, and nothing is started.

$ErrorActionPreference = 'Continue'

$files = @(
    'C:\Users\derek\5slock\ralph\STOP_RALPH',
    'C:\Users\derek\5slock\ralph-community\STOP_RALPH',
    'C:\Users\derek\5slock\ralph-forgeup\STOP_RALPH',
    'C:\AI\locks\STOP_CHAIN'
)

$labels = @{
    'C:\Users\derek\5slock\ralph\STOP_RALPH'            = 'finance loop - the ONLY stop file that loop reads'
    'C:\Users\derek\5slock\ralph-community\STOP_RALPH'  = 'community loop'
    'C:\Users\derek\5slock\ralph-forgeup\STOP_RALPH'    = 'ForgeUp loop'
    'C:\AI\locks\STOP_CHAIN'                             = 'overnight chain / all chains (shared stop)'
}

Write-Host ''
Write-Host 'Clear loop stop files - each file is shown first, then you decide. Enter = KEEP it.'
Write-Host 'Removing a stop file lets that loop run again.'
Write-Host ''

foreach ($f in $files) {
    Write-Host ('--- ' + $f)
    Write-Host ('    what it stops: ' + $labels[$f])
    if (-not (Test-Path -LiteralPath $f)) {
        Write-Host '    not present - nothing to do'
        Write-Host ''
        continue
    }
    $it = Get-Item -LiteralPath $f
    Write-Host ('    written: ' + $it.LastWriteTime + '   size ' + $it.Length + ' bytes')
    Write-Host '    its text:'
    $txt = ''
    try { $txt = (Get-Content -LiteralPath $f -Raw -ErrorAction Stop) } catch { $txt = '(could not read it)' }
    if ([string]::IsNullOrWhiteSpace($txt)) { Write-Host '      (empty)' } else {
        ($txt -split "`r?`n") | ForEach-Object { Write-Host ('      ' + $_) }
    }
    Write-Host ''
    $a = Read-Host 'Remove this file? type Y to remove, anything else = KEEP'
    if ($a -eq 'Y') {
        try {
            Remove-Item -LiteralPath $f -ErrorAction Stop
            Write-Host '    removed. That loop may run again now.'
        } catch {
            Write-Host ('    could not remove: ' + $_.Exception.Message)
        }
    } else {
        Write-Host '    kept, unchanged.'
    }
    Write-Host ''
}

Write-Host 'Done. Only the files you typed Y for were removed.'
Read-Host 'Press Enter to close' | Out-Null
