# Prove what is live, not what the item expected (unreviewed)

**Tag:** unreviewed · **Date:** 2026-10-31 · **Agent:** Forge (ralph, OPT4 close-out) · **Lane:** home-lab

## The situation

A parent "verify + test" item asks to confirm three settings are live and to keep a setting only if it is
within 5% of best. Its two sweep sub-items (OPT4a worker count, OPT4b placement) are closed. Two of the
three confirmations pass. The third does not: the item expects `--resident-budget-gib 32`, and the live
engine has no resident-budget flag at all.

## The trap

Read literally, that is a failure of the box, and the tempting fix is to restore 32 GiB so the item's text
matches. That would have cost the biggest real win in the whole tuning block: the RAM-budget flag was
removed by an item approved **after** this item was written (OPT5, Derrick 13:28 CT), and its benchmark
passed every keep bar (decode +46-57%, wall -41%, prefill +179%). The parent item is older than the
decision that superseded its expectation, and the plan text was never edited.

Same shape in the other direction: the same item's `--pool-workers 8`-era expectation was superseded by
OPT4a's measurement. An old verify item is a list of claims about the future, not a spec of the present.

## The move that works

Answer a verify clause with **evidence of the running state**, then state the supersession in the record:

- Read the live command lines of the processes, not the config file alone:
  `Get-CimInstance Win32_Process -Filter "Name='strata.exe'"` / `"Name='strata-vision.exe'"` →
  ExecutablePath, CreationDate, full CommandLine. The child process carries the flags the spawner used, so
  `--threads 6` in the running vision process proves vision threads=6 in a way the config alone cannot.
- For a setting that is *absent*, prove absence (the flag is not in the live args) and then narrate the
  chain with its numbers: `32` (`.bak-1328`, baseline pp ~617 / tg ~83 / wall 7-8 s) → `28`
  (`.28gib-1251`, prompt read -24%, 0 of 1859 lend slots in RAM, reverted) → removed (OPT5 kept, all bars
  passed). The item's "before/after numbers for every setting" clause is satisfied by the chain — that is
  exactly what a done-line of that shape is for.
- Keep the two `resident` flags apart in the write-up: `--resident-budget-gib` (RAM budget) vs
  `--kv-resident 32768` (resident KV blocks). A reader who conflates them will "confirm" a setting that is
  not live.
- Do not silently rewrite the parent item's expectation into the box. Name it in the record, keep the old
  config file on disk as the restore path, and let the owner (Max/Derrick) decide to re-open.

## The version-proof trick this cost me

`strata-vision.exe --version` prints the bare word `strata-vision`, and its Windows version resource is
empty (`FileVersionRaw 0.0.0.0`), so "confirm vision.exe 0.1.54" cannot be answered with a version query.
The proof chain that works:

1. the running process's `ExecutablePath` (it is under `strata-engine-028\engine\0.1.54-...`),
2. that directory's `BUILD.json` (`version`, `source`, `commit`, `cuda`),
3. SHA-256 of each binary against the `files[]` list in `engine-component.json` — this also proves the
   running model engine, not just the vision one,
4. and only as a corroboration: `strata.exe --version` → `strata 0.1.54`.

Step 3 is the one that turns "the path says 0.1.54" into "the bytes are the signed 0.1.54 component". It
is a few seconds of hashing for a 108 MB + 272 MB pair.

## Applies to

Any ralph `fix_plan` item that says "confirm X is live" — always check whether a later approved item
changed X, and write the chain, not a pass/fail. Any binary with no version string. Any time a child
process is spawned with flags by a parent config: prove from the child's live CommandLine.
