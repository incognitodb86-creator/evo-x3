# Where FC_SYDNEY_h3_face_v1 came from (2026-11-03)

Read-only check. No GPU, no lock, no download, no delete. Names of real people stay in the private set folder; here the character is named.

## Question
Derrick asked where our `FC_SYDNEY_h3_face_v1` LoRA came from.

## Answer, in one line
We did not train it: it is a community H3 face LoRA that already sat on this machine's own backup, and it is byte-identical to a public Hugging Face repo in the profile surveyed today.

## The chain, with the instruments
| Step | Fact | Evidence |
|---|---|---|
| 1 | The file we use is `C:\AI\lora\person_alias_2026-10-29\h3\FC_SYDNEY_h3_face_v1.safetensors`, 155,131,760 B | measured, `sha256sum` on 2026-11-03 |
| 2 | Its SHA-256 is `8fdc5f549ace9636591badba3253f9a86d226b7106d1de9692020e191c33da04` | measured, same run; matches the Oct 29 and Nov 2 records |
| 3 | It was **copied on 2026-10-29** out of the 2026-10-26 C-drive backup, from a folder of LoRAs marked not in use on 2026-10-09 and staged for deletion on 2026-10-17, under the original name `MM-H3 - <person>.safetensors`; a byte-identical twin with an underscored name was skipped as a duplicate | `C:\AI\lora\character-set-private-2026-11-03\MANIFEST_alias.csv` row 1, tool `lora_alias_copy_2026-10-29.py` |
| 4 | The file's own header says community training, not ours: `ss_network_module=fizgig.minimax`, base `minimax_h3_ref2va_pruned_int8_convrot` (int8), dim 16 / alpha 16, 624 tensors, trained **2026-08-24**, 3440 steps / 120 epochs | `probe_header.json` in the set folder; recorded in the Nov 2 integrity refresh |
| 5 | The same SHA-256 and the same 155,131,760 B appear in the public profile `Playtime-AI` as its H3 face LoRA, repo created 2026-08-24, license `apache-2.0`, with the file published under the name `MM-H3 - <person>.safetensors` | `https://huggingface.co/api/models/Playtime-AI/Minimax_H3-<person>?blobs=true`, read 2026-11-03; same survey record `notes\2026-11-03-playtime-ai-hf-survey.md` |

Byte identity is the proof: same size, same SHA-256, same published file name, same training date in the header. So the LoRA entered this machine as a community download long before 2026-10-29, and 2026-10-29 only gave it our character's name.

## What the same manifest shows for the rest of the FC_* set
All seven files came from that same backup subtree as copies, with hashes verified. The three Z-Image character LoRAs are renamed Z-Image face LoRAs of three other real people, and the FLUX.1-dev and LTX-2.3 builds are renamed community builds of the same face as the H3 file. Six of the seven load on no base this box has.

## The record conflict to settle
`C:\AI\lora\person_alias_2026-10-29\README.txt` states the set is fictional-character LoRAs we trained ourselves on this box. The bytes say the set was adopted, not trained: the training happened elsewhere, on 2026-08-24 and earlier, by community authors. The invented-character framing is ours and stays; the training claim is a fact the file headers contradict. The worded fix is Derrick's call, options in chat.

## Why it matters for today's work
- Face strength 0.6-0.8 is the ceiling of a third-party rank-16 identity adapter, trained on another int8 H3 build; on our merged beta7 it bends the face, it cannot rebuild it. That fits the report that the mouth clip at 0.8 is still not the character.
- `apache-2.0` means using and testing these weights is allowed.
- The same public profile has 19 more H3 face LoRAs of the same shape and size class, so they are siblings of the file we already run: any of them is a one-file, ~148 MiB test, and each needs Derrick's GO.

## Private trail
The trained words, the exact source file names and the old disk paths live only in `C:\AI\lora\character-set-private-2026-11-03\` (`MANIFEST_alias.csv`, `README.md`) and in the lane record `C:\Users\derek\sydney\notes\2026-11-03-fc-face-set-private.md`. Nothing in that folder was changed today.
