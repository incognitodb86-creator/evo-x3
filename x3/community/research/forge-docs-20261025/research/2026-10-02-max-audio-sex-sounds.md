# Max/H3 audio — implement sex sounds + voices (ORC_BJ REF2VA)

**Date:** 2026-10-02 CT  
**Scope:** AlienPc `:8189` · 10Eros-Max / MiniMax-H3 REF2VA · adult 21+ fiction · **how to implement**, not Dial queue  
**Cond lock:** `COND_HC3.jpg` (ORC_BJ) · six-section pack under `/workspace/cos/status/max-ref-orc-bj-prompt-pack-2026-10-02/`  
**No Dial ping** from this note.

---

## 1) Are audio / sex sounds in our Integrity scorecard? — VERIFY

**Verdict: No hard audio / sex-SFX / voice score on S0/L1 visual Integrity.** Audio is a **deferred product gate**. Mute (or ignore incidental native audio) is OK until picture is a visual CANDIDATE.

### Path quotes (Plan / brainstorm / research / AUDIT)

| Source | Quote / column |
|--------|----------------|
| `/workspace/cos/status/ce-plan-max-first-ref-probe-2026-10-02.md` § Quality / Integrity gates | Gate table columns: **TECH · Identity · Anatomy/contact · Consistency · Motion amp · Length/continuity · Scope honesty**. Separate row: **`Audio (S0/L1)` → “Picture Integrity > audio · mute OK for v1” / “Do not FAIL S0 on missing AV polish”**. Review scoreboard: “Identity · Anatomy/contact · Consistency · Motion amp · Length class · TECH (screening)” — **no audio column**. Scripts = thumbs/collage only. |
| `/workspace/cos/status/ce-brainstorm-ai-porn-director-1min-2026-10-02.md` § Variables of success | **`Audio` \| gate / defer \| “H3 can be AV; v1 may be mute OK if picture PASS” \| After picture CANDIDATE \| “Audio polish before motion Integrity”** (anti-pattern). Score gates: “Identity + Contact Integrity + Motion amp **before** PASS; TECH ≠ PASS.” |
| `/workspace/cos/research/2026-10-02-10eros-max-hybrid-exhaustive.md` | Scoreboard columns (video): “Identity · Contact Integrity · Motion amp · Length/continuity class · Wardrobe/seam · TECH …” — **no audio**. Gap **G9**: “Audio on/off for v1 · Turbo AV failure modes · **Mute OK until picture CANDIDATE**.” Also: “Native stereo AV · Audio polish ≠ picture Integrity; mute OK for v1.” |
| `/workspace/cos/research/alienpc-ltx-stack-2026-09-25/AUDIT_10EROS_MAX_SMOKE_READY_2026-10-01.md` §8-class notes | Turbo audio failure modes: “**Thump / knock / chomp / level spikes** → Prefer **non-turbo** full steps for AV · … soundscape ‘breathing/moans’ not empty bans · raise audio shift.” Scout settings: default H3 **video shift 12 / audio shift 3**; “Raise audio shift ~6–9 if turbo audio thin.” |
| `/workspace/cos/status/max-ref-orc-bj-prompt-pack-2026-10-02/05_overall_soundscape.txt` | Current S0 prose already names wet oral / breathing / muffled moans — **prompt content ≠ score criterion**. |
| `/workspace/cos/status/max-ref-orc-bj-prompt-pack-2026-10-02/06_non_diegetic_music.txt` | `N/A` (locked for S0). |
| `/workspace/cos/gbrain/04_memory/max-first-ref-orc-bj-2026-10-02/RESUME.md` | Review: watch **mp4** for Integrity; scripts thumbs/collage only — no audio gate listed. |

**Deferred audio pass (after visual CANDIDATE):** sync to mouth/motion · intelligibility · speaker consistency · artifact class (thump/knock/chomp/spike) · levels · consent/licensing of any voice/ref_audio. Do **not** let plausible moans rescue Identity/Contact/Motion FAIL.

---

## 2) H3 native capabilities (cite Comfy + MiniMax)

### Product behavior

| Fact | Cite |
|------|------|
| Joint **video + native stereo audio** in one forward pass (voice, SFX, music); muxed MP4 | [Comfy MiniMax H3 overview](https://docs.comfy.org/tutorials/video/minimax/minimax-h3); [HF MiniMax-H3](https://huggingface.co/MiniMaxAI/MiniMax-H3) |
| Output audio **32 kHz stereo**; dialogue languages stable for 11 (incl. English) | HF MiniMax-H3 system table |
| Duration **4–15 s** trained band; open-weights short edge ~768 px @ 24 fps | HF + Comfy overview |
| **Audio settles later than picture** — speech/timbre weakest at ~8 steps; usable ≥~12; turbo Lightning (4-step R2V) starves refs **and** audio | Comfy overview § Step count |

### Modes

| Mode | Node / checkpoint | Audio role |
|------|-------------------|------------|
| **T2VA / FL2VA** | `MiniMaxH3ImageToVideo` + FL2VA weights | Prompt → AV; 3 fields: `integrated_multimodal_description` · `overall_soundscape` · `non_diegetic_music` |
| **REF2VA** | `MiniMaxH3ReferenceToVideo` + Ref2VA weights (**our SoT on `:8189`**) | Same AV latent + multimodal refs |

### REF2VA ref limits (official)

From HF MiniMax-H3 Ref2VA + Comfy `MiniMaxH3ReferenceToVideo`:

| Input | Limit |
|-------|--------|
| Images | ≤ **9** (`ref_image_1…9`) → `<Picture N>` |
| Videos | ≤ **3** clips, each **2–15 s**, total ≤15 s (`ref_video_*`) → `<Video N>` |
| Standalone audio | ≤ **3** clips, each **2–15 s**, total ≤15 s (`ref_audio_*`) → `<Audio N>` |
| Video soundtracks | ≤ **3** paired (`ref_video_audio_N` with `ref_video_N`) |
| Mixed files | ≤ **12** total |
| Solo audio | **Not allowed** as sole input — audio must accompany image and/or video (HF) |

Wire `audio_vae` (fp32 HAVE on AlienPc) so ref audio encodes as latents, not text-only.

### Prompt dialect (official)

**REF2VA six sections** (order fixed) — local SoT:  
`/workspace/cos/research/alienpc-ltx-stack-2026-09-25/MINIMAX_H3_VIDEO_PROMPT_WRITING_GUIDE_ref_en.md`  
+ [HF VIDEO_PROMPT_WRITING_GUIDE_ref_en.md](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md)  
+ [Comfy prompt guide](https://docs.comfy.org/tutorials/video/minimax/minimax-h3-prompt-guide)

1. `subject_definitions` — Subjects / Pictures / Videos / Audios + jobs  
2. `summary` — `[reference generation]` (+ `audio reference` / `audio reuse` when used)  
3. `retention_analysis` — visual markers + **audio** markers  
4. `detailed_description` — shots, motion, **dialogue/SFX timed to action**  
5. `overall_soundscape` — ambience + physical + **non-verbal human** sounds (1–4 sentences)  
6. `non_diegetic_music` — audience-only score, or **`N/A`**

**Dialogue / voice (base + ref guides, Comfy prompt guide):**

- Stable speaker IDs `(S1)`, `(S2)` by vocal-event order (not Subject number).  
- Delivery / who / action **outside** tags; inside only: `<d>[English] exact words.</d>`  
- ~**one short line per ~3 s** of clip (local prompting BP / community budget).  
- Voiceover: exact phrase `says in an off-screen voiceover` + lips remain closed.  
- Cut continuity: `<scenetrans>` both sides; truncate: `<cutoff>`.  
- **Bans as positives** — Comfy BasicGuider has **no negative** branch; “no dialogue” can amplify the banned token. Prefer explicit soundscape + `N/A` music, or state continuous ambience-only without naming banned speech.

**Audio retention markers** (`<Audio N>` in `retention_analysis`):

| Marker | Meaning |
|--------|---------|
| `fully_copy` | Source audio = entire final track 1:1 |
| `partially_copy` | Part of timeline / selected layers; may add/replace |
| `reference` | Timbre / rhythm / texture / dialogue content **without** copying waveform |
| `weak_reference` | Broad category / atmosphere only |

Define e.g. `<Audio 1> is the voice-timbre reference for <Subject 1> (S1).` then mark `reference` — write **new** lines in `<d>…</d>`; do **not** paste ref transcript unless reusing words.

**Lane split (Comfy prompt guide tip 7):**

- Shot-synced dialogue, singing, diegetic music → **`detailed_description`**  
- Ambience, physical contact, breathing, moans (non-lexical) → **`overall_soundscape`**  
- Score only audience hears → **`non_diegetic_music`** (`N/A` when none)  
- `overall_soundscape: N/A` only for **complete silence**

### Local stack notes (AlienPc Max)

- Audio VAE: `minimax_h3_audio_vae_fp32` **HAVE** (AUDIT / exhaustive).  
- Default shifts: video **12** / audio **3**; raise audio ~**6–9** if turbo audio thin (AUDIT scout).  
- TURBO-hybrid: speed OK for visual TECH; **author + AUDIT: non-turbo / fuller steps better for AV** (thump/knock/chomp/spikes).  
- Comfy: audio keeps improving after picture plateaus — don’t judge final voice on 4-step Lightning R2V.

---

## 3) Best-practice IMPLEMENTATION ladder — ORC_BJ → ~1 min

**Rule:** change **one audio axis at a time**; freeze Cond + visual POS while adding sound. HostBuffer-sensitive 16 GB box → never stack multi-ref audio under open HostBuffer / DynamicVRAM-ON fails.

### Step 0 — Silent / ignore-audio visual TECH (NOW)

**Goal:** S0 TECH then L1 visual Integrity on oral pump / ID / contact.

| Knob | Setting |
|------|---------|
| Cond | Sole `ref_image_1` = `COND_HC3.jpg` |
| Prompt pack | Frozen `INSTRUCT_REF2VA_FULL.txt` (six sections) |
| `06_non_diegetic_music` | **`N/A`** |
| `05_overall_soundscape` | Keep current neon hush / wet oral / breathing / muffled moans **or** temporarily thin to room-tone only if incidental audio distracts review — **do not score it** |
| `ref_audios` / `ref_video_audios` | **Empty** |
| Score | Plan gates only: Identity · Anatomy/contact · Consistency · Motion amp · Length · TECH |

Mute playback OK for Integrity call. Incidental native stereo may exist — ignore unless gross meltdown blocks watching the picture.

### Step 1 — Native SFX / sex sounds in six-section prompt (no audio ref)

**When:** visual CANDIDATE (or at least L1 motion PASS) on same Cond/mode.

**How (official dialect, adult fiction):**

1. Keep Cond + visual motion text frozen.  
2. Expand **`overall_soundscape`** with **concrete physical sources** tied to the act (Comfy: name sources, not “atmospheric sound design”):
   - continuous: neon-room hush, low electrical hum, close breathing  
   - beat-synced: wet oral seal / saliva, soft skin stroke on shaft, bikini-strap fabric rustle  
   - non-lexical vocals: muffled moans, breath catches — **no intelligible words** here  
3. Optionally add **one short timed SFX phrase in `detailed_description`** next to PRIMARY MOTION (diegetic contact sound on the pump beat). Do not dump dialogue into soundscape.  
4. Keep `non_diegetic_music: N/A` unless you want score (usually not for hardcore v1).  
5. Prefer **non-turbo / ~20–25 steps** for the AV accuracy cell if TURBO thumps (AUDIT). Optional one-knob: raise **audio_shift** toward 6–9 if track is thin — only after a labeled A/B.  
6. Review audio only after picture still holds: sync to pump, no thump/knock/chomp, levels, no random speech.

**ORC_BJ starter (aligned with locked pack — improve concreteness, don’t invent KEEP):**

```text
overall_soundscape:
Quiet neon-room hush under a low electrical hum continues throughout. Wet oral contact and soft skin strokes on the shaft stay audible with each pump; bikini-strap fabric rustles lightly. Close breathing and muffled, non-verbal moans rise and fall with the oral rhythm — no intelligible speech.

non_diegetic_music:
N/A
```

Current pack already matches this pattern (`05_overall_soundscape.txt`). Treat Step 1 as **axis A**: soundscape wording only.

### Step 2 — Dialogue / voiced lines in prompt (still no ref_audio)

**When:** Step 1 stable (SFX sync OK, no turbo meltdown).

**How:**

1. Assign speakers: e.g. female performer `(S1)`, partner `(S2)` only if he vocalizes. Silent partner → no ID.  
2. In `detailed_description`, next to visible mouth motion, write **one short line** for a ~5–8 s clip:

```text
<Subject 1> (S1) keeps oral contact and, between pumps, with a breathy low voice says, <d>[English] Don't stop.</d> She immediately reseals her lips around the shaft and resumes the pump.
```

3. Budget: ≤1 short line per ~3 s; leave silence/ambience for the rest or H3 fills with gibberish.  
4. State audio priority in soundscape or shot prose: **dialogue/moans foreground · contact SFX controlled · music N/A**.  
5. Score: intelligibility, correct speaker, lip sync vs `(S1)`, no extra voices.

**Do not** put the spoken words inside `overall_soundscape`.

### Step 3 — Optional short `ref_audio` (timbre / bed)

**When:** Step 2 fails timbre consistency or you need a locked voice; picture still CANDIDATE.

| Practice | Detail |
|----------|--------|
| Count | **One** clean 2–15 s clip first (`ref_audio_1` → `<Audio 1>`) |
| Content | Dry close-mic **consented** adult voice sample (or licensed bed); not a full porn mix under HostBuffer pressure |
| Prompt | `subject_definitions`: `<Audio 1> is the voice-timbre reference for <Subject 1> (S1).` |
| Retention | `reference` (timbre/delivery) — **not** `fully_copy` unless the clip **is** the entire final track |
| Pairing | Always with Cond image (audio alone illegal) |
| VAE | `audio_vae` connected |
| Multi-speaker | Official Comfy note: multi-speaker + multi audio refs can **mis-assign** voices — keep one shot / one voice ref; tie line to visible event |

**Community pattern (cite, not invent KEEP):** Reddit multi-speaker thread reports `ref_audio` as acoustic **target** (can dry out / degrade when mixed badly) vs `ref_video_audios` as soundtrack **bed**. Treat as **unverified on our hybrid** — try only as labeled A/B after Step 2 fails; zero `ref_audio` if bed+voices conflict.

### Step 4 — Post-mix only if native fails

If native AV has persistent thump/knock, wrong voice, or needs frame-accurate adult SFX:

1. Render **visual-priority** pass (soundscape `N/A` / mute OK).  
2. Replace or mix in DAW / FFmpeg: moans, wet contact, room tone, optional VO.  
3. Preserve **consent + licensing** for every voice and recording.  
4. Remux stereo; keep picture Integrity scoreboard unchanged.

Most controllable product finish; official H3 still regenerates audio rather than guaranteeing waveform copy unless `fully_copy` + matching retention.

### Step 5 — ~1 min multi-clip

- Per clip (~8–15 s): same identity Cond; **re-state** soundscape + any `(S1)` lines in that beat’s six-section pack.  
- Do **not** require one continuous 60 s native audio bed on Max first — chain visuals first (exhaustive Path #1), then unify audio in post **or** per-clip native SFX with consistent prompt lanes.  
- Audio Continuity across seams = product polish **after** seam Identity/Contact PASS.

### NSFW SFX tips (official dialect only — no fake community KEEP)

| Do | Don’t |
|----|-------|
| Name physical sources (wet seal, skin stroke, fabric, breath, muffled moan) | Vague “erotic atmosphere” / “sensual sound design” |
| Put non-lexical moans in `overall_soundscape`; lexical lines in `<d>…</d>` | Paste dirty talk into soundscape field |
| Sync SFX language to PRIMARY MOTION tempo | Ask for walls of dialogue in a 5 s TECH clip |
| Prefer fuller steps / non-turbo for AV accuracy cells | Crown TURBO thump as “sexy bass” |
| One audio axis per fair cell | Stack 3 voice refs + multi-angle sheet + `ref_image_size=max` on 16 GB |

---

## 4) What NOT to do

1. **Score audio before visual PASS** — Plan: Picture Integrity > audio; brainstorm anti-pattern “Audio polish before motion Integrity”; G9 mute until CANDIDATE.  
2. **FAIL S0/L1 for missing AV polish** — Plan Audio gate: mute OK for v1.  
3. **Stack multi-ref audio under HostBuffer / DynamicVRAM-ON** — AlienPc AIMDO HostBuffer 1450 path (`2026-10-02-hostbuffer-disable-dynamic-vram.md`); every `ref_audio` / video soundtrack adds tokens every step. Keep `ref_audios` empty until NODDV stack is stable **and** visual CANDIDATE.  
4. **Solo `ref_audio` without image/video** — HF forbids.  
5. **`fully_copy` a voice sample that isn’t the entire final mix** — marker must match behavior (Comfy prompt guide tip 6).  
6. **Negative bans** (“no random voices / no dialogue”) as the only silence control — BasicGuider has no NEG; write positive ambience + `N/A` music, or complete-silence `N/A` soundscape deliberately.  
7. **Turbo 4-step Lightning R2V as the AV quality cell** — refs under-applied + speech weakest (Comfy).  
8. **Let moans rescue Identity/Contact/Motion FAIL** — deferred audio pass never overrides visual Integrity.  
9. **Dual-wire near-duplicate refs + 3 audios “for richness”** — same HostBuffer / dilution trap as multi-angle sheets.  
10. **Post-mix over a broken oral-contact picture** — fix Cond/motion first.

---

## AlienPc `:8189` checklist (implementation)

| # | Action | Done when |
|---|--------|-----------|
| 1 | S0/L1 visual Integrity on ORC_BJ Cond, ignore/mute audio | Plan columns PASS path |
| 2 | Axis A: soundscape-only AV cell (non-turbo if TURBO thumps) | SFX sync OK |
| 3 | Axis B: one short `<d>` line + `(S1)` | Intelligible, correct lips |
| 4 | Axis C: one consented `ref_audio` timbre if needed | Timbre stable; retention=`reference` |
| 5 | Post-mix if native artifacts remain | Product AV; licenses OK |
| 6 | Chain ~1 min visuals; unify audio per-clip or in post | Seam Identity first |

---

## Sources

**Local SoT**

- `/workspace/cos/status/ce-plan-max-first-ref-probe-2026-10-02.md` — Integrity gates + Audio mute OK  
- `/workspace/cos/status/ce-brainstorm-ai-porn-director-1min-2026-10-02.md` — Audio gate/defer  
- `/workspace/cos/research/2026-10-02-10eros-max-hybrid-exhaustive.md` — G9, scoreboard, turbo AV  
- `/workspace/cos/research/alienpc-ltx-stack-2026-09-25/AUDIT_10EROS_MAX_SMOKE_READY_2026-10-01.md` — turbo thump, shifts, soundscape tips  
- `/workspace/cos/research/2026-10-02-max-h3-prompting-best-practices.md` — six-section + Audio mute/N/A for v1  
- `/workspace/cos/status/max-ref-orc-bj-prompt-pack-2026-10-02/` — locked soundscape/music  
- `/workspace/cos/research/alienpc-ltx-stack-2026-09-25/MINIMAX_H3_VIDEO_PROMPT_WRITING_GUIDE_ref_en.md`  
- `/workspace/cos/research/2026-10-02-hostbuffer-disable-dynamic-vram.md` — HostBuffer constraint  

**Official / Comfy**

- https://docs.comfy.org/tutorials/video/minimax/minimax-h3  
- https://docs.comfy.org/tutorials/video/minimax/minimax-h3-prompt-guide  
- https://docs.comfy.org/built-in-nodes/MiniMaxH3ReferenceToVideo  
- https://huggingface.co/MiniMaxAI/MiniMax-H3  
- https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md  

**Community (cite only; not local KEEP)**

- Reddit: multi-speaker / `ref_audio` vs `ref_video_audios` behavior reports — unverified on 10Eros-Max hybrid.
