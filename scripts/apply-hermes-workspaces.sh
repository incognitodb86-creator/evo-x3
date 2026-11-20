#!/usr/bin/env bash
# apply-hermes-workspaces.sh — Set up Hermes Render (default) + Coding (code) workspaces on EVO-X3
# using 3 zero-swap Gufo 0.35.0 aliases (flash-next-render, flash-next-code, flash-next-aux),
# restore Gemma pins + pin ref2va, and archive the hand-made gemma profile.
#
# Decisions (Derrick 2026-11-20 ~9:07 AM CT):
#   D1: flash-next-render presence_penalty=0.0 (override with --render-presence 1.5 for A/B)
#   D2/D2b: code profile thinking=medium, Gufo default 8192 budget
#   D3: archive gemma profile + restore llama-swap pins; keep 25 GiB weights on disk
#   D4: keep 30-workspace.conf during apply; test WebUI profile chip first
#   D7: pin ref2va-27b-heretic-q4 -> flash-next-uncensored-v2
#
# Usage:
#   bash scripts/apply-hermes-workspaces.sh --dry-run          # default: inspect & preview only
#   bash scripts/apply-hermes-workspaces.sh --apply            # take X3 lease, back up, apply, probe
#   bash scripts/apply-hermes-workspaces.sh --rollback         # take X3 lease, restore backups, restart

set -euo pipefail

MODE="dry-run"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
RENDER_PRESENCE="0.0"
CODE_THINKING="medium"
LEASE_FILE="/home/derekboone/AI/locks/x3-lease.txt"
LLAMA_CFG="/etc/evo-x3/llama-swap.yaml"
LLAMA_BAK="/etc/evo-x3/_archive/llama-swap.yaml-20261120-preWS"
HERMES_HOME_DIR="/home/evo/.hermes"
HERMES_BAK="${HERMES_HOME_DIR}/_archive/20261120-ws"
CODE_WS="/home/evo/AI/hermes-code"
RENDER_WS="/home/evo/workspace"
STAGE_DIR=""
LEASE_HELD=0
PY_EVO="/home/evo/AI/render/x3/.venv/bin/python3"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) MODE="dry-run"; shift ;;
    --apply) MODE="apply"; shift ;;
    --rollback) MODE="rollback"; shift ;;
    --repo) REPO_DIR="$2"; shift 2 ;;
    --render-presence) RENDER_PRESENCE="$2"; shift 2 ;;
    --code-thinking) CODE_THINKING="$2"; shift 2 ;;
    -h|--help)
      sed -n '2,18p' "$0"; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

case "$CODE_THINKING" in
  medium|low) ;;
  *) echo "Invalid --code-thinking '$CODE_THINKING' (use medium or low)" >&2; exit 2 ;;
esac

ts_ct() { TZ=America/Chicago date '+%Y-%m-%d %H:%M:%S CT'; }

cleanup() {
  if [[ -n "$STAGE_DIR" && -d "$STAGE_DIR" ]]; then
    rm -rf "$STAGE_DIR" || true
  fi
  if [[ "$LEASE_HELD" -eq 1 ]]; then
    : > "$LEASE_FILE" || true
    LEASE_HELD=0
    echo "[$(ts_ct)] Lease cleared: $LEASE_FILE"
  fi
}
trap cleanup EXIT

take_lease() {
  local what="$1"
  mkdir -p "$(dirname "$LEASE_FILE")"
  if [[ -s "$LEASE_FILE" ]]; then
    echo "BLOCKED: X3 lease is not empty ($LEASE_FILE):" >&2
    cat "$LEASE_FILE" >&2
    exit 1
  fi
  printf '%s | %s | %s\n' "${USER:-derekboone}" "$what" "$(ts_ct)" > "$LEASE_FILE"
  LEASE_HELD=1
  echo "[$(ts_ct)] Lease taken: $(cat "$LEASE_FILE")"
}

check_sources() {
  local f
  for f in \
    "$REPO_DIR/hosts/x3/hermes/workspaces/render/AGENTS.md" \
    "$REPO_DIR/hosts/x3/hermes/workspaces/code/AGENTS.md" \
    "$REPO_DIR/hosts/x3/hermes/workspaces/code/MEMORY.md"; do
    [[ -f "$f" ]] || { echo "MISSING source file: $f (use --repo <mono-clone>)" >&2; exit 1; }
  done
  local sha
  sha="$(git -C "$REPO_DIR" rev-parse --short HEAD 2>/dev/null || echo 'no-git')"
  echo "[$(ts_ct)] Repo: $REPO_DIR (HEAD $sha) | mode=$MODE | render_presence=$RENDER_PRESENCE | code_thinking=$CODE_THINKING"
}

check_idle() {
  if command -v pi-job >/dev/null 2>&1; then
    local st
    st="$(sudo -n -iu evo pi-job status 2>/dev/null || true)"
    if grep -qiE 'RUNNING|QUEUED' <<<"$st"; then
      echo "BLOCKED: active pi-job detected:" >&2
      echo "$st" >&2
      exit 1
    fi
  fi
}

probe_alias() {
  local model="$1" prompt="$2" max_tok="$3" extra_json="${4:-}"
  local payload
  payload="{\"model\":\"${model}\",\"messages\":[{\"role\":\"user\",\"content\":\"${prompt}\"}],\"max_tokens\":${max_tok}${extra_json}}"
  sudo -n -iu evo bash -c '
    set -euo pipefail
    (
      set -a
      # shellcheck disable=SC1091
      . /home/evo/.config/evo-x3/llm.env
      printf "header = \"Authorization: Bearer %s\"\n" "$LLM_KEY_HERMES"
    ) | curl -sS -w "\nHTTP_CODE:%{http_code}\n" -K - \
        -H "Content-Type: application/json" \
        http://127.0.0.1:8080/v1/chat/completions -d "$1"
  ' _ "$payload"
}

check_probe_output() {
  local label="$1" raw="$2" expect_reasoning="$3" expect_substr="${4:-}"
  PROBE_RAW="$raw" python3 - "$label" "$expect_reasoning" "$expect_substr" <<'PY'
import json, os, sys
label, exp_reason, exp_sub = sys.argv[1], sys.argv[2], sys.argv[3]
text = os.environ.get("PROBE_RAW", "")
marker = "\nHTTP_CODE:"
if marker not in text:
    print(f"FAIL {label}: missing HTTP_CODE")
    sys.exit(1)
body, code = text.rsplit(marker, 1)
code = code.strip()
if code != "200":
    print(f"FAIL {label}: HTTP {code} body={body[:300]}")
    sys.exit(1)
d = json.loads(body)
msg = (d.get("choices") or [{}])[0].get("message") or {}
content = (msg.get("content") or "").strip()
rc = (msg.get("reasoning_content") or "").strip()
usage = d.get("usage") or {}
has_r = bool(rc)
if exp_reason == "no" and has_r:
    print(f"FAIL {label}: expected no reasoning, got {len(rc)} chars")
    sys.exit(1)
if exp_reason == "yes" and not has_r:
    print(f"FAIL {label}: expected reasoning_content, got empty")
    sys.exit(1)
if exp_sub and exp_sub not in content:
    print(f"FAIL {label}: expected {exp_sub!r} in content={content[:120]!r}")
    sys.exit(1)
print(f"PASS {label}: HTTP 200 reasoning={has_r} ({len(rc)}c) content={content[:80]!r} usage={usage}")
PY
}

patch_llama_swap() {
  local target="$1" dry="$2"
  local pybin="python3"
  [[ -x "$PY_EVO" ]] && pybin="$PY_EVO"
  sudo -n "$pybin" - "$target" "$RENDER_PRESENCE" "$dry" <<'PY'
import os, re, sys, yaml

path, render_pres, dry = sys.argv[1], float(sys.argv[2]), (sys.argv[3] == "1")
raw = open(path, encoding="utf-8").read()
cfg = yaml.safe_load(raw)
m = cfg["models"]["flash-next-uncensored-v2"]
assert m.get("concurrencyLimit") == 4, f"unexpected concurrencyLimit={m.get('concurrencyLimit')}"
sp = m.get("filters", {}).get("setParamsByID", {})
assert "flash-next-uncensored-v2-sub" in sp and "flash-next-uncensored-sub" in sp, "missing existing -sub aliases"

# Comment-preserving surgical patch of only the flash-next-uncensored-v2 setParamsByID block and halogen-only pins.
BEGIN_A = "        # BEGIN-HERMES-WS-ALIASES"
END_A = "        # END-HERMES-WS-ALIASES"
alias_block = f"""{BEGIN_A}
        "flash-next-render":
          chat_template_kwargs:
            enable_thinking: false
          temperature: 0.7
          top_p: 0.8
          top_k: 20
          min_p: 0.0
          presence_penalty: {render_pres}
        "flash-next-code":
          temperature: 1.0
          top_p: 0.95
          top_k: 20
          min_p: 0.0
          presence_penalty: 0.0
        "flash-next-aux":
          chat_template_kwargs:
            enable_thinking: false
          temperature: 0.35
          top_p: 0.9
          top_k: 20
          min_p: 0.0
          presence_penalty: 0.0
{END_A}"""

text = raw
# Remove any previous managed block or hand-added aliases inside flash-next-uncensored-v2
text = re.sub(r"\n?        # BEGIN-HERMES-WS-ALIASES[\s\S]*?        # END-HERMES-WS-ALIASES", "", text)
for existing in ("flash-next-render", "flash-next-code", "flash-next-aux"):
    text = re.sub(rf'\n        "{existing}":[^\n]*(?:\n          [^\n]*)*', "", text)

anchor = '        "flash-next-uncensored-sub":\n          reasoning_effort: low'
assert anchor in text, "could not find flash-next-uncensored-sub anchor in llama-swap.yaml"
text = text.replace(anchor, anchor + "\n" + alias_block, 1)

# Restore gemma4-heretic / gemma4-heretic-sub pins and add ref2va-27b-heretic-q4 pin (D3, D7)
for pin_key in ("gemma4-heretic", "gemma4-heretic-sub"):
    text = re.sub(rf"^      #\s*{pin_key}:\s*flash-next-uncensored-v2\s*$",
                  f"      {pin_key}: flash-next-uncensored-v2", text, flags=re.M)
    if not re.search(rf"^      {pin_key}:\s*flash-next-uncensored-v2\s*$", text, flags=re.M):
        text = re.sub(r"^(      qwen27b: flash-next-uncensored-v2\s*)$",
                      rf"\1\n      {pin_key}: flash-next-uncensored-v2", text, count=1, flags=re.M)

if not re.search(r"^      ref2va-27b-heretic-q4:\s*flash-next-uncensored-v2\s*$", text, flags=re.M):
    text = re.sub(r"^(      qwen27b: flash-next-uncensored-v2\s*)$",
                  r"\1\n      ref2va-27b-heretic-q4: flash-next-uncensored-v2", text, count=1, flags=re.M)

check = yaml.safe_load(text)
new_sp = check["models"]["flash-next-uncensored-v2"]["filters"]["setParamsByID"]
new_pins = check["profiles"]["halogen-only"]["pins"]
assert {"flash-next-render", "flash-next-code", "flash-next-aux",
        "flash-next-uncensored-v2-sub", "flash-next-uncensored-sub"} <= set(new_sp)
assert new_pins["gemma4-heretic"] == "flash-next-uncensored-v2"
assert new_pins["gemma4-heretic-sub"] == "flash-next-uncensored-v2"
assert new_pins["ref2va-27b-heretic-q4"] == "flash-next-uncensored-v2"
assert check["models"]["flash-next-uncensored-v2"]["concurrencyLimit"] == 4

if dry:
    print("[dry-run] llama-swap setParamsByID keys:", sorted(new_sp.keys()))
    print("[dry-run] halogen-only pins:", sorted(new_pins.keys()))
    sys.exit(0)

tmp = path + ".tmp-ws"
with open(tmp, "w", encoding="utf-8") as fh:
    fh.write(text)
os.chmod(tmp, 0o644)
os.replace(tmp, path)
print("OK: patched (comments preserved)", path)
PY
}

patch_hermes_profile() {
  local cfg_path="$1" role="$2" dry="$3"
  local pybin="python3"
  [[ -x "$PY_EVO" ]] && pybin="$PY_EVO"
  sudo -n -iu evo "$pybin" - "$cfg_path" "$role" "$CODE_THINKING" "$CODE_WS" "$dry" <<'PY'
import os, sys, yaml

path, role, code_think, code_ws, dry = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], (sys.argv[5] == "1")
cfg = yaml.safe_load(open(path, encoding="utf-8"))
aux_entry = {
    "provider": "custom",
    "model": "flash-next-aux",
    "base_url": "http://127.0.0.1:8080/v1",
    "reasoning_effort": "false",
    "key_env": "LLM_KEY_HERMES",
}
aux = cfg.setdefault("auxiliary", {})
for slot in ("vision", "compression", "approval", "title_generation"):
    aux[slot] = dict(aux_entry)

cfg.setdefault("model", {})["context_length"] = 131072
assert cfg["model"].get("key_env") == "LLM_KEY_HERMES", "key_env missing"
assert cfg.get("secrets", {}).get("command", {}).get("enabled") is True, "secrets.command missing"
hooks = (cfg.get("hooks") or {}).get("pre_tool_call") or []
assert any("guard-render-queue.sh" in str(h.get("command", "")) for h in hooks), "guard-render-queue.sh hook missing"

if role == "render":
    cfg["model"]["default"] = "flash-next-render"
    cfg["model"]["reasoning_effort"] = False
    cfg.setdefault("agent", {})["reasoning_effort"] = False
elif role == "code":
    cfg["model"]["default"] = "flash-next-code"
    cfg["model"]["reasoning_effort"] = code_think
    cfg.setdefault("agent", {})["reasoning_effort"] = code_think
    cfg.setdefault("terminal", {})["cwd"] = code_ws
    sk = cfg.setdefault("skills", {})
    sk["external_dirs"] = []
    dis = list(sk.get("disabled") or [])
    for name in ("h3-render", "h3-writer", "pixlstash-image-library"):
        if name not in dis:
            dis.append(name)
    sk["disabled"] = dis
else:
    raise ValueError(role)

if dry:
    print(f"[dry-run] {role} ({path}): model={cfg['model']['default']} "
          f"model.re={cfg['model']['reasoning_effort']} agent.re={cfg['agent']['reasoning_effort']} "
          f"cwd={cfg['terminal']['cwd']} aux={sorted(aux.keys())}")
    sys.exit(0)

out = yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True)
yaml.safe_load(out)
tmp = path + ".tmp-ws"
with open(tmp, "w", encoding="utf-8") as fh:
    fh.write(out)
os.chmod(tmp, 0o600)
os.replace(tmp, path)
print(f"OK: patched {role} config ({path})")
PY
}

do_rollback() {
  take_lease "UNI-APPLY-X3-HERMES-WORKSPACES rollback"
  [[ -f "$LLAMA_BAK" ]] || { echo "Missing backup: $LLAMA_BAK" >&2; exit 1; }
  sudo -n cp -a "$LLAMA_BAK" "$LLAMA_CFG"
  sudo -n systemctl restart llama-swap
  sudo -n -iu evo bash -c '
    set -euo pipefail
    B="'"$HERMES_BAK"'"
    [[ -f "$B/config.yaml" ]] && cp -a "$B/config.yaml" "'"$HERMES_HOME_DIR"'/config.yaml"
    [[ -f "$B/workspace.AGENTS.md" ]] && cp -a "$B/workspace.AGENTS.md" "'"$RENDER_WS"'/AGENTS.md"
    [[ -d "'"$HERMES_HOME_DIR"'/profiles/code" ]] && mv "'"$HERMES_HOME_DIR"'/profiles/code" "$B/profiles-code-rolledback-$(date +%H%M%S)"
    [[ -d "'"$CODE_WS"'" ]] && mv "'"$CODE_WS"'" "$B/ws-code-rolledback-$(date +%H%M%S)"
    [[ -d "$B/profiles-gemma" && ! -d "'"$HERMES_HOME_DIR"'/profiles/gemma" ]] && mv "$B/profiles-gemma" "'"$HERMES_HOME_DIR"'/profiles/gemma"
  '
  sudo -n systemctl --user -M evo@ restart hermes-gateway
  echo "[$(ts_ct)] Rollback complete."
}

check_sources

if [[ "$MODE" == "rollback" ]]; then
  do_rollback
  exit 0
fi

if [[ "$MODE" == "dry-run" ]]; then
  echo "=== DRY RUN (no live changes) ==="
  patch_llama_swap "$LLAMA_CFG" 1
  patch_hermes_profile "${HERMES_HOME_DIR}/config.yaml" render 1
  echo "[dry-run] Would clone default -> code profile, write $CODE_WS/AGENTS.md + code/memories/MEMORY.md,"
  echo "          set model=flash-next-code, model+agent reasoning_effort=$CODE_THINKING, disable render skills,"
  echo "          route auxiliary.{compression,vision,approval,title_generation} -> flash-next-aux,"
  echo "          archive $HERMES_HOME_DIR/profiles/gemma (weights untouched), and restart llama-swap + hermes-gateway."
  echo "Run with --apply to execute."
  exit 0
fi

# === APPLY ===
START_CT="$(ts_ct)"
check_idle
take_lease "UNI-APPLY-X3-HERMES-WORKSPACES"

echo "=== Step 0: Backups ==="
sudo -n mkdir -p /etc/evo-x3/_archive
if [[ ! -f "$LLAMA_BAK" ]]; then
  sudo -n cp -a "$LLAMA_CFG" "$LLAMA_BAK"
  echo "Backed up $LLAMA_CFG -> $LLAMA_BAK"
else
  echo "Keeping existing pre-WS backup: $LLAMA_BAK"
fi

sudo -n -iu evo env HERMES_HOME="$HERMES_HOME_DIR" bash -c '
  set -euo pipefail
  B="'"$HERMES_BAK"'"
  mkdir -p "$B"
  [[ -f "$B/config.yaml" ]] || cp -a "'"$HERMES_HOME_DIR"'/config.yaml" "$B/config.yaml"
  [[ -f "$B/workspace.AGENTS.md" ]] || cp -a "'"$RENDER_WS"'/AGENTS.md" "$B/workspace.AGENTS.md"
  hermes config show > "$B/config-show.before.txt" 2>&1 || true
  hermes profile list > "$B/profiles.before.txt" 2>&1 || true
'

echo "=== Step 1: Patch llama-swap & probe aliases BEFORE touching Hermes ==="
patch_llama_swap "$LLAMA_CFG" 0
sudo -n systemctl restart llama-swap

echo "Waiting for flash-next-uncensored-v2 on /running (up to 120s)..."
READY=0
for _ in $(seq 1 40); do
  if curl -sS http://127.0.0.1:8080/running 2>/dev/null | grep -q 'flash-next-uncensored-v2'; then
    READY=1; break
  fi
  sleep 3
done
[[ "$READY" -eq 1 ]] || { echo "FAIL: flash-next-uncensored-v2 not ready in /running; run --rollback" >&2; exit 1; }

P_RENDER="$(probe_alias flash-next-render 'Say OK.' 32 '')"
check_probe_output "flash-next-render" "$P_RENDER" "no" "OK"

P_AUX="$(probe_alias flash-next-aux 'Say OK.' 32 '')"
check_probe_output "flash-next-aux" "$P_AUX" "no" "OK"

P_CODE="$(probe_alias flash-next-code 'What is 17*23? Reply with just the number.' 1024 '')"
check_probe_output "flash-next-code" "$P_CODE" "yes" "391"

echo "=== Step 2: Update Render workspace (default profile) ==="
# Stage source files via world-readable temp dir in case repo is owned by derekboone (0700 home).
STAGE_DIR="$(mktemp -d /tmp/hermes-ws-stage.XXXXXX)"
chmod 0755 "$STAGE_DIR"
cp "$REPO_DIR/hosts/x3/hermes/workspaces/render/AGENTS.md" "$STAGE_DIR/render.AGENTS.md"
cp "$REPO_DIR/hosts/x3/hermes/workspaces/code/AGENTS.md" "$STAGE_DIR/code.AGENTS.md"
cp "$REPO_DIR/hosts/x3/hermes/workspaces/code/MEMORY.md" "$STAGE_DIR/code.MEMORY.md"
chmod 0644 "$STAGE_DIR"/*

patch_hermes_profile "${HERMES_HOME_DIR}/config.yaml" render 0
sudo -n -iu evo install -m 0644 "$STAGE_DIR/render.AGENTS.md" "${RENDER_WS}/AGENTS.md"

echo "=== Step 3: Create & configure Coding workspace (code profile) ==="
sudo -n -iu evo env HERMES_HOME="$HERMES_HOME_DIR" bash -c '
  set -euo pipefail
  if [[ ! -d "'"$HERMES_HOME_DIR"'/profiles/code" ]]; then
    hermes profile create code --clone --no-alias
  fi
  printf "description: Coding workspace (flash-next-code, thinking %s, delegates edits to pi-job)\ndescription_auto: false\n" "'"$CODE_THINKING"'" \
    > "'"$HERMES_HOME_DIR"'/profiles/code/profile.yaml"
  mkdir -p "'"$CODE_WS"'" "'"$HERMES_HOME_DIR"'/profiles/code/memories"
  install -m 0644 "'"$STAGE_DIR"'/code.AGENTS.md" "'"$CODE_WS"'/AGENTS.md"
  install -m 0644 "'"$STAGE_DIR"'/code.MEMORY.md" "'"$HERMES_HOME_DIR"'/profiles/code/memories/MEMORY.md"
'
rm -rf "$STAGE_DIR"
patch_hermes_profile "${HERMES_HOME_DIR}/profiles/code/config.yaml" code 0

echo "=== Step 4: Archive hand-made gemma profile (weights untouched per D3) ==="
sudo -n -iu evo bash -c '
  if [[ -d "'"$HERMES_HOME_DIR"'/profiles/gemma" ]]; then
    mv "'"$HERMES_HOME_DIR"'/profiles/gemma" "'"$HERMES_BAK"'/profiles-gemma"
    echo "Archived profiles/gemma -> '"$HERMES_BAK"'/profiles-gemma"
  else
    echo "profiles/gemma already absent"
  fi
'

echo "=== Step 5: Restart hermes-gateway & run end-to-end smoke checks ==="
sudo -n systemctl --user -M evo@ restart hermes-gateway
sleep 3
sudo -n systemctl --user -M evo@ is-active hermes-gateway

RUNNING_OUT="$(curl -sS http://127.0.0.1:8080/running)"
echo "/running: $RUNNING_OUT"

RENDER_SMOKE="$(sudo -n -iu evo env HERMES_HOME="$HERMES_HOME_DIR" hermes chat --oneshot -Q -q \
  'Which skill renders a video, and which changes code? One short line.' 2>&1 | tail -n 5)"
echo "Render oneshot: $RENDER_SMOKE"

CODE_SMOKE="$(sudo -n -iu evo env HERMES_HOME="$HERMES_HOME_DIR" hermes -p code chat --oneshot -Q -q \
  'Run pwd, then name the skill that changes code. One short line.' 2>&1 | tail -n 5)"
echo "Code oneshot: $CODE_SMOKE"

CODE_SKILLS="$(sudo -n -iu evo env HERMES_HOME="$HERMES_HOME_DIR" hermes -p code skills list 2>&1 | grep -E 'h3-render|h3-writer|pi-job' || true)"
echo "Code skills check:"
echo "$CODE_SKILLS"

END_CT="$(ts_ct)"
RESULT_PATH="$REPO_DIR/records/UNI-APPLY-X3-HERMES-WORKSPACES/RESULT.md"
if [[ ! -w "$(dirname "$RESULT_PATH")" ]]; then
  RESULT_PATH="/tmp/UNI-APPLY-X3-HERMES-WORKSPACES-RESULT.md"
fi
cat > "$RESULT_PATH" <<EOF
# UNI-APPLY-X3-HERMES-WORKSPACES RESULT

- **When:** ${START_CT} to ${END_CT}
- **Script:** \`scripts/apply-hermes-workspaces.sh --apply --render-presence ${RENDER_PRESENCE} --code-thinking ${CODE_THINKING}\`
- **Backups:** \`${LLAMA_BAK}\`, \`${HERMES_BAK}/\`
- **llama-swap /running:** \`${RUNNING_OUT}\`
- **Render oneshot:** \`${RENDER_SMOKE}\`
- **Code oneshot:** \`${CODE_SMOKE}\`
- **Code skills check:**
\`\`\`
${CODE_SKILLS}
\`\`\`
- **WebUI D4 check:** open Hermes WebUI, pick profile \`code\`, ask \`pwd\`. If WebUI forces \`/home/evo/workspace\`, archive \`/home/evo/.config/systemd/user/hermes-webui.service.d/30-workspace.conf\` and restart \`hermes-webui\`.
EOF
echo "Wrote RESULT: $RESULT_PATH"
echo "DONE. Remember to verify WebUI profile switch (D4) and commit RESULT.md if desired."
