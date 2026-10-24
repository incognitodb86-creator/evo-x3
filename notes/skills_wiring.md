# MEM1 skills wiring - how Pi loads skills, and the one setting Max has to add (2026-10-23)

Forge built the skills; **Pi config is Max's** (AGENTS.md "## Scope": never edit Pi config, ralph.ps1, PROMPT.md,
permission files). Nothing in this pass touched Pi settings - Forge only wrote files under
`C:/AI/community/skills/` and `C:/AI/community/notes/`.

## What exists now

| Skill | Path | Covers |
|---|---|---|
| `h3-hc-render` | `C:/AI/community/skills/h3-hc-render/SKILL.md` | graph wiring + reference slots, frame/canvas math, budget gate, `p7/JOB_REQUEST.json`, objective proof checks |
| `h3-prompting` | `C:/AI/community/skills/h3-prompting/SKILL.md` | v2 chunk-prompt skeleton, reference wording, body/skin vocabulary, contradiction phrases, `overall_soundscape:`, PQ1 research list |
| `forge-self-diagnose` | `C:/AI/community/skills/forge-self-diagnose/SKILL.md` | per-pass ralph.log/denies.log read, `self_diagnosis.md`, deny classes, web-save check bomb, control-char/TASKS tick rules, self-destruct probes, commits |

Each file is the Agent Skills form: frontmatter `name` + `description` (the description is the routing text the
model sees at startup), then "when to use" + steps, then a `## Sources` list of the notes it was distilled from.

## How Pi loads skills (from the shipped docs)

- Docs on this box: `C:/Users/derek/AppData/Roaming/npm/node_modules/@earendil-works/pi-coding-agent/docs/skills.md`
  (and `docs/settings.md#resources`, `docs/configuration.md`, `docs/packages.md`).
  Upstream: `https://github.com/earendil-works/pi` (npm `@earendil-works/pi-coding-agent`, v1.4.0 here); the format
  is the Agent Skills spec, `https://agentskills.io/specification`; examples
  `https://github.com/badlogic/pi-skills` and `https://github.com/anthropics/skills`.
- A skill = a **directory containing `SKILL.md`**; directories are discovered **recursively**.
- At **startup** Pi scans the configured skill locations and puts only `name` + `description` + path in the system
  prompt; the body is read by the model only when a task matches. So adding skills is cheap, and the model can
  miss them - `/skill:<name>` forces a load, and `/reload` re-scans after an edit.
- Discovery locations, in the order the docs list them:
  1. `skills` in settings (user-level `<agent-dir>/settings.json`, i.e. `C:/Users/derek/.pi/agent/settings.json`;
     project-level `.pi/settings.json`). Type `string[]`, default `[]`, description "Skill files or directories".
     **Absolute paths and `~` are supported**; user-level resource paths resolve from the agent directory, project
     ones from the project `.pi` directory. Lists support `!pattern`, `+path`, `-path`. User + project lists are
     combined.
  2. Agent Skills locations `~/.agents/skills/` and `.agents/skills/`; project `.agents/skills/` is discovered from
     the working directory **upward through its ancestors, stopping at a repository root** - so for Ralph runs in
     `C:/Users/derek/5slock` a `C:/Users/derek/5slock/.agents/skills/` directory is picked up.
  3. `.pi/skills/` in the project, and skills shipped by Pi packages (`packages` setting, npm/git/local).
- Frontmatter rules that matter: `name` = lowercase letters, numbers, hyphens, no leading/trailing/consecutive
  hyphens, <=64 chars; `description` <=1024 chars; a `SKILL.md` with malformed frontmatter or no description is
  **not loaded**; a name collision keeps the first one found and warns. `disable-model-invocation: true` = only the
  explicit `/skill:` command loads it. `enableSkillCommands` (default `true`) controls slash-command discovery.
- Project skills can tell the model to run scripts / edit files, so Pi asks for **project trust** - an unattended
  Ralph run needs the trust to be pre-granted, otherwise the skill text never reaches the loop.

## The change Max makes (pick one)

1. User-level, all sessions (simplest). In `C:/Users/derek/.pi/agent/settings.json` add to the JSON object:

   ```json
   "skills": ["C:/AI/community/skills"]
   ```

   (if `skills` already exists, append the path to the array; `"$schema": "https://pi.dev/schemas/settings.schema.json"`
   gives editor validation).
2. Ralph project only: put the three skill directories under `C:/Users/derek/5slock/.agents/skills/` (copy, or a
   directory junction: `cmd /c mklink /J "C:\Users\derek\5slock\.agents\skills" "C:\AI\community\skills"`), and grant
   project trust once. Nothing leaks into other projects.
3. Machine-wide for every Agent Skills app: junction `C:/Users/derek/.agents/skills` -> `C:/AI/community/skills`.

Then verify: start Pi in the target directory, check the startup diagnostics list the three names, and run
`/skill:h3-hc-render` (it should print the loaded instructions). Forge's own loop reads
`skills/forge-self-diagnose/SKILL.md` at the top of every pass even with no setting at all, because PROMPT.md points
the loop at `notes/` - the setting is what makes Pi route to them by description.

## Deliberate non-actions

- No Pi settings, `ralph.ps1`, PROMPT.md, permission/guard files, `chain.ps1` or Strata edits (Max's; a `ralph.ps1`
  edit in an earlier pass = SCOPE fail + STOP_RALPH).
- No GPU work this pass: 0 ComfyUI calls, 0 renders, budget untouched (`logs/p7_budget.json` read-only:
  `used_min 472.9, jobs 38, cap 615/45` at 18:53:47).
