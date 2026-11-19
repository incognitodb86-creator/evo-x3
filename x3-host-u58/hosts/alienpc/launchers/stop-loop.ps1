# stop-loop.ps1 - stop one of the Ralph loops / the overnight chain, by writing its stop file. ALI-150 v2 (findings F11, F12).
# Writing a stop file is safe: it asks the loop to stop at the end of the current step. This script starts nothing and
# deletes nothing. A stop file may be a deliberate stop by an agent or by the loop itself (ralph.ps1 writes STOP_RALPH on a
# failure, with a reason) - this script never overwrites silently: it shows what is there first and asks.
#
# Which file each loop really checks (read from the scripts, 2026-10-21):
#   finance loop   5slock\ralph\ralph.ps1            : STOP_RALPH only (it does NOT read STOP_CHAIN)
#   community loop 5slock\ralph-community\ralph.ps1  : STOP_RALPH (chain.ps1 also reads it)
#   ForgeUp loop   5slock\ralph-forgeup\ralph.ps1    : STOP_RALPH and C:\AI\locks\STOP_CHAIN
#   overnight chain C:\AI\director\scripts\overnight_chain.ps1 : C:\AI\locks\STOP_CHAIN
# Starting a loop is not offered here on purpose: start them through overnight_chain.ps1 or the supervisor.

$ErrorActionPreference = 'Continue'

$targets = [ordered]@{
    '1' = @{ name = 'finance loop';   path = 'C:\Users\derek\5slock\ralph\STOP_RALPH' }
    '2' = @{ name = 'community loop'; path = 'C:\Users\derek\5slock\ralph-community\STOP_RALPH' }
    '3' = @{ name = 'ForgeUp loop';   path = 'C:\Users\derek\5slock\ralph-forgeup\STOP_RALPH' }
    '4' = @{ name = 'overnight chain (all chains)'; path = 'C:\AI\locks\STOP_CHAIN' }
}

function Show-File($path) {
    if (Test-Path -LiteralPath $path) {
        $it = Get-Item -LiteralPath $path
        Write-Host ('    already exists, written ' + $it.LastWriteTime + ':')
        Get-Content -LiteralPath $path -ErrorAction SilentlyContinue | ForEach-Object { Write-Host ('      ' + $_) }
        return $true
    }
    Write-Host '    not present'
    return $false
}

Write-Host ''
Write-Host 'Stop a loop - this writes a stop file. The loop stops at the end of its current step.'
Write-Host 'Nothing is started and nothing is deleted.'
Write-Host ''
Write-Host '  1  finance loop      (its stop file is the only one that loop reads)'
Write-Host '  2  community loop'
Write-Host '  3  ForgeUp loop      (it also reads the chain stop file)'
Write-Host '  4  overnight chain   (C:\AI\locks\STOP_CHAIN)'
Write-Host '  anything else = do nothing'
Write-Host ''
$pick = Read-Host 'Type 1, 2, 3 or 4'

if (-not $targets.Contains($pick)) {
    Write-Host ''
    Write-Host 'OK, nothing was changed.'
    Read-Host 'Press Enter to close' | Out-Null
    exit 0
}

$t = $targets[$pick]
Write-Host ''
Write-Host ('chosen: ' + $t.name)
Write-Host ('  file: ' + $t.path)
$existed = Show-File $t.path
Write-Host ''
if ($existed) {
    Write-Host 'A stop file is already there. It may be a stop an agent or the loop put there on purpose.'
    $ok = Read-Host 'Write over it with your own stop note anyway? Type YES to overwrite, anything else leaves it alone'
    if ($ok -cne 'YES') {
        Write-Host 'Left as it was. Nothing was changed.'
        Read-Host 'Press Enter to close' | Out-Null
        exit 0
    }
}

$line = 'manual stop by Derek ' + (Get-Date -Format 's')
try {
    Set-Content -LiteralPath $t.path -Value $line -Encoding ASCII -ErrorAction Stop
    Write-Host ('  written: ' + $line)
} catch {
    Write-Host ('  COULD NOT WRITE: ' + $_.Exception.Message)
    Read-Host 'Press Enter to close' | Out-Null
    exit 1
}
Write-Host ''
Write-Host 'To undo it, use "Clear Loop Stop Files" - it shows the text and asks, per file.'
Read-Host 'Press Enter to close' | Out-Null
