#!/usr/bin/env python3
"""Loopback completion and embedding tests through llama-swap. No secrets."""
import json, time, sys, urllib.request, urllib.error, ssl
from datetime import datetime
from zoneinfo import ZoneInfo

BASE = "http://127.0.0.1:8080"
CT = ZoneInfo("America/Chicago")

def now():
    return datetime.now(CT).strftime("%Y-%m-%d %H:%M:%S %Z")

def req(path, body=None, method=None, timeout=600):
    data = None if body is None else json.dumps(body).encode()
    headers = {"Content-Type": "application/json"} if data else {}
    r = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    t0 = time.time()
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            raw = resp.read()
            return resp.status, json.loads(raw.decode() or "null"), time.time() - t0, dict(resp.headers)
    except urllib.error.HTTPError as e:
        raw = e.read().decode(errors="replace")
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = raw[:500]
        return e.code, parsed, time.time() - t0, dict(e.headers)
    except Exception as e:
        return 0, {"error": f"{type(e).__name__}: {e}"}, time.time() - t0, {}

def timings_of(payload):
    if not isinstance(payload, dict):
        return {}
    t = payload.get("timings") or payload.get("usage") or {}
    # llama.cpp server: timings.prompt_per_second, predicted_per_second
    out = {}
    if "prompt_per_second" in t or "predicted_per_second" in t:
        out["prompt_tok_s"] = t.get("prompt_per_second")
        out["gen_tok_s"] = t.get("predicted_per_second")
        out["prompt_n"] = t.get("prompt_n")
        out["gen_n"] = t.get("predicted_n")
        out["prompt_ms"] = t.get("prompt_ms")
        out["gen_ms"] = t.get("predicted_ms")
    # some engines put it under usage or top-level
    for k in ("prompt_per_second", "predicted_per_second", "tokens_per_second"):
        if k in payload:
            out[k] = payload[k]
    return out

results = {"started": now(), "checks": []}

def record(name, **kw):
    row = {"name": name, "at": now(), **kw}
    results["checks"].append(row)
    print(json.dumps(row, default=str), flush=True)

# 1) /v1/models (no key). With placeholders empty, auth is off so this should list models.
status, body, dt, hdrs = req("/v1/models", timeout=30)
record("v1_models", status=status, seconds=round(dt, 2), body=body)

PROMPT = "Reply with exactly the word PONG and nothing else."

def completion(model, max_tokens=16, timeout=900):
    body = {
        "model": model,
        "messages": [{"role": "user", "content": PROMPT}],
        "max_tokens": max_tokens,
        "temperature": 0,
        "stream": False,
    }
    status, payload, dt, hdrs = req("/v1/chat/completions", body, timeout=timeout)
    text = ""
    if isinstance(payload, dict):
        try:
            text = payload["choices"][0]["message"]["content"]
        except Exception:
            text = str(payload)[:400]
    return status, text, timings_of(payload) if isinstance(payload, dict) else {}, dt, payload if status != 200 else {"ok": True, "id": payload.get("id") if isinstance(payload, dict) else None}

for model, timeout in (("embed-small", 300), ("qwen27b", 900), ("gemma4-heretic", 900), ("flash-next", 1200)):
    if model == "embed-small":
        body = {"model": "embed-small", "input": "EVO-X3 embedding smoke test"}
        # try OpenAI embeddings, then llama.cpp /embedding
        status, payload, dt, hdrs = req("/v1/embeddings", body, timeout=timeout)
        dim = None
        if status != 200:
            status2, payload2, dt2, hdrs2 = req("/embedding", {"model": "embed-small", "content": "EVO-X3 embedding smoke test"}, timeout=timeout)
            if status2 == 200:
                status, payload, dt = status2, payload2, dt2
        if isinstance(payload, dict):
            try:
                vec = payload["data"][0]["embedding"]
                dim = len(vec)
            except Exception:
                try:
                    vec = payload.get("embedding")
                    dim = len(vec) if vec is not None else None
                except Exception:
                    dim = None
        record("embed-small", status=status, seconds=round(dt, 2), dim=dim, timings=timings_of(payload) if isinstance(payload, dict) else {})
        continue
    status, text, timings, dt, raw = completion(model, timeout=timeout)
    record(model, status=status, seconds=round(dt, 2), text=(text or "")[:200], timings=timings)

results["finished"] = now()
Path = __import__("pathlib").Path
outp = Path("/home/derekboone/evo-x3/model-tests.json")
outp.write_text(json.dumps(results, indent=2, default=str) + "\n")
print("WROTE", outp)
