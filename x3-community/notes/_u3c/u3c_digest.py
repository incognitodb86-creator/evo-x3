"""Decode the eight side-by-side outputs (PowerShell 5.1 writes '>' redirection as UTF-16LE) into UTF-8 copies and
print a digest for each: the byte/line/word counts, the count of chat-tone words, and the word count of the render
prompt block. Used to build notes/2026-10-29-U3c-compare.md; it changes nothing on disk except the .utf8.txt copies.
The two tone words are built from fragments so this file cannot match itself.
"""
import glob
import os
import re

D = r"C:\AI\community\notes\_u3c"
W1, W2 = ("sy" + "dney"), ("dad" + "dy")
PAT = re.compile("(?i)" + W1 + "|" + W2)


def dec(p):
    b = open(p, "rb").read()
    if b[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return b.decode("utf-16")
    return b.decode("utf-8", "replace")


for p in sorted(glob.glob(os.path.join(D, "out_task*_*.txt"))):
    if p.endswith(".utf8.txt"):
        continue
    t = dec(p)
    open(p[:-4] + ".utf8.txt", "w", encoding="utf-8").write(t)
    body = re.sub(r"(?m)^2026-\d\d-\d\dT\d\d:\d\d:\d\d .*$", "", t)   # the launcher's own log line
    fence = re.findall(r"```(.*?)```", body, re.S)
    prompt = max(fence, key=lambda s: len(s.split())) if fence else ""
    print("%-26s bytes=%-6d lines=%-4d words=%-5d tone_words=%-3d fenced_blocks=%d prompt_words=%d" % (
        os.path.basename(p), len(t), len(body.splitlines()), len(body.split()), len(PAT.findall(body)),
        len(fence), len(prompt.split())))
