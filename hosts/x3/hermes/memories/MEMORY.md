EVO-X3 paths: monorepo clone /home/evo/AI/evo-x3 (branch mono only); /home/evo/AI/{render,community,forge} are symlinks into x3/{render,community,forge}. Runs live in /home/evo/AI/community/runs/<run>.
§
Services: X3 llama-swap http://127.0.0.1:8080/v1 (writer/Hermes); PixlStash http://127.0.0.1:9537 (token file /home/evo/.config/pixlstash/render-read.token, never print); AlienPc ComfyUI https://alienpc.tailf242b2.ts.net:8446 and Swift :8447.
§
Stills: PixlStash inbox /home/evo/AI/pixl-inbox (auto-imported in background by pixl-import); Flux still builder /home/evo/AI/community/scripts/parody/flux_still.py (supports --hybrid "<Name>" for 0.85 Klein9 RefMod + 0.60 Prodigy LoRA).
§
H3Max Beta 7: 10Eros-Max Beta 7 rules (TenStrip HF #77 / U56 Decision #1: no overall_soundscape/non_diegetic_music/integrated_multimodal_description headers); Realism LoRA opt-in via --realism-lora (r34l1sm auto-injected only when loaded).
§
Coding goes to pi via /usr/local/bin/pi-job code|review (AlienPc Swift ESP-off when idle, X3 Gufo when busy). Never edit render/community/forge code directly from Hermes.
