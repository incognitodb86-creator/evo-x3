# PLAN-v3.2 Phase 0 Result (P0.0 Complete; Derrick Y Recorded; P0.1–P0.4 Held While Render Busy)

- **Date:** 2026-11-18 14:30 CST
- **Branch / Base commit:** `evo-x3` branch `u58` (`834356f`)
- **X3 Lease (`/home/derekboone/AI/locks/x3-lease.txt`):** `0` bytes (no lease taken; read-only prep only)
- **Status:** `P0.0` **PASS**; Derrick's `t2462s8784` **Y** approvals recorded; **HOLD active (2:23 PM / 2:26 PM CT)** while Render (`w3:p1`) is busy — zero benchmarks (`C1`–`C6`), zero `llama-swap` restarts, zero model loads/unloads, zero container pulls, and zero package installs executed.

---

## 1. Derrick Approvals Recorded (`t2462s8784`, 2:20 PM CT)

| Gate | Answer | Notes |
|---|---|---|
| **Q1 (`P0.1 Y` & `P0.2 Y`)** | **YES** | Run C2–C6 on the live `flash-next-uncensored-v2` slot and clone `deepu105/quant-bench` for C5. |
| **Q2 (`P0.3 Y`)** | **YES** | Run `P0.3` (`gufo 0.35.0` image pull, `907 MB` `mmproj-Qwen3.8-Flash-Next-BF16.gguf` download, temporary slot swap for C1–C6), then restore Halogen v2 HGN and verify it serves; take the X3 lease line for the swap and clear it after restore. |
| **Q3 (`P0.4 Y`)** | **YES** | Run `P0.4` memory check and reserve **`2.5 GB`** for `P4.10` NPU models (no TTS). |
| **AlienPc Forge SSH** | **NOT APPROVED** | Leave `forge_alienpc` as is. |

### Active HOLD (2:23 PM CT & 2:26 PM CT)
- Render (`w3:p1`) is actively working for Derrick (`herdr pane list` shows `w3:p1` `agent_status: "working"`, writing a 60s continuation batch).
- Per HOLD: no benchmarks (`C1`–`C6`), no `P0.3` slot swap, no `llama-swap` restart, no `apply-llama-swap.sh` live run, and no model load/unload until Max confirms Render is idle. Zero requests were sent to `127.0.0.1:8080` or `127.0.0.1:8081`.

---

## 2. Read-Only Prep Completed Under HOLD

1. **C5 (`deepu105/quant-bench`) cloned and prepped (zero LLM calls):**
   - Cloned `https://github.com/deepu105/quant-bench` -> `/home/derekboone/evo-x3/bench/quant-bench`.
   - Executed `python3 /home/derekboone/evo-x3/bench/quant-bench/quant_bench.py prep --agent --data /home/derekboone/.cache/quant-bench`:
     - `math.jsonl` (3 problems), `lcb.jsonl` (`arc196_c`, `arc196_a`, `arc196_d`), `speed-corpus.jsonl` (172 statements), and `polyglot-benchmark` cloned to `/home/derekboone/.cache/quant-bench/polyglot-benchmark`.
   - Wrote `/home/derekboone/evo-x3/records/plan-v32/quant-bench-c5.toml` (`sets = ["agent"]`, `runs = 1`, `host = "127.0.0.1"`, `port = 8081`, `ctx = 131072`, `served_name = "flash-next-uncensored-v2"`, `timeout_s = 300`, dummy `[engines.live]` `cmd = "sleep 86400"`).
   - Verified `python3 /home/derekboone/evo-x3/bench/quant-bench/quant_bench.py run /home/derekboone/evo-x3/records/plan-v32/quant-bench-c5.toml --dry-run` -> `=== live/resident / sleep 86400` (exit `0`).
   - **C5 compiler preflight (read-only check):** `cmake` (`4.3.0`) and `g++` (`16.2.1`) are installed and the 3 C++ tasks bundle `test/catch.hpp`. All 4 Rust tasks (`Cargo.toml`) and 4 Go tasks (`go.mod`) have zero external crate/module dependencies, **but** `cargo`/`rust` (`~40 MB` dnf) and `golang` (`~1.5 MB` dnf) are not currently installed on the host. No packages installed under HOLD; will note/confirm once HOLD lifts.

2. **Staged C2 / C3 / C4 / C6 Benchmark Harness:**
   - Wrote `/home/derekboone/evo-x3/records/plan-v32/run_c2_c4_c6.py` (`0755`):
     - **C2:** concurrent `/v1/chat/completions` needle tests (`--c2-jobs`).
     - **C3:** runs `/home/derekboone/evo-x3/bakeoff/u26/refusal_key.py` via `--key-stdin`.
     - **C4:** 3-trial 3-step tool chain checking distinct non-empty `tool_call.id`s (gufo #780), plus 2 requests with `tool_choice: "none"` checking no tool calls and no leaked XML/JSON tool text (gufo #1232).
     - **C6:** runs `/home/derekboone/evo-x3/bakeoff/bench/vision_bench.py` against `http://127.0.0.1:8081` with `vision-test.png`.
   - Verified `python3 -m py_compile /home/derekboone/evo-x3/records/plan-v32/run_c2_c4_c6.py` -> exit `0`.

3. **Staged P0.3 Candidate `llama-swap.yaml` Files (Not Applied):**
   - Verified GHCR `ghcr.io/gufo-org/toolboxes/gufo-runtime:0.35.0` digest via `skopeo inspect`:
     - `sha256:99e9b5471b7a9b007c686c2aa795afaf966744d64e753cb009c89541f9e9c2b6` (`org.opencontainers.image.version: 0.35.0`, created `2026-11-17T08:40:40Z`).
   - Verified Hugging Face `huihui-ai/Huihui-Qwen3.8-Flash-Next-abliterated-v2-GGUF` vision file:
     - `mmproj-Qwen3.8-Flash-Next-BF16.gguf` (`907,543,008` bytes, `sha256: b1a82259702816a5330d7bd7607cd9676b11780e79ff7348c21103ff3ce49bd0`).
   - Wrote `/home/derekboone/evo-x3/records/plan-v32/llama-swap.yaml.p03-gufo-v2` (with `--mtp-model ... --speculative mtp`) and `/home/derekboone/evo-x3/records/plan-v32/llama-swap.yaml.p03-gufo-v2-nospec` (`--speculative off`), updating only `flash-next-uncensored-v2`'s `cmd` and matching `useModelName: "flash-next-uncensored-v2"` via `--served-model-name flash-next-uncensored-v2`.
   - Verified both with `/home/derekboone/evo-x3/scripts/apply-llama-swap.sh --validate-only` -> exit `0`, `YAML and unique-alias check passed. Preload models: flash-next-uncensored-v2`, `config is valid: 7 model(s), 0 peer(s)`.

---

## 3. P0.0 Snapshot Summary (Baseline Before HOLD)

- `llama-swap.service`: `active (running)` since `2026-11-18 13:49:44 CST`, serving `flash-next-uncensored-v2` on Halogen `0.20.7` (`vision.enabled: true`, 4 slots, 524,288 KV pool, MTP drafter loaded).
- `verify-serve.sh`: `no key: 401`, `LLM_KEY_BOX: 200`. Live `/etc/evo-x3/llama-swap.yaml` matches `config/llama-swap.yaml` (`sha256: b11edc691be44ef0137a144ef4b5cd9710ee771a3f9ddbb7d991fffb69840e85`).
- `MemAvailable: 23398000 kB` (~22.3 GiB), `Mlocked: 66001200 kB`, GTT used `29824745472` (~27.78 GiB / 120 GiB), `/` free `600G`.
- `u42-pixlstash-tagger.service` and `.timer`: `inactive`.
- Earlier AlienPC render `c6c416c5` completed at `14:01:09-06:00` (`DONE pos=1 tag=clip ok ... bytes=2527471`, `gpu_lock release rc=0`).
- Phase 1 read-only audit notes (ready for when Phase 1 runs):
  - `B3` / `P1.2`: `remote_comfy.py` uses `fcntl.flock(..., LOCK_EX | LOCK_NB)`.
  - `I3` / `P1.4`: `community/scripts/tests/test_p6_review.py` (6 ffmpeg `subprocess.Popen` errors when run alongside `parody/test_c2v_context.py`'s `sys.addaudithook`) was observed in `U56-render-writer-fixes/baseline-community.txt`.
  - `P1.10`: `models.json` and `config/pi-evo/models.json.example` still use `contextWindow: 262144` on resident-slot entries instead of `131072`.
