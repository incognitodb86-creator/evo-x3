# ALI-163 R4F - face identity research + machine similarity table (2026-10-23, Forge)

Task line: `R4F FACE RESEARCH` in ralph-community\TASKS.md. No GPU, no vision judge, no video watched.
Everything below is (a) community sources fetched with `curl.exe` GET, (b) a CPU face-embedding
measurement, and (c) this file. PACING: this pass wrote (a)+(b) and the ranked fix list; the
prompt/reference audit (`notes\hc_prompt_face_audit_20261023.md`) lands in the next pass.
Step (d) IS done this pass: TASKS.md now has task line **R4G** (apply F1-F5 onto R6-R9) and the R6-R9
lines were rewritten from "the HCn still + its sheet as references" to "the HCn still as the ONLY
reference [R4G FACE FIX ...]", plus a PROGRESS line on R4F.

## Method (the metric, so the numbers are reproducible)

* Detector/embedder: insightface **SCRFD-10G** (`scrfd_10g_bnkps.onnx`) + **ArcFace glintr100**
  (`glint360k_r100`/glintr100 512-d), `onnxruntime` **CPUExecutionProvider** only, venv
  `C:\AI\qa_gate_venv` (never the ComfyUI `.venv` = GPU torch). Preprocessing matches insightface
  (blob mean 127.5, scale 1/128, 112x112 aligned crop from the 5 kps).
  Sources: https://raw.githubusercontent.com/deepinsight/insightface/master/detection/scrfd/README.md
  (SCRFD, WIDERFace table), model-zoo page saved as notes\web\gh_insightface_modelzoo.html (200,230 B).
* Frame extraction: ffmpeg (AGENTS.md build) from the finished mp4s into notes\face_r4f\ as PNG.
  7 evenly spaced frames per new clip (r1/r2 at 0/40/80/120/160/200/240 of 243; c1/c2 at
  0/80/.../480 of 481) + 5 frames of two older no-sheet reference clips.
* Scripts: notes\hc_r4f_facelib.py (SCRFD/ArcFace ONNX wrappers), notes\ali163_hc_r4f_face.py
  (the anchor/assignment/drift pass -> face_r4f\r4f_table.txt + r4f_metrics.json),
  notes\ali163_hc_r4f_calib.py (the pick-vs-sheet control pass -> face_r4f\r4f_calib.txt).
* Anchoring: for each woman the anchor = mean of her per-woman Klein sheet's top face embeddings;
  each frame face is assigned to the woman whose anchor scores higher (a "swap" = the other
  woman's anchor wins that frame). Numbers are **cosine of 512-d ArcFace embeddings**, not a
  human-grade score: at these box sizes (150-200 px, see T3) a same-person pair does NOT reach the
  clean-face 0.4-0.6 region, so read the numbers as **ranked/relative** against the controls.
* Controls that make the numbers readable: pick->own-sheet (the identity chain ceiling),
  pick->other-woman-sheet (the cross-woman floor), sheet(w1)->sheet(w2) and
  sheet(pickA)->sheet(pickB) (pollution baselines).

## (b) Similarity table

### T1 - the identity chain pick -> sheet -> video (per woman, cos)

| chain link | HC1 w1 (blonde, BD004) | HC1 w2 (dark, BD004) | HC2 w1 (blonde, BD007) | HC2 w2 (dark, BD007) |
|---|---|---|---|---|
| pick face -> own sheet (mean-of-top4) | 0.431 | 0.369 | 0.217 | 0.240 |
| pick face -> own sheet (largest face) | 0.377 | 0.466 | 0.266 | 0.242 |
| pick face -> OTHER woman's sheet (floor) | 0.181 | 0.009 | 0.113 | 0.039 |

Cross-sheet controls (same faces, different women / different picks, largest-face anchor):

| pair | cos | reading |
|---|---|---|
| HC1_w1 sheet vs HC1_w2 sheet (same pick, different women) | 0.411 | two different women |
| HC2_w1 sheet vs HC2_w2 sheet | 0.543 | two different women |
| **HC1_w1 sheet vs HC2_w1 sheet (different picks, both "the blonde")** | **0.692** | two *unrelated* women score higher than a pick scores to its own sheet |
| HC1_w2 sheet vs HC2_w2 sheet | 0.540 | ditto (both dark-haired) |
| HC1_w1 vs HC2_w2 / HC1_w2 vs HC2_w1 | 0.522 / 0.400 | hair-group, not person |

Faces found inside each per-woman sheet (SCRFD thr 0.4, 768x1344 input):
HC1_w1 **2** faces (areas 66002, 15700 px); HC1_w2 **4** (86640, 50009, 14747, 8539);
HC2_w1 **4** (50091, 21068, 13548, 9185); HC2_w2 **6** (72742, 8161, 6693, 5752, 5466, 5377).
Intra-sheet face cosines: HC1_w1 0.639; HC1_w2 0.693/0.589/0.720/0.007/0.106/0.048;
HC2_w1 0.589/0.401/0.313/0.207/0.164/0.058; HC2_w2 0.626/0.312 and 13 pairs at 0.37..-0.049.
=> every "per-woman" sheet is a **multi-face** reference, and the small panels are only weakly the
same person as the big panel (several < 0.2).

### T2 - clip frames vs the start still (pick) and vs the sheet, per woman (median over frames)

| clip (id, len) | w1 vs PICK | w2 vs PICK | w1 vs SHEET | w2 vs SHEET | frames with a face |
|---|---|---|---|---|---|
| r1 ali147_pool_hc_r1_s51130001, 243 f, sheeted | 0.216 | 0.156 | 0.198 | 0.196 | 7/7, 7/7 |
| r2 ali147_pool_hc_r2_s51130002, 243 f, sheeted | 0.242 | 0.236 | 0.286 | 0.228 | 6/7, 6/7 (f80 = 0 faces) |
| c1 ali147_pool_hc_c1_s51100001, 481 f, no sheet | 0.250 | 0.223 | 0.096 | 0.212 | 7/7, 7/7 |
| c2 ali147_pool_hc_c2_s51100002, 481 f, no sheet | 0.249 | 0.153 | 0.128 | 0.135 | 7/7, 7/7 |
| old r1 arm, 157 s no-sheet (baseline) | 0.218 | 0.118 | 0.105 | 0.101 | 5/5, 5/5 |
| old r2 arm, 157 s no-sheet (baseline) | 0.197 | 0.117 | 0.075 | 0.184 | 5/5, 5/5 |

Per-frame means with the swap counter (r4f_table.txt, mean-of-top4 anchors):
r1 w1 0.180 (3 swaps), r1 w2 0.170 (3), r2 w1 0.357 (1), r2 w2 0.313 (3),
c1 w1 0.127 (7 swaps), c1 w2 0.236 (0), c2 w1 0.141 (3), c2 w2 0.178 (2),
old r1 w1 0.138 / w2 0.117, old r2 w1 0.328 / w2 0.224.

Reading of T1+T2:

1. **The chain is broken at the SHEET, not (only) at H3.** A pick scores 0.22-0.47 against its own
   Klein sheet, while sheets of two *unrelated* women score 0.69 (blonde) / 0.54 (dark) against each
   other. The Klein 9B sheet pass re-draws a hair-group prototype face, so the sheet ref *injects a
   Klein prior* that is closer to the other pick's sheet than to the approved woman. The sheet refs
   are the identity problem, before H3.
2. **The sheet ref did not buy measurable identity in the clip.** The sheeted 243 f clips (r1 0.156-
   0.216 vs pick) are not better than the no-sheet 481 f clips (c1 0.223-0.250, c2 0.153-0.249);
   they are flat/worse. So the current sheet wiring (pick + 2 multi-view sheets on c0, 2 sheets on
   c1) costs time and does not raise pick similarity.
3. **Faces in the clips are the same size as in the pick** (T3), so "the face got small" is not the
   story; the face that is there is a *different face*. Small boxes do cap how high a cosine can go,
   which is why only the ranked/relative reading is used.
4. **w2 (the dark-haired woman) is consistently the loser**: pick->sheet 0.369/0.240, clip vs pick
   0.156 (r1) / 0.153 (c2) / 0.118 (old r1). The w1-vs-w2 assignment flips a lot in r1 (3 swaps both
   women), i.e. the two women blur into each other in the pair clips.

### T3 - face box size (px, and % of frame) - measured, no vision judge

| item | image size | face box (WxH px) | face area | % of frame |
|---|---|---|---|---|
| HC1 pick (BD004) face0 / face1 | 1376x768 (1.057 Mpx) | 175x150 / 126x163 | 26271 / 20542 | 2.5% / 1.9% |
| HC2 pick (BD007) face0 / face1 | 1376x768 | 134x204 / 186x145 | 27289 / 26976 | 2.6% / 2.6% |
| HC1_w1 sheet (1152x2016, 2.32 Mpx) largest face | 1152x2016 | area 66002 | 66002 | 2.8% |
| HC1_w2 sheet largest face | 1152x2016 | area 86640 | 86640 | 3.7% |
| r1 frames w1 / w2 (median of 7) | 1344x768 (1.032 Mpx) | 129x181 / 133x179 | mean 24124 / 24652 | 2.3% / 2.4% |
| r2 frames w1 / w2 (median of 7) | 1344x768 | 133x189 / 129x192 | mean 26101 / 25770 | 2.5% / 2.5% |
| c1 frames w1 / w2 | 1344x768 | 123x164 / 141x171 | mean 20576 / 24689 | 2.0% / 2.4% |
| c2 frames w1 / w2 | 1344x768 | 124x146 / 125x144 | mean 18704 / 18846 | 1.8% / 1.8% |

So: pick faces 1.9-2.6% of frame, sheet faces 2.8-3.7%, clip faces 1.8-2.5% - the clip faces are
the same order as the pick faces; identity loss is not a framing loss.

## (a) Community sources on H3 identity (fetched 2026-10-23, byte counts proved)

1. https://raw.githubusercontent.com/tritant/ComfyUI_MiniMax_H3_Extender/main/README.md (21,826 B,
   saved notes\web\ext_readme.md). Quoted: L379-392 "When using image references, it is strongly
   recommended to place a `subject_definitions` block at the **beginning of every clip prompt** ...
   `<Picture 1>` is the reference image defining the exact visual appearance, **identity, face**,
   hairstyle, body proportions, clothing, accessories, and overall look of `<Subject 1>` ...
   `<Subject 1>` is the **exact same woman** shown in `<Picture 1>`." L245 "`<Picture 1>` defines the
   new character identity". L44 "**Choose Ref** lets you pick any frame from the source video and use
   it as a normal `<Picture N>` reference, useful for **preserving character identity** when the end
   of the source video does not show the subject clearly."
2. https://raw.githubusercontent.com/Smite79/MiniMax-H3-LongVideos/main/README.md (40,528 B,
   notes\web\longvid_readme.md). Quoted: L458-461 "A person's picture always goes in **cropped to
   their face and hair** (found with DWPose), so their clothes come only from the words ... and says
   when no face could be found and the whole picture went in." L174-177 "A reference picture shows
   its person in the clothes they had on, and H3 copies what it sees, print and all, back onto them.
   So the picture goes in cropped to their face and hair ... once a garment is off the shot also says
   the picture is for their face and hair only." L436-437 "Once a person is held, their own picture
   ... is **left out of shots that start on a frame they are already in**." L350 "A beat that sets
   the camera's framing (*close-up*, *the camera frames her face*) always holds only its own people."
   L566-567 (few-step speed LoRA: 4step/turbo/lightning/distill/DMAD/FlashGen, L455) "FastH3 ...
   **gets reference pictures only where nobody can be drawn twice**". L621 "Denoise is fixed at 1.0:
   partial denoise desyncs the joint audio/video schedule."
3. https://raw.githubusercontent.com/ttulttul/ComfyUI-Minimax-H3-Continuation/main/README.md
   (5,483 B, notes\web\cont_readme.md): **no** face/identity/reference guidance at all (grep for
   reference|identity|face = 0 hits) - the continuation packs defer identity to the prompt+refs.
4. https://docs.comfy.org/tutorials/video/minimax/minimax-h3 (547,161 B,
   notes\web\comfy_h3_tutorial.html): "Reference-driven generation: **Lock identity**, style, motion,
   camera, or voice from references" (the official framing: refs lock identity).
5. https://huggingface.co/TenStrip/10Eros-Max/discussions/63 (294,656 B, notes\web\hf_eros_d63.html):
   the model card's own subject block wording: "`<Subject 1>` (appears in [Shot 1]): **fully_preserved
   - her face, hair, clothes, bone structure are exactly as in `<picture 1>`**; `<Subject 2>` ...
   exactly as in `<picture 2>`; `<Audio 1>`: reference - its vocal timbre guides the dialogue
   delivery of `<Subject 1>`".
6. https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/28 (240,710 B, notes\web\hf_h3_d28.html):
   the length thread R1 used (5 s / 124 f); page body is client-rendered, so only the header/meta and
   the R1-quoted snippet are usable - logged, no new identity claim taken from it.
7. https://civitai.com/api/v1/models/2967166 (10,035 B), /2860061 (62,558 B), /2833322 (519,296 B)
   (notes\web\civ_*.json): the three H3 Ref2VA workflow pages named in the task, fetched as JSON.
   Full-text mining of their descriptions is the next pass's job (the files are on disk); nothing is
   claimed from them here.
8. https://raw.githubusercontent.com/deepinsight/insightface/master/detection/scrfd/README.md
   (8,883 B) + https://raw.githubusercontent.com/deepinsight/insightface/master/recognition/arcface_torch/README.md
   (18,134 B) + https://github.com/deepinsight/insightface/wiki/FAQ (390,883 B, notes\web\if_wiki_faq.html):
   the metric's own provenance (SCRFD WIDERFace accuracy table, glintr100 training/eval, FAQ model zoo).
9. https://raw.githubusercontent.com/Fannovel16/comfyui_controlnet_aux/main/README.md (21,894 B,
   notes\web\cnaux_readme.md): DWPose estimator is already documented here (the face+hair crop method
   Smite79 uses), i.e. a face-crop reference is a node-chain thing, not a model download.

Fetch failures, logged, not retried: `https://www.reddit.com/r/StableDiffusion/comments/1dfw17v.json`
(403, reddit blocked for this client), `https://raw.githubusercontent.com/Gourieff/comfyui-reactor-node/{main,master}/README.md`
(404 both), `.../lkbb0216/MiniMax-H3-Prompt-Guide/main/README.md` (404),
`.../deepinsight/insightface/master/python/README.md` (404). ReActor/InstantID/PuLID/FaceDetailer
READMEs could not be fetched, so the face-swap post-pass option is listed below as **unverified +
needs download**, never as a chosen fix.

## Ranked fix list (each: source, expected effect, cost, needs-download)

| # | fix | source | expected effect (from T1/T2) | cost | download |
|---|---|---|---|---|---|
| F1 | **Stop feeding the Klein multi-view sheets as identity refs.** Keep the approved pick as `<Picture 1>`; drop the sheet refs from c0 and c1 (R6-R9). | ext_readme L379-392/L245 (one ref per subject); T1: sheet(w1) vs sheet(other pick) 0.69 > pick vs own sheet 0.22-0.47; T2: sheeted clips are not better than no-sheet clips | removes the Klein prior face that is closer to the other woman's sheet than to the woman; restores the only asset proven to carry her face | 0 GPU min saved on c0 refs x2 (+ a few % render time) | **no** |
| F2 | **One face per reference image.** No sheet = no 2-6 faces per ref; for pair picks both subjects bind to the single pair pick, and the pair pick's own faces are the two anchors. | longvid L458-461 + L566-567 (refs only "where nobody can be drawn twice", and our run is beta6 8-step TURBO = the few-step case); T1 intra-sheet cosines 0.007-0.106 on the small panels | fewer face collisions; less w1/w2 swapping (r1 had 3 swaps) | 0 | **no** |
| F3 | **Rewrite subject_definitions to the extender/card wording** on BOTH chunks: "...exact visual appearance, identity, **face**, hairstyle, body proportions ... of `<Subject 1>`" + "`<Subject 1>` is the exact same woman shown in `<Picture 1>`", restated at the top of every clip prompt; keep the per-woman binding in c1 too. | ext_readme L379-392, hf_eros_d63 quote | the model is told to preserve face/bone structure, not just "the woman in the picture"; the binding survives into the extension chunk (that is where r1/r2 drift most) | 0 (prompt text only) | **no** |
| F4 | **Say the ref is for face and hair only**, and keep garment words out of the reference binding. | longvid L174-177 | stops the pick's clothes/print being painted back on in a hardcore scene, which is what makes it read as "not her" | 0 | **no** |
| F5 | **Add a face-framing beat** in c0 beat 1 and c1 ("the camera frames her face in close-up", per woman, one beat each) so the face occupies more pixels for the rest of the clip. | longvid L350; T3 (clip faces already ~2% of frame; a close-up beat raises face pixels) | raises both the human match and the measurable cosine; audio stays in the same sound line | 0 | **no** |
| F6 | **Do not touch denoise/shift/cfg.** Keep denoise 1.0 / cfg 1 / shift 10/3 / euler / 10 steps. | longvid L621, L620 | rules out the settings as the cause; nothing to change | 0 | **no** |
| F7 | **Per-chunk identity hand-off (needs a node UI, not a graph): "Choose Ref"** = a frame of the previous chunk where the face is clear becomes `<Picture N>` of the next chunk. | ext_readme L44 | the community answer for multi-chunk drift; in our single-job graph it can only be done by a second job (chunk 0 -> pick a frame -> request chunk 1), so it is a **2-job** plan: cost = 2 requests per clip + 1 job slot each | 0 | **no** |
| F8 | **A face-and-hair crop of the pick as `<Picture 2>`** (the single most-cited community practice). | longvid L458-461; cnaux DWPose | T1 says the pick is the only clean identity source; a crop of the pick's own face (250-400 px) would raise the ref face to ~4x the pixels of the pick's face in a 2-woman frame | CPU PIL crop, ~0 GPU min | **no download**, but the batch rule says no crop without Derrick, and writing a derived image into ComfyUI\input is outside my write list -> **[!] needs Derrick/Max sign-off** |
| F9 | Face-swap / face-restore post pass (ReActor, FaceDetailer, PuLID/InstantID-style for video). | READMEs 404'd (see fetch failures) | cannot be evaluated from a source I could fetch; on this chain it also needs new custom nodes + models (insightface pack / PuLID / IPAdapter) | +GPU pass | **YES - needs install + model download** (list: comfyui-reactor-node, inswapper_128.onnx, FaceDetailer in comfyui_controlnet_aux, IPAdapter/PuLID) |
| F10 | H3 identity LoRA (e.g. H3-Anti-Burn-LoRA and identity LoRAs). | notes\hc_redo_research_20261023.md:198 (https://huggingface.co/Imagineer13/H3-Anti-Burn-LoRA) | a LoRA whose timestep layers were built for another checkpoint's curve is explicitly warned against with a few-step speed LoRA (longvid L455, L566) and our model IS 8-step TURBO | +download | **YES** |

Top fix that is applicable with **no download, no new node, no install** = **F1 + F2 + F3 + F4 + F5**
(applied to R6-R9 as a set, they are all graph/prompt-only). F8 is the strongest single change by the
data but needs a Derrick-approved face crop; F9/F10 need downloads. Step (d) of the task line is done
in TASKS.md (see the R6-R9 edits + the PROGRESS line).
