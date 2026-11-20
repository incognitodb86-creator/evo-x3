# U59 (Antigravity, Hydrogen Medium): apply Hermes workspaces + PixlStash picker on the X3, Nov 20 2026

Derrick 2026-11-20 ~10:20 AM CT (VS Code orchestrator chat): "include a hand off prompt for max. I want him to
delegate this to antigravity hydrogen medium to implement." Approvals this brief applies:

- H7 workspaces, D1-D7: Derrick 2026-11-20 ~9:07 AM CT. Render alias `presence_penalty` 0.0, code thinking
  medium with the 8192 budget, archive the Gemma profile, pin `ref2va-27b-heretic-q4` to Flash-Next.
- PixlStash PX1 + PX2: Derrick 2026-11-20 ~9:56-10:01 AM CT ("lest do it #1 & #2. smart score 2.2").

Plans: [records/uplan/PLAN.md](uplan/PLAN.md) (H7),
[records/PIXLSTASH-UPGRADE-20261120/PLAN.md](PIXLSTASH-UPGRADE-20261120/PLAN.md) (PX1, PX2),
[records/REA-PARODY-PIPELINE/PLAN.md](REA-PARODY-PIPELINE/PLAN.md) (C0 only). Max verifies your RESULT afterwards.

U number: U59 is an ASSUMPTION (U58 is the highest in `mono`; the box can be ahead).

## Goal

Run the two reviewed installers on the X3 and record what they print. That gives Hermes two workspaces: render
(default profile, `flash-next-render`) and code (`code` profile, `flash-next-code`, thinking medium). It also gives
the render workspace the new still picker (Smart Score 2.2 floor only, aspect filter, 1 pick per stack). Then set up
the C0 clone the local LLM will code in. You do NOT write REA code: C1-C7 are Derrick's test of the coding
workspace and run from the Hermes code chat.

## Access

- You run as `derekboone`. The mono clone is `/home/derekboone/evo-x3` (ASSUMPTION: Max pulled `mono` there before
  launching you). Evo-owned files are changed only by the installers or by the exact commands below.
- No code changes, so no per-run worktree. You write only `records/U59-RESULT.md` in `/home/derekboone/evo-x3`.
- Lease: both installers take and clear `/home/derekboone/AI/locks/x3-lease.txt` themselves and stop if it isn't
  empty. So do NOT hold the lease while an installer runs. For S1 and S4 only, write ONE line
  `agy | U59 <step> | <start time CT>` before the step (stop if the file isn't empty), and empty the file right
  after the step, done or blocked.
- Why: Hermes runs one workspace on the old settings, and the live picker skill returns the same 5 close-ups every
  time (`sort=SMART_SCORE&limit=5`, VERIFIED in
  `hosts/x3/live/hermes/skills/custom/pixlstash-image-library/SKILL.md`).
- Run every code block below exactly as written. Copy them from column 0; the heredoc end markers must stay at the
  start of the line.

## Work

### S0. Preflight (read-only, no lease)

- `git -C ~/evo-x3 status -sb` is clean and on `mono`, and `git -C ~/evo-x3 log -1 --format=%h` matches the SHA in
  Max's launch message.
- `cat /home/derekboone/AI/locks/x3-lease.txt` prints nothing, and
  `sudo -n systemctl --user -M evo@ list-units 'pi-job-*' --no-legend` lists no active unit.
- If any of these fails, stop: BLOCKED.

### S1. Remove one stale Hermes memory entry (lease line `agy | U59 USER.md | <time>`)

Derrick 2026-11-20 ~10:20 AM CT asked that the Sydney Sweeney / FCSydny distinction not be mentioned anywhere. The
repo copy is already fixed. This removes the same entry from the live memory file BEFORE S2 restarts the gateway and
clones the profile. It never prints the file.

```bash
sudo -n -u evo -H env -C /home/evo python3 - <<'PY'
import pathlib, shutil
arch = pathlib.Path("/home/evo/.hermes/_archive")
for name, p in (("default", pathlib.Path("/home/evo/.hermes/memories/USER.md")),
                ("code", pathlib.Path("/home/evo/.hermes/profiles/code/memories/USER.md"))):
    if not p.is_file():
        print(name, "absent")
        continue
    s = p.read_text(encoding="utf-8")
    parts = s.split("\n§\n")
    keep = [x for x in parts if "not FCSydny" not in x]
    if len(keep) < len(parts):
        new = "\n§\n".join(keep)
    else:
        lines = s.split("\n")
        keep_lines = [l for l in lines if "not FCSydny" not in l]
        if len(keep_lines) == len(lines):
            print(name, "already clean")
            continue
        new = "\n".join(keep_lines)
    arch.mkdir(parents=True, exist_ok=True)
    bak = arch / f"{name}-USER.md.bak-20261120-u59"
    shutil.copy2(p, bak)
    p.write_text(new, encoding="utf-8")
    print(name, "removed 1 entry;", len(s), "->", len(new), "chars; backup", bak)
PY
```

Clear the lease line.

### S2. H7 Hermes workspaces (the installer takes its own lease)

1. `bash ~/evo-x3/scripts/apply-hermes-workspaces.sh --dry-run`. If it prints `BLOCKED`, stop.
2. `bash ~/evo-x3/scripts/apply-hermes-workspaces.sh --apply`. The defaults are Derrick's choices (render presence
   0.0, code thinking medium). Pass no other flags.
3. On any `FAIL`: `bash ~/evo-x3/scripts/apply-hermes-workspaces.sh --rollback`, then stop: BLOCKED.
4. The installer writes `records/UNI-APPLY-X3-HERMES-WORKSPACES/RESULT.md` (or `/tmp/...` if records isn't
   writable). Keep that file.
5. It prints a NOTE about `models.json`. Do NOT open `models.json`; Max does that check.

### S3. PixlStash PX1 + PX2 (after S2; the installer takes its own lease)

1. `bash ~/evo-x3/scripts/apply-pixlstash-upgrade.sh --status` (read-only). Keep the memcap lines, the
   `memory.events` lines and the dedup-count numbers. For penalised tags, record only how many there are.
2. `bash ~/evo-x3/scripts/apply-pixlstash-upgrade.sh --dry-run`, then `bash ~/evo-x3/scripts/apply-pixlstash-upgrade.sh --apply`.
   The apply runs the picker pytest (expect `8 passed`).
3. On failure: `bash ~/evo-x3/scripts/apply-pixlstash-upgrade.sh --rollback`, then stop: BLOCKED.
4. Do NOT run `--create-smart-sets --apply`, and do NOT POST or PATCH anything to PixlStash. Smart Sets (Q-PX2),
   dedup stacks and penalty tuning are Derrick's UI steps.

### S4. C0, the REA coding clone (lease line `agy | U59 C0 | <time>`)

A bundle, so evo needs no git credentials:

```bash
B=/tmp/u59-mono.bundle
git -C ~/evo-x3 bundle create "$B" mono && chmod 0644 "$B"
sudo -n -u evo -H env -C /home/evo bash -c '
set -euo pipefail
D=/home/evo/AI/_worktrees/rea-parody
if [[ -e "$D" ]]; then echo "EXISTS: $D (left as is)"; exit 3; fi
mkdir -p /home/evo/AI/_worktrees
git clone -q -b mono "$1" "$D"
git -C "$D" switch -q -c pi/rea-parody
git -C "$D" status -sb | head -n 1
/home/evo/AI/render/x3/.venv/bin/python3 -c "import numpy, PIL, pytest; print(\"venv ok\")"
' _ "$B"
rm -f "$B"
```

If it prints `EXISTS:`, the clone is already there: record that and don't touch it. If it prints neither the branch
line nor `venv ok`, record the error lines as BLOCKED. Clear the lease line either way.

### S5. RESULT and local commit

Write `records/U59-RESULT.md` (see STOP CONDITION). Commit by path only:
`git -C ~/evo-x3 add records/U59-RESULT.md` plus `records/UNI-APPLY-X3-HERMES-WORKSPACES/RESULT.md` if the installer
wrote it there, then `git -C ~/evo-x3 commit -m "U59: H7 workspaces + PX1/PX2 apply RESULT"`. Don't push. Max pushes
to GitHub first, then mirrors to Gitea.

## Tests

- S2: the H7 RESULT shows the `flash-next-render`, `flash-next-aux` and `flash-next-code` probes OK and `hermes hooks
  doctor` healthy. The render oneshot names `h3-render`, and the code oneshot names `pi-job`. The code skills check
  does NOT list `h3-render` or `h3-writer`.
- S2: `pi-job code --help 2>&1 | grep -c -- --timeout-min` is 1 or more, and
  `sudo -n -u evo grep -c FORGE_KEEP_CWD /home/evo/evo-x3/pi-chats/forge-pi.sh` is 1 or more.
- S3: `sudo -n systemctl --user -M evo@ show pixlstash.service -p MemoryHigh -p MemoryMax` shows
  `MemoryHigh=15032385536` and `MemoryMax=17179869184` (14G and 16G).
- S3 live picker check. It also checks the API field names the picker assumes. Record only the dict it prints;
  don't open the sheet or list file paths:

```bash
sudo -n -u evo -H env -C /home/evo /home/evo/AI/render/x3/.venv/bin/python3 \
  /home/evo/AI/render/x3/still_candidate_sheet.py --character-id 1 --aspect 16:9 --limit 6 \
  --out /tmp/u59-sheet.png --seed 59 \
| python3 -c 'import json,sys; r=json.load(sys.stdin); f=lambda k: sum(1 for x in r if x.get(k) is not None); print({"picked": len(r), "distinct_stacks": len({x.get("stack_id") for x in r if x.get("stack_id") is not None}), "has_width": f("width"), "has_likeness": f("likeness_score"), "has_smart": f("smart_score"), "needs_reframe": any(x.get("needs_reframe") for x in r), "smart_floor_fallback": any(x.get("smart_floor_fallback") for x in r)})'
sudo -n -u evo rm -f /tmp/u59-sheet.png
```

  It passes when `picked` is 1-6 and the command exits 0. Report `has_width` = 0 or `has_likeness` = 0 as a
  FINDING, not a failure: it means an API field has a different name live.
- S4: as evo, `git -C /home/evo/AI/_worktrees/rea-parody status -sb` shows `## pi/rea-parody`, and S4 printed
  `venv ok`.

## Rules

- The installers back up everything they change, to `/etc/evo-x3/_archive/`, `/home/evo/.hermes/_archive/20261120-ws/`,
  `/home/evo/AI/_archive/20261120-ws-pi/` and `/home/evo/AI/_archive/20261120-pixlstash-upgrade/`. Don't edit those
  backups by hand. S1 backs up to `/home/evo/.hermes/_archive/*-USER.md.bak-20261120-u59`.
- Don't edit llama-swap, Hermes config, skills, systemd units or PixlStash outside the installers. Don't touch
  AlienPc, ComfyUI or pi models, and don't touch `/home/evo/AI/_worktrees/rea-parody` after S4. Don't run `pi-job`.
- Never read or print `auth.json`, `mcp.json`, `models.json`, `.env` or `llm.env`, `*.token`, secrets under
  `/etc/evo-x3/`, or `~/.ssh`. Never put a key on a command line. Don't print git remote URLs.
- Don't browse PixlStash pictures, captions or chat memory beyond S1 and the S3 picker check.
- Commit by path only. No `git add -A`, no force push, no push at all.
- Keep it small: no new gates, knobs or scripts. If an installer has a bug, stop and report it; don't patch it.

STOP CONDITION: when done or blocked, write `/home/derekboone/evo-x3/records/U59-RESULT.md`, then stop. List S0-S5 and
each Tests item as DONE, BLOCKED or SKIPPED. Include:
- start and end times (CT);
- the H7 RESULT path;
- the S1 output lines and backup paths;
- the S3 memcap values, `memory.events` and dedup counts;
- the picker-check dict;
- the S4 branch line;
- every rollback you ran;
- the local commit SHA.
