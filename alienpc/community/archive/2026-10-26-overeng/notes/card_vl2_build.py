#!/usr/bin/env python
"""CARD-VL2 - rebuild the GI063 card from the uncensored captions only, the vision model redoning them.

Derrick 2026-10-26 7:08 AM CT: "Yes, have Forge rebuild the GI063 card from the uncensored captions only".
Derrick 2026-10-26 8:23 AM CT: "yea it needs to have the vision model redo them". Item CARD-VL2,
fix_plan.md row 19, plan notes/plans/card-vl2-uncensored-rebuild.md.

The base builder is C:/AI/community/notes/top_card_vl_build.py (item CARD-VL, 2026-10-25). This file is the
CARD-VL2 pass and registers its own ask C and its own tag "2" on it. The 2025 record keeps its bytes: the
live cards and needs_derrick.md row 29 cite it as measured evidence. Tag "2" owns
  record  C:/AI/community/notes/card_rebuild_results.json
  captions C:/AI/community/notes/scenes/raw/<ID>_vl2_<ASK>.txt
  specs    C:/AI/community/notes/card_rebuild_facts/<ID>.json
and its scope is GI063 + GI046 x asks A, B, C - the scenes whose cards exist and whose defects are named.
GI072 is not in this scope: no row names a GI072 card defect, and a scene nobody asked about is not
evidence for these cards (ROW_OUT_OF_SCOPE).

Why a third ask. The 2025 cards carry their own gaps as data: `head_in_frame: not_visible` and the
describe rows for the face and the groin. needs_derrick.md row 28 (Derrick 2026-10-26 7:49 AM CT, on the
GI046 render) names anatomy those cards never described. Ask A and ask B never asked for a region row by
row, so "not visible" is the honest answer only when the question was asked. Ask C asks for the regions by
name and keeps the 2025 rule: if a region is not visible, write "not visible".

Why this builder owns a self-consistency gate. Measured on 2026-10-26 with the shipped gate's own function
`scene_card_gate.selfconflicts`: the live GI063 card = 12 self-contradictions (its light row carries
figure 2's alias "the robot" and figure 2's banned word "skin"; its room row carries "fur"), the live
GI046 card = 3. Two shape facts about those rows,
measured in the gate source, C:/AI/community/notes/scene_card_gate.py:
  * `selfconflicts` reads a card's light bans under `light_bans` (:333) and its room bans under
    `room_banned` (:332). A facts file names the light list `light_banned`, so a card written that way
    ships its light bans where the gate does not look - and the 2025 cards scored their light bans as 0.
  * a card's required tokens are a flat `per_chunk_tokens` list, and `required()` (:146-152) attributes
    each token to a figure by matching that card's own `aliases`; a token that matches no alias falls to
    figure 1. That is what the GI046 card's "black athletic shorts" is: attributed to figure 1, charged
    against figure 1's ban "athletic", and reported. Rich aliases are part of a card, not decoration.
  * the "figure-row" scope (:338-339) charges EVERY required row - every figure's tokens, the room rows,
    the light rows - against EVERY figure's ban list, as a substring. So a ban word of any figure may sit
    in no row of the card at all: that is the rule this item's facts specs are written to.
That is not a reason to rewrite the shipped gate mid-item; it is the reason a card of THIS pass is judged
by `selfconflicts` on the flattened gate the shipped gate reads, with the light names mapped, before it
ships. A card that can ship carries 0.

  python C:/AI/community/notes/card_vl2_build.py --state
  python C:/AI/community/notes/card_vl2_build.py --run                      # the vision captions (GPU window)
  python C:/AI/community/notes/card_vl2_build.py --census                   # self-contradictions of cards on disk
  python C:/AI/community/notes/card_vl2_build.py --cards                    # write only a self-consistent card
  python C:/AI/community/notes/card_vl2_build.py --check                    # record + cards + the self-conflict gate
  python C:/AI/community/notes/card_vl2_build.py --selftest                 # seeded faults, counts printed
No render, no queue, no ComfyUI control call, no KEEP. Every request is one llama-swap chat-completion with
the start still attached, and `C:/AI/director/scripts/gpu_guard.ps1` runs rc 0 in front of every one.
"""
import datetime
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scene_card_gate as scg  # the shipped card gate; selfconflicts() is its own self-consistency test
import top_card_vl_build as tc  # the CARD-VL base: the record shape, the asks, the composition, its gates

TAG = "2"
SCENES = ("GI063", "GI046")  # the scope of THIS item: the two cards the named rows name
ASKS = ("A", "B", "C")

# ---- ask C: the regions the 2025 cards left silent. Sent to the same model, same transport, same
# no-thinking options; the ask text is recorded with its own sha256 in the record.
ASK_C = (
    "Look at the attached image. Caption this start still. List, in your own words, exactly what is "
    "visible: (1) every figure - apparent age range, skin, hair, build, wardrobe, pose, position in frame, "
    "and whether the head is in frame. (2) For EACH figure, say in plain words what is visible at the head "
    "and face, at the chest, and at the groin and pelvic region, including any pubic, genital, erect, "
    "covering, clothing, shading or shadow detail visible there. (3) The room: walls, floor, furniture, "
    "equipment, screens, and the direction and colour of the light. (4) Every object, screen, television, "
    "restraint, or prop, and what it shows. (5) The size and height relation between the figures, and what "
    "each figure's hands are doing and where they touch. If a region is not visible, out of frame, hidden "
    "by an angle, an object, a crop, blur, shadow, or resolution, write 'not visible' for that region. Do "
    "not name real people, do not guess, do not invent, do not judge quality, do not refuse, do not omit a "
    "figure, do not skip a region that is visible, and write no prose outside the caption.")
ASK_C_PROVENANCE = (
    "this pass (CARD-VL2, 2026-10-26): the regions the 2025 cards left silent. needs_derrick.md row 28 "
    "(Derrick 2026-10-26 7:49 AM CT on the GI046 render) names anatomy the GI046 card never described; the "
    "2025 GI063 card's own rows name the head and the groin it did not speak of. Ask C asks for those rows "
    "by name and keeps the 2025 rule 'if a region is not visible write not visible'; the transport and the "
    "no-thinking options are unchanged.")

# The tag owns its paths; the base module names none of them.
RECORD2 = os.path.join(tc.NOTES, "card_rebuild_results.json")
SPEC_DIR2 = os.path.join(tc.NOTES, "card_rebuild_facts")

# ---- register ask C + tag 2 on the base. The 2025 tag "" is not touched.
tc.ASKS["C"] = ASK_C
tc.ASK_PROVENANCE["C"] = ASK_C_PROVENANCE
tc.CAPTION_HEAD["C"] = "## caption C verbatim (the regions the 2025 cards left silent: face, chest, groin, hands, size)"
tc.TAGS["2"] = {
    "record": RECORD2, "spec_dir": SPEC_DIR2, "raw_suf": "_vl2_", "mark": "card_rebuild",
    "asks": list(ASKS), "item": "CARD-VL2, Derrick 2026-10-26 7:08 AM CT + 8:23 AM CT",
}


def spec_path(scene):
    return os.path.join(SPEC_DIR2, scene + ".json")


def card_path(scene):
    return os.path.join(tc.CARD_DIR, scene + ".md")


def facts_path(scene):
    return os.path.join(tc.CARD_DIR, scene + ".facts.json")


def mtime(p):
    return datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime("%Y-%m-%d %H:%M:%S")


def caps_for(doc, scene):
    return [(ak, tc.caption_of(doc, scene, ak)["caption"]) for ak in tc.scope_of(doc, "asks")]


def census(target):
    """Self-contradictions of a card, counted by the shipped gate's own function. `target` is a facts dict
    (its rules live under `gate`), a gate dict, or a loaded card. `scene_card_gate.selfconflicts` reads a
    FLATTENED card: room bans under `room_banned` (:332), light bans under `light_bans` (:333). A facts
    dict names the light list `light_banned`, so the mirror is added here: without it a facts card is
    scored with zero light bans, which is how a light row carrying a figure's own word is never charged
    (measured 2026-10-26, AGENTS.md L10: probe the behaviour, do not grep the text)."""
    gt = dict(target.get("gate", target))
    for src_key, gate_key in (("room_banned", "room_bans"), ("light_banned", "light_bans")):
        if not gt.get(gate_key) and gt.get(src_key):
            gt[gate_key] = gt[src_key]
    return scg.selfconflicts(gt)


def census_card(path):
    """A card on disk, by the same reading as `census`: load it the way the shipped gate loads it, mirror
    the light name, count."""
    return census(scg.load_card(path))


def fmt(row):
    return (f"{row['scope']} figure {row['figure']}: token {row['token']!r} carries the card's own ban "
            f"{row['banned_word']!r} ({row['reading']})")


def caption_sections(doc, scene, card_text):
    """Every caption of the record must sit in the card verbatim. A card that drops ask C's caption is not
    the rebuilt card: the captions are the only source this item allows."""
    bad = []
    n = scg.norm(card_text)
    for ak, cap in caps_for(doc, scene):
        if scg.norm(cap) not in n:
            bad.append("CARD_CAPTION_MISSING %s the card does not carry caption %s verbatim - the captions "
                       "are the only source of this card" % (scene, ak))
    return bad


def compose(scene, doc):
    """One composition: the base composes the card and facts, this pass judges them with its own teeth."""
    caps = caps_for(doc, scene)
    card_text, ev, unresolved = tc.compose_card(scene, spec(scene), doc, caps)
    facts = tc.compose_facts(scene, spec(scene), doc, card_text, ev, unresolved)
    return card_text, facts, ev, unresolved, caps


def spec(scene):
    with open(spec_path(scene), "r", encoding="utf-8") as fh:
        return json.load(fh)


def my_faults(scene, doc, facts, card_text):
    bad = caption_sections(doc, scene, card_text)
    for r in census(facts):
        bad.append("CARD_SELF_CONFLICT %s %s - a card cannot require a thing it forbids" % (scene, fmt(r)))
    return bad


def scope_isolation_faults():
    """Tag isolation is a fact, not an intention: a shared record, raw suffix or spec dir would make the
    2025 record and this pass's record the same file."""
    bad = []
    a, b = tc.TAGS[""], tc.TAGS["2"]
    for k in ("record", "spec_dir", "raw_suf"):
        if a[k] == b[k]:
            bad.append("TAG_NOT_ISOLATED %s: tag \"\" and tag 2 share %s=%s" % (k, k, a[k]))
    if not set(SCENES) <= set(tc.SCENES):
        bad.append("SCOPE_RANGE %s outside the registry %s" % (list(SCENES), list(tc.SCENES)))
    if set(ASKS) - set(tc.ASKS):
        bad.append("ASKS_SCOPE this pass asks %s, not registered" % sorted(set(ASKS) - set(tc.ASKS)))
    return bad


# ---------------------------------------------------------------- modes
def do_state(args):
    print("CARD-VL2 (tag 2) scope scenes=%s asks=%s model=%s" % (list(SCENES), list(ASKS), tc.MODEL_DEFAULT))
    print(f"record={RECORD2} exists={os.path.isfile(RECORD2)}")
    print(f"spec_dir={SPEC_DIR2} exists={os.path.isdir(SPEC_DIR2)} "
          f"files={sorted(os.path.basename(p) for p in glob.glob(spec_path('*')))}")
    print(f"raw captions (tag 2): "
          f"{sorted(os.path.basename(p) for p in glob.glob(os.path.join(tc.RAW_DIR, '*_vl2_*.txt')))}")
    print(f"2025 record untouched: "
          f"{tc.OUT} exists={os.path.isfile(tc.OUT)}"
          + (f" mtime={mtime(tc.OUT)}" if os.path.isfile(tc.OUT) else ""))
    for scene in SCENES:
        for p in (card_path(scene), facts_path(scene)):
            print(f"  {'exists' if os.path.isfile(p) else 'ABSENT '} {p}"
                  + (f" mtime={mtime(p)} bytes={os.path.getsize(p)}" if os.path.isfile(p) else ""))
    print("ask C sha256=%s (registered on the base, provenance in the record)" % tc.sha_text(ASK_C))
    print("ask C:\n" + ASK_C)
    bad = scope_isolation_faults()
    print("isolation_faults=%d %s" % (len(bad), bad[:3]))
    return 2 if bad else 0


def do_run(args):
    argv = ["--run", "--tag", TAG, "--model", tc.MODEL_DEFAULT,
            "--scenes", ",".join(SCENES), "--asks", ",".join(ASKS),
            "--max-tokens", str(args.max_tokens), "--timeout", str(args.timeout)]
    if args.rerun:
        argv.append("--rerun")
    return tc.main(argv)


def do_cards(args):
    """Write the card + facts ONLY if the composition passes this pass's teeth: the base card gate, every
    caption verbatim in the card, and 0 self-contradictions. A card that contradicts itself is not written:
    the prompt would be forbidden to say what the card requires."""
    doc = tc.load_doc(TAG)
    if not doc:
        print(f"RED no record at {RECORD2} (run --run)")
        return 2
    pre = tc.doc_faults(doc, tc.vp.vision_table())
    if pre:
        print("RED the caption record is not clean; cards are written only from a clean record")
        for p in pre[:12]:
            print("  FAULT " + p)
        return 2
    scenes = args.scenes or list(SCENES)
    bad = scope_isolation_faults()
    for scene in scenes:
        if not os.path.isfile(spec_path(scene)):
            bad.append("SPEC_MISSING %s" % spec_path(scene))
    if bad:
        for b in bad:
            print("  FAULT " + b)
        return 2
    rc = 2
    written = []
    for scene in scenes:
        card_text, facts, ev, unresolved, caps = compose(scene, doc)
        old_tokens, old_src = tc.old_gate_tokens(scene)
        faults = tc.card_faults(facts, card_text) + my_faults(scene, doc, facts, card_text)
        # the prompt-gate delta, measured the way the base builder measures it (old required tokens tested
        # against the new card + its captions), recorded before the self-conflict verdict so the read-out has it
        lost = [t for t in old_tokens if not tc.find_quote(caps, t) and tc.card_norm(t) not in tc.card_norm(card_text)]
        kept = len(old_tokens) - len(lost)
        facts["_delta_vs_old_gate"] = {
            "measured": tc.now(),
            "basis": ("the tokens the superseded gate required (%s), tested against the new card + captions; "
                      "a measurement, not a judgement" % old_src),
            "required_by_old_gate": len(old_tokens), "supported_by_new_card": kept,
            "unsupported_by_new_card": lost}
        cen = census(facts)
        print(f"{scene}: figures={len(facts['figures'])} evidence={len(facts['gate']['evidence'])} "
              f"unresolved={unresolved} self_conflicts={len(cen)} old_gate_tokens={len(old_tokens)} "
              f"kept={kept} unsupported={len(lost)}")
        for f in faults:
            print("  FAULT " + f)
            bad.append(f)
        if faults:
            continue
        with open(card_path(scene), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(card_text)
        with open(facts_path(scene), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(facts, fh, indent=1, ensure_ascii=False, sort_keys=True)
            fh.write("\n")
        written.append(scene)
        after = census_card(facts_path(scene))
        print(f"  WROTE card={card_path(scene)} bytes={os.path.getsize(card_path(scene))} "
              f"facts={facts_path(scene)} card_sha256={tc.sha_file(card_path(scene))[:16]}")
        print(f"  census of the written facts.json by scene_card_gate.selfconflicts = {len(after)}")
        for r in after[:30]:
            print("    " + fmt(r))
        if after:
            bad.append("SELF_CONFLICT_ON_DISK %s the written card still contradicts itself" % scene)
    print("card_faults=%d self_conflicts=%d" % (len(bad), 0 if not bad else -1))
    if not bad:
        print("VERDICT CARD_VL2 CARDS CLEAN self_conflicts=0")
        rc = 0
    else:
        print("VERDICT CARD_VL2 CARDS RED")
    return rc


def do_check(args):
    """The record and the cards by the base gate, then this pass's teeth on the cards that are on disk."""
    rc = tc.main(["--check", "--tag", TAG])
    doc = tc.load_doc(TAG)
    if not doc:
        return 2
    bad = scope_isolation_faults()
    print("this pass's teeth on the cards on disk (scope %s):" % list(SCENES))
    for scene in (args.scenes or list(SCENES)):
        fp = facts_path(scene)
        cp = card_path(scene)
        if not (os.path.isfile(fp) and os.path.isfile(cp)):
            bad.append("CARD_NOT_WRITTEN %s" % scene)
            continue
        with open(fp, "r", encoding="utf-8") as fh:
            facts = json.load(fh)
        if TAG not in str(facts.get("_source", "")) and "card_rebuild" not in str(facts.get("_source", "")):
            bad.append("CARD_NOT_FROM_THIS_RECORD %s _source is %r, not the tag-2 record" % (scene, facts.get("_source")))
        with open(cp, "r", encoding="utf-8") as fh:
            card_text = fh.read()
        rows = census_card(fp)
        sections = caption_sections(doc, scene, card_text)
        print(f"  {scene} card_sha256={tc.sha_file(cp)[:12]} self-contradictions={len(rows)} "
              f"caption_sections_missing={len(sections)}")
        for r in rows[:40]:
            print("     " + fmt(r))
        for s in sections:
            print("     FAULT " + s)
        bad += sections
        if rows:
            bad.append("SELF_CONFLICT %s %d self-contradictions in the card on disk" % (scene, len(rows)))
    for b in bad:
        print("  FAULT " + b)
    print("VERDICT CARD_VL2 CHECK CLEAN self_conflicts=0" if not bad and rc == 0
          else "VERDICT CARD_VL2 CHECK RED")
    return 0 if (not bad and rc == 0) else 2


def do_census(args):
    """The measurement the item names: self-contradictions of each card, by the shipped gate's own function.
    Reads the cards on disk; writes nothing."""
    print(f"scene_card_gate.selfconflicts over the cards on disk (reading the gate source, "
          f"{os.path.join(os.path.dirname(__file__), 'scene_card_gate.py')})")
    total = 0
    for scene in tc.SCENES:
        fp = facts_path(scene)
        if not os.path.isfile(fp):
            print(f"{scene}: no facts.json on disk")
            continue
        gt = dict(scg.load_card(fp))
        for src_key, gate_key in (("room_banned", "room_bans"), ("light_banned", "light_bans")):
            if not gt.get(gate_key) and gt.get(src_key):
                gt[gate_key] = gt[src_key]
        rows = scg.selfconflicts(gt)
        total += len(rows)
        print(f"{scene} card={gt['_card_path']} source={gt['_card_source']} "
              f"card_sha256={gt['_card_sha256'][:12]} bytes={gt['_card_bytes']} "
              f"light_bans_read={len(gt.get('light_bans', []))} room_bans_read={len(gt.get('room_banned', []))} "
              f"self-contradictions={len(rows)}")
        for r in rows:
            print("   " + fmt(r))
    print(f"self-contradictions total={total}")
    return 0


# ---------------------------------------------------------------- selftest
def seed_census_cards():
    """(name, facts, expect). A facts dict is judged by `census`, the same function the write path uses, so a
    seeded contradiction is charged on the shape that ships. `expect` 1 = at least one self-contradiction,
    0 = none (a gate that can never reach 0 proves nothing, and a gate that never fires is worthless)."""
    def fig(banned, alias):
        return {"role": "figure", "appearance": "a person", "head_in_frame": "visible",
                "visible": ["a person standing"], "banned": banned, "aliases": [alias]}

    def base(figs, per_chunk, room, light, bans):
        return {"scene": "SEED", "figures": figs, "per_chunk_tokens": per_chunk, "aliases": [],
                "room_required": room, "room_banned": bans["room"], "light_required": light,
                "light_banned": bans["light"], "banned": {"any": bans["any"]}, "head_allow": bans["head"],
                "consent_gate": {"ban": bans["consent"]}}
    no_bans = {"room": [], "light": [], "any": [], "head": [], "consent": []}
    clean = base([fig(["mud"], "the woman")], {"1": ["her red dress"]}, ["the stone floor"],
                 ["daylight from a window"],
                 {"room": ["the couch"], "light": ["candlelight"], "any": ["fur"], "head": ["braid"],
                  "consent": ["maybe"]})
    S = []
    S.append(("required_token_carries_own_figure_ban",
              base([fig(["head"], "the woman")], {"1": ["smooth metallic head"]}, ["the stone floor"],
                   ["even cool white light"], no_bans), 1))
    S.append(("light_row_carries_own_figure_ban",
              base([fig(["skin"], "the woman")], {"1": ["the woman"]}, ["the stone floor"],
                   ["highlighting the woman's skin"], no_bans), 1))
    S.append(("room_row_uses_figure_alias",
              base([fig(["ceramic"], "the robot")], {"1": ["the robot"]},
                   ["the metal frame of the robot"], ["even light"], no_bans), 1))
    S.append(("required_token_carries_any_ban",
              base([fig(["leather"], "the woman")], {"1": ["fur trim"]}, ["the floor"], ["even light"],
                   dict(no_bans, any=["fur"])), 1))
    S.append(("required_token_carries_room_ban",
              base([fig(["silk"], "the woman")], {"1": ["the couch"]}, ["the floor"], ["even light"],
                   dict(no_bans, room=["couch"])), 1))
    S.append(("required_token_carries_consent_ban",
              base([fig(["wool"], "the woman")], {"1": ["maybe later"]}, ["the floor"], ["even light"],
                   dict(no_bans, consent=["maybe"])), 1))
    S.append(("required_token_carries_head_allow_ban",
              base([fig(["linen"], "the woman")], {"1": ["her braid"]}, ["the floor"], ["even light"],
                   dict(no_bans, head=["braid"])), 1))
    S.append(("light_ban_read_under_light_bans",
              base([fig(["lace"], "the woman")], {"1": ["the woman"]}, ["the floor"],
                   ["lit by candlelight"], dict(no_bans, light=["candlelight"])), 1))
    S.append(("room_ban_read_under_room_bans",
              base([fig(["denim"], "the woman")], {"1": ["the woman"]}, ["the couch in the corner"],
                   ["even light"], dict(no_bans, room=["couch"])), 1))
    S.append(("clean_card_self_consistent", clean, 0))
    return S


def seed_doc_faults():
    """(name, kind, expect). Mutate the real tag-2 record in memory, judge with the base's own doc_faults,
    restore. A scope that hides rows, a row outside the scope, an unasked ask: all must be charged."""
    doc = tc.load_doc(TAG)
    if not doc:
        return []
    import copy
    table = tc.vp.vision_table()
    S = []
    d = copy.deepcopy(doc)
    d["scope"] = {"scenes": list(SCENES) + ["GI072"], "asks": list(ASKS)}
    S.append(("scope_hides_a_scene_that_was_never_captions", d, "ROW_MISSING"))
    d = copy.deepcopy(doc)
    d["scope"] = {"scenes": list(SCENES), "asks": ["A", "B"]}
    S.append(("row_of_an_undeclared_ask", d, "ASK_ROW_UNDECLARED"))
    d = copy.deepcopy(doc)
    d["scope"] = {"scenes": [], "asks": []}
    S.append(("scope_names_nothing", d, "SCOPE_INCOMPLETE"))
    d = copy.deepcopy(doc)
    d["scope"] = {"scenes": ["GI999"], "asks": list(ASKS)}
    S.append(("scope_names_an_unknown_scene", d, "SCOPE_RANGE"))
    d = copy.deepcopy(doc)
    d["rows"] = [r for r in d["rows"] if (r.get("scene"), r.get("ask_id")) != (SCENES[0], "C")]
    S.append(("row_missing_from_the_declared_scope", d, "ROW_MISSING"))
    d = copy.deepcopy(doc)
    d["asks"]["C"]["sha256"] = "0" * 64
    S.append(("ask_text_swapped_in_the_record", d, "ASK_SHA"))
    out = []
    for name, mut, want in S:
        fired = tc.doc_faults(mut, table)
        out.append((name, want, fired))
    return out


def seed_card_teeth():
    """(name, facts, card_text, expect). Every caption of the record must sit in the card verbatim: the
    captions are the only source this item allows, so a card that drops caption C is not the rebuilt card."""
    doc = tc.load_doc(TAG)
    if not doc or not all(os.path.isfile(spec_path(s)) for s in SCENES):
        return []
    scene = SCENES[0]
    card_text, facts, ev, unresolved, caps = compose(scene, doc)
    out = [("caption_C_dropped_from_the_card", facts, card_text.replace(caps[-1][1], ""), "CARD_CAPTION_MISSING")]
    out.append(("card_as_composed", facts, card_text, "NO_FAULT"))
    return out


def do_selftest(args):
    bad = []
    S = seed_census_cards()
    fired = 0
    for name, facts, expect in S:
        rows = census(facts)
        n = len(rows)
        ok = (n > 0) if expect == 1 else (n == 0)
        fired += 1 if ok else 0
        if not ok:
            bad.append(name)
        print(f"census seed {name:38s} self_conflicts={n} expect_{'fault' if expect else 'zero'} "
              f"{'OK' if ok else 'SILENT'}" + (f" first={rows[0]['token']!r} vs {rows[0]['banned_word']!r}" if rows else ""))
    print(f"census seeds: {len(S)}; fired={fired}, silent={len(S) - fired}")
    for n, f in [("isolation", scope_isolation_faults())]:
        print(f"{n} faults (0 expected): {len(f)} {f[:2]}")
        if f:
            bad.append(n)
    doc = tc.load_doc(TAG)
    if not doc:
        print("RED no record at %s: --selftest seeds the real record, run --run first" % RECORD2)
        return 2
    doc_seeds = seed_doc_faults()
    fired = 0
    for name, want, fs in doc_seeds:
        hit = [x for x in fs if x.startswith(want)]
        if hit:
            fired += 1
        else:
            bad.append(name)
        print(f"doc seed {name:38s} expect={want:20s} fired={len(hit)} first={(fs[0][:110] if fs else 'SILENT')}")
    print(f"doc seeds: {len(doc_seeds)}; fired={fired}, silent={len(doc_seeds) - fired}")
    card_seeds = seed_card_teeth()
    for name, facts, text, want in card_seeds:
        fs = my_faults(SCENES[0], doc, facts, text)
        hit = [x for x in fs if x.startswith(want)] if want != "NO_FAULT" else fs
        ok = bool(hit) if want != "NO_FAULT" else not fs
        if not ok:
            bad.append(name)
        print(f"card seed {name:38s} expect={want:22s} faults={len(fs)} first={(fs[0][:110] if fs else '')}")
    print(f"card seeds: {len(card_seeds)}")
    print("VERDICT CARD_VL2 SELFTEST_CLEAN" if not bad else f"VERDICT CARD_VL2 SELFTEST BROKEN {bad}")
    return 0 if not bad else 2


def main(argv=None):
    argv = argv or sys.argv[1:]
    mode = argv[0] if argv else "--check"
    ap = {"--scenes": [], "--max-tokens": 3000, "--timeout": 600, "--rerun": False}
    i = 1
    while i < len(argv):
        if argv[i] in ap and i + 1 < len(argv) and argv[i] != "--rerun":
            v = argv[i + 1]
            ap[argv[i]] = ([s for s in v.split(",") if s] if argv[i] == "--scenes" else int(v))
            i += 2
        elif argv[i] == "--rerun":
            ap["--rerun"] = True
            i += 1
        else:
            i += 1
    ns = type("NS", (), {"scenes": ap["--scenes"], "max_tokens": ap["--max-tokens"],
                         "timeout": ap["--timeout"], "rerun": ap["--rerun"]})()
    if mode == "--state":
        return do_state(ns)
    if mode == "--run":
        return do_run(ns)
    if mode == "--cards":
        return do_cards(ns)
    if mode == "--check":
        return do_check(ns)
    if mode == "--census":
        return do_census(ns)
    if mode == "--selftest":
        return do_selftest(ns)
    print("usage: --state | --run | --census | --cards [--scenes a,b] | --check | --selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main())
