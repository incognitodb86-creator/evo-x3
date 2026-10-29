"""Research (2026-10-29): measure the live PROMPT.md as an artifact - what it names, whether each named
thing exists, and how much of it duplicates other files on this box. Read-only, CPU only."""
import hashlib, json, os, re
from pathlib import Path

PROMPT = Path(r"C:/Users/derek/5slock/ralph-community/PROMPT.md")
raw = PROMPT.read_bytes()
txt = raw.decode("utf-8")
lines = txt.splitlines()
words = len(re.findall(r"[A-Za-z0-9_]+", txt))
print("LIVE PROMPT.md: %d bytes, %d lines, ~%d words, sha256 %s" % (len(raw), len(lines), words, hashlib.sha256(raw).hexdigest()[:16]))
print("  rule blocks: %s" % ", ".join(re.match(r"^\s*(\d+[a-z]?)\.", l).group(1) for l in lines if re.match(r"^\s*(\d+[a-z]?)\.", l)))
per_line = sorted(((len(l), i + 1) for i, l in enumerate(lines)), reverse=True)[:6]
print("  longest lines (chars, line#): %s" % per_line)
print("  chars in the two provenance-heavy lines 13-14: %d = %.1f%% of the file"
      % (len(lines[12]) + len(lines[13]), 100.0 * (len(lines[12]) + len(lines[13])) / len(txt)))

# 1. every absolute path PROMPT.md names: does it exist?
paths = sorted(set(re.findall(r"C:\\\\?AI\\\\?[^\s,)]+", txt)) | set(re.findall(r"C:\\\\?Users\\\\?[^\s,)]+", txt)))
print("\nPATHS NAMED BY PROMPT.md (%d) - existence check:" % len(paths))
for p in paths:
    q = p.rstrip(".,")
    for cand in (q, q.replace("\\", "/")):
        if os.path.exists(cand):
            kind = "DIR " if os.path.isdir(cand) else "FILE"
            n = len(os.listdir(cand)) if os.path.isdir(cand) else os.path.getsize(cand)
            print("  OK   %s %s (%s)" % (kind, cand, n))
            break
    else:
        print("  MISS %s" % q)

# 2. relative names it tells the agent to go use (notes\..., specs\*, scripts\tests\...)
rel = ["notes\\hc_pick_scan_20261023.py", "notes\\learnings\\agents_md_learnings_20261026.md",
       "notes\\prompt_reference_20261027.md", "specs", "notes\\progress.md", "notes\\web",
       "notes\\p15_writer_batch.py", "notes\\bk26_judge_harness.py", "notes\\p15_driver.ps1",
       "sessions", "logs", "notes\\actions.log", "notes\\denies.log", "notes\\self_diagnosis.md",
       "notes\\guard_requests.md", "notes\\needs_derrick.md", "notes\\plans", "notes\\learnings"]
K = PROMPT.parent
print("\nRELATIVE NAMES PROMPT.md points at (resolved from ralph-community):")
for r in rel:
    p = K / r
    print("  %-52s %s" % (r, ("exists (%d entries)" % len(os.listdir(p)) if p.is_dir() else "exists (%d B)" % p.stat().st_size) if p.exists() else "MISSING"))

# 3. things PROMPT.md does not name that the loop rules reference (drift check)
probes = {
  "SELF-DIAGNOSE rule in PROMPT.md": "SELF-DIAGNOSE" in txt,
  "COMPLETE token rule": "promise>COMPLETE" in txt,
  "chain.ps1 exists": (K / "chain.ps1").exists(),
  "tests dir in ralph-community": (K / "tests").exists(),
  "forge-policy dir (ralph.ps1 sets it as policy agent dir)": os.path.isdir(r"C:\Users\derek\.pi\forge-policy"),
  "gpu_guard.ps1": os.path.exists(r"C:\AI\director\scripts\gpu_guard.ps1"),
  "gpu lock dir": os.path.isdir(r"C:\AI\locks"),
}
print("\nDRIFT / ENFORCEMENT PROBES:")
for k, v in probes.items():
    print("  %-58s %s" % (k, v))

# 4. duplication: phrases PROMPT.md shares with AGENTS.md / RUNBOOK.md / fix_plan.md / skills
SOURCES = {
  "ralph-community/AGENTS.md": K / "AGENTS.md",
  "5slock/AGENTS.md": Path(r"C:/Users/derek/5slock/AGENTS.md"),
  "community/RUNBOOK.md": Path(r"C:/AI/community/RUNBOOK.md"),
  "ralph-community/fix_plan.md": K / "fix_plan.md",
  "community/skills/h3-hc-render/SKILL.md": Path(r"C:/AI/community/skills/h3-hc-render/SKILL.md"),
  "community/skills/forge-self-diagnose/SKILL.md": Path(r"C:/AI/community/skills/forge-self-diagnose/SKILL.md"),
  "community/skills/h3-prompting/SKILL.md": Path(r"C:/AI/community/skills/h3-prompting/SKILL.md"),
}
KEYS = {
  "run_graph_job.py": "run_graph_job.py",
  "gpu_guard": "gpu_guard",
  "gpu-render.lock": "gpu-render.lock",
  "comfy_ctl.py status": "comfy_ctl.py status",
  "adults-only / youth guard": "adults",
  "KEEP is Derrick": "KEEP is Derrick",
  "no vision model judges": "vision model",
  "350-500 word": "350-500",
  "one fetch per URL / notes\\web": "notes\\web",
  "commit once per repo": "commit once",
  "progress line": "progress.md",
  "test_p6_review.py": "test_p6_review.py",
  "test_guard_scope.py": "test_guard_scope.py",
  "no secrets/.env": ".env",
  "default_b2 graph": "default_b2_terrace",
  "--frames": "--frames",
  "subagents": "subagent",
  "complete token": "COMPLETE",
  "GI063": "GI063",
  "Klein/ComfyUI custom_nodes read deny": "custom_nodes",
}
docs = {}
for name, p in SOURCES.items():
    docs[name] = p.read_text(encoding="utf-8", errors="replace") if p.exists() else None
print("\nDUPLICATION MATRIX (1 = also present in that file):")
head = "  %-26s %s" % ("PROMPT.md concept", " ".join("%-4s" % ("P" if k in txt else "-") for k in ["self"]))
files = list(SOURCES)
print("  %-34s %s" % ("concept", " ".join("%-28s" % f.split('/')[-1] for f in files)))
for label, needle in KEYS.items():
    row = []
    for f in files:
        d = docs[f]
        row.append("YES" if (d and needle.lower() in d.lower()) else "-")
    if needle.lower() in txt.lower():
        print("  %-34s %s" % (label, " ".join("%-28s" % r for r in row)))
print("\n  (only rows where PROMPT.md itself contains the concept are printed)")
