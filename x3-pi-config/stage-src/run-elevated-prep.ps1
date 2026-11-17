# EVO-X3 Elevated Windows Prep Script (Consolidated single Admin PowerShell script)
# Run from an elevated (Administrator) PowerShell prompt:
#   powershell -NoProfile -ExecutionPolicy Bypass -File C:\evo-x3\stage\run-elevated-prep.ps1
#
# Runs:
#   0a: Clock timezone + w32time service + resync
#   0b: winget install Git.Git and Tailscale.Tailscale + tailscale up (interactive browser sign-in)
#   U1: Read-only Admin checks (Confirm-SecureBootUEFI, BitLocker status ONLY - never keys, ESP free space via mountvol S: /S)
#   U2: pnputil /export-driver * C:\evo-x3\drivers
#   U2b (B2): Reversible Windows prep (Fast Startup off, powercfg /h off, RealTimeIsUniversal=1, Windows Update manual/no auto-reboot)
# Outputs before/after JSON to C:\evo-x3\records\elevated-prep-result.json

$ErrorActionPreference = "Continue"
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Error "This script must be run from an Administrator PowerShell prompt."
    exit 1
}

$result = [ordered]@{
    timestamp_ct_before = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    is_admin = $isAdmin
    clock = [ordered]@{}
    packages = [ordered]@{}
    u1_admin = [ordered]@{}
    u2_drivers = [ordered]@{}
    u2b_before = [ordered]@{}
    u2b_after = [ordered]@{}
    errors = @()
}

try {
    # 0a: Clock & TimeZone
    $result.clock.timezone_before = (Get-TimeZone).Id
    Set-TimeZone -Id "Central Standard Time"
    Set-Service -Name w32time -StartupType Automatic
    Start-Service w32time
    $resyncOut = (& w32tm /resync /force 2>&1) -join "`n"
    $w32Status = (Get-Service w32time)
    $result.clock.timezone_after = (Get-TimeZone).Id
    $result.clock.w32time_status = "$($w32Status.Status) / $($w32Status.StartType)"
    $result.clock.resync_output = $resyncOut
    $result.clock.resync_exit = $LASTEXITCODE
    $result.clock.time_after_ct = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss zzz")
    $result.clock.time_after_utc = (Get-Date).ToUniversalTime().ToString("o")
} catch {
    $result.errors += "0a_clock: $($_.Exception.Message)"
}

try {
    # 0b: Install full Git.Git and Tailscale.Tailscale via official winget
    Write-Host "Installing Git.Git via winget..."
    & winget install -e --id Git.Git --source winget --accept-package-agreements --accept-source-agreements
    $result.packages.git_exit = $LASTEXITCODE

    Write-Host "Installing Tailscale.Tailscale via winget..."
    & winget install -e --id Tailscale.Tailscale --source winget --accept-package-agreements --accept-source-agreements
    $result.packages.tailscale_exit = $LASTEXITCODE

    $tsExe = "C:\Program Files\Tailscale\tailscale.exe"
    if (Test-Path $tsExe) {
        Write-Host "Launching tailscale up (complete browser sign-in when prompted)..."
        Start-Process -FilePath $tsExe -ArgumentList "up"
        $result.packages.tailscale_up_launched = $true
    } else {
        $result.packages.tailscale_up_launched = $false
    }
} catch {
    $result.errors += "0b_packages: $($_.Exception.Message)"
}

try {
    # U1 Admin checks (NO keys or protectors queried!)
    try {
        $sb = Confirm-SecureBootUEFI
        $result.u1_admin.confirm_secure_boot = "$sb"
    } catch {
        $result.u1_admin.confirm_secure_boot = "error: $($_.Exception.Message)"
    }

    try {
        $blVol = Get-BitLockerVolume -MountPoint C: | Select-Object MountPoint, EncryptionMethod, VolumeStatus, ProtectionStatus, LockStatus, EncryptionPercentage, VolumeType
        $result.u1_admin.bitlocker_volume = [ordered]@{
            MountPoint = $blVol.MountPoint
            EncryptionMethod = "$($blVol.EncryptionMethod)"
            VolumeStatus = "$($blVol.VolumeStatus)"
            ProtectionStatus = "$($blVol.ProtectionStatus)"
            LockStatus = "$($blVol.LockStatus)"
            EncryptionPercentage = $blVol.EncryptionPercentage
            VolumeType = "$($blVol.VolumeType)"
        }
    } catch {
        $result.u1_admin.bitlocker_volume = "error: $($_.Exception.Message)"
    }

    try {
        $bdeRaw = (& manage-bde -status C: 2>&1) -join "`n"
        # Safety guard: strip any accidental protector/password lines if present
        $bdeSafe = ($bdeRaw -split "`n" | Where-Object { $_ -notmatch "Password|Key|Protector" }) -join "`n"
        $result.u1_admin.manage_bde_status = $bdeSafe
    } catch {
        $result.u1_admin.manage_bde_status = "error: $($_.Exception.Message)"
    }

    try {
        $mvOut = (& mountvol S: /S 2>&1) -join "`n"
        if ($LASTEXITCODE -eq 0 -or (Test-Path "S:\")) {
            $driveS = Get-PSDrive S
            $efiDirs = (Get-ChildItem "S:\EFI" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name) -join ", "
            $result.u1_admin.esp_used_bytes = $driveS.Used
            $result.u1_admin.esp_free_bytes = $driveS.Free
            $result.u1_admin.esp_used_mb = [math]::Round($driveS.Used / 1MB, 2)
            $result.u1_admin.esp_free_mb = [math]::Round($driveS.Free / 1MB, 2)
            $result.u1_admin.esp_efi_dirs = $efiDirs
            & mountvol S: /D | Out-Null
        } else {
            $result.u1_admin.esp_error = "mountvol S: /S failed ($LASTEXITCODE): $mvOut"
        }
    } catch {
        $result.u1_admin.esp_error = $_.Exception.Message
        & mountvol S: /D 2>$null | Out-Null
    }
} catch {
    $result.errors += "u1_admin: $($_.Exception.Message)"
}

try {
    # U2 Safe Prep: Export drivers
    New-Item -ItemType Directory -Path "C:\evo-x3\drivers" -Force | Out-Null
    $pnpOut = (& pnputil /export-driver * C:\evo-x3\drivers 2>&1) -join "`n"
    $pnpExit = $LASTEXITCODE
    $drvFolders = (Get-ChildItem "C:\evo-x3\drivers" -Directory -ErrorAction SilentlyContinue | Measure-Object).Count
    $drvTotalBytes = (Get-ChildItem "C:\evo-x3\drivers" -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    $result.u2_drivers.exit_code = $pnpExit
    $result.u2_drivers.exported_folder_count = $drvFolders
    $result.u2_drivers.total_size_mb = [math]::Round(($drvTotalBytes / 1MB), 2)
    $result.u2_drivers.summary_tail = (($pnpOut -split "`n") | Select-Object -Last 8) -join "`n"
} catch {
    $result.errors += "u2_drivers: $($_.Exception.Message)"
}

try {
    # U2b Before state
    $hibBefore = Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Power" -Name HiberbootEnabled -ErrorAction SilentlyContinue
    $rtcBefore = Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\TimeZoneInformation" -Name RealTimeIsUniversal -ErrorAction SilentlyContinue
    $wuBefore = Get-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" -ErrorAction SilentlyContinue
    $result.u2b_before.HiberbootEnabled = if ($null -ne $hibBefore) { $hibBefore.HiberbootEnabled } else { "<absent>" }
    $result.u2b_before.powercfg_a = ((& powercfg /a 2>&1) -join "`n")
    $result.u2b_before.RealTimeIsUniversal = if ($null -ne $rtcBefore) { $rtcBefore.RealTimeIsUniversal } else { "<absent>" }
    $result.u2b_before.WU_AU = if ($null -ne $wuBefore) { ($wuBefore | Select-Object NoAutoUpdate, AUOptions, NoAutoRebootWithLoggedOnUsers | ConvertTo-Json -Compress) } else { "<absent>" }

    # Apply reversible U2b settings
    Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Power" -Name "HiberbootEnabled" -Value 0 -Type DWord
    $hOffOut = (& powercfg /h off 2>&1) -join "`n"
    $result.u2b_after.powercfg_h_off_exit = $LASTEXITCODE
    $result.u2b_after.powercfg_h_off_out = $hOffOut

    $regUtcOut = (& reg add "HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\TimeZoneInformation" /v RealTimeIsUniversal /d 1 /t REG_DWORD /f 2>&1) -join "`n"
    $result.u2b_after.reg_utc_exit = $LASTEXITCODE
    $result.u2b_after.reg_utc_out = $regUtcOut

    $wuKey = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU"
    if (-not (Test-Path $wuKey)) { New-Item -Path $wuKey -Force | Out-Null }
    Set-ItemProperty -Path $wuKey -Name "NoAutoUpdate" -Value 0 -Type DWord
    Set-ItemProperty -Path $wuKey -Name "AUOptions" -Value 2 -Type DWord
    Set-ItemProperty -Path $wuKey -Name "NoAutoRebootWithLoggedOnUsers" -Value 1 -Type DWord

    # U2b After state
    $hibAfter = Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Power" -Name HiberbootEnabled -ErrorAction SilentlyContinue
    $rtcAfter = Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\TimeZoneInformation" -Name RealTimeIsUniversal -ErrorAction SilentlyContinue
    $wuAfter = Get-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" -ErrorAction SilentlyContinue
    $result.u2b_after.HiberbootEnabled = if ($null -ne $hibAfter) { $hibAfter.HiberbootEnabled } else { "<absent>" }
    $result.u2b_after.powercfg_a = ((& powercfg /a 2>&1) -join "`n")
    $result.u2b_after.RealTimeIsUniversal = if ($null -ne $rtcAfter) { $rtcAfter.RealTimeIsUniversal } else { "<absent>" }
    $result.u2b_after.WU_AU = if ($null -ne $wuAfter) { ($wuAfter | Select-Object NoAutoUpdate, AUOptions, NoAutoRebootWithLoggedOnUsers | ConvertTo-Json -Compress) } else { "<absent>" }
} catch {
    $result.errors += "u2b_prep: $($_.Exception.Message)"
}

$result.timestamp_ct_after = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
$result | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath "C:\evo-x3\records\elevated-prep-result.json" -Encoding UTF8
Write-Host "Completed elevated prep. Output saved to C:\evo-x3\records\elevated-prep-result.json"
