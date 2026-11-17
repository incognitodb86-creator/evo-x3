"""ALI-147 FINAL summary - graph provenance compare (read-only, CPU only).

For each arm: sha256 + size of the arm's request.api.json (what Forge wrote) vs
the harness-written <id>.api.json (what actually rendered). Byte-equal means the
rendered graph is the authored graph. Writes
notes/ali147-summary-api-20261022.txt.
"""
import hashlib
import os

RUNS = r"C:\AI\community\runs"
OUT = r"C:\AI\community\notes\ali147-summary-api-20261022.txt"

ARMS = [
    ("CTRL", "ali147_pool_ctrl_s51080000"),
    ("FIX1", "ali147_pool_fix1_s51080000"),
    ("FIX5", "ali147_pool_fix5_s51080000"),
    ("DIP", "ali147_pool_dip_s51080000"),
    ("FIX4", "ali147_pool_fix4_s51080000"),
    ("REFSHEET", "ali147_pool_refsheet_s51080000"),
    ("REFSHEET_B", "ali147_pool_refsheet_b_s51080000"),
]


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


lines = []


def w(s):
    lines.append(s)
    print(s)


w("ALI-147 graph provenance (request.api.json vs harness <id>.api.json)")
for name, arm in ARMS:
    d = os.path.join(RUNS, arm)
    req = os.path.join(d, "request.api.json")
    cap = os.path.join(d, arm + ".api.json")
    w("")
    w("%s %s" % (name, arm))
    for p in (req, cap):
        if os.path.exists(p):
            w("  %s size=%d sha256=%s" % (p, os.path.getsize(p), sha(p)))
        else:
            w("  %s ABSENT" % p)
    if os.path.exists(req) and os.path.exists(cap):
        a = open(req, "rb").read()
        b = open(cap, "rb").read()
        w("  byte-equal=%s" % (a == b))
        if a != b and (b.startswith(a) or a.startswith(b)):
            w("  byte-prefix=%s (larger file has a %d-byte tail)"
              % (True, max(len(a), len(b)) - min(len(a), len(b))))
        w("  CRLF in request=%s CRLF in captured=%s"
          % (b"\r\n" in a, b"\r\n" in b))

with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(lines) + "\n")
print("WROTE %s bytes=%d" % (OUT, os.path.getsize(OUT)))
