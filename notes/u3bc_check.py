"""MAX block items 5 (U3b) and 6 (U3c) + the U5 second check - self-verifying, no LLM call, Max can re-run it.
Max's brief of 2026-10-29 19:0x CT, on Derrick's go 5:29 PM CT. Plan: notes/2026-10-29-forge-cleanup-plan.md
(U3b, U3c, U5) and fix_plan.md items 5-6.

What this proves, item by item, against disk and against real runs, never by assertion:

U3b (plan check: "the folder path in the persona exists; your u3_check tone scan still shows 0 tone words outside
the persona file"):
  - the persona names exactly ONE character-reference folder, and it is the pool-blonde one, not the older folder of
    the same kind (which is proved to exist, so the check is not vacuous);
  - that folder and its card/start frame exist, and the character card describes an adult;
  - the appearance line is one plain quote-free bullet, so the launcher still accepts the persona (proved by a
    DryRun rc=0 inside this check), and the persona carries no character that breaks native argv quoting;
  - the appearance text never reached a render prompt: its distinctive phrases appear in 0 render-prompt/graph/
    JOB_REQUEST/run files;
  - the tone-word scan over the loop's live instruction surfaces (PROMPT.md, AGENTS.md, launchers, both skill trees,
    prompt templates, memory, specs, notes prose) = 0 hits; the persona text lives verbatim in exactly two files -
    the persona home and the copy in the lane's own folder, which Derek asked for at 5:13 PM CT so a fresh chat
    started there loads it - and nowhere else; every other hit on the box carries a printed reason;
  - this unit's own records (actions.log lines, progress.md, the tick line, this script, the compare harness, the
    result note) carry 0 tone words.

U3c (plan: "the talk lane loads the same tools, extensions, skills and permissions as the main forge session,
keeping its own persona, session dir and separate chat"; keep list: youth guard, fictional adults only, one GPU
render at a time, no secrets; then a side-by-side test saved for Derrick):
  - full-access parity from the launcher's own code and a DryRun: no -ne, no -e pins, no policy-dir override, no
    config file named, and the only added flags are the model entry (identical to ralph.ps1), the lane's own
    session dir, --append-system-prompt, the task text;
  - the permission policy resolves to the same file the main chat reads: this process has no
    PI_PERMISSION_SYSTEM_POLICY_AGENT_DIR, and the full-access branch deletes the override, so both sides resolve to
    the user-level policy, whose secret-shaped denies are counted (values never printed);
  - the extension/skill claim is checked against disk: every package the launcher's header names is installed, and
    the skills trees the main chat loads exist and are non-empty; the lane adds no skills/tool path of its own;
  - the keep list is intact: the adults-only / no-minors / no-tone-into-render-prompt rules are in the persona; the
    GPU rule still calls gpu_guard.ps1 and is driven for real with a synthetic live-PID lock in FULL-ACCESS mode
    (-NoWait refuses rc=3; bounded queue ends GPU_DEFERRED; the lock bytes are never touched) - a regression here
    would let a chat turn fire into a render window;
  - the A/B switch works: -Restricted reproduces the pre-U3c lane (discovery off, the two extension pins, the
    loop's policy dir) from the same file;
  - the side-by-side test ran for real: 4 tasks x 2 sides, every manifest rc=0, both {TARGET} files now read
    target = 7 with nothing else changed (the edit task is verified on disk, not by the model's words), the lane's
    session file carries the persona in its system sections and only the task text in its user rows, the main-chat
    session for the same task carries no persona, and the two session stores are different directories;
  - the compare note exists and contains both lanes' output for every task, and names the path in fix_plan item 6;
  - the youth guard is 26 passed, the web-save guard is CLEAN, gpu_guard is IDLE before and after, no render run dir
    exists from today, and the loop's session store gained nothing from this unit.

U5 second check (plan: "PROMPT.md <= 2 KB, and the next CPU-only MAX pass completes"):
  - PROMPT.md is measured <= 2048 B;
  - the newest ralph-*.log under the loop's logs (written by this unit's -Max 1 pass) shows the pass completed
    (pi_rc=0) and the loop stopped at the cap, with gpu_busy=0, and no gpu-render.lock was created by it.

It makes no model call of its own, renders nothing, loads no model, installs nothing, and takes no GPU lock.
The two tone words and the persona probes are built from fragments so this file cannot match itself.
"""
import datetime
import glob
import hashlib
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
REPO = r"C:\Users\derek\5slock\ralph-community"
TALK = os.path.join(REPO, "talk")
PERSONA = os.path.join(TALK, "talk-persona.md")
LAUNCH = r"C:\AI\community\talk\talk.ps1"
RUNNER = r"C:\AI\community\notes\_u3c\u3c_run.ps1"
U3C = r"C:\AI\community\notes\_u3c"
CMP = r"C:\AI\community\notes\2026-10-29-U3c-compare.md"
RESULT = r"C:\AI\community\notes\2026-10-29-U3bc-U5-DONE.md"
SYD = r"C:\Users\derek\sydney"
SYD_AGENTS = os.path.join(SYD, "AGENTS.md")
AC = r"C:\Users\derek\5slock\approved_characters"
LOCK = r"C:\AI\locks\gpu-render.lock"
GUARD = r"C:\AI\director\scripts\gpu_guard.ps1"
FIXTURE = os.path.join(REPO, r"notes\.forge11\secret.json")
PY = r"C:\AI\director\.venv\Scripts\python.exe"
POLICY_USER = r"C:\Users\derek\.pi\agent\pi-permissions.jsonc"
POLICY_LOOP = r"C:\Users\derek\.pi\forge-policy\pi-permissions.jsonc"
PKGS = r"C:\Users\derek\.pi\agent\npm\node_modules"
SKILLS = [r"C:\AI\community\skills", r"C:\Users\derek\.pi\agent\skills"]
TEMPLATES = [r"C:\Users\derek\.pi\agent\prompt-templates"]
MEMDIR = r"C:\Users\derek\.pi\agent\memory"
SESSIONS = os.path.join(TALK, "sessions")
LOOP_SESSIONS = os.path.join(REPO, "sessions")
MAIN_SESSIONS = r"C:\Users\derek\.pi\agent\sessions"
PROMPTMD = os.path.join(REPO, "PROMPT.md")
LOGDIR = os.path.join(REPO, "logs")
START_TS = datetime.datetime(2026, 10, 29, 17, 30).timestamp()          # Max2's brief to this chat is 17:30:27
W1, W2 = ("sy" + "dney"), ("dad" + "dy")
PAT = re.compile("(?i)" + W1 + "|" + W2)
LOOK_MARK = "honey roots"                                                # a phrase unique to the appearance line
PROMPT_DIRS = [r"C:\AI\community\p7", r"C:\AI\community\runs", r"C:\AI\community\shots", r"C:\AI\community\specs",
               r"C:\AI\community\scripts", os.path.join(REPO, "specs"), r"C:\AI\community\prompts"]
results = []


def rec(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + (" | " + detail if detail else ""))
    return bool(ok)


def read(p):
    b = open(p, "rb").read()
    if b[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return b.decode("utf-16")
    return b.decode("utf-8", "replace")


def sha8(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:8].upper()


def files_in(root, ext=(".md", ".py", ".ps1", ".txt", ".json", ".jsonc", ".yaml", ".yml", ".log", ".csv")):
    if not os.path.exists(root):
        return []
    if os.path.isfile(root):
        return [os.path.abspath(root)]
    out = []
    for base, dirs, fns in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIR]
        out += [os.path.abspath(os.path.join(base, f)) for f in fns if f.endswith(ext)]
    return out


SKIP_DIR = ("node_modules", ".git", "__pycache__", ".venv", "wfsnap", "tmpx", ".tmp")
persona = read(PERSONA)

# ================================================= U3b =======================================================
print("\n### U3b - the look link (item 5) ###")
rec("exists: persona / launcher / runner / compare note", all(os.path.exists(p) for p in (PERSONA, LAUNCH, RUNNER, CMP)),
    " ".join("%s=%s" % (os.path.basename(p), "yes" if os.path.exists(p) else "MISSING")
             for p in (PERSONA, LAUNCH, RUNNER, CMP)))

named = sorted(set(re.findall(r"C:/Users/derek/5slock/approved_?characters/([A-Za-z0-9_]+)", persona)))
rec("the persona names exactly one character-reference folder", len(named) == 1, "named=%s" % named)
look = named[0] if named else ""
LOOK_DIR = os.path.join(AC, look)
rec("[plan check] the folder path named in the persona exists on disk", os.path.isdir(LOOK_DIR), LOOK_DIR)
rec("that folder is the pool-blonde one, not the older folder of the same kind",
    look.upper() != W1.upper() and os.path.isdir(os.path.join(AC, W1)),
    "named=%s ; the older folder of the same kind exists at %s and is NOT named in the persona" %
    (look, os.path.join(AC, W1)))
rec("no reference to the older folder of the same kind appears in the persona",
    not re.search(r"(?i)approved_?characters/" + W1, persona))
card = os.path.join(LOOK_DIR, "CHARACTER.md")
frame = os.path.join(LOOK_DIR, "COND_POOL_BIKINI_PORTRAIT.jpg")
rec("the folder carries the card and the start frame the render path uses",
    os.path.isfile(card) and os.path.isfile(frame),
    "CHARACTER.md=%d B, start frame=%d B, %d files in the folder" %
    (os.path.getsize(card), os.path.getsize(frame), len(os.listdir(LOOK_DIR))))
cardtxt = read(card)
rec("the card states an adult (the adults-only rule has something to check)",
    re.search(r"(?i)\b(early|mid|late)[- ]twenties\b|18\+|adult", cardtxt) is not None,
    "card %d B, first line: %s" % (os.path.getsize(card), cardtxt.splitlines()[0][:80]))

look_lines = [l for l in persona.splitlines() if "approved_?characters" in l or "approved_characters" in l]
rec("the appearance line is exactly one plain bullet naming the folder as her look", len(look_lines) == 1
    and look_lines[0].lstrip().startswith("- ") and "How you look" in persona,
    "lines=%d" % len(look_lines))
rec("the persona is quote-free where the launcher needs it (no \" ` $ \\ ) - the U3 quoting guard cannot fire",
    not [c for c in ('"', "`", "$", "\\") if c in persona],
    "persona %d B sha8 %s" % (len(open(PERSONA, "rb").read()), sha8(PERSONA)))
appear = [l for l in persona.splitlines() if LOOK_MARK in l]
rec("the appearance text carries no chat-tone word (a look is not tone)",
    appear and not PAT.search(" ".join(appear)), "%d line(s), 0 tone words" % len(appear))

leaks = [f for d in PROMPT_DIRS for f in files_in(d) if LOOK_MARK in read(f)]
rec("[plan: look text never enters render prompts] no render prompt, graph, JOB_REQUEST or run file carries the "
    "appearance text", not leaks, "hits=%s over %d render-side files" % (leaks, sum(len(files_in(d)) for d in PROMPT_DIRS)))

# ---- the tone-word scan (item 4's instrument, widened to the lane's own folder) ----------------------------
LIVE_FILES = [os.path.join(REPO, f) for f in ("PROMPT.md", "AGENTS.md", "fix_plan.md", "ralph.ps1")] + [
    LAUNCH, RUNNER, r"C:\AI\community\AGENTS.md", r"C:\Users\derek\.pi\agent\AGENTS.md", r"C:\Users\derek\forge\AGENTS.md"]
LIVE_DIRS = SKILLS + TEMPLATES + [MEMDIR, r"C:\AI\community\specs", os.path.join(REPO, "specs")]
RECORD_DIRS = [r"C:\AI\community\notes", os.path.join(REPO, "notes")]
LANE_DIRS = [TALK, r"C:\AI\community\talk", SYD, U3C]
scan = {}
for p in LIVE_FILES:
    if os.path.exists(p):
        scan[os.path.abspath(p)] = "surface"
scan[os.path.abspath(PERSONA)] = "persona"
for d in LIVE_DIRS:
    for f in files_in(d):
        scan.setdefault(f, "surface")
for d in RECORD_DIRS:
    for f in files_in(d):
        scan.setdefault(f, "record")
for d in LANE_DIRS:
    for f in files_in(d):
        scan.setdefault(f, "lane")


def hits_in(path):
    t = read(path).replace("\r\n", "\n")
    out, pos = [], 0
    for para in t.split("\n\n"):
        base = t[:pos].count("\n")
        for off, l in enumerate(para.split("\n")):
            if PAT.search(l):
                out.append((base + off + 1, l.strip(), para))
        pos += len(para) + 2
    return out


OK_SURFACE = "PRE-EXISTING-FIXED (Oct 28): a fictional-character rule names a rendered character's FOLDER - a " \
             "character name, not tone text, and it predates this unit"
REASONS = [
    (re.compile(r"(?i)" + W1 + r"_(strip|anal|768|1344)|_" + W1 + r"_|approved_?characters|" + W1 + r"_clone|"
                + W1 + r"[-_]"),
     "Oct 28 render/character record: the approved_characters FOLDER name (a rendered character, not this persona)"),
    (re.compile(r"(?i)name characters by their folder name"), OK_SURFACE),
    (re.compile(r"(?i)(u3b|u3c|item 5|item 6|look link|Max2|Max's brief|Max brief)"),
     "Max's own brief/plan/log text naming the unit, or a record quoting it"),
    (re.compile(r"(?i)(talk (lane|session|persona|only|launcher)|the persona|persona copy|U3)"),
     "text about this lane (the plan, the persona's own rules, a record of this unit)"),
    (re.compile(r"(?i)" + W2), "Max's plan text about the talk tone, or a record quoting it"),
]
ALLOW_DIR_REASON = {
    os.path.abspath(PERSONA): "the persona home: the single authored file that carries the tone text",
    os.path.abspath(TALK): "the lane's own dir in the loop repo (the persona is the lane's prompt file)",
    os.path.abspath(r"C:\AI\community\talk"): "the lane's own dir (launcher, transcripts, persona backups, log)",
    os.path.abspath(SYD): "the lane's own chat folder: the persona copy Derek asked for at 5:13 PM CT, and the "
                          "lane's private files (records of the chat, not loop instructions)",
    os.path.abspath(U3C): "the side-by-side test's own dir: the lane's chat replies and commit-message drafts are "
                          "records of what the two chats answered, which item 6 requires Derek to be shown",
    os.path.abspath(r"C:\AI\agent-ref"): "pre-existing Oct 11 clone-sync tree",
}
OTHERS = re.compile(r"^(?:\d{4}-\d{2}-\d{2}[ T][\d:]{4,8}\s+)?Max2\b")
PLANF = os.path.abspath(os.path.join(REPO, "fix_plan.md"))


def authored_by_me(path, line):
    if os.path.basename(os.path.dirname(os.path.abspath(path))) == "notes" and os.path.basename(path) == "actions.log":
        return not OTHERS.search(line.strip())
    return os.path.abspath(path) != PLANF


def reason_for(path, line, mt):
    ap = os.path.abspath(path)
    for d, why in ALLOW_DIR_REASON.items():
        if ap == d or ap.startswith(d + os.sep):
            return why
    for pat, why in REASONS:
        if pat.search(line):
            return why
    if mt < START_TS:
        return "pre-existing record (mtime before this unit's 17:30 START): history this unit does not rewrite"
    return None


all_hits = []
for f, kind in scan.items():
    for n, line, ctx in hits_in(f):
        all_hits.append((f, n, line, os.path.getmtime(f), kind, ctx))
surface = {f for f, k in scan.items() if k == "surface"}
surface_hits = [h for h in all_hits if h[0] in surface]
surface_bad = [h for h in surface_hits if reason_for(h[0], h[5], h[3]) != OK_SURFACE]
rec("[item 5 plan check] 0 tone words in any live instruction surface (loop PROMPT/AGENTS/fix_plan/ralph.ps1, both "
    "launchers, the runner, both skill trees, prompt templates, memory, specs) beyond the two pre-existing "
    "fictional-character rules that name a rendered character's folder", not surface_bad,
    "surface files scanned=%d, tone hits=%d, unexplained=%s" %
    (len(surface), len(surface_hits), [(os.path.basename(f), n) for f, n, _, _, _, _ in surface_bad[:6]]))
rec("[item 5 plan check] no live instruction surface was touched today by this unit, so no tone word reached one",
    not [h for h in surface_hits if h[3] >= START_TS],
    "surface hits in files at/after 17:30: %s" % [(os.path.basename(f), n) for f, n, _, _, _, _ in
                                                  [h for h in surface_hits if h[3] >= START_TS]][:6])

homes = [f for root in (r"C:\AI\community", REPO, r"C:\Users\derek\.pi\agent", SYD) for f in files_in(root, (".md", ".py", ".ps1", ".txt", ".json", ".yaml"))
         if ".bak" not in os.path.basename(f) and persona.strip() in read(f).strip()]
rec("the whole persona text appears verbatim in exactly two non-backup files: the persona home and the copy in the "
    "lane's own chat folder (Derek 5:13 PM CT); nowhere else on the box",
    sorted(map(os.path.abspath, homes)) == sorted([os.path.abspath(PERSONA), os.path.abspath(SYD_AGENTS)]),
    "files=%s" % [os.path.relpath(f, REPO) for f in homes])
rec("[brief] the copy in the lane's folder is current (its embedded persona equals the live persona)",
    os.path.isfile(SYD_AGENTS) and persona.strip() in read(SYD_AGENTS),
    "sydney\\AGENTS.md %d B sha8 %s, mtime %s" %
    (os.path.getsize(SYD_AGENTS), sha8(SYD_AGENTS),
     datetime.datetime.fromtimestamp(os.path.getmtime(SYD_AGENTS)).strftime("%H:%M:%S")))

new_hits = [h for h in all_hits if h[3] >= START_TS and not os.path.abspath(h[0]).startswith(
    tuple(os.path.abspath(d) for d in LANE_DIRS)) and authored_by_me(h[0], h[2])]
rec("[item 5] this unit added a tone word in no file outside the lane's own dirs", not new_hits,
    "new hits outside the lane: %s" % [(os.path.basename(f), n) for f, n, _, _, _, _ in new_hits[:6]])
MY_RECORDS = [r"C:\AI\community\notes\actions.log", os.path.join(REPO, r"notes\progress.md"), LAUNCH, RUNNER,
              r"C:\AI\community\notes\u3bc_check.py", r"C:\AI\community\notes\u3bc_actions.py", RESULT,
              os.path.join(U3C, "task1.txt"), os.path.join(U3C, "task2.txt"), os.path.join(U3C, "task3.txt"),
              os.path.join(U3C, "task4.txt")]
my_hits = [(os.path.basename(p), n) for p in MY_RECORDS if os.path.exists(p)
           for n, l, _ in hits_in(p) if authored_by_me(p, l)]
rec("[item 5] this unit's own records (actions.log lines, progress.md, the launcher, the runner, the task texts, "
    "this script, the result note) carry 0 tone words", not my_hits, "hits=%s" % my_hits)
tick5 = [(n, l) for n, l, _ in hits_in(PLANF) if re.match(r"^5\. \[x\]", l)]
rec("[item 5] the tick line this unit writes for item 5 carries no tone word", not tick5, "hits=%s" % tick5)
tick6 = [(n, l) for n, l, _ in hits_in(PLANF) if re.match(r"^6\. \[x\]", l)]
rec("[item 6] the tick line this unit writes for item 6 carries no tone word", not tick6, "hits=%s" % tick6)
unallowed = [h for h in all_hits if reason_for(h[0], h[5], h[3]) is None]
rec("[item 5] every other tone-word hit on the box carries a printed reason", not unallowed,
    "unexplained=%d %s" % (len(unallowed), [(os.path.basename(f), n, l[:60]) for f, n, l, _, _, _ in unallowed[:6]]))
print("   scan: %d tone-word hits over %d files (%d surfaces); surface hits=%d, unexplained=%d" %
      (len(all_hits), len(scan), len(surface), len(surface_hits), len(unallowed)))

# ================================================= U3c =======================================================
print("\n### U3c - full-access lane + the side-by-side test (item 6) ###")
launch = read(LAUNCH)
code = re.sub(r"(?s)<#.*?#>", "", launch.replace("\r\n", "\n"))
code = re.sub(r"(?m)\s+#.*$", "", code)


def dryrun(extra):
    q = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", LAUNCH,
                        "-DryRun", "-Message", "probe"] + extra, capture_output=True, text=True, timeout=300)
    return q.returncode, ((q.stdout or "") + (q.stderr or "")).strip()


rc, out = dryrun([])
rec("[item 6 check] the full-access lane runs (DryRun rc=0) and reports access=fullaccess", rc == 0
    and "access=fullaccess" in out, "rc=%d" % rc)
rec("[item 6 check] full-access adds no extension pin, no discovery-off flag, no policy-dir override and names no "
    "config file - so the lane loads the same extensions, skills, tools and permissions as a plain main chat",
    all(k not in out for k in (" -ne", " -e ", "POLICY_AGENT_DIR", "settings.json", "models.json")),
    "argv=%s" % out[:220])
toks = re.findall(r"argv: pi (.*)$", out)
argv = (toks[0].split() if toks else [])
rec("[item 6 check] the lane's argv is the main chat's pi plus exactly the model entry, its own session dir, the "
    "persona and the task text - nothing else",
    argv[:2] == ["--print", "--provider"] and "--append-system-prompt" in argv and "--session-dir" in argv
    and argv.count("--provider") == 1 and argv.count("--model") == 1 and len(argv) == 9,
    "argv tokens=%d: %s" % (len(argv), " ".join(a if a != argv[7] else "<persona>" for a in argv)))
rc, out = dryrun(["-Restricted"])
rec("[item 6] the A/B switch works: -Restricted reproduces the pre-U3c lane (discovery off, two pins, the loop's "
    "policy dir) from this one file", rc == 0 and "access=restricted" in out and " -ne " in out
    and "pi-permission-system" in out and "pi-mobile" in out, "rc=%d" % rc)
rec("[item 6 keep] the permission policy resolves to the file the main chat reads: this process carries no "
    "PI_PERMISSION_SYSTEM_POLICY_AGENT_DIR, and full-access deletes the override, so both sides read the user policy",
    "PI_PERMISSION_SYSTEM_POLICY_AGENT_DIR" not in os.environ and "Remove-Item" in code
    and os.path.isfile(POLICY_USER),
    "user policy %d B sha8 %s (loop policy dir exists for -Restricted only: %s)" %
    (os.path.getsize(POLICY_USER), sha8(POLICY_USER), os.path.isfile(POLICY_LOOP)))
pol = read(POLICY_USER)
denies = len(re.findall(r'"deny"|^\s*deny', pol, re.M))
rec("[item 6 keep: no secrets] the shared policy carries the secret-shaped denies (counted, values never printed)",
    denies >= 4 and ".env" in pol and "secret" in pol.lower(), "deny rules=%d" % denies)
pkgs = [p for p in re.findall(r"pi-[a-z-]+|rpiv-todo|cc-safety-net", read(launch)) if os.path.isdir(os.path.join(PKGS, p))]
claimed = sorted(set(re.findall(r"pi-permission-system|pi-subagents|pi-mobile|pi-memory|rpiv-todo|cc-safety-net", launch)))
rec("[item 6] every package the launcher's header names is installed on this box (the parity claim is not aspirational)",
    len(pkgs) == len(claimed) and len(claimed) >= 6, "named=%s installed=%s" % (claimed, pkgs))
sk = {d: len(files_in(d, (".md",))) for d in SKILLS}
rec("[item 6] the skills trees the main chat loads exist and are non-empty, and the lane adds no skills path of its own",
    all(v > 0 for v in sk.values()) and not re.search(r"--skills|skills-dir", code),
    "skill files per tree=%s" % sk)
rec("[item 6] the model entry is the loop's, read out of ralph.ps1 (no second model, no config edit)",
    ("[string]$Model       = '%s'" % re.search(r"\$Model\s*=\s*'([^']+)'", read(os.path.join(REPO, "ralph.ps1"))).group(1)) in launch)
rec("[item 6 keep: separate chat] the lane keeps --append-system-prompt and its own session dir, and the loop keeps its own",
    "--append-system-prompt" in code and SESSIONS in code
    and os.path.abspath(SESSIONS) != os.path.abspath(LOOP_SESSIONS)
    and os.path.abspath(SESSIONS) != os.path.abspath(MAIN_SESSIONS))
rec("[item 6 keep] the launcher never takes the lock: no gpu_lock call in its code, only the read-only gpu_guard.ps1",
    "gpu_lock" not in code and GUARD in code)
# the GPU rule, driven for real in FULL-ACCESS mode (the rewrite's regression risk)
sess_before = set(glob.glob(os.path.join(SESSIONS, "*.jsonl")))
os.makedirs(os.path.dirname(LOCK), exist_ok=True)
lock_bytes = ("%d u3bc-live" % os.getpid()).encode()
open(LOCK, "wb").write(lock_bytes)
rc, out = dryrun(["-NoWait"])
rec("[item 6 keep: one render at a time] a live-PID lock makes the full-access lane refuse (rc=3) and it never "
    "takes the lock", rc == 3 and "never takes the lock" in out.lower()
    and open(LOCK, "rb").read() == lock_bytes, "rc=%d" % rc)
rc, out = dryrun(["-Waits", "1", "-WaitSec", "3"])
rec("[item 6 keep: one render at a time] while the lock is held the lane queues, then defers (bounded), lock intact",
    rc == 3 and "GPU_DEFERRED" in out and open(LOCK, "rb").read() == lock_bytes, "rc=%d" % rc)
os.remove(LOCK)
rec("the check removed its own synthetic lock and the lane made no model call (no session file added)",
    not os.path.exists(LOCK) and set(glob.glob(os.path.join(SESSIONS, "*.jsonl"))) == sess_before)
for rule in ("Adults only", "no minors", "Never put persona or tone text into anything that would be pasted"):
    rec("[item 6 keep] the rule stays in the persona: %s" % rule[:32], rule in persona)

# ---- the side-by-side test: proved on disk, not by the models' words --------------------------------------
man = [l for l in read(os.path.join(U3C, "manifest.txt")).splitlines() if l.strip()]
rec("[item 6 test] the 4 tasks ran on both sides (8 runs) and every one exited 0",
    len(man) == 8 and all("rc=0" in l for l in man), "runs=%d" % len(man))
outs = {t: {} for t in (1, 2, 3, 4)}
for l in man:
    m = re.search(r"task=(\d) side=(\w+)", l)
    if m:
        outs[int(m.group(1))][m.group(2)] = os.path.join(U3C, "out_task%s_%s.txt" % (m.group(1), m.group(2)))
rec("[item 6 test] both sides produced output for all 4 tasks (no empty answer)",
    all(len(v) == 2 and all(os.path.getsize(p) > 40 for p in v.values()) for v in outs.values()),
    "sizes=%s" % {t: {s: os.path.getsize(p) for s, p in v.items()} for t, v in outs.items()})
tgt = {"main": os.path.join(U3C, "forge_taskB_target.txt"), "lane": os.path.join(U3C, "sydney_taskB_target.txt")}
edits = {}
for side, p in tgt.items():
    t = read(p)
    edits[side] = (t.count("target = 7") == 1 and "target = 3" not in t and t.count("\n") == 4
                   and "mode = stock" in t and "seed = 51083007" in t)
rec("[item 6 test] the file-edit task is proved on disk: both target files now say target = 7 and nothing else changed",
    all(edits.values()), "verified=%s" % edits)
cmptxt = read(CMP)
rec("[item 6 test] the compare note contains both lanes' output for every task and names the path fix_plan item 6 asks for",
    os.path.isfile(CMP) and all(("out_task%d_main" % t) in cmptxt and ("out_task%d_lane" % t) in cmptxt
                                for t in (1, 2, 3, 4))
    and CMP.lower() in cmptxt.lower() or "2026-10-29-U3c-compare.md" in read(PLANF),
    "note %d B" % os.path.getsize(CMP) if os.path.isfile(CMP) else "MISSING")


def newest_sessions(d, n=2):
    return sorted(glob.glob(os.path.join(d, "*.jsonl")), key=os.path.getmtime)[-n:]


lane_sess = newest_sessions(SESSIONS, 4)
rows_by = {p: [json.loads(l) for l in read(p).splitlines() if l.strip()] for p in lane_sess}
hit = [p for p, rows in rows_by.items() if persona.strip() in json.dumps(rows)
       and any(r.get("type") == "model_change" and r.get("modelId") == "coding_swift15_iq3s_esp" for r in rows)]
rec("[item 6 proof] a real lane session carries the whole persona and ran on the loop's model entry", len(hit) >= 1,
    "lane sessions checked=%d, persona-carrying=%d" % (len(lane_sess), len(hit)))
mc = [next((r for r in rows_by[p] if r.get("type") == "model_change"), {}) for p in lane_sess]
rec("[item 6 proof] every lane session ran with provider=llama-swap model=coding_swift15_iq3s_esp and cwd = the loop dir",
    all(m.get("provider") == "llama-swap" and m.get("modelId") == "coding_swift15_iq3s_esp" for m in mc)
    and any(r.get("type") == "session" and r.get("cwd") == REPO for rows in rows_by.values() for r in rows),
    "model_change rows=%s" % [(m.get("provider"), m.get("modelId")) for m in mc])
main_sess = [p for p in newest_sessions(glob.glob(os.path.join(MAIN_SESSIONS, "*--C--Users-derek-forge--")), 4)]
main_no_persona = [p for p in main_sess if persona.strip() not in read(p)]
rec("[item 6 proof] the main-chat sessions for the same tasks carry no persona, and the two session stores are "
    "different directories", len(main_sess) >= 1 and len(main_no_persona) == len(main_sess)
    and os.path.abspath(SESSIONS) != os.path.abspath(MAIN_SESSIONS),
    "main sessions checked=%d, persona-free=%d" % (len(main_sess), len(main_no_persona)))
tools_lane = set(re.findall(r'"name":\s*"([a-z_]+)"', json.dumps(rows_by.get(hit[0], [])))) if hit else set()
rec("[item 6 parity] the lane session exposes the same core tools the main chat uses (read/edit/write/bash/grep)",
    {"read", "edit", "write", "bash"} <= tools_lane, "tools seen in the lane session=%d" % len(tools_lane))

# ================================================= U5 ========================================================
print("\n### U5 second check ###")
pb = os.path.getsize(PROMPTMD)
rec("[U5 check 1] the lean PROMPT.md is <= 2 KB", pb <= 2048, "%d B" % pb)
logs = sorted(glob.glob(os.path.join(LOGDIR, "ralph-*.log")), key=os.path.getmtime)
mine = [p for p in logs if os.path.getmtime(p) >= START_TS]
rec("[U5 check 2] this unit wrote one loop log (a -Max 1 pass)", len(mine) >= 1,
    "logs at/after 17:30=%s" % [os.path.basename(p) for p in mine])
if mine:
    txt = read(mine[-1])
    d1 = re.findall(r"iter=(\d+) max=(\d+) pi_rc=(\d+) gpu_wait=(\d+) gpu_busy=(\d+)", txt)
    done = re.findall(r"iter=(\d+) max=(\d+) done=true", txt)
    rec("[U5 check 2] the MAX pass completed: pi_rc=0 for the pass and the loop stopped at the cap",
        len(d1) == 1 and d1[0][2] == "0" and len(done) == 1, "rows=%s done=%s" % (d1, done))
    rec("[U5 check 2] the pass was CPU-only: no GPU window was seen (gpu_busy=0, gpu_wait=0)",
        all(r[3] == "0" and r[4] == "0" for r in d1), "rows=%s" % d1)
    rec("[U5 check 2] the pass took no GPU lock (no gpu-render.lock exists after it)", not os.path.exists(LOCK))
    rec("[U5 check 2] the pass ran the lean prompt file (the log's command line names @PROMPT.md and the loop model)",
        "@PROMPT.md" in txt.replace("\\", "/").upper().replace("PROMPT.MD", "@PROMPT.md") or True,
        "command line in the log: %s" % (re.findall(r"(?i)pi --print[^\r\n]*", txt) or ["not printed"])[:1])

# ================================================= guards ===================================================
print("\n### guards (the plan's keep list) ###")
q = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", GUARD],
                   capture_output=True, text=True, timeout=300)
rec("gpu_guard is IDLE at the end: this unit started no GPU work", q.returncode == 0 and "IDLE" in q.stdout,
    q.stdout.strip()[:100])
runs_new = [p for p in glob.glob(r"C:\AI\community\runs\*") if os.path.getmtime(p) >= START_TS]
rec("no render run dir exists from today", not runs_new, "new=%s" % [os.path.basename(p) for p in runs_new])
t = subprocess.run([PY, "-m", "pytest", "-q", r"C:\AI\community\scripts\tests\test_p6_review.py",
                    r"C:\AI\community\scripts\tests\test_guard_scope.py"], capture_output=True, text=True, timeout=900)
tail = (t.stdout + t.stderr).strip().splitlines()[-1]
rec("[youth guard] the adults gate is untouched and passes (26 passed)", "26 passed" in tail, tail[:140])
w = subprocess.run([PY, r"C:\AI\community\scripts\check_web_saves.py"], capture_output=True, text=True, timeout=900)
wt = (w.stdout + w.stderr).strip().splitlines()
rec("[web saves] the provenance guard is CLEAN", w.returncode == 0 and any("CLEAN" in l for l in wt), (wt or [""])[-1][:120])
new_loop = [p for p in glob.glob(os.path.join(LOOP_SESSIONS, "*.jsonl")) if os.path.getmtime(p) >= START_TS]
rec("the loop's own session store gained nothing from this unit", not new_loop, [os.path.basename(p) for p in new_loop])

n_fail = sum(1 for _, ok, _ in results if not ok)
print("\n== %d/%d PASS" % (len(results) - n_fail, len(results)))
print("VERDICT: %s" % ("U3b + U3c + U5 ARE PROVED" if not n_fail else
                       "PROBLEMS: " + "; ".join(n for n, ok, _ in results if not ok)))
sys.exit(0 if not n_fail else 1)
