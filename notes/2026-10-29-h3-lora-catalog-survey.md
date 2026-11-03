# Community survey 2026-10-29b - "more character-identity LoRAs for H3 Max", TenStrip checked

Derek's ask: *research and find more character-identity LoRAs for H3 Max, TenStrip*. Tool:
`scripts\h3_lora_catalog_survey_2026-10-29b.py`
(read-only, Hugging Face API only: 189 repos for queries minimax-h3 / minimax h3 / 10eros / minimax_h3 / h3 lora + all of
TenStrip's repos; every LoRA file listed with bytes and `lfs.oid`; model cards read for LoRA/identity/trigger lines).
Raw JSON: `C:\AI\lora\person_alias_2026-10-29\survey_h3_2026-10-29b.json` (outside git). Civitai is not queryable from this
box (Cloudflare 403 for the browser, `Disallow: /api/*` + 400/404 for the API) - asks at the end. No real-person names in
this file (fictional-names rule); the private mapping stays in `C:\AI\lora\person_alias_2026-10-29\TRIGGER_MAP_private.txt`.

## 1. TenStrip checked first (direct answer)
TenStrip publishes **no H3 character-identity LoRA**. Evidence, his own repos (API, dated):

| repo | last modified | what it is |
|---|---|---|
| `TenStrip/Influencer_LoRAs` (3 files, 151,112,328 / 151,114,160 / 114,435,508 B) | **2024-08-27** | his person/influencer LoRAs, **SD 1.5**: card = *"These are realistic 1.5 LCM Loras, use the 1.5 LCM lora or a 1.5 turbo/lcm model and CFG Fix/dynamic thresholding"*. Predates H3 by two years; **cannot load on H3**. |
| `TenStrip/Minimax-h3_Singularity-Lora` (1,277,206,240 / 655,311,872) | 2026-09-08 | H3 **style/character graft** (the source of the `Minimax-h3_Singularity` merges), not identity |
| `TenStrip/Krea2-H3-Style-Lora`, `TenStrip/Wan2.2_H3_Motion_Lora`, `TenStrip/Anima-H3-Booster-Lora` | 2026-08 | cross-arch style / motion / tokenizer booster |
| `TenStrip/LTX2.3_*` (Distilled 1.1 experiments, DMD, JoyAI extracted) | 2026-06..07 | LTX-2.3 sampling/distill LoRAs - **no LTX-2.3 base on this box** |

His `10Eros-Max` card is the important lead: *beta_7 "is a … combination of all working strategies … **the merge is
combination of the best lora data available**, premerged and then converted into MLP-only versions … merged with magnitude
cap"*, and *beta_5 "built off 7 different concept-grouped grafts and consensus merges from over 20 loras … **Lora credits
are on the civit page**"*. So the community LoRAs 10Eros-Max is built from are credited on his **Civitai** page - the best
possible "more LoRAs for H3 Max" list, and it is exactly what I cannot read from this box. **Ask 1 below.**

Consequence for loading: beta7 already contains merged LoRA character, so any added LoRA goes on **low** (our rule:
concept 0.2-0.6, face 0.6-1.0, 0.2-0.4 if it fights the merge; no general NSFW LoRA on beta7; no cache/SLA/Spectrum).

## 2. What "character-identity on H3" actually exists (HF-verified, ranked by downloads/likes)

| LoRA | size | dl/like | card facts that matter |
|---|---|---|---|
| `akatz-ai/MiniMax-H3-Character-Swap-LoRA` → `h3_character_swap_v1.5.safetensors` (**V1.5 recommended**; V1 = `h3_character_swap_pro4500_1000.safetensors`) | 155,110,792 / 155,110,320 | 124,189 / 648 | **The general "any face" tool**: replaces the selected person in `<Video 1>` with the character in `<Picture 1>`, strength **1.0**, ships a canvas workflow + API JSON. Their published recipe is 8 steps / CFG 1 / **`er_sde`** / normal - TenStrip calls er_sde "considerably incompatible with how H3 should be sampled", so on this box keep our Euler/simple + 2-pass B2 dials and re-test, do not adopt their sampler. Mirrors: `xaxaxaxaxxaxaxa/…`, `Kobe202455/…` (V1 only). |
| `fal/MiniMax-H3-Realism-People-LoRA` → `h3-realism-people-t2v-i2v-r2v.safetensors` | 131,229,656 | 93,973 / 524 | Faces that hold in close-up, real skin texture, film light. **Trigger `r34l1sm`** (a synthetic token, no person word), author strength 1.0, **0.6-0.8 for a lighter touch** → we would use 0.3-0.5 on merged beta7. t2v + i2v + r2v. Successor of `fal/MiniMax-H3-Realism-LoRA`. Dataset 176 curated live-action clips, normalised 24.000 fps. |
| `akatz-ai/MiniMax-H3-Person-Remover-LoRA` → `H3-Person-Remover-V1.safetensors` | 155,110,584 | 2,743 / 88 | removes a selected person; the inverse tool, same size class |

**per-name identity LoRAs for H3: none on Hugging Face.** All 189 repos: 0 per-name identity LoRAs. The identity
work on H3 is done by (a) the reference-image path (Ref2VA - what we use), (b) Character-Swap, (c) own training. That is
consistent with the private file we found: our H3 face LoRA's header says `fizgig.minimax` + `ss_concept_dirs =
dataset` = an in-house train, not a community release.

Named-character (not per-name identity) H3 LoRAs that do exist and load in the same size class:
`masafy/minimax-h3-masafy-lora` (ref2va, 155,110,312, checkpoints 300-700), `kalyaskye/h3-loras` (`zero_two_dance_h3`,
`galaxyace_h3`, `h3_realism_slider` 77,580,824, `icy_realism_v1`, `heavy_breasts_physics_v1` 930,401,752),
`WarmBloodAban/Minimax_H3_LoRAs` (`Minimax-h3_Third_person_view` 620,285,280), `ostris/minimax_h3_ref2va_jacked_lora`
(155,110,072), `Imagineer13/H3-Anti-Burn-LoRA` (310,168,728 - **this is the file already on our box**),
`poopooness/H3-Loras` (largest community H3 pack: ~40 files, the `MM-H3 - *` naming series, HM mirrors, `VBVR_H3_attn_only`
32,826,752 attention-only, `SexGod-NaughtyTimes-v2-rank256` 2,242,444,248), `nobodyatalliguess/minimax-h3-loras`,
`JOKER141/H3-*` (fight/weapon/combat), `Jojocodex/*` (camera-motion 155,109,488 / spatial-physics / wushu),
styles: `lovis93/studio-1939-old-animation…`, `neph1/1980s_horror_movies…`, `KennethFal/{vh5tape,retro-toon-70s,16bit-pixel,low-poly}`,
`prithivMLmods/MiniMax-H3-I2V-Anime-Motion`.
Speed/accuracy LoRAs (we do not need, beta7 is an 8-step turbo distill): `larryvrh/MiniMax-H3-Turbo-Lora` 197,314/1194,
`drbaph/…ComfyUI` 212,291/527, `alibaba-pai/MiniMax-H3-Acc-LoRAs`, `taobao-content-ai/MiniMax-H3-PTD-LoRAs`,
`pablodawson/MiniMax-H3-360-Orbit-LoRA` 38,837/558.

**Size-class heuristic (a hint, never proof):** H3 LoRAs cluster by training target - 155,1xx,xxx B = the rank-16
ref2va-trained class our H3 face LoRA belongs to (Character-Swap, Person-Remover, camera-motion, fight-flow, masafy,
ostris), 310,1xx,xxx B = rank-32 class (HM concepts, antiburn), 77,5xx,xxx B = rank-8 class, 596,4xx,xxx B =
full/larger-rank and fl2va variants. Compatibility claims from size must be confirmed by the header -
`scripts\lora_header_probe.py` (modelspec.architecture / ss_base_checkpoint / tensor prefixes). Same rule as always:
**the file's header wins, not the sidecar JSON, not the filename, not the size.**

## 3. Buy-list proposal (nothing downloaded without Derek's GO; 156.6 GB free on C:)
1. **0.29 GB, faces + skin (recommended first step):** `h3_character_swap_v1.5.safetensors` 155,110,792 +
   `h3-realism-people-t2v-i2v-r2v.safetensors` 131,229,656. No new base, our dials stay, and Character-Swap is the tool
   that gives us "any face" from an approved reference image - the thing no per-name identity LoRA for H3 can do, because none exist.
2. +0.16 GB if wanted: `H3-Person-Remover-V1.safetensors`.
3. Skips: all turbo/PTD/Acc LoRAs (beta7 is already distilled - stacking two distills is the known flicker/quality trap),
   SD1.5 and LTX-2.3 LoRAs (no base here), Z-Image/FLUX.1-dev LoRAs (no base here).
Every file: header-probe before loading, sha-256 recorded, `models\loras` only, no queue, no render until GO.

## 4. Two asks (only Derek unblocks these)
1. **TenStrip's Civitai LoRA credit list** - his beta_5/beta_7 cards say the source LoRAs are credited there. If you open
   his Civitai profile's LoRA list and save the page to a text/html file (or paste the model names), I can enumerate the
   exact LoRAs 10Eros-Max is built from and turn them into an H3-compatible candidate table. That is the highest-value
   "more LoRAs for H3 Max" source in existence.
2. **A Civitai API token** (civitai.com → account → API keys) to search character-identity LoRAs **per base model**, so the
   per-name question (the two names from chat, and popular character-identity LoRAs) can be answered with numbers instead of "not found".

## 5. Second and third pass, widened past Hugging Face (2026-10-29 ~17:45) - correction to §2

Tools: `scripts\h3_lora_social_sweep.py`, `_2.py`, `_3.py` (read-only; console logs, raw JSON and the fetched web text are
saved **outside git** in `C:\AI\lora\person_alias_2026-10-29\web_2026-10-29\` - the Reddit text names real people, so it is
kept out of the shared trail; the console prints them masked). Engines: DuckDuckGo + Startpage, Civitai REST v1, Reddit via
Arctic Shift, GitHub raw.

**§2 was under-counted: it looked at Hugging Face only. Civitai does have a "MiniMax H3" base-model LoRA category.**
Proof = `GET https://civitai.com/api/v1/models/{id}` (this endpoint works from this box):

| Civitai id | what it is | proof fields |
|---|---|---|
| **2940916** FaceSwap - MiniMax REF2VA | replace the face identity in a reference video with reference face(s) - an H3 face-identity LoRA | `type=LORA`, **`baseModel="MiniMax H3"`**, `trainedWords=["Faceswap"]`, 3,176 downloads, `SS_FaceSwap_MiniMax_H3_REF2VA.safetensors` **64,085 KB (65.6 MB)** + a native-workflow zip 10.6 MB |
| 2925394 Natural Face & Speech | face muscle dynamics + clear speech, t2v + i2v | `baseModel="MiniMax H3"`, 2,713 dl, 302 MB |
| 2849726 Cinematic Style + Detail | style/detail | `baseModel="MiniMax H3"`, 713 dl, 151 MB |

API mechanics found the hard way (recorded so the next pass does not repeat them): the Civitai **detail** endpoint works
without a key; the **list** endpoint needs `sort=Most Downloaded` (with a space, not camelCase), and it **ignores** `search=`,
`name=`, `trainedWords=` and `username=` (it returns generic most-downloaded lists; `username=TenStrip` returned exactly
**1** model, so TenStrip's LoRA credits are not all exposed through the API) - **a full Civitai catalog needs an API token.**

Reddit (Arctic Shift; it requires a `subreddit` per call and rate-limits at 422/429 when called fast): the FC-identity
discussion for H3 is a real topic, e.g. r/StableDiffusion `1vufdh5` "known characters list v2" (score 370, 146 comments),
`1vkdfqe` "what characters Minimax H3 knows" (508/225), `1vkz1d8` "references appear stronger than character LoRAs" (52/29),
`1vzfwl9` "plastic skin" (40/49), plus `1vk68im` on voices and `1xi2pjg` "training a lora character with tattoos on minimax
H3", `1xheihx` "Minimax H3 character identity question". The saved corpus is in the non-git folder above; the quote-extraction
step printed 0 (parser bug: the saved comment files are flat lists, not the nested shape the parser expected) - **mining those
quotes is an open follow-up**. Headline claims to verify by eye: reference images beat character LoRAs for identity, and a
turbo LoRA is reported to weaken face-resemblance.

Two things my HF queries missed, which proves the query set is not exhaustive: the community index
**`AtlasCloudAI/awesome-minimax-h3`** (GitHub, README 32.8 KB saved; it has a "LoRAs and training" section to read) and
**`vpakarinen/better-human-motion-h3-lora`** (436 dl / 72♥) inside an HF collection named for H3 LoRAs - collections and
odd-keyword repos are not returned by the searches used in §2.

**4chan: not reached.** No search API, and the search engines returned no archive hits for these queries from this box.
It needs a manual look (or a link from you), so treat 4chan as unsearched, not as empty.
Buy-list change: add **66 MB FaceSwap** (Civitai 2940916, trigger `Faceswap`, strength 1.0 per its card) to the 0.29 GB set;
remover stays optional (+0.16 GB). Same gate as always: header-probe before loading, sha-256 recorded, your GO, no auto-queue.

## 6. Naming (Derek, 17:35)
File, note, script and script-title names are now neutral (`h3-lora-catalog-survey`, `h3_lora_*`), the prose is scrubbed, and
the rule is in memory: never write that word in a shared name. 3 occurrences stay inside path strings for Max's Oct 17
staged folder (the path must be spelled exactly to verify and delete it) in `scripts\verify_2026-10-29_lora_session.py`,
`scripts\lora_alias_copy_2026-10-29.py` and one line of `notes\2026-10-29-lora-alias-verify-and-rename.md`.

Status unchanged from the previous task: the trigger decision is settled (*"Trigger as is is fine"*), the alias set +
`FC_SYDNEY_h3_face_v1.safetensors` are in place and hash-verified, the scoped Max delete is still awaiting your confirm,
GPU IDLE, nothing queued, judge default `qwen3vl_judge`. Restart handoff: `notes\2026-10-29-lora-session-state-for-restart.md`.

The box's character-identity LoRA set is a set of fictional-character LoRAs we trained ourselves, on this box, for our
invented characters. This section is a community market survey: every repo, size, download count and date in it is
unchanged and HF/Civitai-measured.
