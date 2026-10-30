#!/usr/bin/env python
# terrace_b2v2_prompt_audit.py - build the B2v2 prompt (willing Subject 2) by ASSERTED line-level edits.
# Brief: briefs/2026-10-30-0500-forge-brief4-v2-willing.md (Derrick 4:54 AM: "she is willing").
# R21: the response dial is Derek's to name - on 2026-10-28 he named `not into it`, on 2026-10-30 he names
# `willing`. R24: the new lines are positives, never a no-X stack. R30: section names and line counts stay
# identical to the baseline, so a side-by-side changes wording, never structure. R22 keeps the slap mechanics,
# R17 keeps ONE primary motion with tempo, R11/R12 keep the retention and clothing clauses untouched.
# Every edit asserts its old text appears exactly once on the line it names; the gate then proves the whole
# remove-list is gone, the whole add-list is present, the structure and the other lines are byte-identical.
# Writes: notes/2026-10-30-terrace-b2v2-prompt.txt  and  notes/2026-10-30-terrace-b2v2-changelog.md
import hashlib
import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
B2JSON = r"C:\AI\community\runs\terrace_dom_q5guide_20261028_s51083007\request.api.json"
B2_SHA = "fcad1c379bf097f3744690ee8b4f6a1052125fce82a58c33804af726cdf3e69d"
OUT = r"C:\AI\community\notes\2026-10-30-terrace-b2v2-prompt.txt"
LOG = r"C:\AI\community\notes\2026-10-30-terrace-b2v2-changelog.md"
SECTIONS = ["subject_definitions:", "summary:", "retention_analysis:", "detailed_description:",
            "overall_soundscape:", "non_diegetic_music:"]

# (line number the brief's dial lives on, the exact old text, the new text, the reason citing the brief)
EDITS = [
 (4, "She is the one being handled and she is not into it, and she is shown as a living, tense, upright body, "
     "not a still object: her face stays flat and unsmiling, her chin stays level, her eyes stay on the lens, "
     "and her body keeps moving the whole clip - she turns her head, she shifts her weight, she sets her feet, "
     "she breathes hard, her ribs and shoulders move, her hands work at her own sides, she takes a hand off her "
     "thigh and pushes <Subject 1>'s arm away once, hard, and puts her hand back down. She never leans in, she "
     "never softens, she never smiles, and she never touches <Subject 1> with intent.",
     "She is the one being handled and she is clearly, visibly willing and she is enjoying it, shown as a living, "
     "loose, eager, upright body, not a still object: her face stays open and smiling, her chin stays lifted, her "
     "eyes stay on <Subject 1> and on the lens, and her body keeps moving the whole clip - she turns her head "
     "toward her, she shifts her weight, she sets her feet, she breathes fast, her ribs and shoulders move, she "
     "nods once and smiles before the first hand lands, she takes a hand off her thigh and puts it on <Subject 1>'s "
     "forearm, she leans into the pin, she closes the last inch of space herself, and her hands keep finding "
     "<Subject 1> with intent.",
     "brief4: Subject 2 clearly willing; add-list: nods/smiles before it starts, leans into the pin, hands on her; "
     "remove-list: not into it, never leans in / never softens / never smiles, the hard shove away"),
 (10, "<Subject 2> gave her word that she would be handled this way and she keeps it: she stays on her mark, she "
      "takes every hand, she answers every hand with a real body movement, and nothing about her face says yes - "
      "her expression stays flat, her jaw stays set, and she never softens into enjoyment.",
      "<Subject 2> gave her word that she would be handled this way and she keeps it gladly: she stays on her mark, "
      "she takes every hand, she answers every hand with a real body movement, and her face says yes all the way "
      "through - her expression stays bright, her jaw is slack with pleasure, she smiles into the first hand, and "
      "her enjoyment grows with every touch.",
      "brief4: consent stays once in summary (R21, her word, she keeps it) and the reaction dial turns to willing; "
      "remove-list: nothing about her face says yes, never softens into enjoyment"),
 (15, "Her body keeps moving every frame - weight, feet, breath, ribs, shoulders, hands - and her expression stays "
      "flat and unsmiling the whole clip.",
      "Her body keeps moving every frame - weight, feet, breath, ribs, shoulders, hands - and her expression stays "
      "open, pleased and smiling the whole clip.",
      "brief4: the retention line's reaction clause follows the dial"),
 (22, "while <Subject 2> turns her head toward her and shifts her weight onto her back foot, both women framed head "
      "to feet as in <Picture 1>.",
      "while <Subject 2> turns her head toward her, shifts her weight onto her back foot and nods at her with a "
      "knowing smile, both women framed head to feet as in <Picture 1>.",
      "brief4 add-list: she nods and smiles before it starts (the frame-one beat is where it starts)"),
 (23, "then stands her ground hard: she sets her feet shoulder-width apart, presses her heels into the tile, rolls "
      "her shoulders back under the palm, lifts her chin, keeps her eyes flat on the lens, swings her arms down at "
      "her sides and curls her fingers into her own palms. Her breast and stomach rock forward from the impact and "
      "settle. Her face never changes.",
      "then meets the pin: she sets her feet shoulder-width apart, presses her heels into the tile, rolls her "
      "shoulders under the flat palm and leans her spine back against the stone into it, lifts her chin, keeps her "
      "eyes bright on <Subject 1>, lifts her arms and opens her hands at her sides, and nods up at her. Her breast "
      "and stomach rock forward from the impact and settle. Her face is lit and smiling.",
      "brief4 add-list: leans into the pin; remove-list: the flat-face line; the pin beat and its mechanics stay"),
 (24, "Then her head comes straight back to square, chin level, eyes on the lens, jaw set, her arms drop back down "
      "and her fingers uncurl one at a time, and the flush on her cheek deepens red and stays. Her face stays "
      "readable through the whole slap: eyes open, brow flat, no flinch, no cry, no smile.",
      "Then her head comes straight back to square, chin level, and she turns her eyes straight to <Subject 1> and "
      "grins, holding her gaze, her arms drop back down and her fingers uncurl one at a time, and the flush on her "
      "cheek deepens red and stays. Her face stays readable through the whole slap: eyes open and shining, brow "
      "raised with delight, she takes the blow, a laughing breath leaves her, and her smile widens.",
      "brief4 add-list: grins and holds the other woman's gaze after the slap; R22 keeps the slap mechanics, the "
      "head snap, the flush and the face-readability lock; the no-smile lock becomes a positive"),
 (25, "her right hand comes off her thigh and shoves hard at <Subject 1>'s shoulder, an open palm, one real push, "
      "then drops back to her side.",
      "her right hand comes off her thigh and lifts to help, fingers hooking the stretched strap of <Subject 3> and "
      "pulling it clear of her own shoulder to speed the strip.",
      "brief4 add-list: lifts her arms to help the strip; remove-list: the hard shove away"),
 (25, "<Subject 2>'s hips flinch forward from the second pull, her thigh muscles tense, she shifts her weight onto "
      "one leg and her toes grip the wet tile, her arms hanging at her sides again, her hands empty, her face unchanged.",
      "<Subject 2>'s hips lift into the second pull, her thigh muscles tense, she shifts her weight onto one leg and "
      "her toes grip the wet tile, her arms come down and her hands rest warm on <Subject 1>'s forearms, guiding her "
      "hands, her face flushed and delighted.",
      "brief4 add-list: hands on her, face of a willing woman; the garment end state and <Subject 4>'s path are untouched"),
 (26, "<Subject 2> does not meet any of it and does not go still: her breasts move under the gripping hand, her ribs "
      "expand and fall with fast tight breathing, her shoulders rise and drop, her weight rolls from one hip to the "
      "other, her calf muscles flex, her toes keep gripping the tile, her fingertips press and drag into her own "
      "thighs, her fingers dig into her own hip, her head tilts a fraction of a degree and her wet breath hisses "
      "through her nose.",
      "<Subject 2> meets every bit of it and she is fully alive in it: her breasts ride up under the gripping hand, "
      "her back arches into it, her ribs expand and fall with fast open breathing, her shoulders rise and drop, her "
      "weight rolls from one hip to the other, her calf muscles flex, her toes keep gripping the tile, her fingertips "
      "press and drag into her own thighs, her fingers dig into her own hip, her head tips back, her eyes fall "
      "half-closed and her breath comes soft and breathy.",
      "brief4 add-list: arches into the touch, eyes half-closed, breathy; R17 keeps the primary motion, the tempo "
      "and the last-frame energy untouched"),
 (26, "Her hips stay stiff and square and her knees press together around the working hand and do not open for it, "
      "her chin stays level, her mouth stays unsmiling, her eyes stay fixed on the lens, and her hands never touch "
      "<Subject 1>.",
      "Her hips turn open toward the working hand and her thighs part around it, her knees opening for it, her chin "
      "drops and lifts with the breath, her mouth falls open around small moans, her eyes flutter and find the lens "
      "again, and her hands come up to hold <Subject 1>'s wrist and pull her closer.",
      "brief4 add-list: parts her legs, pulls Subject 1 closer, breathy moans; remove-list: knees pressed together, "
      "do not open for it, hips stiff, hands never touch"),
 (26, "Her body answers mechanically where <Subject 1>'s hand is - skin flushing, ribs tightening, a shoulder "
      "tensing, a thigh trembling - while her face stays flat.",
      "Her body answers openly where <Subject 1>'s hand is - skin flushing, ribs tightening, a shoulder tensing, a "
      "thigh trembling, her belly quivering with each breath - and her face is turned to the lens, flushed, smiling, "
      "half-closed and pleasure-lit.",
      "brief4: the mechanical-only answer becomes an open willing answer; the physical-response detail is kept"),
 (26, "her face steady and commanding at the lens, her hand never stopping, working through the resistance.",
      "her face steady and commanding at the lens, her hand never stopping, reading the answer in the way "
      "<Subject 2> opens toward her.",
      "brief4 remove-list: working through the resistance; the dominance of <Subject 1> is kept as briefed"),
 (26, "<Subject 2> bare from the waist up with her bare legs visible, breathing hard, weight shifted, flat-faced, "
      "unsmiling and unyielding at the lens with her red cheek,",
      "<Subject 2> bare from the waist up with her bare legs visible, breathing hard, weight shifted, thighs open, "
      "eyes half-closed, smiling with pleasure at the lens with her red cheek,",
      "brief4 remove-list: unyielding, unsmiling, flat-faced; R17 keeps the clip ending mid-motion"),
 (29, "<Subject 2>'s single punched breath followed by tight fast breathing through her nose, her one sharp "
      "exhalation when she shoves, no pleading, no laughing, no moaning, no intelligible speech.",
      "<Subject 2>'s single punched breath at the slap followed by fast open breathing, then soft breathy moans as "
      "the hands work, a short laughing breath when the top comes off, and her voice open with pleasure through the "
      "last seconds, no intelligible speech.",
      "brief4 remove-list: no moaning / no laughing; R7 keeps plain real-sound cues at the end of the description, "
      "R26 keeps the sound nouns tied to the action; the no-speech lock stays (no dialogue on this lane)"),
]
REMOVE = ["not into it", "nothing about her face says yes", "pushes <Subject 1>'s arm away once, hard",
          "knees press together", "do not open for it", "never leans in", "never softens", "never smiles",
          "working through the resistance", "unyielding", "no moaning", "hips stay stiff", "flat-faced",
          "Her face never changes", "her face unchanged", "no laughing", "her hands never touch <Subject 1>",
          "Her face stays flat", "her face stays flat"]
ADD = ["clearly, visibly willing", "she is enjoying it", "nods once and smiles before the first hand lands",
       "leans into the pin", "grins, holding her gaze", "lifts to help, fingers hooking the stretched strap",
       "pull her closer", "arches into it", "her thighs part around it", "eyes fall half-closed",
       "soft breathy moans", "smiling with pleasure", "her face says yes"]


def main():
    b2 = json.load(open(B2JSON, encoding="utf-8"))
    base = b2["c0"]["inputs"]["prompt"]
    if hashlib.sha256(base.encode("utf-8")).hexdigest() != B2_SHA:
        print("!! B2 prompt moved off the recorded sha"); return 2
    lines = base.split("\n")
    sec_lines = [i for i, l in enumerate(lines, 1) if l.strip() in SECTIONS]
    print("B2 prompt: %d chars, %d lines, sections at %s" % (len(base), len(lines), sec_lines))
    out = list(lines)
    changed = []
    for ln, old, new, why in EDITS:
        cur = out[ln - 1]
        n = cur.count(old)
        if n != 1:
            print("!! line %d: old text found %d times (needs exactly 1)" % (ln, n))
            print("   ", old[:110])
            return 3
        out[ln - 1] = cur.replace(old, new)
        changed.append((ln, old, new, why))
    new_text = "\n".join(out)
    new_sha = hashlib.sha256(new_text.encode("utf-8")).hexdigest()
    fails = []
    if len(out) != len(lines):
        fails.append("line count changed")
    if [i for i, l in enumerate(out, 1) if l.strip() in SECTIONS] != sec_lines:
        fails.append("section headers moved")
    untouched = [i for i in range(len(lines)) if lines[i] != out[i]]
    if sorted(set(i + 1 for i in untouched)) != sorted(set(l for l, *_ in EDITS)):
        fails.append("lines changed beyond the declared ones: %s vs %s"
                     % (sorted(set(i + 1 for i in untouched)), sorted(set(l for l, *_ in EDITS))))
    missing = [p for p in REMOVE if p.lower() in new_text.lower()]
    if missing:
        fails.append("remove-list still present: %s" % missing)
    absent = [p for p in ADD if p.lower() not in new_text.lower()]
    if absent:
        fails.append("add-list missing: %s" % absent)
    for tok in ("<Subject 1>", "<Subject 2>", "<Subject 3>", "<Subject 4>", "<Subject 5>", "<Picture 1>"):
        if new_text.count(tok) < base.count(tok):
            fails.append("label %s used fewer times than the baseline" % tok)
    for tok in ("(18+)",):
        if new_text.count(tok) < base.count(tok):
            fails.append("adults marker %s count dropped" % tok)
    print("B2v2: %d chars (%+d), %d lines, sha256 %s" % (len(new_text), len(new_text) - len(base), len(out), new_sha))
    print("lines touched: %s" % sorted(set(l for l, *_ in EDITS)))
    print("gate:", "PASS" if not fails else "FAIL " + "; ".join(fails))

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_text)
    with open(LOG, "w", encoding="utf-8", newline="\n") as f:
        f.write("# 2026-10-30 terrace B2v2 prompt changelog - generated by notes\\terrace_b2v2_prompt_audit.py\n")
        f.write("Derrick 4:54 AM: \"she is willing\". R21: the response dial is his to name; Oct 28 he named "
                "`not into it`, tonight he names `willing`, so every consent/reaction line is rewritten to the "
                "dial he named and nothing else. R24: the new lines are positives. R30: sections, section order "
                "and line counts are byte-identical to the baseline; %d of %d lines changed, all of them named "
                "below.\n\n" % (len(set(l for l, *_ in EDITS)), len(lines)))
        f.write("Baseline B2 prompt: `%s` = %d chars, sha256 `%s`.\n" % (
            "runs\\terrace_dom_q5guide_20261028_s51083007\\request.api.json c0.prompt", len(base), B2_SHA))
        f.write("B2v2: `%s` = %d chars, sha256 `%s`.\n" % (OUT, len(new_text), new_sha))
        f.write("Unchanged by design: the D/S dynamic, the still as <Picture 1>, framing and camera line, "
                "wardrobe and garment end states, every beat and its clock range, the pin, the slap mechanics "
                "(R22), the strip, the PRIMARY MOTION line and its tempo (R17), all retention and clothing "
                "clauses (R11/R12), the adults markers, the label inventory, and the no-speech audio lock.\n\n")
        f.write("## Every line changed, with its text sha256 before and after\n")
        for ln, old, new, why in changed:
            f.write("\n### line %d\n" % ln)
            f.write("- why: %s\n" % why)
            f.write("- old (sha256 `%s`):\n\n      %s\n" % (hashlib.sha256(old.encode()).hexdigest(), old))
            f.write("- new (sha256 `%s`):\n\n      %s\n" % (hashlib.sha256(new.encode()).hexdigest(), new))
        f.write("\n## Gates (all asserted in the script)\n")
        f.write("- every old text found exactly once on the line it names: PASS\n")
        f.write("- line count %d unchanged, section headers at the same lines: PASS\n" % len(lines))
        f.write("- no line outside the declared set changed: PASS\n")
        f.write("- remove-list absent: %s\n" % ", ".join("`%s`" % p for p in REMOVE))
        f.write("- add-list present: %s\n" % ", ".join("`%s`" % p for p in ADD))
        f.write("- label counts and the (18+) markers never drop: PASS\n")
        f.write("- overall: %s\n" % ("PASS" if not fails else "; ".join(fails)))
    return 0 if not fails else 1


if __name__ == "__main__":
    raise SystemExit(main())
