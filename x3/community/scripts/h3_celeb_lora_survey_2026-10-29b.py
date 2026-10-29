r"""h3_celeb_lora_survey_2026-10-29b.py - community survey: celebrity / identity LoRAs for MiniMax-H3 (10Eros-Max).

Read-only. Uses the Hugging Face API only (Civitai is not queryable from this box - see the note).
Steps: (1) find HF repos related to H3 / 10Eros and to LoRAs, incl. TenStrip's own repos; (2) list their
files (size + lfs.oid) and classify by name into identity/celeb vs act/concept/utility; (3) read the model
cards (raw README.md) and pull every line that mentions lora/celeb/identity/character/trigger, so TenStrip's
own words are on the record; (4) save raw JSON outside git.

Usage: python h3_celeb_lora_survey_2026-10-29b.py
"""
import json, re, urllib.request, urllib.parse
from pathlib import Path

OUT = Path(r"C:\AI\lora\person_alias_2026-10-29\survey_h3_2026-10-29b.json")
UA = {"User-Agent": "pi-alienpc (read-only community survey)"}
IDENT = ["celeb", "person", "identity", "face", "idol", "likeness", "actress", "actor", "star ", "portrait",
         "character", "swap", "ts ", "personality"]
CONCEPT = ["nsfw", "sex", "position", "doggy", "cowgirl", "missionary", "anal", "blowjob", "cum", "penis",
           "pussy", "breast", "squirt", "ahegao", "hardcore", "kink", "pose"]
UTILITY = ["turbo", "lora-lcm", "lcm", "cache", "camera", "orbit", "motion", "physics", "detail", "sharp",
           "realism", "skin", "light", "style", "film", "grade", "vsa", "speed", "addguide", "guide"]
CARDS = ["TenStrip/10Eros-Max", "TenStrip/10Eros-Max-h3-8stepTURBO-beta7-int8HQ", "LokkenJP/TenEros_Max_optimized_learned"]


def get(u):
    try:
        return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40).read())
    except Exception as e:
        return {"_err": "%s %s" % (u.split("api")[0][:40], repr(e)[:110])}


def text(u):
    try:
        return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40).read().decode("utf-8", "replace")
    except Exception as e:
        return "_ERR " + repr(e)[:110]


raw, repos = {}, []
for q in ["minimax-h3", "minimax h3", "10eros", "minimax_h3", "h3 lora"]:
    r = get("https://huggingface.co/api/models?" + urllib.parse.urlencode({"search": q, "limit": 60,
              "sort": "downloads", "direction": -1, "full": "true"}))
    raw["search:" + q] = r
    if isinstance(r, list):
        for m in r:
            if m.get("id") and m["id"] not in [x[0] for x in repos]:
                repos.append((m["id"], m.get("downloads"), m.get("likes")))
repos += [("TenStrip/" + n, None, None) for n in []]
raw["author:TenStrip"] = get("https://huggingface.co/api/models?" + urllib.parse.urlencode({"author": "TenStrip", "full": "true", "limit": 60}))
if isinstance(raw["author:TenStrip"], list):
    for m in raw["author:TenStrip"]:
        if m.get("id") and m["id"] not in [x[0] for x in repos]:
            repos.append((m["id"], m.get("downloads"), m.get("likes")))

print("### HF repos found for H3 / 10Eros / LoRA queries (+ TenStrip's own), %d" % len(repos))
cand = []
for rid, dl, likes in sorted(repos, key=lambda x: -(x[1] or 0)):
    low = rid.lower()
    tag = "LORA" if ("lora" in low or any(k in low for k in IDENT)) else ("MODEL" if any(k in low for k in
          ["10eros", "minimax", "h3"]) else "OTHER")
    print("  %-6s dl=%-7s like=%-5s %s" % (tag, dl, likes, rid))
    if tag == "LORA":
        cand.append(rid)

print("\n### files inside each LoRA repo (classified by file name)")
for rid in cand:
    tr = get("https://huggingface.co/api/models/%s/tree/main?recursive=true" % rid)
    print("\n== %s" % rid)
    if isinstance(tr, dict): print("   ", tr.get("_err")); continue
    for f in tr:
        p, sz = f["path"], f.get("size", 0)
        if not p.lower().endswith((".safetensors", ".ckpt", ".pt", ".bin", ".gguf")): continue
        n = " ".join(p.lower().split("/")[-1].replace("_", " ").replace(".", " ").split())
        cls = [k for k in IDENT + CONCEPT + UTILITY if k.strip() in n]
        oid = (f.get("lfs") or {}).get("oid") or ""
        print("   %-58s %11s  id=%s cls=%s" % (p, sz, "IDENTITY" if any(k in cls for k in IDENT) else "-", ",".join(sorted(set(cls))) or "-"))

print("\n### model cards: every line mentioning lora / celeb / identity / character / trigger")
for rid in CARDS + cand[:4]:
    t = text("https://huggingface.co/%s/raw/main/README.md" % rid)
    lines = [l.strip() for l in t.splitlines() if re.search(r"lora|celeb|identity|character|trigger", l, re.I)]
    print("\n== %s (%d lines matched, README %d chars)" % (rid, len(lines), len(t)))
    for l in lines[:25]:
        print("   | " + l[:300])
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(raw, indent=1), encoding="utf-8")
print("\nraw JSON ->", OUT)
