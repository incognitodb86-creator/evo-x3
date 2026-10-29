r"""h3_lora_social_sweep2.py - 2nd pass, outside Hugging Face: Civitai, Reddit (Arctic Shift), GitHub index.

Why: the 1st pass used the HF API only and the web-search engines. Web search then found H3 LoRAs **on Civitai**
(a face-swap LoRA, a face/speech LoRA, style LoRAs) and Reddit threads about H3 and name-reference faces - so the
1st pass under-counted. This pass reads those sources properly:
  A. Civitai REST v1: model detail for the found ids (baseModel / trainedWords / file sizes = the proof fields),
     plus name/username/trainedWords filters (names read from the private map, never printed).
  B. Reddit via Arctic Shift: the threads about H3 + name-reference identity, by id, plus their comments; raw text is
     saved to a NON-git folder (C:\AI\lora\person_alias_2026-10-29\web_2026-10-29) because the posts name real
     people, and printed here with name-looking tokens masked.
  C. The community index AtlasCloudAI/awesome-minimax-h3 (GitHub raw README), LoRA/name-reference lines, names masked.
Read-only: no downloads, no GPU, nothing written inside git.
Usage: python h3_lora_social_sweep2.py
"""
import json, re, urllib.request, urllib.parse
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129 Safari/537.36"}
PRIV = Path(r"C:\AI\lora\person_alias_2026-10-29\TRIGGER_MAP_private.txt")
WEB = Path(r"C:\AI\lora\person_alias_2026-10-29\web_2026-10-29")
WEB.mkdir(parents=True, exist_ok=True)
CIVITAI_IDS = [2940916, 2925394, 2849726]
REDDIT_IDS = ["1vufdh5", "1vkdfqe", "1vkz1d8", "1vzfwl9"]
NAMES = set()
if PRIV.exists():
    NAMES = {t for t in re.findall(r"[A-Z][a-z]{2,}\s[A-Z][a-z]{2,}", PRIV.read_text(encoding="utf-8", errors="replace"))}
NAMES |= {t for t in re.findall(r"\b[A-Z][a-z]{2,}\s[A-Z][a-z]{2,}\b", "")}   # extra names live only in the private file


def mask(s):
    for n in sorted(NAMES, key=len, reverse=True):
        s = s.replace(n, "[NAME]")
    return re.sub(r"\b[A-Z][a-z]{2,}\s[A-Z][a-z]{2,}\b", "[NAME]", s)


def get(u, data=None, hdr=None):
    h = dict(UA); h.update(hdr or {})
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, data=data, headers=h), timeout=45)
        return r.status, r.read()
    except urllib.error.HTTPError as e:
        try:
            return e.code, e.read()[:400]
        except Exception:
            return "HTTP%s" % e.code, b""
    except Exception as e:
        return "ERR " + repr(e)[:110], b""


def js(b):
    try:
        return json.loads(b)
    except Exception:
        return {"_nonjson": b[:300].decode("utf-8", "replace")}


print("### A. Civitai REST v1 - model detail (baseModel / trainedWords / size = the proof fields)")
for mid in CIVITAI_IDS:
    st, b = get("https://civitai.com/api/v1/models/%s" % mid)
    d = js(b)
    if not isinstance(d, dict) or "modelVersions" not in d:
        print("  id=%s -> %s %s" % (mid, st, str(b)[:150])); continue
    (WEB / ("civitai_%s.json" % mid)).write_text(json.dumps(d, indent=1), encoding="utf-8")
    v = d["modelVersions"][0]
    print("  id=%s %s\n      type=%s baseModel=%s triggerWords=%s\n      downloads=%s favs=%s nsfw=%s files=%s" % (
        mid, (d.get("name") or "")[:70], d.get("type"), v.get("baseModel"), (v.get("trainedWords") or [])[:6],
        (v.get("stats") or {}).get("downloadCount"), (v.get("stats") or {}).get("favCount"), d.get("nsfw"),
        [(f.get("name"), f.get("sizeKB")) for f in v.get("files", [])][:5]))
    print("      creator=%s tags=%s" % ((v.get("modelUser") or {}).get("username"),
          [mask(str(t.get("name") if isinstance(t, dict) else t)) for t in (d.get("tags") or [])][:8]))
    st2, b2 = get("https://civitai.com/api/v1/models/%s/versions/%s" % (mid, v.get("id")))
    (WEB / ("civitai_%s_version.json" % mid)).write_text(b2.decode("utf-8", "replace"), encoding="utf-8")

print("\n### A2. Civitai filters: name=, username=, trainedWords= (names from the private map, not printed)")
FILT = [("name=minimax+h3", "https://civitai.com/api/v1/models?name=minimax%20h3&limit=30&sort=MostDownloads"),
        ("name=lora+minimax", "https://civitai.com/api/v1/models?name=lora%20minimax&limit=30&sort=MostDownloads"),
        ("username=TenStrip", "https://civitai.com/api/v1/models?username=TenStrip&limit=50&sort=MostDownloads"),
        ("top video LoRAs (year)", "https://civitai.com/api/v1/models?types=LoRA&minMode=Image2Video&period=Year&sort=MostDownloads&limit=40"),
        ("top LoRAs (year, any mode)", "https://civitai.com/api/v1/models?types=LoRA&period=Year&sort=MostDownloads&limit=40")]
for q in sorted(NAMES)[:4]:
    FILT.append(("trainedWords=<private person>", "https://civitai.com/api/v1/models?trainedWords=%s&types=LoRA&limit=30&sort=MostDownloads" % urllib.parse.quote(q)))
for label, u in FILT:
    st, b = get(u)
    d = js(b)
    items = d.get("items") if isinstance(d, dict) else None
    print("  %-32s -> %s items=%s" % (label, st, len(items) if items is not None else "-"))
    for x in (items or [])[:12]:
        print("      id=%-8s %-10s %s" % (x.get("id"), x.get("type"), mask((x.get("name") or "")[:60])))
    if not items and isinstance(d, dict): print("      ", str(b)[:200])

print("\n### A3. Build the H3 LoRA catalog from Civitai (name= / username= searches, then detail-check baseModel)")
SEED = ["https://civitai.com/api/v1/models?name=%s&limit=40&sort=MostDownloads" % urllib.parse.quote(q) for q in
        ["minimax h3", "minimax-h3", "minimaxh3", "minimax h3 lora", "h3 lora", "10eros", "minimax ref2va", "faceswap h3"]]
SEED += ["https://civitai.com/api/v1/models?username=%s&limit=50&sort=MostDownloads" % urllib.parse.quote(u) for u in
         ["TenStrip", "Ten__Strip", "UntMods"]]
seen, h3 = set(), []
for u in SEED:
    st, b = get(u)
    d = js(b)
    items = d.get("items") if isinstance(d, dict) else []
    print("  %-58s -> %s items=%s" % (u.split("v1/models?")[1][:56], st, len(items) if items is not None else "-"))
    for x in (items or []):
        if x.get("id") in seen: continue
        seen.add(x["id"])
        st2, b2 = get("https://civitai.com/api/v1/models/%s" % x["id"])
        d2 = js(b2)
        if not isinstance(d2, dict) or "modelVersions" not in d2: continue
        v = d2["modelVersions"][0]
        bm = str(v.get("baseModel") or "")
        if not re.search(r"h3|minimax", bm, re.I): continue
        h3.append({"id": x["id"], "name": mask(str(d2.get("name") or ""))[:70], "type": d2.get("type"),
                   "baseModel": bm, "dl": (v.get("stats") or {}).get("downloadCount"),
                   "favs": (v.get("stats") or {}).get("favCount"), "trigger": (v.get("trainedWords") or [])[:6],
                   "user": (v.get("modelUser") or {}).get("username"),
                   "files": [(f.get("name"), round((f.get("sizeKB") or 0) / 1024)) for f in v.get("files", []) if str(f.get("name", "")).endswith(".safetensors")][:4]})
print("\n  H3/MiniMax-based Civitai models found: %d (of %d candidates checked)" % (len(h3), len(seen)))
for r in sorted(h3, key=lambda x: -(x["dl"] or 0)):
    print("   dl=%-6s fav=%-5s id=%-8s %-7s %-16s by %-12s trigger=%s\n      name=%s\n      files(MB)=%s" % (
        r["dl"], r["favs"], r["id"], r["type"], r["baseModel"], r["user"], r["trigger"], r["name"], r["files"]))
(WEB / "civitai_h3_catalog.json").write_text(json.dumps(h3, indent=1), encoding="utf-8")
print("  catalog ->", WEB / "civitai_h3_catalog.json")

print("\n### B. Reddit via Arctic Shift - the H3/name-reference threads and their comments")
st, b = get("https://arctic-shift.photon-reddit.com/api/posts/ids?" + urllib.parse.urlencode({"ids": ",".join(REDDIT_IDS)}))
d = js(b)
posts = d.get("data") if isinstance(d, dict) else []
for p in (posts or []):
    (WEB / ("reddit_%s.json" % p.get("id"))).write_text(json.dumps(p, indent=1), encoding="utf-8")
    print("  r/%s %s score=%s nc=%s | %s" % (p.get("subreddit"), str(p.get("created_utc"))[:10], p.get("score"),
          p.get("num_comments"), mask((p.get("title") or "")[:120])))
    body = p.get("selftext") or ""
    print("      body %d chars, links: %s" % (len(body), " ".join(sorted(set(re.findall(r"https?://\S+", body))))[:6])[:300])
    st2, b2 = get("https://arctic-shift.photon-reddit.com/api/comments/search?" + urllib.parse.urlencode(
        {"link_id": "t3_%s" % p.get("id"), "limit": 60, "after": "2026-08-01T00:00:00Z"}))
    d2 = js(b2)
    cs = d2.get("data") if isinstance(d2, dict) else []
    (WEB / ("reddit_%s_comments.json" % p.get("id"))).write_text(json.dumps(cs, indent=1), encoding="utf-8")
    print("      comments fetched=%s (saved, names masked only in console)" % (len(cs) if cs is not None else "-"))

print("\n### B2. Arctic Shift search (fixed params: one subreddit, no fields)")
for sub in ["StableDiffusion", "ComfyUI", "LocalLLaMA"]:
    for q in ['"minimax h3" lora', '"10eros" lora', '"minimax h3" character', '"minimax h3" name-reference', '"h3" faceswap lora']:
        st, b = get("https://arctic-shift.photon-reddit.com/api/posts/search?" + urllib.parse.urlencode(
            {"query": q, "subreddit": sub, "after": "2026-07-01T00:00:00Z", "limit": 60}))
        d = js(b)
        rows = d.get("data") if isinstance(d, dict) else []
        print("  r/%-16s %-26s -> %s rows=%s" % (sub, q, st, len(rows) if rows is not None else "-"))
        for r in (rows or [])[:8]:
            print("      %s score=%-4s id=%s %s" % (str(r.get("created_utc"))[:10], r.get("score"), r.get("id"),
                  mask((r.get("title") or "")[:110])))

print("\n### C. community index AtlasCloudAI/awesome-minimax-h3 (LoRA/name-reference lines, names masked)")
st, b = get("https://raw.githubusercontent.com/AtlasCloudAI/awesome-minimax-h3/main/README.md")
t = b.decode("utf-8", "replace") if isinstance(b, bytes) else ""
(WEB / "awesome-minimax-h3_README.md").write_text(t, encoding="utf-8")
print("  README status=%s chars=%d (saved to the non-git web folder)" % (st, len(t)))
for i, l in enumerate(t.splitlines()):
    if re.search(r"lora|name-reference|identity|face|character", l, re.I):
        print("   L%-4d %s" % (i, mask(l.strip())[:260]))
