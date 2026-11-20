# AGENTS.md — h3max-bridge (RV2, H5 harness)

Canonical package path: `x3/community/scripts/h3max_bridge/` (version 0.2.0).
Do not modify `build_request.py` from this package. Oral-speech, cast-count,
and lip-sync supplements live in `gates.py` and wrap official parody validators.

## Done gate (H5)
- `pi-job code` is **not DONE** until `make check-all` is green (lint + typecheck + tests).
- Never silence or weaken assertions to make a failing check pass; fix the root cause.
- Keep unit tests offline: mock `llama-swap` HTTP calls and `ffmpeg` subprocesses.
- Never commit secrets, tokens, `.env*`, or caches.
- Never print RefMod/LoRA triggers, adult prompt prose, or API keys.
- Strictly enforce `U56 Decision #1` via shared `scripts/parody/beta7_convert.py`: zero
  `integrated_multimodal_description:`, `overall_soundscape:`, or `non_diegetic_music:` headers.

## Commands
- `make lint` — `ruff check src tests`
- `make typecheck` — `ty check --extra-search-path src src tests`
- `make test` — `pytest`
- `make check-all` — runs all three in order
