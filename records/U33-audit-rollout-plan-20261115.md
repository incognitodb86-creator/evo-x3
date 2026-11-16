# U33 — EVO-X3 audit + official rollout plan (2026-11-15, 8:56 PM CT)

Asked by Derrick t1835u / t1836u. **Read-only audit; nothing was changed, restarted, loaded or requested.** U21 benchmarks + deep-research bake-off (Antigravity, agy PID 125527) hold the lease and were running during the audit (flash-next-gufo slot loaded for Step 3A).

Order (Derrick): U21 benchmarks/bake-off → **this audit + plan** → Derrick's yes → implementation → cleanup → live Fedora backup to QNAP (no weights) last.

---

## 1. Current state (live, 8:53–9:00 PM CT)

**Host:** Fedora 44, kernel 7.3.3-200.fc44, cmdline `amdgpu.gttsize=122880 ttm.pages_limit=31457280`. UMA now 1 GiB (`mem_info_vram_total` 1.0 GiB), GTT 120 GiB (96 GiB in use during bench). RAM 124 GiB, zram 8 GiB. tuned `accelerator-performance`. Root LV 1.7T, 814G used (49%); `/srv/models` 404G.

**Engines / tools**
| Item | Version / pin |
|---|---|
| llama-swap | v272 (802f1c4), `/usr/local/bin/llama-swap`, wrapper `/usr/local/bin/evo-llama-swap` (empty-key guard, exit 78), unit `llama-swap.service` + drop-in `10-empty-key-guard.conf`, listen 127.0.0.1:8080 |
| llama.cpp | kyuz0 strix-halo Vulkan RADV build 12405 (9f26fe11c) `@sha256:9a9e4d8f…` |
| Gufo | gufo-runtime 0.34.0 `@sha256:49b1fce4…` |
| Halogen | halogen-flash-server 0.20.5 `@sha256:30412723…` |
| pi | 1.5.2 (`~/.local/bin/pi`, `@earendil-works/pi-coding-agent@1.5.2`) — **already installed** |
| Node | v24.22.1 (`/usr/bin/node`) — U27 noted 24.18.0; TLS update appears done (verify Plannotator warning gone) |
| pi packages (global) | pi-subagents 0.83.1, cc-safety-net 2.7.0, rpiv-todo 2.15.0, pi-web-access 0.46.0 |
| Antigravity CLI | agy 1.5.9 |
| herdr | 0.9.5 installed, not running (no `--remote`/phone bridge on X3) |
| Open WebUI | Quadlet `/etc/containers/systemd/open-webui.container`, digest-pinned `@sha256:59b912d4…`, 127.0.0.1:3000, signup off |

**llama-swap live config** `/etc/evo-x3/llama-swap.yaml` (0644, placeholders only; 23 `.bak-*` beside it; etckeeper HEAD 9a3b135 U31). Global: `healthCheckTimeout 900`, `captureBuffer 0`, `includeAliasesInList true`, `globalConcurrencyLimit 6`, 5 apiKeys from `/etc/evo-x3/llm.env`. Groups: `main` (swap, exclusive): flash-next, flash-next-gufo, flash-next-uncensored, gemma4-heretic, qwen27b; `small` (persistent, non-exclusive): embed-small.

| Slot | Engine | Model file / quant | Ctx | KV | Parallel | Batch | Other | Sampling | ttl | Aliases |
|---|---|---|---|---|---|---|---|---|---|---|
| flash-next | Halogen 0.20.5 | `/srv/models/flash-next-halogen` (native HGN v2) | 262144 | engine default | concurrencyLimit 4 | default | `--ipc=host`, memlock unlimited, effort medium | T1.0 / p0.95 / k20 | 86400 | flash-next-sub (useModelName flash-next) |
| flash-next-uncensored | Halogen 0.20.5 | `/srv/models/flash-next-uncensored-hgn/model.hgn` (U26 Huihui) | 262144 | default | 1 | default | effort medium | T1.0 / p0.95 / k20 | 3600 | — |
| flash-next-gufo | Gufo 0.34.0 | Qwen3.8-Flash-Next UD-Q4_K_XL (4 shards) + MTP Q8_0 | 262144 | default | sessions 1 | default | `--speculative mtp`, cache-ram 2 GiB, preserve-thinking on, effort medium | engine default | 86400 | — |
| gemma4-heretic | llama.cpp b12405 | gemma-4-26B-A4B-it-heretic Q8_0 + unsloth mmproj BF16 | 524288 total (-np 2 → 262144/slot) | f16 (no -ctk/-ctv) | np 2 / concurrencyLimit 2 | -b 2048 -ub 2048 | `-fa on --jinja --load-mode none --reasoning-format deepseek`, image tokens 560–1120, slots endpoint on | T1.0 / p0.95 / k64 | 3600 | gemma4-heretic-sub (useModelName gemma4-heretic) |
| qwen27b | Gufo 0.34.0 | Qwen3.8-27B UD-Q8_K_XL + DFlash2 Q4_K_M draft | 262144 | default | sessions 2 / concurrencyLimit 2 | default | `--speculative dflash2`, cache-ram 2 GiB | engine default (pi sends T1.0/p0.95/k20/minp0) | 1800 | — |
| embed-small | llama.cpp b12405 | nomic-embed-text-v1.5 Q8_0 | 8192 | — | — | -b/-ub 8192 | `--embeddings --rope-scaling yarn --rope-freq-scale 0.75 --no-slots`, port 8083 | — | 86400 | — |

**pi** `~/.pi/agent/models.json` (0600, apiKey present — not printed): provider `x3-local` → `http://127.0.0.1:8080/v1`, `openai-completions`. Models: gemma4-heretic (text+image, reasoning true, ctx 262144, Gemma sampling, `thinkingFormat qwen-chat-template`, `supportsReasoningEffort false`), gemma4-heretic-sub (reasoning false, maxTokens 4096), qwen27b, flash-next (ctx 262144), flash-next-sub (ctx 131072). **No entries for flash-next-gufo, flash-next-uncensored, embed-small.** `settings.json`: default `x3-local/gemma4-heretic`, thinking off, subagents default `x3-local/gemma4-heretic`, telemetry off, retry 2, provider timeout 1200 s. `auth.json`, `models-store.json` 0600. 10 `models.json.bak-*` (0600). Global `AGENTS.md` = untrusted-content rules (Alfred card t498s2271). `pi-permissions.jsonc` + 2 baks.

**Chats** (`~/evo-x3/pi-chats/`, README says not production):
- Render `render-pi.sh` → `~/AI/render/x3/render-pi.sh`: x3-local/gemma4-heretic, `--thinking medium`, `--no-extensions` + 5 explicit `-e`, `--no-mcp --no-skills` + 9 render skills, `--no-context-files --append-system-prompt ~/AI/render/AGENTS.md`.
- Sydney `sydney-pi.sh`: x3-local/gemma4-heretic, `--thinking medium`, cwd `~/AI/sydney` (empty; persona not on X3). Contents of Sydney files not read beyond model/flag lines.
- Forge `forge-pi.sh`: cwd `~/AI/forge`, x3-local/flash-next, **no `--thinking` flag** → inherits `defaultThinkingLevel: off` from `~/AI/forge/.pi/settings.json` (thinkingBudgets 512/1024/2048/4096). Project packages: permission-system, pi-memory, plannotator, pi-canvas, pi-say, CE plugin @34492307 (12 skills off), workspace-history.
- Phone: not set up on X3 (herdr/pi-mobile bridge gated to cutover).

**Services:** llama-swap, open-webui, tailscaled, firewalld, sshd, tuned, smartd, auditd running. Timers: `evo-x3-kuma-push` (1 min, Kuma on QNAP), `evo-x3-config-backup` (daily 00:00). ntfy / Uptime Kuma / Vaultwarden are **not** on the X3 (envs in `/etc/evo-x3/` are client creds for QNAP-hosted services).
**Secrets present** in `/etc/evo-x3/` (all root 0600): llm.env, openwebui.env, gitea.env, hf.env, kuma.env, ntfy.env, pihole.env, plex.env, qnap.cred, unifi.env, vaultwarden.env.

**Security:** sshd `PermitRootLogin no`, `PasswordAuthentication no`, kbd-interactive no, but `X11Forwarding yes`, `MaxAuthTries 6`, listens 0.0.0.0/::. firewalld zone FedoraServer on wlp99s0: **cockpit**, dhcpv6-client, ssh. sudoers `/etc/sudoers.d/90-max-temp` = `derekboone ALL=(ALL) NOPASSWD: ALL` (stays until Derrick says). Tailscale Serve: `https://evo-x3-1…` → 127.0.0.1:8080 (llama-swap, key-gated), `:8443` → 127.0.0.1:3000 (Open WebUI). Tailnet peers: alfred-box (offline 7d), old `evo-x3` Windows node (offline 12h), `grokbot-user-288846804` (offline 10h).

**Git:**
- `~/evo-x3` — **not a git repo** (no `.git`). The plan file could not be committed (see §9).
- `~/AI/render` — HEAD 513fd09 (U31); remote only `alienpc-bundle` (file bundle); untracked `stills/` (by design).
- `~/AI/community` — HEAD ef420c8; remote only `alienpc-bundle`; 14 dirty entries (actions.log modified; untracked skills, prompts, references, queue scripts, `_archive/alienpc-only/`, `templates/faces/FC_SYDNEY.api.json`).
- `~/AI/forge`, `~/.pi/agent` — not repos.
- `/etc` etckeeper — HEAD 9a3b135, 7 uncommitted changes.
- **No Gitea remote on any repo** (gitea.env present with URL + token).

**Leftovers:** `/tmp/u31-stage/` (1.1M), `/tmp/u31-webui-count.py`, `~/u31-render-sub/` (84K) incl. `hdr` (0600, 72 B — likely an auth header; **not read**), `~/u29-parallel/`, `~/u6-262k/`, `~/evo-x3/llama-swap_272_linux_amd64.tar.gz`, `~/evo-x3/llama-swap.yaml` (stale rev-8 copy, differs from live), `~/evo-x3/stage-src`, `model-tests-fail1.*`, `~/.pi/agent/dummy_run/`, rollback weights (`Gemma-4-26B-A4B-Heretic.mmproj-Q8_0.gguf`, `Qwen3.8-27B-UD-Q4_K_XL.gguf`), `~/rocm` 9.9G.

**Open items in records:** U6 262K 3-run passed (U31/MF-10, `~/u6-262k/`); U26 HGN slot live but uncensored route not benchmarked in U21 scope (check); U29 parallel 16/16 pass; U31 deferred SF-03 (container persistence), SF-04 (Halogen effort vs qwen-chat-template; heretic-sub still emits thinking server-side), SF-05 (SearXNG home: `web-search.json` → QNAP 192.168.0.147:8888), SF-06 (drop `amdgpu.gttsize`), SF-07 (Render compaction reserve 24K vs ~95K); U22 Open WebUI model list not checked; U23 #11 Render relative run-path bug (also AlienPc); AlienPc still-guard patch `~/AI/_xfer/alienpc-patches/still-guard-rundir-20261115.patch` not applied; Flash-Next mmproj not downloaded (~0.9 GB, optional); Forge launcher thinking level unset; U27 Phase 3 swap guard held (Derrick: skip pi-model-swap guard, t1800u).

## 2. Gaps and risks (vs official cards, llama.cpp docs, community practice)

| # | Gap | Sev | Fix |
|---|---|---|---|
| G1 | No Gitea backup of anything; `~/evo-x3`, `~/AI/forge`, pi config not under git at all | High | Step 9 |
| G2 | `~/evo-x3/llama-swap.yaml` is a stale rev-8 copy (32K ctx Gufo flash-next, old heretic flags). Anyone reading the repo copy gets wrong settings | High | Replace with sanitized copy of live config; live file is source of truth |
| G3 | Thinking control mismatch: gemma4-heretic(+sub) use `thinkingFormat qwen-chat-template` with Gemma 4; U31 saw heretic-sub still thinking with "off". Halogen effort vs pi `qwen-chat-template` unconfirmed (SF-04) | High (Render/Sydney/subagent cost + latency) | Verify per-slot what toggles thinking (`chat_template_kwargs.enable_thinking` / `reasoning_effort`), set pi compat per slot; heretic-sub server-side default off via separate llama-swap `filters`/model or `--reasoning-budget 0` alias |
| G4 | flash-next `concurrencyLimit 4` at 262K: MF-09 says Halogen KV pool ≈ 524K, so 4×262K overcommits. U29 16/16 passed only at modest prompt sizes | Med | Keep 4 for subagents but cap flash-next-sub at 128K (already in pi) and test 2×200K + 2×32K; else limit 2 |
| G5 | pi models.json lacks flash-next-gufo / flash-next-uncensored / embed-small; pi `contextWindow` 262144 per model but llama-swap Heretic slot is 262144/slot (OK) | Low | Add only the slots kept after U21 |
| G6 | Forge launcher has no thinking level (inherits off). Qwen3.8 card practice for coding agents is thinking on | Med | `--thinking medium` (OPEN: U21/bake-off decides low vs medium) |
| G7 | Qwen sampling: slots use T1.0/p0.95/k20. Qwen thinking-coding guidance has historically been lower temp (0.6) and presence_penalty for general thinking — **verify against the Qwen3.8 card** before rollout | Med | Per-mode sampling in pi models.json (coding vs general) |
| G8 | Heretic KV f16 at 2×262K (U24: ~5 GiB/262K, fine); `-b/-ub 2048` matches Strix Halo community practice. OK. Gemma 4 sampling T1.0/p0.95/k64 matches Google card | OK | none |
| G9 | `podman run --rm` on every swap drops prompt cache (SF-03); Halogen/Gufo cache-ram 2 GiB lost on swap | Low | Accept for now (community default); revisit only if swap latency hurts |
| G10 | Kernel cmdline still has deprecated `amdgpu.gttsize` (SF-06); `ttm.pages_limit` alone is the current community way | Low | Drop on next planned reboot |
| G11 | Host hygiene: cockpit open in firewall (cockpit-ws installed, socket not enabled), `X11Forwarding yes`, `MaxAuthTries 6`; VM-only services enabled on bare metal (qemu-guest-agent, vmtoolsd, vgauthd), iscsi/multipathd, ModemManager, bluetooth | Low | Remove cockpit from zone, X11Forwarding no, MaxAuthTries 3, disable unused services |
| G12 | Passwordless sudo `90-max-temp` (full NOPASSWD ALL) | Med | Stays until Derrick says (t1800u); plan a scoped replacement |
| G13 | `~/u31-render-sub/hdr` likely holds a key header outside `/etc/evo-x3` | Med | Move to `_archive` 0600 or shred-with-OK; rotate that key if it was a real key |
| G14 | SearXNG points at QNAP (SF-05); if QNAP is down, pi web search breaks | Low | Derrick's pick |
| G15 | `~/AI/community` has 14 uncommitted items incl. a Sydney face template; `actions.log` modified | Med | Explicit per-path `git add` (never `-A`) after review |
| G16 | Stale tailnet nodes (old Windows `evo-x3`, alfred-box 7d, grokbot-user-288846804) | Low | Derrick removes in admin console (ACLs are his) |
| G17 | Open WebUI model list never verified (U22); embed-small not wired to Open WebUI RAG | Low | Test step 7 |

## 3. Target final configuration

Keep llama-swap v272, the empty-key guard, loopback + Tailscale Serve, captureBuffer 0, pinned digests. Slot picks depending on U21 are **OPEN**.

| Slot | Final engine / file | Ctx | KV | Parallel | Sampling | Thinking | Status |
|---|---|---|---|---|---|---|---|
| flash-next (Forge main) | **OPEN: Halogen native HGN vs Gufo Q4_K_XL+MTP** — decided by U21 B1–B3 (tg/pp at d0/32K/131K/245K, cold TTFT) + coding/deep-research bake-off pass rate | 262144 | engine default | 4 if pool test passes at ≥2×200K, else 2 | Qwen3.8 card (verify; G7) | medium (OPEN low/medium) | OPEN |
| flash-next-sub (alias) | same process | 131072 (pi) | — | shares limit | same | low | keep |
| loser of Halogen/Gufo | archive slot from yaml (weights stay on disk until Derrick OKs deletion) | — | — | — | — | — | OPEN |
| flash-next-uncensored | Halogen HGN Huihui | 262144 | default | 1 | as flash-next | medium | **OPEN** — keep only if Derrick wants an uncensored Forge route (no benchmark yet) |
| gemma4-heretic (Render, Sydney writer) | llama.cpp b12405, Heretic Q8_0 + unsloth mmproj BF16 (unchanged) | 2×262144 | f16 | np 2 / limit 2 | T1.0 p0.95 k64 (Google card) | medium for Render/Sydney | keep; Q8 vs Q4 writer pick OPEN on U21 B4 |
| gemma4-heretic-sub | alias, **thinking forced off server-side** (G3) | 262144 | — | shares | same | off | fix |
| qwen27b | Gufo UD-Q8_K_XL + DFlash2 | 262144 | default | sessions 2 | Qwen card | medium | **OPEN** — keep as fallback/coder only if U21 shows a use not covered by flash-next; else archive slot |
| embed-small | nomic v1.5 Q8_0, yarn 0.75 @ 8192 (matches nomic card) | 8192 | — | — | — | — | keep |

pi target: `models.json` lists only kept slots, each with the verified thinking compat (G3); `settings.json` defaults unchanged (gemma4-heretic, thinking off; subagents → gemma4-heretic-sub for Render, flash-next-sub for Forge via project settings). Forge launcher adds `--thinking <OPEN>`.

## 4. Implementation steps (after Derrick's yes; one lease; one change at a time)

Each step: **backup** (`.bak-<date>-u33-<step>`, etckeeper commit for `/etc`) → **change** → **test** → **rollback** = restore the .bak + `systemctl restart llama-swap`.

1. **Pre-flight.** Confirm U21 + bake-off finished, lease released, no render queued on AlienPc. Take lease. Snapshot: `etckeeper commit "pre-U33"`, `cp models.json/settings.json` baks, sanitized copy of live yaml into `~/evo-x3/config/`.
2. **Engine pick for flash-next** (from U21). Edit `/etc/evo-x3/llama-swap.yaml`: keep winner as `flash-next`, remove loser from `main` group (comment-out block, file keeps it). Test: `/v1/models` lists expected names; one coding prompt; cold TTFT within 10% of U21. Rollback: yaml .bak.
3. **Thinking control fix (G3).** Determine per engine the request field that disables thinking (test with `enable_thinking:false` via `chat_template_kwargs`, and Halogen `reasoning_effort`). Then update pi `compat` per model and make `gemma4-heretic-sub` thinking-off server-side. Test: heretic-sub reply has empty `reasoning_content`; Render with `--thinking medium` does produce reasoning. Rollback: models.json + yaml .bak.
4. **Concurrency (G4).** Run 2×~200K + 2×32K concurrent on flash-next. Pass → keep limit 4; fail → limit 2. Rollback: yaml .bak.
5. **Sampling (G7).** Align Qwen slots with the Qwen3.8 card (coding vs general) in pi `samplingParams`; leave Gemma as is. Test: 3 Forge coding prompts, 1 long writer prompt. Rollback: models.json .bak.
6. **pi config.** Prune/add models.json entries to the kept slots; Forge `--thinking` level; fix SF-07 compaction reserve if Derrick wants (~95K). Test: `pi -p --no-session` one-shot per chat launcher (Render dry-run only, no queue). Rollback: .bak.
7. **Open WebUI + embeddings.** Verify model list; optionally point RAG embeddings at embed-small. Test: one chat from Open WebUI. Rollback: Quadlet .bak.
8. **Host hygiene (G10, G11).** sshd drop-in: `X11Forwarding no`, `MaxAuthTries 3` (`sshd -t` first, keep a second SSH session open). firewalld: remove `cockpit`. Disable qemu-guest-agent, vmtoolsd, vgauthd, iscsi*, multipathd, ModemManager (bluetooth only if Derrick doesn't use it). Kernel: `grubby --remove-args=amdgpu.gttsize` (takes effect at next reboot — reboot needs Derrick's OK). Test: SSH in fresh session; `firewall-cmd --list-all`; after reboot GTT still 120 GiB. Rollback: remove drop-in / re-add service / `grubby --args`.
9. **Gitea (G1).** See §7.
10. **Phase 6 cutover** (§5), only on Derrick's explicit yes.

## 5. Phase 6 chat cutover (needs Derrick's yes)

| Chat | From (AlienPc) | To (X3) | Steps | Test | Rollback |
|---|---|---|---|---|---|
| Render | `llama-swap/gemma4_heretic_poly_think --thinking medium` | `x3-local/gemma4-heretic --thinking medium` via `render-pi.sh` | AlienPc herdr Render pane → ssh to X3 launcher (or keep AlienPc pi with provider pointed at `https://evo-x3-1…`); queueing stays `queue-remote.sh <run> --yes-derrick` | 1 dry-run write + still_read; no queue | revert pane args in `pi_herdr_at_logon.ps1` (.bak) |
| Sydney | same | `x3-local/gemma4-heretic --thinking medium` | Persona stays on AlienPc; X3 only serves the model (pi on AlienPc with X3 provider) | Derrick sends one message | revert provider |
| Forge | `llama-swap/coding_swift15_iq3s_esp` | `x3-local/flash-next --thinking <OPEN>` | Project settings already mirrored; MCP servers still missing on X3 (decide: run pi on AlienPc against X3 endpoint, or port MCP) | one small repo task + subagent fan-out | revert model id |
| Phone | herdr `--remote` / pi-mobile on AlienPc | **OPEN**: keep phone on AlienPc herdr pointed at X3 models (simplest), or move herdr to X3 | — | phone message round-trip | revert |

AlienPc GPU then frees for ComfyUI renders only.

## 6. Cleanup (archive to `_archive/`, never delete)

- `~/evo-x3/_archive/u33/`: `llama-swap.yaml` (stale), `llama-swap_272_linux_amd64.tar.gz`, `model-tests-fail1.*`, `download-*.{log,txt}`, `podman-pull*.log`, `stage-src/` (if unused), U21/U31 `*.pid`/wrapper logs after results are recorded.
- `/etc/evo-x3/_archive/`: all `llama-swap.yaml.bak-*` except the last 2 and `pre-U33`.
- `~/.pi/agent/_archive/`: `models.json.bak-*`, `pi-permissions.jsonc.bak-*` except latest (keep 0600).
- `/tmp/u31-stage`, `/tmp/u31-webui-count.py`, `~/u29-parallel`, `~/u6-262k`, `~/u31-render-sub` → `~/evo-x3/_archive/u33/scratch/` (`hdr` stays 0600; Derrick decides shred + key rotation).
- `~/.pi/agent/dummy_run/` → archive.
- Model files: loser engine weights (~107–112 GB), `Qwen3.8-27B-UD-Q4_K_XL.gguf`, Heretic mmproj Q8_0 → `/srv/models/_archive/` (deletion only with Derrick's OK).
- `~/rocm` (9.9G): check what uses it; archive if nothing.
- Tailnet stale nodes: list for Derrick (he removes).

## 7. Gitea backup (git best practice)

Repos on Gitea (URL in `/etc/evo-x3/gitea.env`; token via credential helper reading the env file, never on argv):
- **x3-forge**: `~/AI/forge` (AGENTS.md, `.pi/settings.json`, launcher copy). `.gitignore`: `_archive/`, `ralph-community/` if it's a clone, sessions.
- **x3-render**: `~/AI/render` existing repo → add `gitea` remote, push `main`. Keep `stills/` untracked (ignore it).
- **x3-pi-config**: new repo from `~/evo-x3` (records, scripts, pi-chats, bench scripts, sanitized `config/llama-swap.yaml`, Quadlet copy, systemd units) + `~/.pi/agent` copies of `settings.json`, `AGENTS.md`, `pi-permissions.jsonc`, `web-search.json`, and **`models.json.example` with apiKey removed**. `.gitignore`: `models.json*`, `auth.json`, `models-store.json`, `*.env`, `*.cred`, `hdr`, `.venv*`, `*.gguf`, `*.hgn`, `*.tar.gz`, `sessions/`, `bench/**/raw*`. Run gitleaks before first push.
- `~/AI/community`: add `gitea` remote; stage only reviewed paths by name (never `git add -A`).
- `/etc` etckeeper: commit the 7 pending changes; stays local (contains host config; push only if Derrick wants, after gitleaks).
- Commit per logical change, message `U33: <what>`; push after each step.

## 8. Final QNAP backup (last)

Live rsync to QNAP (under ~180 GiB; estimate **~25 GiB**):
```
sudo rsync -aAXH --numeric-ids --info=progress2 \
  --exclude=/srv/models --exclude=/var/lib/containers/storage/overlay* \
  --exclude=/home/*/.cache --exclude=/home/*/.npm --exclude=/home/*/rocm \
  --exclude={/dev,/proc,/sys,/run,/tmp,/mnt,/media,/var/tmp,/boot/efi,"/lost+found"} \
  / <qnap-target>/evo-x3-fedora-20261116/
```
Plus `podman volume export open-webui` (chat DB) and a text manifest of image digests + `/srv/models/SHA256SUMS` (weights re-download). Target path + mount (`/mnt/qnap/...`, creds from `/etc/evo-x3/qnap.cred`) set at run time. `/etc/evo-x3/*` secrets: include only if the QNAP share is private (Derrick decides). Verify: `rsync -n` dry run size first; after copy, `rsync -c -n` spot check of `/etc` and `~/evo-x3`. Never touches Windows partitions or X3BACKUP.

## 9. Notes for this record

- `~/evo-x3` is not a git repo, so this file was **not committed** (task asked to commit only this file). Committing it waits for Step 9 (`x3-pi-config` repo) or Derrick's OK to `git init` there.
- Copy: `/workspace/maxops/x3/U33-audit-rollout-plan-20261115.md` on the Grok box.

## 10. Decisions that need Derrick's yes

1. Approve this plan to implement (Steps 1–9) after U21 finishes.
2. flash-next engine: Halogen vs Gufo (after U21 numbers); archive the loser slot (and later its ~110 GB weights).
3. Keep or drop `flash-next-uncensored` and `qwen27b` slots.
4. Forge thinking level (low / medium) and Qwen sampling per the card.
5. flash-next parallel limit 4 vs 2 (after the pool test).
6. Phase 6 cutover: Render, Sydney, Forge, and how the phone connects.
7. Reboot to drop `amdgpu.gttsize`; host hygiene (cockpit off, X11 off, disable VM/iscsi/modem services, bluetooth?).
8. Shred `~/u31-render-sub/hdr` and rotate that key, or keep archived.
9. SearXNG home (QNAP vs X3).
10. Push etckeeper `/etc` to Gitea or keep local; include `/etc/evo-x3` secrets in QNAP backup or not.
11. When to replace `90-max-temp` sudo with a scoped rule.
12. Remove stale tailnet nodes (his admin console).
