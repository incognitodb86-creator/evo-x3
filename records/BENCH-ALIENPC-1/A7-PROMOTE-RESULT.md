# A7 promotion — `tq2_vsa_0.2` / `oc_ref_2pass` + `pick_template()` — 2026-11-19

All times are America/Chicago (CT). Doer: Grok Bot executor. Approvals: Derrick t2970s10407 and t2971u (promote `tq2_vsa_0.2` as the video template winner and apply the `pick_template()` fix). A8 lockdown was not run. A5 still tests were not queued.

`mono` commit: `4d909034f9e5764f61cdae84122f05700b9e0e53` (`4d909034`). gitleaks: no leaks found on the promotion paths and the staged commit.

## What was promoted

Production template `oc_ref_2pass.api.json` is the TQ1 `oc_ref_2pass` graph with:

- `m_vsa.start_percent=0.2` (the stage-2 winner vs 0.0)
- pass-1 `ksel.sampler_name=euler`, `s0_sched=simple` 8 steps
- pass-2 `p2sched=beta` 3 steps, denoise 0.4
- 4-header Beta 7 (header-free lost in stage 2 and was not promoted)

1-pass `oc_ref.api.json` is unchanged and stays available via `--template oc_ref`. TQ4 Beta 7 candidates (`two_person`, `ref2va_16x9`, `long_continuation`) were not promoted (still need Derrick's eye pick). M5 H3 realism stays dropped (t2885u). Mystic audio arm stays rejected.

## Template hashes (SHA256) — AlienPc live, X3 mono clone, and `mono` match

| File | SHA256 |
|---|---|
| `templates/oc_ref_2pass.api.json` (X3 tree and AlienPc tree) | `1d3ec1da3ef8f2f2d8f111e52697713685d9084cb2271cc0aac8fc32e1882c9c` |
| `scripts/allowlist_promoted.json` | `834d1d0a65e3bec938167ddf5f58ac5aaefa75024bdf4a1a4b94fef2195a71c4` |
| `templates/CANDIDATES-TQ.md` (both trees) | `0d85a42db833cde67e1c18c85b33f93b15ce932e8ee1ac7c66acdef9424d6f8b` |
| 1-pass `templates/oc_ref.api.json` (unchanged) | `d3b2f381fdb6a39ca4b399a4587d911fadf66125d2987183195dc09950a55c4a` |
| leftover candidate `oc_ref_2pass.candidate.api.json` (still `start_percent=0.0`, not allowlisted) | `c7ed0621cf9d76a5e2097bbdb9e86d8ea93de605855e7789d39a6d59872125b8` |

Verified MATCH on:

- `/workspace/mono-sync` (both `x3/community` and `alienpc/community` copies)
- AlienPc live `C:\AI\community\` (installed 20:46:44–20:47 CT, lease cleared)
- X3 user clone `/home/derekboone/evo-x3/` (files copied for tests only)

## `pick_template()` fix

In `x3/community/scripts/parody/fill_request.py`:

- `oc_ref_2pass` is registered in `TEMPLATES`.
- Default portrait `ref` routing (`768x1344`, with or without identity) now returns `oc_ref_2pass`.
- 16:9 `1344x768` ref stays on 1-pass `oc_ref` until TQ4 is promoted.
- Explicit `--template oc_ref` still fills the 1-pass graph.
- `_c0_canvas_for_graph()` keeps 2-pass `c0` at half the requested final canvas (384x672 when the caller asks for 768x1344) so `fill_request` does not smash pass-1 up to the final size.

## Tests (dry-run only, no GPU video render)

- Box: `test_pick_template_2pass.py` 6 passed; `tests/test_template_allowlist.py` 13 passed, including `test_promoted_oc_ref_2pass_vsa_0_2_allowlisted_and_candidate_refused` (promoted graph ALLOW, candidate and VSA 0.0 REFUSE, 1-pass `oc_ref` still ALLOW).
- X3 user clone, `/home/derekboone/AI/render/x3/.venv`: same 6 + 13 passed at 8:48 PM CT.
- Full `test_u55_clip_types_e2e.py` was not used as a gate on these checkouts: they have no local RefMod tree under the clone's `comfy-alienpc/models/refmods`. The new 2-pass unit tests cover routing, half-res `c0`, VSA 0.2, and allowlist behavior without that tree.
- S2 allowlist hook into `run_queue.py` / `comm.py` was not installed (that is A8, deferred until A5 still tests).

## Live host apply

- **AlienPc:** lease taken 20:46:44 CT (`Grok Bot | A7 promote tq2_vsa_0.2 + pick_template`), backups under `C:\AI\_archive\20261119\a7-promote\`, live files installed and hash-verified, lease cleared, no `gpu-render.lock`. ComfyUI was not started. No still or video was queued.
- **X3 live `/home/evo/AI/community`:** not updated. The X3 lease is still held by `Max Architect | Hermes 3-model W1b rerun | 2026-11-19T19:57-06:00`, and the running test is using live community writer scripts. After that test finishes and the lease is cleared, pull `mono` `4d909034` into `/home/evo/AI/community` (or copy the promoted files) so live `pick_template()` matches AlienPc.
- Dual-host `snapshot-live-setup.sh` + `sync-config-copies.sh` were **not** run in this pass, so this commit does not include a fresh `hosts/*/live` snapshot (would have mixed a large live-config diff into the promotion, and the X3 lease/test was still active).

## Rollback

Restore `C:\AI\community\templates\CANDIDATES-TQ.md` and `scripts\allowlist_promoted.json` from `C:\AI\_archive\20261119\a7-promote\`, delete live `templates\oc_ref_2pass.api.json`, and revert `mono` to the parent of `4d909034`. 1-pass `oc_ref.api.json` was not overwritten.
