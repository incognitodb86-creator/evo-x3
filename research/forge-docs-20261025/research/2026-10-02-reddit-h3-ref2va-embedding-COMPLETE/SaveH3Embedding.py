import os
import folder_paths
import torch
from safetensors.torch import save_file


class SaveH3Embedding:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "conditioning": ("CONDITIONING",),
                "name": ("STRING", {"default": "minimaxh3_my_orbit"}),
            }
        }


    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("path",)
    FUNCTION = "save"
    CATEGORY = "minimax_h3"
    OUTPUT_NODE = True


    def save(self, conditioning, name):
        cond = conditioning[0][0]  # [1, N, 5120]
        if cond.ndim == 3:
            cond = cond[0]
        # keep text-tagged rows if present
        extra = conditioning[0][1] if len(conditioning[0]) > 1 else {}
        tags = extra.get("minimax_token_tags")
        if tags is not None:
            tags = tags.reshape(-1)
            # 1 = text modality in H3
            mask = tags.cpu() == 1
            if mask.any():
                cond = cond[mask]
        vec = cond.detach().float().cpu().contiguous()
        folder = folder_paths.get_folder_paths("embeddings")[0]
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, f"{name}.safetensors")
        save_file({"qwen3vl_32b": vec}, path)
        return (path,)

NODE_CLASS_MAPPINGS = {"SaveH3Embedding": SaveH3Embedding}
NODE_DISPLAY_NAME_MAPPINGS = {"SaveH3Embedding": "Save MiniMax H3 Embedding"}
