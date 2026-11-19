#!/usr/bin/env bash
# U57: show exactly what pi sends for each --thinking level to x3-local/flash-next-uncensored (reasoning_effort,
# chat_template_kwargs, sampling, max_tokens). pi talks to a throwaway local capture server, so this uses no GPU,
# no llama-swap slot and no API key (the model entry is copied from models.json with a dummy key).
# Run as evo:  bash probe-pi-thinking.sh [model-id]      (default flash-next-uncensored)
# Reading the result: Halogen honours a top-level reasoning_effort (U34 probe); when a row has none, the server
# default HALOGEN_REASONING_EFFORT=medium applies. Qwen3.8-Flash-Next supports low, medium and xhigh.
set -euo pipefail
MODEL_ID="${1:-flash-next-uncensored}"
MODELS="${PI_MODELS_JSON:-$HOME/.pi/agent/models.json}"
command -v pi >/dev/null || export PATH="$HOME/.local/bin:$PATH"
TMP="$(mktemp -d)"; chmod 700 "$TMP"
cleanup() { [ -n "${SRV:-}" ] && kill "$SRV" 2>/dev/null; rm -rf "$TMP"; }
trap cleanup EXIT

python3 - "$MODELS" "$MODEL_ID" "$TMP" <<'PY'
import json, sys, pathlib
src, mid, tmp = pathlib.Path(sys.argv[1]), sys.argv[2], pathlib.Path(sys.argv[3])
d = json.loads(src.read_text(encoding="utf-8"))
m = next((m for p in d.get("providers", {}).values() for m in p.get("models", []) if m.get("id") == mid), None)
if m is None:
    sys.exit(f"model {mid} not found in {src}")
x3 = d["providers"].get("x3-local", {})
prov = {k: v for k, v in x3.items() if k not in ("models", "apiKey", "baseUrl", "headers")}
prov.update(baseUrl="http://127.0.0.1:PORT/v1", apiKey="probe-dummy", models=[m])
(tmp / "agent").mkdir()
(tmp / "agent/models.json").write_text(json.dumps({"providers": {"capture": prov}}, indent=2))
(tmp / "agent/settings.json").write_text(json.dumps({"defaultProvider": "capture", "enableInstallTelemetry": False,
                                                     "enableAnalytics": False}))
PY

cat > "$TMP/server.py" <<'PY'
import json, sys, http.server
out = open(sys.argv[1], "a", buffering=1)
class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        b = json.dumps({"object": "list", "data": []}).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
        body.pop("messages", None); body.pop("tools", None)
        out.write(json.dumps(body) + "\n")
        chunk = {"id": "p", "object": "chat.completion.chunk", "created": 0, "model": body.get("model", ""),
                 "choices": [{"index": 0, "delta": {"role": "assistant", "content": "OK"}, "finish_reason": None}]}
        done = dict(chunk, choices=[{"index": 0, "delta": {}, "finish_reason": "stop"}],
                    usage={"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2})
        if body.get("stream"):
            self.send_response(200); self.send_header("Content-Type", "text/event-stream"); self.end_headers()
            for c in (chunk, done):
                self.wfile.write(b"data: " + json.dumps(c).encode() + b"\n\n")
            self.wfile.write(b"data: [DONE]\n\n")
        else:
            b = json.dumps({"id": "p", "object": "chat.completion", "created": 0, "model": body.get("model", ""),
                            "choices": [{"index": 0, "message": {"role": "assistant", "content": "OK"},
                                         "finish_reason": "stop"}], "usage": done["usage"]}).encode()
            self.send_response(200); self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
s = http.server.HTTPServer(("127.0.0.1", 0), H)
open(sys.argv[2], "w").write(str(s.server_address[1]))
s.serve_forever()
PY
python3 "$TMP/server.py" "$TMP/requests.jsonl" "$TMP/port" & SRV=$!
for _ in $(seq 50); do [ -s "$TMP/port" ] && break; sleep 0.1; done
[ -s "$TMP/port" ] || { echo "capture server did not start" >&2; exit 1; }
sed -i "s/PORT/$(cat "$TMP/port")/" "$TMP/agent/models.json"

printf '%-8s %-6s %s\n' level rc "what pi sent (messages and tools omitted)"
cd "$TMP"
for lvl in off minimal low medium high xhigh; do
  n_before=$(wc -l < "$TMP/requests.jsonl" 2>/dev/null || echo 0)
  rc=0
  PI_CODING_AGENT_DIR="$TMP/agent" timeout 60 pi --offline --print --no-session --no-context-files --no-extensions \
    --no-skills --no-mcp --model "capture/$MODEL_ID" --thinking "$lvl" "Reply with OK." >"$TMP/out.$lvl" 2>&1 || rc=$?
  if [ "$(wc -l < "$TMP/requests.jsonl" 2>/dev/null || echo 0)" -gt "$n_before" ]; then
    sent=$(tail -n 1 "$TMP/requests.jsonl" | python3 -c 'import json,sys
d=json.load(sys.stdin)
keep=("reasoning_effort","enable_thinking","chat_template_kwargs","reasoning","temperature","top_p","top_k","min_p","presence_penalty","max_tokens","max_completion_tokens")
print(json.dumps({k:d[k] for k in keep if k in d}))')
  else
    sent="(no request; pi said: $(head -c 200 "$TMP/out.$lvl" | tr '\n' ' '))"
  fi
  printf '%-8s %-6s %s\n' "$lvl" "$rc" "$sent"
done
