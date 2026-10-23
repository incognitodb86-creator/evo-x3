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
