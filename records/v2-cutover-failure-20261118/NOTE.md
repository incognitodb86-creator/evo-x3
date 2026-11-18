# v2 cutover failure, Nov 18 2026 (Max Architect, Derrick t2437u)

Model: johnlockejrr/Huihui-Qwen3.8-Flash-Next-abliterated-v2-HGN (flash-next-uncensored v2, Halogen 0.20.7 image, sha256-verified at /srv/models/flash-next-uncensored-v2-hgn).
Edit by agy Hydrogen at ~12:25 CT: added slot "flash-next-uncensored-v2", added it to the group, and repointed aliases
(flash-next-uncensored, flash-next-uncensored-sub, flash-next, flash-next-sub, gemma4-heretic, gemma4-heretic-sub) to v2.

Failure: llama-swap refused the config: duplicate alias "flash-next-uncensored-sub" (see journal-error.txt).
The v1 slot still declares that alias, and the new alias map also declares it -> llama-swap crash-looped ~12:25-12:49 (456 restarts); X3 Render/Forge had no model.
The v2 model itself never started, so v2 is untested.

Recovery 12:49 CT: restored /etc/evo-x3/_archive/llama-swap.yaml.bak-20261118-1225-pre-v2-cutover; v1 /health ok. pi defaults were never switched to v2.
Likely fix: remove the v2-pointing aliases that the v1 slot already owns (or drop them from the v1 slot), then load v2.

Files: llama-swap.broken-v2.yaml (exact broken config; keys are env refs only), cutover.diff (vs pre-cutover backup), journal-error.txt.
