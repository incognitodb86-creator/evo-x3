r"""queue_klein9b_kv_bfs.py - FLUX.2 Klein 9B-KV + BFS head LoRA: gate, speed and quality test.
Plan: brain 40_projects/max-fix-tests/plans/2026-10-30-klein9b-kv-bfs-test-plan.md (APPROVED 4:33 PM CT).
NOTE: the flux redo plan (5:52 PM CT) lists "Klein KV + BFS ... on hold"; confirm with Derrick before --go.

Reuses Forge's staged, checked job set (fix_plan F3): runs\klein9b_kv_bfs_20261030\_render_order.json = 27 jobs
(G gate 4 at pos 1-4 first, B 3 warm baseline, KP 10, KC 10), request.api.json per job built by make_bfs_request.py.
--go copies the 27 requests into a new date-first run dir runs\YYYY-MM-DD_klein9b_kv_bfs_NNNN, changing only
24.filename_prefix, and submits one run_queue.py --detach batch under gpu-render.lock. Gate fails at render time
(BFS 1.0 tile = 0.0 tile, or "lora key not loaded" in the log) -> stop, per plan.
Default is a dry run: prints every job and checks models, LoRAs, start images and the template; no lock, no ComfyUI.
Scoring (plan: face_sim/T2 vs the approved still): existing box scorer /workspace/flux_redo_review/score.py.
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _qcommon as q

TEST = "klein9b_kv_bfs"
STAGED = os.path.join(q.RUNS, "klein9b_kv_bfs_20261030")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--go", action="store_true"); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(); go = a.go and not a.dry_run
    src = json.load(open(os.path.join(STAGED, "_render_order.json"), encoding="utf-8"))
    order = src["order"] if isinstance(src, dict) else src
    run, run_dir = q.new_run_dir(TEST, go)
    problems, jobs = [], []
    if not os.path.isfile(q.TEMPLATE): problems.append("MISSING template %s" % q.TEMPLATE)
    for o in order:
        g = json.load(open(os.path.join(STAGED, o["tag"], "request.api.json"), encoding="utf-8"))
        g["24"]["inputs"]["filename_prefix"] = "community/%s/%s" % (run, o["tag"])
        for n in ("7", "8"):
            p = os.path.join(q.mr.COMFY_IN, g[n]["inputs"]["image"].replace("/", os.sep))
            if not os.path.isfile(p): problems.append("MISSING start image %s" % p)
        jobs.append(dict({k: v for k, v in o.items() if k != "pos"}, graph=g))
    problems += q.check_graph_files([j["graph"] for j in jobs])
    of = q.write_jobs(run_dir, jobs, header=dict(run=run, test=TEST, source=STAGED))
    print("%s %s run=%s jobs=%d (from %s)" % ("GO" if go else "DRY", TEST, run, len(jobs), STAGED))
    for j in jobs:
        g = j["graph"]
        print("  %-3s scene=%-6s seed=%s unet=%s steps=%s bfs=%s kv=%s out=%s" % (
            j.get("arm"), j.get("scene"), j.get("seed"), g["1"]["inputs"]["unet_name"], g["19"]["inputs"]["steps"],
            g["2"]["inputs"]["strength_model"], "26" in g, g["24"]["inputs"]["filename_prefix"]))
    for p in sorted(set(problems)): print("BLOCKER " + p)
    rc, out = q.run_queue_dry(run_dir, of); print(out)
    if not go:
        print("DRY RUN: nothing submitted (built in %s)" % run_dir); return 1 if problems else rc
    if problems: sys.exit("FAILED blockers above; nothing submitted")
    q.submit(run_dir, of, jobs[0].get("size", "768x1344"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
