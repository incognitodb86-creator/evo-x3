# Citation correction for the F2b record (2026-11-05 18:5x CT, Forge). Appends only.
REC = r"""
### Citation correction (18:5x CT)

The v2 plan of record cited in this file and in the card addendum is
**`C:\Users\derek\5slock\ralph-community\notes\2026-11-05-forge-cleanup-v2.md`** - not a file under
`C:\AI\community\notes\`, where it does not exist. Verified: `grep -n 'b2_fc_sydney_lora' ` in that file returns
line 22 ("**Every FC_SYDNEY and b2_fc_sydney_lora* file stays.**") and line 28 ("F2b must not move
b2_fc_sydney_lora*"), so the quotations and line numbers used above are correct; only the directory in my shorthand
was ambiguous, and it is made absolute here. Records-only edit; nothing else in this pass changes.
"""
ACT = ("2026-11-05 18:5x CT | forge | pi-chat | FIX | F2b record citation made absolute: the v2 plan of record is "
       "C:\\Users\\derek\\5slock\\ralph-community\\notes\\2026-11-05-forge-cleanup-v2.md (lines 22 and 28 re-verified verbatim by grep -n), "
       "NOT under C:\\AI\\community\\notes (no such file there). Quotes and line numbers were right, the directory shorthand was not. "
       "Records-only edit; no GPU, no render, no process touched, nothing deleted, no .bak, no git add -A, no GitHub; Sydney untouched.\n")

for p, t in [(r"C:\AI\community\notes\2026-11-05-cleanup-F2b-BLOCKED.md", REC),
             (r"C:\AI\community\notes\actions.log", ACT)]:
    d = open(p, "rb").read()
    nl = "" if d.endswith(b"\n") else "\n"
    with open(p, "a", encoding="utf-8", newline="\n") as f:
        f.write(nl + t)
    print("appended", p, len(t))
