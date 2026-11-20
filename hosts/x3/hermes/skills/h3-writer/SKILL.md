---
name: h3-writer
description: "Use when Derrick wants a MiniMax-H3 video prompt written in this chat ('write it yourself', 'community way', 'path B', or the default slim render path): write the Beta 7 prompt yourself, save it, and hand it to the h3-render lint/build/queue gate. Do not call Python writer or judge scripts."
version: 2.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [render, h3, writing]
    category: creative
---

# H3 writer (you write the prompt)

You write the MiniMax-H3 prompt. Do not call `render_writer_pipeline.py`, a writer model, or a judge model.

1. Load `h3-prompting` for Beta 7 format. Load `h3-parody-identity` only for a named parody.
2. Everyone depicted is 18+. If the ask or still has a youth cue, stop and report it. Write only the prompt text: no preamble, no code fence, no notes.
3. Use exactly these four headers, once each, in this order:
   - `subject_definitions:`
   - `summary:`
   - `retention_analysis:`
   - `detailed_description:`
   No pre-U56 headers and no Markdown in the body. Put diegetic sound in ordinary sentences at the end of `detailed_description`.
4. Save the prompt to both `<run_dir>/hermes_prose.txt` and `<run_dir>/writer_output.txt` (same text; `fill_request.py` reads `writer_output.txt`). Then go back to `h3-render` for lint, JSON build, and the yes/queue rules. Never skip that gate. Never queue from this skill alone.
