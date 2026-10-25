# RESEARCH — Max baseline resolution quick-check — 2026-10-05

**When_CT:** 2026-10-05 ~10:17 AM CT · Access date CT same. Scope: live primary re-check only.

## TLDR
**CONFIRM** CoS. Official quality / node default = **1344×768** (768 short edge). **864×480** = template fast preview / low-VRAM community — not quality SoT. **124f is valid** (node default; `17k+5`). No newer primary contradiction.

## Facts (cited)
1. Comfy H3 tutorial: open weights **768 short edge**; full-quality 16:9 Megapixels **0.98 → 1344×768**; template ships **fast preview**; soft = resolution first; multiple **32**. https://docs.comfy.org/tutorials/video/minimax/minimax-h3
2. MiniMaxH3ReferenceToVideo defaults: width **1344**, height **768**, length **124** (trained ~124–362); W/H step **32**; length step **17**; length aligned to supported count. https://docs.comfy.org/built-in-nodes/MiniMaxH3ReferenceToVideo
3. HF MiniMax-H3: shorter side **768 by default**; H3-Base = **768p**; 2K = Regenerate-2K (not open native). https://huggingface.co/MiniMaxAI/MiniMax-H3
4. edge-dit: frames ≥22 and **`17k+5`** (…**124**…); W/H ×32; quality short edge **768**; CLI often **864×480** as runnable, not quality SoT. https://raw.githubusercontent.com/THU-MIG/edge-dit.cpp/main/docs/minimax-h3.md

## 124f
**Valid.** Node default. `17×7+5 = 124`. In trained band.

## Recommend (clock only)
START baseline at KEEP **864×480** (chase ~125s→~225s debt); then one-axis clock **1344×768** for speed-vs-quality. Do not crown preview.

## Gate 4
**no standing fact** — confirms existing SoT. LEARNED: live defaults still match this morning’s brief; 124 = exact `17k+5`.
