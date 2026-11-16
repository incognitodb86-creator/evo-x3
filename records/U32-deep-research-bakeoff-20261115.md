# U32 Deep-research bake-off: EVO-X3, 2026-11-15/16

Approved: card t1811s6671. Plan: `coding-harness-research-20261115.md` §5.
- R1 was run by Antigravity, 23:51–23:57 CT on Nov 15. Antigravity then hit its quota (429).
- Max Architect installed the R2 and R3 tools and ran both on Nov 16, 06:23–06:41 CT, then wrote this record.
- Fixed questions: 5 (`deep-research-bakeoff/questions.json`). n=1 per arm, so the results are tentative.

## Setup
- **LLM:** x3-local `flash-next` (Halogen 0.20.5) through llama-swap at 127.0.0.1:8080. The key is loaded into the environment only, by `run_arm.sh`.
- **Embeddings:** `embed-small`, the resident nomic slot (R3).
- **Search:** SearXNG Podman container `u32-searxng`, bound to **127.0.0.1:8888 only** (verified with `podman ps`: `127.0.0.1:8888->8080/tcp`; 43 JSON results). No paid search API.
- **Arms:**
  - **R1:** a clean-room private build of kyuz0's 3-tier approach (orchestrator, searcher, page analyzer, with tool quotas). No kyuz0 code was copied; that repo has no license.
  - **R2:** LearningCircuit local-deep-research **2.0.1** (pip, CPU torch), quick_summary, 2 iterations × 2 questions.
  - **R3:** GPT-Researcher **0.17.0** (pip), research_report, `RETRIEVER=searx`, 2 iterations / 2 subtopics.
- **Install notes:**
  - `.venv-ldr` and `.venv-gptr` sit under `~/evo-x3`. `.venv-gptr` is 1.2 GB. Nothing over 5 GB.
  - R2's runner crashed once on JSON serialization (an LDR `Document` object). Fixed with `default=str`; backup `run_r2_ldr.py.bak-20261116`.
  - R3 warns that MCPRetriever is not installed. It isn't needed.

## Results
- **Rubric** = how many ground-truth terms appear in the report.
- **Correct** = Max's judgment against the ground truth.
- **Cites checked** = cited URLs Max opened, and whether each one supports the claim.

| Arm | Correct (of 5) | Rubric hits | Sources per question | Mean wall time | Cites checked |
|---|---|---|---|---|---|
| R1 3-tier (clean-room) | 4 (Q5: analyzers extracted nothing, so it honestly declined) | 20/26 | 4–5 | 71.0 s | 4/4 support |
| R2 local-deep-research | 5 (Q1 left out the 76.9% overall rate) | 23/26 | 29–54 | **56.9 s** | 5/6 support, 1 unverifiable (PyPI blocks curl) |
| R3 GPT-Researcher | **5** | **25/26** | 8–13 | 79.9 s | 4/4 support |

Wall time per question, Q1–Q5:
- R1: 64.8 / 54.6 / 81.5 / 103.2 / 51.1 s
- R2: 31.6 / 60.0 / 45.6 / 71.8 / 75.8 s
- R3: 69.5 / 72.8 / 85.2 / 86.0 / 86.2 s

R1 tokens per question: about 26–30K prompt and 2–5K completion, with 4–6 searches, 7–9 fetches and 4–5 analyses.

R3 reports are long (11–15K characters each). R3's URL list also catches localhost example URLs quoted from pages; those are not real sources.

## Ranking
1. **R2 local-deep-research and R3 GPT-Researcher are tied on correctness** (5/5 each).
   - R3 had the most complete answers (25/26).
   - R2 was 29% faster, had the most sources, and gave tighter answers. SearXNG is its main search backend, built in. In GPT-Researcher it's an add-on you have to switch on, because the default is the paid Tavily API.
   - **Pick: LDR is the default deep-research tool on the X3, with GPT-Researcher as the alternate.**
2. **R3 GPT-Researcher:** most thorough, slowest.
3. **R1 3-tier clean-room:** good citations, but its page analyzer fails on JavaScript and challenge-protected pages (Q5). Worth keeping only as a pi-native design reference.

## Skipped / notes
- The R4 pi-subagents arm (optional).
- n=3.
- Token counts for R2 and R3 (not exposed cheaply).
