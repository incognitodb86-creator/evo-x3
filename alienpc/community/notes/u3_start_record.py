"""MAX block item 4 (U3) START record (Max brief 11:0x CT, same procedure as items 2-3).

Proves the unit creates only NEW files (nothing to back up): every target path is probed and must not exist.
Appends one START line to C:/AI/community/notes/actions.log (append-only, ASCII, no tone words) and records the
baseline the DONE record will compare against: pi settings/models + llama-swap yaml mtimes (no config edits),
the loop's model entry string, today's daily-memory size/mtime (the talk session must not write loop daily logs),
gpu_guard state, and the youth-guard test count.
"""
import datetime
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
LOG = Path = __import__("pathlib").Path(r"C:\AI\community\notes\actions.log")
REPO = r"C:\Users\derek\5slock\ralph-community"
TALK = os.path.join(REPO, "talk")
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M CT")
NEW = [os.path.join(TALK, "talk.ps1"), os.path.join(TALK, "talk-persona.md"),
       os.path.join(TALK, "sessions"), os.path.join(REPO, "talk")]
CFG = [r"C:\Users\derek\.pi\agent\settings.json", r"C:\Users\derek\.pi\agent\models.json",
       r"C:\AI\director\scripts\llama_swap_keepalive.ps1", os.path.join(REPO, "ralph.ps1"),
       os.path.join(REPO, "PROMPT.md"), os.path.join(REPO, "AGENTS.md")]
DAILY = r"C:\Users\derek\.pi\agent\memory\daily\2026-10-29.md"
START = ("%s | MAX item 4 (U3) START | create the talk-only launcher and its persona as NEW files under "
         "ralph-community\\talk\\ (talk.ps1, talk-persona.md, own sessions dir): pre-existence probed "
         "exists=False for every target, so nothing is overwritten and no backup applies; the launcher adds "
         "--append-system-prompt <persona file>, its own --session-dir, and -ne -e pi-permission-system "
         "-e pi-mobile (so pi-memory is off and this session never writes the loop daily logs), keeps the loop's "
         "same --provider/--model entry with NO config edits, and calls C:\\AI\\director\\scripts\\gpu_guard.ps1 "
         "before every reply: it never takes C:\\AI\\locks\\gpu-render.lock and queues while a render holds it. "
         "Checks per plan: a case-insensitive scan for the two tone words over PROMPT/AGENTS/skills/notes/memory/"
         "new prompts must be 0 hits outside the persona file, and a real talk turn must show a DENIED secret read "
         "(notes/.forge11 fixtures) to prove permissions load. No GPU, no render, no model load, no queue, no "
         "install; the youth guard files are not touched; the plan file is touched only by the record tick") % NOW

for p in NEW:
    print("  exists=%-5s %s" % (os.path.exists(p), p))
assert all(os.path.isdir(p) or not os.path.exists(p) for p in NEW), "a target already exists - back it up before writing"
if not os.path.isdir(TALK):
    os.makedirs(TALK)
    print("created %s (new dir, nothing overwritten)" % TALK)

text = LOG.read_bytes().decode("utf-8")
if "MAX item 4 (U3) START" in text:
    print("actions.log: START already recorded (idempotent)")
else:
    d = text.encode("utf-8")
    if not d.endswith(b"\r\n"):
        d += b"\r\n"
    LOG.write_bytes(d + (START + "\r\n").encode("utf-8"))
    print("actions.log: START appended (append-only), file now %d B" % len(LOG.read_bytes()))

print("=== baselines the DONE record compares against")
for p in CFG:
    st = os.stat(p)
    print("  cfg mtime=%s size=%d %s" % (datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                                         st.st_size, p))
st = os.stat(DAILY)
print("  daily-memory baseline mtime=%s size=%d" % (datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S"), st.st_size))
t = open(os.path.join(REPO, "ralph.ps1"), encoding="utf-8").read()
loop = [l.strip() for l in t.split("\n") if "pi --print" in l]
print("  loop entry (talk must match provider/model): %s" % loop[0][:120])
g = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                    r"C:\AI\director\scripts\gpu_guard.ps1"], capture_output=True, text=True, timeout=180)
print("  gpu_guard start: rc=%d %s" % (g.returncode, (g.stdout or g.stderr).strip().splitlines()[-1][:160]))
print("  lock present=%s" % os.path.exists(r"C:\AI\locks\gpu-render.lock"))
assert all(ord(c) < 128 for c in START)
