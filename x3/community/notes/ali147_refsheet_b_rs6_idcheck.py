r"""RS6 read-only check (CPU only, no GPU call): does the LIVE ralph.ps1 accept the
REFSHEET_B job id, and is the budget gate open?

v2 (2026-10-22, RS6 re-request): v1 hardcoded the two patterns from memory and reported the
underscore in "refsheet_b" as unmatchable. After Max Architect widened the gates (~18:52 CT,
ralph.ps1.bak-20261022-idregex), a hardcoded copy can only confirm the old bug. This version
PARSES the two -notmatch patterns out of the live ralph.ps1:
  gate 1 (all kinds):  line with  P7 job refused: bad id
  gate 2 (graph/dip):  line with  graph/dip ids are ali147_pool_<arm>_s<seed>
and prints the verdict for each id, plus the budget gate ralph.ps1:187-188 reads
(used_min vs cap_min, jobs vs job_cap) from ralph-community\logs\p7_budget.json.
Prints only; writes nothing. Run: python notes/ali147_refsheet_b_rs6_idcheck.py
"""
import json
import re

RALPH = r"C:/Users/derek/5slock/ralph-community/ralph.ps1"
BUDGET = r"C:/Users/derek/5slock/ralph-community/logs/p7_budget.json"
ARM_ID = "ali147_pool_refsheet_b_s51080000"

IDS = [
    "ali147_pool_ctrl_s51080000",        # rendered (CTRL)
    "ali147_pool_refsheet_s51080000",    # rendered (RS4) - arm segment has no underscore
    ARM_ID,                              # RS5/RS6 arm - the id TASKS.md names
    "ali147_pool_dip_s51080000",         # rendered (DIP)
]

lines = open(RALPH, encoding="utf-8", errors="replace").read().splitlines()
gates = {}
for n, line in enumerate(lines, 1):
    if "-notmatch" in line and ("refused: bad id" in line or "graph/dip ids are" in line):
        key = "gate1_all_kinds" if "refused: bad id" in line else "gate2_graph_dip"
        gates[key] = (n, re.search(r"-notmatch '([^']+)'", line).group(1))

print("ralph.ps1 gates read from the live file:")
for key in ("gate1_all_kinds", "gate2_graph_dip"):
    if key in gates:
        print("  %s  ralph.ps1:%d  %s" % (key, gates[key][0], gates[key][1]))
    else:
        print("  %s NOT FOUND in ralph.ps1 - check the harness" % key)

ok = True
for i in IDS:
    verdicts = []
    for key in ("gate1_all_kinds", "gate2_graph_dip"):
        if key not in gates:
            verdicts.append("n/a")
            ok = False
            continue
        v = bool(re.match(gates[key][1], i))
        verdicts.append(str(v))
        if i == ARM_ID and not v:
            ok = False
    print("%-38s gate1=%-5s gate2=%-5s" % (i, verdicts[0], verdicts[1]))

b = json.load(open(BUDGET, encoding="utf-8-sig"))
print("budget file", BUDGET)
print("  used_min", b.get("used_min"), "cap_min", b.get("cap_min"),
      "jobs", b.get("jobs"), "job_cap", b.get("job_cap"), "updated", b.get("updated"))
gate_open = float(b["used_min"]) < float(b["cap_min"]) and int(b["jobs"]) < int(b["job_cap"])
print("  ralph.ps1:187-188 budget/job-cap gate open:", gate_open)

print("ARM ID ACCEPTED BY BOTH LIVE GATES, BUDGET GATE OPEN" if (ok and gate_open)
      else "STILL REFUSED - do not re-request")
