# brief9: switch terrace queue to batch run_queue.py (Derrick 9:52 AM CT go)
1. Let the current terrace driver finish the clip in flight, then stop that driver (do not kill ComfyUI/llama-swap; it releases the lock as usual).
2. Confirm gpu-render.lock is free, then run:
   cd C:\AI\community
   python scripts\run_queue.py --run-dir C:\AI\community\runs\terrace_settings_v3_20261030 --queue C:\AI\community\runs\terrace_settings_v3_20261030\_render_order.json --resume
   (add --dry-run first if you want; it should list the remaining clips in plan order)
3. Script sha256 f1765eef54558d42dad79676bc6e3673ec528e944a5a7d06213db9ead95fdd24; usage: templates\render-queue-template.md. Same settings and order; only the lock/ComfyUI cycle changes.
4. If it errors, fall back to the old driver with the remaining clips and note why in notes\actions.log.
Done line in notes\actions.log: "brief9 batch resume started pos=<n>".
