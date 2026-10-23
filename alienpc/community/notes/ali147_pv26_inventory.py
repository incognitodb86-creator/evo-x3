import os
FILES = [
 r"C:/AI/community/notes/ali147-report-pv2-20261023.md",
 r"C:/AI/community/notes/ali147-pv26-report-probe-20261023.txt",
 r"C:/AI/community/notes/ali147-pv26-card-probe-20261023.txt",
 r"C:/AI/community/notes/ali147-pv26-settings-20261023.txt",
 r"C:/AI/community/notes/ali147-pv26-commits-20261023.txt",
 r"C:/AI/community/runs/ali147_pool_promptv2_s51080000/REPORT_pv2.md",
]
tot = 0
for f in FILES:
    n = os.path.getsize(f)
    tot += n
    print(n, f)
print("TOTAL", tot, "files", len(FILES))
