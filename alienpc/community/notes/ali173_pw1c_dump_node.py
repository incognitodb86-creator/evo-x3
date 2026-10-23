"""PW1c: save the raw /object_info spec of the prompt-rewriter node classes to a small file.

Run this in the SAME tool call that woke ComfyUI (llama-swap unloads ComfyUI as soon as the
next model turn starts - ALI-173 iter 04: a check in a later call hits a refused port).
Parsing happens later, off the saved file, on CPU.

The per-node endpoint (/object_info/<class>) keeps the fetch small: ~5 MB for the whole graph
would be dumped into notes for nothing.
"""
import json
import sys
import urllib.request

PORT = sys.argv[1]
OUT = sys.argv[2]
CLASSES = sys.argv[3:] or ["MiniMaxH3PromptWriterOmni", "MiniMaxH3RewriterOptions"]
rep = {}
for cls in CLASSES:
    try:
        raw = urllib.request.urlopen("http://127.0.0.1:%s/object_info/%s" % (PORT, cls),
                                     timeout=120).read()
        rep[cls] = json.loads(raw).get(cls)
        print("%s: %d bytes" % (cls, len(raw)), flush=True)
    except Exception as e:
        rep[cls] = {"error": str(e)}
        print("%s: %s" % (cls, e), flush=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(rep, f, indent=1, ensure_ascii=False)
print("saved -> " + OUT)
