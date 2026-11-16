# Live EVO-X3 configs (sanitized)

Snapshot of what is running on the EVO-X3, with secrets stripped. Taken 2026-11-15 6:12 PM CT (America/Chicago) for G1 of the EVO plan (rev 10).

| Live path | Repo copy |
|---|---|
| `/etc/evo-x3/llama-swap.yaml` | `configs/llama-swap.yaml` and `stage/config/llama-swap/config-production.yaml` (kept identical) |
| `/etc/containers/systemd/open-webui.container` | `configs/quadlets/open-webui.container` and `stage/config/quadlets/open-webui.container` |
| `/etc/modprobe.d/ttm.conf` | `configs/modprobe.d/ttm.conf` and `stage/config/modprobe.d/ttm.conf` |
| `/etc/systemd/system/llama-swap.service` | `configs/systemd/llama-swap.service` (already matched `stage/config/systemd/llama-swap.service`) |
| `/usr/local/bin/evo-llama-swap` | `configs/systemd/evo-llama-swap` (already matched `stage/config/llama-swap/evo-llama-swap`) |
| `/proc/cmdline` and `/etc/default/grub` | `configs/kernel-args.txt` |
| `/etc/evo-x3/*.env`, `qnap.cred` | not committed; names only in `env-placeholders.md` |

After a config change on the host, copy the live file here (and the matching `stage/config/` production copy), run `ops/gitleaks-pre-push.sh`, commit, and `git push origin HEAD`.

`~/evo-x3` on the host is the live ops directory. It is not a checkout of this repo (different layout: bakeoff logs, download tarballs, in-progress records). Do not `git init` inside it.
