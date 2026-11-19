# Video Template Quality Candidates (TQ1–TQ5)

Candidates only — **not live**. Production templates (`b2*`, the 8 U55 templates, `flux_stills_s2_*`) are untouched, and `alienpc/community/scripts/template_allowlist.py` (S2) refuses `*.candidate.api.json`. Promotion happens **only** after Derrick's eye pick via a Derrick-approved S2 allowlist update (`allowlist_promoted.json` / production template swap).

## Candidate Files

| File | Item | What it tests |
|---|---|---|
| `oc_guide_2pass.candidate.api.json` | TQ1 | `b2.api.json` 2-pass path (`384x672` 8-step `euler`/`simple` -> `MinimaxH3LatentUpscaler3D` 2x -> `768x1344` 3-step `beta` `denoise=0.4` refine, Pass-1 audio via `s0_sep[1]`) + `MiniMaxH3RefModsLoader`/`MiniMaxH3RefModApply` + `AddGuide` on both passes (`ag0`/`ag1`). Tests flicker reduction and skin/fabric sharpness vs 1-pass `oc_guide`. |
| `oc_ref_2pass.candidate.api.json` | TQ1 | Same 2-pass path + `RefMods`, using `c0.ref_images.ref_image_1` with `ref_image_size: "max"` (no `AddGuide`). Tests 2-pass vs 1-pass `oc_ref`. |
| `two_person.b7.candidate.api.json` | TQ4 | Beta 7 rebuild of `two_person` (`1344x768`): adds `LTXVSeparateAVLatent` (`s0_sep`), `RefMods`, and `ref_image_size: "max"`. |
| `ref2va_16x9.b7.candidate.api.json` | TQ4 | Beta 7 rebuild of `ref2va_16x9` (`1344x768`): adds `s0_sep`, `RefMods`, and `ref_image_size: "max"`. |
| `long_continuation.b7.candidate.api.json` | TQ4 | Beta 7 rebuild of `long_continuation`: upgrades `576x1024` I2V to `768x1344` `MiniMaxH3ReferenceToVideo` + `g0` + `RefMods` (beats 1 & 2) + `s0_sep` after `app1`. |

All 5 candidates keep the exact node IDs `fill_request.py` fills (`c0`, `c1`, `win1`, `img_1`/`img`/`img2`, `refmods`, `noise`, `save`).

## Queue-Time A/B Arms (Set on a Copy — No Extra Template Files)

Max / AlienPc Forge run A/B comparisons on a copy of the request using **fixed seed + same start still + same prompt** (except TQ5's prompt-header arm):

- **TQ2 (VSA dense start):** `m_vsa.inputs.start_percent`: `0.2` vs `0.0` (curbs early layout/limb/wardrobe drift; measure time/VRAM delta).
- **TQ3 (Sampler):** `ksel.inputs.sampler_name`: `res_multistep` vs `euler` with `simple` scheduler (**`er_sde` is banned** — failed 4/7 sets on Oct 30). Test on both 1-pass and 2-pass copies.
- **TQ5 (Prompt format):** header-free plain prose (via `beta7_convert.py`) vs 4-header format (`subject_definitions:`, `summary:`, `retention_analysis:`, `detailed_description:`) on identical seed, still, and graph.

## Suggested A/B Order & Promotion

1. **TQ1** — 2-pass vs 1-pass (`oc_guide`, `oc_ref`)
2. **TQ4** — Beta 7 rebuild smoke + eye check (`two_person`, `ref2va_16x9`, `long_continuation`)
3. **TQ2 / TQ3** — VSA `start_percent: 0.2` and `res_multistep` on the TQ1 winner
4. **TQ5** — header-free vs 4-header prompt on the winning graph

**Promotion rule:** winners move out of `*.candidate.api.json` into production templates / `alienpc/community/scripts/allowlist_promoted.json` only after Derrick's eye pick and approval.
