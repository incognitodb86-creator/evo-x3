# b2_fc_sydney_lora.api.json - the B2 template plus one face LoRA (a diff, not a replacement)

Created 2026-10-30 13:29 CT on Derek's instruction in the talk lane: *"Make a diff be template with fc syd lora
don't overwrite b2"*. **`templates/b2.api.json` is untouched** - it is still the default recipe (sha256
`124fb1331874f27803e95c81db67fe270b30dd5533732d7032105839dfd81ca2`, the hash in `b2.README.md`). The generator
script asserts that hash before and after it writes, so running it cannot change the default.

Built by `C:\AI\community\scripts\make_b2_lora_template.py` (run it to regenerate; it prints a gate list and
`RESULT PASS`). This file's sha256 after the 2026-10-30 build: `fdd5eed50a761c1c465240a92856820a410a5fc0d731c5268062ba72299d46ab`
(20,098 bytes, CRLF, same bytes style as `b2.api.json`).

## The diff (exactly two changes, checked by the generator)
| What | Node | B2 | this template |
|---|---|---|---|
| Face LoRA | `lora` (new, `LoraLoader`) | absent | `FC_SYDNEY_h3_face_v1.safetensors`, `strength_model 0.7`, `strength_clip 1.0`, `model: ["unet",0]`, `clip: ["clip",0]` |
| Model chain | `m_attn.inputs.model` | `["unet",0]` | `["lora",0]` (unet -> lora -> ModelAttentionBackend) |

26 nodes -> 27. Nothing else differs: the generator asserts no drift outside `lora`/`m_attn`, that every B2 locked dial
is identical, and that a self-destruct probe fires on `b2.api.json` (no `lora` node, `m_attn.model = unet`).
Wiring proven by a rendered cell on 2026-10-30: `runs/bj_pov_20261030/b5_s51083020_lora` (builder
`C:/Users/derek/sydney/work/bj_pov_20261030/build_bj_pov_b5_lora.py`).

## Per run (unchanged from B2 - `make_b2_request.py` already takes `--template`)
    C:\AI\director\.venv\Scripts\python.exe C:\AI\community\scripts\make_b2_request.py \
      --template C:\AI\community\templates\b2_fc_sydney_lora.api.json \
      --arm-dir <run dir>\<tag> --prompt-file <txt> --seed <n> \
      --image community/<file>.png --prefix community/<run>/<tag> [--frames <n>]

The five per-run placeholders (`c0.prompt`, `noise.noise_seed`, `img.image`, `save.filename_prefix`, `c0.length`)
are left in this file exactly as in B2, and the generator checks they are present, so requests are built the same
way as for the default recipe. Frames stay a per-run choice; `--frames` must equal `c0.length` and be passed to
`run_graph_job.py` / `run_queue.py`.

## LoRA notes
- File: `FC_SYDNEY_h3_face_v1.safetensors` (155,131,760 B, sha256 head `8fdc5f54`), `modelspec.architecture = MiniMax-H3/lora`,
  `ss_base_checkpoint = minimax_h3_ref2va_pruned_int8_convrot`, dim 16 / alpha 16 - the only one of the seven character
  LoRAs that fits this base model (`notes/2026-10-29-lora-alias-verify-and-rename.md` §2).
- Strength 0.7 is inside the face range 0.6-0.8 for a merged beta7 (`C:/AI/lora/person_alias_2026-10-29/h3/USAGE_FC_SYDNEY_h3.md`);
  drop to 0.4 if it fights the merge. No general NSFW LoRA on beta7 (h3-prompting R31).
- Trigger hygiene (R31): this LoRA carries a trained trigger string; it is recorded in the private
  `C:/AI/lora/person_alias_2026-10-29/TRIGGER_MAP_private.txt` and is named in a prompt **only** for a request built
  from this template, never for a plain B2 request. Which prompts name it is Derek's call; his standing rule for the
  shared trail is that the trained token stays in the private file and only the character name appears in shared names
  and shared notes, so prompt files for this template
  live in the talk lane (`C:/Users/derek/sydney/prompts/`), and run dirs are gitignored.
- Measured effect of this LoRA on one earlier cell (`notes/2026-10-30-bj-pov-three-methods-DONE.md`): at 0.7 with no
  trigger and no face in frame 0 it moved face similarity by noise (+0.0002 mean); the start frame is the driver of
  face fidelity. Use this template where the start frame carries the face, and expect the trigger path to be the
  stronger one.

## Not changed
`b2.api.json`, `b2.README.md`, `make_b2_request.py`, every run graph already rendered, and the default in every
brief. To render without the LoRA, use the plain B2 template as before.
