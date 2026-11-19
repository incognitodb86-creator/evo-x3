# F2b records appender (2026-11-05, Forge pi session). Appends only: card addendum, actions.log lines,
# progress.md line, brain status mirror. No file rewrites, no deletes, LF, no BOM.
import shutil, os

TS = "2026-11-05 18:4x CT"

CARD = """
### {TS} addendum to the 13:00 F2a card - F2b is BLOCKED on Ask 1, no new ask

F2b (phase 2b, "retire the per-face copies") states its own dependency: F2a's two `OBJECTIVE ok` lines. They do not
exist, so F2b is `- [BLOCKED]`. **Ask 1 above is the only thing that unblocks it**; the GPU gate is open right now
(`gpu-render.lock` absent, `comfy_ctl.py status` 18:37:16 CT `guard=(0, ['IDLE'])`).

Measured, nothing moved (record `notes\\2026-11-05-cleanup-F2b-BLOCKED.md`):
- **The move is already built by the agy lane, and it is 23 files, not 24.** `git show --name-status 25e403c` (U7,
  12:00:59) deletes 23 `templates/faces/FC_*.api.json`; they are at `C:\\AI\\_archive\\2026-11-05-cleanup\\7\\faces\\`,
  not in phase 2. `git ls-tree 25e403c^ templates/faces | grep -c 'FC_.*\\.api\\.json$'` = **23**. "24" is the on-disk
  count - `templates\\faces\\README.md` says "24 templates on disk, 23 in git", `.gitignore` `*sydney*`.
- **`FC_SYDNEY.api.json` is intact**: 21171 B, mtime 2026-11-03 19:01:34 (predates the cleanup).
- **The rg clause is clean**: 7 hits = 4 records/history + 2 that name the phase-7 **archive** path deliberately
  (the F2a node-set test fixture and its evidence generator) + `make_b2_lora_template.py`, whose `DST` is
  `templates\\b2_fc_sydney_lora.api.json`, a file that still exists. 0 hits in `.pi\\agent\\skills` and `C:\\AI\\render`.
- **Not built**: the `templates\\b2.README.md` `--lora/--strength` section (0 hits; last commit 2026-10-30).

**One decision I am not making (it is the keep/drop call in your 12:0x CT card, so I am not adding a new ask):** this
F2b text moves the 3 `b2_fc_sydney_lora*.api.json` + their README, and v2 line 22-23/28 (Max's 11:12 audit) says
"**F2b must not move b2_fc_sydney_lora\\***" and "Every FC_SYDNEY and b2_fc_sydney_lora* file stays". I executed
neither version: with the item's dependency unmet, moving files that a plan-of-record line forbids is the one thing I
will not do unasked. Same for `faces\\README.md`: it is the per-face **builder doc** for the live
`make_b2_lora_template.py`, so the "per-face index" move would strand a generator.

Answer Ask 1 and F2b is one pass: run the 2 cells, quote the two OBJECTIVE lines, add the b2.README section, commit.
Nothing else in this pass: no GPU, no render, no lock, no model load, no successful HTTP, no process touched, no config
write, nothing deleted, no `.bak`, no GitHub. Sydney untouched.
""".format(TS=TS)

ACTIONS = [
    "{TS} | forge | pi-chat | START | F2b phase 2b (retire the per-face copies) - gate: F2a's two OBJECTIVE oks, measure the live phase-2 state before touching any template".format(TS=TS),
    "{TS} | forge | pi-chat | DONE | F2b phase2b -> [BLOCKED], not [x]. Dependency unmet: F2a is PARTIAL with no OBJECTIVE line and its 2 GPU cells await the GO (needs_derrick.md 13:00 Ask 1); F2a's own rule: F2b archives only after those two oks. Measured, nothing moved: clause 1 already built by agy 25e403c (23 FC_*.api.json -> C:\\AI\\_archive\\2026-11-05-cleanup\\7\\faces, NOT phase 2; the item's/v2's 24 is the on-disk count, git ls-tree 25e403c^ = 23, .gitignore *sydney*), clause 2 met (FC_SYDNEY.api.json 21171 B mtime 2026-11-03 19:01:34, untouched), clause 3 met with 0 real violations (rg = 7 files: 4 history + 2 archive-path fixtures by design + make_b2_lora_template.py whose DST still exists), clause 4 not met (no F2b commit; agy's 25e403c is already on gitea/master). b2.README --lora/--strength section not built (0 hits). v1-vs-v2 conflict NOT self-resolved: v2:22-23,28 says 'F2b must not move b2_fc_sydney_lora*' while this item's Do moves those 3 files + READMEs - keep/drop is Derrick's (12:0x card), so nothing moved; faces\\README.md is the per-face builder doc, flagged not moved. GPU gate open (no lock, guard IDLE 18:37:16). Pushes: HTTP 502 from qnap.tailf242b2.ts.net on both gitea (community, 17 ahead) and fleet-brain origin (3 ahead) = Gitea unhealthy on the QNAP, tailnet up. No GPU, no render, no model, no successful HTTP, no process touched, nothing deleted, no .bak, no git add -A, no force-push, no GitHub; Sydney untouched.".format(TS=TS),
]

PROGRESS = ("2026-11-05 18:4x F2b BLOCKED (cleanup phase 2b) - [F2b] the item's own dependency is unmet: F2a is PARTIAL with no "
            "OBJECTIVE line, its 2 GPU cells await Derrick's GO (C:\\AI\\community\\notes\\needs_derrick.md 13:00 CT Ask 1, unanswered), "
            "and F2a says F2b archives only after those two oks; GPU gate measured OPEN (no gpu-render.lock, comfy_ctl 18:37:16 CT "
            "guard=(0, ['IDLE'])), so one word unblocks it. Measured, nothing moved. Clause 1 is already built by the agy lane: "
            "git show --name-status 25e403c (U7 12:00:59) deletes **23** templates/faces/FC_*.api.json, which sit at "
            "C:\\AI\\_archive\\2026-11-05-cleanup\\7\\faces (23), not phase 2; the item's and v2's '24' is the on-disk count - "
            "git ls-tree 25e403c^ | grep -c FC = 23, and templates\\faces\\README.md states '24 on disk, 23 in git' (.gitignore "
            "*sydney*): count tracked and untracked separately. Clause 2 met: FC_SYDNEY.api.json 21171 B, mtime 2026-11-03 19:01:34, "
            "predates the cleanup. Clause 3 met, 0 real violations: the rg returns 7 files = 4 records/history + 2 naming the phase-7 "
            "archive path on purpose (test_b2_lora_param.py:13-14 and notes\\_f2a\\make_evidence.py:14 - the retired artifact IS the "
            "node-set fixture) + make_b2_lora_template.py whose DST is a template that still exists; 0 hits in .pi\\agent\\skills and "
            "C:\\AI\\render. Clause 4 not met: F2b has no commit (agy's 25e403c is already on gitea/master). The b2.README.md "
            "--lora/--strength section is not built (rg 0, last commit bb1290f 2026-10-30). Not self-resolved: v2 (notes\\2026-11-05-"
            "forge-cleanup-v2.md:22-23,28, Max's 11:12 audit) says 'F2b must not move b2_fc_sydney_lora*' / 'Every FC_SYDNEY and "
            "b2_fc_sydney_lora* file stays', this item's Do moves those 3 files + README, and faces\\README.md is the per-face builder "
            "doc for the live make_b2_lora_template.py - so I moved nothing (narrowing approved work is Derrick's 12:0x card, unanswered). "
            "Did not move the 23 files from phase 7 to phase 2: the F2a test/evidence resolve that path, a move makes the test "
            "skipUnless silently vacuous. Pushes: HTTP 502 from qnap.tailf242b2.ts.net on git push gitea master (community 17 ahead) and "
            "git push origin master (fleet-brain 3 ahead) - DNS/TLS/proxy answer so the tailnet is up and **Gitea on the QNAP is "
            "unhealthy**; records push themselves at 200. Record C:\\AI\\community\\notes\\2026-11-05-cleanup-F2b-BLOCKED.md. No GPU, no "
            "render, no lock, no model load, no successful HTTP, no process touched (loop pid 36992), no config write, nothing deleted, "
            "no .bak, no dated copy, no git add -A, no force-push, no GitHub; Sydney untouched.\n")

MIRROR = r"C:\AI\fleet-brain\40_projects\max-fix-tests\status\forge-fix-plan.md"

paths = {
    r"C:\AI\community\notes\needs_derrick.md": CARD,
    r"C:\AI\community\notes\actions.log": "\n".join(ACTIONS) + "\n",
    r"C:\Users\derek\5slock\ralph-community\notes\progress.md": PROGRESS,
}
for p, text in paths.items():
    data = open(p, "rb").read()
    nl = "" if data.endswith(b"\n") else "\n"
    with open(p, "a", encoding="utf-8", newline="\n") as f:
        f.write(nl + text)
    print("appended", p, len(text), "chars")

shutil.copyfile(r"C:\Users\derek\5slock\ralph-community\fix_plan.md", MIRROR)
print("mirrored fix_plan ->", MIRROR, os.path.getsize(MIRROR), "bytes")
