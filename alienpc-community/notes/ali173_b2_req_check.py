r"""ALI-173 B2 - pre-submit gate for the staged graph job (READ-ONLY, CPU only, 2026-10-23).

The Learnings rule "ralph.ps1 id gates: parse its -notmatch patterns and test the id against all of
them first" is a real gate, not a ritual: the bakeoff raised the caps AND widened the graph id gate,
and a job whose id trips any of those patterns comes back as p7/jobs/<id>.result.json with
ok=false "refused: ..." and burns a budget job slot.

What this checks, in order:
  1 every id pattern in ralph.ps1 (both the two allow-gates at lines 202/283 and every long
    -notmatch deny list) is parsed out of the file and my id is tested against all of them, so a
    deny is named with its line number before anything is written;
  2 the request shape the RunJobs graph branch reads: kind == "graph", frames, frames_tol, minutes
    clamped 30..180 (the proven shape is p7/jobs/request_iter09.skipped.json);
  3 runs/<id>/request.api.json exists and runs/<id>/<id>.mp4 does NOT (a present mp4 = "arm already
    rendered" refusal), p7/jobs/<id>.result.json does NOT exist ("id already used");
  4 the budget line (used_min vs -GpuCapMin, jobs vs -JobMax as ralph.ps1 declares them);
  5 the id appears in TASKS.md (ReqTicked, ralph.ps1:307) and the ticked line is there;
  6 json.tool on both json files, which is exactly what the harness CHECK runs on changed files.

No network, no GPU, no writes. Exit 0 = every gate green; exit 1 = a named gate blocks the submit.
"""
import json, os, re, subprocess, sys

W = r"C:\AI\community"
K = r"C:\Users\derek\5slock\ralph-community"
RALPH = os.path.join(K, "ralph.ps1")
BUDGET = os.path.join(K, "logs", "p7_budget.json")
ID = "ali173_cont_hc1_s51140001"
STAGED = os.path.join(W, "runs", ID, "JOB_REQUEST.staged.json")
GRAPHF = os.path.join(W, "runs", ID, "request.api.json")
RUN = os.path.join(W, "runs", ID)
TASKS = os.path.join(K, "TASKS.md")

lines = open(RALPH, encoding="utf-8", errors="replace").read().splitlines()
fails = []


def ck(cond, label, extra=""):
    print(("PASS  " if cond else "FAIL  ") + label + ((" | " + extra) if extra else ""))
    if not cond:
        fails.append(label)


allow = [(i + 1, m) for i, l in enumerate(lines) for m in re.findall(r"\$id -notmatch '(\^\(.+\)\$|\^.+\\$)'", l)]
deny = [(i + 1, m) for i, l in enumerate(lines) for m in re.findall(r"-notmatch '([^']{40,})'", l)]
print(f"id gates found in ralph.ps1: {len(allow)} allow-shape, {len(deny)} deny list(s)")
for ln, pat in allow:
    ck(bool(re.search(pat, ID)), f"line {ln} allow-gate accepts the id", pat[:110])
for ln, pat in deny:
    toks = [t for t in re.split(r"[|]", pat) if t and len(t) > 2]
    hits = [t for t in toks if t in ID]
    ck(not hits, f"line {ln} deny list does not hit the id", f"patterns={len(toks)} hits={hits or 'none'}")

req = json.load(open(STAGED, encoding="utf-8"))
jobs = req.get("jobs")
ck(isinstance(jobs, list) and len(jobs) == 1, "request has exactly one job")
j = jobs[0]
ck(j.get("id") == ID, "job id matches", str(j.get("id")))
ck(j.get("kind") == "graph", 'kind == "graph" (ralph.ps1:281,298 rejects anything else)', str(j.get("kind")))
ck(isinstance(j.get("frames"), int) and j["frames"] == 240, "frames = 240 (the Continuum assembly target)", str(j.get("frames")))
ck(isinstance(j.get("frames_tol"), int) and 0 <= j["frames_tol"] <= 100, "frames_tol is a percent", str(j.get("frames_tol")))
ck(isinstance(j.get("minutes"), int) and 30 <= j["minutes"] <= 180,
   "minutes clamped 30..180 (ralph.ps1:287) -> per-attempt timeout minutes*20 s, --max-redo 2", str(j.get("minutes")))

ck(os.path.isfile(GRAPHF), "runs/<id>/request.api.json exists (ralph.ps1:286)", GRAPHF)
ck(not os.path.exists(os.path.join(RUN, ID + ".mp4")), "runs/<id>/<id>.mp4 absent, so no 'arm already rendered' refusal")
ck(not os.path.exists(os.path.join(W, "p7", "jobs", ID + ".result.json")), "p7/jobs/<id>.result.json absent, so no 'id already used' refusal")

b = json.load(open(BUDGET, encoding="utf-8"))
# the caps live in the param() block (ralph.ps1:49 = [int]$GpuCapMin=615, [int]$JobMax=45); the
# [int]\$-anchored pattern is needed because "-GpuCapMin" also appears in prose, where a loose
# "GpuCapMin[^=]*=" search runs past the line and captures an unrelated number (it found 375 here).
caps = "\n".join(l for l in lines if l.startswith("param("))
cap_min = int(re.search(r"\[int\]\$GpuCapMin\s*=\s*(\d+)", caps).group(1))
job_max = int(re.search(r"\[int\]\$JobMax\s*=\s*(\d+)", caps).group(1))
print(f"budget {b['used_min']} min / {b['jobs']} jobs; ralph.ps1 param caps {cap_min} min / {job_max} jobs "
      f"(STOP_RALPH asks for -GpuCapMin 700 -JobMax 55 at relaunch); budget file caps "
      f"{b.get('cap_min')}/{b.get('job_cap')}")
ck(float(b["used_min"]) < cap_min, "used_min is under the cap", f"{b['used_min']} < {cap_min}")
ck(int(b["jobs"]) < job_max, "jobs is under the cap", f"{b['jobs']} < {job_max}")

tk = open(TASKS, encoding="utf-8", errors="replace").read()
ck(ID in tk, "ReqTicked (ralph.ps1:307): TASKS.md names the id")
# ONE-LINE tests: an early ticked line must not satisfy the B2 check (a [.]*.*ID regex matched across
# lines on the first run, which made this check vacuous).
mine = [l for l in tk.splitlines() if ID in l]
ck(len(mine) >= 1 and all("- [x]" in l for l in mine), f"every TASKS.md line naming the id is ticked - [x]",
   f"{len(mine)} line(s)")
ck(not any("BLOCKED" in l.upper() for l in mine), "no B2 line carries a BLOCKED note", " | ".join(l.strip()[:60] for l in mine))
# Control chars in a task line are a real fault, not cosmetics: a non-raw Python string with a C:\ path
# turns "\ali173" into \a (0x07), "\bakeoff" into \b (0x08) and "\request" into \r (0x0d), which SPLITS
# the line for splitlines()/the harness's line regexes - my first B2 tick did exactly that and the tick
# check below saw three fragments, one unticked. A ticked line must be ONE line with no control chars.
cctrl = [c for c in (mine[0] if mine else "") if ord(c) < 32 or ord(c) == 127]
ck(not cctrl, "the B2 task line is one physical line with no control chars (a \\a \\b \\r from a C:\\ path "
             "splits it and breaks ReqTicked)",
   f"{len(cctrl)} control char(s)" + (f" {[hex(ord(c)) for c in sorted(set(cctrl))]}" if cctrl else ""))
_v = "- [x] B2 CONTINUUM C:" + chr(13) + "ali173_cont_hc1_s51140001"      # the exact bug shape
print(f"PROBE {'FIRED ' if any(ord(c) < 32 for c in _v) else 'SILENT'} a \\r from a C:\\ path in a task line "
      f"is caught by this check ({'rejected' if any(ord(c) < 32 for c in _v) else 'ACCEPTED - VACOUS'})")

for f in (GRAPHF, STAGED):
    r = subprocess.run([sys.executable, "-m", "json.tool", f], capture_output=True, text=True)
    ck(r.returncode == 0, f"json.tool accepts {os.path.basename(f)} (the harness CHECK)", r.stderr.strip()[:120])

# self-destruct for the tick check (Learnings: a green check that cannot fail is worthless): the same
# predicate must be False for an unticked line, and it must not be satisfied by another line's tick.
def ticked(text):
    ms = [l for l in text.splitlines() if ID in l]
    return len(ms) >= 1 and all("- [x]" in l for l in ms)


p1 = ticked(f"- [x] OTHER LINE s51140001 BAKEOFF START.\n- [ ] B2 CONTINUUM {ID} seed {ID[-8:]}.")
p2 = ticked(f"- [x] B2 CONTINUUM {ID} seed {ID[-8:]}.")
print(f"PROBE {'FIRED ' if not p1 else 'SILENT'} tick check is per-line (an earlier tick must not cover B2: "
      f"{'rejected' if not p1 else 'ACCEPTED - VACOUS'})")
print(f"PROBE {'FIRED ' if p2 else 'SILENT'} tick check accepts a real tick ({'accepted' if p2 else 'REJECTED - VACOUS'})")
ck(not p1 and p2, "tick check discriminates unticked vs ticked for this exact id")

print("VERDICT:", "ALL GATES GREEN - the staged job is submittable" if not fails else f"BLOCKED by: {fails}")
sys.exit(0 if not fails else 1)
