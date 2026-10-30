# Max :8189 production argv (Turbo KEEP 2026-10-09 3:19 PM CT Derrick GO · restated 2026-10-14)

**PRODUCTION KEEP:** model `10Eros_Max_h3_8stepTURBO_beta6_int8` (beta6 int8 Turbo path on AlienPc) · sampler **Euler** / simple · **8 steps** · **shift 10** video / 3 audio · dynamic VRAM ON · `--use-ck-attention` · no-fp8 · ComfyUI **0.38.x pinned** · no RIFE in production.
**Tests / local loop:** **6 steps + RIFE 20**.
**Optional experiment (not default):** quality A/B vs old non-Turbo beta/25-step.

_History below (Oct 2–5) is superseded where it conflicts._

Evidence: Desktop pack `MAX_REF_ORC_BJ_SPEED_MATRIX_2026-10-02` · fair SCH warm beta 125.5s ≈BASE · STEPS-20 dropped (under-denoise) · SPARSEsol FAIL speed · Sage skipped.  
Canvas split (Auditor apply 2026-10-05 Derrick GO): soft mush at 864×480 = resolution first (Comfy MiniMax-H3 / MiniMaxAI ~768 short edge quality SoT).

**Production launch (REF2VA / Max H3 on :8189):**
```
main.py --listen 127.0.0.1 --port 8189 \
  --lowvram --disable-async-offload --disable-pinned-memory \
  --use-ck-attention
```

- **KEEP argv** dynamic VRAM ON + `--disable-async-offload` + `--disable-pinned-memory` + **no fp8** (HostBuffer 1450 / kitchen float8). Old: "NODDV triad" (superseded 2026-10-09: dynamic VRAM ON is KEEP).
- **KEEP 2026-10-09 (Derrick): dynamic VRAM ON is the production default** — Oct 8 test: cold first run 116.2s → 44.1s; hot runs unchanged. `--disable-dynamic-vram` removed from KEEP argv. ST8 default stays. All defaults REVALIDATE after rebuild.
- **KEEP argv** `--use-ck-attention` ON.
- ~~KEEP argv workflow: scheduler beta · res_multistep~~ (superseded 2026-10-09: Euler/simple Turbo) · REF2VA match · length default **124f**.
- ~~KEEP steps — Quality/ID (Oct 2): 25 steps~~ → optional experiment only (superseded by Turbo ST8 KEEP).
- **KEEP steps — Fabric/speed strip (2026-10-05 ~9:24 PM CT Derrick GO):** **8 steps** @ **768×1344** (~141s/cell). Speed lane only — (history; superseded 2026-10-09 by Turbo ST8 production KEEP).
- **Preview canvas (speed / low-VRAM dial):** **864×480** — not native quality SoT. Label soft Quality at this size as canvas miss until a fair NE768 (or Derrick GO elsewhere).
- **Quality canvas (TRY / fair after Derrick GO):** **~768 short edge** AR-locked to Cond (~1344×768 @ 16:9 when Cond is landscape). One axis only vs preview — do not peel steps / scheduler on OOM; stop and report (old "NODDV" (superseded 2026-10-09: dynamic VRAM ON is KEEP)).
- **DROP / do not promote:** STEPS-20 · SPARSEsol · Sage · Lightning/EasyCache/Spectrum/fp8 peel. (Turbo beta6 int8 is KEEP.) ("DynVRAM peel" DROP (superseded 2026-10-09: dynamic VRAM ON is KEEP).)
- ~~Do **not** re-enable DynamicVRAM until AIMDO ≥2 TECH.~~ (superseded 2026-10-09: dynamic VRAM ON is KEEP). `:8188` closed unless H2H.
- If WinError 1450 / paging-file errors return, disable dynamic VRAM for that single cell and log it.
- Remacri = export after a native quality survivor — does **not** invent generate detail missing from a soft 480.

**Derrick OK 2026-10-02 ~10:33 CT — ck CANDIDATE ON after OPT-CKATTN gate** → **KEEP 2026-10-02:** ck ON + beta + **25 steps** quality/ID. **ADD 2026-10-05:** Fabric/speed strip **KEEP ST8** (Derrick GO) — (history — Oct 2 KEEP-25 superseded 2026-10-09 by beta6 int8 Turbo ST8; 25-step now optional experiment only). STEPS-20 / SPARSEsol / Sage not promoted. Pack `FABRIC_V3_ST8_ST16_MINI`.

## Default test steps (LOCKED 2026-10-05 ~9:27 PM CT Derrick GO)
**Production = ST8 Turbo.** **Tests / local loop = ST6 + RIFE 20.** ST16 / non-Turbo 25 = optional experiment Derrick names.

## Matrix warm-first (LOCKED 2026-10-05 ~8:20 PM CT Derrick GO)
**Next Max decision matrices:** warm = **~1s sacrificial** (unscored) **then full 124f warm** (unscored) before scored rows. Do not change an in-flight pack mid-run. Optional prewarm: leave Comfy hot / no `/free` between packs; short sac can run before GO while Plan is reviewed.

## Product seeds (LOCKED 2026-10-06 Derrick · Research/Auditor fair)
**Product / parade / diversity packs:** new **random seeds every wave** — do **not** reuse the overnight ladder `71–73` (same-video fail class with V4 peel + 1MIN).
**METHOD fair twins only:** `71–73` (or any fixed seed set) OK when labeled METHOD and comparing one axis (wiring/steps/Cond) under identical prompt.
Closed fair arms stay baseline — no re-queue same Cond/steps/seeds just to compare. Live 15s×3 already on fresh seeds — leave alone.
