#!/usr/bin/env python3
"""PQ1 audit of the shipped hc_r* prompts, with real line numbers.

CPU only. Every number it prints is read off the file in this run, because an earlier
audit pass in this iteration published line numbers and word counts that this script
then proved wrong (hc_r3_c0.txt is 5151 bytes / 23 lines on disk, not 6657 bytes / 78
lines; the stale sentence is at line 2, not 27). So: no hand-written citations.

  python -m py_compile ali163_pq1_audit.py
  python ali163_pq1_audit.py
"""
import glob
import io
import os
import re

NOTE = os.path.dirname(os.path.abspath(__file__))
BEAT = re.compile(r"\bAt \d\d:\d\d(?:\.\d+)?,")
CAM = re.compile(
    r"\b(camera|lens)\b[^.]{0,160}?\b(push(es)? in|pull(s)? (out|back)|pan(s)? (left|right)|"
    r"truck(s)? (left|right)|tilt(s)? (up|down)|pedestal|arc shot|tracking shot|static shot|"
    r"shake(s)? (slightly|strongly)|zoom(s)? (in|out)|fixed|locked|slow dolly|dolly)",
    re.I | re.S,
)
AMPL = re.compile(r"with (small|large|subtle|large-scale|slow) amplitude|at (slow|fast|normal) speed", re.I)
SECTIONS = (
    "subject_definitions:",
    "summary:",
    "retention_analysis:",
    "detailed_description:",
    "integrated_multimodal_description:",
    "overall_soundscape:",
    "non_diegetic_music:",
)
PROBE_WORDS = ("amplitude", "speed", "fully_preserved", "reference generation", "video continuation")


def audit(path: str) -> dict:
    text = io.open(path, encoding="utf-8").read()
    lines = text.split("\n")
    low = text.lower()
    section = ""
    hits = {}
    desc = []
    sound = []
    for n, ln in enumerate(lines, 1):
        s = ln.strip().lower()
        head = next((h for h in SECTIONS if s.startswith(h)), "")
        if head:
            section = head
            ln = ln.strip()[len(head):]  # content may sit on the header line itself
        for w in PROBE_WORDS:
            if w in ln.lower() and w not in hits:
                hits[w] = n
        m = BEAT.search(ln)
        if m and "beats" not in hits:
            hits["beats"] = n
            hits["beat@"] = m.group(0)
        cm = CAM.search(ln)
        if cm and "camera@" not in hits:
            hits["camera@"] = n
            hits["camera_text"] = re.sub(r"\s+", " ", cm.group(0))[:150]
        if section in ("detailed_description:", "integrated_multimodal_description:"):
            desc.append(ln)
        if section == "overall_soundscape:":
            sound.append(ln)
    body = "\n".join(desc)
    soundbody = "\n".join(sound)
    summ = ""
    for n, ln in enumerate(lines, 1):
        if ln.strip().lower().startswith("summary:"):
            summ = re.sub(r"\s+", " ", ln.strip()[len("summary:"):].strip() or (lines[n] if n < len(lines) else ""))
            hits["summary_line"] = n
            break
    negs = re.findall(r"\b(?:no|never|without|not)\s+[a-z][a-z ,]{0,60}", body.lower() + "\n" + soundbody.lower())
    return {
        "name": os.path.basename(path),
        "bytes": len(text.encode("utf-8")),
        "lines": len(lines),
        "desc_words": len(body.split()),
        "sound_words": len(soundbody.split()),
        "stale_only_ref": low.count("only visual reference"),
        "pic_lines": sum(1 for l in lines if re.match(r"^\s*<Picture \d>", l)),
        "subj_lines": sum(1 for l in lines if re.match(r"^\s*<Subject \d>", l)),
        "video_lines": sum(1 for l in lines if "<Video 1>" in l),
        "beats": len(BEAT.findall(body)),
        "amplitude": bool(AMPL.search(body)),
        "summary": summ[:220],
        "neg_count": len(negs),
        "neg_sample": [re.sub(r"\s+", " ", x)[:48] for x in negs[:4]],
        "hits": hits,
    }


def main() -> int:
    files = sorted(glob.glob(os.path.join(NOTE, "hc_r*_c*.txt")))
    if not files:
        print("AUDIT FAILED: no hc_r*_c*.txt in", NOTE)
        return 1
    rows = [audit(f) for f in files]
    for r in rows:
        print(
            "%-15s bytes=%-5d lines=%-3d descw=%-4d soundw=%-4d beats=%-2d ampl=%d stale=%d "
            "pics=%d subj=%d video=%d negs=%d"
            % (
                r["name"],
                r["bytes"],
                r["lines"],
                r["desc_words"],
                r["sound_words"],
                r["beats"],
                1 if r["amplitude"] else 0,
                r["stale_only_ref"],
                r["pic_lines"],
                r["subj_lines"],
                r["video_lines"],
                r["neg_count"],
            )
        )
        for k, n in sorted((kv for kv in r["hits"].items() if isinstance(kv[1], int)), key=lambda kv: kv[1]):
            extra = " :: " + r["camera_text"] if k == "camera@" else (" :: " + r["summary"][:150] if k == "summary_line" else "")
            print("      %-14s line %d%s" % (k, n, extra))
        if r["neg_sample"]:
            print("      negations      " + " | ".join(r["neg_sample"]))
    print("files=%d" % len(rows))
    print("PQ1 AUDIT DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
