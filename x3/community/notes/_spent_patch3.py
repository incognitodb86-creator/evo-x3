"""Part 3: TOP_TAKES covers every take once, and the selftest seeds the new card gates, the facts file, and the
spent-render receipts. Every seed must fire on its own detector and the real artifacts must stay clean (L10)."""
P = r"C:/AI/community/notes/hc15_anchor_carry_build.py"
src = open(P, encoding="utf-8").read()

NEW = '''
    # ---- card gates: each rule seeded on a real graph, and ck_top_card must fire there (TOP-SCENE) ----
    def app(ch, text):
        def fn(gg):
            gg[ch]["inputs"]["prompt"] = gg[ch]["inputs"]["prompt"] + text
        return fn

    inmem("solo clause written back onto a two-figure card ('the only person in that photograph')", B46,
          app("c0", "\\nThe woman is the only person in that photograph."), "ck_top_card")
    inmem("invented appearance charged to the orc (tusk, claw, fur)", B46,
          app("c0", "\\nThe orc's tusked shoulder rubs against her back, clawed hand on the small of her back."),
          "ck_top_card")
    inmem("invented head for the head-cropped figure (the card crops him at the neck)", B46,
          app("c1", "\\nHis head grins down at her from the top of the frame."), "ck_top_card")
    def pose_drift(gg):
        p = gg["c1"]["inputs"]["prompt"]
        i = p.index("At 00:")
        gg["c1"]["inputs"]["prompt"] = (p[:i] + "At 00:10.400 the woman stands up and the orc kneels up behind her. "
                                        + p[i:])

    inmem("opening pose drift in the c1 opening beat (stands up / kneels up, against the card's opening pose)",
          B46, pose_drift, "ck_top_card")
    inmem("the card's opening pose written out of the c1 opening beat", B46,
          lambda gg: gg["c1"]["inputs"].__setitem__("prompt", gg["c1"]["inputs"]["prompt"].replace(
              "At 00:10.400", "At 00:10.400 She rises to her feet and the orc stands. ", 1)), "ck_top_card")
    inmem("invented room on the GI046 card (bedroom, couch)", B46,
          app("c0", "\\nThe scene moves to the bedroom, where the couch sits against the wall."), "ck_top_card")
    inmem("the card's room words stripped from the prompt (living room, rug)", B46,
          sub("living room", "room", "shag rug", "floor"), "ck_top_card")
    inmem("canon adult age stripped from a sentence naming a person-word", B46,
          sub("a fictional adult aged 27", "a woman", "a fictional adult aged 34", "an orc"), "ck_top_card")
    inmem("invented machine appearance on the refusal card (chrome chassis, glowing panels)", B63,
          app("c0", "\\nThe machine shows a chrome chassis with glowing panels and a metal jaw."), "ck_top_card")
    inmem("the shipped consent line written back in ('consenting and eager')", A63,
          app("c0", "\\nThe woman is consenting and eager, and she loves it."), "ck_top_card")
    inmem("the consent routing stripped from the GI063 prose (card record + needs_derrick row)", A63,
          sub("the card record shows restraint and distress", "the frame reads as staged",
              "notes/needs_derrick.md row 21", "the notes file"), "ck_top_card")
    inmem("invented room on the GI063 refusal card (couch, television)", A63,
          app("c1", "\\nBehind her the couch and the television sit in the room."), "ck_top_card")
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
            "ck_top_facts", "GI046", facts_json(lambda d: d.__setitem__("status", "OK")))
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
        m["note"] = m["note"].replace("This prose record has 0 renders", "This prose record was rendered")
        json.dump(m, open(P["man"], "w", encoding="utf-8"), indent=1)

    onfile("manifest note claims the current prose record was rendered when it was not", A46, "ck_top_manifest",
           man_note_prose, files=("man",))

    def req_spent(k, P):
        req = json.load(open(P["req"], encoding="utf-8"))
        req["jobs"][0]["id"] = A46
        req["id"] = A46
        req["api"] = gpath(A46).replace("\\\\", "/")
        open(P["req"], "w", encoding="utf-8").write(json.dumps(req, indent=2, ensure_ascii=False))

    onfile("request arms the SPENT id (a render receipt used as a queue entry)", B46, "ck_top_arm", req_spent,
           files=("req",))

    real = {n: run(n) for n in TOP_TAKES}'''

PAIRS = [
    (
        'TOP_TAKES = TOP_ORDER + [TOP["GI046"]["take_b"], TOP["GI063"]["take_b"]]',
        '# every take of both named stills, once each (TOP_ORDER can carry a take B when a take A is spent)\n'
        'TOP_TAKES = [TOP[_ts][_tk2] for _ts in TOP for _tk2 in ("take_a", "take_b")]'
    ),
    (
        '    onfile("id already spent (an mp4 exists on disk)", A46, "ck_idfree", man_spent, files=("mp4",))\n'
        '    onfile("manifest claims an unrendered id and it is spent", A46, "ck_top_manifest", man_spent, files=("mp4",))',
        '    # seeded on a FREE take: a spent take carries a receipt, so its id-free claim is not the property under test\n'
        '    onfile("id already spent (an mp4 exists on disk)", B46, "ck_idfree", man_spent, files=("mp4",))\n'
        '    onfile("manifest claims an unrendered id and it is spent", B46, "ck_top_manifest", man_spent, files=("mp4",))'
    ),
    (
        '        req["jobs"] += [{"id": B46, "kind": "graph", "frames": FRAMES, "frames_tol": 33, "minutes": TOP_EST_MIN,\n'
        '                        "note": top_job_note(B46)},\n'
        '                       {"id": B63, "kind": "graph", "frames": FRAMES, "frames_tol": 33, "minutes": TOP_EST_MIN,\n'
        '                        "note": top_job_note(B63)}]',
        '        req["jobs"] += [{"id": TOP["GI046"]["take_a"], "kind": "graph", "frames": FRAMES, "frames_tol": 33,\n'
        '                        "minutes": TOP_EST_MIN, "note": top_job_note(TOP["GI046"]["take_a"])},\n'
        '                       {"id": B63, "kind": "graph", "frames": FRAMES, "frames_tol": 33, "minutes": TOP_EST_MIN,\n'
        '                        "note": top_job_note(B63)}]'
    ),
    ('    real = {n: run(n) for n in TOP_TAKES}', NEW),
]

for old, new in PAIRS:
    n = src.count(old)
    assert n == 1, ("anchor count", n, old[:90])
    src = src.replace(old, new, 1)

open(P, "w", encoding="utf-8", newline="\n").write(src)
print("patched part 3: TOP_TAKES + card/facts/receipt seeds")
