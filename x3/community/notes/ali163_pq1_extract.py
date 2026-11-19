#!/usr/bin/env python3
"""PQ1 (ALI-163) prompt research + IM1 prompt completeness check, CPU only.

Part 1 - extraction. Turns the saved research pages in notes/web into plain text so
notes/prompt_guide_20261023.md can quote them, and copies the saved MiniMax guides
next to them:

  notes/web/pq1_minimax_*.txt              -> ..._text.txt (verbatim copy; web_fetch
                                              saves a markdown body as .txt)
  notes/web/pq1_tenstrip_d<N>.html       -> ..._text.txt (every post body, no nav/svg)
  notes/web/pq1_civitai_model_<id>.json  -> ..._text.txt (civitai card body)

Part 2 - the PQ1 completeness check of notes/im1_prompts.md: one block per IM1 render
(6 clips x c0 + c1), the six v2 sections on every c0, the continuation sections on
every c1, the beat-by-beat timings, and the new reference wiring.

Part 3 - self-destruct, because a green check that cannot fail is worthless:
  (a) the stale face-crop-only wording MUST be found in exactly the four c0 prompts
      built with that wiring (r3, r4, r5, r6) and in none of the improved ones;
  (b) PQ1_DESTRUCT=<clone of im1_prompts.md with a broken section line> makes the
      completeness check run on the clone, where it MUST fail.

Run:  python notes/ali163_pq1_extract.py
Destruct run:  set PQ1_DESTRUCT=<clone> && python notes/ali163_pq1_extract.py
"""
from __future__ import annotations
import glob
import html
import io
import json
import os
import re
import sys

WEB = r"C:/AI/community/notes/web"
NOTES = r"C:/AI/community/notes"
IM1 = os.path.join(NOTES, "im1_prompts.md")

TAG = re.compile(r"<[^>]+>")
PROSE_START = re.compile(r'class="prose[^"]*"[^>]*>')
SPACE = re.compile(r"[ \t]{2,}")
NL = re.compile(r"\n{3,}")

# The stale wiring: face crops described as the ONLY reference, i.e. the approved
# start photograph is not in the graph at all. Root cause of the ugly bodies
# (notes/body_quality_r3b_vs_r3r_20261023.md), so it must never reappear.
STALE = "only visual reference"
STALE_MUST_FIRE_ON = {"hc_r3_c0.txt", "hc_r4_c0.txt", "hc_r5_c0.txt", "hc_r6_c0.txt"}
STALE_MUST_NOT_FIRE_ON = {"hc_r1_c0.txt", "hc_r2_c0.txt", "hc_r3b_c0.txt"}

C0_SECTIONS = [
    "subject_definitions:",
    "summary:",
    "retention_analysis:",
    "detailed_description:",
    "overall_soundscape:",
    "non_diegetic_music:",
]
C1_SECTIONS = [
    "subject_definitions:",
    "integrated_multimodal_description:",
    "overall_soundscape:",
    "non_diegetic_music:",
]
# PQ1 asks for the beat by beat action with timing across the 10 s, and the MiniMax
# base guide (5.1) requires timecodes in first-pass description text.
TIMES = re.compile(r"\b\d{2}:\d{2}\b")
CLIPS = {
    "r1i": "51130001",
    "r2i": "51130002",
    "r3i": "51130003",
    "r4i": "51130004",
    "r5i": "51130005",
    "r6i": "51130006",
}
BLOCK = re.compile(r"^### id=(ali147_pool_hc_r\di_s\d{8}) chunk=(c[01]) seed=(\d{8})\s*$", re.M)
MIN_CHARS = {"c0": 5000, "c1": 4000}


def clean(chunk: str) -> str:
    txt = html.unescape(chunk)
    txt = txt.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    txt = txt.replace("</p>", "\n\n").replace("</li>", "\n")
    txt = TAG.sub(" ", txt)
    txt = html.unescape(txt)
    txt = SPACE.sub(" ", txt)
    txt = NL.sub("\n\n", txt)
    return txt.strip()


def prose_spans(h: str) -> list[str]:
    """Post bodies: from each class="prose" opening to the next post / article end.
    A plain non-greedy `.*?</div>` loses any post with a nested div (code, images),
    so the end is the next boundary, not the first closing tag."""
    starts = [m.end() for m in PROSE_START.finditer(h)]
    out = []
    for s in starts:
        ends = [x for x in (h.find('class="prose', s), h.find("</article>", s), s + 8000) if x > 0]
        out.append(h[s : min(ends)])
    return out


def civitai_texts(path: str) -> list[str]:
    """civitai /api/v1/models/<id> JSON: the card body is HTML in description and in
    media.images[].description; the rates[] review list is a separate endpoint.
    tags[] is a list of plain strings on /api/v1/models and of objects on /models/<id>,
    so take the name from either shape."""
    j = json.load(io.open(path, encoding="utf-8"))

    def tag_name(t) -> str:
        return t.get("name", "") if isinstance(t, dict) else str(t)

    out = [
        "[civitai model %s] %s | type %s | nsfw %s | tags %s"
        % (
            j.get("id"),
            j.get("name"),
            j.get("type"),
            j.get("nsfw"),
            ", ".join(tag_name(t) for t in j.get("tags", [])),
        )
    ]
    for key in ("shortDescription", "description"):
        if j.get(key):
            out.append(clean(j[key]))
    for img in (j.get("media") or {}).get("images", []):
        if img.get("description"):
            out.append("[image %s]\n%s" % (img.get("name"), clean(img["description"])))
    return [x for x in out if x.strip()]


def texts(path: str) -> list[str]:
    name = os.path.basename(path)
    if name.endswith(".txt") or name.endswith(".md"):
        return [io.open(path, encoding="utf-8", errors="replace").read()]
    if name.endswith(".json"):
        return civitai_texts(path)
    h = io.open(path, encoding="utf-8", errors="replace").read()
    parts = [clean(x) for x in prose_spans(h)]
    parts = [p for p in parts if len(p) > 40]
    if not parts:
        body = re.search(r"<body.*</body>", h, re.S)
        parts = [clean(body.group(0))] if body else []
    return parts


def root(path: str) -> str:
    base = os.path.basename(path)
    for ext in (".html", ".json", ".md", ".txt"):
        if base.endswith(ext):
            return os.path.join(os.path.dirname(path), base[: -len(ext)])
    return path


def extract_all() -> list[str]:
    sources = [
        f
        for f in (
            sorted(glob.glob(os.path.join(WEB, "pq1_minimax_*.txt")))
            + sorted(glob.glob(os.path.join(WEB, "pq1_tenstrip_d*.html")))
            + sorted(glob.glob(os.path.join(WEB, "pq1_civitai_model_*.json")))
        )
        if not f.endswith("_text.txt")  # never re-read our own output
    ]
    print(f"sources={len(sources)}")
    thin = []
    for f in sources:
        txt = "\n\n---- block ----\n\n".join(texts(f)).strip()
        out = root(f) + "_text.txt"
        io.open(out, "w", encoding="utf-8").write(txt + "\n")
        print(f"{os.path.basename(f)} -> {os.path.basename(out)} chars={len(txt)}")
        if len(txt) < 200:
            thin.append(os.path.basename(f))
    return thin


def check_im1(path: str) -> list[str]:
    """One block per IM1 render, with the sections, the timings and the new wiring."""
    if not os.path.exists(path):
        return [f"{os.path.basename(path)} does not exist yet"]
    md = io.open(path, encoding="utf-8", errors="replace").read()
    fails: list[str] = []
    marks = list(BLOCK.finditer(md))
    want = {f"ali147_pool_hc_{k}_s{v}" for k, v in CLIPS.items()}
    got = {m.group(1) for m in marks}
    if len(marks) != 12:
        fails.append(f"expected 12 prompt blocks (6 clips x c0 + c1), found {len(marks)}")
    for j in sorted(want - got):
        fails.append(f"missing prompt block for {j}")
    for j in sorted(got - want):
        fails.append(f"unexpected prompt block {j}")
    for n, m in enumerate(marks):
        jid, chunk, seed = m.group(1), m.group(2), m.group(3)
        end = marks[n + 1].start() if n + 1 < len(marks) else len(md)
        body = md[m.end() : end].strip()
        tag = f"{jid} {chunk}"
        if seed != CLIPS[jid.split("_")[-2]]:
            fails.append(f"{tag}: seed {seed} is not the round seed")
        if len(body) < MIN_CHARS[chunk]:
            fails.append(f"{tag}: only {len(body)} chars, PQ1 wants a long descriptive prompt (>= {MIN_CHARS[chunk]})")
        for s in (C0_SECTIONS if chunk == "c0" else C1_SECTIONS):
            if s not in body:
                fails.append(f"{tag}: missing the {s} section")
        seg = body[body.find("detailed_description:") :] if chunk == "c0" else body[body.find("integrated_multimodal_description:") :]
        if not TIMES.search(seg):
            fails.append(f"{tag}: no mm:ss beat timings in the description section")
        if STALE in body:
            fails.append(f"{tag}: carries the stale face-crop-only wiring ({STALE!r})")
        if chunk == "c0":
            for need in ("<Picture 1>", "<Subject 1>", "fictional adult", "body"):
                if need not in body:
                    fails.append(f"{tag}: c0 prompt never mentions {need}")
            if "wardrobe" not in body and "clothing" not in body:
                fails.append(f"{tag}: c0 prompt has no wardrobe/clothing description")
            if "lens" not in body:
                fails.append(f"{tag}: c0 prompt has no lens description")
    return fails


def main() -> int:
    thin = extract_all()

    hits = {}
    for p in sorted(glob.glob(os.path.join(NOTES, "hc_r*_c0.txt"))):
        hits[os.path.basename(p)] = io.open(p, encoding="utf-8", errors="replace").read().count(STALE)
    fired = {k for k, v in hits.items() if v}
    print("stale-wording hits:", json.dumps(hits, sort_keys=True))

    destruct = os.environ.get("PQ1_DESTRUCT", "").strip()
    if destruct:
        fails = check_im1(destruct)
        print(f"DESTRUCT target={os.path.basename(destruct)} fails={len(fails)}")
        for x in fails:
            print("  destruct fail:", x)
        if thin:
            print(f"PQ1 EXTRACT FAILED - no usable prose in {thin} - STOP_RALPH")
            return 1
        if fails:
            print("PQ1 DESTRUCT OK - the completeness check fails on the broken clone")
            return 0
        print("PQ1 DESTRUCT FAILED - the check cannot fail, it is worthless - STOP_RALPH")
        return 1

    fails = check_im1(IM1)
    print(f"im1_prompts.md fails={len(fails)}")
    for x in fails:
        print("  -", x)

    ok = True
    if thin:
        print(f"CHECK FAILED: no usable prose in {thin} - parser stale or page is a JS shell")
        ok = False
    if fired != STALE_MUST_FIRE_ON:
        print(f"CHECK FAILED: stale wording fired on {sorted(fired)}, expected exactly {sorted(STALE_MUST_FIRE_ON)}")
        ok = False
    for name in STALE_MUST_NOT_FIRE_ON:
        if hits.get(name, 0) != 0:
            print(f"CHECK FAILED: {name} carries the stale wiring wording")
            ok = False
    if fails:
        print("CHECK FAILED: im1_prompts.md is incomplete")
        ok = False
    if ok:
        print("PQ1 EXTRACT + IM1 PROMPT CHECK OK")
        return 0
    print("PQ1 EXTRACT / IM1 PROMPT CHECK FAILED - STOP_RALPH")
    return 1


if __name__ == "__main__":
    sys.exit(main())
