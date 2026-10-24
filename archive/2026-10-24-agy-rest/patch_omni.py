with open(r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\custom_nodes\MiniMax-H3-Prompt-Rewriter-ComfyUI\minimax_h3_rewriter\writer_omni.py", "r", encoding="utf-8") as f:
    c = f.read()

target = """        repeat_last=False,
        library_pick="",
    ) -> io.NodeOutput:
        given = dict(locals())"""

replacement = """        repeat_last=False,
        library_pick="",
        **kwargs,
    ) -> io.NodeOutput:
        if not references:
            references = {k: v for k, v in kwargs.items() if k.startswith("ref_")}
        given = dict(locals())"""

assert target in c, "target not found"
with open(r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\custom_nodes\MiniMax-H3-Prompt-Rewriter-ComfyUI\minimax_h3_rewriter\writer_omni.py", "w", encoding="utf-8") as f:
    f.write(c.replace(target, replacement, 1))
print("PATCH_OK")
