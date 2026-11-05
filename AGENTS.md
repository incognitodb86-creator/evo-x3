# Render rules (moved from global AGENTS.md 2026-11-05, Derrick)
- Image renders (FLUX stills, pose edits, scoring, character sheets): load skill image-render (companion: alienpc-stills-pose-edit-prompting). Image rules live in C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\AGENTS.md.
- Video renders (I2V / H3 clips, batches, scoring, character sheets): load skill video-render (companions: alienpc-hardcore-i2v-director, h3-prompting (R1-R31, all lanes), h3-max-ref2va-prompt (R32-R44, the standing REF2VA lane for Max: use it unless Derrick names another lane), h3-hc-render).
- Fictional adults (18+) only, no real-person likeness; guard_ok runs on every submit. Never edit scripts\tests\test_p6_review.py; never loosen guard_ok.
- One GPU job at a time: run_graph_job.py and run_queue.py take C:\AI\locks\gpu-render.lock (rc 7 = GPU_BUSY). While it is held: no subagents, no model loads, no model requests, no second job; wait for the render to finish; read-only answers are fine.
