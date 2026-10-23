# ALI-173 community pipeline bakeoff - 2026-10-23 (Forge)

Bakeoff arms: infinite-creation, ComfyUI-H3-Continuum, tritant MiniMax-H3 Extender (our current R4-R9 chain),
h3-storyboard-ALLInOne, comfy-cli / comfy-mcp, the Civitai H3 NSFW prompt writer, the Qwen2.5-Omni Ref2VA
prompt writer. The ranked table + winner is B8; this file grows one section per B-line. KEEP / adopt is Derrick's.

## Installs (B1, 2026-10-23 ~15:15 CT)

| folder | git HEAD | upstream commit date | state |
| --- | --- | --- | --- |
| `C:\AI\community\tools\infinite-creation` | `0defb3888e7ce07cc0c167c0502d62c52d612f42` | 2026-10-23 16:53 +0800 | cloned `--depth 1` (4827 files), `pnpm install` **exit 0**, `pnpm run install:skills` **exit 0** (9 skills, 35 files) |
| `C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\custom_nodes\ComfyUI-H3-Continuum` | `308653cff108061a94381cef446fef985384b214` | 2026-10-24 03:16 +0900 | cloned `--depth 1`, `version.py PACKAGE_VERSION = 3.10.2`, **no pip deps** (requirements.txt = "No extra pip dependencies. Uses PyTorch and safetensors bundled with ComfyUI"), loads in ComfyUI |

Sources: https://github.com/SwotAtmk/infinite-creation (README_EN.md), https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum (README.md).
Tooling installed: `npm install -g pnpm@11.7.0 bun` (pnpm = the repo's own `packageManager`, README asks >= 9; bun 1.4.4 is a
README prerequisite that builds the Agent kernel). Full per-item detail (sizes, URLs, rc codes) is in `notes/installs_downloads.md`.
Skipped on purpose: its default model downloads (Qwen-Image 2.1, Krea2, Qwen3-TTS, MiniMax Music3) and the
`comfyui_original_workflows/` first-run pass. No ComfyUI core update. Disk after: 52 GB free on C: (95 % used).

## Registered workflows (B1)

Both of our graphs were copied into its `workflows/` dir **and** registered through its own API path
(`lib/core/db.js` -> `Workflows.upsert`, the same call `POST /api/workflows` uses). Script:
`notes/ali173_b1_register_workflows.mjs`; it prints the DB ids.

| name | kind | sourceFile | nodes |
| --- | --- | --- | --- |
| `H3 int8 Ref2VA (AlienPc R1)` | `r2v` | `workflows/ali173_h3_int8_ref2v.json` (13,806 B, copy of `runs/ali147_pool_hc_r1_s51130001/request.api.json`) | 27 |
| `FLUX.2 Klein 9B sheet (AlienPc)` | `i2i` | `workflows/ali173_flux2_klein9b_sheet.json` (28,547 B, copy of `runs/ali147_pool_hc_sheet_s51120000/request.api.json`) | 116 |

Its shipped workflow templates are the **same API-graph format** as our `request.api.json` (dict keyed by node id),
so our graphs drop in without conversion. Spec roles for the H3 graph: prompt `c0.prompt`, width/height `c0.*`,
length `c0.length`, seed `noise.noise_seed`, `save.filename_prefix`, media = `c0.ref_images` + LoadImage pool
`img/sheet/sheet2`, outputs `SaveVideo`. Sheet graph: branch `hc1w1*` is the role-addressable one (prompt
`hc1w1pos.text`, seed `hc1w1noise.noise_seed`, `hc1w1save.filename_prefix`, LoadImage pool of the 10 per-woman
inputs, outputs `SaveImage`); its other 9 branches keep baked prompts/seeds.

## Config diff (B1) - `config.json` written, never called

`config.example.json` -> `config.json` (repo root, gitignored), diff =
- `comfyui.baseUrl` `http://127.0.0.1:8188` -> **`http://127.0.0.1:10004`** (the llama-swap-managed ComfyUI port).
- `llm.baseUrl` vendor-hosted default -> **`http://127.0.0.1:8080/v1`**, `llm.model` `deepseek-v4-flash-vision-exp`
  -> **`coding_swift15_iq3s`**, `llm.apiKey` `sk-xxx` -> `""`, `llm.vision` `true` -> **`false`** (the no-vision-judge
  rule: our local model is text-only and no vision judge is allowed on explicit output).
- added `generation.*` explicitly (`videoTimeoutMinutes 90`, `imageTimeoutMinutes 30`, `freeAfterEvery 0`,
  `videoConcurrency 1`, `imageConcurrency 2`) and `_alienpc_note` (provenance).
- `hardware.mode nvidia`, `workflows` left on its built-in ids - see the gap below.
- Config file itself: `C:\AI\community\tools\infinite-creation\config.json` (1,563 B, `python -m json.tool` OK).

## Gotchas found in B1 (all reproducible)

1. **`bun.exe` must be on PATH as a real exe.** `scripts/ensure-agent.mjs` does `spawnSync('bun', ['--version'],
   {stdio:'ignore'})` with no `shell:true` on win32, so npm's `bun.cmd` shim is invisible and `pnpm install`
   postinstall fails with "bun not found". Workaround used: `PATH+=C:/Users/derek/AppData/Roaming/npm/node_modules/bun/bin`.
2. **Upstream build guard fails the Agent-kernel build (rc 1) while still emitting the artifacts**: `vendor/openclaude`
   `bun run build` reports a new missing-module stub `src/commands/plan/index.ts` (that source file is absent from the
   published tree). `dist/sdk.mjs` 9.6 MB + `dist/cli.mjs` 21 MB are produced, so `ensure-agent`'s existence check passes
   and the second `pnpm install` is clean - but a strict install is red on a clean machine.
3. **`data/` is not in the repo**, so `node:sqlite` cannot open `data/ic.db` (`ERR_SQLITE_ERROR errcode 14`) until the
   dir exists; the registration script creates it (`ensureDirs()` only makes `data/projects`).
4. **Registered workflows are NOT reachable by the pipeline runner.** `lib/core/workflow-specs.js:getSpecForKind()`
   resolves `cfg.workflows[kind]` (or the hardware preset) through `getDefaultSpecById()`, i.e. **only the
   hand-written `DEFAULT_SPECS`**; DB rows show in the Workflows page/API and drive the self-iteration skill factory,
   but the run path would still use `MiniMax_H3_Easy_r2v.json`. To run OUR H3 graph in B4 the spec has to be added to
   `DEFAULT_SPECS` (a fork patch) or `config.workflows.r2v` pointed at a built-in id. This is the main adoption gap.
5. **GPU/VRAM exclusivity is the real constraint for B4**: llama-swap runs ComfyUI and the coding model in one exclusive
   group, so every model turn swaps ComfyUI out (`comfy_ctl.py status` showed `running=['coding_swift15_iq3s']` and
   `comfy_ok=False` minutes after a start). Any arm that needs ComfyUI up while the agent thinks needs the
   `comfy_ctl.py start` + queue + fetch in ONE call, and a re-wake after every gap.
6. Continuum's public node surface is filtered (`nodes.py:463-480`): `H3ContinuumJoin` and the V1 names are **not**
   exported, so `/object_info/H3ContinuumJoin` = `{}`. Verified live classes on `:10004` (HTTP 200):
   `H3ContinuumSamplerV39` (required inputs incl. `sequence_prompt`, `prompt_mode`, `chunks`, `chunk_seconds`,
   `aspect`, `preset`, `custom_mp`), plus `H3ContinuumReferenceImagesV39`, `H3ContinuumAssembleSeamV35`,
   `H3EasyLoadImage`, `H3DecodeCacheHelper` (12 exported classes total). Example graphs in its `examples/`:
   `MiniMax_H3_Continuum_V39.json`, `MiniMax_H3_Continuum_V38X2.json`, `MiniMax_H3_Continuum_V39_Turbo_Sample.json`
   - these are the B2 starting point, not the V1 zip files in the repo root.
7. Its README says the ComfyUI-registry submission is held (3.10.0 manual review) and to use the GitHub release ZIP;
   the `--depth 1` clone matches `version.py 3.10.2`, the same version as the release.
8. B5 disk reality: 52 GB free on C: - a "tens of GB" 27B GGUF + mmproj does not fit alongside 8-step H3 int8, the
   FLUX.2 sheet models and node_modules. Needs a Derrick decision (free space) before B5.

## ComfyUI restart evidence (B1)

`python C:\AI\community\scripts\comfy_ctl.py status` first showed `guard=(0, ['IDLE'])` (GPU LOCK clear, no render),
so the restart was legal: `restart` -> `stop: ComfyUI not loaded` -> `start: GET /comfyui/` -> `COMFY_OK
http://127.0.0.1:10004 running=['comfyui_auto']` at 15:08:30 CT; `status` then `comfy_ok=True queue=(0, 0)
guard=(0, ['IDLE'])`. ComfyUI log `ComfyUI/user/comfyui_10004.log`: `H3 Continuum 3.10.2 loaded (V2 integrated sampler
+ hidden legacy workflow compatibility)` and `0.9 seconds: ...\custom_nodes\ComfyUI-H3-Continuum` with **no
IMPORT FAILED** for it. (Pre-existing unrelated IMPORT FAILEDs in that log: comfyui-various, was-node-suite, RES4LYF,
ComfyUI-LTXVideo, CRT-Nodes (`No module named 'soundfile'`), ComfyUI-WanVideoWrapper - untouched, none of them is ours.)

## B2 Continuum scene - not started (this pass ended at B1)

Plan for B2: build from `examples/MiniMax_H3_Continuum_V39.json` + our `unet/clip/vae` int8 slots + the HC1 sheet refs
(27 nodes of the R1 graph are the reference), request through `p7\JOB_REQUEST.json` as `ali173_cont_hc1_s51140001`,
check as FINAL + face similarity. Budget gate before requesting: read
`C:\Users\derek\5slock\ralph-community\logs\p7_budget.json` (at B1: used_min 450.8, jobs 35, caps 615/45; the 120 min /
10 jobs above 495/35 belong to this bakeoff).
