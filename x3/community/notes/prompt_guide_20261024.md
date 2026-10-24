# prompt_guide_20261024.md - community H3 prompt guide for Forge (PQ1 / fix_plan 3.1)

Last Updated: 2026-10-24 (written by Antigravity, brief agy_setup_20261024, item 5). No render, no GPU.
Supersedes nothing: it condenses `notes/prompt_guide_20261023.md` (283 lines, 20 findings, the 14-prompt audit)
into the answer to three questions: how long, what sections, what examples. The longer file stays as the evidence.

## Date
2026-10-24

## Summary
Every community source says the same thing: write the **official MiniMax six-section Ref2VA format**, make
`detailed_description` **350-500 English words**, describe only what is visible/audible, and spend the extra
length on per-shot detail, not on quality words or negations. Our shipped prompts are 275-498 words, so most
were below the floor, and none uses beat timestamps, canon camera wording, or the continuation label.

## Key Findings

### Sources (each fetched once on 2026-10-24; `ok` = HTTP 200; saved under `C:/AI/community/notes/web/`)
| # | Source | URL | Saved as | Result |
|---|---|---|---|---|
| 1 | MiniMax-H3 full-reference (Ref2VA) guide, official | https://huggingface.co/MiniMaxAI/MiniMax-H3/resolve/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md | `agy51_ref_guide.md` | ok, 23,553 B, same size as the 2026-10-23 save |
| 2 | MiniMax-H3 base guide (T2VA/I2VA/FL2VA/L2VA), official | https://huggingface.co/MiniMaxAI/MiniMax-H3/resolve/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md | `agy51_base_guide.md` | ok, 15,773 B, same size |
| 3 | MiniMax-AI/MiniMax-H3 GitHub repo (ships the `h3-prompt-writing` skill with `references/base-en.txt` and `ref-en.txt`) | https://github.com/MiniMax-AI/MiniMax-H3 | `agy51_gh_minimax_h3.html` | ok; README says `npx skills add https://github.com/MiniMax-AI/MiniMax-H3 --skill h3-prompt-writing`; the two guides are the same documents as 1-2 |
| 4 | TenStrip/10Eros-Max model card | https://huggingface.co/TenStrip/10Eros-Max/raw/HEAD/README.md | `agy51_tenstrip_readme.md` | ok, 3,698 B, same size; card API `agy51_tenstrip_card.json` shows 870 likes, last modified 2026-10-13 |
| 5 | TenStrip `h3_graft_methodology.md` | https://huggingface.co/TenStrip/10Eros-Max/raw/HEAD/h3_graft_methodology.md | `agy51_graft_method.md` | ok, 24,858 B; model-building doc, no prompt rules read from it |
| 6 | TenStrip HF discussion list | https://huggingface.co/api/models/TenStrip/10Eros-Max/discussions | `agy51_tenstrip_disc.json` | ok, 69 discussions, identical to the 2026-10-23 save (50 on page 1); prompt threads = #35, #45, #49, #50, #52, #63, #68 (text already extracted in `pq1_tenstrip_d*_text.txt`) |
| - | Reddit | - | - | blocked 403 on 2026-10-23 (`pq1_reddit_*_403.txt`); not retried |

Nothing changed upstream since the 2026-10-23 pass, so the per-thread pages were not fetched again.

### How long
| Part | Length | Source |
|---|---|---|
| `detailed_description` (generation tasks) | **350-500 English words**; dialogue-dense clips fit the spoken timeline first; "a single shot does not automatically justify a shorter description" | source 1 section 5.2 |
| `overall_soundscape` | 1-4 sentences, one paragraph; `N/A` only for requested total silence | source 2 section 4.6 |
| `non_diegetic_music` | 1-3 sentences (instruments, tempo, dynamics, no mood words); `N/A` when none | source 2 section 4.7 |
| `summary` | one short paragraph with a `[task type]` prefix | source 1 section 3 |
| `subject_definitions` / `retention_analysis` | one line per label | source 1 sections 2, 4 |
| Community report | ~300 words for a 15 s clip was already reported as workable | HF discussion #50 (`pq1_tenstrip_d50_text.txt`) |
| Ours (audit 2026-10-23) | c0 275-435 words, c1 345-498; 5 of 7 c0 prompts below 350 | `prompt_guide_20261023.md` section 3 |

Rule for Forge: c0 and c1 `detailed_description` = 350-500 words each; the whole prompt lands near 550-800 words.
Detail is added by shot and body part/contact point/secondary motion, never by "8k, masterpiece" words.

### What sections (official order, English, source 1 section 1)
1. `subject_definitions` - one line per `<Subject N>` / `<Picture N>` / `<Video N>` / `<Audio N>`; identity-only crops are cited inside the subject line, not given their own `<Picture N>` line.
2. `summary` - starts `[reference generation]` (or `[video continuation + reference generation]` for c1; `[keyframe completion]` when a picture is a concrete frame).
3. `retention_analysis` - one line per label with `fully_preserved | partially_preserved | attribute_transfer | weak_reference` (audio: `fully_copy | partially_copy | reference | weak_reference`).
4. `detailed_description` - style sentence(s) before `[Shot 1]`; `[Shot 1]` has no timestamp; later shots `[Shot N] At MM:SS.mmm, the camera cuts to ...`; a cut must add new information, otherwise use camera motion.
5. `overall_soundscape` - ambience + physical action sound + non-verbal human sound; dialogue stays in the description inside `<d>[English] ...</d>`.
6. `non_diegetic_music` - audience-only score or `N/A`.

Format rules that decide whether the model follows the prompt: TenStrip says the model "is heavily trained on ref2va prompts and if you do not give it the correct prompt structure it does not follow the format well" and a community user in the same thread reads "ignores my prompt" as "prompt written so poorly it can't be tokenized" (#45, user stphnvdb; owner answers: #49 "FL2VA for beta4 and earlier, ref2va for beta5"; #50 "I would use ref prompting for everything"). Camera = canon type + `with small/large amplitude` + `at slow/fast speed`, written as a natural sentence (source 2 section 4.3). No negation prose: the official guides never use prohibition wording, and the one community route for negation is a NegPip token-weight node (https://github.com/gas/comfyui-minimax-h3-negpip, named in HF discussion #52, `pq1_tenstrip_d52_text.txt:3`). The 2026-10-23 guide's claim that the model has "embedded NegPip guidance" cites card lines 77-78 that do not exist in the saved 63-line card (`agy51_tenstrip_readme.md`), so it is unverified and not repeated here.

### Examples
Official, copy-paste ready (full texts in the saved sources):
- Full Ref2VA example, 3 shots, all six sections: source 1 section 7 (`agy51_ref_guide.md` lines 305-341).
- T2VA / I2VA / FL2VA / L2VA examples: source 2 section 5 (`agy51_base_guide.md` lines 168-222).
- Camera sentence: "The camera pushes in with small amplitude at slow speed toward the folded letter in her hands." (source 2 section 4.3).

Skeleton for one Forge c0 clip (fictional adults, non-explicit placeholders in `[]`; fill every bracket with visible detail until the description reaches 350-500 words):
```text
subject_definitions:
<Subject 1> is the woman in <Picture 1> and <Picture 2>: [face, hair, skin, body build, marks, wardrobe as seen].
<Subject 2> is the woman in <Picture 1> and <Picture 3>: [same pattern].
<Picture 1> is the first frame of [Shot 1] and the scene anchor: [framing, room, light, colour cast, depth of field].

summary:
[reference generation] [one sentence: who does what in one shot, plus the preserved anchors: room, light, camera, wardrobe state].

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - [named visible details].
<Subject 2> (appears in [Shot 1]): fully_preserved - [named visible details].
<Picture 1> ([Shot 1] first frame): fully_preserved - [framing, room, light, lens character].

detailed_description:
The target video is in a [style] style with [lighting] and [palette].
[Shot 1] [framing and composition], <Picture 1> as the first frame. [action onset -> development -> result, by body part and contact point, with hair/fabric secondary motion, At 00:01.200 / 00:02.600 / 00:04.100 beats]. The camera [canon move] with small amplitude at slow speed. The shot ends with [named end state].

overall_soundscape:
[room tone/ventilation hum]. [physical contact and fabric sounds]. [breath and non-verbal vocal sounds].

non_diegetic_music:
N/A
```
The 12 verbatim prompts built from this skeleton are in `notes/im1_prompts.md`.

## Action Items
1. Rewrite c0/c1 prompts to 350-500 words per `detailed_description` with `At MM:SS.mmm` beats and canon camera wording (14 of 14 shipped prompts have 0 beats).
2. Add `summary:` and `retention_analysis:` plus a `<Video 1>` continuation line to every c1 prompt (the six shipped c1 files have neither).
3. Keep the full-body start photo as `<Picture 1>`; cite face crops inside `<Subject N>` only (the r3-r6 crop-only wording coincided with the body/limb defects).
4. Move negation out of prose; describe the ambience layer in `overall_soundscape`.
5. Leave steps, sampler, shift, LoRA and start-image fixes to 3.8 (IM1) and 3.2-3.5; they are settings, not prompt text.
6. Fix_plan 3.1 stays open until Forge writes and renders prompts to this length; this note is its research deliverable.
