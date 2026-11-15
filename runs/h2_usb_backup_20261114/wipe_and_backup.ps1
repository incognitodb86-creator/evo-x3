$ErrorActionPreference = 'Stop'
$logPath = 'C:\evo-x3\runs\h2_usb_backup_20261114\backup.log'
Start-Transcript -Path $logPath -Force

try {
    Write-Output "=== Step 1: Identify target disk ==="
    $disks = @(Get-Disk | Where-Object {
        $_.BusType -eq 'USB' -and
        $_.FriendlyName -eq 'ASMT 2115' -and
        $_.Size -ge 440GB -and
        $_.Size -le 455GB -and
        -not $_.IsBoot -and
        -not $_.IsSystem
    })

    if ($disks.Count -ne 1) {
        throw "Expected exactly 1 matching disk, found $($disks.Count). Aborting."
    }

    $disk = $disks[0]
    Write-Output "Target Disk: Number=$($disk.Number), FriendlyName=$($disk.FriendlyName), BusType=$($disk.BusType), SizeGB=$([math]::Round($disk.Size/1GB, 2)), PartitionStyle=$($disk.PartitionStyle)"

    Write-Output "=== Step 2: Wipe and format disk ==="
    Clear-Disk -Number $disk.Number -RemoveData -RemoveOEM -Confirm:$false
    Initialize-Disk -Number $disk.Number -PartitionStyle GPT

    $usedLetters = (Get-Volume | Where-Object { $_.DriveLetter }).DriveLetter
    $letter = if ($usedLetters -notcontains 'F') { 'F' } else {
        ([char[]]([char]'G'..[char]'Z') | Where-Object { $usedLetters -notcontains $_ } | Select-Object -First 1)
    }
    if (-not $letter) { throw "No free drive letter found." }

    $part = New-Partition -DiskNumber $disk.Number -UseMaximumSize -DriveLetter $letter
    Format-Volume -Partition $part -FileSystem NTFS -NewFileSystemLabel 'X3BACKUP' -Confirm:$false | Out-Null

    Write-Output "Formatted Volume: DriveLetter=$letter, Label=X3BACKUP, FileSystem=NTFS"
    Get-Disk -Number $disk.Number | Select-Object Number, FriendlyName, BusType, @{Name='SizeGB';Expression={[math]::Round($_.Size/1GB, 2)}}, PartitionStyle | Format-Table -AutoSize
    Get-Volume -DriveLetter $letter | Select-Object DriveLetter, FileSystemLabel, FileSystem, @{Name='SizeGB';Expression={[math]::Round($_.Size/1GB, 2)}}, @{Name='SizeRemainingGB';Expression={[math]::Round($_.SizeRemaining/1GB, 2)}} | Format-Table -AutoSize

    Write-Output "=== Step 3: Check BitLocker status (read-only) ==="
    manage-bde -status C: | Select-String -Pattern 'Protection Status|Percentage Encrypted'

    Write-Output "=== Step 3b: Run wbadmin backup ==="
    $target = "${letter}:"
    & wbadmin start backup -backupTarget:$target -include:C: -allCritical -quiet
    $wbExit = $LASTEXITCODE
    Write-Output "wbadmin start backup exit code: $wbExit"
    if ($wbExit -ne 0) {
        throw "wbadmin start backup failed with exit code $wbExit"
    }

    Write-Output "=== Step 4: Verify backup ==="
    & wbadmin get versions -backupTarget:$target
    $backupDir = "${letter}:\WindowsImageBackup"
    if (Test-Path $backupDir) {
        $sizeBytes = (Get-ChildItem -Path $backupDir -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        Write-Output "WindowsImageBackup exists at $backupDir. Total size: $([math]::Round($sizeBytes/1GB, 2)) GB ($sizeBytes bytes)"
    } else {
        throw "$backupDir does not exist!"
    }
}
finally {
    Stop-Transcript
}
