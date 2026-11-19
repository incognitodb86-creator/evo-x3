# Phase 3 Result (`P3.1` Gufo Cutover) — 2026-11-18 CST

- **Plan:** [`PLAN-v3.2.md`](file:///home/derekboone/AI/agy-runs/plan-v32-20261118/PLAN-v3.2.md) Phase 3 (`P3.1`, pre-approved by Derrick at 3:49 PM CT and confirmed at 6:05 PM CT)
- **Status:** **PASS** (Phase 4 not started; Phase 5 remains on **HOLD**; no deletes)

## Changes Applied
- **Resident slot (`flash-next-uncensored-v2`):** Cut over `/etc/evo-x3/llama-swap.yaml` from Halogen `0.20.7` (Huihui v2 HGN) to **Gufo `0.35.0`** (`ghcr.io/gufo-org/toolboxes/gufo-runtime@sha256:99e9b5471b7a9b007c686c2aa795afaf966744d64e753cb009c89541f9e9c2b6`) with:
  - Model: `/srv/bakeoff/Huihui-Qwen3.8-Flash-Next-abliterated-v2-GGUF@cbc7fba/Qwen3.8-Flash-Next-UD-Q4_K_XL-00001-of-00004.gguf`
  - Vision: `--mmproj /srv/bakeoff/Huihui-Qwen3.8-Flash-Next-abliterated-v2-GGUF@cbc7fba/mmproj-Qwen3.8-Flash-Next-BF16.gguf`
  - Speculative: `--mtp-model /srv/models/flash-next/mtp-Qwen3.8-Flash-Next-shared-Q8_0.gguf --speculative mtp`
  - Identity/pins/pool: `--served-model-name flash-next-uncensored-v2 --sessions 2 --context 131072 --preserve-thinking on --reasoning-effort medium --reasoning-budget 8192 --cache-ram-bytes 2147483648 --max-pending 16 --temperature 1.0 --top-p 0.95 --top-k 20 --stall-timeout-ms 120000 --log-progress`
  - Kept slot ID (`flash-next-uncensored-v2`), `-sub` settings, `useModelName`, preload hook, and `halogen-only` pins unchanged.
- **Candidate & Rollback files:**
  - Candidate: [`llama-swap.yaml.p31-gufo-resident`](llama-swap.yaml.p31-gufo-resident)
  - Rollback (Halogen v2 kept): [`llama-swap.yaml.halogen-v2-rollback`](llama-swap.yaml.halogen-v2-rollback) + `/etc/evo-x3/_archive/llama-swap.yaml.pre-p31-20261118-180547` + `/etc/evo-x3/_archive/llama-swap.yaml.bak-20261118-180605`
- **Apply & `/etc` commit:**
  - Applied via [`apply-llama-swap.sh`](../../scripts/apply-llama-swap.sh) (`config is valid: 7 model(s), 0 peer(s)`).
  - Committed `/etc` with `sudo etckeeper commit` (`master 47a54bd`).

## Verification Results

| Check | Result | Details |
|---|---|---|
| `verify-serve.sh` | **PASS** | `no key: 401`, `LLM_KEY_BOX: 200` |
| `llama-swap.service` | **PASS** | `ActiveState=active`, `SubState=running`, `NRestarts=0` |
| C2 (Parallel 4x100K) | **PASS (`4/4`)** | `total_wall_s: 118.01` (`75,039` prompt tokens each; `100000`, `107919`, `115838`, `123757` exact matches); [`p31-gufo-resident/summary.json`](p31-gufo-resident/summary.json) |
| C3 (Refusal probes) | **PASS (`3/3`)** | `benign_sysadmin`, `explicit_adult`, `adult_fiction` all `comply` (`refuse: false`); [`p31-gufo-resident/c3_refusal.json`](p31-gufo-resident/c3_refusal.json) |
| `gemma4-heretic` pin | **PASS** | HTTP `200`, answered `HERETIC_PIN_OK`; `/running` afterwards showed only `[('flash-next-uncensored-v2', 'ready')]` (no model load) |
| `Forge-X3` (`w4`) | **PASS** | One-shot `forge-pi.sh -p --no-session --thinking low` answered `Forge-X3 on evo-x3 — P31_FORGE_OK` |
| `Render-X3` (`w3`) | **PASS** | One-shot `render-pi.sh -p --no-session --thinking low` answered `Agent: Render-X3 / Host: evo-x3 / P31_RENDER_OK` |
| AlienPC panes | **Not run from X3** | AlienPC Forge SSH is not approved; AlienPC panes share the same `gemma4-heretic` / `flash-next` pins verified above |
