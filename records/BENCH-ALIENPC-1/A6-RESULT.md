# A6 speed flags — SKIPPED 2026-11-19

A4 / R1 (`records/BENCH-ALIENPC-1/A4-RESULT.md`) already recommended **not** to try:

- **R3** `--disable-fast-disk`: only if a start log shows `fast_disk=True`. That line was not found.
- **R4** CUDA sysmem-fallback policy: no HostBuffer / OOM evidence in the A4 logs.

**R2** is a >5 GB model download. The brief says skip downloads over 5 GB, and the plan says R2 only if Derrick wants that download.

R6 (`--fast fp16_accumulation`) was already tested earlier this evening and left production unchanged (quality not a same-seed tie; no speed win). Production argv remains `--use-ck-attention --disable-pinned-memory --reserve-vram 1.5`. No flag was applied in this pass.
