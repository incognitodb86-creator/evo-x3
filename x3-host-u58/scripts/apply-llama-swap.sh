#!/usr/bin/env bash
# Safely validate, back up, apply, and health-check a candidate llama-swap.yaml on EVO-X3.
# Plan v3.2 Phase 0 requirement:
#   1. Require active X3 lease, validate YAML + unique aliases + `llama-swap -validate`.
#   2. Back up /etc/evo-x3/llama-swap.yaml to /etc/evo-x3/_archive/ (timestamped) and install candidate.
#   3. Restart llama-swap.service and wait up to 180s for:
#      - http://127.0.0.1:8080/health (HTTP 200)
#      - preloaded resident model(s) reporting state=="ready" in /running
#      - verify-serve.sh passing (no key: 401, LLM_KEY_BOX: 200)
#   4. On any failure, restore the backup immediately and restart llama-swap.
set -euo pipefail

LIVE_CFG="/etc/evo-x3/llama-swap.yaml"
ARCHIVE_DIR="/etc/evo-x3/_archive"
LEASE_FILE="/home/derekboone/AI/locks/x3-lease.txt"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERIFY_SERVE="${SCRIPT_DIR}/verify-serve.sh"
TIMEOUT_SECS="${LLAMA_SWAP_APPLY_TIMEOUT:-180}"

usage() {
  cat <<'EOF'
Usage:
  apply-llama-swap.sh [--validate-only] <candidate-llama-swap.yaml>

Options:
  --validate-only   Run YAML, duplicate-alias, and `llama-swap -validate` checks only.
                    Does not require a lease, back up, install, or restart llama-swap.
  -h, --help        Show this help message.
EOF
}

VALIDATE_ONLY=0
CANDIDATE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --validate-only)
      VALIDATE_ONLY=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    -*)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
    *)
      if [[ -n "$CANDIDATE" ]]; then
        echo "Unexpected extra argument: $1" >&2
        usage >&2
        exit 2
      fi
      CANDIDATE="$1"
      shift
      ;;
  esac
done

if [[ -z "$CANDIDATE" ]]; then
  usage >&2
  exit 2
fi

if [[ ! -f "$CANDIDATE" ]]; then
  echo "Candidate file not found: $CANDIDATE" >&2
  exit 1
fi
CANDIDATE="$(realpath "$CANDIDATE")"

# 1. Structural YAML + duplicate alias check + extract preloaded model IDs
PRELOAD_MODELS="$(python3 - "$CANDIDATE" <<'PY'
import sys, yaml

path = sys.argv[1]
with open(path, "r", encoding="utf-8") as f:
    doc = yaml.safe_load(f)

if not isinstance(doc, dict) or not isinstance(doc.get("models"), dict):
    sys.stderr.write("ERROR: YAML missing top-level 'models' mapping\n")
    sys.exit(1)

models = doc["models"]
seen = {}
dups = []

def record(name, owner):
    if name in seen:
        dups.append((name, seen[name], owner))
    else:
        seen[name] = owner

for model_id, cfg in models.items():
    record(str(model_id), f"model:{model_id}")
    if isinstance(cfg, dict):
        filters = cfg.get("filters") or {}
        if isinstance(filters, dict):
            sp = filters.get("setParamsByID") or {}
            if isinstance(sp, dict):
                for alias in sp.keys():
                    record(str(alias), f"setParamsByID:{model_id}")

if dups:
    for name, first, second in dups:
        sys.stderr.write(f"ERROR: duplicate model/alias '{name}' in {first} and {second}\n")
    sys.exit(1)

preload = ((doc.get("hooks") or {}).get("on_startup") or {}).get("preload") or []
for m in preload:
    if str(m) not in seen:
        sys.stderr.write(f"ERROR: preload model '{m}' not defined in models/aliases\n")
        sys.exit(1)

print(" ".join(str(m) for m in preload))
PY
)"

echo "YAML and unique-alias check passed. Preload models: ${PRELOAD_MODELS:-<none>}"

# 2. Official llama-swap -validate (with /etc/evo-x3/llm.env sourced inside root subshell)
sudo bash -c 'set -a; . /etc/evo-x3/llm.env; set +a; /usr/local/bin/llama-swap -config "$1" -validate' _ "$CANDIDATE"

if [[ "$VALIDATE_ONLY" -eq 1 ]]; then
  echo "Validation only succeeded for $CANDIDATE"
  exit 0
fi

# 3. Require active X3 lease before any live config change/restart
if [[ ! -s "$LEASE_FILE" ]]; then
  echo "ERROR: X3 lease file is missing or empty: $LEASE_FILE" >&2
  echo "Write a lease line (bot, what, start) before running live apply." >&2
  exit 1
fi

if [[ ! -f "$VERIFY_SERVE" ]]; then
  echo "ERROR: verify-serve script not found: $VERIFY_SERVE" >&2
  exit 1
fi

check_ready() {
  local health_code
  health_code="$(curl -s -o /dev/null -w '%{http_code}' -m 5 http://127.0.0.1:8080/health || true)"
  [[ "$health_code" == "200" ]] || return 1

  local running_json
  running_json="$(sudo bash -c '. /etc/evo-x3/llm.env; printf "Authorization: Bearer %s\n" "$LLM_KEY_BOX"' \
    | curl -s -m 10 -H @- http://127.0.0.1:8080/running || true)"
  [[ -n "$running_json" ]] || return 1

  python3 - "$running_json" "$PRELOAD_MODELS" <<'PY' || return 1
import json, sys

raw = sys.argv[1]
expected = [x for x in sys.argv[2].split() if x]
try:
    data = json.loads(raw)
except Exception:
    sys.exit(1)

running = {item.get("model"): item.get("state") for item in (data.get("running") or [])}
for m in expected:
    if running.get(m) != "ready":
        sys.exit(1)
PY

  local vs_out
  vs_out="$(bash "$VERIFY_SERVE" || true)"
  grep -q '^no key: 401$' <<<"$vs_out" || return 1
  grep -q '^LLM_KEY_BOX: 200$' <<<"$vs_out" || return 1
  return 0
}

wait_until_ready() {
  local deadline=$(( $(date +%s) + TIMEOUT_SECS ))
  while [[ "$(date +%s)" -le "$deadline" ]]; do
    local restarts
    restarts="$(systemctl show llama-swap -p NRestarts --value || echo 999)"
    if [[ "$restarts" != "0" ]]; then
      echo "ERROR: llama-swap NRestarts=$restarts (expected 0)" >&2
      return 1
    fi
    if systemctl is-active --quiet llama-swap && check_ready; then
      return 0
    fi
    sleep 2
  done
  return 1
}

# 4. Back up live config
TS="$(date +%Y%m%d-%H%M%S)"
BACKUP_PATH="${ARCHIVE_DIR}/llama-swap.yaml.bak-${TS}"
sudo mkdir -p "$ARCHIVE_DIR"
sudo cp -a "$LIVE_CFG" "$BACKUP_PATH"
echo "Backed up $LIVE_CFG -> $BACKUP_PATH"

# 5. Install candidate and restart llama-swap
sudo install -m 0644 -o root -g root "$CANDIDATE" "$LIVE_CFG"
echo "Installed $CANDIDATE -> $LIVE_CFG; restarting llama-swap..."
sudo systemctl restart llama-swap

if wait_until_ready; then
  echo "SUCCESS: llama-swap healthy, preloaded model(s) ready, verify-serve 401/200."
  exit 0
fi

# 6. Auto-rollback on failure
echo "ERROR: health/readiness check failed within ${TIMEOUT_SECS}s. Rolling back to $BACKUP_PATH..." >&2
sudo cp -a "$BACKUP_PATH" "$LIVE_CFG"
sudo systemctl restart llama-swap

# Re-extract original preload list for rollback readiness check
PRELOAD_MODELS="$(sudo python3 - "$BACKUP_PATH" <<'PY' || true
import sys, yaml
with open(sys.argv[1], "r", encoding="utf-8") as f:
    doc = yaml.safe_load(f) or {}
preload = ((doc.get("hooks") or {}).get("on_startup") or {}).get("preload") or []
print(" ".join(str(m) for m in preload))
PY
)"

if wait_until_ready; then
  echo "ROLLBACK OK: restored $BACKUP_PATH and confirmed llama-swap healthy." >&2
else
  echo "CRITICAL: rollback restart did not pass readiness check within ${TIMEOUT_SECS}s!" >&2
fi
exit 1
