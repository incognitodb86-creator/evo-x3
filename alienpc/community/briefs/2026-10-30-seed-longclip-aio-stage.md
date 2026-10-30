# Forge brief: stage SS / LC / AIO test (NO RENDERS)  - 2026-10-30

Plan: brain 40_projects/max-fix-tests/plans/2026-10-30-seed-longclip-aio-test-plan.md (commit 8f7c549). Readable copy: C:\AI\community\runs\sslcaio_20261030\_inputs\plan.md
Derrick, 2:26 PM CT: "Forge should pick a new thing and write a new scene" / "Use H3-Multishot" / "Yes, install the long-clip pack and download the All-In-One workflow" / "Hold for now". 2:54 PM CT: "Run the long-clip arms at low res, then rerun only the winner at full B2 res".
GO = HOLD. Stage and dry-run only. Do not render. Do not install Continuum (LC-c waits for Derrick's install yes). Do not touch anything in Sydney's folders. The adults wording check stays exactly as it is.

## Steps
1. Install H3-Multishot. Check free disk first. Run `git clone https://github.com/jlucasmcrell/ComfyUI-H3-Multishot` into `C:\AI\comfy-longvideo\ComfyUI\custom_nodes` (expect v2.7.2, ~8.3 MB, commit d7d19770). pyproject lists no pip deps. If a requirements.txt shows up, read it and pip install nothing that touches torch/torchaudio. Log the size, path and commit to `notes\installs_downloads.md`. Do not restart ComfyUI while `C:\AI\locks\gpu-render.lock` is held. If a restart is needed, log it as pending.
2. Download the civitai 2906001 workflow zip, latest version ("Dmad+SelfLift Version", model version 3415436, file 3308286, 17 KB) using your own civitai access if you have any. Never print keys. If a login is needed and fails, STOP and report. Log it to `notes\installs_downloads.md`. A 307 to /login or an HTML file instead of a zip means a login is needed: stop, delete that file, skip to step 4, and note it in needs_derrick.md (Max is fetching the zip for you). Never search env vars, config or .env files for keys.
3. Open the zip. List every custom node and LoRA/model it needs (name, size, URL, already installed y/n) in `notes\needs_derrick.md`. Install none of them.
4. Pick one still from `C:\Users\derek\5slock\approved_characters` that was not used in recent tests (not E10, POOL_F041, M04, TERRACE). Crop or pad it to 768x1344 (never stretch). Write a 3-beat explicit scene in plain natural sentences: a fictional adult 21+, one motion per shot, anatomy placed relative to the body, dialogue in quotes. Save the still and `scene.txt` in a staged run dir under `C:\AI\community\runs\sslcaio_20261030\`.
5. Build templates in `C:\AI\community\templates\`, all on `10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors`:
   - `b2_pass1.api.json`: b2 minus the pass-2 upscale/sampler, decoding pass 1, at 124 f.
   - a Tritant chain template: 3 x 243 f, full_batch, Final Decode seam/color correction on.
   - a Multishot template: 3 shots from the CORE workflow, `---` between shots, ~10 s each.
   - an AIO template: the 2906001 stage on 10Eros (no merged checkpoint; drop any node or LoRA not installed and note it).
   Do not change any terrace-v3 setting.
6. Patch the requests. SS gets 8 seeds on beat 1. SS-full gets 2 placeholder slots (Derrick picks later). LC-a and LC-b get the same seed, one beat per segment. AIO gets beat 1 at 243 f. LC-a and LC-b requests run at 512x896 (per-run patch only; b2.api.json unchanged; frames unchanged). Confirm in the dry run that Tritant and Multishot accept 512x896 and report it. Then run `run_queue.py --run-dir <dir> --dry-run` for every job.
7. STOP. Report: the still path, the scene text, the dry-run output, the zip's node/LoRA list, and any pending restart.
