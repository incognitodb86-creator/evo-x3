# brief7 - Forge's independent verification of the archive (Max did the move)

Brief: `C:\AI\community\briefs\2026-10-30-0810-forge-brief7-archive-probe-submit.md` (Max2, 8:10 AM CT; plan
`C:\AI\community\plans\2026-10-30-0800-forge-simplify-plan.md`, cut #15 only; no renders, no GPU, no lock, delete
nothing). **The brief asked Forge to do the move and write `notes\2026-10-30-brief7-probe-submit-DONE.md`. Max
Architect 2 did both first, on Derrick's 8:27 AM CT ask ("Forge appeared stalled"), and his note says "Forge:
brief7 needs no further action."** I did not move anything and I did not edit his note.
`notes\2026-10-30-brief7-probe-submit-DONE.md` stays as he wrote it. What follows is my own evidence, gathered
with my own commands, for the record.

## 1. The archive is exactly as the brief specifies, and nothing was copied

| check | result |
|---|---|
| source `C:\AI\community\scripts\probe_submit.py` | `Test-Path` **False** (moved away, no copy left) |
| archive `C:\AI\_archive\2026-10-30-forge-simplify\scripts\probe_submit.py` | present, **1,894 B**, mtime **2026-10-28 15:42:38** (the original mtime, so a move, not a re-write) |
| sha256 `Get-FileHash` | `1169C498105F3F0746BC651163D88199D9A3EB7BE02F62D3A8DB4CDA4B48B256` |
| sha256 `hashlib` (python, my format) | `1169c498105f3f0746bc651163d88199d9a3eb7be02f62d3a8db4cda4b48b256` - same |
| my own pre-move hash, taken before anyone moved it | `1169c498105f3f0746bc651163d88199d9a3eb7be02f62d3a8db4cda4b48b256`, 39 lines, 1,894 B - **matches** |
| a `probe_submit.py` anywhere else under `C:\AI` or `C:\Users\derek\forge` | none (the archive is the only copy) |
| the other 5 `probe_*.py` in `scripts/` (cut #19) | untouched - `probe_full / probe_nodes / probe_obj / probe_sharpen / probe_spec`, mtimes 2026-10-28. Only cut #15 was approved, so I touched none of them |
| `git status` for `scripts/probe_submit.py` | empty - the file was **never tracked**, so the move has no repo effect and nothing to commit for it |

The FO-4 claim in the plan is true of this file: the archived copy contains **no `guard_ok`**, and it POSTs
`/prompt` itself (L18-22) and cancels with `DELETE /prompt` (L28). It is a 39-line direct-API bypass.

## 2. Callers and references - nothing will break

`rg -n probe_submit C:\AI\community C:\Users\derek\forge` (ripgrep 15.2.0, the briefed command). One tooling
warning, not a search failure: `rg: C:\Users\derek\forge\NUL: Incorrect function. (os error 1)` (a stray `NUL`
file in this lane's cwd), which is why that run exits rc 2.

Every hit, in full:
- `C:\AI\community\scripts\probe_submit.py:9` - its own usage string (now lives at the archive path).
- `C:\AI\community\plans\2026-10-30-0800-forge-simplify-plan.md:22,34,58,77` - the plan's own text (FO-4, the minimal-version step 3, cut row #15, the order line).
- `C:\AI\community\briefs\2026-10-30-0810-forge-brief7-archive-probe-submit.md:1,2,6,7,8` - the brief itself.
- `C:\AI\community\notes\terrace_retest_plan_probe.txt:439` - a **directory listing captured on 2026-10-29** (an `os.listdir` dump that includes the filename as text). Not a call.

Then, wider than the brief asked, so the answer is complete rather than lucky:
- `rg -uu -n -F probe_submit` over the two briefed trees restricted to text types (`py ps1 psm1 json jsonc md txt csv cmd bat xml yaml yml`) - same 11 hits, nothing new. (The unrestricted `-uu` walk over the whole trees timed out at 300 s on binary/pycache volume; the scoped run is complete, and that limit is stated so the record is honest.)
- `rg -uu -n -F probe_submit` over `C:\Users\derek\5slock`, `C:\AI\director`, `C:\Users\derek\.pi` (beyond the brief): only pi **session transcripts** (`.jsonl` logs of past chats, including this lane's and Max's) - no task XML, no `ralph.ps1`, no skill, no settings, no `.jsonc`.

**Conclusion: no caller exists in code.** Nothing was fixed, per the brief.

## 3. The adults-only check on the two real submit paths (my own grep, current files)

| file | line | code |
|---|---|---|
| `C:\AI\community\scripts\comm.py` | 41 | `def guard_ok(t):` - the 13-line keyword guard, unchanged |
| `C:\AI\community\scripts\comm.py` | 194 | `def run(g, tag, meta, outdir, ...)` - the guarded submit path |
| `C:\AI\community\scripts\comm.py` | 196 | comment: "pre-check for the outcome record only; the block below is the gate that stops the queue" |
| `C:\AI\community\scripts\comm.py` | 197-198 | the logging-only pre-check (`outcome(out, "guard", ...)`) - **cut #14, not approved, left in place** |
| `C:\AI\community\scripts\comm.py` | 200-202 | the real gate: `if not guard_ok(s): log(f"SKIP {tag} adults-only guard hit", logfile); return None` - runs before the `/prompt` POST at L204+ |
| `C:\AI\community\scripts\run_graph_job.py` | 127 | `if not comm.guard_ok(s): log(f"CLIP_SKIP {a.tag} adults-only guard"); return 3` |

After this cut, every ComfyUI `/prompt` submit on the box goes through `guard_ok`: `comm.run()` (L200-202) and
`run_graph_job.py` (L127, which calls `comm` for the graph it submits). `probe_submit.py` was the only bypass and
it is now off the live tree. I did not run the test suite (Max's note records 21 passed plus a live
"teen girl" block) - brief7 step 4 asks only for the call sites, which are above.

## 4. State

No render, no queue, no GPU, `C:\AI\locks\gpu-render.lock` never touched, nothing deleted, no other simplify cut
touched, no config changed. `gpu_guard` IDLE. B2 default graph unchanged.

**Two process notes, kept on record:** the brief and Max's action describe the same work at the same time, which is
how the "stalled" situation arose - the fix is that a brief naming Forge gets picked up by Forge, and if the
operator wants it done sooner, say so in the brief and I hand it back with a "done by" line. And Max's note is
untracked in git (`?? notes/2026-10-30-brief7-probe-submit-DONE.md`); I am not committing another agent's file.
