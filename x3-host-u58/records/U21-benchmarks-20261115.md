# U21 (UB) benchmarks B1–B5 — EVO-X3, 2026-11-15

Run by Antigravity Orchestrator (Argon) 20:35–23:46 CT, 2026-11-15. Antigravity hit its quota (429) at about 23:57 CT and died before writing this record. Max Architect wrote it on 2026-11-16, about 06:30 CT, from the raw outputs in `~/evo-x3/bench/2026-11-15-u21/` (checksums in `SHA256SUMS` there). No step was re-run: B1–B5 all have outputs. B6 was skipped (AlienPc-only).

## B1 Quiet window — PASS
- Window start 20:36:53 CT. The llama-swap log shows 0 non-bench requests in the 30 minutes before. No cron or downloads were running.
- Kernel 7.3.3-200.fc44, cmdline `amdgpu.gttsize=122880 ttm.pages_limit=31457280`, IOMMU ON. Power: BIOS Balanced 85 W, tuned `accelerator-performance`. Temperatures at the start: edge 37 °C, Tctl 39 °C.
- Engines: llama.cpp kyuz0 Vulkan RADV b12405 (9f26fe11c); Gufo 0.34.0; Halogen 0.20.5. Full header: `b1_environment_header.json`.

## B2 Speed

### Served path (llama-benchy through llama-swap, `--runs 3 --no-cache`, mean ± sd)

| Slot | tg128 d0 | tg128 d32K | tg128 d131K | e2e TTFT d32K | e2e TTFT d131K | pp512 d32K t/s |
|---|---|---|---|---|---|---|
| flash-next (Halogen HGN v2) | 53.6 ± 2.2 | 42.8 ± 3.4 | 50.2 ± 7.2 | 18.65 s | 72.5 s | 1785 ± 15 |
| flash-next-gufo (Q4_K_XL + MTP) | 55.8 ± 0.4 | 58.2 ± 1.0 | 56.7 ± 2.0 | 21.05 s | 87.1 s | invalid* |
| gemma4-heretic (Q8_0, llama.cpp) | 46.1 ± 0.0 | 38.3 ± 0.1 | 28.3 ± 0.1 | 30.3 s | 250.6 s | 1102 ± 4 |
| qwen27b (Q8_K_XL + DFlash2, Gufo) | 22.4 ± 0.9 | 22.7 ± 4.6 | 14.1 ± 4.0 | 90.1 s | 458.9 s | invalid* |

flash-next also ran at d245760: pp512 1710 ± 4 t/s, tg128 49.9 ± 11.5, TTFT 144 s.

\* Gufo's component cache answered llama-benchy's pp probe from cache despite `--no-cache`. Its pp t/s values (144K–2.7M t/s) are not real, so they are struck out. For Gufo slots, use the e2e TTFT column.

**Halogen vs Gufo (flash-next), by the overlap rule**
- Decode: d0 is a tie, Gufo wins at d32K, d131K is a tie.
- Prefill / TTFT: Halogen wins at d32K (−11%) and d131K (−17%).
- Cold load (U12): Halogen wins.

### U12 cold TTFT fixture
Fixture: about 20.3K-token prompt, first request after load, no warmup.

| Slot | Wall time |
|---|---|
| flash-next (Halogen) | **23.5 s** |
| gemma4-heretic | 28.3 s |
| flash-next-gufo | 36.8 s (prefill 1,647 t/s) |
| qwen27b | 69.3 s (prefill 387 t/s) |

### Engine floor (llama-bench `-o json`, Vulkan b12405 9f26fe11c, `-fa 1`, f16 KV; `-r 5` at d0/d32K, `-r 2` deeper)

| Model | pp512 d0 | tg128 d0 | pp512 d32K | tg128 d32K | pp512 d131K | tg128 d131K |
|---|---|---|---|---|---|---|
| Heretic Q8_0 (b/ub 2048) | 1674 ± 13 | 48.0 | 771 ± 6 | 38.6 | 295 | 27.7 ± 0.7 |
| Heretic Q4_K_M (b/ub 2048) | 1570 ± 8 | 67.2 | 751 ± 5 | 50.1 | 298 ± 3 | 33.2 ± 1.1 |
| Flash-Next Q4_K_XL (no MTP, floor) | 613 ± 5 | 27.1 | 414 ± 4 | 25.2 | 296 ± 8 | 21.3 ± 0.4 |
| Qwen3.8-27B Q8 | 375 ± 6 | 7.3 | 276 ± 2 | 6.8 | 171 | 5.6 |

Heretic Q4_K_M beats Q8 on decode at every depth (+40% at d0). Prefill is a tie or a small Q8 win.

### U6 pair (qwen27b Q8, Gufo `gufo bench`, ROCm)
| Mode | tg128 d0 | tg128 d32K |
|---|---|---|
| Plain AR | 7.27 | 6.83 |
| DFlash2 | **26.1** | **43.8** |

DFlash2 is 3.6× faster at d0 and 6.4× at d32K. The live long fixture: TTFT 47.3 s on 18,253 tokens, decode 30.1 t/s.

## B3 Coherence and provenance — PASS
- **Served coherence: all pass.** flash-next, flash-next-gufo, gemma4-heretic and qwen27b each produced one real generation, and all were coherent (`coherence_*.json`).
- **Vulkan raw coherence:**
  - Flash-Next Q4_K_XL: PASS.
  - Qwen27B Q8: PASS.
  - Heretic Q4_K_M with raw `-no-cnv`: FAIL, degenerate output. It passes with `--jinja --single-turn`, so this was a template issue, not the model.
  - Its throughput rows above come from the templated rerun's build, which is the same binary.
- Model and raw-JSON sha256s are in `SHA256SUMS`. The tokenizer sha256 is in `b5_ruler_results.json`.

## B4 Writer quality (gemma4-heretic vs flash-next-uncensored) — generations done, scores PENDING
- 10 prompts × 3 rounds (30/30 clean completions). Prompt file `~/AI/community/benchmarks/u21-writer-prompts-20261115.json`, commit d1505a5, sha256 b66b3156…
- Samplers: T0.7, p0.95, k64, min_p 0.05, max 500 tokens, thinking off. Seeds 101/202/303. A/B order: round 2 is round 1 inverted; round 3 is seeded random.
- Blind packet: `b4_writer_blind_packet.md`. The key is kept separately in `b4_writer_key.json`.
- **Official scores are pending from Prompt maker.** Max did not self-score.
- The Vulkan T=0 fixed-seed check gave 3/3 different outputs, which confirms HALOBENCH: the 3 runs are samples, not replays.

## B5 Long context (RULER 4-task subset, seed 42, Qwen tokenizer sha 0997f410…)
| Model | 32K | 128K |
|---|---|---|
| flash-next (Halogen) | 3/4 (failed fwe_aggregation) | 4/4 |
| qwen27b | 3/4 (failed vt_multihop) | 4/4 |

Wall time per task at 128K: flash-next 74–83 s, qwen27b 465–530 s.

## Slot-pick implications (used by U34)
1. **flash-next stays on Halogen.**
   - Quality: no head-to-head difference was measured. Both are coherent, the same Qwen3.8-Flash-Next weights, and RULER was run on Halogen.
   - Speed: Halogen wins prefill and TTFT, which matter most for Forge's long agent contexts, and cold load. Gufo wins decode only at d32K.
   - Parallelism: Halogen serves 4 slots against Gufo's 1 session, and Forge subagents need that.
   - Decision: archive the `flash-next-gufo` slot config. The weights stay on disk.
2. **qwen27b: keep.** It is 3–6× slower than flash-next, but it is the only dense-27B coder fallback, and DFlash2 is confirmed (3.6–6.4×).
3. **gemma4-heretic Q8 vs Q4_K_M:** Q4_K_M decodes about 40% faster. The writer pick stays with B4's official scores (pending). Q8 stays live for now.
4. **flash-next-uncensored:** stays as a non-production slot. Its B4 samples are in the blind packet.

## Skipped
- B6 (AlienPc).
- The paid EQ-Bench judge and the coding bake-off (not approved).
- The brain copy at `records/bench/` (Antigravity had no brain checkout). This file is the record.
