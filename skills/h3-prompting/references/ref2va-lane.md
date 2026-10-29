# Folded in from skill ref2va-prompt (verbatim body, audit 2026-10-29). Original description:

description: Pointer skill. The paste shape and every prompt rule for text going into MiniMaxH3ReferenceToVideo on Max live in the h3-prompting skill (C:\AI\community\skills\h3-prompting\SKILL.md, numbered rules R1-R31, worked examples, detail checklist). This file keeps only the lane facts - which node, what must not be pasted into it, and the pre-queue gate. Use for any REF2VA paste; cite rules as R<n>, never restate them.


# REF2VA prompt (pointer - U2 2026-10-29)

**All prompt rules are in one place: skill `h3-prompting`, file
`C:\AI\community\skills\h3-prompting\SKILL.md`.** Rules R1-R31 cover: output contract (R1), adults-only and youth
guard (R2-R4), paste shape and task type (R5-R6), audio (R7), shot timing and length (R8-R9), continuation (R10),
identity clauses and retention lines (R11), clothing clause (R12), reference roles (R13), start-image records and
garment end states (R14), `ref_image_size` (R15), get-into-position (R16), PRIMARY MOTION (R17), body inventory
(R18), contact geometry (R19), motion verbs (R20), response dial (R21), slap (R22), camera line (R23),
positives-only (R24), plain style and skin words (R25), sound-word vocabulary (R26), contradiction phrases (R27), label
discipline (R28), one pose per cell and chain hygiene (R29), pre-queue gate and diff (R30), LoRA triggers (R31).
Read that file for the wording, the detail checklist (section 5) and the worked examples (section 6). Do not copy a
rule sentence into a brief - cite `R<n>`.

## Lane facts (this file only)

- Node: `MiniMaxH3ReferenceToVideo` on Max via llama-swap :8080/comfyui. Which node is which, and what may not
  share one node, is **R6** in `C:\AI\community\skills\h3-prompting\SKILL.md`.
- Multi-cell chains: the chain lane is `references/ref2va-chain-lane.md` (in h3-prompting). Single clips start here.
- The cond is the still Derek named this turn (**R28** covers what may be invented). When the pose must be unlocked
  first, that work is the stills lane (`alienpc-stills-pose-edit-prompting`), then come back to the paste.
- Which POS may enter Max TE at all is the director lane's rule (`alienpc-hardcore-i2v-director`, "Max POS craft"
  section). This file is the Max REF2VA paste lane only.
- Render dials, node wiring, queue and watch/triage are `h3-hc-render` and `alienpc-local-video-ops`; KEEP is
  Derek's alone. None of that is a prompt rule.

## Gate before queueing (this file only)

1. Write the paste to a prompt file in the run dir (R1), then run the checklist in `h3-prompting` section 5 over
   that file.
2. Run the adults-only tests: `C:\AI\director\.venv\Scripts\python.exe -m pytest -q
   C:\AI\community\scripts\tests\test_p6_review.py C:\AI\community\scripts\tests\test_guard_scope.py`;
   `comm.guard_ok` also runs inside `run_graph_job.py` - never loosen either.
3. Run the **R30** diff gate over the paste file (one axis of change only) before queueing.

Source of the node contract: MiniMax-H3 `VIDEO_PROMPT_WRITING_GUIDE_ref_en`
(`huggingface.co/MiniMaxAI/MiniMax-H3`, docs).
