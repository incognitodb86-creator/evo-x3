# ALI-147 FIX4_REQ: prove the .bak -> new diff is the clips_json pair ONLY. READ-ONLY probe.
import json, os, difflib, builtins

D = r"C:/AI/community/runs/ali147_pool_fix4_s51080000"
OLD = os.path.join(D, "request.api.json.bak-20261022-fix4graph")
NEW = os.path.join(D, "request.api.json")
ga = json.load(open(OLD, encoding="utf-8"))
gb = json.load(open(NEW, encoding="utf-8"))
J = lambda x: json.dumps(x, sort_keys=True)
changed_nodes = sorted(k for k in set(ga) | set(gb) if J(ga.get(k)) != J(gb.get(k)))
import hashlib
print("old sha256", hashlib.sha256(open(OLD, "rb").read()).hexdigest(), os.path.getsize(OLD))
print("new sha256", hashlib.sha256(open(NEW, "rb").read()).hexdigest(), os.path.getsize(NEW))
print("changed top-level nodes:", changed_nodes)
print("byte-identical node count:", sum(1 for k in set(ga) | set(gb) if J(ga.get(k)) == J(gb.get(k))), "of", len(set(ga) | set(gb)))
for k in changed_nodes:
    ia, ib = ga[k]["inputs"], gb[k]["inputs"]
    print("node", k, ga[k]["class_type"], "changed input keys:", sorted(n for n in set(ia) | set(ib) if J(ia.get(n)) != J(ib.get(n))))
    for n in sorted(set(ia) | set(ib)):
        if J(ia.get(n)) == J(ib.get(n)):
            continue
        if n == "clips_json":
            ca, cb = json.loads(ia[n])["clips"], json.loads(ib[n])["clips"]
            for i, (x, y) in enumerate(zip(ca, cb), 1):
                dk = sorted(m for m in set(x) | set(y) if J(x.get(m)) != J(y.get(m)))
                print("   clip_%d changed keys %s validated %s -> %s duration %s -> %s seed %s -> %s" % (i, dk, x.get("validated"), y.get("validated"), x.get("duration"), y.get("duration"), x.get("seed"), y.get("seed")))
            print("   clips_json identical after dropping validated/duration:", all(J({m: v for m, v in x.items() if m not in ("validated", "duration")}) == J({m: v for m, v in y.items() if m not in ("validated", "duration")}) for x, y in zip(ca, cb)))
        else:
            print("   input", n, "old", repr(ia.get(n))[:120], "new", repr(ib.get(n))[:120])
text_a = open(OLD, encoding="utf-8").read().replace("\r\n", "\n").splitlines()
text_b = open(NEW, encoding="utf-8").read().replace("\r\n", "\n").splitlines()
ud = [l for l in difflib.unified_diff(text_a, text_b, lineterm="") if l[:1] in "-+" and l[:3] not in ("---", "+++")]
print("unified diff -/+ lines:", len(ud), "removed", sum(1 for l in ud if l[0] == "-"), "added", sum(1 for l in ud if l[0] == "+"))
dif = [l for l in open(os.path.join(D, "graph_diff.txt"), encoding="utf-8").read().splitlines() if l[:1] in "-+" and l[:3] not in ("---", "+++")]
print("graph_diff.txt -/+ lines:", len(dif), "removed", sum(1 for l in dif if l[0] == "-"), "added", sum(1 for l in dif if l[0] == "+"))
print("graph_diff.txt matches the rebuilt diff:", [l.rstrip("\n") for l in dif] == [l.rstrip("\n") for l in ud])
