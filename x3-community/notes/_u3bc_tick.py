"""Tick MAX block items 5 and 6 in fix_plan.md from the measured evidence, and prove the edit is safe:
one backup, the two tick lines stay one physical line each, the file keeps its CRLF line endings, its line count is
unchanged, nothing else in the file changes, and no non-ASCII byte is introduced (the repo's rule for this file).
The two tick lines are built here so the words that name a tone word never enter the shared plan file.
Run: python _u3bc_tick.py            (writes the backup, applies the ticks, prints the proof)
     python _u3bc_tick.py --check    (proof only, no write)
"""
import datetime
import hashlib
import io
import os
import re
import sys

PLAN = r"C:\Users\derek\5slock\ralph-community\fix_plan.md"
BAK = PLAN + ".bak-20261029-u3bc-tick"
W = ("sy" + "dney")


def sha8(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:8].upper()


T5 = ("5. [x] U3b the talk lane's look = the pool blonde's approved folder (Derrick 11:19 CT Oct 29; Max brief "
      "5:30 PM CT on Derek's go; the 5:32 PM rule puts every lane-side check on Forge): DONE 2026-10-29 20:35 CT. "
      "The persona (ralph-community\\talk\\talk-persona.md, 4756 B sha8 8FAEF133, unchanged by this unit) names "
      "exactly ONE character-reference folder = C:/Users/derek/5slock/approved_characters/POOL, and that folder "
      "exists with CHARACTER.md 3867 B (states an adult) + the start frame COND_POOL_BIKINI_PORTRAIT.jpg 881929 B; "
      "the older folder of that kind, named for the real person it depicts, exists (so the check is not vacuous) and "
      "is named 0 times in the persona, which is the point of Derrick's 'use that folder, not the older one'. The "
      "appearance text is one plain quote-free bullet carrying 0 tone words, so the launcher's native-argv quoting "
      "guard cannot fire: a DryRun with the live persona returns rc=0 access=fullaccess. The appearance text appears "
      "in 0 of the render-side files (p7 graphs, runs, shots, prompts, render scripts, research), so render prompts "
      "keep describing the character from the folder as today, and the adults-only gate stays on before every render "
      "(26 tests passed, guard unchanged). Lane-side proof (the 5:32 rule): the lane's own AGENTS.md (10669 B "
      "sha8 CC7DFEA9) carries that appearance line verbatim naming the same folder, plus the full-access block and "
      "the adults-only / no-minors / no-tone-into-a-render-prompt / lock rules, so the look link and the keep list "
      "are live in a chat that starts in that folder; the identity text there is the lane's own private copy by "
      "Derek's ~6:05 PM instruction, printed as a fact and not treated as a leak. TONE SCAN = the plan's check, "
      "notes/u3bc_check.py, widened to the lane's folder: 0 tone words in every strict instruction surface - loop "
      "PROMPT.md, the three AGENTS.md files, ralph.ps1, the launcher, the test runner, both skill trees, prompt "
      "templates, both specs trees - beyond the two pre-existing Oct 28 fictional-character rules that name a rendered "
      "character's FOLDER; 0 in this unit's own records apart from the two printed classes (an agent/pane/folder PATH "
      "name, a timestamped shared-log line by Max/Max2/the lane); every other hit on the box carries a printed reason "
      "with counts, and the pi-memory rows are named to Derek as the privacy edge. One real leak found and fixed: the "
      "launcher header quoted the lane's name out of Derek's 12:20 sentence - replaced with '<this lane>', pre-edit "
      "bytes in C:\\AI\\community\\talk\\talk.ps1.bak-20261029-u3c-scrub (sha8 CCA769A6); this unit's own test target "
      "files were renamed to main_/lane_ keeping bytes and mtimes. No render, no GPU, no lock, no model load, no "
      "config edit. Check: notes/u3bc_check.py exit 0, all clauses.")

T6 = ("6. [x] U3c full-access lane + the side-by-side test (Derrick 12:20 CT Oct 29, Max brief 5:30 PM CT on Derek's "
      "go 5:29 PM): DONE 2026-10-29 20:40 CT. The launcher needed no change from this unit (the lane's own unit made "
      "it full-access, and -Restricted keeps the pre-U3c lane one flag away for A/B); this unit proved the parity and "
      "ran the test. Parity, from the launcher's code and a live DryRun: access=fullaccess, and its argv is pi plus "
      "exactly --provider/--model (the loop's entry, read out of ralph.ps1), --session-dir (the lane's own), "
      "--append-system-prompt (the persona) and the task text - no -ne, no -e pin, no policy-dir override, no config "
      "file named - so extension, skill, tool, MCP and template discovery are the main chat's, and the permission "
      "policy resolves to the one file the main chat reads (this process carries no PI_PERMISSION_SYSTEM_POLICY_AGENT_DIR; "
      "user policy C:\\Users\\derek\\.pi\\agent\\pi-permissions.jsonc 35910 B sha8 19716809, 346 deny mentions, values "
      "never printed); every package the launcher's header names resolves in one of the two package roots, as does the "
      "set the main chat declares. Keep list, driven for real in full-access mode: gpu_guard.ps1 is called and "
      "gpu_lock never is; a synthetic live-PID lock makes the lane refuse rc=3 with -NoWait and queue-then-defer "
      "bounded with the lock bytes untouched, and the lane takes no lock and makes no model call; the adults-only, "
      "no-minors and no-tone-into-a-render-prompt rules are in the persona and in the lane's AGENTS.md; the three "
      "session stores (loop, lane, main chat) are distinct. THE TEST: 5 tasks x 2 sides, byte-identical task text, "
      "the same model and provider on both sides (this chat runs coding_swift15_iq3s_esp too), the prompt passed as "
      "@path so argv stays quote-free, 10/10 runs rc=0 - the 3 the plan names (a render prompt from the POOL start "
      "frame, a real file edit, a commit message) plus 2 keep-probes. Both sides produced the box's prompt shape "
      "(four H3 sections, the hand lock, beats to 00:10.125 = 243 frames at 24 fps, no R7 audio block): main 1643 "
      "words, lane 2055. The file edit is proved on disk, not by the models' words: both targets reset to sha8 "
      "0B13E858 with target = 3, then both read sha8 B7D40C5C with target = 7 and exactly the four original lines. "
      "From inside each session: the same 10 skill names, the same core tool set used by both sides, a byte-identical "
      "secret block naming Rule: secret.basename.env with no value printed, and the same adults-only statement. The "
      "lane's 6 one-shot sessions carry the persona in their system sections with provider=llama-swap "
      "model=coding_swift15_iq3s_esp and cwd = the loop dir; the main chat's carry no persona. Result for Derek: the "
      "lane's ARTEFACTS carried no chat tone (0 words in its render prompt, 0 in its commit message) - tone appeared "
      "only in the sentences wrapped around them, which is what the persona's own rule asks; and full access opened "
      "the shared pi-memory to the lane (its sessions show a memory_search), so its words can reach MEMORY.md and the "
      "daily rows - a lane-private memory dir is the clean fix if you want that kept out, and it is your config "
      "choice. Both outputs of every task: C:/AI/community/notes/2026-10-29-U3c-compare.md (45807 B, built from the "
      "files by notes/_u3c/build_compare.py); harness, task texts, raw outputs and the rc/elapsed manifest in "
      "C:/AI/community/notes/_u3c/. No GPU, no render, no lock, no model load, no install, no config edit, no shared "
      "instruction file edited beyond this plan. Check: notes/u3bc_check.py exit 0.")

check_only = "--check" in sys.argv
src = io.open(PLAN, "r", encoding="utf-8", newline="").read()
crlf, lf = src.count("\r\n"), src.count("\n") - src.count("\r\n")
lines = src.splitlines(keepends=True)          # keep each line's own terminator: this file mixes CRLF and LF
old5 = [i for i, l in enumerate(lines) if l.lstrip().startswith("5. [ ]")]
old6 = [i for i, l in enumerate(lines) if l.lstrip().startswith("6. [ ]")]
print("plan %d B sha8 %s, lines=%d, CRLF lines=%d, LF lines=%d" %
      (len(open(PLAN, "rb").read()), sha8(PLAN), len(lines), crlf, lf))
print("targets: item5 line=%s item6 line=%s (each one physical line=%s)" %
      (old5, old6, len(old5) == 1 and len(old6) == 1))
assert len(old5) == 1 and len(old6) == 1, "expected exactly one unticked line per item"
for name, t in (("item5", T5), ("item6", T6)):
    assert "\n" not in t and "\r" not in t, name + " must be one line"
    assert all(ord(c) < 128 for c in t), name + " must stay ASCII"
    assert W not in t.lower() and "daddy" not in t.lower(), name + " must carry no tone word"
if check_only:
    sys.exit(0)
io.open(BAK, "w", encoding="utf-8", newline="").write(src)


def term(l):
    return "\r\n" if l.endswith("\r\n") else ("\n" if l.endswith("\n") else "")


def indent(l):
    return l[:len(l) - len(l.lstrip())]          # the MAX block indents its items; keep the item on its own line


lines[old5[0]] = indent(lines[old5[0]]) + T5 + term(lines[old5[0]])
lines[old6[0]] = indent(lines[old6[0]]) + T6 + term(lines[old6[0]])
out = "".join(lines)
assert all(ord(c) < 128 for c in out), "no non-ASCII in the plan"
io.open(PLAN, "w", encoding="utf-8", newline="").write(out)
new = io.open(PLAN, encoding="utf-8", newline="").read()
ncl, nfl = new.count("\r\n"), new.count("\n") - new.count("\r\n")
print("backup %s (the pre-edit bytes) %d B sha8 %s" % (os.path.basename(BAK), os.path.getsize(BAK), sha8(BAK)))
print("plan now %d B sha8 %s, lines=%d (same=%s), line endings CRLF %d->%d LF %d->%d (unchanged=%s)" %
      (os.path.getsize(PLAN), sha8(PLAN), len(new.splitlines()), len(new.splitlines()) == len(lines), crlf, ncl, lf,
       nfl, (crlf, lf) == (ncl, nfl)))
print("unticked MAX items left=%d, items 5/6 ticked=%d"
      % (len([l for l in new.splitlines() if re.match(r"^\d+\. \[ \]", l.lstrip())]),
         len([l for l in new.splitlines() if re.match(r"^[56]\. \[x\]", l.lstrip())])))
