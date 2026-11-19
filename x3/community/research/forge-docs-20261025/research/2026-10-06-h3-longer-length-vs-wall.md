# RESEARCH — H3 / REF2VA longer length vs wall — 2026-10-06 ~11:25 CT

**Owner:** Dial (Max Studio GO) · **Ask:** why hot 10s@768 ~3.5× vs hot 5s; official guidance on longer clips

## TLDR
Hot 10s sA **484.4s** / sB **375.4s** @243f vs hot 5s ~**140s** @124f = **~3.5× / ~2.7× wall** for **~2.0× frames** — super-linear. Matches community: attention cost grows faster than frame count; on our **NODDV+lowvram+no-pinned/async** box, longer clips also spill host RAM (VRAM cliff / unload), so linear-hot ETA is wrong. Official trained band **124–362f (~5–15s)** on **17k+5** @24fps; native short edge ~768.

## Facts (live AlienPc)
1. R3c10 sA START 11:03:21 CT · CELL_DONE wall_s_comfy **484.4** · 768×1344×**243** ST8 simple · no OOM/1450 · clip on Desktop pack (`meta/R3c_full_simple_10s_sA_stdout.txt`, WAVE_EVENTS).
2. R3c10 sB START 11:11:28 CT · wall_s_comfy **375.4** · same shape · still hot session (Comfy never restarted).
3. Hot 5s class ~140–141s @124f ST8 768 (research `2026-10-06-max-15s-generate-time-reduction.md`; W1 simple hot twin ~43s was different cell — fabric/speed KEEP cites ~141s for full strip 124f).
4. Argv locked: `--lowvram --disable-dynamic-vram --disable-async-offload --disable-pinned-memory --use-ck-attention`.
5. Standing note: “15s@768 portrait wall NOT optimized (VRAM spill cliff)” — `04_memory/max-optimize-2026-10-06/...author-optimize.md`.

## Official / community (access 2026-10-06 CT)
| Source | Claim |
|--------|--------|
| https://docs.comfy.org/tutorials/video/minimax/minimax-h3 | Open weights ~15s @24fps; duration snaps **17k+5**; native ~768 short edge / 768×1344 cap |
| https://note.com/aicu/n/n491f17a464e3 (AICU 2026-08-17) | Trained ~124–362; measured 20-step: 124=16.4m, 243=48.1m (**2.9× wall / 2× frames**), 362=97.2m (**5.9× / 2.9×**); attention quadratic-ish |
| https://github.com/YHK-AI/MiniMax-H3-Benchmark | 4060 8GB: 243f@20steps ~46m; 1344×768×243 stall/OOM |
| https://github.com/tonyd2wild/minimax-h3-local | 3090 362f ~23m; VRAM peak can drop while host RAM spills dominate |
| Local | `/workspace/cos/research/2026-10-06-max-15s-generate-time-reduction.md` |

## Contradictions
- “Hot keep” ≠ “linear time”: sB faster than sA but both >> 2×5s.
- VRAM % alone is a poor cliff signal (community: host spill).

## Unknowns
- Exact s/frame breakdown (sample vs VAE) for 243f on this box — NO_DATA instrumented this turn.
- True hot 362f@768 wall still unmeasured (15s canceled @18min; 480@362 live interrupted for 6s/8s insert).

## Recommend
- Probe **6s=141f** and **8s=192f** (17k+5 nearest to 145/193) to map cliff onset — **armed R3c68** this turn.
- For ~15s product without DROP accelerators: preview **480×864** or **3×124f hops**, not expect 141s×2.9.

## close-out
Evidence paths: Desktop `MAX_OPTIMIZE_MATRIX_2026-10-06\meta\` · WAVE_EVENTS · this file.  
Standing fact: longer H3 length is **super-linear wall** under our argv; 10s live proves it. No KEEP.
