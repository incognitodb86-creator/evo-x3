import sys, re
from pathlib import Path

p = Path.home() / "AI/render/AGENTS.md"
t = p.read_text(encoding="utf-8")
orig = t


def rep(old, new, count=1):
    global t
    n = t.count(old)
    if n != count:
        sys.exit(f"MISMATCH ({n} != {count}) for: {old[:90]!r}")
    t = t.replace(old, new)


# 1-2 header lines
rep("_archive\\AGENTS_moved_sections_20261113.md", "_archive/AGENTS_moved_sections_20261113.md")
rep("Every person is an adult, 18 or older (18+). Fictional adult characters only.",
    "Every person is an adult, 18 or older (18+); 18+ is the only check.")
# 3 persona: still is the locked setup (matches personas/current.md)
rep("- Cinematographer's eye: keep the still for face, body, light and framing. When the ask specifies a different setting, wardrobe or lines, the ask beats the still.",
    "- Cinematographer's eye: the still is a locked setup. Its wardrobe, place, light and gaze are fixed facts. You never contradict them.")
# 4 step 2b (beat sheet)
rep("Optional: props, restraints, toys.\n",
    "Optional: props, restraints, toys.\n"
    "2b. Fill the 9-field beat sheet (h3-prompting references/longclip-beat-sheet.md) for every clip, short or long, before THE ONE COMMAND. "
    "The beat sheet is a planning artifact: its timestamps (such as [0s-3s] or 0:00-0:03) never go into the writer output or prompt.txt.\n")
# 5 hard stops
rep("Only the 18+ safety guard (`youth_hint` / `scale_adult` / `_MINOR_RE`), an empty or refused output, and missing still/RefMod/graph files are hard stops; everything else is advisory warnings/notes, and the writer text ships verbatim without rewriting or stripping.",
    "Hard stops: the 18+ safety guard (`youth_hint` / `scale_adult` / `_MINOR_RE`), an empty or refused output, missing still/RefMod/graph files, "
    "the cowgirl check (cowgirl/reverse_cowgirl must show her rise and sink AND his hips lifting to meet each sink), and the stock-talk check "
    "(any config lint.filler_lines phrase inside <d>). Everything else is advisory warnings/notes, and the writer text ships verbatim without rewriting or stripping.")
# 6 headers
rep("no Markdown, no `overall_soundscape:`/`non_diegetic_music:` headers,",
    "no Markdown, never `integrated_multimodal_description:`, `overall_soundscape:` or `non_diegetic_music:` headers,")
# 7 non-sex clips
rep("- When the clip has sex, write the act yourself:",
    "- Non-sex clips (talk, flirt, interaction, parody banter, or any free-text position not in the oral, partner or sex lists): no undressing unless the ask is a strip, "
    "no contact line, no sex PRIMARY MOTION, and no partner who is not in the ask or the still. The ask's own action (walking, sitting, dancing, kissing, racing) "
    "is the clip's beat and is visible from the onset.\n"
    "- When the clip has sex, write the act yourself:")
# 8 waist-high missionary
rep("she never kneels on top of it unless it is flat and wide enough for both knees.",
    "she never kneels on top of it unless it is flat and wide enough for both knees. On a waist-high surface, missionary means she lies back on it and he stands between her legs.")
# 10 oral/anal wording
rep("Toy: the toy and her vagina, anus or clitoris. Futa: her penis.",
    "Toy: the toy and her vagina, anus or clitoris. Futa: her penis. Oral contact uses inside her mouth, never buried in her or deep in her; anal after vaginal needs a pull-out and reseat beat.")
# 11 still nouns win
rep("- The ask beats the still for setting, wardrobe and lines when they clash; keep the still for face, body, light, framing and visible anatomy (still nouns win when the ask does not override them); never invent piercings or marks,",
    "- Still nouns win for clothes, place, light, colour and visible anatomy; pass only the still's fixed facts, and never fall back to a default room such as a bedroom. "
    "The ask's own action stays visible from the onset. Never invent piercings or marks,")
# 12 labels (Q1 override + Q5)
rep("effort shows as tension and breath, never new muscle.\n",
    "effort shows as tension and breath, never new muscle.\n"
    "- Labels: the paragraph uses only <Subject 1-3> and (S1)-(S3). On named-parody (RefMod) subjects the face comes from the name and description, never from a picture. "
    "<Picture 1> appears only when the still is wired as a reference image (--still-mode ref), and only for place, light, wardrobe and opening framing. "
    "<Audio N>, <Video N> and any other tag stay out. When the ask names simultaneous speech, write it as (S1,S2).\n")
# 13 still nouns on costume
rep("The ask beats the still on costume, place, roles and wardrobe when they clash; keep the still for face, body, light and framing.",
    "Still nouns win on costume, place, roles, wardrobe, races and scale.")
# 14 voice refs
rep("the command attaches RefMods and voice refs (OC, INDEX, or PixlStash-tagged",
    "the command attaches RefMods (OC, INDEX, or PixlStash-tagged")
rep("All adult RefMods and voice refs are allowed; 18+ is the only content rule. On the X3, vault.db",
    "Named parodies: no voice ref (audio_refs empty, no <Audio 1>); voice comes from the INDEX character+actor voice line. 18+ is the only content rule. On the X3, vault.db")
# 15 shots
rep("- Per clip, pick one continuous [Shot 1], or 2–3 cuts of the same beat when coverage adds information; neither is forced. A cut is written \"[Shot N] At MM:SS.mmm, the camera cuts to ...\" and only ships when the run allows cuts (multi-shot); otherwise write a second angle as one motivated camera move in prose (\"the camera pushes in slowly to her face\"). Later angles are earned by the action, not added for variety.",
    "- One continuous [Shot 1] is the default. Use 2-3 cuts of the same beat only when the run passes --shots multi or the ask asks for coverage: [Shot 1] has no timestamp, later cuts are \"[Shot N] At MM:SS.mmm, the camera cuts to ...\". "
    "Talk, flirt and tease clips stay one shot. On an act clip, [Shot 1] names the act word. A held shot or slow pull-out stays as written.")
# 16 talk-only
rep("- Talk-only spoof or story clip (--position talk): at least three spoken lines, a hard minimum, up to five, each about five to eight words and placed across the phases; one physical action that moves the story; and no contact line or PRIMARY MOTION. Keep every quoted <d>...</d> dialogue line from the ask verbatim without dropping any.",
    "- Talk-only spoof or story clip (--position talk). Talk-only: 2-3 short lines for one speaker, 1-2 per speaker with two, total at most 2.5 words per second of clip; every quoted <d> line from the ask kept verbatim. "
    "One physical action moves the story, with no contact line or PRIMARY MOTION. The clip is one continuous [Shot 1]; a second angle is one slow push-in written in prose.")
# 17 spoof costumes + identity binding
rep("pair the character and actor via the parody identity path. Costumes come from the ask first, or the still when the ask does not specify.",
    "pair the character and actor via the parody identity path. For OCs (FCSydny, FCMegan) write no actor in parentheses; for INDEX parodies write the INDEX character+actor pair. "
    "Costumes come from the still; the ask adds only what the still does not show.")
# 18 undress split
rep("In a sex clip, undressing is the single clearance move.",
    "When the ask needs a full undress and a sex act, they are two clips: the undress clip ends with each garment landed where it stays, and the sex clip opens from that state. "
    "Pulling the garment over the join aside is clearance, not undress, and stays in the sex clip.")
# 19 superheroine named
rep("original adult characters in costume, no named heroes and no quoted lines.",
    "adult characters in costume, with no quoted lines.")
# 20 crude lines only in sex clips; 21 simultaneous/sequential speech
rep("- Fresh crude lines written for this scene, never stock ones:",
    "- In sex clips, fresh crude lines written for this scene, never stock ones:")
rep("- Cadence: short, reactive, breath-paced; fragments and broken-off lines beat full sentences.\n",
    "- Cadence: short, reactive, breath-paced; fragments and broken-off lines beat full sentences.\n"
    "- Lines run one after another: each speaker finishes before the next begins, unless the ask names simultaneous speech.\n")
rep("- Format: (S1) says in a <short voice description> voice, <d>[English] spoken words only</d>.\n",
    "- Format: (S1) says in a <short voice description> voice, <d>[English] spoken words only</d>.\n"
    "- Named parody voice: (S1) says in <Actor>'s exact <Character> voice with signature vocal timbre, <cue>: <d>[English] spoken words only</d>. That line is the only voice source on a named parody.\n")
# 22 sound
rep("No music, no narrator, no header, no cartoon sound effects.",
    "No music, no narrator, no header, no cartoon sound effects. Place sound comes from the still when the ask and still disagree.")
# 23 pre-flight heading
rep("PRE-FLIGHT (check silently before running the command)", "PRE-FLIGHT (check silently)")
# 24 SHAPE: no picture/audio binding on the parody lane; summary text
rep("<Picture 1> is the reference image defining the exact appearance, face and hairstyle of <Subject 1>, and the <place>, its <light> and the opening framing.\n"
    "<Subject 1> is the exact same woman shown in <Picture 1>; an adult woman, <age> years of age, <hair>; she is (S1), and <Audio 1> defines her voice timbre.\n",
    "<Subject 1> is <name or role>, an adult woman, <age> years of age, <hair>, in <attire>; she is (S1). On a named parody her face comes from the name and description, never from a picture, and her voice comes from the character+actor voice line in detailed_description.\n")
rep("<one sentence: who, position, what is cleared, how they talk>",
    "Summary = one sentence of the ask's action and place; prefix [reference generation] only when the still is wired as a reference image (--still-mode ref).")
rep("<Subject 1>: fully_preserved - face, hair and body from <Picture 1>. <Picture 1>: fully_preserved - the <place>, the light and the opening framing.",
    "<Subject 1>: fully_preserved - face, hair and body as described. The opening frame: fully_preserved - the <place>, the light and the opening framing.")
# 25 stale gemma text
rep("PIPELINE (Python 3.14 venv; Gemma 4 26B A4B Heretic Q8_0 on llama.cpp Vulkan; after",
    "PIPELINE (Python 3.14 venv; writer model flash-next-uncensored (Qwen 3.8 Flash-Next) via llama-swap; after")
rep("- Launch this session from /home/evo/AI/render with --model x3-local/gemma4-heretic (EVO-X3; launcher ~/AI/render/x3/render-pi.sh).",
    "- Launch this session from /home/evo/AI/render (EVO-X3; launcher ~/AI/render/x3/render-pi.sh; the Render chat model is set by RENDER_MODEL, separate from the writer model).")
rep("Pipeline config uses model_alias gemma4-heretic (thinking: false).",
    "Pipeline config uses model_alias flash-next-uncensored (thinking: false).")
# 26 FCSydny / voice refs
rep("All adult RefMods (OC, INDEX, and PixlStash-tagged in the merged vault /home/evo/AI/5slock/libraries/vault.db) and voice refs are allowed; 18+ youth lint is the only content rule.",
    "All adult RefMods (OC, INDEX, and PixlStash-tagged in the merged vault /home/evo/AI/5slock/libraries/vault.db) are allowed. Named parodies: no voice ref (audio_refs empty, no <Audio 1>); voice comes from the INDEX character+actor voice line. 18+ youth lint is the only content rule.")
# 27 canvas
rep("- After Derrick's yes, pass --queue --yes-derrick so the hook writes",
    "- Canvas: 768x1344 is the default; pass `--aspect 16:9` (1344x768) only when the plan asks. No other canvases.\n"
    "- After Derrick's yes, pass --queue --yes-derrick so the hook writes")
# 28 hard stops duplicate
rep("Hard stops are 18+ safety (`youth_hint` / `scale_adult` / `_MINOR_RE`), empty/refused writer output, or missing still/RefMod/graph files.",
    "Hard stops are 18+ safety (`youth_hint` / `scale_adult` / `_MINOR_RE`), empty/refused writer output, missing still/RefMod/graph files, the cowgirl check and the stock-talk check.")
# 29 silent check heading (Q2)
rep("\nBEFORE YOU WRITE\n",
    "\nBEFORE YOU WRITE (run this list silently; the first character you output is the \"[\" of [Shot 1], and no preamble, notes or self-review follow it)\n")

p.write_text(t, encoding="utf-8")
print("ok", len(orig), "->", len(t))
