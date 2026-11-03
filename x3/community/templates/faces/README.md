# templates/faces/ - one B2 + face-LoRA request template per FC_* identity (built 2026-11-03)

`<FC_ALIAS>.api.json` = `templates/b2.api.json` **plus one LoraLoader node and m_attn re-pointed unet -> lora**.
That is the same two-node diff proven on this box on 2026-10-30 (`../b2_fc_sydney_lora.api.json`, rendered ok).
`b2.api.json` is untouched: the generator asserts its text is byte-identical before and after, and refuses to run
if it ever carries a `lora` node of its own.

**Alias form (Derek, 2026-11-03).** A face's shared name is `FC_<FIRST NAME>` so a shared record says which face it
means. The first name is taken from the author's own published words for that LoRA; the trained phrase itself stays in
the private map and is injected at build time. `FC_SYDNEY` is the 2026-10-29 alias, unchanged.

| What | Value | Why |
|---|---|---|
| `lora_name` | `FC_<ALIAS>_h3_face_v1.safetensors` | the invented alias is the shared name for a face |
| `strength_model` | **1.0** | the owner's rule for this set (2026-11-03), set in the template, not per run |
| `strength_clip` | 1.0 | the 2026-10-30 value, unchanged |
| model chain | `unet -> lora -> m_attn` | the only changed node is `m_attn` (gated) |
| trigger phrase | **not in the template** | injected into the *prompt* at build time; a graph carries no such string |

**The prompt-side rule.** The words a face listens for (its trigger phrase) live only in the private lane: the map
`C:\Users\derek\sydney\tools\MANIFEST_fc_alias_h3_private.csv` and the record
`C:\Users\derek\sydney\notes\2026-11-03-fc-face-set-private.md` (the lane and the gitignored `runs/`, `review/`
dirs are the private home). `C:\Users\derek\sydney\tools\render_face_clip.py` reads the map, injects the words at a
`{TRIGGER}` token or at the head of the paste, and refuses to build if the face is not FIT, has no trigger words, the
frame count is off the `(frames-5) % 17 == 0` grid, or `C:\AI\locks\gpu-render.lock` exists. Prompt cards:
`h3_face_prompt_cards.md` here.

**Fit proof.** Every installed `FC_*_h3_face_v1.safetensors` scored 100 % key-map and 0 bad shapes against the
resident `10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors` with the L3 instrument
(`C:\AI\5slock\ralph-community\notes\_lora_l3\l3_fit_analysis.py`), with the 2026-10-30 face LoRA as positive
control. Instrument output: `C:\Users\derek\sydney\tools\h3_fc_fit_sweep.json`. No model was loaded for that proof.

**Regenerate** (adds a template for any new `FC_*` in `models/loras`, writes nothing else):

Note: 24 templates exist on disk, 23 are in git - the community `.gitignore` line 75 (`*sydney*`) keeps any path
containing that string out of the repo. Regenerate on this box, and re-run the generator after a clone.

```
C:\AI\director\.venv\Scripts\python.exe C:\Users\derek\sydney\tools\make_face_templates.py
```

**One clip** (builds, and with `--go` queues through `scripts/run_queue.py`, which takes the lock and the gates):

```
C:\AI\director\.venv\Scripts\python.exe C:\Users\derek\sydney\tools\render_face_clip.py \
  --fc FC_<ALIAS> --prompt-file <card.txt> --image community/<frame>_768x1344.png \
  --seed <n> --run-name face_<topic>_<YYYYMMDD> --frames 124 [--go] [--strength <for a labelled A/B only>]
```

**Open, for the skill owner:** `skills/h3-prompting` R31 caps face-LoRA strength at 0.2-0.6 from the 2026-10-30
test line. The 1.0 above is the owner's newer instruction for this set. R31 is Max's file, so it is not edited here;
`--strength` exists so an A/B of 1.0 against 0.6-0.8 is one flag away.
