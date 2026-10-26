#!/usr/bin/env python3
"""scene_card_gate.py - the scene-card gate that reads a card record at a path.

Why this file exists (ORC-ROBOT, Derrick 2026-10-24 8:39 PM CT, quoted verbatim in
`C:/Users/derek/5slock/ralph-community/notes/plans/receipts/ORC-ROBOT-L33.md`:2: "Ok and I want the two videos the orc and
the robot fucking video" / "Like hardcore sex"; the item's prompt rule: describe every figure "exactly as it is (the orc as
an orc, the robot as a robot, the partner as they actually appear; species, body, build)").
The shipped card gate is `hc15_anchor_carry_build.card_measure(nid, p)`: its first argument is a **scene id** and
`card_facts(nid)` resolves it through a hard-coded `CARDS` dict - measured 2026-10-26 02:0x CT,
`card_measure("ali163_top5_gi046_s51160001", prompt)` raises `KeyError: 'ali163_top5_gi046_s51160001'` at
line 312, `CARDS[nid]`, and `CARDS` holds exactly `{"GI046": "...GI046.facts.json", "GI063": "...GI063.facts.json"}`.
So a pass that has a card record at its own path cannot use it, and this pass does not edit that file: a live Ralph loop
owns the worktree (my one uncommitted change there was restored by the harness; the L8 boundary).
This file takes `--card <path>` and `--doc <prompt doc>`, and `--probe-norm` compares its own fold and figure-owner
matcher to the shipped `card_norm`/`card_owner` on two strings, so the rules stay one dialect and any drift is visible.
`hc15_anchor_carry_build` is imported softly: if that file moves (it moved mid-pass today: `card_measure` sat at line 2970
at 01:0x and at line 363 at 02:0x), this gate still runs and says why the comparison is `unavailable`.

What is measured, not assumed:
* A card can be self-contradictory. Run each of its required tokens through its own bans (`selfconflicts`), with no prompt
  involved. The card built on 2026-10-26 01:52 from this pass's caption of the GI063 start photograph
  (`notes/scenes/candidates/GI063.card_gate.json`) requires figure 2 to say "its right hand gripping her right buttock" and
  bans figure 2's word "her" - no robot prompt can satisfy both. The live card (`notes/scenes/GI063.facts.json`) has the
  same shape: it requires the light row "highlighting the woman's skin, hair, and the metallic surfaces of the robot"
  ("the robot" = figure 2's alias, "skin" = figure 2's banned word) and it requires the room row "indistinct equipment or
  furniture silhouettes" while figure 2 bans "fur". Measured, and printed by `--table`.
* The shipped gate matches banned tokens as substrings of the punctuation-folded text, so "he" is "tall", "tall" is
  "metallic", "face" is "metallic surfaces", "LED" is "model", "fur" is "furniture". This gate matches a single-word ban at
  word boundaries and charges it only in a sentence the card assigns to that figure (`card_owner`'s rule, verbatim).
  A word-boundary hit that sits inside a verbatim token the same card REQUIRES is reported in `exempted`, with the token
  quoted, and is not a finding: the card wrote both sides. Substring-only hits are reported in `substring_only` and charged
  when the card is self-consistent, because then a word-boundary reading is the honest one.

Modes:
  --selftest                                    seeded faults (banned word, required token dropped, room ban, consent
                                                claim, feeling word, age with no marker, person-word sentence with no
                                                age, head in a head-out-of-frame card, beat-0 pose, beat-0 ban word,
                                                solo phrase, a 3-figure sentence with no card figure) + the real
                                                records. Every seeded fault fires its named finding; 0 fire on a clean
                                                control; no-op seeds abort.
  --probe-norm                                  the fold/owner agreement with the shipped functions
  --table                                       every card record on disk measured against itself: 0 rows = 0
                                                self-contradictions; a row is required-token + banned-word
  --scene GI063 --card notes/scenes/GI063.facts.json --doc notes/orcrobot_prompts.md
                                                gate the doc's prompt blocks (never the doc's prose about its own
                                                gates: `notes/top5_prompts.md` says "no judge word", "the card record",
                                                "Both of them consent" in its header, and charging that prose to the
                                                scene rules is a false positive)
  --selfconflicts --card <path>                 the card's own self-contradictions, as data
No GPU, no queue, no render, no vision model, no LLM, no judge.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ali31_prompt_set_check as A31  # noqa: E402  the shipped prompt-block parser

try:  # soft: the live builder is being rewritten by another owner
    import hc15_anchor_carry_build as HC
except Exception as exc:  # pragma: no cover
    HC = None
    _HC_WHY = type(exc).__name__ + ": " + str(exc)[:100]
else:
    _HC_WHY = None

LIVE_DIR = os.path.join(HERE, "scenes")
CAND_DIR = os.path.join(LIVE_DIR, "candidates")
PUNCT = [("\u2018", "'"), ("\u2019", "'"), ("\u201c", '"'), ("\u201d", '"'),
         ("\u2013", "-"), ("\u2014", "-"), ("\u2026", "...")]


def norm(s):
    """The shipped fold, verbatim from `hc15_anchor_carry_build.card_norm` (punctuation only, no word
    changes), reimplemented here so this gate cannot break when that file moves."""
    for a, b in PUNCT:
        s = (s or "").replace(a, b)
    return re.sub(r"\s+", " ", s.lower().strip())


def owner(sent, aliases):
    """Verbatim from `hc15_anchor_carry_build.card_owner`: a sentence belongs to every figure whose
    alias occurs in it at word boundaries; a sentence carrying `he/him/his` and no other figure belongs
    to figure 2; `"<=2"` means the card cannot assign it, and is not a number."""
    own = {int(k): aliases[k] for k in aliases}
    hit = {f for f in own if any(re.search(r"(?<![a-z])" + w + r"(?![a-z])", sent) for w in own[f])}
    if not hit and any(re.search(r"(?<![a-z])" + w + r"(?![a-z])", sent) for w in ("he", "him", "his")):
        hit = {2}
    return ("<=2" if len(hit) > 2 else "+".join(str(x) for x in sorted(hit))) if hit else "any"


def probe_norm():
    """Compare this file's fold and matcher with the shipped functions on two strings. `unavailable`
    is a disclosed reading, never a pass: it names why."""
    cases = [("She is Tall, the Metal's face; the LED glows on the table.",
              {"1": ["she", "her"], "2": ["metal", "led", "face", "tall"]}),
             ("he stands there", {"1": ["she"], "2": ["metal"]})]
    mine = {"norm": [norm(t) for t, _ in cases], "owner": [owner(norm(t), a) for t, a in cases]}
    if HC is None:
        return {"status": "unavailable", "why": _HC_WHY, **mine}
    ship = {"norm": [HC.card_norm(t) for t, _ in cases],
            "owner": [HC.card_owner(norm(t), a) for t, a in cases]}
    return {"status": "compared", "norm_equal": mine["norm"] == ship["norm"],
            "owner_equal": mine["owner"] == ship["owner"], "mine": mine, "shipped": ship,
            "all_equal": mine == ship}


def load_card(path):
    """A card record at a path, keyed by its own bytes (a card is data, cited). Two shapes live on
    disk: the CARD-VL facts file, whose rules are under `gate` (`notes/scenes/GI046.facts.json`,
    `notes/scenes/GI063.facts.json`), and a bare gate file (`*.card_gate.json`)."""
    raw = open(path, encoding="utf-8").read()
    j = json.loads(raw)
    gt = j.get("gate", j)
    gt.setdefault("card_text", j.get("card", ""))
    gt["_card_path"] = path.replace(os.sep, "/")
    gt["_card_sha256"] = hashlib.sha256(raw.encode()).hexdigest()
    gt["_card_bytes"] = len(raw.encode())
    gt["_card_scene"] = j.get("scene")
    gt["_card_kind"] = j.get("card_kind")
    gt["_card_source"] = j.get("_source") or j.get("built_from")
    gt["_caption_sha"] = j.get("caption_sha256")
    return gt


def _attrib(tok, aliases):
    """A required token's figures, by the card's own alias words. The live card stores
    `per_chunk_tokens` as ONE FLAT LIST for both figures (`["anthropomorphic metallic robot",
    "bent at waist", "long, wavy blonde", "pink lace lingerie set", ...]`, measured
    2026-10-26 02:0x CT on `notes/scenes/GI063.facts.json`), so attribution is by alias, not by a
    label the card does not carry. No alias = "any" (a room/light row)."""
    n = norm(tok)
    hit = [str(f) for f in aliases if any(re.search(r"(?<![a-z])" + re.escape(norm(a)) + r"(?![a-z])", n)
                                          for a in aliases[f])]
    return hit or ["any"]


def required(gt):
    """Every verbatim token the card requires, with its figures. Three shapes are on disk: a flat
    list (the live CARD-VL facts cards), a dict keyed by figure (the older `*.card_gate.json` cards),
    and `[token, figure]` pairs (this pass's candidate card). All three are read, and the figure
    attribution of a flat list is computed from the card's own aliases."""
    f = {}
    pcts = gt.get("per_chunk_tokens", [])
    items = []
    if isinstance(pcts, dict):
        items = [(t, [str(k)]) for k, vs in pcts.items() for t in vs]
    else:
        for it in pcts:
            if isinstance(it, (list, tuple)) and len(it) == 2:
                items.append((it[0], [str(it[1])]))
            elif isinstance(it, dict):
                items.append((it.get("token"), [str(x) for x in it.get("figures", ["any"])]))
            else:
                items.append((it, _attrib(it, gt["aliases"])))
    for tok, labs in items:
        for lab in labs:
            f.setdefault(lab, []).append(tok)
    return {"figures": f, "items": [(t, labs) for t, labs in items],
            "room": list(gt.get("room_required", [])), "light": list(gt.get("light_required", [])),
            "open_beat": {k: list(v) for k, v in gt.get("open_beat", {}).items()},
            "consent": list(gt.get("consent_gate", {}).get("require", []))}


def _word(low, w):
    return re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", low)


def _inside_required(sent, word, start, end, req_words):
    """True when this word hit lies inside a verbatim token the card requires. Offsets are read in the
    SAME string that produced the hit (the sentence), because a position in a sentence and a position
    in the whole prompt are not the same number - measured 2026-10-26 02:1x CT: comparing a
    sentence offset against a whole-text offset makes the exemption never fire."""
    for tok in req_words:
        n = norm(tok)
        for m in re.finditer(re.escape(n), sent):
            if m.start() <= start and end <= m.end():
                return tok
        for w in n.split():
            if w == word:
                for m in re.finditer(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", sent):
                    if m.start() == start:
                        return tok
    return None


def sentences(text):
    return [s for s in re.split(r"(?<=[.!?])\s+", norm(text)) if s.strip()]


def scan(text, gt, req):
    """The measurement. `counted` findings stop a prompt; `exempted` (inside a required token) and
    `substring_only` (a shorter form inside a longer word) are disclosed, and `selfconflicts` is the
    card's own contradiction, measured with no prompt."""
    low = norm(text)
    sents = sentences(text)
    sc = selfconflicts(gt)
    sc_words = {(str(r["scope"]), str(r["figure"]), r["banned_word"]) for r in sc} | \
        {(str(r["figure"]), r["banned_word"]) for r in sc}
    figs = sorted({str(k) for k in gt["aliases"]} | set(req["figures"]))
    all_req = [t for toks in req["figures"].values() for t in toks] + req["room"] + req["light"] \
        + [t for toks in req["open_beat"].values() for t in toks] + req["consent"]
    counted, exempted, substring_only = [], [], []

    def charge(scope, fig, word, sent, hit, why):
        tok = _inside_required(sent, word, hit.start(), hit.end(), all_req)
        rec = (scope, str(fig), word, sent[:110], hit.start(), why)
        (exempted if tok else counted).append(rec + ((norm(tok),) if tok else ()))

    def mid_word(scope, fig, word, sent):
        """The word itself is not in the text; a longer word contains that letter run. Disclosed
        always; charged only when the card carries NO self-contradiction for that word, because then
        a word-boundary reading is the honest one and the author can avoid the collision."""
        for m in occ(word, sent)[1]:
            conflicting = (scope, str(fig), word) in sc_words or (str(fig), word) in sc_words
            if conflicting:
                substring_only.append((scope, str(fig), word, sent[max(0, m.start() - 26):m.end() + 26]))
            else:
                charge(scope, fig, word, sent, m, "inside a longer word, and the card is self-consistent "
                                                 "for this word, so a word-boundary reading is the honest one")

    for sent in sents:
        own = owner(sent, gt["aliases"])
        named = [] if own in ("any", "<=2") else [x for x in own.split("+")]
        for f in [x for x in gt["aliases"]]:
            for w in gt["banned"].get(f, []):
                w = norm(w)
                if not w:
                    continue
                if " " in w:
                    if w in sent:
                        charge("figure", f, w, sent, re.search(re.escape(w), sent), "phrase, substring")
                    continue
                wb, _mid = occ(w, sent)
                for m in wb:
                    if str(f) in named:
                        charge("figure", f, w, sent, m, "word-boundary, and this sentence is the card's for figure %s" % f)
                mid_word("figure", f, w, sent)
        for w in gt["banned"].get("any", []) + gt.get("room_banned", []) + gt.get("light_bans", []) \
                + gt.get("consent_gate", {}).get("ban", []):
            w = norm(w)
            if not w:
                continue
            if " " in w:
                if w in sent:
                    charge("any", "any", w, sent, re.search(re.escape(w), sent), "phrase, substring")
                continue
            wb, _mid = occ(w, sent)
            for m in wb:
                charge("any", "any", w, sent, m, "word-boundary, a card-wide ban")
            mid_word("any", "any", w, sent)
    # coverage: the tokens the card requires, and the figures they belong to
    have, miss = {}, []
    for lab, toks in req["figures"].items():
        have[lab] = [t for t in toks if norm(t) in low]
    miss = sorted({t for t, _labs in req["items"] if norm(t) not in low})
    room_missing = [t for t in req["room"] if norm(t) not in low]
    light_missing = [t for t in req["light"] if norm(t) not in low]
    beat = norm(beat0(text))
    beat_missing = {k: [t for t in v if norm(t) not in beat] for k, v in req["open_beat"].items()}
    beat_banned = {k: [b for b in gt.get("open_beat_ban", {}).get(k, []) if norm(b) in beat]
                   for k in req["open_beat"]}
    # heads: the card says which figures' heads are in frame; a head word for a cropped head is a finding
    head_hits = {}
    for lab in [x for x in gt["aliases"]]:
        if gt.get("head_in_frame", {}).get(lab) is False:
            hits = [w for w in ("head", "face", "gaze", "eyes", "skull")
                    if _word(low, w) and not any(norm(a) in low for a in gt.get("head_allow", []))]
            if hits:
                head_hits[lab] = hits
    # ages: a sentence that states an age must carry the card's marker; a sentence that uses a
    # person-word must state an age (the shipped rule, `age_no_marker` / `age_missing`)
    age_no_marker = [s for s in sents if re.search(r"\baged?\s+\d{2}\b", s) and norm(gt["age_marker"]) not in s]
    age_missing = []
    for s in sents:
        who = sorted({w for w in gt.get("age_required", []) if _word(s, w)})
        if who and not re.search(r"\b\d{2}\b", s):
            age_missing.append({"words": who, "sent": s[:110]})
    consent_missing = [c for c in req["consent"] if norm(c) not in low]
    solo = [p for p in gt.get("solo_phrases", []) if norm(p) in low]
    # how many of the card's figures the text carries, by the card's own alias words, word-boundary,
    # over the WHOLE text (measured 2026-10-26 02:2x CT: reading this from a leftover loop variable
    # scored only the last sentence, so a two-figure prompt read as one figure and F-SUBJECTS fired)
    nfig = len({f for f in gt["aliases"] if any(_word(low, norm(a)) for a in gt["aliases"][f])})
    return {"card_path": gt["_card_path"], "card_sha256": gt["_card_sha256"], "card_scene": gt["_card_scene"],
            "age_marker": gt.get("age_marker"),
            "counted": counted, "exempted": exempted, "substring_only": substring_only,
            "tokens_have": have, "tokens_missing": miss, "room_missing": room_missing,
            "light_missing": light_missing, "beat_missing": beat_missing, "beat_banned": beat_banned,
            "head_hits": head_hits, "age_no_marker": age_no_marker, "age_missing": age_missing,
            "consent_missing": consent_missing, "solo_hits": solo, "figures_present": nfig,
            "figure_count": gt.get("figure_count"), "selfconflicts": selfconflicts(gt)}


def _re_iter(w, sent):
    return list(re.finditer(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", sent))


def occ(word, text):
    """Every occurrence of a ban token, split the only two ways it can occur: at word boundaries, or
    inside a longer word. The shipped gate cannot tell them apart (`token in normalized`), and that is
    why it charges "fur" to "furniture", "face" to "metallic surfaces", "LED" to "model" and "he" to
    "the". The split is mechanical: a letter on either side means the word itself is not there."""
    wb, mid = [], []
    for m in re.finditer(re.escape(word), text):
        adj = text[max(0, m.start() - 1):m.start()] + text[m.end():m.end() + 1]
        (mid if re.search(r"[a-z]", adj) else wb).append(m)
    return wb, mid


def beat0(text):
    """The opening beat: the first `At 00:00.000` paragraph, which is what the card's open_beat rules
    speak about (the shipped `card_beat0`)."""
    m = re.search(r"At 00:00\.000[^\n]*", text)
    return m.group(0) if m else ""


def selfconflicts(gt):
    """The card measured against itself: each of its own required tokens run through its own bans.
    No prompt: this is a property of the card, and it is what a required-token exemption is based on."""
    out = []
    req = required(gt)
    scopes = [("figure", lab, gt["banned"].get(lab, []), toks)
              for lab, toks in req["figures"].items() if lab != "any"]
    scopes += [("room", "room", gt.get("room_banned", []), req["room"]),
               ("light", "light", gt.get("light_bans", []), req["light"]),
               ("any", "any", gt["banned"].get("any", []) + [c for c in gt.get("consent_gate", {}).get("ban", [])],
                sorted({t for t, _labs in req["items"]}) + req["room"] + req["light"] + req["consent"])]
    # every required row against every figure's own bans: a room/light row that carries a figure's
    # alias also carries that figure's bans into the sentence, and the shipped gate charges it there.
    all_rows = sorted({t for t, _labs in req["items"]} | set(req["room"]) | set(req["light"]))
    scopes += [("figure-row", lab, gt["banned"].get(lab, []), all_rows) for lab in gt["aliases"]]
    for scope, fig, bans, toks in scopes:
        for t in toks:
            n = norm(t)
            for w in bans:
                w = norm(w)
                if w and (w in n if " " in w else w in n):
                    out.append({"scope": scope, "figure": str(fig), "token": t, "banned_word": w,
                                "reading": "word-boundary" if (" " in w or _word(n, w)) else "substring-only"})
    for k, toks in req["open_beat"].items():
        for t in toks:
            for b in gt.get("open_beat_ban", {}).get(k, []):
                if norm(b) and norm(b) in norm(t):
                    out.append({"scope": "beat0", "figure": str(k), "token": t, "banned_word": b,
                                "reading": "word-boundary"})
    for c in req["consent"]:
        for b in gt.get("consent_gate", {}).get("ban", []):
            if norm(b) and norm(b) in norm(c):
                out.append({"scope": "consent", "figure": "any", "token": c, "banned_word": b,
                            "reading": "word-boundary"})
    return out


def findings(m):
    """The findings that stop a prompt. `exempted` (a hit inside a token the card itself requires) and
    `substring_only` (a banned letter run that appears only inside a longer word) are REPORTED fields,
    never findings: a word that is not present as a word is not used, and a collision the card wrote
    itself is not the prompt's fault. Both are printed by every mode, so nothing is hidden."""
    out = []
    if m["figures_present"] != m["figure_count"]:
        out.append("F-SUBJECTS the text carries %s of the card's %s figures"
                   % (m["figures_present"], m["figure_count"]))
    if m["tokens_missing"]:
        out.append("F-CARD-TOKENS %d of the card's required appearance tokens are absent: %s"
                   % (len(m["tokens_missing"]), ";".join(m["tokens_missing"][:6])))
    if m["room_missing"]:
        out.append("F-ROOM %d of the card's room rows are absent: %s"
                   % (len(m["room_missing"]), ";".join(m["room_missing"][:4])))
    if m["light_missing"]:
        out.append("F-LIGHT %d of the card's light rows are absent: %s"
                   % (len(m["light_missing"]), ";".join(m["light_missing"][:4])))
    for k, v in sorted(m["beat_missing"].items()):
        if v:
            out.append("F-BEAT0 figure %s's opening pose is not in the 00:00.000 beat: %s" % (k, ";".join(v)))
    for k, v in sorted(m["beat_banned"].items()):
        if v:
            out.append("F-BEAT0-BAN figure %s's opening beat uses the card's banned words: %s" % (k, ";".join(v)))
    for lab, ws in sorted(m["head_hits"].items()):
        out.append("F-CARD-HEAD figure %s: %s, and the card says the frame crops its head out" % (lab, ",".join(ws)))
    for scope, fig, w, sent, _pos, why, *_tail in m["counted"]:
        out.append("F-BANNED %s %s uses the banned word '%s' (%s) in the sentence %r" % (scope, fig, w, why, sent))
    if m["age_no_marker"]:
        out.append("F-AGE %d sentence(s) state an age without the card's '%s' words"
                   % (len(m["age_no_marker"]), m.get("age_marker") or "canon declaration"))
    if m["age_missing"]:
        out.append("F-AGE %d sentence(s) use a person-word (%s) and state no age"
                   % (len(m["age_missing"]), ",".join(sorted({w for a in m["age_missing"] for w in a["words"]}))))
    if m["consent_missing"]:
        out.append("F-CONSENT the card's required card-honesty lines are absent: %s"
                   % ";".join(m["consent_missing"]))
    if m["solo_hits"]:
        out.append("F-SOLO a solo phrase of a %s-figure scene: %s" % (m["figure_count"], ",".join(m["solo_hits"])))
    return out


# ------------------------------------------------------------------ seeded selftest
def clean_control():
    """A card and a prompt that satisfy it: the control that keeps every seeded fault an event.
    "tall" is banned for figure 2 on purpose: the word-boundary seed then has one variable - the word -
    and cannot pass by naming the figure through an alias the seed text forgot (measured 2026-10-26
    02:3x CT: "It is a tall machine" is the card's for NO figure, because "machine" is not one of this
    card's alias rows, so the owner rule left the sentence unowned and the ban correctly did not fire)."""
    gt = {"figure_count": 2, "age_min": 21, "age_marker": "canon declaration",
          "age_required": ["woman", "man", "female", "male"],
          "aliases": {"1": ["she", "her", "woman"], "2": ["it", "its", "metal"]},
          "banned": {"1": ["he", "tall"], "2": ["fur", "tall"], "any": ["beautiful"]},
          "per_chunk_tokens": [("her long blonde hair", "1"), ("polished silver metal plating", "2")],
          "room_required": ["dark interior"], "room_banned": ["bed", "lamp"],
          "light_required": ["cool blue glow"], "light_bans": ["warm"],
          "head_in_frame": {"1": True, "2": True}, "head_allow": [],
          "open_beat": {"1": ["lying on the bench"], "2": ["bent at the waist"]},
          "open_beat_ban": {"1": ["frees her"], "2": ["lets go"]},
          "consent_gate": {"require": ["the card record shows restraint and gives no consent evidence"],
                           "ban": ["eager", "willingly"]}, "solo_phrases": ["she is alone"],
          "_card_path": "control", "_card_sha256": "control", "_card_scene": "CONTROL"}
    prompt = (
        "<Subject 1> is the woman in the start photograph, a fictional adult aged 27 (canon declaration): "
        "her long blonde hair, her hands at her sides.\n"
        "<Subject 2> is the machine in the same photograph, a fictional adult of a fictional non-human build "
        "aged 34 (canon declaration): polished silver metal plating, articulated limbs.\n"
        "The room is a dark interior with a black padded bench, lit by strong directional light from front-left "
        "and a cool blue glow from the right.\n"
        "At 00:00.000, the frame is the opening photograph: the woman is lying on the bench, her wrists at the "
        "bench edge; the machine is bent at the waist behind her, its hand on her hip, and it keeps that grip.\n"
        "The card record shows restraint and gives no consent evidence, and the clip claims nothing else; the "
        "question is notes/needs_derrick.md row 21.\n")
    return gt, prompt


def selftest_cases():
    gt, clean = clean_control()
    cases = []

    def add(name, text, want, scope=None):
        cases.append((name, text, want, scope))

    add("clean_control", clean, [])
    add("figure_ban_word_boundary", clean + " The metal is tall, and the plating is bright.", "F-BANNED", "2")
    add("mid_word_ban_charged_when_card_is_consistent", clean + " The room has furniture and a metal surface.",
        "F-BANNED")
    add("card_token_dropped", clean.replace("polished silver metal plating", "bright plating"), "F-CARD-TOKENS")
    add("room_ban_word", clean.replace("dark interior", "bright bedroom"), "F-BANNED")
    add("light_ban_word", clean.replace("cool blue glow", "warm light"), "F-BANNED")
    add("consent_claim_banned", clean + " She does it willingly.", "F-BANNED")
    add("consent_required_missing", clean.replace("The card record shows restraint and gives no consent evidence, "
                                                  "and the clip claims nothing else; the question is "
                                                  "notes/needs_derrick.md row 21.", "The clip shows a scene."),
        "F-CONSENT")
    add("age_marker_missing", clean.replace("aged 27 (canon declaration)", "aged 27"), "F-AGE")
    add("age_missing_on_person_word", clean.replace("the woman in the start photograph, a fictional adult aged 27 "
                                                   "(canon declaration)", "the woman in the start photograph"),
        "F-AGE")
    add("solo_phrase", clean + " She is alone in the frame.", "F-SOLO")
    add("beat0_pose_missing", clean.replace("the woman is lying on the bench", "the woman kneels by the bench"),
        "F-BEAT0")
    add("beat0_banned_word", clean.replace("it keeps that grip", "then it lets go"), "F-BEAT0-BAN")
    add("figures_one_of_two", clean.replace("<Subject 2> is the machine in the same photograph, a fictional adult "
                                           "of a fictional non-human build aged 34 (canon declaration): polished "
                                           "silver metal plating, articulated limbs.", "It is one person, alone."),
        "F-CARD-TOKENS")
    # a head-out-of-frame card: the same text must fire F-CARD-HEAD on that figure only
    gt2 = json.loads(json.dumps(gt))
    gt2["head_in_frame"] = {"1": True, "2": False}
    cases.append(("head_out_of_frame_card", (clean + " The machine's head is out of frame."), "F-CARD-HEAD", gt2))
    # a card that bans figure 2's "her" and REQUIRES "its right hand gripping her right buttock": the
    # hit inside the required token is exempted with the token quoted; the same word outside it is a
    # finding. The text carries every required row of this card verbatim, so the only variable is where
    # the word sits.
    gt3 = json.loads(json.dumps(gt))
    gt3["per_chunk_tokens"] = gt3["per_chunk_tokens"] + [("its right hand gripping her right buttock", "2")]
    gt3["banned"]["2"] = gt3["banned"]["2"] + ["her"]
    clean3 = clean + (" At 00:00.000, the machine keeps its place: its right hand gripping her right buttock, "
                      "bent at the waist, and it holds that grip to the last frame.\n")
    cases.append(("exempted_inside_required_token", clean3, [], gt3))
    cases.append(("banned_outside_required_token", clean3 + " At 00:01.400, its metal hand presses and "
                  "it lifts clear, and her head turns aside.", "F-BANNED", gt3))
    # the live GI063 card's exact shape: it requires a room row containing "furniture" and bans "fur".
    # The same mid-word run that is charged on a self-consistent card is only disclosed here, and the
    # text carries the card's room rows verbatim so the room check is not the variable.
    gt4 = json.loads(json.dumps(gt))
    gt4["room_required"] = gt4["room_required"] + ["indistinct equipment or furniture silhouettes"]
    clean4 = clean + (" The room shows indistinct equipment or furniture silhouettes along the back wall, "
                      "and a metal surface beside the bench.\n")
    cases.append(("mid_word_disclosed_when_card_self_contradicts", clean4, [], gt4))
    # the real records: the live card and this pass's caption-built card, measured against themselves
    for path in (os.path.join(LIVE_DIR, "GI063.facts.json"), os.path.join(CAND_DIR, "GI063.card_gate.json")):
        cases.append(("real_card_" + os.path.basename(os.path.dirname(path)) + "_" + os.path.basename(path),
                      None, "selfconflicts", path))
    return gt, clean, cases


def exemption_probe():
    """The two behaviours this gate adds over the shipped substring rule, run on constructed cards so
    they are events, not prose:
    (a) a word-boundary hit INSIDE a verbatim token the same card requires is exempted with the token
        quoted and is not a finding - the card wrote both sides;
    (b) a mid-word hit (the shipped gate's "fur" in "furniture") is CHARGED on a self-consistent card
        and only DISCLOSED on a card that contradicts itself on that word - the live GI063 card's exact
        shape: it requires "indistinct equipment or furniture silhouettes" and bans "fur".
    A control card with no self-contradiction, on clean text, must read 0 findings."""
    gt, clean = clean_control()
    g3 = json.loads(json.dumps(gt))
    g3["per_chunk_tokens"] = g3["per_chunk_tokens"] + [("its right hand gripping her right buttock", "2")]
    g3["banned"]["2"] = g3["banned"]["2"] + ["her"]
    m3 = scan(clean + " At 00:01.400, its right hand gripping her right buttock presses and holds.",
              g3, required(g3))
    g4 = json.loads(json.dumps(gt))
    g4["room_required"] = g4["room_required"] + ["indistinct equipment or furniture silhouettes"]
    # the text carries the card's own room row verbatim, so only the mid-word collision is under test
    text = clean + (" The room shows indistinct equipment or furniture silhouettes along the back wall, "
                    "and a metal surface beside the bench.")
    m4 = scan(text, g4, required(g4))
    m5 = scan(text, gt, required(gt))
    m0 = scan(clean, gt, required(gt))
    assert any(x[1] == "2" and x[2] == "her" for x in m3["exempted"]), \
        "the required-token exemption never fires on the card's own collision: %s" % (m3["counted"][:2],)
    assert not any(x.startswith("F-BANNED") for x in findings(m3)), "an exempted hit is still a finding"
    assert m4["substring_only"], "the mid-word disclosure is dead"
    assert not findings(m4), "a disclosed mid-word hit is charged on a self-contradictory card: %s" % findings(m4)[:1]
    assert any(x[2] == "fur" for x in m5["counted"]), "a mid-word hit is not charged on a self-consistent card"
    assert findings(m0) == [], "the control is not clean: %s" % findings(m0)[:1]
    return {"exempted_rows": len(m3["exempted"]), "exempted_findings": len(findings(m3)),
            "self_contradictory_card_disclosed": len(m4["substring_only"]),
            "self_contradictory_findings": len(findings(m4)),
            "consistent_card_charged": len([x for x in m5["counted"] if x[2] == "fur"]),
            "control_findings": len(findings(m0))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--table", action="store_true")
    ap.add_argument("--probe-norm", action="store_true")
    ap.add_argument("--selfconflicts", action="store_true")
    ap.add_argument("--scene")
    ap.add_argument("--card")
    ap.add_argument("--doc")
    a = ap.parse_args()
    if a.probe_norm:
        print(json.dumps(probe_norm(), indent=2)[:1400])
        return 0
    if a.selfconflicts:
        gt = load_card(a.card)
        rows = selfconflicts(gt)
        print(json.dumps({"card": gt["_card_path"], "sha256": gt["_card_sha256"], "scene": gt["_card_scene"],
                          "kind": gt["_card_kind"], "source": gt["_card_source"], "conflicts": len(rows),
                          "rows": rows}, indent=2))
        return 0
    if a.table:
        total = 0
        for p in sorted(glob.glob(os.path.join(LIVE_DIR, "*.facts.json"))
                        + glob.glob(os.path.join(LIVE_DIR, "*.card_gate.json"))
                        + glob.glob(os.path.join(CAND_DIR, "*.json"))):
            gt = load_card(p)
            rows = selfconflicts(gt)
            total += len(rows)
            print("card %s scene=%s kind=%s sha=%s bytes=%d self-contradictions=%d"
                  % (gt["_card_path"], gt["_card_scene"], gt["_card_kind"], gt["_card_sha256"][:16],
                     gt["_card_bytes"], len(rows)))
            for r in rows:
                print("   %s %s: token %r contains the card's own banned %r (%s)"
                      % (r["scope"], r["figure"], r["token"], r["banned_word"], r["reading"]))
        print("VERDICT TABLE, %d self-contradiction rows across the cards above" % total)
        return 0
    if not a.selftest:
        gt = load_card(a.card)
        rows = selfconflicts(gt)
        print(json.dumps({"card": gt["_card_path"], "sha256": gt["_card_sha256"], "scene": gt["_card_scene"],
                          "kind": gt["_card_kind"], "source": gt["_card_source"], "caption_sha": gt["_caption_sha"],
                          "self_conflicts": len(rows)}, indent=2))
        bad = 0
        for name, text in A31_blocks(a.doc):
            m = scan(text, gt, required(gt))
            f = findings(m)
            bad += len(f)
            print(json.dumps({"card": gt["_card_sha256"][:16], "target": name,
                              "counted": [list(x[:4]) for x in m["counted"]],
                              "exempted": [list(x[:4]) + [x[6]] for x in m["exempted"]],
                              "substring_only": [list(x[:3]) for x in m["substring_only"]],
                              "self_conflicts": m["selfconflicts"],
                              "coverage": {"tokens_have": {k: len(v) for k, v in m["tokens_have"].items()},
                                           "tokens_total": {k: len(v) for k, v in required(gt)["figures"].items()},
                                           "room_missing": m["room_missing"], "light_missing": m["light_missing"]},
                              "age": {"stated_with_marker": not m["age_no_marker"], "missing": m["age_missing"]},
                              "consent": {"required_present": not m["consent_missing"]},
                              "findings": f}, indent=2))
        print("VERDICT " + ("SCENE CARD GATE CLEAN, 0 findings, card %s %s" % (gt["_card_scene"], gt["_card_sha256"][:16])
                            if not bad else "NOT CLEAN %d findings, card %s %s" % (bad, gt["_card_scene"],
                                                                                  gt["_card_sha256"][:16])))
        return 0 if not bad else 1
    gt, clean, cases = selftest_cases()
    fired, silent = [], []
    for name, text, want, extra in cases:
        if want == "selfconflicts":
            g2 = load_card(extra)
            rows = selfconflicts(g2)
            print("  %-40s card %s self-contradictions=%d" % (name, g2["_card_sha256"][:12], len(rows)))
            continue
        g2 = extra if isinstance(extra, dict) and "aliases" in extra else gt
        if not text.strip():
            continue
        m = scan(text, g2, required(g2))
        f = findings(m)
        if want == []:
            if f:
                silent.append(name + " " + f[0][:90])
            continue
        if not any(x.startswith(want) for x in f):
            fired.append(name + " wants " + want + " got " + (f[0][:90] if f else "nothing"))
        else:
            print("  %-40s fires %s" % (name, want))
    # the required-token exemption and the mid-word disclosure must be fields, never findings
    ex = exemption_probe()
    print("  exemption/mid-word probe: %s" % json.dumps(ex))
    print("selftest: %d cases, %d silent (%s), %d fired (%s), exemption+disclosure probes live"
          % (len(cases), len(silent), ";".join(silent) or "none", len(fired), ";".join(fired) or "none"))
    print("VERDICT " + ("SCENE CARD GATE SELFTEST OK" if not silent and not fired else
                        "SELFTEST BROKEN silent=" + str(silent) + " fired=" + str(fired)))
    return 0 if not silent and not fired else 1


def A31_blocks(path):
    return [(b["id"] + "/" + b["chunk"], b["text"]) for b in A31.parse_blocks(open(path, encoding="utf-8").read())]


if __name__ == "__main__":
    sys.exit(main())
