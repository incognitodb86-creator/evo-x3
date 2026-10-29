"""item 4 close-out (2026-10-29 08:24 CT): append the record lines to notes/actions.log and notes/progress.md.
Append-only, LF-terminated, ASCII only (same pattern as notes/item4_append_records.py)."""
from pathlib import Path

ACTIONS = Path(r"C:/AI/community/notes/actions.log")
PROGRESS = Path(r"C:/AI/community/notes/progress.md")

action_lines = [
    "2026-10-29 08:24 CT Pi (item 4 CLOSED, Derek 8:20 AM 'PROMPT.md is no longer protected. Finish item 4'): PROMPT.md item 1e now copies p7/graphs/default_b2_terrace_dom_q5guide_s51083007.api.json (the B2 default) and 1f renders --frames 243. Backups PROMPT.md.bak-20261029-item4-apply (sha256 62B6DE7863AEB6D9D6E3ED8DB74A7C7E87769F96B5E8792EC33D674EF018177B = the pre-edit file, hash-checked first) and the earlier .bak-20261029-item4-b2default (same bytes). Diff vs backup = exactly the 1e and 1f lines; the strings 'stock_base_tenstrip10' and '--frames 124' are gone from the 4,969 B file. All three pointers (PROMPT.md 1e/1f, fix_plan '## Stock path', skills/h3-hc-render/SKILL.md s2) now name the same graph. Commit ralph-community 872a5fe.",
    "2026-10-29 08:24 CT Pi (item 4 verify): notes/item4_verify_prompt_lines.py reads the LIVE PROMPT.md and tests its own claims against disk - target exists, 20,072 B, sha256 8d1d1a41e9915f2a3ef3f1350b65a4bf563f9607af7e3ed9538e4c9abae4695e, 26 nodes, byte-identical to runs/terrace_dom_q5guide_20261028_s51083007/request.api.json, --frames 243 == c0.length, and the frozen settings are in the file (beta7 int8HQ, 8 steps + simple, pass2 beta/3/0.4, shift 12/3, VSA keep_percent 10, AddGuide ag0+ag1, ref_image_size max, upscaler scale-by-multiplier 2.0, euler, fps 24). Youth guard untouched and re-proved after the edit: pytest -q scripts/tests/test_p6_review.py scripts/tests/test_guard_scope.py = 26 passed in 3.23 s. No render, no GPU job, no ComfyUI/llama-swap call.",
    "2026-10-29 08:24 CT Pi (item 4): fix_plan MAX item 4 ticked [x] with the evidence written inline in the line (bak fix_plan.md.bak-20261029-item4-tick); item 3's checkbox left exactly as Max wrote it. DONE note notes/2026-10-29-item4-b2-default-DONE.md updated with the close-out, the verification output and the guard re-run. B2 is now the default for new render runs; p7/graphs/stock_base_tenstrip10.api.json stays on disk unchanged for old ids.",
]

progress_line = (
    "- 2026-10-29 [MAX item 4 CLOSED, B2 = the default render setup] Derek 8:20 AM 'PROMPT.md is no longer protected ... Finish item 4', so the pointer that was policy-blocked in the 08:09 pass is applied: "
    "PROMPT.md item 1e copies `C:/AI/community/p7/graphs/default_b2_terrace_dom_q5guide_s51083007.api.json` (the B2 default = `runs/terrace_dom_q5guide_20261028_s51083007/request.api.json` byte-for-byte, 20,072 B, sha256 8d1d1a41e9915f2a3ef3f1350b65a4bf563f9607af7e3ed9538e4c9abae4695e, 26 nodes) and changes only LoadImage path, c0.prompt, noise_seed, filename_prefix; item 1f renders `--frames 243` because that number must equal c0.length (run_graph_job.py fails the objective gate when abs(frames - c0.length) > tol, so the old 124 against this graph = one paid window + 2 redos). "
    "Verified from the live file, not from prose: `notes/item4_verify_prompt_lines.py` extracts the path/frames/sha/bytes/nodes claims out of PROMPT.md lines 13-14 and tests them against disk - target exists, all claims match, byte-identical to B2's request, c0.length 243 == --frames 243, frozen settings present (beta7 int8HQ, euler + simple 8, pass2 [beta, 3, 0.4], shift [12.0, 3.0], VSA keep_percent 10, AddGuide ag0+ag1, ref_image_size max, LatentUpscaler3D scale-by-multiplier 2.0, fps 24), the strings 'stock_base_tenstrip10' and '--frames 124' are gone, and the diff vs the backup is exactly 2 lines in a 4,969 B file. "
    "Backups: PROMPT.md.bak-20261029-item4-apply (sha256 62B6DE7863AEB6D9D6E3ED8DB74A7C7E87769F96B5E8792EC33D674EF018177B, hash-checked before writing = the pre-edit state), PROMPT.md.bak-20261029-item4-b2default, fix_plan.md.bak-20261029-item4-tick, skills/h3-hc-render/SKILL.md.bak-20261029-b2default. fix_plan item 4 ticked [x] with the evidence inline; item 3's checkbox untouched (Max's). "
    "Youth guard never touched (no edit to scripts/comm.py, guard_ok, prompt_strings or the tests): pytest -q scripts/tests/test_p6_review.py scripts/tests/test_guard_scope.py = 26 passed in 3.84 s before the edit and 26 passed in 3.23 s after. "
    "GPU: 0 renders, 0 queue, 0 ComfyUI/llama-swap calls, gpu lock never taken. Commits: ralph-community 872a5fe (PROMPT.md + fix_plan.md only); this repo's commit carries the updated note notes/2026-10-29-item4-b2-default-DONE.md, notes/item4_verify_prompt_lines.py and this line, on top of 25b5303 which landed the default graph, the first pointer moves and the probes. Full record: notes/2026-10-29-item4-b2-default-DONE.md."
)

for p, lines in ((ACTIONS, action_lines), (PROGRESS, [progress_line])):
    raw = p.read_bytes()
    assert raw.endswith(b"\n"), f"{p} does not end with LF"
    add = "".join(l + "\n" for l in lines).encode("ascii")
    p.write_bytes(raw + add)
    print("appended %d line(s) to %s (+%d bytes)" % (len(lines), p, len(add)))
