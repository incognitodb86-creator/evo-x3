r"""ALI-163 R1 research probe 2 (read-only, CPU, no GPU calls, no render).

Prints:
  - the full c0 / c1 / m_vsa / win1 / tail1 / app1 node inputs for the HC1 graph and the
    ref-sheet arms (exact settings R1 can cite)
  - render cost per frame from every objective.json in runs (both shapes: flat driver run
    and harness attempts[] run)
Writes nothing.
"""
import json
import os

RUNS = r"C:\AI\community\runs"
DETAIL = [
    "ali147_pool_hc_c1_s51100001",
    "ali147_pool_refsheet_s51080000",
    "ali147_pool_refsheet_b_s51080000",
]
NODES = ("c0", "c1", "m_vsa", "m_attn", "m_shift", "win1", "tail1", "app1", "s0_sched", "s1_sched", "ksel", "unet", "mkvid")


def secs_of(path):
    obj = json.load(open(path, encoding="utf-8-sig"))
    frames = obj.get("frames")
    if "secs" in obj:
        return frames, float(obj["secs"]), "flat"
    att = obj.get("attempts") or []
    if att:
        return frames, float(att[-1].get("secs")), "attempts[%d]" % len(att)
    return frames, None, "none"


def main():
    for arm in DETAIL:
        graph = json.load(open(os.path.join(RUNS, arm, "request.api.json"), encoding="utf-8-sig"))
        print("=" * 70)
        print("ARM", arm)
        for nid in NODES:
            if nid in graph:
                print(" ", nid, graph[nid]["class_type"],
                      json.dumps(graph[nid]["inputs"], sort_keys=True, ensure_ascii=False))

    print("=" * 70)
    print("RENDER COST TABLE (objective.json)")
    rows = []
    for name in sorted(os.listdir(RUNS)):
        p = os.path.join(RUNS, name, "objective.json")
        if not os.path.isfile(p):
            continue
        try:
            frames, secs, shape = secs_of(p)
        except Exception as exc:  # noqa: BLE001
            print("  skip", name, exc)
            continue
        mp4 = os.path.join(RUNS, name, name + ".mp4")
        dims = ""
        if os.path.isfile(mp4):
            obj = json.load(open(p, encoding="utf-8-sig"))
            dims = "%sx%s" % (obj.get("w"), obj.get("h"))
        rows.append((name, frames, secs, shape, dims))
    for name, frames, secs, shape, dims in rows:
        per = "" if (frames and secs) else "-"
        if frames and secs:
            per = "sec/frame %.2f" % (secs / frames)
        print("  %-46s frames=%-5s secs=%-8s %-12s %s %s" % (name, frames, secs, shape, dims, per))
    print("=" * 70)
    budget = json.load(open(r"C:\Users\derek\5slock\ralph-community\logs\p7_budget.json", encoding="utf-8-sig"))
    print("BUDGET", json.dumps(budget, sort_keys=True))
    print("minutes left", round(budget["cap_min"] - budget["used_min"], 1), "job slots left", budget["job_cap"] - budget["jobs"])


if __name__ == "__main__":
    main()
