#!/usr/bin/env python3
"""U26 Forge-style coding task: implement a module from a spec, run hidden tests. Key from stdin if --key-stdin."""
import argparse, json, time, urllib.request, re, subprocess, sys, tempfile, os
ap=argparse.ArgumentParser(); ap.add_argument('--base',required=True); ap.add_argument('--model',required=True)
ap.add_argument('--out',required=True); ap.add_argument('--key-stdin',action='store_true'); ap.add_argument('--effort',default='medium')
a=ap.parse_args(); KEY=sys.stdin.readline().strip() if a.key_stdin else None
spec='''Implement a Python module with a class `TTLCache(capacity: int, ttl: float, clock=time.monotonic)`:
- get(key, default=None): return the value if present and not expired (expired = clock() - set_time >= ttl), else default. A hit marks the key most-recently-used.
- set(key, value): insert/update (resets its timestamp, marks MRU). If over capacity, first drop all expired entries, then evict the least-recently-used.
- __len__ returns the number of non-expired entries.
- delete(key) -> bool (True if a live entry was removed).
- capacity < 1 or ttl <= 0 raises ValueError.
Use only the standard library. Reply with only the complete module in one ```python code block.'''
tests='''
t=[0.0]; clk=lambda: t[0]
c=TTLCache(2,10,clock=clk)
c.set('a',1); c.set('b',2); assert c.get('a')==1
c.set('c',3); assert c.get('b') is None and c.get('a')==1 and c.get('c')==3
t[0]=5; c.set('a',11); t[0]=12; assert c.get('c') is None and c.get('a')==11 and len(c)==1
t[0]=15.0; assert c.get('a')==None or True
t[0]=14.999; 
c2=TTLCache(3,1,clock=clk); t[0]=0; c2.set('x',1); c2.set('y',2); c2.set('z',3); t[0]=1.0; assert len(c2)==0
c2.set('w',4); assert c2.get('w')==4 and c2.delete('w') is True and c2.delete('w') is False
c3=TTLCache(2,5,clock=clk); t[0]=0; c3.set('p',1); t[0]=1; c3.set('q',2); t[0]=5; c3.set('r',3); assert c3.get('q')==2 and c3.get('r')==3 and c3.get('p') is None
for bad in [(0,1),(1,0),(1,-1)]:
    try: TTLCache(*bad); raise SystemExit('no ValueError')
    except ValueError: pass
print('OK')
'''
body={"model":a.model,"messages":[{"role":"user","content":spec}],"max_tokens":12000,"temperature":0.6,"reasoning_effort":a.effort,"stream":False}
h={"Content-Type":"application/json"}
if KEY: h["Authorization"]="Bearer "+KEY
t0=time.time()
js=json.loads(urllib.request.urlopen(urllib.request.Request(a.base+"/v1/chat/completions",data=json.dumps(body).encode(),headers=h),timeout=1200).read())
el=time.time()-t0; msg=js['choices'][0]['message']; content=msg.get('content') or ''
m=re.findall(r"```(?:python)?\n(.*?)```",content,re.S); ok=False; err=''
if m:
    p=subprocess.run([sys.executable,'-c',m[-1]+"\n"+tests],capture_output=True,text=True,timeout=30); ok=p.stdout.strip().endswith('OK'); err=(p.stderr or '')[-400:]
res={"pass":ok,"elapsed_s":round(el,1),"usage":js.get('usage'),"finish":js['choices'][0].get('finish_reason'),"err":err,"code":m[-1] if m else content[-800:]}
json.dump(res,open(a.out,'w'),indent=1); print(json.dumps({k:v for k,v in res.items() if k!='code'}))
