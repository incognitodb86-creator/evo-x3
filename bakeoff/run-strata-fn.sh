#!/bin/bash
set -e
echo "STRATA_FN_SHA_START $(date)"
cd /srv/bakeoff/fn-q4kxl-strata
if sha256sum -c SHA256SUMS.expected; then
  echo "STRATA_FN_SHA_OK $(date)"
else
  echo "STRATA_FN_SHA_FAIL $(date)"
  exit 1
fi
cd ~/evo-x3/bakeoff
echo "STRATA_FN_SETUP_START $(date)"
./setup-strata.sh --family unsloth --model UD-Q4_K_XL --gguf-dir /srv/bakeoff/fn-q4kxl-strata --models-dir /srv/bakeoff/polystrata-data --context 32768 --vision no --port 8090 --yes --no-start --setup
echo "STRATA_FN_SETUP_END $(date) exit $?"
# find the config it wrote
ls -la /srv/bakeoff/src/PolyStrata/strata-*.json /srv/bakeoff/src/PolyStrata/run-*.sh
# run the arm using whatever config matches unsloth/q4kxl
CFG=$(ls /srv/bakeoff/src/PolyStrata/strata-*q4_k_xl*.json /srv/bakeoff/src/PolyStrata/strata-*unsloth*.json /srv/bakeoff/src/PolyStrata/strata-qwen*.json 2>/dev/null | head -1)
echo "CFG=$CFG"
if [ -z "$CFG" ]; then
  echo "NO_CONFIG"; ls /srv/bakeoff/src/PolyStrata/strata-*.json; exit 1
fi
export SDK=$HOME/rocm/install
export ROCM_PATH=$SDK HIP_PATH=$SDK HIP_PLATFORM=amd
export PATH=$SDK/bin:$SDK/lib/llvm/bin:$PATH
export LD_LIBRARY_PATH=$SDK/lib:$SDK/lib/rocm_sysdeps/lib:$SDK/lib/llvm/lib:${LD_LIBRARY_PATH:-}
# model name from config
MODEL=$(python3 -c "import json; print(json.load(open('$CFG')).get('model_name','qwen3.8-flash-next'))")
echo "MODEL=$MODEL"
pkill -f "serve/server.py --engine strata" 2>/dev/null || true
sleep 2
./run_arm.sh u6-strata-fn-q4kxl 8090 "$MODEL" long,code,tool,decode 900 -- /srv/bakeoff/src/PolyStrata/.venv/bin/python /srv/bakeoff/src/PolyStrata/serve/server.py --engine strata --config "$CFG" --port 8090
pkill -f "serve/server.py --engine strata" 2>/dev/null || true
sleep 5
pkill -9 -f "engine/strata|engine-poly/strata" 2>/dev/null || true
echo STRATA_FN_ARM_DONE $(date)
