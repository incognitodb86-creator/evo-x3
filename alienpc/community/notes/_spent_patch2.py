"""Part 2 of the spent-id plumbing: measure_top carries the render receipt, the notes state it, ck_top_arm
bars a spent id from the queue, and the take-B rule follows TOP_ORDER instead of hard-coded take B ids."""
P = r"C:/AI/community/notes/hc15_anchor_carry_build.py"
src = open(P, encoding="utf-8").read()

PAIRS = [
    # ---- ck_top_arm: data-driven take rule + a spent id can never be armed -------------------
    (
        '    """The handoff: p7/JOB_REQUEST.json carries take A of each named still as its own 6-key job row, in the\n'
        '    order Max\'s unblock row gave (GI046 then GI063). Take B stays staged and unarmed - disclosed, not hidden -\n'
        '    and the ledger has to absorb what is armed (5:52-5:53 PM CT rule: the plan\'s queue math must not overdraw\n'
        '    the standing cap)."""',
        '    """The handoff: p7/JOB_REQUEST.json carries the FREE take of each named still as its own 6-key job row,\n'
        '    in the order Max\'s unblock row gave (GI046 then GI063). The other take stays staged and unarmed -\n'
        '    disclosed, not hidden - and the ledger has to absorb what is armed (5:52-5:53 PM CT rule: the plan\'s\n'
        '    queue math must not overdraw the standing cap). A spent id (a video already in the ComfyUI output dir)\n'
        '    is never armed: the render row is a receipt, not a queue entry."""'
    ),
    (
        '        out.append(f"TOP-ARM jobs[] {ids} != take A of each named still {TOP_ORDER} (Max\'s order: GI046 first, "\n'
        '                   "GI063 second; take B is staged, not armed)")',
        '        out.append(f"TOP-ARM jobs[] {ids} != the free take of each named still {TOP_ORDER} (Max\'s order: "\n'
        '                   "GI046 first, GI063 second; the other take is staged, not armed)")'
    ),
    (
        '        if j.get("minutes") != TOP_EST_MIN:\n'
        '            out.append(f"TOP-ARM {j.get(\'id\')} minutes {j.get(\'minutes\')} != measured {TOP_EST_MIN}")',
        '        if j.get("minutes") != TOP_EST_MIN:\n'
        '            out.append(f"TOP-ARM {j.get(\'id\')} minutes {j.get(\'minutes\')} != measured {TOP_EST_MIN}")\n'
        '        rec = top_render_receipt(str(j.get("id")))\n'
        '        if rec:\n'
        '            out.append(f"TOP-ARM {j.get(\'id\')} is SPENT (video {rec[\'bytes\']} B sha {rec[\'sha256\'][:16]} "\n'
        '                       f"written {rec[\'written\']}) - a render receipt is not a queue entry; arm the free "\n'
        '                       f"take of that still")'
    ),
    (
        '    for nid in (TOP["GI046"]["take_b"], TOP["GI063"]["take_b"]):\n'
        '        if nid in json.dumps(req):\n'
        '            out.append(f"TOP-ARM take B {nid} armed; its minutes are not in the disclosed queue math")',
        '    for nid in [x for x in TOP_TAKES if x not in TOP_ORDER]:\n'
        '        if nid in json.dumps(req):\n'
        '            out.append(f"TOP-ARM the staged take {nid} is armed; its minutes are not in the disclosed "\n'
        '                       f"queue math (the armed set is {TOP_ORDER})")'
    ),
    # ---- measure_top: the render receipt ------------------------------------------------------
    (
        '        "static_scan_defects": 0, "graph_sha256": sha(gp), "graph_bytes": os.path.getsize(gp),\n'
        '        "run_dir_request_sha256": sha(rd) if os.path.isfile(rd) else None,\n'
        '        "budget_at_build": json.load(open(LEDGER, encoding="utf-8")), "est_min": TOP_EST_MIN,\n',
        '        "static_scan_defects": 0, "graph_sha256": sha(gp), "graph_bytes": os.path.getsize(gp),\n'
        '        "run_dir_request_sha256": sha(rd) if os.path.isfile(rd) else None,\n'
        '        "rendered": (dict(TOP_RENDERS[nid], **top_render_receipt(nid)) if nid in TOP_RENDERS\n'
        '                     and top_render_receipt(nid) else None),\n'
        '        "budget_at_build": json.load(open(LEDGER, encoding="utf-8")), "est_min": TOP_EST_MIN,\n'
    ),
    # ---- top_note: the id-free clause is data-driven, and the arm clause names the free takes --
    (
        '    armed = nid in [j.get("id") for j in (json.load(open(os.path.join(W, "p7", "JOB_REQUEST.json"),\n'
        '                                                        encoding="utf-8")).get("jobs", [])\n'
        '                                         if os.path.isfile(os.path.join(W, "p7", "JOB_REQUEST.json")) else [])]\n',
        '    armed = nid in [j.get("id") for j in (json.load(open(os.path.join(W, "p7", "JOB_REQUEST.json"),\n'
        '                                                        encoding="utf-8")).get("jobs", [])\n'
        '                                         if os.path.isfile(os.path.join(W, "p7", "JOB_REQUEST.json")) else [])]\n'
        '    rec = top_render_receipt(nid)\n'
        '    idf = ("id-free: no mp4, 0 result.json, no ComfyUI output dir, no GPU call in this pass."\n'
        '           if not rec else\n'
        '           "id SPENT: %s, %d B, sha256 %s, written %s, and the run-dir status.log ends in poll-warn "\n'
        '           "timeouts with 0 result.json: the id is spent by file evidence. %s This prose record has 0 "\n'
        '           "renders of this still, so the free take carries it. No GPU call in this pass."\n'
        '           % (os.path.basename(rec["file"]), rec["bytes"], rec["sha256"][:16], rec["written"],\n'
        '              TOP_RENDERS.get(nid, {}).get("prose", "")))\n'
    ),
    (
        '        "prompt-bearing strings, scripts/tests/test_p6_review.py 21 passed. id-free: no mp4, 0 result.json, no "\n'
        '        "ComfyUI output dir, no GPU call in this pass. minutes=%d (clip 1-6 measured 24.0 min/job +25%% "\n'
        '        "contingency). Receipts: notes/hc15_anchor_carry_build.py --top-check / --top-selftest. Arm: %s (take A of "\n'
        '        "each still armed, take B staged; ledger %s/%s min, %s/%s jobs, stamp %s). "\n',
        '        "prompt-bearing strings, scripts/tests/test_p6_review.py 21 passed. %s minutes=%d (clip 1-6 measured "\n'
        '        "24.0 min/job +25%% contingency). Receipts: notes/hc15_anchor_carry_build.py --top-check / "\n'
        '        "--top-selftest. Arm: %s (the free take of each still armed in Max\'s row-18 order, the other take "\n'
        '        "staged; ledger %s/%s min, %s/%s jobs, stamp %s). "\n'
    ),
    (
        '         m["gate_ok_all_prose"], len(f["ps"]), TOP_EST_MIN, "armed" if armed else "staged",\n',
        '         m["gate_ok_all_prose"], len(f["ps"]), idf, TOP_EST_MIN, "armed" if armed else "staged",\n'
    ),
    # ---- top_request_note: names the armed free ids and the spent take -----------------------
    (
        '        "TOP (fix_plan TOP): the two named HC15 stills rendered with species-accurate prose on the fixed clip-1 "\n'
        '        "shape, take A of each, GI046 (the orc) then GI063 (the robot) in Max\'s 2026-10-24 9:30 PM CT order "\n'
        '        "(notes/needs_derrick.md row 18). Each job is its own 6-key row, frames 362 (15.083333 s), 30 min each, "\n'
        '        "ledger %s/%s min and %s/%s jobs before the render. Take B of each still is staged (graph, run-dir request, "\n'
        '        "manifest) and unarmed: arming 4 jobs = 120 min over the standing cap. This arm displaces the single-job "\n',
        '        "TOP (fix_plan TOP): the two named HC15 stills rendered with card-faithful prose on the fixed clip-1 "\n'
        '        "shape, GI046 (the orc) then GI063 (the robot) in Max\'s 2026-10-24 9:30 PM CT order "\n'
        '        "(notes/needs_derrick.md row 18). Each job is its own 6-key row, frames 362 (15.083333 s), 30 min each, "\n'
        '        "ledger %s/%s min and %s/%s jobs before the render. The armed ids are the FREE take of each still: "\n'
        '        "ali163_hc15_gi046_s51150031 is spent (its mp4 is in the ComfyUI output dir, rendered 2026-10-25 04:04 "\n'
        '        "off the pre-card-fidelity prose, receipt in its manifest and notes/needs_derrick.md row 25), so the "\n'
        '        "GI046 slot is take B. The other take of each still is staged (graph, run-dir request, manifest) and "\n'
        '        "unarmed: arming 4 jobs = 120 min over the standing cap. This arm displaces the single-job "\n'
    ),
]

for old, new in PAIRS:
    n = src.count(old)
    assert n == 1, ("anchor count", n, old[:90])
    src = src.replace(old, new, 1)

open(P, "w", encoding="utf-8", newline="\n").write(src)
print("patched part 2")
