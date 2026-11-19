# ALI-147 PV2-2 tick + completion line (idempotent). Writes ONLY ralph-community\TASKS.md, which is
# in this task's writable list. No GPU/ComfyUI/llama-swap/Strata/render call.
import os

P = r"C:/Users/derek/5slock/ralph-community/TASKS.md"
RAW = open(P, "rb").read()
KEEP = RAW.splitlines(keepends=True)          # keeps each line's own terminator (the file is mixed)
START = b"- [ ] PV2-2 PROMPT_V2_SEG3"
TICKED = b"- [x] PV2-2 PROMPT_V2_SEG3"
ID = "ali147_pool_promptv2_seg3_s51080002"

COMPLETED = (
    "  - Completed: 2026-10-23T04:33:18Z, Derek-approved. VERIFIED (no render by Forge: the harness ran the job at iter 10 exit; "
    "this iteration made no p7 request and called no GPU, ComfyUI, node list, llama-swap, Strata, run_graph_job.py, batch_queue, "
    "contact-sheet build, vision judge, download, install, deletion, model/node change; read-only probe notes\\ali147_pv22_verify.py "
    "-> notes\\ali147-pv22-verify-20261022.txt, 20,240 B, ends ALL CHECKS PASS). result.json rc=0 ok=true wall 14.5 min "
    "(started 2026-10-22T23:12:00 finished 23:26:28 CT); status.log quoted in full in PROOF.md: \"2026-10-22 23:26:27 CT JOB end "
    + ID + " ok secs=837.7\", and every grep of error|SKIP|redo|STUCK|clip_skip|blocked|node_errors|Traceback|STATIC_FAIL|COMFY_DOWN "
    "on that log = 0 hits (the file is 5 lines, all quoted); <id>.api.json BYTE-IDENTICAL to request.api.json (12,569 B sha256 "
    "935622324ad136b1c970963c5c1331143677717e39c33d5c62bdbb19f0492fe2 on both sides) = the rendered graph is the graph Forge built; "
    "ffprobe -count_packets on <id>.mp4 = 481 packets 768x1344 24/1 + one aac 32000 Hz stereo audio stream, format duration "
    "20.041688 s (informational), 5,654,344 B = objective.json and the request's frames 481 / frames_tol 0, counted from packets and "
    "never from format=duration; objective.json ok=true attempts=1 (no REDO line, no STUCK, no *_redo* graph) blackfreeze [] "
    "reproduced by re-running the harness's own blackdetect+freezedetect chain (0 events) and by stricter probes (blackdetect d=0.2, "
    "freezedetect n=0.005 d=0.5) = 0 events, no black/frozen frames; mp4 sha256 "
    "f58198551261f1beb7ac555703f2a578440110497bf532682e4d3766052ea788, contact sheet 1,721,133 B sha256 "
    "2a3762ab13139662acb88f6ded88b2f1d028fd1c2dafdb43147e7787a5a81879 with PIL (1816, 900) = exactly the geometry "
    "run_graph_job.py:contact_sheet produces for 10 tiles of a 20.041688 s clip (grid 7x2, tile 256x448, padding 4), sampling "
    "t 8.5-11.5 s and 18.5-19.5 s = frames 204/216/228/240/252/264/276 + 444/456/468, so frame 243 falls inside the sampled window "
    "and 200/300/400/480/0 are never sampled by it. P0 = P1 = P2 = P3 BY HASH: the base seg3 graph prompts 3354 ch "
    "8ed332629e80a8702f11eb4eb996e5a42fe3ee5f716168d25512ae01d7df5d76 and 2269 ch "
    "dcd574692f426508d5ed5703cda68080ad7e9b1e8b4a49c0da3b049fd4b45d89 equal the base run's own prompt sidecars after CRLF-fold + "
    "rstrip; the two PROMPT_V2 files (v2_seg3_c0_r2v.txt 4358 chars ad77122b96f4ad474a6329a72b556f3372a80cb010e68a6c3ea10fe48a53763b, "
    "v2_seg3_c1_t2va.txt 2903 chars 2e3905ee2272a9d7ff0ab47d5db1765e4fa456ba4aa5ae2798e3fac404cfb383, both matching SHA256SUMS.txt) "
    "appear VERBATIM in the rendered graph, so the delta is the only variable; run_graph_job.py writes no prompt sidecar dir for a p7 "
    "graph job, so P3 closes through the byte-identical <id>.api.json (documented in PROOF.md). Fairness re-proved at verify: 22/25 "
    "nodes byte-identical, differing node set exactly ['c0','c1','save'], changed inputs exactly prompt / prompt / filename_prefix; "
    "graph_diff.txt 13,806 B sha256 1d9cd4dee53e5b6c792a44150ffd50edf793934bd20f1639178140f064b091b7 = 3 hunks and exactly 3 removed "
    "+ 3 added lines at control line indices 100/183/343 with the line count unchanged 349/349; seed 51080002 in an identical noise "
    "node (the base run's own seg3 seed), c0.length 243 + win1.extension_frames 238 = 481 (the control's own budget), m_attn "
    "(attention = \"comfy kitchen attention\", read from the file, not asserted from an enum), m_vsa, m_shift, s0_sched/s1_sched "
    "steps 10 simple denoise 1.0, ksel euler, app1 context_frames 22, img LoadImage string, checkpoint/CLIP/VAE loader strings all "
    "IDENTICAL; the LoadImage string resolves inside ComfyUI\\input at the measured 64-hex "
    "9cf9ff95f2d6f2fb3882219a8d98995b673e78a80001d7a41af1755cc918d075 (1,354,030 B); comm.guard_ok (the harness's own adults-only "
    "check, run_graph_job.py:60) passes on both rendered prompts and only c0/c1 carry prompt strings; every character is a fictional "
    "adult 21+ per plans/canon/fiction-cond-lock.md, no minors. CONTROL measured as a valid 481/768x1344/24 fps/audio pair: "
    "p7_r2_c3_pmot_full_pool_seg3.mp4 481 packets, 5,624,126 B, sha256 "
    "fc28701abc585f3ae052b9316df22ba4edf7f31a2f3c685d2bbd758d2191d053, sidecar secs 816.0 seed 51080002, so the pair delta is "
    "+21.7 s (+2.66 %) render time and +30,218 B (+0.54 %); other 481-frame renders CTRL 809.7 s and PV2-1 827.7 s. p7_budget.json "
    "after the job {\"used_min\": 356.5, \"jobs\": 25, \"cap_min\": 390, \"job_cap\": 27} = 33.5 min and 2 jobs of headroom, and the "
    "14.5 min job cost matches the control's 13.6 min. sbs/stills pending Max: find runs -name sbs_*.mp4 = 0 results and "
    "run_graph_job.py has no hstack path and no fixed-frame still path, so sbs_base_seg3_promptv2.mp4 (base stitched frames 962-1442, "
    "measured 1443 packets sha256 ae93a7477aefc5ef698de0ac71d45e13f29731732ce3a0c832ac8360acda581d, vs new frames 0-480) and the "
    "full-res stills at 200/243/300/400/480 do not exist and are Max's files, not Forge's; the contact sheet cannot supply "
    "200/300/400/480. PROOF.md (runs\\" + ID + "\\PROOF.md) PENDING ledger closed item by item + a \"Render verify\" section with the "
    "verbatim status.log and the arm-vs-control table; fairness.txt unchanged from iter 07. No quality judgement, no vision judge, no "
    "by-eye claim, no inferred counts; METHOD_ONLY, KEEP is Derek's."
)

i = [n for n, x in enumerate(KEEP) if x.startswith(START)]
assert len(i) == 1, ("PV2-2 task line not found exactly once", i)
n = i[0]
print("task line index", n, "len", len(KEEP[n]))
assert b"PROMPT_V2_SEG3" in KEEP[n]
j = n + 1
while j < len(KEEP) and KEEP[j].startswith(b"  - "):
    j += 1
block = KEEP[n + 1:j]
print("sub-lines", len(block), "->", [x[:40] for x in block])
assert len(block) >= 4, "the sub-line block is unexpectedly short"
assert not any(b"Completed:" in x for x in block), "a Completed line already exists (idempotency guard)"
assert not any(x.startswith(b"- [ ]") for x in block), "a sub-line is itself a task line"

eol = b"\r\n" if KEEP[j - 1].endswith(b"\r\n") else b"\n"      # match the last sub-line's terminator
new = KEEP[:]
new[n] = TICKED + KEEP[n][len(START):]
assert new[n].startswith(TICKED) and new[n][len(TICKED):len(TICKED) + 1] == b" ", "tick failed"
new.insert(j, COMPLETED.encode("utf-8") + eol)
out = b"".join(new)
assert out.count(b"- [x] PV2-2 PROMPT_V2_SEG3") == 1 and out.count(b"- [ ] PV2-2 PROMPT_V2_SEG3") == 0
assert out.count(b"PV2-2 PROMPT_V2_SEG3") == 1, "the task name must appear exactly once"
assert out.count(b"Completed: 2026-10-23T04:33:18Z") == 1
assert out.count(b"\n") == RAW.count(b"\n") + 1, "exactly one new line"
assert out.replace(b"- [x] PV2-2", b"- [ ] PV2-2").replace(COMPLETED.encode("utf-8") + eol, b"") == RAW, "byte-exact minimal change"
print("newline shape: total \\n %d, \\r\\n %d (unchanged shape apart from the inserted %r)" % (RAW.count(b"\n"), RAW.count(b"\r\n"), eol))
open(P, "wb").write(out)
print("TASKS.md %d B -> %d B, lines %d -> %d, delta %d B" % (len(RAW), len(out), len(KEEP), len(new), len(out) - len(RAW)))
print("PV2-2 ticked at line %d, completion line inserted as line %d (1-based)" % (n + 1, j + 1))
