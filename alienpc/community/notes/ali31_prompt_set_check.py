#!/usr/bin/env python
"""ali31_prompt_set_check.py - fix_plan 3.1 (PQ1): audit the IM1 prompt set against the community guide.

notes/prompt_guide_20261024.md rule 4 is "Move negation out of prose" (the official MiniMax guides use no
prohibition wording; the community route for negation is a NegPip token-weight node). The 12 verbatim prompts
in notes/im1_prompts.md were written under that guide and measured 28 prohibition tokens in them (15 "no",
8 "not", 5 "without"), so the set did not follow its own rule. notes/ali31_prompt_negation_pass.py rewrote
those 28 sites into positive phrasing; this gate is the standing check, and it checks the whole guide, not
just the fix:

  COVERAGE    12 blocks = the six r1i..r6i pool runs x c0/c1, one each, seed == the id suffix
  SECTIONS    official section set and order (c0 detailed_description, c1 integrated_multimodal_description)
  WORDS       main field in band: c0 350-500 words, c1 350-550 words (the c1 band is the measured 430-501)
  BEATS       >=3 "At MM:SS.mmm" beats; c0 beats inside 00:00-00:05, c1 beats inside 00:05-00:10 (5s chunks)
  CAMERA      >=1 canon camera term, with amplitude and speed words (the 2026-10-23 finding)
  CONTINUE    c1 summary starts "[video continuation + reference generation]" and cites <Video 1>
  NEGATION    ZERO prohibition tokens in every section of every block (the 3.1 fix; the guide's rule 4)
  ADULTS      scripts/comm.py guard_ok() is True for EVERY section of every block, and every block states a
              fictional adult age >= 21 (the content lock floor)
  CANVAS      the canvas the doc header claims == the canvas of the baseline graph on disk, multiple of 32
  SYNC        the staged p7 graph carries the doc text byte-for-byte, and differs from the rendered baseline
              graph on prompt + filename_prefix ONLY (the 2.1b one-variable rule survives the rewrite)
  GUIDE_CITES every saved page the guide's source table names exists in notes/web, and the byte sizes it
              states equal the files on disk (a cited page that is not on disk is not evidence)
  KEEPWORD    the manifest carries no verdict word: KEEP is Derrick's alone
  NO_GPU      this gate's own source opens no network port (AGENTS.md hard line)

No GPU, no queue, no request: this file reads text and json and writes notes/ali31_prompt_set_manifest.json.

Reproduce:
  C:/AI/director/.venv/Scripts/python.exe C:/AI/community/notes/ali31_prompt_set_check.py --check
  C:/AI/director/.venv/Scripts/python.exe C:/AI/community/notes/ali31_prompt_set_check.py --selftest
  C:/AI/director/.venv/Scripts/python.exe C:/AI/community/notes/ali11_run_checks.py --run
"""
import copy
import hashlib
import json
import os
import re
import sys
import tempfile

C = "C:/AI/community"
DOC = os.path.join(C, "notes", "im1_prompts.md")
GUIDE = os.path.join(C, "notes", "prompt_guide_20261024.md")
WEB = os.path.join(C, "notes", "web")
KEEPER = os.path.join(C, "p7", "graphs", "ali147_pool_hc_r3b_s51130003.baseline.api.json")
STAGED = os.path.join(C, "p7", "graphs", "ali147_pool_hc_r3i_s51130003.api.json")
MAN = os.path.join(C, "notes", "ali31_prompt_set_manifest.json")
FIXER = os.path.join(C, "notes", "ali31_prompt_negation_pass.py")

SEEDS = [51130001, 51130002, 51130003, 51130004, 51130005, 51130006]
BLOCK_IDS = [f"ali147_pool_hc_r{i}i_s{s}" for i, s in enumerate(SEEDS, start=1)]
SECTIONS = {"c0": ["subject_definitions", "summary", "retention_analysis", "detailed_description",
                   "overall_soundscape", "non_diegetic_music"],
            "c1": ["subject_definitions", "summary", "retention_analysis", "integrated_multimodal_description",
                   "overall_soundscape", "non_diegetic_music"]}
MAIN = {"c0": "detailed_description", "c1": "integrated_multimodal_description"}
BAND = {"c0": (350, 500), "c1": (350, 550)}
CAM_TERMS = ["Push In", "Pull Out", "Pan", "Tilt", "Truck", "Pedestal", "Tracking", "Crash Zoom", "Dolly Zoom",
             "Handheld", "Static Shot", "Static Frame", "Arc Shot", "Zoom", "Dolly", "Rack Focus", "Snap Cranes"]
NEG = re.compile(r"\b(no|not|never|without|neither|nor)\b", re.I)
BEAT = re.compile(r"At (\d\d):(\d\d)\.(\d\d\d)")
AGE = re.compile(r"fictional adult(?: woman)? aged (\d\d?)(?: and)?")
KEEPWORDS = re.compile(r"\b(best|better|good|nice|great|keep|keeper|pick|winner|rank)\w*", re.I)
ALLOWED_DIFF = {"c0.prompt", "c1.prompt", "save.filename_prefix"}
# tokens are built by concatenation so this file's own text never contains them; "/prompt" is NOT a token
# because the guide path notes/prompt_guide_20261024.md contains that substring (measured 2026-10-24).
NET = ["127.0" + ".0.1:" + "8188", "127.0" + ".0.1:" + "8189", "127.0" + ".0.1:" + "10004",
       "127.0" + ".0.1:" + "8080", "ur" + "llib", "sock" + "et", "llama-" + "swap", "run_" + "graph_job"]


def parse_blocks(doc):
    """(id, chunk, seed, sections-in-order, text) for each '### id=.. chunk=.. seed=..' block."""
    out = []
    for m in re.finditer(r"### id=(\S+) chunk=(c\d) seed=(\d+)\n(.*?)(?=\n### id=|\Z)", doc, re.S):
        bid, chunk, seed, body = m.group(1), m.group(2), int(m.group(3)), m.group(4)
        body = re.sub(r"\n---\s*$", "", body.rstrip())
        secs = re.findall(r"^([a-z_]+):$", body, flags=re.M)
        out.append({"id": bid, "chunk": chunk, "seed": seed, "secs": secs, "text": body,
                    "sections": dict(re.findall(r"^([a-z_]+):$\n(.*?)(?=^\w[\w_]*:$|\Z)", body, flags=re.M | re.S))})
    return out


def main_words(b):
    m = re.search(rf"^{MAIN[b['chunk']]}:\n(.*?)(?=^\w[\w_]*:$|\Z)", b["text"], flags=re.M | re.S)
    return len((m.group(1) if m else "").split())


def beat_times(text):
    """every 'At MM:SS.mmm' beat in a block, as seconds (BEAT groups are MM, SS, mmm - no hours field)."""
    return sorted(int(m) * 60 + int(s) + int(ms) / 1000 for m, s, ms in BEAT.findall(text))


def graph_canvas(js):
    """(width, height) every MiniMaxH3 generation node claims; one canvas per graph is required.
    The r3b/r3i graphs use MiniMaxH3ReferenceToVideo (not ImageToVideo, which has no audio_vae - AGENTS.md)."""
    g = json.loads(js)
    sizes = {(int(n["inputs"]["width"]), int(n["inputs"]["height"]))
             for n in g.values() if n.get("class_type", "").startswith("MiniMaxH3")
             and isinstance(n.get("inputs", {}).get("width"), int)}
    if not sizes:
        raise ValueError("no MiniMaxH3 node with an integer width/height in this graph")
    if len(sizes) > 1:
        raise ValueError(f"graph carries {len(sizes)} canvases {sorted(sizes)}")
    return sizes.pop()


def diff_paths(a, b):
    out = []
    for nid in sorted(set(a) | set(b)):
        if nid not in a or nid not in b:
            out.append(f"{nid}.NODE")
            continue
        if a[nid]["class_type"] != b[nid]["class_type"]:
            out.append(f"{nid}.class_type")
        for k in sorted(set(a[nid]["inputs"]) | set(b[nid]["inputs"])):
            if a[nid]["inputs"].get(k) != b[nid]["inputs"].get(k):
                out.append(f"{nid}.{k}")
    return out


# ----------------------------------------------------------------- detectors
def ck_coverage(ctx):
    bs = parse_blocks(ctx["doc"])
    out = []
    want = {(b, c) for b in BLOCK_IDS for c in ("c0", "c1")}
    got = [(b["id"], b["chunk"]) for b in bs]
    if len(set(got)) != len(got):
        out.append(f"COVERAGE duplicate blocks in {sorted(set(x for x in got if got.count(x) > 1))}")
    missing = sorted(want - set(got))
    extra = sorted(set(got) - want)
    if missing or extra:
        out.append(f"COVERAGE missing={missing} unexpected={extra} (want the six pool runs x c0/c1)")
    for b in bs:
        if b["seed"] != int(b["id"].rsplit("_s", 1)[1]):
            out.append(f"COVERAGE {b['id']} {b['chunk']} seed header {b['seed']} != id suffix")
    return out


def ck_sections(ctx):
    out = []
    for b in parse_blocks(ctx["doc"]):
        if b["secs"] != SECTIONS[b["chunk"]]:
            out.append(f"SECTIONS {b['id']} {b['chunk']} order {b['secs']} != {SECTIONS[b['chunk']]}")
    return out


def ck_words(ctx):
    out = []
    for b in parse_blocks(ctx["doc"]):
        lo, hi = BAND[b["chunk"]]
        w = main_words(b)
        if not lo <= w <= hi:
            out.append(f"WORDS {b['id']} {b['chunk']} main field {w} words outside {lo}-{hi}")
    return out


def ck_beats(ctx):
    out = []
    for b in parse_blocks(ctx["doc"]):
        beats = beat_times(b["text"])
        if len(beats) < 3:
            out.append(f"BEATS {b['id']} {b['chunk']} only {len(beats)} At MM:SS.mmm beats")
        if b["chunk"] == "c0" and any(not (0.0 <= t < 5.0) for t in beats):
            out.append(f"BEATS {b['id']} c0 beat outside the 00:00-00:05 window")
        if b["chunk"] == "c1" and any(not (5.0 <= t <= 10.0) for t in beats):
            out.append(f"BEATS {b['id']} c1 beat outside the 00:05-00:10 continuation window")
    return out


def ck_camera(ctx):
    out = []
    for b in parse_blocks(ctx["doc"]):
        m = b["sections"].get(MAIN[b["chunk"]], "")
        if not any(t in m for t in CAM_TERMS):
            out.append(f"CAMERA {b['id']} {b['chunk']} main field names no canon camera term")
        if "amplitude" not in m or "speed" not in m:
            out.append(f"CAMERA {b['id']} {b['chunk']} main field has no amplitude/speed wording")
    return out


def ck_continue(ctx):
    out = []
    for b in parse_blocks(ctx["doc"]):
        s = b["sections"].get("summary", "")
        if b["chunk"] == "c1":
            if not s.lstrip().startswith("[video continuation + reference generation]"):
                out.append(f"CONTINUE {b['id']} c1 summary is not tagged [video continuation + reference generation]")
            if "<Video 1>" not in s or "<Video 1>" not in b["sections"].get("retention_analysis", ""):
                out.append(f"CONTINUE {b['id']} c1 does not cite <Video 1> in summary and retention_analysis")
        elif not s.lstrip().startswith("[reference generation]"):
            out.append(f"CONTINUE {b['id']} c0 summary is not tagged [reference generation]")
    return out


def ck_negation(ctx):
    out = []
    for b in parse_blocks(ctx["doc"]):
        toks = NEG.findall(b["text"])
        if toks:
            out.append(f"NEGATION {b['id']} {b['chunk']} carries {len(toks)} prohibition tokens "
                       f"{sorted({t.lower() for t in toks})} - guide rule 4 puts negation in the negpip node "
                       "(https://github.com/gas/comfyui-minimax-h3-negpip), not in the prompt prose")
    return out


def ck_adults(ctx):
    sys.path.insert(0, os.path.join(C, "scripts"))
    from comm import guard_ok
    out = []
    for b in parse_blocks(ctx["doc"]):
        for name, text in b["sections"].items():
            if not guard_ok(f"{name} {text}"):
                out.append(f"ADULTS {b['id']} {b['chunk']} section {name} fails scripts/comm.py guard_ok")
        ages = [int(a) for a in AGE.findall(b["text"])]
        if not ages:
            out.append(f"ADULTS {b['id']} {b['chunk']} states no 'fictional adult aged N'")
        if any(a < 21 for a in ages):
            out.append(f"ADULTS {b['id']} {b['chunk']} age {min(ages)} under the 21 floor of the content lock")
    return out


def ck_canvas(ctx):
    w, h = graph_canvas(ctx["base"])
    out = []
    claim = re.findall(r"the SAME (\d{3,4})x(\d{3,4}) 16:9 canvas", ctx["doc"])
    if not claim:
        return ["CANVAS the doc header states no canvas"]
    if len(set(claim)) != 1:
        out.append(f"CANVAS the doc header states more than one canvas {sorted(set(claim))}")
    cw, ch = int(claim[0][0]), int(claim[0][1])
    if (cw, ch) != (w, h):
        out.append(f"CANVAS the doc claims {cw}x{ch}, the baseline graph on disk is {w}x{h}")
    if w % 32 or h % 32:
        out.append(f"CANVAS {w}x{h} is not a multiple of 32 (continuum v3/resolution.py H3_CANVAS_MULTIPLE)")
    return out


def ck_sync(ctx):
    g = json.loads(ctx["staged"])
    base = json.loads(ctx["base"])
    out = []
    for b in parse_blocks(ctx["doc"]):
        if b["id"] == "ali147_pool_hc_r3i_s51130003":
            if g[b["chunk"]]["inputs"]["prompt"].strip() != b["text"].strip():
                out.append(f"SYNC staged graph {b['chunk']} prompt != the doc text (the render window would "
                           "render words that are not the reviewed set)")
    d = sorted(set(diff_paths(base, g)) - ALLOWED_DIFF)
    if d:
        out.append(f"SYNC staged graph changes {d} beyond prompt + filename_prefix (the 2.1b one-variable rule)")
    return out


def ck_guide(ctx):
    out = []
    rows = re.findall(r"^\|\s*\d+\s*\|.*$", ctx["guide"], flags=re.M)
    if len(rows) < 5:
        return [f"GUIDE_CITES the guide source table has {len(rows)} rows"]
    named = 0
    for row in rows:
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        saved = re.findall(r"`([^`]+\.(?:md|json|html|txt))`", cells[3]) if len(cells) > 3 else []
        stated = re.findall(r"([\d,]+) B", cells[4]) if len(cells) > 4 else []
        for name in saved:
            path = os.path.join(WEB, name)
            if not os.path.isfile(path):
                out.append(f"GUIDE_CITES the guide names {name} and notes/web has no such file")
                continue
            named += 1
        for size in stated:
            n = int(size.replace(",", ""))
            hit = [os.path.join(WEB, s) for s in saved
                   if os.path.isfile(os.path.join(WEB, s)) and os.path.getsize(os.path.join(WEB, s)) == n]
            if not hit:
                out.append(f"GUIDE_CITES the guide states {size} B and no named page in that row is that size on disk")
    if named < 4:
        out.append(f"GUIDE_CITES only {named} cited saved pages exist in notes/web")
    return out


def ck_keepword(ctx):
    m = ctx["manifest"]
    if not m:
        return ["KEEPWORD no manifest on disk (run --check to write notes/ali31_prompt_set_manifest.json)"]
    # only the fields this gate writes are graded: prompt prose legitimately contains "keeps dancing topless"
    audit = {k: v for k, v in m.items() if k not in ("blocks", "cited_pages")}
    hits = sorted({w.group(0) for w in KEEPWORDS.finditer(json.dumps(audit))})
    return [f"KEEPWORD manifest carries verdict words {hits}; KEEP is Derrick's alone (AGENTS.md hard line)"] if hits else []


def ck_nogpu(ctx):
    hits = [t for t in NET if t in ctx["self_src"]]
    return [f"NO_GPU this gate names {hits}"] if hits else []


CHECKS = [ck_coverage, ck_sections, ck_words, ck_beats, ck_camera, ck_continue, ck_negation, ck_adults,
          ck_canvas, ck_sync, ck_guide, ck_keepword, ck_nogpu]


def load():
    man = json.loads(open(MAN, encoding="utf-8").read()) if os.path.isfile(MAN) else {}
    return dict(doc=open(DOC, encoding="utf-8").read(), guide=open(GUIDE, encoding="utf-8").read(),
                staged=open(STAGED, encoding="utf-8").read(), base=open(KEEPER, encoding="utf-8").read(),
                self_src=open(os.path.abspath(__file__), encoding="utf-8").read(),
                fixer=open(FIXER, encoding="utf-8").read() if os.path.isfile(FIXER) else "", manifest=man)


def run(ctx):
    probs = []
    for fn in CHECKS:
        try:
            probs += fn(ctx)
        except Exception as e:                                       # a crashing detector is a defect, not a pass
            probs.append(f"{fn.__name__[3:].upper()}_CRASH {type(e).__name__}: {e}")
    return probs


def build_manifest(ctx):
    bs = parse_blocks(ctx["doc"])
    w, h = graph_canvas(ctx["base"])
    g = json.loads(ctx["staged"])
    blocks = {}
    for b in bs:
        beats = beat_times(b["text"])
        blocks[f"{b['id']}/{b['chunk']}"] = {
            "sections": b["secs"], "main_field": MAIN[b["chunk"]], "main_words": main_words(b),
            "words": len(b["text"].split()), "beats": len(beats),
            "beat_window": [beats[0], beats[-1]] if beats else None,
            "camera_terms": sorted({t for t in CAM_TERMS if t in b["sections"][MAIN[b["chunk"]]]}),
            "amplitude": "amplitude" in b["sections"][MAIN[b["chunk"]]],
            "negation_tokens": len(NEG.findall(b["text"])),
            "ages": sorted({int(a) for a in AGE.findall(b["text"])}),
            "video1": "<Video 1>" in b["text"],
        }
    rows = re.findall(r"^\|\s*\d+\s*\|.*$", ctx["guide"], flags=re.M)
    saved = sorted({n for row in rows for n in re.findall(r"`([^`]+\.(?:md|json|html|txt))`", row)})
    return {
        "item": "3.1", "mission": "ALI-163", "doc": DOC, "guide": GUIDE,
        "guide_rule_audited": "rule 4: Move negation out of prose (negpip node, not prose)",
        "negpip_repo": "https://github.com/gas/comfyui-minimax-h3-negpip",
        "hf_discussion": "https://huggingface.co/spaces/NeuralNova/Stable-Video-Infinitie-Systems-Solutions/discussions/52",
        "blocks": blocks,
        "doc_graph_sync": {"staged": STAGED, "staged_sha256": hashlib.sha256(ctx["staged"].encode()).hexdigest(),
                           "staged_prompt_matches_doc": [c for c in ("c0", "c1")
                                                         if g[c]["inputs"]["prompt"].strip()
                                                         == next(b["text"] for b in bs
                                                                 if b["id"] == "ali147_pool_hc_r3i_s51130003"
                                                                 and b["chunk"] == c).strip()],
                           "one_variable_diff": sorted(set(diff_paths(json.loads(ctx["base"]), g)) - ALLOWED_DIFF)},
        "canvas": {"doc_claim": re.findall(r"the SAME (\d{3,4}x\d{3,4}) 16:9 canvas", ctx["doc"])[:1],
                   "baseline_graph": f"{w}x{h}"},
        "cited_pages": {n: (os.path.getsize(os.path.join(WEB, n)) if os.path.isfile(os.path.join(WEB, n)) else None)
                        for n in saved},
        "totals": {"blocks": len(blocks), "negation_tokens": sum(v["negation_tokens"] for v in blocks.values()),
                   "words_min": min(v["main_words"] for v in blocks.values()),
                   "words_max": max(v["main_words"] for v in blocks.values()),
                   "beats_min": min(v["beats"] for v in blocks.values()),
                   "adult_age_min": min(min(v["ages"]) for v in blocks.values() if v["ages"])},
        "fixer": FIXER, "fixer_sites": 29,
        "no_verdict_note": "this file states no verdict on any prompt: a prompt set is audited against the guide, "
                           "and the verdict on a render is Derrick's alone",
    }


# ----------------------------------------------------------------- selftest
def selftest():
    ctx = load()
    real = run(ctx)
    seeds = []

    def case(tag, mut, allowed=()):
        c = copy.deepcopy(ctx)
        mut(c)
        probs = run(c)
        hit = any(p.split()[0] == tag for p in probs)
        extra = [p for p in probs if p.split()[0] not in (tag,) + tuple(allowed)]
        seeds.append((tag, hit, probs, extra))

    def drop_block(c):
        c["doc"] = re.sub(r"### id=ali147_pool_hc_r6i_s51130006 chunk=c1 seed=51130006\n.*?(?=\n### id=|\Z)",
                          "", c["doc"], flags=re.S)
    case("COVERAGE", drop_block, allowed=("WORDS", "BEATS", "CAMERA", "CONTINUE", "NEGATION", "ADULTS", "SYNC"))

    def drop_section(c):
        c["doc"] = c["doc"].replace("summary:\n[reference generation]", "summary_removed:\n[reference generation]", 1)
    case("SECTIONS", drop_section, allowed=("ADULTS", "CONTINUE", "NEGATION"))

    def short_main(c):
        b = next(x for x in parse_blocks(c["doc"]) if x["chunk"] == "c0")
        body = b["sections"]["detailed_description"]
        cut = " ".join(body.split()[:340]) + body[len(body.rstrip()):]   # keep the trailing blank line
        c["doc"] = c["doc"].replace(body, cut, 1)
    case("WORDS", short_main, allowed=("ADULTS",))

    def no_beats(c):
        b = next(x for x in parse_blocks(c["doc"]) if x["chunk"] == "c1")
        c["doc"] = c["doc"].replace(b["sections"]["integrated_multimodal_description"],
                                    re.sub(r"At \d\d:\d\d\.\d\d\d, ", "",
                                           b["sections"]["integrated_multimodal_description"]), 1)
    case("BEATS", no_beats, allowed=("ADULTS",))

    def plain_move(c):
        b = next(x for x in parse_blocks(c["doc"]) if x["chunk"] == "c0")
        c["doc"] = c["doc"].replace(b["sections"]["detailed_description"],
                                    b["sections"]["detailed_description"]
                                    .replace("Push In", "move in").replace("small amplitude", "a small range")
                                    .replace("slow speed", "slowly"), 1)
    case("CAMERA", plain_move, allowed=("ADULTS",))

    def no_video1(c):
        c["doc"] = c["doc"].replace("summary:\n[video continuation + reference generation]",
                                    "summary:\n[reference generation]", 1)
    case("CONTINUE", no_video1, allowed=("ADULTS", "CONTINUE"))

    def negation(c):
        c["doc"] = c["doc"].replace("one continuous take.", "no cuts.", 1)
    case("NEGATION", negation, allowed=("ADULTS", "CONTINUE"))

    def banned(c):
        b = parse_blocks(c["doc"])[0]
        c["doc"] = c["doc"].replace(b["text"],
                                    b["text"] + " The scene is a schoolgirl in uniform and the minors watch.", 1)
    case("ADULTS", banned)

    def no_age(c):
        b = next(x for x in parse_blocks(c["doc"]) if x["id"].endswith("s51130005") and x["chunk"] == "c0")
        c["doc"] = c["doc"].replace(b["text"], re.sub(r"aged \d\d", "aged", b["text"]), 1)
    case("ADULTS", no_age)

    def canvas(c):
        c["doc"] = c["doc"].replace("the SAME 1344x768 16:9 canvas", "the SAME 1024x576 16:9 canvas")
    case("CANVAS", canvas)

    def drift_graph(c):
        g = json.loads(c["staged"])
        g["c0"]["inputs"]["prompt"] += " extra words"
        c["staged"] = json.dumps(g)
    case("SYNC", drift_graph)

    def second_var(c):
        g = json.loads(c["staged"])
        g["s0_sched"]["inputs"]["steps"] = 20
        c["staged"] = json.dumps(g)
    case("SYNC", second_var)

    def ghost_page(c):
        c["guide"] = c["guide"].replace("agy51_ref_guide.md", "agy51_ref_guide_absent.md")
    case("GUIDE_CITES", ghost_page)

    def fake_size(c):
        c["guide"] = c["guide"].replace("23,553 B", "99,999 B")
    case("GUIDE_CITES", fake_size)

    def verdict(c):
        c["manifest"] = dict(c["manifest"], no_verdict_note="the best prompt of the batch")
    case("KEEPWORD", verdict)

    def net(c):
        c["self_src"] = c["self_src"] + ("\nimport ur" + "lib.request\nur" + "lib.request.url"
                                         + "open('http://127.0.0.1:" + "10004/prompt')\n")
    case("NO_GPU", net)

    fired = [t for t, hit, p, x in seeds if hit]
    leaky = [(t, p) for t, hit, p, x in seeds if not hit]
    collateral = [(t, x) for t, hit, p, x in seeds if hit and x]
    for t, hit, p, x in seeds:
        print(f"seed {t}: fired={'yes' if hit else 'NO '} problems={len(p)} unexpected={len(x)} {p[:1]}")
    print(f"SELFTEST seeds={len(seeds)} fired={len(fired)} silent={len(leaky)} collateral={len(collateral)} "
          f"real_tree_problems={len(real)}")
    for t, p in leaky + collateral:
        print(f"  DEFECT {t}: {p}")
    for p in real:
        print(f"  REAL {p}")
    return 0 if not leaky and not collateral and not real and len(fired) == len(seeds) else 1


def main():
    mode = (sys.argv[1] if len(sys.argv) > 1 else "--check").lower()
    if mode == "--selftest":
        return selftest()
    ctx = load()
    man = build_manifest(ctx)
    if mode == "--build":
        open(MAN, "w", encoding="utf-8").write(json.dumps(man, indent=2, sort_keys=True) + "\n")
        ctx["manifest"] = man
    probs = run(ctx)
    t = man["totals"]
    print(f"PROBLEMS {len(probs)} VERDICT {'CLEAN' if not probs else 'RED'} blocks={t['blocks']} "
          f"negation_tokens={t['negation_tokens']} words={t['words_min']}-{t['words_max']} beats_min={t['beats_min']} "
          f"adult_age_min={t['adult_age_min']} canvas={man['canvas']['baseline_graph']} "
          f"cited_pages={sum(1 for v in man['cited_pages'].values() if v)} sync={len(man['doc_graph_sync']['staged_prompt_matches_doc'])}/2 "
          f"one_variable={man['doc_graph_sync']['one_variable_diff']} manifest={'written' if mode == '--build' else 'read'}")
    for p in probs:
        print("  " + p)
    return 0 if not probs else 1


if __name__ == "__main__":
    sys.exit(main())
