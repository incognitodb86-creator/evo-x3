#!/usr/bin/env python
"""TOP-SCENE step 1 + step 3 builder (ALI-163, HC15).

WHAT: (1) writes one scene card per HC15 START STILL, containing the measured
source facts + the vision model's OWN WORDS copied byte-for-byte out of the
captured stdout (notes/scenes/raw/<ID>[_2].txt), and (2) writes
notes/audits/2026-10-25-prompt-vs-image.md: every runs/*hc15*/request.api.json
prompt compared against the card for the still its LoadImage node points at.

NO RENDER, NO GPU, NO QUEUE. No vision model scores, ranks, judges or picks a
keeper here: the model READS a start still and says who is in it (fix_plan.md
item VIS: KEEP is Derrick's alone).

MODES
  --cards     write notes/scenes/<ID>.md            (idempotent, no timestamp of its own)
  --audit     write notes/audits/2026-10-25-prompt-vs-image.md
  --check     run every detector on the real tree, print PROBLEMS n + VERDICT
  --facts     print the card-derived fact census + the prompt-side census
  --selftest  seed each fault on a clone; the named detector MUST fire there and 0 on the real tree

CAPTION RUNS (measured in Git Bash, 2026-10-25, wall/rc recorded per run below):
  pi --print --provider llama-swap --model coding_swift15_iq3s --tools read \
     --no-session --no-context-files --no-skills --no-prompt-templates \
     --no-themes --no-mcp --thinking off "<ask>"
ask A (all 6 stills): "Use the read tool once on <abs still>. Then list every figure
 in frame - species/race, build, skin, hair colour, wardrobe, pose, position - then
 the room, the props and the light. Quote nothing you cannot see. No prose before it."
ask B (the 3 GI explicit frames, retry for the non-sexual fields): "... for EACH
 figure in frame state species as visible, build, skin tone, hair colour, the wardrobe
 items visible, and where it sits in the frame; then the room, the props and the light.
 Do not describe any sexual act, nudity, genitals, nipple/areola, erection, or body
 position during a sexual act. No prose before it."
Option (b) of fix_plan.md item TOP-SCENE step 1. WHY this option: pi 1.4.0 has no
image-generation tool and no OpenAI-shaped image_url client is wired in the community
scripts, so a nested `pi --print --tools read` run is the only on-box way to put a
start still in front of a vision model and keep its words. ask A returned a full
per-figure inventory for BD002/BD006/BD013; on the three explicit GI frames the model
refused the body catalogue and gave the figure count, species, room and light inside
the refusal, and ask B refused all three (recorded verbatim in the cards).
"""
import sys, os, re, json, glob, hashlib, argparse, copy, datetime

C = "C:/AI/community"
SCENES = C + "/notes/scenes"
AUDITS = C + "/notes/audits"
RAWDIR = SCENES + "/raw"
AUDIT_DOC = AUDITS + "/2026-10-25-prompt-vs-image.md"
MODEL = "llama-swap/coding_swift15_iq3s"
PI_FLAGS = ("pi --print --provider llama-swap --model coding_swift15_iq3s --tools read "
            "--no-session --no-context-files --no-skills --no-prompt-templates "
            "--no-themes --no-mcp --thinking off")
SESSION = "01a17267-3630-70f2-b245-8a4a843b81a3"
ASK_A = ("Use the read tool once on {src}. Then list every figure in frame - species/race, "
         "build, skin, hair colour, wardrobe, pose, position - then the room, the props and "
         "the light. Quote nothing you cannot see. No prose before it.")
ASK_B = ("Use the read tool once on {src}. Give only the non-sexual identity and composition "
         "record: for EACH figure in frame state species as visible, build, skin tone, hair "
         "colour, the wardrobe items visible, and where it sits in the frame; then the room, "
         "the props and the light. Do not describe any sexual act, nudity, genitals, "
         "nipple/areola, erection, or body position during a sexual act. No prose before it.")

AK = "C:/Users/derek/5slock/approved_characters"
STILLS = {
 "BD002": {"src": AK + "/FLOW_BLONDE_DARK_PAIRS_2026-10-19/BD002.jpg",
   "runs": [("BD002.txt", "A", 21, 0), ],
   "status": "FULL_INVENTORY",
   "facts": {
     "figures": 2, "fig_ev": ["**Figures (2)**", "**Figure 1 — left/centre**", "**Figure 2 — right/centre**"],
     "species": "2 human female-presenting adults (no non-human figure)", "sp_ev": ["human, female-presenting"],
     "non_human": False, "nh_ev": [],
     "hair": [("Subject 1", "dark blonde / dirty-blonde, darker roots", "dark blonde / dirty-blonde with darker roots"),
              ("Subject 2", "dark brown/black", "dark brown/black, wet-look")],
     "room": "no room: high-key white studio cyclorama, black side bars",
     "room_ev": ["Seamless high-key white studio backdrop/cyclorama"],
     "props": "one low cast-concrete block/bench", "props_ev": ["One low rectangular cast-concrete block/bench"],
     "light": "large soft frontal key, background clipped to white, magenta bounce off the vinyl",
     "light_ev": ["Large soft frontal key, high-key exposure"],
     "extra_ev": ["A third set of bottoms and a hand appear between them; which figure each limb belongs to is not resolvable"]}},
 "BD006": {"src": AK + "/FLOW_BLONDE_DARK_PAIRS_2026-10-19/BD006.jpg",
   "runs": [("BD006.txt", "A", 17, 0), ],
   "status": "FULL_INVENTORY",
   "facts": {
     "figures": 2, "fig_ev": ["**FIGURE 1 — reclining (left)**", "**FIGURE 2 — kneeling/leaning (right)**"],
     "species": "2 human female-presenting adults (no non-human figure)", "sp_ev": ["human, female-presenting"],
     "non_human": False, "nh_ev": [],
     "hair": [("Subject 1", "platinum/dirty blonde", "long platinum/dirty blonde, wavy"),
              ("Subject 2", "dark brown/near-black", "long dark brown/near-black, swept over one shoulder")],
     "room": "studio set: cream seamless backdrop, pale concrete pillar, black side flags",
     "room_ev": ["Interior studio set."],
     "props": "matte black plinths; magenta gauntlet glove with silver circuit motifs on Figure 2's hand",
     "props_ev": ["Glossy magenta-pink gauntlet glove with silver circuit motifs"],
     "light": "bright diffuse key front / slightly camera-left, hard speculars on oiled skin",
     "light_ev": ["Bright diffuse studio key from front and slightly camera-left"]}},
 "BD013": {"src": AK + "/FLOW_BLONDE_DARK_PAIRS_2026-10-19/BD013.jpg",
   "runs": [("BD013.txt", "A", 14, 0), ],
   "status": "FULL_INVENTORY",
   "facts": {
     "figures": 2, "fig_ev": ["**Figure 1 — front/left**", "**Figure 2 — behind/right**"],
     "species": "2 human female adults (no non-human figure)", "sp_ev": ["human, female;"],
     "non_human": False, "nh_ev": [],
     "hair": [("Subject 1", "blonde, wet", "blonde, wet, slicked back from the face"),
              ("Subject 2", "dark brown/black", "dark brown/black, wet, slicked back")],
     "room": "seamless white-to-light-grey studio cyclorama",
     "room_ev": ["Seamless white-to-light-grey studio cyclorama"],
     "props": "one low concrete ledge/plinth, black pillarbox bars",
     "props_ev": ["Single low concrete/cement ledge or plinth"],
     "light": "high-key, bright and even, soft frontal key, shadowless blown-out background",
     "light_ev": ["High-key studio lighting, bright and even, soft frontal key"]}},
 "GI046": {"src": AK + "/GROK_IMAGINE_2026-10-19/GI046.jpg",
   "runs": [("GI046.txt", "A", 14, 0), ("GI046_2.txt", "B", 9, 0)],
   "status": "REFUSAL_TRUNCATED",
   "facts": {
     "figures": 2, "fig_ev": ["Two figures."],
     "species": "1 human adult + 1 non-human humanoid (green-skinned, heavily muscled) = a two-figure start",
     "sp_ev": ["large, heavily muscled green-skinned figure in dark grey shorts", "no head"],
     "non_human": True, "nh_ev": ["green-skinned figure"],
     "hair": [("Subject 1", "blonde, long, wavy", "fair-skinned blonde person with long wavy hair")],
     "room": "interior living room: beige/tan sofa, dark hardwood floor, beige shag rug",
     "room_ev": ["Setting: interior living room."],
     "props": "sofa, shag rug", "props_ev": ["beige shag rug"],
     "light": "soft warm diffuse front-side, shallow depth of field",
     "light_ev": ["soft, warm, diffuse front-side lighting"],
     "extra_ev": ["I can't produce that inventory.", "The frame is explicit sexual imagery"]}},
 "GI063": {"src": AK + "/GROK_IMAGINE_2026-10-19/GI063.jpg",
   "runs": [("GI063.txt", "A", 12, 0), ("GI063_2.txt", "B", 14, 0)],
   "status": "REFUSAL_TRUNCATED",
   "facts": {
     "figures": 2, "fig_ev": ["a restrained person", "penetrated by a robot"],
     "species": "1 human adult + 1 robot (machine figure) = a two-figure start",
     "sp_ev": ["by a robot", "bound to a table (wrists chained, ankles in shackles)"],
     "non_human": True, "nh_ev": ["by a robot"],
     "hair": [("Subject 1", "blonde, long, wavy", "long wavy blonde hair, blue eyes, light complexion, slim build")],
     "room": "not resolvable from the caption (the model gave no room row)",
     "room_ev": ["I can't produce this record."],
     "props": "restraint hardware: wrists chained, ankles in shackles, table",
     "props_ev": ["wrists chained, ankles in shackles"],
     "light": "not resolvable from the caption", "light_ev": ["I can't produce that description."],
     "extra_ev": ["an anguished, distressed expression", "That's non-consensual sexual content."]}},
 "GI072": {"src": AK + "/GROK_IMAGINE_2026-10-19/GI072.jpg",
   "runs": [("GI072.txt", "A", 10, 0), ("GI072_2.txt", "B", 12, 0)],
   "status": "REFUSAL_TRUNCATED",
   "facts": {
     "figures": 2, "fig_ev": ["a person performing oral sex on another", "one figure performing oral sex on another using a strap-on"],
     "species": "2 human adults (no non-human figure)", "sp_ev": ["one figure performing oral sex on another"],
     "non_human": False, "nh_ev": [],
     "hair": [],
     "room": "outdoor campus pedestrian plaza: brick buildings, green trees, overcast daylight, pink neon strip, blurred pedestrians, 16:9 letterboxed",
     "room_ev": ["outdoor pedestrian plaza on a campus, brick buildings, green trees, overcast daylight"],
     "props": "pink metallic wardrobe palette, pink thigh-high patent boots, clear strappy heels",
     "props_ev": ["pink thigh-high patent boots, clear strappy heels"],
     "light": "overcast daylight, shallow depth of field, camera at kneeling height, 16:9 letterboxed",
     "light_ev": ["shallow depth of field, camera at kneeling height", "16:9 letterboxed"],
     "extra_ev": ["I can't produce that inventory.", "colour palette (pink metallics against muted brick and green)"]}},
}
ORDER = ["BD002", "BD006", "BD013", "GI046", "GI063", "GI072"]

SOLO_PAT = [r"the only person in that photograph", r"standing alone", r"the only person in frame",
            r"alone in the room", r"the only bodies in the shot"]
SPECIES_TOK = {"GI046": [r"\borc\b", r"green-skin", r"green skin", r"heavily muscled", r"tusks?"],
               "GI063": [r"\brobot\b", r"\bandroid\b", r"\bmachine\b", r"chrome", r"hydraulic"]}
HAIR_TOK = ["blonde", "platinum", "dark brown", "auburn", "ginger", "red-haired", "dark-haired", "black hair", "brunette"]
SCALES = ["head taller", "full head"]
RENDER_TOKENS = [r"\.mp4", r"ComfyUI/output", r"/frames/", r"_frame\d", r"contact sheet"]


def sha(b): return hashlib.sha256(b).hexdigest()


def rd(p):
    with open(p, "rb") as f: return f.read()


def fwd(p): return p.replace(chr(92), "/")


def raw_text(sid):
    """concatenated stdout of every caption run for this still, in run order."""
    parts = []
    for fn, ask, wall, rc in STILLS[sid]["runs"]:
        parts.append(rd(os.path.join(RAWDIR, fn)).decode("utf-8", "replace"))
    return "\n".join(parts)


def measure_src(sid):
    p = STILLS[sid]["src"]
    b = rd(p)
    return {"path": fwd(p), "bytes": len(b), "sha256": sha(b),
            "mtime": datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime("%Y-%m-%dT%H:%M:%S")}


def card_text(sid):
    st, m = STILLS[sid], measure_src(sid)
    f = st["facts"]
    L = ["# SCENE CARD %s - what the vision model sees in the START STILL %s" % (sid, sid),
         "",
         "start_still: " + m["path"],
         "start_still_bytes: %d" % m["bytes"],
         "start_still_sha256: " + m["sha256"],
         "start_still_mtime: " + m["mtime"],
         "vision_model: " + MODEL + " (pi 1.4.0, --tools read, --thinking off, --no-session, pass session " + SESSION + ")",
         "command: " + PI_FLAGS + ' "<ask>"',
         "caption_status: " + st["status"],
         "read_scope: the start still ONLY. No rendered clip, no frame of a render, no contact sheet.",
         "role: the model READS the still and lists what is in it. No score, no rank, no judgement, no keeper (KEEP is Derrick's alone).",
         "",
         "## facts read out of the model's own words (each cited verbatim below)"]
    L.append("figures: %d  <- %s" % (f["figures"], " | ".join('"%s"' % e for e in f["fig_ev"])))
    L.append("species: " + f["species"] + ("  <- " + " | ".join('"%s"' % e for e in f["sp_ev"]) if f.get("sp_ev") else ""))
    if f["hair"]:
        L.append("hair: " + "; ".join("%s = %s <- \"%s\"" % (a, b, c) for a, b, c in f["hair"]))
    else:
        L.append("hair: not reported by the model for this frame")
    L.append("room: " + f["room"] + "  <- " + " | ".join('"%s"' % e for e in f["room_ev"]))
    L.append("props: " + f["props"] + "  <- " + " | ".join('"%s"' % e for e in f["props_ev"]))
    L.append("light: " + f["light"] + "  <- " + " | ".join('"%s"' % e for e in f["light_ev"]))
    L.append("")
    for fn, ask, wall, rc in st["runs"]:
        b = rd(os.path.join(RAWDIR, fn))
        mt = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(RAWDIR, fn))).strftime("%Y-%m-%dT%H:%M:%S")
        L += ["## caption run %s" % fn,
              "ask: " + ("ask A" if ask == "A" else "ask B"),
              "prompt_sent: " + (ASK_A if ask == "A" else ASK_B).format(src=m["path"]),
              "run_finished_localtime: " + mt + "   (mtime of the captured stdout file)",
              "wall_seconds: %d (measured by the shell around the pi call)" % wall,
              "rc: %d" % rc,
              "stdout_bytes: %d" % len(b), "stdout_sha256: " + sha(b), ""]
    L += ["--- THE MODEL'S OWN WORDS, UNEDITED, BYTE-FOR-BYTE FROM STDOUT ---", ""]
    for fn, ask, wall, rc in st["runs"]:
        L += ["### %s" % fn, raw_text_run(fn), ""]
    return "\n".join(L).rstrip() + "\n"


def raw_text_run(fn):
    return rd(os.path.join(RAWDIR, fn)).decode("utf-8", "replace").rstrip()


def facts_dict():
    out = {}
    for sid in ORDER:
        f = STILLS[sid]["facts"]
        out[sid] = dict(facts=f, status=STILLS[sid]["status"], src=STILLS[sid]["src"],
                        source=measure_src(sid),
                        raws=[{"file": fn, "ask": ask, "wall_s": wall, "rc": rc,
                               "sha256": sha(rd(os.path.join(RAWDIR, fn))), "bytes": len(rd(os.path.join(RAWDIR, fn)))}
                              for fn, ask, wall, rc in STILLS[sid]["runs"]])
    return out


def prompt_census():
    """every runs/*hc15* dir with a request.api.json: which still, what the prompt claims."""
    rows = []
    for rd_ in sorted(glob.glob(C + "/runs/*hc15*")):
        req = os.path.join(rd_, "request.api.json")
        if not os.path.exists(req): continue
        g = json.loads(rd(req).decode("utf-8", "replace"))
        imgs = [n.get("inputs", {}).get("image") for n in g.values() if n.get("class_type") == "LoadImage"]
        prompts = [n["inputs"]["prompt"] for n in g.values()
                   if isinstance(n.get("inputs", {}).get("prompt"), str) and len(n["inputs"]["prompt"]) > 200]
        txt = "\n".join(prompts); low = txt.lower()
        still = next((str(i).split("/")[-1].split(".")[0] for i in imgs
                      if isinstance(i, str) and i.split("/")[-1].split(".")[0] in ORDER), None)
        subs = sorted(set(re.findall(r"<Subject\s*(\d+)>", txt)), key=int)
        row = {"dir": os.path.basename(rd_), "req": fwd(req), "still": still, "n_img": len(imgs),
               "imgs": [str(i) for i in imgs], "subs": subs, "n_sub": len(subs),
               "words": len(txt.split()),
               "solo": sorted({m for p in SOLO_PAT for m in re.findall(p, low)}),
               "species_hits": sorted({m for m in re.findall("|".join(SPECIES_TOK[still]), low)}) if still in SPECIES_TOK else [],
               "hair_hits": sorted({t for t in HAIR_TOK if t in low}),
               "scale_hits": sorted({m for m in SCALES if m in low}),
               "mp4": len(glob.glob(os.path.join(rd_, "*.mp4"))),
               "prompts": prompts}
        rows.append(row)
    return rows


def count_support(f):
    """does the cited evidence support the stated figure count? the model's own numerals
    ("Figures (2)", "Figure 1/2", "Two figures.") win; with no numeral in the cited words,
    one cited phrase per figure is required. A count that no citation supports = D5."""
    ev, n = f["fig_ev"], f["figures"]
    parsed = []
    spell = {"two": 2, "three": 3, "four": 4, "five": 5}
    for e in ev:
        for m in re.findall(r"Figures?\s*\((\d+)\)", e, re.I): parsed.append(int(m))
        for m in re.findall(r"Figures?\s*(\d+)", e, re.I): parsed.append(int(m))
        for w, v in spell.items():
            if re.search(r"\b%s\b" % w, e, re.I): parsed.append(v)
    if parsed: return n == max(parsed), "numerals " + str(sorted(set(parsed)))
    return n == len(ev), "%d cited phrases" % len(ev)


def classify(row):
    """defect flags = claims the prompt makes that the card's own words do not support.
    A card the model refused to finish (hair: []) cannot support a hair claim in EITHER
    direction, so it raises CARD_NO_HAIR_ROW (disclosure), never a defect."""
    f = STILLS[row["still"]]["facts"] if row["still"] in STILLS else None
    flags = []
    if not f: return ["NO_CARD"], []
    if f["figures"] >= 2 and row["n_sub"] < f["figures"]:
        flags.append("SOLO_PROMPT_ON_%d_FIGURE_START" % f["figures"])
    if f["figures"] >= 2 and row["solo"]:
        flags.append("SOLO_CLAIM_ON_%d_FIGURE_START" % f["figures"])
    if f["non_human"] and not row["species_hits"]:
        flags.append("SPECIES_ABSENT_FROM_PROMPT")
    card_hair = " ".join(b for _, b, _ in f["hair"]).lower()
    if f["hair"]:
        foreign = [t for t in row["hair_hits"] if t not in card_hair]
        if row["hair_hits"] and len(foreign) == len(row["hair_hits"]):
            flags.append("HAIR_NOT_IN_CARD:" + ",".join(foreign))
    elif row["hair_hits"]:
        flags.append("CARD_NO_HAIR_ROW")
    if row["scale_hits"] and any("no head" in e for e in f.get("sp_ev", [])):
        flags.append("SCALE_CLAIM_NO_HEAD_IN_CARD")
    return (flags or ["MATCH"]), [q for q in row["solo"] + row["species_hits"] + row["hair_hits"] + row["scale_hits"]]


# ---------- audit document ----------
def audit_text(runs=None, facts=None):
    runs = runs or prompt_census()
    facts = facts or facts_dict()
    stamp = "2026-10-25"
    L = ["# PROMPT vs IMAGE - HC15 / ALI-163 - %s" % stamp,
         "",
         "item TOP-SCENE steps 1+3. Built by `C:/AI/community/notes/hc15_scene_audit_build.py --audit`; re-run that command to reproduce every row.",
         "",
         "- image reader: `%s` via nested `pi --print --tools read --thinking off` (pi 1.4.0, provider llama-swap). The model READS a START STILL and lists the figures in it. No score, no rank, no judgement, no keeper: KEEP is Derrick's alone, and no rendered clip was opened by a model for this document." % MODEL,
         "- side B: every `runs/*hc15*/request.api.json` in the tree - the prose the 22 HC15 clips were queued with.",
         "- evidence: each fact quotes the card (`notes/scenes/<ID>.md`, whose body is the model's stdout byte-for-byte) and quotes the prompt clause. Detector `D5FACT_EVIDENCE` fails the build if any quoted string is not verbatim in the captured stdout.",
         "- scope: start stills under `C:/Users/derek/5slock/approved_characters/` only. A caption of a render is out of scope (fix_plan.md VIS).",
         "",
         "## 1. the card facts (what the picture actually contains)", "",
         "| still | figures | species | non-human figure | hair in the card | room | caption_status |",
         "|---|---|---|---|---|---|---|"]
    for sid in ORDER:
        f = facts[sid]["facts"]
        L.append("| %s | %d | %s | %s | %s | %s | %s |" % (
            sid, f["figures"], f["species"], "YES" if f["non_human"] else "no",
            "; ".join("%s=%s" % (a, b) for a, b, _ in f["hair"]) or "not reported (refused)",
            f["room"], facts[sid]["status"]))
    L += ["", "## 2. every prompt against its card", "",
          "| run | start still | card figures | subjects in prompt | solo claim | species words | card | verdict |",
          "|---|---|---|---|---|---|---|---|"]
    flagged = []
    for r in runs:
        fl, ev = classify(r)
        if fl != ["MATCH"]: flagged.append((r, fl, ev))
        L.append("| %s | %s | %s | %d (%s) | %s | %s | %s | %s |" % (
            r["dir"], r["still"] or "?", facts[r["still"]]["facts"]["figures"] if r["still"] in facts else "?",
            r["n_sub"], ",".join(r["subs"]) or "-",
            "; ".join(r["solo"]) or "none", "; ".join(r["species_hits"]) or "none",
            facts[r["still"]]["status"] if r["still"] in facts else "?", " + ".join(fl)))
    L += ["", "## 3. the mismatches, with the words that prove them", ""]
    for r, fl, ev in flagged:
        f = facts[r["still"]]["facts"]
        L.append("### %s (`%s`)" % (r["dir"], r["still"]))
        L.append("- verdict: " + " + ".join(fl))
        L.append("- the card: %d figures - %s" % (f["figures"], " ".join('"%s"' % e for e in f["fig_ev"])))
        L.append("- the card on species: " + f["species"] + " " + " ".join('"%s"' % e for e in f.get("sp_ev", [])))
        if f["hair"]:
            L.append("- the card on hair: " + "; ".join('"%s"' % c for _, _, c in f["hair"]))
        for q in r["solo"]:
            L.append('- the prompt says: "%s" (%d subjects named: %s)' % (q, r["n_sub"], ",".join(r["subs"])))
        if not r["species_hits"] and f["non_human"]:
            L.append("- the prompt names no non-human figure at all: 0 hits for " +
                     ", ".join("`%s`" % t for t in SPECIES_TOK[r["still"]]))
        if r["hair_hits"]:
            L.append("- hair words in the prompt: " + ", ".join('"%s"' % t for t in r["hair_hits"]) +
                     " - card: " + ("; ".join('"%s"' % c for _, _, c in f["hair"]) or
                                    "NO HAIR ROW: the model refused the attribute catalogue for this frame, "
                                    "so the card cannot confirm or contradict the prompt's hair words"))
        if "CARD_NO_HAIR_ROW" in fl:
            L.append("- disclosure: this card has no hair row (caption_status " + STILLS[r["still"]]["status"] +
                     "), so the prompt's hair words are UNVERIFIED here, not called a defect.")
        if r["scale_hits"]:
            L.append("- the prompt claims " + ", ".join('"%s"' % t for t in r["scale_hits"]) +
                     " while the card reports " + " ".join('"%s"' % e for e in f.get("sp_ev", [])))
        L.append("- rendered clips in that run dir: %d. This row is a defect list, not a keep/skip order." % r["mp4"])
        L.append("")
    L += ["## 4. needs-Derrick (the card changes a premise; not mine to resolve)", "",
          "- **GI063 consent read.** The card for GI063 reports the woman as restrained and in distress: "
          '"bound to a table (wrists chained, ankles in shackles)" and "an anguished, distressed expression", '
          'and the model reads the scene as "That\'s non-consensual sexual content.". The canon lock '
          "(C:/Users/derek/5slock/plans/canon/fiction-cond-lock.md) makes every character a fictional adult; "
          "a start still whose own caption is restraint-plus-distress cannot be written into an "
          "enthusiastic-consent scene by editing prose alone. Your call: replace the GI063 start still, "
          "or state how the scene treats it. Nothing in this pass edits the GI063 prompts.",
          "- **GI046 head/scale.** The card reports the second figure with NO head in frame "
          '("only its torso, arms, hands and legs are in frame - no head"), so a prompt that fixes his height '
          '("a full head taller") is inventing a fact the reference cannot support. s51150031/s51150032 carry that phrase.',
          "- **the armed p7 request cites a superseded probe.** p7/JOB_REQUEST.json (armed for GI046/GI063 "
          "s51150031/s51150032, untouched in this pass) cites `notes/hc15_gi_figures_2026-10-25.md`, whose green "
          "test measured 0.0000 at GI046. The vision read reports a green-skinned figure in the same frame, so "
          "that row measures the warm cast, not skin. The figures file is the monitor's artifact (not edited here); "
          "the card is the citation to use for species.",
          "- **caption reach.** ask A returned a full per-figure inventory for BD002/BD006/BD013 and, on the three "
          "explicit GI frames, refused the body catalogue while still naming the figure count, species, room and "
          "light. ask B (non-sexual fields only) was refused on all three GI frames. Both refusals are in the cards "
          "verbatim. So the cards are complete for the BD set and decisive-not-exhaustive for the GI set.",
          "", "## 5. sources", ""]
    for sid in ORDER:
        s = facts[sid]["source"]
        L.append("- start still %s: `%s` (%d bytes, sha256 %s)" % (sid, s["path"], s["bytes"], s["sha256"]))
        for r in facts[sid]["raws"]:
            L.append("  - caption stdout `notes/scenes/raw/%s` (%d bytes, sha256 %s, ask %s, wall %ds, rc %d)" %
                     (r["file"], r["bytes"], r["sha256"], r["ask"], r["wall_s"], r["rc"]))
    L += ["- cards: " + ", ".join("`notes/scenes/%s.md`" % s for s in ORDER),
          "- prompt side: " + "%d request.api.json files under `C:/AI/community/runs/*hc15*`" % len(runs),
          "- builder + detectors: `C:/AI/community/notes/hc15_scene_audit_build.py` (`--check`, `--selftest`)",
          "- canon lock: `C:/Users/derek/5slock/plans/canon/fiction-cond-lock.md`",
          "", "no render, no queue, no GPU call, no model verdict in this pass.", ""]
    return "\n".join(L)


# ---------- detectors ----------
def check(cards, audit, runs, facts, written=None, guard_fn=None):
    """cards: {id: text}. audit: doc text. runs: prompt census. facts: facts_dict().
    written: files this builder created (LITTER). guard_fn: comm.guard_ok or None."""
    p = []
    for sid in ORDER:
        t = cards.get(sid)
        if t is None:
            p.append(("D1CARD_MISSING", sid + ": notes/scenes/%s.md is absent" % sid)); continue
        body = t
        for fn, ask, wall, rc in STILLS[sid]["runs"]:
            w = raw_text_run(fn)
            if w not in body:
                p.append(("D1CARD_UNEDITED", "%s: the stdout of %s is not verbatim in the card - the model's words were edited" % (sid, fn)))
        if t != card_text(sid):
            p.append(("D1CARD_STALE", "%s: the card on disk differs from regenerated card bytes (drift or a hand-added line)" % sid))
        for probe in [STILLS[sid]["src"], "start_still_sha256: ", "stdout_sha256: ", "prompt_sent: ",
                      "run_finished_localtime: ", "wall_seconds: ", "rc: ", MODEL]:
            if probe not in t:
                p.append(("D2CARD_PROVENANCE", "%s: card carries no %r - no model id / command / timestamp / sha to re-run" % (sid, probe[:28])))
        m = measure_src(sid)
        if "start_still_bytes: %d" % m["bytes"] not in t or "start_still_sha256: " + m["sha256"] not in t:
            p.append(("D3SOURCE_SHA", "%s: card source bytes/sha do not match the bytes on disk now (%d, %s)" % (sid, m["bytes"], m["sha256"][:16])))
        if not STILLS[sid]["src"].startswith(AK) or not STILLS[sid]["src"].endswith(".jpg"):
            p.append(("D4CARD_SOURCE_STILL", "%s: card source %s is not an approved start still" % (sid, STILLS[sid]["src"])))
        for tok in RENDER_TOKENS:
            if re.search(tok, raw_text(sid), re.I):
                p.append(("D4CARD_SOURCE_STILL", "%s: a caption body references %s - the reader read a render, not the start still" % (sid, tok)))
        f = facts[sid]["facts"]
        if not (isinstance(f["figures"], int) and f["figures"] >= 1):
            p.append(("D5FACT_EVIDENCE", "%s: figure count is not a positive int" % sid))
        else:
            ok, why = count_support(f)
            if not ok:
                p.append(("D5FACT_EVIDENCE", "%s: facts claim %d figures, the cited words give %s - the count has no support in the model's words" % (sid, f["figures"], why)))
        for key in ["fig_ev", "sp_ev", "nh_ev", "room_ev", "props_ev", "light_ev", "extra_ev"]:
            for e in f.get(key, []):
                if e not in raw_text(sid):
                    p.append(("D5FACT_EVIDENCE", "%s: fact row cites %r which is NOT verbatim in the model's words" % (sid, e[:60])))
        for _, _, e in f["hair"]:
            if e not in raw_text(sid):
                p.append(("D5FACT_EVIDENCE", "%s: hair row cites %r which is NOT verbatim in the model's words" % (sid, e[:60])))
    dirs = {r["dir"] for r in runs}
    rows = re.findall(r"^\| (ali163_hc15_[^ ]+|hc15_[^ ]+) \|", audit, re.M)
    missing = sorted(dirs - set(rows))
    if missing:
        p.append(("D6RUN_COVERAGE", "%d request.api.json run(s) with no row in the audit doc: %s" % (len(missing), ", ".join(missing[:6]))))
    if len(rows) != len(set(rows)):
        p.append(("D6RUN_COVERAGE", "the audit doc carries a duplicate run row"))
    for r in runs:
        fl, ev = classify(r)
        if fl == ["MATCH"]: continue
        sec = re.search(r"### %s \([^\n]*\)\n(.*?)(?=\n### |\n## )" % re.escape(r["dir"]), audit, re.S)
        if not sec:
            p.append(("D7FLAGGED_LISTED", "%s flagged %s but the doc lists no mismatch section for it" % (r["dir"], "+".join(fl))))
        elif "the prompt says" not in sec.group(1) and "names no non-human" not in sec.group(1) \
                and "hair words in the prompt" not in sec.group(1) and "the prompt claims" not in sec.group(1):
            p.append(("D7FLAGGED_LISTED", "%s: mismatch section has no quoted prompt words" % r["dir"]))
    prose = "\n".join(l for l in audit.split("\n") if not l.startswith("> ") and not l.startswith("- the card")
                      and not l.startswith("- the prompt") and not l.startswith("- hair words")
                      and not l.startswith("- the model") and not l.startswith("  - caption stdout")
                      and not l.startswith("- start still"))
    for w in ["best", "keeper", "KEEP", "prettiest", "ugliest", "winner", "score", "ranking", "judged", "verdict: keep"]:
        for line in prose.split("\n"):
            if re.search(r"\b%s\b" % re.escape(w), line) and "no keeper" not in line and "No score, no rank" not in line \
                    and "no model verdict" not in line and "not a keep/skip" not in line:
                p.append(("D8KEEPWORD", "the doc prose carries the quality word %r: %s" % (w, line.strip()[:90])))
                break
    for cite in sorted(set(re.findall(r"C:/[A-Za-z0-9_./-]+", audit) + re.findall(r"C:/[A-Za-z0-9_./-]+", "".join(cards.values())))):
        if any(x in cite for x in ["<", "*", "%"]): continue
        if not os.path.exists(cite.rstrip(".,)")) and not glob.glob(cite.rstrip(".,)")):
            p.append(("D9BAD_CITE", "cited path does not exist on this box: " + cite))
    if guard_fn is not None:
        for r in runs:
            for pr in r["prompts"]:
                if not guard_fn(pr):
                    p.append(("D10GUARD", "%s: comm.guard_ok REJECTS a prompt in %s" % (r["dir"], r["req"])))
    else:
        p.append(("D10GUARD", "comm.guard_ok could not be imported - the adults gate did not run on any audited prompt"))
    if written is not None:
        for f_ in written:
            if not (f_.startswith(SCENES) or f_.startswith(AUDITS)):
                p.append(("D11LITTER", "the builder wrote outside notes/scenes and notes/audits: " + f_))
    return p


def guard_import():
    try:
        sys.path.insert(0, C + "/scripts")
        import comm
        return comm.guard_ok
    except Exception as e:
        print("guard import failed: %s" % e)
        return None


def load_cards():
    out = {}
    for sid in ORDER:
        p = os.path.join(SCENES, sid + ".md")
        if os.path.exists(p): out[sid] = rd(p).decode("utf-8", "replace")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cards", action="store_true")
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--facts", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    facts, runs, cards, written = facts_dict(), prompt_census(), {}, []
    if a.facts:
        print(json.dumps(facts, indent=2)[:4000])
        for r in runs:
            print("%-32s still=%-6s subs=%s solo=%s sp=%s hair=%s scale=%s -> %s" %
                  (r["dir"], r["still"], r["n_sub"], r["solo"], r["species_hits"], r["hair_hits"],
                   r["scale_hits"], "+".join(classify(r)[0])))
    if a.cards:
        for sid in ORDER:
            p = os.path.join(SCENES, sid + ".md")
            os.makedirs(SCENES, exist_ok=True)
            t = card_text(sid)
            if not os.path.exists(p) or rd(p) != t.encode("utf-8"):
                open(p, "w", encoding="utf-8", newline="\n").write(t)
            cards[sid] = t; written.append(p)
        print("cards: %d written" % len(cards))
    if a.audit:
        os.makedirs(AUDITS, exist_ok=True)
        t = audit_text(runs, facts)
        if not os.path.exists(AUDIT_DOC) or rd(AUDIT_DOC) != t.encode("utf-8"):
            open(AUDIT_DOC, "w", encoding="utf-8", newline="\n").write(t)
        written.append(AUDIT_DOC)
        print("audit: %s (%d B, %d run rows, %d flagged)" % (AUDIT_DOC, len(t), len(runs),
              sum(1 for r in runs if classify(r)[0] != ["MATCH"])))
    if a.check or not any([a.cards, a.audit, a.facts, a.selftest]):
        cards = cards or load_cards()
        audit = rd(AUDIT_DOC).decode("utf-8") if os.path.exists(AUDIT_DOC) else ""
        if not audit: print("PROBLEMS 1\n('D6RUN_COVERAGE', 'no audit doc on disk')")
        pr = check(cards, audit, runs, facts, written=None, guard_fn=guard_import())
        print("PROBLEMS %d" % len(pr))
        for c, m in pr[:25]: print("  (%r, %r)" % (c, m))
        print("VERDICT %s" % ("CLEAN" if not pr else "STOP_RALPH"))
    if a.selftest:
        art0 = {"cards": load_cards(),
                "audit": rd(AUDIT_DOC).decode("utf-8") if os.path.exists(AUDIT_DOC) else "",
                "facts": copy.deepcopy(facts), "runs": copy.deepcopy(runs), "written": []}
        restores = []

        def probe(name, mut, code):
            art = copy.deepcopy(art0)
            mut(art)
            pr = check(art["cards"], art["audit"], art["runs"], art["facts"],
                       written=art["written"], guard_fn=guard_import())
            for r_ in restores: r_()   # undo STILLS-level seeds only AFTER the check
            del restores[:]
            hits = [x for x in pr if x[0] == code]
            print(("  OK   " if hits else "  MISS ") + code + " <- " + name + (" | " + hits[0][1][:78] if hits else ""))
            return bool(hits)

        def m_src_to_mp4(a):
            mp = sorted(glob.glob(C + "/runs/*hc15*/*.mp4"))
            if not mp: return
            keep = STILLS["BD006"]["src"]
            STILLS["BD006"]["src"] = fwd(mp[0])
            restores.append(lambda: STILLS["BD006"].update(src=keep))

        mp = sorted(glob.glob(C + "/runs/*hc15*/*.mp4"))
        seeds = [
          ("edit one word inside the model's own words", "D1CARD_UNEDITED",
           lambda a: a["cards"].__setitem__("BD002", a["cards"]["BD002"].replace("**Figures (2)**", "**Figures (3)**"))),
          ("strip stdout_sha256 from a card", "D2CARD_PROVENANCE",
           lambda a: a["cards"].__setitem__("GI046", "\n".join(l for l in a["cards"]["GI046"].split("\n") if not l.startswith("stdout_sha256")))),
          ("corrupt a start-still sha256 in a card", "D3SOURCE_SHA",
           lambda a: a["cards"].__setitem__("BD013", a["cards"]["BD013"].replace("start_still_sha256: ", "start_still_sha256: 0f"))),
          ("build a card off a rendered clip " + (os.path.basename(mp[0]) if mp else "?"), "D4CARD_SOURCE_STILL", m_src_to_mp4),
          ("facts claim 1 figure, the cited words say two", "D5FACT_EVIDENCE",
           lambda a: a["facts"]["GI046"]["facts"].__setitem__("figures", 1)),
          ("drop one run's row from the audit doc", "D6RUN_COVERAGE",
           lambda a: a.__setitem__("audit", "\n".join(l for l in a["audit"].split("\n") if not l.startswith("| hc15_gi072_s51150006 |")))),
          ("drop a flagged run's mismatch section", "D7FLAGGED_LISTED",
           lambda a: a.__setitem__("audit", re.sub(r"### ali163_hc15_gi046_s51150004 \([^#]*?(?=\n### )", "", a["audit"], flags=re.S))),
          ("put the quality words best/keeper in the doc prose", "D8KEEPWORD",
           lambda a: a.__setitem__("audit", a["audit"].replace("## 3. the mismatches", "## 3. the mismatches\n\nThe best clip of the set is the keeper."))),
          ("cite a notes file that is not on this box", "D9BAD_CITE",
           lambda a: a.__setitem__("audit", a["audit"].replace("## 5. sources", "## 5. sources\n\n- see C:/AI/community/notes/does_not_exist_2026-10-25.md"))),
          ("seed a prompt the adults gate (comm.guard_ok) rejects", "D10GUARD",
           lambda a: a["runs"][0]["prompts"].append("a barely legal teen schoolgirl in the room of picture 1")),
          ("builder writes a file outside notes/scenes and notes/audits", "D11LITTER",
           lambda a: a["written"].append(C + "/notes/stray_litter_2026-10-25.md")),
        ]
        bad = []
        for nm, code, fn in seeds:
            if code == "D4CARD_SOURCE_STILL" and not mp:
                print("  SKIP D4CARD_SOURCE_STILL: no rendered mp4 under runs/*hc15*"); continue
            if not probe(nm, fn, code): bad.append(code)
        pr = check(art0["cards"], art0["audit"], art0["runs"], art0["facts"],
                   written=art0["written"], guard_fn=guard_import())
        print("real tree PROBLEMS %d (must be 0: every detector quiet on the real artifacts)" % len(pr))
        for c_, m_ in pr[:12]: print("   ", c_, m_[:110])
        print("SEEDS %d/%d FIRED  SELFTEST %s" % (len(seeds) - len(bad), len(seeds),
              "PASS" if not bad and not pr else "FAIL " + ",".join(bad) + (" realtree=%d" % len(pr) if pr else "")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
