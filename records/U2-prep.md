# B1 / U2: Safe Prep, ISOs, Driver Export & USB/Imaging Instructions

- **Recorded:** 2026-11-15 (America/Chicago; system clock pre-sync reading, ~15 h ahead offset before `w32time` sync)
- **Overall U2 Status:** `DONE (backup image on X3BACKUP USB, Derrick confirmed 2026-11-15)`. The original prep notes below are historical and were written before that confirmation. This session did not re-verify image checksums or run a restore test. QNAP off-pool second copy, if still desired, remains a Household item.

## Confirmation (2026-11-15, America/Chicago)

Derrick confirmed the U2 backup image already exists on the X3BACKUP USB. Treat the full-disk image step as done on that confirmation.

## 1. Driver Export (`pnputil /export-driver * C:\evo-x3\drivers`)
- **Status:** `PARTIAL / BLOCKED-ON-DERRICK` (requires Administrator PowerShell)
- Non-elevated run exported **7 driver packages** (`20.86 MB`) before hitting access denied (`ExitCode: -1`).
- **Next Action:** Included in [run-elevated-prep.ps1](file:///C:/evo-x3/stage/run-elevated-prep.ps1) — running that script as Administrator exports **all** Windows driver packages to `C:\evo-x3\drivers\`.

## 2. Clonezilla Live Stable ISO (`C:\evo-x3\iso\clonezilla-live-3.3.3-37-amd64.iso`)
- **Status:** **`DONE` & SHA-256 VERIFIED**
- **Official Source:** `https://free.nchc.org.tw/clonezilla-live/stable/clonezilla-live-3.3.3-37-amd64.iso`
- **Checksum Source:** `https://free.nchc.org.tw/clonezilla-live/stable/SHA256SUMS`
- **File Size:** `505,413,632` bytes (`482 MB`)
- **Expected SHA-256:** `3079458d926a37d3533e5d5caeb61b6e49c2dc69e2c97e0332ef37986bb3414f`
- **Measured SHA-256:** `3079458d926a37d3533e5d5caeb61b6e49c2dc69e2c97e0332ef37986bb3414f` (**Match: True**)

## 3. Fedora 44 Server x86_64 ISO
- **Status:** **`BLOCKED-ON-DERRICK`** (Anti-bot Proof-of-Work challenge)
- `https://dl.fedoraproject.org/pub/fedora/linux/releases/44/Server/x86_64/iso/Fedora-Server-44-1.7-x86_64-CHECKSUM` returned an **Anubis v1.25.0 Proof-of-Work challenge** (`"Making sure you're not a bot!"`). Per policy, the agent does not bypass anti-bot challenges.
- **What Derrick must do in a normal browser on this PC:**
  1. Open and download `Fedora-Server-dvd-x86_64-44-1.7.iso` (~3.6 GB):
     `https://dl.fedoraproject.org/pub/fedora/linux/releases/44/Server/x86_64/iso/Fedora-Server-dvd-x86_64-44-1.7.iso`
  2. Open and save the official checksum file:
     `https://dl.fedoraproject.org/pub/fedora/linux/releases/44/Server/x86_64/iso/Fedora-Server-44-1.7-x86_64-CHECKSUM`
  3. Move both files into `C:\evo-x3\iso\` and verify the hash in PowerShell:
     ```powershell
     Get-FileHash C:\evo-x3\iso\Fedora-Server-dvd-x86_64-44-1.7.iso -Algorithm SHA256
     Get-Content C:\evo-x3\iso\Fedora-Server-44-1.7-x86_64-CHECKSUM
     ```

## 4. Exact USB & Full-Disk Clonezilla Imaging Steps for Derrick (STOP Points — Not Run by Agent)

### A. Create & Boot-Test Windows Recovery USB
1. Plug in a dedicated USB flash drive (≥ 32 GB, contents will be wiped). Confirm drive letter.
2. Press `Win+R` → run `recovery` (`RecoveryDrive.exe`) → keep **"Back up system files to the recovery drive"** ticked → select the USB drive and create.
3. Reboot once using the BIOS one-time boot menu to verify the recovery USB boots to its menu, then shut down / reboot back to Windows.

### B. Create Bootable Clonezilla Live USB & Capture Full-Disk Image to QNAP
1. Wait for Household to confirm the QNAP SMB share name and ≥ ~118 GiB free (1.5× the 78.37 GiB used on `C:`), **plus** a second off-pool copy destination (because QNAP Data pool HDD2 is degraded).
2. Write `C:\evo-x3\iso\clonezilla-live-3.3.3-37-amd64.iso` to a USB stick using **Rufus** (`rufus.ie`) or **Fedora Media Writer** / **Ventoy** (GPT / UEFI mode, DD mode if using Rufus).
3. Boot the Clonezilla USB in UEFI mode (`Clonezilla live (VGA 800x600)`).
4. Choose:
   - `device-image` → `samba_server` (configure Wi-Fi or wired 2.5GbE DHCP, enter QNAP IP/hostname, SMB share name, and Derrick/Household SMB credentials interactively).
   - **Beginner** or **Expert** mode → **`savedisk`** (capture the **entire** `nvme0n1` disk: Partition 1 EFI, Partition 2 MSR, Partition 3 `BACKUP_OS`, Partition 4 `C:`, Partition 5 `Recovery`).
   - Enable **`-scr`** / image verification (**"Check saved image restorable"**) when prompted at the end of capture (or run `ocs-chkimg` from Clonezilla shell).
5. Copy `C:\evo-x3\drivers\` and `C:\evo-x3\stage\` onto the same QNAP backup folder.
6. Record the Clonezilla image SHA-256 checksums and verify result (`OK`), and place a **second copy** of the image off the degraded QNAP pool.

### C. Create Fedora 44 Server Installer USB (After Resize Gate `yes` Card)
1. Use **Fedora Media Writer** (`fedoraproject.org/fmw`) or **Rufus (DD Image mode)** to write `C:\evo-x3\iso\Fedora-Server-dvd-x86_64-44-1.7.iso` to a USB stick.
2. Also copy `C:\evo-x3\stage\` to a second folder on a USB drive (or keep accessible via QNAP/Gitea) so `fedora-bootstrap.sh` can be run on first Fedora boot.
