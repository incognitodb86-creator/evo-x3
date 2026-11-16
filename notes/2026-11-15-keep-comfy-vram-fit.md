# keep-comfy-part1 - VRAM fit: Gemma 4 26B + ComfyUI on the 16 GB card (2026-11-15)

Measurements only, no changes made to llama-swap.yaml or any model settings. The flag work is in
`scripts/run_queue.py` (`--keep-comfy-process`) and `scripts/queue/chain_queue.py`; this note records
what the card can actually hold, because item 4 decides whether part 2 (keeping a writer LLM loaded
between chained calls) is worth building.

## The two live numbers on this box (RTX 5070 Ti, 16303 MiB total)

| side | measured footprint | source |
|---|---|---|
| ComfyUI video render (H3 768x1344, the chain's job) | peaks ~15.4 GB of 16.3 GB -> about **0.9 GB free** at the end of a clip | `notes/ali147-summary-20261022.txt:28` (`COMFY ready ... vram_free=0.9GiB`, same H3 pack); the 15.4 GB peak is the value recorded for this job in the brief and the v2 run |
| Gemma writer, as served today by llama-swap `gemma4_heretic_poly` (PolyStrata/strata-poly) | Q4_K_M GGUF **15.71 GB** on disk (`C:\Users\derek\maxdrop\polystrata-gguf-gemma4-heretic-q4\gemma-4-26b-a4b-it-heretic-nohurry.q4_k_m.gguf`), mmproj bf16 **1.11 GB**. The engine's own startup log for this config: expert cache 7.44 GiB of VRAM + KV resident 32768 cells, then **"749 MiB of VRAM free with everything loaded"** | `/home/derekboone/AI/PolyStrata/strata-gemma4-heretic-poly.json`; `notes/2026-10-29-capa-context-overflow.md:139-143` (the same engine, 32k KV streaming; the 749 MiB line is with everything loaded) |

The MoE weights are not all resident: strata keeps a bounded expert cache in VRAM and puts the expert
arena in RAM (that note: "the expert arena needs 46.84 GiB of RAM"), which is why a 15.71 GB GGUF
plus 7.44 GiB of cache fits an idle card at all. Even so the free margin is **0.7 GB**, not 0.6: the
same note carries the standing warning `only 749 MiB of VRAM free at the start of this request (below
1024 MiB)`.

## Answer to item 4

**No - Gemma and ComfyUI video rendering do not fit at the same time on this card, and they are not
supposed to.** The two measured numbers are ~15.4 GB (render) + ~15.0-15.7 GB of GPU-side model state
(writer), against 16.3 GB. A live H3 render leaves about 0.9 GB free; the writer needs at least
7.4 GiB of VRAM for its expert cache alone. That is a 2x oversubscription, not a squeeze, and there
is no quant/KV setting that closes it: even a hypothetical 4-bit-resident writer would need ~8 GB.

What `--keep-comfy-process` therefore buys, and what it must not be sold as:

- it removes the **process** churn (ComfyUI start, CUDA cache warm, node import) for a chained
  writer->render sequence - the keep-alive ping (`GET /comfyui/system_stats`, llama-swap
  `upstream.ignorePaths`) resets the comfyui_auto ttl without waking a stopped process;
- it does **not** mean both models sit on the GPU together. Between a writer call and a render, the
  GPU-side model state of one side is unloaded/evicted by llama-swap (ttl) and ComfyUI's own
  unloading; the queue's `comm.free_comfy` (`POST /api/free`, `unload_models: true, free_memory:
  true`) stays unconditional in this patch precisely so the hand-off to a render always gets its VRAM.

Part 2 (keeping the writer loaded between chained calls) is therefore about **writer-side** latency
only, and it fits only in the gaps where nothing renders - which is what chain_queue.py's ping loop
assumes. Any design that keeps both loaded *during* a render needs a card change, not a config
change; the numbers above are the evidence for that.

## Safe settings to carry into part 2 (no changes made)

- Keep `comfyui_auto` ttl 300 s and ping every 60 s (chain_queue.py `PING_SEC = 60`): 5 pings inside
  a ttl window, so a writer gap of up to ~4 minutes costs no wake (~40 s).
- The chain's gaps are the only windows where a writer may stay resident: 12.9 s of prompt build per
  clip and the gpt2v LLM call per clip (the v2 run measured 35.6 s/clip end-to-end), with no render
  running.
- `--kv-resident 32768` is the current, working setting for the writer; do not raise it while a video
  pack has to load on the same card. The 1024 MiB free-VRAM warning in the note is the tripwire: if
  a chain starts logging it, the writer's KV is too big for the window, not ComfyUI's fault.
