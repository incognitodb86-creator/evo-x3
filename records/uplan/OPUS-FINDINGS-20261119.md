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
   - Arm 1b's sampler was a range; `config.yaml` already pins `sampler_arm: Q`.

8. **X3-D brief and Hermes `MEMORY.md` said S5 had already happened.** I read Derrick's "we already switched over" (the `mono` branch) as the live S5 switch. `/home/evo/AI/evo-x3` does not exist yet. Both now say "after S5", and X3-D says to use the part-branch bridge until then and to hold SK1 until W1b has a `RESULT.md`.

Also synced in this commit (left over from the 14:20-16:30 CT reviews):
- `x3/community/scripts/comm.py` gets Max's `ensure_comfy` cold-wake fix from `f3d0b7ce` (same code as the AlienPc copy) plus its 2 tests: 5 passed.
- `x3/render/.gitattributes` (`writer_pipeline/writer_prompt.md -text`), same as `alienpc/render/`.
- `alienpc/community/skills/flux-klein-prompting/SKILL.md` now matches the X3 copy, which is what Max put live on AlienPc (A4-RESULT, sha256 `3b7d033b...`).
- `hosts/x3/hermes/memories/MEMORY.md`: "ESP-off" corrected to ESP on.
- PLAN: W3e row (MIT, already live, leave Reference Cache off), X4 row (tests pending), stale ESP-off comment, Derrick's 16:48 CT words.

Not done here, needs a look on its own: the other `alienpc/community/skills/` copies differ from `x3/community/skills/` in 24 files, mostly from before today. Copying them over blind could break AlienPc paths, so this waits for SK4 in `UNI-APPLY-ALIENPC-C`.
