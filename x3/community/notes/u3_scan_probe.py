"""U3 probe: measure the plan's tone-word scan before the check is written.

Scans the plan's set (PROMPT/AGENTS/skills/notes/memory/new prompts) for the two tone words and prints every hit
with its path, line number, file mtime and the line text. The purpose is to separate hits in live instruction
surfaces from hits in pre-existing notes (Max's own tone/cleanup plan text) so the final check states exactly what
it proves. Read-only; the pattern is built from fragments so this file cannot match itself.
"""
import datetime
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
PAT = re.compile("(?i)" + "sy" + "d" + "ney" + "|" + "dad" + "dy")
SURFACES = [
    r"C:\Users\derek\5slock\ralph-community\PROMPT.md",
    r"C:\Users\derek\5slock\ralph-community\AGENTS.md",
    r"C:\Users\derek\5slock\ralph-community\ralph.ps1",
    r"C:\AI\community\talk\talk.ps1",
    r"C:\AI\community\AGENTS.md",
    r"C:\Users\derek\.pi\agent\AGENTS.md",
]
DIRS = {
    "skills-community": r"C:\AI\community\skills",
    "skills-pi": r"C:\Users\derek\.pi\agent\skills",
    "prompt-templates-pi": r"C:\Users\derek\.pi\agent\prompt-templates",
    "memory-pi": r"C:\Users\derek\.pi\agent\memory",
    "notes-community": r"C:\AI\community\notes",
    "notes-ralph": r"C:\Users\derek\5slock\ralph-community\notes",
    "talk-persona-dir": r"C:\Users\derek\5slock\ralph-community\talk",
    "community-root": r"C:\AI\community",
    "ralph-root": r"C:\Users\derek\5slock\ralph-community",
}
SKIP_DIR = ("node_modules", ".git", "__pycache__", ".venv", "runs", "tmpx", "wfsnap", "sessions", "logs")
START = datetime.datetime(2026, 10, 29, 10, 40).timestamp()


def scan(path, tag):
    out = []
    try:
        t = open(path, "rb").read().decode("utf-8", "replace")
    except Exception as e:
        return out
    for n, line in enumerate(t.replace("\r\n", "\n").split("\n"), 1):
        if PAT.search(line):
            out.append((tag, path, n, os.path.getmtime(path), line.strip()[:150]))
    return out


hits = []
for p in SURFACES:
    if os.path.exists(p):
        hits += scan(p, "surface")
for tag, root in DIRS.items():
    if not os.path.isdir(root):
        continue
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIR]
        for fn in files:
            if not fn.endswith((".md", ".py", ".ps1", ".txt", ".json", ".jsonc", ".yaml", ".yml", ".jsonl", ".log")):
                continue
            p = os.path.join(base, fn)
            if tag in ("community-root", "ralph-root") and os.path.dirname(os.path.abspath(p)) != os.path.abspath(root):
                continue   # root scan = top-level files only (PROMPT.md, AGENTS.md, *.ps1, ...)
            hits += scan(p, tag)

print("total hits:", len(hits))
by_tag = {}
for h in hits:
    by_tag.setdefault(h[0], []).append(h)
for tag, items in sorted(by_tag.items()):
    print("\n== %s: %d hits" % (tag, len(items)))
    for t, p, n, mt, line in items[:12]:
        print("   %s L%d [%s] %s\n      %s" % (os.path.basename(p), n,
              datetime.datetime.fromtimestamp(mt).strftime("%m-%d %H:%M"),
              "NEW-today" if mt >= START else "pre-existing", line))
    if len(items) > 12:
        print("   ... %d more" % (len(items) - 12))
new = [h for h in hits if h[3] >= START]
print("\n== hits in files modified at/after 10:40 today: %d" % len(new))
for t, p, n, mt, line in new[:20]:
    print("   %s L%d %s :: %s" % (p, n, datetime.datetime.fromtimestamp(mt).strftime("%H:%M"), line))
