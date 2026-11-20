EVO-X3 coding workspace (Hermes `code` profile, `flash-next-code` on Gufo 0.35.0, thinking medium).
Renders do not happen here; renders use the default Hermes profile.
Code changes and code reviews go to pi via `pi-job code <repo> "<task>"` or `pi-job review <repo> "<task>"` (AlienPc Swift when idle, X3 Gufo fallback; single active slot).
Repos on X3 (owner `evo`): `/home/evo/AI/community`, `/home/evo/AI/render`, `/home/evo/AI/forge`.
Monorepo `mono` is the only pushed branch (GitHub first, Max mirrors to Gitea).
Live X3 config/service changes need Derrick's yes and the one-line lease in `/home/derekboone/AI/locks/x3-lease.txt`.
Gemma is dropped on X3; Qwen3.8-Flash-Next (`flash-next-uncensored-v2`) stays resident.
