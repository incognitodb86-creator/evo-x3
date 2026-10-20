# P3 (ALI-123): App Mode json for TenStrip - official FastH3 I2V template + beta6 int8 + 10 steps + VSA + shift 10/3 + euler/simple, per pipeline_defaults clip block.
# Anti-burn stays OFF (no LoRA node in the graph). Drafts 0.3-0.6 MP, finals 768x1344 (1.03 MP). 5s first pass.
import json, os, copy
W = r"C:\AI\community"
C = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI"
TD = os.path.join(C, r"user\default\workflows")
# The official FastH3 I2V template ships inside the ComfyUI templates package, not in user\default\workflows.
TPL_DIRS = [TD, os.path.join(C, r".venv\Lib\site-packages\comfyui_workflow_templates_json\templates")]
TPL = "video_fast" + "video_fasth3_i2v.json"   # stock template path, not a UNET setting
TPL_PATH = next((os.path.join(d, TPL) for d in TPL_DIRS if os.path.exists(os.path.join(d, TPL))), None)
assert TPL_PATH, f"stock FastH3 I2V template not found in {TPL_DIRS}"
UNET = "10Eros_Max_h3_8stepTURBO_beta6_int8.safetensors"
TE = "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"
VVAE = "minimax_h3_video_vae_int8_convrot.safetensors"
AVAE = "minimax_h3_audio_vae_fp32.safetensors"
j = json.load(open(TPL_PATH, encoding="utf-8"))
nodes = {n["id"]: n for n in j["nodes"]}
sg = next(s for s in j["definitions"]["subgraphs"] if any(n.get("type") == "MiniMaxH3ImageToVideo" for n in s.get("nodes", [])))
sgn = {n["id"]: n for n in sg["nodes"]}

w = nodes[105]["widgets_values"]
assert w[5].startswith("fasth3_8step_v2") or "fasth3" in w[5], f"unexpected stock UNET {w[5]}"
w[5] = UNET
w[6] = TE; w[7] = VVAE; w[8] = AVAE; w[9] = "comfy kitchen attention"
w[3] = 5      # first pass 5 s (ALI-124)
w[4] = 51050001
default_prompt = ("The woman from the start image, an adult with auburn hair, stands in the concrete courtyard "
                  "among potted plants. She looks into the camera with a slow smile, unhooks her sheer black corset top "
                  "and lets it fall, then runs both hands down over her bare breasts and hips while swaying gently. "
                  "Static medium shot, soft daylight, shallow depth of field. Sound: quiet courtyard ambience, "
                  "distant birds, her soft breath and a low laugh.")
w[0] = default_prompt
nodes[136]["widgets_values"][0] = "community/FD006_768x1344.png"
nodes[142]["widgets_values"][1] = 0.5   # D3: drafts 0.3-0.6 MP; set 1.03 for the 768x1344 final
nodes[92]["widgets_values"][0] = "community/app_h3_i2v"

# Positional subgraph settings (the graph values ComfyUI executes).
sgn[6]["widgets_values"] = [UNET, "default"]
sgn[13]["widgets_values"] = [TE, "minimax", "default"]
sgn[11]["widgets_values"] = [VVAE]
sgn[24]["widgets_values"] = [AVAE]
sgn[17]["widgets_values"] = ["euler"]
sgn[9]["widgets_values"] = ["simple", 10, 1]        # scheduler, 10 steps, denoise
sgn[143]["widgets_values"] = [10, 3]                # MiniMaxH3SigmaShift video 10 / audio 3
sgn[128]["widgets_values"] = ["comfy kitchen attention"]
sgn[127]["widgets_values"][0] = "vsa"
sgn[127]["widgets_values"][1] = 10                   # selection.keep_percent
sgn[127]["widgets_values"][2] = 0.2                  # start_percent

# C2 fix (2026-10-20 Ralph): App Mode reads widgets_values_named as well as widgets_values.
# The stock template left its own sampler / 8 steps / stock distilled UNET / 0.4 MP in those named
# mirrors, which silently overrode the positional patches above. Mirror every positional patch.
def named(node, kv):
    node.setdefault("widgets_values_named", {}).update(kv)

named(nodes[105], {"prompt": default_prompt, "value_1": 5, "noise_seed": 51050001, "unet_name": UNET})
named(nodes[136], {"image": "community/FD006_768x1344.png"})
named(nodes[142], {"megapixels": 0.5})
named(nodes[92], {"filename_prefix": "community/app_h3_i2v"})
named(sgn[6], {"unet_name": UNET})
named(sgn[17], {"sampler_name": "euler"})
named(sgn[9], {"scheduler": "simple", "steps": 10, "denoise": 1})
named(sgn[143], {"shift_video": 10, "shift_audio": 3})
named(sgn[127], {"selection": "vsa", "selection.keep_percent": 10, "start_percent": 0.2, "end_percent": 1})
named(sgn[128], {"attention": "comfy kitchen attention"})

# Required TenStrip settings, both representations, before writing (C2 check).
for wv, nvm, key, want in ((w, nodes[105]["widgets_values_named"], "unet_name", UNET),
                           (sgn[6]["widgets_values"], sgn[6]["widgets_values_named"], "unet_name", UNET),
                           (sgn[17]["widgets_values"], sgn[17]["widgets_values_named"], "sampler_name", "euler"),
                           (sgn[9]["widgets_values"], sgn[9]["widgets_values_named"], "scheduler", "simple"),
                           (sgn[143]["widgets_values"], sgn[143]["widgets_values_named"], "shift_video", 10),
                           (sgn[143]["widgets_values"], sgn[143]["widgets_values_named"], "shift_audio", 3),
                           (sgn[127]["widgets_values"], sgn[127]["widgets_values_named"], "selection", "vsa"),
                           (sgn[128]["widgets_values"], sgn[128]["widgets_values_named"], "attention", "comfy kitchen attention")):
    assert want in wv, f"positional missing {key}={want}"
    assert nvm.get(key) == want, f"named mirror missing {key}={want} (got {nvm.get(key)})"
assert w[3] == 5 and nodes[142]["widgets_values"][1] == 0.5 == nodes[142]["widgets_values_named"]["megapixels"]
assert sgn[9]["widgets_values"][1] == 10 == sgn[9]["widgets_values_named"]["steps"]
assert sgn[127]["widgets_values"][2] == 0.2 == sgn[127]["widgets_values_named"]["start_percent"]
assert sgn[127]["widgets_values"][1] == 10 == sgn[127]["widgets_values_named"]["selection.keep_percent"]
assert "beta6mix" not in json.dumps(j).lower(), "Eros_beta6mix_Lora must never be stacked on beta6"
assert not any(n.get("type") == "LoraLoaderModelOnly" for n in list(sgn.values()) + list(nodes.values())), "no LoRA node in the community graph (anti-burn OFF)"
sel = [n["widgets_values"][0] for n in sgn.values() if n.get("type") == "BlockSparseAttention" and n.get("widgets_values")]
assert sel and all(s == "vsa" for s in sel), f"VSA required, not SLA (got {sel})"

sg["name"] = "H3 I2V beta6 (community settings)"
j["extra"]["linearMode"] = True
j["extra"]["linearData"] = {"inputs": [[136, "image"], [105, "prompt"], [105, "value_1"], [105, "noise_seed"], [142, "megapixels"]],
                            "outputs": [92]}   # same shape ComfyUI itself writes for App Mode
j["extra"]["community_note"] = ("ALI-52 P3, 2026-10-20: beta6 int8, euler/simple 10 steps (8 for drafts), shift 10/3, "
                                "VSA keep 10 start 0.2, comfy kitchen attention. megapixels 0.5 = draft, 1.03 = "
                                "768x1344 final. Start image must already match the output aspect. Adult (21+) "
                                "approved stills only. Start image community/FD006_768x1344.png (copy to "
                                "ComfyUI\\input\\community\\ first). 27B caption variant: set the subgraph text encoder "
                                "to qwen3_2b_128fp4_arar.safetensors (ALI-126). Never stack Eros_beta6mix_Lora on beta6.")
os.makedirs(os.path.join(W, "p3"), exist_ok=True)
dst = os.path.join(W, "p3", "Community_H3_I2V_beta6.app.json")
json.dump(j, open(dst, "w", encoding="utf-8"), indent=1, ensure_ascii=True)
print("WROTE", dst, os.path.getsize(dst))
