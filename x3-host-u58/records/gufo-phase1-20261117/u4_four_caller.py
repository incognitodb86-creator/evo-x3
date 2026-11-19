#!/usr/bin/env python3
"""U4: Forge parent (flash-next, ~16K prompt, effort medium) + 3 subagents (flash-next-sub, effort low via setParamsByID,
bench tool-chain step 1 shape) fired together through llama-swap. n runs. Counts HTTP codes; key from env BENCH_KEY."""
import json,os,sys,time,threading,urllib.request,urllib.error,random
B="http://127.0.0.1:8080"; K=os.environ["BENCH_KEY"]; n=int(sys.argv[1]) if len(sys.argv)>1 else 3
fx=json.load(open('fixture_long.json')); doc=fx['system'][:int(len(fx['system'])*0.9)]
tools=[{"type":"function","function":{"name":"lookup_user","description":"Find a customer by email. Returns the user id.","parameters":{"type":"object","properties":{"email":{"type":"string"}},"required":["email"]}}},
       {"type":"function","function":{"name":"get_orders","description":"List orders for a user id.","parameters":{"type":"object","properties":{"user_id":{"type":"string"}},"required":["user_id"]}}}]
def call(name,body,out):
    t0=time.time()
    try:
        req=urllib.request.Request(B+"/v1/chat/completions",data=json.dumps(body).encode(),headers={"Content-Type":"application/json","Authorization":"Bearer "+K})
        r=json.load(urllib.request.urlopen(req,timeout=1800)); u=r.get("usage",{}); g=u.get("gufo",{})
        m=r["choices"][0]["message"]; tc=m.get("tool_calls") or []
        ok = (tc and tc[0]["function"]["name"]=="lookup_user" and json.loads(tc[0]["function"]["arguments"]).get("email")=="dana@example.com") if name!="parent" else bool((m.get("content") or "").strip())
        out[name]={"http":200,"ok":bool(ok),"wall_s":round(time.time()-t0,1),"queue_ms":round(g.get("queue_ms",0)),"ttft_s":round(g.get("ttft_ms",0)/1000,2),
                   "decode_tps":round(u.get("completion_tokens_per_second") or 0,1),"prompt_tokens":u.get("prompt_tokens"),"width":g.get("physical_execution_width"),"resident":g.get("resident_requests_at_admission")}
    except urllib.error.HTTPError as e: out[name]={"http":e.code,"ok":False,"wall_s":round(time.time()-t0,1),"body":e.read()[:200].decode('utf-8','replace')}
    except Exception as e: out[name]={"http":None,"ok":False,"err":repr(e)[:200]}
for run in range(n):
    out={}; th=[]
    pb={"model":"flash-next","messages":[{"role":"system","content":f"forge-parent {run} {random.random()}\n"+doc},{"role":"user","content":"Plan, in about 300 words, how you would split reviewing this document across three subagents."}],"max_tokens":600,"temperature":1.0}
    th.append(threading.Thread(target=call,args=("parent",pb,out)))
    for s in range(3):
        sb={"model":"flash-next-sub","messages":[{"role":"system","content":f"You are an agent (sub {s}, run {run}). Use the tools; do not guess ids."},{"role":"user","content":"How many orders does dana@example.com have? Look it up with the tools."}],"tools":tools,"max_tokens":1200,"temperature":1.0}
        th.append(threading.Thread(target=call,args=(f"sub{s}",sb,out)))
    t0=time.time()
    for t in th: t.start(); time.sleep(0.2)
    for t in th: t.join()
    codes=[v.get("http") for v in out.values()]
    print(json.dumps({"run":run,"wall_s":round(time.time()-t0,1),"n429":codes.count(429),"n503":codes.count(503),"all_200":all(c==200 for c in codes),"all_ok":all(v.get("ok") for v in out.values()),"calls":out}),flush=True)
