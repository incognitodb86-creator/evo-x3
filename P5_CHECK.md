# P5 scripts dry check (C6 / ALI-127) - 2026-10-20

Ran read-only / no-GPU checks only. `batch_queue.py` was **not** run (it calls the LLM and ComfyUI); no LLM,
ComfyUI, `/upstream/*` or llama-swap call was made in this task. No file was edited, so no `.bak-20261020-ralph`
was needed (this page is a new file). Nothing was downloaded, installed, deleted or moved.

## 1. py_compile - all 5 named scripts pass

`py_compile.compile(..., doraise=True)` with `cfile` pointed at `C:\AI\community\tmpx\c6_<name>.pyc` so no
`__pycache__` in `scripts\` was touched. Exit 0, one `.pyc` printed per file, no tracebacks:

| Script | Result |
| --- | --- |
| C:\AI\community\scripts\batch_queue.py | PY_COMPILE OK |
| C:\AI\community\scripts\comm.py | PY_COMPILE OK |
| C:\AI\community\scripts\prompt_writer.py | PY_COMPILE OK |
| C:\AI\community\scripts\p6.py | PY_COMPILE OK |
| C:\AI\community\scripts\sy_1min.py | PY_COMPILE OK |

(The `.pyc` files are in `C:\AI\community\tmpx\`, left in place - no deletes.)

## 2. batch_queue.py - stitch, contact sheet, single rclone copy behind --no-upload: present

`python batch_queue.py shots.json RUN_NAME [--no-stitch] [--no-upload] [--dry-run]` (batch_queue.py:3).
Order of operations: all prompts first while the LLM is loaded (line 56) -> `--dry-run` writes prompts + graph
json and exits before any GPU work (57-59) -> `ensure_comfy()` unloads the LLM and wakes ComfyUI (60, comm.py:140)
-> renders one at a time (61-67) -> `results.json` (68) -> contact sheet + notes (69) -> stitch (70-71) -> upload (72).

- **Stitch (ffmpeg concat)** - `stitch()` batch_queue.py:24-30. Writes a concat list, then
  `ffmpeg -f concat -safe 0 -i list -c copy out` (line 26); if that fails or the file is missing it falls back to a
  re-encode `libx264 -crf 16 -pix_fmt yuv420p -c:a aac -b:a 192k` (28-29). Called at line 71, output
  `C:\AI\community\runs\<RUN>\<RUN>_stitched.mp4`.
- **Contact sheet + review notes** - `contact_sheet()` batch_queue.py:31-45. Per clip: `fps=1,scale=192:-2,tile=12x1`
  one row per clip, then `vstack` of the rows into `runs\<RUN>\contact_sheet.png`; writes `runs\<RUN>\notes.md`
  as notes only, "Notes are optional and do not block anything" (D14, line 41-44). Called at line 69, unconditionally.
- **Single rclone copy behind `--no-upload`** - `upload()` batch_queue.py:47-51 is the only rclone call in the whole
  `scripts\` tree (grep `rclone|RCLONE`: hits only batch_queue.py:7,49,50 and its own `.bak-20261020-v1`). One
  `rclone copy <stitched mp4> gdrive:AlienPc/community/<RUN> --retries 1 --low-level-retries 1`, logged as
  `RCLONE copy ... rc=`. Called exactly once, at line 72, gated on `"--no-upload" not in flags` and on stitch success.
- Shared by both P6 paths: `p6.py` runs `batch_queue.py` twice (p6_pairs with `--no-stitch`, p6_1min_community with
  defaults) and `sy_1min.py:4` imports `stitch, contact_sheet, FFD` from `batch_queue`, so there is one stitch/contact-sheet
  implementation, not two.

## 3. rclone - the 403 is gone

Command (read-only, config untouched): `rclone lsd gdrive:` with the winget rclone.exe that batch_queue.py:6 points at.

- **Result: SUCCESS, no 403.** Exit 0, 17 top-level Drive folders listed (CoinbaseWalletBackups, Derek Drive Library,
  Flow_Derek_Library_2026-09, GasketOptima, Gemini_Gems_Canon, Google AI Studio, the Google Flow Export folders,
  Grok Fleet Backups / Memory, GrokBot_*, Grok_Imagine_Library_DerekBoone, SB20261014, YouTube_Shorts_Ops).
  So the `gdrive:` remote is authorized right now; no re-auth was needed for this check.
- Two NOTICEs, not errors: (a) `gdrive:` uses rclone's **shared Google Drive client_id, which is being retired and
  will stop working during 2026** - the auth that works today can break on its own; (b) a Google Maps doc in
  `Taiwan Trip` is unexportable (harmless for our path).
- `rclone lsd gdrive:AlienPc` -> `ERROR : error listing: directory not found` (exit 3). The upload root
  `gdrive:AlienPc/community/<RUN>` does not exist yet; `rclone copy` creates remote dirs, so the first upload should
  create it. Flagging it so the first real upload is watched rather than assumed.
- rclone config was **not** changed (no `rclone config edit/create`, no client_id added) - that is Derrick's call.

## 4. Flags found while reading (not fixed - out of C6 scope, "only edit files named")

1. **`--no-stitch` also suppresses upload.** The upload at line 72 is nested inside `if files and "--no-stitch" not in
   flags:` (line 70), so a `--no-stitch` run can never upload. That is what `p6.py` does for p6_pairs, so the D1 x D2
   pairs will stay local (fine), but the flag combination is misleading: `--no-stitch --no-upload` and plain
   `--no-stitch` behave identically.
2. **`sy_1min.py` never uploads** - it stitches (its own `stitch()` call) but has no `upload()` call, so only the
   community 1-minute arm leaves the machine. Intentional for a side-by-side test, worth stating in the runbook (C7).
3. **Unknown flags are silently ignored** (`flags = set(sys.argv[3:])`, line 54) - a typo like `--no-uplod` runs the
   upload instead of skipping it.
4. `contact_sheet()` and `notes.md` are written before the stitch/upload step, so a failed render batch still produces
   review material; `results.json` is written even when some jobs failed (`done` list only holds successes).
5. Nothing in these five scripts calls a GPU job at import time except `sy_1min.py`, which does real work at module
   level (prompts, `ensure_comfy`, renders) - so it must never be imported for a dry check; only `py_compile` on it is safe.
