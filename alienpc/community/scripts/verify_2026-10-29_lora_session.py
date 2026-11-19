r"""verify_2026-10-29_lora_session.py - double-check of everything claimed today, plus a full state snapshot for the
restart handoff (notes/2026-10-29-lora-session-state-for-restart.md). Read-only: nothing is written, moved or deleted.

Checks:
 1. the 7 alias copies in C:\AI\lora\person_alias_2026-10-29: bytes + SHA-256 vs the E: snapshot source, via
    MANIFEST_alias.csv (re-derives every row from the files, not from the log)
 2. the one file placed in the live ComfyUI models\loras: SHA-256 must equal the H3 source
 3. the E: snapshot tree is still intact (file count + total bytes vs its own MANIFEST.csv arithmetic)
 4. community provenance claims stated today, compared by SHA-256 against the Hugging Face file listings
    (HF tree API returns lfs.oid = SHA-256 for LFS files): our klein_snofs_v1_4 vs Se0ulSeeker/
    flux2_klein_9b_nsfw_loras, and every file in models\loras vs the Hearmeman H3 pack.
Usage: python verify_2026-10-29_lora_session.py
"""
import csv, hashlib, json, urllib.request
from pathlib import Path

ALIAS = Path(r"C:\AI\lora\person_alias_2026-10-29")
SRC = Path(r"E:\Backups\AlienPc-C-2026-10-26\Users\derek\Desktop\_TO_DELETE_celeb-lora-lineage_2026-10-17")
LORAS = Path(r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\models\loras")
UA = {"User-Agent": "pi-alienpc (read-only verify)"}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


CACHE = {}


def sha_cached(p):
    p = str(p)
    if p not in CACHE:
        CACHE[p] = sha(p)
    return CACHE[p]


def hf_tree(repo, sub=""):
    u = "https://huggingface.co/api/models/%s/tree/main%s?recursive=true" % (repo, ("/" + sub) if sub else "")
    try:
        return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=45).read())
    except Exception as e:
        return [{"_err": repr(e)[:120]}]


print("### 1. alias copies vs the snapshot source (through MANIFEST_alias.csv)")
ok = bad = 0
for r in csv.DictReader(open(ALIAS / "MANIFEST_alias.csv", encoding="utf-8")):
    t, s = r.get("target"), r.get("source")
    if not t:
        print("   skip-duplicate row:", r["source_sha256"][:16], "|", r["status"]); continue
    a, b = (sha_cached(t) if Path(t).exists() else "-"), (sha_cached(s) if Path(s).exists() else "-")
    good = a == b == r["source_sha256"]
    ok, bad = ok + good, bad + (not good)
    print("   %-8s %-38s %13s %s" % ("OK" if good else "MISMATCH", Path(t).name, Path(t).stat().st_size, a[:16]))
print("   -> copies verified: %d, mismatched: %d" % (ok, bad))

srcd = SRC / r"LORA_ARCHIVE_NOT_IN_USE_2026-10-09\HardcoreNSFW-TestRuntime\ComfyUI\models\loras"
src = sorted(srcd.glob("MM-H3*.safetensors"))[0]   # the real-person file name is not written in a git-tracked file
print("\n### 2. the live models\\loras file")
lt = LORAS / "FC_SYDNEY_h3_face_v1.safetensors"

print("   present=%s size=%s sha=%s  == source(%s): %s" % (lt.exists(), lt.stat().st_size, sha_cached(lt)[:16],
      src.name, sha_cached(lt) == sha_cached(src)))

print("\n### 3. snapshot tree integrity (file count / bytes vs its own MANIFEST.csv)")
files = [f for f in SRC.rglob("*") if f.is_file()]
tot = sum(f.stat().st_size for f in files)
m = list(csv.DictReader(open(SRC / "MANIFEST.csv", encoding="utf-8")))
msum = sum(int(x["bytes"]) for x in m if x["bytes"].isdigit())
own = (SRC / "MANIFEST.csv").stat().st_size + (SRC / "NOT_MOVED_inside-ComfyUI-folders.txt").stat().st_size
print("   manifest rows=%d manifest_bytes=%d" % (len(m), msum))
print("   on_disk files=%d bytes=%d  extra=%d (expected = MANIFEST.csv + NOT_MOVED.txt = %d)" % (len(files), tot, tot - msum, own))
print("   integrity:", "EXACT" if tot - msum == own else "DIFFERS - investigate")

print("\n### 4. community provenance, compared by SHA-256 (HF lfs.oid vs our files)")
for repo, sub, ours in [("Se0ulSeeker/flux2_klein_9b_nsfw_loras", "loras", LORAS),
                        ("Hearmeman/minimax-h3-loras", "", LORAS)]:
    tr = hf_tree(repo, sub)
    mine = {g: sha_cached(g) for g in LORAS.glob("*.safetensors")}   # hash each local LoRA once
    print("\n== %s (local models\\loras hashed: %d files)" % (repo, len(mine)))
    for f in tr:
        if f.get("_err"): print("   ", f["_err"]); break
        if not f["path"].endswith(".safetensors"): continue
        oid = (f.get("lfs") or {}).get("oid") or ""
        exact = [g.name for g, s in mine.items() if oid and s == oid]
        sizeonly = [g.name for g in mine if mine[g] and g.stat().st_size == f.get("size")]
        print("   %-46s %10s sha=%s  on-box: %s%s" % (f["path"], f.get("size"), (oid[:12] or "-"),
              exact or "-", ("(size-only match: %s)" % sizeonly) if (not exact and sizeonly) else ""))
