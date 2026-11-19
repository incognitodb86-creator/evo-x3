"""strip_tease_20261030_bedroom01_s51103001 - prompt gate (h3-prompting R5-R12, R17, R23, R25, R27, R30).

Reads the cell's prompt file raw (newline=""), asserts the structure and the verbatim clauses, refuses the
contradiction phrases, the transition words, the negation stack, the banned skin words and the retired audio blocks,
and checks the timed beats total the requested length (124 frames / 24 fps = 5.1667 s).
Self-destruct probe: every detector must fire on a clone restored to the old (terrace) wording.
Run: C:\\AI\\director\\.venv\\Scripts\\python.exe C:\\AI\\community\\notes\\strip_tease_20261030_gate.py
"""
import re
import sys

PROMPT = r"C:\AI\community\runs\strip_tease_20261030_bedroom01\strip_tease_bedroom01_s51103001\prompt.txt"
FRAMES = 124
FPS = 24
SECTIONS = ["subject_definitions:", "summary:", "retention_analysis:", "detailed_description:"]

# R11 verbatim clause fragments (identity lock, hand lock) and R12 clothing-clause frame, R23 camera line, R6 tag
REQUIRED = [
    ("<Picture 1> is the reference image defining the exact visual appearance, identity, face and hairstyle of <Subject 1>", "R11-identity"),
    ("is the exact same woman shown in <Picture 1> of the reference pictures and in the first 5 seconds of this clip, preserving her face, hairstyle, body, skin and figure with complete fidelity", "R11-same-woman"),
    ("HAND ANATOMY HARD-LOCKED - exactly five separate fingers, readable knuckles, no melt, merge or extra digit", "R11-hands"),
    ("fully_preserved", "R11-retention"),
    ("is an action in the story", "R12-action-clause"),
    ("The light clothing worn at the start of this shot is the clothing of <Picture 1>; it is removed during the shot and stays", "R12-clothing"),
    ("so the bodies that become bare are the same bodies the photograph shows", "R12-clothing-end"),
    ("The camera holds a static shot.", "R23-camera"),
    ("[reference generation]", "R6-task-tag"),
    ("PRIMARY MOTION", "R17-primary-motion"),
    ("aged 28 by canon declaration", "R2-canon-age"),
]

# R27 contradiction phrases (measured to cancel the body reference)
ABSENT_R27 = [
    "body proportions",
    "are new and are not taken from",
    "used for the faces and the hair of the two women only",
    "These two crops are the only visual references",
    "carries no reference pictures at all",
]
# R8 transition words inside detailed_description
BANNED_TRANSITION = [r"\bthen\b", r"\bafter\b", r"\bafterwards\b", r"\bnext\b"]
# R24 negation stack (the R11 hand lock is the one allowed retention marker)
BANNED_NEGATION = [r"\bnever\b", r"\bwithout\b", r"\bnone\b", r"\bnot\b"]
# R25 skin-quality buzzwords
BANNED_SKIN = [r"\boiled\b", r"\bglossy\b", r"\bgloss\b", r"\bsheen\b", r"\bglistening\b", r"\bairbrushed\b", r"\bplastic\b"]
# R7 retired audio blocks
BANNED_AUDIO = [r"^overall_soundscape:", r"^non_diegetic_music:"]
# R2/R4 youth-guard vocabulary
BANNED_YOUTH = [r"\bgirl\b", r"\bgirls\b", r"\bteen\b", r"\bteenage\b", r"\bchild\b", r"\byoung\b", r"\bminor\b", r"\bbabe\b"]


def flat(text):
    """Section parsing is line-anchored, so CRLF must become LF first (the baseline file is CRLF)."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def sections(text):
    parts = re.split(r"(?m)^(?=[a-z_]+:$)", flat(text))
    return {p.split(":", 1)[0].strip(): p for p in parts if p.strip()}


def beats(text):
    out = []
    for m in re.finditer(r"(?m)^BEAT [A-Z]+,\s*([0-9.]+)-([0-9.]+)s", flat(text)):
        out.append((float(m.group(1)), float(m.group(2))))
    return out


def checks(text):
    """(required_present, absent_hits) as name lists; used by the gate and by the self-destruct probe."""
    text = flat(text)
    secs = sections(text)
    req_hits = [name for frag, name in REQUIRED if frag not in text]
    abs_hits = [p for p in ABSENT_R27 if p in text]
    dd = secs.get("detailed_description:", "")
    abs_hits += ["transition:" + w for w in BANNED_TRANSITION if re.search(w, dd, re.I)]
    body = "\n".join(ln for ln in text.splitlines() if "HAND ANATOMY HARD-LOCKED" not in ln)
    abs_hits += ["negation:" + w for w in BANNED_NEGATION if re.search(w, body, re.I)]
    abs_hits += ["skin:" + w for w in BANNED_SKIN if re.search(w, text, re.I)]
    abs_hits += ["audio:" + w for w in BANNED_AUDIO if re.search(w, text, re.I | re.M)]
    abs_hits += ["youth:" + w for w in BANNED_YOUTH if re.search(w, text, re.I)]
    return req_hits, abs_hits, secs


def main():
    text = open(PROMPT, encoding="utf-8", newline="").read()
    fail = []
    secs = sections(text)
    order = [s.rstrip(":") for s in sections_order(text)]
    want_order = [s.rstrip(":") for s in SECTIONS]
    if order != want_order:
        fail.append("section order/headers: %s" % order)
    if "continuation:" in secs:
        fail.append("single clip carries a continuation section")
    req_missing, abs_hits, _ = checks(text)
    if req_missing:
        fail.append("required clause(s) missing: %s" % ", ".join(sorted(set(req_missing))))
    if abs_hits:
        fail.append("banned phrase(s) present: %s" % ", ".join(sorted(set(abs_hits))))
    bs = beats(text)
    want = round(FRAMES / FPS, 2)
    if not bs:
        fail.append("no timed BEAT ranges found")
    else:
        if abs(bs[0][0] - 0.0) > 1e-6:
            fail.append("first beat does not start at 0.0 (%s)" % bs[0][0])
        for i in range(1, len(bs)):
            if abs(bs[i][0] - bs[i - 1][1]) > 1e-6:
                fail.append("beat gap/overlap at %s" % (bs[i],))
        if abs(bs[-1][1] - want) > 0.02:
            fail.append("beats total %.2fs, target %.2fs" % (bs[-1][1], want))
    if "then" in text.lower():
        fail.append("literal 'then' anywhere")
    # self-destruct probe: the detectors must all fire on the old terrace wording
    old = open(r"C:\AI\community\runs\terrace_dom_q5guide_20261028_s51083007\prompt_seg0.txt",
               encoding="utf-8", newline="").read()
    old_req, old_abs, old_secs = checks(old)
    probe = []
    if not old_req:
        probe.append("required-clause detector did not fire on the old baseline")
    if not old_abs:
        probe.append("absence detector did not fire on the old baseline")
    if "overall_soundscape" not in sections(old):
        probe.append("baseline carries no overall_soundscape section, audio detector untested")
    if not re.search(r"^overall_soundscape:", old, re.I | re.M):
        probe.append("baseline carries no overall_soundscape block, audio detector untested")
    print("gate: %s" % ("PASS" if not fail and not probe else "FAIL"))
    print("  prompt chars: %d, words: %d, beats: %s total %.2fs (target %.2fs = %d frames @ %d fps)"
          % (len(text), len(text.split()),
             ", ".join("%.1f-%.1f" % b for b in bs), bs[-1][1] if bs else 0.0, want, FRAMES, FPS))
    for f in fail:
        print("  FAIL %s" % f)
    for p in probe:
        print("  PROBE %s" % p)
    if not fail:
        print("  sections in order: %s" % ", ".join(order))
        print("  self-destruct probe fired on the baseline as expected" if not probe else "")
    return 1 if (fail or probe) else 0


def sections_order(text):
    return [p.split(":", 1)[0].strip() for p in re.split(r"(?m)^(?=[a-z_]+:$)", flat(text)) if p.strip()]


if __name__ == "__main__":
    sys.exit(main())
