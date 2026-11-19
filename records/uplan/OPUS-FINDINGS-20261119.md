# Opus findings 2026-11-19

For Opus to read before the next file pass. Each item: what went wrong, evidence, fix. Derrick's chat decisions for today are in [PLAN.md "Derrick decisions 2026-11-19 (chat)"](./PLAN.md); where a commit conflicts with them, Derrick wins (t2830u).

1. **W1 did not test the ref2va rewriter the official way.**
   - What: W1 ran the ref2va rewriter through our `writer_prompt.md` with thinking off, not through its own guide, request format and thinking setting (Derrick t2810u).
   - Evidence: `records/BENCH-X3-W1/BRIEF.md` (commits `3787c283`, `0ac71cf0`): line 8 says "W1 tests the writer prompt that is live now" for every arm, Arm 3 `ref2va-27b` included; line 23 sets a non-thinking sampler for arms 1a/1b.
   - Fix applied: W1b reruns it officially (upstream guide, thinking on, upstream sampler, recommended quant). PLAN.md rows X5 and W1 updated. Needed: future benchmark briefs must state, per arm, the upstream guide, thinking and sampler they follow.

2. **W1 and the plan used stock (censored) models.**
   - What: the ref2va arm used the stock build, not the community uncensored one; the rule is now community uncensored (heretic/abliterated) only (t2843u).
   - Evidence: `records/BENCH-X3-W1/BRIEF.md` step 1 (Arm 3 `ref2va-27b` Q4_K_M); a stock ref2va Q5 was then queued for W1b.
   - Fix applied: stock ref2va Q5 cancelled and deleted; W1b runs heretic Q4 (step 2c) then heretic Q5 (step 2b) only. Needed: every model row in new plans names the heretic/abliterated build.

3. **`scripts/gitleaks-pre-commit.sh` blocked every commit, clean ones too.**
   - What: the built-in Python regex scan did not compile. The private-key alternative was written as `r"-"*5 + r"BEGIN ..." + r"-"*5` inside an implicitly concatenated string list, which is a Python syntax error at `pat = re.compile(`. Python reports `SyntaxError: invalid syntax. Did you mean True?` on the X3 (`Perhaps you forgot a comma?` on newer Python). With `set -e` the hook exits non-zero for any commit.
   - Evidence: commit `a6018891` ("split regex literals so secret scanners never self-trigger"); broken file sha256 `dfbfe3bb665c23d7cf5233a6691c00a418a8d7a365f263d5f50b42c13d01ad4c`.
   - Fix applied: that alternative is now one literal, `r"-{5}BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-{5}"` (still does not self-match). Fixed file sha256 `11cba7e5b629c5f65e5cae60915d9651ebe6a97a0e47582b642de176b0204190`, installed on the X3 at `~/.local/lib/evo-gitleaks/gitleaks-pre-commit.sh` and committed in `mono` with this note. Verified on the box in a scratch repo: clean file rc 0, fake `ghp_` token rc 1. Needed: run the hook once on a clean staged file before committing a hook change.

4. **A subfolder LoRA was written with a forward slash, so ComfyUI on Windows rejected it.**
   - What: the H3 max LoRA test request copies (AlienPc, `C:\AI\community\runs\h3max_lora_test_20261119\`) wrote a subfolder LoRA as `folder/file`. ComfyUI on Windows lists subfolder LoRAs with a backslash, so prompt validation failed with `value_not_in_list` for the 3 arms that used it. The top-level LoRA worked. After changing the slash to a backslash the subfolder-LoRA arm passed validation and started rendering (4:44 PM CT).
   - Rule: anything that writes `lora_name` must use the separator the target ComfyUI lists (Windows: backslash). Builders on the X3 (Linux) that target AlienPc must convert it, not use `os.sep`.
   - Code in `mono` that would hit this (paths only, no names):
     - `x3/community/scripts/parody/flux_still.py`: the `--hybrid` stack hard-codes a subfolder LoRA with `/` (line 154); `_inject_flux_loras` passes the name through unchanged.
     - `x3/community/scripts/parody/test_flux_h3_redteam.py`: asserts the forward-slash form (lines 75, 113), so it must change with the fix.
     - `x3/community/scripts/parody/fill_request.py`: writes `lora_name` straight from `--lora` / LoRA list entries (line 120) with no separator conversion; hits whenever a subfolder LoRA is given with `/`.
   - No `*.api.json` template in `mono` has a `lora_name` containing `/`.
   - Fix needed (file-only, Opus): one helper that rewrites `/` to `\` in `lora_name` when the target is AlienPc ComfyUI, used by the three files above, with the test updated.

5. **Some X3-B tests could not run during W1b.**
   - What: pending `UNI-APPLY-X3-B` tests that need the GPU, Swift or a render window were skipped as unsafe while W1b runs (t2850u).
   - Evidence: `records/UNI-APPLY-X3-B-PIJOB/RESULT.md` (H1c, L5, H5+L6, L9, R11 marked PENDING).
   - Fix needed: run them after W1b has a `RESULT.md`.

## Opus response 2026-11-19 17:05 CT

All five are right. They are Opus mistakes, not box problems. What changed in this commit:

1. **and 2. Benchmarks not run the official way, stock builds.** Agreed. The W1 brief pushed every arm through our `writer_prompt.md` and named the stock ref2va build.
   - New rule in `.github/instructions/records.instructions.md` and the brief template: every benchmark arm names its community uncensored build (heretic/abliterated), its upstream guide and request format, its thinking setting, its sampler and its quant, each with a link. No arm runs on our own prompt unless the arm is "our prompt" on purpose.
   - `records/BENCH-X3-W1/BRIEF.md` has an Update section: superseded by W1b, Arm 4 dropped, and the other faults listed (#7) so nobody reruns it as written.
   - `records/BENCH-ALIENPC-1/BRIEF.md` has an Update section: the A5 still arms follow the same per-arm rule.
3. **Hook blocked every commit.** Agreed. I split the regex to dodge my own scanner and never ran the hook once. Max's fix re-checked on the Windows clone (Git Bash, throwaway repo, no gitleaks binary so the built-in scan ran): clean staged file rc 0, synthetic `ghp_` token rc 1. New brief rule: run a changed hook or script once on a clean input before committing it.
4. **LoRA slash.** Fixed. `fill_request.comfy_lora_name()` turns `/` into `\` (AlienPc ComfyUI lists subfolder LoRAs with a backslash). `EVO_COMFY_PATH_SEP=/` switches it for a ComfyUI on Linux. `fill_request._inject_h3_loras` and `flux_still._inject_flux_loras` (so `--hybrid` too) both use it. `resolve.names_from_flux_refmod_or_lora` already reads either slash, so the Flux -> H3 celeb pickup still works. `test_flux_h3_redteam.py` now expects the backslash and has a new subfolder test: 6 passed. Full parody suite on the Windows scratch copy: same 39 environment failures as the unchanged tip, plus 1 new pass.
5. **X3-B tests pending.** Agreed. `records/UNI-APPLY-X3-B-PIJOB/BRIEF.md` has an Update section saying they run after W1b has a `RESULT.md`, and fixes the wrong "(ESP off)" on the idle-path test.

Three more Opus faults found while checking:

6. **X3-F brief used a path that does not exist yet.** It installs the hook on `/home/evo/AI/evo-x3`, which only exists after S5. Max installed it on `/home/derekboone/evo-x3` instead (X3-F RESULT). `records/UNI-APPLY-X3-F-PARITY/BRIEF.md` has an Update section for Items 2-3 and the post-S5 hook.
7. **More W1 brief faults, not in the list above.** For any rerun of a W1 arm:
   - Live llama-swap `profiles.halogen-only` maps `gemma4-heretic` to the resident Gufo slot, so "Arm 2" would have tested Gufo again. Check `/running` shows the arm's own model before scoring.
   - `writer_pipeline/acceptance/wp_accept.py` has no `--arm` option, must run with the render venv (`/home/evo/AI/render/x3/.venv/bin/python3`), uses fixed still paths nobody checked on the X3, and its `comfy_busy()` probes `127.0.0.1:8188`, not AlienPc.
   - `test_u54_named_e2e.py` is a mocked pytest, not a runner for the 2 named-parody asks.
   - The "4 creative-writing asks from F4" were only categories, not prompts.
   - Arm 1b's "Qwen native non-thinking" sampler was a range and had the thinking-mode top_p (0.95). The real non-thinking values are 0.7 / 0.80 / 20 / presence 1.5 (see Setup audit S1/S2).

8. **X3-D brief and Hermes `MEMORY.md` said S5 had already happened.** I read Derrick's "we already switched over" (the `mono` branch) as the live S5 switch. `/home/evo/AI/evo-x3` does not exist yet. Both now say "after S5", and X3-D says to use the part-branch bridge until then and to hold SK1 until W1b has a `RESULT.md`.

Also synced in this commit (left over from the 14:20-16:30 CT reviews):
- `x3/community/scripts/comm.py` gets Max's `ensure_comfy` cold-wake fix from `f3d0b7ce` (same code as the AlienPc copy) plus its 2 tests: 5 passed.
- `x3/render/.gitattributes` (`writer_pipeline/writer_prompt.md -text`), same as `alienpc/render/`.
- `alienpc/community/skills/flux-klein-prompting/SKILL.md` now matches the X3 copy, which is what Max put live on AlienPc (A4-RESULT, sha256 `3b7d033b...`).
- `hosts/x3/hermes/memories/MEMORY.md`: "ESP-off" corrected to ESP on.
- PLAN: W3e row (MIT, already live, leave Reference Cache off), X4 row (tests pending), stale ESP-off comment, Derrick's 16:48 CT words.

Not done here, needs a look on its own: the other `alienpc/community/skills/` copies differ from `x3/community/skills/` in 24 files, mostly from before today. Copying them over blind could break AlienPc paths, so this waits for SK4 in `UNI-APPLY-ALIENPC-C`.

## W1b correction 2026-11-19 17:13 CT

W1 ran ref2va with our `writer_prompt.md` replacing its trained guide (wrong shape). Fixed per the model card and the pytraveler MiniMax-H3-Prompt-Rewriter node: the system message is only `fast_system_prompt.txt`, and `fast_user_prefix.txt` goes at the start of the user message before `Original prompt:`. Thinking is off, `max_tokens` is 3000, and MTP stays on if the llama-server build supports it. Official thinking-on heretic Q4 (step 2c) was paused after 3 finished cases; heretic Q4 then Q5 are rerun in this layout. General writers (Flash-Next) still use `writer_prompt.md`.

## Setup audit 2026-11-19 17:40 CT (Opus, read-only, Derrick: "debug our setup")

Sources: live copies on `mono` `df79048` (X3 snapshot 4:29 PM CT, AlienPc refresh 4:54 PM CT), repo code, and upstream model cards and runtime docs read today (links in each line). Nothing here was run on a box.

**Model settings vs upstream (the "official way" rule, t2810u):**

| # | What | Ours (where) | Upstream (source) | Verdict |
|---|---|---|---|---|
| S1 | Writer sampler, thinking off | `sampler_arm: Q` 0.85 / 0.90 / 20 / min_p 0 / presence 0.5, labelled "Qwen3.8-Flash-Next card preset" (`x3/render/writer_pipeline/config.yaml`, U56) | Non-thinking: 0.7 / 0.80 / 20 / min_p 0 / presence 1.5 ([Qwen/Qwen3.8-Flash-Next](https://huggingface.co/Qwen/Qwen3.8-Flash-Next) card; the Huihui abliterated card gives no sampler) | **WRONG label and values.** Not changed live (W1b running, t2850u). Proposed arm W1c below. |
| S2 | My W1 Arm 1b "Qwen native non-thinking" | 0.7-1.0 / top_p 0.95 / 20 | 0.7 / 0.80 / 20 / presence 1.5 | **WRONG** (top_p 0.95 is the thinking value). Adds to #7. |
| S3 | Writer thinking | off (`enable_thinking: false`) | On by default, effort `xhigh` | Our choice for speed. Never tested the official way. W1c. |
| S4 | Gufo server defaults for `flash-next-uncensored-v2` | 1.0 / 0.95 / 20, effort medium, `--reasoning-budget 8192` | Thinking values 1.0 / 0.95 / 20 match. No upstream source for the 8192 cap (Qwen allows up to 262,144 reasoning tokens); default effort is xhigh | OK sampler. Budget 8192 is a community cap (Derrick t2322), not upstream; keep, but note it can cut long Hermes/pi thinking. |
| S5 | ref2va heretic Q4 (W1b) | 0.7 / 0.8 / 20, 16384 out, thinking on, xhigh, ctx 32768 | Same ([lightx2v vllm_server.sh / post_vllm.py](https://huggingface.co/lightx2v/MiniMax-H3-Prompt-Rewriter-Qwen3.8-27B-Ref2VA)) | **OK.** Check W1b sends the official system prompt + `VIDEO_PROMPT_WRITING_GUIDE_ref_en.md`, and images interleaved with their labels. Case 1 used 13,645 of 16,384 tokens: count `finish_reason=length` cases as truncated, not as model failures. |
| S6 | gemma4 heretic | 1.0 / 0.95 / 64 | Same ([google/gemma-4-26B-A4B-it](https://huggingface.co/google/gemma-4-26B-A4B-it)) | OK (pinned to Gufo by `halogen-only`, so not in use). |
| S7 | Swift 1.5 coding | pi "medium"; AlienPc `thinkingBudgets.medium = 2048`; X3 pi `thinkingTokenBudgetField: thinking_budget_tokens` | Effort is set with `chat_template_kwargs.reasoning_effort` (xhigh default; medium/low supported); sampler 1.0 / 0.95 / 20 / 0 / presence 0 ([ukisai/Swift1.5-Qwen3.8-Flash-Next](https://huggingface.co/ukisai/Swift1.5-Qwen3.8-Flash-Next)) | **ASSUMPTION / check:** pi's "medium" may not set `reasoning_effort: medium` at all; it may run xhigh thinking with a 2,048-token cap, which cuts reasoning short. Check one request body on AlienPc (llama-swap log). "ESP" is not in any Swift card: say where it comes from in the AlienPc llama-swap entry. |
| S8 | AlienPc Swift llama-swap entry | not in the repo | - | **GAP:** `C:\AI\director\config\llama-swap.yaml` has no redacted copy under `hosts/alienpc/live/`, so nobody can check Swift's sampler, context or ESP flags from GitHub. Add it to the AlienPc snapshot. |
| S9 | Miraclein 4.5 (A5) | candidate templates | Author: "12 steps Euler CFG 1.1" ([civitai 2453960](https://civitai.com/models/2453960)); stock Klein 9B distilled: 4 steps, guidance 1.0 | Check the 3 `miraclein_*.candidate` templates use 12 / Euler / 1.1 before A5 (the official-way arm). |
| S10 | Klein9 RefMod | `--hybrid` 0.85 + LoRA 0.60; default retention 0.7 | Guide: strength 0.80-0.90 (0.90 each for 2 people); `partially_preserved (0.7)` for creative, `fully_preserved (1.0)` + strength 1.0 for portraits ([malcolmrey guide](https://huggingface.co/datasets/malcolmrey/various)) | OK. |
| S11 | 10Eros-Max beta_7 (A7) | `res_multistep` / Euler arms | "8 step Euler/Simple or Er/SGM to start", shift 12/3, VSA 90% sparsity, no cache/spectrum with references ([TenStrip/10Eros-Max](https://huggingface.co/TenStrip/10Eros-Max)) | Our TQ3 bans `er_sde`; upstream lists `er_sde` / `sgm_uniform` as an optimal pair. Add it as a TQ3 arm instead of banning it, and check shift 12/3 on the beta7 candidates. |
| S12 | H3 realism LoRA | default 0.7, trigger `r34l1sm` | 1.0 intended, 0.6-0.8 lighter, trigger `r34l1sm` ([fal/MiniMax-H3-Realism-People-LoRA](https://huggingface.co/fal/MiniMax-H3-Realism-People-LoRA)) | OK (M5 tests 0.60 and 1.00). |

**Setup bugs found:**

| # | Issue | Evidence | Fix |
|---|---|---|---|
| B1 | Hermes `h3-render` ran THE ONE COMMAND in the foreground, but Hermes stops terminal calls at 180 s and the writer takes about 2 min, up to 30 (Opus fault, `9b10d43`) | live `hosts/x3/live/hermes/config.yaml` `terminal.timeout: 180`; pi-job skill "prep usually ~2 min, can take up to 30 min" | **Fixed in this commit:** `hosts/x3/hermes/skills/h3-render/HEAD.md` item 9 runs it (and `flux_still.py --queue`) with `setsid nohup` and polls for an `EXIT` line. The queue guard hook still sees the flags. Goes live with X3-E. |
| B2 | `pi-job` codes on AlienPc Swift with `--thinking low`, but Derrick wants medium (t2766s9752, 16:48 CT) | `config/bin/pi-job` `_run_pi` | **Fixed in this commit:** medium on the AlienPc route (`PI_JOB_ALIENPC_THINKING` to change it), low on the X3 fallback; new test passes. Not live until Max reinstalls `pi-job` (after W1b). |
| B3 | AlienPc `settings.json` has the same key twice (`llama-swap/coding_swift15_iq3s_esp` in `compaction.modelOverrides`), left by the ESP rename in `0ac71cf` | JSON duplicate-key scan | **Fixed in this commit** in the proposed AGT1 copy (kept the last one, which is the value JSON already uses). |
| B4 | Gufo returns HTTP 400 when a request has top-level `reasoning_effort` and `enable_thinking: false` (by design, [gufo openai_chat.cpp](https://github.com/gufo-org/gufo)). llama-swap `setParamsByID` adds `reasoning_effort: low` to `flash-next-uncensored-v2-sub` / `flash-next-uncensored-sub`. | live `llama-swap.yaml` | Any caller that asks for a `-sub` name with thinking off gets a 400. Today pi subagents keep thinking low, so it does not fire. If it ever shows: send `reasoning_effort: "none"`, or put the effort inside `chat_template_kwargs`. |
| B5 | Hermes sets reasoning effort twice: `model.reasoning_effort: low` and `agent.reasoning_effort: medium` | live Hermes `config.yaml` | Max: check which one Hermes sends (`hermes config get`) and delete the other. |
| B6 | `qwen27b` is still a pi model and in the exclusive `main` group with no `halogen-only` pin, so picking it in pi unloads Gufo (Hermes + writer down, ttl 1800 s) | live `llama-swap.yaml`, pi `models.json.example` | Pin it like the others, or drop it from pi's model list. Derrick's call (Q card below). |
| B7 | Gufo runs `--sessions 2` while llama-swap allows `concurrencyLimit: 4`; Hermes, the writer, Forge/Ralph and pi-job's X3 fallback all share 2 sessions | live `llama-swap.yaml` | Writer calls can wait behind a Ralph loop (writer timeout 900 s). Note only; measure before changing. The slot's comments still describe Halogen KV pools: stale. |
| B8 | The production writer/Hermes model loads from `/srv/bakeoff/...@cbc7fba/` | live `llama-swap.yaml` | Kept by the P2.2 manifest, so safe today. Move it to `/srv/models/` in a quiet window so a future bakeoff cleanup can't take it. |

**Proposed, needs Derrick's yes (Q cards):**
- **Q-W1c:** after W1b has a `RESULT.md`, run the live writer (Gufo `flash-next-uncensored-v2`, already the uncensored build) the official way, as 2 extra arms on the same 12 cases: (a) Qwen non-thinking 0.7 / 0.80 / 20 / 0 / presence 1.5; (b) thinking on, effort xhigh, 1.0 / 0.95 / 20 (slow). Compare with today's `Q`. Only `config.yaml` copies change; no model downloads.
- **Q-B6:** pin `qwen27b` to Gufo in `halogen-only` (or remove it from pi)?

## beta7_validate gap 2026-11-19 evening

`beta7_validate` only checks banned headers/markdown/refusals/tag balance, so it passed 12/12 W1 outputs that were missing sections. The six-section check must be part of scoring. Needed fix: add a section-completeness check for ref2va outputs.

## Opus 466bcf3b verification 2026-11-19 5:33 PM CT (box, read-only on live X3 and AlienPc)

Checked against live X3 writer `config.yaml` and `/etc/evo-x3/llama-swap.yaml`, live Hermes `config.yaml`, live `/usr/local/bin/pi-job`, the fresh snapshots (including the AlienPc Swift llama-swap file), and the repo copies. No live fixes. `config/bin/tests/test_pi_job_chat_reply.py`: 5 passed.

| # | Verdict | Evidence |
|---|---|---|
| S1 | correct | Live and repo writer `sampler_arm: Q` is 0.85 / 0.90 / 20 / min_p 0 / presence 0.5, labelled "Qwen3.8-Flash-Next card preset". Not changed live. |
| S2 | correct | W1 brief step 3 still says temp 0.7-1.0, top_p 0.95, top_k 20 for the "Qwen native non-thinking" arm. |
| S3 | correct | Live writer `thinking: false`. Official-way writer arms remain the open Q-W1c card. |
| S4 | correct | Live Gufo `flash-next-uncensored-v2` is 1.0 / 0.95 / 20, `--reasoning-effort medium`, `--reasoning-budget 8192`. |
| S5 | correct (superseded in the client) | Live Q4 slot comment still says per-request 0.7 / 0.8 / 20, `max_tokens` 16384, thinking on, xhigh, `--ctx-size 32768`. Later t2884u/t2887u client runs use thinking off and `max_tokens` 3000. |
| S6 | correct | Live `gemma4-heretic` is 1.0 / 0.95 / 64; `halogen-only` pins it to Gufo. |
| S7 | partly right | AlienPc `defaultThinkingLevel: medium` and `thinkingBudgets.medium = 2048` are right. `thinkingTokenBudgetField: thinking_budget_tokens` is only on the AlienPc Swift entry in X3 pi config; X3 local Flash-Next models use `thinking_budget`. The Swift entry has no `medium` → `reasoning_effort` map (only an `off` sampler override), so the "medium may not set effort" check still stands; no live request body was read (W1b running). ESP is the `_esp` llama-swap slot (`--config strata-swift15-iq3s-esp.json`) plus pi `experimental_speed_projection: true`. |
| S8 | correct (gap now filled) | The live file exists at `C:\AI\director\config\llama-swap.yaml` (11,926 bytes, mtime 2026-11-17 5:11 PM CT). It was missing from the repo; a redacted copy is in this commit at `hosts/alienpc/live/llama-swap/llama-swap.yaml`. No keys in the live file. |
| S9 | correct (already matches) | All 3 `miraclein_*.candidate` templates (X3 and AlienPc) already use 12 steps, Euler, CFG 1.1. |
| S10 | correct | `--hybrid` is RefMod 0.85 + LoRA 0.60; default retention is `partially_preserved (0.7)`. |
| S11 | correct | TQ3 still bans `er_sde` (`res_multistep` vs `euler`). |
| S12 | correct (later dropped from use) | Repo `h3_realism_lora` is strength 0.7, trigger `r34l1sm`, `enabled: false`. t2885u later archived the realism LoRA; values in the file were right. |
| B1 | correct, not live | Repo `hosts/x3/hermes/skills/h3-render/HEAD.md` has `setsid`/`nohup`. Live Hermes skills do not include `h3-render`. Waits on X3-E. |
| B2 | correct, not live | Repo `pi-job` has `PI_JOB_ALIENPC_THINKING`; tests 5 passed. Live `/usr/local/bin/pi-job` is still sha256 `c7858c1a…` with no such flag. Waits on reinstall after W1b. |
| B3 | correct | The proposed AGT1 repo `settings.json` has one `llama-swap/coding_swift15_iq3s_esp` override key. Live AlienPc `settings.json` still has that key twice. Repo copy was not overwritten. |
| B4 | yaml correct; 400 not re-tested | Live `setParamsByID` still adds `reasoning_effort: low` on `flash-next-uncensored-v2-sub` and `flash-next-uncensored-sub`. The Gufo HTTP 400 was not reproduced (would hit the writer slot during W1b). |
| B5 | partly right | Live Hermes has `model.reasoning_effort: low` and `agent.reasoning_effort: medium`, and also `auxiliary.vision.reasoning_effort: low`. |
| B6 | correct | `qwen27b` is in exclusive group `main` and is not in `halogen-only` pins ("qwen27b left alone"). It is still in pi `models.json.example`. |
| B7 | correct | Live Gufo slot has `--sessions 2` and `concurrencyLimit: 4`. |
| B8 | correct | Live writer/Hermes weights path is `/srv/bakeoff/Huihui-Qwen3.8-Flash-Next-abliterated-v2-GGUF@cbc7fba/`. |

## Opus got wrong (466bcf3b setup audit)

1. **S7 over-generalized the token-budget field.** Opus wrote "X3 pi `thinkingTokenBudgetField: thinking_budget_tokens`". In the live X3 pi `models.json.example`, that field is `thinking_budget` on the local Flash-Next models and `thinking_budget_tokens` only on the AlienPc Swift (`coding_swift15_iq3s_esp`) entry. The AlienPc `thinkingBudgets.medium = 2048` figure was right. The open check (does pi "medium" set `reasoning_effort: medium` on Swift?) was not closed; the Swift entry has no medium/low/high effort map, which keeps the concern open. ESP origin, which S7 asked to name, is the AlienPc llama-swap `_esp` slot config `strata-swift15-iq3s-esp.json` and the pi flag `experimental_speed_projection: true`.
2. **B5 was incomplete.** Hermes also sets `auxiliary.vision.reasoning_effort: low`, a third copy besides `model` (low) and `agent` (medium).
