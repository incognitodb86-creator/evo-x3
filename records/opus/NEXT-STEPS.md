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

**First:** Max's 2:08 PM CT brief and live snapshot are on branch `origin/mono-brief` (`52567d19`, one commit on top of `mono` `8e75395`). Fast-forward `mono` to it. All six PRs also merge cleanly on top of `mono-brief` (checked with `git merge-tree` and each PR's real merge base, 2026-11-20 ~2:25 PM CT).

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
  python alienpc\community\scripts\run_flux_likeness_ab.py --dry-run --ab-suite l7 --num-seeds 6 --with-v1-lora --with-nvfp4 --celebs "Sydney Sweeney,Megan Fox" --ref-dir C:\AI\refs_ab_celeb --prompts-json C:\AI\refs_ab_celeb\prompts_l7.json
  python alienpc\community\scripts\run_flux_likeness_ab.py --run --ab-suite l7 --num-seeds 6 --with-v1-lora --with-nvfp4 --celebs "Sydney Sweeney,Megan Fox" --ref-dir C:\AI\refs_ab_celeb --prompts-json C:\AI\refs_ab_celeb\prompts_l7.json
  ```
  Verify `RESULT.md` reports real numeric intra-gallery ceiling + per-ref `mean/max/min` + multi-seed summary (no `n/a`). `--with-v1-lora` adds `L7-v1lora` (the 165 MB `fk9_*_v1.safetensors` @ 0.60, the LoRA malcolmrey's official hybrid workflow uses) and `--with-nvfp4` adds `L7-nvfp4` (`Miraclein_4.5_9b_NVFP4.safetensors` on the exact same fixed graph, head-to-head speed & likeness vs FP8). Neither LoRA has text-encoder tensors (VERIFIED), so model-only loading is correct.
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
- **3-slot Flash-Next test at 131K on X3:** See Section 11 below for the verified concurrency audit, exact test steps, and rollback to 2 slots.
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

---

## 8. Flux likeness after 1:59 PM CT L7fix: Kontext-style edit vs T2I+RefMod (`mono-brief` `52567d19` items a–c)

Max's 2:08 PM CT brief (`origin/mono-brief` `52567d19`, Derrick `t3108u`–`t3120u`) reports that the 1:59 PM CT L7fix stills (~139 s each, `ConditioningZeroOut` + strength `1.0` + trigger/name/likeness prompt) **still looked off**. Do not promote L7fix as the final likeness fix. Going forward, Hermes Render writes still prompts (never Max or harness scripts).

### Recommendation: test Kontext-style `ReferenceLatent` edit + non-Miraclein Klein9 isolation

1. **Why L7fix T2I+RefMod can still miss likeness:**
   - Miraclein 4.5 is a heavy NSFW fine-tune, whereas Malcolmrey's 98% RefMod+LoRA score was measured on distilled `flux-2-klein-9b-fp8` (8 steps, CFG 1.0). Miraclein's weights may shift away from stock Klein9 RefMod/LoRA manifolds.
   - Each official RefMod bundles 21 varied images (5,376 compressed 512x512 tokens), averaging angles/lighting/eras together.
2. **Why a Kontext-style `ReferenceLatent` edit may beat T2I+RefMod for likeness (ASSUMPTION; Arm C tests it):**
   - FLUX.2 Klein 9B is natively a Kontext-style reference-conditioning edit model (`miraclein_edit.candidate.api.json`: `LoadImage -> ResizeImageMaskNode (1.0 MP) -> VAEEncode -> ReferenceLatent` on pos + neg, denoising from pure `EmptyFlux2LatentImage` noise).
   - Unlike pixel img2img (partial denoise, which locks pose/framing), `ReferenceLatent` edit lets you change scene, pose, lighting, and wardrobe while giving the DiT one crisp 1 MP reference face directly (~4,000 tokens from one 1 MP image instead of 21 images pooled to 512×512). You can optionally add `fk9_*_v1` LoRA (`0.5–0.6`) for angle changes.
3. **Controlled 5-arm likeness test on AlienPc (6 seeds, ArcFace vs `C:\AI\refs_ab_celeb`):**
   - **Arm A (L7fix FP8 baseline):** Miraclein FP8 (`9.08 GB`) + 21-img RefMod (`1.0`) + LoRA (`0.6`) + `ConditioningZeroOut`, Hermes-written prompt.
   - **Arm A2 (Miraclein NVFP4 head-to-head):** Exact same fixed graph as Arm A on `Miraclein_4.5_9b_NVFP4.safetensors` (`5.18 GB`, `--with-nvfp4` in `#4`). Tests whether NVFP4 matches FP8 likeness at ~3× the speed (A5 measured 43–55 s on NVFP4 vs 139–180 s on FP8).
   - **Arm B (model-drift isolation):** Exact same graph as Arm A on `FLUX-KLEIN-9B-FP8-NSFW.safetensors` if the runner preflight finds it on disk (stock `flux-2-klein-9b-fp8` was not downloaded, D6). Shows whether Miraclein's fine-tune is what breaks likeness.
   - **Arm C (Kontext-style `ReferenceLatent` edit, single picked still):** `miraclein_edit.candidate.api.json` as is (`flux_still.py --mode edit --image <photo>`, which already defaults to `Miraclein_4.5_9b_NVFP4.safetensors` — compare against Arm A2 so UNET is not confounded), taking one clean front/3-quarter ref photo from `C:\AI\refs_ab_celeb`, with and without `fk9_*_v1` LoRA @ `0.55`.
   - **Arm D (curated small RefMod):** 4–8 curated portraits from `C:\AI\refs_ab_celeb` extracted at `--token-budget 256` (`1,024–2,048` total tokens) via `extract_klein9_mod.py`.
   - **NVFP4 default rule (Derrick 2026-11-20 ~2:36 PM CT):** All static `miraclein_*.candidate.api.json` templates already default to `Miraclein_4.5_9b_NVFP4.safetensors`. **Stay on NVFP4 as the default** unless FP8 (`Arm A`) clearly beats NVFP4 (`Arm A2`) by >0.02 ArcFace mean AND wins Derrick's eye check. Arms run at the same CFG; at CFG 1.0 the negative branch (and `ConditioningZeroOut`) is never evaluated (section 12).

## 9. Phone-friendly Hermes subscription login flows (`mono-brief` `52567d19` item e)

Never store tokens, keys, or cookies in git. Verified against upstream `NousResearch/hermes-agent` (`website/docs/guides/xai-grok-oauth.md`, `hermes_cli/auth.py`):

### A. xAI Grok OAuth (`xai-oauth` — SuperGrok / SuperGrok Heavy / X Premium+)
- **Why the box browser failed:** xAI's login page rejects headless/Linux browsers on the X3 ("We could not verify this browser").
- **Phone-friendly device-code flow (no X3 browser, no SSH tunnel needed):**
  1. Over SSH (or Termius/Blink on phone) to X3, run as `evo`:
     ```bash
     sudo -n -u evo -H env HERMES_HOME=/home/evo/.hermes \
       /home/evo/.hermes/hermes-agent/.hermes/bin/hermes auth add xai-oauth --no-browser
     ```
     (Full path: `hermes` is not on `sudo`'s PATH. Keep this terminal open; it polls until you approve.)
  2. Hermes prints an `https://accounts.x.ai/...` verification URL and short user code and polls in the background.
  3. Open that URL in your **phone's real Safari/Chrome browser** (normal session, not an in-app webview), sign into your SuperGrok Heavy account, enter the code if asked, and approve.
  4. Hermes saves tokens to `/home/evo/.hermes/auth.json` (mode `0600`, gitignored) and auto-refreshes. Verify with `hermes doctor` (same full path).
- **Known upstream caveat (issue `#26847`):** xAI has rejected some SuperGrok OAuth inference calls with `HTTP 403` even after login succeeds. If inference returns 403, fall back to API key (`XAI_API_KEY` in `/home/evo/.config/evo-x3/llm.env`, `provider: xai`).

### B. Google Gemini login (confirmed API-key only in Hermes)
- **VERIFIED (`hermes_cli/auth.py` `_REGISTRY_ROWS`):** Hermes Agent has **no** Google One / Gemini Advanced subscription OAuth flow. The `gemini` provider (`Google AI Studio`, `https://generativelanguage.googleapis.com/v1beta`) uses `GEMINI_API_KEY` or `GOOGLE_API_KEY` only.
- **Phone-friendly setup:**
  1. Open `https://aistudio.google.com/apikey` in your phone browser and create an API key.
  2. Add `GEMINI_API_KEY=<key>` to `/home/evo/.config/evo-x3/llm.env` (owner-only `0600`, never committed; Hermes already loads this file via `secrets.command`).
  3. Select `gemini` in `hermes model` (or `hermes config set model.provider gemini`).

## 10. X3 Master Catalog & H3 Beta 7 RefMod + INDEX linking plan (`mono-brief` `52567d19` item 9, Derrick `t3109u`/`t3111u`)

### Audit of current `detect_still_identity()` + `resolve.py` (VERIFIED)
- **What works today:** `detect_still_identity()` reads `flux_meta.json`, ComfyUI PNG `prompt` chunks (`Klein9RefModsLoader`/`LoraLoader`), or PixlStash character tags, and passes extracted names into `resolve_identities()`.
- **3 gaps against Derrick's `t3109u`/`t3111u` rules:**
  1. `resolve.py` ranks overall status (`good > onthefence > bad`) but does **not** select strictly **ONE** character index per celeb (432 actors have multiple INDEX rows; 76 span good+bad).
  2. Flux-to-H3 carry-through attaches the H3 RefMod and matches INDEX rows, but does not enforce **celeb INDEX + ONE best character INDEX + H3 RefMod + `{TRIGGER}` together**.
  3. Metadata is fragmented across `INDEX.md`, `INDEX_BAD.md`, drifted `aliases.json` (345 keys on X3 vs 15 on AlienPc), `_DEFAULT_ICONIC_VOICE_ROLE` (126 entries), 1,495 0-byte X3 stubs, and AlienPc's 12 unusable 132-byte Git LFS pointer stubs in `models\refmods\`.

### Proposed X3 Master Catalog design (`x3/community/index/master_catalog.json`)
- **Host split (`t3111u`):** All weight files (H3 RefMods, Klein9 RefMods, Klein9 LoRAs) stay on **AlienPc only**. X3 holds one compact JSON catalog (`master_catalog.json`) that Hermes Render and `resolve.py` read locally.
- **Inputs to a small offline/sync generator (`scripts/build_master_catalog.py`, gated on Q-CAT1):**
  1. AlienPc model inventory manifest (real `>= 1 KB` H3 RefMods — flagging the 12 LFS stubs as `valid_on_alienpc: false`; real Klein9 RefMods; Klein9 LoRAs with `has_trigger: true|false` booleans only — **zero literal triggers in git**).
  2. `INDEX.md` + `INDEX_BAD.md` grouped by normalized actor. Deterministic **ONE-character picker** per celeb:
     - Tier 1: status `good` > `onthefence` > `bad`.
     - Tier 2: curated `_DEFAULT_ICONIC_VOICE_ROLE` match if in the same best status tier.
     - Tier 3: most clips in INDEX, as a stand-in for popularity (no popularity data exists; ASSUMPTION) (tie-breaker: fictional character row over `"Real Person / Celebrity"`, else solo-actor mode for singers/models/influencers).
  3. Synced 345-key `aliases.json` + PixlStash `GET /api/v1/characters` (`character_id` and `person <Name>` tag; no library browsing).
- **Per-entry schema (keyed by compact slug, e.g. `sydneysweeney`, `fcsydny`):**
  ```json
  {
    "canonical_name": "{NAME}",
    "kind": "celeb|oc",
    "aliases": [],
    "h3_refmod": {"stem": "minimaxh3_<slug>_v1_refmod", "valid_on_alienpc": true},
    "h3_audio_refmod": null,
    "flux_refmod": "fk9_<slug>_v1_refmod",
    "flux_loras": [{"file": "klein9/fk9_<slug>_v1.safetensors", "has_trigger": true}],
    "celeb_index_status": "good|onthefence|bad|none",
    "primary_character": {"name": "{CHAR}", "franchise": "{SHOW}", "status": "good", "clips": 1},
    "pixlstash": {"character_id": null, "person_tag": "person {NAME}"},
    "trigger_key": "<slug>"
  }
  ```
  *(Literal trigger words live only in a local non-git `/home/evo/.config/evo-x3/triggers.json` or PixlStash model shelf, never in git. Celeb `h3_audio_refmod` is always `null` per U56 #2.)*
- **Resolver & skill changes (after Q-CAT1 yes):** Update `resolve.py` so `resolve_identities()` and `detect_still_identity()` consult `master_catalog.json` first (auto-selecting H3 visual RefMod + celeb INDEX + ONE `primary_character` + `{TRIGGER}`, refusing LFS stubs), sync `aliases.json` to AlienPc, and add a 3-line `jq` lookup example to `h3-render` and `flux-klein-prompting` skills.
- **Q-CAT1 (for Derrick):** Approve building `master_catalog.json` + generator + `resolve.py` single-character rule? Default **yes** (plan/PR first, live sync under lease). Also approve pulling or quarantining the 12 LFS-stub H3 RefMods on AlienPc?

## 11. X3 3-agent / 3-slot 131K concurrency check & test plan (`mono-brief` `52567d19` item 10, Derrick `t3108u`)

### Config & memory audit (VERIFIED against live `8e753955` snapshot)
- **Can 3 Hermes agents/sessions run concurrently today? Almost — blocked only by Gufo `--sessions 2`.**
  - **Hermes (`config.yaml` + `profiles/code/config.yaml`):** `max_concurrent_sessions: null`, `gateway.multiplex_profiles: true`, `gateway.api_server.max_concurrent_runs: 10` -> **ready for 3+ sessions.**
  - **llama-swap (`llama-swap.yaml`):** `globalConcurrencyLimit: 6`, `flash-next-uncensored-v2` `concurrencyLimit: 4` -> **mismatched** against Gufo's `--sessions 2` (the extra requests wait in Gufo's own queue, `--max-pending 16`). Match both to `3`.
  - **Memory budget on 128 GiB Strix Halo:** Flash-Next Q4_K_XL + MTP + mmproj (size not recorded in the repo; ASSUMPTION ~50 GiB, read it from the startup log) + KV for 3 × 131,072 tokens at ~27.5 KiB/tok (`gufo/docs/models/qwen3.8-flash-next.md`) ≈ **10.3 GiB** (+3.44 GiB over 2 slots; ASSUMPTION that `--context` is per session) + PixlStash (~9.4 GiB live RSS, 14G/16G cap) + OS/Hermes/embed-small/cache (~10–12 GiB) ≈ **~80–88 GiB total, an estimate** (~40 GiB headroom; still check `free -g` and Gufo's startup memory log before raising RAM prefix cache).

### 3-slot 131K live test steps (X3 lease required, on Derrick's go)
1. **Lease & backup:** Take X3 lease (`max | 3-slot 131K test | <CT>`). Confirm idle (`pi-job.active` empty, no `gpu-render.lock`). Back up `/etc/evo-x3/llama-swap.yaml` to `/etc/evo-x3/_archive/llama-swap.yaml-20261120-pre3slot`.
2. **Edit `flash-next-uncensored-v2`:** Change `--sessions 2` -> `--sessions 3` and `concurrencyLimit: 4` -> `concurrencyLimit: 3`. Keep `--context 131072`.
3. **Restart & check startup memory:** `sudo -n systemctl restart llama-swap`, wait for authed `/running` `state=ready` (as `apply-hermes-workspaces.sh` does since `8888ba63`), record `free -g` and Gufo's startup log line showing reserved KV + RAM cache budget (`journalctl -u llama-swap -n 80`).
4. **3-way concurrent test:** Fire 3 parallel authenticated requests simultaneously (one each to `flash-next-render`, `flash-next-code`, and `flash-next-aux` with `max_tokens: 256`) and verify all 3 return `HTTP 200` cleanly with no stall timeout and total RAM stays under ~105 GiB (`memory.events` on `pixlstash.service` stays flat).
5. **Rollback to 2 slots (if OOM, stall, or slowdown):**
   ```bash
   sudo -n cp -a /etc/evo-x3/_archive/llama-swap.yaml-20261120-pre3slot /etc/evo-x3/llama-swap.yaml
   sudo -n systemctl restart llama-swap
   ```
   Verify `/running` `state=ready` and clear lease.

## 12. Flux speed without quality loss & bakeoff design (`mono-brief` `52567d19` item 11, Derrick `t3115u`)

### Measured timing breakdown (placeholder — to be filled by timing job)
<!-- TIMING_BREAKDOWN_PLACEHOLDER: replace with measured per-phase seconds (TE load/encode, UNET load, 12-step sample, VAE decode, offload/swap) from AlienPc -->
- **Measured timing breakdown:** _PENDING — another job will fill in per-phase seconds (TE load/encode, UNET load, sampling steps, VAE decode, VRAM offload) here._

### Why L7 stills take ~139–180 s (checked against repo records)
1. **Miraclein FP8 vs NVFP4 is the likely main cost.** A5 (2026-11-19, [A5-RESULT.md](../BENCH-ALIENPC-1/A5-RESULT.md)) ran the same 12 steps / CFG 1.1 / `euler` RefMod and Hybrid graphs on `Miraclein_4.5_9b_NVFP4` (5.18 GB) with sample times of **55 s** and **43 s**. L7 on `Miraclein_4.5_9b_FP8` (9.08 GB) takes ~139–180 s. FP8 UNET (9.08 GB) plus the Qwen3-8B FP8 text encoder (8.66 GB) cannot both sit in 16 GB, so ComfyUI swaps weights; NVFP4 is native on the RTX 5070 Ti (Blackwell). ASSUMPTION until the timing breakdown above confirms where the seconds go.
2. **CFG 1.1 costs a second model pass every step.** VERIFIED in ComfyUI `comfy/samplers.py` (`sampling_function`): at CFG exactly 1.0 the negative is not evaluated. L7 runs 12 steps × 2 passes = 24 passes; the official malcolmrey workflows run 8 steps × 1 pass (CFG 1.0, `res_multistep` / `simple`). Side effect: at CFG 1.0 the `ConditioningZeroOut` negative from `#3` is never run, so that fix only matters at CFG above 1.0.
3. **Reference tokens.** 21 images × 256 = 5,376 reference tokens on top of ~4,032 image tokens at 768×1344. Attention cost grows with sequence length, so a 4–8 image RefMod (1,024–2,048 tokens) should be faster. ASSUMPTION; measure it.
4. **Cold starts.** `comfyui_auto` sits in AlienPc llama-swap's one exclusive `main` group with the Swift, judge and JoyCaption LLMs. Any of those requests between stills stops ComfyUI, and the next still pays a cold load. Time the first (cold) still separately from warm ones.

### Already tested on this box and not adopted (do not add to the bakeoff)
From [the follow-up plan](../source-plans/2026-11-18-x3-alienpc-followup-plan.md) section 4 and [R6-RESULT.md](../BENCH-ALIENPC-1/R6-RESULT.md) (measured on H3; same `comfyui_auto` process):
- **SageAttention:** off since Oct 14; Comfy Kitchen (`--use-ck-attention`, the live flag) won by 23%. `run_nvidia_gpu.bat`'s `--use-sage-attention --fast` is an old manual launcher, not production.
- **`--fast fp16_accumulation`:** R6 tied on time (286.3 s vs 286.5 s) and changed the output (SSIM 0.78).
- **`torch.compile`:** conflicts with Dynamic VRAM. **TeaCache / EasyCache / Spectrum:** change the sampling trajectory.
- **Dropping `--disable-pinned-memory`:** the flag exists because of Windows WinError 1450 (Linux plan LX7).
- **`--highvram` / `--gpu-only`:** 16 GB cannot hold the FP8 UNET plus the 8.66 GB text encoder.

### Flux speed + likeness bakeoff (AlienPc lease, one change per arm)
Same 6 seeds, the same Hermes-written prompt, ArcFace against `C:\AI\refs_ab_celeb` (runner `#4`). Record the cold first still on its own, then the median of warm stills 2–6, plus peak VRAM (`nvidia-smi`).

| Arm | Change vs S0 | Why |
|---|---|---|
| **S0** | Current L7fix graph (Miraclein FP8, 12 steps, CFG 1.1, 21-image RefMod @ 1.0, LoRA @ 0.6) | Baseline |
| **S1** | Miraclein **NVFP4** instead of FP8 | A5 measured 43–55 s on NVFP4; check likeness holds |
| **S2** | **CFG 1.0** | Halves model passes (VERIFIED); malcolmrey's setting |
| **S3** | **8 steps, `res_multistep` / `simple`** | Official malcolmrey workflow settings |
| **S4** | Curated 4–8 image RefMod (Arm D in section 8) | Fewer reference tokens; may also help likeness |
| **S5** | Kontext-style single-image edit (Arm C in section 8) | Different identity path; compare time and likeness |

Keep a change only if ArcFace mean stays within 0.01 of S0 (or better) and Derrick's eye check agrees, then stack the winners and run one final 6-seed check. No speed target is promised before the timing breakdown is in. Rollback: the arms only change per-run graphs; no launch flag or llama-swap edit is part of this bakeoff.

## 13. One ComfyUI or two (Flux + H3Max)? (Derrick 2026-11-20 ~2:22 PM CT)

**Answer: keep one running ComfyUI for both Flux stills and H3Max clips.** Two at once would hurt, not help, on this box.

Facts (VERIFIED, `hosts/alienpc/live/llama-swap/llama-swap.yaml`, AlienPc notes): one RTX 5070 Ti 16 GB, 64 GB system RAM, Windows. Two ComfyUI installs already exist: `comfyui_auto` (`HardcoreNSFW-TestRuntime`, used for both Flux and H3) and `comfyui_longvideo` (`C:\AI\comfy-longvideo`, sharing the same input folder). Both are members of the single exclusive `main` swap group, so llama-swap only ever runs one; starting one stops the other after its queue drains (`comfy_graceful_stop.ps1`).

Why two running at the same time is worse:
- **VRAM:** each process gets its own CUDA context and its own copy of the weights. ComfyUI's dynamic VRAM only sees its own process, so the two fight over 16 GB: out-of-memory errors or slow system-memory fallback. Flux FP8 alone (9.08 GB UNET + 8.66 GB text encoder) already overflows 16 GB.
- **System RAM:** each process keeps its own RAM cache of offloaded weights (ComfyUI's default `--cache-ram` keeps inactive models up to the system RAM size). Flux and H3 weights cached twice on 64 GB means paging to disk.
- **No speed gain:** there is one GPU and `gpu-render.lock` already runs one job at a time.

What one process costs: switching Flux → H3 unloads the Flux weights from VRAM and loads H3. With RAM to spare, ComfyUI reloads from its RAM cache instead of disk. Measure that switch in the timing breakdown above. The bigger risk is the shared llama-swap group: an LLM request on AlienPc between a still and its clip stops ComfyUI completely. Max's `8c079afb` pi-job routing already hands coding back to the X3 when ComfyUI holds the GPU; keep it that way.

A second ComfyUI only makes sense with a second GPU, or as a separate install for dependency isolation that runs one at a time (that is what `comfyui_longvideo` already is).

## 14. Hermes learning loop (brief addendum item 12, Derrick 2026-11-20)

Goal: the X3 Hermes chats (default/Render, `code`, `writertest`, `grok`) learn from their mistakes the way Forge does, so fixes like the M6/L7 prompt issues (missing LoRA `{TRIGGER}`, celeb `{NAME}`, likeness line, identical prompts) stick without Max fixing them by hand.

### How Hermes v0.23.3 learns (VERIFIED, upstream docs at tag `v0.23.3`: `user-guide/features/memory.md`, `skills.md`, `curator.md`, `profiles.md`, `sessions.md`)
- **Memory:** `MEMORY.md` (2,200 chars) and `USER.md` (1,375 chars), written with the `memory` tool. They load into the system prompt as a frozen snapshot at session start, so a new lesson is only seen by the *next* session.
- **Background review:** after a turn, every `memory.nudge_interval` / `skills.creation_nudge_interval` turns, Hermes forks a review that can save memory or create/patch a skill. That review is the learning loop.
- **Skills:** new agent-made skills go to the profile's own `skills/` folder. Existing skills are patched where they are found, **including skills under `external_dirs`** ("external dirs are not a write-protection boundary").
- **`skills.write_approval: true`** stages every `skill_manage` write in `pending/skills/<id>.json` until someone runs `/skills pending` → `/skills diff <id>` → `/skills approve <id>`. **`memory.write_approval`** (default `false`) does the same for memory.
- **Curator** (on by default): every 7 days it marks unused agent-made skills stale (14 days) and archives them (30 days); it never deletes. **Pin** blocks deletion only. **Lock** (`hermes curator lock <skill>`) blocks every agent write to that skill, including `skill_manage`, `write_file`/`patch` and `terminal` writes into the skill's folder, in normal turns, the background review and the curator. Your own edits still work.
- **Per profile:** memory, skills, sessions (`state.db`, `session_search`), pins and locks are all per profile. `--clone` copies skills and memory once, then the profiles are separate.
- **Long chats don't learn:** a WebUI chat that runs for days is one session, so new memory never loads and `session_search` rarely fires. The docs say to start a new chat (`/new`) at natural task boundaries.

### What is on now (VERIFIED from the live snapshot on `mono-brief` `52567d19`, except `grok`)
| Profile | Memory | `memory.write_approval` | `skills.write_approval` | `external_dirs` | Nudges (memory/skills) |
|---|---|---|---|---|---|
| default (Render) | on | unset → `false` | `true` | `/home/evo/AI/community/skills` | 10 / 15 |
| `code` | on | unset → `false` | `true` | none | 10 / 15 |
| `writertest` | **off** | — | `true` | `/home/evo/AI/community/skills` | 10 / 15 |
| `grok` | cloned from default (ASSUMPTION: same settings; its config is not in the snapshot yet) | | | | |

What this means:
1. **Skill lessons don't stick today.** Every skill create/patch from the review is staged and waits for an approval that nobody does. ASSUMPTION until Max counts the staged files (live check below).
2. **Memory lessons do land at once.** They are unreviewed, and limited to 2,200 characters.
3. **Render can rewrite shared community skills.** An approved patch to `h3-writer`, `h3-prompting`, `flux-klein-prompting` or `h3-parody-identity` edits `/home/evo/AI/community/skills` in place, outside git review. The terminal can also edit them directly, because the write gate only covers `skill_manage`.
4. **The nightly `hermes-state-commit.timer` (03:15) only commits the default profile.** It runs `git add SOUL.md skills/ memories/` in `~/.hermes`, so `profiles/*/skills` and `profiles/*/memories` are not in that history.
5. **The background review runs on the same Gufo slot as the chat.** Its "wait for idle GPU" default only applies to Hermes' managed local server, not our `custom` provider. So a review can take one of the 2 Gufo sessions right after a turn (see section 11).
6. **The M6/L7 prompt mistakes came from Max's A/B harness script, not Hermes** (brief item a). So the fix belongs in the skill text, which PR `#3` already does (`{TRIGGER}` + `{NAME}` + a short likeness cue when a LoRA is loaded). Hermes has nothing to "learn" for that one.

### Proposed loop (plan only; each live step needs Derrick's yes, the X3 lease and a backup)
**One source of truth.** Shared skills live in git: `hosts/x3/hermes/skills/*` and `x3/community/skills/*`. Hermes proposes changes, people review them, and changes ship through a PR plus the existing installers. This avoids duplicates, keeps history, and keeps a skill from drifting differently in each profile.

1. **Lock what Render must not change on its own (Q-LRN1).** In every profile, run `hermes curator lock` on:
   - the shared skills: `h3-render`, `h3-writer`, `h3-prompting`, `h3-parody-identity`, `flux-klein-prompting`, `pixlstash-image-library`, `rea-remake`, `pi-job`;
   - any skill that holds the 18+ or queue rules.

   When Hermes wants to change a locked skill, it must describe the change in chat. Hermes' own agent-made skills (new topics) stay unlocked, so it can still learn new things.
2. **Block edits to the locked parody graph and safety files (Q-LRN2).** A lock only covers skill folders. Extend the existing `guard-render-queue.sh` `pre_tool_call` terminal hook (fail-closed) to refuse writes to:
   - `/home/evo/AI/community/templates/*.api.json` and `scripts/parody/*`;
   - `/home/evo/AI/render/**`;
   - `/home/evo/.hermes/agent-hooks/*`;
   - the profiles' `config.yaml` files.

   This is a policy check, not a sandbox (it does not see `execute_code`). It matches the h3-render rule "never edit render, community, or forge code or config yourself".
3. **Review queue → brain (Hermes → `20_learnings`, Q-LRN3).**
   - Extend the nightly state commit to also add `profiles/*/skills` and `profiles/*/memories`, plus a list of staged `pending/skills/*.json`, for each profile.
   - Max's daily job reads that diff and the pending list. He writes one `20_learnings` note per real lesson with `ce-compound`. Each note gets a stable key (`hermes/<profile>/<skill-or-topic>`) so a second sighting updates the same note instead of adding a new one, plus the source commit SHA.
   - Before anything is written: drop anything matching the gitleaks rules, replace literal LoRA/RefMod triggers and adult prompt text with `{TRIGGER}` / `{NAME}` placeholders, and never copy `auth.json`, `.env` or `llm.env`.
   - Derrick gets a short digest (lessons found, staged skill writes waiting) and approves or rejects staged writes in chat with `/skills approve|reject <id>`.
4. **Brain → Hermes (no duplicates).** A brain lesson that applies to Hermes becomes a PR to the canonical SKILL.md in git, not a new Hermes skill. After merge, the existing installers copy it to every profile (`apply-hermes-workspaces.sh` pattern). If Hermes made its own skill on the same topic, fold it into the canonical one and archive the local copy (`hermes curator` archive; never delete). Keep `fleet-brain` out of Hermes `external_dirs`: it holds Max-only skills, and Hermes would patch it in place.
5. **Learn at task boundaries.** Add one line to the Render and Code workspace `AGENTS.md`: start a new chat after each finished task (render delivered, unit DONE). The docs say this is when memory and `session_search` pay off.
6. **Keep the review off the busy slot (Q-LRN4).** Route `auxiliary.background_review` to `flash-next-aux` (thinking off) with `max_input_tokens: 48000`, or set `auxiliary.background_review.enabled: false` on `writertest` (memory is already off there). Re-check after the 3-slot test in section 11.
7. **Memory approval (Q-LRN5, default no).** Keep `memory.write_approval: false` for Render, because a memory note cannot change a locked skill or the guard hook. Turn it on for `grok` if Derrick wants cloud-model notes reviewed.

Upstream also offers external memory providers (Honcho, Mem0, etc.) to share memory across profiles. Not proposed: it adds a service, and with `grok` on xAI it would send local chat context to a cloud model. I found no community practice beyond the upstream docs worth adopting here.

### Live read-only checks for Max (no lease needed)
```bash
for h in /home/evo/.hermes /home/evo/.hermes/profiles/*; do
  echo "== $h"; sudo -n -u evo ls "$h/pending/skills" 2>/dev/null | wc -l
done
sudo -n -u evo -H env -C /home/evo HERMES_HOME=/home/evo/.hermes /home/evo/.hermes/hermes-agent/.hermes/bin/hermes curator status
sudo -n -u evo git -C /home/evo/.hermes log --stat -5 --format='%h %ad %s' --date=short
```
Record the counts in the next RESULT. Do not print the staged files' contents (they can hold prompt text).

## 15. Hermes `grok` profile (brief addendum item 13; created 2026-11-20, record only)

- **What:** new Hermes profile `grok` (wrapper `/home/evo/.local/bin/grok`), cloned from default with shared logins.
  - `model.provider: xai-oauth`, `model.default: grok-4.6`, `base_url: https://api.x.ai/v1`.
  - `image_gen` and `video_gen` toolsets are on, backed by xAI (`grok-imagine-image` / `grok-imagine-video`).
  - Backup: `profiles/grok/config.yaml.bak-20261120-1415CT`.
- **Default/Render is unchanged and fully local** (config sha256 `526812b3…`, per Max).
- **Auth:** two `xai-oauth` credentials are linked (pool entries #1 and #2; ids are in `hermes auth list xai-oauth`, not copied here). Both return `403 personal-team-blocked:spending-limit`, most likely because the account is out of credits right now. Retest after the reset:
  ```bash
  sudo -n -u evo -H env -C /home/evo /home/evo/.local/bin/grok chat --oneshot -Q -q 'Say OK.'
  ```
  If it still returns 403 with credits available, see the upstream tier caveat in section 9A (issue `#26847`).
- **Things to decide (Q-GROK1):**
  - As a clone of default, `grok` inherits the render skills, `external_dirs` and the queue guard hook. Prompts sent from `grok` go to xAI's cloud, not the local model. Proposal: in `grok`, disable `h3-render`, `h3-writer`, `pixlstash-image-library` and `rea-remake`, the same way `code` does, so render work stays on the local default profile.
  - Lock the shared skills (section 14, item 1).
  - xAI image/video generation spends credits.
- **Docs:** added to `hosts/x3/live/hermes/README.md` (profile list). The next live snapshot should copy `profiles/grok/{config.yaml,profile.yaml,SOUL.md}` with secrets redacted, the same as `code`. Never copy `auth.json`.

## 16. Push and snapshot rules for this batch (Max)
1. Merge the PRs on GitHub only after Derrick's yes; never push straight to `mono` from the Windows clone.
2. On the box: run gitleaks first (pre-push), push GitHub first, then mirror to Gitea.
3. Take a fresh live snapshot of **both** the X3 (`scripts/snapshot-live-setup.sh` + `sync-config-copies.sh`, now including `profiles/grok`) and AlienPc (`model-inventory.txt`, `custom-nodes.tsv`, the redacted llama-swap copy), as one commit, and say which PRs it follows.
