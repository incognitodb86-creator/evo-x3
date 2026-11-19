"""U3 probe (read-only): (a) what pi-permission-system's policy dir contains, (b) files whose NAMES are
credential-shaped (candidates for the "denied secret read" proof), (c) does ralph-community/.gitignore cover a
talk/ session dir, (d) the loop's model entry string (to prove 'same entry, no config edits')."""
import glob
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

POLICY = r"C:\Users\derek\.pi\forge-policy"
print("=== %s exists=%s" % (POLICY, os.path.isdir(POLICY)))
for base, dirs, files in os.walk(POLICY):
    for fn in files:
        p = os.path.join(base, fn)
        print("  file %s (%d B)" % (p, os.path.getsize(p)))
        if os.path.getsize(p) < 6000 and fn.endswith((".md", ".json", ".txt", ".yaml", ".yml")):
            print("   " + open(p, encoding="utf-8", errors="replace").read()[:2500].replace("\n", "\n   "))

PAT = re.compile(r"(secret|token|api[_-]?key|credential|passwd|password|\.env$|auth)", re.I)
print("=== credential-SHAPED file names (name only, content not read) under C:\\AI\\director, C:\\AI\\community, C:\\Users\\derek\\5slock")
hits = []
for root in (r"C:\AI\director", r"C:\AI\community", r"C:\Users\derek\5slock"):
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "__pycache__", ".pytest_cache")]
        if base.count(os.sep) - root.count(os.sep) > 4:
            continue
        for fn in files:
            if PAT.search(fn):
                hits.append(os.path.join(base, fn))
for h in hits[:40]:
    print("  ", h)
print("total", len(hits))

gi = r"C:\Users\derek\5slock\ralph-community\.gitignore"
print("=== .gitignore (%s) exists=%s" % (gi, os.path.exists(gi)))
if os.path.exists(gi):
    print(open(gi, encoding="utf-8", errors="replace").read())

print("=== talk dir pre-existence")
for p in (r"C:\Users\derek\5slock\ralph-community\talk",
          r"C:\Users\derek\5slock\ralph-community\talk\talk.ps1",
          r"C:\Users\derek\5slock\ralph-community\talk\talk-persona.md",
          r"C:\AI\community\notes\talk"):
    print("  exists=%-5s %s" % (os.path.exists(p), p))

print("=== loop entry string in ralph.ps1")
t = open(r"C:\Users\derek\5slock\ralph-community\ralph.ps1", encoding="utf-8").read()
for l in t.split("\n"):
    if "pi --print" in l or "PI_PERMISSION" in l:
        print("  ", l.strip())

print("=== gpu_guard usage / names")
for p in (r"C:\AI\community\scripts\gpu_guard.ps1", r"C:\AI\community\scripts\gpu_lock.ps1"):
    print("  exists=%-5s %s (%s B)" % (os.path.exists(p), p, os.path.getsize(p) if os.path.exists(p) else "-"))
print("  lock file present=%s" % os.path.exists(r"C:\AI\locks\gpu-render.lock"))
print("=== pi version / list not needed here")
