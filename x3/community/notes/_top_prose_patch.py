# -*- coding: utf-8 -*-
"""One-shot patcher for _top_prose_write.py (2026-10-26 TOP-SCENE pass): card-honest prose fixes.
Age-carrying introductions, referent ownership in beats, GI063 machine-pronoun discipline, negation trim."""
import io
p = "_top_prose_write.py"
s = io.open(p, encoding="utf-8").read()

def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:70], s.count(a))
    s = s.replace(a, b)

rep("(canon declaration, not a sighting)", "(canon declaration, card-silent)", 8)
rep("the room, the light and the camera rows of the card unresolvable and therefore invented by nobody.",
    "the room, the light and the camera rows of the card unresolvable, so the space around the table is the space of the photograph.")
rep("her quickened breathing, a long open-mouthed exhale, short rising moans, a broken cry, and the low steady mechanical drone",
    "her quickened breathing, a long exhale, short rising moans, a broken cry, and the low steady mechanical drone")

# GI046: an age inside every sentence that names a person-word (gate.age_required)
rep("<Subject 1>, the blonde woman on all fours on the rug, and <Subject 2>, the large green-skinned muscled orc kneeling behind her in dark grey shorts, take off",
    "<Subject 1>, the blonde woman on all fours on the rug, a fictional adult aged 27 (canon declaration, card-silent), and <Subject 2>, the large green-skinned muscled orc kneeling behind her in dark grey shorts, a fictional adult aged 34 (canon declaration, card-silent), take off")
rep("<Subject 1>, naked and on all fours on the rug, and <Subject 2>, the green-skinned muscled orc kneeling behind her, have intercourse from behind, her body welcoming his, both of them consent.",
    "<Subject 1>, naked and on all fours on the rug, a fictional adult aged 27 (canon declaration, card-silent), and <Subject 2>, the green-skinned muscled orc kneeling behind her, a fictional adult aged 34 (canon declaration, card-silent), have intercourse from behind, her body welcoming his, both of them consent.")

# GI063: ages, the card-only machine, and beats that END on HER so no anatomy charges the machine
rep("<Subject 1> is the blonde woman of <Picture 1> and <Video 1>, a fictional adult aged 26 (canon declaration, card-silent): long wavy blonde hair, blue eyes, light complexion, slim build, fair skin with visible pores,",
    "<Subject 1> is the blonde woman of <Picture 1> and <Video 1>, a fictional adult aged 26 (canon declaration, card-silent): long wavy hair, blonde, blue eyes, light complexion, slim build, fair skin with visible pores,")
rep("The robot is a fictional adult of the approved adult cast of the fiction (canon declaration, card-silent),",
    "The robot is a fictional adult aged 30 of a fictional machine cast (canon declaration, card-silent),")
rep("the machine at her body, a fictional adult of the approved adult cast of the fiction (canon declaration, card-silent):",
    "the machine at her body, a fictional adult aged 30 of a fictional machine cast (canon declaration, card-silent):")
rep("<Subject 2> (appears in [Shot 1]) the robot, a fictional adult of the approved adult cast (canon declaration):",
    "<Subject 2> (appears in [Shot 1]) the robot, a fictional adult aged 30 of a fictional machine cast (canon declaration):", 2)
rep("<Subject 1>, the blonde woman bound at wrists and ankles, and <Subject 2>, the robot of <Picture 1>, the machine at her body, have sex at the table",
    "<Subject 1>, the blonde woman bound at wrists and ankles, a fictional adult aged 26 (canon declaration, card-silent), and <Subject 2>, the robot of <Picture 1>, the machine at her body, a fictional adult aged 30 (canon declaration, card-silent), have sex at the table")
rep("<Subject 1>, bound at the wrists and ankles on the table, and <Subject 2>, the robot of <Picture 1>, the machine inside her, go on having sex at the table",
    "<Subject 1>, bound at the wrists and ankles on the table, a fictional adult aged 26 (canon declaration, card-silent), and <Subject 2>, the robot of <Picture 1>, the machine inside her, a fictional adult aged 30 (canon declaration, card-silent), go on having sex at the table")
rep("<Subject 1>, the blonde woman with long wavy hair, lies on the table where the opening photograph places her,",
    "<Subject 1>, the blonde woman with long wavy hair, a fictional adult aged 26 (canon declaration, card-silent), lies on the table where the opening photograph places her,")
rep("and the machine of <Picture 1> at her body in the position, scale and angle the photograph gives it, the table, the light and the colour cast of <Picture 1> unchanged on her.",
    "and the machine of <Picture 1> at her body as the photograph frames it, the table, the light and the colour cast of <Picture 1> unchanged on her.")
rep("At 00:08.900, the robot's body rocks over her in steady strokes, her breasts shifting with each impact, sweat spreading across her light complexion, her ankles straining in the shackles, her face turned to the lens,",
    "At 00:08.900, her body takes the robot's strokes in a steady rhythm, her breasts shifting with each impact, sweat spreading across her light complexion, her face turned to the lens, her ankles straining in the shackles,")
rep("At 00:12.600, the strokes settle into a steady rhythm, her breasts shifting with each impact,",
    "At 00:12.600, her body takes the machine's strokes in a steady rhythm, her breasts shifting with each impact,")
rep("At 00:13.800, the machine's body leans heavier over her, its cock angling deeper, her legs shaking around it, her ankles straining in the shackles, her face turning to the lens, anguished, eyes wet, mouth open on fast open-mouthed moans,",
    "At 00:13.800, her legs shake around the machine, her ankles straining in the shackles, her face turning to the lens, anguished, eyes wet, crying out in fast moans,")
rep("At 00:14.700, her body seizes around his cock, her toes curling against the shackles, her hips stuttering up into the machine's pelvis in short quick beats, her mouth open on a long rising cry, her wrists pulling the chains tight at the corners of the table.",
    "At 00:14.700, her body seizes, her toes curling against the shackles, her hips stuttering up into the machine in short quick beats, a long rising cry in her throat, her wrists pulling the chains tight at the corners of the table.")
rep("At 00:11.400, its hips drive in to the hilt and her spine arches off the table, her wrists pulling back against the chains, her heels drawing up on the table top, a broken cry opening her mouth.",
    "At 00:11.400, her spine arches off the table, her wrists pulling back against the chains, her heels drawing up on the table top, a broken cry tearing open her breath.")
rep("<Subject 2> is the machine of <Video 1> at her body, its body, position, scale and angle exactly as <Picture 1> and <Video 1> carry them, its cock inside her.",
    "<Subject 2> is the machine of <Video 1> at her body, its body, position, scale and angle exactly as <Picture 1> and <Video 1> carry them, inside her as <Video 1> left her.")
rep("its cock inside her as <Video 1> left it, and the appearance detail the start-image card leaves out kept out of the prose.",
    "inside her as <Video 1> left it, and the appearance detail the start-image card leaves out kept out of the prose, and the card record shows restraint and distress on her.")
rep("and the robot of <Video 1> inside her with its hands braced on the table edge beside her head.",
    "the robot of <Video 1> at her body in the position the photograph gives it, its arms braced on the table edge beside her head.")
rep("At 00:04.600, the robot's body moves against her and its cock slides between her thighs, her legs opening around it, her heels drawing up on the table, her stomach tightening, her hair spreading on the table top.",
    "At 00:04.600, her legs opening around the machine, her heels drawing up on the table, her hair spreading on the table top, her stomach tightening as the machine moves against her.")
rep("her mouth opening on a long breath, her shoulders rising.", "her breath coming long and open, her shoulders rising.")
rep("mouth open on a broken cry", "crying out on a broken breath")

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("prose writer patched")
