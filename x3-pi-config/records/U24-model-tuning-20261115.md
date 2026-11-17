# U24 EVO-X3 model tuning, research and live verification (2026-11-15, ~3:52–4:20 PM CT)

Asked by Derrick t1760u ("Ok continue and do research and verify everything"). Q8 Heretic stays the writer (t1757u, no Q4 rerun).
Config: `/etc/evo-x3/llama-swap.yaml` (backups `*.bak-20261115-1554*/1556*/1557*-pretune-<slot>`). pi: `~/.pi/agent/models.json` (backup `.bak-20261115-pretune`).
Hardware now: BIOS UMA minimal (`mem_info_vram_total` 1 GiB), GTT 120 GiB (`amdgpu.gttsize=122880 ttm.pages_limit=31457280`), OS sees 124 GiB. Exclusive swap group `main` (one of flash-next / gemma4-heretic / qwen27b) + resident `embed-small`.

## Settings per slot

### gemma4-heretic (Gemma 4 26B A4B IT Heretic Q8_0 + mmproj Q8_0, kyuz0 llama.cpp Vulkan build 12405)
| Setting | Value | Source |
|---|---|---|
| Sampling | temp 1.0, top_p 0.95, top_k 64 | Google model card "Best Practices" [G1] |
| Context | `-np 2 -c 524288` = 262144 per slot (native 256K) | Card context 256K [G1]; KV only ~5 GiB per 262K at f16 (5 full-attn layers) [G3] |
| KV cache | f16 (dropped `-ctk/-ctv q8_0`) | KV tiny so q8 saves nothing; localbench measured q8_0 KV KLD 0.377 on Gemma-4-26B-A4B vs <0.04 on Qwen [LB2]; r/LocalLLaMA also reports q8 KV hurts Gemma 4 vision [G4] |
| Vision | `--mmproj ...mmproj-Q8_0.gguf`, `--image-min-tokens 560 --image-max-tokens 1120` | Card budgets 70/140/280/560/1120, default 280 [G1][G5]; 280 weak on detail [G4] |
| Batch | `-b 2048 -ub 2048` | Gemma 4 image tokens are non-causal and must fit one ubatch [G2] |
| Thinking | per request: `chat_template_kwargs.enable_thinking` true/false; `--reasoning-format deepseek` → `reasoning_content` | Card thinking control [G1]; llama-server `--reasoning-format` |
| Flash attn | `-fa on`, `--load-mode none` | kyuz0 Strix Halo toolbox flags |

### flash-next (official unsloth Qwen3.8-Flash-Next UD-Q4_K_XL + shared Q8 MTP, Gufo runtime 0.34.0)
| Setting | Value | Source |
|---|---|---|
| Context | `--context 262144 --sessions 1` (was 32768) | Native 262144; ~27.5 KiB/token with MTP [F2]; LLMKube runs 262144 on one Strix Halo [F4] |
| Speculative | `--speculative mtp --mtp-model mtp-...-shared-Q8_0.gguf` | Gufo model doc [F2][F3] |
| Sampling | Gufo model/thinking preset (= card: 1.0 / 0.95 / 20 / min_p 0, presence 0; instruct 0.7 / 0.8 / presence 1.5) | Unsloth guide [F1]; `gufo serve llm --help` |
| Reasoning | default effort `medium`, per-request `reasoning_effort` (xhigh for planning); `--preserve-thinking on` | Unsloth: medium for routine edits/tool calls, xhigh complex, preserve for multi-turn coding [F1] |
| RAM cache | `--cache-ram-bytes 2147483648` | Gufo auto = half of free RAM up to 32 GiB, which overcommits UMA with 113 GiB loaded (`--help`) |
| Batch/ubatch, flash-attn | n/a in Gufo (scheduler-managed; `--prefill-chunk` deprecated) | `gufo serve llm --help`, SERVER.md [F3] |
| Vision | Model is multimodal via `mmproj-BF16.gguf` (~0.9 GB, Gufo `--mmproj`, auto-discovered beside model). **Not downloaded**; coding doesn't need it (Derrick t1759u) | Gufo doc files table [F2]; HF discussion [F5] |

### qwen27b (unsloth Qwen3.8-27B UD-Q4_K_XL, kyuz0 llama.cpp Vulkan)
| Setting | Value | Source |
|---|---|---|
| Sampling | temp 1.0, top_p 0.95, top_k 20, min_p 0, presence 0 | Qwen3.8 card thinking preset (same family table as [F1]) |
| Context | `-np 2 -c 524288` = 262144 per slot, f16 KV | Native 262144; only 16 of 64 layers full attention [Q1] (old 65 GiB estimate assumed all layers) |
| Flash attn | `-fa on --load-mode none` | kyuz0 flags |

### embed-small (nomic-embed-text-v1.5 Q8_0)
| Setting | Value | Source |
|---|---|---|
| Context | `-c 8192 -b 8192 -ub 8192 --rope-scaling yarn --rope-freq-scale 0.75` | nomic GGUF card: llama.cpp defaults to 2048, this is the 8192 recipe [E1] |
| Prefixes | callers must send `search_query:` / `search_document:` | [E1] |

### UMA budget
Flash-Next at 262144: 103.69 GiB weights + 2.60 MTP + ~6.9 KV + 2 cache ≈ 115 GiB of 120 GiB GTT (observed `free`: 95 used / 29 available while loaded with embed + Open WebUI). Heretic at 2×262144 f16: ~44 GiB used system-wide. qwen27b at 2×262144 f16: ~16.5 + ~32 GiB KV. All fit one at a time in the exclusive group.

## Live verification (all on X3, 2026-11-15 CT)
| Check | Result | Evidence |
|---|---|---|
| 401/200 after each slot edit (4 restarts) | PASS | `verify-serve.sh`: no key 401, LLM_KEY_BOX 200 every time |
| Heretic vision on POOL still `COND_POOL_BIKINI_PORTRAIT.jpg` | PASS | 1139 prompt tokens (image ≈1.1K budget), pp 236 t/s, tg 41.5 t/s; "standing in a pool, leaning one hand against the edge … light beige, translucent two-piece swimsuit … outdoor pool overlooking the ocean at dusk"; `/props` n_ctx 262144, vision true |
| Heretic thinking off vs on per request | PASS | off: reasoning_content 0 chars; on: 516 chars; same answer (6:15 PM), tg ~44.5 t/s |
| Flash-Next tool call | PASS | finish `tool_calls`, `read_file({"path":"src/app.py"})`; MTP 45/56 accepted |
| Flash-Next code task | PASS | correct `is_valid_ipv4` + 4 asserts; decode 75.4 t/s (MTP 254/294) |
| Flash-Next prefill/decode at ~9.8K prompt | PASS | pp 1520 t/s, tg 38.9 t/s; swap qwen27b→flash-next + answer 35 s |
| qwen27b sanity | PASS | 17×23 = 391, reasoning on, pp 43 t/s (tiny prompt), tg 11.8 t/s |
| embed-small sanity | PASS | dim 768; cos(query, relevant) 0.698 vs (query, unrelated) 0.310 |
| Swap between slots | PASS | heretic → flash-next → qwen27b → flash-next, embed stayed resident |
| Render pi chat (`render-pi.sh -p`, image attached as `@file` arg) | PASS | model gemma4-heretic, image block in user msg, 3 thinking blocks (thinking medium), "standing in the pool, leaning one hand on the edge. Sheer white bikini…" |
| Render pi with the path only inside the prompt text | Caution | image NOT attached and the model invented a different outfit. Attach stills as `@path` arguments / the still-read tool, never by path in prose |
| Forge pi chat (`forge-pi.sh -p`) | PASS | model flash-next, answer `s[::-1]` (no thinking blocks shown; launcher sets no `--thinking`) |

## Builder guard (step 4)
- Commit `12ef873` (start-still guard + relative run-dir fix, 19 tests) had converted `render_writer_pipeline.py` CRLF→LF (3518-line diff). `7e96373` restores CRLF, so the real diff vs the AlienPc snapshot is 93+/3−.
- Suite `scripts/parody` (X3 venv): baseline at `12ef873~1` 507 passed / 5 failed / 1 skipped; now 526 passed / same 5 failed (Windows-only queue/vault tests) / 1 skipped. Guard tests 19/19.
- AlienPc patch (NOT applied): `~/AI/_xfer/alienpc-patches/still-guard-rundir-20261115.patch` (sha256 c17732e7…d2fbd814), `git apply --check` clean on the snapshot. Apply only after the v2 render finishes (~6:05 PM CT) and with Derrick's OK; back up first, then run `git apply --check` again because AlienPc may have moved.

## Sources
- [G1] google/gemma-4-26B-A4B model card — https://huggingface.co/google/gemma-4-26B-A4B
- [G2] "A Quick Note on Gemma 4 Image Settings in Llama.cpp" — https://www.someoddcodeguy.dev/a-quick-note-on-gemma-4-image-settings-in-llama-cpp/
- [G3] unsloth issue #11435 (Gemma 4 KV per token) — https://github.com/unslothai/unsloth/issues/11435 ; r/LocalLLaMA 262K context thread — https://www.reddit.com/r/LocalLLaMA/comments/1sihwo8/
- [LB2] localbench KV cache quantization benchmark ("Gemma 26B A4B at q8_0 is 0.377") — https://localbench.substack.com/p/kv-cache-quantization-benchmark (cite fixed 2026-11-15 X3 Phase 4, quant audit error 4)
- [G4] r/LocalLLaMA "Gemma 4 for 16 GB VRAM" — https://www.reddit.com/r/LocalLLaMA/comments/1scw979/gemma_4_for_16_gb_vram/
- [G5] unsloth/gemma-4-26B-A4B-it-GGUF discussion 32 — https://huggingface.co/unsloth/gemma-4-26B-A4B-it-GGUF/discussions/32
- [S1] Strix Halo Gemma 4 numbers: r/LocalLLaMA QAT bench https://www.reddit.com/r/LocalLLaMA/comments/1tyilv7/ ; hec-ovi/llama-vulkan-strix https://github.com/hec-ovi/llama-vulkan-strix
- [F1] Unsloth Qwen3.8-Flash-Next guide — https://unsloth.ai/docs/models/qwen3.8-next
- [F2] Gufo docs/models/qwen3.8-flash-next.md — https://github.com/gufo-org/gufo/blob/main/docs/models/qwen3.8-flash-next.md
- [F3] Gufo docs/SERVER.md — https://github.com/gufo-org/gufo/blob/main/docs/SERVER.md
- [F4] LLMKube "Qwen3.8-Flash-Next on Gufo on one Strix Halo" — https://llmkube.com/docs/labs/qwen38-flash-next-gufo-on-strix-halo
- [F5] unsloth/Qwen3.8-Flash-Next-GGUF discussion 24 — https://huggingface.co/unsloth/Qwen3.8-Flash-Next-GGUF/discussions/24
- [Q1] hec-ovi/llama-vulkan-strix context table (Qwen3.8-27B: 16 of 64 layers full attention)
- [E1] nomic-ai/nomic-embed-text-v1.5-GGUF card — https://huggingface.co/nomic-ai/nomic-embed-text-v1.5-GGUF
- Not found / not used: Level1Techs had no slot-specific settings in search; no Gufo issue changed a setting here.

## Open
- Flash-Next vision mmproj not downloaded (optional, ~0.9 GB).
- Forge launcher has no `--thinking` level (AlienPc Forge level not checked; AlienPc offline from the box).
- AlienPc parity of Heretic slot flags (ctx/KV/image budget) not checked: AlienPc offline from here.
- Commits are local on the X3 (`~/AI/community` x3-linux, `~/AI/render` x3-linux): no Gitea remote is configured on those repos, so nothing was pushed.
- Bio "damp skin / sheen" template issue (Prompt maker) untouched.

## U25 quant upgrades (2026-11-15, ~4:41–5:10 PM CT)
Approved by Derrick (widget t1769s6505): "Yes, swap in the official BF16 vision file for Heretic and re-test vision" and "Yes, upgrade qwen27b to Q8 on Gufo and test it". Follows the read-only quant audit `/workspace/maxops/x3-quant-audit-20261115.md` (box).

### Files (all sha256 = HF LFS oid, size = HF API)
| File | Source | Bytes | sha256 |
|---|---|---|---|
| `/srv/models/gemma4-heretic/gemma-4-26B-A4B-it-unsloth-mmproj-BF16.gguf` | unsloth/gemma-4-26B-A4B-it-GGUF `mmproj-BF16.gguf` (main) | 1,194,828,256 | 41926ed5f1403cf5add23b0684992805ea6f97253096132e769e65646b8cef9d |
| `/srv/models/qwen27b/Qwen3.8-27B-UD-Q8_K_XL.gguf` | unsloth/Qwen3.8-27B-GGUF (main 4af51b35; same oid as Gufo lock rev ce331efc) | 31,457,991,680 | af36ecb6b5db1407953345b746c14ac93f0657dda413910b4348683a2d990377 |
| `/srv/models/qwen27b/Qwen3.8-27B-DFlash2-Q4_K_M.gguf` | z-lab/Qwen3.8-27B-DFlash2-GGUF @2d9571f8 (the source Gufo's `models.lock.json` pins for `qwen27-q8`) | 1,143,006,816 | 1a25c56858e1ebe93f2718ac1d49d1151f9323325c1bbfd6209370f4db131ebd |

Kept as rollback (not deleted): `Gemma-4-26B-A4B-Heretic.mmproj-Q8_0.gguf`, `Qwen3.8-27B-UD-Q4_K_XL.gguf`. Disk: root 660G → 691G used (+~33.8 GB), `/srv/models` 181G.

### Config changes (`/etc/evo-x3/llama-swap.yaml`)
Backups: `llama-swap.yaml.bak-20261115-164343-pre-mmproj-q8` (before mmproj edit), `llama-swap.yaml.bak-20261115-170054-pre-mmproj-q8` (before qwen27b edit).
- gemma4-heretic: `--mmproj` → the unsloth BF16 file. Nothing else changed.
- qwen27b: moved from kyuz0 llama.cpp (`-m ...Q4_K_XL -np 2 -c 524288`, explicit sampling) to Gufo 0.34.0 (same pinned image as flash-next): `gufo serve llm --model ...UD-Q8_K_XL.gguf --speculative dflash2 --dflash-model ...DFlash2-Q4_K_M.gguf --context 262144 --sessions 2 --cache-ram-bytes 2147483648 --served-model-name qwen27b`. Recipe from Gufo `docs/models/qwen3.8-27b.md` (+ `src/models/qwen/models.lock.json`); sampling/thinking left on Gufo's model preset (per-request override). Text-only: Gufo's optional `mmproj-BF16.gguf` (0.93 GB) is not beside the model.
- Comments only: removed stale flash-next "try --context 32768 / 262144 ≈ 132.3 GiB" estimator text and stale Heretic "conservative 65536 total" text; mmproj provenance now stated correctly.
- pi `~/.pi/agent/models.json` (backup `.bak-20261115-pre-mmproj-q8`): display names only (Heretic "official unsloth mmproj BF16"; qwen27b "UD-Q8_K_XL + DFlash2 (Gufo)"). Ids, context, sampling unchanged.
- `~/AI/render/x3/README-X3.md` settings table updated.

### Live checks (X3, 2026-11-15 CT)
| Check | Result | Evidence |
|---|---|---|
| verify-serve after each restart (2) and at the end | PASS | no key 401 / LLM_KEY_BOX 200 |
| Heretic loads BF16 mmproj | PASS | log `loaded multimodal model, '.../gemma-4-26B-A4B-it-unsloth-mmproj-BF16.gguf'` |
| Heretic vision, POOL still `COND_POOL_BIKINI_PORTRAIT.jpg` as base64 `image_url` part, thinking off | PASS | 1145 prompt tok, pp 215 t/s, tg 42.5 t/s: "blonde woman stands in a swimming pool, leaning her right hand against the light-colored stone edge … two-piece swimsuit … sheer, cream-colored mesh … scoop-neck top and low-rise bikini bottoms … pool overlooking the ocean under a cloudy sky at dusk" |
| Same, thinking on | PASS | pp 259 t/s, tg 42.2 t/s, 5106 reasoning chars: "off-white bikini … sheer, translucent mesh … infinity pool overlooking the ocean under a cloudy, twilight sky" (matches U24 Q8-mmproj result: light beige translucent two-piece, ocean at dusk) |
| qwen27b Q8 load on Gufo | PASS | load 5.0 s (file cached), `sessions=2 context_tokens=262144 speculative=dflash2`; GTT used 70.2 GiB loaded |
| qwen27b arithmetic (17×23 + 144/12) | PASS | "403"; tg 47.8 t/s (DFlash2 71/77 accepted) |
| qwen27b code (`is_valid_ipv4` + 4 asserts) | PASS | correct, rejects leading zeros; tg 34.1 t/s (874/1386 accepted), thinking on |
| qwen27b tool call | PASS | finish `tool_calls`, `read_file({"path":"src/app.py"})`, tg 33.1 t/s |
| qwen27b ~9K prompt read/write, thinking off | PASS | pp 397.5 t/s (9038 tok), tg 14.7 t/s on free prose (143/541 accepted). Q4 on llama.cpp was 11.8 t/s; Gufo docs Q8 AR ~7 t/s, DFlash2 mixed ~16 t/s |
| Swap heretic → qwen27b → flash-next (twice), embed-small resident | PASS | one main container at a time; `llama-swap-embed-small` stayed up through all swaps (note: after a llama-swap restart it starts on its first embedding request, dim 768) |
| GTT per main model | info | heretic 39.9 GiB, qwen27b Q8 70.2 GiB, flash-next ~89 GiB just after load (grows toward ~108-115 at use) |

Nothing reverted. Left loaded at the end: flash-next + embed-small (same as before).
Sources: Gufo `docs/models/qwen3.8-27b.md`, `docs/internal/models/qwen3.8-27b/BENCHMARKS.md` (Q8 AR/DFlash2 tables, memory 53–63 GiB at C1 262144), `src/models/qwen/models.lock.json`, CHANGELOG 0.34.0 (latest release, = our pinned image), commit 2cf36518 (fetched 2026-11-15); HF API tree listings for the three repos.
