"""U1 close-out (2026-10-29, MAX block item 1): tick fix_plan.md item 1 and append the
actions.log lines (U1 DONE + U1b START) and the ralph-community progress line.
fix_plan.md IS CRLF: read/write with newline='' and join on CRLF (a tick is ONE physical line).
Every appended line is normalised to ASCII and asserted ASCII before writing."""
import io
import re
import time
from pathlib import Path

NOW = time.strftime("%Y-%m-%d %H:%M")
FIXPLAN = Path(r"C:/Users/derek/5slock/ralph-community/fix_plan.md")
ACTIONS = Path(r"C:/AI/community/notes/actions.log")
PROGRESS = Path(r"C:/Users/derek/5slock/ralph-community/notes/progress.md")
CHECK = r"C:/AI/community/notes/item5_u1_check.py"

OLD_TICK = ("  1. [ ] U1 close-out: re-run C:\\AI\\community\\notes\\item5_u1_check.py "
            "(Max applied U1a at 9:06 AM CT, backups *.bak-20261029-max2u1a). If every check passes, "
            "record it as item 5 (U1) done in actions.log and here; if not, stop and report.")
NEW_TICK = ("  1. [x] U1 close-out DONE %s CT: %s exit 0 ALL CLAUSES PASS - ralph.ps1 param default = "
            "coding_swift15_iq3s_esp, PROMPT.md 1b = coding_swift15_iq3s_esp, '0a claims pinned' = False "
            "(matches the ralph.ps1:51 argv, only @PROMPT.md), beta6_int8 scan over both skill trees = 2 hits "
            "both marked (RETIRED/SUPERSEDED, PRIOR KEEP) 0 unmarked. Max's U1a diff measured now = exactly 2 "
            "lines in ralph.ps1 (L3 usage comment, L6 param default) + 1 line in PROMPT.md 1b, backups "
            "*.bak-20261029-max2u1a present. All three U1 sub-items are closed (U1a Max, U1b PROMPT.md 0a "
            "fc2945b, U1c director skill). The plan's other U1 criterion 'the next iteration log shows the _esp "
            "model' cannot be read now: the loop is not running (logs/ralph.log newest line 2026-10-27T09:07:54), "
            "so it lands with the next real loop start; the measured equivalents (launcher default, PROMPT.md 1b, "
            "the id in models.json) are green. Recorded in C:\\AI\\community\\notes\\actions.log. No GPU, no render."
            ) % (NOW, CHECK)

raw = FIXPLAN.read_bytes()
crlf = raw.count(b"\r\n") == raw.count(b"\n") and raw.count(b"\n") > 0
text = raw.decode("utf-8")
lines = text.split("\r\n" if crlf else "\n")
assert "\n" not in NEW_TICK and "\r" not in NEW_TICK
hits = [i for i, l in enumerate(lines) if l == OLD_TICK]
if not hits:  # idempotent: a second run must not double-tick
    assert any(l.startswith("  1. [x] U1 close-out DONE") for l in lines), \
        "neither the open nor the ticked item-1 line is in fix_plan.md"
    print("fix_plan.md item 1 is already ticked - no write")
else:
    assert len(hits) == 1, "expected exactly 1 exact match of the item-1 line, got %d" % len(hits)
    lines[hits[0]] = NEW_TICK
    sep = "\r\n" if crlf else "\n"
    FIXPLAN.write_bytes(sep.join(lines).encode("utf-8"))
    print("fix_plan.md item 1 ticked [x] (CRLF preserved: %s; %d lines)" % (crlf, len(lines)))

action_lines = [
    ("%s CT Pi (MAX block item 1 = U1 CLOSE-OUT) DONE, all three U1 sub-items now closed, no GPU, no render. "
     "Re-ran %s -> exit 0, VERDICT ALL CLAUSES PASS: ralph.ps1 param default = coding_swift15_iq3s_esp (PASS), "
     "PROMPT.md 1b = coding_swift15_iq3s_esp (PASS), 'PROMPT.md 0a claims pinned' = False i.e. it matches what "
     "ralph.ps1:51 really passes (PASS), beta6_int8 scan over C:/Users/derek/.pi/agent/skills + C:/AI/community/skills "
     "= 2 hits, both marked (alienpc-hardcore-i2v-director SKILL.md:25 RETIRED/SUPERSEDED, alienpc-local-video-ops "
     "SKILL.md:20 PRIOR KEEP), 0 unmarked (PASS). U1a is Max's edit at 09:05 CT (his actions.log line, backups "
     "ralph.ps1.bak-20261029-max2u1a and PROMPT.md.bak-20261029-max2u1a); measured with git diff --numstat now: "
     "ralph.ps1 2/2 lines (L3 usage comment, L6 $Model default), PROMPT.md 1/1 line (1b) - nothing else in either "
     "file. I did NOT commit those two: 'git -C ralph-community add -- ralph.ps1' is denied by pi-permissions.jsonc:465 "
     "and the pair is Max's working-tree change, so the harness/Max commits it. U1b (PROMPT.md 0a) = fc2945b, "
     "U1c (director skill beta6 KEEP line retired) = e384abe/d449544. The plan's second U1 criterion, 'the next "
     "iteration log shows the _esp model', is NOT observable this minute: no ralph.ps1 process is running and "
     "logs/ralph.log newest line is 2026-10-27T09:07:54, so it is recorded as pending the next real loop start "
     "rather than claimed. fix_plan.md MAX item 1 ticked [x] with the evidence inline (line-preserving CRLF edit, "
     "script notes/u1_closeout_record.py). Item 2 (U1b) starts next." % (NOW, CHECK)),
    ("%s CT Pi (MAX block item 2 = U1b UPGRADES) START (Derrick 'yes go' 9:08 AM CT; plan "
     "C:/AI/community/notes/2026-10-29-forge-cleanup-plan.md unit U1b). Scope: bring Strata, llama-swap and pi to "
     "their latest releases on THIS box, each verified against its own release source (hints only: Strata 0.2.7.1, "
     "llama-swap v268). Measured today's baseline before touching anything: pi 1.4.0 (npm global, "
     "C:/Users/derek/AppData/Roaming/npm), llama-swap v266 c099777 built 2026-10-22 (C:/AI/llama-swap-trial/bin/"
     "llama-swap.exe, pid 3076, -config C:/AI/director/config/llama-swap.yaml -watch-config), Strata terminal "
     "checkout C:/AI/strata-0.2.2 (not a git repo) with its engine installed from the signed feed at "
     "github.com/Niko1221/Strata/releases/download/v0.2.2/strata-feed.json into C:/AI/strata-engine-022, served "
     "through C:/AI/strata-0.2.2/sy_strata_launch.py with configs strata-swift15-iq3s.json and strata-swift15-"
     "iq3s-esp.json. Keep: ESP on, the Swift 1.5 IQ3_S model file, the calibrated flags; back up every config and "
     "binary first (llama-swap.yaml, the strata configs, pi models.json/settings.json); one start + one done line "
     "per upgrade; revert from backup on failure. No GPU render job during this - gpu_guard.ps1 says IDLE at start and "
     "is re-checked before any model load." % NOW),
]

progress_line = (
    "- %s [MAX block item 1 = U1 CLOSE-OUT DONE, no GPU] %s exit 0 ALL CLAUSES PASS: ralph.ps1 $Model default "
    "= coding_swift15_iq3s_esp, PROMPT.md 1b = coding_swift15_iq3s_esp, 0a-vs-argv clause clean, beta6_int8 over "
    "both skill trees = 2 hits both marked 0 unmarked. U1a = Max2 09:05 CT (git diff --numstat: ralph.ps1 2 lines, "
    "PROMPT.md 1 line, backups *.bak-20261029-max2u1a); U1b = fc2945b; U1c = e384abe. ralph.ps1 and PROMPT.md were "
    "left uncommitted on purpose: adding ralph.ps1 is denied (pi-permissions.jsonc:465) and the pair is Max's "
    "working-tree edit. The plan's other U1 criterion (the next iteration log shows the _esp model) is pending the "
    "next loop start - no ralph process is running and logs/ralph.log stops at 2026-10-27T09:07:54, so it is not "
    "claimed as observed. fix_plan item 1 ticked with evidence inline via notes/u1_closeout_record.py (CRLF "
    "preserved). Item 2 = U1b upgrades starts next.\n" % (NOW, CHECK)
)



# the item-1 line takes (NOW, CHECK); the item-2 START line is a plain string
def norm(s):
    for a, b in (("\u2026", "..."), ("\u2192", "->"), ("\u2190", "<-"), ("\u2019", "'"), ("\u2018", "'"),
                 ("\u201c", '"'), ("\u201d", '"'), ("\u00a0", " "), ("\u2014", "--"), ("\u2013", "-")):
        s = s.replace(a, b)
    return s


for p, lines in ((ACTIONS, [norm(l) for l in action_lines]), (PROGRESS, [norm(progress_line)])):
    data = p.read_bytes()
    assert data.endswith(b"\n"), p
    add = "".join(l + "\n" for l in lines).encode("ascii")  # asserts ASCII
    p.write_bytes(data + add)
    print("appended %d line(s) to %s (+%d B, ASCII-clean)" % (len(lines), p, len(add)))
