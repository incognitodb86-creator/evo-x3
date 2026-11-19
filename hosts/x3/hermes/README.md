# Hermes on EVO-X3 (snapshot, Derrick t2613u)

Live home: /home/evo/.hermes (local git, nightly hermes-state-commit, no remote). Not pushed itself: it holds .env, state DBs, sessions.
hermes-agent: https://github.com/NousResearch/hermes-agent.git @ ae2a81ccc00e9b7c06301523e5bb09608397149c
Unit: hosts/x3/systemd/user/hermes-gateway.service (+ .d drop-ins).
config.yaml: key/token/password values replaced with <redacted>. memories/ was empty at snapshot time.
Snapshot taken 2026-11-19 09:44 CST.

## H9 proposal: Hermes renders itself, pi only for coding (2026-11-19, not live until `UNI-APPLY-X3-E-HERMES`)

- `SOUL.md` here is the proposed SOUL: Hermes's tone paragraph only. The old extra lines (video -> pi-job, OC facts,
  adult rule) move: routing to the `h3-render` skill, facts to `memories/USER.md`. Hermes docs: SOUL is identity and
  tone; workflow and paths belong in skills or project files.
- `skills/h3-render/HEAD.md` + `bin/build-hermes-skills.sh`: the render skill is built on the box from this header plus
  a verbatim copy of `render/OPERATOR.md`, so Hermes follows the same rules as Render on pi. `--check` prints DRIFT
  when OPERATOR.md changes.
- `skills/h3-writer/SKILL.md`: "write it yourself" mode; the build adds `references/writer_prompt.md` (the pipeline's
  compiled writer prompt).
- `skills/pi-job/SKILL.after-h9.md`: the coding-only pi-job skill installed at the switch. `skills/pi-job/SKILL.md`
  stays the current one until then.
- `memories/USER.md`: Derrick's facts (OCs, 18+, Hermes renders / pi codes), 578 chars of the 1,375 limit.
