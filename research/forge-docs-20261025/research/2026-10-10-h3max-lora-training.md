# Training our own LoRA for MiniMax-H3 / 10Eros-Max beta6 (AlienPc, 16 GB): research + first-run plan (2026-10-10)

**Scope.** LoRA training for TenStrip 10Eros-Max **beta6** (`10Eros_Max_h3_8stepTURBO_beta6_int8.safetensors`, 21.71 GB, a "mostly-reference hybrid" with a custom 8-step turbo baked in). Dataset is Derrick's own **original fictional adult characters** (Flow / Nano Banana stills). **No real people, no celebrity-named LoRAs or RefMods.**
**Hardware.** AlienPc: RTX 5070 Ti 16 GB (sm_120, ComfyUI log `Total VRAM 16275 MB`), Core Ultra 7 265KF, **63.7 GB RAM** (log `total RAM 65235 MB`), Windows 11. **Free disk on AlienPc is UNKNOWN.** No Cos record has it, so it has to be measured before any download (P11 gate).
**Mode.** Research only. Nothing was installed, downloaded or run on AlienPc.
**Builds on.** `2026-10-10-face-lock-lora-and-methods.md` (item 9: ai-toolkit numbers, the note.com 12 GB recipe, the RefMod and FaceRefine lanes), `2026-10-05-max-h3-face-lora-hunt.md`, `2026-10-09-h3-face-lock-prompting.md` §11.5 (anatomy LoRAs and their beta6 strengths), `2026-10-08-10strip-h3max-optimal-vs-current.md`. Those notes are not repeated here.
**Labels.** [OFFICIAL] = model, trainer or Comfy docs/source · [AUTHOR] = tool or checkpoint author (shootthesound, TenStrip, malcolmrey) · [COMMUNITY] = user reports · [INFERRED] = our reasoning. Sources accessed 2026-10-10, ~9:58–10:40 AM CT.

---
## TL;DR
1. **Lead trainer: Fizgig** (shootthesound, v7.2.x, repo pushed 2026-10-09). It is the only H3 trainer that is native on Windows (installer `.bat`), has a **documented 16 GB tier** (int8 base with ~36 blocks streamed one way), and puts a ComfyUI-ready LoRA "straight into ComfyUI's H3 workflows, including the pruned inference builds" [AUTHOR]. The backup is musubi-tuner, which is official-quality, verified on Windows, and slower. ai-toolkit is third, because a zero-gradient bug on the pruned default (PR #1046) is still open and there are Windows hangs.
2. **Compatibility with beta6: yes in principle.** There is no key mismatch, because every trainer skips the AdaLN tensors and trains only `attn`/`mlp` linears, and Comfy only drops adaln keys on pruned builds [OFFICIAL]. Community LoRAs trained on stock H3 already work on 10Eros at 0.4–0.8 [COMMUNITY]. Expect a **weaker or shifted effect**: TenStrip says most LoRAs "aren't trained on reference and will impact it negatively", and he recommends 0.2–0.6 for concepts and 0.5–1.0 for new LoRAs [AUTHOR]. The baked turbo exposes overtraining (Fizgig #118) [AUTHOR].
3. **Train on stock `minimax_h3_fl2va_pruned_int8_convrot.safetensors`** (Fizgig's default and most-tested base) with the Circlestone adapter, on **stills at 0.25 MP**, Fast preset (rank 8, Automagic v3), and **preview through the Turbo LoRA** so each epoch is judged roughly as beta6 will render it.
4. **Expected time on our card:** about 1.5–2.5 h for a 35-image × 50-epoch run including caching and sparse previews [INFERRED from the field figure of 1.1–1.3 s/step at 0.25 MP on 12–16 GB cards]. **New disk:** about 45 GB (about 66 GB with the optional ref2va base).
5. **Biggest gain per hour [INFERRED]:** (a) a **character LoRA plus a RefMod of the same character** for face lock ("RefMod + identity LoRA beats either alone") [COMMUNITY]; (b) a **sheer-fabric concept LoRA** trained on many different women, so it learns fabric rather than a face. For hands and anatomy, test the existing anatomy LoRAs first (§11.5 of the 10-09 note). Do not train hands from AI stills.
6. **Dataset gate before any run:** the box holds only **8 blonde-elf picks**, all full-body 768×1376 with faces about 100 px tall. That is too few and too far away for identity. Build 30–40 images of the **same** fictional character, including about 12 face and upper-body crops at ≥1024 px, and run the provenance/likeness check (see Risks).

---
## Q1. Which trainers support H3 today, and on Windows?
| Trainer | H3 support | Windows | 16 GB | Notes | Label |
|---|---|---|---|---|---|
| **Fizgig** (shootthesound/Fizgig, 509★, v7.2.x) | LoRA, LoKR (not recommended on H3, #86), slider, experimental full fine-tune, **RefMods**; trains on photos, clips, audio and voice | **Native**: `install_fizgig.bat`, then `run_fizgig.bat` (CUDA 12.8 wheels, RTX 30/40/**50**; driver 555+) | **Yes**: "MiniMax H3 … Smallest card 16 GB". Auto picks **int8 base + ~36 blocks streamed** at ~15 GB free | Default training adapter is Circlestone, so de-distillation is handled. Text token refiner is off and blocks 0–5 are excluded (anatomy/colour). EMA 0.98 by default. Turbo-LoRA previews. Output loads in ComfyUI | [AUTHOR] docs/MINIMAX_H3.md, INSTALL.md |
| **musubi-tuner** (kohya-ss) | T2VA, FL2VA, Ref2VA, one-frame image LoRA (exp., added 2026-09-16); three anti-de-distillation loss methods incl. **teacher matching** (`subject_ref`) | Yes: Win10 + 3080 20 GB smoke test (Discussion #1061); `triton-windows` for fused int8 kernels | Yes with `--blocks_to_swap 48 --block_swap_h2d_only`. note.com: 12 GB 4070, 100 stills, 1,000 steps in 2 h 45 m | Outputs Diffusers-format keys (`diffusion_model.blocks.N…lora_A/B`) that ComfyUI and other tools load. Fizgig #71: musubi was *faster* than Fizgig on a 5070 Ti, but only because Fizgig's teacher option was on | [OFFICIAL] docs/minimax_h3*.md; [COMMUNITY] |
| **ai-toolkit** (ostris) | `minimax_h3` (FL2VA) and `minimax_h3_ref2va`; Ostris training adapters; UI | Runs on Windows, but #1050 (Win 11 + 5090: clean hang on first step with triton, OOM without) and #1017 (triton `python*.lib` path) | 12 GB recipe works (note.com: 7.4 GB VRAM, 21.7 GiB RAM, 10.3 s/step) | **#1046 (open PR, not merged): the pruned default can train zero gradients** (every `lora_B` = 0, from an fp16 adaLN overflow). #991: "videos pure noise", "LoRA did not look like the data" | [OFFICIAL] docs; GitHub issues |
| **diffusion-pipe** (tdrussell) | T2I / T2VA only (2026-08-06); CFG-augmented training; trains directly on int8 convrot | DeepSpeed, so Linux/WSL2 only [INFERRED] | Pipeline-parallel design; no 16 GB H3 figure | Saves ComfyUI format | [OFFICIAL] README, supported_models.md |
| **SimpleTuner** (bghira) | PEFT LoRA, FL2VA, convrot int8/int4, "drift distillation" loss | Linux-first [INFERRED] | Smallest shipped example is `…int8-24g.peft-lora+ramtorch`. **No 16 GB example** | — | [OFFICIAL] quickstart MINIMAX_H3.md |
| **OneTrainer** | **No H3 support found** (README has no mention; issue #1681 "Int8 conv rot" is open) | — | — | — | [OFFICIAL, by absence] |
| Others | fal.ai Ref2VA trainer (paid cloud, ~$30 per 2,000 steps; see 10-05 note); AcademiaSD all-in-one trainer (Reddit 1wxey7r, 2026-10-04; unvetted); IAmIronMan42 minimal trainer (multi-GPU) | — | — | — | [COMMUNITY] |

## Q2. Will a LoRA trained on stock H3 work on beta6 hybrid TURBO int8?
- **Keys: no mismatch expected.** Comfy: "A LoRA distilled on the full build carries adaln weights with no matching tensor in the pruned build… that part of the LoRA is skipped" [OFFICIAL docs.comfy.org H3]. ai-toolkit sets `ignore_if_contains: ["adaln_proj"]` [OFFICIAL]. musubi targets `attn.qkv_proj, attn.out_proj, mlp.fc1, mlp.fc2` [OFFICIAL]. Fizgig: "nothing a LoRA learns lives there [AdaLN]: you train against the exact weights you deploy on" [AUTHOR]. beta6 int8 (21.71 GB) is the same size as a pruned int8 (20.97 GB) and keeps standard block names, so these keys should load [INFERRED]. Check the ComfyUI console for "lora key not loaded" on the first load.
- **Effect: weaker or shifted.** beta6 = "built mostly-reference hybrid… on the delta1024 h3 merge", with grafts "to attn layers at a low level" (from LTX 2.3, Wan 2.2 and Krea 2) [AUTHOR README]. Those are the same attn layers our LoRA trains, so the LoRA lands on shifted weights [INFERRED]. TenStrip says concept LoRAs "load on top more readily, usually needing lower strength 0.2–0.6"; new LoRAs need 0.5–1.0. In Sep 12 comments he said most LoRAs "aren't trained on reference and will impact it negatively" [AUTHOR]. Community: Fingering v1.1 "0.8 with 10ErosMax… golden touch"; Free Pussy "works great with Eros 5 turbo at 8 steps"; H3 Innie at 8-step turbo needed 0.4–0.5 to stop the background snapping [COMMUNITY, 10-09 note §11.5]. None of these reports is a key-mismatch report.
- **Which base to train on:**
  1. **Stock FL2VA pruned int8 (recommended for Run 1).** It is Fizgig's default and best-tested base. Most community LoRAs that work on 10Eros were trained on FL2VA. Circlestone's single adapter covers it [AUTHOR + COMMUNITY].
  2. Stock Ref2VA pruned int8 (+21 GB). This is closer to beta6's "mostly-reference" weights [INFERRED]. Fizgig has a Training Base picker and an Ostris ref2va adapter, but says the ref2va DiT is needed "only for reference distillation". Reference distillation (the teacher) **does not fit 16 GB** (Fizgig #71, author: "On 16 GB the teacher is out of reach"). Whether a plain LoRA can be trained on ref2va in Fizgig is UNVERIFIED. Keep it as a Run-2 A/B.
  3. Train **on beta6 itself**. musubi detects ComfyUI int8 convrot checkpoints "from their tensor structure", and its guidance loss "works on a pre-quantized INT8 base" [OFFICIAL]. But only the released bases are supported, and the de-distill adapters were made for stock weights. Experimental only [INFERRED].
- **8-step turbo handling:** H3 is CFG-distilled, and plain flow training "washes out"; image training "breaks structurally within about 50 steps" [OFFICIAL musubi]. So use an adapter, guidance loss or teacher. Fizgig handles this automatically. On the turbo side, a LoRA that "moved that far still looks fine at 20 steps but falls apart under a 6-step Turbo, which has no margin for it" [AUTHOR, Fizgig #118, a 300–600-image set run 10× too long]. Mitigations: lower rank (8), keep **earlier epochs**, use EMA, and judge previews **with the Turbo LoRA on** (Fizgig Preferences → `minimax_h3_turbo_v4_step600.safetensors`, larryvrh, ~780 MB). Final judgement is always on beta6 in ComfyUI.

## Q3. Fitting on 16 GB
- **Fizgig Auto (close ComfyUI first; it reads free VRAM):** ~15 GB free gives **int8 base + ~36 of 50 blocks streamed**. Streaming is one-way H2D, 6.4× faster than round-trip swap [AUTHOR]. 4-bit HQQ is optional (~4.8% base error); NF4 has ~9.5% error. Prefer int8 (~0.17%).
- **Resolution and frames on 16 GB [AUTHOR table]:** stills default to **0.25 MP** ("the extra resolution has not paid for itself"). Clips are possible up to **56 frames at ≤0.25 MP only**; 73+ frames do not fit at 16 GB. A 22-frame clip costs ~7× a still per step. Previews cap at 768×640, 22 frames.
- **RAM:** H3 wants 32 GB for training and **48 GB with previews**. Leave the Windows paging file system-managed, or previews die with error 1455. We have 64 GB: OK if ComfyUI, the llama-server LLM and browsers are closed [AUTHOR + INFERRED]. Fizgig parks the TE in RAM (~40 GB free needed for the fast path).
- **musubi equivalents:** `--int8_convrot_base`/pre-quantized `--dit`, `--blocks_to_swap 48 --block_swap_h2d_only`, `--gradient_checkpointing`, NVFP4 TE + `--text_encoder_blocks_to_swap 50` for caching, `--nvfp4_scaled_mm` (Blackwell, PyTorch ≥2.10). **FP8 bases are rejected** [OFFICIAL].
- **Image-only vs image + short video:** use image-only for Run 1. Stills teach the look (identity, fabric), and clips teach motion and voice [AUTHOR]. Clips cost 7–37× per step and the Circlestone adapter is best for stills. Use Ostris instead for clip-heavy sets [AUTHOR, #142; one dissent: firsack got better results with Ostris on 96–224 px camcorder stills]. Add 4–6 clips of 22–39 frames from our own H3 outputs only if Run 1 stiffens motion [INFERRED].

## Q4. Dataset
- **Count:** Fizgig's Fast and likeness presets are tuned for **30–60 images** [AUTHOR #118]. note.com used 31–32 (ai-toolkit) and 100 (musubi) [COMMUNITY]. musubi validated its subject_ref recipe on a **20-image** character set [OFFICIAL]. Target **35** for us.
- **Shot mix:** whole-body-only sets do not lock the face. note.com needed an extra 500 face-only steps because "the face did not look very similar" [COMMUNITY]. Use ~35% face/shoulders crops, ~35% waist-up, ~30% full-body [INFERRED].
- **Variety:** front, ¾ left/right, profile, over-shoulder, back; neutral, smile, open-mouth, eyes-closed and lidded expressions; warm, cool, hard, soft, backlit and wet-look lighting; at least 6 outfits, including the sheer/lace ones she is used with, plus 2–3 settings that are **not** stone halls, so the LoRA does not learn the background [INFERRED + AUTHOR tip: "give one sample prompt something your dataset doesn't have"].
- **Resolution and buckets:** the source stills are 768×1376 (9:16). Fizgig resizes to Target MP (0.25 MP, about 384×672 at 9:16) on a /32 grid. Feed **≥1024 px face crops**, because a 100 px face in a full-body still gives the model only ~3×3 tokens [INFERRED from 32 px/token]. Keep a mix of 9:16, 3:4 and 1:1 crops.
- **Captions:** natural-language and scene-first, using the Fizgig Captions tab (Qwen3-VL captioner). **Trigger word first** (e.g. `lyraelf`, a made-up token). Describe pose, framing, outfit, setting and light. **Keep fixed identity traits (face, eye colour, ears) out of the caption** so the trigger carries them; this is the logic of musubi's teacher recipe, "appearance left out" [OFFICIAL]. Caption dropout 0.05 [AUTHOR]. musubi suggests stating that stills are silent ("sound: silent still") [OFFICIAL 1f doc]. Do not train the text token refiner [AUTHOR].
- **Video clips:** not in Run 1. If added later, use Gizmo to make 24 fps clips of 22/39/56 frames, /32 dimensions, cropped to her, muted if the audio is not worth learning [AUTHOR].

## Q5. Hyperparameters (what worked)
| Recipe | Rank / α | LR / optimizer | Length | Other | Source |
|---|---|---|---|---|---|
| **Fizgig "MiniMax H3 Fast"** | **8 / 8** | **Automagic v3 starting at 1e-6** (sets its own LR; leave the box at 1e-6) | **50 epochs** ("likeness in a few hundred steps") | 0.25 MP, Training Structure "Likeness and Style", Training mode Default (blocks 20–49), EMA 0.98, Circlestone adapter, TREAD on | [AUTHOR] |
| Fizgig rank-16 preset | 16 / 16 | Automagic v3 | 60 epochs | for larger sets | [AUTHOR] |
| Fizgig full-precision adamw option | — | adamw ("single biggest likeness gain on H3") | — | for large sets, LR 1e-4 (2e-4 overshoots at 300–600 images) | [AUTHOR #118] |
| musubi subject_ref teacher (image identity) | 16 | **3e-4, warmup 50** | **~500 steps** | `--h3_teacher_condition_sigma_min 0.15 --h3_teacher_loss_mag_weight 0.5 --h3_teacher_loss_dc_weight 0.3`, trigger can be `<Subject 1>` | [OFFICIAL] |
| musubi guidance-loss stills | 16 / 16 | AdamW8bit 1e-4, cosine, warmup 50 | 1,000 (+500 face-only) | `--h3_guidance_loss_scale 4.0 --h3_guidance_loss_sigma_min 0.15`, swap 48 H2D | [COMMUNITY note.com] |
| AkaneTendo25 musubi fork | — | Automagic v3, LR 1e-4, wd 1e-4 | char LoRA "perfect in ~2,700 steps" | distill scale 3.5–4, contrastive, **timestep sampling sigmoid** "(important!)", spatial jitter 0.1–0.2 | [COMMUNITY r/SD 1vqly7i] |
| ai-toolkit (Guidance + adapter default) | 16 / 16 | AdamW8bit 1e-4 | 2,000 default; "clearly apparent at 750, done by 1,500" | `do_guidance_loss 3.5`; caveat #1046 | [OFFICIAL + COMMUNITY] |
| Fizgig default-preset user | 16 | default | 28 photos converged ~3,500 steps (~120 epochs); "not as good as Krea 2" | early (Aug) version | [COMMUNITY r/SD 1vemx58] |
- **Timestep sampling:** H3 in musubi accepts only `uniform`, `none`, shift 1.0. H3 derives the video and audio sigmas itself with shifts 12 and 3 [OFFICIAL]. Fizgig exposes this as "Training Structure" [AUTHOR]. Do not paste image-model shift presets.

## Q6. Time, files and disk on AlienPc
- **Time [INFERRED]:** field figures are 1.1–1.31 s/step for stills at 0.25 MP on 12–16 GB-tier cards (Fizgig #102). On a 5070 Ti with 36 blocks streamed, plan on **~1.5–3 s/step**. 35 images × 50 epochs = 1,750 steps ≈ **45–90 min**. Add first-launch TE streaming and caching (~10–15 min) and previews every 5 epochs (≈10 × 1–2 min). **Total ≈ 1.5–2.5 h.** The musubi equivalent is probably 3–6 s/step (note.com 4070: 10 s/step) [INFERRED]. Never tick Reference distillation on 16 GB: caching crawls to a "freeze" (#71).
- **Files** (Comfy-Org/MiniMax-H3 unless noted):
| File | Size | On AlienPc? |
|---|---|---|
| `diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors` | ~21 GB (Fizgig) | probably **no** (we run beta6) — check |
| `text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` | 15.69 GB | **yes** (current TE), reuse by path |
| `vae/minimax_h3_video_vae_fp16.safetensors` | 5.21 GB (Fizgig lists ~4.9 GB) | we run `…video_vae_int8_convrot`; whether Fizgig accepts the int8 VAE is UNVERIFIED, so plan on fp16 |
| `vae/minimax_h3_audio_vae_fp32.safetensors` | 605 MB | **yes** (optional for still-only runs) |
| Circlestone `circlestone-labs/MiniMax-H3-Image-Training-Adapter` | ~620 MB | no (Fizgig updater fetches it) |
| Turbo LoRA `larryvrh/MiniMax-H3-Turbo-Lora/minimax_h3_turbo_v4_step600.safetensors` | ~780 MB | maybe — check ComfyUI `loras/` |
| *(Run-2 option)* `diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors` + Ostris `minimax_h3_ref2va_training_adapter_v1.safetensors` | 20.97 GB + 155 MB | no |
- **Disk:** Fizgig venv ~10 GB + DiT ~21 + VAE ~5.2 + adapter 0.6 + turbo 0.8 + caches ~2–5 + checkpoints (rank 8 ≈ 75 MB × 50 epochs ≈ 3.7 GB; prune later) ≈ **45 GB new**, **~66 GB** with the ref2va option. Require free space ≥ planned + 10 GB (P11).

## Q7. Character LoRA vs concept/style LoRA: what helps our weaknesses most
| Weakness | Best lever | Why | Label |
|---|---|---|---|
| Face lock (post-turn drift, weak 2nd face) | **Character LoRA + RefMod of the same OC**, used together with the existing refs | A LoRA holds identity in the weights, so it does not depend on the ~1k ref tokens rebuilding the face after a turn [INFERRED]. malcolmrey: "RefMod + identity LoRA beats either alone" (Jinx, epoch 60). shootthesound: RefMods "cannot know as much… don't generalise as well"; LoRAs bleed in multi-character shots. On ref2va with good refs, a LoRA alone added little (note.com) | [COMMUNITY + AUTHOR] |
| Sheer fabric | **Concept LoRA "sheer fabric"** (Fizgig Style preset, rank 8) on **many different women** (the sheer-bikini picks + `bikini_cands.txt`, 209 lines) | Varied faces mean it learns the material, not a face. Fizgig's style example: 341 stills, heavily captioned, LoRA 0 vs 1.0 clips (v6.2.0). Use 0.2–0.6 on beta6 | [AUTHOR + INFERRED] |
| Anatomy | **Test existing anatomy LoRAs first** (Synth Pussy 0.6, HMPussy 0.5; 10-09 §11.5) | Already trained on real-photo data; training our own from AI stills adds no new truth | [COMMUNITY + INFERRED] |
| Hands | Do not train | AI-still datasets carry their own hand errors; use prompt staging, steps 12 and FaceRefine-style post passes | [INFERRED] |
Reddit "Are MiniMax spicy LoRAs a lie?" (1wbpwcq, 2026-09-09): many users say Civitai NSFW LoRAs rarely match their samples and look "AWFUL" on SFW workflows. "You can try the loras but they don't help much" (JesusShaves_). WholeBrain9977: "(almost) all the issues were resolved by using the Eros model". One working stack used MysticXXX 0.5–1.0 + turbo 0.8 at 8 steps Euler/simple. Yasstronaut: fl2va or a hybrid works better than stock ref2va [COMMUNITY]. Also r/SD 1vqly7i "H3 is a great model but the training is bad": character LoRAs are OK, new concepts are "super frustrating" [COMMUNITY]. **Meaning for us:** a character LoRA is the most proven type on H3, and a concept LoRA is riskier. Both must beat beta6 + prompt alone in a blind A/B before they ship [INFERRED].

## Q8. Evaluation protocol
1. **Fizgig gallery first:** sample prompts include one shot the dataset lacks (e.g. "looking over her shoulder from a low angle, city rooftop at night"). The last epoch that still follows it is the candidate [AUTHOR]. Previews use the Turbo LoRA and 22 frames.
2. **ComfyUI A/B on beta6** (seed 43029049, Euler/simple 8 steps, shift 10/3, 768 short edge; existing pin and refs). Cells from `/workspace/maxops/facelock-v2-2026-10-10/`: **FV2_C0R_POOL** (5 s), **FV2_LP10_POOL10S** (10 s, turn), **FV2_TR1_TWOREF** (two-ref bleed test).
   - Control = the v2 face-block prompt, no LoRA.
   - Arms = LoRA at **0.4 / 0.6 / 0.8 / 1.0**, trigger word added to the face block, then the best strength × 2–3 checkpoints (e.g. epochs 25 / 35 / 50).
   - Then the best arm + a RefMod built from the same images (`ComfyUI-MiniMaxH3Mod`, GO needed).
3. **Scoring:** the existing protocol, face at 0/2/4/6/8/10 s against frame 0, plus the VR scores. Add motion quality, outfit/prompt adherence and audio. n=1 seed is directional; re-run winners on 2 more seeds.
4. **Overfit signs:** the stone-hall background or 9:16 full-body framing returns unasked; silver boots or circlets appear unprompted; skin and grain turn rough only under the 8-step turbo (#118 pattern); motion stiffens; her face appears on the second subject in TR1 or couple shots; audio degrades; anatomy changes at >0.6. If these appear, step back one checkpoint or lower the strength.

## Q9. Risks and gotchas
- **Likeness/provenance gate [INFERRED, policy].** A LoRA permanently encodes whatever face the dataset carries. The box also holds celebrity-named Flux/LTX LoRAs and `sydney-*` folders (10-05 inventory), and the 10-09 doppelganger note exists because AI faces can drift toward real people. Before training, confirm every image came from original-character prompts with no person-named LoRA or ref in the chain. Provenance only: per Derrick's rule, no bot runs likeness or resemblance checks, and vision tools never judge whether a face is real.
- **License:** the MiniMax-H3 Community License has territory exclusions; SimpleTuner lists "authorization required in US/EU/UK/KR". beta6 also carries the LTX 2.3 / Wan 2.2 / Krea 2 licenses [AUTHOR README]. Already flagged 10-05: legal/ops check, local private use only.
- **Fizgig on 16 GB:** never tick Reference distillation (caching freeze, #71). Close ComfyUI before launch, because Auto sizes from *free* VRAM. Still previews can OOM at VAE decode on 16 GB (#134, fixed in a later release); training continues regardless. LoKR is not recommended on H3 (#86). RAM shortages look like "CUDA out of memory" during caching. LoRA names with invalid characters kill the run at the first save (#70).
- **ai-toolkit:** silent zero-gradient LoRAs on the pruned default (#1046 open). Check that `lora_B` ≠ 0 before trusting any run. Windows triton hang (#1050).
- **musubi:** int8 backward GEMM route issue (#1059) and validation-cache leak (#1060), per the lcdrzx runbook. Training samples under `--base_weights` show the de-distilled model, not base + LoRA [OFFICIAL].
- **beta6:** the grafts sit in the same attn layers, so strength needs a sweep. The LoRA may weaken reference adherence (TenStrip). The custom turbo exposes overtraining. No cache or spectrum with reference runs [AUTHOR].
- **Other:** TenStrip calls beta6 an interim release before Sulphur H3 v1.0, so a LoRA tuned to beta6 may need a re-check later [AUTHOR]. Disk free is unknown. LoRA + RefMod both cost reference tokens (RefMod ≈ image tokens) [COMMUNITY].

---
## Proposed first run (⚠ AWAITING DERRICK'S GO; nothing below has been done)
**Goal.** A character LoRA for the original blonde-elf OC that improves face lock on beta6 without hurting motion.
**Trainer.** Fizgig latest (7.2.x), Windows native, on AlienPc.
**Base.** `minimax_h3_fl2va_pruned_int8_convrot.safetensors` + Circlestone adapter (Fizgig default). Run-2 A/B option: ref2va pruned int8 + Ostris ref2va adapter, if Fizgig allows a plain LoRA on it.

**Steps**
0. **Gates (Derrick):**
   - (a) GO for install and download.
   - (b) AlienPc free disk ≥ 55 GB on the models drive (`Get-PSDrive`).
   - (c) The elf character confirmed original (provenance only).
   - (d) License acknowledgement.
1. **Dataset (box, reversible) → `/workspace/maxops/lora-elf-v1/`:**
   - The **8 picks** from `/workspace/maxops/blonde-elf-picks-2026-10-09/` (E2, E3, E6, E7, E8, E9, E10, E11).
   - ~15 more from the same-character candidates in `blonde-elf-picks-2026-10-09/cands.txt`, which point to `/workspace/flow-export-2026-10-09/ex/…` (59 listed). Keep only images that clearly show the same face.
   - ~12 new face/upper-body stills of her at ≥1024 px (Flux 2 Klein / Nano Banana edits: front, ¾ each side, profile, 4 expressions, 3 lighting set-ups, 2 non-stone settings).
   - **N = 35.** Crop faces from the full-body picks as extra items.
2. **Captions:** Fizgig Captions tab, trigger `lyraelf` first. Describe pose, outfit, setting and light; leave out face, eyes and ears. Add "silent still". Dropout 0.05.
3. **Install** (`install_fizgig.bat`). In Preferences, point the TE at the existing nvfp4 file. Download the fl2va pruned int8, fp16 video VAE, Circlestone adapter and Turbo v4 (if not present). Paging file system-managed.
4. **Settings:** Base Model MiniMax H3. Preset **✨ MiniMax H3 Fast** (rank 8, Automagic v3 at 1e-6, 50 epochs, 0.25 MP, Likeness and Style, Training mode Default, EMA 0.98, TREAD on). Blocks Swap and Base Precision on **Auto**. **Reference distillation OFF.** Train text token refiner OFF. Save every epoch. Previews: still + one 22-frame clip every 5 epochs, Turbo LoRA on, including one out-of-dataset prompt.
5. **Run:** close ComfyUI, llama-server and browsers. Expected **~1.5–2.5 h** [INFERRED]. Watch the console for the planner line (int8 + ~36 swap) and for OOM/1455 errors.
6. **Pick 3 checkpoints** from the gallery (last one that still follows the out-of-dataset prompt, plus its neighbours). Copy them to ComfyUI `models/loras/`.
7. **A/B on beta6** per Q8: FV2_C0R, FV2_LP10, FV2_TR1 × {off, 0.4, 0.6, 0.8, 1.0} at the best epoch, then epochs at the best strength, then + RefMod. Score and write up in `cos/brain-staging/60_reviews/max-clips/`.

**Fallbacks.** If Fizgig misbehaves on the 5070 Ti, use musubi-tuner one-frame `subject_ref` teacher matching (rank 16, 3e-4, warmup 50, 500 steps; `--blocks_to_swap 48 --block_swap_h2d_only`; NVFP4 TE + `--text_encoder_blocks_to_swap 50`). Run 2: the sheer-fabric concept LoRA (Fizgig Style preset, 40–60 sheer stills of varied women from the sheer-bikini picks and `bikini_cands.txt`, no faces cropped).

---
## Sources (accessed 2026-10-10 CT)
**Official / trainer docs**
- Comfy H3 guide (LoRA build matching, adaln skip): https://docs.comfy.org/tutorials/video/minimax/minimax-h3
- Ostris ai-toolkit Ref2VA: https://ostris.com/docs/ai-toolkit/models/minimax-h3-ref2va
- musubi-tuner: https://github.com/kohya-ss/musubi-tuner (docs/minimax_h3.md, minimax_h3_1f.md, minimax_h3_advanced.md); Discussion #1061; roadmap #1029; runbook https://github.com/lcdrzxlcdrzx/minimax-h3-lora-runbook
- diffusion-pipe: https://github.com/tdrussell/diffusion-pipe (docs/supported_models.md)
- SimpleTuner: https://github.com/bghira/SimpleTuner/blob/main/documentation/quickstart/MINIMAX_H3.md
- Circlestone adapter: https://huggingface.co/circlestone-labs/MiniMax-H3-Image-Training-Adapter
- OneTrainer: https://github.com/Nerogar/OneTrainer (no H3)

**Fizgig (author)**
- https://github.com/shootthesound/Fizgig: README, docs/MINIMAX_H3.md, docs/INSTALL.md, release notes v4.0.0 / v5.0.0 / v6.0.0 / v6.3.0
- Issues #71, #73, #86, #102, #118, #134, #142

**TenStrip**
- https://huggingface.co/TenStrip/10Eros-Max (README; beta6 files: int8 21.71 GB, pruned 40.22 GB, bf16 66.25 GB, FastH3 VSAgates UNSTABLE int8_HQ 26.75 GB)
- https://github.com/TenStrip/10S-Comfy-nodes (no H3 LoRA or beta6 notes; LTX face reinforcer, tiled sampler)

**Other tools**
- Tomiigo 16 GB repo: https://github.com/Tomiigo/minimax-h3-16gb (inference only, no LoRA notes; Windows "never run")
- malcolmrey RefMod guides (local copies in `2026-10-02-reddit-h3-ref2va-embedding-COMPLETE/related/`): 8–20 images, 1024 px short edge, 8,192 tokens; "RefMod + identity LoRA beats either alone"

**Community**
- r/SD 1wbpwcq "Are MiniMax spicy loras… a lie?"; 1vqly7i "H3 is a great model but the training is bad"; 1wi4y9c Fizgig 6.0 RefMods (shootthesound vs malcolmrey on LoRA vs RefMod); 1vemx58 Fizgig H3 launch; 1wxey7r AcademiaSD trainer (all via Apify trudax/reddit-scraper-lite)
- note.com かみもと: https://note.com/sepiablue/n/nf0763f854580 , https://note.com/sepiablue/n/nc1ce412d6ea2 , https://note.com/sepiablue/n/n67e809a90956
- ai-toolkit issues #1046, #1050, #991, #1017

**Local**
- AlienPc RAM: `2026-10-09-alienpc-speedups-torch-compile.md` L15
- Dataset folders: `/workspace/maxops/*-picks-2026-10-09/`, `/workspace/flow-export-2026-10-09/ex/`
