---
name: last30days-research
description: >-
  use this when researching what people actually say about a topic in the last
  ~30 days with dated cited sources (last30days pattern; runs on research-core)
---
# last30days-style research

**Run [research-core](sand-workflow:research-core) first.** It covers plan, gather, verify, budget/stop, the evidence table and dead ends. The rules below are this lane's add-on.

## When
Use this for what people say about a topic across public web and social surfaces (Reddit, X, YouTube, HN, web news) in roughly the **last 30 days**. Prefer it over training-only answers for trend, market or sentiment asks. Default tier: STANDARD.

## Lane rules
- Window: a rolling 30 days ending today, CT. Drop anything **published** outside the window, even if a search inside the window surfaced it. Watch for syndicated copies or reposts that carry a new date.
- Community posts are evidence of **sentiment**, never of **fact**. Facts need the primary source, as research-core §3 says.
- Engagement, "viral" or revenue claims need a dated snapshot taken from the post or page itself; otherwise write `NO_DATA`.
- Sort the findings into Facts (cited) · Sentiment themes · Contradictions · Unknowns.

## Output
A short brief with TLDR · Timeline · Top claims with links · Sentiment themes · Contradictions · Risks/biases · What to verify next. Then add the research-core evidence table and the "Searched, not found" log.

CE: follow [fleet-ce-adapter](sand-workflow:fleet-ce-adapter) (ce-plan · ce-doc-review · ce-work · ce-compound).
