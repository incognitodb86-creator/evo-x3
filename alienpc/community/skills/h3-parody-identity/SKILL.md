---
name: h3-parody-identity
description: Use when a MiniMax H3 run names a character or actor from Malcolm INDEX (or equivalent), wires standalone RefMod on the Nov 6 single-pass native 768x1344 b2_refmod default (beta7_int8HQ, no RefLoRA, no start photo, optional --ref-audio <Audio 1>), or compiles multi-clip parody prompts from a beat sheet without spoken stage-cue leakage or static [Shot 1] boilerplate.
---

# MiniMax H3 Parody Identity (`INDEX + RefMod`)

One shared pipeline for every named character or actor parody run on MiniMax H3 (`10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors`). Never build a separate skill or code path per celebrity - resolve every character or actor through the same `INDEX` + standalone `RefMod` lookup and single-pass builder (`scripts/parody/build_request.py`, default `--graph-mode single-pass`).

## 1. Identity & Render Stack (Nov 6 2026 lock: single-pass native `768x1344`, `INDEX + RefMod` only)

1. **Default = `--graph-mode single-pass`** (Derrick `t213u`, Nov 6 2026; won the 1-pass vs 2-pass A/B on face sharpness, motion and likeness):
   - `templates/b2_refmod.api.json`, native `768x1344`, `124` frames, `8` steps `euler`/`simple`, `shift` `12` (video) / `3` (audio), `cfg=1.0`, checkpoint `10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors`.
   - `INDEX + RefMod` only: `MiniMaxH3RefModsLoader` (`mod_1..mod_8` = `models/refmods/minimaxh3_<id>_v<N>_refmod.safetensors`, `strength=1.0`) -> `MiniMaxH3RefModApply` (`retention=1.0`) -> `s0_guide`. Zero `RefLoRA`.
   - **No start photo needed**: with neither `--image` nor `--cond-source`, single-pass + standalone RefMod (no RefLoRA hybrid) builds with no `LoadImage`, no `MiniMaxH3AddGuide`, no `<Picture 1>`. A supplied photo still goes through `approved_characters` + SHA256 (FG-2/FG-11). A RefLoRA hybrid still requires a Cond.
   - `two-pass-parody` (384x672 -> 2x latent upscale -> 768x1344 beta refine) stays available only via an explicit `--graph-mode two-pass-parody`; it softens faces vs native single-pass.
2. **Fail closed on silent empty RefMod**: if a matching RefMod file exists on disk, `loaded_refmods` in `assets.json` must be non-empty (`mod_1 != "(none)"`).
3. **Optional `--ref-audio <file> --stage-ref-audio` (`<Audio 1>` voice-timbre reference)**:
   - `.wav/.mp3/.flac/.m4a/.ogg`, never a path containing `sydney`; staged to `ComfyUI\input\ref_audios\<basename>`, SHA256-verified; `ref_audio_source_path` / `ref_audio_input_name` / `ref_audio_sha256` / `ref_audio_wired` recorded in `assets.json`.
   - Graph: `ref_audio_1` = `LoadAudio {"audio": "ref_audios/<basename>"}`, wired into every `MiniMaxH3ReferenceToVideo` as the flat V3 Autogrow key `"ref_audios.ref_audio_1": ["ref_audio_1", 0]` (same form as `ref_images.ref_image_1`), with `audio_vae = ["avae", 0]` so the clip is VAE-encoded into `minimax_refs`. `minimax.py` emits the text label `<Audio 1>: ` ahead of the prompt (audio never enters Qwen).
   - Only use voice recordings Derrick supplies and has the right to use.

## 2. Clean Five-Section Prompt Contract (`h3-prompting` R5 + R32-R42)

Keep `prompt.txt` strictly visual and acoustic - compliance metadata belongs in `run_record.json`, never in conditioning text:

1. **`subject_definitions:`**:
   - `<Subject 1> is the woman in <Video 1>.` (binds the `RefMod` conditioning route).
   - `<Subject 1> <Name>, <resolved character/actor biometric + wardrobe description>, the only person in the clip` - **one** full description (`R28`; never paste another still's facial caption onto a named subject, and never append `"a fictional adult, canon age 28"`, `"styled in parody tone"`, or `(character ..., actor ...)` parentheticals). Stated adult age (21+) lives naturally inside the biometric description (`"25-year-old woman"`).
   - Include `<Picture 1> is the start frame of [Shot 1] for setting, light and framing` **only** when `ref_image_1` is wired in the graph.
2. **`summary:`**:
   - `[reference generation] <natural prose summary of who, where, wardrobe, and the single physical transition/action of this clip>.`
   - Never append `"One adult performer, adults-only."` or policy prose (`R3`).
   - Never dump raw beat-sheet field labels (`Set:`, `Wardrobe:`, `Props kept in hand:`, `Opening:`, `Ending:`, `Anchors:`, `Camera:`, `Method: planned cut`) into `summary:`.
3. **`retention_analysis:`**:
   - `<Subject 1> (appears in [Shot 1]): fully_preserved - face, hair, body, skin, wardrobe` (plus `<Picture 1>` line only when `Cond` is wired).
4. **`detailed_description:` - Real Per-Clip Camera, Action & Clean Speech**:
   - **Style line** (`R39`), followed by the clip's **actual camera line** (`R23` vocabulary: `The camera holds a static shot.`, `Tracking, slow, small amplitude...`, `Push In, slow, small amplitude...`) - never leave a hardcoded static camera line on a tracking/push-in clip.
   - **`[Shot 1] 00:00.000 - <end_clock>` must carry the clip's real pose and motion**: compile the beat sheet's opening posture, primary physical action, garment state, prop handling, and ending posture directly into `[Shot 1]`. Never leave smoke-test boilerplate (`"stands facing the camera, weight even on both feet, hands resting lightly at her sides... PRIMARY MOTION - small steady upper-body sway"`) on multi-clip scenes where the subject walks, sits, leans, undresses, or drinks, because H3 obeys `[Shot 1]` over `summary:`.
   - **Speech `<d>[English] ... </d>` holds ONLY spoken words (`R37`)**:
     - When the character speaks, emit `<Subject 1> <Name> (S1) ... says, <d>[English] <spoken words only></d>` with punctuation limited to `, . ? !`.
     - **Never** pass beat-sheet timestamps (`t=00.00.000-...`), `"No speech"`, foley/SFX cues (`room tone`, `glass clink`, `paper, card stock`, `heels on wood`), backticks, or nested `<d>` tags into `--dialogue` / `<d>...</d>`. H3's TTS skips `t=` numbers and speaks stage cues out loud.
     - On silent clips, omit `(S1)` and `<d>...</d>` completely (`dialogue=None`).
   - **Plain ambient sound sentences** at the end of `detailed_description:` carry room tone and physical foley outside `<d>...</d>` (`R7`). Never include `overall_soundscape:` or `non_diegetic_music:`.

### Nov 6 2026 clean `R37` lock (builder-enforced)
- Never `overall_soundscape:`, `no_dubs:`, `non_diegetic_music:`, `<scenedirect>`/`</scenedirect>` or `[English in ...]` (R32; TenStrip HF #77: `overall_soundscape` "is the easiest way to introduce extremely bad audio"). `format_parody_prompt` raises if any appears.
- Character + actor both resolved -> `<Subject 1>` is named `Character (Actor)` (e.g. `Jennifer Check (Megan Fox)`) in `subject_definitions`, `summary` and `[Shot 1]`.
- `--action` puts the natural blocking into `[Shot 1]` (and `summary:`) instead of the static stand/sway beat.
- Speech is inline in `[Shot 1]`: `<Subject 1> (S1) looks into the lens and says, <d>[English] <words>.</d> Her speaking voice is close, clear, and natural in the foreground.` Quotes stripped, ends in `. ? !`; stage notes (`no speech`, `[sfx`, `(no dialogue`, `t=`, `room tone`, `<d>`) raise `ValueError`.
- With `--ref-audio`: summary tag `[reference generation + audio reference]`; `subject_definitions` adds `<Audio 1> is the reference audio defining the exact vocal timbre, pitch, and speaking cadence of <Subject 1>.`; `retention_analysis` adds `<Audio 1>: reference - vocal timbre, pitch, and speaking cadence of <Subject 1>, without copying the reference audio's spoken words.`; the voice sentence after `</d>` becomes `Her speaking voice follows the close, natural vocal timbre and cadence of <Audio 1> in the foreground.` `<Subject 1> is the woman in <Video 1>.` stays (RefMod route label; `ref_videos` is not wired, and `minimax.py` only emits labels for wired refs, so `<Audio 1>` coexists with it).


## 3. Pre-Render Gates & Brief Fidelity

1. **Builder / test validation (fail closed before queuing)**:
   - Reject any `dialogue` input containing `t=\d`, `<d>`, `</d>`, backticks, `"no speech"` (case-insensitive), or `"room tone"`.
   - Reject raw beat-sheet schema headers (`Opening:`, `Ending:`, `Anchors:`, `Method:`) inside `summary:` or `detailed_description:`.
   - Verify ComfyUI `/object_info` exposes every node class in `request.api.json` (`submit_parody_run.py --dry-run`) before starting a batch.
   - Enforce `comm.guard_ok` and `comm.adult_stated` fail-closed at build time and write compliance fields (`guard_ok`, `adult_stated`, `character`, `actor`, `tone`, `description_sha256`) to `run_record.json`.
2. **Tone fidelity & prompt readback**:
   - Preserve the exact wardrobe, framing, and consensual adult/provocative parody tone specified in the brief (never sanitize a requested provocative parody into tame generic filler, while keeping `comm.guard_ok` vocabulary clean and zero non-consensual themes).
   - On multi-clip runs, inspect a sample of generated `prompt.txt` files (including silent and spoken cells) and `assets.json` (`loaded_refmods` non-empty) before `run_queue.py` launches.
