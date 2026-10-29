r"""h3_lora_social_sweep.py - 2nd pass for H3/10Eros character-reference LoRAs outside Hugging Face.

Sources hit from this box (read-only, no downloads):
  A. Arctic Shift (public Reddit JSON API) - posts and comments, filtered to H3/10Eros + LoRA context, with any
     huggingface.co / civitai.com / drive.google.com link extracted from the text (that is how people share LoRAs).
  B. Civitai API v1 with a browser UA, several parameter shapes, statuses recorded. If a model is returned, its
     version is expanded for baseModel / trainedWords / file size - the fields that prove whether a name-reference LoRA
     targets H3. Real-person queries are read from the private map file so no real name is written in git.
Usage: python h3_lora_social_sweep.py
"""
import csv, json, re, urllib.request, urllib.parse
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129 Safari/537.36"}
PRIV = Path(r"C:\AI\lora\person_alias_2026-10-29\TRIGGER_MAP_private.txt")
H3PAT = re.compile(r"(minimax[ -]?h3|10eros|h3[ -]?max)", re.I)
LORAPAT = re.compile(r"\blora\b|\bloras\b", re.I)
name-referencePAT = re.compile(r"name-reference|name-reference|identity|face[- ]?swap|character[- ]?swap|likeness|actress|actress|person lora|ts\b", re.I)
LINK = re.compile(r"https?://(?:[^\s\"'<>\)\]]*?)(?:huggingface\.co|civitai\.com|drive\.google\.com|mega\.nz|pixeldrain\.com|kaggle\.com|github\.com)[^\s\"'<>\)\]]*", re.I)
SUBS = "StableDiffusion,LocalLLaMA,ComfyUI,SillyTavern,mlsubreddit,SDNSFW"


def get(u, tries=1):
    for i in range(tries):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=45)
            b = r.read()
            return r.status, b
        except Exception as e:
            last = "%s" % repr(e)[:120]
    return "ERR " + last, b""


def as_json(status, b):
    try:
        return json.loads(b)
    except Exception:
        return {"_nonjson": (b[:200].decode("utf-8", "replace") if b else "")}


print("### A. Reddit via Arctic Shift (posts + comments, H3/10EROS + lora context)")
for kind in ["posts", "comments"]:
    for q in ["minimax h3 lora", "10eros lora", "minimax h3 name-reference", "minimax h3 character swap",
              "10eros max lora", "minimax h3 face lora"]:
        u = "https://arctic-shift.photon-reddit.com/api/%s/search?" % kind + urllib.parse.urlencode(
            {"query": q, "subreddit": SUBS, "after": "2026-07-01", "limit": 100,
             "fields": "id,subreddit,title,author,url,score,created_utc,body,selftext"})
        st, b = get(u)
        d = as_json(st, b)
        rows = (d.get("data") if isinstance(d, dict) else None) or (d if isinstance(d, list) else [])
        print("\n-- %s q=%r -> %s rows=%d" % (kind, q, st, len(rows)))
        seen = set()
        for r in rows:
            body = (r.get("body") or r.get("selftext") or "")
            title = r.get("title") or ""
            if not (H3PAT.search(body + title) and LORAPAT.search(body + title)):
                continue
            key = r.get("id")
            if key in seen: continue
            seen.add(key)
            links = sorted({l.strip(".,)") for l in LINK.findall(body + " " + (r.get("url") or ""))})
            flag = "name-reference" if name-referencePAT.search(body + title) else ""
            print("   [%s] r/%s %s score=%s %s | %s" % (flag or "lora ", r.get("subreddit"), str(r.get("created_utc"))[:10],
                  r.get("score"), (title[:110] if kind == "posts" else (body[:110].replace("\n", " ") + " ...")),
                  " ".join(links[:3])[:220] or "-"))
        if isinstance(d, dict) and d.get("_nonjson"): print("   ", d["_nonjson"][:120])

print("\n\n### B. Civitai API v1 with browser UA (statuses recorded; names from the private file, never printed)")
QUERIES = [("minimax h3", None), ("10eros", None), ("minimax-h3", None), ("minimax h3 lora", None)]
if PRIV.exists():
    txt = PRIV.read_text(encoding="utf-8", errors="replace")
    for tok in sorted({t for t in re.findall(r"[A-Z][a-z]{3,}\s[A-Z][a-z]{3,}", txt)})[:6]:
        QUERIES.append((tok, "private-map person"))
SHAPES = ["https://civitai.com/api/v1/models?query=%s&limit=30&sort=MostDownloads",
          "https://civitai.com/api/v1/models?query=%s&limit=30&types=Model&sort=HighestRated",
          "https://civitai.com/api/v1/models?search=%s&limit=30"]
for q, src in QUERIES:
    for sh in SHAPES:
        u = sh % urllib.parse.quote(q)
        st, b = get(u)
        d = as_json(st, b)
        items = (d.get("items") if isinstance(d, dict) else None) or []
        hits = [x for x in items if H3PAT.search(json.dumps(x)[:2000])]
        print("  q=%-22r %-60s -> %s items=%d h3-hits=%d" % (q[:22], sh.split("?")[1][:58], st, len(items), len(hits)))
        for x in items[:6]:
            name = (x.get("name") or "")[:60]
            print("      id=%-9s type=%-6s %s" % (x.get("id"), x.get("type"), name))
        if isinstance(d, dict) and d.get("_nonjson"): print("      ", d["_nonjson"][:140])
    if src: print("      (query source: %s)" % src)

print("\n### Civitai version detail for any model ids that look H3-related (baseModel/trainedWords/size)")
ids = []
for q, _ in QUERIES[:3]:
    st, b = get("https://civitai.com/api/v1/models?query=%s&limit=30&sort=MostDownloads" % urllib.parse.quote(q))
    d = as_json(st, b)
    for x in (d.get("items") or []):
        ids.append(x.get("id"))
for mid in sorted(set([i for i in ids if i]))[:8]:
    st, b = get("https://civitai.com/api/v1/models/%s" % mid)
    d = as_json(st, b)
    if not isinstance(d, dict) or "modelVersions" not in d:
        print("  id=%s -> %s (no version detail)" % (mid, st)); continue
    v = d["modelVersions"][0]
    files = [(f.get("name"), f.get("sizeKB"), f.get("type")) for f in v.get("files", [])][:4]
    print("  id=%s name=%s type=%s nsfw=%s dl=%s\n      baseModel=%s trainedWords=%s\n      files=%s\n      nsfwSfw=%s urls=%s" % (
        mid, (d.get("name") or "")[:70], d.get("type"), d.get("nsfwLevel"), (v.get("stats") or {}).get("downloadCount"),
        v.get("baseModel"), (v.get("trainedWords") or [])[:8], files, d.get("nsfw"), [x.get("url") for x in v.get("images", [])][:1]))
