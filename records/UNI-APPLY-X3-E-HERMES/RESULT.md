# UNI-APPLY-X3-E-HERMES RESULT

When: 2026-11-19 7:44-7:51 PM CT (America/Chicago). Doer: Max X3 lane (executor), Derrick t2958u ("Setup the soul.md and ext for hermes ... Ensure our setup to run shit through hermes is correct"). Prereqs: `UNI-APPLY-X3-B-PIJOB/RESULT.md` and `UNI-APPLY-X3-D/RESULT.md` (same commit). No render running, `active_agents 0` before the restart. Source: `mono` `0fdf10a2` `hosts/x3/hermes/` staged at `/home/evo/AI/_staging/hermes-src-mono0fdf10a2` (the `/home/derekboone/evo-x3` clone is stale at `a383932` with local snapshot edits and was not pulled). Hermes Agent v0.23.2 (`ae2a81ccc00e`). snapshot: in this commit. Rollback: not triggered.

## Step 0 - DONE
Backup root `/home/evo/.hermes/_archive/20261119-h9/`: `config.yaml`, `SOUL.md`, `pi-job.SKILL.md`, `memories/` (was empty), `config-show.before.txt`, `skills.before.txt`. No local `flux-klein-prompting` copy existed.

## Item 1 - DONE
`build-hermes-skills.sh` -> `installed .../skills/creative/h3-render .../skills/creative/h3-writer`; `--check` -> `OK h3-render h3-writer match OPERATOR.md and writer_prompt.md`. `grep -c '$PIXL_KEY'` in built `h3-render/SKILL.md` = 0.

## Item 2 - DONE (one change from the brief)
Set: `skills.external_dirs [/home/evo/AI/community/skills]`, `skills.disabled` (10 names), `skills.write_approval true`, `approvals.mode smart`, `approvals.timeout 300`, `approvals.cron_mode deny`, `approvals.single_query_mode deny`, `approvals.unattended_mode deny`, `agent.max_turns 80`.
- `agent.reasoning_effort` = `false` (thinking OFF), not the brief's `low`: Derrick's chat rule "thinking stays OFF in production" wins. In v0.23.2 `hermes config set ... none` stores YAML null (= default); `false` is the documented "disabled" value (`hermes_constants.parse_reasoning_effort`).
- `hermes config set` warned that `skills.disabled` and `agent.reasoning_effort` are not in its schema, but both are read (`agent/skill_utils.get_disabled_skill_names`, `gateway/run_config_loaders.py`); `hermes skills list` shows the 10 names as `disabled`.

## Item 3 - DONE
`SOUL.md` (668 B, tone only), `memories/USER.md` (582 B), `memories/MEMORY.md` (1,221 chars; Flux still builder renamed "Miraclein still builder" per Derrick), `skills/devops/lab-status`, `skills/knowledge/fleet-brain`, `skills/pi-job/SKILL.md` = `SKILL.after-h9.md` (coding only).

## Item 3b - DONE
- `agent-hooks/guard-render-queue.sh` + `scripts/morning-digest.sh` installed; digest smoke run printed the 6-line digest.
- `hooks.pre_tool_call` registered (terminal, timeout 5, fail_closed) + `shell-hooks-allowlist.json` entry. `hermes hooks doctor`: "All shell hooks look healthy". Hand tests: `ls` -> allow; `render_writer_pipeline.py ... --queue` -> block; same with `--yes-derrick` -> allow; `queue-remote.sh --dry-run` -> allow.
- Cron `morning-lab-digest` (id `1cd80ccc3b1a`, `0 8 * * *`, `--no-agent`, zero LLM calls), next run 2026-11-20 8:00 AM CT.

## Item 4 - DONE
- `~/.config/systemd/user/hermes-webui.service.d/20-media-roots.conf`: `MEDIA_ALLOWED_ROOTS` (`os.pathsep` ":") = `/home/evo/AI/5slock/libraries`, `/home/evo/AI/community/runs`, `/home/evo/AI/evo-x3/x3/community/runs`, `/home/evo/AI/render/_inputs`, `/srv/renders`. (The NAS run folder `/mnt/qnap/renders/runs` is not in the list; adding it widens WebUI access and needs Derrick's OK.)
- `systemctl --user restart hermes-gateway hermes-webui` -> both `active`.
- `hermes skills list`: `h3-render`, `h3-writer`, `h3-prompting`, `h3-parody-identity`, `flux-klein-prompting`, `lab-status`, `fleet-brain`, `pi-job`, `pixlstash-image-library` enabled; all 10 disabled names show `disabled`.
- Pytest (`test_prose_file_gate.py test_flux_h3_redteam.py test_beta7_convert.py`): 19 passed (full parody suite 577 passed).
- `hermes chat --oneshot -Q -q "Which skill do you use to render a video, and which to change code in a repo? ..."` -> `h3-render and pi-job` (model `flash-next-uncensored-v2`, thinking off).

## Derrick checks (Item 5)
Pending. Hermes is ready for Derrick's five WebUI checks (render ask -> still + full prompt + "Render this?", nothing queued; "write it yourself"; yes -> queue + inline 2x clip; small coding ask -> `pi-job code`; Miraclein still ask).
