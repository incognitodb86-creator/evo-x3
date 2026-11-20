# Handoff to Max: X3 apply (U59, agy Hydrogen Medium) + what stays with you and Derrick, Nov 20 2026

From: Opus (VS Code, Windows clone), 2026-11-20 ~10:35 AM CT. Derrick 2026-11-20 ~10:20 AM CT: "do a final double
check for errors and debug. red team audit ... include a hand off prompt for max. I want him to delegate this to
antigravity hydrogen medium to implement."

The commit is the `mono` commit that adds this file: `git -C ~/evo-x3 log -1 --format=%h -- records/HANDOFF-MAX-20261120.md`.

## Paste this to Max

```text
Max, pull mono on the X3 (~/evo-x3) and on AlienPc. Then:

1. Launch agy on U59 at Gemini 4 Hydrogen, MEDIUM effort (Derrick 2026-11-20 ~10:20 AM CT). Use the
   launcher's medium id (gemini-4-hydrogen-medium if that's what it's called). If the launcher can't run
   medium, tell Derrick; don't switch to high quietly.
   Brief: records/U59-x3-hermes-pixlstash-apply-brief-20261120.md
   Give it the mono SHA you pulled, for S0. Leave x3-lease.txt EMPTY at launch: the two installers take and
   clear the lease themselves, and agy takes it only for S1 and S4.
2. When agy stops, check records/U59-RESULT.md (S0-S5 and the Tests), then push GitHub first and mirror to Gitea.
3. Then do your own items in records/HANDOFF-MAX-20261120.md ("Max does these himself").
Don't hand agy the REA C1-C7 code: Derrick runs those from the Hermes code chat, since they're the local-LLM
coding test.
```

## What changed since `02f552c6` (red-team pass)

1. **Critical, both installers:** every multi-line `sudo -n -iu evo bash -c '...'` block was broken. sudo `-i`
   rewrites argv for a login shell, escaping every non-alphanumeric character except `_ - $` (sudo
   `src/parse_args.c`, VERIFIED on sudo-project/sudo `main`). Two effects:
   - `$1` and `$B` expand to empty in evo's login shell;
   - each newline becomes a line continuation.

   So backups, installs, the PixlStash token call and the llama-swap probes would have failed or written to the
   wrong paths. Fixed with one `as_evo` helper in both scripts: `sudo -n -u evo -H env -C /home/evo PATH=...
   HERMES_HOME=...`.
   - Offline test with a fake sudo that rejects `-i`: the PixlStash `curl -K -` header is exact (token present,
     CR stripped), and the `probe_alias` payload and header are exact.
2. **PixlStash memcap:** apply now uses `set-property --runtime`. A plain `set-property` writes a `user.control`
   drop-in that outranks `10-memcap.conf` and survives rollback. `--rollback` now also resets the live values from
   the backed-up drop-in.
3. **`--create-smart-sets`:** combined with `--rollback`, it used to run the Smart Set path and skip the rollback.
   Now that combination is refused. The usage text and PX plan now say it never POSTs; the sets are made in the UI.
4. **Picker:** `/api/v1/pictures` calls now send `descending=true` explicitly, as `OPERATOR.md` does with
   `sort=DATE`. That keeps "recent imports" and "strongest likeness" from depending on an unknown default. A test
   asserts it.
5. **Sydney lines:** removed the Sydney Sweeney / FCSydny distinction from these files:
   - `hosts/x3/hermes/memories/USER.md`
   - `x3/render/OPERATOR.md`
   - `x3/render/records/LOOPTEST.md`
   - `records/hermes-direct-render/PLAN.md`
   - `records/UNI-OPUS-HERMES-WORKSPACES/BRIEF.md`

   The U56 #2 voice rule stays: no celebrity voice audio ref on named parodies. The live `USER.md` entry is U59 S1.
6. Tests on this PC:
   - picker 8 passed;
   - `test_flux_h3_redteam.py` 7 passed;
   - `pi-job` 9 passed;
   - `bash -n` clean on both installers;
   - U59's S1 script tested on the old `USER.md`: removes 1 entry, and a second run is a no-op.

## Order

1. **U59 (agy, X3):** S1 USER.md, then H7 workspaces, then PX1+PX2, then the C0 clone.
2. **Max, X3:** the `models.json` field check (below).
3. **Derrick, X3 WebUI:** the D4 check. Pick profile `code` and ask `pwd`. If it says `/home/evo/workspace`, Max
   archives `hermes-webui.service.d/30-workspace.conf` and restarts `hermes-webui`.
4. **Max, AlienPc:** M6 Flux likeness A/B, per [FLUX-LIKENESS-20261120/BRIEF.md](FLUX-LIKENESS-20261120/BRIEF.md),
   under the AlienPc lease. Download `Miraclein_4.5_9b_FP8.safetensors` first (Derrick D6 yes).
5. **Derrick, Hermes code chat:** REA C1 to C7, one at a time, per
   [REA-PARODY-PIPELINE/PIJOB-TASKS.md](REA-PARODY-PIPELINE/PIJOB-TASKS.md).
6. **Max:** C8 (review, merge, deploy) and C9 (`rea-remake` skill) from
   [REA-PARODY-PIPELINE/PLAN.md](REA-PARODY-PIPELINE/PLAN.md).
7. **Derrick, Hermes render chat:** R1 to R4, per [REA-PARODY-PIPELINE/RENDER-TEST.md](REA-PARODY-PIPELINE/RENDER-TEST.md).
   Max writes `RESULT-RENDER.md`.

## Max does these himself

- **`models.json` check** (prints only model ids and two non-secret fields, never `apiKey` or `baseUrl`):

```bash
sudo -n -u evo -H env -C /home/evo python3 - <<'PY'
import json
d = json.load(open("/home/evo/.pi/agent/models.json", encoding="utf-8"))
for prov, pv in (d.get("providers") or {}).items():
    for m in pv.get("models", []):
        print(prov, m.get("id"), "maxTokens=%s" % m.get("maxTokens"),
              "budgetField=%s" % (m.get("compat") or {}).get("thinkingTokenBudgetField"))
PY
```

  Expected, matching `config/pi-evo/models.json.example`: every Flash-Next row has `budgetField=thinking_budget_tokens`,
  and `alienpc coding_swift15_iq3s_esp` has `maxTokens=32768`. If a row differs, fix only that field, with a backup.
- **Rollbacks, if U59 needs one later:** roll back in reverse order.
  1. `bash ~/evo-x3/scripts/apply-pixlstash-upgrade.sh --rollback`
  2. `bash ~/evo-x3/scripts/apply-hermes-workspaces.sh --rollback`
  3. Restore `USER.md` from `/home/evo/.hermes/_archive/default-USER.md.bak-20261120-u59`.
- **Later, each needs Derrick's yes:** PX5 (re-enable `ComfyUI-PixlStash` on AlienPc, Q-PX3) and PX6 (dataset
  picker, Q-PX4). They're briefs, not part of U59.

## Open Q-cards for Derrick (defaults in bold)

- **Q-PX1:** detach the empty "Library 1" and archive the old `_u39`/`_u42` vault backups. **Yes, archive first.**
- **Q-PX2:** create the 4 Smart Sets in the PixlStash UI and review `--status` before collapsing dedup stacks. **Yes.**
- **Q-PX3:** re-enable `ComfyUI-PixlStash` on AlienPc for the Face Likeness Gate. **Yes, after M6.**
- **Q-PX4:** use `character_set_suggestion` for M2 RefMod picks. **Yes, when M2 resumes.**
- **Q-RP1 to Q-RP4** (REA): decompose on AlienPc; a 2-shot clip under 15 s that Derrick picks; Beta 7 layout as
  `h3-writer` makes it today; U5 nodes later.
  See [REA-PARODY-PIPELINE/PLAN.md](REA-PARODY-PIPELINE/PLAN.md).
