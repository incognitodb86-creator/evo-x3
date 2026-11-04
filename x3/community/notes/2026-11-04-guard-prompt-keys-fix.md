# Guard scope fix: MiniMaxH3PromptBuilder prompt keys, named gate failures, stated ages 18+

2026-11-04 12:1x CT (sydney-lane, pi). Derek: "Ok all 3", then "1 and 2" (apply + render).

## What failed, measured
`runs/pw_strip_20261104b/fc_sydney_strip` never rendered: `run_queue.py` closed `rc=5` at 11:25:10 after
`GATE-FAIL pos=1 tag=fc_sydney_strip adults guard` twice. The prompt is clean (guard_ok true,
`adult_stated` true). Cause: the gate reads prompts only from `comm.PROMPT_KEYS`, and the new node
`pw` = `MiniMaxH3PromptBuilder` carries the prompt under **`prompt_text`** (5,535 chars) plus
**`builder_state`** (6,093 chars) - keys not in the list. The guard collected 0 of the 5 string values in
that graph, so `any(adult_stated)` was False and the gate failed closed. Any graph with that node shape
fails every time. Control from the same day, `runs/take_wide_20261104/w01_s51083411`, puts the text in
`c0` / `MiniMaxH3ReferenceToVideo` / key `prompt`: gate passed, clip rendered.

## The three changes (scripts/comm.py, scripts/run_queue.py, scripts/tests/test_guard_scope.py; +94 -12)
1. **Read the keys the node writes.** `PROMPT_KEYS` += `prompt_text`, `builder_state`.
2. **Name the failure.** New `comm.guard_reason(g, require_adult=True) -> (ok, reason)`;
   `run_queue.guard_graph` stays a thin bool wrapper so the 6 callers
   (`run_graph_job`, `make_b2_request`, `make_bfs_request`, `make_render`, `p6_review`, tests) are unchanged.
   The queue's GATE-FAIL line prints the reason. Measured strings: `no prompt text visible to the guard
   (every node input is outside PROMPT_KEYS - check the node's key names)`,
   `minor-coded word in node pw (MiniMaxH3PromptBuilder).prompt_text`, `no adult stated in 2 prompt string(s)`.
   A prompt the guard cannot see is now a named failure, never a silent pass.
3. **Loosen the adult proof, narrowly.** `_ADULT_RE` accepts the word `adult` plus an unambiguous age
   18-99 stated as an age: `28-year-old`, `28 years old`, `28 yo`, `age 28`, `21+`.
   Measured still blocked: `a 17 years old woman`, `a woman in her twenties`, `a 12-year-old`,
   `a woman on a terrace`, `adulthood`. Unclear text stays fail-closed.

## Proof
- `python -m pytest -q scripts/tests/{test_adults_guard,test_guard_scope,test_p6_review,test_phase1_still}.py`
  **before: 6 failed, 43 passed. after: 6 failed, 50 passed.** 7 new tests, all green, no new failures.
- The named pre-render gate pair `test_p6_review.py` + `test_guard_scope.py`: **33 passed**.
- `runs/pw_strip_20261104b/fc_sydney_strip/request.api.json` → `guard_reason (True, '')`, `guard_graph True`.
- `runs/take_wide_20261104/w01_s51083411/request.api.json` → `guard_reason (True, '')`, no regression.

## The 6 pre-existing failures are not from this change
`test_adults_guard.test_graph_require_adult` expects `guard_graph(g("a woman"))` True - the default before
Max's 2026-11-03 flip to `require_adult=True`; and 5 `test_phase1_still` cases use template prompts that
state no adult. Both need a Max/loop decision (update the expectation, or put an adult statement in the
still templates). Left untouched on purpose.

## Rollback
`scripts/comm.py.bak-guard-20261104-1214`, `scripts/run_queue.py.bak-guard-20261104-1214`,
`scripts/tests/test_guard_scope.py.bak-guard-20261104-1214` (bytes of the previous versions), plus
`git checkout -- scripts/comm.py scripts/run_queue.py scripts/tests/test_guard_scope.py`.
The tested sandbox and the patch file: `C:\Users\derek\sydney\work\guard-fix-2026-11-04\`
(`PATCH_adults_guard_3items.diff`). Lane record: `C:\Users\derek\sydney\notes\2026-11-04-adults-guard-fix-3items.md`.

## Box notes worth keeping
- `builder_state` carries the same prose as `prompt_text`, so a prompt that states an age also passes
  through the state blob; the denylist scans it too, which is the point of adding it.
- Never poll a detached render on `OBJECTIVE` alone: a gate-failed clip never writes that line. Poll with
  a terminal condition (`BATCH closed` / `FAIL` / `rc=`) and a wall cap, and report the first queue log line.

## 12:1x CT - the second bug this fix exposed, same family (Derek: "1")
The gate fix let the clip through: `runs/pw_strip_20261104c/fc_sydney_strip` rendered well - `OBJECTIVE ok
frames=124 size=768x1344 audio=True bytes=1954116`, ffprobe h264 768x1344 124f 5.1667 s + aac, delivered to
`/pi-drop/pw-strip-2026-11-04/fc_sydney_strip_s51083510.mp4` - and the batch still closed `rc=5`, because the
journal step crashed: `FAIL pos=1 tag=fc_sydney_strip error AttributeError: 'list' object has no attribute 'encode'`.
Cause: `run_queue.py` built `prompt_sha256` as `hashlib.sha256(prompt.encode("utf-8"))` where `prompt` is read
from `c0.inputs.prompt`. In a writer-routed graph that value is the link `["pw", 0]`, not a string. So a good
render was marked failed, twice, and done=0/1. Same root shape as the gate bug: harness code that assumes the
prompt text sits plainly in `c0`. `still_done` had the same pattern on the Klein text input.
**Fix:** `run_queue.prompt_behind(g, value)` returns the prompt string behind an input - plain text, or the text
of the node a link points to, via `comm.prompt_items`; `run_queue.prompt_sha` returns
`("unresolved", why)` instead of raising, and the queue logs `NOTE ... prompt_sha256 unresolved: <why>`.
Both call sites use it.
**Proof:** writer graph `runs/pw_strip_20261104c` -> `b85d945825850e65...`, byte-identical to the sha the
builder tool reports for the same prompt (`prompt_sha256 b85d9458`), so the journal and the builder agree.
Plain-prompt graph `runs/take_wide_20261104/w01_s51083411` -> `5d0540d49ca39427...`, identical to what the old
code produced: no regression for normal graphs. Old code on the writer graph: `AttributeError`.
**Tests:** `scripts/tests/test_run_queue_prompt_sha.py` (6 tests, green) covers plain text, the writer link, the
Klein `CLIPTextEncode` link through `still_prompt`, and the unresolvable shapes (missing node, empty string,
non-string, node with no prompt key) as notes rather than crashes.
Suite `test_adults_guard + test_guard_scope + test_p6_review + test_phase1_still + test_run_queue_prompt_sha`:
before this change 6 failed / 50 passed, after 6 failed / **56 passed** - the 6 are the same pre-existing ones.
Rollback: `scripts/run_queue.py.bak-sha-20261104-1212`.
Not touched, on purpose: `free_comfy note expected str, bytes or os.PathLike object, not function` in the same
writer-graph path (caught and logged, cosmetic) and the 6 pre-existing test expectations Max owns.
