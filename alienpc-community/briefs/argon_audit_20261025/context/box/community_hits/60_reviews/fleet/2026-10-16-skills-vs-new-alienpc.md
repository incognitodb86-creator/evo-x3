# Skills vs new AlienPc setup — report-only audit (2026-10-16, ~15:10 CT)
Scope: 84 SKILL.md in /home/box/agent-data/workflows. No skills edited. AlienPc probed read-only (file listing, config read, HTTP GET :8080/:8188/:8189 only; no POST/kill/restart).
Source of claimed setup: Max Architect (not Derrick). **No evidence found of Derrick approving llama-swap adoption or 96K** (rg of /workspace/cos for approval wording found nothing; U43 trial config header still says "trial"). → NEEDS DERRICK CONFIRMATION before any skill rewrite.

## Verification on AlienPc
| Claim | Result | Evidence |
|---|---|---|
| llama-swap v265 on :8080 | CONFIRMED | listener = C:\AI\llama-swap-trial\bin\llama-swap.exe `-config D:\AI\director\config\llama-swap.yaml -listen 127.0.0.1:8080 -watch-config`; `--version` = v265 (d1e743f). GET /health = OK; /v1/models 401 (API key required). Binary still lives in a *trial* folder. |
| ONLY model/GPU manager | PARTIAL | Exclusive group `main` (swap+exclusive) present. Can't prove nothing else touches GPU; no Switchyard process seen. |
| Group = comfyui_auto, coding_sc117_strata, vl_judge | CONFIRMED | config (mtime 2026-10-16 13:59). Strata aliases still include `coding_heretic27b`, `coding_huihui27b` (legacy names kept as aliases). |
| ComfyUI at :8080/comfyui | PARTIAL | GET returns 401 (route exists, key-gated); not exercised further. |
| Flash-Next IQ3_XXS, 96K | CONFIRMED (config) | strata-iq3_xxs-switchyard.json `--max-context 98304` (=96K). Contradicts Forge 64K record. File name still says "switchyard". |
| vl_judge = Dark Roast Q8, director + only judge | MODEL CONFIRMED; ROLE UNVERIFIED | Qwen3.5-9B Dark Roast Q8 + mmproj, `-c 65536`. "Director/only judge" is policy, not checkable. |
| Switchyard retired; :8188/:8189 gone | PORTS CONFIRMED | :8188 and :8189 refuse connection. C:\AI\switchyard-upgrade dir still exists; strata cfg filename references switchyard. |
| 7B VL judge gone | PARTIAL | No 7B in C:\AI\vlm\models (only 9B Fable/Dark Roast). |
| Deleted LTX, Wan 2.2, old Flux, IQ2_XS, coder-iq1m | **CONTRADICTED for LTX/Wan/Flux** | Still on disk in TestRuntime ComfyUI\models: `checkpoints\ltx-2.3-22b-distilled…fp8`, `ltx_text_projection`, LTX LoRAs (SexGod_LTX23_*, Sulphur_LTX 2.3, LTX2_3_NSFW_*), `diffusion_models\Wan2_2-TI2V-5B_fp8…`, `vae\wan2.2_vae`, `Wan2.1_VAE`, `unet\flux1-dev-Q4_K_S.gguf`, `vae\ae.safetensors`, text_encoders LTX-2 gemma. IQ2_XS / iq1m: none found under C:\AI\Strata-data\models (CONFIRMED). Old LTX Pipeline install dir not searched by name. |
| Klein 9B + flux2 encoder + FLUX.2 VAE | PARTIAL | FLUX-KLEIN-9B-FP8-NSFW present; flux2-vae.safetensors present; qwen_3_8b_fp8mixed present. Which encoder the graph uses not verified. |
| Pi=Forge, ViMax director, Piscord on hold | UNVERIFIED (policy) | C:\AI\pi-agent, forge-* dirs exist; no ViMax dir in C:\AI top level. |
| 768x1344/1344x768 @24fps; H3 frames%17==5 | UNVERIFIED (policy) | Skills' 124f and 362f both satisfy %17==5. No skill states fps. |
| KEEP from Derrick only; floor = minors guard only | CONSISTENT with skills | Skills already say this. |

Security note: the live config contains a plaintext apiKeys entry (printed in a probe output; not reproduced here). Consider rotation.

## Verdict counts
OK 77 · STALE 6 · OBSOLETE 1 (total 84). fleet-*, gbrain-sync, bot-fleet-audit, alienpc-local-exec-lease, alienpc-stills-pose-edit-prompting (already updated 2026-10-16), ref2va-prompt = OK.

## Non-OK skills
| Skill | Verdict | Lines | Fix |
|---|---|---|---|
| alienpc-ltx-i2v-prompting | OBSOLETE | 2,4,5,10,13,15,18,30,45,59,60,64 | Archive (LTX/:8188/:8189 lane). Hold until Derrick confirms LTX retired — files still on disk. Remove inbound links (hardcore-director L13, community-matrix-cell). |
| alienpc-local-video-ops | STALE | 5,11,15,17,23,26,51,54,57,70 | Replace :8189/:8188 hosts with llama-swap :8080/comfyui (`comfyui_auto`, key-gated, exclusive swap); drop :8188 H2H/LTX Recipe B lines; "Flux.1 Kontext" → Klein 9B only; L22 dynamic-VRAM note re-check under `--lowvram`; add 768x1344/1344x768 @24fps, frames%17==5; canon path L15 (alienpc-ltx-stack) → mark historical. |
| alienpc-hardcore-i2v-director | STALE | 5,13,15,17,33,34,35,55*,66,75,91,105,109 | :8189→:8080/comfyui; delete L34 :8188 baseline, L66 H2H arm; L13 drop LTX-prompting pairing; L33 drop Flux.1 Kontext; add vl_judge (Dark Roast) as judge; add res/fps/frames rule. |
| alienpc-community-matrix-cell | STALE | 12,14,54,60,61 | L14 "Flux+Max on :8189 / LTX on :8188" → single llama-swap host; remove LTX matrix cells; research path L54 historical. |
| alienpc-max-movie-director | STALE | 11 (65 role) | L11 `:8189` → `:8080/comfyui`; add ViMax director pipeline + vl_judge; res/fps/frames. L65 Max Architect "takes the lease" – keep, confirm. |
| cos-subagent-dispatch | STALE | 62,64,65 | L62 "Comfy/LTX/Ten Eros" → "ComfyUI (llama-swap)/Max H3"; L64 `HardcoreNSFW-LTX-Pipeline` workspace dead → TestRuntime ComfyUI; L65 "LTX Seat" → generic. |
| artframe-quality-bar-95 | STALE (minor) | 110 | "live Pipeline" (= old LTX Pipeline :8188) → current llama-swap ComfyUI. (artframe-ops L51, artframe-i2v-paste-gate L52 say "Comfy" generically — OK.) |

## Top 10 fixes
1. Get Derrick confirmation on llama-swap adoption (vs U43 "don't adopt") and 96K (vs Forge 64K) before rewriting.
2. Archive alienpc-ltx-i2v-prompting (after #1 + LTX retire confirm).
3. Global :8189/:8188 → `http://127.0.0.1:8080/comfyui` (comfyui_auto) in local-video-ops, hardcore-director, community-matrix-cell, max-movie-director.
4. Remove "LTX Recipe B on :8188 baseline/H2H" doctrine (local-video-ops L23/51, hardcore L34/66, matrix-cell L14).
5. Add exclusive-swap note: one job at a time; ComfyUI jobs must use sync hold (ComfyClient.run) so a strata/vl_judge swap doesn't kill them.
6. Add video spec 768x1344/1344x768, 24 fps, frames%17==5 (124f/362f OK) to Max skills.
7. Name vl_judge (Dark Roast Q8) as judge/director in hardcore-director + max-movie-director; drop any 7B judge refs (none found).
8. cos-subagent-dispatch L62–65: kill `HardcoreNSFW-LTX-Pipeline` and "LTX Seat".
9. Drop Flux.1 Kontext from production SoT (local-video-ops L11/51, hardcore L33) — but flux1-dev still on disk; confirm.
10. Disk cleanup claim false: LTX 2.3, Wan 2.2, flux1-dev still in TestRuntime models — ask Max Architect/Derrick before treating as deleted. Also rotate plaintext API key and move binary out of llama-swap-trial.

## rg sweep
No hits anywhere for: Switchyard, iq1m, IQ2_XS, 7B judge, vl-judge, Huihui, 64K, queue_dynvram, beta5, old resolutions, fps. Hits only in the 7 non-OK skills above (+ ref2va-prompt L12/113 "no LTX paste" negatives — harmless) and alienpc-stills-pose-edit (already new-setup).
