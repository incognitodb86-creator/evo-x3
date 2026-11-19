r"""ali147_refsheet_b_rs5_probe_h3.py - read-only probe: how MiniMaxH3ReferenceToVideo declares its reference-image
inputs, in the built-in node source (built-ins are not in specs\extender_object_info.json - the known ALI-147 rule).

RS5 needs proof that the graph key `ref_images.ref_image_2` is a real input on the c0 node (the task's static check names
it). This prints the exact lines of the INPUT_TYPES / signature region so the builder's check string can be written
against real text. Read-only; no writes.
"""
P = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\comfy_extras\nodes_minimax_h3.py"
lines = open(P, encoding="utf-8").read().splitlines()
start = [i for i, l in enumerate(lines) if "class MiniMaxH3ReferenceToVideo" in l]
print("class line (1-based):", [i + 1 for i in start])
a = start[0]
for i in range(a, a + 60):
    print("%4d| %s" % (i + 1, lines[i]))
print("---- literal presence ----")
src = "\n".join(lines)
for s in ('"ref_images.ref_image_1"', '"ref_images.ref_image_2"', '"ref_images.ref_image_3"',
          'prefix="ref_image_"', 'io.Autogrow.Input("ref_images"', 'options=["match", "max"]',
          'io.Combo.Input("ref_image_size"'):
    print("%-45s %s" % (s, s in src))
