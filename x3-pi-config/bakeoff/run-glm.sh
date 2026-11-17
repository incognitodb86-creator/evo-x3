#!/bin/bash
set -euo pipefail
cd ~/evo-x3/bakeoff
IMG=docker.io/kyuz0/amd-strix-halo-toolboxes@sha256:cf0d43fe54fae7a744942c49656e3c7b2be9890b4d6b3c60a5570f06874efb8c
MODEL=/srv/bakeoff/glm/Maya-S24/GLM-5.3-Flash-Maya-S24-IQ2_XXS_S-00001-of-00003.gguf
PACK=/srv/bakeoff/glm/Maya-S24/maya-pack
C=(--rm --name bake-arm --network=host --device=/dev/kfd --device=/dev/dri --group-add=keep-groups --security-opt seccomp=unconfined --ipc=host --ulimit memlock=-1:-1 -v /srv/bakeoff/glm:/srv/bakeoff/glm:Z)
echo "GLM_PREPARE_START $(date '+%F %T %Z')"
if [ ! -f "$PACK/tokenizer/tokenizer.json" ] && [ ! -d "$PACK/tokenizer" ]; then
  sudo podman run "${C[@]}" $IMG maya-prepare --family glm --model "$MODEL" --output "$PACK"
fi
echo "GLM_PREPARE_END $(date '+%F %T %Z')"
export HEALTH_PATH=/v1/models
./run_arm.sh u15-glm-maya-s24 8090 glm-maya-s24 long,code,tool,decode 1200 -- \
  sudo podman run "${C[@]}" $IMG maya-serve --family glm --pack "$PACK" --model-name glm-maya-s24 --context 32768 --mode mtp --host 127.0.0.1 --port 8090
unset HEALTH_PATH
sudo podman stop -t 20 bake-arm >/dev/null 2>&1 || true
sleep 3
echo "GLM_ARM_DONE $(date '+%F %T %Z')"
