# 2026-11-05 cleanup F2a - PARTIAL (make_b2_request --lora/--strength)

- PASS ID: interactive pi session (not a ralph run), Forge, AlienPc, 2026-11-05 12:29-13:00 CT, model 01r_gpt-5.2-codex_xhigh. Continues ralph run 20261105-115023 pass 1 (that pass = F6a, DONE).
- Item: `fix_plan.md` FORGE block F2a (2/6). Card: `C:\AI\fleet-brain\40_projects\2026-11-05-community-cleanup-card.md` item 2. Plan: `C:\AI\community\plans\2026-11-05-community-cleanup-plan.md` phase 2. Brief: `C:\AI\community\briefs\2026-11-05-0941-forge-cleanup-v2-brief.md` ("make_b2_request.py gains `--lora`/`--strength`").
- Status: `- [PARTIAL]`. CPU clauses met; the 2 GPU test cells and the green-pytest clause did not.

## Measured before any edit

- GPU gate (measured 12:30 CT): `C:\AI\locks\gpu-render.lock` absent; only `gpu-render.collected`. `C:\AI\render\scripts\comfy_ctl.py status` -> `comfy_ok=False guard_state=IDLE` and the running process `comfyui_auto.py` was listed. No render run: a render needs Derrick's GO (PROMPT 0e, render AGENTS).
- `python make_b2_request.py --help` shows `--lora LORA` and `--strength STRENGTH` (added by ralph-community `20bf547`, cleanup U6).
- Defect found: `--lora none` built a graph with a `LoraLoader` node named `"none"`. Node ids 27 vs `templates\b2.api.json` 26; `m_attn.model` = `['lora', 0]` in the build vs `['unet', 0]` in b2. The Do clause "`--lora none` must produce the plain b2 graph" fails.
- Node-by-node diff, retired `templates\bfs_klein9b.api.json` (its git blob at `25e403c^`, kept as `notes\_f2a\bfs_klein9b.api.json.retired`) vs `templates\flux_stills_s2_bfs.api.json`: 25 nodes each, 0 added, 0 removed, 0 `class_type` changes; 5 `inputs` value differences - node 2 LoraLoaderModelOnly `strength_model` 1.0 -> 0.5, node 20 RandomNoise `noise_seed` 432262096973493 -> 0, node 24 SaveImage `filename_prefix` community/flux_p1/TAG -> community/flux_s2/TAG, node 7 and node 8 LoadImage `image` (per-run placeholder paths). Full values: `notes\_f2a\node_diff_bfs_klein9b_to_flux_stills_s2_bfs.json`. So the merge is a structural no-op; the 5 differences are the S2 pass-2 LoRA strength and per-run placeholder values.
- Test baseline is not what the item states. `python -m pytest tests -q` in `C:\AI\community\scripts` at HEAD (`e280503`): **7 failed, 103 passed** (110 tests, not the item's "83"). The identical 7-name list comes from `8428dcc` (2026-11-04, the item's own baseline commit) - `diff` of the two lists: IDENTICAL - and also from `8a60f52` (U7) and `424f6d5`. So the red tests pre-date cleanup phases 1-7. Copies: `notes\_f2a\failures_8428dcc.txt`, `notes\_f2a\failures_head_before_my_change.txt` (the last reproduces the 7 at HEAD with my edits present: `pytest tests -q --ignore tests/test_b2_lora_param.py` -> 7 failed, 103 passed).
  - `tests/test_adults_guard.py::TestAdultsGuard::test_graph_require_adult` (assert False is not true, test_adults_guard.py:28)
  - `tests/test_phase1_still.py::TestTemplate::test_shipped_values` (0.5 != 1.0 - the test asserts the retired bfs_klein9b shipped values against the merged S2 template), `TestTemplate::test_guard_ok_on_template_prompts`, `TestPatcher::test_kv_plan_dials_patch_only_their_keys`, `TestStillBranch::test_still_ok_no_frames_or_audio`, `TestStillBranch::test_still_wrong_size_fails`, `TestStillBranch::test_video_job_still_uses_video_checks`

## The fix (one concern, 3 lines)

`C:\AI\community\scripts\make_b2_request.py`, in the argument post-processing, before the strength-needs-lora check:

```python
    # "none" is the documented off switch: --lora none must build the plain b2 graph (no LoraLoader node).
    if a.lora is not None and a.lora.strip().lower() == "none":
        a.lora = None
```

`git diff --stat` for this file: 1 file changed, 3 insertions(+). Nothing else in the file changed; `--lora`/`--strength`, the lora/strength pairing check, `build(g, lora=, strength=)` and the FC node wiring built by the agy lane (U6, ralph-community `20bf547` "cleanup U6") are untouched.

## Checks run after the fix (all offline: no HTTP, no GPU, no ComfyUI queue)

- `--lora none` -> `notes\_f2a\stage_nolora2\request.api.json`: 26 nodes (`templates\b2.api.json` = 26), no `lora` key, `m_attn.model` = `['unet', 0]`. Only the 4 documented per-run fields differ from `templates\b2.api.json`: c0 `prompt` (+ its `length`), img `image`, noise `noise_seed`, save `filename_prefix` - measured in `notes\_f2a\diff_nolora_vs_b2.json`.
- The defect reproduced on the old code path (handing the string to `build()` directly, what `main()` did before the fix): 27 nodes, `lora` present - `notes\_f2a\b2_lora_string_none_before_fix.nodes.txt`.
- `--lora FC_ARIANA_h3_face_v1.safetensors --strength 0.7` -> `notes\_f2a\stage_with_lora\request.api.json`: 27 nodes = the retired per-face template `C:\AI\_archive\2026-11-05-cleanup\7\faces\FC_ARIANA.api.json` (27, list `notes\_f2a\fc_ariana_nodes.txt`), `lora` LoraLoader with the same inputs, `m_attn.model` = `['lora', 0]`.
- New keeper test `C:\AI\community\scripts\tests\test_b2_lora_param.py` (5 tests, offline): LoRA injection wiring, strength applied, `--lora none` node set equals b2 exactly, CLI `--lora none` end-to-end, generated graph equals the archived FC file (skips if the archive copy is absent). `pytest tests/test_b2_lora_param.py -q`: **5 passed**.
- Full suite after my change: **7 failed, 108 passed** - same 7 pre-existing failures, +5 passing (my new file), 0 new failures.
- `python -m py_compile` on the 5 files I touched: ok.

## Retired-name references (the Do clause "update every reference")

Before: 4 live scripts named `bfs_klein9b`. After: **0 live path references**; 5 lines still contain the string as a retirement note / a verbatim quote, all in the same 4 files: `scripts\make_bfs_request.py:3` (Derrick's 2026-10-30 2:52 PM CT quote, kept verbatim + a note that the name is retired), `scripts\make_render.py:11,44`, `scripts\queue\queue_klein_explicit.py:5`, `scripts\queue\queue_storyboard.py:8` (each now names `templates\flux_stills_s2_bfs.api.json` and records the old name as merged/retired 2026-11-05). `rg -l bfs_klein9b` over `C:\AI\community\templates`, `C:\Users\derek\.pi\agent\skills`, `C:\AI\render`: **0 hits**, before and after. `__pycache__` hits: 0 (they regenerated). History files left as history, not rewritten: 175 files under `C:\AI\community` contain the string (runs/, plans/, briefs/, notes/, progress, `.bak`, `.pi\last-run.log`) - that count is for F2b.
- Pre-change copies of the two **untracked** queue scripts are in `C:\AI\_archive\2026-11-05-cleanup\2\scripts\queue\` (they have no git history; the other two edits are in tracked files).

## Not done (why F2a is PARTIAL)

1. The 2 GPU test cells (1 face-LoRA arm, 1 `--lora none` arm, each printing `OBJECTIVE ok` in `status.log`) are not run: no render GO from Derrick. GPU was free when measured, so this is ready to run on his word.
2. The "pytest stays green" clause cannot pass at F2a's code: 7 failures pre-date the whole cleanup (identical list at `8428dcc`, 2026-11-04). They assert the retired Phase-1 template values and the S2 template prompt against the current guard. Rewriting that spec is the FLX lane's call - card in `notes\needs_derrick.md`.
3. The archive placement in F2a's Do ("`bfs_klein9b.api.json` sits in `templates\_archive\` with a pointer README") is not how phase 2 landed, measured: `ls C:\AI\community\templates\_archive\` = `README.md` only, 0 `*.api.json`; the README points at `C:\AI\community\_archive\2026-11-04-superseded\templates\`, and `ls` of that path is **No such file or directory** (stale pointer, written 2026-11-04, untouched today); the retired copy is at `C:\AI\_archive\2026-11-05-cleanup\7\bfs_klein9b.api.json` (the agy lane's phase 7 archive). F2b's Do owns that placement ("`bfs_klein9b.api.json` in `templates\_archive\` and a README that names where it went") - recorded for the next pass, not changed here.

## Not touched

No GPU work, no model, no service, no loop, no ComfyUI, no llama-swap, no pi process. No render. No file deleted; nothing moved in `C:\AI\render`. No `.bak` created. No `git add -A`; no force-push; no GitHub. Sydney paths untouched. No secret values printed (the commit list is SHA/subject only).

## Files this pass wrote or changed (all in `C:\AI\community`)

- `scripts\make_b2_request.py` (the 3-line fix) - commit `50dda24` (parent `e280503`)
- `scripts\tests\test_b2_lora_param.py` (new, 5 offline tests) - same commit `50dda24`
- `scripts\make_render.py`, `scripts\make_bfs_request.py`, `scripts\queue\queue_klein_explicit.py`, `scripts\queue\queue_storyboard.py` (retired-name notes only; the two queue scripts went from untracked to tracked) - commit `95de74c`
- `notes\2026-11-05-cleanup-F2a-PARTIAL.md` (this record), `notes\_f2a\*` (the measured evidence, generated by `notes\_f2a\make_evidence.py`), `notes\progress.md`, `notes\needs_derrick.md`, `notes\2026-11-05-forge-blocker.md`, `notes\actions.log` - the records commit (parent `95de74c`); its own SHA is not written in this record (the F6a lesson: a SHA written before the last commit moves when the records complete) - read it with `git -C C:\AI\community log --oneline -1`.
- `C:\Users\derek\5slock\ralph-community\fix_plan.md`: F2a `- [ ]` -> `- [PARTIAL]` with a one-line-start RESULT paragraph (the house style, as F5a/F5b). Committed in that repo, remote `gitea`.
- Evidence kept: `C:\AI\community\notes\_f2a\` = `make_evidence.py` (the offline generator, re-runnable), `b2_nodes.txt`, `stage_nolora2/` + `stage_nolora2.nodes.txt`, `stage_with_lora/` + `stage_with_lora.nodes.txt`, `b2_lora_string_none_before_fix.nodes.txt`, `diff_nolora_vs_b2.json`, `bfs_klein9b.api.json.retired`, `node_diff_bfs_klein9b_to_flux_stills_s2_bfs.json`, `fc_ariana_nodes.txt`, `failures_8428dcc.txt`, `failures_head_before_my_change.txt`.

## Network (box state this pass)

12:30 CT: `git pull --rebase --autostash` in `C:\AI\fleet-brain` failed (qnap.tailf242b2.ts.net:443), pushes rc 128, `nslookup github.com` DNS timeout, `https://github.com` -> 000, SearXNG `192.168.0.147:8888` -> 000. Worked from local briefs/plans/learnings and the cached web copies (PROMPT 0a).

12:56 CT, re-measured: public DNS and internet are back (`github.com` -> 140.82.114.3, https 200); the QNAP/Tailscale path is still down - `qnap.tailf242b2.ts.net:443` no connection after 21 s, SearXNG `192.168.0.147:8888` -> 000. So every push is blocked: `git push gitea master` in `C:\AI\community` -> the 443 failure (the remote is named **`gitea`** in `C:\AI\community` and `C:\Users\derek\5slock\ralph-community`, not `origin`; my first two attempts used `origin` and their rc 128 was my command, stated not hidden). `C:\AI\fleet-brain` pushes to `origin` on the same host. Card: `notes\2026-11-05-forge-blocker.md` 12:56 CT.
