# forgeopen PROMPT.md + TASKS.md edits (Max, 2026-10-23). Run once on AlienPc between passes. Prints what changed / what was not found.
import sys
K = r"C:\Users\derek\5slock\ralph-community"
Q = ("PERMISSIONS (forgeopen, Derrick 2026-10-23 1:53 PM CT \"Really anything secrets cause it's gotta do the finance stuff\"; 1:52 PM CT \"Even looser only restricted "
     "secrets and finances. Other than that it just needs to keep a log\"; 1:48 PM CT \"No setup forge correctly\"; 11:09 AM CT \"Yes don't be so restrictive to forge wtf\"): "
     "the ONLY thing blocked is SECRETS - never read or print .env* files (the finance app's included), the rclone config or its tokens, API-key or token files, SSH keys, "
     "or credential stores. Everything else is allowed in bash and powershell alike: ; && | newlines, python -c, redirects, any path (the finance app D:\\Apps / C:\\Apps / :3100 included), "
     "installs, downloads, deletes, git commit/push, your own harness, guard and permission files, ComfyUI and llama-swap. Two hard rules that are not permissions stay: the GPU LOCK "
     "(never stop/restart ComfyUI while a render runs; use python C:\\AI\\community\\scripts\\comfy_ctl.py, which refuses then) and the FICTION LOCK (never edit, move or delete "
     "scripts\\comm.py or scripts\\tests\\test_p6_review.py). Be careful rather than restricted: commit before risky edits, log every install/download in "
     "C:\\AI\\community\\notes\\installs_downloads.md (what, size, URL, where). The harness logs every tool call to C:\\AI\\community\\notes\\forge_actions.log and every deny to "
     "C:\\AI\\community\\notes\\denies.log. Where an older line below says never/only/blocked/[!]-and-pause, this paragraph wins (except the content lock and the no-vision-judge rule).")
SD = ("SELF-DIAGNOSE (every pass, before the task; community Ralph pattern, ghuntley.com/ralph: \"loop back is everything\", \"each time Ralph does something bad, Ralph gets tuned - like a guitar\"): "
      "read the last 2 \"summary:\" lines of logs\\ralph.log and the lines of C:\\AI\\community\\notes\\denies.log newer than your last entry in C:\\AI\\community\\notes\\self_diagnosis.md. "
      "If the last pass timed out, ticked 0 or had denies: FIRST append to self_diagnosis.md the time, what failed, the cause and the fix; then make every fix within your reach yourself "
      "(split the task into smaller TASKS lines so each pass ticks one, fix scripts/harness in C:\\AI\\community or ralph-community, save partial work to notes before long steps). "
      "A deny now only means a secret: never retry it and never work around it; if the work truly needs that secret, write the exact proposed rule change to "
      "C:\\AI\\community\\notes\\guard_requests.md and print GUARD_REQUEST on its own line. You own diagnosing your own loop: if C:\\Users\\derek\\5slock\\AGENTS.md \"## Learnings\" has no line "
      "saying so, add \"- Forge owns diagnosing its own loop: each pass read ralph.log + notes\\denies.log, write notes\\self_diagnosis.md, fix what is in reach (Derrick 2026-10-23 1:48 PM CT).\"")
BUD = r"C:\Users\derek\5slock\ralph-community\logs\p7_budget.json"
def load(p):
    b = open(p, "rb").read().decode("utf-8"); nl = "\r\n" if "\r\n" in b else "\n"; return b.replace("\r\n", "\n"), nl
def save(p, s, nl): open(p, "wb").write(s.replace("\n", nl).encode("utf-8"))
log = []
def rep(s, old, new, tag):
    if old in s: log.append(f"OK   {tag}"); return s.replace(old, new)
    log.append(f"MISS {tag}"); return s
# ---------------- PROMPT ----------------
p = K + r"\PROMPT.md"; s, nl = load(p)
if "SELF-DIAGNOSE (every pass" not in s:
    L = s.split("\n"); i = next(k for k, l in enumerate(L) if l.startswith("STEP 0 ")); L[i + 1:i + 1] = [SD]; s = "\n".join(L); log.append("OK   PROMPT SELF-DIAGNOSE")
s = rep(s, "You are Forge working on AlienPc (Windows; your bash tool is Git Bash, where ; && || $( backticks, newlines and redirects are denied (one command per bash call); the powershell tool allows ; and |, and since 2026-10-23 any command runs there except the hazard denylist in C:\\Users\\derek\\5slock\\AGENTS.md).",
        "You are Forge working on AlienPc (Windows; bash tool = Git Bash, powershell tool = PowerShell 5.1; both run any command, see PERMISSIONS).\n" + Q, "PROMPT line 3 + PERMISSIONS")
s = rep(s, "(\"Web\" line: curl.exe GET to github.com, raw.githubusercontent.com, huggingface.co, docs.comfy.org, civitai.com, reddit.com)", "(any site)", "PROMPT web list")
s = rep(s, "- Never touch C:\\Apps\\ (finance). Never edit llama-swap.yaml, Strata or Pi config, pi-permissions, PROMPT.md, AGENTS-level permission files, ralph.ps1, scripts\\comm.py (youth guard), scripts\\tests\\*, or Switchyard code (C:\\AI\\director).",
        "- Secrets are off-limits (PERMISSIONS). Fiction lock: never edit scripts\\comm.py (youth guard) or scripts\\tests\\test_p6_review.py. Everything else (finance app, llama-swap.yaml, Strata, pi config, ralph.ps1, Switchyard) you may change when the task needs it; say what you changed in notes and commit it.", "PROMPT hard-rule never-touch")
import re
m = re.search(r"- Harness fixes \(Derrick 4:55 PM CT, \"Yes it should\"\):[^\n]*", s)
if m:
    s = s[:m.start()] + ("- Harness upkeep and fixes are yours (Derrick 2026-10-23 1:48 PM CT \"No setup forge correctly\"): scripts, tests, the guard, ralph.ps1, PROMPT/AGENTS notes, TASKS caps. "
                         "Test what you change (py_compile / node --test C:\\AI\\director\\tests\\pi / a dry run), then commit it with git -C <repo> add <files> and git commit -m \"<task id>: <what changed and why>\" "
                         "(C:\\AI\\community or ralph-community), and add one Learnings line.") + s[m.end():]; log.append("OK   PROMPT harness-fix line")
else: log.append("MISS PROMPT harness-fix line")
m = re.search(r"- Outside the BAKEOFF EXCEPTION below, never call ComfyUI[^\n]*", s)
if m:
    s = s[:m.start()] + ("- Renders: R-lines request their render through C:\\AI\\community\\p7\\JOB_REQUEST.json (the harness runs it after you exit, tracks the GPU budget in " + BUD +
                         " and writes C:\\AI\\community\\p7\\jobs\\<id>.result.json); bakeoff lines may also call ComfyUI directly (below). CPU ffmpeg, dip_join.py and scripts are fine anywhere.") + s[m.end():]; log.append("OK   PROMPT renders line")
else: log.append("MISS PROMPT renders line")
s = rep(s, " Still blocked: /upstream/*, /unload, /api/* on :8080, /interrupt, /free, Strata's port, raw Stop-Process/taskkill/Start-Process.", "", "PROMPT bakeoff still-blocked")
m = re.search(r"- Files you may write: [^\n]*", s)
if m:
    s = s[:m.start()] + ("- Files: write wherever the task needs (secrets excepted). Keep your work in C:\\AI\\community (notes, runs, scripts, tools), ComfyUI\\input\\community and TASKS.md, and one-line "
                         "additions to C:\\Users\\derek\\5slock\\AGENTS.md \"## Learnings\". Face crops: python C:\\AI\\community\\scripts\\face_crop.py (yours to improve).") + s[m.end():]; log.append("OK   PROMPT files line")
else: log.append("MISS PROMPT files line")
m = re.search(r"- Web is read-only: [^\n]*", s)
if m:
    s = s[:m.start()] + ("- Web, installs, downloads: any site, any method (curl, Invoke-WebRequest, git clone, pip, pnpm, huggingface downloads) without a card; check free disk first and log each install/download in "
                         "C:\\AI\\community\\notes\\installs_downloads.md. Git checkpoints handle backups. The budget file is " + BUD + " (there is no p7_budget.json under C:\\AI\\community).") + s[m.end():]; log.append("OK   PROMPT web line")
else: log.append("MISS PROMPT web line")
save(p, s, nl)
# ---------------- TASKS ----------------
p = K + r"\TASKS.md"; s, nl = load(p)
s = rep(s, "No new characters, no LoRAs, no downloads, no deletes.", "No new characters. Installs, downloads and deletes are allowed (secrets-only policy, Derrick 2026-10-23 1:53 PM CT); log each install/download in C:\\AI\\community\\notes\\installs_downloads.md.", "TASKS content line")
s = rep(s, "Already approved installs: infinite-creation + ComfyUI-H3-Continuum code and dependencies ONLY. Anything else that needs an install or a new model download (h3-storyboard-ALLInOne's 27B vision GGUF, the Civitai prompt writer's uncensored model, pip install of comfy-mcp / comfy-cli, any ComfyUI update, any extra custom node) gets its own [!] line naming the download/package and its size, and you pause there (STOP_RALPH).",
        "Installs and downloads need no card any more (Derrick 2026-10-23 1:53 PM CT, secrets-only): install/download what each candidate needs yourself (h3-storyboard-ALLInOne's 27B vision GGUF, the Civitai prompt writer's model, comfy-mcp / comfy-cli, ComfyUI updates, extra custom nodes); check free disk first and log each one in C:\\AI\\community\\notes\\installs_downloads.md (what, size, URL, where).", "TASKS bakeoff approvals")
s = rep(s, "If either install needs a new model download, a ComfyUI version update or admin rights: [!] naming it + STOP_RALPH.", "If either install needs a model download or a ComfyUI update, do it and log it in notes\\installs_downloads.md; only admin rights (you have none) is a [!] + STOP_RALPH.", "TASKS B1 pause")
s = rep(s, "- [!] line naming the download + size from its README (web GET), then pause; do not install.", "- download and install it yourself (size from its README; check free disk first), log it in notes\\installs_downloads.md, then run the scene like B2.", "TASKS B5 pause")
s = rep(s, "- [!] line naming the packages + size, then pause.", "- install them yourself (pip into a venv under C:\\AI\\community\\tools), log them in notes\\installs_downloads.md, then run the scene like B2.", "TASKS B6 pause")
s = rep(s, "- [!] line naming the download + size, then pause.", "- download/install what it needs yourself, log it in notes\\installs_downloads.md, then run it as an arm.", "TASKS B7 pause")
s = rep(s, "Any download is a separate [!] line naming the file + size + URL (pause for Derrick's card); do not download.", "This line is research only; to try a candidate, add a B-line for it (downloads are allowed now, log them in notes\\installs_downloads.md).", "TASKS R4H pause")
n = s.count("logs\\p7_budget.json") - s.count("ralph-community\\logs\\p7_budget.json")
s = s.replace("ralph-community\\logs\\p7_budget.json", "\0").replace("logs\\p7_budget.json", BUD).replace("\0", "ralph-community\\logs\\p7_budget.json")
log.append(f"OK   TASKS budget path made absolute x{n}")
save(p, s, nl)
print("\n".join(log))
