# Forge brief 5 - render terrace v2 (Max2, 2026-10-30 5:30 AM CT)
Derrick 4:56 AM: "Update the prompt rerun and score". Max read the full B2v2 prompt (sha256 e202e512...) and the v2 diff table: PASS. Subject 2 is clearly willing and enjoying it, both women 18+, no resistance language left; still, framing, beats and settings unchanged; S8 = B2v2 + the #74 line.

1. Render the 14 v2 arms in runs/terrace_retest_v2_20261030 (b2 x3 seeds, s1-s8 on 51083002, t4c x3) one at a time, same rules as brief3: pre-render pytest (scripts/tests/test_p6_review.py + test_guard_scope.py) and comm.guard_ok before each render, gpu_guard IDLE + C:/AI/locks/gpu-render.lock, run_graph_job.py --frames 124, one unchanged retry on failure then drop + log. t4g stays built and NOT rendered.
2. Judges flag-only per clip (prechecks, vlm_judge, vlm_variants --variants Z); T4c judged on its _raw. No scoring by Forge; Max scores.
3. Blind pack like last night: neutral ids in review/terrace-retest-v2-2026-10-30/pack + key.csv, upload to QNAP /pi-drop/terrace-retest-v2-2026-10-30 with the key at /pi-drop/terrace-retest-v2-2026-10-30-key.csv.
4. Write notes/2026-10-30-terrace-retest-v2-DONE.md, log a DONE line in actions.log, release the lock and go idle. Never kill llama-swap, strata or the pi-mobile hub.
