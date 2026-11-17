# -*- coding: utf-8 -*-
"""Append item-0 (sslcaio staging installs) records. One-shot, run once 2026-10-30."""
import pathlib
import datetime

ts = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
ts = ts[:-2] + ":" + ts[-2:]

installs = """

## 2026-10-30 Forge (sslcaio item 0, installs; approved Derrick 3:58 PM CT, GO=HOLD, NO renders)
Target = C:\\Users\\derek\\HardcoreNSFW-TestRuntime\\ComfyUI (= llama-swap comfyui_auto, the render runtime; per Max's 4:16 PM CT correction). comfy-longvideo is the separate comfyui_longvideo model.

### Node packs git-cloned into TestRuntime custom_nodes (pip: none needed, all three ship no pip deps)
- ComfyUI-H3-Multishot - https://github.com/jlucasmcrell/ComfyUI-H3-Multishot @ tag v2.7.2 = d7d197709fc93c1afb125e3db1dfd4ac0ae28c60 (verified: GitHub tags API, tag v2.7.2 points at d7d19770; cloned with `git clone --branch v2.7.2 --depth 1`; `git checkout` is not permitted by this lane's policy, tag-clone is) - path C:\\Users\\derek\\HardcoreNSFW-TestRuntime\\ComfyUI\\custom_nodes\\ComfyUI-H3-Multishot - 19 MB - pyproject `dependencies = []` so no pip.
- comfyui-SelfLift - https://github.com/facok/comfyui-SelfLift @ 835c3cf7919410f71f414688f049c6ca497789d0 (2026-09-19) - 293 KB - provides SelfLiftH3Sampler / SelfLiftImageSampler / SelfLiftH3TST (the AIO graph's SelfLiftH3Sampler source). No requirements.txt, no pyproject deps, so no pip. Official source identified from the AIO graph's own Note node 131 "Model Links" custom_nodes list.
- ComfyUI_UniBlockSwap - https://github.com/smthemex/ComfyUI_UniBlockSwap @ 95bb6d9f302394e7a1f4a2ba29142d4f35dad225 (2026-09-11) - 11 MB - provides UniBlockSwap / UniBlockSwapTE / UniBlockSwapCacheControl (the AIO graph's UniBlockSwap source, same Note node 131). pyproject has no dependencies block, so no pip.
- Housekeeping: a plain default-branch clone of Multishot made this pass (before the tag route was found) was MOVED (not deleted) to C:\\AI\\community\\_archive\\2026-10-30-item0-installs\\ComfyUI-H3-Multishot-default-branch-20261030.

### Already installed, verified not missing (no action)
- Tritant pack = ComfyUI_MiniMax_H3_Extender - https://github.com/tritant/ComfyUI_MiniMax_H3_Extender - present in TestRuntime custom_nodes at commit 0861230 (2026-10-20) = registry v3.0.13 (saved pages notes/web/02v_extender_registry.json + 02v_extender_repo.json). Its nodes MiniMaxH3Extender / MiniMaxH3MotionContextDiskJoin / MiniMaxH3MotionContextDiskFinalDecode (the "Final Decode" of the plan's seam/color-correction line) / MiniMaxH3MotionContextRAM / MiniMaxH3PromptPackBridge are in notes/objinfo/NODE_INDEX.txt lines 1505, 1522-1525.
- ComfyUI-KJNodes, rgthree-comfy, ComfyUI-VideoHelperSuite, ComfyMath: installed (git remotes verified).
- Fast Groups Bypasser, Label, GetNode, SetNode: ComfyUI frontend-only, never in object_info, so NOT missing, nothing installed.

### LoRAs referenced by the AIO json, downloaded (public, no login) into TestRuntime models\\loras
Source = the AIO graph's own Note node 131: "loras: all-loras link to https://huggingface.co/noname1992/loras/tree/main" (HF tree body saved notes/web/hf_noname1992_loras_tree_20261030.json; all six files present there). Downloaded via https://huggingface.co/noname1992/loras/resolve/main/<file>, sha256 computed during download (full record notes/item0_lora_hashes_20261030.json). The six widget strengths in the json: 0.65 / 0.35 / 0.35 / 0.5 / 0.75 / 3.0.
- H3_Combat_V2.safetensors - 155,140,408 B - sha256 5b3edb09e9d6029439badf9bc9db4ba4a355ae679b0810888de82c4793c0bac8
- H3_Fight_Flow_V1.safetensors - 155,123,950 B - sha256 579e8eca67b6d70f4db94b2db67cd938751d576ee3d72aba875dae3d911f7398
- H3_speed_slider_1.1.safetensors - 170,459 B - sha256 e5970e97f8a5aa69e3ddc8d2ec4018e6c493cf8c7d0f1f1aa5c17d16e01270b1
- Motion_Repair_V2.safetensors - 155,127,836 B - sha256 edfa0e2858caeba7be9108883f61da8525d3c58af998c94ac7a449d9603d7574
- MysticXXX_MMH3-V1.safetensors - 596,467,449 B - sha256 7dd837f4c5420d4ec59f3ff1757b3f9d264a6c0f120d65d9c4f59c77584dd0be
- minimax_h3_dmad_full_dareties_v4_step600_comfy_fro.safetensors - 956,712,984 B - sha256 4d4ea608992d72303e4971f78728f587f43ecb72490f365a042ed82e37a907ce
Total 2,018,742,906 B. C: free was 239 GB, now ~237 GB. Nothing was behind a Civitai login: all six came from the graph author's own public HF mirror, so the brief's no-key rule was never exercised.

### Step-1 record (brief step 1, the comfy-longvideo clone, the entry step 1 needs)
- ComfyUI-H3-Multishot v2.7.2 (d7d197709fc93c1afb125e3db1dfd4ac0ae28c60) cloned 2026-10-30 into C:\\AI\\comfy-longvideo\\ComfyUI\\custom_nodes\\ComfyUI-H3-Multishot - 19 MB on disk (measured du, Oct 30) - pyproject lists no pip deps, requirements.txt absent - nothing pip-installed.
- RESTART PENDING (both runtimes): ComfyUI was NOT started or restarted this item (Max restarts TestRuntime and regenerates notes/objinfo after item 0). The new nodes are not in the live object_info until then.

### Checks
- Banned face nodes scan (d): rg for InsightFace/ReActor/PuLID/InstantID/FaceDetailer/AutoCropFaces in the three new packs = 0 files. (Pre-existing PuLID/face packs in the runtime predate this item and are not in the AIO graph.)
- Adults tests named in AGENTS.md: 26 passed (run before the records).
- Renders: 0. GPU lock never touched. ComfyUI start/restart: no. Config: no.
"""

needs = """

## 2026-10-30 Forge (sslcaio item 0) - leftovers after installs
- Nothing behind a Civitai login: all six AIO-graph LoRAs were public on the graph author's own HF mirror (noname1992/loras) and are installed with sha256 (notes/installs_downloads.md, item 0 section).
- Out of item 0 scope (not a LoRA, not a node), graph-pinned model file, public, NOT downloaded: `h3_upscaler_lms_v0.1.safetensors` (690.6 MB) named in SelfLiftH3Sampler's widget; source per graph Note 131: https://huggingface.co/Alissonerdx/Minimax-H3-ComfyUI/resolve/main/latent_upscaler/h3_upscaler_lms_v0.1.safetensors (tree body saved notes/web/hf_alissonerdx_tree_20261030.json). NOT blocking: models/latent_upscale_models already holds two working H3 latent upscalers and the SelfLift node auto-selects the first filename containing "h3"; item 3's AIO template wires that widget to an installed file. Max: fetch it only if you want the exact pinned file.
- Banned face nodes (d): 0 hits in the three packs installed this item, nothing to refuse.
- Restart pending: TestRuntime ComfyUI must be restarted (by Max) before H3-Multishot, SelfLift, UniBlockSwap nodes appear in object_info; then regenerate notes/objinfo.
"""

prog = ("\n- " + ts + " [MAX sslcaio item 0, installs, NO render] Approved installs (Derrick 3:58 PM CT) staged into the "
        "render runtime (HardcoreNSFW-TestRuntime ComfyUI, per Max's 4:16 PM correction): git clone x3 into custom_nodes - "
        "ComfyUI-H3-Multishot v2.7.2=d7d19770 (tag-clone route; `git checkout` is policy-blocked; a stray default-branch clone "
        "was moved to _archive\\2026-10-30-item0-installs), comfyui-SelfLift 835c3cf (SelfLiftH3Sampler), ComfyUI_UniBlockSwap "
        "95bb6d9 (UniBlockSwap); sources provenanced from the AIO graph's own Note 131. Tritant pack = ComfyUI_MiniMax_H3_Extender "
        "@ 0861230 = registry v3.0.13 CONFIRMED PRESENT (no install); KJNodes/rgthree/VHS/ComfyMath present; frontend-only nodes "
        "correctly treated as not-missing. All 6 AIO LoRAs (H3_Combat_V2, Motion_Repair_V2, H3_Fight_Flow_V1, MysticXXX_MMH3-V1, "
        "minimax_h3_dmad_full_dareties_v4_step600_comfy_fro, H3_speed_slider_1.1 at widget strengths 0.65/0.35/0.35/0.5/0.75/3.0) "
        "from the graph author's public HF mirror into models\\loras, 2,018,742,906 B, per-file sha256 in notes/item0_lora_hashes_20261030.json; "
        "no Civitai login needed, keys never sought. No pip (all three packs ship zero deps). Banned-face-node scan on new packs: 0. "
        "Graph-pinned h3_upscaler_lms_v0.1 NOT downloaded (not a LoRA; two working H3 upscalers + SelfLift auto-select cover it) - "
        "noted in needs_derrick.md for Max. AGENTS.md adults tests: 26 passed. Full step-1 (comfy-longvideo Multishot, 19 MB, d7d19770) "
        "+ all installs logged in notes/installs_downloads.md; TestRuntime restart PENDING for Max. 0 renders, no lock, ComfyUI never "
        "started/restarted, no config touched.\n")

act = (ts + " Forge: sslcaio item 0 (installs, GO=HOLD) DONE - 3 node packs cloned into TestRuntime custom_nodes "
       "(Multishot v2.7.2=d7d19770, SelfLift 835c3cf, UniBlockSwap 95bb6d9), Tritant Extender confirmed pre-installed "
       "(0861230/v3.0.13), 6 AIO LoRAs downloaded from the graph author's public HF mirror (2,018.7 MB, sha256 in "
       "notes/item0_lora_hashes_20261030.json), 0 banned-face hits, no pip, restart pending for Max; adults tests 26 passed; "
       "0 renders, no lock, ComfyUI untouched.\n")

root = pathlib.Path(r"C:\AI\community\notes")
(root / "installs_downloads.md").open("a", encoding="utf-8", newline="\n").write(installs)
(root / "needs_derrick.md").open("a", encoding="utf-8", newline="\n").write(needs)
(root / "progress.md").open("a", encoding="utf-8", newline="\n").write(prog)
(root / "actions.log").open("a", encoding="utf-8", newline="\n").write(act)
print("appended ok, ts=", ts)
