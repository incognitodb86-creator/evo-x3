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
w("METHOD_ONLY. Review = contact sheet + objective checks only (ffprobe -count_packets, ffmpeg stream copy, "
  "sha256, status.log greps). NO vision judge was called on any output (superseded 2026-10-22). "
  "No quality redo was requested. **KEEP is Derrick's only.**")
w("")
w(f"Contact sheet: `{SHEET}` (built by notes\\ali163_hc_final_sheet.py from frames extracted by "
  "notes\\ali163_hc_final_media.ps1 at t = 0.50 / 2.60 / 5.00 / 7.40 / 9.60 s; rows 0 and 1 use the SAME "
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
  "(Derrick 1:07 PM CT). **jobs is now 35 = the R-line cap, so no further R-line render can be requested** - the "
  "extra 120 min / 10 jobs are the ALI-173 bakeoff's. This reading (used_min 450.8 / jobs 35) is the recorded "
  "BAKEOFF START.")
w("")
w("## Table (all 8 clips: 2 old-batch reference + 6 requested R-clips)")
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
          "the runner refuses 'id already used') and the R-line job cap 35/35 is reached. "
          "A re-render needs a NEW id (e.g. ali147_pool_hc_r7_s51130007) + a cap decision from Max/Derrick - "
          "reported, not self-requested (PROMPT.md: real failures = rc 4 or TIMEOUT; rc=2 is a static-check "
          "failure, and STUCK is reported, never re-requested).")
w("")
w("## Objective check list (the FINAL items)")
w("")
ok = all(obj[c]["ok"] for c in obj if c.startswith("ali147_pool_hc_r"))
rows_ok = []
for label, cid, pick, refs, line, batch in CLIPS:
    r = obj[cid]
    v = r.get("video") or {}
    item = (f"`{cid}`: result.json {'ok' if r.get('ok') else 'NOT ok (rc=%s)' % r.get('rc')}; "
            f"JOB start + JOB end quoted above; 'JOB error' = {r.get('job_error_grep', 0)} and "
            f"'CLIP_SKIP' = {r.get('clip_skip_grep', 0)}; probe {v.get('w')}x{v.get('h')} {v.get('fps')} "
            f"{v.get('packets')} f (expected {r['expected_frames']}); audio stream present = "
            f"{bool(r.get('audio_stream'))}; m4a per clip = {r.get('m4a_exists', False)}")
    rows_ok.append((cid, r.get("ok"), item))
for cid, o, item in rows_ok:
    w(f"- [{'x' if o else ' '}] {item}")
w("")
w("The 5 requested R-clips that rendered (r1, r2, r4, r5, r6) pass every objective item: 1344x768, 24/1 fps, "
  "243 packets = the R1 count, an audio stream, an extracted `<id>.m4a` (aac, 32000 Hz, 2 ch, 10.125 s), "
  "0 'JOB error' / 0 'CLIP_SKIP'. r3 is listed with its failure (rc=2 static check, clip 3 has no render). "
  "The two old-batch clips (c1, c2) are in the table + row 0 of the contact sheet for the side-by-side; "
  "they are 481 f / 20.04 s by design and are not part of the R batch.")
w("")
w("## Files made by this pass")
w("- notes\\ali163_hc_final_check.py (objective dump) -> notes\\ali163_hc_final_objective.json")
w("- notes\\ali163_hc_final_media.ps1 (m4a stream copy + 5 frames per clip) -> notes\\hc_final_frames\\*.png")
w("- notes\\ali163_hc_final_sheet.py -> notes\\hc_redo_20261023_contact.png (7 rows x 5 frames, labelled)")
w(f"- this file: {OUT}")
w("")
w(f"Written {datetime.now().strftime('%Y-%m-%d %H:%M')} CT by Forge, ALI-163 FINAL. "
  "METHOD_ONLY; face similarity numbers are in notes\\hc_prompt_face_audit_20261023.md (R4F/R4G) - no new "
  "face metric was run here (FINAL check list does not ask for one). No vision judge, no GPU, no render, "
  "no new seed.")
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("WROTE", OUT, os.path.getsize(OUT), "bytes")
