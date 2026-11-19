"""Part 4: two gate rules the new seeds need - a consent gate has to state wording it requires, and the note of
a spent take has to state which prose ran and that the current record has 0 renders of that still."""
P = r"C:/AI/community/notes/hc15_anchor_carry_build.py"
src = open(P, encoding="utf-8").read()

PAIRS = [
    (
        '    for k in ("model", "status", "sha256"):\n'
        '        if card_norm(f[k]) not in md:\n'
        '            bad.append("F-FACTS-%s: \'%s\' is not a row in the card" % (k.upper(), f[k]))\n',
        '    cg = gt.get("consent_gate") or {}\n'
        '    if cg.get("ban") and not [x for x in (cg.get("require") or []) if str(x).strip()]:\n'
        '        bad.append("F-FACTS-CONSENT: the consent gate bars %d phrases and requires none, so prose can "\n'
        '                   "never satisfy it: a ban with no required wording is a gate that only blocks" % len(cg["ban"]))\n'
        '    for k in ("model", "status", "sha256"):\n'
        '        if card_norm(f[k]) not in md:\n'
        '            bad.append("F-FACTS-%s: \'%s\' is not a row in the card" % (k.upper(), f[k]))\n'
    ),
    (
        '        if str(rec["bytes"]) not in note_of(m):\n'
        '            out.append("TOP-MANIFEST note does not quote the spent render (mp4 bytes) the manifest carries")\n',
        '        if str(rec["bytes"]) not in note_of(m):\n'
        '            out.append("TOP-MANIFEST note does not quote the spent render (mp4 bytes) the manifest carries")\n'
        '        pn = TOP_RENDERS.get(ctx["id"], {}).get("prose", "")\n'
        '        if pn and pn.split(":")[0] not in note_of(m):\n'
        '            out.append("TOP-MANIFEST note of a spent take must say which prose the render ran (the "\n'
        '                       "before/after rule: a reader must not take the mp4 for the current record)")\n'
        '        if "0 renders" not in note_of(m):\n'
        '            out.append("TOP-MANIFEST note of a spent take must state that the current prose record has 0 "\n'
        '                       "renders of this still, and which take carries it")\n'
    ),
]

for old, new in PAIRS:
    n = src.count(old)
    assert n == 1, ("anchor count", n, old[:90])
    src = src.replace(old, new, 1)

open(P, "w", encoding="utf-8", newline="\n").write(src)
print("patched part 4")
