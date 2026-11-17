"""item 4 (2026-10-29): append the record lines to notes/actions.log and notes/progress.md.
Append-only, LF-terminated, ASCII only (actions.log is ASCII, last byte LF)."""
from pathlib import Path

ACTIONS = Path(r"C:/AI/community/notes/actions.log")
PROGRESS = Path(r"C:/AI/community/notes/progress.md")

action_lines = [
    "2026-10-29 08:09 CT Pi (Max block item 4): B2 (runs/terrace_dom_q5guide_20261028_s51083007) made the default render setup - new p7/graphs/default_b2_terrace_dom_q5guide_s51083007.api.json = B2 request.api.json byte-for-byte (20072 B, sha256 8d1d1a41e9915f2a3ef3f1350b65a4bf563f9607af7e3ed9538e4c9abae4695e, 26 nodes, beta7 int8HQ, euler/simple 8 steps full schedule + pass 2 beta/3/0.4, shift 12/3, VSA keep_percent 10, AddGuide frame 0 both passes, ref_image_size max, 384x672 -> LatentUpscaler3D x2 -> 768x1344, 243 f, 24 fps). No render, no GPU job, no ComfyUI call.",
    "2026-10-29 08:09 CT Pi (item 4): fix_plan.md '## Stock path' now points at that graph and --frames 243 (it named ali163_top5_gi046_s51160001.api.json + --frames 124); bak fix_plan.md.bak-20261029-item4-stockpath. skills/h3-hc-render/SKILL.md s2 'Base graph' names the B2 default and marks runs/ali147_pool_promptv2_s51080000 and p7/graphs/stock_base_tenstrip10.api.json superseded for new runs; bak SKILL.md.bak-20261029-b2default. stock_base_tenstrip10.api.json kept on disk for old ids. MAX block text untouched.",
    "2026-10-29 08:09 CT Pi (item 4) BLOCKED, not closed: PROMPT.md item 1e/1f is the pointer the Ralph loop actually reads (ralph.ps1 runs pi @PROMPT.md) and PROMPT.md is a protected path - edit denied by policy (matched 'edit:C:/Users/derek/5slock/ralph-community/PROMPT.md'). Paste-ready 1e/1f replacement text is in notes/2026-10-29-item4-b2-default-DONE.md; --frames 243 is required there because run_graph_job.py fails the objective gate when abs(frames - c0.length) > tol. Item 4 checkbox left unticked for Max.",
    "2026-10-29 08:09 CT Pi (item 4): youth guard unchanged - scripts/comm.py, guard_ok, prompt_strings and the tests not edited; proof pytest -q scripts/tests/test_p6_review.py scripts/tests/test_guard_scope.py = 26 passed in 3.84 s (CPU only). The beta7 UNET + shift 12 diff on comm.py in git status is pre-existing (2026-10-28, comm.py.bak-20261028-1330-b7default) and matches B2's graph.",
]

progress_line = (
    "- 2026-10-29 [MAX item 4, B2 = default render setup, one pointer BLOCKED] Derrick 6:59 AM CT 'Ok let's keep the b2 setup and make it default'. "
    "Made `p7/graphs/default_b2_terrace_dom_q5guide_s51083007.api.json` = `runs/terrace_dom_q5guide_20261028_s51083007/request.api.json` copied byte-for-byte "
    "(verified equal: 20,072 B, sha256 8d1d1a41e9915f2a3ef3f1350b65a4bf563f9607af7e3ed9538e4c9abae4695e, 26 nodes, JSON parses; the paid B2 render in that dir is objective ok 243 f 768x1344 24/1 audio 240.1 s). "
    "Settings read out of the file, not from prose: beta7 int8HQ + qwen3vl_32b nvfp4_awq CLIP + int8_convrot video VAE + fp32 audio VAE, euler/simple 8 steps on the FULL schedule, pass 2 BasicScheduler(beta, 3, denoise 0.4), shift 12.0/3.0, VSA keep_percent 10, MiniMaxH3AddGuide frame 0 (start image, vae wired) before both guiders, c0.ref_image_size max, one ref slot, MinimaxH3LatentUpscaler3D 'scale by multiplier' 2.0 (384x672 -> 768x1344) with enable_temporal_chunking true, audio decoded from the pass-1 latent, c0.length 243, fps 24. "
    "Pointers moved: fix_plan.md '## Stock path' (was ali163_top5_gi046_s51160001.api.json + --frames 124) and `skills/h3-hc-render/SKILL.md` s2 Base graph (was runs/ali147_pool_promptv2_s51080000); backups fix_plan.md.bak-20261029-item4-stockpath, SKILL.md.bak-20261029-b2default. "
    "Old default `p7/graphs/stock_base_tenstrip10.api.json` (beta6 int8, 124 f, 1344x768, single-pass, 10 steps, shift 10/3 - measured by notes/item4_b2_default_probe.py) stays on disk, unchanged, for reproducing those ids. "
    "BLOCKED: the live pointer is PROMPT.md item 1e/1f and PROMPT.md is a protected path for this agent (edit denied: matched 'edit:C:/Users/derek/5slock/ralph-community/PROMPT.md'); paste-ready replacement lines are in notes/2026-10-29-item4-b2-default-DONE.md for Max, and `--frames 243` in 1f is not cosmetic - run_graph_job.py fails the objective gate on abs(frames - c0.length) > tol, so a 243-frame default requested with --frames 124 burns a paid window plus 2 redos. "
    "Youth guard untouched and proven: pytest -q scripts/tests/test_p6_review.py scripts/tests/test_guard_scope.py = 26 passed in 3.84 s (CPU only); no edit to scripts/comm.py (its beta7 UNET/shift diff is pre-existing 2026-10-28). "
    "GPU: 0 renders, 0 queue, 0 ComfyUI/llama-swap calls, gpu lock never taken. Full record: notes/2026-10-29-item4-b2-default-DONE.md, probes notes/item4_b2_default_probe.py + notes/item4_b2_default_verify.py."
)

for p, lines in ((ACTIONS, action_lines), (PROGRESS, [progress_line])):
    raw = p.read_bytes()
    assert raw.endswith(b"\n"), f"{p} does not end with LF, append shape unknown"
    add = "".join(l + "\n" for l in lines).encode("ascii")
    p.write_bytes(raw + add)
    print("appended %d line(s) to %s (+%d bytes)" % (len(lines), p, len(add)))
