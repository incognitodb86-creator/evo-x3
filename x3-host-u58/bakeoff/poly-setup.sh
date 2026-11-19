#!/bin/bash
cd ~/evo-x3/bakeoff
while ! grep -q BATCH2_DONE batch2.log; do sleep 5; done
./setup-strata.sh --family gemma4 --gguf-dir /srv/bakeoff/heretic-q8 --models-dir /srv/bakeoff/polystrata-data --context 32768 --vision no --port 8092 --yes --no-start
echo POLY_SETUP_Q8_DONE
