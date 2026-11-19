# fix_plan TOP step 1-3: the start-image CARD as data. notes/scenes/<SCENE>.md = the vision model's own words off
# the start still (stamped: model, md5, caption_status, read_scope); notes/scenes/<SCENE>.facts.json = the same
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
                  "consent_gate", "solo_phrases", "evidence")
CARD_TOP_KEYS = ("scene", "card", "caption", "audit", "image", "md5", "model", "status", "figures",
                 "room", "light", "camera", "gate")
CARD_FIG_KEYS = ("label", "kind", "noun", "pose", "head_in_frame", "visible", "not_visible")
CARD_HEAD_WORDS = ("head", "face", "eye", "eyes", "brow", "nose", "jaw", "mouth", "lip", "lips", "teeth",
                   "grin", "smile", "chin", "cheek", "forehead", "hair", "bald", "beard", "skull")
CARD_AGE_RE = re.compile(r"aged \d{2}|age of \d{2}|\b\d{2}[- ]year[- ]old|age \d{2}")
CARD_PUNCT = (("\u2014", " - "), ("\u2013", " - "), ("\u2019", "'"), ("\u2018", "'"),
              ("\u201c", '"'), ("\u201d", '"'))
CARD_SCOPE = "read_scope: the start still only. no rendered clip"


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


def card_owner(sent, aliases):
    """the label whose alias sits nearest the END of the sentence: a word answers for its nearest referent, so
    'her hair falls over its green arms' charges 'arms' to the card's figure 2, not to her. None = no referent."""
    low, best, best_d = card_norm(sent), None, 10 ** 9
    for lab, alist in aliases.items():
        for a in alist:
            i = low.rfind(card_norm(a))
            if i >= 0 and len(low) - i <= best_d:
                best, best_d = lab, len(low) - i
    return best


def card_beat0(p):
    """the opening beat: the text from 'At 00:00.000' to the next beat marker - the second the clip opens on."""
    m = re.search(r"At 00:00\.000", p)
    if not m:
        return ""
    nxt = p.find("At ", m.end() + 3)
    return p[m.end():nxt if nxt > 0 else len(p)]


def card_measure(nid, p):
    """The card gate run on ONE prompt string; every count is returned for the manifest. Nine rules:
    F-SUBJ the <Subject> count = the card's figure count; F-WORDS every gate token present in this chunk; F-SOLO
    no alone/only-person clause on a multi-figure card; F-BANNED no card-banned word charged to a figure (owner =
    nearest referent) and none in the all-figures ban list; F-HEAD no head/face words for a figure the card says
    the frame crops, outside the head_allow out-of-frame phrasing; F-POSE the 00:00.000 beat carries the card's
    pose for each figure and says none of the poses the card does not show; F-ROOM the card's room/light words
    present; F-ROOM2 no room word the card does not name; F-AGE every age number carries the card's canon marker
    in its own sentence (an age is a canon declaration, not a sighting); F-CONSENT the consent row: banned claims
    absent, required card-honesty lines present."""
    gt = card_facts(nid)["gate"]
    out = {}
    np = card_norm(p)
    sent = [s for s in re.split(r"(?<=[.!?])\s+", p) if s.strip()]
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
    out["consent_hits"] = [c for c in gt["consent_gate"]["ban"] if card_norm(c) in np]
    out["consent_missing"] = [c for c in gt["consent_gate"]["require"] if card_norm(c) not in np]
    return out


def card_fires(nid, out):
    """the nine card rules as (code, detail) pairs on one prompt's measurement; [] = the prompt is card-faithful."""
    gt = card_facts(nid)["gate"]
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
    if out["consent_hits"]:
        hit.append(("F-CARD-CONSENT", "%s" % ", ".join(out["consent_hits"][:3])))
    if out["consent_missing"]:
        hit.append(("F-CARD-CONSENT2", "no card-honesty line %s" % ", ".join(out["consent_missing"][:2])))
    return hit


def ck_top_card(g, ctx):
    """F-CARD: ck_card_2.ck_figures proved every <Subject> has an input row; this proves the WORDS next to each
    <Subject> are the card's words. Both chunks of a TOP graph run through card_measure/card_fires, the counts land
    in g['card_flags'] for the manifest, and every hit is a FAIL. 9 rules x 2 chunks."""
    if ctx["nid"] not in CARDS:
        return []
    bad, flags = [], {}
    for ch, key in (("c0", "detailed_description"), ("c1", "integrated_multimodal_description")):
        out = card_measure(ctx["nid"], top_prompt(g, key))
        flags[ch] = out
        for code, det in card_fires(ctx["nid"], out):
            bad.append("F-CARD %s %s: %s" % (ch, code, det))
    g["card_flags"] = flags
    return bad


def ck_top_facts(g, ctx):
    """F-FACTS: the gate is only as honest as the card behind it. The facts file parses with every top-level, gate
    and figure-row key; its model/status/md5 are rows IN the card file; the card read the START STILL ONLY
    (read_scope, no rendered clip); every gate.evidence quote sits verbatim in the card (punctuation-folded);
    every word the gate requires (per-chunk, figure-visible, room, light) carries such a quote; the figure rows and
    the gate agree on the figure count and the card states it; the cited card/caption/audit paths exist; the facts
    scene is this graph's scene; head_in_frame covers every figure label. 11 rules."""
    if ctx["nid"] not in CARDS:
        return []
    bad = []
    f = card_facts(ctx["nid"])
    gt, md = f["gate"], card_md(ctx["nid"])
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
    for k in ("model", "status", "md5"):
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
    if f["scene"] != ctx["nid"]:
        bad.append("F-FACTS-SCENE: facts scene %s, graph %s" % (f["scene"], ctx["nid"]))
    if sorted(gt["head_in_frame"]) != sorted(str(r["label"]) for r in f["figures"]):
        bad.append("F-FACTS-HEADKEY: head_in_frame keys do not match the figure labels")
    return bad


def ck_top_md(g, ctx):
    """F-MD-SYNC: notes/hc15_top_prompts_20261025.md is the prose record a human reads; the graph is what runs.
    This graph's c0/c1 fields must equal the record's take-A blocks BYTE FOR BYTE (the 2.1b clone of
    top_selftest's F-21B-SYNC, run on the prose side), so the file a reader trusts is the text that renders."""
    if ctx["nid"] not in CARDS:
        return []
    bad = []
    take = TOP_BY_ID[ctx["top"]]["take_a"]
    for ch, key in (("c0", "detailed_description"), ("c1", "integrated_multimodal_description")):
        want, got = top_md(take, key), top_prompt(g, key)
        if want is None:
            bad.append("F-MD-SYNC %s: %s has no %s block for %s" % (ch, TOP_MD, key, take))
        elif want != got:
            d = next((i for i in range(min(len(want), len(got))) if want[i] != got[i]), min(len(want), len(got)))
            bad.append("F-MD-SYNC %s: the graph's %s and the prose record differ (%d vs %d words), first byte %d: %r"
                       % (ch, key, len(word_re.findall(got)), len(word_re.findall(want)), d, got[d:d + 40]))
    return bad
