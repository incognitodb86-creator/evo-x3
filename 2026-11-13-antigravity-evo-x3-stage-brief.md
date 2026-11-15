---
id: antigravity-evo-x3-stage-brief
title: Antigravity brief — stage the EVO-X3 Fedora setup now; build on the box when it arrives
author: Scout (Research & Planning) · read-only; this file only; no install, no lease, no messages, no secrets
date: 2026-11-13 · ~8:15 PM CT · rev 2 ~8:21 PM CT folds Max Architect 3 review (RELAYED, 8:20 PM CT) · rev 3 ~8:23 PM CT folds Derrick t311s1125, t312u, t313u · rev 4 11:44 AM CT Nov 14 folds plan rev 7 A/B tests (t322u/t323u) · rev 5 6:49 PM CT Nov 14 folds plan rev 8 (t327u)
asked_by: Derrick t309u ("Go") after t303u–t308u; model routing t311s1125, t312u, t313u (8:22–8:23 PM CT)
audience: Antigravity (Agy; already on AlienPc). Stage now on AlienPc / the QNAP. Build on the EVO after order GMKUS42137 arrives. Max Architect 3 reviewed this brief at 8:20 PM CT (PASS, with a later default-model placeholder; Derrick's routing answer is folded here). Scout never takes the AlienPc or EVO lease.
status: BRIEF REVISED (rev 5). Stage now is reversible file work. There is no single default model; routing is below. Model staging covers both models and starts only after Household confirms QNAP space. On-box install waits for the EVO, the verified Windows image, and Derrick's resize / ACL / tools-port cards. Plan rev 8 adds cold TTFT, a recorded fourth U6 bake-off arm, and a 27B DFlash2 long-context test; defaults stay until a later card.
tier: carries out the approved T2 EVO-X3 setup plan rev 8; does not replace it
source_of_truth: 40_projects/compute-expansion/plans/2026-11-11-evo-x3-setup-plan.md (rev 8, Fleet Reviewer @ 97d7db4 folded in rev 6; R13–R15 / U19–U20 from t322u/t323u; R16 / TTFT, fourth U6 arm, DFlash2 test from t327u)
review_of_brief: Max Architect 3, RELAYED 8:20 PM CT Nov 13 — PASS, default-model placeholder folded in rev 2; rev 3 replaces that placeholder with Derrick's routing (t311s1125, t312u, t313u)
standing_rules: 10_packs/fleet/derricks-standing-rules.md (link, do not restate)
order: GMKUS42137 (GMKtec EVO-X3, Ryzen AI Max+ 395, 128 GB, 2 TB SSD)
pending_upload: true
---

# EVO-X3 stage now, build on arrival (Antigravity) — one page

**Job, two phases.** **Stage now** (on AlienPc and the QNAP, no EVO required): write the setup script, Podman/quadlet (and compose-equivalent) files, llama-swap config with `${env.…}` placeholders only, and a runbook. **Model staging covers both models below, and starts only after Household confirms there is space on the QNAP.** **Build on arrival:** image Windows to the QNAP + one recovery USB, shrink Windows, install **Fedora 44 Server** dual-boot on the **same 2 TB SSD**, then run the staged script and pull models from the QNAP.

**Why not "install on AlienPc and swap the drive":** Derrick asked (t303u) whether the Strix Halo system could be built and Docker-tested on AlienPc so "when it comes in I can just swap them." **No.** AlienPc is Intel + NVIDIA. The EVO is AMD Strix Halo (ROCm / Vulkan). Windows Docker / WSL on either box **cannot** reach the AMD iGPU for ROCm, so any speed you measure there will not carry over. The 9100 PRO stays on AlienPc (plan Q9 = A; also the AlienPc Ubuntu brief). The EVO keeps its factory 2 TB drive and dual-boots on that disk (R8).

**Keep every plan rev 8 pick, except there is no single default model.** Fedora 44 Server, headless, btrfs, **no Linux encryption** (Q13). **Gufo** after a day-1 bake-off vs Halogen and Strata, with a recorded fourth U6 arm (kyuz0 `rocm-10.0-strix-llama` toolbox, not a default; do not run the pwilkin installer) and kyuz0 llama.cpp Vulkan-RADV as fallback. **Model routing (Derrick, t311s1125, t312u, t313u, 8:22–8:23 PM CT):** the EVO has no single default model; requests are routed by task. Writing (prompts, fiction, uncensored) goes to **Gemma 4 26B A4B Heretic**. Everything else (coding, general, tools, long context) goes to **Flash-Next**. Callers pick a model by name through llama-swap. Plan rev 6 had named Flash-Next UD-Q4_K_XL (111.3 GB) + shared Q8 MTP head (2.79 GB) as the only default, with Qwen3.8-27B UD-Q4_K_XL (17.6 GB) as fallback; Max later relayed t1381u as dropping Flash-Next. Derrick's 8:22–8:23 PM CT answer keeps **both** and routes by task. Heretic's on-disk size is **NO_DATA** until measured. BIOS: **Balanced 85 W**, **IOMMU/SVM on**, UMA 512 MB, Restore on AC power loss = Power On, Secure Boot left on. Those Q8/Q10 values were starred defaults accepted via t225s813, not individual picks; plan U19 measures IOMMU on vs `amd_iommu=off` and 85 W vs 140 W, including cold TTFT on the U12 Hermes-sized fixture, and U20 compares Gemma Heretic on PolyStrata `strata-poly` vs kyuz0 llama.cpp. **Defaults stay until a later Derrick yes.** Endpoint: engine `127.0.0.1:8081`, llama-swap `127.0.0.1:8080` (loopback only), published only through **Tailscale Serve** on 443 to the **whole tailnet**; **per-caller API keys**, no key = 401. Derrick holds the keys in **Vaultwarden** and types them himself. Windows shrinks to **~450 GB**; Fedora is the **default boot** (GRUB, 3-second timeout). While the box is in Windows, the bots have no AI server.

**Why Antigravity:** "Can antigravity do it to save usage?" (t305u) and "build both now and save to qnap" (t308u, then t309u "Go"). Agy stages the files now. Model downloads for **both** Heretic and Flash-Next wait only for Household to confirm QNAP space. GPU-dependent steps wait for Fedora on the real box. Max or Fleet Reviewer signs off; Agy does not self-certify.

**Community way:** headless Fedora + kyuz0 Strix Halo Toolboxes (Gufo / Vulkan RADV), `ttm pages_limit` (not `amdgpu.gttsize`), loopback engine + a front door, models on a local Linux filesystem. → **reuse** the plan rev 8 community line (opened 2026-11-11; PolyStrata Strix Halo docs and kyuz0 `rocm-10.0-strix-llama` README opened 2026-11-14 CT).

---

## Derrick's asks (t303u–t313u, his words where possible)

| ID | When | Derrick's words | This brief does |
|---|---|---|---|
| R1 | t303u | "install the stryx halo system and stuff test it in docker so when it comes in I can just swap them" | **Stage** the system now; **do not** claim a Docker test on AlienPc is an EVO test. No drive swap. |
| R2 | t303u | "Can we backup the os system to my qnap instead of a flash driv" | **Both:** full factory-SSD image **on the QNAP**, plus **one** recovery USB (plan Q7 = A). Image is taken **on the EVO after it arrives**, before any shrink. |
| R3 | t304u | "can you do that in windows and docker in the stryx and then just dual boot it?" | **No** for GPU work. Windows Docker/WSL will not drive ROCm on the AMD iGPU. Dual boot is still the plan, on Fedora, after the image. |
| R4 | t305u, t308u, t309u | "Can antigravity do it to save usage?" · "build both now and save to qnap" · **"Go"** | Agy writes the staged tree now. Model downloads start only after Household confirms QNAP space. On-box build waits for arrival. |
| R5 | t311s1125, t312u, t313u (8:22–8:23 PM CT) | No single default model; writing (prompts, fiction, uncensored) to Gemma 4 26B A4B Heretic; everything else (coding, general, tools, long context) to Flash-Next; callers pick a model by name through llama-swap. | Recorded as the routing. Stage **both** models, only after Household confirms QNAP space. |

---

## Hard stops (both phases)

- **Never take or override** the AlienPc lease / gpu_lock while staging on AlienPc, or the EVO lease once that box exists. Check `30_handoff/status/*lease*` and gpu_lock first. Staging file work on the QNAP does not need the GPU; **do not** use AlienPc's GPU for EVO tests. Tonight the AlienPc lease is held overnight for the H3 render queue (see the AlienPc brief); do not use that GPU until it is released.
- **No secrets in files:** llama-swap and systemd unit files use `${env.LLM_KEY_*}` / `EnvironmentFile` placeholders only. Derrick types every key and the Tailscale join key from Vaultwarden. No Windows licence, BitLocker key, password, or serial in the brain.
- **Ask Derrick before anything irreversible** on the EVO: the **resize card** (Fedora install into free space) only after a verified image + recovery USB exist and the BitLocker key is in Vaultwarden; the **ACL / remote-access card** before publishing the LLM endpoint; the **tools-port card** before Playwright MCP leaves loopback (named callers only — whole-tailnet applies to the LLM endpoint, not tools).
- Do not shrink NTFS with GParted or the Fedora installer. Do not reformat the existing EFI partition or add a second ESP. Do not touch C:, MSR, or Recovery. No Linux LUKS.
- **Do not download EVO models** until Household confirms there is space on the QNAP for **both** Gemma 4 26B A4B Heretic and Flash-Next (and the plan's Flash-Next MTP head). Do not invent Heretic's size.
- GPU-dependent steps (**Gufo / ROCm or Vulkan install, `ttm` check, bake-off, tok/s**) run **only on Fedora on the real EVO**. Do not invent tok/s. For Flash-Next, use the plan's pass bars: Flash-Next at 32K ≥ 35 tok/s decode and ≥ 800 prefill, log shows **gfx1151** not CPU; also record cold TTFT on a Hermes-sized long prompt with no warmup (the video's 55 s → 19.4 s figure is the author's claim, not an EVO target). For Heretic, record measured tok/s and do not invent a bar.
- QNAP Data pool is **degraded until HDD2 is replaced**. Keep a **second copy of backup images** somewhere else. Confirm free space before large downloads (see open questions). Do not fill the last of the pool.
- Stop and ask if: the image will not verify, Windows will not shrink to ≤ ~500 GB, the ESP has < 30 MB free, the engine falls back to CPU, or anything needs money.

---

## Phase A — stage now (AlienPc / QNAP)

No Fedora install, no BIOS changes, no AlienPc GPU, no keys in files, **no model downloads until Household confirms QNAP space**. Write into a single staged tree on the QNAP (share name **NO_DATA** — ask Household) and keep a copy in `40_projects/compute-expansion/` only if it contains **no secrets**.

### A1. Runbook and setup script
- One scripted path that implements plan units U5–U8, U10 (config/backups, not the secret values), U12, U14, and the day-1 pieces of U9b/U17/U18 **as files**, to be run on Fedora after U4b. Each unit keeps the plan's pass test. Pin container images **by digest**. Models are read-only from `/srv/models`.
- Runtime on the EVO is **Podman + quadlets/systemd**, as in the plan — not Windows Docker. A compose file may exist as documentation, but the live units are quadlets.
- **Pass:** a reviewer can read the script top to bottom and see U5→U8 in order, with pass tests quoted from the plan; `gitleaks dir --redact` on the tree is clean.

### A2. Config templates (no values)
- `ttm.conf`: `options ttm pages_limit=31457280`.
- Gufo quadlet on `127.0.0.1:8081` (image digest TBD live; do not invent a digest — leave a `PIN_DIGEST=` hole). llama-swap on `127.0.0.1:8080`, with **no single default**. Entries for **Gemma 4 26B A4B Heretic** (writing: prompts, fiction, uncensored) and **Flash-Next** (coding, general, tools, long context). Callers pick a model **by name**. Keep a `qwen27b` fallback entry as in the plan unless Derrick later drops it. `apiKeys` from env (`LLM_KEY_ALIENPC`, `LLM_KEY_PI`, `LLM_KEY_BOX`, `LLM_KEY_HERMES`, plus per-device keys Derrick names). firewalld: 8080/8081 not opened.
- Model list: both Heretic and Flash-Next (plan Flash-Next sizes 111.3 + 2.79 GB; Heretic size **NO_DATA** until measured; do not invent it). The plan's 17.6 GB 27B fallback is optional until space is confirmed. Write a SHA-256 manifest **once files are on disk**.
- **Pass:** no literal key material; a dry `grep` for `sk-`, `tskey-`, Bearer tokens, and `LLM_KEY_.*=` values is empty; llama-swap lists both models by name and has no implicit single default.

### A3. Download EVO models to the QNAP (both models, after Household confirms space)
- Stage **both** Gemma 4 26B A4B Heretic and Flash-Next (plus the plan's Flash-Next Q8 MTP head). **Do not start** until Household names a share and confirms enough free space for that set (and for the later Windows image: U2 asked for ≥ ~100 GB / ≥ 1.5× C: used). The plan's Flash-Next cold copy alone was already **~130 GB** (U10). Measure Heretic's size first — do not invent it — and add that to the space check. If space is short, **skip A3**, keep the download list in the runbook, and pull on the EVO later.
- **Pass:** each file matches a SHA-256 written beside it, **or** A3 is explicitly deferred with the space number Household gave (do not invent that number).

### A4. What you must not pretend to have tested
- Gufo, Halogen, Strata, kyuz0 `rocm-10.0-strix-llama`, ROCm, Vulkan RADV, gfx1151, tok/s, cold TTFT, DFlash2, IOMMU, 85 W, 140 W, `amd_iommu=off`, PolyStrata/`strata-poly` on gfx1151, `/dev/kfd`. Those are Phase B (U6, U19, U20).
- **Pass:** the staged README says "not yet run on the EVO" and lists the Phase B gates.

Max or Fleet Reviewer checks the staged tree before the box arrives.

---

## Phase B — build on arrival (Fedora on the real EVO)

Install Antigravity on Fedora so the rest can run there. Follow the plan's order. Record pass tests in `40_projects/compute-expansion/records/` with America/Chicago times. Take an EVO lease file first.

### B0 / U1. Unbox and inventory
- BIOS shows 128 GB and the 2 TB drive; version noted. Wired 2.5GbE; Household adds a UniFi DHCP reservation. Boot Windows once. Record BitLocker state; if on, Derrick saves the recovery key to Vaultwarden (not to a file). Record partitions, ESP size/free, C: used.
- **Pass:** inventory in `records/`; key in Vaultwarden or BitLocker confirmed off.

### B1 / U2. Full image + recovery USB, before any change
- Household confirms the QNAP folder has enough free space (plan: ≥ ~100 GB, or ≥ 1.5× C: used). Make **both** the GMKtec/Windows recovery USB **and** a **full-disk** Clonezilla image (all partitions, incl. ESP and Recovery) to that folder, plus `pnputil /export-driver *`. Verify restorable; record the checksum. If BitLocker is still on, turn it off first (**only after** the key is in Vaultwarden) so the image is not a ~full-disk encrypted blob. Keep a **second copy of the image** off the degraded pool.
- **Pass:** image + drivers on the QNAP; checksum and verify = OK; recovery USB boots to its menu; second copy noted or Derrick accepted the risk in writing.

### B2 / U2b. Windows prep, then STOP for the resize card
- BitLocker fully decrypted; Fast Startup off; `powercfg /h off`; shut down once (not restart); RTC in UTC (`RealTimeIsUniversal=1`); Windows Update manual. Shrink C: in **Disk Management** to **~450 GB**; leave the rest **unallocated**. Do not use GParted.
- **Pass:** `manage-bde -status` is Fully Decrypted or None; hibernation unavailable; Fast Startup unticked; C: ≈ 450 GB + ~1.4 TB unallocated; Windows still boots.
- **STOP** for Derrick's resize card (the card shows the U2 verify result, recovery USB tested, BitLocker off, layout table, and "bots have no AI server in Windows").

### B3 / U3. BIOS
- UMA 512 MB, SMT on, **IOMMU/SVM on**, Above-4G on if shown, Restore on AC power loss = Power On, **Balanced 85 W**, fan curve default. Secure Boot left on (enable "3rd-party CA" only if the Fedora USB will not boot; Secure Boot off is last resort). These are the running defaults (starred via t225s813). Do not leave `amd_iommu=off` or 140 W in place after U19 without Derrick's later yes.
- **Pass (after U4b):** `mem_info_vram_total` ≈ 0.5 GiB; `mokutil --sb-state` recorded.

### B4 / U4–U4b. Fedora 44 Server in the free space
- Custom/Blivet, **free space only**: `/boot` 2 GiB ext4; btrfs for `/`, `/home`, `/srv/models`. Existing EFI mounted at `/boot/efi`, **Reformat unticked**. No encryption. Headless (`multi-user.target`). SSH key-only; root locked. Kernel ≥ 6.18.4; linux-firmware ≥ 20260110; MES ≠ 0x83; `dnf versionlock add kernel* linux-firmware`. GRUB default Fedora, timeout 3 s, os-prober on, Fedora first in `efibootmgr`.
- **Pass:** `lsblk -f` shows Windows partitions unchanged; key-only SSH works; 3 cold reboots land in Fedora; one power-cut boots Fedora unattended; `grub2-reboot` into Windows works and the clock is correct both ways (`timedatectl` shows RTC in UTC).

### B5. Pull the staged tree and models; run U5–U8 on the real GPU
- Copy the Phase A tree onto the EVO; copy **both** staged models from the QNAP to `/srv/models` (or download if A3 was deferred); `sha256sum -c`.
- U5: `ttm pages_limit=31457280`; user in `video` and `render`. **Pass:** that sysfs value; `mem_info_gtt_total` ≈ 120 GiB; `/dev/kfd` and `/dev/dri/renderD*` exist.
- U6: Gufo (pinned digest) on 8081; bake-off Gufo vs Halogen vs Strata, plus a recorded fourth arm using the kyuz0 `rocm-10.0-strix-llama` toolbox (not a default; do not run the pwilkin installer), on the plan's 3 Forge-style tasks and a cold Hermes-sized TTFT prompt with no warmup; Vulkan fallback serves once; measure 27B long-context decode with and without DFlash2. **Pass:** log shows gfx1151, not CPU; bake-off table recorded for all four arms, including cold TTFT; Flash-Next at 32K meets the plan bars; the 27B DFlash2 with/without pair is in the table; Heretic tok/s are recorded and not invented.
- U7: llama-swap as staged, **no single default**; callers pick Heretic or Flash-Next **by name**. **Pass:** 8080 and 8081 bound to 127.0.0.1 only; LAN curl to 8080 refused; `/v1/models` with a key lists both models, without a key = 401; a by-name request for each model returns after reboot.
- **STOP** for the ACL card before U8 (Tailscale Serve on 443 to the whole tailnet). Derrick types the join key and API keys.

Then continue the plan: U9 Forge/pi wiring (under the AlienPc lease when that box is touched, never during a render), U9b Hermes as a **client** only, U10 keys (sandbox + `MCP_KEY_*` before U17/U18), U12 (including the cold Hermes-sized TTFT fixture with no warmup), **U19** (day-1 A/B: IOMMU on vs `amd_iommu=off`, and 85 W vs 140 W, on the U12 Flash-Next fixture, including cold TTFT; restore the defaults afterward), U14, U16 (QNAP SearXNG), U17, U18 loopback-only, **STOP** for the tools-port card, U10 rest, U11, then U13 after day-1 is live. **U15** (GLM-5.3-Flash) and **U20** (Gemma 4 26B A4B Heretic on PolyStrata `strata-poly` vs kyuz0 llama.cpp, plus a Prompt maker writing-quality spot check) are day-2 and do not change routing, Q8, Q10, or the writing-model engine without a later card.

### Final check
Max Architect 3 or Fleet Reviewer signs off from the records and a clean `gitleaks` on the config repo. Agy's own report is not enough. Gitea is home again — commit as usual and let the hook push; no keys in those commits.

---

## Open questions (NO_DATA — do not guess)

- QNAP share name, and **current** free space for the U2 image plus **both** model sets (Flash-Next ~130 GB per the plan, plus Heretic — size **NO_DATA** until measured). Household was asked (Q11) to find ~100 GB for the image; whether that folder exists today is unconfirmed here. A3 waits on that confirmation.
- Where the **second** copy of backup images will live while the pool is degraded.
- Vaultwarden reachability today (needed before BitLocker is turned off on the EVO).
- Whether the factory EVO Windows install has BitLocker / device-encryption on (check at U1).
- Live container digests for Gufo / kyuz0 toolboxes (pin at build time, do not invent).
- Exact BIOS menu labels for Balanced 85 W and IOMMU on this US-model board (confirm in U3).
- Whether PolyStrata `strata-poly` / Gemma 4 has been measured on `gfx1151` (plan U20: official HIP/ROCm support is experimental; that Gemma measurement is NO_DATA until run on this box).

CE steps: plan already exists (EVO-X3 rev 8, R13–R15 / U19–U20 from t322u/t323u, R16 from t327u) · this file is an Antigravity brief, rev 5 folds the plan rev 8 measurements into the Phase B order · review of the revised brief is for Max / Fleet Reviewer before Agy runs · compound n/a.
