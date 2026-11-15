# B0 / U1: Hardware & Windows Inventory (Read-Only)

- **Recorded:** 2026-11-15 (America/Chicago; system clock pre-sync reading, ~15 h ahead offset before `w32time` sync)
- **Status:** `PARTIAL (non-elevated checks complete; Admin checks packaged in C:\evo-x3\stage\run-elevated-prep.ps1)`
- **Note:** No recovery keys, Windows licence / OA3 keys, passwords, or hardware serial numbers are queried or recorded here.

## System & Firmware
- **Manufacturer / Model:** GMKtec `EVO-X3`
- **CPU:** `AMD RYZEN AI MAX+ 395 w/ Radeon 8060S` (16 cores, 32 logical processors, max clock 3000 MHz)
- **BIOS:** American Megatrends International, LLC. · `EVO-X3_V1.01` · Version `ALASKA - 1072009` · Release Date `2026-06-16`
- **Physical Memory (RAM):** **128 GiB** soldered LPDDR5X-8000 (`8 × 17,179,869,184 bytes` = `8 × 16 GiB`, `P0 CHANNEL A` through `P0 CHANNEL H`, ConfiguredClockSpeed `8000`, SMBIOSMemoryType `35`)
  - **Windows OS-visible RAM:** `68,340,748,288` bytes (**63.65 GiB**), because factory BIOS UMA frame buffer reserves ~64 GiB for the GPU (`AMD Radeon(TM) 8060S Graphics`, Driver `32.0.22029.1019`, `AdapterRAM` reported as `4293918720` in 32-bit WMI field).
  - *U3 BIOS requirement:* Change UMA from factory 64 GiB to **512 MB** (smallest explicit value, not Auto) before Fedora GPU work.

## OS & Windows Build
- **OS:** Microsoft Windows 11 Pro (`64-bit`), Version `10.0.26200`
- **DisplayVersion / Build:** `25H2`, Build `26200.7840` (`EditionID: Professional`)
- **Time Zone:** Switched non-elevated via `tzutil /s "Central Standard Time"` → `(UTC-06:00) Central Time (US & Canada)`
- **Windows Time (`w32time`):** `Stopped / Manual` (requires Admin UAC to start and run `w32tm /resync`)

## Storage, Partitions & Free Space
- **Disk 0:** `CT2000E100SSD8` (Crucial 2 TB NVMe), `Online`, `GPT`, **1863.02 GiB**

| Partition # | Type | Drive | Label | File System | Size | Used | Free | Flags |
|---|---|---|---|---|---:|---:|---:|---|
| 1 | System (EFI) | — | — | FAT32 (assumed) | **100.0 MiB** (0.098 GiB) | `NO_DATA` (Admin `mountvol S: /S` needed) | `NO_DATA` (Admin `mountvol S: /S` needed) | `IsSystem: True` |
| 2 | Reserved (MSR) | — | — | — | **16.0 MiB** (0.016 GiB) | — | — | — |
| 3 | Recovery | — | `BACKUP_OS` | FAT32 | **30.27 GiB** (31000 MiB) | ~0.44 GiB | **29.83 GiB** | — |
| 4 | Basic | `C:` | — | NTFS | **1831.46 GiB** (1875412 MiB) | **78.37 GiB** | **1753.09 GiB** | `IsBoot: True` |
| 5 | Recovery | — | `Recovery` | NTFS | **1.17 GiB** (1200 MiB) | ~0.82 GiB | **0.35 GiB** | — |

- **Shrink Headroom Note:** `C:` uses **78.37 GiB** out of `1831.46 GiB`. Shrinking `C:` to ~450 GB (`~460,800 MB`) leaves ~370+ GB free inside Windows (well above the plan's ≥ 100 GB free requirement) and frees **~1.38 TB** for Fedora 44 Server.
- **ESP Check (KTD1a):** Partition 1 is 100.0 MiB total. Confirm free space ≥ 30 MB via `mountvol S: /S` in Admin PowerShell before any Fedora install.

## Security, Boot & Power State
- **BitLocker / Device Encryption:**
  - Non-elevated Shell check (`System.Volume.BitLockerProtection` on `C:`): **`2`** (**Off / Unencrypted**).
  - Admin `Get-BitLockerVolume` and `manage-bde -status C:` failed non-elevated (`Access denied`) — confirm from Admin PowerShell (`C:\evo-x3\stage\run-elevated-prep.ps1`) and verify Vaultwarden rule before any change.
- **Secure Boot:** `HKLM:\SYSTEM\CurrentControlSet\Control\SecureBoot\State\UEFISecureBootEnabled` = **`0`** (Off in factory state). `Confirm-SecureBootUEFI` requires Admin privileges. (*U3 BIOS step:* enable Secure Boot and allow Microsoft 3rd Party UEFI CA if needed for Fedora shim.)
- **Fast Startup (`HiberbootEnabled`):** **`0`** (disabled; `powercfg /a` also confirms `Fast Startup: This action is disabled in the current system policy`).
- **Hibernation (`powercfg /a`):** **`Hibernate`** is currently **Available** (not yet turned off; requires Admin `powercfg /h off`).
- **RTC UTC (`RealTimeIsUniversal`):** **Not present** (`<absent>`) — requires Admin `reg add`.

## Network Interfaces & Link Speed
| Name | Description | Status | Link Speed | Notes |
|---|---|---|---|---|
| `Wi-Fi 6` | `RZ717 WiFi 7 160MHz` | `Up` (Connected) | **1.2 Gbps** | Currently active internet connection |
| `Ethernet` | `Realtek PCIe 2.5GbE Family Controller` | `Disconnected` | `0 bps` | Wired 2.5GbE port ready for cable + Household UniFi DHCP reservation |
| `Wi-Fi 7`, `10` | `RZ717 WiFi 7 160MHz` | `Disconnected` | `0 bps` | Virtual/secondary adapters |
| `Wi-Fi 8`, `9` | `RZ717 WiFi 7 160MHz` | `Not Present` | `0 bps` | — |
| `Bluetooth Network Connection 2` | `Bluetooth Device (PAN) #2` | `Disconnected` | `3 Mbps` | — |

## U1 Pass Test Checklist
- [x] BIOS facts recorded (`EVO-X3_V1.01`, 128 GiB LPDDR5X-8000, 2 TB `CT2000E100SSD8`)
- [x] Partition table & `C:` used space recorded (`78.37 GiB` used)
- [x] NICs, Windows build, Fast Startup, Hibernation, and Secure Boot registry state recorded
- [ ] **Admin verification (`BLOCKED-ON-DERRICK`):** Run `C:\evo-x3\stage\run-elevated-prep.ps1` in Admin PowerShell to record `mountvol S: /S` ESP free bytes (must be ≥ 30 MB), `manage-bde -status C:`, and `Confirm-SecureBootUEFI`
- [ ] **Wired 2.5GbE + UniFi DHCP reservation (`WAITING-ON-DERRICK / HOUSEHOLD`):** Connect 2.5GbE Ethernet cable and add UniFi DHCP reservation
- [ ] **Windows local account password (`BLOCKED-ON-DERRICK`):** Confirm Derrick has written down the local Windows password (per Plan U1) and verified BitLocker state / Vaultwarden if ever enabled
