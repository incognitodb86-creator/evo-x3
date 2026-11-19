# Plan: reference-only still mode (`--still-mode ref`)

Written Mon Nov 16 2026, late morning CT. T1 plan only — do not implement until Derrick says yes, and not until the PixlStash setup is done. No renders in this write-up.

Approval so far (t1940s7144): write this plan; implement the shape-check + skill note separately (U41). This mode is the later test.

Community way: TenStrip, [HF #63](https://huggingface.co/TenStrip/10Eros-Max/discussions/63) (2026-10-12) + official Comfy [R2V](https://docs.comfy.org/built-in-nodes/MiniMaxH3ReferenceToVideo) / [native H3](https://docs.comfy.org/tutorials/video/minimax/minimax-h3-native) / [AddGuide](https://docs.comfy.org/built-in-nodes/MiniMaxH3AddGuide) docs (opened this session, 2026-11-16 CT) → adapt. Our locked graph already has `MiniMaxH3ReferenceToVideo` (`c0`) plus RefMods. The change is to skip the frame-0 AddGuide and send the still into `c0` as an un-resized reference image.

Related earlier plan (OG + pose wiring, not this crop problem): `/workspace/cos/brain-staging/40_projects/max-fix-tests/plans/2026-10-27-0820-ref2va-inputs-review-and-plan.md`.

## Goal

Run a 16:9 (or any wide) shot from a portrait still without AddGuide center-cropping the top and bottom off frame 0. Keep INDEX RefMod (face) and the voice RefMod as they are.

## How the still is wired today (guide mode)

Locked 1-pass graph (commit `4bc9bba` baseline; template `templates/b2_refmod.api.json`, INDEX + RefMod, `10Eros_Max_h3_8stepTURBO_beta7_int8HQ`).

1. `c0` = `MiniMaxH3ReferenceToVideo` builds the prompt conditioning and an empty AV latent at the canvas from `--aspect` / `--size` (`build_request.resolve_canvas`; default 768x1344). On the default path `c0` has **no** `ref_image_*` wired. Template `ref_image_size` is `match`.
2. `img_1` = `LoadImage` (the PixlStash / `--image` / `--still` start still). The template does not include this; `build_request` adds it.
3. `add_guide` = `MiniMaxH3AddGuide` (`frame_idx=0`, `image=img_1`, `positive=c0.0`, `latent=c0.1`, `vae=vvae`). Official AddGuide source (`nodes_minimax_h3.py`) resizes with `common_upscale(..., "lanczos", "center")`, so a taller still on a wider canvas is **center-cropped**, not stretched. (Do not confuse this with `MiniMaxH3ImageToVideo.first_frame`, which official docs say is stretched.)
4. `refmods` = `MiniMaxH3RefModsLoader` (INDEX look + voice slots). `refapply` = `MiniMaxH3RefModApply` (`retention 1.0`). When a guide is wired, `refapply.conditioning` is moved from `["c0", 0]` to `["add_guide", 0]`. Sampler latent is still `c0.1`.

Canvas presets: `9:16`/`portrait` 768x1344, `16:9`/`landscape`/`widescreen` 1344x768, `1:1`/`square` 1024x1024, `4:3` 1152x864, `3:4` 864x1152.

Parody prompt policy today (U2 / t289u): the `--image` still is a frame-0 keyframe and is **not** named as `<Picture N>` in the text. OC writer prompts often *do* talk about `<Picture 1>`, but the still is still pinned by AddGuide, not by a `c0` ref slot — except the S3 path, which already does `c0.inputs["ref_images.ref_image_1"] = ["img_1", 0]` when an S3 still is present (`build_request.py` ~3667).

## Proposed mode

`--still-mode guide|ref`, default **`guide`**. Default leaves today's graph unchanged.

In `ref` mode, `request.api.json` changes only around the still:

- Keep `img_1` (`LoadImage`). Do not pre-resize or crop the file.
- Wire `c0.inputs["ref_images.ref_image_1"] = ["img_1", 0]`.
- Do **not** add `add_guide` (or any `MiniMaxH3AddGuide` for the start still).
- Leave `refapply.conditioning` as `["c0", 0]` (the template's wiring). `refmods` / `refapply` stay; INDEX look and voice RefMods do not move.
- Sampler latent stays `c0.1` (empty latent). Official docs: AddGuide/R2V guides are conditioning; sampling still starts from the empty latent.
- Prompt: add TenStrip's one-liner, then the normal scene prompt:

  `<Picture 1> is the correct scene identity. All lighting, lighting hue, color palette, visual output style, camera angle, camera focal length, camera orbit, camera framing, background, background objects, and characters fully preserved from <Picture 1>.`

  This **breaks** today's parody U2 rule ("never name the still in the text"). That is expected in `ref` mode only; `guide` keeps U2. Measure voice/identity in the test.

**`ref_image_size`:** use **`max`** for the test. Official meaning: keep aspect, downscale only if the short edge is over 2048; slower, better identity. Matches TenStrip's "one not-resized image" and EllipsesMark (HF #63) "on my references I select max rather than match." Also matches `h3-prompting` R15 (Derrick 2026-10-30). The locked template still stores `match`, which is inert on the default path (no ref image). Do not silently flip `guide` mode to `max`. Optional follow-up: a second take with `match` if `max` is soft or slow. UNKNOWN: whether beta7 still has dartagnan69's beta6 motion issue when a ref's aspect does not match the canvas.

**beta7_int8HQ and R2V:** TenStrip's model card (opened 2026-11-16) says beta_7 "Does all modes" (one drawback: VSA + 90% sparsity; flicker in some single-pass setups). We already run this checkpoint through `MiniMaxH3ReferenceToVideo`. UNKNOWN until the test: how closely frame 0 matches a portrait still when it is only a reference, not an AddGuide pin — the opening is not guaranteed to be the still.

**S3:** today's S3 path already uses `ref_image_1` for the start still and adds `img_s3`. `ref` mode plus an S3 still must not collide; likely Picture 1 = start still, Picture 2 = S3. Spell that out in the implementation brief. UNKNOWN until read against a live S3 graph at implement time.

## Files to change (when approved; not U41)

- `scripts/parody/submit_parody_run.py` — `--still-mode` on the main CLI and on `writer-run`.
- `scripts/parody/render_writer_pipeline.py` — pass it through (OC entry).
- `scripts/parody/build_request.py` — the wiring above; keep `guide` as default.
- Unit tests for the graph (no queue): `ref` has `ref_image_1` and no start-still AddGuide; `guide` is unchanged; RefMods still attach; S3 numbering does not collide.
- Skills: after a pass, one line that `ref` mode is available. Not before the test.

Work only in `/home/evo/AI/community` as user `evo`. This is a locked-graph change (`4bc9bba`): Derrick's yes is required before any edit or render.

## Test (later; Derrick's yes; after PixlStash setup)

One short clip, same seed, same portrait still, canvas `--aspect 16:9` (1344x768). Two dry-then-queued takes: `--still-mode guide` vs `--still-mode ref`. Compare: does `guide` crop head/feet; does `ref` keep the whole body and still read as the same person/wardrobe/room; does the opening frame stay close to the still; do INDEX face + voice still hold. Pick the still at run time (do not browse PixlStash in this plan). No queue until Derrick says yes. Take the GPU lease only for that test.

## Rollback

Default stays `guide`. A bad `ref` run is "don't pass `--still-mode ref`." Revert the scoped commit if the flag itself mis-wires `guide`.

## Unknowns

- beta7 motion when a portrait ref is used on a 16:9 canvas (beta6 report only).
- How tightly `ref` mode opens on the still (it is not frame-0 pinned).
- Voice/identity effect of adding the TenStrip `<Picture 1>` line vs U2's text-only rule.
- S3 + `ref` picture-slot numbering.
- VRAM of one extra ref image; `max` vs `match` speed/quality on this still.

## Sources (opened this session, 2026-11-16 CT)

- TenStrip owner comment, HF #63, 2026-10-12 17:53 UTC: "the reference node does the same thing with much more control" / "one not-resized image input" / the fully-preserved `<Picture 1>` string. EllipsesMark: crop to match for i2v, `max` for references. dartagnan69, 2026-10-14: in beta6, mismatched ref aspect hurt motion; "Beta 5 handles reference images much better."
- Official Comfy R2V, AddGuide, and native H3 tutorial (R2V can feed AddGuide; `ref_image_size` `match`|`max`; sampling starts from the empty latent).
- TenStrip/10Eros-Max model card: beta_7 "Does all modes."
- Live X3 graph/template/scripts (read-only): `/home/evo/AI/community/templates/b2_refmod.api.json`, `scripts/parody/build_request.py`, `submit_parody_run.py`. AddGuide crop confirmed in local `nodes_minimax_h3.py`.
