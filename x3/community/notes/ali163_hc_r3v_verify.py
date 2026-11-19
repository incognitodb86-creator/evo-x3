"""ALI-163 R3V VERIFY SHEETS - read-only probe (no GPU, no writes outside notes/).

Checks:
 1. the sheet job result.json / status.log / objective.json (ok, rc, secs)
 2. every expected SaveImage prefix from the graph exists as a png in
    ComfyUI\output\community\hc_sheets, with PIL size + sha256 + bytes
 3. provenance: cmp request.api.json vs <id>.api.json (byte prefix)
 4. the LoadImage resolution rule, read out of the REAL source on this box
    (comfy_extras/nodes.py LoadImage.get_files / validate_image_file_existence /
     folder_paths.get_annotated_filepath / is_within_directory) and the live
    candidate strings, so "sheet placement" is proved, not asserted
 5. what is already placed in ComfyUI\input\community\hc (for R4-R9)
 6. live budget (logs\p7_budget.json) for the R4 gate
Prints PASS/FAIL lines. Never calls the network, never the GPU.
"""
import hashlib
import json
import os
import re

CUI = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI"
INP = os.path.join(CUI, "input")
OUT = os.path.join(CUI, "output")
SHEETS = os.path.join(OUT, "community", "hc_sheets")
HCIN = os.path.join(INP, "community", "hc")
RUN = r"C:\AI\community\runs\ali147_pool_hc_sheet_s51120000"
ID = "ali147_pool_hc_sheet_s51120000"
RES = r"C:\AI\community\p7\jobs\ali147_pool_hc_sheet_s51120000.result.json"
BUD = r"C:\Users\derek\5slock\ralph-community\logs\p7_budget.json"
PICKS = r"C:\AI\community\notes\hc_sheets_map_20261023.md"

fails = []


def chk(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (" | " + detail if detail else ""))
    if not ok:
        fails.append(name)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def size(p):
    img = __import__("PIL.Image", fromlist=["open"]).open(p)
    return img.size, img.mode, img.format


# --- 1 job record -----------------------------------------------------------
res = json.load(open(RES, encoding="utf-8-sig"))
chk("result.json ok/rc", res.get("ok") is True and res.get("rc") == 0,
    "ok=%s rc=%s wall_min=%s started=%s finished=%s" % (res.get("ok"), res.get("rc"), res.get("wall_min"), res.get("started"), res.get("finished")))
st = open(os.path.join(RUN, "status.log"), encoding="utf-8").read()
chk("status.log JOB end ok + image objective",
    "JOB end %s ok" % ID in st and "OBJECTIVE ok" in st,
    " | ".join(x.strip() for x in st.strip().splitlines()[-3:]))
obj = json.load(open(os.path.join(RUN, "objective.json"), encoding="utf-8"))
a = obj["attempts"][0]
chk("objective image 1152x2016 1 packet bytes>0",
    obj.get("image") is True and a["w"] == 1152 and a["h"] == 2016 and a["frames"] == 1 and a["bytes"] > 0,
    "size=%dx%d frames=%s bytes=%s secs=%s audio=%s" % (a["w"], a["h"], a["frames"], a["bytes"], a["secs"], a["audio"]))

# --- 2 the 10 chains' save prefixes vs the 10 pngs --------------------------
g = json.load(open(os.path.join(RUN, "request.api.json"), encoding="utf-8"))
prefixes = sorted(v["inputs"]["filename_prefix"] for k, v in g.items() if v.get("class_type") == "SaveImage")
chk("graph has 10 SaveImage chains", len(prefixes) == 10, str(prefixes))
files = {}
for root, _dirs, fns in os.walk(SHEETS):
    for fn in fns:
        if fn.lower().endswith(".png"):
            files[os.path.join(root, fn)] = None
chk("10 sheet pngs on disk in output\\community\\hc_sheets", len(files) == 10, str(len(files)))
rows = []
for pre in prefixes:
    want = pre.split("/")[-1] + "_00001_.png"
    hits = [p for p in files if os.path.basename(p) == want]
    if len(hits) != 1:
        chk("sheet exists " + want, False, "hits=%d" % len(hits))
        continue
    p = hits[0]
    (w, h), mode, fmt = size(p)
    rows.append({"prefix": pre, "name": want, "path": p, "w": w, "h": h,
                 "mode": mode, "format": fmt, "bytes": os.path.getsize(p), "sha": sha(p)})
chk("all 10 save prefixes have exactly one png", len(rows) == 10, str(len(rows)))
chk("all sheets 1152x2016 RGB PNG = RS016 shape",
    all(r["w"] == 1152 and r["h"] == 2016 and r["mode"] == "RGB" and r["format"] == "PNG" for r in rows),
    str(sorted({(r["w"], r["h"], r["mode"]) for r in rows})))
chk("all sheet sha256 = 64 hex", all(len(r["sha"]) == 64 and re.fullmatch(r"[0-9a-f]{64}", r["sha"]) for r in rows))

# --- 3 provenance: the graph that rendered is mine --------------------------
raw_a = open(os.path.join(RUN, "request.api.json"), "rb").read()
raw_b = open(os.path.join(RUN, ID + ".api.json"), "rb").read()
ga = json.loads(raw_a.decode("utf-8-sig"))
gb = json.loads(raw_b.decode("utf-8-sig"))
diff = [k for k in set(ga) | set(gb) if json.dumps(ga.get(k), sort_keys=True) != json.dumps(gb.get(k), sort_keys=True)]
chk("rendered <id>.api.json == request.api.json (node-body compare)", ga.keys() == gb.keys() and not diff,
    "req=%d B (crlf=%d, lf=%d, trailing_nl=%s) api=%d B (crlf=%d, lf=%d, trailing_nl=%s) nodekeys=%d/%d diffnodes=%s reqsha=%s apisha=%s" % (
        len(raw_a), raw_a.count(b"\r\n"), raw_a.count(b"\n"), raw_a.endswith(b"\n"),
        len(raw_b), raw_b.count(b"\r\n"), raw_b.count(b"\n"), raw_b.endswith(b"\n"),
        len(ga), len(gb), diff, sha(os.path.join(RUN, "request.api.json"))[:16], sha(os.path.join(RUN, ID + ".api.json"))[:16]))
print("api.json first 200 B:", raw_b[:200])
print("request.api.json first 200 B:", raw_a[:200])

# --- 4 the real LoadImage resolution rule ----------------------------------
nodes = open(os.path.join(CUI, "nodes.py"), encoding="utf-8", errors="replace").read().splitlines()
fp = open(os.path.join(CUI, "folder_paths.py"), encoding="utf-8", errors="replace").read().splitlines()
print("nodes.py has class LoadImage:", "class LoadImage" in "\n".join(nodes))


def src(lines, pat, n=14):
    out = []
    for i, L in enumerate(lines):
        if pat in L:
            out.append(":%d %s" % (i + 1, L.rstrip()))
            for j in range(i + 1, min(i + 1 + n, len(lines))):
                nx = lines[j].rstrip()
                if nx and not nx.startswith((" ", "\t", ")", "]", "}")) and out and not nx.endswith(":"):
                    break
                out.append(":%d %s" % (j + 1, nx))
            break
    return "\n".join(out)


print("--- comfy_extras/nodes.py LoadImage ---")
print(src(nodes, "class LoadImage"))
print("--- folder_paths.get_annotated_filepath ---")
print(src(fp, "def get_annotated_filepath"))
print("--- folder_paths.is_within_directory ---")
print(src(fp, "def is_within_directory"))

abs_out = [os.path.join(SHEETS, r["name"]) for r in rows]
cands = []
for r in rows:
    cands.append(("output-rooted rel", "community/hc_sheets/" + r["name"]))
    cands.append(("absolute output path", os.path.join(SHEETS, r["name"])))
    cands.append(("proposed input/hc target", "community/hc/" + r["name"]))
print("--- nodes.py LoadImage.load_image / validate (the runtime resolution) ---")
print(src(nodes, "def load_image", 8))
print(src(nodes, "def validate_image_file_existence", 6))
print(src(fp, "def annotated_filepath", 16))
print("--- candidate LoadImage strings (resolution against get_input_directory) ---")
resc = []
for kind, s in cands:
    if os.path.isabs(s):
        # an absolute string reaches folder_paths.get_annotated_filepath, which
        # hard-requires is_within_directory(get_input_directory(), path): a path
        # under ComfyUI\output is NOT within ComfyUI\input -> ValueError
        exists = os.path.isfile(s) and os.path.realpath(s).lower().startswith(os.path.realpath(INP).lower() + os.sep)
    else:
        exists = os.path.isfile(os.path.join(INP, s))
    resc.append((kind, s, exists))
for kind, s, exists in resc[:12]:
    print("%-22s resolves_in_input=%-5s %s" % (kind, exists, s))
chk("no output sheet resolves inside ComfyUI\\input (needs placement)",
    not any(e for _k, _s, e in resc if _k in ("output-rooted rel", "absolute output path")),
    "input dir=%s; %d candidate strings tested, output-rooted/absolute all absent from input" % (INP, len(resc)))
prop = [e for _k, s, e in resc if s.startswith("community/hc/") for e in [e]]
chk("proposed community/hc/<sheet>.png NOT yet placed (Max copy needed)", not any(prop),
    "target dir=%s (exists=%s)" % (HCIN, os.path.isdir(HCIN)))
print("input\\community\\hc contents (placed picks):")
for fn in sorted(os.listdir(HCIN)) if os.path.isdir(HCIN) else []:
    print("  " + fn + " %d B sha %s" % (os.path.getsize(os.path.join(HCIN, fn)), sha(os.path.join(HCIN, fn))[:16]))
print("input\\community subdirs:", sorted(d for d in os.listdir(os.path.join(INP, "community")) if os.path.isdir(os.path.join(INP, "community", d))))
for root, dirs, fns in os.walk(INP):
    for fn in fns:
        if "HC" in fn.upper() and fn.lower().endswith(".png"):
            print("EXISTING input png: %s" % os.path.join(root, fn))

# --- 5 R4-R9 id gates + budget ---------------------------------------------
ralph = open(r"C:\Users\derek\5slock\ralph-community\ralph.ps1", encoding="utf-8-sig").read()
pats = [p.split("'", 2)[1] for p in re.findall(r"-notmatch\s*'[^']+'", ralph) if "ali147_pool" in p]
ids = ["ali147_pool_hc_r%d_s5113000%d" % (i, i) for i in range(1, 7)]
chk("R4-R9 ids accepted by live ralph.ps1 gates", all(re.fullmatch(p, i) for p in pats for i in ids), str(pats))
bud = json.load(open(BUD, encoding="utf-8-sig"))
print("budget:", json.dumps(bud))

print()
print("RESULT:", "ALL CHECKS PASS" if not fails else "FAILS " + str(fails))
print()
print("=== SHEETS TABLE for notes\\hc_redo_research_20261023.md '## Sheets' ===")
for r in sorted(rows, key=lambda x: x["name"]):
    print("%s | %dx%d %s %s | %d B | %s | src=%s | LoadImage(needed) = community/hc/%s" %
          (r["name"], r["w"], r["h"], r["mode"], r["format"], r["bytes"], r["sha"], r["path"], r["name"]))
print("sheet-job sha256 graph:", sha(os.path.join(RUN, "request.api.json")))
print("rendered graph <id>.api.json sha256:", sha(os.path.join(RUN, ID + ".api.json")))
print("harness copy sha256:", sha(os.path.join(RUN, ID + ".png")))
print("picks map notes exists:", os.path.isfile(PICKS))
