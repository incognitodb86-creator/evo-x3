"""T3 long-scene dry plan (no writer calls). Meets render-long-scene-spec-20261113.md: 285-315 s, one arc, no restated strip."""
from __future__ import annotations

import json
from pathlib import Path

H3_FPS = 24
LEGAL = (56, 73, 90, 107, 124, 141, 158, 175, 192, 209, 226, 243)
STILL = r"C:\AI\render\stills\approved_characters\BEDROOM01\01_BEDROOM_LINGERIE.jpg"
SURFACE = "the bed"
GENRE = "hardcore pro"
TARGET_MIN, TARGET_MAX = 285.0, 315.0

# Skeleton: one arc. pad_frames on act rows are filled with continue clips (243f) until the total is in range.
# (role, name_stub, ask, position, frames, shots, shot_count, wardrobe, pose, screen_side, contact)
SKELETON = [
    ("setup", "talk", "short flirty banter only, no sex, three lines", "talk", 107, "single", 1,
     "sheer slip and heels on", "stands at the foot of the bed, facing him", "center", "none"),
    ("tease", "tease", "slow reveal, she lets the slip strap fall", "tease", 124, "single", 1,
     "slip on, left strap down", "stands at the bed, one strap off her shoulder", "center", "none"),
    ("strip", "strip", "she strips the slip and it stays on the floor", "tease", 158, "single", 1,
     "slip off, on the floor, heels stay", "stands nude by the bed except heels", "center", "none"),
    ("transition", "trans_miss", "he turns her onto her back, missionary", "missionary", 141, "single", 1,
     "nude, heels on", "on her back on the bed, knees up", "center, her head to frame left", "his penis inside her vagina"),
    ("act", "miss", "missionary on the bed, he takes her", "missionary", 243, "multi", 2,
     "nude, heels on", "on her back, knees up", "center, her head to frame left", "his penis inside her vagina"),
    ("transition", "trans_doggy", "he turns her over from missionary to doggy", "doggy", 141, "single", 1,
     "nude, heels on", "knees on the bed, forearms down, looking frame left", "her hips frame right, head frame left",
     "his penis inside her vagina from behind"),
    ("act", "doggy", "doggy on the bed, he takes her from behind", "doggy", 243, "multi", 2,
     "nude, heels on", "knees on the bed, forearms down", "her hips frame right, head frame left",
     "his penis inside her vagina from behind"),
    ("transition", "trans_cow", "he rolls under her, she sits astride, cowgirl", "cowgirl", 141, "single", 1,
     "nude, heels on", "astride him on the bed, knees planted", "center, she faces the lens", "his penis inside her vagina"),
    ("act", "cowgirl", "she rides him on the bed, cowgirl", "cowgirl", 243, "multi", 2,
     "nude, heels on", "astride him, knees planted on the bed", "center, she faces the lens", "his penis inside her vagina"),
    ("transition", "trans_bj", "she slides down and takes him in her mouth", "blowjob", 141, "single", 1,
     "nude, heels on", "kneels on the bed between his knees", "center, her face mid-frame",
     "his penis inside her mouth, her lips sealed around his shaft"),
    ("act", "bj", "she gives him a blowjob on the bed", "blowjob", 226, "single", 1,
     "nude, heels on", "kneels between his knees", "center, her face mid-frame",
     "his penis inside her mouth, her lips sealed around his shaft"),
    ("finish", "finish", "he finishes on her, facial, she stays on her knees", "finish", 175, "single", 1,
     "nude, heels on", "kneels on the bed, face tilted up", "center, her face mid-frame",
     "his penis at her lips; the semen lands on her cheeks and lips and stays"),
    ("aftercare", "aftercare", "short aftercare banter only, three lines, no sex", "talk", 124, "single", 1,
     "nude, heels on, a sheet pulled over her lap", "sits on the bed beside him", "center", "none"),
]

CONTINUE_ASK = {
    "missionary": "keep going, missionary, same position",
    "doggy": "keep going, doggy, same position",
    "cowgirl": "keep going, she rides him, same position",
    "blowjob": "keep going, slow blowjob, same position",
}


def seconds(frames: int) -> float:
    return frames / float(H3_FPS)


def _row(i, role, stub, ask, pos, frames, shots, scount, wardrobe, pose, side, contact, continue_from):
    assert frames in LEGAL, frames
    return {
        "clip": i, "name": f"t3_c{i:02d}_{stub}", "ask": ask, "position": pos,
        "continue_from": continue_from, "frames": frames, "seconds": round(seconds(frames), 3),
        "shots": shots, "shot_count": scount, "still": STILL, "surface": SURFACE, "genre": GENRE,
        "wardrobe": wardrobe, "pose": pose, "screen_side": side, "contact": contact, "role": role,
        "full_frame": True,
    }


def build_plan() -> dict:
    # Pad each act block with 243f continues, last remainder a legal length, until 285-315 s.
    base_frames = sum(r[4] for r in SKELETON)
    need = int(TARGET_MIN * H3_FPS) - base_frames  # at least this many extra frames
    # four act blocks to pad: miss, doggy, cowgirl, bj
    act_idxs = [i for i, r in enumerate(SKELETON) if r[0] == "act"]
    extras = {i: 0 for i in act_idxs}  # extra 243f continues per act block
    extra_total = 0
    while extra_total + 243 <= (TARGET_MAX * H3_FPS - base_frames) and extra_total < need:
        # add to the shortest-padded act first
        k = min(act_idxs, key=lambda i: extras[i])
        extras[k] += 1
        extra_total += 243
    total_f = base_frames + extra_total
    # if still under 285s, add one more 192f continue to the first act if it fits
    if seconds(total_f) < TARGET_MIN:
        for n in (192, 175, 158, 141, 124):
            if TARGET_MIN <= seconds(total_f + n) <= TARGET_MAX:
                extras[act_idxs[0]] += 1  # handled as a non-243 below via remainder list
                # store remainder on first act
                extras["_rem"] = n
                total_f += n
                break

    clips = []
    rem = extras.pop("_rem", 0)
    for si, row in enumerate(SKELETON):
        role, stub, ask, pos, frames, shots, scount, wardrobe, pose, side, contact = row
        prev = clips[-1]["name"] if clips else None
        clips.append(_row(len(clips) + 1, role, stub, ask, pos, frames, shots, scount, wardrobe, pose, side, contact, prev))
        n_cont = extras.get(si, 0)
        for j in range(n_cont):
            prev = clips[-1]["name"]
            fr = 243
            clips.append(_row(len(clips) + 1, "act", f"{stub}_cont{j+1}", CONTINUE_ASK[pos], pos, fr,
                              "single", 1, wardrobe, pose, side, contact, prev))
        if rem and si == act_idxs[0]:
            prev = clips[-1]["name"]
            clips.append(_row(len(clips) + 1, "act", f"{stub}_contR", CONTINUE_ASK[pos], pos, rem,
                              "single", 1, wardrobe, pose, side, contact, prev))
            rem = 0

    total_f = sum(c["frames"] for c in clips)
    total_s = round(seconds(total_f), 3)
    assert TARGET_MIN <= total_s <= TARGET_MAX, total_s
    strip_roles = [c for c in clips if c["role"] == "strip"]
    assert len(strip_roles) == 1
    assert any(c["role"] == "finish" for c in clips)
    assert clips[-1]["role"] == "aftercare"
    nude_from = strip_roles[0]["clip"]
    for c in clips:
        if c["clip"] > nude_from:
            assert "strips the slip" not in c["ask"] and "strap fall" not in c["ask"]
    acts = [(c["clip"], c["position"], c["role"]) for c in clips]
    for prev, cur in zip(acts, acts[1:]):
        # finish may follow oral on the same kneel; every other position change needs a transition clip
        if prev[1] != cur[1] and prev[2] in ("act", "transition") and cur[2] in ("act", "transition"):
            assert cur[2] == "transition" or prev[2] == "transition", (prev, cur)
    return {
        "scene": "t3_long",
        "n": len(clips),
        "total_frames": total_f,
        "total_seconds": total_s,
        "genre": GENRE,
        "still": STILL,
        "surface": SURFACE,
        "note": "dry plan only, no writer calls; chain_unverified until a KEEP parent exists; bed still so cowgirl is surface-legal",
        "spec": "render-long-scene-spec-20261113.md, 285-315s, one arc, strip once, transitions, finish, continuity fields",
        "clips": clips,
    }


def write_plan(out_dir: str | Path) -> Path:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    plan = build_plan()
    path = out / "t3_30plus_plan.json"
    path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    return path


if __name__ == "__main__":
    import sys
    dest = sys.argv[1] if len(sys.argv) > 1 else "."
    path = write_plan(dest)
    p = json.loads(path.read_text(encoding="utf-8"))
    print("T3_PLAN", p["n"], p["total_seconds"], path)
