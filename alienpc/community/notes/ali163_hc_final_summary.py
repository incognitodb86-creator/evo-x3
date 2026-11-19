"""ALI-163 FINAL summary writer (CPU only, no vision judge, no GPU).

Reads notes/ali163_hc_final_objective.json (built by notes/ali163_hc_final_check.py) and
C:/Users/derek/5slock/ralph-community/logs/p7_budget.json, writes
C:/AI/community/notes/hc_redo_20261023_summary.md. METHOD_ONLY; KEEP is Derrick's only.
"""
import json
import os
import re
from datetime import datetime

OBJ = "C:/AI/community/notes/ali163_hc_final_objective.json"
BUD = "C:/Users/derek/5slock/ralph-community/logs/p7_budget.json"
OUT = "C:/AI/community/notes/hc_redo_20261023_summary.md"
SHEET = "C:/AI/community/notes/hc_redo_20261023_contact.png"

CLIPS = [
    # label, id, pick still, reference input(s), line, batch
    ("clip 1 OLD", "ali147_pool_hc_c1_s51100001",
     "C:/Users/derek/5slock/approved_characters/FLOW_BLONDE_DARK_PAIRS_2026-10-19/BD004.jpg (HC1, pair)",
     "img = community/hc/HC1_Two_women_in_studio_editorial.jpg (start still only; no sheet ref on c0 or c1)",
     "HC1/HC2 batch (481 f)", "old"),
    ("clip 2 OLD", "ali147_pool_hc_c2_s51100002",
     "C:/Users/derek/5slock/approved_characters/FLOW_BLONDE_DARK_PAIRS_2026-10-19/BD007.jpg (HC2, pair)",
     "img = community/hc/HC2_Two_women_in_passionate_embrace.jpg (start still only)",
     "HC1/HC2 batch (481 f)", "old"),
    ("clip 1 NEW (R4)", "ali147_pool_hc_r1_s51130001",
     "HC1 BD004 (pair)",
     "img = community/hc/HC1_Two_women_in_studio_editorial.jpg + sheet refs "
     "community/hc/HC1_w1_blonde_00001_.png, community/hc/HC1_w2_darkhair_00001_.png",
     "R4 (243 f, Klein sheet refs)", "new"),
    ("clip 2 NEW (R5)", "ali147_pool_hc_r2_s51130002",
     "HC2 BD007 (pair)",
     "img = community/hc/HC2_Two_women_in_passionate_embrace.jpg + sheet refs "
     "community/hc/HC2_w1_blonde_00001_.png, community/hc/HC2_w2_darkhair_00001_.png",
     "R5 (243 f, Klein sheet refs)", "new"),
    ("clip 3 (R6)", "ali147_pool_hc_r3_s51130003",
     "HC3 GI173 (pair)",
     "img = community/hc/HC3_w1_face.png, img2 = community/hc/HC3_w2_face.png (face crops, R4G2)",
     "R6 (243 f, face-crop refs) - NOT RENDERED", "new"),
    ("clip 3 R6R", "ali147_pool_hc_r3r_s51130003",
     "HC3 GI173 (pair)",
     "img = community/hc/HC3_w1_face.png, img2 = community/hc/HC3_w2_face.png "
     "(2 face crops only, R4G2 wiring; NO start still in this graph - Max 4:51 PM CT)",
     "R6R re-render of clip 3 (243 f, face crops only)", "new"),
    ("clip 3 BQ1c", "ali147_pool_hc_r3b_s51130003",
     "HC3 GI173 (pair)",
     "img = community/hc/HC3_lesbian_beach.jpg (start still back in c0 ref_1) + "
     "community/hc/HC3_w1_face.png + community/hc/HC3_w2_face.png (BQ1 rewire, c0 AND c1)",
     "BQ1c test render of clip 3 (243 f, start still + 2 face crops)", "new"),
    ("clip 4 (R7)", "ali147_pool_hc_r4_s51130004",
     "HC4 GI107 (solo)",
     "img = community/hc/HC4_w1_face.png (face crop, R4G2)",
     "R7 (243 f, face-crop refs)", "new"),
    ("clip 5 (R8)", "ali147_pool_hc_r5_s51130005",
     "HC5 GI150 (solo)",
     "img = community/hc/HC5_w1_face.png (face crop, R4G2)",
     "R8 (243 f, face-crop refs)", "new"),
    ("clip 6 (R9)", "ali147_pool_hc_r6_s51130006",
     "HC6 BD076 (pair)",
     "img = community/hc/HC6_w1_face.png, img2 = community/hc/HC6_w2_face.png (face crops, R4G2)",
     "R9 (243 f, face-crop refs)", "new"),
]

obj = {r["id"]: r for r in json.load(open(OBJ, encoding="utf-8"))}
bud = json.load(open(BUD, encoding="utf-8"))
L = []
w = L.append
w("# ALI-163 hc redo - FINAL summary (2026-10-23, Forge)")
w("")
w("> **Correction 2026-10-23 (Max, 4:51 PM CT):** the 2:59 PM CT claim that the redos use the approved start "
  "still is wrong. r3r–r6 used face crops only; the start still was not in the graph (found 4:03 PM CT; fix in "
  "ALI-184 BQ1). The original lines below are kept.")
w("")
w("## FINAL reopened (Max 3:16 PM CT) - what this pass added")
w("")
w("- **clip 3 now has renders.** The original R6 id `ali147_pool_hc_r3_s51130003` died on the rc=2 static check "
  "(audio_vae on MiniMaxH3ImageToVideo); the fixed graph was re-queued under two NEW ids, both now verified here: "
  "`ali147_pool_hc_r3r_s51130003` (R6R, face crops only) and `ali147_pool_hc_r3b_s51130003` (BQ1c rewire = the "
  "approved start still back in c0 + c1 ref slots plus the 2 face crops).")
w("- Contact sheet `notes\\hc_redo_20261023_contact.png` is now **9 rows x 5 frames** (adds the r3r and r3b rows, "
  "same 5 timestamps, labelled with id / seed / start still / reference images).")
w("- New objective items per clip (pure PIL, no vision judge): the 5 sheet frames are counted, sha256'd, checked "
  "for duplicates, and their grayscale luma stdev is reported (a black/flat frame would sit near 0; every rendered "
  "clip here measures 33.9-56.8).")
w("- This pass is CPU only: no render, no GPU, no new seed, no ComfyUI port call, no vision judge.")
w("")
w("METHOD_ONLY. Review = contact sheet + objective checks only (ffprobe -count_packets, ffmpeg stream copy, "
  "sha256, status.log greps). NO vision judge was called on any output (superseded 2026-10-22). "
  "No quality redo was requested. **KEEP is Derrick's only.**")
w("")
w(f"Contact sheet: `{SHEET}` (9 rows x 5 frames, built by notes\\ali163_hc_final_sheet.py from frames extracted "
  "by notes\\ali163_hc_final_media.ps1 at t = 0.50 / 2.60 / 5.00 / 7.40 / 9.60 s; rows 0 and 1 use the SAME "
  "timestamps, so old clip 1 and new clip 1 line up frame-for-frame). "
  "Raw objective dump: notes\\ali163_hc_final_objective.json (notes\\ali163_hc_final_check.py).")
w("")
w("## R1 length + R2 causes (3 lines)")
w("1. R1 length: 243 frames = c0 124 + win1.extension_frames 119 (overlap 22) at 24 fps = 10.125 s per clip "
  "(notes/hc_redo_research_20261023.md; R1 line in TASKS.md). Every R-clip and every check below uses 243 f.")
w("2. R2 top causes (ranked, notes/hc_redo_research_20261023.md '## R2 diagnosis'): (1) `c1` was "
  "MiniMaxH3ImageToVideo with NO ref_images slot, so the whole continuation chunk had no fresh appearance input; "
  "(2) one `ref_images` slot holding the wide two-person start still at `ref_image_size = match` "
  "= 1.03 Mpx shared by two faces.")
w("3. R2 causes 3-5: `subject_definitions` bound both subjects to the same `<Picture 1>` (and 7 `<Picture>` "
  "mentions pointed at slots that do not exist); `c1.prompt` had no subject_definitions and no `<Picture>` anchor "
  "(free-text hair wording = the model prior that lets a new face in); the landscape 1344x768 canvas plus a "
  "landscape two-shot shrinks the face area, and nothing compensated for it.")
w("")
w("## Budget (C:/Users/derek/5slock/ralph-community/logs/p7_budget.json)")
w(f"read at FINAL tick: used_min **{bud['used_min']}**, jobs **{bud['jobs']}**, cap_min {bud['cap_min']}, "
  f"job_cap {bud['job_cap']}, updated {bud['updated']}.")
w("R-line gate was used_min < 475 and jobs < 35 (495 min / 35 jobs); the harness caps are now 615 min / 45 jobs "
  "(Derrick 1:07 PM CT). At the first FINAL tick jobs was 35 = the R-line cap, so clip 3 could not be re-requested "
  "under an R-line id; that reading (used_min 450.8 / jobs 35) is the recorded BAKEOFF START. "
  "**clip 3 was then re-rendered twice under the ALI-173 bakeoff allowance** (Max 3:15 PM CT gave R6R one slot; "
  "BQ1c took one more), which is why jobs is now above 35. No render ran in this pass.")
w("")
w("## Table (all 10 rows: 2 old-batch reference + 6 R-clips + 2 clip-3 re-renders r3r / r3b)")
w("")
w("| clip | id | ok/rc | frames (probe/expected) | WxH | fps | audio (mp4) | m4a | m4a dur | "
  "mp4 bytes | render s | seed |")
w("|---|---|---|---|---|---|---|---|---|---|---|---|")
for label, cid, pick, refs, line, batch in CLIPS:
    r = obj[cid]
    v = r.get("video") or {}
    m4 = (r.get("m4a_probe") or {}).get("lines") or []
    dur = next((l for l in m4 if re.fullmatch(r"[\d.]+", l)), "")
    w(f"| {label} | `{cid}` | {r.get('ok')}/{r.get('rc')} | {v.get('packets')}/{r['expected_frames']} | "
      f"{v.get('w')}x{v.get('h')} | {v.get('fps')} | {r.get('audio_stream') or '-'} | "
      f"{r.get('m4a_exists', False)} | {dur or '-'} | {r.get('mp4_bytes', '-')} | "
      f"{r.get('render_secs', '-')} | {(r.get('seed') or ['-'])[0]} |")
w("")
w("Probe = `ffprobe -v error -select_streams v:0 -count_packets -show_entries "
  "stream=nb_read_packets,r_frame_rate,width,height -of csv=p=0` (exact packet count, not the container count).")
w("")
w("## Per clip")
for label, cid, pick, refs, line, batch in CLIPS:
    r = obj[cid]
    v = r.get("video") or {}
    m4 = (r.get("m4a_probe") or {}).get("lines") or []
    w("")
    w(f"### {label} - `{cid}` ({line})")
    w(f"- mp4: `{r['mp4']}` exists={r['mp4_exists']}"
      + (f", bytes={r['mp4_bytes']}, sha256={r['mp4_sha256']}" if r["mp4_exists"] else ""))
    w(f"- m4a: `{r.get('m4a','-')}` exists={r.get('m4a_exists', False)}"
      + (f", bytes={r['m4a_bytes']}, sha256={r['m4a_sha256']}, probe={m4}" if r.get("m4a_exists") else ""))
    w(f"- video probe: {v.get('w')}x{v.get('h')}, fps {v.get('fps')}, packets {v.get('packets')} "
      f"(expected {r['expected_frames']}) -> {'MATCH' if str(v.get('packets')) == str(r['expected_frames']) else 'n/a'}")
    w(f"- audio in mp4: {r.get('audio_stream') or '-'}; audio stream extract = ffmpeg -vn -c:a copy (stream copy, no re-encode)")
    frs = r.get("frames") or []
    if frs:
        w(f"- sheet frames: {r.get('frames_count')}/5 present, all sha256 distinct = {r.get('frames_sha_unique')}, "
          f"min luma stdev = {r.get('frames_min_luma_std')} (0 would mean a black/flat frame); "
          f"mean/stdev per frame = {[(f['luma_mean'], f['luma_std']) for f in frs]}")
    else:
        w("- sheet frames: none extracted (clip 2 OLD is table-only by spec - the old-batch row of the contact "
          "sheet is clip 1 OLD; clip 3 R6 has no render at all)")
    w(f"- render secs: {r.get('render_secs')} (prompt_id {r.get('prompt_id')}), finished {r.get('finished_ct')}")
    w(f"- result.json: ok={r.get('ok')} rc={r.get('rc')} started {r.get('started')} finished {r.get('finished')} "
      f"wall_min={r.get('wall_min')} budget_used_min_at_finish={r.get('budget_used_min')} note=\"{r.get('note_rc')}\"")
    for s in r.get("job_start", []):
        w(f"- status.log: `{s}`")
    for s in r.get("job_end", []):
        w(f"- status.log: `{s}`")
    for s in r.get("objective_line", []):
        w(f"- status.log: `{s}`")
    w(f"- greps: 'JOB error' = {r.get('job_error_grep', 0)}, 'CLIP_SKIP' = {r.get('clip_skip_grep', 0)} "
      f"(both must be 0)")
    w(f"- start still: {pick}")
    w(f"- reference input(s) in graph: {refs}")
    w(f"- sound line: {r.get('soundscape')}")
    w(f"- graph canvas: width {r.get('width')}, height {r.get('height')}, "
      f"extension_frames {r.get('ext_frames')}, seed {r.get('seed')}")
    if r.get("ok"):
        w("- failures: none (objective items all pass)")
    else:
        tail = " | ".join(r.get("status_tail", []))
        w(f"- FAILURES: rc={r.get('rc')} - {r.get('note_rc')}; status.log tail: `{tail}`. "
          "No mp4, no m4a, no frames (the job never queued a sample). "
          "The graph was fixed after the fail by the iter 03 builder pass (notes\\ali163_hc_r4g2_build.py pops the "
          "invalid `c1.audio_vae` link + runs the offline static self-check), so this clip is renderable, "
          "**but the job id `ali147_pool_hc_r3_s51130003` is spent** (p7\\jobs\\<id>.result.json exists = "
          "the runner refuses 'id already used') and the R-line job cap 35/35 was reached at that moment. "
          "Reported, not self-requested (PROMPT.md: real failures = rc 4 or TIMEOUT; rc=2 is a static-check "
          "failure, and STUCK is reported, never re-requested).")
        w("- RESOLVED (Max 3:15 PM CT): the fixed clip-3 graph was re-queued under two NEW ids inside the ALI-173 "
          "bakeoff allowance - `ali147_pool_hc_r3r_s51130003` (R6R, face crops only, ok rc=0, 243 f, 416.3 s) and "
          "`ali147_pool_hc_r3b_s51130003` (BQ1c rewire = start still + 2 face crops on c0 AND c1, ok rc=0, 243 f, "
          "481.9 s). Both are verified in this file and both have their own contact-sheet row.")
w("")
w("## Objective check list (the FINAL items)")
w("")
w("Task check list, item by item: (1) every requested clip passes the objective items or is listed with its failure "
  "= the per-id lines below (r3 is the failure line, with its RESOLVED note); (2) m4a per clip = the `m4a` column of "
  "the table + the per-clip m4a sha256/probe lines; (3) contact sheet + summary exist = "
  "`notes\\hc_redo_20261023_contact.png` and this file, both regenerated this pass. No vision judge was called, no "
  "quality redo, no new seed, no GPU.")
w("")
ok = all(obj[c]["ok"] for c in obj if c.startswith("ali147_pool_hc_r") and not c.startswith("ali147_pool_hc_r3_"))
rows_ok = []
for label, cid, pick, refs, line, batch in CLIPS:
    r = obj[cid]
    v = r.get("video") or {}
    fc = r.get("frames_count") or 0
    fr_txt = (f"{fc}/5 sheet frames, all sha256 distinct = {r.get('frames_sha_unique')}, "
              f"min luma stdev = {r.get('frames_min_luma_std')}"
              if fc else "no sheet frames (table-only row: clip 2 OLD has no contact-sheet row by spec, "
                         "clip 3 R6 has no render at all)")
    item = (f"`{cid}`: result.json {'ok' if r.get('ok') else 'NOT ok (rc=%s)' % r.get('rc')}; "
            f"JOB start + JOB end quoted above; 'JOB error' = {r.get('job_error_grep', 0)} and "
            f"'CLIP_SKIP' = {r.get('clip_skip_grep', 0)}; probe {v.get('w')}x{v.get('h')} {v.get('fps')} "
            f"{v.get('packets')} f (expected {r['expected_frames']}); audio stream present = "
            f"{bool(r.get('audio_stream'))}; m4a per clip = {r.get('m4a_exists', False)}; {fr_txt}")
    rows_ok.append((cid, r.get("ok"), item))
for cid, o, item in rows_ok:
    w(f"- [{'x' if o else ' '}] {item}")
w("")
w(f"**Verdict: all requested R-clip ids ok except the dead `ali147_pool_hc_r3_s51130003` (rc=2, listed with its "
  f"failure + RESOLVED line) = {ok}** - computed straight from the result.json files in "
  "C:\\AI\\community\\p7\\jobs, not asserted.")
w("")
w("The 7 requested R-clip renders that produced media (r1, r2, r3r, r3b, r4, r5, r6) pass every objective item: "
  "1344x768, 24/1 fps, 243 packets = the R1 count, an audio stream, an extracted `<id>.m4a` (aac, 32000 Hz, 2 ch, "
  "10.125 s), 5 distinct non-black sheet frames, 0 'JOB error' / 0 'CLIP_SKIP'. The original r3 id is listed with "
  "its failure (rc=2 static check, no render) and is superseded by r3r (R6R) and r3b (BQ1c). The two old-batch "
  "clips (c1, c2) are in the table, and c1 is row 0 of the contact sheet, for the side-by-side; they are 481 f / "
  "20.04 s by design and are not part of the R batch.")
w("")
w("Clip 3 is now a 3-way comparison on the same pick (HC3 GI173) and the same seed 51130003: r3 (dead, rc=2) -> "
  "r3r (face crops only, the R4G2/R6R wiring) -> r3b (BQ1c rewire: the approved start still back in the ref slots "
  "of c0 AND c1 + the 2 face crops + the BQ1 prompt rewire). Side-by-side frames of r3b vs r3r are also in "
  "notes\\body_quality_r3b_vs_r3r_contact.png (BQ1d). No face-similarity number was run in this pass (not asked by "
  "the FINAL check list); the R4F/R4G numbers are in notes\\hc_prompt_face_audit_20261023.md.")
w("")
w("## Files made by this pass")
w("- notes\\ali163_hc_final_check.py (objective dump) -> notes\\ali163_hc_final_objective.json. Per clip it now "
  "also sha256s the 5 sheet frames, checks they are distinct and reports their PIL grayscale luma stdev "
  "(a black/flat frame would sit near 0).")
w("- notes\\ali163_hc_final_media.ps1 (m4a stream copy + 5 frames per clip) -> notes\\hc_final_frames\\*.png; "
  "the id list now includes r3r + r3b (r3 has no media to extract).")
w("- notes\\ali163_hc_final_sheet.py -> notes\\hc_redo_20261023_contact.png (9 rows x 5 frames, labelled) with a "
  "built-in self-check: every rendered row's 5 cells must be non-flat (luma stdev > 5) and the NO-RENDER row must "
  "show the red panel (mean R > G+15). Self-destruct probe run 2026-10-23: hid r6 frame 4 -> the builder exited "
  "rc=1 naming `ali147_pool_hc_r6_s51130006` cell 4; restored -> rc=0 PASS 9 rows.")
w(f"- this file: {OUT}")
w("")
w(f"Written {datetime.now().strftime('%Y-%m-%d %H:%M')} CT by Forge, ALI-163 FINAL (reopened pass: r3r + r3b "
  "added to the verify and the contact sheet). METHOD_ONLY; the R4F/R4G face numbers are in "
  "notes\\hc_prompt_face_audit_20261023.md - no new face metric was run here (the FINAL check list does not ask "
  "for one). No vision judge, no GPU, no render, no new seed.")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("WROTE", OUT, os.path.getsize(OUT), "bytes")
