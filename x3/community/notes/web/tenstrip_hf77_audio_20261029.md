# TenStrip / 10Eros-Max discussion #77 — audio prompting (saved 2026-10-29, U2)

URL: https://huggingface.co/TenStrip/10Eros-Max/discussions/77
Title: "The beta7 version feels like a technological setback," (opened ~14 h before save, closed by the opener)
Fetched: 2026-10-29 CT, one fetch, MCP fetch (text extract). Quote verified against the page text.

## The ruling used by U2 (TenStrip, model owner, ~14 h before save)

> Don't use developer H3 style prompting, it causes the most interference. "overall_soundcape" especially is actually
> the easiest way to introduce extremely bad audio and will cause the model to go out of it's way and start putting
> cartoon sounds on the output and ignore prompt and should be deleted. Prompt very normal audio queues in prompt or
> at the end of the main prompt.

Spelling note: the owner writes `overall_soundcape`; this repo's prompts and skills used `overall_soundscape:`.
Both are the same developer-H3 block, and the ruling deletes it.

## Supporting detail from the same thread (not used as a rule, useful context)

- `agapes` (~10 h before save): "for audio issues, strictly use only video step at 12 and audio at 3 or 8, i dont
  have any audio issue with it with super simple workflow euler/simple at 4step only run global comfy kitchen
  nothing else" — matches this box's beta7 dials (shift 12 video / 3 audio, Euler/simple, comfy kitchen attention),
  which is the standing KEEP line in `skills/h3-hc-render` and `alienpc-local-video-ops`.
- `ssjenforcer191`: background noise "animates its way through the entire video" on beta7; beta5/beta6 less so —
  the same single-pass background-flicker/noise family TenStrip noted on 2026-10-23 (2-pass is the next cell).
- `firsak`: on beta7 character likeness/lighting drift; recommends extra anchors in the prompt (describe the outfit)
  rather than relying on the reference alone.
- `liuxingsyue` (opener): beta7 female anatomy drifts during motion; beta6 colour/saturation problems.

## Consequence for the prompt skills (U2)

`overall_soundscape:` and `non_diegetic_music:` stop being prompt sections. Audio is written as plain, concrete
cues inside the main prompt text, at its end (the owner's own words). The rule lives in exactly one place:
`C:\AI\community\skills\h3-prompting\SKILL.md` (R7 + R26), which the other prompt skills point at.

Older run records (e.g. `C:\AI\community\runs\terrace_dom_q5guide_20261028_s51083007\prompt_seg0.txt`, which has
`overall_soundscape:` at line 28) and the B2 default graph are NOT edited: they are history and the graph is the
audited default.
