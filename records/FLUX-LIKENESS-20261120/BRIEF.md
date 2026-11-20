# FLUX-LIKENESS-20261120 (Max on AlienPc): fix celeb likeness for Klein9 RefMods and LoRAs, Nov 20 2026

Derrick, 2026-11-20 ~8:20 AM CT (form answer, no message id yet): "the refmod and lora did not carry the correct
likeness ... Refmods and lora didn't look like who they were supposed to." He asked today to "debug and fix our flux
setup and ensure it works". That supersedes t3011u ("don't debug the stills") for Flux. Plan:
[Miraclein M0-M5 plan](../source-plans/2026-11-19-alienpc-miraclein43-refmods-h3max-realism-plan.md) item **M6**
(added today). Max verifies the RESULT with Derrick.

## Goal

Find which setting kills the likeness and switch to the arm that keeps it. Run one short still A/B with one change per
arm, a fixed seed, and the same prompt. Score each arm with ArcFace (InsightFace `buffalo_l`, the scorer already in
`alienpc/community/scripts/make_render.py`) and by Derrick's eye. Derrick's eye picks.

## What the code fix already changed (mono, this commit)

From the RefMod author's own guide (`malcolmrey/various` `klein9/docs/FLUX2_KLEIN9_REFMODS_GUIDE.md`, read 2026-11-20):

- `flux_still.py --refmod` now defaults to the author's likeness preset, `fully_preserved (1.0)` at strength 1.0. The A5
  runs used `partially_preserved (0.7)`, which the guide calls the flexible-styling preset. `--hybrid` keeps the
  author's hybrid recipe (RefMod 0.85, LoRA 0.60, retention 0.7).
- A RefMod prompt that never says "reference" gets the author's anchor sentence prepended ("The reference images
  represent one adult person; keep the face and hair unchanged and exact as in the reference images."). Klein is an
  edit model and must be pointed at the reference.
- The RefMod now goes into both the positive and the negative conditioning, as in the author's workflow. A5 had it on
  the positive only.
- `flux-klein-prompting` skill updated to match (its RefMod example never pointed at the reference).

Still unknown (this A/B answers it): the author tested only on distilled `flux-2-klein-9b-fp8`, never on Miraclein. Our
Miraclein file is NVFP4, and ComfyUI's LoRA patch on NVFP4 is approximate (ComfyUI PR #11866: "changes results a
bit"). The Miraclein creator runs FP8.

## Needs before launch

- Derrick's yes to this brief, and his answer to Q-FL1 to Q-FL3.
- 2-3 real reference photos per celeb for ArcFace. Derrick drops them, or Max finds them with the PixlStash search API
  by name (no browsing of library folders, tags, or name lists). If neither, score by eye only and say so.
- AlienPc lease free (one line per brain `10_packs/max/max-briefing.md`). No render running.

## Access

- Build every per-run `request.api.json` with **mono** `x3/community/scripts/parody/flux_still.py` in dry-run (no GPU),
  from the box's mono clone `/home/derekboone/evo-x3` after `git pull`, with `EVO_AI_ROOT` set to a scratch folder.
  The AlienPc staged copy of `flux_still.py` and its older `build_request.py` / `resolve.py` (A5-RESULT issue 4) are not
  used. Copy the built run folders to AlienPc and queue them locally there, the way A5 did (no `--remote`).
- Each run folder keeps its `flux_meta.json` and `prompt.txt`. Images stay on AlienPc and the QNAP, never in git.

## Work

Celebs: two that have BOTH `refmods-klein9\fk9_<name>_v1_refmod.safetensors` and
`loras\klein9\fk9_<name>_v1_prodigy.safetensors` (check with a directory listing of those two exact paths). Default:
the A5 hybrid celeb plus one Derrick names (Q-FL1).

Fixed for every arm: seed `51083601`, `768x1344`, `--no-upscale`, one clothed portrait prompt P per celeb (45-80 words,
`flux-klein-prompting`, starts with the anchor sentence, no face or hair-color words). Defaults below mean the new
mono defaults: Miraclein 4.5 NVFP4, euler, 12 steps, CFG 1.1.

| Arm | Change from the row above it | How |
|---|---|---|
| L0 | Old A5 setup (baseline) | Celeb 1: the existing A5 hybrid still (no re-render). Celeb 2: build L3, then in its `request.api.json` set the CFGGuider `negative` back to node `"6"`, take the anchor sentence out of node `"5"`, and set the retention to `partially_preserved (0.7)`. |
| L1 | Pure RefMod, new default (retention 1.0, strength 1.0, anchor, pos+neg) | `--refmod '<Name>'` |
| L1-off | Check that the RefMod is applied at all | L1 with `strength_1` set to `0.0`. If its ArcFace score is within 0.05 of L1's, the RefMod is not being applied: stop and report. |
| L2 | L1 with CFG 1.0 (the author's CFG; also skips the negative pass) | `--refmod '<Name>' --cfg 1.0` |
| L3 | Hybrid, author's recipe | `--hybrid '<Name>'` |
| L4 | L3 with retention 1.0 | `--hybrid '<Name>' --retention 'fully_preserved (1.0)'` |
| L5 | LoRA only at the author's baseline strength 1.0 | `--mode t2i --lora 'klein9/fk9_<name>_v1_prodigy.safetensors:1.0'`, P without the anchor sentence |
| L6 | L1 on a non-fine-tuned Klein base (the author's setup) | L2's `request.api.json` with node `"1"` `unet_name` = `flux-2-klein-9b-fp8.safetensors` if it is on disk, else `flux-2-klein-9b-kv-fp8.safetensors` (mark the arm "KV variant"); `steps` 8; `sampler_name` `er_sde`. |
| L7 | Best of L1-L5 with Miraclein **FP8** | Only if Derrick says yes to the 8.87 GB download (Q-FL2). Same graph, node `"1"` = `Miraclein_4.5_9b_FP8.safetensors`. |
| L8 | Best arm with the A5 adult (NSFW) prompt instead of P | Tests whether likeness drops only on explicit prompts. |

Score: ArcFace cosine of the largest face against the mean embedding of the reference photos, with the
`make_render.py` `FACE_PY` venv on CPU. Make one labeled contact sheet per celeb (arm, score, sample seconds, peak
VRAM).

## Tests

- Every arm's `request.api.json` validates in ComfyUI (no `value_not_in_list`). RefMod values are stems, LoRA names use
  `klein9\` (backslash).
- L1-off differs from L1 (the RefMod is applied).
- 18+ guard and `wp_lint` pass on every prompt.

## After the A/B (Derrick's pick)

- If the best arm is not the current mono default, change only the matching default in `flux_still.py` (or the
  candidate template's UNET), with a test, on mono. Promotion out of `*.candidate.api.json` is still a separate yes (S2).

## Q-cards for Derrick

- **Q-FL1:** the second celeb for the A/B (default: one of the skill examples with both files, such as
  `meganfox`).
- **Q-FL2:** download Miraclein 4.5 **FP8** (8.87 GB, the creator's own format) for arm L7? Default **yes**. NVFP4
  LoRA patching is approximate.
- **Q-FL3:** if `flux-2-klein-9b-fp8.safetensors` (the RefMod author's base, about 9 GB) is not on disk, download it for
  L6? Default **no** (use the KV variant first).

## Rules

- AlienPc lease as above. One arm at a time. No production template edits; per-run graph edits only. No images or
  prompt prose in git. No secrets on argv or in output.

STOP CONDITION: when done or blocked, write `records/FLUX-LIKENESS-20261120/RESULT.md` on mono with the arm table
(ArcFace score per celeb, sample seconds, peak VRAM, PNG path on AlienPc or the QNAP) and the L1-off check, then stop
for Derrick's eye pick.
