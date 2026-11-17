# PW1c REGISTER + RESTART - ALI-173, 2026-10-23 ~16:03 CT (iter 10)

## What ran (exact)
- `python C:\AI\community\scripts\comfy_ctl.py status` first: `comfy_ok=False queue=None guard=(0, ['IDLE']) running=['coding_swift15_iq3s']` (the GPU LOCK was clear).
- `python C:\AI\community\scripts\comfy_ctl.py restart` (the exact command the task names): `stop: ComfyUI not loaded` -> `start: GET /comfyui/` -> `16:02:52 CT COMFY_OK http://127.0.0.1:10004 running=['comfyui_auto']`, rc 0.
- `python C:\AI\community\scripts\comfy_ctl.py status` after: `comfy_ok=True queue=(0, 0) guard=(0, ['IDLE']) running=['comfyui_auto']`.
- `python C:\AI\community\notes\ali173_pw1c_live_check.py 10004` in the SAME call as the restart: **6/6 PASS**.
- `python C:\AI\community\notes\ali173_pw1c_offline.py` (CPU, no port, no GPU): **8/8 PASS**.
- No smoke test (PW1d's), no render, no workflow queued, queue (0,0) the whole time.

## The registration answer (live, `/object_info` filtered in-process, never dumped raw)
- ComfyUI 0.38.0, python 3.12.10, `cuda:0 NVIDIA GeForce RTX 5070 Ti`, 2605 node classes, **50 `MiniMax*` classes**, including `MiniMaxH3PromptWriterOmni`, `MiniMaxH3UniversalRewriter`, `MiniMaxH3RewriterOptions`.
- `MiniMaxH3PromptWriterOmni.model` lists 4 rows, the on-disk base included:
  `Qwen2.5-Omni-7B GGUF Q4_K_M - 6.2 GB download - ~9 GB with the adapter and a 12k context`
  The scanned 7B row is *hidden*, by design: `model_sections.copy_of()` drops a scanned row that is the same file as a catalog entry, so the entry that runs is the entry the list names.
  The 3B row stays visible and is flagged `(wrong size for the adapter)` - the adapter is 7B-only, which is the proof the node checks the base matches the adapter.
- The adapter is listed by the node, on disk:
  `MiniMaxH3RewriterOptions.adapter = on disk: MiniMax-H3-Prompt-Rewriter-LoRA-Omni-Q8_0.gguf [qwen2vl, 0.3 GB]`
  plus the catalog alt `MiniMax-H3-Prompt-Rewriter-LoRA-Omni-Q8_0.gguf - 0.34 GB download`.
- 29 `on disk:` rows across the pack's widgets; the `'(no Qwen2.5-Omni base found - install llama_cpp, download the Qwen2.5-Omni pair)'` sentinel is **not** present in any list.

## The offline half (this is what makes the live answer trustworthy)
`notes/ali173_pw1c_offline.py` imports the pack's own modules with `folder_paths` stubbed (no ComfyUI, no torch, no port) and calls the exact three functions the dropdown is built from:
- `discovery.scan_captioner_gguf(GGUF_ARCH_OMNI)` -> `Qwen2.5-Omni-7B-Q4_K_M.gguf [+mmproj, vision, audio, 5.8 GB]`, model `LLM/Qwen2.5-Omni-7B-GGUF/Qwen2.5-Omni-7B-Q4_K_M.gguf`, mmproj `LLM/Qwen2.5-Omni-7B-GGUF/mmproj-Qwen2.5-Omni-7B-Q8_0.gguf`; `gguf_header(mmproj)` = `audio True, vision True` (a real Omni projector) and `gguf_problem_omni()` = None (no "wrong size" suffix).
- `discovery.scan_local_gguf_adapters()` -> `MiniMax-H3-Prompt-Rewriter-LoRA-Omni-Q8_0.gguf [qwen2vl, 0.3 GB]`.
- `catalog.models_omni()` entry `Qwen2.5-Omni-7B GGUF Q4_K_M` -> `on_disk = [that model, that mmproj]` through `paths.present_pair`.

## models.json: NOT edited, on purpose
`C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\user\minimax_h3_rewriter\models.json` is unchanged. Discovery + the built-in catalog already resolve every file PW1b put on disk, so the task's condition ("add an entry if discovery misses one") is not met. The one entry that would go in is the 18.6 GB `Qwen3.6-27B + pytraveler/MiniMax-H3-Prompt-Rewriter-LoRA` pair (18.7 GB) - listing it invites an 18.6 GB download on a card box with 45 GB free, and PW1d runs the Omni route, which needs no new bytes.

## Two layout fixes found by reading the resolver, not guessed
The scanner finds a GGUF at depth 2 under `models/LLM`, but the catalog's *run this entry* path uses the **repo-id folder name**. PW1b's folders did not match, so the files were listed but not resolvable:
1. `paths.present_file(repo, file)` looks in `LLM/<repo last segment>/<file>` -> the Q8_0 adapter moved to
   `models/LLM/MiniMax-H3-Prompt-Rewriter-LoRA-Omni-GGUF/MiniMax-H3-Prompt-Rewriter-LoRA-Omni-Q8_0.gguf` (repo `pytraveler/MiniMax-H3-Prompt-Rewriter-LoRA-Omni-GGUF`). Before the move `present_file` returned "" (a pick would have re-downloaded).
2. `paths.present_folder(repo, complete=paths.adapter_is_complete)` wants `adapter_config.json` + `adapter_model.safetensors` **in** the repo folder -> the lightx2v files moved up from `...\MiniMax-H3-Prompt-Rewriter-LoRA-Omni\lightx2v-safetensors\` into `...\MiniMax-H3-Prompt-Rewriter-LoRA-Omni\`. Before: the safetensors route saw nothing; after: `adapter_is_complete = True`.
No bytes re-downloaded (moves only, sha256 of iter 09 still refers to the same content, sizes unchanged: 343,173,408 B and 1,291,899,160 B).

## Cost
~1.5 GPU minutes of ComfyUI windows (three llama-swap wakes, all status/registration). The task text said "0 GPU minutes for this pass", which is only true of a pass that never restarts; the restart it demands is the action that owns the GPU, so the minutes are recorded in `notes/bakeoff_gpu_ledger.md` and no render ran.

## Files
`notes/ali173_pw1c_offline.py`, `notes/ali173_pw1c_live_check.py`, `notes/ali173_pw1c_dump_node.py`, dumps `notes/pw1c_objective.json` + `notes/pw1c_live_objective.json` + `notes/pw1c_nodes.json`, `notes/forge_pw1c_register.md`, `notes/bakeoff_gpu_ledger.md`, `notes/installs_downloads.md` (PW1c section), `p7/jobs/ali173_pw1c.result.json` (ok=True, comfy_ok line), TASKS.md, AGENTS.md, `notes/self_diagnosis.md`.
