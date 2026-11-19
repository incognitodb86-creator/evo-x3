#!/usr/bin/env python3
"""Dump graph nodes by id from a request.api.json (keys + input wiring).

The builder patches nodes by key, so the exact input key names of the base graph must be read
before writing a new builder. Used for the VSA / shift / sampler / scheduler keys of the A/B/C arms.
Usage: dump_nodes.py <request.api.json> [id id ...]
"""
import json
import sys

path = sys.argv[1]
g = json.load(open(path, encoding="utf-8"))
ids = sys.argv[2:] or sorted(g, key=lambda x: int(x) if x.isdigit() else 0)
for nid in ids:
    n = g.get(nid)
    if not n:
        print(f"{nid}: absent")
        continue
    print(f"{nid} {n['class_type']}")
    for k, v in n["inputs"].items():
        print(f"    {k} = {json.dumps(v, ensure_ascii=False)[:120]}")
    print()
