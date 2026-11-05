r"""queue_storyboard.py - FLUX Phase 6 (Storyboard), stage + queue.
Plans: brain 40_projects/flux2-overnight/plans/2026-10-30-flux-full-replan.md (Phase 6 row) and
plans/flux-edit-ce-plan-2026-10-28.md (Phase S: arms, grid, downloads). Derrick 1:10 AM CT Oct 31: "Get the storyboard
Phase 6 staged first". Q8/Q9: "Yes, storyboard downloads in the Phase 6 go"; Q11/Q12: Derrick sets the C8-S bar first.

Grid per arm setting (plan): 2 approved characters x 4 shots (wide / medium / close / over-the-shoulder) x 2 seeds
(432262096973493, 20261028) = 16 jobs at 768x1344 (9:16). Base graph = templates\flux_stills_s2_bfs.api.json
(the file named bfs_klein9b.api.json when this plan ran, merged and retired 2026-11-05; arm L:
4 steps, CFG 1, lcm), head = image 1, body/outfit = image 2 (both = the approved still; no head crops on disk),
output size fixed to the plan's W x H. Per-job copies only; the template is never edited.
Arms built here (one variable each):
  S0  baseline, slot-named prompt, 1 shot per job                        16
  S1  + Consistency V2 LoRA 0.35 / 0.5 / 0.7            (needs C13)     48
  S2  + EmmyJ Character Consistency LoRA 2.4 / 1.6      (needs C16)     32
  S4  character restated in the shot line (R) vs stated once/omitted (O) 32
  S5  one-shot 2x2 grid, canvas 1536x1536 / 1920x1088 / 1088x1920, cut with core ImageCrop x4   12
  S9  Change Scene LoRA, location change from panel 3 on (needs C15)    16
  MC  multi-character set on S0 settings (deliverable set; 1 two-adult still)   8
Not built (need a result or input that does not exist yet): S3 (no QuadView sheet on disk), S6 (best S5 panel),
S7 (Phase P skeletons + base-9B), S8 (C17 + C18 + base-9B + S5 panel), S10 (chained: panel n output feeds n+1),
S11' RefGrid (the 4 refs are not defined in the plan).
Every prompt passes run_queue.guard_graph (unchanged). Default = dry run (no lock, no ComfyUI, no copy, %TEMP%).
--go submits the chosen arms (default: those whose files exist) as one run_queue.py --detach batch.
"""
import argparse, copy, csv, json, os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _qcommon as q

TEST = "storyboard"
SEEDS = [432262096973493, 20261028]
SIZE916 = (768, 1344)
SHOTS = [("wide", "wide shot, full body, the whole room visible"),
         ("medium", "medium shot from the waist up"),
         ("close", "close-up of her face and shoulders"),
         ("ots", "over-the-shoulder shot from behind her, looking past her shoulder into the room")]
CHAR = "the same adult woman (fictional, in her 30s) with the face and hair from Picture 1 and the outfit from Picture 2"
CHAR2 = "the same two adults (fictional, in their 30s) with the faces, hair and outfits from Picture 1"
S0_TPL = "Picture 1 is the head reference. Picture 2 is the body and outfit reference. Show {char}, {shot}, same room, same outfit. Photoreal, soft natural light."
S4_ONCE = "Picture 1 is the head reference. Picture 2 is the body and outfit reference. Storyboard panel: {shot}. Photoreal, soft natural light."
GRID = ("Picture 1 is the head reference. Picture 2 is the body and outfit reference. 2x2 grid, left-to-right, top-to-bottom, "
        "same person, same outfit, same room. {char}. Panel 1 wide shot, panel 2 medium shot, panel 3 close-up, panel 4 over-the-shoulder shot.")
S9_LOC = "on a sunlit rooftop terrace"   # location for panels 3-4
LORAS = {"S1": ("Flux2-Klein-9B-consistency-V2.safetensors", [0.35, 0.5, 0.7]),
         "S2": ("flux2_klein_9b_character_consistency_lora_v1.safetensors", [2.4, 1.6]),
         "S9": ("change-scene-klein_v1.safetensors", [1.0])}   # S9 "as-published strength": 1.0 NOT VERIFIED
DOWNLOADS = [  # (card, file, folder, bytes, url)
    ("C13", "Flux2-Klein-9B-consistency-V2.safetensors", "lora", 331379608, "https://huggingface.co/dx8152/Flux2-Klein-9B-Consistency"),
    ("C14", "refcontrol_v2_poses.safetensors", "lora", 165704416, "https://huggingface.co/thedeoxen/refcontrol-FLUX.2-klein-9B-reference-pose-lora"),
    ("C15", "change-scene-klein_v1.safetensors", "lora", 165704704, "https://civitai.com/models/2660894"),
    ("C16", "flux2_klein_9b_character_consistency_lora_v1.safetensors", "lora", 79709184, "https://civitai.com/models/2988766"),
    ("C17", "flux2_klein_9b_refcontrol_depth.safetensors", "lora", 165704480, "https://huggingface.co/thedeoxen/refcontrol-FLUX.2-klein-9B-reference-depth-lora"),
    ("C18", "depth_anything_v2_vits.pth", None, 99218434, "https://huggingface.co/depth-anything/Depth-Anything-V2-Small"),
    ("base-9B", "flux-2-klein-base-9b-fp8.safetensors", "unet", 9570000000, "https://huggingface.co/black-forest-labs/FLUX.2-klein-base-9b-fp8 (gated)"),
]
SKIP = {"E10", "SYDNEY"}


def pick_chars(n, exclude):
    """Next n INDEX.csv ids not in used.txt / exclude / SKIP, skipping _dropped/_needs_derrick paths."""
    used_p = os.path.join(q.mr.STATE, "used.txt")
    used = set(l.strip() for l in open(used_p, encoding="utf-8")) if os.path.exists(used_p) else set()
    out = []
    for sid, p in q.mr.approved_stills():
        if sid in used or sid in exclude or sid in SKIP or "_dropped" in p or "_needs_derrick" in p: continue
        out.append((sid, p))
        if len(out) == n: break
    return out


def base(image, seed, prefix, text, w, h):
    g = copy.deepcopy(json.load(open(q.TEMPLATE, encoding="utf-8")))
    g["7"]["inputs"]["image"] = image; g["8"]["inputs"]["image"] = image
    g["20"]["inputs"]["noise_seed"] = seed; g["24"]["inputs"]["filename_prefix"] = prefix
    g["5"]["inputs"]["text"] = text
    for n in ("19", "21"): g[n]["inputs"]["width"] = w; g[n]["inputs"]["height"] = h
    return g


def add_lora(g, name, s):
    g["27"] = {"_meta": {"title": "arm_lora"}, "class_type": "LoraLoaderModelOnly",
               "inputs": {"lora_name": name, "model": ["1", 0], "strength_model": s}}
    g["2"]["inputs"]["model"] = ["27", 0]


def add_crops(g, w, h, prefix):
    """core ImageCrop x4 on the decoded grid, each saved (panels p1..p4, left-to-right, top-to-bottom)."""
    cw, ch = w // 2, h // 2
    for i, (x, y) in enumerate([(0, 0), (cw, 0), (0, ch), (cw, ch)], 1):
        c, s = str(40 + i), str(50 + i)
        g[c] = {"_meta": {"title": "crop_p%d" % i}, "class_type": "ImageCrop",
                "inputs": {"image": ["23", 0], "width": cw, "height": ch, "x": x, "y": y}}
        g[s] = {"_meta": {"title": "save_p%d" % i}, "class_type": "SaveImage",
                "inputs": {"images": [c, 0], "filename_prefix": prefix + "_panels/p%d" % i}}


def build(run, chars, multi):
    jobs = []
    def job(arm, setting, sid, img, seed, shot, text, w, h, lora=None, grid=False):
        tag = "sb_%s%s_%s_%s_s%d" % (arm, setting, sid, shot, seed)
        pre = "community/%s/%s" % (run, tag)
        g = base(img, seed, pre, text, w, h)
        if lora: add_lora(g, *lora)
        if grid: add_crops(g, w, h, pre)
        jobs.append(dict(tag=tag, arm=arm, setting=setting, scene=sid, still=sid, seed=seed, shot=shot,
                         job_type="still", size="%dx%d" % (w, h), graph=g))
    w, h = SIZE916
    for sid, img in chars:
        for seed in SEEDS:
            for k, (shot, line) in enumerate(SHOTS):
                job("S0", "", sid, img, seed, shot, S0_TPL.format(char=CHAR, shot=line), w, h)
                for arm in ("S1", "S2"):
                    name, strengths = LORAS[arm]
                    for s in strengths:
                        job(arm, "_%g" % s, sid, img, seed, shot, S0_TPL.format(char=CHAR, shot=line), w, h, lora=(name, s))
                job("S4", "R", sid, img, seed, shot, S0_TPL.format(char=CHAR, shot=line), w, h)
                job("S4", "O", sid, img, seed, shot, S4_ONCE.format(shot=line), w, h)
                loc = line + (", " + S9_LOC if k >= 2 else "")
                job("S9", "", sid, img, seed, shot, S0_TPL.format(char=CHAR, shot=loc), w, h, lora=(LORAS["S9"][0], LORAS["S9"][1][0]))
            for gw, gh in ((1536, 1536), (1920, 1088), (1088, 1920)):
                job("S5", "_%dx%d" % (gw, gh), sid, img, seed, "grid", GRID.format(char=CHAR), gw, gh, grid=True)
    if multi:
        sid, img = multi
        for seed in SEEDS:
            for shot, line in SHOTS:
                job("MC", "", sid, img, seed, shot, S0_TPL.format(char=CHAR2, shot=line).replace(
                    "Picture 2 is the body and outfit reference.", "Picture 2 is the same picture."), w, h)
    return jobs


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--arms", default="ready", help="comma list (S0,S1,S2,S4,S5,S9,MC) or 'ready' = arms with no missing file")
    ap.add_argument("--multi", default="M04", help="approved id of the two-adult still for the MC set")
    ap.add_argument("--exclude", default="E11,E2,E3", help="ids held by another run (Klein explicit)")
    ap.add_argument("--go", action="store_true"); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(); go = a.go and not a.dry_run
    chars = pick_chars(2, set(a.exclude.split(",")))
    pool = dict(q.mr.approved_stills()); multi = (a.multi, pool[a.multi]) if a.multi in pool else None
    run, run_dir = q.new_run_dir(TEST, go)
    staged = {}
    for sid, p in chars + ([multi] if multi else []):
        ext = os.path.splitext(p)[1].lower(); staged[sid] = "community/%s/%s%s" % (run, sid, ext)
        if go:
            d = os.path.join(q.mr.COMFY_IN, "community", run); os.makedirs(d, exist_ok=True)
            shutil.copyfile(p, os.path.join(d, sid + ext))
    jobs = build(run, [(s, staged[s]) for s, _ in chars], (multi[0], staged[multi[0]]) if multi else None)

    import run_queue as rq
    print("DOWNLOADS (not downloaded by this script):")
    for card, f, kind, b, url in DOWNLOADS:
        if kind: here = q.model_path(kind, f)
        else:
            here = os.path.join(q.MODELS, "..", "custom_nodes", "comfyui_controlnet_aux", "ckpts", "depth-anything", "Depth-Anything-V2-Small", f)
            here = here if os.path.isfile(here) else None
        print("  %-7s %-58s %6.1f MB  %s  %s" % (card, f, b / 1e6, "PRESENT" if here else "MISSING", url))
    by_arm, ready = {}, {}
    for j in jobs:
        miss = q.check_graph_files([j["graph"]]); ok = rq.guard_graph(j["graph"])
        r = by_arm.setdefault(j["arm"], [0, 0, set()]); r[0] += 1; r[1] += ok; r[2].update(miss)
    for arm, (n, ok, miss) in by_arm.items():
        ready[arm] = not miss and ok == n
        print("ARM %-3s jobs=%3d guard_ok=%3d/%d %s" % (arm, n, ok, n, "READY" if ready[arm] else "BLOCKED " + "; ".join(sorted(miss))))
    arms = [x for x in by_arm if ready[x]] if a.arms == "ready" else a.arms.split(",")
    sel = [j for j in jobs if j["arm"] in arms]
    print("chars=%s multi=%s selected arms=%s jobs=%d of %d" % (",".join(c[0] for c in chars), multi[0] if multi else None, ",".join(arms), len(sel), len(jobs)))
    for j in sel:
        g = j["graph"]
        print("  %-3s%-12s still=%-4s %-6s seed=%s size=%s lora=%s out=%s" % (j["arm"], j["setting"], j["still"], j["shot"], j["seed"], j["size"],
              g.get("27", {}).get("inputs", {}).get("lora_name", "-"), g["24"]["inputs"]["filename_prefix"]))
    if not sel: print("nothing selected"); return 1
    of = q.write_jobs(run_dir, sel, header=dict(run=run, test=TEST, arms=arms))
    with open(os.path.join(run_dir, "prompts.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["tag", "arm", "prompt"])
        for j in sel: w.writerow([j["tag"], j["arm"], j["graph"]["5"]["inputs"]["text"]])
    rc, out = q.run_queue_dry(run_dir, of); print(out)
    bad = [j["tag"] for j in sel if not rq.guard_graph(j["graph"]) or q.check_graph_files([j["graph"]])]
    if not go:
        print("DRY RUN: nothing submitted (built in %s)" % run_dir); return 1 if bad else rc
    if bad: sys.exit("FAILED %d selected jobs blocked; nothing submitted" % len(bad))
    q.submit(run_dir, of, sel[0]["size"]); return 0


if __name__ == "__main__":
    sys.exit(main())
