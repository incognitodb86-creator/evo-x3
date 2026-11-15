#!/usr/bin/env python3
"""Translate AlienPc (Windows) paths in Render's code/skills/docs to the EVO-X3 layout.

Max Architect, 2026-11-15 (Derrick t1739u-t1741u: "copy it over", "transferred over to the setup on x3").
Mapping (only paths change; logic is untouched):
  & 'C:\\Program Files\\Python312\\python.exe'      -> python3
  C:\\Users\\derek\\HardcoreNSFW-TestRuntime\\ComfyUI -> ~/AI/comfy-alienpc   (refmods: OC files real, rest name stubs)
  C:\\Users\\derek\\5slock                           -> ~/AI/5slock          (empty: PixlStash libraries are never copied)
  C:\\AI\\...                                        -> ~/AI/...
  ~\\.pi\\agent\\...                                 -> ~/.pi/agent/...
Usage: linuxize.py FILE... (in place; writes FILE.bak-x3linux once before the first change). Idempotent.
"""
import re, sys
from pathlib import Path

HOME = "/home/derekboone"
SEP = r"(?:\\\\|\\|/)"
SEG = r"[^\s\"'`|?\\/:;,()\[\]{}]+"
def path_re(prefix):
    return re.compile(prefix + r"((?:" + SEP + SEG + r")*" + SEP + r"?)")

RULES = [
    (re.compile(r"&\s*'C:" + SEP + r"Program Files" + SEP + r"Python312" + SEP + r"python\.exe'"), lambda m: "python3"),
    (re.compile(r"C:" + SEP + r"Program Files" + SEP + r"Python312" + SEP + r"python\.exe"), lambda m: "python3"),
    (path_re(r"C:" + SEP + r"Users" + SEP + r"derek" + SEP + r"HardcoreNSFW-TestRuntime" + SEP + r"ComfyUI"),
     lambda m: HOME + "/AI/comfy-alienpc" + re.sub(SEP, "/", m.group(1))),
    (path_re(r"C:" + SEP + r"Users" + SEP + r"derek" + SEP + r"5slock"),
     lambda m: HOME + "/AI/5slock" + re.sub(SEP, "/", m.group(1))),
    (path_re(r"[Cc]:" + SEP + r"AI(?=" + SEP + r"|\b)"),
     lambda m: HOME + "/AI" + re.sub(SEP, "/", m.group(1))),
    (path_re(r"~" + r"(?:\\\\|\\)" + r"\.pi"), lambda m: "~/.pi" + re.sub(SEP, "/", m.group(1))),
]

def convert(text):
    for rx, fn in RULES:
        text = rx.sub(fn, text)
    return text

if __name__ == "__main__":
    changed = 0
    for f in sys.argv[1:]:
        p = Path(f)
        raw = p.read_bytes()
        try:
            t = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        n = convert(t)
        if n != t:
            bak = p.with_name(p.name + ".bak-x3linux")
            if not bak.exists():
                bak.write_bytes(raw)
            p.write_bytes(n.encode("utf-8"))
            changed += 1
            print("linuxized", f)
    print(f"{changed} file(s) changed")
