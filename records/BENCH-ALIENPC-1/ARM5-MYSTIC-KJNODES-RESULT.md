# AlienPc: Miraclein live check, KJNodes re-enable, arm5 Mystic audio LoRA — 2026-11-19

All times are America/Chicago (CT). Doer: Max Architect executor. Derrick's go: t2939u ("Yes to all what about the flux fixes and stuff?").

No Miraclein stills were rendered. The original ComfyUI folder was not touched. No pip installs, no downloads, llama-swap / strata / the 7878 hub / pi / the gate were not killed. LoRA, RefMod and character names are omitted (counts and hashes only). Adult prompt text is not quoted.

## Preflight (VERIFIED)

- 2026-11-19 18:16:52 CT: `C:\AI\locks\gpu-render.lock` absent; lease file existed and was empty (0 bytes, last write 18:04:34 CT after R6). RTX 5070 Ti 0% util, 367 MiB / 16303 MiB. `:10003` down. llama-swap `/running` was `[]`. `:8447` was `tailscaled` (idle). 7878 hub was listening (left alone).
- Lease appended (not replaced): `Max | KJNodes re-enable + Klein9Mod object_info + arm5 Mystic | 2026-11-19 18:20:57 CT`. Removed 18:31:45 CT; file empty again. Lock was absent after the batch.

## 1. Miraclein live check (VERIFIED)

Compared live `C:\AI\community` copies against `mono` `alienpc/` (and the matching `x3/` templates/skill, which are byte-identical in this clone). `flux_still.py` lives only under `x3/community/scripts/parody/` (not in `alienpc/`); it is not on AlienPc. FX1 is the `flux-klein-prompting` skill.

| Live path | Result vs `mono` `alienpc/` |
|---|---|
| `templates/miraclein_refmod.candidate.api.json` | **Already live, not rewritten.** Raw sha differs by key order only (`6752bfeb…` live vs `61c7c1ae…` repo). Canonical JSON sha matches: `05b37fb9fce223a392b9cbec60d89cf2185374fd2a323adc717d62c4668ad58e`. Schema (15:25 CT fix): `mod_1..8` default `"none"` (not `"(none)"`), `copies_1..8` present, `Klein9RefModApply` input `klein9_refmods` (not `refmods`), `custom_retention: 1.0`. mtime still 14:36:43 CT. |
| `templates/miraclein_t2i.candidate.api.json` | Already live, raw sha `f37f97d0…` |
| `templates/miraclein_edit.candidate.api.json` | Already live, raw sha `bfc320a3…` |
| `templates/flux_stills_t2i_klein.candidate.api.json` (ST4) | Already live, raw sha `74d511fe…` |
| `templates/flux_stills_pose_klein.candidate.api.json` (ST5) | Already live, raw sha `14759cc2…` |
| `templates/flux_stills_layout_klein.candidate.api.json` (ST5) | Already live, raw sha `8d34ef01…` |
| `templates/flux_stills_s2_bfs.api.json`, `flux_stills_s2_kv.api.json`, `flux_stills_s2.README.md` | Already live, raw shas `ca6d5a32…` / `c76a69b1…` / `b5ec933e…` |
| `skills/flux-klein-prompting/SKILL.md` (FX1 + Still Photographer) | Already live (applied earlier today 16:41:00 CT). sha `3b7d033b124ab25c26d27a6e4e0f1beaf44789a80217f60490ace72f1e17be6c`. Markers present: Still Photographer & Set Lighting Director persona (1), Hybrid 98% likeness (1), `--hybrid` (2). |

**Applied this run: nothing.** Every listed fix was already on the live AlienPc copies.

`/object_info` after the KJNodes-enabled wake (18:21:57 CT, ComfyUI 0.46.0, 1673 classes, argv `--use-ck-attention --disable-pinned-memory --reserve-vram 1.5`, no `--fast`): all 4 `ComfyUI-Flux2Klein9Mod` classes loaded — `Klein9RefModsLoader`, `Klein9RefModApply`, `Klein9RefModExtract`, `Klein9RefModFolderLoader`. `Klein9RefModApply` required inputs include `klein9_refmods` and `custom_retention` (no `refmods` key). Startup log `C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\user\comfyui_10003.log` (startup 18:21:40–18:21:56 CT): `ComfyUI-Flux2Klein9Mod` import 0.0 s; no `IMPORT FAILED` / `Traceback` / `ImportError`.

## 2. KJNodes re-enable (VERIFIED)

Disabled as a renamed folder: `C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\custom_nodes\ComfyUI-KJNodes.disabled` (last write 2026-06-27 15:56:02 CT; `__init__.py` present).

- Backup first: robocopy to `C:\AI\_archive\20261119\kjnodes-reenable\ComfyUI-KJNodes.disabled` (112 files = 112 files, robocopy rc=1 = success with copies).
- Renamed live folder to `ComfyUI-KJNodes`. No enabled folder was already present. Original ComfyUI tree not touched.
- Woke `comfyui_auto` the normal llama-swap way (`run_graph_job.wake`: GET `/comfyui/`, then `/system_stats`). Ready in ~16 s (already no LLM loaded).
- `/object_info`: **243** KJNodes classes. `LTX2LoraLoaderAdvanced` is `custom_nodes.ComfyUI-KJNodes` — the Mystic arm needs this node, which is why the pack had to be re-enabled first.
- Startup log: `ComfyUI-KJNodes` import 0.1 s; no KJNodes import errors. Server started 18:21:56 CT on `127.0.0.1:10003`.

## 3. Mystic arm5 (VERIFIED)

Prepared arm (notes + run folder `C:\AI\community\runs\h3max_lora_test_20261119\arm5_mystic_audio\`): `request.api.json` sha256 `dc4da102fc6ed18d61913f688d6f8e3af29a94018aa1274bfdbf6b0eb73ffb40` (written 16:53:08 CT). Diff vs arm0 `request.api.json` (`4359fffb2c8ee252458ccf8cac10c73f0858d4896439eadd16d7c6e5f3a6e5bc`): same prompt field sha `6adb8150…` (matches arm0 `prompt.txt`); seed **51083601**; added one `LTX2LoraLoaderAdvanced` node; `m_attn` rewired through that node; sampler `euler` → `lcm`; scheduler `simple` → `beta` (t2868u / HF #98). The referenced LoRA file is on the TestRuntime models tree (size 298,932,824 bytes, sha256 `4168917daeb6e570a004bc6994f73d091b9f3e887f7e946bd00c0f2f7573e5f3`). Four mystic-like files are present; no download.

Queued with `python C:\AI\community\scripts\run_queue.py --run-dir C:\AI\community\runs\h3max_lora_test_20261119 --queue …\_render_order_arm5.json` (one-item order, tag `arm5_mystic_audio`, seed 51083601). Default RTX 2x ULTRA post-pass on.

| Event | Time (CT) | Evidence |
|---|---|---|
| BATCH open, gpu-render.lock acquired pid 2804 | 18:22:49 | `_render_queue.log`, lock file |
| JOB start / QUEUE submitted | 18:22:53 | prompt_id `ee8e03b8-fda5-4f92-9327-a9d6a00a647e` |
| JOB end ok | 18:27:51 | **295.0 s** wall |
| OBJECTIVE ok | 18:27:51 | **243 frames, 768x1344, audio yes, 6,966,896 raw bytes** (graph is authority; CLI default 124 was noted and ignored) |
| UNLOAD comfyui_auto | 18:27:53 | llama-swap API, not a process kill |
| UPSCALE ok | 18:28:03 | 768x1344 → **1536x2688**, 24 fps, 243 frames, audio yes, 32,889,124 bytes, 9.8 s; raw kept locally only |
| BATCH closed | 18:28:03 | **rc=0**, done=1/1, lock released |

ffprobe (both clips): h264 yuv420p, 24 fps, 243 frames, 10.125 s, AAC 32 kHz stereo. Upscaled sha256 `6A6108D0EED03B5DA5D2CC37165042C49728201C27B97058924C0ACC5931A100`. Raw sha256 `B0344914519AE1B1F327D076A0548F951BA624C43B4A5BF5490EE04AC3928DF3`. After the batch: GPU 0%, 368 MiB; lock absent.

NAS: copied the arm folder to `\\NAS4CBE37.local\renders\runs\h3max_lora_test_20261119\arm5_mystic_audio\` excluding `*_raw*`. NAS upscaled mp4 size 32,889,124, sha256 **matches** `6A6108D0…`. No `_raw` file on the NAS arm folder. Also copied `_render_order_arm5.json`, `_run_queue_arm5.out.log`, and the updated run-level `_render_queue.log` / `status.log`.

## Snapshots (VERIFIED AlienPc; X3 incomplete here)

Before this records commit, `mono` had already been fast-forwarded to `0361e0d4` (18:26:51 CT, "records: PixlStash sync timer re-armed (Derrick t2939u) + live snapshots"). That commit already recorded KJNodes enabled and restored llama-swap argv (no `--fast fp16_accumulation`).

Re-read live after the 18:28 CT unload and compared to those copies:

- `comfy.settings.json` sha `defe342f…` — match
- `extra_model_paths.yaml` sha `5a9039c7…` — match
- redacted `llama-swap.yaml` sha `ed16b392…` — match; live `comfyui_auto` cmd is `--use-ck-attention --disable-pinned-memory --reserve-vram 1.5` (no `--fast`); live file sha equals the R6 restore
- `pip-freeze.txt` matches after stripping a UTF-8 BOM from a local re-freeze (normalized sha `c9084a74…`)
- `community-HEAD.txt` still `8eec1d3d` (rev-parse only; no `git remote -v` in `C:\AI\community`)
- `custom-nodes.tsv` lists `ComfyUI-KJNodes` enabled at `bc8e4ce4254bcd0050383386ee2f9d753dbf1fa5`, which matches the live folder name and `git rev-parse HEAD`. A freshly generated tsv differs only in sort order, not in names or the KJNodes row.

`scripts/snapshot-live-setup.sh` + `scripts/sync-config-copies.sh` were **not re-run on the X3 in this pass**. The EVO-X3 Cursor machine was disconnected. `0361e0d4` updated only `hosts/x3/live/hermes/memories-listing.txt`; `hosts/x3/live/README.md` is still the 17:56 CT copy. A full X3 snapshot refresh remains outstanding if Max wants one from a connected X3 session.

## Not done

- No Miraclein still renders (each still still needs Derrick's yes).
- No production template promotion.
- This clone does not include `records/BENCH-ALIENPC-1/R6-RESULT.md` or untracked `x3/comfy-alienpc/` files in the commit (pre-existing, other work).
