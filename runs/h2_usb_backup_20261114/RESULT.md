# EVO-X3 USB Backup Result (Run 2)

- **Status:** BLOCKED
- **Date:** 2026-11-15

## Target Disk Identity
- **Disk Number:** 1
- **FriendlyName:** ASMT 2115
- **BusType:** USB
- **Size:** 447.14 GB
- **IsBoot:** False
- **IsSystem:** False
- **Before State:** PartitionStyle MBR; Volume `F:` (`OS`, NTFS, 431.62 GB)
- **After State:** Unchanged (not wiped)

## Commands Run
1. `Get-Disk` and `Get-Volume` (verified exact single match on Disk 1; Disk 0 `CT2000E100SSD8` NVMe untouched).
2. Created `C:\evo-x3\runs\h2_usb_backup_20261114\wipe_and_backup.ps1`.
3. Attempted `Start-Process powershell -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File "C:\evo-x3\runs\h2_usb_backup_20261114\wipe_and_backup.ps1"' -Verb RunAs -Wait -PassThru`.

## Blocker
`Start-Process -Verb RunAs` failed immediately with:
`This command cannot be run due to the error: The request is not supported.`

This non-interactive shell session cannot display a UAC prompt. No changes were made to Disk 1 or Disk 0.

## Backup Verification
- **Result:** FAIL / BLOCKED (backup not started)
