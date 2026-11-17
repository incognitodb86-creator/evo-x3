#!/usr/bin/env python3
"""EVO-X3 bake-off harness. Loopback only, no auth (standalone engines). Usage:
bench.py --base http://127.0.0.1:8090 --model NAME --arm ARM --tasks long,code,tool,decode[,write] [--effort low]"""
import argparse, json, time, urllib.request, re, subprocess, sys, os
ap=argparse.ArgumentParser()
ap.add_argument('--base',required=True); ap.add_argument('--model',required=True); ap.add_argument('--arm',required=True)
ap.add_argument('--tasks',default='long,code,tool,decode'); ap.add_argument('--effort',default='low')
ap.add_argument('--out',default=None); ap.add_argument('--maxtok',type=int,default=1200)
ap.add_argument('--extra',default='{}'); ap.add_argument('--timeout',type=int,default=900)
a=ap.parse_args(); EXTRA=json.loads(a.extra)
HERE="/home/derekboone/evo-x3/bakeoff/bench"
def chat(messages, max_tokens=800, tools=None, stream=True, temperature=0.2):
    body={"model":a.model,"messages":messages,"max_tokens":max_tokens,"temperature":temperature,"stream":stream}
    if a.effort: body["reasoning_effort"]=a.effort
    if stream: body["stream_options"]={"include_usage":True}
    if tools: body["tools"]=tools
    body.update(EXTRA)
    req=urllib.request.Request(a.base+"/v1/chat/completions",data=json.dumps(body).encode(),headers=dict({"Content-Type":"application/json"}, **({"Authorization":"Bearer "+os.environ["BENCH_KEY"]} if os.environ.get("BENCH_KEY") else {})))
    t0=time.time(); ttft=None; content=""; reasoning=""; usage=None; timings=None; tcalls={}; finish=None; raw_last=None
    with urllib.request.urlopen(req,timeout=a.timeout) as r:
        for line in r:
            line=line.decode('utf-8','replace').strip()
            if not line.startswith('data:'): continue
            d=line[5:].strip()
            if d=='[DONE]': break
            try: j=json.loads(d)
            except Exception: continue
            raw_last=j
            if j.get('usage'): usage=j['usage']
            if j.get('timings'): timings=j['timings']
            for c in j.get('choices') or []:
                dl=c.get('delta') or {}
                got=False
                if dl.get('content'): content+=dl['content']; got=True
                for k in ('reasoning_content','reasoning'):
                    if dl.get(k): reasoning+=dl[k]; got=True
                for tc in dl.get('tool_calls') or []:
                    got=True; i=tc.get('index',0); e=tcalls.setdefault(i,{"id":tc.get('id'),"name":"","arguments":""})
                    f=tc.get('function') or {}
                    if f.get('name'): e['name']+=f['name']
                    if f.get('arguments'): e['arguments']+=f['arguments']
                    if tc.get('id'): e['id']=tc['id']
                if got and ttft is None: ttft=time.time()-t0
                if c.get('finish_reason'): finish=c['finish_reason']
    tot=time.time()-t0
    ct=(usage or {}).get('completion_tokens'); pt=(usage or {}).get('prompt_tokens')
    dec=(ct/(tot-ttft)) if (ct and ttft and tot>ttft) else None
    return {"ttft_s":ttft,"total_s":tot,"prompt_tokens":pt,"completion_tokens":ct,"client_decode_tps":dec,
            "timings":timings,"content":content,"reasoning_chars":len(reasoning),"tool_calls":list(tcalls.values()),"finish":finish}
res={"arm":a.arm,"model":a.model,"effort":a.effort,"started":time.strftime('%Y-%m-%d %H:%M:%S %Z'),"tasks":{}}
def save():
    if a.out: json.dump(res,open(a.out,'w'),indent=1)
for task in a.tasks.split(','):
  try:
    if task=='long':
        fx=json.load(open(os.path.join(HERE,'fixture_long.json')))
        r=chat([{"role":"system","content":fx['system']},{"role":"user","content":fx['question']}],max_tokens=a.maxtok)
        r['pass']=('TANGERINE-4471' in r['content']) and ('03:40' in r['content'])
    elif task=='code':
        prompt=("Fix the bug in this Python function. Reply with only the corrected function in one ```python code block.\n\n"
"```python\ndef median(xs):\n    \"\"\"Return the median of a non-empty list of numbers.\"\"\"\n    s = sorted(xs)\n    n = len(s)\n    mid = n // 2\n    if n % 2 == 0:\n        return s[mid]\n    return (s[mid - 1] + s[mid]) / 2\n```")
        r=chat([{"role":"user","content":prompt}],max_tokens=a.maxtok)
        m=re.findall(r"```(?:python)?\n(.*?)```",r['content'],re.S)
        ok=False
        if m:
            code=m[-1]+"\nassert median([3,1,2])==2\nassert median([4,1,3,2])==2.5\nassert median([5])==5\nassert median([1,2])==1.5\nprint('OK')\n"
            p=subprocess.run([sys.executable,'-c',code],capture_output=True,text=True,timeout=20); ok=p.stdout.strip().endswith('OK')
        r['pass']=ok
    elif task=='tool':
        tools=[{"type":"function","function":{"name":"lookup_user","description":"Find a customer by email. Returns the user id.","parameters":{"type":"object","properties":{"email":{"type":"string"}},"required":["email"]}}},
               {"type":"function","function":{"name":"get_orders","description":"List orders for a user id.","parameters":{"type":"object","properties":{"user_id":{"type":"string"}},"required":["user_id"]}}}]
        msgs=[{"role":"system","content":"You are an agent. Use the tools; do not guess ids."},{"role":"user","content":"How many orders does dana@example.com have? Look it up with the tools."}]
        r1=chat(msgs,max_tokens=a.maxtok,tools=tools)
        steps={"step1":r1}; ok1=False; ok2=False; ok3=False
        if r1['tool_calls']:
            c=r1['tool_calls'][0]
            try: args=json.loads(c['arguments'] or '{}')
            except Exception: args={}
            ok1= c['name']=='lookup_user' and args.get('email')=='dana@example.com'
            if ok1:
                cid=c.get('id') or 'call_1'
                msgs+= [{"role":"assistant","content":None,"tool_calls":[{"id":cid,"type":"function","function":{"name":c['name'],"arguments":c['arguments']}}]},
                        {"role":"tool","tool_call_id":cid,"content":json.dumps({"user_id":"u-4821","name":"Dana"})}]
                r2=chat(msgs,max_tokens=a.maxtok,tools=tools); steps['step2']=r2
                if r2['tool_calls']:
                    c2=r2['tool_calls'][0]
                    try: a2=json.loads(c2['arguments'] or '{}')
                    except Exception: a2={}
                    ok2= c2['name']=='get_orders' and a2.get('user_id')=='u-4821'
                    if ok2:
                        cid2=c2.get('id') or 'call_2'
                        msgs+=[{"role":"assistant","content":None,"tool_calls":[{"id":cid2,"type":"function","function":{"name":c2['name'],"arguments":c2['arguments']}}]},
                               {"role":"tool","tool_call_id":cid2,"content":json.dumps({"orders":[{"id":"A1"},{"id":"A2"},{"id":"A3"}]})}]
                        r3=chat(msgs,max_tokens=a.maxtok,tools=tools); steps['step3']=r3
                        ok3= bool(re.search(r"\b(3|three)\b",r3['content'],re.I))
        r={"steps":steps,"pass":ok1 and ok2 and ok3,"step_pass":[ok1,ok2,ok3]}
    elif task=='longdecode':
        fx=json.load(open(os.path.join(HERE,'fixture_long.json')))
        r=chat([{"role":"system","content":fx['system']},{"role":"user","content":"Summarize the reference document in about 600 words, as plain prose."}],max_tokens=900,temperature=0.7)
        r['pass']=r['completion_tokens'] is not None
    elif task=='decode':
        r=chat([{"role":"user","content":"Write a 500-word explanation of how a heat pump works, in plain English."}],max_tokens=900,temperature=0.7)
        r['pass']=r['completion_tokens'] is not None
    elif task.startswith('write'):
        prompts={"write1":"Write a 200-word scene: a lighthouse keeper finds a letter washed ashore. Vivid, specific, no cliches.",
                 "write2":"Write a punchy 150-word product description for a cast-iron skillet, with one surprising detail."}
        r=chat([{"role":"user","content":prompts[task]}],max_tokens=max(a.maxtok,4000),temperature=1.0)
        r['pass']=len(r['content'])>200 and r['finish']=='stop'
    else: continue
    res['tasks'][task]=r
    short={k:(v if not isinstance(v,float) else round(v,2)) for k,v in r.items() if k in('ttft_s','total_s','prompt_tokens','completion_tokens','client_decode_tps','pass','finish','step_pass')}
    print(task, json.dumps(short), flush=True)
  except Exception as e:
    res['tasks'][task]={"error":repr(e)}; print(task,"ERROR",repr(e),flush=True)
  save()
save()
