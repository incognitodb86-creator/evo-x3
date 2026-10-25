# Max community gap-check (2026-10-19 ~8:55 AM CT)

Research-only. Nothing downloaded, installed, or changed.
Read first: `2026-10-19-max-video-community-review.md`, `plans/max-DECISIONS.md`, `max-loras/MANIFEST.md`.
~12 web searches. Sources opened or indexed as linked below. Never invent sources.

Scope: gaps vs current plan (short prompts + MysticXXX/AIO/MisDog test ALI-80 + H3 Continuation / LongVideos + simple one-image H3 path). Do **not** re-propose multi-ref, head swap, Flux/Klein stills, judges/gates (owner locked simple path; Oct 18 Part 2 "not with the judge and other stuff").

---

## Verdict

**A few real gaps remain; the big ones from this morning's review (short prompts, NSFW LoRAs, drop judges) are already in the plan.** Nothing found that says "abandon H3 / 10Eros / Continuation." Highest-impact missing items: (1) LoRA card sampler mismatch on AIO clips, (2) Anti-Burn on chained chunk 2+, (3) native FL2VA first+last for transitions, (4) Forge using stock ComfyUI `/prompt` poll instead of custom queue harness.

---

## Gaps (only what we are missing)

| # | Gap | Why it matters | Source | Needs download? |
|---|---|---|---|---|
| 1 | **HMNSFW AIO card settings ≠ ALI-80 clip 4** — author: Euler/Simple, **12 steps**, **shift 6**, Turbo LoRA strength 0.5; strength 0.5–0.9 (author often 0.7–0.9). Our plan keeps global ST8 / shift 10. | Clip 4 tests AIO under non-card settings → false negative on whether AIO helps. | https://civarchive.com/models/2834417?modelVersionId=3268303 | **Setting only** (do not stack LightX2V on 10Eros — turbo already baked; prior review + 10Eros cards). |
| 2 | **H3-Anti-Burn-LoRA on continuation chunks** — load with `LoraLoaderModelOnly` on clips **2+ only**, start **0.5**; not on clip 1. Measured face-burn cut on chained runs. | ALI-80 clip 6 and longer scenes use 22-frame chaining; community burn is the known failure mode of latent tails. Listed optional this morning; still not in the test matrix. | https://huggingface.co/Imagineer13/H3-Anti-Burn-LoRA | **Yes — owner approval** (~295 MB `h3_antiburn_universal_v1.safetensors`). |
| 3 | **Official ComfyUI H3 I2V template + native `first_frame`/`last_frame`** — Template Library > Video > MiniMax H3 I2V; FL2VA keyframes for transitions. Aspect gotcha: `first_frame` stretch-resized, `last_frame` center-cropped; set AR to the image. | Scene transitions without only relying on Continuation/LongVideos custom nodes; simpler graph for Forge to drive. We already approved Continuation + LongVideos — this is the **official** alternative path, not a replacement mandate. | https://docs.comfy.org/tutorials/video/minimax/minimax-h3-native | **Workflow/setting** (weights already assumed present). |
| 4 | **Optional RIFE delivery pass after native 24 fps** — generate native; then RIFE 2×/48 or lattice→60 via Frame-Interpolation (`rife49.pth`). IAMCCS Delivery Router pattern; GIMM-VFI exists but heavier/slower. KEEP "no RIFE" on **generation** matches community. | Smooth review cut for Derrick eye-pick; not for identity or sex motion during sample. | https://comfy.icu/node/IAMCCS_MiniMaxH3DeliveryRouterV2 · https://github.com/Fannovel16/ComfyUI-Frame-Interpolation · https://github.com/kijai/ComfyUI-GIMM-VFI | **Yes if adopted** (nodes + RIFE weights). Skip for ALI-80 unless owner wants polish. |
| 5 | **HMPenis (low strength) stacked under AIO** — AIO author: AIO alone OK; "maybe a low strength penis/pussy LoRA"; Cuddle Cup stack uses HMPenis @ 0.6. | Sex clips (orc storyboard) — anatomy/contact is our known failure mode; community stacks anatomy under motion. | https://civarchive.com/models/2834417?modelVersionId=3268303 (author reply) · https://civarchive.com/models/2849923?modelVersionId=3247473 | **Yes — owner approval** (~74 MB v2). Optional after AIO arm, not blocking ALI-80. |
| 6 | **Blowjob H3 v3 LoRA** — trigger `bl0w_j0b`, strength 1.0; **15,632** downloads. | Only if a BJ beat is planned; AIO covers BJ weakly per comments. Not needed for missionary/doggy ALI-80. | https://civarchive.com/models/2845331?modelVersionId=3285598 | **Yes if BJ scenes** (~296 MB). Else skip. |
| 7 | **Forge unattended = stock ComfyUI API** — `POST /prompt` → poll `GET /history/{prompt_id}` (and/or `/ws`); gate on `GET /queue`. Matches Derrick "use community shit for forge" / Ralph loop. Optional CLI wrapper: shinshin86/comfy-agent (H3 presets + prompt skill). | Custom 24 KB queue / preflight harness is the opposite of the Oct 17 community-replace decision. | https://blog.kingsclaw.org/comfyui-automation-websocket-events-history-polling-no-webhook/ · https://github.com/shinshin86/comfy-agent · https://github.com/shinshin86/comfy-agent/blob/main/docs/minimax-h3-prompting.md | **No download** — script/pattern change. |
| 8 | **Megapixel guard** — official deploy guide: prefer **0.98 MP** or exact **1344×768**; avoid the **1.0 MP** step (resolves to 1376×768, over H3-Base area). Our 768×1344 ≈ 1.03 MP sits at the edge. | VRAM headroom + out-of-spec canvas risk on 16 GB AlienPc. | https://platform.minimax.io/docs/guides/local-deploy-h3 · https://docs.comfy.org/tutorials/video/minimax/minimax-h3 | **Setting only**. |

---

## What community suggests is wrong in our plan

1. **ALI-80 clip 4 at ST8 / shift 10 with HMNSFW AIO** — card wants 12 steps / shift 6 (gap #1). Clip 5 (MisDog, shift 6, ST8) is already closer to that LoRA's card (Euler/simple 8, shift 6).
2. **Chaining without Anti-Burn on chunk 2+** — community default for multi-chunk (gap #2); our clip 6 omits it.
3. **Still-long prompts / judges / multi-ref** — already covered in this morning's review; plan already moves them out. Do not re-open.
4. **LightX2V / separate turbo LoRA on 10Eros** — community uses LightX2V on **stock** H3; 10Eros author and prior review say **do not** add speed LoRAs on TURBO merges. **Not a gap for us.** Sources: https://github.com/modeltc/minimax-h3-turbo · prior review citing civitai/10Eros.

---

## Explicitly not gaps (found, then discarded)

| Item | Why discarded |
|---|---|
| Multi-ref / RefMods / face-swap graphs | Community likes them; owner locked **one start image**, no head swap / multi-ref (best clips Oct 9–10; Oct 18 Part 2 scope). |
| Lotus / Cuddle Cup position LoRAs | Niche; Lotus has letterbox dataset bug; not in ALI-80 acts. |
| GIMM as default interpolator | Exists; community still defaults to RIFE for speed/VRAM. |
| Restarting from official graph as mandatory | Useful as a **reference** (gap #3); not required to throw away Continuation/LongVideos already approved. |
| CapCut / DaVinci as must-haves | Eye-pick + hard cuts: FFmpeg concat or VHS VideoCombine is enough for review stitches. |

---

## Bottom line for parent

Important missing pieces: **AIO sampler alignment (settings)**, **Anti-Burn for chains (download card)**, **native FL2VA first/last (workflow)**, **Forge = `/prompt`+`/history` (no new models)**. Optional later: HMPenis, BJ LoRA, RIFE delivery. **No need to re-plan the core loop** (one image → short I2VA → H3 NSFW LoRAs → pick by eye → short chain).

