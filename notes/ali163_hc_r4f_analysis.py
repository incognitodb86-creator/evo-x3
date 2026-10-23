"""ALI-163 R4F audit - fills the <!--ANALYSIS--> block of C:/AI/community/notes/hc_prompt_face_audit_20261023.md.

Mechanical prompt-language count over the 8 prompt strings (c0+c1 of c1, c2, r1, r2) plus the written
comparison. No GPU, no render, no download, no install, no vision judge. Re-runnable: it replaces the
marker text, so run ali163_hc_r4f_audit.py first (it writes the tables + the marker).
"""
import json
import os
import re

RUNS = r"C:\AI\community\runs"
AUD = r"C:\AI\community\notes\hc_prompt_face_audit_20261023.md"
IDS = ["ali147_pool_hc_c1_s51100001", "ali147_pool_hc_c2_s51100002",
       "ali147_pool_hc_r1_s51130001", "ali147_pool_hc_r2_s51130002"]
TERMS = ["face", "facial", "close-up", "close up", "crop", "bust", "headshot", "portrait", "macro",
         "shallow depth of field", "bokeh", "negative prompt", "4K", "8K", "ultra", "hyper8n",
         "hyper", "detailed skin", "natural matte skin", "visible pores", "long blonde hair",
         "long dark hair", "LEFT", "RIGHT", "left woman", "right woman", "on the left", "on the right",
         "multi-view reference sheet", "identity", "same woman", "Picture 1", "Picture 2", "Picture 3"]

prompts = {}
for jid in IDS:
    g = json.load(open(os.path.join(RUNS, jid, "request.api.json"), encoding="utf-8"))
    tag = jid.split("_")[3]
    for chunk in ("c0", "c1"):
        prompts["%s.%s" % (tag, chunk)] = g[chunk]["inputs"]["prompt"]

A = []
W = A.append
W("")
W("---")
W("")
W("## ANALYSIS (written part, R4F pass 2 - 2026-10-23)")
W("")
W("Author: Forge Ralph (ALI-163 R4F, widened scope). All numbers above are machine-measured by "
  "`C:\\AI\\community\\notes\\ali163_hc_r4f_audit.py`; this block is the reading of them. "
  "Community sources read (local, saved): `C:\\AI\\community\\notes\\web\\ext_readme.md` "
  "(MiniMax-H3-ComfyUI-Extender README, https://github.com/chaos20044/MiniMax-H3-ComfyUI-Extender - "
  "`subject_definitions` at the start of every clip prompt, lines 379-406) and "
  "`C:\\AI\\community\\notes\\web\\comfy_h3_tutorial.html` (https://docs.comfy.org/tutorials/video/minimax-minimax-h3-alpha, "
  "Ref2VA = \"Lock identity, style, motion, camera, or voice from references\"). "
  "Implementation read: `ComfyUI\\custom_nodes\\ComfyUI_MiniMax_H3_Extender\\extender.py` "
  "(installed local copy of the community node) lines 110-116 and 2267-2310.")
W("")

W("### A. Prompt texts: listing (verbatim above, complete)")
W("")
W("Every text node of all four graphs is quoted verbatim in the `<details>` blocks above - 8 prompts "
  "(c0 + continuation chunk of each of c1, c2, r1, r2), with char counts in each clip's *Prompt nodes* table:")
W("")
for k, v in prompts.items():
    blocks = [b for b in ["subject_definitions", "summary", "retention_analysis", "detailed_description",
                          "integrated_multimodal_description", "overall_soundscape", "non_diegetic_music"]
              if b + ":" in v]
    first = v.split("\n")[0]
    W("- `%s` - %d chars, %d lines, opens with `%s...`, blocks: %s" % (k, len(v), len(v.split("\n")), first[:48], ", ".join(blocks)))
W("")
W("Source of truth for the wording: `C:\\AI\\community\\notes\\ali163_hc_r5_build.py::prompts(pair)` "
  "(lines 80-145). It emits the **v1** style (one start-still ref, hair-colour binding) for HC3/HC4/HC5/HC6 "
  "and the **v2** style (pick + 2 per-woman sheets, sheet-first binding) for HC1/HC2. "
  "c1/c2 (the 120 s clips, the only approved pair) carry the v1 shape; r1/r2 carry v2. "
  "R6-R9 are HC3-HC6, i.e. they inherit the **v1** shape with the R5 sheet wiring bolted on "
  "(`refs_json` 3 slots, `ref_image_size=max`, `continuation_window` on node `win1`, length 243).")
W("")

W("### B. Line-by-line comparison of the two prompt shapes")
W("")
W("Identity binding, c1/c2 (v1, verbatim, c1.c0 lines 2-3):")
W("")
W("```text")
W("<Subject 1> is the adult woman with long blonde hair shown in <Picture 1>, a fictional adult aged 25, ...")
W("<Subject 2> is the adult woman with long dark hair shown in <Picture 1>, a fictional adult aged 24, ...")
W("```")
W("")
W("Identity binding, r1/r2 (v2, verbatim, r1.c0 lines 2-6):")
W("")
W("```text")
W("<Subject 1> is the adult woman shown in the multi-view reference sheet in <Picture 2>, the blonde woman of the two-woman start still in <Picture 1>, ...")
W("<Subject 2> is the adult woman shown in the multi-view reference sheet in <Picture 3>, the dark-haired woman of the two-woman start still in <Picture 1>, ...")
W("<Picture 1> is the start still of <Subject 1> and <Subject 2> seated close together in a warm photo studio.")
W("<Picture 2> is the multi-view reference sheet of <Subject 1> alone.")
W("<Picture 3> is the multi-view reference sheet of <Subject 2> alone.")
W("```")
W("")
W("Continuation chunk of r1/r2 (v2, verbatim, r1.c1 lines 2-4):")
W("")
W("```text")
W("<Subject 1> is the adult woman shown in the multi-view reference sheet in <Picture 1>, a fictional adult aged 25, ...")
W("<Subject 2> is the adult woman shown in the multi-view reference sheet in <Picture 2>, ...")
W("<Picture 1> is the multi-view reference sheet of <Subject 1> alone.")
W("```")
W("")
W("Mechanical differences, in the order they matter:")
W("")
W("1. **Who is in charge of identity in the second chunk.** c1/c2 continue with `MiniMaxH3ImageToVideo` and "
  "**zero** image references (c1.c1 2794 chars, c2.c1 3227 chars, 0 binding lines, no `subject_definitions:` block): "
  "identity is carried by the last generated frame. r1/r2 continue with `MiniMaxH3ReferenceToVideo` whose only "
  "references are the **two Klein sheets** - the approved start still (the only real evidence of the two faces) "
  "is **never** a reference in chunk 2 (`pick in c1 refs? = False`, `sheet in c1 refs? = True`, "
  "slot/size summary). So from frame ~120 on, r1/r2 are drawn from the sheet faces.")
W("2. **Reference pixel weight.** `ref_image_size` is `max` in both r1/r2 chunks, and the node's `max` rule is "
  "`scale = min(1, 2048/min(w,h))` (`extender.py:2274`, `REF_IMAGE_SHORT_EDGE = 2048` at `extender.py:113`), "
  "i.e. a 1152x2016 sheet is **not** downscaled at all: each sheet enters the VAE at 2.32 Mpx. "
  "r1/r2 chunk 1 = 5.70 Mpx of reference, chunk 2 = 4.64 Mpx, for a 1.03 Mpx (1344x768) canvas = 5.5x / 4.5x. "
  "c1/c2 = 1.03 Mpx in chunk 1 (`match` = cap at canvas pixels) and 0 Mpx in chunk 2.")
W("3. **Aspect mismatch.** The reference set mixes 16:9 (1376x768 pick, 1.792) with 9:16 "
  "(1152x2016 sheets, 0.571) in one slot list, and the 9:16 slots are the big ones. "
  "The 16:9 start frame - the only thing that matches the 1344x768 target - is 18% of the reference pixels in chunk 1 and 0% in chunk 2.")
W("4. **Face density per slot.** A pick slot holds exactly 2 faces (175x150 + 126x162 for HC1; 133x203 + 186x144 for HC2, "
  "1.94-2.58% of the frame). A sheet slot holds 2-6 faces (multi-view panels: 188x266 to 247x349 for the biggest panel, "
  "44x99 to 110x190 for the profile/back panels, all in the top two thirds of the 2016 px height). "
  "The model must pick which panel is the identity and which is a pose, from a collage with up to 6 faces in it.")
W("5. **Anchors.** v1 names the woman by hair colour inside the same picture the video starts from "
  "(\"the adult woman with long blonde hair shown in <Picture 1>\"). v2 names her **sheet-first** "
  "(\"the adult woman shown in the multi-view reference sheet in <Picture 2>\") and demotes the start still to a "
  "scene/wardrobe reference (\"<Picture 1> is the start still of ...\"). Neither shape uses the spatial anchors "
  "(\"on the LEFT side of <Picture 1>\") that the R5 v1 builder template has for HC3-HC6 - grep count for "
  "the R5 builder's v1 template for HC3-HC6 does (the word table below counts `LEFT`, `RIGHT`, "
  "`left woman`, `right woman` in the 8 submitted prompt strings).")
W("6. **Face language.** No prompt in any of the four clips contains a face crop / close-up / bust / headshot / "
  "portrait / macro / shallow-depth instruction (see the word table below: 0 hits for `close-up`, `crop`, `bust`, "
  "`headshot`, `portrait`, `macro`, `shallow depth of field`, `bokeh`, `negative prompt`, `4K`, `ultra`, `hyper`). "
  "`face` occurs in only 4 of the 8 prompt strings and where it occurs it is action prose (r1: \"faces close\", "
  "\"faces stay close, foreheads touching\"); the binding lines of v1 and v2 never use the word, and `facial` occurs in "
  "0 of 8 - there is no facial-identity word in the binding at all. Skin-quality language is `natural matte skin` / "
  "`visible pores` (8 of 8) inside `detailed_description:`; `detailed skin` 0 of 8.")
W("7. **Length.** r1/r2 = 124 frames in c0 + `win1.extension_frames` 119 (overlap 22) = 243 frames = 10.1 s of video. "
  "c1/c2 = 243 + 238 = 481 frames = 20.0 s. All four are 1344x768 at 24 fps, 10 steps, `simple`, `euler`, "
  "`denoise 1.0` on **both** chunks (`s0_sched` and `s1_sched`), `shift_video 10.0`, `shift_audio 3.0`. "
  "The R4G spec keeps that sampling and the 243 f (124 + 119) shape for R6-R9 - length is not a face fix, "
  "it is the batch shape R1/R2 chose.")
W("")

W("### C. Reference images as placed (tables above, read out)")
W("")
W("- Picks: `HC1_Two_women_in_studio_editorial.jpg` 1376x768, 1.792, sha256 `dd9ed0cb69e4`; "
  "`HC2_Two_women_in_passionate_embrace.jpg` 1376x768, 1.792, sha256 `530f056f4eb2` - both in "
  "`ComfyUI\\input\\community\\hc\\`, both wired as `<Picture 1>` of chunk 1 in all four clips.")
W("- Sheets used by r1/r2: `HC1_w1_blonde_00001_.png` `022cd65e0c33`, `HC1_w2_darkhair_00001_.png` `8336fa03aab3`, "
  "`HC2_w1_blonde_00001_.png` `0daac8df30bb`, `HC2_w2_darkhair_00001_.png` `3c9701692eb0` - all 1152x2016, 0.571, "
  "2.32 Mpx, all in the **same** `input\\community\\hc` folder (the LoadImage strings resolve, no ` [output]` tag needed).")
W("- All 10 sheets R3 built (HC1 w1/w2, HC2 w1/w2, HC3 w1/w2, HC4, HC5, HC6 w1/w2) are 1152x2016 portrait "
  "multi-view collages; per-woman sheets exist only for HC1, HC2 and HC6; HC4, HC5 are single sheets for the pair "
  "and HC3 has 2 per-woman sheets; so \"one sheet per woman\" is true only for 5 of the 6 pairs.")
W("- Face quality of those sheets, measured: sheet-to-sheet cosine inside a pair is 0.30-0.57 and pick-to-own-sheet "
  "is 0.22-0.47 (R4F pass 1 table T1, same detector). The two per-woman sheets of one pair are therefore as close "
  "to each other in face space as a sheet is to the real face it was built from: the Klein 9B edit flattened the "
  "two women toward one generic face, HC2 worst (pick->sheet 0.217-0.240).")
W("")

W("### D. Face box size per woman, per clip (measured, 5 frames each)")
W("")
W("| clip | faces per sampled frame | face box px (W x H) | face area px2 | % of 1344x768 frame | video face vs her sheet anchor (cos) |")
W("|---|---|---|---|---|---|")
W("| c1 (no sheets, 120 s) | 2 (one frame 1) | 104x131 - 191x166 | 13,803 - 33,340 | 1.34 - 3.23% | 0.065 - 0.350 |")
W("| c2 (no sheets, 120 s) | 2 (one frame 1) | 90x123 - 170x199 | 11,215 - 34,095 | 1.09 - 3.30% | 0.078 - 0.283 |")
W("| r1 (sheets, 60 s) | 2 | 89x148 - 114x192 | 13,284 - 20,240 | 1.29 - 1.96% | 0.074 - 0.556 |")
W("| r2 (sheets, 60 s) | 2 (one frame 0) | 96x153 - 147x253 | 15,711 - 37,317 | 1.52 - 3.62% | 0.138 - 0.425 |")
W("")
W("Reading: every clip renders the two faces at 90-190 px wide, i.e. 1.1-3.6% of the frame, and **the sheet-fed "
  "clips do not render bigger faces than the sheet-free clips** - r1 is the smallest of the four (89-114 px wide). "
  "At 1344x768 a 100 px face is ~70 px at 1080p, which is the whole reason the output reads as \"no facial detail\". "
  "In 6 of the 10 sampled r1/r2 frames the best-matching face for woman 1 and for woman 2 is the *same* detection, "
  "so the second face in frame scores lower against both anchors: the pair is not separable per woman in the video.")
W("")

W("### E. Prompt-language count (all 8 submitted prompt strings, case-insensitive substring count)")
W("")
cnt = {}
for t in TERMS:
    cnt[t] = sum(1 for v in prompts.values() if t.lower() in v.lower())
W("| term | prompts containing it (of 8) |")
W("|---|---|")
for t in TERMS:
    W("| `%s` | %d |" % (t, cnt[t]))
W("")
W("`denoise`/`shift` are graph settings, not prompt words: all four clips, both chunks: `BasicScheduler` "
  "`steps 10`, `scheduler simple`, `denoise 1.0`, `euler`, shift `shift_video 10.0` / `shift_audio 3.0` "
  "(the H3 distill path, and the reason the community README puts identity language in `subject_definitions:` at the "
  "top of every clip prompt: with `denoise 1.0` the prompt is the only lever). "
  "No prompt in the batch contains a negative-prompt block (H3 prompt fields are positive-only).")
W("")

W("### F. Five-line summary (plain language, exactly five lines)")
W("")
W("1. The redo let the reference sheets speak for identity: the second chunk of r1/r2 receives **only** the two 9:16 multi-view sheets, the approved start still is never a reference there, and those sheet faces measure cosine 0.22-0.47 from the real faces in the still, so the model faithfully renders the Klein sheet's generic face and the result drifts off the pick.")
W("2. Pixel weight is why: with `ref_image_size=max` a 1152x2016 sheet is fed at full 2.32 Mpx, so the redo carries 5.70 Mpx of reference in chunk 1 and 4.64 Mpx in chunk 2 against a 1.03 Mpx frame, 4.5-5.5x the reference load of the approved 120 s clips, which use one 1.03 Mpx 16:9 start frame and nothing at all in the continuation.")
W("3. The prompts never ask for a face: 0 of 8 prompt strings contain close-up / crop / bust / headshot / portrait / macro / shallow-depth / negative-prompt words, and the face boxes prove it - 90-190 px wide, 1.1-3.6% of the frame, sheet-fed clips no better than sheet-free ones, which is unresolvable at 1080p; only a 400-550 px face-crop reference plus explicit face language changes that, keeping the full-body 16:9 start frame.")
W("4. The binding got weaker at the same time: v1 names each woman by hair colour inside the same picture the video starts from, v2 names her \"the woman shown in the multi-view reference sheet\" and demotes the start still to scenery, and no submitted prompt uses the left/right spatial anchor - so hair colour is the only thing separating the two identities, and the pair's sheets are 0.30-0.57 similar to each other, which invites a swap.")
W("5. What to change for R6-R9 (R4G), no new renders and no new seeds in this pass: keep the 16:9 approved start frame as the ONLY reference and keep it present in **every** chunk including the continuation (c1/c2's chunk 2 has no reference at all, r1/r2's chunk 2 has only the two sheets), carry the extender README's `subject_definitions` wording on both chunks with \"<Subject 1> is the exact same woman shown in <Picture 1>\", say the picture is for her face and hair only, add one \"the camera frames her face in close-up\" beat per woman, keep `denoise 1.0 / shift 10 and 3 / euler / 10 steps`, and keep 1344x768 / 24 fps / 243 f (124 c0 + 119 extension) with audio.")
W("")
W("### G. R4F -> R4G")
W("")
W("R4F (research + measurement, this pass) is complete: the ranked fix list is "
  "`C:\\AI\\community\\notes\\hc_face_research_20261023.md` (F1-F10); this file is the prompt/reference/face-box "
  "audit it was built on. R4G (next task, TASKS.md line 36) applies F1 (approved pick as the ONLY reference, "
  "Klein sheets dropped from c0 **and** c1), F2 (`ref_image_size` back to the node default `match`, 1 ref), "
  "F3 (extender `subject_definitions` wording on both chunks, \"the exact same woman shown in <Picture 1>\"), "
  "F4 (picture = face and hair only, garment words out of the binding) and F7 (one face close-up beat per woman) "
  "to the remaining redo lines R6-R9 in the builder `C:\\AI\\community\\notes\\ali163_hc_r5_build.py`; "
  "no render is requested while `used_min >= 475` or `jobs >= 35`. F8 (a per-woman 400-550 px face crop) is the "
  "strongest single change by these numbers but needs a Derrick-approved crop written into "
  "`ComfyUI\\input\\community\\hc`, so it stays out of the no-download set.")
W("")
W("Statements required by the task: c1, c2, r1, r2 prompt texts are listed verbatim and completely (section A + the "
  "`<details>` blocks); the line-by-line comparison is section B; the reference images as placed (pixel sizes, aspect, "
  "sha256, per-face box sizes) are in the tables of sections C and D; face box size per woman per clip is measured in "
  "D. **No new renders were submitted in this pass** (no `p7\\JOB_REQUEST.json` was written, no GPU touched), "
  "**no new seeds** (only the seeds of the four already-submitted clips are named), **no vision judge**, "
  "**no download, no install** (R4F runs used `C:\\AI\\qa_gate_venv` only, per its ALLOWLIST).")
W("")

md = open(AUD, encoding="utf-8").read()
if "<!--ANALYSIS-->" in md:
    md = md.replace("<!--ANALYSIS-->", "\n".join(A))
    open(AUD, "w", encoding="utf-8").write(md)
    print("analysis written into %s (%d bytes)" % (AUD, os.path.getsize(AUD)))
else:
    print("marker already consumed; appending")
    open(AUD, "a", encoding="utf-8").write("\n".join(A) + "\n")
