---
name: h3-parody-identity
description: >-
  INDEX + RefMod celebrity/character parody lane for MiniMax H3 — use when asked
  for a parody video of any named character, actor, or celebrity on single-pass
  768x1344 B2 (beta7_int8HQ, no RefLoRA, no 2-pass, no voice ref), including
  autonomous 1-clip chat execution from C:\AI\render.
---
# H3 parody / identity lane (INDEX + RefMod)

Community way (Malcolm Rey, HF `malcolmrey/various` h3-center docs, Sep 2026): RefMod usage is a **separate** guide from base H3 prompting. With RefMods loaded, skip positional `<Picture N>` identity tags and put the **name + biometric description** in `subject_definitions`. Full reference and history: `/workspace/cos/brain-staging/10_packs/max/h3-parody-identity-reference.md`.

## When to load

- Derrick asks in chat or brief for a named character / actor / celebrity likeness parody video (e.g., *"Give me a parody video of Jennifer Check in a random scenario."* or *"Give me a parody video of Sydney Sweeney."*).
- Resolver hits INDEX `good` / `bad` / `onthefence` (`onthefence` = treat like `bad`).
- Any run that loads `MiniMaxH3RefModsLoader` for identity.

Do **not** load for ordinary approved-still REF2VA pastes that only use `<Picture N>` refs — those stay on `h3-max-ref2va-prompt` + `h3-prompting`.

## Locked baseline & hard bans (Derrick, Nov 5–6, 2026)

1. **Single-pass `768x1344` (`4bc9bba` / `ab72d88`, `templates/b2_refmod.api.json`)**: `8` steps (`euler` / `simple`, `shift` `12.0` video / `3.0` audio) on `10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors` + `MiniMaxH3RefModsLoader` (`strength_1: 1.0`) → `MiniMaxH3RefModApply` (`retention: 1.0`). **No `RefLoRA`, no `2-pass` upscaler, no `ref_audio` / voice ref, and no start photo by default.** Any new flag, node, or input requires Derrick's yes on a 1:1 question card first.
2. **Stills / conds / refs only from `approved_characters`.** That folder is the whole likeness gate (movie/TV screenshots OK once in the pool after the one-time adults-only check). Never touch `C:\Users\derek\sydney\`, `talk-persona.md`, or `SYDNEY` still paths — note that single-pass RefMod parody runs use `stills=[]`, so celebrity names like *"Sydney Sweeney"* are valid RefMod/INDEX lookups, not local `SYDNEY` persona files.
3. Image/adults-only rules live only in `C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\LANE_IMAGE_RULES.md` (linked from `C:\AI\render\AGENTS.md`) — never add Forge global `AGENTS.md` rules without Derrick's card yes.
4. KEEP dials unchanged (`B2` / REF2VA 10strip eros beta7 stock). Max 8 RefMod slots (`mod_1…mod_8`; unused = `(none)`).

## INDEX status → what is native

| INDEX status | Face / look | Voice |
|---|---|---|
| **good** | H3-native from the name (still apply INDEX + matching RefMod + description) | native |
| **bad** / **onthefence** | look from RefMod (name alone is not enough for look) | native voice works from name |

Always apply **both** INDEX resolution and RefMods (never RefMod-only or prompt-only). When character and actor both resolve, stack both matching RefMods + INDEX assets (cap at 8 slots: keep character matches and highest INDEX status first). `submit_parody_run.py` fails closed before creating `run_dir` if an `index:bad` / `onthefence` / `none` identity has no installed `.safetensors` in `C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\models\refmods`.

## Prompt shape (`build_request.py`)

```text
subject_definitions:
(S1) <Character or Celebrity> - an adult performer, age 28+, featuring <Character/Actor clause>, <facial + hair + scenario wardrobe description>, styled in <parody> tone.

summary:
(S1) <scene summary>. Adult cast, adults-only, fictional 18+ adult scene. Non-speaking characters: none. No singing, no rapping, no songs, no music, no narration, no voice-over.

detailed_description:
[static medium shot, eye level, 50mm lens, shallow depth of field]
(S1) <scene summary / active pose>, late afternoon ambient lighting, soft key on face, subtle fill. Camera locked off, no zoom, no pan.
<scenedirect>
(S1): <d>[English in <Character or Actor>'s natural speaking voice] <spoken words only></d>
</scenedirect>
She holds eye contact, gives a small nod at the end, and stops talking. Her mouth movements stop completely after the sentence. Her speaking voice, accent and cadence are the one natural voice she uses in this scene, used consistently in every clip of this character.

overall_soundscape:
quiet room ambience, soft natural room tone; the single close-micd human voice in the foreground.
no_dubs: no extra dubbing, no studio VO, no dubbing actors, no voice actors.
No music, no songs, no score, no soundtrack.
```

1. **Full facial, hair & scenario outfit in `--description`:** Write concrete celebrity facial features (eyes, brows, cheekbones, lips, skin tone), hair color/cut/styling, and scenario-matched adult wardrobe. Do **not** begin `--description` with `"featuring"` (`resolve.py` prepends the `featuring` header automatically, and `build_request.py` dedupes accidental repeats).
2. **Open scenario pose & adult setting in `--scene`:** Write a concrete adult setting (e.g., velvet cocktail lounge, penthouse balcony, upscale hotel bar, marble vanity dressing room, neon diner booth) and natural body language/head/eye action. Let `--scene` carry specific lighting when you want it (e.g. `2 AM neon booth light`, `warm vanity bulbs`) — the builder then drops its default late-afternoon lighting. **Never** use minor-coded words (`girl`, `teen`, `school`, `high school`, `cheerleader`, `dorm`, `student`) — `comm.guard_ok` blocks them on every submit.
3. **Spoken words only in `--dialogue`:** Voice framing prefers `--character` when given (`[English in Jennifer Check's natural speaking voice]`) and falls back to `--actor` / `--name` (`[English in Sydney Sweeney's natural speaking voice]`). Keep spoken lines ~8–15 words so speech ends cleanly inside `124` frames with natural mouth closure. Never include timestamps (`t=0`, `00:00`), `<d>` tags, backticks, `"No speech"`, or `"room tone"` — `build_request.py` rejects stage cues. Omit `--dialogue` only when a silent clip is requested.
4. **Prop-anchored hands (always):** Anchor hands on a concrete prop in `--scene` (`holding a cocktail glass stem`, `holding a makeup brush`, `holding a purse strap`, `holding a phone edge`, `fingers on a jacket lapel`) or keep them relaxed in the lap / at her sides. Never write open fingers splayed on hips, counters, or tabletops — they warp in 8-step single-pass H3.
5. **No duplicate tone:** Do not write `styled in (a) satirical adult parody tone` inside `--description`; `resolve.py` already appends the tone clause (`build_request.py` collapses repeats as a safety net).

## Autonomous chat execution recipe (Forge in `C:\AI\render`)

When Derrick asks in chat for a parody video of a named character or celebrity, his message **is** the go for **one `124`-frame (~5.2s) `768x1344` clip** (`LANE_IMAGE_RULES.md` / `fiction-cond-lock` rule 3). Do **not** ask to stage first unless he asks for a multi-clip batch or a missing model download.

**Fast path — one tool call after this skill loads.** `submit_parody_run.py` already resolves `aliases.json`, `INDEX.md`, and installed `RefMods` in Python. So for a named parody clip, do **not** spend turns reading or grepping `aliases.json`, `INDEX.md`, `resolve.py`, or `comm.py`, and do **not** load `h3-hc-render` or `h3-prompting`. Go straight from this skill to step 1 and then the single PowerShell call in step 2. Only read `aliases.json` / list `RefMods` if Derrick explicitly asks what characters or RefMods exist, or if `submit_parody_run.py` fails on an unknown spelling.

1. **Map the name and invent the details in your head (no tool call):** Character name given (e.g. `Jennifer Check`) → `--name "Megan Fox" --character "Jennifer Check" --actor "Megan Fox"`; celebrity alone (e.g. `Sydney Sweeney`) → `--name "Sydney Sweeney" --actor "Sydney Sweeney"`. If Derrick gives only a name or a loose scenario, invent a fitting adult satirical scenario, scenario-matched outfit, prop-anchored pose, and witty spoken line in character.
2. **Submit, wait, copy MP4, and upload to QNAP in ONE blocking PowerShell call** (never detach and return to the LLM mid-render — an LLM turn while ComfyUI holds the GPU evicts `comfyui_auto` from VRAM; avoid shell redirects in command strings):

```powershell
$ts = Get-Date -Format 'yyyyMMdd_HHmmss'
$runName = "parody_<slug>_$ts"
$runDir = "C:\AI\community\runs\$runName"
$py = 'C:\AI\director\.venv\Scripts\python.exe'
$argsList = @(
  'C:\AI\community\scripts\parody\submit_parody_run.py',
  '--name', '<Actor or Celebrity>',
  '--actor', '<Actor or Celebrity>',
  # include '--character', '<Character>' when a character is named
  '--tone', 'satirical adult parody',
  '--frames', '124',
  '--run-dir', $runDir,
  '--description', '<concrete facial features, hair, eyes, lips, and scenario-matched adult outfit>',
  '--scene', '<adult setting, optional specific lighting, natural pose/expression, hands holding a prop or relaxed in lap>',
  '--dialogue', '<spoken words only, ~8-15 words>'
)
& $py @argsList
if ($LASTEXITCODE -eq 7) { Write-Output 'STOP: GPU_BUSY rc=7'; return }
if (-not (Test-Path (Join-Path $runDir '_render_order.json'))) { throw "submit_parody_run stopped before queueing (check missing RefMod or guard error above)" }
Get-Content -Raw (Join-Path $runDir 'prompt.txt')
$qlog = Join-Path $runDir '_render_queue.log'
for ($i = 0; $i -lt 150; $i++) {
  if ((Test-Path $qlog) -and (Select-String -Path $qlog -Pattern 'BATCH closed rc=' -Quiet)) { break }
  Start-Sleep -Seconds 4
}
Get-Content -Tail 5 (Join-Path $runDir 'status.log')
Get-Content -Tail 3 $qlog
$comfyOut = Get-ChildItem "C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\output\community\$runName" -Filter 'clip*.mp4' | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$finalMp4 = Join-Path $runDir 'clip.mp4'
Copy-Item $comfyOut.FullName $finalMp4 -Force
& $py 'C:\AI\community\scripts\pi_qnap.py' put $finalMp4 "pi-drop/$runName.mp4"
Select-String -Path (Join-Path $runDir 'status.log') -Pattern 'OBJECTIVE' | Select-Object -Last 1 | ForEach-Object { $_.Line }
```

3. **Stop cleanly on missing RefMod or busy GPU:** If `submit_parody_run.py` raises `ValueError` (no local RefMod for a non-`good` celebrity) or returns `rc=7` (`GPU_BUSY`), report that exact reason in chat and stop without retrying or downloading weights.
4. **Reply right after `OBJECTIVE ok` + QNAP upload:** Do **not** run a follow-up `ffprobe`, `ls`, or any other tool call — reply directly in chat. Give Derrick `<run_dir>\clip.mp4`, `pi-drop/<runName>.mp4`, the `OBJECTIVE` line, and a 1-sentence description of the scene and spoken line (never crown `KEEP` or numeric scores).

## Sibling skills & sources

- `h3-prompting` (R1–R31), `h3-max-ref2va-prompt` (picture-ref REF2VA), `alienpc-hardcore-i2v-director`, `alienpc-stills-pose-edit-prompting`, `h3-hc-render` / `comfy-render` / `video-render`.
- Malcolm: `MINIMAX_H3_REFMODS_INSTALLATION_AND_USAGE_GUIDE.md` §6; `MINIMAX_H3_PROMPTING_GUIDE.md`; `known-characters/INDEX.md`.
- Derrick decisions: Nov 5, 2026 (`INDEX + RefMod`, BA-1 `approved_characters` gate) & Nov 6, 2026 (`t218u`/`t375s1715`: `4bc9bba` 1-pass `768x1344` baseline locked; `RefLoRA`, `2-pass`, and `ref_audio` retired).
