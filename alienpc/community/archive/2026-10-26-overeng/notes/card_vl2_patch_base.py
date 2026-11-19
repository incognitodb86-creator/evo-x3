"""One-pass patch of top_card_vl_build.py for CARD-VL2: generic tag/scope plumbing, nothing item-specific.
Every replacement is asserted to match exactly once, so a silent miss is a hard stop."""
import io, sys

P = "C:/AI/community/notes/top_card_vl_build.py"
src = open(P, encoding="utf-8").read()

E = []

# ---- ask C is NOT base: the base module registers asks A/B only; a pass registers its own ask.
E.append(('''ASK_C = ("Look at the attached image. Caption this start still. List, in your own words, exactly what is "
         "visible: (1) every figure - apparent age range, skin, hair, build, wardrobe, pose, position in "
         "frame, and whether the head is in frame. (2) For EACH figure, say in plain words what is visible at "
         "the head and face, at the chest, and at the groin and pelvic region, including any pubic, genital, "
         "erect, covering, clothing, shading or shadow detail visible there. (3) The room: walls, floor, "
         "furniture, equipment, screens, and the direction and colour of the light. (4) Every object, screen, "
         "television, restraint, or prop, and what it shows. (5) The size and height relation between the "
         "figures, and what each figure's hands are doing and where they touch. If a region is not visible, "
         "out of frame, hidden by an angle, an object, a crop, blur, shadow, or resolution, write "
         "'not visible' for that region. Do not name real people, do not guess, do not invent, do not judge "
         "quality, do not refuse, do not omit a figure, do not skip a region that is visible, and write no "
         "prose outside the caption.")

ASK_B = (''', '''ASK_B = ('''))
E.append(('''    "C": "this builder's CARD-VL2 pass (2026-10-26): the regions the 2025 cards left silent. needs_derrick.md "
         "row 28 (Derrick 2026-10-26 7:49 AM CT on the GI046 render) names anatomy the GI046 card never "
         "described, and the 2025 GI063 card's own head_in_frame/not_visible rows name the face and the "
         "groin it did not speak of. Ask C asks for those rows by name and keeps the 2025 rule 'if a region "
         "is not visible write not visible'; the transport and the no-thinking options are unchanged.",
}''', '''}'''))
E.append(('''ASKS = {"A": ASK_A, "B": ASK_B, "C": ASK_C}''', '''ASKS = {"A": ASK_A, "B": ASK_B}'''))
E.append(('''    "C": "## caption C verbatim (the regions the 2025 cards left silent: face, chest, groin, hands, size)",
}''', '''}'''))
E.append(('''    "2": {"record": RECORD2, "spec_dir": SPEC_DIR2, "raw_suf": "_vl2_", "mark": "card_rebuild",
          "asks": ["A", "B", "C"], "item": "CARD-VL2, Derrick 2026-10-26 7:08 AM CT"},
}''', '''}'''))
E.append(('''# A caption pass is a TAG, and a tag owns its record, its raw captions and its facts spec. The 2025 record
# is cited by the live cards and by needs_derrick.md row 29, so a later pass never writes over it.
RECORD2 = os.path.join(NOTES, "card_rebuild_results.json")
SPEC_DIR2 = os.path.join(NOTES, "card_rebuild_facts")''',
'''# A caption pass is a TAG, and a tag owns its record, its raw captions and its facts spec. The 2025 record
# is cited by the live cards and by needs_derrick.md row 29, so a later pass never writes over it. A pass
# that wants its own record registers a tag here: card_vl2_build.py adds tag "2" (its own record, raw
# captions, facts spec, ask C) at import, so the 2025 pass keeps the exact bytes the cards cite. The one
# rule a tag cannot escape: the record, the raw captions and the spec are the tag's, never shared.'''))

# ---- the record's own integrity: a scope is the contract, asked asks only, rows outside scope are faults
E.append(('''    for k in ASKS:
        a = (doc.get("asks") or {}).get(k)
        if not a or a.get("text") != ASKS[k] or a.get("sha256") != sha_text(ASKS[k]):
            bad.append("ASK_SHA ask %s text/sha in the record is not the ask this builder sends" % k)''',
'''    for k in scope_of(doc, "asks"):
        a = (doc.get("asks") or {}).get(k)
        if not a or a.get("text") != ASKS.get(k) or a.get("sha256") != sha_text(ASKS.get(k, "")):
            bad.append("ASK_SHA ask %s text/sha in the record is not the ask this builder sends" % k)
    bad += scope_faults(doc)'''))
E.append(('''        if ak not in ASKS:
            bad.append("ASK_ID row %s/%s is not ask A or B" % (sc, ak))''',
'''        if ak not in ASKS:
            bad.append("ASK_ID row %s/%s is not a registered ask %s" % (sc, ak, sorted(ASKS)))
        if ak not in scope_of(doc, "asks"):
            bad.append("ASK_ROW_UNDECLARED row %s/%s: the record declares asks %s, this row is ask %r - "
                       "an unasked caption in a record is an unasked word"
                       % (sc, ak, scope_of(doc, "asks"), ak))'''))
E.append(('''    for sc in args_scenes(doc):
        for ak in ASKS:
            if (sc, ak) not in have:
                bad.append("ROW_MISSING no row for %s/%s (the item is 3 scenes x 2 asks)" % (sc, ak))''',
'''    for sc in args_scenes(doc):
        for ak in scope_of(doc, "asks"):
            if (sc, ak) not in have:
                bad.append("ROW_MISSING no row for %s/%s (the record's scope is %s x %s)"
                           % (sc, ak, args_scenes(doc), scope_of(doc, "asks")))
    for key in have:
        if key[0] not in args_scenes(doc):
            bad.append("ROW_OUT_OF_SCOPE row %s names a scene outside the record's scope %s - a row for a "
                       "scene this record never asked about is not evidence for these cards"
                       % (list(key), args_scenes(doc)))'''))

# ---- do_run: a tag, its raw captions, its scope, its record
E.append(('''    doc = load_doc() or new_doc(table)''',
          '''    doc = load_doc(args.tag) or new_doc(table, args.tag)'''))
E.append(('''    command = (f"python C:/AI/community/notes/top_card_vl_build.py --run --model {args.model} "
               f"--scenes {','.join(args.scenes)} --asks {','.join(args.asks)} "
               f"--max-tokens {args.max_tokens} --no-thinking")''',
'''    tag_arg = f"--tag {args.tag} " if args.tag else ""
    command = (f"python C:/AI/community/notes/top_card_vl_build.py --run {tag_arg}--model {args.model} "
               f"--scenes {','.join(args.scenes)} --asks {','.join(args.asks)} "
               f"--max-tokens {args.max_tokens} --no-thinking")'''))
E.append(('''                raw = os.path.join(RAW_DIR, f"{sc}_vl_{ak}.txt").replace("\\\\", "/")''',
          '''                raw = raw_path(sc, ak, args.tag).replace("\\\\", "/")'''))
E.append(('''            doc["rows"] = [r for r in doc["rows"] if (r.get("scene"), r.get("ask_id")) != key] + [row]
            save_doc(doc)''',
'''            doc["rows"] = [r for r in doc["rows"] if (r.get("scene"), r.get("ask_id")) != key] + [row]
            # the scope is what this record covers, written from the run itself: the scenes it asked about
            # plus any scene it already paid for, and the tag's asks as the contract. A run of 2 of 3
            # scenes is 2 x asks, not 3 x asks, and a missing asked row stays ROW_MISSING.
            doc["scope"] = {"scenes": sorted(set(args.scenes) | {r.get("scene") for r in doc["rows"]}),
                            "asks": sorted(ctx(args.tag)["asks"])}
            save_doc(doc)'''))
E.append(('''    print(f"record: {OUT} rows={len(doc['rows'])}")''',
          '''    print(f"record: {ctx(args.tag)['record']} rows={len(doc['rows'])} scope="
          f"{doc.get('scope', 'none (the 2025 shape)')}")'''))

# ---- do_state: name the tag, its record, its spec dir, and measure the cards on disk self-conflicts
E.append(('''    print(f"  record={OUT} exists={os.path.isfile(OUT)} spec_dir={SPEC_DIR} exists={os.path.isdir(SPEC_DIR)}")''',
'''    print(f"  tag={args.tag!r} record={ctx(args.tag)['record']} exists={os.path.isfile(ctx(args.tag)['record'])} "
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
                  f"{r['banned_word']!r} ({r['reading']})")'''))

# ---- a describe row may cite any registered ask, not only A and B
E.append(('''    base = re.sub(r"\\s*\\((?:ask [AB] adds[^)]*)\\)", "", value)
    base = re.sub(r"\\s*;\\s*ask [AB] adds.*$", "", base, flags=re.S)''',
'''    base = re.sub(r"\\s*\\((?:ask [A-Z] adds[^)]*)\\)", "", value)
    base = re.sub(r"\\s*;\\s*ask [A-Z] adds.*$", "", base, flags=re.S)'''))
E.append(('''    comma and parenthetical parts) and quote the longest candidate a caption states verbatim. No candidate''',
'''    comma and parenthetical parts, where an annotation may cite any registered ask (ask A, B, C...)) and
    quote the longest candidate a caption states verbatim. No candidate'''))

# ---- compose_card: the record's own asks, the record's own path, the spec's own supersedes, every caption
E.append(('''    add(f"asks: A sha256 {doc['asks']['A']['sha256']} / B sha256 {doc['asks']['B']['sha256']} - the 04:34 CT "
        "ask text with only the first sentence replaced (the pi read-tool sentence cannot apply to a request "
        "that attaches the image), so the MODEL is the only variable")''',
'''    add("asks: " + " / ".join(f"{k} sha256 {(doc.get('asks') or {}).get(k, {}).get('sha256', 'NONE')}"
                              for k in scope_of(doc, "asks")))
    for k in scope_of(doc, "asks"):
        add(f"ask_{k}_provenance: {((doc.get('asks') or {}).get(k) or {}).get('provenance', 'UNDECLARED')}")'''))
E.append(('''    add(f"record: {OUT.replace(chr(92), '/')}")''',
'''    rec = ctx(doc.get("tag", ""))["record"].replace(chr(92), "/")
    add(f"record: {rec}")'''))
E.append(('''    add(f"supersedes: notes/scenes/{scene}.md of 2026-10-25 04:34-04:38 CT (caption_status REFUSAL_TRUNCATED, "
        "coding_swift15_iq3s). Git history is the backup; no .bak.")''',
'''    add(spec.get("supersedes",
        f"supersedes: notes/scenes/{scene}.md of 2026-10-25 04:34-04:38 CT (caption_status REFUSAL_TRUNCATED, "
        "coding_swift15_iq3s). Git history is the backup; no .bak."))'''))
E.append(('''    add("")
    add("## caption A verbatim (full inventory ask)")
    add("")
    add(caps[0][1])
    add("")
    add("## caption B verbatim (non-sexual identity + composition ask)")
    add("")
    add(caps[1][1])''',
'''    for ak, cap_text in caps:
        add("")
        add(CAPTION_HEAD.get(ak, f"## caption {ak} verbatim"))
        add("")
        add(cap_text)'''))

# ---- compose_facts: every raw caption of the record, the record path from the tag, light_bans for the shipped gate
E.append(('''        "caption": caption_of(doc, scene, "A")["raw_path"],
        "caption2": caption_of(doc, scene, "B")["raw_path"],''',
'''        "caption": caption_of(doc, scene, "A")["raw_path"],
        "caption2": caption_of(doc, scene, "B")["raw_path"],
        "captions_all": {ak: caption_of(doc, scene, ak)["raw_path"] for ak in scope_of(doc, "asks")}
        if all(caption_of(doc, scene, ak) for ak in scope_of(doc, "asks")) else {},'''))
E.append(('''        "light_required": spec["light"],''',
'''        "light_required": spec["light"],
        # the shipped gate reads a card's light bans under `light_bans` (scene_card_gate.py:246,333) and a
        # CARD-VL facts file names them `light_banned`, so on 2026-10-26 the shipped gate read 0 light bans
        # off these cards and selfconflicts scored them 0. The rebuilt card carries both keys, so its light
        # bans are enforced and its self-conflict census can see them: the card must be self-consistent.
        "light_bans": spec["light_banned"],'''))
E.append(('''        "_source": f"{OUT.replace(chr(92), '/')} rows {scene}/A + {scene}/B, captioned by the uncensored "
                   "vision model on the start still, 2026-10-25",''',
'''        "_source": f"{ctx(doc.get('tag', ''))['record'].replace(chr(92), '/')} rows "
                   + " + ".join(f"{scene}/{ak}" for ak in scope_of(doc, "asks"))
                   + ", captioned by the uncensored vision model on the start still",'''))

for i, (old, new) in enumerate(E):
    n = src.count(old)
    if n != 1:
        print("ANCHOR %d matched %d times - STOP\n%s\n..." % (i, n, old[:200]))
        sys.exit(2)
    src = src.replace(old, new)
open(P, "w", encoding="utf-8", newline="\n").write(src)
print("patched %d blocks" % len(E))
