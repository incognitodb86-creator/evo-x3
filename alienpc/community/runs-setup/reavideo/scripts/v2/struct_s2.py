import json, re
from pathlib import Path
man = json.loads(Path(r"C:\Users\derek\forge\reavideo\out\hotel_vlm2_val30s_v2\bridge\h3max_manifest.json").read_text(encoding="utf-8"))

def classify(text, pat):
    hits = []
    for m in re.finditer(pat, text):
        start = m.start()
        pre = text[max(0, start-40):start]
        sent_start = (start == 0 or pre.strip() == "" or bool(re.search(r"[\.\n!?]\s*$", pre)))
        after_section = bool(re.search(r"\]\s*$", pre.rstrip()))
        hits.append({"tag": m.group(1), "sent_start": sent_start, "after_section": after_section, "offset": start})
    return hits

for clip in man["clips"]:
    text = clip["prompt"]
    tags = re.findall(r"<[^>]{1,40}>", text)
    print({
        "clip_index": clip.get("clip_index"),
        "prompt_len": len(text),
        "s1": classify(text, r"(?i)(\(S1\)|<Subject 1>)"),
        "s2": classify(text, r"(?i)(\(S2\)|<Subject 2>)"),
        "tags": tags,
        "conv_keys": sorted((clip.get("conversion") or {}).keys()),
        "val_status": (clip.get("validation") or {}).get("status"),
        "offline": clip.get("offline_fallback"),
    })
