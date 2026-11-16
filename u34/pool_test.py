#!/usr/bin/env python3
"""U34 G4 pool test: 2x~200K + 2x~32K concurrent requests on flash-next (limit 4). Needle per request; key from env."""
import json, os, time, random, urllib.request, concurrent.futures as cf
key = os.environ["LLM_KEY_BOX"]
words = "the quick brown fox jumps over a lazy dog while seven clocks ring in the old harbour town at dusk".split()
def make(tokens, needle):
    random.seed(tokens + len(needle))
    n = int(tokens * 0.75)
    body = [random.choice(words) for _ in range(n)]
    body.insert(n // 2, f" The secret code is {needle}. ")
    return " ".join(body) + "\n\nWhat is the secret code? Reply with the code only."
def run(i, tokens):
    needle = str(100000 + i * 7919)
    msg = make(tokens, needle)
    body = {"model": "flash-next", "messages": [{"role": "user", "content": msg}], "max_tokens": 256,
            "chat_template_kwargs": {"enable_thinking": False}}
    req = urllib.request.Request("http://127.0.0.1:8080/v1/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "Authorization": "Bearer " + key})
    t = time.time()
    try:
        r = json.load(urllib.request.urlopen(req, timeout=1800))
        ans = r["choices"][0]["message"].get("content") or ""
        return {"i": i, "target_tokens": tokens, "prompt_tokens": r.get("usage", {}).get("prompt_tokens"),
                "wall_s": round(time.time() - t, 1), "pass": needle in ans, "answer": ans[:40]}
    except Exception as e:
        return {"i": i, "target_tokens": tokens, "wall_s": round(time.time() - t, 1), "pass": False, "error": str(e)[:200]}
jobs = [200000, 200000, 32000, 32000]
t0 = time.time()
with cf.ThreadPoolExecutor(4) as ex:
    res = list(ex.map(lambda a: run(*a), enumerate(jobs)))
out = {"started": time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime(t0)), "total_wall_s": round(time.time() - t0, 1),
       "all_pass": all(r["pass"] for r in res), "results": res}
json.dump(out, open(os.path.expanduser("~/evo-x3/u34/pool_test_result.json"), "w"), indent=2)
print(json.dumps(out))
