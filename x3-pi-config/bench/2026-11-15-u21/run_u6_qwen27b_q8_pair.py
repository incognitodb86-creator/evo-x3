#!/usr/bin/env python3
"""Run the U6 18k fixture_long.json tasks (long, longdecode, decode) on live qwen27b
(UD-Q8_K_XL + DFlash2 on Gufo) via llama-swap to complement the existing U6 Q4 AR vs DFlash2 pair."""
import datetime
import json
import os
import subprocess
import time
import urllib.request
from zoneinfo import ZoneInfo

CT = ZoneInfo("America/Chicago")
OUT_DIR = "/home/derekboone/evo-x3/bench/2026-11-15-u21"
FIXTURE = "/home/derekboone/evo-x3/bakeoff/bench/fixture_long.json"
BASE = "http://127.0.0.1:8080/v1/chat/completions"


def chat(key, model, messages, max_tokens, temperature, effort="low"):
    body = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "reasoning_effort": effort,
        "stream": True,
        "stream_options": {"include_usage": True},
    }
    req = urllib.request.Request(
        BASE,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        method="POST",
    )
    t0 = time.monotonic()
    ttft = None
    content = ""
    reasoning = ""
    usage = None
    timings = None
    finish = None
    with urllib.request.urlopen(req, timeout=900) as r:
        for line in r:
            line = line.decode("utf-8", "replace").strip()
            if not line.startswith("data:"):
                continue
            d = line[5:].strip()
            if d == "[DONE]":
                break
            try:
                j = json.loads(d)
            except Exception:
                continue
            if j.get("usage"):
                usage = j["usage"]
            if j.get("timings"):
                timings = j["timings"]
            for c in j.get("choices") or []:
                dl = c.get("delta") or {}
                got = bool(dl.get("content") or dl.get("reasoning_content") or dl.get("reasoning"))
                if dl.get("content"):
                    content += dl["content"]
                for k in ("reasoning_content", "reasoning"):
                    if dl.get(k):
                        reasoning += dl[k]
                if got and ttft is None:
                    ttft = time.monotonic() - t0
                if c.get("finish_reason"):
                    finish = c["finish_reason"]
    tot = time.monotonic() - t0
    ct = (usage or {}).get("completion_tokens")
    pt = (usage or {}).get("prompt_tokens")
    dec = (ct / (tot - ttft)) if (ct and ttft and tot > ttft) else None
    return {
        "ttft_s": round(ttft or 0, 3),
        "total_s": round(tot, 3),
        "prompt_tokens": pt,
        "completion_tokens": ct,
        "client_decode_tps": round(dec, 2) if dec else None,
        "timings": timings,
        "finish": finish,
        "reasoning_chars": len(reasoning),
        "content": content,
    }


def main():
    key = os.environ.get("LLM_KEY_BOX") or os.environ.get("OPENAI_API_KEY")
    if not key:
        raise SystemExit("LLM_KEY_BOX not set")
    fx = json.load(open(FIXTURE))
    res = {
        "arm": "u21-qwen27b-q8-gufo-dflash2",
        "model": "qwen27b",
        "quant": "Qwen3.8-27B-UD-Q8_K_XL + DFlash2-Q4_K_M",
        "started_ct": datetime.datetime.now(CT).strftime("%Y-%m-%d %H:%M:%S %Z"),
        "tasks": {},
    }
    r_long = chat(key, "qwen27b", [{"role": "system", "content": fx["system"]}, {"role": "user", "content": fx["question"]}], 1200, 0.2)
    r_long["pass"] = ("TANGERINE-4471" in r_long["content"]) and ("03:40" in r_long["content"])
    res["tasks"]["long"] = r_long
    print("long:", r_long["pass"], "ttft:", r_long["ttft_s"], "ptok:", r_long["prompt_tokens"], "timings:", bool(r_long["timings"]))

    r_ld = chat(key, "qwen27b", [{"role": "system", "content": fx["system"]}, {"role": "user", "content": "Summarize the reference document in about 600 words, as plain prose."}], 900, 0.7)
    r_ld["pass"] = r_ld["completion_tokens"] is not None
    res["tasks"]["longdecode"] = r_ld
    print("longdecode:", r_ld["pass"], "ctok:", r_ld["completion_tokens"], "dec:", r_ld["client_decode_tps"])

    r_dec = chat(key, "qwen27b", [{"role": "user", "content": "Write a 500-word explanation of how a heat pump works, in plain English."}], 900, 0.7)
    r_dec["pass"] = r_dec["completion_tokens"] is not None
    res["tasks"]["decode"] = r_dec
    print("decode:", r_dec["pass"], "ctok:", r_dec["completion_tokens"], "dec:", r_dec["client_decode_tps"])

    res["finished_ct"] = datetime.datetime.now(CT).strftime("%Y-%m-%d %H:%M:%S %Z")
    out_p = os.path.join(OUT_DIR, "u6_27b_gufo_q8_dflash2_fixture.json")
    json.dump(res, open(out_p, "w"), indent=2)
    print("Saved", out_p)


if __name__ == "__main__":
    main()
