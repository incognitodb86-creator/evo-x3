"""U2 follow-up: remove the last rule restatements from the director skill (a pointer cites R<n>,
it does not repeat the sentence). Line-anchored by unique ASCII substrings, unicode-safe.
Rollback: SKILL.md.bak-20261029-u2 (the .pi skills tree is not a git repo)."""
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

D = Path(r"C:/Users/derek/.pi/agent/skills/alienpc-hardcore-i2v-director/SKILL.md")
HOME = r"C:\AI\community\skills\h3-prompting\SKILL.md"

SUBS = [
    # frontmatter description
    ("get-into-position when Cond\u2260act",
     "position-unlock when Cond\u2260act (rules: h3-prompting)"),
    # director card motion line
    ("**Motion** continuous from Cond (or get-into-position then act)",
     "**Motion** continuous from Cond (or the R16 position beats first)"),
    # the card paste pointer -> terse cites only
    ("- **Max paste** = the shape in skill `h3-prompting`", None),
    # audio mention inside the H3-prompt-shape pointer (two adjacent single lines)
    ("R7 audio (plain cues,", "R7 audio"),
    ("no overall_soundscape / non_diegetic_music block - TenStrip HF #77),",
     "the developer audio block is deleted (TenStrip HF #77),"),
    # METHOD note node line
    ("**REF2VA** multi-ref six-section (prefer for 1-min path)",
     "**REF2VA** multi-ref (prefer for 1-min path); paste shape and rules = skill `h3-prompting` (%s)" % HOME),
]

ANCHOR = "- **Max paste** = the shape in skill `h3-prompting`"
PASTE_NEW = [
    "- **Max paste** = the shape and rules in skill `h3-prompting` (`%s`) - cite R1, R5, R9, R31; write the text to a\n"
    "  prompt file before the builder touches it. The director card stays here: intent_id, Lock from still, Camera hold,\n"
    "  Length default 124f (~5s), and an ~80-180 word motion-intent card is planning only - never pasted." % HOME,
]

raw = D.read_bytes()
sep = "\r\n" if raw.count(b"\r\n") == raw.count(b"\n") and raw.count(b"\n") > 0 else "\n"
lines = raw.decode("utf-8").split(sep)
print("read %d lines, %d B (%s)" % (len(lines), len(raw), "CRLF" if sep == "\r\n" else "LF"))

for old, new in SUBS:
    if new is None:
        continue
    hits = [i for i, l in enumerate(lines) if old in l]
    assert len(hits) == 1, "anchor %r -> %d hits" % (old[:40], len(hits))
    lines[hits[0]] = lines[hits[0]].replace(old, new)
    print("fixed line %d (anchor %r)" % (hits[0] + 1, old[:40]))

start = [i for i, l in enumerate(lines) if l.startswith(ANCHOR)]
assert len(start) == 1, "paste pointer anchor -> %d hits" % len(start)
i = start[0]
end = i + 1
while end < len(lines) and lines[end].startswith("  "):
    end += 1
lines[i:end] = PASTE_NEW[0].split(sep)
print("replaced the card paste pointer (%d lines -> %d)" % (end - i, len(PASTE_NEW[0].split(sep))))

out = sep.join(lines)
D.write_bytes(out.encode("utf-8"))

GONE = ["The camera holds a static shot", "six-section", "get-into-position", "documentary porn framing",
        "five-finger", "five fingers", "Do not steer with a ban list", "no JSON-as-POS", "no word cap",
        "LoRA trigger only when that LoRA is loaded", "overall_soundscape", "non_diegetic_music",
        "keyframe completion", "static hold cannot also fully reveal"]
txt = out
bad = [g for g in GONE if g in txt]
print("rule strings absent from the director skill: %d/%d" % (len(GONE) - len(bad), len(GONE)))
for g in bad:
    print("  STILL PRESENT (line %s): %s" % ([n + 1 for n, l in enumerate(lines) if g in l], ascii(g)))
print("size %d B -> %d B; non-ascii chars: %d" % (len(raw), len(out.encode("utf-8")),
                                                   sum(1 for c in txt if ord(c) > 127)))
sys.exit(0 if not bad else 1)
