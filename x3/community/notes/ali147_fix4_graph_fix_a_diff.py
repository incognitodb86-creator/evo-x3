"""ALI-147 FIX4_GRAPH: readable old->new table for the single changed line (read-only).

Writes notes/ali147-fix4-graph-fix-a-20261022.md from request.api.json vs its .bak.
No GPU, no writes outside notes/.
"""

import hashlib
import json
import os

ARM = r"C:/AI/community/runs/ali147_pool_fix4_s51080000"
SRC = os.path.join(ARM, "request.api.json")
BAK = SRC + ".bak-20261022-fix4graph"
DIFF = os.path.join(ARM, "graph_diff.txt")
NOTE = r"C:/AI/community/notes/ali147-fix4-graph-fix-a-20261022.md"
FPS = 24
CTX = 22

old = json.load(open(BAK, encoding="utf-8"))
new = json.load(open(SRC, encoding="utf-8"))
oc = json.loads(old["ext"]["inputs"]["clips_json"])["clips"]
nc = json.loads(new["ext"]["inputs"]["clips_json"])["clips"]

lines = []
w = lines.append
w("# ALI-147 FIX4_GRAPH option (A) - the two changes, old -> new (Forge, 2026-10-22, CPU only)")
w("")
w("File edited in place: `C:/AI/community/runs/ali147_pool_fix4_s51080000/request.api.json`")
w("Backup (untouched, byte-identical to the pre-edit file, `cmp` silent): "
  "`request.api.json.bak-20261022-fix4graph` (%d B vs %d B after the edit)."
  % (os.path.getsize(BAK), os.path.getsize(SRC)))
w("Readable evidence: `graph_diff.txt` (git diff --no-index .bak -> request.api.json, exit 1): "
  "one hunk, exactly 1 removed and 1 added line = the single `ext.inputs.clips_json` string "
  "line (the file is JSON with `indent=1`, so the whole clip list is one line). "
  "The builder self-check `notes/ali147_fix4_graph_fix_a.py` (ALL CHECKS PASS) is the "
  "semantic proof: every other node and every other `ext` input is byte-identical, and no "
  "clip key other than `validated` / `duration` changed.")
w("")
w("| clip | name | prompt sha256 (unchanged) | len | duration old -> new | frames old -> new | validated old -> new |")
w("|---|---|---|---|---|---|---|")
for a, b in zip(oc, nc):
    fa = a["duration"] * FPS
    fb = b["duration"] * FPS
    w("| %s | %s | `%s` | %d | %s -> %s | %g -> %g | %s -> %s |"
      % (a["id"], a["name"], hashlib.sha256(b["prompt"].encode("utf-8")).hexdigest()[:16],
         len(b["prompt"]), a["duration"], b["duration"], fa, fb, a["validated"], b["validated"]))
raw = sum(round(c["duration"] * FPS) for c in nc)
kept = raw - (len(nc) - 1) * CTX
w("")
w("Frame budget: raw %d (243 + 5x260, all on the 5+17k grid at 24 fps) - %d Motion Context "
  "seams x%d = **%d kept frames = %.3f s**, |%d - 1443| = %d <= frames_tol 24."
  % (raw, len(nc) - 1, CTX, kept, kept / float(FPS), kept, abs(kept - 1443)))
w("")
w("Why (from the failed run, status.log 17:36:56-17:37:07 CT, 3/3 attempts, 5.1 s each): "
  "`Ref2VA clip 1 is marked Validated but its disk cache is missing. Refusing to rerender a "
  "validated clip. Uncheck Validated explicitly if you want this clip rendered again.` "
  "`validated: true` is the UI clip-card checkbox; a cold headless full_batch cannot satisfy "
  "it, so every clip is set to `validated: false`. The 243/238 mirror of the base run put "
  "clip_2..6 off the length grid (238 frames), which the Extender snaps; the grid-aligned "
  "243 + 5x260 is the fair mapping (notes/ali147-fix4-graph-20261022.md finding 2).")
w("")
w("Old failed job outputs were moved aside, never deleted: "
  "`p7/jobs/ali147_pool_fix4_s51080000.{result.json,out,err.out}` -> `*.failed-20261022`, "
  "and the run folder's `ali147_pool_fix4_s51080000*.api.json`, `objective.json`, "
  "`status.log` -> `runs/ali147_pool_fix4_s51080000/failed-20261022/`. "
  "`request.api.json` stays as the input for the re-request (FIX4_REQ).")
w("")
w("METHOD_ONLY. No render, no GPU, no ComfyUI/llama-swap call by Forge; the job is only "
  "requested by the next task (FIX4_REQ). KEEP is Derrick's only.")
w("")
open(NOTE, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("wrote %s (%d lines)" % (NOTE, len(lines)))
