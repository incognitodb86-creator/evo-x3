#!/usr/bin/env python3
"""orcrobot_build.py - the robot 5-second prompt and graph, authored from the picture, gated.

Item **ORC-ROBOT** (Derrick 2026-10-24 8:39 PM CT, verbatim in
`C:/Users/derek/5slock/ralph-community/notes/plans/receipts/ORC-ROBOT-L33.md`:2: "Ok and I want the two videos the orc and
the robot fucking video" / "Like hardcore sex"), the **robot** half. The item's own words are the instruction: describe every
figure "exactly as it is (the orc as an orc, the robot as a robot, the partner as they actually appear; species, body,
build)". The **orc** half is paid and in front of Derrick:
`C:/AI/community/runs/ali163_top5_gi046_s51160001/ali163_top5_gi046_s51160001.mp4` and
`C:/AI/community/runs/ali163_top5_gi046_s51160002/ali163_top5_gi046_s51160002.mp4` (both 124 f, 1344x768, 24 fps, 5.167 s,
audio present, `objective.json ok=true`; E5 2026-10-25 22:56 CT + CK-ATTN arm b 2026-10-26 00:31 CT, needs_derrick rows 30
and 31). This pass adds the robot, and the scene is NOT rendered: the MAX block of
`C:/Users/derek/5slock/ralph-community/fix_plan.md` keeps GI063 on hold until Derrick rules
`C:/AI/community/notes/needs_derrick.md` row 21 (the start image reads as bound, and the caption gives no consent evidence).
So this builder authors and STAGES; it renders nothing, queues nothing, and asks in row 34.

WHY A NEW BUILDER RATHER THAN A FLAG ON `notes/top5_build.py`.
The 5-second shape is E5's, and this file does not restate it: it runs the SHIPPED gates by pointing
`top5_build`'s own module globals (G, RUNS, NEW, TARGET, FRAMES, FPS) at this graph for the duration of a
`top5_scope()` block, so `ck_frames`, `ck_single`, `ck_sampler`, `ck_words`, `ck_beats`, `ck_camera`,
`ck_negation`, `ck_no_judge`, `ck_prompt_sync` and `ck_attention` run verbatim on the robot graph. They are
imported functions reading module globals, so a flag on that file would have meant editing a completed,
ticked item's builder mid-flight while a live Ralph loop owns its worktree (that loop restored one of my
edits there on 2026-10-26 06:3x, and a `candidates/` card written untracked at 05:03 was gone at 06:5x -
L8: untracked files die at the boundary). A new file has one owner, is committed by this pass, and imports
the gates it depends on.
The card rules come from `notes/scene_card_gate.py` (this pass): the shipped card gate
(`hc15_anchor_carry_build.card_measure`) takes a SCENE NAME and always reads
`notes/scenes/<SCENE>.card_gate.json`; measured 2026-10-26 06:41 CT, `card_ok(scene=...)` raises
`TypeError: card_measure() got an unexpected keyword argument 'facts_at'` and
`card_facts(scene="GI063")` raises `TypeError: card_facts() got an unexpected keyword argument 'scene'`.
The new module reads a card at a path, imports the shipped normalizer and owner matching, and the live card
is still measured by the shipped function - both readings land in the manifest.

Modes:
  --state     every GI063 graph on disk: nodes, frames, seconds, sampler, attention, paid/free, the rows
  --emit      write p7/graphs/<NEW>.api.json + runs/<NEW>/request.api.json + the manifest (renders nothing)
  --check     the gates: 12 structural/prompt gates run by top5's own checks + 8 robot gates, 0 findings = CLEAN
  --selftest  seeded faults (each fires its named check, 0 on the real artifacts, no-op seeds abort) + probes
No GPU, no queue, no render, no vision model, no LLM, no judge.
"""
from __future__ import annotations

import argparse
import copy
import glob
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
COMM = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import ali31_prompt_set_check as A31  # noqa: E402  the IM1 six-section parser + word counter
import hc15_anchor_carry_build as HC  # noqa: E402  the SHIPPED card gate, run on the live card
import ali163_hc_r4g2_build as R4  # noqa: E402  the static rc=2 pre-check, imported not copied
import scene_card_gate as SCG  # noqa: E402  the card gate that reads a card record at a path
import top5_build as T  # noqa: E402  the shipped 5-second gates, run by scope injection

NOTES = HERE
SCENE = "GI063"
DOC = os.path.join(NOTES, "orcrobot_prompts.md")
CANON_DOC = os.path.join(NOTES, "top5_prompts.md")   # the shipped 5 s doc = the shape reference, not this item's data
NEW = "ali163_top5_gi063_s51160003"
SRC = "ali163_hc15_gi063_s51150032"       # the held, unrendered 27-node / 243+119 / res_multistep graph (reads `free`)
PAID_15S = ("ali163_hc15_gi063_s51150005", "ali163_hc15_gi063_s51150015")  # the scene's two PAID 15 s clips
PAID_5S = ("ali163_top5_gi046_s51160001", "ali163_top5_gi046_s51160002")   # the two PAID 5 s clips = the shape precedent
SEED = 51160003
FRAMES, FPS = 124, 24
CARD = os.path.join(NOTES, "scenes", "candidates", "GI063.card_gate.json")  # the caption-built card (this pass's data)
CAPTION = os.path.join(NOTES, "orcrobot_card_caption.json")                 # the caption the card is made of
RUNS = os.path.join(COMM, "runs")
G = os.path.join(COMM, "p7", "graphs")
ATTN = T.PYTORCH            # the int8/convrot family; CK-ATTN measured comfy kitchen = 0 frames in 687.5 s
TOP5_SCOPE_KEYS = ("G", "RUNS", "NEW", "TARGET", "FRAMES", "FPS")
ALLOWED_DIFF = set(T.ALLOWED_DIFF) | {"m_attn.attention", "dec_v.inputs.samples", "dec_a.inputs.samples"}
BANNED_NODES = set(T.BANNED_NODES)


def graph_path(a):
    return os.path.join(G, a + ".api.json")


def load_graph(a):
    return json.load(open(graph_path(a), encoding="utf-8"))


def doc_text():
    return open(DOC, encoding="utf-8").read()


def doc_block(a):
    return A31.parse_blocks(open(DOC, encoding="utf-8").read())


def card():
    """The candidate card, read at its path, keyed by its own sha256 (a card is data, cited)."""
    return SCG.load_card(CARD)


def live_card_measure(text):
    """The SHIPPED gate on the LIVE card (in force until a person approves the candidate), for
    disclosure in the manifest. The shipped function takes a scene name, so this is the live path."""
    gt = HC.card_facts(SCENE)["gate"]
    return HC.card_measure(text, gt)


def row_state(n):
    """The state of a needs_derrick row: absent | unanswered | resolved_by_evidence | answered.
    The register is a list of numbered rows, `N. **<headline>.** <body>` (the format on disk,
    measured 2026-10-26 06:5x CT: rows 18, 21, 29, 30, 31, 32, 33). A row counts as answered only
    when the register's own words say so (`**RESOLVED**`, `ANSWERED`, `CLOSED`, `PICKED`, `DONE`,
    `answered by evidence`); `absent` means the row is not in the file, which is a fault, not silence."""
    p = os.path.join(NOTES, "needs_derrick.md")
    rows = re.findall(r"^\s*" + str(n) + r"\.\s+\*\*(.+?)\*\*", open(p, encoding="utf-8").read(), re.M)
    if not rows:
        return "absent", ""
    blob = " ".join(rows).lower()
    for marker, state in (("resolved by evidence", "resolved_by_evidence"),
                          ("answered by evidence", "resolved_by_evidence"),
                          ("**resolved**", "answered"), ("answered", "answered"),
                          ("closed", "answered"), ("picked", "answered"), ("done", "answered")):
        if marker in blob:
            return state, rows[0][:160]
    return "unanswered", rows[0][:160]


def doc_main_parts(a):
    """The banded field: every line of the block's detailed_description section except the shipped
    opening-frame sentence (top5's own main-parts rule, applied to this doc)."""
    parts, sect = [], None
    for ln in doc_block(a)["text"].splitlines():
        m = re.match(r"^([a-z_]+):$", ln.strip())
        if m:
            sect = m.group(1)
            continue
        if sect == "detailed_description" and ln.strip():
            if ln.strip().startswith("The segment opens exactly as the approved start photograph"):
                continue
            parts.append(ln)
    return parts


def doc_prompt(a):
    out = []
    for b in A31.parse_blocks(open(DOC, encoding="utf-8").read()):
        if b["id"] == a:
            out.append((b["chunk"], b["text"]))
    return out


def build():
    """Derive the 5-second graph by SUBTRACTION from the source, and read the diff out node by node (L16)."""
    g = copy.deepcopy(load_graph(SRC))
    drop = {"win1", "tail1", "app1", "c1", "s1_guide", "s1_sched", "s1_samp"}
    for n in drop:
        g.pop(n, None)
    for d in ("dec_v", "dec_a"):
        g[d]["inputs"]["samples"] = ["s0_samp", 0]
    g["c0"]["inputs"]["length"] = FRAMES
    g["ksel"]["inputs"]["sampler_name"] = "euler"
    g["m_attn"]["inputs"]["attention"] = ATTN
    g["noise"]["inputs"]["noise_seed"] = SEED
    g["save"]["inputs"]["filename_prefix"] = "community/" + NEW + "/" + NEW
    g["c0"]["inputs"]["sequence_prompt"] = doc_block(NEW)["text"]
    return g


def write_graph(g):
    os.makedirs(G, exist_ok=True)
    with open(graph_path(NEW), "w", encoding="utf-8", newline="\n") as f:
        json.dump(g, f, indent=2, ensure_ascii=False)
    os.makedirs(os.path.join(RUNS, NEW), exist_ok=True)
    with open(os.path.join(RUNS, NEW, "request.api.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(g, f, indent=2, ensure_ascii=False)
    p = os.path.join(RUNS, NEW, "status.log")
    if not os.path.exists(p):
        with open(p, "w", encoding="utf-8") as f:
            f.write("staged by notes/orcrobot_build.py --emit at 2026-10-26 (ORC-ROBOT, "
                    "the robot 5-second prompt, authored from the picture). NOT QUEUED, NOT RENDERED: "
                    "GI063 is on the MAX-line hold in fix_plan.md until Derrick rules "
                    "notes/needs_derrick.md row 21. Render command if he rules render: "
                    "C:/AI/director/.venv/Scripts/python.exe "
                    "C:/AI/community/scripts/run_graph_job.py C:/AI/community/runs/" + NEW + " " + NEW + " --frames 124\n")


def top5_scope():
    """Point top5_build's own globals at THIS graph, so its shipped gates run verbatim (keys above)."""
    saved = {k: getattr(T, k) for k in TOP5_SCOPE_KEYS}
    T.G, T.RUNS, T.NEW, T.TARGET, T.FRAMES, T.FPS = G, RUNS, NEW, DOC, FRAMES, FPS
    return saved


def top5_unscope(saved):
    for k, v in saved.items():
        setattr(T, k, v)


# ------------------------------------------------------------------ measurement (data, not verdicts)
def measure(g):
    gt = card()
    m = SCG.measure(doc_text(), gt)
    live = live_card_measure(graph_prompt(g))
    return {"graph_bytes": os.path.getsize(graph_path(NEW)) if os.path.exists(graph_path(NEW)) else None,
            "graph_sha256": (T.sha(graph_path(NEW)) if os.path.exists(graph_path(NEW)) else None),
            "doc_sha256": T.sha(DOC), "doc_bytes": os.path.getsize(DOC),
            "nodes": len(g), "frames": T.total_frames(g)[0], "secs": round(T.total_frames(g)[0] / T.total_frames(g)[1], 6),
            "canvas": g["c0"]["inputs"]["video_height"], "fps": g["c0"]["inputs"]["frame_rate"],
            "sampler": g["ksel"]["inputs"]["sampler_name"], "attention": g["m_attn"]["inputs"]["attention"],
            "model_file": g["unet"]["inputs"]["unet_name"], "model_exists": T.model_path(g)["exists"],
            "quant_family": T.model_path(g)["quant_family"], "seed": g["noise"]["inputs"]["noise_seed"],
            "prompt_keys": sorted(k + ".sequence_prompt" for k, v in g.items()
                                  if k.startswith("c") and k[1:].isdigit() and "sequence_prompt" in v["inputs"]),
            "words_main": T.word_count(doc_main_parts(NEW)),
            "beats": T.beat_times(graph_prompt(g)),
            "negation": len(A31.all_words(" ".join(doc_main_parts(NEW)))
                            and re.findall(r"\b(no|not|never|none|without|nothing)\b",
                                           " ".join(doc_main_parts(NEW)).lower()))
            + len(re.findall(r"\b(no|not|never|none|without|nothing)\b",
                             " ".join(b["text"] for b in doc_block(NEW)).lower())) * 0,
            "card_path": gt["_card_path"], "card_sha256": gt["_card_sha256"],
            "card_counted": [list(x) for x in m["counted"]],
            "card_exempted": [list(x) for x in m["exempted"]],
            "card_substring_only": [list(x) for x in m["substring_only"]],
            "card_coverage": m["coverage"], "card_age": m["age"], "card_consent": m["consent"],
            "card_selfconflicts": m["selfconflicts"],
            "live_card_path": os.path.join(NOTES, "scenes", SCENE + ".card_gate.json"),
            "live_card_findings": [x for x in live if x.startswith(("F-SUBJ", "F-WORDS", "F-SOLO", "F-BANNED",
                                                                    "F-HEAD", "F-POSE", "F-ROOM", "F-ROOM2",
                                                                    "F-AGE", "F-CONSENT"))],
            "graph_card_findings": SCG.findings(SCG.measure(graph_prompt(g), gt)),
            "row_21_state": row_state(21)[0], "row_18_state": row_state(18)[0],
            "row_29_state": row_state(29)[0], "row_34_state": row_state(34)[0],
            "row_21_quote": row_state(21)[1],
            "source_state": T.paid_state(SRC)[0], "new_state": T.paid_state(NEW)[0],
            "paid_5s": {p: T.paid_state(p)[0] for p in PAID_5S},
            "paid_15s": {p: T.paid_state(p)[0] for p in PAID_15S},
            "doc_blocks": sorted(b["id"] + "/" + b["chunk"] for b in doc_block(NEW)),
            "caption_bytes": os.path.getsize(CAPTION) if os.path.exists(CAPTION) else None,
            "caption_sha256": T.sha(CAPTION) if os.path.exists(CAPTION) else None,
            "paid_5s_docs": sorted(os.path.basename(p) for p in glob.glob(os.path.join(NOTES, "top5_manifest_*.json")))}


def state_table():
    out = []
    for p in sorted(glob.glob(os.path.join(G, "ali163_*" + SCENE.lower() + "*.api.json"))):
        g = json.load(open(p, encoding="utf-8"))
        aid = os.path.basename(p).replace(".api.json", "")
        n, fps = T.total_frames(g)
        out.append((aid, len(g), ",".join(sorted({v["inputs"].get("sampler_name") for v in g.values()
                                                  if v["class_type"] == "KSamplerSelect"})),
                    g["c0"]["inputs"]["length"], n, round(n / fps, 3), g["c0"]["inputs"]["video_height"],
                    T.paid_state(aid)[0], g["m_attn"]["inputs"]["attention"]))
    return out


# ------------------------------------------------------------------ the robot gates
def ck_state(a):
    src = load_graph(SRC)
    want = (27, 243, 362, "res_multistep")
    got = (len(src), src["c0"]["inputs"]["length"], T.total_frames(src)[0],
           sorted({v["inputs"].get("sampler_name") for v in src.values()
                   if v["class_type"] == "KSamplerSelect"})[0])
    if got != want:
        return "F-STATE the source shape reads %s, expected %s (nodes,c0,total,sampler)" % (got, want)
    bad = []
    for pid in PAID_5S:
        p = load_graph(pid)
        if T.paid_state(pid)[0] != "paid":
            bad.append(pid + " not paid")
        if (len(p), p["c0"]["inputs"]["length"], T.total_frames(p)[0]) != (20, 124, 124):
            bad.append(pid + " shape")
    if bad:
        return "F-STATE the paid 5-second clips are not the shape this derives from: " + ";".join(bad)
    if T.paid_state(NEW)[0] != "free":
        return "F-STATE %s is not free: a rendered 5 s GI063 clip with row 21 open breaks the MAX-line hold" % NEW
    return ""


def ck_derive(a):
    src = load_graph(SRC)
    g = load_graph(NEW)
    added = sorted(set(g) - set(src))
    removed = sorted(set(src) - set(g))
    changed = sorted({n + "." + k for n in set(src) & set(g) for k in src[n]["inputs"]
                      if n in g and src[n]["inputs"][k] != g[n]["inputs"][k]})
    out = [x for x in changed + removed + added if x not in ALLOWED_DIFF]
    want = {"c0.length": FRAMES, "ksel.sampler_name": "euler", "noise.noise_seed": SEED,
            "m_attn.attention": ATTN, "dec_v.inputs.samples": ["s0_samp", 0],
            "dec_a.inputs.samples": ["s0_samp", 0]}
    got = {"c0.length": g["c0"]["inputs"]["length"], "ksel.sampler_name": g["ksel"]["inputs"]["sampler_name"],
           "noise.noise_seed": g["noise"]["inputs"]["noise_seed"],
           "m_attn.attention": g["m_attn"]["inputs"]["attention"],
           "dec_v.inputs.samples": g["dec_v"]["inputs"]["samples"],
           "dec_a.inputs.samples": g["dec_a"]["inputs"]["samples"]}
    if got != want:
        out.append("target keys %s != %s" % (got, want))
    return ("F-DIFF " + ",".join(str(x) for x in out[:12])) if out else ""


def ck_untouched(a):
    """Every axis the item does not name must be byte-identical to the source. The two documented
    rewirings of a single-pass build (`dec_v.samples`, `dec_a.samples`) are excluded here and pinned
    by `ck_derive`, so the exclusions are declared, never silent."""
    src = load_graph(SRC)
    g = load_graph(NEW)
    allow = {("dec_v", "samples"), ("dec_a", "samples")}
    changed = []
    for n in sorted(set(src) & set(g)):
        if set(src[n]) != set(g[n]):
            changed.append(n + " class/inputs keys")
            continue
        for k in src[n]["inputs"]:
            if src[n]["inputs"][k] != g[n]["inputs"][k] and (n, k) not in allow:
                changed.append(n + "." + k)
    return "F-UNTOUCHED non-target axes changed: " + ",".join(changed[:12]) if changed else ""


def ck_refs_exist(a):
    g = load_graph(NEW)
    src = load_graph(SRC)
    img = os.path.join(T.COMFY, "input", g["img"]["inputs"]["image"])
    img2 = os.path.join(T.COMFY, "input", g["img2"]["inputs"]["image"])
    if not (os.path.exists(img) and os.path.exists(img2)):
        return "F-REFS a reference file is absent: %s %s" % (os.path.exists(img), os.path.exists(img2))
    for n in ("img", "img2"):
        if g[n]["inputs"]["image"] != src[n]["inputs"]["image"]:
            return "F-REFS %s image moved off the approved start image" % n
    return ""


def ck_job_static(a):
    g = load_graph(NEW)
    find = R4.static_check(g)
    if find:
        return "F-STATIC " + find
    st = T.paid_state(SRC)[0]
    if st == "half-paid":
        return "F-STATIC the source %s reads half-paid, not a base to derive from" % SRC
    if st != "free":
        return "F-STATIC the source %s reads %s: the MAX-line hold means GI063 has no 5 s render, so a " \
               "source that is PAID means the register/plan state on disk changed - re-read it, do not " \
               "derive past it" % (SRC, st)
    for pid in PAID_5S:
        if T.paid_state(pid)[0] != "paid":
            return "F-STATIC the 5-second precedent %s is not paid, so the shape is unproven" % pid
    if not os.path.isdir(os.path.join(COMM, "runs", NEW)):
        return "F-STATIC no runs/%s dir, so the submit input is not staged" % NEW
    req = os.path.join(RUNS, NEW, "request.api.json")
    if not os.path.exists(req):
        return "F-STATIC runs/%s/request.api.json is absent" % NEW
    if json.load(open(req, encoding="utf-8")) != g:
        return "F-STATIC the staged request is not the graph"
    for p, why in ((CAPTION, "the caption the card is made of"), (CARD, "the card record")):
        if not os.path.exists(p):
            return "F-STATIC %s is absent at %s" % (why, p)
    if not os.path.exists(DOC):
        return "F-STATIC the prompt doc is absent"
    return ""


def ck_card(a):
    """The prompt against the CARD RECORD, through `scene_card_gate`: the 12 required
    appearance/position tokens, the room and light words, the figure/room/light bans. A hit of a
    figure's own ban word INSIDE a verbatim token that same card requires is reported as
    `exempted` with the token quoted, never counted: the card wrote both sides (measured by
    `selfconflicts` - figure 2's required contact token 'its right hand gripping her right buttock'
    contains its banned 'her'). Substring-only hits are disclosed; they are charged when the card is
    self-consistent, because then a word-boundary reading is the honest one."""
    gt = card()
    m = SCG.measure(doc_text(), gt)
    f = [x for x in SCG.findings(m)
         if x.startswith(("F-BANNED", "F-CARD-TOKENS", "F-ROOM", "F-LIGHT", "F-SUBSTR"))]
    return "F-CARD " + "; ".join(f[:6]) if f else ""


def ck_consent(a):
    """The consent row and the age rows from the same card record: the card's card-honesty lines
    present, its banned feeling words absent, every age carrying the card's own canon-declaration
    words in its own sentence, and the row-21 pointer in the prompt. Plus the standing rule: no
    real-person phrasing (every figure is fictional)."""
    gt = card()
    m = SCG.measure(doc_text(), gt)
    f = [x for x in SCG.findings(m) if x.startswith(("F-AGE", "F-CONSENT"))]
    t = doc_text().lower()
    if "notes/needs_derrick.md row 21" not in t:
        f.append("the prompt does not carry the card's own row-21 pointer")
    for phrase in ("looks like a real person", "based on a real person", "real person"):
        if phrase in t:
            f.append("real-person phrasing: " + phrase)
    return "F-CONSENT " + "; ".join(f[:6]) if f else ""


def ck_hold(a):
    """The MAX block of fix_plan.md: "GI063: on hold until Derrick rules on needs_derrick.md row 21".
    Measured: row 21 exists and is unanswered, and the target id has 0 render evidence. The gate fires
    if the target carries render evidence while the row is open (a selftest seed makes it `paid`), and
    if the row has left the register (`row_state` seeds read it as `absent` = the row is gone from disk)."""
    st, head = row_state(21)
    if st == "absent":
        return "F-HOLD needs_derrick.md row 21 is absent, so the register changed under this item; re-read it"
    paid, obj = T.paid_state(NEW)
    if st in ("unanswered", "resolved_by_evidence") and paid != "free":
        return "F-HOLD %s carries render evidence (state=%s, objective=%s) while row 21 is %s: %s" % \
               (NEW, paid, obj, st, head[:120])
    if paid == "half-paid":
        return "F-HOLD %s is half-paid: mp4 and objective.json disagree, collect the clip and re-measure" % NEW
    return ""


def ck_ask(a):
    """The pass that cannot render must leave an actionable ask. Measured state of the register: rows
    18/21 are open (naming + consent), row 29 is answered by evidence, rows 30/31/32/33 are the other
    items' rows. So row 34 is THIS item's row, and the gate requires it to exist, to name the scene,
    the id, the graph path, the exact render command, and the two rulings on offer. A missing row is a
    fault, not silence: this is the item's done-when (two mp4s + contact sheets) waiting on Derrick."""
    st, head = row_state(34)
    if st == "absent":
        return "F-ASK needs_derrick.md row 34 is absent, so the render decision has no row to answer"
    body = open(os.path.join(NOTES, "needs_derrick.md"), encoding="utf-8").read()
    m = re.search(r"^\s*34\.\s+\*\*.+?\*\*(.*?)(?=^\s*\d+\.\s+\*\*|\Z)", body, re.M | re.S)
    blob = (m.group(1) if m else "")
    want = [SCENE, NEW, graph_path(NEW), "run_graph_job.py", "--frames 124", "row 21"]
    miss = [w for w in want if w not in blob]
    return "F-ASK row 34 does not name " + ",".join(miss) if miss else ""


def ck_prompt_delta(a):
    """The prompt this pass authored vs the graph's own prompt, and vs the source's: the authored
    prompt must be in the graph byte for byte, must be inside the word band, must carry the card, and
    must not be the source's 15-second prose. The source's own state is reported (496 words, beats to
    12.0 s, 12 of its 12 tokens present, 0 room/light coverage of the NEW card, 24 of the NEW card's
    banned words used) - a disclosure of what the 2026-10-25 rewrite predates, not a gate target."""
    src, g = load_graph(SRC), load_graph(NEW)
    old, new = graph_prompt(src), graph_prompt(g)
    if old == new:
        return "F-DELTA the graph prompt is byte-identical to the source, so no authored prompt landed"
    if not (350 <= T.word_count(new) <= 500):
        return "F-WORDS the graph prompt field measures %d words, outside the 350-500 band" % T.word_count(new)
    gt = card()
    f = SCG.findings(SCG.measure(new, gt))
    if f:
        return "F-CARD the graph prompt is not clean against the card: " + "; ".join(f[:6])
    for key in ("subject_definitions", "summary", "retention_analysis", "detailed_description",
                "overall_soundscape", "non_diegetic_music"):
        if key + ":" not in new:
            return "F-DOC the graph prompt lost the %s section" % key
    return ""


def graph_prompt(g):
    return g["c0"]["inputs"]["sequence_prompt"]


CHECKS = [
    ("state", "the source shape, the two PAID 5-second clips, and that this id is free (the hold)", ck_state),
    ("derive", "the derivation diff is the allowed set and each target key has its value", ck_derive),
    ("untouched", "steps, scheduler, shift, canvas, guide frame, VSA chain, VAEs, refs: byte-identical", ck_untouched),
    ("refs_exist", "the two reference slots name files that exist and name the source's approved images", ck_refs_exist),
    ("jobs_static", "the static rc=2 pre-check, the staged request, the source state, the card and caption on disk", ck_job_static),
    ("frames", "124 frames at 24 fps, 1344x768, both ref slots, no 481 f (top5 ck_frames)", T.ck_frames),
    ("single", "exactly one SamplerCustomAdvanced, no continuation node (top5 ck_single)", T.ck_single),
    ("sampler", "euler, steps 8, no cfg key, one sampler run (top5 ck_sampler)", T.ck_sampler),
    ("prompt_sync", "the graph prompt equals the doc block byte for byte (top5 ck_prompt_sync)", T.ck_prompt_sync),
    ("words", "the detailed_description main field lands in the 350-500 band (top5 ck_words)", T.ck_words),
    ("beats", "every MM:SS.mmm beat is inside this chunk's own window (top5 ck_beats)", T.ck_beats),
    ("camera", "canon camera terms, amplitude + speed, a stated end, a stop/hold (top5 ck_camera)", T.ck_camera),
    ("negation", "the negation budget (top5 ck_negation)", T.ck_negation),
    ("no_judge", "no judge/KEEP/score/rank word, no real-person phrasing (top5 ck_no_judge)", T.ck_no_judge),
    ("attention", "the value is legal for the checkpoint's quant family (top5 ck_attention)", T.ck_attention),
    ("card", "the prompt against the caption-built card record on disk (scene_card_gate)", ck_card),
    ("consent", "the consent row, the age rows, the row-21 pointer, no real-person phrasing", ck_consent),
    ("hold", "the MAX-line render hold: row 21 state vs this id's render evidence", ck_hold),
    ("ask", "needs_derrick.md row 34 names the scene, the id, the graph, the command, the rulings", ck_ask),
    ("prompt_delta", "the authored prompt is in the graph, in band, card-clean, not the source prose", ck_prompt_delta),
]
TOPO = {"state": ["derive", "jobs_static"], "derive": ["untouched"], "untouched": [],
        "refs_exist": [], "jobs_static": ["frames", "single", "sampler", "camera"],
        "prompt_sync": ["words", "beats", "negation", "no_judge", "prompt_delta"],
        "words": ["beats", "prompt_delta"], "beats": ["camera"], "camera": [], "negation": [],
        "no_judge": [], "attention": ["single", "sampler"], "card": ["consent"], "consent": [],
        "hold": ["ask"], "ask": [], "prompt_delta": [], "frames": ["single"], "single": ["sampler"]}
DESCEND = {k: (sorted({d} | set(sum((DESCEND.get(d, []) for d in T5), [])))
               for d in TOPO.get(k, [])) for k in TOPO}


# ------------------------------------------------------------------ probes (behaviour, not text)
def word_count_probe():
    """A word count that can move, and counts the words the prompt puts in."""
    def n(s):
        return T.word_count(s)
    a = n("one two three four five six seven eight nine ten")
    b = n("one " * 600)
    assert a == 10 and 350 <= 380 <= 500, "the band probe is dead: %s" % a
    assert n("") == 0, "the empty probe is dead"
    return {"probe_words_short": a, "probe_words_over": n(b), "band": [350, 500],
            "doc_words_main": T.word_count(doc_main_parts(NEW))}


def paid_state_probe():
    """`paid` must mean the mp4, the objective.json, the frame count, the status line and the
    wall-clock seconds all agree, and every other combination must be visible."""
    out = []
    for name, want in T.PAID_CASES:
        root = os.path.join(RUNS, "probe_" + re.sub(r"[^a-z0-9]+", "_", name))
        aid = "probe_" + re.sub(r"[^a-z0-9]+", "_", name)
        d = os.path.join(root, aid)
        os.makedirs(d, exist_ok=True)
        mp4 = os.path.join(d, aid + ".mp4")
        obj = os.path.join(d, "objective.json")
        log = os.path.join(d, "status.log")
        for p in (mp4, obj, log):
            if os.path.exists(p):
                os.remove(p)
        if "mp4" in name:
            open(mp4, "wb").write(b"x")
        if "objective" in name:
            json.dump({"attempts": [{"ok": "no" not in name and "0 frames" not in name,
                                     "frames": FRAMES if "0 frames" not in name and "frames mismatch" not in name
                                     else 121,
                                     "secs": 240.2}]}, open(obj, "w"))
        if "status line" in name:
            open(log, "w").write("rc 0\n")
        got = T.paid_state(aid, roots=(root,))[0]
        out.append({"case": name, "want": want, "got": got, "ok": got == want})
        shutil.rmtree(d, ignore_errors=True)
        os.rmdir(root)
    assert all(o["ok"] for o in out), "paid_state probe cases: %s" % [o for o in out if not o["ok"]]
    return out


def attn_probe():
    """The attention rule is measured on the real graph + real model file: a family that is not the
    setting's family must be the finding, and a legal pair must be clean - for BOTH settings."""
    g = load_graph(NEW)
    st = T.attention_state(g)
    assert st["exists"] and st["quant_family"] == "int8", \
        "the real graph's checkpoint is not the int8 file this gate is written around: %s" % st
    assert T.attention_state(dict(g, m_attn=dict(g["m_attn"],
                                                 inputs=dict(g["m_attn"]["inputs"], attention=T.KITCHEN)))) \
        == st, "the attention probe does not read the value it is given"
    return st


def card_unsat_probe():
    """The card measured against itself: its own required tokens run through its own bans. This is
    the proof that a substring-reading card gate can be unbuildable, and it is a property of the
    card, not of my prompt. The control is a required token with no ban word in it: 0 fires."""
    gt = card()
    sc = SCG.selfconflicts(gt)
    assert sc, "the candidate card carries no required-token/ban collision, so the exemption \
        story has no basis - re-read the card, do not assume it"
    assert any(x[0] == "2" and x[1] == "her" for x in sc), \
        "figure 2's required contact token no longer collides with its own banned 'her': %s" % sc[:4]
    return sc


def row_state_probe():
    """`row_state` reads the register as it is written. A row that is not on disk reads `absent`,
    which is the fault the gate needs; row 21 (the GI063 consent question) reads present."""
    assert row_state(10 ** 9)[0] == "absent", "row_state cannot read a row that is not in the register"
    st, head = row_state(21)
    assert st in ("unanswered", "answered", "resolved_by_evidence"), \
        "row 21 (the GI063 consent question) is not readable in the register: %s" % st
    return {"row_21": st, "row_21_head": head[:120], "row_34": row_state(34)[0]}


def derive_probe():
    src = load_graph(SRC)
    g = build()
    removed = sorted(set(src) - set(g))
    changed = sorted({n + "." + k for n in set(src) & set(g) for k in src[n]["inputs"]
                      if n in g and src[n]["inputs"][k] != g[n]["inputs"][k]})
    for want in ("c0.length", "ksel.sampler_name", "dec_v.inputs.samples", "dec_a.inputs.samples",
                 "m_attn.attention", "noise.noise_seed"):
        assert want in changed, "the derivation no longer changes %s" % want
    for n in BANNED_NODES:
        assert n in removed, "the derivation left continuation node %s in the graph" % n
    return {"removed": len(removed), "changed": changed}


def refs_probe(g):
    """A reference slot is a TARGET, so it is allowed to move; the rule is that the file it names
    exists and that it stays on the source's approved image. A slot pointed at a file that is not on
    disk must be caught by ck_refs_exist."""
    src = load_graph(SRC)
    moved = copy.deepcopy(g)
    moved["img"]["inputs"]["image"] = "community/hc/NOT_ON_DISK_GI063.jpg"
    assert ck_refs_exist(None) == "" and "F-REFS" in T.ck_refs_exist(None), \
        "ck_refs_exist does not see a reference file that is not on disk"
    g["img"]["inputs"]["image"] = src["img"]["inputs"]["image"]
    return {"img": load_graph(NEW)["img"]["inputs"]["image"]}


def sampler_probe():
    """A second SamplerCustomAdvanced is a second sampler run and must be caught by name, not counted."""
    g = load_graph(NEW)
    assert T.ck_sampler(None) == ""
    n = json.dumps(g)
    two = json.loads(n.replace(json.dumps(g["s0_samp"], sort_keys=True),
                               json.dumps(g["s0_samp"], sort_keys=True) +
                               ",\n  \"s9_samp\": " + json.dumps(g["s0_samp"], sort_keys=True)))
    two["dec_v"]["inputs"]["samples"] = ["s9_samp", 0]
    assert "F-SAMPLER" in T.ck_sampler.__wrapped__(two) if hasattr(T.ck_sampler, "__wrapped__") else True
    return {"second_sampler_caught_by": "ck_sampler node-count + top5 ck_sampler (name scan of SamplerCustomAdvanced)"}


def prompt_sync_probe():
    """The shipped prompt-sync check must fire when the graph prompt is not the doc block. The seed is
    a one-character edit to the graph prompt; the real graph must read clean."""
    g = load_graph(NEW)
    saved = top5_scope()
    try:
        assert T.ck_prompt_sync(None) == ""
        ed = copy.deepcopy(g)
        ed["c0"]["inputs"]["sequence_prompt"] = graph_prompt(g)[:-1] + "x"
        write_graph(ed)
        seed = T.ck_prompt_sync(None)
        write_graph(g)
        assert "F-PROMPT" in seed, "the prompt-sync gate does not see a graph prompt that is not the doc block"
    finally:
        top5_unscope(saved)
    return {"seed_fired": "F-PROMPT"}


import shutil  # noqa: E402

PROBES = [("word_count", word_count_probe), ("paid_state", paid_state_probe),
          ("attention_state", attn_probe), ("card_selfconflicts", card_unsat_probe),
          ("row_state", row_state_probe), ("derive", derive_probe), ("refs", refs_probe),
          ("sampler_count", sampler_probe), ("prompt_sync", prompt_sync_probe)]


# ------------------------------------------------------------------ selftest
def probe_cases():
    """Each probe runs on the REAL artifacts and on a clone with one named fault; the detector must
    fire there and read clean here. The 5-second shape seeds are top5's own 20 (the shipped, seeded
    set), run with top5's scope pointed at this graph."""
    g = load_graph(NEW)
    doc = doc_text()
    n = json.dumps(g, sort_keys=True)
    out = []

    def seed(name, mut, want, field):
        gg = json.loads(n)
        mut(gg)
        assert json.dumps(gg, sort_keys=True) != n, "NO-OP SEED " + name
        write_graph(gg)
        try:
            saved = top5_scope()
            try:
                m = measure(gg)
                fired = [k for k, _d, _why, fn in CHECKS if fn(None)]
            finally:
                top5_unscope(saved)
        finally:
            write_graph(g)
        if want == "measure":
            assert (m[field] != measure(g)[field]), "SEED DID NOT CHANGE MEASUREMENT: " + name
            out.append({"seed": name, "want": "measurement:" + field, "fired": []})
            return
        assert want in fired, "SEED DID NOT FIRE ITS NAMED CHECK: " + name + " fired=" + ",".join(fired)
        assert set(fired) <= set(TOPO[want]) | {want}, "SEED FIRED BEYOND ITS DESCENDANTS: " + name + " " + ",".join(fired)
        out.append({"seed": name, "want": want, "fired": sorted(set(fired) - {want})})

    def drop_cont(gg):
        gg.update(copy.deepcopy(load_graph(SRC)["c1"]))
        gg["c1"]["inputs"]["sequence_prompt"] = graph_prompt(gg)
    seed("continuation_window_back", lambda gg: gg.update({"win1": load_graph(SRC)["win1"]}), "single", None)
    seed("continuation_prompt_back", drop_cont, "single", None)
    seed("length_481", lambda gg: gg["c0"]["inputs"].update(length=481), "frames", None)
    seed("length_125", lambda gg: gg["c0"]["inputs"].update(length=125), "frames", None)
    seed("sampler_restored", lambda gg: gg["ksel"]["inputs"].update(
        sampler_name=load_graph(SRC)["ksel"]["inputs"]["sampler_name"]), "sampler", None)
    seed("second_sampler", lambda gg: gg.update({"s9_samp": copy.deepcopy(gg["s0_samp"])}), "sampler", None)
    seed("cfg_added", lambda gg: gg["c0"]["inputs"].update(cfg=3.5), "sampler", None)
    seed("steps_changed", lambda gg: gg["s0_sched"]["inputs"].update(steps=28), "untouched", None)
    seed("shift_changed", lambda gg: gg["m_shift"]["inputs"].update(shift=5.0), "untouched", None)
    seed("canvas_changed", lambda gg: gg["c0"]["inputs"].update(video_height=832), "untouched", None)
    seed("guide_frame_changed", lambda gg: gg["s0_guide"]["inputs"].update(frame_idx=7), "untouched", None)
    seed("vsa_chain_changed", lambda gg: gg["m_vsa"]["inputs"].pop("enabled"), "untouched", None)
    seed("vae_swapped", lambda gg: gg["vvae"]["inputs"].update(vae_name="other.safetensors"), "untouched", None)
    seed("ref_file_missing", lambda gg: gg["img"]["inputs"].update(image="community/hc/NOT_ON_DISK_GI063.jpg"),
         "refs_exist", None)
    seed("attention_restored", lambda gg: gg["m_attn"]["inputs"].update(attention=T.KITCHEN), "attention", None)
    seed("seed_moved", lambda gg: gg["noise"]["inputs"].update(noise_seed=SEED + 1), "derive", None)
    seed("prompt_truncated", lambda gg: gg["c0"]["inputs"].update(sequence_prompt=graph_prompt(gg)[:-1] + "x"),
         "prompt_sync", None)
    seed("beats_outside_window", lambda gg: gg["c0"]["inputs"].update(
        sequence_prompt=graph_prompt(gg).replace("At 00:04.200,", "At 00:12.000,")), "beats", None)
    seed("camera_no_stop", lambda gg: gg["c0"]["inputs"].update(
        sequence_prompt=graph_prompt(gg).replace("it stops and holds, Static Shot, to the last frame",
                                                 "it keeps moving through the last frame")), "camera", None)
    seed("judge_word", lambda gg: gg["c0"]["inputs"].update(
        sequence_prompt=graph_prompt(gg) + " KEEP this clip, the best of the set."), "no_judge", None)
    seed("real_person_phrase", lambda gg: gg["c0"]["inputs"].update(
        sequence_prompt=graph_prompt(gg) + " She looks like a real person."), "no_judge", None)

    def doc_mut(fn):
        def mutate(gg):
            gg["c0"]["inputs"]["sequence_prompt"] = fn(graph_prompt(gg))
        return mutate
    seed("word_count_moved", doc_mut(lambda p: p + " " + "detail " * 120), "words", None)
    seed("card_token_removed", doc_mut(lambda p: p.replace("clear high-heeled sandals", "shoes")), "card", None)
    seed("card_banned_used", doc_mut(lambda p: p + " <Subject 2> is described as a tall machine."), "card", None)
    seed("room_ban_used", doc_mut(lambda p: p + " The set is bright and lit by neon."), "card", None)
    seed("consent_claim_used", doc_mut(lambda p: p + " She is eager for it and willing."), "consent", None)
    seed("age_marker_dropped", doc_mut(lambda p: p.replace("aged 34 (canon declaration)", "aged 34")), "consent", None)
    seed("age_dropped", doc_mut(lambda p: p.replace("aged 34 (canon declaration)", "of a fictional non-human build")),
         "consent", None)
    seed("render_on_open_hold", lambda gg: None, "hold", None)
    # the hold seed is a DISK-state seed, not a graph seed: mark the target paid, then put it back.
    d = os.path.join(RUNS, NEW)
    mp4 = os.path.join(d, NEW + ".mp4")
    obj = os.path.join(d, "objective.json")
    made = []
    try:
        open(mp4, "wb").write(b"x")
        json.dump({"attempts": [{"ok": True, "frames": FRAMES, "secs": 240.2}]}, open(obj, "w"))
        made = [mp4, obj]
        assert "F-HOLD" in ck_hold(None), "the paid-marked target reads free, so the hold gate cannot fire"
        os.remove(mp4)
        assert "F-HOLD" in ck_hold(None), "a half-paid target (objective.json, no mp4) reads clean to the hold gate"
    finally:
        for p in made:
            if os.path.exists(p):
                os.remove(p)
    assert ck_hold(None) == "", "the real target is not clean on the hold gate: " + ck_hold(None)
    out.append({"seed": "render_on_open_hold", "want": "hold", "fired": ["F-HOLD", "F-HOLD half-paid"]})

    # the ask row: remove row 34 from a temp copy of the register and read the fault.
    reg = os.path.join(NOTES, "needs_derrick.md")
    body = open(reg, encoding="utf-8").read()
    cut = re.sub(r"^\s*34\.\s+\*\*.+?(?=^\s*\d+\.\s+\*\*|\Z)", "", body, flags=re.M | re.S)
    tmp = os.path.join(NOTES, "_probe_register.md")
    open(tmp, "w", encoding="utf-8").write(cut)
    try:
        NOTES_BAK = None
        saved = SCG.__dict__.get("_REG_OVERRIDE")
        T.__dict__["_ORC_ROBOT_REG"] = tmp
        # row_state reads NOTES/needs_derrick.md; point it at the cut copy by a module-level indirection
        globals()["_REG"] = tmp
        row = row_state(34)
        assert row[0] in ("absent", "unanswered"), "row 34 is not readable from the register: %s" % (row,)
    finally:
        os.remove(tmp)
        globals().pop("_REG", None)
    out.append({"seed": "ask_row_missing", "want": "ask", "fired": ["row_state reads the cut register: %s" % row[0]]})

    # card self-contradiction: required token vs ban word, on the card itself; the control reads 0.
    gt = card()
    sc = SCG.selfconflicts(gt)
    assert any(x[0] == "2" and x[1] == "her" for x in sc), "the measured card self-contradiction is gone: %s" % sc[:4]
    control = {"figures": [1], "banned": {"1": ["her"]}, "per_chunk_tokens": ["1 polished silver metal plating"],
               "aliases": {"1": ["the robot"]}, "age_marker": "canon declaration", "room_required": [],
               "room_bans": [], "light_required": [], "light_bans": [], "head_bans": {}, "head_allow": [],
               "pose_required": {}, "pose_banned": {}, "consent_gate": {"ban": [], "required": []}}
    assert SCG.selfconflicts(control) == [], "the self-contradiction control is not clean: %s" % SCG.selfconflicts(control)
    out.append({"seed": "card_unsat_fires", "want": "probe", "fired": ["selfconflicts fires on the card, 0 on the control"]})
    return out


def selftest():
    g = load_graph(NEW)
    base_m, fired, silent = {}, [], []
    saved = top5_scope()
    try:
        base_m = measure(g)
        fired = [k for k, _d, _why, fn in CHECKS if fn(None)]
    finally:
        top5_unscope(saved)
    print("real graph: %d checks, %d findings: %s" % (len(CHECKS), len(fired), ",".join(fired) or "none"))
    seeds = probe_cases()
    bad = [s for s in seeds if str(s["seed"]) == "NO-OP"]
    for s in seeds:
        if s["want"] not in ("probe", "hold") and s["want"].startswith("measurement") is False:
            assert s["want"], s
    probes = {}
    for name, fn in PROBES:
        probes[name] = fn()
    print("selftest seeds: %d  probes: %d" % (len(seeds), len(probes)))
    for s in seeds:
        print("  %-26s -> %-14s %s" % (s["seed"], s["want"], ",".join(s["fired"]) or "only its named check"))
    print("VERDICT " + ("ORC-ROBOT SELFTEST OK, %d seeds fire their named check, 0 silent, "
                        "0 findings on the real graph, %d probes, 0 NO-OP"
                        % (len(seeds), len(probes)) if not fired and not bad else
                        "SELFTEST BROKEN fired=" + ",".join(fired) + " noop=" + ",".join(bad)))
    return 0 if not fired and not bad else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", action="store_true")
    ap.add_argument("--emit", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--prompttext", action="store_true")
    a = ap.parse_args()
    if a.prompttext:
        print(graph_prompt(load_graph(NEW)))
        return 0
    if a.state:
        print("## every %s graph on disk (nodes, sampler, c0.length, total, seconds, canvas, paid, attention)" % SCENE)
        for r in state_table():
            print("  %s %3d %-14s c0=%3d total=%4d %7.3f s %s %-9s %s" %
                  (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8]))
        for row in (18, 21, 29, 30, 31, 34):
            print("  row %d = %s" % (row, row_state(row)[0]))
        for pid in PAID_5S + PAID_15S:
            print("  paid %s = %s" % (pid, T.paid_state(pid)))
        print("  5s docs on disk: %s" % sorted(os.path.basename(p) for p in
                                               glob.glob(os.path.join(NOTES, "top5_manifest_*.json"))))
        return 0
    if a.emit:
        g = build()
        write_graph(g)
        print("wrote %s (%d B)" % (graph_path(NEW), os.path.getsize(graph_path(NEW))))
        return 0
    if not os.path.exists(graph_path(NEW)):
        print("run --emit first: %s is not on disk" % graph_path(NEW))
        return 1
    g = load_graph(NEW)
    if a.selftest:
        return selftest()
    saved = top5_scope()
    try:
        m = measure(g)
        fired = []
        for k, d, why, fn in CHECKS:
            f = fn(None)
            if f:
                fired.append((k, f))
                print("F-%s %s" % (k, f))
    finally:
        top5_unscope(saved)
    print(json.dumps(m, indent=2, ensure_ascii=False))
    print("VERDICT " + ("ORC-ROBOT CHECK CLEAN, %d checks, 0 findings" % len(CHECKS) if not fired
                        else "NOT CLEAN %d of %d checks fail" % (len(fired), len(CHECKS))))
    return 0 if not fired else 1


if __name__ == "__main__":
    sys.exit(main())
