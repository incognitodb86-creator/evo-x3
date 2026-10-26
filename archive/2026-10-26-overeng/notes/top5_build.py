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
  --arm a|b          a = the paid graph ...s51160001 (comfy kitchen attention, E5); b = the CK-ATTN A/B
                     graph ...s51160002 (pytorch attention). Same prompt, same seed, one key differs:
                     m_attn.attention. Gate 19 `attention` is the published rule, 20 `ab` is the
                     one-variable rule measured as an exact path diff (L16).
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
# CK-ATTN (2026-10-25, MAX block pick 3 "Sort out the Comfy Kitchen attention conflict"): the same
# builder renders arm b, an A/B that moves ONE key. Arm a is the paid graph and keeps its value; arm b
# carries the value the published docs name for an int8/convrot checkpoint (the schema default).
NEW2 = "ali163_top5_gi046_s51160002"
CK = "comfy kitchen attention"
PYTORCH = "pytorch attention"
ARMS = {"a": {"id": NEW, "attention": CK, "item": "E5 EULER-5S"},
        "b": {"id": NEW2, "attention": PYTORCH, "item": "CK-ATTN CK-ATTN-B"}}
MODEL_DIR = "C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/models/diffusion_models"
# the live options/default for the attention node, read on THIS box this date by
# notes/ali173_b2_objinfo.py --only ModelAttentionBackend --prefix ckattn_20261025_obj
LIVE_ATTN_SCHEMA = os.path.join(C, "notes", "ckattn_20261025_obj_ModelAttentionBackend.json")
# Every published line the attention gate is keyed on, with the saved body + line that carries it
# (PROMPT.md 5, L4: a claim cites a source read on this box). Quoted in findings and in the manifest.
PUB = {
    "ck_no_int8": 'notes/web/02v_docs_h3.txt:201 "Templates use int8_convrot checkpoints. Comfy Kitchen '
                  'does not support them (issue #15529). Use default attention, or switch UNETLoader to '
                  'pruned_bf16 then change backend." the same rule at :80 ("Comfy Kitchen attention '
                  'cannot run int8_convrot checkpoints; use a bf16 build with that backend"), and the '
                  'int8_convrot 21 GB row at :75',
    "ck_allows_the_other_families": 'notes/web/02v_docs_h3.txt:77-79 lists "Comfy Kitchen attention" as '
                  'the attention for the fp8_scaled / fp32 / bf16 rows, so the published bar is the int8 '
                  'family only',
    "ck_is_int8_kernels": 'notes/web/01_h3_ckpt_versions.txt:214 "ComfyUI-Kitchen (comfy-kernel int8 '
                  'attention)" and :216 "int8_convrot ... needs the int8 convrot mm kernel"',
    "author_names_the_family": 'notes/web/hc15_tenstrip_readme.txt:47-48: the int8 builds are the '
                  '"10Eros-Max-h3-int8-convrot" repo, so a file named *_int8* from that line is the '
                  'published int8_convrot family',
    "schema_defaults": 'live /object_info read on this box 2026-10-25 23:32 CT, ComfyUI system 0.38.0 '
                  '(notes/ckattn_20261025_obj_ModelAttentionBackend.json): options ["pytorch attention", '
                  '"comfy kitchen attention"], default "pytorch attention", tooltip "Comfy Kitchen '
                  'attention uses quantized INT8 attention"',
    "bf16_branch_out_of_reach": 'the live /object_info UNETLoader list (notes/ckattn_20261025_obj_'
                  'UNETLoader.json) offers 3 unet files and the only H3 one is the int8 file; pruned_bf16 '
                  'is 40 GB and bf16 66 GB (notes/web/02v_docs_h3.txt:76,79) on a 16 GB RTX 5070 Ti',
}
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
# Arm b moves one key more, the attention value. The `ab` gate is that exact set MEASURED as a path
# diff against the paid arm-a graph on disk, never prose (L16).
ARM_B_DIFF = ALLOWED_DIFF | {"m_attn.attention"}
# The arm-vs-arm diff, read off the two graphs: exactly the attention value and the arm's own output
# prefix (the prefix must differ or the two clips overwrite each other in ComfyUI/output).
ARMS_DIFF = {"m_attn.attention", "save.filename_prefix"}
# the card row no wording can satisfy, with the reason (measured by card_unsat below)
CARD_KNOWN = ("F-CARD-POSE2",)
NEG_WORDS = HC.TOP_NEG_WORDS
WANT_SECTIONS = A31.SECTIONS["c0"]
MAIN = "detailed_description"
WORD_BAND = (350, 500)
SUMMARY_MAX = 200


def doc_block(arm="a"):
    """the c0 block whose header id is this arm's graph: (id, seed, sections, body text). The doc may
    carry the two A/B blocks and nothing else; both carry byte-identical prose and the same seed, so the
    A/B changes one key. A31.parse_blocks is the shipped IM1 parser (L15), so the section order this
    item renders is the order that gate reads."""
    bs = A31.parse_blocks(open(DOC, encoding="utf-8").read())
    ids = sorted(b["id"] for b in bs)
    if not bs or set(ids) - {ARMS["a"]["id"], ARMS["b"]["id"]}:
        raise SystemExit(f"top5: {DOC} carries blocks {ids}, want only the arm ids "
                         f"{ARMS['a']['id']}/{ARMS['b']['id']}")
    for b in bs:
        if b["chunk"] != "c0" or int(b["seed"]) != SEED:
            raise SystemExit(f"top5: block {b['id']} is chunk={b['chunk']} seed={b['seed']}, "
                             f"want c0/{SEED}")
    if len(bs) == 2 and bs[0]["text"] != bs[1]["text"]:
        raise SystemExit("top5: the A/B blocks do not carry byte-identical prose, so the two clips would "
                         "differ by more than the attention value")
    b = next(b for b in bs if b["id"] == ARMS[arm]["id"])
    if b is None:
        raise SystemExit(f"top5: no prompt block for arm {arm} ({ARMS[arm]['id']}) in {DOC}")
    return b


def gload(nid):
    return json.load(open(os.path.join(GRAPHS, nid + ".api.json"), encoding="utf-8"))


def build(arm="a"):
    """the arm's 5-second single-pass euler graph, derived from SRC by subtraction (pure: returns a dict).
    The only arm-dependent lines are the attention value and the output prefix (check `ab`)."""
    aid = ARMS[arm]["id"]
    g = copy.deepcopy(gload(SRC))
    b = doc_block(arm)
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
    g["m_attn"]["inputs"]["attention"] = ARMS[arm]["attention"]
    g["noise"]["inputs"]["noise_seed"] = SEED
    g["save"]["inputs"]["filename_prefix"] = f"community/{aid}/{aid}"
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
    allowed = ARM_B_DIFF if ctx.get("arm") == "b" else ALLOWED_DIFF
    d = A31.diff_paths(src, g)
    bad = [f"DERIVE {p} is outside the allowed change set" for p in d if p not in allowed]
    bad += [f"DERIVE allowed change {p} did not happen" for p in sorted(allowed) if p not in d]
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
        if nid == "m_attn" and ctx.get("arm") == "b":
            continue        # the attention value IS the arm-b variable; gate 19 owns it, gate 20 bounds it
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
    aid = ARMS[ctx.get("arm", "a")]["id"]
    st, have, _ = paid_state(aid)
    if st == "half-paid":
        out.append(f"JOBS-static {aid} is half-paid: {len(have)} of 3 evidence files exist: {have}")
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


# ------------------------------------------------- CK-ATTN (2026-10-25): gates 19-20, the attention pair
INT8_NAME = re.compile(r"int8|convrot", re.I)


def unet_family(name):
    """the published quant family read off the file name. The docs name the builds by these tokens
    (pruned_int8_convrot / fp8_scaled / fp32 / bf16, notes/web/02v_docs_h3.txt:75-79), and the
    checkpoint's own author labels the int8 line "10Eros-Max-h3-int8-convrot" (:47-48 of the saved
    TenStrip README). Only the int8 family is what the published rule bars Comfy Kitchen from."""
    n = name.lower()
    if INT8_NAME.search(n):
        return "int8"
    for fam in ("fp8", "fp32", "bf16"):
        if fam in n:
            return fam
    return "unknown"


def attn_schema():
    """the live options + default for the attention node, read on this box (a dated file). No live
    file, no rule: the gate says so loudly instead of trusting the 2026-10-23 pinned dump (L4, L17)."""
    if not os.path.isfile(LIVE_ATTN_SCHEMA):
        return None
    spec = json.load(open(LIVE_ATTN_SCHEMA, encoding="utf-8"))["ModelAttentionBackend"]["input"]["required"]["attention"][1]
    return {"options": list(spec["options"]), "default": spec.get("default"), "file": LIVE_ATTN_SCHEMA}


def attention_state(g):
    name = g["unet"]["inputs"]["unet_name"]
    path = os.path.join(MODEL_DIR, name)
    exists = os.path.isfile(path)
    return {"unet_name": name, "unet_path": path, "unet_exists": exists,
            "unet_bytes": os.path.getsize(path) if exists else None,
            "quant_family": unet_family(name), "attention": g["m_attn"]["inputs"]["attention"],
            "schema": attn_schema(), "published": PUB,
            "vsa": {"selection": g["m_vsa"]["inputs"].get("selection"),
                    "keep_percent": g["m_vsa"]["inputs"].get("keep_percent"),
                    "start_percent": g["m_vsa"]["inputs"].get("start_percent"),
                    "recorded_for": "the dense backend is the fallback the sparse node names "
                                    "(live ModelAttentionBackend description, 2026-10-25 23:32 CT)"}}


def ck_attention(g, ctx):
    """the published attention rule, keyed off the checkpoint's quant family and the live schema.
    ComfyUI's H3 page (saved body): "Comfy Kitchen attention cannot run int8_convrot checkpoints; use a
    bf16 build with that backend" (notes/web/02v_docs_h3.txt:80) and "Use default attention, or switch
    UNETLoader to pruned_bf16 then change backend" (:201); the fp8/fp32/bf16 rows (:77-79) list CK as
    available, so the bar is the int8 family only. A graph that asks for CK on an int8/convrot file is
    the conflict this item settles; the paid arm-a graph reads red on it, by design."""
    st = attention_state(g)
    out = []
    if not st["unet_exists"]:
        out.append(f"ATTENTION-UNET-MISSING {st['unet_name']} is not in {MODEL_DIR}, so no queue can "
                   f"load it. " + PUB["bf16_branch_out_of_reach"])
    if st["schema"] is None:
        out.append(f"ATTENTION-SCHEMA-UNREAD no live options file at {LIVE_ATTN_SCHEMA}; read one with "
                   "notes/ali173_b2_objinfo.py --only ModelAttentionBackend --prefix <dated> (L4: a claim "
                   "cites a source read on this box, and a schema-stale pin is L17)")
        return out
    opts = st["schema"]["options"]
    if st["attention"] not in opts:
        out.append(f"ATTENTION-VALUE-OUTSIDE-SCHEMA {st['attention']} is not one of {opts}. "
                   + PUB["schema_defaults"])
    if st["quant_family"] == "int8" and st["attention"] == CK:
        out.append(f"ATTENTION-CK-INT8 {st['attention']} on {st['unet_name']} ({st['unet_bytes']} B, "
                   "family int8 = the published int8_convrot family the checkpoint's author names). "
                   + PUB["ck_no_int8"] + " | " + PUB["ck_is_int8_kernels"] + " | " +
                   PUB["author_names_the_family"] + " | the published value for this family is "
                   f"{st['schema']['default']} (the schema default); the other published branch (bf16) is "
                   "out of reach on this box. " + PUB["bf16_branch_out_of_reach"])
    return out


def ck_ab(g, ctx):
    """the A/B rule (L16: a cloned graph is only as safe as the diff you run on it). Arm b may differ
    from the paid arm-a graph on disk by exactly the attention value and its own output prefix - one
    variable, so any difference in the two clips belongs to the backend and to nothing else."""
    if ctx.get("arm") != "b":
        return []
    ref = os.path.join(GRAPHS, NEW + ".api.json")
    if not os.path.isfile(ref):
        return [f"AB the A/B reference graph {ref} is not on disk, so the one-variable rule cannot be measured"]
    d = A31.diff_paths(gload(NEW), g)
    out = []
    extra = sorted(p for p in d if p not in ARMS_DIFF)
    missing = sorted(p for p in ARMS_DIFF if p not in d)
    if extra:
        out.append(f"AB {extra} changed too: the A/B moves one variable only (m_attn.attention + its own "
                   "output prefix), else the pixels answer is not attributable")
    if missing:
        out.append(f"AB not an A/B: {missing} is identical in both arms")
    return out


CHECKS = [("state", ck_state), ("derive", ck_derive), ("frames", ck_frames), ("single", ck_single),
          ("sampler", ck_sampler), ("untouched", ck_untouched), ("refs_exist", ck_refs_exist),
          ("schema", ck_schema), ("jobs_static", ck_job_static), ("prompt_sync", ck_prompt_sync),
          ("words", ck_words), ("beats", ck_beats), ("camera", ck_camera), ("negation", ck_negation),
          ("ages", ck_ages), ("card", ck_card), ("card_unsat", ck_card_unsat), ("no_judge", ck_no_judge),
          ("attention", ck_attention), ("ab", ck_ab)]


# ---------------------------------------------------------------------------- the record
def measure(g, arm="a"):
    aid = ARMS[arm]["id"]
    b = doc_block(arm)
    n, fps = total_frames(g)
    card = HC.card_measure(SCENE, b["text"])
    allowed = ARM_B_DIFF if arm == "b" else ALLOWED_DIFF
    ref = os.path.join(GRAPHS, NEW + ".api.json")
    return {
        "as_of": "2026-10-25",
        "item": ARMS[arm]["item"],
        "arm": arm,
        "scene": SCENE,
        "graph": aid,
        "graph_path": os.path.join(GRAPHS, aid + ".api.json"),
        "source_graph": SRC,
        "source_sha256": HC.sha(os.path.join(GRAPHS, SRC + ".api.json")),
        "graph_sha256": hashlib.sha256(json.dumps(g, sort_keys=True).encode()).hexdigest(),
        "nodes": len(g),
        "dropped_nodes": sorted(DROP),
        "changed_paths": sorted(allowed),
        "attention": attention_state(g),
        "ab_reference_graph": NEW if arm == "b" else None,
        "ab_diff_measured": sorted(A31.diff_paths(gload(NEW), g)) if arm == "b" and os.path.isfile(ref) else None,
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
                           f"{os.path.join(RUNS, aid)} {aid} --frames {FRAMES}"),
    }


def write_graph(g, arm="a"):
    aid = ARMS[arm]["id"]
    data = json.dumps(g, indent=2)
    os.makedirs(os.path.join(RUNS, aid), exist_ok=True)
    with open(os.path.join(GRAPHS, aid + ".api.json"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(data)
    with open(os.path.join(RUNS, aid, "request.api.json"), "w", encoding="utf-8", newline="\n") as fh:
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


# The attention rule is a live-disk + live-schema rule, so it gets behaviour probes, not text grepping
# (L10): the PAID arm-a wiring must fire the named code, the built arm-b graph must be clean, and the
# families the published docs do NOT bar (fp8) must stay clean against a real file. A rule with no
# passing case is a ban, not a rule - that is what these probes check.
def attn_probe_cases():
    def mut(g, unet=None, attn=None):
        g = copy.deepcopy(g)
        if unet:
            g["unet"]["inputs"]["unet_name"] = unet
        if attn:
            g["m_attn"]["inputs"]["attention"] = attn
        return g
    paid = os.path.join(GRAPHS, NEW + ".api.json")
    return [
        ("paid_arm_a_asks_ck_on_an_int8_unet", gload(NEW) if os.path.isfile(paid) else None,
         ["ATTENTION-CK-INT8"]),
        ("built_arm_b_uses_the_published_default", build("b"), []),
        ("an_fp8_unet_may_use_ck_real_file_on_disk",
         mut(build("b"), unet="FLUX-KLEIN-9B-FP8-NSFW.safetensors", attn=CK), []),
        ("a_bf16_name_off_disk_names_the_missing_file",
         mut(build("b"), unet="minimax_h3_pruned_bf16.safetensors", attn=CK),
         ["ATTENTION-UNET-MISSING"]),
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", action="store_true")
    ap.add_argument("--emit", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--arm", choices=["a", "b"], default="a",
                    help="a = the paid ...s51160001 (comfy kitchen attention); b = the CK-ATTN A/B "
                         "...s51160002 (pytorch attention), one key from arm a")
    a = ap.parse_args()
    aid = ARMS[a.arm]["id"]
    if a.state:
        run_state()
        return 0

    # A seed mutates a copy of the real graph (or the manifest row) and names the check that MUST fire
    # on it. A seed whose named check stays silent is an ABORT: that is the L10 rule - a green check
    # that cannot fail is worthless, so every gate here is probed by the fault it exists to catch.
    def P(fn):                      # mutate the render payload (the graph's c0.prompt) from the doc text
        return lambda g, man: g["c0"]["inputs"].update(prompt=fn(doc_block(a.arm)["text"]))

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
        ("canvas_changed", lambda g, man: g["c0"]["inputs"].update(width=1024), "untouched"),
        ("fps_changed", lambda g, man: g["mkvid"]["inputs"].update(fps=30), "frames"),
        ("seed_copied", lambda g, man: g["noise"]["inputs"].update(noise_seed=51150032), "untouched"),
        ("manifest_carries_a_judge_word",
         lambda g, man: man.update(keep="Derrick picks, so no row here may score the clip"), "no_judge"),
    ]
    if a.arm == "a":
        # arm a: the attention value is not an arm-a variable, so moving it is an UNTOUCHED fault.
        seeds.append(("attention_value_moved_off_the_paid_wiring",
                      lambda g, man: g["m_attn"]["inputs"].update(attention=PYTORCH), "untouched"))
    else:
        # arm b: the attention value IS the variable, so the seeds name the attention gate, and one seed
        # restores the paid graph's wiring (the OLD value) - that is the L10 form: the detector fires on
        # the fault it exists to catch, and the A/B seed proves a second moved key is caught too.
        seeds += [
            ("paid_ck_value_restored_on_the_int8_unet",
             lambda g, man: g["m_attn"]["inputs"].update(attention=CK), "attention"),
            ("attention_value_outside_the_live_schema",
             lambda g, man: g["m_attn"]["inputs"].update(attention="sage attention"), "attention"),
            ("unet_file_not_on_disk",
             lambda g, man: g["unet"]["inputs"].update(unet_name="minimax_h3_pruned_bf16.safetensors"),
             "attention"),
            ("ab_moves_a_second_key",
             lambda g, man: g["s0_sched"]["inputs"].update(steps=12), "ab"),
        ]

    def findings(g, ctx, mut=lambda g, man: None):
        man = measure(g, a.arm)
        mut(g, man)
        ctx = dict(ctx, manifest=man, prompt=g["c0"]["inputs"]["prompt"])
        return {name: fn(g, ctx) for name, fn in CHECKS}, man

    ctx = {"block": doc_block(a.arm), "arm": a.arm}
    g = build(a.arm)

    if a.selftest:
        base, _ = findings(g, ctx)
        real = {k: v for k, v in base.items() if v}
        print(f"real artifact (arm {a.arm} {aid}): {len(real)} checks fire "
              f"{[list(v)[0][:70] for v in real.values()]}")
        bad = []
        # Arm a is the PAID graph, and the attention rule charges it the published conflict on purpose:
        # that one named finding is the measured state this item exists to settle, disclosed in the record.
        # So arm a's selftest requires that fire set to be exactly {attention: ATTENTION-CK-INT8} and 0
        # others; arm b (the artifact under construction) must be clean on every gate.
        paid_known = a.arm == "a"
        if paid_known:
            codes = [f.split()[0] for v in real.values() for f in v]
            if sorted(real) != ["attention"] or codes != ["ATTENTION-CK-INT8"]:
                bad.append(f"arm a: the paid graph's fire set is {sorted(real)} {codes}, want exactly "
                           "['attention'] ['ATTENTION-CK-INT8'] - the disclosed conflict, and nothing else")
            else:
                print("  KNOWN   arm a paid graph: the disclosed CK-on-int8 conflict fires, 0 other findings")
        elif real:
            bad.append("the real artifact is not clean: " + json.dumps(real)[:300])
        for name, mut, want in seeds:
            gs = build(a.arm)
            snap = (json.dumps(gs, sort_keys=True),
                    json.dumps(measure(gs, a.arm), sort_keys=True, default=str))
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
        for case in PAID_CASES:
            tmp = tempfile.mkdtemp(prefix="top5_paid_")
            try:
                for what in case["make"]:
                    f = {"obj": os.path.join(tmp, "runs", aid, "objective.json"),
                         "log": os.path.join(tmp, "runs", aid, "status.log"),
                         "out": os.path.join(tmp, "out", aid),
                         "rj": os.path.join(tmp, "jobs", aid + ".result.json")}[what]
                    os.makedirs(os.path.dirname(f), exist_ok=True)
                    if what == "out":
                        os.makedirs(f, exist_ok=True)
                    else:
                        open(f, "w").write("{}")
                got = paid_state(aid, roots=tmp)[0]
                print(f"  {'PROBE' if got == case['want'] else 'SILENT':6s} "
                      f"paid_state.{case['name']:27s} -> {got} (want {case['want']})")
                if got != case["want"]:
                    bad.append(f"paid_state.{case['name']}: reads {got}, want {case['want']}")
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
        for name, gprobe, want in attn_probe_cases():
            if gprobe is None:
                bad.append(f"attention.{name}: the paid graph {NEW}.api.json is not on disk to probe")
                continue
            codes = sorted(f.split()[0] for f in ck_attention(gprobe, ctx))
            ok = codes == sorted(want)
            print(f"  {'PROBE' if ok else 'SILENT':6s} attention.{name:44s} -> {codes} (want {sorted(want)})")
            if not ok:
                bad.append(f"attention.{name}: codes {codes}, want {sorted(want)}")
        if bad:
            print("SELFTEST ABORT " + json.dumps(bad, indent=1)[:2000])
            return 1
        print(f"SELFTEST OK arm {a.arm} {aid}: {len(seeds)} seeds fire their named check, 0 silent, "
              f"{('the paid graph fires only the disclosed attention conflict' if paid_known else '0 findings on the real graph')}, "
              f"{len(PAID_CASES)} paid-state probes and {len(attn_probe_cases())} attention behaviour "
              "probes all read as designed")
        return 0

    if a.emit:
        data = write_graph(g, a.arm)
        print(f"EMIT arm {a.arm} {aid} {len(data)} bytes sha256 {hashlib.sha256(data.encode()).hexdigest()}")
        print(f"  {os.path.join(GRAPHS, aid + '.api.json')}")
        print(f"  {os.path.join(RUNS, aid, 'request.api.json')}")
        return 0

    res, man = findings(g, ctx)
    n_ok = 0
    for name, _ in CHECKS:
        f = res[name]
        print(("PASS " if not f else "FAIL ") + name + ("" if not f else " :: " + " | ".join(f)))
        n_ok += 0 if not f else 1
    man["checks"] = [{"name": k, "ok": not v, "detail": v} for k, v in res.items()]
    with open(os.path.join(C, "notes", f"top5_manifest_{aid}.json"), "w", encoding="utf-8",
              newline="\n") as fh:
        json.dump(man, fh, indent=1, sort_keys=True)
    print(f"MANIFEST notes/top5_manifest_{aid}.json")
    print(f"clip {man['frames']} f at {man['fps']} fps = {man['seconds']} s, sampler {man['sampler']}, "
          f"{man['prompt_words_main']} words in the main field, beats {man['beats_s']}")
    print(f"attention {man['attention']['attention']} on unet {man['attention']['unet_name']} "
          f"family {man['attention']['quant_family']} exists={man['attention']['unet_exists']} "
          f"schema_default={man['attention']['schema'] and man['attention']['schema']['default']}")
    if man["ab_diff_measured"] is not None:
        print(f"ab diff vs the paid arm-a graph: {man['ab_diff_measured']}")
    if n_ok:
        print(f"VERDICT NOT CLEAN {n_ok} of {len(CHECKS)} checks fail")
        return 1
    print(f"VERDICT TOP5 CHECK CLEAN ({len(CHECKS)} checks, 0 findings, arm {a.arm} {aid})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
