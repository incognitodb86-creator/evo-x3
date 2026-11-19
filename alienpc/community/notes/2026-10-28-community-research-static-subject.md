# 2026-10-28 ~13:50 CT - research: why a subject "just stands there" in H3, and what the community does about it

Trigger: Derek watched `terrace_dom_20261028_s51083002.mp4` - "it wasn't that great as she just stood there after being slapped".
Cell audit re-run first: `python C:\AI\community\scripts\verify_cell.py <run_dir>` = **all checks pass** (beta7 int8HQ,
shift 12/3, 8 steps, VSA keep 10, ck attention, match, 768x1344, 243f, seed 51083002, cond = the attached still,
graph prompt == prompt_seg0.txt 10,552 chars, 243 frames / 24 fps / audio / 10.125 s / 3,881,931 B, blackfreeze empty,
1 JOB, no re-queue, render 360.2 s, QNAP size matches). The graph did what I asked. The defect is in what I asked.

## 1. Objective confirmation (no viewing, pixel differencing only)
`runs/terrace_dom_20261028_s51083002/motion_check.py` -> `motion_check.out.txt`: mean |luma diff| per 0.5 s, whole frame /
LEFT half (<Subject 1>, the dominant) / RIGHT half (<Subject 2>, the woman being handled). Noise floor = 2.95.

| t (s) | all | left | right | verdict |
|---|---|---|---|---|
| 0.0-1.0 | 1.7-3.6 | 2.5-4.5 | 0.9-2.6 | both near-static (the opening pose hold) |
| 1.0-3.0 | 6.1-8.7 | 6.3-9.4 | 5.9-8.0 | real motion: cross, pin, slap |
| 3.0-6.5 | 2.4-5.5 | 3.0-8.3 | **1.8-2.6** | **STATIC-RIGHT for 7 of 8 buckets** - the dominant rips, she stands |
| 7.0-10.1 | 2.1-2.5 | 1.9-2.6 | 1.5-2.8 | **LOW-ALL** - the grope (PRIMARY MOTION, 3 s) is nearly frozen |

Thirds: right-half mean 4.58 → 2.10 → 2.05; left-half 5.39 → 5.36 → 2.50. So: her motion dies from 3 s on, and the whole
frame dies from 7 s on. Derek's watch is measured, not impression. Caveat: halves are crude (bodies cross the midline),
and sub-threshold micro-motion (breathing) is invisible at 96x168 - this is a screen, not a verdict.

## 2. What my prompt did (self-check, the cause)
`prompt_seg0.txt` for <Subject 2> literally says: "arms stay down at her sides", "does not lean into any hand",
"does not meet any movement", "knees press together ... do not open", "her hands never touch <Subject 1>",
"shoulders stay squared", "chin stays level", "breath goes short and tight through her nose", "face stays flat".
Nine non-motion instructions for one of two subjects, and the model rendered a statue. I encoded **"not into it" as "no
motion"**. H3 has no way to infer "resistant but alive" from the absence of verbs; a prompt with no verbs for a subject
gets no pixels for that subject. My own prompt is the first suspect and the evidence above fits it exactly.

## 3. How the community handles it (saved corpus, cited)
All paths under `C:\AI\community\notes\web\` (Max's saved community docs) and `notes\` (our own tests).

**a. Reword for motion, and change the seed - the model author's own answer.** `pq1_tenstrip_d68_text.txt:24` (TenStrip,
discussion #68 "Low fps result when continuing a video"): "First I would do is rewording your prompt, and adding
something in the line of **'dynamic video, fluid natural motions' with different seeds**. If that doesn't work, maybe
changing the scheduler settings to **res_multistep** or even **lcm**." Same thread: "There's something causing a **motion
frame rate drop** randomly. I can only assume it's the fasth3 turbo used..." - the author suspects the turbo path itself.
Recorded in our own notes as `prompt_guide_20261023.md:143` (item 18).

**b. Sampler choice is a motion dial.** `agy51_tenstrip_readme.md:33`: "**res_multistep/simple 6-8 steps (my go-to for
best motion quality)**", "Euler/simple 4-8 steps", "SLA sparsity seems to destroy it", "No cache or spectrum if doing
reference". Our KEEP is euler/simple - a legitimate one-axis arm.
`pq1_tenstrip_d47_text.txt:22` (author): "9 should be the maximum ever needed... Some samplers only clean up fast motion
at 6-8 steps, but you will get cooked contrast" - steps buy cleanup/contrast, not motion.

**c. Precision beats brevity; verbs per body part; timecode beats.** `pq1_tenstrip_d45_text.txt:227` (user): "The key to
success really is the correct prompting... I really did **describe every little detail very precisely** (much more so than
I usually do)". The MiniMax official REF guide (S1 = `pq1_minimax_ref_guide_text.txt`, condensed in
`prompt_guide_20261023.md:57-72` and `prompt_guide_20261024.md:43,78`): `detailed_description` is **350-500 words**,
built as "**action onset → continuous development → result, per body part, per contact point, per secondary motion
(hair, fabric, chest/belly, thighs)**", with intra-shot beats written as `At 00:01.200, ...`, camera as a sentence with
**amplitude and speed**, and an **end-state sentence**. A prompt that names a subject's state instead of her verbs
produces a still.

**d. Our own tested rule: one action per 5 s.** `ali163_hc_r1_length_layout_20261023.md:71`: "keep-items named once,
**one action per 5 s**, one camera line, sound line, 60-120 words"; `longvid_readme.md:587` sizes a shot at
"**about 2.2 s per action**". My 10 s cell asked for four actions (cross+pin, slap, two rips, grope) in one chunk with
1,837 words. The measured result: the first two actions land (1-3 s), the rips half-land, the grope dies. The community
answer to a multi-action ask is **a clip per action**, chained with the `<Video 1>` continuation grammar.

**e. Prompt-following is model/beta-dependent, so judge per model.** `prompt_guide_20261023.md` item 20 (discussion #61):
"reference adherence has improved with beta6; 10/3 shift required"; users in `pq1_tenstrip_d61_text.txt:1` report beta6
"struggles to follow my prompts... motion accuracy" vs beta5. TenStrip #64 asks for non-turbo "**better physics** vs
visual quality" - the community explicitly trades turbo speed against motion/physics.

**f. Negative prompts exist as a community tool, not our tool.** `prompt_guide_20261023.md` (item 16): community uses the
ComfyUI **negpip** token-weight node; our stack runs cfg 1 with no NEG branch, and the MiniMax guides never use
prohibition wording. Low-priority arm.

**g. Identity/pose drift is usually the start image, not the words** (item 17, discussions #57/#53) - not this defect,
recorded so the prompt is not blamed for image-side problems.

## 4. Diagnosis
Not a broken graph, not the model dial, not the seed: a **prompt that instructed one subject to do nothing**, plus a
**4-action ask in a single 10 s chunk** against our own one-action-per-5-s rule. Community-consistent fixes, in the order
the evidence supports: prompt reword (a), then scheduler as a measured arm (b), then split the ask into chained clips (d).

## 5. Proposed arms (one variable each, all beta7 KEEP, 243f, 768x1344)
- **A. PROMPT v2, seed 51083002 held** (recommended first; the defect is in the prompt, so this is the isolated axis).
  Rewrite for <Subject 2> with **verbs on every beat** while her face stays flat: head snaps back then she turns it to
  the lens, wipes her cheek with the back of her hand, steps her feet, shoves at <Subject 1>'s shoulder, crosses her
  arms, uncrosses them, presses her lips, breathes with her shoulders, shifts her weight, fingers dig into her own
  thigh, her ribs move. Add the author's phrase "dynamic video, fluid natural motion" + amplitude/speed words; write the
  beats as `At 00:00.000 ... At 00:02.400 ...`; keep secondary motion (hair, fabric, breast, thighs, water); name the
  end state. Two actions in 10 s (slap+rip, then grope), not four.
- **B. SCHEDULER arm**: `res_multistep`/`simple`, 8 steps, everything else held (author's "best motion quality"), on the
  v2 prompt only if A lands - A and B must not move together.
- **C. SPLIT arm**: 5 s (124f) slap+rip, then 5 s continuation (`[video continuation] Continuing seamlessly from
  <Video 1>.`) for the grope. Community-canonical for multi-action asks; costs two renders.
- **D. (later) SEED arm**: 2-3 seeds of the winning arm, since the author ties low-motion to seed luck.
Not proposed: more steps (buys contrast, not motion), VSA loosening (beta7 wants 90% sparsity), negpip (no NEG in our
cfg-1 stack), RIFE (speed lane, not motion).

## 6. Standing rules this produces (for the skills, after an arm proves it - not before)
1. "Not into it" is an **affect** dial, not a motion dial: flat face, busy body. Every subject gets a verb every beat;
   a subject with no verbs renders as furniture.
2. Multi-action asks get **chained clips**, one action per ~5 s; a 10 s chunk carries at most two actions.
3. Add `motion_check.py` to the post-render record for every clip: half-frame motion trace + thirds, so a "she stood
   there" report becomes a number and a next arm.

## 7. UPDATE 14:25 CT - what got run
Derek picked **A + the recommended beta 7 two-pass workflow in one instruction**, so `terrace_dom_v2_20261028_s51083003`
ran A **and** the two-pass graph together - two variables, so rule 1's clean prompt-only arm was NOT tested alone.
Result: render **300.1 s = 1.23 s/frame** (faster than the single-pass control's 1.48 s/frame: pass 1 samples
0.26 MP and pass 2 is only 4 steps), 26-check cell audit all pass, delivered to
`/pi-drop/terrace_dom_v2_20261028_s51083003.mp4` (3,071,104 B).
Motion trace v2: right-half thirds **5.87 / 4.12 / 3.26** at noise floor **4.32** vs the control's
4.58 / 2.10 / 2.05 at floor 2.95. The comparable numbers are ratios to floor: receiver middle third
**0.71x -> 0.95x** (the mid-clip freeze is gone), last third **0.69x -> 0.75x** (the dead grope is only partly
fixed; v2's 8.0-10.0 s band flags LOW-ALL), opening relatively calmer (1.55x -> 1.36x). Caveat: `er_sde` + the
pass-2 CONST re-noise raise the floor, so raw numbers are not comparable and this metric counts pixel noise as motion.
Record: `notes/2026-10-28-terrace-dom-v2-two-pass-DONE.md`.
Next single-variable arms: **C** (chain two 5 s cells) for the ending; **`MiniMaxH3LatentSharpen` 0.15-0.30 alone**
if the picture reads soft; **D** seeds on the winner; **B** only to compare the single-pass line. The three standing
rules above stay out of the skills until an arm is confirmed by Derek's watch.
