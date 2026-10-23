# ALI-147 — full-minute pool loop · SUMMARY (FINAL, plan section 5)

Date 2026-10-22 (America/Chicago) · authored by **Forge** (Ralph iteration 05) · owner/report: **Max** posts it on Linear · **every output below is METHOD_ONLY. KEEP is Derrick's only.** No render was chosen, approved, ranked or quality-redone by Forge; no vision judge, no `p6_review`, no `qwen3vl_judge`, no `keep-candidate`.

Sources, all read-only: `ralph-community/TASKS.md`, `ralph-community/specs/ali147.md`, each arm's `PROOF.md` / `fairness.txt`, `runs/<id>/objective.json`, `runs/<id>/status.log` (DIP: `dip.log`), `p7/jobs/<id>.result.json`, and this iteration's CPU-only probes:

- `C:\AI\community\notes\ali147_summary_probe.py` → `C:\AI\community\notes\ali147-summary-20261022.txt` (37,898 B: per-arm file lists, bytes, sha256, `ffprobe -count_packets` rows, `objective.json` fields, `status.log`/`dip.log` lines, `p7\jobs` records incl. `.failed-20261022`, contact-sheet hashes, identity images (PIL + sha256), the BASE-minute control, and `os.path.exists` checks for every cited evidence file)
- `C:\AI\community\notes\ali147_summary_api_compare.py` → `C:\AI\community\notes\ali147-summary-api-20261022.txt` (2,717 B: `request.api.json` vs harness `<id>.api.json` byte compare)

No GPU, no ComfyUI (10004), no llama-swap (:8080), no Strata, no render, no `run_graph_job.py`, no ffmpeg encode by Forge — only `ffprobe` reads, `sha256`, `python -m json.tool`.

Path shorthand: `runs\` = `C:\AI\community\runs\`. Every mp4 is 768×1344 h264 + aac 32 kHz stereo. Frame counts are `ffprobe -count_packets nb_read_packets`, never `format=duration`.

## Matrix (the five arms)

| arm | control | the one variable | output mp4 | bytes | ffprobe duration | frames | render secs | contact sheet | failures |
|---|---|---|---|---|---|---|---|---|---|
| **CTRL** `ali147_pool_ctrl_s51080000` | the BASE minute `p7_r2_c3_pmot_full_pool` (3×481 @ 24 fps), not re-rendered | pool graph unchanged, single 481-frame 20.04 s clip, seed 51080000, steps 10 euler/simple | `runs\ali147_pool_ctrl_s51080000\ali147_pool_ctrl_s51080000.mp4` | 5,781,091 | 20.041688 s (video stream 20.041667) | 481 | **809.7** (`objective.json` `secs`, flat driver form) | `runs\ali147_pool_ctrl_s51080000\ali147_pool_ctrl_s51080000_stills_contact.png` (1,711,845 B) | none — `objective.json ok=true`, 1 attempt, 0 redos, `blackfreeze: []`, no `p7\jobs` record (driver job, not a loop job) |
| **FIX1** `ali147_pool_fix1_s51080000` | CTRL (481 frames / 24 fps / 20.042 s / same prompt / seed 51080000 / steps 10) | chunk 2 node `c0` `MiniMaxH3TextToVideo` → `MiniMaxH3ReferenceToVideo` (+`vae`/`audio_vae`, same start-still string, `length` 238→243, `ref_image_size` max→match) | `runs\ali147_pool_fix1_s51080000\ali147_pool_fix1_s51080000.mp4` | 5,841,241 | 20.041688 s | 481 | **857.5** (`objective.json` `attempts[0].secs`) | `runs\ali147_pool_fix1_s51080000\ali147_pool_fix1_s51080000_stills_contact.png` (1,715,915 B) | none — `result.json ok=true rc=0`, 1 attempt, 0 redos, `blackfreeze: []`, `err.out` 0 B |
| **FIX5** `ali147_pool_fix5_s51080000` | FIX1 (identical graph except the scheduler pair) | one variable only: steps 10 → **8** on both schedulers (`10/3` → `8/3`) | `runs\ali147_pool_fix5_s51080000\ali147_pool_fix5_s51080000.mp4` | 5,705,872 | 20.041688 s | 481 | **706.8** (`attempts[0].secs`) | `runs\ali147_pool_fix5_s51080000\ali147_pool_fix5_s51080000_stills_contact.png` (1,705,795 B) | none — `result.json ok=true rc=0`, 1 attempt, 0 redos, `blackfreeze: []`, `err.out` 0 B |
| **DIP** `ali147_pool_dip_s51080000` | the BASE minute segments (`segment_frames [481,481,481]`) | CPU ffmpeg only: 3-segment concat + 12-out/12-in dip **at the two segment restarts 481/962** (`dipblack` + `dipwhite`) + `base_reenc` (no-dip control) | `runs\ali147_pool_dip_s51080000\base_reenc.mp4` · `dipblack.mp4` · `dipwhite.mp4` | 35,488,827 · 36,068,806 · 38,260,910 | 60.166667 s each (audio stream 60.160000 s) | 1443 each | **0** (no GPU render; `dip.log` wall 17 s, `result.json wall_min=0.3`) | `runs\ali147_pool_dip_s51080000\base_reenc_stills_contact.png` (5,337,750 B) · `dipblack_stills_contact.png` (5,147,427 B) · `dipwhite_stills_contact.png` (5,185,853 B) | 1st run failed: `result.json.failed-20261022` `note="dip_join rc=5"`, outputs produced 1444 frames (the `-r 24` extra-frame bug). Fixed by `dip_join.py` DIP_FIX (`-frames:v` = probed sum 1443, no `-r 24`) → re-run `ok=true rc=0`. No STUCK line. Old outputs moved by Max to `runs\ali147_pool_dip_s51080000\failed-20261022\` |
| **FIX4** `ali147_pool_fix4_s51080000` | the BASE minute as one 59.709 s clip (1443 raw − 5×22 context = 1433 kept, tol 24; no 481 control for this arm) | one `MiniMaxH3Extender` chain, 6 clips (c0 243 + 5×260 raw), `validated true→false`, `duration` = `round(frames/24, 6)`, plain-string prompts, seed 51080000 on every clip | `runs\ali147_pool_fix4_s51080000\ali147_pool_fix4_s51080000.mp4` | 65,791,775 | 59.709000 s (video stream 59.708333) | **1433** (`|1433−1443| = 10` ≤ tol 24) | **3004.9** (`attempts[0].secs`; request `minutes:180` is a PRE-job gate, a longer render is not a failure) | `runs\ali147_pool_fix4_s51080000\ali147_pool_fix4_s51080000_stills_contact.png` (5,463,574 B, 35 tiles) | 1st run FAILED and STUCK: 3 attempts (base, `_redo1`, `_redo2`) each `secs=5.1`, Extender `RuntimeError: Ref2VA clip 1 is marked Validated but its disk cache is missing`, 3× `OBJECTIVE FAIL ... JOB error`, `2026-10-22 17:37:07 CT STUCK ... objective failure after 2 redos - flagged for Derrick`, `result.json.failed-20261022 rc=5`. Graph edited by `FIX4_GRAPH` (per-clip `validated`→`false`, `duration` 10.125/9.916667) → re-render `ok=true rc=0`, 1 attempt, 0 redos, `blackfreeze: []`. Old outputs in `failed-20261022\` |

## status.log / dip.log lines (verbatim, CT)

**CTRL** — `runs\ali147_pool_ctrl_s51080000\status.log` (396 B, three lines, no `OBJECTIVE`/`UNLOAD` lines):

```
2026-10-22 15:42:03 CT COMFY ready v0.38.0 wait=0s vram_free=0.9GiB
2026-10-22 15:42:03 CT JOB start ali147_pool_ctrl_s51080000 prompt_id=bb419c84-4af7-44c2-b106-04a7b5e0762b
2026-10-22 15:55:32 CT JOB end ali147_pool_ctrl_s51080000 ok secs=809.7 file=C:\AI\community\runs\ali147_pool_ctrl_s51080000\ali147_pool_ctrl_s51080000.mp4 (recorded by ali147_record_ctrl.py; wall secs from JOB start)
```

**CTRL was rendered by the driver, NOT by this Ralph loop.** It has no `request.api.json`, no `submitted_graph` request of ours, and no `p7\jobs\ali147_pool_ctrl_s51080000.*` record; `ali147_record_ctrl.py` wrote the log/objective. Its captured graph is `runs\ali147_pool_ctrl_s51080000\ali147_pool_ctrl_s51080000.api.json` (10,886 B, sha256 `21e47217d3d6ceda46b60ebab0a298db9016868cd27c1565c389d624ed72192a`).

**FIX1** — `runs\ali147_pool_fix1_s51080000\status.log` (607 B):

```
2026-10-22 16:00:02 CT UNLOAD LLM coding_swift15_iq3s_esp
2026-10-22 16:00:40 CT JOB start ali147_pool_fix1_s51080000 prompt_id=e6f88f11-c13a-4d12-8205-7c0e039e3e48
2026-10-22 16:14:58 CT JOB end ali147_pool_fix1_s51080000 ok secs=857.5 file=C:\AI\community\runs\ali147_pool_fix1_s51080000\ali147_pool_fix1_s51080000.mp4
2026-10-22 16:14:58 CT OBJECTIVE ok ali147_pool_fix1_s51080000 frames=481 audio=True dur=20.042 bytes=5841241 contact=...\ali147_pool_fix1_s51080000_stills_contact.png
2026-10-22 16:14:59 CT UNLOAD comfyui_auto (POST /api/models/unload)
```

**FIX5** — `runs\ali147_pool_fix5_s51080000\status.log` (607 B):

```
2026-10-22 16:18:13 CT UNLOAD LLM coding_swift15_iq3s_esp
2026-10-22 16:18:44 CT JOB start ali147_pool_fix5_s51080000 prompt_id=11eb97b4-a100-4207-a3ce-020db3b0567d
2026-10-22 16:30:31 CT JOB end ali147_pool_fix5_s51080000 ok secs=706.8 file=C:\AI\community\runs\ali147_pool_fix5_s51080000\ali147_pool_fix5_s51080000.mp4
2026-10-22 16:30:31 CT OBJECTIVE ok ali147_pool_fix5_s51080000 frames=481 audio=True dur=20.042 bytes=5705872 contact=...\ali147_pool_fix5_s51080000_stills_contact.png
2026-10-22 16:30:32 CT UNLOAD comfyui_auto (POST /api/models/unload)
```

**DIP** — `runs\ali147_pool_dip_s51080000\dip.log` (782 B) is the job log; **there is no `status.log`, no `objective.json`, no `.api.json` for DIP** (a `kind=dip` job goes through `scripts\dip_join.py`, not `run_graph_job.py`), so render secs = 0 (GPU) and the wall clock is the 17 s CPU encode:

```
2026-10-22 17:23:19 CT DIP start
2026-10-22 17:23:19 CT segment_frames [481, 481, 481]
2026-10-22 17:23:24 CT DIP base_reenc.mp4 ffmpeg_exit=0 frames=1443 audio=True dur=60.166667 bytes=35488827
2026-10-22 17:23:24 CT DIP contact C:\AI\community\runs\ali147_pool_dip_s51080000\base_reenc_stills_contact.png
2026-10-22 17:23:29 CT DIP dipblack.mp4 ffmpeg_exit=0 frames=1443 audio=True dur=60.166667 bytes=36068806
2026-10-22 17:23:30 CT DIP contact C:\AI\community\runs\ali147_pool_dip_s51080000\dipblack_stills_contact.png
2026-10-22 17:23:36 CT DIP dipwhite.mp4 ffmpeg_exit=0 frames=1443 audio=True dur=60.166667 bytes=38260910
2026-10-22 17:23:36 CT DIP contact C:\AI\community\runs\ali147_pool_dip_s51080000\dipwhite_stills_contact.png
2026-10-10 17:23:36 CT DIP end ok
```
(Last line reads `2026-10-22 17:23:36 CT DIP end ok` — transcribed exactly as printed; the date is 2026-10-22 in every line. Exact ffmpeg command: `runs\ali147_pool_dip_s51080000\ffmpeg_cmd.txt`, 2,255 B.)

**FIX4 (final, successful run)** — `runs\ali147_pool_fix4_s51080000\status.log` (610 B):

```
2026-10-22 20:08:29 CT UNLOAD LLM coding_swift15_iq3s_esp
2026-10-22 20:09:08 CT JOB start ali147_pool_fix4_s51080000 prompt_id=40a1e10d-f9e8-46b4-a774-c797c03af5ba
2026-10-22 20:59:13 CT JOB end ali147_pool_fix4_s51080000 ok secs=3004.9 file=C:\AI\community\runs\ali147_pool_fix4_s51080000\ali147_pool_fix4_s51080000.mp4
2026-10-22 20:59:15 CT OBJECTIVE ok ali147_pool_fix4_s51080000 frames=1433 audio=True dur=59.709 bytes=65791775 contact=...\ali147_pool_fix4_s51080000_stills_contact.png
2026-10-22 20:59:15 CT UNLOAD comfyui_auto (POST /api/models/unload)
```

**FIX4 (first run, the STUCK evidence)** — `C:\AI\community\p7\jobs\ali147_pool_fix4_s51080000.out.failed-20261022` (5,720 B), first and last lines:

```
2026-10-22 17:36:51 CT JOB start ali147_pool_fix4_s51080000 prompt_id=256f4f0f-ac8c-4dae-a2c6-bc10b9b59dce
2026-10-22 17:36:56 CT JOB error ali147_pool_fix4_s51080000 secs=5.1 [["execution_error", {... "node_id": "ext", "node_type": "MiniMaxH3Extender", "exception_message": "MiniMax H3 Extender: Ref2VA clip 1 is marked Validated but its disk cache is missing. Refusing to rerender a validated clip. Uncheck Validated explicitly if you want this clip rendered again.", "exception_type": "RuntimeError", ...
2026-10-22 17:36:56 CT OBJECTIVE FAIL ali147_pool_fix4_s51080000 JOB error
2026-10-22 17:37:01 CT JOB error ali147_pool_fix4_s51080000_redo1 secs=5.1 [...same exception...]
2026-10-22 17:37:01 CT OBJECTIVE FAIL ali147_pool_fix4_s51080000_redo1 JOB error
2026-10-22 17:37:07 CT JOB error ali147_pool_fix4_s51080000_redo2 secs=5.1 [...same exception...]
2026-10-22 17:37:07 CT OBJECTIVE FAIL ali147_pool_fix4_s51080000_redo2 JOB error
2026-10-22 17:37:07 CT STUCK ali147_pool_fix4_s51080000 objective failure after 2 redos - flagged for Derrick
```

## Per-arm detail

### CTRL — pool control (single 20.04 s chunk)
- `objective.json` (416 B) **flat** form, `ok=true`: `secs=809.7`, `frames=481`, `duration=20.041688`, `bytes=5781091`, `audio=true`, `blackfreeze=[]`, `sha256=1dc59ed4…`, `contact_sheet=…\ali147_pool_ctrl_s51080000_stills_contact.png`.
- My `ffprobe -count_packets` agrees: video `h264,768,1344,24/1,24/1,20.041667,481`; audio `aac,32000,2,20.041688,628`.
- mp4 sha256 `1dc59ed446e4cf1a5ecbfa18616a311b658d1acc281a3624974732373ba42fda`; contact sheet sha256 `9d97ecca9df312a0d9b997757d58c2f4daf15f10ba36f435fb9c48ddbe4930c6`.
- Scope/lineage: copy of the BASE graph at the native 481-frame length with `RandomNoise.seed` forced to 51080000 (`graph_diff.txt` 2 lines, in `runs\p7_r2_c3_pmot_full_pool\`), `window1 = 238/22` → 481 frames. Fairness: `runs\ali147_pool_ctrl_s51080000\fairness.txt`.
- **Rendered by the driver, not this loop** (see above). All later arms use it as their control.

### FIX1 — chunk-2 node swap (Ref2V form)
- Graph provenance: `request.api.json` 11,025 B sha256 `4d27cff7f055c37ce32986a46082adccd5aa99962fa7e7d39a36866dd03e3d49` = harness `ali147_pool_fix1_s51080000.api.json`, **byte-equal** → the graph that rendered is the authored graph.
- `graph_diff.txt` (3,198 B) shows exactly the four `c0` keys of the arm spec (node type, `vae`/`audio_vae` wiring, `length` 238→243, `ref_image_size` max→match, same `LoadImage` string, prompt 2693→3090 chars); `RandomNoise` untouched, seed 51080000.
- `objective.json ok=true`, 1 attempt, `attempts[0].secs=857.5`, `frames=481`, `dur=20.041688`, `bytes=5841241`, `audio=true`, `blackfreeze=[]`. Contact sheet sha256 `5738807d04ea48ec711ff87fded812bc79d2fd23059d71be577d7922947e7ed6`.
- Fairness: `runs\ali147_pool_fix1_s51080000\fairness.txt` — 21/21 nodes, prompt n-gram Jaccard 0.986, CLIPTextEncode 7080 = 7080 chars, seed 51080000 = 51080000, 481/481 frames, 24 fps, 20.042/20.042 s, 768×1344.
- vs CTRL: +47.8 s render (857.5 vs 809.7, **+5.90 %**), +60,150 B (+1.04 %). Numbers only.
- Verification record: `runs\ali147_pool_fix1_s51080000\PROOF.md` (4,828 B).

### FIX5 — scheduler test (steps 10 → 8)
- Graph provenance: `request.api.json` 10,884 B sha256 `0f268e9073fcf277a5c10e35c0416b159454c02d0c594c89bc4d77eb9e027ded` = captured `.api.json`, **byte-equal**.
- `graph_diff.txt` (720 B) = exactly 4 lines: the two scheduler nodes' `51080000_ksampler.10/3` → `.8/3` (+context). Nothing else; seed 51080000, 21 nodes, prompt node untouched (7,080 chars).
- `objective.json ok=true`, 1 attempt, `attempts[0].secs=706.8`, `frames=481`, `dur=20.041688`, `bytes=5705872`, `audio=true`, `blackfreeze=[]`. Contact sheet sha256 `63330ee51ba5ffd32ac11e9e21f8c6b217670b1b8b30697e3a19623102a50ef3`.
- Fairness: `runs\ali147_pool_fix5_s51080000\fairness.txt` (100 lines) — the required pass line `RESULT: scheduler test - one variable (steps 10 -> 8) on an identical graph` and the full `FAIRNESS PASS` block.
- vs CTRL: −102.9 s (706.8 vs 809.7, **−12.71 %**), −75,219 B (−1.30 %). **Render-time saving and byte-count only — no claim about seam/choppy motion: that is by-eye (Derrick) and no vision judge was used.**
- Verification record: `runs\ali147_pool_fix5_s51080000\PROOF.md` (6,200 B).

### DIP — CPU dip join at the two seams
- `result.json ok=true rc=0 note="dip_join rc=0"`, started 17:23:19, finished 17:23:36, `wall_min=0.3`, `budget_used_min=242.5` (cap 345 at that moment); `err.out` 0 B. **Render secs = 0**: no GPU generation, ffmpeg concat/dip only.
- All three outputs `768,1344,24/1` with **1443 packets** and `dur=60.166667`:
  - `base_reenc.mp4` 35,488,827 B sha256 `0f3579e349eba99e5d18ce910959d9b2608449e21ee08ae5bee33fe4d42ec6c1` (the no-dip control)
  - `dipblack.mp4` 36,068,806 B sha256 `10a80877735d61b764d5b7a07d3cad3af408fad026c00cd9e1008a5426cc395b`
  - `dipwhite.mp4` 38,260,910 B sha256 `4ece130b98afc4464cb3c2b08f0be9b6b066dad7bb33eade1a884f6b51365e26`
  - audio streams `aac,32000,2` 1,881 packets / 60.160000 s (container duration 60.166667 s — the aac padding noted in AGENTS; frame count is the authority).
- Contact sheets: base `207d712b372776c047e144f74b916c9b1f553312d14d7405402a7376942eccb1`, dipblack `fe1b80893a7a9442bc123a3f151a49d28fa341c30f74a58cd0554556b6eb9b33`, dipwhite `6ae28caca8466cf65528c570f7b178ad6dab740e9a362e23102d82c35ef636a6`.
- Seam positions (DIP): segment restarts at raw frames **481** and **962** (`segment_frames [481,481,481]`); the 12-out/12-in dips are applied there — seam/frame evidence in `runs\ali147_pool_dip_s51080000\PROOF.md` (10,553 B).
- Failure history: first run produced 1444 frames (`dur=60.192`) and `dip_join rc=5`; the fixed probe is `notes\dip_join_probe.py`, the fix line is documented in AGENTS (DIP_FIX `0f03d9a`). Old outputs `runs\...\failed-20261022\`, old job records `p7\jobs\ali147_pool_dip_s51080000.{out,err.out,result.json}.failed-20261022`.
- **DIP is not a 60 s render** — it is the same 1,443 rendered frames the BASE minute already has, re-cut with dissolves. The loop does not claim a 60 s generation from it.

### FIX4 — the full-minute Extender chain (the plan's headline test)
- Graph provenance: `request.api.json` 41,921 B sha256 `7530cf228c73bae7631b3a97b1c8770e56797318d1782925907b4738956dbf57`; captured `ali147_pool_fix4_s51080000.api.json` 41,919 B sha256 `46ea6ce34f74c8371dd6691481151a154b5777bfb1062952f903d1cd6e8955f5`; **`byte-prefix=True` with a 2-byte tail** — the harness strips the request's trailing CRLF, so the rendered graph is the authored graph (documented in `PROOF.md` 4.5/4.6).
- Clip grid: c0 = 243, c1–c5 = 260 raw (all satisfy `(frames−5) % 17 == 0`), `duration` = `round(frames/24, 6)` (10.125 / 9.916667 …), 1,543 raw − 5 seams × 22 context = **1,433 kept**, tol 24. The Extender honoured the grid: rendered 1433 = computed kept.
- Seam positions (raw-frame starts): **243, 481, 719, 957, 1195**. All five seams are sampled by the 35-tile contact sheet (frames 204–276, 444–516, 684–756, 924–996, 1164–1236); frames 1237–1432 are not sampled by any machine contact.
- `objective.json ok=true`, 1 attempt, `attempts[0].secs=3004.9` (= 50.1 min, matches `result.json wall_min=50.8`), `frames=1433`, `dur=59.709`, `bytes=65791775`, `audio=true`, `blackfreeze=[]`. `result.json ok=true rc=0`, `budget_used_min=327.1`, cap 390.
- mp4 sha256 `2cd0ed70067cfbe3182a43abefb20d1a4556b789b963f54adb0b53b49c0a299f`; contact sheet sha256 `f2d1f7971cd30622ed638479ca0a2b6f127a7821dddf94f26941ca530107d1de`.
- Fairness (vs the 20.04 s BASE chunks; no 481-frame control exists for this arm): `runs\ali147_pool_fix4_s51080000\fairness.txt` (16,349 B) — same pool reference identity (LoadImage `community/POOL_768x1344.png` 9cf9ff95…, required `fc4f4ea4…` is in the 6 r2v prompts), seed 51080000 on all 6 clips, steps 10, fps 24, same prompt text (segment prompts + their exact 6 continuations), `RESULT: FAIRNESS PASS` 4/4.
- Control comparison: the BASE minute is 1,443 frames in 3 jobs = 836.1 + 816.0 + 816.0 = **2,468.1 s** (`.out` `BATCH DONE total_secs=2468`); FIX4 is 1,433 frames in **one** job of **3,004.9 s** = 536.8 s / **+21.75 %** for 5 seams it does not pay for. Numbers only, no seam claim.
- Verification record: `runs\ali147_pool_fix4_s51080000\PROOF.md` (11,265 B); this iteration re-ran `notes\ali147_fix4_proof_verify.py` → `notes\ali147-fix4-proof-verify-20261022.txt` (17,747 B) = `ALL CHECKS PASS`.

## Objective-check coverage (all five arms)

| check | CTRL | FIX1 | FIX5 | DIP | FIX4 |
|---|---|---|---|---|---|
| frames (ffprobe `-count_packets`) | 481 ✔ | 481 ✔ | 481 ✔ | 1443 ×3 ✔ | 1433 ✔ (tol 24 vs 1443) |
| 768×1344 | ✔ | ✔ | ✔ | ✔ | ✔ |
| 24 fps | ✔ (24/1) | ✔ | ✔ | ✔ (`avg_frame_rate 8658/361` = aac-padding artifact, frame count authoritative) | ✔ |
| audio present | ✔ aac 32k stereo 628 pkts | ✔ 628 | ✔ 628 | ✔ 1881 | ✔ 1867 |
| no black / frozen frames | `objective.json blackfreeze=[]` | `blackfreeze=[]` | `blackfreeze=[]` | not applicable — no `objective.json` for a `kind=dip` job; the harness blackdetect+freezedetect chain is not run for DIP (evidence = `dip.log` + contact sheets) | `blackfreeze=[]` |
| contact sheet exists | ✔ 1,711,845 B | ✔ 1,715,915 B | ✔ 1,705,795 B | ✔ 3 sheets | ✔ 5,463,574 B, 35 tiles |
| seam coverage | no seams (single chunk) | no seams (chunk boundary is inside the graph) | no seams | 2 seams 481/962 covered by the 3 sheets + `ffmpeg_cmd.txt` | 5 seams 243/481/719/957/1195 all sampled by the sheet |

Contact-sheet coverage for 481-frame arms (`scripts\run_graph_job.py:45-52`): tiles at 0.5 s steps in ±1.5 s windows around 10/20/30/40/50 s → only frames **204–276** and **444/456/468/480** exist; **frame 0 is never sampled**, and frames 481–1432 exist only on FIX4/DIP. So "20 s arms are comparable to the 60 s arms at seams and endings" is **not** machine-satisfiable on the 20 s arms (single-chunk, 1.8 s of contact coverage, no second/third seam, no 60 s ending) — that is a review-surface fact for Max/Derrick, not a rendered result.

## Appendix — the reference-sheet arms (RS0-RS7, same plan, not part of the five rows)

| arm | output mp4 | bytes | duration | frames | render secs | contact sheet | failures |
|---|---|---|---|---|---|---|---|
| REFSHEET `ali147_pool_refsheet_s51080000` (chunk-1 node = `MiniMaxH3ReferenceToVideo`, `ref_image_1` = the start still) | `runs\ali147_pool_refsheet_s51080000\ali147_pool_refsheet_s51080000.mp4` | 5,733,637 | 20.041688 s | 481 | 902.7 | `…_stills_contact.png` 1,721,371 B (`c2d022ef…`) | none — `result.json ok=true rc=0`, 1 attempt, `blackfreeze=[]`; graph byte-equal to `request.api.json` (11,424 B, `97d1b140…`); `sbs_fix1_refsheet.mp4` is Max's (present, 19,649,768 B; RS7's tick recorded ffprobe `1536,1344,24/1,481` for it - not re-measured by this probe) |
| REFSHEET_B `ali147_pool_refsheet_b_s51080000` (same + `ref_image_2` = the RS016 portrait sheet, `ref_image_size` → `max`) | `runs\ali147_pool_refsheet_b_s51080000\ali147_pool_refsheet_b_s51080000.mp4` | 5,705,213 | 20.041688 s | 481 | 978.1 | `…_stills_contact.png` 1,773,478 B (`def7cbe0…`) | 1 refused request, no GPU spent: `ralph.log` `P7 job refused: bad id 'ali147_pool_refsheet_b_s51080000'` 18:46:35 (id regex); Max widened both `ralph.ps1` gates (`^ali147_pool_[a-z0-9]+(_[a-z0-9]+)?_s\d+$`), re-request accepted, render `ok=true rc=0`, 1 attempt, `blackfreeze=[]`; graph byte-equal to `request.api.json` (12,144 B, `5236bd38…`); `sbs_refsheet_refsheetb.mp4` (19,180,461 B) is Max's |

Reference-sheet inputs, measured in `notes\ali147-summary-20261022.txt` (PIL + sha256) — the start still and the approved source are **two different files, and no graph loads the approved jpg**:

| file | bytes | sha256 | PIL |
|---|---|---|---|
| `C:\Users\derek\5slock\approved_characters\POOL\COND_POOL_BIKINI_PORTRAIT.jpg` (approved canon source, the required baseline) | 881,929 | `fc4f4ea4e3d3befb4dd50cc32abf9e71bfbbae37d153fe56bd51132556e0bfaa` | (1536, 2752) RGB JPEG |
| `C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input\community\POOL_768x1344.png` = every graph's `img` LoadImage `community/POOL_768x1344.png` (the start still) | 1,354,030 | `9cf9ff95f2d6f2fb3882219a8d98995b673e78a80001d7a41af1755cc918d075` | (768, 1344) RGB PNG |
| `C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input\community\RS016_portrait_1152x2016.png` = REFSHEET/REFSHEET_B `sheet` LoadImage → `c0 ref_images.ref_image_2` | 2,314,891 | `da0b6a0b0c313e468cb225c7ca0e46dd97321722764aee9d7e76c7297b5caa4a` | (1152, 2016) RGB PNG |

The derivation chain is R0's logged conclusion, not re-derived here: R0 established `cond_lock_base.png` (512×896) → `POOL_768x1344.png` (768×1344, 1,354,030 B, `9cf9ff95…`) as the active pool reference, with the 1536×2752 `COND_POOL_BIKINI_PORTRAIT.jpg` (`fc4f4ea4…`) as the same subject's approved source; RS1 established `RS016_portrait_1152x2016.png` is a **single low-resolution portrait panel, not a panels strip** (that is why RS1 is the low-res panel, and why the sheet row in the graph is one portrait). `approved_characters\POOL\` contains `CHARACTER.md` (+dated `.bak`s), `COND_POOL_BIKINI_PORTRAIT.jpg`, `POOL_face_crop_250.png`, `POOL_ref_1.png` (the subject-reference sheet the r2v prompts name). Details in the RS tick texts, `notes\ali147_refsheet_rs4_verify.md`, `notes\ali147_refsheet_b_rs6_verify.md`. **No FaceEmbedDistance / identity-similarity number exists for any arm** (`grep -i faceembed C:\AI\community\runs` = 0); identity comparison is by-eye on the contact sheets (Derrick).

## Failures, redos, STUCK and `[!]` items (the whole loop)

- **DIP_FIX** `[!]` → resolved: `dip_join.py` `-r 24` produced 1,444 packets → `ok=false`; fixed to `-frames:v = probed sum` (1443), `dip_join rc=0` on re-run.
- **DIP_PROOF** `[!]` (logs-only decision) → resolved: "use 3×20 s renders + the dip test; no 60 s render requested (DIP is 60 s of the same 1,443 frames, no 60 s generation by the loop)".
- **FIX4 (first run)**: 3 × 5.1 s failures + `STUCK … flagged for Derrick`, `rc=5`. Root cause `"validated": true` = the UI clip-card checkbox with no disk cache (`extender.py:6104-6107, 6317-6323`). Decision line `DIP_PROOF`/`FIX4` decision recorded; `FIX4_GRAPH` applied the edit (`validated true→false`, `duration = frames/24` from the real frame counts), re-render passed.
- **RS3** `[!]` (sheet placement, no copy in a read-only task) → resolved by measurement (the sheet was already in `ComfyUI\input\community\`).
- **RS4 / RS6** `[!]` for `sbs_*.mp4` / frame-0 stills and a `ralph.ps1` id-regex refusal → resolved: the id regex was widened by Max (`ralph.ps1.bak-20261022-idregex`), and `find runs -name sbs_*` now returns exactly two files, both Max's: `runs\ali147_pool_refsheet_s51080000\sbs_fix1_refsheet.mp4` 19,649,768 B and `runs\ali147_pool_refsheet_b_s51080000\sbs_refsheet_refsheetb.mp4` 19,180,461 B. Frame-0 stills are still absent (no Forge/hstack path produces them).
- **Renders**: no duplicate mp4 anywhere — `find runs -name "ali147_pool_*.mp4"` returns exactly 6 paths (CTRL, FIX1, FIX4, FIX5, REFSHEET, REFSHEET_B), one per arm, and `uniq -d` is empty. DIP's outputs are named `base_reenc/dipblack/dipwhite.mp4`, so they are outside that pattern.
- **No JOB error / CLIP_SKIP / STUCK in any final record**: `grep -E "JOB error|CLIP_SKIP|STUCK"` over the live `p7\jobs\*.out` matches only the archived `ali147_pool_fix4_s51080000.out.failed-20261022`.
- **P7 budget** (the live file is `C:\Users\derek\5slock\ralph-community\logs\p7_budget.json` — there is **no** `C:\AI\community\logs\p7_budget.json`, so any report that cites that path is quoting a file that does not exist): live content at 21:3x CT is `{"used_min": 327.1, "jobs": 23, "cap_min": 390, "job_cap": 27, "updated": "2026-10-22T20:59:15"}`. The per-job snapshots in the `result.json` files climb 229.6 (FIX1, cap 345) → 241.9 (FIX5, cap 345) → 242.5 (DIP, cap 345) → 259.3 (REFSHEET, cap 390) → 276.3 (REFSHEET_B, cap 390) → 327.1 (FIX4, cap 390), i.e. 23 jobs: 22 pre-existing P7 jobs plus these 6 (FIX4's STUCK run is not counted). Every job was under the cap; no `refused: budget` line exists in `logs\ralph.log`.
- **Data-provenance gaps for the report (stated, not papered over).** Files that the `[x]` tick texts cite as written evidence are **not on disk** at the time of writing (verified by `os.path.exists` in the probe; their `__pycache__` entries survive for the scripts): `notes\ali147_REPORT_rs7.md` (the RS7 report), `runs\RS0_lowres_resolution_probe\`, `runs\RS1_lowres_pool_sheet\` (so `PROOF.md`/`probe.py`/`objective.json` for R0/RS1 are gone), `notes\ali147_rs1_lowres_build.py`, `notes\ali147_rs1_lowres_selfcheck.py`. Everything they asserted is re-measured directly here (the image table above, the graph comparisons, the ffprobe rows), so the summary does not depend on the missing files; the gaps are stated so nobody reads the tick texts as fresh evidence. Also absent: `runs\ali147_pool_ctrl_s51080000\fairness.txt` and `…\PROOF.md` (CTRL is a driver arm) — CTRL's scope evidence is `runs\p7_r2_c3_pmot_full_pool\graph_diff.txt` (2 lines) + `graph_diff.n3v.txt` (5 lines) + the R-tick texts. `p6_variants.ps1:319` on this machine calls `run_graph_job.py` (no hstack path), which is why no `sbs_*` file is a Forge file.
- **Items NOT closed by this summary** (owner Max): the by-eye review of every arm (Derrick's KEEP), the PV2-4 `contact_review.md` / PV2-5 `by_eye_verdicts.md` (held at `[ ]` per Max's 2026-10-22 stop), U160 cards U86-U96, and the Linear post of this summary.

## Method notes (what this loop is and is not)

- Single-variable comparisons only: CTRL→FIX1 (chunk-2 node type), FIX1→FIX5 (steps 10→8), FIX1/FIX5/CTRL (the 20 s pool control), BASE-minute (the 60 s control for DIP and FIX4). Everything else is byte-identical per the graph diffs above.
- Every number here was re-measured this iteration from the files on disk (probe outputs in `notes\ali147-summary-20261022.txt` and `notes\ali147-summary-api-20261022.txt`); nothing is inherited from a vision judge, and no `p6_review` / `qwen3vl_judge` / contact-sheet scoring pipeline was called (the 2026-10-22 Max Architect decision in AGENTS: review = contact sheet + objective checks).
- **METHOD_ONLY on every arm. KEEP is Derrick's only.** No render was selected, kept, ranked, scored or quality-redone by Ralph/Forge; no quality REDO was requested (the only REDOs are the harness's own two automatic `run_graph_job` redos inside the failed FIX4 record).

Ralph 2026-10-22 21:40 CT, iteration 05 (edit 2: budget file, identity table, sbs sizes, missing-evidence list). METHOD_ONLY; KEEP is Derrick's only.
