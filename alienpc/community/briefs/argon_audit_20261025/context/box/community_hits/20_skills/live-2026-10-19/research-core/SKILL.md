---
name: research-core
description: >-
  Use this before any web research that has to produce cited claims (facts,
  trends, sentiment, news, best practice). It covers the shared plan, gather,
  verify and stop loop plus the evidence table. Lane skills add their own rules
  on top.
---
# Research core

Lane rules override this core when they conflict (e.g., a lane's tighter budget or its accepted single official source).

## 1. Plan (write it down before searching)
- Question, then 3–6 sub-questions asked from different angles (user, expert, skeptic, official).
- Date window and recency filter (e.g. "published ≥ YYYY-MM-DD"). Source classes to try. Budget tier (§5).
- Breadth ask: default is 1 agent. You may use 2–4 background executors, each given an objective, an output file path, sources and tools, and what NOT to cover. Executors write to files. The lead reads them and runs §4 itself.

## 2. Gather: community first, wide then narrow
- For tools, methods or "how do people do X", start with the community and the maintainers: GitHub (README, issues, releases), Reddit, HN, Hugging Face, official docs. Reuse an existing tool or skill before building one.
- Run independent searches as parallel calls. Start broad, then narrow toward the sub-questions that are still open.
- Tool order: WebSearch/WebFetch, then Firecrawl `search`/`scrape` for JS-heavy or thin pages. Use Firecrawl `agent` only with `--max-credits`. For platform metrics (YouTube/Reddit/X), use the Apify MCP and set `callOptions.maxItems` (pay-per-result) **and** `maxTotalChargeUsd` (pay-per-event) **and** a `timeout`, plus the Actor's own result-limit input. Never print API keys.
- Write the URL and date down when you find the source, not afterwards.

## 3. Weigh: primary over secondary, triangulate
- Prefer the original publisher: official site or filing, collection record, the maintainer's repo, the channel or post page itself. Aggregators, listicles, SEO pages and AI answers are pointers only. Follow them to the origin.
- Community posts are evidence of sentiment, not fact, unless the poster is the primary source (for example a maintainer announcing a release).
- Hard claims (numbers, dates, names, quotes, status) need ≥2 **independent** agreeing sources. Syndicated copies count as one source. If sources conflict, report both sides and never average them.
- Record the **published date** (from the page, not the SERP) and the **accessed date CT** for every source. An undated source is flagged as `UNDATED`. Drop anything outside the window even if it showed up in a search inside it (watch for reposts with a new date).
- Mark predictions, "could/may" language and projections as `SPECULATIVE`. Mark a secondhand source as `AGGREGATOR`.

## 4. Verify (before DONE), one claim at a time
- Open each cited page this session; a SERP snippet is never a cite. Find the passage and copy a quote of ≤25 words.
- Mark each claim `SUPPORTED` / `PARTIAL` / `UNSUPPORTED`. Drop or hedge anything that is not SUPPORTED. Do not cite what you did not open.
- If a page is paywalled or blocked, say so. It cannot be the only cite.
- A claim carried over from memory, an older file or another agent that you did not re-open this session is labelled `NOT CHECKED THIS SESSION`.

## 5. Budget and stop
- Pick a tier when you plan: QUICK ≤8 tool calls · STANDARD ≤20 · DEEP ≤40 total (≤15 per executor). Use a wall-clock cap if the lane sets one.
- Stop early (saturation) when two search rounds in a row add no new independent source or claim, or when every sub-question has ≥2 agreeing sources.
- If you go over budget, stop and report the gaps. Never silently extend. More searching is not more accuracy.

## 6. Record dead ends
- Keep a "Searched, not found" log: each query or source tried and why it failed (404, paywall, blocked, off-window, no support, duplicate). That way the next run does not repeat it.

## Bans
Never invent metrics, dates, quotes, names, injuries or engagement. Write `NO_DATA` instead of guessing.

## Output template (append to the lane's own output)
```
Question · window · tier used (N calls) · accessed YYYY-MM-DD CT
TLDR (2–4 lines, hedged)
| claim | source (publisher) | URL | published | accessed CT | class (primary/secondary/community/aggregator; lane tier) | quote ≤25w | status | hedge (hard/soft/contested/speculative) |
Conflicts: …   Not checked this session: …   Searched, not found: query/source → reason
Open questions / what to verify next
```
