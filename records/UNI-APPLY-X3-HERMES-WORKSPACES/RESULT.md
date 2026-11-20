# UNI-APPLY-X3-HERMES-WORKSPACES RESULT

- **When:** 2026-11-20 11:11:28 CT to 2026-11-20 11:12:28 CT
- **Script:** `scripts/apply-hermes-workspaces.sh --apply --render-presence 0.0 --code-thinking medium`
- **Backups:** `/etc/evo-x3/_archive/llama-swap.yaml-20261120-preWS`, `/home/evo/.hermes/_archive/20261120-ws/`
- **llama-swap /running:** `{"running":[{"model":"flash-next-uncensored-v2","state":"ready","cmd":"podman run --rm --name llama-swap-flash-next-uncensored-v2\n  --network=host --device=/dev/kfd --device=/dev/dri --group-add=keep-groups\n  --security-opt seccomp=unconfined --security-opt label=disable\n  -v /srv/models:/srv/models:ro -v /srv/bakeoff:/srv/bakeoff:ro\n  ghcr.io/gufo-org/toolboxes/gufo-runtime@sha256:99e9b5471b7a9b007c686c2aa795afaf966744d64e753cb009c89541f9e9c2b6\n  gufo serve llm --host 127.0.0.1 --port 8081\n  --model /srv/bakeoff/Huihui-Qwen3.8-Flash-Next-abliterated-v2-GGUF@cbc7fba/Qwen3.8-Flash-Next-UD-Q4_K_XL-00001-of-00004.gguf\n  --mmproj /srv/bakeoff/Huihui-Qwen3.8-Flash-Next-abliterated-v2-GGUF@cbc7fba/mmproj-Qwen3.8-Flash-Next-BF16.gguf\n  --mtp-model /srv/models/flash-next/mtp-Qwen3.8-Flash-Next-shared-Q8_0.gguf\n  --speculative mtp\n  --served-model-name flash-next-uncensored-v2\n  --sessions 2 --context 131072 --preserve-thinking on\n  --reasoning-effort medium --reasoning-budget 8192\n  --cache-ram-bytes 2147483648 --max-pending 16\n  --temperature 1.0 --top-p 0.95 --top-k 20\n  --stall-timeout-ms 120000\n  --log-progress\n","proxy":"http://127.0.0.1:8081","ttl":0,"name":"","description":""}]}`
- **Render oneshot:** `  Command helper: applied 4 secrets
h3-render renders video; pi-job handles code (code|review).

session_id: local-2cd474d53e2310b6f775ce6f284c6ee448edec94c4711526bebe16d2b1380221`
- **Code oneshot:** `  Commands run with your full user credentials.  Only approve
  commands you trust.
Allow this hook to run? [y/N]: pwd: /home/evo — code changes go through the pi-job skill (`pi-job code <repo> "<task>"`).

session_id: local-13658fac72c4914418fd50a8567c75064da297283baf7a60b5c6976b3c07577d`
- **Code skills check:**
```
│ pi-job                 │                      │ local   │ local   │ enabled  │
│ h3-render              │ creative             │ local   │ local   │ disabled │
│ h3-writer              │ creative             │ local   │ local   │ disabled │
```
- **WebUI D4 check:** open Hermes WebUI, pick profile `code`, ask `pwd`. If WebUI forces `/home/evo/workspace`, archive `/home/evo/.config/systemd/user/hermes-webui.service.d/30-workspace.conf` and restart `hermes-webui`.
