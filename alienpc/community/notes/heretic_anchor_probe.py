"""One-shot: print the real anchor slugs a new sheet row may key.

emit_rows() matches `sheet.get("+" + it["slug"])`, and a slug is slugify(item id, base-plan line)
(notes/ali14d_shortplan_build.py:196) - it is COMPUTED from the base plan, not grepped from it, so the
only way to know a valid anchor is to run the builder's own item pass. This does that read-only.
"""
import importlib.util
import subprocess
import sys

BUILDER = "C:/Users/derek/5slock/ralph-community/notes/ali14d_shortplan_build.py"
spec = importlib.util.spec_from_file_location("spb", BUILDER)
spb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(spb)

base = subprocess.run(["git", "-C", "C:/Users/derek/5slock/ralph-community", "show", "HEAD:fix_plan.md"],
                      capture_output=True).stdout
raw, clean = spb.decode_lines(base)
buckets = spb.bucketize(clean) if hasattr(spb, "bucketize") else None
if buckets is None:
    names = [n for n in dir(spb) if not n.startswith("_")]
    print("no bucketize; module functions:", names)
    raise SystemExit(1)
items = spb.items_of(buckets)
print("base items=%d" % len(items))
for it in items:
    if any(k in it["id"] for k in ("3.18", "3.17", "CK-ATTN", "E5", "TOP-SCENE", "4.1", "3.19", "2.4", "PM2")):
        print("ANCHOR-CANDIDATE slug=%s id=%s line=%d tick=%s" %
              (it["slug"], it["id"], it["start"] + 1, it["tick"]))
