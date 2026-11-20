---
title: "REA-video -> FLUX.2 Klein (RefMod + LoRA) -> H3Max Beta 7 parody remake pipeline (corrected plan)"
date: 2026-11-20
type: plan
artifact_contract: ce-unified-plan/v1
source: Derrick's draft blueprint (rea-flux-h3max-b7-parody-auto-final, 2026-11-20 ~9:19 AM CT); original PDF removed from git per Derrick (~9:45 AM CT) to avoid confusing local LLMs with its 21 outdated claims. This PLAN.md + PIJOB-TASKS.md are the single source of truth.
author: Opus (VS Code, Windows clone). PLAN ONLY. Nothing applied on the X3 or AlienPc.
---

# REA parody remake pipeline (corrected plan)

Derrick, 2026-11-20 ~9:19 AM CT: "This portion will validate our coding pipeline works and i want this part done by
our local llm to test and verify the coding work space works and can implement this plan. Then we will use our render
workspace to test out if everything works as this will verify both flux and h3max with refmods and lora."
~9:21 AM CT: "dont specify strictly sfw, it can be nsfw".

So this plan has three parts:

1. **Coding workspace test (build):** the local LLM writes the code. Derrick asks in the Hermes `code` chat, Hermes runs
   one `pi-job code` per unit (C1-C7 in [PIJOB-TASKS.md](./PIJOB-TASKS.md)), pi commits each unit with its tests.
   Max reviews and merges. Opus (this clone) wrote only the plan, the unit specs, the queue-guard update and the
   render skill. The units are small on purpose: one unit = one `pi-job code` run (1 h cap) = one commit.
2. **Render workspace test (use):** the Hermes render chat runs Flux and H3Max with RefMods and LoRAs, then a 2-shot
   REA remake with the new `rea-remake` skill. Steps and pass checks: [RENDER-TEST.md](./RENDER-TEST.md).
3. **Optional extras** (blueprint U5: FaceRefine, PromptSync): separate yes each, after 1 and 2 pass.

Content scope: adults 18+ only, hard stop on any youth cue (existing 18+ gates). NSFW is allowed. U56 Decision #2
stays: a named celebrity parody never gets a celebrity voice audio ref; OC lanes (FCSydny, FCMegan) may use OC voice
RefMods as today.

## What changed from the blueprint (red team, 2026-11-20 ~9:30 AM CT)

Every row is VERIFIED against mono `bd32066a` or a RESULT file unless marked ASSUMPTION.

| # | Blueprint says | Fact | This plan |
|---|---|---|---|
| 1 | "Strictly SFW" | Derrick ~9:21 AM CT: NSFW allowed | Adults 18+ only; NSFW allowed |
| 2 | AlienPc ComfyUI 0.38.0 | `comfyui_auto` reports 0.46.0 ([R6-RESULT](../BENCH-ALIENPC-1/R6-RESULT.md)) | 0.46.0 |
| 3 | Aliases `flash-next-render-strict` / `-writer` / `-think` | Not real. H7 adds `flash-next-aux` (0.35, no think), `flash-next-render` (0.7/0.8/20, no think), `flash-next-code` (thinking) ([H7 brief](../UNI-APPLY-X3-HERMES-WORKSPACES/BRIEF.md)) | strict -> `flash-next-aux`, writer -> Hermes render chat on `flash-next-render`, think -> not used |
| 4 | Executor `coding-qfn`, Swift "ESP OFF" | Hermes profile is `code`; `pi-job` uses `coding_swift15_iq3s_esp` (ESP on, t2764u), thinking medium, X3 fallback low (`config/bin/pi-job`) | Hermes `code` chat -> `pi-job code` |
| 5 | Repo at `/home/evo/AI/evo-x3` | Does not exist (MONO-S5 not done); live code is `/home/evo/AI/community` (x3-community checkout) | pi works in a mono clone `/home/evo/AI/_worktrees/rea-parody` (C0); Max deploys after merge (C8) |
| 6 | The script calls an LLM writer for FLUX prompts and Beta 7 prose (Links 3 and 5) with prefill priming | H9: Hermes writes prompts itself; `h3-render` forbids calling a writer model; Path A writer is held (W4) | Script is deterministic. Hermes writes `flux_prompt.txt` and `hermes_prose.txt` per shot (rea-remake skill). Script gates and queues |
| 7 | Header-free `[Shot 1]` Beta 7 prose | Live `h3-writer` and workspace `AGENTS.md` use 4 headers; the U56 #1 wording conflict is open | Hermes writes what `h3-writer` says; `render_writer_pipeline.py --prose-file` + `beta7_convert` normalize |
| 8 | RefMod retention 0.7, LoRA 0.65 hardcoded | M6: `flux_still.py` defaults to `fully_preserved (1.0)`; the likeness A/B decides | Use `flux_still.py` defaults and its `--hybrid` recipe; no hardcoded retention |
| 9 | FP8 fallback `Miraclein_4.3_9b_FP8`, auto-swap on error | Live base is 4.5 NVFP4; 4.5 FP8 download approved (D6c) for A/B arm L7 | No auto-swap. Base follows the M6 A/B pick |
| 10 | New "frozen" FLUX templates | S2: only allowlisted production templates; new ones stay `*.candidate.api.json` | `flux_rea_edit.candidate.api.json`, `flux_rea_pose.candidate.api.json` |
| 11 | Install rea-video on X3 with `uv venv` + `pip` | Not on X3 (RV0 open). Installed on AlienPc `C:\Users\derek\forge\tools\rea-video` @ `e3858539` ([HANDOFF-forge](../../alienpc/community/runs-setup/reavideo/install/HANDOFF-forge.md)). `uv venv` has no pip | First test decomposes on AlienPc (Q-RP1). X3 install later uses `uv pip install` |
| 12 | Register `h3max-10strip-beta7` capability | RV1 YAML already installed on X3 ([UNI-APPLY-X3-A](../UNI-APPLY-X3-A/RESULT.md) item 3) | Do not redo |
| 13 | New shot packing / snap / split code | Exists: `build_request.align_h3_frames` (17n+5, cap 243) and `h3max_bridge` `pack_shots`, `slice_long_shots`, `best_voice_window`, `strip_video_audio` | Reuse. Fix the two known bridge bugs in the new path: per-shot seed, keep the voice window `start` ([REA-VIDEO-VAL30S-RESULT](../BENCH-ALIENPC-1/REA-VIDEO-VAL30S-RESULT.md)) |
| 14 | Wrappers `hermes-render/bin/rea-intake.sh`, `hermes-coding/bin/run-pytest-gate.sh`, `gitleaks-diff.sh`, `check-render-workspace.sh` | None exist (outside Opus brief, blocked) | No wrappers. Skill calls the venv python directly. gitleaks runs on the box pre-push |
| 15 | W1 quality gate `D:\AI\quality-gates` (DOVER) | No record of it on mono (ASSUMPTION: not installed) | Dropped; Derrick's eye + existing objective checks |
| 16 | Copy master to `/srv/renders`, `SCOREBOARD.md` | `sync-renders` already publishes 2x clips; no SCOREBOARD exists | `assemble --publish` copies the master only; no scoreboard |
| 17 | (not covered) | The Hermes queue guard did not know a new queuing script | `guard-render-queue.sh` now blocks `rea_parody_remake.py ... --queue` / `queue` without `--yes-derrick` (this commit) |
| 18 | pi installs into `/etc`, `/home/evo/.rea-video` | `evo` has no sudo from a pi-job (X3-A item 10) | pi units touch repo files only; installs are Max steps |
| 19 | Push Gitea first, then GitHub | Repo rule (Derrick 2026-11-19): GitHub first, Max mirrors | Max merges `pi/rea-parody` into mono, pushes GitHub, mirrors |
| 20 | Stage 5 uses frozen copies of `named_parody` / `b2_refmod` | `fill_request.pick_template()` routes (t3013u: original 1-pass); `b2_refmod` is AlienPc-only | `render_writer_pipeline.py --prose-file` picks the template as today |
| 21 | Mode C element-crop RefMod (`Klein9RefModExtract`) | Untested here | Deferred until after the M6 A/B |

## Architecture (who does what)

| Stage | Who | Command / skill | Output |
|---|---|---|---|
| 1 Decompose | AlienPc rea-video (Q-RP1), or X3 after RV0 | `rea-video decompose <clip> -o <out> --lang en` | `breakdown.json`, `shots/*.jpg`, `stems/*.wav` |
| 1b Beats | script | `rea_onset_probe.py` (numpy only) | `onset_beats.json` |
| 2 Plan | script | `rea_parody_remake.py plan` | per-shot folders, `raw_still_read.json` (18+ gate), `shot_brief.json`, `parody_cast_lock.json`, `batch_card.md` |
| GO | Derrick | one batch yes in the render chat | (h3-render batch rule) |
| 3a FLUX prompts | Hermes render chat | `flux-klein-prompting` skill | `shots/shot_XXX/flux_prompt.txt` |
| 3b FLUX stills | script | `rea_parody_remake.py flux <batch> --queue --yes-derrick` (calls `flux_still.py`) | `shots/shot_XXX/_inputs/shot_XXX_edited.png` |
| 4/5a Beta 7 prose | Hermes render chat | `h3-writer` skill, from the edited still + `shot_brief.json` | `shots/shot_XXX/hermes_prose.txt` |
| 5b Gate + build | script | `rea_parody_remake.py build` (calls `render_writer_pipeline.py --prose-file`, dry run) | per-shot `build_report.json`, `clip/request.api.json` |
| 5c Render + 2x | script | `rea_parody_remake.py queue <batch> --yes-derrick` (calls `queue-remote.sh` per shot, sequential) | per-shot 2x `clip/*.mp4` |
| 6 Assemble | script | `rea_parody_remake.py assemble <batch> [--bgm] [--publish]` (calls `rea_color_match.py`) | `final_2x.mp4` |

Batch folder: `/home/evo/AI/community/runs/rea_<YYYYMMDD_HHMM>_<slug>/` (inside `MEDIA_ALLOWED_ROOTS` and the guard's
runs root). Each shot has `shots/shot_XXX/` as the H3 run dir and `shots/shot_XXX/flux/` as the FLUX run dir, so
`_render_order.json` and `prompt.txt` never collide.

CLI contract (the units must keep it; the skill depends on it):

```text
rea_parody_remake.py plan     <batch_dir> --rea-dir <dir> (--names "<Actor as Character>" | --character FCSydny|FCMegan)
                              [--lane parody|oc] [--aspect 9:16|16:9] [--shots shot_001,shot_002]
rea_parody_remake.py flux     <batch_dir> [--shot shot_001] [--queue --yes-derrick]
rea_parody_remake.py build    <batch_dir> [--shot shot_001]
rea_parody_remake.py queue    <batch_dir> --yes-derrick [--shot shot_001]
rea_parody_remake.py assemble <batch_dir> [--bgm] [--publish]
rea_parody_remake.py status   <batch_dir>
```

Every subcommand prints one final line: `READY ...`, `DONE ...`, `NOT_READY <reason>` or `STUCK <shot> <reason>`.

## Update 2026-11-20 ~2:30 PM CT

C0 done (U59). C1–C7 coded by the local LLM via `pi-job` (all DONE); C8 check + test fixes on `pi/rea-parody` `4b2d142`. Opus review and fixes are PR `#6` (test PNGs removed, `tmp_path` fixture, BPM range, WAV width, shot ids, `rea_pose` pose image). C8 deploy, C9 and R1–R4 wait on Derrick's go ([NEXT-STEPS.md](../opus/NEXT-STEPS.md) section 5).

## Units

| ID | Who | What | Test / gate | Rollback |
|---|---|---|---|---|
| C0 | Max (live, X3 lease) | Clone mono for `evo` into `/home/evo/AI/_worktrees/rea-parody`, branch `pi/rea-parody`; check the render venv has numpy, Pillow, pytest | `git -C ... status` clean; `python3 -c "import numpy, PIL, pytest"` | `rm -rf` the worktree |
| C1-C7 | Local LLM via Hermes `code` chat -> `pi-job code` | One unit each, specs in [PIJOB-TASKS.md](./PIJOB-TASKS.md) | Each unit's pytest line passes; pi-job `DONE` with 1 commit | `git revert` the unit commit on `pi/rea-parody` |
| C8 | Max | Review `pi/rea-parody` (diff + full parody pytest + gitleaks), fast-forward mono, push GitHub, mirror; copy the new `x3/community` files and the updated guard into the live X3 trees with backups | Same pytest on the live tree; `hermes hooks doctor` healthy | Restore the `_archive/20261120_rea/` backups |
| C9 | Max | Install the `rea-remake` skill for the render profile (`~/.hermes/skills/creative/rea-remake/SKILL.md`) | `hermes skills list` shows it enabled in default, disabled in `code` | Archive the skill folder |
| R1-R4 | Derrick in the Hermes render chat | [RENDER-TEST.md](./RENDER-TEST.md) | Eye + listed checks | Nothing live to undo (run folders only) |

Order: H7 apply (`scripts/apply-hermes-workspaces.sh`) -> C0 -> C1..C7 -> C8 -> C9 -> R1..R4. The M6 Flux likeness A/B on
AlienPc can run any time before R1; its pick sets the Flux defaults R1 uses.

## Q-cards for Derrick (answer in chat; Max records the id)

- **Q-RP1:** where to decompose the test clip. **Default: AlienPc** (rea-video already installed, CPU only), then copy
  the output folder to the X3 batch. Other option: install rea-video on the X3 first (RV0, live step).
- **Q-RP2:** the test clip. Default: a short 2-shot clip Derrick picks (under 15 s), lane `parody` with Sydney Sweeney.
- **Q-RP3:** Beta 7 prose layout. Default: whatever the installed `h3-writer` produces (4 headers today); the U56 #1
  wording conflict stays open.
- **Q-RP4:** blueprint U5 nodes (BSAI FaceRefine, Genkai PromptSync). Default: later, separate yes each.
