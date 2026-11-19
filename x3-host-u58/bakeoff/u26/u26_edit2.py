import sys
p=sys.argv[1]; s=open(p).read()
assert '"flash-next-uncensored"' not in s
s=s.replace('            - "flash-next-gufo"\n','            - "flash-next-gufo"\n            - "flash-next-uncensored"\n',1)
new='''  "flash-next-uncensored":
    # U26 2026-11-15 ~6:25 PM CT (Derrick t1774s6524 "Download and test the abliterated Flash-Next in Halogen's format"):
    # NON-PRODUCTION slot; not Forge's default. johnlockejrr/Huihui-Qwen3.8-Flash-Next-abliterated-HGN @e3c04876
    # (community bf16-to-hgn native v2 conversion of huihui-ai's abliterated BF16; MTP head, n-gram table and tokenizer from
    # the same source; Qwen Community License 1.0, LICENSE beside the weights). sha256 OK: model.hgn 6d5f4c66..., ngram
    # 339f5c50..., vision b6ca6716... in /srv/models/flash-next-uncensored-hgn (110.7 GiB). Same engine/flags as flash-next.
    # U26 bench (cold, effort low): load 25 s; 18k prefill 1,859 / decode 81 long, 61 prose; 127k 1,790 / 71; 237k 1,688 / 69,
    # needle found at both; tools 3/3; Forge coding task pass; write1/write2 pass; refusal probes comply 3/3 (stock refuses
    # explicit_adult). 88.9 GiB engine total, same as stock. Vision sidecar present but not loaded (text-only slot).
    cmd: |
      podman run --rm --name llama-swap-flash-next-uncensored
        -p 127.0.0.1:8081:8731
        --device /dev/kfd --device /dev/dri --group-add keep-groups --ipc=host --ulimit memlock=-1:-1
        -e HALOGEN_MODEL_ID=flash-next-uncensored -e HALOGEN_CTX=262144
        -e HALOGEN_CHECKPOINT=/models/model.hgn
        -e HALOGEN_REASONING_EFFORT=medium
        -e HALOGEN_TEMPERATURE=1.0 -e HALOGEN_TOP_P=0.95 -e HALOGEN_TOP_K=20
        -v /srv/models/flash-next-uncensored-hgn:/models:ro
        ghcr.io/peonist-ai/halogen-flash-server@sha256:3041272385d1ac88e5b842be3dbf4b99472bb079f22430c1ea3b3e0dbd1e1568
    proxy: "http://127.0.0.1:8081"
    ttl: 3600
    concurrencyLimit: 1
    checkEndpoint: "/health"

'''
i=s.index('\n  "flash-next-gufo":\n')+1
s=s[:i]+new+s[i:]
open(p,'w').write(s); print("edited")
