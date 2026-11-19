# Hermes Skill Prune & Adaptation List (H4)

Canonical copy for `hosts/x3/hermes/`. Applied on EVO-X3 (`/home/evo/.hermes/skills/`) by X3 Forge under the X3 lease after Max imports this commit.

- Source snapshot: `hosts/x3/live/hermes/skills/all-skills.txt` @ `eabc8c7` (46 installed skills on Hermes `v0.23.2`: 44 stock + 2 custom `pi-job`, `pixlstash-image-library`).
- Result: **27 removed** (archived out of `~/.hermes/skills/`), **20 kept** (17 stock + 2 existing local custom: `pi-job` adapted in `hosts/x3/hermes/skills/pi-job/SKILL.md`, and `pixlstash-image-library` from H8 + 1 reserved custom: `flux-klein-prompting`, installed at FX1 apply).
- Reserved / planned (do **not** prune when added later): `h3-writer` (from the held `records/hermes-direct-render/PLAN.md` U0-U9 track; not created or modified here); `flux-klein-prompting` (installed at FX1 apply from `x3/community/skills/flux-klein-prompting/SKILL.md`).

## Guardrails & X3 Adaptations

1. **No unguarded ComfyUI MCPs:** never install ComfyUI MCPs or external video tools that bypass the 18+ check, Derrick's explicit in-chat yes / ntfy approval, or the RTX 2x upscale publish gate (`/srv/renders`).
2. **X3 paths:** `/usr/local/bin/pi-job`, `~/AI/community/runs/`, `/srv/renders` (QNAP-backed 2x-only publish), `~/.hermes/cache/documents/native-inputs/` (attached stills), local SearXNG at `http://127.0.0.1:8888`.
3. **Beta 7 prompt contract (`U56 Decision #1`):** final `10Eros-Max Beta 7` prompts must not contain `integrated_multimodal_description:`, `overall_soundscape:`, or `non_diegetic_music:`; sound is plain diegetic cues at the end of the description.
4. **H2 web/browser guard:** kept web/research skills (`grounded-citations`, `blocked-page-recovery`) use local SearXNG (`http://127.0.0.1:8888`) and stay subject to the H2 network-layer SSRF blocklist (no loopback/tailnet/link-local fetches except SearXNG).
5. **No unsupervised pushes:** `github` skill is read/PR-prep only on X3; pushes and Gitea mirrors follow Derrick/Max rules.

## REMOVE (27 skills — archive to `~/.hermes/skills-archived/`)

| # | Skill path (`skills-installed.txt`) | Reason |
|---|---|---|
| 1 | `./apple/apple-notes/SKILL.md` | macOS-only; X3 is Fedora 44 Linux |
| 2 | `./apple/apple-reminders/SKILL.md` | macOS-only |
| 3 | `./apple/findmy/SKILL.md` | macOS-only |
| 4 | `./apple/imessage/SKILL.md` | macOS-only |
| 5 | `./autonomous-ai-agents/claude-code/SKILL.md` | Unused external CLI; X3 uses `pi-job` / `Forge-X3` |
| 6 | `./autonomous-ai-agents/codex/SKILL.md` | Unused external CLI; X3 uses `pi-job` / `Forge-X3` |
| 7 | `./autonomous-ai-agents/computer-use/SKILL.md` | Headless server; no GUI desktop session for Hermes |
| 8 | `./creative/baoyu-infographic/SKILL.md` | Unused SaaS/infographic bloat |
| 9 | `./creative/claude-design/SKILL.md` | Unused Anthropic-specific design skill |
| 10 | `./creative/manim-video/SKILL.md` | Not installed on X3; causes video requests to misroute away from `pi-job` |
| 11 | `./creative/p5js/SKILL.md` | Unused browser sketch bloat |
| 12 | `./creative/popular-web-designs/SKILL.md` | Unused web-design catalog bloat |
| 13 | `./creative/songwriting-and-ai-music/SKILL.md` | Unused AI music SaaS skill |
| 14 | `./email/email-inbox-triage/SKILL.md` | No email/IMAP configured on X3 |
| 15 | `./email/himalaya/SKILL.md` | No `himalaya` CLI configured on X3 |
| 16 | `./media/youtube-content/SKILL.md` | Unused YouTube creator workflow |
| 17 | `./note-taking/obsidian/SKILL.md` | No Obsidian vault on X3 |
| 18 | `./productivity/google-workspace/SKILL.md` | Unused Google Workspace SaaS |
| 19 | `./productivity/maps/SKILL.md` | Unused Maps API/SaaS |
| 20 | `./productivity/meeting-action-items/SKILL.md` | Unused meeting SaaS workflow |
| 21 | `./productivity/microsoft-office/SKILL.md` | Headless Linux; no MS Office desktop |
| 22 | `./productivity/product-price-monitor/SKILL.md` | Unused e-commerce monitor |
| 23 | `./productivity/teams-meeting-pipeline/SKILL.md` | Unused Teams/SaaS pipeline (named in F4 H4) |
| 24 | `./productivity/weekly-review-planning/SKILL.md` | Unused personal productivity template |
| 25 | `./research/competitor-news-monitor/SKILL.md` | Unused business/SaaS monitor |
| 26 | `./social-media/xurl/SKILL.md` | Unused X/Twitter CLI |
| 27 | `./software-development/dogfood/SKILL.md` | Unused browser-QA dogfooding bloat |

## KEEP (20 skills, including 1 reserved)

| # | Skill path (`all-skills.txt`) | Mode | X3 note |
|---|---|---|---|
| 1 | `./autonomous-ai-agents/hermes-agent/SKILL.md` | stock | Hermes self-reference; `SOUL.md` and `pi-job` take precedence |
| 2 | `./creative/architecture-diagram/SKILL.md` | stock | Local architecture diagrams |
| 3 | `./creative/ascii-video/SKILL.md` | stock + local edits | Preserve existing local edits (`local-edits-to-bundled-skills.diff`); real video renders still route to `pi-job` |
| 4 | `./creative/humanizer/SKILL.md` | stock | General writing helper |
| 5 | `./devops/sdlc-review/SKILL.md` | stock | Pairs with `pi-job review` |
| 6 | `./pi-job/SKILL.md` | **custom (adapted)** | Updated in `hosts/x3/hermes/skills/pi-job/SKILL.md` (X3 paths, `U56 Decision #1`, `/srv/renders`, no unguarded Comfy MCP) |
| 7 | `./pixlstash-image-library/SKILL.md` | **custom (H8, done)** | Local PixlStash image library skill; keep untouched |
| 8 | `./productivity/document-to-action-items/SKILL.md` | stock | Local text utility, no external SaaS |
| 9 | `./productivity/pdf/SKILL.md` | stock | Local PDF inspection |
| 10 | `./research/arxiv/SKILL.md` | stock | Research paper lookup |
| 11 | `./research/grounded-citations/SKILL.md` | stock | Pairs with H2 local SearXNG (`http://127.0.0.1:8888`) |
| 12 | `./software-development/codebase-inspection/SKILL.md` | stock | Local repo inspection |
| 13 | `./software-development/github/SKILL.md` | stock | `gh`/GitHub inspection; no unsupervised pushes |
| 14 | `./software-development/requesting-code-review/SKILL.md` | stock | Pairs with `pi-job review` |
| 15 | `./software-development/simplify-code/SKILL.md` | stock | Pairs with `pi-job code` |
| 16 | `./software-development/spike/SKILL.md` | stock | Prototyping |
| 17 | `./software-development/systematic-debugging/SKILL.md` | stock | Debugging |
| 18 | `./software-development/test-driven-development/SKILL.md` | stock | Pairs with H5 `make check-all` / pytest |
| 19 | `./web/blocked-page-recovery/SKILL.md` | stock | Pairs with H2 web/browser under SSRF blocklist |
| 20 | `./flux-klein-prompting/SKILL.md` | **custom (reserved)** | FLUX.2 Klein / Miraclein 4.5 stills prompting; installed at FX1 apply from `x3/community/skills/flux-klein-prompting/SKILL.md` |

## Reserved / Planned (do not prune)

- `h3-writer` (held under `records/hermes-direct-render/PLAN.md` U0-U9).
- `flux-klein-prompting` (installed at FX1 apply to `/home/evo/.hermes/skills/flux-klein-prompting/SKILL.md`).

## Apply & Verify (X3 Forge, under X3 lease)

1. Backup: `cp -a /home/evo/.hermes/skills /home/evo/.hermes/skills.bak-h4-$(date +%F-%H%M%S)`
2. Archive the 27 removed skill directories into `/home/evo/.hermes/skills-archived/` (preserving relative subpaths; remove empty parent dirs like `apple/`, `email/`, `media/`, `note-taking/`, `social-media/`).
3. Install adapted `pi-job`: `install -m 0644 -o evo -g evo hosts/x3/hermes/skills/pi-job/SKILL.md /home/evo/.hermes/skills/pi-job/SKILL.md`
4. Verify: run Hermes skill loader check (`hermes skills list` / frontmatter validation) and `SKILL_SMOKE_OK`; confirm 19 active skills before FX1 apply (20 including `flux-klein-prompting` once installed at FX1 apply), 0 broken paths, and `pi-job`, `pixlstash-image-library`, and `flux-klein-prompting` loaded.
5. Re-snapshot with `scripts/snapshot-live-setup.sh` so `hosts/x3/hermes/skills-installed.txt` matches live.
6. Rollback: restore `/home/evo/.hermes/skills` from the `skills.bak-h4-*` backup.
