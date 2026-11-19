#!/bin/bash
cd ~/evo-x3/bakeoff
H=ghcr.io/peonist-ai/halogen-flash-server@sha256:70445bcf7acff8f1fe11396a97b866ed30dca31caf5fac62049127658080e07f
./run_arm.sh u6-halogen 8790 qwen3.8-flash-next long,code,tool,decode 1200 -- sudo podman run --rm --name bake-arm -p 127.0.0.1:8790:8731 --device /dev/kfd --device /dev/dri --group-add keep-groups --ipc=host --ulimit memlock=-1:-1 -e HALOGEN_REASONING_EFFORT=low -e HALOGEN_CTX=32768 -v /srv/bakeoff/halogen-models:/models:ro $H
sudo podman stop -t 15 bake-arm >/dev/null 2>&1; sleep 5
./setup-strata.sh --family gemma4 --model UD-Q4_K_M --gguf-dir /srv/bakeoff/heretic-q8-poly --models-dir /srv/bakeoff/polystrata-data --context 32768 --vision no --port 8092 --yes --no-start > poly-setup.log 2>&1
echo BATCH3_DONE
