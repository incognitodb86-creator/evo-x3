#!/bin/bash
set -euo pipefail
D=/home/derekboone/evo-x3/bench/2026-11-15-u21
V_IMG=docker.io/kyuz0/amd-strix-halo-toolboxes@sha256:9a9e4d8f56e7792dffca1e2906d9399ff03ef87c9e2148983c9393fcbb8d7fb6
G_IMG=ghcr.io/gufo-org/toolboxes/gufo-runtime@sha256:49b1fce40cb43e33c46d91595e300cb320cdec768fcd976f8c8da24b402fc133
POD_V="podman run --rm --device=/dev/kfd --device=/dev/dri --group-add=keep-groups --security-opt seccomp=unconfined -v /srv/models:/srv/models:ro -v /srv/bakeoff:/srv/bakeoff:ro"
POD_G="podman run --rm --device=/dev/kfd --device=/dev/dri --group-add=keep-groups --security-opt seccomp=unconfined --ulimit memlock=-1:-1 -v /srv/models:/srv/models:ro"

echo "=== Unload llama-swap before direct engine runs ==="
$D/with_key.sh python3 -c '
import os, json, time, urllib.request, subprocess
hdr={"Authorization":"Bearer "+os.environ["LLM_KEY_BOX"]}
def get(p): return urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8080"+p,headers=hdr),timeout=30).read().decode()
print("UNLOAD:", get("/unload"))
for _ in range(60):
    r=json.loads(get("/running"))
    ps=subprocess.run("sudo -n podman ps --format {{.Names}}",shell=True,capture_output=True,text=True).stdout.splitlines()
    gtt=int(open("/sys/class/drm/card1/device/mem_info_gtt_used").read().strip())
    if not r.get("running") and not [x for x in ps if x.startswith("llama-swap-")] and gtt < 512*1024*1024:
        print("CLEAN GTT:", gtt); break
    time.sleep(1)
'

echo "=== B3 Coherence checks for direct llama.cpp Vulkan arms ==="
COH_PROMPT="Explain in two clear sentences why unified memory limits matter on AMD Strix Halo APUs."
$POD_V $V_IMG llama-completion -m /srv/bakeoff/heretic-q4km/gemma-4-26B-A4B-it-heretic.Q4_K_M.gguf -fa on -ctk f16 -ctv f16 -b 2048 -ub 2048 -lm none -n 128 -p "$COH_PROMPT" --no-display-prompt > $D/coherence_vulkan_heretic_q4km.txt 2> $D/coherence_vulkan_heretic_q4km.err
$POD_V $V_IMG llama-completion -m /srv/models/flash-next/Qwen3.8-Flash-Next-UD-Q4_K_XL-00001-of-00004.gguf -fa on -ctk f16 -ctv f16 -b 2048 -ub 512 -lm none -n 128 -p "$COH_PROMPT" --no-display-prompt > $D/coherence_vulkan_flash_next_q4kxl.txt 2> $D/coherence_vulkan_flash_next_q4kxl.err
$POD_V $V_IMG llama-completion -m /srv/models/qwen27b/Qwen3.8-27B-UD-Q8_K_XL.gguf -fa on -ctk f16 -ctv f16 -b 2048 -ub 512 -lm none -n 128 -p "$COH_PROMPT" --no-display-prompt > $D/coherence_vulkan_qwen27b_q8.txt 2> $D/coherence_vulkan_qwen27b_q8.err

echo "=== E1: Heretic Q8_0 Vulkan llama-bench ==="
$POD_V $V_IMG llama-bench -m /srv/models/gemma4-heretic/gemma-4-26B-A4B-it-heretic.Q8_0.gguf -fa on -ctk f16 -ctv f16 -b 2048 -ub 2048 -lm none -p 512 -n 128 -d 0,32768 -r 5 -o json > $D/llama_bench_heretic_q8_vulkan_d0_d32k.json 2> $D/llama_bench_heretic_q8_vulkan_d0_d32k.err
$POD_V $V_IMG llama-bench -m /srv/models/gemma4-heretic/gemma-4-26B-A4B-it-heretic.Q8_0.gguf -fa on -ctk f16 -ctv f16 -b 2048 -ub 2048 -lm none -p 512 -n 128 -d 131072 -r 2 --no-warmup -o json > $D/llama_bench_heretic_q8_vulkan_d131k.json 2> $D/llama_bench_heretic_q8_vulkan_d131k.err

echo "=== E2: Heretic Q4_K_M Vulkan llama-bench ==="
$POD_V $V_IMG llama-bench -m /srv/bakeoff/heretic-q4km/gemma-4-26B-A4B-it-heretic.Q4_K_M.gguf -fa on -ctk f16 -ctv f16 -b 2048 -ub 2048 -lm none -p 512 -n 128 -d 0,32768 -r 5 -o json > $D/llama_bench_heretic_q4km_vulkan_d0_d32k.json 2> $D/llama_bench_heretic_q4km_vulkan_d0_d32k.err
$POD_V $V_IMG llama-bench -m /srv/bakeoff/heretic-q4km/gemma-4-26B-A4B-it-heretic.Q4_K_M.gguf -fa on -ctk f16 -ctv f16 -b 2048 -ub 2048 -lm none -p 512 -n 128 -d 131072 -r 2 --no-warmup -o json > $D/llama_bench_heretic_q4km_vulkan_d131k.json 2> $D/llama_bench_heretic_q4km_vulkan_d131k.err

echo "=== E3: Flash-Next UD-Q4_K_XL Vulkan llama-bench (floor, no MTP) ==="
$POD_V $V_IMG llama-bench -m /srv/models/flash-next/Qwen3.8-Flash-Next-UD-Q4_K_XL-00001-of-00004.gguf -fa on -ctk f16 -ctv f16 -b 2048 -ub 512 -lm none -p 512 -n 128 -d 0,32768 -r 5 -o json > $D/llama_bench_flash_next_q4kxl_vulkan_floor_d0_d32k.json 2> $D/llama_bench_flash_next_q4kxl_vulkan_floor_d0_d32k.err
$POD_V $V_IMG llama-bench -m /srv/models/flash-next/Qwen3.8-Flash-Next-UD-Q4_K_XL-00001-of-00004.gguf -fa on -ctk f16 -ctv f16 -b 2048 -ub 512 -lm none -p 512 -n 128 -d 131072 -r 2 --no-warmup -o json > $D/llama_bench_flash_next_q4kxl_vulkan_floor_d131k.json 2> $D/llama_bench_flash_next_q4kxl_vulkan_floor_d131k.err

echo "=== E4a: Qwen27B UD-Q8_K_XL Vulkan llama-bench ==="
$POD_V $V_IMG llama-bench -m /srv/models/qwen27b/Qwen3.8-27B-UD-Q8_K_XL.gguf -fa on -ctk f16 -ctv f16 -b 2048 -ub 512 -lm none -p 512 -n 128 -d 0,32768 -r 5 -o json > $D/llama_bench_qwen27b_q8_vulkan_d0_d32k.json 2> $D/llama_bench_qwen27b_q8_vulkan_d0_d32k.err
$POD_V $V_IMG llama-bench -m /srv/models/qwen27b/Qwen3.8-27B-UD-Q8_K_XL.gguf -fa on -ctk f16 -ctv f16 -b 2048 -ub 512 -lm none -p 512 -n 128 -d 131072 -r 2 --no-warmup -o json > $D/llama_bench_qwen27b_q8_vulkan_d131k.json 2> $D/llama_bench_qwen27b_q8_vulkan_d131k.err

echo "=== E4b: Qwen27B UD-Q8_K_XL Gufo bench (AR vs DFlash2) ==="
{
  echo "=== GUFO BENCH AR (speculative none) ==="
  $POD_G $G_IMG gufo bench -m /srv/models/qwen27b/Qwen3.8-27B-UD-Q8_K_XL.gguf --speculative none -p 512 -n 128 -d 0,32768,131072 -r 3 -v
  echo "=== GUFO BENCH DFLASH2 ==="
  $POD_G $G_IMG gufo bench -m /srv/models/qwen27b/Qwen3.8-27B-UD-Q8_K_XL.gguf --speculative dflash2 --dflash-model /srv/models/qwen27b/Qwen3.8-27B-DFlash2-Q4_K_M.gguf -p 512 -n 128 -d 0,32768,131072 -r 3 -v
} > $D/gufo_bench_qwen27b_q8.txt 2>&1

echo "STEP3B_ENGINE_DONE"
