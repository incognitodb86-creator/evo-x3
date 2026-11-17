#!/usr/bin/env python3
"""speed.py BASE MODEL TARGET_TOKENS LABEL [n] : non-stream request, prompt ~TARGET tokens built from fixture_long.json,
unique prefix per run (no cache reuse), max_tokens 512, effort low, temp 0.7. Prints engine prefill/decode from usage."""
import json,sys,time,os,urllib.request,random
base,model,target,label=sys.argv[1],sys.argv[2],int(sys.argv[3]),sys.argv[4]; n=int(sys.argv[5]) if len(sys.argv)>5 else 1
fx=json.load(open('/home/derekboone/evo-x3/records/gufo-phase1-20261117/fixture_long.json'))
doc=fx['system']; per=18253/len(doc)  # fixture is 18,253 Qwen tokens
need=int(target/per); text=(doc*((need//len(doc))+1))[:need]
for i in range(n):
    body={"model":model,"messages":[{"role":"system","content":f"run {label}-{i}-{random.random()}\n"+text},
          {"role":"user","content":"Write about 400 words summarizing the reference document as plain prose."}],
          "max_tokens":512,"temperature":0.7,"reasoning_effort":"low","stream":False}
    h={"Content-Type":"application/json"}
    if os.environ.get("BENCH_KEY"): h["Authorization"]="Bearer "+os.environ["BENCH_KEY"]
    t0=time.time()
    r=json.load(urllib.request.urlopen(urllib.request.Request(base+"/v1/chat/completions",data=json.dumps(body).encode(),headers=h),timeout=1800))
    tot=time.time()-t0; u=r.get("usage",{}); g=u.get("gufo",{})
    pt,ct=u.get("prompt_tokens"),u.get("completion_tokens")
    print(json.dumps({"label":label,"run":i,"prompt_tokens":pt,"completion_tokens":ct,
      "engine_prefill_tps":round(u.get("prompt_tokens_per_second") or 0,1),"engine_decode_tps":round(u.get("completion_tokens_per_second") or 0,1),
      "ttft_s":round((g.get("ttft_ms") or 0)/1000,2),"queue_ms":round(g.get("queue_ms") or 0,1),"draft_acc":f'{u.get("draft_tokens_accepted")}/{u.get("draft_tokens")}',
      "plan":g.get("execution_plan"),"wall_s":round(tot,1),"client_e2e_decode_tps":round(ct/(tot-(g.get("ttft_ms") or 0)/1000),1) if ct else None}),flush=True)
