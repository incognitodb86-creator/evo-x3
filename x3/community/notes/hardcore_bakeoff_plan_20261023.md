# Hardcore community bakeoff: 27B vision prompter, All-In-One Uncensored graph, 7B rewriter vs current (ALI-173 child)

**Approval:** Derrick 2026-10-23 3:23 PM CT, verbatim: "I want all of these tested". He was replying to Max's list of the community hardcore setup (a)–(d) below.
**Roles:** Max directs. Forge does the downloads, installs, renders and diagnosis, inside the Ralph loop (`C:\Users\derek\5slock\ralph-community\TASKS.md`, block HB). Forge's copy of this plan: `C:\AI\community\notes\hardcore_bakeoff_plan_20261023.md`.
**Research:** `/workspace/cos/audits/2026-10-23-comfy-auto-pipeline-research/research.md`, section C (and A1 for infinite-creation).

## Arms (same scene for all)

The fixed scene for every arm:
- Start still: the HC3 pick, the same still as R6R/r3r (`ComfyUI\input\community\hc\HC3_*`), plus the HC3 512 px face crops (R4G2).
- Seed: 51130003.
- Settings: 1344x768, 24 fps, 243 frames (124 + 119, about 10.1 s), Ref2VA, 10Eros-Max beta6 int8, euler/simple, 10 steps, shift 10/3.
- No upscale, refine or RIFE in the scored clip, so every arm is compared on equal settings.

| Arm | What | Community source | New render jobs | Est. GPU min |
|---|---|---|---|---|
| HB0 control | Current setup: start still + face crop, Extender chain, our v2 prompt | ours (R4F/R4G/R4G2) | **0**: reuse R6R `ali147_pool_hc_r3r_s51130003` | 0 (counted in R6R, ~7) |
| HB1 | **27B vision prompter**: abliterated Qwen3.8-27B-Heretic GGUF + mmproj reads the HC3 still and face crop and writes the Ref2VA prompt (prompt writer only), then renders with the HB0 graph | https://civitai.com/models/2967166/minimax-h3-llm-vision-and-reasoning-nsfwsfw-ref2va · https://huggingface.co/0bserverx/Qwen3.8-27B-Heretic-Abliterated-Uncensored-GGUF | 1 (`ali173_hb1_s51130003`) | ~8 |
| HB2 | **All-In-One Uncensored graph**: the 2906001 workflow JSON (+ its custom nodes), stage 1 only at our settings | https://civitai.com/models/2906001/minimax-h3-all-in-one-uncensored-workflow-nsfw | 1 (`ali173_hb2_s51130003`) | ~10–15 |
| HB3 | **7B rewriter**: PW1's pytraveler MiniMax-H3-Prompt-Rewriter node + Qwen2.5-Omni-7B + lightx2v LoRA-Omni rewrites our prompt, then renders with the HB0 graph (this replaces the separate B9 render) | https://github.com/pytraveler/MiniMax-H3-Prompt-Rewriter-ComfyUI · https://huggingface.co/lightx2v/MiniMax-H3-Prompt-Rewriter-LoRA-Omni · `C:\AI\community\notes\small_prompt_llm_research_20261023.md` | 1 (`ali173_hb3_s51130003`) | ~8 |
| HB4 | **infinite-creation orchestrator** (installed in B1): the same scene end to end, its LLM pointed at local llama-swap, our int8 Ref2VA workflow registered. This is B4 run on the HB scene, so it replaces the separate B4 render | https://github.com/SwotAtmk/infinite-creation (research A1) | 1–2 (`ali173_hb4_s51130003`, max 1 retry) | ~8–16 |

**Total: 5 arms (1 control + 4 new), 4–5 new render jobs, about 34–47 GPU min.** This does not count prompt-LLM time, which happens outside render jobs.

## Budget (no cap raise)

- **Left today:** 615 − 450.8 = 164.2 GPU min and 45 − 35 = 10 jobs.
- **Queued first:** R6R (1 job, ~7 min) and B2 Continuum (1 job, ~8 min). After those: ~149 min and 8 jobs.
- **HB block:** 4–5 jobs and ~34–47 min. That fits and leaves ~100 min and 3–4 jobs for B3/B5/B6 and the retries.
- **Order:** after R6R and B2: HB1 → HB3 → HB2 → HB4.
- **Rule before every request:** read `ralph-community\logs\p7_budget.json`. If the request would go past 45 jobs or 615 min, do not request it. Mark the arm `[!] QUEUED FOR TOMORROW (budget)` and continue with CPU work. Nobody raises the caps; the arm runs on tomorrow's budget.

## Downloads Forge may do (approved by the 3:23 PM CT reply)

**Workflow JSONs and custom nodes**
- The 2967166 and 2906001 workflow JSONs, plus any custom nodes they need, go into `custom_nodes`.
- If a workflow needs a new **checkpoint** (for example 2906001's merged H3 model), Forge runs that arm with our 10Eros int8 model instead. It writes the checkpoint name, size and URL to `notes\guard_requests.md`, and Max asks Derrick.

**The 27B Heretic GGUF + mmproj** (largest quant that fits)
- Pick the quant from the HF page. While Forge's own model is loaded on llama-swap, check `nvidia-smi` free VRAM and choose the quant whose weights + mmproj + ~1.5 GB of context fit in that free space. On a 4090 (24 GB) next to the resident coder this is likely an IQ3/Q3 quant.
- If nothing fits fully, use partial offload (`--n-gpu-layers`).
- Run it as its own llama-server, or as a llama-swap entry that does **not** evict Forge's model. Use it only while no render is running (GPU lock), and unload it after use.
- Log sizes and paths to `notes\installs_downloads.md`. Check free disk first.

**Ollama:** if 2967166 needs it, install Ollama for Windows per its page. llama.cpp/llama-server serving the same GGUF is fine too.

## Content and scoring

- **Fiction lock v2.3.0** (`/workspace/cos/canon/fiction-cond-lock.md`): fictional adults aged 21+ only, from `5slock\approved_characters` (the HC3 pick). comm.py and its youth guard stay as they are.
- **Vision models are prompt writers only.** HB1's 27B model and HB3's Omni model look only at the start still and face crop, before the render. They never see rendered output.
- **Scoring**
  - Objective checks: ffprobe 1344x768/24 fps/243 frames, an audio stream, no black or frozen frames, result.json rc.
  - Wall time, retries and the manual steps or `[!]` items each arm needed.
  - The CPU ArcFace cosine of each woman vs the start still (the R4F metric).
  - **KEEP and "best" are Derrick's call** from a side-by-side contact sheet plus the clips. There is no vision judge on explicit output.

## Output

`C:\AI\community\notes\hardcore_bakeoff_20261023.md` has one table: arm, ran yes/no/[!], prompt used, wall time, GPU min, retries, face cosine per woman, objective checks, and install notes (sizes, paths). Next to it goes a side-by-side contact sheet `notes\hardcore_bakeoff_20261023_contact.png`. B8 RANK includes the HB arms. Max copies the clips to the box for Derrick.

## Amendment 2026-10-23 3:44 PM CT: HB2 merged model approved

Derrick 3:44 PM CT, verbatim: "Ok do it also have forge research lora for our fictional characters and do research on how to get better face consistency ect". His "Ok do it" answered Max's note that HB2 may need its own merged model.

- **Approved:** if the 2906001 All-In-One Uncensored graph requires its own merged H3 checkpoint, Forge may download that one checkpoint, at the version the workflow page names. Before downloading, Forge checks free disk and logs the name, size, URL and path in `notes\installs_downloads.md`. HB2 then runs with that checkpoint instead of our int8 model. Everything else about the scene stays the same.
- **Not approved:** any other new model or checkpoint still goes to `notes\guard_requests.md`.
- **Research follow-ons (text only, no GPU):** queued after HB5 as RL1 (character LoRAs, ALI-181), RF1 (face consistency, ALI-182) and RA1 (audio, ALI-183; Derrick 3:45 PM CT "Also have forge research voices and stuff better audio").
