Goal: After `UNI-APPLY-ALIENPC-C` (Flux nodes load) and `UNI-APPLY-X3-D` (FX1 skill on the X3) have RESULTs, (1) time render stages from renders Derrick already approves (R1) and (2) test the Flux / Miraclein still candidates, so Derrick picks still templates and speed flags from results.

# BENCH-ALIENPC-1 (AlienPc Forge): render timing + Flux / Miraclein still tests, Nov 19 2026

Authority: Derrick 2026-11-19 13:46 CT ("run benchmarks first") and 13:55 CT ("while we choose prompt writer we can install and test our setup for flux miraclein"); `records/uplan/PLAN.md` items `R1`, `M4`, `ST4`, `ST5`, card 37 (yes per still), card 30 (existing still read + text lint only). "Order of work" steps A4, A5. Runs while the X3 does `BENCH-X3-W1`, but not during W1's quiet window.

## Update 2026-11-19 17:05 CT (Opus)
- Step 1 (A4 / R1) is DONE: `records/BENCH-ALIENPC-1/A4-RESULT.md`. Per-stage times were not in any log (only wall times), so R3/R4 stay untried. That was this brief's fault: it assumed ComfyUI stdout was logged.
- Step 2 (A5), per arm, before Derrick's yes (OPUS-FINDINGS #1/#2): name the model build, its upstream guide (model card or node README), steps, CFG/guidance, sampler and scheduler, with links, and follow them. Our own settings are a separate arm only if Derrick wants one.
- Hybrid arm and any subfolder LoRA: build it with `flux_still.py` from `mono` at this commit or newer. It writes `klein9\...` with a backslash, which AlienPc ComfyUI needs (OPUS-FINDINGS #4). Older copies fail with `value_not_in_list`.

## Needs before launch (ALL required)
- `UNI-APPLY-ALIENPC-C` RESULT shows the Klein9Mod nodes in `object_info` (M3 pass) and lists their widget enums; `UNI-APPLY-X3-D` RESULT shows `flux-klein-prompting` installed on the X3.
- AlienPc lease free (one line per brain `10_packs/max/max-briefing.md`); no render running (`C:\AI\locks\gpu-render.lock` absent, `:8447` idle).
- Max hands over the still test prompts in the launch message: written on the X3 (Gufo, `flux-klein-prompting` skill), adult-only, one per test below. AlienPc writes prompts only if the X3 is busy coding (backup writer).

## Work
### Step 1 — R1 render timing (no changes)
- For the next 1-2 real renders Derrick approves in chat (no extra renders), read per-stage times from the ComfyUI log (load, sampling per pass, VAE decode, RTX 2x, total) and `fast_disk` / pinned-memory messages. Record a timing table.
- This decides whether R3 (`--disable-fast-disk`, only if the log shows `fast_disk=True`) and R4 (driver sysmem fallback) are worth testing; don't change anything here.

### Step 2 — Flux / Miraclein still tests (Derrick yes per still, in chat)
- First fix nothing silently: if `UNI-APPLY-ALIENPC-C` reported a widget-name or enum mismatch for a candidate, stop and report it (Max fixes the candidate on `mono`).
- Run each through the existing queue path (`run_queue` + `C:\AI\locks\gpu-render.lock`), one at a time, only after Derrick's yes for that still:
  1. `miraclein_t2i.candidate` (M4 T2I), 2. `miraclein_refmod.candidate` (M4 RefMod — also optional Hybrid arm `0.85` RefMod + `0.60` Prodigy LoRA via `flux_still.py --hybrid "Sydney Sweeney"` or `"Megan Fox"`), 3. `miraclein_edit.candidate` (M4 single-change edit),
  4. `flux_stills_t2i_klein.candidate` (ST4), 5. `flux_stills_pose_klein.candidate` + 6. `flux_stills_layout_klein.candidate` (ST5; each reference picture goes through the existing still read + text lint first, card 30).
- Record per still: pass/fail, seconds warm and cold, peak VRAM (target < 16 GB), any node error. Derrick judges identity, skin and pose by eye; images stay on AlienPc / Hermes chat, never in git.
- Depth LoRA (card 24) only if the layout still fails to keep the background and Derrick says yes.

## Rollback
- Nothing is promoted or changed: candidates stay candidates (`S2` allowlist still REFUSEs them). Delete test outputs if Derrick asks.

## Rules
- One GPU job at a time; a real render always wins (stop and hand back). No Manager, no downloads, no template promotion, no edits to production templates. Never open PixlStash library contents or `C:\Users\derek\sydney\`.

STOP CONDITION: write `C:\AI\_archive\20261119\BENCH-ALIENPC-1-RESULT.md` (Max files it as `records/BENCH-ALIENPC-1/RESULT.md`): the R1 timing table and the per-still table, with Derrick's picks filled in by Max from chat. Clear the lease line, then stop. Next: R3/R4 only if R1 shows they help; then the TQ video A/B (step A7).
