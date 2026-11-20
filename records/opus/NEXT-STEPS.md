# Next steps for Max (live X3 & AlienPc actions, Nov 20, 2026)

Companion to `records/opus/OPUS-BRIEF-20261120.md`. Covers everything that could not be executed or verified from files on the Windows clone. Every live host action requires Derrick's yes and the target host's lease (`x3-lease.txt` on X3; AlienPc lease per brain `10_packs/max/max-briefing.md`).

## 1. Review and merge PRs into `mono`

All file-only fixes are open as separate PRs into `mono` (no direct pushes to `mono` were made):

| PR | Branch | Brief item(s) | Scope |
|---|---|---|---|
| `#2` | `fix/brief-1-1b-3-hermes-render-gallery` | 1, 1b, 3 | `hosts/x3/hermes/skills/h3-render/SKILL.md` (inline image/video `MEDIA:`, ComfyUI `:8446`, AlienPc IIB `:8444`, X3 `:8443/renders/`, stop-if-missing line) |
| `#3` | `fix/brief-4-flux-likeness-templates` | 4 | `miraclein_refmod.candidate.api.json` (`ConditioningZeroOut`), placeholder `miraclein_l7_prompt.template.txt`, `flux-klein-prompting/SKILL.md`, `records/FLUX-LIKENESS-20261120/REFMOD-AUDIT-20261120.md` |
| `#4` | `fix/brief-5-flux-ab-runner-scoring` | 5 (+ 4 A/B) | `alienpc/community/scripts/run_flux_likeness_ab.py` + tests (magic-byte ref filter, last-JSON-line parsing, intra-gallery ceiling, per-ref mean/max/min, 6-seed L7 suite) |
| `#5` | `fix/brief-6-flux-still-flags` | 6 | `x3/community/scripts/parody/flux_still.py` + tests (`--unet`, `--request-json`) |
| `#6` | `fix/brief-7-rea-parody-review` | 7 | `pi/rea-parody` review & fixes (drop 7 PNGs, `conftest.py` `tmp_path` isolation, `.gitignore`, BPM lag range, WAV width check, shot discovery, `rea_pose` `pose_image`) |

After merging on GitHub (with Derrick's yes), mirror to Gitea and pull `mono` on X3 (`~/evo-x3`) and the AlienPc sparse `mono` clone. Note: `#5` and `#6` both touch `x3/community/scripts/parody/flux_still.py` in different regions; verify clean merge and run full parody pytest on X3 afterward.

## 2. X3 live: deploy `h3-render/SKILL.md` to all Hermes profiles (Brief items 1, 1b, 3)

- **Lease:** `max | deploy h3-render skill | <CT time>` in `/home/derekboone/AI/locks/x3-lease.txt`.
- **Action:** Back up existing copies into `/home/evo/.hermes/_archive/20261120-h3-render/`, then copy canonical `hosts/x3/hermes/skills/h3-render/SKILL.md` to:
  1. `/home/evo/.hermes/skills/creative/h3-render/SKILL.md` (default)
  2. `/home/evo/.hermes/profiles/code/skills/creative/h3-render/SKILL.md` (if present)
  3. `/home/evo/.hermes/profiles/writertest/skills/creative/h3-render/SKILL.md` (if present)
- **Live tests:**
  1. From X3 as `evo`, confirm `curl -sS https://alienpc.tailf242b2.ts.net:8444/infinite_image_browsing/global_setting | head -c 200` returns JSON (if IIB requires an `IIB_SECRET_KEY`, note it without committing it).
  2. Confirm `curl -sS "https://alienpc.tailf242b2.ts.net:8446/history?max_items=5" | jq 'keys | length'` works from X3.
  3. In Hermes Render chat, ask to show today's outputs: verify it fetches an image (`.png`) AND a video (`.mp4`/`.webm`) into `/home/evo/.hermes/image_cache/` and renders both inline via `MEDIA:`.
- **Rollback:** Restore the backed-up `SKILL.md` files from `/home/evo/.hermes/_archive/20261120-h3-render/`.
- **Optional X3 gallery parity (item 1b, needs Derrick's yes):** X3 `:8444` is confirmed to be `pi-mobile-hub` (`127.0.0.1:7878`), not a gallery. If Derrick wants a matching browseable gallery API over `/mnt/qnap/renders/runs` on X3 (separate tailnet Serve port), write a small plan first.

## 3. AlienPc live: OpenSSH Tailscale-only install (Brief item 2, needs Derrick at console for UAC)

- **Could not verify from files:** `C:\Users\derek\AppData\Local\Temp\openssh-setup-20261120\enable-openssh-tailscale.ps1` is not in the repo.
- **Lease:** AlienPc lease.
- **Pre-UAC review checklist for Max on AlienPc:**
  1. Confirm `sshd_config` enforces `PasswordAuthentication no`, `PubkeyAuthentication yes`.
  2. Confirm Windows Firewall inbound rule on TCP 22 is scoped strictly to `100.64.0.0/10` (Tailscale CGNAT).
  3. If `derek` is in Windows `Administrators`, confirm `evo`'s `alienpc_ed25519.pub` goes into `C:\ProgramData\ssh\administrators_authorized_keys` with ACLs restricted to `SYSTEM` and `Administrators` (`icacls /inheritance:r`).
- **Action:** Run the staged script with Derrick at the console to click UAC.
- **Test (from X3):** `sudo -n -u evo ssh -o BatchMode=yes alienpc "hostname"` returns AlienPc's hostname.
- **Post-install follow-up:** Update the stop-if-missing line in `hosts/x3/hermes/skills/h3-render/SKILL.md` (and live profiles) to try `ssh alienpc` once for `C:\...` paths before stopping.
- **Rollback:** `Stop-Service sshd; Set-Service sshd -StartupType Disabled` and remove the Tailscale-SSH firewall rule.

## 4. AlienPc live: confirm local RefMod headers & run 6-seed M6 L7 A/B (Brief items 4, 5, 6)

- **Lease:** AlienPc lease (no render in flight).
- **Step 4a (read-only header check, 2 s):** Confirm AlienPc's local `fk9_sydneysweeney_v1_refmod.safetensors` and `fk9_meganfox_v1_refmod.safetensors` under `ComfyUI\models\refmods-klein9\` match HuggingFace `malcolmrey/klein9` (`5,505,600` bytes, `shape: [21, 128, 32, 32]`, `token_budget: 256`, `token_count: 5376`, `vae: flux2_vae.safetensors`):
  ```powershell
  python -c "import json,struct,pathlib; root=pathlib.Path(r'C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\models\refmods-klein9'); [print(fn, (root/fn).stat().st_size, json.loads((root/fn).read_bytes()[8:8+struct.unpack('<Q',(root/fn).read_bytes()[:8])[0]])['__metadata__']['klein9_refmod_meta']) for fn in ('fk9_sydneysweeney_v1_refmod.safetensors','fk9_meganfox_v1_refmod.safetensors')]"
  ```
- **Step 4b (create local non-git prompts JSON):** On AlienPc (NEVER commit to git), create `C:\AI\refs_ab_celeb\prompts_l7.json` with per-celeb `trigger`, `name`, `likeness_desc` (and optional `scene`).
- **Step 4c (optional rebuilt RefMod arm):** If testing fewer images (e.g. 4–8 curated portraits at `token_budget=256` -> `1,024–2,048` total tokens), extract `fk9_<name>_v1_refmod_rebuilt.safetensors` into `ComfyUI\models\refmods-klein9\` via `ComfyUI-Flux2Klein9Mod\extract_klein9_mod.py`. (If omitted, `L7-rebuilt` skips cleanly.)
- **Step 4d (run 6-seed A/B against `C:\AI\refs_ab_celeb`, NEVER `C:\AI\refs_ab`):**
  ```powershell
  python alienpc\community\scripts\run_flux_likeness_ab.py --dry-run --ab-suite l7 --num-seeds 6 --celebs "Sydney Sweeney,Megan Fox" --ref-dir C:\AI\refs_ab_celeb --prompts-json C:\AI\refs_ab_celeb\prompts_l7.json
  python alienpc\community\scripts\run_flux_likeness_ab.py --run --ab-suite l7 --num-seeds 6 --celebs "Sydney Sweeney,Megan Fox" --ref-dir C:\AI\refs_ab_celeb --prompts-json C:\AI\refs_ab_celeb\prompts_l7.json
  ```
  Verify `RESULT.md` reports real numeric intra-gallery ceiling + per-ref `mean/max/min` + multi-seed summary (no `n/a`). Optionally test `fk9_*_v1.safetensors` (165 MB, official workflow LoRA) vs `_prodigy`.
- **Step 4e (deploy `flux_still.py` + `miraclein_refmod.candidate.api.json` to X3 live):** Under X3 lease, back up and copy updated `flux_still.py` (`--unet`, `--request-json`) and `miraclein_refmod.candidate.api.json` (`ConditioningZeroOut`) into `/home/evo/AI/community/`, and verify `flux_still.py --request-json <winning L7 request.api.json> --prompt "..."` dry-runs `READY`.
- **Rollback:** Restore backups in `/home/evo/AI/community/_archive/`. Do not enable `ComfyUI-PuLID-Flux2.disabled` unless fixed L7 falls short and Derrick approves.

## 5. X3 live: full parody pytest & REA C8/C9 deploy (Brief item 7)

- **Lease:** X3 lease.
- **Test:** After merging `#5` and `#6`, run the full suite on X3 where H3 RefMods exist:
  ```bash
  cd ~/evo-x3/x3/community/scripts/parody && /home/evo/AI/render/x3/.venv/bin/python3 -m pytest -q
  ```
  Expect 700+ passed, 0 failed, and `git status` clean with zero files written to `x3/comfy-alienpc/`.
- **Deploy (on Derrick's go):** Run gitleaks, copy REA C1–C7 files into `/home/evo/AI/community/` with backups (C8), and install `rea-remake/SKILL.md` into the Hermes render profile (C9).
- **Rollback:** Restore `/home/evo/AI/community/` from C8 backup and archive `~/.hermes/skills/creative/rea-remake/`.

## 6. Held / Queued (wait for Derrick's explicit yes)

- **Brief item 8 (shared folder for all new images/stills):** Held until Derrick decides whether non-final images should copy to one shared folder. Do not change `sync-renders` or ComfyUI output paths yet.
- **3-slot Flash-Next test at 131K on X3:** Queued live test (take X3 lease, keep 2-slot `llama-swap.yaml` backup for rollback).
- **REA R1–R4 Render test:** Run in Hermes Render chat after C8/C9 deploy and Derrick's go (`records/REA-PARODY-PIPELINE/RENDER-TEST.md`).
