---
title: AlienPc idle coding/agent model is uncensored - Huihui abliterated Qwen3.8-27B GSQ-RCO-IQ3_S-mtp
date: 2026-10-09
status: recorded
tags: [max, alienpc, local-llm, model-pick]
supersedes_in_part: gbrain/04_memory/max-studio-2026-10-08/2026-10-08_decision_alienpc-local-llm-optimize.md (its "Do not use Heretic 27B for agents or tools" line, for the AlienPc idle coding/agent profile only)
---

- **Override (RELAYED):** Derrick said "i want the uncenscored" in chat on 2026-10-09 at about 5:06 PM CT. This overrides the earlier lock that Heretic/abliterated builds are not for agents and tools (DEC 2026-10-08), for the AlienPc idle coding/agent model only. The 9B Heretic vision profile stays tools-off.
- **Pick (RELAYED):** at about 5:10 PM CT, Derrick chose from the options shown: `huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF`, file `Huihui-Qwen3.8-27B-abliterated-GSQ-RCO-IQ3_S-mtp.gguf`. The alternatives were UD-IQ4_XS and downloading both. The thread lists the file at 11.0 GiB; the HF file is 12,120,016,416 bytes (11.29 GiB).
- **Still required:** (1) Derrick's separate download GO, with the target `C:\AI\models\`; (2) a local tool-call smoke test and a coding comparison before any coding or agent job uses it. Each is a benchmark and needs its own GO.
- **Runtime notes (web-checked 2026-10-09):** the repo ships `mmproj-model-bf16.gguf` (931,145,888 bytes). The card says vision and MTP were not modified. The GSQ-RCO files are standard GGUF, per the ISTA source card, and MTP has been in llama.cpp since PR #22673, so no newer build than b11482 is stated as required. The card only says "use the latest llama.cpp". The Ternary series in the same repo needs the PrismML fork; it is not this file.
- **Plan:** `ce/plans/2026-10-09-1622-feat-alienpc-local-ai-shared-gpu-plan.md` (Key Decisions, R11, KTD4, KTD16, U12).

- **Superseded-by pointers (Fleet Reviewer N-19):** added to files Grok Bot owns (this file, the plan's Key Decision and R11, research `2026-10-09-local-llm-community-variants.md` §3b). Still needed, by its owner: the Chief of Staff's DEC `gbrain/04_memory/max-studio-2026-10-08/2026-10-08_decision_alienpc-local-llm-optimize.md` line 27 ("Do not use Heretic 27B for agents or tools") should get a superseded-in-part pointer to this file.
