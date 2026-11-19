import sys, json, base64, time, types, importlib.util, urllib.request, os, argparse
ap=argparse.ArgumentParser(); ap.add_argument("--model",choices=["omni","hauhau","ref2va27","ref2va9"],required=True)
ap.add_argument("--name",required=True); ap.add_argument("--still",required=True); ap.add_argument("--ask",required=True)
ap.add_argument("--refs",default="")
a=ap.parse_args()
root=r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\custom_nodes\MiniMax-H3-Prompt-Rewriter-ComfyUI\minimax_h3_rewriter"
pkg=types.ModuleType("minimax_h3_rewriter"); pkg.__path__=[root]; sys.modules["minimax_h3_rewriter"]=pkg
def load(n):
    spec=importlib.util.spec_from_file_location("minimax_h3_rewriter."+n, os.path.join(root,n+".py"))
    m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m); return m
if a.model=="omni":
    m=load("prompt_template_omni")
    msgs=m.build_messages(a.ask, task="ref2av", resolution="9:16", duration=10.0, kinds=("image",))
    uri="data:image/jpeg;base64,"+base64.b64encode(open(a.still,"rb").read()).decode()
    for part in msgs[1]["content"]:
        if part.get("type")=="image": part.clear(); part.update({"type":"image_url","image_url":{"url":uri}})
    body={"model":"h3max_omni_rewriter","messages":msgs,"temperature":0,"top_k":1,"seed":42,"max_tokens":2048}
elif a.model in ("ref2va27","ref2va9"):
    if not a.refs.strip(): sys.exit("ref2va needs --refs 'Picture 1: ...'")
    g=load("guide_prompt")
    guide=open(r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\user\minimax_h3_rewriter\guides\VIDEO_PROMPT_WRITING_GUIDE_ref_en.md",encoding="utf-8").read()
    msgs=g.build_messages(guide, g.REF_MODE, a.ask, "9:16", 10.0, references=a.refs)
    uri="data:image/jpeg;base64,"+base64.b64encode(open(a.still,"rb").read()).decode()
    msgs[1]["content"]=[{"type":"text","text":"<Picture 1>"},{"type":"image_url","image_url":{"url":uri}},{"type":"text","text":msgs[1]["content"]}]
    body={"model":"h3_ref2va_27b" if a.model=="ref2va27" else "h3_ref2va_9b","messages":msgs,"temperature":0,"top_k":1,"seed":42,"max_tokens":4096,"chat_template_kwargs":{"enable_thinking":False}}
else:
    if not a.refs.strip(): sys.exit("hauhau needs --refs 'Picture 1: ...'")
    g=load("guide_prompt")
    guide=open(r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\user\minimax_h3_rewriter\guides\VIDEO_PROMPT_WRITING_GUIDE_ref_en.md",encoding="utf-8").read()
    msgs=g.build_messages(guide, g.REF_MODE, a.ask, "9:16", 10.0, references=a.refs)
    body={"model":"hauhaucs_writer","messages":msgs,"seed":42,"max_tokens":4096}
req=urllib.request.Request("http://127.0.0.1:8080/v1/chat/completions",json.dumps(body).encode(),{"Content-Type":"application/json"})
t=time.time(); r=json.load(urllib.request.urlopen(req,timeout=1200))
txt=r["choices"][0]["message"]["content"]
out=os.path.join(r"C:\AI\community\runs\u6_omni_rewriter_20261112", f"{a.model}_llamaswap_{a.name}"); os.makedirs(out,exist_ok=True)
open(os.path.join(out,"rewritten_prompt.txt"),"w",encoding="utf-8").write(txt)
open(os.path.join(out,"request.json"),"w",encoding="utf-8").write(json.dumps({"model":body["model"],"still":a.still,"ask":a.ask,"refs":a.refs},indent=1))
print(f"{a.model} {a.name} OK secs={time.time()-t:.0f} chars={len(txt)} tokens={r.get('usage',{}).get('completion_tokens')} out={out}")
