---
name: alienpc-hardcore-i2v-director
description: Use when Derrick wants approved Condition stills animated into hardcore I2V clips on AlienPc (MiniMax-H3 / 10Eros-Max via Tailscale Serve :8446 / queue-remote.sh from the X3). Covers still-to-intent matching, the director card, and package D triage. KEEP is Derrick's GO only.
---

# AlienPc hardcore I2V director

> Render rules live in ~/AI/render/AGENTS.md; run render work from ~/AI/render. Character index: [references/characters/README.md](references/characters/README.md) (OC/PixlStash rules in [../h3-parody-identity/SKILL.md](../h3-parody-identity/SKILL.md)).

Identity = same character as the Cond. Records decide whether a character is fictional: approved_characters/INDEX.csv or max-DECISIONS.md. A face, a resemblance or a shared word in a filename ("Sheer", "Sarah") is never evidence. If you have a real concern, say it once, in one line, with the record, and pause that one item. Once Derrick answers, it's settled: don't raise it again.

- Content floor: follow rule **R2** in `/home/derekboone/AI/community/skills/h3-prompting/SKILL.md` (the adults-only floor, the minors hard stop and the real-person rule); named adult celebrity/character parodies Derrick asks for use `h3-parody-identity` (INDEX + RefMod) instead of this Cond stills lane; canon rule 4 (the image-shows-a-minor pause) and "records decide" stay this skill's gate.
- R3: never open, read, quote or parse Derrick's Grok Imagine generation prompts or prompt sidecar files (Derrick 2026-10-09).

## Where things live
- Render settings (current KEEP = B2, beta7) and how to render: the `/render` prompt template (`/home/derekboone/AI/community/agent-shared/prompts/render.md`) and skill `/home/derekboone/AI/community/skills/h3-hc-render/SKILL.md`. Don't restate settings here.
- Prompt wording (R1-R31, all lanes): `~/AI/community/skills/h3-prompting/SKILL.md`. **REF2VA picture-reference lane (non-parody):**
  the paste shape, the label set, task-type tags, retention, frame anchors, style opening, language, speech form and the
  extra gate (R32-R44) are the skill `~/AI/community/skills/h3-max-ref2va-prompt/SKILL.md` (chain: `references/chain-lane.md`).
  Cite `R<n>`; don't restate.
- Stills pose unlock: [alienpc-stills-pose-edit-prompting](../alienpc-stills-pose-edit-prompting/SKILL.md). Ops and package D triage: [video-render](../video-render/SKILL.md).

## Steps
1. **Cond.** If Derrick attached a still, that exact file is the Cond and first frame. Never swap it (no HC3/neon/P157 substitutes) unless he names another file. Before queue, the path and WxH match that file.
2. **Read the still:** pose, contact plane, solo/duo, wardrobe, AR, location.
3. **Pick an `intent_id`** the geometry supports (missionary, mating_press, prone_bone, doggy, standing_rear, standing_lift, against_wall, cowgirl, reverse_cowgirl, spooning, oral_fellatio, oral_cunnilingus, handjob, titjob, sixty_nine, solo_masturbate, choke_assist). Prefer the act the still implies; across a wave, vary intents when frames allow. Choke only when the still shows throat contact or Derrick asks. Never paste a prior KEEP POS onto a still that doesn't match it.
4. **Cond != act:** if the needed pose or bare contact doesn't fit the still, unlock the still first with stills pose-edit (Derrick clears it), or stage ordered position beats per R16. Exception: a named ORC_BJ/HC3 oral still can go to Max as is.
5. **Director card** (planning only, never pasted): intent_id, lock from still, motion, camera hold, length from the plan. Log `intent_id` on the card and in `POS_PACK_*.json`. Apply suggestions below.
6. **Max paste:** write the prompt per h3-prompting to a prompt file. One act per clip (R29). Only Max/H3 prompts go into Max TE.
7. **Render** with `/render` (Forge does the render).
8. **Check and triage** (package D): objective checks only (frames, resolution, file exists); no vision model judges, scores or picks a clip. Hard scrapes go to a reject folder with a one-line reason. Soft breaks are named in words on three axes:
   - **Identity:** a different person, broken features or a mid-clip swap. A new expression or turned head is not a break.
   - **Quality:** broken body, hands, wardrobe or contact; a garment that vanishes or teleports. Fix the wording, not another seed.
   - **Motion:** the asked action isn't visible, a freeze, or an unprompted zoom/push/crop.
9. **Hand to Derrick:** a clip that passed objective checks may be tagged **AI_KEEP** (candidate only). Derrick sets the 1-5 and gives the only KEEP. Never type PASS, KEEP or 0.95. Old KEEPs don't transfer to new stills.

## Realism & Beat Continuity Suggestions (Heuristics)
- **Motion, contact, weight, camera:** follow h3-prompting R16–R23b in `/home/derekboone/AI/community/skills/h3-prompting/references/motion-contact-anatomy.md`. Do not restate those rules here. For sex and close-action shots, use the full R23 camera sentence in motion-contact-anatomy.md; the short official line `The camera holds a static shot.` remains allowed on ordinary holds, or one move in plain English with type, amplitude and speed. No degree numbers (R23a). No bracket camera macros such as `[Med 35mm, slow push]`.
- **Shot timing & order:** follow h3-prompting R8 (shot headers and timing).
- **Lighting & Skin:** Directional key + rim avoids flat exposure. Favor pores/matte texture over smoothing words (*flawless, glowing*), without an absolute ban.
- **Motion & Contact:** Single primary action with contact indentation, per R17/R19. Resting hands on props reduces digit warping risk (no guarantee); avoid abrupt sip cutoffs.
- **Native Continuity (22f tail):** Across continuous joins (not cuts), keep framing, eyeline, wardrobe; open each beat from prior beat's final pose (start angle and gaze follow R14).
- **Dialogue & Audio Limits:** Rough guide ~8–15 words / 5s. Delivery cues (`calm deadpan poise`) guide timbre without pitch guarantee. Pair breath/friction with contact.
- *Beat 1 (Contact, ordinary hold):* `The camera holds a static shot.` Palm on table, hand on hip; directional key; matte skin, pores. Contact indentation.
- *Beat 2 (Native Join, ordinary hold):* `The camera holds a static shot.` Seamless join from Beat 1: hands anchored, eyeline held. Composed line: "Right where you are." Breath and friction.

## Notes
- Production render host is AlienPc ComfyUI (from the X3, queued via `~/AI/render/x3/queue-remote.sh` over Tailscale Serve `https://alienpc.tailf242b2.ts.net:8446`; AlienPc local: `llama-swap :8080/comfyui`). Ports :8188 and :8189 are retired.
- A ~1 min product needs a beat sheet with distinct primary motion per clip; continuous long asks use 2+ explicit native beats (carrying camera/pose across native joins) not separate clips; stitches without beats are method smokes only.
- Out of scope: ReActor face paste, EmptyLatent as Cond, Artframe, soft-sway lanes.
