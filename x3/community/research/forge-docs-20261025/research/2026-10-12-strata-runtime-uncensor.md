# Strata runtime uncensor (sergqwer/strata-nvfp4): claim check
Date: 2026-10-12 (CT). Sources: shallow clone of https://github.com/sergqwer/strata-nvfp4 at 7b00d30 (2026-10-11 12:45 PM CT), GitHub API, one Apify rag-web-browser Reddit query. Prior notes: 2026-10-11-strata.md. No AlienPc access.

## Verdict
**Real, with corrections.** The fork exists and does runtime refusal-direction removal, but the vector is **precomputed and shipped** (not computed at startup), and it is **off by default**. Worth testing on AlienPc as a replacement for downloading abliterated weights, on IQ3_XXS/IQ3_S or Q2_0 GGUF (not IQ2_XS for agents, see below).

## Exact flag and config (README.md, https://github.com/sergqwer/strata-nvfp4/blob/main/README.md)
- L92: "for one request: the API field `"uncensored": true`;"
- L93: "as the default: install with `START-HERE.bat --uncensored on`, or set **Disable censorship by default** in the web page's Model settings"
- L96: "The engine removes the model's refusal direction at run time in layers 8-33 only; the weights are untouched."
- L153: "`--uncensored on|off`) sets the default, `"uncensored"` in `strata-<model>.json`." (config file is `strata-<model>.json`, not `strata.json`)
- data/uncensor/README.md: API alias `"experimental_speed_projection"`; engine args set by setup:
  `--control-vector-scaled data/uncensor/qwen-nvfp4-gptq-uncensored.gguf:1.0 --control-vector-layer-range 8 33 --cvec-mode project --cvec-dir per-layer`

## How it works
- Precomputed 268 KB control vector (`data/uncensor/qwen-nvfp4-gptq-uncensored.gguf`, GGUF controlvector, one 2,560-value direction per layer; JSON beside it has strengths/build/scores). No calibration at startup.
- After each of layers 8-33: `h -= s (h . v) v` on every hyper-connection residual stream, s = 1.0. Off = bit-identical to stock (kernel skips it). Same mechanism as upstream's `experimental_speed_projection`, with the fork's own vector.

## Model / quant support
- On: `qwen-nvfp4-gptq` (default), `qwen-nvfp4-mix`, `qwen-q8`, ISTA GSQ-RCO GGUFs (`qwen` family: Q2_0, IQ2_XS, IQ3_XXS, IQ3_S), Unsloth GGUFs. Measured on NVFP4-GPTQ, Q2_0, IQ2_XS, UD-Q4_K_XL; IQ3_XXS/IQ3_S **not measured** ("sit between").
- Never for `qwen-nvidia-nvfp4` (license), Swift 1.5, Coder.

## Cost (fork's own numbers, unverified independently)
- Refusals with it on, thinking on: 0/104 EN, 0/30 UK (NVFP4); Q2_0 1/104, IQ2_XS 0/104, UD-Q4_K_XL 0/104.
- KL vs stock: 0.016 (Q2_0), 0.017 (IQ2_XS), 0.026 (NVFP4), 0.028 (UD-Q4_K_XL). Thinking length ~unchanged (1,947 vs 1,699 tok). No speed cost stated (a per-layer projection; likely negligible).
- Fork says weight-edited abliteration (OrcaRouter) made a much weaker agent (10-70 steps vs 175) and withdrew it. Implication for us: likely better agent quality than weight-abliterated SC117/Heretic; untested here.
- Warning: "IQ2_XS loops in long greedy agentic thinking by itself (3 of 3 replays ... switch on or off): choose another size for agents." Our current default is IQ2_XS.

## RTX 5070 Ti (16 GB, sm_120) + AlienPc 64 GB RAM
- Requirements: RTX 20-50, 12 GB+ VRAM, driver 580+/CUDA 13; release engine has sm_120 code and FP4xFP4 prompt unit for 120a (RTX 50). So NVFP4 runs on Blackwell consumer.
- RAM: NVFP4 GPTQ wants 69 GiB / 96 GB PC for full speed; on 64 GB it runs "low-RAM mode ~115 tok/s, 32K prompt ~9 s" (README L36-40, fork's measurement on 5090 host). Setup minimum: 48 GB for ISTA 2-bit, 60-64 GB for ISTA 3-bit. IQ3_XXS ~45 GiB in use.
- NVFP4 download is large (>5 GB rule: needs Derek's OK). Speeds in the table are RTX 5090; expect lower on 16 GB.

## Maturity / community
- sergqwer/strata-nvfp4: 125 stars, 13 forks, created 2026-09-29, 3 open issues (WSL2 2x16 GB split crash in MTP prefill; Windows KV-streaming cudaHostAlloc refused after ~1 GiB; A6000 report NVFP4 works 73 t/s). Very young, single-maintainer, rapid versioning (0.1.41-nvfp4.5 to .7, 0.1.42-nvfp4.2).
- Upstream Niko1221/Strata: 22,598 stars, pushed 2026-10-12. Upstream has the projection mechanism (`experimental_speed_projection`) but per fork, its vector costs more (log p(</think>) +0.087 to +0.149 vs fork's +0.027 to +0.040).
- Reddit/r/LocalLLaMA: Apify query returned nothing usable; **no community verification found**. All quality/refusal numbers are the maintainer's.

## Corrections to the claim
- "computes the refusal direction at runtime": NO, precomputed vector shipped in repo; it is *applied* at runtime.
- "strata.json": actually `strata-<model>.json`, key `"uncensored"`.
- Flag `--uncensored on` is a setup/installer flag (START-HERE.bat / setup), not confirmed as an engine CLI flag; engine uses `--control-vector-*` / `--cvec-*` args.
- IQ2_XS support yes, but loops in agent use.

## How to test on AlienPc safely (when lease allows; not now)
1. Install fork in a separate folder (e.g. D:\AI\strata-nvfp4), keep upstream Strata + SC117 + Heretic rollback untouched. Reuse the already-downloaded ISTA IQ2_XS GGUF first (no new download); IQ3_XXS/NVFP4 need Derek's OK (>5 GB).
2. Localhost only; different port than live Strata; GPU idle check first (one model at a time on 16 GB).
3. A/B per request with API `"uncensored": false/true` on a fixed set: our real Forge coding task + 10 adult-fiction prompts (fictional adults 21+ only; no minors, no real people). Record refusals, step count, loop occurrences, tok/s.
4. Hard floor stays in the harness/persona regardless of the switch: refuse/abort on any minor or real-person content; the vector removes refusals, so the floor must be enforced outside the model.
5. Compare with SC117 abliterated IQ2_XS on the same tasks; adopt only if agent quality >= and no floor breaches.

## Guide verification (2026-10-12 3:25 PM CT; fork commit 7b00d30)
Base: https://github.com/sergqwer/strata-nvfp4/blob/7b00d30
| Claim | Verdict | Source |
|---|---|---|
| `START-HERE.bat --setup` | VERIFIED | README.md L74 ("run setup again (`START-HERE.bat --setup`)") https://github.com/sergqwer/strata-nvfp4/blob/7b00d30/README.md#L74 |
| CUDA 12.4+ VMM shim vs CUDA 13/driver 580 | WRONG (no "VMM shim"/12.4 found). Requirement is driver 580+ (CUDA 13) | https://github.com/sergqwer/strata-nvfp4/blob/7b00d30/README.md#L199 ; VMM is used for the elastic K/V only (docs/NVFP4.md L1571) |
| Refusal 5/5 -> 0/5 | VERIFIED, but for qwen-nvfp4-mix/qwen-q8 held-out set; for GPTQ the figure is 0/104 EN, 0/30 UK | https://github.com/sergqwer/strata-nvfp4/blob/7b00d30/README.md#L61-L62 , #L97 |
| UD-Q3_K_XL 57.5 GiB, 208 tok/s, 90.7% | VERIFIED (RTX 5090, 128 GB, every expert in RAM) | https://github.com/sergqwer/strata-nvfp4/blob/7b00d30/README.md#L75-L76 , #L22 |
| NVFP4-GPTQ experts over 92 GiB + SSD streaming low-RAM mode | WRONG: experts are 63 GiB; 92 GiB is the installed-RAM threshold below which low-RAM mode starts (pins hottest experts, reads rest from experts.bin). Real speed on 16 GB card + 64 GB: 54-56 tok/s (emulated) | https://github.com/sergqwer/strata-nvfp4/blob/7b00d30/README.md#L223-L227 ; https://github.com/sergqwer/strata-nvfp4/blob/7b00d30/docs/NVFP4.md#L221-L225 |
| `--max-context 262144` | VERIFIED flag; but only for 32 GB cards. 16 GB card = 65536 | https://github.com/sergqwer/strata-nvfp4/blob/7b00d30/README.md#L204-L207 ; src/program/generate.cpp L751 |
| `--kv int8` | VERIFIED | https://github.com/sergqwer/strata-nvfp4/blob/7b00d30/src/program/generate.cpp#L712 |
| `--spec 4 --spec-min-p 0.60` | --spec 4 VERIFIED; 0.60 NOT FOUND (setup writes 0.5; 0.3/0.7 tested) | https://github.com/sergqwer/strata-nvfp4/blob/7b00d30/src/program/generate.cpp#L814-L817 ; docs/NVFP4.md L180 |
| MTP 74% acceptance | NOT FOUND (docs give 2.2-2.5 tokens/round; p>=0.9 drafts 93-98%) | https://github.com/sergqwer/strata-nvfp4/blob/7b00d30/docs/NVFP4.md#L865 |
| mmproj vision autoload | WRONG: optional, setup asks "Images?" or `--vision gpu|cpu` | https://github.com/sergqwer/strata-nvfp4/blob/7b00d30/docs/DETAILS.md#L1394-L1397 |
| `--kv-resident 32768` | VERIFIED (setup turns it on from 64K context) | https://github.com/sergqwer/strata-nvfp4/blob/7b00d30/docs/DETAILS.md#L80 ; generate.cpp L718 |

Hardware conclusions (265KF: 8P+12E, no SMT, no AVX-512; AVX2+VNNI path README L213-219): NVFP4-GPTQ in auto low-RAM mode (peak ~54 GiB) fits 64 GB; IQ3_S (52 GiB) is the GGUF alternative; UD-Q3_K_XL drops to SSD budget mode below ~68 GB. Context 65536, --kv int8, --kv-resident 32768, --spec 4 --spec-min-p 0.5, MTP on, --pool-affinity p-cores (A/B vs auto), vision off, page file fixed 65536 MB, optional per-exe Prefer No Sysmem Fallback (unmeasured).
SC117 IQ2_XS looping: no fix found; the fork's only advice is "choose another size for agents" (README L161-163).
Upstream Niko1221/Strata not re-checked beyond the fork's README.upstream mirror; claims above are fork-sourced.
