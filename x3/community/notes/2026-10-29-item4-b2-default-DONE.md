# 2026-10-29 item 4 - B2's render setup is the default for new render runs (DONE, closed 08:24 CT)

Derrick 2026-10-29 6:59 AM CT: "Ok let's keep the b2 setup and make it default". fix_plan MAX item 4.
No render, no GPU job, no ComfyUI/llama-swap call this pass. CPU only.

## B2 = the setup being made default
`C:/AI/community/runs/terrace_dom_q5guide_20261028_s51083007` (scored 6/10; T4 stock simple_v2 tied at 6/10 but wider framing).
Graph of record: `runs/terrace_dom_q5guide_20261028_s51083007/request.api.json`, 20,072 B, 26 nodes,
sha256 `8d1d1a41e9915f2a3ef3f1350b65a4bf563f9607af7e3ed9538e4c9abae4695e`. Paid render proof in that dir:
`objective.json` ok=True, 243 f, 768x1344, 24/1, audio=True, 240.1 s.

Settings carried as-is (read from that file, not restated from prose): `10Eros_Max_h3_8stepTURBO_beta7_int8HQ`,
CLIP `qwen3vl_32b_minimax_h3_nvfp4_awq`, video VAE `minimax_h3_video_vae_int8_convrot`, audio VAE `minimax_h3_audio_vae_fp32`,
`euler` + `simple` 8 steps on the FULL schedule (pass 1), pass 2 `BasicScheduler(beta, 3, denoise 0.4)`,
`MiniMaxH3SigmaShift` 12.0 / 3.0, VSA `selection.keep_percent 10`, `MiniMaxH3AddGuide` frame 0 (start image, vae wired)
before BOTH BasicGuiders, `c0.ref_image_size = max`, one reference slot (`ref_images.ref_image_1`),
`MinimaxH3LatentUpscaler3D` mode `scale by multiplier` 2.0 (384x672 -> 768x1344) with `enable_temporal_chunking true`,
audio decoded from the pass-1 latent, `c0.length 243`, `mkvid.fps 24`. Start image in the file: `community/TERRACE2_768x1344.png`
(present in ComfyUI/input, 1,352,963 B); the per-run keys the loop changes stay per-run (`img.image`, `c0.prompt`,
`noise.noise_seed`, `save.filename_prefix`).

## What was changed
1. **NEW default graph file** `C:/AI/community/p7/graphs/default_b2_terrace_dom_q5guide_s51083007.api.json`
   = B2's `request.api.json` copied byte-for-byte, verified: 20,072 B, sha256 `8d1d1a41...4695e` equal, 26 nodes,
   parses as JSON, `c0.length 243`. Nothing inside was edited (name carries the provenance, as every other file in `p7/graphs`).
   Scripts: `C:/AI/community/notes/item4_b2_default_probe.py` (read-only probe of B2 vs the old default),
   `C:/AI/community/notes/item4_b2_default_verify.py` (byte/sha/parse check).
2. **`fix_plan.md` "## Stock path" line** now points at that file and at `--frames 243`
   (it named `ali163_top5_gi046_s51160001.api.json` and `--frames 124`, which predates beta 7).
   Backup: `C:/Users/derek/5slock/ralph-community/fix_plan.md.bak-20261029-item4-stockpath`. MAX block left untouched.
3. **Skill `C:/AI/community/skills/h3-hc-render/SKILL.md` section 2 "Base graph"** now names the B2 default
   with its sha256, the four keys that may change and `--frames 243`, and marks the two previous defaults
   (`runs/ali147_pool_promptv2_s51080000`, then `p7/graphs/stock_base_tenstrip10.api.json`) as superseded for new runs.
   Backup: `SKILL.md.bak-20261029-b2default` (same dir).

The old default is not deleted: `p7/graphs/stock_base_tenstrip10.api.json` (beta6 int8, 124 f, 1344x768,
single-pass, shift 10/3, 10 steps - measured by the probe) stays on disk for reproducing those ids.

## The live pointer in PROMPT.md - was blocked, RESOLVED at 08:24 CT
`C:/Users/derek/5slock/ralph-community/PROMPT.md` was protected from this agent in the first pass
(`edit` denied by policy: `matched 'edit:C:/Users/derek/5slock/ralph-community/PROMPT.md'`), and PROMPT.md
item 1e is the real default the Ralph loop follows ("PROMPT.md is read fresh every pass", ralph.ps1:51 runs
`pi --print ... @PROMPT.md`). Derek lifted it at 8:20 AM ("PROMPT.md is no longer protected ... Finish item 4"),
so the two lines below were applied verbatim at 08:24 CT. Backups, both byte-identical to the pre-edit file
(sha256 `62B6DE7863AEB6D9D6E3ED8DB74A7C7E87769F96B5E8792EC33D674EF018177B`, hash-checked before writing):
`PROMPT.md.bak-20261029-item4-b2default` (first pass) and `PROMPT.md.bak-20261029-item4-apply` (this pass).
Applied as lines 13-14 (item 1e, 1f):

```
     e. Build graph: copy C:\AI\community\p7\graphs\default_b2_terrace_dom_q5guide_s51083007.api.json to <run_dir>\request.api.json and change only LoadImage path, c0.prompt, noise_seed, filename_prefix. That file IS the B2 setup (Derrick 2026-10-29 6:59 AM CT "Ok let's keep the b2 setup and make it default"): a byte-identical copy of runs\terrace_dom_q5guide_20261028_s51083007\request.api.json, sha256 8d1d1a41e9915f2a3ef3f1350b65a4bf563f9607af7e3ed9538e4c9abae4695e, 20072 B, 26 nodes = beta7 int8HQ, euler/simple, 8 steps full schedule + pass 2 beta/3/denoise 0.4, shift 12/3, VSA keep_percent 10, AddGuide frame 0 on both passes, ref_image_size max, 384x672 -> LatentUpscaler3D x2 -> 768x1344, 243 frames, 24 fps. Do not change any of those.
     f. Render: C:\AI\director\.venv\Scripts\python.exe C:\AI\community\scripts\run_graph_job.py <run_dir> <id> --frames 243 (the number must equal c0.length in the graph you copied; the B2 default renders 243 f = 10.125 s at ~240 s GPU. runs gpu_guard and gpu lock).
```

`--frames 243` is not optional: `run_graph_job.py` fails the objective gate when `abs(frames - c0.length) > tol`,
so a 243-frame default graph requested with `--frames 124` would burn a paid window and then redo twice.

### Verification of the applied lines (CPU only, `notes/item4_verify_prompt_lines.py`)
The check reads the live PROMPT.md, pulls the graph path, the `--frames` number, the sha256 and the byte/node
claims out of lines 13-14, and tests them against the file on disk - it verifies the prompt, not my prose:

```
1e line 13, 748 chars / 1f line 14, 267 chars
target = p7/graphs/default_b2_terrace_dom_q5guide_s51083007.api.json  exists True, 20,072 B,
         sha256 8d1d1a41e9915f2a3ef3f1350b65a4bf563f9607af7e3ed9538e4c9abae4695e
bytes match claim True | sha match True | node count match True (26)
c0.length = 243 -> frames arg equals c0.length: True
byte-identical to B2 request.api.json: True
frozen settings in the default: beta7 int8HQ, 8 steps + simple, pass2 [beta, 3, 0.4], shift [12.0, 3.0],
         vsa_keep 10, ref_image_size max, addguides [ag0, ag1], upscaler [scale by multiplier, 2.0], euler, fps 24
old strings gone: 'stock_base_tenstrip10' False, '--frames 124' False
diff vs backup: exactly 2 lines changed (the 1e and 1f replacements), nothing else in the 4,969 B file
```

fix_plan item 4 is now `[x]` with that evidence written into the line (backup `fix_plan.md.bak-20261029-item4-tick`);
item 3's checkbox is left exactly as Max wrote it.

## Youth guard unchanged
No edit to `scripts/comm.py`, `guard_ok`, `prompt_strings` or the tests. Proof runs, CPU only, both before the
PROMPT.md edit and again after it: `python -m pytest -q scripts/tests/test_p6_review.py scripts/tests/test_guard_scope.py`
-> **26 passed in 3.84 s**, then **26 passed in 3.23 s**.
The `comm.py` diff in `git status` is pre-existing (2026-10-28 beta7 UNET + shift 12, backup
`comm.py.bak-20261028-1330-b7default`), not from this pass, and it agrees with B2's graph.

## Not touched / left for Max
- Item 4's checkbox: ticked by Pi at 08:24 CT on Derek's explicit "tick item 4 if done" (the earlier convention is
  Max ticking after re-checking evidence, so the evidence is written inline in the line). Item 3 stays as Max left it.
- The rest of `h3-hc-render/SKILL.md` section 2/3 (3-ref wiring, 1344x768 batch canvas) predates B2 and
  contradicts it; I only moved the base-graph pointer and flagged the rest in-line.
- Any GPU comparison of B2 vs anything: no render was requested and none happened.
