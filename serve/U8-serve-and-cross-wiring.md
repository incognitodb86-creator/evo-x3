# U8 / U9-U10 wiring: Tailscale Serve + AlienPc <-> EVO-X3 (2026-11-15, CT)

Authorized: Derrick "Yes" (t1683u) to Tailscale Serve + access setup for the X3 LLM endpoint, and to wiring both
directions (AlienPc tools -> X3 models; X3 -> AlienPc ComfyUI GPU). No keys are in this file.

## 1. X3 LLM endpoint (tailnet only, not Funnel)
- Before: `tailscale serve status` = "No serve config" (nothing to back up). After-state JSON: `~/evo-x3/serve/x3-serve-after.json`.
- 09:45 CT: `sudo tailscale serve --bg --https=443 http://127.0.0.1:8080`
- URL: `https://evo-x3-1.tailf242b2.ts.net/` -> `http://127.0.0.1:8080` (llama-swap v272, apiKeys = 5 per-caller keys).
  `tailscale serve status` and `tailscale funnel status` both say "(tailnet only)". Persists across reboot (--bg).
- Loopback-only check: `ss -ltn` shows nothing on 0.0.0.0:8080; only Serve publishes it.
- Reachability verified: Grok Bot tailnet device -> evo-x3-1:443 reachable (tailscale_check_host); box curl
  `/v1/models` -> **502**; AlienPc curl `/v1/models` -> **502**. 502 = Serve and the TLS cert work, but llama-swap is
  stopped: the EVO-X3 bake-off stopped `llama-swap.service` at 09:18:53 CT to free the GPU for its test arms
  (ports 8090+). Not restarted by this run.
- **Pending (after the bake-off restarts llama-swap):** on the X3 run `stage/scripts/verify-serve.sh`
  (expect `no key: 401`, `LLM_KEY_BOX: 200`). The 401/200 auth checks have NOT been observed yet.

## 2. ACL
- No ACL edit was made. The Grok Bot MCP tailscale tools have no policy read/write tool, and no auth keys were created.
- Observed: box (tagged/grokbot device) and AlienPc can both open evo-x3-1:443; the X3 can open alienpc:8446.
  So the current tailnet policy allows these paths (consistent with the default allow-all policy, or a policy that
  already permits them). The policy file itself was not read.
- Plan's U8 ACL hardening (tagOwners, 443-only to the X3 for autogroup:member + existing tags, admin-only :22,
  and deny tests) is still a Derrick/Household console step: https://login.tailscale.com/admin/acls (Preview before Save).
  Suggested for the new ComfyUI port (8446 has no app-level auth): tag the X3 (e.g. `tag:evo-x3`) and allow only
  `tag:evo-x3` and Derrick's own devices to `alienpc:8446`, instead of the whole tailnet.

## 3. AlienPc pi -> X3 models
- Key: `LLM_KEY_PI` copied X3 -> box /tmp (0600) -> AlienPc %TEMP% -> User env var `EVO_X3_LLM_KEY`
  (same storage pattern as `LLAMA_SWAP_KEY`, a User env var). Temp copies zeroed/shredded on all three machines
  (X3 `shred -u`, box `shred -u`, AlienPc overwrite + delete). Value never printed; length check 64 only.
- Backup: `C:\Users\derek\.pi\agent\models.json.bak-20261115-evox3`.
- Added provider `evo-x3` to `~\.pi\agent\models.json` (baseUrl `https://evo-x3-1.tailf242b2.ts.net/v1`,
  `openai-completions`, `apiKey: "$EVO_X3_LLM_KEY"`):
  | id | ctx (per slot) | max out | thinking |
  |---|---|---|---|
  | flash-next | 32768 (Gufo --context 32768) | 8192 | yes (qwen-chat-template) |
  | gemma4-heretic | 32768 (-c 65536 -np 2) | 8192 | no |
  | qwen27b | 131072 (-c 262144 -np 2) | 16384 | yes (qwen-chat-template) |
  Text-only (no mmproj on the X3). Sampling copied from the X3 llama-swap cmd lines.
- `pi --list-models` (fresh process) lists `evo-x3 flash-next / gemma4-heretic / qwen27b` plus the unchanged
  `llama-swap` provider. `settings.json` (default model) untouched; Render's and Forge's writers untouched.
- AlienPc `C:\AI\director\config\llama-swap.yaml` NOT edited (render executor active; no peers entry added).
- **Restart pending:** 3 live `pi --remote` sessions (started 11/14 11:48 AM and 12:46 PM CT) predate the env var;
  they pick up `EVO_X3_LLM_KEY` and the new provider at their next restart. New pi processes see it now.

## 4. X3 -> AlienPc ComfyUI
- Backup: `C:\AI\backups\tailscale-serve-20261115\alienpc-serve-before.json` (8443/8444/8445 unchanged).
- 09:47 CT on AlienPc: `tailscale serve --bg --https=8446 http://127.0.0.1:8080/upstream/comfyui_auto`
  -> `https://alienpc.tailf242b2.ts.net:8446` (tailnet only). Path-scoped: only the ComfyUI upstream is
  published, not AlienPc's LLM models. ComfyUI itself still binds 127.0.0.1 (llama-swap member, on demand).
- Read-only check from the X3 (09:47 CT): `GET /system_stats` and `/api/system_stats` -> **HTTP 409**
  `{"src":"llama-swap","error":{"message":"model comfyui_auto is not loaded; path matches upstream.ignorePaths"}}`.
  This proves X3 -> tailnet -> AlienPc Serve -> llama-swap end to end, and that status GETs do not wake ComfyUI
  (by design, ignorePaths). A 200 with ComfyUI's stats needs comfyui_auto loaded (happens when a render runs).
  AlienPc GPU was idle (361 MiB, 0%, `/running` empty, no gpu-render.lock) at the time. No render queued.
- Risk: 8446 has no app auth; any tailnet device can POST /prompt, which loads ComfyUI and evicts AlienPc's loaded
  LLM. Tighten with the ACL grant above. Off switch: `tailscale serve --https=8446 off` on AlienPc.
- How an X3 job submits a saved request.api.json: `stage/scripts/comfy-submit.sh request.api.json`
  (POST `{prompt, client_id}` to `/prompt`, poll `/history/<id>`, fetch outputs via `/view?filename=..&type=output`).
  H3 renders still need Derrick's yes per prompt.
