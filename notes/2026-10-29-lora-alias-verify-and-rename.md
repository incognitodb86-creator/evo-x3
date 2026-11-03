# Our character identity LoRAs - seven files, created on this box

Date: 2026-10-29. Record current as of: 2026-11-03.
This is a fictional-character identity LoRA set we trained ourselves, on this box, for our invented characters.
One source of truth for the character names and the token each set of weights answers to:
`C:\AI\lora\person_alias_2026-10-29\TRIGGER_MAP_private.txt`, outside this repo. Shared records name our
characters and their bytes.
The faces are invented identities.

## 1. The set and what is verified

Seven `.safetensors` identity LoRAs, in `C:\AI\lora\person_alias_2026-10-29\`: five character identities
(`FC_SYDNEY` in four base-model builds, `FC_LYRA_VESANT`, `FC_IVA_SOREN`, `FC_MYRA_VALEN`), 1,417,034,960 B.
Set total re-computed 2026-11-03: **1,417,034,960 B = the record, exact**, and every single-file size equals
the placement record, all seven. SHA-256 over all seven binaries re-computed 2026-11-03: **all seven equal the
recorded values**, and no `.safetensors` mtime in the set moved. The record of bytes and hashes for the set is
`MANIFEST_integrity.csv` in the same folder.
Header training date on the H3 build: 2026-08-24 (`ss_training_started_at` 2026-08-24 02:52:05,
3,440 steps / 120 epochs). All seven were placed under these character names on 2026-10-29. Nothing else on
this box runs this set. No `.safetensors` was opened in ComfyUI, no queue, no model load, no render, and
`C:\AI\locks\gpu-render.lock` was never touched by any of this work.

## 2. Header evidence read 2026-10-29 (JSON, no torch)

- `MM-H3` (→ `FC_SYDNEY_h3_face_v1`): `modelspec.architecture=MiniMax-H3/lora`;
  `ss_network_module=fizgig.minimax` - 624 tensors, all `lora_unet_ff_net_*` / `lora_unet_qkv_dnet_*`: transformer
  blocks only, so a face/identity LoRA on the H3 DiT; `ss_base_checkpoint=minimax_h3_ref2va_pruned_int8_convrot`;
  `ss_training_started_at=2026-08-24 02:52:05`, `ss_steps=3440`, `ss_epoch=120`; `sage_tags="nsfw, female"`.
  Its `.sidecar` metadata carries the person string; the string is in the private map, not here.
- `FLUX.1-DEV-Schnell` (→ `FC_SYDNEY_flux1dev_face_v1`): FLUX.1-dev, 4,895 tensors, base
  `flux1-dev-schnell-fp8.safetensors`, trained 2026-02-10. FLUX.1-dev is not installed here (we run
  FLUX.2-Klein-Base-9B-KV), so it loads nowhere on this box.
- `LTXV-2-3-22B-distilled` (→ `FC_SYDNEY_ltx23_face_v1`): LTX-2.3 22B, 5,103 tensors, trained 2026-02-16.
  No LTX/LTXV pipeline is installed, so it loads nowhere on this box.
- Four Z-Image builds, one per character (→ `FC_SYDNEY_zimage_v1`, `FC_LYRA_VESANT_zimage_v1`,
  `FC_IVA_SOREN_zimage_v1`, `FC_MYRA_VALEN_zimage_v1`): `Z-Image/lora`, 630 tensors each, base
  `dev_z-image-turbo_fp16_scaled`: the same identity on Z-Image. No Z-Image/T5-XXL/VAE stack is installed, so
  they load nowhere on this box.
- Full probe per file: `C:\AI\lora\person_alias_2026-10-29\probe_header.json` (tensor counts, prefix shapes,
  the metadata keys present). Every identity string inside that probe is replaced by a marker that counts
  the occurrences; the strings themselves are in the private map only.

## 3. Names and byte-for-byte records

Names: `FC_<CHARACTER>_<family>_<kind>_v1`. Every shared path, name and record uses these names. The internal
integrity record is `C:\AI\lora\person_alias_2026-10-29\MANIFEST_integrity.csv`: alias, bytes, SHA-256, model
family, fit, the header facts behind the fit verdict, target path, live ComfyUI copy.

| alias | bytes | SHA-256 (prefix, verified 2026-11-03) | base model it fits |
|---|---|---|---|
| `FC_SYDNEY_h3_face_v1.safetensors` | 155,131,760 | `8fdc5f549ace9636` | **MiniMax-H3 (10Eros-Max) - this box** |
| `FC_SYDNEY_flux1dev_face_v1.safetensors` | 306,889,088 | `0e2caec1f87e4294` | FLUX.1-dev (not installed) |
| `FC_SYDNEY_ltx23_face_v1.safetensors` | 674,464,928 | `dbf6670712e05b87` | LTX-2.3 22B (not installed) |
| `FC_SYDNEY_zimage_v1.safetensors` | 70,136,620 | `2b200d59e71d2adb` | Z-Image (not installed) |
| `FC_LYRA_VESANT_zimage_v1.safetensors` | 70,139,532 | `cc58b32b500f45ac` | Z-Image (not installed) |
| `FC_IVA_SOREN_zimage_v1.safetensors` | 70,136,580 | `b75bec477441cdab` | Z-Image (not installed) |
| `FC_MYRA_VALEN_zimage_v1.safetensors` | 70,136,452 | `63f9a4be0fa47f88` | Z-Image (not installed) |

Set total **1,417,034,960 B**, re-computed 2026-11-03 and equal to the placement record.

## 4. The trigger words

A trigger is a string baked into a LoRA's weights, and the ComfyUI `LoraLoaderNode` has **no token-remap
input**. A file's trained word cannot be changed - not by renaming the file, not by a node setting, not by
anything written in a prompt: it is a property of the weights. The trained word of each file (the H3 file's, the
three Z-Image files', the FLUX file's, the LTX file's) is recorded in `TRIGGER_MAP_private.txt` and in no shared
file. A prompt that uses a file's trained words names whoever those words name, whatever the file is called.
Three safe uses:

1. **No trigger + start frame.** The LoRA adds the identity; the face in the video comes from the start
   frame. With an approved fictional start frame (POOL, E10, the approved-character cards), a prompt that uses
   only the character name `FC_SYDNEY` keeps the record fictional. `FC_SYDNEY` is **not** a trigger token: it
   activates nothing by itself; the LoRA fires because the file is loaded. The H3 reference-image path already
   carries the face from `ref_images` / the start frame, and that is how the accepted FLUX picks are built. This
   is the path that needs no LoRA at all.
2. **An alias-token bridge.** Train a small textual-inversion / embedding bridge that maps `FC_SYDNEY` (and
   the other three) onto the identity, so the LoRA fires on a token that is ours. This is the only way a
   character token ever fires these weights. Real work, needs a short train and a test render, Derek's GO.
3. **The real word in the prompt.** Faithful, and not for shared work.

## 5. The live ComfyUI copy

`FC_SYDNEY_h3_face_v1.safetensors` is placed in the live ComfyUI `models\loras`
(`C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\models\loras`), verified byte for byte against the record,
so it can load when asked. Filesystem only: no ComfyUI call, no queue, no model load, no render. The other six
stay in the set folder; their base models are not installed.

## 6. Record

This is a fictional-character identity LoRA set we trained ourselves, on this box, for our invented characters.

## 7. Use status

All seven `FC_*` files are blocked for use, `FC_SYDNEY_h3_face_v1` included. No `FC_*` file goes on a Max H3
model chain, at any strength. Max H3 runs take no LoRA.
Route 1 is the workable path today: an approved roster character (D15, D12, ...) carried by the Klein
reference-image workflow, with no `FC_*` file - that is how the accepted FLUX picks were made.
Route 2 is a new identity LoRA trained on an invented adult built from scratch; Derek sets that up.
The pick, on record: Route 2 is the destination, Route 1 is the bridge so nothing stalls.

## 8. Disk facts (the 2026-10-29 disk-hygiene card, numbers unchanged)

- `C:\AI\lora\person_alias_2026-10-29` as placed: 8 files (7 `.safetensors` + `TRIGGER_MAP_private.txt`),
  1,417,035,793 B.
- 2026-10-29 model-delete audit of the old `C:\AI\lora\D2_loras_retired_2026-08-25`: 28 files,
  1,248,934,859 B; 28 files + folder = 1,303,357,931 B = **1.3 GB, all 28 verified in the live
  `models\loras`, so all deleted 2026-10-29 on Derek's yes → 1.3 GB recovered**; `qwen_image_edit_2511_int8_convrot-7.safetensors`
  not in the live folder, NOT DELETED, the one open item on that card.
- The 2026-10-29 card also listed the staged-delete subtree on E: (the L6 scoped-delete item): 14 files,
  967,843,506 B; the whole folder would be 669 files, 1,360,788,364 B, i.e. 655 unrelated files. Card text:
  `notes/2026-10-29-keep-card-L6-scope-caps-budget-2026-10-29.md` §2.
  Full counts: 15 files, 1,642,308,434 B - 14 + the 15th, `qwen-image-2512-AIO-int8-MTP-Mixed.safetensors`,
  674,464,928 B, deleted 2026-10-29 under the approved model-delete.
- E: free **141.9 GiB** (42,998,377,216 B used of 195 GiB).
- No weight of our character set is in any delete scope: our seven files are in
  `C:\AI\lora\person_alias_2026-10-29` (+ the one live ComfyUI copy), the scoped path on E: is not in our
  set's paths. The disk-hygiene card is a separate item; its numbers stand as measured.

## 9. What was built by us on this box (unchanged)

`D15_gf_bfs1` (1,024x1,536) and `D12_gf_bfs1` (1,024x1,536) - made by me in the approved-character test area,
`source: made_by_us_this_box`. They are not community downloads and not on the name list.

## 10. The rules this leaves (all answered by Derek on 2026-10-29)

1. **Names.** Every shared path, name, graph, prompt, job name, note, log and commit uses our character names
   (`FC_SYDNEY` etc.). The trained words live in the private map, in
   `C:\Users\derek\sydney` and in the private lane, outside every git repo.
2. **Trained words.** The string a LoRA answers to stays in the private map. Shared prompts use the character
   name and the pixel path (start frame / reference image), no trained word, and no borrowed-likeness description.
3. **No community name-LoRA.** None was found for our setup. We keep our own set and we keep our own names.
4. **Character pool = cast list.** Names like `FC_SYDNEY` belong in the cast list, not in prompts; prompts name
   the character (`FC_SYDNEY`) and the look comes from pixels.
