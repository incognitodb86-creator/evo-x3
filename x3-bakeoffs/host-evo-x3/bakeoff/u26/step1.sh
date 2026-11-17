#!/bin/bash
# U26 step 1: official Halogen native v2 Flash-Next at full 262144 context (Derrick t1774s6524).
set -uo pipefail
cd ~/evo-x3/bakeoff
IMG=ghcr.io/peonist-ai/halogen-flash-server@sha256:3041272385d1ac88e5b842be3dbf4b99472bb079f22430c1ea3b3e0dbd1e1568
ARM=${ARM:-u26-halogen-native-262k}
R=results; GTT=$(ls /sys/class/drm/card*/device/mem_info_gtt_used | head -1)
( while true; do echo "$(date +%T) $(( $(cat $GTT)/1048576 )) $(free -m | awk '/Mem:/{print $3}')"; sleep 2; done ) > $R/$ARM.mem &
MP=$!
BENCH_ARGS="--effort low" ./run_arm.sh $ARM 8790 flash-next long,code,tool,decode 900 -- \
  sudo podman run --rm --name bake-arm -p 127.0.0.1:8790:8731 \
    --device /dev/kfd --device /dev/dri --group-add keep-groups --ipc=host --ulimit memlock=-1:-1 \
    -e HALOGEN_MODEL_ID=flash-next -e HALOGEN_CTX=262144 \
    -e HALOGEN_REASONING_EFFORT=medium -e HALOGEN_TEMPERATURE=1.0 -e HALOGEN_TOP_P=0.95 -e HALOGEN_TOP_K=20 \
    ${EXTRA_ENV:-} \
    -v ${MODELS:-/srv/bakeoff/halogen-models}:/models:ro $IMG
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8790/health | grep -q 200; then
  for c in 7 13; do python3 u26/longctx.py --base http://127.0.0.1:8790 --model flash-next --copies $c --out $R/$ARM.long$c.json 2>&1 | tee -a $R/$ARM.meta; done
  python3 u26/forge_task.py --base http://127.0.0.1:8790 --model flash-next --out $R/$ARM.forge.json 2>&1 | tee -a $R/$ARM.meta
  [ -n "${REFUSAL:-}" ] && python3 u26/refusal_key.py --base http://127.0.0.1:8790 --model flash-next --arm $ARM --out $R/$ARM-refusal.json 2>&1 | tee -a $R/$ARM.meta
  [ -n "${WRITE:-}" ] && python3 bench/bench.py --base http://127.0.0.1:8790 --model flash-next --arm $ARM-w --tasks write1,write2 --out $R/$ARM.write.json --maxtok 4000 --effort low 2>&1 | tee -a $R/$ARM.meta
  curl -s http://127.0.0.1:8790/health > $R/$ARM.health.json
fi
kill $MP
echo "PEAK_GTT_MIB $(sort -k2 -n $R/$ARM.mem | tail -1)" | tee -a $R/$ARM.meta
sudo podman stop -t 20 bake-arm >/dev/null 2>&1
echo "=== STEP1 DONE $(date +%T)" | tee -a $R/$ARM.meta
