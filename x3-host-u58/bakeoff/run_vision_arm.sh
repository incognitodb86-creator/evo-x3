#!/bin/bash
# run_vision_arm.sh ARM PORT MODEL HT -- command...
set -e
ARM=$1; PORT=$2; MODEL=$3; HT=$4; shift 4
[ "$1" = "--" ] && shift
D=~/evo-x3/bakeoff/results
mkdir -p $D
echo "=== $ARM start $(date '+%F %T %Z')" | tee $D/$ARM.meta
echo "CMD: $*" >> $D/$ARM.meta
T0=$(date +%s)
"$@" > $D/$ARM.engine.log 2>&1 &
PID=$!
up=0
for i in $(seq 1 $HT); do
  if ! kill -0 $PID 2>/dev/null; then echo "ENGINE EXITED during load" | tee -a $D/$ARM.meta; break; fi
  c=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:$PORT${HEALTH_PATH:-/health} || true); [ "$c" = 200 ] && { up=1; break; }
  sleep 1
done
echo "LOAD_S $(( $(date +%s) - T0 )) up=$up" | tee -a $D/$ARM.meta
if [ $up = 1 ]; then
  timeout 600 python3 ~/evo-x3/bakeoff/bench/vision_bench.py --base http://127.0.0.1:$PORT --model "$MODEL" --arm $ARM --image ~/evo-x3/bakeoff/bench/vision-test.png --out $D/$ARM.json 2>&1 | tee -a $D/$ARM.meta
fi
echo "=== $ARM end $(date '+%F %T %Z')" | tee -a $D/$ARM.meta
