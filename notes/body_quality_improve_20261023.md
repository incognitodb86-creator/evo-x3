# BQ1b IMPROVE - the HC body-quality rewire (ALI-184, CPU only, 2026-10-23 ~5:00 PM CT)

Task: `BQ1b IMPROVE` = apply research rows 1+2 of `notes/body_quality_research_20261023.md` to the HC graph,
validate offline, write the improve note. No render, no `p7/JOB_REQUEST.json` (that is BQ1c). 0 GPU minutes:
no ComfyUI port, no comfy_ctl, no llama-swap, no vision judge, no image viewing.

## New files

| file | what |
|---|---|
| `notes/ali163_hc_bq1_build.py` | the BQ1 builder (cloned from the FROZEN `notes/ali163_hc_r4g2_build.py`), 13 checks, HC3-only dict |
| `notes/hc_r3b_c0.txt` / `notes/hc_r3b_c1.txt` | the rewired v2 prompts (c0 6518 chars / c1 5912 chars, same line counts 22 / 14 as the r3r prompts) |
| `notes/bq1_prompt_diff.txt` | the unified prompt diff r3r -> BQ1b, written by check 12 |
| `runs/ali147_pool_hc_r3b_s51130003/request.api.json` | the built graph, 18339 bytes, sha256 `ce01686e03909d04be500bb8a186230011c71d12668d2a0fb4686f60809df9f7`, byte-identical over 2 runs |

## The rewire (research row 1 + the Max REWIRE 4:51 PM CT)

`r3r` put ONLY face crops in the graph (`c0` refs = `HC3_w1_face.png` + `HC3_w2_face.png`, `c1` =
`MiniMaxH3ImageToVideo` with no refs at all), so the model invented the bodies from text = the "their bodies are
ugly as fuck" complaint (Derrick 4:00 PM CT). BQ1b:

```
<Picture 1> = node img  = community/hc/HC3_lesbian_beach.jpg  (1792x1008, aspect 1.778, sha256 4646d75b65e6...
                          == approved_characters/GROK_IMAGINE_2026-10-19b/GI173.jpg byte for byte)
                          = BODY / SKIN / FIGURE / WARDROBE / SCENE / LIGHT reference
<Picture 2> = node img2 = community/hc/HC3_w1_face.png  (512 px SCRFD crop, face_box [382,0,171,240]) = FACE + HAIR only
<Picture 3> = node img3 = community/hc/HC3_w2_face.png  (512 px SCRFD crop, face_box [799,228,222,204]) = FACE + HAIR only
```

3 slots in **both** chunks, `ref_image_size: match` in both, both chunks `MiniMaxH3ReferenceToVideo` (so `c1`
keeps `audio_vae` legally - the R4G2 `MiniMaxH3ImageToVideo` c1 has no such input, which is what made r3 die at
STATIC_FAIL rc=2 on 2026-10-23 14:15 CT). No sheet node, no Klein sheet.

Graph diff vs base `ali147_pool_refsheet_b_s51080000` (RS6, 26 nodes): `+img2 +img3 -sheet` = **27 nodes**;
changed nodes `c0 c1 img img2 img3 noise save win1`; every other node byte-identical (sampling frozen:
euler/simple/10 steps, shift 10.0 video / 3.0 audio, vsa, beta6 int8, BasicGuider x2, 1344x768, 24 fps,
c0 124 f + `win1.extension_frames` 119 = 243 f = the R1 count, single pass, audio VAE + decoder wired).

## The contradiction fix (research row 2)

Deleted from both prompts (check 8 asserts each string is ABSENT, and check 12 shows 11 removed diff lines carry
them): `body proportions` in the crop sentences, `the bodies and the camera of this video are new and are not
taken from the reference pictures`, `used for the faces and the hair of the two women only`, `These two crops are
the only visual references`, and the c1 sentence `This continuation clip carries no reference pictures at all`
(c1 now declares the same three reference pictures).

Kept from R4G2: the exact `subject_definitions` skeleton -
`<Picture N> is the reference image defining the exact visual appearance, identity, face and hairstyle of <Subject N>`
(face + hairstyle only, no body claim in the crop lines),
`<Subject N> is the exact same woman shown in <Picture N> of the reference pictures and in the first 5 seconds of
this clip, preserving her face, hairstyle, body, skin and figure with complete fidelity`, `the face fills`,
`is an action in the story` (the clothing-removal clause, so H3 does not treat the start photo's clothes as a body
change), and the community body wording (`matte skin with visible pores`, `fine vellus hair`, `never a waxy,
plastic or airbrushed surface`, waist / hips / thigh / breast / weight, `five separate fingers`, joint wording).

## Deferred, one variable per render (research section 2 - NOT in this arm)

Realism LoRA (fal `official-community-model-realism-lora`, 7.0 GB, `strength_model` 1.0, needs `LoraLoaderModelOnly`
before the ModelMetadata block and a model-name gate first), steps 8 + shift 12/5 (the community "kill the gloss"
setting), `CFGGuider`+`NAGuidance` (negatives, ~2x/step), `MiniMaxH3AddGuide` frame_idx 0, BlockSparseAttention
off. Each gets its own arm after the BQ1c side-by-side.

## Self-check (run: `python -X utf8 notes/ali163_hc_bq1_build.py HC3`)

`ALL CHECKS PASS (32 PASS lines, 13 numbered checks)`. Highlights: check 1 graph diff + per-node key sets +
byte-identical untouched nodes; check 4 the 3-slot rewire with the start-still sha256 == the approved pick;
check 5 `match` + the row-12 quality gate (PIL only: 1792x1008, aspect 1.778, short side 1008 >= 768, crops
512x512); check 8 the wording (definition line once per chunk, crop lines face+hair only, 5 forbidden phrases
absent, body wording present, `<Picture>` set 1/2/3, 2 subject lines each, no garment word in a binding line);
check 9 the live `ralph.ps1` id gates + id free + no `JOB_REQUEST.json`; check 10 crop provenance from
`notes/face_crop.log` + start-still byte/sha equality with the approved pick; check 11 the offline
`static_check` clone (input names + required inputs vs the on-disk H3 schema; reproduces the r3
`c1.audio_vae: not an input of MiniMaxH3ImageToVideo` defect in the dead r3 graph, 0 findings on the new graph);
check 12 the prompt diff; check 13 a **self-destruct probe** that restores the r3r wiring in a clone and fires
5/5 detectors there and 0/5 on the real graph, so checks 4/5/8/11 are not vacuous.

## BQ1c handoff

`BQ1c` writes `C:\AI\community\p7\JOB_REQUEST.json` (absolute path only) for
`ali147_pool_hc_r3b_s51130003`, its `request.api.json` must byte-match
`runs/ali147_pool_hc_r3b_s51130003/request.api.json` (plain `cmp`), seed 51130003 (same seed as r3r so the
side-by-side is a clean A/B), then END the iteration. BQ1d reviews the 243-frame render against
`runs/ali147_pool_hc_r3r_s51130003` with objective checks only (ffprobe frames/res/fps/audio, seam diff, hashes,
labelled contact sheet) - no vision judge, KEEP is Derrick's.

## BQ1d (2026-10-23 ~17:55 CT) the rewire VERIFIED in the rendered graph + the side-by-side
- The rendered r3b graph (p7/jobs/ali147_pool_hc_r3b_s51130003.submitted_graph.json, sha8 ce01686e =
  notes/ali163_hc_bq1b_request.api.json byte-for-byte) carries on c0 AND c1, class MiniMaxH3ReferenceToVideo,
  ref_image_size match: ref_image_1 = community/hc/HC3_lesbian_beach.jpg (the approved start still =
  <Picture 1> body/scene) + ref_image_2 = community/hc/HC3_w1_face.png + ref_image_3 = community/hc/HC3_w2_face.png
  (face-only). The r3r control carries ONLY the 2 face crops (LoadImage list = the 2 crops, 2 ref slots on c0):
  the body defect, proved, not asserted.
- Objective verify (notes/ali163_hc_bq1d_check.py, 22/22 gates + 3 self-destruct probes): both clips
  ok=True rc=0, 1 JOB start + 1 JOB end ok, 0 JOB error / 0 CLIP_SKIP, 1344x768, 24/1 fps, 243 packets
  = 10.125 s, audio aac 32 kHz 2ch in the mp4 AND in the demuxed m4a (165,349 B / 166,134 B), seed 51130003
  both, 124 + 119 f, euler, 10 steps, shift 10.0 / 3.0, 2 SamplerCustomAdvanced = one sampling pass,
  overall_soundscape: line present, offline static_check clean. Fairness: seed, scene, frames, resolution,
  steps, sampler, shift all fixed; the single variable = the ref wiring.
- Side-by-side = notes/body_quality_r3b_vs_r3r_contact.png (2186x834, 1,291,630 B): row A = r3r control,
  row B = r3b rewired, 5 stamps each at the SAME t = 0.50 / 2.60 / 5.00 / 7.40 / 9.60 s, label cells carry
  id / seed / start still / refs / ok / rc / WxH / fps / packets / audio / m4a / wall / sha8 read from
  notes/ali163_hc_bq1d_objective.json; a reference row shows the approved start still + the 2 face crops.
  Frame gates 21/21: every frame 1344x768 and non-black (mean 117.8-138.0), the same t across the two clips
  always differs (two distinct renders), f0 vs f4 differs inside each clip (motion). Sheet gates 4/4, and a
  missing stamp paints a red MISSING block and fails the builder, so the sheet cannot hide a gap.
- BQ1 TEMPLATE for the bakeoff arms: HB1, HB2, HB3, HB4 now each carry a TASKS.md line saying they use the
  improved template (start still = ref_image_1 on c0 AND c1 + face crops face-only, builder
  notes/ali163_hc_bq1_build.py, prompts notes/hc_r3b_c0.txt + notes/hc_r3b_c1.txt); the HB parent line carries
  the HB0-control note (HB0 = r3r = the before-shot, no new job).
- No vision judge: no image was opened, shown, described or scored by a model. KEEP is Derrick's only.
