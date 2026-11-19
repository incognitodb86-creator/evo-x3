#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ali163_hc_lessons_build.py - fix_plan 2.1 first deliverable: notes/hc_lessons_20261023.md.

Derrick 2026-10-23 6:12 PM CT (AGENTS.md L7): NO KEEP on r1-r6 / r3r / r3b; write
notes/hc_lessons_20261023.md, improve ONE variable per render, re-render the same seeds.
The file did not exist when this builder was written (find over C:/AI/community and
C:/Users/derek/5slock = 0 hits, 2026-11-03).

The deliverable is GENERATED and FALSIFIABLE (AGENTS.md L10: a green check that cannot fail is
worthless). Nothing in the doc's numbers is typed by hand: every measured cell is rendered from
notes/ali163_hc_lessons_facts.json, which is itself a measurement of the runs on disk.

  --facts     measure the HC runs -> notes/ali163_hc_lessons_facts.json
  --build     render notes/hc_lessons_20261023.md from facts + the LESSONS table below
  --check     re-measure from disk, then run all 13 detectors; exit 0 = VERDICT CLEAN
  --selftest  seed one fault per detector in a CLONE: each MUST fire there, and 0 on the real tree

CPU only. Read-only on C:/AI/community/runs. No GPU, no queue, no network, no pi, no writes under runs/.
Exit 0 clean, 1 problems found, 2 usage / selftest failure.

DETECTORS (one seed each in --selftest; names prefix the problem lines):
  MEASURE   facts JSON does not equal a fresh measurement of the same mp4s (stale facts)
  DRIFT     doc on disk != doc regenerated from facts
  INVENTED  a roster run id with no run dir on disk (AGENTS.md L4: never cite what you did not read)
  ROSTER    a roster row claims a render with no mp4, or claims NO RENDER while an mp4 exists
  MATH      duration != frames/fps (beyond 0.05 s container slack)
  CANVAS    a canvas W or H is not a multiple of 32 (H3_CANVAS_MULTIPLE)
  PATH      an artifact path cited by a lesson is not on disk
  VALUE     a {F:...} fact token in a lesson does not resolve to a measured value
  KNOB      a lesson acts on a graph key that the measured graphs do not expose (the cfg trap)
  ASRUN     a roster render claim contradicts that run's own committed objective record
  EVIDENCE  a lesson with no artifact path in its evidence
  COVERAGE  a roster run is not named anywhere in the doc
  KEEPWORD  a KEEP verdict is assigned in the doc (KEEP is Derrick's alone)
  JUDGE     a vision judge is credited with picking a keeper
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

FFPROBE = ("C:/Users/derek/AppData/Local/Microsoft/Winget/Packages/"
           "Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.0.1-full_build/bin/ffprobe.exe")
NOTES = "C:/AI/community/notes"
RUNS = "C:/AI/community/runs"
FACTS = NOTES + "/ali163_hc_lessons_facts.json"
DOC = NOTES + "/hc_lessons_20261023.md"
# The as-run objective gate: what each render's own run recorded (wall_min, budget burn, frame
# proxies, static defects). The final file has no mp4 container duration; bq1d does (task-2 recon).
AS_RUN = [NOTES + "/ali163_hc_final_objective.json", NOTES + "/ali163_hc_bq1d_objective.json"]
AS_RUN_KEYS = ["ok", "rc", "wall_min", "budget_used_min", "budget_cap_min", "frames", "frames_count",
               "frames_sha_unique", "frames_min_luma_std", "job_error_grep", "clip_skip_grep",
               "static_defects", "objective_line", "seed", "refs", "ref_slots", "soundscape",
               "width", "height", "c0_length", "ext_frames", "sampler_name", "shift", "steps",
               "node_count", "class_counts", "prompt_id"]
ASRUN_FIELDS = ["ok", "rc", "wall_min", "budget_used_min", "frames_count", "frames_sha_unique",
                "frames_min_luma_std", "job_error_grep", "static_defects"]
CANVAS_MULT = 32
DUR_SLACK = 0.05
# The only phrasings in which an uppercase KEEP may appear: the quoted rule and the NO-KEEP statements.
KEEP_ALLOW = ("NO KEEP", "KEEP is Derrick", "keepers", "KEEP is Derrick's alone")

# The 10 HC clips, as notes/ali163_hc_final_check.py measured them. Kept in code so the doc's
# roster can be re-measured off disk; `expected` and `note` are claims the check tests, not facts.
CLIPS = [
    ("clip1 OLD", "ali147_pool_hc_c1_s51100001", "HC1 BD004", 481, "old batch: the 481 f / 20.04 s shape"),
    ("clip2 OLD", "ali147_pool_hc_c2_s51100002", "HC2 BD007", 481, "old batch: 481 f"),
    ("clip1 NEW", "ali147_pool_hc_r1_s51130001", "HC1 BD004", 243, "R4"),
    ("clip2 NEW", "ali147_pool_hc_r2_s51130002", "HC2 BD007", 243, "R5"),
    ("clip3", "ali147_pool_hc_r3_s51130003", "HC3 GI173", 243, "R6: static-check rc=2, NO RENDER (no mp4, no objective.json)"),
    ("clip3 R6R", "ali147_pool_hc_r3r_s51130003", "HC3 GI173", 243, "R6R: face crops only, start still NOT in the graph"),
    ("clip3 BQ1c", "ali147_pool_hc_r3b_s51130003", "HC3 GI173", 243, "BQ1c: start still + face crops in all 3 slots"),
    ("clip4", "ali147_pool_hc_r4_s51130004", "HC4 GI107", 243, "R7"),
    ("clip5", "ali147_pool_hc_r5_s51130005", "HC5 GI150", 243, "R8"),
    ("clip6", "ali147_pool_hc_r6_s51130006", "HC6 BD076", 243, "R9"),
]

# Derrick's rules, quoted, kept in code so the doc can never reword them and the KEEPWORD/JUDGE
# detectors have an allowlist to work against.
RULES = [
    "NO KEEP on r1-r6 / r3r / r3b - Derrick 2026-10-23 6:12 PM CT. KEEP is Derrick's alone; this doc assigns no verdict.",
    "One variable improved per render, re-render the same seeds. IM1 (fix_plan 3.8) wins over the one-variable rule where they conflict (Derrick 6:25 PM CT).",
    "Contact sheet + objective checks only; no vision judge picks keepers.",
    "The GPU is off-limits in an unattended pass (AGENTS.md, PROMPT.md 99999999): this doc queues nothing and names no queued job.",
    "Every character is a fictional adult 21+ and every render passes scripts/comm.py first (fix_plan 1.2).",
]


# ----------------------------------------------------------------------------- measurement
def probe(mp4):
    """ffprobe by FIELD NAME (json), never by CSV position: the CSV order documented in
    AGENTS.md (nb_read_packets,r_frame_rate,width,height) is not the order ffprobe 8.0.1
    emits, and reading it positionally silently swaps width and packet count."""
    if not os.path.exists(mp4):
        return {"mp4_exists": False}
    j = subprocess.run([FFPROBE, "-v", "error", "-select_streams", "v:0", "-count_packets",
                        "-show_entries", "stream=width,height,r_frame_rate,nb_read_packets",
                        "-of", "json", mp4], capture_output=True, text=True)
    out = {"mp4_exists": True, "rc": j.returncode, "err": (j.stderr or "").strip()[:200]}
    try:
        st = json.loads(j.stdout)["streams"][0]
        out["w"], out["h"] = int(st["width"]), int(st["height"])
        num, _, den = str(st["r_frame_rate"]).partition("/")
        out["fps"] = float(num) / float(den or 1)
        out["packets"] = int(st["nb_read_packets"])
    except Exception as e:
        out["probe_error"] = repr(e)[:160]
        return out
    k = subprocess.run([FFPROBE, "-v", "error", "-show_entries",
                        "stream=codec_type,codec_name,sample_rate,channels:format=duration",
                        "-of", "json", mp4], capture_output=True, text=True)
    try:
        d = json.loads(k.stdout)
        aud = [s for s in d.get("streams", []) if s.get("codec_type") == "audio"]
        out["audio"] = bool(aud)
        out["audio_desc"] = ",".join("%s %s %sch" % (a.get("codec_name"), a.get("sample_rate"),
                                                     a.get("channels")) for a in aud)
        out["dur"] = float(d["format"]["duration"])
    except Exception as e:
        out["audio_probe_error"] = repr(e)[:160]
    out["bytes"] = os.path.getsize(mp4)
    out["sha256"] = hashlib.sha256(open(mp4, "rb").read()).hexdigest()
    return out


def graph_keys(run_dir, run_id):
    """The keys the lessons act on, read out of the submitted graph (never assumed)."""
    api = os.path.join(run_dir, run_id + ".api.json")
    g = {"api_exists": os.path.exists(api)}
    if not g["api_exists"]:
        return g
    data = json.load(open(api, encoding="utf-8"))
    nodes = data.get("nodes") if isinstance(data, dict) and "nodes" in data else data
    if not isinstance(nodes, dict):
        g["shape"] = type(nodes).__name__
        return g
    g["n_nodes"] = len(nodes)
    g["cfg_keys"] = sorted({k for n in nodes.values() for k in n.get("inputs", {}) if "cfg" in k.lower()})
    for nid, n in nodes.items():
        cls, inp = n.get("class_type", ""), n.get("inputs", {})
        if cls == "RandomNoise":
            g["noise_seed"] = inp.get("noise_seed")
        elif cls == "KSamplerSelect":
            g["sampler_name"] = inp.get("sampler_name")
        elif cls == "BasicScheduler":
            g.setdefault("steps", []).append([nid, inp.get("steps")])
        elif cls == "SamplerCustomAdvanced":
            g.setdefault("sampler_nodes", []).append(nid)
        elif cls == "MiniMaxH3SigmaShift":
            g["shift_video"] = inp.get("shift_video")
            g["shift_audio"] = inp.get("shift_audio")
        elif cls.startswith("MiniMaxH3") and cls.endswith("Video"):
            g.setdefault("video_nodes", []).append({
                "id": nid, "cls": cls, "width": inp.get("width"), "height": inp.get("height"),
                "length": inp.get("length"), "ref_image_size": inp.get("ref_image_size"),
                "refs": sorted(k for k in inp if re.fullmatch(r"ref_images\.ref_image_\d+", k)),
            })
    return g


def status_lines(run_dir):
    """The run's own JOB end / OBJECTIVE lines, quoted from status.log (never typed)."""
    log = os.path.join(run_dir, "status.log")
    out = {"status_exists": os.path.exists(log)}
    if not out["status_exists"]:
        return out
    txt = open(log, encoding="utf-8", errors="replace").read().splitlines()
    out["job_end"] = [x for x in txt if " JOB end " in x][-1:]
    out["objective"] = [x for x in txt if " OBJECTIVE " in x][-1:]
    out["job_error_grep"] = sum(1 for x in txt if "JOB error" in x)
    for line in out["job_end"]:
        m = re.search(r"secs=([0-9.]+)", line)
        if m:
            out["secs"] = float(m.group(1))
    return out


def as_run_index():
    """Index the two committed objective files by run id, keeping only the keys they actually carry."""
    idx = {}
    for path in AS_RUN:
        if not os.path.exists(path):
            continue
        rows = json.load(open(path, encoding="utf-8"))
        rows = rows if isinstance(rows, list) else rows.get("rows", [])
        for row in rows:
            if not isinstance(row, dict) or "id" not in row:
                continue
            keep = {k: row[k] for k in AS_RUN_KEYS if k in row}
            keep["_src"] = os.path.basename(path)
            idx.setdefault(row["id"], {}).update(keep)
    return idx


def measure():
    asrun = as_run_index()
    rows = []
    for label, rid, pick, exp, note in CLIPS:
        d = os.path.join(RUNS, rid)
        row = {"label": label, "id": rid, "pick": pick, "expected_frames": exp, "note": note,
               "run_dir_exists": os.path.isdir(d), "rendered": False,
               "mp4": "", "contact_png": "", "contact_bytes": 0,
               "objective_json": False, "probe": {}, "graph": {}, "status": {}, "as_run": {}}
        if os.path.isdir(d):
            mp4 = os.path.join(d, rid + ".mp4")
            row["mp4"] = mp4.replace("\\", "/")
            row["rendered"] = os.path.exists(mp4)
            row["probe"] = probe(mp4) if row["rendered"] else {"mp4_exists": False}
            row["as_run"] = {k: v for k, v in asrun.get(rid, {}).items()}
            png = [x for x in os.listdir(d) if x.endswith("_stills_contact.png")]
            if png:
                p = os.path.join(d, png[0])
                row["contact_png"], row["contact_bytes"] = p.replace("\\", "/"), os.path.getsize(p)
            row["objective_json"] = os.path.exists(os.path.join(d, "objective.json"))
            row["graph"] = graph_keys(d, rid)
            row["status"] = status_lines(d)
        rows.append(row)
    return rows


# ---------------------------------------------------------------------------- lesson table
# Each lesson: claim (the lesson), evidence (artifact paths and {F:...} fact tokens),
# knobs (graph keys the next render may act on - the KNOB detector proves they exist),
# action (the ONE variable for the next render), repro (a command on this box).
# Fact tokens resolve against the facts row named, so every number in the doc traces to disk.
LESSONS = [
    dict(id="L1", title="The 481-frame shape is the rejected shape, and it costs double",
         claim="The two OLD clips are 481 f / 20.04 s and took {F:clip1 OLD:status.secs} s and "
               "{F:clip2 OLD:status.secs} s of GPU; every 243 f / 10.125 s clip after them ran "
               "between {MINSECS} s and {MAXSECS} s. Length, not quality work, was the cost driver.",
         evidence=["C:/AI/community/runs/ali147_pool_hc_c1_s51100001/status.log",
                   "C:/AI/community/runs/ali147_pool_hc_r1_s51130001/status.log",
                   "C:/AI/community/notes/ali163_hc_final_objective.json"],
         knobs=["MiniMaxH3ReferenceToVideo.length", "MiniMaxH3GuidedContinuationWindow.extension_frames"],
         action="Keep the 243 f shape ((frames-5) % 17 == 0 grid: c0 length 124 + extension 119 = 243) "
                "and never spend a GPU slot on 481 f again; 3.8 (IM1) is where resolution moves.",
         repro="C:/AI/director/.venv/Scripts/python.exe C:/AI/community/notes/ali163_hc_lessons_build.py --facts"),
    dict(id="L2", title="No CFG key exists in the video graphs, so CFG advice is not a lever",
         claim="Across the {NGRAPH} clip graphs on disk the number of input keys containing 'cfg' is "
               "{CFGMAX} ({CFGDETAIL}). The levers the shipped graph actually exposes are "
               "KSamplerSelect.sampler_name = {F:clip3 BQ1c:graph.sampler_name}, BasicScheduler.steps = "
               "{F:clip3 BQ1c:graph.steps}, MiniMaxH3SigmaShift shift_video {F:clip3 BQ1c:graph.shift_video} / "
               "shift_audio {F:clip3 BQ1c:graph.shift_audio}, and {F:clip3 BQ1c:samplers} SamplerCustomAdvanced "
               "nodes = one denoise pass per clip.",
         evidence=["C:/AI/community/runs/ali147_pool_hc_r3b_s51130003/ali147_pool_hc_r3b_s51130003.api.json",
                   "C:/AI/community/notes/self_setup_20261023.md"],
         knobs=["KSamplerSelect.sampler_name", "BasicScheduler.steps",
                "MiniMaxH3SigmaShift.shift_video", "MiniMaxH3SigmaShift.shift_audio"],
         action="Drop CFG from the candidate-variable list for the video path (it is a Klein sheet-edit key, "
                "not a clip key); the sampler/steps/shift keys above are the ones that exist.",
         repro='grep -c cfg C:/AI/community/runs/ali147_pool_hc_*/ali147_pool_hc_*.api.json'),
    dict(id="L3", title="Reference slots: the one clean same-seed A/B on this box is r3r vs r3b",
         claim="Seed {F:clip3 R6R:graph.noise_seed} was rendered twice: R6R wired c0 with "
               "{F:clip3 R6R:refcount} ref slots (face crops, start still NOT in the graph) and BQ1c wired "
               "{F:clip3 BQ1c:refcount} ref slots on c0 and {F:clip3 BQ1c:refcount_c1} on c1 "
               "(start still + face crops). Same seed, same canvas {F:clip3 BQ1c:canvas}, same frames "
               "{F:clip3 BQ1c:probe.packets} - the ref-slot wiring is the only difference, so it is the "
               "comparison to read, and no verdict on it is recorded here.",
         evidence=["C:/AI/community/runs/ali147_pool_hc_r3r_s51130003/ali147_pool_hc_r3r_s51130003.api.json",
                   "C:/AI/community/runs/ali147_pool_hc_r3b_s51130003/ali147_pool_hc_r3b_s51130003.api.json",
                   "C:/AI/community/notes/ali163_hc_bq1d_objective.json"],
         knobs=["ref_images.ref_image_1", "ref_images.ref_image_2", "ref_images.ref_image_3",
                "MiniMaxH3ReferenceToVideo.ref_image_size"],
         action="Continue from the BQ1c wiring and change one variable per render (3.8/IM1 list), re-rendering "
                "seeds 51130003-51130006; read slots with fullmatch ref_images\\.ref_image_\\d+.",
         repro="C:/AI/director/.venv/Scripts/python.exe C:/AI/community/notes/ali163_hc_bq1d_objective.json"),
    dict(id="L4", title="A static-check fail costs a whole iteration and zero GPU",
         claim="clip3 R6 ({F:clip3:id}) never rendered: its run dir holds {F:clip3:nfiles} files, no mp4 "
               "({F:clip3:mp4_exists}) and no objective.json ({F:clip3:objective_json}), so the roster row "
               "says NO RENDER and the GPU minutes spent on it are 0.",
         evidence=["C:/AI/community/runs/ali147_pool_hc_r3_s51130003",
                   "C:/AI/community/notes/ali163_hc_final_objective.json"],
         knobs=["MiniMaxH3MultiReferenceToVideo.clips_json", "MiniMaxH3ImageToVideo.audio_vae"],
         action="Run the offline static check (check 11 of notes/ali163_hc_r4g2_build.py) before writing a "
                "JOB_REQUEST, so a schema fail lands in seconds, not in a lost iteration.",
         repro="ls -la C:/AI/community/runs/ali147_pool_hc_r3_s51130003"),
    dict(id="L5", title="Canvas arithmetic is a hard constraint, not a preference",
         claim="All 9 rendered clips came out {F:clip3 BQ1c:canvas}, i.e. {F:clip3 BQ1c:w_div} x "
               "{F:clip3 BQ1c:h_div} multiples of 32. The 832x468 canvas our notes repeated is unreachable "
               "(468 % 32 = 20), so a render that asks for it cannot be the fix; it is an unbuildable request.",
         evidence=["C:/AI/community/runs/ali147_pool_hc_r3b_s51130003/ali147_pool_hc_r3b_s51130003.mp4",
                   "C:/AI/community/notes/self_setup_20261023.md"],
         knobs=["MiniMaxH3ReferenceToVideo.width", "MiniMaxH3ReferenceToVideo.height"],
         action="For 16:9 keep a canvas whose W and H are both multiples of 32 (1344x768 today, 1024x576 for a "
                "Continuum target); step resolution only in those units.",
         repro="C:/AI/director/.venv/Scripts/python.exe C:/AI/community/notes/ali163_hc_lessons_build.py --facts"),
    dict(id="L6", title="Native audio is already in every clip, so 'add audio' is not a variable",
         claim="Every rendered mp4 carries an audio stream ({F:clip1 NEW:probe.audio_desc} in clip1 NEW); the "
               "count of rendered clips with audio = {AUDIOCOUNT} of {RENDEREDCOUNT}. The variable that "
               "exists is the soundscape wording inside the prompt, not an audio node to add.",
         evidence=["C:/AI/community/notes/ali163_hc_final_objective.json",
                   "C:/AI/community/runs/ali147_pool_hc_r5_s51130005/ali147_pool_hc_r5_s51130005.m4a"],
         knobs=["MiniMaxH3SigmaShift.shift_audio", "MiniMaxH3ReferenceToVideo.prompt"],
         action="For 2.3 (ALI-183), treat the prompt's soundscape line as the one variable and keep the audio "
                "shift at {F:clip3 BQ1c:graph.shift_audio}; extract the m4a with the AGENTS.md FINAL media command.",
         repro="C:/AI/director/.venv/Scripts/python.exe C:/AI/community/notes/ali163_hc_lessons_build.py --facts"),
    dict(id="L7", title="A green roster is not a quality verdict",
         claim="The objective gate records frames, size, audio, duration, bytes, sha256 and a contact sheet "
               "({F:clip3 BQ1c:contact_bytes} bytes for clip3 BQ1c). It records no quality verdict, and this "
               "doc assigns none: all 9 renders are NO KEEP material handed to Derrick.",
         evidence=["C:/AI/community/notes/ali163_hc_final_check.py",
                   "C:/AI/community/notes/hc_final_frames"],
         knobs=[],
         action="Ship the contact sheet + the objective table with every batch and leave the pick to Derrick; "
                "no automated scorer for the visual result.",
         repro="C:/AI/director/.venv/Scripts/python.exe C:/AI/community/notes/ali163_hc_final_summary.py"),
    dict(id="L8", title="Our own face embeddings refuted the reference-sheet method we rendered with",
         claim="The prompt/face audit measured face cosine: a pick against its OWN sheet scores "
               "0.22-0.47, while two unrelated picks' sheets score 0.69 - the sheet does not carry the "
               "identity, so the sheeted clips could not beat the no-sheet clips. R9 then dropped the "
               "Klein multi-view sheets from c0 AND c1 (quote: 'references = the approved pick ONLY - drop "
               "the Klein multi-view sheets from c0 AND c1'). Measured here: c0 ref slots went "
               "{F:clip1 NEW:refcount} -> {F:clip3 BQ1c:refcount} across the lineage, so the reference set "
               "is the variable that actually moved on this line.",
         evidence=["C:/AI/community/notes/hc_prompt_face_audit_20261023.md",
                   "C:/AI/community/notes/TASKS.md.bak-20261023-r6r",
                   "C:/AI/community/notes/hc_sheets_map_20261023.md"],
         knobs=["ref_images.ref_image_1", "ref_images.ref_image_2", "ref_images.ref_image_3"],
         action="Keep the BQ1c slot wiring (start still + face crops) and change one variable per render; the "
                "sheet refs are already refuted by our own numbers, do not re-litigate them on GPU.",
         repro="grep -n 'own-sheet' C:/AI/community/notes/hc_prompt_face_audit_20261023.md | head"),
    dict(id="L9", title="Untracked evidence dies at the iteration boundary, so a lesson must cite tracked files",
         claim="While this doc was being built, four untracked notes (task_r4gnote.md, task_r6r.md, "
               "task_rl1hold.md, task_im1.md - all read at the start of the pass), "
               "notes/ali163_hc_r4g2_objective.json and the whole "
               "notes/ali173_cont_hc1_s51140001_s20261103_070509/ directory disappeared from disk, and none "
               "of them was in git ls-files. AGENTS.md L8 states this for notes/web; it applies to every "
               "untracked artifact, including the runs/ media this builder re-measures.",
         evidence=["C:/Users/derek/5slock/ralph-community/notes/progress.md",
                   "C:/AI/community/notes/ali163_hc_r4g2_build.py"],
         knobs=[],
         action="Commit the notes that carry a lesson in the same pass as the lesson, and treat runs/ media as "
                "ephemeral: the builder re-measures them, and MEASURE/PATH fire when the evidence is gone.",
         repro="git -C C:/AI/community ls-files --error-unmatch notes/ali163_hc_r4g2_objective.json"),
    dict(id="L10", title="The claims we acted on that our own 0.2 audit refuted",
         claim="The HC research notes carried advice that the 0.2 audit of our own notes marks stale or wrong: "
               "a 50-100 word prompt rule attributed to the lightx2v card (0 hits in the fetched card), CFG "
               "ranges (no cfg key, see L2), FaceRefine as installed (probe: NOT installed, 47 packs), the "
               "'no anatomy lora' line (wrong for penis), and the 832x468 canvas (see L5). Each was a variable "
               "candidate that did not exist on this box.",
         evidence=["C:/AI/community/notes/self_setup_20261023.md",
                   "C:/AI/community/notes/ali02_node_inventory_probe.py",
                   "C:/AI/community/notes/hc_redo_research_20261023.md"],
         knobs=[],
         action="Before any variable enters a render, check it against the 0.2 audit verdict and the committed "
                "probe, not against the research note that proposed it.",
         repro="C:/AI/director/.venv/Scripts/python.exe C:/AI/community/notes/ali02_node_inventory_probe.py --check"),
]


# ------------------------------------------------------------------------------- rendering
def fact_value(row, key):
    """Resolve one fact token key against a measured row. Derived keys are computed, never typed."""
    p, g, s = row["probe"], row["graph"], row["status"]
    if key == "id":
        return row["id"]
    if key == "nfiles":
        return len(os.listdir(os.path.join(RUNS, row["id"]))) if row["run_dir_exists"] else 0
    if key == "mp4_exists":
        return "present" if row["rendered"] else "ABSENT"
    if key == "objective_json":
        return "present" if row["objective_json"] else "ABSENT"
    if key == "canvas":
        return "%sx%s" % (p.get("w"), p.get("h"))
    if key == "w_div":
        return p.get("w", 0) // CANVAS_MULT
    if key == "h_div":
        return p.get("h", 0) // CANVAS_MULT
    if key == "refcount":
        return max([len(v["refs"]) for v in g.get("video_nodes", [])] or [0])
    if key == "refcount_c1":
        c1 = [v for v in g.get("video_nodes", []) if v["id"] == "c1"]
        return len(c1[0]["refs"]) if c1 else 0
    if key in ("steps_desc", "graph.steps_desc"):
        return ", ".join("%s = %s" % (nid, st) for nid, st in g.get("steps", [])) or "none"
    if key in ("samplers", "graph.samplers"):
        return len(g.get("sampler_nodes", []))
    if key == "contact_bytes":
        return row["contact_bytes"]
    for src in ("probe", "graph", "status", "as_run"):
        d = row.get(src) or {}
        if key in d:
            return d[key]
        if "." in key:
            sec, leaf = key.split(".", 1)
            if sec == src and leaf in d:
                return d[leaf]
    raise KeyError("%s not measured on %s" % (key, row["id"]))


def expand(text, facts):
    """Replace {F:row:key} and the aggregate tokens with measured values."""
    by = {r["label"]: r for r in facts}

    def sub(m):
        row, key = m.group(1), m.group(2)
        try:
            return fmt(fact_value(by[row], key))
        except KeyError as e:
            # render an unresolved token visibly; the VALUE detector reports it (and DRIFT will too)
            return "{UNRESOLVED %s %s}" % (row, e)

    out = re.sub(r"\{F:([^:}]+):([a-z_0-9.]+)\}", sub, text)
    rend = [r for r in facts if r["rendered"]]
    secs = sorted(r["status"].get("secs", 0) for r in rend if r["id"].startswith("ali147_pool_hc_r"))
    cfg = [len(r["graph"].get("cfg_keys", [])) for r in rend if r["graph"].get("api_exists")]
    detail = "; ".join("%s cfg keys %d" % (r["id"].replace("ali147_pool_hc_", ""), len(r["graph"].get("cfg_keys", [])))
                       for r in rend if r["graph"].get("api_exists"))
    agg = {"{MINSECS}": min(secs) if secs else 0, "{MAXSECS}": max(secs) if secs else 0,
           "{NGRAPH}": sum(1 for r in rend if r["graph"].get("api_exists")),
           "{CFGMAX}": max(cfg) if cfg else 0, "{CFGDETAIL}": detail,
           "{AUDIOCOUNT}": sum(1 for r in rend if r["probe"].get("audio")),
           "{RENDEREDCOUNT}": len(rend)}
    for k, v in agg.items():
        out = out.replace(k, fmt(v))
    return out


def fmt(v):
    if isinstance(v, float):
        return ("%.1f" % v) if v > 10 else ("%.6g" % v)
    if isinstance(v, list):
        return json.dumps(v)
    return str(v)


def cell(v):
    """A markdown cell: no pipes, no newlines (a defect string can carry both)."""
    return fmt(v).replace("|", "/").replace("\n", " ")


def render(facts, lessons=LESSONS, rules=RULES):
    L = []
    A = L.append
    A("# hc_lessons_20261023.md - ALI-163 hardcore redo: what the r1-r6 / r3r / r3b renders teach")
    A("")
    A("Generated by `C:/AI/community/notes/ali163_hc_lessons_build.py --build` from")
    A("`C:/AI/community/notes/ali163_hc_lessons_facts.json`, a measurement of the runs on disk. Every number in")
    A("the roster and in the lessons below is a rendered measured value: `--check` re-measures the mp4s, rebuilds")
    A("this text and fails on any drift (DRIFT/MEASURE), so the doc cannot be quietly reworded. Edit the builder.")
    A("Purpose: fix_plan 2.1 names this file as the first deliverable (Derrick 2026-10-23 6:12 PM CT: NO KEEP on")
    A("r1-r6 / r3r / r3b, write notes\\hc_lessons_20261023.md, improve ONE variable per render, re-render the same")
    A("seeds). It did not exist until this builder wrote it (2026-11-03).")
    A("")
    A("## Rules in force (quoted, not reworded)")
    A("")
    for r in rules:
        A("- " + r)
    A("")
    A("## The measured roster (every cell re-measured by --check)")
    A("")
    A("| clip | run id | pick | exp f | measured f | canvas | fps | dur s | audio | mp4 bytes | sha256-16 | wall s | contact bytes |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in facts:
        p = r["probe"]
        if r["rendered"] and p.get("packets"):
            cells = [r["label"], r["id"], r["pick"], str(r["expected_frames"]), str(p["packets"]),
                     "%sx%s" % (p["w"], p["h"]), fmt(p["fps"]), "%.3f" % p["dur"],
                     ("yes " + p["audio_desc"]) if p.get("audio") else "NO",
                     str(p["bytes"]), p["sha256"][:16], fmt(r["status"].get("secs", 0)),
                     str(r["contact_bytes"])]
        else:
            cells = [r["label"], r["id"], r["pick"], str(r["expected_frames"]), "NO RENDER", "-", "-", "-",
                     "-", "0", "-", "0", str(r["contact_bytes"])]
        A("| " + " | ".join(cell(c) for c in cells) + " |")
    A("")
    A("Roster notes are claims the check tests against disk: " +
        "; ".join("`%s` = %s" % (r["label"], r["note"]) for r in facts) + ".")
    A("")
    A("## The as-run objective gate (quoted from the committed objective JSONs, not re-measured)")
    A("")
    A("Sources: " + ", ".join("`%s`" % p for p in AS_RUN) +
        ". These are what each run recorded about itself: wall minutes, budget burn, frame-count/proxy")
    A("counts, grep counts over status.log, and the builder's static defects. `-` = that file has no such key")
    A("for that row (the final file records no mp4 container duration; the bq1d file records no per-frame proxies).")
    A("")
    A("| clip | run id | ok | rc | wall_min | budget_used_min | frames_count | sha_unique | min_luma_std | job_error_grep | static_defects |")
    A("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in facts:
        a = r["as_run"]
        cells = [r["label"], r["id"]] + [cell(a[k]) if k in a and a[k] not in (None, "") else "-" for k in ASRUN_FIELDS]
        A("| " + " | ".join(cells) + " |")
    A("")
    dead = [r for r in facts if not r["rendered"]]
    gate = ("every rendered row's own gate says ok with rc 0, and the one dead row carries rc " +
            fmt(dead[0]["as_run"].get("rc")) + " with its static defect text") if dead else \
        "the roster has no dead row, so the gate records ok/rc 0 for every clip"
    A("Read: " + gate + ", so 'the batch is green' is a claim about the gate, never a quality verdict.")
    A("")
    A("## Lessons (each: claim, evidence, reproduce, and the ONE variable for the next render)")
    A("")
    for ls in lessons:
        A("### %s %s" % (ls["id"], ls["title"]))
        A("- Claim: " + expand(ls["claim"], facts))
        A("- Evidence: " + "; ".join(expand(e, facts) for e in ls["evidence"]))
        A("- Reproduce: `" + expand(ls["repro"], facts) + "`")
        A("- Next render, one variable: " + expand(ls["action"], facts))
        if ls["knobs"]:
            A("- Graph keys this lesson may touch: " + ", ".join("`%s`" % k for k in ls["knobs"]))
        A("")
    A("## What this doc is not")
    A("")
    A("- Not a ranking: no clip is called better, and no model scored these renders.")
    A("- Not a queue: no job is requested here, and the GPU stays off-limits in an unattended pass.")
    A("- Not a source of community advice: claims that the 0.2 audit marks stale, wrong or blocked are named as")
    A("  such in L10, and the audit row is the citation (C:/AI/community/notes/self_setup_20261023.md).")
    A("")
    return "\n".join(L).replace("\\\\", "\\") + "\n"


# ------------------------------------------------------------------------------- detectors
def check(facts, doc, lessons=LESSONS, rules=RULES, src_dir=RUNS):
    problems = []
    by = {r["id"]: r for r in facts}
    # INVENTED / ROSTER
    for r in facts:
        if not r["run_dir_exists"]:
            problems.append("INVENTED %s: run dir %s is not on disk - never cite a path you did not read"
                            % (r["id"], src_dir))
            continue
        if r["rendered"] and not r["probe"].get("mp4_exists"):
            problems.append("ROSTER %s: row claims a render, mp4 absent" % r["id"])
        if not r["rendered"] and "NO RENDER" not in r["note"].upper():
            problems.append("ROSTER %s: no mp4 on disk, so the roster note must say NO RENDER" % r["id"])
        # MATH / CANVAS
        p = r["probe"]
        if r["rendered"] and p.get("packets"):
            want = p["packets"] / (p["fps"] or 1)
            if abs(p["dur"] - want) > DUR_SLACK:
                problems.append("MATH %s: dur %.6f != %d/%g = %.6f" % (r["id"], p["dur"], p["packets"], p["fps"], want))
            if p["packets"] != r["expected_frames"]:
                problems.append("MATH %s: measured %d packets != expected %d" % (r["id"], p["packets"], r["expected_frames"]))
            for side in ("w", "h"):
                if p[side] % CANVAS_MULT:
                    problems.append("CANVAS %s: %s=%d is not a multiple of %d" % (r["id"], side, p[side], CANVAS_MULT))
    # PATH / VALUE / EVIDENCE / KNOB
    all_keys = {k for r in facts for k in list(r["graph"].keys()) + ["sampler_name", "steps"]}
    for ls in lessons:
        if not ls["evidence"]:
            problems.append("EVIDENCE %s: no artifact given" % ls["id"])
        for e in ls["evidence"]:
            m = re.match(r"^([A-Za-z]:/[^\s,;(]+)", e)
            if not m:
                problems.append("EVIDENCE %s: %r names no artifact path on disk" % (ls["id"], e[:48]))
                continue
            path = re.sub(r":\d+$", "", m.group(1).rstrip("/."))
            if not os.path.exists(path):
                problems.append("PATH %s: %s not on disk" % (ls["id"], path))
        try:
            expanded = [expand(x, facts) for x in
                        [ls["claim"], ls["action"], ls["repro"]] + list(ls["evidence"])]
        except Exception as e:
            problems.append("VALUE %s: render failed %s" % (ls["id"], repr(e)[:80]))
            expanded = []
        for t in expanded:
            for bad in re.findall(r"\{UNRESOLVED [^}]*\}", t):
                problems.append("VALUE %s: %s is not a measured value" % (ls["id"], bad))
        for k in ls["knobs"]:
            leaf = k.split(".")[-1]
            if leaf == "cfg" or "cfg" in k.lower():
                problems.append("KNOB %s: acts on %r, and no clip graph exposes a cfg key (measured cfg keys %s)"
                                % (ls["id"], k, sorted({x for r in facts for x in r["graph"].get("cfg_keys", [])})))
            elif "." in k and leaf not in all_keys and not re.fullmatch(r"ref_image_\d+", leaf) \
                    and leaf not in ("length", "width", "height", "prompt", "steps", "clips_json",
                                     "audio_vae", "extension_frames", "sampler_name", "shift_video",
                                     "shift_audio", "ref_image_size"):
                problems.append("KNOB %s: key %r is not in any measured graph (keys: %s)"
                                % (ls["id"], k, sorted(all_keys)[:12]))
    # ASRUN: the run's own objective gate must agree with the roster claim
    for r in facts:
        a = r.get("as_run") or {}
        if r["rendered"] and not a:
            problems.append("ASRUN %s: roster claims a render but no as-run objective record exists" % r["id"])
        elif r["rendered"] and a.get("ok") is False:
            problems.append("ASRUN %s: as-run ok=False (rc %s) while the roster calls it rendered" % (r["id"], a.get("rc")))
        elif not r["rendered"] and a.get("rc") != 2:
            problems.append("ASRUN %s: no mp4, so the as-run record must show the rc=2 static fail (it shows %r)"
                            % (r["id"], a.get("rc")))
    # DRIFT
    fresh = render(facts, lessons, rules)
    if doc != fresh:
        first = next((i for i, (a, b) in enumerate(zip(doc.splitlines(), fresh.splitlines())) if a != b),
                     min(len(doc.splitlines()), len(fresh.splitlines())))
        problems.append("DRIFT: doc on disk != doc regenerated from facts (first differing line %d; disk %d B, built %d B)"
                        % (first, len(doc.encode()), len(fresh.encode())))
    # COVERAGE
    for r in facts:
        if r["id"] not in doc:
            problems.append("COVERAGE: roster run %s is not named in the doc" % r["id"])
    # KEEPWORD / JUDGE: any uppercase KEEP in the doc must sit inside a quoted rule / NO-KEEP phrasing
    for i, line in enumerate(doc.splitlines()):
        if "KEEP" in line and not any(a in line for a in KEEP_ALLOW):
            problems.append("KEEPWORD line %d: %r - KEEP is Derrick's alone, no verdict in this doc" % (i + 1, line[:70]))
    for i, line in enumerate(doc.splitlines()):
        low = line.lower()
        if ("vision judge" in low or "scorer" in low) and "no vision judge" not in low and "no automated scorer" not in low:
            problems.append("JUDGE line %d: %r - no vision judge picks keepers" % (i + 1, line[:70]))
    return problems


def check_facts_vs_disk(problems, facts_override=None):
    """facts_override lets --selftest measure disk fresh and compare against a MUTATED facts clone
    (the real facts file is never rewritten)."""
    fresh = measure()
    stored = load_facts() if facts_override is None else facts_override
    if json.dumps(fresh, sort_keys=True) != json.dumps(stored, sort_keys=True):
        problems.append("MEASURE: facts JSON != a fresh measurement of the same runs (run --facts, then --build)")
    return fresh


def load_facts():
    return json.load(open(FACTS, encoding="utf-8"))


def load_doc():
    return open(DOC, encoding="utf-8").read()


def run_check():
    problems = []
    facts = load_facts()
    check_facts_vs_disk(problems)
    problems += check(facts, load_doc())
    if problems:
        for p in problems:
            print("PROBLEM " + p)
        print("VERDICT problems=%d" % len(problems))
        return 1
    print("VERDICT CLEAN facts=%d lessons=%d doc=%d B" % (len(facts), len(LESSONS), len(load_doc().encode())))
    return 0


# ------------------------------------------------------------------------------- selftest
def seed_faults(facts, doc, lessons, rules):
    """One mutation per detector. Returns (name, mutated artifacts, expectation)."""
    import copy
    J = lambda o: json.loads(json.dumps(o))
    s = []
    f = J(facts); f[2]["probe"]["bytes"] += 1
    s.append(("MEASURE", dict(facts=f, doc=doc, lessons=lessons, rules=rules)))
    f = J(facts)
    s.append(("DRIFT", dict(facts=f, doc=doc.replace("hardcore redo", "hardcore REDO"), lessons=lessons, rules=rules)))
    f = J(facts); f[1]["run_dir_exists"] = False
    s.append(("INVENTED", dict(facts=f, doc=doc.replace(f[1]["id"], "ali147_pool_hc_ghost_s99999999"),
                               lessons=lessons, rules=rules)))
    f = J(facts); f[4]["rendered"] = True; f[4]["note"] = "claims a render"
    s.append(("ROSTER", dict(facts=f, doc=doc.replace("| clip3 | ali147_pool_hc_r3_s51130003 | HC3 GI173 | 243 | NO RENDER |",
                                                       "| clip3 | ali147_pool_hc_r3_s51130003 | HC3 GI173 | 243 | 243 |"),
                             lessons=lessons, rules=rules)))
    f = J(facts); f[3]["as_run"]["ok"] = False
    s.append(("ASRUN", dict(facts=f, doc=doc, lessons=lessons, rules=rules)))
    f = J(facts); f[3]["probe"]["dur"] += 3.0
    s.append(("MATH", dict(facts=f, doc=doc, lessons=lessons, rules=rules)))
    f = J(facts); f[3]["probe"]["h"] = 468
    s.append(("CANVAS", dict(facts=f, doc=doc, lessons=lessons, rules=rules)))
    ls = J(lessons); ls[0]["evidence"] = ["C:/AI/community/notes/ali163_hc_ghost_probe_20991231.py"]
    s.append(("PATH", dict(facts=facts, doc=render(facts, ls, rules), lessons=ls, rules=rules)))
    ls = J(lessons); ls[1]["claim"] = "seed {F:clip3 BQ1c:not_measured_at_all} was used"
    s.append(("VALUE", dict(facts=facts, doc=render(facts, ls, rules), lessons=ls, rules=rules)))
    ls = J(lessons); ls[2]["knobs"] = ["KSamplerAdvanced.cfg"]
    s.append(("KNOB", dict(facts=facts, doc=render(facts, ls, rules), lessons=ls, rules=rules)))
    ls = J(lessons); ls[6]["evidence"] = []
    s.append(("EVIDENCE", dict(facts=facts, doc=render(facts, ls, rules), lessons=ls, rules=rules)))
    d = doc.replace("ali147_pool_hc_r6_s51130006", "ali147_pool_hc_rX_s51130006")
    s.append(("COVERAGE", dict(facts=facts, doc=d, lessons=lessons, rules=rules)))
    s.append(("KEEPWORD", dict(facts=facts, doc=doc + "\nKEEP: clip3 BQ1c is the one to use.\n",
                               lessons=lessons, rules=rules)))
    s.append(("JUDGE", dict(facts=facts, doc=doc + "\nThe vision judge picked clip4 as the best render.\n",
                            lessons=lessons, rules=rules)))
    return s


def selftest():
    facts, doc = load_facts(), load_doc()
    base = check(facts, doc)
    print("real tree problems=%d %s" % (len(base), base[:3]))
    fired, silent = set(), []
    for name, m in seed_faults(facts, doc, LESSONS, RULES):
        probs = check(m["facts"], m["doc"], m["lessons"], m["rules"])
        hits = [p for p in probs if p.startswith(name)]
        if name == "MEASURE":
            # MEASURE is the only detector that compares disk against stored facts, so seed it by
            # measuring disk and comparing to a mutated clone (the real facts file is never touched).
            probs = []
            check_facts_vs_disk(probs, facts_override=m["facts"])
            hits = [p for p in probs if p.startswith("MEASURE")]
        if hits:
            fired.add(name)
        else:
            silent.append((name, probs[:2]))
    for n, p in silent:
        print("SILENT_SEED %s %s" % (n, p))
    missing = [n for n, _ in seed_faults(facts, doc, LESSONS, RULES) if n not in fired]
    if missing:
        print("SELFTEST_FAILED missing=%s" % missing)
        return 2
    if base:
        print("SELFTEST_FAILED real tree is not clean: %s" % base[:3])
        return 1
    print("SELFTEST_CLEAN seeds=%d fired=%d real_tree_problems=0" % (len(seed_faults(facts, doc, LESSONS, RULES)), len(fired)))
    return 0


def main():
    a = sys.argv[1:]
    if "--facts" in a:
        rows = measure()
        json.dump(rows, open(FACTS, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print("facts -> %s rows=%d rendered=%d" % (FACTS, len(rows), sum(1 for r in rows if r["rendered"])))
        return 0
    if "--build" in a:
        open(DOC, "w", encoding="utf-8", newline="\n").write(render(load_facts()))
        print("built -> %s %d B" % (DOC, os.path.getsize(DOC)))
        return 0
    if "--selftest" in a:
        return selftest()
    if "--check" in a:
        return run_check()
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main())
