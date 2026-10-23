# ALI-173 BAKEOFF GPU ledger - C:/AI/community/notes/bakeoff_gpu_ledger.md

Cap from `C:/Users/derek/5slock/ralph-community/logs/p7_budget.json`: cap_min 615, job_cap 45.
Read that file for the authoritative `used_min`/`jobs`; this ledger only records what the
bakeoff opened on the card, one line per ComfyUI window. "open" = ComfyUI loaded (llama-swap
swap or a render). Nothing here ran a workflow unless the row says so.

| ts (CT) | window | min | what ran | queue | proof |
|---|---|---|---|---|---|
| 2026-10-23 15:57:35 -> 15:58:04 | ComfyUI wake (llama-swap GET /comfyui/) | 0.5 | `/system_stats`, `/queue`, `/object_info` filtered in-process | (0, 0) | `notes/pw1c_live_objective.json` (run 1) |
| 2026-10-23 15:59:25 -> 15:59:54 | ComfyUI wake | 0.5 | live check + `/object_info/<class>` dumps of 3 rewriter classes | (0, 0) | `notes/pw1c_nodes.json` |
| 2026-10-23 16:02:26 -> 16:02:57 | `comfy_ctl restart` (stop not-loaded -> wake) | 0.5 | PW1c live registration check 6/6 | (0, 0) | `p7/jobs/ali173_pw1c.result.json`, `notes/pw1c_live_objective.json` |

Bakeoff total so far: **1.5 min** (PW1b = 0, PW1c = 1.5, no render yet).

Readings that frame the card, taken this pass: at 15:58:04 the ComfyUI device line was
`cuda:0 NVIDIA GeForce RTX 5070 Ti : cudaMallocAsync`; llama-swap ran `['comfyui_auto']` while
ComfyUI was up and `['coding_swift15_iq3s']` when it slept. Between the windows ComfyUI is
unloaded by llama-swap, so a check written as "wake, then ask" in a LATER call hits a refused
port - every live row above was captured in the same tool call that opened the window.
| 2026-10-23 16:17:23 -> 2026-10-23 16:17:28 | ComfyUI wake + ONE Omni prompt-writer job (text only, no DiT) | 0.1 | PW1d smoke rewrite REF2AV 16:9 10.0 s, seed 42, 7B Q4_K_M + Q8_0 Omni adapter | (0, 0) | `notes/pw1_smoke_omni_hc3.md`, `notes/pw1d_objective.json` |
| 2026-10-23 16:15:35 -> 16:16:02 | ComfyUI wake (llama-swap GET /comfyui/) | 0.5 | comfy_ok, live /object_info/<class> of the writer + options nodes (the first read was wrapped by class key -> 0 rows) | (0, 0) | `notes/pw1d_objective.json` |
| 2026-10-23 16:16:57 -> 16:17:24 | ComfyUI wake + ONE Omni prompt-writer job (text only, no DiT) | 0.6 | PW1d smoke rewrite REF2AV 16:9 10.0 s seed 42, 7B Q4_K_M + on-disk Q8_0 Omni adapter, auto_download False - **failed in 0.19 s**: execute() got an unexpected keyword argument 'ref_0' (autogrow references must be a LIST of links) | (1,0) -> (0,0) | `notes/pw1_smoke_omni_hc3.md`, `notes/pw1d_graph.json`, ComfyUI console `user/comfyui_10004.log` |
