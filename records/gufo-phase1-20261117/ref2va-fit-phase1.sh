#!/bin/bash
# 2026-11-17 t61u/t62u ref2va-fit test. Never prints keys.
set -uo pipefail
REC=/home/derekboone/evo-x3/records/gufo-phase1-20261117
LOG=$REC/ref2va-fit-test.txt
IMG=/home/derekboone/evo-x3/bakeoff/bench/vision-test.png
mkdir -p "$REC"
exec > >(tee -a "$LOG") 2>&1
echo "======== START $(date) ========"

auth() {
  sudo -n bash -c 'set -a; . /etc/evo-x3/llm.env; set +a; curl "$@"' _ "$@"
}

echo "=== pre-restart mem ==="
free -h
echo "=== stop any model containers, drop_caches, compact, restart llama-swap ==="
for c in llama-swap-embed-small llama-swap-ref2va-27b llama-swap-joycaption llama-swap-flash-next-uncensored llama-swap-flash-next llama-swap-gemma4-heretic llama-swap-qwen27b; do
  sudo -n podman stop -t 20 "$c" 2>/dev/null || true
done
sudo -n sync
echo 3 | sudo -n tee /proc/sys/vm/drop_caches >/dev/null
echo 1 | sudo -n tee /proc/sys/vm/compact_memory >/dev/null
sleep 1
free -h
sudo -n systemctl restart llama-swap
sleep 2
systemctl is-active llama-swap || { echo "LLAMA_SWAP_NOT_ACTIVE"; systemctl status llama-swap --no-pager | tail -20; exit 2; }

echo "=== hold side models, kick halogen ==="
hold_sides() {
  for c in llama-swap-embed-small llama-swap-ref2va-27b llama-swap-joycaption; do
    if sudo -n podman ps --format "{{.Names}}" | grep -qx "$c"; then
      echo "STOP $c (halogen-first)"
      sudo -n podman stop -t 10 "$c" || true
    fi
  done
}
for i in 1 2 3 4 5 6; do hold_sides; sleep 0.3; done

sudo -n bash -c 'set -a; . /etc/evo-x3/llm.env; set +a
curl -sS -m 180 -o /tmp/ref2va-fit-kick.json -w "kick_http=%{http_code} time=%{time_total}\n" \
  -H "Authorization: Bearer ${LLM_KEY_BOX}" -H "Content-Type: application/json" \
  -d "{\"model\":\"flash-next-uncensored\",\"messages\":[{\"role\":\"user\",\"content\":\"Reply with the single word READY.\"}],\"max_tokens\":16,\"temperature\":0}" \
  http://127.0.0.1:8080/v1/chat/completions
' &
KICK_PID=$!

ok=0
for i in $(seq 1 90); do
  if sudo -n podman ps --format "{{.Names}}" | grep -qx llama-swap-flash-next-uncensored; then
    logs=$(sudo -n podman logs --tail 120 llama-swap-flash-next-uncensored 2>&1 || true)
    if echo "$logs" | grep -q "host memory left for everything else"; then
      echo "HALOGEN_READY at $(date) iter=$i"
      echo "$logs" | grep -E "KV budget|slots:|listening on|host memory left|memory:|reserving the KV pool|KV pool reserved|HALOGEN_KV|HALOGEN_CTX" || true
      ok=1
      break
    fi
    if echo "$logs" | grep -qiE "refusing to pin|HIP .* out of memory|fatal"; then
      echo "HALOGEN_START_FAIL"
      echo "$logs" | tail -50
      break
    fi
  fi
  hold_sides
  sleep 2
done

if [[ "$ok" -ne 1 ]]; then
  echo "HALOGEN_NOT_READY"
  sudo -n podman ps -a --format "{{.Names}} {{.Status}}"
  sudo -n podman logs --tail 100 llama-swap-flash-next-uncensored 2>&1 || true
  wait $KICK_PID || true
  exit 2
fi

echo "=== wait kick ==="
wait $KICK_PID || true
python3 -c 'import json,pathlib; p=pathlib.Path("/tmp/ref2va-fit-kick.json"); t=p.read_text() if p.exists() else "";
try:
 d=json.loads(t); print("kick_text:", (d["choices"][0]["message"].get("content") or "")[:200].replace("\n"," "))
except Exception as e:
 print("kick_parse:", e, "raw:", t[:400])'

echo "=== MEM AFTER HALOGEN (before side models) ==="
free -h
grep MemAvailable /proc/meminfo
sudo -n podman logs llama-swap-flash-next-uncensored 2>&1 | grep -E "host memory left|listening on|slots:|KV budget|startup \[.*\] memory:" | tail -20
# snapshot dmesg
sudo -n dmesg -T | tail -20 | tee /tmp/ref2va-fit-dmesg-pre.txt >/dev/null
echo "DMESG_PRE_SAVED"

echo "=== load embed-small after halogen ==="
sudo -n bash -c 'set -a; . /etc/evo-x3/llm.env; set +a
curl -sS -m 90 -o /tmp/ref2va-fit-embed.json -w "embed_http=%{http_code} time=%{time_total}\n" \
  -H "Authorization: Bearer ${LLM_KEY_BOX}" -H "Content-Type: application/json" \
  -d "{\"model\":\"embed-small\",\"input\":\"ping\"}" \
  http://127.0.0.1:8080/v1/embeddings
'
echo "=== MEM after embed ==="
free -h
grep MemAvailable /proc/meminfo
sudo -n bash -c 'set -a; . /etc/evo-x3/llm.env; set +a; curl -s -m 10 -H "Authorization: Bearer ${LLM_KEY_BOX}" http://127.0.0.1:8080/running' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('running:', [x.get('model')+':'+x.get('state','') for x in d.get('running',[])])"

echo "PHASE1_DONE $(date)"