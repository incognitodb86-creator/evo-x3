"""PV2-1 graph_diff read-only check: the diff vs the CTRL graph must show EXACTLY the
three intended changes (c0.prompt, c1.prompt, save.filename_prefix) = 3 removed + 3 added
lines, with the hunk headers pointing at the c0 / c1 / save node blocks and nothing else.

Also: diff line counts by hunk, the -/+ pair keys, the new prefix line, and that the
context lines of the c0/c1 hunks contain no other prompt text.

Writes only notes/. Run: python notes/ali147_pv21_diffcheck.py
"""
import json
import os
import re
import hashlib

DIFF = r"C:/AI/community/runs/ali147_pool_promptv2_s51080000/graph_diff.txt"
SRC = r"C:/AI/community/runs/ali147_pool_ctrl_s51080000/submitted_graph.pretty.json"
DST = r"C:/AI/community/runs/ali147_pool_promptv2_s51080000/request.api.json"
NEW_ID = "ali147_pool_promptv2_s51080000"

fails = []
raw = open(DIFF, encoding="utf-8").read()
lines = raw.split("\n")


def chk(cond, label):
    print(("PASS " if cond else "FAIL ") + label)
    if not cond:
        fails.append(label)


minus = [l for l in lines if l.startswith("-") and not l.startswith("---")]
plus = [l for l in lines if l.startswith("+") and not l.startswith("+++")]
hunks = [l for l in lines if l.startswith("@@")]
print("bytes", os.path.getsize(DIFF), "sha256", hashlib.sha256(open(DIFF, 'rb').read()).hexdigest())
print("hunk_headers", hunks)
print("removed", len(minus), "added", len(plus))
chk(len(minus) == 3 and len(plus) == 3, "exactly 3 removed + 3 added lines (no other change in the file)")
chk(len(hunks) == 3, "3 hunks (one per edited line: c0, c1, save)")


def key_of(line):
    m = re.match(r'^[-+]\s+"([a-z0-9_.]+)":', line)
    return m.group(1) if m else None


keys = [key_of(l) for l in minus] + [key_of(l) for l in plus]
print("changed_keys", keys)
chk(keys == ["prompt", "prompt", "filename_prefix", "prompt", "prompt", "filename_prefix"],
    "removed/added lines are exactly prompt, prompt, filename_prefix (paired)")
chk(all(l.startswith('-   "prompt"') or l.startswith('+   "prompt"') for l in minus + plus if "prompt" in l[:12]),
    "prompt lines are at the node input indent (3 spaces)")
pre = [l for l in plus if "filename_prefix" in l]
chk(pre == ['+   "filename_prefix": "community/%s/%s",' % (NEW_ID, NEW_ID)],
    "the added prefix line is exactly the new id: " + json.dumps(pre))
ctx = [l for l in lines if l.startswith(" ") and '"prompt"' in l]
chk(not ctx, "no unchanged context line touches any prompt input (the prompts are fully replaced)")

# pairing: each removed prompt must equal the CTRL node's text, each added = the v2 file text
g = json.loads(open(DST, encoding="utf-8").read())
s = json.loads(open(SRC, encoding="utf-8").read())
ctrl_prompts = [s["c0"]["inputs"]["prompt"], s["c1"]["inputs"]["prompt"]]
new_prompts = [g["c0"]["inputs"]["prompt"], g["c1"]["inputs"]["prompt"]]
lines_of = lambda sign, node, key: ['%s   "%s": %s,' % (sign, key, json.dumps(json.loads(open(DST if sign == "+" else SRC, encoding="utf-8").read())[node]["inputs"][key], ensure_ascii=True))]
ctrl_prompt_lines = [lines_of("-", n, "prompt")[0] for n in ("c0", "c1")]
new_prompt_lines = [lines_of("+", n, "prompt")[0] for n in ("c0", "c1")]
chk(sorted(ctrl_prompt_lines) == sorted(l for l in minus if '"prompt"' in l),
    "every removed prompt line is byte-equal to a CTRL c0/c1 prompt line (with indent and comma)")
chk(sorted(new_prompt_lines) == sorted(l for l in plus if '"prompt"' in l),
    "every added prompt line is byte-equal to the graph's new c0/c1 prompt line (with indent and comma)")
for tgt, node in ((r"C:/AI/community/specs/prompt_v2/v2_seg1_c0_r2v.txt", "c0"),
                  (r"C:/AI/community/specs/prompt_v2/v2_seg1_c1_t2va.txt", "c1")):
    txt = open(tgt, encoding="utf-8").read()
    chk(g[node]["inputs"]["prompt"] == txt,
        "%s prompt == %s text exactly (chars %d, sha256 %s)"
        % (node, os.path.basename(tgt), len(txt), hashlib.sha256(txt.encode()).hexdigest()))
chk(g["c1"]["inputs"]["prompt"] != s["c1"]["inputs"]["prompt"], "c1 prompt differs from CTRL's")
print("ALL CHECKS PASS" if not fails else "FAILS " + json.dumps(fails))
