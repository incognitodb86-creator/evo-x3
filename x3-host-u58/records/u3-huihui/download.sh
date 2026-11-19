#!/bin/bash
# U3: Huihui v2 UD-Q4_K_XL-V2 @ cbc7fba13f19 (public repo, no token)
set -u
D=/srv/models/flash-next-uncensored-huihui-v2
REV=cbc7fba13f1939ac3fa42b18d77ccf43847d74ef
BASE=https://huggingface.co/huihui-ai/Huihui-Qwen3.8-Flash-Next-abliterated-v2-GGUF/resolve/$REV/unsloth-UD-Q4_K_XL-V2
cd $D
echo "start $(date)"
for i in 1 2 3 4; do f=Qwen3.8-Flash-Next-UD-Q4_K_XL-0000$i-of-00004.gguf
  for try in 1 2 3 4 5; do curl -sSfL -C - --retry 5 -o $f "$BASE/$f" && break; echo "retry $f $try"; sleep 10; done
  echo "got $f $(stat -c %s $f) $(date)"
done
sha256sum -c SHA256SUMS && echo SHA_OK || echo SHA_FAIL
echo "done $(date)"
