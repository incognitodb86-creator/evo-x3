#!/usr/bin/env bash
# Copy live X3 setup (configs, units, launchers, Hermes/pi/herdr/PixlStash config) into ~/evo-x3/hosts/x3/live.
# Read-only on live files. Secrets are replaced with <redacted-in-locked-keyfile>. Max Architect, Derrick t2613u.
set -uo pipefail
R=~/evo-x3/hosts/x3/live
rm -rf "$R"; mkdir -p "$R"/{containers,tailscale,ssh,agy,herdr,hermes/skills,pi-derekboone/agent,pi-evo/panes/forge,pi-evo/panes/render}
E() { sudo -n -u evo "$@"; }
cpe() { # cpe <evo-src> <dest>  (copy evo-owned file)
  mkdir -p "$(dirname "$2")"; E cat "$1" > "$2" 2>/dev/null || { rm -f "$2"; echo "skip $1"; }; }
cpr() { mkdir -p "$(dirname "$2")"; sudo -n cat "$1" > "$2" 2>/dev/null || { rm -f "$2"; echo "skip $1"; }; }
SCRUB=$(cat <<'P'
import sys, re, json
pat = re.compile(r'(api[_-]?key|apikey|token|secret|password|passwd|bearer|authorization|credential|private[_-]?key)', re.I)
safe_val = re.compile(r'^(\$\{.*\}|!cat .*|<.*>|/.*|env:.*|)$')
src, dst = sys.argv[1], sys.argv[2]
txt = sys.stdin.read()
if src.endswith('.json') or src.endswith('.jsonc') and txt.lstrip().startswith('{') and '//' not in txt:
    try:
        d = json.loads(txt)
        def s(o):
            if isinstance(o, dict):
                return {k: ('<redacted-in-locked-keyfile>' if pat.search(k) and isinstance(v, str) and not safe_val.match(v) else s(v)) for k, v in o.items()}
            if isinstance(o, list): return [s(x) for x in o]
            return o
        open(dst, 'w').write(json.dumps(s(d), indent=2) + '\n'); sys.exit(0)
    except Exception:
        pass
out = []
for line in txt.splitlines():
    m = re.match(r'^(\s*-?\s*"?([A-Za-z0-9_.-]+)"?\s*[:=]\s*)(.*)$', line)
    if m and pat.search(m.group(2)):
        v = m.group(3).strip().strip('",\'')
        if v and not safe_val.match(v) and v not in ('true','false','null','~','{','[') and not re.match(r'^\d+$', v):
            line = m.group(1) + '"<redacted-in-locked-keyfile>"'
    out.append(line)
open(dst, 'w').write('\n'.join(out) + '\n')
P
)
scrub_evo() { mkdir -p "$(dirname "$2")"; E cat "$1" 2>/dev/null | python3 -c "$SCRUB" "$1" "$2" || echo "skip $1"; }
scrub_root() { mkdir -p "$(dirname "$2")"; sudo -n cat "$1" 2>/dev/null | python3 -c "$SCRUB" "$1" "$2" || echo "skip $1"; }

# --- llama-swap (Gufo, Halogen, strix toolboxes are launched from here)
scrub_root /etc/evo-x3/llama-swap.yaml "$R/llama-swap/llama-swap.yaml"
cpr /etc/systemd/system/llama-swap.service "$R/llama-swap/llama-swap.service"
for f in /etc/systemd/system/llama-swap.service.d/*.conf; do cpr "$f" "$R/llama-swap/llama-swap.service.d/$(basename "$f")"; done
cpr /usr/local/bin/evo-llama-swap "$R/llama-swap/evo-llama-swap"
cpr /etc/sysctl.d/90-halogen-compaction.conf "$R/llama-swap/sysctl.d_90-halogen-compaction.conf"
/usr/local/bin/llama-swap --version > "$R/llama-swap/llama-swap-version.txt" 2>&1 || true

# --- system units (custom only)
for f in /etc/systemd/system/*.service /etc/systemd/system/*.timer /etc/systemd/system/*.mount /etc/systemd/system/*.automount; do
  [ -f "$f" ] && [ ! -L "$f" ] && cpr "$f" "$R/systemd/system/$(basename "$f")"; done
systemctl list-unit-files --state=enabled --no-pager > "$R/systemd/system-enabled-units.txt" 2>/dev/null || true

# --- evo user units
for f in $(E find /home/evo/.config/systemd/user -maxdepth 2 -type f -not -path '*/_archive/*' \( -name '*.service' -o -name '*.timer' -o -name '*.conf' \)); do
  cpe "$f" "$R/systemd/evo-user/${f#/home/evo/.config/systemd/user/}"; done
sudo -n systemctl --user -M evo@ list-unit-files --state=enabled --no-pager > "$R/systemd/evo-user-enabled-units.txt" 2>/dev/null || true
for f in /etc/containers/systemd/open-webui.container ~/.config/containers/systemd/searxng.container; do
  [ -r "$f" ] || sudo -n test -r "$f" && scrub_root "$f" "$R/containers/$(basename "$f")"; done

# --- /usr/local/bin scripts (not binaries, not .bak)
for f in /usr/local/bin/*; do case "$f" in *.bak*|*/llama-swap) continue;; esac
  sudo -n file "$f" | grep -q text && cpr "$f" "$R/bin/$(basename "$f")"; done

# --- pi (evo)
A=/home/evo/.pi/agent
for f in AGENTS.md settings.json pi-permissions.jsonc web-search.json trust.json npm/package.json extensions/herdr-agent-state.ts extensions/pi-permission-system/config.json extensions/subagent/config.json pi-subagents/last-seen-version.json pi-web-access/last-seen-version.json; do
  E test -f "$A/$f" && scrub_evo "$A/$f" "$R/pi-evo/agent/$f"; done
scrub_evo "$A/mcp.json" "$R/pi-evo/agent/mcp.json"
cpe "$A/npm/package-lock.json" "$R/pi-evo/agent/npm/package-lock.json"
E cat "$A/models.json" | python3 -c '
import json,sys,re
d=json.load(sys.stdin)
def s(o):
  if isinstance(o,dict): return {k:("<redacted-in-locked-keyfile>" if re.fullmatch("api[_-]?key|apikey|authorization|token|bearer",k,re.I) and isinstance(v,str) else s(v)) for k,v in o.items()}
  if isinstance(o,list): return [s(x) for x in o]
  return o
json.dump(s(d),open(sys.argv[1],"w"),indent=2)' "$R/pi-evo/agent/models.json.example"
for p in forge render; do
  for f in $(E find /home/evo/.pi/panes/$p -maxdepth 1 \( -type f -o -type l \) 2>/dev/null); do
    b=$(basename "$f")
    if E test -L "$f"; then echo "$b -> $(E readlink "$f")" >> "$R/pi-evo/panes/$p/SYMLINKS.txt"
    else case "$b" in auth.json|models-store.json|*.secret|*.log) continue;; esac; scrub_evo "$f" "$R/pi-evo/panes/$p/$b"; fi
  done; done
for f in README.md render-pi.sh forge-pi.sh; do E test -f /home/evo/evo-x3/pi-chats/$f && scrub_evo /home/evo/evo-x3/pi-chats/$f "$R/pi-evo/pi-chats/$f"; done
for f in $(E find /home/evo/evo-x3/scripts -type f -not -path '*/_archive/*'); do scrub_evo "$f" "$R/pi-evo/evo-x3-scripts/${f#/home/evo/evo-x3/scripts/}"; done
E test -f /home/evo/.pi/agent/pi-mobile/config.json && scrub_evo /home/evo/.pi/agent/pi-mobile/config.json "$R/pi-evo/agent/pi-mobile/config.json"

# --- pi (derekboone, Max's own harness)
for f in AGENTS.md settings.json pi-permissions.jsonc web-search.json; do [ -f ~/.pi/agent/$f ] && python3 -c "$SCRUB" "$f" "$R/pi-derekboone/agent/$f" < ~/.pi/agent/$f; done

# --- Hermes
H=/home/evo/.hermes
scrub_evo $H/config.yaml "$R/hermes/config.yaml"
cpe $H/SOUL.md "$R/hermes/SOUL.md"
cpe $H/.gitignore "$R/hermes/gitignore"
cpe $H/skills/.bundled_manifest "$R/hermes/skills/bundled_manifest.txt"
E git -C $H/hermes-agent log -1 --format='hermes-agent %H %cd %s' > "$R/hermes/hermes-agent-version.txt" 2>/dev/null
E git -C $H/hermes-agent remote get-url origin >> "$R/hermes/hermes-agent-version.txt" 2>/dev/null
E git -C $H diff -- skills > "$R/hermes/skills/local-edits-to-bundled-skills.diff" 2>/dev/null
# custom (non-bundled) skills: copy in full
BUND=$(E cut -d: -f1 $H/skills/.bundled_manifest)
for s in $(E find $H/skills -name SKILL.md -not -path '*/_archive/*' -not -path '*/.locks/*'); do
  d=$(dirname "$s"); n=$(basename "$d")
  echo "$BUND" | grep -qx "$n" && continue
  for f in $(E find "$d" -type f -not -path '*/_archive/*'); do scrub_evo "$f" "$R/hermes/skills/custom/${f#$H/skills/}"; done
done
E find $H/skills -name SKILL.md -not -path '*/_archive/*' | sed "s#$H/skills/##" | sort > "$R/hermes/skills/all-skills.txt"
E ls -la $H/memories > "$R/hermes/memories-listing.txt" 2>/dev/null
for f in $(E find $H/hooks $H/plugins -maxdepth 2 -type f 2>/dev/null); do scrub_evo "$f" "$R/hermes/${f#$H/}"; done

# --- herdr
cpe /home/evo/.config/herdr/config.toml "$R/herdr/config.toml"
herdr --version > "$R/herdr/herdr-version.txt" 2>&1 || true

# --- PixlStash (config only; no DB, library, tokens, password)
scrub_evo /home/evo/.config/pixlstash/server-config.json "$R/pixlstash/server-config.json"
for f in tag_runner.py import_inbox.py index_backfill.py index_map.py joycaption_compare.py; do
  E test -f /home/evo/AI/pixlstash-tagging/$f && scrub_evo /home/evo/AI/pixlstash-tagging/$f ~/evo-x3/hosts/x3/pixlstash-tagging/$f; done

# --- forge-mcp launchers (tokens stay in evo-only files)
for f in $(E find /home/evo/.config/forge-mcp -maxdepth 1 -name 'run-*.sh'); do scrub_evo "$f" "$R/forge-mcp/$(basename "$f")"; done
cpe /home/evo/.config/aria2/aria2.conf "$R/aria2/aria2.conf"

# --- host bits
{ echo "# podman images (rootful)"; sudo -n podman images --format '{{.Repository}}:{{.Tag}} {{.Digest}}'
  echo "# podman images (derekboone)"; podman images --format '{{.Repository}}:{{.Tag}} {{.Digest}}'; } > "$R/containers/images.txt" 2>/dev/null
{ tailscale version; echo; echo "# serve"; tailscale serve status 2>&1; } > "$R/tailscale/tailscale.txt" 2>/dev/null || true
for f in ~/.ssh/config; do [ -f "$f" ] && cpr "$f" "$R/ssh/derekboone-ssh-config"; done
agy --version > "$R/agy/agy-version.txt" 2>&1 || true
{ echo "# nested community repos kept out of this repo (name, remote, commit)";
  for d in ~/evo-x3/bench/quant-bench ~/evo-x3/src/gemma4-gufo-extension; do echo "$d $(git -C $d remote get-url origin 2>/dev/null) $(git -C $d rev-parse HEAD)"; done
  for d in /home/evo/.hermes/hermes-agent; do echo "$d $(E git -C $d remote get-url origin) $(E git -C $d rev-parse HEAD)"; done
} > "$R/nested-repos.txt"
find "$R" -type f | wc -l
