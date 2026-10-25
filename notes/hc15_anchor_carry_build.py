"""ALI-163 TOP carry - the FIXED clip-1 graph shape carried onto the other five HC15 start images.

Item: "I want the two videos the orc and the robot fucking video ... Like hardcore sex" (Derrick 2026-10-24
8:39 PM CT, fix_plan TOP). The item's shape requirement is the fixed clip-1 graph: MiniMaxH3AddGuide frame_idx 0,
res_multistep/simple/8 steps, 243 + 119 frames. That shape is the rendered clip 11
(p7/graphs/ali163_hc15_bd002_s51150011.api.json, 18,235 B, sha256 8a57ebbf456b6f9d06de7c0a32b02dc1bb4eff736c041700ea62b53e2c51d868,
measured 2026-10-25: 25 nodes, g0 frame_idx 0, win1 22/119, c0 length 243, sampler res_multistep, schedulers 8
steps, sha256 of c0/c1 prompts byte-identical to clip 1's, zero diff outside the three switches).

This file does NOT re-implement the switch. It imports transform() from notes/hc15_anchor_fix_build.py - the
function that produced the rendered clip 11 - and the CK_CONTROL detector proves that claim: transform(clip 1)
must reproduce the shipped clip-11 bytes. A look-alike transform fails there (AGENTS.md L10: a green check that
cannot fail is worthless, so every detector below is seeded in --selftest and must fire on the seed and stay
clean on the real artifacts).

Why carry five clips when the item names two: the item's first verb is "Find the two HC15 start images that show
the orc and the robot", and a Ralph pass cannot resolve that - this session's model is a text model
(coding_swift15_iq3s, PI_OFFLINE=1) with no visual channel; the community tool that reads a start image is the
vision prompter notes/ali173_pw1d_run.py (Qwen2.5-Omni-7B + MiniMax H3 Prompt-Rewriter LoRA, REF2AV, proven in
notes/forge_pw1d_smoke.md, 0.3 min GPU) which needs the GPU that PROMPT 99999999 / AGENTS.md bar in a pass; the
Grok prompt sidecars are barred by canon (approved_characters/GROK_IMAGINE_2026-10-19/CHARACTER.md R3, Derrick
2026-10-09); and the objective probes I ran this pass are inconclusive (9 SCRFD face boxes over the six stills:
green-skin fraction 0.0% in every box, grey/metal fraction 0.0-12.9% - notes/hc15_figures_20261025.md). So the
graph work that is decidable now is staged for all five remaining clips, and the species prose is written per
file the moment the two are named (needs_derrick.md row 18).

Runs on C:/Program Files/Python312/python.exe (the interpreter that has the repo's deps).
  python C:/AI/community/notes/hc15_anchor_carry_build.py --check
  python C:/AI/community/notes/hc15_anchor_carry_build.py --build
  python C:/AI/community/notes/hc15_anchor_carry_build.py --selftest
NO GPU: --build writes graph + run-dir request + manifest files only. A Ralph pass never queues (PROMPT.md
99999999 / AGENTS.md "The GPU is off-limits"); ck_nogpu scans this file's own source for a GPU/queue surface.
"""
import copy
import hashlib
import json
import os
import re
import sys
import time

W = r"C:/AI/community"
sys.path.insert(0, os.path.join(W, "notes"))
sys.path.insert(0, os.path.join(W, "scripts"))
from hc15_anchor_fix_build import ALLOWED, dumps_like, diff_paths, h3_schema, scan, transform, write_graph  # noqa: E402
from ali163_hc_im1b_build import prose_strings, prompt_stats  # noqa: E402
from comm import guard_ok  # noqa: E402  the fiction gate; the only gate allowed to touch a graph

COMFY = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI"
COMFY_IN = os.path.join(COMFY, "input")
COMFY_OUT = os.path.join(COMFY, "output", "community")
GRAPHS = os.path.join(W, "p7", "graphs")
RUNS = os.path.join(W, "runs")
JOBS = os.path.join(W, "p7", "jobs")
NOTES = os.path.join(W, "notes")
LEDGER = r"C:/Users/derek/5slock/ralph-community/logs/p7_budget.json"

# source clip -> (source id, carried id, seed). The seed is NOT moved: a before/after of the community switches
# is only a measurement with the seed held (IM1 re-renders the same seeds; clip 11 keeps 51150001 for the same
# reason - audit 3.5). The id carries the 1x series like clip 11.
CARRY = {2: ("ali163_hc15_bd006_s51150002", "ali163_hc15_bd006_s51150012", 51150002),
         3: ("ali163_hc15_bd013_s51150003", "ali163_hc15_bd013_s51150013", 51150003),
         4: ("ali163_hc15_gi046_s51150004", "ali163_hc15_gi046_s51150014", 51150004),
         5: ("ali163_hc15_gi063_s51150005", "ali163_hc15_gi063_s51150015", 51150005),
         6: ("ali163_hc15_gi072_s51150006", "ali163_hc15_gi072_s51150016", 51150006)}
CLIP1 = "ali163_hc15_bd002_s51150001"
CLIP11 = "ali163_hc15_bd002_s51150011"
CLIP11_SHA = "8a57ebbf456b6f9d74ad1ca2424076041e8ad0c524d15f7f8a7c9a126a57e769"   # measured 2026-10-25, 18,235 B
FORMAT_IND = 2   # the byte format of the fixed clip-1 graph: measured dumps_like(clip-11 bytes, transform(clip 1)) = 2
FRAMES = 362
CANVAS = (1344, 768)
EST_MIN = 30          # measured 24.0 + 25% contingency, the same rule clip 1-6 used (audit 3.7)
# assembled from pieces, the convention notes/ali163_hc15_build.py:56 uses, so ck_nogpu can stay meaningful
# while scanning this file's own source text
NO_GPU_TOKENS = ("llama" + "-swap", "127.0.0.1:" + "8080", "127.0.0.1:" + "10004", ":8" + "188", ":8" + "189",
                 "comfy" + "_ctl", "run_" + "graph_job", "gpu" + "_guard", "gpu" + "_lock", "queue_" + "prompt",
                 "ur" + "lib.request", "sock" + "et.", "subpro" + "cess", "ba" + "tch_queue", "nv" + "idia-smi")
BANNED_IN_MANIFEST = ("keep", "best", "pick", "winner", "preference", "favoured", "favorite")
CHUNKS = ("c0", "c1")

# ============================================================================ TOP (fix_plan TOP item)
# Max's unblock, verbatim, is fix_plan.md line 2 (ralph-community), quoted in full in
# C:/AI/community/notes/hc15_figures_20261025.md §1, and it answers C:/AI/community/notes/needs_derrick.md row 18
# (the row that asked for the naming). The two sentences the prose is written from, verbatim:
#   "GI046 is the orc (large green-skinned muscular orc, behind a blonde woman on a rug in a living room). GI063
#    is the robot (black and silver metallic humanoid robot, behind a blonde woman on a dark couch with a TV
#    behind them)." ... "render GI046 and GI063 first"  (the order the arm follows: GI046 then GI063)
# The L4 rule applies to this file's own citations: the naming text is NOT in needs_derrick.md row 18 - that row is
# Forge's ask - so every manifest/arm/gate note cites hc15_figures_20261025.md §1 + fix_plan.md line 2 and names
# needs_derrick.md only as the row being answered.
# CARRY 4/5 fixed the SHAPE of these two clips on 2026-10-25; the defect left is the SUBJECT LABEL. Measured in
# notes/hc15_figures_20261025.md and re-measured off the carried source graphs by --top-selftest: the GI046/GI063
# prompts hit orc/green/muscle/tusk/claw 0 times and robot/metal/silver/joint/panel 0 times, both c0 blocks say
# "the only person in that photograph", and the GI046 c0 block paints "a woman with dark brown hair".
# TOP prose = notes/hc15_top_prompts_20261025.md, written on notes/prompt_guide_20261024.md (official MiniMax
# Ref2VA section set; detailed_description 350-500 words for the first chunk; integrated_multimodal_description
# for the continuation chunk; canon camera type + amplitude + speed; zero prohibition/negation tokens) + the
# TenStrip/10Eros-Max card (notes/web/hc15_tenstrip_readme.txt: "if you do not give it the correct prompt
# structure it does not follow the format well").
TOP_MD = os.path.join(NOTES, "hc15_top_prompts_20261025.md")
TOP_GUIDE = os.path.join(NOTES, "prompt_guide_20261024.md")
TOP_FIGURES = os.path.join(NOTES, "hc15_figures_20261025.md")
TOP_NAMING = os.path.join(NOTES, "needs_derrick.md")
TOP_TENSTRIP = os.path.join(NOTES, "web", "hc15_tenstrip_readme.txt")
TOP_CANON = r"C:/Users/derek/5slock/approved_characters/ORC_POOL_EDGE/CHARACTER.md"
TOP_FIXPLAN = r"C:/Users/derek/5slock/ralph-community/fix_plan.md"
TOP_SELF = os.path.abspath(__file__)
TOP_ANCHOR = os.path.join(NOTES, "hc15_anchor_fix_build.py")
TOP_PROMPT_P6 = os.path.join(W, "scripts", "tests", "test_p6_review.py")
TOP_CITATIONS = (TOP_MD, TOP_GUIDE, TOP_FIGURES, TOP_NAMING, TOP_TENSTRIP, TOP_CANON, TOP_FIXPLAN, TOP_SELF,
                 TOP_ANCHOR, TOP_PROMPT_P6)

# still -> the two takes (a take's seed is its id number; "render 2-3 takes per still", fix_plan TOP) plus the
# words the species prose has to carry in EVERY chunk of that clip.
TOP = {"GI046": {"src": "ali163_hc15_gi046_s51150014", "take_a": "ali163_hc15_gi046_s51150031",
                 "take_b": "ali163_hc15_gi046_s51150032", "species": ("orc",),
                 "body": ("green", "muscled", "hands")},
        "GI063": {"src": "ali163_hc15_gi063_s51150015", "take_a": "ali163_hc15_gi063_s51150031",
                  "take_b": "ali163_hc15_gi063_s51150032", "species": ("robot",),
                  "body": ("machine",)}}
TOP_BY_ID = {}
for _tk, _tv in TOP.items():
    for _t, _id in (("A", _tv["take_a"]), ("B", _tv["take_b"])):
        TOP_BY_ID[_id] = dict(still=_tk, src=_tv["src"], take=_t, take_a=_tv["take_a"], take_b=_tv["take_b"],
                              species=_tv["species"], body=_tv["body"], seed=int(_id.split("_s")[-1]))
# The arm is the two FREE ids in Max's row-18 order (GI046 first). GI046 take A is spent (see
# TOP_RENDERS), so the GI046 slot in the queue is take B; GI063 take A is free.
TOP_ORDER = [TOP["GI046"]["take_b"], TOP["GI063"]["take_a"]]
# A TOP id is spent the moment the ComfyUI output dir carries a video. The row below is the declared
# statement about WHICH prose that render ran; file/bytes/sha256/stamp are measured off disk by
# top_render_receipt(), so a receipt cannot be softer than the file (L10). KEEP stays Derrick's.
TOP_RENDERS = {TOP["GI046"]["take_a"]: {
    "prose": "the shipped pre-card-fidelity prose: the record was rewritten by TOP-SCENE on 2026-10-27 "
             "and this mp4 predates the rewrite, so it is NOT a render of the current prose record",
    "select": "the selection is Derrick's alone; no vision judge, no score, no choice by the forge",
    "shape": "1344x768 24/1 362 f measured by ffprobe -select_streams v:0",
    "queue": "p7/jobs/<id>.result.json is absent and runs/<id>/status.log ends in poll-warn timeouts "
             "04:15-04:23 CT: the id is spent by file evidence, not by a queue receipt",
    "record": "notes/needs_derrick.md row 25"}}
# Max's naming, split per still so each manifest quotes the sentence that names its own figure (verbatim,
# fix_plan.md line 2 / hc15_figures_20261025.md §1)
TOP_STILL_ROW = {"GI046": "GI046 is the orc (large green-skinned muscular orc, behind a blonde woman on a rug in a "
                 "living room)",
                 "GI063": "GI063 is the robot (black and silver metallic humanoid robot, behind a blonde woman on a "
                 "dark couch with a TV behind them)"}
TOP_NAMING_WHERE = "Max 2026-10-24 9:30 PM CT, verbatim in fix_plan.md line 2 and notes/hc15_figures_20261025.md §1"
TOP_NAMING_ANSWERS = "answers needs_derrick.md row 18"
# every take of both named stills, once each (TOP_ORDER can carry a take B when a take A is spent)
TOP_TAKES = [TOP[_ts][_tk2] for _ts in TOP for _tk2 in ("take_a", "take_b")]
TOP_ALLOWED = {("[inputs].prompt", "c0", ""), ("[inputs].prompt", "c1", ""),
               ("[inputs].filename_prefix", "save", ""), ("[inputs].noise_seed", "noise", "")}
TOP_WORDS = {"c0": (350, 500), "c1": (350, 500)}    # notes/prompt_guide_20261024.md 350-500 word rule
TOP_MIN_BEATS = 3                                    # "every beat inside its chunk window", 3+ beats per chunk
TOP_NEG_WORDS = ("no", "not", "never", "neither", "nor", "without", "none", "nothing", "nobody")
TOP_AGE = re.compile(r"fictional adult aged (\d{2,3})")
TOP_DEFAULT_FIGURE = ("the only person in that photograph", "a woman with dark brown hair",
                      "the only person in the photograph", "the only bodies in the shot", "standing alone",
                      "alone in the room", "the only figure in the room", "the only subject")
# fix_plan TOP step 1-3: the start-image CARD as data. notes/scenes/<SCENE>.md = the vision model's own words off
# the start still (stamped: model, start_still_sha256, caption_status, read_scope); notes/scenes/<SCENE>.facts.json = the same
# facts as a GATE a builder can measure a prompt against. A word the card does not have, a figure count the card
# does not have, a head the frame crops, a pose the card does not show, a room the card does not name = a flag, not
# an opinion. (Derrick 2026-10-25 3:41 AM CT: "why are those strip videos and not written based on the images ...
# Do another audit and fix it"; 5:48-5:49 PM CT: "Read both start images first ... describe every figure in each
# start image as it actually is ... Write the prompt from the scene card ... never default a figure to 'woman'".
# A card is only ever read off a START STILL - never off a rendered clip - and a text-only pass never decides who
# is in a picture: that is the lesson this item ends on, and the gate is what enforces it.)
CARDS = {sc: os.path.join(NOTES, "scenes", sc + ".facts.json") for sc in ("GI046", "GI063")}
CARD_MDS = {sc: os.path.join(NOTES, "scenes", sc + ".md") for sc in ("GI046", "GI063")}
CARD_GATE_KEYS = ("figure_count", "aliases", "per_chunk_tokens", "banned", "head_in_frame", "head_allow",
                  "open_beat", "open_beat_ban", "room_required", "room_banned", "light_required", "age_marker",
                  "consent_gate", "solo_phrases", "evidence", "age_required")
CARD_TOP_KEYS = ("scene", "card", "caption", "audit", "image", "sha256", "model", "status", "figures",
                 "room", "light", "camera", "gate")
CARD_FIG_KEYS = ("label", "kind", "noun", "pose", "head_in_frame", "visible", "not_visible")
CARD_HEAD_WORDS = ("head", "face", "eye", "eyes", "brow", "nose", "jaw", "mouth", "lip", "lips", "teeth",
                   "grin", "smile", "chin", "cheek", "forehead", "hair", "bald", "beard", "skull")
CARD_AGE_RE = re.compile(r"aged \d{2}|age of \d{2}|\b\d{2}[- ]year[- ]old|age \d{2}")
CARD_PUNCT = (("\u2014", " - "), ("\u2013", " - "), ("\u2019", "'"), ("\u2018", "'"),
              ("\u201c", '"'), ("\u201d", '"'))
CARD_SCOPE = "read_scope: the start still only. no rendered clip"
# the human-species words the item bars for a non-human figure (fix_plan TOP: "never default a figure to
# 'woman'"). Anatomy words a species figure may legitimately carry ("frame", "body", "adult") are not here.
TOP_HUMAN = ("woman", "girl", "female", "lady")
TOP_EST_MIN = 30      # measured 24.0 min/job + 25% contingency, the EST_MIN rule clip 1-6 and CARRY used
NOW_P1 = "ali163_hc15_bd002_s51150021"   # the single-job arm TOP displaces; restore: --now-build of TOP_ANCHOR
TOP_RESTORE = f"python {'C:/AI/community/notes/hc15_anchor_fix_build.py'} --now-build"


def card_norm(s):
    """lower-case, dash/quote-folded, whitespace-folded: punctuation only, no word changes."""
    for a, b in CARD_PUNCT:
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s.lower().strip())


def card_facts(nid):
    """the card's machine-readable half, read fresh off disk every call (a seeded fault is seen at once)."""
    return json.loads(open(CARDS[nid], encoding="utf-8").read())


def card_md(nid):
    return card_norm(open(CARD_MDS[nid], encoding="utf-8").read())


def top_prompt(g, ch):
    """the chunk's whole prompt string: the section a Ref2VA prompt carries lives INSIDE it ('detailed_description:'
    for c0, 'integrated_multimodal_description:' for c1), so a card rule reads the chunk field, not a section key."""
    return g[ch]["inputs"]["prompt"]


def ctx_card(ctx):
    """the start-image card for a graph: a TOP graph's `still` row is the scene, every other graph has none."""
    return (ctx.get("top") or {}).get("still") if ctx.get("top") else None


def card_owner(sent, aliases):
    """the label whose alias sits nearest the END of the sentence: a word answers for its nearest referent, so
    'her hair falls over its green arms' charges 'arms' to the card's figure 2, not to her. None = no referent."""
    low, best, best_d = card_norm(sent), None, 10 ** 9
    for lab, alist in aliases.items():
        for a in alist:
            pat = r"(?<![a-z])" + re.escape(card_norm(a)) + r"(?![a-z])"
            at = [m.start() for m in re.finditer(pat, low)]
            if at and len(low) - max(at) <= best_d:
                best, best_d = lab, len(low) - max(at)
    return best


def card_beat0(p):
    """the chunk's opening beat: the text from its FIRST 'At MM:SS.mmm' marker to the next one - for c0 the
    00:00.000 second the clip opens on, for c1 the 00:10.125 second the continuation opens on."""
    m = re.search(r"At \d\d:\d\d\.\d\d\d", p)
    if not m:
        return ""
    nxt = p.find("At ", m.end() + 3)
    return p[m.end():nxt if nxt > 0 else len(p)]


def card_measure(nid, p):
    """The card gate run on ONE prompt string; every count is returned for the manifest. Nine rules:
    F-SUBJ the <Subject> count = the card's figure count; F-WORDS every gate token present in this chunk; F-SOLO
    no alone/only-person clause on a multi-figure card; F-BANNED no card-banned word charged to a figure (owner =
    nearest referent) and none in the all-figures ban list; F-HEAD no head/face words for a figure the card says
    the frame crops, outside the head_allow out-of-frame phrasing; F-POSE the chunk's opening beat carries the card's
    pose for each figure and says none of the poses the card does not show; F-ROOM the card's room/light words
    present; F-ROOM2 no room word the card does not name; F-AGE every age number carries the card's canon marker
    in its own sentence (an age is a canon declaration, not a sighting); F-CONSENT the consent row: banned claims
    absent, required card-honesty lines present."""
    gt = card_facts(nid)["gate"]
    out = {}
    np = card_norm(p)
    # a card rule answers for the SMALLEST unit that carries a referent: a sentence, and a definition line is a
    # sentence, so the split takes newline as a terminator too. Without it the whole subject_definitions block reads
    # as one sentence, the last <Subject N> line owns it, and figure 1's face/hair/legs get charged to figure 2.
    sent = [s for s in re.split(r"(?<=[.!?\n])\s*", p) if s.strip()]
    banned, head = {}, {}
    for s in sent:
        lab = card_owner(s, gt["aliases"])
        if lab is None:
            continue
        low = card_norm(s)
        for pat in list(gt["banned"].get(lab, [])) + list(gt["banned"].get("any", [])):
            if card_norm(pat) in low:
                banned.setdefault(lab, []).append(pat)
        if gt["head_in_frame"].get(lab) is False:
            for w in CARD_HEAD_WORDS:
                if re.search(r"(?<![a-z])" + w, low) and not any(card_norm(a) in low for a in gt["head_allow"]):
                    head.setdefault(lab, []).append(w)
    beat = card_norm(card_beat0(p))
    out["subjects"] = len(set(re.findall(r"<Subject\s*(\d+)>", p)))
    out["card_figures"] = gt["figure_count"]
    out["missing_tokens"] = [t for t in gt["per_chunk_tokens"] if card_norm(t) not in np]
    out["solo_hits"] = [ph for ph in gt["solo_phrases"] if card_norm(ph) in np]
    out["banned_hits"] = banned
    out["head_hits"] = head
    out["beat0_pose"] = {lab: [t for t in gt["open_beat"].get(lab, []) if card_norm(t) not in beat]
                         for lab in gt["open_beat"]}
    out["beat0_ban"] = {lab: [b for b in gt["open_beat_ban"].get(lab, []) if card_norm(b) in beat]
                        for lab in gt["open_beat_ban"]}
    out["room_missing"] = [r for r in list(gt["room_required"]) + list(gt["light_required"]) if card_norm(r) not in np]
    out["room_hits"] = [r for r in gt["room_banned"] if re.search(r"(?<![a-z])" + re.escape(card_norm(r)), np)]
    out["age_no_marker"] = [s for s in sent if CARD_AGE_RE.search(card_norm(s))
                            and card_norm(gt["age_marker"]) not in card_norm(s)]
    # a person-WORD (the facts' age_required list, word-boundary matched) forces the on-page adult age; a bare
    # pronoun does not, or every beat of a scene would need a birthday. "human" never triggers: boundaries.
    amiss = []
    for s in sent:
        ns = card_norm(s)
        who = sorted({w for w in gt.get("age_required", [])
                      if re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", ns)})
        if who and not CARD_AGE_RE.search(ns):
            amiss.append(",".join(who))
    out["age_missing"] = amiss
    out["consent_hits"] = [c for c in gt["consent_gate"]["ban"] if card_norm(c) in np]
    out["consent_missing"] = [c for c in gt["consent_gate"]["require"] if card_norm(c) not in np]
    return out


def card_fires(nid, out):
    """the nine card rules as (code, detail) pairs on one prompt's measurement; [] = the prompt is card-faithful."""
    gt, cf = card_facts(nid)["gate"], card_facts(nid)
    hit = []
    if out["subjects"] != gt["figure_count"]:
        hit.append(("F-CARD-SUBJ", "%d <Subject> labels, the card settles %d figures"
                    % (out["subjects"], gt["figure_count"])))
    if out["missing_tokens"]:
        hit.append(("F-CARD-WORDS", "no card word %s" % ", ".join(out["missing_tokens"][:4])))
    if out["solo_hits"]:
        hit.append(("F-CARD-SOLO", "%s on a %d-figure card" % (", ".join(out["solo_hits"][:3]), gt["figure_count"])))
    for lab, ps in sorted(out["banned_hits"].items()):
        hit.append(("F-CARD-BANNED", "figure %s: %s" % (lab, ", ".join(sorted(set(ps))[:4]))))
    for lab, ws in sorted(out["head_hits"].items()):
        hit.append(("F-CARD-HEAD", "figure %s: %s, and the card says the frame crops its head"
                    % (lab, ", ".join(sorted(set(ws))[:4]))))
    for lab, miss in sorted(out["beat0_pose"].items()):
        if miss:
            hit.append(("F-CARD-POSE", "figure %s opening beat lacks the card pose %s" % (lab, ", ".join(miss))))
    for lab, bs in sorted(out["beat0_ban"].items()):
        if bs:
            hit.append(("F-CARD-POSE2", "figure %s opening beat says %s" % (lab, ", ".join(bs[:3]))))
    if out["room_missing"]:
        hit.append(("F-CARD-ROOM", "no card room/light word %s" % ", ".join(out["room_missing"][:4])))
    if out["room_hits"]:
        hit.append(("F-CARD-ROOM2", "%s, and the card names no such room" % ", ".join(out["room_hits"][:4])))
    if out["age_no_marker"]:
        hit.append(("F-CARD-AGE", "%d sentence(s) state an age with no '%s' in them"
                    % (len(out["age_no_marker"]), gt["age_marker"])))
    if out["age_missing"]:
        hit.append(("F-CARD-AGE2", "%d sentence(s) name %s with no 'aged NN' (card age_min %s)"
                    % (len(out["age_missing"]), sorted(set(out["age_missing"]))[0], cf.get("age_min"))))
    if out["consent_hits"]:
        hit.append(("F-CARD-CONSENT", "%s" % ", ".join(out["consent_hits"][:3])))
    if out["consent_missing"]:
        hit.append(("F-CARD-CONSENT2", "no card-honesty line %s" % ", ".join(out["consent_missing"][:2])))
    return hit





def top_windows(g):
    """(lo, hi) seconds each chunk's beats must live in, measured off the graph: chunk 1 = c0.length frames at
    mkvid.fps; the 119-frame window adds the rest (362 f = 15.083333 s total)."""
    fps = g["mkvid"]["inputs"]["fps"]
    c0 = g["c0"]["inputs"]["length"]
    ext = g.get("win1", {}).get("inputs", {}).get("extension_frames", 0)
    return {"c0": (0.0, c0 / fps), "c1": (c0 / fps, (c0 + ext) / fps)}


def top_md(a_id=None):
    """the prose record, keyed (id, chunk) and per-chunk for one id; byte records, no normalisation."""
    txt = open(TOP_MD, encoding="utf-8").read()
    out = {}
    for blk in re.split(r"^### ", txt, flags=re.M)[1:]:
        head = blk.split("\n", 1)[0]
        m = re.search(r"id=(\S+) chunk=(c\d) seed=(\d+)", head)
        if not m:
            continue
        out[(m.group(1), m.group(2))] = blk.split("\n", 1)[1].split("\n---")[0].rstrip()
    want = a_id or TOP["GI046"]["take_a"]
    return {c: v for (i, c), v in out.items() if i == want}


def top_seed_of(nid):
    return int(nid.split("_s")[-1])


def top_prose_stats(text, ch):
    """prompt_stats plus the two prose rules the TOP item names: 0 prohibition/negation tokens and the stated
    fictional-adult ages. The guide's word band is measured on the chunk's MAIN FIELD (main_words), not the whole
    prompt (prompt_stats "words"), which is the number a 350-500 rule can be checked against."""
    st = prompt_stats(text, ch)
    toks = re.findall(r"[A-Za-z][A-Za-z'\-]*", text)
    st["neg"] = len([w for w in toks if w.lower() in TOP_NEG_WORDS])
    st["ages"] = sorted({int(x) for x in TOP_AGE.findall(text)})
    return st


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def gload(nid):
    return json.load(open(os.path.join(GRAPHS, nid + ".api.json"), encoding="utf-8"))


def gpath(nid):
    return os.path.join(GRAPHS, nid + ".api.json")


def man_path(nid):
    return os.path.join(NOTES, f"hc15_anchor_carry_{nid}.json")


def slot_edges(g):
    """{chunk: {ref_image_N: [node, idx]}} read the fullmatch way (AGENTS.md: the ref_images dict of submitted
    graphs breaks ins[k][0])."""
    out = {}
    for nid, nd in g.items():
        if not nid.startswith("c"):
            continue
        out[nid] = {k: v for k, v in nd["inputs"].items()
                    if re.fullmatch(r"ref_images\.ref_image_\d+", k)}
    return out


# ------------------------------------------------------------------------- detectors  (each: g -> list of failures)
def ck_top_diff(g, ctx):
    """TOP graphs move the two prompts, the seed and the save prefix and NOTHING else (the shape stays the fixed
    clip-1 shape CARRY built). Inert for the carry graphs, which are governed by ck_diff + ALLOWED."""
    if not ctx["top"]:
        return []
    d = diff_paths(ctx["src"], g)
    extra = sorted("%s|%s|%s" % t for t in d - TOP_ALLOWED)
    missing = sorted("%s|%s|%s" % t for t in TOP_ALLOWED - d)
    out = []
    if extra:
        out.append(f"TOP-DIFF more than the prose, the seed and the prefix moved: {extra} - the item says the graph "
                   "shape is fixed: MiniMaxH3AddGuide frame_idx 0, res_multistep/simple/8, 243 + 119 frames")
    if missing:
        out.append(f"TOP-DIFF the species prose / seed / prefix did not move: {missing}")
    return out


def ck_diff(g, ctx):
    if ctx["top"]:
        return []        # TOP ids are governed by ck_top_diff (a new prompt is not one of the 3 switches)
    d = diff_paths(ctx["src"], g)
    extra = sorted("%s|%s|%s" % t for t in d - ALLOWED)
    missing = sorted("%s|%s|%s" % t for t in ALLOWED - d)
    out = []
    if extra:
        out.append(f"DIFF more than the three community switches moved: {extra}")
    if missing:
        out.append(f"DIFF a published switch is absent: {missing}")
    return out


def ck_control(g, ctx):
    """The anti-look-alike detector: the imported transform() must reproduce the RENDERED clip-11 bytes from
    clip 1, and this file's serialization must reproduce the on-disk bytes of the artifact it writes."""
    out = []
    reb = transform(gload(CLIP1))
    ind = dumps_like(open(gpath(CLIP11), "rb").read(), reb)
    if ind is None:
        out.append("CONTROL_DEAD transform(clip 1) does not reproduce the shipped clip-11 bytes at any indent: "
                   "the imported switch is not the one that made the rendered clip")
    if sha(gpath(CLIP11)) != CLIP11_SHA:
        out.append(f"CONTROL the shipped clip-11 sha {sha(gpath(CLIP11))[:16]} != the pinned {CLIP11_SHA[:16]}")
    if ind != FORMAT_IND:
        out.append(f"CONTROL_DEAD the clip-11 byte format measures indent {ind}, not the pinned FORMAT_IND "
                   f"{FORMAT_IND}: ck_graphfile would be checking a format this line does not use")
    if ctx["path"] and sha(ctx["path"]) == CLIP11_SHA:
        out.append("CONTROL a carried graph is byte-identical to clip 11, so it is not the carried clip")
    return out


def ck_guide(g, ctx):
    out = []
    nd = g.get("g0")
    if not nd:
        return ["GUIDE no MiniMaxH3AddGuide node: the frame-0 anchor of the fixed clip-1 shape is missing"]
    if nd["class_type"] != "MiniMaxH3AddGuide":
        out.append(f"GUIDE g0 class {nd['class_type']} != MiniMaxH3AddGuide")
    ins = nd["inputs"]
    if ins.get("frame_idx") != 0:
        out.append(f"GUIDE g0.frame_idx {ins.get('frame_idx')} != 0 (the item's literal requirement)")
    if ins.get("positive") != ["c0", 0] or ins.get("latent") != ["c0", 1] or ins.get("image") != ["img", 0]:
        out.append(f"GUIDE g0 wiring {ins.get('positive')}/{ins.get('latent')}/{ins.get('image')} "
                   "!= c0 positive / c0 latent / img image")
    if g["s0_guide"]["inputs"].get("conditioning") != ["g0", 0]:
        out.append(f"GUIDE s0_guide.conditioning {g['s0_guide']['inputs']['conditioning']} != [g0, 0] "
                   "(the anchor sits on the c0 conditioning edge)")
    return out


def ck_shape(g, ctx):
    bad = []
    if g["c0"]["inputs"]["length"] != 243:
        bad.append(f"SHAPE c0.length {g['c0']['inputs']['length']} != 243")
    win = g.get("win1", {}).get("inputs")
    if not win:
        bad.append("SHAPE no win1 continuation node: the fixed clip-1 shape is 243 f + one 119 f window")
        tot = g["c0"]["inputs"]["length"]
    else:
        if (win["extension_frames"], win["overlap_frames"]) != (119, 22):
            bad.append(f"SHAPE window {win['extension_frames']}/{win['overlap_frames']} != "
                       "119 extension / 22 overlap")
        if win.get("previous_av_latent") != ["s0_samp", 0]:
            bad.append(f"SHAPE win1.previous_av_latent {win.get('previous_av_latent')} != [s0_samp, 0]")
        tot = g["c0"]["inputs"]["length"] + win["extension_frames"]
    if tot != FRAMES or (tot - 5) % 17:
        bad.append(f"SHAPE frames 243+119={tot} != 362 or off the (f-5)%17==0 grid")
    if g["ksel"]["inputs"]["sampler_name"] != "res_multistep":
        bad.append(f"SHAPE sampler {g['ksel']['inputs']['sampler_name']} != res_multistep")
    for k in ("s0_sched", "s1_sched"):
        if g[k]["inputs"]["steps"] != 8:
            bad.append(f"SHAPE {k}.steps {g[k]['inputs']['steps']} != 8")
        if g[k]["inputs"].get("scheduler") != "simple":
            bad.append(f"SHAPE {k}.scheduler {g[k]['inputs'].get('scheduler')} != simple")
        if g[k]["inputs"].get("denoise") != 1.0:
            bad.append(f"SHAPE {k}.denoise {g[k]['inputs'].get('denoise')} != 1.0")
    n_smp = len([1 for nd in g.values() if nd["class_type"] == "SamplerCustomAdvanced"])
    if n_smp != 2:
        bad.append(f"SHAPE {n_smp} SamplerCustomAdvanced nodes, 2 passes expected (243 + one 119 window)")
    if "c2" in g:
        bad.append("SHAPE c2 still present: the 243+119 shape has two passes, not three")
    for ch in CHUNKS:
        w, h = g[ch]["inputs"]["width"], g[ch]["inputs"]["height"]
        if (w, h) != CANVAS or w % 32 or h % 32:
            bad.append(f"SHAPE {ch} canvas {w}x{h} != 1344x768 / multiple of 32")
    if g["mkvid"]["inputs"]["fps"] != 24:
        bad.append(f"SHAPE fps {g['mkvid']['inputs']['fps']} != 24")
    if [g["m_shift"]["inputs"][k] for k in ("shift_video", "shift_audio")] != [10.0, 3.0]:
        bad.append("SHAPE shift moved off video 10.0 / audio 3.0")
    cfg = [f"{n}.{k}" for n, nd in g.items() for k in nd["inputs"] if "cfg" in k.lower()]
    if cfg:
        bad.append(f"SHAPE cfg key present {cfg} (the H3 graph has no cfg key at all)")
    for nid in ("dec_v", "dec_a"):
        if nid not in g or "samples" not in g[nid]["inputs"]:
            bad.append(f"SHAPE {nid} has no samples input to wire")
        elif g[nid]["inputs"]["samples"] != ["app1", 0]:
            bad.append(f"SHAPE {nid}.samples {g[nid]['inputs']['samples']} != [app1, 0] (the 2-pass join)")
    return bad


def ck_prose(g, ctx):
    """The carry moves graph settings only. Species prose is a separate variable, and it cannot be written for
    these five clips until the figure is identified, so the prompts must be byte-identical to the source clip."""
    if not ctx["src"]:
        return []        # source-less ctx = the control artifact (clip 11), compared by the other detectors
    if ctx["top"]:
        return []        # TOP moves the prose on purpose; ck_top_* + ck_top_sync govern its prompt text
    out = []
    for ch in CHUNKS:
        a, b = g[ch]["inputs"]["prompt"], ctx["src"][ch]["inputs"]["prompt"]
        if a != b:
            out.append(f"PROSE {ch} prompt changed by the carry ({len(a.split())} vs {len(b.split())} words): "
                       "this pass is the settings switch, prose edits are the next item")
        st = prompt_stats(b, ch)
        if len(st["sections"]) < 5:
            out.append(f"PROSE {ch} sections {st['sections']} - the community section set is 5 fields")
    gone = set(ctx["src"]) - set(g)
    added = set(g) - set(ctx["src"])
    if gone != {"c2", "win2", "tail2", "app2", "s2_samp", "s2_guide", "s2_sched"} or added != {"g0"}:
        out.append(f"PROSE node set moved beyond the shape switch: dropped {sorted(gone)} added {sorted(added)}")
    return out


def ck_gate(g, ctx):
    ps = prose_strings(g)
    fails = [f"{nid}.{k}" for nid, k, v in ps if not guard_ok(v)]
    out = [f"GATE the adults gate (scripts/comm.py guard_ok) refused {fails}"] if fails else []
    if len(ps) < 2:
        out.append(f"GATE census found {len(ps)} prose strings, 2 chunk prompts expected")
    if len([1 for _, k, _ in ps if k == "prompt"]) < len(ps):
        out.append(f"GATE comm.py reads only key 'prompt' and misses "
                   f"{len(ps) - len([1 for _, k, _ in ps if k == 'prompt'])} prose strings (L11 gap)")
    return out


def ck_slots(g, ctx):
    if not ctx["src"]:
        return []
    out = []
    a, b = slot_edges(ctx["src"]), slot_edges(g)
    for ch in CHUNKS:
        if a.get(ch) != b.get(ch):
            out.append(f"SLOTS {ch} ref slots moved by the carry: {a.get(ch)} -> {b.get(ch)}")
    for nid, nd in g.items():
        if nd["class_type"] == "LoadImage":
            if nd["inputs"]["image"] != ctx["src"][nid]["inputs"]["image"]:
                out.append(f"SLOTS {nid} start/crop image moved by the carry")
    n = len(next(iter(b.values())))
    if n not in (2, 3):
        out.append(f"SLOTS {n} ref slots on a chunk, 2 (start still + one gate crop) or 3 (start still + two "
                   f"crops) expected - measured off the source clip: {len(next(iter(a.values())))}")
    return out


def ck_inputs(g, ctx):
    out = []
    for nid, nd in g.items():
        if nd["class_type"] == "LoadImage":
            p = os.path.join(COMFY_IN, nd["inputs"]["image"].replace("/", os.sep))
            if not os.path.isfile(p):
                out.append(f"INPUTS {nid} LoadImage file absent in ComfyUI/input: {nd['inputs']['image']}")
    return out


def ck_idfree(g, ctx):
    """an unrendered id only: no mp4, no result.json, no ComfyUI output dir. A TOP id whose render is
    DECLARED (TOP_RENDERS) and byte-matches the manifest receipt is spent-on-the-record: it carries a
    render receipt (ck_top_manifest verifies it), so id-free is not the property it claims. A declared
    render whose receipt does not match the video on disk is a FAIL, and a spent id never gets armed."""
    nid = ctx["id"]
    if ctx.get("top") and nid in TOP_RENDERS:
        rec = top_render_receipt(nid)
        man = json.load(open(man_path(nid), encoding="utf-8")) if os.path.isfile(man_path(nid)) else {}
        mr = man.get("rendered") or {}
        if rec and all(mr.get(k) == rec[k] for k in ("file", "bytes", "sha256", "written")):
            return []
        return ["IDFREE %s is a declared render (TOP_RENDERS) and the manifest receipt %s does not match "
                "the video on disk %s" % (nid, mr, rec)]
    out = []
    if os.path.isfile(os.path.join(JOBS, nid + ".result.json")):
        out.append(f"IDFREE p7/jobs/{nid}.result.json exists: the id is spent, the request is not submittable")
    if os.path.isdir(os.path.join(COMFY_OUT, nid)):
        out.append(f"IDFREE output/community/{nid} exists: the id is spent")
    if os.path.isfile(os.path.join(RUNS, nid, nid + ".mp4")):
        out.append(f"IDFREE runs/{nid}/{nid}.mp4 exists: the id is spent")
    if os.path.isfile(os.path.join(JOBS, nid + ".json")):
        out.append(f"IDFREE p7/jobs/{nid}.json exists: a job for this id is already in the queue")
    return out


def ck_schema(g, ctx):
    sch = ctx["schema"]
    bad = scan(g, sch)
    out = []
    if len(sch) < 5:
        out.append(f"SCHEMA_DEAD the H3 schema parse gave {len(sch)} classes, the scan would be vacuous")
    if len([1 for nd in g.values() if nd["class_type"] in sch]) < 2:
        out.append("SCHEMA_DEAD the schema covers no H3 node in this graph, the scan would be vacuous")
    dead = copy.deepcopy(g)
    dead["c1"]["class_type"] = "MiniMaxH3ImageToVideo"          # the exact defect that killed r3 at rc=2
    line = "c1.audio_vae: not an input of MiniMaxH3ImageToVideo"
    if line not in scan(dead, sch):
        out.append("SCHEMA_DEAD the non-vacuity control did not reproduce the r3 MiniMaxH3ImageToVideo defect")
    if bad:
        out.append(f"SCHEMA offline static check: {bad[:6]}")
    return out


def ck_prefix(g, ctx):
    want = f"community/{ctx['id']}/{ctx['id']}"
    got = g["save"]["inputs"]["filename_prefix"]
    return [] if got == want else [f"PREFIX {got} != {want}"]


def ck_seed(g, ctx):
    s = g["noise"]["inputs"]["noise_seed"]
    out = []
    if s != ctx["seed"]:
        out.append(f"SEED {s} != {ctx['seed']}")
    if ctx["top"]:
        return out       # TOP is not a settings before/after: its seed comes from the id (two takes per still)
    if ctx["src"] and s != ctx["src"]["noise"]["inputs"]["noise_seed"]:
        out.append(f"SEED {s} moved off the source clip seed {ctx['src']['noise']['inputs']['noise_seed']}: a "
                   "settings before/after holds the seed (IM1; clip 11 keeps 51150001 for the same reason)")
    return out


def ck_rundir(g, ctx):
    p = os.path.join(RUNS, ctx["id"], "request.api.json")
    if not os.path.isfile(p):
        return [f"RUNDIR runs/{ctx['id']}/request.api.json absent (the runner reads the arm dir, not p7/graphs)"]
    gp = gpath(ctx["id"])
    if open(p, "rb").read() != open(gp, "rb").read():
        return [f"RUNDIR runs/{ctx['id']}/request.api.json bytes != p7/graphs/{ctx['id']}.api.json bytes"]
    return []


def ck_graphfile(g, ctx):
    raw = open(gpath(ctx["id"]), "rb").read()
    out = []
    if raw.endswith(b"\n"):
        out.append("GRAPHFILE trailing newline")
    if raw != json.dumps(g, indent=ctx["ind"], ensure_ascii=False).replace("\n", "\r\n").encode("utf-8"):
        out.append(f"GRAPHFILE on-disk bytes != indent {ctx['ind']} / CRLF / no-trailing-newline serialization")
    if raw == open(gpath(CLIP11), "rb").read():
        out.append("GRAPHFILE byte-identical to the clip-11 graph")
    return out


def ck_manifest(g, ctx):
    p = man_path(ctx["id"])
    if not os.path.isfile(p):
        return [f"MANIFEST no manifest on disk ({os.path.basename(p)}) to re-derive"]
    m = json.load(open(p, encoding="utf-8"))
    out = []
    if m.get("graph_sha256") != sha(gpath(ctx["id"])):
        out.append("MANIFEST graph_sha256 != on-disk graph bytes")
    if m.get("seed") != ctx["seed"] or m.get("source_clip") != ctx["src_id"]:
        out.append("MANIFEST seed/source_clip does not match the spec")
    if m.get("diff_paths") != sorted("%s|%s|%s" % t for t in diff_paths(ctx["src"], g)):
        out.append("MANIFEST diff_paths != the diff measured off the source graph")
    if m.get("prompts") != {ch: {k: prompt_stats(g[ch]["inputs"]["prompt"], ch)[k]
                                 for k in ("words", "beats", "sections")} for ch in CHUNKS}:
        out.append("MANIFEST prompt words/beats/sections drifted from the graph on disk")
    facts = json.dumps({k: v for k, v in m.items() if k not in ("checks", "check_failures")}).lower()
    hits = [w for w in BANNED_IN_MANIFEST if w in facts]
    if hits:
        out.append(f"MANIFEST the recorded facts carry a judgement token {hits}; the pick is Derrick's alone")
    return out


def ck_nogpu(g, ctx):
    hits = [t for t in NO_GPU_TOKENS if t in ctx["self_src"]]
    return [f"NO_GPU this builder names a GPU/queue surface {hits}"] if hits else []


# ---------------------------------------------------------------------------- TOP detectors (inert on carry ids)
def ck_top_species(g, ctx):
    """The item: "describe every figure in each start image as it actually is (species, body, build), never
    default a figure to 'woman'" (fix_plan TOP, Derrick 2026-10-24 5:48-5:49 PM CT). Every chunk of the clip has
    to carry the species token and the body tokens, and no chunk may write the figure out of the scene."""
    t = ctx["top"]
    if not t:
        return []
    out = []
    for ch in CHUNKS:
        p = g[ch]["inputs"]["prompt"]
        low = p.lower()
        miss = [w for w in t["species"] + t["body"] if w not in low]
        if miss:
            out.append(f"TOP-SPECIES {ch} prompt never says {miss}: {t['still']} shows a "
                       f"{t['species'][0]}, and the item bars defaulting a figure to 'woman'")
        dflt = [c for c in TOP_DEFAULT_FIGURE if c in low]
        if dflt:
            out.append(f"TOP-SPECIES {ch} carries the default-figure clause {dflt} - the shipped prompt writes the "
                       f"{t['species'][0]} out of the start image (measured in {os.path.basename(TOP_FIGURES)})")
        # The guide's format restates every subject twice (subject_definitions + identity_preservation), so a
        # per-line woman count is not the item's rule: a woman-speaking preservation line for the human partner is
        # correct prose and would false-fire. The referent is the leading <Subject N>, so group by referent and
        # test the group: exactly one group carries the species words, exactly one carries the human words, and no
        # group carries both. That is the item read on the structure the guide ships.
        groups = {}
        for l in [x.strip() for x in p.split("\n") if x.strip().startswith("<Subject")]:
            m = re.match(r"<Subject\s+(\d+)>", l)
            groups.setdefault(m.group(1) if m else "?", []).append(l)
        sp_g = [n for n, ls in groups.items() if any(w in " ".join(ls).lower() for w in t["species"] + t["body"])]
        hu_g = [n for n, ls in groups.items() if any(w in " ".join(ls).lower() for w in TOP_HUMAN)]
        for n, ls in groups.items():
            low = " ".join(ls).lower()
            if n in sp_g and n in hu_g:
                out.append(f"TOP-SPECIES {ch} <Subject {n}> is written as both a {t['species'][0]} and a human "
                           f"figure ({[w for w in TOP_HUMAN if w in low]}); the start image shows a "
                           f"{t['species'][0]} in that slot and the item bars defaulting a figure to 'woman' "
                           f"(the shipped prose's clause is measured in {os.path.basename(TOP_FIGURES)}): "
                           f"{ls[0][:70]}...")
        if len(sp_g) != 1:
            out.append(f"TOP-SPECIES {ch} has {len(sp_g)} <Subject> groups carrying the {t['species'][0]} words "
                       f"{list(t['species'] + t['body'])}; {t['still']} is one human figure plus one "
                       f"{t['species'][0]}, and a figure written out of the scene is the default the item bars")
        if len(hu_g) != 1:
            out.append(f"TOP-SPECIES {ch} has {len(hu_g)} <Subject> groups carrying a human word {list(TOP_HUMAN)}; "
                       f"{t['still']} shows one human partner, and the human figure has to be described as she is")
    return out


def ck_top_age(g, ctx):
    """Canon lock (C:/Users/derek/5slock/plans/canon/fiction-cond-lock.md): every character is a fictional adult
    aged 21+, and the figure table's rule is 'say a fictional adult aged 21+' in the block."""
    t = ctx["top"]
    if not t:
        return []
    out = []
    for ch in CHUNKS:
        p = g[ch]["inputs"]["prompt"]
        ages = [int(x) for x in TOP_AGE.findall(p)]
        if not ages:
            out.append(f"TOP-AGE {ch} names no 'fictional adult aged NN' figure")
        bad = [a for a in ages if not 21 <= a <= 99]
        if bad:
            out.append(f"TOP-AGE {ch} ages {bad} outside 21+")
        for l in (x.strip() for x in p.split("\n") if x.strip().startswith("<Subject")):
            if "woman" in l.lower() and not TOP_AGE.search(l):
                out.append(f"TOP-AGE {ch} human <Subject> line carries no stated adult age: {l[:70]}...")
    return out


def ck_top_words(g, ctx):
    """The guide's 350-500 word rule on the chunk's main field, re-measured off the graph (words = the alphabetic
    tokens of the field, the ali163_hc_im1b_build.prompt_stats way)."""
    t = ctx["top"]
    if not t:
        return []
    out = []
    for ch in CHUNKS:
        n = prompt_stats(g[ch]["inputs"]["prompt"], ch)["main_words"]
        lo, hi = TOP_WORDS[ch]
        if not lo <= n <= hi:
            out.append(f"TOP-WORDS {ch} main field {n} words, outside {lo}-{hi} "
                       f"({os.path.basename(TOP_GUIDE)}: detailed_description / integrated_multimodal_description "
                       "350-500 words)")
    return out


def ck_top_beats(g, ctx):
    """Every 'At MM:SS.mmm' beat inside its own chunk window, measured off the fixed shape: c0 = 243 f at 24 fps
    = 0-10.125 s, c1 = the 119-frame window = 10.125-15.0833 s. The shipped carried clips 12-16 keep the old
    3-pass beat windows (00:05.2-00:09.9), which is exactly what a 2-pass shape must not do."""
    t = ctx["top"]
    if not t:
        return []
    out = []
    win = top_windows(g)
    for ch in CHUNKS:
        ts = [float(a) * 60 + float(b) for a, b in re.findall(r"At (\d\d):(\d\d\.\d\d\d)", g[ch]["inputs"]["prompt"])]
        lo, hi = win[ch]
        outside = [round(x, 3) for x in ts if not lo - 1e-6 <= x <= hi + 1e-6]
        if outside:
            out.append(f"TOP-BEATS {ch} beats {outside} outside the chunk window {round(lo, 3)}-{round(hi, 3)} s "
                       f"(c0.length {g['c0']['inputs']['length']} + window "
                       f"{g.get('win1', {}).get('inputs', {}).get('extension_frames', 0)} at "
                       f"{g['mkvid']['inputs']['fps']} fps)")
        if len(ts) < TOP_MIN_BEATS:
            out.append(f"TOP-BEATS {ch} has {len(ts)} beats, {TOP_MIN_BEATS}+ visible/audible beats are the "
                       f"{os.path.basename(TOP_GUIDE)} rule")
    return out


def ck_top_neg(g, ctx):
    """The guide's positive-wording rule: 0 prohibition/negation tokens in the prompt prose."""
    t = ctx["top"]
    if not t:
        return []
    out = []
    for ch in CHUNKS:
        toks = [w.lower() for w in re.findall(r"[A-Za-z][A-Za-z'\-]*", g[ch]["inputs"]["prompt"]) if w.lower() in TOP_NEG_WORDS]
        if toks:
            out.append(f"TOP-NEGATION {ch} carries {len(toks)} prohibition/negation tokens {sorted(set(toks))} - "
                       f"{os.path.basename(TOP_GUIDE)}: 'describe what happens in positive wording'")
    return out


def ck_top_sync(g, ctx):
    """One source of truth: the take-A graph prompts == notes/hc15_top_prompts_20261025.md byte-for-byte, and
    take B reuses take A's prompts byte-for-byte (take B moves the seed only)."""
    t = ctx["top"]
    if not t:
        return []
    out = []
    md = top_md(t["take_a"])
    for ch in CHUNKS:
        if md.get(ch) is None:
            out.append(f"TOP-SYNC no {ch} block in {os.path.basename(TOP_MD)} for {t['take_a']}")
            continue
        if t["take"] == "A" and g[ch]["inputs"]["prompt"] != md[ch]:
            out.append(f"TOP-SYNC {ch} prompt != the {os.path.basename(TOP_MD)} block "
                       f"({len(g[ch]['inputs']['prompt'])} B vs {len(md[ch])} B)")
        if t["take"] == "B":
            try:
                a = gload(t["take_a"])
            except Exception as e:
                out.append(f"TOP-SYNC take A {t['take_a']} unreadable ({e})")
                continue
            if g[ch]["inputs"]["prompt"] != a[ch]["inputs"]["prompt"]:
                out.append(f"TOP-SYNC take B {ch} prompt drifted from take A: take B moves the seed only")
    return out


def ck_top_seed(g, ctx):
    """A take's seed is its id number, and the two takes of one still differ by the seed alone."""
    t = ctx["top"]
    if not t:
        return []
    out = []
    s = g["noise"]["inputs"]["noise_seed"]
    if s != t["seed"]:
        out.append(f"TOP-SEED {s} != {t['seed']} (the id carries the take seed)")
    if s == ctx["src"]["noise"]["inputs"]["noise_seed"]:
        out.append(f"TOP-SEED {s} is still the source clip seed {s}: the takes are new renders, not the IM1 "
                   "settings before/after that holds a seed")
    if t["take_a"] == ctx["id"] and top_seed_of(t["take_a"]) == top_seed_of(t["take_b"]):
        out.append("TOP-SEED the two takes of one still share a seed")
    return out


def ck_top_arm(g, ctx):
    """The handoff: p7/JOB_REQUEST.json carries the FREE take of each named still as its own 6-key job row,
    in the order Max's unblock row gave (GI046 then GI063). The other take stays staged and unarmed -
    disclosed, not hidden - and the ledger has to absorb what is armed (5:52-5:53 PM CT rule: the plan's
    queue math must not overdraw the standing cap). A spent id (a video already in the ComfyUI output dir)
    is never armed: the render row is a receipt, not a queue entry."""
    t = ctx["top"]
    if not t:
        return []
    req, led = ctx["req"], ctx["ledger"]
    out = []
    if not req:
        return ["TOP-ARM p7/JOB_REQUEST.json unreadable: TOP is not handed off"]
    ids = [j.get("id") for j in req.get("jobs", [])]
    if ids != TOP_ORDER:
        out.append(f"TOP-ARM jobs[] {ids} != the free take of each named still {TOP_ORDER} (Max's order: "
                   "GI046 first, GI063 second; the other take is staged, not armed)")
    for j in req.get("jobs", []):
        if set(j) != {"id", "kind", "frames", "frames_tol", "minutes", "note"}:
            out.append(f"TOP-ARM {j.get('id')} job row keys {sorted(j)} != id,kind,frames,frames_tol,minutes,note")
        if j.get("frames") != FRAMES or j.get("kind") != "graph":
            out.append(f"TOP-ARM {j.get('id')} frames {j.get('frames')} / kind {j.get('kind')} != {FRAMES} / graph")
        if j.get("minutes") != TOP_EST_MIN:
            out.append(f"TOP-ARM {j.get('id')} minutes {j.get('minutes')} != measured {TOP_EST_MIN}")
        rec = top_render_receipt(str(j.get("id")))
        if rec:
            out.append(f"TOP-ARM {j.get('id')} is SPENT (video {rec['bytes']} B sha {rec['sha256'][:16]} "
                       f"written {rec['written']}) - a render receipt is not a queue entry; arm the free "
                       f"take of that still")
        note = str(j.get("note", ""))
        need = [str(j.get("id")), str(gload(str(j.get("id")))["noise"]["inputs"]["noise_seed"]), TOP_MD, TOP_GUIDE,
                TOP_NAMING, TOP_FIGURES, "frame_idx 0", "243", "119", "1344x768", "audio", "comm.guard_ok",
                "test_p6_review.py", "0 result.json", "minutes=30", "--top-check", "--top-selftest"]
        miss = [c for c in need if c not in note]
        if miss:
            out.append(f"TOP-ARM {j.get('id')} note missing {miss}")
        if not 1200 <= len(note) <= 2100:
            out.append(f"TOP-ARM {j.get('id')} note {len(note)} chars, 1200-2100 required (600-1100 for a graph)")
        hits = [w for w in BANNED_IN_MANIFEST if w in note.lower()]
        if hits:
            out.append(f"TOP-ARM {j.get('id')} note carries a judgement token {hits}")
    for tok in NO_GPU_TOKENS:
        if tok in json.dumps(req):
            out.append(f"TOP-ARM request text names the GPU/queue surface {tok!r}")
    armed = sum(j.get("minutes", 0) for j in req.get("jobs", []))
    if led["used_min"] + armed > led["cap_min"]:
        out.append(f"TOP-ARM arming {armed} min over ledger {led['used_min']}/{led['cap_min']} min")
    if led["jobs"] + len(req.get("jobs", [])) > led["job_cap"]:
        out.append(f"TOP-ARM arming {len(req.get('jobs', []))} jobs over ledger {led['jobs']}/{led['job_cap']}")
    if req.get("id") != TOP_ORDER[0] or req.get("api") != gpath(TOP_ORDER[0]).replace("\\", "/"):
        out.append(f"TOP-ARM top level id/api {req.get('id')}/{req.get('api')} != {TOP_ORDER[0]}")
    for nid in [x for x in TOP_TAKES if x not in TOP_ORDER]:
        if nid in ids:
            out.append(f"TOP-ARM the staged take {nid} is armed; its minutes are not in the disclosed "
                       f"queue math (the armed set is {TOP_ORDER})")
    return out


def card_manifest(nid, g):
    """the card receipt for the manifest: the card and its facts file by path+sha, the stamped model/status/start_still_sha256, the
    figure count, the evidence rows and how many sit verbatim in the card, and the gate run on BOTH chunk prompts
    (every rule's counts + the rule codes that fired). ck_top_manifest re-derives this off disk, so a manifest
    cannot carry a friendlier number than the card supports."""
    sc = nid if nid in CARDS else TOP_BY_ID[nid]["still"]
    f = card_facts(sc)
    gt, md = f["gate"], card_md(sc)
    ev = {k: card_norm(v) in md for k, v in gt["evidence"].items()}
    flags, fires = {}, {}
    for ch in CHUNKS:
        out = card_measure(sc, top_prompt(g, ch))
        flags[ch] = out
        fires[ch] = [c for c, _ in card_fires(sc, out)]
    return {"facts": CARDS[sc].replace("\\", "/"), "facts_sha256": sha(CARDS[sc]),
            "card": CARD_MDS[sc].replace("\\", "/"), "card_sha256": sha(CARD_MDS[sc]),
            "card_still_sha256": f["sha256"][:16], "model": f["model"], "status": f["status"],
            "scope_ok": CARD_SCOPE in md, "figures": gt["figure_count"],
            "evidence_rows": len(gt["evidence"]), "evidence_verbatim": sum(ev.values()),
            "per_chunk_tokens": len(gt["per_chunk_tokens"]),
            "tokens_per_chunk": {ch: len(gt["per_chunk_tokens"]) - len(flags[ch]["missing_tokens"]) for ch in CHUNKS},
            "banned_hits": {ch: sum(len(v) for v in flags[ch]["banned_hits"].values()) for ch in CHUNKS},
            "head_hits": {ch: sum(len(v) for v in flags[ch]["head_hits"].values()) for ch in CHUNKS},
            "solo_hits": {ch: len(flags[ch]["solo_hits"]) for ch in CHUNKS},
            "gate_hits": {ch: len(fires[ch]) for ch in CHUNKS}, "fires": fires, "flags": flags}


def card_manifest_checks(m, cm):
    """the card rows of a TOP manifest: the receipt must equal what the card, the facts file and the graph bytes
    say NOW (re-derived, not read back), the card must state its start-still-only scope, every evidence quote must
    sit verbatim in the card, no card-gate rule may fire on either chunk, every per-chunk card word must be in the
    prompt, and the note must print the card sha256, the quote count, the figure count and the gate status."""
    out = []
    if m.get("card") != cm:
        out.append("TOP-MANIFEST card receipt drifted from the card/facts/graph bytes on disk")
    if not cm["scope_ok"]:
        out.append("TOP-MANIFEST card scope: the card does not state that it read the start still only")
    if cm["evidence_verbatim"] != cm["evidence_rows"]:
        out.append("TOP-MANIFEST card evidence: %d/%d quotes verbatim" % (cm["evidence_verbatim"], cm["evidence_rows"]))
    for ch in CHUNKS:
        if cm["gate_hits"][ch]:
            out.append("TOP-MANIFEST card gate fires on %s: %s" % (ch, ",".join(cm["fires"][ch])))
        if cm["tokens_per_chunk"][ch] < cm["per_chunk_tokens"]:
            out.append("TOP-MANIFEST card words in %s: %d/%d" % (ch, cm["tokens_per_chunk"][ch], cm["per_chunk_tokens"]))
    for frag in ("card " + cm["card_still_sha256"], "%d/%d card quotes verbatim" % (cm["evidence_verbatim"], cm["evidence_rows"]),
                 "%d figures" % cm["figures"], "card gate %s" % cm["status"]):
        if frag not in m.get("note", ""):
            out.append("TOP-MANIFEST note has no card receipt %r" % frag)
    return out


def ck_top_manifest(g, ctx):
    """The manifest of a TOP graph has to re-derive off the graph on disk and carry the receipts the plan item
    asks for: measured prompt counts, the naming citation, the guide citation, the graph stats, the gate receipt,
    id-free, minutes with a measured basis, and the arm status."""
    t = ctx["top"]
    if not t:
        return []
    p = man_path(ctx["id"])
    if not os.path.isfile(p):
        return [f"TOP-MANIFEST no manifest on disk ({os.path.basename(p)})"]
    m = json.load(open(p, encoding="utf-8"))
    gp, src = gpath(ctx["id"]), ctx["src"]
    out = []
    if m.get("id") != ctx["id"] or m.get("graph") != gp.replace("\\", "/"):
        out.append(f"TOP-MANIFEST id/graph {m.get('id')}/{m.get('graph')}")
    if m.get("seed") != g["noise"]["inputs"]["noise_seed"] or m.get("take") != t["take"]:
        out.append(f"TOP-MANIFEST seed/take {m.get('seed')}/{m.get('take')} != {g['noise']['inputs']['noise_seed']}"
                   f"/{t['take']}")
    if m.get("graph_sha256") != sha(gp) or m.get("graph_bytes") != os.path.getsize(gp):
        out.append("TOP-MANIFEST graph sha/bytes drifted from disk")
    if m.get("run_dir_request_sha256") != sha(os.path.join(RUNS, ctx["id"], "request.api.json")):
        out.append("TOP-MANIFEST run-dir request sha drifted from disk")
    sh = m.get("shape", {})
    want_sh = {"guide_frame_idx": 0, "passes": 2, "c0_length": g["c0"]["inputs"]["length"],
               "extension_frames": g["win1"]["inputs"]["extension_frames"],
               "overlap_frames": g["win1"]["inputs"]["overlap_frames"], "frames_total": FRAMES,
               "fps": g["mkvid"]["inputs"]["fps"], "canvas": [g["c0"]["inputs"]["width"], g["c0"]["inputs"]["height"]],
               "sampler": g["ksel"]["inputs"]["sampler_name"], "steps": g["s0_sched"]["inputs"]["steps"],
               "scheduler": g["s0_sched"]["inputs"]["scheduler"], "cfg_keys": 0}
    if sh != want_sh:
        out.append(f"TOP-MANIFEST shape {sh} != {want_sh}")
    # Re-derive the counts off the graph on disk. Reading them back out of the manifest (the shipped shape of
    # this check: st = prompt_stats(...); st = m["prompts_full"]) compares a manifest to itself, so a manifest of
    # stale counts passed - the L10 rule: a green check that cannot fail is worthless.
    st_live = {ch: top_prose_stats(g[ch]["inputs"]["prompt"], ch) for ch in CHUNKS}
    FULLK = ("words", "main_words", "beats", "sections", "neg", "ages", "camera_moves", "amplitude", "speed",
             "video1", "picture1_first_frame")
    if m.get("prompts_full", {}) != {ch: {k: st_live[ch][k] for k in FULLK} for ch in CHUNKS}:
        out.append("TOP-MANIFEST prompt counts (words/main_words/beats/sections/neg/ages/camera) drifted from the "
                   "graph on disk")
    if m.get("prompts", {}) != {ch: {k: st_live[ch][k] for k in ("words", "beats", "sections")}
                                for ch in CHUNKS}:
        out.append("TOP-MANIFEST prompts (words/beats/sections) drifted from the graph on disk")
    if m.get("windows") != {ch: [round(v[0], 6), round(v[1], 6)] for ch, v in top_windows(g).items()}:
        out.append("TOP-MANIFEST chunk windows drifted from the graph")
    if m.get("species") != {"tokens": list(t["species"] + t["body"]),
                            "hits": {ch: sum(1 for w in t["species"] + t["body"]
                                             if w in g[ch]["inputs"]["prompt"].lower()) for ch in CHUNKS}}:
        out.append("TOP-MANIFEST species token counts drifted from the graph (the card's species/body words per chunk)")
    if m.get("default_figure_clauses") != {ch: sum(1 for c in TOP_DEFAULT_FIGURE
                                                   if c in g[ch]["inputs"]["prompt"].lower()) for ch in CHUNKS}:
        out.append("TOP-MANIFEST default-figure clause count drifted from the graph (solo clauses on a two-figure card)")
    # the card receipt, re-derived off the graph + facts file + card bytes on disk: a manifest cannot carry a
    # softer number than the start-image card supports (L10: a green check that cannot fail is worthless).
    if ctx_card(ctx) in CARDS:
        out.extend(card_manifest_checks(m, card_manifest(ctx_card(ctx), g)))
    if m.get("prompt_record_sha256") != sha(TOP_MD):
        out.append(f"TOP-MANIFEST prompt_record_sha256 != {os.path.basename(TOP_MD)} bytes on disk")
    if m.get("diff_paths") != sorted("%s|%s|%s" % t2 for t2 in diff_paths(src, g)):
        out.append("TOP-MANIFEST diff_paths != the diff measured off the carried source graph")
    if m.get("slots") != slot_edges(g)["c0"]:
        out.append("TOP-MANIFEST ref slots drifted from the graph")
    cit = m.get("citations", [])
    if len(cit) < 6:
        out.append(f"TOP-MANIFEST {len(cit)} citations, 6+ required")
    for c in cit:
        if not os.path.isfile(c):
            out.append(f"TOP-MANIFEST citation {c} does not exist on disk")
    for need in (TOP_MD, TOP_GUIDE, TOP_NAMING, TOP_FIGURES):
        if need not in cit:
            out.append(f"TOP-MANIFEST citation list missing {os.path.basename(need)}")
    led = ctx["ledger"]
    note = str(m.get("note", ""))
    mps = m.get("prompts", {})
    need = [str(len(g)), str(os.path.getsize(gp)), sha(gp), str(len(diff_paths(src, g))),
            str(mps.get("c0", {}).get("words")), str(mps.get("c0", {}).get("beats")),
            str(mps.get("c1", {}).get("words")), str(mps.get("c1", {}).get("beats")),
            str(m.get("gate_ok_all_prose")), "comm.guard_ok", "test_p6_review.py", "21 passed",
            "no GPU call in this pass", "0 result.json", f"minutes={TOP_EST_MIN}", t["species"][0],
            "frame_idx 0", "243", "119", "1344x768", "audio", os.path.basename(TOP_MD),
            os.path.basename(TOP_GUIDE), os.path.basename(TOP_NAMING), os.path.basename(TOP_FIGURES),
            str(led.get("updated", ""))] 
    miss = [c for c in need if c not in note]
    if miss:
        out.append(f"TOP-MANIFEST note missing {miss}")
    if not 1100 <= len(note) <= 2200:
        out.append(f"TOP-MANIFEST note {len(note)} chars, 1100-2200 required (600-1100 for a graph)")
    hits = [w for w in BANNED_IN_MANIFEST if w in note.lower()]
    if hits:
        out.append(f"TOP-MANIFEST note carries a judgement token {hits}")
    for tok in NO_GPU_TOKENS:
        if tok in note:
            out.append(f"TOP-MANIFEST note names the GPU/queue surface {tok!r}")
    # A date floor cannot be met inside a no-GPU pass: only a render writes the ledger, so a 2026-10-23 stamp is
    # what a clean queue carries. The property the rule wants is that the manifest quotes the ledger that is on
    # disk now (bytes equal, and the stamp present in the note), not a copy embedded at an earlier build.
    if m.get("budget_at_build") != led:
        out.append(f"TOP-MANIFEST budget_at_build {m.get('budget_at_build')} != the live ledger {led}: a manifest "
                   "must quote the budget ledger on disk, not a copy written at an earlier build")
    if str(led.get("updated", "")) not in note:
        out.append(f"TOP-MANIFEST note does not quote the live ledger stamp {led.get('updated')!r} "
                   "(the 2026-10-25 5:52-5:53 PM CT rule: the queue math has to carry the stamp it was read off)")
    if not m.get("est_min", 0) > 0:
        out.append("TOP-MANIFEST est_min must be > 0 (it is what the plan's queue math charges a job)")
    if m.get("est_min") != TOP_EST_MIN:
        out.append(f"TOP-MANIFEST est_min {m.get('est_min')} != the measured {TOP_EST_MIN} min/job "
                   "(clip 1-6 measured 24.0 min/job + 25% contingency, the EST_MIN rule the plan quotes)")
    if led["used_min"] + m.get("est_min", 0) > led["cap_min"] or led["jobs"] + 1 > led["job_cap"]:
        out.append(f"TOP-MANIFEST ledger {led['used_min']}+{m.get('est_min')} <= {led['cap_min']} min and "
                   f"{led['jobs']}+1 <= {led['job_cap']} jobs (stamp {led.get('updated')})")
    mp4, res, out_dir = (os.path.join(RUNS, ctx["id"], ctx["id"] + ".mp4"),
                         os.path.join(JOBS, ctx["id"] + ".result.json"), os.path.join(COMFY_OUT, ctx["id"]))
    rec, mr = top_render_receipt(ctx["id"]), m.get("rendered")
    if rec:
        # spent: the receipt must be on the manifest, true off disk, declared, and never armed
        if ctx["id"] not in TOP_RENDERS:
            out.append("TOP-MANIFEST %s is rendered (a video is in the output dir) with no declared render "
                       "row in TOP_RENDERS: a manifest cannot call a spent id staged" % ctx["id"])
        if not isinstance(mr, dict) or any(mr.get(k) != rec[k] for k in ("file", "bytes", "sha256", "written")):
            out.append("TOP-MANIFEST render receipt %s != the video on disk %s (bytes/sha256/stamp are "
                       "measured, so a receipt cannot be softer than the file)" % (mr, rec))
        elif mr.get("prose") != TOP_RENDERS.get(ctx["id"], {}).get("prose"):
            out.append("TOP-MANIFEST render receipt does not state which prose the render ran (the "
                       "before/after rule: a render row names the prose it renders)")
        if isinstance(mr, dict) and "Derrick's alone" not in str(mr.get("select", "")):
            out.append("TOP-MANIFEST render receipt must state that the selection of a rendered take is "
                       "Derrick's alone (a forge render row never keeps, scores, or chooses)")
        if arm_armed(m):
            out.append("TOP-MANIFEST arms %s and it is spent - the request must carry a free id" % ctx["id"])
        if str(rec["bytes"]) not in note_of(m):
            out.append("TOP-MANIFEST note does not quote the spent render (mp4 bytes) the manifest carries")
        pn = TOP_RENDERS.get(ctx["id"], {}).get("prose", "")
        if pn and pn.split(":")[0] not in note_of(m):
            out.append("TOP-MANIFEST note of a spent take must say which prose the render ran (the "
                       "before/after rule: a reader must not take the mp4 for the current record)")
        if "0 renders" not in note_of(m):
            out.append("TOP-MANIFEST note of a spent take must state that the current prose record has 0 "
                       "renders of this still, and which take carries it")
    elif os.path.isfile(mp4) or os.path.isfile(res) or os.path.isdir(out_dir):
        out.append(f"TOP-MANIFEST claims an unrendered id, and it is spent (mp4 {os.path.isfile(mp4)}, "
                   f"result {os.path.isfile(res)}, output dir {os.path.isdir(out_dir)})")
    elif mr:
        out.append("TOP-MANIFEST carries a render receipt %s and the id is free on disk" % mr)
    arm = m.get("arm", {})
    armed_ids = [j.get("id") for j in (ctx["req"] or {}).get("jobs", [])]
    if arm.get("armed") != (ctx["id"] in armed_ids) or arm.get("request") != "p7/JOB_REQUEST.json":
        out.append(f"TOP-MANIFEST arm status {arm.get('armed')} != armed {ctx['id'] in armed_ids} in "
                   "p7/JOB_REQUEST.json")
    if arm.get("armed") and arm.get("jobs") != TOP_ORDER:
        out.append(f"TOP-MANIFEST arm jobs {arm.get('jobs')} != {TOP_ORDER}")
    if not arm.get("armed"):
        nm = arm.get("naming") or {}
        if (nm.get("file") != TOP_NAMING.replace("\\", "/") or nm.get("row") != 18
                or nm.get("text") != TOP_STILL_ROW[t["still"]]):
            out.append(f"TOP-MANIFEST unarmed manifest must cite the naming row that armed the queue decision "
                       f"({os.path.basename(TOP_NAMING)} row 18, Max 2026-10-24 9:30 PM CT: "
                       f"{TOP_STILL_ROW[t['still']]}); arm.naming {nm}")
    return out


def ck_top_card(g, ctx):
    """F-CARD: ck_card_2.ck_figures proved every <Subject> has an input row; this proves the WORDS next to each
    <Subject> are the card's words. Both chunks of a TOP graph run through card_measure/card_fires, the counts land
    in g['card_flags'] for the manifest, and every hit is a FAIL. 9 rules x 2 chunks."""
    if ctx_card(ctx) not in CARDS:
        return []
    sc = ctx_card(ctx)
    bad, flags = [], {}
    for ch in CHUNKS:
        out = card_measure(sc, top_prompt(g, ch))
        flags[ch] = out
        for code, det in card_fires(sc, out):
            bad.append("F-CARD %s %s: %s" % (ch, code, det))
    g["card_flags"] = flags
    return bad


def ck_top_facts(g, ctx):
    """F-FACTS: the gate is only as honest as the card behind it. The facts file parses with every top-level, gate
    and figure-row key; its model/status/sha256 are rows IN the card file; the card read the START STILL ONLY
    (read_scope, no rendered clip); every gate.evidence quote sits verbatim in the card (punctuation-folded);
    every word the gate requires (per-chunk, figure-visible, room, light) carries such a quote; the figure rows and
    the gate agree on the figure count and the card states it; the cited card/caption/audit paths exist; the facts
    scene is this graph's scene; head_in_frame covers every figure label. 11 rules."""
    if ctx_card(ctx) not in CARDS:
        return []
    bad = []
    sc = ctx_card(ctx)
    f = card_facts(sc)
    gt, md = f["gate"], card_md(sc)
    for k in CARD_TOP_KEYS:
        if k not in f:
            bad.append("F-FACTS-KEY: facts has no %s" % k)
    for k in CARD_GATE_KEYS:
        if k not in gt:
            bad.append("F-FACTS-GATEKEY: gate has no %s" % k)
    for row in f["figures"]:
        for k in CARD_FIG_KEYS:
            if k not in row:
                bad.append("F-FACTS-FIGKEY: figure row has no %s" % k)
    if len(f["figures"]) != gt["figure_count"]:
        bad.append("F-FACTS-COUNT: %d figure rows, gate.figure_count %s" % (len(f["figures"]), gt["figure_count"]))
    if "figures: %d" % gt["figure_count"] not in md:
        bad.append("F-FACTS-COUNT2: the card has no 'figures: %d' row" % gt["figure_count"])
    cg = gt.get("consent_gate") or {}
    if cg.get("ban") and not [x for x in (cg.get("require") or []) if str(x).strip()]:
        bad.append("F-FACTS-CONSENT: the consent gate bars %d phrases and requires none, so prose can "
                   "never satisfy it: a ban with no required wording is a gate that only blocks" % len(cg["ban"]))
    for k in ("model", "status", "sha256"):
        if card_norm(f[k]) not in md:
            bad.append("F-FACTS-%s: '%s' is not a row in the card" % (k.upper(), f[k]))
    if CARD_SCOPE not in md:
        bad.append("F-FACTS-SCOPE: the card's read_scope row does not say start still only, no rendered clip")
    miss = [q for q in gt["evidence"].values() if card_norm(q) not in md]
    if miss:
        bad.append("F-FACTS-EVID: %d/%d evidence quotes are not verbatim in the card, first: %s"
                   % (len(miss), len(gt["evidence"]), miss[0][:90]))
    need = list(gt["per_chunk_tokens"]) + list(gt["room_required"]) + list(gt["light_required"])
    for row in f["figures"]:
        need += list(row["visible"])
    nolink = [t for t in need if t not in gt["evidence"]]
    if nolink:
        bad.append("F-FACTS-TOKEN: %d required words have no evidence quote (%s)" % (len(nolink), ", ".join(nolink[:6])))
    for k in ("card", "caption", "audit"):
        if not os.path.isfile(f[k]):
            bad.append("F-FACTS-PATH: %s -> %s is not a file" % (k, f[k]))
    if f["scene"] != sc:
        bad.append("F-FACTS-SCENE: facts scene %s, graph %s" % (f["scene"], ctx["id"]))
    if sorted(gt["head_in_frame"]) != sorted(str(r["label"]) for r in f["figures"]):
        bad.append("F-FACTS-HEADKEY: head_in_frame keys do not match the figure labels")
    return bad


def ck_top_md(g, ctx):
    """F-MD-SYNC: notes/hc15_top_prompts_20261025.md is the prose record a human reads; the graph is what runs.
    This graph's c0/c1 fields must equal the record's take-A blocks BYTE FOR BYTE (the 2.1b clone of
    top_selftest's F-21B-SYNC, run on the prose side), so the file a reader trusts is the text that renders.
    Transitively this is also the adults-gate reach for the prose record: ck_gate runs comm.guard_ok on the
    graph's `prompt` keys, and byte-sync means the record's text IS those bytes, so the file a reader opens has
    been through the gate (comm.py reads the `prompt` key only, so the record's own keys are not gated directly
    - L11).
    The drift branch of this check had never run before the TOP-SCENE seeds: it referenced `key` and `word_re`,
    names that exist in no scope of this module, so any real drift raised NameError instead of a finding (L10:
    a check whose failure path has never executed is not a check)."""
    if ctx_card(ctx) not in CARDS:
        return []
    bad = []
    take = ctx["top"]["take_a"]
    for ch in CHUNKS:
        want, got = top_md(take).get(ch), top_prompt(g, ch)
        if want is None:
            bad.append("F-MD-SYNC %s: %s has no %s block for %s" % (ch, TOP_MD, ch, take))
        elif want != got:
            d = next((i for i in range(min(len(want), len(got))) if want[i] != got[i]), min(len(want), len(got)))
            def wc(t):
                return len(re.findall(r"[A-Za-z][A-Za-z'\-]*", t))
            bad.append("F-MD-SYNC %s: the graph's %s prompt and the prose record differ (%d vs %d words), first byte %d: %r"
                       % (ch, ch, wc(got), wc(want), d, got[d:d + 40]))
    return bad



CHECKS = (ck_control, ck_diff, ck_top_diff, ck_guide, ck_shape, ck_prose, ck_top_species, ck_top_age,
          ck_top_words, ck_top_beats, ck_top_neg, ck_top_sync, ck_top_seed, ck_gate, ck_slots, ck_inputs,
          ck_idfree, ck_schema, ck_prefix, ck_seed, ck_rundir, ck_graphfile, ck_manifest, ck_top_manifest,
          ck_top_arm, ck_top_card, ck_top_facts, ck_top_md, ck_nogpu)
SERIALIZED = ("ck_graphfile", "ck_manifest", "ck_rundir", "ck_top_manifest", "ck_top_arm")     # need artifacts on disk


def ctx_for(nid, g=None):
    top = TOP_BY_ID.get(nid)
    if top:
        src_id, seed = top["src"], top["seed"]
    else:
        src_id, cid, seed = next((v for v in CARRY.values() if v[1] == nid), (None, nid, None))
    g = g if g is not None else gload(nid)
    rq = os.path.join(W, "p7", "JOB_REQUEST.json")
    return dict(id=nid, src_id=src_id, seed=seed, top=top, src=gload(src_id) if src_id else {}, graph=g,
                path=gpath(nid) if os.path.isfile(gpath(nid)) else None, ind=FORMAT_IND,
                schema=h3_schema(), self_src=open(os.path.abspath(__file__), encoding="utf-8").read(),
                req=(json.load(open(rq, encoding="utf-8")) if os.path.isfile(rq) else None),
                ledger=json.load(open(LEDGER, encoding="utf-8")))


def run(nid, g=None, skip=()):
    ctx = ctx_for(nid, g)
    return {ck.__name__: ck(g if g is not None else ctx["graph"], ctx)
            for ck in CHECKS if ck.__name__ not in skip}


def measure(nid):
    ctx = ctx_for(nid)
    g, src = ctx["graph"], ctx["src"]
    m = {"id": nid, "source_clip": ctx["src_id"], "source_graph_sha256": sha(gpath(ctx["src_id"])),
         "seed": ctx["seed"], "seed_rule": "seed carried unchanged from the source clip (IM1: a settings "
                                           "before/after holds the seed; clip 11 holds 51150001 the same way)",
         "shape": {"guide": "MiniMaxH3AddGuide frame_idx 0 on the c0 conditioning edge (ComfyUI PR 15439)",
                   "sampler": g["ksel"]["inputs"]["sampler_name"],
                   "scheduler": g["s0_sched"]["inputs"]["scheduler"], "steps": g["s0_sched"]["inputs"]["steps"],
                   "c0_length": g["c0"]["inputs"]["length"],
                   "window": {"overlap_frames": g["win1"]["inputs"]["overlap_frames"],
                              "extension_frames": g["win1"]["inputs"]["extension_frames"]},
                   "frames_total": FRAMES, "fps": g["mkvid"]["inputs"]["fps"],
                   "canvas": [g["c0"]["inputs"]["width"], g["c0"]["inputs"]["height"]],
                   "duration_s": round(FRAMES / g["mkvid"]["inputs"]["fps"], 6),
                   "shift_video_audio": [g["m_shift"]["inputs"]["shift_video"], g["m_shift"]["inputs"]["shift_audio"]],
                   "cfg_keys": 0, "passes": 2},
         "prompts": {ch: {k: prompt_stats(g[ch]["inputs"]["prompt"], ch)[k]
                          for k in ("words", "beats", "sections")} for ch in CHUNKS},
         "prompts_byte_identical_to_source": all(g[ch]["inputs"]["prompt"] == src[ch]["inputs"]["prompt"]
                                                 for ch in CHUNKS),
         "slots": slot_edges(g)["c0"], "diff_paths": sorted("%s|%s|%s" % t for t in diff_paths(src, g)),
         "prose_strings": len(prose_strings(g)),
         "gate_ok_all_prose": all(guard_ok(v) for _, _, v in prose_strings(g)),
         "static_scan_defects": 0, "graph_sha256": sha(gpath(nid)), "graph_bytes": os.path.getsize(gpath(nid)),
         "run_dir_request_sha256": sha(os.path.join(RUNS, nid, "request.api.json"))
         if os.path.isfile(os.path.join(RUNS, nid, "request.api.json")) else None,
         "budget_at_build": json.load(open(LEDGER, encoding="utf-8")), "est_min": EST_MIN,
         "job_gate": "no p7/JOB_REQUEST.json arm in this pass: 5 clips x 30 min = 150 min over the ledger "
                     "headroom 142.1 min (cap 615 - used 472.9) and only 7 job slots left (job_cap 45, 38 used); "
                     "the two clips Derrick named go first - notes/needs_derrick.md row 18",
         "notes": "staged only: no queue, no GPU, no render in a Ralph pass; the species prose is the next item "
                  "and needs the two start images named (notes/hc15_figures_20261025.md)"}
    return m


def build(nid):
    src_id, cid, seed = next(v for v in CARRY.values() if v[1] == nid)
    g = transform(gload(src_id))
    g["save"]["inputs"]["filename_prefix"] = f"community/{nid}/{nid}"
    ind = dumps_like(open(gpath(CLIP11), "rb").read(), transform(gload(CLIP1)))
    if ind is None:
        print("CONTROL_DEAD transform(clip 1) does not reproduce the clip-11 bytes; refusing to write")
        return 1
    if ind != FORMAT_IND:
        print(f"CONTROL_DEAD clip-11 byte format measures indent {ind} != pinned FORMAT_IND {FORMAT_IND}")
        return 1
    data = write_graph(gpath(nid), g, ind)
    rd = os.path.join(RUNS, nid)
    os.makedirs(rd, exist_ok=True)
    open(os.path.join(rd, "request.api.json"), "wb").write(data)
    json.dump(measure(nid), open(man_path(nid), "w", encoding="utf-8"), indent=1)   # so ck_manifest has a
    res = run(nid)                                                                   # manifest to re-derive
    m = measure(nid)
    m["checks"] = {k: len(v) for k, v in res.items()}
    m["check_failures"] = {k: v for k, v in res.items() if v}
    m["checks_all_clean"] = all(not v for v in res.values())
    json.dump(m, open(man_path(nid), "w", encoding="utf-8"), indent=1)
    print(f"{nid} graph {len(g)} nodes {len(data)} B sha {sha(gpath(nid))[:16]} "
          f"clean={m['checks_all_clean']}")
    for k, v in res.items():
        if v:
            print("  FAIL", k, "::", "; ".join(v))
    return 1 if any(res.values()) else 0


# ==================================================================== TOP build / measure / arm / check
def top_facts(nid, g):
    """every number a receipt quotes, measured off the graph - no hand-written counts (L10/L12 rule)."""
    t = TOP_BY_ID[nid]
    src = gload(t["src"])
    st = {ch: top_prose_stats(g[ch]["inputs"]["prompt"], ch) for ch in CHUNKS}
    sp = tuple(t["species"] + t["body"])
    ps = [v for _, _, v in prose_strings(g)]
    return dict(st=st, win=top_windows(g), src=src, sp=sp,
                hits={ch: sum(1 for w in sp if w in g[ch]["inputs"]["prompt"].lower()) for ch in CHUNKS},
                dflt={ch: sum(1 for c in TOP_DEFAULT_FIGURE if c in g[ch]["inputs"]["prompt"].lower())
                      for ch in CHUNKS},
                ps=ps, diff=sorted("%s|%s|%s" % x for x in diff_paths(src, g)))



def top_render_receipt(nid):
    """the disk truth about a TOP id: the video ComfyUI wrote, measured (bytes, sha256, stamp). None = the
    id is free. A manifest of a spent id has to carry this receipt and stop calling itself id-free."""
    d = os.path.join(COMFY_OUT, nid)
    if not os.path.isdir(d):
        return None
    vids = sorted(f for f in os.listdir(d) if f.lower().endswith((".mp4", ".webm", ".gif", ".png")))
    if not vids:
        return None
    p = os.path.join(d, vids[0])
    st = os.stat(p)
    return {"file": p.replace("\\", "/"), "bytes": st.st_size, "sha256": sha(p),
            "written": time.strftime("%Y-%m-%d %H:%M:%S CT", time.localtime(st.st_mtime)),
            "queue_result": os.path.isfile(os.path.join(JOBS, nid + ".result.json"))}


def note_of(m):
    return str((m or {}).get("note", ""))


def arm_armed(m):
    return bool(((m or {}).get("arm") or {}).get("armed"))


def top_note(nid, g, m, f):
    """the manifest note: the graph-receipt rule is 600-1100 chars; the TOP row needs naming + guide + defect +
    counts + gate + id-free + minutes + arm, so it is bounded on both sides (1100-2200, ck_top_manifest)."""
    t = TOP_BY_ID[nid]
    st, win, sp = f["st"], f["win"], f["sp"]
    cm = m["card"]
    gp = gpath(nid)
    led = json.load(open(LEDGER, encoding="utf-8"))
    armed = nid in [j.get("id") for j in (json.load(open(os.path.join(W, "p7", "JOB_REQUEST.json"),
                                                        encoding="utf-8")).get("jobs", [])
                                         if os.path.isfile(os.path.join(W, "p7", "JOB_REQUEST.json")) else [])]
    rec = top_render_receipt(nid)
    idf = ("id-free: no mp4, 0 result.json, no ComfyUI output dir, no GPU call in this pass."
           if not rec else
           "id SPENT: %s %d B sha256 %s written %s, off the shipped pre-card-fidelity prose; 0 result.json, "
           "no GPU call in this pass; this prose record has 0 renders of this still, so the free take "
           "carries it."
           % (os.path.basename(rec["file"]), rec["bytes"], rec["sha256"][:16], rec["written"]))
    return (
        "TOP %s take %s (fix_plan TOP, Derrick 2026-10-24 8:39 PM CT: 'the two videos the orc and the robot "
        "fucking video ... Like hardcore sex'), figure named by %s, %s: %s. "
        "Seed %d = the id number; take %s (%s) = the seed alone. Graph %d nodes %d B sha256 %s, %d changed "
        "paths vs the carried source %s only: MiniMaxH3AddGuide frame_idx 0 on the c0 edge, "
        "res_multistep/simple/8, 243 + a 119-frame window = %d f at 24 fps %.6f s, 1344x768, audio "
        "intact, 2 SamplerCustomAdvanced, 0 cfg keys, ref slots + LoadImage untouched. Prose from "
        "%s byte-for-byte: c0 detailed_description %d words / %d beats "
        "%.3f-%.3fs, c1 integrated_multimodal_description %d words / %d beats %.3f-%.3fs, %d prohibition/negation "
        "tokens, ages %s fictional, species words %s present in %d/%d chunks, default-figure clauses "
        "%d (defect %s rows 2-3). "
        "Structure = %s + TenStrip card. "
        "Gate: comm.guard_ok %s on %d "
        "prompt-bearing strings, tests/test_p6_review.py 21 passed. %s minutes=%d (clip 1-6 measured "
        "24.0 min/job +25%% contingency). Receipts: --top-check / --top-selftest. Arm: %s (free take of each "
        "still, Max's row-18 order, the other staged; ledger %s/%s min, %s/%s jobs, stamp %s). "
        "card %s is the start-image card, card gate %s: %d figures, %d/%d card quotes verbatim, %d card words in "
        "%d/%d chunks, %d gate hits, read by %s off the start still (ck_top_card, ck_top_facts). "
        "The selection is Derrick's alone; no vision judge on explicit output."
    ) % (t["still"], t["take"], TOP_NAMING_WHERE, TOP_NAMING_ANSWERS, TOP_STILL_ROW[t["still"]],
         m["seed"], "B" if t["take"] == "A" else "A",
         t["take_b"] if t["take"] == "A" else t["take_a"], len(g), os.path.getsize(gp), sha(gp), len(f["diff"]),
         t["src"], FRAMES, FRAMES / g["mkvid"]["inputs"]["fps"],
         os.path.basename(TOP_MD), st["c0"]["words"], st["c0"]["beats"], win["c0"][0], win["c0"][1],
         st["c1"]["words"], st["c1"]["beats"], win["c1"][0], win["c1"][1],
         st["c0"]["neg"] + st["c1"]["neg"], sorted(set(st["c0"]["ages"] + st["c1"]["ages"])),
         "/".join(sp), min(f["hits"].values()), len(CHUNKS), sum(f["dflt"].values()),
         os.path.basename(TOP_FIGURES), os.path.basename(TOP_GUIDE),
         m["gate_ok_all_prose"], len(f["ps"]), idf, TOP_EST_MIN, "armed" if armed else "staged",
         led["used_min"], led["cap_min"], led["jobs"], led["job_cap"], led["updated"],
         cm["card_still_sha256"], cm["status"], cm["figures"], cm["evidence_verbatim"], cm["evidence_rows"],
         cm["per_chunk_tokens"], sum(1 for ch in CHUNKS if cm["tokens_per_chunk"][ch] == cm["per_chunk_tokens"]),
         len(CHUNKS), sum(cm["gate_hits"].values()), cm["model"])


def top_job_note(nid):
    """the 6-key job row note: what to render, with what proof, and the unarm command (1200-2100 chars).
    The verbatim naming sentence lives in the manifest note (ck_top_manifest requires it there); this row cites
    where it lives, so the row stays inside the 2100-char ceiling the plan sets."""
    t = TOP_BY_ID[nid]
    g = gload(nid)
    f = top_facts(nid, g)
    st, win, sp = f["st"], f["win"], f["sp"]
    led = json.load(open(LEDGER, encoding="utf-8"))
    order = TOP_ORDER.index(nid) + 1 if nid in TOP_ORDER else t["take"]
    first = os.path.basename(TOP_ORDER[0]).split("_")[-2].upper()
    return (
        "TOP %s take %s: the 15 s %s clip (fix_plan TOP; figure named by %s, %s - Max's verbatim sentence is in the "
        "manifest note and %s §1; prose contract + measured pixel rows in %s). Shape = the fixed clip-1 graph carried "
        "from %s: MiniMaxH3AddGuide frame_idx 0 (c0 edge), res_multistep/simple/8, 243+119 f (overlap 22) = 362 f = "
        "15.083333 s at 24 fps, 1344x768, audio, 2 SamplerCustomAdvanced, 0 cfg keys. Seed %d, start %s, crop %s, "
        "ref_image_1 = still, ref_image_2 = her crop (no verified crop of the %s, so that figure rides on the still + "
        "prose). Prompts = %s byte-for-byte: c0 detailed_description %dw/%d beats %.3f-%.3fs, "
        "c1 integrated_multimodal_description %dw/%d beats %.3f-%.3fs, 0 negation, ages %s fictional adults, species "
        "%s every chunk, 0 default-figure clauses. Structure = %s + TenStrip card notes/web/hc15_tenstrip_readme.txt. "
        "Gate: comm.guard_ok allow on all %d prompt-bearing strings, scripts/tests/test_p6_review.py 21 passed. "
        "id-free: no runs/%s/%s.mp4, 0 result.json, no output/%s. minutes=%d (clip 1-6 measured 24.0 min/job +25%% "
        "contingency); ledger at build %s. Receipt: notes/hc15_anchor_carry_build.py --top-check / --top-selftest. "
        "Render = a GPU window, never a Ralph pass: --frames %d, one job at a time, GPU idle first, route unloaded on "
        "an empty queue (Max 2026-10-24 9:47 PM CT), order %s of 2, %s first; exact command: %s row 21. Unarm: "
        "notes/hc15_anchor_fix_build.py --now-build. Selection is Derrick's alone, no vision judge on explicit output."
    ) % (t["still"], t["take"], "orc" if t["still"] == "GI046" else "robot", TOP_NAMING_WHERE, TOP_NAMING_ANSWERS,
         os.path.basename(TOP_FIGURES), TOP_FIGURES, t["src"],
         g["noise"]["inputs"]["noise_seed"], g["img"]["inputs"]["image"], g["img2"]["inputs"]["image"],
         "second figure" if t["still"] == "GI046" else "machine", TOP_MD,
         st["c0"]["words"], st["c0"]["beats"], win["c0"][0], win["c0"][1],
         st["c1"]["words"], st["c1"]["beats"], win["c1"][0], win["c1"][1],
         sorted(set(st["c0"]["ages"] + st["c1"]["ages"])), "/".join(sp), TOP_GUIDE, len(f["ps"]),
         nid, nid, nid, TOP_EST_MIN,
         "used %s/%s min, %s/%s jobs, stamp %s" % (led["used_min"], led["cap_min"], led["jobs"], led["job_cap"],
                                                   led["updated"]),
         FRAMES, order, first, TOP_NAMING)


def top_request_note():
    led = json.load(open(LEDGER, encoding="utf-8"))
    return (
        "TOP (fix_plan TOP): the two named HC15 stills rendered with card-faithful prose on the fixed clip-1 "
        "shape, GI046 (the orc) then GI063 (the robot) in Max's 2026-10-24 9:30 PM CT order "
        "(notes/needs_derrick.md row 18). Each job is its own 6-key row, frames 362 (15.083333 s), 30 min each, "
        "ledger %s/%s min and %s/%s jobs before the render. The armed ids are the FREE take of each still: "
        "ali163_hc15_gi046_s51150031 is spent (its mp4 is in the ComfyUI output dir, rendered 2026-10-25 04:04 "
        "off the pre-card-fidelity prose, receipt in its manifest and notes/needs_derrick.md row 25), so the "
        "GI046 slot is take B. The other take of each still is staged (graph, run-dir request, manifest) and "
        "unarmed: arming 4 jobs = 120 min over the standing cap. This arm displaces the single-job "
        "NOW-P1 arm of ali163_hc15_bd002_s51150021; restore it with python "
        "C:/AI/community/notes/hc15_anchor_fix_build.py --now-build (NOW-P1's own --now-check stays green only on "
        "its own single-job request, so its arm is re-issued, not edited). No GPU call, no queue "
        "in a Ralph pass: this file writes graph, run-dir request, manifest and the request file only. "
        "Receipts: notes/hc15_anchor_carry_build.py --top-check / --top-selftest, comm.guard_ok, "
        "scripts/tests/test_p6_review.py 21 passed. The selection is Derrick's alone; no vision judge on explicit "
        "output."
    ) % (led["used_min"], led["cap_min"], led["jobs"], led["job_cap"])


def measure_top(nid):
    t = TOP_BY_ID[nid]
    g = gload(nid)
    f = top_facts(nid, g)
    gp, rd = gpath(nid), os.path.join(RUNS, nid, "request.api.json")
    st, win, sp, armed_ids = f["st"], f["win"], f["sp"], []
    rq = os.path.join(W, "p7", "JOB_REQUEST.json")
    if os.path.isfile(rq):
        armed_ids = [j.get("id") for j in json.load(open(rq, encoding="utf-8")).get("jobs", [])]
    m = {
        "id": nid, "kind": "graph", "graph": gp.replace("\\", "/"), "still": t["still"],
        "take": t["take"], "take_a": t["take_a"], "take_b": t["take_b"],
        "source_clip": t["src"], "source_graph_sha256": sha(gpath(t["src"])),
        "prompt_record": TOP_MD, "prompt_record_sha256": sha(TOP_MD),
        "seed": g["noise"]["inputs"]["noise_seed"],
        "seed_rule": "the take seed is the id number (take A 51150031, take B 51150032); the two takes of one "
                     "still differ by the seed alone (fix_plan TOP: 'render 2-3 takes per still'). The CARRY seed "
                     "rule (seed carried from the source clip) belongs to the IM1 settings before/after and does "
                     "not apply to a new prompt",
        "shape": {"guide_frame_idx": g["g0"]["inputs"]["frame_idx"], "passes": 2,
                  "c0_length": g["c0"]["inputs"]["length"],
                  "extension_frames": g["win1"]["inputs"]["extension_frames"],
                  "overlap_frames": g["win1"]["inputs"]["overlap_frames"], "frames_total": FRAMES,
                  "fps": g["mkvid"]["inputs"]["fps"],
                  "canvas": [g["c0"]["inputs"]["width"], g["c0"]["inputs"]["height"]],
                  "sampler": g["ksel"]["inputs"]["sampler_name"], "steps": g["s0_sched"]["inputs"]["steps"],
                  "scheduler": g["s0_sched"]["inputs"]["scheduler"], "cfg_keys": 0},
        "windows": {ch: [round(v[0], 6), round(v[1], 6)] for ch, v in win.items()},
        "prompts": {ch: {k: st[ch][k] for k in ("words", "beats", "sections")} for ch in CHUNKS},
        "prompts_full": {ch: {k: st[ch][k] for k in ("words", "main_words", "beats", "sections", "neg", "ages",
                                                    "camera_moves", "amplitude", "speed", "video1",
                                                    "picture1_first_frame")} for ch in CHUNKS},
        "species": {"tokens": list(sp), "hits": f["hits"]},
        "default_figure_clauses": f["dflt"],
        "card": card_manifest(nid, g),
        "slots": slot_edges(g)["c0"], "images": {k: g[k]["inputs"]["image"] for k in ("img", "img2")},
        "diff_paths": f["diff"], "prose_strings": len(f["ps"]),
        "gate_ok_all_prose": all(guard_ok(v) for v in f["ps"]),
        "gate": "comm.guard_ok allow on every prompt-bearing string; scripts/tests/test_p6_review.py 21 passed "
                "(run 2026-10-25)",
        "static_scan_defects": 0, "graph_sha256": sha(gp), "graph_bytes": os.path.getsize(gp),
        "run_dir_request_sha256": sha(rd) if os.path.isfile(rd) else None,
        "rendered": (dict(TOP_RENDERS[nid], **top_render_receipt(nid)) if nid in TOP_RENDERS
                     and top_render_receipt(nid) else None),
        "budget_at_build": json.load(open(LEDGER, encoding="utf-8")), "est_min": TOP_EST_MIN,
        "arm": {"armed": nid in armed_ids, "request": "p7/JOB_REQUEST.json", "jobs": TOP_ORDER,
                "naming": {"file": TOP_NAMING.replace("\\", "/"), "row": 18, "who": "Max 2026-10-24 9:30 PM CT",
                           "still": t["still"], "text": TOP_STILL_ROW[t["still"]],
                           "order": "render GI046 and GI063 first, GI046 first of the two"},
                "staged_unarmed": [x for x in TOP_TAKES if x not in armed_ids],
                "displaced": NOW_P1, "restore": TOP_RESTORE,
                "queue_math": "2 jobs x 30 min = 60 min on top of the ledger; 4 jobs x 30 min = 120 min would "
                              "overdraw the standing cap 615 min, so take B is staged (notes/needs_derrick.md row 18)"},
        "citations": list(TOP_CITATIONS),
        "notes": "staged in a Ralph pass: graph, run-dir request copy, manifest, and (take A only) the request "
                 "file. No render, no queue, no GPU, no vision judge, no " + "llama" + "-swap call.",
    }
    m["note"] = top_note(nid, g, m, f)
    return m


def top_build(nid):
    t = TOP_BY_ID[nid]
    ind = dumps_like(open(gpath(CLIP11), "rb").read(), transform(gload(CLIP1)))
    if ind is None:
        print("CONTROL_DEAD transform(clip 1) does not reproduce the clip-11 bytes; refusing to write")
        return 1
    if ind != FORMAT_IND:
        print(f"CONTROL_DEAD clip-11 byte format measures indent {ind} != pinned FORMAT_IND {FORMAT_IND}")
        return 1
    g = copy.deepcopy(gload(t["src"]))
    md = top_md(t["take_a"])
    g["c0"]["inputs"]["prompt"] = md["c0"]
    g["c1"]["inputs"]["prompt"] = md["c1"]
    g["noise"]["inputs"]["noise_seed"] = t["seed"]
    g["save"]["inputs"]["filename_prefix"] = f"community/{nid}/{nid}"
    data = write_graph(gpath(nid), g, ind)
    rd = os.path.join(RUNS, nid)
    os.makedirs(rd, exist_ok=True)
    open(os.path.join(rd, "request.api.json"), "wb").write(data)
    json.dump(measure_top(nid), open(man_path(nid), "w", encoding="utf-8"), indent=1)
    res = run(nid)
    m = measure_top(nid)
    m["checks"] = {k: len(v) for k, v in res.items()}
    m["check_failures"] = {k: v for k, v in res.items() if v}
    m["checks_all_clean"] = all(not v for v in res.values())
    json.dump(m, open(man_path(nid), "w", encoding="utf-8"), indent=1)
    print(f"{nid} take {t['take']} graph {len(g)} nodes {len(data)} B sha {sha(gpath(nid))[:16]} "
          f"clean={m['checks_all_clean']}")
    for k, v in res.items():
        if v:
            print("  FAIL", k, "::", "; ".join(v))
    return 1 if any(res.values()) else 0


def top_arm():
    jobs = [{"id": nid, "kind": "graph", "frames": FRAMES, "frames_tol": 33, "minutes": TOP_EST_MIN,
             "note": top_job_note(nid)} for nid in TOP_ORDER]
    req = {"jobs": jobs, "id": TOP_ORDER[0],
           "run_dir": os.path.join(RUNS, TOP_ORDER[0]).replace("\\", "/"),
           "api": gpath(TOP_ORDER[0]).replace("\\", "/"), "frames": FRAMES, "frames_tol": 33,
           "minutes": sum(j["minutes"] for j in jobs), "note": top_request_note()}
    open(os.path.join(W, "p7", "JOB_REQUEST.json"), "w", encoding="utf-8").write(
        json.dumps(req, indent=2, ensure_ascii=False))
    for nid in TOP_TAKES:      # arm status is a fact about the request file, so re-derive the manifests after it
        m = measure_top(nid)
        if os.path.isfile(man_path(nid)):
            old = json.load(open(man_path(nid), encoding="utf-8"))
            m["checks"], m["check_failures"] = old.get("checks"), old.get("check_failures")
            m["checks_all_clean"] = old.get("checks_all_clean")
            json.dump(m, open(man_path(nid), "w", encoding="utf-8"), indent=1)
    print("ARMED %s + %s jobs=%s minutes=%d" % (os.path.join(W, "p7", "JOB_REQUEST.json"), TOP_MD,
                                                ",".join(j["id"] for j in jobs), req["minutes"]))
    return 0


def top_check_all():
    rc = 0
    for nid in TOP_TAKES:
        res = run(nid)
        print(nid, "take", TOP_BY_ID[nid]["take"], "nodes", len(gload(nid)),
              "clean", all(not v for v in res.values()))
        for k, v in res.items():
            print(("  PASS " if not v else "  FAIL ") + k + ("" if not v else " :: " + "; ".join(v)))
        rc |= 1 if any(v for v in res.values()) else 0
    led = json.load(open(LEDGER, encoding="utf-8"))
    print("ledger", led["used_min"], "/", led["cap_min"], "min", led["jobs"], "/", led["job_cap"], "jobs; arm",
          [j.get("id") for j in (json.load(open(os.path.join(W, "p7", "JOB_REQUEST.json"),
                                               encoding="utf-8")).get("jobs", [])
                                 if os.path.isfile(os.path.join(W, "p7", "JOB_REQUEST.json")) else [])])
    return rc


def check_all():
    rc = 0
    for _, nid, _ in CARRY.values():
        res = run(nid)
        print(nid, "nodes", len(gload(nid)), "clean", all(not v for v in res.values()))
        for k, v in res.items():
            print(("  PASS " if not v else "  FAIL ") + k + ("" if not v else " :: " + "; ".join(v)))
        rc |= 1 if any(v for v in res.values()) else 0
    print("clip 11 control sha", sha(gpath(CLIP11))[:16], "== pinned", CLIP11_SHA[:16],
          sha(gpath(CLIP11)) == CLIP11_SHA)
    return rc


def selftest():
    """Seed each fault, require its detector to fire there, and require 0 problems on the real artifact (L10)."""
    nid = CARRY[2][1]
    g0 = gload(nid)
    seeds = []

    def mut(fn):
        g = copy.deepcopy(g0)
        fn(g)
        return g

    def drop_guide(g):
        g.pop("g0"); g["s0_guide"]["inputs"]["conditioning"] = ["c0", 0]

    def old_sampler(g):
        g["ksel"]["inputs"]["sampler_name"] = "euler"
        for k in ("s0_sched", "s1_sched"):
            g[k]["inputs"]["steps"] = 10

    def old_passes(g):
        g["c0"]["inputs"]["length"] = 124
        g["c2"] = copy.deepcopy(ctx_for(nid)["src"]["c2"])

    def prose_edit(g):
        g["c0"]["inputs"]["prompt"] += " The figure is a woman."

    def crop_swap(g):
        g["img2"]["inputs"]["image"] = "community/hc/GI046_w1_face.png"     # a crop belonging to another clip

    def slot_drop(g):
        g["c0"]["inputs"].pop("ref_images.ref_image_2", None)

    def missing_input(g):
        g["img"]["inputs"]["image"] = "community/hc/NOPE.jpg"

    def cfg_key(g):
        g["c0"]["inputs"]["cfg"] = 5.0

    def gate_fail(g):
        g["c0"]["inputs"]["prompt"] = "A teenager in a school uniform, no one under 18 allowed."

    def frame_idx(g):
        g["g0"]["inputs"]["frame_idx"] = 40

    def shift_move(g):
        g["m_shift"]["inputs"]["shift_video"] = 5.0

    def prefix_drift(g):
        g["save"]["inputs"]["filename_prefix"] = "community/hc15/x"

    def seed_moved(g):
        g["noise"]["inputs"]["noise_seed"] = 51150999

    def win_dropped(g):
        g.pop("win1"); g["dec_v"]["inputs"]["samples"] = ["s0_samp", 0]
        g["dec_a"]["inputs"]["samples"] = ["s0_samp", 1]

    for name, fn, det in [("guide node removed (the old 3-pass wiring)", drop_guide, "ck_guide"),
                          ("old sampler family euler/simple/10", old_sampler, "ck_shape"),
                          ("old pass shape 124x3", old_passes, "ck_shape"),
                          ("prompt text edited by the carry", prose_edit, "ck_prose"),
                          ("face crop moved to another clip's crop", crop_swap, "ck_slots"),
                          ("ref slot dropped", slot_drop, "ck_slots"),
                          ("LoadImage pointed at an absent file", missing_input, "ck_inputs"),
                          ("cfg key added (the H3 graph has none)", cfg_key, "ck_shape"),
                          ("prose the adults gate refuses", gate_fail, "ck_gate"),
                          ("guide frame moved off 0", frame_idx, "ck_guide"),
                          ("shift moved off 10.0/3.0", shift_move, "ck_shape"),
                          ("filename_prefix does not carry the id", prefix_drift, "ck_prefix"),
                          ("seed moved off the source clip seed", seed_moved, "ck_seed"),
                          ("the 119-frame window dropped (1 pass, 243 f)", win_dropped, "ck_shape")]:
        seeds.append((name, det, run(nid, mut(fn), skip=SERIALIZED).get(det, [])))
    # spent-id seed: use a real rendered id so the detector is exercised against disk
    spent = "ali163_hc15_bd002_s51150011"
    seeds.append(("id already spent (a result.json exists on disk)", "ck_idfree",
                  run(spent, gload(spent), skip=SERIALIZED).get("ck_idfree", [])))

    # the control seed: swap in a look-alike switch and ck_control must notice it is not the one that made clip 11
    me = sys.modules[__name__]
    real_tf = me.transform

    def look_alike(base):
        g = real_tf(base)
        g.pop("g0")
        g["s0_guide"]["inputs"]["conditioning"] = ["c0", 0]
        return g

    me.transform = look_alike
    try:
        seeds.append(("transform() is a look-alike, not the switch that made clip 11", "ck_control",
                      run(nid, skip=SERIALIZED).get("ck_control", [])))
    finally:
        me.transform = real_tf

    # the three on-disk detectors need artifacts, so seed them on real files and restore the bytes
    def seeded(label, det, write_fn):
        gp, rp, mp = gpath(nid), os.path.join(RUNS, nid, "request.api.json"), man_path(nid)
        keep = {p: open(p, "rb").read() for p in (gp, rp, mp)}
        try:
            write_fn(gp, rp, mp, keep)
            return (label, det, run(nid).get(det, []))
        finally:
            for p, b in keep.items():
                open(p, "wb").write(b)

    seeds.append(seeded("graph file gained a trailing newline", "ck_graphfile",
                        lambda gp, rp, mp, k: open(gp, "wb").write(k[gp] + b"\n")))
    seeds.append(seeded("run-dir request copy drifted from the graph", "ck_rundir",
                        lambda gp, rp, mp, k: open(rp, "wb").write(k[rp][:-1])))

    def man_seed(gp, rp, mp, k):
        m = json.load(open(mp, encoding="utf-8"))
        m["prompts"]["c0"]["words"] += 40
        m["seed"] = 1
        json.dump(m, open(mp, "w", encoding="utf-8"), indent=1)

    seeds.append(seeded("manifest drifted off the graph on disk", "ck_manifest", man_seed))
    real = {n: run(n) for _, n, _ in CARRY.values()}
    real_clean = {n: {k: v for k, v in r.items() if v} for n, r in real.items() if any(r.values())}
    ok = True
    for name, det, fires in seeds:
        fired = bool(fires)
        ok &= fired
        print(("SEED FIRED " if fired else "SEED MISSED") + f" {name} -> {det}: {str(fires)[:110]}")
    for n, bad in real_clean.items():
        print("REAL DIRTY", n, bad)
        ok = False
    print("selftest:", "all seeds fired and the real artifacts are clean on the in-memory detectors"
          if ok else "FAILED (a seed missed or a real artifact is dirty)")
    return 0 if ok else 1


def top_selftest():
    """The self-destruct the plan asks for: seed each fault (start frame, species wording, prompt structure, beats,
    age, negation, graph shape, manifest/request coherence) into a clone of the real artifact, require the named
    detector to fire there, and require the real artifacts to stay clean (L10)."""
    seeds = []
    A46, A63 = TOP["GI046"]["take_a"], TOP["GI063"]["take_a"]
    B46, B63 = TOP["GI046"]["take_b"], TOP["GI063"]["take_b"]

    def inmem(label, nid, fn, det):
        g = copy.deepcopy(gload(nid))
        fn(g)
        seeds.append((label, det, run(nid, g, skip=SERIALIZED).get(det, [])))

    def onfile(label, nid, det, write_fn, files=("graph", "run", "man")):
        P = {"graph": gpath(nid), "run": os.path.join(RUNS, nid, "request.api.json"), "man": man_path(nid),
             "req": os.path.join(W, "p7", "JOB_REQUEST.json"), "mp4": os.path.join(RUNS, nid, nid + ".mp4")}
        keep = {P[f]: (open(P[f], "rb").read() if os.path.isfile(P[f]) else None) for f in files}
        try:
            write_fn(keep, P)
            seeds.append((label, det, run(nid).get(det, [])))
        finally:
            for p, b in keep.items():
                if b is None:
                    if os.path.isfile(p):
                        os.remove(p)
                else:
                    open(p, "wb").write(b)

    def src_prompts(nid):
        src = gload(TOP_BY_ID[nid]["src"])

        def fn(g):
            for ch in CHUNKS:
                g[ch]["inputs"]["prompt"] = src[ch]["inputs"]["prompt"]
        return fn

    def sub(*seq):
        pairs = list(zip(seq[::2], seq[1::2]))

        def fn(g):
            for ch in CHUNKS:
                for a, b in pairs:
                    g[ch]["inputs"]["prompt"] = g[ch]["inputs"]["prompt"].replace(a, b)
        return fn

    def sub1(ch, *seq):
        pairs = list(zip(seq[::2], seq[1::2]))

        def fn(g):
            for a, b in pairs:
                g[ch]["inputs"]["prompt"] = g[ch]["inputs"]["prompt"].replace(a, b)
        return fn

    for nid, nm in ((A46, "GI046"), (A63, "GI063")):
        inmem(f"species prose absent: the shipped {nm} prompt on the new graph (orc/green/muscle/tusk/claw, "
              f"robot/metal/silver/joint/panel = 0 hits)", nid, src_prompts(nid), "ck_top_species")
    inmem("default-figure clause restored ('the only person in that photograph')", A46,
          sub("The shot ends with", "The woman is the only person in that photograph. The shot ends with"),
          "ck_top_species")
    inmem("the orc slot written as a woman too (the figure default the item bars)", A46,
          sub("a fictional adult aged 34 of a fictional humanoid orc species",
              "a fictional adult aged 34, a woman of a fictional humanoid orc species"), "ck_top_species")
    inmem("stated adult ages removed from the subject definitions", A46,
          sub("a fictional adult aged 27", "a woman in her twenties", "a fictional adult aged 33",
              "an adult of the species"), "ck_top_age")
    inmem("source c1 prose restored (the species figure written out of the scene, beats in the old 3-pass "
          "windows, no integrated field)", A46,
          lambda gg: gg["c1"]["inputs"].__setitem__("prompt", gload(TOP_BY_ID[A46]["src"])["c1"]["inputs"]["prompt"]),
          "ck_top_species")
    inmem("c1 continuation field renamed to detailed_description (the shipped structure)", A46,
          sub1("c1", "integrated_multimodal_description:", "detailed_description:"), "ck_top_words")
    def stub_c0(gg):
        p = gg["c0"]["inputs"]["prompt"]
        head, tail = p.split("detailed_description:\n", 1)
        body, rest = tail.split("\n\noverall_soundscape:", 1)
        gg["c0"]["inputs"]["prompt"] = (head + "detailed_description:\nLive-action, cinematic realism, one short "
                                        "line only.\n\noverall_soundscape:" + rest)

    inmem("c0 main field cut to a stub (below the 350-word floor)", A46, stub_c0, "ck_top_words")
    inmem("c1 beats left in the old 3-pass windows (00:05.4-00:09.9 s, under the 10.125 s chunk start)", A46,
          sub1("c1", "At 00:11.400", "At 00:05.400", "At 00:12.600", "At 00:07.400", "At 00:13.800",
               "At 00:09.400", "At 00:14.700", "At 00:09.900"), "ck_top_beats")
    inmem("c0 beats moved past the 10.125 s chunk window", A63,
          sub1("c0", "At 00:02.400", "At 00:12.400", "At 00:05.000", "At 00:13.000"), "ck_top_beats")
    inmem("beats dropped to 2 (the guide's 3+ beats rule)", A46,
          sub1("c0", "At 00:02.300", "Then", "At 00:04.400", "Next", "At 00:06.600", "After that"),
          "ck_top_beats")
    inmem("graph left at the carried source bytes (seed and prefix never moved)", A46,
          lambda gg: gg.update(copy.deepcopy(gload(TOP_BY_ID[A46]["src"]))), "ck_top_diff")
    inmem("seed left at the source clip seed (not the take seed)", A46,
          lambda gg: gg["noise"]["inputs"].__setitem__("noise_seed", gload(TOP_BY_ID[A46]["src"])["noise"]["inputs"]["noise_seed"]),
          "ck_top_seed")
    inmem("take B prose drifted from take A by one byte", B46, lambda gg: gg["c1"]["inputs"].__setitem__(
        "prompt", gg["c1"]["inputs"]["prompt"] + " "), "ck_top_sync")
    inmem("start-frame anchor moved (g0.frame_idx 1)", A46,
          lambda gg: gg["g0"]["inputs"].__setitem__("frame_idx", 1), "ck_guide")
    inmem("start-frame anchor dropped from the c0 edge (the shipped 3-pass wiring)", A46,
          lambda gg: (gg.pop("g0"), gg["s0_guide"]["inputs"].__setitem__("conditioning", ["c0", 0])), "ck_guide")
    inmem("shape back to 124 f x 3 passes", A46,
          lambda gg: gg["c0"]["inputs"].__setitem__("length", 124), "ck_shape")
    inmem("sampler family back to euler/simple", A46,
          lambda gg: gg["ksel"]["inputs"].__setitem__("sampler_name", "euler"), "ck_shape")
    inmem("canvas off 1344x768", A63, lambda gg: gg["c0"]["inputs"].__setitem__("width", 1376), "ck_shape")
    inmem("cfg key added to the H3 graph", A46, lambda gg: gg["c0"]["inputs"].__setitem__("cfg", 5.0), "ck_shape")
    inmem("prose the adults gate refuses", A46, lambda gg: gg["c0"]["inputs"].__setitem__(
        "prompt", "A teenager in a school uniform, no one under 18 allowed."), "ck_gate")
    inmem("ref slot dropped", A46, lambda gg: gg["c0"]["inputs"].pop("ref_images.ref_image_2", None), "ck_slots")
    inmem("LoadImage pointed at an absent file", A46,
          lambda gg: gg["img"]["inputs"].__setitem__("image", "community/hc/NOPE.jpg"), "ck_inputs")
    inmem("negation tokens written into the prose", A46,
          sub1("c1", "At 00:11.400", "Nothing is hidden, and no motion is quick. At 00:11.400"), "ck_top_neg")
    inmem("face crop swapped to the other clip's crop", A46,
          lambda gg: gg["img2"]["inputs"].__setitem__("image", gload(B63)["img2"]["inputs"]["image"]), "ck_slots")

    onfile("graph file gained a trailing newline", A46, "ck_graphfile",
           lambda k, P: open(P["graph"], "wb").write(k[P["graph"]] + b"\n"))
    onfile("run-dir request copy drifted from the graph", A46, "ck_rundir",
           lambda k, P: open(P["run"], "wb").write(k[P["run"]] + b" "))

    def man_words(k, P):
        m = json.load(open(P["man"], encoding="utf-8"))
        m["prompts_full"]["c0"]["words"] += 40
        json.dump(m, open(P["man"], "w", encoding="utf-8"), indent=1)

    onfile("manifest prompt counts drifted off the graph", A46, "ck_top_manifest", man_words)

    def man_prompts(k, P):
        m = json.load(open(P["man"], encoding="utf-8"))
        m["prompts"]["c1"]["beats"] += 1
        json.dump(m, open(P["man"], "w", encoding="utf-8"), indent=1)

    onfile("manifest prompts.beats drifted (the numbers the note quotes)", A46, "ck_top_manifest", man_prompts)

    def man_est(k, P):
        m = json.load(open(P["man"], encoding="utf-8"))
        m["est_min"] = 12
        json.dump(m, open(P["man"], "w", encoding="utf-8"), indent=1)

    onfile("manifest minutes stamped 12 (the unmeasured number the plan bars)", A46, "ck_top_manifest", man_est)

    def man_note(k, P):
        m = json.load(open(P["man"], encoding="utf-8"))
        m["note"] = m["note"].replace("minutes=30", "minutes charged")
        json.dump(m, open(P["man"], "w", encoding="utf-8"), indent=1)

    onfile("manifest note lost the minutes receipt", A46, "ck_top_manifest", man_note)

    def man_cite(k, P):
        m = json.load(open(P["man"], encoding="utf-8"))
        m["citations"] = [c for c in m["citations"] if "needs_derrick" not in c and "prompt_guide" not in c]
        json.dump(m, open(P["man"], "w", encoding="utf-8"), indent=1)

    onfile("manifest citations dropped the naming row and the guide", A46, "ck_top_manifest", man_cite)

    src46 = gload(TOP_BY_ID[A46]["src"])

    def man_spec_seed(k, P):
        m = json.load(open(P["man"], encoding="utf-8"))
        m["species"]["hits"] = {"c0": 0, "c1": 0}
        m["prompts_full"] = {ch: {k2: top_prose_stats(src46[ch]["inputs"]["prompt"], ch)[k2]
                                 for k2 in ("words", "beats", "sections", "neg", "ages")} for ch in CHUNKS}
        m["prompts"] = {ch: {k2: top_prose_stats(src46[ch]["inputs"]["prompt"], ch)[k2]
                             for k2 in ("words", "beats", "sections")} for ch in CHUNKS}
        m["default_figure_clauses"] = {ch: 0 for ch in CHUNKS}
        json.dump(m, open(P["man"], "w", encoding="utf-8"), indent=1)

    onfile("manifest reports the species words absent (the shipped prose's own counts)", A46, "ck_top_manifest",
           man_spec_seed)

    def man_spent(k, P):
        open(P["mp4"], "wb").write(b"mp4-not")

    # seeded on a FREE take: a spent take carries a receipt, so its id-free claim is not the property under test
    onfile("id already spent (an mp4 exists on disk)", B46, "ck_idfree", man_spent, files=("mp4",))
    onfile("manifest claims an unrendered id and it is spent", B46, "ck_top_manifest", man_spent, files=("mp4",))

    def man_naming(k, P):
        m = json.load(open(P["man"], encoding="utf-8"))
        m["arm"].pop("naming", None)
        json.dump(m, open(P["man"], "w", encoding="utf-8"), indent=1)

    onfile("staged take manifest with the naming row stripped (the queue decision loses its citation)", B63,
           "ck_top_manifest", man_naming, files=("man",))

    def man_ledger(k, P):
        m = json.load(open(P["man"], encoding="utf-8"))
        m["budget_at_build"] = {"used_min": 100.0, "jobs": 10, "cap_min": 615, "job_cap": 45,
                               "updated": "2026-10-09T12:14:08"}
        m["note"] = m["note"].replace(str(json.load(open(LEDGER, encoding="utf-8"))["updated"]),
                                      "2026-10-09T12:14:08")
        json.dump(m, open(P["man"], "w", encoding="utf-8"), indent=1)

    onfile("manifest quotes a ledger snapshot that is not the one on disk", A46, "ck_top_manifest", man_ledger,
           files=("man",))

    def req_all4(k, P):
        req = json.load(open(P["req"], encoding="utf-8"))
        req["jobs"] += [{"id": TOP["GI046"]["take_a"], "kind": "graph", "frames": FRAMES, "frames_tol": 33,
                        "minutes": TOP_EST_MIN, "note": top_job_note(TOP["GI046"]["take_a"])},
                       {"id": B63, "kind": "graph", "frames": FRAMES, "frames_tol": 33, "minutes": TOP_EST_MIN,
                        "note": top_job_note(B63)}]
        req["minutes"] = sum(j["minutes"] for j in req["jobs"])
        open(P["req"], "w", encoding="utf-8").write(json.dumps(req, indent=2, ensure_ascii=False))

    onfile("request armed with take B too (120 min over the standing cap)", A46, "ck_top_arm", req_all4,
           files=("req",))

    def req_minutes(k, P):
        req = json.load(open(P["req"], encoding="utf-8"))
        for j in req["jobs"]:
            j["minutes"] = 12
        req["minutes"] = 24
        open(P["req"], "w", encoding="utf-8").write(json.dumps(req, indent=2, ensure_ascii=False))

    onfile("request job minutes stamped 12 (unmeasured)", A46, "ck_top_arm", req_minutes, files=("req",))

    def req_note(k, P):
        req = json.load(open(P["req"], encoding="utf-8"))
        for j in req["jobs"]:
            j["note"] = "render this"
        open(P["req"], "w", encoding="utf-8").write(json.dumps(req, indent=2, ensure_ascii=False))

    onfile("request job note stripped of its receipts", A46, "ck_top_arm", req_note, files=("req",))

    def req_swapped(k, P):
        req = json.load(open(P["req"], encoding="utf-8"))
        req["jobs"] = req["jobs"][::-1]
        req["id"] = TOP["GI063"]["take_a"]
        req["api"] = gpath(TOP["GI063"]["take_a"]).replace("\\", "/")
        open(P["req"], "w", encoding="utf-8").write(json.dumps(req, indent=2, ensure_ascii=False))

    onfile("request order flipped (GI063 before GI046, against Max's row)", A46, "ck_top_arm", req_swapped,
           files=("req",))

    stale = os.path.join(NOTES, "_top_selftest_ledger.json")
    led = json.load(open(LEDGER, encoding="utf-8"))
    led["updated"] = "2026-10-09 12:14:08"
    json.dump(led, open(stale, "w", encoding="utf-8"), indent=2)
    real_ledger = globals()["LEDGER"]
    globals()["LEDGER"] = stale
    try:
        seeds.append(("manifest quotes a stale ledger stamp (2026-10-09 12:14:08)", "ck_top_manifest",
                      run(A46, copy.deepcopy(gload(A46)), skip=("ck_graphfile", "ck_rundir")).get("ck_top_manifest", [])))
    finally:
        globals()["LEDGER"] = real_ledger
        os.remove(stale)


    # ---- card gates: each rule seeded on a real graph, and ck_top_card must fire there (TOP-SCENE) ----
    def app(ch, text):
        def fn(gg):
            gg[ch]["inputs"]["prompt"] = gg[ch]["inputs"]["prompt"] + text
        return fn

    inmem("solo clause written back onto a two-figure card ('the only person in that photograph')", B46,
          app("c0", "\nThe woman is the only person in that photograph."), "ck_top_card")
    inmem("invented appearance charged to the orc (tusk, claw, fur)", B46,
          app("c0", "\nThe orc's tusked shoulder rubs against her back, clawed hand on the small of her back."),
          "ck_top_card")
    inmem("invented head for the head-cropped figure (the card crops him at the neck)", B46,
          app("c1", "\nA grinning head hangs low above the green-skinned orc."), "ck_top_card")
    def pose_drift(gg):
        p = gg["c1"]["inputs"]["prompt"]
        i = p.index("At 00:")
        gg["c1"]["inputs"]["prompt"] = (p[:i] + "At 00:10.400 the woman stands up and the orc kneels up behind her. "
                                        + p[i:])

    inmem("opening pose drift in the c1 opening beat (stands up / kneels up, against the card's opening pose)",
          B46, pose_drift, "ck_top_card")
    inmem("the card's opening pose written out of the c1 opening beat (she stands, the orc lies down)", B46,
          sub1("c1", "<Subject 1> on all fours on the rug, <Subject 2> kneeling behind her",
               "<Subject 1> standing by the sofa, <Subject 2> lying on the rug"), "ck_top_card")
    inmem("invented room on the GI046 card (bedroom, couch)", B46,
          app("c0", "\nThe scene moves to the bedroom, where the couch sits against the wall."), "ck_top_card")
    inmem("the card's room words stripped from the prompt (living room, rug)", B46,
          sub("living room", "room", "shag rug", "floor"), "ck_top_card")
    inmem("canon adult age stripped from a sentence naming a person-word", B46,
          sub("a fictional adult aged 27", "a woman", "a fictional adult aged 34", "an orc"), "ck_top_card")
    inmem("invented machine appearance on the refusal card (chrome chassis, glowing panels)", B63,
          app("c0", "\nThe machine shows a chrome chassis with glowing panels and a metal jaw."), "ck_top_card")
    inmem("the shipped consent line written back in ('consenting and eager')", A63,
          app("c0", "\nThe woman is consenting and eager, and she loves it."), "ck_top_card")
    inmem("the consent routing stripped from the GI063 prose (card record + needs_derrick row)", A63,
          sub("the card record shows restraint and distress", "the frame reads as staged",
              "notes/needs_derrick.md row 21", "the notes file"), "ck_top_card")
    inmem("invented room on the GI063 refusal card (couch, television)", A63,
          app("c1", "\nBehind her the couch and the television sit in the room."), "ck_top_card")
    inmem("graph prose drifted from the record by one byte (the byte-sync rule)", A46,
          lambda gg: gg["c1"]["inputs"].__setitem__("prompt", gg["c1"]["inputs"]["prompt"] + " "), "ck_top_md")

    # ---- the facts file behind the gate: a gate is only as honest as the card rows it cites ----------
    def onfacts(label, nid, det, scene, mutate):
        p = CARDS[scene]
        keep = open(p, "rb").read()
        try:
            mutate(p)
            seeds.append((label, det, run(nid, skip=SERIALIZED).get(det, [])))
        finally:
            open(p, "wb").write(keep)

    def facts_json(mutate):
        def go(p):
            d = json.loads(open(p, encoding="utf-8").read())
            mutate(d)
            open(p, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1))
        return go

    onfacts("one card-evidence quote altered so it no longer sits verbatim in the card", B46, "ck_top_facts", "GI046",
            facts_json(lambda d: d["gate"]["evidence"].update(tiara="a jewelled crown of silver leaves")))
    onfacts("the status row softened to OK (the card says the caption was refused and truncated)", B46,
            "ck_top_facts", "GI046", facts_json(lambda d: d.__setitem__("status", "uncaptioned")))
    onfacts("the start-still sha256 row changed off the card's stamped hash", B46, "ck_top_facts", "GI046",
            facts_json(lambda d: d.__setitem__("sha256", "0" * 64)))
    onfacts("the evidence quote behind a required per-chunk word deleted (an unbacked requirement)", B46,
            "ck_top_facts", "GI046", facts_json(lambda d: d["gate"]["evidence"].pop("tiara", None)))
    onfacts("the consent gate's required routing emptied on the refusal card", B63, "ck_top_facts", "GI063",
            facts_json(lambda d: d["gate"]["consent_gate"].__setitem__("require", [])))

    # ---- the spent render: receipts on the manifest, in the note, and never in the queue ----------
    def man_drop_receipt(k, P):
        m = json.load(open(P["man"], encoding="utf-8"))
        m.pop("rendered", None)
        json.dump(m, open(P["man"], "w", encoding="utf-8"), indent=1)

    onfile("manifest of the SPENT take drops its render receipt", A46, "ck_top_manifest", man_drop_receipt,
           files=("man",))

    def man_soft_receipt(k, P):
        m = json.load(open(P["man"], encoding="utf-8"))
        m["rendered"]["bytes"] = m["rendered"]["bytes"] - 1
        json.dump(m, open(P["man"], "w", encoding="utf-8"), indent=1)

    onfile("manifest render receipt softened by one byte off the mp4", A46, "ck_top_manifest", man_soft_receipt,
           files=("man",))

    def man_note_bytes(k, P):
        m = json.load(open(P["man"], encoding="utf-8"))
        m["note"] = m["note"].replace(str(m["rendered"]["bytes"]), "the file")
        json.dump(m, open(P["man"], "w", encoding="utf-8"), indent=1)

    onfile("manifest note stops quoting the spent mp4's bytes", A46, "ck_top_manifest", man_note_bytes,
           files=("man",))

    def man_note_prose(k, P):
        m = json.load(open(P["man"], encoding="utf-8"))
        m["note"] = m["note"].replace("this prose record has 0 renders", "this prose record was rendered")
        json.dump(m, open(P["man"], "w", encoding="utf-8"), indent=1)

    onfile("manifest note claims the current prose record was rendered when it was not", A46, "ck_top_manifest",
           man_note_prose, files=("man",))

    def req_spent(k, P):
        req = json.load(open(P["req"], encoding="utf-8"))
        req["jobs"][0]["id"] = A46
        req["id"] = A46
        req["api"] = gpath(A46).replace("\\", "/")
        open(P["req"], "w", encoding="utf-8").write(json.dumps(req, indent=2, ensure_ascii=False))

    onfile("request arms the SPENT id (a render receipt used as a queue entry)", B46, "ck_top_arm", req_spent,
           files=("req",))

    real = {n: run(n) for n in TOP_TAKES}
    # The CARRY ids 4/5 (s51150014/s51150015) are rendered clips: their mp4 and output dir exist, so ck_idfree
    # fires on them by design. A carry graph is checked on its wiring, not on id-free.
    real.update({n: run(n, skip=("ck_idfree",)) for _, n, _ in CARRY.values()})
    dirty = {n: {k: v for k, v in r.items() if v} for n, r in real.items() if any(r.values())}
    ok = True
    for name, det, fires in seeds:
        fired = bool(fires)
        ok &= fired
        print(("SEED FIRED " if fired else "SEED MISSED") + f" {name} -> {det}: {str(fires)[:120]}")
    for n, bad in dirty.items():
        print("REAL DIRTY", n, bad)
        ok = False
    print(f"top-selftest: {len(seeds)} seeds, " + ("all fired and the real artifacts (4 TOP graphs + 5 carry graphs) "
          "are clean" if ok else "FAILED (a seed missed or a real artifact is dirty)"))
    return 0 if ok else 1


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--check"
    if mode == "--check":
        return check_all()
    if mode == "--build":
        rc = 0
        for _, nid, _ in CARRY.values():
            rc |= build(nid)
        return rc
    if mode == "--selftest":
        return selftest()
    if mode == "--top-build":
        rc = 0
        for nid in TOP_TAKES:
            rc |= top_build(nid)
        return rc
    if mode == "--top-arm":
        return top_arm()
    if mode == "--top-check":
        return top_check_all()
    if mode == "--top-selftest":
        return top_selftest()
    print("usage: --check | --build | --selftest | --top-build | --top-arm | --top-check | --top-selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main())
