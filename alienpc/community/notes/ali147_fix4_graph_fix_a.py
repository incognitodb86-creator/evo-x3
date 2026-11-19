"""ALI-147 FIX4_GRAPH option (A) - edit the existing FIX4 graph in place (CPU only, no GPU).

Two changes only, per TASKS.md FIX4_GRAPH (Max Architect / Derrick 5:44 PM CT):
  1. "validated": false on all 6 clips in the Extender node's clips_json
     (a cold headless full_batch raises "Ref2VA clip 1 is marked Validated but its
      disk cache is missing" when validated is true - status.log 17:36:56, 3/3, 5.1 s).
  2. Grid-aligned clip lengths 243 + 5x260 frames (durations in seconds at 24 fps),
     i.e. 1543 raw frames, 1543 - 5x22 Motion Context overlap = 1433 kept frames,
     inside frames_tol 24 of 1443. See notes\ali147-fix4-graph-20261022.md finding 2.
Nothing else changes: the file is re-dumped with the builder's exact formatting
(json.dump indent=1, ensure_ascii=True + trailing newline), so a byte diff vs the
.bak shows only the clips_json string.

Run:  python C:/AI/community/notes/ali147_fix4_graph_fix_a.py
"""

import json
import os

ARM = r"C:/AI/community/runs/ali147_pool_fix4_s51080000"
SRC = os.path.join(ARM, "request.api.json")   # edited in place (bak taken first)
BAK = SRC + ".bak-20261022-fix4graph"
OUT_DIR = r"C:/Users/derek/5slock/ralph-community/specs"

LEN_FRAMES = [243, 260, 260, 260, 260, 260]   # 5+17k grid: 243 = 5+17*14, 260 = 5+17*15
FPS = 24
CONTEXT_LENGTH = 22                            # Extender context_length widget, "22"
TARGET = 1443
TOL = 24

fails = []


def ck(cond, msg):
    print(("  ok   " if cond else "  FAIL ") + msg)
    if not cond:
        fails.append(msg)


def canon(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=True)


# ---- format stability: re-dumping the untouched backup reproduces it byte for byte ----
raw_bak = open(BAK, "rb").read()
bak = json.loads(raw_bak.decode("utf-8"))
reser = json.dumps(bak, indent=1, ensure_ascii=True) + "\n"
print("[1] builder format is stable (indent=1, ensure_ascii=True, trailing newline)")
ck(canon(bak) == canon(json.loads(reser))
   and reser.encode("utf-8") == raw_bak.replace(b"\r\n", b"\n"),
   "json.dumps(.bak, indent=1) == original bytes (%d B, CRLF-normalised)" % len(raw_bak))

# ---- apply the two changes ----
ext_bak = bak["ext"]
clips_bak = json.loads(ext_bak["inputs"]["clips_json"])
graph = json.loads(raw_bak.decode("utf-8"))
clips = json.loads(graph["ext"]["inputs"]["clips_json"])["clips"]
for idx, clip in enumerate(clips):
    clip["validated"] = False
    clip["duration"] = round(LEN_FRAMES[idx] / float(FPS), 6)
graph["ext"]["inputs"]["clips_json"] = json.dumps(
    {"version": 2, "clips": clips}, ensure_ascii=True, separators=(",", ":")
)
with open(SRC, "w", encoding="utf-8") as fh:
    json.dump(graph, fh, indent=1, ensure_ascii=True)
    fh.write("\n")
print("wrote %s (%d bytes, was %d)" % (SRC, os.path.getsize(SRC), len(raw_bak)))

# ---- self-check of the written file ----
new_raw = open(SRC, "rb").read()
new = json.loads(new_raw.decode("utf-8"))
new_clips = {"version": 2, "clips": json.loads(new["ext"]["inputs"]["clips_json"])["clips"]}

print("[2] json parses, node set unchanged")
ck(sorted(new) == sorted(bak), "node ids identical (%d nodes)" % len(new))

print("[3] every node except ext is byte-identical")
for node in sorted(bak):
    if node != "ext":
        ck(canon(new[node]) == canon(bak[node]), "node %s untouched" % node)

print("[4] ext node: only clips_json differs")
ck(canon({k: v for k, v in new["ext"].items() if k != "inputs"})
   == canon({k: v for k, v in bak["ext"].items() if k != "inputs"}), "ext class_type unchanged")
ck(canon({k: v for k, v in new["ext"]["inputs"].items() if k != "clips_json"})
   == canon({k: v for k, v in bak["ext"]["inputs"].items() if k != "clips_json"}),
   "ext inputs unchanged except clips_json (run_mode/generation_mode/motion_context/"
   "context_length/refine_enabled/steps/width/height/refs_json)")

print("[5] clips_json: 6 clips, validated false, lengths 243,260,260,260,260,260")
ck(len(new_clips["clips"]) == 6, "clip count 6")
ck(new_clips["version"] == 2, "clips_json version 2")
for idx, clip in enumerate(new_clips["clips"]):
    old = clips_bak["clips"][idx]
    frames = int(round(clip["duration"] * FPS))
    ck(clip["validated"] is False, "%s validated is False" % clip["id"])
    ck(clip["duration"] == round(LEN_FRAMES[idx] / float(FPS), 6) and frames == LEN_FRAMES[idx],
       "%s (%s) duration %s = %d frames (grid 5+17k: %s)"
       % (clip["id"], clip["name"], clip["duration"], frames, (frames - 5) % 17 == 0))
    ck(sorted(clip) == sorted(old), "%s key set unchanged" % clip["id"])
    diffs = sorted(k for k in old if k not in ("validated", "duration")
                   and canon(clip.get(k)) != canon(old.get(k)))
    ck(diffs == [], "%s nothing else changed (prompt/seed/seed_mode/color_adjustment/"
       "loras/local_refs/frames/guides/first_source): diffs %s" % (clip["id"], diffs))
ck(all(c["seed"] == 51080000 and c["seed_mode"] == "fixed" for c in new_clips["clips"]),
   "seed 51080000 fixed on all clips")

raw_frames = sum(int(round(c["duration"] * FPS)) for c in new_clips["clips"])
kept = raw_frames - (len(new_clips["clips"]) - 1) * CONTEXT_LENGTH
print("[6] frame budget")
ck(raw_frames == 1543, "raw clip frames %d (243 + 5x260)" % raw_frames)
ck(kept == 1433, "after %d Motion Context seams x%d = %d kept frames"
   % (len(new_clips["clips"]) - 1, CONTEXT_LENGTH, kept))
ck(abs(kept - TARGET) <= TOL, "|%d - %d| = %d <= frames_tol %d (%.3f s at %d fps)"
   % (kept, TARGET, abs(kept - TARGET), TOL, kept / float(FPS), FPS))

print("[7] prompts and ref unchanged (provenance hashes from the build note)")
ck([c["id"] for c in new_clips["clips"]] == ["clip_%d" % (i + 1) for i in range(6)],
   "clip ids clip_1..clip_6 in order")
names = [c["name"] for c in new_clips["clips"]]
ck(names == ["seg1_c0", "seg1_c1", "seg2_c0", "seg2_c1", "seg3_c0", "seg3_c1"],
   "clip names %s" % names)
for c in new_clips["clips"]:
    import hashlib
    print("       %s %s sha256 %s len %d"
          % (c["id"], c["name"],
             hashlib.sha256(c["prompt"].encode("utf-8")).hexdigest(), len(c["prompt"])))
ck(canon(new["ppack"]["inputs"]) == canon(bak["ppack"]["inputs"]), "ppack prompts untouched")
ck(canon(new["rpack"]["inputs"]) == canon(bak["rpack"]["inputs"]), "rpack ref untouched")
ck(canon(new["img"]["inputs"]) == canon(bak["img"]["inputs"]), "LoadImage untouched")

print("[8] class_type / input names exist in specs/extender_object_info.json")
oi = json.load(open(os.path.join(OUT_DIR, "extender_object_info.json"), encoding="utf-8"))


def schema_of(node):
    cls = node["class_type"]
    ent = oi.get(cls)
    if isinstance(ent, list) and ent and isinstance(ent[0], dict):
        ent = ent[0]
    return cls, (ent or {})


ok_all = True
for node in sorted(new):
    cls, ent = schema_of(new[node])
    req = (ent.get("input") or {}).get("required") or {}
    opt = (ent.get("input") or {}).get("optional") or {}
    known = set(req) | set(opt)
    # ComfyUI dynamic-combo sub-widgets are written "widget.subkey" in an API graph
    for wname, wspec in list(req.items()) + list(opt.items()):
        if isinstance(wspec, list) and len(wspec) > 1 and isinstance(wspec[1], dict):
            for option in wspec[1].get("options") or []:
                if not isinstance(option, dict):
                    continue
                for sub in (option.get("inputs") or {}).values():
                    if not isinstance(sub, dict):
                        continue
                    for subkey in sub:
                        known.add("%s.%s" % (option.get("key"), subkey))
                        known.add("%s.%s" % (wname, subkey))
    missing_schema = cls not in oi
    bad = sorted(k for k in new[node]["inputs"] if k not in known)
    miss_req = sorted(k for k in req if k not in new[node]["inputs"])
    flag = (not missing_schema) and bad == [] and miss_req == []
    ok_all = ok_all and (flag or missing_schema)
    print("  %s %-14s %s %s"
          % ("ok  " if flag else ("n/a " if missing_schema else "FAIL"), node, cls,
             ("built-in / not in extender specs" if missing_schema
              else "unknown=%s missing_required=%s" % (bad, miss_req))))
ck(ok_all, "every extender-pack class_type in the graph is in specs/extender_object_info.json "
   "with known input names (built-ins are not in that file)")

print()
print("ALL CHECKS PASS" if not fails else "FAILURES: %d %s" % (len(fails), fails))
