---
name: h3-writer
description: "Use only when Derrick says to write the H3 video prompt yourself ('write it yourself', 'community way', 'path B'): write the MiniMax-H3 prompt from the same writer rules the pipeline uses, then hand it to the h3-render gate with --prose-file."
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [render, h3, writing]
    category: creative
---

# H3 writer (you write the prompt)

1. Read `references/writer_prompt.md` fully (`skill_view h3-writer references/writer_prompt.md`). It is the same
   writer prompt the pipeline model gets: a copy of `/home/evo/AI/render/writer_pipeline/writer_prompt.md` (compiled
   from `render/AGENTS.md`), built in by build-hermes-skills.sh.
2. Load `h3-prompting` for the format. Load `h3-parody-identity` for a named parody.
3. Everyone is 18+. Write only the prompt text: no preamble, no code fence, no notes.
4. Save it to `<run_dir>/hermes_prose.txt` and go back to h3-render point 7. The pipeline gate (lint, 18+ stops,
   build) decides READY. Never skip the gate. Never queue without Derrick's yes.
