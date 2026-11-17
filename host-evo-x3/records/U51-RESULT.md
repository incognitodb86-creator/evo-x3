# U51: Community Alignment Review of the Render H3 Pipeline (EVO-X3)

**Date:** 2026-11-16  
**Scope:** Report-only comparison of our EVO-X3 Render H3 (`10Eros-Max`) pipeline against official MiniMax H3 documentation, official ComfyUI H3 workflow templates/nodes, `pytraveler/MiniMax-H3-Prompt-Rewriter-ComfyUI`, and recent (Sept–Nov 2026) community practice. No files in `/home/evo/` were modified.

---

## 0. Community Baseline & Sources (Verified URLs)

1. **Official MiniMax H3 Prompt Structure & Architecture**
   - Repo & README: https://github.com/MiniMax-AI/MiniMax-H3 and https://huggingface.co/MiniMaxAI/MiniMax-H3
   - Prompt skill (`SKILL.md`, `base-en.txt`, `ref-en.txt`):
     - https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/SKILL.md
     - https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/references/base-en.txt
     - https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/references/ref-en.txt
   - **Key facts:** 24 fps, native 768px short edge (`1344x768` / `768x1344`, multiples of 32), 4–15 s duration. Base modes (`T2VA`/`I2VA`/`FL2VA`/`L2VA`) use optional alignment line + `integrated_multimodal_description`, `overall_soundscape`, `non_diegetic_music`. Full-reference (`Ref2VA`) uses 6 sections (`subject_definitions`, `summary`, `retention_analysis`, `detailed_description`, `overall_soundscape`, `non_diegetic_music`), labels `<Subject N>`, `<Picture N>`, `<Video N>`, `<Audio N>`, dialogue `<d>[Language] ...</d>` with speaker IDs `(S1)`, `(S2)`, and multi-shot cuts `[Shot 2] At MM:SS.mmm`. Safety guardrails moderate unlawful/minor/non-consensual content.

2. **Official ComfyUI Nodes & Templates**
   - Docs & Prompt Guide:
     - https://docs.comfy.org/tutorials/video/minimax/minimax-h3
     - https://docs.comfy.org/tutorials/video/minimax/minimax-h3-prompt-guide
   - Node implementation (`nodes_minimax_h3.py`): https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_minimax_h3.py
   - Workflow templates:
     - https://github.com/Comfy-Org/workflow_templates/blob/main/templates/video_minimax_h3_i2v.json
     - https://github.com/Comfy-Org/workflow_templates/blob/main/templates/video_minimax_h3_r2v.json
   - **Key facts:**
     - **Frame grid (`5 + 17k`):** `align_frame_count(n)` in `nodes_minimax_h3.py` lines 50–53 runs `while n % 17 != 5: n += 1` (always snaps **up** to `5 + 17k`, e.g., `120 -> 124`, `192 -> 192`, `243 -> 243`). `video_minimax_h3_r2v.json` node 131 computes `max(5, round(a * 24)) + (5 - (max(5, round(a * 24)) % 17)) % 17`.
     - **Resolution:** Native 768 short edge (`adapt_canvas`, `1344x768` or `768x1344`, multiples of 32).
     - **No negative prompt:** `BasicGuider` runs at CFG 1 with no negative branch (`minimax-h3-prompt-guide`; `video_minimax_h3_r2v.json` node 126).

3. **`pytraveler/MiniMax-H3-Prompt-Rewriter-ComfyUI` (HF + ComfyUI Node Pack)**
   - Repo & README: https://github.com/pytraveler/MiniMax-H3-Prompt-Rewriter-ComfyUI and https://github.com/pytraveler/MiniMax-H3-Prompt-Rewriter-ComfyUI/blob/main/README.md
   - Checker code (`checks.py`): https://github.com/pytraveler/MiniMax-H3-Prompt-Rewriter-ComfyUI/blob/main/minimax_h3_rewriter/checks.py
   - Weights: https://huggingface.co/lightx2v/MiniMax-H3-Prompt-Rewriter-LoRA, https://huggingface.co/pytraveler/MiniMax-H3-Prompt-Rewriter-LoRA-GGUF, https://huggingface.co/lightx2v/MiniMax-H3-Prompt-Rewriter-Qwen3.5-9B-Ref2VA
   - **Key facts on wiring & linting:**
     - **Wiring:** `Duration` snaps to `17n+5` before writing the prompt (`README.md` §"The duration widget" & lines 391–395). Reference captioners (`Reference Caption`, `Multi Reference Caption`) describe media into text first; writer/rewriter expands a short idea + captions in a **single turn** (no intermediate JSON beat-card schema) and feeds `prompt` straight into ComfyUI's `MiniMaxH3ImageToVideo` or `MiniMaxH3ReferenceToVideo`.
     - **Linter philosophy (`MiniMax-H3 Prompt Check` / `checks.py`):** *"Findings are said, never enforced — a prompt that trips a rule still ships, because the model is sometimes right to bend one and the person is the judge."* Only hard structural capacity errors (e.g., >9 images / >3 videos / >3 audio, or an LLM refusal) halt execution; `fix_once` is **off by default**, and when off, *"the answer you get is exactly what the model wrote, with nothing edited on the way out."*

4. **Recent Community Workflows & `10Eros-Max` Practice (Sept–Nov 2026)**
   - `10Eros-Max` model cards & merges:
     - https://huggingface.co/Darklock/10Eros-Max (2026-11-10)
     - https://huggingface.co/ibyteohdear/10Eros-Max-Transformer_8stepTURBO_beta7 (2026-11-16)
     - https://huggingface.co/TenStrip/10Eros_Max_v1_dev-only (2026-11-16)
   - Recent HF discussions & community workflows:
     - https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/125 (2026-11-08: Ref2VA field study on input roles, character identity, shot timing)
     - https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/124 (2026-11-05: multi-segment long shots on 12 GB VRAM)
     - https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/122 (2026-11-03: 715 sampler/scheduler benchmark)
     - https://huggingface.co/Alissonerdx/Minimax-H3-ComfyUI (2026-11-16)
     - https://huggingface.co/javawock7618/comfy-MiniMax-H3-workflows (2026-11-16)
     - https://github.com/sepiablue-ai/minimax_h3_workflows
     - https://github.com/tritant/ComfyUI_MiniMax_H3_Extender
   - **Key community practices:**
     - **10Eros-Max audio:** `TenStrip` (10Eros-Max creator, HF #77, recorded in our `h3-prompting/SKILL.md:63-67`) explicitly advises deleting `overall_soundscape:` / `non_diegetic_music:` headers on `10Eros-Max` and writing plain diegetic audio cues inside/at the end of the main prompt.
     - **10Eros-Max sampling:** `8stepTURBO` beta7 runs at 4–8 steps (`euler`/`simple` or `res_multistep`/`simple` or `er_sde`/`beta`), shift `12/3`, no negative prompt, optional 2-pass latent spatial upscale to reduce background flicker.
     - **Seeds & resolution:** Changing base resolution with a locked seed shifts the DiT latent grid; keep draft/final resolution locked or use latent upscale.
     - **Linters/gates:** Nobody in the community runs blocking regex prose linters or silent prompt rewriters in production; `pytraveler`'s `Prompt Check` is purely advisory (`warnings and notes`, `off` by default for rewrites).

---

## 1. Pipeline Step-by-Step Audit Table

Classification key:
- **COMMUNITY**: Matches official MiniMax H3 / ComfyUI / `pytraveler` / `10Eros-Max` practice (including legitimate 18+ safety guardrails).
- **HELPER**: Our domain/craft guidance that only advises or informs without blocking or overwriting.
- **OVERRIDE**: Blocks, rewrites, strips, or replaces community/writer behavior.

| # | Pipeline Step | Class | Our `file:line` | What Ours Does | Community Source & Comparison |
|---|---|---|---|---|---|
| 1 | Session & skill loading | **HELPER** / **OVERRIDE** | `render/x3/render-pi.sh:30-35`, `render/AGENTS.md:13-187`, `skills/h3-prompting/SKILL.md:1-222`, `skills/h3-parody-identity/SKILL.md:1-54` | Craft rules (R7 plain audio cues, R8, R16-R25, R37 `<d>`) & `h3-parody-identity` voice tips (**HELPER**). However, `AGENTS.md:15-18, 160` forbids direct prompt authoring and forces the `render_writer_pipeline.py` loop (**OVERRIDE**). | [pytraveler README](https://github.com/pytraveler/MiniMax-H3-Prompt-Rewriter-ComfyUI/blob/main/README.md) & [MiniMax SKILL.md](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/SKILL.md): guides/skills inform the prompt writer; user/writer owns the prompt. |
| 2 | 18+ Youth hint pre-check on `--ask` | **COMMUNITY** | `parody/render_writer_pipeline.py:1323-1326`, `parody/wp_lint.py:358-360` | Hard-stops (`NOT_READY`) if `YOUTH_RE` matches `--ask`. | [MiniMax-H3 README](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/README.md) ("Safety Guardrails"): unlawful/minor content blocked; intentional 18+ local lock. |
| 3 | Chain parent check & last-frame extraction | **OVERRIDE** / **COMMUNITY** | `parody/render_writer_pipeline.py:1205-1217, 1341-1361, 1430-1434` | Extracting last frame of previous `.mp4` (`ffmpeg -sseof -0.1`) is **COMMUNITY**. Blocking continuation if parent `pick.json` was `NOT_READY` or `ending_state.pose` is empty is **OVERRIDE**. | [ComfyUI_MiniMax_H3_Extender](https://github.com/tritant/ComfyUI_MiniMax_H3_Extender) & [MiniMax base-en.txt](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/references/base-en.txt): frame/latent continuation does not require a JSON `ending_state` schema lock. |
| 4 | Canvas & aspect resolution + shape check | **COMMUNITY** | `parody/render_writer_pipeline.py:1384-1394`, `parody/build_request.py:443-525` | Multiples of 32 (`768x1344`, `1344x768`, `1024x1024`, `auto`), warns (never blocks) on >5% aspect mismatch. | [nodes_minimax_h3.py:66-76](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_minimax_h3.py) (`adapt_canvas`) & [ComfyUI Prompt Guide](https://docs.comfy.org/tutorials/video/minimax/minimax-h3-prompt-guide): 768 short edge, multiples of 32. |
| 5 | Vision still captioning (`still_read.json`) | **COMMUNITY** / **OVERRIDE** | `parody/render_writer_pipeline.py:1122-1202, 1396, 1412-1420`, `parody/build_request.py:4657-4678` | Vision read of `<Picture 1>` is **COMMUNITY**. `clean_still_read` rewriting `"unseen"`->`"the floor"` & shiny skin words, and `strip_male_solo_still_read` erasing fields for downstream regexes are **OVERRIDE**. | [pytraveler README](https://github.com/pytraveler/MiniMax-H3-Prompt-Rewriter-ComfyUI/blob/main/README.md) (`Reference Caption`): captioners describe reference media into plain context; nothing mutates the caption. |
| 6 | Mode router & waist-high surface gate | **HELPER** / **OVERRIDE** | `parody/render_writer_pipeline.py:1398-1426`, `parody/wp_router.py:60-125` | Detecting overlays/themes as prompt context is **HELPER**. Silently rerouting `doggy`->`standing_mf` (`1401-1403`) and hard-blocking `cowgirl` on waist-high surfaces as `NOT_READY` (`1404-1408`) are **OVERRIDE**. | [pytraveler checks.py](https://github.com/pytraveler/MiniMax-H3-Prompt-Rewriter-ComfyUI/blob/main/minimax_h3_rewriter/checks.py): no pose/surface compatibility blocker exists in community tools. |
| 7 | Frame count & speech budget setup | **COMMUNITY** / **OVERRIDE** | `parody/render_writer_pipeline.py:1435-1448`, `parody/build_request.py:217-242` | Defaulting to `snap_h3_frames` (`5+17k`, <=243f for 16 GB) is **COMMUNITY**. Passing explicit `--frames` (e.g. `120`) without grid snapping (`1435-1437`, `231-242`) causes **Bug (c)**; hard per-speaker line/word caps (`1443-1444`) are **OVERRIDE**. | [nodes_minimax_h3.py:50-63](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_minimax_h3.py) (`align_frame_count`), [pytraveler README](https://github.com/pytraveler/MiniMax-H3-Prompt-Rewriter-ComfyUI/blob/main/README.md) (`17n+5`), [HF #124](https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/124). |
| 8 | System prompt & slots brief assembly | **HELPER** / **OVERRIDE** | `parody/render_writer_pipeline.py:215-249, 549-648, 1453-1495`, `parody/writer_sys.py:44-63` | Providing still facts, mode notes, tone/focus variety, and scene continuity context is **HELPER**. Mandating builder-only syntax (`PRIMARY MOTION -`, `aside`, `strokes a second`, `"never write X"`) is **OVERRIDE**. | [MiniMax SKILL.md](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/SKILL.md): guides give natural-language structure, not builder-parser keywords. |
| 9 | JSON Beat Card (`json_schema`) | **OVERRIDE** | `parody/render_writer_pipeline.py:252-316, 1505-1548` | Forces a separate constrained-JSON planning call (`BEAT_SCHEMA_*`) before prose, and enforces schema rules (e.g. `line_topics` `minItems: 3`). | [pytraveler README](https://github.com/pytraveler/MiniMax-H3-Prompt-Rewriter-ComfyUI/blob/main/README.md): community writers go straight from ask + captions to H3 prose in 1 pass. |
| 10 | Prose generation (x3) + `clean_prose` / `normalize_prose` / `glue_fix` / `assemble_output` | **OVERRIDE** | `parody/render_writer_pipeline.py:657-768, 842-921, 1598-1610` | Generates 3 `detailed_description`-only drafts, silently rewrites prose (`bunched`->`gathered`, `thrusts a second`->`strokes a second`, deletes `(S1)` lines after `MOUTH_CONTACT_RE`, inserts `PRIMARY MOTION -`, strips `cinematic`), and overwrites `subject_definitions:`/`summary:`/`retention_analysis:`. | [pytraveler README](https://github.com/pytraveler/MiniMax-H3-Prompt-Rewriter-ComfyUI/blob/main/README.md) (`fix_once` off by default): *"the answer you get is exactly what the model wrote, with nothing edited on the way out."* |
| 11 | `wp_lint.py` + 2 auto-rewrites + LLM judge | **HELPER** / **OVERRIDE** | `parody/render_writer_pipeline.py:1612-1673, 1695-1715`, `parody/wp_lint.py:529-783` | Post-build `wp_lint` was changed to warn-only except `youth_hint` & `scale_adult` (**HELPER** for warnings; **COMMUNITY** for 18+ block). However, lines `1613-1640` still trigger up to 2 automatic rewrites (`rewrite`, `rewrite_block`) on non-safety rules (**OVERRIDE**). | [pytraveler checks.py](https://github.com/pytraveler/MiniMax-H3-Prompt-Rewriter-ComfyUI/blob/main/minimax_h3_rewriter/checks.py): *"Findings are said, never enforced — a prompt that trips a rule still ships."* |
| 12 | `submit_parody_run.py writer-run` -> `build_request.finalize_writer_prompt` | **OVERRIDE** | `parody/submit_parody_run.py:1258-1492, 1551-1651`, `parody/build_request.py:2921-3489, 3760-3873` | **Biggest override in the stack:** discards writer `subject_definitions`/`retention_analysis`, splits & reorders `detailed_description`, drops spoken lines over `max_lines`/`speech_budget`, strips `[Shot 2+]` unless `--shots multi`, strips/drops clauses via regex, injects canned camera/motion/contact/wardrobe/consent sentences, and hard-blocks (`NOT_READY`) on `WriterPromptError`/`WriterNotReady`. | [pytraveler README](https://github.com/pytraveler/MiniMax-H3-Prompt-Rewriter-ComfyUI/blob/main/README.md) & [ComfyUI R2V Template](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/video_minimax_h3_r2v.json): prompt goes directly into `MiniMaxH3ReferenceToVideo.prompt` unmodified. |
| 13 | RefMod + AddGuide + 10Eros-Max graph wiring | **COMMUNITY** | `parody/submit_parody_run.py:997-1231`, `parody/build_request.py:5402-5491`, `templates/b2_refmod.api.json:1-287` | Attaches visual/audio RefMods (`MiniMaxH3RefModsLoader`/`Apply`), frame-0 `MiniMaxH3AddGuide` (or `ref_images.ref_image_1` in `--still-mode ref`), `10Eros_Max_h3_8stepTURBO_beta7_int8HQ`, 8 steps `euler`/`simple`, shift `12/3`, VSA 10%, no negative prompt. | [Darklock/10Eros-Max](https://huggingface.co/Darklock/10Eros-Max) & [ComfyUI R2V Template](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/video_minimax_h3_r2v.json): matches 10Eros-Max beta7 settings and ComfyUI Ref2VA/AddGuide nodes. |
| 14 | `queue-remote.sh` -> `run_queue.py --remote` | **COMMUNITY** / **OVERRIDE** | `render/x3/queue-remote.sh:1-48`, `scripts/run_queue.py:341-874`, `scripts/remote_comfy.py:1-100` | `guard_reason` (18+), `static_check` (`/object_info`), `/upload/image`, `/prompt`, `/history`, `/view` download are **COMMUNITY**. `run_queue.py:544-556` (`graph_expect` + `finish`) hard-rejects ComfyUI-snapped frames (`124 != 120`) (**OVERRIDE** / Bug c). `queue-remote.sh:27-33` checks X3-local `flock` rather than AlienPc lock. | [ComfyUI API](https://docs.comfy.org/tutorials/video/minimax/minimax-h3) & [nodes_minimax_h3.py:50-63](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_minimax_h3.py): ComfyUI snaps `length` internally to `17k+5`. |
| 15 | Post-pass & state logging | **HELPER** | `parody/render_writer_pipeline.py:1756-1814`, `scripts/run_queue.py:846-863` | Updates `dialogue_blacklist.jsonl`, `recent_outputs.jsonl`, `last_tone.txt`, `scene_state.json`, `pick.json`; AlienPc runs RTX VSR 2x upscale. (Bug: `summary_line` at `1813` hardcodes `queued=False`.) | Standard local bookkeeping; non-blocking. |

---

## 2. Every Bug and Mismatch Found (Including (c)) & Smallest Fix

### (c) `--frames 120` off-grid -> H3 renders 124 -> `run_queue.py` objective check rejects it
- **Root cause (exact path):**
  1. `parody/render_writer_pipeline.py:1435-1437` sets `clip_frames = int(job["frames"])` (`120`) verbatim when `--frames` is passed, skipping `br.snap_h3_frames`.
  2. `parody/build_request.py:231-242` (`validate_single_clip_frames`) checks only `1 <= f <= 243`; it never checks or snaps to `(f - 5) % 17 == 0`.
  3. `parody/submit_parody_run.py:1645` (`_writer_run_cli`), `371` (`submit_parody_job`), and `parody/build_request.py:3814, 6310, 6421-6422` write `length: 120` into `c0.inputs.length` and `build_report.json`.
  4. `render/x3/queue-remote.sh:21-22` reads `120` and passes `--frames 120` to `run_queue.py`.
  5. ComfyUI's `MiniMaxH3ReferenceToVideo` (`nodes_minimax_h3.py:50-63`, `align_frame_count`) runs `while n % 17 != 5: n += 1`, snapping `120` **up** to `124` (`17 * 7 + 5`) and rendering a `124`-frame MP4.
  6. `scripts/run_queue.py:422-425, 544-556` (`graph_expect` + `finish`) reads `c0.inputs.length` (`120`) as `ef = 120` and fails the clip with `FAIL ... objective frames 124 != 120`.
- **Smallest fix:**
  1. Add `align_h3_frames(frames: int) -> int` in `build_request.py` matching ComfyUI's exact rule (`while f % 17 != 5: f += 1`, clamped to `SINGLE_CLIP_MAX_FRAMES = 243` via `min(f, 243)` if `f > 243` raises as before), and apply it in `validate_single_clip_frames` (or at entry in `render_writer_pipeline.py:1437`, `submit_parody_run.py:1645`, and `build_request.py:6422`). Then `120` becomes `124` at build time across `slots.json`, `c0.inputs.length`, `build_report.json`, and `queue-remote.sh`.
  2. In `scripts/run_queue.py:415-445` (`graph_expect`), also inspect `MiniMaxH3ImageToVideo` and `EmptyMiniMaxH3LatentAV` (not only `MiniMaxH3ReferenceToVideo`), and apply `while f % 17 != 5: f += 1` to `f` when `f >= 5` so `graph_expect` always matches ComfyUI's actual output length even for manually built graphs.

### (a) Talk `line_topics` `minItems` vs lint (fixed in schema, residual speech-cap bug live)
- **Observation:** `BEAT_SCHEMA_TALK` (`render_writer_pipeline.py:295`) now sets `minItems: 3, maxItems: 4`, matching `wp_lint.MODE_RULES["talk"]["min_lines"] = 3` (`wp_lint.py:64`).
- **Residual live mismatch:** For a default 8s (`192f`) talk clip, `render_writer_pipeline.py:1444` sets `max_lines_spk = max(2, round(8.0 / 5.0)) = 2`, and `build_request.py:3092` sets `max_lines = max(1, int(round(8.0 / 5.0))) = 2` per speaker. In a solo talk clip (`(S1)` speaking alone, no `(S2)`), `convert_speech` (`build_request.py:1367-1376`) **drops `(S1)`'s 3rd spoken line**, leaving 2 lines — while `wp_lint.py:752-753` requires `>= 3` lines!
- **Smallest fix:** Stop dropping spoken lines in `convert_speech` (or set `max_lines >= 5` for `talk` clips / warn-only).

### (b) Lint was made warn-only except `youth_hint` & `scale_adult`, but pipeline & builder still rewrite and block
- **Observation:** `render_writer_pipeline.py:1703-1708` only downgraded `wp_lint`'s post-build gate. Three active overrides still alter or block the prompt:
  1. `render_writer_pipeline.py:1613-1640` still runs `rewrite` and `rewrite_block` loops whenever `wp_lint` reports non-passing / `block_ready` issues (`writer_pipeline/config.yaml:47`).
  2. `render_writer_pipeline.py:1675-1693` invokes `submit_parody_run.py writer-run` -> `build_request.build_writer_request(..., strict=True)` (`build_request.py:3804`) -> `finalize_writer_prompt(..., strict=True)` (`build_request.py:2921-3489`), which replaces `subject_definitions` and `retention_analysis`, strips/reorders `detailed_description`, drops spoken lines, injects canned sentences, and raises `WriterPromptError`/`WriterNotReady` (`NOT_READY`) on `issues`, `final_lint`, `packed_beats`, `w5_final`, `audio_act_checks`, `scene_addenda.check_prompt`, `act:false`, `off_still_undefined`, and `writer_gate` (<400 tokens).
  3. `render_writer_pipeline.py:1404-1408` still hard-blocks `cowgirl`/`reverse_cowgirl` on waist-high surfaces as `NOT_READY` (`surface_mismatch`).
- **Smallest fix:** In `build_writer_request` / `finalize_writer_prompt`, add a helper/passthru path (or `advisory=True` default) that logs findings as warnings without rewriting prose or raising `NOT_READY` (keeping ONLY 18+ `youth_hint`/`_MINOR_RE` and missing file/RefMod hardware errors as hard stops); gate `rewrite`/`rewrite_block`/`rewrite_builder` behind an opt-in `--fix-once` flag (off by default, matching `pytraveler`), and downgrade `surface_mismatch` (`1404-1408`) to a warning.

### (d) `summary_line` hardcodes `queued=False`
- **Observation:** `parody/render_writer_pipeline.py:1813` ends with literal `queued=False` even when `--queue --yes-derrick` succeeded (`r["submitted"] == True`).
- **Smallest fix:** Change `queued=False` to `f"queued={bool(r.get('submitted'))}"`.

### (e) `[Shot 2+]` cuts and `summary:` boilerplate mismatch
- **Observation:** Official MiniMax H3 (`base-en.txt`, `ref-en.txt`, `pytraveler`) natively supports multi-shot `[Shot 2] At MM:SS.mmm` cuts. Our pipeline blocks `[Shot 2+]` in `wp_lint.py:548`, truncates at `[Shot 1]` in `clean_prose` (`render_writer_pipeline.py:678-685`), and strips `[Shot N]` in `build_request.py:1723` unless `--shots multi` is passed. Also `build_request.py:3262` injects `"; all characters are consenting adults."` into `summary:`, violating `h3-prompting` R3 (no policy boilerplate in prompt).
- **Smallest fix:** Remove the `[Shot 2+]` ban and forced stripping (keep monotonic timestamp check `<= clip_seconds` as advisory warning per `pytraveler/checks.py`); remove `"; all characters are consenting adults."` injection from `summary:`.

### (f) `ref_image_size` mismatch in `templates/b2_refmod.api.json`
- **Observation:** `templates/b2_refmod.api.json:24` has `"ref_image_size": "match"`, whereas `h3-prompting` R15, `h3-max-ref2va-prompt` R15, and `build_request.py:3757` specify `"max"` when reference images are wired on `c0`. Also `b2_refmod.api.json:22` has `"length": 192` as template default.
- **Smallest fix:** Keep `"match"` when no `ref_images` are wired (zero effect) and ensure `--still-mode ref` / `--partner2-still` sets `"max"` (already done in `_wire_ref_mode_start_still`, `build_request.py:3757`); document in `h3-parody-identity`.

### (g) `queue-remote.sh` local lock vs AlienPc lock & `run_queue.py` `graph_expect` node coverage
- **Observation:** `render/x3/queue-remote.sh:27-33` `flock`s X3-local `~/AI/locks/gpu-render.lock`, which `AGENTS.md:172` and `remote_comfy.py:14` explicitly state is invisible to AlienPc's GPU lock (`C:\AI\locks\gpu-render.lock`). Also `queue-remote.sh:44` runs `run_queue.py --detach`, returning `rc=0` before `pytest` / `static_check` / `POST /prompt` runs on X3.
- **Smallest fix:** Print clearly in `queue-remote.sh` that `flock` serializes X3 submits only (and keep non-waking `/system_stats` probe hint); expand `run_queue.py:422` `graph_expect` to check `MiniMaxH3ImageToVideo` and `EmptyMiniMaxH3LatentAV` alongside `MiniMaxH3ReferenceToVideo`.

### (h) `10Eros-Max` audio headers (`overall_soundscape:` / `non_diegetic_music:`) vs base MiniMax H3
- **Observation:** `render/rewriter/ref2va-system-prompt.md:23-24` uses MiniMax's official 6-section format (with `overall_soundscape:` and `non_diegetic_music:`), while `wp_lint.py` / `build_request.py:2987-2991` strip them per TenStrip HF #77 (`h3-prompting` R7: plain diegetic audio sentences at the end of `detailed_description` for `10Eros-Max`).
- **Smallest fix:** Keep R7's plain diegetic audio guidance in `h3-prompting` as **10Eros-Max helper advice** (not a silent regex dropper), and drop the silent stripping so a user/writer testing base H3 vs `10Eros-Max` gets exactly what was written.

---

## 3. Minimal Target Pipeline (Community Backbone + Skills as Advice Only)

Keep everything genuinely useful we built (RefMod + voice-ref resolution, frame-0 `AddGuide` / `--still-mode ref`, `5+17k` grid snapping, `16 GB` 243f cap & native latent-tail continuation, vision captioning, scene continuity memory, 18+ safety guard, `run_queue.py` remote execution + RTX 2x upscale), while stripping out all prompt-rewriting and non-safety blocking:

```text
[1. Inputs & Canvas] (COMMUNITY)
  --still, --character/--names, --ask, --aspect/--size (mult of 32), --frames/--seconds
  -> align_h3_frames() snaps onto 5+17k (<= 243f single shot; multi-beat uses native continuation)
  -> warn-only aspect mismatch check (check_still_canvas_shape)
        │
        ▼
[2. Vision Reference Caption] (COMMUNITY, optional cache still_read.json)
  1 vision call describes room, surface, light, pose, garments verbatim (NO clean_still_read word-swaps)
        │
        ▼
[3. Prompt Authoring — Skills as HELPER ONLY] (COMMUNITY + HELPER)
  Writer (direct Render pi chat writing writer_output.txt, OR single-turn writer LLM call)
  receives as ADVISORY context only:
    - Craft skills: h3-prompting (R7 10Eros plain audio cues, R8 shots/cuts, R16-R25, R37 <d>),
      h3-parody-identity (voice quality cues, framing), AGENTS.md craft notes
    - Optional mode/overlay hints (wp_router), still_read facts, scene_state.json continuity,
      recent dialogue_blacklist.jsonl (advisory "avoid repeating", never hard-blocked)
  -> Emits prompt verbatim (NO JSON beat-card gate, NO clean_prose/normalize_prose/glue_fix,
     NO assemble_output overwrite, NO finalize_writer_prompt stripping/reordering/injecting).
  -> Optional --fix-once flag (OFF by default, matching pytraveler): only re-asks LLM if explicitly requested.
        │
        ▼
[4. Advisory Prompt Check + Hard 18+ Safety Gate] (HELPER + COMMUNITY SAFETY)
  - Hard block ONLY on: 18+ youth_hint / _MINOR_RE, LLM refusal/empty prompt, missing still/RefMod files.
  - Everything else (wp_lint / H3 structure checks: missing sections, unbalanced <d>, cut > duration,
    unfilled <...>, craft notes) is PRINTED as advisory warnings/notes in pick.json & stdout. Never blocks READY.
        │
        ▼
[5. ComfyUI Graph Build & Remote Queue] (COMMUNITY + LOCKED 10Eros-Max DIALS)
  - Resolve OC/INDEX/PixlStash RefMods + audio voice refs into templates/b2_refmod.api.json
  - Inject exact writer prompt into c0.inputs.prompt + aligned length + width/height + seed + AddGuide/ref_image_1
  - queue-remote.sh -> run_queue.py --remote:
      pytest guard_scope -> comm.guard_reason (18+) -> rgj.static_check (/object_info)
      -> /upload/image -> POST /prompt -> poll /history -> ffprobe objective check (aligned graph_expect)
      -> RTX VSR 2x ULTRA post-pass (AlienPc) -> update scene_state / dialogue_blacklist / pick.json
```

---

## 4. Proposed Edits (Numbered List — DO NOT APPLY)

All backups use the repo's `_archive/<filename>.bak-20261116-u51` convention.

1. **`/home/evo/AI/community/scripts/parody/build_request.py`** (backup: `/home/evo/AI/community/scripts/parody/_archive/build_request.py.bak-20261116-u51`)
   - Add `align_h3_frames(frames: int) -> int` implementing ComfyUI's `align_frame_count` (`while f % 17 != 5: f += 1`, checking `<= SINGLE_CLIP_MAX_FRAMES`), and call it inside `validate_single_clip_frames` (lines 231–242) and `main` (lines 6421–6422) so `--frames 120` cleanly aligns to `124` everywhere (`c0.inputs.length`, `build_report.json`, `--frames`).
   - Add a `passthrough` / `advisory` mode to `build_writer_request` (lines 3760–3873) and `finalize_writer_prompt` (lines 2921–3489) — made the default for `writer-run` — that leaves the writer's `subject_definitions:`, `summary:`, `retention_analysis:`, `detailed_description:` (and `[Shot N]` / audio lines) **unmodified**, runs checks as non-blocking `warnings`/`flags`, removes `"; all characters are consenting adults."` injection (line 3262), removes spoken-line dropping in `convert_speech` (lines 1367–1376), and hard-fails **only** on `_MINOR_RE` / youth checks, missing still/RefMod/graph errors, or empty/refusal output.

2. **`/home/evo/AI/community/scripts/run_queue.py`** (backup: `/home/evo/AI/community/scripts/_archive/run_queue.py.bak-20261116-u51`)
   - In `graph_expect(g)` (lines 415–445), match `("MiniMaxH3ReferenceToVideo", "MiniMaxH3ImageToVideo", "EmptyMiniMaxH3LatentAV")` instead of only `MiniMaxH3ReferenceToVideo`.
   - Apply ComfyUI's `align_frame_count` (`while f % 17 != 5: f += 1` when `f is not None and f >= 5`) to `f` before returning, so `OBJECTIVE` never false-fails if an off-grid `length` reaches ComfyUI.

3. **`/home/evo/AI/community/scripts/parody/render_writer_pipeline.py`** (backup: `/home/evo/AI/community/scripts/parody/_archive/render_writer_pipeline.py.bak-20261116-u51`)
   - Align explicit `--frames` in `run_clip` (lines 1435–1437) via `br.align_h3_frames(int(job["frames"]))` so `slots.json`, `clip_seconds`, and `_bx` `--frames` match `124` when `120` is passed.
   - Replace the mandatory JSON Beat Card + 3-candidate + `clean_prose`/`normalize_prose`/`glue_fix`/`assemble_output` + auto-`rewrite`/`rewrite_block`/`rewrite_builder` chain (lines 1505–1694) with a single clean writer call (receiving skills, `still_read`, optional `wp_router` hints, and `scene_state`/blacklist as **advisory context only**), keeping the writer's full 4/5-section output verbatim; move `wp_lint` to pure advisory `warnings` (keeping only `youth_hint` and `scale_adult` as hard stops, already partially done at 1705–1708) and gate any auto-retry behind an explicit `--fix-once` CLI flag (default `False`).
   - Downgrade `surface_mismatch` (`cowgirl`/`reverse_cowgirl` on waist-high surface, lines 1404–1408) and missing `ending_state.pose` (`1430–1434`) from `_Stop()` (`NOT_READY`) to warnings; stop `clean_still_read` (1122–1151) from silently mutating caption strings.
   - Fix `summary_line(r)` (line 1813): change literal `queued=False` to `f"queued={bool(r.get('submitted'))}"`.

4. **`/home/evo/AI/community/scripts/parody/wp_lint.py`** (backup: `/home/evo/AI/community/scripts/parody/_archive/wp_lint.py.bak-20261116-u51`)
   - Remove the `[Shot 2+]` ban (`SHOT2_RE`, lines 30, 548) and instead check monotonic shot timestamps `<= clip_seconds` as a soft warning (matching `pytraveler/checks.py`).
   - Fix `max_lines_spk` / `talk_lines` mismatch: treat `talk_lines`, `speech_budget`, `blacklist`, `cloned`, `negatives`, `dial`, `throat`, `clearance_missing`, `act_mismatch`, and `builder_primary` as advisory notes (`hard=False`), keeping `SAFETY_HARD` focused on `youth_hint` and `scale_adult` only.

5. **`/home/evo/AI/community/scripts/parody/submit_parody_run.py`** (backup: `/home/evo/AI/community/scripts/parody/_archive/submit_parody_run.py.bak-20261116-u51`)
   - In `_writer_run_cli` (line 1645) and `submit_parody_job` (line 371), use `br.validate_single_clip_frames` (which now snaps via `align_h3_frames`) and pass `advisory=True` (or `strict=False`, no `finalize_writer_prompt` text rewriting) into `br.build_writer_request` (line 1433) unless `--strict` is explicitly passed.

6. **`/home/evo/AI/render/AGENTS.md` and `/home/evo/AI/community/skills/h3-prompting/SKILL.md`** (backups: `/home/evo/AI/render/_archive/AGENTS.md.bak-20261116-u51`, `/home/evo/AI/community/skills/h3-prompting/_archive/SKILL.md.bak-20261116-u51`)
   - Update `AGENTS.md` (lines 13–18, 156–166) so Render may either write `writer_output.txt` directly using the skills as craft advice and call `submit_parody_run.py writer-run` (passthrough), OR call `render_writer_pipeline.py` as a helper — removing the "builder checks/rejects/rewrites X" constraints and "do not edit its writer_output.txt" rule.
   - Update `h3-prompting/SKILL.md` to mark R5–R31 (except R4 18+ youth guard) explicitly as **craft guidance / helper advice** for H3 / `10Eros-Max` rather than hard parser gates, and note the `5 + 17k` frame-grid snap rule (`align_frame_count`).

7. **`/home/evo/AI/render/x3/queue-remote.sh`** (backup: `/home/evo/AI/render/x3/_archive/queue-remote.sh.bak-20261116-u51`)
   - Clarify the message at line 32 to state `"X3 submitter busy: waiting in background..."` (not `"GPU busy"`, since `~/AI/locks/gpu-render.lock` only serializes local X3 submits, while AlienPc's lock is checked inside `run_queue.py` on AlienPc).
