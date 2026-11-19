r"""ALI-173 B1: append the installs log + the pruned AGENTS.md learnings verbatim. Run once."""
import io

FL = 'notes/forge-learnings.md'
INST = 'notes/installs_downloads.md'

learn = """
## ALI-173 B1 pass 2026-10-23 ~15:15 CT (AGENTS.md Learnings pruned to 15 bullets, verbatim here)
- Redo clips R4-R9: builders notes/ali163_hc_r5_build.py (sheet refs) then ali163_hc_r4g2_build.py (face-crop refs); 243 f = c0 124 + win1 119; R6-R9 request checker notes/ali163_hc_r6_request_check.py.
- Request checks notes/ali163_hc_r8 (solo) + ali163_hc_r9 (pair): diff vs the sibling graph = per-clip keys only (5 solo; 6 pair + c1.audio_vae); sheet scan = LoadImage paths
"""

inst = """
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
"""

with io.open(FL, 'a', encoding='utf-8') as f:
    f.write(learn)
with io.open(INST, 'a', encoding='utf-8') as f:
    f.write(inst)
print('appended forge-learnings + installs_downloads')
