# RESEARCH: H3 Max prompting BPs + autoprompt ComfyUI node hunt — 2026-10-08

**When_CT:** 2026-10-08 ~2:06 PM CT (America/Chicago)  
**Owner:** Max Research executor · **AlienPc untouched** (no Shell lease, no :8189, no install, no messages)  
**Ask:** Derrick — (1) H3 Max prompting best practice; (2) is there a ComfyUI node that builds/enhances/auto-writes the H3 prompt (he recalls "wasn't there a node that would do it for us?"); (3) rank realistic options for 16GB :8189 GPU-share.  
**Locks:** KEEP = Derrick exact GO only · fiction adults 21+ · NO_DATA = not published / not in our files · no invent.

---

## Local priors (read first — do not invent)

| Path | What we already recorded |
|------|--------------------------|
| `research/2026-10-02-max-h3-prompting-best-practices.md` | REF2VA = **six-section** dialect; TenStrip: single still → REF not classic I2V; ~350–500 word body; no NEG branch |
| `research/2026-10-05-h3max-prompting-best-practices-addendum.md` | Skill audit; bans-as-positives; javawock HF LLM system prompt cited as persona source (text file, **not** a Comfy node); `[reference generation]` vs keyframe |
| `research/2026-10-08-10strip-h3max-optimal-vs-current.md` (sha prior `4aeb6e72…`) | Sampling/TE/refs — **no autoprompt node** named |
| `canon/max-i2v-prompt-improve-v1.md` · `research/2026-10-08-max-prompt-stack-audit.md` | Paste kit + craft locks (Static Shot, one act, no ban laundry) |
| `alienpc-ltx-stack-2026-09-25/MINIMAX_H3_VIDEO_PROMPT_WRITING_GUIDE_{ref,base}_en.md` | Local mirror of official guides |
| Skills: `ref2va-prompt` · `alienpc-hardcore-i2v-director` | Manual six-section writer (our current "node") |

**Gap this stamp fills:** prior work never catalogued ComfyUI **auto-prompt / rewriter / ✦ magic-prompt** nodes. That is what Derrick is remembering.

---

## STEP 1 — H3 Max prompting best practice (token-tight)

### Structure / length
| Mode | Shape | Length cue |
|------|-------|------------|
| **REF2VA** (our path) | Fixed **6 sections**: `subject_definitions` → `summary` → `retention_analysis` → `detailed_description` → `overall_soundscape` → `non_diegetic_music` | Generation `detailed_description` normally **~350–500 English words** [O4] |
| T2VA / I2VA / FL2VA / L2VA | 3 fields: `integrated_multimodal_description` · `overall_soundscape` · `non_diegetic_music` (+ fixed alignment line for I/FL/L) | Shorter; still shot markers + audio lanes [O3] |
| Hosted API text | Max **7000 characters** per `text` item [O6] | Local Comfy: multi-batch tokenize raises `"exceeds the supported prompt length"` — practical ceiling = Qwen3-VL tokenizer batch; **exact token max NO_DATA in official open docs** [O7] |

### What H3 responds to
- **Camera:** natural English motion type + optional amplitude/speed inside the shot (`The camera holds a static shot.` when hold asked) [O3/O4]
- **Motion / physics:** observable causal chains (prep → travel → contact → consequence); name tempo in plain English [O4 · local craft]
- **Wardrobe / ID:** retention markers `fully_preserved` / `partially_preserved` / `attribute_transfer` / `weak_reference` — not ban lists [O4]
- **Timing:** `[Shot N]` · cut times `At MM:SS.mmm` · length = argv frames (124–362 @24fps) [O1/O4]
- **Audio:** diegetic + dialogue in body; ambience/physical in `overall_soundscape`; audience score in `non_diegetic_music` (`N/A` OK) [O3]
- **TenStrip author:** "Sampling **and prompt** are the key"; prefer **REF** over classic i2v; no cache/spectrum on reference [P1]

### Negative prompts
**No NEG branch.** Templates use `BasicGuider` @ cfg 1 — naming an unwanted element *adds* it. Write bans as positives / retention markers [O3 tip 8].

### REF2VA × reference images
- Tags 1-based by connection order: `<Picture N>` / `<Video N>` / `<Audio N>` · ≤9 img · ≤3 vid · ≤3 aud · ≤12 mixed [O2]
- Assign each ref a **job** (identity/style/motion/camera/voice) [O1]
- `ref_image_size`: `match` (speed, our KEEP) vs `max` (stronger ID, slower) [O2]
- Cond still → use **REF six-section**, not I2VA 3-field (TenStrip High) [P1 · local Oct2]

### 32B text encoder notes
- H3-Encoder = Qwen3-VL-32B truncated to **layer 50** hidden states (no `lm_head` — **cannot generate/rewrite text**) [O5]
- Our file: `qwen3vl_32b_minimax_h3_nvfp4_awq` (~15.7 GB) · under `--lowvram` → **CPU** [local 10strip stamp]
- **Cannot reuse TE as a prompt rewriter** — different vocab/arch from LightX2V rewriter bases [C1]

### Failure modes (known)
| Mode | Cause | Mitigate |
|------|-------|----------|
| Ignored / weak prompt | Wrong dialect (LTX/I2VA paste into REF); starved body; turbo 4-step starves ref tokens | Six-section; ~350–500 words; base ~20 steps when ID-critical [O1] |
| ID / pose drift | Short turbo schedule on REF; cache/spectrum on; `match` when ID fragile | Steps↑ · cache off · try `max` one-axis [O1 · P1] |
| Ban laundry backfire | "no X / never Y" in guider text | Positives only [O3] |
| Soft motion | PRIMARY MOTION underspecified / multi-act in 5s | One act · tempo named · phased contact [local] |

---

## STEP 2 — the NODE question (heart of ask)

### Official "built-in" rewriter (not a Comfy stock node)
| Name | What | Local 16GB? |
|------|------|-------------|
| **MiniMax H3-Context-IR** | Hosted API `POST /v2/h3_context_ir` — MiniMax's own multimodal prompt enhancer; returns `content.prompt` only (no video). Supports t2va/i2va/**r2va**. **Not open-sourced.** [O6] | Needs **API key** · no local VRAM · uploads refs to MiniMax |
| Official Comfy H3 nodes | `MiniMaxH3ReferenceToVideo` / ImageToVideo — **no** prompt-enhancer widget [O1/O2] | N/A |
| TenStrip / 10Eros | Author ships **no** prompt node/workflow for H3 (Workflows repo pre-H3; README = sampling+prompt prose only) [P1 · prior 10strip] | N/A |

### Candidate ComfyUI nodes / extensions

| # | Exact name + repo | What it does | 16GB / GPU-share vs :8189 + 32B TE | Install | H3 / REF2VA compat | Notes |
|---|-------------------|--------------|-------------------------------------|---------|--------------------|-------|
| A | **ComfyUI-MiniMaxH3-Easy** · `nkxx188/ComfyUI-MiniMaxH3-Easy` (Manager: Nightly) · https://github.com/nkxx188/ComfyUI-MiniMaxH3-Easy | Main Easy workflow node + editor **`✦` prompt-optimizer** (manual or auto-on-run). Mode-aware H3 guides; OpenAI-compat / Responses / Gemini / **Ollama**; optional media read; segment split | Optimizer itself = **API/Ollama call** (no extra DiT VRAM). Ollama on **same** GPU competes with H3/TE unless CPU/off-box | Manager Nightly or `git clone` → restart | Yes — Reference-to-video mode + `@` refs | **Most likely what Derrick remembers** (sparkle/"magic" button) |
| B | **MiniMax-H3 Prompt Rewriter** pack · `pytraveler/MiniMax-H3-Prompt-Rewriter-ComfyUI` · https://github.com/pytraveler/MiniMax-H3-Prompt-Rewriter-ComfyUI | Local LightX2V rewriter LoRAs + guide Writers. **Rewriter Omni** does **Ref2VA**; Writers (GGUF) do all 5 tasks; Guide Prompt = zero-VRAM strings for any LLM | 27B LoRA ~**13–16 GB** alone — **conflicts** with H3 on one 16GB card unless unload (`keep_model_loaded=false`) then reload H3. Writer GGUF ~**5–8 GB**. Omni ~**9 GB** | Manager / `git clone` + deps | REF2VA: Omni rewriter **or** Prompt Writer (Ref2VA) / Universal Writer | Closest to "model's own rewriter" locally; LightX2V 27B LoRA still **T2VA-only** upstream [C2] |
| C | **ComfyUI-MiniMax-H3-Prompt-Enhancer** · `hyukudan/…` · https://github.com/hyukudan/ComfyUI-MiniMax-H3-Prompt-Enhancer | Guide-constrained enhancer + validator + **Guide Builder** (no LLM). API or isolated GGUF `llama-server` with VRAM reclaim | Guide Builder = **0 VRAM**. GGUF 7B Q4 reclaimable if `keep_server_loaded=false`. API/Ollama off-GPU = fine | Manager / clone | Explicit Ref2VA 6-block | Strong "enhancer" name match; heavier UI (Prompt Studio) |
| D | **ComfyUI-MiniMax-H3-Guide** · `ethanfel/…` · https://github.com/ethanfel/ComfyUI-MiniMax-H3-Guide | Plan-v2 compiler (typed refs/shots → valid H3 prose) + optional **Qwen3-VL Prompt Enhancer** using TE generation tail | Compiler = **0 VRAM**. Qwen enhancer loads gen layers — **VRAM conflict** with our TE/DiT if same GPU | clone | Native REF2VA routing | Inspired by Easy; more structured than magic-button |
| E | **JR_H3_OpenAICompatiblePromptOptimizer** · `Goldlionren/ComfyUI_JR_MiniMaxH3Node` · https://github.com/Goldlionren/ComfyUI_JR_MiniMaxH3Node | LLM fills JSON schema → Python builds H3 text (pinned to MiniMax guide commit) | Needs OpenAI-compat endpoint; no bundled LLM | Manager | H3-shaped out | Good if Ollama already elsewhere |
| F | **ComfyUI-H3-VisionPromptor** · `benjiyaya/…` · https://github.com/benjiyaya/ComfyUI-H3-VisionPromptor | Local VLM via Comfy native text-gen → H3 fields; no API | Uses on-disk VLM — VRAM share risk | clone | Claims H3 structure | Newer / less cited |
| G | **FeiHou Easy H3** · `FX-FeiHou/ComfyUI-FeiHou-Easy-H3` | Easy fork + prompt-optimizer (Zhipu/Ollama/etc.) | Same class as A | Manager/clone | Yes | Fork of Easy lineage |
| H | Generic: OneButtonPrompt / Searge / generic promptgen | SD1.5/SDXL-era template expanders | Local small | Manager | **Not H3 six-section** — wrong dialect | Unlikely the memory |
| I | **javawock7618** HF `llm_system_prompt_for_minimax-h3_ref2va-*.txt` · https://huggingface.co/javawock7618/comfy-MiniMax-H3-workflows | System prompt **file** for external LLM — **not a node** | N/A | Download txt | Ref2VA six-section | Cited in our Oct5 addendum as persona source |

### Flag — what Derrick most likely remembers
**Primary recall: ComfyUI-MiniMaxH3-Easy `✦` prompt optimizer** (row A) — unique "magic sparkle" UX community demos show; literally "a node/button that would do it for us."  
**Secondary (if he meant "the model's own"): MiniMax H3-Context-IR** (hosted) or **pytraveler LightX2V Prompt Rewriter** (local LoRA).  
**Not TenStrip-shipped** — author has no H3 prompt node [P1].

**Can we run A today?** Install = Derrick GO (custom node). Optimizer needs API key **or** Ollama. On 16GB sharing :8189: prefer **Ollama on CPU / other host**, or run optimize **before** H3 load. Do **not** keep a 7B+ GPU model resident beside H3+TE.

---

## STEP 3 — recommendation (no KEEP)

### Free / local / reversible to try (after Derrick GO to install — still not KEEP)
1. **Keep manual path** — `ref2va-prompt` + `canon/max-i2v-prompt-improve-v1.md` (already works; 0 VRAM; dialect SoT).  
2. **hyukudan Guide Builder** or **pytraveler Guide Prompt** — emit system/user strings → paste into any off-box LLM (Gemini/Grok/API) → paste result back. **0 VRAM on AlienPc.**  
3. **pytraveler Prompt Writer (Ref2VA)** on small GGUF (~5 GB) with `keep_model_loaded=false` — unload before H3 sample. Reversible custom-node add.  
4. **Easy ✦** with **external** OpenAI-compat / CPU Ollama — best UX match to memory; no resident GPU LLM.

### Needs own model/VRAM or API key (higher cost / conflict)
| Option | Cost |
|--------|------|
| H3-Context-IR | MiniMax API key · uploads media · best "official" quality · **NSFW policy risk NO_DATA** vs our fiction lane |
| LightX2V 27B / Omni rewriter on :8189 GPU | **~9–16 GB** — fights DiT + 32B TE; only sane with second GPU or strict unload |
| ethanfel Qwen TE-tail enhancer | Contends with our TE load |
| Easy ✦ / JR / hyukudan via paid cloud LLM | API $ · key in `prompt_optimizer.json` plaintext |

### VRAM tradeoff (16GB reality)
We already park **32B TE on CPU** under `--lowvram` and run TURBO w4a8 DiT on GPU. Any **resident** prompt LLM on the same GPU is a direct conflict. Prefer: off-box LLM · CPU Ollama · or load-rewrite-unload-then-H3. **Do not install anything this turn.**

---

## NO_DATA (ask Derrick)
1. Is Easy / pytraveler / hyukudan / ethanfel **already installed** on AlienPc `:8189`? (not in COS inventory today)  
2. Does he remember a **✦ sparkle button** (Easy) vs a separate **Prompt Rewriter** node vs **hosted Context-IR**?  
3. Any MiniMax / OpenAI / Gemini **API key** he wants used for Context-IR or Easy ✦?  
4. Exact **local TE token ceiling** (beyond API 7000 chars) — Comfy raises on multi-batch only; numeric max unpublished.  
5. NSFW policy of Context-IR / Easy cloud providers on adult fiction — not tested.  
6. Whether Tr1dae pack's latent-contrast node exists (prior NO_DATA; unrelated but still open).

---

## Sources (accessed 2026-10-08 CT)

**Official / primary (≥4)**  
- O1 https://docs.comfy.org/tutorials/video/minimax/minimax-h3  
- O2 https://docs.comfy.org/built-in-nodes/MiniMaxH3ReferenceToVideo  
- O3 https://docs.comfy.org/tutorials/video/minimax/minimax-h3-prompt-guide  
- O4 https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md  
- O5 https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/main/README.md (H3-Encoder = Qwen3-VL-32B @ layer 50)  
- O6 https://platform.minimax.io/docs/api-reference/video-generation-v2-h3-context-ir (7000-char text · Context-IR)  
- O7 https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/text_encoders/minimax.py (prompt-length ValueError)

**Author**  
- P1 https://huggingface.co/TenStrip/10Eros-Max/raw/main/README.md ("Sampling and prompt are the key")

**Community node primary**  
- C1 https://github.com/pytraveler/MiniMax-H3-Prompt-Rewriter-ComfyUI  
- C2 https://huggingface.co/lightx2v/MiniMax-H3-Prompt-Rewriter-LoRA (T2VA; FL2VA/Ref2VA checklist open)  
- C3 https://github.com/nkxx188/ComfyUI-MiniMaxH3-Easy (`✦` optimizer)  
- C4 https://github.com/hyukudan/ComfyUI-MiniMax-H3-Prompt-Enhancer  
- C5 https://github.com/ethanfel/ComfyUI-MiniMax-H3-Guide  
- C6 https://github.com/Goldlionren/ComfyUI_JR_MiniMaxH3Node  
- C7 https://github.com/benjiyaya/ComfyUI-H3-VisionPromptor  
- C8 https://huggingface.co/javawock7618/comfy-MiniMax-H3-workflows (LLM system prompt file)

**Local priors:** paths in §Local priors above · `research/2026-10-08-10strip-h3max-optimal-vs-current.md`

---

*Research only · no KEEP · nothing installed · AlienPc untouched · no messages sent*
