#!/bin/bash
# Blind Gemma 4 26B A4B Heretic Q8_0 vs Q4_K_M Render writing test on the EVO-X3 (Max Architect 2026-11-15,
# Derrick t1737s6381 "Yes, add the temp Q4 slot and run the blind test"; t1739u-t1741u run it in Render's setup on the X3).
# Each arm: Render pi chat (render-pi.sh) on that model + the writer pipeline on the same model, identical sampling
# (writer_pipeline config arm A, pi samplingParams), identical pristine pipeline state, dry run only, never queued.
set -uo pipefail
B=$HOME/AI/render/x3/bakeoff/heretic-q8-vs-q4-20261115
RUNS=$HOME/AI/community/runs/heretic_blind_20261115
POOL=$HOME/AI/render/stills/approved_characters/POOL/flow_more_2026-10-19
SRC=$HOME/AI/community/runs/u6_gemma_heretic_20261113/gemma_pmfix6
export PATH=$HOME/AI/render/x3/.venv/bin:$HOME/.local/bin:$PATH
asks=("she has sex with him|missionary|POOL_F034.jpg|u6_01_missionary"
      "she has sex with him|doggy|POOL_F053.jpg|u6_02_doggy"
      "she gives him a blowjob|blowjob|POOL_F058.jpg|u6_03_blowjob")
warm() { python3 - "$1" <<'PY'
import sys; sys.path.insert(0, "/home/evo/AI/community/scripts/parody"); import wp_llm
c = wp_llm.Client({"endpoint": "http://127.0.0.1:8080/v1", "model_alias": sys.argv[1], "timeout_s": 900, "retry_backoff_s": [10, 30]})
c.chat([{"role": "user", "content": "Say ok."}], {"temperature": 1.0}, 1, 8, purpose="warm"); print("warm", sys.argv[1])
PY
}
for arm in q8 q4km; do
  [ $arm = q8 ] && model=gemma4-heretic || model=gemma4-heretic-q4km
  warm $model
  for i in 1 2 3; do
    IFS='|' read -r ask pos still srcrun <<<"${asks[$((i-1))]}"
    rd=$RUNS/${arm}_ask$i; mkdir -p "$rd"
    python3 -c "import json,sys; d=json.load(open(sys.argv[1])); d['source']=sys.argv[2]; json.dump(d,open(sys.argv[3],'w'),indent=1)" \
      "$SRC/$srcrun/still_read.json" "$POOL/$still" "$rd/still_read.json"
    msg="Dry run only, never queue. Ask: \"$ask\". Position: $pos. Character FCSydny. Start still: $POOL/$still. A still read already exists at $rd/still_read.json, so reuse it with --still-read (do not re-read the image). Use run folder $rd. Report the READY/NOT_READY line and the prompt.txt path."
    t0=$(date +%s.%N)
    RENDER_MODEL=x3-local/$model WP_HOME=$B/wp_$arm timeout 1500 bash $HOME/AI/render/x3/render-pi.sh -p --no-session --mode json "$msg" > "$rd/_pi.jsonl" 2> "$rd/_pi.err"
    rc=$?; t1=$(date +%s.%N)
    printf '%s\t%s\t%s\t%.1f\n' "$arm" "ask$i" "$rc" "$(echo "$t1 - $t0" | bc)" | tee -a $B/timing_raw.tsv
  done
done
echo DONE
