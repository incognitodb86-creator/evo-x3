# Argon Medium final review (argon_medium_20261026) — M14 / M14c

Last Updated: 2026-10-26

## Date
2026-10-26, 11:20 CT. Written by Antigravity on Gemini 3.8 Flash High (CONTINUATION 2, following Argon Medium 9:46–10:49 CT exit 3 and Claude Opus 5.5 Medium 10:50–10:56 CT exit 3). Argon's unlogged 10:49 draft is archived as `final_review.argon_draft.20261026m-m14.archived.md` (sha256 `23F5F875CA9DECF3F091E30E099650B737AB33461F0A53B36E49EB898823597C`). M14c updates the review to reflect implementation of M2 (Derrick 10:57 AM CT "point it at llama swap"), M3b (Derrick 10:59 AM CT "ok do it"), and M15 pass-1 review.

GPU: **NVIDIA GeForce RTX 5070 Ti 16 GB** (`nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader` → `NVIDIA GeForce RTX 5070 Ti, 16303 MiB, 616.92`, run 10:53 CT).

## Summary
- Steps M0–M15 are complete (M0–M12 by Argon; M13 verified and closed by Opus; M14 scored by Opus; M2 implemented, M3b implemented, M15 reviewed, M14c updated by Flash High).
- Commits this run:
  - `community`: `15c7e44` (M1), `6358c39` (M13), `b0350ff` (M14)
  - `ralph-community`: `086f6ec` (M4), `9aee708` (M6), `e895778` (M8), `9af1ee9` (M13), `d02307f` (M13)
  - `director`: `5f94a9d` (M2-1), `2b2ed06` (M2-2), `6758533` (M2-3), `6b6ecbc` (M2-4)
- Out-of-git edits: `C:\Users\derek\.pi\agent\settings.json` (M3, M13, M3b; backups `.bak-20261026m-m3`, `.bak-20261026m-m13`, `.bak-20261026-m3b`).
- Youth guard intact: guard runs on every prompt string before any `/prompt` POST; 26/26 guard tests pass; `test_p6_review.py` hash unchanged (`C3C2E169…E213`). GI063 not rendered.
- FAIL rows (open work): llama-swap `-watch-config` mid-pass reloads, pi-mobile remote tailnet check, `ralph.log` NUL bytes, stale `ali05_loop_check.py` validator, `scene_card_gate.py` selftest, 15 s graph builders still on `res_multistep`, MAX block missing Oct 25 lines, unused face/identity custom nodes. (Note: `director.switchyard` import break and skill filter gaps were resolved in M2 and M3b, flipping to PASS).

## Key Findings

Source rule: official page or official repo only; if none was read, the column says UNVERIFIED and the row is not scored PASS on docs (internal policy rows cite the brief's HARD LIMIT instead of a URL). "Evidence" = a command run on 2026-10-26 during this run.

| Component | Check | Source link | PASS/FAIL | Note |
|---|---|---|---|---|
| GPU | Card name used everywhere | https://docs.nvidia.com/deploy/nvidia-smi/index.html | PASS | `nvidia-smi` → `NVIDIA GeForce RTX 5070 Ti, 16303 MiB`. Old "RTX 4080" text corrected in M1 (`15c7e44`). |
| Youth guard | `comm.guard_ok` runs on every prompt-bearing input before the `/prompt` POST | Internal: brief HARD LIMIT 2 | PASS | `run_graph_job.py:125-127` (all `comm.prompt_strings`, return 3) runs before `gpu_idle`/`gpu_lock`/`wake`/`static_check`; `comm.py:197,201` re-check before `comm.py:206` POST. `6358c39` only moved `static_check` (`run_graph_job.py:136-137`) inside `try:`; not weakened. |
| Youth guard | pytest + protected test hash | https://docs.pytest.org/en/stable/how-to/usage.html | PASS | `python -m pytest test_p6_review.py test_guard_scope.py -q` → `26 passed in 2.20s`; `test_p6_review.py` sha256 `C3C2E169…E213` = pre_hashes.txt. |
| Youth guard | Guard pins / comm.py lock | Internal: brief HARD LIMIT 2 | PASS | `rt_window_probe.py --check` → `RT_WINDOW_PROBE CLEAN checks=16`; `--selftest` → `SELFTEST_OK seeds=16 missed=[]`; `comm.py` sha256 `AB4217FE…F740` = pre_hashes.txt; `guard_pins.json` marker `not guard_ok(s)` (`d02307f`) matches `comm.py:197,201`. |
| Youth guard | No vision judge on rendered output; vision never decides identity/age; no real-person LoRAs | Internal: brief HARD LIMIT 2 | PASS | M10 read only ffprobe/blackdetect/freezedetect signals. `PROMPT.md:23` and `AGENTS.md:17` state adults-only/fictional/no real people. See custom-node row for installed identity nodes. |
| GI063 hold | No `runs\*gi063*` newer than 2026-10-25 11:28 AM | Internal: brief HARD LIMIT 6 | PASS | Newest = `runs\ali163_hc15_gi063_s51150032` 2026-10-25T11:28:36; count newer = 0; newest in ComfyUI `output` = 2026-10-24T23:12:31. |
| Protected files | test_p6_review.py, mcp.json, pi-permissions.jsonc unchanged | Internal: brief HARD LIMIT 3 | PASS | Hashes = pre_hashes.txt (see progress.md End of run, `post_hashes_flash.txt`). |
| pi | `defaultProvider`/`defaultModel` | https://github.com/earendil-works/pi (`docs/settings.md:13-14`, package 1.4.0) | PASS | `settings.json` valid (`python -m json.tool` rc 0); `defaultProvider=llama-swap`, `defaultModel=coding_swift15_iq3s` (M13). Undocumented legacy key `model` kept (read by `ali04_pi_probe.py`). |
| pi | Package skill filters | https://github.com/earendil-works/pi (`docs/packages.md:94-121`) | PASS | M3 + M3b: 17 skills disabled via documented package filter in `settings.json`; verified via `DefaultPackageManager.resolve()`: 17 disabled, 21 loaded. Backup: `settings.json.bak-20261026-m3b`. |
| pi | compaction / retry / httpIdleTimeoutMs | https://github.com/earendil-works/pi (`docs/settings.md`) | PASS | Values logged in M13; `retry.provider.maxRetries 0` per docs; `httpIdleTimeoutMs 1950000` > llama-swap comfy `unloadTimeout 1900` s. |
| pi | Probes after `9af1ee9` | https://github.com/earendil-works/pi | PASS | `ali04_pi_probe.py --selftest` → `17/17`; `--stock --no-pi` → `VERDICT stock: OK`; `ali20b_ext_probe.py` rc 0. |
| pi | Legacy `C:\AI\director\config\pi\settings.json` | https://github.com/earendil-works/pi | FAIL | Stale `defaultProvider "alienpc"` / `defaultModel "huihui-qwen3.8-27b-iq3xxs-mtp"`. Not loaded by ralph (runs from ralph-community); report only. |
| pi | pi-permission-system policy unchanged | https://github.com/MasuRii/pi-permission-system | PASS | sha256 `170AAE66…ADEB` = pre_hashes.txt; installed 0.8.0. |
| pi-mobile | Port 7878 owner, no EADDRINUSE | https://github.com/jkeskikangas/pi-mobile | PASS | `127.0.0.1:7878` owned by PID 21748 (`pi_mobile_hub.cjs`, task `\pi-mobile`); 0 `7878/EADDRINUSE` hits in `iter-*.log` (M5); extension dials first and only hosts on ECONNREFUSED (`src/link.ts:115-138`). Ownership choice is Derrick's. |
| pi-mobile | HTTPS from another tailnet device | https://github.com/jkeskikangas/pi-mobile | FAIL | Only ever curled from AlienPc itself (audit K-2/N2-10 part 3). Needs a test from phone/laptop. |
| llama-swap | Single exclusive group, no co-load | https://github.com/mostlygeek/llama-swap (`docs/config.example.yaml`) | PASS | One group `main`, `swap`/`exclusive` true; `RT_NO_CO_LOAD` OK in `rt_window_probe.py --check`. Live: `/health` 200 `OK`, `/running` `{"running":[]}`, `/v1/models` 200. |
| llama-swap | ComfyUI stop budget | https://github.com/mostlygeek/llama-swap/blob/main/docs/kb/guides/upstreams/comfyui.md | PASS | `comfyui_auto` `cmdStop` = `comfy_graceful_stop.ps1` (MaxWaitSec 1800), `unloadTimeout: 1900`, `ttl: 300` (`llama-swap.yaml:129-136`). |
| llama-swap | 128K on models that have it | https://github.com/mostlygeek/llama-swap | PASS | `coding_swift15_iq3s` and `_esp`: `--max-context 131072`. `coding_sc117_strata` = 98304 (96K): whether that model supports 128K is UNVERIFIED; unchanged. |
| llama-swap | Vision mmproj | https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md | PASS | `vl_judge` / `qwen3vl_judge` pass `--mmproj` (`llama-swap.yaml:115,124`). |
| llama-swap | `-watch-config` during passes | https://github.com/mostlygeek/llama-swap (README flag table `-watch-config`) | FAIL | `llama_swap_keepalive.ps1` runs with `-watch-config`; a YAML edit mid-pass reloaded and killed the running model (Oct 25 22:22, Oct 26 06:11, M13). Not edited; Derrick decides. |
| ComfyUI | Launch flags | https://github.com/Comfy-Org/ComfyUI (`comfy/cli_args.py`) | PASS | `--disable-async-offload --disable-pinned-memory`, no `--lowvram` (`llama-swap.yaml:132`); both flags exist in local `cli_args.py:179,205` (v0.38.0). |
| ComfyUI | Attention default | https://docs.comfy.org/tutorials/video/minimax/minimax-h3 | PASS | `comm.py:86,134` default `pytorch attention`. Official doc: Comfy Kitchen cannot run `int8_convrot`; this checkpoint is int8 `comfy_quant` without convrot, and M10 ran CK attention rc 0, 362 f, 600.3 s vs 780.3 s (pytorch). Default unchanged; card for Derrick. |
| ComfyUI | Sampler default = Euler (Derrick 6:48 PM Oct 25) | https://docs.comfy.org/tutorials/video/minimax/minimax-h3 | PASS | `comm.py:107` `euler`; 3 newest `p7\graphs` (Oct 25-26) use `euler`. Note: the official H3 templates use `res_multistep` + `simple`; Euler is Derrick's pick, not the doc default. |
| ComfyUI | All graph builders match Euler | https://docs.comfy.org/tutorials/video/minimax/minimax-h3 | FAIL | `notes\hc15_anchor_fix_build.py:255` and `hc15_anchor_carry_build.py:608` (15 s builders) still force/require `res_multistep`; `p7\graphs` = 11 euler / 11 res_multistep. Report only (M9); no change this run. |
| ComfyUI | GPU gate before any `/comfyui` call | https://github.com/mostlygeek/llama-swap/blob/main/docs/kb/guides/upstreams/comfyui.md | PASS | `6358c39`: `static_check` (`/object_info`) now after `gpu_idle`/`gpu_lock`/`wake`, inside `try` with `finally: gpu_unlock`. |
| ComfyUI | Custom nodes | https://docs.comfy.org/troubleshooting/custom-node-issues | FAIL | 46 node packs; face/identity packs installed but unused by `comm.py` graphs (`comfyui-reactor-node`, three PuLID packs, `ComfyUI-IPAdapter_plus`, `ComfyUI_FaceAnalysis`). Report only; archiving them is Derrick's call. |
| ralph loop | Timeout, circuit breaker, log isolation | https://github.com/frankbria/ralph-claude-code | PASS | `ralph.ps1:13` `IterationTimeoutSec = 7200` (M6); `-LogPath` isolation (M4); PSParser 0 errors; `ralph.ps1:158` logs pi rc; sandbox test `notes\ali05_loop_test.ps1` → `0 failing case(s) (15 sandbox runs, expected 15)`, exit 0 (stub pi, temp sandbox). |
| ralph loop | `ralph.log` NUL bytes (plan_v3 S12-1) | https://github.com/frankbria/ralph-claude-code | FAIL | `logs\ralph.log` 70,411 B, 343 NUL bytes (measured 10:54). S12-1 never run; open. |
| ralph loop | Validators agree with code | https://ghuntley.com/ralph/ | FAIL | `ali05_loop_check.py` → `VERDICT VIOLATIONS (11)` in `iter_log`, `pi_rc`, `plan_pin`, `rules_agree`, `rules_render`: stale regexes vs current `ralph.ps1`/root `AGENTS.md` pointer. Not in the active `ali11_run_checks.py` suite. Left for Forge. |
| ralph loop | AGENTS.md / PROMPT.md | https://ghuntley.com/ralph/ | PASS | `AGENTS.md` 39 lines (< 40 cap), `PROMPT.md` 25 lines; adults-only line present in both. M11 carry-over lines proposed, not applied. |
| Forge config | fix_plan.md shape, MAX block untouched | https://ghuntley.com/ralph/ | PASS | MAX prefix 1,044 chars identical to `ad0a2d4`; 63 `- [ ]` lines; `ali02_citation_check.py --plan` → `0 problems`. M8 (`e895778`) cleaned repeated IDs / duplicate E5. |
| Forge config | MAX block content | Internal: brief HARD LIMIT 13 | FAIL | `ad0a2d4` dropped Oct 25 lines still needed (GI063 row 21 reason + seed ban, GI046 orc feedback, Euler/5 s/350–500 word spec, ALI-7/ALI-102 go). Listed in M7 for Max. |
| Forge config | Scheduled tasks | Internal: brief "Forge during this run" | PASS | `ForgeRalphLoop Disabled IgnoreNew`; `pi-mobile Running IgnoreNew`; `Switchyard llama-swap Running IgnoreNew` (name is stale; report only). 0 ralph/pi processes; `C:\AI\locks` empty. |
| Forge config | `scene_card_gate.py --selftest` (2554abc) | UNVERIFIED | FAIL | Exits 1, `banned_outside_required_token wants F-BANNED got nothing`; cause in `_inside_required()` lines 186-190 (M13). Forge's draft; not fixed. |
| director | `director.switchyard` imports | https://github.com/mostlygeek/llama-swap | PASS | M2 implemented per Derrick's 10:57 AM CT go (commits `5f94a9d`, `2b2ed06`, `6758533`, `6b6ecbc`): standalone `jobstore.py` added; `queue.py`, `runner.py`, `cli.py`, `config.py`, `gateway.py` repointed off switchyard; retired commands fail loudly with clear message. `import director.cli` PASS (rc 0); `import director.discord_bridge` PASS (rc 0); `/queue` command path verified. |
| Forge pass-1 | Interrupted pass-1 (CARD-VL2) review | Internal: brief M15 | PASS | Reviewed uncommitted pass-1 files in community notes: 7/7 `.py` compile cleanly, 4/4 JSON valid, raw captions intact. Kept for Forge; `agy_monitor.out.txt` reverted. GI063 render hold untouched. Director older files reported. |

### M0–M15 results

| Step | Result | Commit |
|---|---|---|
| M0 | Pre-flight: 11/11 hashes matched, Forge stopped, locks empty, RTX 5070 Ti confirmed | — |
| M1 | Errata sections added to prior final_review.md / ab_test_res_vs_euler.md | community `15c7e44` |
| M2 | Repoint director off switchyard to llama-swap + ComfyUI queue (DECIDED by Derrick) | director `5f94a9d`, `2b2ed06`, `6758533`, `6b6ecbc` |
| M3 | 5 broken skill filters fixed via package filter in settings.json | out of git (`settings.json.bak-20261026m-m3`) |
| M3b | 12 additional skills disabled per Derrick; 17 disabled / 21 loaded verified | out of git (`settings.json.bak-20261026-m3b`) |
| M4 | `-LogPath` isolation for `-CommandOverride`; S12-1 open | ralph-community `086f6ec` |
| M5 | pi-mobile 7878: no conflict seen; owner choice + remote test (NEEDS DERRICK) | — |
| M6 | IterationTimeoutSec 4500 → 7200 from renders-per-pass data | ralph-community `9aee708` |
| M7 | Dropped Oct 25 MAX lines listed for Max | — |
| M8 | Repeated IDs / duplicate E5 cleaned, open count unchanged | ralph-community `e895778` |
| M9 | comm.py = euler; 15 s builders res_multistep; A/B confound explained | — |
| M10 | CK attention test: 600.3 s vs 780.3 s, rc 0, default unchanged | — (runs/ only) |
| M11 | forgesafe carry-over lines proposed | — |
| M12 | plan_v3 vs audit matrix; 9 gaps confirmed | — |
| M13 | pi defaultModel, probe fixes, static_check order, guard pin; verified 10:52 | ralph-community `9af1ee9`, `d02307f`; community `6358c39`; settings.json `.bak-20261026m-m13` |
| M14 | Final review written and verified | community `b0350ff` |
| M14c | Review updated for M2 implementation, M3b skill disables, M15 pass-1 | this commit |
| M15 | Interrupted pass-1 CARD-VL2 files reviewed (kept for Forge; `agy_monitor.out.txt` reverted) | — |

## Action Items

### Decisions Derrick still owes (from the brief; not decided here)
1. **Sampler:** Euler (current `comm.py` default, your 6:48 PM Oct 25 pick) or `res_multistep` (official H3 template default; still used by the 15 s builders) — M9.
2. **GI063 render go** (needs_derrick.md row 34a; row 21 consent question from Oct 25). [RELEASED: Derrick 2026-10-27 9:09 AM CT — wrongly flagged by wrong model; youth guard kept on GI063].
3. **Forge paused or running** after this run (now paused: `\ForgeRalphLoop` Disabled).
4. **pi-mobile:** who owns port 7878 (hub task vs pi extension), QR pairing, and a test from another tailnet device (M5).

*(Note: Prior Decisions 2 [director.switchyard] and 5 [pi skills to disable] were DECIDED by Derrick at 10:57 and 10:59 AM CT and implemented in M2 and M3b).*

Also pending: Comfy Kitchen attention card (M10: 23% faster on the same seed; default stays pytorch attention until you say); budget caps question (audit A-6, `p7_budget.json` warn-only); `-watch-config` on or off during passes (M13); archive unused face/identity custom nodes or not; `coding_sc117_strata` context (96K now; 128K support unverified).

### For Max / Forge (no Derrick decision needed)
- Max: restore the dropped Oct 25 lines below the MAX block (M7); update pack line `production-defaults-st8-dynamic-vram.md:15` (ck-attention KEEP superseded, audit R2-7 #6).
- Forge: run S12-1 (copy `ralph.log`, strip NUL); update stale `ali05_loop_check.py` regexes; fix `scene_card_gate.py` selftest; finish CARD-VL2 pass-1 files per M15.
