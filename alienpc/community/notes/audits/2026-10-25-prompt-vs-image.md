# PROMPT vs IMAGE - HC15 / ALI-163 - 2026-10-25

item TOP-SCENE steps 1+3. Built by `C:/AI/community/notes/hc15_scene_audit_build.py --audit`; re-run that command to reproduce every row.

- image reader: `llama-swap/coding_swift15_iq3s` via nested `pi --print --tools read --thinking off` (pi 1.4.0, provider llama-swap). The model READS a START STILL and lists the figures in it. No score, no rank, no judgement, no keeper: KEEP is Derrick's alone, and no rendered clip was opened by a model for this document.
- side B: every `runs/*hc15*/request.api.json` in the tree - the prose the 22 HC15 clips were queued with.
- evidence: each fact quotes the card (`notes/scenes/<ID>.md`, whose body is the model's stdout byte-for-byte) and quotes the prompt clause. Detector `D5FACT_EVIDENCE` fails the build if any quoted string is not verbatim in the captured stdout.
- scope: start stills under `C:/Users/derek/5slock/approved_characters/` only. A caption of a render is out of scope (fix_plan.md VIS).

## 1. the card facts (what the picture actually contains)

| still | figures | species | non-human figure | hair in the card | room | caption_status |
|---|---|---|---|---|---|---|
| BD002 | 2 | 2 human female-presenting adults (no non-human figure) | no | Subject 1=dark blonde / dirty-blonde, darker roots; Subject 2=dark brown/black | no room: high-key white studio cyclorama, black side bars | FULL_INVENTORY |
| BD006 | 2 | 2 human female-presenting adults (no non-human figure) | no | Subject 1=platinum/dirty blonde; Subject 2=dark brown/near-black | studio set: cream seamless backdrop, pale concrete pillar, black side flags | FULL_INVENTORY |
| BD013 | 2 | 2 human female adults (no non-human figure) | no | Subject 1=blonde, wet; Subject 2=dark brown/black | seamless white-to-light-grey studio cyclorama | FULL_INVENTORY |
| GI046 | 2 | 1 human adult + 1 non-human humanoid (green-skinned, heavily muscled) = a two-figure start | YES | Subject 1=blonde, long, wavy | interior living room: beige/tan sofa, dark hardwood floor, beige shag rug | REFUSAL_TRUNCATED |
| GI063 | 2 | 1 human adult + 1 robot (machine figure) = a two-figure start | YES | Subject 1=blonde, long, wavy | not resolvable from the caption (the model gave no room row) | REFUSAL_TRUNCATED |
| GI072 | 2 | 2 human adults (no non-human figure) | no | not reported (refused) | outdoor campus pedestrian plaza: brick buildings, green trees, overcast daylight, pink neon strip, blurred pedestrians, 16:9 letterboxed | REFUSAL_TRUNCATED |

## 2. every prompt against its card

| run | start still | card figures | subjects in prompt | solo claim | species words | card | verdict |
|---|---|---|---|---|---|---|---|
| ali163_hc15_bd002_s51150001 | BD002 | 2 | 2 (1,2) | none | none | FULL_INVENTORY | MATCH |
| ali163_hc15_bd002_s51150011 | BD002 | 2 | 2 (1,2) | none | none | FULL_INVENTORY | MATCH |
| ali163_hc15_bd002_s51150021 | BD002 | 2 | 2 (1,2) | none | none | FULL_INVENTORY | MATCH |
| ali163_hc15_bd006_s51150002 | BD006 | 2 | 2 (1,2) | none | none | FULL_INVENTORY | MATCH |
| ali163_hc15_bd006_s51150012 | BD006 | 2 | 2 (1,2) | none | none | FULL_INVENTORY | MATCH |
| ali163_hc15_bd013_s51150003 | BD013 | 2 | 2 (1,2) | none | none | FULL_INVENTORY | MATCH |
| ali163_hc15_bd013_s51150013 | BD013 | 2 | 2 (1,2) | none | none | FULL_INVENTORY | MATCH |
| ali163_hc15_gi046_s51150004 | GI046 | 2 | 1 (1) | alone in the room; standing alone; the only person in frame; the only person in that photograph | none | REFUSAL_TRUNCATED | SOLO_PROMPT_ON_2_FIGURE_START + SOLO_CLAIM_ON_2_FIGURE_START + SPECIES_ABSENT_FROM_PROMPT + HAIR_NOT_IN_CARD:dark brown |
| ali163_hc15_gi046_s51150014 | GI046 | 2 | 1 (1) | alone in the room; standing alone; the only person in frame; the only person in that photograph | none | REFUSAL_TRUNCATED | SOLO_PROMPT_ON_2_FIGURE_START + SOLO_CLAIM_ON_2_FIGURE_START + SPECIES_ABSENT_FROM_PROMPT + HAIR_NOT_IN_CARD:dark brown |
| ali163_hc15_gi046_s51150031 | GI046 | 2 | 2 (1,2) | none | green skin; green-skin; heavily muscled; orc; tusks | REFUSAL_TRUNCATED | SCALE_CLAIM_NO_HEAD_IN_CARD |
| ali163_hc15_gi046_s51150032 | GI046 | 2 | 2 (1,2) | none | green skin; green-skin; heavily muscled; orc; tusks | REFUSAL_TRUNCATED | SCALE_CLAIM_NO_HEAD_IN_CARD |
| ali163_hc15_gi063_s51150005 | GI063 | 2 | 1 (1) | alone in the room; the only bodies in the shot; the only person in frame; the only person in that photograph | none | REFUSAL_TRUNCATED | SOLO_PROMPT_ON_2_FIGURE_START + SOLO_CLAIM_ON_2_FIGURE_START + SPECIES_ABSENT_FROM_PROMPT + HAIR_NOT_IN_CARD:dark-haired |
| ali163_hc15_gi063_s51150015 | GI063 | 2 | 1 (1) | alone in the room; the only bodies in the shot; the only person in frame; the only person in that photograph | none | REFUSAL_TRUNCATED | SOLO_PROMPT_ON_2_FIGURE_START + SOLO_CLAIM_ON_2_FIGURE_START + SPECIES_ABSENT_FROM_PROMPT + HAIR_NOT_IN_CARD:dark-haired |
| ali163_hc15_gi063_s51150031 | GI063 | 2 | 2 (1,2) | none | chrome; hydraulic; machine; robot | REFUSAL_TRUNCATED | MATCH |
| ali163_hc15_gi063_s51150032 | GI063 | 2 | 2 (1,2) | none | chrome; hydraulic; machine; robot | REFUSAL_TRUNCATED | MATCH |
| ali163_hc15_gi072_s51150006 | GI072 | 2 | 2 (1,2) | none | none | REFUSAL_TRUNCATED | CARD_NO_HAIR_ROW |
| ali163_hc15_gi072_s51150016 | GI072 | 2 | 2 (1,2) | none | none | REFUSAL_TRUNCATED | CARD_NO_HAIR_ROW |
| hc15_bd002_s51150001 | BD002 | 2 | 2 (1,2) | none | none | FULL_INVENTORY | MATCH |
| hc15_bd006_s51150002 | BD006 | 2 | 2 (1,2) | none | none | FULL_INVENTORY | MATCH |
| hc15_bd013_s51150003 | BD013 | 2 | 2 (1,2) | none | none | FULL_INVENTORY | MATCH |
| hc15_gi046_s51150004 | GI046 | 2 | 1 (1) | alone in the room; standing alone; the only person in frame; the only person in that photograph | none | REFUSAL_TRUNCATED | SOLO_PROMPT_ON_2_FIGURE_START + SOLO_CLAIM_ON_2_FIGURE_START + SPECIES_ABSENT_FROM_PROMPT + HAIR_NOT_IN_CARD:dark brown |
| hc15_gi063_s51150005 | GI063 | 2 | 1 (1) | alone in the room; the only bodies in the shot; the only person in frame; the only person in that photograph | none | REFUSAL_TRUNCATED | SOLO_PROMPT_ON_2_FIGURE_START + SOLO_CLAIM_ON_2_FIGURE_START + SPECIES_ABSENT_FROM_PROMPT + HAIR_NOT_IN_CARD:dark-haired |
| hc15_gi072_s51150006 | GI072 | 2 | 2 (1,2) | none | none | REFUSAL_TRUNCATED | CARD_NO_HAIR_ROW |

## 3. the mismatches, with the words that prove them

### ali163_hc15_gi046_s51150004 (`GI046`)
- verdict: SOLO_PROMPT_ON_2_FIGURE_START + SOLO_CLAIM_ON_2_FIGURE_START + SPECIES_ABSENT_FROM_PROMPT + HAIR_NOT_IN_CARD:dark brown
- the card: 2 figures - "Two figures."
- the card on species: 1 human adult + 1 non-human humanoid (green-skinned, heavily muscled) = a two-figure start "large, heavily muscled green-skinned figure in dark grey shorts" "no head"
- the card on hair: "fair-skinned blonde person with long wavy hair"
- the prompt says: "alone in the room" (1 subjects named: 1)
- the prompt says: "standing alone" (1 subjects named: 1)
- the prompt says: "the only person in frame" (1 subjects named: 1)
- the prompt says: "the only person in that photograph" (1 subjects named: 1)
- the prompt names no non-human figure at all: 0 hits for `\borc\b`, `green-skin`, `green skin`, `heavily muscled`, `tusks?`
- hair words in the prompt: "dark brown" - card: "fair-skinned blonde person with long wavy hair"
- rendered clips in that run dir: 1. This row is a defect list, not a keep/skip order.

### ali163_hc15_gi046_s51150014 (`GI046`)
- verdict: SOLO_PROMPT_ON_2_FIGURE_START + SOLO_CLAIM_ON_2_FIGURE_START + SPECIES_ABSENT_FROM_PROMPT + HAIR_NOT_IN_CARD:dark brown
- the card: 2 figures - "Two figures."
- the card on species: 1 human adult + 1 non-human humanoid (green-skinned, heavily muscled) = a two-figure start "large, heavily muscled green-skinned figure in dark grey shorts" "no head"
- the card on hair: "fair-skinned blonde person with long wavy hair"
- the prompt says: "alone in the room" (1 subjects named: 1)
- the prompt says: "standing alone" (1 subjects named: 1)
- the prompt says: "the only person in frame" (1 subjects named: 1)
- the prompt says: "the only person in that photograph" (1 subjects named: 1)
- the prompt names no non-human figure at all: 0 hits for `\borc\b`, `green-skin`, `green skin`, `heavily muscled`, `tusks?`
- hair words in the prompt: "dark brown" - card: "fair-skinned blonde person with long wavy hair"
- rendered clips in that run dir: 1. This row is a defect list, not a keep/skip order.

### ali163_hc15_gi046_s51150031 (`GI046`)
- verdict: SCALE_CLAIM_NO_HEAD_IN_CARD
- the card: 2 figures - "Two figures."
- the card on species: 1 human adult + 1 non-human humanoid (green-skinned, heavily muscled) = a two-figure start "large, heavily muscled green-skinned figure in dark grey shorts" "no head"
- the card on hair: "fair-skinned blonde person with long wavy hair"
- hair words in the prompt: "blonde" - card: "fair-skinned blonde person with long wavy hair"
- the prompt claims "full head", "head taller" while the card reports "large, heavily muscled green-skinned figure in dark grey shorts" "no head"
- rendered clips in that run dir: 0. This row is a defect list, not a keep/skip order.

### ali163_hc15_gi046_s51150032 (`GI046`)
- verdict: SCALE_CLAIM_NO_HEAD_IN_CARD
- the card: 2 figures - "Two figures."
- the card on species: 1 human adult + 1 non-human humanoid (green-skinned, heavily muscled) = a two-figure start "large, heavily muscled green-skinned figure in dark grey shorts" "no head"
- the card on hair: "fair-skinned blonde person with long wavy hair"
- hair words in the prompt: "blonde" - card: "fair-skinned blonde person with long wavy hair"
- the prompt claims "full head", "head taller" while the card reports "large, heavily muscled green-skinned figure in dark grey shorts" "no head"
- rendered clips in that run dir: 0. This row is a defect list, not a keep/skip order.

### ali163_hc15_gi063_s51150005 (`GI063`)
- verdict: SOLO_PROMPT_ON_2_FIGURE_START + SOLO_CLAIM_ON_2_FIGURE_START + SPECIES_ABSENT_FROM_PROMPT + HAIR_NOT_IN_CARD:dark-haired
- the card: 2 figures - "a restrained person" "penetrated by a robot"
- the card on species: 1 human adult + 1 robot (machine figure) = a two-figure start "by a robot" "bound to a table (wrists chained, ankles in shackles)"
- the card on hair: "long wavy blonde hair, blue eyes, light complexion, slim build"
- the prompt says: "alone in the room" (1 subjects named: 1)
- the prompt says: "the only bodies in the shot" (1 subjects named: 1)
- the prompt says: "the only person in frame" (1 subjects named: 1)
- the prompt says: "the only person in that photograph" (1 subjects named: 1)
- the prompt names no non-human figure at all: 0 hits for `\brobot\b`, `\bandroid\b`, `\bmachine\b`, `chrome`, `hydraulic`
- hair words in the prompt: "dark-haired" - card: "long wavy blonde hair, blue eyes, light complexion, slim build"
- rendered clips in that run dir: 1. This row is a defect list, not a keep/skip order.

### ali163_hc15_gi063_s51150015 (`GI063`)
- verdict: SOLO_PROMPT_ON_2_FIGURE_START + SOLO_CLAIM_ON_2_FIGURE_START + SPECIES_ABSENT_FROM_PROMPT + HAIR_NOT_IN_CARD:dark-haired
- the card: 2 figures - "a restrained person" "penetrated by a robot"
- the card on species: 1 human adult + 1 robot (machine figure) = a two-figure start "by a robot" "bound to a table (wrists chained, ankles in shackles)"
- the card on hair: "long wavy blonde hair, blue eyes, light complexion, slim build"
- the prompt says: "alone in the room" (1 subjects named: 1)
- the prompt says: "the only bodies in the shot" (1 subjects named: 1)
- the prompt says: "the only person in frame" (1 subjects named: 1)
- the prompt says: "the only person in that photograph" (1 subjects named: 1)
- the prompt names no non-human figure at all: 0 hits for `\brobot\b`, `\bandroid\b`, `\bmachine\b`, `chrome`, `hydraulic`
- hair words in the prompt: "dark-haired" - card: "long wavy blonde hair, blue eyes, light complexion, slim build"
- rendered clips in that run dir: 1. This row is a defect list, not a keep/skip order.

### ali163_hc15_gi072_s51150006 (`GI072`)
- verdict: CARD_NO_HAIR_ROW
- the card: 2 figures - "a person performing oral sex on another" "one figure performing oral sex on another using a strap-on"
- the card on species: 2 human adults (no non-human figure) "one figure performing oral sex on another"
- hair words in the prompt: "dark brown" - card: NO HAIR ROW: the model refused the attribute catalogue for this frame, so the card cannot confirm or contradict the prompt's hair words
- disclosure: this card has no hair row (caption_status REFUSAL_TRUNCATED), so the prompt's hair words are UNVERIFIED here, not called a defect.
- rendered clips in that run dir: 1. This row is a defect list, not a keep/skip order.

### ali163_hc15_gi072_s51150016 (`GI072`)
- verdict: CARD_NO_HAIR_ROW
- the card: 2 figures - "a person performing oral sex on another" "one figure performing oral sex on another using a strap-on"
- the card on species: 2 human adults (no non-human figure) "one figure performing oral sex on another"
- hair words in the prompt: "dark brown" - card: NO HAIR ROW: the model refused the attribute catalogue for this frame, so the card cannot confirm or contradict the prompt's hair words
- disclosure: this card has no hair row (caption_status REFUSAL_TRUNCATED), so the prompt's hair words are UNVERIFIED here, not called a defect.
- rendered clips in that run dir: 0. This row is a defect list, not a keep/skip order.

### hc15_gi046_s51150004 (`GI046`)
- verdict: SOLO_PROMPT_ON_2_FIGURE_START + SOLO_CLAIM_ON_2_FIGURE_START + SPECIES_ABSENT_FROM_PROMPT + HAIR_NOT_IN_CARD:dark brown
- the card: 2 figures - "Two figures."
- the card on species: 1 human adult + 1 non-human humanoid (green-skinned, heavily muscled) = a two-figure start "large, heavily muscled green-skinned figure in dark grey shorts" "no head"
- the card on hair: "fair-skinned blonde person with long wavy hair"
- the prompt says: "alone in the room" (1 subjects named: 1)
- the prompt says: "standing alone" (1 subjects named: 1)
- the prompt says: "the only person in frame" (1 subjects named: 1)
- the prompt says: "the only person in that photograph" (1 subjects named: 1)
- the prompt names no non-human figure at all: 0 hits for `\borc\b`, `green-skin`, `green skin`, `heavily muscled`, `tusks?`
- hair words in the prompt: "dark brown" - card: "fair-skinned blonde person with long wavy hair"
- rendered clips in that run dir: 1. This row is a defect list, not a keep/skip order.

### hc15_gi063_s51150005 (`GI063`)
- verdict: SOLO_PROMPT_ON_2_FIGURE_START + SOLO_CLAIM_ON_2_FIGURE_START + SPECIES_ABSENT_FROM_PROMPT + HAIR_NOT_IN_CARD:dark-haired
- the card: 2 figures - "a restrained person" "penetrated by a robot"
- the card on species: 1 human adult + 1 robot (machine figure) = a two-figure start "by a robot" "bound to a table (wrists chained, ankles in shackles)"
- the card on hair: "long wavy blonde hair, blue eyes, light complexion, slim build"
- the prompt says: "alone in the room" (1 subjects named: 1)
- the prompt says: "the only bodies in the shot" (1 subjects named: 1)
- the prompt says: "the only person in frame" (1 subjects named: 1)
- the prompt says: "the only person in that photograph" (1 subjects named: 1)
- the prompt names no non-human figure at all: 0 hits for `\brobot\b`, `\bandroid\b`, `\bmachine\b`, `chrome`, `hydraulic`
- hair words in the prompt: "dark-haired" - card: "long wavy blonde hair, blue eyes, light complexion, slim build"
- rendered clips in that run dir: 1. This row is a defect list, not a keep/skip order.

### hc15_gi072_s51150006 (`GI072`)
- verdict: CARD_NO_HAIR_ROW
- the card: 2 figures - "a person performing oral sex on another" "one figure performing oral sex on another using a strap-on"
- the card on species: 2 human adults (no non-human figure) "one figure performing oral sex on another"
- hair words in the prompt: "dark brown" - card: NO HAIR ROW: the model refused the attribute catalogue for this frame, so the card cannot confirm or contradict the prompt's hair words
- disclosure: this card has no hair row (caption_status REFUSAL_TRUNCATED), so the prompt's hair words are UNVERIFIED here, not called a defect.
- rendered clips in that run dir: 1. This row is a defect list, not a keep/skip order.

## 4. needs-Derrick (the card changes a premise; not mine to resolve)

- **GI063 consent read.** The card for GI063 reports the woman as restrained and in distress: "bound to a table (wrists chained, ankles in shackles)" and "an anguished, distressed expression", and the model reads the scene as "That's non-consensual sexual content.". The canon lock (C:/Users/derek/5slock/plans/canon/fiction-cond-lock.md) makes every character a fictional adult; a start still whose own caption is restraint-plus-distress cannot be written into an enthusiastic-consent scene by editing prose alone. Your call: replace the GI063 start still, or state how the scene treats it. Nothing in this pass edits the GI063 prompts.
- **GI046 head/scale.** The card reports the second figure with NO head in frame ("only its torso, arms, hands and legs are in frame - no head"), so a prompt that fixes his height ("a full head taller") is inventing a fact the reference cannot support. s51150031/s51150032 carry that phrase.
- **the armed p7 request cites a superseded probe.** p7/JOB_REQUEST.json (armed for GI046/GI063 s51150031/s51150032, untouched in this pass) cites `notes/hc15_gi_figures_2026-10-25.md`, whose green test measured 0.0000 at GI046. The vision read reports a green-skinned figure in the same frame, so that row measures the warm cast, not skin. The figures file is the monitor's artifact (not edited here); the card is the citation to use for species.
- **caption reach.** ask A returned a full per-figure inventory for BD002/BD006/BD013 and, on the three explicit GI frames, refused the body catalogue while still naming the figure count, species, room and light. ask B (non-sexual fields only) was refused on all three GI frames. Both refusals are in the cards verbatim. So the cards are complete for the BD set and decisive-not-exhaustive for the GI set.

## 5. sources

- start still BD002: `C:/Users/derek/5slock/approved_characters/FLOW_BLONDE_DARK_PAIRS_2026-10-19/BD002.jpg` (584054 bytes, sha256 8209bfb95593553c0d430da1659dd3435603adf99b84fec31692d030855b7cb6)
  - caption stdout `notes/scenes/raw/BD002.txt` (2704 bytes, sha256 348b35a9df3ed32e372bd38eb0d44ba2e7f7d1db66129bf3634807f52abbe536, ask A, wall 21s, rc 0)
- start still BD006: `C:/Users/derek/5slock/approved_characters/FLOW_BLONDE_DARK_PAIRS_2026-10-19/BD006.jpg` (689369 bytes, sha256 15b9d267c3c52323fb7ed1625f709e97c1f4cddc5e3dd046f17f78497b237bd4)
  - caption stdout `notes/scenes/raw/BD006.txt` (2740 bytes, sha256 9ecf270d1044d8516faa10b2073a3862ff970d4b102cd9f8078a4018388e29d9, ask A, wall 17s, rc 0)
- start still BD013: `C:/Users/derek/5slock/approved_characters/FLOW_BLONDE_DARK_PAIRS_2026-10-19/BD013.jpg` (604111 bytes, sha256 fbb90d143e586ad68a7e36505c5e70eccdc669a380a6061f2ad28a4edd7153ce)
  - caption stdout `notes/scenes/raw/BD013.txt` (2066 bytes, sha256 5122a69dc3654cd8cd3c225acde3d625d024ac8d76cd5982a7cf3762c8918006, ask A, wall 14s, rc 0)
- start still GI046: `C:/Users/derek/5slock/approved_characters/GROK_IMAGINE_2026-10-19/GI046.jpg` (567489 bytes, sha256 3be40b2aeef5dc9876b4c5a2ad489800d97cdea3571b6b76f11b2e3db08cbdfd)
  - caption stdout `notes/scenes/raw/GI046.txt` (1407 bytes, sha256 8bc946031f0ab543765eb88a0848fd652405ebd29f3b8dcf373c7a181b39115d, ask A, wall 14s, rc 0)
  - caption stdout `notes/scenes/raw/GI046_2.txt` (1226 bytes, sha256 b711da16d2acd6ce75ba32f489c0c4d8b573009cf31d94bb46034ad0b7b84a98, ask B, wall 9s, rc 0)
- start still GI063: `C:/Users/derek/5slock/approved_characters/GROK_IMAGINE_2026-10-19/GI063.jpg` (531083 bytes, sha256 e8fdb85a6f2a2cce82fbc1a3a32aaa71c1d732be87efae3e7f16a1c5bd977295)
  - caption stdout `notes/scenes/raw/GI063.txt` (885 bytes, sha256 f113852d84427b9a77111d1a0fa43eb2c74c5a6aac942a7bf1c4038754e04a77, ask A, wall 12s, rc 0)
  - caption stdout `notes/scenes/raw/GI063_2.txt` (1337 bytes, sha256 5db4267b7e01a7eb7c1205a6c298099c904d83e0e958b6af5f69679d27a11e22, ask B, wall 14s, rc 0)
- start still GI072: `C:/Users/derek/5slock/approved_characters/GROK_IMAGINE_2026-10-19/GI072.jpg` (519486 bytes, sha256 54e13b00dcc9895331e3b8cfef08dae95c4fdf7305f7736c392ebb2658417588)
  - caption stdout `notes/scenes/raw/GI072.txt` (914 bytes, sha256 9b8baf45d6cf557cea8c4164e9471c79b6547aa0974700c72e057686e0ea6072, ask A, wall 10s, rc 0)
  - caption stdout `notes/scenes/raw/GI072_2.txt` (1337 bytes, sha256 3ba2fc85ce71e20d8c9dd0b69fbd677429aaa813e4e5421684e51296591c3736, ask B, wall 12s, rc 0)
- cards: `notes/scenes/BD002.md`, `notes/scenes/BD006.md`, `notes/scenes/BD013.md`, `notes/scenes/GI046.md`, `notes/scenes/GI063.md`, `notes/scenes/GI072.md`
- prompt side: 23 request.api.json files under `C:/AI/community/runs/*hc15*`
- builder + detectors: `C:/AI/community/notes/hc15_scene_audit_build.py` (`--check`, `--selftest`)
- canon lock: `C:/Users/derek/5slock/plans/canon/fiction-cond-lock.md`

no render, no queue, no GPU call, no model verdict in this pass.
