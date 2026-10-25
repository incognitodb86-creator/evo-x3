# CF1 Community Setup Audit Table (3.9 / CF1)
Date: 2026-10-24
Last Updated: 2026-10-27 (AUD1 citation repair - this revision replaces the citation column)

## What changed in this revision (AUD1, 2026-10-27)
The 2026-10-24 revision cited **bare URLs** ("https://docs.comfy.org/...", "https://github.com/mostlygeek/
llama-swap", "https://huggingface.co/Qwen/Qwen2.5-Coder-32B-Instruct", "https://pi.dev/docs/") and asserted
"match" for every row. `fix_plan.md` AUD1 measured the fault: the saved body those URL rows stand on
(`notes/web/02v_docs_h3.txt`) contains **0 hits** for `lowvram|RIFE|cfg`, so that citation cannot support
those cells. This revision does what AUD1 asks: **every** row now names a file that is on disk, quotes the
wording it carries, and states a verdict. The gate `notes/ali02_citation_check.py` checks these rows.

Verdicts used in the last column:
- `ON-DISK` - a saved body in `notes/web/` carries the quoted community wording (path + line + verbatim).
- `OURS` - the value is Forge's own choice; the source named is the shipped config/graph file that carries
  it, not community advice (the 0.2 rule: our numbers never get dressed up as community advice).
- `UNSOURCED` - no saved body in `notes/web/` carries the claim; the grep that shows it is in §CITATION AUDIT.
- `CONFLICT` - a saved body contradicts the row.
- `BLOCKED` - the source refused the fetch; the 40x stamp is on disk (a stamp is a blocked row, never evidence).

Sources of the `Ours` column (measured 2026-10-27, all readable on this box): the live render upstream
`C:/AI/director/config/llama-swap.yaml`, the LLM launcher config `C:/AI/strata-0.2.2/strata-swift15-iq3s.json`,
the live agent config `C:/Users/derek/.pi/agent/settings.json` + `models.json`, and the shipped graph
`C:/AI/community/p7/graphs/ali163_hc15_bd002_s51150001.api.json` (33 nodes) and its fixed sibling
`ali163_hc15_bd002_s51150011.api.json` (27 nodes). 19 `.api.json` graphs exist in `p7/graphs/`.

## Audit Table

| # | Component / Setting | Ours (source on disk) | Community wording on disk (`notes/web/<body>:<line>`, verbatim) | Verdict |
|---|---|---|---|---|
| 1 | llama-swap: ComfyUI check endpoint | `llama-swap.yaml:120` `checkEndpoint: /` (comfyui_auto), `:137` (comfy-longvideo) | `01r_ls_comfyui.txt:29` `checkEndpoint: /` + `:6` lists `models.*.checkEndpoint` as a config key of the ComfyUI upstream type | ON-DISK |
| 2 | llama-swap: ComfyUI websocket compat | `compat.ignoreWebsockets: true` in the live ComfyUI upstream block | `01r_ls_comfyui.txt:6` `config_keys: [models.*.compat.ignoreWebsockets, models.*.concurrencyLimit, models.*.checkEndpoint, models.*.cmdStop, models.*.unloadTimeout, models.*.ttl, ...]` | ON-DISK |
| 3 | llama-swap: per-model concurrency | raised `concurrencyLimit` (live upstream block) | `01r_ls_comfyui.txt:68` "\| `concurrencyLimit` \| raised to at least `999` \| the per-model default is 10; one open ComfyUI tab makes many parallel asset and API requests" | ON-DISK |
| 4 | llama-swap: `cmdStop` exists and is what releases the GPU | `llama-swap.yaml:131-135` (comment + `cmdStop` for the long-video upstream) | `01r_ls_comfyui.txt:6` (config key `models.*.cmdStop`), `:30` `cmdStop: docker stop comfyui-auto`; `01r_llamaswap_readme.txt:322` "`cmdStop` gracefully stop Docker/Podman containers" | ON-DISK (the mechanism); our Windows `taskkill` script is OURS - `taskkill` = 0 hits in every saved body |
| 5 | llama-swap: ComfyUI `unloadTimeout: 1900` | `llama-swap.yaml:122` `unloadTimeout: 1900  # ALI-156: > graceful-stop cap`, `:139` (long-video), with the reason in `:131-135` | The key is documented (`01r_llamaswap_readme.txt:319` "`unloadTimeout` to tune graceful unloads (manual, API and `ttl` expiry)"). The numbers `1900`, `1800` and the sentence "unloadTimeout must be greater than the budget of that script" are in NO saved body (`1900` hits are byte-counts in unrelated JSON, `1800` = 0 hits) | OURS (key ON-DISK, value UNSOURCED) |
| 6 | llama-swap: ComfyUI `ttl: 300` + `persistent` group | `llama-swap.yaml:121` `ttl: 300  # RENDER-TIMEOUT (2026-10-26): was ttl: 0...` | `01r_ls_ttl-and-unloading.txt:96` "**Keeping a small model always warm.** `ttl: 0` plus a `persistent` group." - the pattern; `01r_llamaswap_readme.txt:68,:318` "`ttl` to automatically unload models" | ON-DISK (pattern), value OURS |
| 7 | llama-swap: LLM group `swap: true, exclusive: true`; ComfyUI group `persistent: true, swap: false, exclusive: false` | `llama-swap.yaml:52-54` (`main:` `swap: true`, `exclusive: true`), `:46-51` (`comfyui:` `persistent: true`, `swap: false`, `exclusive: false`, member `comfyui_auto`) | `agy41_ls_groups.md:33` "swap: true # only one member runs at a time", `:34` "exclusive: true # running a member unloads every other group", `:55` "**`exclusive`** (default `true`) \u2014 how the group affects *other* groups", `:57` "**`persistent`** (default `false`) \u2014 other groups can never unload this one" (same 10,836 B page saved twice: `agy41_ls_groups.md`, `rt_ls_groups-and-matrix.txt`) | **ON-DISK** \u2014 the groups page IS on disk under the agy41/rt prefixes. My first measurement (2026-10-27) grepped only `01r_ls_*.txt` + the README and concluded "never saved": the gate refuted that, recorded in \u00a7CITATION AUDIT. |
| 8 | llama-swap: model health timeout "120-1200 s" | not present in the live config | `120-1200` = **0 hits** in all 1,146 saved bodies | UNSOURCED |
| 9 | Strata: context window 131072 | `C:/AI/strata-0.2.2/strata-swift15-iq3s.json:22-23` `"--max-context", "131072"` | `--max-context` = **0 hits** in any saved body; the llama-swap docs never mention Strata (`Strata` = 0 hits outside unrelated HF model jsons) | OURS (was cited as llama-swap advice - not supported) |
| 10 | Strata: `--vram-reserve-mib 1100` | same file `:37` `"--vram-reserve-mib"` | `vram-reserve-mib` = 0 hits in any saved body; the "1024-1408 MiB on 16GB RTX 5070 Ti" range = 0 hits (`1024`/`1408` hits are byte-counts) | OURS |
| 11 | Strata: speculative decoding `--spec 4 --spec-min-p 0.5` | same file `:16,:18` (`--spec`, `--spec-min-p`) | `--spec` / `--spec-min-p` = 0 hits in any saved body | OURS |
| 12 | Strata: KV cache `--kv int8` | not present: `kv int8` = 0 hits in `strata-swift15-iq3s.json` and in `llama-swap.yaml` (the vision upstream uses `-ctk q8_0 -ctv q8_0`, `llama-swap.yaml:110`) | 0 hits | UNSOURCED (the 2026-10-24 row describes a flag we do not pass) |
| 13 | Sampling: temp 1.0 / top_p 0.95 / top_k 20 | `strata-swift15-iq3s.json:95-97` `"temperature": 1, "top_p": 0.95, "top_k": 20` | `Qwen2.5-Coder-32B-Instruct` = **0 hits**, `top_p 0.95` = **0 hits** in all 1,146 saved bodies - the cited HF card was never saved | OURS (the URL row is UNSOURCED) |
| 14 | pi: defaultProvider / model | `C:/Users/derek/.pi/agent/settings.json` `"defaultProvider": "llama-swap"`, `"model": "coding_swift15_iq3s"` | `defaultProvider` is documented in the saved pi settings page: `01r_pidev_settings.html` (token present; the page is the pi docs copy) | ON-DISK (doc) + OURS (values) |
| 15 | pi: `contextWindow` | `C:/Users/derek/.pi/agent/models.json` - 4 model entries: two carry `"contextWindow": 92160`, two carry `"contextWindow": 128000` | `contextWindow` documented in `01r_pidev_modelsconfig.html` and `01r_pidev_compaction.html` | ON-DISK (doc); the 2026-10-24 row's "128000, switched from 92160" is only true for 2 of the 4 entries - the mixed state is the accurate description |
| 16 | pi: `extensionSlots` / `["-builtin:llama.cpp"]` | NOT in live `settings.json` (keys present: `defaultProvider`, `model`, `images`, `compaction`, `httpIdleTimeoutMs`, `retry`) | `extensionSlots` = 0 hits in the saved pi docs bodies | UNSOURCED (and not our live state) |
| 17 | pi: installed packages | `C:/Users/derek/.pi/agent/settings.json` packages block (pi-permission-system, pi-subagents, compound-engineering) | `01r_pidev_packages.html` documents the packages mechanism; `01r_npm_pi_permission_system.json`, `01r_npm_pi_subagents.json` are the npm registry bodies | ON-DISK (mechanism) + OURS (what we installed) |
| 18 | pi: GPU MCP servers `enabled: false` | live `.pi/agent/mcp.json` | `enabled: true|false` = 0 hits in the saved pi docs bodies (no MCP page saved) | OURS (measured by `pi mcp list`, recorded in AGENTS.md L3) |
| 19 | pi: compaction / timeouts | `settings.json` `compaction.enabled: true`, `reserveTokens: 16384`, `httpIdleTimeoutMs: 1950000`, `retry.provider.timeoutMs: 1200000` | `01r_pidev_compaction.html` (`compaction.*`), `01r_pidev_settings.html` (`httpIdleTimeoutMs`, `retry.*`); `contextThrottle`/`cacheRetention`/`127.0.0.1:3489`/`totalTimeout` = 0 hits (`cacheRetention` hits are in the models-config page, unrelated) | ON-DISK (keys), values OURS |
| 20 | ComfyUI launch: network | `llama-swap.yaml:118` `... main.py --listen 127.0.0.1 --port ${PORT} --disable-async-offload --disable-pinned-memory` (comfyui_auto); `:130` (long-video, + `--input-directory`) | `--listen` is documented in `01r_comfymcp_readme.html:1025` ("`--listen 127.0.0.1` / `::1` / `localhost` is the default bind spelled explicitly"); the H3 docs page carries no launch-flag row | ON-DISK (loopback bind advice), flags OURS |
| 21 | ComfyUI launch: memory `--lowvram` | NOT in the live launch command (`llama-swap.yaml:118,:130` pass `--disable-async-offload --disable-pinned-memory`, no `--lowvram`) | `lowvram` = **0 hits** in all 1,146 saved bodies; `>20GB` = **0 hits**; `16GB VRAM` appears in exactly one body, `pq1_civitai_h3_prompt_models.json` (a Civitai prompt-models listing, not a launch recommendation). The flags `--disable-async-offload`/`--disable-pinned-memory` appear in exactly one body: `02v_comfyui_issue15337.json` (a ComfyUI issue report, not a recommendation) | UNSOURCED + the "Ours" cell was wrong (we do not pass `--lowvram`) |
| 22 | ComfyUI launch: attention `--use-ck-attention` | NOT in the live launch command (`llama-swap.yaml:118,:130`) | `02v_docs_h3.txt:204` "Add **Model Attention Backend** (`comfy kitchen attention`) on the model path to `BasicGuider` (after LoRA/turbo), or use `--use-ck-attention` (0.32.0+). Requires `comfy-kitchen` INT8 kernels on your hardware." · `:202` "On **bf16** checkpoints, **Comfy Kitchen attention** (channel rotation before quantize) clears artifacts at similar speed." · **`02v_docs_h3.txt:80` "Comfy Kitchen attention cannot run `int8_convrot` checkpoints"; use a `bf16` build with that backend."** | ON-DISK + **CONFLICT**: our checkpoint IS `int8_convrot` (`p7/graphs/ali163_hc15_bd002_s51150001.api.json` node `unet` = `10Eros_Max_h3_8stepTURBO_beta6_int8.safetensors`), so the 2026-10-24 "match" was wrong. Attention is set in-graph (`m_attn` = ModelAttentionBackend), which is the shape the doc prescribes. |
| 23 | Checkpoint | `p7/graphs/ali163_hc15_bd002_s51150001.api.json` node `unet` UNETLoader `10Eros_Max_h3_8stepTURBO_beta6_int8.safetensors` | The card on disk is 3,698 B, md5 `6471e229…`, 63 lines, five identical copies (Key Finding 5). It describes beta_6 at `:16` and points at an int8-convrot build at `:47-48`; it publishes no benchmark row. | ON-DISK (the card) + OURS (which file we loaded) |
| 24 | VAE: int8 video + fp32 audio | same graph: `vvae` = `minimax_h3_video_vae_int8_convrot.safetensors`, `avae` = `minimax_h3_audio_vae_fp32.safetensors` | "int8 video VAE + fp32 audio VAE" is not a published phrase (`int8 video VAE` = 0 hits in fetched bodies); the docs list model/VAE files by variant (`02v_docs_h3.txt:74,:80`) and `audio_vae` is a node input in `02v_core_nodes_minimax_head.txt:75-81` | OURS (measured off the graph), not community advice |
| 25 | Resolution 1344x768, multiple of 32 | graph `width`/`height` inputs; canvas rule enforced by the Continuum code (`notes/ali173_b2_object_info_full.json`) | `02v_docs_h3.txt:128` "For 16:9 native quality, set **0.98** (\~1344×768) or enter **1344 × 768** on the node. Avoid **1.0** MP (1376×768 exceeds the 768×1344 cap). H3 is trained near 1 MP; oversizing does not add detail." · `:126` "Templates open at **Megapixels** **0.4**: **864×480** at 16:9, **640×640** at 1:1 (the I2V default)." · `02v_docs_h3_native.txt:218` "round sides to 32" | ON-DISK (the 2026-10-24 "16 GB resolution row" is this row; the "16 GB" in `02v_docs_h3.txt:74` is a **model file size** column, not a VRAM row) |
| 26 | Frame grid `(frames-5) % 17 == 0` @ 24 fps | graph `length` inputs (124 / 243) | `02v_docs_h3.txt:148` "\| Frame grid \| `17k+5` at 24 fps (124 frames = 5 s) \|", `:142` "Templates expose `duration` in seconds, converted to frames on the `17k+5` grid at 24fps." · the same grid in the shipped node source `02v_core_nodes_minimax_head.txt:101,:105,:131` | ON-DISK. `(frames - 5)` as a literal string = 0 hits; the published form is `17k+5`, so the row's wording is now the published one. |
| 27 | Sampler / scheduler `res_multistep` + `simple` | `ksel`/`bsch` in the fixed graphs (`ali163_hc15_bd002_s51150011.api.json`) | `02v_docs_h3.txt:180` "Templates use **`res_multistep`** + **`simple`**." · `:182` "`res_multistep` is second-order multistep (first step is Euler). Splitting the schedule across two samplers drops multistep history..." · card `03y_mc_readme.txt:33` "res_multistep/simple 6-8 steps (my go-to for best motion quality)", `:39` "Euler/simple 4-8 steps" | ON-DISK |
| 28 | Steps | `s0_sched`/`s1_sched` in the graph (8 for s51150011/s51150021) | card `03y_mc_readme.txt:16` "It's a slow 8-12 step reference model in that configuration. 4step turbo loras can be run on top of it to reduce that." · docs `02v_docs_h3.txt:171` "* Simple shots: **12–16** steps often enough", `:173` "* Most motion/prompt gains by step **16**; little visible change past **50**", `:176` "Audio converges later than video in the joint denoise. Speech and timbre need **12+** steps; at **8** steps audio is oft…" | ON-DISK |
| 29 | Sigma shift 10 video / 3 audio | `m_shift` inputs in every graph | card `03y_mc_readme.txt:16` "Samples on 10/3 shift, fully dense or with Fastv2 VSA sparse node settings..." · the shipped node defaults are `shift_video` 12.0 / `shift_audio` 3.0, so 10/3 is the card's value, not a default | ON-DISK (card), OURS (we set it) |
| 30 | CFG / Guider "BasicGuider cfg 1.0, no negative prompt" | the graphs: 0 `cfg` keys in all 19 `p7/graphs/*.api.json` (measured, `inputs` scan) - there is no CFG to set; `BasicGuider` is on the model path | `02v_docs_h3.txt:192` "Insert between `UNETLoader` and `BasicGuider`; set `sage_attention` to `auto`", `:204` "...on the model path to `BasicGuider`" - the page names the node, it publishes no cfg value. The card on disk has **no** CFG text (`cfg` = 0 hits in `03y_mc_readme.txt`). `cfg 1.0` as a string exists in 6 bodies, all listings/LoRA text (`02v_civitai_2833322.json`, `03y_civ_multishot.json`, `08ca_loralab_readme.txt:529`) and in NO H3 docs or card body. | ON-DISK (node name) + UNSOURCED ("cfg 1.0" as community advice); our no-CFG shape is Forge-measured |
| 31 | `ref_image_size: "max"` | `scripts/comm.py` default (switched 2026-10-24) | `02v_docs_h3_native.txt:218` "**`ref_image_size`**: Default **`match`** (fit to canvas). **`max`** keeps 2048px short edge and is much slower; it does not upscale small files (round sides to 32). Pre-scale to 2048 short edge when needed" · shipped node source `02v_core_nodes_minimax_head.txt:267-268,:290,:301` | ON-DISK. The 2026-10-24 row dropped "is much slower" and "does not upscale small files" - both now quoted. |
| 32 | Anti-Burn LoRA on continuation clips @ 0.5 | clip graphs that carry the LoRA node | `02v_docs_h3.txt:157` "For longer chains, [H3-Anti-Burn-LoRA](https://huggingface.co/Imagineer13/H3-Anti-Burn-LoRA/blob/main/h3_antiburn_universal_v1.safetensors) on clips after the first at `strength_model` \~0.5 (tune for your continuation style)." · the LoRA card `02v_antiburn_readme.txt:31` "**Start at 0.5.** If faces still get crunchier from clip to clip, go up; turbos that burn harder need more." · `:46` "Face burn in this scene: **+52%** without the LoRA, **+6%** with it at 0.5." | ON-DISK |
| 33 | Sparse attention: VSA keep 10%, start 0.2; SLA avoided | `m_vsa` = BlockSparseAttention (`keep_percent` 10, `start_percent` 0.2, `end_percent` 1.0, `min_tokens` 12288, `extra_tokens` 256, `sink_conditioning: exact_kv_and_rows`) | docs `02v_docs_h3.txt:215` "FastH3 uses **`vsa`** at `keep_percent` **10**", `:210` "Defaults `start_percent` **0.2**, `end_percent` **1.0**. Later start (~~**0.4**) and earlier end (~~**0.9**) protect opening/closing frames." · card `03y_mc_readme.txt:16` "**SLA sparsity seems to destroy it, avoid using that on any workflows.**" · `02v_docs_h3_fastvideo.txt:110` "`keep_percent` 10 starting at 20%" | ON-DISK. `topk` = 0 hits in the card and 1 hit in an unrelated Qwen README, so "topk 0.1-0.2" is NOT published by H3 sources. |
| 34 | Frame interpolation / RIFE: none | all 19 graphs: 0 RIFE/interpolation nodes (measured class scan), fps 24 native | `RIFE` is in 8 bodies and **none is a recommendation**: `rd_llama_abl.html`, `rd_sd_pe.html`, `reddit_anatomy.html` (reddit threads), `civ_list_h3.json` (a Civitai search listing), `bq1_web_extract2.txt` (a Forge-made extract, not a source), and three `.403.txt` stamps (`hf2_live_reddit`, `pq1_reddit_comfy_search`, `pq1_reddit_sd_search` = blocked rows, never evidence). `RIFE` = **0 hits** in `01r_ls_comfyui.txt` and `02v_docs_h3.txt` (gates `aud1-ls-comfyui-no-rife`, `aud1-docs-no-rife`), so the "docs.comfy.org RIFE row" this doc cited on 2026-10-24 does not exist | OURS (measured absence in our graphs); no community row to match |
| 35 | Prompt structure: 6 sections | the prompt templates in `scripts/comm.py` and the six `p7/prompts/hc15/*.txt` | the 6 section names are published in the prompt-engineering cards: `02v_lightx2v_pe_readme.txt:61` (`non_diegetic_music`), `02v_pytraveler2_readme.txt:353,:355`, `02v_extender_readme.txt:379,:385,:392`, `02v_mc_disc63_page.html:109` | ON-DISK (the section list). `350-500 words` = **0 hits** in all 1,146 saved bodies - the length rule is ours (it is a Forge prompt-guide rule, see AGENTS.md L15), not community advice. |
| 36 | Review: `comm.guard_ok` pre-queue, objective metrics only, no vision judge on rendered explicit output | `scripts/comm.py:154` (reads the `prompt` key), `scripts/run_graph_job.py` (the only render path), `notes/rt_window_probe.py` | no community source: the adults gate and the no-vision-judge rule are Derrick's (fix_plan.md MAX block, 2026-10-23 6:12 PM CT "KEEP is Derrick's alone") | OURS (Derrick's rule) - the 2026-10-24 row cited the llama-swap README for it, which cannot support it |

## Key Findings (2026-10-27, replaces the 2026-10-24 list)
1. **Two rows asserted settings we do not run.** `--lowvram` and `--use-ck-attention` are not in the live
   ComfyUI launch command (`llama-swap.yaml:118,:130`), and `--kv int8` appears in no config on this box.
   A setup audit that marks a flag "match" must quote the command line it measured; this revision does.
2. **One row is a real conflict.** Comfy Kitchen attention "cannot run `int8_convrot` checkpoints"
   (`02v_docs_h3.txt:80`) and our checkpoint is `int8_convrot` - so `--use-ck-attention` as a global launch
   flag would be the wrong shape. The graphs set attention in-graph (`m_attn`), which is what `:204`
   prescribes. Recorded as CONFLICT, not "match".
3. **"16 GB" in the docs body is a model-file-size column** (`02v_docs_h3.txt:74`, the `pruned_w6a8` row),
   not a VRAM recommendation. The 2026-10-24 memory row read a VRAM recommendation into it.
4. **The Strata and health-timeout rows were the weakest**: the health range "120-1200 s" is in no body on
   disk (`120-1200` = 0 hits, gate `g-120-1200`), and the four Strata flags come from our own launcher
   config - no body mentions Strata (`Strata` = 0 hits) or llama.cpp's `--max-context` / `--vram-reserve-mib` /
   `--spec-min-p` (each 0 hits, gates `g-max-context`, `g-vram-reserve-mib`, `g-spec-min-p`). The llama-swap
   **groups** row looked unsupported to my first grep and is NOT: the page is on disk as `agy41_ls_groups.md` /
   `rt_ls_groups-and-matrix.txt` (row 7). Measuring a token in one filename prefix is not measuring the corpus.
5. **What the card on disk actually publishes** (3,698 B, md5 `6471e229…`, sha256[:16] `ba3be667bf67bba7`,
   63 lines, **five** byte-identical copies: `03y_mc_readme.txt`, `03y_mc_readme_main2.txt`,
   `hc15_tenstrip_readme.txt`, `agy51_tenstrip_readme.md`, `pq1_tenstrip_card.txt`; full line map in
   `notes/hc15_start_fidelity_audit.md` §CITATION AUDIT):
   shift 10/3, the 8-12 step reference configuration, the sampler list, "SLA sparsity seems to destroy it,
   avoid using that on any workflows", "No cache or spectrum if doing reference, they cause accuracy loss",
   the sampler/step list (`:29` er_sde/beta **4**, `:31` er_sde/beta57 **4-6**, `:33` res_multistep/simple
   **6-8** "my go-to for best motion quality", `:35` LCM/simple **6-8** "(best turbo audio)", `:37` LCM/beta
   **4-6**, `:39` Euler/simple **4-8**), `:24` "Non-turbo full step audio will always be better than audio on
   turbo versions." (no step count), `:22` "usually needing lower strength 0.2-0.6" for LoRAs on top, `:47-48`
   an external `10Eros-Max-h3-int8-convrot` link, `:52` beta_3/beta_4 are corrupted, `:54` the delta1024 base,
   `:63` the LTX 2.3 / Wan 2.2 / Krea 2 license terms, and
   "4step turbo loras can be run on top of it". It publishes NO topk number, NO "video-only", NO word-count
   rule, NO CFG/Guider sentence, NO 16 GB/VRAM row, NO "10Eros Max" benchmark, NO "12+ steps" (that is the
   docs page, `02v_docs_h3.txt:176`), NO "3 images of a character", NO "Ultra Mode", NO quantization recipe. (Those strings do occur in the
   wider corpus - `topk 0.1-0.2` in the TenStrip-derived quotes we inherited, `simple motion` in
   `civ_list_h3.json` - which is why the refuted rows are file-scoped BANNED rows, not "absent from the world"
   claims; a bare `topk` also matches an unrelated Qwen README, and `exclusive` matches "exclusively".)
6. **The 2026-10-24 "Key Findings" claimed `ref_image_size` was switched in `scripts/comm.py:108`** - the
   current default is in `scripts/comm.py` (this file cites it as OURS). The claim itself is true; only the
   citation style (a bare URL + the doc's "match" verdict) was the fault.

## CITATION AUDIT (AUD1, 2026-10-27) - how every row above was checked
Auditor (inline, run from `C:/AI/community/notes/web`, no new script file - Max 2026-10-26 "do not write
new scripts"): reads all 1,146 saved bodies (`.txt/.md/.json/.html` in `notes/web`, counted 2026-10-27) and prints, per token, how many bodies carry it and where:

```
python - <<'PY'
import io, os
tokens = ["lowvram","disable-async-offload","disable-pinned-memory","use-ck-attention","kitchen attention",
 "16 GB",">20GB","BasicGuider","cfg","RIFE","1344","Avoid **1.0** MP","17k+5","(frames - 5)","res_multistep",
 "8-12 step","10/3 shift","keep_percent","start_percent","ref_image_size","2048px short edge",
 "Qwen2.5-Coder-32B-Instruct","top_p 0.95","350-500 words","ignoreWebsockets","unloadTimeout","checkEndpoint",
 "120-1200","unload_delay","vram-reserve-mib","max-context","kv int8","spec-min-p","127.0.0.1:3489",
 "totalTimeout","contextThrottle","exclusive","group:","swap: true","taskkill","cmdStop",
 "much smarter","ModelSamplingModelPatch","Use 3 images","topk","video-only","simple motion"]
files=[f for f in os.listdir(".") if f.endswith((".txt",".md",".json",".html"))]
texts={f: io.open(f,encoding="utf-8",errors="replace").read() for f in files}
for t in tokens:
    hits=[(f,i+1) for f,tx in texts.items() for i,ln in enumerate(tx.splitlines()) if t.lower() in ln.lower()]
    print("%-28s %4d %s" % (t, len(hits), hits[:4]))
PY
```

0 hits across all 1,146 saved bodies (the UNSOURCED rows above): `lowvram`, `>20GB`, `Qwen2.5-Coder-32B-Instruct`,
`top_p 0.95`, `350-500 words`, `(frames - 5)` (published form is `17k+5`), `120-1200`, `unload_delay`,
`vram-reserve-mib`, `--max-context`, `--kv int8`, `--spec-min-p`, `127.0.0.1:3489`, `totalTimeout`,
`contextThrottle`, `taskkill`, `much smarter`, `ModelSamplingModelPatch`, `Use 3 images`, `topk 0.1`,
`video-only ON`. These 20 tokens are now the gate's `GLOBAL_ABSENT` list, so "0 hits" stays a measured fact and
not a claim: if a future fetch carries one, `GLOBAL-PRESENT` fires and that row stops being UNSOURCED.

**Five of my own 0-hit claims were refuted by the gate on 2026-10-27** (recorded, because AUD1 is about
citations that over-claim, and mine included): `16GB VRAM` (1 body: `pq1_civitai_h3_prompt_models.json`),
`RIFE` (8 bodies: 3 reddit threads, 1 Civitai listing, 1 Forge extract, 3 `.403.txt` stamps - 0 in the docs
pages, which is the claim the row actually needs), `cfg 1.0` (6 bodies, all listings/LoRA text, 0 in H3 docs or
card), `exclusive: true` (the llama-swap groups page IS on disk: `agy41_ls_groups.md:34`,
`rt_ls_groups-and-matrix.txt:34`), `simple motion` (`civ_list_h3.json`). Each of those five became a
file-scoped BANNED row ("not in the page the audit cited") instead of a corpus-wide absence.

**Paths cited by the old doc that do not exist on this box** (measured 2026-10-27):
`C:/AI/community/notes/pq0_sources/` (directory absent - the bodies live in `C:/AI/community/notes/web/`;
this is the row-owner's problem for the NOW section, logged in `notes/plans/aud1.md`),
`C:/Users/derek/.llama-swap.trial.bak`, `C:/AI/director/config/.llama-swap.yaml.bak-2026-10-22-170635`,
`.llama-swap.prev.yaml` (the flags live at `C:/AI/director/config/llama-swap.yaml:118,:121,:122,:130,:137,:139`),
`ComfyUI/templates/video/Minimax_H3/i2v.json`, and `C:/AI/community/scripts/sy_strata_launch.py`
(the launcher is `C:/AI/strata-0.2.2/sy_strata_launch.py`, called from `llama-swap.yaml:70,:79,:88`).

**The prior AUD1 plan file (`notes/plans/aud1-citation-repair.md`, 2026-10-27) carries invented quotes of
its own**: it attributes to the card `:14` "Beta 6 has made this model much smarter...", `:17` "For character
consistency: Use 3 images of the character...", `:24` "If you have a Guider and Sampling nodes, you only need
the ModelSamplingModelPatch node, no CFG." All three are **0 hits** in every saved body (the 3,698 B card on
disk has no such text; these are from the 15,125 B card revision that the gate's own docstring records as
gone). None of them was copied into this doc. Lesson: re-measure a quote in the body it cites, even when a
"measured" plan file supplies it (AGENTS.md L4).

**Gate**: `notes/ali02_citation_check.py` - the CITES list (133 rows, 46 added by AUD1, 0 problems) now carries
every verbatim quote this doc uses, the BANNED list (40 rows, 24 of them file-scoped rows added by AUD1) carries
every refuted string including the three invented card quotes from the prior plan and the nine `card-no-*` rows
that record the 15,125 B card sentences, `GLOBAL_ABSENT` (22 tokens over 1,146 bodies) carries the corpus-wide
0-hit list, and `SCAN_DOCS` includes this doc and `notes/hc15_start_fidelity_audit.md`, so a citation of a body
that is not on disk is a named failure. `--selftest` seeds all six detectors (MISSING-FILE, MISSING-TEXT,
BAN-HOLDS, DOC-MISSING, AUTO-CITE-MISSING, GLOBAL-PRESENT) and requires them to fire.

## Action Items
- 2026-10-24 (kept): `ref_image_size` switched from `"match"` to `"max"`; context window raised in the
  Strata config and pi `models.json` (the mixed 92160/128000 state is recorded in row 15).
- 2026-10-27 (this revision): citations resolved to files on disk; rows marked by verdict - 4 UNSOURCED
  (health range, `--kv int8`, the Qwen sampling params, the `127.0.0.1:3489` proxy), 13 OURS, 1 CONFLICT
  (Comfy Kitchen attention vs our `int8_convrot`), the rest ON-DISK with body + line + verbatim. Row 7 moved
  from UNSOURCED to ON-DISK and the corpus-wide 0-hit claims were scoped to the cited files - both were my own
  faults, found by the gate (table above).
- Next pass, not this one: run the same auditor over the NOW section of `fix_plan.md` (its rows cite
  `notes/pq0_sources/`, a directory that does not exist) and over `notes/now_h3_quality_research_20261025.md`.
- Standing suite at ship: `test_p6_review.py` 21 passed, `ali02_citation_check.py` 0 problems,
  `--selftest` fires, `ali05_loop_check.py`, `ali06_learnings_check.py`, `rt_window_probe.py --check`,
  `check_web_saves.py`, `ali11_run_checks.py --run` - see `notes/progress.md` for the numbers.
