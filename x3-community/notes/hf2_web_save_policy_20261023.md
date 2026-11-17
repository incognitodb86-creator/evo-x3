# HF2 - web saves can never trip the harness check again (2026-10-23, Forge)

## What stopped the loop
`2026-10-23T16:59:37 iter 01 CHECK FAIL: json.tool C:\AI\community\notes\web\reddit_anatomy.json:
Expecting value: line 1 column 1 (char 0)` -> `STOP_RALPH` (ralph.log), iteration had ticked BQ1a
cleanly (status=fail exit=0 ticks=+1 denies=0 checkfails=1).

## Diagnosis (root cause, not the symptom)
1. The harness runs `python -m json.tool` over **every** `C:\AI\community\notes\web\*.json` after each
   iteration. That glob is unconditional, so a research body with a `.json` extension is a gate file.
2. Read-only web GETs on this box do **not** return JSON where the URL says `.json`:
   - `reddit.com/*/search.json` -> **403 + HTML** body (AGENTS.md: "reddit.com/search.json = 403 here").
   - proxy/mirror pages (llama-civilisation SD prompt-engineering, r/StableDiffusion mirrors) -> **HTTP 200
     + "Blocked" HTML** body, so the transport looks fine and only the body lies.
3. BQ1a saved four such bodies with a `.json` extension (names copied from the URL). The file was never
   JSON; the check was not broken, the extension was. **A web body is untrusted input; the extension is a
   claim about it and must be proven from the bytes, not from the URL.**
4. Second-order defect: a research pass had no pre-check of its own writes, so the loop died on the next
   summary. The older saves (`notes/web/if_*.404.txt`) already used a stamped-name convention; the rule was
   never written down as a tool.

## Fix (all inside community scope, committed in C:\AI\community)
- `scripts/web_fetch.py` - the only sanctioned web-save path. Fetches (or reclassifies a body already on
  disk with `--from`) and picks the extension **from the body**: `.json` only when `json.loads` (the same
  parser the harness check uses) accepts it; markup -> `.html`; other -> `.txt`; non-200 -> `.txt` with the
  status stamped in the name (`x.403.txt`). `--ext json` on a non-JSON body **refuses** (that exact bomb).
- `scripts/check_web_saves.py` - the pre-check to run at the end of a research pass. Sweeps `notes/web`
  for `*.json` that `json.tool` would reject; `--fix` renames offenders out of the glob (collision-safe),
  rc 1 when dirty so it can gate a pass.
- `scripts/tests/test_web_fetch.py` - 17 offline tests, no network, no GPU:
  classify matrix (valid JSON / 200-HTML / 403-HTML / plain / empty), the **HF2 incident replay** (plant the
  403-HTML `.json` bomb -> the detector fires -> `--from` lands it as `.html` -> sweep goes CLEAN, bytes
  preserved), refusal of a forced `.json`, no-overwrite suffixing, collision-safe fix, cli rc, and a
  **non-vacuity probe**: the detector MUST fire on the planted bad file and stay silent on a valid one
  ("a green check that cannot fail is worthless"). Plus a live-repo regression test: `notes/web` sweep == [].
- Data: the four BQ1a offenders were renamed to `.html` last pass (content kept, evidence intact).
  Live proof this pass: `check_web_saves.py` = `CLEAN ... 43 checked`; then a live GET of
  `reddit.com/r/StableDiffusion/search.json` (the file class that killed the loop) -> `HTTP 403 ->
  notes/web/hf2_live_reddit.403.txt (189908 bytes)` and the sweep stayed `CLEAN ... 44 checked`; a live GET
  of `huggingface.co/api/models/ggml-org/Qwen2.5-Omni-7B-GGUF` -> `HTTP 200 -> notes/web/hf2_live_hf.json
  (json.loads accepted)`. So both the failure path and the success path route to the right extension.
- AGENTS.md "Check commands": the web-save line now names both scripts (pre-check, not post-mortem).

## [!] Max (informational, not blocking - PROMPT.md: ralph.ps1 stays Max's)
Optional hardening on the harness side, if Max wants it: validate only harness JSON (e.g. check
`p7/JOB_REQUEST.json` + `p7/jobs/*.json` by name, plus `shots/*.json`) instead of globbing
`C:\AI\community\notes\web\*.json`, since that folder holds third-party response bodies. Forge's side is
already safe: nothing writes an unproven `.json` there any more, and `check_web_saves.py` gates a pass.

## Files
`C:\AI\community\scripts\web_fetch.py`, `C:\AI\community\scripts\check_web_saves.py`,
`C:\AI\community\scripts\tests\test_web_fetch.py`, `notes\web\hf2_live_reddit.403.txt`,
`notes\web\hf2_live_hf.json`, this note, `notes\forge-learnings.md`, `TASKS.md`, `AGENTS.md`.
0 GPU minutes: no ComfyUI port call, no comfy_ctl, no llama-swap, no render, no pip, no download install.
