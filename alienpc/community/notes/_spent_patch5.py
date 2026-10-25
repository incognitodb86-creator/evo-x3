"""Part 5: the spent-take note fits the plan's 1100-2200 manifest-note ceiling, and the render row's selection
sentence carries no judgement token (BANNED_IN_MANIFEST: keep/best/pick/winner/preference/favoured/favorite)."""
P = r"C:/AI/community/notes/hc15_anchor_carry_build.py"
src = open(P, encoding="utf-8").read()

PAIRS = [
    # judgement-token-safe selection sentence in the declared render row
    (
        '    "keep": "KEEP is Derrick\'s alone; no vision judge, no score, no keep by the forge",',
        '    "select": "the selection is Derrick\'s alone; no vision judge, no score, no choice by the forge",'
    ),
    (
        '        if isinstance(mr, dict) and not str(mr.get("keep", "")).strip():\n'
        '            out.append("TOP-MANIFEST render receipt must state that KEEP is Derrick\'s alone")',
        '        if isinstance(mr, dict) and "Derrick\'s alone" not in str(mr.get("select", "")):\n'
        '            out.append("TOP-MANIFEST render receipt must state that the selection of a rendered take is "\n'
        '                       "Derrick\'s alone (a forge render row never keeps, scores, or chooses)")'
    ),
    # the spent-take note: short, and it carries the required fragments
    (
        '           "id SPENT: %s, %d B, sha256 %s, written %s, and the run-dir status.log ends in poll-warn "\n'
        '           "timeouts with 0 result.json: the id is spent by file evidence. %s This prose record has 0 "\n'
        '           "renders of this still, so the free take carries it. No GPU call in this pass."\n'
        '           % (os.path.basename(rec["file"]), rec["bytes"], rec["sha256"][:16], rec["written"],\n'
        '              TOP_RENDERS.get(nid, {}).get("prose", "")))\n',
        '           "id SPENT: %s %d B sha256 %s written %s, off the shipped pre-card-fidelity prose; 0 result.json, "\n'
        '           "no GPU call in this pass; this prose record has 0 renders of this still, so the free take "\n'
        '           "carries it."\n'
        '           % (os.path.basename(rec["file"]), rec["bytes"], rec["sha256"][:16], rec["written"]))\n'
    ),
    # note trims to stay inside 1100-2200 on a spent take too
    (
        '        "intact, 2 SamplerCustomAdvanced, 0 cfg keys, ref slots + LoadImage untouched. Prose from "\n'
        '        "%s byte-for-byte: c0 detailed_description %d words / %d beats in "\n'
        '        "%.3f-%.3f s, c1 integrated_multimodal_description %d words / %d beats in %.3f-%.3f s, %d prohibition/negation "\n'
        '        "tokens, ages %s stated as fictional adults, species words %s present in %d/%d chunks, default-figure clauses "\n'
        '        "%d (the defect %s rows 2-3: \'the only person in that photograph\'). "\n'
        '        "Structure = %s + TenStrip card notes/web/hc15_tenstrip_readme.txt. "',
        '        "intact, 2 SamplerCustomAdvanced, 0 cfg keys, ref slots + LoadImage untouched. Prose from "\n'
        '        "%s byte-for-byte: c0 detailed_description %d words / %d beats "\n'
        '        "%.3f-%.3fs, c1 integrated_multimodal_description %d words / %d beats %.3f-%.3fs, %d prohibition/negation "\n'
        '        "tokens, ages %s fictional, species words %s present in %d/%d chunks, default-figure clauses "\n'
        '        "%d (defect %s rows 2-3). "\n'
        '        "Structure = %s + TenStrip card. "'
    ),
    (
        '        "contingency). Receipts: notes/hc15_anchor_carry_build.py --top-check / "\n'
        '        "--top-selftest. Arm: %s (the free take of each still armed in Max\'s row-18 order, the other take "\n'
        '        "staged; ledger %s/%s min, %s/%s jobs, stamp %s). "',
        '        "contingency). Receipts: --top-check / --top-selftest. Arm: %s (free take of each still, Max\'s "\n'
        '        "row-18 order, the other staged; ledger %s/%s min, %s/%s jobs, stamp %s). "'
    ),
    (
        '        "paths vs the carried source %s only: MiniMaxH3AddGuide frame_idx 0 on the c0 edge, "\n'
        '        "res_multistep/simple/8, c0 length 243 + one 119-frame window = %d f at 24 fps = %.6f s, 1344x768, audio "',
        '        "paths vs the carried source %s only: MiniMaxH3AddGuide frame_idx 0 on the c0 edge, "\n'
        '        "res_multistep/simple/8, 243 + a 119-frame window = %d f at 24 fps %.6f s, 1344x768, audio "'
    ),
]

for old, new in PAIRS:
    n = src.count(old)
    assert n == 1, ("anchor count", n, old[:90])
    src = src.replace(old, new, 1)

open(P, "w", encoding="utf-8", newline="\n").write(src)
print("patched part 5")
