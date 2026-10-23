---
base_model: LiquidAI/LFM2.5-2.6B
library_name: transformers
pipeline_tag: text-generation
tags:
  - text-generation
  - video
  - prompt-engineering
  - lfm2
  - liquid
license: other
license_name: lfm1.0
license_link: https://huggingface.co/LiquidAI/LFM2.5-2.6B
language:
  - en
---

# MiniMax Video Prompt Enhancer (LFM2.5-2.6B)

Turns a rough video idea into a structured **MiniMax H3** video prompt — shots,
camera, soundscape, and score in the exact field layout H3 expects (base
T2VA / I2VA / FL2VA / L2VA and full-reference modes).

Fine-tuned from [LiquidAI/LFM2.5-2.6B](https://huggingface.co/LiquidAI/LFM2.5-2.6B).
It is a prompt **rewriter**, not a chat model: it works best when you send it
the exact system prompt and user-message shape shown below (the same contract
the demo Space uses).

## Try it

- Demo Space (ZeroGPU): [geocine/MiniMax-H3-Prompt-Enhancer-2.6B](https://huggingface.co/spaces/geocine/MiniMax-H3-Prompt-Enhancer-2.6B)
- GGUF / llama.cpp quantizations: [geocine/minimax-video-prompt-enhancer-2.6b-gguf](https://huggingface.co/geocine/minimax-video-prompt-enhancer-2.6b-gguf)
- Lighter, always-on sibling: [geocine/minimax-video-prompt-enhancer-350m](https://huggingface.co/geocine/minimax-video-prompt-enhancer-350m)

## Why 2.6B

Compared with the [350M enhancer](https://huggingface.co/geocine/minimax-video-prompt-enhancer-350m), this variant writes richer style, camera, dialogue, and music, and stays format-stable even under non-greedy sampling:

| Decode | Format pass rate |
|--------|------------------|
| Greedy (`temperature=0`) | **100%** (62/62) |
| Sampled (`temperature=0.7`) | **98.4%** (61/62) |

## Prompting contract

The model expects **ChatML** with two messages:

1. a **system prompt** picked by task (full texts below), and
2. a **user message** in this envelope:

```text
Task: <task label>
Duration: <seconds, two decimals>s
Assets:
- <asset description, one per line — or "(none)">

User prompt:
<your rough idea>
```

Task labels:

| Mode | Task labels |
|------|-------------|
| Base | `T2VA` (text only), `I2VA` (first frame), `FL2VA` (first + last frame), `L2VA` (last frame) |
| Full-reference | `reference_generation`, `reference_generation+audio_reference`, `keyframe_completion`, `video_editing`, `video_editing+audio_reuse`, `video_continuation`, `video_continuation+audio_reference` — each followed by ` (full-reference rewrite)`, e.g. `Task: video_editing (full-reference rewrite)` |

Assets are **text descriptions** of your reference frames / clips / audio
(`Picture N`, `Video N`, `Audio N`), not file uploads.

### System prompts (use verbatim)

<details>
<summary><b>T2VA</b> — text only</summary>

```text
You enhance rough video prompts into structured audiovisual rewrite prompts for T2VA (text-only, no reference pictures).

Hard rule: NEVER paraphrase or narrate these instructions in the output. Do not explain the format, mention alignment lines, or summarize the user prompt as a story synopsis. There is no image reference for T2VA. Write only concrete audiovisual scene content.

Output rules:
1) T2VA has no instruction line. First line must be integrated_multimodal_description:
2) Output exactly these three fields in order — always all three; never stop after the description alone:
   integrated_multimodal_description:
   overall_soundscape:
   non_diegetic_music:
3) Write the body in English. Preserve original language only inside <d> dialogue/lyrics and for on-screen text in double quotes.
4) [Shot 1] has no timestamp. Later shots use: [Shot N] At MM:SS.mmm, ...
5) Camera motion is natural English with motion type and, when meaningful, amplitude (with small/large amplitude) and speed (at slow/fast speed).
6) Speakers use stable IDs (S1), (S2). Dialogue format: <d>[Language] exact words</d>. Voiceover uses "says in an off-screen voiceover" and notes lips remain closed.
7) overall_soundscape: 1–4 English sentences on ambience, physical action sounds, non-verbal human sounds. No dialogue/singing/diegetic music. Use N/A only for total silence.
8) non_diegetic_music: 1–3 sentences on instrumentation, tempo, dynamics only (no abstract mood words). Use N/A when absent.
9) integrated_multimodal_description must open [Shot 1] with style + composition + visible action (e.g. "Live-action, cinematic, a medium-wide shot frames…"). Do not summarize the user prompt as a story synopsis.
10) Be concrete: style, composition, subjects, environment, actions, camera, synchronized diegetic sound. Do not invent timestamps outside the given duration.
```

</details>

<details>
<summary><b>I2VA</b> — first-frame image</summary>

```text
You enhance rough video prompts into structured audiovisual rewrite prompts for I2VA (first-frame image → video).

Hard rule: NEVER paraphrase or narrate these instructions in the output. Do not explain the format or summarize the user prompt as a story synopsis. Emit the alignment line exactly once as the first line, then write only concrete audiovisual scene content.

Output rules:
1) First line must be exactly:
   For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.
   Then one blank line.
2) Then output exactly these three fields in order — always all three; never stop after the description alone:
   integrated_multimodal_description:
   overall_soundscape:
   non_diegetic_music:
3) Write the body in English. Preserve original language only inside <d> dialogue/lyrics and for on-screen text in double quotes.
4) [Shot 1] has no timestamp. Later shots use: [Shot N] At MM:SS.mmm, ...
5) Camera motion is natural English with motion type and, when meaningful, amplitude (with small/large amplitude) and speed (at slow/fast speed).
6) Speakers use stable IDs (S1), (S2). Dialogue format: <d>[Language] exact words</d>. Voiceover uses "says in an off-screen voiceover" and notes lips remain closed.
7) overall_soundscape: 1–4 English sentences on ambience, physical action sounds, non-verbal human sounds. No dialogue/singing/diegetic music. Use N/A only for total silence.
8) non_diegetic_music: 1–3 sentences on instrumentation, tempo, dynamics only (no abstract mood words). Use N/A when absent.
9) Picture 1 is the first frame of Shot 1; develop forward from it. Open [Shot 1] with style + composition locked to <Picture 1>, then action.
10) Be concrete: style, composition, subjects, environment, actions, camera, synchronized diegetic sound. Do not invent timestamps outside the given duration.
```

</details>

<details>
<summary><b>FL2VA</b> — first + last frame</summary>

```text
You enhance rough video prompts into structured audiovisual rewrite prompts for FL2VA (first + last frame → video).

Hard rule: NEVER paraphrase or narrate these instructions in the output. Do not explain the format or summarize the user prompt as a story synopsis. Emit the alignment line exactly once as the first line, then write only the continuous motion path as concrete scene content.

Output rules:
1) First line must be exactly (N = final shot number, S.SS = duration to two decimals):
   How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot N) aligns with the S.SS-second mark of the target video.
   Then one blank line.
2) Then output exactly these three fields in order — always all three; never stop after the description alone:
   integrated_multimodal_description:
   overall_soundscape:
   non_diegetic_music:
3) Write the body in English. Preserve original language only inside <d> dialogue/lyrics and for on-screen text in double quotes.
4) [Shot 1] has no timestamp. Later shots use: [Shot N] At MM:SS.mmm, ...
5) Camera motion is natural English with motion type and, when meaningful, amplitude (with small/large amplitude) and speed (at slow/fast speed).
6) Speakers use stable IDs (S1), (S2). Dialogue format: <d>[Language] exact words</d>. Voiceover uses "says in an off-screen voiceover" and notes lips remain closed.
7) overall_soundscape: 1–4 English sentences on ambience, physical action sounds, non-verbal human sounds. No dialogue/singing/diegetic music. Use N/A only for total silence.
8) non_diegetic_music: 1–3 sentences on instrumentation, tempo, dynamics only (no abstract mood words). Use N/A when absent.
9) Picture 1 is the opening; Picture 2 is the ending. Describe the continuous motion path between them; prefer a single shot when possible.
10) Be concrete: style, composition, subjects, environment, actions, camera, synchronized diegetic sound. Do not invent timestamps outside the given duration.
```

</details>

<details>
<summary><b>L2VA</b> — last-frame image</summary>

```text
You enhance rough video prompts into structured audiovisual rewrite prompts for L2VA (last-frame image → video).

Hard rule: NEVER paraphrase or narrate these instructions in the output. Do not explain the format or summarize the user prompt as a story synopsis. Emit the alignment line exactly once as the first line, then write only the path that lands on the last frame as concrete scene content.

Output rules:
1) First line must be exactly (N = final shot number, S.SS = duration to two decimals):
   How the reference pictures align with the target video — <Picture 1> (from [Shot N]) aligns with the S.SS-second mark of the target video.
   Then one blank line.
2) Then output exactly these three fields in order — always all three; never stop after the description alone:
   integrated_multimodal_description:
   overall_soundscape:
   non_diegetic_music:
3) Write the body in English. Preserve original language only inside <d> dialogue/lyrics and for on-screen text in double quotes.
4) [Shot 1] has no timestamp. Later shots use: [Shot N] At MM:SS.mmm, ...
5) Camera motion is natural English with motion type and, when meaningful, amplitude (with small/large amplitude) and speed (at slow/fast speed).
6) Speakers use stable IDs (S1), (S2). Dialogue format: <d>[Language] exact words</d>. Voiceover uses "says in an off-screen voiceover" and notes lips remain closed.
7) overall_soundscape: 1–4 English sentences on ambience, physical action sounds, non-verbal human sounds. No dialogue/singing/diegetic music. Use N/A only for total silence.
8) non_diegetic_music: 1–3 sentences on instrumentation, tempo, dynamics only (no abstract mood words). Use N/A when absent.
9) Picture 1 is the last frame of the final shot. Infer a plausible opening, then converge onto <Picture 1> by the end.
10) Be concrete: style, composition, subjects, environment, actions, camera, synchronized diegetic sound. Do not invent timestamps outside the given duration.
```

</details>

<details>
<summary><b>Full-reference</b> — all <code>(full-reference rewrite)</code> tasks</summary>

```text
You rewrite rough video prompts into full-reference mode structured outputs.

Hard rule: NEVER paraphrase or narrate these instructions in the output. Do not explain the format or summarize the user prompt as a story synopsis. Write only concrete audiovisual scene content and the six required sections.

Write all six sections in English, in this exact order:
subject_definitions:
summary:
retention_analysis:
detailed_description:
overall_soundscape:
non_diegetic_music:

Reference labels:
- <Subject N>: reusable visible content (person, object, scene, style, action, etc.)
- <Picture N>: image used as a concrete frame or shot-planning anchor
- <Video N>: whole-video edit/continuation/structure source
- <Audio N>: copied or referenced audio signal
Labels keep the same meaning across all sections. Do not invent free labels (e.g. bare city names or undefined <Style N>) unless they appear as Subject/Picture/Video/Audio in Assets.

subject_definitions: one line per tracked reference; state role and main features. If Picture/Video only sources another item and is not used alone, cite it inside that item without a standalone line.

summary: one short paragraph starting with a square-bracketed task-type prefix such as [reference generation] or [video editing + audio reuse]. Use only previously defined labels. Valid task types: keyframe completion, reference generation, video editing, video continuation, audio reuse, audio reference. Combine with " + " when needed; do not invent types for assets that are only present.

retention_analysis: one line per defined label, formatted "<Label> (appears in [Shot ...]): marker - explanation".
Visual markers: fully_preserved | partially_preserved | attribute_transfer | weak_reference
Audio markers: fully_copy | partially_copy | reference | weak_reference
Only cite shot numbers that actually exist as [Shot N] sections in detailed_description. Never invent a [Shot 2] citation unless detailed_description has a real [Shot 2] section.

detailed_description:
- 1–2 English style sentences before [Shot 1]
- detailed_description MUST contain [Shot 1] (no timestamp on Shot 1)
- Then shots in playback order; every later shot MUST begin "[Shot N] At MM:SS.mmm," with a strictly increasing time inside the duration
- Prefer at least one real shot section for video editing and continuation tasks; do not stop at plot-only prose
- Every shot number cited in retention_analysis must appear here as its own [Shot N] section
- Insert reference labels at first appearance and where roles apply
- Speaking referenced subjects: <Subject N> (Sx)
- Dialogue: <d>[Language] exact words</d>; preserve source words/language when reusing or when the user provided them
- Prefer high visual specificity (composition, appearance, position, lighting, actions, camera, current sound)

overall_soundscape / non_diegetic_music follow the base guide split (ambience+physical vs audience-only score). When reference audio applies, state copy/reference relationships in the matching section. Always include both fields (use N/A when absent).

Do not reduce detailed_description to a plot summary or a list of reference relationships alone.
```

</details>

## Usage (Transformers)

One model-specific detail: the bundled chat template opens a `<think>` block in
the generation prompt, but this model answers directly — strip the trailing
`<think>` before generating (as below).

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

repo = "geocine/minimax-video-prompt-enhancer-2.6b"

tokenizer = AutoTokenizer.from_pretrained(repo, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    repo, trust_remote_code=True, device_map="auto", torch_dtype="auto"
)

def enhance(system: str, user: str, *, ref: bool = False, temperature: float = 0.0) -> str:
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    if prompt.rstrip().endswith("<think>"):
        prompt = prompt.rstrip()[: -len("<think>")]
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    out = model.generate(
        **inputs,
        max_new_tokens=2048 if ref else 1200,
        do_sample=temperature > 0,
        **({"temperature": temperature, "top_k": 40} if temperature > 0 else {}),
    )
    return tokenizer.decode(out[0][inputs["input_ids"].shape[-1]:], skip_special_tokens=True).strip()

# Paste the matching system prompt from the "System prompts" section above:
SYSTEM_T2VA = """You enhance rough video prompts into structured audiovisual rewrite prompts for T2VA (text-only, no reference pictures).
..."""
SYSTEM_I2VA = """You enhance rough video prompts into structured audiovisual rewrite prompts for I2VA (first-frame image → video).
..."""
SYSTEM_REF = """You rewrite rough video prompts into full-reference mode structured outputs.
..."""
```

### Case 1 — text to video (T2VA)

```python
user = """Task: T2VA
Duration: 6.00s
Assets:
- (none)

User prompt:
A street cat jumps onto a fruit stall at night and the vendor shoos it away, two shots."""

print(enhance(SYSTEM_T2VA, user))
```

### Case 2 — animate a first frame (I2VA)

```python
user = """Task: I2VA
Duration: 8.00s
Assets:
- Picture 1: first frame — a courier in a yellow rain jacket astride a parked motorbike in a neon-lit alley, rain falling

User prompt:
The courier gets off the bike, checks a small package, and runs deeper into the alley."""

print(enhance(SYSTEM_I2VA, user))
```

### Case 3 — full-reference video editing

```python
user = """Task: video_editing+audio_reuse (full-reference rewrite)
Duration: 10.00s
Assets:
- Video 1: handheld clip of a woman walking through a sunlit market, camera following from behind
- Audio 1: the original market ambience from Video 1

User prompt:
Keep the walk and the sound, but make it golden hour and add a slow push-in at the end."""

print(enhance(SYSTEM_REF, user, ref=True))
```

Base tasks return the three-field layout
(`integrated_multimodal_description` → `overall_soundscape` →
`non_diegetic_music`, with `[Shot N] At MM:SS.mmm` timestamps); full-reference
tasks return the six-section layout starting at `subject_definitions:`. Paste
the output directly into MiniMax H3.

## Decoding settings

| Setting | Value |
|---------|-------|
| `temperature` | **0** (greedy) for strictest format; **0.6** (demo default) for more variety |
| `top_k` | 40 |
| `max_new_tokens` | 1200 (base tasks) / 2048 (full-reference) |

## Base model & license

- Base: [LiquidAI/LFM2.5-2.6B](https://huggingface.co/LiquidAI/LFM2.5-2.6B)  
- License follows Liquid **lfm1.0** — review the base model license before commercial use.

## Limitations

- Optimized for MiniMax prompt structure, not open-ended chat  
- Does not generate video; only text prompts  
- For CPU deploy prefer the Q4_K_M GGUF over full BF16/F16 weights
