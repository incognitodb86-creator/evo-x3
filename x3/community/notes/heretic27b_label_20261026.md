# HERETIC-LABEL - the coding_heretic27b mislabel, fixed and measured (2026-10-26)

Derrick's pick 4 of six (MAX block `C:/Users/derek/5slock/ralph-community/fix_plan.md:18`, 2026-10-25
6:48 PM CT, verbatim): **"Fix the coding_heretic27b mislabel"**. The same line's audit context (Max's 6:47 PM
read-only audit) records **"coding_heretic27b aliases coding_sc117_strata"** and **"RVN 27B llama-server PID
3848 on :8090 outside llama-swap"**, and his pick 5 on that line is **"Look into the 27B server on port
8090"**. No plan row carried pick 4, so this item added its own row.

## What the mislabel was

`C:/AI/director/config/llama-swap.yaml` defined the upstream `coding_sc117_strata`, which serves
`C:/AI/Strata-data/models/qwen38-flash-next-iq3s/IQ3_S/Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00001-of-00002.gguf`
(a Qwen3.8-Flash-Next IQ3_S model), and gave it four aliases. Three of them named a model that file is
not:

| alias | what the name claims | what a request naming it was served |
|---|---|---|
| `coding_heretic27b` | family `heretic`, size `27b` | Qwen3.8-Flash-Next **IQ3_S**, no Heretic, not a 27B |
| `coding_huihui27b` | family `huihui`, size `27b` | same; and **no Huihui GGUF exists on this box at all** |
| `qwen3.8-flash-next-iq3_xxs` | quant `iq3_xxs` | the **IQ3_S** file |
| `strata` | the engine the cmd launches (`C:/AI/strata-0.2.2`) | matches, kept |

llama-swap's README (saved body `C:/AI/community/notes/web/01r_llamaswap_readme.txt:320`) documents
`aliases` as the way "to use familiar model names", and `:345` that a request's `model` value selects
the upstream that serves it - so a name is a route, and a false familiar name is a **silent
substitution**. It is invisible on the surface too: measured `GET http://127.0.0.1:8080/v1/models`
advertises only the 5 model ids
(`coding_sc117_strata, coding_swift15_iq3s, coding_swift15_iq3s_esp, qwen3vl_judge, vl_judge`)
and never an alias.

## The gate (built first, and it saw the fault before I touched anything)

`C:/AI/community/notes/heretic_label_check.py` (schema `heretic-label-1`, PyYAML is importable in the
default `python` - measured 6.0.3). Rule, a rule and not a ban: **every model-family / quant / size
word in a model id or alias must be backed by the file that upstream serves.** An id's claims are
checked against the served file (self-support is vacuous); an alias may also inherit the id's own
honest label (that is why `strata` is fine). Words outside the published lexicons (`sc117`, `esp`,
`judge`, `coding`, `auto`, `vision_9b`'s "vision") name nothing, so they never fire.

Commands and measured output:

```
python C:/AI/community/notes/heretic_label_check.py --check     # BEFORE the edit: 5 findings, VERDICT NAME_CHECK NOT_CLEAN (rc 1)
python C:/AI/community/notes/heretic_label_check.py --selftest  # BEFORE: 14 seeds fired, 0 silent, and NOT_CLEAN because the REAL config is the fault
python C:/AI/community/notes/heretic_label_check.py --check     # AFTER : findings=0, names_audited=11, VERDICT NAME_CHECK CLEAN (rc 0)
python C:/AI/community/notes/heretic_label_check.py --selftest  # AFTER : VERDICT SELFTEST_CLEAN - 16 seeds fire, 0 silent, 0 control violations, 13 unit rows 0 faults
python C:/AI/community/notes/heretic_label_check.py --live --probe-model coding_heretic27b       # 404 -> VERDICT LIVE_PROBE CLEAN
python C:/AI/community/notes/heretic_label_check.py --live --expect-served --probe-model qwen3.8-flash-next-iq3_s  # 200 -> VERDICT LIVE_PROBE CLEAN
```

`--selftest` seeds, each naming the check it must fire (L10): `alias_heretic_restored`→MISLABEL_FAMILY,
`alias_heretic_size`→MISLABEL_SIZE, `alias_huihui_restored`→MISLABEL_FAMILY,
`alias_iq3xxs_restored`→MISLABEL_QUANT, `id_serves_wrong_family`→MISLABEL_FAMILY (id layer),
`served_path_missing`→PATH_MISSING, `alias_is_model_id`→ALIAS_IS_MODEL_ID,
`alias_collision`→ALIAS_COLLISION, `live_missing_one_id`/`live_extra_id`→LIVE_MISMATCH,
`probe_serves_the_name`→NAME_RESOLVES, `probe_not_running`→PROBE_NOT_RUNNING (3.18's required seed
class), `honest_name_does_not_route`→NAME_MISSING. Two controls must stay CLEAN: the fixed wiring
itself, and **`correct_27b_wiring`** - a correctly-named 27B Heretic upstream serving
`C:/AI/models/RVN-Qwen3.8-27B-Heretic-GSQ-RCO-IQ3_XXS-mtp.gguf` reads 0 findings, which is what proves
the gate is a rule about served files and not a ban on the word "heretic27b".

A third probe is the claim parser itself (`UNIT_ROWS`, 13 rows of names measured on this box): the
first run of it caught a real bug - a flat substring scan read a **size `7b` claim out of
`coding_heretic27b`** (`27b` contains `7b`). Sizes are now matched in a separator-preserving view with
a digit-boundary rule (`_has_size`), so `27b` is not evidence of `7b` and `qwen3.5-9b` still shows its
`9b`. 13 rows, 0 faults.

## The edit

`C:/AI/director/config/llama-swap.yaml` (repo `C:/AI/director`, the file is tracked and was clean at
HEAD `36dadae`; the commit is the backup, no .bak in a git repo): the three false aliases are removed,
`strata` and `qwen3.8-flash-next-iq3_s` are kept, and a comment block names the item, the record, the
gate, and the 27B state. **The gateway hot-reloaded it - no restart, no /load, no /unload:**
the 404s below came from the running process minutes after the file edit, which is also direct proof
that this file is the config the live router reads.

## Live after the edit (all with `gpu_guard.ps1` rc=0 `IDLE` recorded inline)

- `coding_heretic27b` -> **HTTP 404** `{"src":"llama-swap","error":{"message":"no router for requested model","type":"invalid_request_error"...`
- `coding_huihui27b` -> **HTTP 404** same shape.
- `qwen3.8-flash-next-iq3_xxs` -> **HTTP 404** same shape.
- `qwen3.8-flash-next-iq3_s` (the honest name) -> **HTTP 200** `chatcmpl-...`, `model` echoes the name.
- `GET /v1/models` -> the same 5 ids as the config's served-model upstreams, so `LIVE_MISMATCH` = 0.
- GPU discipline: **0 renders, 0 queue posts, 0 `/load|/unload|/upstream`, no vision model, no
  vision judge, no KEEP** - no image, video, audio, frame, still, caption or prompt was produced.

## The 27B: what is on this box (measured, for needs_derrick row 32)

- `C:/AI/models/RVN-Qwen3.8-27B-Heretic-GSQ-RCO-IQ3_XXS-mtp.gguf` **10,569,270,720 B**, with
  `C:/AI/models/RVN-Qwen3.8-27B-Heretic-GSQ-RCO-IQ3_XXS-mtp.gguf.md5` and `.DONE` (both 2026-10-10),
  plus `C:/AI/models/mmproj-Qwen3.8-27B-Q8_0.gguf` 629,247,008 B and
  `mmproj-Qwen3.8-27B-BF16.gguf` 931,145,888 B, and a partial
  `nsfm/Qwen3.8-27B-NSFM-Q3_V2-heretic-AF-IQ4_XL.gguf.part`.
- llama-swap serves **nothing** with a Heretic-27B name (5 upstreams, none of them). `netstat -ano`
  shows **0 listeners on :8090 at 2026-10-26 00:47 and 01:0x CT** (piped to python; the two netstat
  header lines are counted as non-listening). MAX pick 5 reads verbatim **"Look into the 27B server on
  port 8090"**, and its audit context (`fix_plan.md:18`, Max 2026-10-25 6:47-6:48 PM CT) records **"RVN 27B
  llama-server PID 3848 on :8090 outside llama-swap"**. So the honest statement is **live yesterday evening,
  DOWN now** - not "never existed" - and a 27B llama-server outside llama-swap is a shape this box has
  actually run. Reviving it is a GPU-shape ruling (AGENTS.md: one job at a time), so it goes to
  `needs_derrick.md` row 32, not to a render queue from me.
- No Huihui model on the box: `find C:/AI C:/Users/derek/HardcoreNSFW-TestRuntime -maxdepth 4
  -iname "*huihui*"` = 2 hits, both `notes/web/02v_huihui_page.401*.txt` (blocked rows, L8/L9).
- Serving the 27B (which ctx, which mmproj, what it displaces on a 16 GB RTX 5070 Ti) is **Derrick's
  call**; the gate already accepts that wiring, so the next pass can add it with its honest name the
  moment he says which shape.

## A side finding, measured while reading the config (needs_derrick row 33)

The file on disk is mtime **2026-10-25 19:34:55 CT**, `git status` clean == HEAD `36dadae`, and it has
**no `model_config:` / `parameters:` / `max_tokens:` block on any LLM upstream.** The text the E5
record quotes at 16:40 CT (flow-style aliases, a `max_tokens: 32768` block, launcher
`C:/AI/strata-0.2.2/strata/llama.cpp/build/bin/Release/llama-server.exe`,
`--config C:/AI/strata-0.2.2/configs/qwen38-flash-next-iq3s.json`) names **two paths that do not exist
on disk** - measured with `os.path.exists`: those two are MISSING, and every path the 19:34 file names
exists. So the 16:40-era text is not the live config; the 19:34 write superseded it, and E5's
`max_tokens` floor is not on disk. Two claims from those receipts are not on disk either:
`ck_e5_bakeoff_settings` and `ck_ck_attn_render_window` do not appear in `notes/ali11_run_checks.py`
(grep = 0 hits), so nothing re-measures them. I did not re-apply them - they belong to a ticked item,
and the ruling is Derrick's.

**Measurement-method lesson (L8-shaped):** my 00:45 `grep` of this file returned the 16:40-era text
while `read`/`edit`/`python open()` on the same path returned the 19:34 text. For a file a live service
owns, read it with the program that acts on it (the gate parses it with PyYAML and `os.path.exists`),
and let the live endpoint be the referee (the 404/200 pair is what proves which config is running).

## GPU discipline

`gpu_guard.ps1` with no arguments = rc 0 `IDLE`, recorded by the gate before every llama-swap call
(`gpu_guard rc=0 IDLE` prints in all three modes). `comfy_ctl.py status` =
`guard=(0, ['IDLE']) queue=None` at 00:5x CT. No render was queued, no LLM request ran while a render
ran (there was no render), no ComfyUI start/stop/restart, no model load/unload call from me
(the honest-name probe let the gateway load its own model, which is normal client use).
