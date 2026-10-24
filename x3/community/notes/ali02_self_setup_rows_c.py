"""ROWS - PROMPT.md / AGENTS.md / plan claims for notes/self_setup_20261023.md (fix_plan 0.2).
Row = (claim, evidence, verdict, what_you_will_do); evidence contract is documented in rows_a.
"""

ROWS = [
    ("H3 graph internals: steps live in s0_sched / s1_sched, the sampler is ksel (euler), shift is m_shift 10 video / 3 audio, and two SamplerCustomAdvanced nodes mean a single pass",
     "local:notes/ali02_local_probe2.py", "verified",
     "Keep the key map in AGENTS.md; count SamplerCustomAdvanced nodes rather than KSamplerAdvanced when validating a graph (the naive count false-fails a correct graph)."),
    ("MiniMaxH3ImageToVideo has no audio_vae input, only the ReferenceToVideo node does",
     "local:ComfyUI/comfy_extras/nodes_minimax_h3.py", "verified",
     "Keep it in the static pre-check (check 11 of the r4g2 builder): an audio_vae key on the I2V node is an instant rc 2, not a warning."),
    ("the Continuum sampler exposes no negative-prompt input, so negative / nag style advice belongs in the sequence_prompt as prose",
     "local:notes/ali02_local_probe2.py", "verified",
     "Keep prose 'no:' lines in the sequence prompt and stop adding negative-encoder wiring to HC graphs."),
    ("the loop calls C:/AI/director/scripts/gpu_guard.ps1 with no arguments at ralph.ps1:51 and :77",
     ["local:C:/Users/derek/5slock/ralph-community/ralph.ps1", "local:C:/AI/director/scripts/gpu_guard.ps1"], "stale",
     "The script exists but ralph.ps1 never calls it (0 hits). Fix AGENTS.md this pass: either wire the guard before a render tick in ralph.ps1 (backed up, parser-checked) or delete the line - today GPU contention is unguarded."),
    ("the render-budget ledger that gates these runs sits in the ralph-community logs folder with cap_min 615 and job_cap 45",
     "local:C:/Users/derek/5slock/ralph-community/logs/p7_budget.json", "verified",
     "Read the ledger before any gate/BAKEOFF decision (used_min 472.9, jobs 38 at this audit); there is no ledger under C:/AI/community - never quote an assumed count."),
    ("run_graph_job.py calls the adults-only guard on every prompt before queueing",
     "local:scripts/run_graph_job.py", "verified",
     "Keep the guard call; the adults-only suite is 21 passed, and every render path must keep passing through it."),
    ("the fiction lock document exists in the repo and defines the adults-only canon",
     "local:C:/Users/derek/5slock/plans/canon/fiction-cond-lock.md", "verified",
     "Keep the path in AGENTS.md; it is the authority for the 21+ canon line and the content checks."),
    ("pi skills exist for this project at skills/<name>/SKILL.md",
     "local:skills/h3-hc-render/SKILL.md", "verified",
     "Three skills exist (forge-self-diagnose, h3-hc-render, h3-prompting); keep them out of the Ralph cwd so they stay visible, and never duplicate a skill's content into notes."),
    ("AGENTS.md states ComfyUI 0.19.2 dropped sparse_blocks / sparse_size / max_dims, so the frozen r3b attention nodes are schema-stale",
     "local:C:/AI/community/notes/ali02_local_probe.py", "stale",
     "The installed version is 0.38.0 and the upstream changelog is not fetchable, so the key-drop list is unverifiable: re-dump the live node schema (object_info) before cloning those nodes, and rewrite the AGENTS.md line to name the version in use."),
    ("AGENTS.md header claims the box is an RTX 4090 with 64 GB",
     ["local:C:/Users/derek/5slock/ralph-community/AGENTS.md", "label:nvidia-smi (driver version, GPU name, VRAM)"], "wrong",
     "Rewrite the header to RTX 5070 Ti 16 GB this pass (Forge owns the file); quant and batch-size advice in the notes is derived from that line."),
    ("481 frames is the 20 s shape on the (frames - 5) % 17 grid and 243 frames is 10.125 s at 24 fps",
     ["web/02x_minimax_disc28.json", "web/02v_docs_h3.txt"], "verified",
     "Keep the grid and the seconds arithmetic in AGENTS.md; the grid is the source claim, the seconds are our division by 24 fps."),
    ("continuation work belongs to the repo path Physon-XX/ComfyUI_Minimax_H3_Continuum",
     ["web/04x_cont_repo.json", "web/02v_continuation_repo.json"], "wrong",
     "That path 404s; the live continuation pack is ukr8b3g-cmyk/ComfyUI-H3-Continuum (265 stars). Fix every note and job comment that names Physon-XX."),
    ("the Continuum long-form pack on this box is a plain community pack with a healthy registry status",
     ["web/02v_registry_continuation.json", "web/04y_reg_continuum.json"], "wrong",
     "The registry flags the latest versions of both Continuum packs; expect install friction and say so in render notes instead of promising a clean install."),
    ("civitai 2860061 is a model to install for the Continuum workflow",
     "web/02v_civitai_2860061.json", "wrong",
     "It is a Workflow (type Workflows, 6,942 downloads, 187 thumbs): import it as a workflow, never as a model slot."),
    ("the AGENTS.md command line for the render cost claim (VSA keep 10 = 2:09, keep max = 5:05) is reproducible on this box",
     ["local:notes/ali02_local_probe.py", "local:runs/ali147_pool_hc_r3b_s51130003/request.api.json"], "stale",
     "Only the r3b run dir survives; re-run the A/B with a committed timing script before the number is quoted again, and mark it as our own measurement, not community advice."),
]

BLOCKED = [
    ("the ModelAttentionBackend schema on 0.38.0 (which keys the attention node exposes)",
     "https://raw.githubusercontent.com/Comfy-Org/ComfyUI/main/CHANGELOG.json", "web/04x_comfy_changelog.404.txt"),
    ("ComfyUI GitHub discussions 8568 / 12471 / 24165 about H3 quality",
     "https://github.com/Comfy-Org/ComfyUI/discussions/8568", "web/02x_comfyui_disc8568.401.txt"),
    ("ComfyUI issues 17706 / 18071 / 24551 (the extra upstream bug reports)",
     "https://api.github.com/repos/Comfy-Org/ComfyUI/issues/17706", "web/02x_comfyui_issue17706.404.txt"),
    ("the MiniMax H3 model repo page discussion 28 HTML view",
     "https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/28", "web/02v_minimax_disc28_page.401.txt"),
    ("prompt-relabeller model card page (the lightx2v PE card as a web page)",
     "https://huggingface.co/ByteDance-Seed/prompt-relabeller-9B", "web/04z_pe_api.json"),
    ("the Continuum continuation README as fetched from its repo root",
     "https://raw.githubusercontent.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/main/README.md", "web/03y_continuation_readme.404.txt"),
]

SELF_MEASURED = [
    "the 106-class HF-Face pack support result and 0/5 model support come from Forge's own probe scripts, not from the HF space (API 401)",
]

# No extra blocked entries: rows_b carries the shared BLOCKED list (401/403/404 stamps, each
# checked against the manifest URL that wrote it).
BLOCKED = []
