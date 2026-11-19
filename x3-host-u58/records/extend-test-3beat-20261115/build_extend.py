#!/usr/bin/env python3
"""Build + lint for the 3-beat extend test (Prompt maker, 2026-11-15). Reuses the v2 pack's lint() unchanged.
Never deletes; overwrites only its own outputs (beat1.txt, beat2.txt, beat3.txt, lint_report.json)."""
import json, os, re, sys
from beats_data import BEATS, LIGHT, S1_BIO, S2_BIO, ROOM, CAM, WARD_B1, WARD_CONT, WARD_LINE, V2
sys.path.insert(0, V2)
import build_pack as bp  # noqa: E402
from clips_data import CLIPS as V2_CLIPS  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SETP = ("the charcoal wall, the dark hardwood floor, the low bed with the grey upholstered headboard and grey-lavender "
        "sheets, and the warm lamp light from frame left with soft dim fill")

def compose(b):
    out = []
    for i, (t, key, text) in enumerate(b["shots"], 1):
        if i == 1:
            s = f"[Shot 1] The camera holds a static {CAM[key]}, shallow depth of field. {LIGHT} "
            if b["id"] > 1:
                s += WARD_LINE + " "
            s += text
        else:
            s = f"[Shot {i}] At {t}, the camera cuts to {bp.art(CAM[key])}. The camera holds a static shot. {text}"
        out.append(s)
    return "\n".join(out) + " " + b["sfx"]

def build(b):
    desc = compose(b)
    if b["id"] == 1:
        p1 = (f"<Picture 1> is the start still GI183, the reference image defining the exact visual appearance, identity, face and hairstyle of "
              f"<Subject 1> and <Subject 2>, and {ROOM}, its light and the opening pose and framing of this clip: {b['frame0']}.")
        ward = WARD_B1
    else:
        p1 = (f"<Picture 1> is the start still GI183 that opened beat 1 of this same continuous take, the reference image defining the exact "
              f"visual appearance, identity, face and hairstyle of <Subject 1> and <Subject 2>, and {ROOM}; this beat opens on the last "
              f"moment of the previous beat: {b['frame0']}.")
        ward = WARD_CONT
    sd = [p1,
          f"<Subject 1> is the exact same woman shown in <Picture 1> of the reference pictures and in the first 5 seconds of this clip, preserving her face, hairstyle, body, skin and figure with complete fidelity; {S1_BIO}; she is (S1) and stays on screen right.",
          f"<Subject 2> is the exact same man shown in <Picture 1> of the reference pictures and in the first 5 seconds of this clip, preserving his face, hair, stubble, body, skin and build with complete fidelity; {S2_BIO}; he is (S2) and stays on screen left.",
          ward]
    if b["id"] == 1:
        sd.append("The light clothing worn at the start of this shot is the clothing of <Picture 1>; during the shot the crotch strip of the pink bikini bottom is pulled aside to her right buttock and stays there while its side straps stay on her hips, and his navy boxer briefs slide down to mid-thigh and stay there, so the bodies that become bare are the same bodies the photograph shows.")
    sd.append(bp.HAND)
    pic = (f"partially_preserved - {SETP} are kept; the framing follows the move into the new position" if b["id"] == 1
           else f"fully_preserved - {SETP} are kept; the framing continues from the previous beat")
    ra = ["<Subject 1> (appears in [Shot 1]): fully_preserved - her face, hairstyle, body, skin and figure are kept from <Picture 1> in every shot",
          "<Subject 2> (appears in [Shot 1]): fully_preserved - his face, hair, stubble, body, skin and build are kept from <Picture 1> in every shot",
          f"<Picture 1> ([Shot 1] scene/identity anchor): {pic}",
          "Her pink sheer bikini top, white over-the-knee high-heel boots, thin gold belly chain at her waist and necklace: fully_preserved - they stay on her for the whole take"]
    if b["id"] == 1:
        ra += ["The pink bikini bottom of <Picture 1>: partially_preserved - it is an action in the story: its crotch strip is pulled aside to her right buttock during the shot and stays there for the rest of the take, its side straps staying on her hips",
               "The navy boxer briefs of <Picture 1>: partially_preserved - it is an action in the story: they slide down to his mid-thigh during the shot and stay there for the rest of the take"]
    else:
        ra += ["The pink bikini bottom: partially_preserved - it stays on her hips with its crotch strip pulled aside to her right buttock for the whole beat",
               "The navy boxer briefs: partially_preserved - they stay slid down at his mid-thigh for the whole beat"]
    txt = ("subject_definitions:\n" + "\n".join(sd) + "\n\nsummary:\n[reference generation] " + b["summary"] +
           "\n\nretention_analysis:\n" + "\n".join(ra) + "\n\ndetailed_description:\n" + desc + "\n")
    return txt, desc

# builder gate mirrors (live/build_request.py, box copy)
ACT_ASK = re.compile(r"\b(?:sex|fuck\w*|missionary|doggy\w*|cowgirl|blow ?job|bj|oral|suck\w*|deepthroat\w*|penetrat\w*|rides? him|position)\b", re.I)
ACT_RE = re.compile(r"(?i)\b(?:thrust\w*|strokes?|stroking|rides?|riding|pump\w*|grind\w*)\b")
PEN_RE = re.compile(r"\b(sheathed|fully seated|inside her|enters her|enters|seats fully|astride)\b", re.I)
WALK_RE = re.compile(r"(?i)\b(?:walks?|steps?|strolls?|crosses?|kneels?|sits?\s+down|lies?\s+(?:down|back)|gets?\s+(?:up|down|onto)|climbs?\s+onto|lowers?\s+(?:herself|himself|onto)|turns?\s+(?:and|toward|towards))\b")
PLACE_RE = re.compile(r"(?i)\b(bedroom|bathroom|shower|kitchen|hallway|corridor|living\s+room|parlor|lounge|bar|diner|booth|office|study|balcony|terrace|patio|garden|pool|beach|stage|studio|gym|locker\s+room|car|backseat|elevator|stairwell|rooftop|alley|street|forest|cabin|tent|yacht|deck|cellar|attic|barn|warehouse|club)\b")
DOGGY_BACK = re.compile(r"(?i)\bpresses her back (?:down )?(?:against|into|to) the (?:mattress|sheets|bed)")

def main():
    all_lines = {}
    for c in V2_CLIPS:  # catch reuse of any v2 line
        for _, l in bp.SPK_RE.findall(bp.compose(c)):
            all_lines.setdefault(l.strip().lower(), 100 + c["id"])
    wp = open("/workspace/u6/writer_pipeline_20261113/results5_xhigh/writer_prompt.md", encoding="utf-8").read()
    exs = wp[wp.find("EXAMPLES ("):wp.find("SHAPE (")]
    we = open("/home/box/agent-data/workflows/h3-prompting/references/worked-examples.md", encoding="utf-8").read()
    exs += "\n".join(re.findall(r"```text\n(.*?)```", we, re.S))
    exgrams = bp.ngrams(exs)
    BOILER = ("lens shallow depth", "depth of field", "mm lens", "camera holds a static", "five fingers", "pores", "fine hair",
              "stays buried in her", "flush against her", "hips flush", "past her lips toward", "medium two shot", "medium close up", "stays deep in her")
    report, prev = [], None
    for b in BEATS:
        txt, desc = build(b)
        with open(os.path.join(HERE, f"beat{b['id']}.txt"), "w", encoding="utf-8") as f:
            f.write(txt)
        c = dict(b, frames=b["window"])  # time checks run against the sampled window this prompt conditions
        issues, lines, words = bp.lint(c, desc, all_lines, prev)
        clones = [g for g in sorted(bp.ngrams(bp.D_RE.sub(" ", desc)) & exgrams) if not any(x in g for x in BOILER)]
        if clones: issues.append(f"6-word runs shared with examples: {clones[:4]}")
        shot1 = re.split(r"\[Shot 2\]", desc)[0]
        s1plain = bp.D_RE.sub(" ", shot1)
        if not ACT_ASK.search(b["summary"]): issues.append("summary is not an act ask")
        if not (ACT_RE.search(s1plain) or PEN_RE.search(s1plain)): issues.append("Shot 1 has no builder act word")
        if DOGGY_BACK.search(desc): issues.append("doggy back-press wording")
        if b["id"] > 1:
            if WALK_RE.search(bp.D_RE.sub(" ", desc)): issues.append(f"continuation walk-verb: {WALK_RE.search(desc).group(0)}")
            if PLACE_RE.search(bp.D_RE.sub(" ", desc)): issues.append(f"continuation place word: {PLACE_RE.search(desc).group(0)}")
            if b["shots"][1][0] and bp.tsec(b["shots"][1][0]) - 22 / 24 < 2.0: issues.append("visible part of Shot 1 under 2.0 s")
        report.append({"id": b["id"], "visible_frames": b["frames"], "window_frames": b["window"], "window_seconds": round(b["window"] / 24, 3),
                       "chars": len(txt), "shot_keys": [k for _, k, _ in b["shots"]], "spoken_words": words, "lines": lines, "issues": issues})
        prev = b
    tot = sum(b["frames"] for b in BEATS)
    with open(os.path.join(HERE, "lint_report.json"), "w") as f:
        json.dump({"beats": report, "total_visible_frames": tot, "total_seconds": round(tot / 24, 3)}, f, indent=1)
    for r in report:
        print(f"beat{r['id']} visible={r['visible_frames']}f window={r['window_frames']}f ({r['window_seconds']}s) chars={r['chars']} words={r['spoken_words']} "
              + ("OK" if not r["issues"] else "ISSUES: " + " | ".join(r["issues"])))
    print(f"TOTAL visible frames={tot} seconds={tot/24:.3f}")

if __name__ == "__main__":
    main()
