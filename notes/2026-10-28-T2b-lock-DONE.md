# T2b consistency lock — DONE (2026-10-28 20:02 CT)

Brief: `notes/2026-10-28-max-brief-T2b-lock.md` (Max, 7:53 PM CT; Derek's go 7:50 PM CT — "Lets run it again with this to see if it makes any difference").
Run dir: `C:\AI\community\runs\terrace_dom_q5biglock_20261028_s51083009` · tag `terrace_dom_q5biglock_20261028_s51083009` · arm id 09.
Builder: `runs/terrace_dom_q5biglock_20261028_s51083009/build_graph.py` — T2's builder with `SRC` pointed at **T2's `request.api.json`**.
One GPU window, one render, rc=0, **no redo**. Stopping after this render, as the brief says.

## The two changed widget values (proof, not intent)

The builder deep-copies T2's graph, edits in place, then **diffs every input of every node against T2 and requires the
diff set to be exactly these two paths** (printed by the build):

| Node · input | T2 | T2b |
|---|---|---|
| `c0` `MiniMaxH3ReferenceToVideo` · `prompt` | 13,128 chars | **13,640 chars** = `notes/2026-10-28-consistency-lock-block.txt` **verbatim** (510 chars, read from the file at build time so Derek's words are byte-exact) + `"\n\n"` (one blank line) + T2's `prompt_seg0.txt` unchanged (13,128 chars) |
| `save` · `filename_prefix` | `…/terrace_dom_q5big_20261028_s51083008/…` | **`community/terrace_dom_q5biglock_20261028_s51083009/terrace_dom_q5biglock_20261028_s51083009`** |

Node count 26 → 26; no node added, removed, rewired, or re-tuned. Verified on the file that will be submitted
(`request.api.json`, via `guard_check.py`): `startswith(lock-verbatim) = True`, bytes right after the lock
`0a 0a 73` = the blank line and then `subject_definitions:` (`exactly one blank line = True`), `endswith(T2 base) = True`.
Provenance copies in the run dir: `prompt_lock_block.txt` (lock, verbatim), `prompt_seg0.txt` (T2's base, unchanged), `prompt_full.txt` (exactly what was submitted).

Everything else asserted identical to T2 before the edit (drift = the builder refuses to write): seed **51083002** (same latent
init, so any difference in the clip is the prompt's doing) · **512×896** first pass with `lsu3` `mode "scale by multiplier"` **1.5**
→ canvas exactly **768×1344** · `ag0`/`ag1` `MiniMaxH3AddGuide` (`vae ← vvae`, `frame_idx 0`, latents `c0:1` / `s1_cat:0`) into the
two guiders · `c0.ref_image_size "max"` · pass 1 `s0_sched` **simple/8/1.0** fed in full · pass 2 `p2sched` **beta/3/0.4** ·
one `ksel` **euler** for both samplers · `dec_a.samples ← s0_sep:1` (audio from pass 1), `dec_v ← s1_samp:0` ·
`lsu3` conv_v1_bf16 / `align 32` / **chunking true** / force_unload / cuda / fp16 · **243 frames** · **24 fps** · beta7 int8HQ ·
CLIP nvfp4_awq · video/audio VAEs · **shift 12/3** · **VSA vsa keep_percent 10** · start image `community/TERRACE2_768x1344.png`.

## Adults-only guard (brief rule 3), run before the GPU window

`guard_check.py` (in the run dir) applies the community helper's own rule (`scripts/comm.py:41 guard_ok` + `PROMPT_KEYS`/`prompt_strings`,
the same gate inside `comm.run()` that stops a queue):
**1 prompt-bearing string in the graph — `c0` (13,640 chars) → PASS. ALL PASS = True**, so the runner's gate submits.
`guard_ok` also passes on the lock block alone and on T2's base separately. (Console showed the em dash in the lock header as `?` —
that's the PowerShell console codepage; the graph JSON escapes it as `\u2014` and `prompt_full.txt` is UTF-8.)

## Render seconds, exact

- `19:52:57 CT` window opened by `gpu_window.ps1` (`gpu_lock -Acquire` → pid 13176; runner's own `gpu_guard`:
  "lock held by parent driver pid 13176 | IDLE"), LLM `coding_swift15_iq3s_esp` unloaded, ComfyUI woken.
- `19:53:28` prompt `2d6bcf05-ef22-458a-85e0-c5a9cdc0ea12` submitted · `19:58:28` **JOB end ok secs=300.1** ·
  `19:58:29` **OBJECTIVE ok** `frames=243 size=768x1344 fps=24/1 audio=True dur=10.125 bytes=4848341 blackfreeze=[] outcome=ok` ·
  `19:58:30` `comfyui_auto` unloaded, lock released, post-window `gpu_guard` **IDLE**.
- **300.1 s = 1.235 s/frame** — vs T2's 300.3 s: **the lock costs nothing measurable (−0.2 s, 0.07 %)**, as expected
  (same steps, same canvas; the extra 512 prompt chars are inside the same text-encoder budget). Family: B2 240.1 s, A 360.1 s, C 480.2 s.

## Files delivered

| File | Bytes | Content |
|---|---:|---|
| `terrace_dom_q5biglock_20261028_s51083009_raw.mp4` | **4,848,341** | untouched render, native **768×1344** @ 24/1, 243 frames, 10.125 s, h264 + aac, **3831 kbps** |
| `terrace_dom_q5biglock_20261028_s51083009_final.mp4` | **6,606,689** | `ffmpeg -c:v libx264 -preset slow -crf 18 -c:a copy` **of the raw, native 768×1344**, 5220 kbps |

- QNAP `/pi-drop/` via `pi_qnap.py put`; `lsl` reports **the same sizes**: `…_raw.mp4 4848341`, `…_final.mp4 6606689`.
  **No RTX** (brief rule 4) — no `_rtx12` / `_rtx920` for this arm.
- Also in the run dir: `request.api.json` + `<tag>.api.json` + `<tag>.api.pretty.json`, `build_graph.py`, `guard_check.py`,
  `prompt_lock_block.txt` / `prompt_seg0.txt` / `prompt_full.txt`, `status.log`, `objective.json`, `<tag>.mp4.json`,
  the runner's contact sheet `<tag>_stills_contact.png`, `motion_check.py` + `motion_check.txt`.

## Does it make a difference? What the proxies can and cannot say

Same seed, same graph, so the only variable is the prompt. Paired against T2:

| Signal | T2 (no lock) | T2b (lock) | Direction |
|---|---:|---:|---|
| render seconds | 300.3 | **300.1** | unchanged |
| raw bytes / kbps | 4,846,757 / 3830 | **4,848,341 / 3831** | +0.03 % — statistically nothing |
| final (crf-18) bytes | 6,642,299 | **6,606,689** | −0.5 % |
| `motion_check` noise floor (per-path) | 6.664 | **7.028** | floors are per-path, not comparable across cells; only the shape inside each clip is |
| right-half thirds (first/mid/last) | 8.72 / 7.49 / 5.18 | **9.00 / 8.05 / 4.70** | front half livelier, **tail marginally quieter** |
| STATIC / LOW-ALL flags | STATIC-RIGHT ×2, LOW-ALL ×4 | **STATIC-RIGHT ×4, LOW-ALL ×3** | more static windows in the 7.0–9.0 s band (0.46×–0.52× of floor at 7.0/7.5/8.5 s) |

**Honest read:** on the proxies I have, the lock did **not** produce a livelier tail — if anything the 7–9 s window is calmer and the
last third is 9 % below T2's (4.70 vs 5.18 right-half mean), and the mid-section is a little livelier (8.05 vs 7.49).
**And the decisive caveat: none of my tools measures what the lock asks for.** Luma-diff motion and fixed-crf bitrate measure
frame-to-frame change and high-frequency energy, not identity fidelity — "zero drift / zero morphing of faces, bodies, lighting"
needs an identity or face-embedding comparison that is not installed on this box, and there is no face-crop embedding tool in
`scripts/`. So the answer to Derek's question "does it make any difference" is **his watch**, arm against arm at native 768×1344:
`terrace_dom_q5big_…_s51083008_final.mp4` vs `terrace_dom_q5biglock_…_s51083009_final.mp4` (same seed, so the two clips are a
matched pair — start frames should be near-identical; judge the faces/hands/wardrobe across the 10 s, and the BEAT FOUR tail).
Both raws and finals are in `/pi-drop/` for exactly that comparison.

## Not done, on purpose

- No RTX (brief rule 4); `final` = native-res crf-18 of the raw, per the standing deliverable preference.
- No identity/embedding drift metric — not available here; flagged above as the missing instrument rather than faked with a motion proxy.
- `verify_cell.py` not run (asserts another cell's recipe → false-alarm FAILs, handoff rule); ran the per-cell `motion_check.py` instead.
- No follow-up render. Report and stop.

GPU state after: `gpu_guard` IDLE, lock released (pid 13176), `comfyui_auto` unloaded, LLM left unloaded.
