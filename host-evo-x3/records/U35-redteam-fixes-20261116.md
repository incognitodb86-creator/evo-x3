# U35 red-team fixes (C1 agents-as-evo, H4 SSH from=), Mon Nov 16 2026, started 8:12 AM CT

Derrick's yes: widget t1866s6872, 8:10 AM CT ("Yes, apply fixes 1, 2 and 5 now"). Fix 2 (QNAP) DROPPED by Derrick t1867u: no new backup, no QNAP permission change (none was made).
Executor: Max Architect (U35). STATUS: DONE 8:18 AM CT (see FINAL STATE).

## NOTE FOR THE CONSOLIDATION EXECUTOR (herdr / panes / pi-mobile on the X3)
- All agents (pi panes Forge/Render/Sydney/Research, ralph loop, herdr, pi-mobile, agent timers) run as user `evo` (uid 1001, no sudo), NOT derekboone.
- Agent home: /home/evo. Trees: /home/evo/AI/{render,forge,sydney,community,comfy-alienpc,fleet-brain,locks,5slock}, /home/evo/.pi/agent, /home/evo/evo-x3/pi-chats/*.sh, pi at /home/evo/.local/bin/pi, herdr at /home/evo/.local/bin/herdr.
- `loginctl enable-linger evo` is set. Put herdr-panes.service / pi-mobile units in /home/evo/.config/systemd/user (run them with `sudo -u evo XDG_RUNTIME_DIR=/run/user/1001 systemctl --user ...`), NOT under derekboone, and do not enable linger work for derekboone agents.
- LLM key for evo: /home/evo/.config/evo-x3/llm.env (0600 evo, LLM_KEY_PI). models.json reads it; never copy other /etc/evo-x3 files to evo.
- evo has NO Gitea token (derekboone's credential helper is unreadable to evo) — git pushes stay with derekboone/Max.
- derekboone's ~/AI and ~/.pi copies remain as the backup/source; do not start agent panes from them.

## FINAL STATE (8:18 AM CT)

### Fix 1 (C1) — agents run as `evo`: DONE (agy excepted)
Backups: /root/u35-backups/home-evo-pre-20261116-*.tgz (evo home before), etc-evo-x3-facl-pre-*.txt.
Changes:
- /home/evo (0700, evo:evo, 1.4 GiB): copies of ~/AI/{render,forge,sydney,community,comfy-alienpc,fleet-brain,locks,5slock}, ~/.pi/agent (minus _archive, *.bak, auth.json -> fresh `{}`), pi 1.5.2 node_modules + ~/.local/bin/pi symlink, herdr binary, ~/evo-x3/pi-chats launchers, scripts/comfy-submit.sh. _xfer bundles not copied.
- Paths /home/derekboone -> /home/evo rewritten in 207 text files of evo's copy (not .git/node_modules/.venv internals; venv shebangs/pyvenv fixed). This leaves path-only working-tree diffs in evo's git copies: community 55 M, render 9 M, forge 2 M (uncommitted on purpose; derekboone's repos untouched).
- Key: /home/evo/.config/evo-x3/llm.env (0600 evo, only LLM_KEY_PI, copied root-to-file, never printed). evo models.json apiKey = `!sed -n 's/^LLM_KEY_PI=//p' /home/evo/.config/evo-x3/llm.env`.
- `setfacl -m u:evo:--- /etc/evo-x3` (evo denied the whole dir; derekboone/root unchanged).
- evo pi-permissions.jsonc: bash deny `sudo*`, `*sudo *`, `*/etc/evo-x3*` appended (last match wins); JSONC parse checked.
- `loginctl enable-linger evo`.
- evo has no Gitea credential (helper file in derekboone's 0700 home).
Verification (as evo): `sudo -n true` -> "a password is required" (fail); `sudo -l -U evo` -> not allowed; cat /etc/evo-x3/vaultwarden.env, ls /etc/evo-x3, cat /etc/evo-x3/llama-swap.yaml, derekboone llm-key, gitea token -> all Permission denied. /v1/models with evo key -> 200. `forge-pi.sh -p --no-session` (flash-next, already loaded, no swap) -> "EVO PI OK", rc 0. All render/sydney launcher -e extension and skill paths exist under /home/evo. Exact-value scan of /home/evo against 26 secret values from /etc/evo-x3 + gitea token + llm-key: only /home/evo/.config/evo-x3/llm.env holds a key (other hits are the non-secret GITEA_URL/UNIFI_URL hostnames).
Not moved:
- agy (Antigravity): sign-in is per-user, an OAuth token file under ~/.gemini/antigravity-cli. Moving it means copying Derrick's Google token (refresh-token rotation could break one copy) or a new Google sign-in as evo. Left as derekboone; agy still runs with derekboone's root path until Derrick signs in as evo or OKs a token copy.
- SearXNG rootless container stays under derekboone (a service, not an agent; loopback only).
- No agent services/timers existed for derekboone (no user units, no crontab); none were running.

### Fix 2 (QNAP) — DROPPED by Derrick t1867u
No QNAP permission change and no new backup were made. U34-rollout-done wording corrected (contains secrets by design; aborted file 5.2 GiB). Old backups untouched: QNAP u34-final-20261116-0733 (7.6 GiB) and /var/backups/evo-x3/_aborted-u34-final-20261116-0732 (5.2 GiB).

### Fix 5 (H4) — SSH key source restrictions: DONE
sshd log (journal since Nov 14 + /var/log/secure): max-architect-box key SHA256:pdoxyDrM -> 226 logins, all from 100.103.175.80 (tailnet node grokbot-user-419859074, the box; NOT grok-box 100.91.255.124 as the audit guessed). household-box key SHA256:sCgQNv3f -> 28 logins, all from 192.168.0.175 (Wi-Fi LAN, MAC e0:d5:5d:d0:16:82).
authorized_keys now: from="192.168.0.175" household…, from="100.103.175.80" max…. Backup: ~/.ssh/authorized_keys.bak-20261116-081555-u35.
Safety: systemd-run u35-ak-revert.timer (5 min restore) armed, fresh non-multiplexed login from the box succeeded ("Accepted publickey … from 100.103.175.80 SHA256:pdoxyDrM"), timer then stopped.
Risks: if the box's tailnet node/IP changes, or 192.168.0.175's DHCP lease changes, that key stops working; recovery = console or the other key. A DHCP reservation for 192.168.0.175 is recommended (Derrick's router).

### For the consolidation executor
Use /home/evo for every agent launcher/unit (see NOTE at top).
