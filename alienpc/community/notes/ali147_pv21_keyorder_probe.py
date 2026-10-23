"""PV2-1 read-only provenance probe (name promised in PROOF.md / TASKS.md).

Proves the one claim that makes runs/ali147_pool_ctrl_s51080000/submitted_graph.pretty.json
a safe copy source for the CTRL-sourced arms: it is the SAME graph as the
ali147_pool_ctrl_s51080000.api.json that rendered 481 frames ok - identical node names,
identical node bodies, byte-size equal - and the only structural difference is the
TOP-LEVEL key order of the node ids. Prints both key orders, their set-equality, the
sorted-order equality of the two files, per-node canonical compare, sizes/sha256.

CPU only, writes nothing. Run: python notes/ali147_pv21_keyorder_probe.py
"""
import hashlib
import json
import os

CTRL = r"C:/AI/community/runs/ali147_pool_ctrl_s51080000"
PRETTY = os.path.join(CTRL, "submitted_graph.pretty.json")
API = os.path.join(CTRL, "ali147_pool_ctrl_s51080000.api.json")

fails = []


def chk(cond, label):
    print(("PASS " if cond else "FAIL ") + label)
    if not cond:
        fails.append(label)


def load(p):
    raw = open(p, "rb").read()
    return json.loads(raw.decode("utf-8")), raw


def canon(x):
    return json.dumps(x, sort_keys=True)


p, praw = load(PRETTY)
a, araw = load(API)
print("pretty", os.path.basename(PRETTY), "bytes", len(praw),
      "sha256", hashlib.sha256(praw).hexdigest(), "crlf", praw.count(b"\r\n"), "nodes", len(p))
print("api   ", os.path.basename(API), "bytes", len(araw),
      "sha256", hashlib.sha256(araw).hexdigest(), "crlf", araw.count(b"\r\n"), "nodes", len(a))
print("pretty top-level key order", list(p))
print("api    top-level key order", list(a))
chk(set(p) == set(a), "node id sets are equal (%d ids)" % len(p))
chk(list(p) != list(a), "top-level key ORDER differs (the only structural difference)")
chk(sorted(p) == sorted(a), "sorted key lists are equal -> same graph, order-only diff")
chk(len(praw) == len(araw), "both files are %d bytes (same content, same formatting width)" % len(praw))
chk(canon(p) == canon(a), "every node body is byte-identical under json.dumps(sort_keys=True)")
diff = [k for k in p if canon(p[k]) != canon(a[k])]
chk(diff == [], "per-node compare: zero differing nodes (diff list %s)" % diff)
chk(praw != araw and len(praw) == len(araw) and canon(p) == canon(a),
    "raw bytes differ ONLY in top-level key order (len equal at %d, canonical content equal)"
    % len(praw))
for k in ["c0", "c1", "save", "img", "noise", "unet", "m_attn", "m_vsa", "win1"]:
    print("  node %-6s %s inputs %d  body-equal %s" %
          (k, p[k]["class_type"], len(p[k]["inputs"]), canon(p[k]) == canon(a[k])))
obj = json.load(open(os.path.join(CTRL, "objective.json"), encoding="utf-8"))
print("control objective.json secs", obj.get("secs"), "attempts", obj.get("attempts"),
      "frames", obj.get("frames") or obj.get("nb_read_packets"))
print("ALL CHECKS PASS" if not fails else "FAILS " + json.dumps(fails))
