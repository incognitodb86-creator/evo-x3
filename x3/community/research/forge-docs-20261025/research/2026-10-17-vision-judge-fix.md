# Vision judge fix — 2026-10-17
Model research is deferred. The 7:48 AM CT steer said to debug the harness first, and the harness is defective: answer-first schema, rubric missing the defects, leading strip prompt, fail-open scorer.
See /workspace/cos/audits/2026-10-17-judge-harness-debug.md for root cause, evidence, the proposed patch and the J1 run steps (J1 = one yes/no logprob question per check, candidate alone except face, preflight pixel check, fail-closed, 18-item manifest, bar ≥17/18 + 0 false passes).
Resume model research (16 GB VRAM: Qwen3-VL-30B-A3B abliterated, Gemma 3 27B abliterated, InternVL3, MiniCPM-V 4.5, JoyCaption) only if the on-disk judges still fail under J1.
