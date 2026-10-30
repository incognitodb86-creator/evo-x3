# Terrace A/B/C handoff — 2026-10-28 (stop point: pi restart)

Cell family: `terrace_dom` / start image `community/TERRACE2_768x1344.png` · 243 f @ 24/1 · 768×1344 native ·
beta7 `10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors` · seed **51083002** for arms A/B/B2 (v2 used 51083003) ·
prompt 13,128 chars, byte-identical across arms · VSA keep_percent 10 · shift 12/3 · euler · adults-only guard on.
Briefs: `ab_q4_q5_brief_2026-10-28.md`, `2026-10-28-max-brief-B-addguide.md`.

## State: done, with Max's review scores

| Arm | Cell | Graph state | Result | Max score |
|---|---|---|---|---|
| **A** | `runs/terrace_dom_q4_20261028_s51083004` | native single-pass, 8 steps @1.03 MP | 360.1 s, raw 4,377,514 B / 3459 kbps | **4/10** |
| **C** | `runs/terrace_dom_c12_20261028_s51083006` | same graph, steps 12 | 480.2 s, raw 4,587,989 B / 3625 kbps | **5/10** |
| **B** | `runs/terrace_dom_q5_20261028_s51083005` | 3D-latent-upscaler two-pass, **MISWIRED** (below) | 240.1 s, raw 11,560,944 B / **9135 kbps**, burned | **3.5/10** |
| **B2** | `runs/terrace_dom_q5guide_20261028_s51083007` | **graph fixed to LokkenJP's published two-pass + the #74 Add Guide change** | 240.1 s, raw 4,520,700 B / 3572 kbps, final 5,770,214 B (crf-18 native, no RTX) | **6/10** |
| v2 | `runs/terrace_dom_v2_20261028_s51083003` | earlier `MiniMaxH3LatentUpscaleCombined` two-pass (seed 51083003) | 300.1 s, 3,071,104 B | — |

B's burn was two miswires in my graph, not the model: `SplitSigmas(step 4)` truncated pass 1 to 4 of 8 steps, and
pass 2 used `ManualSigmas 0.9035→0.0` = **denoise ≈0.9 at full res** (a single-pass r2v template as a refine).
LokkenJP's published `H3_Turbo_2Pass_ErosMax_b7_simple_v1.json` (SHA256 `05FA6B2A…67C57E7`) uses the **full 8-step
schedule** (no SplitSigmas) + **`BasicScheduler(beta, 3, denoise 0.4)`**, decodes audio from the **pass-1** latent,
and sets `enable_temporal_chunking=true`. Full node-by-node diff: `notes/2026-10-28-B-graph-vs-lokken.md`.
B2 DONE record: `notes/2026-10-28-B-addguide-DONE.md`. De-liverables verified on `/pi-drop/` (same sizes).

## B2 graph path (the one to branch from)

- **`C:\AI\community\runs\terrace_dom_q5guide_20261028_s51083007\request.api.json`** (26 nodes, what the runner submits)
- `…\build_graph.py` = the reproducible builder (asserts every constant, refuses to write on drift, static-validates links + reachability). Node ids: `c0` (ref_image_size **max**), `ag0`/`ag1` `MiniMaxH3AddGuide`, `s0_sched` simple/8/1.0 → **full** schedule, `p2sched` **beta/3/0.4**, `lsu3` conv_v1_bf16 ×2.0 **chunking true**, `dec_a ← s0_sep:1`, single `ksel` euler for both passes, `dec_v ← s1_samp:0`.
- Geometry kept: 384×672 (0.258 MP) × **2.0** = exactly 768×1344. The published `ResolutionSelector` 0.3 MP + `mode "megapixels"` 1.0 rounds to ~768×1408 → off-canvas, so it is not copied.

## Open next tests (not started; GPU is IDLE)

**T1 — B2 without the Add Guide** (isolate what the #74 node contributed; same seed 51083002, same prompt).
Build = copy B2's `request.api.json`, then exactly: delete `ag0`, `ag1`; `s0_guide.conditioning ← ["c0",0]`;
`s1_guide.conditioning ← ["c0",0]`; `save.filename_prefix ← community/<newtag>/<newtag>`.
**Keep `ref_image_size "max"`** (pure Add-Guide ablation). If Max wants the whole #74 fix ablated instead, one extra line:
`c0.ref_image_size ← "match"`. Say which in the note — do not guess silently.

**T2 — larger first pass** (B2 recipe, bigger low-res base, same 768×1344 canvas).
The multiplier must land exactly on the canvas: k=2 (384×672, current) → **k=1.5 = 512×896 (0.459 MP)** is the only
step up that keeps integers on a 32 grid (k=1.25 → 614.4, breaks). Set `c0.width 512`, `c0.height 896`, keep
`lsu3` `mode "scale by multiplier"` **1.5**, `ag0/ag1` untouched. Estimated cost ≈ 8×~27 s + 3×~45 s ≈ **~380 s**
(over arms A 360.1 s / B2 240.1 s); keep `-Timeout 3600`.

## Exact next command (T1, arm id 08)

```
# 1. build the ablated graph (new dir, copy B2's builder, point SRC at B2's request.api.json, apply T1's 4 lines)
#    run it with: & "C:\AI\director\.venv\Scripts\python.exe" -u <dir>\build_graph.py   (writes request.api.json)
# 2. render in ONE GPU window:
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\AI\community\scripts\gpu_window.ps1" `
  -Dir "C:\AI\community\runs\terrace_dom_q5noag_20261028_s51083008" `
  -Tag "terrace_dom_q5noag_20261028_s51083008" -Frames 243 -Timeout 3600
# 3. post (no RTX arg = native crf-18 of the raw, the brief's rule):
& "C:\AI\director\.venv\Scripts\python.exe" -u "C:\AI\community\scripts\finalize_encode.py" `
  "C:\AI\community\runs\terrace_dom_q5noag_20261028_s51083008" "terrace_dom_q5noag_20261028_s51083008"
# 4. upload + verify sizes:
& "C:\AI\director\.venv\Scripts\python.exe" "C:\AI\community\scripts\pi_qnap.py" put "<dir>\<tag>_raw.mp4"   "/pi-drop/<tag>_raw.mp4"
& "C:\AI\director\.venv\Scripts\python.exe" "C:\AI\community\scripts\pi_qnap.py" put "<dir>\<tag>_final.mp4" "/pi-drop/<tag>_final.mp4"
& "C:\AI\director\.venv\Scripts\python.exe" "C:\AI\community\scripts\pi_qnap.py" ls /pi-drop/ | Select-String "<tag>"
```

## Rules for the next session (hard-won today)

PowerShell tool only, **never bash**; one GPU window per render via `gpu_window.ps1` (it handles the lock + `GPU_LOCK_DRIVER_PID`);
`gpu_guard.ps1` must say IDLE first — it does now, lock released, comfyui_auto unloaded. No new scripts unless a step fails
(`probe_full.py` reads live node specs; `objinfo_has.py` checks registration). Prompt bytes and seed are constants — builders
assert them. `MiniMaxH3AddGuide`: `vae` is **required** when an image is connected; `latent` must be the AV latent entering the
sampler (it takes the canvas from it); `frame_idx` default 0. `verify_cell.py` from another cell = false-alarm FAILs; run the
per-cell `motion_check.py` instead. Bitrate at fixed crf = high-frequency-energy proxy, **not** a quality score; motion floors
are per-path so compare only inside a cell — **Derek's watch is the judge**. Copy notes with
`[IO.File]::ReadAllText($src,[Text.Encoding]::UTF8)` + `WriteAllText(...,UTF8Encoding($false))` (PS 5.1 `Get-Content -Raw` mangles UTF-8).
Then stop and report; no follow-up renders in the same window.
