# DRAFT (not briefed) - Own-photo REF2VA rerun, one reference, short clip - 1 page

Status: DRAFT 2026-11-03 10:10 AM CT. Not sent to Forge: Derrick 10:09 AM CT "ok well update gitea dont brief forge".

Derrick decision(s) this comes from: "Yes, brief Forge to rerun with my photo as the only reference, TenStrip's short prompt, no her-face LoRA, a short clip" (10:04 AM CT Nov 3). Own body, no face, private renders only (card 9:58 AM CT Nov 3).

**Goal:** a ~5 s clip where his anatomy stays true to his own photo, with a fictional adult partner already in frame at frame 0.
**Done when:** the clip completes (121 frames, 24 fps, 768x1344) in a private folder outside every Infinite Image Browsing root; Derrick judges likeness by his own look (Forge makes no likeness claim); no face of him; partner is a fictional adult described in the prompt only.
**Writer inputs:** caption-fed. Forge captions its own start image with its own vision model.
**Pictures:** Picture 1 = ComfyUI input community\bj_pov_20261030\start_pov_768x1344.png (the man's lap) at original size, the only reference (no larger original found on disk by name/size; Forge's tmp_view copy is byte-identical). Same image is the open frame. No her start frame, no face crops.
**Who builds:** Forge. Max briefs; he does not build.
**Community baseline:** TenStrip / MiniMax guide: MiniMaxH3ReferenceToVideo with one reference, aspect matching output, ref_image_size max; short prompt "<Picture 1> is the correct scene identity ... fully preserved from <Picture 1>" (retention fully_preserved); no cache or spectrum nodes; no her-face LoRA; tool LoRAs only 0.2-0.6; 8stepTurbo shift 12/3, 8 steps euler/simple; single pass at output size (no 2x upscale + 0.4 denoise second pass).
**Arms:** A1 = 10Eros_Max_h3_8stepTURBO_beta7_int8HQ (current KEEP model), photo-only reference. No second arm: no beta7 fix model file is on disk (only int8HQ and activation_learned_HQ). Same seed for any rerun.
**Acceptance before GPU:** Max reads the generated prompt against the still and this plan; adults-only check once per still per standing rule; scores go to Derrick before GO.
**Stop:** one render. Fail = clip does not complete, his face appears, partner enters over many frames instead of being present at frame 0, or output lands in a shared gallery root.
