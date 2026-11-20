# REA-Video hotel_vlm2 30s validation (v1 and v2) — records

Date: 2026-11-19 night through 2026-11-20 morning, America/Chicago (CT). This is a records file for Opus review. Nothing was rerun or debugged in this pass (Derrick t3011u). No clips are in git; paths and hashes are in [QNAP-MEDIA-INDEX-20261120.md](./QNAP-MEDIA-INDEX-20261120.md).

## What was rendered

Both validations used the `hotel_vlm2` breakdown as-is (no re-decompose), FCSydny OC visual+voice RefMod, Adam Jensen visual RefMod, and `<d>` dialogue, targeting a 30-second clip on 1-pass `oc_ref` at 1344×768 landscape (Derrick t2976u / t2978u / t2980u / t2988u). The 20-minute remake and the 101-pack batch stayed held.

QNAP (share `\\NAS4CBE37.local\renders\runs`):

- v1: `reavideo_hotel_vlm2_val30s\` (concat `reavideo_val_30s.mp4`, plus `run\pack01\pack01.mp4` and `run\pack02\pack02.mp4`)
- v2: `reavideo_hotel_vlm2_val30s_v2\` (same layout)

Copied to the share 2026-11-20 06:34–06:39 CT; all hashes matched the AlienPc sources.

## videoReview

- v1: FAILED. pack01 had cloned men, an unsynced male line, and an offline fallback. pack02 had a spoken sentence during an oral-sex beat. The 20-minute batch was held.
- v2: FAILED. Clones and speech issues from v1 were gone. Tongue morphing was present on both pack clips. pack02 audio was reported to duplicate pack01. The 101-pack batch stayed held.

A separate full root-cause writeup was not found in `mono` or in `~/evo-x3/records` on the X3 this morning (2026-11-20 ~07:23 CT). The notes below are the pipeline facts already recorded from the v2 review, not a new debug.

## Recorded pipeline facts (v2 review)

- `h3max_bridge` computes per-shot start times in `best_voice_window`, then `normalize_breakdown`, `pack_shots`, and the export step drop `start`. The manifest keeps only `audio_stems` (the full `vocals.wav`) and `audio_duration_s`.
- The fill script `rv30v2_fill_graphs.py` ignores audio and uses a shared `noise_seed` 51083601.
- `MiniMaxH3ReferenceToVideo` has no negative-prompt input. Audio is generated inside the node; there is no LoadAudio node in `oc_ref`.

## Open

v3 proposal and the 101-pack batch remain held, waiting on Derrick.
