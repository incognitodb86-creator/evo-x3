# Community Qwen 3.8 H3 prompt vs Render (report only, nothing edited)

Snapshot: /workspace/shared/render-prompt-snapshot-20261117/ (all 30 non-archive files read, README.md included; the 12 `_archive/*.bak` files are older copies of current files, diffed only, not used as evidence).
Short names: **AG** = render/AGENTS.md, **WP** = render/writer_pipeline/writer_prompt.md, **CFG** = writer_pipeline/config.yaml, **RED** = reddit-qwen38-h3-system-prompt.md. Skills are under community/skills/. Citations read `file § heading (line)`.

## 0. How to read the Reddit post
- The only Qwen 3.8 claim in RED is its title: "qwen 3.8 is out and it writes awesome minimax prompts a lot better than 3.6 (same system prompt)". The scraped text has no samples, sampler settings, thinking mode, length data or A/B numbers. Everything below about Qwen 3.8 *behaviour* is therefore unverified.
- The title says the **same prompt** worked better on a newer model. It is not evidence that shorter or simpler prompts work better.
- RED targets stock MiniMax H3 with the Contex Loop workflows. Render targets 10Eros-Max beta7 on the locked 4bc9bba parody graph. RED contains no adult-content writing, and it names "Qwen 3.8", not the Flash-Next uncensored variant. All transfer to Render is untested.
- The writer model only sees WP, the pinned persona and the beat card. WP is compiled from AG's craft sections (WP § header L2: "Compiled from the craft sections of the Render instruction file by wp_compile_prompt.py"). AG PIPELINE/NEVER/STEPS and all skills do not reach the writer. Any new writer rule must therefore go into **AG** and then be recompiled into WP; hand-editing WP only is overwritten.
- Not in the snapshot, so not audited: render_writer_pipeline.py, wp_compile_prompt.py, the beat-card prompt, the judge prompt, the lint code.

## 1. What RED has that Render lacks or contradicts (ranked)
Overall: Render is far denser than RED and already covers most of it. **There is no High item.** Four small additions are worth taking, plus a larger set of conflicts to skip (section 4).

| # | Gain | RED says | Render today | Verdict |
|---|------|----------|--------------|---------|
| 1 | MED | "Use only reference tags that are genuinely available in the workflow ... Never invent unavailable reference tags." | The writer paragraph gets no label whitelist. WP § SHAPE (L126-127) only shows `<Subject 1>`/(S1)/(S2). `<Picture` appears once, in the Partners bullet (WP L38). Unwired labels are an error elsewhere (h3-max-ref2va-prompt § R33 L90-92, § R42 L168-170, gate item 1 L192). | Gap. A new model could invent `<Picture 2>`, `<Video 1>` or `<Audio 2>`. |
| 2 | MED | "Before answering, silently verify: all reference tags exist; ... dialogue exact or explicitly absent; ..." as the final block | WP § BEFORE YOU WRITE (L144-153) is the last block but never says "silently" and carries no first-character contract. WP § OUTPUT (L139-142) says "No header, no Markdown, no notes", but AG § STEPS 3 (L17) ships writer text "verbatim without rewriting or stripping". | Partial gap. Any preamble or self-review leaks into prompt.txt. |
| 3 | LOW | "Do not request readable text, subtitles, logos, watermarks, UI, or exact typography." | No such rule in AG or WP. Visible text is covered only for REF2VA, as quote-it-verbatim (h3-max-ref2va-prompt § R38 L146-149). | Gap, but the harm on H3 is unmeasured. Must be phrased positively (wording.md § R24 L5-8). |
| 4 | LOW | "For dialogue, comedy, greetings, direct-to-camera performance, or character acting: prefer one continuous shot." | AG § CAMERA AND TIME (L57): "one continuous [Shot 1], or 2-3 cuts ... neither is forced"; CFG `shots_default: single`. The talk-only bullet (AG § PACING L78, WP L69) says nothing about shots. | Small gap for `--position talk` clips. |
| 5 | LOW | "Avoid overlapping speech unless specifically requested." | AG § DIALOGUE AND SOUND has sequential examples and "finish a spoken line inside one shot" (AG § CAMERA AND TIME L60). Nothing explicit on overlap. | Tiny gap. |
| 6 | LOW | "Be explicit. Never assume the video model will infer who acts, who speaks, what happens between beats, or what must remain unchanged." | Covered piecemeal: AG § BEFORE YOU WRITE L186-188 (garments, labels/places/roles, final states), AG § PACING L77 (position change). | Already covered. No change. |

## 2. Ready-to-paste text
Convention: AG is the writer-run owner, its rules carry no R-numbers, and it feeds WP. h3-prompting's one-rule-one-file principle (SKILL § 0 L12-16, § 9 L212) is respected: each rule below goes in AG only and is not restated in a skill. If Max wants any of them cross-lane instead, the next free box-unique number is **R45** (highest in use is R44 in h3-max-ref2va-prompt; h3-prompting § 9 L212: "gets the next box-unique number; never renumber"). Cross-lane would add it to references/wording.md § 4, but then the writer would not see it. After editing AG: recompile WP and update CFG `writer_prompt_sha256`.

**Item 1: label whitelist (MED).** Target: AG § CRAFT RULES, new bullet after "Bodies:" (L44). WP compiles it into § CRAFT RULES after L36.
```
- Labels: the paragraph uses only <Subject 1>, <Subject 2>, <Subject 3>, (S1), (S2), (S3) and a <Picture N> that the beat card lists. <Audio N>, <Video N> and any other tag stay out of the paragraph; the pipeline writes them in the headers.
```

**Item 2: silent check and first character (MED).** Target: AG § BEFORE YOU WRITE heading (L179), compiled to WP L144. Replace the heading line with:
```
BEFORE YOU WRITE (run this list silently; the first character you output is the "[" of [Shot 1], and no preamble, notes or self-review follow it)
```
Optional tidy in the same recompile: AG § PRE-FLIGHT heading (L131, WP L132) says "(check silently before running the command)", which addresses the pi agent, not the writer. Compile it out of WP or reword to "(check silently)".

**Item 3: lettering, logos, watermarks (LOW).** Target: AG § CRAFT RULES, directly after the "Every quality word needs a noun" bullet (L25).
```
- Write signs, screens, labels and garments as plain colour and material (a plain grey T-shirt, a dim TV glow, a blank notice board). Lettering, logos, subtitles and watermarks stay out of the frame.
```
Reddit-only claim; no H3 measurement exists in the snapshot.

**Item 4: talk and direct-to-camera clips (LOW).** Target: AG § PACING, append to the talk-only bullet (L78), compiled to WP L69.
```
 The clip is one continuous [Shot 1]; a second angle is one slow push-in written in prose.
```

**Item 5: no overlapping speech (LOW).** Target: AG § DIALOGUE AND SOUND, after the "Cadence:" bullet (L124).
```
- Lines run one after another: each speaker finishes before the next begins, unless the ask names simultaneous speech.
```

## 3. Render rules that may conflict with Qwen 3.8 behaviour
None of these is shown to fail on Qwen 3.8. RED is silent on each, so every row is a **check to run**, not a finding about the model.

1. **Thinking and reasoning leakage (check first).** CFG L7: `thinking: false  # chat_template_kwargs.enable_thinking (Gemma thinking is on/off only)`. The comment is Gemma-era. AG § STEPS 3 (L17): "the writer text ships verbatim without rewriting or stripping". Hard stops are only 18+, empty/refused output, and missing files. If the flash-next server ignores `enable_thinking`, or returns `<think>` text or reasoning in `content`, it ships into prompt.txt. If thinking tokens are counted, CFG `prose_max_tokens: 1100` can truncate or empty the answer. Test: run 3 clips and grep writer_output.txt for `<think`, a leading non-`[` character, and truncation.
2. **WP is stale against AG, so the Qwen writer gets an older rule set.** CFG L10 `writer_prompt_sha256: 7a9479b5...` does not match the snapshot's WP (`997e1048...`), and WP header L2 source sha `d9a4d956...` does not match AG (`6c5b4012...`). Lines in AG that are missing from or different in WP:
   - AG L7 "When the ask specifies a different setting, wardrobe or lines, the ask beats the still" vs WP L7 "the still is a locked setup ... You never contradict them". Same for AG L42 and L45. The pinned persona (personas/current.md L2) repeats the WP wording.
   - AG L78 talk-only "at least three spoken lines, a hard minimum ... Keep every quoted <d> line from the ask verbatim" vs WP L69 "aim for 1-5 short spoken lines".
   - AG L81 spoof "pair the character and actor via the parody identity path" vs WP L72 "original adult characters ... with no named celebrity or character". This does not reopen the parody decision; it is a stale sentence that contradicts AG and the owner decision.
   - AG L32 "PRIMARY MOTION contains one tempo word" vs WP L24 "works best with a clear tempo phrase". Minor: AG L35 "explicit join wording" vs WP L27 "clear spatial join wording".
   - AG § EXAMPLES (L175-177, about 300 and 284 words) are not compiled into WP, so the writer sees zero few-shot examples.
   A more literal-following model will follow the stale WP lines more strictly than Gemma did. This predates Qwen but now matters. Recompile before judging Qwen output.
3. **Length lint vs the length rules.** CFG `lint: words_min 90, words_max 190` vs h3-prompting § R9 (L88): "no word cap ... no word floor or quota"; h3-max-ref2va-prompt § R41 L163-166 (upstream 350-500 words is a writer style target, "not a model limit"); AG § CRAFT RULES L26 "as much ... detail as the beat needs"; AG's own examples at about 284-300 words. The lint is advisory (CFG `min_ready_score` "reported only"; AG § STEPS 3), but if Qwen 3.8 writes longer or shorter than Gemma, warnings and tie-break scores shift. Nothing in RED gives a Qwen length figure.
4. **Sampler arm A was chosen for Gemma.** CFG: `sampler_arm: A  # FROZEN: setup A/B 2026-11-13 ... lint pass 7/10 vs 5/10`, "never re-tuned automatically", temperature 1.0, top_p 0.95, top_k 64, min_p 0.10. RED gives no Qwen sampler. The `judge_sampler` note ("temperature <= 0 falls back to the server default 1.0") describes the PolyStrata server; confirm it still holds for flash-next. CFG L6 comment still describes Gemma 4 26B as the model behind alias `flash-next-uncensored`. AG § PIPELINE (L157, L159) and h3-prompting § Sibling (L219) also still say Gemma.
5. **Output contract mismatch across files.** WP § OUTPUT L140: paragraph "starts with [Shot 1]". h3-prompting § R1 (L31): "very first emitted token must be `subject_definitions:`". AG § STEPS 4 (L18) says the pipeline writes the headers. The writer only sees WP, so this is safe unless h3-prompting reaches the writer (h3-prompting § 3-4 L137, L141 say its references are "already loaded in writer context"). Confirm which is true. If both reach the writer, Qwen gets two first-token rules.
6. **Strict format is asserted for Qwen by RED only.** RED: "OUTPUT RULES FOR CONTEX LOOP: strict valid JSON only (no fences, no trailing commas ...)". Render asks for plain text with "zero Markdown" (AG § PERSONA L11; WP § OUTPUT). Beat-card JSON (CFG `beat_card_sampler`, `beat_card_max_tokens 1400`) cannot be audited: its prompt is not in the snapshot.
7. **Suggested A/B (uses the existing harness, CFG header comment `acceptance\sampler_ab.json`).** Arm 1: current WP as is. Arm 2: WP recompiled from AG (fixes item 2 above). Arm 3: arm 2 plus Items 1-5. Same 10 stills and asks. Compare lint pass rate and Derrick's picks. This measures the community claim; the post does not.

## 4. Skip list
| RED item (quoted) | Why skip |
|---|---|
| "If there is no dialogue, explicitly write: "No spoken dialogue. Characters communicate through facial expressions and gestures."" | Contradicts Render's own measured rule. longclip-beat-sheet.md § Required Beat Sheet Fields (`ambient_sfx`): "Never put "No speech" here (negations condition TTS/audio)"; § Compilation Contract 1: silent clips omit (S1) and `<d>` entirely. h3-prompting § Oral, riding and sex sound (L83): "never write `no speech`". Also breaks wording.md § R24 (positives only). |
| "For clips without music, write: non_diegetic_music: N/A" and the `Audio:` section ("Ambience, Foley, music, impacts") | Contradicts h3-prompting § R7 (L62-72): TenStrip HF #77 says labelled audio sections cause cartoon audio. h3-max-ref2va-prompt § R32 (L65-74) explains they come from the hosted H3-Context-IR, which the local H3-Base does not use. WP § OUTPUT L142 forbids those headers. |
| "Storyboard: [0s-Xs] [Explicit action beat.] [Xs-Xs] ..." | Contradicts h3-prompting § R8 (L86): `[Shot 1]` gets no timestamp; beats use phase words ("at first", "as it builds", "by the end"). AG § PACING L74 enforces the four phase words. |
| "For action, trailers, fights, chases, and product films: up to 3-4 clear shots in a 6-7 second clip." | Conflicts with AG § CAMERA AND TIME L57-58 (a cut must add information; slight tightening is a push-in) and CFG `shots_default: single`. |
| "Visual style: [Rendering style, lighting, environment, materials, lens/look, mood.]" as the first field | A style opener exists only as h3-max-ref2va-prompt § R39 (REF2VA lane). Named-parody format takes precedence (h3-prompting § Named-parody precedence L8-10). Render's camera sentence plus light sentence (AG § CAMERA AND TIME L62-63) covers it. |
| "Scene overview" / "Consistency:" fields, "Character Name says clearly: "Exact dialogue."" | Different tested formats: retention_analysis is pipeline-filled (AG § RETENTION L139); speech form is `(S1) says in a <voice> voice, <d>[English] ...</d>` (AG § DIALOGUE AND SOUND L123). |
| "Use positive desired constraints." / "Keep each shot physically plausible, readable, and focused." / "Do not overload a short clip ..." | Already in Render: wording.md § R24, AG § PACING L69 ("One beat per clip"), AG § CRAFT RULES "Bodies:" L44, AG § PACING L68-77. |
| "Keep dialogue short for 5-7 second clips." / "Generated dialogue must always be exact and short." | Already stricter in Render: AG § PACING L72 (at most 2.5 words per second of T), L73; AG § BEFORE YOU WRITE L184 (25 words or fewer); CFG `lint.speech_words_max: 25`. |
| "When a reference is available, state exactly what it controls ..." / "Preserve signature features ..." | Already covered by AG § SHAPE L143-149 and § RETENTION L139. |
| Contex Loop block: "prompt_prefix", "15 s per scene", "context_length 22", `anchor_mode "head"`, "960x544", "4 scenes", "20 steps", seeds, `run_name`, JSON-only output | Out of scope (lane is locked to 4bc9bba single-pass 768x1344). One-line notes only: "Each scene prompt contains only what changes." is what the builder does with shared subject definitions (h3-max-ref2va-prompt references/chain-lane.md § Chain lane). "End with a visible unfinished action" is h3-prompting references/motion-contact-anatomy.md § R17 (L16-19) and AG § BEFORE YOU WRITE L186. 15 s scenes exceed the 243f cap on 16 GB (h3-parody-identity-reference § 0.1 L15-23). |
