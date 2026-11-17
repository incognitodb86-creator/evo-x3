# templates/faces/ - B2 + one face LoRA, per fictional character (built 2026-11-03)

One template per installed face LoRA: `<FC_ALIAS>.api.json` = `templates/b2.api.json` **plus one `LoraLoader` node,
with `m_attn` re-pointed `unet -> lora`**. `b2.api.json` is untouched (the generator byte-asserts it and refuses to
run if it ever carries a `lora` node). The same two-node diff was proven on this box on 2026-10-30.

- `FC_*` is a **fictional character**. The alias is `FC_<FIRST NAME>` so a shared file says who it means.
- The trigger word is **the person's actual full name** (the phrase the LoRA was trained on). It lives only in the
  private map
  `C:\Users\derek\sydney\tools\MANIFEST_fc_alias_h3_private.csv`, and the builder injects it at a `{TRIGGER}` token
  (or at the head of the paste). Never type it into a shared card, prompt, graph, note, log or commit.
- `strength_model` **0.7**, `strength_clip` 1.0 - the owner's setting for this set (Derek, 2026-11-03), measured the
  same day: three faces, one seed, the dial only (`prompt_sha256` identical per face) gave **0.7 >= 0.9 > 1.0**, so
  the top of the dial washes the face it should impose. `--strength` is there for a labelled A/B cell.
- Fit: 25/25 FIT (the set plus the 2026-10-30 face LoRA as positive control), 100% key-map and 0 bad shapes against
  the resident `10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors`, with the L3 header instrument
  (`C:\Users\derek\5slock\ralph-community\notes\_lora_l3\l3_fit_analysis.py`). No model load, no GPU. Output:
  `C:\Users\derek\sydney\tools\h3_fc_fit_sweep.json`.
- The builder refuses a face that is not FIT, has no trigger words in the map, asks for off-grid frames
  (`(frames-5) % 17 == 0`: 124, 243, 510, 1422), or finds `C:\AI\locks\gpu-render.lock` held.
- 24 templates on disk, 23 in git: `.gitignore` line 75 (`*sydney*`) keeps that one path out of the repo.
  Regenerate after a clone.

**Regenerate** (adds a template for any new `FC_*` in `models/loras`, writes nothing else):

```
C:\AI\director\.venv\Scripts\python.exe C:\Users\derek\sydney\tools\make_face_templates.py
```

**One clip** (builds; with `--go` it queues through `scripts/run_queue.py`, which takes the lock and the gates):

```
C:\AI\director\.venv\Scripts\python.exe C:\Users\derek\sydney\tools\render_face_clip.py \
  --fc FC_<ALIAS> --prompt-file <card.txt> --image community/<frame>_768x1344.png \
  --seed <n> --run-name face_<topic>_<YYYYMMDD> --frames 124 [--go] [--strength <A/B only>]
```

Prompt cards: `h3_face_prompt_cards.md` here. Records, maps and test runs: `C:\Users\derek\sydney\`.
**Open, for the skill owner:** `skills/h3-prompting` R31 caps the in-paste face weight at 0.2-0.6 from the
2026-10-30 test line. The graph dial here is 0.7, just above that cap, and it is the measured optimum for these
files on this base (0.1 gives no face at all, 0.5 gives a type, 1.0 washes it). R31 is Max's file, so it is not
edited; `--strength` keeps every A/B one flag away, and the number goes in the run record.
