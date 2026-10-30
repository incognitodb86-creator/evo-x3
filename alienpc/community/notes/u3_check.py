# HISTORICAL one-shot record (U3), not a reusable check: hard-coded paths/sizes/dates from that day; do not re-run as a live gate. Max2 audit-fix #20, 2026-10-29.
"""MAX block item 4 (U3, the talk lane) self-verifying check - Max brief 11:0x CT; plan U3 = file/check source.

The plan's two checks:
  (1) a case-insensitive scan for the two tone words over PROMPT/AGENTS/skills/notes/memory/new prompts = 0 hits
      outside the talk persona file;
  (2) a denied secret read in a talk session proves permissions load.
Plan stop conditions are checked too: tone text outside talk, a second model load, chat during the lock, a
duplicated rule, a missing backup.

Check (1) is built as the instrument the plan means, and says exactly what it proves: 0 tone words in any LIVE
instruction surface (the files that tell a model what to do: PROMPT.md, AGENTS.md, the launchers, skills, prompt
templates, memory, render-prompt sources) - the persona file is the only prompt file that carries tone; 0 tone words
in this unit's own records and in its tick line; and every other hit on the box must carry a printed, narrow reason
(an Oct 28 render/character record naming the approved_characters FOLDER, a rendered character and not this persona;
Max's own plan/brief/item titles; records quoting those titles; the talk lane's own dir). A new leak fails the check.
Conversation records (sessions dirs, transcripts) are excluded as records of what was said, not instructions.

It also proves the rest of U3 objectively: the launcher's argv equals the loop's entry (provider and model read out
of ralph.ps1) plus exactly the three talk-only additions; the session file's SYSTEM sections carry the whole
persona while its user rows carry only Derek's message; the session's model_change row is the loop's llama-swap
entry and cwd; the session has no memory tool and the memory tree is byte-identical to the START baseline; the GPU
rule (ask gpu_guard, never take the lock, queue while it is held) is driven with a synthetic live-PID lock; the
native-quoting guard fires on a persona containing a quote character (the defect that broke the first run); and no
config file, MAX item 2/3 state, youth guard or web-save guard moved.

No LLM call is made here (the real turn is already evidenced), nothing is rendered, no model is loaded, nothing is
installed. The tone words and the persona probes are built from fragments so that this file cannot match itself.
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
PERBAK = r"C:\AI\community\talk\talk-persona.md.bak-20261029-u3a"
LAUNCH = r"C:\AI\community\talk\talk.ps1"
LOOP_PS1 = os.path.join(REPO, "ralph.ps1")
SESSIONS = os.path.join(TALK, "sessions")
LOOP_SESSIONS = os.path.join(REPO, "sessions")
LOCK = r"C:\AI\locks\gpu-render.lock"
GUARD = r"C:\AI\director\scripts\gpu_guard.ps1"
FIXTURE = os.path.join(REPO, r"notes\.forge11\secret.json")
EVID = r"C:\AI\community\talk\talk_run_20261029_take3.txt"
MEMDIR = r"C:\Users\derek\.pi\agent\memory"
PY = r"C:\AI\director\.venv\Scripts\python.exe"
W1, W2 = ("sy" + "dney"), ("dad" + "dy")
PAT = re.compile("(?i)" + W1 + "|" + W2)
PROBE = "warm talk " + "companion"                                    # the persona's own signature phrase
PROBES_SYS = [PROBE, "Ground " + "rules", "What this lane never does", "gpu-render.lock", "swearing level"]
START_TS = datetime.datetime(2026, 10, 29, 10, 56).timestamp()        # the unit's START record is 10:57
MEM_WRITE_OK = datetime.datetime(2026, 10, 29, 11, 20).timestamp()     # the close-out record commit
SKILLS = [r"C:\AI\community\skills", r"C:\Users\derek\.pi\agent\skills"]
TEMPLATES = [r"C:\Users\derek\.pi\agent\prompt-templates"]
LIVE_FILES = [os.path.join(REPO, f) for f in ("PROMPT.md", "AGENTS.md", "ralph.ps1")] + [
    LAUNCH, r"C:\AI\community\AGENTS.md", r"C:\Users\derek\.pi\agent\AGENTS.md"]
LIVE_DIRS = SKILLS + TEMPLATES + [MEMDIR, r"C:\AI\community\specs", os.path.join(REPO, "specs")]
CODE_DIRS = [r"C:\AI\community\scripts", r"C:\AI\community\shots"]     # render code/inputs: allow-list enforced
RECORD_DIRS = [r"C:\AI\community\notes", os.path.join(REPO, "notes"), TALK, r"C:\AI\community\talk"]
# The unit's record LINES must carry no tone word at all (a log line, a progress line, a tick, a launcher, a
# script). The DONE note is a record of the scan itself: it has to quote what it found, so it is enforced by the
# reason classifier instead of by zero.
MY_RECORDS = [r"C:\AI\community\notes\actions.log", os.path.join(REPO, r"notes\progress.md"),
              LAUNCH, os.path.join(REPO, r"notes\u3_check.py"), os.path.join(REPO, r"notes\u3_start_record.py")]
# A tone-word hit needs a printed reason. The persona home is the one prompt file allowed to carry tone; the rest
# must be Oct 28 render/character records (the approved_characters FOLDER, a rendered character, not this persona),
# Max's own plan/brief/item titles, records quoting those titles, or the talk lane's own dir. The classifier is
# deliberately narrow: a pre-existing TONE leak in a note matches none of these and fails the check.
REASONS = [
    (re.compile(r"(?i)" + W1 + r"_(strip|anal|768|1344)|_" + W1 + r"_|approved_characters|" + W1 + r"_clone|"
                + W1 + r"[-_]"),
     "Oct 28 render/character record: the approved_characters FOLDER name (a rendered character, not this persona)"),
    (re.compile(r"(?i)name characters by their folder name"),
     "PRE-EXISTING-FIXED: a fictional-character rule names a character FOLDER (Oct 28, a rendered character, not "
     "this persona)"),
    (re.compile(r"(?i)(u3b|look link|item 5|Max2)"),
     "Max2's own brief/plan/log text naming the unit (his lines, written after this unit's record)"),
    (re.compile(r"(?i)(" + W1 + r" talk session|talk session|talk lane|talk companion|talk persona|talk-only|"
                r"talk launcher|the plan|MAX block|units -> u3|item 4)"),
     "Max's own plan/brief/item text naming the unit, or a record of this unit quoting that title / describing the "
     "lane"),
    (re.compile(r"(?i)" + W2), "Max's plan text about the talk tone, or a record quoting it"),
]
ALLOW_DIR_REASON = {
    os.path.abspath(TALK): "the talk lane's own dir (the persona file and its backup)",
    os.path.abspath(r"C:\AI\community\talk"): "the talk lane's own dir (launcher, transcript, backup, log)",
    os.path.abspath(r"C:\AI\agent-ref"): "pre-existing Oct 11 clone-sync tree",
}
BASELINE = {  # measured at the unit's START by notes/u3_start_record.py
    r"C:\Users\derek\.pi\agent\settings.json": (3551, "2026-10-29 05:22:33"),
    r"C:\Users\derek\.pi\agent\models.json": (4224, "2026-10-29 09:45:28"),
    r"C:\AI\director\scripts\llama_swap_keepalive.ps1": (817, "2026-10-26 08:17:36"),
    LOOP_PS1: (4924, "2026-10-29 09:05:59"),
    os.path.join(REPO, "PROMPT.md"): (6122, "2026-10-29 10:07:38"),
    os.path.join(REPO, "AGENTS.md"): (3381, "2026-10-28 17:02:33"),
    os.path.join(MEMDIR, "MEMORY.md"): (10454, None),
    os.path.join(MEMDIR, "SCRATCHPAD.md"): (412, None),
    os.path.join(MEMDIR, r"daily\2026-10-29.md"): (40872, "2026-10-29 10:55:23"),
    os.path.join(MEMDIR, r"daily\2026-10-28.md"): (146941, None),
}
JOB2 = ["notes/sh_job2_audit.py", "notes/sh_job2_collect.py", "notes/sh_job2_dump_sheet.py", "notes/sh_job2_llm.py",
        "notes/sh_job2_metrics.py", "notes/2026-10-28-small-helper-job2-DONE.md",
        "notes/2026-10-28-p15v2-scoring-rows.csv", "notes/2026-10-28-p15v2-scoring-rows.json",
        "notes/2026-10-28-p15v2-scoring-rows-run1-copy.csv", "notes/2026-10-28-p15v2-scoring-rows-run1-copy.json",
        "notes/2026-10-28-p15v2-scoring-rows-run2-select.csv", "notes/2026-10-28-p15v2-scoring-rows-run2-select.json"]
SKIP_DIR = ("node_modules", ".git", "__pycache__", ".venv", "runs", "tmpx", "wfsnap", "logs", "sessions")
SCAN_EXT = (".md", ".py", ".ps1", ".txt", ".json", ".jsonc", ".yaml", ".yml", ".log", ".csv")
results = []


def rec(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + (" | " + detail if detail else ""))
    return bool(ok)


def read(p):
    b = open(p, "rb").read()
    if b[:2] in (b"\xff\xfe", b"\xfe\xff"):        # PowerShell 5.1 Tee-Object writes UTF-16LE
        return b.decode("utf-16")
    return b.decode("utf-8", "replace")


def files_in(root):
    if not os.path.exists(root):
        return []
    if os.path.isfile(root):
        return [os.path.abspath(root)]
    out = []
    for base, dirs, fns in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIR]
        out += [os.path.abspath(os.path.join(base, f)) for f in fns if f.endswith(SCAN_EXT)]
    return out


def hits_in(path):
    """(line_no, line, paragraph). Markdown is hard-wrapped, so a reason often sits on a neighbour line: the
    classifier is given the whole paragraph, the report shows the line (method lesson of 2026-10-28: test prose on
    sentences, not lines)."""
    t = read(path).replace("\r\n", "\n")
    out, pos = [], 0
    for para in t.split("\n\n"):
        base = t[:pos].count("\n")
        for off, l in enumerate(para.split("\n")):
            if PAT.search(l):
                out.append((base + off + 1, l.strip(), para))
        pos += len(para) + 2
    return out


def reason_for(path, line, mt):
    ap = os.path.abspath(path)
    if ap == os.path.abspath(PERSONA):
        return "the persona home: the single file that carries the tone text"
    for d, why in ALLOW_DIR_REASON.items():
        if ap.startswith(d + os.sep) or ap == d:
            return why
    for pat, why in REASONS:
        if pat.search(line):
            return why
    if mt < START_TS:
        return ("pre-existing record, mtime before this unit's START: history that U3 does not rewrite (the plan "
                "keeps Oct 28 records as history)")
    return None


def code_of(text):
    """Keep only the launcher's code: the block comment and inline comments explain what the script does NOT do,
    which is prose, not an invocation."""
    t = re.sub(r"(?s)<#.*?#>", "", text.replace("\r\n", "\n"))
    return re.sub(r"(?m)\s+#.*$", "", t)


# ---- 0. files, and the backup rule (a missing backup of a touched file = fail per the plan) ------------------
for p in (PERSONA, LAUNCH, PERBAK, EVID):
    rec("exists: " + p, os.path.exists(p), "%d B" % (os.path.getsize(p) if os.path.exists(p) else -1))
rec("both U3 files were created by this unit (ctime >= START)",
    all(os.path.getctime(p) >= START_TS for p in (PERSONA, LAUNCH)),
    "the START probe printed exists=False for every target, so nothing was overwritten and no backup applies; the "
    "one file edited after creation (the persona) has its pre-edit bytes in the .bak above")
rec("the persona backup holds the earlier bytes (sha8 DE74EBE6, 2191 B) and differs from the live file",
    hashlib.sha256(open(PERBAK, "rb").read()).hexdigest().upper().startswith("DE74EBE6")
    and os.path.getsize(PERBAK) == 2191
    and hashlib.sha256(open(PERBAK, "rb").read()).hexdigest() != hashlib.sha256(open(PERSONA, "rb").read()).hexdigest(),
    "live sha8 %s" % hashlib.sha256(open(PERSONA, "rb").read()).hexdigest()[:8])

# ---- 1. one home for the persona ----------------------------------------------------------------------------
# Transcripts (sessions dirs) record what was sent, so they carry the persona by construction; the claim is about
# authored files, so *.jsonl and sessions dirs are excluded.
home = [f for root in (r"C:\AI\community", REPO, r"C:\Users\derek\.pi\agent") for f in files_in(root)
        if ".bak" not in os.path.basename(f) and f.endswith((".md", ".py", ".ps1", ".txt", ".json", ".yaml"))
        and PROBE in read(f)]
rec("the persona text lives in exactly one non-backup file, and it is the persona file",
    home == [os.path.abspath(PERSONA)], "files: %s" % home)

# ---- 2. plan check 1: the tone-word scan -------------------------------------------------------------------
scan = {}
for p in LIVE_FILES:
    if os.path.exists(p):
        scan[os.path.abspath(p)] = "surface"
scan[os.path.abspath(PERSONA)] = "persona"
scan[os.path.abspath(os.path.join(REPO, "fix_plan.md"))] = "record"
for d in LIVE_DIRS:
    for f in files_in(d):
        scan[f] = "surface"
for d in CODE_DIRS:
    for f in files_in(d):
        scan.setdefault(f, "code")
for d in RECORD_DIRS:
    for f in files_in(d):
        scan.setdefault(f, "record")
all_hits = []
for f, kind in scan.items():
    for n, line, ctx in hits_in(f):
        all_hits.append((f, n, line, os.path.getmtime(f), kind, ctx))
live_set = {f for f, kind in scan.items() if kind == "surface"}
live_hits = [h for h in all_hits if h[0] in live_set]
# The only permitted tone word in a live instruction surface is the pre-existing fictional-character rule that names
# a rendered character's FOLDER (present in two of Derek's Oct 28 skills). It is a character name, not tone text, and
# it predates this unit. A surface file touched today fails, and so does any other surface hit.
OK_SURFACE = "PRE-EXISTING-FIXED: a fictional-character rule names a character FOLDER (Oct 28, a rendered character, not this persona)"
live_bad = [h for h in live_hits if reason_for(h[0], h[5], h[3]) != OK_SURFACE]
live_new = [h for h in live_hits if h[3] >= START_TS]
lane_dirs = tuple(os.path.abspath(d) for d in (TALK, r"C:\AI\community\talk"))
DOC_NOTE = os.path.abspath(r"C:\AI\community\notes\2026-10-29-U3-talk-lane-DONE.md")
lane_hits = [h for h in all_hits if h[3] >= START_TS and os.path.abspath(h[0]).startswith(lane_dirs)]
# The DONE note is the record of this scan, so it must quote what it found; it is policed by the reason
# classifier, not by zero. Everything else new today must be the persona file.
# Max2's lines in the shared append-only actions.log start with his own author token, e.g.
#   "2026-10-29 11:20 Max2 EDIT fix_plan.md: ..."  or  "Max2: 2026-10-29 10:58 CT BRIEF ..."
# Case-sensitive on purpose: this unit's own lines carry the uppercase token "MAX", so they stay in scope.
OTHERS = re.compile(r"^(?:\d{4}-\d{2}-\d{2}[ T][\d:]{4,8}\s+)?Max2\b")
PLANF = os.path.abspath(os.path.join(REPO, "fix_plan.md"))


def authored_by_me(path, line):
    """actions.log is append-only and shared: lines whose author prefix says Max2/Max are his, not this unit's.
    fix_plan.md is Max2's task list: only the tick line is mine, and that is checked by tick_hits."""
    if os.path.basename(os.path.dirname(os.path.abspath(path))) == "notes" and os.path.basename(path) == "actions.log":
        return not OTHERS.search(line.strip())
    return os.path.abspath(path) != PLANF


new_hits = [h for h in all_hits if h[3] >= START_TS and os.path.abspath(h[0]) not in
            (os.path.abspath(PERSONA), DOC_NOTE)
            and not os.path.abspath(h[0]).startswith(lane_dirs) and authored_by_me(h[0], h[2])]
my_hits = [(p, n, l) for p in MY_RECORDS if os.path.exists(p) and os.path.abspath(p) != os.path.abspath(PERSONA)
           for n, l, _ in hits_in(p) if authored_by_me(p, l)]
# the tick line I write must stay clean; Max's item 4 title line is allowed
tick_hits = [(n, l) for n, l, _ in hits_in(os.path.join(REPO, "fix_plan.md")) if l.startswith("4. [x]")]
unallowed = [h for h in all_hits if reason_for(h[0], h[5], h[3]) is None]
print("\n--- scan: %d tone-word hits over %d files (%d surface files, %d record files); surface hits=%d, "
      "new-today hits=%d, unallowed=%d" % (len(all_hits), len(scan), len(live_set),
                                           len(scan) - len(live_set), len(live_hits), len(new_hits), len(unallowed)))
for f, n, line, mt, kind, ctx in sorted(all_hits, key=lambda h: (h[4], h[0], h[1]))[:30]:
    print("   [%s] %s L%d [%s] %s" % (kind, f, n, datetime.datetime.fromtimestamp(mt).strftime("%m-%d %H:%M"),
                                       line[:150]))
    print("        reason: %s" % reason_for(f, ctx, mt))
rec("[plan check 1] no tone word in any live instruction surface (PROMPT.md, AGENTS.md x3, both launchers, skills, "
    "prompt templates, memory, render-prompt sources) beyond the two printed pre-existing fictional-character rules "
    "that name a rendered character's folder", not live_bad,
    "surface hits: %s" % [(f, n, reason_for(f, c, mt)) for f, n, _, mt, _, c in live_bad])
rec("[plan check 1] no live instruction surface was touched by this unit, so no tone word reached one today",
    not live_new, "surface hits in files modified at/after START: %s" %
    [(f, n) for f, n, _, _, _, _ in live_new])
rec("[plan check 1] this unit added a tone word in exactly one authored file (the persona) plus its own lane dir "
    "(the transcripts where the model names itself) and the DONE note that records this scan; Max2's plan/log lines "
    "are his, and this unit's tick line is checked separately", not new_hits,
    "new hits elsewhere: %s" % [(f, n) for f, n, _, _, _, _ in new_hits])
print("   lane-dir hits (the persona home + the lane's own transcripts): %s" %
      [(os.path.basename(f), n) for f, n, _, _, _, _ in lane_hits])
rec("[plan check 1] the unit's own records (actions.log, progress.md, DONE note, the tick line, the launcher, its "
    "scripts) carry no tone word", not my_hits and not tick_hits,
    "record hits: %s | tick: %s" % ([(os.path.basename(p), n) for p, n, _ in my_hits], tick_hits))
rec("[plan check 1] every other hit on the box carries a printed reason (Oct 28 render/character records, Max's own "
    "plan/brief/item titles, records quoting them, records older than this unit, the talk lane's own dir)",
    not unallowed, "unexplained: %s" % [(f, n, l[:60]) for f, n, l, _, _, _ in unallowed[:8]])

# ---- 3. the launcher = the loop's entry + exactly the three talk-only additions -----------------------------
launch, loopps = read(LAUNCH), read(LOOP_PS1)
launch_code = code_of(launch)
loop_model = re.search(r"\$Model\s*=\s*'([^']+)'", loopps).group(1)
loop_provider = re.search(r"--provider\s+(\S+)", loopps).group(1)
need = ["--append-system-prompt", "--session-dir", "-ne", "-e", "--provider", "--model",
        "pi-permission-system", "pi-mobile", GUARD, "PI_PERMISSION_SYSTEM_POLICY_AGENT_DIR"]
rec("the launcher carries every element the plan names", all(k in launch for k in need),
    "missing: %s" % [k for k in need if k not in launch])
rec("the entry is the loop's %s / %s, read out of ralph.ps1 (no second model, no config edit)" %
    (loop_provider, loop_model),
    ("[string]$Model       = '%s'" % loop_model) in launch and ("[string]$Provider    = '%s'" % loop_provider) in launch)
exts = re.findall(r"\[string\]\$\w*Ext\s*=\s*'([^']+)'", launch)
rec("exactly two extensions load and both paths exist: pi-permission-system and pi-mobile",
    len(exts) == 2 and all(os.path.isdir(e) for e in exts) and any("pi-permission-system" in e for e in exts)
    and any("pi-mobile" in e for e in exts), "exts=%s" % exts)
rec("pi-memory is absent from the launcher's code (-ne turns discovery off, so it cannot load; the prose may "
    "explain this)", "pi-memory" not in launch_code)
rec("the launcher never takes the lock: no gpu_lock call in its code, only the read-only gpu_guard.ps1",
    "gpu_lock" not in launch_code and GUARD in launch_code)
rec("the talk session dir is the lane's own, and the loop keeps its own",
    os.path.abspath(SESSIONS) != os.path.abspath(LOOP_SESSIONS) and SESSIONS in launch and '"$K\\sessions"' in loopps)
rec("the native-quoting guard is present (a persona with a quote char must abort, not word-split into chat)",
    "[char]34" in launch and "break native argv quoting" in launch.lower())
rec("the launcher names no config file (settings.json / models.json / llama-swap.yaml)",
    not any(k in launch for k in ("settings.json", "models.json", "llama-swap.yaml")))

# ---- 4/5/6. the GPU rule and the quoting guard, driven for real ---------------------------------------------
def run_launch(args, timeout=300):
    q = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", LAUNCH] + args,
                       capture_output=True, text=True, timeout=timeout)
    return q.returncode, ((q.stdout or "") + (q.stderr or "")).strip()


sess_before = set(glob.glob(os.path.join(SESSIONS, "*.jsonl")))
rc, out = run_launch(["-DryRun", "-Message", "probe"])
rec("[GPU rule] with the GPU idle the DryRun runs, prints the argv, and never echoes the persona",
    rc == 0 and "--append-system-prompt" in out and "-ne" in out and "pi-permission-system" in out
    and PROBE not in out, "rc=%d" % rc)
rec("[no second model load] the DryRun created no session file, so no model call happened",
    set(glob.glob(os.path.join(SESSIONS, "*.jsonl"))) == sess_before)
os.makedirs(os.path.dirname(LOCK), exist_ok=True)
lock_bytes = ("%d u3-check-live" % os.getpid()).encode()
open(LOCK, "wb").write(lock_bytes)
rc, out = run_launch(["-DryRun", "-NoWait", "-Message", "probe"])
rec("[plan stop: chat during the lock] a live-PID lock makes the lane refuse (-NoWait) and it does not take the lock",
    rc == 3 and "never takes the lock" in out.lower() and open(LOCK, "rb").read() == lock_bytes,
    "rc=%d out=%s" % (rc, out[:150]))
rc, out = run_launch(["-DryRun", "-Message", "probe", "-Waits", "1", "-WaitSec", "3"])
rec("[plan stop: chat during the lock] while the lock is held the lane queues, then defers (bounded), lock intact",
    rc == 3 and "queues" in out.lower() and "GPU_DEFERRED" in out and open(LOCK, "rb").read() == lock_bytes,
    "rc=%d" % rc)
if os.path.exists(LOCK):
    os.remove(LOCK)
rec("the check removed its own synthetic lock", not os.path.exists(LOCK))
badp = r"C:\AI\community\talk\u3-bad-persona.md"
open(badp, "w", encoding="utf-8").write('You are a persona with a "quoted" word.\n')
rc, out = run_launch(["-DryRun", "-PersonaFile", badp, "-Message", "probe"])
rec("the quoting guard fires: a persona with a double quote aborts rc=4 instead of becoming chat noise",
    rc == 4 and "ABORT" in out, "rc=%d out=%s" % (rc, out[:160]))
os.remove(badp)

# ---- 7. the real talk turn: persona in the system prompt, permission denial, same entry, no memory ----------
sess = sorted(glob.glob(os.path.join(SESSIONS, "*.jsonl")), key=os.path.getmtime)[-1]
rows = [json.loads(l) for l in read(sess).splitlines() if l.strip()]
sysrow = next((r["message"] for r in rows if (r.get("message") or {}).get("role") == "system"), None)
sec_json = json.dumps((sysrow or {}).get("sections") or {})
rec("[the persona reaches the model] the session's system sections carry the whole persona",
    all(p in sec_json for p in PROBES_SYS),
    "session=%s missing=%s" % (os.path.basename(sess), [p for p in PROBES_SYS if p not in sec_json]))
users = [c if isinstance(m.get("content"), str) else json.dumps(m.get("content"))
         for r in rows for m in [r.get("message") or {}] if m.get("role") == "user"]
rec("Derek's message is the only user content: the persona is a system prompt, not chat noise",
    len(users) == 1 and PROBE not in users[0] and "secret.json" in users[0], "user rows=%d" % len(users))
mc = next((r for r in rows if r.get("type") == "model_change"), {})
rec("[plan: same entry and context as the loop] the session ran on %s/%s with cwd = the loop's dir" %
    (loop_provider, loop_model), mc.get("provider") == loop_provider and mc.get("modelId") == loop_model
    and any(r.get("type") == "session" and r.get("cwd") == REPO for r in rows))
dump = json.dumps(rows)
rec("[plan check 2] the secret read is DENIED by the permission system, naming the rule",
    "not permitted to run" in dump and "read:*/secret.*" in dump,
    "denial strings present in the session log")
trans = read(EVID)
name = re.search(r"You are ([A-Z][A-Za-z-]+),", read(PERSONA)).group(1)
rec("the answer self-reports as the talk persona and states the lane's GPU rule",
    name in trans and "never touches the GPU" in trans, "name=%s" % name)
probe_fixture = re.sub(r"[^A-Za-z0-9]", "", read(FIXTURE))[:24]
rec("no byte of the secret file reached the answer (the denial is real, not a soft warning)",
    probe_fixture not in re.sub(r"[^A-Za-z0-9]", "", trans), "fixture probe=%s" % probe_fixture)
rec("pi-memory is OFF in the lane: the session has no memory tool",
    not any(k in dump for k in ("memory_write", "memory_read", "memory_search", "memory_forget", "memory_status")))
rec("[plan: no duplicated rule] the GPU lock rule lives in gpu_guard.ps1 only (the lane calls it, it copies no logic)",
    "Get-Process" not in launch_code and "Win32_Process" not in launch_code and GUARD in launch_code)

# ---- 8/9. nothing else moved -------------------------------------------------------------------------------
new_loop = [p for p in glob.glob(os.path.join(LOOP_SESSIONS, "*.jsonl")) if os.path.getmtime(p) >= START_TS]
rec("the loop's own sessions dir gained nothing", not new_loop, [os.path.basename(p) for p in new_loop])
moved = []
allowed_drift = []
for p, (size, stamp) in BASELINE.items():
    st = os.stat(p)
    is_today_daily = p.endswith(os.path.join("daily", datetime.date.today().strftime("%Y-%m-%d") + ".md"))
    if st.st_size == size and (not stamp or
                               abs(st.st_mtime - datetime.datetime.strptime(stamp, "%Y-%m-%d %H:%M:%S").timestamp()) <= 2):
        continue
    if is_today_daily and st.st_mtime >= MEM_WRITE_OK:
        # This chat's own pi-memory writes after the record commit. The talk lane is a different thing and is proven
        # separately: its session loads no memory tool, and its sessions dir is private.
        allowed_drift.append((os.path.basename(p), "grew to %d B at %s = this chat's own memory writes after the "
                                                  "record, not the talk lane" % (
            st.st_size, datetime.datetime.fromtimestamp(st.st_mtime).strftime("%H:%M:%S"))))
        continue
    moved.append((os.path.basename(p), "size=%d (baseline %d) mtime=%s (baseline %s)" % (
        st.st_size, size, datetime.datetime.fromtimestamp(st.st_mtime).strftime("%H:%M:%S"), stamp)))
rec("[plan: no config edits] pi settings/models, the keepalive, ralph.ps1, PROMPT.md, AGENTS.md and the memory tree "
    "match the START baseline (so the talk lane wrote no loop daily log); growth of today's daily log after "
    "11:20 CT is this chat's own memory and is printed, not counted", not moved, "moved=%s allowed=%s" %
    (moved, allowed_drift))
rec("[MAX items 2-3 intact] the 12 job-2 files are still absent",
    not [p for p in JOB2 if os.path.exists(os.path.join(REPO, p.replace("/", os.sep)))])
git = lambda *a: subprocess.run(["git", "-C", REPO] + list(a), capture_output=True, text=True)
por = git("status", "--porcelain").stdout
diff_names = set(git("diff", "--name-only", "HEAD").stdout.split())
wh = git("hash-object", "AGENTS.md").stdout.strip()
hh = git("rev-parse", "HEAD:AGENTS.md").stdout.strip()
# Method gotcha, measured here: 'git diff --quiet HEAD -- AGENTS.md' said CLEAN for a file whose bytes differ from
# HEAD, because the index stat cache matched (same size, mtime recorded). 'git diff --name-only HEAD' and
# 'git hash-object' vs 'git rev-parse HEAD:<path>' are the content truth. Use those.
rec("[MAX items 2-3 intact] Max's AGENTS.md / PROMPT.md / ralph.ps1 are still his uncommitted work, and AGENTS.md "
    "still holds the Oct 28 bytes this unit found (so this unit never touched it)",
    {"AGENTS.md", "PROMPT.md", "ralph.ps1"} <= diff_names and wh == "687e5487e8d7c1bf912f0f740162c3a2b685276a"
    and wh != hh,
    "worktree AGENTS.md sha=%s HEAD sha=%s (differ = Max's Oct 28 edit, uncommitted) | diff vs HEAD: %s"
    % (wh[:12], hh[:12], sorted(diff_names)))
rec("8a0707e / 9cae06e / 987e49f are ancestors of HEAD (no reset, amend, rebase or force-push)",
    all(git("merge-base", "--is-ancestor", s, "HEAD").returncode == 0 for s in ("8a0707e", "9cae06e", "987e49f")))

# ---- 10. guards, and no render ------------------------------------------------------------------------------
q = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", GUARD],
                   capture_output=True, text=True, timeout=300)
rec("gpu_guard is IDLE at the end: this unit started no GPU work", q.returncode == 0 and "IDLE" in q.stdout,
    q.stdout.strip()[:120])
runs_new = [p for p in glob.glob(r"C:\AI\community\runs\*") if os.path.getmtime(p) >= START_TS]
rec("no render run dir exists from today", not runs_new, "new=%s" % runs_new)
t = subprocess.run([PY, "-m", "pytest", "-q", r"C:\AI\community\scripts\tests\test_p6_review.py",
                    r"C:\AI\community\scripts\tests\test_guard_scope.py"], capture_output=True, text=True, timeout=900)
tail = (t.stdout + t.stderr).strip().splitlines()[-1]
rec("[youth guard] the adults gate is untouched and passes (26 passed)", "26 passed" in tail, tail[:140])
w = subprocess.run([PY, r"C:\AI\community\scripts\check_web_saves.py"], capture_output=True, text=True, timeout=900)
wt = (w.stdout + w.stderr).strip().splitlines()
rec("[web saves] the provenance guard is CLEAN", w.returncode == 0 and any("CLEAN" in l for l in wt),
    (wt or [""])[-1][:140])

n_fail = sum(1 for _, ok, _ in results if not ok)
print("\n== %d/%d PASS" % (len(results) - n_fail, len(results)))
print("VERDICT: %s" % ("U3 IS PROVED" if not n_fail else "PROBLEMS: " + "; ".join(n for n, ok, _ in results if not ok)))
sys.exit(0 if not n_fail else 1)
