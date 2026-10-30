# DRAFT: FLUX.2 overnight test matrix (AlienPc :8189). Not queued; needs Derrick's GO.
Drafted 2026-10-09 ~22:25 CT. Research and sources: `/workspace/cos/research/2026-10-10-flux2-settings-prompting.md`. Tags: [official] / [community] / [inferred] / [local].

## 0. Gates (all must pass before queueing anything)
1. **Start gate:** start the queue only after `ORCH_FIXTEST_END` appears in `C:\Users\derek\Desktop\MAX_FIXTEST_2026-10-09\meta\orchestrator_fixtest.log` (written by `/workspace/maxops/fixtest-2026-10-10/scripts/orchestrate_fixtest.ps1`). Noted only; nothing was queued.
2. **Shell lease:** Max Studio holds the AlienPc Shell lease (`/workspace/cos/brain-staging/10_packs/max/one-holder-for-the-alienpc-shell.md`). Production argv and locks stay as they are without Derrick's GO (same pack). Use `production-defaults-st8-dynamic-vram.md` for argv.
3. **Inventory not verified tonight:** AlienPc was **offline** (2026-10-09 22:17 CT), so the HAVE/MISSING status below comes from box notes dated 09-25 to 10-06. Run `alienpc_flux2_inventory_READONLY.ps1` (this folder) under the lease. Then mark each cell HAVE/SKIP.
4. **LoRA gate:** a LoRA cell runs only if its safetensors header shows a FLUX.2 Klein base **of the same size as the cell's model** (4B vs 9B), and the file is a tool LoRA, not person-named.
5. **Fiction lock:** every prompt is built from the canon via links only: `/workspace/cos/brain-staging/10_packs/max/fiction-and-cnc-follow-the-linked-canon.md`, `attached-still-is-the-cond.md`, `lock-length-and-beats-before-a-product-queue.md`, `quality-stamp-before-derricks-eyes.md`, `scores-in-words-keep-is-derricks-go.md`. No canon text is pasted here. Prompt slots below are placeholders (`P_T2I`, `P_EDIT`) to fill from those packs at queue-build time. No real-person names in any prompt.
6. **Start images:** use only the approved sets (§4).

## 1. Seeds and output rules
- 3 images per cell, same prompt within the cell, random seeds. **Recommendation [inferred]:** draw one random triplet per mode (T2I triplet, EDIT triplet) at queue time and reuse it in every cell of that mode. The seeds are still random and are recorded, and this keeps "one change per cell" a fair comparison. Alternative if Derrick wants fresh seeds per cell: draw 3 per cell. Either way, write `seed` per image into `results.json` plus `knobs.json` per cell (same shape as `/workspace/FAIR_FLUX2_KLEIN9B_P163_ACTFIRST_2026-10-02/meta/knobs.json`).
- Record wall_s per image and cold/warm, so the s/it estimates below get replaced with measured numbers.

## 2. Baselines (one change per cell against these)
| | T0 (text-to-image, Derrick's "t2v") | E0 (reference edit, Derrick's "i2v") |
|---|---|---|
| UNET | `FLUX-KLEIN-9B-FP8-NSFW.safetensors` (community 9B FP8; HAVE per 10-06 runs) | same |
| TE / VAE | `qwen_3_8b_fp8mixed` / `flux2-vae` [official pairing] | same |
| Steps / cfg | 4 / 1.0 [official distilled] | same |
| Sampler / scheduler | euler / Flux2Scheduler [official template] | same |
| Size | 768×1376 (matches approved conds, ÷16) | 768×1376, 1 ref via ReferenceLatent, ref at native 768×1376 |
| LoRA | none | none |
| Prompt style | natural language, Subject→Action→Style→Context, 30–80 words, camera/lens line, positive-only [official] | "image 1" indexed + one change + "keep … unchanged" invariants [official+community] |
| Start image | n/a | `/workspace/maxops/sheer-bikini-picks-2026-10-09/B01_POOL_SHEER_CROCHET.jpg` |
| Negative | empty (has no effect at cfg 1 [inferred]) | empty |

## 3. Cells (52 cells, 156 images)
Time per cell = 3 images + ~10 s overhead (+~70 s on a model switch), **ESTIMATE [inferred]** scaled from [local] 15.1 s warm / 48.2 s cold per image (9B FP8, 4 steps, 1792×1008, 1 ref, --lowvram), from [official] Comfy 5090 timings (4B dist ~1.2 s, 4B base ~17 s) at a 5090→5070 Ti factor of ~2–2.5×, and assuming cfg>1 ≈ 2× per step.

### Text-to-image (T)
| Cell | Single change vs T0 | Status | Est min |
|---|---|---|---|
| T0 | baseline | HAVE* | 1.7 |
| T-V1 | UNET flux-2-klein-4b-fp8 + qwen_3_4b (TE swap is part of the variant) | HAVE* | 1.5 |
| T-V2 | official flux-2-klein-9b-fp8 | **verify** (gated; not HAVE on 10-02) | 1.7 |
| T-V3 | 9B **Base** FP8, 50 steps, cfg 4.0 (the variant's own official recipe) | MISSING | 10.3 |
| T-V4 | 4B **Base** FP8 + qwen_3_4b, 50 / 4.0 | MISSING | 3.6 |
| T-V5 | 9B **NVFP4** | MISSING | 1.7 |
| T-S1 / S2 / S3 | steps 3 / 6 / 8 (expect no gain past 4 [official+community]) | HAVE* | 0.5 / 0.7 / 0.9 |
| T-G1 / G2 / G3 | cfg 0.8 [community] / 1.5 / 2.5 (expect breakage at ≥2) | HAVE* | 0.8 each |
| T-K1..K5 | euler/simple · euler/beta · res_multistep/simple [community] · ddim/ddim_uniform [community] · dpmpp_2m/simple | HAVE* (res_* built-in; skip res_2s unless RES4LYF installed) | 0.6 each |
| T-R1 / R2 / R3 | 576×1024 · 896×1600 · 1088×1936 (~2.1 MP; BFL recommends ≤2 MP) | HAVE* | 0.4 / 0.8 / 1.2 |
| T-L1 / L2 / L3 | + `MS_real_and_Details_klein` @0.5 / 0.8 / 1.0 (trigger first if the header lists one) | **gate 4** (base size unknown; run it on the 4B baseline instead if the header says 4B) | 0.6 each |
| T-P1 | same content as JSON structured prompt (BFL schema) [official] | HAVE* | 0.6 |
| T-P2 | short 10–30 words | HAVE* | 0.6 |
| T-P3 | long 80+ words | HAVE* | 0.6 |
| T-P4 | baseline with the camera/lens line removed | HAVE* | 0.6 |
| T-P5 | word order reversed (context first, subject last) | HAVE* | 0.6 |

### Reference edit (E)
| Cell | Single change vs E0 | Status | Est min |
|---|---|---|---|
| E0 | baseline | HAVE* | 1.8 |
| E-V1 / V2 / V3 / V4 | 4B dist FP8 · official 9B FP8 · 9B Base 50/4.0 · 9B NVFP4 | HAVE* / verify / MISSING / MISSING | 1.6 / 1.8 / 11.3 / 1.7 |
| E-S1 | steps 6 | HAVE* | 0.8 |
| E-G1 | cfg 1.5 | HAVE* | 0.9 |
| E-K1..K3 | euler/simple · euler/beta · res_multistep/simple | HAVE* | 0.6 each |
| E-R1 / R2 | 896×1600 · 1088×1936 (ref scaled to match via ImageScaleToTotalPixels [community]) | HAVE* | 0.9 / 1.4 |
| E-L1 / L2 | + MS_real_and_Details_klein @0.5 / 1.0 | gate 4 | 0.7 each |
| E-P1 | refer to the subject by visual attributes, not "image 1" [community] | HAVE* | 0.6 |
| E-P2 | drop the "keep … unchanged" invariant clause | HAVE* | 0.6 |
| E-P3 | JSON structured edit prompt | HAVE* | 0.6 |
| E-P4 | long 80+ words | HAVE* | 0.6 |
| E-M1 | 2 refs: B01 (subject) + `/workspace/maxops/blonde-elf-picks-2026-10-09/E3_STONE_SANCTUARY.jpg` (setting), roles indexed [official] | HAVE* | 0.8 |
| E-I1 | start image `blonde-elf-picks-2026-10-09/E2_THRONE_ROOM.jpg` | HAVE* | 0.6 |
| E-I2 | start `couple-picks-2026-10-09/M01_DARK_LOFT_EMBRACE.jpg` | HAVE* | 0.6 |
| E-I3 | start `dark-hair-picks-2026-10-09/D12_Woman_posing_in_bikini.jpg` (bikini picks only: D12, D15) | HAVE* | 0.6 |
| E-I4 | start `sydney-10s-tests-2026-10-09/COND_ORC_POOL_EDGE_SUNSET.jpg` | **provenance check** (see note) | 0.6 |
| E-C1 | + ddpm pass at 0.06 denoise for colour restore [community] | HAVE* | 0.8 |
*HAVE = per box notes; reconfirm with the inventory script.

**E-I4 note:** this folder is on Derrick's approved list. I made no judgement about faces. The 10-09 LoRA cleanup audit, though, *held* COND_* files without checking them (REPORT §Media rule), and the folder name matches the archived person-LoRA pattern. Before E-I4 runs, Derrick should confirm this COND was not made with an archived person LoRA. If he doesn't, cut E-I4.

## 4. Totals and cut-lines
- **All 52 cells / 156 images: ~1.1 h nominal, ~2.2 h at a 2× safety factor (ESTIMATE).** This is under the 4 h cap.
- HAVE-only tonight (drop the 5 MISSING cells): 47 cells / 141 images, ~0.65 h nominal / ~1.3 h ×2.
- Run order: group by model to cut reloads: 9B-NSFW block (T then E) → 4B → official 9B → NVFP4 → Base cells last.
- **Cut-lines if the measured pace projects past 4 h** (cut in this order): (1) T-V3 and E-V3 9B Base cells (~22 min); (2) T-R3/E-R2 2 MP cells; (3) T-S1, T-G3, T-K5, T-P5; (4) E-C1, E-P4, T-P3; (5) the LoRA strength midpoints (T-L2). Keep T0/E0, the variant cells, and E-I1..I3 to the end.
- Optional with headroom, only if Dev files are downloaded: O-D1 T2I and O-D2 edit on `flux2_dev_fp8mixed` + `mistral_3_small_flux2_fp8`, 28 steps / guidance 4 [official]. Guess 3–6 min/image on 16 GB with offload [inferred], so ~10–20 min per cell. Needs ≥64 GB system RAM [inferred].

## 5. Download list (for Derrick's yes; nothing downloaded)
| File | Size | Source | Needed by |
|---|---|---|---|
| flux-2-klein-9b-fp8.safetensors (if the inventory shows it missing) | 9.43 GB | https://huggingface.co/black-forest-labs/FLUX.2-klein-9b-fp8 (gated, accept the licence) | T-V2, E-V2 |
| flux-2-klein-base-9b-fp8.safetensors | 9.57 GB | https://huggingface.co/black-forest-labs/FLUX.2-klein-base-9b-fp8 (gated) | T-V3, E-V3 |
| flux-2-klein-base-4b-fp8.safetensors | 4.09 GB | https://huggingface.co/black-forest-labs/FLUX.2-klein-base-4b-fp8 (Apache-2.0) | T-V4 |
| flux-2-klein-9b-nvfp4.safetensors | 5.76 GB | https://huggingface.co/black-forest-labs/FLUX.2-klein-9b-nvfp4 (gated) | T-V5, E-V4 |
| (optional) flux-2-klein-4b-nvfp4.safetensors | 2.46 GB | https://huggingface.co/black-forest-labs/FLUX.2-klein-4b-nvfp4 | extra 4B NVFP4 cell |
| (optional Dev) flux2_dev_fp8mixed + mistral_3_small_flux2_fp8 | 35.46 + 18.03 GB | https://huggingface.co/Comfy-Org/flux2-dev | O-D1/O-D2 |
Core set = **19.42 GB** (base 9B + base 4B + 9B NVFP4), or **28.85 GB** if official 9B FP8 is also missing. Reconfirm what is present first (expected HAVE: flux-2-klein-4b-fp8 4.07, FLUX-KLEIN-9B-FP8-NSFW, qwen_3_4b 8.04, qwen_3_8b_fp8mixed 8.66, flux2-vae 0.34).

> 2026-10-10: the E-I4 cut was wrong. A folder name is never a reason (canon rule 2), and E-I4 can be re-run.
