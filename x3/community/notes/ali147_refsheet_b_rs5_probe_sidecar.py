r"""ali147_refsheet_b_rs5_probe_sidecar.py - read-only probe for RS5's prompt provenance check.

RS5 must show that arm 5b's chunk-1 prompt differs from the REFSHEET arm's chunk-1 prompt ONLY in the
subject_definitions block. The base run's sidecar text
  runs\\p7_r2_c3_pmot_full_pool\\prompts\\p7_r2_c3_pmot_full_pool_seg1_c0_long_r2v.txt
is that chunk-1 text (RS0 compared it with the base graph's c0 prompt and printed MATCH). This prints the two hashes
(raw bytes and EOL-normalised) and the first differing offset, so the builder's provenance check is written against
measured bytes, not a guess. Read-only; no writes.
"""
import hashlib
import json

SIDECAR = r"C:\AI\community\runs\p7_r2_c3_pmot_full_pool\prompts\p7_r2_c3_pmot_full_pool_seg1_c0_long_r2v.txt"
GRAPH = r"C:\AI\community\runs\ali147_pool_refsheet_s51080000\request.api.json"

raw = open(SIDECAR, "rb").read()
t = open(SIDECAR, encoding="utf-8", newline="").read()
p = json.load(open(GRAPH, encoding="utf-8"))["c0"]["inputs"]["prompt"]

print("sidecar bytes=%d crlf=%d lf_only=%d" % (len(raw), raw.count(b"\r\n"), raw.count(b"\n")))
print("sidecar raw sha256      = %s" % hashlib.sha256(raw).hexdigest())
for name, s in (("as-read(text)", t), ("crlf->lf", t.replace("\r\n", "\n")), ("crlf->lf+rstrip", t.replace("\r\n", "\n").rstrip("\n"))):
    print("%-16s len=%d sha256=%s" % (name, len(s), hashlib.sha256(s.encode("utf-8")).hexdigest()))
print("graph c0 prompt   len=%d sha256=%s" % (len(p), hashlib.sha256(p.encode("utf-8")).hexdigest()))

a = t.replace("\r\n", "\n")
b = p
print("equal after EOL fold:", a == b)
if a != b:
    i = next((k for k in range(min(len(a), len(b))) if a[k] != b[k]), min(len(a), len(b)))
    print("first diff at %d" % i)
    print("sidecar[%d:%d] = %r" % (max(0, i - 60), i + 60, a[max(0, i - 60):i + 60]))
    print("graph  [%d:%d] = %r" % (max(0, i - 60), i + 60, b[max(0, i - 60):i + 60]))
    print("len sidecar=%d len graph=%d delta=%d" % (len(a), len(b), len(a) - len(b)))
    print("tail sidecar=%r" % a[-40:])
    print("tail graph =%r" % b[-40:])
