r"""h3_lora_social_sweep3.py - the 3rd pass that fixes the API parameters and builds the real catalog.

Findings from pass 2 that this pass fixes:
  - Civitai REST v1 /models/{id} works and is the proof field: baseModel, trainedWords, file sizes. It already
    proved 3 LoRAs with baseModel = "MiniMax H3" (a face-identity swap LoRA, a face/speech LoRA, a style LoRA).
  - The Civitai LIST endpoint rejected my sort values: the ZodError lists the allowed ones ("Most Downloaded",
    "Highest Rated", "Hot", ...) - spaces, not camelCase. Fixed here, and the allowed enums are printed once.
  - Arctic Shift rate-limited (422/429) at full speed: calls are paced and retried.
  - The Reddit threads found in pass 2 are saved in the non-git web folder; this pass greps them for LoRA links and
    the community's statements about name-reference identity, printed with person names masked.
Read-only, no downloads, no GPU.
Usage: python h3_lora_social_sweep3.py
"""
import json, re, time, urllib.request, urllib.parse
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129 Safari/537.36"}
PRIV = Path(r"C:\AI\lora\person_alias_2026-10-29\TRIGGER_MAP_private.txt")
WEB = Path(r"C:\AI\lora\person_alias_2026-10-29\web_2026-10-29")
NAMES = set(re.findall(r"[A-Z][a-z]{2,}\s[A-Z][a-z]{2,}", PRIV.read_text(encoding="utf-8", errors="replace"))) if PRIV.exists() else set()


def mask(s):
    for n in sorted(NAMES, key=len, reverse=True):
        s = s.replace(n, "[NAME]")
    return re.sub(r"\b[A-Z][a-z]{2,}\s[A-Z][a-z]{2,}\b", "[NAME]", str(s))


def get(u, data=None, hdr=None, tries=3, pause=0.0):
    h = dict(UA); h.update(hdr or {})
    for i in range(tries):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, data=data, headers=h), timeout=45)
            return r.status, r.read()
        except urllib.error.HTTPError as e:
            body = b""
            try:
                body = e.read()
            except Exception:
                pass
            if e.code in (422, 429, 503) and i + 1 < tries:
                time.sleep(4 + 4 * i); continue
            return e.code, body
        except Exception as e:
            if i + 1 < tries:
                time.sleep(2 + 2 * i); continue
            return "ERR " + repr(e)[:100], b""
    return "gaveup", b""


def js(b):
    try:
        return json.loads(b)
    except Exception:
        return {"_nonjson": b[:400].decode("utf-8", "replace")}


def civ(u, label):
    st, b = get(u)
    d = js(b)
    items = d.get("items") if isinstance(d, dict) else None
    print("  %-52s -> %s items=%s" % (label, st, len(items) if items is not None else "-"))
    if items is None and isinstance(d, dict):
        msg = str(d)[:600]
        print("      allowed enums in the error:", sorted(set(re.findall(r'"values": \[(.{0,300}?)\]', msg, re.S)))[:3])
    time.sleep(1.2)
    return items or []


print("### A. Civitai: collect H3-related model ids (valid sort values), then detail-check baseModel")
Q = ["minimax h3", "minimax-h3", "minimaxh3", "minimax h3 lora", "h3 lora", "10eros", "ref2va lora", "faceswap",
     "minimax realism", "h3 character", "h3 name-reference"]
cands, seen = [], set()
for q in Q:
    for extra in ["&types=LoRA", ""]:
        cands += civ("https://civitai.com/api/v1/models?name=%s&limit=50&sort=Most%%20Downloaded%s" %
                     (urllib.parse.quote(q), extra), "name=%s%s" % (q, extra))
for u in ["TenStrip", "Ten__Strip", "UntMods"]:
    cands += civ("https://civitai.com/api/v1/models?username=%s&limit=50&sort=Most%%20Downloaded" % urllib.parse.quote(u), "username=%s" % u)
for nm in sorted(NAMES)[:6]:
    cands += civ("https://civitai.com/api/v1/models?trainedWords=%s&limit=50&sort=Most%%20Downloaded&types=LoRA" %
                 urllib.parse.quote(nm), "trainedWords=<private person>")
for x in cands:
    if x.get("id") in seen: continue
    seen.add(x["id"])
print("  unique candidate ids collected:", len(seen))

h3 = []
for n, x in enumerate([c for c in cands if c.get("id") in seen]):
    st, b = get("https://civitai.com/api/v1/models/%s" % x["id"])
    d = js(b)
    if not isinstance(d, dict) or not d.get("modelVersions"): continue
    for v in d["modelVersions"][:2]:
        bm = str(v.get("baseModel") or "")
        if not re.search(r"h3|minimax", bm, re.I): continue
        h3.append({"id": d.get("id"), "name": mask(str(d.get("name") or ""))[:70], "type": d.get("type"),
                   "baseModel": bm, "version": v.get("name"), "published": str(v.get("publishedAt"))[:10],
                   "dl": (v.get("stats") or {}).get("downloadCount"), "favs": (v.get("stats") or {}).get("favCount"),
                   "trigger": (v.get("trainedWords") or [])[:8], "user": (v.get("modelUser") or {}).get("username"),
                   "nsfw": d.get("nsfw"), "tags": [str(t.get("name") if isinstance(t, dict) else t) for t in (d.get("tags") or [])][:8],
                   "files": [(f.get("name"), round((f.get("sizeKB") or 0) / 1024)) for f in v.get("files", [])
                             if str(f.get("name", "")).endswith(".safetensors")][:4]})
    if n % 25 == 24: print("   ... checked %d/%d" % (n + 1, len(seen)))
    time.sleep(0.35)
h3 = [h for n, h in enumerate(h3) if (h["id"], h.get("version")) not in {k for k in h3[:n]}]
print("\n### B. The H3 LoRA catalog from Civitai (baseModel matches H3/MiniMax), by downloads")
seen2 = set()
rows = []
for r in sorted(h3, key=lambda x: -(x["dl"] or 0)):
    if r["id"] in seen2: continue
    seen2.add(r["id"]); rows.append(r)
print("  models:", len(rows), "of", len(seen), "candidates checked")
IDENT = re.compile(r"face|swap|identit|name-reference|person|likeness|portrait|head|ts\b|character", re.I)
for r in rows:
    tagid = "IDENTITY/name-reference" if IDENT.search(r["name"] + " " + " ".join(r["tags"]) + " " + " ".join(t for t in r["trigger"])) else "other"
    print("  %-15s dl=%-6s fav=%-5s id=%-8s %-12s by %-14s published=%s\n      %s\n      trigger=%s tags=%s\n      safetensors(MB)=%s" % (
        tagid, r["dl"], r["favs"], r["id"], r["baseModel"], r["user"], r["published"], r["name"], r["trigger"], r["tags"], r["files"]))
(WEB / "civitai_h3_catalog_v3.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
print("  catalog ->", WEB / "civitai_h3_catalog_v3.json")

print("\n### C. the saved Reddit corpus (pass 2) - LoRA links and what the community says about name-reference identity")
LINK = re.compile(r"https?://[^\s\"'<>\)\]]+", re.I)
for f in sorted(WEB.glob("reddit_*.json")):
    data = json.loads(f.read_text(encoding="utf-8"))
    posts = data.get("data") if isinstance(data, dict) else data
    for p in (posts if isinstance(posts, list) else [posts]):
        if not isinstance(p, dict): continue
        body = (p.get("selftext") or "") + "\n" + "\n".join(c.get("body", "") for c in (p.get("comments") or []) if isinstance(c, dict))
        links = sorted({l.rstrip(".,)") for l in LINK.findall(body) if re.search(r"huggingface|civitai|drive\.google|pixeldrain|mega\.nz", l, re.I)})
        sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", body) if re.search(r"lora|name-reference|known character|identity", s, re.I)]
        print("  %s: %d links, %d identity-related sentences" % (f.name, len(links), len(sents)))
        for l in links[:10]: print("      ", l[:150])
        for s in sents[:8]: print("      Q:", mask(s)[:260])

print("\n### D. awesome-minimax-h3 - the LoRAs/training section (names masked)")
t = (WEB / "awesome-minimax-h3_README.md").read_text(encoding="utf-8", errors="replace")
lines = t.splitlines()
start = next((i for i, l in enumerate(lines) if re.match(r"^#+\s*.*LoRAs and training", l, re.I)), None)
if start is None:
    print("  section heading not found; printing LoRA lines")
    [print("   L%-4d %s" % (i, mask(l.strip())[:200])) for i, l in enumerate(lines) if re.search(r"lora", l, re.I)][:40]
else:
    end = next((i for i in range(start + 1, len(lines)) if re.match(r"^##\s", lines[i])), len(lines))
    print("  section lines %d-%d" % (start, end))
    for i in range(start, min(end, start + 120)):
        print("   L%-4d %s" % (i, mask(lines[i].strip())[:240]))
