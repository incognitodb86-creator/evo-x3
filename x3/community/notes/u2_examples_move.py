"""U2 follow-up (context cost): the two archived p15 few-shots are ~20 KB of verbatim prompt text.
Keeping them inside SKILL.md made the home skill 36 KB, which loads on every prompt task - the opposite of
PROMPT.md 0d ("Context is the budget"). Pi skills support supporting files (pi docs configuration.md:
"<agent-dir>/skills/ ... and supporting files"), so the verbatim examples move to the skill's
references/examples_archived.md and SKILL.md keeps the two short composed examples + a pointer.

Effect measured: the plan's 3-6 examples requirement stays satisfied INSIDE THE SKILL PACKAGE (2 verbatim
p15 few-shots + 2 composed), the rule strings stay in one file, and SKILL.md drops back to a small file.
Rollback: SKILL.md.bak-20261029-u2 (pre-U2) - this script is reversible by hand (the moved text is verbatim).
"""
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

SK = Path(r"C:\AI\community\skills\h3-prompting\SKILL.md")
REF = SK.parent / "references" / "examples_archived.md"
raw = SK.read_text(encoding="utf-8")
size_before = len(raw.encode("utf-8"))
snap = SK.parent / "SKILL.md.mid-20261029-u2-examples"
snap.write_text(raw, encoding="utf-8")
print("snapshot of the intermediate SKILL.md -> %s" % snap)

# section 6 = the worked-examples section
m = re.search(r"(?ms)^## 6\. Worked examples\n(.*?)(?=^## 7\. )", raw)
assert m, "section 6 not found"
sec = m.group(1)
intro_end = sec.index("### Example 1 ")
intro, rest = sec[:intro_end], sec[intro_end:]
parts = re.split(r"(?m)^(?=### Example )", rest)
parts = [p for p in parts if p.strip()]
assert len(parts) == 4, "expected 4 example blocks, got %d" % len(parts)
archived, composed = parts[:2], parts[2:]
print("blocks: archived=%d composed=%d" % (len(archived), len(composed)))

REF.parent.mkdir(parents=True, exist_ok=True)
head = (
    "# Archived H3 examples - verbatim (U2, 2026-10-29)\n\n"
    "Supporting file of the skill `h3-prompting` (`SKILL.md` in this directory). Read this when a full paste is\n"
    "needed: it holds the two winning prompts archived in\n"
    "`C:\\Users\\derek\\5slock\\ralph-community\\notes\\p15_writer_skill.md` (its only two few-shots), copied\n"
    "**verbatim** - byte-for-byte of the fenced blocks, verified by `C:\\AI\\community\\notes\\u2_check.py`. Nothing in the p15 file was\n"
    "changed: it is the writer model's system prompt, not a rule file.\n\n"
    "**Audio supersession (R7 in `SKILL.md`):** the `overall_soundscape:` and `non_diegetic_music:` blocks in these\n"
    "two archived prompts are deleted for anything written fresh on this box - TenStrip (owner), HF 10Eros-Max\n"
    "discussion #77: *\"...should be deleted. Prompt very normal audio queues in prompt or at the end of the main\n"
    "prompt.\"* On reuse, move those sound sentences, unedited in wording, to the end of `detailed_description` and\n"
    "drop the two blocks. The rules themselves are in `SKILL.md` (R1-R31); do not restate them here.\n\n"
)
ref_text = head + "\n" + \
    "\n".join(p.replace("### Example 1 ", "## Archived Example A - verbatim (p15 Few-Shot 1) ").strip()
              .replace("### Example 2 ", "## Archived Example B - verbatim (p15 Few-Shot 2) ").strip()
              for p in archived) + "\n"
REF.write_text(ref_text, encoding="utf-8")
print("wrote %s (%d B)" % (REF, len(ref_text.encode("utf-8"))))

# SKILL.md keeps the intro, gains a pointer, keeps the two composed examples renumbered 1 and 2
pointer = (
    "The two **archived** winning prompts - both few-shots from `p15_writer_skill.md`, verbatim - are in the\n"
    "supporting file `references/examples_archived.md` in this skill directory (they are ~10 KB each: read them when\n"
    "a full paste is needed, they are not loaded with the skill). That file also carries the audio-supersession\n"
    "note. Together the skill package carries **4 worked examples**, inside the plan's 3-6 range. The two below are\n"
    "short, current-shape examples (audio inline, no soundscape block) built from this box's measured rules.\n\n"
)
new_examples = pointer
for i, p in enumerate(composed, start=1):
    p = re.sub(r"^### Example \d+ ", "### Example %d " % i, p, count=1, flags=re.M)
    new_examples += p
new_sec = intro + new_examples
raw2 = raw[:m.start(1)] + new_sec + raw[m.end(1):]
SK.write_text(raw2, encoding="utf-8")
size_after = len(raw2.encode("utf-8"))
print("SKILL.md %d B -> %d B (%+.0f)" % (size_before, size_after, size_after - size_before))

# prove the invariants
t = SK.read_text(encoding="utf-8")
rt = REF.read_text(encoding="utf-8")
p15 = open(r"C:\Users\derek\5slock\ralph-community\notes\p15_writer_skill.md", encoding="utf-8").read()
blocks = re.findall(r"```text\n(.*?)```", p15, flags=re.S)
in_pkg = [i + 1 for i, b in enumerate(blocks) if b.strip() in t or b.strip() in rt]
n_skill = len(re.findall(r"(?m)^### Example \d+", t))
n_ref = len(re.findall(r"(?m)^## Archived Example ", rt))
rules_in_ref = [rid for rid, b in re.findall(r"(?ms)^\*\*(R\d+) - (.*?)(?=\n\n\*\*R\d+ - |\n\n## |\Z)", t)
                if re.sub(r"\s+", " ", b.replace("**", "").replace("`", ""))[:90]
                in re.sub(r"\s+", " ", rt.replace("**", "").replace("`", ""))]
print("examples: SKILL.md=%d, references=%d, package total=%d (plan asks 3-6)" % (n_skill, n_ref, n_skill + n_ref))
print("p15 few-shots reproduced verbatim inside the skill package: %s of %d" % (in_pkg, len(blocks)))
print("rule signatures present in the references file (must be none): %s" % (rules_in_ref or "none"))
ok = (n_skill + n_ref == 4 and len(in_pkg) == len(blocks) and not rules_in_ref and size_after < 20000)
print("VERDICT: %s" % ("OK" if ok else "PROBLEM"))
sys.exit(0 if ok else 1)
