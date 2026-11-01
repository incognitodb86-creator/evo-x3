- 2026-10-23 R4H: no binaries/weights installed (research only). ~20 read-only web GETs saved as text under C:\AI\community\notes\web (HF /api/models searches, /api/models/<id>?blobs=true metadata, .../raw/main/README.md model cards, one GitHub raw README 198 KB) - sizes listed in notes\small_prompt_llm_research_20261023.md "## Method". Total ~0.5 MB, no disk impact.

## 2026-10-23 ~15:15 CT ALI-173 B1 INSTALL (bakeoff, Forge)
- git clone --depth 1 https://github.com/SwotAtmk/infinite-creation -> C:/AI/community/tools/infinite-creation (4827 files; HEAD 0defb3888e7ce07cc0c167c0502d62c52d612f42, committed 2026-10-23 16:53 +0800).
- git clone --depth 1 https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum -> C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/custom_nodes/ComfyUI-H3-Continuum (version.py PACKAGE_VERSION 3.10.2; HEAD 308653cff108061a94381cef446fef985384b214, 2026-10-24 03:16 +0900).
- npm install -g pnpm@11.7.0 bun (npm global dir C:/Users/derek/AppData/Roaming/npm; 3 packages, 8 s). pnpm 11.7.0 = the repo packageManager (README wants >= 9), bun 1.4.4 = the README prerequisite that builds the Agent kernel.
- pnpm install (repo root) rc 0: 385 packages from the npm registry (next 15.5.26, react 18.3.1, next-themes, tailwindcss 3.4.19, framer-motion 14, @heroui/react, ws, adm-zip). The FIRST run's postinstall failed because scripts/ensure-agent.mjs calls spawnSync('bun') without shell, so npm's bun shim (bun.cmd) is invisible; fix = put C:/Users/derek/AppData/Roaming/npm/node_modules/bun/bin (bun.exe) on PATH.
- vendor/openclaude: bun install --ignore-scripts rc 0 (482 packages, 53 s, incl. the @vscode/ripgrep 1.18.0 binary); bun run build rc 1 (upstream build guard: src/commands/plan/index.ts is missing in the published tree, so it is stubbed) yet it produced dist/cli.mjs 21.0 MB + dist/sdk.mjs 9.6 MB (+ 72 MB of .map). Second pnpm install rc 0 (ensure-agent skips, dist exists).
- pnpm run install:skills rc 0: pulled the 9 official MiniMax-H3 skills from the GitHub repo (branch main) into skills/ = 35 files (~1 MB). No model weights.
- Registered our graphs as its workflows: workflows/ali173_h3_int8_ref2v.json 13,806 B (27 nodes, copy of runs/ali147_pool_hc_r1_s51130001/request.api.json) + workflows/ali173_flux2_klein9b_sheet.json 28,547 B (116 nodes, copy of runs/ali147_pool_hc_sheet_s51120000/request.api.json), plus 2 rows in data/ic.db through lib/core/db.js Workflows.upsert (script notes/ali173_b1_register_workflows.mjs; it also had to create the missing data/ dir - node:sqlite cannot open a db in a folder that does not exist).
- NO model downloads (skipped Qwen-Image 2.1 / Krea2 / Qwen3-TTS / MiniMax Music3 and the comfyui_original_workflows first-run per the task) and NO pip install for Continuum (its requirements.txt = "No extra pip dependencies. Uses PyTorch and safetensors bundled with ComfyUI"). No ComfyUI core update.
- Disk: 55 GB free before, 52 GB free after (C: 95% used). The ~3 GB = node_modules + bun's openclaude dist/maps. B5 (27B vision GGUF + mmproj, tens of GB) does not fit without a cleanup - flagged for Max/Derrick.

## 2026-10-23 ~15:40 CT PW1 (ALI-163/HB3, H3 Omni prompt rewriter, Forge iter 10)
- No pip installs, no new packages: the node pack was already on disk and all five of its requirements were already in ComfyUI's own venv.
- git pull --ff-only origin main in C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/custom_nodes/MiniMax-H3-Prompt-Rewriter-ComfyUI: v0.27.1 (14c0712, cloned 2026-10-16) -> **v0.30.0 (c22cb38 "[0.30.0] experience Lightx2v")**, 4 commits, 56 files +4212/-529. Source only, no weights in the repo, no ComfyUI core change. The 2026-10-16 local edit to the packaged minimax_h3_rewriter/models.json (+39 lines) is preserved.
- HF metadata GETs (no weight bytes): /api/models/<repo>?blobs=true for ggml-org/Qwen2.5-Omni-7B-GGUF, unsloth/Qwen2.5-Omni-7B-GGUF, pytraveler/MiniMax-H3-Prompt-Rewriter-LoRA-Omni-GGUF, lightx2v/MiniMax-H3-Prompt-Rewriter-LoRA-Omni -> notes/web/<repo>.json (3.7 + 9.7 + 2.1 + 3.7 KB).
- Weights (~7.9 GB total, chosen per the node README Omni table row "Q4_K_M base + projector + Q8_0 adapter = 4.4 + 1.4 + 0.34 GB, ~9 GB VRAM"; the 16 GB card cannot hold the Q8_0 base 8.1 GB + F16 adapter = ~13 GB, and the safetensors route 22.4 GB base does not fit in 49 GB free with room to spare):
  - https://huggingface.co/ggml-org/Qwen2.5-Omni-7B-GGUF/resolve/main/Qwen2.5-Omni-7B-Q4_K_M.gguf 4,683,072,384 B -> ComfyUI/models/LLM/Qwen2.5-Omni-7B-GGUF/Qwen2.5-Omni-7B-Q4_K_M.gguf (DONE rc=0 15:36:36 CT, 1.8 min)
  - https://huggingface.co/ggml-org/Qwen2.5-Omni-7B-GGUF/resolve/main/mmproj-Qwen2.5-Omni-7B-Q8_0.gguf 1,548.5 MB -> same folder (pair layout copied from the existing models/LLM/Qwen2.5-Omni-3B-GGUF, so the pack's _pair_mmproj pairs them by stem)
  - https://huggingface.co/pytraveler/MiniMax-H3-Prompt-Rewriter-LoRA-Omni-GGUF/resolve/main/MiniMax-H3-Prompt-Rewriter-LoRA-Omni-Q8_0.gguf 343.2 MB -> ComfyUI/models/LLM/MiniMax-H3-Prompt-Rewriter-LoRA-Omni/ (README: "drop the file in models/LLM and it appears" as an `on disk:` adapter entry; Q8_0 = "half the size, same rewrite behaviour")
  - https://huggingface.co/lightx2v/MiniMax-H3-Prompt-Rewriter-LoRA-Omni/resolve/main/adapter_model.safetensors 1,291.9 MB + adapter_config.json + README.md + requirements.txt + system_prompt.py -> ComfyUI/models/LLM/MiniMax-H3-Prompt-Rewriter-LoRA-Omni/lightx2v-safetensors/ (the safetensors/PEFT route for a transformers base, the LoRA the task names by id)
- Runner: notes/pw1_download.ps1 run DETACHED (Start-Process powershell -WindowStyle Hidden, PID 34644, log notes/pw1_download.log + .err) with curl.exe -sSL --fail --retry 8 -C - so a dropped transfer resumes and the download survives across iterations. No GPU, no llama-swap, no ComfyUI port, no render: this is network + CPU only. Disk 51 GB free before, ~43 GB expected after.

### PW1b weights VERIFIED complete 2026-10-23 15:37:57 CT (log notes/pw1_download.log, "ALL DONE", 8/8 rc=0, wall 3.2 min, ~7.9 GB, C: 51 GB free -> 42 GB free)
- ComfyUI/models/LLM/Qwen2.5-Omni-7B-GGUF/Qwen2.5-Omni-7B-Q4_K_M.gguf 4,683,072,384 B (HF 4,683.1 MB, match) sha256 09883dff531dc56923a041c9c99c7c779e26ffde32caa83adeeb7502ec3b50fe - header (read with the pack's own minimax_h3_rewriter/gguf_meta.py read_keys(verify=True), the code the node uses to list models): general.architecture qwen2vl, tokenizer.ggml.model gpt2, general.file_type 15 = Q4_K_M
- ComfyUI/models/LLM/Qwen2.5-Omni-7B-GGUF/mmproj-Qwen2.5-Omni-7B-Q8_0.gguf 1,548,488,480 B (HF 1,548.5 MB) sha256 4a7bc5478a2ec8c5d186d63532eb22e75b79ba75ec3c0ce821676157318ef4ad - general.architecture clip, clip.projector_type **qwen2.5o** = the Omni projector with the audio encoder (the README's "vision only, not an Omni build" case is a plain Qwen2.5-VL mmproj, this is not it)
- ComfyUI/models/LLM/MiniMax-H3-Prompt-Rewriter-LoRA-Omni/MiniMax-H3-Prompt-Rewriter-LoRA-Omni-Q8_0.gguf 343,173,408 B (HF 343.2 MB) sha256 c43ebb841da384807a93370fe2f6da70dd4e8a6042c404ee6d8e7a2a2fa51dea - adapter.type lora, general.name "Omni Lora", general.architecture qwen2vl = same architecture as the base, so the adapter attaches
- ComfyUI/models/LLM/MiniMax-H3-Prompt-Rewriter-LoRA-Omni/lightx2v-safetensors/adapter_model.safetensors 1,291,899,160 B (HF 1,291.9 MB) sha256 25e325683814eccdfa8597d509e966f552722aeeecce31b38f6fc0089784345b, plus adapter_config.json 6,612 B, README.md 10,540 B, requirements.txt 184 B, system_prompt.py 22,163 B (the PEFT route for a transformers base; the GGUF route above is what we run on a 16 GB card)
- Next (PW1c): the pair lives in models/LLM so the node lists them as `on disk:`; restart ComfyUI only when idle (comfy_ctl status first) and confirm comfy_ok, then the HC3 REF2AV smoke test with no render.


### PW1b CHECK 2026-10-23 ~15:45 CT (iter 10, network + CPU only, 0 GPU min, no ComfyUI port, no restart)
- Independent re-verification of the 8 PW1b downloads: size vs the Hugging Face API + sha256 + file headers. Builder notes/ali173_pw1b_verify.py -> dump notes/pw1b_objective.json (8/8 PASS, rc 0).
- Size source (read-only GET, no POST/-H/cookies): curl.exe -sL --max-time 30 "https://huggingface.co/api/models/<repo>/tree/main?recursive=true" -o C:\AI\community\notes\web\pw1b_tree_*.json (3 repos: ggml-org/Qwen2.5-Omni-7B-GGUF, pytraveler/MiniMax-H3-Prompt-Rewriter-LoRA-Omni-GGUF, lightx2v/MiniMax-H3-Prompt-Rewriter-LoRA-Omni). The short form /api/<repo>/tree/main 404s (62-byte "we can't find the page" body) - the /api/models/ prefix is required.
- Result: local bytes == the API size on ALL 8 files (stricter than the task's ">="), total 7,866,672,931 B = 7,866.7 MB. Disk C: 51 GB free before the download, 44,990,410,752 B = 45 GB free now.
- sha256 re-hashed with hashlib this pass and matched the iter 09 record byte for byte: Qwen2.5-Omni-7B-Q4_K_M.gguf 09883dff531dc56923a041c9c99c7c779e26ffde32caa83adeeb7502ec3b50fe / mmproj-Qwen2.5-Omni-7B-Q8_0.gguf 4a7bc5478a2ec8c5d186d63532eb22e75b79ba75ec3c0ce821676157318ef4ad / MiniMax-H3-Prompt-Rewriter-LoRA-Omni-Q8_0.gguf c43ebb841da384807a93370fe2f6da70dd4e8a6042c404ee6d8e7a2a2fa51dea / adapter_model.safetensors 25e325683814eccdfa8597d509e966f552722aeeecce31b38f6fc0089784345b (small files: adapter_config.json 147a9235.., README.md 955026f5.., requirements.txt ab7f9e99.., system_prompt.py b06e6fd7..).
- Header integrity (no HTML error page, no partial transfer): the 3 GGUFs are magic b'GGUF' version 3; adapter_model.safetensors' JSON header parses = 53,520 B header, 392 tensors, __metadata__ format 'pt', first key base_model.model.model.layers.0.mlp.down_proj.lora_A.weight F32 [128, 18944].
- Nothing new installed; no pip, no GPU, no model loaded.

### PW1c REGISTER + RESTART CHECK 2026-10-23 ~16:03 CT (iter 10, ~1.5 GPU min of ComfyUI windows, no render, queue (0,0))
- Restart by the exact command: `python C:\AI\community\scripts\comfy_ctl.py restart` -> `16:02:26 stop: ComfyUI not loaded`, `16:02:52 COMFY_OK http://127.0.0.1:10004 running=['comfyui_auto']`, rc 0; `status` after = `comfy_ok=True queue=(0, 0) guard=(0, ['IDLE'])`.
- Live registration 6/6 (`notes/ali173_pw1c_live_check.py` run in the SAME call as the restart, dump `notes/pw1c_live_objective.json`): `MiniMaxH3PromptWriterOmni` IS registered (50 `MiniMax*` classes in a 5,523,929-byte /object_info, 2605 classes total, ComfyUI 0.38.0, cuda:0 RTX 5070 Ti); its `model` combo = 4 rows and names the on-disk base `Qwen2.5-Omni-7B GGUF Q4_K_M`; the adapter is listed `on disk: MiniMax-H3-Prompt-Rewriter-LoRA-Omni-Q8_0.gguf [qwen2vl, 0.3 GB]` (widget `MiniMaxH3RewriterOptions.adapter`); 29 `on disk:` rows; the `(no Qwen2.5-Omni base found - install llama_cpp, download the Qwen2.5-Omni pair)` sentinel is absent.
- The 3B row carries `(wrong size for the adapter)` and the 7B rows do not: the node judges the base against the adapter, so the 7B Q4_K_M pair is a usable pairing, not just a listed file.
- Offline half 8/8 (`notes/ali173_pw1c_offline.py`, folder_paths stubbed, no ComfyUI/torch/port; dump `notes/pw1c_objective.json`): the pack's own `discovery.scan_captioner_gguf(qwen2vl)` returns the 7B pair with `mmproj audio=True vision=True`; `discovery.scan_local_gguf_adapters()` returns the Q8_0 adapter; the catalog entry `Qwen2.5-Omni-7B GGUF Q4_K_M` resolves through `paths.present_pair` (both files) - so **no models.json entry is needed and none was added** (user `models.json` still valid JSON, unchanged).
- models.json decision: the only entry worth adding is the 18.6 GB `Qwen3.6-27B + pytraveler/MiniMax-H3-Prompt-Rewriter-LoRA` pair; adding it invites an 18.6 GB download on a box with 45 GB free for a route PW1d does not use. The Omni GGUF route needs no new bytes.
- Two layout fixes (moves, zero re-download, sizes unchanged): `models\LLM\MiniMax-H3-Prompt-Rewriter-LoRA-Omni-GGUF\MiniMax-H3-Prompt-Rewriter-LoRA-Omni-Q8_0.gguf` (343,173,408 B) - the folder now carries the repo-id name `paths.present_file()` looks for, it resolved to "" before; and the lightx2v safetensors set (README.md, adapter_config.json, adapter_model.safetensors 1,291,899,160 B, requirements.txt, system_prompt.py) moved UP from `models\LLM\MiniMax-H3-Prompt-Rewriter-LoRA-Omni\lightx2v-safetensors\` into `models\LLM\MiniMax-H3-Prompt-Rewriter-LoRA-Omni\`, where `paths.adapter_is_complete()` is true (`present_folder(complete=adapter_is_complete)` resolved; before: nothing).
- Full note: `notes/forge_pw1c_register.md`. Result: `p7/jobs/ali173_pw1c.result.json` ok=True with the comfy_ok line.

## 2026-10-25 04:29 CT - VIS: pi config change (not an install, no bytes downloaded)
- `C:/Users/derek/.pi/agent/settings.json`: `images.blockImages` `true` -> `false` (pi docs/settings.md:114, pi
  default `false`; `dist/core/sdk.js` `convertToLlm` replaces every `image` block with the literal text
  "Image reading is disabled." while it is true).
- `C:/Users/derek/.pi/agent/models.json`: `providers.llama-swap.models[coding_swift15_iq3s].input`
  `["text"]` -> `["text","image"]` (docs/models-configuration.md:38 default `["text"]`; the `openai-completions`
  provider emits `image_url` parts only inside `model.input.includes("image")`). `_esp` and
  `coding_sc117_strata` left `["text"]` on purpose = control rows.
- Backups (the only copies; `C:/Users/derek/.pi` is not a git repo):
  `C:/AI/community/notes/pi_config_snapshots/models-pre-VIS.json` (sha256 head 416bd0cecbd48d06, 2952 B) and
  `settings-pre-VIS.json` (d21909015d2a9f52, 1206 B). Revert = copy them back over the two live files.
- Not touched: `llama-swap.yaml`, `C:/AI/strata-0.2.2/strata-swift15-iq3s.json` (its `vision` section,
  `gpu: false` CPU encoder, is the server side that was already there), secrets, ComfyUI config.
- Proof + control: `C:/Users/derek/5slock/ralph-community/notes/vis/vis_proof_after.md` (9/9 with the gates
  open, `VISION-FAILED` with `blockImages` restored).

## 2026-10-29 Max (judge upgrade, Derrick approved 1:28 PM CT)
- venv C:\AI\community\judge\.venv (Python 3.12, separate from ComfyUI): pip install torch (CPU wheel, download.pytorch.org/whl/cpu), scenedetect, transformers, pillow, numpy (+ opencv-python as scenedetect dep). Versions: numpy==2.5.4, opencv-python==5.0.0.93, pillow==13.0.0, scenedetect==0.7.2, torch==2.15.0+cpu, transformers==5.22.0.
- HF model downloads (default HF cache): facebook/dinov2-small, openai/clip-vit-base-patch32.
- 2026-10-29 PM Max (judge refine): pip install mediapipe==1.2.0 into C:\AI\community\judge\.venv for a pose/anatomy trial; not used in the shipped judge (VLM zoom + CLIP ring + optical flow were tried instead and dropped).
- 2026-10-29 14:22 Max audit2: downloaded mediapipe pose_landmarker_full.task (float16, Google storage) to C:\AI\community\judge\models\ (CPU pose sanity experiment)


## 2026-10-30 Forge (sslcaio item 0, installs; approved Derrick 3:58 PM CT, GO=HOLD, NO renders)
Target = C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI (= llama-swap comfyui_auto, the render runtime; per Max's 4:16 PM CT correction). comfy-longvideo is the separate comfyui_longvideo model.

### Node packs git-cloned into TestRuntime custom_nodes (pip: none needed, all three ship no pip deps)
- ComfyUI-H3-Multishot - https://github.com/jlucasmcrell/ComfyUI-H3-Multishot @ tag v2.7.2 = d7d197709fc93c1afb125e3db1dfd4ac0ae28c60 (verified: GitHub tags API, tag v2.7.2 points at d7d19770; cloned with `git clone --branch v2.7.2 --depth 1`; `git checkout` is not permitted by this lane's policy, tag-clone is) - path C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\custom_nodes\ComfyUI-H3-Multishot - 19 MB - pyproject `dependencies = []` so no pip.
- comfyui-SelfLift - https://github.com/facok/comfyui-SelfLift @ 835c3cf7919410f71f414688f049c6ca497789d0 (2026-09-19) - 293 KB - provides SelfLiftH3Sampler / SelfLiftImageSampler / SelfLiftH3TST (the AIO graph's SelfLiftH3Sampler source). No requirements.txt, no pyproject deps, so no pip. Official source identified from the AIO graph's own Note node 131 "Model Links" custom_nodes list.
- ComfyUI_UniBlockSwap - https://github.com/smthemex/ComfyUI_UniBlockSwap @ 95bb6d9f302394e7a1f4a2ba29142d4f35dad225 (2026-09-11) - 11 MB - provides UniBlockSwap / UniBlockSwapTE / UniBlockSwapCacheControl (the AIO graph's UniBlockSwap source, same Note node 131). pyproject has no dependencies block, so no pip.
- Housekeeping: a plain default-branch clone of Multishot made this pass (before the tag route was found) was MOVED (not deleted) to C:\AI\community\_archive\2026-10-30-item0-installs\ComfyUI-H3-Multishot-default-branch-20261030.

### Already installed, verified not missing (no action)
- Tritant pack = ComfyUI_MiniMax_H3_Extender - https://github.com/tritant/ComfyUI_MiniMax_H3_Extender - present in TestRuntime custom_nodes at commit 0861230 (2026-10-20) = registry v3.0.13 (saved pages notes/web/02v_extender_registry.json + 02v_extender_repo.json). Its nodes MiniMaxH3Extender / MiniMaxH3MotionContextDiskJoin / MiniMaxH3MotionContextDiskFinalDecode (the "Final Decode" of the plan's seam/color-correction line) / MiniMaxH3MotionContextRAM / MiniMaxH3PromptPackBridge are in notes/objinfo/NODE_INDEX.txt lines 1505, 1522-1525.
- ComfyUI-KJNodes, rgthree-comfy, ComfyUI-VideoHelperSuite, ComfyMath: installed (git remotes verified).
- Fast Groups Bypasser, Label, GetNode, SetNode: ComfyUI frontend-only, never in object_info, so NOT missing, nothing installed.

### LoRAs referenced by the AIO json, downloaded (public, no login) into TestRuntime models\loras
Source = the AIO graph's own Note node 131: "loras: all-loras link to https://huggingface.co/noname1992/loras/tree/main" (HF tree body saved notes/web/hf_noname1992_loras_tree_20261030.json; all six files present there). Downloaded via https://huggingface.co/noname1992/loras/resolve/main/<file>, sha256 computed during download (full record notes/item0_lora_hashes_20261030.json). The six widget strengths in the json: 0.65 / 0.35 / 0.35 / 0.5 / 0.75 / 3.0.
- H3_Combat_V2.safetensors - 155,140,408 B - sha256 5b3edb09e9d6029439badf9bc9db4ba4a355ae679b0810888de82c4793c0bac8
- H3_Fight_Flow_V1.safetensors - 155,123,950 B - sha256 579e8eca67b6d70f4db94b2db67cd938751d576ee3d72aba875dae3d911f7398
- H3_speed_slider_1.1.safetensors - 170,459 B - sha256 e5970e97f8a5aa69e3ddc8d2ec4018e6c493cf8c7d0f1f1aa5c17d16e01270b1
- Motion_Repair_V2.safetensors - 155,127,836 B - sha256 edfa0e2858caeba7be9108883f61da8525d3c58af998c94ac7a449d9603d7574
- MysticXXX_MMH3-V1.safetensors - 596,467,449 B - sha256 7dd837f4c5420d4ec59f3ff1757b3f9d264a6c0f120d65d9c4f59c77584dd0be
- minimax_h3_dmad_full_dareties_v4_step600_comfy_fro.safetensors - 956,712,984 B - sha256 4d4ea608992d72303e4971f78728f587f43ecb72490f365a042ed82e37a907ce
Total 2,018,742,906 B. C: free was 239 GB, now ~237 GB. Nothing was behind a Civitai login: all six came from the graph author's own public HF mirror, so the brief's no-key rule was never exercised.

### Step-1 record (brief step 1, the comfy-longvideo clone, the entry step 1 needs)
- ComfyUI-H3-Multishot v2.7.2 (d7d197709fc93c1afb125e3db1dfd4ac0ae28c60) cloned 2026-10-30 into C:\AI\comfy-longvideo\ComfyUI\custom_nodes\ComfyUI-H3-Multishot - 19 MB on disk (measured du, Oct 30) - pyproject lists no pip deps, requirements.txt absent - nothing pip-installed.
- RESTART PENDING (both runtimes): ComfyUI was NOT started or restarted this item (Max restarts TestRuntime and regenerates notes/objinfo after item 0). The new nodes are not in the live object_info until then.

### Checks
- Banned face nodes scan (d): rg for InsightFace/ReActor/PuLID/InstantID/FaceDetailer/AutoCropFaces in the three new packs = 0 files. (Pre-existing PuLID/face packs in the runtime predate this item and are not in the AIO graph.)
- Adults tests named in AGENTS.md: 26 passed (run before the records).
- Renders: 0. GPU lock never touched. ComfyUI start/restart: no. Config: no.


## 2026-10-30 Forge (flux Item F1, model downloads; Derrick 5:06 PM CT; GO=HOLD, NO render)
Target = C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI (llama-swap comfyui_auto, the render runtime). Disk checked before any bytes moved: C: free 236.2 GB, so the ">= ~12 GB free per file" bar is met; after the download 228.96 GB free.
Placement rule used: UNETLoader takes a bare `unet_name`, and the baseline `FLUX-KLEIN-9B-FP8-NSFW.safetensors` + `flux-2-klein-4b-fp8.safetensors` already resolve from `models\diffusion_models\`, so both F1 files go there. `models\unet\` in this runtime holds only `.json` sidecars, no weights.

### Downloaded (public, no login, no token, no licence gate enforced)
- **flux-2-klein-9b-kv-fp8.safetensors** - 9,818,935,984 B (9.82 GB, matches the plan exactly) - sha256 `33f7da5625a00798349a719742999d3c7dd20c1a7eda14663922c363640728f1` - path `C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\models\diffusion_models\flux-2-klein-9b-kv-fp8.safetensors`
  - URL: `https://huggingface.co/black-forest-labs/FLUX.2-klein-9b-kv-fp8/resolve/main/flux-2-klein-9b-kv-fp8.safetensors` (repo `black-forest-labs/FLUX.2-klein-9b-kv-fp8`, commit 8430c03ee457ea86907ed31a009cd56280df003d). HF API for that repo reads `gated: false`, `private: false`, licence tag `license:other` = the FLUX Non-Commercial License the plan cites; no key/token was needed and none was sought (item rule).
  - Transfer: 17:11 CT 25 s probe landed 1,077,199,829 B, then `curl -L --fail --retry 3 -C -` into `*.part` finished it in 3 min 12 s (~43 MB/s, resumed from the probe bytes, no restart of the stream), renamed with `mv -n` (nothing overwritten, nothing deleted).
  - Proof: `Get-FileHash SHA256` (13 s) = `33F7DA56...728F1`, byte-for-byte equal to HF's own `X-Linked-ETag` for that file, and on-disk size equals HF's `X-Linked-Size` 9,818,935,984 B. So F3's model file is present and verified; the F3 run dir can name it.

### Not downloaded (Civitai login gate - per the item, no keys sought, URL handed to Max)
- **Miraclein 4.3 FP8, the 9.14 GB fp8 safetensors** (author 6tZ) - Civitai model 2453960, version 4.3 = 3272965, **file 3158025** `miracleinNSFWGeneration_43_3158025.safetensors`, API metadata `{"format":"SafeTensor","fp":"fp8"}`, sizeKB 9,142,971.4462890625 = **9,362,402,761 B** (the page shows it as 9.14 GB). Gate evidence and the full v4.3 file list (fp8 9.14/8.87/5.06, int8 8.87, bf16 17.73, GGUF Q4_0 + Q8_0) are in `notes/needs_derrick.md`, F1 section. Disambiguation done against the API's own `fp` tags: 3158025 is the only 9.14 GB fp8 file, 3158021 is the int8 8.87 GB, 3158029 the fp8 8.87 GB, 3157985 the fp8 5.06 GB.

### Checks
- AGENTS.md adults tests (`scripts/tests/test_p6_review.py` + `test_guard_scope.py`): **26 passed in 3.28 s**, run before the records.
- Renders: 0. GPU lock: never taken. ComfyUI: never started/restarted, no request sent. Config: untouched. No file deleted, no existing file overwritten (`mv -n`, `curl` into a `.part`).


## 2026-10-31 00:0x CT Max (long-video-queue lease): ComfyUI-H3-Continuum installed
- git clone https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum into C:\AI\comfy-longvideo\ComfyUI\custom_nodes, detached at 308653cff108061a94381cef446fef985384b214 = tag v3.10.2, 27.6 MB. No pip install run. Derrick yes 12:01 AM CT Oct 31.
- ComfyUI restart PENDING (Klein run holds gpu-render.lock). Rollback: remove folder, restart.


| gitleaks | 8.30.1 (windows_x64) | GitHub release `v8.30.1` `gitleaks_8.30.1_windows_x64.zip` + `gitleaks_8.30.1_checksums.txt` | SHA-256 `d29144deff3a68aa93ced33dddf84b7fdc26070add4aa0f4513094c8332afc4e` = official checksums.txt (MATCH True) | `C:\AI\tools\gitleaks` + User `Path` (17 -> 18) | 2026-11-01 08:05 CT | `gitleaks --version` -> 8.30.1; used by `C:\AI\fleet-brain\.githooks\pre-commit` (GAP3, fail-closed). Version pinned per the 2026-10-31 22:30 CT card; do not `--update` it. |
