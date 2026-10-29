"""U1 close-out stop line (2026-10-29): U1b is Max's per Derrick 9:27 AM CT, so the 09:28
U1b START line is superseded and nothing was installed by me. Append-only, ASCII, LF-terminated."""
import time
from pathlib import Path

NOW = time.strftime("%Y-%m-%d %H:%M")
ACTIONS = Path(r"C:/AI/community/notes/actions.log")

line = (
    "%s CT Pi (MAX block stops at the U1 close-out) STOP. Per Max/Derrick 9:27 AM CT, U1b upgrades are Max's, so "
    "my 09:28 U1b START line is superseded and is NOT a claim of work: I installed nothing. No binary, config, "
    "model, pi package, strata checkout, engine component or pi models.json/settings.json was modified by me, and "
    "no service was restarted (llama-swap pid 3076 v266, strata pid 39208, pi 1.4.0 all still the running "
    "baseline). The only writes were: the U1-DONE + this line in notes/actions.log, the close-out line in "
    "ralph-community/notes/progress.md (commit fca8df9), the item-1 tick in fix_plan.md (fca8df9, backup "
    "fix_plan.md.bak-20261029-u1closeout) and notes/u1_closeout_record.py (2486d0e). U1b discovery output I "
    "fetched for Max is left in C:/AI/bench (rel_strata.json = the Niko1221/Strata releases API, pi_npm.json = "
    "the npm @earendil-works/pi-coding-agent latest, rel_lswap.json = 404: the API path Mozilla-Ocho/llama-swap "
    "is wrong, the real repo is mostlygeek/llama-swap per bin/CHANGELOG.md) - unverified hints, nothing applied. "
    "Measured baseline for whoever runs U1b: pi 1.4.0 (npm global), llama-swap v266 c099777 built 2026-10-22 at "
    "C:/AI/llama-swap-trial/bin, Strata terminal checkout C:/AI/strata-0.2.2 (not a git repo) with the engine "
    "from the v0.2.2 signed feed in C:/AI/strata-engine-022, served through sy_strata_launch.py with "
    "strata-swift15-iq3s.json and strata-swift15-iq3s-esp.json. gpu_guard.ps1 = IDLE; no GPU, no render, no "
    "ComfyUI/llama-swap model load by me." % NOW
)

for a, b in (("\u2026", "..."), ("\u2192", "->"), ("\u2019", "'"), ("\u201c", '"'), ("\u201d", '"'),
             ("\u00a0", " "), ("\u2014", "--")):
    line = line.replace(a, b)
add = (line + "\n").encode("ascii")  # asserts ASCII
raw = ACTIONS.read_bytes()
assert raw.endswith(b"\n")
ACTIONS.write_bytes(raw + add)
print("appended 1 line (+%d B, ASCII-clean)" % len(add))
