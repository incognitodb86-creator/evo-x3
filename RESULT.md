# EVO-X3 Orchestrator Final Report (`RESULT.md`)

- **Generated:** 2026-11-15 (America/Chicago; system clock pre-sync reading, ~15 h ahead offset before `w32time` NTP sync)
- **Sources of Truth:** [orchestrator_full_20261114.md](file:///C:/evo-x3/orchestrator_full_20261114.md), [2026-11-11-evo-x3-setup-plan.md](file:///C:/evo-x3/2026-11-11-evo-x3-setup-plan.md) (rev 8), [2026-11-13-antigravity-evo-x3-stage-brief.md](file:///C:/evo-x3/2026-11-13-antigravity-evo-x3-stage-brief.md) (rev 5)
- **Lease:** Active (`Antigravity / Max Architect 3`), recorded in [evo-x3-lease.md](file:///C:/evo-x3/records/evo-x3-lease.md)
- **Safety:** Zero recovery keys, Windows licence keys, passwords, or hardware serials queried, printed, or stored. All STOP points respected. No changes made outside `C:\evo-x3\` (except non-elevated Windows timezone switch to `Central Standard Time`).

---

## Executive Summary & Live Hardware Facts
- **Machine:** GMKtec `EVO-X3`, `AMD RYZEN AI MAX+ 395 w/ Radeon 8060S` (16C / 32T), BIOS `EVO-X3_V1.01` (`ALASKA - 1072009`, `2026-06-16`)
- **Memory:** **128 GiB** physical soldered LPDDR5X-8000 (`8 × 16 GiB`, `P0 CHANNEL A`–`H` @ 8000 MT/s); `63.65 GiB` OS-visible in Windows due to factory 64 GiB BIOS UMA carveout (U3 BIOS step will lower UMA to `512 MB`)
- **Disk (`nvme0n1`):** Crucial `CT2000E100SSD8` (`1863.02 GiB`, GPT)
  - Part 1: EFI System (`100.0 MiB`, `IsSystem: True`, free space check requires Admin `mountvol S: /S`)
  - Part 2: MSR (`16.0 MiB`)
  - Part 3: `BACKUP_OS` FAT32 (`30.27 GiB`, `29.83 GiB` free)
  - Part 4: `C:` NTFS (`1831.46 GiB` total, **`78.37 GiB` used**, `1753.09 GiB` free)
  - Part 5: `Recovery` NTFS (`1.17 GiB`, `0.35 GiB` free)
- **OS & Build:** Windows 11 Pro `25H2` (`10.0.26200`, Build `26200.7840`), user `Derek` (non-elevated shell)
- **Security & Power (Pre-Admin):** `System.Volume.BitLockerProtection` on `C:` = `2` (**Off**); `UEFISecureBootEnabled` = `0` (**Off**); `HiberbootEnabled` = `0` (Fast Startup off); `Hibernate` = Available; `RealTimeIsUniversal` = `<absent>`
- **NICs:** `Wi-Fi 6` (`RZ717 WiFi 7 160MHz`) `Up` at `1.2 Gbps`; `Ethernet` (`Realtek PCIe 2.5GbE Family Controller`) `Disconnected` (`0 bps`)
- **Elevation Constraint Observed:** This `agy` execution shell has no interactive UAC desktop session; `Start-Process -Verb RunAs`, `winget install Git.Git`, and `winget install Tailscale.Tailscale` returned `ERROR_NOT_SUPPORTED` (`0x80070032`: cannot elevate). Official `Git.MinGit` v2.56.1 installed cleanly in user scope (`git init` + local commit succeeded), and all elevated Windows commands are consolidated in [run-elevated-prep.ps1](file:///C:/evo-x3/stage/run-elevated-prep.ps1) for Derrick to run in one Administrator PowerShell window.

---

## Complete Unit-by-Unit Status Table

| Unit | Description | Status | Timestamp (CT, pre-sync) | Evidence / Pass Test Result |
|---|---|---|---|---|
| **0a** | Clock (`Central Standard Time`, `w32time`, `w32tm /resync`) | **PARTIAL / BLOCKED-ON-DERRICK** | 2026-11-15 | `tzutil /s "Central Standard Time"` succeeded (`ExitCode: 0`); `w32time` start + `w32tm /resync` blocked on UAC (`0x80070032`). See [00-connectivity-and-backup.md](file:///C:/evo-x3/records/00-connectivity-and-backup.md). |
| **0b** | Install Git & Tailscale; `tailscale up` & tailnet DNS | **PARTIAL / BLOCKED-ON-DERRICK** | 2026-11-15 | `Git.MinGit` v2.56.1 installed (`DONE` for CLI `git`); full `Git.Git` & `Tailscale.Tailscale` installers downloaded/hash-verified by `winget` but failed elevation (`0x80070032`). Tailscale install + browser sign-in (`tailscale up`) require Admin PowerShell. See [00-connectivity-and-backup.md](file:///C:/evo-x3/records/00-connectivity-and-backup.md). |
| **0c** | `git init`, `.gitignore`, commit `"EVO-X3 Orchestrator"`, `gitea` remote, push | **DONE (local) / BLOCKED (push)** | 2026-11-15 | Repo initialized at `C:\evo-x3`, `.gitignore` excludes `iso/`, `drivers/`, `*.img`, `*.gguf`, `runs/*/agy.*`, remote `gitea` = `https://qnap.tailf242b2.ts.net/derrick/evo-x3.git`, local commit created. Push blocked on Tailscale sign-in + Household creating Gitea repo + Derrick GCM credentials. |
| **0d** | QNAP backup target (`qnap-target.md`) | **WAITING-ON-HOUSEHOLD** | 2026-11-15 | Target share name & free space are `NO_DATA`. Waiting items (drivers, stage, U2 Clonezilla image ≥ ~118 GiB, off-pool 2nd copy, A3 models) recorded in [qnap-target.md](file:///C:/evo-x3/records/qnap-target.md). |
| **A1** | Phase A runbook & Fedora setup script (`C:\evo-x3\stage\`) | **DONE** | 2026-11-15 | [RUNBOOK.md](file:///C:/evo-x3/stage/RUNBOOK.md), [setup-fedora.sh](file:///C:/evo-x3/stage/setup-fedora.sh), [compose-reference.yml](file:///C:/evo-x3/stage/compose-reference.yml) written; Podman + quadlets/systemd; quotes all pass tests. |
| **A2** | Phase A config templates (no secrets, no single default model) | **DONE** | 2026-11-15 | `ttm.conf`, 5 quadlets (`PIN_DIGEST_AT_BUILD_TIME`), `llama-swap` YAML (`flash-next`, `gemma4-heretic`, `qwen27b`, `captureBuffer: 0`, `${env.LLM_KEY_*}`), U14/U18 proxies, U17 sandbox wrapper, U18 egress firewall & quadlet, U12/U9b fixtures. See [Phase-A-stage.md](file:///C:/evo-x3/records/Phase-A-stage.md). |
| **A3** | Model downloads to QNAP | **DEFERRED** | 2026-11-15 | Deferred per brief rev 5 because QNAP share & free space are unconfirmed; download list staged in [RUNBOOK.md](file:///C:/evo-x3/stage/RUNBOOK.md) and [MANIFEST.md](file:///C:/evo-x3/stage/models/MANIFEST.md). |
| **A4** | Explicit untested Phase B gates list (`stage/README.md`) | **DONE** | 2026-11-15 | [README.md](file:///C:/evo-x3/stage/README.md) declares `"NOT YET RUN ON THE EVO"` and lists all untested GPU/Linux gates. |
| **Step 5** | Write `C:\evo-x3\stage\fedora-bootstrap.sh` | **DONE** | 2026-11-15 | Installs `agy`, copies stage tree, checks U3/U4/U4b prereqs, prints ordered U5–U20 next steps in [fedora-bootstrap.sh](file:///C:/evo-x3/stage/fedora-bootstrap.sh). |
| **Step 6** | Secret scan (`gitleaks` v8.30.1 + dry grep) | **DONE** | 2026-11-15 | `gitleaks dir C:\evo-x3\stage --redact -v`: **0 leaks** (`84.06 KB`); dry grep `sk-`, `tskey-`, `LLM_KEY_.*=`: **0 matches**; post-commit `gitleaks git` clean. See [secret-scan.md](file:///C:/evo-x3/records/secret-scan.md). |
| **B0 / U1** | Hardware & Windows read-only inventory | **PARTIAL / BLOCKED-ON-DERRICK** | 2026-11-15 | Non-elevated inventory complete in [U1-inventory.md](file:///C:/evo-x3/records/U1-inventory.md). Admin `mountvol S: /S` (ESP free ≥ 30 MB), `manage-bde -status C:`, `Confirm-SecureBootUEFI` require Admin (`run-elevated-prep.ps1`); 2.5GbE cable + UniFi DHCP reservation pending. |
| **B1 / U2** | Safe prep (`pnputil`, ISOs, imaging guide) | **PARTIAL / BLOCKED-ON-DERRICK** | 2026-11-15 | Clonezilla Live `3.3.3-37` ISO downloaded (`505,413,632` bytes) & SHA-256 verified (`3079458d926a37d3533e5d5caeb61b6e49c2dc69e2c97e0332ef37986bb3414f`). Non-elevated `pnputil` exported 7 drivers (`20.86 MB`); full export needs Admin. Fedora 44 ISO blocked by Anubis PoW anti-bot gate on `dl.fedoraproject.org`. USB creation & Clonezilla capture are STOP points. See [U2-prep.md](file:///C:/evo-x3/records/U2-prep.md). |
| **B2 / U2b** | Reversible Windows prep & shrink | **PARTIAL / BLOCKED-ON-DERRICK** | 2026-11-15 | Fast Startup already `0`. Hibernation off, `RealTimeIsUniversal=1`, and manual Windows Update staged in `run-elevated-prep.ps1` (Admin needed). C: shrink (`~450 GB`) is a STOP point until U2 passes. See [U2b-windows-prep.md](file:///C:/evo-x3/records/U2b-windows-prep.md). |
| **RESIZE GATE** | Derrick `yes` card before Fedora installer touches disk | **STOP / BLOCKED-ON-DERRICK** | — | Hard stop waiting on U2 verified image, recovery USB boot test, BitLocker confirmation, and Derrick `yes` card. |
| **B3 / U3** | BIOS (UMA 512 MB, SMT, IOMMU on, AC Power On, 85 W, Secure Boot) | **NOT-YET (BIOS / Fedora)** | — | Requires Derrick at physical BIOS (`EVO-X3_V1.01`). |
| **B4 / U4** | Fedora 44 Server install in free space (shared ESP, no LUKS, versionlock) | **NOT-YET (Fedora)** | — | Requires Derrick interactive Anaconda Custom/Blivet install after Resize Gate. |
| **U4b** | GRUB default Fedora 3 s, `efibootmgr`, 3 cold reboots, power-cut test | **NOT-YET (Fedora)** | — | Verified after U4 install. |
| **B5 / U5** | `ttm.conf` (`pages_limit=31457280`), Podman, `video`/`render`, `/dev/kfd` | **NOT-YET (Fedora)** | — | Staged in `setup-fedora.sh u5`. |
| **U6** | Gufo pinned quadlet + 4-arm bake-off (incl. `rocm-10.0-strix-llama`, cold TTFT, Vulkan fallback, 27B DFlash2) | **NOT-YET (Fedora)** | — | Quadlets & fixtures staged (`PIN_DIGEST_AT_BUILD_TIME`). |
| **U7** | `llama-swap` loopback (`127.0.0.1:8080`), no single default, per-caller keys | **NOT-YET (Fedora)** | — | Config staged in `config/llama-swap/config.yaml`. |
| **ACL GATE** | Derrick `yes` card for Tailscale ACL Preview + auth/API keys | **STOP / NOT-YET (Fedora)** | — | Hard stop before U8 Tailscale Serve. |
| **U8** | Tailscale Serve 443 (`Funnel` off), `tag:llm`, ACL, close LAN SSH | **NOT-YET (Fedora)** | — | Staged behind `--confirm-acl-card`. |
| **U9** | Fleet wiring (Forge/pi controller -> EVO `flash-next`; disable AlienPc Strata) | **NOT-YET (Fedora)** | — | Requires AlienPc lease, never during render. |
| **U9b** | Hermes Agent personal client (client only, `LLM_KEY_HERMES`, planted test) | **NOT-YET (Fedora)** | — | Starts once U8 is live; fixture staged. |
| **U10** | Keys (`0600`), gitleaks, snapper pre-update snapshots, Gitea push | **NOT-YET (Fedora)** | — | Key files created by Derrick on Fedora (`mcp.env`/`sandbox.env` before U17/U18). |
| **U12** | Agent serving profile (`q8_0` KV, `parallel=2`, `--no-slots`/401, cold TTFT fixture) | **NOT-YET (Fedora)** | — | Fixtures staged in `stage/fixtures/`. |
| **U19** | Day-1 A/B: IOMMU on vs `amd_iommu=off`, 85 W vs 140 W on U12 fixture; restore defaults | **NOT-YET (Fedora)** | — | Requires real EVO hardware & BIOS. |
| **U14** | Fair share & logging (`evo-rate-proxy`, `captureBuffer: 0`, CT key_id logs) | **NOT-YET (Fedora)** | — | Proxy & systemd unit staged. |
| **U16** | Hermes -> QNAP SearXNG (`:8888`) + planted injection test | **NOT-YET (Fedora)** | — | Waits on U9b + QNAP Docker/SearXNG back online. |
| **U17** | Rootless Podman code sandbox (`evosandbox` user, `--network=none`, fixed wrapper) | **NOT-YET (Fedora)** | — | Wrapper staged in `config/sandbox/evo-sandbox-run.sh`. |
| **U18** | Playwright MCP container + egress nftables + bearer proxy (loopback only) | **NOT-YET (Fedora)** | — | Quadlet, egress script & proxy staged. |
| **TOOLS PORT GATE** | Derrick `yes` card (Serve port, name, named callers) before U18 leaves loopback | **STOP / NOT-YET (Fedora)** | — | Hard stop before exposing U18 off `127.0.0.1`. |
| **U11** | Close (Alfred roster row on yes, release lease, final DONE/MISSING report) | **NOT-YET (Fedora)** | — | Requires U1–U19 done. |
| **U13** | Persistent `small` embedding group beside `flash-next` | **NOT-YET (Fedora)** | — | Runs after day-1 setup is live; YAML staged. |
| **U15** | Day-2 GLM-5.3-Flash bake-off vs `flash-next` | **NOT-YET (Fedora)** | — | Day-2 only; default unchanged without Derrick `yes`. |
| **U20** | Day-2 Gemma 4 26B A4B Heretic: PolyStrata `strata-poly` vs `kyuz0` llama.cpp + Prompt maker spot check | **NOT-YET (Fedora)** | — | Day-2 only; engine unchanged without Derrick `yes`. |

---

## Numbered Next Steps for Derrick (and Household) in Exact Order

1. **Run the Consolidated Administrator Prep Script on This PC:**
   Open **PowerShell as Administrator** (`Win+X` → Terminal (Admin)) and run:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File C:\evo-x3\stage\run-elevated-prep.ps1
   ```
   This single script fixes `w32time` NTP sync, installs full `Git.Git` and `Tailscale.Tailscale` from winget, launches `tailscale up` for your browser sign-in, checks `Confirm-SecureBootUEFI` / `manage-bde -status C:` / ESP free bytes (`mountvol S: /S`), exports all Windows drivers via `pnputil /export-driver * C:\evo-x3\drivers`, and applies reversible B2 Windows settings (`powercfg /h off`, `RealTimeIsUniversal=1`, manual Windows Update).
   - **Important:** Complete the Tailscale browser sign-in when it opens (never use an auth key) and confirm `tailscale status` and `Resolve-DnsName qnap.tailf242b2.ts.net` succeed.
   - Review `C:\evo-x3\records\elevated-prep-result.json` afterward to confirm ESP free space ≥ 30 MB and `manage-bde -status C:` = Fully Decrypted (and if BitLocker is ever enabled, confirm the recovery key is saved in **Vaultwarden** first). Also write down the Windows local account password.

2. **Connect Wired 2.5GbE & Push Config Repo to Gitea (Household + Derrick):**
   - Plug Ethernet into the EVO-X3's 2.5GbE port; **Household** adds the UniFi DHCP reservation and creates `derrick/evo-x3.git` on Gitea (`https://qnap.tailf242b2.ts.net/derrick/evo-x3.git`).
   - Once Tailscale & the Gitea repo are ready, run `git -C C:\evo-x3 push -u gitea main` and enter your credentials in Git Credential Manager.

3. **Household Confirms QNAP SMB Share & Space (for U2 Image, 2nd Copy, and A3 Models):**
   - **Household** names the QNAP SMB share and confirms free space (need **≥ ~118 GiB** for the U2 Clonezilla full-disk image + driver export, **plus** a second backup location off the degraded HDD2 pool, and **≥ ~132 GB + Heretic size** if staging A3 models on QNAP). Record it in `C:\evo-x3\records\qnap-target.md`.

4. **Download Fedora 44 Server ISO in Browser (Anubis Anti-Bot Gate):**
   - Open `https://dl.fedoraproject.org/pub/fedora/linux/releases/44/Server/x86_64/iso/Fedora-Server-dvd-x86_64-44-1.7.iso` and `https://dl.fedoraproject.org/pub/fedora/linux/releases/44/Server/x86_64/iso/Fedora-Server-44-1.7-x86_64-CHECKSUM` in a browser on this PC, save both into `C:\evo-x3\iso\`, and verify the SHA-256 hash matches.

5. **STOP POINT — Create & Boot-Test Windows Recovery USB + Capture Verified Clonezilla Full-Disk Image (U2):**
   - Create a Windows Recovery USB (`RecoveryDrive.exe` with system files) and test booting to its menu.
   - Flash `C:\evo-x3\iso\clonezilla-live-3.3.3-37-amd64.iso` (already SHA-256 verified) to a USB stick (Rufus / Fedora Media Writer), boot it in UEFI mode, and `savedisk` the entire `nvme0n1` drive to the QNAP share alongside `C:\evo-x3\drivers\` and `C:\evo-x3\stage\`.
   - Run Clonezilla's restore verification (`ocs-chkimg` / `-scr`), record checksums & verify = OK, and save the **second copy** off the degraded QNAP pool.

6. **Complete U2b Full Shutdown & Shrink `C:` in Disk Management:**
   - Ensure you did a full **Shut down** (not Restart) after `powercfg /h off`.
   - Open **Disk Management (`diskmgmt.msc`)** → right-click `C:` → **Shrink Volume** → target `C:` = **~450 GB** (`~460,800 MB`, leaving ≥ 100 GB free inside Windows and **~1.38 TB unallocated**). Do NOT use GParted.

7. **STOP POINT — RESIZE GATE Card:**
   - Confirm in writing (`yes` card) that: U2 Clonezilla image checksum & restore check passed, 2nd copy is handled, recovery USB boot-tested, BitLocker is off (or key in Vaultwarden), partition layout is verified, and *"the bots have no AI server whenever the box is in Windows."*

8. **STOP POINT — U3 BIOS + U4/U4b Fedora 44 Server Dual-Boot Install:**
   - Enter BIOS (`EVO-X3_V1.01`): set **UMA = 512 MB** (not Auto), **SMT On**, **IOMMU/SVM On**, **Above 4G On** (if shown), **Restore on AC Power Loss = Power On**, **Power Mode = Balanced 85 W**, **Secure Boot On** (allow Microsoft 3rd Party UEFI CA if needed). Record the one-time boot menu key.
   - Flash `Fedora-Server-dvd-x86_64-44-1.7.iso` to USB and boot UEFI.
   - In Anaconda **Custom / Blivet**: use **unallocated free space only** (`/boot` 2 GiB ext4 + btrfs pool with `/`, `/home`, `/srv/models`), mount existing `nvme0n1p1` at `/boot/efi` with **Reformat UNTICKED**, no LUKS, headless (`multi-user.target`), SSH key-only, root locked.
   - After boot: confirm kernel ≥ `6.18.4`, `linux-firmware` ≥ `20260110`, MES ≠ `0x83`, run `sudo dnf versionlock add 'kernel*' linux-firmware`, configure GRUB (`GRUB_DEFAULT=0`, `GRUB_TIMEOUT=3`, `os-prober`), set `efibootmgr` Fedora first, and pass 3 cold reboots + 1 AC power-cut test + `grub2-reboot` to Windows & back.

9. **First Fedora Boot — Run `fedora-bootstrap.sh` and Continue Orchestrator on Fedora:**
   - Copy or mount `stage/` on Fedora and run `bash fedora-bootstrap.sh` to install `agy`, copy `/opt/evo-x3/stage`, verify U3/U4/U4b facts, and launch the Fedora Orchestrator from **U5 onward** (stopping at **ACL GATE** before U8 and **TOOLS PORT GATE** before exposing U18 off loopback, and never changing defaults after U15/U19/U20 without your `yes` card).
