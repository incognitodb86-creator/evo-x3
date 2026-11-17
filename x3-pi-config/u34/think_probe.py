#!/usr/bin/env python3
"""U34 thinking-control probe: which request field changes reasoning on a slot. Key from env (LLM_KEY_BOX)."""
import json, os, sys, time, urllib.request
model = sys.argv[1]
variants = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
key = os.environ["LLM_KEY_BOX"]
prompt = "A farmer has 17 sheep; all but 9 run away. How many are left? Answer with one number."
out = {}
for name, extra in variants.items():
    body = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 2048, **extra}
    req = urllib.request.Request("http://127.0.0.1:8080/v1/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "Authorization": "Bearer " + key})
    t = time.time()
    try:
        r = json.load(urllib.request.urlopen(req, timeout=900))
        m = r["choices"][0]["message"]
        u = r.get("usage", {})
        out[name] = {"wall_s": round(time.time() - t, 1), "reasoning_chars": len(m.get("reasoning_content") or ""),
                     "reasoning_tokens": (u.get("completion_tokens_details") or {}).get("reasoning_tokens"),
                     "completion_tokens": u.get("completion_tokens"), "answer": (m.get("content") or "")[:80]}
    except Exception as e:
        out[name] = {"error": str(e)[:200]}
    print(name, json.dumps(out[name]), flush=True)
