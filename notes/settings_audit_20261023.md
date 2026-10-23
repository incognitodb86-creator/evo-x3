# H3 hc render settings audit vs TenStrip + community (Max, 2026-10-23 ~6:35 PM CT)

Graph read: `C:\AI\community\runs\ali147_pool_hc_r3b_s51130003\request.api.json` (the newest hc graph, BQ1 rewire; IM1 builds from it). Read-only; no explicit prompt text quoted.
Sources:
- TenStrip model card: https://huggingface.co/TenStrip/10Eros-Max
- TenStrip discussions: https://huggingface.co/TenStrip/10Eros-Max/discussions
- Reddit watch digest: /workspace/cos/research/reddit-h3-watch/2026-10-12-digest.md (Oct 12-16; r/StableDiffusion + r/comfyui)

| Setting | Ours (r3b graph) | Recommended | Match | Source |
|---|---|---|---|---|
| Model | 10Eros_Max_h3_8stepTURBO_beta6_int8 (int8 convrot) | beta6 TURBO; int8 at cicalooo/10Eros-Max-h3-int8-convrot | yes | model card |
| Sampler / scheduler | euler / simple | Euler/simple 4-8; res_multistep/simple 6-8 = "my go-to for best motion quality"; LCM/simple 6-8 = best turbo audio | partly (valid, but not the author's motion pick) | model card |
| Steps | 10 + 10 (c0, c1) | beta6 reference config: "slow 8-12 step reference model"; turbo lists 4-8 | yes (8-12 band) | model card |
| CFG / guider | BasicGuider (cfg 1, no negative) | turbo = cfg 1; the community says state wanted things positively, and "don't X" lines add X | yes | digest run 1 #5, run 5 #4 |
| Shift | video 10 / audio 3 | "Samples on 10/3 shift" | yes | model card |
| Sparse attention | BlockSparseAttention VSA keep 10%, start 0.2 | "Fastv2 VSA sparse node settings" OK; "SLA sparsity seems to destroy it" | yes (VSA, not SLA) | model card |
| Attention backend | comfy kitchen attention | VEDA causes white flash frames; ck is fine | yes | digest run 4 #1 |
| Cache / spectrum | none | "No cache or spectrum if doing reference" | yes | model card |
| Resolution / fps | 1344x768 (1.03 MP), 24 fps | >=1.5 MP for faces in wide shots, or a FaceRefine post-pass | no (lower than the face advice) | digest run 1 #4 |
| Reference image size | ref_image_size "match" | "max" instead of "match" for sharper faces | no | digest run 1 #4 |
| Chunking | c0 124 f + continuation window 119 f, overlap 22 = 243 f = 10.125 s | best clips 2-6 s then stitch; long-clip burn grows across chunks | partly | digest run 1 #5, run 6 #1 |
| Anti-burn on continuation | none (h3_antiburn_universal_v1 is on disk, unused) | anti-burn LoRA on continuation clips only, start 0.5 | no | digest run 6 #1, run 7 #1 |
| Concept LoRAs | none in graph | beta6 TURBO "other concept loras load on top ... lower strength 0.2-0.6" | no (none used) | model card |
| Prompt | v2 structured prompt, single pass | community: paste the whole structured prompt twice; follow MiniMax's ref prompt guide (VIDEO_PROMPT_WRITING_GUIDE_ref_en.md); give each ref a distinguishing description | partly | digest run 1 #3, run 5 #3 |
| References | c0/c1: start still (body/scene) + 2 face crops (BQ1 rewire) | 1-2 key-pose refs for hard two-person moves; room/set ref for layout | partly | digest run 5 #2, run 6 #4 |
| RIFE / interpolation | none (Frame-Interpolation installed, unused) | not needed at a native 24 fps | yes | - |
| VRAM flags | not read (ComfyUI was not running during the audit) | dynamic VRAM; --lowvram dropped (ALI-162 card) | unknown | ALI-162 |
| ComfyUI version | per ALI-162: 0.42.1 pending card | 0.38.x pin advised Oct 12-16 (INT8 / LoRA breakage, slowdowns) | check | digest runs 1, 2, 7 |

## Community LoRAs / nodes not in use, and which TASKS item covers each

| Item | On disk? | Covered by |
|---|---|---|
| h3_antiburn_universal_v1 (continuation, 0.5) | yes | none, so it goes in IM1(b) candidates |
| MysticXXX_MMH3-V4, HMNSFW-AIO-V2.5, MM-H3 concept LoRAs (0.2-0.6) | yes | none, so it goes in IM1(b) candidates |
| H3-Realism-People / Character-Swap LoRAs (Forge researched, sz_*.json) | no | BQ1 research; RL1 (character LoRA) |
| Character / identity LoRA training | - | RL1 (training HELD) |
| PuLID / ReActor / FaceRefine for faces | PuLID-Flux, reactor installed | RF1 (face research) |
| 2906001 All-In-One Uncensored graph + merged checkpoint | download | HB2 |
| 27B vision prompter | download | HB1 |
| 7B prompt rewriter (MiniMax-H3-Prompt-Rewriter, installed) | yes | PW1 / HB3 |
| Infinite-Creation end to end | download | HB4 |
| H3-Continuum (installed) | yes | B2 |
| Latent upscaler (2 node packs installed) / two-pass sharpen | yes | none |
| H3 Clip Refiner (noEmbryo, color drift) | no | none |
| Refmods (Load/Apply Refmods) | ? | none (parked C2) |
| Seed screening (half-step previews) | - | none |
| Audio (voices) | - | RA1 |
