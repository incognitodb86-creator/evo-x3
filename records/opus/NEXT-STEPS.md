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

After merging on GitHub (with Derrick's yes), mirror to Gitea and pull `mono` on X3 (`~/evo-x3`) and the AlienPc sparse `mono` clone. `#5` and `#6` both touch `x3/community/scripts/parody/flux_still.py` in different regions; `git merge-tree` shows all six PRs merge cleanly into `mono` 8e753955, including `#5` + `#6` together (VERIFIED 2026-11-20 ~2:10 PM CT). Run the full parody pytest on X3 afterward. `#6` carries the original C1-C8 commits, so the 7 synthetic test PNGs stay in history (added in 4b2d142, removed in the next commit); a squash merge keeps them out of `mono` history if Derrick prefers.

## 2. X3 live: deploy `h3-render/SKILL.md` to all Hermes profiles (Brief items 1, 1b, 3)

- **Lease:** `max | deploy h3-render skill | <CT time>` in `/home/derekboone/AI/locks/x3-lease.txt`.
- **Action:** Back up existing copies into `/home/evo/.hermes/_archive/20261120-h3-render/`, then copy canonical `hosts/x3/hermes/skills/h3-render/SKILL.md` to:
  1. `/home/evo/.hermes/skills/creative/h3-render/SKILL.md` (default)
  2. `/home/evo/.hermes/profiles/code/skills/creative/h3-render/SKILL.md` (if present)
  3. `/home/evo/.hermes/profiles/writertest/skills/creative/h3-render/SKILL.md` (if present; the 8e753955 snapshot dropped `profiles/writertest/skills-list.txt`, so this profile may be gone)
- **Live tests:**
  1. From X3 as `evo`, confirm `curl -sS https://alienpc.tailf242b2.ts.net:8444/infinite_image_browsing/global_setting | jq '.is_readonly, (.extra_paths | length)'` returns values. A `401 secret_verification_failed` means IIB has a secret key and expects an `IIB_S` cookie: tell Derrick, never commit the key, and keep the skill's stop rule.
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
- **Step 4a (read-only header check, 2 s):** Confirm AlienPc's local `fk9_sydneysweeney_v1_refmod.safetensors` and `fk9_meganfox_v1_refmod.safetensors` under `ComfyUI\models\refmods-klein9\` match HuggingFace `malcolmrey/klein9` (Sydney `5,505,592` bytes, Megan `5,505,584` bytes; both `shape: [21, 128, 32, 32]`, `token_budget: 256`, `token_count: 5376`, `vae: flux2_vae.safetensors`). The `fk9_*_v1` and `_prodigy` LoRA sizes in `model-inventory.txt` already match HuggingFace exactly (VERIFIED):
  ```powershell
  python -c "import json,struct,pathlib; root=pathlib.Path(r'C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\models\refmods-klein9'); [print(fn, (root/fn).stat().st_size, json.loads((root/fn).read_bytes()[8:8+struct.unpack('<Q',(root/fn).read_bytes()[:8])[0]])['__metadata__']['klein9_refmod_meta']) for fn in ('fk9_sydneysweeney_v1_refmod.safetensors','fk9_meganfox_v1_refmod.safetensors')]"
  ```
- **Step 4b (create local non-git prompts JSON):** On AlienPc (NEVER commit to git), create `C:\AI\refs_ab_celeb\prompts_l7.json` with per-celeb `trigger`, `name`, `likeness_desc` (and optional `scene`).
- **Step 4c (optional rebuilt RefMod arm):** If testing fewer images (e.g. 4–8 curated portraits at `token_budget=256` -> `1,024–2,048` total tokens), extract `fk9_<name>_v1_refmod_rebuilt.safetensors` into `ComfyUI\models\refmods-klein9\` via `ComfyUI-Flux2Klein9Mod\extract_klein9_mod.py`. (If omitted, `L7-rebuilt` skips cleanly.)
- **Step 4d (run 6-seed A/B against `C:\AI\refs_ab_celeb`, NEVER `C:\AI\refs_ab`):**
  ```powershell
  python alienpc\community\scripts\run_flux_likeness_ab.py --dry-run --ab-suite l7 --num-seeds 6 --with-v1-lora --celebs "Sydney Sweeney,Megan Fox" --ref-dir C:\AI\refs_ab_celeb --prompts-json C:\AI\refs_ab_celeb\prompts_l7.json
  python alienpc\community\scripts\run_flux_likeness_ab.py --run --ab-suite l7 --num-seeds 6 --with-v1-lora --celebs "Sydney Sweeney,Megan Fox" --ref-dir C:\AI\refs_ab_celeb --prompts-json C:\AI\refs_ab_celeb\prompts_l7.json
  ```
  Verify `RESULT.md` reports real numeric intra-gallery ceiling + per-ref `mean/max/min` + multi-seed summary (no `n/a`). `--with-v1-lora` adds `L7-v1lora` (the 165 MB `fk9_*_v1.safetensors` @ 0.60, the LoRA malcolmrey's official hybrid workflow uses) beside the `_prodigy` arms. Neither LoRA has text-encoder tensors (VERIFIED), so model-only loading is correct.
- **Step 4e (deploy to X3 live, only after the A/B):** `#3` changes the live `refmod` template's negative path to `ConditioningZeroOut`, which changes every Hermes Flux RefMod still. Deploy it only if `L7-fixed` beats `L7-base` in `RESULT.md` and Derrick says yes. Then, under X3 lease, back up and copy updated `flux_still.py` (`--unet`, `--request-json`, from `#5`) and `miraclein_refmod.candidate.api.json` into `/home/evo/AI/community/`, and verify `flux_still.py --request-json <winning L7 request.api.json> --prompt "..."` dry-runs `READY`. `flux_still.py` alone (`#5`) is safe to deploy any time: it only adds flags.
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
- **3-slot Flash-Next test at 131K on X3:** Queued live test (take X3 lease, keep 2-slot `llama-swap.yaml` backup for rollback). Live `flash-next-uncensored-v2` runs Gufo `--sessions 2` but llama-swap `concurrencyLimit: 4`; set both to 3 for the test so requests queue in llama-swap, not inside Gufo. KV for 3 x 131K is about 10.3 GiB if `--context` is per session (Gufo docs: ~27.5 KiB/token with MTP; ASSUMPTION that it is per session, so check the startup log's reported budget).
- **REA R1–R4 Render test:** Run in Hermes Render chat after C8/C9 deploy and Derrick's go (`records/REA-PARODY-PIPELINE/RENDER-TEST.md`).

## 7. Community tips checked against upstream (Q-cards for Derrick; nothing applied)

Checked 2026-11-20 ~2:10 PM CT against upstream source. Each is a yes/no for Derrick; each live step needs its lease and a backup.

- **Q-OPT1 Gufo prompt cache (biggest speed win):** live `flash-next-uncensored-v2` sets `--cache-ram-bytes 2147483648` (2 GiB). Gufo's default is half of free RAM up to 32 GiB, and its docs show a 203K-token Flash-Next turn dropping from 184.4 s to 0.7 s when the prefix is cached (`gufo-org/gufo` `docs/cache.md`, v0.35.0). Proposal: `--cache-ram-bytes 17179869184` (16 GiB) plus the disk tier `--cache-disk /srv/cache/gufo-flash-next-v2 --cache-disk-bytes 34359738368` (survives restarts; one server per directory). Check `free -g` with PixlStash (16G cap) loaded first. Rollback: restore the llama-swap backup.
- **Q-OPT2 Hermes loop hard stop:** `tool_loop_guardrails.hard_stop_enabled: false` is Hermes' own default for interactive chats ("hard stops are opt-in", `hermes_cli/config_defaults.py`); only gateway/cron hard-stop by default. Turning it on for the default (Render) profile would have cut the 9-minute `C:\` loop at 5 identical failures. Optional; the skill stop rule already covers it.
- **Q-OPT3 ComfyUI-PixlStash for PX5:** upstream is now v1.9.2 (`d9b9b0ea`, released 2026-11-20), newer than AlienPc's disabled `e5ce77da`. Useful nodes: **Face Likeness Gate** (splits a batch into accepted/rejected by face match; read-scope token is enough), **Multi Adapter (LoRA) Loader** with a `trigger_words` output (triggers come from the PixlStash model shelf at run time, never git), PR #80 MiniMax-H3 image support. URL and token live in ComfyUI Settings, never in workflow JSON.
- **Q-OPT4 ComfyUI-MiniMaxH3Mod features already installed (`54f93eb6`) for M2 OC RefMods:** `image_refs=separate` (keeps stills as image refs, fixes the last-image flash), **Collect H3 RefMod Masks** (per-reference masks to stop background/outfit bleed), single-file visual+audio bundles with per-slot Visual/Audio strengths. The upstream README says speaker-voice transfer still fails, which matches the U56 #2 rule.
- **Q-OPT5 Klein9 RefMod `copies_1`:** `Klein9RefModsLoader` can repeat a RefMod's tokens (`copies_1 = 2`) instead of pushing strength above 1.0, which multiplies the latents (`nodes.py`). ASSUMPTION worth one extra M6 arm after the 6-seed run; official workflows use `copies 1`, strength 1.0, `res_multistep`/`simple`, 8 steps, CFG 1.0 on stock `flux-2-klein-9b-fp8`.
- **Q-OPT6 Gufo speech models:** Gufo v0.35.0 ships Qwen3-ASR 1.7B (speech to text) and Qwen3-TTS 1.7B in the same runtime. Hermes STT uses local Whisper `base` today. A future plan item, not a quick swap.
- **IIB prompt recovery (now in `#2`):** `GET /infinite_image_browsing/image_geninfo?path=<fullpath>` returns the saved prompt/seed of an output, and `POST /infinite_image_browsing/db/search_by_substr` searches indexed outputs.

**Checked and not needed (do not change):**
- `auxiliary.*.reasoning_effort: 'false'` (a string) is fine: Hermes treats `"none"`, `"off"`, `"disabled"`, `"false"` and `"0"` as off (`agent/auxiliary_reasoning_floor.py`), and the U59 probes passed.
- Symlinks into `image_cache` deliver fine: live `gateway.strict: false` delivers any path outside the credential denylist, and the Hermes cache is always trusted (`gateway/media_policy.py`, `config_defaults.py`). `media_delivery_allow_dirs` only matters if `strict` is turned on.
- Keep `compression.proactive_prune_tokens: 0`: each prune rewrites sent history and breaks the prompt-cache prefix (`config_defaults.py`), which would undo Q-OPT1.
