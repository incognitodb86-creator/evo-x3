#!/bin/bash
# U8 check: run ON the X3 (needs sudo to read /etc/evo-x3/llm.env). Never prints a key.
# Expect: no key -> 401; LLM_KEY_BOX -> 200 on /v1/models. llama-swap must be running (502 = it is stopped).
set -u
URL=${1:-https://evo-x3-1.tailf242b2.ts.net/v1/models}
printf 'no key: '; curl -s -o /dev/null -w '%{http_code}\n' -m 20 "$URL"
printf 'LLM_KEY_BOX: '
sudo bash -c '. /etc/evo-x3/llm.env; printf "Authorization: Bearer %s\n" "$LLM_KEY_BOX"' \
  | curl -s -o /dev/null -w '%{http_code}\n' -m 20 -H @- "$URL"
