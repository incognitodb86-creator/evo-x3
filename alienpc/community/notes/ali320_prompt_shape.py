#!/usr/bin/env python3
"""ali320_prompt_shape.py - fix_plan 3.20 gate: measure the prompt SHAPE a graph really carries.

Why this file exists (2026-10-27): every prompt-side item in the plan reads a prompt SET (a file under
notes/), and the render carries a GRAPH. A set can be in shape while the graph that feeds the sampler is
not, so the census below reads the graph - every prompt-bearing key of every node - and measures it
against the ranges the community guides recorded in
C:/AI/community/notes/now_h3_prompt_format_research_20261025.md and
C:/AI/community/notes/h3_scene_prompt_research_20261025.md, which the plan's 3.x rows also cite:

  sequence prompt 800-1200 words; opening passage 40-60 words; closing passage 150-200 words;
  one clause per line, 12-16 words, a line <= 160 characters; a sentence <= 60 words;
  clip segments 20-30 words.

"first/last sentence" is read as the opening/closing PASSAGE (a blank-line-separated block of short
clause lines), because the same guide asks for one clause per 12-16-word line: a sentence-level read
cannot fit a compliant text, and that reading was measured, not chosen for convenience (see --selftest:
the control is a text built exactly to the guide and must score 0 defects).

Modes:
  --check [graph.json]      census the graph, print one KEY line per prompt-bearing key, print every
                            defect, write the JSON census (default graph: the one row 3.20 names;
                            --json <path> moves the output, --json '' skips writing it)
  --selftest                one compliant control + nine seeded defects; every seed MUST fire and the
                            control MUST score 0 (L10: a green check that cannot fail is worthless)

Exit codes: 0 = no defect / selftest clean, 1 = defects found (that IS the finding row 3.20 asks for),
2 = selftest fault. rc 1 from --check is not a tool failure.
"""
import json
import os
import re
import sys

GRAPH = os.path.join("p7", "graphs", "ali163_hc15_gi046_s51150032.api.json")
OUT = os.path.join("notes", "ali320_prompt_shape.json")
SEQ_KEYS = ("sequence_prompt", "prompt")
SEG_KEYS = ("clips_json", "clip_prompt")
PROMPT_KEY = re.compile(r"^(prompt(_\d+)?|sequence_prompt|clip_prompt|clips_json)$")
NL = chr(10)
BLANK_LINE = NL + NL

RANGE = {
    "seq_words": (800, 1200),
    "opening_passage": (40, 60),
    "closing_passage": (150, 200),
    "line_words": (12, 16),
    "line_chars": 160,
    "sentence_words": 60,
    "segment_words": (20, 30),
}


def words(t):
    return len(t.split())


def sentences(t):
    return [s for s in re.split(r"(?<=[.!?])\s+", t.replace(NL, " ").strip()) if s]


def lines_of(t):
    return [l.strip() for l in t.split(NL) if l.strip()]


def paragraphs(t):
    return [b.strip() for b in re.split(NL + r"\s*" + NL, t.strip()) if b.strip()]


def measure(text):
    ls = lines_of(text)
    sents = sentences(text)
    paras = paragraphs(text)
    pw = [words(p) for p in paras]
    return {
        "words": words(text),
        "lines": len(ls),
        "max_line_chars": max([len(l) for l in ls]) if ls else 0,
        "avg_line_chars": sum(len(l) for l in ls) // len(ls) if ls else 0,
        "line_words": [words(l) for l in ls],
        "sentences": len(sents),
        "sentence_words": [words(s) for s in sents],
        "paragraphs": len(paras),
        "first_passage_words": pw[0] if pw else 0,
        "last_passage_words": pw[-1] if pw else 0,
    }


def keys_of(graph):
    """Every prompt-bearing (node, key, text) in a graph in either format (API dict or node list)."""
    out = []
    nodes = graph.items() if isinstance(graph, dict) else list(enumerate(graph))
    for nid, node in nodes:
        if not isinstance(node, dict):
            continue
        for k, v in node.get("inputs", {}).items():
            if isinstance(v, str) and PROMPT_KEY.match(k):
                out.append((str(nid), k, v))
    return out


def census(graph):
    rows, defects = [], []
    for nid, k, text in sorted(keys_of(graph)):
        m = measure(text)
        kind = "sequence" if k in SEQ_KEYS else ("segment" if k in SEG_KEYS else "other")
        rows.append({"node": nid, "key": k, "kind": kind, **m})
        lo, hi = RANGE["seq_words"]
        if kind == "sequence":
            if not lo <= m["words"] <= hi:
                defects.append("SEQ_WORDS %s.%s = %d words, the sources ask for %d-%d"
                               % (nid, k, m["words"], lo, hi))
            if m["lines"] <= 1 and m["words"] > 200:
                defects.append("NO_LINES %s.%s = %d words on one line, no clause structure at all"
                               % (nid, k, m["words"]))
            if m["max_line_chars"] > RANGE["line_chars"]:
                defects.append("LINE_CHARS %s.%s = a %d-character line, cap %d"
                               % (nid, k, m["max_line_chars"], RANGE["line_chars"]))
            bad = [w for w in m["line_words"] if not RANGE["line_words"][0] <= w <= RANGE["line_words"][1]]
            if len(bad) > max(2, len(m["line_words"]) // 3):
                defects.append("LINE_WORDS %s.%s = %d/%d lines outside %d-%d words"
                               % (nid, k, len(bad), len(m["line_words"]),
                                  RANGE["line_words"][0], RANGE["line_words"][1]))
            over = [w for w in m["sentence_words"] if w > RANGE["sentence_words"]]
            if over:
                defects.append("SENTENCE_WORDS %s.%s = %d sentences over %d words (max %d)"
                               % (nid, k, len(over), RANGE["sentence_words"], max(over)))
            if not RANGE["opening_passage"][0] <= m["first_passage_words"] <= RANGE["opening_passage"][1]:
                defects.append("FIRST_SENTENCE %s.%s = the opening passage is %d words, the sources ask for %d-%d"
                               % (nid, k, m["first_passage_words"],
                                  RANGE["opening_passage"][0], RANGE["opening_passage"][1]))
            if not RANGE["closing_passage"][0] <= m["last_passage_words"] <= RANGE["closing_passage"][1]:
                defects.append("LAST_SENTENCE %s.%s = the closing passage is %d words, the sources ask for %d-%d"
                               % (nid, k, m["last_passage_words"],
                                  RANGE["closing_passage"][0], RANGE["closing_passage"][1]))
        if kind == "segment":
            lo, hi = RANGE["segment_words"]
            try:
                data = json.loads(text)
            except Exception:
                data = None
            segs = []
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        segs += [v for v in item.values() if isinstance(v, str)]
                    elif isinstance(item, str):
                        segs.append(item)
            else:
                segs = lines_of(text)
            if not segs:
                defects.append("SEG_READ %s.%s = no segment text the census can read" % (nid, k))
            else:
                off = [words(s) for s in segs if not lo <= words(s) <= hi]
                if off:
                    defects.append("SEG_WORDS %s.%s = %d/%d segments outside %d-%d words (max %d)"
                                   % (nid, k, len(off), len(segs), lo, hi,
                                      max([words(s) for s in segs])))
    return rows, defects


# ------------------------------------------------------------- synthetic text: control + seeded defects
POOL = ("the camera holds a steady frame as the scene breathes and the light moves across the floor "
        "while the figure turns and keeps a slow calm posture").split()


def _words(n, seed=0):
    """n plain words, deterministic. The gate counts SHAPE, so the filler is plain on purpose; no
    model ever reads this file, and the text is never judged for prose."""
    return " ".join(POOL[(seed + i) % len(POOL)] for i in range(n))


def _clauses(count_words, lw=14, seed=0):
    """count_words of filler, one clause per line, lw words per line (the spec: 12-16 words, <=160 chars)."""
    out, i = [], 0
    while i < count_words:
        n = min(lw, count_words - i)
        out.append(_words(n, seed=seed + i))
        i += n
    return out


def mkseq(total=924, opening=56, closing=170, lw=14, wide=False, flat=False,
          long_sentence=False, opening_words=None, closing_words=None):
    """The CONTROL, built exactly to the ranges in this file's docstring: an opening passage of 40-60
    words, body lines of 12-16 words (one clause each), a closing passage of 150-200 words, 800-1200
    words in all, passages separated from the body by a blank line. Every keyword injects exactly one
    defect, and each seed in SEEDS below requires a named detector to fire on it."""
    op = opening_words if opening_words is not None else opening
    cl = closing_words if closing_words is not None else closing
    body = max(0, total - op - cl)
    blocks = [
        NL.join(l + "." for l in _clauses(op, lw, 0)),
        NL.join(l + "." for l in _clauses(body, lw, op)),
        NL.join(l + "." for l in _clauses(cl, lw, op + body)),
    ]
    if wide:
        blocks[1] = (_words(40, seed=800) + "." + NL) + blocks[1]
    if long_sentence:
        ls = blocks[1].split(NL)
        ls.insert(len(ls) // 2, _words(90, seed=700) + ".")
        blocks[1] = NL.join(ls)
    if flat:
        return " ".join(l for b in blocks for l in b.split(NL))
    return BLANK_LINE.join(blocks)


def mkseg(n=6, words_per=25, off=None):
    """A clips_json payload of n segments of words_per words each (the spec is 20-30 words)."""
    rows = []
    for i in range(n):
        w = off if (off is not None and i == 0) else words_per
        rows.append({"clip_" + str(i + 1): _words(w, seed=i * 7) + "."})
    return json.dumps(rows, ensure_ascii=False)


def seed_graph(name):
    seq, seg = mkseq(), mkseg()
    if name == "control":
        pass
    elif name == "seq_short":
        seq = mkseq(total=602)
    elif name == "seq_long":
        seq = mkseq(total=1400)
    elif name == "line_chars":
        seq = mkseq(wide=True)
    elif name == "line_words":
        seq = mkseq(lw=8)
    elif name == "sentence_words":
        seq = mkseq(long_sentence=True)
    elif name == "first_sentence":
        seq = mkseq(opening_words=18)
    elif name == "last_sentence":
        seq = mkseq(closing_words=40)
    elif name == "seg_words":
        seg = mkseg(off=52)
    elif name == "no_lines":
        seq = mkseq(flat=True)
    return {"9": {"class_type": "X", "inputs": {"sequence_prompt": seq, "clips_json": seg}}}


SEEDS = ["seq_short", "seq_long", "line_chars", "line_words", "sentence_words",
         "first_sentence", "last_sentence", "seg_words", "no_lines"]
SEED_PAT = {"seq_short": "SEQ_WORDS", "seq_long": "SEQ_WORDS", "line_chars": "LINE_CHARS",
            "line_words": "LINE_WORDS", "sentence_words": "SENTENCE_WORDS",
            "first_sentence": "FIRST_SENTENCE", "last_sentence": "LAST_SENTENCE",
            "seg_words": "SEG_WORDS", "no_lines": "NO_LINES"}


def selftest():
    rows, defects = census(seed_graph("control"))
    seq = [r for r in rows if r["kind"] == "sequence"][0]
    print("control: words=%d lines=%d max_line_chars=%d paragraphs=%d opening=%d closing=%d -> %d defects"
          % (seq["words"], seq["lines"], seq["max_line_chars"], seq["paragraphs"],
             seq["first_passage_words"], seq["last_passage_words"], len(defects)))
    for d in defects:
        print("  control defect: " + d)
    fired, silent = 0, []
    if defects:
        silent.append("control is not clean")
    for name in SEEDS:
        _, d = census(seed_graph(name))
        hit = any(SEED_PAT[name] in x for x in d)
        print("seed %-16s fires=%d defects=%d %s"
              % (name, int(hit), len(d), (d[0][:72] if d else "")))
        fired += int(hit)
        if not hit:
            silent.append(name)
    ok = not silent and fired == len(SEEDS)
    print("seed selftest: %d/%d fired, required %d, %d silent%s"
          % (fired, len(SEEDS), len(SEEDS), len(silent),
             " -> VERDICT SEEDS CLEAN" if ok else " -> VERDICT SEEDS DIRTY " + str(silent)))
    return 0 if ok else 2


def main():
    args = sys.argv[1:]
    if "--selftest" in args:
        return selftest()
    graph_path, out = None, OUT
    for i, a in enumerate(args):
        if a == "--json":
            out = args[i + 1] if i + 1 < len(args) else ""
        elif a.endswith(".json") and a != out:
            graph_path = a
    graph_path = graph_path or GRAPH
    if not os.path.isfile(graph_path):
        print("DEFECT GRAPH_ABSENT %s is not on disk (name a graph you measured)" % graph_path)
        return 1
    graph = json.load(open(graph_path, encoding="utf-8"))
    rows, defects = census(graph)
    print("prompt-shape census: graph=%s keys=%d ranges=%s" % (graph_path, len(rows), json.dumps(RANGE)))
    for r in rows:
        print("KEY %s.%s kind=%s words=%d lines=%d max_line_chars=%d avg_line_chars=%d sentences=%d "
              "paragraphs=%d opening_passage_words=%d closing_passage_words=%d"
              % (r["node"], r["key"], r["kind"], r["words"], r["lines"], r["max_line_chars"],
                 r["avg_line_chars"], r["sentences"], r["paragraphs"], r["first_passage_words"],
                 r["last_passage_words"]))
    for d in defects:
        print("DEFECT " + d)
    print("prompt shape: %d key(s), %d defect(s)%s"
          % (len(rows), len(defects), " -> shape matches the ranges" if not defects
             else " -> shape is NOT in the ranges"))
    if out:
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        json.dump({"graph": graph_path, "ranges": RANGE, "keys": rows, "defects": defects},
                  open(out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        print("wrote " + out)
    return 0 if not defects else 1


if __name__ == "__main__":
    sys.exit(main())
