r"""top5_build.py - E5 EULER-5S: back to euler, a real 5-second clip, a 350-500 word prompt.

Derrick 2026-10-25 6:48 PM CT (MAX block, fix_plan.md L18): "Go back to Euler, 5-second clips and
350-500 word prompts." 10:40 AM: "I just want the 5 second clips to be good and I will choose the scenes."

WHAT THE SHIPPED GRAPHS DO (measured by --state on the 17 files in C:/AI/community/p7/graphs at
2026-10-25 22:1x CT): every one totals 362 frames = 15.083 s at 24 fps. The s5115000x line is
euler with c0 length 124 and TWO MiniMaxH3GuidedContinuationWindow passes (124+119+119); the
s5115001x/s51150021/s5115003x line is res_multistep with c0 length 243 and ONE window (243+119).
No shipped graph is a 5-second clip; the c0 length is only the FIRST pass. c0 main-field words run
413-497, so the word band was already close - sampler and clip length are the drift.

WHY A SINGLE PASS IS THE RIGHT SHAPE (published, saved in C:/AI/community/notes/web/):
  02v_core_nodes_minimax_head.txt:266  MiniMaxH3ReferenceToVideo length "default=124, min=5, max=3600,
      step=17", tooltip "(124 = ~5s, trained range is ~124-362)" - 124 frames at 24 fps = 5.167 s and
      124 % 17 = 5, the same 17k+5 grid the shipped 243 uses.
  02v_docs_h3.txt:181-183 "Sampler and scheduler": "res_multistep is second-order multistep (first step
      is Euler). Splitting the schedule across two samplers drops multistep history: the second sampler's
      first step is first-order again. Keep one sampler run, or give the second enough steps to warm up."
      A one-pass 124-frame clip is "one sampler run", and euler is the first-order sampler that run wants.
  02v_core_nodes_minimax_head.txt:286 - the node outputs [Conditioning positive, Latent], the same
      LATENT type SamplerCustomAdvanced returns, so one pass feeds VAEDecode + VAEDecodeAudio directly.
NOT changed here (the item names three axes; IM1's one-variable rule): steps (8), scheduler (simple),
shift (video 10 / audio 3), canvas (1344x768), the MiniMaxH3AddGuide at frame 0, the
ModelAttentionBackend/BlockSparseAttention chain (Derrick's separate "Comfy Kitchen attention conflict"
pick), LoRAs, the reference slots, fps. Published rows recorded for the owner: 02v_docs_h3.txt:170
"Simple shots: 12-16 steps often enough", :174 "Speech and timbre need 12+ steps; at 8 steps audio is
often the weak link", and the R2V 4-step default with "For tight reference match ... raise toward 25".

THE CHANGE SET, as a diff of graph paths (check `derive`): drop the continuation half of
ali163_hc15_gi046_s51150032.api.json (c1, win1, tail1, app1, s1_guide, s1_sched, s1_samp), rewire
dec_v.samples and dec_a.samples from app1[0] to s0_samp[0], and set exactly c0.length 124,
ksel.sampler_name "euler", c0.prompt = the block in notes/top5_prompts.md, noise.noise_seed 51160001
(a new family; 5115003x is the 15 s family), save.filename_prefix for the new id. Nothing else.

THE PROMPT: notes/top5_prompts.md, one c0 block in the IM1 shape (notes/im1_prompts.md), gate reusing
notes/ali31_prompt_set_check.py (sections, 350-500 word band on the main field, beats inside the window
the graph measures, camera terms + amplitude/speed, negation count) and
notes/hc15_anchor_carry_build.py card_measure/card_fires against C:/AI/community/notes/scenes/GI046.facts.json
(the card CARD-VL rebuilt at 21:58 CT from the uncensored vl_judge captions). One card row is
provably unsatisfiable - gate.open_beat demands "lying prone on stomach" for figure 1 in the opening beat
while gate.open_beat_ban forbids the substring "lying" for figure 2 in that same single string - so this
file measures that with a constructed minimal prompt (check `card_unsat`) and requires the emitted
prompt's card-firing set to be exactly that one row, reported to the card owner.

MODES
  --state            print the measured shape of every shipped HC15 graph (reads, writes nothing)
  --emit             write p7/graphs/<id>.api.json + runs/<id>/request.api.json, print bytes/sha256
  --check            build in memory, run every check, write notes/top5_manifest_<id>.json, print VERDICT
  --selftest         mutate a copy per seed, require the NAMED check to fire, and require 0 findings on
                     the real artifact; prints SELFTEST OK / ABORT
No GPU, no queue, no network: the schema check is the offline clone of run_graph_job.static_check
(ali163_hc_r4g2_build.h3_schema/scan, parsed from comfy_extras/nodes_minimax_h3.py)."""
import sys, os, re, json, copy, hashlib, glob, argparse
import shutil, tempfile                      # the paid-state probes build each disk state in a temp root

C = "C:/AI/community"
sys.path.insert(0, os.path.join(C, "notes"))
import hc15_anchor_carry_build as HC            # card gate + windows + sha
import ali31_prompt_set_check as A31            # IM1 prompt shape: blocks, band, beats, camera, diff
import ali163_hc_r4g2_build as R4               # offline H3 schema (the rc=2 class list)

DOC = os.path.join(C, "notes", "top5_prompts.md")
GRAPHS = os.path.join(C, "p7", "graphs")
RUNS = os.path.join(C, "runs")
SRC = "ali163_hc15_gi046_s51150032"
NEW = "ali163_top5_gi046_s51160001"
SCENE = "GI046"
SEED = 51160001
FRAMES = 124                       # 17k+5 grid, 5.167 s at 24 fps, inside the node's trained range
FPS = 24
DROP = {"c1", "win1", "tail1", "app1", "s1_guide", "s1_sched", "s1_samp"}
CONT_CLASSES = ("MiniMaxH3GuidedContinuationWindow", "MiniMaxH3AppendContinuation",
                "MiniMaxH3LatentTailGuide", "MiniMaxH3Ref2VA", "H3ContinuumWindow",
                "H3ContinuumSamplerV39", "MiniMaxH3Continuation")
# the whole allowed diff: 2 rewires + 5 values + the dropped nodes as "<id>.NODE"
ALLOWED_DIFF = {f"{n}.NODE" for n in DROP} | {
    "dec_v.samples", "dec_a.samples", "c0.length", "c0.prompt",
    "ksel.sampler_name", "noise.noise_seed", "save.filename_prefix"}
# the card row no wording can satisfy, with the reason (measured by card_unsat below)
CARD_KNOWN = ("F-CARD-POSE2",)
NEG_WORDS = HC.TOP_NEG_WORDS
WANT_SECTIONS = A31.SECTIONS["c0"]
MAIN = "detailed_description"
WORD_BAND = (350, 500)
SUMMARY_MAX = 200


def doc_block():
    """the one c0 block of the prompt doc: (id, seed, sections dict, whole body text)."""
    bs = A31.parse_blocks(open(DOC, encoding="utf-8").read())
    if len(bs) != 1:
        raise SystemExit(f"top5: {DOC} carries {len(bs)} prompt blocks, want exactly 1")
    b = bs[0]
    if b["chunk"] != "c0" or b["id"] != NEW or b["seed"] != SEED:
        raise SystemExit(f"top5: block header id={b['id']} chunk={b['chunk']} seed={b['seed']}, "
                         f"want id={NEW} chunk=c0 seed={SEED}")
    return b


def gload(nid):
    return json.load(open(os.path.join(GRAPHS, nid + ".api.json"), encoding="utf-8"))


def build():
    """the 5-second single-pass euler graph, derived from SRC by subtraction (pure: returns a dict)."""
    g = copy.deepcopy(gload(SRC))
    b = doc_block()
    for n in DROP:
        g.pop(n, None)
    g["dec_v"]["inputs"]["samples"] = ["s0_samp", 0]
    g["dec_a"]["inputs"]["samples"] = ["s0_samp", 0]
    for nd in g.values():                       # nothing may point into the dropped half
        for k, v in list(nd["inputs"].items()):
            if isinstance(v, list) and v[0] in DROP:
                raise SystemExit(f"top5: {k} still links to dropped node {v[0]}")
    g["c0"]["inputs"]["length"] = FRAMES
    g["c0"]["inputs"]["prompt"] = b["text"]
    g["ksel"]["inputs"]["sampler_name"] = "euler"
    g["noise"]["inputs"]["noise_seed"] = SEED
    g["save"]["inputs"]["filename_prefix"] = f"community/{NEW}/{NEW}"
    return g


def total_frames(g):
    fps = g["mkvid"]["inputs"]["fps"]
    n = g["c0"]["inputs"]["length"]
    for nd in g.values():
        if nd["class_type"] in ("MiniMaxH3GuidedContinuationWindow", "H3ContinuumWindow"):
            n += nd["inputs"].get("extension_frames", 0)
    return n, fps


def slot_edges(g):
    out = {}
    for nid, nd in g.items():
        if not nid.startswith("c"):
            continue
        out[nid] = {k: v for k, v in nd["inputs"].items()
                    if re.fullmatch(r"ref_images\.ref_image_\d+", k)}
    return out


def ref_files(g):
    """[(slot, LoadImage image path, absolute file, exists)] read the fullmatch way (AGENTS.md)."""
    out = []
    for ch, slots in sorted(slot_edges(g).items()):
        for k in sorted(slots):
            nd = g[slots[k][0]]
            out.append((f"{ch}.{k}", nd["inputs"]["image"],
                        os.path.join("C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/input",
                                     nd["inputs"]["image"].replace("/", os.sep)),
                        nd["class_type"] == "LoadImage"))
    return out


def sections_of(text):
    """a bare block body parsed the way notes/ali31_prompt_set_check.parse_blocks does it, so the
    graph payload (which carries the body, not the doc header) meets the same section gates."""
    body = re.sub(r"\n---\s*$", "", text.rstrip())
    return dict(re.findall(r"^([a-z_]+):$\n(.*?)(?=^\w[\w_]*:$|\Z)", body, flags=re.M | re.S))


def neg_count(text):
    return len([w for w in re.findall(r"[A-Za-z][A-Za-z'\-]*", text) if w.lower() in NEG_WORDS])


# ---------------------------------------------------------------------------- checks: each returns [] when it passes
def ck_derive(g, ctx):
    src = gload(SRC)
    d = A31.diff_paths(src, g)
    bad = [f"DERIVE {p} is outside the allowed change set" for p in d if p not in ALLOWED_DIFF]
    bad += [f"DERIVE allowed change {p} did not happen" for p in sorted(ALLOWED_DIFF) if p not in d]
    if set(g) & set(SRC) and set(g) - set(src):
        bad.append(f"DERIVE added nodes {sorted(set(g) - set(src))}")
    if set(src) - set(g) != DROP:
        bad.append(f"DERIVE dropped {sorted(set(src) - set(g))}, want {sorted(DROP)}")
    return bad


def ck_state(g, ctx):
    """the source really is the drifted shape (a source edited under this pass fires this)."""
    src = gload(SRC)
    n, fps = total_frames(src)
    out = []
    if [v["inputs"].get("sampler_name") for v in src.values()
        if v["class_type"] == "KSamplerSelect"] != ["res_multistep"]:
        out.append("STATE source sampler is not res_multistep - the drift this item reverses moved")
    if src["c0"]["inputs"]["length"] != 243 or (n, fps) != (362, FPS):
        out.append(f"STATE source shape is c0 243 / {n} f, not the measured 243 / 362 f")
    return out


def ck_frames(g, ctx):
    n, fps = total_frames(g)
    sec = n / fps
    out = []
    if g["c0"]["inputs"]["length"] != FRAMES:
        out.append(f"FRAMES c0 length {g['c0']['inputs']['length']} != {FRAMES}")
    if FRAMES % 17 != 5:
        out.append(f"FRAMES {FRAMES} is not on the 17k+5 grid the templates expose")
    if fps != FPS:
        out.append(f"FRAMES fps {fps} != {FPS}")
    if n != FRAMES:
        out.append(f"FRAMES graph total {n} != one pass of {FRAMES}")
    if not (5.0 <= sec <= 5.3):
        out.append(f"FRAMES {sec:.3f} s is not a 5-second clip")
    return out


def ck_single(g, ctx):
    cc = {k: v["class_type"] for k, v in g.items() if v["class_type"] in CONT_CLASSES}
    counts = {}
    for v in g.values():
        counts[v["class_type"]] = counts.get(v["class_type"], 0) + 1
    out = []
    if cc:
        out.append(f"SINGLE continuation nodes present {cc}")
    for cls, want in (("MiniMaxH3ReferenceToVideo", 1), ("SamplerCustomAdvanced", 1),
                      ("BasicScheduler", 1), ("BasicGuider", 1), ("KSamplerSelect", 1)):
        if counts.get(cls, 0) != want:
            out.append(f"SINGLE {counts.get(cls, 0)} {cls} nodes, want {want} (one sampler run)")
    return out


def ck_sampler(g, ctx):
    names = [v["inputs"].get("sampler_name") for v in g.values() if v["class_type"] == "KSamplerSelect"]
    return [] if names == ["euler"] else [f"SAMPLER ksel.sampler_name {names}, want ['euler']"]


def ck_untouched(g, ctx):
    """the axes the item does NOT name stay byte-identical to the source."""
    src = gload(SRC)
    out = []
    if g["s0_sched"]["inputs"] != src["s0_sched"]["inputs"]:
        out.append(f"UNTOUCHED s0_sched changed {src['s0_sched']['inputs']} -> {g['s0_sched']['inputs']}")
    for nid in ("m_shift", "m_attn", "m_vsa", "unet", "clip", "vvae", "avae", "g0", "mkvid", "ksel"):
        if nid == "ksel":
            continue
        if g[nid]["inputs"] != src[nid]["inputs"]:
            out.append(f"UNTOUCHED {nid} inputs changed")
    for nid in ("c0",):
        for k in ("width", "height", "ref_image_size"):
            if g[nid]["inputs"].get(k) != src[nid]["inputs"].get(k):
                out.append(f"UNTOUCHED {nid}.{k} changed")
    if slot_edges(g).get("c0", {}) != slot_edges(src).get("c0", {}):
        out.append(f"UNTOUCHED the c0 reference slots changed {sorted(slot_edges(g).get('c0', {}))} "
                   f"vs {sorted(slot_edges(src).get('c0', {}))}")
    # keyed by slot and restricted to the slots the 5-second graph still has: the source's c1 slots are
    # legitimately gone with the continuation half, so a whole-list compare would charge that as a change.
    mine = {t[0]: t[1] for t in ref_files(g)}
    theirs = {k: v for k, v in ((t[0], t[1]) for t in ref_files(src)) if k in mine}
    if mine != theirs:
        out.append("UNTOUCHED a reference file target changed "
                   + json.dumps({k: [theirs.get(k), mine[k]] for k in mine if mine[k] != theirs.get(k)}))
    if g["noise"]["inputs"]["noise_seed"] == src["noise"]["inputs"]["noise_seed"]:
        out.append("UNTOUCHED noise_seed is the source seed - a new config renders on a new seed")
    return out


def ck_refs_exist(g, ctx):
    out = []
    for slot, rel, abspath, is_load in ref_files(g):
        if not is_load:
            out.append(f"REFS {slot} is not a LoadImage node")
        elif not os.path.isfile(abspath):
            out.append(f"REFS {slot} resolves to a missing file {abspath}")
    want = {f"{SCENE}.jpg", f"{SCENE}_w1_face.png"}
    got = {os.path.basename(t[1]) for t in ref_files(g)}
    if got != want:
        out.append(f"REFS slots carry {sorted(got)}, want the approved {sorted(want)} "
                   "(a second face crop for a third slot does not exist for this scene)")
    return out


def ck_schema(g, ctx):
    return [f"SCHEMA {v}" for v in R4.scan(g, R4.h3_schema())]


def paid_state(id_, roots=None):
    """classify what a render left on disk. The three pieces of proof are the ones L20 names - `objective.json` +
    `status.log` in the run dir + the ComfyUI output folder - NOT `p7/jobs/<id>.result.json`, which this render path
    does not write (measured 2026-10-25 23:3x: the job wrote runs/<id>/{status.log,objective.json} and
    ComfyUI/output/community/<id>/ and left no result.json; `p7/jobs/*.result.json` is the 38 older job-dir runs,
    newest 2026-10-24). All three = PAID: collect the clip, never re-render it (L19). None of them and no
    result.json = FREE, i.e. submittable (AGENTS.md: a request is submittable only while that file is absent).
    Any other mix = HALF-PAID, which no gate may call clean: a half-collected run is not a paid clip.
    `roots` lets --selftest probe every state on temp paths without touching the real run dir."""
    ev = [os.path.join(RUNS, id_, "objective.json"), os.path.join(RUNS, id_, "status.log"),
          os.path.join("C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/output/community", id_)]
    rj = os.path.join(C, "p7", "jobs", id_ + ".result.json")
    if roots:
        ev = [os.path.join(roots, "runs", id_, "objective.json"), os.path.join(roots, "runs", id_, "status.log"),
              os.path.join(roots, "out", id_)]
        rj = os.path.join(roots, "jobs", id_ + ".result.json")
    have = [p for p in ev if os.path.exists(p)]
    st = "paid" if len(have) == 3 else "free" if not have and not os.path.exists(rj) else "half-paid"
    return st, have, ev + [rj]


def ck_job_static(g, ctx):
    """the offline clone of run_graph_job's frame gate: the graph's ONE pass must total the --frames value the
    render passes, and no job may be queued while it is checked. The id-free rule is a PRE-SUBMIT condition and is
    asserted only while the id is unpaid: this item rendered its job, and the same three pieces of evidence that
    made this check read red at 23:0x CT (`VERDICT NOT CLEAN 1 of 18`, the selftest ABORTing on the real artifact)
    are the paid clip - a paid clip is never re-rendered (L19), so the gate must not demand the absence of the
    evidence the item exists to produce. A HALF-PAID id is still a fault."""
    n, _ = total_frames(g)
    out = []
    if n != FRAMES:
        out.append(f"JOBS-static graph total {n} != the --frames value {FRAMES}")
    st, have, _ = paid_state(NEW)
    if st == "half-paid":
        out.append(f"JOBS-static {NEW} is half-paid: {len(have)} of 3 evidence files exist: {have}")
    if os.path.exists(os.path.join(C, "p7", "JOB_REQUEST.json")):
        out.append("JOBS-static p7/JOB_REQUEST.json is already queued")
    return out


def ck_prompt_sync(g, ctx):
    b = ctx["block"]
    out = []
    if g["c0"]["inputs"]["prompt"] != b["text"]:
        out.append("SYNC the graph c0.prompt is not the doc block, byte for byte")
    if list(b["sections"].keys()) != WANT_SECTIONS:
        out.append(f"SYNC doc sections {list(b['sections'].keys())} != the c0 shape {WANT_SECTIONS}")
    if not str(g["noise"]["inputs"]["noise_seed"]) == str(b["seed"]):
        out.append("SYNC graph seed != the block header seed")
    if b["text"].lstrip().startswith("At "):
        out.append("SYNC the block body starts on a beat, not a section header")
    return out


def ck_words(g, ctx):
    sec = sections_of(ctx["prompt"])
    n = len(sec[MAIN].split())
    sw = len(sec["summary"].split())
    lo, hi = WORD_BAND
    out = []
    if not lo <= n <= hi:
        out.append(f"WORDS {MAIN} is {n} words, outside the {lo}-{hi} band Derrick set")
    if sw > SUMMARY_MAX:
        out.append(f"WORDS summary is {sw} words, over {SUMMARY_MAX}")
    return out


def ck_beats(g, ctx):
    n, fps = total_frames(g)
    hi = n / fps
    ts = A31.beat_times(ctx["prompt"])
    out = []
    if len(ts) < 3:
        out.append(f"BEATS {len(ts)} beats, want at least 3 across the clip")
    if not ts or ts[0] != 0.0:
        out.append(f"BEATS first beat is {ts[:1]}, want 00:00.000 (the graph is anchored at frame 0)")
    late = [t for t in ts if t > hi]
    if late:
        out.append(f"BEATS beats at {late} s sit past the {hi:.3f} s this clip is")
    return out


def ck_camera(g, ctx):
    m = sections_of(ctx["prompt"])[MAIN]
    out = []
    if not any(t in m for t in A31.CAM_TERMS):
        out.append("CAMERA no canon camera term in the main field")
    if "amplitude" not in m or "speed" not in m:
        out.append("CAMERA no amplitude/speed wording")
    if not re.search(r"stops and holds|the camera holds", m):
        out.append("CAMERA the published move shape ends in a stop; the guide wants the last 2/3 held")
    return out


def ck_negation(g, ctx):
    n = neg_count(ctx["prompt"])
    return [] if n <= 2 else [f"NEGATION {n} negation tokens, over the shipped 2"]


def ck_ages(g, ctx):
    p = ctx["prompt"]
    out = []
    for lab in sorted(set(re.findall(r"<Subject\s*(\d+)>", p))):
        line = next((s for s in re.split(r"\n", p) if re.search(rf"<Subject\s*{lab}>.*aged", s)), "")
        m = re.search(r"aged (\d{2})", line)
        if not m:
            out.append(f"AGES <Subject {lab}> carries no 'aged NN'")
        elif int(m.group(1)) < 21:
            out.append(f"AGES <Subject {lab}> states {m.group(1)}, under the adult floor 21")
        elif "canon declaration" not in line:
            out.append(f"AGES <Subject {lab}> states an age with no canon declaration")
    return out


def ck_card(g, ctx):
    fires = HC.card_fires(SCENE, HC.card_measure(SCENE, ctx["prompt"]))
    out = [f"CARD {code} {det}" for code, det in fires if code not in CARD_KNOWN]
    if tuple(sorted({c for c, _ in fires})) != CARD_KNOWN:
        out.append(f"CARD firing set {sorted({c for c, _ in fires})} is not exactly the one "
                   f"measured-unsatisfiable row {list(CARD_KNOWN)} - see card_unsat")
    return out


MINIMAL = """subject_definitions:
<Subject 1> is the human female, a fictional adult aged 27 (canon declaration), lying prone on stomach
on the beige shag rug, propped on forearms, in an interior living space with dark wood flooring and a
beige upholstered sofa, wearing the silver chain-link bikini top and bottom, the silver chain-link bikini
and choker, the sparkling tiara, blonde, long and wavy, light, glossy, slim, toned, her head in frame, both of them
consent.
<Subject 2> is the green-skinned humanoid, a fictional adult aged 34 (canon declaration), extremely
muscular, large hands and feet, skin green, textured with visible muscle definition, in black athletic
shorts, kneeling behind figure 1, head out of frame.
soft, diffused lighting from front-left, highlights on skin and metallic jewelry, no direct sunlight.

summary:
x

detailed_description:
At 00:00.000, the frame is the start photograph: a human female aged 27 (canon declaration) lying prone
on stomach, propped on forearms, hips lifted; the green-skinned humanoid aged 34 (canon declaration)
kneeling behind figure 1, leaning forward with both hands placed on figure 1's lower back and thigh.
Push In with small amplitude at slow speed, Static Shot, and the camera stops and holds.

overall_soundscape:
room tone.

non_diegetic_music:
low guitar."""


def ck_card_unsat(g, ctx):
    """the card's own contradiction, measured: a prompt that satisfies every required open_beat pose for
    both figures in one opening beat MUST contain 'lying' (figure 1's card pose), and open_beat_ban
    charges 'lying' to figure 2 in that same string. The row passes only while the fixture fires that
    exact rule; if the card is repaired so it stops firing, this check says so."""
    fires = dict((c, d) for c, d in HC.card_fires(SCENE, HC.card_measure(SCENE, MINIMAL)))
    out = []
    miss = HC.card_measure(SCENE, MINIMAL)["beat0_pose"]
    if any(miss.values()):
        out.append(f"CARD-UNSAT fixture fails open_beat poses {miss}, so it proves nothing")
    if "F-CARD-POSE2" not in fires:
        out.append("CARD-UNSAT the constructed minimal prompt no longer fires F-CARD-POSE2: the card's "
                   "open_beat / open_beat_ban contradiction is repaired, so drop the exception")
    if not str(fires.get("F-CARD-POSE2", "")).startswith("figure 2 opening beat says lying"):
        out.append(f"CARD-UNSAT fixture fires {sorted(fires)}; the named row must be the "
                   f"'lying'-for-figure-2 charge, got {fires.get('F-CARD-POSE2')}")
    return out


def ck_no_judge(g, ctx):
    return [f"NO-JUDGE manifest text carries {w}" for w in HC.BANNED_IN_MANIFEST
            if re.search(r"\b" + w + r"\b", json.dumps(ctx["manifest"], ensure_ascii=False), re.I)]


CHECKS = [("state", ck_state), ("derive", ck_derive), ("frames", ck_frames), ("single", ck_single),
          ("sampler", ck_sampler), ("untouched", ck_untouched), ("refs_exist", ck_refs_exist),
          ("schema", ck_schema), ("jobs_static", ck_job_static), ("prompt_sync", ck_prompt_sync),
          ("words", ck_words), ("beats", ck_beats), ("camera", ck_camera), ("negation", ck_negation),
          ("ages", ck_ages), ("card", ck_card), ("card_unsat", ck_card_unsat), ("no_judge", ck_no_judge)]


# ---------------------------------------------------------------------------- the record
def measure(g):
    b = doc_block()
    n, fps = total_frames(g)
    card = HC.card_measure(SCENE, b["text"])
    return {
        "as_of": "2026-10-25",
        "item": "E5 EULER-5S",
        "scene": SCENE,
        "graph": NEW,
        "graph_path": os.path.join(GRAPHS, NEW + ".api.json"),
        "source_graph": SRC,
        "source_sha256": HC.sha(os.path.join(GRAPHS, SRC + ".api.json")),
        "graph_sha256": hashlib.sha256(json.dumps(g, sort_keys=True).encode()).hexdigest(),
        "nodes": len(g),
        "dropped_nodes": sorted(DROP),
        "changed_paths": sorted(ALLOWED_DIFF),
        "prompt_doc": DOC,
        "prompt_keys": ["c0.inputs.prompt"],
        "prompt_words_main": len(b["sections"][MAIN].split()),
        "prompt_words_total": len(b["text"].split()),
        "word_band": list(WORD_BAND),
        "summary_words": len(b["sections"]["summary"].split()),
        "beats_s": A31.beat_times(b["text"]),
        "negation_tokens": neg_count(b["text"]),
        "ages": sorted({int(x) for x in re.findall(r"aged (\d{2})", b["text"])}),
        "frames": n, "fps": fps, "seconds": round(n / fps, 6),
        "sampler": g["ksel"]["inputs"]["sampler_name"],
        "steps": g["s0_sched"]["inputs"]["steps"],
        "shift": [g["m_shift"]["inputs"]["shift_video"], g["m_shift"]["inputs"]["shift_audio"]],
        "canvas": [g["c0"]["inputs"]["width"], g["c0"]["inputs"]["height"]],
        "ref_slots": [t[0] for t in ref_files(g)],
        "ref_files": [t[1] for t in ref_files(g)],
        "seed": g["noise"]["inputs"]["noise_seed"],
        "card_fires": [list(x) for x in HC.card_fires(SCENE, card)],
        "card_known_unsatisfiable": list(CARD_KNOWN),
        "card_measurement": {k: v for k, v in card.items() if v},
        "render_command": (f"C:/AI/director/.venv/Scripts/python.exe {C}/scripts/run_graph_job.py "
                           f"{os.path.join(RUNS, NEW)} {NEW} --frames {FRAMES}"),
    }


def write_graph(g):
    data = json.dumps(g, indent=2)
    os.makedirs(os.path.join(RUNS, NEW), exist_ok=True)
    with open(os.path.join(GRAPHS, NEW + ".api.json"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(data)
    with open(os.path.join(RUNS, NEW, "request.api.json"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(data)
    return data


def run_state():
    rows = []
    for p in sorted(glob.glob(os.path.join(GRAPHS, "ali163_hc15_*.api.json"))):
        g = json.load(open(p, encoding="utf-8"))
        ks = [v["inputs"].get("sampler_name") for v in g.values() if v["class_type"] == "KSamplerSelect"]
        n, fps = total_frames(g)
        w = A31.main_words({"chunk": "c0", "text": g["c0"]["inputs"]["prompt"]})
        rows.append((os.path.basename(p), len(g), ",".join(sorted(set(ks))), g["c0"]["inputs"]["length"],
                     n, round(n / fps, 3), w))
    print(f"{'graph':44s} nodes sampler        c0_len total  sec     c0_main_words")
    for r in rows:
        print(f"{r[0]:44s} {r[1]:5d} {r[2]:16s} {r[3]:6d} {r[4]:5d} {r[5]:7} {r[6]:5d}")
    tot = {r[5] for r in rows}
    print(f"STATE {len(rows)} shipped graphs, clip lengths {sorted(tot)} s, "
          f"c0_main_words {min(r[6] for r in rows)}-{max(r[6] for r in rows)} - "
          f"no shipped graph is a 5-second clip")
    return rows


# The paid-state rule is a live-disk rule, not an artifact rule, so it gets its own behaviour probe (L10: probe the
# behaviour; a seed that mutates nothing is not allowed). Build each disk state in a temp root and read the
# classification off paid_state(): `paid` and `free` are the two good states; one piece of evidence, and a lone
# p7/jobs result.json (the older job-dir path), are HALF-PAID and must not read clean.
PAID_CASES = [{"name": n, "make": m, "want": w} for n, m, w in (
    ("paid_all_three", ["obj", "log", "out"], "paid"),
    ("free_nothing_on_disk", [], "free"),
    ("half_paid_one_piece", ["obj"], "half-paid"),
    ("half_paid_old_job_dir_only", ["rj"], "half-paid"))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", action="store_true")
    ap.add_argument("--emit", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.state:
        run_state()
        return 0

    # A seed mutates a copy of the real graph (or the manifest row) and names the check that MUST fire
    # on it. A seed whose named check stays silent is an ABORT: that is the L10 rule - a green check
    # that cannot fail is worthless, so every gate here is probed by the fault it exists to catch.
    def P(fn):                      # mutate the render payload (the graph's c0.prompt) from the doc text
        return lambda g, man: g["c0"]["inputs"].update(prompt=fn(doc_block()["text"]))

    seeds = [
        ("sampler_restored", lambda g, man: g["ksel"]["inputs"].update(sampler_name="res_multistep"),
         "sampler"),
        ("length_restored", lambda g, man: g["c0"]["inputs"].update(length=243), "frames"),
        ("continuation_back",
         lambda g, man: g.update(win1=copy.deepcopy(gload(SRC)["win1"]),
                                 app1=copy.deepcopy(gload(SRC)["app1"])), "single"),
        ("prompt_is_the_source_prose",
         lambda g, man: g["c0"]["inputs"].update(prompt=gload(SRC)["c0"]["inputs"]["prompt"]), "beats"),
        ("prompt_short", P(lambda t: re.sub("At 00:01.400.*", "At 00:01.400, hands move.", t, flags=re.S)),
         "words"),
        ("beats_past_the_clip", P(lambda t: t.replace("At 00:04.200", "At 00:12.000")), "beats"),
        ("no_camera_move",
         P(lambda t: re.sub(r"The camera opens.*segment\.", "", t, flags=re.S)), "camera"),
        ("age_row_dropped",
         P(lambda t: re.sub(r"aged \d\d(?: of a fictional non-human species)? \(canon declaration\)",
                            "of a fictional species", t)), "ages"),
        ("negations_added", P(lambda t: t + " no light, no sound, no cloth."), "negation"),
        ("card_token_dropped", P(lambda t: re.sub(r"[Tt]iara", "crown", t)), "card"),
        ("graph_prompt_drifts_from_doc", P(lambda t: t + " "), "prompt_sync"),
        ("ref_slot_dropped", lambda g, man: g["c0"]["inputs"].pop("ref_images.ref_image_2"), "untouched"),
        ("ref_file_missing",
         lambda g, man: g[slot_edges(g)["c0"]["ref_images.ref_image_1"][0]]["inputs"].update(
             image="community/hc/NO_SUCH_CARD.jpg"), "refs_exist"),
        ("steps_raised", lambda g, man: g["s0_sched"]["inputs"].update(steps=12), "untouched"),
        ("shift_raised", lambda g, man: g["m_shift"]["inputs"].update(shift_video=12.0), "untouched"),
        ("attention_changed",
         lambda g, man: g["m_attn"]["inputs"].update(attention="pytorch attention"), "untouched"),
        ("canvas_changed", lambda g, man: g["c0"]["inputs"].update(width=1024), "untouched"),
        ("fps_changed", lambda g, man: g["mkvid"]["inputs"].update(fps=30), "frames"),
        ("seed_copied", lambda g, man: g["noise"]["inputs"].update(noise_seed=51150032), "untouched"),
        ("manifest_carries_a_judge_word",
         lambda g, man: man.update(keep="Derrick picks, so no row here may score the clip"), "no_judge"),
    ]

    def findings(g, ctx, mut=lambda g, man: None):
        man = measure(g)
        mut(g, man)
        ctx = dict(ctx, manifest=man, prompt=g["c0"]["inputs"]["prompt"])
        return {name: fn(g, ctx) for name, fn in CHECKS}, man

    ctx = {"block": doc_block()}
    g = build()

    if a.selftest:
        base, _ = findings(g, ctx)
        real = {k: v for k, v in base.items() if v}
        print(f"real artifact: {len(real)} checks fire {[list(v)[0][:70] for v in real.values()]}")
        bad = []
        for name, mut, want in seeds:
            gs = build()
            snap = (json.dumps(gs, sort_keys=True),
                    json.dumps(measure(gs), sort_keys=True, default=str))
            got, man = findings(gs, ctx, mut)
            if (json.dumps(gs, sort_keys=True), json.dumps(man, sort_keys=True, default=str)) == snap:
                # a seed whose pattern does not match the artifact changes nothing, so it can never fire:
                # that is a broken probe, not a passing one, and it must be loud (L10).
                bad.append(f"{name}: NO-OP, the seed changed neither the graph nor the manifest")
                print(f"  {'NO-OP':6s} {name:34s} expects {want:14s} mutated nothing")
                continue
            fired = sorted(k for k, v in got.items() if v)
            tag = "FIRED" if want in fired else "SILENT"
            if want not in fired:
                bad.append(f"{name}: {want} did not fire, fired={fired} first={list(got.get(want, ['n/a']))[:1]}")
            print(f"  {tag:6s} {name:34s} expects {want:14s} fired={fired}")
        if real:
            bad.append("the real artifact is not clean: " + json.dumps(real)[:300])
        for case in PAID_CASES:
            tmp = tempfile.mkdtemp(prefix="top5_paid_")
            try:
                for what in case["make"]:
                    f = {"obj": os.path.join(tmp, "runs", NEW, "objective.json"),
                         "log": os.path.join(tmp, "runs", NEW, "status.log"),
                         "out": os.path.join(tmp, "out", NEW),
                         "rj": os.path.join(tmp, "jobs", NEW + ".result.json")}[what]
                    os.makedirs(os.path.dirname(f), exist_ok=True)
                    if what == "out":
                        os.makedirs(f, exist_ok=True)
                    else:
                        open(f, "w").write("{}")
                got = paid_state(NEW, roots=tmp)[0]
                print(f"  {'PROBE' if got == case['want'] else 'SILENT':6s} "
                      f"paid_state.{case['name']:27s} -> {got} (want {case['want']})")
                if got != case["want"]:
                    bad.append(f"paid_state.{case['name']}: reads {got}, want {case['want']}")
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
        if bad:
            print("SELFTEST ABORT " + json.dumps(bad, indent=1)[:2000])
            return 1
        print(f"SELFTEST OK {len(seeds)} seeds fire their named check, 0 silent, 0 findings on the real graph, "
              f"{len(PAID_CASES)} paid-state probes all read as designed")
        return 0

    if a.emit:
        data = write_graph(g)
        print(f"EMIT {NEW} {len(data)} bytes sha256 {hashlib.sha256(data.encode()).hexdigest()}")
        print(f"  {os.path.join(GRAPHS, NEW + '.api.json')}")
        print(f"  {os.path.join(RUNS, NEW, 'request.api.json')}")
        return 0

    res, man = findings(g, ctx)
    n_ok = 0
    for name, _ in CHECKS:
        f = res[name]
        print(("PASS " if not f else "FAIL ") + name + ("" if not f else " :: " + " | ".join(f)))
        n_ok += 0 if not f else 1
    man["checks"] = [{"name": k, "ok": not v, "detail": v} for k, v in res.items()]
    with open(os.path.join(C, "notes", f"top5_manifest_{NEW}.json"), "w", encoding="utf-8",
              newline="\n") as fh:
        json.dump(man, fh, indent=1, sort_keys=True)
    print(f"MANIFEST notes/top5_manifest_{NEW}.json")
    print(f"clip {man['frames']} f at {man['fps']} fps = {man['seconds']} s, sampler {man['sampler']}, "
          f"{man['prompt_words_main']} words in the main field, beats {man['beats_s']}")
    if n_ok:
        print(f"VERDICT NOT CLEAN {n_ok} of {len(CHECKS)} checks fail")
        return 1
    print(f"VERDICT TOP5 CHECK CLEAN ({len(CHECKS)} checks, 0 findings)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
