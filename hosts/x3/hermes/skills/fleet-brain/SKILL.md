---
name: fleet-brain
description: "Use when Derrick asks about past lab decisions, project plans, briefings, fleet notes, or shared GrokBot/Max context stored in /home/evo/AI/fleet-brain (e.g., 'what did we decide about X?', 'check the brain', 'read my notes on Y'). Read-only."
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [knowledge, notes, parity]
    category: knowledge
    requires_toolsets: [terminal]
---

# Fleet Brain (Read-Only Shared Knowledge)

Read the shared home-lab knowledge base at `/home/evo/AI/fleet-brain` (the same notes/plans/briefings GrokBot uses) so Hermes stays in sync with prior decisions.

## Rules (strict)
- **Read-only:** never edit, move, or delete files inside `/home/evo/AI/fleet-brain`.
- **No secrets:** never open or print files matching `*.env`, `*.token`, `*.cred`, `*.key`, `auth.json`, `mcp.json`, or `models.json`.
- **Fast targeted search:** use `rg` or `find` with depth limits — never dump whole folders.

## Workflow (1–2 read-only commands)

1. **Locate matching notes / plans / briefings:**
   ```bash
   B=/home/evo/AI/fleet-brain
   [ -d "$B" ] || { echo "fleet-brain not present at $B"; exit 0; }
   rg -i -l --max-filesize 512K --glob '!*.{env,token,cred,key}' '<keywords>' "$B" 2>/dev/null | head -n 15
   ```
   Or inspect top folders / recent updates:
   ```bash
   ls -1 /home/evo/AI/fleet-brain
   find /home/evo/AI/fleet-brain -maxdepth 3 -name '*.md' -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -n 15
   ```

2. **Read the specific matching file(s)** with `sed -n '1,120p' <file>` (or `read_file`), cite the file path and date in your answer, and keep the reply concise.
