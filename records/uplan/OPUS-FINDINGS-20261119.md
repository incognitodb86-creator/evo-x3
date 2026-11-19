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
