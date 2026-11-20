# Opus brief: open problems and fixes (Nov 20, 2026, 1:35 PM CT)

Written by Max Architect for Derrick. Opus does file-only work on mono (records/uplan/PLAN.md). Live changes on the X3 or AlienPc go back through Max/Forge.
Hard rules: no keys, tokens or passwords; never write RefMod/LoRA trigger words or adult prompt prose into the repo; never read the PixlStash library.

Branches: `mono` at c6ae510a (live X3 + AlienPc snapshot, 1:24 PM CT); `pi/rea-parody` at 4b2d142 (REA C1-C8 + test fixes; 700 passed, 1 skipped on the X3).

## 1. Hermes chats can't show today's images or videos (top priority)
- Problem: the h3-render skill never says where outputs live, how to fetch them, or how to show them. Derrick could not see today's stills from Hermes.
- Known facts: Hermes WebUI renders a `MEDIA:/absolute/path` line inline via `/api/media?path=...` (WebUI changelog). The skill already mentions copying stills into `/home/evo/.hermes/image_cache/` and replying with `MEDIA:`. AlienPc ComfyUI is reachable from the X3 at `https://alienpc.tailf242b2.ts.net:8446` (`/history`, `/view?filename=&subfolder=&type=output`).
- Fix: add a short section to h3-render SKILL.md (default profile; mirror to code and writertest copies) for listing today's images and videos (ComfyUI /history and X3 folders, /mnt/qnap/renders/runs), fetching them to image_cache, and posting with MEDIA:. Videos must play too (mp4/webm). Snapshot copy is under the X3 live snapshot in mono.

## 1b. Give Render (and all Hermes chats) gallery access (Derrick t3105u)
- Problem: Render can't browse what has been made. Galleries already exist on the tailnet: AlienPc gallery (Infinite Image Browsing) at `https://alienpc.tailf242b2.ts.net:8444/`, which shows ComfyUI's output folders; the X3 serves `https://evo-x3-1.tailf242b2.ts.net:8443/renders/` (from /mnt/qnap/renders/runs), and X3 `:8444` proxies 127.0.0.1:7878 (confirm what that app is).
- Fix: document these in h3-render SKILL.md so Render can list and search outputs through each gallery's HTTP API (IIB has a file-listing API; confirm from its docs), fetch a file into image_cache, and show it with `MEDIA:`. Read-only use, tailnet only, with no new ports or auth changes. Consider also giving the X3 a matching gallery over its own render outputs so both machines look the same (standing rule: same save locations on both).

## 2. X3 can't reach AlienPc files (no SSH server on AlienPc)
- State: the X3 side is done (user evo key `~/.ssh/alienpc_ed25519`, Host `alienpc` in `~evo/.ssh/config`). The AlienPc installer is staged at `C:\Users\derek\AppData\Local\Temp\openssh-setup-20261120\enable-openssh-tailscale.ps1`. It is key-only, Tailscale-only (100.64.0.0/10) and needs one UAC click on the AlienPc console, which timed out. Derrick is away.
- Fix after install: update the h3-render stop-if-missing line so it tries `ssh alienpc` once for `C:\` paths before stopping. Review the staged script for correctness.

## 3. Render chat looped on Windows paths
- Problem: it searched the X3 for `C:\...` paths for about 9 minutes, then hit "Gateway run failed". A stop-if-missing line was added to the default h3-render skill (sha256 6f5ba4d7...). Only the default profile was edited; the code and writertest copies were not.
- Fix: mirror the line, then revise it per item 2.

## 4. M6 Flux likeness setup (Sydney/Megan celeb RefMod + LoRA, L7 Miraclein FP8 hybrid)
Audit (read-only, partly unverified):
- The prompts don't include the LoRA trigger, the celeb's name or a likeness description. Sydney and Megan prompts are identical. L0, L0-t2i and L5 also lack the reference-image anchor wording.
- L7 RefMod strength is 0.85; the author's high-fidelity setting is 1.0 (retention 1.0 is already right).
- No `ConditioningZeroOut` on the negative path, unlike the official workflow.
- UNVERIFIED and questioned by Derrick: "RefMods built from 21 images / 5,376 tokens vs a 1,024 sweet spot". Check from the RefMod metadata who built them and with how many images. Also prove they are Flux 2 Klein image RefMods and not H3 video RefMods.
- PuLID-Flux2 is installed on AlienPc but disabled. The `fk9_*_v1` Klein-9B LoRAs are unused.
- The render chat's queued L7 stills used the unfixed graph.
- Fix: new L7 prompt templates (trigger + name + short likeness text + anchor, kept out of git if they contain triggers), strength 1.0, ZeroOut. Then an A/B on AlienPc: baseline vs fixed vs fixed + rebuilt RefMod, 6 seeds, ArcFace against `C:\AI\refs_ab_celeb`, plus the photo-to-photo similarity ceiling.

## 5. M6 runner bugs: `alienpc/community/scripts/run_flux_likeness_ab.py`
- Ref filter: the refs in `C:\AI\refs_ab` are HTML files named `.png`. Check magic bytes and skip non-images; never score from refs_ab.
- `score_arcface` (~line 281) runs `json.loads(proc.stdout)`, which fails because InsightFace logs first. Parse the last JSON line. RESULT.md shows n/a because of this.
- Add intra-gallery similarity and per-ref mean/max/min to the scoring.

## 6. `flux_still.py` gaps
- It has no `--unet` flag and can't take a saved `request.api.json`, so the winning Miraclein L7 graph had to be copied by hand. Add both, smallest change.

## 7. Test hygiene in pi/rea-parody
- 4b2d142 committed 7 test-side-effect PNGs under `x3/comfy-alienpc/input/community/`. The tests write fixtures into the repo. Point them at `tmp_path`, drop the PNGs, and gitignore the folder.
- Review C1-C8 + 4b2d142 in general (plan: `records/REA-PARODY-PIPELINE/PIJOB-TASKS.md`, result: `RESULT-CODING.md`).

## 8. Images don't land in one place
- Per Derrick's rule, only the final RTX-upscaled videos go to the QNAP/PixlStash. Stills and test outputs stay in each machine's ComfyUI or run folders. Derrick hasn't decided whether all new images should also copy to one shared folder. Don't implement this without his yes.

## Still queued (live, not Opus)
- 3-slot Flash-Next test at 131K on the X3 (Derrick picked it), with rollback to 2 slots.
- R1-R4 Render test on Derrick's go.
