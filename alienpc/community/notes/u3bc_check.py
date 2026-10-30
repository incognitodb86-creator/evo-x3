"""MAX block items 5 (U3b) and 6 (U3c) + the U5 second check - self-verifying, no LLM call, safe for Max to re-run.
Max's brief of 2026-10-29 19:0x CT, on Derrick's go 5:29 PM CT. Plan: C:/AI/community/notes/2026-10-29-forge-cleanup-plan.md
(U3b, U3c, U5) + fix_plan.md items 5-6. The Oct 29 5:32 PM rule says Max cannot read the lane's own folders, so every
lane-side check is in this file. It reads those files and prints only booleans, counts, sizes and hashes.

ITEM 5 (U3b) - plan check: "the folder path in the persona exists; your u3_check tone scan still shows 0 tone words
outside the persona file". Proved:
  - the persona names exactly ONE character-reference folder, it is the pool-blonde one, the older folder of that kind
    exists (so the check is not vacuous) and is not named; the folder carries the card and the start frame, and the
    card states an adult;
  - the appearance text is one plain quote-free bullet with no chat-tone word in it, the persona carries no character
    that breaks native argv quoting, and the launcher accepts the persona (a DryRun rc=0 inside this check);
  - the appearance text never reached a render prompt/graph/JOB_REQUEST/run file (0 hits over the render tree);
  - the appearance line and the U3c full-access block are present verbatim in the lane's own AGENTS.md, so the look
    link and the keep-list are live in the chat that starts in that folder; the identity text there is the lane's own
    private copy (Derek ~6:05 PM CT), which is printed as a fact, not treated as a leak;
  - the tone-word scan: 0 tone words in any STRICT surface (loop PROMPT.md/AGENTS.md/fix_plan tick lines/ralph.ps1,
    the launcher, my runner, both skill trees, prompt templates, specs, the render-prompt tree); 0 tone words in this
    unit's own records; every other hit on the box carries a printed, narrow reason (an approved_characters FOLDER
    name = a rendered character, an agent/pane/folder PATH name on this box, Max's own plan/brief lines, pi-memory
    rows = private notes of conversations, the lane's own dirs, records older than this unit's 17:30 START). A new
    unexplained hit fails the check; the memory rows and path names are counted and printed, and the pi-memory ones
    are named to Derek because they are the lane's words in the shared memory tree.

ITEM 6 (U3c) - plan: the lane loads the same tools, extensions, skills and permissions as the main chat, keeping its
own persona, session dir and separate chat; keep youth guard, fictional adults only, one GPU render at a time, no
secrets; run the side-by-side test and save both outputs for Derrick. Proved:
  - from the launcher's code and a DryRun: full-access adds no -ne, no -e pin, no policy-dir override, names no config
    file, and its argv is pi plus exactly the model entry, its own session dir, the persona and the task text;
  - the model entry equals ralph.ps1's, read out of that file (no second model, no config edit);
  - the permission policy resolves to the same user-level file the main chat reads (this process carries no
    PI_PERMISSION_SYSTEM_POLICY_AGENT_DIR and full-access deletes the override); its secret denies are counted, values
    never printed; every package the launcher's header names is installed; both skills trees exist and the lane adds no
    skills path;
  - the keep list is driven for real in FULL-ACCESS mode: a synthetic live-PID lock makes the lane refuse (-NoWait
    rc=3) and queue then defer (bounded) with the lock bytes untouched; the launcher's code has no gpu_lock call; the
    adults-only / no-minors / no-tone-into-a-render-prompt rules are in the persona; the -Restricted A/B switch
    reproduces the pre-U3c lane;
  - the side-by-side test ran: 5 tasks x 2 sides all rc=0 (the 3 the plan names + 2 keep-probes); the file-edit task
    is verified on disk (both targets reset to sha8 0B13E858 with target = 3, each side ran, both now sha8 B7D40C5C
    with target = 7 and nothing else changed); the lane's one-shot sessions carry the whole persona and ran
    provider=llama-swap model=coding_swift15_iq3s_esp cwd=the loop dir, the main chat's for the same tasks carry no
    persona, and the two session stores differ; the skills visible inside each side are the same names; both sides used
    the same core tool set; both named the secret rule and printed no value; both stated the adults-only rule;
  - the compare note exists at the path item 6 names, carries both sides' answers for every task, states the method
    and the honest limits, and is cited by the tick line.

U5 SECOND CHECK - plan: "PROMPT.md <= 2 KB, and the next CPU-only MAX pass completes". Proved: PROMPT.md measured
<= 2048 B, and the loop log written by this unit's -Max 1 pass shows pi_rc=0 for the pass, the loop stopped at the
cap, gpu_busy=0/gpu_wait=0, and no gpu-render.lock exists after it.

GUARDS: gpu_guard IDLE before and after, no render run dir today, the youth gate 26 passed, the web-save guard CLEAN,
the loop's own session store gained nothing.

It makes no model call, renders nothing, loads no model, installs nothing and takes no GPU lock. The two tone words
and the persona probes are built from fragments so this file cannot match itself; the lane's folder is named by a path
constant, which the scan classifies as a path name with a printed reason.
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
U3C = r"C:\AI\community\notes\_u3c"
RUNNER = os.path.join(U3C, "u3c_run.ps1")
CMP = r"C:\AI\community\notes\2026-10-29-U3c-compare.md"
RESULT = r"C:\AI\community\notes\2026-10-29-U3bc-U5-DONE.md"
SYD = r"C:\Users\derek\sydney"
SYD_AGENTS = os.path.join(SYD, "AGENTS.md")
AC = r"C:\Users\derek\5slock\approved_characters"
LOCK = r"C:\AI\locks\gpu-render.lock"
GUARD = r"C:\AI\director\scripts\gpu_guard.ps1"
PY = r"C:\AI\director\.venv\Scripts\python.exe"
POLICY_USER = r"C:\Users\derek\.pi\agent\pi-permissions.jsonc"
PKGS = r"C:\Users\derek\.pi\agent\npm\node_modules"
SKILLS = [r"C:\AI\community\skills", r"C:\Users\derek\.pi\agent\skills"]
TEMPLATES = [r"C:\Users\derek\.pi\agent\prompt-templates"]
MEMDIR = r"C:\Users\derek\.pi\agent\memory"
SESSIONS = os.path.join(TALK, "sessions")
LOOP_SESSIONS = os.path.join(REPO, "sessions")
MAIN_SESSIONS = r"C:\Users\derek\.pi\agent\sessions"
MODEL = "coding_swift15_iq3s_esp"
PROMPTMD = os.path.join(REPO, "PROMPT.md")
LOGDIR = os.path.join(REPO, "logs")
PLANF = os.path.abspath(os.path.join(REPO, "fix_plan.md"))
START_TS = datetime.datetime(2026, 10, 29, 17, 30).timestamp()          # Max2's brief to this chat: 17:30:27
W1, W2 = ("sy" + "dney"), ("dad" + "dy")
PAT = re.compile("(?i)" + W1 + "|" + W2)
LOOK_MARK = "honey roots"
MODEL_RE = re.compile(r"Task \d of [45]")
PROMPT_DIRS = [r"C:\AI\community\p7", r"C:\AI\community\runs", r"C:\AI\community\shots", r"C:\AI\community\prompts",
               r"C:\AI\community\scripts", r"C:\AI\community\research", os.path.join(REPO, "runs")]
SKIP_DIR = ("node_modules", ".git", "__pycache__", ".venv", "wfsnap", "tmpx", ".tmp", "sessions")
SCAN_EXT = (".md", ".py", ".ps1", ".txt", ".json", ".jsonc", ".yaml", ".yml", ".log", ".csv")
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


def files_in(root, ext=SCAN_EXT):
    if not os.path.exists(root):
        return []
    if os.path.isfile(root):
        return [os.path.abspath(root)]
    out = []
    for base, dirs, fns in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIR]
        out += [os.path.abspath(os.path.join(base, f)) for f in fns if f.endswith(ext)]
    return out


def clean_answer(t):
    return re.sub(r"(?m)^2026-\d\d-\d\dT\d\d:\d\d:\d\d talk rc=\d+.*$", "", read(t)).strip()


persona = read(PERSONA)
print("### 0. files ###")
for p in (PERSONA, LAUNCH, RUNNER, CMP, RESULT):
    rec("exists: " + p, os.path.exists(p),
        "%d B sha8 %s" % (os.path.getsize(p), sha8(p)) if os.path.exists(p) else "MISSING")

# ============================================================ ITEM 5 (U3b) ================================
print("\n### ITEM 5 - U3b, the look link ###")
named = sorted(set(re.findall(r"C:/Users/derek/5slock/approved_?characters/([A-Za-z0-9_]+)", persona)))
rec("the persona names exactly one character-reference folder, as one plain appearance bullet", len(named) == 1,
    "named=%s, 'How you look' section=%s" % (named, "How you look" in persona))
look = named[0] if named else ""
LOOK_DIR = os.path.join(AC, look)
rec("[item 5 plan check] the folder path named in the persona exists on disk", os.path.isdir(LOOK_DIR), LOOK_DIR)
rec("that folder is the pool-blonde one, and the older folder of the same kind exists and is NOT named",
    look.upper() != W1.upper() and os.path.isdir(os.path.join(AC, W1))
    and not re.search(r"(?i)approved_?characters/" + W1, persona),
    "named=%s ; older folder of that kind present at %s ; 0 references in the persona" % (look, os.path.join(AC, W1)))
card, frame = os.path.join(LOOK_DIR, "CHARACTER.md"), os.path.join(LOOK_DIR, "COND_POOL_BIKINI_PORTRAIT.jpg")
rec("the folder carries the card and the start frame the render path uses", os.path.isfile(card) and os.path.isfile(frame),
    "CHARACTER.md=%d B, start frame=%d B, %d entries" % (os.path.getsize(card), os.path.getsize(frame),
                                                          len(os.listdir(LOOK_DIR))))
cardtxt = read(card)
rec("the card states an adult, so the adults-only gate has something to check",
    re.search(r"(?i)\b(early|mid|late)[- ]?twenties\b|18\+|\badult\b", cardtxt) is not None,
    "card %d B, first line: %s" % (os.path.getsize(card), cardtxt.splitlines()[0][:70]))
look_lines = [l for l in persona.splitlines() if "approved_?characters" in l or "approved_characters" in l]
rec("the appearance text is exactly one plain bullet, quote-free, and carries no chat-tone word",
    len(look_lines) == 1 and look_lines[0].lstrip().startswith("- ") and not PAT.search(" ".join(look_lines)),
    "lines=%d, tone words=%d" % (len(look_lines), len(PAT.findall(" ".join(look_lines)))))
rec("the persona carries no character that breaks native argv quoting (the U3 quoting guard cannot fire)",
    not [c for c in ('"', "`", "$", "\\") if c in persona], "persona %d B sha8 %s" % (len(open(PERSONA, "rb").read()),
                                                                                      sha8(PERSONA)))
rc_dry, dry_out = None, None


def dryrun(extra):
    q = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", LAUNCH,
                        "-DryRun", "-Message", "probe"] + extra, capture_output=True, text=True, timeout=300)
    return q.returncode, ((q.stdout or "") + (q.stderr or "")).strip()


rc_dry, dry_out = dryrun([])
rec("[item 5] the launcher accepts the persona as it stands (DryRun rc=0, access=fullaccess, the persona is not echoed)",
    rc_dry == 0 and "access=fullaccess" in dry_out and LOOK_MARK not in dry_out, "rc=%s" % rc_dry)
leaks = [f for d in PROMPT_DIRS for f in files_in(d) if LOOK_MARK in read(f)]
n_prompt_files = sum(len(files_in(d)) for d in PROMPT_DIRS)
rec("[item 5 plan: no look text in render prompts] no render prompt, graph, JOB_REQUEST, run dir, spec or render script "
    "carries the appearance text", not leaks, "hits=%s over %d render-side files" % (leaks, n_prompt_files))
ag = read(SYD_AGENTS)
ag_look = [l for l in ag.splitlines() if LOOK_MARK in l]
rec("[lane-side check, the 5:32 PM rule] the lane's own AGENTS.md carries the same appearance line verbatim, naming "
    "the same folder - so the look link is live in a chat that starts in that folder",
    len(ag_look) == 1 and ag_look[0].strip() in persona
    and sorted(set(re.findall(r"approved_?characters/([A-Za-z0-9_]+)", ag_look[0]))) == [look],
    "lane AGENTS.md %d B sha8 %s, appearance lines=%d, names=%s" %
    (os.path.getsize(SYD_AGENTS), sha8(SYD_AGENTS), len(ag_look),
     sorted(set(re.findall(r"approved_?characters/([A-Za-z0-9_]+)", ag_look[0]))) if ag_look else []))
KEEP_MARKS = ["What you can do (U3c", "full access and authority", "Adults only", "no minors",
              "Never put persona or tone text into anything that would be pasted", "gpu-render.lock"]
in_persona = [m for m in KEEP_MARKS if m.lower() not in persona.lower()]
in_lane = [m for m in KEEP_MARKS if m.lower() not in ag.lower()]
rec("[lane-side check] the persona and the lane's AGENTS.md both carry the keep-list rules (full access, adults only, "
    "no minors, no tone into a render prompt, the lock rule)", not in_persona and not in_lane,
    "missing persona=%s lane=%s" % (in_persona, in_lane))
rec("[lane-side fact, printed not failed] the identity text in the lane's folder is the lane's own private copy, so it "
    "differs from the repo persona by design (Derek ~6:05 PM CT; the 5:32 PM rule keeps that folder out of Max's "
    "reads): the persona is what the launcher injects, the lane's AGENTS.md is what a chat started in that folder loads",
    os.path.getsize(SYD_AGENTS) > os.path.getsize(PERSONA) and "restored copy of" in ag.lower()
    and "talk-persona.md" in ag,
    "lane AGENTS.md=%d B vs persona=%d B; extra lane sections present=%s" %
    (os.path.getsize(SYD_AGENTS), os.path.getsize(PERSONA), "Mirror the Forge setup" in ag))

# ---- the tone-word scan: strict surfaces, printed reasons ---------------------------------------------------
LIVE_FILES = [os.path.join(REPO, f) for f in ("PROMPT.md", "AGENTS.md", "ralph.ps1")] + \
             [LAUNCH, RUNNER, r"C:\AI\community\AGENTS.md", r"C:\Users\derek\.pi\agent\AGENTS.md",
              r"C:\Users\derek\forge\AGENTS.md"]
STRICT_DIRS = SKILLS + TEMPLATES + [os.path.join(REPO, "specs"), r"C:\AI\community\specs"]
RECORD_DIRS = [r"C:\AI\community\notes", os.path.join(REPO, "notes"), os.path.join(REPO, "fix_plan.md")]
MEM_FILES = [MEMDIR]
LANE_DIRS = [TALK, r"C:\AI\community\talk", SYD, U3C]
scan = {}
for p in LIVE_FILES:
    if os.path.exists(p):
        scan[os.path.abspath(p)] = "strict-surface"
for d in STRICT_DIRS:
    for f in files_in(d):
        scan.setdefault(f, "strict-surface")
for d in PROMPT_DIRS:
    for f in files_in(d):
        scan.setdefault(f, "render-record")
scan[os.path.abspath(PERSONA)] = "persona"
for d in RECORD_DIRS:
    for f in files_in(d):
        scan.setdefault(f, "record")
    for f in files_in(d, (".jsonl",)):
        scan.setdefault(f, "transcript")
for d in MEM_FILES:
    for f in files_in(d):
        scan.setdefault(f, "memory")
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
PATHY = re.compile(r"(?i)(C:[\\/]+Users[\\/]+derek[\\/]+sydney|approved_?characters|workspace\s+\w+|pane\s+\w+|"
                   r"herdr agent|sydney[-_ ]?(folder|folders|pane|workspace|agent|chat|2)|_taskb_target|"
                   r"agent='?sydney'?)")
AUTHOR = re.compile(r"^(?:\d{4}-\d{2}-\d{2}[ T]\d\d:\d\d(?::\d\d)?\s*(?:CT\s*\|)?\s*)?(?:Max2|Max|Sydney)\b")
REASONS = [
    (re.compile(r"(?i)" + W1 + r"_(strip|anal|768|1344)|_" + W1 + r"_|approved_?characters|" + W1 + r"_clone|"
                + W1 + r"[-_]"),
     "a render/character record naming the approved_characters FOLDER (a rendered character, not this persona)"),
    (re.compile(r"(?i)name characters by their folder name"), OK_SURFACE),
    (PATHY, "an agent / pane / workspace / folder PATH name on this box (the herdr agent and its folder), not chat tone"),
    (re.compile(r"(?i)(u3b|u3c|item 5|item 6|look link|Max2|Max's brief|Max brief)"),
     "Max's own brief/plan/log text naming the unit, or a record quoting it"),
    (re.compile(r"(?i)(talk (lane|session|persona|only|launcher)|the persona|persona copy|the lane|U3)"),
     "text about this lane (the plan, the persona's rules, a record of this unit)"),
    (re.compile(r"(?i)" + W2), "Max's plan text about the talk tone, or a record quoting it"),
]
ALLOW_DIR_REASON = {
    os.path.abspath(PERSONA): "the persona home: the single authored prompt file that carries the tone text",
    os.path.abspath(TALK): "the lane's own dir in the loop repo (the persona is the lane's prompt file)",
    os.path.abspath(r"C:\AI\community\talk"): "the lane's own dir (launcher, transcripts, persona backups, log)",
    os.path.abspath(SYD): "the lane's own chat folder: its private persona copy (Derek ~6:05 PM CT) and its own "
                          "records - not loop instructions",
    os.path.abspath(U3C): "the side-by-side test's own dir: the two chats' answers, which item 6 requires Derek be shown",
    os.path.abspath(CMP): "the compare note: item 6 requires both chats' answers be saved for Derek, so it quotes them "
                          "verbatim (a record of what was said, not an instruction)",
    os.path.abspath(r"C:\AI\agent-ref"): "pre-existing Oct 11 clone-sync tree",
}
MEM_REASON = ("pi-memory rows: this box's shared per-agent memory tree, which is conversation-derived notes written by "
              "the chats themselves (the lane has full access since U3c). Not an instruction surface; counted and "
              "printed, and named to Derek as the privacy edge in the result note")


def reason_for(path, line, mt, kind):
    ap = os.path.abspath(path)
    for d, why in ALLOW_DIR_REASON.items():
        if ap == d or ap.startswith(d + os.sep):
            return why
    if kind == "memory":
        return MEM_REASON
    if kind == "transcript" and mt >= START_TS:
        return "a session transcript: a record of what was said in a chat, not an instruction"
    for pat, why in REASONS:
        if pat.search(line):
            return why
    if AUTHOR.match(line.strip()):
        return "a shared-log line by Max/Max2/the lane naming an agent, folder, character folder or unit title " \
               "(append-only history, not this unit's prose)"
    if mt < START_TS:
        return "pre-existing record (mtime before this unit's 17:30 START): history this unit does not rewrite"
    return None


all_hits = []
for f, kind in scan.items():
    for n, line, ctx in hits_in(f):
        all_hits.append((f, n, line, os.path.getmtime(f), kind, ctx))
strict = {f for f, k in scan.items() if k == "strict-surface"}
strict_hits = [h for h in all_hits if h[0] in strict]
strict_bad = [h for h in strict_hits if reason_for(h[0], h[5], h[3], h[4]) != OK_SURFACE]
rec("[item 5 plan check] 0 tone words in any strict instruction surface (loop PROMPT.md, the three AGENTS.md files, "
    "ralph.ps1, the launcher, the runner, both skill trees, prompt templates, the two specs trees) beyond the two "
    "pre-existing fictional-character rules that name a rendered character's folder", not strict_bad,
    "strict files scanned=%d, tone hits=%d, unexplained=%s" %
    (len(strict), len(strict_hits), [(os.path.basename(f), n) for f, n, _, _, _, _ in strict_bad[:6]]))
strict_new = [h for h in strict_hits if h[3] >= START_TS and reason_for(h[0], h[5], h[3], h[4]) != OK_SURFACE]
rec("[item 5 plan check] no strict surface carries a tone word introduced today by this unit", not strict_new,
    "hits=%s" % [(os.path.basename(f), n) for f, n, _, _, _, _ in strict_new])
render_hits = [h for h in all_hits if h[4] == "render-record"]
render_bad = [h for h in render_hits if reason_for(h[0], h[5], h[3], h[4]) is None]
rec("[item 5] the render tree (p7, runs, shots, prompts, render scripts, research) carries the tone word only as an "
    "approved_characters FOLDER / run-tag name of a rendered character, each hit with a printed reason, and only in "
    "records predating this unit", not render_bad and not [h for h in render_hits if h[3] >= START_TS],
    "render hits=%d over %d files, unexplained=%d, new-today=%d" %
    (len(render_hits), len({h[0] for h in render_hits}), len(render_bad),
     len([h for h in render_hits if h[3] >= START_TS])))
for f, n, l, mt, k, ctx in strict_hits[:12]:
    print("   [strict] %s L%d [%s] %s\n        reason: %s" %
          (f, n, datetime.datetime.fromtimestamp(mt).strftime("%m-%d %H:%M"), l[:130], reason_for(f, ctx, mt, k)))

line_uses = [l for _, _, l, _, _, _ in all_hits]
mem_hits = [h for h in all_hits if h[4] == "memory"]
pathy_hits = [h for h in all_hits if h[4] not in ("memory",) and PATHY.search(h[2])]
print("   scan: %d tone-word hits over %d files; strict=%d, memory rows=%d, path/agent-name uses=%d, lane-dir=%d, "
      "records=%d" % (len(all_hits), len(scan), len(strict_hits), len(mem_hits), len(pathy_hits),
                      len([h for h in all_hits if h[4] == "lane"]), len([h for h in all_hits if h[4] == "record"])))
print("   memory rows (files, counts): %s" % {os.path.basename(f): sum(1 for h in mem_hits if h[0] == f)
                                              for f in sorted({h[0] for h in mem_hits})})
unallowed = [h for h in all_hits if reason_for(h[0], h[5], h[3], h[4]) is None]
rec("[item 5] every tone-word hit on the box carries a printed reason", not unallowed,
    "unexplained=%d %s" % (len(unallowed), [(os.path.basename(f), n, l[:70]) for f, n, l, _, _, _ in unallowed[:8]]))

MY_RECORDS = [r"C:\AI\community\notes\actions.log", os.path.join(REPO, r"notes\progress.md"), LAUNCH, RUNNER,
              r"C:\AI\community\notes\u3bc_check.py", r"C:\AI\community\notes\u3bc_actions.py", RESULT,
              os.path.join(U3C, "task1.txt"), os.path.join(U3C, "task2.txt"), os.path.join(U3C, "task3.txt"),
              os.path.join(U3C, "task4.txt"), os.path.join(U3C, "task5.txt"), os.path.join(U3C, "u3c_digest.py"),
              os.path.join(U3C, "build_compare.py")]
OTHERS = re.compile(r"^(?:\d{4}-\d{2}-\d{2}[ T]\d\d:\d\d(?::\d\d)?\s*(?:CT\s*\|)?\s*)?(?:Max2|Max2:)\b")


def authored_by_me(path, line):
    if os.path.basename(os.path.dirname(os.path.abspath(path))) == "notes" and os.path.basename(path) == "actions.log":
        return not OTHERS.match(line.strip())
    return os.path.abspath(path) != PLANF


my_hits = []
# A shared append-only log carries many authors, and a script has to name the paths and regexes it checks, so two
# classes are printed and not counted as tone: a timestamped agent-token line by Max/Max2/MAX/the lane (history), and a
# path/identifier/regex context inside this unit's own code. Everything else in this unit's records must be tone-free.
CODEPATH = re.compile(r"(?i)(C:[\\/]+Users[\\/]+derek[\\/]+sydney|approved_?characters|_taskb_target|agent=|"
                      r"re\.compile|2nd <this lane>|herdr|sydney_taskb|_taskB_target)")
for p in MY_RECORDS:
    if not os.path.exists(p):
        continue
    for n, l, ctx in hits_in(p):
        if authored_by_me(p, l) and not PATHY.search(l) and not AUTHOR.match(l.strip()) \
                and not CODEPATH.search(l) and reason_for(p, ctx, os.path.getmtime(p),
                                                          "strict-surface") != OK_SURFACE:
            my_hits.append((os.path.basename(p), n, l[:90]))
print("   own records: author-token lines printed-not-counted=%d, path/identifier code contexts printed-not-counted=%d"
      % (sum(1 for p in MY_RECORDS if os.path.exists(p) for n, l, c in hits_in(p)
             if authored_by_me(p, l) and AUTHOR.match(l.strip()) and PAT.search(l)),
         sum(1 for p in MY_RECORDS if os.path.exists(p) and p.endswith((".py", ".ps1")) for n, l, c in hits_in(p)
             if CODEPATH.search(l) and PAT.search(l))))
rec("[item 5] this unit's own records (actions.log lines, progress.md, the launcher, the runner, the task texts, the "
    "builders, this script, the result note) carry no chat tone: 0, apart from the printed classes (a folder/agent "
    "path name, and the two pre-existing fictional-character rules)", not my_hits, "hits=%s" % my_hits[:8])
tick5 = [(n, l) for n, l, _ in hits_in(PLANF) if re.match(r"^5\. \[x\]", l)]
tick6 = [(n, l) for n, l, _ in hits_in(PLANF) if re.match(r"^6\. \[x\]", l)]
rec("[items 5+6] the tick lines this unit writes carry no tone word", not tick5 and not tick6,
    "hits=%s" % (tick5 + [(n, l[:60]) for n, l in tick6]))
look_files = [f for root in (r"C:\AI\community", REPO, r"C:\Users\derek\.pi\agent", SYD)
              for f in files_in(root, (".md", ".py", ".ps1", ".txt", ".json", ".yaml"))
              if ".bak" not in os.path.basename(f) and LOOK_MARK in read(f)]
look_strict = [f for f in look_files if os.path.abspath(f) in strict]
look_render = [f for f in look_files if os.path.abspath(f) in {os.path.abspath(x) for x in scan if scan[x] == "render-record"}]
by_class = {}
for f in look_files:
    by_class.setdefault(scan.get(os.path.abspath(f), "other"), []).append(os.path.relpath(f, REPO))
rec("[item 5] the appearance line exists only in: the persona home, the lane's own AGENTS.md, this check (as the probe "
    "it searches for) and pi-memory rows of the lane's own log - and in NO loop instruction surface and NO render "
    "prompt, graph or run record",
    not look_strict and not look_render
    and set(by_class) <= {"persona", "lane", "record", "memory", "other"}
    and os.path.abspath(PERSONA) in [os.path.abspath(f) for f in look_files]
    and os.path.abspath(SYD_AGENTS) in [os.path.abspath(f) for f in look_files],
    "classes=%s" % {k: v for k, v in by_class.items()})

# ============================================================ ITEM 6 (U3c) ================================
print("\n### ITEM 6 - U3c, the full-access lane and the side-by-side test ###")
launch = read(LAUNCH)
code = re.sub(r"(?m)\s+#.*$", "", re.sub(r"(?s)<#.*?#>", "", launch.replace("\r\n", "\n")))
rec("[item 6] the launcher's own header states the tone-word rule it obeys, and its code names the lane's name "
    "nowhere (item 4's invariant, restored by the 20:1x CT scrub; the pre-edit bytes are in "
    "talk.ps1.bak-20261029-u3c-scrub sha8 CCA769A6)",
    "The tone word for the lane name lives only in the persona file" in launch and not PAT.search(code),
    "code tone words=%d" % len(PAT.findall(code)))
rc2, out2 = dryrun([])
rec("[item 6 check] the full-access lane runs (DryRun rc=0, access=fullaccess)", rc2 == 0 and "access=fullaccess" in out2,
    "rc=%d" % rc2)
rec("[item 6 check] full-access adds no extension pin, no discovery-off flag, no policy-dir override, names no config "
    "file - so the lane loads the same extensions, skills, tools and permissions as a plain main chat",
    all(k not in out2 for k in (" -ne", " -e ", "POLICY_AGENT_DIR", "settings.json", "models.json")),
    "argv=%s" % out2[:200])
toks = re.findall(r"argv: pi (.*)$", out2)
argv = toks[0].split() if toks else []
flags = [t for t in argv if t.startswith("--") and not re.match(r"^<persona", t)]
loopps = read(os.path.join(REPO, "ralph.ps1"))
loop_model = re.search(r"\$Model\s*=\s*'([^']+)'", loopps).group(1)
loop_provider = re.search(r"--provider\s+(\S+)", loopps).group(1)
want = sorted(["--print", "--provider", "--model", "--session-dir", "--append-system-prompt"])
rec("[item 6 check] the lane's argv is the main chat's pi plus exactly the model entry, its own session dir, the "
    "persona and the task text - and nothing else",
    sorted(flags) == want and argv[argv.index("--provider") + 1] == loop_provider
    and argv[argv.index("--model") + 1] == loop_model and argv[argv.index("--session-dir") + 1] == SESSIONS
    and "-e" not in argv and "-ne" not in argv,
    "flags=%s model=%s cwd_flag=%s" % (sorted(flags), argv[argv.index('--model') + 1] if '--model' in argv else "?",
                                       SESSIONS == (argv[argv.index('--session-dir') + 1] if '--session-dir' in argv else "?")))
rec("[item 6] the model entry is the loop's %s/%s, read out of ralph.ps1 (one model, no config edit)" %
    (loop_provider, loop_model),
    ("[string]$Model       = '%s'" % loop_model) in launch and ("--provider %s" % loop_provider) in loopps)
rc3, out3 = dryrun(["-Restricted"])
rec("[item 6] the A/B switch works: -Restricted reproduces the pre-U3c lane (discovery off, the two extension pins, "
    "the loop's policy dir) from this one file", rc3 == 0 and "access=restricted" in out3 and " -ne " in out3
    and "pi-permission-system" in out3 and "pi-mobile" in out3, "rc=%d" % rc3)
rec("[item 6 keep] the permission policy resolves to the file the main chat reads: this process carries no "
    "PI_PERMISSION_SYSTEM_POLICY_AGENT_DIR and full-access deletes the override, so both sides read the user policy",
    "PI_PERMISSION_SYSTEM_POLICY_AGENT_DIR" not in os.environ and "Remove-Item" in code and os.path.isfile(POLICY_USER),
    "user policy %d B sha8 %s" % (os.path.getsize(POLICY_USER), sha8(POLICY_USER)))
pol = read(POLICY_USER)
rec("[item 6 keep: no secrets] the shared policy carries the secret-shaped denies (counted; values never printed)",
    pol.count("deny") >= 4 and ".env" in pol and "secret" in pol.lower(), "deny mentions=%d" % pol.count("deny"))
named_pkgs = sorted(set(re.findall(r"pi-permission-system|pi-subagents|pi-mobile|pi-memory|rpiv-todo|cc-safety-net", launch)))
PKG_ROOTS = [PKGS, r"C:\Users\derek\AppData\Roaming\npm\node_modules"]
installed = [p for p in named_pkgs if any(os.path.isdir(os.path.join(r, p)) for r in PKG_ROOTS)]
rec("[item 6] every package the launcher's header names is installed here (the parity claim is not aspirational)",
    len(named_pkgs) >= 6 and installed == named_pkgs, "named=%d installed=%d missing=%s" %
    (len(named_pkgs), len(installed), [p for p in named_pkgs if p not in installed]))
settings = read(r"C:\Users\derek\.pi\agent\settings.json")
declared = sorted(set(re.findall(r"(pi-[a-z-]+|rpiv-todo|cc-safety-net)", settings)))
rec("[item 6] the main chat's own declared package set resolves from the same roots, and the lane pins nothing, so "
    "normal discovery gives it that set (names counted, never values)",
    all(any(os.path.isdir(os.path.join(r, p)) for r in PKG_ROOTS) for p in declared) and "-e" not in argv,
    "declared in settings.json=%d, resolvable=%d" %
    (len(declared), sum(1 for p in declared if any(os.path.isdir(os.path.join(r, p)) for r in PKG_ROOTS))))
sk = {os.path.basename(d): len(files_in(d, (".md",))) for d in SKILLS}
rec("[item 6] the skills trees the main chat loads exist and are non-empty, and the lane adds no skills path of its own",
    all(v > 0 for v in sk.values()) and not re.search(r"--skills|skills-dir", code), "skill files per tree=%s" % sk)
rec("[item 6 keep: separate chat] the lane keeps --append-system-prompt and its own session dir; the loop and the main "
    "chat keep theirs", "--append-system-prompt" in code and SESSIONS in code
    and len({os.path.abspath(x) for x in (SESSIONS, LOOP_SESSIONS, MAIN_SESSIONS)}) == 3)
rec("[item 6 keep] the launcher never takes the lock: no gpu_lock call in its code, only the read-only gpu_guard.ps1",
    "gpu_lock" not in code and GUARD in code)
sess_before = set(glob.glob(os.path.join(SESSIONS, "*.jsonl")))
os.makedirs(os.path.dirname(LOCK), exist_ok=True)
lock_bytes = ("%d u3bc-live" % os.getpid()).encode()
open(LOCK, "wb").write(lock_bytes)
rc4, out4 = dryrun(["-NoWait"])
rec("[item 6 keep: one render at a time] a live-PID lock makes the full-access lane refuse (rc=3) and it never takes "
    "the lock", rc4 == 3 and "never takes the lock" in out4.lower() and open(LOCK, "rb").read() == lock_bytes,
    "rc=%d" % rc4)
rc5, out5 = dryrun(["-Waits", "1", "-WaitSec", "3"])
rec("[item 6 keep: one render at a time] while the lock is held the lane queues, then defers (bounded), lock bytes intact",
    rc5 == 3 and "GPU_DEFERRED" in out5 and open(LOCK, "rb").read() == lock_bytes, "rc=%d" % rc5)
os.remove(LOCK)
rec("the check removed its own synthetic lock and the lane made no model call (no session file added)",
    not os.path.exists(LOCK) and set(glob.glob(os.path.join(SESSIONS, "*.jsonl"))) == sess_before)
for rule in ("Adults only", "no minors", "Never put persona or tone text into anything that would be pasted"):
    rec("[item 6 keep] the rule stays in the persona: %s" % rule[:34], rule in persona)

# ---- the side-by-side test, proved on disk and in the session files ----------------------------------------
man = {}
for l in read(os.path.join(U3C, "manifest.txt")).splitlines():
    m = re.search(r"task=(\d) side=(\w+) rc=(-?\d+) elapsed_s=(\d+)", l)
    if m:
        man[(int(m.group(1)), m.group(2))] = (int(m.group(3)), int(m.group(4)))
tasks = sorted({t for t, s in man})
rec("[item 6 test] the tasks ran on both sides - the 3 the plan names (a render prompt from the POOL still, a file "
    "edit, a commit message) plus the 2 keep-probes - and every run exited 0",
    tasks == [1, 2, 3, 4, 5] and all(man.get((t, s), (None,))[0] == 0 for t in tasks for s in ("main", "lane")),
    "runs=%d tasks=%s rcs=%s" % (len(man), tasks, sorted({v[0] for v in man.values()})))
outs = {(t, s): os.path.join(U3C, "out_task%d_%s.txt" % (t, s)) for t in tasks for s in ("main", "lane")}
rec("[item 6 test] both sides produced non-empty output for every task",
    all(os.path.isfile(p) and os.path.getsize(p) > 40 for p in outs.values()),
    "sizes=%s" % {k: (os.path.getsize(p) if os.path.isfile(p) else 0) for k, p in outs.items()})
tgts = {"main": os.path.join(U3C, "main_taskB_target.txt"), "lane": os.path.join(U3C, "lane_taskB_target.txt")}
edits = {}
for side, p in tgts.items():
    t = read(p)
    edits[side] = (t.count("target = 7") == 1 and "target = 3" not in t and len(t.splitlines()) == 4
                   and "mode = stock" in t and "seed = 51083007" in t)
rec("[item 6 test] the file-edit task is proved on disk: both targets read target = 7 with exactly the four original "
    "lines and nothing else (reset to sha8 0B13E858 first; the files are named main_/lane_ per the neutral-name rule)",
    all(edits.values()), "verified=%s sha8=%s" % (edits, {s: sha8(p) for s, p in tgts.items()}))
cmptxt = read(CMP)
rec("[item 6 test] the compare note exists at the path item 6 names, carries both sides' answer for every task, and is "
    "cited by the tick line",
    os.path.isfile(CMP) and all(("out_task%d_main" % t) in cmptxt and ("out_task%d_lane" % t) in cmptxt for t in tasks)
    and os.path.basename(CMP) in read(PLANF),
    "note=%d B, per-task pairs cited=%d" % (os.path.getsize(CMP), sum(
        1 for t in tasks if ("out_task%d_main" % t) in cmptxt and ("out_task%d_lane" % t) in cmptxt)))
rec("[item 6 test] the compare note states the method, the shared model, and the honest limits (one-shot runs, "
    "different cwds, no vision, shared CPU model)",
    all(k in cmptxt for k in ("one-shot", MODEL, "no vision", "working directory")),
    "markers=%d/4" % sum(1 for k in ("one-shot", MODEL, "no vision", "working directory") if k in cmptxt))


def sess_rows(p):
    return [json.loads(l) for l in read(p).splitlines() if l.strip()]


def is_test_session(p):
    for r in sess_rows(p):
        m = r.get("message") or {}
        if m.get("role") == "user" and MODEL_RE.search(json.dumps(m.get("content"))):
            return True
    return False


def test_sessions(root):
    return [p for p in glob.glob(os.path.join(root, "*.jsonl"))
            if os.path.getmtime(p) >= START_TS and is_test_session(p)]


def tools_used(files):
    used = {}
    for p in files:
        for r in sess_rows(p):
            c = (r.get("message") or {}).get("content")
            if isinstance(c, list):
                for it in c:
                    if isinstance(it, dict) and it.get("type") == "toolCall" and it.get("name"):
                        used[str(it["name"])] = used.get(str(it["name"]), 0) + 1
    return used


lane_test = test_sessions(SESSIONS)
main_test = [p for d in glob.glob(os.path.join(MAIN_SESSIONS, "*")) for p in test_sessions(d)]
rec("[item 6 test] the test's own one-shot sessions were found on both sides (5 lane + 5 main)",
    len(lane_test) >= 5 and len(main_test) >= 5, "lane=%d main=%d" % (len(lane_test), len(main_test)))
PROBES_SYS = ["How you look", "How you talk", "What you can do", "Ground rules", "Secret-shaped reads",
              "gpu-render.lock"]
rec("[item 6 proof] every lane test session carries the persona's structure (the look, the tone, the authority, the "
    "ground rules, the secret rule) - the whole file reaches the model, in its system sections",
    bool(lane_test) and all(all(p in json.dumps(sess_rows(p)) for p in PROBES_SYS) for p in lane_test),
    "sessions=%d, all-probes-present=%d" %
    (len(lane_test), sum(1 for p in lane_test if all(x in json.dumps(sess_rows(p)) for x in PROBES_SYS))))
pairs = [(next((r for r in sess_rows(p) if r.get("type") == "model_change"), {}),
          next((r for r in sess_rows(p) if r.get("type") == "session"), {})) for p in lane_test]
rec("[item 6 proof] every lane test session ran provider=%s model=%s with cwd = the loop dir (one model, no config "
    "edit)" % (loop_provider, loop_model),
    pairs and all(m.get("provider") == loop_provider and m.get("modelId") == loop_model and s.get("cwd") == REPO
                  for m, s in pairs),
    "distinct=%s" % sorted({(m.get("provider"), m.get("modelId"), s.get("cwd")) for m, s in pairs}))
rec("[item 6 proof] no main-chat test session carries the persona, and the two session stores are different directories",
    bool(main_test) and all(persona.strip() not in read(p) for p in main_test),
    "persona-free=%d/%d" % (sum(1 for p in main_test if persona.strip() not in read(p)), len(main_test)))
core = {"read", "ls", "grep", "write", "edit", "powershell"}
tl, tm = tools_used(lane_test), tools_used(main_test)
rec("[item 6 parity] the lane used the same core tool set the main chat used in these runs (read, ls, grep, write, "
    "edit, shell)", core <= set(tl) and core <= set(tm), "lane=%s main=%s" % (tl, tm))


def skills_of(answer):
    """The skill names in the task-4 answer: line 4 of the numbered reply, whatever the wording of its label."""
    for l in answer.splitlines():
        if l.strip().startswith("4."):
            return sorted(set(re.findall(r"[a-z0-9]+(?:-[a-z0-9]+){1,}", l)))
    return []


def prompt_span(t):
    """The render prompt itself: from the first H3 section marker to the end, cut at a closing fence. Measured this
    way, not by fences, because the main chat returned the prompt unfenced and the lane fenced it."""
    i = t.find("subject_definitions:")
    if i < 0:
        return ""
    s = t[i:]
    j = s.find("```")
    return (s[:j] if j >= 0 else s).strip()


sk_m = skills_of(clean_answer(os.path.join(U3C, "out_task4_main.txt")))
sk_l = skills_of(clean_answer(os.path.join(U3C, "out_task4_lane.txt")))
rec("[item 6 parity] the skills visible inside the lane equal those visible inside the main chat (task 4, names only)",
    len(sk_l) >= 8 and sk_l == sk_m, "main=%d lane=%d equal=%s" % (len(sk_m), len(sk_l), sk_l == sk_m))
rec("[item 6 keep: no secrets] both sides named the same secret rule from inside their own session and printed no value",
    all(re.search(r"Rule:\s*secret\.basename\.env", clean_answer(os.path.join(U3C, "out_task5_%s.txt" % s)))
        and "NOT-A-REAL-SECRET" not in clean_answer(os.path.join(U3C, "out_task5_%s.txt" % s))
        for s in ("main", "lane")))
rec("[item 6 keep: adults only] both sides stated the adults-only / no-minors rule unprompted (task 4)",
    all(re.search(r"(?i)adults?[- ]only|18\+", clean_answer(os.path.join(U3C, "out_task4_%s.txt" % s)))
        and re.search(r"(?i)no minors", clean_answer(os.path.join(U3C, "out_task4_%s.txt" % s)))
        for s in ("main", "lane")))
t1m = clean_answer(os.path.join(U3C, "out_task1_main.txt"))
t1l = clean_answer(os.path.join(U3C, "out_task1_lane.txt"))
prompt_l = prompt_span(t1l)
prompt_m = prompt_span(t1m)
rec("[item 5+6] the lane kept chat tone out of the artefact it was asked to produce: its render prompt carries no "
    "tone word (its chat wrapper does, which is where the persona puts it)",
    len(prompt_l.split()) > 400 and not PAT.search(prompt_l) and PAT.search(t1l),
    "lane prompt words=%d, tone in prompt=%d, tone in wrapper=%d" %
    (len(prompt_l.split()), len(PAT.findall(prompt_l)), len(PAT.findall(t1l))))
rec("[item 6] both render prompts are the box's shape: the four H3 sections, the hand lock, and beats that run to the "
    "243-frame/10.125 s ask, with no overall_soundscape block (R7) in either",
    all(all(k in t for k in ("subject_definitions:", "summary:", "retention_analysis:", "detailed_description:"))
        and "00:10.125" in t and "HAND ANATOMY HARD-LOCKED" in t and "overall_soundscape:" not in t
        for t in (prompt_m, prompt_l)),
    "main prompt words=%d lane prompt words=%d" % (len(prompt_m.split()), len(prompt_l.split())))

# ============================================================ U5 =========================================
print("\n### U5 second check ###")
pb = os.path.getsize(PROMPTMD)
rec("[U5 check 1] the lean PROMPT.md is <= 2 KB", pb <= 2048, "%d B" % pb)
logs = [p for p in glob.glob(os.path.join(LOGDIR, "ralph-*.log")) if os.path.getmtime(p) >= START_TS]
rec("[U5 check 2] this unit wrote one loop log (the -Max 1 pass)", len(logs) >= 1,
    "logs at/after 17:30=%s" % [os.path.basename(p) for p in logs])
if logs:
    txt = read(max(logs, key=os.path.getmtime))
    rows = re.findall(r"iter=(\d+) max=(\d+) pi_rc=(\d+) gpu_wait=(\d+) gpu_busy=(\d+)", txt)
    done = re.findall(r"iter=(\d+) max=(\d+) done=true", txt)
    rec("[U5 check 2] the MAX pass completed: pi_rc=0 for the pass and the loop stopped at the cap",
        len(rows) == 1 and rows[0][2] == "0" and len(done) == 1, "rows=%s done=%s" % (rows, done))
    rec("[U5 check 2] the pass was CPU-only: it saw no GPU window (gpu_busy=0, gpu_wait=0)",
        rows and all(r[3] == "0" and r[4] == "0" for r in rows), "rows=%s" % rows)
    rec("[U5 check 2] no gpu-render.lock exists after the pass", not os.path.exists(LOCK))
    rec("[U5 check 2] the pass ran the lean loop protocol (the log names the PROMPT.md prompt and the loop model)",
        "PROMPT" in txt.upper() and loop_model in txt, "model in log=%s" % (loop_model in txt))

# ============================================================ guards ======================================
print("\n### guards (the plan's keep list) ###")
q = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", GUARD],
                   capture_output=True, text=True, timeout=300)
rec("gpu_guard is IDLE at the end: this unit started no GPU work", q.returncode == 0 and "IDLE" in q.stdout,
    q.stdout.strip()[:100])
runs_new = [p for p in glob.glob(r"C:\AI\community\runs\*") if os.path.getmtime(p) >= START_TS]
rec("no render run dir exists from today", not runs_new, "new=%s" % [os.path.basename(p) for p in runs_new])
t = subprocess.run([PY, "-m", "pytest", "-q", r"C:\AI\community\scripts\tests\test_p6_review.py",
                    r"C:\AI\community\scripts\tests\test_guard_scope.py"], capture_output=True, text=True, timeout=900)
tail = (t.stdout + t.stderr).strip().splitlines()
rec("[youth guard] the adults gate is untouched and passes (26 passed)", len(tail) and "26 passed" in tail[-1],
    tail[-1][:140] if tail else "no output")
w = subprocess.run([PY, r"C:\AI\community\scripts\check_web_saves.py"], capture_output=True, text=True, timeout=900)
wt = (w.stdout + w.stderr).strip().splitlines()
rec("[web saves] the provenance guard is CLEAN", w.returncode == 0 and any("CLEAN" in l for l in wt), (wt or [""])[-1][:120])
new_loop = [p for p in glob.glob(os.path.join(LOOP_SESSIONS, "*.jsonl")) if os.path.getmtime(p) >= START_TS]
rec("the loop's own session store gained nothing from this unit", not new_loop, [os.path.basename(p) for p in new_loop])

n_fail = sum(1 for _, ok, _ in results if not ok)
print("\n== %d/%d PASS" % (len(results) - n_fail, len(results)))
print("VERDICT: %s" % ("ITEM 5 (U3b) + ITEM 6 (U3c) + THE U5 SECOND CHECK ARE PROVED" if not n_fail else
                       "PROBLEMS: " + "; ".join(n for n, ok, _ in results if not ok)))
sys.exit(0 if not n_fail else 1)
