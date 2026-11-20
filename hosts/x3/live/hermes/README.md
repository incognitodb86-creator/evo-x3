# X3 Hermes live snapshot (for Opus review)

Read-only copy from the X3 Hermes home `/home/evo/.hermes` (user `evo`, Hermes Agent v0.23.3). Default profile and skills from `scripts/snapshot-live-setup.sh` (2026-11-20 07:52 CT). Profiles and workspace file added 2026-11-20 ~8:10 AM CT over `ssh evo-x3-1` (`sudo -n -u evo cat`, no lease, no live changes). Key-like values go through the same scrub as the snapshot script; none were found. Configs read keys at runtime from owner-only files (`secrets.command`, `key_env: LLM_KEY_HERMES`).

## Included
- `config.yaml`, `SOUL.md`: the **default** profile. This is the RENDER workspace (`flash-next-uncensored-v2`, memory on, `terminal.cwd=/home/evo/workspace`).
- `workspace/AGENTS.md`: the render workspace instruction file Hermes loads from `/home/evo/workspace`.
- `profiles/writertest/`: `config.yaml`, `SOUL.md`, `profile.yaml`, `skills-list.txt`. Writer dry-run tests with memory off (`fb35316c`).
- `profiles/gemma/`: the same four files. **Flag: this profile was hand-made by Max, cloned from the render default. It is wrong and pending Derrick.** It differs from the default only in its model (`gemma4-heretic`), memory off, and the gateway/API-server lines. It shares the render workspace `cwd` and `AGENTS.md`, the render SOUL and the same skills. Derrick wants the Gemma workspace set up by a job sent through a Hermes chat to pi (which chat to use is waiting on him). See `records/UNI-OPUS-HERMES-WORKSPACES/BRIEF.md`.
- **Profile update 2026-11-20 ~2:40 PM CT (Opus, from Max's notes and the U59 RESULT; not a fresh copy):**
  - default (Render): model `flash-next-render` since H7 (U59, 11:13 AM CT); the `flash-next-uncensored-v2` above is the 8:10 AM copy. Fully local. Config sha256 `526812b3…` per Max, 2:15 PM CT.
  - `code`: added by H7 (`flash-next-code`, thinking medium, render skills disabled; `profiles/code/` in this folder).
  - `gemma`: archived by H7 (U59). The copy above is history.
  - `grok` (new 2026-11-20, wrapper `/home/evo/.local/bin/grok`): cloned from default with shared logins. `model.provider: xai-oauth`, `grok-4.6`, `base_url https://api.x.ai/v1`. `image_gen` / `video_gen` on with xAI (`grok-imagine-image` / `grok-imagine-video`). Backup `profiles/grok/config.yaml.bak-20261120-1415CT`. Two `xai-oauth` credentials are linked; both return `403 personal-team-blocked:spending-limit` (likely out of credits; retest after the reset). Its files are not copied here yet. The next snapshot should copy `config.yaml`, `profile.yaml` and `SOUL.md` redacted, never `auth.json`. See `records/opus/NEXT-STEPS.md` section 15.
- `profiles/default-skills-list.txt`: `SKILL.md` paths in the default profile. All three profiles have the same list.
- `skills/`, `hermes-agent-version.txt`, `memories-listing.txt` (a directory listing only), `gitignore`: from the snapshot script.
- Related: `../llama-swap/llama-swap.yaml` (live router, redacted), `../hermes-webui/`, and repo copies in `hosts/x3/hermes/` (agent hooks, morning digest, build scripts).

## Excluded
`.env`, `auth.*`, `install_id`, `log_hash_salt`, every `*.db` (state, sessions, response store, kanban, projects), `sessions/`, memories content, `logs/`, `cache/`, `image_cache/`, `audio_cache/`, `pairing/`, `pending*`, `gateway*` runtime files, `spawn-ledger.json`, `.skills_prompt_snapshot.json`, `_archive/`, `backups/`, the nightly `.git` history, and the bundled `hermes-agent/` source.
