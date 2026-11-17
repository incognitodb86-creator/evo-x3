#!/bin/bash
cd ~/evo-x3/bakeoff
P=/srv/bakeoff/src/PolyStrata
export STRATA_HIPBLASLT_TUNING=$P/tools/hip/gfx1151-hipblaslt-100401.txt
export HEALTH_PATH=/v1/models
./run_arm.sh u20-heretic-q8-polystrata 8092 gemma4-heretic long,decode,write1,write2,tool 900 -- $P/.venv/bin/python $P/serve/server.py --engine strata --config $P/strata-gemma4-ud-q4_k_m.json --port 8092
pkill -f "strata-gemma4-ud-q4_k_m.json"; sleep 8; pkill -9 -f engine-poly/strata-poly; sleep 3
./run_arm.sh u20-heretic-q4km-polystrata 8093 gemma4-heretic long,decode,write1,write2,tool 900 -- $P/.venv/bin/python $P/serve/server.py --engine strata --config $P/strata-gemma4-heretic-q4km.json --port 8093
pkill -f "strata-gemma4-heretic-q4km.json"; sleep 8; pkill -9 -f engine-poly/strata-poly; sleep 3
unset HEALTH_PATH
H=ghcr.io/peonist-ai/halogen-flash-server@sha256:70445bcf7acff8f1fe11396a97b866ed30dca31caf5fac62049127658080e07f
./run_arm.sh u6-halogen-gguf-q4kxl 8790 qwen3.8-flash-next long,code,tool,decode 1200 -- sudo podman run --rm --name bake-arm -p 127.0.0.1:8790:8731 --device /dev/kfd --device /dev/dri --group-add keep-groups --ipc=host --ulimit memlock=-1:-1 -e HALOGEN_REASONING_EFFORT=low -e HALOGEN_CTX=32768 -e HALOGEN_MAX_TOK=16384 -e HALOGEN_CHECKPOINT=/gguf/Qwen3.8-Flash-Next-UD-Q4_K_XL-00001-of-00004.gguf -e HALOGEN_MTP_HEAD=/models/qwen38-flash-next-mtp.hgn -e HALOGEN_TOKENIZER=/models/tokenizer -v /srv/models/flash-next:/gguf:ro -v /srv/bakeoff/halogen-models:/models:ro $H
sudo podman stop -t 15 bake-arm >/dev/null 2>&1; sleep 5
echo BATCH4_DONE
