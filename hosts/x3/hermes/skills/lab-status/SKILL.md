---
name: lab-status
description: "Use when Derrick asks for lab status, GPU availability, what model is loaded on X3 or AlienPc, whether a render or pi-job is running, PixlStash inbox count, or disk space ('status', 'is AlienPc busy?', 'what is rendering?', 'check the queue'). Read-only; never wakes ComfyUI or prints secrets."
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [ops, status, health]
    category: devops
    requires_toolsets: [terminal]
---

# Lab Status (Read-Only X3 + AlienPc Snapshot)

Run ONE compact read-only command to report live EVO-X3 + AlienPc status. Never print keys/tokens and never hit endpoints that wake AlienPc ComfyUI (use `/system_stats`, which is in AlienPc `llama-swap` `ignorePaths` and returns `409` when unloaded).

```bash
echo "=== X3 llama-swap ==="; curl -sS -m 3 http://127.0.0.1:8080/running 2>/dev/null || echo "unreachable"
echo "=== AlienPc GPU (non-waking) ==="
c_code=$(curl -sS -o /dev/null -m 4 -w '%{http_code}' https://alienpc.tailf242b2.ts.net:8446/system_stats 2>/dev/null || echo 000)
s_code=$(curl -sS -o /dev/null -m 4 -w '%{http_code}' https://alienpc.tailf242b2.ts.net:8447/health 2>/dev/null || echo 000)
echo "comfy(:8446/system_stats)=$c_code (409=unloaded/idle, 200=loaded)  swift(:8447/health)=$s_code"
[ "$c_code" = "200" ] && curl -sS -m 4 https://alienpc.tailf242b2.ts.net:8446/queue 2>/dev/null | jq -c '{running:(.queue_running|length), pending:(.queue_pending|length)}' || true
echo "=== Locks & Jobs ==="
flock -n /home/evo/AI/locks/gpu-render.lock true 2>/dev/null && echo "x3 gpu-render.lock: FREE" || echo "x3 gpu-render.lock: BUSY"
echo "x3-lease: $(cat /home/derekboone/AI/locks/x3-lease.txt 2>/dev/null || echo empty)"
/usr/local/bin/pi-job status 2>/dev/null | head -n 12 || true
echo "=== PixlStash inbox & Disk ==="
echo "pixl-inbox files: $(find /home/evo/AI/pixl-inbox -maxdepth 1 -type f ! -name '.*' 2>/dev/null | wc -l)  pixl-import: $(systemctl --user is-active pixl-import.service 2>/dev/null || echo inactive)"
df -h / /home/evo/AI 2>/dev/null | tail -n +2
```

Summarize the result in 5-6 short plain lines (X3 model, AlienPc ComfyUI/Swift state, active render/pi-job, inbox count, disk free). Never dump raw JSON.
