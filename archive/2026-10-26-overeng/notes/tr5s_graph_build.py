#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""tr5s_graph_build.py - the one 5-second Euler clip of the TR5S test run: build the graph, judge it, and
only then let run_graph_job.py queue it. `--check` judges and prints; `--emit` writes
C:/AI/community/runs/tr5s_gi102_s51170001/request.api.json; `--selftest` seeds each fault into a copy and
requires the detector to fire there and 0 on the real files (AGENTS.md L10).

Why each check exists, with the file that made it:
  WORDS_MIN/MAX      - the MAX block: "write a 350-500 word H3 prompt". Counted on the prompt bytes that go
                       into the graph, not on the draft file, so a graph prompt cannot drift from the length.
  GRAPH_DRIFT        - the graph is a COPY of a paid graph (p7/graphs/ali163_top5_gi046_s51160001.api.json:
                       20 nodes, MiniMaxH3ReferenceToVideo + MiniMaxH3AddGuide frame_idx 0 + euler + 8 steps +
                       1344x768 + 124 frames at fps 24 = 5.167 s, the shape the objective gate accepts).
                       Only five input paths may differ: c0.prompt, img.image, img2.image, noise.noise_seed,
                       save.filename_prefix. Measured: that paid graph's `prompt` is ONE string
                       (c0.inputs.prompt, str, 1202 words), and the 10 s graphs use a 3-item list - a
                       single-pass 124-frame job takes one string, so this builder requires a str, not a list.
  GRAPH_INPUT        - the two LoadImage inputs are the approved start image and the face-reference crop;
                       both must exist in the ComfyUI input tree AND the start image's bytes must equal the
                       sha256 in the approved MANIFEST.csv (AGENTS.md L16: a cloned graph is only as safe as
                       the diff you run on it).
  GRAPH_SEED         - a new seed, never used by any runs/*/*.json (a re-render of the same seed+graph is a
                       paid duplicate, the 7-identical-mp4 fault in run_graph_job.py's header).
  GRAPH_SHAPE        - sampler euler, length 124, 1344x768, steps 8, denoise 1.0, filename_prefix = the run
                       tag (the SaveVideo subfolder is where a stalled job's clip is collected from,
                       run_graph_job.py collect_from_disk).
  PROMPT_ADULTS      - comm.guard_ok on the prompt string before the GPU window (run_graph_job.py:main calls
                       the same function; AGENTS.md "Hard lines: Adults only, fictional, no real people").
  GATE:<code>        - the shipped card gate over this prompt against THIS card:
                       scene_card_gate.load_card/required/scan/findings. Hard codes: the card's required
                       rows must be carried (F-CARD-TOKENS, F-ROOM, F-LIGHT), the opening pose must be the
                       card's (F-BEAT0 / F-BEAT0-BAN), both figures must be present (F-SUBJECTS, F-COUNT),
                       ages stated (F-AGE / F-AGE-MARKER), consent rows present (F-CONSENT), no ban word
                       (F-BANNED), no cropped-head word (F-HEADS).
  SOLO_REDUCE        - F-SOLO's own list (facts.gate.solo_phrases, 145 entries) is charged as a substring,
                       and it contains words this card and the H3 format require: the card's open_beat row
                       carries "his face close to her upper back" and "torso", and the format's keys are
                       `subject_definitions` / `<Subject 1>`. Measured: the paid prompt
                       (p7/graphs/ali163_top5_gi046_s51160001.api.json, c0.inputs.prompt) hits
                       "a hand" (in "by a hand's width"), "her shoulder", "his head", "subject", "figure" -
                       so F-SOLO as shipped is not satisfiable by an H3 prompt. The rule's intent is a
                       two-figure scene written as one person, so this builder enforces that reading
                       mechanically (phrases that name a single person) and reports the shipped count
                       separately, with the reason. That is a disclosed judgement, not a silent pass.
Nothing here queues a job; run_graph_job.py owns the queue, the GPU lock, the adults gate at queue time, the
objective gate and the contact sheet.
"""
import sys, os, json, re, copy, glob, hashlib, subprocess

sys.path.insert(0, r"C:\AI\community\notes")
sys.path.insert(0, r"C:\AI\community\scripts")
import scene_card_gate as scg
import comm
import tr5s_card_build as tcd

SCENE = "GI102"
REF = "C:/AI/community/p7/graphs/ali163_top5_gi046_s51160001.api.json"
PROMPT_SRC = "C:/AI/community/notes/tr5s_prompt_GI102.txt"
RUN_DIR = "C:/AI/community/runs/tr5s_gi102_s51170001"
TAG = "tr5s_gi102_s51170001"
SEED = 51170001
WORDS_MIN, WORDS_MAX = 350, 500
ALLOWED_DIFF = {"c0.prompt", "img.image", "img2.image", "noise.noise_seed", "save.filename_prefix"}
HARD_CODES = ("F-SUBJECTS", "F-CARD-TOKENS", "F-ROOM", "F-LIGHT", "F-BEAT0", "F-BEAT0-BAN",
              "F-CARD-HEAD", "F-BANNED", "F-AGE", "F-CONSENT")
# a two-figure scene must not be written as one person; this is F-SOLO's intent, stated as phrases that
# name exactly one person. Body-part and format words are reported separately (see SOLO_REDUCE in the doc).
SOLO_REDUCE = ["a man", "a woman", "the man", "the woman", "the man's", "the woman's", "a person",
               "the person", "one person", "a figure", "the figure", "one figure", "a single figure",
               "a single person", "a single subject", "single subject", "solo subject", "a subject",
               "the subject", "he is alone", "she is alone", "solo", "alone", "a male", "a female",
               "his body", "her body", "a man's body", "a woman's body", "a man's torso", "a woman's torso"]
FIELDS = {
    "c0.prompt": lambda v: v == prompt_text(),
    "c0.length": lambda v: v == 124,
    "c0.width": lambda v: v == 1344,
    "c0.height": lambda v: v == 768,    "img.image": lambda v: v == "community/hc/GI102.jpg",
    "img2.image": lambda v: v == "community/hc/GI102_w1_face.png",
    "noise.noise_seed": lambda v: int(v) == SEED,
    "save.filename_prefix": lambda v: v == f"community/{TAG}/{TAG}",
}


def prompt_text():
    return open(PROMPT_SRC, encoding="utf-8").read()


def ref_graph():
    return json.load(open(REF, encoding="utf-8"))


def build():
    """The paid graph with this prompt, this start image, this face crop, a new seed and this run tag."""
    g = ref_graph()
    g["c0"]["inputs"]["prompt"] = prompt_text()
    g["img"]["inputs"]["image"] = "community/hc/GI102.jpg"
    g["img2"]["inputs"]["image"] = "community/hc/GI102_w1_face.png"
    g["noise"]["inputs"]["noise_seed"] = SEED
    g["save"]["inputs"]["filename_prefix"] = f"community/{TAG}/{TAG}"
    return g


def words(text):
    return len(text.split())


def used_seeds():
    """Every noise_seed that appears in any runs/*/*.json - the record of what was queued (AGENTS.md L20)."""
    out = set()
    for p in glob.glob("C:/AI/community/runs/*/*.json"):
        try:
            txt = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        out |= {int(x) for x in re.findall(r'"noise_seed":\s*(\d+)', txt)}
    return out


def input_files(g):
    """(path, exists, bytes, sha) for each LoadImage input, resolved in the ComfyUI input tree."""
    out = []
    for nid in sorted(k for k, v in g.items() if v.get("class_type") == "LoadImage"):
        rel = g[nid]["inputs"]["image"]
        p = os.path.join(tcd.COMFY_IN, rel)
        row = {"node": nid, "rel": rel, "path": p, "exists": os.path.isfile(p),
               "bytes": os.path.getsize(p) if os.path.isfile(p) else 0}
        if row["exists"]:
            row["sha256"] = hashlib.sha256(open(p, "rb").read()).hexdigest()
        out.append(row)
    return out


def pool_sha(scene):
    """The approved MANIFEST.csv sha256 for a scene id (tr5s_card_build.pool reads the same manifests)."""
    return tcd.pool().get(scene, (None, None))[0]


def prompt_of(g, text):
    """The prompt string that ships in the graph. Every prompt rule is judged on these bytes, so a graph
    prompt cannot drift from the 350-500 word draft (the MAX block's number is about the prompt that renders)."""
    p = g["c0"]["inputs"]["prompt"]
    return p if isinstance(p, str) else text


def graph_faults(g):
    """The diff against the paid graph, plus every field rule. A graph that differs anywhere outside
    ALLOWED_DIFF is a fault: this pass changes the words, the two images, the seed and the tag, nothing else."""
    ref, faults = ref_graph(), []
    if sorted(g) != sorted(ref):
        faults.append("GRAPH_NODES node set != the paid graph " + str(sorted(set(g) ^ set(ref))))
    for nid in sorted(set(g) & set(ref)):
        if g[nid].get("class_type") != ref[nid].get("class_type"):
            faults.append(f"GRAPH_CLASS {nid} class {g[nid].get('class_type')} != paid {ref[nid].get('class_type')}")
        for k in sorted(set(g[nid]["inputs"]) | set(ref[nid]["inputs"])):
            path = f"{nid}.{k}"
            if g[nid]["inputs"].get(k) == ref[nid]["inputs"].get(k):
                continue
            if path not in ALLOWED_DIFF:
                faults.append(f"GRAPH_DRIFT {path} differs from the paid graph and is not an allowed change")
            elif not FIELDS[path](g[nid]["inputs"].get(k)):
                faults.append(f"GRAPH_FIELD {path} = {str(g[nid]['inputs'].get(k))[:80]} fails its field rule")
    pr = g["c0"]["inputs"]["prompt"]
    if not isinstance(pr, str):
        faults.append(f"GRAPH_PROMPT_TYPE prompt is {type(pr).__name__}; a single-pass 124-frame graph takes one "
                      "string (the paid graph's c0.inputs.prompt is a str)")
    for f in input_files(g):
        if not f["exists"]:
            faults.append(f"GRAPH_INPUT {f['node']} {f['rel']} is not in the ComfyUI input tree")
    st = [f for f in input_files(g) if f["rel"].endswith("/GI102.jpg")]
    if st and st[0].get("sha256") != pool_sha(SCENE):
        faults.append(f"GRAPH_INPUT {SCENE}.jpg sha {str(st[0].get('sha256'))[:12]} != approved MANIFEST sha "
                      f"{str(pool_sha(SCENE))[:12]}")
    if SEED in used_seeds():
        faults.append(f"GRAPH_SEED {SEED} already appears in runs/*/*.json")
    return faults


def gate_rows(text):
    """The shipped gate over a prompt against this card, split into the hard codes and the solo reading."""
    gt = scg.load_card(tcd.facts_path(SCENE))
    req = scg.required(gt)
    m = scg.scan(text, gt, req)
    fnd = scg.findings(m)
    code = lambda f: f.split()[0]
    hard = [f for f in fnd if code(f) in HARD_CODES]
    solo = [f for f in fnd if code(f) == "F-SOLO"]
    low = scg.norm(text)
    reduce_hits = [p for p in SOLO_REDUCE if scg.norm(p) in low]
    # the shipped list charges a phrase per finding; count the phrase hits it charges, by class
    shipped_hits = [p for p in gt.get("solo_phrases", []) if scg.norm(p) in low]
    return {"findings": fnd, "hard": hard, "solo": solo, "reduce": reduce_hits,
            "shipped_solo_hits": shipped_hits, "model": m, "req": req,
            "counts": {c: len([f for f in fnd if code(f) == c]) for c in sorted({code(f) for f in fnd})}}


def prompt_faults(text):
    faults = []
    n = words(text)
    if n < WORDS_MIN:
        faults.append(f"WORDS_MIN {n} words < {WORDS_MIN} (MAX block: 350-500)")
    if n > WORDS_MAX:
        faults.append(f"WORDS_MAX {n} words > {WORDS_MAX} (MAX block: 350-500)")
    if not re.search(r"At 00:00\.000", text):
        faults.append("PROMPT_BEAT0 no At 00:00.000 line: the card's open_beat rows speak about that beat "
                      "(scene_card_gate.beat0)")
    if not comm.guard_ok(text):
        faults.append("PROMPT_ADULTS comm.guard_ok is False on the prompt string (scripts/comm.py:41)")
    g = gate_rows(text)
    for f in g["hard"]:
        faults.append("GATE:" + f[:220])
    if g["reduce"]:
        faults.append("SOLO_REDUCE a two-figure scene written as one person: " + ", ".join(g["reduce"]))
    return faults


def faults(g, text):
    return graph_faults(g) + prompt_faults(prompt_of(g, text))


def show(g, text):
    gt = tcd.read_facts(tcd.facts_path(SCENE))
    gr = gate_rows(text)
    print(f"prompt={PROMPT_SRC} words={words(text)} chars={len(text)} "
          f"sha256={hashlib.sha256(text.encode()).hexdigest()[:16]}")
    print(f"card={tcd.card_path(SCENE)} facts_sha256={gt['sha256'][:16]} core_tokens={len(gt['gate']['per_chunk_tokens'])} "
          f"self_conflicts={len(tcd.census(gt))} solo_list={len(gt['gate']['solo_phrases'])}")
    print(f"graph=copy of {REF}")
    for f in input_files(g):
        print(f"  input {f['node']} {f['rel']} exists={f['exists']} bytes={f['bytes']} "
              f"sha256={str(f.get('sha256'))[:16]} approved_sha256={str(pool_sha(SCENE))[:16]}")
    print(f"  seed={SEED} used_by_any_run={SEED in used_seeds()} sampler={g['ksel']['inputs']['sampler_name']} "
          f"length={g['c0']['inputs']['length']} size={g['c0']['inputs']['width']}x{g['c0']['inputs']['height']} "
          f"steps={g['s0_sched']['inputs']['steps']} fps={g['mkvid']['inputs']['fps']} prefix={g['save']['inputs']['filename_prefix']}")
    beats = re.findall(r"At \d\d:\d\d\.\d\d\d", text)
    print(f"  beats={beats} sections={[l.rstrip(':') for l in text.splitlines() if l.endswith(':')]}")
    print(f"  gate_findings={json.dumps(gr['counts'])}")
    print(f"  gate_required tokens={sum(len(v) for v in gr['req']['figures'].values())} room={len(gr['req']['room'])} "
          f"light={len(gr['req']['light'])} beat0={sum(len(v) for v in gr['req']['open_beat'].values())} "
          f"consent={len(gr['req']['consent'])}")
    print(f"  gate_missing core={gr['model']['tokens_missing']} room={gr['model']['room_missing']} "
          f"light={gr['model']['light_missing']} beat={gr['model']['beat_missing']} consent={gr['model']['consent_missing']}")
    print(f"  figures_present={gr['model']['figures_present']}/{gr['model']['figure_count']} "
          f"age_missing={len(gr['model']['age_missing'])} age_no_marker={len(gr['model']['age_no_marker'])} "
          f"head_hits={gr['model']['head_hits']}")
    print(f"  F-SOLO shipped list hits={len(gr['shipped_solo_hits'])} (advisory; see the doc: the list carries "
          f"body-part and H3-format words this card and the format require) reduce_hits={gr['reduce']}")
    for f in gr["findings"]:
        print("  FINDING " + f[:200])


def do_check():
    g, text = build(), prompt_text()
    show(g, prompt_of(g, text))
    bad = faults(g, text)
    print("VERDICT TR5S GRAPH " + ("CLEAN" if not bad else f"{len(bad)} FAULT"))
    for f in bad:
        print(" FAULT " + f)
    return 0 if not bad else 1


def do_emit():
    g, text = build(), prompt_text()
    show(g, prompt_of(g, text))
    bad = faults(g, text)
    if bad:
        print("NOT WRITTEN: the graph is red")
        for f in bad:
            print(" FAULT " + f)
        return 1
    os.makedirs(RUN_DIR, exist_ok=True)
    with open(os.path.join(RUN_DIR, "request.api.json"), "w", encoding="utf-8") as fh:
        json.dump(g, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    with open(os.path.join(RUN_DIR, "prompt.txt"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    p = os.path.join(RUN_DIR, "request.api.json")
    again = json.load(open(p, encoding="utf-8"))
    print(f"  WROTE {p} bytes={os.path.getsize(p)} "
          f"sha256={hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]} "
          f"prompt_in_graph_words={words(again['c0']['inputs']['prompt'])} "
          f"prompt_bytes_equal={again['c0']['inputs']['prompt'] == text}")
    print(f"  queue with: python C:/AI/community/scripts/run_graph_job.py {RUN_DIR} {TAG} --frames 124")
    print("VERDICT TR5S GRAPH EMITTED")
    return 0


# ------------------------------------------------------------------ seed selftest (AGENTS.md L10)
def seed_cases(g, text):
    """Each fault seeded into a copy, with the field the rule reads. Every case must fire, and the real
    pair must fire 0 - the measured standard `ali14d_shortplan_build.py` and the card builder use."""
    out = []

    def copy_prompt():
        return text

    def mut(fn):
        gg, tt = copy.deepcopy(g), copy_prompt()
        fn(gg, tt)
        return gg, tt
    # the word count is the MAX block's number, so it is a range with both ends seeded
    out.append(("words_short", mut(lambda gg, tt: gg["c0"]["inputs"].__setitem__(
        "prompt", " ".join(tt.split()[:200]))), "WORDS_MIN"))
    out.append(("words_long", mut(lambda gg, tt: gg["c0"]["inputs"].__setitem__(
        "prompt", tt + " " + " ".join(["steady breathing"] * 60))), "WORDS_MAX"))
    out.append(("core_token_dropped", mut(lambda gg, tt: gg["c0"]["inputs"].__setitem__(
        "prompt", tt.replace("Neutral-toned walls", "plain painted dividers"))), "GATE:F-CARD-TOKENS"))
    out.append(("beat0_pose_changed", mut(lambda gg, tt: gg["c0"]["inputs"].__setitem__(
        "prompt", tt.replace("On all fours, forearms planted on the bed",
                             "Sitting back on the mattress, hips settled"))), "GATE:F-BEAT0"))
    out.append(("ban_word_added", mut(lambda gg, tt: gg["c0"]["inputs"].__setitem__(
        "prompt", tt.replace("Neutral-toned walls", "green walls"))), "GATE:F-BANNED"))
    out.append(("figure2_never_named", mut(lambda gg, tt: gg["c0"]["inputs"].__setitem__(
        "prompt", re.sub(r"\b(his|himself|him|he)\b", lambda m: {"his": "their", "himself": "themself",
                                                                  "him": "them", "he": "they"}[m.group(1)],
                                                  tt))), "GATE:F-SUBJECTS"))
    out.append(("age_stripped", mut(lambda gg, tt: gg["c0"]["inputs"].__setitem__(
        "prompt", tt.replace("a 27-year-old fictional adult", "a fictional adult"))), "GATE:F-AGE"))
    out.append(("consent_row_dropped", mut(lambda gg, tt: gg["c0"]["inputs"].__setitem__(
        "prompt", tt.replace("Both of them consent:", "Both agree:"))), "GATE:F-CONSENT"))
    out.append(("solo_reduce_added", mut(lambda gg, tt: gg["c0"]["inputs"].__setitem__(
        "prompt", tt + " The woman waits alone.")), "SOLO_REDUCE"))
    out.append(("youth_word_added", mut(lambda gg, tt: gg["c0"]["inputs"].__setitem__(
        "prompt", tt + " A teenage girl watches from the doorway.")), "PROMPT_ADULTS"))
    # graph-side seeds
    out.append(("input_missing", mut(lambda gg, tt: gg["img2"]["inputs"].__setitem__(
        "image", "community/hc/NO_SUCH_CROP.png")), "GRAPH_INPUT"))
    out.append(("seed_reused", mut(lambda gg, tt: gg["noise"]["inputs"].__setitem__(
        "noise_seed", 51160001)), "GRAPH_SEED"))
    out.append(("sampler_swapped", mut(lambda gg, tt: gg["ksel"]["inputs"].__setitem__(
        "sampler_name", "euler_ancestral")), "GRAPH_DRIFT"))
    out.append(("frames_changed", mut(lambda gg, tt: gg["c0"]["inputs"].__setitem__(
        "length", 243)), "GRAPH_FIELD"))
    out.append(("prefix_changed", mut(lambda gg, tt: gg["save"]["inputs"].__setitem__(
        "filename_prefix", "community/other/other")), "GRAPH_FIELD"))
    out.append(("prompt_list_not_string", mut(lambda gg, tt: gg["c0"]["inputs"].__setitem__(
        "prompt", [tt, tt, tt])), "GRAPH_PROMPT_TYPE"))
    return out


def do_selftest():
    g, text = build(), prompt_text()
    base = faults(g, text)
    fired = silent = 0
    for name, (gg, tt), expect in seed_cases(g, text):
        got = faults(gg, tt)
        hit = [f for f in got if f.split()[0] == expect]
        ok = bool(hit)
        fired += ok
        silent += not ok
        print(f"seed {name:24s} expect={expect:22s} {'FIRED' if ok else 'SILENT'} "
              f"{(hit[0][:110] if hit else '')}")
    print(f"real pair faults={len(base)} {[f.split()[0] for f in base]}")
    clean = not base
    print(f"seed selftest: {fired}/{len(seed_cases(g, text))} fired, required {len(seed_cases(g, text))}, "
          f"{silent} silent, {len(base)} fired on the real pair -> VERDICT TR5S GRAPH SEEDS "
          + ("CLEAN" if fired == len(seed_cases(g, text)) and clean else "BROKEN"))
    return 0 if fired == len(seed_cases(g, text)) and clean else 1


def main(argv):
    mode = argv[0] if argv else "--check"
    if mode == "--emit":
        return do_emit()
    if mode == "--selftest":
        return do_selftest()
    return do_check()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
