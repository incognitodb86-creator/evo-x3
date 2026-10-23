# PW1d SMOKE TEST - one Omni rewrite from the HC3 start still (no render)

- task: REF2AV | resolution 16:9 | duration 10.0 s (node snaps to the 243 f @ 24 fps grid) | greedy | seed 42
- reference: `community/hc/HC3_lesbian_beach.jpg` (the HC3 approved pick, the only reference)
- base: `Qwen2.5-Omni-7B GGUF Q4_K_M · 6.2 GB download · ~9 GB with the adapter and a 12k context`
- adapter: `on disk: MiniMax-H3-Prompt-Rewriter-LoRA-Omni-Q8_0.gguf [qwen2vl, 0.3 GB]`
- options: max_new_tokens 2048, temperature 0.7, top_p 0.8, top_k 20, repetition_penalty 1.05, n_ctx 8192, gpu_layers -1, auto_download **False** (a smoke test must fail, not fetch)
- prompt_id `d0606964-415f-4bbc-ba0f-d68e286bb023` | port 10004 | mode run
- window: 2026-10-23 16:17:23 -> 2026-10-23 16:17:28 CT = 0.1 min GPU
- text output only: no sampler, no DiT, no SaveVideo, no vision judge, no media file (check 9)

## The short prompt that went in

```
Use <Picture 1> for the beach scene and for the two adult women in it. The clip opens on them close and unhurried in the shallow surf at golden hour, the camera low and near, handheld with a slow drift in; warm rim light, wet skin, spray backlit. Adult fictional scene, two women, no one else in frame, the sound is the surf and their breathing.
```

## rewritten_prompt (the six fields the node produced)

```

```

## Fields split out

### subject_definitions

(label not found)

### summary

(label not found)

### retention_analysis

(label not found)

### detailed_description

(label not found)

### overall_soundscape

(label not found)

### non_diegetic_music

(label not found)

## integrated_multimodal_description

```

```

## Objective checks

- FAIL 1 subject_definitions
- FAIL 2 summary
- FAIL 3 retention_analysis
- FAIL 4 detailed_description
- FAIL 5 overall_soundscape
- FAIL 6 non_diegetic_music
- FAIL 7 rewritten_prompt >= 600 chars
- FAIL 8 the 10.0 s answer quotes the 243-frame grid
- PASS 9 no media file written under ComfyUI/output/community
- FAIL 10 writer status completed without error

0/6 checks passed. Media files in the window: none

## What this pass proved (iter 02, 16:15-16:26 CT) - the smoke test ran, the answer did not come back

The job was built, accepted by `/prompt` (HTTP 200, prompt_id d0606964-415f-4bbc-ba0f-d68e286bb023) and executed in 0.19 s.
It failed inside the node:

```
[16:17:23.974] !!! Exception during processing !!! MiniMaxH3PromptWriterOmni.execute() got an unexpected keyword argument 'ref_0'
```

Cause (root, not guesswork): the Omni node declares `references` as one plain `execute()` parameter
(`writer_omni.py:918-930`), and its v3 declaration is `IO.Autogrow(io_type="COMFY_AUTOGROW_V3",
prefix="ref_", min 0, max 12)`. ComfyUI expands a **dict** value for that input into per-slot kwargs, so
`"references": {"ref_0": ["11", 0]}` reaches `execute()` as `ref_0=...` and dies. In an API graph the value
has to be a **list of links**: `"references": [["11", 0]]`, which ComfyUI resolves to `[IMAGE]` and passes as
the `references` parameter the node actually reads (`_refs(references)` iterates it).

Fixed in `notes/ali173_pw1d_run.py` (`build_graph(..., ref_form="list")`, the dict form kept as the fallback
for a 400 that mentions references). The graph has 11 nodes: LoadImage, the options node, the writer, 8
PreviewAny text nodes - nothing that can write media, and check 9 (no mp4/webm/png/wav under
ComfyUI/output/community in the window) passed with 0 files.

Live rows resolved from the running server this pass (the objective of the previous task, now used for real):
- `MiniMaxH3PromptWriterOmni.model` = `Qwen2.5-Omni-7B GGUF Q4_K_M . 6.2 GB download . ~9 GB with the adapter and a 12k context` (the catalog row resolves to the on-disk base+mmproj pair - proof `notes/pw1c_objective.json`)
- `MiniMaxH3RewriterOptions.adapter` = `on disk: MiniMax-H3-Prompt-Rewriter-LoRA-Omni-Q8_0.gguf [qwen2vl, 0.3 GB]`
- `auto_download=False` was set on purpose: a smoke test must fail loudly, never fetch 6.2 GB.

GPU used by this pass: 1.1 min (two wakes 0.5 + 0.6, job 0.19 s), logged in `notes/bakeoff_gpu_ledger.md`;
bakeoff total 2.6 min of the 120 min / 10 job extra. The line stays open as `[!]`.

Next pass (one command, self-contained, gpu_guard IDLE is checked inside, no media node):
```
python C:/AI/community/notes/ali173_pw1d_run.py run     # wake + submit + poll + write the six fields
python C:/AI/community/notes/ali173_pw1d_run.py fetch   # if the answer is not back inside the budget
```
Then copy `notes/pw1_smoke_omni_hc3.md` into `notes/forge_pw1d_smoke.md` if the checks pass and tick the line.
