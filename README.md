# EVO-X3 all-in-one snapshot (Nov 17, 2026 — U56 fixes + Halogen concurrency)

Each folder corresponds to one X3 branch from Gitea:

- `x3-render` (`ff1b41f` + U56 recompiled `writer_prompt.md` (`77/77 PASS`), Qwen `sampler_arm: Q` + `vision_model_alias: joycaption` in `config.yaml`, lean `OPERATOR.md`, `render-pi.sh` unified on `flash-next-uncensored` for zero GPU swaps, and `queue-remote.sh` AlienPc `:8446/queue` preflight)
- `x3-community` (`8377852` + complete U56 writer/builder/skill fixes: no `<Audio 1>` on named parodies, no `<Picture 1>` in `guide` mode, `[reference generation]` prefix on `ref` mode, `beat_sheet.json` persisted per clip, `wp_lint.HARD_STOP` wired for `cowgirl_check`/`stock_talk` + reference-manifest tag audit, `pick_template` 16:9 `beta7_int8HQ` routing, `resolve.py` indexed SQLite query, 5 skill contradictions resolved, and U56 pytest suite green)
- `x3-forge` (`69ea8be` + `ralph.sh` `-PiCwd`, process-group cleanup on `TERM`/`INT`/`EXIT`, `~/` skill remap; `run-u56-pass.sh`; `fix_plan.u56-item0.md`; Forge settings mirror of the live 131K compaction + `flash-next-uncensored` pins)
- `x3-bakeoffs` (`5370762`)
- `x3-pi-config` (`41068a4` + `scripts/patch-llama-swap-u56.py` adding 4-slot `flash-next-uncensored` + `HALOGEN_VISION_TOWER` + `flash-next-uncensored-sub` + `ttl: 300`, `llama-swap.yaml` mirror, Open WebUI forwarded-ip lock, staged proxy/sandbox/Playwright fixes)
- `alienpc-community` (`c85afa0`), `alienpc-render` (`7c219cc`), `alienpc-comfyui-config` (untouched on this X3/Render branch; AlienPc ComfyUI hardening lives separately on `feature/alienpc-only-remediation`)

## Applying on EVO-X3

Every file the installer overwrites is first copied to `<dir>/_archive/<name>.bak-20261117-u56bundle` (the first
backup is kept on re-runs). `bash apply-on-x3.sh evo-rollback` restores all of them.

### Step 1. Ralph loop fixes (as `evo`; no llama-swap restart)

```bash
systemctl --user stop u42-pixlstash-tagger.service   # if running: it swaps gemma4-heretic into the exclusive main group
bash apply-on-x3.sh evo-preview                      # your live ralph.sh has uncommitted edits: check nothing is lost
bash apply-on-x3.sh evo                              # installs ralph.sh, run-u56-pass.sh, fix_plan.u56-item0.md
```

Then do Item 0 one of two ways:

- **B (recommended). Install the Item 0 fixes directly:** `bash apply-on-x3.sh evo --with-tests` (prints `2 passed`), then
  tick `- [x] 0` in `~/AI/forge/ralph-community/fix_plan.md` and start the loop at item 1.
- **A. Let one headless pass do Item 0** (handoff §11.3 proof): replace `0a`/`0b` in `fix_plan.md` with Item 0 from
  `fix_plan.u56-item0.md`, keep the Render/Forge panes idle (live `flash-next-uncensored` is limited to 1 request until
  Step 2), and run `bash ~/AI/forge/ralph-community/run-u56-pass.sh 1`. The pass commits on the loop branch
  `ralph-<day>-<pid>-community` in `~/AI/_worktrees/`, not on live `x3-linux`. Bring it in before the next loop run, or
  that run's gate starts from the old tests and fails again:
  `git -C ~/AI/community merge --ff-only ralph-<day>-<pid>-community`

### Step 2. llama-swap (root; needs Derrick's yes for the restart)

```bash
sudo bash apply-on-x3.sh root-preview   # exact diff to /etc/evo-x3/llama-swap.yaml
sudo bash apply-on-x3.sh root-apply     # flash-next-uncensored: limit 4, HALOGEN_VISION_TOWER, -sub alias; joycaption/ref2va ttl 300
sudo systemctl restart llama-swap       # when /running shows nothing in flight
```

`root-apply` edits the live file in place (it never copies the repo `llama-swap.yaml`, whose `joycaption` block is
reconstructed), validates it with `llama-swap -validate`, skips the vision tower if its file is missing, and prints a
health check to run after the restart. The vision tower on the Huihui checkpoint is untested (U26 ran it text-only), so
run that health check and keep the printed restore command handy.

### Step 3. Render pipeline (as `evo`; only after Step 2 and the restart)

```bash
bash apply-on-x3.sh evo --with-render
```

Refuses to run until root-apply has been done and llama-swap restarted after it. Installs the U56 parody scripts, skills
and render files (`OPERATOR.md`, `config.yaml`, `writer_prompt.md`, `render-pi.sh`, `queue-remote.sh`), updates
`~/.pi/agent/models.json` (`flash-next-uncensored` image input when the vision tower is on, plus
`flash-next-uncensored-sub`) and the render pane's Gemma subagent pin, then runs the 77-rule gate and the parody tests.
If verification fails it stops and tells you to run `evo-rollback`. Restart the Render herdr pane afterwards.

Not changed by this bundle: the Sydney pane still runs `gemma4-heretic`, so using Sydney while Render or Forge is busy
swaps the exclusive `main` group.