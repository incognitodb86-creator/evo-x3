r"""queue_klein_explicit.py - Klein NSFW (Jib Mix) vs Klein 9B-KV + SNOFS, nude/explicit test.
Plan: brain 40_projects/max-fix-tests/plans/2026-10-30-klein-uncensored-vs-kv-test-plan.md (APPROVED 7:53/7:54 PM CT).
Brief: C:\AI\community\briefs\2026-10-30-1957-klein-explicit-test-brief.md (fix_plan items K2-K8).

Arms (all + BFS head swap at 0.5 on templates\flux_stills_s2_bfs.api.json - the file named bfs_klein9b.api.json
when this plan ran, merged and retired 2026-11-05 - per-job copies, template untouched):
  G   gate: K, P1, first still, seed S, SNOFS 0.8 vs 0.0 (2 images)
  N   FLUX-KLEIN-9B-FP8-NSFW (template UNET, 4 steps, lcm)              12 images
  N8  N at 8 steps, Euler/Simple                                       12 images
  K   flux-2-klein-9b-kv-fp8 + SNOFS v1.4 @0.8 (loads before BFS), no FluxKVCache node   12 images
  K0  only if the gate fails: KV + BFS, no SNOFS                       12 images
  N12 N at 12 steps, Euler/Simple, its own job after N, N8, K          12 images
Negative: plan text minus "child, teen" (Derrick 11:33 PM CT Oct 30: "ok then remove them") and "school uniform" (Derrick 11:35 PM CT: "Yes, drop school uniform too"); run_queue guard bans those words.
Set: P1-P4 x the next 3 approved stills (INDEX.csv order, not in render\used.txt) x 1 seed S.

Phases (one GPU job at a time; each phase = one run_queue.py --detach batch under gpu-render.lock):
  --phase first   gate + N + N8 (26 images). New run dir runs\YYYY-MM-DD_klein_explicit_NNNN, RESULTS.md gets the
                  3 still ids and S before anything is submitted.
  --phase k       K (or --k0 if the gate failed: log has "lora key not loaded"/lokr ERROR, or 0.8 tile = 0.0 tile).
  --phase n12     N12 (after N, N8, K finished).
  --phase finish  append the 3 still ids to render\used.txt (plan: only after the run).
Seed: S = seed_counter.txt read once at launch; the counter is bumped by 1 at launch (reserves S so /render can't
reuse it; plan says bump after the run, end value is the same). Do NOT bump it again at K7.
Without --go every phase is a dry run: prints each job, checks files, runs run_queue.py --dry-run; no lock, no
ComfyUI, no counter bump, no file copy.
Scoring (plan K7, existing scorer, box only): /workspace/flux_redo_review/score.py --renders <run dir copy>
--cells <run dir>\cells.csv --out scores.csv (w600k_r50, cutoffs.json PASS 0.46 / REVIEW 0.31, vs approved still only).
"""
import argparse, copy, csv, json, os, shutil, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _qcommon as q

TEST = "klein_explicit"
UNET_N = "FLUX-KLEIN-9B-FP8-NSFW.safetensors"
UNET_KV = "flux-2-klein-9b-kv-fp8.safetensors"
SNOFS = "klein_snofs_v1_4.safetensors"
BFS = 0.5
PROMPTS = [
    ("P1", "nude", "{subject}, a fictional adult woman in her 30s, standing fully nude by a sunlit bedroom window, relaxed confident pose, full body, natural skin texture, soft daylight, photorealistic"),
    ("P2", "nude", "{subject}, a fictional adult woman in her 30s, lying fully nude on white sheets, propped on one elbow, looking at the camera, full body, warm lamp light, photorealistic"),
    ("P3", "explicit", "{subject}, a fictional adult woman in her 30s, nude, having consensual sex with an adult man in missionary position on a bed, intimate, both faces visible, explicit, photorealistic, soft light"),
    ("P4", "explicit", "{subject}, a fictional adult woman in her 30s, nude, riding an adult man in cowgirl position on a couch, consensual, smiling, explicit, full body, photorealistic, evening light"),
]
NEGATIVE = "young-looking, extra limbs, fused fingers, deformed anatomy, watermark"
STATE = "_klein_state.json"


def next_stills(n=3):
    """Plan rule: next n INDEX.csv ids (file order) not in used.txt. Returns [(id, name, path)]."""
    used_p = os.path.join(q.mr.STATE, "used.txt")
    used = set(l.strip() for l in open(used_p, encoding="utf-8")) if os.path.exists(used_p) else set()
    names = {r["id"].strip(): r["name"].strip() for r in csv.DictReader(open(os.path.join(q.mr.APPROVED, "INDEX.csv"), encoding="utf-8"))}
    out = [(sid, names.get(sid, sid), p) for sid, p in q.mr.approved_stills() if sid not in used][:n]
    if len(out) < n:
        sys.exit("STOP: fewer than %d unused approved stills (plan: stop and ask, don't reuse)" % n)
    return out


def graph(arm, prompt, subject, image, seed, prefix, snofs=None):
    g = copy.deepcopy(json.load(open(q.TEMPLATE, encoding="utf-8")))
    g["7"]["inputs"]["image"] = image            # Picture 1 = approved still
    g["8"]["inputs"]["image"] = image            # Picture 2 = approved still (no head-crop tool on disk; as make_render)
    g["20"]["inputs"]["noise_seed"] = seed
    g["24"]["inputs"]["filename_prefix"] = prefix
    g["5"]["inputs"]["text"] = prompt.replace("{subject}", subject)
    g["6"]["inputs"]["text"] = NEGATIVE
    g["2"]["inputs"]["strength_model"] = BFS
    if arm in ("N8", "N12"):                     # Euler/Simple at 8 or 12 steps
        g["18"]["inputs"]["sampler_name"] = "euler"
        g["19"] = {"_meta": {"title": "scheduler"}, "class_type": "BasicScheduler",
                   "inputs": {"model": ["2", 0], "scheduler": "simple", "steps": 8 if arm == "N8" else 12, "denoise": 1.0}}
    if arm in ("G", "K", "K0"):
        g["1"]["inputs"]["unet_name"] = UNET_KV
    if arm in ("G", "K"):                        # SNOFS loads before BFS; no FluxKVCache node
        g["27"] = {"_meta": {"title": "snofs"}, "class_type": "LoraLoaderModelOnly",
                   "inputs": {"lora_name": SNOFS, "model": ["1", 0], "strength_model": snofs}}
        g["2"]["inputs"]["model"] = ["27", 0]
    return g


def jobs_for(phase, st, k0=False):
    S, run, stills = st["seed"], st["run"], st["stills"]
    arms = {"first": ["G", "N", "N8"], "k": ["K0" if k0 else "K"], "n12": ["N12"]}[phase]
    out = []
    for arm in arms:
        if arm == "G":
            sid, name, img = stills[0]["id"], stills[0]["name"], stills[0]["image"]
            pid, lvl, p = PROMPTS[0]
            for s in (0.8, 0.0):
                tag = "kx_G_snofs%.1f_%s_%s_s%d" % (s, pid, sid, S)
                out.append(dict(tag=tag, arm="G", scene=sid, seed=S, job_type="still", size=stills[0]["size"], still=sid,
                                prompt=pid, level=lvl, snofs=s, graph=graph("G", p, name, img, S, "community/%s/%s" % (run, tag), s)))
            continue
        for pid, lvl, p in PROMPTS:
            for x in stills:
                tag = "kx_%s_%s_%s_s%d" % (arm, pid, x["id"], S)
                out.append(dict(tag=tag, arm=arm, scene=x["id"], seed=S, job_type="still", size=x["size"], still=x["id"],
                                prompt=pid, level=lvl, snofs=0.8 if arm == "K" else None,
                                graph=graph(arm, p, x["name"], x["image"], S, "community/%s/%s" % (run, tag), 0.8)))
    return out


def describe(j):
    g = j["graph"]
    steps = g["19"]["inputs"]["steps"]
    sched = "%s/%s" % (g["18"]["inputs"]["sampler_name"], g["19"]["inputs"].get("scheduler", "Flux2Scheduler"))
    loras = ["%s@%s" % (n["inputs"]["lora_name"], n["inputs"]["strength_model"]) for k, n in sorted(g.items())
             if n["class_type"] == "LoraLoaderModelOnly"]
    return "%-4s still=%-4s %s seed=%d unet=%s steps=%d %s cfg=%s loras=[%s] out=%s" % (
        j["arm"], j["still"], j["prompt"], j["seed"], g["1"]["inputs"]["unet_name"], steps, sched,
        g["17"]["inputs"]["cfg"], " -> ".join(loras), g["24"]["inputs"]["filename_prefix"])


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--phase", choices=["first", "k", "n12", "finish"], default="first")
    ap.add_argument("--run-dir", help="existing run dir (phases k, n12, finish)")
    ap.add_argument("--k0", action="store_true", help="phase k: the gate failed, run K0 (KV + BFS, no SNOFS)")
    ap.add_argument("--go", action="store_true", help="really submit (default: dry run)")
    ap.add_argument("--dry-run", action="store_true", help="the default; kept for symmetry")
    a = ap.parse_args()
    go = a.go and not a.dry_run
    problems = []

    if a.phase == "first":
        picks = next_stills()
        S = q.mr.counter("seed_counter.txt", 1, start=70000001) if go else q.peek("seed_counter.txt", 70000001)
        run, run_dir = q.new_run_dir(TEST, go)
        stills = []
        for sid, name, p in picks:
            if not os.path.isfile(p): problems.append("MISSING still %s" % p)
            ext = os.path.splitext(p)[1].lower()
            img = "community/%s/%s%s" % (run, sid, ext)
            if go:  # copy OUT of approved_characters (read only) into ComfyUI input
                d = os.path.join(q.mr.COMFY_IN, "community", run); os.makedirs(d, exist_ok=True)
                shutil.copyfile(p, os.path.join(d, sid + ext))
            stills.append(dict(id=sid, name=name, source=p, image=img, size=None))
        st = dict(run=run, seed=S, stills=stills, plan="2026-10-30-klein-uncensored-vs-kv-test-plan.md")
    else:
        if not a.run_dir: sys.exit("--run-dir required for phase %s" % a.phase)
        run_dir = a.run_dir
        st = json.load(open(os.path.join(run_dir, STATE), encoding="utf-8"))
        if a.phase == "finish":
            ids = [x["id"] for x in st["stills"]]
            if go:
                with open(os.path.join(q.mr.STATE, "used.txt"), "a", encoding="utf-8") as f:
                    f.write("".join(i + "\n" for i in ids))
            print("%s append to used.txt: %s" % ("DONE" if go else "DRY would", ", ".join(ids))); return 0

    # size per still (make_bfs_request.expected_size, 1 MP)
    sys.path.insert(0, q.SCRIPTS)
    import make_bfs_request as mb
    for x in st["stills"]:
        if not x.get("size"):
            from PIL import Image
            x["size"] = "%dx%d" % mb.expected_size(*Image.open(x["source"]).size)
    jobs = jobs_for(a.phase, st, a.k0)

    # file checks: template, models, LoRAs, stills; SNOFS hash prefix/suffix
    if not os.path.isfile(q.TEMPLATE): problems.append("MISSING template %s" % q.TEMPLATE)
    problems += q.check_graph_files([j["graph"] for j in jobs])
    for x in st["stills"]:
        if not os.path.isfile(x["source"]): problems.append("MISSING still %s" % x["source"])
    try:
        import run_queue as rq
        bad = [j["tag"] for j in jobs if not rq.guard_graph(j["graph"])]
        if bad: problems.append("run_queue.guard_graph refuses: %s" % ", ".join(bad))
    except Exception as e:
        problems.append("NOTE guard_graph not checked (%s)" % str(e)[:80])

    order_name = "_order_%s%s.json" % (a.phase, "_k0" if a.k0 else "")
    order = q.write_jobs(run_dir, jobs, order_name, header=dict(run=st["run"], test=TEST, phase=a.phase, seed=st["seed"],
                                                             stills=[x["id"] for x in st["stills"]]))
    json.dump(st, open(os.path.join(run_dir, STATE), "w", encoding="utf-8"), indent=1)
    if a.phase == "first":
        with open(os.path.join(run_dir, "cells.csv"), "w", newline="", encoding="utf-8") as f:  # for score.py (K7)
            w = csv.writer(f); w.writerow(["cell", "still", "seed", "arm", "tag", "level", "prompt"])
            for ph in ("first", "k", "n12"):
                for j in jobs_for(ph, st, a.k0):
                    w.writerow([j["prompt"], j["still"], j["seed"], j["arm"], j["tag"], j["level"], j["graph"]["5"]["inputs"]["text"]])
        if go:
            with open(os.path.join(run_dir, "RESULTS.md"), "w", encoding="utf-8") as f:
                f.write("# Klein explicit test - %s\nPlan: brain 40_projects/max-fix-tests/plans/2026-10-30-klein-uncensored-vs-kv-test-plan.md\n"
                        "Stills: %s\nSeed S: %d (seed_counter.txt bumped by 1 at launch to reserve S; do not bump again)\n"
                        % (st["run"], ", ".join(x["id"] for x in st["stills"]), st["seed"]))

    print("%s %s phase=%s run=%s seed S=%d stills=%s jobs=%d" % ("GO" if go else "DRY", TEST, a.phase, st["run"], st["seed"],
          ",".join(x["id"] for x in st["stills"]), len(jobs)))
    for j in jobs: print("  " + describe(j))
    for x in st["stills"]: print("  still %s = %s (%s) subject=%r" % (x["id"], x["source"], x["size"], x["name"]))
    for p in problems: print("BLOCKER " + p if not p.startswith("NOTE") else p)
    rc, out = q.run_queue_dry(run_dir, order)
    print(out)
    if not go:
        print("DRY RUN: nothing submitted, no lock, no ComfyUI, no counter bump, no copy (built in %s)" % run_dir); return 1 if problems else rc
    if any(not p.startswith("NOTE") for p in problems): sys.exit("FAILED blockers above; nothing submitted")
    q.submit(run_dir, order, jobs[0]["size"])
    nxt = {"first": "check the gate (log + 2 tiles), then: py queue_klein_explicit.py --phase k --run-dir %s --go  (add --k0 if the gate failed)",
           "k": "then: py queue_klein_explicit.py --phase n12 --run-dir %s --go",
           "n12": "then score on the box (K7) and: py queue_klein_explicit.py --phase finish --run-dir %s --go"}[a.phase]
    print("NEXT " + nxt % run_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
