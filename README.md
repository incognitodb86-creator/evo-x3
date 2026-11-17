# EVO-X3 all-in-one snapshot (Nov 17, 2026 — U56 fixes + Halogen concurrency)

Each folder corresponds to one X3 branch from Gitea:

- `x3-render` (`ff1b41f` + U56 recompiled `writer_prompt.md` (`77/77 PASS`), Qwen `sampler_arm: Q` + `vision_model_alias: joycaption` in `config.yaml`, lean `OPERATOR.md`, `render-pi.sh` unified on `flash-next-uncensored` for zero GPU swaps, and `queue-remote.sh` AlienPc `:8446/queue` preflight)
- `x3-community` (`8377852` + complete U56 writer/builder/skill fixes: no `<Audio 1>` on named parodies, no `<Picture 1>` in `guide` mode, `[reference generation]` prefix on `ref` mode, `beat_sheet.json` persisted per clip, `wp_lint.HARD_STOP` wired for `cowgirl_check`/`stock_talk` + reference-manifest tag audit, `pick_template` 16:9 `beta7_int8HQ` routing, `resolve.py` indexed SQLite query, 5 skill contradictions resolved, and U56 pytest suite green)
- `x3-forge` (`69ea8be` + `ralph.sh` `-PiCwd`, process-group cleanup on `TERM`/`INT`/`EXIT`, `~/` skill remap; `run-u56-pass.sh`; `fix_plan.u56-item0.md`; Forge settings mirror of the live 131K compaction + `flash-next-uncensored` pins)
- `x3-bakeoffs` (`5370762`)
- `x3-pi-config` (`41068a4` + `scripts/patch-llama-swap-u56.py` adding 4-slot `flash-next-uncensored` + `HALOGEN_VISION_TOWER` + `flash-next-uncensored-sub` + `ttl: 300`, `llama-swap.yaml` mirror, Open WebUI forwarded-ip lock, staged proxy/sandbox/Playwright fixes)
- `alienpc-community` (`c85afa0`), `alienpc-render` (`7c219cc`), `alienpc-comfyui-config` (untouched on this X3/Render branch; AlienPc ComfyUI hardening lives separately on `feature/alienpc-only-remediation`)

## Applying on EVO-X3

### 1. While U56 is open (as user `evo`; no llama-swap restart)

```bash
systemctl --user stop u42-pixlstash-tagger.service   # if running: it swaps gemma4-heretic into the exclusive main group
bash apply-on-x3.sh evo-preview                      # your live ralph.sh has uncommitted edits: check nothing is lost
bash apply-on-x3.sh evo                              # installs ralph.sh, run-u56-pass.sh, fix_plan.u56-item0.md
```

Then pick one:

- **A. Loop does Item 0** (meets handoff §11.3): replace `0a`/`0b` in `~/AI/forge/ralph-community/fix_plan.md` with Item 0
  from `fix_plan.u56-item0.md`, keep the Render/Forge panes idle, and run
  `bash ~/AI/forge/ralph-community/run-u56-pass.sh 1`.
  Stay on `flash-next-uncensored` (the default). Do not switch to `flash-next`: both are in the exclusive `main` group,
  so it would swap Halogen checkpoints (~25 s) every time the pass and a pane alternate.
- **B. Install only the Item 0 test fixes directly:** `bash apply-on-x3.sh evo --with-tests`, then tick Item 0 and start the loop at item 1.
- **C. One-Shot Full U56 + Render Pipeline Install (Fastest — skips waiting on Ralph Loop A):**
  `bash apply-on-x3.sh evo --with-render`
  Backs up every touched file to `_archive/*.bak-20261117-u56bundle`, installs all U56 `community` parody scripts + skills + `render` (`OPERATOR.md`, `config.yaml`, `writer_prompt.md`, `render-pi.sh`, `queue-remote.sh`), updates `/home/evo/.pi/agent/models.json` (`input: ["text", "image"]` + `flash-next-uncensored-sub`), and runs both the 77-rule compiler check and the `pytest` suite automatically.

### 2. After U56 closes and Derrick approves a llama-swap restart

```bash
sudo bash apply-on-x3.sh root-preview   # prints the exact diff to /etc/evo-x3/llama-swap.yaml
sudo bash apply-on-x3.sh root-apply     # patches flash-next-uncensored (limit 4 + HALOGEN_VISION_TOWER + -sub alias) and joycaption/ref2va ttl 300
sudo systemctl restart llama-swap       # when /running shows nothing in flight
```

`root-apply` edits the live file in place and never copies the repo `llama-swap.yaml` (that mirror's `joycaption` block is
reconstructed and unverified). After the restart, add `flash-next-uncensored-sub` to `~/.pi/agent/models.json` from
`x3-pi-config/config/pi-evo/models.json.example` before pointing any `subagents.defaultModel` at it.
