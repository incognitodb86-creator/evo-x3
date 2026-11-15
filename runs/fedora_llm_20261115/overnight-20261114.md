# EVO-X3 overnight bootstrap log

PROGRESS: 2026-11-14 23:56:32 CST | IN PROGRESS | DOWNLOADS FINISHED ok=8 fail=0. SHA256SUMS written.


























































- Started: 2026-11-14 22:45:40 CST
- Host: evo-X3 / Fedora 44 Server / kernel 6.19.10-300.fc44.x86_64
- Plan: 2026-11-11-evo-x3-setup-plan.md rev 8, from U5 onward (limited overnight scope)
- Community way: https://strix-halo-toolboxes.com/ (opened 2026-11-14 CT) + kyuz0 amd-strix-halo-toolboxes README → adapt: use ttm.pages_limit and amdgpu.gttsize style settings; leave IOMMU on (plan Q10 / parent); use plan KTD2 120 GiB caps (pages_limit=31457280, gttsize=122880 MiB), not the guide's 124 GiB / amd_iommu=off.

## 0. Pre-flight inventory

```
Sat Nov 14 22:45:40 CST 2026
Linux evo-X3 6.19.10-300.fc44.x86_64 #1 SMP PREEMPT_DYNAMIC Wed Mar 25 18:23:49 UTC 2026 x86_64 GNU/Linux
               total        used        free      shared  buff/cache   available
Mem:            62Gi       2.3Gi        60Gi       1.8Mi       530Mi        60Gi
Swap:          8.0Gi          0B       8.0Gi
--- lsblk ---
NAME             SIZE TYPE FSTYPE      LABEL     MOUNTPOINTS
zram0              8G disk swap        zram0     [SWAP]
nvme0n1          1.8T disk                       
├─nvme0n1p1      100M part vfat        SYSTEM    /boot/efi
├─nvme0n1p2       16M part                       
├─nvme0n1p3     30.3G part vfat        BACKUP_OS 
├─nvme0n1p4      170G part ntfs                  
├─nvme0n1p5      1.2G part ntfs        Recovery  
├─nvme0n1p6        2G part xfs                   /boot
└─nvme0n1p7      1.6T part LVM2_member           
  └─fedora-root   15G lvm  xfs                   /
--- pvs/vgs/lvs ---
  PV             VG     Fmt  Attr PSize PFree 
  /dev/nvme0n1p7 fedora lvm2 a--  1.62t <1.61t
  VG     #PV #LV #SN Attr    VSize VFree 
  fedora   1   1   0 wz--n-- 1.62t <1.61t
  LV   VG     Attr       LSize  Pool Origin Data%  Meta%  Move Log Cpy%Sync Convert
  root fedora -wi-ao---- 15.00g                                                    
--- df ---
Filesystem              Type  Size  Used Avail Use% Mounted on
/dev/mapper/fedora-root xfs    15G  2.5G   13G  17% /
--- cmdline ---
BOOT_IMAGE=(hd0,gpt6)/vmlinuz-6.19.10-300.fc44.x86_64 root=/dev/mapper/fedora-root ro rd.lvm.lv=fedora/root rhgb quiet
--- mem_info ---
vram_total=68719476736
gtt_total=33511735296
pages_limit=8181576
--- boot order ---
BootCurrent: 0003
Timeout: 2 seconds
BootOrder: 0000,0001,0003
Boot0000* Windows Boot Manager	HD(1,GPT,b7f27e1b-1e3d-41f6-bd3b-17d6372e644f,0x800,0x32000)/\EFI\Microsoft\Boot\bootmgfw.efi57494e444f5753000100000088000000780000004200430044004f0042004a004500430054003d007b00390064006500610038003600320063002d0035006300640064002d0034006500370030002d0061006300630031002d006600330032006200330034003400640034003700390035007d00000039000100000010000000040000007fff0400
Boot0001* UEFI OS	HD(3,GPT,643fa1e4-faa0-4aa7-95d0-278b55baf73c,0x3a800,0x3c8c000)/\EFI\BOOT\BOOTX64.EFI0000424f
Boot0003* Fedora	HD(1,GPT,b7f27e1b-1e3d-41f6-bd3b-17d6372e644f,0x800,0x32000)/\EFI\fedora\shimx64.efi
```

Notes: Windows/BACKUP_OS/Recovery/EFI partitions will not be touched. USB not present. fedora VG has ~1.61T free; fedora-root is 15G XFS on LVM. UMA currently 64 GiB (vram_total=68719476736), OS RAM ~62 GiB. BIOS UMA 512 MB is Derrick's morning job.

## 1. Grow fedora-root (XFS on LVM)

Confirmed free space was in VG fedora on PV /dev/nvme0n1p7 (PFree 1765718097920 B / ~1.61 TiB). No unpartitioned disk space needed; no new partitions created. Windows/BACKUP_OS/EFI/Recovery left untouched. USB not present.

Command: `sudo lvextend -r -l +100%FREE fedora/root`

- Before: fedora-root 15.00 GiB, df 15G (2.5G used, 13G avail)
- After: fedora-root 1.62 TiB (424820 extents), df 1.7T (34G used includes XFS metadata after grow, 1.6T avail), VG PFree 0
- Filesystem remains XFS on LVM (no reinstall).

Grew at 2026-11-14 22:45:53 CST

## 2. Packages
```
linux-firmware-20261019-1.fc44.noarch
amd-gpu-firmware-20261019-1.fc44.noarch
kernel-6.19.10-300.fc44.x86_64
kernel-7.3.3-200.fc44.x86_64
kernel-core-6.19.10-300.fc44.x86_64
kernel-core-7.3.3-200.fc44.x86_64
podman-5.8.9-1.fc44.x86_64
toolbox-0.3-4.fc44.x86_64
distrobox-1.8.2.5-1.fc44.noarch
skopeo-1.22.3-1.fc44.x86_64
snapper-0.13.0-3.fc44.x86_64
python3-dnf-plugin-versionlock-4.10.1-9.fc44.noarch
6.19.10-300.fc44.x86_64
```


versionlock:
```
# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel
evr = 6.19.10-300.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel
evr = 7.3.3-200.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-core
evr = 6.19.10-300.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-core
evr = 7.3.3-200.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-cross-headers
evr = 6.19.6-300.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-cross-headers
evr = 7.3.3-200.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-debug
evr = 6.19.10-300.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-debug
evr = 7.3.3-200.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-debug-core
evr = 6.19.10-300.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-debug-core
evr = 7.3.3-200.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-debug-devel
evr = 6.19.10-300.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-debug-devel
evr = 7.3.3-200.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-debug-devel-matched
evr = 6.19.10-300.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-debug-devel-matched
evr = 7.3.3-200.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-debug-modules
evr = 6.19.10-300.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-debug-modules
evr = 7.3.3-200.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-debug-modules-core
evr = 6.19.10-300.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-debug-modules-core
evr = 7.3.3-200.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-debug-modules-extra
evr = 6.19.10-300.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-debug-modules-extra
evr = 7.3.3-200.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-debug-modules-internal
evr = 6.19.10-300.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-debug-modules-internal
evr = 7.3.3-200.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-debug-uki-virt
evr = 6.19.10-300.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-debug-uki-virt
evr = 7.3.3-200.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-debug-uki-virt-addons
evr = 6.19.10-300.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-debug-uki-virt-addons
evr = 7.3.3-200.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-devel
evr = 6.19.10-300.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-devel
evr = 7.3.3-200.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-devel-matched
evr = 6.19.10-300.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-devel-matched
evr = 7.3.3-200.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-doc
evr = 6.19.10-300.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-doc
evr = 7.3.3-200.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-headers
evr = 6.19.6-300.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-headers
evr = 7.3.3-200.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-kmap-internal
evr = 7.3.3-200.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-modules
evr = 6.19.10-300.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-modules
evr = 7.3.3-200.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-modules-core
evr = 6.19.10-300.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-modules-core
evr = 7.3.3-200.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-modules-extra
evr = 6.19.10-300.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-modules-extra
evr = 7.3.3-200.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-modules-extra-matched
evr = 6.19.10-300.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-modules-extra-matched
evr = 7.3.3-200.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-modules-internal
evr = 6.19.10-300.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-modules-internal
evr = 7.3.3-200.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-rpm-macros
evr = 205-28.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-selftests-internal
evr = 6.19.10-300.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-selftests-internal
evr = 7.3.3-200.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-srpm-macros
evr = 1.0-28.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-tools
evr = 6.19.10-300.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-tools
evr = 7.3.3-200.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-tools-libs
evr = 6.19.10-300.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-tools-libs
evr = 7.3.3-200.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-tools-libs-devel
evr = 6.19.10-300.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-tools-libs-devel
evr = 7.3.3-200.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-uki-virt
evr = 6.19.10-300.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-uki-virt
evr = 7.3.3-200.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-uki-virt-addons
evr = 6.19.10-300.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernel-uki-virt-addons
evr = 7.3.3-200.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: kernelshark
evr = 1:2.3.1-8.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: linux-firmware
evr = 20261019-1.fc44

# Added by 'versionlock add' command on 2026-11-14 22:50:37
Package name: amd-gpu-firmware
evr = 20261019-1.fc44
```

## 3. Kernel args (U5)
IOMMU left on. Applied via grubby --update-kernel=ALL and /etc/modprobe.d/ttm.conf + dracut --force.
Target: amdgpu.gttsize=122880 ttm.pages_limit=31457280 (120 GiB). Will take effect after reboot.
```
GRUB_TIMEOUT=5
GRUB_DISTRIBUTOR="$(sed 's, release .*$,,g' /etc/system-release)"
GRUB_DEFAULT=saved
GRUB_DISABLE_SUBMENU=true
GRUB_TERMINAL_OUTPUT="console"
GRUB_CMDLINE_LINUX="rd.lvm.lv=fedora/root rhgb quiet amdgpu.gttsize=122880 ttm.pages_limit=31457280"
GRUB_DISABLE_RECOVERY="true"
GRUB_ENABLE_BLSCFG=true
index=0
kernel="/boot/vmlinuz-7.3.3-200.fc44.x86_64"
args="ro rd.lvm.lv=fedora/root rhgb quiet amdgpu.gttsize=122880 ttm.pages_limit=31457280"
root="/dev/mapper/fedora-root"
initrd="/boot/initramfs-7.3.3-200.fc44.x86_64.img"
title="Fedora Linux (7.3.3-200.fc44.x86_64) 44 (Server Edition)"
id="b56891dd49424566a2ca1d209e5dca2b-7.3.3-200.fc44.x86_64"
# EVO-X3 Kernel GPU Memory Configuration (Plan KTD2 / U5)
# 31457280 pages * 4 KiB = 120 GiB GTT/VRAM pool for Strix Halo (BIOS UMA = 512 MB).
# Step up to 32505856 (124 GiB) only on an allocation failure.
# amdgpu.gttsize is set via grubby as well (kyuz0/community still ships it; values kept in sync).
# IOMMU stays on (do NOT set amd_iommu=off).
options ttm pages_limit=31457280
```

## 4. llama-swap
Installed official v272 linux_amd64 (sha256 3f21b4c13f55ea5576badcd6cc1d114ccdcf74a5d56346d3ac1e777d28e0fdf1) to /usr/local/bin/llama-swap.
```
version: v272 (802f1c4), built at 2026-11-10T06:55:17Z
```

## 5. Firmware boot order (completed after stage recopy)
Set `efibootmgr -o 0003,0000,0001` (Fedora, Windows Boot Manager, UEFI OS on BACKUP_OS). Did not touch partition contents.
```
BootCurrent: 0003
Timeout: 2 seconds
BootOrder: 0003,0000,0001
Boot0000* Windows Boot Manager	HD(1,GPT,b7f27e1b-1e3d-41f6-bd3b-17d6372e644f,0x800,0x32000)/\EFI\Microsoft\Boot\bootmgfw.efi57494e444f5753000100000088000000780000004200430044004f0042004a004500430054003d007b00390064006500610038003600320063002d0035006300640064002d0034006500370030002d0061006300630031002d006600330032006200330034003400640034003700390035007d00000039000100000010000000040000007fff0400
Boot0001* UEFI OS	HD(3,GPT,643fa1e4-faa0-4aa7-95d0-278b55baf73c,0x3a800,0x3c8c000)/\EFI\BOOT\BOOTX64.EFI0000424f
Boot0003* Fedora	HD(1,GPT,b7f27e1b-1e3d-41f6-bd3b-17d6372e644f,0x800,0x32000)/\EFI\fedora\shimx64.efi
```

## 4b. llama-swap unit
Installed /etc/systemd/system/llama-swap.service. Not enabled yet (yaml digests still to pin after image pull).

## 6. Engine images and GPU probe (pre-reboot)

Community way: https://strix-halo-toolboxes.com/ (opened 2026-11-14 CT) + kyuz0 amd-strix-halo-toolboxes README → adapt. IOMMU left on. 120 GiB caps (`amdgpu.gttsize=122880 ttm.pages_limit=31457280`) applied with grubby to kernel 7.3.3, 6.19.10, and rescue. `amd_iommu=off` was not added.

Pinned image digests (podman pull 2026-11-14 22:54 CT):

- `ghcr.io/gufo-org/toolboxes/gufo-runtime@sha256:49b1fce40cb43e33c46d91595e300cb320cdec768fcd976f8c8da24b402fc133` — Gufo 0.34.0 (2845939), built-in `qwen38_flash_next` and `qwen27-q4` providers
- `docker.io/kyuz0/amd-strix-halo-toolboxes@sha256:9a9e4d8f56e7792dffca1e2906d9399ff03ef87c9e2148983c9393fcbb8d7fb6` — llama.cpp 1.0.0-dev (build 12405, commit 9f26fe11c)

GPU probe inside the vulkan-radv toolbox (`vulkaninfo --summary`), devices passed: `/dev/dri` `/dev/kfd`:

- GPU0: `AMD Radeon 8060S Graphics (RADV STRIX_HALO)`, Mesa 26.2.6, vendor 0x1002 device 0x1586, api 1.4.354, integrated GPU
- GPU1: `llvmpipe` CPU (ignored; not used)

llama-swap v272 (802f1c4, official GitHub linux_amd64, sha256 `3f21b4c13f55ea5576badcd6cc1d114ccdcf74a5d56346d3ac1e777d28e0fdf1`) is at `/usr/local/bin/llama-swap`. Config is `/etc/evo-x3/llama-swap.yaml` with digest-pinned images and `${env.LLM_KEY_*}` placeholders only. Service unit installed, not yet enabled (waiting on remaining model files + reboot).

## 7. Official Hugging Face models (SHA-256 from git-lfs pointers, verified on disk)

| llama-swap ID | Official repo / file | Bytes | SHA-256 (HF lfs oid) | Status |
|---|---|---|---|---|
| embed-small | nomic-ai/nomic-embed-text-v1.5-GGUF `nomic-embed-text-v1.5.Q8_0.gguf` | 146146432 | 3e24342164b3d94991ba9692fdc0dd08e3fd7362e0aacc396a9a5c54a544c3b7 | VERIFIED 22:47 CT |
| qwen27b | unsloth/Qwen3.8-27B-GGUF `Qwen3.8-27B-UD-Q4_K_XL.gguf` | 17659407264 | 2a5f3565f39cf885103da591182c1266da64745737b42b452fd3e675369f1211 | VERIFIED 22:56 CT |
| gemma4-heretic | mradermacher/gemma-4-26B-A4B-it-heretic-GGUF `gemma-4-26B-A4B-it-heretic.Q8_0.gguf` | 26859855008 | 1f2e89b8382fd2182ef3a7e15a5cf272722f767a8a08a58dd69ae36c52edbf1c | VERIFIED 23:08 CT |
| flash-next MTP | unsloth/Qwen3.8-Flash-Next-GGUF `MTP/mtp-Qwen3.8-Flash-Next-shared-Q8_0.gguf` | 2786568256 | 5ff54097406a905cf3a724c709124ceb0e3e10235ee862298969e91c96fa96e6 | VERIFIED 23:09 CT |
| flash-next shard1 | `UD-Q4_K_XL/Qwen3.8-Flash-Next-UD-Q4_K_XL-00001-of-00004.gguf` | 10946618 | acc44040f74d0e55fb89c3967056cce5dbda1bcc52e909c3ba6fc72b5e9c0858 | VERIFIED 23:09 CT |
| flash-next shard2 | `...-00002-of-00004.gguf` | 49720539552 | 45792ae869072d8229384c51c7c73dd959e191505252b41dd71852d9746f5ce4 | VERIFIED 23:30 CT |
| flash-next shard3 | `...-00003-of-00004.gguf` | 32803030176 | 8c76e79d444b16a663d9c8db54e585ed3b1da13eebd2619c37b0c355da803c82 | downloading (resumed by existing curl, not duplicated) |
| flash-next shard4 | `...-00004-of-00004.gguf` | 28800138432 | 5de8b5dbf89409acc39468decafd4a4a95b13c29d88a14b0356107897829ec36 | pending |

27B VRAM estimator (fp16 KV table in the toolbox tool; q8_0 KV is ~half): at 262,144 tokens, fp16 context 65.00 GiB / total 83.45 GiB; q8_0 estimate ~50.95 GiB, which fits in the current ~62 GiB visible. llama-swap uses `-c 262144 -np 2 -ctk q8_0 -ctv q8_0`.

Tailscale Serve (U8) was not enabled: ACL gate still needs Derrick's yes card. No new Tailscale auth keys. LAN SSH was left open. Windows and BACKUP_OS partitions were not written.


## 8. Worker continuation (23:39 CT)

Previous worker was interrupted during flash-next shard3. A new worker attached at 23:36 CT over Tailscale SSH (`derekboone@evo-x3-1.tailf242b2.ts.net`).

Found:
- fedora-root still 1.7T, ~148G used.
- Kernel args already set via grubby on 7.3.3, 6.19.10, and rescue; default kernel is 7.3.3-200.fc44; no reboot yet (cmdline still lacks gttsize/pages_limit).
- BootOrder already `0003,0000,0001` (Fedora first). Entries were not deleted.
- llama-swap v272 installed, unit disabled/inactive, yaml digest-pinned, llm.env placeholders all empty (Derrick types keys).
- download-models.sh PID 8773 still running; curl PID 34537 still fetching shard3 `.partial` only. Did not start a duplicate curl.
- Already VERIFIED on disk (size + sha256 in download-status.txt): embed-small, qwen27b, gemma4-heretic, flash-next MTP, shard1, shard2.
- Shard4 not started yet; the existing sequential script will fetch it after shard3 verifies.
- Noted config issue to fix after downloads (backup first): embed-small is on 127.0.0.1:8081 in `/etc/evo-x3/llama-swap.yaml`, which would collide with the main-group engines. Staged U13 config uses 8083. Will move embed-small to 8083 before enabling the unit.

Next: wait for the existing downloader to finish (shard3 + shard4 + SHA256SUMS), then reboot, confirm kernel args and visible GPU memory, enable llama-swap on 127.0.0.1, run completion/embedding tests, commit the record, then remove `/etc/sudoers.d/90-max-setup`.


## 9. Morning continuation (2026-11-15, America/Chicago)

Fedora came back on the tailnet at 07:38 CT after Derrick set UEFI BootOrder to `0003,0000,0001` (Fedora first) from Windows and restarted into Fedora. BootCurrent=0003. Kernel 7.3.3-200.fc44.x86_64 with `amdgpu.gttsize=122880 ttm.pages_limit=31457280` applied. Boot order was left unchanged this session.

Visible memory after reboot:
- OS RAM ~62 GiB
- mem_info_vram_total = 68719476736 (64.00 GiB) — BIOS UMA still 64 GB (Derrick's morning task is 512 MB)
- mem_info_gtt_total = 67019173888 (62.41 GiB); ttm.pages_limit=31457280
- Gufo `diagnose`: unified pool totalBytes=67019173888 (~62.4 GiB). Flash-Next weights (~111.3 GB + 2.60 GiB MTP) cannot load until UMA is 512 MB.

### 9.1 SHA256 re-verification (official Hugging Face LFS oids)

Local `/srv/models/SHA256SUMS` already matched the official HF LFS sha256 values exactly. Re-ran `sha256sum -c /srv/models/SHA256SUMS` under systemd unit `evo-sha256-verify` (script-owned log, no secrets).

- Started: 2026-11-15 07:40:39 AM CST
- Finished: 2026-11-15 07:42:10 AM CST, EXIT 0, ok=8 fail=0

| file | bytes | sha256 (official HF = local) | result |
|---|---:|---|---|
| embed-small/nomic-embed-text-v1.5.Q8_0.gguf | 146146432 | 3e24342164b3d94991ba9692fdc0dd08e3fd7362e0aacc396a9a5c54a544c3b7 | OK |
| flash-next/Qwen3.8-Flash-Next-UD-Q4_K_XL-00001-of-00004.gguf | 10946618 | acc44040f74d0e55fb89c3967056cce5dbda1bcc52e909c3ba6fc72b5e9c0858 | OK |
| flash-next/Qwen3.8-Flash-Next-UD-Q4_K_XL-00002-of-00004.gguf | 49720539552 | 45792ae869072d8229384c51c7c73dd959e191505252b41dd71852d9746f5ce4 | OK |
| flash-next/Qwen3.8-Flash-Next-UD-Q4_K_XL-00003-of-00004.gguf | 32803030176 | 8c76e79d444b16a663d9c8db54e585ed3b1da13eebd2619c37b0c355da803c82 | OK |
| flash-next/Qwen3.8-Flash-Next-UD-Q4_K_XL-00004-of-00004.gguf | 28800138432 | 5de8b5dbf89409acc39468decafd4a4a95b13c29d88a14b0356107897829ec36 | OK |
| flash-next/mtp-Qwen3.8-Flash-Next-shared-Q8_0.gguf | 2786568256 | 5ff54097406a905cf3a724c709124ceb0e3e10235ee862298969e91c96fa96e6 | OK |
| gemma4-heretic/gemma-4-26B-A4B-it-heretic.Q8_0.gguf | 26859855008 | 1f2e89b8382fd2182ef3a7e15a5cf272722f767a8a08a58dd69ae36c52edbf1c | OK |
| qwen27b/Qwen3.8-27B-UD-Q4_K_XL.gguf | 17659407264 | 2a5f3565f39cf885103da591182c1266da64745737b42b452fd3e675369f1211 | OK |

Official sources: `nomic-ai/nomic-embed-text-v1.5-GGUF`, `unsloth/Qwen3.8-Flash-Next-GGUF`, `mradermacher/gemma-4-26B-A4B-it-heretic-GGUF`, `unsloth/Qwen3.8-27B-GGUF`.

### 9.2 llama-swap

- Already installed (v272), unit enabled+active after boot, listening on `127.0.0.1:8080` only. Engines on `127.0.0.1:8081`, embed-small on `127.0.0.1:8083`.
- `/etc/evo-x3/llm.env` is 0600 root:root; all five `LLM_KEY_*` placeholders are empty. Derrick types the keys. The wrapper `/usr/local/bin/evo-llama-swap` omits the `apiKeys` block at runtime until at least one key is typed (llama-swap v272 rejects empty apiKeys). Auth stays off, loopback only, until then.
- Root podman store had no images (they were only in derekboone's user store). Pulled the same pinned digests into the root store so the root unit can start containers:
  - `ghcr.io/gufo-org/toolboxes/gufo-runtime@sha256:49b1fce40cb43e33c46d91595e300cb320cdec768fcd976f8c8da24b402fc133` (0.34.0)
  - `docker.io/kyuz0/amd-strix-halo-toolboxes@sha256:9a9e4d8f56e7792dffca1e2906d9399ff03ef87c9e2148983c9393fcbb8d7fb6` (llama.cpp 12405)
- Config backups: `/etc/evo-x3/llama-swap.yaml.bak-20261115-074229` (pre-morning) and `.bak-20261115-074634`.
- Config fixes applied this morning (official flags for this build):
  - `healthCheckTimeout: 900`
  - qwen27b thinking-mode sampling from the Unsloth/Qwen card: `--temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0`. Context stays native 262144, q8_0 KV (estimator ~50.95 GiB, fits).
  - gemma4-heretic and qwen27b: dropped `--no-mmap` (invalid on llama.cpp 12405) and set `--load-mode none -fa on`. Gemma sampling unchanged (`--temp 1.0 --top-p 0.95 --top-k 64`), context 65536.
  - embed-small: dropped `--no-mmap`; stays on 8083, context 8192.
  - flash-next: `gufo serve llm` (image has no ENTRYPOINT; bare `serve` is not on PATH). Context 32768, MTP on. Did not raise context because the load itself does not fit yet.
- Tailscale Serve / ACLs were not changed. Windows / BACKUP_OS / Recovery / EFI partitions were not touched. No BIOS changes. No money spent. No new Tailscale keys.

### 9.3 Completion / embedding tests (loopback, no API keys)

Script: `/home/derekboone/evo-x3/evo-model-tests.py`. Prompt: `Reply with exactly the word PONG and nothing else.` `max_tokens=16`. Results in `~/evo-x3/model-tests.json`.

| model | status | wall | prompt tok/s | gen tok/s | notes |
|---|---:|---:|---:|---:|---|
| embed-small | 200 | 1.33 s | — | — | 768-dim embedding of "EVO-X3 embedding smoke test" |
| qwen27b | 200 | 6.99 s | 45.52 | 11.21 | prompt_n=63, gen_n=16. Message content empty (thinking mode used the 16-token budget). |
| gemma4-heretic | 200 | 4.36 s | 61.56 | 45.47 | prompt_n=26, gen_n=16. Message content empty (same 16-token budget). |
| flash-next | 500 | 21.61 s | — | — | Gufo: `device allocation failed for blk.36.ffn_up_exps.weight (471859200 bytes)`. `host_available_mib≈60991`. Needs BIOS UMA 512 MB so the unified pool is ~120 GiB. No BIOS change made. |

llama-swap remained enabled and active on 127.0.0.1:8080 after the tests. embed-small stays resident in the "small" group.

### 9.4 sudoers

`/etc/sudoers.d/90-max-setup` is removed as the last step after the repo commit and push, then `sudo -n true` is verified to fail.

Repo commit (pushed to gitea derrick/evo-x3 main): `1758d4731d61c568fef5652f14f2eeb99dd29c3e`.

### 9.4 sudoers (done)

Removed `/etc/sudoers.d/90-max-setup` at 2026-11-15 after the repo push. `sudo -n true` now fails (exit 1). Passwordless sudo is gone.

Derrick restored `/etc/sudoers.d/90-max-setup` on 2026-11-15 at 08:19 CT so remaining admin gaps could be finished. It is removed again after the section 10 commit and push.

## 10. Morning closeout gaps (2026-11-15 08:22–08:24 CT)

Derrick restored passwordless sudo via `/etc/sudoers.d/90-max-setup` and explicitly asked to generate API keys, fix the hardware clock, and finish remaining admin gaps before removing sudo again.

### 10.1 Time
- Ran `timedatectl set-local-rtc 0` so the hardware clock stores UTC. Windows already has `RealTimeIsUniversal=1`.
- Timezone remains `America/Chicago` (CST, -0600). NTP is active and the system clock is synchronized.
- After the change, `timedatectl` showed local 08:22:13 CST, universal 14:22:13 UTC, RTC 14:22:13, `RTC in local TZ: no`, and the previous local-RTC warning was gone. Recheck at 08:24:23 CST was the same.

### 10.2 Cockpit
- Ran `systemctl disable --now cockpit.socket`. Socket is disabled and inactive. Port 9090 is closed (no listener in `ss`).

### 10.3 GRUB
- Backed up `/etc/default/grub` and `/boot/grub2/grub.cfg` to `/root/evo-x3-backups-20261115-082213/` on the host.
- Set `GRUB_TIMEOUT=3` and `GRUB_DEFAULT=0`, then ran `grub2-mkconfig -o /boot/grub2/grub.cfg`.
- UEFI BootOrder left at `0003,0000,0001` (Fedora first). os-prober still lists Windows Boot Manager; Windows partitions were not modified.

### 10.4 API keys
- Derrick's one-time override: generate the keys on the host rather than waiting for him to type them.
- Generated five unique 64-hex keys with `openssl rand -hex 32` and wrote them only to `/etc/evo-x3/llm.env` (mode 0600, owner root:root, SELinux `system_u:object_r:etc_t:s0`). Values were not printed, logged, committed, or copied off the host.
- Key names: `LLM_KEY_ALIENPC`, `LLM_KEY_PI`, `LLM_KEY_BOX`, `LLM_KEY_HERMES`, `LLM_KEY_DERRICK_LAPTOP`.
- Restarted `llama-swap.service`. The restart blocked briefly because leftover container `llama-swap-embed-small` ignored SIGTERM; it was SIGKILL'd so the unit could return. llama-swap is using the canonical config `/etc/evo-x3/llama-swap.yaml` (auth on) and is listening on `127.0.0.1:8080`.
- `/v1/models` verification on loopback, status codes only: `401` without a key, `200` with a key read from the file on the host.
- Derrick can copy the values from `/etc/evo-x3/llm.env` into Vaultwarden.

### 10.5 MES firmware debugfs check
- Kernel `7.3.3-200.fc44.x86_64`, `linux-firmware-20261019-1.fc44`, `amd-gpu-firmware-20261019-1.fc44`.
- `/sys/kernel/debug/dri/{0000:66:00.0,1,128}/amdgpu_firmware_info`: `MES feature version: 1, firmware version: 0x00000096` (MES_KIQ `0x00000075`). MES ≠ `0x83`. PASS. Versionlock was not applied in this session.

### 10.6 U2 backup image
- Derrick confirmed (2026-11-15, America/Chicago) that the U2 backup image already exists on the X3BACKUP USB. Recorded as done on that confirmation. This session did not re-verify image checksums or run a restore test.

### 10.7 Still waiting on Derrick
- BIOS: UMA 512 MB and Balanced 85 W (Flash-Next still cannot load). No BIOS change was made.
- Tailscale Serve / ACL: not changed; needs an explicit yes before publishing off loopback.

### 10.8 sudoers
- `/etc/sudoers.d/90-max-setup` is removed as the last step after the repo commit and push, then `sudo -n true` is verified to fail.
