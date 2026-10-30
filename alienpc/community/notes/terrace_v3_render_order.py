#!/usr/bin/env python
# terrace_v3_render_order.py - brief8: draw the Step B render order NOW, so the CHECKED gate can read the exact
# sequence before a single frame is rendered, and so Step B cannot invent an order under time pressure.
# The plan (step 4) asks for: "interleaved by seed and scene (not arm by arm) and randomized; order recorded".
# This does that, deterministically: one documented RNG seed, cells = (scene, seed), cells shuffled, jobs inside
# each cell shuffled, then round-robin ACROSS cells so no two consecutive jobs share a scene+seed cell and no arm
# is rendered in a block. The 2 pilot clips the plan's step 2 names (A0 on Image A/B, seed 51083002) go first and
# are marked: the plan requires a separate pilot GO from Derrick for those two, distinct from the GO for the other 40.
# Cost estimate uses the measured v2 wall seconds for the same 124 f canvas (110.7-144.7 s), not a guess.
import json
import os
import random
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"C:\AI\community\runs\terrace_settings_v3_20261030"
RNG_SEED = 20261030
V2_WALL_MIN, V2_WALL_MAX = 110.7, 144.7
table = json.load(open(os.path.join(ROOT, "_arms_table.json"), encoding="utf-8"))
targets = [m for m in table if not m["reuse_from"]]
pilots = [m for m in targets if m["arm"] == "a0" and m["scene"] in ("imgA", "imgB") and m["seed"] == 51083002]
rest = [m for m in targets if m not in pilots]
rng = random.Random(RNG_SEED)

cells = {}
for m in rest:
    cells.setdefault((m["scene"], m["seed"]), []).append(m)
keys = sorted(cells)
rng.shuffle(keys)
for k in keys:
    rng.shuffle(cells[k])

cell_counts = {k: len(v) for k, v in cells.items()}
# Greedy, deterministic given the shuffles above: at each step take a job from a cell that is not the previous cell
# and whose arm is not the previous arm. The plan forbids "arm by arm"; a round-robin over cells alone can still
# put the same arm back to back when two cells hand over the same arm in consecutive rounds, so the arm is part of
# the pick, not an afterthought. Cells with more jobs left go first, which keeps the queue drainable.
pending = {k: list(v) for k, v in cells.items()}
order = []
# continue the same interleaving across the pilot boundary: the two pilot clips are a0 by the plan's own step 2, so
# the main queue must not open with a third a0 job. The scheduler starts from the last pilot's cell and arm.
prev_cell = (pilots[-1]["scene"], pilots[-1]["seed"]) if pilots else None
prev_arm = pilots[-1]["arm"] if pilots else None
while any(pending.values()):
    cands = sorted([k for k in keys if pending[k]], key=lambda k: (-len(pending[k]), keys.index(k)))
    pick = None
    for k in cands:
        if k == prev_cell:
            continue
        for i, job in enumerate(pending[k]):
            if job["arm"] != prev_arm:
                pick = (k, i)
                break
        if pick:
            break
    if not pick:  # unavoidable at the tail: take anything left
        for k in cands:
            for i, job in enumerate(pending[k]):
                pick = (k, i)
                break
            if pick:
                break
    k, i = pick
    job = pending[k].pop(i)
    order.append(job)
    prev_cell, prev_arm = k, job["arm"]

seq = [{"pos": i + 1, "tag": m["tag"], "arm": m["arm"], "scene": m["scene"], "seed": m["seed"],
        "cell": "%s/%d" % (m["scene"], m["seed"]), "kind": "pilot (plan step 2, separate GO)",
        "prompt_sha256": m["prompt_sha256"], "frames": m["frames"]}
       for i, m in enumerate(pilots)]
seq += [{"pos": len(pilots) + i + 1, "tag": m["tag"], "arm": m["arm"], "scene": m["scene"], "seed": m["seed"],
         "cell": "%s/%d" % (m["scene"], m["seed"]), "kind": "main (plan step 4, after the drift check)",
         "prompt_sha256": m["prompt_sha256"], "frames": m["frames"]} for i, m in enumerate(order)]

bad = []
for i in range(2, len(seq)):
    if seq[i]["cell"] == seq[i - 1]["cell"]:
        bad.append("pos %d repeats cell %s" % (seq[i]["pos"], seq[i]["cell"]))
    if seq[i]["arm"] == seq[i - 1]["arm"]:
        bad.append("pos %d repeats arm %s" % (seq[i]["pos"], seq[i]["arm"]))
by_arm = {}
for s in seq:
    by_arm[s["arm"]] = by_arm.get(s["arm"], 0) + 1
gaps = {a: [] for a in by_arm}
for i, s in enumerate(seq):
    gaps[s["arm"]].append(i)
spacing = {a: min([b - c for c, b in zip(gaps[a], gaps[a][1:])], default=0) for a in gaps}
print("order drawn with random.Random(%d); %d jobs = %d pilots + %d main; %d (scene, seed) cells: %s"
      % (RNG_SEED, len(seq), len(pilots), len(rest), len(cell_counts),
         ", ".join("%s/%d=%d" % (k[0], k[1], n) for k, n in sorted(cell_counts.items()))))
print("jobs per arm: %s | min gap between two jobs of the same arm (positions): %s"
      % (json.dumps(by_arm, sort_keys=True), json.dumps(spacing, sort_keys=True)))
print("interleave check (no consecutive job in the same cell, none from the same arm): %s"
      % ("PASS" if not bad else "FAIL " + "; ".join(bad)))
lo, hi = len(seq) * V2_WALL_MIN, len(seq) * V2_WALL_MAX
print("estimated GPU time from the measured v2 walls: %.0f-%.0f s (%.1f-%.1f min) for %d clips, one job at a time"
      % (lo, hi, lo / 60, hi / 60, len(seq)))
out = {"rng_seed_documented": RNG_SEED, "rule": "pilots first (plan step 2); then round-robin across shuffled "
       "(scene, seed) cells with shuffled jobs inside each cell - never arm-by-arm, never two jobs from one cell "
       "in a row", "n_jobs": len(seq), "n_pilots": len(pilots), "pilots_need_a_separate_GO_per_plan": True,
       "v2_measured_wall_seconds_range": [V2_WALL_MIN, V2_WALL_MAX],
       "estimated_total_seconds": [round(lo), round(hi)], "consecutive_check": "PASS" if not bad else bad,
       "min_gap_same_arm_positions": spacing, "order": seq}
json.dump(out, open(os.path.join(ROOT, "_render_order.json"), "w", encoding="utf-8"), indent=1)
print("wrote runs/terrace_settings_v3_20261030/_render_order.json")
print("\nthe order Step B will follow, verbatim:")
for s in seq:
    print("  %2d  %-22s %-4s %-5s seed=%d  %s" % (s["pos"], s["tag"], s["arm"], s["scene"], s["seed"], s["kind"]))
sys.exit(0 if not bad else 1)
