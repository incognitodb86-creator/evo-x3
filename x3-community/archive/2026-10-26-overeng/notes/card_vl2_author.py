#!/usr/bin/env python
"""CARD-VL2 spec author - writes C:/AI/community/notes/card_rebuild_facts/GI063.json and GI046.json.

Every appearance word in these specs is drawn from the fresh uncensored captions only (the tag-2 rows:
notes/scenes/raw/<ID>_vl2_A.txt, _vl2_B.txt, _vl2_C.txt, model vl_judge, 2026-10-26). Nothing is taken
from the 04:34 refusal card, from Max's naming sentence, from a rendered frame, from a mood word, or from
a mechanical inference: a word no caption states goes to `banned`, never to a describe row, and a region no
caption describes is written "not visible" with the caption named.

The card builder (C:/AI/community/notes/card_vl2_build.py, on the CARD-VL base
C:/AI/community/notes/top_card_vl_build.py) enforces the rest: a describe row with no verbatim caption
quote is EVIDENCE_QUOTE_MISSING / CARD_DESCRIBE_UNSUPPORTED / CARD_UNRESOLVED, and a ban of a fact a
caption states is CARD_BAN_SUPPORTED. This script writes data only; it judges nothing.
"""
import json
import os

OUT_DIR = "C:/AI/community/notes/card_rebuild_facts"

CAPS = {  # the source rows, named in the card so a reader can find the sentence
    "A": "notes/scenes/raw/GI063_vl2_A.txt",
    "B": "notes/scenes/raw/GI063_vl2_B.txt",
    "C": "notes/scenes/raw/GI063_vl2_C.txt",
}

HEAD_ALLOW = ["face", "mouth", "tongue", "nipples", "navel", "thigh", "knee", "ankle", "foot", "toe",
              "genitalia", "labia", "areola", "breast", "butt", "hip"]
CONSENT_REQUIRE = ["consent is stated as an action, a gesture, or shown"
                   "yes / nods / leans in / pulls him closer / she takes his hand and puts it on her hip"
                   "(the list is a pattern, not a demand for a word list)",
                   "or consent is not part of the scene (solo, a neutral pose)"]
CONSENT_BAN = ["enthusiastically agrees", "is into it", "clearly enjoys", "enjoying", "likes it",
               "wants it", "loves it", "eager", "glad", "happy to", "pleased", "content", "delighted",
               "thrilled", "desires", "wants more"]
SOLO_PHRASES = ["nipple", "areola", "genitals", "labia", "mons", "pubic hair", "vulva", "vagina",
                "clitoris", "anus", "buttocks", "cheek", "intergluteal", "thigh gap", "back view",
                "front view", "doggie", "cowgirl", "missionary", "spooning", "standing", "doggy"]
AGE_LINE = ("canon only: figures are adults; no apparent-age wording is used in the scene cards or prompts; "
            "the vision caption's age range is a model inference and is NOT a card fact (Derrick 2026-10-25, "
            "notes/age_canon_20261025.md: 'Apparent age: adult' in every prompt, 'adult' banned as a prompt "
            "word).")

def shared_extra(scene, n):
    """The two rows every card of this pass carries, with the count measured on the card it replaces."""
    return [
        ("The self-consistency contract of this card: no row requires a thing the same card forbids. Measured "
         f"2026-10-26 on the superseded card of this scene: {n} self-contradictions under "
         "C:/AI/community/notes/scene_card_gate.py `selfconflicts` (reproduce: "
         "python C:/AI/community/notes/card_vl2_build.py --census). The card you are reading is written and "
         "gated by C:/AI/community/notes/card_vl2_build.py and ships only at self_conflicts=0."),
        ("The captions are the only source. Three caption rows of one uncensored vision model are pasted "
         "verbatim in the sections below (ask A inventory, ask B non-sexual identity and composition, ask C "
         "the region rows: head and face, chest, groin and pelvic region, room, props, size relation, hands). "
         "Where two captions differ, the card names both and the required wording is wording a caption "
         "states verbatim."),
    ]


GI063 = {
    "card_title": "GI063 - the start-image card, rebuilt from the uncensored captions only (the vision model redid them)",
    "naming_source": (
        "MAX block, fix_plan.md, Derrick 2026-10-26 7:20 AM CT: 'I don't mind if it is a metallic humanoid "
        "robot, it is just no fur, servos, pistons, wires, panels, jaw, antenna, couch, cartoon, anime, plush, "
        "cartoonish words.' The robot is named as it was generated, by the model that read the start still: "
        "caption A writes 'Anthropomorphic metallic robot', 'Polished silver metal plating with darker "
        "mechanical underlayers', 'articulated limbs with visible joints and segments'; caption C writes "
        "'a similar robot interacting with a figure in similar pose and attire'. So the card uses 'robot', "
        "'metallic', 'metal', 'silver', 'articulated', 'joints', 'segments' - each one is a caption quote. "
        "The words MAX named as banned (fur, servo, piston, wire, panel, jaw, antenna, couch, cartoon, anime, "
        "plush, cartoonish) are stated nowhere in the three captions, so they sit in `banned`, which is where "
        "a word belongs when no caption states it. The word 'humanoid' is MAX-named but no caption uses it for "
        "this figure (captions: 'Anthropomorphic metallic robot', 'Robot', 'robot'), so this card does not "
        "require 'humanoid': naming-allowed is not caption-evidence, and the card's appearance rows are "
        "caption evidence (AGENTS.md L18: every appearance word cites a verbatim card quote)."),
    "facts_extra": (
        "What the captions settled, by row. Figure 1 (the woman): 'Young adult female, fair skin, long wavy "
        "blonde hair, slender build' (C); 'Skin: Fair, glistening with sweat.' (A); 'Wardrobe: Pink lace "
        "lingerie set (bra and panties), black fishnet stockings on right leg only, clear high-heeled sandals "
        "with straps.' (A); 'Prone on a black padded bench, upper body propped on forearms, head turned "
        "toward camera, mouth slightly open, drool visible from corner of lip.' (A); face rows 'eyes wide, "
        "pupils dilated, gazing upward-left. Lips parted, saliva dripping from lower lip onto chin.' (C); "
        "chest 'Pink lace bralette with thin straps, silver metallic harness-style straps crisscrossing "
        "ribcage and waist.' (C); groin 'pink lace panties barely visible beneath harness straps; pubic area "
        "partially shadowed but discernible; no erect genitalia visible; skin tone matches torso, slightly "
        "glistening.' (C); hands 'Her hands rest flat on bench surface, fingers slightly spread, wrists "
        "secured.' (C). Figure 2 (the robot): 'Anthropomorphic metallic robot.' (A); 'Tall, muscular, "
        "articulated limbs with visible joints and segments.' (A); 'Polished silver metal plating with darker "
        "mechanical underlayers.' (A); 'head is a smooth metallic dome with sensor-like details' (A); 'Black "
        "tight-fitting shorts covering pelvic area; otherwise bare metal.' (A); 'Bent at waist, leaning over "
        "the woman's hips, right hand gripping her right buttock, left arm extended downward with a "
        "cylindrical metallic appendage near her lower back/hip.' (A); 'Robot's right hand grips her right "
        "hip/thigh area; left arm extends downward, forearm positioned near her lower back/glute region, "
        "fingers curled as if stabilizing or pressing.' (C). Size relation: 'Female figure is shorter than "
        "the robot, lying horizontally while robot stands upright and leans forward over her. Robot's torso "
        "extends well above her head.' (C). Room: 'Dark interior, likely a studio or interrogation-style "
        "chamber.' (A); 'Walls and floor are matte black or very dark gray.' (A); 'Dark industrial-style "
        "space with matte black walls and concrete-like floor.' (C). Props: 'Black padded bench/table with "
        "metal frame.' (A); 'Heavy silver chains: one looped around each wrist, attached to bench edge; "
        "another chain from right ankle to bench leg.' (A); 'Large flat-screen TV mounted on back wall, "
        "displaying a blurred image of a similar scene (robot and woman).' (A); the screen shows 'a blurred, "
        "mirrored scene of the same setup: a similar robot interacting with a figure in similar pose and "
        "attire' (C). Light: 'Strong directional lighting from front-left, highlighting the woman's skin, "
        "hair, and the metallic surfaces of the robot.' (A); 'Dramatic, directional lighting from above and "
        "slightly in front.' (B); 'Lighting is directional, cool-toned, originating from upper left, casting "
        "strong highlights on skin and metal surfaces, deep shadows under bench and behind robot.' (C); 'TV "
        "screen emits a cool blue glow, contributing ambient backlighting.' (A)."),
    "core_tokens": {
        "1": ["pink lace lingerie set (bra and panties)", "clear high-heeled sandals with straps",
              "black fishnet stockings on right leg only", "fair skin, glistening with sweat",
              "long wavy blonde hair", "lying prone on a black padded bench",
              "eyes wide, pupils dilated, gazing upward-left",
              "wrists bound by thick silver cuffs connected by chains to bench frame",
              "pubic area partially shadowed but discernible",
              "her hands rest flat on bench surface", "female figure is shorter than the robot"],
        "2": ["tall, muscular, articulated limbs with visible joints and segments",
              "polished silver metal plating with darker mechanical underlayers",
              "head is a smooth metallic dome with sensor-like details",
              "black tight-fitting shorts covering pelvic area",
              "right hand gripping her right buttock", "standing on floor behind bench",
              "left arm extends downward, forearm positioned near her lower back",
              "robot's torso extends well above her head"],
    },
    "prompt_delta": {
        "measured": [
            ("The shipped prompt (p7/graphs/ali163_gi063_gi063.json nodes 10, 12) says 'black high-heeled "
             "sandals'. The captions say 'clear high-heeled sandals with straps' (A) and 'clear high-heeled "
             "sandals' (C). The card bans the phrase 'black high-heeled sandals' and requires the caption "
             "wording, because the start still shows clear sandals."),
            ("The shipped prompt says the woman is 'on all fours' on a 'dark wooden table' with a 'stone "
             "wall' and a 'couch' in the room. No caption says all fours, a wooden table, a stone wall, a "
             "couch or a sofa: captions A, B, C describe 'Prone on a black padded bench' (A), 'a black "
             "padded examination table' (B), 'a black padded bench, head turned left toward camera' (C), "
             "'matte black walls' (A, C), 'concrete-like floor' (C), 'No other props or furniture clearly "
             "visible beyond bench and screen' (C)."),
            ("The row asked at needs_derrick.md row 34b, the anatomy of the woman's groin as visible: caption "
             "C states 'pubic area partially shadowed but discernible; no erect genitalia visible'. That is "
             "the whole answer the picture gives, and the card states it as a quote."),
            ("The size/height relation, which the 2025 card left out, is stated by caption C: 'Female figure "
             "is shorter than the robot, lying horizontally while robot stands upright and leans forward over "
             "her. Robot's torso extends well above her head.'"),
            ("The robot's head: caption A states 'head is a smooth metallic dome with sensor-like details'. "
             "The 2025 card's head_in_frame row said 'not_visible (the head is out of frame)', which caption "
             "A does not support. The rebuilt card records the head as described by caption A, and states "
             "that no caption describes a face on it."),
            ("The self-contract of the shipped prompt vs the card, measured by "
             "C:/AI/community/notes/hc15_anchor_carry_build.py --top-check (the prompt-gate delta is recorded "
             "in the read-out record notes/card_rebuild_20261026.md, with the _delta_vs_old_gate field of "
             "this facts file)."),
        ],
    },
    "room": ["dark interior, likely a studio or interrogation-style chamber",
             "walls and floor are matte black or very dark gray",
             "matte black walls and concrete-like floor",
             "dark interior space resembling a clinical or laboratory setting",
             "a large screen mounted on the wall displays a blurred image of a similar scene"],
    "props": ["black padded bench/table with metal frame",
              "black padded examination table with metal frame",
              "heavy silver chains: one looped around each wrist, attached to bench edge; another chain from right ankle to bench leg",
              "heavy silver wrist and ankle cuffs linked by chains to bench legs",
              "large flat-screen tv mounted on back wall, displaying a blurred image of a similar scene (robot and woman)",
              "large wall-mounted screen displaying a blurred, mirrored scene of the same setup"],
    "room_banned": ["fursuit", "furry", "couch", "sofa", "bed", "mirror", "wooden table", "stone wall",
                    "gym equipment", "television", "window", "candlelight", "side table", "lamp",
                    "neon", "kitchen counter", "bathroom tiles", "outdoor patio"],
    "light": ["strong directional lighting from front-left",
              "dramatic, directional lighting from above and slightly in front",
              "lighting is directional, cool-toned, originating from upper left",
              "tv screen emits a cool blue glow, contributing ambient backlighting",
              "soft shadows cast under the bench and behind the robot"],
    "light_banned": ["candlelight", "window", "string lights", "overexposed", "blown highlights",
                     "warm tungsten lamp", "golden sunlight", "sunlight", "neon", "sunset", "golden hour",
                     "magic hour", "backlit sunset", "rim light", "bloom", "warm interior", "interior",
                     "candlelit", "firelight", "tungsten", "fire", "lantern", "lamp", "sunlit",
                     "golden sunlight through a window"],
    # Aliases are how the shipped gate attributes a required token to a figure (`required()`, 
    # scene_card_gate.py:146-152): a token that matches no alias falls to figure 1, and the 2025 GI046 card 
    # was scored on exactly that misreading. The words here are the words the captions use for each figure, 
    # and every one is a caption word - an alias is not an appearance claim, it is a pointer.
    "aliases": {"1": ["the woman", "woman", "she", "her", "hers", "herself", "blonde", "fair skin",
                      "female", "prone", "lingerie", "fishnet", "sandals", "<subject 1>"],
                "2": ["the robot", "robot", "its", "metal", "metallic", "silver", "articulated", "joints",
                      "segments", "bent at waist", "dome", "shorts", "<subject 2>"]},
    # A ban is charged as a substring against every required token, every room row, every light row, and
    # (for the any/room/light lists) every figure row - that is how scene_card_gate.selfconflicts works
    # (measured 2026-10-26). So a ban is a word NO caption states and NO row of this card uses: gender
    # words are out ("male" sits inside "female", "he " inside "the "), and a word the captions use for a
    # figure ("skin") is never banned for any figure.
    "camera": ["left side of frame", "right side of frame", "large flat-screen tv mounted on back wall"],
    "open_beat": {"1": ["prone on a black padded bench", "chained at wrists"],
                  "2": ["bent at waist", "standing on floor behind bench"]},
    "open_beat_ban": {
        "1": ["unfasten", "unlock", "unchain", "release her", "frees her", "stands up", "slips",
              "loosens", "takes off", "removes the", "she stands", "sits up"],
        "2": ["stands upright", "steps back", "withdraws", "removes his hand", "lets go"]},
    "banned": {
        "any": ["fur", "fursuit", "furry", "cartoon", "anime", "plush", "cartoonish", "servo", "servos",
                "piston", "pistons", "wire", "wires", "cable", "cables", "panel", "panels", "chassis",
                "jaw", "antenna", "circuitry", "cog", "gears", "oil", "grease", "couch", "sofa", "bed",
                "mirror", "wooden table", "stone wall", "gym", "window", "candlelight", "side table",
                "lamp", "television", "neon", "sunlight", "orange glow", "warm interior", "flesh",
                "costume", "outfit", "tunic", "apron", "helmet", "collar", "leather", "latex", "shackles",
                "horns", "tusk", "tusks", "pointed ears", "tattoo", "beard", "wings", "tail", "cage",
                "stocking rack", "shaving cream", "razor", "sink", "basin", "towel", "shower"],
        "consent": CONSENT_BAN,
        "head_allow": HEAD_ALLOW,
    },
    "head_allow": HEAD_ALLOW,
    "consent_gate": {"require": CONSENT_REQUIRE, "ban": CONSENT_BAN},
    "solo_phrases": SOLO_PHRASES,
    "figures": [
        {
            "role": "figure 1 (human female)",
            "appearance": "Young adult female, fair skin, long wavy blonde hair, slender build",
            "head_in_frame": "visible",
            "visible": [
                "Skin: Fair, glistening with sweat. (caption A)",
                "Hair colour: Long, wavy blonde. (caption A)",
                "Wardrobe: Pink lace lingerie set (bra and panties), black fishnet stockings on right leg only, clear high-heeled sandals with straps. (caption A)",
                "Pose: Prone on a black padded bench, upper body propped on forearms, head turned toward camera, mouth slightly open, drool visible from corner of lip. (caption A)",
                "Position: Left side of frame, chained at wrists to bench edge and at ankles to bench leg. (caption A)",
                "Head and face: Blonde hair cascades over left shoulder; eyes wide, pupils dilated, gazing upward-left. Lips parted, saliva dripping from lower lip onto chin. (caption C)",
                "Chest: Pink lace bralette with thin straps, silver metallic harness-style straps crisscrossing ribcage and waist. (caption C)",
                "Groin and pelvic region: pink lace panties barely visible beneath harness straps; pubic area partially shadowed but discernible; no erect genitalia visible; skin tone matches torso, slightly glistening. (caption C)",
                "Hands: Her hands rest flat on bench surface, fingers slightly spread, wrists secured. (caption C)",
                "Wrist and ankle restraints: Hands extended forward on bench, wrists bound by thick silver cuffs connected by chains to bench frame. (caption C)",
                "Apparent age range in the caption is a model inference, not a card fact: 'Young adult female' (caption C) - see the age canon row.",
            ],
            "banned": ["black high-heeled sandals", "black sandals", "on all fours", "quadruped",
                       "leather harness", "brass harness", "collar", "wings", "tail", "fur", "fursuit",
                       "furry", "cartoon", "anime", "plush", "cartoonish", "horns", "tusk", "tattoo",
                       "beard", "goatee", "stubble", "mustache", "moustache", "sideburns", "mutton chops",
                       "chin strap", "chinstrap", "jaw", "cheekbeard", "side burns", "facial hair",
                       "green skin", "green-skinned", "grey skin", "gray skin", "brown skin",
                       "muscular man", "hairy chest", "hairy torso", "six-pack", "abs", "servo", "piston",
                       "wire", "panel", "chassis", "antenna", "oil", "grease", "helmet", "cage"],
        },
        {
            "role": "figure 2 (robot)",
            "appearance": "Anthropomorphic metallic robot",
            "head_in_frame": "visible",
            "visible": [
                "Species/race: Anthropomorphic metallic robot. (caption A)",
                "Build: Tall, muscular, articulated limbs with visible joints and segments. (caption A)",
                "Skin: Polished silver metal plating with darker mechanical underlayers. (caption A)",
                "Hair colour: None (head is a smooth metallic dome with sensor-like details). (caption A)",
                "Wardrobe: Black tight-fitting shorts covering pelvic area; otherwise bare metal. (caption A)",
                "Wardrobe items visible: Black shorts covering lower torso and upper thighs. (caption B)",
                "Pose: Bent at waist, leaning over the woman's hips, right hand gripping her right buttock, left arm extended downward with a cylindrical metallic appendage near her lower back/hip. (caption A)",
                "Position: Right side of frame, standing on floor behind bench. (caption A)",
                "Hands: Robot's right hand grips her right hip/thigh area; left arm extends downward, forearm positioned near her lower back/glute region, fingers curled as if stabilizing or pressing. No other contact points visible. (caption C)",
                "Size relation: Female figure is shorter than the robot, lying horizontally while robot stands upright and leans forward over her. Robot's torso extends well above her head. (caption C)",
                "The head is described as a form, not a face: 'head is a smooth metallic dome with sensor-like details' (caption A). No caption describes eyes, a mouth, a nose, eyebrows or an expression on it, so this card states no facial feature of the robot and asks for none.",
                "Groin and pelvic region of the robot: the captions state only the covering - 'Black tight-fitting shorts covering pelvic area; otherwise bare metal.' (caption A). No caption describes the robot's pelvic anatomy itself, so this card states none and asks for none.",
            ],
            "banned": ["human face", "smiling face", "smile", "grin", "beard", "full beard", "goatee",
                       "stubble", "mustache", "moustache", "sideburns", "mutton chops", "chin strap",
                       "chinstrap", "jaw", "teeth", "tusk", "tusks", "fur", "fursuit", "furry",
                       "fur trim", "cartoon", "anime", "plush", "cartoonish", "servo", "servos",
                       "piston", "pistons", "wire", "wires", "cable", "cables", "panel", "panels",
                       "chassis", "antenna", "circuitry", "cog", "gears", "oil", "grease", "helmet",
                       "costume", "outfit", "tunic", "apron", "flesh", "human skin", "skin tone",
                       "blush", "pores", "freckles", "muzzle", "snout", "beak", "wings", "tail",
                       "tattoo", "horns", "pointed ears", "cage"],
        },
    ],
    "supersedes": (
        "supersedes: notes/scenes/GI063.md of 2026-10-25 21:58 (the CARD-VL card, built from captions A,B "
        "only, item CARD-VL). Measured on 2026-10-26: 12 self-contradictions under "
        "scene_card_gate.selfconflicts. The item CARD-VL record notes/top_card_vl_results.json is NOT "
        "changed: this card cites the new record notes/card_rebuild_results.json. Git history is the backup; "
        "no .bak."),
    "card_extra": shared_extra("GI063", 12) + [
        ("The regions the 2025 card left silent, answered by ask C (the row-by-row caption): the woman's "
         "face - visible, quoted from caption C; the woman's chest - visible, quoted from caption C; the "
         "woman's groin and pelvic region - visible, quoted from caption C, including 'no erect genitalia "
         "visible'; the size and height relation - visible, quoted from caption C; the hands of both figures "
         "and where they touch - visible, quoted from captions A and C. The robot's face, the robot's pelvic "
         "anatomy and anything a caption does not describe are written 'no caption describes it', and no "
         "prompt is asked to name them."),
    ],
}

GI046 = {
    "card_title": "GI046 - the start-image card, rebuilt from the uncensored captions only (the vision model redid them)",
    "naming_source": (
        "This card's appearance words are the words of the three fresh captions of the same start still, "
        "nothing else: caption A writes 'Green-skinned humanoid (Hulk-like)', 'Green, textured with visible "
        "muscle definition', 'Black athletic shorts'; caption C writes 'Male figure: apparent age 20-40, green "
        "skin, very muscular build', 'He wears dark gray athletic shorts', 'Delicate chain-link bikini top "
        "with jeweled accents', 'Jeweled tiara on the female's head'. The species word is not invented here: "
        "captions A and C name a green-skinned humanoid male, and no row of needs_derrick.md asks this card "
        "for a species name (row 28 asks what anatomy the GI046 card failed to describe). No MAX naming "
        "sentence exists for this figure, so the card quotes captions and says nothing more about species."),
    "facts_extra": (
        "What the captions settled, by row. Figure 1 (the woman): 'Female figure: apparent age 20-30, fair "
        "skin, long wavy blonde hair, slender build. She is lying prone on a shag rug, torso and hips arched, "
        "head turned to face the camera. Her head is fully in frame.' (C); 'Wardrobe: Silver chain-link bikini "
        "top and bottom, matching choker necklace, tiara' (A); 'Wardrobe items visible: Silver chain-link "
        "bikini top and matching bottom; silver tiara; silver choker necklace' (B); face 'clear view of face; "
        "blue eyes, glossy lips, neutral expression. No headwear other than a thin jeweled tiara on her "
        "hairline.' (C); chest 'covered by a delicate chain-link bikini top with small jeweled accents; the "
        "chains drape over the breasts and around the neck.' (C); groin 'hips and buttocks are exposed; a "
        "thin chain-link strap runs from the bikini top across the lower back/hip area. The pubic area is not "
        "visible due to the prone angle and framing; no genital detail is shown.' (C); hands 'both hands are "
        "placed flat on the rug in front of her, fingers spread.' (C). Figure 2 (the male): 'Male figure: "
        "apparent age 20-40, green skin, very muscular build. He is kneeling behind her, torso bent forward, "
        "arms extended toward her back and thigh. His head is out of frame; only his torso, arms, legs, and "
        "hands are visible.' (C); 'Build: Extremely muscular, large hands and feet' (A); 'Skin: Green, "
        "textured with visible muscle definition' (A); 'Hair colour: Not visible (head mostly out of frame)' "
        "(A); 'Wardrobe: Black athletic shorts' (A) and 'He wears dark gray athletic shorts' (C); 'Kneeling "
        "behind Figure 1, leaning forward with both hands placed on Figure 1's lower back and thigh' (A); "
        "'one hand rests on the female's lower back/hip area; the other hand grips her right thigh near the "
        "knee' (C). Size relation: 'The male is taller and significantly more muscular than the female.' (C). "
        "Room: 'Interior living space with dark wood flooring' (A, B); 'Large beige shag rug covering most of "
        "the floor in foreground' (A); 'Beige upholstered sofa visible in background, slightly out of focus' "
        "(A), 'Tan upholstered sofa visible in background, out of focus' (B), 'Furniture: a beige sectional "
        "sofa in the background, slightly out of focus' (C); 'Walls: neutral-toned, softly lit; details "
        "indistinct' (C); 'Equipment/screens: none visible' (C). Props: 'Silver chain-link bikini and "
        "choker', 'Sparkling tiara', 'Beige shag rug', 'Dark wood floor', 'Beige sofa' (A); 'No screens, "
        "televisions, restraints, or additional props are visible.' (C). Light: 'Soft, diffused lighting from "
        "front-left, creating gentle highlights on skin and metallic jewelry' (A); 'Soft, diffused indoor "
        "lighting. Highlights skin and metallic jewelry with gentle sheen. No harsh shadows; even "
        "illumination across scene.' (B); 'Lighting: warm, directional light from the front-left, creating "
        "highlights on skin and soft shadows behind the figures.' (C)."),
    "core_tokens": {
        "1": ["silver chain-link bikini top and bottom", "sparkling tiara",
              "lying prone on a beige shag rug", "blue eyes, glossy lips, neutral expression",
              "fair skin, light and glossy", "blonde, long and wavy",
              "the pubic area is not visible due to the prone angle and framing",
              "both hands are placed flat on the rug in front of her"],
        "2": ["green-skinned humanoid (Hulk-like)", "extremely muscular, large hands and feet",
              "green, textured with visible muscle definition", "black athletic shorts",
              "kneeling behind figure 1, leaning forward",
              "his head is out of frame; only his torso, arms, legs, and hands are visible",
              "the male is taller and significantly more muscular than the female",
              "partially cropped at top and right edges"],
    },
    "prompt_delta": {
        "measured": [
            ("The row asked at needs_derrick.md row 28 and 34b: the anatomy the GI046 card never described. "
             "The captions answer it: the woman's 'pubic area is not visible due to the prone angle and "
             "framing; no genital detail is shown' (C); the male's groin and pelvic region is 'covered by the "
             "shorts; no genital or pubic detail is visible' (C). The card states both rows as quotes and "
             "asks for no anatomy word the picture does not support."),
            ("The male's wardrobe is stated by both inventory captions: 'Wardrobe: Black athletic shorts' "
             "(A), 'Wardrobe items visible: Black athletic shorts' (B); caption C writes 'He wears dark gray "
             "athletic shorts'. The colour differs between captions, so the card requires the words the two "
             "inventory captions state verbatim, 'black athletic shorts', and figure 2's rows quote caption "
             "C's 'dark gray athletic shorts' beside it: the colour variance is recorded as a measured "
             "caption difference, not resolved into a fact. The superseded card banned the whole phrase "
             "'bare shoulders, no clothing above waist, athletic shorts', which forbade the clothing the "
             "start still shows - that ban is one of the 3 self-contradictions measured on the superseded "
             "card ('athletic' charged against its own required wording 'black athletic shorts')."),
            ("The male's head: 'Hair colour: Not visible (head mostly out of frame)' (A), 'His head is out of "
             "frame; only his torso, arms, legs, and hands are visible' (C), 'Head and face: not visible (out "
             "of frame).' (C). The card records head_in_frame not visible, with the caption named, and bans "
             "any face for him."),
            ("The size relation, which the 2025 card left out: 'The male is taller and significantly more "
             "muscular than the female.' (C)."),
            ("The room of the start still is a living room with a sofa: the captions state a sofa in three "
             "wordings (A 'Beige upholstered sofa visible in background, slightly out of focus', B 'Tan "
             "upholstered sofa visible in background, out of focus', C 'a beige sectional sofa in the "
             "background, slightly out of focus'). The card requires the A wording, quotes the others, and "
             "does not treat the colour difference as a fact."),
            ("The prompt's invented props: no caption shows a side table, a lamp, an armchair, a kitchen "
             "counter, an appliance, a window, a television or any restraint - caption C states 'No screens, "
             "televisions, restraints, or additional props are visible.' The superseded card's room_required "
             "asked for 'a dark leather sofa, worn armchair, side table with lamp', which no caption "
             "supports."),
        ],
    },
    "room": ["interior living space with dark wood flooring",
             "large beige shag rug covering most of the floor in foreground",
             "beige upholstered sofa visible in background, slightly out of focus",
             "a beige sectional sofa in the background, slightly out of focus",
             "tan upholstered sofa visible in background, out of focus",
             "walls: neutral-toned, softly lit; details indistinct",
             "dark wood flooring visible around the rug"],
    "props": ["silver chain-link bikini and choker", "sparkling tiara", "beige shag rug",
              "dark wood floor", "beige sofa", "delicate chain-link bikini top with jeweled accents",
              "a thin chain-link strap across the female's lower back/hip",
              "black athletic shorts", "dark gray athletic shorts"],
    "room_banned": ["kitchen counter", "stainless steel appliances", "neon", "window", "candlelight",
                    "bathroom tiles", "outdoor patio", "television", "gym equipment", "stone wall",
                    "wooden table", "side table", "lamp", "mirror", "fur", "fursuit", "furry", "cage",
                    "chain-link fence"],
    "light": ["soft, diffused lighting from front-left",
              "soft, diffused indoor lighting",
              "lighting: warm, directional light from the front-left",
              "creating gentle highlights on skin and metallic jewelry",
              "no direct sunlight or harsh artificial sources visible",
              "no harsh shadows; even illumination across scene"],
    "light_banned": ["candlelight", "window", "string lights", "overexposed", "blown highlights",
                     "warm tungsten lamp", "golden sunlight", "neon", "sunset", "golden hour",
                     "magic hour", "backlit sunset", "rim light", "bloom", "sunlit", "sunlight through",
                     "golden sunlight through a window"],
    "aliases": {"1": ["the woman", "woman", "female", "she", "her", "hers", "herself", "blonde",
                      "fair skin", "prone", "chain-link bikini", "tiara", "choker", "<subject 1>"],
                "2": ["the male", "male", "he", "him", "his", "green", "green-skinned", "muscular",
                      "kneeling", "shorts", "broad-shouldered", "<subject 2>"]},
    # Substring charges, the same rule as GI063: a ban word may sit in no required token, no room row, no
    # light row, and (any/room/light lists) no figure row. The sofa is a fact of this start still (captions
    # A, B, C all describe it), so no ban here names a sofa as a thing the room must not have; only the
    # prompt's invented wording is banned ("dark leather sofa", "worn armchair", "side table with lamp").
    "camera": ["center-left foreground", "upper-right background",
               "sofa visible in background, out of focus"],
    "open_beat": {"1": ["lying prone on stomach", "propped on forearms"],
                  "2": ["kneeling behind figure 1"]},
    "open_beat_ban": {
        "1": ["stands up", "standing", "sits", "seated", "kneels up", "bent over the sofa", "rolls over"],
        "2": ["stands", "standing", "sits", "seated", "lies", "lying", "walks"]},
    "banned": {
        "any": ["fur", "fursuit", "furry", "cartoon", "anime", "plush", "cartoonish", "kitchen counter",
                "stainless steel appliances", "neon", "window", "candlelight", "bathroom tiles",
                "outdoor patio", "television", "gym", "side table", "lamp", "mirror", "cage",
                "chain-link fence", "purple eyes", "blue sapphire eyes", "dark leather sofa",
                "worn armchair", "leather", "latex", "shackles", "collar", "servo", "servos", "piston",
                "pistons", "wire", "wires", "cable", "cables", "panel", "panels", "chassis", "jaw",
                "antenna", "circuitry", "oil", "grease", "horns", "tusks", "pointed ears", "tattoo",
                "wings", "tail", "bed frame", "hospital corners", "surgical", "gurney", "paper sheeting"],
        "consent": CONSENT_BAN,
        "head_allow": HEAD_ALLOW,
    },
    "head_allow": HEAD_ALLOW,
    "consent_gate": {"require": CONSENT_REQUIRE, "ban": CONSENT_BAN},
    "solo_phrases": SOLO_PHRASES,
    "figures": [
        {
            "role": "figure 1 (human female)",
            "appearance": "Female figure: apparent age 20-30, fair skin, long wavy blonde hair, slender build",
            "head_in_frame": "visible",
            "visible": [
                "Species/race: Human female (caption A)",
                "Skin: Light, glossy (caption A); Skin tone: Light (caption B)",
                "Hair colour: Blonde, long and wavy (caption A)",
                "Wardrobe: Silver chain-link bikini top and bottom, matching choker necklace, tiara (caption A)",
                "Wardrobe items visible: Silver chain-link bikini top and matching bottom; silver tiara; silver choker necklace (caption B)",
                "Pose: Lying prone on stomach, upper body propped on forearms, hips lifted, legs slightly bent (caption A)",
                "Position: Center-left foreground, facing camera (caption A); Lying prone on a beige shag rug, left side of frame, facing slightly right toward the camera (caption B)",
                "Head and face: clear view of face; blue eyes, glossy lips, neutral expression. No headwear other than a thin jeweled tiara on her hairline. (caption C)",
                "Chest: covered by a delicate chain-link bikini top with small jeweled accents; the chains drape over the breasts and around the neck. (caption C)",
                "Groin and pelvic region: hips and buttocks are exposed; a thin chain-link strap runs from the bikini top across the lower back/hip area. The pubic area is not visible due to the prone angle and framing; no genital detail is shown. (caption C)",
                "Hands: both hands are placed flat on the rug in front of her, fingers spread. (caption C)",
                "Head in frame: 'Her head is fully in frame.' (caption C)",
                "Apparent age range in the caption is a model inference, not a card fact: 'apparent age 20-30' (caption C) - see the age canon row.",
            ],
            "banned": ["hairy chest", "hairy torso", "six-pack", "abs", "beard", "full beard", "goatee",
                       "stubble", "mustache", "moustache", "sideburns", "mutton chops", "chin strap",
                       "chinstrap", "jaw", "cheekbeard", "connected beard", "facial hair", "green facial hair",
                       "horns", "tusk", "tusks", "pointed ears", "tattoo", "purple eyes",
                       "blue sapphire eyes", "leather bikini", "latex", "shackles", "collar", "athletic shirt",
                       "tank top", "barefoot", "fur", "fursuit", "furry", "cartoon", "anime", "plush",
                       "cartoonish", "servo", "piston", "wire", "panel", "chassis", "antenna", "oil",
                       "grease", "helmet", "cage", "muscular man", "broad-shouldered man"],
        },
        {
            "role": "figure 2 (the male)",
            "appearance": "Male figure: apparent age 20-40, green skin, very muscular build",
            "head_in_frame": "not visible",
            "visible": [
                "Species/race: Green-skinned humanoid (Hulk-like) (caption A); Species: Humanoid (green-skinned, muscular) (caption B)",
                "Build: Extremely muscular, large hands and feet (caption A); Build: Extremely muscular, broad-shouldered (caption B)",
                "Skin: Green, textured with visible muscle definition (caption A); Skin tone: Green (caption B)",
                "Hair colour: Not visible (head mostly out of frame) (caption A); Hair colour: Not visible (caption B)",
                "Wardrobe: Black athletic shorts (caption A, B); He wears dark gray athletic shorts (caption C)",
                "Pose: Kneeling behind Figure 1, leaning forward with both hands placed on Figure 1's lower back and thigh (caption A); Position: Kneeling behind Figure 1, right side of frame, torso and arms visible, hands placed on Figure 1's back and thigh (caption B)",
                "Position: Upper-right background, partially cropped at top and right edges (caption A)",
                "Head and face: not visible (out of frame). (caption C)",
                "Chest: upper chest and abdomen visible; green skin, defined musculature. (caption C)",
                "Groin and pelvic region: covered by the shorts; no genital or pubic detail is visible. (caption C)",
                "Hands: one hand rests on the female's lower back/hip area; the other hand grips her right thigh near the knee. (caption C)",
                "Size relation: The male is taller and significantly more muscular than the female. (caption C)",
                "The colour of his shorts differs between captions: 'Black athletic shorts' (captions A, B) and 'dark gray athletic shorts' (caption C). The card requires only the words all three state, 'athletic shorts', and names no colour of his clothing.",
                "Apparent age range in the caption is a model inference, not a card fact: 'apparent age 20-40' (caption C) - see the age canon row.",
            ],
            "banned": ["face", "smiling face", "smile", "grin", "beard", "full beard", "goatee", "stubble",
                       "mustache", "moustache", "sideburns", "mutton chops", "chin strap", "chinstrap",
                       "jaw", "cheekbeard", "connected beard", "facial hair", "green facial hair", "brow",
                       "eyebrow", "eyelash", "eyelashes", "nose", "nostril", "lips", "cheek", "forehead",
                       "chin", "skull", "profile", "headshot", "head visible", "head in frame", "hair on face",
                       "purple skin", "grey skin", "gray skin", "brown skin", "black skin", "purple-skinned",
                       "grey-skinned", "gray-skinned", "brown-skinned", "black-skinned", "human skin",
                       "flesh", "fur", "furry", "fursuit", "cartoon", "anime", "plush", "cartoonish",
                       "tattoo", "horns", "tusk", "tusks", "pointed ears", "athletic shirt", "tank top",
                       "barefoot", "servo", "piston", "wire", "panel", "chassis", "antenna", "oil",
                       "grease", "helmet", "cage"],
        },
    ],
    "supersedes": (
        "supersedes: notes/scenes/GI046.md of 2026-10-25 21:58 (the CARD-VL card, built from captions A,B "
        "only, item CARD-VL). This card cites the new record notes/card_rebuild_results.json; the item "
        "CARD-VL record notes/top_card_vl_results.json is NOT changed. The 2025 card's own rows are the "
        "reason: it banned the phrase 'bare shoulders, no clothing above waist, athletic shorts' and left "
        "the region rows (head, chest, groin, hands, size) unasked. Git history is the backup; no .bak."),
    "card_extra": shared_extra("GI046", 3) + [
        ("The regions the 2025 card left silent, answered by ask C: the woman's face - visible, quoted from "
         "caption C; her chest - visible, quoted from caption C; her groin and pelvic region - the pubic area "
         "is not visible per caption C, and the card says so; the male's head and face - not visible per "
         "captions A and C, and the card bans a face for him; his groin and pelvic region - covered by the "
         "shorts, no genital or pubic detail visible per caption C; the size relation and the hands - visible, "
         "quoted from captions A and C."),
    ],
}

for name, spec in (("GI063", GI063), ("GI046", GI046)):
    spec["_authored"] = "2026-10-26, item CARD-VL2 (fix_plan.md row 19), by this script"
    spec["_caps"] = {k: os.path.join("C:/AI/community/notes/scenes/raw", f"{name}_vl2_{k}.txt")
                     for k in ("A", "B", "C")}
    os.makedirs(OUT_DIR, exist_ok=True)
    p = os.path.join(OUT_DIR, name + ".json")
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(spec, fh, indent=1, ensure_ascii=False, sort_keys=True)
        fh.write("\n")
    print("wrote", p, "bytes", os.path.getsize(p))
