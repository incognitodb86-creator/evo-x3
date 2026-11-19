import json, urllib.request, urllib.parse
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/129"}


def g(u, data=None, hdr=None):
    h = dict(UA); h.update(hdr or {})
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, data=data, headers=h), timeout=45)
        return r.status, r.read()[:900].decode("utf-8", "replace")
    except Exception as e:
        return "ERR", repr(e)[:250]


B = "https://arctic-shift.photon-reddit.com/api"
for kind in ["posts", "comments"]:
    for params in [{"query": "minimax h3", "limit": 5},
                   {"query": '"minimax h3"', "limit": 5, "after": "2026-07-01T00:00:00Z"},
                   {"query": '"10eros lora"', "limit": 5, "subreddit": "StableDiffusion"}]:
        st, body = g("%s/%s/search?" % (B, kind) + urllib.parse.urlencode(params))
        print("A %-8s %-70s -> %s\n   %s" % (kind, urllib.urlencode(params) if hasattr(urllib, "urlencode") else list(params), st, body[:400]))

GQL = "https://civitai.com/api/graphql"
for label, qq in [("plain", '{models(query:{search:"minimax h3",limit:5}){items{id name type}}}'),
                  ("lora-type", '{models(query:{search:"minimax h3",limit:5,types:[LoRA]}){items{id name}}}'),
                  ("celeb-lora", '{models(query:{search:"celebrity",limit:5,types:[LoRA],sort:MostDownloads}){items{id name}}}'),
                  ("introspect-fields", '{models(query:{search:"minimax",limit:1}){items{id name type nsfw stats{downloadCount} modelVersions{baseModel trainedWords files{name sizeKB type}}}}}')]:
    st, body = g(GQL, data=json.dumps({"query": qq}).encode(), hdr={"Content-Type": "application/json"})
    print("\nB %-16s -> %s\n   %s" % (label, st, body[:800]))
