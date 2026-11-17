#!/bin/bash
# U26 endpoint re-test through Tailscale Serve + llama-swap auth. Key goes via stdin only.
M=${1:-flash-next}; ARM=${2:-u26-ep-flash-next}; B=https://evo-x3-1.tailf242b2.ts.net
R=~/evo-x3/bakeoff/results; cd ~/evo-x3/bakeoff/u26
key() { sudo bash -c ". /etc/evo-x3/llm.env; printf \"%s\n\" \"\$LLM_KEY_BOX\""; }
T0=$(date +%s); key | python3 bench_key.py --key-stdin --base $B --model $M --arm $ARM --tasks code --out $R/$ARM.cold.json --effort low; echo "COLD_LOAD_PLUS_CODE_S $(( $(date +%s)-T0 ))"
key | python3 bench_key.py --key-stdin --base $B --model $M --arm $ARM --tasks long,tool,decode --out $R/$ARM.json --effort low
key | python3 longctx.py --key-stdin --base $B --model $M --copies 13 --out $R/$ARM.long13.json
key | python3 forge_task.py --key-stdin --base $B --model $M --out $R/$ARM.forge.json
