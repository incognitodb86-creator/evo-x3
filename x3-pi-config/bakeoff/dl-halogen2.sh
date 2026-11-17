#!/bin/bash
REV=f5a151cf3f5fac07c2da30cb9af08066231c9ef0
B=https://huggingface.co/peonist-ai/halogen-qwen3.8-flash-next/resolve/$REV
cd /srv/bakeoff/halogen-models
rm -f qwen38-flash-next-v2.hgn
: > ~/evo-x3/bakeoff/halogen.aria
for f in qwen38-flash-next-mtp.hgn qwen38-flash-next-v2.hgn qwen38-flash-next-ngram.hgn; do printf "%s\n  out=%s\n" "$B/$f" "$f" >> ~/evo-x3/bakeoff/halogen.aria; done
aria2c -i ~/evo-x3/bakeoff/halogen.aria -d /srv/bakeoff/halogen-models -x 16 -s 16 -j 1 -c --file-allocation=none --console-log-level=warn --summary-interval=60
echo "ARIA_EXIT $?"
cat > SHA256SUMS.expected <<S
0f50e9626df98168e7c6e0cc264e2a92b5184dd885a175a06628d979b5edceeb  qwen38-flash-next-mtp.hgn
71246c6ab3fc1de2cf06326f18e275fe9c2a18366d646ed3357d194c884fc687  qwen38-flash-next-v2.hgn
3450acada94e19aabad88bd49b45eb70304820949c2240fc178067b20ae5dffe  qwen38-flash-next-ngram.hgn
0997f410c57a1f4e53b09e4be8f4a172d90edd9564368fb0847030937229b9f3  tokenizer/tokenizer.json
S
sha256sum -c SHA256SUMS.expected && echo SHA_OK || echo SHA_FAIL
echo "ALLDONE $(date +%T)"
