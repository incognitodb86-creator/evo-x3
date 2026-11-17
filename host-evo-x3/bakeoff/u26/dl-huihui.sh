#!/bin/bash
# U26 step 2 download (Derrick t1774s6524): johnlockejrr/Huihui-Qwen3.8-Flash-Next-abliterated-HGN, pinned revision.
# Not gated; Qwen Community License 1.0 (LICENSE copied beside the weights). ~110.7 GiB.
REV=e3c04876bfca686eb0c1101c651d60d7baff7379
B=https://huggingface.co/johnlockejrr/Huihui-Qwen3.8-Flash-Next-abliterated-HGN/resolve/$REV
D=/srv/models/flash-next-uncensored-hgn
mkdir -p $D/tokenizer; cd $D
L=~/evo-x3/bakeoff/u26/huihui.aria; : > $L
for f in model.hgn qwen38-flash-next-ngram.hgn qwen38-flash-next-vision.hgn LICENSE README.md config.json conversion-manifest.json \
  preprocessor_config.json video_preprocessor_config.json sha256.txt \
  tokenizer/chat_template.jinja tokenizer/config.json tokenizer/generation_config.json tokenizer/merges.txt \
  tokenizer/tokenizer.json tokenizer/tokenizer_config.json tokenizer/vocab.json; do
  printf "%s\n  out=%s\n" "$B/$f" "$f" >> $L; done
aria2c -i $L -d $D -x 16 -s 16 -j 2 -c --file-allocation=none --console-log-level=warn --summary-interval=120
echo "ARIA_EXIT $?"
cat > SHA256SUMS.expected <<S
6d5f4c66ad653301bb103c77364becb7270711df04162e8f4d85f5aad1ac16be  model.hgn
339f5c508ca592ee2613ac5c3082587a88991d5592c4160d49a32a6dbdb3f30b  qwen38-flash-next-ngram.hgn
b6ca6716eaab601773f7155701bb09f39c72922caa21620bab577f0281f2ea2a  qwen38-flash-next-vision.hgn
0997f410c57a1f4e53b09e4be8f4a172d90edd9564368fb0847030937229b9f3  tokenizer/tokenizer.json
S
sha256sum -c SHA256SUMS.expected && echo SHA_OK || echo SHA_FAIL
ls -l model.hgn qwen38-flash-next-ngram.hgn qwen38-flash-next-vision.hgn
echo "ALLDONE $(date +%T)"
