# Forge simplify plan (AlienPc): stock pi + 4 keeps

Derrick decisions: "Forge runs stock community settings, Max adds nothing" (Oct 23, 7:28 PM CT, relayed); bash on, Forge may edit comm.py and its own files, and only 4 keeps (Oct 30, relayed); "Plan this out and do research... how does the community do it?... Be more specific on what you are cutting" (Oct 30, 7:58 AM CT).
Inputs: audit `/workspace/audits/2026-10-30-forge-setup-overengineering-audit.md`, review `60_reviews/max/2026-10-30-forge-setup-overengineering-audit-review.md` (PASS WITH FIXES). AlienPc read-only lease 8:02–8:06 AM CT; nothing changed.

**Goal:** Forge runs as close to stock pi as possible. Only 4 controls remain, and each is enforced where Forge can't switch it off.
**Done when:** Every row in the cut list is done or carded. The 4 keep tests (FO-9b) pass: a secret read is refused, the adults fixture is refused on every submit path, two jobs collide and the second gets rc 7 `GPU_BUSY`, and a dry NAS delete asks first.
**Who builds:** Forge does the file trims and archives. Derrick does anything needing admin (Windows user, ACLs, tokens). Max briefs only.
**Stop:** If any keep test fails after a cut, restore it from the dated archive (step 0) and report.

## Community comparison
| Area | Community (source) | Ours now | Gap |
|---|---|---|---|
| Base pi | YOLO by default, with no permission system. "Run the whole process in a container/VM" or "a dedicated user account" ([pi security docs](http://pi.dev/docs/latest/security); [pi README](https://github.com/earendil-works/pi/blob/64b51efb6ef6f1e42676e866da906a5f900e592d/README.md); fetched Oct 30 2026) | 2 policy files (181+323 deny), cc-safety-net, an 11-rule pi-rules skill, bash off | **Overbuilt** on rules, **missing** an OS boundary |
| Permission extension | pi-permission-system: a short `"*"` fallback, `bash` patterns, and a cross-cutting `path` deny for `~/.ssh/*` and `.env` (one rule covers all tools and bash) ([config docs](https://github.com/gotgenes/pi-packages/blob/main/packages/pi-permission-system/docs/configuration.md); npm v42.0.0, updated Oct 28 2026). Ours is 0.8.0 | 394-line interactive policy and a 343-line loop policy | **Overbuilt.** About 15 lines matches the docs' examples |
| Secrets | Keep credentials out of the environment, or use scoped short-lived ones (pi security docs) | Readable by derek (FO-1) | **Missing** |
| Ask-first (HA/UniFi/NAS) | HA: a read-only user's token ([HA community thread, Jan 2023](https://community.home-assistant.io/t/read-only-access-to-api/522340); unverified on current HA). UniFi: **API keys have no read-only scope** ([UI community](https://community.ui.com/questions/fec51b17-2f12-46c2-8837-a71d094ae4fa); [Art of WiFi](https://artofwifi.net/blog/unifi-api-authentication-local-admin-vs-api-key-vs-site-manager)) | Shell patterns only (FO-3) | **Missing.** UniFi "View Only key" from the review is not possible, so the key stays off Forge's user |
| Adults-only | See below | 13-line keyword guard | **Matches the norm.** The duplication around it is overbuilt, and one submit path is **missing** the guard |
| GPU single-job | ComfyUI queues jobs serially by itself (general knowledge, not re-verified) | gpu_lock.ps1 (32 lines) + gpu_guard.ps1 (202 lines, 13 KB) | Lock **matches** a Derrick keep. The guard is extra but load-bearing (FO-5) |

## Adults-only check
**Today:** `comm.py` lines 38-48 hold `guard_ok()`. It has 6 exception words (cowgirl, girlfriend…), 10 blocked words (girl, teen, school, minor, kid, child, loli…) plus plurals, and the phrase "barely legal". It scans every prompt string in the graph. It is called in `comm.run()` at L197-198 (a duplicate pre-check, logging only) and L200-202 (the real gate), and in `run_graph_job.py` L127 (rc 3). Tests: `tests\test_p6_review.py` (179 lines, 10 guard refs). **The gap:** `probe_submit.py` (39 lines) POSTs `/prompt` with no guard. Note that `comm.run()` is guarded, which corrects FO-4's wording; probe_submit.py is the only bypass. The rule text is also copied into 4 instruction files.
**Community norm:**
- Local creators mostly rely on fictional-adult character wording and negative prompts such as `loli, child, young` ([Civitai model page example](https://civitai.com/models/669139/realistic-manhwa-style)).
- Hosted sites filter prompts with a term list plus image moderation (Rekognition plus human review) ([Civitai Safety Center](https://civitai.com/safety)). Their public lists are in [civitai/civitai src/utils/metadata/lists](https://github.com/civitai/civitai/tree/main/src/utils/metadata/lists), cited in a [Reddit thread, Jul 2024](https://www.reddit.com/r/civitai/comments/1dtju0b/).
- A keyword hard-block node exists for ComfyUI ([TextPromptBlocker](https://www.runcomfy.com/comfyui-nodes/COMFYUI_PROMPTMODELS/text-prompt-blocker)). Age-classifier gates exist but are niche ([ComfyUI-Underage-Filter](https://github.com/T-Ph525/ComfyUI-Underage-Filter), ViT age model).
- Fuller stacks exist ([FightCSAM promptshield](https://fightcsam.org/docs/promptshield)) but are aimed at services.
- Evidence on what solo local users do is thin, mostly forum posts. A keyword list is the common "something", and classifiers are rare locally.

**Verdict:** The check itself is *not* overengineered. 13 lines is the lightweight end of community practice. The overbuild is the 4 rule copies and the duplicate pre-check.
**Minimal version:**
1. Keep `guard_ok` unchanged.
2. Make `comm.run()` the one submit path. `run_graph_job` keeps its L127 call as belt and braces.
3. Archive `probe_submit.py`.
4. Delete the logging-only pre-check at L197-198.
5. Replace the 4 instruction copies with 1 AGENTS line: "Fictional adults (18+) only; guard_ok runs on every submit."
6. Make `comm.py`'s guard section and the test ACL read-only for Forge's user (FO-4).

Optional, Derrick's call: move the same list into a ComfyUI-side TextPromptBlocker so a direct API POST is also blocked.

## Cut list (archive to `C:\AI\_archive\2026-10-30-forge-simplify\` with sha256; nothing deleted)
| # | Path / rule | What | Size | Action | Why | Community |
|---|---|---|---|---|---|---|
| 1 | `.pi\agent\settings.json` defaultTools | no `bash` | 1 key | add `bash` **after FO-1/2** | Oct 30 decision | stock pi |
| 2 | `.pi\forge-policy\pi-permissions.jsonc` | loop policy | 343 lines, 10 allow / 323 deny | archive; loop uses #3 | stale since 10/24 | docs examples ~10 lines |
| 3 | `.pi\agent\pi-permissions.jsonc` | interactive policy | 394 lines, 148/181/30 | trim to ~15: `path` deny for secrets, `ask` for 5 ask-first patterns, `"*":"allow"` | 4 keeps only | path surface |
| 4 | `.pi\agent.bak-20261029-max2\` | old policy (652 lines) | dir | archive | leftover | – |
| 5 | `forge\loop1017\.pi\…jsonc` | 10/20 policy | 41 lines | archive | stale | – |
| 6 | skill alienpc-pi-rules | 11 "override" rules | 495 words | archive; 4 keeps + FO-6 lines into AGENTS | Max controls | none |
| 7 | skill forge-self-diagnose | RETIRED | 987 words | archive | stale | – |
| 8 | skill alienpc-ltx-i2v-prompting | archived LTX | 513 words | archive | unused | – |
| 9 | skill alienpc-local-video-ops | CAPA/park/loop gates | 1,278 words | trim to ops facts (~200) | Max QA layer | – |
| 10 | h3-hc-render "p7 budget gate" + JOB_REQUEST | gate | section | trim | plan-GO gate removed | – |
| 11 | PROMPT.md "9999" rules, fix_plan MAX block | Max queue | 281 + 2,346 words | archive the done items; PROMPT to steps 0a/1/2 | Max gate | no loop in stock |
| 12 | `notes\pi_forge_updates_2026-10-28.md` + learnings | read-every-chat | 630 + 1,521 words | archive; fold needed lines | context | – |
| 13 | AGENTS.md | instructions | 629 words, ~45 lines | trim to ≤40 lines, no repeats | dup rules ×3-4 | one AGENTS.md |
| 14 | comm.py L197-198 | dup guard pre-check | 2 lines | delete lines (git/archive copy) | gate is L200-202 | – |
| 15 | `scripts\probe_submit.py` | unguarded POST | 39 lines | archive **now** | FO-4 bypass | – |
| 16 | packages pi-memory, rpiv-todo, pi-subagents | extras | 3 pkgs | remove if unused (Derrick confirms subagents) | not stock | – |
| 17 | cc-safety-net | destructive-cmd net | pkg | **keep** (FO-8) | only bash-level net | – |
| 18 | gpu_guard.ps1 | busy check | 202 lines | **keep** until the collision test passes without it (FO-5) | lock depends on it | – |
| 19 | one-off scripts: probe_* (5 left), q5_* (4), capa_* (2), h3_lora_social_sweep 1-3, gpu_window.ps1, 3 `.bak` | leftovers | ~20 files | archive | one-offs | – |
| 20 | ~25 `.bak-*`, `pi-skills-20261028.zip`, `missions\` (13), root `*.out`/P5/RUNBOOK/SETTINGS_CHECK | leftovers | – | archive | clutter | – |
| 21 | director: overnight_chain, after_p7_forgeup, apply_swiftesp_p7, forge.ps1, check_pi_extension* | stale 10/16-22 | ~7 files | archive | unused | – |
| 22 | tasks MaxOptMatrix, SY_Runner, SY_Night, SY_AgyFix, SY_AgyFix2, SY_Capa2, SY_Phone, agy-harness-gates, agy-ui-settings, HereticDownload | Disabled | 10 tasks | unregister: **Derrick's card** (export XML first) | dead | – |
| 23 | `compaction.modelOverrides` | 3 unused models | 3 keys | trim | stale | – |
Keep: PiHerdrAtLogon, pi-mobile, Switchyard llama-swap, GrokBot AutoStart, Kopia, Household GDrive to NAS, EOSv3, plus run_graph_job/comfy_ctl/pi_qnap and h3-prompting.

## Security fixes first (before #1 and #3)
| FO | Fix | Simplest community way |
|---|---|---|
| FO-1 secrets | Run Forge (herdr/pi) as a new standard Windows user `forge`. Secrets stay in derek's profile, which `forge` can't read | pi docs "dedicated user account" (container is stronger but heavy with GPU on Windows) |
| FO-2 policy self-edit | Policy and `comm.py` guard owned by Administrators, read-only for `forge` | follows from the OS boundary |
| FO-3 ask-first | HA: read-only-user token. UniFi: no key on `forge` (keys can't be read-only). NAS: forced-command SSH key. Money: nothing on AlienPc | pi docs "narrowly scoped credentials" |

## Order
0. Archive and sha256 (FO-9a). 1. Archive probe_submit (#15). 2. FO-1/2/3 (Derrick, admin). 3. #1, #3, then #2, #4-14, #16, #19-21, #23. 4. Keep tests (FO-9b). 5. Card for #22. Lease and start/done messages each run; Linear id TBD.

## Open questions for Derrick
1. Can a separate `forge` Windows user live with ComfyUI/llama-swap running as derek? Is a loopback HTTP route enough?
2. Keep pi-subagents?
3. FO-10: are plan-level GO gates gone too, or only Max's pre-render checklist?
4. Add the optional ComfyUI-side TextPromptBlocker?
5. Unregister the 10 disabled tasks (#22)?
