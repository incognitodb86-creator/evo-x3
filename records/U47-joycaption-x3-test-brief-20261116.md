# U47 — JoyCaption Beta One on the X3 for a side-by-side test (Derrick t1985s7307 "Yes, set up JoyCaption on the X3 for a test")

Owner: Max Architect. Executor: agy gemini-4-hydrogen-high on evo-X3. T1.

## Goal
JoyCaption Beta One (GGUF Q8_0 + f16 mmproj, the same files AlienPc's llama-swap uses: C:\AI\models\joycaption\Llama-Joycaption-Beta-One-Hf-Llava-Q8_0.gguf and llama-joycaption-beta-one-llava-mmproj-model-f16.gguf, ~8.8 GB total) served by the X3 llama-swap next to gemma4-heretic, plus a small script that captions pictures Derrick marks in PixlStash so he can compare them with Gemma's tags.

## HARD RULES
- Never view, print, cat or summarize picture contents, tags, captions or person names. Counts and exit codes only. Never cat /home/evo/AI/pixlstash-tagging/unmatched-person-names.txt.
- No secrets on argv or in logs. Never print tokens/passwords/LLAMA_SWAP_KEY. Read keys from existing files (/etc/evo-x3/llm.env, /home/evo/.config/pixlstash/*.token) inside the program.
- Getting the files: COPY from AlienPc using an access path that already exists (existing ssh/scp key, an existing share, or Taildrop that AlienPc initiates). If none works without new credentials or new access, use the HF download ONLY if the repo is the official JoyCaption Beta One GGUF and the total is <= 10 GB, and note it in RESULT; otherwise stop BLOCKED. Verify size and, if published, SHA256.
- Put files in /srv/models/joycaption/ (root-owned, same perms as other model dirs). Add a line to /srv/models/SHA256SUMS.
- Do not touch Windows partitions, the USB X3BACKUP, BIOS, Tailscale settings, or PixlStash settings. No git add -A. No force push.
- llama-swap: back up /etc/evo-x3/llama-swap.yaml to llama-swap.yaml.bak-20261116-u47-pre first. Add a `joycaption` model using the same podman/toolbox image pattern as gemma4-heretic, settings from the model card / AlienPc entry (ctx 4096, temp 0.6, top_p 0.9, -fa on, all layers on GPU). Put it in the NON-exclusive group (swap:false/exclusive:false, like embed-small) so gemma4-heretic stays loaded; do NOT add it to the exclusive main group. Validate the yaml (llama-swap config check or a dry parse) before restarting.
- Restart llama-swap ONCE, and only after ~/evo-x3/records/U46-RESULT.md exists (U46 owns the tagger restart; wait for it, polling at most every 2 min, max 90 min, then stop BLOCKED). The Gemma tagger will lose a few in-flight pictures during the restart; that is accepted. Confirm gemma4-heretic answers again and the tagger's done count resumes rising within 5 min.
- Never queue anything on AlienPc ComfyUI.

## Steps
1. Copy/verify the files (rules above).
2. Add the llama-swap entry + restart (rules above). Smoke test: one text-only request and one request with a synthetic test image you generate (e.g. a solid-color PNG made with PIL) — never a library picture. Record load time, tokens/s and RAM.
3. Write /home/evo/AI/pixlstash-tagging/joycaption_compare.py (owned by evo):
   - Finds pictures carrying the PixlStash tag `jc-test` (Derrick adds this tag to ~20 pictures himself).
   - For each, sends the picture (max edge 1280, same as tag_runner) to llama-swap model `joycaption` twice: (a) the PixlStash JoyCaption tag prompt "Generate only comma-separated Danbooru tags. Only add general tags. Include counts (1girl), appearance, clothing, accessories, pose, expression, actions, background." and (b) the official JoyCaption descriptive prompt "Write a long detailed description for this image."
   - Writes (a) as tags prefixed `jc ` (e.g. `jc cowgirl_position`, max 40) and (b) to a 0600 file /home/evo/AI/pixlstash-tagging/jc-compare/<picture_id>.txt, so it never overwrites Gemma's tags or PixlStash's description. Idempotent (skip pictures already done unless --force). --dry-run prints counts only.
   - Prints counts only: pictures found, done, failed, seconds per picture.
   - py_compile it. Run it with --dry-run. If 0 pictures carry jc-test yet, that is expected: stop there.
4. Write ~/evo-x3/records/U47-RESULT.md: PASS/BLOCKED, how the files were copied, sizes/hashes, yaml diff (no keys), restart time, smoke-test numbers, the tagger done count before/after the restart, script path and usage, and the exact one-liner Derrick's bot runs after he tags pictures `jc-test`.

## STOP CONDITION
Write U47-RESULT.md and stop. Do not run the compare on real pictures.
