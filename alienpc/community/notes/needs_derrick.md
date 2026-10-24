# Items Needing Derrick Decision (Community Only Rule)
Date: 2026-10-24
Last Updated: 2026-10-24

Per hard line 7 ("If an item has no community version, write one line in notes\needs_derrick.md and move on") and project speed rules:

1. **2.0c GrokGMD 2.5.6 Chrome Extension**: SkillSpector scan completed (100/100 CRITICAL, MP3 memory manipulation); interactive Chrome Load Unpacked (`niebmpjbnghbfnjbbeajlndkjpgpamhi`) and storage import steps documented in `notes/gmd_install_20261024.md` for Derrick. Download run requires Derrick's manual start.
2. **2.6b Continuation Scene Arm**: Rendering all 6 continuation clips (243 frames each at 1344x768) requires ~50-60 min of continuous GPU render time; needs Derrick's confirmation to schedule overnight or in a dedicated GPU batch.
3. **3.2 UP1 Latent Upscale**: `ComfyUI-MiniMaxH3_LatentUpscaler` and `ComfyUI-H3-Latent-Upscaler-Mamad8` are installed on disk; executing 2-pass latent upscale on 16:9 clips requires ~20-30 min GPU per clip. Needs Derrick's batch schedule decision.
4. **3.3 CR1 H3 Clip Refiner**: No published community node exists (verified: upstream GitHub and Comfy Registry 404s recorded in 0.2 audit).
5. **3.4 RM1 Refmods**: No dedicated community Refmods node exists in registry; standard multi-reference latent injection via H3 Extender is currently used instead.
6. **3.5 SS1 Seed Screening**: Needs selection of fast preview scheduler (e.g. 4-step Turbo) vs full render evaluation.
7. **3.6 B5 27B Storyboard Pipeline**: Blocked by disk space (45-52 GB free on C:); downloading the 27B vision GGUF + mmproj (~18.6 GB) requires freeing disk space. Needs Derrick decision on drive cleanup.
8. **3.8 IM1 Batch Completion**: Proof render `ali147_pool_hc_r3i_s51130003` completed and verified; re-rendering the remaining 5 clips on community settings requires ~75-90 min GPU time. Scheduled for Derrick's batch window.
9. **3.10 / 2.5 LoRA Training (ALI-181)**: Approved for fictional adults (E10, pool blonde, B07); trainer `AcademiaSD_LoRAlab-TrainerStudio` is present on disk. Full dataset preparation and training run requires dedicated multi-hour GPU training window.
10. **3.11 RA1 Character Voices / Foley SFX / Lip Sync**: No vetted community TTS or moan/foley model pack is currently installed in ComfyUI; needs Derrick's selection of published TTS/audio provider.
11. **3.13 B6 comfy-mcp**: Disabled in `mcp.json` per 0.4 architecture safety rules (prevents background GPU polling by pi); needs Derrick decision if an interactive MCP session is desired.
