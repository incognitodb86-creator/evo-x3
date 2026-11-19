# T2 bigger first pass — DONE (2026-10-28 19:40 CT)

Brief: `notes/2026-10-28-max-brief-T2-bigpass.md` (Max, 7:23 PM CT; Derek's go "Lets do t2" 7:21 PM CT). Test: handoff §T2.
Run dir: `C:\AI\community\runs\terrace_dom_q5big_20261028_s51083008` · tag `terrace_dom_q5big_20261028_s51083008` · arm id 08.
Builder: `runs/terrace_dom_q5big_20261028_s51083008/build_graph.py` — B2's builder, `SRC` pointed at **B2's `request.api.json`**
(an edited copy of B2's graph, never rebuilt from B). One GPU window, one render, rc=0, **no redo**. Stopping after this render.

## Canvas check — exact 768×1344

| Stage | Value |
|---|---|
| `c0` `MiniMaxH3ReferenceToVideo` | **512×896**, `length 243` (0.459 MP; B2 was 384×672 = 0.258 MP) |
| `lsu3` `MinimaxH3LatentUpscaler3D` | `mode "scale by multiplier"`, **`mode.scale 1.5`**, `align 32`, `enable_temporal_chunking true` |
| Arithmetic asserted in the builder | 512 × 1.5 = **768**, 896 × 1.5 = **1344**; all four edges divisible by 16 (VAE) and 32 (`align`) |
| Runner objective (`objective.json`, first attempt) | **`frames=243 size=768x1344 fps=24/1 audio=True dur=10.125 bytes=4846757 blackfreeze=[] outcome=ok`** |
| `ffprobe` on both deliverables | **768×1344 @ 24/1, 243 frames, 10.125 s, h264 + aac** |

k = 1.5 is the only step up from B2's k = 2 that lands on integers of the 32 grid (k = 1.25 → 614.4, breaks), per the handoff.
No `ResolutionSelector` (its 0.3 MP / 32-rounding preset list resolves to ~768×1408, off this cell's canvas) — unchanged from B2.

## Files delivered

| File | Bytes | Content |
|---|---:|---|
| `terrace_dom_q5big_20261028_s51083008_raw.mp4` | **4,846,757** | the untouched render, native 768×1344 @ 24/1, 243 frames, 10.125 s, h264 + aac, **3830 kbps** |
| `terrace_dom_q5big_20261028_s51083008_final.mp4` | **6,642,299** | `ffmpeg -c:v libx264 -preset slow -crf 18 -c:a copy` **of the raw, native 768×1344**, 5248 kbps |

- QNAP `/pi-drop/` via `pi_qnap.py put`; `pi_qnap.py ls /pi-drop/` reports **the same sizes**:
  `…_raw.mp4 4846757`, `…_final.mp4 6642299`. **No RTX** (brief: no RTX arg) — no `_rtx12` / `_rtx920` for this arm.
- Also in the run dir: `request.api.json` + `<tag>.api.json` + `<tag>.api.pretty.json`, `build_graph.py`, `prompt_seg0.txt`,
  `status.log`, `objective.json`, `<tag>.mp4.json`, the runner's contact sheet `<tag>_stills_contact.png`,
  `motion_check.py` + `motion_check.txt` (copied from B2, recipe-independent).

## Render seconds, exact

- `19:30:56 CT` GPU window opened by `gpu_window.ps1` (`gpu_lock -Acquire` → pid 17620; the runner's own `gpu_guard` read
  "lock held by parent driver pid 17620 | IDLE"), LLM `coding_swift15_iq3s_esp` unloaded, ComfyUI woken.
- `19:31:39` prompt `bfcc404a-f76b-4868-9c13-65b90f149955` submitted · `19:36:39` **JOB end ok secs=300.3** ·
  `19:36:40` OBJECTIVE ok (line above) · `19:36:41` `comfyui_auto` unloaded, lock released, post-window `gpu_guard` **IDLE**.
- **300.3 s = 1.236 s/frame** for 243 frames at 768×1344. Single window, rc=0, no stall, no redo.
- Cost vs the family (same prompt/seed/model, 243 f): **B2 240.1 s (0.258 MP pass 1)** → **T2 300.3 s (0.459 MP)** = **+25 %**;
  A native-8 360.1 s; C native-12 480.2 s. Below the handoff's ~380 s estimate. Consistent with pixel cost:
  the 8 low-res steps scale with MP (0.459/0.258 = 1.78×, ≈120 s → ≈165 s) while the 3 full-res steps (~135 s) do not move,
  i.e. ≈300 s. Pass split is inferred from that arithmetic, not measured per-phase.

## What changed in the graph — exactly four widget values

The builder asserts every B2 constant on the source, edits in place, then **diffs all inputs against B2 and requires the diff set
to be exactly these 4 paths** (printed by the run): `c0.width` 384 → **512**, `c0.height` 672 → **896**,
`lsu3.mode.scale` 2.0 → **1.5**, `save.filename_prefix` → `community/terrace_dom_q5big_20261028_s51083008/…`.
Node count 26 → 26; no node added, removed, rewired, or re-tuned.

Kept and asserted (drift = the builder refuses to write): `ag0`/`ag1` `MiniMaxH3AddGuide` (`positive ← c0:0`, `image ← img:0`,
`vae ← vvae:0`, `frame_idx 0`, latents `c0:1` / `s1_cat:0`) feeding the two `BasicGuider`s · `c0.ref_image_size "max"` ·
pass 1 `s0_sched` simple/**8**/1.0 fed **in full** to `s0_samp` · pass 2 `p2sched` **beta / 3 / 0.4** · one `ksel` **euler** for
both samplers (`ksel1` stays deleted) · `dec_a.samples ← s0_sep:1` (audio from pass 1), `dec_v ← s1_samp:0` ·
`lsu3` conv_v1_bf16 / `align 32` / `force_unload true` / cuda / fp16 / **chunking true** ·
seed **51083002** · prompt **13,128 chars byte-identical** · `community/TERRACE2_768x1344.png` ·
`10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors` · CLIP nvfp4_awq · video/audio VAEs · **shift 12 / 3** ·
**VSA vsa keep_percent 10** · **243 frames** · **24 fps**. Static validation (link targets + reachability from `save`)
plus the runner's `static_check` against live `/object_info`: both clean.

## Proxy signal (not a verdict)

- **Bitrate at fixed crf is a high-frequency-energy proxy, not a quality score.** Raw **3830 kbps** / 4.85 MB vs B2's raw
  3572 kbps / 4.52 MB (+7.3 % at the same crf path) — a denser first pass carries more real detail into the same canvas,
  and it stays inside the single-pass band (A 3459, C 3625), i.e. no burn signature.
- `motion_check.py` on the raw: noise floor **6.664** (B2's 5.650 — floors are per-path, comparable only inside a cell);
  right-half `right/floor` **0.64×–2.02×**, no STATIC collapse; peak whole-frame motion at t = 1.42 s (16.91).
  **Honest deviation to flag:** the **last third is quieter than B2's** — right-half means 8.72 / 7.49 / 5.18 across the thirds
  and four LOW-ALL windows at 7.5/8.5/9.5/10.0 s, where B2 held ~0.85–1.05× into the 8–10 s grope. That is the watch item
  for this arm: the sustained BEAT FOUR motion is what Derek asked for, and this render's tail reads less alive on the proxy.
- Derek's watch is the judge. The claim here is only: the graph changed in exactly four widget values, the canvas is exactly
  768×1344, and it cost 300.3 s (+25 % over B2).

## Not done, on purpose

- No RTX super-resolution (brief rule 4) — `final` is the native-res crf-18 of the raw, per the standing deliverable preference.
- `verify_cell.py` not run: it asserts another cell's recipe, so its FAILs would be false alarms (handoff rule).
- No T1 (Add-Guide ablation) and no follow-up render of any kind — the brief ends at the DONE note.

GPU state after: `gpu_guard` IDLE, lock released (pid 17620), `comfyui_auto` unloaded, LLM left unloaded.
