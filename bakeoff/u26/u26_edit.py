import sys
p=sys.argv[1]; s=open(p).read()
assert s.count('\n  "flash-next":\n')==1
s=s.replace('\n  "flash-next":\n','\n  "flash-next-gufo":\n    # U26 2026-11-15 ~5:30 PM CT: ROLLBACK slot. This was "flash-next" (Gufo) until Derrick t1774s6524 moved Forge to Halogen.\n    # To roll back: rename this back to "flash-next" and the Halogen slot above to "flash-next-halogen", restart llama-swap.\n',1)
assert s.count('--served-model-name flash-next\n')==1
s=s.replace('--served-model-name flash-next\n','--served-model-name flash-next-gufo\n',1)
s=s.replace('            - "flash-next"\n','            - "flash-next"\n            - "flash-next-gufo"\n',1)
new='''  "flash-next":
    # U26 2026-11-15 ~5:30 PM CT (Derrick t1774s6524 "Move Forge to Halogen native and test it at full context"):
    # official Peonist Halogen native v2 checkpoint (peonist-ai/halogen-qwen3.8-flash-next: qwen38-flash-next-v2.hgn
    # 62.1 GiB + n-gram table 47.7 GiB mmap, not held + MTP head built in) on halogen-flash-server 0.20.5 (official image,
    # pulled 2026-11-15, same checkpoints as 0.20.4). Full native context: HALOGEN_CTX=262144 per request; default KV pool
    # 524288 positions (two full conversations resident, 4 slots) because it fits: engine-measured 88.9 GiB in all
    # (62.1 weights + 14.4 KV pool + 12.4 working), GTT peak 27.0 GiB of 120. U26 bench (cold, effort low): 18k prefill
    # 1,870 tok/s, decode 85 long / 64 prose; 127k prefill 1,807 / decode 69; 237k prefill 1,707 / decode 58; tools 3/3.
    # Sampling defaults = Qwen card / old Gufo preset (1.0 / 0.95 / 20); requests that send their own win. Effort medium.
    # Loopback publish (-p 127.0.0.1) instead of --network=host: the image's API binds [::], host network would expose it.
    # Rollback: slot "flash-next-gufo" below (or backup llama-swap.yaml.bak-20261115-172352-pre-u26-halogen).
    cmd: |
      podman run --rm --name llama-swap-flash-next
        -p 127.0.0.1:8081:8731
        --device /dev/kfd --device /dev/dri --group-add keep-groups --ipc=host --ulimit memlock=-1:-1
        -e HALOGEN_MODEL_ID=flash-next -e HALOGEN_CTX=262144
        -e HALOGEN_REASONING_EFFORT=medium
        -e HALOGEN_TEMPERATURE=1.0 -e HALOGEN_TOP_P=0.95 -e HALOGEN_TOP_K=20
        -v /srv/bakeoff/halogen-models:/models:ro
        ghcr.io/peonist-ai/halogen-flash-server@sha256:3041272385d1ac88e5b842be3dbf4b99472bb079f22430c1ea3b3e0dbd1e1568
    proxy: "http://127.0.0.1:8081"
    ttl: 86400
    concurrencyLimit: 1
    checkEndpoint: "/health"

'''
i=s.index('\n  "flash-next-gufo":\n')+1
s=s[:i]+new+s[i:]
open(p,'w').write(s)
print("edited")
