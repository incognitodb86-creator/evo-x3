# Research skills audit (report only)

- **Requested by:** Derrick, 9:25 PM CT Oct 16 2026 (relayed by Max Architect)
- **Executor:** Fleet Reviewer audit executor
- **Mode:** Read only. No skill was edited.
- **Scope:** `last30days-research`, `artframe-research`, `shorts-trends-research`, `shorts-historian`, `shorts-google-source-verify`, `fantasy-news-scout`, `cos-roster-verify` (all at `/home/box/agent-data/workflows/<id>/SKILL.md`; none has a `references/` folder; the `/home/box/sand-data/workflows/` mirror matches byte for byte). I also looked at the plugin skills `firecrawl-search`, `firecrawl-agent` and `apify-ultimate-scraper`, plus the history allowlist `/workspace/cos/research/trusted-history-websites-2026-09-10.md`.

## Counts

| Item | N |
|---|---:|
| Skills read | 7 (6 research, plus `cos-roster-verify`, which is not a research skill) |
| Plugin skills checked | 3 (firecrawl ×2, apify ×1) |
| External sources checked | 13 (14 URLs; Reddit via search excerpt only) |
| Findings | **15**: P0 **0** · P1 **5** · P2 **6** · P3 **4** |

## Bottom line

- **Shared skill:** Yes. Write one thin `research-core` skill of about 60 lines, and keep the lane rules as short add-ons inside the existing lane skills. Do not merge the lanes, and do not build tooling.
- **Separate research bot:** I agree with Max Architect: **not yet**. Reasons are in the bot verdict section below.
- **Biggest gap:** Only `shorts-google-source-verify` checks claims against their citations ("open the page, confirm the text"). The other five research skills ask for a URL but never check that the page actually supports the claim. No skill has a stop rule or a cost cap.

---

## Best-practice sources checked (opened Oct 16 2026, CT)

| # | Source | Takeaway used here |
|---|---|---|
| S1 | Anthropic, "How we built our multi-agent research system": https://www.anthropic.com/engineering/multi-agent-research-system | Lead agent plans, saves the plan, and gives parallel subagents an objective, an output format, tools and sources, and clear boundaries. Scale effort to the query: 1 agent and 3–10 calls for a simple fact, 2–4 subagents with 10–15 calls each for a comparison. Start wide, then narrow. A separate CitationAgent runs at the end. Judge rubric: factual accuracy, citation accuracy, completeness, primary over secondary sources, tool efficiency. Agents chose "SEO-optimized content farms" over authoritative sources until source-quality heuristics were added. Multi-agent runs use about 15× the tokens of a chat. Subagents should write their output to files. |
| S2 | Anthropic cookbook lead prompt: https://raw.githubusercontent.com/anthropics/anthropic-cookbook/main/patterns/agents/prompts/research_lead_agent.md | Default is 3 subagents, at most 20. "STOP FURTHER RESEARCH" once returns diminish. |
| S3 | Anthropic cookbook subagent prompt: https://raw.githubusercontent.com/anthropics/anthropic-cookbook/main/patterns/agents/prompts/research_subagent.md | Set a research budget (<5, ~5, ~10 or ≤15 calls by difficulty) with a hard cap of 20 calls. Stop when there are no new findings. Flag speculation ("could", "may", projections) and aggregators that are not the original source. |
| S4 | LangChain open_deep_research: https://github.com/langchain-ai/open_deep_research (README and `configuration.py` read through raw.githubusercontent) | Optional clarification step. Explicit caps: `max_concurrent_research_units`, `max_researcher_iterations`, `max_react_tool_calls`. Research notes are compressed before the final report. Warns that a 100-example eval run costs "~$20-$100". |
| S5 | Stanford STORM: https://github.com/stanford-oval/storm (README) | Query planning by asking questions from several perspectives, then outline, then write with citations. Notes that cheaper models can handle question asking and stronger ones the cited writing. |
| S6 | GPT Researcher: https://github.com/assafelovic/gpt-researcher (README) | A planner writes the research questions, executors gather in parallel, and each resource is summarized and source-tracked. Deep mode is a tree with configurable depth and breadth, and aggregates 20+ sources to reduce bias. |
| S7 | Hugging Face, "Open-source DeepResearch": https://huggingface.co/blog/open-deep-research | Simple tools and low complexity first. Community comments report context-window blowups of 419K–709K tokens, an argument for caps and compression. |
| S8 | OpenAI, "Introducing deep research": https://openai.com/index/introducing-deep-research/ | Admits it "may struggle with distinguishing authoritative information from rumors" and has "weakness in confidence calibration". The Feb 10 2026 update can restrict searches to trusted sites. Cites "specific sentences or passages". Performance rises with the tool-call budget. |
| S9 | "Cited but Not Verified" (arXiv): https://arxiv.org/html/2605.06635 | Fact-check accuracy fell about 42% on average as search depth grew from 2 to 150 tool calls, while link and relevance checks stayed above 92%. More searching is not automatically better. |
| S10 | Agents Handbook, deep research plus citation check: https://agentshandbook.com/p/run-a-deep-research-report-and-verify-its-citations | Claim table with title, URL, publication date and an exact quote of ≤30 words. "Do not cite what you did not read." Label inference. Check citations in a separate fresh pass. Watch for syndicated copies. |
| S11 | HN, "Ask HN: How to Use Deep Research?": https://news.ycombinator.com/item?id=43603574 · HN validation thread: https://news.ycombinator.com/item?id=48739064 | Deep research returns "blogspam listicles" unless told which trustworthy sources to use. A reviewer agent cuts confabulated citations, but spot checks can still miss them. |
| S12 | Reddit r/PromptEngineering: https://www.reddit.com/r/PromptEngineering/comments/1m368sn/how_do_you_get_an_ai_to_actually_use_and_cite/ (curl returned 403, so this rests on the search-index excerpt only) | Ask for the citation during the search, not afterwards; after-the-fact references are where models invent. Demand a verbatim quote. |
| S13 | Upstream last30days: https://github.com/mvanhorn/last30days-skill (search result, ~22K stars) | The community skill our `last30days-research` copies. Searches Reddit, X, YouTube, HN, Polymarket and GitHub in parallel with a strict 30-day window and engagement scoring. It is **not installed** on the box. |

---

## Comparison matrix

Legend: ✅ present · ◐ partial · ❌ missing

| Dimension | last30days | artframe-research | shorts-trends | shorts-historian | google-source-verify | fantasy-news-scout | Best practice |
|---|---|---|---|---|---|---|---|
| Query planning | ◐ topic + window | ◐ checklist of facets | ◐ lane scope | ◐ "claims from brief" | ✅ claim list + era/kit nouns | ❌ | Plan the sub-questions, perspectives (STORM) and effort tier (S1) |
| Triangulation | ❌ ("contradictions" section only) | ◐ conflicts → split, never average | ❌ | ◐ via verify | ✅ ≥2 independent Tier A/B | ◐ rumor vs report → low confidence | ≥2 independent sources for hard claims |
| Primary over secondary | ❌ | ◐ Tier A/B, but art tiers undefined | ❌ | ✅ Tier A/B | ✅ follow footnotes to museum/academic | ❌ | Primary first; secondary only as a pointer (S1, S3, S8) |
| Recency / date checks | ◐ 30-day window, dated sources | ❌ | ◐ capture date CT | ◐ "never invent dates" | ✅ access date CT | ◐ timestamp, no staleness cutoff | Publication date and access date; stale cutoff by lane |
| Claim → citation verify | ❌ | ❌ (links out to verify) | ❌ | ◐ via verify | ✅ re-open, confirm text, no SERP-only | ❌ | Open every cited page and quote the support (S1 CitationAgent, S10) |
| Saturation / stop | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | Budget plus a diminishing-returns stop (S2, S3, S9) |
| Dead ends recorded | ◐ "Unknowns" | ❌ | ◐ `NO_DATA` | ❌ | ◐ WEAK/FAIL | ◐ "no material news" + sources checked | "Searched, not found" log |
| Output format | ✅ brief | ✅ files | ✅ dated file | ✅ pack | ◐ notes | ✅ bullets | Common evidence table, plus a lane-specific body |
| Parallel subagents | ❌ | ❌ | ◐ "subagent-first" | ❌ | ❌ | ❌ | 1 agent by default; 2–4 for breadth with non-overlapping briefs; outputs written to files |
| Cost limits | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | Call caps, plus `--max-credits` on Firecrawl agent runs and max items on Apify runs |

`cos-roster-verify` is a disk and allowlist audit, not web research, so it stays out of the shared skill. It already does well on recording dead ends ("UI/sync mismatch") and on failure handling ("unreadable → stop").

---

## Overlap and duplication

1. **Tier A/B and CONTEXT_PACK when/where are defined in three places:** `artframe-research` (checklist), `shorts-historian` (HARD) and `shorts-google-source-verify` (Steps 2 and 4). Only the last one says what Tier A/B means in practice. The other two restate the rule and link to it, so the copies will drift apart.
2. **"Never invent metrics/dates/injuries" is written five times** (last30days, trends, historian, fantasy, artframe). That is a cheap duplicate, but it belongs in core.
3. **"Cite URL + date CT" is written four times with four different formats:** URL + date (last30days), capture date CT (trends), access date CT (verify), source + timestamp CT (fantasy).
4. **Trends and last30days overlap.** Both cover "what is hot on Reddit/X/YouTube in a window". Trends is last30days with Shorts metrics and a PD/OA filter on top.
5. **Historian and artframe-research overlap on Artframe lore packs.** The historian's "When" includes "Artframe lore packs", and artframe-research also produces `CONTEXT_PACK_L4.md`. Neither skill says which one owns the file.

## Gaps

- No stop rule or effort budget in any skill.
- No cost cap, although paid tools are listed (Firecrawl credits, Apify actor runs).
- No claim-to-citation check outside history.
- No art-history trusted-source list. The allowlist covers "Mycenaean, Homeric, Classical Greek, Roman, broader military history", while Artframe needs museum collection records, catalogues raisonnés and conservation reports.
- No staleness rule for fantasy news, where a Wednesday practice report is stale by Sunday.
- No dead-end log, so the next run repeats the same failed queries.
- `last30days-research` line 17 says to prefer the official marketplace skill "if installed". It is not installed, and the community upstream exists (S13).
- The Apify MCP namespace (`user-Apify`) is connected but is not mentioned in any research skill. The Apify CLI is not installed; the Firecrawl CLI is (`/home/box/.local/bin/firecrawl`).

---

## Findings

### P0: none
No research skill is set up to cause harm right now. The hard bans on invented metrics, dates and injuries hold everywhere.

### P1

**P1-1. Claim-to-citation verification is missing in 5 of 6 research skills.**
Evidence: Only `shorts-google-source-verify` steps 3 and 5 ("never cite from SERP snippet alone"; "re-open it; confirm text still matches") do it. S9 and S10 show that live, relevant links still fail to support their claims.
Fix (core, applies to every lane):
```
## Verify (before DONE)
For every hard claim: open the cited page (no SERP snippet cites), record a ≤25-word quote that supports it,
mark SUPPORTED / PARTIAL / UNSUPPORTED. Drop or hedge anything not SUPPORTED. Do not cite what you did not open.
Paywalled/blocked = say so; it cannot be the sole cite.
```

**P1-2. No stop rule or budget anywhere.**
Evidence: There is no cap in any of the 7 skills. S2 and S3 use explicit tiers and a hard cap of 20 calls. S9 shows accuracy falling as search depth grows.
Fix (core):
```
## Budget + stop
Pick a tier at plan time: QUICK ≤8 tool calls · STANDARD ≤20 · DEEP ≤40 total (≤15 per executor).
Stop early when two consecutive search rounds add no new independent source or claim, or every sub-question has ≥2 agreeing sources.
Over budget = stop and report gaps; never silently extend.
```

**P1-3. Primary over secondary is missing in last30days, trends and fantasy.**
Fix: Core gets one line: "Prefer the original publisher (official, filing, collection record, channel page itself). Aggregators and listicles are pointers only." Lane add-ons:
- fantasy: "Injury or status claims need the team or league official injury report, or a named beat reporter. Aggregator or rumor accounts mean confidence low."
- trends: "View counts come from the video or channel page itself, with a snapshot time CT. Third-party stat sites count as pointers."
- last30days: "Community posts are evidence of *sentiment*, never of *fact*." This also settles the apparent conflict with google-verify's "Reddit ban as sole evidence".

**P1-4. Recency rules are inconsistent and there is no staleness cutoff.**
Fix: Core rule: "Record **published date** (from the page, not the SERP) and **accessed date CT** for each source. Undated = flagged." Lane add-ons:
- fantasy: "News older than 24h before lock, or superseded by a newer practice report, is STALE."
- last30days: "Drop anything published outside the window, even if surfaced inside it. Watch syndicated copies that carry a new date (S10)."

**P1-5. Artframe Tier A/B is undefined for art history.**
Evidence: `artframe-research` requires "Tier A/B cites", but the only tier list on disk is scoped to ancient and military history.
Fix: Add a short Artframe section to the trusted-sites list, or a sibling file (museum collection records, catalogue raisonné, conservation and technical studies, university press monographs = A/B; Wikipedia and artsy blogs = C). Have artframe-research point at it. This is one list, not a new skill.

### P2

**P2-1. No common evidence table.**
Each lane has its own body format, so the output cannot be audited the same way across lanes.
Fix: Core appendix that every lane adds to the bottom of its normal output:
`| claim | source (publisher) | URL | published | accessed CT | tier/class | quote ≤25w | status | hedge |`

**P2-2. Dead ends are not recorded.**
Fix: Core section "Searched, not found": each query or source tried, plus the reason it failed (404, paywall, off-window, no support). Fantasy's "no material news + sources checked" already follows this pattern; generalize it.

**P2-3. No guidance on parallel subagents.**
Only trends mentions "subagent-first".
Fix (core, three lines): "Default 1 agent. Breadth asks may use 2–4 executors in background, each given an objective, an output file path, sources and tools, and what NOT to cover (S1). Executors write to files; the lead reads the files and runs Verify itself."

**P2-4. Three copies of the history verification rules (overlap items 1 and 5).**
Fix: Make `shorts-google-source-verify` the single history and art verify add-on. In historian and artframe-research, replace the restated Tier A/B lines with "Run [shorts-google-source-verify] before hard claims". Name **one** owner for `CONTEXT_PACK_L4.md`: artframe-research writes it and the historian reviews it for Artframe.

**P2-5. Tooling routing and cost caps are missing.**
Fix (core "Tools" block):
- WebSearch/WebFetch first.
- Then Firecrawl `search` or `scrape` for JS-heavy or thin pages.
- Firecrawl `agent` only with `--max-credits`.
- The Apify MCP namespace for platform metrics (YouTube, Reddit, X), with a max-items limit set.
- Never print keys.

This is community-first: these tools already exist, so nothing custom is needed.

**P2-6. The last30days skill points to a marketplace skill that is not installed.**
Community-first says to use the upstream `mvanhorn/last30days-skill` instead of hand-rolling it. Installing it needs reasoning and search API keys (S13), so it needs Derrick's approval.
Fix: Either (a) get Derrick's go to install upstream and make our skill a thin wrapper (window, CT labels, evidence table), or (b) delete line 17's conditional so the skill stops implying a tool exists.

### P3

**P3-1. Calibration and hedges are uneven.**
artframe has hard/soft/contested and fantasy has a confidence level; the others have nothing. S8 names calibration as a known weakness.
Fix: Put the `hedge` column in the shared table (P2-1).

**P3-2. No speculation or aggregator flagging.**
Fix: Core line taken from S3: "Mark predictions/'could/may'/projections as SPECULATIVE; mark aggregator-not-original."

**P3-3. "Google-double-check" wording.**
WebSearch is not literally Google.
Fix: Rename it in text to "independent web double-check", or keep the name as a label only. Cosmetic.

**P3-4. `cos-roster-verify` frontmatter `name: CoS roster verify` does not match its slug.**
Every other skill uses its slug. This is out of scope for research.
Fix: `name: cos-roster-verify` when someone next touches the file.

---

## Shared-skill recommendation

**One shared `research-core` skill, with lane add-ons left in the lane skills. Do not merge the lanes.**

What goes in core (about 60 lines, no scripts):
1. **Plan:** the question, 3–6 sub-questions (from several perspectives, as in STORM), date window, source classes, and budget tier.
2. **Gather:** wide then narrow. Use parallel tool calls. Executors are optional for breadth asks.
3. **Triangulate:** ≥2 independent sources for hard claims, primary preferred, aggregators as pointers only.
4. **Verify:** see P1-1.
5. **Budget and stop:** see P1-2.
6. **Record:** the evidence table (P2-1) and the "Searched, not found" log (P2-2).
7. **Bans:** never invent metrics, dates, quotes or injuries. Never print keys.

What stays in each lane, as 5–15 lines of add-on:

| Lane skill | Keeps |
|---|---|
| last30days-research | Rolling 30-day window; community = sentiment evidence; upstream tool wrapper |
| shorts-trends-research | `NO_DATA` metrics; PD/OA filter; showrunner greenlight; trend file paths |
| shorts-google-source-verify | Trusted-site allowlist; ≥2 Tier A/B; footnote chase. Becomes the history and art verify add-on |
| shorts-historian | SHOW/AVOID; authenticity pack |
| artframe-research | Punch pack HARD gate; LORE/REFS/CONTEXT_PACK files |
| fantasy-news-scout | ESPN single-seat ban; official injury report; staleness; bullet format |

Why this beats separate lane copies:
- The missing pieces (verify, stop, dates, dead ends) are the same in every lane, so they are fixed once instead of six times.
- The lane-specific pieces really are different, so merging the lanes would lose the HARD gates.

Avoiding overengineering:
- No new bot, no scripts, no custom citation checker.
- A community checker exists (`citesure` on PyPI) but is **not recommended yet**. Revisit only if manual verification proves too slow.
- Each lane skill grows by one link line ("Follow [research-core] then the add-on below") and loses its duplicated lines.

## Separate research bot: verdict

**I agree with Max Architect: not yet.** My reasons:
1. **It has been tried and it failed.** The Sep 24 audit scored the old Research bot **28/100 FAIL** ("Job = tool laundry list; 0 routines… overlap Trends/Historian"). Later audits record it as deleted and absorbed into lane skills (`2026-09-18-artframe-e2e-workflow-redteam.md`; `2026-09-24-alfred-roster-recheck-and-sizing-bp.md`: "no fourth research bot").
2. **The fleet already has the orchestrator-worker pattern.** Anthropic's design (S1) is a lead agent plus parallel subagents with their own context windows. Here the lane bot is the lead and its background executors are the subagents. A research bot would add a hop between them and recreate the "game of telephone" problem S1 warns about.
3. **Research depends on lane context.** PD/OA rules, punch-pack gates, ESPN seat rules and the Tier A/B allowlist all live with the lanes. A central bot would have to load every lane's rules, which is the "laundry list" failure all over again.
4. **The fixes are content fixes, not ownership fixes.** None of the 15 findings needs a new owner.
5. **Cost and roster.** Multi-agent research uses about 15× the tokens of a chat (S1). A standing bot invites always-on runs. The create-wall also needs Derrick's exact yes naming the bot, and the roster has just been cut to 11 agent folders.

**When to revisit:**
- ≥3 lanes need the same cross-lane research every week and no lane owns it (for example, a weekly cross-lane digest).
- Or `research-core` is in place for 2 weeks and audits still show lanes skipping Verify.

At that point, propose one bot with a single named routine to Derrick for an exact yes.

---

## Suggested order of work (for whoever is approved to edit)
1. Write `research-core` (P1-1, P1-2, P1-3 core line, P1-4 core line, P2-1, P2-2, P2-3, P2-5, P3-2).
2. Add a link line and the lane add-ons to each of the 6 lane skills, and delete the duplicated lines (P2-4).
3. Add the art-history tier section (P1-5).
4. Get Derrick's decision on installing upstream last30days (P2-6).
5. Cosmetic items (P3-3, P3-4).

*Report only. No skill, bot or setting was changed.*
