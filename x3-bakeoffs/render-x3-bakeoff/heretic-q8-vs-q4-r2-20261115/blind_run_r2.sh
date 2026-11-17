#!/bin/bash
# Blind Heretic Q8_0 vs Q4_K_M rerun r2 on the EVO-X3 (Max Architect 2026-11-15, Derrick ~3:36 PM CT
# "Yes, make the fixes and rerun the Q8 vs Q4 test"). Real Render pi chats (render-pi.sh: thinking medium, vision),
# each run does its own still read with the read tool; plus one control per ask sharing AlienPc's production read.
# Fixed seeds: the pipeline seeds from the run folder name, and both arms use the same leaf names.
# WP_HOME reset to pristine before every chat. Dry run only, never queued.
set -uo pipefail
B=$HOME/AI/render/x3/bakeoff/heretic-q8-vs-q4-r2-20261115
R1=$HOME/AI/render/x3/bakeoff/heretic-q8-vs-q4-20261115
RUNS=$HOME/AI/community/runs/heretic_blind_r2_20261115
POOL=$HOME/AI/render/stills/approved_characters/POOL/flow_more_2026-10-19
SRC=$HOME/AI/community/runs/u6_gemma_heretic_20261113/gemma_pmfix6
export PATH=$HOME/AI/render/x3/.venv/bin:$HOME/.local/bin:$PATH
mkdir -p $B $RUNS
asks=("she has sex with him|missionary|POOL_F034.jpg|u6_01_missionary"
      "she has sex with him|doggy|POOL_F053.jpg|u6_02_doggy"
      "she gives him a blowjob|blowjob|POOL_F058.jpg|u6_03_blowjob"
      "she rides him with her dress kept on, just hiked up to her waist|cowgirl|POOL_F034.jpg|u6_01_missionary")
warm() { python3 - "$1" <<'PY'
import sys; sys.path.insert(0, "/home/evo/AI/community/scripts/parody"); import wp_llm
c = wp_llm.Client({"endpoint": "http://127.0.0.1:8080/v1", "model_alias": sys.argv[1], "timeout_s": 900, "retry_backoff_s": [10, 30]})
c.chat([{"role": "user", "content": "Say ok."}], {"temperature": 1.0}, 1, 8, purpose="warm"); print("warm", sys.argv[1])
PY
}
for arm in q8 q4km; do
  [ $arm = q8 ] && model=gemma4-heretic || model=gemma4-heretic-q4km
  rm -rf $B/wp_$arm.pristine; cp -a $R1/_pristine/render/writer_pipeline $B/wp_$arm.pristine
  cp $HOME/AI/render/writer_pipeline/config.yaml $B/wp_$arm.pristine/config.yaml   # X3 config (endpoint :8080, Linux paths)
  sed -i "s/^model_alias: gemma4-heretic /model_alias: $model /" $B/wp_$arm.pristine/config.yaml
  grep -q "^model_alias: $model " $B/wp_$arm.pristine/config.yaml || { echo "alias edit failed $arm"; exit 2; }
  warm $model
  for i in 1 2 3 4; do
    IFS='|' read -r ask pos still srcrun <<<"${asks[$((i-1))]}"
    for k in 1 2 3 ctrl; do
      name=ask${i}_run$k; [ $k = ctrl ] && name=ask${i}_ctrl
      rd=$RUNS/$arm/$name; mkdir -p "$rd"
      rm -rf $B/wp_$arm; cp -a $B/wp_$arm.pristine $B/wp_$arm
      if [ $k = ctrl ]; then
        sr=$RUNS/$arm/_shared_read_ask$i.json
        python3 -c "import json,sys; d=json.load(open(sys.argv[1])); d['source']=sys.argv[2]; d['shared_from']=sys.argv[1]; json.dump(d,open(sys.argv[3],'w'),indent=1)" \
          "$SRC/$srcrun/still_read.json" "$POOL/$still" "$sr"
        msg="Dry run only, never queue. Ask: \"$ask\". Position: $pos. Character FCSydny. Start still: $POOL/$still. A still read for this exact still already exists at $sr: do not re-read the image; run the PIPELINE command with --still '$POOL/$still' and --still-read '$sr'. Use run folder $rd (absolute path). Report the READY/NOT_READY line and the prompt.txt path."
      else
        msg="Dry run only, never queue. Ask: \"$ask\". Position: $pos. Character FCSydny. Start still: $POOL/$still. Follow your STEPS: look at that still with the read tool, write still_read.json in the run folder (source = that still path), then run the PIPELINE command with --still '$POOL/$still'. Use run folder $rd (absolute path). Report the READY/NOT_READY line and the prompt.txt path."
      fi
      t0=$(date +%s.%N)
      RENDER_MODEL=x3-local/$model WP_HOME=$B/wp_$arm timeout 1800 bash $HOME/AI/render/x3/render-pi.sh -p --no-session --mode json "$msg" > "$rd/_pi.jsonl" 2> "$rd/_pi.err"
      rc=$?; t1=$(date +%s.%N)
      cp -a $B/wp_$arm/logs "$rd/_wp_logs" 2>/dev/null
      printf '%s\t%s\t%s\t%.1f\t%s\n' "$arm" "$name" "$rc" "$(echo "$t1 - $t0" | bc)" "$(date +%H:%M:%S)" | tee -a $B/timing_raw.tsv
    done
  done
done
echo DONE
