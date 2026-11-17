#!/bin/bash
cd ~/evo-x3/bakeoff
V=docker.io/kyuz0/amd-strix-halo-toolboxes@sha256:9a9e4d8f56e7792dffca1e2906d9399ff03ef87c9e2148983c9393fcbb8d7fb6
R=docker.io/kyuz0/amd-strix-halo-toolboxes@sha256:459730d6cdfdd43b10036414be6ab3c2c0fe634a22fa764c9f5d577ddc40306c
C="--rm --name bake-arm --network=host --device=/dev/kfd --device=/dev/dri --group-add=keep-groups --security-opt seccomp=unconfined -v /srv/models:/srv/models:ro,Z -v /srv/bakeoff:/srv/bakeoff:ro,Z"
stop(){ sudo podman stop -t 10 bake-arm >/dev/null 2>&1; sleep 3; }
./run_arm.sh u6-27b-vulkan-prod 8090 qwen27b long,longdecode,decode,tool 600 -- sudo podman run $C $V llama-server --host 127.0.0.1 --port 8090 -m /srv/models/qwen27b/Qwen3.8-27B-UD-Q4_K_XL.gguf --jinja --load-mode none -fa on -ctk q8_0 -ctv q8_0 -np 2 -c 262144 --no-slots --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 --alias qwen27b; stop
./run_arm.sh u6-27b-rocm 8090 qwen27b long,longdecode,decode,tool 600 -- sudo podman run $C $R llama-server --host 127.0.0.1 --port 8090 -m /srv/models/qwen27b/Qwen3.8-27B-UD-Q4_K_XL.gguf --jinja --load-mode none -fa on -ngl 999 -b 4096 -ub 2048 -ctk q8_0 -ctv q8_0 -np 1 -c 32768 --no-slots --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 --alias qwen27b; stop
./run_arm.sh u20-heretic-q8-vulkan-prod 8090 gemma4-heretic long,decode,write1,write2,tool 600 -- sudo podman run $C $V llama-server --host 127.0.0.1 --port 8090 -m /srv/models/gemma4-heretic/gemma-4-26B-A4B-it-heretic.Q8_0.gguf --jinja --load-mode none -fa on -ctk q8_0 -ctv q8_0 -np 2 -c 65536 --no-slots --temp 1.0 --top-p 0.95 --top-k 64 --alias gemma4-heretic; stop
./run_arm.sh u20-heretic-q8-rocm 8090 gemma4-heretic long,decode,write1,write2,tool 600 -- sudo podman run $C $R llama-server --host 127.0.0.1 --port 8090 -m /srv/models/gemma4-heretic/gemma-4-26B-A4B-it-heretic.Q8_0.gguf --jinja --load-mode none -fa on -ngl 999 -b 4096 -ub 2048 -ctk q8_0 -ctv q8_0 -np 1 -c 32768 --no-slots --temp 1.0 --top-p 0.95 --top-k 64 --alias gemma4-heretic; stop
echo BATCH1_DONE
