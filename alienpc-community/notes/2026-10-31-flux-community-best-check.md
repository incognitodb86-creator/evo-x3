# FLUX community-best check (Forge, 2026-10-31 21:3x CT)

research-core used: yes · Question: what does the community/maintainer say today about the S2
two-pass FLUX stills workflow (Klein 9B-KV body pass + BFS head swap on the community NSFW 9B)
and about multi-reference / storyboard consistency, and what changed in the last day ·
window: published >= 2026-08-01 (model cards accepted at any date if the maintainer's current page) ·
tier: STANDARD (14 calls, under 20) · accessed 2026-10-31 CT

TLDR (hedged): the S2 components are what the community uses, and S2's two-pass order already
follows the BFS card's "keep the head edit and the scene change apart" rule. Four S2 settings sit
below the card values we can verify today (LoRA strength, prompt wording, head-reference input,
pass-2 sampler/steps) - a small 8-cell calibration is the cheapest way to close that gap.
dx8152 Consistency V2 is the right tool for Phase 6 and its file is only 331 MB, not the 3.6 GB the
plan quotes for all three Phase 6 LoRAs (real total 577 MB). One real change from the last two
weeks: FLUX 3 Image Klein (open 5.6B, released 2026-10-17, multi-reference editing) is the current
open-weight model; it belongs in Phase 8's candidate list next to Qwen-Image-Edit-2511 + BFS v5.

## Evidence table

| claim | source (publisher) | URL | published | accessed CT | class | quote (<=25w) | status | hedge |
|---|---|---|---|---|---|---|---|---|
| BFS Klein head-swap input contract: image 1 = target body, image 2 = reference face/head, "Do not reverse" | Alissonerdx (maintainer) | https://huggingface.co/Alissonerdx/BFS-Best-Face-Swap/blob/main/docs/flux-2-klein.md | doc commit "about 1 month ago" (~2026-09-27) | 2026-10-31 21:05 | primary | "Do not reverse the images for these releases." | SUPPORTED | hard |
| Current BFS head-swap prompt adds a body/pose/background preservation clause | same | same | same | same | primary | "Keep the body, clothing, pose, framing, and background intact." | SUPPORTED | hard |
| BFS card starting LoRA strength for Klein = 1.0 (S2 runs 0.5) | same | same | same | same | primary | "Start around LoRA strength `1.0`; adjust after checking identity preservation" | SUPPORTED | hard |
| BFS card: do not ask for an unrelated scene change in the head-swap prompt (S2 splits pose-change pass 1 / head-swap pass 2 = matches) | same | same | same | same | primary | "avoid requesting an unrelated scene change in the same prompt" | SUPPORTED | hard |
| The exact weight S2 uses is a current BFS release; a `step3500_rank128` and a 4B v1.1 optional also exist | same | same | same | same | primary | "bfs_head_v1_flux-klein_9b_step3750_rank64.safetensors" | SUPPORTED | hard |
| Klein 9B-KV is 4-step step-distilled and caches reference KV for multi-reference editing (up to 2.5x faster) | Black Forest Labs | https://huggingface.co/black-forest-labs/FLUX.2-klein-9b-kv-fp8 | model card (family, 2026) | 2026-10-31 21:05 | primary | "step-distilled to 4 inference steps"; "speeding up inference by up to 2.5 times for multi-reference" | SUPPORTED | hard |
| C3 model on this box = the community NSFW 9B the plan names, sha matches | local file metadata | `C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\models\unet\FLUX-KLEIN-9B-FP8-NSFW.metadata.json` | 2026-06-01 (file) | 2026-10-31 21:25 | primary (local) | `"sha256": "39e16031c2bed5...aa5b3d3b"` | SUPPORTED | hard |
| The same author's card for the community NSFW 9B build: 8-12 Euler/Simple steps beat 4 for anatomy | Civitai card via CivArchive mirror (author quote) | https://civarchive.com/models/2625738?modelVersionId=2948023 | model card (v1.0) | 2026-10-31 21:10 | community/primary-mirror (aggregator page quoting the author) | "8-12 Steps of Euler/Simple seems to be good... you can get lucky with 4 steps" | PARTIAL | soft: mirror page, not the Civitai page; the Oct 28 plan quotes the same sentence |
| dx8152 Consistency LoRA is the maintained Klein consistency tool ("without any cue words") | dx8152 (maintainer) | https://huggingface.co/dx8152/Flux2-Klein-9B-Consistency/blob/main/README.md | README current (page updated; V2 text 2026-04-17 per Oct 30 pass) | 2026-10-31 21:05 | primary | "LoRA can significantly improve Klein consistency without any cue words." | SUPPORTED (this sentence); the "strength 1.0-1.4 / V2 color-cast" wording = NOT CHECKED THIS SESSION (not on the README today; it came from the Oct 30 pass) | soft |
| RefGrid = stitch up to 4 refs into a 2x2 grid (core ImageStitch rebuild, no new node) | xb1n0ry / yash2code repos + myaiforce how-to | https://github.com/xb1n0ry/ComfyUI-KleinRefGrid ; https://myaiforce.com/improve-multi-reference-image-results-flux-2-klein/ | 2026 (undated pages) | 2026-10-31 21:05 | secondary/community | "Improve multi-reference image results in Flux.2 Klein... with Flux Klein Ref Grid or Image Stitch" | SUPPORTED (exists, method) | soft; sizes/steps not verified this session |
| FLUX 3 Image Klein: open 5.6B image model, released 2026-10-17, generation + editing, multi-reference | Black Forest Labs blog + HF (Oct 17) + VentureBeat | https://bfl.ai/blog/flux-3-image-klein ; https://huggingface.co/black-forest-labs/flux-3-image-klein ; https://venturebeat.com/technology/black-forest-labs-opens-flux-3-image-klein-weights-with-free-commercial-use-limited-to-smaller-businesses | 2026-10-16/17 | 2026-10-31 21:10 | primary (blog/HF) + secondary (news) | "open 5.6B image model released in October 2026" (fal summary of the card) | SUPPORTED (exists, open weights, 5.6B, Oct 2026) | hard on existence; SPECULATIVE for our box (no local test) |
| FLUX 3 Image Klein is a different model family; FLUX.2 Klein LoRAs do not carry over | fal.ai guide (cites both model cards) | https://fal.ai/learn/devs/how-to-fine-tune-flux-with-the-api | 2026-10 (page "20 hours ago" at search) | 2026-10-31 21:12 | secondary (aggregator citing primary) | "FLUX.2 [klein] is the earlier 4B and 9B family... their LoRAs are not interchangeable." | SUPPORTED | soft: fal is a vendor page; the model cards are the primary |
| BFL self-eval: FLUX 3 Image Klein ranks first among open weights, +91 Elo over FLUX.2 [klein] 9B in T2I | fal quoting BFL; BFL blog is the primary | https://fal.ai/learn/devs/how-to-fine-tune-flux-with-the-api (refs 4/7 -> bfl.ai/blog/flux-3-image-klein) | 2026-10 | 2026-10-31 21:12 | aggregator (needs the BFL blog to be a cite) | "91 Elo over FLUX.2 [klein] 9B in text-to-image" | PARTIAL | soft: I did not open the BFL blog; treat the number as unverified locally |
| BFS supports Krea 2 + Qwen Image 2.1/2509/2511 + LTX-2 experiments (each release has its own base, input order, prompt) | Alissonerdx (maintainer) | https://huggingface.co/Alissonerdx/BFS-Best-Face-Swap (README, commit 2026-08-10) | 2026-08-10 | 2026-10-31 21:08 | primary | "Each release has its own base-model, input-order, prompt, and workflow" | SUPPORTED | hard |

Conflicts: none between sources on the four S2 deltas.
Not checked this session: dx8152's "strength 1.0-1.4" and V2 color-cast wording (carried from the
Oct 30 research pass); the BFL 91-Elo number; `Comfy-Org/Flux-2-Klein-9B` encoder/VAE list; the
Oct 30 research doc's 23 sources as a whole (I re-opened only the load-bearing ones).
Searched, not found: an official BFL/ComfyUI recommended *sampler* for the Klein 9B-KV edit graph
(only "4 steps, CFG 1" is documented; `lcm` vs `euler` at 4 steps is community practice, not a
card value) -> Phase 7 T1 "official template" run is the test, no doc answer.
A published community "S2-style" two-pass (KV body + BFS head) workflow with measured numbers: none
found; S2 is our own measured arm, which is why the calibration in this plan is small.

Open questions for the next pass (not for this run): FLUX 3 Image Klein file sizes + whether an
FP8 fits our 16 GB; does BFS ship a FLUX 3 head-swap LoRA yet (README lists Krea 2, Qwen, Klein,
LTX-2 - no FLUX 3 row as of 2026-10-31); is `flux-3` compatible with our Qwen3-8B encoder files.
