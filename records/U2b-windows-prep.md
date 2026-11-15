# B2 / U2b: Reversible Windows Prep Record

- **Recorded:** 2026-11-15 (America/Chicago; system clock pre-sync reading, ~15 h ahead offset before `w32time` sync)
- **Overall Status:** `PARTIAL / BLOCKED-ON-DERRICK` (Fast Startup already disabled; elevated Admin commands packaged in [run-elevated-prep.ps1](file:///C:/evo-x3/stage/run-elevated-prep.ps1) because this non-interactive shell cannot trigger UAC elevation).
- **HARD STOP Reminder:** Do **NOT** shrink `C:` or modify partitions until U2 (verified Clonezilla full-disk image + tested Windows recovery USB + BitLocker state check) passes and Derrick confirms.

## Before / After State & Rollback Commands

| Setting | Before Value (Measured) | Desired B2 / U2b Value | Current Status | Exact Rollback Command |
|---|---|---|---|---|
| **BitLocker / Device Encryption (`C:`)** | Non-elevated Shell `BitLockerProtection` = `2` (**Off**) | Off / Fully Decrypted (confirm via Admin `manage-bde -status C:`; save key in Vaultwarden if ever enabled) | `PARTIAL` (Admin `manage-bde -status C:` pending) | `manage-bde -on C:` (only if Derrick chooses later) |
| **Fast Startup (`HiberbootEnabled`)** | `0` (`powercfg /a`: disabled in current system policy) | `0` (Disabled) | `DONE` (already `0`) | `Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Power" -Name HiberbootEnabled -Value 1 -Type DWord` |
| **Hibernation (`powercfg /h off`)** | `Hibernate` = **Available** (`powercfg /a`) | Unavailable (`powercfg /h off`), followed by full **Shut down** (not Restart) | `BLOCKED-ON-DERRICK` (needs Admin PowerShell) | `powercfg /h on` |
| **RTC in UTC (`RealTimeIsUniversal`)** | `<absent>` | `1` (`REG_DWORD`) | `BLOCKED-ON-DERRICK` (needs Admin PowerShell) | `reg delete "HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\TimeZoneInformation" /v RealTimeIsUniversal /f` |
| **Windows Update Manual / Attended** | `<absent>` policy key (default automatic) | `NoAutoUpdate=0`, `AUOptions=2` (Notify), `NoAutoRebootWithLoggedOnUsers=1` | `BLOCKED-ON-DERRICK` (needs Admin PowerShell) | `Remove-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" -Recurse` |

## Exact Commands for Derrick (Administrator PowerShell)
Run `powershell -NoProfile -ExecutionPolicy Bypass -File C:\evo-x3\stage\run-elevated-prep.ps1` (which also performs `0a`, `0b`, `U1`, `U2` driver export, and saves before/after JSON to `C:\evo-x3\records\elevated-prep-result.json`), OR run individually:
```powershell
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Power" -Name "HiberbootEnabled" -Value 0 -Type DWord
powercfg /h off
reg add "HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\TimeZoneInformation" /v RealTimeIsUniversal /d 1 /t REG_DWORD /f
$wuKey = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU"
if (-not (Test-Path $wuKey)) { New-Item -Path $wuKey -Force | Out-Null }
Set-ItemProperty -Path $wuKey -Name "NoAutoUpdate" -Value 0 -Type DWord
Set-ItemProperty -Path $wuKey -Name "AUOptions" -Value 2 -Type DWord
Set-ItemProperty -Path $wuKey -Name "NoAutoRebootWithLoggedOnUsers" -Value 1 -Type DWord
```
Then perform a full **Shut down** (not Restart) per Arch Wiki Dual-boot guidance.

## C: Shrink Calculation (Only AFTER U2 Verified — NOT EXECUTED)
- Current `C:` size: `1,831.46 GiB` (`~1,875,412 MiB`), `78.37 GiB` used, `1,753.09 GiB` free.
- Target Windows size: **~450 GB** (`~460,800 MB`, leaving > 370 GB free inside Windows — well above the ≥ 100 GB free rule).
- Approximate amount to shrink in **Disk Management (`diskmgmt.msc`)**: **`~1,414,612 MB`** (do NOT use GParted or Fedora installer to shrink NTFS; leave freed space **unallocated**).
- After shrink, **STOP** for Derrick's **RESIZE GATE** `yes` card before booting the Fedora 44 Server installer.
