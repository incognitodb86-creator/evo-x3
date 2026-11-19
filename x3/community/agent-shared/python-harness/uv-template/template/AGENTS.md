# AGENTS.md — {{ cookiecutter.project_name }}

## Done gate (H5)
- `pi-job code` is **not DONE** until `make check-all` is green (lint + typecheck + tests).
- Never silence or weaken assertions to make a failing check pass; fix the root cause.
- Keep unit tests offline: mock HTTP, `llama-swap`, `ffmpeg`, and remote hosts.
- Never commit secrets, tokens, `.env*`, or test caches.

## Commands
- `make lint` — `ruff check src tests`
- `make typecheck` — `ty check src tests`
- `make test` — `pytest`
- `make check-all` — runs all three in order
