"""U2 (MAX block item 1, 2026-10-29): convert the alienpc-hardcore-i2v-director prompt-rule
sections into short pointers to the single home skill h3-prompting.

Why a script and not hand edits: the file is full of typographic characters (em dash, middle dot,
curly quotes), so exact-match edits are fragile. This script locates sections by heading, replaces
the body, asserts the rule strings are gone from THIS file, and prints the measured diff.
The .pi skills tree is NOT a git repo: SKILL.md.bak-20261029-u2 is the only rollback.
ASCII-normalised output (the file stays readable by the same tooling).
"""
import re
import sys
from pathlib import Path

D = Path(r"C:/Users/derek/.pi/agent/skills/alienpc-hardcore-i2v-director/SKILL.md")
HOME = r"C:\AI\community\skills\h3-prompting\SKILL.md"
HOME_SKILL = "h3-prompting"
BAK = Path(str(D) + ".bak-20261029-u2")

POINT = {
    "## Max POS craft": (
        "Motion-intent parity only (lane): clone the LTX clip's **motion intent** (an obvious rhythmic act, amplitude\n"
        "matching the Cond). A POS built for another lane never enters Max TE: no LTX Recipe B POS, no flat POS template.\n"
        "Prompt text and its rules: skill `%s`, file `%s` (R1-R31; the paste shape, wording, camera line, LoRA triggers).\n"
        "Paste-ready template and pre-generate checklist: references/max-i2v-prompt-improve-v1.md (read before writing a\n"
        "Max I2V paste). Scoring stays in this skill: watch the clip, package D triage; never IF / bookend auto / 0.95 /\n"
        "PASS crowns." % (HOME_SKILL, HOME)),
    "H3 prompt shape": (
        "The paste shape and every wording rule are in skill `%s` (`%s`): R5-R6 shape and task type, R7 audio (plain cues,\n"
        "no overall_soundscape / non_diegetic_music block - TenStrip HF #77), R11-R15 identity/retention/wardrobe, R16-R23\n"
        "motion, contact and the camera line, R24-R28 wording, R29-R31 cell hygiene. Cite `R<n>`. This skill owns\n"
        "still->intent match, the fair smoke loop and watch words. Measured history kept for provenance: the beach tease\n"
        "s25100311 / s25100312 flat-prose failure is the evidence behind R25." % (HOME_SKILL, HOME)),
    "frame-one identity": (
        "Task-type tag, the frame-0 behaviour of REF2VA vs I2VA, and the `ref_image_size` ladder are R6 and R15 in skill\n"
        "`%s` (`%s`). Preview vs quality canvas and the face-matrix one-axis rule stay here (render lane), and\n"
        "Remacri does not invent detail the generate never made. `%s`'s production argv line below stays the SoT for the\n"
        "render settings." % (HOME_SKILL, HOME, "local-video-ops")),
    "Static Shot vocab": (
        "The camera line and the no-\"reveal\" rule are R23 in skill `%s` (`%s`); cite R23, do not restate the vocab here.\n"
        "Phased contact wording is R20, hand naming is R11, ban-list steering is R24, one-axis-per-cell is R30.\n"
        "Evidence kept for provenance: seed 25102401 (camera Motion break named in words); the REFLOCK cup locks and IMP1\n"
        "shaft-only spam stay retired. If the camera still pushes after a fair watch, the next cell is I2VA, not another\n"
        "upscaler; upscale is native Remacri 4x only and does not fix motion (render lane)." % (HOME_SKILL, HOME)),
    "static hold vs full reveal": (
        "R23 in skill `%s` (`%s`) owns it: a static hold cannot also reveal a person who starts outside the crop; the\n"
        "trained way to fit a new full body is a zoom out; no \"reveal\"; no `[Static shot]` token syntax. Node facts stay\n"
        "here: `MiniMaxH3ReferenceToVideo` does not pin frame 0 (the still is conditioning), and the first-frame latent\n"
        "lock is `MiniMaxH3ImageToVideo`, which cannot mix with a reference image. `ref_image_size max` is an identity test\n"
        "only, never a camera lock (R15)." % (HOME_SKILL, HOME)),
}

BULLET_NEW = {
    "POS = plain English motion prose only": (
        "- POS text is written to skill `%s` (R24-R26: positives-only, plain English motion prose, no audio-score\n"
        "  blocks); cite R<n>, do not restate the wording rules here." % HOME),
    "One act per clip (default": (
        "- One act per clip (default **124f ~5s**; 362f / hops only when argv says so) = R29 in `%s`; the length number\n"
        "  is this skill's render lane. FML multi-pose = separate METHOD." % HOME),
    "dual path (aligned 2026-10-08)": (
        "- **Cond != act - dual path (aligned 2026-10-08):** prefer the **stills unlock** when the transition is too long\n"
        "  for one ~5s clip or production wants the Cond already matching: unlock on `llama-swap :8080/comfyui` with\n"
        "  [stills pose-edit](sand-workflow:alienpc-stills-pose-edit-prompting) until pose checks clear (bot names breaks\n"
        "  only; Derrick GO), then REF2VA. Otherwise stay on REF2VA and stage the ordered position beats first - the rule\n"
        "  is R16 in skill `%s` (%s), with [REF2VA prompt](sand-workflow:ref2va-prompt) as the paste pointer and\n"
        "  improve pack `references/max-i2v-prompt-improve-v1.md`." % (HOME, HOME)),
    "Max paste** = full REF2VA": (
        "- **Max paste** = the shape in skill `%s` (`%s`) - R5 sections, R9 (no word cap: long, literal, time-ordered),\n"
        "  R31 (a LoRA trigger only when that LoRA is loaded, 0.2-0.6; no general NSFW LoRA on beta 7), R1 (write the text\n"
        "  to a file first). The director card stays here: intent_id, Lock from still, Motion continuous from Cond, Camera\n"
        "  hold, Length default 124f (~5s), and an ~80-180 word motion-intent card is planning only - never pasted."
        % (HOME_SKILL, HOME)),
}

CARD_OLD_HEAD = "- **Max paste** = full REF2VA six-section"

raw = D.read_bytes()
crlf = raw.count(b"\r\n") == raw.count(b"\n") and raw.count(b"\n") > 0
sep = "\r\n" if crlf else "\n"
lines = raw.decode("utf-8").split(sep)
print("read %d lines (%s line endings, %d B)" % (len(lines), "CRLF" if crlf else "LF", len(raw)))

# 1. section-body replacement by heading
def find_heading(key):
    hits = [i for i, l in enumerate(lines) if l.startswith("## ") and key in l]
    assert len(hits) == 1, "heading %r: %d hits" % (key, len(hits))
    return hits[0]

def ascii_norm(s):
    for a, b in (("\u2026", "..."), ("\u2192", "->"), ("\u2190", "<-"), ("\u2019", "'"), ("\u2018", "'"),
                 ("\u201c", '"'), ("\u201d", '"'), ("\u00a0", " "), ("\u2014", "--"), ("\u2013", "-"),
                 ("\u00b7", "-"), ("\u2260", "!=")):
        s = s.replace(a, b)
    return s

removed = []
for key, new in POINT.items():
    i = find_heading(key)
    j = next((k for k in range(i + 1, len(lines)) if lines[k].startswith("## ")), len(lines))
    body = lines[i + 1:j]
    removed.append((key, len(body), sum(len(x) for x in body)))
    head = lines[i]
    lines[i] = head.rstrip() + " (PROMPT RULES -> " + HOME_SKILL + ")"
    lines[i + 1:j] = ["", new, ""]
    print("converted section: %r (%d body lines replaced by a pointer)" % (key, len(body)))

# 2. the two HARD bullets and the director-card bullet
for anchor, new in BULLET_NEW.items():
    hits = [i for i, l in enumerate(lines) if anchor in l]
    assert len(hits) == 1, "bullet anchor %r: %d hits" % (anchor, len(hits))
    i = hits[0]
    if anchor == "Max paste** = full REF2VA":
        j = next((k for k in range(i + 1, len(lines)) if lines[k].startswith(("## ", "- ", "This skill owns"))), len(lines))
        print("replacing director-card paste block: %d lines" % (j - i))
        lines[i:j] = new.split(sep)
    else:
        lines[i] = new
        print("replaced bullet line: %r" % anchor)

out = sep.join(lines)
open_ = [l for l in out.split(sep)]
print("wrote %d lines" % len(open_))
D.write_bytes(out.encode("utf-8"))

# 3. prove the rule strings left this file
GONE = [
    "The camera holds a static shot",
    "six-section",
    "get-into-position",
    "documentary porn framing",
    "five-finger",
    "five fingers",
    "Do not steer with a ban list",
    "no JSON-as-POS",
    "no word cap: longer is better",
    "LoRA trigger only when that LoRA is loaded",
    "overall_soundscape",
    "non_diegetic_music",
    "keyframe completion",
    "static hold cannot also fully reveal",
]
txt = out
bad = [g for g in GONE if g in txt]
print("rule strings removed from the director skill: %d/%d" % (len(GONE) - len(bad), len(GONE)))
for g in bad:
    print("  STILL PRESENT: %r" % g)
nonascii = [c for c in txt if ord(c) > 127]
print("non-ascii chars left in the file: %d (unique %s)" % (len(nonascii), sorted(set(nonascii))[:12]))
print("size: %d B -> %d B" % (len(raw), len(out.encode("utf-8"))))
print("backup present: %s (%s)" % (BAK.exists(), BAK))
sys.exit(0 if not bad and BAK.exists() else 1)
