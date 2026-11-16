#!/usr/bin/env python3
"""Quick image-description probe. Neutral synthetic PNG only."""
import argparse, json, time, urllib.request, base64, os, re, sys
ap=argparse.ArgumentParser()
ap.add_argument('--base', required=True)
ap.add_argument('--model', required=True)
ap.add_argument('--arm', required=True)
ap.add_argument('--image', required=True)
ap.add_argument('--out', required=True)
a=ap.parse_args()
img=open(a.image,'rb').read()
b64=base64.b64encode(img).decode()
url=a.base.rstrip('/')+"/v1/chat/completions"
payload={
  "model": a.model,
  "messages":[{"role":"user","content":[
      {"type":"image_url","image_url":{"url":"data:image/png;base64,"+b64}},
      {"type":"text","text":"Describe this image in one short paragraph. Name every shape you see, the color of each shape, and transcribe any text exactly."}
  ]}],
  "max_tokens": 4000,
  "temperature": 0.2,
  "stream": False,
  "chat_template_kwargs": {"enable_thinking": False},
  "reasoning_effort": "low",
}
req=urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type":"application/json"})
t0=time.time()
try:
    with urllib.request.urlopen(req, timeout=600) as r:
        body=r.read()
        code=r.status
except Exception as e:
    res={"arm":a.arm,"model":a.model,"error":repr(e),"elapsed_s":time.time()-t0,"vision_works":False}
    json.dump(res, open(a.out,'w'), indent=2)
    print("ERROR", repr(e), flush=True)
    sys.exit(1)
elapsed=time.time()-t0
data=json.loads(body)
choice=(data.get("choices") or [{}])[0]
msg=choice.get("message") or {}
content=msg.get("content") or ""
# some servers put reasoning separately
usage=data.get("usage") or {}
tim=data.get("timings") or {}
text=content.lower()
# expected elements of the synthetic image
checks={
  "yellow_or_gold_circle": bool(re.search(r"yellow|gold|amber", text) and re.search(r"circle|disk|disc|round", text)),
  "red_square": bool(re.search(r"red|crimson|scarlet", text) and re.search(r"square|rectangle", text)),
  "green_triangle": bool(re.search(r"green", text) and re.search(r"triangle", text)),
  "text_x3_bakeoff": bool(re.search(r"x3[-\s]?bakeoff", text, re.I)),
}
works=sum(checks.values())>=3  # at least 3 of 4 visual facts
res={
  "arm":a.arm,"model":a.model,"http":code,"elapsed_s":round(elapsed,3),
  "ttft_s": tim.get("prompt_ms",0)/1000.0 if tim.get("prompt_ms") is not None else None,
  "prompt_tokens": usage.get("prompt_tokens") or tim.get("prompt_n"),
  "completion_tokens": usage.get("completion_tokens") or tim.get("predicted_n"),
  "prompt_per_second": tim.get("prompt_per_second"),
  "predicted_per_second": tim.get("predicted_per_second"),
  "timings": tim,
  "usage": usage,
  "finish": choice.get("finish_reason"),
  "content": content,
  "checks": checks,
  "checks_passed": sum(checks.values()),
  "vision_works": works,
}
# If timings only have prompt_ms, wait ~= prefill time
if res["ttft_s"] is None and tim.get("predicted_ms") is not None:
    res["ttft_s"]=tim.get("prompt_ms",0)/1000.0
json.dump(res, open(a.out,'w'), indent=2)
print("VISION", json.dumps({k:res[k] for k in ("elapsed_s","ttft_s","prompt_tokens","completion_tokens","prompt_per_second","predicted_per_second","checks","vision_works","finish")}), flush=True)
print("TEXT:", content[:800], flush=True)
