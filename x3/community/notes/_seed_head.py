P = r"C:/AI/community/notes/hc15_anchor_carry_build.py"
lines = open(P, encoding="utf-8").read().split("\n")
i = next(k for k, l in enumerate(lines) if "invented head for the head-cropped figure" in l)
assert "app(" in lines[i + 1], lines[i + 1]
lines[i + 1] = '          app("c1", "' + chr(92) + 'nA grinning head hangs low above the green-skinned orc."), "ck_top_card")'
open(P, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("head seed line:", lines[i + 1])
