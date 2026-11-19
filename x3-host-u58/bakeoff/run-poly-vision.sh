#!/bin/bash
set -e
export SDK=$HOME/rocm/install
export ROCM_PATH=$SDK HIP_PATH=$SDK HIP_PLATFORM=amd
export PATH=$SDK/bin:$SDK/lib/llvm/bin:$PATH
export LD_LIBRARY_PATH=$SDK/lib:$SDK/lib/rocm_sysdeps/lib:$SDK/lib/llvm/lib:${LD_LIBRARY_PATH:-}
cd ~/evo-x3/bakeoff
# ensure no leftover poly
pkill -f "strata-gemma4-heretic-q4km" 2>/dev/null || true
pkill -f "engine-poly/strata-poly" 2>/dev/null || true
sleep 2
./run_vision_arm.sh u20-heretic-q4km-polystrata-vision 8093 gemma-4-26b-a4b-ud-q4_k_m 900 -- /srv/bakeoff/src/PolyStrata/.venv/bin/python /srv/bakeoff/src/PolyStrata/serve/server.py --engine strata --config /srv/bakeoff/src/PolyStrata/strata-gemma4-heretic-q4km-vision.json --port 8093
pkill -f "strata-gemma4-heretic-q4km-vision.json" 2>/dev/null || true
sleep 5
pkill -9 -f "engine-poly/strata-poly" 2>/dev/null || true
pkill -9 -f "engine-poly/strata-vision" 2>/dev/null || true
echo POLY_VISION_DONE
