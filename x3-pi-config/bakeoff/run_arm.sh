#!/bin/bash
# run_arm.sh ARM PORT MODEL TASKS HEALTH_TIMEOUT -- command...
ARM=$1; PORT=$2; MODEL=$3; TASKS=$4; HT=$5; shift 6
D=~/evo-x3/bakeoff/results; mkdir -p $D
echo "=== $ARM start $(date "+%F %T %Z")" | tee $D/$ARM.meta
echo "CMD: $*" >> $D/$ARM.meta
T0=$(date +%s)
"$@" > $D/$ARM.engine.log 2>&1 &
PID=$!
up=0
for i in $(seq 1 $HT); do
  if ! kill -0 $PID 2>/dev/null; then echo "ENGINE EXITED during load" | tee -a $D/$ARM.meta; break; fi
  c=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:$PORT${HEALTH_PATH:-/health}); [ "$c" = 200 ] && { up=1; break; }
  sleep 1
done
echo "LOAD_S $(( $(date +%s) - T0 )) up=$up" | tee -a $D/$ARM.meta
if [ $up = 1 ]; then
  timeout 2400 python3 ~/evo-x3/bakeoff/bench/bench.py --base http://127.0.0.1:$PORT --model "$MODEL" --arm $ARM --tasks $TASKS --out $D/$ARM.json ${BENCH_ARGS:-} 2>&1 | tee -a $D/$ARM.meta
fi
free -g | head -2 >> $D/$ARM.meta
echo "=== $ARM end $(date "+%F %T %Z")" | tee -a $D/$ARM.meta
