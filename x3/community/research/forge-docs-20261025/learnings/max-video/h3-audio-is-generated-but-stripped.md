---
title: H3 already generates audio; our harness discarded it
tags: [max, audio]
date: 2026-10-09
---
- The sampler denoises a joint audio+video latent every run. Add VAEDecodeAudio (fp32 audio VAE) into CreateVideo/VHS audio to keep it; cost is decode+mux seconds.
- Fair audio on/off control = one render saved twice (muted and with sound). Deleting the soundscape text changes the picture too.
- 8-step turbo audio is weakest (speech usable from ~12 steps). Describe physical sounds ("soft wet sliding", "light water slaps"), never act labels or "no speech" (no negative branch in H3).
- Prompt lip sync: <d>[English] line</d> with voice descriptors outside the tag, lips close after; exact lip sync needs TTS + audio-latent lock node (install needs GO).
- Source: /workspace/cos/research/2026-10-09-h3-prompt-improve-and-audio.md
