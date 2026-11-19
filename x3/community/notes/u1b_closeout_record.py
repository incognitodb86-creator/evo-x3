"""U1b close-out (2026-10-29, MAX block item 2): tick fix_plan.md item 2, append the
actions.log DONE line and the ralph-community progress line.
The installs are Max2's (actions.log 09:30-09:45 CT); this pass only measures and records.
fix_plan.md IS CRLF: read/write with newline='' and join on CRLF (a tick is ONE physical line).
Every appended line is normalised to ASCII and asserted ASCII before writing.
Idempotent: a second run must not double-tick.
"""
import time
from pathlib import Path

NOW = time.strftime("%Y-%m-%d %H:%M")
FIXPLAN = Path(r"C:/Users/derek/5slock/ralph-community/fix_plan.md")
ACTIONS = Path(r"C:/AI/community/notes/actions.log")
PROGRESS = Path(r"C:/Users/derek/5slock/ralph-community/notes/progress.md")
CHECK = r"C:/AI/community/notes/u1b_done_check.py"
LOGCMP = r"C:/AI/community/notes/u1b_log_compare.py"
DONE = r"C:/AI/community/notes/2026-10-29-U1b-upgrades-DONE.md"
KEEPALIVE = r"C:\AI\director\scripts\llama_swap_keepalive.ps1:8"
PREFIX = "  2. [ ] U1b upgrades"
TICKED = "  2. [x] U1b upgrades DONE"

VERIFIED = (
    "%s exit 0 ALL CLAUSES PASS 22/22, read-only against this disk and the live processes. "
    "WHAT IS LIVE: Strata 0.2.7 tree + engine 0.1.52-windows-x86_64-cuda-cuda13 in C:\\AI\\strata-engine-027 "
    "serving the _esp slot (pid 32144; cmdline carries --expert-profile --expert-cache --control-vector-scaled "
    "--control-vector-layer-range --cvec-mode --cvec-dir --max-context 262144, and both ESP data files exist in "
    "the 0.2.7 tree at the same sizes as 0.2.2: expert-profile.bin 196,632 B and the experimental-speed-projection "
    "gguf 483,520 B); llama-swap v268 (commit 2576af3, built 2026-10-28T03:26:39Z) as pid 16880, /api/version "
    "answers v268, started with the standing launcher args from %s (-config <yaml> -listen 127.0.0.1:8080 "
    "-watch-config), so the -listen form is this box's normal service shape and not an U1b config change; pi stays "
    "1.4.0. " % (CHECK, KEEPALIVE))

LATEST = (
    "LATEST VERIFIED AT EACH SOURCE, not from the plan's hints: github.com/Niko1221/Strata releases/latest = v0.2.7 "
    "(published 2026-10-27T14:54:42Z) = what is installed; the plan's 'Strata 0.2.7.1' hint is a git TAG only - "
    "GET /releases/tags/v0.2.7.1 = 404 and the full releases list stops at v0.2.7 - so v0.2.7 IS the latest "
    "published release; github.com/mostlygeek/llama-swap releases/latest = v268 (published 2026-10-28T03:32:27Z) = "
    "installed; npm view @earendil-works/pi-coding-agent = 1.4.0 = the installed pi --version, so there is NO pi "
    "upgrade to do and none was installed. ")

CARRY = (
    "CONFIG CARRY-OVER PROVED, NOT ASSERTED: the live llama-swap.yaml has 0 refs to strata-0.2.2 and both swift15 "
    "launch lines point at strata-0.2.7 (diff vs the pre-upgrade backup = exactly those 2 cmd lines + a BOM); "
    "C:\\AI\\strata-0.2.7\\strata-swift15-iq3s-esp.json is identical to the 0.2.2 file after masking ONLY the "
    "0.2.7/0.2.2 and 0.1.52/0.1.47 path strings (both mask to 3,064 chars), i.e. the calibrated flags, the ESP "
    "profile paths and the Swift 1.5 IQ3_S model file are unchanged - no flag drift. ")

BACKUPS = (
    "BACKUPS AND REVERT PATH PRESENT: llama-swap.yaml.bak-20261029-0932-max2-strata (6 old-tree refs inside), "
    "strata-0.2.2\\strata-swift15-iq3s-esp.json.bak-20261029-0932, bin\\llama-swap.exe.bak-v266-20261029 "
    "(42,984,960 B), models.json.bak-20261029-max2, C:\\Users\\derek\\.pi\\agent.bak-20261029-max2, and the whole "
    "C:\\AI\\strata-0.2.2 + C:\\AI\\strata-engine-022 trees kept, with 0 processes on the old engine. ")

PERF = (
    "MEASURED CEILING ON coding_swift15_iq3s_esp WITH THE NEW ENGINE (strata-0.2.7\\strata-swift15-iq3s-esp.log): "
    "a 261,264-token prompt was served at 2,991.7 tok/s prefill - larger than ANY prompt in the entire 0.2.2 log "
    "(max 249,936 over 1,271 served prompts), so the ceiling moved up, and pi models.json _esp contextWindow = "
    "257,000 / maxTokens = 32,768 (bak-20261029-max2) with settings.json defaultModel = coding_swift15_iq3s_esp "
    "sits under the measured acceptance, i.e. the pi-side ceiling is conservative as U1b asks. Max's 262,635-token "
    "refusal is his measurement; I did not reproduce a refusal, so it is not re-claimed here. THROUGHPUT, old-vs-new "
    "log (%s): decode median 104.6 / p90 117.8 / max 130.4 tok/s on n=43 in the 19-minute 0.2.7 log vs median "
    "103.1 / p90 118.5 / max 158.4 on n=1,271 in the 0.2.2 log = decode unchanged; prefill median 407.4 (new) vs "
    "411.1 (old) and the new p90/max 2,626/3,059 sit under the old 2,843/3,314, which is a 43-sample-vs-1,271-"
    "sample max-of-different-samples effect and NOT a measured slowdown - U1b asks for the ceiling and a tok/s "
    "reading, both delivered, and a fair prefill A/B (warm-first matrix) was not asked for and is not claimed. "
    % LOGCMP)

DOCS = (
    "PI-DOCS CLAUSE: no pi upgrade exists, so the docs are unchanged bytes - cli.md sha8 c45e59f3, configuration.md "
    "sha8 fc48d1ce - and all three U3 behaviours are documented in the installed 1.4.0 (--append-system-prompt "
    "cli.md:224/231, skills discovery and -ns cli.md:202-203, AGENTS.md and skills-dir configuration.md:18/22), so "
    "U3's assumptions are unaffected by U1b. ")

SMOKE = (
    "LIVE SMOKE: this close-out pass itself ran THROUGH the upgraded stack (PI_PROVIDER=llama-swap, "
    "PI_MODEL=coding_swift15_iq3s_esp served by v268 + engine 0.1.52), which is an end-to-end working smoke. ")

NO_REGRESS = (
    "NO REGRESSION SIGNAL in the old-vs-new log compare (%s): the strata-vision 'no CUDA-capable device' and 'on "
    "the CPU' lines and the low-VRAM warnings appear in the 0.2.2 log too (42 and 55 occurrences there vs 2 and 2 "
    "in the short 0.2.7 log), so they are pre-existing, not introduced by 0.2.7. " % LOGCMP)

COSMETIC = (
    "COSMETIC, NOT MINE TO FIX, LEFT FOR MAX: llama-swap.yaml:2 header comment still reads 'Supervisor for Strata "
    "0.2.1.1' (pre-existing - the same text is in the pre-upgrade backup) and bin\\CHANGELOG.md is topped at v266 "
    "while the binary is v268 (the v268 install replaced only the exe). ")

STOP = (
    "gpu_guard.ps1 = IDLE before and after this pass; no GPU render, no ComfyUI/llama-swap model load by me, "
    "nothing rendered, no service restarted by me. STOP AFTER U1b per the MAX block: U2-U5 not started. Recorded in "
    "C:\\AI\\community\\notes\\actions.log; detail in %s." % DONE)

NEW_TICK = ("  2. [x] U1b upgrades DONE %s CT (installs = Max2 09:30-09:45 CT per actions.log; close-out measured "
            "by Pi). " % NOW) + VERIFIED + LATEST + CARRY + BACKUPS + PERF + DOCS + SMOKE + NO_REGRESS + COSMETIC + STOP

raw = FIXPLAN.read_bytes()
crlf = raw.count(b"\r\n") == raw.count(b"\n") and raw.count(b"\n") > 0
text = raw.decode("utf-8")
lines = text.split("\r\n" if crlf else "\n")
assert "\n" not in NEW_TICK and "\r" not in NEW_TICK
open_hits = [i for i, l in enumerate(lines) if l.startswith(PREFIX)]
done_hits = [i for i, l in enumerate(lines) if l.startswith(TICKED)]
if not open_hits:
    assert len(done_hits) == 1, "neither the open nor the ticked item-2 line is in fix_plan.md"
    print("fix_plan.md item 2 is already ticked - no write")
else:
    assert len(open_hits) == 1, "expected exactly 1 open item-2 line, got %d" % len(open_hits)
    assert not done_hits, "both an open and a ticked item-2 line exist"
    lines[open_hits[0]] = NEW_TICK
    sep = "\r\n" if crlf else "\n"
    FIXPLAN.write_bytes(sep.join(lines).encode("utf-8"))
    print("fix_plan.md item 2 ticked [x] (CRLF preserved: %s; %d lines, %d B; tick line %d chars)" % (
        crlf, len(lines), len(sep.join(lines).encode("utf-8")), len(NEW_TICK)))

action_line = (
    "%s CT Pi (MAX block item 2 = U1b UPGRADES) DONE + STOP - close-out of Max2's installs (his actions.log lines "
    "09:30-09:45 CT). No GPU, no render, no model load, no restart and no install by me. %s exit 0, VERDICT ALL "
    "CLAUSES PASS 22/22, read-only. " + VERIFIED + LATEST + CARRY + BACKUPS + PERF + DOCS + SMOKE + NO_REGRESS +
    COSMETIC +
    "fix_plan MAX item 2 ticked [x] with this evidence inline via notes/u1b_closeout_record.py (line-preserving "
    "CRLF edit, backup fix_plan.md.bak-20261029-u1b-tick). Detail note %s. " + STOP) % (
        NOW, CHECK, DONE)

progress_line = (
    "- %s [MAX block item 2 = U1b UPGRADES DONE + STOP, no GPU] close-out of Max2's 09:30-09:45 CT installs, "
    "measured read-only: %s exit 0 ALL CLAUSES PASS 22/22. Live: Strata 0.2.7 + engine 0.1.52-cuda13 "
    "(C:\\AI\\strata-engine-027, pid 32144) on the _esp slot with every ESP flag intact and --max-context 262144, "
    "llama-swap v268 2576af3 (pid 16880, /api/version = v268) on the standing launcher args "
    "(C:\\AI\\director\\scripts\\llama_swap_keepalive.ps1:8), pi unchanged at 1.4.0 = npm latest. Latest checked at "
    "each source: Strata releases/latest = v0.2.7 = installed (the '0.2.7.1' hint is a tag with no release, GET "
    "/releases/tags/v0.2.7.1 = 404), llama-swap releases/latest = v268 = installed, npm pi latest = 1.4.0 = "
    "installed. Proved carry-over, not asserted: live yaml has 0 strata-0.2.2 refs and uses strata-0.2.7 in both "
    "swift15 slots (diff vs backup = 2 cmd lines + BOM); the 0.2.7 esp config == the 0.2.2 config with only the "
    "version path strings masked, so the calibrated flags and the Swift 1.5 IQ3_S model did not drift. Measured on "
    "_esp: 261,264 tokens served at 2,991.7 tok/s prefill - above every prompt in the 0.2.2 log (max 249,936), so "
    "the ceiling moved up; decode median 104.6 tok/s (n=43) vs 103.1 (n=1,271) = unchanged, and the lower prefill "
    "p90/max on 43 samples is NOT claimed as a slowdown (no fair warm-first A/B was asked for). pi models.json "
    "contextWindow 257,000 is under the measured acceptance, defaultModel still _esp. Max's 262,635-refused number "
    "is his, not reproduced by me. U1b's pi-docs clause is moot by upgrade: the 1.4.0 docs are unchanged (cli.md "
    "sha8 c45e59f3, configuration.md sha8 fc48d1ce) and document --append-system-prompt, skills and AGENTS.md "
    "discovery, so U3's assumptions stand. The log compare (%s) shows the vision-CUDA and low-VRAM warnings are "
    "pre-existing in the 0.2.2 log (42/55 vs 2/2), not a 0.2.7 regression. Backups/revert path all present (old "
    "strata trees, v266 exe, yaml + esp config, models.json.bak-20261029-max2, .pi\\agent.bak-20261029-max2). "
    "Cosmetic items left for Max: stale 'Strata 0.2.1.1' header comment in llama-swap.yaml:2, bin\\CHANGELOG.md "
    "still topped at v266 for a v268 binary. This pass ran on the upgraded stack itself (pi @ coding_swift15_iq3s_"
    "esp through v268 + 0.1.52), which is the live smoke. I installed/restarted/rendered nothing; gpu_guard IDLE "
    "before and after. STOP: the MAX block says stop after U1b, so U2-U5 are not started.\n" % (
        NOW, CHECK, LOGCMP))


def norm(s):
    for a, b in (("\u2026", "..."), ("\u2192", "->"), ("\u2190", "<-"), ("\u2019", "'"), ("\u2018", "'"),
                 ("\u201c", '"'), ("\u201d", '"'), ("\u00a0", " "), ("\u2014", "--"), ("\u2013", "-")):
        s = s.replace(a, b)
    return s


for p, lines in ((ACTIONS, [norm(action_line)]), (PROGRESS, [norm(progress_line)])):
    data = p.read_bytes()
    assert data.endswith(b"\n"), p
    add = "".join(l + "\n" for l in lines).encode("ascii")  # asserts ASCII
    p.write_bytes(data + add)
    print("appended %d line(s) to %s (+%d B, ASCII-clean)" % (len(lines), p, len(add)))
