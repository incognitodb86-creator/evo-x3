# FLUX-LIKENESS-20261120 (Max or Derrick on AlienPc): fix celeb likeness for Klein9 RefMods and LoRAs, Nov 20 2026

Derrick, 2026-11-20 ~8:20 AM CT & ~9:07 AM CT (orchestrator chat): "the refmod and lora did not carry the correct
likeness ... Sydney sweeney and i want the miraclien". Approved D6: Sydney Sweeney (+ Megan Fox as 2nd celeb),
PixlStash search for reference photos, download `Miraclein_4.5_9b_FP8.safetensors` (8.87 GB) for arm L7, skip
downloading stock `flux-2-klein-9b-fp8` (use existing `FLUX-KLEIN-9B-FP8-NSFW.safetensors` first for L6). Plan:
[Miraclein M0-M5 plan](../source-plans/2026-11-19-alienpc-miraclein43-refmods-h3max-realism-plan.md) item **M6**.

## One-command runner (`alienpc/community/scripts/run_flux_likeness_ab.py`)

Run from any freshly pulled `mono` clone on AlienPc (uses `mono`'s `flux_still.py` directly, never stale
`C:\AI\community` copies):

```powershell
# Step 0 preflight + build all arm graphs (0s GPU):
python alienpc\community\scripts\run_flux_likeness_ab.py --dry-run --celebs "Sydney Sweeney,Megan Fox"

# Execute all arms one-by-one locally on AlienPc ComfyUI, scan logs, score ArcFace, build contact sheets:
python alienpc\community\scripts\run_flux_likeness_ab.py --run --celebs "Sydney Sweeney,Megan Fox" --ref-dir C:\AI\refs_ab
```

Place `Miraclein_4.5_9b_FP8.safetensors` (8.87 GB, Civitai model 2453960) into
`ComfyUI\models\diffusion_models\` before `--run` so arm **L7** runs (otherwise the script skips L7 cleanly).

## What the code fixes already changed (`mono`)

- `flux_still.py`: `--refmod` defaults to `fully_preserved (1.0)` at strength 1.0 (was `0.7` flexible styling);
  prepends the RefMod author's reference-anchor sentence if missing; mirrors `Klein9RefModApply` onto negative
  conditioning; omits `--remote` when queueing locally on Windows.
- `miraclein_refmod.candidate.api.json` (`x3/` and `alienpc/`): static template synced to `fully_preserved (1.0)` +
  pos/neg RefMod (node `"14"`).
- `flux-klein-prompting/SKILL.md` (`x3/` and `alienpc/`): updated likeness rules and worked example.

## Controlled one-change-per-arm matrix (same seed `51083601`, same clothed portrait prompt P)

| Arm | What it tests |
|---|---|
| **L0** | Apples-to-apples old A5 settings with **same prompt P** (hybrid 0.85/0.60, ret 0.7, no anchor, pos-only) |
| **L0-t2i** | Plain T2I control (no RefMod, no LoRA) — proves whether RefMod moves the face at all |
| **L1** | Pure RefMod, new defaults (ret 1.0, str 1.0, anchor, pos+neg, CFG 1.1) |
| **L2** | L1 at CFG 1.0 (author's CFG) |
| **L3** | Hybrid author's recipe (RefMod 0.85 + Prodigy LoRA 0.60, ret 0.7, anchor, pos+neg) |
| **L4** | Hybrid at retention 1.0 |
| **L5** | LoRA only @ 1.0 (author's pure-LoRA baseline, Miraclein NVFP4) |
| **L6** | L2 on non-KV Klein FP8 (`flux-2-klein-9b-fp8` if on disk, else existing `FLUX-KLEIN-9B-FP8-NSFW`, 8 steps `er_sde`, CFG 1.0 — never bare `kv-fp8` without `FluxKVCache`) |
| **L7** | Hybrid ret 1.0 on `Miraclein_4.5_9b_FP8.safetensors` (creator's own FP8 format; tests NVFP4 LoRA approx) |
| **L8** | Optional NSFW prompt check (pass `--nsfw-prompt-file`) |

The runner also scans ComfyUI's log (if `--comfy-log` is passed) for `lora key not loaded` / `Klein9RefMod` messages,
scores every still via `make_render.py`'s InsightFace `buffalo_l` (`FACE_PY` on CPU) when `--ref-dir` is given,
writes one labeled contact sheet per celeb, and writes `RESULT.md` inside `--out-dir` (no images or prompt prose in git).
