#!/usr/bin/env python
"""TR5S card - the start-image card of a NEW image, built only from its fresh captions.

Derrick 2026-10-26 12:37 PM CT (plan MAX block): "pick out a new image and animate it, 5 seconds", and the
TEST RUN row names the steps: "caption it with your own vision model (llama-swap `vl_judge`) ... write the
H3 prompt from that caption ... the card is self-consistent: zero self-contradictions". Item TR5S,
plan notes/plans/tr5s-test-run.md.

The base builder is C:/AI/community/notes/top_card_vl_build.py (CARD-VL, 2026-10-25): it composes a card and
a facts file from a caption record + a spec, and it owns the card gate `card_faults`. C:/AI/community/notes/
card_vl2_build.py (CARD-VL2, 2026-10-26) is the sibling that added ask C and the self-conflict census; this
pass reads both and adds nothing to them. What is new here is only the scope: a scene id that has never been
captioned, carded, prompted, graphed or animated (measured 2026-10-26: 0 files match notes/scenes/GI102.*,
0 graphs under C:/AI/community/p7/graphs load community/hc/GI102.jpg, 0 runs/* reference it).

The teeth this pass runs before a card ships:
  * tc.doc_faults - the caption record is clean: the uncensored vision model, gpu_guard IDLE rc 0 in front of
    every request, no-thinking rows (L21), byte-identical ComfyUI input copy, no refusal, no decline.
  * tc.card_faults - the shipped card gate: every required row cites a verbatim caption quote, no UNRESOLVED
    token, the figures row matches gate.figure_count, the head map matches the figure rows, the ban lists are
    not facts a caption states, and the card names the model file that wrote the captions.
  * scene_card_gate.selfconflicts - 0. Measured on the shipped cards on 2026-10-26: GI063 = 12, GI046 = 3
    (notes/card_vl2_build.py --census). A card of this pass is judged by the same function, with the light
    names mapped the way that pass maps them.
  * every caption of the record sits in the card verbatim (the captions are the only source).
  * the face-reference crop is attributed by measurement, not by a guess: the frontal cascade's full
    detection list is printed by --cropcheck and the card carries it.

  python C:/AI/community/notes/tr5s_card_build.py --state
  python C:/AI/community/notes/tr5s_card_build.py --cropcheck          # face crops + every detection, CPU
  python C:/AI/community/notes/tr5s_card_build.py --cards              # write only a self-consistent card
  python C:/AI/community/notes/tr5s_card_build.py --check              # record + card + the self-conflict gate
  python C:/AI/community/notes/tr5s_card_build.py --selftest           # seeded faults, counts printed
No model call, no render, no queue, no ComfyUI control call, no KEEP. The GPU is not touched by this file.
"""
import glob
import json
import os
import sys

sys.path.insert(0, "C:/AI/community/notes")
import scene_card_gate as scg          # the shipped card gate; selfconflicts() is its own test
import top_card_vl_build as tc         # the CARD-VL base: composition, card gate
import card_vl2_build as cv2           # registers ask C on the base; its census() maps the light-name gap
import tr5s_caption as tr5             # the tag, the pool resolver, the manifest check

TAG = tr5.TAG
SCENES = ("GI102",)                    # the card this pass writes; GI076 stays a captioned shortlist row
SPEC_DIR = tr5.SPEC_DIR
CARD_DIR = tc.CARD_DIR

# this process only: the base resolves a scene id out of one approved folder; TR5S ids live in two, verified
# against their MANIFEST.csv (tr5s_caption.resolve), and the base registry must know this pass's scene.
tc.SCENES = tuple(sorted(set(tc.SCENES) | set(SCENES)))
tc.still_path = lambda sc: tr5.resolve(sc)[0]


def spec_path(scene):
    return os.path.join(SPEC_DIR, scene + ".spec.json")


def card_path(scene):
    return os.path.join(CARD_DIR, scene + ".md")


def facts_path(scene):
    return os.path.join(CARD_DIR, scene + ".facts.json")


def read_facts(path):
    """A facts file read as it is on disk (no key normalising): the shape `census` judges, the shape
    `scene_card_gate.load_card` reads. The base's `load_facts` rewrites `banned_any` back to `banned`,
    which is fine for its own checks; the TR5S detectors read the disk shape so a rule is judged against
    the bytes that ship."""
    return json.load(open(path, encoding="utf-8"))


def spec(scene):
    """The authored spec (data, never generated). The long 'what the captions settled' row sits in the spec as
    `facts_extra_prose` and is merged into spec['facts_extra'] here, because that is the block the base
    builder merges into the facts file (top_card_vl_build.py:1105-1106)."""
    with open(spec_path(scene), "r", encoding="utf-8") as fh:
        s = json.load(fh)
    if s.get("facts_extra_prose"):
        s.setdefault("facts_extra", {})["_settled_rows"] = s.pop("facts_extra_prose")
    return s


def doc():
    tr5.sync_asks()          # a declared ask must carry the text that was sent; rows are never rewritten
    d = tc.load_doc(TAG)
    if not d:
        raise SystemExit("RED no caption record at %s - run python C:/AI/community/notes/tr5s_caption.py --run first"
                         % tr5.RECORD)
    tc.SCENES = tuple(sorted(set(tc.SCENES) | set(tc.scope_of(d, "scenes"))))
    return d


def caps_for(d, scene):
    return [(ak, tc.caption_of(d, scene, ak)["caption"]) for ak in tc.scope_of(d, "asks")]


def compose(scene, d):
    s = spec(scene)
    caps = caps_for(d, scene)
    card_text, ev, unresolved = tc.compose_card(scene, s, d, caps)
    facts = tc.compose_facts(scene, s, d, card_text, ev, unresolved)
    return card_text, facts, ev, unresolved, caps


def census(facts):
    """Self-contradictions, by the shipped gate's own function, with the light-name mapping CARD-VL2 measured
    (scene_card_gate.py:332-333 reads `room_bans`/`light_bans`; a facts file names them `room_banned`/
    `light_banned`). Without the mapping a card is scored with zero light bans."""
    gt = dict(facts.get("gate", facts))
    for src_key, gate_key in (("room_banned", "room_bans"), ("light_banned", "light_bans")):
        if not gt.get(gate_key) and gt.get(src_key):
            gt[gate_key] = gt[src_key]
    return scg.selfconflicts(gt)


def caption_sections(d, scene, card_text):
    """Every caption of the record sits in the card verbatim, all three asks."""
    bad = []
    n = scg.norm(card_text)
    for ak, cap in caps_for(d, scene):
        if scg.norm(cap) not in n:
            bad.append("CARD_CAPTION_MISSING %s the card does not carry caption %s verbatim" % (scene, ak))
    return bad


def pick_faults(scene, d):
    """The MAX block's own conditions, checked as facts: a NEW image, never animated, not GI063, approved.
    'Never animated' is read off runs/*/request.api.json, the record of what was queued, not off a list."""
    bad = []
    if scene == "GI063":
        bad.append("PICK_GI063 the MAX block names GI063 as the image not to use")
    rows = tr5.pool_rows()
    key = scene + ".jpg"
    if key not in rows:
        bad.append("PICK_NOT_APPROVED %s is not in any approved GROK_IMAGINE MANIFEST.csv" % scene)
    else:
        path, want = rows[key]
        if not os.path.isfile(path):
            bad.append("PICK_FILE_ABSENT %s named by a manifest and not on disk" % path)
        elif tc.sha_file(path) != want:
            bad.append("PICK_SHA_DRIFT %s bytes do not match MANIFEST" % path)
    animated = animated_ids()
    if scene in animated:
        bad.append("PICK_ALREADY_ANIMATED %s appears as the LoadImage input of %s" % (scene, animated[scene]))
    row = tc.caption_of(d, scene, "A")
    if not row or row.get("http_status") != 200 or row.get("guard_rc") != 0:
        bad.append("PICK_NOT_CAPTIONED %s has no clean ask A row (the prompt is written from the caption)" % scene)
    return bad


def animated_ids():
    """id -> the run file that names it as an image input. Every JSON under a runs/ directory, read as text:
    the graph and request files are the record of what was sent to ComfyUI (AGENTS.md L20: a run's proof is
    its files on disk), so 'this image has been animated before' is read off those bytes, not off a list."""
    out = {}
    for p in sorted(glob.glob("C:/AI/community/runs/*/*.json")):
        try:
            with open(p, "r", encoding="utf-8", errors="replace") as fh:
                t = fh.read()
        except OSError:
            continue
        for tok in ("GI", "BD", "HC", "RS", "POOL"):
            for name in set(w for w in t.replace('"', " ").replace(",", " ").replace("/", " ").split()
                            if w.endswith(".jpg")):
                base = os.path.basename(name)[:-4].upper()
                if base.startswith(tok) and base not in out:
                    out[base] = os.path.relpath(p, "C:/AI/community/runs")
    return out


def face_crops(scene):
    """The face-reference crop of the start frame, re-measured in this process (CPU, OpenCV; the Python 3.12
    interpreter has cv2 4.11.0 - AGENTS.md L16 names this interpreter for the face work)."""
    import cv2
    src = tr5.resolve(scene)[0]
    img = cv2.imread(src)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    out = {"src": src.replace("\\", "/"), "dims": list(img.shape[:2])[::-1], "cascades": {}}
    for name, f in (("frontal_default", "haarcascade_frontalface_default.xml"),
                    ("frontal_alt2", "haarcascade_frontalface_alt2.xml"),
                    ("profile", "haarcascade_profileface.xml")):
        c = cv2.CascadeClassifier(cv2.data.haarcascades + f)
        d = sorted([list(map(int, x)) for x in c.detectMultiScale(gray, 1.1, 5, minSize=(60, 60))],
                   key=lambda b: -b[2] * b[3])
        out["cascades"][name] = d
    crop = os.path.join(tc.COMFY_INPUT, scene + "_w1_face.png")
    out["crop"] = crop.replace("\\", "/")
    out["crop_exists"] = os.path.isfile(crop)
    out["crop_bytes"] = os.path.getsize(crop) if out["crop_exists"] else 0
    return out


def crop_faults(scene, facts):
    """A card that cites a crop must name the file that exists, and the crop must be attributed: the largest
    frontal detection is the frontal figure the captions name."""
    bad = []
    m = face_crops(scene)
    if not m["crop_exists"]:
        bad.append("CROP_ABSENT %s the face-reference input %s is not on disk" % (scene, m["crop"]))
    front = m["cascades"].get("frontal_default") or []
    if not front:
        bad.append("CROP_NO_FACE %s the frontal cascade finds no face in the start frame" % scene)
        return bad
    quoted = json.dumps(facts.get("gate", {}).get("evidence", {})) + json.dumps(facts.get("_face_crop", {}))
    if str(front[0]) not in quoted.replace(" ", "") and f"{front[0][0]},{front[0][1]},{front[0][2]},{front[0][3]}" \
            not in quoted.replace(" ", ""):
        bad.append("CROP_NOT_CITED %s the card does not carry the largest frontal detection %s" % (scene, front[0]))
    if m["cascades"].get("profile"):
        bad.append("CROP_PROFILE_FACES %s the profile cascade detects faces, so the card's attribution of the "
                   "crop needs a second reading: %s" % (scene, m["cascades"]["profile"]))
    return bad


# ---------------------------------------------------------------- modes
def do_state(args):
    d = doc()
    print("TR5S tag=%s scope=%s asks=%s model=%s" % (TAG, tc.scope_of(d, "scenes"), tc.scope_of(d, "asks"),
                                                     tc.MODEL_DEFAULT))
    print(f"record={tr5.RECORD} rows={len(d['rows'])}")
    print("rows:")
    for r in d["rows"]:
        print("  %s/%s http=%s finish=%s words=%s declines=%s guard_rc=%s raw=%s"
              % (r["scene"], r["ask_id"], r["http_status"], r["finish_reason"], r["caption_words"],
                 r["decline_markers"], r["guard_rc"], os.path.basename(r.get("raw_path") or "")))
    for scene in SCENES:
        print(f"  spec={spec_path(scene)} exists={os.path.isfile(spec_path(scene))}")
        for p in (card_path(scene), facts_path(scene)):
            print(f"  {'exists' if os.path.isfile(p) else 'ABSENT '} {p}"
                  + (f" bytes={os.path.getsize(p)}" if os.path.isfile(p) else ""))
    print(f"animated ids read off runs/*/request.api.json: {len(animated_ids())} "
          f"{sorted(animated_ids())[:20]}")
    return 0


def do_cropcheck(args):
    for scene in SCENES:
        m = face_crops(scene)
        print(f"{scene} src={m['src']} dims={m['dims']}")
        for k, v in m["cascades"].items():
            print(f"  {k}: {json.dumps(v)}")
        print(f"  crop={m['crop']} exists={m['crop_exists']} bytes={m['crop_bytes']}")
    return 0


def do_cards(args):
    """Write the card + facts only if every gate above reads 0. A card that contradicts itself is not written."""
    d = doc()
    pre = tc.doc_faults(d, tc.vp.vision_table())
    if pre:
        print("RED the caption record is not clean; a card is written only from a clean record")
        for p in pre[:15]:
            print("  FAULT " + p)
        return 2
    print(f"record clean: faults=0 rows={len(d['rows'])} scope={tc.scope_of(d,'scenes')}x{tc.scope_of(d,'asks')}")
    bad = []
    for scene in SCENES:
        if not os.path.isfile(spec_path(scene)):
            bad.append("SPEC_MISSING %s" % spec_path(scene))
            continue
        card_text, facts, ev, unresolved, caps = compose(scene, d)
        faults = (tc.card_faults(facts, card_text) + caption_sections(d, scene, card_text)
                  + pick_faults(scene, d))
        # CARD_PATH is the rule that the card file exists on disk; that is the write this step is about to do,
        # so the pre-write pass drops it and the post-write re-judgement enforces it on the written bytes.
        faults = [f for f in faults if not f.startswith("CARD_PATH")]
        cen = census(facts)
        print(f"{scene}: figures={len(facts['figures'])} captions={len(caps)} evidence={len(ev)} "
              f"unresolved={len(unresolved)} card_faults={len(faults)} self_conflicts={len(cen)} "
              f"core_tokens={len(facts['gate']['per_chunk_tokens'])} "
              f"open_beat={sum(len(v) for v in facts['gate']['open_beat'].values())} "
              f"banned_any={len(facts['gate']['banned']['any'])}")
        for f in faults:
            print("  FAULT " + f)
        for r in cen[:40]:
            print(f"  SELF-CONFLICT {r['scope']} figure {r['figure']}: token {r['token']!r} carries the "
                  f"card's own ban {r['banned_word']!r} ({r['reading']})")
        if faults or cen:
            print("  NOT WRITTEN: a card this pass judges red does not go on disk")
            continue
        # the base's own order (top_card_vl_build.py:1265-1283): write the files, then judge the written bytes,
        # because card_faults charges CARD_PATH against the card file existing. A card that reads red after the
        # write is removed again, so a red card is never left on disk for a prompt writer to read.
        with open(card_path(scene), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(card_text)
        with open(facts_path(scene), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(facts, fh, indent=1, ensure_ascii=False, sort_keys=True)
            fh.write("\n")
        written = open(card_path(scene), "r", encoding="utf-8").read()
        after = tc.card_faults(facts, written) + caption_sections(d, scene, written) + crop_faults(scene, facts)
        cen2 = census(json.load(open(facts_path(scene), encoding="utf-8")))
        print(f"  WROTE card={card_path(scene)} bytes={os.path.getsize(card_path(scene))} "
              f"card_sha256={tc.sha_file(card_path(scene))[:16]} "
              f"facts={facts_path(scene)} bytes={os.path.getsize(facts_path(scene))}")
        print(f"  re-judged from disk: card_faults={len(after)} self_conflicts={len(cen2)}")
        for f in after:
            print("   FAULT " + f)
        if after or cen2:
            for p in (card_path(scene), facts_path(scene)):
                os.remove(p)
            print("  REMOVED both files: a card that reads red is not left on disk")
        bad += after + cen2
    print("VERDICT TR5S CARD CLEAN self_conflicts=0" if not bad else "VERDICT TR5S CARD RED")
    return 0 if not bad else 2


def do_check(args):
    d = doc()
    bad = tc.doc_faults(d, tc.vp.vision_table())
    print(f"record faults={len(bad)}")
    for b in bad[:15]:
        print("  FAULT " + b)
    for scene in SCENES:
        cp, fp = card_path(scene), facts_path(scene)
        if not (os.path.isfile(cp) and os.path.isfile(fp)):
            print(f"  FAULT CARD_NOT_WRITTEN {scene} card={os.path.isfile(cp)} facts={os.path.isfile(fp)}")
            continue
        card_text = open(cp, encoding="utf-8").read()
        facts = json.load(open(fp, encoding="utf-8"))
        f1 = tc.card_faults(facts, card_text) + caption_sections(d, scene, card_text) + pick_faults(scene, d) \
            + crop_faults(scene, facts)
        cen = census(facts)
        gt = scg.load_card(fp)
        # the card alone, with no prompt text: the gate's scan of an empty text is a coverage measurement, so
        # the numbers printed here are the card's own (self-conflicts) and never a prompt verdict.
        empty = scg.scan("", gt, scg.required(gt))
        print(f"  {scene} card_sha256={tc.sha_file(cp)[:12]} card_faults={len(f1)} self_conflicts={len(cen)} "
              f"core_tokens={len(facts['gate']['per_chunk_tokens'])} "
              f"open_beat={sum(len(v) for v in facts['gate']['open_beat'].values())} "
              f"gate_reads_tokens={sum(len(v) for v in scg.required(gt)['figures'].values())} "
              f"gate_reads_room={len(scg.required(gt)['room'])} light={len(scg.required(gt)['light'])} "
              f"empty_text_findings={len(scg.findings(empty))}")
        for f in f1[:15]:
            print("   FAULT " + f)
        for r in cen[:15]:
            print(f"   SELF-CONFLICT {r['scope']} {r['figure']}: {r['token']!r} vs {r['banned_word']!r}")
        bad += f1 + cen
    ok = not bad
    print("VERDICT TR5S CARD CHECK CLEAN" if ok else "VERDICT TR5S CARD CHECK RED")
    return 0 if ok else 2


def seed_specs(scene):
    """(name, mutated facts, expect_fault_prefix). Each seed is a real composition with one thing broken,
    judged by the same functions --cards runs (L10: seed the fault, require the detector to fire)."""
    import copy
    d = doc()
    card_text, facts, ev, unresolved, caps = compose(scene, d)
    S = []

    def mut(fn):
        f = copy.deepcopy(facts)
        fn(f)
        return f

    S.append(("required_token_carries_a_ban",
              mut(lambda f: f["gate"]["per_chunk_tokens"].append("a candle on the nightstand")), "SELF_CONFLICT"))
    S.append(("light_row_carries_a_light_ban",
              mut(lambda f: f["gate"]["light_required"].append("lit by candlelight")), "SELF_CONFLICT"))
    S.append(("room_row_carries_a_room_ban",
              mut(lambda f: f["gate"]["room_required"].append("the kitchen counter")), "SELF_CONFLICT"))
    S.append(("open_beat_carries_its_own_ban",
              mut(lambda f: f["gate"]["open_beat"]["1"].append("she is sitting up in bed")), "SELF_CONFLICT"))
    S.append(("clean_card_as_composed", copy.deepcopy(facts), "NO_FAULT"))
    texts = [("card_as_composed", card_text, "NO_FAULT"),
             ("caption_C_dropped", card_text.replace(caps[-1][1], ""), "CARD_CAPTION_MISSING"),
             ("quote_made_up", card_text.replace(ev[facts["gate"]["room_required"][0]][:40], "XX invented XX"),
              "CARD_EVIDENCE"),
             ("figure_count_row_lied", card_text.replace("figures: 2", "figures: 9"), "CARD_COUNT"),
             ("model_row_removed", card_text.replace(facts["model"], "no_such_model"), "CARD_MODEL")]
    return S, texts, card_text, facts


def do_selftest(args):
    scene = SCENES[0]
    if not (os.path.isfile(tr5.RECORD) and os.path.isfile(spec_path(scene))):
        print("RED needs the caption record and the spec before it can seed faults")
        return 2
    bad = []
    S, texts, card_text, facts = seed_specs(scene)
    fired = 0
    for name, f, want in S:
        rows = census(f)
        n = len(rows)
        ok = (n > 0) if want == "SELF_CONFLICT" else (n == 0)
        fired += 1 if ok else 0
        if not ok:
            bad.append(name)
        print(f"census seed {name:34s} self_conflicts={n} expect_{'fault' if want=='SELF_CONFLICT' else 'zero'} "
              f"{'OK' if ok else 'SILENT'}" + (f" first={rows[0]['token']!r} vs {rows[0]['banned_word']!r}" if rows else ""))
    print(f"census seeds: {len(S)} fired={fired} silent={len(S)-fired}")
    d = doc()
    cfired = 0
    for name, text, want in texts:
        fs = tc.card_faults(facts, text) + caption_sections(d, scene, text)
        hit = [x for x in fs if x.startswith(want)] if want != "NO_FAULT" else fs
        ok = bool(hit) if want != "NO_FAULT" else not fs
        cfired += 1 if ok else 0
        if not ok:
            bad.append(name)
        print(f"card seed {name:34s} expect={want:22s} faults={len(fs)} first={(fs[0][:90] if fs else '')}")
    # the pick detector: seed the three things the MAX block forbids
    pfire = 0
    for name, sc, want in [("pick_GI063", "GI063", "PICK_GI063"),
                           ("pick_already_animated", "GI046", "PICK_ALREADY_ANIMATED"),
                           ("pick_not_in_pool", "ZZ999", "PICK_NOT_APPROVED")]:
        fs = pick_faults(sc, d)
        hit = [x for x in fs if x.startswith(want)]
        ok = bool(hit)
        pfire += 1 if ok else 0
        if not ok:
            bad.append(name)
        print(f"pick seed {name:34s} expect={want:24s} faults={len(fs)} first={(fs[0][:90] if fs else 'NONE - SILENT')}")
    real = pick_faults(scene, d)
    print(f"real pick {scene}: faults={len(real)} {real[:2]}")
    if real:
        bad.append("real_pick")
    cfaults = tc.card_faults(facts, card_text)
    print(f"real card {scene}: card_faults={len(cfaults)} self_conflicts={len(census(facts))} "
          f"{[c[:60] for c in cfaults][:3]}")
    if cfaults:
        bad.append("real_card")
    print("VERDICT TR5S CARD SELFTEST CLEAN" if not bad else f"VERDICT TR5S CARD SELFTEST BROKEN {bad}")
    return 0 if not bad else 2


def main(argv=None):
    argv = argv or sys.argv[1:]
    mode = argv[0] if argv else "--check"
    if mode == "--state":
        return do_state(argv)
    if mode == "--cropcheck":
        return do_cropcheck(argv)
    if mode == "--cards":
        return do_cards(argv)
    if mode == "--check":
        return do_check(argv)
    if mode == "--selftest":
        return do_selftest(argv)
    print("usage: --state | --cropcheck | --cards | --check | --selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main())
