"""R4G probe 10: solo-woman prompt shapes proven on this box (printed with delimiters, read-only).
  1. runs/ali147_pool_refsheet_b_s51080000 c0+c1 prompts (single woman POOL + sheet, v2)
  2. notes/p6_r1_prompt.txt (single woman, earlier community line)
"""
import json
import os

W = r"C:/AI/community"

def dump_graph(path, label):
    g = json.loads(open(path, encoding="utf-8").read().replace("\r\n", "\n"))
    print("#" * 100)
    print(label, "nodes", len(g))
    for nid in sorted(g):
        i = g[nid]["inputs"]
        if "prompt" in i:
            refs = {k: v for k, v in i.items() if str(k).startswith("ref_")}
            print(f"-- {nid} {g[nid]['class_type']} w={i.get('width')} h={i.get('height')} L={i.get('length')} refs={refs}")
            print("PROMPT-START\n" + i["prompt"] + "\nPROMPT-END")

p = os.path.join(W, "runs", "ali147_pool_refsheet_b_s51080000", "request.api.json")
dump_graph(p, "POOL refsheet_b (RS6)")
f = os.path.join(W, "notes", "p6_r1_prompt.txt")
if os.path.isfile(f):
    t = open(f, encoding="utf-8").read()
    print("#" * 100)
    print("p6_r1_prompt.txt", len(t), "chars")
    print("PROMPT-START\n" + t + "\nPROMPT-END")
