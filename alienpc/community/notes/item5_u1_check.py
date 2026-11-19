"""item 5 U1 (2026-10-29): the check the MAX block specifies, run against the live files.
Check = (1) ralph.ps1 default -Model and PROMPT.md 1b both name coding_swift15_iq3s_esp;
        (2) rg beta6_int8 over the skills finds only lines marked retired/superseded.
Read-only, CPU only, no GPU/render/ComfyUI. Exit 0 = all clauses pass, 1 = any clause fails.
Also reports the U1(b) criterion (PROMPT.md 0a must match what ralph.ps1:51 really passes)."""
import re, sys
from pathlib import Path

RALPH = Path(r"C:/Users/derek/5slock/ralph-community/ralph.ps1")
PROMPT = Path(r"C:/Users/derek/5slock/ralph-community/PROMPT.md")
SKILL_ROOTS = [Path(r"C:/Users/derek/.pi/agent/skills"), Path(r"C:/AI/community/skills")]
WANT = "coding_swift15_iq3s_esp"
RETIRED_MARKS = ("retired", "superseded", "prior keep", "history only", "was production", "do not use", "never for a new")

rl = RALPH.read_text(encoding="utf-8").splitlines()
pl = PROMPT.read_text(encoding="utf-8").splitlines()

# clause 1a: the ralph.ps1 param default
m = next((l for l in rl if re.match(r"\s*\[string\]\$Model\s*=", l)), None)
ralph_default = re.search(r"=\s*'([^']+)'", m).group(1) if m else "NOT FOUND"
print("ralph.ps1 param default : %s" % ralph_default)
print("  wants %s : %s" % (WANT, "PASS" if ralph_default == WANT else "FAIL"))

# clause 1b: PROMPT.md item 1b
b = next((l for l in pl if re.match(r"\s*b\.\s*Caption once", l)), None)
ids = re.findall(r"coding_swift15[a-z_0-9]*", b or "")
print("PROMPT.md 1b model      : %s" % (ids or "NO MODEL STRING"))
print("  wants %s : %s" % (WANT, "PASS" if ids == [WANT] else "FAIL"))

# U1(b): 0a must not claim fix_plan.md is pinned; ralph.ps1:51 is the ground truth
argv = next((l for l in rl if "@$K" in l and "PROMPT.md" in l), "")
inc = re.findall(r'@"?\$K\\([A-Za-z_.]+)', argv)
zero_a = next((l for l in pl if l.startswith("0a.")), "")
claims_pinned = "pinned in ralph.ps1 argv" in zero_a
print("\nralph.ps1 L51 includes   : %s" % (inc or "none"))
print("PROMPT.md 0a claims pinned: %s   -> %s" % (claims_pinned, "FAIL (false claim)" if claims_pinned else "PASS (matches argv)"))

# clause 2: every beta6_int8 line in any skills tree must be marked retired/superseded
print("\nbeta6_int8 scan over skills:")
bad = 0
for root in SKILL_ROOTS:
    if not root.is_dir():
        continue
    for f in sorted(root.rglob("*.md")):
        for i, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if "beta6_int8" in line:
                low = line.lower()
                marked = any(k in low for k in RETIRED_MARKS)
                bad += 0 if marked else 1
                print("  %-4s %s:%d  %s" % ("ok" if marked else "BAD", f.relative_to(root), i,
                                            line.strip()[:120]))
print("unmarked beta6_int8 lines: %d -> %s" % (bad, "PASS" if bad == 0 else "FAIL"))

ok = (ralph_default == WANT) and (ids == [WANT]) and bad == 0 and (not claims_pinned)
print("\nVERDICT: %s" % ("ALL CLAUSES PASS" if ok else "FAIL - revert the edits that caused it (see lines above)"))
sys.exit(0 if ok else 1)
