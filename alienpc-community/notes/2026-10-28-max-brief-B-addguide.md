# Max brief: B re-run with the H3 two-pass Add Guide fix (2026-10-28)
ONE task. Fresh session. PowerShell tool only (bash is off).

## Goal
Re-run test B identically (same graph as B, same seed, prompt, start still TERRACE2_768x1344.png, beta7 int8HQ, steps, shift, VSA, 243 frames, per spec C:\AI\community\notes\ab_q4_q5_brief_2026-10-28.md) with ONLY the discussion #74 fix applied.
- Source graph: C:\AI\community\runs\terrace_dom_q5_20261028_s51083005\terrace_dom_q5_20261028_s51083005.api.json (copy it, edit the copy; do not build a new graph). Keep B's seed value exactly as in that JSON.
- New run folder: C:\AI\community\runs\terrace_dom_q5guide_20261028_s51083007 (same scheme; 07 = next arm id).

## The fix (source: https://huggingface.co/TenStrip/10Eros-Max/discussions/74, wittywolk's reply to LokkenJP)
1. "Reference to Video" setting: Match -> Max.
2. Add one "Add Guide For MiniMax H3" node before the FIRST Basic Guider, and one before the SECOND Basic Guider (the one after the upscale pass). Both fed the initial first-frame image (TERRACE2_768x1344.png). The discussion gives no other settings for the node: leave its other inputs at defaults.
3. Do NOT add the "<Picture 1> is the correct scene identity..." steering prompt. The thread found prompt + Add Guide together caused artifacts (character not blinking for seconds). Prompt stays byte-identical to B.

## Rules
- Adults-only youth guard (comm.guard_ok) runs before render, as always.
- Take the GPU lock via the existing gpu_window.ps1 runner. One PowerShell call per render.
- No new scripts unless a step fails. Never use bash.
- If the Add Guide node is missing, install it through the normal ComfyUI node/manager route (no card needed).

## Output
- *_raw.mp4 and a native-resolution (768x1344) crf-18 *_final.mp4 only. No RTX upscale.
- Upload both to QNAP /pi-drop/ with pi_qnap.py put, as before; verify sizes.

## Done
Write C:\AI\community\notes\2026-10-28-B-addguide-DONE.md: files, sizes, render time, exactly what changed in the graph (node ids added/edited, the Reference to Video input). Then stop and wait.

## Added 17:05: check graph vs LokkenJP first
Before rendering, compare B's graph (C:\AI\community\runs\terrace_dom_q5_20261028_s51083005\request.api.json) node by node with LokkenJP's published beta 7 two-pass workflow (find it from https://huggingface.co/TenStrip/10Eros-Max/discussions and LokkenJP's linked repo; download it, don't rebuild from memory). Pay special attention to the sigma split (SplitSigmas step), the second-pass denoise/sigmas, CFG, the upscaler node inputs, and VAE decode. Write the differences to C:\AI\community\notes\2026-10-28-B-graph-vs-lokken.md. Fix B's graph to match the published workflow; stock values only, plus the discussion #74 Add Guide change as the one deliberate difference. Then render as the brief says.
