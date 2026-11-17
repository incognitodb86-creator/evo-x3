# Always-on brief vs on-demand skills (AGENTS-style)

**Stamp:** 2026-10-02 ~16:50 CT  
**Source:** research rank **2** in `/workspace/cos/research/2026-10-02-community-agent-skills-subagents-efficiency.md` (AGENTS.md + Anthropic simple composable + Cursor/agentskills.io progressive disclosure).  
**Rank 5** already live: [fleet-handoff-schema](sand-workflow:fleet-handoff-schema).

## Split
| Layer | What belongs | What does not |
| --- | --- | --- |
| **Always-on Job** (this bot's description) | Who you are, HARD locks, lease, who owns what, approval walls, skill **cites** | WPM math, seat bash, stage tables, smoke recipes, checklists |
| **On-demand skill** | Trigger description (third person, when) + short HARD one-liners | Full transcripts, other bots' Jobs |
| **`references/` beside the skill** | Long procedure, KEEP argv, checklists loaded by Read | A second always-on prompt |

## Rules
1. If a Job restates a skill recipe, delete the recipe from the Job and cite the skill.
2. Slimming a Job must **KEEP every HARD lock** (constraint stays; wording may shorten).
3. Group shells (Fantasy Football, Imagine Crew) route only — they are not operators.
4. Phase end still uses STATE/LOCKS/NEXT/BLOCKERS/FILES/DO-NOT-REPEAT.
5. End of phase: 3–7 don't-dos merge into living CAPA or skill same turn ([close-out-verify](sand-workflow:close-out-verify)).

## Owners (rank 3)
- **AlienPc Video Dial** = Max scoreboard + Max handoff owner.
- **CoS** = Plan / CAPA / research **agent-as-tool** only. Not a second Max watcher.
- AlienPc Shell lease = Dial XOR CoS. Never dual-Shell.
