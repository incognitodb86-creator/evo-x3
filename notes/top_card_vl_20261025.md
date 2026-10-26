# CARD-VL - the GI046 / GI063 / GI072 scene cards re-read by the uncensored vision model

Derrick 2026-10-25 6:48 PM CT, his pick: **"Redo the orc, robot and GI072 scene cards with the uncensored vision model"**.
The three cards were `REFUSAL_TRUNCATED`, written by `coding_swift15_iq3s` at 4:43 AM; the facts files were that thin
(no room, no props, no light, no camera; GI072 had no facts.json at all). Item plan:
C:/Users/derek/5slock/ralph-community/notes/plans/card-vl-uncensored-cards.md. Nothing rendered this pass.

## The model, read off the serving config (never assumed)
`vl_judge` = `C:\AI\vlm\models\Qwen3.5-9B-The-Defiant-Fable-DARK-ROAST-Uncensored-Heretic-NEO-IMATRIX-MAX-MTP.mmproj-Q8_0.gguf`
served with `--mmproj` (llama.cpp vision projector), `C:/AI/director/config/llama-swap.yaml:74-86`, read 2026-10-25.
Uncensored in the file name; the run measured it: 6/6 asks answered, 0 decline markers, `finish_reason=stop`.
L21 handled the way `notes/ali163_vision_probe.py` proves it: `reasoning_effort=none` +
`chat_template_kwargs.enable_thinking=false`, `max_tokens=3000` (the 4:43 AM run used 700 and got empty answers with
378-521 reasoning words). Vision capability is read off the table, not assumed: `python notes/ali163_vision_probe.py
--selftest` (the seeded fault = the `mmproj` token removed from the cmd, and the probe must stop calling that row vision).

## The six paid requests (every row carries its own gpu_guard)
`C:/AI/community/notes/top_card_vl_results.json`; raw captions `C:/AI/community/notes/scenes/raw/GI0*_vl_[A|B].txt`.
Ask A = full inventory of every figure; ask B = identity, composition, room, light, camera. Start stills only, never a
rendered clip or a frame of one. Total request wall time 37 s; 0 renders; no queue post; no ComfyUI/llama-swap control call.

| scene | ask | model | gpu_guard before the request | max_tokens | finish | http | caption words | declines |
|---|---|---|---|---|---|---|---|---|
| GI046 | A | vl_judge | rc=0 IDLE | 3000 | stop | 200 | 209 | 0 |
| GI046 | B | vl_judge | rc=0 IDLE | 3000 | stop | 200 | 176 | 0 |
| GI063 | A | vl_judge | rc=0 IDLE | 3000 | stop | 200 | 305 | 0 |
| GI063 | B | vl_judge | rc=0 IDLE | 3000 | stop | 200 | 215 | 0 |
| GI072 | A | vl_judge | rc=0 IDLE | 3000 | stop | 200 | 219 | 0 |
| GI072 | B | vl_judge | rc=0 IDLE | 3000 | stop | 200 | 164 | 0 |

Start stills were hashed before the request and the ComfyUI `input/` copy is byte-compared to the approved file
(`comfy_copy_sha_match` per row): GI046 `3be40b2aeef5...`, GI063 `e8fdb85a6f2a...`, GI072 `54e13b00dcc9...`.

## What the cards say now (the model's own words, quoted verbatim in each card)
- **GI046** (`notes/scenes/GI046.md`, sha256 `f58374af9902e387...`, 2 figures, 32 evidence rows): a **blonde woman in a
  silver chain-link bikini and tiara lying prone on a beige shag rug** and a **green-skinned, extremely muscular
  humanoid in black athletic shorts kneeling behind her** in an interior living space, soft diffused light from
  front-left. The old card had neither the room, the rug, the chain-link, the tiara, the pose, nor the green figure's build.
- **GI063** (`GI063.md`, sha256 `90c0a7b195bf159f...`, 2 figures, 39 evidence rows): a **blonde woman in pink lace
  lingerie, prone on a black padded bench, chained at wrists** and an **anthropomorphic metallic robot in polished
  silver plating and black tight-fitting shorts, bent at the waist**; dark interior, a wall of heavy silver chains,
  a large flat-screen TV, cool blue glow. This is what answers needs_derrick row 18 (which start image is the robot).
- **GI072** (`GI072.md` + `GI072.facts.json`, sha256 `ceb8b438c0c84b3e...`, 2 figures, 32 evidence rows, **the scene's
  first card at all**): **two adult women** in an outdoor urban plaza, paved ground, natural overcast daylight - one in
  a shiny pink bikini kneeling on both knees, the other standing upright in a pink bikini and pink thigh-high boots
  with block heels, hands on the kneeling figure's head. Both human, no third person, no partial head at the edges.

Consent stays a gate, never an inference: each card carries the head-in-frame map, a `consent_gate` (words the frame
does not support, e.g. the old "anguished/distressed/crying" for GI063, plus a required phrasing line), and the age
floor as a canon-declaration row (`age_min: 21`,
`C:/Users/derek/5slock/plans/canon/fiction-cond-lock.md v2.3.0`). No score, rank, keep, best or winner anywhere:
KEEP is Derrick's alone, and no vision model judged any rendered output.

## The delta the prompt rows own (measured, not asserted)
`python C:/AI/community/notes/hc15_anchor_carry_build.py --top-check` full capture:
`notes/top_card_vl_topcheck_20261025.txt` (2026-10-25). Against the new cards the shipped prompts do not carry the
card, which is the point of redoing the cards. Verbatim from that capture, also copied into each `facts.json` under
`prompt_delta` with the measuring command:
- GI046 graphs (`ali163_hc15_gi046_s51150031`, c0 and c1): `F-CARD-WORDS` (missing "black athletic shorts",
  "blonde, long and wavy", "extremely muscular", "green-skinned humanoid"), `F-CARD-BANNED` (figure 1 "nude",
  "on all fours"; figure 2 "dark grey shorts", "grasped", "grey shorts", "on all fours"), `F-CARD-POSE` x2,
  `F-CARD-ROOM`, and **`TOP-MANIFEST card words in c0: 2/11`, c1: 2/11**.
- GI063 graphs (c0 and c1): `F-CARD-BANNED` ("anguished", "crying", "distressed", "he", "LED", "skin", "tail"),
  `F-CARD-POSE` x2, `F-CARD-ROOM`, `F-CARD-CONSENT` (anguished, distressed, crying), `F-CARD-CONSENT2`, and
  **`TOP-MANIFEST card words in c0: 0/12`, c1: 0/12**.
- `ck_top_facts` **PASSES** on all three new facts files, and the live gate counts **32/32** (GI046) and **39/39**
  (GI063) evidence quotes verbatim in the card. `ck_top_manifest` is RED by design: its card receipt and its note
  strings describe the card that was on disk when those renders were armed, and it demands the shipped prompts satisfy
  the card - so the receipt moves when the prompt rewrite lands (ORC-ROBOT, SUBJECT-LABELS, ANCHOR-CARRY,
  CARD-CONSENT-LINE, DIALOGUE-NO-MOUTH, NO-SOLO). GI072 has no built graph, so no prompt has been measured against
  its card; its card-shape gate measured 0 faults.

## Gates on this artifact, and the seeds that make them able to fail
```
python C:/AI/community/notes/top_card_vl_build.py --state      # model table + card status + gpu_guard, no request
python C:/AI/community/notes/top_card_vl_build.py --run        # the 6 asks (the paid pass), writes the record
python C:/AI/community/notes/top_card_vl_build.py --cards      # cards + facts.json from the record + the specs
python C:/AI/community/notes/top_card_vl_build.py --check      # record + on-disk cards judged by the gate rules
python C:/AI/community/notes/top_card_vl_build.py --selftest   # seeded faults must fire, real artifacts must not
```
Verdicts measured 2026-10-25: `VERDICT TOP_CARD_VL CLEAN` (6/6 captions, 0 declines, 0 integrity faults);
`VERDICT TOP_CARD_VL CARDS CLEAN` (`card_faults=0`, `_unresolved=[]` on all three);
`VERDICT SELFTEST_CLEAN` - 23 record seeds + 1 vision-table seed + **15 card seeds x 3 scenes = 45**, every one
firing, `silent=0`, real cards 0 faults. The card seeds include removing the model row, the caption-status row, the
sha row, the scope line, a non-verbatim quote, a required token with no evidence, a figures-row count that disagrees
with `gate.figure_count`, a head-map that disagrees with the figure rows, a consent ban with no required phrasing, a
token no caption supports, an unmeasured `prompt_delta`, and a missing gate/figure/top key.

The card builder reads only tokens a caption states verbatim: a spec token with no caption support lands in
`_unresolved` and fails `--cards` (`CARD_UNRESOLVED`), and a ban of a word a caption states is a self-contradiction
(`CARD_BAN_SUPPORTED`, word-boundary matched, scoped to the verbatim caption sections only). The superseded gate is
read from `git HEAD` so the measurement survives a re-run; reporting per scene, GI046 16 of 25 old tokens are still
supported and 9 are not ("fair-skinned", "muscled", "long hair", "hardwood", "warm", "dark grey shorts", "grasped",
"on all fours", "head out of frame"); GI063 5 of 14, 9 not ("blue eyes", "light complexion", "slim build", "long
hair", "bound", "shackles", "machine", "anguished", "distressed"); GI072 had no prior gate.

## Other checks run for this change (all green, each run once)
- `C:/AI/director/.venv/Scripts/python.exe -m pytest -q C:/AI/community/scripts/tests/test_p6_review.py` = **21 passed**
- `python C:/AI/community/scripts/check_web_saves.py` = **CLEAN**, 172 `notes/web/*.json` parse
- `python notes/ali02_citation_check.py --plan` = **plan path gate: 61 open-row lines, 13 citations, 0 problems**
- from ralph-community: `python notes/ali06_learnings_check.py` = **RESULT CLEAN**; `python notes/ali05_loop_check.py` = **VERDICT CLEAN**
- `python notes/rt_window_probe.py --check` = **RT_WINDOW_PROBE FAULTS 1 (RT_PERSISTENT)**, a **pre-existing red gate,
  not opened by this pass**: it measures `group=main persistent=False exclusive_true=True swap_true=True ttl=300`,
  where AGENTS.md prescribes `comfyui_auto` alone in a `persistent: true, swap: false, exclusive: false` group. The
  other 12 checks are OK (`RT_GUARD_REGION`, `RT_COMM_SHA` byte-match their pins). Nothing in this item touched
  llama-swap.yaml, and no render was queued, so the fix belongs to the GPU-window row, not to a card pass.

Budget: this item used no render minutes; `logs/p7_budget.json` read at 472.9 / 615 min, 38 / 45 jobs (unchanged by
this pass; 6 CPU-side vision requests are not ledger jobs). No `p7/JOB_REQUEST.json` was written: no render is queued.
