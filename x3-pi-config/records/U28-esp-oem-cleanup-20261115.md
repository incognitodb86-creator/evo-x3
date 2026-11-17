# U28 — ESP EFI/OEM cleanup (Derrick t1801s6636, 6:48 PM CT Nov 15 2026)

Max Architect. Approved: "Yes, back up EFI/OEM to the Linux drive and remove it from the boot partition." Done 6:49 PM CT Nov 15 2026. No reboot. Windows partitions, X3BACKUP USB, BIOS, EFI/Microsoft, EFI/fedora, and EFI/Boot were not touched.

## Before
- ESP: `/dev/nvme0n1p1` mounted at `/boot/efi`, 100 MiB (100663296 B)
- Used 89 MiB (92675072 B), available 7.7 MiB (7988224 B), 93%
- `EFI/OEM`: 31 MiB, 157 files (byte-identical Windows boot tree; NVRAM did not reference it)
- Other trees: `EFI/fedora` 6 files / 6.8 MiB; `EFI/Microsoft` 157 files / 32 MiB; `EFI/Boot` 2 files / 1.2 MiB
- `efibootmgr -v`: BootCurrent 0003; BootOrder 0003,0000,0001
  - Boot0000* Windows Boot Manager → `\EFI\Microsoft\Boot\bootmgfw.efi` on this ESP
  - Boot0001* UEFI OS → `\EFI\BOOT\BOOTX64.EFI` on HD(3,…)
  - Boot0003* Fedora → `\EFI\fedora\shimx64.efi` on this ESP
  - No entry pointed at `\EFI\OEM`

## Backups
Directory `/root/esp-backup-20261115` (mode 0700, root:root), written 6:49 PM CT.

| File | Size | sha256 |
| --- | --- | --- |
| `/root/esp-backup-20261115/EFI-OEM.tar` | 32491520 B | `56a1062fb23aad8af782c034a1bbe9103f1dbfe11993e2345529f4cc06bdd335` |
| `/root/esp-backup-20261115/esp-full.tar` | 92692480 B | `05ddc89e4fbcb6c550e6c98cbcaafbab47de1402bf289f2fc6cb3b78b02c3651` |

Integrity: both `tar -tf` listed cleanly. EFI-OEM.tar: 213 entries, 157 files, 0 paths outside `OEM/`. esp-full.tar: 590 entries, 421 files, includes EFI/OEM, EFI/Microsoft, EFI/fedora, and EFI/Boot.

## After
- Removed only `/boot/efi/EFI/OEM`. Directory gone; no OEM remnants under `/boot/efi`.
- Used 58 MiB (60200960 B), available 39 MiB (40462336 B), 60%. Freed ~31 MiB (32463872 B). Above the 30 MiB safety line.
- File counts unchanged: `EFI/fedora` 6 / 6.8 MiB; `EFI/Microsoft` 157 / 32 MiB; `EFI/Boot` 2 / 1.2 MiB.
- `efibootmgr -v` unchanged (same BootCurrent, BootOrder, and three entries/paths).
- `grub2-editenv list` works: `saved_entry=b56891dd49424566a2ca1d209e5dca2b-7.3.3-200.fc44.x86_64`, `boot_success=1`, `boot_indeterminate=0`.

## Restore
To put EFI/OEM back (does not overwrite other ESP trees):

```bash
sudo tar -xpf /root/esp-backup-20261115/EFI-OEM.tar -C /boot/efi/EFI
```

Full ESP restore if needed: `sudo tar -xpf /root/esp-backup-20261115/esp-full.tar -C /boot/efi`
