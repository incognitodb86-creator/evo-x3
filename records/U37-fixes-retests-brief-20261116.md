# U37 brief: AlienPc fixes, skills fix batch, builder fixes, retests (Derrick-approved)

Written Mon Nov 16 2026, ~9:30 AM CT, by Grok Bot (Max executor) for Antigravity (Gemini 4 Hydrogen High) on the X3.
Approval: Derrick's widget answers at 9:20 AM CT Nov 16 (answer to t1883s6930), and t1884u ("have Antigravity do these fixes").
Read first: X3 copies of the two reports if present, otherwise the summaries in this brief:
- red-team AlienPc render node report (box: /workspace/maxops/x3/redteam-alienpc-render-node-20261116.md)
- skills/builder/retest audit (box: /workspace/maxops/x3/audit-skills-builder-retest-20261116.md)
Key findings from the skills audit you need: S1 shared render skills (video-render L28-29/L35/L45-46, h3-hc-render L113/L116, image-render L21/L35, h3-parody-identity L40-46) run `/home/evo/AI/director/.venv/Scripts/python.exe` in ```powershell blocks, which doesn't exist on the X3. S2 h3-parody-identity "Autonomous recipe — ONE command" (`submit_parody_run.py ... --wait --qnap-put`) is a direct queue path. S3 video-render L36-37, h3-hc-render L79/L113, image-render L28, alienpc-stills L16 treat `/home/evo/AI/locks/gpu-render.lock` as the real lock; on the X3 it is unused and AlienPc's lock is invisible (Render AGENTS.md L170). S4 h3-parody-identity L19, h3-hc-render L109 still name AlienPc models (`gemma4_heretic_poly`, `coding_swift15_iq3s_esp`, "ralph.ps1 default"). Forge loads 5 render skills twice (community/skills vs agent-shared/skills vs fleet-brain/20_skills/current). The builder (submit_parody_run.py / build_request.py) reported READY in all 3 runs of a test where the still was missing.

## What is already done before this handoff
- Nothing in steps A-F was changed by Grok Bot. Both reports were read. No files edited, no renders, no leases taken.
- Route check (9:25 AM CT): there is NO shell route from the X3 to AlienPc. Direct SSH X3 -> AlienPc times out (U36-RESULT.md), and AlienPc has no key for the X3. The only X3 -> AlienPc path is HTTP through Tailscale Serve `https://alienpc.tailf242b2.ts.net:8446` (llama-swap -> comfyui_auto), used by `~/AI/render/x3/queue-remote.sh`.
- `agy models` has no "Halogen" model. This run uses gemini-4-hydrogen-high.

## How to handle what you cannot reach
- Step A is all AlienPc Windows work. If you cannot run Windows commands on AlienPc, mark every A item BLOCKED (reason: no X3 -> AlienPc shell) in U37-RESULT.md and continue. Do NOT try to make a route (no new SSH keys, no Tailscale changes, no auth keys).
- Steps E and F require taking and releasing the AlienPc GPU lease and checking AlienPc's GPU is free of PixlStash. You can't do either from the X3. So for E and F: do the dry build (prompt.txt, request JSON, node list) so the run is READY, do NOT run queue-remote.sh, and mark them "BLOCKED: needs AlienPc lease + GPU check, run dir READY at <path>". Grok Bot will take the lease and queue them.

---

## Steps, in this order, verifying each before moving on (as Derrick approved them)

A. AlienPc fixes (machine ecc21911-e61e-44fb-80b1-4bbe46bc56bd). Back up before every change. Disable, never delete.
1. Disable the PiHerdrAtLogon and pi-mobile startup on AlienPc. Stop AlienPc's herdr and the leftover pi agents. Turn off AlienPc Tailscale Serve :8443. Derrick is now paired with the X3 hub.
2. Make llama-swap and IIB (the output browser) start at boot without anyone logged in. Use a "run whether user is logged on or not" scheduled task or a service, with restart-on-failure. Do not enable auto-logon.
3. Block automatic reboots while a user is logged on (NoAutoRebootWithLoggedOnUsers policy).
4. Add /queue to llama-swap's ignorePaths so the X3 lock check can't wake ComfyUI. Only edit llama-swap.yaml when no render is running, and back it up first. If the X3 lock check could use a non-waking path instead, note that.
5. Disable the forge-cleanup20261105-loopA task.
6. Tighten the Python Windows Firewall allow rules: scope them to Private/Tailscale and the specific ports needed, or remove the any-port Public allows by disabling them. Do not cut off ComfyUI on localhost, Tailscale Serve, or QNAP sync. Do not change PixlStash's listen address and never open PixlStash. Re-verify that :8446 still works from the X3.
Do NOT touch the Tailscale ACL, D: files, or the ComfyUI folder contents.
(Even if A is blocked: for A4, read ~/AI/render/x3/queue-remote.sh and remote_comfy.py on the X3 and note which ComfyUI paths the "lock check" hits and whether a non-waking path exists. Read-only.)

B. Skills fix batch, as one commit with backups. Fix the shared render skills the X3 chats load:
- Swap Windows python and PowerShell commands for the X3 equivalents.
- Change h3-parody-identity's direct queue recipe to: dry build, then queue-remote.sh only after Derrick's yes.
- Correct the GPU-lock wording for the X3.
- Update the stale model names and hosts, and the C:\Users\derek paths.
- Give render/RUN_ME.md an X3 section.
- Resolve Forge's duplicate skill loading so one canonical copy loads, keeping the newest correct content.
- Make h3-max-ref2va-prompt stop claiming to be the standing lane.
Rules: Don't change the locked 4bc9bba pipeline settings. Don't add new rules. Don't touch Sydney's private files.

C. Builder fixes, with backups and tests:
- Add a hard fail when --still is missing.
- Enforce absolute run paths.
- Turn the quiet post-write rewrites (fps/aspect/throat/negatives) into lint failures the writer has to fix.
- Drop no rules.
Run pytest and keep any existing passes passing. Commit.
(Record the pytest pass/fail counts before and after. Known: 5 Windows-only parody tests fail on the X3; leave them, note them.)

D. Retest 2 (dry, no GPU): Render's writer on the X3 (gemma4-heretic, via a Render pi chat started as evo, not a standalone script). Use 4 asks with its own still read and lint logging, all dry_run. Record which lint rules fire.
(Start it with the existing launcher ~/AI/render/x3/render-pi.sh as user evo per U35/U36. If you can't start a chat as evo, mark D BLOCKED with the reason; do not fall back to a standalone script. Model swapping on llama-swap is fine. Never pass LLAMA_SWAP_KEY or any secret on argv.)

E. Retest 1 (Derrick's yes): one live 124-frame remote render from the X3, using queue-remote.sh --yes-derrick on the locked pipeline with a still from the approved stills.
- Take the AlienPc lease and release it after.
- Save prompt.txt and the node list, and include the full prompt text in your report.
- Verify the output plays (ffprobe frames/duration), then copy it to /workspace/maxops/renders/.
(See "How to handle what you cannot reach": build it dry, put the full prompt text and node list in U37-RESULT.md, do not queue without the lease.)

F. Then, under one lease: VRAM probe 2 refs @192 frames, VRAM probe 3 refs @107 frames, and the 243-frame 3-shot cut probe.
- Record the peak VRAM, spills, times and pass/fail for each.
- Keep the GPU free of PixlStash during the probes.
- Release the lease when done.
- No clip review passes.
(Same: build the three run dirs dry, do not queue; mark BLOCKED pending lease.)

General rules:
- Never put secrets on command lines or in output.
- Never read Sydney's or PixlStash's content.
- Don't run the extend-test rerender: Prompt maker's hold stays.
- If a step is blocked, continue with later steps that don't depend on it.
- Keep usage efficient: no review subagents.

## HARD RULES (standing, keep)
- Never queue an H3 render without Derrick's yes. Only E and F have it, and only with the AlienPc lease held.
- No edits or deletes outside steps A-F. Back up first (`*.bak-20261116-u37`), use `_archive/` instead of deleting.
- Back up X3 work to Gitea with normal git practice: stage named files only, never `git add -A`; clear commit messages; push. Don't commit ~/.pi/agent/models.json, SearXNG settings.yml, or anything under /etc/evo-x3/.
- X3 secrets live only in /etc/evo-x3/*; pass them via stdin or env file. Never print tokens or passwords. Never create API keys or Tailscale auth keys.
- Never touch the Windows partitions or USB X3BACKUP. No BIOS, LUKS, firmware, spending. Don't turn Tailscale SSH on. No downloads over ~5 GB. No plugin installs.
- Never view PixlStash library contents; never touch the original ComfyUI folder. Never read Sydney's chats, persona or memory.
- Don't edit llama-swap.yaml during an active render.

## STOP CONDITION
When done or blocked, write /home/derekboone/evo-x3/records/U37-RESULT.md with, step by step (A1-A6, B, C, D, E, F): DONE / BLOCKED / PARTIAL, what changed (file + backup path), live evidence (command + output summary), commit hashes (and push status), pytest before/after counts, the D lint-rule counts per ask, the E/F run dirs and the full E prompt text and node list, and decisions Derrick needs with a recommended answer. Then stop.
