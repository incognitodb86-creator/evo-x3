# Review: UNI-OPUS-HERMES-WORKSPACES/BRIEF.md (2026-11-20)

Reviewer: `evo-plan-reviewer` subagent, spot-checked by Opus (VS Code, Windows clone) on mono `8b45a745`, 2026-11-20
~8:40 AM CT. Read-only; nothing was applied. The brief was written outside this repo and saved verbatim (t3015u), so
every claim in it was checked against the repo and the live snapshot (`hosts/x3/live/`).

## VERDICT: BLOCK. Do not apply this brief. Use the replacement instead.

The goal is right: two workspaces (render and coding) on the one resident Flash-Next slot, each with good sampler
settings. The brief as written would break the live setup in four places and redoes work that is already done.
Replacement: [../UNI-APPLY-X3-HERMES-WORKSPACES/BRIEF.md](../UNI-APPLY-X3-HERMES-WORKSPACES/BRIEF.md) (2 aliases, 1 new
profile, 1 `AGENTS.md`).

## Blockers (VERIFIED)

| # | Brief lines | Problem | Evidence |
|---|---|---|---|
| 1 | 2205-2250 (Track 4) | Rewrites the WebUI unit with the wrong paths (`/home/evo/AI/hermes-webui`, `.venv/bin/python3 app.py`, `hermes-secrets.env`). | Live unit `hosts/x3/live/systemd/evo-user/hermes-webui.service`: `/usr/bin/python3 /home/evo/hermes-webui/bootstrap.py`, `HERMES_WEBUI_CHAT_BACKEND=gateway` on `:8642`, `EnvironmentFile=%h/.config/evo-x3/llm.env`, plus drop-ins `20-media-roots.conf` and `30-workspace.conf`. |
| 2 | 274-275, 301-302, 314-315 (Track 1) | Aliases send `chat_template_kwargs.enable_thinking` and `reasoning_effort` together. Gufo 0.35.0 answers HTTP 400 `invalid_reasoning`. | `records/plan-v32/PHASE-0-RESULT.md`; F4 plan section 0 ("Gufo 0.35.0 quirk"). |
| 3 | 346-442, 1401-1495 (Tracks 2-3) | New profile configs drop `key_env: LLM_KEY_HERMES`, `secrets.command`, and the `guard-render-queue.sh` pre-tool hook (`fail_closed: true`), and set `reasoning_effort: none`, which Hermes stores as null (default), not off. | Live `hosts/x3/live/hermes/config.yaml`; `records/UNI-APPLY-X3-E-HERMES/RESULT.md` (`false` is the documented off value). |
| 4 | 1121, 1385, 2185 | Secret scrubbing during export left literal `******` in shell scripts: `-H "Authorization: ******"` (always 401) and `grep -rnE "sk-...|******"` (bad regex). | The brief text itself. |

## Major

- **Redoes shipped code (Track 5).** `--prose-file`, `test_prose_file_gate.py`, and `wp_llm.py` sampler pass-through are
  already on mono (`render_writer_pipeline.py`, `test_prose_file_gate.py`, `wp_llm.py`). Only the optional
  image-before-text order in `build_request.py` is new; it is not needed for the goal.
- **Forks the render skills and adds prefill priming** (header-free `[Shot 1]` prose). That conflicts with the live
  4-header Beta 7 contract in `/home/evo/workspace/AGENTS.md` and `h3-writer` v2.0.0. Both workspaces share the live
  skills instead.
- **Track 1 splits the llama-swap source of truth** into a fragment file, drops `flash-next-uncensored-sub`, and raises
  `concurrencyLimit` from 4 to 6 on `--sessions 2`. Live is 4, proven 12/12 with no 429s (F4 section 1).
- **Its "Qwen" samplers are not the Qwen card's.** The render writer alias uses temp 0.75, top_k 40, min_p 0.05, rep
  1.03. The card has two presets only (research check 2026-11-20): thinking 1.0 / 0.95 / 20 / min_p 0 / presence 0, and
  instruct 0.7 / 0.8 / 20 / min_p 0 / presence 1.5.
- **Over-built:** about 35 files, 6 aliases, 12 wrapper scripts, 9 Curator-locked `0444` skills, `PROJECT_NOTES.md`.
  The live `h3-render` skill forbids inventing wrapper scripts.

## Minor

- Stale facts: ComfyUI `0.38.0` (live is 0.46.0), `pi-job` Swift "ESP off" (ESP is on, t2764u).
- Backs up `/etc/evo-x3/llama-swap.yaml` into the `evo`-owned `/home/evo/AI/_archive/`; the convention is
  `/etc/evo-x3/_archive/` (root).
- Issue numbers it cites (`gufo#388`, `gufo#957`, `hermes-agent #156360`, `#9635`) and `hermes curator lock` could not be
  checked here.

## What carries over into the replacement

- Two aliases on the resident slot via `setParamsByID` (now `flash-next-render` and `flash-next-code`, sampler only).
- A separate code profile with its own `terminal.cwd` and a short, scanner-safe `AGENTS.md`.
- Hermes memory caps (USER 1375, MEMORY 2200) stay as live.
- Derrick 2026-11-20 ~8:45 AM CT: Gemma is dropped and the X3 stays on Qwen Flash-Next. The replacement brief restores
  the Gemma pins and archives the hand-made `gemma` profile.
