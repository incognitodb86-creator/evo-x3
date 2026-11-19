"""BQ1d TASKS.md writer (CPU only). Repairs the escape-corrupted BQ1d insert (a python -c
non-raw string ate \\b and \\a: 'notes\\body' -> backspace + 'ody') and writes the same text
clean, with FORWARD SLASHES ONLY so no backslash escape can ever touch it again.

Verifies: no control chars (ord < 32) outside newlines in TASKS.md, BQ1d is [x] with a result,
exactly 5 BQ1-template lines (HB0 note + HB1/HB2/HB3/HB4), 18 unchecked lines.
"""
import io
import re

P = "C:/Users/derek/5slock/ralph-community/TASKS.md"
NOTE = ("  BQ1 TEMPLATE (BQ1d 2026-10-23, ticked): this arm uses the IMPROVED BQ1 template - the approved "
        "HC3 start still as ref_images.ref_image_1 (the body/scene reference, <Picture 1>) on c0 AND c1, "
        "the 2 face crops as face-only refs (builder notes/ali163_hc_bq1_build.py, prompts "
        "notes/hc_r3b_c0.txt + notes/hc_r3b_c1.txt, method notes/body_quality_improve_20261023.md). "
        "Proof render ali147_pool_hc_r3b_s51130003 (ok=True rc=0, 243 f, 1344x768, 24 fps, audio aac) "
        "against the r3r control in notes/body_quality_r3b_vs_r3r_contact.png. No vision judge; KEEP is "
        "Derrick's.")
HB0 = ("  HB0 CONTROL + the BQ1 TEMPLATE line (BQ1d 2026-10-23): HB0 = r3r ali147_pool_hc_r3r_s51130003 keeps "
       "the OLD wiring (2 face crops only, the approved start still is NOT in that graph at all - proved in "
       "notes/ali163_hc_bq1d_objective.json), so HB0 is the before-shot; the improved BQ1 template (start "
       "still = ref_image_1 body/scene on c0 AND c1 + face crops face-only) is what r3b rendered and what "
       "HB1, HB2, HB3 and HB4 must use. Side-by-side = notes/body_quality_r3b_vs_r3r_contact.png "
       "(2 clips x 5 stamps at t = 0.50 / 2.60 / 5.00 / 7.40 / 9.60 s). No new job, no vision judge.")
RES = (" - DONE 2026-10-23 ~17:45 CT (BQ1d pass, CPU only, 0 GPU minutes: no ComfyUI port call, no comfy_ctl, "
       "no llama-swap, no download, no render, no vision judge, no image opened): r3b verified "
       "p7/jobs/ali147_pool_hc_r3b_s51130003.result.json ok=True rc=0 wall=8.8m; status.log 17:20:19 CT JOB "
       "start -> 17:28:20 CT JOB end ok, 0 JOB error / 0 CLIP_SKIP; ffprobe -count_packets 1344x768 24/1 fps "
       "243 packets, audio aac 32000 Hz 2ch, demuxed m4a 166,134 B (sha8 bceb4cd6), mp4 3,527,348 B sha8 "
       "d125b8fe, graph sha8 ce01686e = the BQ1b file byte-for-byte; seed 51130003, 124+119 f, euler, 10 "
       "steps, shift 10/3, 2 SamplerCustomAdvanced (single pass), overall_soundscape: line present, offline "
       "static_check clean. THE REWIRE IS PROVED IN THE RENDERED GRAPH: r3b c0 AND c1 are "
       "MiniMaxH3ReferenceToVideo with ref_image_1 = community/hc/HC3_lesbian_beach.jpg (the approved start "
       "still = body/scene, ref_image_size match) + ref_image_2/3 = the 2 face crops; the r3r control carries "
       "NO start still at all (the BQ1 body defect). Sheet notes/body_quality_r3b_vs_r3r_contact.png built by "
       "notes/ali163_hc_bq1d_sheet.py = 2186x834, 1,291,630 B, 2 clips x 5 stamps at the SAME t = 0.50 / 2.60 "
       "/ 5.00 / 7.40 / 9.60 s + a reference row; every label cell carries id/seed/still/refs/ok/rc/WxH/fps/"
       "packets/audio/sha read from notes/ali163_hc_bq1d_objective.json (data, not typed). Gates 22/22 "
       "(check, 3 self-destruct probes) + 21/21 (frames: non-black, the same t across clips differs = two "
       "distinct renders, f0 vs f4 differs = motion) + 4/4 (sheet: a missing stamp paints red and fails). "
       "HB0-HB4 TASKS lines each got the BQ1-template line. Derrick compares and picks KEEP; no redo for "
       "quality. TOOL BUG FOUND IN THIS PASS: the insert was first written by a python -c non-raw string and "
       "backslash-b / backslash-a became backspace / bell ('notes/body' -> 'notesody'); rewritten with "
       "forward slashes and the file re-verified control-char-free. Rule: never write Windows paths through a "
       "non-raw python string - use forward slashes, a raw string or a quoted heredoc.")

raw = io.open(P, encoding="utf-8").read()
lines = raw.split("\n")
kept = []
for ln in lines:
    if ln.startswith("  BQ1 TEMPLATE (BQ1d 2026-10-23") or ln.startswith("  HB0 CONTROL + BQ1 TEMPLATE note"):
        continue
    if re.match(r"^- \[.\] BQ1d SIDE-BY-SIDE", ln):
        ln = re.split(r" - DONE 2026-10-23 ~17:45 CT", ln)[0]
        ln = ln.replace("- [ ] BQ1d", "- [x] BQ1d", 1) + RES
    kept.append(ln)
out = []
for ln in kept:
    out.append(ln)
    if ln.startswith("- HB HARDCORE COMMUNITY BAKEOFF"):
        out.append(HB0)
    elif re.match(r"^- \[.\] HB[1234] ", ln):
        out.append(NOTE)
text = "\n".join(out)

ctrl = [(i + 1, repr(l[:60]), [ord(c) for c in l if ord(c) < 32])
        for i, l in enumerate(text.split("\n")) if any(ord(c) < 32 for c in l)]
gates = [("no control chars in TASKS.md (the escape trap is gone)", not ctrl, str(ctrl)[:220]),
         ("BQ1d is [x] with a result", bool(re.search(r"^- \[x\] BQ1d SIDE-BY-SIDE.* - DONE 2026-10-23",
                                                      text, re.M)), "tick + result line"),
         ("5 BQ1-template lines (HB0 note + HB1 + HB2 + HB3 + HB4)",
          text.count("BQ1 TEMPLATE (BQ1d 2026-10-23, ticked)") == 4 and "HB0 CONTROL + the BQ1 TEMPLATE line" in text,
          f"note={text.count('BQ1 TEMPLATE (BQ1d 2026-10-23, ticked)')}"),
         ("every BQ1-template line sits directly under its HB line",
          all(out[i].startswith("  BQ1 TEMPLATE") and re.match(r"^- \[.\] HB[1234] ", out[i - 1])
              for i in range(len(out)) if out[i].startswith("  BQ1 TEMPLATE")), "placement"),
         ("unchecked lines 18 and BQ1d not among them",
          text.count("\n- [ ] ") == 18 and "- [ ] BQ1d" not in text,
          f"open={text.count(chr(10) + '- [ ] ')}"),
         ("no stray 'notesody'/'notesli' corruption left", "notesody" not in text and "notesli163" not in text,
          "scan")]
io.open(P, "w", encoding="utf-8", newline="\n").write(text)
bad = [g for g in gates if not g[1]]
for n, ok, det in gates:
    print(("PASS " if ok else "FAIL ") + n + ("  [" + str(det)[:180] + "]" if det else ""))
print("GATES", len(gates) - len(bad), "/", len(gates),
      "ALL CHECKS PASS" if not bad else "CHECKS FAILED: " + "; ".join(g[0] for g in bad))
raise SystemExit(0 if not bad else 1)
