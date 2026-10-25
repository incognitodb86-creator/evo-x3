"""Part 6: re-anchor the seeds whose anchors belonged to the pre-TOP-SCENE prose (a seed whose anchor is absent
is a no-op seed, and a no-op seed that prints SEED FIRED for another reason is a lie). Each seed below was
SEED MISSED on the current prose; each now fires on its own detector."""
P = r"C:/AI/community/notes/hc15_anchor_carry_build.py"
src = open(P, encoding="utf-8").read()

PAIRS = [
    # 1: <Subject 2> written as a woman as well as the orc -> ck_top_species (two human groups)
    (
        '    inmem("both figures called a woman (the figure default the item bars)", A46,\n'
        '          sub("is the orc standing directly behind", "is the woman standing directly behind",\n'
        '              "is the large green-skinned orc of", "is the woman of"), "ck_top_species")',
        '    inmem("the orc slot written as a woman too (the figure default the item bars)", A46,\n'
        '          sub("a fictional adult aged 34 of a fictional humanoid orc species",\n'
        '              "a fictional adult aged 34, a woman of a fictional humanoid orc species"), "ck_top_species")'
    ),
    # 2: c1 beats back inside the old 3-pass windows
    (
        '    inmem("c1 beats left in the old 3-pass windows (00:05.2-00:09.9 s)", A46,\n'
        '          sub1("c1", "At 00:10.400", "At 00:05.400", "At 00:11.900", "At 00:07.400", "At 00:13.300",\n'
        '               "At 00:09.400", "At 00:14.600", "At 00:09.900"), "ck_top_beats")',
        '    inmem("c1 beats left in the old 3-pass windows (00:05.4-00:09.9 s, under the 10.125 s chunk start)", A46,\n'
        '          sub1("c1", "At 00:11.400", "At 00:05.400", "At 00:12.600", "At 00:07.400", "At 00:13.800",\n'
        '               "At 00:09.400", "At 00:14.700", "At 00:09.900"), "ck_top_beats")'
    ),
    # 3: beats down to 2
    (
        '    inmem("beats dropped to 2 (the guide\'s 3+ beats rule)", A46,\n'
        '          sub1("c0", "At 00:02.100", "Then", "At 00:04.300", "Next", "At 00:06.900", "After that"),\n'
        '          "ck_top_beats")',
        '    inmem("beats dropped to 2 (the guide\'s 3+ beats rule)", A46,\n'
        '          sub1("c0", "At 00:02.300", "Then", "At 00:04.400", "Next", "At 00:06.600", "After that"),\n'
        '          "ck_top_beats")'
    ),
    # 4: negation words in the prose
    (
        '    inmem("negation tokens written into the prose", A46,\n'
        '          sub1("c1", "At 00:10.400", "Nothing is hidden, and no motion is quick. At 00:10.400"), "ck_top_neg")',
        '    inmem("negation tokens written into the prose", A46,\n'
        '          sub1("c1", "At 00:11.400", "Nothing is hidden, and no motion is quick. At 00:11.400"), "ck_top_neg")'
    ),
    # 5: the STAGED take is the one that must cite the naming row (take B of GI046 is armed now)
    (
        '    onfile("staged take B manifest with the naming row stripped (the queue decision loses its citation)", B46,\n'
        '           "ck_top_manifest", man_naming, files=("man",))',
        '    onfile("staged take manifest with the naming row stripped (the queue decision loses its citation)", B63,\n'
        '           "ck_top_manifest", man_naming, files=("man",))'
    ),
    # 6: the card\'s opening pose written out of the c1 opening beat
    (
        '    inmem("the card\'s opening pose written out of the c1 opening beat", B46,\n'
        '          lambda gg: gg["c1"]["inputs"].__setitem__("prompt", gg["c1"]["inputs"]["prompt"].replace(\n'
        '              "At 00:10.400", "At 00:10.400 She rises to her feet and the orc stands. ", 1)), "ck_top_card")',
        '    inmem("the card\'s opening pose written out of the c1 opening beat (she stands, the orc lies down)", B46,\n'
        '          sub1("c1", "<Subject 1> on all fours on the rug, <Subject 2> kneeling behind her",\n'
        '               "<Subject 1> standing by the sofa, <Subject 2> lying on the rug"), "ck_top_card")'
    ),
    # 7: a status row that is not a row in the card ("OK" is a substring of ordinary card words)
    (
        '            "ck_top_facts", "GI046", facts_json(lambda d: d.__setitem__("status", "OK")))',
        '            "ck_top_facts", "GI046", facts_json(lambda d: d.__setitem__("status", "uncaptioned")))'
    ),
]

for old, new in PAIRS:
    n = src.count(old)
    assert n == 1, ("anchor count", n, old[:90])
    src = src.replace(old, new, 1)

open(P, "w", encoding="utf-8", newline="\n").write(src)
print("patched part 6: seeds re-anchored on the current prose")
