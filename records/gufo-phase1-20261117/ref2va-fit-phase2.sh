#!/bin/bash
# Phase 2: load ref2va, image+text tests, verify-serve. Never prints keys.
set -uo pipefail
REC=/home/derekboone/evo-x3/records/gufo-phase1-20261117
LOG=$REC/ref2va-fit-test.txt
IMG=/home/derekboone/evo-x3/bakeoff/bench/vision-test.png
SUM=$REC/ref2va-fit-summary.txt
exec > >(tee -a "$LOG") 2>&1
echo "======== PHASE2 START $(date) ========"

recover_halogen() {
  echo "=== RECOVERY: unload ref2va, stop small, drop_caches, keep halogen up ==="
  sudo -n podman stop -t 20 llama-swap-ref2va-27b 2>/dev/null || true
  sudo -n podman stop -t 20 llama-swap-joycaption 2>/dev/null || true
  # keep embed if halogen still healthy; if halogen is dead, full recover
  if ! sudo -n podman ps --format "{{.Names}}" | grep -qx llama-swap-flash-next-uncensored; then
    echo "halogen container gone; compact and reload uncensored only"
    sudo -n podman stop -t 20 llama-swap-embed-small 2>/dev/null || true
    sudo -n sync
    echo 3 | sudo -n tee /proc/sys/vm/drop_caches >/dev/null
    echo 1 | sudo -n tee /proc/sys/vm/compact_memory >/dev/null
    sudo -n bash -c 'set -a; . /etc/evo-x3/llm.env; set +a
      curl -sS -m 180 -o /tmp/ref2va-fit-recover.json -w "recover_http=%{http_code} time=%{time_total}\n" \
        -H "Authorization: Bearer ${LLM_KEY_BOX}" -H "Content-Type: application/json" \
        -d "{\"model\":\"flash-next-uncensored\",\"messages\":[{\"role\":\"user\",\"content\":\"Reply READY.\"}],\"max_tokens\":8,\"temperature\":0}" \
        http://127.0.0.1:8080/v1/chat/completions
    '
  fi
}

python3 - "$IMG" <<'PY'
import base64, json, sys, pathlib
img = pathlib.Path(sys.argv[1]).read_bytes()
b64 = base64.b64encode(img).decode()
def payload(model, text, max_tokens=128):
    return {
      "model": model,
      "messages": [{"role":"user","content":[
        {"type":"text","text": text},
        {"type":"image_url","image_url":{"url": "data:image/png;base64," + b64}}
      ]}],
      "max_tokens": max_tokens,
      "temperature": 0,
    }
pathlib.Path("/tmp/ref2va-fit-img-uncens.json").write_text(json.dumps(payload(
    "flash-next-uncensored", "In one short sentence, describe this image.")))
pathlib.Path("/tmp/ref2va-fit-img-uncens2.json").write_text(json.dumps(payload(
    "flash-next-uncensored", "Second look: name the main subject in one short sentence.")))
pathlib.Path("/tmp/ref2va-fit-img-ref2va.json").write_text(json.dumps(payload(
    "ref2va-27b", "Write a brief Ref2VA video prompt for this still: the subject looks at the camera.", 256)))
pathlib.Path("/tmp/ref2va-fit-text-ref2va.json").write_text(json.dumps({
    "model":"ref2va-27b",
    "messages":[{"role":"user","content":"Rewrite this as a short Ref2VA prompt: a person waves hello at the camera in a quiet room."}],
    "max_tokens":256,
    "temperature":0
}))
for i,t in enumerate(["Reply with the single word ONE.","Reply with the single word TWO.","Reply with the single word THREE."],1):
    pathlib.Path(f"/tmp/ref2va-fit-par{i}.json").write_text(json.dumps({
        "model":"flash-next-uncensored",
        "messages":[{"role":"user","content":t}],
        "max_tokens":8,
        "temperature":0
    }))
print("payloads ok, image_bytes", len(img))
PY

echo "=== MEM before ref2va ==="
free -h
grep MemAvailable /proc/meminfo
echo "=== dmesg oom check pre ==="
sudo -n dmesg -T | grep -iE "oom|killed process|out of memory" | tail -5 || echo "(no oom lines)"

echo "=== ref2va TEXT request (this loads the model) ==="
# memory watcher while loading
(
  for i in $(seq 1 60); do
    awk '/MemAvailable/ {printf "watch %s MemAvailable_kB=%s\n", strftime("%H:%M:%S"), $2}' /proc/meminfo
    if ! sudo -n podman ps --format "{{.Names}}" | grep -qx llama-swap-flash-next-uncensored; then
      echo "WATCH: halogen container disappeared"
      break
    fi
    sleep 3
  done
) > /tmp/ref2va-fit-memwatch.txt &
WATCH=$!

sudo -n bash -c 'set -a; . /etc/evo-x3/llm.env; set +a
curl -sS -m 300 -o /tmp/ref2va-fit-ref2va-text.json -w "ref2va_text_http=%{http_code} time=%{time_total}\n" \
  -H "Authorization: Bearer ${LLM_KEY_BOX}" -H "Content-Type: application/json" \
  -d @/tmp/ref2va-fit-text-ref2va.json \
  http://127.0.0.1:8080/v1/chat/completions
'
RT=$?
echo "ref2va_text_curl_exit=$RT"
kill $WATCH 2>/dev/null || true
wait $WATCH 2>/dev/null || true
echo "=== memwatch (head/tail) ==="
head -5 /tmp/ref2va-fit-memwatch.txt
echo "..."
tail -8 /tmp/ref2va-fit-memwatch.txt

# halogen still up?
if ! sudo -n podman ps --format "{{.Names}}" | grep -qx llama-swap-flash-next-uncensored; then
  echo "FAIL: halogen died during ref2va text load"
  sudo -n podman ps -a --format "{{.Names}} {{.Status}}"
  sudo -n dmesg -T | tail -30
  recover_halogen
  echo "RECOVERED_REF2VA_OFF $(date)"
  exit 3
fi

python3 -c 'import json,pathlib; p=pathlib.Path("/tmp/ref2va-fit-ref2va-text.json"); t=p.read_text() if p.exists() else ""
try:
 d=json.loads(t); print("ref2va_text:", (d["choices"][0]["message"].get("content") or "")[:400].replace("\n"," | "))
except Exception as e:
 print("ref2va_text_parse:", e, "raw:", t[:500])'

echo "=== MEM after ref2va text ==="
free -h
grep MemAvailable /proc/meminfo
sudo -n bash -c 'set -a; . /etc/evo-x3/llm.env; set +a; curl -s -m 10 -H "Authorization: Bearer ${LLM_KEY_BOX}" http://127.0.0.1:8080/running' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('running:', [x.get('model')+':'+x.get('state','') for x in d.get('running',[])])"

echo "=== halogen logs around ref2va load (PING/stall/oom) ==="
sudo -n podman logs --since 10m llama-swap-flash-next-uncensored 2>&1 | grep -iE "PING|stall|oom|killed|warn|error|wedge" | tail -30 || echo "(no PING/stall/oom matches)"

echo "=== ref2va IMAGE request ==="
sudo -n bash -c 'set -a; . /etc/evo-x3/llm.env; set +a
curl -sS -m 180 -o /tmp/ref2va-fit-ref2va-img.json -w "ref2va_img_http=%{http_code} time=%{time_total}\n" \
  -H "Authorization: Bearer ${LLM_KEY_BOX}" -H "Content-Type: application/json" \
  -d @/tmp/ref2va-fit-img-ref2va.json \
  http://127.0.0.1:8080/v1/chat/completions
'
python3 -c 'import json,pathlib; p=pathlib.Path("/tmp/ref2va-fit-ref2va-img.json"); t=p.read_text() if p.exists() else ""
try:
 d=json.loads(t); print("ref2va_img:", (d["choices"][0]["message"].get("content") or "")[:400].replace("\n"," | "))
except Exception as e:
 print("ref2va_img_parse:", e, "raw:", t[:500])'

if ! sudo -n podman ps --format "{{.Names}}" | grep -qx llama-swap-flash-next-uncensored; then
  echo "FAIL: halogen died during ref2va image"
  recover_halogen
  echo "RECOVERED_REF2VA_OFF $(date)"
  exit 3
fi

echo "=== MEM after ref2va image ==="
free -h
grep MemAvailable /proc/meminfo

echo "=== uncensored IMAGE #1 + 3 parallel text (ref2va still loaded) ==="
sudo -n bash -c 'set -a; . /etc/evo-x3/llm.env; set +a
curl -sS -m 180 -o /tmp/ref2va-fit-uncens-img1.json -w "uncens_img1_http=%{http_code} time=%{time_total}\n" \
  -H "Authorization: Bearer ${LLM_KEY_BOX}" -H "Content-Type: application/json" \
  -d @/tmp/ref2va-fit-img-uncens.json \
  http://127.0.0.1:8080/v1/chat/completions
'
python3 -c 'import json,pathlib; p=pathlib.Path("/tmp/ref2va-fit-uncens-img1.json"); t=p.read_text() if p.exists() else ""
try:
 d=json.loads(t); print("uncens_img1:", (d["choices"][0]["message"].get("content") or "")[:300].replace("\n"," | "))
except Exception as e:
 print("uncens_img1_parse:", e, "raw:", t[:400])'

# 3 parallel text
sudo -n bash -c 'set -a; . /etc/evo-x3/llm.env; set +a
for i in 1 2 3; do
  curl -sS -m 120 -o /tmp/ref2va-fit-par$i-out.json -w "par${i}_http=%{http_code} time=%{time_total}\n" \
    -H "Authorization: Bearer ${LLM_KEY_BOX}" -H "Content-Type: application/json" \
    -d @/tmp/ref2va-fit-par$i.json \
    http://127.0.0.1:8080/v1/chat/completions &
done
wait
'
for i in 1 2 3; do
  python3 -c 'import json,pathlib,sys; i=sys.argv[1]; p=pathlib.Path(f"/tmp/ref2va-fit-par{i}-out.json"); t=p.read_text() if p.exists() else ""
try:
 d=json.loads(t); print(f"par{i}:", (d["choices"][0]["message"].get("content") or "")[:120].replace("\n"," "))
except Exception as e:
 print(f"par{i}_parse:", e, "raw:", t[:250])' "$i"
done

echo "=== uncensored IMAGE #2 ==="
sudo -n bash -c 'set -a; . /etc/evo-x3/llm.env; set +a
curl -sS -m 180 -o /tmp/ref2va-fit-uncens-img2.json -w "uncens_img2_http=%{http_code} time=%{time_total}\n" \
  -H "Authorization: Bearer ${LLM_KEY_BOX}" -H "Content-Type: application/json" \
  -d @/tmp/ref2va-fit-img-uncens2.json \
  http://127.0.0.1:8080/v1/chat/completions
'
python3 -c 'import json,pathlib; p=pathlib.Path("/tmp/ref2va-fit-uncens-img2.json"); t=p.read_text() if p.exists() else ""
try:
 d=json.loads(t); print("uncens_img2:", (d["choices"][0]["message"].get("content") or "")[:300].replace("\n"," | "))
except Exception as e:
 print("uncens_img2_parse:", e, "raw:", t[:400])'

echo "=== post-test health ==="
if ! sudo -n podman ps --format "{{.Names}}" | grep -qx llama-swap-flash-next-uncensored; then
  echo "FAIL: halogen died after tests"
  recover_halogen
  echo "RECOVERED_REF2VA_OFF $(date)"
  exit 3
fi
free -h
grep MemAvailable /proc/meminfo
sudo -n bash -c 'set -a; . /etc/evo-x3/llm.env; set +a; curl -s -m 10 -H "Authorization: Bearer ${LLM_KEY_BOX}" http://127.0.0.1:8080/running' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('running:', [x.get('model')+':'+x.get('state','') for x in d.get('running',[])])"
echo "=== halogen PING/stall/oom after tests ==="
sudo -n podman logs --since 15m llama-swap-flash-next-uncensored 2>&1 | grep -iE "PING|stall|oom|killed process|wedge" | tail -40 || echo "(no PING/stall/oom matches)"
echo "=== dmesg oom check post ==="
sudo -n dmesg -T | grep -iE "oom|killed process|out of memory" | tail -10 || echo "(no oom lines)"

echo "=== verify-serve.sh ==="
/home/derekboone/evo-x3/scripts/verify-serve.sh

echo "PHASE2_DONE $(date)"