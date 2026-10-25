---
title: H3 reference images need real pixels; tiny crops starve the face
tags: [unreviewed, max, face-lock]
date: 2026-10-10
---
- H3 uses one token per 32x32 pixels. The 2026-10-09 two-ref crops (244x192, 262x172) gave each face only about 40-50 tokens, which probably explains much of the weak second face.
- Resize references to about 1280 px on the long edge, and use ref_image_size `max` for large start images (the pool image goes from about 1,030 to about 4,130 tokens).
- There is no general face-lock LoRA for H3 (2026-10-10 research). Identity tools for other models (PuLID, InstantID, Stand-In, Phantom and others) don't load on H3.
- Source: /workspace/cos/research/2026-10-10-face-lock-lora-and-methods.md
