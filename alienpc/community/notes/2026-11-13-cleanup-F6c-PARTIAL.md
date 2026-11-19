# F6c phase 6c - the comfy-render skill around the one workflow script: PARTIAL

Worked 2026-11-13 23:5x CT (Forge, ralph pass). Card item "Make the comfy-render skill around the one workflow script"; item line: `fix_plan.md` F6c. Marked `[PARTIAL]`, not ticked: every clause except the test render is met and measured; the render needs Derrick's GO for a GPU window.

No skill file was edited this pass (the smallest change that meets the done-line was zero edits), so there is no `.bak` of any skill file and nothing to archive from `.pi\agent`. llama-swap (:8080), gpu_lock_gate (:8085), strata, pi-mobile, ComfyUI: not touched. No GPU work, no lock taken, no render queued, no model loaded by me (the pi probes ran on the model already loaded).

## 1. The gate, measured first (same rule as F2a)

| check | command | result |
|---|---|---|
| no GPU render lock | `ls C:/AI/locks/` | only `_removed`, `gpu-render.collected`, and two `.bak-2026111*` files - **no live `gpu-render.lock`** |
| no queued ComfyUI job | `C:\AI\director\.venv\Scripts\python.exe C:\AI\community\scripts\comfy_ctl.py status` | 23:52:27 CT `comfy_ok=False queue=None guard=(0, ['IDLE']) running=['comfyui_auto']` - ComfyUI unloaded, so nothing of mine queued |

Gate OPEN, so the item was worked, not deferred.

## 2. What already exists (the card's point: search first, one implementation)

- `C:\Users\derek\.pi\agent\skills\comfy-render` is a **symlink/junction to `C:\AI\community\skills\comfy-render`** (`ls -la .pi/agent/skills`: `comfy-render -> /c/AI/community/skills/comfy-render`, made 2026-11-10 under needs_derrick ask 8, so the loaded copy cannot drift from the community master).
- `SKILL.md` (1,609 B): front matter `name: comfy-render`; body routes every submission to the **existing locked runners** - "Legacy / do-not-call: `scripts/render_workflow.py` is legacy: it bypasses `gpu-render.lock` and the locked baseline. Do not call it; all submissions go through `run_queue.py` or `submit_parody_run.py`." It carries the pointer line to `C:\AI\render\AGENTS.md`, states it never copies template workflows, points at the canonical templates in `C:\AI\community\templates\`, and defers named INDEX + RefMod parodies to `h3-parody-identity`.
- `scripts/render_workflow.py` (117 lines) is the thin legacy builder: docstring names the route (`http://127.0.0.1:8080/upstream/comfyui_auto` "reusing comm.py"), it imports `comm` and `make_b2_request.build` from `C:\AI\community\scripts`, guards with `comm.guard_ok`, POSTs `f"{comm.BASE}/prompt"` with `comm.SUBMIT_TIMEOUT`. It is **not** the call path the skill tells an agent to use, so the box keeps one render implementation (`run_queue.py` / `run_graph_job.py` under `gpu-render.lock`).

## 3. Clause-by-clause (the Pass line)

| clause | command run this pass | result |
|---|---|---|
| `ls C:/Users/derek/.pi/agent/skills/comfy-render` shows SKILL.md + scripts\ | `ls`, `wc -l` | **PASS** - `SKILL.md` (14 lines) + `scripts/render_workflow.py` (117 lines) |
| description length prints <=1024 with a python one-liner | front-matter parse of every `*/SKILL.md` in the live skills dirs | **PASS** - comfy-render = **287 chars**; all 9 render/H3 skills under 1024 (max 698) |
| pi discovers the skill, answer contains comfy-render and NOT alienpc-local-video-ops | `pi --print --provider llama-swap --model coding_swift15_iq3s_esp --no-session "List the available skill names ONLY, one per line, nothing else."` (model already loaded, no GPU) | **PASS** - 46 names, `comfy-render` present (`grep -c` = 1), `alienpc-local-video-ops` absent (`grep -c` = 0). Proof: `notes/_f6c_pi_skill_list.txt`. The name is gone from every live skills dir (F5b/U5 folded it into video-render) |
| one test render through the skill passes with an OBJECTIVE ok line (GPU gate, lock, small frames, non-Sydney) | staged + dry-run only; **not queued** | **NOT MET - needs Derrick's GO for a GPU window** (standing rule: any render without his go). Section 4 |

## 4. The render is staged so GO is one word

Run dir `C:\AI\community\runs\f6c_comfy_render_skill_2026-11-13\`:
- `c1_f6c_preflight/request.api.json` - the **existing non-Sydney B2 graph** copied byte-for-byte from `runs/speed_ab_20261113/arm_C_6step_base/request.api.json` (22 nodes, seed 51083601, 124 f, 768x1344, euler/simple/6 steps). Only `save.filename_prefix` changed: `community/f6c_comfy_render_skill_20261113/c1_f6c_preflight`. No new builder, no graph invented.
- `_render_order.json` - 1 clip, the shape `submit_parody_run.py` writes (`pos/tag/arm/scene/seed`).
- Adults gate: `comm.guard_reason(g)` = `(True, '')`.
- Dry run (the item's own dry-run rule, no lock/GPU/HTTP): `run_queue.py --run-dir runs/f6c_comfy_render_skill_2026-11-13 --frames 124 --size 768x1344 --no-upscale --dry-run` → rc 0
  `queue 1 clips, 0 already DONE ok, 1 to render / pos 1 c1_f6c_preflight / prompt_ids on file: 0 / post-pass: off (--no-upscale) / dry run: no lock, GPU or HTTP call made`.

The command for the GO (must be `--detach`: this pass's model is llama-swap's and a render request unloads it; `run_queue.py` runs its own pytest gate and takes/releases `gpu-render.lock` itself):

```
C:\AI\director\.venv\Scripts\python.exe C:\AI\community\scripts\run_queue.py \
  --run-dir C:\AI\community\runs\f6c_comfy_render_skill_2026-11-13 --frames 124 --size 768x1344 --no-upscale --detach
```

Cost is measured, not estimated: the same graph rendered 124 f in **122 s** on this box today (`runs/speed_ab_20261113/status.log` 22:21:11 CT `OBJECTIVE ok arm_C_6step_base frames=124 size=768x1344 audio=True bytes=1594553`), plus ~35-40 s of comfyui_auto wake.

**Why "small frames" is not smaller:** H3 is on the `(frames - 5) % 17 == 0` grid, so the floor is 22 f, and no 22-frame render exists on this box as precedent (the `graph_expect` of a staged clip must equal what OBJECTIVE checks). 124 f / 768x1344 is the shape with measured OBJECTIVE-ok history today. If Derrick names a smaller/other shape, that replaces the staged clip.

## 5. The ComfyUI API reference (the Do asks for it)

The card's `https://docs.comfy.org/development/comfyui-server/comms_routes` contract is what `comm.py` implements and what the skill's route points at: `POST /prompt` (submit, returns `prompt_id`) then `GET /history/<prompt_id>` (outputs), through llama-swap's documented `/comfyui/` passthrough to the reserved `comfyui_auto` (`run_graph_job.py:31-34`, `comm.py:6`). Not re-opened as a live page this pass; the contract is cited from the code and the CA2 usage audit.

## 6. FYI found, not fixed (filed for F6b / Max)

The Do's "presets are names/arguments pointing at templates" is **not** built as named preset flags: `render_workflow.py --help` exposes `--template / --prompt(-file) / --seed / --image / --lora / --strength / --refmod / --frames / --prefix / --dry-run`, and SKILL.md points at the canonical templates with no copies, but it names **no preset for `flux_stills_s2_bfs` / `flux_stills_s2_kv`**. Two pointer lines would close that; left undone because F6b rewrites skills and script paths (the C:\AI\lib move) and touching the same file twice in one job is churn.

Also: three of the four "render skills" (`alienpc-hardcore-i2v-director`, `alienpc-stills-pose-edit-prompting`, `image-render`) are **plain copies** in `.pi/agent/skills` while five others are junctions - byte-identical today (verified by `cmp`, all 9 SAME), so no live drift, but they can drift. Not F6c's scope; recorded for the mirror/F6b pass.

## 7. Records

- This note: `C:\AI\community\notes\2026-11-13-cleanup-F6c-PARTIAL.md`
- Ask + evidence card: `C:\AI\community\notes\needs_derrick.md` "F6c needs one render GO (2026-11-13 23:5x CT)" and its source `notes/_f6c_ask.md`
- pi discovery proof: `C:\Users\derek\forge\ralph-community\notes\_f6c_pi_skill_list.txt` (46 names)
- Staged render dir: `C:\AI\community\runs\f6c_comfy_render_skill_2026-11-13\` (preflight_arm_c = the first dry-run copy, c1_f6c_preflight = the one to queue)
- fix_plan `[PARTIAL]` RESULT + FYI sub-bullet; `notes/progress.md` line; actions.log START / FIX / DONE
- Commits: ralph-community `5cba23d` (fix_plan + progress), community `8d08617` (ask record) - both pushed to gitea master at rc 0 (Gitea answered 200 this pass, unlike the 2026-11-05 502 series).
- Sydney: FC_SYDNEY named by path only, never opened; no `C:\Users\derek\sydney\` path touched.
