#!/usr/bin/env bash
# Copy live X3 config into ~/evo-x3/config (secrets stripped). Live files stay the source of truth.
set -euo pipefail
D=~/evo-x3/config
mkdir -p "$D/pi" "$D/systemd" "$D/quadlet" "$D/bin" "$D/forge-pi"
cp /etc/evo-x3/llama-swap.yaml "$D/llama-swap.yaml"          # placeholders only (${env.*})
for f in settings.json AGENTS.md pi-permissions.jsonc web-search.json; do
  [ -f ~/.pi/agent/$f ] && cp ~/.pi/agent/$f "$D/pi/$f"
done
python3 - <<'P'
import json, os
src = os.path.expanduser('~/.pi/agent/models.json')
d = json.load(open(src))
def scrub(o):
    if isinstance(o, dict):
        return {k: ('<from /etc/evo-x3/llm.env>' if k.lower() in ('apikey','api_key','authorization') else scrub(v)) for k, v in o.items()}
    if isinstance(o, list):
        return [scrub(x) for x in o]
    return o
out = os.path.expanduser('~/evo-x3/config/pi/models.json.example')
json.dump(scrub(d), open(out, 'w'), indent=2); open(out, 'a').write('\n')
P
cp /etc/systemd/system/llama-swap.service "$D/systemd/"
cp /etc/systemd/system/llama-swap.service.d/*.conf "$D/systemd/"
cp /etc/systemd/system/evo-x3-*.service /etc/systemd/system/evo-x3-*.timer "$D/systemd/" 2>/dev/null || true
cp /etc/containers/systemd/open-webui.container "$D/quadlet/"
cp /usr/local/bin/evo-llama-swap "$D/bin/" 2>/dev/null || true
[ -f ~/AI/forge/.pi/settings.json ] && cp ~/AI/forge/.pi/settings.json "$D/forge-pi/settings.json"
# Host config copies (no secrets). etckeeper /etc stays LOCAL: it tracks shadow, ssh host keys and wifi PSKs.
mkdir -p "$D/host"
for f in /etc/default/grub /etc/ssh/sshd_config.d/*.conf /etc/firewalld/zones/*.xml /etc/modprobe.d/*.conf /etc/sysctl.d/*.conf /etc/tuned/active_profile; do
  [ -r "$f" ] && cp "$f" "$D/host/$(echo "${f#/etc/}" | tr / _)" 2>/dev/null || true
done
cat /proc/cmdline | sed -E 's/(root=|rd\.luks\.uuid=|luks-)[^ ]*/\1<redacted>/g' > "$D/host/proc_cmdline.txt"
grep -rIl -E '(sk-|hf_)[A-Za-z0-9]{16,}' "$D" && { echo "SECRET-LIKE STRING FOUND"; exit 1; } || true
echo synced
