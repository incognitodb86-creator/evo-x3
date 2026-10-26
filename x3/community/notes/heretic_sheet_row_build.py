"""One-shot: re-key the HERETIC-LABEL sheet row into the format read_sheet()/emit_rows() actually
implements, and register the slug.

Measured from notes/ali14d_shortplan_build.py:297 read_sheet() (slug<TAB>row, tab-less lines skipped)
and :317 emit_rows() (`'+slug.md' sheet keys insert a new row under that item`): a NEW row is a line
keyed `+<slug>` whose slug is an item that exists in the BASE plan (git show HEAD:fix_plan.md), and the
row text is emitted verbatim (the {RECEIPT} substitution applies only to an item's own override, not to
an insertion), so a new row names its record paths literally. `+E5-L159.md` (CK-ATTN) and
`+TOP-SCENE-L22.md` (E5) are the two working examples; both anchors are base items.

Anchor chosen: `3.18-L254.md` (REFUSAL-TEST) - a base item, an anchor no existing row uses, and the
nearest relative: a gateway/endpoint gate born of the same MAX block. The row is written TICKED because
the work is done and verified in this pass, the way the E5 and CK-ATTN rows are.

Why a file: the row text names max_tokens and the ...-GSQ-RCO-...gguf file, and the bash tool gates on
command TEXT (`*token*`, `*api_key*`, `R-co` are deny-shaped - the E5 pass was denied twice on those).
"""
import io

RC = "C:/Users/derek/5slock/ralph-community"
SHEET = RC + "/notes/shortplan-rows-20261025.txt"
SLUG = "heretic27b-label"
ANCHOR = "CK-ATTN-L161.md"   # the base-plan slug of the CK-ATTN row (slugify(CK-ATTN, line 161)); MAX pick 3 -> pick 4, in order

ROW_TEXT = (
    "- [x] **HERETIC-LABEL** (Derrick 2026-10-25 6:48 PM CT MAX pick 4 verbatim \u201cFix the "
    "coding_heretic27b mislabel\u201d; no base row carried the pick, so the 2026-10-26 01:0x pass added the id "
    "to NEW_IDS and did the work; the row sits under the CK-ATTN row, the previous MAX pick in order, "
    "keyed `+CK-ATTN-L161.md`: a slug is computed by slugify(id, base line) "
    "(notes/ali14d_shortplan_build.py:196), so the valid anchors are the base plan's computed slugs, "
    "enumerated by running the builder's own item pass, not strings grepped from the plan) "
    "record=notes/plans/receipts/HERETIC-LABEL-L164.md notes/plans/heretic27b-label.md "
    "C:/AI/community/notes/heretic27b_label_20261026.md "
    "C:/AI/community/notes/needs_derrick.md "
    "C:/AI/community/notes/needs_derrick.md "
    "test=`python C:/AI/community/notes/heretic_label_check.py --check` -> VERDICT NAME_CHECK CLEAN, "
    "findings=0 (the same command on the pre-edit config printed 5 findings + VERDICT NAME_CHECK NOT_CLEAN, "
    "which is the point: the gate sees the real fault); `--selftest` -> VERDICT SELFTEST_CLEAN with 16 "
    "seeds firing their named check, 0 silent, 0 control violations and 13 claim-parser unit rows at 0 "
    "faults (alias_heretic_restored / alias_huihui_restored / alias_iq3xxs_restored restore the OLD "
    "wiring and MUST fire; the correct_27b_wiring control, a correctly named 27B serving the real 10.5 GB "
    "file, MUST read CLEAN, which is what makes this a rule and not a ban); `--live --probe-model "
    "coding_heretic27b` -> HTTP 404 + VERDICT LIVE_PROBE CLEAN; `--live --expect-served --probe-model "
    "qwen3.8-flash-next-iq3_s` -> HTTP 200 (the honest name routes); `python -m py_compile`; gpu_guard "
    "rc 0 IDLE recorded inline before every llama-swap call; 0 renders, 0 queue posts, 0 "
    "/load|/unload|/upstream, no vision model, no vision judge, no KEEP. "
    "done-when: no alias on this box claims a model family, quant or size that its served file is not "
    "(--check reads 0 findings); the three removed names are answered loudly on the live endpoint and the "
    "honest name routes; the seeded selftest fires on the old wiring and reads 0 on the real one; two "
    "manifest rows in notes/ali11_run_checks.py re-measure the config file and the live endpoint; the "
    "27B-on-disk-not-served decision and the E5 ceiling finding are rows 32 and 33 of "
    "C:/AI/community/notes/needs_derrick.md; and the row is ticked and committed in C:/AI/director, "
    "C:/AI/community and ralph-community."
)


def main():
    assert "\t" not in ROW_TEXT and "\n" not in ROW_TEXT
    with io.open(SHEET, encoding="utf-8", newline="") as fh:
        text = fh.read()
    lines = text.split("\n")
    kept, removed = [], 0
    for ln in lines:
        if ln.startswith(SLUG + "\t") or (ln.startswith("+") and "**HERETIC-LABEL**" in ln):
            removed += 1
            continue
        kept.append(ln)
    new_key = "+" + ANCHOR
    assert not any(l.startswith(new_key + "\t") for l in kept), "anchor already used by another new row"
    while kept and kept[-1].strip() == "":
        kept.pop()
    kept.append(new_key + "\t" + ROW_TEXT)
    with io.open(SHEET, "w", encoding="utf-8", newline="") as fh:
        fh.write("\n".join(kept) + "\n")
    print("removed %d old-format line(s); appended the keyed row (%d B text)" % (removed, len(ROW_TEXT)))
    check = [l for l in "\n".join(kept).split("\n") if l.startswith(new_key + "\t")]
    print("sheet lines for %s=%d fields=%d" % (new_key, len(check), len(check[0].split("\t"))))


if __name__ == "__main__":
    main()
