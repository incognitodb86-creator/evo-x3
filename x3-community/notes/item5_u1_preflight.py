"""item 5 U1 (2026-10-29): append the START line to notes/actions.log, then print the pre-flight facts
the U1 check depends on. Append-only, LF, ASCII. No GPU, no render, no ComfyUI/llama-swap call."""
import json, subprocess, sys, time
from pathlib import Path

NOW = time.strftime("%Y-%m-%d %H:%M")
ACTIONS = Path(r"C:/AI/community/notes/actions.log")
START = ("%s CT Pi (Max block item 5 = U1 quick fixes, Derrick go 8:52 AM CT) START. " % NOW
         + "Scope: (a) ralph.ps1 default -Model and PROMPT.md 1b -> coding_swift15_iq3s_esp; "
         + "(b) PROMPT.md 0a argv line corrected to what ralph.ps1 L51 really passes (only @PROMPT.md); "
         + "(c) retire the beta6 KEEP line at L25 of C:/Users/derek/.pi/agent/skills/alienpc-hardcore-i2v-director/SKILL.md. "
         + "Backup before each edit, check after, revert on fail. No GPU, no render. Item 3 untouched. Stop after U1.\n")
raw = ACTIONS.read_bytes()
assert raw.endswith(b"\n")
ACTIONS.write_bytes(raw + START.encode("ascii"))
print("START line appended (+%d bytes)" % len(START.encode("ascii")))

# 1. the exact model id in models.json (must exist before it becomes a default)
mp = Path(r"C:/Users/derek/.pi/agent/models.json")
m = json.loads(mp.read_text(encoding="utf-8-sig"))
ids = [mm.get("id") for prov in m.get("providers", {}).values() for mm in prov.get("models", [])]
print("models.json ids:", ids)
print("coding_swift15_iq3s_esp present:", "coding_swift15_iq3s_esp" in ids,
      "| old coding_swift15_iq3s present:", "coding_swift15_iq3s" in ids)

# 2. settings.json defaultModel (report only; not in U1 scope)
sp = Path(r"C:/Users/derek/.pi/agent/settings.json")
s = json.loads(sp.read_text(encoding="utf-8-sig"))
print("settings.json defaultModel:", s.get("defaultModel"), "| model:", s.get("model"))

# 3. current state of the three targets, before any edit
for p, pat in ((r"C:/Users/derek/5slock/ralph-community/ralph.ps1", r"\$Model = '"),
               (r"C:/Users/derek/5slock/ralph-community/PROMPT.md", "coding_swift15_iq3s"),
               (r"C:/Users/derek/.pi/agent/skills/alienpc-hardcore-i2v-director/SKILL.md", "beta6_int8")):
    print("--- %s" % p)
    for i, l in enumerate(Path(p).read_text(encoding="utf-8").splitlines(), 1):
        if pat in l:
            print("    L%d: %s" % (i, l[:150]))

# 4. is the skills tree a git repo? (affects the commit step)
r = subprocess.run(["git", "-C", r"C:/Users/derek/.pi/agent/skills", "rev-parse", "--show-toplevel"],
                   capture_output=True, text=True)
print("skills git toplevel:", (r.stdout.strip() or "NOT A REPO"), (r.stderr.strip()[:80] if r.returncode else ""))
