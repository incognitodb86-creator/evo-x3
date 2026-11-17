# COMPLETE SCRAPE + REVIEW — Reddit H3 / Eros Ref2VA identity + SaveH3Embedding (tenowg2022)

**When_CT:** 2026-10-02 ~1:19 PM CT (America/Chicago)  
**Owner:** CoS executor · **Ask:** Derrick — proper scrape of screenshots (WholeBrain9977 Ref2VA Eros not following refs + tenowg2022 SaveH3Embedding + Qwen describe) · full OP + all comments · critical review vs AlienPc Max REF2VA KEEP  
**Scrape status:** **COMPLETE for post + all comments** via Arctic Shift (`photon-reddit.com`). Reddit.com / `.json` / old.reddit / pullpush / firecrawl = blocked or unauth (same wall as H3 upscale scrape).  
**Artifacts dir:** `/workspace/cos/research/2026-10-02-reddit-h3-ref2va-embedding-COMPLETE/`

---

## 1) URL found

| Field | Value |
|-------|--------|
| **Canonical** | https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/ |
| **ID** | `t3_1wbpwcq` |
| **Title** | Are Minimax spicy loras ... a lie? |
| **OP** | u/North_Enthusiasm_331 |
| **Created** | 2026-09-09 ~11:08 AM CT (utc `1788970123`) |
| **Score (archive)** | 160 |
| **num_comments (Reddit field)** | 190 |
| **Scraped unique comments** | **214** (Arctic; may include removes/dup retrieval — all IDs unique) |
| **Subreddit** | r/StableDiffusion |

**Screenshot match:** WholeBrain**9977** (three 9s — not 9777) · tenowg2022 · LocoMod “Go on…” / “OP delivered” · SaveH3Embedding · Qwen VL describe · `embedding:minimaxh3_test` — all live under this post’s Eros / Ref2VA reply chain (parent `p8rt79z` → `p8s440v` → …).

---

## 2) Scrape completeness checklist

| Item | Status | Notes |
|------|--------|-------|
| Post OP selftext | **YES** | Full 649 chars |
| All comments (flat) | **YES** | 214 unique JSON · `comments-all.json` |
| Threaded markdown dump | **YES** | `RAW-FULL-THREAD.md` (~95 KB) |
| Embedding subtree (WB → tenowg → code → replies) | **YES** | Fully reconstructed below |
| **SaveH3Embedding** full source | **YES** | Intact through `NODE_DISPLAY_NAME_MAPPINGS` · cleaned `SaveH3Embedding.py` |
| System prompt (Qwen describe) | **YES** | Full text in tenowg `p8t46yy` |
| Usage line (`<Subject 1> … embedding:…`) | **YES** | |
| WF screenshot (Comfy graph) | **YES** | `assets/ieush1wvpjoh1.png` (+ i.redd full) |
| Character-sheet WF screenshot | **YES** | `assets/n8qf6wtdwkoh1.png` |
| Character-sheet JSON drop | **PARTIAL** | tenowg offered drag-drop PNG WF; WB said drag-drop failed; tenowg said “give a shout and I will drop the json” — **JSON never appeared in thread** |
| Pastebin / gist links | **NONE in thread** | Scanned all bodies — no pastebin/gist. External links = HF TenStrip · malcolmrey RefMod guides · Civit · Qwen GitHubs · reddit previews |
| Firecrawl live scrape | **NO** | `firecrawl --status` = Not authenticated |
| Reddit.com browser/.json | **NO** | 403 / network policy (same as upscale thread) |
| User mobile screenshots | **YES** | Copied to `screenshots-user/` |

**Verdict:** Scrape of Reddit content is **complete**. Only missing external deliverable is the **never-posted** character-sheet Comfy JSON.

---

## 3) OP (full)

> I know that the answer is ultimately no, and also that they're all still early in development ...
>
> BUT I'm having a hard time getting the ones I find on civitai to produce anything resembling the examples. I follow generation guidelines where provided, and have even taken workflow settings from downloaded videos ... but they never seem to work very well. And if I try to add a lora to a sfw workflow that I'm happy with, the results look AWFUL.
>
> I've resorted to using wan generations as video references.
>
> Is i2v the best option? Does ref2va ever work?
>
> Any tips, recommendations, or resources you can recommend? Any else struggled with this?

**Thread theme (beyond embedding):** spicy LoRA frustration on H3 · paywalled Civit · “don’t need LoRAs / use Eros or hybrid + MysticXXX” · Wan-as-video-ref · Qwen local coding digressions. Embedding workaround is a **high-signal subtree**, not the OP topic.

---

## 4) Embedding / Ref2VA identity subtree (complete)

### 4.1 Chain root — Eros recommendation

**u/bstr3k** `p8rt79z` · score 47 · https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8rt79z/

> Have you tried Eros? This is Tenstrip's model that hes been tweaking with. He's a wizard  
> https://huggingface.co/TenStrip/10Eros-Max/tree/main?not-for-all-audiences=true  
> People have been saying beta 5 version without the turbo integrated has been good, but you can try turbo if you'd like. It would be a drop in replacement for the H3 model since it started its life being tweaked from H3

### 4.2 Problem report — WholeBrain9977 (matches Derrick screenshots)

**u/WholeBrain9977** `p8s440v` · score **16** · reply to Eros tip

> The Eros model worked really well for me—using **8 steps and no additional LoRA**. I do have one issue, though: for some reason, the model doesn't seem to **strictly follow every detail of the reference when using Ref2VA mode**. In specific areas—like the **breasts**—it tends to render a **generic shape**, likely derived from the training dataset. I have a workflow for a specific actress with a very distinctive breast shape; when I use a reference image of her in a "three-point" pose, the model simply forgets her actual breast shape and replaces it with a generic one bouncing. I haven't figured out a workaround for this yet. Additionally, I generated a **POV-angle** shot of her to use as a reference, but the model alters the pose to something similar—yet not identical—to the original image. I haven't found a solution for this either.

Follow-ups (same author):
- `p8u9ebp` — clarifies “perfect perky … teardrop nipple … part of her identity”
- `p8ub8tf` — anatomy (penetration) mostly fixed by Eros vs stock Comfy H3; still FL vs REF questions
- `p8ypwxy` — even with character sheet + breast close-up, **rapid motion** swaps nipple size / bounce bias (implants ≠ natural prior)

### 4.3 Workaround offer — tenowg2022

**u/tenowg2022** `p8sx599` · score 9

> I had the same issue with the **base ref2va** model, for some reason I had an off the wall idea, and asked **grok**, he recommended I use **embedding for my reference descriptions**, sure it was bs I tried it anyways, he gave me a custom node to generate the embedding. I use **qwen locally** to generate a very detailed description of about **200 words**, pass that to the embedding and use that, and the results were **impossible to ignore**. if interested I could dump the code for the node and a screen of the workflow.

**u/LocoMod** `p8t07e0` · “Go on…” (score 3)

### 4.4 Delivery — code + prompt + WF shot

**u/tenowg2022** `p8t46yy` · score **20** · full body captured (len 2736)

Contains:
1. Full `SaveH3Embedding` node (below)
2. Preview WF: https://preview.redd.it/ieush1wvpjoh1.png → local `assets/ieush1wvpjoh1.png`
3. System prompt for nude / character-sheet describe (below)
4. Prompt usage: `<Subject 1> from <Picture 1> embedding:minimaxh3_test`
5. Install note: drop into `custom_nodes/__init__.py`

**u/LocoMod** `p8tk4ih` · “OP delivered. Hot dang!” (score 7)

### 4.5 Character sheet / theory follow-ups

| Who | ID | Summary |
|-----|-----|---------|
| WholeBrain9977 | `p8udbww` | Asks creation method + what character sheets look like |
| tenowg2022 | `p8uhuxh` | Shares LTX-ingredients character-sheet WF PNG (`n8qf6wtdwkoh1.png`); warns head-chop; offers JSON if drag-drop fails |
| WholeBrain9977 | `p8vnjbg` | Drag-drop failed |
| StandWorth9165 | `p8wglou` / `p8wgrkr` / `p8wiskx` | Alt Krea2/Flux2 sheet WF (r/comfyui `1w6o357`); clothing transfer note |
| OrdinaryAward4498 | `p8vp6ti` | “That’s Effy the succubus!” |
| tenowg2022 | `p8vxj2x` | Different character, similar taste |
| LeKhang98 | `p8wbcry` | Why embeddings > raw text? Negatives? Long prompts? |
| tenowg2022 | `p8xfb0f` | SD1.5-style TI analogy: pre-encode 200w identity so scene text_encoder has less clutter; not an expert |
| cashcowman | `p9elbkl` | “Yes please.” → tenowg `p9elvj3` “look down…” |

### 4.6 WF screenshot notes (from image + comment)

Comfy graph (ieush1wvpjoh1) shows roughly:
- **OpenAI Compatible LLM** → `http://127.0.0.1:1234/v1` · model near `qwen2.5-vl-…` (local LM Studio / similar)
- Multiline **system** text = describe prompt
- Vision describe → text into **CLIP Text Encode** / H3 TE path
- **Save MiniMax H3 Embedding** named e.g. `minimaxh3_normal`
- `Get_CLIP_REF2`-style wiring into encode → save

**No separate LoadH3Embedding node posted** — consumption is via prompt token `embedding:minimaxh3_test` (Comfy textual-inversion style load from `models/embeddings/`).

---

## 5) SaveH3Embedding — complete code

Source: tenowg2022 `p8t46yy` · cleaned copy:  
`/workspace/cos/research/2026-10-02-reddit-h3-ref2va-embedding-COMPLETE/SaveH3Embedding.py`

```python
import os
import folder_paths
import torch
from safetensors.torch import save_file


class SaveH3Embedding:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "conditioning": ("CONDITIONING",),
                "name": ("STRING", {"default": "minimaxh3_my_orbit"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("path",)
    FUNCTION = "save"
    CATEGORY = "minimax_h3"
    OUTPUT_NODE = True

    def save(self, conditioning, name):
        cond = conditioning[0][0]  # [1, N, 5120]
        if cond.ndim == 3:
            cond = cond[0]
        # keep text-tagged rows if present
        extra = conditioning[0][1] if len(conditioning[0]) > 1 else {}
        tags = extra.get("minimax_token_tags")
        if tags is not None:
            tags = tags.reshape(-1)
            # 1 = text modality in H3
            mask = tags.cpu() == 1
            if mask.any():
                cond = cond[mask]
        vec = cond.detach().float().cpu().contiguous()
        folder = folder_paths.get_folder_paths("embeddings")[0]
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, f"{name}.safetensors")
        save_file({"qwen3vl_32b": vec}, path)
        return (path,)

NODE_CLASS_MAPPINGS = {"SaveH3Embedding": SaveH3Embedding}
NODE_DISPLAY_NAME_MAPPINGS = {"SaveH3Embedding": "Save MiniMax H3 Embedding"}
```

**Mechanics (critical):**
- Input = Comfy **CONDITIONING** from H3 / Qwen3-VL text encode (dim comment **5120**)
- Optionally filters rows where `minimax_token_tags == 1` (text modality)
- Saves tensor under key **`qwen3vl_32b`** into `models/embeddings/{name}.safetensors`
- This is **not** a trained textual-inversion; it is a **frozen dump of encoded description tokens** reused via `embedding:name`

---

## 6) System prompt (full) + usage

```
You are a master at extracting human details from images.
You will describe the figure in the image you receive to extreme details. If the user supplies any text, organicly use that text to override your descriptions in a additive fashion.

## Include
- face, eye, mouth
- figure shape, demensions, fitness, etc
- skin color and type
- breast size and shape
- areola size and shape
- nipple size and shape
- pelvic region description

Once you have fully analysed the image, generate a concise summaried version, keeping it to 200 words or less.

You will return only the concise summarized version, no padding text, no explaination, no additional words, only the concise summaried version as your response.
```

**Usage (tenowg):**  
`then use the text: <Subject 1> from <Picture 1> embedding:minimaxh3_test`

**Pipeline:** character sheet / nude ref → local Qwen-VL (~200w) → CLIP/H3 TE encode → SaveH3Embedding → later REF gens cite `embedding:…` alongside `<Picture N>`.

---

## 7) Related links in thread (not pastebins)

| Link | Relevance |
|------|-----------|
| https://huggingface.co/TenStrip/10Eros-Max | Eros Max drop-in |
| https://huggingface.co/datasets/malcolmrey/various/blob/main/h3-center/docs/MINIMAX_H3_REFMODS_INSTALLATION_AND_USAGE_GUIDE.md | **RefMods** = different product: pre-encoded conditioning adapters (~1.1–1.6 MB) for likeness — local copy in `related/` |
| https://huggingface.co/datasets/malcolmrey/various/blob/main/h3-center/docs/MINIMAX_H3_REFMOD_CREATION_GUIDE.md | How to extract RefMods |
| https://www.reddit.com/r/comfyui/comments/1w6o357/… | StandWorth alt character-sheet WF |
| Qwen38 GitHubs / orcarouter GGUF | Digression (local LLM), not REF recipe |

**Pastebins / gists:** **none** found in any of 214 comment bodies.

---

## 8) Critical review vs AlienPc Max REF2VA KEEP

### Our locked KEEP (AlienPc `:8189`)

| Knob | KEEP |
|------|------|
| Product | ORC_BJ · Cond `COND_HC3.jpg` sole `ref_image_1` |
| Graph | `MiniMaxH3ReferenceToVideo` REF2VA |
| UNET | 10Eros Max **TURBO-hybrid beta5** w4a8 (not stock Ref2VA) |
| Res / length / steps | **864×480 · 124f · 25** · `res_multistep` |
| Host | **NODDV** triad (+ lowvram) · no fp8 CLI |
| Attn | **ck-attn = DISPUTED**, not early KEEP (matrix) |
| Prompt | Six-section REF dialect · lean single Cond |
| Post | Upscale after gen (separate H3 upscale review) |

### What the thread claims

| Claim | Evidence quality | Fit to our box |
|-------|------------------|----------------|
| Eros @ **8 steps, no LoRA** “works well” NSFW | Anecdote (WB + others) | **Conflicts with our KEEP** — we hold **20–25** for REF AV Integrity; 8-step is draft/turbo lane |
| Stock / base Ref2VA **soft-rewrites** distinctive anatomy (breasts, POV) toward dataset prior | Multiple users (WB, tenowg on base) | **Aligned risk** — Max hybrid can also dilute per-frame ref accuracy (Stuubs); ORC_BJ hardcore contact/breast ID is exactly this failure class |
| **Qwen-VL 200w → H3 embedding** improves ref adherence | Single power user, strong self-report, no fair A/B | **Interesting PARK→DISPUTED probe** — not proven; TE already is Qwen3-VL 32B; dumping encode may help *or* fight six-section packing |
| Embedding ≈ SD1.5 TI / reduces encoder clutter | Hand-wavy theory by author | Plausible for long identity prose, **unproven** on Max hybrid + six-section |
| Character sheets help | Community habit | We already researched sheets; **S0 = keep Cond**, add sheet only after TECH failure |
| Hybrid B30-49 + MysticXXX + Turbo stack (top comment Chiduk99) | Popular spicy recipe | **KNOWN_FAIL / draft-only** vs our Integrity KEEP (Turbo off for finals) |

### KEEP / CHANGE / PARK

| Action | Item | Why |
|--------|------|-----|
| **KEEP** | 864×480 · 124f · **25 steps** · REF2VA · NODDV · Cond ORC_BJ · six-section | Thread’s 8-step Eros praise is draft culture, not our Integrity bar |
| **KEEP** | Post-gen upscale path (Lanczos / Remacri / SeedVR2 / RTX blend) | Identity fails in-thread are **gen-time priors**, not upscale fixes |
| **KEEP** | Lean single Cond until TECH proves a *specific* anatomy axis fail | Matches WB’s failure (distinctive breast) — only then escalate refs/text |
| **CHANGE (prompt-only, low risk)** | If breast/areola/nipple or contact geometry drifts: **literal size/shape locks** in `subject_definitions` + `fully_preserved` retention (already in local prompting BPs) | Thread proves prior-bias is real; prose locks are free vs new nodes |
| **PARK — DISPUTED A/B (home, Shell clear)** | tenowg **SaveH3Embedding** path: Qwen-VL describe Cond → encode → `embedding:orc_bj_id` cited with `<Picture 1>` | Same failure mode we care about; one-axis vs current six-section-only; watch VRAM (extra TE encode pass) + whether Max hybrid honors `embedding:` key `qwen3vl_32b` |
| **PARK** | Install `SaveH3Embedding` as tiny custom_node when home | Code is complete; no gist needed |
| **PARK (adjacent, not same)** | malcolmrey **RefMods** (conditioning adapters) | Heavier/different stack (`ComfyUI-MiniMaxH3Mod`); evaluate only if embedding A/B fails |
| **DO NOT CHANGE** | Drop to 8 steps / crown Turbo / EasyCache for KEEP | Thread habits ≠ our matrix |
| **DO NOT CHANGE** | Swap Cond for “beauty sheet” mid-probe | Sheets are for ID axes after failure; Cond is act lock |
| **DO NOT COPY blindly** | Assume embedding beats multi-angle stills | Official binding is still text+Picture labels; embedding is a *compressed text* shortcut |

### Risk notes for embedding probe (if run later)

1. **TE key / loader:** file must be loadable as Comfy embedding with tensor key `qwen3vl_32b` — verify against our `qwen3vl_32b_minimax_h3_nvfp4_awq` TE; mismatch = silent no-op or crash.  
2. **Double identity:** Cond image + 200w breast/pelvic prose + embedding may **over-constrain** or fight scene audio/act — fair A/B needs same seed.  
3. **NSFW describe model:** local Qwen-VL must actually emit breast/pelvic detail (censorship) or embedding is empty calories.  
4. **NODDV cost:** extra encode pass before save is fine offline; don’t put Save node on every TECH smoke.  
5. **WB residual:** even with sheet + close-up, **motion** still genericized breasts — embedding may help static ID more than bounce physics.

---

## 9) Thread-wide takeaways (non-embedding, for completeness)

- Spicy **Civit LoRAs** often disappoint vs examples; many recommend **Eros Max**, hybrids, or “H3 already knows acts — refs for pose/genitalia” (DjMesiah, high score).  
- **Paywall rage** (15k buzz) is loud but irrelevant to KEEP.  
- **Wan video as ref** is OP’s current crutch — we already deprioritize video refs for S0.  
- Top spicy stack comments push **Turbo + MysticXXX** — treat as draft culture opposite our Integrity freeze.

---

## 10) Artifact index

| Path | Contents |
|------|----------|
| `/workspace/cos/research/2026-10-02-reddit-h3-ref2va-embedding-COMPLETE.md` | This stamp |
| `…/2026-10-02-reddit-h3-ref2va-embedding-COMPLETE/RAW-FULL-THREAD.md` | Full OP + **all** comments threaded |
| `…/comments-all.json` | 214 comments raw |
| `…/post-full.json` | Post metadata + selftext |
| `…/SaveH3Embedding.py` | Clean node |
| `…/assets/ieush1wvpjoh1.png` | Embedding WF screenshot |
| `…/assets/n8qf6wtdwkoh1.png` | Character-sheet WF screenshot |
| `…/related/MINIMAX_H3_REFMOD*.md` | malcolmrey RefMod guides |
| `…/screenshots-user/01–05.png` | Derrick mobile captures |

---

## 11) Bottom line for Derrick

**URL:** https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/  

**Scrape:** **Complete** (OP + 214 comments + full SaveH3Embedding + system prompt + usage + both WF images). No pastebins. Character-sheet **JSON never posted**.  

**Vs Max KEEP:** Problem statement **matches** our Ref2VA identity risk (generic anatomy under motion). Proposed fix (Qwen→H3 embedding) is a **PARK / fair A/B when Shell is back** — do **not** change 25-step / NODDV / Cond ORC_BJ KEEP to chase the thread’s 8-step Eros habits. First free move remains **literal anatomy locks in six-section prose**; embedding node is the next experiment if that fails.
