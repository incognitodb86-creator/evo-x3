#!/usr/bin/env python3
"""ORC-ROBOT (fix_plan.md L27) - the robot (GI063) 5-second clip: prompt + graph + gates, offline.

Derrick's row: "write the H3 prompt for ... the robot start image from what is in the picture - species,
body, build, the partner as the picture shows them - community prompt structure and published defaults,
render 15 s 16:9 with audio, send the mp4 + a contact sheet." This pass does the robot half offline: the
prose (`notes/orc_robot_prompts.md`, one 124-frame single-pass euler block) and the graph
(`p7/graphs/ali163_top5_gi063_s51160011.api.json`), derived from the scene's staged, unpaid, card-faithful
15 s graph `ali163_hc15_gi063_s51150031` by subtraction. Nothing is queued: the same card's consent row
(`C:/AI/community/notes/needs_derrick.md` row 21) is an open question to Derrick, and `fix_plan.md` carries
"GI063: on hold until Derrick rules on needs_derrick.md row 21 ... Do not render GI063 s51150031/s51150032
before his answer". The 5-second shape is the paid E5/CK-ATTN pair (needs_derrick rows 30, 31), so this
graph is that shape with the robot's prompt: no new shape, no new dial, one scene (L16, IM1).

The gates:
  state         the source is the measured 243-frame / 362-frame res_multistep shape this item reverses
  derive        the diff is the allowed change set: the 7 dropped nodes + 2 rewires + length, prompt,
                sampler, seed, prefix, attention. Nothing else.
  frames/single/sampler  (top5_build, the paid E5 instrument) one pass, 124 f, 5.167 s at 24 fps, euler
  untouched     steps, shift, VSA, canvas, the vae chain, unet, clip, mkvid, the reference slots stay
                byte-identical to the source; a new config renders on a new seed
  refs          the slots are LoadImage nodes on the approved card files, and the set is exactly that pair
  schema        the offline H3 class+key scan (ali163_hc_r4g2_build), the class that made the rc-2
  jobs_static   the graph totals the --frames value the render passes, the id is unpaid, the files load
  graph_file    the graph on disk is the builder's output byte-for-byte (the derivation is the artifact)
  sync/words/beats/camera/negation/ages  the IM1 prompt shape (ali31_prompt_set_check) on this block
  card          the start-image card gate (hc15_anchor_carry_build) with a MEASURED unsatisfiable row,
                stated in code: this card's `banned` lists are substring-matched, and its own required rows
                contain the banned substrings - "the" contains "he" (banned for any figure), "metal" (in
                the required token "polished silver metal plating") contains "tall" (figure 1),
                "detailed" (the card's own "sensor-like details" row) contains "tail" (figure 2),
                "furniture" contains "fur", "cool blue glow" contains "glow", "the woman's skin ...
                surfaces" contains "skin" and "face". So F-CARD-BANNED cannot be driven to 0. The gate
                REQUIRES that set and nothing else, and gate `card_noise` requires every fired token to be
                a substring of a row the card itself mandates (per_chunk_tokens / room_required /
                light_required / consent require / evidence). Any other token is a real breach, and stops
                the queue.
  card_probe    the same gate on a degraded prompt built to breach named rows of THIS card: the positive
                control that proves the card gate reads this scene's card and can stop this queue
  ab_shape      the graph equals the paid 5 s shape on disk (the CK-ATTN pytorch graph) except for the
                prompt, the seed, the output prefix and the scene's two reference files - the one-variable
                rule (IM1) as a path diff (L16)
  attention     the value is the published one: the live schema default, the value docs/02v_docs_h3.md
                names, clean for the int8/convrot family this box loads
  hold          while fix_plan.md carries an OPEN row putting this scene on render hold pending
                needs_derrick row 21, the render id must be unpaid: a queue before his ruling is the fault
                this gate stops
  no_judge      the manifest carries no verdict word

Selftest: every gate gets a seeded fault in a COPY of the built graph, prompt, manifest, doc block, source
graph, or the on-disk graph (each named); the paid-state classifier (the proof `jobs_static` reads before a
queue) and the hold gate are built in temp roots and against the plan rule in memory; the attention-value
gate is probed on both paid states and three values; the NO-OP check restores the originals in the clone and
requires 0.
"""
import sys, os, re, json, copy, hashlib, argparse, tempfile, shutil
C = "C:/AI/community"
PLAN = "C:/Users/derek/5slock/ralph-community/fix_plan.md"
sys.path.insert(0, os.path.join(C, "notes"))
import hc15_anchor_carry_build as HC          # the card gate
import ali31_prompt_set_check as A31          # the IM1 prompt shape
import ali163_hc_r4g2_build as R4             # the offline H3 schema (the rc-2 class)
import top5_build as T5                       # the paid E5 instrument: the scene-agnostic gates, reused

GRAPHS = T5.GRAPHS
RUNS = T5.RUNS
DOC = os.path.join(C, "notes", "orc_robot_prompts.md")
NEEDS = os.path.join(C, "notes", "needs_derrick.md")
INPUT = "C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/input"   # same root top5_build.ref_files resolves
SCENE = "GI063"
SRC = "ali163_hc15_gi063_s51150031"        # the staged, unpaid, card-faithful 15 s graph of this scene
ID = "ali163_top5_gi063_s51160011"
SEED = 51160011
ATTN = "pytorch attention"                  # published: the live schema default (docs/02v_docs_h3.md:196)
OTHER_ATTN = "comfy kitchen attention"      # the value the paid E5 arm a runs, and no published source names
FRAMES, FPS = T5.FRAMES, T5.FPS             # 124 f = 5.167 s at 24 fps, the paid E5 shape
DROP, CONT_CLASSES = T5.DROP, T5.CONT_CLASSES
# c1 is DROPPED in this shape, so the E5 allowed set loses "c1.prompt"; attention is a value here (the
# published value), so it is in the allowed set and gate `attention` owns its value, as CK-ATTN arm b did.
ALLOWED_DIFF = (set(T5.ALLOWED_DIFF) - {"c1.prompt"}) | {"m_attn.attention"}
CARD_CODE_KNOWN = ("F-CARD-BANNED",)        # measured: the card's own substring-collision rows, stated
PAID_SHAPE = "ali163_top5_gi046_s51160002"  # the paid pytorch-attention 5 s graph: the shape to match
SHAPE_DIFF = {"c0.prompt", "noise.noise_seed", "save.filename_prefix", "img.image", "img2.image"}
PUBLISHED_SOURCE = ("file docs/02v_docs_h3.md line 196 says default attention; the live schema default is "
                    "pytorch attention; the unet file is the int8_convrot family, the family whose attention "
                    "the docs fix")
WANT_SECTIONS = A31.SECTIONS["c0"]
NEG_WORDS = HC.TOP_NEG_WORDS
AGE_RE = re.compile(r"aged (\d{2})")
CANON_RE = re.compile(r"aged (\d{2})(?: [^\n]{0,80}?)?(canon declaration)")
AGE_MIN = 21
SUBJ = re.compile(r"<Subject\s*(\d+)>")


def gload(nid):
    return json.load(open(os.path.join(GRAPHS, nid + ".api.json"), encoding="utf-8"))


def src_graph(ctx):
    return ctx.get("src") if ctx.get("src") is not None else gload(SRC)


def block():
    """the one c0 block of the doc: (id, seed, sections, text). Any other id, a non-c0 chunk, a second
    block, a missing section, a short body: the builder stops. A31.parse_blocks is the shipped parser."""
    bs = A31.parse_blocks(open(DOC, encoding="utf-8").read())
    if len(bs) != 1:
        raise SystemExit("orc_robot: %s carries %d blocks, want exactly the one robot block %s"
                         % (DOC, len(bs), ID))
    b = bs[0]
    if b["id"] != ID or b["chunk"] != "c0" or int(b["seed"]) != SEED:
        raise SystemExit("orc_robot: block %s chunk=%s seed=%s, want %s/c0/%d" % (b["id"], b["chunk"],
                                                                                  b["seed"], ID, SEED))
    if list(b["sections"].keys()) != WANT_SECTIONS:
        raise SystemExit("orc_robot: %s sections %s, want %s" % (ID, list(b["sections"].keys()),
                                                                 WANT_SECTIONS))
    if len(b["text"]) < 300:
        raise SystemExit("orc_robot: the block body is short (%d bytes), a fixture not a prompt"
                         % len(b["text"]))
    return b


def build():
    """the robot's 5-second single-pass euler graph, derived from SRC by subtraction (pure: a dict)."""
    g = copy.deepcopy(gload(SRC))
    b = block()
    for n in DROP:
        g.pop(n, None)
    g["dec_v"]["inputs"]["samples"] = ["s0_samp", 0]
    g["dec_a"]["inputs"]["samples"] = ["s0_samp", 0]
    g["c0"]["inputs"]["length"] = FRAMES
    g["c0"]["inputs"]["prompt"] = b["text"]
    g["ksel"]["inputs"]["sampler_name"] = "euler"
    g["m_attn"]["inputs"]["attention"] = ATTN
    g["noise"]["inputs"]["noise_seed"] = SEED
    g["save"]["inputs"]["filename_prefix"] = "community/%s/%s" % (ID, ID)
    return g


def sections_of(text):
    return T5.sections_of(text)


def neg_spans(text):
    """negation-word occurrences in the card-normalized text: [(start, end, word)] (L15's word list, the
    same set top5_build counts)."""
    n = HC.card_norm(text)
    pat = r"(?<![a-z])(%s)(?![a-z])" % "|".join(re.escape(w) for w in NEG_WORDS)
    return [(m.start(), m.end(), m.group(1)) for m in re.finditer(pat, n)]


def neg_forced(text):
    """the negation spans the card forces: inside an occurrence of a row the card itself mandates."""
    n = HC.card_norm(text)
    spans = [(m.start(), m.end()) for r in card_rows(SCENE) for m in re.finditer(re.escape(r), n)]
    return [(w, s, e) for s, e, w in neg_spans(n) if any(s >= a and e <= b for a, b in spans)], [
        (w, s, e) for s, e, w in neg_spans(n) if not any(s >= a and e <= b for a, b in spans)]


def card_rows(nid):
    """the rows the card mandates for itself: the wording a compliant prompt MUST carry. A banned token
    that is a substring of one of these is the card's defect (banned list vs its own required wording)."""
    gt = HC.card_facts(nid)["gate"]
    rows = (list(gt["per_chunk_tokens"]) + list(gt["room_required"]) + list(gt["light_required"])
            + list(gt["consent_gate"]["require"]) + list(gt["evidence"].values()))
    return [HC.card_norm(r) for r in rows]


def degraded_prompt(p):
    """the card gate's positive control: a prompt built to breach named rows of THIS card - the opening
    beat loses the card poses, an eagerness claim appears, the two consent rows go, a card-banned word is
    charged to figure 1, an age loses its canon marker, and a room the card never names appears."""
    out = p.replace("At 00:00.000, the frame is the opening photograph: <Subject 1> prone on a black padded "
                    "bench, chained at wrists to the bench edge",
                    "At 00:00.000, the frame is a bedroom, the woman stands up smiling, aged 27")
    out = out.replace("The card record shows restraint and gives no consent evidence, and "
                      "notes/needs_derrick.md row 21 carries that question to Derrick.",
                      "She is consenting and eager.")
    out = out.replace("heavy silver chains", "chains")   # a per-chunk token the card requires
    return out


# ------------------------------------------------------------------ checks: each returns [] when it passes
def ck_state(g, ctx):
    src = src_graph(ctx)
    n, fps = T5.total_frames(src)
    out = []
    if [v["inputs"].get("sampler_name") for v in src.values()
        if v["class_type"] == "KSamplerSelect"] != ["res_multistep"]:
        out.append("STATE the source sampler is not res_multistep - the shape this item reverses moved")
    if src["c0"]["inputs"]["length"] != 243 or (n, fps) != (362, FPS):
        out.append("STATE the source shape is c0 %d / %d f at %s, not the measured 243 / 362 f at 24"
                   % (src["c0"]["inputs"]["length"], n, fps))
    return out


def ck_derive(g, ctx):
    src = src_graph(ctx)
    d = A31.diff_paths(src, g)
    bad = ["DERIVE %s is outside the allowed change set" % p for p in d if p not in ALLOWED_DIFF]
    bad += ["DERIVE allowed change %s did not happen" % p for p in sorted(ALLOWED_DIFF) if p not in d]
    if set(g) - set(src):
        bad.append("DERIVE added nodes %s" % sorted(set(g) - set(src)))
    if set(src) - set(g) != DROP:
        bad.append("DERIVE dropped %s, want %s" % (sorted(set(src) - set(g)), sorted(DROP)))
    for nid, nd in g.items():
        for k, v in nd["inputs"].items():
            if isinstance(v, list) and v[0] not in g:
                bad.append("DERIVE %s.%s links to the dropped node %s" % (nid, k, v[0]))
    return bad


def ck_untouched(g, ctx):
    """the axes this item does not name stay byte-identical to the source. The attention value IS named
    (it is the published value), and gate `attention` owns it."""
    src = src_graph(ctx)
    out = []
    for nid in ("s0_sched", "s0_guide", "m_shift", "m_vsa", "unet", "clip", "vvae", "avae", "g0", "mkvid",
                "img", "img2"):
        if nid not in src or nid not in g:
            out.append("UNTOUCHED %s is in one graph and not the other" % nid)
            continue
        if g[nid]["inputs"] != src[nid]["inputs"]:
            out.append("UNTOUCHED %s inputs changed" % nid)
    for nid in ("dec_v", "dec_a"):
        if [x for k, x in g[nid]["inputs"].items() if k.endswith("samples")] != [["s0_samp", 0]]:
            out.append("UNTOUCHED %s keeps a link into the dropped continuation half" % nid)
        if {k: v for k, v in g[nid]["inputs"].items() if not k.endswith("samples")} != \
           {k: v for k, v in src[nid]["inputs"].items() if not k.endswith("samples")}:
            out.append("UNTOUCHED %s changed a key beside its samples link" % nid)
    for k in ("width", "height", "ref_image_size"):
        if g["c0"]["inputs"].get(k) != src["c0"]["inputs"].get(k):
            out.append("UNTOUCHED c0.%s changed" % k)
    if T5.slot_edges(g).get("c0", {}) != T5.slot_edges(src).get("c0", {}):
        out.append("UNTOUCHED the c0 reference slots changed")
    mine = {t[0]: t[1] for t in T5.ref_files(g) if t[0].startswith("c0.")}
    theirs = {t[0]: t[1] for t in T5.ref_files(src) if t[0].startswith("c0.")}
    if {k: v for k, v in mine.items() if k in theirs} != theirs:
        out.append("UNTOUCHED a reference file target changed %s"
                   % json.dumps({k: [theirs[k], mine.get(k)] for k in theirs if mine.get(k) != theirs[k]}))
    if g["noise"]["inputs"]["noise_seed"] == src["noise"]["inputs"]["noise_seed"]:
        out.append("UNTOUCHED noise_seed is the source seed - a new config renders on a new seed")
    return out


def ck_refs(g, ctx):
    out = []
    for slot, rel, abspath, is_load in T5.ref_files(g):
        if not is_load:
            out.append("REFS %s is not a LoadImage node" % slot)
        elif not os.path.isfile(abspath):
            out.append("REFS %s resolves to a missing file %s" % (slot, abspath))
    want = {"%s.jpg" % SCENE, "%s_w1_face.png" % SCENE}
    got = {os.path.basename(t[1]) for t in T5.ref_files(g)}
    if got != want:
        out.append("REFS the slots carry %s, want the approved %s (this scene has two reference files; a "
                   "third slot has no file to fill it)" % (sorted(got), sorted(want)))
    return out


def ck_schema(g, ctx):
    return ["SCHEMA %s" % v for v in R4.scan(g, R4.h3_schema())]


def ck_negation(g, ctx):
    """L15: no negation wording in the prose. This card's own required rows carry negation - the consent
    row 'the card record shows restraint and gives no consent evidence', the room row's 'not', an evidence
    row's 'none' - so a negation inside a card-mandated row is the card's defect (reported, and the same
    class as the banned-substring rows), and any negation OUTSIDE those rows is the fault this gate stops."""
    forced, free = neg_forced(ctx["prompt"])
    return ["NEGATION %r at %d is negation wording outside any card-mandated row (L15)" % (w, s)
            for w, s, _e in free]


def ck_jobs(g, ctx):
    """the offline clone of run_graph_job's frame gate + the pre-submit condition (T5.ck_job_static with
    its ARMS pointing at this id) + the card rule L18: the files this render reads are on disk."""
    T5.ARMS = {"a": {"id": ID, "attention": ATTN}}
    out = T5.ck_job_static(g, {"arm": "a"})
    for _slot, rel, abspath, _is_load in T5.ref_files(g):
        if not os.path.isfile(abspath):
            out.append("JOBS-static a reference file this render reads is absent: %s" % rel)
    return out


def ck_graph_file(g, ctx):
    if "on_disk" not in ctx:
        return ["GRAPH-FILE the on-disk graph was not read"]
    return [] if ctx["on_disk"] == g else [
        "GRAPH-FILE the graph on disk is not the builder's output byte-for-byte: the derivation is the "
        "artifact, so the shape is unverified (edit the builder, run --emit)"]


def ck_sync(g, ctx):
    b = ctx["block"]
    out = []
    if g["c0"]["inputs"]["prompt"] != b["text"]:
        out.append("SYNC the graph c0.prompt is not the doc block, byte for byte")
    if list(b["sections"].keys()) != WANT_SECTIONS:
        out.append("SYNC the doc sections %s != the c0 shape %s" % (list(b["sections"].keys()),
                                                                   WANT_SECTIONS))
    if str(g["noise"]["inputs"]["noise_seed"]) != str(b["seed"]):
        out.append("SYNC the graph seed != the block header seed")
    if b["text"].lstrip().startswith("At "):
        out.append("SYNC the block body starts on a beat, not a section header")
    return out


def ck_words(g, ctx):
    return T5.ck_words(g, ctx)


def ck_ages(g, ctx):
    """the SUBJECT DEFINITION lines (the ones that open with the tag): each carries an age >= 21 with the
    card's canon marker (AGENTS.md content lock; A31.AGE_RE + AGE_MIN_RE are the shipped IM1 rules). A line
    that only mentions a subject inside a <Picture> description is not a definition line."""
    out = []
    for line in sections_of(ctx["prompt"])["subject_definitions"].splitlines():
        m = re.match(r"\s*<Subject\s*(\d+)>", line)
        if not m:
            continue
        am = AGE_RE.search(line)
        if not am:
            out.append("AGES <Subject %s> has no age" % m.group(1))
            continue
        if int(am.group(1)) < AGE_MIN:
            out.append("AGES <Subject %s> is aged %d, under %d (canon: every character is an adult 21+)"
                       % (m.group(1), int(am.group(1)), AGE_MIN))
        if not CANON_RE.search(line):
            out.append("AGES <Subject %s> has no 'canon declaration' with the age" % m.group(1))
    return out


def ck_card(g, ctx):
    """the card gate on the emitted prompt. This card's banned-substring rows are the measured, stated
    card defect (see CARD_CODE_KNOWN): the gate passes on exactly that set, its rows go in the manifest, and
    any OTHER card row - a missing pose, room, light, age, consent, subject row - stops the queue."""
    fires = sorted({c for c, _ in HC.card_fires(SCENE, ctx["card"])})
    if tuple(fires) != CARD_CODE_KNOWN:
        return (["CARD the firing set is %s, want exactly %s (the measured substring-collision rows): %s"
                 % (fires, list(CARD_CODE_KNOWN),
                    "; ".join("%s: %s" % (c, d) for c, d in HC.card_fires(SCENE, ctx["card"])))]
                if len(fires) > len(CARD_CODE_KNOWN) else
                ["CARD the firing set is %s, want exactly %s: a card row this prompt must carry is missing "
                 "(see the measurement in the manifest)" % (fires, list(CARD_CODE_KNOWN))])
    return []


def ck_card_noise(g, ctx):
    """every banned token this prompt fires must be a substring of a row the card itself mandates: that is
    the card's own defect, and the report its owner needs. Any other token is a real card breach."""
    mand = card_rows(SCENE)
    bad = sorted({t for toks in ctx["card"]["banned_hits"].values() for t in toks
                  if not any(t in r for r in mand)})
    return ["CARD-NOISE %r is charged to a figure and sits in no card-mandated row - a real card breach" % t
            for t in bad]


def ck_card_probe(g, ctx):
    """the card gate is alive on this scene: a degraded prompt built to breach named rows must fire them,
    and the emitted prompt must be clean of the rows that are satisfiable."""
    want = ("F-CARD-WORDS", "F-CARD-POSE", "F-CARD-POSE2", "F-CARD-ROOM2", "F-CARD-AGE",
            "F-CARD-CONSENT", "F-CARD-CONSENT2")
    got = {c for c, _ in HC.card_fires(SCENE, HC.card_measure(SCENE, degraded_prompt(ctx["prompt"])))}
    out = ["CARD-PROBE %s did not fire on the seeded prompt: the gate cannot stop this queue" % m
           for m in want if m not in got]
    clean = {c for c, _ in HC.card_fires(SCENE, ctx["card"])}
    if "F-CARD-CONSENT" in clean or "F-CARD-CONSENT2" in clean:
        out.append("CARD-PROBE the emitted prompt fails a consent row of this card")
    return out


def ck_ab_shape(g, ctx):
    """the one-variable rule, measured: this graph is the PAID 5 s shape (the CK-ATTN arm-b graph on disk)
    with the robot's prompt, a new seed, its own prefix and its own two reference files - nothing "
    "else (L16, IM1)."""
    paid = gload(PAID_SHAPE)
    d = A31.diff_paths(paid, g)
    out = []
    if sorted(g) != sorted(paid):
        out.append("AB-SHAPE the node set differs from the paid 5 s shape")
    if extra := sorted(p for p in d if p not in SHAPE_DIFF):
        out.append("AB-SHAPE vs the paid 5 s shape moves %s, outside prompt+seed+prefix+reference files" % extra)
    if missing := sorted(p for p in SHAPE_DIFF if p not in d):
        out.append("AB-SHAPE vs the paid 5 s shape keeps %s - the robot prompt, seed and prefix must all "
                   "be this clip's own" % missing)
    return out


def ck_attention(g, ctx):
    return T5.ck_attention(g, {"paid": ctx["paid"]})


def plan_hold_row():
    """the plan's standing render-hold rule for this scene (fix_plan.md line 6, Derrick's directive, not a
    checkbox row): 'GI063: on hold until Derrick rules on needs_derrick.md row 21 ...'. The plan file is the
    authority: it is the file that changes when he rules, so the gate reads the rule there."""
    try:
        plan = open(PLAN, encoding="utf-8", errors="replace").read().replace("\r\n", "\n")
    except OSError:
        return None, None
    row = [ln for ln in plan.split("\n")
           if re.match(r"^\s*[-*]?\s*%s\b" % SCENE, ln) and "on hold" in ln.lower()
           and "row 21" in ln]
    return (row[0] if row else None), plan


def ck_hold(g, ctx):
    """the row-21 hold, measured off the plan and off the render evidence: while the plan carries the
    render-hold rule for this scene, this id must be unpaid - a clip of this scene rendered before his
    ruling is the fault this gate stops. When the rule leaves the plan (his ruling lands), the builder's own
    basis has moved: the gate fires and says so, because the item must be re-read before any queue."""
    row, _plan = ctx["plan_row"] if "plan_row" in ctx else plan_hold_row()
    if row is None:
        return ["HOLD the plan carries no %s render-hold rule: the rule moved (a ruling landed?) - re-read "
                "needs_derrick row 21 and this item before any queue, and update this builder" % SCENE]
    if ctx["hold_paid"]:
        return ["HOLD %s is paid while the plan keeps %s on render hold pending needs_derrick row 21 - a "
                "render ran before the ruling" % (ID, SCENE)]
    return []


def ck_no_judge(g, ctx):
    hits = sorted({w.lower() for w in A31.KEEPWORDS.findall(ctx["note"])})
    return ["NO-JUDGE the manifest note carries %s: this item keeps no verdict" % ", ".join(hits)] if hits else []


def measure(g, ctx):
    txt = g["c0"]["inputs"]["prompt"]
    sec = sections_of(txt)
    cm = HC.card_measure(SCENE, txt)
    mand = card_rows(SCENE)
    n, fps = T5.total_frames(g)
    sha = lambda rel: hashlib.sha256(open(os.path.join(INPUT, rel.replace("/", os.sep)), "rb").read()).hexdigest()[:16]
    return {
        "id": ID, "scene": SCENE, "seed": g["noise"]["inputs"]["noise_seed"], "source": SRC,
        "derived_from": "the source minus %s + 2 rewires + length, prompt, sampler, seed, prefix, attention"
                        % sorted(DROP),
        "frames": n, "fps": fps, "seconds": round(n / fps, 6), "c0_length": g["c0"]["inputs"]["length"],
        "sampler": [v["inputs"]["sampler_name"] for v in g.values() if v["class_type"] == "KSamplerSelect"],
        "steps": [v["inputs"]["steps"] for v in g.values() if v["class_type"] == "BasicScheduler"],
        "shift": {k: v for k, v in g["m_shift"]["inputs"].items() if k.startswith("shift_")},
        "canvas": (g["c0"]["inputs"]["width"], g["c0"]["inputs"]["height"]),
        "guide_node": g["s0_guide"]["inputs"],
        "unet": g["unet"]["inputs"]["unet_name"], "unet_family": T5.unet_family(g["unet"]["inputs"]["unet_name"]),
        "attention_value": g["m_attn"]["inputs"]["attention"], "paid_state": ctx["paid"],
        "vsa": g["m_vsa"]["inputs"], "published_rule": PUBLISHED_SOURCE,
        "attention_schema": T5.attn_schema(), "attention_state": T5.attention_state(g),
        "ref_files": [t[1] for t in T5.ref_files(g)],
        "ref_sha256_16": [sha(t[1]) for t in T5.ref_files(g)],
        "ref_files_agree_with_the_source_graph": sorted(set(t[1] for t in T5.ref_files(src_graph(ctx)))),
        "sections": list(ctx["block"]["sections"].keys()),
        "words": {k: len(v.split()) for k, v in sec.items()},
        "beats": A31.beat_times(txt), "window_s": [0.0, round(n / fps, 6)],
        "camera_terms": sorted({t for t in A31.CAM_TERMS if t in sec["detailed_description"]}),
        "negation": {"total": len(neg_spans(txt)),
                     "card_forced": sorted({w for w, _s, _e in neg_forced(txt)[0]}),
                     "outside_card_rows": sorted({w for w, _s, _e in neg_forced(txt)[1]}),
                     "forced_rows": [r for r in card_rows(SCENE)
                                    if any(w in r.split() for w in NEG_WORDS)]},
        "negation_words": sorted({w for _s, _e, w in neg_spans(txt)}),
        "ages": [{"subject": m.group(1), "age": int(m.group(2)), "canon_declaration": True}
                 for line in sec["subject_definitions"].splitlines()
                 for m in [re.search(r"<Subject\s*(\d+)>.*?aged (\d{2})", line)] if m],
        "card_measurement": cm,
        "card_fires": sorted({c for c, _ in HC.card_fires(SCENE, cm)}),
        "card_known_unsatisfiable": list(CARD_CODE_KNOWN),
        "card_banned_tokens": {k: sorted(set(v)) for k, v in cm["banned_hits"].items()},
        "card_banned_tokens_all_in_card_rows": {t: any(t in r for r in mand) for t in sorted(
            {t for toks in cm["banned_hits"].values() for t in toks})},
        "card_probe_fires": sorted({c for c, _ in HC.card_fires(SCENE,
                                      HC.card_measure(SCENE, degraded_prompt(txt)))}),
        "prompt_sha256_16": hashlib.sha256(txt.encode()).hexdigest()[:16],
        "graph_path": os.path.join(GRAPHS, ID + ".api.json"),
        "render_path": "C:/AI/director/.venv/Scripts/python.exe C:/AI/community/scripts/run_graph_job.py "
                       "<run_dir> %s --frames %d, gpu_guard IDLE + gpu_lock first (L19)" % (ID, FRAMES),
        "render_queued": False,
        "hold_row": "needs_derrick.md row 21 (the consent question about this same card) is open, the plan "
                    "keeps %s on render hold, and the scene's 15 s ids s51150031/s51150032 are armed and "
                    "unpaid" % SCENE,
        "diff_vs_source": len(A31.diff_paths(src_graph(ctx), g)),
        "diff_vs_paid_5s_shape": len(A31.diff_paths(gload(PAID_SHAPE), g)),
        "gates": [d["id"] for d in GATES],
    }


GATES = [
    {"id": "state", "fn": ck_state, "fault": "the source graph in hand is not the 243 / 362 f "
                                             "res_multistep shape"},
    {"id": "derive", "fn": ck_derive, "fault": "a node outside the drop list is removed, an out-of-set "
                                               "value is moved, a kept node links into the dropped half"},
    {"id": "frames", "fn": T5.ck_frames, "fault": "c0.length is set to 243 (the 15.083 s shape)"},
    {"id": "single", "fn": T5.ck_single, "fault": "the source continuation nodes are restored (two samplers)"},
    {"id": "sampler", "fn": T5.ck_sampler, "fault": "ksel.sampler_name back to res_multistep"},
    {"id": "untouched", "fn": ck_untouched, "fault": "s0_sched.steps 8 to 12, m_shift.shift_to 5.0, c0.width "
                                                     "1344 to 1024, the noise seed back to the source seed, "
                                                     "an unet file, a reference slot edge, a reference target, "
                                                     "a dec_v link left in the dropped half"},
    {"id": "refs", "fn": ck_refs, "fault": "a slot points at GI046.jpg, a slot's LoadImage node is replaced "
                                           "by a generated-image link, a third slot is added on a missing file"},
    {"id": "schema", "fn": ck_schema, "fault": "a class name is renamed to a class the runtime does not "
                                               "expose, and a key no node of that class accepts is added"},
    {"id": "jobs_static", "fn": ck_jobs, "fault": "the graph totals 243 f against --frames 124, a reference "
                                                  "file is renamed, the id is built paid in a temp root"},
    {"id": "graph_file", "fn": ck_graph_file, "fault": "the on-disk graph carries one extra word in the "
                                                       "prompt"},
    {"id": "prompt_sync", "fn": ck_sync, "fault": "the graph prompt gains a word, the graph seed differs "
                                                  "from the doc header, a section is removed from the doc"},
    {"id": "words", "fn": ck_words, "fault": "detailed_description under 350, over 500, summary over 200"},
    {"id": "beats", "fn": T5.ck_beats, "fault": "a beat past 5.167 s, no beat at 00:00.000, one beat"},
    {"id": "camera", "fn": T5.ck_camera, "fault": "no camera term, no amplitude/speed, no stop/hold clause"},
    {"id": "negation", "fn": ck_negation,
     "fault": "negation wording outside the card's own rows: three added; the card-forced 'no' in the "
              "consent row the card requires is reported, not a fault"},
    {"id": "ages", "fn": ck_ages, "fault": "an age below 21, an age with no canon declaration, a subject "
                                           "with no age"},
    {"id": "card", "fn": ck_card, "fault": "the opening beat loses a card pose; a required card word is "
                                           "dropped; the firing set grows past the measured card-defect set"},
    {"id": "card_noise", "fn": ck_card_noise, "fault": "a card-banned word the card does not force is "
                                                       "charged to a figure"},
    {"id": "card_probe", "fn": ck_card_probe, "fault": "the prompt is a stub, so the seeded rows stop firing"},
    {"id": "ab_shape", "fn": ck_ab_shape, "fault": "the graph moves a shape key (m_shift) against the paid "
                                                   "5 s graph; the seed is set to the paid graph's seed"},
    {"id": "attention", "fn": ck_attention, "fault": "the attention value is one no published source names, "
                                                     "and the built value on a paid id"},
    {"id": "hold", "fn": ck_hold, "fault": "the id is built PAID while the plan's on-hold row is open"},
    {"id": "no_judge", "fn": ck_no_judge, "fault": "the manifest note carries a verdict word"},
]

NOTE = ("The robot (GI063) 5-second clip, built offline. The prose and the graph are gated: the shape is the "
        "paid E5/CK-ATTN single-pass 124-frame euler shape with this scene's prompt, a new seed, its own "
        "prefix and its own two reference files, and the attention value is the published one. Nothing is "
        "queued: the same card's consent row (needs_derrick.md row 21) is an open question to Derrick and the "
        "plan holds this scene on a render-hold rule, so gate `hold` would stop a queue today. The scene's "
        "15 s ids stay armed and unpaid.")


def row21_row():
    """the row itself: needs_derrick.md numbers its rows as markdown list items ('21. **13:20 CT ...')."""
    for ln in open(NEEDS, encoding="utf-8").read().replace("\r\n", "\n").split("\n"):
        if re.match(r"\s*21\.\s", ln):
            return ln.strip()
    return ""


def row21_answered():
    """an answer to that row arrives the way row 18's did (row 29 names it): a LATER numbered row whose
    text names row 21 and an answer. That is the shape of a ruling in this file, measured off row 18/29."""
    out = []
    for ln in open(NEEDS, encoding="utf-8").read().replace("\r\n", "\n").split("\n"):
        m = re.match(r"\s*(\d+)\.\s", ln)
        if m and int(m.group(1)) > 21 and re.search(r"row\s*21\b[^\n]{0,90}?(answer|rul)", ln, re.I):
            out.append(ln.strip())
    return out[0] if out else ""


def run_state():
    src = gload(SRC)
    n, fps = T5.total_frames(src)
    print("STATE source %s = %d nodes, %d frames, %s fps, %.6f s; c0.length %d, sampler %s; canvas %s; "
          "steps %s; shift %s; attention %r; refs %s; seed %s; prefix %r"
          % (SRC, len(src), n, fps, n / fps, src["c0"]["inputs"]["length"],
             json.dumps([v["inputs"].get("sampler_name") for v in src.values()
                         if v["class_type"] == "KSamplerSelect"]),
             (src["c0"]["inputs"]["width"], src["c0"]["inputs"]["height"]),
             json.dumps([v["inputs"]["steps"] for v in src.values() if v["class_type"] == "BasicScheduler"]),
             json.dumps({k: v for k, v in src["m_shift"]["inputs"].items() if k.startswith("shift_")}),
             src["m_attn"]["inputs"]["attention"], json.dumps([t[1] for t in T5.ref_files(src)]),
             src["noise"]["inputs"]["noise_seed"], src["save"]["inputs"]["filename_prefix"]))
    g = build()
    n2, _ = T5.total_frames(g)
    print("STATE target = %d nodes, %d frames, %.6f s, one sampler run, euler, attention %r, seed %d, "
          "prefix %r" % (len(g), n2, n2 / FPS, g["m_attn"]["inputs"]["attention"],
                         g["noise"]["inputs"]["noise_seed"], g["save"]["inputs"]["filename_prefix"]))
    paid = gload(PAID_SHAPE)
    print("STATE paid shape %s = %d nodes, %d frames; the shape diff this item keeps is prompt+seed+prefix"
          % (PAID_SHAPE, len(paid), T5.total_frames(paid)[0]))
    st, have, _ = T5.paid_state(ID)
    print("STATE render evidence for %s: %s (%d of 3)" % (ID, st, len(have)))
    print("STATE needs_derrick row 21 (the consent question, verbatim head): %s"
          % (row21_row()[:170] if row21_row() else "row 21 is not in the file"))
    print("STATE a later row that answers it: %s" % (row21_answered()[:150] if row21_answered()
                                                    else "none: the question is open"))
    print("STATE plan render-hold rule for %s present: %s" % (SCENE, bool(plan_hold_row()[0])))
    txt = g["c0"]["inputs"]["prompt"]
    cm = HC.card_measure(SCENE, txt)
    print("STATE card %s: subjects %d/%d, fires %s; banned tokens %s; every token card-forced: %s"
          % (SCENE, cm["subjects"], cm["card_figures"],
             json.dumps(sorted({c for c, _ in HC.card_fires(SCENE, cm)})),
             json.dumps({k: sorted(set(v)) for k, v in cm["banned_hits"].items()}),
             json.dumps({t: any(t in r for r in card_rows(SCENE))
                         for t in sorted({t for toks in cm["banned_hits"].values() for t in toks})})))
    print("STATE prompt: sections %s; words %s; beats %s; negation %s; camera %s"
          % (list(sections_of(txt).keys()), {k: len(v.split()) for k, v in sections_of(txt).items()},
             A31.beat_times(txt), json.dumps(neg_forced(txt)[0]),
             sorted({t for t in A31.CAM_TERMS if t in sections_of(txt)["detailed_description"]})))


def probe_paid():
    """the paid-state classifier is live: every state is built in a temp root, so the real disk decides nothing."""
    res = []
    for state in ("paid", "free", "half-paid"):
        tmp = tempfile.mkdtemp(prefix="orcpaid")
        try:
            d = os.path.join(tmp, "runs", ID)
            if state == "free":
                os.makedirs(os.path.join(tmp, "jobs"))          # no run dir, no output dir, no result.json
            if state in ("paid", "half-paid"):
                os.makedirs(d)
                open(os.path.join(d, "status.log"), "w").close()
                open(os.path.join(d, "objective.json"), "w").close()
            if state == "paid":
                os.makedirs(os.path.join(tmp, "out", ID))       # L20: the third piece is the output folder
            want = "paid" if state == "paid" else "free" if state == "free" else "half-paid"
            got, have, _ = T5.paid_state(ID, roots=tmp)
            res.append((state, got == want, "evidence %d/3" % len(have)))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return res


def probe_hold(g, ctx):
    """the hold gate answers off the plan rule and the render proof, both built here: rule present + paid
    id fires (a render before the ruling); rule present + unpaid is clean; rule gone fires in both states
    (the basis moved)."""
    _r, plan = plan_hold_row()
    rule = "- %s: on hold until Derrick rules on needs_derrick.md row 21. Do not render." % SCENE
    cases = [("rule present + paid id", rule, True, True), ("rule present + unpaid id", rule, False, False),
             ("rule gone + paid id", None, True, True), ("rule gone + unpaid id", None, False, True)]
    out = []
    for label, row, paid, want_fire in cases:
        c = dict(ctx)
        c["probe"] = True
        c["paid"] = "paid" if paid else "free"
        c["hold_paid"] = paid
        c["plan_row"] = (row, plan)
        hits = ck_hold(g, c)
        out.append((label, bool(hits) == want_fire, hits[:1]))
    return out


def attn_probe_cases(g, ctx):
    """the attention-value gate is live: the built value on a free id is clean (the paid state of this id is
    free), the published value on a PAID id is clean, a value no published source names fires on both states,
    and on a paid id the non-published value fires (a paid clip cannot carry the published value)."""
    cases = [("built value on a free id", g, "free", False)]
    for val in (ATTN, OTHER_ATTN, "flash attention"):
        gg = copy.deepcopy(g)
        gg["m_attn"]["inputs"]["attention"] = val
        cases.append(("built value %r on a free id" % val, gg, "free", val != ATTN))
        cases.append(("built value %r on a paid id" % val, gg, "paid", val != ATTN))
    return cases


SEEDS = []


def seed(name, gates):
    def deco(fn):
        SEEDS.append((name, fn))
        return fn
    return deco


def set_prompt(g, ctx, txt):
    """a prompt-side fault: the graph, the measured prompt and the card measurement move together."""
    g["c0"]["inputs"]["prompt"] = txt
    ctx["prompt"] = txt
    ctx["card"] = HC.card_measure(SCENE, txt)


@seed("source shape moved", "state")
def s_state(g, ctx):
    ctx["src"] = copy.deepcopy(src_graph(ctx))
    ctx["src"]["c0"]["inputs"]["length"] = 124
    ctx["src"]["ksel"]["inputs"]["sampler_name"] = "euler"


@seed("node set and keys moved", "derive")
def s_derive(g, ctx):
    g.pop("g0")
    g["m_vsa"]["inputs"]["extra_key"] = 1
    g["dec_v"]["inputs"]["vae"] = ["c1", 0]


@seed("frames 15 s", "frames, jobs_static")
def s_frames(g, ctx):
    g["c0"]["inputs"]["length"] = 243


@seed("continuation restored", "single, derive")
def s_single(g, ctx):
    src = src_graph(ctx)
    for n in DROP:
        g[n] = copy.deepcopy(src[n])


@seed("sampler not euler", "sampler")
def s_sampler(g, ctx):
    g["ksel"]["inputs"]["sampler_name"] = "res_multistep"


@seed("steps 8 to 12", "untouched")
def s_steps(g, ctx):
    g["s0_sched"]["inputs"]["steps"] = 12


@seed("shift moved", "untouched, ab_shape")
def s_shift(g, ctx):
    g["m_shift"]["inputs"]["shift_to"] = 5.0


@seed("canvas moved", "untouched")
def s_canvas(g, ctx):
    g["c0"]["inputs"]["width"] = 1024


@seed("source seed reused", "untouched, derive")
def s_seedreuse(g, ctx):
    g["noise"]["inputs"]["noise_seed"] = src_graph(ctx)["noise"]["inputs"]["noise_seed"]


@seed("ref slot edge rewired", "untouched")
def s_edge(g, ctx):
    g["c0"]["inputs"]["ref_images.ref_image_2"] = ["img", 0]


@seed("ref target is another scene's card", "refs, untouched")
def s_ref(g, ctx):
    g["img2"]["inputs"]["image"] = "community/hc/GI046.jpg"


@seed("a third ref slot on a missing file", "refs")
def s_ref3(g, ctx):
    g["img3"] = {"class_type": "LoadImage", "_meta": {"title": "LoadImage"},
                 "inputs": {"image": "community/hc/GI063_w2_face.png"}}
    g["c0"]["inputs"]["ref_images.ref_image_3"] = ["img3", 0]


@seed("class not in the schema", "schema")
def s_cls(g, ctx):
    g["m_attn"]["class_type"] = "ModelAttentionBackends"


@seed("key not in the schema", "schema")
def s_key(g, ctx):
    g["m_vsa"]["inputs"]["sparse_blocks"] = 4


@seed("the id is paid and the graph carries the non-published attention value", "attention (the paid branch), jobs_static")
def s_paid(g, ctx):
    ctx["paid"] = "paid"
    g["m_attn"]["inputs"]["attention"] = OTHER_ATTN


@seed("graph on disk carries an extra word", "graph_file, prompt_sync")
def s_disk(g, ctx):
    ctx["on_disk"] = copy.deepcopy(g)
    ctx["on_disk"]["c0"]["inputs"]["prompt"] = g["c0"]["inputs"]["prompt"] + " her hand rests."


@seed("graph prompt gains a word", "prompt_sync")
def s_sync(g, ctx):
    g["c0"]["inputs"]["prompt"] = g["c0"]["inputs"]["prompt"] + " her hand rests."


@seed("graph seed is not the doc seed", "prompt_sync, derive")
def s_syncseed(g, ctx):
    g["noise"]["inputs"]["noise_seed"] = SEED + 1


@seed("doc block loses a section", "prompt_sync")
def s_docsec(g, ctx):
    sec = dict(ctx["block"]["sections"])
    sec.pop("retention_analysis")
    ctx["block"] = dict(ctx["block"])
    ctx["block"]["sections"] = sec


@seed("prose off the word band", "words")
def s_words(g, ctx):
    txt = "\n".join(l for l in ctx["prompt"].splitlines()
                   if not l.startswith("[Shot 1] <Picture 1> is the first frame"))
    set_prompt(g, ctx, txt)


@seed("a beat past the clip", "beats")
def s_beats(g, ctx):
    set_prompt(g, ctx, ctx["prompt"] + "\nAt 00:10.000, the pair settle, the frames hold on the room.")


@seed("no camera wording", "camera")
def s_camera(g, ctx):
    txt = ctx["prompt"].replace(
        "The camera opens on a Static Shot of the pair, then a Push In with small amplitude at slow speed "
        "closes the lens distance by a hand's width across the first third of the segment, and from "
        "00:03.600 the camera stops and holds the same frame for the rest of the segment.",
        "The pair stay as the photograph frames them, and the room, light and lens distance stay as the "
        "photograph built them.")
    assert txt != ctx["prompt"], "the camera sentence moved in the doc: fix this seed"
    set_prompt(g, ctx, txt)


@seed("three negations", "negation")
def s_neg(g, ctx):
    set_prompt(g, ctx, ctx["prompt"] + "\nno lens move, not slow, never bright.")


@seed("an age below 21", "ages")
def s_age1(g, ctx):
    txt = ctx["prompt"].replace("aged 31 of a fictional", "aged 19 of a fictional", 1)
    assert txt != ctx["prompt"], "the subject line moved in the doc: fix this seed"
    set_prompt(g, ctx, txt)


@seed("an age with no canon declaration", "ages")
def s_age2(g, ctx):
    txt = ctx["prompt"].replace("aged 27 (canon declaration)", "aged 27", 1)
    assert txt != ctx["prompt"], "the subject line moved in the doc: fix this seed"
    set_prompt(g, ctx, txt)


@seed("a subject with no age", "ages")
def s_age3(g, ctx):
    txt = ctx["prompt"].replace("a fictional adult aged 27 (canon declaration): fair",
                                "a fictional adult: fair", 1)
    assert txt != ctx["prompt"], "the subject line moved in the doc: fix this seed"
    set_prompt(g, ctx, txt)


@seed("opening beat loses a card pose", "card")
def s_card1(g, ctx):
    txt = ctx["prompt"].replace("bent at waist over her hips with one hand", "over her hips with one hand", 1)
    assert txt != ctx["prompt"], "the opening beat moved in the doc: fix this seed"
    set_prompt(g, ctx, txt)


@seed("a required card word is dropped", "card")
def s_card2(g, ctx):
    txt = ctx["prompt"].replace("heavy silver chains", "chains")
    assert txt != ctx["prompt"], "a card-mandated token moved in the doc: fix this seed"
    set_prompt(g, ctx, txt)


@seed("a real card-banned word", "card, card_noise")
def s_card3(g, ctx):
    txt = ctx["prompt"].replace("head turned toward camera, mouth slightly open",
                                "head turned toward camera, she is smiling", 1)
    assert txt != ctx["prompt"], "the evidence row moved in the doc: fix this seed"
    set_prompt(g, ctx, txt)


@seed("the prompt is a stub", "card_probe, card, words, ages")
def s_stub(g, ctx):
    set_prompt(g, ctx, "<Picture 1> shows a room.")


@seed("shape key moved against the paid clip", "ab_shape, untouched, derive")
def s_ab(g, ctx):
    g["m_shift"]["inputs"]["shift_video"] = 12.0


@seed("the paid clip's seed reused", "ab_shape")
def s_abseed(g, ctx):
    ps = gload(PAID_SHAPE)["noise"]["inputs"]["noise_seed"]
    g["noise"]["inputs"]["noise_seed"] = ps
    ctx["block"] = dict(ctx["block"])
    ctx["block"]["seed"] = ps


@seed("the source prefix reused", "derive, jobs_static")
def s_prefix(g, ctx):
    g["save"]["inputs"]["filename_prefix"] = src_graph(ctx)["save"]["inputs"]["filename_prefix"]


@seed("attention is not the published value", "attention, derive")
def s_attn(g, ctx):
    g["m_attn"]["inputs"]["attention"] = "flash attention"


@seed("a render before the ruling", "hold")
def s_hold(g, ctx):
    ctx["paid"] = "paid"
    ctx["hold_paid"] = True


@seed("the manifest carries a verdict word", "no_judge")
def s_note(g, ctx):
    ctx["note"] = "The robot clip is the best of the set."


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", action="store_true")
    ap.add_argument("--emit", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.state:
        return run_state()
    g = build()
    txt = g["c0"]["inputs"]["prompt"]
    paid = T5.paid_state(ID)[0]
    ctx = {"block": block(), "prompt": txt, "card": HC.card_measure(SCENE, txt), "paid": paid,
           "hold_paid": paid == "paid", "note": NOTE}
    if a.emit:
        path = os.path.join(GRAPHS, ID + ".api.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(g, fh, indent=2, sort_keys=True)
        print("WROTE %s\nNEXT: gpu_guard IDLE, gpu_lock, then run_graph_job.py --frames %d. The render is "
              "held by needs_derrick row 21: this pass queues nothing." % (path, FRAMES))
        return
    if a.check:
        try:
            ctx["on_disk"] = json.load(open(os.path.join(GRAPHS, ID + ".api.json"), encoding="utf-8"))
        except OSError as e:
            ctx["on_disk"] = None
            print("NOTE the graph file is unreadable: %s" % e)
        m = measure(g, ctx)
        fails = []
        for d in GATES:
            try:
                out = d["fn"](g, ctx)
            except Exception as e:
                out = ["%s raised %r" % (d["id"].upper(), e)]
            if out:
                fails.append((d["id"], out[0]))
        print(json.dumps(m, indent=1, sort_keys=True))
        print("VERDICT " + ("NOT CLEAN " + "; ".join(i for i, _ in fails) if fails
                            else "CLEAN %d gates, %d nodes, %d frames, %s, card fires %s and every token is "
                                 "card-forced" % (len(GATES), len(g), m["frames"], m["attention_state"],
                                                  ",".join(m["card_fires"]))))
        return 1 if fails else 0
    if a.selftest:
        fired, fails = [], []
        # the graph-file gate owns the file on disk; the selftest seeds it directly, so the NO-OP reads the
        # emitted file when it exists and the built graph when it does not (run --emit before --check).
        try:
            ctx["on_disk"] = json.load(open(os.path.join(GRAPHS, ID + ".api.json"), encoding="utf-8"))
        except OSError:
            ctx["on_disk"] = g
            print("NOTE the graph file is not on disk yet: run --emit, then --check. The selftest reads the "
                  "built graph for that one gate.")
        for name, fn in SEEDS:
            gg = copy.deepcopy(g)
            c2 = dict(ctx)
            hits = []
            try:
                fn(gg, c2)
            except AssertionError as e:
                fails.append("SEED %s: the doc moved under the seed: %s" % (name, e))
                fired.append((name, ["doc_moved"]))
                continue
            for d in GATES:
                try:
                    hits += d["fn"](gg, c2)
                except Exception as e:
                    hits.append("%s raised %r" % (d["id"].upper(), e))
            fired.append((name, sorted({x.split(" ")[0].replace("-", "_").lower() for x in hits})))
            if not hits:
                fails.append("SEED %s fires NO gate - a seeded fault no check can see" % name)
        print("SEEDED FAULTS:")
        for name, codes in fired:
            print("  %-42s %s" % (name, ",".join(codes) if codes else "NONE"))
        print("PAID-STATE PROBES (temp roots, the real disk decides nothing):")
        for st, ok, note in probe_paid():
            print("  %-12s %s  %s" % (st, "OK" if ok else "FAIL", note))
            if not ok:
                fails.append("PROBE paid_state returns the wrong state for a built %s root" % st)
        print("HOLD-STATE PROBES (the plan row and the render proof, both built here):")
        for label, ok, hits in probe_hold(g, ctx):
            print("  %-24s %s  %s" % (label, "OK" if ok else "FAIL", hits))
            if not ok:
                fails.append("PROBE the hold gate does not answer the plan/proof matrix: %s" % label)
        print("ATTENTION-VALUE PROBES (the built graph, copied):")
        for label, gg, st, want_fire in attn_probe_cases(g, ctx):
            hits = ck_attention(gg, {"paid": st})
            ok = bool(hits) == want_fire
            print("  %-46s %s  %s" % (label, "OK" if ok else "FAIL", hits[:1]))
            if not ok:
                fails.append("PROBE the attention gate does not answer the published-rule matrix: %s" % label)
        noop = []
        for d in GATES:
            try:
                noop += [(d["id"], x) for x in d["fn"](g, ctx)]
            except Exception as e:
                noop.append((d["id"], "raised %r" % e))
        print("NO-OP: every gate on the unseeded built graph, prompt and manifest:", noop)
        if noop:
            fails.append("NO-OP: gates firing on the real artifact: %s" % noop)
        silent = len([f for f in fails if f.startswith("SEED")])
        probes_bad = len([f for f in fails if f.startswith("PROBE")])
        print("SELFTEST: %d/%d seeds fired, %d silent, %d no-op, %d probes failed"
              % (len(fired) - silent, len(fired), silent, len(noop), probes_bad))
        print("SELFTEST " + ("ABORT " + "; ".join(fails) if fails
                             else "PASS %d/%d fired, 0 silent, 0 no-op, 0 probes failed"
                             % (len(fired), len(fired))))
        return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main() or 0)
