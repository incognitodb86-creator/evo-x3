"""CARD-VL - re-read the three GI start stills with the UNCENSORED vision model and rebuild the scene
cards from what it says.

Derrick 2026-10-25 6:48 PM CT (first of his picks): "Redo the orc, robot and GI072 scene cards with the
uncensored vision model". The three cards `notes/scenes/GI046.md GI063.md GI072.md` were written at
04:34-04:38 CT by `coding_swift15_iq3s`, which refused: `caption_status: REFUSAL_TRUNCATED`, "I won't
catalogue her body, wardrobe, pose, and position in the detail you're asking for". Every prompt built off
those cards is thin, and L18 makes the card the ONLY source for an appearance word, so ORC-ROBOT,
SUBJECT-LABELS and the GI063 render all sit behind the cards, not behind the GPU.

The uncensored vision model is named by its own file, read off the serving config:
`C:/AI/director/config/llama-swap.yaml:74-86` id `vl_judge` (aliases vision_9b, darkroast) =
`Qwen3.5-9B-The-Defiant-Fable-DARK-ROAST-Uncensored-Heretic-NEO-IMATRIX-MAX-MTP.Q8_0.gguf`
`--mmproj ...mmproj-Q8_0.gguf`. Vision capability is never assumed (3.17's rule): it is read off the yaml
by `ali163_vision_probe.vision_table`.

One variable changed vs the 04:34 cards: the MODEL. The two asks are the same ask A / ask B text recorded
in those cards, with only the pi read-tool sentence replaced by "Look at the attached image." because this
transport attaches the image bytes to the request (the exact delta is stored in the record). The L21 fix
is applied: `reasoning_effort=none` + `chat_template_kwargs.enable_thinking=false`, max_tokens above the
reasoning phase, so the answer lands in `content` and not in `reasoning_content`.

GPU discipline: gpu_guard.ps1 (no arguments) rc 0 = IDLE is required in front of EVERY request, one model
loaded at a time, all requests inside one process so no LLM request is in flight while the vLM loads. No
render, no queue post, no graph, no ComfyUI/llama-swap control call. Objective rows only: no score, rank,
keep, best, winner - KEEP is Derrick's alone, and a row carrying one of those keys is a fault (3.17's
BANNED census).

Modes:
  python C:/AI/community/notes/top_card_vl_build.py --state          # measure: vision set, guard, stills, current cards
  python C:/AI/community/notes/top_card_vl_build.py --run            # 3 scenes x 2 asks on vl_judge, paid rows saved as they land
  python C:/AI/community/notes/top_card_vl_build.py --check          # the record's own integrity, then VERDICT
  python C:/AI/community/notes/top_card_vl_build.py --selftest       # seeded faults must fire, 0 on the real record
  python C:/AI/community/notes/top_card_vl_build.py --cards          # write the cards + facts.json from a facts spec (verbatim-quote enforced)

CARD-VL2 (Derrick 2026-10-26 7:08 AM CT "Yes, have Forge rebuild the GI063 card from the uncensored
captions only" + 8:23 AM CT "yea it needs to have the vision model redo them") adds `--tag`: a caption
pass with its OWN record, raw captions and facts spec, so the CARD-VL record of 2026-10-25 keeps the exact
bytes the live cards and needs_derrick.md row 29 cite. `--tag` with no flag is the 2025 pass, unchanged;
`--tag 2` = `notes/card_rebuild_results.json` + `notes/scenes/raw/<ID>_vl2_<ASK>.txt` +
`notes/card_rebuild_facts/`. Ask C names the regions the 2025 cards left silent (head and face in frame,
the groin and pelvic region as visible, anatomy form and colour if visible, the size relation, what each
hand touches) - the gap needs_derrick.md row 28 measured on the GI046 card. A card this builder writes is
judged by `scene_card_gate.selfconflicts` before it can ship: a card whose own required token carries its
own ban is a CARD_SELF_CONFLICT, and the shipped gate charges that collision to the prompt (measured on
the 2025 GI063 card: 12 self-contradictions at `scene_card_gate.py --table`; a card that can ship: 0).
"""

import copy
import datetime
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, "C:/AI/community/notes")
import ali163_vision_probe as vp  # the 3.17 instrument: transport, guard, vision table, dims, shas
import scene_card_gate as scg     # the shipped card gate: its own selfconflicts is the self-consistency test

NOTES = "C:/AI/community/notes"
SCENES = ("GI046", "GI063", "GI072")          # the orc, the robot and GI072 - Derrick's three
SCENE_TITLE = {"GI046": "the orc", "GI063": "the robot", "GI072": "GI072"}
APPROVED_DIR = "C:/Users/derek/5slock/approved_characters/GROK_IMAGINE_2026-10-19"
COMFY_INPUT = "C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/input/community/hc"
CARD_DIR = os.path.join(NOTES, "scenes")
RAW_DIR = os.path.join(CARD_DIR, "raw")
OUT = os.path.join(NOTES, "top_card_vl_results.json")
SPEC_DIR = os.path.join(NOTES, "top_card_vl_facts")
# A caption pass is a TAG, and a tag owns its record, its raw captions and its facts spec. The 2025 record
# is cited by the live cards and by needs_derrick.md row 29, so a later pass never writes over it. A pass
# that wants its own record registers a tag here: card_vl2_build.py adds tag "2" (its own record, raw
# captions, facts spec, ask C) at import, so the 2025 pass keeps the exact bytes the cards cite. The one
# rule a tag cannot escape: the record, the raw captions and the spec are the tag's, never shared.
TAGS = {
    "": {"record": OUT, "spec_dir": SPEC_DIR, "raw_suf": "_vl_", "mark": "top_card_vl",
         "asks": ["A", "B"], "item": "CARD-VL, Derrick 2026-10-25 6:48 PM CT"},
}


def ctx(tag=""):
    """The paths a tag owns. An unknown tag stops the run: a pass that means to write tag 2 and lands on
    tag \"\" would overwrite the 2025 record that the live cards cite as evidence."""
    if tag not in TAGS:
        raise SystemExit("RED unknown --tag %r (valid tags: %s)"
                         % (tag, ",".join(repr(t) for t in sorted(TAGS))))
    return TAGS[tag]


def raw_path(scene, ask_id, tag=""):
    return os.path.join(RAW_DIR, f"{scene}{ctx(tag)['raw_suf']}{ask_id}.txt")
AUDIT = os.path.join(NOTES, "hc15_figures_20261025.md")   # the figures audit the cards cite
SCHEMA = "top-card-vl-1"
MODEL_DEFAULT = "vl_judge"
MIN_WORDS = 60                       # 3.17 measured 164-267 words on this model with no-thinking
UNCENSORED_RE = re.compile(r"uncensored|abliterated", re.I)
CARD_PUNCT = (("\u2014", " - "), ("\u2013", " - "), ("\u2019", "'"), ("\u2018", "'"),
              ("\u201c", '"'), ("\u201d", '"'))   # same fold as hc15_anchor_carry_build.py:303 card_norm

# The two asks of the 04:34 cards, kept word-for-word after the first sentence (the pi read-tool
# instruction cannot apply to a request that attaches the image), so the model is the only variable.
ASK_A = ("Look at the attached image. Then list every figure in frame - species/race, build, skin, "
         "hair colour, wardrobe, pose, position - then the room, the props and the light. Quote nothing "
         "you cannot see. No prose before it.")
ASK_B = ("Look at the attached image. Give only the non-sexual identity and composition record: for EACH "
         "figure in frame state species as visible, build, skin tone, hair colour, the wardrobe items "
         "visible, and where it sits in the frame; then the room, the props and the light. Do not describe "
         "any sexual act, nudity, genitals, nipple/areola, erection, or body position during a sexual act. "
         "No prose before it.")
ASKS = {"A": ASK_A, "B": ASK_B}
ASK_PROVENANCE = {
    "A": "notes/scenes/GI046.md 'prompt_sent' (ask A, 2026-10-25 04:34 CT): 'Use the read tool once on "
         "<path>.' replaced by 'Look at the attached image.'; the rest is byte-identical.",
    "B": "notes/scenes/GI072.md 'prompt_sent' (ask B, 2026-10-25 04:38 CT): same first-sentence "
         "substitution; the rest is byte-identical.",
}
CAPTION_HEAD = {  # the verbatim sections of a card, in ask order; card_faults reads the "## caption A" split
    "A": "## caption A verbatim (full inventory ask)",
    "B": "## caption B verbatim (non-sexual identity + composition ask)",
}
BANNED = set(vp.BANNED) | {"score", "rank", "keep", "best", "winner", "verdict", "judgement"}
AGE_MIN = 21
AGE_SOURCE = ("C:/Users/derek/5slock/plans/canon/fiction-cond-lock.md v2.3.0: every character is a "
              "fictional adult aged 21+. The card carries the age floor as a row, never as an inference.")
# gate.evidence values must be verbatim in the card (the rule ck_top_card enforces), so the age evidence is
# one constant rendered in both places, never two sentences that can drift.
AGE_EVIDENCE = ("The frame alone gives no age cue; the canon lock declares every character a fictional adult "
                "aged 21+, so the age marker is a canon declaration, not an inference from a face. "
                "C:/Users/derek/5slock/plans/canon/fiction-cond-lock.md v2.3.0")
CARD_SCOPE_LINE = ("read_scope: the start still ONLY. No rendered clip, no frame of a render, "
                   "no contact sheet.")
CARD_TOP_KEYS = ("scene", "card", "caption", "audit", "image", "sha256", "model", "status", "figures",
                 "room", "light", "camera", "gate")          # hc15_anchor_carry_build.py:286
CARD_GATE_KEYS = ("figure_count", "aliases", "per_chunk_tokens", "banned", "head_in_frame", "head_allow",
                  "open_beat", "open_beat_ban", "room_required", "room_banned", "light_required",
                  "age_marker", "consent_gate", "solo_phrases", "evidence")   # :283
CARD_FIG_KEYS = ("label", "kind", "noun", "pose", "head_in_frame", "visible", "not_visible")  # :288
# The words that force an on-page adult age in prose (the shipped gate's list, unchanged: it is a prompt rule,
# not a picture fact). facts.age_min = 21 is a canon declaration, never a sighting.
AGE_REQUIRED = ["woman", "man", "girl", "boy", "lady", "guy", "female", "male"]
FACTS_SCHEMA = ("gate keys: figure_count, aliases, per_chunk_tokens, banned{1,2,any}, head_in_frame{1,2}, "
                "head_allow, open_beat{1,2}, open_beat_ban{1,2}, room_required, room_banned, light_required, "
                "age_marker, age_required, consent_gate{ban,require}, solo_phrases, evidence{token: card quote}. "
                "ck_top_facts: every gate.per_chunk_tokens entry, every figures[].visible token and every "
                "gate.room_required token has a quote in gate.evidence, and every quote sits verbatim in the "
                "card file (punctuation normalized: em/en dash to -, curly to straight quotes, "
                "case-insensitive). ck_top_card measures the graph prompts against this gate. Built by "
                "notes/top_card_vl_build.py --cards from notes/top_card_vl_facts/<ID>.json + "
                "notes/top_card_vl_results.json; a token no caption states is listed in _unresolved, never in a gate.")


def card_norm(s):
    """punctuation + case + whitespace fold only, no word changes (the gate's rule, copied so this
    builder enforces the same quote test the gate will run)."""
    s = str(s)
    for a, b in CARD_PUNCT:
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s.lower().strip())


def sha_file(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def sha_text(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def mtime_iso(p):
    return datetime.datetime.fromtimestamp(os.path.getmtime(p)).isoformat(timespec="seconds")


def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S CT")


def still_path(scene):
    return os.path.join(APPROVED_DIR, scene + ".jpg")


def comfy_copy(scene):
    return os.path.join(COMFY_INPUT, scene + ".jpg")


def load_doc(tag=""):
    p = ctx(tag)["record"]
    if not os.path.isfile(p):
        return None
    with open(p, "r", encoding="utf-8") as fh:
        doc = json.load(fh)
    doc.setdefault("tag", tag)
    return doc


def save_doc(doc, tag=None):
    p = ctx(doc.get("tag", "") if tag is None else tag)["record"]
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, p)


def new_doc(table, tag=""):
    c = ctx(tag)
    return {
        "schema": SCHEMA,
        "tag": tag,
        "goal": ("the GI046 (orc), GI063 (robot), GI072 scene cards re-read by the uncensored vision "
                 "model - Derrick 2026-10-25 6:48 PM CT" if tag == "" else
                 "the GI063 (robot) and GI046 (orc) scene cards rebuilt from the uncensored captions only, "
                 "the vision model redoning them - Derrick 2026-10-26 7:08 AM CT 'Yes, have Forge rebuild the "
                 "GI063 card from the uncensored captions only' + 8:23 AM CT 'yea it needs to have the vision "
                 "model redo them'; item " + c["item"]),
        "started": now(),
        "scope": {"scenes": list(SCENES), "asks": list(c["asks"])},
        "asks": {k: {"text": v, "sha256": sha_text(v), "provenance": ASK_PROVENANCE[k]}
                 for k, v in ASKS.items() if k in c["asks"]},
        "model_evidence": {
            "id": MODEL_DEFAULT,
            "source": "C:/AI/director/config/llama-swap.yaml:74-86 read 2026-10-25",
            "table": [r for r in table if r["id"] == MODEL_DEFAULT],
            "uncensored_proof": "the model file named by --mmproj/cmd carries 'Uncensored'",
        },
        "gates": [],
        "rows": [],
        "role": ("objective record only. no score, no rank, no keep, no judgement of any caption or "
                 "still. KEEP is Derrick's alone. every read is of a START STILL, never of a rendered clip."),
    }


# ------------------------------------------------------------------ --state

def do_state(args):
    table = vp.vision_table()
    rc, text = vp.guard_rc()
    live, err = vp.live_models()
    print(f"# CARD-VL state {now()}  gpu_guard rc={rc} {text!r}")
    print(f"# llama-swap vision set read off {vp.SWAP_YAML}: {len(table)} ids")
    for r in table:
        unc = "UNCENSORED" if UNCENSORED_RE.search(r["evidence"]) else "not-uncensored-by-filename"
        print(f"  {r['id']:24s} kinds={','.join(r['kinds'])} aliases={','.join(r['aliases'])} {unc}")
        print(f"      {r['evidence'][:200]}")
    if err:
        print(f"  live_models: {err}")
    else:
        print("  live: " + ", ".join(f"{k}={v['status']}" for k, v in sorted(live.items())))
    for sc in SCENES:
        ap, cp = still_path(sc), comfy_copy(sc)
        card = os.path.join(CARD_DIR, sc + ".md")
        facts = os.path.join(CARD_DIR, sc + ".facts.json")
        status = "no card"
        if os.path.isfile(card):
            with open(card, "r", encoding="utf-8") as fh:
                m = re.search(r"^caption_status:\s*(\S+)", fh.read(), re.M)
            status = m.group(1) if m else "card with no caption_status row"
        print(f"  {sc} ({SCENE_TITLE[sc]}): approved_sha={sha_file(ap)[:16]} dims={vp.image_dims(ap)} "
              f"bytes={os.path.getsize(ap)} comfy_copy_sha_match={sha_file(ap) == sha_file(cp)} "
              f"card_status={status} facts={'yes' if os.path.isfile(facts) else 'ABSENT'} "
              f"card_in_gate_registry={'yes' if os.path.isfile(facts) else 'no (CARDS is keyed on facts.json)'}")
        print(f"      card={card} mtime={mtime_iso(card) if os.path.isfile(card) else '-'}")
    print(f"  tag={args.tag!r} record={ctx(args.tag)['record']} exists={os.path.isfile(ctx(args.tag)['record'])} "
          f"spec_dir={ctx(args.tag)['spec_dir']} exists={os.path.isdir(ctx(args.tag)['spec_dir'])}")
    print(f"  raw_captions={RAW_DIR} suffix={ctx(args.tag)['raw_suf']!r} "
          f"files={sorted(os.path.basename(p) for p in __import__('glob').glob(os.path.join(RAW_DIR, '*' + ctx(args.tag)['raw_suf'] + '*.txt')))}")
    print("  self_conflicts (scene_card_gate.selfconflicts, the shipped gate's own test):")
    for sc in SCENES:
        fp = os.path.join(CARD_DIR, sc + ".facts.json")
        if not os.path.isfile(fp):
            print(f"    {sc}: no facts.json on disk")
            continue
        gt = scg.load_card(fp)
        rows = scg.selfconflicts(gt)
        print(f"    {sc} card={gt['_card_sha256'][:12]} bytes={gt['_card_bytes']} self-contradictions={len(rows)}")
        for r in rows[:40]:
            print(f"       {r['scope']} {r['figure']}: token {r['token']!r} carries the card's own ban "
                  f"{r['banned_word']!r} ({r['reading']})")
    print(f"  audit_cited={AUDIT} exists={os.path.isfile(AUDIT)}")
    return 0


# ------------------------------------------------------------------ --run

def do_run(args):
    table = vp.vision_table()
    ids = {r["id"] for r in table}
    if args.model not in ids:
        print(f"REFUSE model {args.model} is not in the llama-swap vision set ({sorted(ids)})")
        return 3
    ev = " ".join(r["evidence"] for r in table if r["id"] == args.model)
    if not UNCENSORED_RE.search(ev):
        print(f"REFUSE model {args.model} carries no 'Uncensored'/'abliterated' in its served file: {ev[:160]}")
        return 3
    doc = load_doc(args.tag) or new_doc(table, args.tag)
    extra = {"reasoning_effort": "none", "chat_template_kwargs": {"enable_thinking": False}}
    tag_arg = f"--tag {args.tag} " if args.tag else ""
    command = (f"python C:/AI/community/notes/top_card_vl_build.py --run {tag_arg}--model {args.model} "
               f"--scenes {','.join(args.scenes)} --asks {','.join(args.asks)} "
               f"--max-tokens {args.max_tokens} --no-thinking")
    done = {(r["scene"], r["ask_id"]) for r in doc["rows"]
            if r.get("http_status") == 200 and r.get("caption", "").strip()}
    for sc in args.scenes:
        for ak in args.asks:
            key = (sc, ak)
            if key in done and not args.rerun:
                print(f"skip {sc}/{ak}: a paid caption row is already in the record (never re-ask)")
                continue
            rc, text = vp.guard_rc()
            if int(rc) != 0:
                print(f"gpu_guard rc={rc} {text!r} - NOT idle, refusing to load a model "
                      f"(a mid-render swap is the RENDER-TIMEOUT failure)")
                return 7
            doc["gates"].append({"ts": vp.now_iso(), "kind": "pre-request", "gpu_guard_rc": int(rc),
                                 "gpu_guard_text": text, "scene": sc, "ask_id": ak})
            ap = still_path(sc)
            row = vp.ask(args.model, sc, ap, args.max_tokens, args.timeout, sha_text(ASKS[ak]),
                         extra=extra, arm="card-ask-" + ak + ";no-thinking",
                         prompt=ASKS[ak], command=command)
            row["scene"] = sc
            row["ask_id"] = ak
            row["still_id"] = sc
            row["ask_sha256"] = sha_text(ASKS[ak])
            row["guard_rc"] = int(rc)
            row["guard_text"] = text
            row["comfy_input_copy"] = comfy_copy(sc).replace("\\", "/")
            row["comfy_copy_sha_match"] = sha_file(ap) == sha_file(comfy_copy(sc))
            row["asked_at_local"] = now()
            raw = ""
            if row["http_status"] == 200 and row["caption"].strip():
                raw = raw_path(sc, ak, args.tag).replace("\\", "/")
                os.makedirs(RAW_DIR, exist_ok=True)
                with open(raw, "w", encoding="utf-8", newline="\n") as fh:
                    fh.write(row["caption"])
            row["raw_path"] = raw
            row["raw_sha256"] = sha_file(raw) if raw else ""
            doc["rows"] = [r for r in doc["rows"] if (r.get("scene"), r.get("ask_id")) != key] + [row]
            # the scope is what this record covers, written from the run itself: the scenes it asked about
            # plus any scene it already paid for, and the tag's asks as the contract. A run of 2 of 3
            # scenes is 2 x asks, not 3 x asks, and a missing asked row stays ROW_MISSING.
            doc["scope"] = {"scenes": sorted(set(args.scenes) | {r.get("scene") for r in doc["rows"]}),
                            "asks": sorted(ctx(args.tag)["asks"])}
            save_doc(doc)
            print(f"{sc}/{ak}: http={row['http_status']} finish={row['finish_reason']} "
                  f"words={row['caption_words']} reasoning_words={row['reasoning_words']} "
                  f"wall={row['wall_s']}s declines={row['decline_markers']} guard_rc={row['guard_rc']} "
                  f"raw={raw or 'NONE'}")
    print(f"record: {ctx(args.tag)['record']} rows={len(doc['rows'])} scope="
          f"{doc.get('scope', 'none (the 2025 shape)')}")
    return 0


# ------------------------------------------------------------------ the record's own integrity

def doc_faults(doc, table):
    """Every fault here is a claim the record makes about itself. Seeded in --selftest."""
    bad = []
    if doc.get("schema") != SCHEMA:
        bad.append("SCHEMA record schema %r" % doc.get("schema"))
    for k in scope_of(doc, "asks"):
        a = (doc.get("asks") or {}).get(k)
        if not a or a.get("text") != ASKS.get(k) or a.get("sha256") != sha_text(ASKS.get(k, "")):
            bad.append("ASK_SHA ask %s text/sha in the record is not the ask this builder sends" % k)
    bad += scope_faults(doc)
    ids = {r["id"] for r in table}
    ev = {r["id"]: r["evidence"] for r in table}
    rows = doc.get("rows") or []
    have = {}
    for r in rows:
        key = (r.get("scene"), r.get("ask_id"))
        if key in have:
            bad.append("DUPLICATE row %s appears twice (a paid row must be replaced, never appended)" % (key,))
        have[key] = r
        sc, ak = key
        if sc not in SCENES:
            bad.append("SCENE row %s is not one of the three cards this item names" % (sc,))
        if ak not in ASKS:
            bad.append("ASK_ID row %s/%s is not a registered ask %s" % (sc, ak, sorted(ASKS)))
        if ak not in scope_of(doc, "asks"):
            bad.append("ASK_ROW_UNDECLARED row %s/%s: the record declares asks %s, this row is ask %r - "
                       "an unasked caption in a record is an unasked word"
                       % (sc, ak, scope_of(doc, "asks"), ak))
        if r.get("model_id") not in ids:
            bad.append("MODEL_NOT_VISION %s is not in the llama-swap vision set (never assume vision)" % r.get("model_id"))
        elif not UNCENSORED_RE.search(ev.get(r.get("model_id"), "")):
            bad.append("MODEL_NOT_UNCENSORED %s served file carries no Uncensored/abliterated - the item "
                       "asked for the uncensored vision model" % r.get("model_id"))
        if int(r.get("guard_rc", 9)) != 0:
            bad.append("GUARD_NOT_IDLE %s/%s guard_rc=%s (gpu_guard must be IDLE in front of every request)"
                       % (sc, ak, r.get("guard_rc")))
        if r.get("image_sha256") != sha_file(still_path(sc)):
            bad.append("SHA_DRIFT %s row sha %s != the start still on disk now %s"
                       % (sc, str(r.get("image_sha256"))[:12], sha_file(still_path(sc))[:12]))
        if r.get("comfy_copy_sha_match") is not True:
            bad.append("COPY_SHA the graph-loaded copy under ComfyUI/input is not byte-identical for %s" % sc)
        if not r.get("image_dims"):
            bad.append("NO_DIMS %s/%s records no dimensions" % (sc, ak))
        if not str(r.get("endpoint", "")).startswith("http://127.0.0.1"):
            bad.append("OFF_LOOPBACK endpoint %r is not loopback" % r.get("endpoint"))
        if (r.get("request_options") or {}).get("reasoning_effort") != "none":
            bad.append("NO_THINKING %s/%s has no reasoning_effort=none - L21: a thinking model puts the "
                       "caption in reasoning_content and the card ends up empty" % (sc, ak))
        if int(r.get("max_tokens", 0)) < 1000:
            bad.append("MAX_TOKENS %s/%s max_tokens=%s sits at the 300-token level that truncated the "
                       "04:34 cards" % (sc, ak, r.get("max_tokens")))
        if str(r.get("ask_sha256")) != sha_text(ASKS.get(ak, "")):
            bad.append("ASK_DRIFT %s/%s was asked a different text than the recorded ask %s" % (sc, ak, ak))
        if int(r.get("http_status", 0)) != 200:
            bad.append("HTTP %s/%s status=%s error=%s" % (sc, ak, r.get("http_status"), str(r.get("error"))[:120]))
            continue
        cap = r.get("caption") or ""
        if not cap.strip():
            if int(r.get("reasoning_words", 0)) > 0:
                bad.append("CONTENT_IN_REASONING %s/%s content is empty and %d reasoning words came back "
                           "(L21 exactly)" % (sc, ak, r.get("reasoning_words")))
            else:
                bad.append("EMPTY_CONTENT %s/%s returned no text" % (sc, ak))
        if len(cap.split()) < MIN_WORDS:
            bad.append("CAPTION_SHORT %s/%s %d words < %d - this is what REFUSAL_TRUNCATED looks like"
                       % (sc, ak, len(cap.split()), MIN_WORDS))
        if r.get("decline_markers"):
            bad.append("DECLINE %s/%s carries %s - the caption is not a record of the frame"
                       % (sc, ak, r.get("decline_markers")))
        if str(r.get("status", "")).upper().startswith("REFUSAL"):
            bad.append("STILL_REFUSING %s row status %s" % (sc, r.get("status")))
        raw = r.get("raw_path") or ""
        if not raw or not os.path.isfile(raw):
            bad.append("RAW_MISSING %s/%s raw caption file %r is not on disk" % (sc, ak, raw))
        elif sha_file(raw) != r.get("raw_sha256") or sha_text(cap) != sha_file(raw):
            bad.append("RAW_SHA_DRIFT %s/%s the raw file bytes do not match the caption in the record" % (sc, ak))
        for p in (r.get("image_path"), raw):
            if p and re.search(r"output|\.mp4|contact|frame", str(p), re.I):
                bad.append("RENDERED_CITED %s names %r - a card reads a START STILL only" % (sc, p))
    for sc in args_scenes(doc):
        for ak in scope_of(doc, "asks"):
            if (sc, ak) not in have:
                bad.append("ROW_MISSING no row for %s/%s (the record's scope is %s x %s)"
                           % (sc, ak, args_scenes(doc), scope_of(doc, "asks")))
    for key in have:
        if key[0] not in args_scenes(doc):
            bad.append("ROW_OUT_OF_SCOPE row %s names a scene outside the record's scope %s - a row for a "
                       "scene this record never asked about is not evidence for these cards"
                       % (list(key), args_scenes(doc)))
    if doc.get("gates"):
        for g in doc["gates"]:
            if int(g.get("gpu_guard_rc", 9)) != 0:
                bad.append("GATE_RED a recorded gpu_guard gate reads rc=%s" % g.get("gpu_guard_rc"))
    if _judge_keys(doc):
        bad.append("JUDGE_KEY the record carries a judgement key (%s) - no score/rank/keep, KEEP is Derrick's"
                   % ", ".join(sorted(_judge_keys(doc))[:6]))
    if "start still" not in str(doc.get("role", "")).lower():
        bad.append("ROLE the record does not state the start-still-only scope")
    return bad


def _judge_keys(node, path=""):
    hits = set()
    if isinstance(node, dict):
        for k, v in node.items():
            if str(k).lower() in BANNED:
                hits.add(str(k))
            hits |= _judge_keys(v, path + "/" + str(k))
    elif isinstance(node, list):
        for v in node:
            hits |= _judge_keys(v, path)
    return hits


def scope_of(doc, key):
    """What a record declares it covers: {"scenes": [...], "asks": [...]}. The 2025 record carries no scope, so
    it is judged against three scenes x asks A,B - its own contract, byte-for-byte unchanged. A record that
    declares a scope is judged against that scope: 2 scenes x 3 asks is not 3 scenes x 3 asks, and
    ROW_MISSING on a row nobody asked for is a phantom. A name outside the registry is SCOPE_RANGE, so a
    scope can never hide a scene or an ask that does not exist."""
    sc = doc.get("scope") or {}
    if key == "scenes":
        return list(sc.get("scenes") or SCENES)
    return list(sc.get("asks") or ctx(doc.get("tag", ""))["asks"])


def scope_faults(doc):
    bad = []
    sc = doc.get("scope")
    if sc is None:
        return bad
    for key, valid in (("scenes", SCENES), ("asks", ASKS)):
        for v in (sc.get(key) or []):
            if v not in valid:
                bad.append("SCOPE_RANGE scope.%s names %r, outside %s" % (key, v, list(valid)))
    for key in sc:
        if key not in ("scenes", "asks"):
            bad.append("SCOPE_KEY scope carries %r; a scope names scenes and asks only" % key)
    if not (sc.get("scenes") and sc.get("asks")):
        bad.append("SCOPE_INCOMPLETE scope %r: a record states the scenes and the asks it covers, or "
                   "carries no scope at all (the 2025 shape)" % (sc,))
    declared = sorted(doc.get("asks") or {})
    want = sorted(scope_of(doc, "asks"))
    if declared and declared != want:
        bad.append("ASKS_SCOPE the record declares asks %s and carries text for %s: a declared ask with no "
                   "text is unaskable, text for an undeclared ask is an unasked word" % (want, declared))
    return bad


def args_scenes(doc):
    return scope_of(doc, "scenes")


def caption_of(doc, scene, ask_id):
    for r in doc["rows"]:
        if r.get("scene") == scene and r.get("ask_id") == ask_id and (r.get("caption") or "").strip():
            return r
    return None


def build_scene(scene, doc):
    """Rebuild a card + facts in memory from the record and the spec (no writes), so --cards, --check and
    --selftest all judge one composition."""
    spec_dir = ctx(doc.get("tag", ""))["spec_dir"]
    with open(os.path.join(spec_dir, scene + ".json"), "r", encoding="utf-8") as fh:
        spec = json.load(fh)
    caps = [(ak, caption_of(doc, scene, ak)["caption"]) for ak in scope_of(doc, "asks")]
    card_text, ev, unresolved = compose_card(scene, spec, doc, caps)
    return card_text, compose_facts(scene, spec, doc, card_text, ev, unresolved)


def disk_card_faults(doc):
    """Judge the cards that are ON DISK by the gate's own rules. Once the caption record is clean, a card
    that is not on disk is a fault: the item IS the cards."""
    bad = []
    mark = ctx(doc.get("tag", "")).get("mark", "top_card_vl")
    for scene in args_scenes(doc):
        card_p = os.path.join(CARD_DIR, scene + ".md")
        facts_p = os.path.join(CARD_DIR, scene + ".facts.json")
        if not (os.path.isfile(card_p) and os.path.isfile(facts_p)):
            bad.append("CARD_NOT_WRITTEN %s card=%s facts=%s" % (scene, os.path.isfile(card_p), os.path.isfile(facts_p)))
            continue
        with open(facts_p, "r", encoding="utf-8") as fh:
            facts = json.load(fh)
        with open(card_p, "r", encoding="utf-8") as fh:
            text = fh.read()
        if "uncensored vision model" not in text:
            bad.append("CARD_NOT_VL %s the card does not name the uncensored vision model it came from" % scene)
        if not re.search(r"[A-Za-z]:[^\s,]+\.gguf", text):
            bad.append("CARD_NO_MODEL_FILE %s the card names no served .gguf, so it cannot prove which model "
                       "wrote the caption" % scene)
        if mark not in text:
            bad.append("CARD_NO_RECORD %s the card does not cite the caption record it came from (mark %r)"
                       % (scene, mark))
        bad += card_faults(facts, text)
    return bad


def do_check(args):
    table = vp.vision_table()
    doc = load_doc(args.tag)
    if not doc:
        print(f"RED no record at {ctx(args.tag)['record']} (run --run --tag {args.tag})")
        return 2
    rc, text = vp.guard_rc()
    rows = doc.get("rows") or []
    caps = sum(1 for r in rows if r.get("http_status") == 200 and (r.get("caption") or "").strip())
    declines = sum(1 for r in rows if r.get("decline_markers"))
    bad = doc_faults(doc, table) + disk_card_faults(doc)
    print(f"gpu_guard rc={rc} {text!r} (read at check time; every request row also carries its own)")
    print(f"tag={args.tag!r} record={ctx(args.tag)['record']} scope={scope_of(doc, 'scenes')}x{scope_of(doc, 'asks')} "
          f"model={MODEL_DEFAULT} vision_ids_in_the_serving_config={len(table)} "
          f"rows={len(rows)} captions={caps}/{len(args_scenes(doc)) * len(scope_of(doc, 'asks'))} "
          f"declines={declines} "
          f"words={sorted(len((r.get('caption') or '').split()) for r in rows)}")
    print(f"integrity_faults={len(bad)}")
    for b in bad:
        print("  FAULT " + b)
    print("VERDICT TOP_CARD_VL CLEAN" if not bad else "VERDICT TOP_CARD_VL RED")
    return 0 if not bad else 2


# ------------------------------------------------------------------ --selftest

def set0(d, key, val):
    """Mutate the first row of a record copy. Seeds a fault in the row the detectors read."""
    d["rows"][0][key] = val


def strip_uncensored(table):
    """Seed the serving config, not the record: the same model id served from a file whose name carries
    no Uncensored/abliterated marker. This is the only way to prove MODEL_NOT_UNCENSORED can fire -
    both vision models on this box really are uncensored by filename, so no row mutation can do it."""
    out = copy.deepcopy(table)
    for r in out:
        r["evidence"] = re.sub(UNCENSORED_RE, "stock", r["evidence"])
    return out


TABLE_SEEDS = {"model_not_uncensored": strip_uncensored}

SEEDS = {
    "model_not_vision": lambda d: set0(d, "model_id", "no_such_vision_model"),
    "guard_not_idle": lambda d: set0(d, "guard_rc", 7),
    "no_thinking_off": lambda d: set0(d, "request_options", {}),
    "max_tokens_at_the_old_level": lambda d: set0(d, "max_tokens", 300),
    "ask_drift": lambda d: set0(d, "ask_sha256", "0" * 64),
    "empty_content_reasoning": lambda d: [set0(d, "caption", ""), set0(d, "reasoning_words", 512)][0],
    "caption_short": lambda d: set0(d, "caption", "Two figures. A room."),
    "decline_present": lambda d: set0(d, "decline_markers", ["i can't"]),
    "sha_drift": lambda d: set0(d, "image_sha256", "0" * 64),
    "copy_sha_false": lambda d: set0(d, "comfy_copy_sha_match", False),
    "no_dims": lambda d: set0(d, "image_dims", []),
    "off_loopback": lambda d: set0(d, "endpoint", "https://example.test/v1/chat/completions"),
    "http_error": lambda d: set0(d, "http_status", 502),
    "raw_missing": lambda d: set0(d, "raw_path", os.path.join(RAW_DIR, "nope.txt")),
    "raw_sha_drift": lambda d: set0(d, "raw_sha256", "0" * 64),
    "rendered_path_cited": lambda d: set0(d, "raw_path", "C:/AI/community/runs/ali163/x.mp4"),
    "row_missing": lambda d: d.__setitem__("rows", d["rows"][:1]),
    "duplicate_row": lambda d: d.__setitem__("rows", d["rows"] + [copy.deepcopy(d["rows"][0])]),
    "judge_key": lambda d: d["rows"][0].__setitem__("score", 9),
    "schema": lambda d: d.__setitem__("schema", "other"),
    "ask_text_edited": lambda d: d["asks"]["A"].__setitem__("text", "changed"),
    "role_missing": lambda d: d.__setitem__("role", "objective record only."),
    "gate_red": lambda d: d.__setitem__("gates", [{"gpu_guard_rc": 7}]),
}


def seed_model_row(f, t, s):
    return f, t.replace(f["model"], "stock")


def seed_caption_status(f, t, s):
    return f, t.replace("CAPTIONED", "UNKNOWN")


def seed_sha_row(f, t, s):
    return f, t.replace(f["sha256"], "0" * 64)


def seed_scope(f, t, s):
    return f, t.replace("start still", "frame")


def seed_quote(f, t, s):
    return f, t.replace(f["gate"]["evidence"][f["gate"]["room_required"][0]][:24], "XX invented quote XX")


def seed_required_no_evidence(f, t, s):
    f["gate"]["evidence"].pop(f["gate"]["room_required"][0])
    return f, t


def seed_figure_count_row(f, t, s):
    return f, t.replace(f"figures: {f['gate']['figure_count']}", "figures: 9")


def seed_head_map(f, t, s):
    f["gate"]["head_in_frame"] = {k: not v for k, v in f["gate"]["head_in_frame"].items()}
    return f, t


def seed_consent(f, t, s):
    f["gate"]["consent_gate"] = {"ban": ["eager"]}
    return f, t


def seed_unresolved(f, t, s):
    f["_unresolved"] = ["purple hair"]
    return f, t


def seed_gate_key(f, t, s):
    f["gate"].pop("solo_phrases")
    return f, t


def seed_fig_key(f, t, s):
    f["figures"][0].pop("not_visible")
    return f, t


def seed_image_path(f, t, s):
    f["image"] = "C:/nope/GI.jpg"
    return f, t


def seed_top_key(f, t, s):
    f.pop("camera")
    return f, t


def seed_prompt_delta(f, t, s):
    f.pop("prompt_delta")
    return f, t


CARD_SEEDS = {
    "model_row_removed": seed_model_row,
    "caption_status_removed": seed_caption_status,
    "sha_row_removed": seed_sha_row,
    "scope_removed": seed_scope,
    "quote_not_verbatim": seed_quote,
    "required_token_no_evidence": seed_required_no_evidence,
    "figure_count_row_mismatch": seed_figure_count_row,
    "head_map_disagrees": seed_head_map,
    "consent_ban_no_require": seed_consent,
    "unresolved_token": seed_unresolved,
    "prompt_delta_removed": seed_prompt_delta,
    "missing_gate_key": seed_gate_key,
    "missing_fig_key": seed_fig_key,
    "image_path_missing": seed_image_path,
    "top_key_missing": seed_top_key,
}


def do_selftest(args):
    table = vp.vision_table()
    doc = load_doc()
    if not doc:
        print(f"RED no record at {OUT}; --selftest seeds the real record")
        return 2
    base = doc_faults(doc, table)
    print(f"real artifact: faults={len(base)} (must be 0) {[b[:70] for b in base][:3]}")
    fired, silent = [], []
    for name, mut in SEEDS.items():
        d = copy.deepcopy(doc)
        try:
            mut(d)
        except Exception as exc:
            print(f"  seed {name} could not be applied: {exc!r}")
            silent.append(name)
            continue
        f = doc_faults(d, table)
        if not f:
            silent.append(name)
        fired.append(name)
        print(f"  seed {name:26s} faults={len(f)} first={f[0][:78] if f else 'NONE - SILENT FAULT'}")
    print(f"seeds: {len(SEEDS)} fired: {len(fired)} silent: {len(silent)} {silent}")
    tfired, tsilent = [], []
    for name, mut in TABLE_SEEDS.items():
        f = doc_faults(copy.deepcopy(doc), mut(copy.deepcopy(table)))
        hit = [x for x in f if x.startswith("MODEL_NOT_UNCENSORED")]
        if not hit:
            tsilent.append(name)
        tfired.append(name)
        print(f"  seed {name:26s} faults={len(f)} first={hit[0][:78] if hit else 'NONE - SILENT FAULT'}")
    print(f"table seeds: {len(TABLE_SEEDS)} fired: {len(tfired)} silent: {len(tsilent)} {tsilent}")
    csilent, cbase = [], []
    for scene in SCENES:
        spec_p = os.path.join(SPEC_DIR, scene + ".json")
        if not os.path.isfile(spec_p):
            print(f"  card seeds {scene}: no spec at {SPEC_DIR} - the card side is untested")
            csilent.append(scene + "/no-spec")
            continue
        with open(spec_p, "r", encoding="utf-8") as fh:
            spec = json.load(fh)
        text, facts = build_scene(scene, doc)
        real = card_faults(facts, text)
        cbase += real
        print(f"  real card {scene}: faults={len(real)} first={real[0][:70] if real else 'CLEAN'}")
        for name, mut in CARD_SEEDS.items():
            f2, t2 = copy.deepcopy(facts), text
            try:
                f2, t2 = mut(f2, t2, spec)
            except Exception as exc:
                print(f"  card seed {scene}/{name} could not be applied: {exc!r}")
                csilent.append(scene + "/" + name)
                continue
            got = card_faults(f2, t2)
            if not got:
                csilent.append(scene + "/" + name)
            print(f"  card seed {scene}/{name:26s} faults={len(got)} "
                  f"first={got[0][:66] if got else 'NONE - SILENT FAULT'}")
    print(f"card seeds: {len(CARD_SEEDS)} per scene; real-card faults={len(cbase)} "
          f"silent={len(csilent)} {csilent[:6]}")
    ok = len(base) == 0 and len(silent) == 0 and len(tsilent) == 0 and len(cbase) == 0 and len(csilent) == 0
    print("VERDICT SELFTEST_CLEAN" if ok else "VERDICT SELFTEST RED")
    return 0 if ok else 2


# ------------------------------------------------------------------ --cards: the card is generated, never typed

def find_quote(caps, token):
    """The verbatim caption line that supports a token. caps = [(ask_id, text)]. None = the card cannot
    support that fact, so it must never enter a card, a gate, or a prompt (L18: the card is data)."""
    t = card_norm(token)
    if not t:
        return None
    for ak, text in caps:
        for line in text.splitlines():
            if t in card_norm(line):
                line = line.strip().lstrip("-").strip()
                return f"ask {ak}: {line}"
    return None


def collect_quotes(caps, tokens):
    """token -> verbatim quote, plus the list of tokens no caption supports (never silently kept)."""
    ev, unresolved = {}, []
    for tok in tokens:
        q = find_quote(caps, tok)
        if q:
            ev[tok] = q
        else:
            unresolved.append(tok)
    return ev, unresolved


def model_files(doc, model_id):
    """The served .gguf paths and aliases of a model id, read out of the vision table stored in the record
    (the row itself carries only the id). An empty list means the record cannot prove which file is served."""
    rows = (doc.get("model_evidence") or {}).get("table") or []
    ev = " ".join(r.get("evidence", "") for r in rows if r.get("id") == model_id)
    files = re.findall(r"[A-Za-z]:[^\s,]+\.gguf", ev.replace(chr(92), "/"))
    aliases = next((r.get("aliases", []) for r in rows if r.get("id") == model_id), [])
    return files, aliases, ev


def resolve_describe(caps, value):
    """A descriptive row (species/build/skin/hair/wardrobe/pose/position) is a summary, so it is not a caption
    token. Build candidate phrases (the whole value with the 'ask B adds' annotations removed first, then its
    comma and parenthetical parts, where an annotation may cite any registered ask (ask A, B, C...)) and
    quote the longest candidate a caption states verbatim. No candidate
    supported -> the row is unresolvable and must not be in the card."""
    base = re.sub(r"\s*\((?:ask [A-Z] adds[^)]*)\)", "", value)
    base = re.sub(r"\s*;\s*ask [A-Z] adds.*$", "", base, flags=re.S)
    cands = [base]
    cands += [p.strip(" .,") for p in re.split(r",", base)]
    cands += [p.strip(" .,") for p in re.sub(r"\([^)]*\)", " ", base).split()]
    cands = [c for c in cands if len(c.split()) >= 2] or [base.strip(" .,")]
    for c in sorted(set(cands), key=lambda s: (-len(s.split()), -len(s))):
        q = find_quote(caps, c)
        if q:
            return c, q
    return None


def q(ev, tok):
    """A token's quote, or the honest marker. A KeyError here would kill the run before the faults print."""
    return ev.get(tok, "UNRESOLVED")


def compose_card(scene, spec, doc, caps):
    row = caption_of(doc, scene, "A")
    sha = row["image_sha256"]
    L = []
    add = L.append
    add(f"# {scene} - {spec['card_title']} (start-still card, uncensored vision model)")
    add("")
    add(f"scene: {scene} {spec['card_title']}")
    add(f"start_still: {still_path(scene).replace(chr(92), '/')}")
    add(f"start_still_bytes: {os.path.getsize(still_path(scene))}")
    add(f"start_still_sha256: {sha}")
    add(f"start_still_mtime: {mtime_iso(still_path(scene))}")
    add(f"comfy_input_copy: {comfy_copy(scene).replace(chr(92), '/')} (byte-identical, the path the graph loads)")
    add(f"image_dims: {row['image_dims']}")
    files, aliases, ev = model_files(doc, row["model_id"])
    add(f"vision_model: {row['model_id']} = " + " + ".join(f.replace(chr(92), "/") for f in files))
    add(f"model_evidence: read off C:/AI/director/config/llama-swap.yaml by ali163_vision_probe.vision_table "
        f"(see the record); the served file name carries 'Uncensored' - this is the uncensored vision model "
        f"Derrick asked for; aliases {','.join(aliases)}; evidence: {ev[:220]}")
    add("request_options: reasoning_effort=none + chat_template_kwargs.enable_thinking=false + max_tokens="
        f"{row['max_tokens']} (L21/3.17: without these the caption lands in reasoning_content, not content)")
    add(f"gpu_guard: IDLE rc=0 in front of every request (this row's guard_rc={row['guard_rc']})")
    add("read_scope: the start still ONLY. No rendered clip, no frame of a render, no contact sheet.")
    add("role: an objective record of the start still in the words of the uncensored vision model. No score, "
        "no rank, no keep, no judgement - KEEP is Derrick's alone.")
    add("asks: " + " / ".join(f"{k} sha256 {(doc.get('asks') or {}).get(k, {}).get('sha256', 'NONE')}"
                              for k in scope_of(doc, "asks")))
    for k in scope_of(doc, "asks"):
        add(f"ask_{k}_provenance: {((doc.get('asks') or {}).get(k) or {}).get('provenance', 'UNDECLARED')}")
    add(f"command: {row['command']}")
    rec = ctx(doc.get("tag", ""))["record"].replace(chr(92), "/")
    add(f"record: {rec}")
    add("caption_status: CAPTIONED")
    add(f"figures: {len(spec['figures'])}")
    add(f"age_rule: {AGE_MIN}+ (canon fiction-cond-lock v2.3.0), stated as a row, never inferred from a face")
    add(f"naming_source: {spec['naming_source']}")
    add(spec.get("supersedes",
        f"supersedes: notes/scenes/{scene}.md of 2026-10-25 04:34-04:38 CT (caption_status REFUSAL_TRUNCATED, "
        "coding_swift15_iq3s). Git history is the backup; no .bak."))
    add("")
    add("## facts read out of the model's own words (each cited verbatim below)")
    tok_fig = []
    for i, f in enumerate(spec["figures"], 1):
        for key in ("species", "build", "skin", "hair", "wardrobe", "pose", "position"):
            if f.get(key):
                tok_fig.append((i, key, f[key]))
    need = [f"Figure {i}" for i in range(1, len(spec["figures"]) + 1)]
    need += spec["room"] + spec.get("props", []) + spec["light"]
    need += [t for f in spec["figures"] for t in f["visible"]]
    need += [t for v in spec["open_beat"].values() for t in v]
    ev, unresolved = collect_quotes(caps, need)
    add(f"figures: {len(spec['figures'])}  <- " + " | ".join(
        '"' + ev.get("Figure %d" % i, "UNRESOLVED") + '"' for i in range(1, len(spec["figures"]) + 1)))
    for i, key, t in tok_fig:
        got = resolve_describe(caps, t)
        if not got:
            unresolved.append(f"{key}[{i}]={t}")
            add(f"{key}[{i}]: {t}  <- UNRESOLVED (no caption states any phrase of it)")
            continue
        frag, quote = got
        add(f"{key}[{i}]: {t}  <- \"{quote}\"")
    for i, f in enumerate(spec["figures"], 1):
        add(f"head_in_frame[{i}]: {str(bool(f['head_in_frame'])).lower()}  <- "
            + ('"%s"' % q(ev, f["visible"][0]) if f["visible"] else "(frame edge)")
            + (f" | \"{find_quote(caps, 'out of frame')}\"" if not f["head_in_frame"] else ""))
        add(f"not_visible[{i}]: " + ", ".join(f["not_visible"]))
        add(f"prompt_tokens[{i}] (the appearance words a prompt must carry for this figure): "
            + "; ".join(f["visible"]) + "  <- " + " | ".join('"%s"' % q(ev, t) for t in f["visible"]))
        add(f"open_beat[{i}] (the pose the clip opens in): " + "; ".join(spec["open_beat"].get(str(i), []))
            + "  <- " + " | ".join('"%s"' % q(ev, t) for t in spec["open_beat"].get(str(i), [])))
    add("room: " + "; ".join(spec["room"]) + "  <- " + " | ".join('"%s"' % q(ev, t) for t in spec["room"]))
    if spec.get("props"):
        add("props: " + "; ".join(spec["props"]) + "  <- "
            + " | ".join('"%s"' % q(ev, t) for t in spec["props"]))
    add("light: " + "; ".join(spec["light"]) + "  <- " + " | ".join('"%s"' % q(ev, t) for t in spec["light"]))
    add("camera: " + "; ".join(spec["camera"]))
    add(f"audit: {AUDIT}")
    add(f"age_marker: canon declaration (the card carries the age floor as a row, never as an inference)")
    add("age_evidence: " + AGE_EVIDENCE)
    if spec.get("card_extra"):
        add(spec["card_extra"])
    for ak, cap_text in caps:
        add("")
        add(CAPTION_HEAD.get(ak, f"## caption {ak} verbatim"))
        add("")
        add(cap_text)
    text = "\n".join(L).rstrip() + "\n"
    return text, ev, unresolved


def compose_facts(scene, spec, doc, card_text, ev, unresolved):
    row = caption_of(doc, scene, "A")
    figs = []
    for i, f in enumerate(spec["figures"], 1):
        figs.append({"label": str(i), "kind": f["kind"], "noun": f["noun"], "pose": f["pose"],
                     "head_in_frame": bool(f["head_in_frame"]), "visible": f["visible"],
                     "not_visible": f["not_visible"]})
    ev = dict(ev)
    canon = lambda xs: sorted(set(str(x) for x in xs))
    spec = dict(spec)
    spec["banned"] = {k: canon(v) for k, v in spec["banned"].items()}
    for k in ("room_banned", "light_banned", "solo_phrases"):
        spec[k] = canon(spec.get(k, []))
    spec["open_beat_ban"] = {k: canon(v) for k, v in spec.get("open_beat_ban", {}).items()}
    ev["age_marker"] = AGE_EVIDENCE
    gate = {
        "figure_count": len(figs),
        "aliases": spec["aliases"],
        "per_chunk_tokens": canon(spec.get("core_tokens", [])),
        "banned": spec["banned"],
        "head_in_frame": {str(i): figs[i - 1]["head_in_frame"] for i in range(1, len(figs) + 1)},
        "head_allow": spec["head_allow"],
        "open_beat": spec["open_beat"],
        "open_beat_ban": spec["open_beat_ban"],
        "room_required": spec["room"] + spec.get("props", []),
        "room_banned": spec["room_banned"],
        "light_required": spec["light"],
        # the shipped gate reads a card's light bans under `light_bans` (scene_card_gate.py:246,333) and a
        # CARD-VL facts file names them `light_banned`, so on 2026-10-26 the shipped gate read 0 light bans
        # off these cards and selfconflicts scored them 0. The rebuilt card carries both keys, so its light
        # bans are enforced and its self-conflict census can see them: the card must be self-consistent.
        "light_bans": spec["light_banned"],
        "age_marker": "canon declaration",
        "age_required": AGE_REQUIRED,
        "consent_gate": spec["consent_gate"],
        "solo_phrases": spec["solo_phrases"],
        "evidence": ev,
    }
    facts = {
        "scene": scene, "card": (CARD_DIR + "/" + scene + ".md"),
        "audit": AUDIT,
        "caption": caption_of(doc, scene, "A")["raw_path"],
        "caption2": caption_of(doc, scene, "B")["raw_path"],
        "captions_all": {ak: caption_of(doc, scene, ak)["raw_path"] for ak in scope_of(doc, "asks")}
        if all(caption_of(doc, scene, ak) for ak in scope_of(doc, "asks")) else {},
        "sha256_row": "start_still_sha256: " + caption_of(doc, scene, "A")["image_sha256"],
        "age_min": AGE_MIN,
        "_age_min_source": AGE_SOURCE,
        "_schema": FACTS_SCHEMA,
        "_what": ("The " + scene + " start-image CARD as data, re-read by the uncensored vision model: what the "
                  "picture settled, in the model's own words. Card " + CARD_DIR + "/" + scene + ".md, captions "
                  + OUT + " rows " + scene + "/A + " + scene + "/B (raw " + RAW_DIR + "/" + scene + "_vl_A.txt, "
                  + "_vl_B.txt), audit " + AUDIT + ". Item CARD-VL, Derrick 2026-10-25 6:48 PM CT: 'Redo the orc, "
                  "robot and GI072 scene cards with the uncensored vision model'. A prompt writer and the build "
                  "gate read THIS file: gate.per_chunk_tokens are the words a chunk must carry, gate.banned are "
                  "words the picture does not support, gate.room_banned and gate.light_banned are words the "
                  "shipped prose invented that no caption states. "
                  "notes/hc15_anchor_carry_build.py --top-check enforces it (ck_top_card, ck_top_facts)."),
        "_caption_paths": "facts.caption = the ask A raw file, facts.caption2 = the ask B raw file; both "
                          "captions are also printed verbatim in the card under '## caption A verbatim' and "
                          "'## caption B verbatim'",
        "image": row["image_path"], "sha256": row["image_sha256"],
        "model": row["model_id"], "status": "CAPTIONED",
        "figures": figs,
        "room": "; ".join(spec["room"]), "light": "; ".join(spec["light"]),
        "camera": "; ".join(spec["camera"]), "gate": gate,
        "_source": f"{ctx(doc.get('tag', ''))['record'].replace(chr(92), '/')} rows "
                   + " + ".join(f"{scene}/{ak}" for ak in scope_of(doc, "asks"))
                   + ", captioned by the uncensored vision model on the start still",
        "_scope": "the start still only; no rendered clip, no frame of a render, no contact sheet",
        "_card_quotes": "every fact row and every gate token cites a verbatim caption quote in gate.evidence; "
                        "a token with no quote is not_resolvable and is listed in _unresolved, never in a gate",
        "_unresolved": unresolved,
        "_age": AGE_SOURCE,
    }
    for k, v in spec.get("facts_extra", {}).items():
        facts[k] = v
    # the measured gap between the shipped prompts and this card, for the prompt-rewrite rows. The numbers come
    # from a real --top-check capture (notes/top_card_vl_topcheck_20261025.txt), not from a guess.
    facts["prompt_delta"] = (dict(spec["prompt_delta"],
                                  measured_by="python C:/AI/community/notes/hc15_anchor_carry_build.py "
                                              "--top-check, captured in notes/top_card_vl_topcheck_20261025.txt",
                                  as_of=now())
                             if spec.get("prompt_delta") else
                             {"measured_facts": [],
                              "unresolved": "the spec carries no prompt_delta block, so the gap to the "
                                            "shipped prompts is unmeasured"})
    for i, f in enumerate(spec["figures"], 1):
        facts.setdefault("species", {})[str(i)] = f["species"]
    return facts


def card_faults(facts, card_text):
    """The gate's own card rules (hc15_anchor_carry_build.py ck_top_card / ck_top_facts), re-run here so a
    bad card fails in this builder, not 40 minutes later in a gate run."""
    bad = []
    for k in CARD_TOP_KEYS:
        if k not in facts:
            bad.append("CARD_MISSING_KEY %s %s" % (facts.get("scene"), k))
    for k in CARD_GATE_KEYS:
        if k not in facts.get("gate", {}):
            bad.append("CARD_MISSING_GATE_KEY %s gate.%s" % (facts.get("scene"), k))
    for f in facts.get("figures", []):
        for k in CARD_FIG_KEYS:
            if k not in f:
                bad.append("CARD_MISSING_FIG_KEY %s fig %s %s" % (facts.get("scene"), f.get("label"), k))
    if str(facts.get("model", "")) not in card_text:
        bad.append("CARD_MODEL %s model row missing" % facts.get("scene"))
    if str(facts.get("status", "")) not in card_text:
        bad.append("CARD_CAPTION %s caption status row missing" % facts.get("scene"))
    if str(facts.get("sha256", "")) not in card_text:
        bad.append("CARD_SHA %s sha row missing" % facts.get("scene"))
    if "start still" not in card_text.lower():
        bad.append("CARD_SCOPE %s no start-still-only scope line" % facts.get("scene"))
    ev = facts.get("gate", {}).get("evidence", {})
    if not ev:
        bad.append("CARD_EVIDENCE %s no evidence map" % facts.get("scene"))
    for tok, q in sorted(ev.items()):
        if not q or card_norm(q) not in card_norm(card_text):
            bad.append("CARD_EVIDENCE %s token %r quote is not verbatim in the card" % (facts.get("scene"), tok))
    gt = facts.get("gate", {})
    pcts = gt.get("per_chunk_tokens", [])
    flat = [t for v in pcts.values() for t in v] if isinstance(pcts, dict) else list(pcts)
    need = ([(t, "room_required") for t in gt.get("room_required", [])] +
            [(t, "light_required") for t in gt.get("light_required", [])] +
            [(t, "per_chunk_tokens") for t in flat] +
            [(t, "figure %d visible" % i) for i, f in enumerate(facts.get("figures", []), 1)
             for t in f.get("visible", [])])
    for tok, src in need:
        if tok not in ev:
            bad.append("CARD_REQUIRED_NO_EVIDENCE %s %s lacks evidence for %r" % (facts.get("scene"), src, tok))
    if ("figures: %d" % facts.get("gate", {}).get("figure_count", -1)) not in card_text:
        bad.append("CARD_COUNT %s figures row != gate.figure_count" % facts.get("scene"))
    for p in (facts.get("image"), facts.get("card")):
        if not os.path.isfile(str(p)):
            bad.append("CARD_PATH %s names %s, not on disk" % (facts.get("scene"), p))
    if facts.get("gate", {}).get("head_in_frame") != {str(i + 1): f["head_in_frame"] for i, f in enumerate(facts.get("figures", []))}:
        bad.append("CARD_HEAD %s the head_in_frame map and the figure rows disagree" % facts.get("scene"))
    cg = facts.get("gate", {}).get("consent_gate", {})
    if cg.get("ban") and not cg.get("require"):
        bad.append("CARD_CONSENT %s consent_gate bans words and gives no required phrasing" % facts.get("scene"))
    if facts.get("_unresolved"):
        bad.append("CARD_UNRESOLVED %s tokens no caption supports: %s" % (facts.get("scene"), facts["_unresolved"]))
    if not facts.get("prompt_delta", {}).get("measured_facts"):
        bad.append("CARD_PROMPT_DELTA %s carries no measured gap to the shipped prompts" % facts.get("scene"))
    # a ban of a fact a CAPTION states is a self-contradiction: the prompt would be forbidden to say what
    # the start still shows. Scoped to the two verbatim caption sections, never to this card's own prose
    # (naming_source and the conflict notes quote banned words on purpose). Scene-wide ban lists only: a
    # per-figure ban on a word another figure wears is not a contradiction. Word-boundary match, the same
    # test the gate runs on room_banned (ck_top_card room_hits): a substring match would read "he" in "the".
    caps_only = card_text.split("## caption A verbatim")[-1]
    caps_norm = card_norm(caps_only)
    for tok in facts.get("gate", {}).get("banned", {}).get("any", []) \
            + facts.get("gate", {}).get("room_banned", []) + facts.get("gate", {}).get("light_banned", []):
        pat = r"(?<![a-z])" + re.escape(card_norm(tok)) + r"(?![a-z])"
        if re.search(pat, caps_norm):
            bad.append("CARD_BAN_SUPPORTED %s bans %r, a fact a caption states - the prompt would be "
                       "forbidden to say what the start still shows" % (facts.get("scene"), tok))
    return bad


def old_gate_tokens(scene):
    """Every appearance token the SHIPPED gate asked for. Read from git HEAD (AGENTS.md: the git repo is the
    backup), so the measurement survives re-runs: after the first --cards the on-disk facts.json is the new
    one. Falls back to the file on disk when git has no such path (a scene with no prior facts.json)."""
    rel = "notes/scenes/%s.facts.json" % scene
    try:
        import subprocess
        p = subprocess.run(["git", "-C", "C:/AI/community", "show", "HEAD:" + rel],
                           capture_output=True, text=True, encoding="utf-8")
        if p.returncode == 0 and p.stdout.strip():
            txt, src = p.stdout, "git HEAD:" + rel
        else:
            txt, src = "", "no git HEAD copy"
    except Exception:
        txt, src = "", "git unreadable"
    if not txt:
        p2 = os.path.join(CARD_DIR, scene + ".facts.json")
        if os.path.isfile(p2):
            with open(p2, "r", encoding="utf-8") as fh:
                txt, src = fh.read(), "on-disk facts.json"
    if not txt:
        return [], "no prior facts.json (the scene was outside the card gate registry)"
    d = json.loads(txt)
    if "top_card_vl" in str(d.get("_source", "")):
        # this builder wrote that file; comparing the new gate against itself proves nothing
        return [], "no prior facts.json (the scene entered the card gate registry with this pass)"
    g = d.get("gate", {})
    toks = list(g.get("room_required", [])) + list(g.get("light_required", []))
    pc = g.get("per_chunk_tokens", [])
    if isinstance(pc, dict):
        for v in pc.values():
            toks += list(v)
    else:
        toks += list(pc)
    for f in d.get("figures", []):
        toks += list(f.get("visible", []))
    return sorted(set(t for t in toks if t)), src


def do_cards(args):
    doc = load_doc()
    if not doc:
        print(f"RED no record at {OUT}")
        return 2
    table = vp.vision_table()
    pre = doc_faults(doc, table)
    if pre:
        print("RED the caption record is not clean; cards are written only from a clean record")
        for p in pre[:10]:
            print("  FAULT " + p)
        return 2
    bad = []
    for scene in args.scenes:
        spec_p = os.path.join(SPEC_DIR, scene + ".json")
        if not os.path.isfile(spec_p):
            bad.append("SPEC_MISSING %s" % spec_p)
            continue
        with open(spec_p, "r", encoding="utf-8") as fh:
            spec = json.load(fh)
        rowA, rowB = caption_of(doc, scene, "A"), caption_of(doc, scene, "B")
        caps = [("A", rowA["caption"]), ("B", rowB["caption"])]
        card_text, ev, unresolved = compose_card(scene, spec, doc, caps)
        facts = compose_facts(scene, spec, doc, card_text, ev, unresolved)
        old_facts_p = os.path.join(CARD_DIR, scene + ".facts.json")
        old_tokens, old_src = old_gate_tokens(scene)
        card_path = os.path.join(CARD_DIR, scene + ".md")
        if os.path.isfile(card_path):
            with open(card_path, "r", encoding="utf-8") as fh:
                old_card = fh.read()
        else:
            old_card = ""
        # write first, then judge the written bytes: a card is judged as a file, not as a string
        with open(card_path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(card_text)
        with open(old_facts_p, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(facts, fh, indent=1, ensure_ascii=False, sort_keys=True)
            fh.write("\n")
        with open(card_path, "r", encoding="utf-8") as fh:
            written = fh.read()
        for f in card_faults(facts, written):
            bad.append(f)
        lost = [t for t in old_tokens if not find_quote(caps, t) and card_norm(t) not in card_norm(written)]
        kept = len(old_tokens) - len(lost)
        facts["_delta_vs_old_gate"] = {"measured": now(), "basis":
                                       "the tokens the superseded gate required (%s), tested against the new "
                                       "card + captions; a measurement, not a judgement" % old_src,
                                       "required_by_old_gate": len(old_tokens), "supported_by_new_card": kept,
                                       "unsupported_by_new_card": lost}
        with open(old_facts_p, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(facts, fh, indent=1, ensure_ascii=False, sort_keys=True)
            fh.write("\n")
        print(f"{scene}: card={card_path} bytes={os.path.getsize(card_path)} facts={old_facts_p} "
              f"figures={len(facts['figures'])} evidence={len(facts['gate']['evidence'])} "
              f"unresolved={unresolved} old_gate_tokens={len(old_tokens)} kept={kept} "
              f"unsupported={len(lost)} card_sha256={sha_file(card_path)[:16]}")
        for t in lost:
            print(f"   UNSUPPORTED-BY-NEW-CARD (was in the shipped gate): {t!r}")
    print("card_faults=%d" % len(bad))
    for b in bad:
        print("  FAULT " + b)
    print("VERDICT TOP_CARD_VL CARDS CLEAN" if not bad else "VERDICT TOP_CARD_VL CARDS RED")
    return 0 if not bad else 2


def main(argv=None):
    argv = argv or sys.argv[1:]
    mode = argv[0] if argv else "--check"
    ap = {"--model": MODEL_DEFAULT, "--scenes": list(SCENES), "--asks": ["A", "B"], "--tag": "",
          "--max-tokens": 3000, "--timeout": 600, "--rerun": False}
    i = 1
    while i < len(argv):
        if argv[i] in ap and i + 1 < len(argv):
            v = argv[i + 1]
            ap[argv[i]] = ([s for s in v.split(",") if s] if argv[i] in ("--scenes", "--asks")
                           else int(v) if argv[i] in ("--max-tokens", "--timeout") else v)
            i += 2
        elif argv[i] == "--rerun":
            ap["--rerun"] = True
            i += 1
        else:
            i += 1
    ns = type("NS", (), {"model": ap["--model"], "scenes": ap["--scenes"], "asks": ap["--asks"],
                         "tag": ap["--tag"],
                         "max_tokens": ap["--max-tokens"], "timeout": ap["--timeout"],
                         "rerun": ap["--rerun"]})()
    if mode == "--state":
        return do_state(ns)
    if mode == "--run":
        return do_run(ns)
    if mode == "--check":
        return do_check(ns)
    if mode == "--selftest":
        return do_selftest(ns)
    if mode == "--cards":
        return do_cards(ns)
    print("usage: --state [--tag N] | --run [--tag N] [--model vl_judge] [--scenes a,b] [--asks A,B] "
          "[--max-tokens N] [--rerun] | --check [--tag N] | --selftest [--tag N] | --cards [--tag N] "
          "[--scenes a,b]")
    return 2


if __name__ == "__main__":
    sys.exit(main())
