import os, hashlib, datetime
NOTES = r"C:/AI/community/notes"
F = [
 "ali147_pv26_report_probe.py", "ali147_pv26_card_probe.py", "ali147_pv26_settings.py",
 "ali147_pv26_commits.py", "ali147_pv26_linerepr.py", "ali147_pv26_inventory2.py",
 "ali147-pv26-report-probe-20261023.txt", "ali147-pv26-card-probe-20261023.txt",
 "ali147-pv26-settings-20261023.txt", "ali147-pv26-commits-20261023.txt",
 "ali147-report-pv2-20261023.md", "ali147_REPORT_pv2.md",
]
EXTRA = [r"C:/AI/community/runs/ali147_pool_promptv2_s51080000/REPORT_pv2.md"]
L = ["ALI-147 PV2-6 file inventory - %s (read-only; this file lists the report + probe files this iteration wrote)"
     % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
tot = 0
n = 0
for f in F:
    p = os.path.join(NOTES, f)
    if os.path.exists(p):
        b = open(p, "rb").read()
        tot += len(b); n += 1
        L.append("%10d  %s  %s" % (len(b), hashlib.sha256(b).hexdigest()[:16], p))
    else:
        L.append("MISSING %s" % p)
for p in EXTRA:
    b = open(p, "rb").read()
    tot += len(b); n += 1
    L.append("%10d  %s  %s  (report copy outside notes\\, from the earlier PV2-6 line text; kept, no deletes)" % (len(b), hashlib.sha256(b).hexdigest()[:16], p))
L.append("TOTAL %d files %d bytes" % (n, tot))
# the AGENTS.md Learnings section line count (the 15-line cap check)
ag = open(r"C:/Users/derek/5slock/AGENTS.md", encoding="utf-8").read().splitlines()
i = ag.index("## Learnings (ALI-160, Huntley Ralph pattern; one short operational line each, max 15 lines; Max prunes at review)") if any(s.startswith("## Learnings") for s in ag) else None
cnt = 0
if i is not None:
    for s in ag[i + 1:]:
        if s.startswith("#"):
            break
        if s.strip().startswith("- "):
            cnt += 1
L.append("AGENTS.md Learnings bullet lines = %d (cap 15)" % cnt)
with open(os.path.join(NOTES, "ali147-pv26-inventory-20261023.txt"), "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(L) + "\n")
print("\n".join(L[-3:]))
