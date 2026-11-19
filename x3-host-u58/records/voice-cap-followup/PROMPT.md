# ONE Forge turn: finish the voice-cap / shot-clock follow-up

You are Forge, working in `C:\AI\render` with community code under `C:\AI\community`. This is ONE direct turn. **No GPU render. Do not call run_queue.py. Do not take a gpu-render.lock. Do not queue anything.** Derrick decides on any rerender.

HEAD is `8ee347e`. The previous turn left **uncommitted** work in the working tree. Start from that work; do not throw it away. Finish it, fix the three known bugs, settle the packing question from official source (read-only), dry-run, test, commit, write the RESULT, and stop.

## Already on disk (keep these)

- New voice file, do not overwrite or delete, and do not touch the original 25 s file:
  `C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\models\refmods\minimaxh3_oc_poolclub_v1_refmod_audio_23s.safetensors`
  shape `[1,32,2,920]`, 23.000 s, prefix 0.000–23.000 s of the original. Original `minimaxh3_oc_poolclub_v1_refmod_audio.safetensors` is `[1,32,2,1000]`, still intact.
- Uncommitted: `scripts/parody/build_request.py` (shot-clock rebase + trimmed-voice wiring) and untracked `scripts/parody/voice_refmod_trim.py`.
- Backup already at `C:\AI\community\_archive\voice-cap-shot-lufs-20261116-0008\`. If you edit further, keep copies current.
- Prior RESULT (Max): `C:\AI\render\_handoff\2026-11-16-voice-cap-shot-lufs-RESULT.md`

Leave pre-existing unstaged hunks unstaged: `_trigger_clause` call sites in `build_request.py` and `test_t1109_writer_index_refmods.py`. Never `git add -A`. Scoped commit only. Pack beat files stay hash-identical (beat1.txt `5d507f9a774c12dd0bc40f9fbfa87514f7dcc16d6eb910ab407604cad125bd93` / beat2.txt `e893d29c03bfc0f9d38ab085afb3588271c73a03ff91da572e0201b45a85ea1f` / beat3.txt `f306fd34c09966f8558f9cdb371558c0ce7152d1815e37ebebd2f4b7ce637d7c`). Locked dials stay. Visible `192+187+187=566`. Keep the `12d0733` overlaps 39/22 and window audio 377=377, 348=348.

Official ComfyUI tree is **read-only**: `C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\`. No llama-swap.yaml, no X3.

Write `C:\AI\render\_handoff\2026-11-16-voice-cap-followup-RESULT.md`.

---

## A. Fix these three builder bugs (confirmed with a CPU probe)

1. **shot_frames TypeError.** In `build_writer_beats_continuation_request`, this line crashes:
   `[c["global_frames"] for c in shot_clocks.values()]`
   because `rebase_continuation_shot_clocks` returns the full report dict (ints and a `cuts` map). Iterate `shot_clocks["cuts"].values()` (a probe of that form already returns `[248, 320]`).

2. **Window-local clocks in the prompt, not global.** The rebase math for global frames is correct (authored 78/150 → window-local 95/167 → global 248/320). But the rewrite currently writes **global** clocks into the continuation-window prompt: `At 00:10.333` / `At 00:13.333`. The sampled window is only 226f / 9.417 s, so those times are past the end of what the model sees. Write **window-local** clocks in the prompt text: `At 00:03.958` / `At 00:06.958` (95/24 and 167/24). Keep global 248/320 in the plan/report/asserts only. Beat 3 (overlap stays 22) stays 441 and 495 globally; its window-local clocks stay 00:03.500 and 00:05.750 (or the equivalent after a no-op rebase). Do not edit the pack beat files.

3. **Duplicate `_SHOT_CLOCK_RE`.** Line ~2726 is the original pattern used by `split_shots()` on a body that starts `At 00:03.250, ...`. A later assignment (~3985) overwrites it with a `^[Shot N] At ...` pattern, and `split_shots` then reports `[Shot 2] needs a clock`. Give the new pattern its own name (e.g. `_BEAT_SHOT_CLOCK_RE`). Do not clobber the `split_shots` regex.

Keep the rebase math (`local = authored + (applied - requested)`, `global = window_start + local - applied`).

---

## B. Settle packed vs reserved, from official source, read-only

Do not assume 2000 is a fixed positional cap. The live failures were:

- value `[2000,32]` vs index `[2074,32]` (overlap 22, overlap_audio_t 37)
- value `[2000,32]` vs index `[2130,32]` (overlap 39, overlap_audio_t 65)

`8ee347e` passed the dry-run (and is the only continuation wiring that has actually been GPU-sampled on this pack past c2_samp) with **packed 0 vs reserved 130 / 74** and `cond_audio_block=False` — no cond-audio block, no indexed assignment. Beat 1 was 2000==2000.

Read, read-only, and quote the exact computation:

- `comfy/ldm/minimax/model.py` — `pack_audio`, `PackedLayout`, and the assignment `all_audio_rows[audio_update] = audio_rows` (around 710–713). What is the value tensor? What is the index / reserved length when a latent-tail keyframe is present?
- `comfy/model_base.py` MiniMaxH3 `extra_conds` (around 2199–2227) — how `cond_audio_latents` is built from references vs keyframes.
- Continuation custom nodes: `custom_nodes/comfyui-minimax-h3-continuation/continuation_nodes.py` (GuidedContinuationWindow, LatentTailGuide, layout).
- RefMod apply / ReferenceToVideo as needed.

Answer in the RESULT, with file:line citations:

- Why `0` packed vs `130`/`74` reserved is legal (no indexed write) and why `2000` vs `2000+2*overlap_audio` is not.
- After a 920-token trim, would the runtime see **`[1840,32]` vs `[1970,32]`** (still a mismatch) or something else?
- Is there **any builder-side setting** (trim length, which file is loaded, skipping a slot, a node input) that makes **packed == reserved** on c2/c3 **with the voice RefMod on**?

If yes: use that setting, wire the 23 s file (or a differently trimmed new file; never overwrite the original), and dry-run must show packed == reserved on every beat, with voice on c2/c3.

If no: **keep `8ee347e`'s voice-off path** for continuation beats (visual RefMod + latent tail; voice RefMod on beat 1 only). Leave the 23 s file on disk. Do not wire it into c2/c3. Do not change `ok` to `layout_rows <= 2000`, because that would green-light a graph that still has packed != reserved. Say so clearly in the RESULT. A rerender with voice on all beats is then **not** safe.

The 23 s file stays either way. Shot-clock fixes ship either way.

---

## C. Dry-run asserts and tests

CPU only. Extend or replace `C:\AI\community\runs\extend-test-3beat-20261115\verify_dry_c2_samp.py` as needed. Write under `dry-voice-cap-followup\` or refresh `dry-voice-cap\`; do not overwrite the approved `dry_run\` baseline. Queue nothing.

Assert and print:

- Pack hashes unchanged.
- Visible 566, overlaps 39/22, window audio 377==377 and 348==348.
- Locked dials unchanged (`verify_keep_dials`).
- Per beat: `packed_cond_audio_rows == layout_cond_audio_rows` OR the documented voice-off legal state (packed==0, cond_audio_block==False, which is also `ok`). Do not treat `1840 vs 1970` as ok.
- If voice is on c2/c3, packed == reserved and the 23 s (or chosen) file is the one loaded; beat 1 still has a voice RefMod.
- If voice is off c2/c3, say so and keep visual + tail.
- Global shot frames: beat 2 **248 and 320**, beat 3 **441 and 495**. Window-local clocks in the assembled c2 prompt are 00:03.958 and 00:06.958, not 00:10.333.
- Shot wording and beat-file bytes unchanged. Assembled c2/c3 clock strings may change.

Run the existing `scripts/parody` pytest suite (the 520 that already pass, plus any assertions you add). If the suite fails because of leftover `_trigger_clause` call sites, stash or avoid those hunks; do not include them in the commit.

## D. Commit and RESULT

Scoped commit, specific paths only, no `git add -A`. Do not stage `test_t1109_writer_index_refmods.py` or the `_trigger_clause` call-site hunks. The 23 s RefMod lives outside the community repo; mention it in the commit message and RESULT, do not try to git-add it from ComfyUI/models.

RESULT path above: packing conclusion with citations; whether voice-on-all-beats is safe; the three bug fixes; dry-run numbers; pytest count; commit hash; files/backups. Not pushed. No render.
