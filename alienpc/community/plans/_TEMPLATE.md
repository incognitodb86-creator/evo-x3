# <Plan title> — 1 page, about 400 words max

Derrick decision(s) this comes from: <quote + CT time>

**Goal:** one sentence.
**Done when:** what Derrick sees, and the number or check that says pass.
**Writer inputs:** image-direct | caption-fed | none. Which model reads the picture (Forge's own vision model unless Derrick named another).
**Pictures:** Picture 1 / Picture 2 and the open frame for each arm.
**Who builds:** Forge (default) or Antigravity (only when Derrick named it). Max briefs; he does not build.
**Community baseline:** the published workflow or settings this starts from. No new rules or controls for Forge.
**Acceptance before GPU:** Max reads every generated prompt against the real stills and this plan. Scores go to Derrick before GO.
**Stop:** when to stop, and what counts as a fail.

Small, easy-to-undo jobs skip this. One review round at most, saved only in 60_reviews/.

**Render queue:** build each request with `scripts\make_b2_request.py` (from `templates\b2.api.json`, the B2 default), then the AGENTS.md Render launch line (`run_queue.py ... --detach`); see `templates\render-queue-template.md`. Frames: <n> (c0.length = run_queue --frames).
