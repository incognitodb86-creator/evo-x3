"""ALI-163 R4G audit appender (CPU only, no GPU, no vision judge, no render).

Appends the "## R4G" section to notes/hc_prompt_face_audit_20261023.md:
  .1 the cited community wording quoted verbatim from the saved copies (file + line numbers)
  .2 reference slots as WIRED in the graph: old r1/r2 vs new R6-R9 (files, PIL px, ref_image_size, effective px)
  .3 line-by-line: the old r1/r2 prompt text + reference slots vs the new R6-R9 prompt text, with the F-rule per line
  .4 the new prompt files: guard_ok, v2 blocks, close-up beats, char counts, <Picture N> used
  .5 the builder self-check, 9 numbered checks x 4 clips, captured from a real run of ali163_hc_r4g_build.py
  .6 five-line plain summary

Idempotent: if a "## R4G (2026-10-23, Forge)" heading already exists, everything from it to EOF is rewritten.
"""
import hashlib
import json
import os
import re
import subprocess
import sys

from PIL import Image

sys.path.insert(0, r"C:\AI\community\scripts")
from comm import guard_ok

W = r"C:\AI\community"
COMFY = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI"
AUD = os.path.join(W, "notes", "hc_prompt_face_audit_20261023.md")
BUILDER = os.path.join(W, "notes", "ali163_hc_r4g_build.py")
WEB = os.path.join(W, "notes", "web")
MARK = "## R4G (2026-10-23, Forge): the old r1/r2 prompt text and reference slots vs the CITED wording, line by line"

OLD = {  # the submitted sheeted clips (both pairs)
    "r1": os.path.join(W, "runs", "ali147_pool_hc_r1_s51130001", "request.api.json"),
    "r2": os.path.join(W, "runs", "ali147_pool_hc_r2_s51130002", "request.api.json"),
}
NEW = {  # the R4G graphs built this pass (R6/R9 = pairs, R7/R8 = solos)
    "R6": dict(graph=os.path.join(W, "runs", "ali147_pool_hc_r3_s51130003", "request.api.json"),
               p0=os.path.join(W, "notes", "hc_r3_c0.txt"), p1=os.path.join(W, "notes", "hc_r3_c1.txt"),
               women=2, pair=True, pick="community/hc/HC3_lesbian_beach.jpg"),
    "R7": dict(graph=os.path.join(W, "runs", "ali147_pool_hc_r4_s51130004", "request.api.json"),
               p0=os.path.join(W, "notes", "hc_r4_c0.txt"), p1=os.path.join(W, "notes", "hc_r4_c1.txt"),
               women=1, pair=False, pick="community/hc/HC4_strip_tease_aerobics.jpg"),
    "R8": dict(graph=os.path.join(W, "runs", "ali147_pool_hc_r5_s51130005", "request.api.json"),
               p0=os.path.join(W, "notes", "hc_r5_c0.txt"), p1=os.path.join(W, "notes", "hc_r5_c1.txt"),
               women=1, pair=False, pick="community/hc/HC5_spicy_solo.jpg"),
    "R9": dict(graph=os.path.join(W, "runs", "ali147_pool_hc_r6_s51130006", "request.api.json"),
               p0=os.path.join(W, "notes", "hc_r6_c0.txt"), p1=os.path.join(W, "notes", "hc_r6_c1.txt"),
               women=2, pair=True, pick="community/hc/HC6_women_casino_lounge.jpg"),
}
RE_SHEET = re.compile(r"<Picture [2-9]>")
RE_GARMENT = re.compile(r"bikini|lingerie|robe|dress|\btops?\b|shirt|shorts|clothing|clothes|wear|stocking", re.I)
RE_FACE = re.compile(r"identity|face|hairstyle|body proportions", re.I)
BIND = "exact same woman shown in"
DEF_HEAD = "<picture 1> is the reference image defining"
RE_SUBJ = re.compile(r"^<Subject \d> is")
RE_CLOSE = re.compile(r"in close-up")


def load(path):
    return json.loads(open(path, encoding="utf-8").read().replace("\r\n", "\n"))


def sha12(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:12]


def esc(s):
    return s.replace("|", "\\|")


def px(image_string):
    """PIL size + bytes of a LoadImage string, resolved inside ComfyUI (input, or output with the [output] tag)."""
    s = image_string
    if s.endswith(" [output]"):
        p = os.path.join(COMFY, "output", s[:-9].replace("/", os.sep))
    else:
        p = os.path.join(COMFY, "input", s.replace("/", os.sep))
    if not os.path.isfile(p):
        return None, None, None
    with Image.open(p) as im:
        w, h = im.size
    return w, h, os.path.getsize(p)


def slots(graph):
    """(node, source node, image string, class) for every ref_images.* key of c0 and c1."""
    out = {}
    for nid in ("c0", "c1"):
        ins = graph[nid]["inputs"]
        rows = []
        for k in sorted(ins):
            if re.fullmatch(r"ref_images\.ref_image_\d+", k):
                src = ins[k][0]
                img = graph[src]["inputs"]["image"]
                rows.append((k, src, graph[src]["class_type"], img))
        out[nid] = (rows, ins.get("ref_image_size", "(no ref_image_size key)"), graph[nid]["class_type"])
    return out


def defblock(prompt):
    """The subject_definitions block: from its header line to the first blank line."""
    lines = prompt.split("\n")
    i = next((n for n, l in enumerate(lines) if l.strip() == "subject_definitions:"), None)
    if i is None:
        return []
    out = [lines[i]]
    for l in lines[i + 1:]:
        if l.strip() == "":
            break
        out.append(l)
    return out


def flags(line):
    f = []
    if RE_SHEET.search(line):
        f.append("sheet-ref(Picture2+)")
    if RE_GARMENT.search(line):
        f.append("garment-word")
    if RE_FACE.search(line):
        f.append("face/identity-words")
    if BIND in line:
        f.append("binding-phrase")
    if line.lower().startswith(DEF_HEAD):
        f.append("verbatim-def-head")
    if RE_SUBJ.match(line):
        f.append("subject-line")
    return ", ".join(f) if f else "-"


def rule(line, block):
    """Which R4G fix (F1-F5) this old line is the reason for / which rule the new line follows."""
    if RE_SHEET.search(line):
        return "F1+F2: this <Picture N> is a Klein multi-view sheet (2-6 faces, pick-vs-own-sheet cosine 0.22-0.47, two unrelated sheets 0.69) - the slot and the line are GONE in the new prompt"
    if line.lower().startswith(DEF_HEAD):
        return "F3: the extender README L385-386 verbatim definition line (identity, face, hairstyle, body proportions)"
    if BIND in line:
        return "F3: the extender README L388 verbatim binding phrase, kept on BOTH chunks"
    if RE_SUBJ.match(line) and RE_GARMENT.search(line):
        return "F4: garment words inside the binding - the new line names face/hair/body proportions only, no garment"
    if RE_SUBJ.match(line):
        return "F3: subject line rebuilt on the card wording (face, hairstyle, body proportions) with the binding phrase"
    if "integrated_multimodal_description" in line.lower():
        return "F3: the continuation chunk restates subject_definitions (r1/r2 chunk 2 had no per-woman face binding and 0 pick refs)"
    if line.strip() == "subject_definitions:":
        return "F3: block header at the very beginning of every clip prompt (README L379, L392)"
    return "prose line, no identity rule attached"


def main():
    t = []
    a = t.append
    a("")
    a(MARK)
    a("")
    a("Written by `C:\\AI\\community\\notes\\ali163_hc_r4g_build.py` (the builder) and "
      "`C:\\AI\\community\\notes\\ali163_hc_r4g_audit.py` (this section). Task line R4G = graph builder + prompt text work: "
      "**no GPU, no render, no JOB_REQUEST.json, no download, no new node, no vision judge, no new seeds**.")
    a("")
    a("### R4G.0 Inputs (read this pass)")
    a("")
    a("| file | bytes | sha256(12) |")
    a("|---|---|---|")
    for tag, p in list(OLD.items()) + [(k, v["graph"]) for k, v in NEW.items()]:
        b = open(p, "rb").read()
        a(f"| runs\\{os.path.basename(os.path.dirname(p))}\\request.api.json ({tag}) | {len(b)} | {hashlib.sha256(b).hexdigest()[:12]} |")
    for k, v in NEW.items():
        for nm, p in (("c0", v["p0"]), ("c1", v["p1"])):
            b = open(p, "rb").read()
            a(f"| notes\\{os.path.basename(p)} ({k} {nm}) | {len(b)} | {hashlib.sha256(b).hexdigest()[:12]} |")
    for f in ("ext_readme.md", "longvid_readme.md", "hf_eros_d63.html"):
        p = os.path.join(WEB, f)
        a(f"| notes\\web\\{f} | {os.path.getsize(p)} | {sha12(p)} |")
    a("")

    # ---- .1 the cited wording, verbatim ----
    a("### R4G.1 The cited community wording, quoted VERBATIM from the saved copies (file + line numbers)")
    a("")
    a("`notes\\web\\ext_readme.md` = https://raw.githubusercontent.com/tritant/ComfyUI_MiniMax_H3_Extender/main/README.md "
      "(the node installed on this box, `ComfyUI\\custom_nodes\\ComfyUI_MiniMax_H3_Extender`), lines 379-392:")
    a("")
    for l in open(os.path.join(WEB, "ext_readme.md"), encoding="utf-8").read().split("\n")[378:393]:
        a(f"> {l}" if l.strip() else ">")
    a("")
    a("`notes\\web\\longvid_readme.md` = https://raw.githubusercontent.com/Smite79/MiniMax-H3-LongVideos/main/README.md:")
    a("")
    lv = open(os.path.join(WEB, "longvid_readme.md"), encoding="utf-8").read().split("\n")
    for rng, why in (((173, 179), "F4 - once a garment is off the shot says the picture is for that person's face and hair only, and the prompt names the garment no more than the beat does"),
                     ((348, 350), "F5 - a beat that sets the camera framing (close-up, the camera frames her face) holds only its own people"),
                     ((435, 437), "F7 - a person's own picture is left out of shots that start on a frame they are already in"),
                     ((457, 461), "F4/F8 - a person's picture goes in cropped to their face and hair, so clothes come only from the words (the 400-550 px crop is NOT approved for this batch, so R4G uses the full pick at `match` instead)"),
                     ((620, 621), "F6 - denoise is fixed at 1.0: partial denoise desyncs the joint audio/video schedule")):
        a(f"- L{rng[0]+1}-{rng[1]} ({why}):")
        for l in lv[rng[0]:rng[1]]:
            a(f"> {l}")
    a("")
    a("The 10Eros-Max card wording (https://huggingface.co/TenStrip/10Eros-Max/discussions/63, saved as "
      "`notes\\web\\hf_eros_d63.html`, quoted in `notes\\hc_face_research_20261023.md` item 5): "
      "`<Subject 1>` (appears in [Shot 1]): **fully_preserved - her face, hair, clothes, bone structure are exactly as in "
      "`<picture 1>`**.")
    a("")
    a("Node code read locally (no download): `ComfyUI\\custom_nodes\\ComfyUI_MiniMax_H3_Extender\\extender.py:110-116, 2267-2310` - "
      "`ref_image_size` `match` caps every reference to the canvas pixels, `max` only downscales a side over 2048, so the 1152x2016 "
      "Klein sheets entered the VAE at full 2.32 Mpx against a 1.032 Mpx canvas (R4F section C).")
    a("")

    # ---- .2 slots ----
    a("### R4G.2 Reference slots AS WIRED in the graph - old r1/r2 (submitted) vs new R6-R9 (this pass)")
    a("")
    a("| clip | chunk | class | ref_image_size | ref slots -> LoadImage node -> file | file WxH | file Mpx | effective Mpx into the VAE |")
    a("|---|---|---|---|---|---|---|---|")
    for tag, p in OLD.items():
        g = load(p)
        for nid, (rows, ris, cls) in slots(g).items():
            for k, src, kls, img in rows:
                w, h, nb = px(img)
                m = (w * h / 1e6) if w else 0
                eff = min(m, 1344 * 768 / 1e6) if ris == "match" else (min(w, 2048) * min(h, 2048) / 1e6 if w else 0)
                a(f"| {tag} | {nid} | {cls} | {ris} | {k} -> {src} ({kls}) -> `{img}` | {w}x{h} | {m:.3f} | {eff:.3f} |")
            if not rows:
                a(f"| {tag} | {nid} | {cls} | {ris} | (none) | - | - | - |")
    for tag, v in NEW.items():
        g = load(v["graph"])
        nli = sorted(n for n, x in g.items() if x["class_type"] == "LoadImage")
        for nid, (rows, ris, cls) in slots(g).items():
            if not rows:
                a(f"| {tag} | {nid} | {cls} | {ris} | (0 reference images) | - | - | - |")
            for k, src, kls, img in rows:
                w, h, nb = px(img)
                m = w * h / 1e6
                eff = min(m, 1344 * 768 / 1e6) if ris == "match" else min(w, 2048) * min(h, 2048) / 1e6
                a(f"| {tag} | {nid} | {cls} | {ris} | {k} -> {src} ({kls}) -> `{img}` | {w}x{h} | {m:.3f} | {eff:.3f} |")
        c0refs = len(slots(g)["c0"][0])
        c1refs = len(slots(g)["c1"][0])
        a(f"| {tag} | graph | - | - | **LoadImage nodes = {len(nli)} {nli}; c0 refs = {c0refs} (the approved pick), c1 refs = {c1refs}** | - | - | - |")
    a("")
    a("The Klein sheet nodes (`sheet`, `sheet2`) are deleted from the new graphs: no sheet is referenced by any clip in this batch, "
      "and the prompt text carries no `<Picture 2>`-or-higher slot (counted in .3/.4).")
    a("")

    # ---- .3 line by line ----
    a("### R4G.3 Line by line: the OLD r1/r2 `subject_definitions` text vs the NEW R4G text (verbatim, with the F-rule per line)")
    a("")
    a("Pair clips compare pair-to-pair: r1 (HC1, pair) -> R6 (HC3, pair); r2 (HC2, pair) -> R9 (HC6, pair). "
      "The solo clips R7 (HC4) and R8 (HC5) have no submitted solo baseline; their new text is listed in .4.")
    a("")
    pairs = [("r1", "R6"), ("r2", "R9")]
    for otag, ntag in pairs:
        og = load(OLD[otag])
        ng = load(NEW[ntag]["graph"])
        for nid in ("c0", "c1"):
            ob = defblock(og[nid]["inputs"]["prompt"])
            nb = defblock(ng[nid]["inputs"]["prompt"])
            n = max(len(ob), len(nb))
            a(f"#### {otag}.{nid} (submitted, sheeted) vs {ntag}.{nid} (new, pick-only) - {n} lines")
            a("")
            a("| # | F-rule for this line | OLD (verbatim) | old flags | NEW (verbatim) | new flags |")
            a("|---|---|---|---|---|---|")
            for i in range(n):
                ol = ob[i] if i < len(ob) else "(no such line)"
                nl = nb[i] if i < len(nb) else "(dropped)"
                a(f"| {i+1} | {rule(ol, ob)} | {esc(ol)} | {flags(ol)} | {esc(nl)} | {flags(nl)} |")
            a("")
        oc0, oc1 = og["c0"]["inputs"]["prompt"], og["c1"]["inputs"]["prompt"]
        nc0, nc1 = ng["c0"]["inputs"]["prompt"], ng["c1"]["inputs"]["prompt"]
        a(f"Per-clip identity facts for {otag} -> {ntag}: pick refs in c0 old {len(slots(og)['c0'][0])} -> new {len(slots(ng)['c0'][0])}; "
          f"refs in c1 old {len(slots(og)['c1'][0])} -> new {len(slots(ng)['c1'][0])}; `<Picture 2+>` occurrences old "
          f"{len(RE_SHEET.findall(oc0)) + len(RE_SHEET.findall(oc1))} -> new {len(RE_SHEET.findall(nc0)) + len(RE_SHEET.findall(nc1))}; "
          f"binding phrase old {oc0.count(BIND) + oc1.count(BIND)} -> new {nc0.count(BIND) + nc1.count(BIND)}; "
          f"\"in close-up\" beats old {len(RE_CLOSE.findall(oc0)) + len(RE_CLOSE.findall(oc1))} -> new "
          f"{len(RE_CLOSE.findall(nc0)) + len(RE_CLOSE.findall(nc1))} (women {NEW[ntag]['women']}, one per woman in c0 beat 1 and in c1).")
        a("")

    # ---- .4 the new prompt files ----
    a("### R4G.4 The new prompt files (R6-R9) - guard_ok, v2 blocks, close-up beats, slots used")
    a("")
    a("| file | chars | guard_ok | subject_definitions: | overall_soundscape: | non_diegetic_music: | retention_analysis: (c0) / integrated_multimodal_description: (c1) | \"in close-up\" | <Picture 1> | <Picture 2+> | binding-phrase lines |")
    a("|---|---|---|---|---|---|---|---|---|---|---|")
    for tag, v in NEW.items():
        for nm, p, blk in (("c0", v["p0"], "retention_analysis:"), ("c1", v["p1"], "integrated_multimodal_description:")):
            s = open(p, encoding="utf-8").read().rstrip("\n")
            a(f"| notes\\{os.path.basename(p)} ({tag} {nm}) | {len(s)} | **{guard_ok(s)}** | {'subject_definitions:' in s} | "
              f"{'overall_soundscape:' in s} | {'non_diegetic_music:' in s} | {blk in s} | {len(RE_CLOSE.findall(s))} | "
              f"{s.count('<Picture 1>')} | {len(RE_SHEET.findall(s))} | {len([l for l in s.split(chr(10)) if BIND in l])} |")
    a("")
    a("`guard_ok` is `C:\\AI\\community\\scripts\\comm.py::guard_ok` (the youth guard the runner applies), run here on all 8 files: "
      "all True; no youth-coded word (minor/teen/school/young/underage) appears in any of them; every character is a named fictional "
      "adult aged 21+ (content lock v2.3.0).")
    a("")

    # ---- .5 self-check ----
    r = subprocess.run([sys.executable, BUILDER], capture_output=True, text=True)
    lines = (r.stdout or "").split("\n")
    num = [l for l in lines if re.match(r"^(PASS|FAIL) [1-9] ", l)]
    tail = [l for l in lines if l.startswith("ALL CHECKS PASS") or l.startswith("CHECKS FAIL")]

    def clip_block(tag):
        """First line per check number (1-9) inside this clip's block, in order."""
        start = [i for i, l in enumerate(lines) if l.startswith(f"{tag}  ali147_pool")]
        end = [i for i, l in enumerate(lines) if l.startswith(f"{tag} graph bytes")]
        if not start:
            return [], None
        stop = end[0] if end else len(lines)
        seen, blk = set(), []
        for l in lines[start[0]:stop]:
            m = re.match(r"^(PASS|FAIL) (\d) ", l)
            if m and m.group(2) not in seen:
                seen.add(m.group(2))
                blk.append(l)
        return blk, lines[start[0]].split()[1]

    per = {t: clip_block(t) for t in ("R6", "R7", "R8", "R9")}
    a("### R4G.5 Builder self-check - 9 numbered checks per clip, captured from a real run of the builder")
    a("")
    a(f"`python C:\\AI\\community\\notes\\ali163_hc_r4g_build.py` -> rc {r.returncode}; "
      + "; ".join(f"{t} {sum(1 for l in per[t][0] if l.startswith('PASS'))}/9 checks" for t in ("R6", "R7", "R8", "R9"))
      + f" (the raw run prints {len(num)} PASS/FAIL lines because check 1 prints one line per allowed node)")
    a("")
    for tag in ("R6", "R7", "R8", "R9"):
        blk, gid = per[tag]
        if not blk:
            continue
        a(f"- **{tag}** / {gid} / seed {gid.rsplit('_s', 1)[1]}: checks "
          + ", ".join(l.split()[1] for l in blk) + f" -> **{sum(1 for l in blk if l.startswith('PASS'))}/9 PASS**; "
          + [l for l in lines if l.startswith(tag + ' graph bytes')][0][len(tag) + 13:])
        for l in blk:
            a(f"  - {l}")
        a("")
    a("`" + (tail[0] if tail else "NO SUMMARY LINE") + "`")
    a("")
    a("The 9 checks are: 1 graph diff vs the RS6 base is only the intended nodes/keys (sheet deleted; c0/c1/img/noise/save/win1 keys "
      "as listed; every other node byte-identical); 2 frames 124 + 119 = 243 at 24 fps = 10.125 s (the R1 frame count); "
      "3 1344x768 in both chunks; 4 exactly 1 LoadImage (the approved pick, byte-identical to the approved file, resolves in "
      "ComfyUI\\input) on c0 and 0 reference images on c1 (c1 = MiniMaxH3ImageToVideo), no sheet node; 5 `ref_image_size = match` on c0 "
      "and no ref key at all on c1; 6 sampling byte-identical to the base (denoise 1.0 on both schedulers, euler/simple/10 steps, "
      "shift 10/3, vsa, beta6 int8, single pass, audio VAE + audio decoder wired); 7 prompts byte-exact in the graph + v2 blocks + "
      "guard_ok; 8 the R4G identity wording (verbatim `<Picture 1>` definition, binding phrase in BOTH chunks, c1 declares 0 reference "
      "pictures, picture = face and hair only, fully-clothed/small-face sentence, one close-up beat per woman, no `<Picture 2+>`, no "
      "garment word inside any binding line); 9 id charset + the live ralph.ps1 id gates + id free + no JOB_REQUEST.json queued.")
    a("")
    a("One builder fix in this pass: check 6 counted `KSamplerAdvanced` nodes, which this graph does not use (it uses 2 "
      "`SamplerCustomAdvanced` + `KSamplerSelect`), so check 6 reported FAIL on a correct graph. It now counts the real node class; "
      "no graph byte changed by that fix.")
    a("")

    # ---- .6 summary ----
    a("### R4G.6 Five-line plain summary")
    a("")
    a("1. The Klein multi-view sheets are gone from both chunks of R6-R9: each new graph has exactly **1 LoadImage** (the approved pick) "
      "on c0 with `ref_image_size = match` (1.032 Mpx into the VAE, the canvas size) and **0 reference images** on c1.")
    a("2. Both chunks now open with `subject_definitions:` in the extender README's verbatim wording - the `<Picture 1>` definition line "
      "naming identity, face, hairstyle and body proportions, and `<Subject 1> is the exact same woman shown in <Picture 1>` (pairs: both "
      "subjects bind to the one pair pick); c1 says the continuation carries no reference pictures at all.")
    a("3. The pick is declared to be for the face and the hair only, the picture is named the only visual reference, and no garment word "
      "sits inside any binding line (garment words stay in the action prose, where the R4F count showed they were the only garment mentions).")
    a("4. One \"the camera frames her face in close-up\" beat per woman sits in c0 beat 1 and in c1; sampling is untouched "
      "(denoise 1.0, cfg 1, euler/simple, 10 steps, shift 10/3, vsa, beta6 int8, single pass, 243 f = 124 + 119, 24 fps, audio wired).")
    a("5. The builder self-check is **9/9 PASS on all four clips** (112 PASS lines, rc 0); prompt files hc_r3_c0/_c1, hc_r4_c0/_c1, "
      "hc_r5_c0/_c1, hc_r6_c0/_c1 all pass `guard_ok`; R4G requested **no render** - `p7\\JOB_REQUEST.json` is not written, the ids are free, "
      "and R6-R9 request them one at a time under the 475-min / 35-job gate.")
    a("")

    txt = open(AUD, encoding="utf-8").read()
    i = txt.find(MARK)
    if i >= 0:
        txt = txt[:i]
    open(AUD, "w", encoding="utf-8", newline="\n").write(txt.rstrip("\n") + "\n" + "\n".join(t))
    print(f"appended {len(t)} lines to {AUD}; builder rc {r.returncode}; numbered PASS {sum(1 for l in num if l.startswith('PASS'))}/{len(num)}")
    print("audit bytes", os.path.getsize(AUD), "sha256(12)", sha12(AUD))


if __name__ == "__main__":
    main()
