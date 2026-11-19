# U21 / U32 — Run approved X3 benchmarks and the deep-research bake-off

You are Google Antigravity **Orchestrator (Argon)** (`gemini-pro-orchestrator-g1-pro`). This is an implementation run, not report-only. Do the work on this host (EVO-X3).

Approved by Derrick:

- Benchmarks B1–B5 of the U21 / UB protocol: t346u (unit approved), then t1828u ("continue now… are we ready for the benchmark") and t1830u ("Can we have antigravity orchestor do it?") at 8:16 PM CT on 2026-11-15, to save Grok Bot usage.
- Deep-research bake-off: card t1811s6671 ("Yes, install and run the deep-research bake-off after X3 setup finishes").

A Max job that was going to run this was started at 8:15 PM CT and stopped at 8:16 PM CT. A read-only check at 8:16:56 PM CT found **no leftover work**: no new files under `~/evo-x3` since 20:14, no lease-take file, and no benchmark processes. llama-swap itself was already `active` (normal production). Do not revert anything. If you later find a half-started file from that minute, leave it, note it, and continue cleanly.

Working directory: `~/evo-x3`.

## Source files (already in `~/evo-x3/records/`)

- `U21-benchmark-protocol-rev9-8141f53.md` — the U21 B1–B6 section extracted from fleet-brain commit `8141f53` (EVO plan rev 9). **Run B1–B5 exactly as this text defines them.** Later rev 10 renamed the unit **UB** (X3 records already used U21–U26 for other jobs) and recorded approval at t346u; that does not change the B1–B5 procedure.
- `2026-11-15-llm-benchmarking-methods.md` — the research note the protocol points to (quotes, audit checklist, harness usage). Follow it when the protocol defers to it.
- `coding-harness-research-20261115.md` — section 5 is the deep-research bake-off plan (arms, question set, scoring). Use that, not section 4.
- `evo-x3-lease-README.md` — lease format and release step.

## 1. Lease, then B1–B5

Take the X3 lease before any install, config edit, model load, or benchmark, following `~/evo-x3/records/evo-x3-lease-README.md`. As of 8:16 PM CT the newest brain-style status was a **release** (U29, 7:50 PM CT); U31 finished at 8:12:59 PM CT with no leftover lease file. Holder name: Antigravity Orchestrator (Argon), job `u21-benchmarks-u32-deep-research`. Scope: B1–B5 plus the approved deep-research bake-off. Not touched: B6 / AlienPc, Windows partitions, BIOS, USB X3BACKUP, Tailscale, Sydney, PixlStash, Render chats. Release the lease when this brief is done (or if you stop early), with the required release file. Do not commit lease files on their own.

Then run **B1, B2, B3, B4, B5** exactly as the protocol defines them.

- **Skip B6.** It is AlienPc-only (ComfyUI H3 on the 5090 / 5070 Ti) and is not part of this X3 run.
- **B1:** Render and Sydney chats stay idle. Quiet window, lease held, header fields filled (power mode, IOMMU, kernel, engine/toolbox digest, temperature or NO_DATA, page-cache note). Pass: llama-swap log shows no non-bench requests during the window.
- **B2:** llama-bench JSON + llama-benchy served path at the stated depths and run counts; mean ± sd; overlap = tie; keep the existing U12 cold TTFT fixture and the U6 27B DFlash2 with/without long-context pair (find those fixtures in existing `~/evo-x3` records; do not invent a replacement unless they are missing, and if they are missing say so). Flash-Next MTP numbers come from the served path. If an engine has no llama-bench, served-path rows only.
- **B3:** raw JSON at `~/evo-x3/bench/<YYYY-MM-DD>-<run-id>/`; the human record is `~/evo-x3/records/U21-benchmarks-20261115.md` (and, if a fleet-brain checkout is available, also the plan's `records/bench/<YYYY-MM-DD>-<run-id>.md` path). Coherence check first: one real generation per (model, backend, build); if it fails, delete that arm's throughput rows, do not footnote them. Provenance fields as specified (including model sha256 and raw-JSON sha256).
- **B4:** You run the generations (pinned prompt file of about 8–12 prompts, git hash, pinned samplers, fixed seeds, 3 runs, A/B order swapped between rounds). No secrets and no Imagine prompts in the prompt file. Prompt maker scores the blinded outputs — write a clearly labeled blind set and do not self-score as the official result. If Prompt maker is not available mid-run, leave the blinded set in the record and mark official scores as pending.
- **B5:** free RULER subset (or needle subset) at two or three lengths (e.g. 32K and 128K) for Flash-Next and the 27B, with tokenizer, length and seed.

Before **each** model swap or llama-swap SIGHUP/restart, confirm llama-swap has **no requests in flight**. Restore production `flash-next` when you are done (or between long gaps if safe).

**Not approved — do not run:**

- The paid EQ-Bench Creative Writing judge, and **no paid APIs at all**.
- The coding bake-off (Harbor, Terminal-Bench, SWE-bench, Aider polyglot, Forge coding tasks, section 4 of the research doc).

## 2. Then the approved deep-research bake-off (U32)

After B1–B5 (or in a documented continuation if a quiet-window constraint forces a split), install and run:

- **Arms:** kyuz0's 3-tier *approach* vs LearningCircuit `local-deep-research` vs GPT-Researcher. All on the **x3-local `flash-next`** endpoint, with the same **SearXNG**.
- **SearXNG:** Podman container, **bound to localhost only** (not the tailnet, not a LAN bind). Back up any related config first.
- **kyuz0 arm:** implement the 3-tier design in section 5 of the research doc (orchestrator / searcher / page-analyzer, pages saved as markdown, cited report, tool quotas). `kyuz0/local-agent-builder` has **no license file**. Do **not** copy or vendor that repo's source. Building a private implementation of the published approach is OK. The cheap pi-subagents "R4" arm in the research doc is optional, not required.
- **Questions:** use the small fixed set in section 5d (the five questions with already-verified ground truth). Score **sources found**, **citation accuracy** (you spot-check that cited URLs open and support the claim — not an LLM judge), and **wall time**. Also record tokens/tool-calls if easy. `n=1` first pass is OK if `n=3` would run too long; write the chosen `n` in the record.
- Reuse the resident nomic embed-small slot if an arm needs embeddings. Do not add llama-swap.yaml slots.
- No paid search APIs (no Tavily/OpenAI keys). SearXNG only.

## Hard rules

- Back up every config you change (`.bak-<timestamp>`).
- **No `llama-swap.yaml` slot changes** and **no downloads over about 5 GB**. If something is larger, list it in the record and skip it; do not pull it.
- Never put secrets or API keys on command lines, and never print them. Do not `cat` or echo `/etc/evo-x3/*` env/cred files. If a local endpoint needs a key, **source** the right file under `/etc/evo-x3/` into the process environment (likely `llm.env` for llama-swap) and keep it out of logs, transcripts, and git.
- Do not touch Windows partitions, BIOS, USB X3BACKUP, Tailscale, or Sydney data (no chats, persona, or memory). Do not view PixlStash library contents. Do not touch the original ComfyUI folder.
- Do not delete anything; use `_archive` if you must move a file.
- No new spending, no firmware, no LUKS, no model re-pulls, no ACL/Tailscale changes.
- `~/evo-x3` is **not** a git repository today (no `.git`). Do **not** `git init` it. Commit `/etc` changes with **etckeeper** after a secret-safe review. Commit on-topic changes only in the existing `~/AI` repos (same practice as U31: no secrets, no weights). Do not use `git add -A` in `~/AI/community`. If `gitleaks` is still missing, do not install it; review diffs by hand and note that in the record.
- Fleet pack files: do not edit pack text. List any needed pack change in the record instead.
- Skip and list anything risky or that needs Derrick's choice.

## Records and done condition

Write both of these (times in America/Chicago / CT):

1. `~/evo-x3/records/U21-benchmarks-20261115.md` — B1–B5 (and B6 listed as skipped, AlienPc-only). Tables of the numbers, provenance/header fields, win/tie calls, coherence results, slot-pick implications, anything skipped and why, start/end times in CT.
2. `~/evo-x3/records/U32-deep-research-bakeoff-20261115.md` — bake-off ranking with sources-found, citation-accuracy spot-checks, and wall time per arm/question; install notes (SearXNG bind address confirmed localhost-only); anything skipped and why; times in CT.

Raw bench JSON stays under `~/evo-x3/bench/`. When finished, release the lease, and leave production llama-swap on `flash-next` unless a documented in-flight reason prevents the restore.
