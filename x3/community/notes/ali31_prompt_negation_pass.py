#!/usr/bin/env python
"""ali31_prompt_negation_pass.py - fix_plan 3.1 (PQ1): rewrite the negation prose in the IM1 prompt set.

notes/prompt_guide_20261024.md rule 4 ("Move negation out of prose"): the official MiniMax guides never use
prohibition wording, and the only community route for negation is a NegPip token-weight node
(https://github.com/gas/comfyui-minimax-h3-negpip, HF discussion #52). Measured on 2026-10-24 over the 12
verbatim prompts in notes/im1_prompts.md: 28 prohibition tokens (15 "no", 8 "not", 5 "without") in
6 recurring patterns, so the set did not follow its own guide.

Every replacement is positive phrasing of the same visible content, and the counts are asserted BEFORE any
write, so a partial match aborts the file unchanged. The canvas claim in the header is fixed in the same
pass: it says 1024x576 while the only graphs on disk (p7/graphs/ali147_pool_hc_r3b...baseline and ...r3i)
are 1344x768.

Reproduce:
  C:/AI/director/.venv/Scripts/python.exe C:/AI/community/notes/ali31_prompt_negation_pass.py --check
  C:/AI/director/.venv/Scripts/python.exe C:/AI/community/notes/ali31_prompt_negation_pass.py --apply
"""
import re, os, json, sys

C = "C:/AI/community"
DOC = os.path.join(C, "notes", "im1_prompts.md")
NEG = re.compile(r"\b(no|not|never|without|neither|nor|no:)\b", re.I)

# (pattern, replacement, required count). Counts are the measured census over the 12 prompt blocks.
RULES = [
    ("small amplitude, slow speed, no cuts.", "small amplitude, slow speed, one continuous take.", 6),
    ("with small amplitude, no cuts:", "with small amplitude, in one continuous take:", 6),
    ("at slow speed, no cuts, into", "at slow speed, in one continuous take, into", 2),
    ("at slow speed, no cuts, keeping", "at slow speed, in one continuous take, keeping", 1),
    ("press and slide without merging.", "press and slide as two separate bodies.", 4),
    ("helping each other without breaking the kiss", "helping each other, the kiss continuing", 1),
    ("are actions in this story, not changes of body, skin, figure or identity.",
     "are actions in this story; her body, skin, figure and identity stay exactly as in <Picture 1> and <Video 1>.", 6),
    ("are actions in this story, not changes of identity, body, skin or figure.",
     "are actions in this story; her identity, body, skin and figure stay as in <Picture 1>.", 2),
    ("the SAME 1024x576 16:9 canvas", "the SAME 1344x768 16:9 canvas", 1),
]

def parse(text):
    return re.findall(r"### id=(\S+) chunk=(c\d) seed=(\d+)\n(.*?)(?=\n### id=|\Z)", text, re.S)

def census(text):
    """blocks, negation tokens, and the count of each RULE pattern present (prose + header)."""
    b = parse(text)
    toks = sum(len(NEG.findall(body)) for _, _, _, body in b)
    return {"blocks": len(b), "neg_tokens": toks,
            "patterns": {p: text.count(p) for p, _, _ in RULES},
            "canvas_claim": (re.findall(r"the SAME (\d{3,4}x\d{3,4}) 16:9 canvas", text) or [None])[0]}

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--check"
    text = open(DOC, encoding="utf-8").read()
    before = census(text)
    if mode == "--check":
        print("census", json.dumps(before))
        print("VERDICT CLEAN blocks=12 neg_tokens=0 patterns_all_zero canvas=1344x768"
              if before["blocks"] == 12 and before["neg_tokens"] == 0
              and all(v == 0 for v in before["patterns"].values())
              and before["canvas_claim"] == "1344x768"
              else "NOT CLEAN " + json.dumps({k: v for k, v in before.items() if k != "patterns"}))
        return 0
    out = text
    for pat, rep, want in RULES:
        n = out.count(pat)
        if n != want:
            print(f"ABORT pattern_count_mismatch want={want} found={n} pattern={pat!r} (file unchanged)")
            return 2
        out = out.replace(pat, rep)
    after = census(out)
    if after["blocks"] != 12 or after["neg_tokens"] != 0:
        print("ABORT residual " + json.dumps({k: v for k, v in after.items() if k != "patterns"}))
        return 2
    if mode == "--apply":
        open(DOC, "w", encoding="utf-8").write(out)
    print(f"APPLIED rules={len(RULES)} sites={sum(w for _,_,w in RULES)} before={before['neg_tokens']} after={after['neg_tokens']}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
