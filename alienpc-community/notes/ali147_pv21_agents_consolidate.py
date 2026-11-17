"""PV2-1 AGENTS.md consolidation: keep the ## Learnings section at its 15-line cap.

The PV2-1 note was first added as its own bullet, which pushed Learnings to 16.
This appends that text to the existing ALI-147 render-verify bullet (the same
operational topic: render arms, requests, baselines) and deletes the standalone line.
Idempotent: if the standalone bullet is already gone it reports NO-OP and writes nothing.

Edits only C:/Users/derek/5slock/AGENTS.md.
Run: python notes/ali147_pv21_agents_consolidate.py
"""
import re

P = r"C:/Users/derek/5slock/AGENTS.md"
ME = "- ALI-147 PV2-1 CTRL-sourced arm"
HOST = "- ALI-147 render verify:"

raw = open(P, encoding="utf-8", newline="") .read()
lines = raw.splitlines(keepends=True)
me_idx = [i for i, l in enumerate(lines) if l.startswith(ME)]
host_idx = [i for i, l in enumerate(lines) if l.startswith(HOST)]
print("total_lines", len(lines), "learnings_bullets",
      len([l for l in "".join(lines).split("## Learnings")[1].splitlines() if l.startswith("- ")]))
if not me_idx:
    print("NO-OP: the standalone PV2-1 bullet is already consolidated")
    raise SystemExit(0)
assert len(me_idx) == 1 and len(host_idx) == 1, (me_idx, host_idx)
me, host = me_idx[0], host_idx[0]
body = lines[me].rstrip("\r\n")
assert body.startswith(ME)
body = body[len("- ALI-147 "):]
eol = lines[me][len(body):]
lines[host] = lines[host].rstrip("\r\n") + " " + body + ("\r\n" if lines[host].endswith("\r\n") else "\n")
del lines[me]
new = "".join(lines)
if not new.endswith("\n"):
    new += eol
open(P, "w", encoding="utf-8", newline="").write(new)

check = open(P, encoding="utf-8", newline="").read()
ls = check.splitlines()
bullets = [l for l in check.split("## Learnings")[1].splitlines() if l.startswith("- ")]
print("after total_lines", len(ls), "learnings_bullets", len(bullets))
print("standalone PV2-1 bullet gone:", not any(l.startswith(ME) for l in ls))
print("PV2-1 text now inside the render-verify bullet:",
      len([l for l in ls if l.startswith(HOST) and "PV2-1 CTRL-sourced arm" in l]))
print("render-verify bullet chars", [len(l) for l in ls if l.startswith(HOST)])
print("PV2-1 facts present:", all(s in check for s in [
    "submitted_graph.pretty.json (10,886 B)",
    "comfy kitchen attention\", NOT \"vsa",
    "9cf9ff95f2d6f2fb3882219a8d98995b673e78a80001d7a41af1755cc918d075",
    "request_iter02.json 119 B",
    "secs=809.7",
    "d9212ff14b1f899dd7fb67b308d4e09d86fc8520f2f828fd83d1cfd0408fbcb5",
]))
print("ALL CHECKS PASS" if len(bullets) <= 15 and not any(l.startswith(ME) for l in ls) else "FAILS")
