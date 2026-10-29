"""MAX block item 4 (U3, talk lane) close-out record - ticks item 4 with evidence + commit SHAs, appends one DONE
line to C:/AI/community/notes/actions.log (append-only) and one line to ralph-community/notes/progress.md, then
verifies the plan file's shape (CRLF, one physical line per tick, line count unchanged, no new non-ASCII), that the
items 2-3 ticks are intact, and that the check's verdict is on record.

The tick cites the two artifact commits, which must exist before this runs: they are found by their message markers
so no SHA is typed by hand. Idempotent: it refuses to double-tick. Tone words are never written in this file.
"""
import datetime
import hashlib
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
REPO = r"C:\Users\derek\5slock\ralph-community"
PLAN = os.path.join(REPO, "fix_plan.md")
BAK = PLAN + ".bak-20261029-u3-tick"
LOG = r"C:\AI\community\notes\actions.log"
PROG = os.path.join(REPO, r"notes\progress.md")
CHECK_OUT = r"C:\AI\community\talk\u3_check_out.txt"
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M CT")
MARK_ARTIFACTS = "U3 talk lane (MAX item 4): the talk-only launcher"
MARK_PERSONA = "U3 talk lane (MAX item 4): the persona file"


def git(*a):
    q = subprocess.run(["git", "-C", REPO] + list(a), capture_output=True, text=True)
    return ((q.stdout or "") + (q.stderr or "")).strip()


def git_c(dirpath, *a):
    q = subprocess.run(["git", "-C", dirpath] + list(a), capture_output=True, text=True)
    return ((q.stdout or "") + (q.stderr or "")).strip()


def sha_of_marker(dirpath, marker):
    out = git_c(dirpath, "log", "--format=%H %s", "-20")
    for line in out.splitlines():
        if marker in line:
            return line.split()[0][:7]
    return None


SHA_LAUNCH = sha_of_marker(r"C:\AI\community", MARK_ARTIFACTS)
SHA_PERSONA = sha_of_marker(REPO, MARK_PERSONA)
assert SHA_LAUNCH and SHA_PERSONA, "the artifact commits must exist and be committed before the tick runs " \
                                   "(markers: %r / %r)" % (MARK_ARTIFACTS, MARK_PERSONA)
verdict = open(CHECK_OUT, encoding="utf-8", errors="replace").read()
assert "== 43/43 PASS" in verdict and "VERDICT: U3 IS PROVED" in verdict, "the check verdict is not on record"
PERSONA = os.path.join(REPO, r"talk\talk-persona.md")
psize, psha = os.path.getsize(PERSONA), hashlib.sha256(open(PERSONA, "rb").read()).hexdigest()[:8]

TICK = ('  4. [x] U3 talk lane DONE %s: commits %s (C:/AI/community: talk/talk.ps1 the talk-only launcher, '
        'notes/u3_check.py, notes/u3_start_record.py + probes, notes/2026-10-29-U3-talk-lane-DONE.md, the two real-turn '
        'transcripts, the check output and the persona backup) and %s (ralph-community: talk/talk-persona.md, %d B, '
        'sha8 %s, its pre-edit bytes in talk-persona.md.bak-20261029-u3a sha8 DE74EBE6). The launcher adds '
        '--append-system-prompt <that persona file>, its own --session-dir (ralph-community\\talk\\sessions, '
        'gitignored, proved by git check-ignore), and -ne -e pi-permission-system -e pi-mobile (extension identifiers '
        'taken from "pi list", not guessed), so pi-memory is OFF; it keeps ralph.ps1\'s provider/model entry, proved '
        'by the session file\'s own model_change row provider=llama-swap modelId=coding_swift15_iq3s_esp and cwd = the '
        'loop dir, and sets the loop\'s PI_PERMISSION_SYSTEM_POLICY_AGENT_DIR - no config file edited. The GPU rule '
        'calls C:/AI/director/scripts/gpu_guard.ps1 (one implementation, no copied lock logic, no gpu_lock call) and '
        'never takes the lock: driven with a synthetic live-PID lock, -NoWait returns rc=3, a bounded queue logs '
        'GPU_BUSY then GPU_DEFERRED, and the lock bytes stay intact. PLAN CHECK 1 (the tone-word scan) in '
        'u3_check.py over 2933 files = PROMPT.md, AGENTS.md x3, ralph.ps1, both launchers, both skill trees, prompt '
        'templates, the memory tree, specs/, both notes roots, the talk dirs: 0 tone words in any live instruction '
        'surface except one pre-existing line present in two of Derek\'s Oct 28 skills (the fictional-character rule '
        'naming a rendered character\'s FOLDER - a character name, not tone text, printed in the output as the only '
        'permitted surface hit); 0 in this unit\'s records, its tick line and its scripts; 0 new anywhere outside the '
        'persona, its own transcripts and the DONE note; every other hit carries a printed reason. The literal '
        '"0 over notes and memory" is unmeetable by U3 alone because the plan file, the item titles in this plan and '
        'the Oct 28 render records name the unit/character - the check states that and proves the strong form. '
        'PLAN CHECK 2: a real one-shot turn at 11:05:43 CT asked for notes/.forge11/secret.json and the session '
        'recorded "is not permitted to run \'read\' (matched \'read:*/secret.*\')" with no byte of the file in the '
        'answer, so permissions load with pi-memory off; the reply states the lane\'s identity and its lock rule, and '
        'the session\'s system sections carry the whole persona while its user rows carry only Derek\'s message. '
        'u3_check.py = 43/43 PASS exit 0 ("U3 IS PROVED"), full output at C:/AI/community/talk/u3_check_out.txt; it '
        'makes no model call so Max can re-run it. Two real defects were found and are now tested: '
        '--append-system-prompt does not expand @path, and a persona containing a double quote is word-split by '
        'PowerShell 5.1 native argv quoting (the persona is authored quote-free and the launcher refuses rc=4 on a '
        'persona that would break quoting; argv integrity proved through Python). pi settings.json/models.json, the '
        'keepalive, ralph.ps1, PROMPT.md, AGENTS.md and the whole memory tree match the START baseline '
        'byte-for-byte, so no config edit happened and the lane wrote no loop daily log; the loop\'s sessions dir '
        'gained nothing; items 2-3 are intact (the 12 job-2 files absent, 8a0707e/9cae06e/987e49f ancestors); the '
        'youth guard is 26 passed, check_web_saves CLEAN, gpu_guard IDLE before and after, no runs/ dir today; no '
        'GPU, no render, no model load, no queue, no install by this unit; Max\'s AGENTS.md/PROMPT.md/ralph.ps1 '
        'working-tree edits untouched. Left to Derek: the persona\'s strong-language dial is unset (so none, and ask '
        'once), and the persona name is shared with an approved_characters folder from Oct 28 render work. The plan\'s '
        'review files under 60_reviews/max are not on this box, so the plan text was the source. Record commit '
        'follows this line; script C:/AI/community/notes/u3_closeout_record.py') % (NOW, SHA_LAUNCH, SHA_PERSONA,
                                                                                   psize, psha)

DONE = ("%s | MAX item 4 (U3) DONE | the talk lane exists as two files: C:/AI/community/talk/talk.ps1 (the "
        "talk-only launcher, commit %s) and ralph-community\\talk\\talk-persona.md (the tone text, the only prompt "
        "file carrying it, commit %s). The launcher adds --append-system-prompt <persona>, its own --session-dir and "
        "-ne -e pi-permission-system -e pi-mobile (pi-memory OFF), keeps the loop's provider/model entry and cwd, "
        "sets the loop's secrets-policy env, and asks gpu_guard.ps1 before sending: it never takes "
        "C:\\AI\\locks\\gpu-render.lock, queues while a render holds it, and -NoWait refuses with rc=3. Plan check 1: "
        "notes/u3_check.py scanned 2933 files (PROMPT/AGENTS/launchers/skills/prompt-templates/memory/specs/notes/"
        "talk) - 0 tone words in any live instruction surface except the two pre-existing Oct 28 fictional-character "
        "rules that name a rendered character's folder, 0 in this unit's records and scripts, every other hit with a "
        "printed reason. Plan check 2: a real turn on notes/.forge11/secret.json was DENIED by "
        "'read:*/secret.*' with no byte leaked, so permissions load with pi-memory off, and the session's system "
        "sections carry the persona with one user row only. 43/43 PASS exit 0, output at C:/AI/community/talk/"
        "u3_check_out.txt. Fixed on the way, both now tested: --append-system-prompt does not expand @path; a "
        "persona with a double quote is word-split by PowerShell native argv quoting (persona authored quote-free, "
        "launcher refuses rc=4). No config edit, no loop daily-log write, no loop session, no render, no model load, "
        "no queue, no install; items 2-3 intact; youth guard 26 passed; gpu_guard IDLE. Unchecked dials for Derek: "
        "the persona's strong-language level (unset = none) and the shared folder/character name" % (NOW, SHA_LAUNCH,
                                                                                                    SHA_PERSONA))

PROG_LINE = ("- %s MAX block item 4 (U3, the talk lane) DONE. Two new files: C:/AI/community/talk/talk.ps1 "
             "(commit `%s`) starts pi on the loop's own entry (`--provider llama-swap --model coding_swift15_iq3s_esp`, "
             "the loop's cwd, so the same AGENTS.md context) and adds only the three talk-only things: "
             "`--append-system-prompt` the persona file, a private `--session-dir` under `ralph-community/talk/sessions` "
             "(gitignored), and `-ne -e pi-permission-system -e pi-mobile`, which is how pi-memory is switched off - "
             "proved by the session transcript having no memory tool and the memory tree staying byte-identical, so the "
             "lane writes no loop daily log. The GPU rule is one implementation: the launcher runs "
             "`C:/AI/director/scripts/gpu_guard.ps1`, never calls gpu_lock, and while a render holds the window it "
             "queues and defers (proved with a synthetic live-PID lock: rc=3, bounded queue, lock bytes intact). The "
             "persona lives in exactly one prompt file, `ralph-community/talk/talk-persona.md` (commit `%s`); the "
             "tone-word scan over 2,933 files (`C:/AI/community/notes/u3_check.py`) shows 0 tone words in any live "
             "instruction surface apart from two pre-existing Oct 28 fictional-character rules that name a rendered "
             "character's folder, and 0 in this unit's records; the secret-read check denied "
             "`notes/.forge11/secret.json` with `read:*/secret.*` and leaked nothing. Check = 43/43 PASS, exit 0, "
             "output at `C:/AI/community/talk/u3_check_out.txt`. Two defects were found and are now covered: "
             "`--append-system-prompt` does not expand `@path`, and a persona containing a double quote is word-split "
             "by PowerShell 5.1 native argument quoting (the persona is written quote-free and the launcher refuses "
             "rc=4). Nothing else moved: pi settings/models, the keepalive, ralph.ps1, PROMPT.md, AGENTS.md, the "
             "memory tree, the loop's sessions dir, MAX items 2-3, Max's working tree. Left for Derek: the "
             "strong-language dial is unset (default none) and the persona name collides with an approved_characters "
             "folder name. Stop after item 4 per the brief." % (NOW, SHA_LAUNCH, SHA_PERSONA))


def nonascii(path):
    return [l for l in open(path, "rb").read().decode("utf-8").split("\r\n") if not all(ord(c) < 128 for c in l)]


BASE = {p: len(nonascii(p)) for p in (LOG, PROG, PLAN)}

# --- tick -------------------------------------------------------------------------------------------------
raw = open(PLAN, "rb").read()
if not os.path.exists(BAK):
    open(BAK, "wb").write(raw)
    print("backup -> %s (%d B, sha8 %s)" % (BAK, len(raw), hashlib.sha256(raw).hexdigest()[:8]))
text = raw.decode("utf-8")
lines = text.split("\r\n")
assert text.count("\n") == len(lines) - 1, "expected pure CRLF"
idx = [i for i, l in enumerate(lines) if l.startswith("  4. [ ] ")]
done = [i for i, l in enumerate(lines) if l.startswith("  4. [x] ") and "U3 talk lane DONE" in l]
assert len(idx) + len(done) == 1, "item 4: expected exactly one line, got %r/%r" % (idx, done)
if idx:
    i = idx[0]
    assert "\n" not in TICK
    lines[i] = TICK
    print("ticked item 4 on one physical line (%d chars)" % len(TICK))
else:
    print("item 4 already ticked (idempotent): line %d" % (done[0] + 1))
assert len(lines) == len(text.split("\r\n")), "line count changed"
open(PLAN, "wb").write("\r\n".join(lines).encode("utf-8"))

# --- actions.log + progress.md ----------------------------------------------------------------------------
ltext = open(LOG, "rb").read().decode("utf-8")
if "MAX item 4 (U3) DONE" in ltext:
    print("actions.log: DONE already present (idempotent)")
else:
    d = ltext.encode("utf-8")
    if not d.endswith(b"\r\n"):
        d += b"\r\n"
    open(LOG, "wb").write(d + (DONE + "\r\n").encode("utf-8"))
    print("actions.log: DONE appended (append-only)")

ptext = open(PROG, "rb").read().decode("utf-8")
if "MAX block item 4 (U3, the talk lane) DONE" in ptext:
    print("progress.md: line already present (idempotent)")
else:
    d = ptext.encode("utf-8")
    if not d.endswith(b"\r\n"):
        d += b"\r\n"
    open(PROG, "wb").write(d + (PROG_LINE + "\r\n").encode("utf-8"))
    print("progress.md: appended 1 line")

# --- verify -----------------------------------------------------------------------------------------------
ok = True
t2 = open(PLAN, "rb").read().decode("utf-8")
l2 = t2.split("\r\n")
ticks = [l for l in l2 if re.match(r"^  [1234]\. \[x\] ", l)]
unticked = [l for l in l2 if re.match(r"^  \d+\. \[ \]", l)]
ok &= len(ticks) == 4 and all("\n" not in t for t in ticks)
ok &= len(l2) == len(text.split("\r\n"))
ok &= any(l.startswith("  2. [x] job-2 file removal DONE") for l in l2)
ok &= any(l.startswith("  3. [x] handoff-from-max.md section 4 FIXED DONE") for l in l2)
ok &= SHA_LAUNCH in t2 and SHA_PERSONA in t2
for s in (TICK, DONE, PROG_LINE):
    ok &= all(ord(c) < 128 for c in s)
for p in (LOG, PROG, PLAN):
    n = len(nonascii(p))
    print("%s: %d B, non-ASCII lines=%d (baseline %d)" % (os.path.basename(p), os.path.getsize(p), n, BASE[p]))
    ok &= n == BASE[p]
por = git("status", "--porcelain")
ok &= all((" M " + f) in por for f in ("AGENTS.md", "PROMPT.md", "ralph.ps1"))
print("Max's tree intact:", [l for l in por.splitlines() if l.startswith(" M")])
print("plan state: %d items ticked (1-4), %d unticked" % (len(ticks), len(unticked)))
print("VERDICT: %s" % ("ITEM 4 RECORDED AND TICKED" if ok else "PROBLEM"))
sys.exit(0 if ok else 1)
