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

You write the MiniMax-H3 prompt. Do not call a writer model or judge model; `render_writer_pipeline.py --prose-file` runs the lint, clone/filler/oral-speech gates, and dry-run build on your prose.

1. Load `h3-prompting` for Beta 7 format. Load `h3-parody-identity` only for a named parody.
2. Everyone depicted is 18+. If the ask or still has a youth cue, stop and report it. Write only the prompt text: no preamble, no code fence, no notes.
3. Use exactly these four headers, once each, in this order:
   - `subject_definitions:`
   - `summary:`
   - `retention_analysis:`
   - `detailed_description:`
   No pre-U56 headers and no Markdown in the body. Put diegetic sound in ordinary sentences at the end of `detailed_description`.
4. Save the prompt to `<run_dir>/hermes_prose.txt`. Then go back to `h3-render` to run `render_writer_pipeline.py --prose-file` (which runs `still_read`, `wp_lint`, clone/filler/oral-speech gates, and dry-run ComfyUI JSON build) and follow the yes/queue rules. Never skip that gate. Never queue from this skill alone.
