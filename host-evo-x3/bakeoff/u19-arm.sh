#!/bin/bash
cd ~/evo-x3/bakeoff
./run_arm.sh $1 8090 flash-next long,decode 900 -- sudo podman run --rm --name bake-arm --network=host --device=/dev/kfd --device=/dev/dri --group-add=keep-groups --security-opt seccomp=unconfined --ulimit memlock=-1:-1 -v /srv/models:/srv/models:ro,Z ghcr.io/gufo-org/toolboxes/gufo-runtime@sha256:49b1fce40cb43e33c46d91595e300cb320cdec768fcd976f8c8da24b402fc133 gufo serve llm --host 127.0.0.1 --port 8090 --model /srv/models/flash-next/Qwen3.8-Flash-Next-UD-Q4_K_XL-00001-of-00004.gguf --mtp-model /srv/models/flash-next/mtp-Qwen3.8-Flash-Next-shared-Q8_0.gguf --speculative mtp --context 32768 --sessions 1 --served-model-name flash-next --reasoning-effort low --log-progress
sudo podman stop -t 10 bake-arm >/dev/null 2>&1
sensors 2>/dev/null | grep -i -E "edge|Tctl|temp1" | head -4 >> results/$1.meta
grep "request=1 phase=prefill" results/$1.engine.log | tail -1 | cut -c1-200 >> results/$1.meta
grep "request=1 phase=decode" results/$1.engine.log | tail -1 | cut -c1-200 >> results/$1.meta
grep "request=2 phase=decode" results/$1.engine.log | tail -1 | cut -c1-200 >> results/$1.meta
echo U19_ARM_DONE
