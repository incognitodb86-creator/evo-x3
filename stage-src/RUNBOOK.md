# EVO-X3 Setup Runbook (Plan rev 8 + Brief rev 5)

> **Not yet run on the EVO.** Execute units strictly in the order below. Record every live pass test with `America/Chicago` (CT) timestamps in `40_projects/compute-expansion/records/` (and `C:\evo-x3\records\` / `/opt/evo-x3/records/`). Keep the EVO-X3 shell lease active until U11 closes.

---

## Execution Order
`U1 → U2 → U2b → [RESIZE GATE] → U3 → U4 → U4b → U5 → U6 → U7 → [ACL GATE] → U8 → U9 → U9b → U10 (keys) → U12 → U19 → U14 → U16 → U17 → U18 (loopback) → [TOOLS PORT GATE] → U10 (rest) → U11 → U13 → U15 (day-2) → U20 (day-2)`

---

## Phase B: Windows Prep, Backup & Dual-Boot Install

### B0 / U1. Day-1 Unboxing & Inventory
- Confirm BIOS shows 128 GiB LPDDR5X-8000 and 2 TB NVMe (`CT2000E100SSD8`), BIOS `EVO-X3_V1.01`.
- Connect wired 2.5GbE; Household adds UniFi DHCP reservation.
- Write down Windows local account password (turning BitLocker off can disable PIN/Hello sign-in).
- From **Administrator PowerShell**, run `C:\evo-x3\stage\run-elevated-prep.ps1` (or manually check `manage-bde -status C:`, `Get-BitLockerVolume`, `Confirm-SecureBootUEFI`, and `mountvol S: /S` to verify ESP free ≥ 30 MB, then `mountvol S: /D`).
- **If BitLocker/Device Encryption is ON:** Derrick saves the recovery key to Vaultwarden **before** anything touches it. Never store recovery keys in files or chat.
- **Pass:** BIOS facts, partition table, ESP size/free, `C:` used space, and BitLocker state recorded; key in Vaultwarden (or confirmed off).

### B1 / U2. Full-Disk Image + Recovery USB (Before Any Partition Change)
- **Prerequisite:** Household confirms QNAP SMB share name and ≥ ~100 GB free (≥ 1.5× `C:` used ≈ 118 GiB), **plus** a second off-pool backup location (QNAP Data pool HDD2 is degraded).
- **Safe Windows preps already staged:**
  - Clonezilla live ISO verified in `C:\evo-x3\iso\clonezilla-live-3.3.3-37-amd64.iso` (SHA-256 `3079458d926a37d3533e5d5caeb61b6e49c2dc69e2c97e0332ef37986bb3414f`).
  - Export all drivers via `pnputil /export-driver * C:\evo-x3\drivers` (Admin PowerShell).
  - Download Fedora 44 Server x86_64 DVD ISO in Derrick's browser (Anubis PoW challenge on `dl.fedoraproject.org`) and verify against `Fedora-Server-44-1.7-x86_64-CHECKSUM`.
- Create **both**:
  1. GMKtec / Windows recovery USB (`RecoveryDrive.exe`), and test booting it to its menu.
  2. Boot Clonezilla live USB and capture a **full-disk** image of `nvme0n1` (all 5 partitions, incl. ESP and Recovery) to the QNAP share, copying `C:\evo-x3\drivers` beside it.
- Run Clonezilla **"check image restorable"** (`ocs-chkimg`), record checksum + verify output, and place the second copy off the degraded pool.
- **Pass:** Image + driver export on QNAP; checksum and verify = OK; recovery USB boots to its menu; second copy noted (or Derrick accepts risk in writing).

### B2 / U2b. Windows Prep for Dual Boot
1. Confirm BitLocker / Device Encryption is **Off / Fully Decrypted** (`manage-bde -status C:`).
2. Turn off Fast Startup (`HiberbootEnabled` = 0) and run `powercfg /h off` (Admin). Then perform a full **Shut down** (not Restart).
3. Set Windows RTC to UTC: `reg add "HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\TimeZoneInformation" /v RealTimeIsUniversal /d 1 /t REG_DWORD /f` (leave `w32time` sync active).
4. Set Windows Update to manual / notify (`AUOptions` = 2, `NoAutoRebootWithLoggedOnUsers` = 1) — attended updates only.
5. **Shrink `C:` (only after U2 verified):** Open `diskmgmt.msc` → Shrink `C:` so `C:` ends at **~450 GB** (`~460,800 MB`, leaving ≥ 100 GB free inside Windows). Never use GParted or Anaconda to shrink NTFS. Leave freed space **unallocated**.
- **Rollback:** Extend `C:` back into unallocated space; re-enable settings.
- **Pass:** `manage-bde -status` = Fully Decrypted or None; `powercfg /a` shows hibernation unavailable; Fast Startup unticked; `RealTimeIsUniversal` = 1; Disk Management shows `C:` ≈ 450 GB + ~1.4 TB unallocated; Windows boots cleanly.

### HARD STOP: RESIZE GATE
> **STOP.** Present Derrick with the resize card citing: (1) U2 Clonezilla checksum & restore-verify result, (2) recovery USB boot-tested, (3) BitLocker = Off and key stored if applicable, (4) planned partition layout table, and (5) explicit note: *"the bots have no AI server whenever the box is in Windows."* Wait for Derrick's **`yes`** before booting the Fedora installer.

### B3 / U3. BIOS Settings
- Enter BIOS (`EVO-X3_V1.01`):
  - **UMA Frame Buffer Size:** smallest explicit value (**512 MB**, NOT Auto).
  - **SMT:** On.
  - **IOMMU / SVM:** On (Q10 default; do not leave off after U19 without a card).
  - **Above 4G Decoding:** On (if shown).
  - **Restore on AC Power Loss:** **Power On** (N9).
  - **Power Mode:** **Balanced 85 W** (Q8 default; fan curve default first).
  - **Secure Boot:** Leave **ON** (enable "Microsoft 3rd Party UEFI CA" / "Allow 3rd-party CA" if Fedora USB refuses to boot; disabling Secure Boot is last resort).
- **Pass (verified after U4b):** `mem_info_vram_total` ≈ 0.5 GiB; `mokutil --sb-state` recorded.

### B4 / U4. Fedora 44 Server Install (Free Space Only)
- Boot Fedora 44 Server USB in **UEFI mode**.
- **Installation Destination:** 2 TB NVMe → **Custom (Advanced / Blivet-GUI)**. NEVER pick "Reclaim space" or "Delete all".
- **Partitions in unallocated space ONLY:**
  - `/boot`: **2 GiB ext4**
  - btrfs pool in remaining free space (~1.4 TB) with subvolumes: `/` (`root`), `/home` (`home`), and `/srv/models` (own subvolume, excluded from snapper).
  - **Existing EFI System Partition (`nvme0n1p1`):** select mount point `/boot/efi` with **Reformat UNTICKED**. Do not create a second ESP. Do not touch `C:`, MSR, or Recovery.
  - Read the summary screen carefully before accepting: **only new partitions** may be created, zero existing partitions destroyed.
- **No LUKS encryption** (Q13 = A). Headless (`multi-user.target`). SSH key-only, root locked, admin user with `sudo`.
- Verify post-install: kernel ≥ `6.18.4`, `linux-firmware` ≥ `20260110`, MES ≠ `0x83` in `/sys/kernel/debug/dri/*/amdgpu_firmware_info`.
- Pin updates: `sudo dnf versionlock add 'kernel*' linux-firmware`.
- **Pass:** Key-only SSH works; versions recorded; `dnf versionlock list` shows both; no desktop (`systemctl get-default` = `multi-user.target`); `lsblk -f` shows Windows partitions untouched.

### U4b. Boot Menu, Power-Cut & Recovery Checks
- `/etc/default/grub`: `GRUB_DEFAULT=0`, `GRUB_TIMEOUT=3`, `GRUB_DISABLE_OS_PROBER=false`. Ensure `os-prober` is installed; run `sudo grub2-mkconfig -o /boot/grub2/grub.cfg` and confirm `"Windows Boot Manager"` appears.
- Firmware order: `sudo efibootmgr -o <fedora>,<windows>` (Fedora first, Windows second; match BIOS boot tab).
- Record exact BIOS one-time boot menu key.
- **Windows-update boot-hijack recovery procedure:**
  1. Press BIOS one-time boot key → pick `Fedora` → run `sudo efibootmgr -o <fedora>,<windows>`.
  2. If the Fedora EFI entry was erased, boot Fedora USB → Troubleshooting → Rescue → `chroot /mnt/sysroot` → `dnf reinstall shim-* grub2-efi-*` → `efibootmgr -c -d /dev/nvme0n1 -p 1 -L Fedora -l '\EFI\fedora\shimx64.efi'`. (Prefer this over `bcdedit /set {bootmgr} path \EFI\fedora\shimx64.efi`.)
  3. Always verify Fast Startup is still off in Windows after any Windows feature update.
- **Pass:** 3 cold reboots land in Fedora; 1 physical AC power-cut test boots unattended into Fedora; `sudo grub2-reboot "<Windows Boot Manager entry>"` boots Windows with accurate UTC-synced time; next boot returns to Fedora with `timedatectl` showing RTC in UTC (no local-RTC warning).

---

## Phase A3: Deferred Model Download List (Pull on QNAP Once Space Confirmed, or Direct to `/srv/models` on Fedora)

> **A3 Status:** DEFERRED because Household QNAP SMB share and free space are unconfirmed (`NO_DATA`).

| Logical Model Name | Hugging Face Repo / Variant | Expected On-Disk Size | Routing Role (Brief rev 5) |
|---|---|---|---|
| `flash-next` | `unsloth/Qwen3.8-Flash-Next-GGUF` (`UD-Q4_K_XL`) + shared Q8_0 MTP head (`mtp-...-shared-Q8_0`) | **111.3 GB** + **2.79 GB** | Coding, general, tools, long context (262K max) |
| `gemma4-heretic` | `Gemma 4 26B A4B Heretic` (`gemma4_heretic_poly_think` / GGUF) | **`NO_DATA`** (measure live before copying) | Writing (prompts, fiction, uncensored) |
| `qwen27b` | `unsloth/Qwen3.8-27B-GGUF` (`UD-Q4_K_XL`) | **17.6 GB** | Dense fallback & U6 DFlash2 test |

- Verify every downloaded file with `sha256sum` and record digests in `/srv/models/SHA256SUMS` using `stage/models/verify-models-sha256.sh`.

---

## Phase B (Linux): GPU, Inference Stack, Security & Tests

### B5 / U5. GPU Memory & Devices
- Run `sudo /opt/evo-x3/stage/setup-fedora.sh u5`: installs `/etc/modprobe.d/ttm.conf` (`options ttm pages_limit=31457280`), runs `dracut --force`, installs `podman`, adds service user to `video` and `render`, reboot.
- **Pass:** `cat /sys/module/ttm/parameters/pages_limit` = `31457280`; `mem_info_gtt_total` ≈ 120 GiB; `/dev/kfd` and `/dev/dri/renderD*` exist.

### U6. Engine Quadlet & 4-Arm Bake-Off
- Pin live image digests in `config/quadlets/*.container` (replace `PIN_DIGEST_AT_BUILD_TIME` via `skopeo inspect` / `podman pull`). NEVER run the `pwilkin/strix-halo` installer directly.
- Run bake-off on the 3 Forge-style tasks (coding fix, tool-call chain, long-context read) plus cold Hermes-sized TTFT prompt (no warmup, `U12` fixture) across all 4 arms one at a time:
  1. `Gufo` (`ghcr.io/gufo-org/toolboxes/gufo-runtime` or `kyuz0/amd-strix-halo-toolboxes:rocm-10.0-gufo`) — plan pick Q3=A
  2. `Halogen` (set server-side reasoning effort low/medium; beware xhigh default)
  3. `Strata`
  4. `kyuz0/amd-strix-halo-toolboxes:rocm-10.0-strix-llama` (recorded 4th arm; NOT a default)
- Also test: Vulkan RADV fallback serving `qwen27b` once (`-fa 1 --load-mode none`), and `qwen27b` long-context decode **with and without DFlash2**, and record measured `gemma4-heretic` tok/s.
- **Pass:** Logs show `gfx1151`, not CPU; Flash-Next at 32K ≥ 35 tok/s decode and ≥ 800 tok/s prefill; 4-arm table recorded incl. cold TTFT; Vulkan fallback answers once; 27B DFlash2 pair recorded; Heretic tok/s measured and recorded.

### U7. llama-swap Front Door
- Deploy `config/llama-swap/config.yaml` (no single implicit default; callers pick `flash-next`, `gemma4-heretic`, or `qwen27b` by name) on `127.0.0.1:8080`, proxying to `127.0.0.1:8081`.
- Derrick creates `LLM_KEY_*` values in Vaultwarden and writes `/etc/evo-x3/llm.env` (`0600`, `root:root`). Never store keys in git.
- Keep firewalld closed for `8080` and `8081`.
- **Pass:** `ss -ltnp` shows `8080` and `8081` on `127.0.0.1` only; LAN `curl <lan-ip>:8080` refused; `/v1/models` with key lists models, without key = `401`; by-name completion for `flash-next` and `gemma4-heretic` succeeds after reboot.

### HARD STOP: ACL / REMOTE-ACCESS GATE
> **STOP.** Before running U8, Household backs up the current Tailscale policy (masking hostnames), adds `tagOwners: {"tag:llm": ["autogroup:admin"]}`, adds the `tcp:443` whole-tailnet grant (`autogroup:member`, `tag:box`, `<AlienPc tag>`, `<pi tag>` → `tag:llm`), admin-only `:22` SSH, and ACL deny tests, previews, and sends the **ACL / remote-access card** to Derrick for **`yes`**.

### U8. Tailscale Serve + Firewalld Lock
- Derrick generates a one-off pre-tagged `tag:llm` auth key (≤ 1 h expiry), types it once for `sudo tailscale up --hostname=<neutral-name> --auth-key=...` (never saved). Do not run Tailscale on the Windows side under the same name.
- Point `tailscale serve --bg 443` → `http://127.0.0.1:8080` (later behind U14 rate proxy on `127.0.0.1:8082` → `8080`, or proxy on `8080` and llama-swap on `8082`). Funnel OFF. Close LAN SSH in firewalld.
- **Pass:** (1) LAN curl to `:8080` and `:8081` refused; `ss -ltnp` loopback only; (2) tailnet curl without key → `401`; (3) tailnet curl with key succeeds from AlienPc, pi, box, and Derrick's device; (4) ACL tests pass; (5) `tailscale funnel status` empty; (6) LAN SSH refused.

### U9 & U9b. Fleet Wiring & Hermes Personal Client
- **U9 (Max Architect 3, under AlienPc lease, never during a render):** Point Forge/pi controller at EVO Tailscale Serve URL (`flash-next`); disable (do not delete) AlienPc Strata Swift-1.5 entry until 7-day check passes.
- **U9b (starts right after U8 passes):** On Derrick's personal machine, configure Hermes Agent as **client only** (no managed llama.cpp) using EVO Serve URL + `LLM_KEY_HERMES`. Keep `approvals.mode: manual` until U17 sandbox is live; treat all browsed/searched output as untrusted (`KTD11a`).
- **Pass:** Forge job appears in EVO logs while AlienPc `nvidia-smi` shows only ComfyUI; Hermes returns chat via EVO with zero local `llama-server`, and planted `"run this"` text produces no command without approval.

### U10 (Keys First), U12, U19, U14, U16, U17, U18
1. **U10 (keys):** Create distinct `0600` files for U17 sandbox key and U18 `MCP_KEY_<caller>` (never reuse `LLM_KEY_*`), unreadable by `evosandbox`. Set 90-day rotation reminder.
2. **U12 (Agent serving profile):** Configure chat template/tool parser, `q8_0` KV cache, prefix cache on, `--no-mmap`, flash-attention, `parallel=2`, known per-slot context, `--no-slots` (or confirm `401` on `/slots`). Run `fixtures/u12-tool-call-fixture.json` (must return structured `tool_calls` across overlapping `pi` + `hermes` requests without unloading) and `fixtures/u12-cold-ttft-prompt.py` (no warmup, ~18k tokens).
3. **U19 (Day-1 A/B — defaults unchanged):** On U12 Flash-Next fixture (incl. cold TTFT): (a) IOMMU on vs `amd_iommu=off` (record NPU/USB4 dock visibility, then **remove `amd_iommu=off` and reboot back to IOMMU on**); (b) BIOS Balanced 85 W vs 140 W (record hwmon/`sensors` temp and noise if readable else `NO_DATA`, then **restore Balanced 85 W**).
4. **U14 (Fair share & logs):** Enable `evo-rate-proxy` (`systemd`) for per-key rate limiting + `captureBuffer: 0` + key-ID-only CT logging (verify burst on `hermes` gets queued/429 while `pi` completes, and grep finds zero prompt text or key prefixes in logs).
5. **U16 (Hermes → QNAP SearXNG):** Wait until QNAP Docker/SearXNG is back; verify `pi` and Hermes searches work on port `8888` and planted `"run this"` test still holds.
6. **U17 (Rootless Podman Sandbox):** Create dedicated unprivileged user `evosandbox` with subuid/subgid range and zero access to `/etc/evo-x3/*`, `/srv/models`, or `~/.ssh`. Deploy `config/sandbox/evo-sandbox-run.sh` (`--cap-drop=ALL`, `--security-opt no-new-privileges`, `--read-only`, bounded `--tmpfs /tmp`, `--network=none`, `--cpus`, `--memory`, `--pids-limit`, `timeout`). Pass all 7 U17 checks.
7. **U18 (Playwright MCP — Loopback Until Tools Port Card):** Deploy `config/playwright/playwright-mcp.container` + `playwright-egress-firewall.sh` (separate podman network dropping RFC1918, `100.64.0.0/10`, link-local, and host IPs) behind `evo-mcp-proxy.service` checking `MCP_KEY_<caller>`. Keep `--isolated` and `--allowed-hosts <serve-name>`.

### HARD STOP: TOOLS PORT GATE
> **STOP.** Keep U18 bound strictly to `127.0.0.1` until Derrick approves a Tools Port card specifying the Serve port, Serve name, and **named callers** on its ACL.

### U10 (Rest), U11, U13, U15 (Day-2), U20 (Day-2)
- **U10 (rest):** Run `gitleaks dir --redact`, verify `snapper` pre-update snapshot + `dnf versionlock` workflow, test clean rebuild from repo.
- **U11:** Confirm U1–U19 done, Alfred roster row on Derrick's yes, release lease file, commit & push.
- **U13 (after day-1 live):** Switch to `config/llama-swap/config-u13-with-small-group.yaml` (`main` `swap: true`, `small` `swap: false`, `persistent: true`) and verify `/v1/embeddings` responds without unloading `flash-next`.
- **U15 (day-2):** Test `GLM-5.3-Flash` standalone 128 GB fit + U12 fixture vs `flash-next` (do not change default without Derrick's card).
- **U20 (day-2):** Compare `Gemma 4 26B A4B Heretic` on PolyStrata `strata-poly` (HIP experimental; record explicit failure if it won't build/run on `gfx1151`) vs `kyuz0` llama.cpp Vulkan RADV, plus Prompt maker spot check (do not change writing engine without Derrick's card).
