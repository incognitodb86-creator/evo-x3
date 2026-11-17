#!/bin/bash
# Run the uncensored Flash-Next IQ4_XS arm on Halogen, then Gufo, using the same
# Strix Halo-optimized flags as the official FN arms. Includes write samples and a short refusal probe.
# Does not edit production llama-swap or pi config. Stops only the bake-arm/bake-gufo containers this script starts.
set -euo pipefail
cd ~/evo-x3/bakeoff
D=/srv/bakeoff/fn-uncens-iq4xs
G1=$D/Qwen3.8-Flash-Next-Uncensored-IQ4_XS-00001-of-00003.gguf
MTP_OFFICIAL=/srv/models/flash-next/mtp-Qwen3.8-Flash-Next-shared-Q8_0.gguf
MTP_UNCENS=$D/Qwen3.8-Flash-Next-Uncensored-MTP-draft.gguf
H=ghcr.io/peonist-ai/halogen-flash-server@sha256:70445bcf7acff8f1fe11396a97b866ed30dca31caf5fac62049127658080e07f
GIMG=ghcr.io/gufo-org/toolboxes/gufo-runtime@sha256:49b1fce40cb43e33c46d91595e300cb320cdec768fcd976f8c8da24b402fc133

for f in \
  "$G1" \
  "$D/Qwen3.8-Flash-Next-Uncensored-IQ4_XS-00002-of-00003.gguf" \
  "$D/Qwen3.8-Flash-Next-Uncensored-IQ4_XS-00003-of-00003.gguf"
 do
  [ -s "$f" ] || { echo "MISSING $f — run dl-fn-uncens.sh first"; exit 1; }
done

stop_bake() {
  sudo podman stop -t 15 bake-arm >/dev/null 2>&1 || true
  sudo podman stop -t 15 bake-gufo >/dev/null 2>&1 || true
  sleep 5
}

# Halogen BYO GGUF: same flags as u6-halogen-gguf-q4kxl, plus write + refusal
stop_bake
./run_arm.sh u6-uncens-fn-halogen 8790 qwen3.8-flash-next long,code,tool,decode,write1,write2 1200 -- \
  sudo podman run --rm --name bake-arm -p 127.0.0.1:8790:8731 \
    --device /dev/kfd --device /dev/dri --group-add keep-groups --ipc=host --ulimit memlock=-1:-1 \
    -e HALOGEN_REASONING_EFFORT=low -e HALOGEN_CTX=32768 -e HALOGEN_MAX_TOK=16384 \
    -e HALOGEN_CHECKPOINT=/gguf/Qwen3.8-Flash-Next-Uncensored-IQ4_XS-00001-of-00003.gguf \
    -e HALOGEN_MTP_HEAD=/models/qwen38-flash-next-mtp.hgn \
    -e HALOGEN_TOKENIZER=/models/tokenizer \
    -v "$D":/gguf:ro -v /srv/bakeoff/halogen-models:/models:ro \
    $H
if [ -f results/u6-uncens-fn-halogen.json ]; then
  python3 bench/refusal_bench.py --base http://127.0.0.1:8790 --model qwen3.8-flash-next --arm u6-uncens-fn-halogen \
    --out results/u6-uncens-fn-halogen-refusal.json || true
fi
stop_bake

# Gufo: same flags as production / u6-gufo. Prefer official shared Q8 MTP; fall back to uncensored draft.
MTP=$MTP_OFFICIAL
[ -s "$MTP" ] || MTP=$MTP_UNCENS
[ -s "$MTP" ] || { echo "NO_MTP"; exit 2; }
./run_arm.sh u6-uncens-fn-gufo 8090 flash-next long,code,tool,decode,write1,write2 900 -- \
  sudo podman run --rm --name bake-gufo --network=host \
    --device=/dev/kfd --device=/dev/dri --group-add=keep-groups \
    --security-opt seccomp=unconfined --ulimit memlock=-1:-1 \
    -v /srv/models:/srv/models:ro,Z -v "$D":/srv/uncens:ro,Z \
    $GIMG gufo serve llm --host 127.0.0.1 --port 8090 \
      --model /srv/uncens/Qwen3.8-Flash-Next-Uncensored-IQ4_XS-00001-of-00003.gguf \
      --mtp-model "$( [ "$MTP" = "$MTP_OFFICIAL" ] && echo /srv/models/flash-next/mtp-Qwen3.8-Flash-Next-shared-Q8_0.gguf || echo /srv/uncens/Qwen3.8-Flash-Next-Uncensored-MTP-draft.gguf )" \
      --speculative mtp --context 32768 --sessions 1 \
      --served-model-name flash-next --reasoning-effort low --log-progress
if [ -f results/u6-uncens-fn-gufo.json ]; then
  python3 bench/refusal_bench.py --base http://127.0.0.1:8090 --model flash-next --arm u6-uncens-fn-gufo \
    --out results/u6-uncens-fn-gufo-refusal.json || true
fi
stop_bake
echo "UNCENS_ARMS_DONE $(date '+%F %T %Z')"
