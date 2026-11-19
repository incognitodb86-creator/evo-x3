#!/bin/bash
set -euo pipefail
D=/home/derekboone/evo-x3/bench/2026-11-15-u21
QWEN_TOK=/srv/models/flash-next-halogen/tokenizer/tokenizer.json
GEMMA_TOK=unsloth/gemma-4-26B-A4B-it

echo "=== [1/3] flash-next-gufo (keep already-captured u12_cold_ttft_flash-next-gufo.json) ==="
$D/with_key.sh python3 -u $D/run_step3a_slot.py --slot flash-next-gufo --tokenizer "$QWEN_TOK" --depths 0 32768 131072 --runs 3 --skip-u12

echo "=== [2/3] gemma4-heretic ==="
$D/with_key.sh python3 -u $D/run_step3a_slot.py --slot gemma4-heretic --tokenizer "$GEMMA_TOK" --depths 0 32768 131072 --runs 3

echo "=== [3/3] qwen27b ==="
$D/with_key.sh python3 -u $D/run_step3a_slot.py --slot qwen27b --tokenizer "$QWEN_TOK" --depths 0 32768 131072 --runs 3

echo "=== [3b] qwen27b Q8 DFlash2 U6 18k fixture ==="
$D/with_key.sh python3 -u $D/run_u6_qwen27b_q8_pair.py

echo "STEP3A_REMAINING_DONE"
