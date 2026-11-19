# U1b upgrades - DONE note (2026-10-29, MAX block item 2)

Installs: **Max2** (his `notes/actions.log` lines 09:30-09:45 CT).
Close-out + measurement: **Pi**, 09:5x CT. **No GPU, no render, no model load, no install, no restart by me.**
MAX block says **stop after U1b** - U2-U5 not started.

## Verdict

`C:/AI/community/notes/u1b_done_check.py` -> **exit 0, ALL CLAUSES PASS (22/22)**, read-only against this disk and
the live process table. (Run: `C:/AI/director/.venv/Scripts/python.exe C:/AI/community/notes/u1b_done_check.py`)

| clause | measured |
|---|---|
| strata_0.2.7_tree | `sy_strata_launch.py`, both swift15 configs, `.venv\Scripts\python.exe` present in `C:\AI\strata-0.2.7` |
| revert_path_kept | `C:\AI\strata-0.2.2`, `C:\AI\strata-engine-022`, the 0.2.2 esp config all present |
| engine_0.1.52_cuda13 | `C:\AI\strata-engine-027\engine\0.1.52-windows-x86_64-cuda-cuda13\strata.exe` 272,727,040 B + `strata-vision.exe` |
| llama_swap_v268_binary | `--version` = `v268 (2576af3), built at 2026-10-28T03:26:39Z` |
| llama_swap_v268_live | `127.0.0.1:8080/api/version` = `{"build_date":"2026-10-28T03:26:39Z","commit":"2576af3","version":"v268"}` |
| lswap_v266_backup | `bin\llama-swap.exe.bak-v266-20261029` 42,984,960 B |
| yaml_uses_027_both_slots | 2 strata launch cmd lines, both `strata-0.2.7`; **0** refs to `strata-0.2.2` in the live yaml |
| yaml_backup | `llama-swap.yaml.bak-20261029-0932-max2-strata` 10,140 B, 6 old-tree refs inside |
| esp_flags_kept | none missing: `--expert-profile --expert-cache --control-vector-scaled --control-vector-layer-range --cvec-mode --cvec-dir --max-context` |
| esp_data_files_present | `expert-profile.bin` 196,632 B and the experimental-speed-projection gguf 483,520 B exist in the 0.2.7 tree, **same sizes as in 0.2.2** |
| max_context_262144 | cfg `--max-context 262144` |
| esp_cfg_path_only_diff | 0.2.7 esp config == 0.2.2 esp config once only the `0.2.7/0.2.2` and `0.1.52/0.1.47` path strings are masked (both mask to 3,064 chars) -> **no flag, model or dial drift** |
| live_engine_is_0152_esp | pid 32144 = engine 0.1.52 + `--expert-profile` + `--max-context 262144`; **0** processes on the old engine |
| live_llama_swap | pid 16880, image = the installed v268 bin, args from the standing launcher |
| pi_installed_equals_latest | installed `pi --version` = 1.4.0, `npm view @earendil-works/pi-coding-agent version` = 1.4.0, fetched manifest `C:\AI\bench\pi_npm.json` version = 1.4.0 -> **no pi upgrade exists** |
| models_json_esp_context_257000 | `coding_swift15_iq3s_esp` contextWindow **257000**, maxTokens 32768 |
| defaults_still_esp | `settings.json defaultModel = coding_swift15_iq3s_esp` |
| pi_config_backups | `models.json.bak-20261029-max2` + `C:\Users\derek\.pi\agent.bak-20261029-max2` |
| strata_cfg_backup | `C:\AI\strata-0.2.2\strata-swift15-iq3s-esp.json.bak-20261029-0932` 3,203 B |
| ceiling_261k_served_on_new_engine | 261,264-token prompt served by engine 0.1.52 at 2,991.7 tok/s prefill |
| pi_docs_document_u3_behaviour | `cli.md` sha8 `c45e59f3`, `configuration.md` sha8 `fc48d1ce`; all three U3 behaviours documented |
| gpu_idle_now | `gpu_guard.ps1` = **IDLE** |

## Latest = verified at each release source (the plan's hints were checked, not trusted)

- **Strata**: `api.github.com/repos/Niko1221/Strata/releases/latest` = **v0.2.7** (published 2026-10-27T14:54:42Z)
  = what is installed. The plan's hint "0.2.7.1" is a **git tag with no release object**: `GET
  /releases/tags/v0.2.7.1` = 404, and the full releases list tops out at v0.2.7. So v0.2.7 *is* the latest
  published release; 0.2.7.1 is not installable from the release feed.
- **llama-swap**: `repos/mostlygeek/llama-swap/releases/latest` = **v268** (2026-10-28T03:32:27Z) = installed
  (binary self-reports v268 / 2576af3).
- **pi**: `npm view @earendil-works/pi-coding-agent version` = **1.4.0** = installed 1.4.0 -> no install, no restart.

## Config carry-over (proved, not asserted)

- `C:\AI\director\config\llama-swap.yaml` diff vs its 09:32 backup = **exactly the 2 swift15 `cmd:` lines**
  (0.2.2 -> 0.2.7) + a BOM on line 1. Nothing else changed.
- `strata-swift15-iq3s-esp.json` in 0.2.7 is byte-identical to the 0.2.2 file after masking only the version-path
  strings -> ESP profile path, control-vector path, `--cvec-mode project`, `--cvec-dir per-layer`,
  `--control-vector-layer-range 4 44`, `--kv int8`, `--kv-resident 32768`, `--pool-workers 13`,
  `--vram-reserve-mib 1100`, `--pcie-frac 0.35`, `--adapt-*` and the Swift 1.5 IQ3_S model file all carried over.
- The live engine process shows those flags on the command line, and the ESP features are active in the served log
  (decode expert-cache hit rate 79-83 %, route-tail-skip, KV streaming 99.7 % VRAM hits) -> **ESP is on**.

## Measured ceiling and tok/s on coding_swift15_iq3s_esp

From `C:\AI\strata-0.2.7\strata-swift15-iq3s-esp.log`, compared with `C:\AI\strata-0.2.2\...-esp.log`
by `C:/AI/community/notes/u1b_log_compare.py`:

| | 0.2.2 engine 0.1.47 | 0.2.7 engine 0.1.52 |
|---|---|---|
| served prompts in log | 1,271 (multi-day) | 43 (~19 min) |
| max prompt accepted | 249,936 tokens | **261,264 tokens** (2,991.7 tok/s prefill) |
| decode tok/s | median 103.1 / p90 118.5 / max 158.4 | median 104.6 / p90 117.8 / max 130.4 |
| prefill tok/s | median 411.1 / p90 2,843.5 / max 3,314.3 | median 407.4 / p90 2,626.3 / max 3,059.3 |
| vision "no CUDA" + "on the CPU" lines | 42 | 2 (same shape, pre-existing) |
| low-VRAM warnings | 55 | 2 (pre-existing class) |

Reading: **decode is unchanged** (medians/p90 overlap), the **ceiling moved up** (261,264 > the 249,936 that is the
most the 0.2.2 log ever served), and the lower prefill p90/max on the new side is a **43-sample vs 1,271-sample
max-of-different-samples** effect - *not* a measured slowdown, and no fair head-to-head throughput claim is made
(a warm-first matrix A/B was not asked for by U1b and was not run).
`models.json` `_esp` contextWindow **257,000** sits under the 261,264 acceptance -> conservative, as U1b asks.
Max's "262,635 refused" is **his** measurement; I did not reproduce a refusal, so it is not re-claimed here.

## pi docs clause (U3 assumptions)

No pi upgrade exists (1.4.0 = npm latest), so the docs are the unchanged bytes the plan was written against:
`cli.md` sha8 `c45e59f3`, `configuration.md` sha8 `fc48d1ce`. The three behaviours U3 relies on are documented in
the installed 1.4.0: `--append-system-prompt` (cli.md:224,231), skills discovery + `-ns/--no-skills`
(cli.md:202-203), `AGENTS.md` / `<agent-dir>/skills/` discovery (configuration.md:18,22). **U3's assumptions are
unaffected by U1b.**

## Live smoke

This close-out pass itself ran through the upgraded stack: `PI_PROVIDER=llama-swap`,
`PI_MODEL=coding_swift15_iq3s_esp`, served by llama-swap **v268** + Strata engine **0.1.52**. Max's own esp smoke
(09:33-09:36 CT: load 49 s, coherent reply, tool_call ok, 5 slots, esp ok via v268) is his line in actions.log.

## Revert path (all present)

`llama-swap.yaml.bak-20261029-0932-max2-strata` (restore yaml = revert strata),
`C:\AI\strata-0.2.2\strata-swift15-iq3s-esp.json.bak-20261029-0932`,
`bin\llama-swap.exe.bak-v266-20261029`, `models.json.bak-20261029-max2`,
`C:\Users\derek\.pi\agent.bak-20261029-max2`, plus the whole 0.2.2 tree + `strata-engine-022` kept untouched.

## Cosmetic, left for Max (I changed nothing)

1. `llama-swap.yaml:2` header comment still says *"Supervisor for Strata 0.2.1.1"* - stale, and the same text is in
   the pre-upgrade backup, so it predates U1b.
2. `bin\CHANGELOG.md` is topped at v266 while the binary is v268: the v268 install replaced only `llama-swap.exe`.
3. `strata-vision` runs on CPU (no CUDA device visible to it) - pre-existing in the 0.2.2 log, not a 0.2.7 change.

## Stop

MAX block: **"Stop after U1b."** No U2-U5 work started. fix_plan.md item 2 ticked `[x]` with the evidence inline
via `notes/u1b_closeout_record.py` (line-preserving CRLF edit, backup `fix_plan.md.bak-20261029-u1b-tick`).
gpu_guard IDLE before and after; nothing rendered.
