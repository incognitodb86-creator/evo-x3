# ComfyUI node inputs (from object_info_20261105.json)

1786 node classes. Regenerate: `python notes\objinfo\_make_index.py`.

## AddLabel
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/text
- required:
  - image: IMAGE
  - text_x: INT default=10 min=0 max=4096 step=1
  - text_y: INT default=2 min=0 max=4096 step=1
  - height: INT default=48 min=-1 max=4096 step=1
  - font_size: INT default=32 min=0 max=4096 step=1
  - font_color: STRING default='white'
  - label_color: STRING default='black'
  - font: COMBO[FreeMono.ttf, FreeMonoBoldOblique.otf, TTNorms-Black.otf]
  - text: STRING default='Text'
  - direction: COMBO[up, down, left, right, overlay] default='up'
- optional:
  - caption: STRING default=''
- outputs: IMAGE:IMAGE

## AddLayer
module: comfy_extras.nodes_compositor | category: image
- required:
  - image: IMAGE
- optional:
  - layers: LAYERS
  - mask: MASK
  - name: STRING default=''
  - x: INT default=0 min=-16384 max=16384
  - y: INT default=0 min=-16384 max=16384
  - opacity: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blend_mode: COMBO[normal, multiply, screen, overlay, darken, lighten, color-dodge, color-burn, hard-light, soft-light, ... +16] default='normal'
  - rotation: FLOAT default=0.0 min=-360.0 max=360.0 step=1.0
  - width: INT default=0 min=0 max=16384
  - height: INT default=0 min=0 max=16384
  - z_index: INT default=0 min=-1000 max=1000
  - flip_h: BOOLEAN default=False
  - flip_v: BOOLEAN default=False
- outputs: LAYERS:LAYERS

## AddNoise
module: comfy_extras.nodes_custom_sampler | category: model/sampling/noise
- required:
  - model: MODEL
  - noise: NOISE
  - sigmas: SIGMAS
  - latent_image: LATENT
- outputs: LATENT:LATENT

## AddNoiseToTrackPath
module: custom_nodes.ComfyUI-KJNodes | category: conditioning/video_models
- required:
  - tracks: TRACKS
  - strength: FLOAT default=1.0 min=0.0 max=100.0 step=0.01
  - seed: INT default=0 min=0 max=18446744073709551615 step=1
  - noise_x_ratio: FLOAT default=1.0 min=0.0 max=100.0 step=0.01
  - noise_y_ratio: FLOAT default=1.0 min=0.0 max=100.0 step=0.01
  - noise_temporal_ratio: FLOAT default=1.0 min=0.0 max=100.0 step=0.01
- outputs: TRACKS:TRACKS

## AddTextPrefix
module: comfy_extras.nodes_dataset | category: text
- required:
  - texts: STRING
  - prefix: STRING default=''
- outputs: texts:STRING

## AddTextSuffix
module: comfy_extras.nodes_dataset | category: text
- required:
  - texts: STRING
  - suffix: STRING default=''
- outputs: texts:STRING

## AdjustBrightness
module: comfy_extras.nodes_dataset | category: image/adjustments
- required:
  - images: IMAGE
  - factor: FLOAT default=1.0 min=0.0 max=2.0
- outputs: images:IMAGE

## AdjustContrast
module: comfy_extras.nodes_dataset | category: image/adjustments
- required:
  - images: IMAGE
  - factor: FLOAT default=1.0 min=0.0 max=2.0
- outputs: images:IMAGE

## AIO_Preprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors
- required:
  - image: IMAGE
- optional:
  - preprocessor: COMBO[none, AnimeFace_SemSegPreprocessor, AnyLineArtPreprocessor_aux, BinaryPreprocessor, CannyEdgePreprocessor, ColorPreprocessor, DensePosePreprocessor, DepthAnythingPreprocessor, Zoe_DepthAnythingPreprocessor, DepthAnythingV2Preprocessor, ... +37] default='none'
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## AlignYourStepsScheduler
module: comfy_extras.nodes_align_your_steps | category: model/sampling/schedulers
- required:
  - model_type: COMBO[SD1, SDXL, SVD]
  - steps: INT default=10 min=1 max=10000
  - denoise: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: SIGMAS:SIGMAS

## AnimaLLLiteApply
module: comfy_extras.nodes_model_patch | category: model/patch/anima
- required:
  - model: MODEL
  - model_patch: MODEL_PATCH
  - image: IMAGE
  - strength: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - start_percent: FLOAT default=0.0 min=0.0 max=1.0 step=0.001
  - end_percent: FLOAT default=1.0 min=0.0 max=1.0 step=0.001
- optional:
  - mask: MASK
- outputs: MODEL:MODEL

## AnimalPosePreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Faces and Poses Estimators
- required:
  - image: IMAGE
- optional:
  - bbox_detector: COMBO[None, yolox_l.torchscript.pt, yolox_l.onnx, yolo_nas_l_fp16.onnx, yolo_nas_m_fp16.onnx, yolo_nas_s_fp16.onnx] default='yolox_l.torchscript.pt'
  - pose_estimator: COMBO[rtmpose-m_ap10k_256_bs5.torchscript.pt, rtmpose-m_ap10k_256.onnx] default='rtmpose-m_ap10k_256_bs5.torchscript.pt'
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE, POSE_KEYPOINT:POSE_KEYPOINT

## AnimeFace_SemSegPreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Semantic Segmentation
- required:
  - image: IMAGE
- optional:
  - remove_background_using_abg: BOOLEAN default=True
  - resolution: INT default=512 min=512 max=512 step=64
- outputs: IMAGE:IMAGE, ABG_CHARACTER_MASK (MASK):MASK

## AnimeLineArtPreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Line Extractors
- required:
  - image: IMAGE
- optional:
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## Any Switch (rgthree)
module: custom_nodes.rgthree-comfy | category: rgthree
- outputs: *:*

## AnyLineArtPreprocessor_aux
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Line Extractors
- required:
  - image: IMAGE
- optional:
  - merge_with_lineart: COMBO[lineart_standard, lineart_realisitic, lineart_anime, manga_line] default='lineart_standard'
  - resolution: INT default=1280 min=64 max=16384 step=8
  - lineart_lower_bound: FLOAT default=0 min=0 max=1 step=0.01
  - lineart_upper_bound: FLOAT default=1 min=0 max=1 step=0.01
  - object_min_size: INT default=36 min=1 max=16384 step=1
  - object_connectivity: INT default=1 min=1 max=16384 step=1
- outputs: image:IMAGE

## Anything Everywhere
module: custom_nodes.cg-use-everywhere | category: everywhere
- optional:
  - anything: *
- outputs: 

## Anything Everywhere3
module: custom_nodes.cg-use-everywhere | category: everywhere/deprecated
- optional:
  - anything: *
  - anything2: *
  - anything3: *
- outputs: 

## Anything Everywhere?
module: custom_nodes.cg-use-everywhere | category: everywhere/deprecated
- optional:
  - anything: *
  - title_regex: STRING default=''
  - input_regex: STRING default=''
  - group_regex: STRING default=''
- outputs: 

## APG
module: comfy_extras.nodes_apg | category: model/sampling/custom
- required:
  - model: MODEL
  - eta: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - norm_threshold: FLOAT default=5.0 min=0.0 max=50.0 step=0.1
  - momentum: FLOAT default=0.0 min=-5.0 max=1.0 step=0.01
- outputs: MODEL:MODEL

## AppendInstanceDiffusionTracking
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/InstanceDiffusion
- required:
  - tracking_1: TRACKING
  - tracking_2: TRACKING
- optional:
  - prompt_1: STRING default=''
  - prompt_2: STRING default=''
- outputs: tracking:TRACKING, prompt:STRING

## AppendStringsToList
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/text
- required:
  - string1: STRING default=''
  - string2: STRING default=''
- outputs: STRING:STRING

## ApplyCLIPSeg+
module: custom_nodes.ComfyUI_essentials | category: essentials/segmentation
- required:
  - clip_seg: CLIP_SEG
  - image: IMAGE
  - prompt: STRING default=''
  - threshold: FLOAT default=0.4 min=0.0 max=1.0 step=0.05
  - smooth: INT default=9 min=0 max=32 step=1
  - dilate: INT default=0 min=-32 max=32 step=1
  - blur: INT default=0 min=0 max=64 step=1
- outputs: MASK:MASK

## ApplyPulidFlux
module: custom_nodes.ComfyUI_PuLID_Flux_ll | category: pulid
- required:
  - model: MODEL
  - pulid_flux: PULIDFLUX
  - eva_clip: EVA_CLIP
  - face_analysis: FACEANALYSIS
  - image: IMAGE
  - weight: FLOAT default=1.0 min=-1.0 max=5.0 step=0.05
  - start_at: FLOAT default=0.0 min=0.0 max=1.0 step=0.001
  - end_at: FLOAT default=1.0 min=0.0 max=1.0 step=0.001
- optional:
  - attn_mask: MASK
  - options: OPTIONS
- outputs: MODEL:MODEL

## ApplyPuLIDFlux2
module: custom_nodes.ComfyUI-PuLID-Flux2 | category: PuLID-Flux2
- required:
  - model: MODEL
  - pulid_model: PULID_MODEL
  - strength: FLOAT default=1.0 min=0.0 max=2.0 step=0.01
  - eva_clip: EVA_CLIP
  - face_analysis: INSIGHTFACE
  - image: IMAGE
- optional:
  - face_index: INT default=0 min=0 max=9
  - debug_mode: BOOLEAN default=False
- outputs: MODEL:MODEL

## ApplyRifleXRoPE_HunuyanVideo
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/hunyuanvideo
- required:
  - model: MODEL
  - latent: LATENT
  - k: INT default=4 min=1 max=100 step=1
- outputs: MODEL:MODEL

## ApplyRifleXRoPE_WanVideo
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/wan
- required:
  - model: MODEL
  - latent: LATENT
  - k: INT default=6 min=1 max=100 step=1
- outputs: MODEL:MODEL

## ApplyTextureToMesh
module: comfy_extras.nodes_mesh_postprocess | category: 3d/texturing
- required:
  - mesh: MESH
  - base_color: IMAGE
- optional:
  - metallic: IMAGE
  - roughness: IMAGE
  - occlusion: IMAGE
  - normal_map: IMAGE
- outputs: mesh:MESH

## ARVideoI2V
module: comfy_extras.nodes_ar_video | category: model/conditioning/autoregressive
- required:
  - model: MODEL
  - vae: VAE
  - start_image: IMAGE
  - width: INT default=832 min=16 max=8192 step=16
  - height: INT default=480 min=16 max=8192 step=16
  - length: INT default=81 min=1 max=1024 step=4
  - batch_size: INT default=1 min=1 max=64
- outputs: MODEL:MODEL, LATENT:LATENT

## AudioAdjustVolume
module: comfy_extras.nodes_audio | category: audio
- required:
  - audio: AUDIO
  - volume: INT default=1 min=-100 max=100
- outputs: AUDIO:AUDIO

## AudioConcat
module: comfy_extras.nodes_audio | category: audio
- required:
  - audio1: AUDIO
  - audio2: AUDIO
  - direction: COMBO[after, before] default='after'
- outputs: AUDIO:AUDIO

## AudioConcatenate
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/audio
- required:
  - audio1: AUDIO
  - audio2: AUDIO
  - direction: COMBO[right, left] default='right'
- outputs: AUDIO:AUDIO

## AudioEncoderEncode
module: comfy_extras.nodes_audio_encoder | category: model/conditioning
- required:
  - audio_encoder: AUDIO_ENCODER
  - audio: AUDIO
- outputs: AUDIO_ENCODER_OUTPUT:AUDIO_ENCODER_OUTPUT

## AudioEncoderLoader
module: comfy_extras.nodes_audio_encoder | category: model/loaders
- required:
  - audio_encoder_name: COMBO[]
- outputs: AUDIO_ENCODER:AUDIO_ENCODER

## AudioEqualizer3Band
module: comfy_extras.nodes_audio | category: audio
- required:
  - audio: AUDIO
  - low_gain_dB: FLOAT default=0.0 min=-24.0 max=24.0 step=0.1
  - low_freq: INT default=100 min=20 max=500
  - mid_gain_dB: FLOAT default=0.0 min=-24.0 max=24.0 step=0.1
  - mid_freq: INT default=1000 min=200 max=4000
  - mid_q: FLOAT default=0.707 min=0.1 max=10.0 step=0.1
  - high_gain_dB: FLOAT default=0.0 min=-24.0 max=24.0 step=0.1
  - high_freq: INT default=5000 min=1000 max=15000
- outputs: AUDIO:AUDIO

## AudioLatentStretch
module: custom_nodes.10S-Comfy-nodes | category: 10S Nodes/Latents
- required:
  - audio_latent: LATENT
  - source_fps: FLOAT default=24.0 min=1.0 max=120.0 step=0.1
  - target_fps: FLOAT default=30.0 min=1.0 max=120.0 step=0.1
- optional:
  - interp_mode: COMBO[hermite, linear, nearest] default='hermite'
- outputs: audio_latent:LATENT

## AudioMerge
module: comfy_extras.nodes_audio | category: audio
- required:
  - audio1: AUDIO
  - audio2: AUDIO
  - merge_method: COMBO[add, mean, subtract, multiply]
- outputs: AUDIO:AUDIO

## BAE-NormalMapPreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Normal and Depth Estimators
- required:
  - image: IMAGE
- optional:
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## BakeAmbientOcclusion
module: comfy_extras.nodes_mesh_postprocess | category: 3d/texturing
- required:
  - low_poly: MESH
  - high_poly: MESH
  - resolution: INT default=1024 min=64 max=8192 step=64
  - samples: INT default=64 min=4 max=1024 step=4
  - max_distance: FLOAT default=0.5 min=0.01 max=2.0 step=0.01
  - strength: FLOAT default=1.0 min=0.0 max=2.0 step=0.05
  - bias: FLOAT default=0.01 min=0.0001 max=0.2 step=0.0005
- outputs: occlusion:IMAGE

## BakeNormalMapFromMesh
module: comfy_extras.nodes_mesh_postprocess | category: 3d/texturing
- required:
  - low_poly: MESH
  - high_poly: MESH
  - resolution: INT default=1024 min=64 max=8192 step=64
  - cage_distance: FLOAT default=0.05 min=0.001 max=0.5 step=0.001
  - ignore_backfaces: BOOLEAN default=True
- outputs: normal_map:IMAGE

## BakeTextureFromVoxel
module: comfy_extras.nodes_mesh_postprocess | category: 3d/texturing
- required:
  - mesh: MESH
  - voxel_colors: VOXEL
  - texture_size: INT default=2048 min=64 max=8192
- optional:
  - reference_mesh: MESH
- outputs: base_color:IMAGE, metallic:IMAGE, roughness:IMAGE

## BasicGuider
module: comfy_extras.nodes_custom_sampler | category: model/sampling/guiders
- required:
  - model: MODEL
  - conditioning: CONDITIONING
- outputs: GUIDER:GUIDER

## BasicScheduler
module: comfy_extras.nodes_custom_sampler | category: model/sampling/schedulers
- required:
  - model: MODEL
  - scheduler: COMBO[simple, sgm_uniform, karras, exponential, ddim_uniform, beta, normal, linear_quadratic, kl_optimal]
  - steps: INT default=20 min=1 max=10000
  - denoise: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: SIGMAS:SIGMAS

## BatchCLIPSeg
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking
- required:
  - images: IMAGE
  - text: STRING
  - threshold: FLOAT default=0.5 min=0.0 max=10.0 step=0.001
  - binary_mask: BOOLEAN default=True
  - combine_mask: BOOLEAN default=False
  - use_cuda: BOOLEAN default=True
- optional:
  - blur_sigma: FLOAT default=0.0 min=0.0 max=100.0 step=0.1
  - opt_model: CLIPSEGMODEL
  - prev_mask: MASK default=None
  - image_bg_level: FLOAT default=0.5 min=0.0 max=1.0 step=0.01
  - invert: BOOLEAN default=False
- outputs: Mask:MASK, Image:IMAGE

## BatchCount+
module: custom_nodes.ComfyUI_essentials | category: essentials/utilities
- required:
  - batch: *
- outputs: INT:INT

## BatchCropFromMask
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking
- required:
  - original_images: IMAGE
  - masks: MASK
  - crop_size_mult: FLOAT default=1.0 min=0.0 max=10.0 step=0.001
  - bbox_smooth_alpha: FLOAT default=0.5 min=0.0 max=1.0 step=0.01
- outputs: original_images:IMAGE, cropped_images:IMAGE, bboxes:BBOX, width:INT, height:INT

## BatchCropFromMaskAdvanced
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking
- required:
  - original_images: IMAGE
  - masks: MASK
  - crop_size_mult: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - bbox_smooth_alpha: FLOAT default=0.5 min=0.0 max=1.0 step=0.01
- outputs: original_images:IMAGE, cropped_images:IMAGE, cropped_masks:MASK, combined_crop_image:IMAGE, combined_crop_masks:MASK, bboxes:BBOX, combined_bounding_box:BBOX, bbox_width:INT, bbox_height:INT

## BatchImagesNode
module: comfy_extras.nodes_post_processing | category: image/batch
- required:
  - images: COMFY_AUTOGROW_V3
- outputs: IMAGE:IMAGE

## BatchLatentsNode
module: comfy_extras.nodes_post_processing | category: model/latent/batch
- required:
  - latents: COMFY_AUTOGROW_V3
- outputs: LATENT:LATENT

## BatchMasksNode
module: comfy_extras.nodes_post_processing | category: image/mask
- required:
  - masks: COMFY_AUTOGROW_V3
- outputs: MASK:MASK

## BatchUncrop
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking
- required:
  - original_images: IMAGE
  - cropped_images: IMAGE
  - bboxes: BBOX
  - border_blending: FLOAT default=0.25 min=0.0 max=1.0 step=0.01
  - crop_rescale: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - border_top: BOOLEAN default=True
  - border_bottom: BOOLEAN default=True
  - border_left: BOOLEAN default=True
  - border_right: BOOLEAN default=True
- outputs: IMAGE:IMAGE

## BatchUncropAdvanced
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking
- required:
  - original_images: IMAGE
  - cropped_images: IMAGE
  - cropped_masks: MASK
  - combined_crop_mask: MASK
  - bboxes: BBOX
  - border_blending: FLOAT default=0.25 min=0.0 max=1.0 step=0.01
  - crop_rescale: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - use_combined_mask: BOOLEAN default=False
  - use_square_mask: BOOLEAN default=True
- optional:
  - combined_bounding_box: BBOX default=None
- outputs: IMAGE:IMAGE

## BboxToInt
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking
- required:
  - bboxes: BBOX
  - index: INT default=0 min=0 max=99999999 step=1
- outputs: x_min:INT, y_min:INT, width:INT, height:INT, center_x:INT, center_y:INT

## BboxVisualize
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking
- required:
  - images: IMAGE
  - bboxes: BBOX
  - line_width: INT default=1 min=1 max=10 step=1
  - bbox_format: COMBO[xywh, xyxy] default='xywh'
- outputs: images:IMAGE

## BeebleSwitchXImageEdit
module: comfy_api_nodes.nodes_beeble | category: partner/image/Beeble
- required:
  - image: IMAGE
  - prompt: STRING default=''
  - alpha_mode: COMFY_DYNAMICCOMBO_V3
  - max_resolution: COMBO[1080p, 720p] default='1080p'
  - seed: INT default=0 min=0 max=2147483647
- optional:
  - reference_image: IMAGE
- outputs: image:IMAGE, alpha:MASK

## BeebleSwitchXVideoEdit
module: comfy_api_nodes.nodes_beeble | category: partner/video/Beeble
- required:
  - video: VIDEO
  - prompt: STRING default=''
  - alpha_mode: COMFY_DYNAMICCOMBO_V3
  - max_resolution: COMBO[1080p, 720p] default='1080p'
  - seed: INT default=0 min=0 max=2147483647
- optional:
  - reference_image: IMAGE
- outputs: video:VIDEO, alpha:VIDEO

## BerniniConditioning
module: comfy_extras.nodes_bernini | category: model/conditioning/bernini
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - width: INT default=832 min=16 max=8192 step=16
  - height: INT default=480 min=16 max=8192 step=16
  - length: INT default=81 min=1 max=8192 step=4
  - batch_size: INT default=1 min=1 max=4096
- optional:
  - source_video: IMAGE
  - reference_video: IMAGE
  - reference_images: COMFY_AUTOGROW_V3
  - ref_max_size: INT default=848 min=16 max=8192 step=16
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## BetaSamplingScheduler
module: comfy_extras.nodes_custom_sampler | category: model/sampling/schedulers
- required:
  - model: MODEL
  - steps: INT default=20 min=1 max=10000
  - alpha: FLOAT default=0.6 min=0.0 max=50.0 step=0.01
  - beta: FLOAT default=0.6 min=0.0 max=50.0 step=0.01
- outputs: SIGMAS:SIGMAS

## BinaryPreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Line Extractors
- required:
  - image: IMAGE
- optional:
  - bin_threshold: INT default=100 min=0 max=255 step=1
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## BlockifyMask
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking
- required:
  - masks: MASK
  - block_size: INT default=32 min=8 max=512 step=1
- optional:
  - device: COMBO[cpu, gpu] default='cpu'
- outputs: mask:MASK

## BlockSparseAttention
module: comfy_extras.nodes_sparse_attention | category: model/patch
- required:
  - model: MODEL
  - selection: COMFY_DYNAMICCOMBO_V3
  - start_percent: FLOAT default=0.2 min=0.0 max=1.0 step=0.01
  - end_percent: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - dense_blocks: STRING default=''
  - min_tokens: INT default=12288 min=0 max=1048576 step=512
  - extra_tokens: INT default=256 min=0 max=256 step=64
  - sink_conditioning: COMBO[exact_kv, exact_kv_and_rows, off] default='exact_kv_and_rows'
  - verbose: BOOLEAN default=False
- outputs: model:MODEL

## BOOLConstant
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/constants
- required:
  - value: BOOLEAN default=True
- outputs: value:BOOLEAN

## BriaAddObject
module: comfy_api_nodes.nodes_bria | category: partner/image/Bria
- required:
  - image: IMAGE
  - instruction: STRING default=''
  - seed: INT default=42 min=0 max=2147483647 step=1
  - moderation: COMFY_DYNAMICCOMBO_V3
- outputs: IMAGE:IMAGE, structured_prompt:STRING

## BriaEraseByText
module: comfy_api_nodes.nodes_bria | category: partner/image/Bria
- required:
  - image: IMAGE
  - object_name: STRING default=''
  - moderation: COMFY_DYNAMICCOMBO_V3
- outputs: IMAGE:IMAGE, structured_prompt:STRING

## BriaEraseForeground
module: comfy_api_nodes.nodes_bria | category: partner/image/Bria
- required:
  - image: IMAGE
  - moderation: COMFY_DYNAMICCOMBO_V3
- outputs: IMAGE:IMAGE

## BriaEraser
module: comfy_api_nodes.nodes_bria | category: partner/image/Bria
- required:
  - image: IMAGE
  - mask: MASK
  - mask_type: COMBO[manual, automatic]
  - moderation: COMFY_DYNAMICCOMBO_V3
- outputs: IMAGE:IMAGE

## BriaExpandImage
module: comfy_api_nodes.nodes_bria | category: partner/image/Bria
- required:
  - image: IMAGE
  - expand_mode: COMFY_DYNAMICCOMBO_V3
  - prompt: STRING default=''
  - negative_prompt: STRING default=''
  - seed: INT default=42 min=1 max=2147483647 step=1
  - moderation: COMFY_DYNAMICCOMBO_V3
- outputs: IMAGE:IMAGE, prompt:STRING

## BriaGenFill
module: comfy_api_nodes.nodes_bria | category: partner/image/Bria
- required:
  - image: IMAGE
  - mask: MASK
  - prompt: STRING default=''
  - negative_prompt: STRING default=''
  - refine_prompt: BOOLEAN default=True
  - seed: INT default=42 min=1 max=2147483647 step=1
  - moderation: COMFY_DYNAMICCOMBO_V3
- outputs: IMAGE:IMAGE

## BriaImageEditNode
module: comfy_api_nodes.nodes_bria | category: partner/image/Bria
- required:
  - model: COMBO[FIBO]
  - image: IMAGE
  - prompt: STRING default=''
  - negative_prompt: STRING default=''
  - structured_prompt: STRING default=''
  - seed: INT default=1 min=1 max=2147483647 step=1
  - guidance_scale: FLOAT default=3 min=3 max=5 step=0.01
  - steps: INT default=50 min=20 max=50 step=1
  - moderation: COMFY_DYNAMICCOMBO_V3
- optional:
  - mask: MASK
- outputs: IMAGE:IMAGE, structured_prompt:STRING

## BriaIncreaseResolution
module: comfy_api_nodes.nodes_bria | category: partner/image/Bria
- required:
  - image: IMAGE
  - desired_increase: COMBO[2, 4]
  - auto_downscale: BOOLEAN default=False
  - moderation: COMFY_DYNAMICCOMBO_V3
- outputs: IMAGE:IMAGE

## BriaRelight
module: comfy_api_nodes.nodes_bria | category: partner/image/Bria
- required:
  - image: IMAGE
  - light_type: COMBO[midday, blue hour light, low-angle sunlight, sunrise light, spotlight on subject, overcast light, soft overcast daylight lighting, cloud-filtered lighting, fog-diffused lighting, moonlight lighting, ... +3]
  - light_direction: COMBO[front, side, bottom, top-down]
  - moderation: COMFY_DYNAMICCOMBO_V3
- outputs: IMAGE:IMAGE, structured_prompt:STRING

## BriaRemoveImageBackground
module: comfy_api_nodes.nodes_bria | category: partner/image/Bria
- required:
  - image: IMAGE
  - moderation: COMFY_DYNAMICCOMBO_V3
  - seed: INT default=0 min=0 max=2147483647
- outputs: IMAGE:IMAGE

## BriaRemoveVideoBackground
module: comfy_api_nodes.nodes_bria | category: partner/video/Bria
- required:
  - video: VIDEO
  - background_color: COMBO[Black, White, Gray, Red, Green, Blue, Yellow, Cyan, Magenta, Orange]
  - seed: INT default=0 min=0 max=2147483647
- outputs: VIDEO:VIDEO

## BriaReplaceImageBackground
module: comfy_api_nodes.nodes_bria | category: partner/image/Bria
- required:
  - image: IMAGE
  - background: COMFY_DYNAMICCOMBO_V3
  - original_quality: BOOLEAN default=False
  - seed: INT default=42 min=0 max=2147483647 step=1
  - moderation: COMFY_DYNAMICCOMBO_V3
- outputs: IMAGE:IMAGE, refined_prompt:STRING

## BriaReplaceObject
module: comfy_api_nodes.nodes_bria | category: partner/image/Bria
- required:
  - image: IMAGE
  - instruction: STRING default=''
  - seed: INT default=42 min=0 max=2147483647 step=1
  - moderation: COMFY_DYNAMICCOMBO_V3
- outputs: IMAGE:IMAGE, structured_prompt:STRING

## BriaReseason
module: comfy_api_nodes.nodes_bria | category: partner/image/Bria
- required:
  - image: IMAGE
  - season: COMBO[spring, summer, autumn, winter]
  - moderation: COMFY_DYNAMICCOMBO_V3
- outputs: IMAGE:IMAGE, structured_prompt:STRING

## BriaRestorePhoto
module: comfy_api_nodes.nodes_bria | category: partner/image/Bria
- required:
  - image: IMAGE
  - moderation: COMFY_DYNAMICCOMBO_V3
- outputs: IMAGE:IMAGE, structured_prompt:STRING

## BriaTransparentVideoBackground
module: comfy_api_nodes.nodes_bria | category: partner/video/Bria
- required:
  - video: VIDEO
  - seed: INT default=0 min=0 max=2147483647
- outputs: images:IMAGE, mask:MASK

## BriaVideoEraser
module: comfy_api_nodes.nodes_bria | category: partner/video/Bria
- required:
  - video: VIDEO
  - preserve_audio: BOOLEAN default=True
- optional:
  - mask: MASK
  - mask_video: VIDEO
- outputs: VIDEO:VIDEO

## BriaVideoGreenScreen
module: comfy_api_nodes.nodes_bria | category: partner/video/Bria
- required:
  - video: VIDEO
  - green_shade: COMBO[broadcast_green, chroma_green, blue_screen]
  - seed: INT default=0 min=0 max=2147483647
- outputs: VIDEO:VIDEO

## BriaVideoReplaceBackground
module: comfy_api_nodes.nodes_bria | category: partner/video/Bria
- required:
  - video: VIDEO
  - seed: INT default=0 min=0 max=2147483647
- optional:
  - background_image: IMAGE
  - background_video: VIDEO
- outputs: VIDEO:VIDEO

## BuildJsonPromptIdeogram
module: comfy_extras.nodes_json_prompt | category: text
- required:
  - element: ARRAY
  - high_level_description: STRING default=''
  - background: STRING default=''
  - style: COMFY_DYNAMICCOMBO_V3
  - aesthetics: STRING default=''
  - lighting: STRING default=''
  - medium: STRING default=''
  - color_palette: COLORS default=[]
- outputs: prompt:DICT

## BuildPoseFile
module: comfy_extras.nodes_sam3d_body | category: 3d
- required:
  - pose_data: MHR_POSE_DATA,KIMODO_POSE_DATA
  - format: COMFY_DYNAMICCOMBO_V3
  - fps: FLOAT default=24.0 min=1.0 max=240.0 step=1.0
  - camera_translation: COMBO[off, centered, absolute] default='off'
  - track_index: INT default=-1 min=-1 max=15
- optional:
  - sam3d_body_model: SAM3D_BODY_MODEL
- outputs: model_3d:FILE_3D

## ByteDance2DraftToFinalVideoNode
module: comfy_api_nodes.nodes_bytedance | category: partner/video/ByteDance
- required:
  - draft_task_id: STRING default=''
  - watermark: BOOLEAN default=False
- outputs: VIDEO:VIDEO

## ByteDance2FirstLastFrameNode
module: comfy_api_nodes.nodes_bytedance | category: partner/video/ByteDance
- required:
  - model: COMFY_DYNAMICCOMBO_V3
  - seed: INT default=0 min=0 max=2147483647 step=1
  - watermark: BOOLEAN default=False
- optional:
  - first_frame: IMAGE
  - last_frame: IMAGE
  - first_frame_asset_id: STRING default=''
  - last_frame_asset_id: STRING default=''
- outputs: VIDEO:VIDEO, draft_task_id:STRING

## ByteDance2ReferenceNode
module: comfy_api_nodes.nodes_bytedance | category: partner/video/ByteDance
- required:
  - model: COMFY_DYNAMICCOMBO_V3
  - seed: INT default=0 min=0 max=2147483647 step=1
  - watermark: BOOLEAN default=False
- outputs: VIDEO:VIDEO

## ByteDance2ReferenceNodeV2
module: comfy_api_nodes.nodes_bytedance | category: partner/video/ByteDance
- required:
  - model: COMFY_DYNAMICCOMBO_V3
  - seed: INT default=0 min=0 max=2147483647 step=1
  - watermark: BOOLEAN default=False
- outputs: VIDEO:VIDEO, draft_task_id:STRING

## ByteDance2TextToVideoNode
module: comfy_api_nodes.nodes_bytedance | category: partner/video/ByteDance
- required:
  - model: COMFY_DYNAMICCOMBO_V3
  - seed: INT default=0 min=0 max=2147483647 step=1
  - watermark: BOOLEAN default=False
- outputs: VIDEO:VIDEO, draft_task_id:STRING

## ByteDanceCreateImageAsset
module: comfy_api_nodes.nodes_bytedance | category: partner/image/ByteDance
- required:
  - image: IMAGE
  - group_id: STRING default=''
- outputs: asset_id:STRING, group_id:STRING

## ByteDanceCreateVideoAsset
module: comfy_api_nodes.nodes_bytedance | category: partner/video/ByteDance
- required:
  - video: VIDEO
  - group_id: STRING default=''
- outputs: asset_id:STRING, group_id:STRING

## ByteDanceFirstLastFrameNode
module: comfy_api_nodes.nodes_bytedance | category: partner/video/ByteDance
- required:
  - model: COMBO[seedance-1-5-pro-251215, seedance-1-0-pro-250528] default='seedance-1-5-pro-251215'
  - prompt: STRING
  - first_frame: IMAGE
  - last_frame: IMAGE
  - resolution: COMBO[480p, 720p, 1080p]
  - aspect_ratio: COMBO[adaptive, 16:9, 4:3, 1:1, 3:4, 9:16, 21:9]
  - duration: INT default=5 min=3 max=12 step=1
- optional:
  - seed: INT default=0 min=0 max=2147483647 step=1
  - camera_fixed: BOOLEAN default=False
  - watermark: BOOLEAN default=False
  - generate_audio: BOOLEAN default=False
- outputs: VIDEO:VIDEO

## ByteDanceImageToVideoNode
module: comfy_api_nodes.nodes_bytedance | category: partner/video/ByteDance
- required:
  - model: COMBO[seedance-1-5-pro-251215, seedance-1-0-pro-250528, seedance-1-0-pro-fast-251015] default='seedance-1-0-pro-fast-251015'
  - prompt: STRING
  - image: IMAGE
  - resolution: COMBO[480p, 720p, 1080p]
  - aspect_ratio: COMBO[adaptive, 16:9, 4:3, 1:1, 3:4, 9:16, 21:9]
  - duration: INT default=5 min=3 max=12 step=1
- optional:
  - seed: INT default=0 min=0 max=2147483647 step=1
  - camera_fixed: BOOLEAN default=False
  - watermark: BOOLEAN default=False
  - generate_audio: BOOLEAN default=False
- outputs: VIDEO:VIDEO

## ByteDanceSeedAudio
module: comfy_api_nodes.nodes_bytedance | category: partner/audio/ByteDance
- required:
  - text_prompt: STRING default=''
  - reference_mode: COMFY_DYNAMICCOMBO_V3
  - sample_rate: COMBO[8000, 16000, 24000, 32000, 44100, 48000] default='24000'
  - speech_rate: INT default=0 min=-50 max=100
  - loudness_rate: INT default=0 min=-50 max=100
  - pitch_rate: INT default=0 min=-12 max=12
  - seed: INT default=42 min=0 max=2147483647
- optional:
  - model: COMBO[seed-audio-1.0-multilingual, seed-audio-1.0] default='seed-audio-1.0-multilingual'
- outputs: AUDIO:AUDIO

## ByteDanceSeedNode
module: comfy_api_nodes.nodes_bytedance_llm | category: partner/text/ByteDance
- required:
  - prompt: STRING default=''
  - model: COMFY_DYNAMICCOMBO_V3
  - seed: INT default=0 min=0 max=2147483647
- optional:
  - system_prompt: STRING default=''
- outputs: STRING:STRING

## ByteDanceSeedreamLayerSeparationNode
module: comfy_api_nodes.nodes_bytedance | category: partner/image/ByteDance
- required:
  - image: IMAGE
  - prompt: STRING default=''
  - size: COMBO[auto, 1K, 1.5K, 2K] default='auto'
  - seed: INT default=0 min=0 max=2147483647 step=1
- optional:
  - prompt_optimization: COMBO[standard, fast] default='standard'
  - watermark: BOOLEAN default=False
  - crop_layers: BOOLEAN default=False
- outputs: base_image:IMAGE, base_mask:MASK, layers:IMAGE, masks:MASK, bboxes:BOUNDING_BOX, layer_stack:LAYERS

## ByteDanceSeedreamLayerSeparationNodeV2
module: comfy_api_nodes.nodes_bytedance | category: partner/image/ByteDance
- required:
  - model: COMFY_DYNAMICCOMBO_V3
- outputs: base_image:IMAGE, base_mask:MASK, layers:IMAGE, masks:MASK, bboxes:BOUNDING_BOX, layer_stack:LAYERS

## ByteDanceSeedreamNode
module: comfy_api_nodes.nodes_bytedance | category: partner/image/ByteDance
- required:
  - model: COMBO[seedream 5.0 pro, seedream 5.0 lite, seedream-4-5-251128, seedream-4-0-250828]
  - prompt: STRING default=''
  - size_preset: COMBO[2048x2048 (1:1), 2304x1728 (4:3), 1728x2304 (3:4), 2560x1440 (16:9), 1440x2560 (9:16), 2496x1664 (3:2), 1664x2496 (2:3), 3024x1296 (21:9), 3072x3072 (1:1), 4096x4096 (1:1), ... +1]
- optional:
  - image: IMAGE
  - width: INT default=2048 min=1024 max=6240 step=2
  - height: INT default=2048 min=1024 max=4992 step=2
  - sequential_image_generation: COMBO[disabled, auto]
  - max_images: INT default=1 min=1 max=15 step=1
  - seed: INT default=0 min=0 max=2147483647 step=1
  - watermark: BOOLEAN default=False
  - fail_on_partial: BOOLEAN default=True
- outputs: IMAGE:IMAGE

## ByteDanceSeedreamNodeV2
module: comfy_api_nodes.nodes_bytedance | category: partner/image/ByteDance
- required:
  - prompt: STRING default=''
  - model: COMFY_DYNAMICCOMBO_V3
  - seed: INT default=0 min=0 max=2147483647 step=1
  - watermark: BOOLEAN default=False
- optional:
  - thinking: BOOLEAN default=True
- outputs: IMAGE:IMAGE

## ByteDanceSeedreamNodeV3
module: comfy_api_nodes.nodes_bytedance | category: partner/image/ByteDance
- required:
  - prompt: STRING default=''
  - model: COMFY_DYNAMICCOMBO_V3
- outputs: IMAGE:IMAGE

## ByteDanceTextToVideoNode
module: comfy_api_nodes.nodes_bytedance | category: partner/video/ByteDance
- required:
  - model: COMBO[seedance-1-5-pro-251215, seedance-1-0-pro-250528, seedance-1-0-pro-fast-251015] default='seedance-1-0-pro-fast-251015'
  - prompt: STRING
  - resolution: COMBO[480p, 720p, 1080p]
  - aspect_ratio: COMBO[16:9, 4:3, 1:1, 3:4, 9:16, 21:9]
  - duration: INT default=5 min=3 max=12 step=1
- optional:
  - seed: INT default=0 min=0 max=2147483647 step=1
  - camera_fixed: BOOLEAN default=False
  - watermark: BOOLEAN default=False
  - generate_audio: BOOLEAN default=False
- outputs: VIDEO:VIDEO

## ByteDanceVideoEnhanceNode
module: comfy_api_nodes.nodes_bytedance | category: partner/video/ByteDance
- required:
  - video: VIDEO
  - tool_version: COMFY_DYNAMICCOMBO_V3
  - resolution: COMFY_DYNAMICCOMBO_V3
  - fps: COMBO[source, 24, 25, 30, 48, 50, 60, 120] default='source'
  - bitrate_level: COMBO[low, medium, high] default='medium'
- outputs: VIDEO:VIDEO

## CameraPoseVisualizer
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/misc
- required:
  - pose_file_path: STRING default=''
  - base_xval: FLOAT default=0.2 min=0 max=100 step=0.01
  - zval: FLOAT default=0.3 min=0 max=100 step=0.01
  - scale: FLOAT default=1.0 min=0.01 max=10.0 step=0.01
  - use_exact_fx: BOOLEAN default=False
  - relative_c2w: BOOLEAN default=True
  - use_viewer: BOOLEAN default=False
- optional:
  - cameractrl_poses: CAMERACTRL_POSES default=None
- outputs: IMAGE:IMAGE

## Canny
module: comfy_extras.nodes_canny | category: image/filters
- required:
  - image: IMAGE
  - low_threshold: FLOAT default=0.4 min=0.01 max=0.99 step=0.01
  - high_threshold: FLOAT default=0.8 min=0.01 max=0.99 step=0.01
- outputs: IMAGE:IMAGE

## CannyEdgePreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Line Extractors
- required:
  - image: IMAGE
- optional:
  - low_threshold: INT default=100 min=0 max=255 step=1
  - high_threshold: INT default=200 min=0 max=255 step=1
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## CaseConverter
module: comfy_extras.nodes_string | category: text
- required:
  - string: STRING
  - mode: COMBO[UPPERCASE, lowercase, Capitalize, Title Case]
- outputs: STRING:STRING

## CenterCropImages
module: comfy_extras.nodes_dataset | category: image/transform
- required:
  - images: IMAGE
  - width: INT default=512 min=1 max=8192
  - height: INT default=512 min=1 max=8192
- outputs: images:IMAGE

## CFGGuider
module: comfy_extras.nodes_custom_sampler | category: model/sampling/guiders
- required:
  - model: MODEL
  - positive: CONDITIONING
  - negative: CONDITIONING
  - cfg: FLOAT default=8.0 min=0.0 max=100.0 step=0.1
- outputs: GUIDER:GUIDER

## CFGNorm
module: comfy_extras.nodes_cfg | category: advanced/guidance
- required:
  - model: MODEL
  - strength: FLOAT default=1.0 min=0.0 max=100.0 step=0.01
- optional:
  - pre_cfg: BOOLEAN default=False
- outputs: patched_model:MODEL

## CFGOverride
module: comfy_extras.nodes_custom_sampler | category: model/sampling/guiders
- required:
  - model: MODEL
  - cfg: FLOAT default=1.0 min=0.0 max=100.0 step=0.1
  - start_percent: FLOAT default=0.0 min=0.0 max=1.0 step=0.001
  - end_percent: FLOAT default=1.0 min=0.0 max=1.0 step=0.001
- outputs: MODEL:MODEL

## CFGZeroStar
module: comfy_extras.nodes_cfg | category: advanced/guidance
- required:
  - model: MODEL
- outputs: patched_model:MODEL

## CFGZeroStarAndInit
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/experimental
- required:
  - model: MODEL
  - use_zero_init: BOOLEAN default=True
  - zero_init_steps: INT default=0 min=0
- outputs: MODEL:MODEL

## CheckpointLoader
module: nodes | category: model/loaders
- required:
  - config_name: COMBO[anything_v3.yaml, v1-inference.yaml, v1-inference_clip_skip_2.yaml, v1-inference_clip_skip_2_fp16.yaml, v1-inference_fp16.yaml, v1-inpainting-inference.yaml, v2-inference-v.yaml, v2-inference-v_fp32.yaml, v2-inference.yaml, v2-inference_fp32.yaml, ... +1]
  - ckpt_name: COMBO[]
- outputs: MODEL:MODEL, CLIP:CLIP, VAE:VAE

## CheckpointLoaderKJ
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/model_loaders
- required:
  - ckpt_name: COMBO[]
  - weight_dtype: COMBO[default, fp8_e4m3fn, fp8_e4m3fn_fast, fp8_e5m2, fp16, bf16, fp32]
  - compute_dtype: COMBO[default, fp16, bf16, fp32] default='default'
  - patch_cublaslinear: BOOLEAN default=False
  - sage_attention: COMBO[disabled, auto, sageattn_qk_int8_pv_fp16_cuda, sageattn_qk_int8_pv_fp16_triton, sageattn_qk_int8_pv_fp8_cuda, sageattn_qk_int8_pv_fp8_cuda++, sageattn3, sageattn3_per_block_mean] default=False
  - enable_fp16_accumulation: BOOLEAN default=False
- outputs: MODEL:MODEL, CLIP:CLIP, VAE:VAE

## CheckpointLoaderSimple
module: nodes | category: model/loaders
- required:
  - ckpt_name: COMBO[]
- outputs: MODEL:MODEL, CLIP:CLIP, VAE:VAE

## CheckpointLoader|pysssss
module: custom_nodes.ComfyUI-Custom-Scripts | category: model/loaders
- required:
  - ckpt_name: COMBO[]
- optional:
  - prompt: STRING
- outputs: MODEL:MODEL, CLIP:CLIP, VAE:VAE, example:STRING

## CheckpointPerturbWeights
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/experimental
- required:
  - model: MODEL
  - joint_blocks: FLOAT default=0.02 min=0.001 max=10.0 step=0.001
  - final_layer: FLOAT default=0.02 min=0.001 max=10.0 step=0.001
  - rest_of_the_blocks: FLOAT default=0.02 min=0.001 max=10.0 step=0.001
  - seed: INT default=123 min=0 max=18446744073709551615 step=1
- outputs: MODEL:MODEL

## CheckpointSave
module: comfy_extras.nodes_model_merging | category: model/merging
- required:
  - model: MODEL
  - clip: CLIP
  - vae: VAE
  - filename_prefix: STRING default='checkpoints/ComfyUI'
- outputs: 

## ChromaRadianceOptions
module: comfy_extras.nodes_chroma_radiance | category: model/patch/chroma radiance
- required:
  - model: MODEL
  - preserve_wrapper: BOOLEAN default=True
  - start_sigma: FLOAT default=1.0 min=0.0 max=1.0
  - end_sigma: FLOAT default=0.0 min=0.0 max=1.0
  - nerf_tile_size: INT default=-1 min=-1
  - force_sequential_txt_ids: BOOLEAN default=False
- outputs: MODEL:MODEL

## ClaudeNode
module: comfy_api_nodes.nodes_anthropic | category: partner/text/Anthropic
- required:
  - prompt: STRING default=''
  - model: COMFY_DYNAMICCOMBO_V3
  - seed: INT default=0 min=0 max=2147483647
  - images: COMFY_AUTOGROW_V3
- optional:
  - system_prompt: STRING default=''
- outputs: STRING:STRING

## CLIPAttentionMultiply
module: comfy_extras.nodes_attention_multiply | category: experimental/attention_experiments
- required:
  - clip: CLIP
  - q: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - k: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - v: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - out: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
- outputs: CLIP:CLIP

## CLIPLoader
module: nodes | category: model/loaders
- required:
  - clip_name: COMBO[clip_l.safetensors, qwen3vl_32b_minimax_h3_int4_convrot.safetensors, qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors, qwen_3_4b.safetensors, qwen_3_8b_fp8mixed.safetensors, umt5_xxl_fp8_e4m3fn_scaled.safetensors]
  - type: COMBO[stable_diffusion, stable_cascade, sd3, stable_audio, mochi, ltxv, pixart, cosmos, lumina2, wan, ... +19]
- optional:
  - device: COMBO[default, cpu]
- outputs: CLIP:CLIP

## CLIPLoaderGGUF
module: custom_nodes.ComfyUI-GGUF | category: bootleg
- required:
  - clip_name: COMBO[clip_l.safetensors, qwen3vl_32b_minimax_h3_int4_convrot.safetensors, qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors, qwen_3_4b.safetensors, qwen_3_8b_fp8mixed.safetensors, umt5_xxl_fp8_e4m3fn_scaled.safetensors]
  - type: COMBO[stable_diffusion, stable_cascade, sd3, stable_audio, mochi, ltxv, pixart, cosmos, lumina2, wan, ... +19]
- outputs: CLIP:CLIP

## CLIPMergeAdd
module: comfy_extras.nodes_model_merging | category: model/merging
- required:
  - clip1: CLIP
  - clip2: CLIP
- outputs: CLIP:CLIP

## CLIPMergeSimple
module: comfy_extras.nodes_model_merging | category: model/merging
- required:
  - clip1: CLIP
  - clip2: CLIP
  - ratio: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: CLIP:CLIP

## CLIPMergeSubtract
module: comfy_extras.nodes_model_merging | category: model/merging
- required:
  - clip1: CLIP
  - clip2: CLIP
  - multiplier: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
- outputs: CLIP:CLIP

## CLIPSave
module: comfy_extras.nodes_model_merging | category: model/merging
- required:
  - clip: CLIP
  - filename_prefix: STRING default='clip/ComfyUI'
- outputs: 

## CLIPSetLastLayer
module: nodes | category: model/conditioning
- required:
  - clip: CLIP
  - stop_at_clip_layer: INT default=-1 min=-24 max=-1 step=1
- outputs: CLIP:CLIP

## CLIPTextEncode
module: nodes | category: model/conditioning
- required:
  - text: STRING
  - clip: CLIP
- outputs: CONDITIONING:CONDITIONING

## CLIPTextEncodeControlnet
module: comfy_extras.nodes_cond | category: model/conditioning
- required:
  - clip: CLIP
  - conditioning: CONDITIONING
  - text: STRING
- outputs: CONDITIONING:CONDITIONING

## CLIPTextEncodeFlux
module: comfy_extras.nodes_flux | category: model/conditioning/flux
- required:
  - clip: CLIP
  - clip_l: STRING
  - t5xxl: STRING
  - guidance: FLOAT default=3.5 min=0.0 max=100.0 step=0.1
- outputs: CONDITIONING:CONDITIONING

## CLIPTextEncodeHiDream
module: comfy_extras.nodes_hidream | category: model/conditioning/hidream
- required:
  - clip: CLIP
  - clip_l: STRING
  - clip_g: STRING
  - t5xxl: STRING
  - llama: STRING
- outputs: CONDITIONING:CONDITIONING

## CLIPTextEncodeHunyuanDiT
module: comfy_extras.nodes_hunyuan | category: model/conditioning/hunyuan image
- required:
  - clip: CLIP
  - bert: STRING
  - mt5xl: STRING
- outputs: CONDITIONING:CONDITIONING

## CLIPTextEncodeKandinsky5
module: comfy_extras.nodes_kandinsky5 | category: model/conditioning/kandinsky
- required:
  - clip: CLIP
  - clip_l: STRING
  - qwen25_7b: STRING
- outputs: CONDITIONING:CONDITIONING

## CLIPTextEncodeLumina2
module: comfy_extras.nodes_lumina2 | category: model/conditioning/lumina
- required:
  - system_prompt: COMBO[superior, alignment]
  - user_prompt: STRING
  - clip: CLIP
- outputs: CONDITIONING:CONDITIONING

## CLIPTextEncodePixArtAlpha
module: comfy_extras.nodes_pixart | category: model/conditioning/pixart
- required:
  - width: INT default=1024 min=0 max=16384
  - height: INT default=1024 min=0 max=16384
  - text: STRING
  - clip: CLIP
- outputs: CONDITIONING:CONDITIONING

## CLIPTextEncodeSD3
module: comfy_extras.nodes_sd3 | category: model/conditioning/stable diffusion
- required:
  - clip: CLIP
  - clip_l: STRING
  - clip_g: STRING
  - t5xxl: STRING
  - empty_padding: COMBO[none, empty_prompt]
- outputs: CONDITIONING:CONDITIONING

## CLIPTextEncodeSDXL
module: comfy_extras.nodes_clip_sdxl | category: model/conditioning/stable diffusion
- required:
  - clip: CLIP
  - width: INT default=1024 min=0 max=16384
  - height: INT default=1024 min=0 max=16384
  - crop_w: INT default=0 min=0 max=16384
  - crop_h: INT default=0 min=0 max=16384
  - target_width: INT default=1024 min=0 max=16384
  - target_height: INT default=1024 min=0 max=16384
  - text_g: STRING
  - text_l: STRING
- outputs: CONDITIONING:CONDITIONING

## CLIPTextEncodeSDXL+
module: custom_nodes.ComfyUI_essentials | category: essentials/conditioning
- required:
  - width: INT default=1024.0 min=0 max=16384
  - height: INT default=1024.0 min=0 max=16384
  - size_cond_factor: INT default=4 min=1 max=16
  - text: STRING default=''
  - clip: CLIP
- outputs: CONDITIONING:CONDITIONING

## CLIPTextEncodeSDXLRefiner
module: comfy_extras.nodes_clip_sdxl | category: model/conditioning/stable diffusion
- required:
  - ascore: FLOAT default=6.0 min=0.0 max=1000.0 step=0.01
  - width: INT default=1024 min=0 max=16384
  - height: INT default=1024 min=0 max=16384
  - text: STRING
  - clip: CLIP
- outputs: CONDITIONING:CONDITIONING

## CLIPVisionEncode
module: nodes | category: model/conditioning
- required:
  - clip_vision: CLIP_VISION
  - image: IMAGE
  - crop: COMBO[center, none]
- outputs: CLIP_VISION_OUTPUT:CLIP_VISION_OUTPUT

## CLIPVisionLoader
module: nodes | category: model/loaders
- required:
  - clip_name: COMBO[clip_vision_h.safetensors]
- outputs: CLIP_VISION:CLIP_VISION

## CM_BoolBinaryOperation
module: custom_nodes.ComfyMath | category: math/bool
- required:
  - op: COMBO[Nor, Xor, Nand, And, Xnor, Or, Eq, Neq]
  - a: BOOLEAN default=False
  - b: BOOLEAN default=False
- outputs: BOOLEAN:BOOLEAN

## CM_BoolToInt
module: custom_nodes.ComfyMath | category: math/conversion
- required:
  - a: BOOLEAN default=False
- outputs: INT:INT

## CM_BoolUnaryOperation
module: custom_nodes.ComfyMath | category: math/bool
- required:
  - op: COMBO[Not]
  - a: BOOLEAN default=False
- outputs: BOOLEAN:BOOLEAN

## CM_BreakoutVec2
module: custom_nodes.ComfyMath | category: math/conversion
- required:
  - a: VEC2 default=[0.0, 0.0]
- outputs: FLOAT:FLOAT, FLOAT:FLOAT

## CM_BreakoutVec3
module: custom_nodes.ComfyMath | category: math/conversion
- required:
  - a: VEC3 default=[0.0, 0.0, 0.0]
- outputs: FLOAT:FLOAT, FLOAT:FLOAT, FLOAT:FLOAT

## CM_BreakoutVec4
module: custom_nodes.ComfyMath | category: math/conversion
- required:
  - a: VEC4 default=[0.0, 0.0, 0.0, 0.0]
- outputs: FLOAT:FLOAT, FLOAT:FLOAT, FLOAT:FLOAT, FLOAT:FLOAT

## CM_ComposeVec2
module: custom_nodes.ComfyMath | category: math/conversion
- required:
  - x: FLOAT default=0.0
  - y: FLOAT default=0.0
- outputs: VEC2:VEC2

## CM_ComposeVec3
module: custom_nodes.ComfyMath | category: math/conversion
- required:
  - x: FLOAT default=0.0
  - y: FLOAT default=0.0
  - z: FLOAT default=0.0
- outputs: VEC3:VEC3

## CM_ComposeVec4
module: custom_nodes.ComfyMath | category: math/conversion
- required:
  - x: FLOAT default=0.0
  - y: FLOAT default=0.0
  - z: FLOAT default=0.0
  - w: FLOAT default=0.0
- outputs: VEC4:VEC4

## CM_FloatBinaryCondition
module: custom_nodes.ComfyMath | category: math/float
- required:
  - op: COMBO[Eq, Neq, Gt, Gte, Lt, Lte]
  - a: FLOAT default=0.0 step=0.001
  - b: FLOAT default=0.0 step=0.001
- outputs: BOOLEAN:BOOLEAN

## CM_FloatBinaryOperation
module: custom_nodes.ComfyMath | category: math/float
- required:
  - op: COMBO[Add, Sub, Mul, Div, Mod, Pow, FloorDiv, Max, Min, Log, ... +1]
  - a: FLOAT default=0.0 step=0.001
  - b: FLOAT default=0.0 step=0.001
- outputs: FLOAT:FLOAT

## CM_FloatToInt
module: custom_nodes.ComfyMath | category: math/conversion
- required:
  - a: FLOAT default=0.0
- outputs: INT:INT

## CM_FloatToNumber
module: custom_nodes.ComfyMath | category: math/conversion
- required:
  - a: FLOAT default=0.0
- outputs: NUMBER:NUMBER

## CM_FloatUnaryCondition
module: custom_nodes.ComfyMath | category: math/float
- required:
  - op: COMBO[IsZero, IsPositive, IsNegative, IsNonZero, IsPositiveInfinity, IsNegativeInfinity, IsNaN, IsFinite, IsInfinite, IsEven, ... +1]
  - a: FLOAT default=0.0 step=0.001
- outputs: BOOLEAN:BOOLEAN

## CM_FloatUnaryOperation
module: custom_nodes.ComfyMath | category: math/float
- required:
  - op: COMBO[Neg, Inc, Dec, Abs, Sqr, Cube, Sqrt, Exp, Ln, Log10, ... +22]
  - a: FLOAT default=0.0 step=0.001
- outputs: FLOAT:FLOAT

## CM_IntBinaryCondition
module: custom_nodes.ComfyMath | category: math/int
- required:
  - op: COMBO[Eq, Neq, Gt, Lt, Geq, Leq]
  - a: INT default=0
  - b: INT default=0
- outputs: BOOL:BOOL

## CM_IntBinaryOperation
module: custom_nodes.ComfyMath | category: math/int
- required:
  - op: COMBO[Add, Sub, Mul, Div, Mod, Pow, And, Nand, Or, Nor, ... +6]
  - a: INT default=0
  - b: INT default=0
- outputs: INT:INT

## CM_IntToBool
module: custom_nodes.ComfyMath | category: math/conversion
- required:
  - a: INT default=0
- outputs: BOOLEAN:BOOLEAN

## CM_IntToFloat
module: custom_nodes.ComfyMath | category: math/conversion
- required:
  - a: INT default=0
- outputs: FLOAT:FLOAT

## CM_IntToNumber
module: custom_nodes.ComfyMath | category: math/conversion
- required:
  - a: INT default=0
- outputs: NUMBER:NUMBER

## CM_IntUnaryCondition
module: custom_nodes.ComfyMath | category: math/int
- required:
  - op: COMBO[IsZero, IsNonZero, IsPositive, IsNegative, IsEven, IsOdd]
  - a: INT default=0
- outputs: BOOL:BOOL

## CM_IntUnaryOperation
module: custom_nodes.ComfyMath | category: math/int
- required:
  - op: COMBO[Abs, Neg, Inc, Dec, Sqr, Cube, Not, Factorial]
  - a: INT default=0
- outputs: INT:INT

## CM_NearestSDXLExtendedResolution
module: custom_nodes.ComfyMath | category: math/graphics
- required:
  - image: IMAGE
- outputs: width:INT, height:INT

## CM_NearestSDXLResolution
module: custom_nodes.ComfyMath | category: math/graphics
- required:
  - image: IMAGE
- outputs: width:INT, height:INT

## CM_NumberBinaryCondition
module: custom_nodes.ComfyMath | category: math/float
- required:
  - op: COMBO[Eq, Neq, Gt, Gte, Lt, Lte]
  - a: NUMBER default=0.0
  - b: NUMBER default=0.0
- outputs: BOOL:BOOL

## CM_NumberBinaryOperation
module: custom_nodes.ComfyMath | category: math/number
- required:
  - op: COMBO[Add, Sub, Mul, Div, Mod, Pow, FloorDiv, Max, Min, Log, ... +1]
  - a: NUMBER default=0.0
  - b: NUMBER default=0.0
- outputs: NUMBER:NUMBER

## CM_NumberToFloat
module: custom_nodes.ComfyMath | category: math/conversion
- required:
  - a: NUMBER default=0.0
- outputs: FLOAT:FLOAT

## CM_NumberToInt
module: custom_nodes.ComfyMath | category: math/conversion
- required:
  - a: NUMBER default=0.0
- outputs: INT:INT

## CM_NumberUnaryCondition
module: custom_nodes.ComfyMath | category: math/Number
- required:
  - op: COMBO[IsZero, IsPositive, IsNegative, IsNonZero, IsPositiveInfinity, IsNegativeInfinity, IsNaN, IsFinite, IsInfinite, IsEven, ... +1]
  - a: NUMBER default=0.0
- outputs: BOOL:BOOL

## CM_NumberUnaryOperation
module: custom_nodes.ComfyMath | category: math/number
- required:
  - op: COMBO[Neg, Inc, Dec, Abs, Sqr, Cube, Sqrt, Exp, Ln, Log10, ... +22]
  - a: NUMBER default=0.0
- outputs: NUMBER:NUMBER

## CM_SDXLExtendedResolution
module: custom_nodes.ComfyMath | category: math/graphics
- required:
  - resolution: COMBO[512x2048, 512x1984, 512x1920, 512x1856, 576x1792, 576x1728, 576x1664, 640x1600, 640x1536, 704x1472, ... +30]
- outputs: width:INT, height:INT

## CM_SDXLResolution
module: custom_nodes.ComfyMath | category: math/graphics
- required:
  - resolution: COMBO[1024x1024, 1152x896, 896x1152, 1216x832, 832x1216, 1344x768, 768x1344, 1536x640, 640x1536]
- outputs: width:INT, height:INT

## CM_Vec2BinaryCondition
module: custom_nodes.ComfyMath | category: math/vec2
- required:
  - op: COMBO[Eq, Neq]
  - a: VEC2 default=[0.0, 0.0]
  - b: VEC2 default=[0.0, 0.0]
- outputs: BOOL:BOOL

## CM_Vec2BinaryOperation
module: custom_nodes.ComfyMath | category: math/vec2
- required:
  - op: COMBO[Add, Sub, Cross]
  - a: VEC2 default=[0.0, 0.0]
  - b: VEC2 default=[0.0, 0.0]
- outputs: VEC2:VEC2

## CM_Vec2ScalarOperation
module: custom_nodes.ComfyMath | category: math/vec2
- required:
  - op: COMBO[Mul, Div]
  - a: VEC2 default=[0.0, 0.0]
  - b: FLOAT
- outputs: VEC2:VEC2

## CM_Vec2ToScalarBinaryOperation
module: custom_nodes.ComfyMath | category: math/vec2
- required:
  - op: COMBO[Dot, Distance]
  - a: VEC2 default=[0.0, 0.0]
  - b: VEC2 default=[0.0, 0.0]
- outputs: FLOAT:FLOAT

## CM_Vec2ToScalarUnaryOperation
module: custom_nodes.ComfyMath | category: math/vec2
- required:
  - op: COMBO[Norm]
  - a: VEC2 default=[0.0, 0.0]
- outputs: FLOAT:FLOAT

## CM_Vec2UnaryCondition
module: custom_nodes.ComfyMath | category: math/vec2
- required:
  - op: COMBO[IsZero, IsNotZero, IsNormalized, IsNotNormalized]
  - a: VEC2 default=[0.0, 0.0]
- outputs: BOOL:BOOL

## CM_Vec2UnaryOperation
module: custom_nodes.ComfyMath | category: math/vec2
- required:
  - op: COMBO[Neg, Normalize]
  - a: VEC2 default=[0.0, 0.0]
- outputs: VEC2:VEC2

## CM_Vec3BinaryCondition
module: custom_nodes.ComfyMath | category: math/vec3
- required:
  - op: COMBO[Eq, Neq]
  - a: VEC3 default=[0.0, 0.0, 0.0]
  - b: VEC3 default=[0.0, 0.0, 0.0]
- outputs: BOOL:BOOL

## CM_Vec3BinaryOperation
module: custom_nodes.ComfyMath | category: math/vec3
- required:
  - op: COMBO[Add, Sub, Cross]
  - a: VEC3 default=[0.0, 0.0, 0.0]
  - b: VEC3 default=[0.0, 0.0, 0.0]
- outputs: VEC3:VEC3

## CM_Vec3ScalarOperation
module: custom_nodes.ComfyMath | category: math/vec3
- required:
  - op: COMBO[Mul, Div]
  - a: VEC3 default=[0.0, 0.0, 0.0]
  - b: FLOAT
- outputs: VEC3:VEC3

## CM_Vec3ToScalarBinaryOperation
module: custom_nodes.ComfyMath | category: math/vec3
- required:
  - op: COMBO[Dot, Distance]
  - a: VEC3 default=[0.0, 0.0, 0.0]
  - b: VEC3 default=[0.0, 0.0, 0.0]
- outputs: FLOAT:FLOAT

## CM_Vec3ToScalarUnaryOperation
module: custom_nodes.ComfyMath | category: math/vec3
- required:
  - op: COMBO[Norm]
  - a: VEC3 default=[0.0, 0.0, 0.0]
- outputs: FLOAT:FLOAT

## CM_Vec3UnaryCondition
module: custom_nodes.ComfyMath | category: math/vec3
- required:
  - op: COMBO[IsZero, IsNotZero, IsNormalized, IsNotNormalized]
  - a: VEC3 default=[0.0, 0.0, 0.0]
- outputs: BOOL:BOOL

## CM_Vec3UnaryOperation
module: custom_nodes.ComfyMath | category: math/vec3
- required:
  - op: COMBO[Neg, Normalize]
  - a: VEC3 default=[0.0, 0.0, 0.0]
- outputs: VEC3:VEC3

## CM_Vec4BinaryCondition
module: custom_nodes.ComfyMath | category: math/vec4
- required:
  - op: COMBO[Eq, Neq]
  - a: VEC4 default=[0.0, 0.0, 0.0, 0.0]
  - b: VEC4 default=[0.0, 0.0, 0.0, 0.0]
- outputs: BOOL:BOOL

## CM_Vec4BinaryOperation
module: custom_nodes.ComfyMath | category: math/vec4
- required:
  - op: COMBO[Add, Sub, Cross]
  - a: VEC4 default=[0.0, 0.0, 0.0, 0.0]
  - b: VEC4 default=[0.0, 0.0, 0.0, 0.0]
- outputs: VEC4:VEC4

## CM_Vec4ScalarOperation
module: custom_nodes.ComfyMath | category: math/vec4
- required:
  - op: COMBO[Mul, Div]
  - a: VEC4 default=[0.0, 0.0, 0.0, 0.0]
  - b: FLOAT
- outputs: VEC4:VEC4

## CM_Vec4ToScalarBinaryOperation
module: custom_nodes.ComfyMath | category: math/vec4
- required:
  - op: COMBO[Dot, Distance]
  - a: VEC4 default=[0.0, 0.0, 0.0, 0.0]
  - b: VEC4 default=[0.0, 0.0, 0.0, 0.0]
- outputs: FLOAT:FLOAT

## CM_Vec4ToScalarUnaryOperation
module: custom_nodes.ComfyMath | category: math/vec4
- required:
  - op: COMBO[Norm]
  - a: VEC4 default=[0.0, 0.0, 0.0, 0.0]
- outputs: FLOAT:FLOAT

## CM_Vec4UnaryCondition
module: custom_nodes.ComfyMath | category: math/vec4
- required:
  - op: COMBO[IsZero, IsNotZero, IsNormalized, IsNotNormalized]
  - a: VEC4 default=[0.0, 0.0, 0.0, 0.0]
- outputs: BOOL:BOOL

## CM_Vec4UnaryOperation
module: custom_nodes.ComfyMath | category: math/vec4
- required:
  - op: COMBO[Neg, Normalize]
  - a: VEC4 default=[0.0, 0.0, 0.0, 0.0]
- outputs: VEC4:VEC4

## ColorMatch
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - image_ref: IMAGE
  - image_target: IMAGE
  - method: COMBO[mkl, hm, reinhard, mvgd, hm-mvgd-hm, hm-mkl-hm] default='mkl'
- optional:
  - strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - multithread: BOOLEAN default=True
- outputs: image:IMAGE

## ColorMatchV2
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - image_target: IMAGE
  - image_ref: IMAGE
  - method: COMBO[mkl, hm, reinhard, mvgd, hm-mvgd-hm, hm-mkl-hm, reinhard_lab_gpu] default='mkl'
  - strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - multithread: BOOLEAN default=True
- outputs: image:IMAGE

## ColorPreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/T2IAdapter-only
- required:
  - image: IMAGE
- optional:
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## ColorToMask
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking
- required:
  - images: IMAGE
  - invert: BOOLEAN default=False
  - red: INT default=0 min=0 max=255 step=1
  - green: INT default=0 min=0 max=255 step=1
  - blue: INT default=0 min=0 max=255 step=1
  - threshold: INT default=10 min=0 max=255 step=1
  - per_batch: INT default=16 min=1 max=4096 step=1
- outputs: MASK:MASK

## ColorToRGBInt
module: comfy_extras.nodes_color | category: utilities
- required:
  - color: COLOR default='#ffffff'
- outputs: rgb_int:INT, hex:COLOR, alpha:FLOAT

## ColorTransfer
module: comfy_extras.nodes_post_processing | category: image/filters
- required:
  - image_target: IMAGE
  - image_ref: IMAGE
  - method: COMBO[reinhard_lab, mkl_lab, histogram]
  - source_stats: COMFY_DYNAMICCOMBO_V3
  - strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
- outputs: image:IMAGE

## CombineHooks2
module: comfy_extras.nodes_hooks | category: advanced/hooks/combine
- optional:
  - hooks_A: HOOKS
  - hooks_B: HOOKS
- outputs: HOOKS:HOOKS

## CombineHooks4
module: comfy_extras.nodes_hooks | category: advanced/hooks/combine
- optional:
  - hooks_A: HOOKS
  - hooks_B: HOOKS
  - hooks_C: HOOKS
  - hooks_D: HOOKS
- outputs: HOOKS:HOOKS

## CombineHooks8
module: comfy_extras.nodes_hooks | category: advanced/hooks/combine
- optional:
  - hooks_A: HOOKS
  - hooks_B: HOOKS
  - hooks_C: HOOKS
  - hooks_D: HOOKS
  - hooks_E: HOOKS
  - hooks_F: HOOKS
  - hooks_G: HOOKS
  - hooks_H: HOOKS
- outputs: HOOKS:HOOKS

## Combo Clone
module: custom_nodes.cg-use-everywhere | category: everywhere
- required:
  - combo: COMBO[connect me to a combo widget]
- outputs: comboout:*

## ComfyAndNode
module: comfy_extras.nodes_logic | category: utilities/logic
- required:
  - values: COMFY_AUTOGROW_V3
- outputs: BOOLEAN:BOOLEAN

## ComfyCloudFlux2TextToImageNode
module: comfy_api_nodes.nodes_comfy_cloud | category: comfy cloud/image
- required:
  - prompt: STRING default=''
  - seed: INT default=42 min=0 max=18446744073709551615
  - aspect_ratio: COMBO[1:1, 3:4, 2:3, 3:2, 4:3, 16:9, 9:16, 21:9] default='1:1'
  - megapixels: FLOAT default=1.0 min=0.1 max=16.0 step=0.1
  - turbo: BOOLEAN default=True
- outputs: IMAGE:IMAGE

## ComfyCloudMageFlowTextToImageNode
module: comfy_api_nodes.nodes_comfy_cloud | category: comfy cloud/image
- required:
  - prompt: STRING default=''
  - negative_prompt: STRING default=''
  - seed: INT default=42 min=0 max=18446744073709551615
  - aspect_ratio: COMBO[1:1, 3:4, 2:3, 3:2, 4:3, 16:9, 9:16, 21:9] default='1:1'
  - megapixels: FLOAT default=1.0 min=0.1 max=16.0 step=0.1
- outputs: IMAGE:IMAGE

## ComfyCloudMageFlowTurboTextToImageNode
module: comfy_api_nodes.nodes_comfy_cloud | category: comfy cloud/image
- required:
  - prompt: STRING default=''
  - negative_prompt: STRING default=''
  - seed: INT default=42 min=0 max=18446744073709551615
  - aspect_ratio: COMBO[1:1, 3:4, 2:3, 3:2, 4:3, 16:9, 9:16, 21:9] default='1:1'
  - megapixels: FLOAT default=1.0 min=0.1 max=16.0 step=0.1
- outputs: IMAGE:IMAGE

## ComfyCloudMiniMaxH3FirstLastFrameToVideoNode
module: comfy_api_nodes.nodes_comfy_cloud | category: comfy cloud/video
- required:
  - first_frame: IMAGE
  - prompt: STRING default=''
  - seed: INT default=42 min=0 max=18446744073709551615
  - aspect_ratio: COMBO[1:1, 3:4, 2:3, 3:2, 4:3, 16:9, 9:16, 21:9] default='1:1'
  - resolution: COMBO[480p, 720p] default='480p'
  - duration_seconds: INT default=5 min=5 max=15
- optional:
  - last_frame: IMAGE
- outputs: VIDEO:VIDEO

## ComfyCloudMiniMaxH3ImageToVideoNode
module: comfy_api_nodes.nodes_comfy_cloud | category: comfy cloud/video
- required:
  - first_frame: IMAGE
  - prompt: STRING default=''
  - seed: INT default=42 min=0 max=18446744073709551615
  - aspect_ratio: COMBO[1:1, 3:4, 2:3, 3:2, 4:3, 16:9, 9:16, 21:9] default='1:1'
  - resolution: COMBO[480p, 720p] default='480p'
  - duration_seconds: INT default=5 min=5 max=15
- outputs: VIDEO:VIDEO

## ComfyCloudMiniMaxH3TextToVideoNode
module: comfy_api_nodes.nodes_comfy_cloud | category: comfy cloud/video
- required:
  - prompt: STRING default=''
  - seed: INT default=42 min=0 max=18446744073709551615
  - aspect_ratio: COMBO[1:1, 3:4, 2:3, 3:2, 4:3, 16:9, 9:16, 21:9] default='16:9'
  - resolution: COMBO[480p, 720p] default='480p'
  - duration_seconds: INT default=5 min=5 max=15
- outputs: VIDEO:VIDEO

## ComfyCloudMiniMaxMusic3TextToAudioNode
module: comfy_api_nodes.nodes_comfy_cloud | category: comfy cloud/audio
- required:
  - prompt: STRING default=''
  - lyrics: STRING default=''
  - seed: INT default=42 min=0 max=9223372036854775807
  - max_duration: FLOAT default=120.0 min=0.04 max=360.0 step=0.04
  - audio_quality: COMBO[V0, 128k, 320k] default='V0'
- outputs: AUDIO:AUDIO

## ComfyCloudZImageTurboNode
module: comfy_api_nodes.nodes_comfy_cloud | category: comfy cloud/image
- required:
  - prompt: STRING default=''
  - seed: INT default=42 min=0 max=18446744073709551615
  - aspect_ratio: COMBO[1:1, 3:4, 2:3, 3:2, 4:3, 16:9, 9:16, 21:9] default='1:1'
  - megapixels: FLOAT default=1.0 min=0.1 max=16.0 step=0.1
- outputs: IMAGE:IMAGE

## ComfyMathExpression
module: comfy_extras.nodes_math | category: utilities
- required:
  - expression: STRING default='a + b'
  - values: COMFY_AUTOGROW_V3
- outputs: FLOAT:FLOAT, INT:INT, BOOL:BOOLEAN

## ComfyNotNode
module: comfy_extras.nodes_logic | category: utilities/logic
- required:
  - value: *
- outputs: BOOLEAN:BOOLEAN

## ComfyNumberConvert
module: comfy_extras.nodes_number_convert | category: utilities
- required:
  - value: INT,FLOAT,STRING,BOOLEAN
- outputs: FLOAT:FLOAT, INT:INT

## ComfyOrNode
module: comfy_extras.nodes_logic | category: utilities/logic
- required:
  - values: COMFY_AUTOGROW_V3
- outputs: BOOLEAN:BOOLEAN

## ComfySwitchNode
module: comfy_extras.nodes_logic | category: utilities/logic
- required:
  - switch: BOOLEAN
- optional:
  - on_false: COMFY_MATCHTYPE_V3
  - on_true: COMFY_MATCHTYPE_V3
- outputs: output:COMFY_MATCHTYPE_V3

## ConcatenateVideo
module: comfy_extras.nodes_video | category: video
- required:
  - videos: COMFY_AUTOGROW_V3
  - codec: COMBO[auto, h264, av1] default='auto'
- optional:
  - complete_audio: AUDIO
- outputs: VIDEO:VIDEO

## ConditioningAverage
module: nodes | category: model/conditioning/transform
- required:
  - conditioning_to: CONDITIONING
  - conditioning_from: CONDITIONING
  - conditioning_to_strength: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: CONDITIONING:CONDITIONING

## ConditioningCombine
module: nodes | category: model/conditioning/transform
- required:
  - conditioning_1: CONDITIONING
  - conditioning_2: CONDITIONING
- outputs: CONDITIONING:CONDITIONING

## ConditioningCombineMultiple+
module: custom_nodes.ComfyUI_essentials | category: essentials/conditioning
- required:
  - conditioning_1: CONDITIONING
  - conditioning_2: CONDITIONING
- optional:
  - conditioning_3: CONDITIONING
  - conditioning_4: CONDITIONING
  - conditioning_5: CONDITIONING
- outputs: CONDITIONING:CONDITIONING

## ConditioningConcat
module: nodes | category: model/conditioning/transform
- required:
  - conditioning_to: CONDITIONING
  - conditioning_from: CONDITIONING
- outputs: CONDITIONING:CONDITIONING

## ConditioningLoader
module: comfy_extras.nodes_cond | category: model/loaders
- required:
  - conditioning_name: COMBO[]
- outputs: CONDITIONING:CONDITIONING

## ConditioningMultiCombine
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking/conditioning
- required:
  - inputcount: INT default=2 min=2 max=20 step=1
  - operation: COMBO[combine, concat] default='combine'
  - conditioning_1: CONDITIONING
  - conditioning_2: CONDITIONING
- outputs: combined:CONDITIONING, inputcount:INT

## ConditioningMultiply
module: nodes | category: model/conditioning/transform
- required:
  - conditioning: CONDITIONING
  - multiplier: FLOAT default=1.0 min=-100.0 max=100.0 step=0.01
- outputs: CONDITIONING:CONDITIONING

## ConditioningSetArea
module: nodes | category: model/conditioning/transform
- required:
  - conditioning: CONDITIONING
  - width: INT default=64 min=64 max=16384 step=8
  - height: INT default=64 min=64 max=16384 step=8
  - x: INT default=0 min=0 max=16384 step=8
  - y: INT default=0 min=0 max=16384 step=8
  - strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
- outputs: CONDITIONING:CONDITIONING

## ConditioningSetAreaPercentage
module: nodes | category: model/conditioning/transform
- required:
  - conditioning: CONDITIONING
  - width: FLOAT default=1.0 min=0 max=1.0 step=0.01
  - height: FLOAT default=1.0 min=0 max=1.0 step=0.01
  - x: FLOAT default=0 min=0 max=1.0 step=0.01
  - y: FLOAT default=0 min=0 max=1.0 step=0.01
  - strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
- outputs: CONDITIONING:CONDITIONING

## ConditioningSetAreaPercentageVideo
module: comfy_extras.nodes_video_model | category: model/conditioning/transform
- required:
  - conditioning: CONDITIONING
  - width: FLOAT default=1.0 min=0 max=1.0 step=0.01
  - height: FLOAT default=1.0 min=0 max=1.0 step=0.01
  - temporal: FLOAT default=1.0 min=0 max=1.0 step=0.01
  - x: FLOAT default=0 min=0 max=1.0 step=0.01
  - y: FLOAT default=0 min=0 max=1.0 step=0.01
  - z: FLOAT default=0 min=0 max=1.0 step=0.01
  - strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
- outputs: CONDITIONING:CONDITIONING

## ConditioningSetAreaStrength
module: nodes | category: model/conditioning/transform
- required:
  - conditioning: CONDITIONING
  - strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
- outputs: CONDITIONING:CONDITIONING

## ConditioningSetDefaultCombine
module: comfy_extras.nodes_hooks | category: advanced/hooks/cond single
- required:
  - cond: CONDITIONING
  - cond_DEFAULT: CONDITIONING
- optional:
  - hooks: HOOKS
- outputs: CONDITIONING:CONDITIONING

## ConditioningSetMask
module: nodes | category: model/conditioning/transform
- required:
  - conditioning: CONDITIONING
  - mask: MASK
  - strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - set_cond_area: COMBO[default, mask bounds]
- outputs: CONDITIONING:CONDITIONING

## ConditioningSetMaskAndCombine
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking/conditioning
- required:
  - positive_1: CONDITIONING
  - negative_1: CONDITIONING
  - positive_2: CONDITIONING
  - negative_2: CONDITIONING
  - mask_1: MASK
  - mask_2: MASK
  - mask_1_strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - mask_2_strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - set_cond_area: COMBO[default, mask bounds]
- outputs: combined_positive:CONDITIONING, combined_negative:CONDITIONING

## ConditioningSetMaskAndCombine3
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking/conditioning
- required:
  - positive_1: CONDITIONING
  - negative_1: CONDITIONING
  - positive_2: CONDITIONING
  - negative_2: CONDITIONING
  - positive_3: CONDITIONING
  - negative_3: CONDITIONING
  - mask_1: MASK
  - mask_2: MASK
  - mask_3: MASK
  - mask_1_strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - mask_2_strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - mask_3_strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - set_cond_area: COMBO[default, mask bounds]
- outputs: combined_positive:CONDITIONING, combined_negative:CONDITIONING

## ConditioningSetMaskAndCombine4
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking/conditioning
- required:
  - positive_1: CONDITIONING
  - negative_1: CONDITIONING
  - positive_2: CONDITIONING
  - negative_2: CONDITIONING
  - positive_3: CONDITIONING
  - negative_3: CONDITIONING
  - positive_4: CONDITIONING
  - negative_4: CONDITIONING
  - mask_1: MASK
  - mask_2: MASK
  - mask_3: MASK
  - mask_4: MASK
  - mask_1_strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - mask_2_strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - mask_3_strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - mask_4_strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - set_cond_area: COMBO[default, mask bounds]
- outputs: combined_positive:CONDITIONING, combined_negative:CONDITIONING

## ConditioningSetMaskAndCombine5
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking/conditioning
- required:
  - positive_1: CONDITIONING
  - negative_1: CONDITIONING
  - positive_2: CONDITIONING
  - negative_2: CONDITIONING
  - positive_3: CONDITIONING
  - negative_3: CONDITIONING
  - positive_4: CONDITIONING
  - negative_4: CONDITIONING
  - positive_5: CONDITIONING
  - negative_5: CONDITIONING
  - mask_1: MASK
  - mask_2: MASK
  - mask_3: MASK
  - mask_4: MASK
  - mask_5: MASK
  - mask_1_strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - mask_2_strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - mask_3_strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - mask_4_strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - mask_5_strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - set_cond_area: COMBO[default, mask bounds]
- outputs: combined_positive:CONDITIONING, combined_negative:CONDITIONING

## ConditioningSetProperties
module: comfy_extras.nodes_hooks | category: advanced/hooks/cond single
- required:
  - cond_NEW: CONDITIONING
  - strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - set_cond_area: COMBO[default, mask bounds]
- optional:
  - mask: MASK
  - hooks: HOOKS
  - timesteps: TIMESTEPS_RANGE
- outputs: CONDITIONING:CONDITIONING

## ConditioningSetPropertiesAndCombine
module: comfy_extras.nodes_hooks | category: advanced/hooks/cond single
- required:
  - cond: CONDITIONING
  - cond_NEW: CONDITIONING
  - strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - set_cond_area: COMBO[default, mask bounds]
- optional:
  - mask: MASK
  - hooks: HOOKS
  - timesteps: TIMESTEPS_RANGE
- outputs: CONDITIONING:CONDITIONING

## ConditioningSetTimestepRange
module: nodes | category: model/conditioning/transform
- required:
  - conditioning: CONDITIONING
  - start: FLOAT default=0.0 min=0.0 max=1.0 step=0.001
  - end: FLOAT default=1.0 min=0.0 max=1.0 step=0.001
- outputs: CONDITIONING:CONDITIONING

## ConditioningStableAudio
module: comfy_extras.nodes_audio | category: model/conditioning/stable audio
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - seconds_start: FLOAT default=0.0 min=0.0 max=1000.0 step=0.1
  - seconds_total: FLOAT default=47.0 min=0.0 max=1000.0 step=0.1
- outputs: positive:CONDITIONING, negative:CONDITIONING

## ConditioningTimestepsRange
module: comfy_extras.nodes_hooks | category: advanced/hooks
- required:
  - start_percent: FLOAT default=0.0 min=0.0 max=1.0 step=0.001
  - end_percent: FLOAT default=1.0 min=0.0 max=1.0 step=0.001
- outputs: TIMESTEPS_RANGE:TIMESTEPS_RANGE, BEFORE_RANGE:TIMESTEPS_RANGE, AFTER_RANGE:TIMESTEPS_RANGE

## ConditioningZeroOut
module: nodes | category: model/conditioning/transform
- required:
  - conditioning: CONDITIONING
- outputs: CONDITIONING:CONDITIONING

## CondPassThrough
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/misc
- optional:
  - positive: CONDITIONING
  - negative: CONDITIONING
- outputs: positive:CONDITIONING, negative:CONDITIONING

## ConsoleDebug+
module: custom_nodes.ComfyUI_essentials | category: essentials/utilities
- required:
  - value: *
- optional:
  - prefix: STRING default='Value:'
- outputs: 

## ConsolidateMasksKJ
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking
- required:
  - masks: MASK
  - width: INT default=512 min=0 max=4096 step=64
  - height: INT default=512 min=0 max=4096 step=64
  - padding: INT default=0 min=0 max=4096 step=1
- outputs: MASK:MASK

## ConstrainImageforVideo|pysssss
module: custom_nodes.ComfyUI-Custom-Scripts | category: image
- required:
  - images: IMAGE
  - max_width: INT default=1024 min=0
  - max_height: INT default=1024 min=0
  - min_width: INT default=0 min=0
  - min_height: INT default=0 min=0
  - crop_if_required: COMBO[yes, no] default='no'
- outputs: IMAGE:IMAGE

## ConstrainImage|pysssss
module: custom_nodes.ComfyUI-Custom-Scripts | category: image
- required:
  - images: IMAGE
  - max_width: INT default=1024 min=0
  - max_height: INT default=1024 min=0
  - min_width: INT default=0 min=0
  - min_height: INT default=0 min=0
  - crop_if_required: COMBO[yes, no] default='no'
- outputs: IMAGE:IMAGE

## Context (rgthree)
module: custom_nodes.rgthree-comfy | category: rgthree
- optional:
  - base_ctx: RGTHREE_CONTEXT
  - model: MODEL
  - clip: CLIP
  - vae: VAE
  - positive: CONDITIONING
  - negative: CONDITIONING
  - latent: LATENT
  - images: IMAGE
  - seed: INT
- outputs: CONTEXT:RGTHREE_CONTEXT, MODEL:MODEL, CLIP:CLIP, VAE:VAE, POSITIVE:CONDITIONING, NEGATIVE:CONDITIONING, LATENT:LATENT, IMAGE:IMAGE, SEED:INT

## Context Big (rgthree)
module: custom_nodes.rgthree-comfy | category: rgthree
- optional:
  - base_ctx: RGTHREE_CONTEXT
  - model: MODEL
  - clip: CLIP
  - vae: VAE
  - positive: CONDITIONING
  - negative: CONDITIONING
  - latent: LATENT
  - images: IMAGE
  - seed: INT
  - steps: INT
  - step_refiner: INT
  - cfg: FLOAT
  - ckpt_name: COMBO[]
  - sampler: COMBO[euler, euler_cfg_pp, euler_ancestral, euler_ancestral_cfg_pp, heun, heunpp2, exp_heun_2_x0, exp_heun_2_x0_sde, dpm_2, dpm_2_ancestral, ... +35]
  - scheduler: COMBO[simple, sgm_uniform, karras, exponential, ddim_uniform, beta, normal, linear_quadratic, kl_optimal]
  - clip_width: INT
  - clip_height: INT
  - text_pos_g: STRING
  - text_pos_l: STRING
  - text_neg_g: STRING
  - text_neg_l: STRING
  - mask: MASK
  - control_net: CONTROL_NET
- outputs: CONTEXT:RGTHREE_CONTEXT, MODEL:MODEL, CLIP:CLIP, VAE:VAE, POSITIVE:CONDITIONING, NEGATIVE:CONDITIONING, LATENT:LATENT, IMAGE:IMAGE, SEED:INT, STEPS:INT, STEP_REFINER:INT, CFG:FLOAT, CKPT_NAME:[], SAMPLER:['euler', 'euler_cfg_pp', 'euler_ancestral', 'euler_ancestral_cfg_pp', 'heun', 'heunpp2', 'exp_heun_2_x0', 'exp_heun_2_x0_sde', 'dpm_2', 'dpm_2_ancestral', 'lms', 'dpm_fast', 'dpm_adaptive', 'dpmpp_2s_ancestral', 'dpmpp_2s_ancestral_cfg_pp', 'dpmpp_sde', 'dpmpp_sde_gpu', 'dpmpp_2m', 'dpmpp_2m_cfg_pp', 'dpmpp_2m_sde', 'dpmpp_2m_sde_gpu', 'dpmpp_2m_sde_heun', 'dpmpp_2m_sde_heun_gpu', 'dpmpp_3m_sde', 'dpmpp_3m_sde_gpu', 'ddpm', 'lcm', 'ipndm', 'ipndm_v', 'deis', 'cfgpp_ud10_ab', 'res_multistep', 'res_multistep_cfg_pp', 'res_multistep_ancestral', 'res_multistep_ancestral_cfg_pp', 'gradient_estimation', 'gradient_estimation_cfg_pp', 'er_sde', 'seeds_2', 'seeds_3', 'sa_solver', 'sa_solver_pece', 'ddim', 'uni_pc', 'uni_pc_bh2'], SCHEDULER:['simple', 'sgm_uniform', 'karras', 'exponential', 'ddim_uniform', 'beta', 'normal', 'linear_quadratic', 'kl_optimal'], CLIP_WIDTH:INT, CLIP_HEIGHT:INT, TEXT_POS_G:STRING, TEXT_POS_L:STRING, TEXT_NEG_G:STRING, TEXT_NEG_L:STRING, MASK:MASK, CONTROL_NET:CONTROL_NET

## Context Merge (rgthree)
module: custom_nodes.rgthree-comfy | category: rgthree
- outputs: CONTEXT:RGTHREE_CONTEXT, MODEL:MODEL, CLIP:CLIP, VAE:VAE, POSITIVE:CONDITIONING, NEGATIVE:CONDITIONING, LATENT:LATENT, IMAGE:IMAGE, SEED:INT

## Context Merge Big (rgthree)
module: custom_nodes.rgthree-comfy | category: rgthree
- outputs: CONTEXT:RGTHREE_CONTEXT, MODEL:MODEL, CLIP:CLIP, VAE:VAE, POSITIVE:CONDITIONING, NEGATIVE:CONDITIONING, LATENT:LATENT, IMAGE:IMAGE, SEED:INT, STEPS:INT, STEP_REFINER:INT, CFG:FLOAT, CKPT_NAME:[], SAMPLER:['euler', 'euler_cfg_pp', 'euler_ancestral', 'euler_ancestral_cfg_pp', 'heun', 'heunpp2', 'exp_heun_2_x0', 'exp_heun_2_x0_sde', 'dpm_2', 'dpm_2_ancestral', 'lms', 'dpm_fast', 'dpm_adaptive', 'dpmpp_2s_ancestral', 'dpmpp_2s_ancestral_cfg_pp', 'dpmpp_sde', 'dpmpp_sde_gpu', 'dpmpp_2m', 'dpmpp_2m_cfg_pp', 'dpmpp_2m_sde', 'dpmpp_2m_sde_gpu', 'dpmpp_2m_sde_heun', 'dpmpp_2m_sde_heun_gpu', 'dpmpp_3m_sde', 'dpmpp_3m_sde_gpu', 'ddpm', 'lcm', 'ipndm', 'ipndm_v', 'deis', 'cfgpp_ud10_ab', 'res_multistep', 'res_multistep_cfg_pp', 'res_multistep_ancestral', 'res_multistep_ancestral_cfg_pp', 'gradient_estimation', 'gradient_estimation_cfg_pp', 'er_sde', 'seeds_2', 'seeds_3', 'sa_solver', 'sa_solver_pece', 'ddim', 'uni_pc', 'uni_pc_bh2'], SCHEDULER:['simple', 'sgm_uniform', 'karras', 'exponential', 'ddim_uniform', 'beta', 'normal', 'linear_quadratic', 'kl_optimal'], CLIP_WIDTH:INT, CLIP_HEIGHT:INT, TEXT_POS_G:STRING, TEXT_POS_L:STRING, TEXT_NEG_G:STRING, TEXT_NEG_L:STRING, MASK:MASK, CONTROL_NET:CONTROL_NET

## Context Switch (rgthree)
module: custom_nodes.rgthree-comfy | category: rgthree
- outputs: CONTEXT:RGTHREE_CONTEXT, MODEL:MODEL, CLIP:CLIP, VAE:VAE, POSITIVE:CONDITIONING, NEGATIVE:CONDITIONING, LATENT:LATENT, IMAGE:IMAGE, SEED:INT

## Context Switch Big (rgthree)
module: custom_nodes.rgthree-comfy | category: rgthree
- outputs: CONTEXT:RGTHREE_CONTEXT, MODEL:MODEL, CLIP:CLIP, VAE:VAE, POSITIVE:CONDITIONING, NEGATIVE:CONDITIONING, LATENT:LATENT, IMAGE:IMAGE, SEED:INT, STEPS:INT, STEP_REFINER:INT, CFG:FLOAT, CKPT_NAME:[], SAMPLER:['euler', 'euler_cfg_pp', 'euler_ancestral', 'euler_ancestral_cfg_pp', 'heun', 'heunpp2', 'exp_heun_2_x0', 'exp_heun_2_x0_sde', 'dpm_2', 'dpm_2_ancestral', 'lms', 'dpm_fast', 'dpm_adaptive', 'dpmpp_2s_ancestral', 'dpmpp_2s_ancestral_cfg_pp', 'dpmpp_sde', 'dpmpp_sde_gpu', 'dpmpp_2m', 'dpmpp_2m_cfg_pp', 'dpmpp_2m_sde', 'dpmpp_2m_sde_gpu', 'dpmpp_2m_sde_heun', 'dpmpp_2m_sde_heun_gpu', 'dpmpp_3m_sde', 'dpmpp_3m_sde_gpu', 'ddpm', 'lcm', 'ipndm', 'ipndm_v', 'deis', 'cfgpp_ud10_ab', 'res_multistep', 'res_multistep_cfg_pp', 'res_multistep_ancestral', 'res_multistep_ancestral_cfg_pp', 'gradient_estimation', 'gradient_estimation_cfg_pp', 'er_sde', 'seeds_2', 'seeds_3', 'sa_solver', 'sa_solver_pece', 'ddim', 'uni_pc', 'uni_pc_bh2'], SCHEDULER:['simple', 'sgm_uniform', 'karras', 'exponential', 'ddim_uniform', 'beta', 'normal', 'linear_quadratic', 'kl_optimal'], CLIP_WIDTH:INT, CLIP_HEIGHT:INT, TEXT_POS_G:STRING, TEXT_POS_L:STRING, TEXT_NEG_G:STRING, TEXT_NEG_L:STRING, MASK:MASK, CONTROL_NET:CONTROL_NET

## ContextWindowsManual
module: comfy_extras.nodes_context_windows | category: model/patch
- required:
  - model: MODEL
  - context_length: INT default=16 min=1
  - context_overlap: INT default=4 min=0
  - context_schedule: COMBO[standard_static, standard_uniform, looped_uniform, batched] default='standard_static'
  - context_stride: INT default=1 min=1
  - closed_loop: BOOLEAN default=False
  - fuse_method: COMBO[pyramid, relative, flat, overlap-linear] default='pyramid'
  - dim: INT default=0 min=0 max=5
  - freenoise: BOOLEAN default=False
  - cond_retain_index_list: STRING default=''
  - split_conds_to_windows: BOOLEAN default=False
  - latent_retain_index_list: STRING default=''
  - causal_window_fix: BOOLEAN default=True
- outputs: MODEL:MODEL

## ContextWindowsVisualizerKJ
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/misc
- required:
  - frame_units: COMBO[pixel, latent] default='pixel'
  - dim: INT default=2 min=0 max=5
  - temporal_downscale: INT default=4 min=1 max=16
  - num_frames: INT default=161 min=1 max=100000
  - context_length: INT default=81 min=1 max=100000
  - context_overlap: INT default=30 min=0 max=100000
  - context_schedule: COMBO[standard_static, standard_static_balanced, standard_uniform, looped_uniform, batched, batched_shifted]
  - context_stride: INT default=1 min=1 max=32
  - closed_loop: BOOLEAN default=False
  - fuse_method: COMBO[pyramid, relative, flat, overlap-linear, hann, gaussian] default='pyramid'
  - causal_window_fix: BOOLEAN default=False
  - freenoise: BOOLEAN default=True
  - cond_retain_index_list: STRING default=''
- optional:
  - model: MODEL
- outputs: model:MODEL

## ControlNetApply
module: nodes | category: model/conditioning/controlnet
- required:
  - conditioning: CONDITIONING
  - control_net: CONTROL_NET
  - image: IMAGE
  - strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
- outputs: CONDITIONING:CONDITIONING

## ControlNetApplyAdvanced
module: nodes | category: model/conditioning/controlnet
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - control_net: CONTROL_NET
  - image: IMAGE
  - strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - start_percent: FLOAT default=0.0 min=0.0 max=1.0 step=0.001
  - end_percent: FLOAT default=1.0 min=0.0 max=1.0 step=0.001
- optional:
  - vae: VAE
- outputs: positive:CONDITIONING, negative:CONDITIONING

## ControlNetApplySD3
module: comfy_extras.nodes_sd3 | category: model/conditioning/controlnet
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - control_net: CONTROL_NET
  - vae: VAE
  - image: IMAGE
  - strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - start_percent: FLOAT default=0.0 min=0.0 max=1.0 step=0.001
  - end_percent: FLOAT default=1.0 min=0.0 max=1.0 step=0.001
- outputs: positive:CONDITIONING, negative:CONDITIONING

## ControlNetAuxSimpleAddText
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors
- required:
  - image: IMAGE
  - text: STRING default=''
- outputs: IMAGE:IMAGE

## ControlNetInpaintingAliMamaApply
module: comfy_extras.nodes_controlnet | category: model/conditioning/controlnet
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - control_net: CONTROL_NET
  - vae: VAE
  - image: IMAGE
  - mask: MASK
  - strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - start_percent: FLOAT default=0.0 min=0.0 max=1.0 step=0.001
  - end_percent: FLOAT default=1.0 min=0.0 max=1.0 step=0.001
- outputs: positive:CONDITIONING, negative:CONDITIONING

## ControlNetLoader
module: nodes | category: model/loaders
- required:
  - control_net_name: COMBO[]
- outputs: CONTROL_NET:CONTROL_NET

## ControlNetPreprocessorSelector
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors
- required:
  - preprocessor: COMBO[none, AnimeFace_SemSegPreprocessor, AnyLineArtPreprocessor_aux, BinaryPreprocessor, CannyEdgePreprocessor, ColorPreprocessor, DensePosePreprocessor, DepthAnythingPreprocessor, Zoe_DepthAnythingPreprocessor, DepthAnythingV2Preprocessor, ... +37]
- outputs: preprocessor:['none', 'AnimeFace_SemSegPreprocessor', 'AnyLineArtPreprocessor_aux', 'BinaryPreprocessor', 'CannyEdgePreprocessor', 'ColorPreprocessor', 'DensePosePreprocessor', 'DepthAnythingPreprocessor', 'Zoe_DepthAnythingPreprocessor', 'DepthAnythingV2Preprocessor', 'DSINE-NormalMapPreprocessor', 'DWPreprocessor', 'AnimalPosePreprocessor', 'HEDPreprocessor', 'FakeScribblePreprocessor', 'LeReS-DepthMapPreprocessor', 'LineArtPreprocessor', 'AnimeLineArtPreprocessor', 'LineartStandardPreprocessor', 'Manga2Anime_LineArt_Preprocessor', 'MediaPipe-FaceMeshPreprocessor', 'MeshGraphormer-DepthMapPreprocessor', 'Metric3D-DepthMapPreprocessor', 'Metric3D-NormalMapPreprocessor', 'MiDaS-NormalMapPreprocessor', 'MiDaS-DepthMapPreprocessor', 'M-LSDPreprocessor', 'BAE-NormalMapPreprocessor', 'OneFormer-COCO-SemSegPreprocessor', 'OneFormer-ADE20K-SemSegPreprocessor', 'OpenposePreprocessor', 'PiDiNetPreprocessor', 'PyraCannyPreprocessor', 'ImageLuminanceDetector', 'ImageIntensityDetector', 'ScribblePreprocessor', 'Scribble_XDoG_Preprocessor', 'Scribble_PiDiNet_Preprocessor', 'SAMPreprocessor', 'ShufflePreprocessor', 'TEEDPreprocessor', 'TilePreprocessor', 'TTPlanet_TileGF_Preprocessor', 'TTPlanet_TileSimple_Preprocessor', 'UniFormer-SemSegPreprocessor', 'SemSegPreprocessor', 'Zoe-DepthMapPreprocessor']

## ConvertArrayToString
module: comfy_extras.nodes_string | category: text
- required:
  - array: ARRAY
  - indent: INT default=2 min=0 max=8
- outputs: STRING:STRING

## ConvertDictionaryToString
module: comfy_extras.nodes_string | category: text
- required:
  - dictionary: DICT
  - indent: INT default=2 min=0 max=8
- outputs: STRING:STRING

## CosmosImageToVideoLatent
module: comfy_extras.nodes_cosmos | category: model/conditioning/cosmos
- required:
  - vae: VAE
  - width: INT default=1280 min=16 max=16384 step=16
  - height: INT default=704 min=16 max=16384 step=16
  - length: INT default=121 min=1 max=16384 step=8
  - batch_size: INT default=1 min=1 max=4096
- optional:
  - start_image: IMAGE
  - end_image: IMAGE
- outputs: LATENT:LATENT

## CosmosPredict2ImageToVideoLatent
module: comfy_extras.nodes_cosmos | category: model/conditioning/cosmos
- required:
  - vae: VAE
  - width: INT default=848 min=16 max=16384 step=16
  - height: INT default=480 min=16 max=16384 step=16
  - length: INT default=93 min=1 max=16384 step=4
  - batch_size: INT default=1 min=1 max=4096
- optional:
  - start_image: IMAGE
  - end_image: IMAGE
- outputs: LATENT:LATENT

## CreateAudioMask
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/deprecated
- required:
  - invert: BOOLEAN default=False
  - frames: INT default=16 min=1 max=255 step=1
  - scale: FLOAT default=0.5 min=0.0 max=2.0 step=0.01
  - audio_path: STRING default='audio.wav'
  - width: INT default=256 min=16 max=4096 step=1
  - height: INT default=256 min=16 max=4096 step=1
- outputs: IMAGE:IMAGE

## CreateBoundingBoxes
module: comfy_extras.nodes_bounding_boxes | category: utilities
- required:
  - width: INT default=1024 min=64 max=16384 step=16
  - height: INT default=1024 min=64 max=16384 step=16
  - editor_state: BOUNDING_BOXES default=[]
- optional:
  - background: IMAGE
  - bboxes: BOUNDING_BOX,ARRAY,STRING
  - last_incoming: BOUNDING_BOXES default=[]
- outputs: preview:IMAGE, bboxes:BOUNDING_BOX, elements:ARRAY

## CreateCameraInfo
module: comfy_extras.nodes_gaussian_splat | category: 3d
- required:
  - mode: COMFY_DYNAMICCOMBO_V3
  - target_x: FLOAT default=0.0 min=-1000.0 max=1000.0 step=0.01
  - target_y: FLOAT default=0.0 min=-1000.0 max=1000.0 step=0.01
  - target_z: FLOAT default=0.0 min=-1000.0 max=1000.0 step=0.01
  - roll: FLOAT default=0.0 min=-180.0 max=180.0 step=1.0
  - fov: FLOAT default=35.0 min=1.0 max=120.0 step=1.0
  - zoom: FLOAT default=1.0 min=0.01 max=100.0 step=0.01
  - camera_type: COMBO[perspective, orthographic]
- outputs: camera_info:LOAD3D_CAMERA

## CreateFadeMask
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/deprecated
- required:
  - invert: BOOLEAN default=False
  - frames: INT default=2 min=2 max=10000 step=1
  - width: INT default=256 min=16 max=4096 step=1
  - height: INT default=256 min=16 max=4096 step=1
  - interpolation: COMBO[linear, ease_in, ease_out, ease_in_out]
  - start_level: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - midpoint_level: FLOAT default=0.5 min=0.0 max=1.0 step=0.01
  - end_level: FLOAT default=0.0 min=0.0 max=1.0 step=0.01
  - midpoint_frame: INT default=0 min=0 max=4096 step=1
- outputs: MASK:MASK

## CreateFadeMaskAdvanced
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking/generate
- required:
  - points_string: STRING default='0:(0.0),\n7:(1.0),\n15:(0.0)\n'
  - invert: BOOLEAN default=False
  - frames: INT default=16 min=2 max=10000 step=1
  - width: INT default=512 min=1 max=4096 step=1
  - height: INT default=512 min=1 max=4096 step=1
  - interpolation: COMBO[linear, ease_in, ease_out, ease_in_out, none, default_to_black]
- outputs: MASK:MASK

## CreateFluidMask
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking/generate
- required:
  - invert: BOOLEAN default=False
  - frames: INT default=1 min=1 max=4096 step=1
  - width: INT default=256 min=16 max=4096 step=1
  - height: INT default=256 min=16 max=4096 step=1
  - inflow_count: INT default=3 min=0 max=255 step=1
  - inflow_velocity: INT default=1 min=0 max=255 step=1
  - inflow_radius: INT default=8 min=0 max=255 step=1
  - inflow_padding: INT default=50 min=0 max=255 step=1
  - inflow_duration: INT default=60 min=0 max=255 step=1
- outputs: IMAGE:IMAGE, MASK:MASK

## CreateGradientFromCoords
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - coordinates: STRING
  - frame_width: INT default=512 min=16 max=4096 step=1
  - frame_height: INT default=512 min=16 max=4096 step=1
  - start_color: STRING default='white'
  - end_color: STRING default='black'
  - multiplier: FLOAT default=1.0 min=0.01 max=100.0 step=0.01
- outputs: image:IMAGE

## CreateGradientMask
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking/generate
- required:
  - invert: BOOLEAN default=False
  - frames: INT default=0 min=0 max=255 step=1
  - width: INT default=256 min=16 max=4096 step=1
  - height: INT default=256 min=16 max=4096 step=1
- outputs: MASK:MASK

## CreateHookKeyframe
module: comfy_extras.nodes_hooks | category: advanced/hooks/scheduling
- required:
  - strength_mult: FLOAT default=1.0 min=-20.0 max=20.0 step=0.01
  - start_percent: FLOAT default=0.0 min=0.0 max=1.0 step=0.001
- optional:
  - prev_hook_kf: HOOK_KEYFRAMES
- outputs: HOOK_KF:HOOK_KEYFRAMES

## CreateHookKeyframesFromFloats
module: comfy_extras.nodes_hooks | category: advanced/hooks/scheduling
- required:
  - floats_strength: FLOATS default=-1 min=-1 step=0.001
  - start_percent: FLOAT default=0.0 min=0.0 max=1.0 step=0.001
  - end_percent: FLOAT default=1.0 min=0.0 max=1.0 step=0.001
  - print_keyframes: BOOLEAN default=False
- optional:
  - prev_hook_kf: HOOK_KEYFRAMES
- outputs: HOOK_KF:HOOK_KEYFRAMES

## CreateHookKeyframesInterpolated
module: comfy_extras.nodes_hooks | category: advanced/hooks/scheduling
- required:
  - strength_start: FLOAT default=1.0 min=0.0 max=10.0 step=0.001
  - strength_end: FLOAT default=1.0 min=0.0 max=10.0 step=0.001
  - interpolation: COMBO[linear, ease_in, ease_out, ease_in_out]
  - start_percent: FLOAT default=0.0 min=0.0 max=1.0 step=0.001
  - end_percent: FLOAT default=1.0 min=0.0 max=1.0 step=0.001
  - keyframes_count: INT default=5 min=2 max=100 step=1
  - print_keyframes: BOOLEAN default=False
- optional:
  - prev_hook_kf: HOOK_KEYFRAMES
- outputs: HOOK_KF:HOOK_KEYFRAMES

## CreateHookLora
module: comfy_extras.nodes_hooks | category: advanced/hooks/create
- required:
  - lora_name: COMBO[FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, FC_KIERNAN_h3_face_v1.safetensors, ... +48]
  - strength_model: FLOAT default=1.0 min=-20.0 max=20.0 step=0.01
  - strength_clip: FLOAT default=1.0 min=-20.0 max=20.0 step=0.01
- optional:
  - prev_hooks: HOOKS
- outputs: HOOKS:HOOKS

## CreateHookLoraModelOnly
module: comfy_extras.nodes_hooks | category: advanced/hooks/create
- required:
  - lora_name: COMBO[FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, FC_KIERNAN_h3_face_v1.safetensors, ... +48]
  - strength_model: FLOAT default=1.0 min=-20.0 max=20.0 step=0.01
- optional:
  - prev_hooks: HOOKS
- outputs: HOOKS:HOOKS

## CreateHookModelAsLora
module: comfy_extras.nodes_hooks | category: advanced/hooks/create
- required:
  - ckpt_name: COMBO[]
  - strength_model: FLOAT default=1.0 min=-20.0 max=20.0 step=0.01
  - strength_clip: FLOAT default=1.0 min=-20.0 max=20.0 step=0.01
- optional:
  - prev_hooks: HOOKS
- outputs: HOOKS:HOOKS

## CreateHookModelAsLoraModelOnly
module: comfy_extras.nodes_hooks | category: advanced/hooks/create
- required:
  - ckpt_name: COMBO[]
  - strength_model: FLOAT default=1.0 min=-20.0 max=20.0 step=0.01
- optional:
  - prev_hooks: HOOKS
- outputs: HOOKS:HOOKS

## CreateInstanceDiffusionTracking
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/InstanceDiffusion
- required:
  - coordinates: STRING
  - width: INT default=512 min=16 max=4096 step=1
  - height: INT default=512 min=16 max=4096 step=1
  - bbox_width: INT default=512 min=16 max=4096 step=1
  - bbox_height: INT default=512 min=16 max=4096 step=1
  - class_name: STRING default='class_name'
  - class_id: INT default=0 min=0 max=255 step=1
  - prompt: STRING default='prompt'
- optional:
  - size_multiplier: FLOAT default=[1.0]
  - fit_in_frame: BOOLEAN default=True
- outputs: tracking:TRACKING, prompt:STRING, width:INT, height:INT, bbox_width:INT, bbox_height:INT

## CreateList
module: comfy_extras.nodes_toolkit | category: utilities
- required:
  - inputs: COMFY_AUTOGROW_V3
- outputs: list:*

## CreateMagicMask
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking/generate
- required:
  - frames: INT default=16 min=2 max=4096 step=1
  - depth: INT default=12 min=1 max=500 step=1
  - distortion: FLOAT default=1.5 min=0.0 max=100.0 step=0.01
  - seed: INT default=123 min=0 max=99999999 step=1
  - transitions: INT default=1 min=1 max=20 step=1
  - frame_width: INT default=512 min=16 max=4096 step=1
  - frame_height: INT default=512 min=16 max=4096 step=1
- outputs: mask:MASK, mask_inverted:MASK

## CreateShapeImageOnPath
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - shape: COMBO[circle, square, triangle] default='circle'
  - coordinates: STRING
  - frame_width: INT default=512 min=16 max=4096 step=1
  - frame_height: INT default=512 min=16 max=4096 step=1
  - shape_width: INT default=128 min=2 max=4096 step=1
  - shape_height: INT default=128 min=2 max=4096 step=1
  - shape_color: STRING default='white'
  - bg_color: STRING default='black'
  - blur_radius: FLOAT default=0.0 min=0.0 max=100 step=0.1
  - intensity: FLOAT default=1.0 min=0.01 max=100.0 step=0.01
- optional:
  - size_multiplier: FLOAT default=[1.0]
  - trailing: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - border_width: INT default=0 min=0 max=100 step=1
  - border_color: STRING default='black'
- outputs: image:IMAGE, mask:MASK

## CreateShapeMask
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking/generate
- required:
  - shape: COMBO[circle, square, triangle] default='circle'
  - frames: INT default=1 min=1 max=4096 step=1
  - location_x: INT default=256 min=0 max=4096 step=1
  - location_y: INT default=256 min=0 max=4096 step=1
  - grow: INT default=0 min=-512 max=512 step=1
  - frame_width: INT default=512 min=16 max=4096 step=1
  - frame_height: INT default=512 min=16 max=4096 step=1
  - shape_width: INT default=128 min=8 max=4096 step=1
  - shape_height: INT default=128 min=8 max=4096 step=1
- outputs: mask:MASK, mask_inverted:MASK

## CreateShapeMaskOnPath
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking/generate
- required:
  - shape: COMBO[circle, square, triangle] default='circle'
  - coordinates: STRING
  - frame_width: INT default=512 min=16 max=4096 step=1
  - frame_height: INT default=512 min=16 max=4096 step=1
  - shape_width: INT default=128 min=8 max=4096 step=1
  - shape_height: INT default=128 min=8 max=4096 step=1
- optional:
  - size_multiplier: FLOAT default=[1.0]
- outputs: mask:MASK, mask_inverted:MASK

## CreateTextMask
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/text
- required:
  - invert: BOOLEAN default=False
  - frames: INT default=1 min=1 max=4096 step=1
  - text_x: INT default=0 min=0 max=4096 step=1
  - text_y: INT default=0 min=0 max=4096 step=1
  - font_size: INT default=32 min=8 max=4096 step=1
  - font_color: STRING default='white'
  - text: STRING default='HELLO!'
  - font: COMBO[FreeMono.ttf, FreeMonoBoldOblique.otf, TTNorms-Black.otf]
  - width: INT default=512 min=16 max=4096 step=1
  - height: INT default=512 min=16 max=4096 step=1
  - start_rotation: INT default=0 min=0 max=359 step=1
  - end_rotation: INT default=0 min=-359 max=359 step=1
- outputs: IMAGE:IMAGE, MASK:MASK

## CreateTextOnPath
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking/generate
- required:
  - coordinates: STRING
  - text: STRING default='text'
  - frame_width: INT default=512 min=16 max=4096 step=1
  - frame_height: INT default=512 min=16 max=4096 step=1
  - font: COMBO[FreeMono.ttf, FreeMonoBoldOblique.otf, TTNorms-Black.otf]
  - font_size: INT default=42
  - alignment: COMBO[left, center, right] default='center'
  - text_color: STRING default='white'
- optional:
  - size_multiplier: FLOAT default=[1.0]
- outputs: image:IMAGE, mask:MASK, mask_inverted:MASK

## CreateVideo
module: comfy_extras.nodes_video | category: video
- required:
  - images: IMAGE
  - fps: FLOAT default=30.0 min=1.0 max=120.0 step=1.0
- optional:
  - audio: AUDIO
  - bit_depth: COMBO[auto, 8, 10] default='auto'
  - color_space: COMBO[sRGB, HDR, HDR PQ] default='sRGB'
  - codec: COMBO[none, auto, h264, av1] default='none'
- outputs: VIDEO:VIDEO

## CreateVoronoiMask
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking/generate
- required:
  - frames: INT default=16 min=2 max=4096 step=1
  - num_points: INT default=15 min=1 max=4096 step=1
  - line_width: INT default=4 min=1 max=4096 step=1
  - speed: FLOAT default=0.5 min=0.0 max=1.0 step=0.01
  - frame_width: INT default=512 min=16 max=4096 step=1
  - frame_height: INT default=512 min=16 max=4096 step=1
- outputs: mask:MASK, mask_inverted:MASK

## CropByBBoxes
module: comfy_extras.nodes_sdpose | category: image/transform
- required:
  - image: IMAGE
  - bboxes: BOUNDING_BOX default={'x': 0, 'y': 0, 'width': 512, 'height': 512}
  - output_width: INT default=512 min=64 max=4096 step=8
  - output_height: INT default=512 min=64 max=4096 step=8
  - padding: INT default=0 min=0 max=1024 step=1
  - keep_aspect: COMBO[stretch, pad] default='stretch'
- outputs: IMAGE:IMAGE

## CropMask
module: comfy_extras.nodes_mask | category: image/mask
- required:
  - mask: MASK
  - x: INT default=0 min=0 max=16384 step=1
  - y: INT default=0 min=0 max=16384 step=1
  - width: INT default=512 min=1 max=16384 step=1
  - height: INT default=512 min=1 max=16384 step=1
- outputs: MASK:MASK

## CrossFadeImages
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - images_1: IMAGE
  - images_2: IMAGE
  - interpolation: COMBO[linear, ease_in, ease_out, ease_in_out, bounce, elastic, glitchy, exponential_ease_out]
  - transition_start_index: INT default=1 min=-4096 max=4096 step=1
  - transitioning_frames: INT default=1 min=0 max=4096 step=1
  - start_level: FLOAT default=0.0 min=0.0 max=1.0 step=0.01
  - end_level: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: IMAGE:IMAGE

## CrossFadeImagesMulti
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - inputcount: INT default=2 min=2 max=1000 step=1
  - image_1: IMAGE
  - interpolation: COMBO[linear, ease_in, ease_out, ease_in_out, bounce, elastic, glitchy, exponential_ease_out]
  - transitioning_frames: INT default=1 min=0 max=4096 step=1
- optional:
  - image_2: IMAGE
- outputs: IMAGE:IMAGE

## CurveEditor
module: comfy_extras.nodes_curve | category: utilities
- required:
  - curve: CURVE default={'points': [[0.0, 0.0], [1.0, 1.0]], 'interpolation': 'monotone_cubic'}
- optional:
  - histogram: HISTOGRAM
- outputs: curve:CURVE

## CustomCombo
module: comfy_extras.nodes_logic | category: utilities
- required:
  - choice: COMBO[]
- outputs: STRING:STRING, INDEX:INT

## CustomControlNetWeightsFluxFromList
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/controlnet
- required:
  - list_of_floats: FLOAT
- optional:
  - uncond_multiplier: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - cn_extras: CN_WEIGHTS_EXTRAS
  - autosize: ACNAUTOSIZE
- outputs: CN_WEIGHTS:CONTROL_NET_WEIGHTS, TK_SHORTCUT:TIMESTEP_KEYFRAME

## CustomSigmas
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/noise
- required:
  - sigmas_string: STRING default='14.615, 6.475, 3.861, 2.697, 1.886, 1.396, 0.963, 0.652, 0.3...'
  - interpolate_to_steps: INT default=10 min=0 max=255 step=1
- outputs: SIGMAS:SIGMAS

## CutAndDragOnPath
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - image: IMAGE
  - coordinates: STRING
  - mask: MASK
  - frame_width: INT default=512 min=16 max=4096 step=1
  - frame_height: INT default=512 min=16 max=4096 step=1
  - inpaint: BOOLEAN default=True
- optional:
  - bg_image: IMAGE
- outputs: image:IMAGE, mask:MASK

## Cycle
module: custom_nodes.ControlFlowUtils | category: 🐺 VykosX-ControlFlowUtils
- required:
  - start: INT default=0
  - step: INT default=1
  - end: INT default=10
- optional:
  - manual_reset: BOOLEAN
  - auto_reset: BOOLEAN default=True
- outputs: CYCLE:CYCLE, RESET?:BOOLEAN

## CycleContinue
module: custom_nodes.ControlFlowUtils | category: 🐺 VykosX-ControlFlowUtils
- required:
  - CYCLE: CYCLE
  - data: *
- optional:
  - index_override: INT
  - aux: *
  - aux2: *
  - aux3: *
  - aux4: *
  - aux5: *
- outputs: index:INT, data:*, aux:*, aux2:*, aux3:*, aux4:*, aux5:*

## CycleEnd
module: custom_nodes.ControlFlowUtils | category: 🐺 VykosX-ControlFlowUtils
- required:
  - CYCLE: CYCLE
  - data: *
- optional:
  - aux: *
  - aux2: *
  - aux3: *
  - aux4: *
  - aux5: *
- outputs: index:INT, FINISHED?:BOOLEAN

## DA3GeometryToMesh
module: comfy_extras.nodes_depth_anything_3 | category: image/geometry estimation
- required:
  - da3_geometry: DA3_GEOMETRY
  - batch_index: INT default=0 min=0 max=4096
  - decimation: INT default=1 min=1 max=8
  - discontinuity_threshold: FLOAT default=0.04 min=0.0 max=1.0 step=0.01
  - confidence_threshold: FLOAT default=0.1 min=0.0 max=1.0 step=0.01
  - use_sky_mask: BOOLEAN default=True
  - texture: BOOLEAN default=True
- outputs: MESH:MESH

## DA3Inference
module: comfy_extras.nodes_depth_anything_3 | category: image/geometry estimation
- required:
  - da3_model: DA3_MODEL
  - image: IMAGE
  - resolution: INT default=504 min=140 max=2520 step=14
  - resize_method: COMBO[upper_bound_resize, lower_bound_resize] default='upper_bound_resize'
  - mode: COMFY_DYNAMICCOMBO_V3
- outputs: da3_geometry:DA3_GEOMETRY

## DA3Render
module: comfy_extras.nodes_depth_anything_3 | category: image/geometry estimation
- required:
  - da3_geometry: DA3_GEOMETRY
  - output: COMFY_DYNAMICCOMBO_V3
- outputs: IMAGE:IMAGE

## DaSiWa_CreateExtraMetadata
module: custom_nodes.ComfyUI-DaSiWa-Nodes | category: DaSiWa/IO
- required:
  - key: STRING default='CustomField'
  - value: STRING default=''
- optional:
  - extra_metadata: EXTRA_METADATA
- outputs: EXTRA_METADATA:EXTRA_METADATA

## DaSiWa_EnhancedVideoCombine
module: custom_nodes.ComfyUI-DaSiWa-Nodes | category: DaSiWa/Video
- required:
  - images: IMAGE
  - frame_rate: FLOAT default=24.0 min=0.1 max=240.0 step=0.01
  - codec: COMBO[Auto, AV1, VP9, H.265 (HEVC), H.264] default='Auto'
  - container: COMBO[Auto, WebM, MKV, MP4, Animated WebP, Animated AVIF] default='Auto'
  - bit_depth: COMBO[Auto, 8-bit, 10-bit] default='Auto'
  - quality: INT default=20 min=0 max=51
  - log_level: COMBO[Standard, Verbose] default='Standard'
  - pingpong: BOOLEAN default=False
  - save_metadata: BOOLEAN default=True
  - filename_prefix: STRING default='video_%date:hhmmss%'
  - save_output: BOOLEAN default=True
  - pass_frames: BOOLEAN default=False
  - crop_to_audio: BOOLEAN default=False
  - audio_codec: COMBO[Auto, AAC, Opus, MP3] default='Auto'
  - audio_bitrate: COMBO[64k, 96k, 128k, 160k, 192k, 256k, 320k] default='192k'
  - save_first_frame: BOOLEAN default=False
  - save_last_frame: BOOLEAN default=False
- optional:
  - audio: AUDIO
  - seed: INT
  - free_memory_if_needed: BOOLEAN default=False
- outputs: frames:IMAGE, filename:STRING

## DaSiWa_InpaintComposite
module: custom_nodes.ComfyUI-DaSiWa-Nodes | category: DaSiWa/Inpaint
- required:
  - destination: IMAGE
  - source: IMAGE
  - mask: MASK
  - x: INT default=0
  - y: INT default=0
  - w: INT default=512 min=1 max=8192
  - h: INT default=512 min=1 max=8192
  - correction_method: COMBO[None, Match Channels, Histogram] default='Match Channels'
- outputs: image:IMAGE

## DaSiWa_InpaintCropPrep
module: custom_nodes.ComfyUI-DaSiWa-Nodes | category: DaSiWa/Inpaint
- required:
  - image: IMAGE
  - mask: MASK
  - target_width: INT default=1024 min=64 max=8192
  - target_height: INT default=1024 min=64 max=8192
  - mask_blur: FLOAT default=4.0 min=0.0 max=64.0 step=0.5
  - mask_min: FLOAT default=0.01 min=0.0 max=1.0 step=0.01
  - mask_max: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - grow_px: INT default=32 min=0 max=2048
  - can_shrink: BOOLEAN default=True
- outputs: cropped_image:IMAGE, cropped_mask:MASK, bbox_x:INT, bbox_y:INT, bbox_w:INT, bbox_h:INT

## DaSiWa_LLMAnalyze
module: custom_nodes.ComfyUI-DaSiWa-Nodes | category: DaSiWa/LLM
- required:
  - llm_config: DASIWA_LLM_CONFIG
  - system_prompt_preset: COMBO[custom, enhance_video_ltx23, enhance_video_wan22, caption_image_simple_mixed, caption_image_simple_tag, caption_image_simple_natural, caption_image_detailed_mixed, caption_image_detailed_tag, caption_image_detailed_natural, caption_image_very_detailed_mixed, ... +20] default='custom'
  - system_prompt: STRING default='You are a concise, helpful visual and text analysis assistan...'
  - prompt: STRING default='Follow the selected system instruction for the connected tex...'
  - max_new_tokens: INT default=256 min=1 max=8192 step=1
  - max_input_tokens: INT default=0 min=0 max=131072 step=64
  - temperature: FLOAT default=0.2 min=0.0 max=2.0 step=0.05
  - top_p: FLOAT default=0.9 min=0.01 max=1.0 step=0.01
  - repetition_penalty: FLOAT default=1.0 min=0.1 max=3.0 step=0.05
  - use_kv_cache: BOOLEAN default=True
  - seed: INT default=-1 min=-1 max=18446744073709551615
  - max_frames: INT default=8 min=0 max=256 step=1
  - frame_stride: INT default=1 min=1 max=4096 step=1
  - frame_strategy: COMBO[evenly_spaced, first, middle, last, every_nth] default='evenly_spaced'
  - resize_max_px: INT default=768 min=0 max=4096 step=16
  - resize_algorithm: COMBO[lanczos, bicubic, bilinear, hamming, box, nearest] default='lanczos'
  - memory_cleanup: COMBO[off, before_run, after_run, before_and_after] default='off'
- optional:
  - images: IMAGE
  - text_input: STRING
  - h3_mode: COMBO[T2VA, I2VA, FL2VA, L2VA] default='T2VA'
  - h3_duration: FLOAT default=10.0 min=1.0 max=120.0 step=0.1
- outputs: response:STRING, info:STRING

## DaSiWa_LLMModelSelector
module: custom_nodes.ComfyUI-DaSiWa-Nodes | category: DaSiWa/LLM
- required:
  - model: COMBO[None, MiniMax-H3-Prompt-Rewriter-LoRA-Omni-GGUF\MiniMax-H3-Prompt-Rewriter-LoRA-Omni-Q8_0.gguf, Qwen2.5-Omni-7B-GGUF\Qwen2.5-Omni-7B-Q4_K_M.gguf, Qwen3.5-9B-Uncensored-HauhauCS-Aggressive-Q4_K_M.gguf]
  - custom_path: STRING default=''
  - backend: COMBO[transformers, llama_cpp, ollama, openai, ollama_server] default='transformers'
  - task: COMBO[auto, text, vision] default='auto'
  - device: COMBO[auto, cuda, cpu] default='auto'
  - dtype: COMBO[auto, float16, bfloat16, float32] default='auto'
  - quantization: COMBO[none, 8bit, 4bit] default='none'
  - cache_mode: COMBO[cached, unload_after_run] default='unload_after_run'
  - attention_implementation: COMBO[auto, sdpa, flash_attention_2, eager] default='auto'
  - kv_cache_implementation: COMBO[default, dynamic, static, quantized] default='default'
  - kv_cache_quant_backend: COMBO[quanto, hqq] default='quanto'
  - kv_cache_nbits: COMBO[2, 4, 8] default='4'
  - kv_cache_residual_length: INT default=128 min=0 max=16384 step=8
  - llama_n_ctx: INT default=8192 min=512 max=1048576 step=512
  - llama_n_gpu_layers: INT default=-1 min=-1 max=1000 step=1
  - llama_n_threads: INT default=0 min=0 max=256 step=1
  - llama_chat_format: STRING default=''
  - ollama_model: STRING default=''
  - ollama_timeout: INT default=300 min=1 max=3600 step=1
- optional:
  - server_model: STRING default=''
- outputs: llm_config:DASIWA_LLM_CONFIG

## DaSiWa_LLMPromptWriter
module: custom_nodes.ComfyUI-DaSiWa-Nodes | category: DaSiWa/LLM
- required:
  - model: COMBO[MiniMax-H3-Prompt-Rewriter-LoRA-Omni-GGUF\MiniMax-H3-Prompt-Rewriter-LoRA-Omni-Q8_0.gguf, Qwen2.5-Omni-7B-GGUF\Qwen2.5-Omni-7B-Q4_K_M.gguf, Qwen3.5-9B-Uncensored-HauhauCS-Aggressive-Q4_K_M.gguf]
  - write_for: COMBO[Anima, Illustrious, Krea2, Wan 2.2, LTX 2.3, YuE2 Song Style, YuE2 Lyrics, YuE2 Instrumental Style] default='Anima'
  - start_with: STRING default=''
  - idea: STRING default=''
  - style: COMBO[None, Painterly, Anime, Cel shaded, Flat color, Lineless, Soft painting, Watercolor, Gouache, Sketch, ... +10] default='None'
  - detail: INT default=5 min=1 max=10 step=1
  - creativity: INT default=5 min=1 max=10 step=1
  - max_tokens: INT default=2048 min=128 max=8192 step=64
  - seed: INT default=0 min=0 max=2147483647
  - keep_loaded: BOOLEAN default=False
- optional:
  - images: IMAGE
- outputs: prompt:STRING

## DaSiWa_LTX2LoraLoader
module: custom_nodes.ComfyUI-DaSiWa-Nodes | category: DaSiWa/loaders/lora
- required:
  - model: MODEL
  - clip: CLIP
  - stack_data: STRING default='[]'
  - model_type: COMBO[Basic, LTX-2.3] default='Basic'
- optional:
  - use_cache: BOOLEAN default=False
- outputs: MODEL:MODEL, CLIP:CLIP

## DaSiWa_MetadataConfig
module: custom_nodes.ComfyUI-DaSiWa-Nodes | category: DaSiWa/IO
- required:
  - save_workflow: BOOLEAN default=True
  - model_hash: STRING default=''
- optional:
  - node_positive: CONDITIONING
  - node_negative: CONDITIONING
  - node_model: MODEL
  - node_latent: LATENT
  - node_noise: NOISE
  - node_sigmas: SIGMAS
  - node_sampler: SAMPLER
  - extra_metadata: EXTRA_METADATA
  - text_positive: STRING
  - text_negative: STRING
  - text_steps: INT default=0 min=0 max=10000
  - text_cfg: FLOAT default=0.0 min=0.0 max=100.0 step=0.5
  - text_sampler: COMBO[, euler, euler_ancestral, heun, dpm_2, dpm_2_ancestral, lms, dpmpp_2s_ancestral, dpmpp_2m, dpmpp_2m_sde, ... +3] default=''
  - text_scheduler: COMBO[, normal, karras, exponential, simple, ddim_uniform] default=''
  - text_seed: INT default=0 min=0 max=18446744073709551615
  - text_model: STRING default=''
  - save_output: BOOLEAN
- outputs: config:METADATA_CONFIG

## DaSiWa_MetadataImageSaver
module: custom_nodes.ComfyUI-DaSiWa-Nodes | category: DaSiWa/IO
- required:
  - filename_prefix: STRING default='DaSiWa_%date:yyyyMMdd%_%seed%'
  - file_format: COMBO[webp, png] default='webp'
  - compression: INT default=0 min=0 max=100 step=1
  - save_output: BOOLEAN default=True
- optional:
  - images: IMAGE
  - metadata_config: METADATA_CONFIG
  - extra_metadata: EXTRA_METADATA
- outputs: filename:STRING, metadata:STRING

## DaSiWa_MetadataImageSaverFull
module: custom_nodes.ComfyUI-DaSiWa-Nodes | category: DaSiWa/IO/Advanced
- required:
  - filename_prefix: STRING default='DaSiWa_%date:yyyyMMdd%_%seed%'
  - file_format: COMBO[webp, png] default='webp'
  - compression: INT default=0 min=0 max=100 step=1
  - save_output: BOOLEAN default=True
- optional:
  - images: IMAGE
  - metadata_config: METADATA_CONFIG
  - extra_metadata: EXTRA_METADATA
  - save_workflow: BOOLEAN default=True
  - model_hash: STRING default=''
  - node_positive: CONDITIONING
  - node_negative: CONDITIONING
  - node_model: MODEL
  - node_latent: LATENT
  - node_noise: NOISE
  - node_sigmas: SIGMAS
  - node_sampler: SAMPLER
  - text_positive: STRING
  - text_negative: STRING
  - text_steps: INT default=0 min=0 max=10000
  - text_cfg: FLOAT default=0.0 min=0.0 max=100.0 step=0.5
  - text_sampler: COMBO[, euler, euler_ancestral, heun, dpm_2, dpm_2_ancestral, lms, dpmpp_2s_ancestral, dpmpp_2m, dpmpp_2m_sde, ... +3] default=''
  - text_scheduler: COMBO[, normal, karras, exponential, simple, ddim_uniform] default=''
  - text_seed: INT default=0 min=0 max=18446744073709551615
  - text_model: STRING default=''
- outputs: filename:STRING, metadata:STRING

## DaSiWa_NodeStatusSwitch
module: custom_nodes.ComfyUI-DaSiWa-Nodes | category: DaSiWa/utils
- required:
  - enabled: BOOLEAN default=True
  - trigger_on: COMBO[true → active, false → active] default='true → active'
  - action: COMBO[mute, bypass] default='bypass'
- outputs: enabled_out:BOOLEAN

## DaSiWa_RandomStringPicker
module: custom_nodes.ComfyUI-DaSiWa-Nodes | category: DaSiWa/Text
- required:
  - text: STRING
- outputs: text:STRING

## DaSiWa_ResolutionScaleCalculator
module: custom_nodes.ComfyUI-DaSiWa-Nodes | category: DaSiWa/Scaling
- required:
  - resolution_preset: COMBO[144p, 240p, 360p, 480p, 540p, 576p, 720p, 900p, 1024p, 1080p, ... +22] default='0.52 MP - SD'
  - no_scale: BOOLEAN default=False
  - scale_from_image: BOOLEAN default=True
  - aspect_preset_when_not_image: COMBO[1:1 - Square, 2:3 - Classic, 3:4 - Photo, 5:8 - Tall, 9:16 - Social, 9:21 - Cinema, CUSTOM] default='9:16 - Social'
  - swap_aspect_when_not_image: BOOLEAN default=False
  - custom_aspect_width: INT default=16 min=1 max=8192
  - custom_aspect_height: INT default=9 min=1 max=8192
  - mode: COMBO[Standard, WAN/LTX (Div32), LTX 2-Stage (Div64), CUSTOM] default='WAN/LTX (Div32)'
  - custom_divisor: INT default=8 min=1 max=256 step=1
- optional:
  - image: IMAGE
- outputs: width_int:INT, height_int:INT, width_float:FLOAT, height_float:FLOAT

## DaSiWa_RTX_FrameGeneration
module: custom_nodes.ComfyUI-DaSiWa-Nodes | category: DaSiWa/Video
- required:
  - images: IMAGE
  - generation_type: COMBO[frame rate multiplier, specific timestep]
  - multiplier: INT default=2 min=2 max=16
  - timestep: FLOAT default=0.5 min=0.01 max=0.99 step=0.01
  - mode: COMBO[LOW, MEDIUM, HIGH] default='HIGH'
  - automatic_shot_change_detection: BOOLEAN default=True
  - shot_change: BOOLEAN default=False
  - device_id: INT default=0 min=0 max=8
- optional:
  - image_encoding: COMBO[8-bit RGB, 10-bit RGB (RGB10A2)] default='8-bit RGB'
  - auto_unload_models: BOOLEAN default=True
  - use_mmap: BOOLEAN default=False
- outputs: images:IMAGE

## DaSiWa_RTX_UpscalerRefiner
module: custom_nodes.ComfyUI-DaSiWa-Nodes | category: DaSiWa/Video
- required:
  - images: IMAGE
  - denoise: BOOLEAN default=False
  - denoise_quality: COMBO[Low, Medium, High, Ultra] default='Ultra'
  - deblur: BOOLEAN default=False
  - deblur_quality: COMBO[Low, Medium, High, Ultra] default='Ultra'
  - upscale: COMBO[Off, VSR, High Bitrate, Streaming Medium, Streaming Ultra] default='VSR'
  - upscale_quality: COMBO[Low, Medium, High, Ultra] default='Ultra'
  - resize_type: COMBO[Keep Ratio, Manual, Preset Ratio, Scale, Same Size] default='Scale'
  - scale: FLOAT default=2.0 min=1.0 max=4.0 step=0.05
  - megapixels: FLOAT default=2.0 min=0.01 max=64.0 step=0.01
  - width: INT default=1920 min=64 max=8192 step=8
  - height: INT default=1080 min=64 max=8192 step=8
  - divisible_by: COMBO[8, 16, 32, 64, 128] default='8'
  - ratio_preset: COMBO[1:1, 4:3, 3:2, 16:9, 21:9] default='16:9'
  - resize_method: COMBO[Center Crop (Fill), Letterbox (Fit)] default='Center Crop (Fill)'
  - device_id: INT default=0 min=0 max=8 step=1
- optional:
  - empty_cache: BOOLEAN default=False
  - use_mmap: BOOLEAN default=False
  - auto_unload_models: BOOLEAN default=True
  - chunking: BOOLEAN default=True
  - lossless_fp16: BOOLEAN default=True
  - chunk_frames: INT default=16 min=1 max=1024 step=1
  - image_encoding: COMBO[8-bit RGB, 10-bit RGB (RGB10A2)] default='8-bit RGB'
  - denoise_strength: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - deblur_strength: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - upscale_strength: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - preserve_alpha: BOOLEAN default=False
  - channel_integrity_check: BOOLEAN default=False
  - hdr_enabled: BOOLEAN default=False
  - hdr_contrast: INT default=100 min=0 max=200 step=1
  - hdr_saturation: INT default=100 min=0 max=200 step=1
  - hdr_middle_gray: INT default=50 min=10 max=100 step=1
  - hdr_luminance: INT default=650 min=400 max=2000 step=1
  - hdr_debanding: BOOLEAN default=True
- outputs: images:IMAGE

## DaSiWa_SeamlessLoop
module: custom_nodes.ComfyUI-DaSiWa-Nodes | category: DaSiWa/video
- required:
  - images: IMAGE
- optional:
  - model_name: COMBO[(no native models)]
  - exact_endpoint: BOOLEAN default=False
  - interpolation_backend: COMBO[RIFE / FILM, RTX Frame Generation] default='RIFE / FILM'
  - rtx_mode: COMBO[LOW, MEDIUM, HIGH] default='HIGH'
  - rtx_device_id: INT default=0 min=0 max=8
- outputs: images:IMAGE

## DaSiWa_SeedControl
module: custom_nodes.ComfyUI-DaSiWa-Nodes | category: DaSiWa
- required:
  - seed_value: INT default=0 min=0 max=18446744073709551615 step=1
  - seed_control_state: STRING default='{"mode": "random", "last_seed": null, "recent": []}'
- optional:
  - seed: INT default=0 min=0 max=18446744073709551615 step=1
- outputs: seed:INT, noise:NOISE

## DaSiWa_TorchResize
module: custom_nodes.ComfyUI-DaSiWa-Nodes | category: DaSiWa/Scaling
- required:
  - image: IMAGE
  - size_mode: COMBO[Multiplier, Target resolution] default='Multiplier'
  - aspect_mode: COMBO[Stretch, Fit, Fill and crop, Fit and pad, Long side with divisible crop] default='Fit'
  - target_width: INT default=1920 min=1 max=16384 step=1
  - target_height: INT default=1080 min=1 max=16384 step=1
  - scale_multiplier: FLOAT default=2.0 min=0.01 max=16.0 step=0.01
  - interpolation: COMBO[Nearest, Bilinear, Bicubic, Area, Lanczos] default='Lanczos'
  - gamma_correct: BOOLEAN default=True
  - divisible_by: INT default=1 min=1 max=4096 step=1
  - pad_color: STRING default='0, 0, 0'
  - crop_position: COMBO[center, top-left, top, top-right, left, right, bottom-left, bottom, bottom-right] default='center'
  - batch_size: INT default=0 min=0 max=4096 step=1
  - max_batch_megapixels: FLOAT default=16.0 min=0.25 max=512.0 step=0.25
  - cache_size: INT default=64 min=1 max=512 step=1
- outputs: image:IMAGE

## DaSiWa_Watermark
module: custom_nodes.ComfyUI-DaSiWa-Nodes | category: DaSiWa/Video
- required:
  - images: IMAGE
  - watermark_path: COMBO[01_BEDROOM_LINGERIE.jpg, 32.jpg, 33.jpg, 5slock_B07ref.jpg, 5slock_E10.jpg, 5slock_E10ref.jpg, 5slock_O3.png, 5slock_ORIG01ref.png, 5slock_POOLref.jpg, 5slock_chain_O1_twoshot.png, ... +2817]
  - position: COMBO[bottom-right, bottom-left, top-right, top-left, center] default='bottom-right'
  - scale: FLOAT default=0.2 min=0.01 max=1.0 step=0.01
  - resampling: COMBO[bicubic, bilinear, nearest, area, nearest-exact] default='bicubic'
  - transparency: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - rotation: INT default=0 min=0 max=359 step=1
  - padding_x: INT default=20 min=0 max=4096
  - padding_y: INT default=20 min=0 max=4096
  - optical_padding: BOOLEAN default=False
  - optical_strength: FLOAT default=0.4 min=0.0 max=1.0 step=0.05
  - random_switches: INT default=3 min=1 max=64
  - fade: BOOLEAN default=False
  - fade_margin: FLOAT default=0.1 min=0.01 max=0.5 step=0.01
  - randomize_position: BOOLEAN default=False
  - random_seed: INT default=0 min=0 max=2147483647
- outputs: IMAGE:IMAGE

## DaSiWa_WildcardPresetPromptBuilder
module: custom_nodes.ComfyUI-DaSiWa-Nodes | category: DaSiWa/Text
- required:
  - style: COMBO[Booru, Natural Language] default='Booru'
  - seed: INT default=0 min=0 max=4294967295
  - token_budget: INT default=200 min=1 max=10000
  - selection_state: STRING default='{}'
  - reroll: INT default=0 min=0 max=2147483647
  - auto_reroll: BOOLEAN default=False
- optional:
  - positive_input: STRING
  - negative_input: STRING
- outputs: positive_prompt:STRING, negative_prompt:STRING

## DaSiWaH3ClipAssemble
module: custom_nodes.ComfyUI-DaSiWa-Nodes | category: DaSiWa/MiniMax H3/Continuity
- required:
  - assembly_data: STRING default='{"version":1,"rows":[],"repair_transitions":false,"audio_pol...'
  - filename_prefix: STRING default='H3_Joined'
- outputs: filename:STRING

## DaSiWaH3ContinuityAppend
module: custom_nodes.ComfyUI-DaSiWa-Nodes | category: DaSiWa/MiniMax H3
- required:
  - sampled: LATENT
  - context: DF_H3_CONTINUITY_CONTEXT
- outputs: cumulative_latent:LATENT, ticket:DF_H3_CONTINUITY_TICKET

## DaSiWaH3ContinuityPublish
module: custom_nodes.ComfyUI-DaSiWa-Nodes | category: DaSiWa/MiniMax H3
- required:
  - filename: STRING
  - ticket: DF_H3_CONTINUITY_TICKET
- outputs: status:STRING

## DaSiWaH3ContinuitySegmentDecode
module: custom_nodes.ComfyUI-DaSiWa-Nodes | category: DaSiWa/MiniMax H3
- required:
  - latent: LATENT
  - vae: VAE
  - audio_vae: VAE
  - context: DF_H3_CONTINUITY_CONTEXT
- outputs: images:IMAGE, audio:AUDIO

## DaSiWaH3ContinuitySegmentPrepare
module: custom_nodes.ComfyUI-DaSiWa-Nodes | category: DaSiWa/MiniMax H3
- required:
  - sampled: LATENT
  - context: DF_H3_CONTINUITY_CONTEXT
- outputs: render_latent:LATENT, segment_context:DF_H3_CONTINUITY_CONTEXT, ticket:DF_H3_CONTINUITY_TICKET

## DaSiWaH3RefModExport
module: custom_nodes.ComfyUI-DaSiWa-Nodes | category: DaSiWa/MiniMax H3
- required:
  - timeline_data: STRING default='{}'
  - request_id: STRING default=''
  - name: STRING default=''
  - description: STRING default=''
  - concept_type: COMBO[generic, identity, style, motion, audio]
- optional:
  - vae: VAE
  - audio_vae: VAE
- outputs: refmod_name:STRING

## DaSiWaH3TiledUpscale
module: custom_nodes.ComfyUI-DaSiWa-Nodes | category: DaSiWa/MiniMax H3
- required:
  - model: MODEL
  - conditioning: CONDITIONING
  - latent: LATENT
  - scale: FLOAT default=2.0 min=1.0 max=8.0 step=0.1
  - upscale_model: COMBO[interpolation, minimax_h3_latent_upscaler_3d_conv_v1_bf16.safetensors, minimax_h3_latent_upscaler_3d_fp16.safetensors]
  - steps: INT default=1 min=1 max=100
  - denoise: FLOAT default=0.2 min=0.0 max=1.0 step=0.01
  - seed: INT default=0 min=0 max=18446744073709551615
- optional:
  - director_guide: MINIMAX_H3_DIRECTOR_GUIDE
  - vae: VAE
  - start_image: IMAGE
  - negative: CONDITIONING
  - cfg: FLOAT default=1.0 min=0 max=20 step=0.1
  - sampler_name: COMBO[euler, euler_cfg_pp, euler_ancestral, euler_ancestral_cfg_pp, heun, heunpp2, exp_heun_2_x0, exp_heun_2_x0_sde, dpm_2, dpm_2_ancestral, ... +35] default='euler'
  - scheduler: COMBO[simple, sgm_uniform, karras, exponential, ddim_uniform, beta, normal, linear_quadratic, kl_optimal] default='simple'
  - memory_budget_mb: INT default=0 min=0 max=131072
  - sampler: SAMPLER
  - noise: NOISE
  - continuity_context: DF_H3_CONTINUITY_CONTEXT
  - upscale_precision: COMBO[auto, bf16, fp16, fp32] default='auto'
  - continuity_soft_refine: BOOLEAN default=False
  - continuity_mask_strength: FLOAT default=1.0 min=0.0 max=1.0 step=0.05
  - spatial_tiling: BOOLEAN default=True
  - temporal_chunking: BOOLEAN default=True
  - spike_guard: BOOLEAN default=False
  - guard_sensitivity: FLOAT default=4.3 min=1.5 max=12.0 step=0.1
  - guard_strength: FLOAT default=1.0 min=0.0 max=1.0 step=0.05
  - guard_mode: COMBO[burn_direction, both] default='burn_direction'
  - enforce_memory_budget: BOOLEAN default=True
  - memory_reserve_pct: FLOAT default=5.0 min=0.0 max=100.0 step=5.0
- outputs: latent:LATENT, plan:STRING

## DaSiWaH3TransitionGuide
module: custom_nodes.ComfyUI-DaSiWa-Nodes | category: DaSiWa/MiniMax H3/Continuity
- required:
  - clip: CLIP
  - vae: VAE
  - guide: MINIMAX_H3_DIRECTOR_GUIDE
  - transition_data: STRING default=''
  - audio_vae: VAE
- outputs: positive:CONDITIONING, latent:LATENT, transition:DF_H3_TRANSITION

## DaSiWaH3TransitionRender
module: custom_nodes.ComfyUI-DaSiWa-Nodes | category: DaSiWa/MiniMax H3/Continuity
- required:
  - latent: LATENT
  - vae: VAE
  - audio_vae: VAE
  - transition: DF_H3_TRANSITION
- outputs: filename:STRING

## DaSiWaTiledDiffusion
module: custom_nodes.ComfyUI-DaSiWa-Nodes | category: DaSiWa/Image
- required:
  - model: MODEL
  - tile_width: INT default=1024 min=64 max=8192 step=8
  - tile_height: INT default=1024 min=64 max=8192 step=8
  - overlap: INT default=128 min=0 max=1024 step=8
- outputs: MODEL:MODEL

## DataMonitor
module: custom_nodes.ControlFlowUtils | category: 🐺 VykosX-ControlFlowUtils
- required:
  - text: STRING default=''
  - output_type: COMBO[ANY, STRING, INT, FLOAT, BOOLEAN, LIST, TUPLE, DICT, JSON, FORMULA]
- optional:
  - passthrough: * default=''
  - aux: * default=''
  - aux2: * default=''
  - aux3: * default=''
  - aux4: * default=''
  - aux5: * default=''
- outputs: output:*

## DebugTensorShape+
module: custom_nodes.ComfyUI_essentials | category: essentials/utilities
- required:
  - tensor: *
- outputs: 

## DecimateMesh
module: comfy_extras.nodes_mesh_postprocess | category: 3d/mesh
- required:
  - mesh: MESH
  - target_face_count: INT default=200000 min=0 max=50000000
  - placement_mode: COMFY_DYNAMICCOMBO_V3
- outputs: mesh:MESH

## DecodeAndSaveVideo
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - video_latent: LATENT
  - fps: FLOAT default=25.0 min=0.0 max=999.0 step=0.01
  - filename_prefix: STRING default='video/ComfyUI'
  - format: COMBO[auto, mp4, mkv, webm] default='auto'
  - codec: COMBO[auto, h264, av1] default='auto'
  - video_vae: VAE
  - tiling: COMFY_DYNAMICCOMBO_V3
- optional:
  - audio_latent: LATENT
  - audio_vae: VAE
- outputs: 

## DensePosePreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Faces and Poses Estimators
- required:
  - image: IMAGE
- optional:
  - model: COMBO[densepose_r50_fpn_dl.torchscript, densepose_r101_fpn_dl.torchscript] default='densepose_r50_fpn_dl.torchscript'
  - cmap: COMBO[Viridis (MagicAnimate), Parula (CivitAI)] default='Viridis (MagicAnimate)'
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## DepthAnythingPreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Normal and Depth Estimators
- required:
  - image: IMAGE
- optional:
  - ckpt_name: COMBO[depth_anything_vitl14.pth, depth_anything_vitb14.pth, depth_anything_vits14.pth] default='depth_anything_vitl14.pth'
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## DepthAnythingV2Preprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Normal and Depth Estimators
- required:
  - image: IMAGE
- optional:
  - ckpt_name: COMBO[depth_anything_v2_vitg.pth, depth_anything_v2_vitl.pth, depth_anything_v2_vitb.pth, depth_anything_v2_vits.pth] default='depth_anything_v2_vitl.pth'
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## DiffControlNetLoader
module: nodes | category: model/loaders
- required:
  - model: MODEL
  - control_net_name: COMBO[]
- outputs: CONTROL_NET:CONTROL_NET

## DifferentialDiffusion
module: comfy_extras.nodes_differential_diffusion | category: experimental
- required:
  - model: MODEL
- optional:
  - strength: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: MODEL:MODEL

## DifferentialDiffusionAdvanced
module: custom_nodes.ComfyUI-KJNodes | category: _for_testing
- required:
  - model: MODEL
  - samples: LATENT
  - mask: MASK
  - multiplier: FLOAT default=1.0 min=-10.0 max=10.0 step=0.001
- outputs: MODEL:MODEL, LATENT:LATENT

## DiffusersLoader
module: nodes | category: model/loaders
- required:
  - model_path: COMBO[]
- outputs: MODEL:MODEL, CLIP:CLIP, VAE:VAE

## DiffusionEdge_Preprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Line Extractors
- required:
  - image: IMAGE
- optional:
  - environment: COMBO[indoor, urban, natrual] default='indoor'
  - patch_batch_size: INT default=4 min=1 max=16 step=1
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## DiffusionModelLoaderKJ
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/model_loaders
- required:
  - model_name: COMBO[10Eros_Max_h3_8stepTURBO_beta7_activation_learned_HQ.safetensors, 10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors, FLUX-KLEIN-9B-FP8-NSFW.safetensors, flux-2-klein-9b-kv-fp8.safetensors]
  - weight_dtype: COMBO[default, fp8_e4m3fn, fp8_e4m3fn_fast, fp8_e5m2, fp16, bf16, fp32]
  - compute_dtype: COMBO[default, fp16, bf16, fp32] default='default'
  - patch_cublaslinear: BOOLEAN default=False
  - sage_attention: COMBO[disabled, auto, sageattn_qk_int8_pv_fp16_cuda, sageattn_qk_int8_pv_fp16_triton, sageattn_qk_int8_pv_fp8_cuda, sageattn_qk_int8_pv_fp8_cuda++, sageattn3, sageattn3_per_block_mean] default=False
  - enable_fp16_accumulation: BOOLEAN default=False
- optional:
  - extra_state_dict: STRING
- outputs: MODEL:MODEL

## DiffusionModelSelector
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/model_loaders
- required:
  - model_name: COMBO[10Eros_Max_h3_8stepTURBO_beta7_activation_learned_HQ.safetensors, 10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors, FLUX-KLEIN-9B-FP8-NSFW.safetensors, flux-2-klein-9b-kv-fp8.safetensors]
- outputs: model_path:STRING

## DisableNoise
module: comfy_extras.nodes_custom_sampler | category: model/sampling/noise
- outputs: NOISE:NOISE

## Display Any (rgthree)
module: custom_nodes.rgthree-comfy | category: rgthree
- required:
  - source: *
- outputs: 

## Display Int (rgthree)
module: custom_nodes.rgthree-comfy | category: rgthree
- required:
  - input: INT
- outputs: 

## DisplayAny
module: custom_nodes.ComfyUI_essentials | category: essentials/utilities
- required:
  - input: *
  - mode: COMBO[raw value, tensor shape]
- outputs: STRING:STRING

## DiTBlockLoraLoader
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/lora
- required:
  - model: MODEL
  - strength_model: FLOAT default=1.0 min=-100.0 max=100.0 step=0.01
- optional:
  - lora_name: COMBO[FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, FC_KIERNAN_h3_face_v1.safetensors, ... +48]
  - opt_lora_path: STRING
  - blocks: SELECTEDDITBLOCKS
- outputs: model:MODEL, rank:STRING

## DownloadAndLoadCLIPSeg
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking
- required:
  - model: COMBO[Kijai/clipseg-rd64-refined-fp16, CIDAS/clipseg-rd64-refined]
- outputs: clipseg_model:CLIPSEGMODEL

## DrawBBoxes
module: comfy_extras.nodes_rtdetr | category: image/detection
- required:
  - bboxes: BOUNDING_BOX default={'x': 0, 'y': 0, 'width': 512, 'height': 512}
- optional:
  - image: IMAGE
- outputs: out_image:IMAGE

## DrawInstanceDiffusionTracking
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/InstanceDiffusion
- required:
  - image: IMAGE
  - tracking: TRACKING
  - box_line_width: INT default=2 min=1 max=10 step=1
  - draw_text: BOOLEAN default=True
  - font: COMBO[FreeMono.ttf, FreeMonoBoldOblique.otf, TTNorms-Black.otf]
  - font_size: INT default=20
- outputs: image:IMAGE

## DrawMaskOnImage
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking
- required:
  - image: IMAGE
  - mask: MASK
  - color: STRING default='0, 0, 0'
- optional:
  - device: COMBO[cpu, gpu] default='cpu'
- outputs: images:IMAGE

## DrawText+
module: custom_nodes.ComfyUI_essentials | category: essentials/text
- required:
  - text: STRING default='Hello, World!'
  - font: COMBO[ShareTechMono-Regular.ttf]
  - size: INT default=56 min=1 max=9999 step=1
  - color: STRING default='#FFFFFF'
  - background_color: STRING default='#00000000'
  - shadow_distance: INT default=0 min=0 max=100 step=1
  - shadow_blur: INT default=0 min=0 max=100 step=1
  - shadow_color: STRING default='#000000'
  - horizontal_align: COMBO[left, center, right]
  - vertical_align: COMBO[top, center, bottom]
  - offset_x: INT default=0 min=-16384 max=16384 step=1
  - offset_y: INT default=0 min=-16384 max=16384 step=1
  - direction: COMBO[ltr, rtl]
- optional:
  - img_composite: IMAGE
- outputs: IMAGE:IMAGE, MASK:MASK

## DSINE-NormalMapPreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Normal and Depth Estimators
- required:
  - image: IMAGE
- optional:
  - fov: FLOAT default=60.0 min=0 max=365.0 step=0.01
  - iterations: INT default=5 min=1 max=20 step=1
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## DualCFGGuider
module: comfy_extras.nodes_custom_sampler | category: model/sampling/guiders
- required:
  - model: MODEL
  - cond1: CONDITIONING
  - cond2: CONDITIONING
  - negative: CONDITIONING
  - cfg_conds: FLOAT default=8.0 min=0.0 max=100.0 step=0.1
  - cfg_cond2_negative: FLOAT default=8.0 min=0.0 max=100.0 step=0.1
  - style: COMBO[regular, nested]
- outputs: GUIDER:GUIDER

## DualCLIPLoader
module: nodes | category: model/loaders
- required:
  - clip_name1: COMBO[clip_l.safetensors, qwen3vl_32b_minimax_h3_int4_convrot.safetensors, qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors, qwen_3_4b.safetensors, qwen_3_8b_fp8mixed.safetensors, umt5_xxl_fp8_e4m3fn_scaled.safetensors]
  - clip_name2: COMBO[clip_l.safetensors, qwen3vl_32b_minimax_h3_int4_convrot.safetensors, qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors, qwen_3_4b.safetensors, qwen_3_8b_fp8mixed.safetensors, umt5_xxl_fp8_e4m3fn_scaled.safetensors]
  - type: COMBO[sdxl, sd3, flux, hunyuan_video, hidream, hunyuan_image, hunyuan_video_15, kandinsky5, kandinsky5_image, ltxv, ... +2]
- optional:
  - device: COMBO[default, cpu]
- outputs: CLIP:CLIP

## DualCLIPLoaderGGUF
module: custom_nodes.ComfyUI-GGUF | category: bootleg
- required:
  - clip_name1: COMBO[clip_l.safetensors, qwen3vl_32b_minimax_h3_int4_convrot.safetensors, qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors, qwen_3_4b.safetensors, qwen_3_8b_fp8mixed.safetensors, umt5_xxl_fp8_e4m3fn_scaled.safetensors]
  - clip_name2: COMBO[clip_l.safetensors, qwen3vl_32b_minimax_h3_int4_convrot.safetensors, qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors, qwen_3_4b.safetensors, qwen_3_8b_fp8mixed.safetensors, umt5_xxl_fp8_e4m3fn_scaled.safetensors]
  - type: COMBO[sdxl, sd3, flux, hunyuan_video, hidream, hunyuan_image, hunyuan_video_15, kandinsky5, kandinsky5_image, ltxv, ... +2]
- outputs: CLIP:CLIP

## DualModelGuider
module: comfy_extras.nodes_custom_sampler | category: model/sampling/guiders
- required:
  - model: MODEL
  - positive: CONDITIONING
  - cfg: FLOAT default=4.0 min=0.0 max=100.0 step=0.1
- optional:
  - model_negative: MODEL
  - negative: CONDITIONING
- outputs: GUIDER:GUIDER

## DummyOut
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/misc
- required:
  - any_input: *
- outputs: *:*

## DWPreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Faces and Poses Estimators
- required:
  - image: IMAGE
- optional:
  - detect_hand: COMBO[enable, disable] default='enable'
  - detect_body: COMBO[enable, disable] default='enable'
  - detect_face: COMBO[enable, disable] default='enable'
  - resolution: INT default=512 min=64 max=16384 step=64
  - bbox_detector: COMBO[None, yolox_l.torchscript.pt, yolox_l.onnx, yolo_nas_l_fp16.onnx, yolo_nas_m_fp16.onnx, yolo_nas_s_fp16.onnx] default='yolox_l.onnx'
  - pose_estimator: COMBO[dw-ll_ucoco_384_bs5.torchscript.pt, dw-ll_ucoco_384.onnx, dw-ll_ucoco.onnx] default='dw-ll_ucoco_384_bs5.torchscript.pt'
  - scale_stick_for_xinsr_cn: COMBO[disable, enable] default='disable'
- outputs: IMAGE:IMAGE, POSE_KEYPOINT:POSE_KEYPOINT

## EasyCache
module: comfy_extras.nodes_easycache | category: advanced/debug
- required:
  - model: MODEL
  - reuse_threshold: FLOAT default=0.2 min=0.0 max=3.0 step=0.01
  - start_percent: FLOAT default=0.15 min=0.0 max=1.0 step=0.01
  - end_percent: FLOAT default=0.95 min=0.0 max=1.0 step=0.01
  - verbose: BOOLEAN default=False
- outputs: MODEL:MODEL

## EchoDMDSampler
module: custom_nodes.10S-Comfy-nodes | category: 10S Nodes/Sampling
- outputs: sampler:SAMPLER

## EchoDMDSigmaRemap
module: custom_nodes.10S-Comfy-nodes | category: 10S Nodes/Sampling
- required:
  - sigmas: SIGMAS
  - method: COMBO[interpolate, nearest, none] default='interpolate'
- outputs: sigmas:SIGMAS

## EchoDMDSigmas
module: custom_nodes.10S-Comfy-nodes | category: 10S Nodes/Sampling
- required:
  - preset: COMBO[official, bridge, minimal, 10step, 11step, 12step, custom] default='official'
  - custom_sigmas: STRING default='1.0, 0.99375, 0.9875, 0.98125, 0.975, 0.909375, 0.725, 0.421...'
- outputs: sigmas:SIGMAS

## ElevenLabsAudioIsolation
module: comfy_api_nodes.nodes_elevenlabs | category: partner/audio/ElevenLabs
- required:
  - audio: AUDIO
- outputs: AUDIO:AUDIO

## ElevenLabsInstantVoiceClone
module: comfy_api_nodes.nodes_elevenlabs | category: partner/audio/ElevenLabs
- required:
  - files: COMFY_AUTOGROW_V3
  - remove_background_noise: BOOLEAN default=False
- outputs: voice:ELEVENLABS_VOICE

## ElevenLabsSpeechToSpeech
module: comfy_api_nodes.nodes_elevenlabs | category: partner/audio/ElevenLabs
- required:
  - voice: ELEVENLABS_VOICE
  - audio: AUDIO
  - stability: FLOAT default=0.5 min=0.0 max=1.0 step=0.01
  - model: COMFY_DYNAMICCOMBO_V3
  - output_format: COMBO[mp3_44100_192, opus_48000_192]
  - seed: INT default=0 min=0 max=4294967295
  - remove_background_noise: BOOLEAN default=False
- outputs: AUDIO:AUDIO

## ElevenLabsSpeechToText
module: comfy_api_nodes.nodes_elevenlabs | category: partner/audio/ElevenLabs
- required:
  - audio: AUDIO
  - model: COMFY_DYNAMICCOMBO_V3
  - language_code: STRING default=''
  - num_speakers: INT default=0 min=0 max=32
  - seed: INT default=1 min=0 max=2147483647
- outputs: text:STRING, language_code:STRING, words_json:STRING

## ElevenLabsTextToDialogue
module: comfy_api_nodes.nodes_elevenlabs | category: partner/audio/ElevenLabs
- required:
  - stability: FLOAT default=0.5 min=0.0 max=1.0 step=0.5
  - apply_text_normalization: COMBO[auto, on, off]
  - model: COMBO[eleven_v3]
  - inputs: COMFY_DYNAMICCOMBO_V3
  - language_code: STRING default=''
  - seed: INT default=1 min=0 max=4294967295
  - output_format: COMBO[mp3_44100_192, opus_48000_192]
- outputs: AUDIO:AUDIO

## ElevenLabsTextToSoundEffects
module: comfy_api_nodes.nodes_elevenlabs | category: partner/audio/ElevenLabs
- required:
  - text: STRING default=''
  - model: COMFY_DYNAMICCOMBO_V3
  - output_format: COMBO[mp3_44100_192, opus_48000_192]
- outputs: AUDIO:AUDIO

## ElevenLabsTextToSpeech
module: comfy_api_nodes.nodes_elevenlabs | category: partner/audio/ElevenLabs
- required:
  - voice: ELEVENLABS_VOICE
  - text: STRING default=''
  - stability: FLOAT default=0.5 min=0.0 max=1.0 step=0.01
  - apply_text_normalization: COMBO[auto, on, off]
  - model: COMFY_DYNAMICCOMBO_V3
  - language_code: STRING default=''
  - seed: INT default=1 min=0 max=2147483647
  - output_format: COMBO[mp3_44100_192, opus_48000_192]
- outputs: AUDIO:AUDIO

## ElevenLabsVoiceSelector
module: comfy_api_nodes.nodes_elevenlabs | category: partner/audio/ElevenLabs
- required:
  - voice: COMBO[Roger (male, american), Sarah (female, american), Laura (female, american), Charlie (male, australian), George (male, british), Callum (male, american), River (neutral, american), Harry (male, american), Liam (male, american), Alice (female, british), ... +11]
- outputs: voice:ELEVENLABS_VOICE

## EmptyAceStep1.5LatentAudio
module: comfy_extras.nodes_ace | category: model/latent/ace
- required:
  - seconds: FLOAT default=120.0 min=1.0 max=1000.0 step=0.01
  - batch_size: INT default=1 min=1 max=4096
- outputs: LATENT:LATENT

## EmptyAceStepLatentAudio
module: comfy_extras.nodes_ace | category: model/latent/ace
- required:
  - seconds: FLOAT default=120.0 min=1.0 max=1000.0 step=0.1
  - batch_size: INT default=1 min=1 max=4096
- outputs: LATENT:LATENT

## EmptyARVideoLatent
module: comfy_extras.nodes_ar_video | category: model/latent/autoregressive
- required:
  - width: INT default=832 min=16 max=8192 step=16
  - height: INT default=480 min=16 max=8192 step=16
  - length: INT default=81 min=1 max=1024 step=4
  - batch_size: INT default=1 min=1 max=64
- outputs: LATENT:LATENT

## EmptyAudio
module: comfy_extras.nodes_audio | category: audio
- required:
  - duration: FLOAT default=60.0 min=0.0 max=18446744073709551615 step=0.01
  - sample_rate: INT default=44100 min=1 max=192000
  - channels: INT default=2 min=1 max=2
- outputs: AUDIO:AUDIO

## EmptyChromaRadianceLatentImage
module: comfy_extras.nodes_chroma_radiance | category: model/latent/chroma radiance
- required:
  - width: INT default=1024 min=16 max=16384 step=16
  - height: INT default=1024 min=16 max=16384 step=16
  - batch_size: INT default=1 min=1 max=4096
- outputs: LATENT:LATENT

## EmptyCosmosLatentVideo
module: comfy_extras.nodes_cosmos | category: model/latent/cosmos
- required:
  - width: INT default=1280 min=16 max=16384 step=16
  - height: INT default=704 min=16 max=16384 step=16
  - length: INT default=121 min=1 max=16384 step=8
  - batch_size: INT default=1 min=1 max=4096
- outputs: LATENT:LATENT

## EmptyFlux2LatentImage
module: comfy_extras.nodes_flux | category: model/latent/flux
- required:
  - width: INT default=1024 min=16 max=16384 step=16
  - height: INT default=1024 min=16 max=16384 step=16
  - batch_size: INT default=1 min=1 max=4096
- outputs: LATENT:LATENT

## EmptyHiDreamO1LatentImage
module: comfy_extras.nodes_hidream_o1 | category: model/latent/hidream
- required:
  - width: INT default=2048 min=64 max=4096 step=32
  - height: INT default=2048 min=64 max=4096 step=32
  - batch_size: INT default=1 min=1 max=64
- outputs: LATENT:LATENT

## EmptyHunyuanImageLatent
module: comfy_extras.nodes_hunyuan | category: model/latent/hunyuan image
- required:
  - width: INT default=2048 min=64 max=16384 step=32
  - height: INT default=2048 min=64 max=16384 step=32
  - batch_size: INT default=1 min=1 max=4096
- outputs: LATENT:LATENT

## EmptyHunyuanLatentVideo
module: comfy_extras.nodes_hunyuan | category: model/latent/hunyuan video
- required:
  - width: INT default=848 min=16 max=16384 step=16
  - height: INT default=480 min=16 max=16384 step=16
  - length: INT default=25 min=1 max=16384 step=4
  - batch_size: INT default=1 min=1 max=4096
- outputs: LATENT:LATENT

## EmptyHunyuanVideo15Latent
module: comfy_extras.nodes_hunyuan | category: model/latent/hunyuan video
- required:
  - width: INT default=848 min=16 max=16384 step=16
  - height: INT default=480 min=16 max=16384 step=16
  - length: INT default=25 min=1 max=16384 step=4
  - batch_size: INT default=1 min=1 max=4096
- outputs: LATENT:LATENT

## EmptyImage
module: nodes | category: image
- required:
  - width: INT default=512 min=1 max=16384 step=1
  - height: INT default=512 min=1 max=16384 step=1
  - batch_size: INT default=1 min=1 max=4096
  - color: INT default=0 min=0 max=16777215 step=1
- outputs: IMAGE:IMAGE

## EmptyLatentAudio
module: comfy_extras.nodes_audio | category: model/latent
- required:
  - seconds: FLOAT default=47.6 min=1.0 max=1000.0 step=0.1
  - batch_size: INT default=1 min=1 max=4096
- outputs: LATENT:LATENT

## EmptyLatentHunyuan3Dv2
module: comfy_extras.nodes_hunyuan3d | category: model/latent/hunyuan 3d
- required:
  - resolution: INT default=3072 min=1 max=8192
  - batch_size: INT default=1 min=1 max=4096
- outputs: LATENT:LATENT

## EmptyLatentImage
module: nodes | category: model/latent
- required:
  - width: INT default=1024 min=16 max=16384 step=8
  - height: INT default=1024 min=16 max=16384 step=8
  - batch_size: INT default=1 min=1 max=4096
- outputs: LATENT:LATENT

## EmptyLatentImageCustomPresets
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/latents
- required:
  - dimensions: COMBO[]
  - invert: BOOLEAN default=False
  - batch_size: INT default=1 min=1 max=4096
- outputs: Latent:LATENT, Width:INT, Height:INT

## EmptyLatentImagePresets
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/latents
- required:
  - dimensions: COMBO[512 x 512 (1:1), 768 x 512 (1.5:1), 960 x 512 (1.875:1), 1024 x 512 (2:1), 1024 x 576 (1.778:1), 1536 x 640 (2.4:1), 1344 x 768 (1.75:1), 1216 x 832 (1.46:1), 1152 x 896 (1.286:1), 1024 x 1024 (1:1)] default='512 x 512 (1:1)'
  - invert: BOOLEAN default=False
  - batch_size: INT default=1 min=1 max=4096
- outputs: Latent:LATENT, Width:INT, Height:INT

## EmptyLTXVLatentVideo
module: comfy_extras.nodes_lt | category: model/latent/ltxv
- required:
  - width: INT default=768 min=64 max=16384 step=32
  - height: INT default=512 min=64 max=16384 step=32
  - length: INT default=97 min=1 max=16384 step=8
  - batch_size: INT default=1 min=1 max=4096
- outputs: LATENT:LATENT

## EmptyMiniMaxH3LatentAV
module: comfy_extras.nodes_minimax_h3 | category: model/latent/minimax
- required:
  - width: INT default=1344 min=32 max=16384 step=32
  - height: INT default=768 min=32 max=16384 step=32
  - length: INT default=124 min=5 max=3600 step=17
- outputs: LATENT:LATENT

## EmptyMiniMaxMusic3LatentAudio
module: comfy_extras.nodes_minimax_music | category: model/latent/minimax music
- required:
  - seconds: FLOAT default=120.0 min=0.04 max=360.0 step=0.04
  - batch_size: INT default=1 min=1 max=4096
- outputs: LATENT:LATENT

## EmptyMochiLatentVideo
module: comfy_extras.nodes_mochi | category: model/latent/mochi
- required:
  - width: INT default=848 min=16 max=16384 step=16
  - height: INT default=480 min=16 max=16384 step=16
  - length: INT default=25 min=7 max=16384 step=6
  - batch_size: INT default=1 min=1 max=4096
- outputs: LATENT:LATENT

## EmptyQwenImageLayeredLatentImage
module: comfy_extras.nodes_qwen | category: model/latent/qwen
- required:
  - width: INT default=640 min=16 max=16384 step=16
  - height: INT default=640 min=16 max=16384 step=16
  - layers: INT default=3 min=0 max=16384 step=1
  - batch_size: INT default=1 min=1 max=4096
- outputs: LATENT:LATENT

## EmptySD3LatentImage
module: comfy_extras.nodes_sd3 | category: model/latent/stable diffusion
- required:
  - width: INT default=1024 min=16 max=16384 step=16
  - height: INT default=1024 min=16 max=16384 step=16
  - batch_size: INT default=1 min=1 max=4096
- outputs: LATENT:LATENT

## EmptyTrellis2LatentStructure
module: comfy_extras.nodes_trellis2 | category: model/latent/trellis
- required:
  - batch_size: INT default=1 min=1 max=4096
- outputs: LATENT:LATENT

## EmptyYuE2LatentAudio
module: comfy_extras.nodes_yue2 | category: model/latent/yue2
- required:
  - seconds: FLOAT default=120.0 min=0.04 max=1000.0 step=0.04
  - batch_size: INT default=1 min=1 max=4096
- outputs: LATENT:LATENT

## EncodeVideoComponents
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - video: VIDEO
  - vae: VAE
  - width: INT default=768 min=0 max=16384 step=2
  - height: INT default=512 min=0 max=16384 step=2
  - max_frames: INT default=0 min=0 max=999999 step=1
  - upscale_method: COMBO[nearest-exact, bilinear, area, bicubic, lanczos] default='lanczos'
  - keep_proportion: COMFY_DYNAMICCOMBO_V3
- outputs: latent:LATENT, audio:AUDIO, fps:FLOAT, frame_count:INT

## EndLoop
module: comfy_extras.nodes_loop | category: utilities/looping
- required:
  - accumulate: BOOLEAN default=False
- optional:
  - output_value: COMFY_MATCHTYPE_V3
  - next_iteration_value: COMFY_MATCHTYPE_V3
  - terminations: COMFY_AUTOGROW_V3
- outputs: outputs:COMFY_MATCHTYPE_V3

## EndRecordCUDAMemoryHistory
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/memory
- required:
  - input: *
  - output_path: STRING default='comfy_cuda_memory_history'
- outputs: input:*, output_path:STRING

## Epsilon Scaling
module: comfy_extras.nodes_eps | category: model/patch/unet
- required:
  - model: MODEL
  - scaling_factor: FLOAT default=1.005 min=0.5 max=1.5 step=0.001
- outputs: MODEL:MODEL

## ExecuteAllControlNetPreprocessors
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors
- required:
  - image: IMAGE
- optional:
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## ExponentialScheduler
module: comfy_extras.nodes_custom_sampler | category: model/sampling/schedulers
- required:
  - steps: INT default=20 min=1 max=10000
  - sigma_max: FLOAT default=14.614642 min=0.0 max=5000.0 step=0.01
  - sigma_min: FLOAT default=0.0291675 min=0.0 max=5000.0 step=0.01
- outputs: SIGMAS:SIGMAS

## ExtendIntermediateSigmas
module: comfy_extras.nodes_custom_sampler | category: model/sampling/sigmas
- required:
  - sigmas: SIGMAS
  - steps: INT default=2 min=1 max=100
  - start_at_sigma: FLOAT default=-1.0 min=-1.0 max=20000.0 step=0.01
  - end_at_sigma: FLOAT default=12.0 min=0.0 max=20000.0 step=0.01
  - spacing: COMBO[linear, cosine, sine]
- outputs: SIGMAS:SIGMAS

## FaceAlign
module: custom_nodes.ComfyUI_FaceAnalysis | category: FaceAnalysis
- required:
  - analysis_models: ANALYSIS_MODELS
  - image_from: IMAGE
- optional:
  - image_to: IMAGE
- outputs: IMAGE:IMAGE

## FaceAnalysisModels
module: custom_nodes.ComfyUI_FaceAnalysis | category: FaceAnalysis
- required:
  - library: COMBO[insightface, auraface]
  - provider: COMBO[CPU, CUDA, DirectML, OpenVINO, ROCM, CoreML]
- outputs: ANALYSIS_MODELS:ANALYSIS_MODELS

## FaceBoundingBox
module: custom_nodes.ComfyUI_FaceAnalysis | category: FaceAnalysis
- required:
  - analysis_models: ANALYSIS_MODELS
  - image: IMAGE
  - padding: INT default=0 min=0 max=4096 step=1
  - padding_percent: FLOAT default=0.0 min=0.0 max=2.0 step=0.05
  - index: INT default=-1 min=-1 max=4096 step=1
- outputs: IMAGE:IMAGE, x:INT, y:INT, width:INT, height:INT

## FaceEmbedDistance
module: custom_nodes.ComfyUI_FaceAnalysis | category: FaceAnalysis
- required:
  - analysis_models: ANALYSIS_MODELS
  - reference: IMAGE
  - image: IMAGE
  - similarity_metric: COMBO[L2_norm, cosine, euclidean]
  - filter_thresh: FLOAT default=100.0 min=0.001 max=100.0 step=0.001
  - filter_best: INT default=0 min=0 max=4096 step=1
  - generate_image_overlay: BOOLEAN default=True
- outputs: IMAGE:IMAGE, distance:FLOAT

## FaceSegmentation
module: custom_nodes.ComfyUI_FaceAnalysis | category: FaceAnalysis
- required:
  - analysis_models: ANALYSIS_MODELS
  - image: IMAGE
  - area: COMBO[face, main_features, eyes, left_eye, right_eye, nose, mouth, face+forehead (if available)]
  - grow: INT default=0 min=-4096 max=4096 step=1
  - grow_tapered: BOOLEAN default=False
  - blur: INT default=13 min=1 max=4096 step=2
- outputs: mask:MASK, image:IMAGE, seg_mask:MASK, seg_image:IMAGE, x:INT, y:INT, width:INT, height:INT

## FaceWarp
module: custom_nodes.ComfyUI_FaceAnalysis | category: FaceAnalysis
- required:
  - analysis_models: ANALYSIS_MODELS
  - image_from: IMAGE
  - image_to: IMAGE
  - keypoints: COMBO[main features, full face, full face+forehead (if available)]
  - grow: INT default=0 min=-4096 max=4096 step=1
  - blur: INT default=13 min=1 max=4096 step=2
- outputs: IMAGE:IMAGE, MASK:MASK

## FacialPartColoringFromPoseKps
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Pose Keypoint Postprocess
- required:
  - pose_kps: POSE_KEYPOINT
  - mode: COMBO[point, polygon] default='polygon'
  - skin: STRING default='rgb(0, 153, 255)'
  - left_eye: STRING default='rgb(0, 204, 153)'
  - right_eye: STRING default='rgb(255, 153, 0)'
  - nose: STRING default='rgb(255, 102, 255)'
  - upper_lip: STRING default='rgb(102, 0, 51)'
  - inner_mouth: STRING default='rgb(255, 204, 255)'
  - lower_lip: STRING default='rgb(255, 0, 102)'
- outputs: IMAGE:IMAGE

## FakeScribblePreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Line Extractors
- required:
  - image: IMAGE
- optional:
  - safe: COMBO[enable, disable] default='enable'
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## FallbackAnyBatch
module: custom_nodes.ControlFlowUtils | category: 🐺 VykosX-ControlFlowUtils
- required:
  - method_for_images: COMBO[nearest-exact, bilinear, area, bicubic, lanczos] default='lanczos'
- optional:
  - input1: *
  - input2: *
  - input3: *
  - input4: *
  - input5: *
  - input6: *
- outputs: batch:*

## FallbackImagePreviewer
module: custom_nodes.ControlFlowUtils | category: 🐺 VykosX-ControlFlowUtils
- required:
  - images: IMAGE
- optional:
  - fallback_width: INT default=512 min=0 max=16384 step=256
  - fallback_height: INT default=512 min=0 max=16384 step=256
  - save_image: BOOLEAN default=False
  - filename_prefix: STRING default='ComfyUI'
- outputs: passthrough:IMAGE

## FastPreview
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/experimental
- required:
  - image: IMAGE
  - format: COMBO[JPEG, PNG] default='JPEG'
  - max_size: INT default=768 min=128 max=4096 step=64
- outputs: 

## FastPreviewBatch
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/experimental
- required:
  - input: IMAGE,MASK
  - max_thumb_size: INT default=512 min=512 max=1024 step=8
  - crf: INT default=25 min=0 max=51 step=1
  - max_grid_frames: INT default=1024 min=1 max=4096 step=1
- outputs: 

## FeatherMask
module: comfy_extras.nodes_mask | category: image/mask
- required:
  - mask: MASK
  - left: INT default=0 min=0 max=16384 step=1
  - top: INT default=0 min=0 max=16384 step=1
  - right: INT default=0 min=0 max=16384 step=1
  - bottom: INT default=0 min=0 max=16384 step=1
- outputs: MASK:MASK

## File3DToSplat
module: comfy_extras.nodes_gaussian_splat | category: 3d/splat
- required:
  - model_3d: FILE_3D,FILE_3D_SPLAT_ANY,FILE_3D_PLY,FILE_3D_SPLAT,FILE_3D_KSPLAT,FILE_3D_SPZ
- outputs: splat:SPLAT

## FillHoles
module: comfy_extras.nodes_mesh_postprocess | category: 3d/mesh
- required:
  - mesh: MESH
  - max_perimeter: FLOAT default=0.03 min=0.0 step=0.0001
  - weld_epsilon_rel: FLOAT default=1e-05 min=0.0 step=1e-06
  - max_vertices: INT default=16 min=3 max=1024
  - fill_chains: BOOLEAN default=False
- outputs: mesh:MESH

## FilterZeroMasksAndCorrespondingImages
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking
- required:
  - masks: MASK
- optional:
  - original_images: IMAGE
- outputs: non_zero_masks_out:MASK, non_zero_mask_images_out:IMAGE, zero_mask_images_out:IMAGE, zero_mask_images_out_indexes:INDEXES

## FishAudioInstantVoiceClone
module: comfy_api_nodes.nodes_fishaudio | category: partner/audio/Fish Audio
- required:
  - files: COMFY_AUTOGROW_V3
  - enhance_audio_quality: BOOLEAN default=True
- outputs: voice:FISHAUDIO_VOICE

## FishAudioSpeechToText
module: comfy_api_nodes.nodes_fishaudio | category: partner/audio/Fish Audio
- required:
  - audio: AUDIO
  - language: STRING default=''
  - precise_timestamps: BOOLEAN default=False
- outputs: text:STRING, language_code:STRING, segments_json:STRING

## FishAudioTextToSpeech
module: comfy_api_nodes.nodes_fishaudio | category: partner/audio/Fish Audio
- required:
  - text: STRING default=''
  - model: COMFY_DYNAMICCOMBO_V3
  - seed: INT default=42 min=0 max=2147483647
- outputs: AUDIO:AUDIO

## FishAudioVoiceSelector
module: comfy_api_nodes.nodes_fishaudio | category: partner/audio/Fish Audio
- required:
  - voice: COMFY_DYNAMICCOMBO_V3
- outputs: voice:FISHAUDIO_VOICE

## FixPulidFluxPatch
module: custom_nodes.ComfyUI_PuLID_Flux_ll | category: pulid
- required:
  - model: MODEL
- outputs: MODEL:MODEL

## FlipSigmas
module: comfy_extras.nodes_custom_sampler | category: model/sampling/sigmas
- required:
  - sigmas: SIGMAS
- outputs: SIGMAS:SIGMAS

## FlipSigmasAdjusted
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/noise
- required:
  - sigmas: SIGMAS
  - divide_by_last_sigma: BOOLEAN default=False
  - divide_by: FLOAT default=1 min=1 max=255 step=0.01
  - offset_by: INT default=1 min=-100 max=100 step=1
- outputs: SIGMAS:SIGMAS, sigmas_string:STRING

## FloatConstant
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/constants
- required:
  - value: FLOAT default=0.0 min=-18446744073709551615 max=18446744073709551615 step=1e-05
- outputs: value:FLOAT

## FloatToMask
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking/generate
- required:
  - input_values: FLOAT default=0
  - width: INT default=100 min=1
  - height: INT default=100 min=1
- outputs: MASK:MASK

## FloatToSigmas
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/noise
- required:
  - float_list: FLOAT default=0.0
- outputs: SIGMAS:SIGMAS

## Flux2ImageNode
module: comfy_api_nodes.nodes_bfl | category: partner/image/BFL
- required:
  - prompt: STRING default=''
  - model: COMFY_DYNAMICCOMBO_V3
  - seed: INT default=0 min=0 max=18446744073709551615
- outputs: IMAGE:IMAGE

## Flux2MaxImageNode
module: comfy_api_nodes.nodes_bfl | category: partner/image/BFL
- required:
  - prompt: STRING default=''
  - width: INT default=1024 min=256 max=2048 step=32
  - height: INT default=768 min=256 max=2048 step=32
  - seed: INT default=0 min=0 max=18446744073709551615
  - prompt_upsampling: BOOLEAN default=True
- optional:
  - images: IMAGE
- outputs: IMAGE:IMAGE

## Flux2ProImageNode
module: comfy_api_nodes.nodes_bfl | category: partner/image/BFL
- required:
  - prompt: STRING default=''
  - width: INT default=1024 min=256 max=2048 step=32
  - height: INT default=768 min=256 max=2048 step=32
  - seed: INT default=0 min=0 max=18446744073709551615
  - prompt_upsampling: BOOLEAN default=True
- optional:
  - images: IMAGE
- outputs: IMAGE:IMAGE

## Flux2Scheduler
module: comfy_extras.nodes_flux | category: model/sampling/schedulers
- required:
  - steps: INT default=20 min=1 max=4096
  - width: INT default=1024 min=16 max=16384 step=1
  - height: INT default=1024 min=16 max=16384 step=1
- outputs: SIGMAS:SIGMAS

## Flux3ImageToVideoNode
module: comfy_api_nodes.nodes_bfl | category: partner/video/BFL
- required:
  - prompt: STRING default=''
  - keyframes: COMFY_AUTOGROW_V3
  - placement: COMFY_DYNAMICCOMBO_V3
  - aspect_ratio: COMBO[auto, 21:9, 2:1, 16:9, 4:3, 1:1, 3:4, 9:16] default='auto'
  - duration: COMBO[auto, 5, 6, 7, 8, 9, 10, 11, 12, 13, ... +7] default='auto'
  - resolution: COMBO[720p, 1080p] default='720p'
  - generate_audio: BOOLEAN default=True
  - safety_tolerance: INT default=2 min=0 max=4
  - seed: INT default=42 min=0 max=4294967295
- outputs: VIDEO:VIDEO

## Flux3TextToVideoNode
module: comfy_api_nodes.nodes_bfl | category: partner/video/BFL
- required:
  - prompt: STRING default=''
  - aspect_ratio: COMBO[auto, 21:9, 2:1, 16:9, 4:3, 1:1, 3:4, 9:16] default='auto'
  - duration: COMBO[auto, 5, 6, 7, 8, 9, 10, 11, 12, 13, ... +7] default='auto'
  - resolution: COMBO[720p, 1080p] default='720p'
  - generate_audio: BOOLEAN default=True
  - safety_tolerance: INT default=2 min=0 max=4
  - seed: INT default=42 min=0 max=4294967295
- outputs: VIDEO:VIDEO

## Flux3VideoContinuationNode
module: comfy_api_nodes.nodes_bfl | category: partner/video/BFL
- required:
  - video: VIDEO
  - prompt: STRING default=''
  - aspect_ratio: COMBO[auto, 21:9, 2:1, 16:9, 4:3, 1:1, 3:4, 9:16] default='auto'
  - duration: COMBO[auto, 5, 6, 7, 8, 9, 10, 11, 12, 13, ... +7] default='auto'
  - resolution: COMBO[720p, 1080p] default='720p'
  - generate_audio: BOOLEAN default=True
  - safety_tolerance: INT default=2 min=0 max=4
  - seed: INT default=42 min=0 max=4294967295
- outputs: VIDEO:VIDEO

## FluxAttentionSeeker+
module: custom_nodes.ComfyUI_essentials | category: essentials/conditioning
- required:
  - clip: CLIP
  - apply_to_query: BOOLEAN default=True
  - apply_to_key: BOOLEAN default=True
  - apply_to_value: BOOLEAN default=True
  - apply_to_out: BOOLEAN default=True
  - clip_l_0: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_l_1: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_l_2: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_l_3: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_l_4: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_l_5: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_l_6: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_l_7: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_l_8: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_l_9: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_l_10: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_l_11: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_0: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_1: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_2: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_3: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_4: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_5: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_6: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_7: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_8: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_9: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_10: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_11: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_12: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_13: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_14: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_15: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_16: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_17: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_18: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_19: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_20: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_21: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_22: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_23: FLOAT default=1.0 min=0 max=5 step=0.05
- outputs: CLIP:CLIP

## FluxBlockLoraSelect
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/experimental
- required:
  - double_blocks.0.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.1.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.2.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.3.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.4.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.5.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.6.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.7.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.8.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.9.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.10.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.11.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.12.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.13.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.14.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.15.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.16.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.17.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.18.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.0.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.1.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.2.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.3.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.4.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.5.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.6.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.7.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.8.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.9.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.10.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.11.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.12.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.13.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.14.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.15.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.16.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.17.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.18.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.19.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.20.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.21.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.22.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.23.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.24.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.25.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.26.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.27.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.28.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.29.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.30.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.31.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.32.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.33.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.34.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.35.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.36.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.37.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
- outputs: blocks:SELECTEDDITBLOCKS

## FluxBlocksBuster+
module: custom_nodes.ComfyUI_essentials | category: essentials/conditioning
- required:
  - model: MODEL
  - blocks: STRING default='## 0 = 1.0\n## 1 = 1.0\n## 2 = 1.0\n## 3 = 1.0\n## 4 = 1.0\n## 5 ...'
- outputs: MODEL:MODEL, patched_blocks:STRING

## FluxDisableGuidance
module: comfy_extras.nodes_flux | category: model/conditioning/flux
- required:
  - conditioning: CONDITIONING
- outputs: CONDITIONING:CONDITIONING

## FluxEraseNode
module: comfy_api_nodes.nodes_bfl | category: partner/image/BFL
- required:
  - image: IMAGE
  - mask: MASK
  - dilate_pixels: INT default=10 min=0 max=25
- optional:
  - seed: INT default=0 min=0 max=2147483647
- outputs: IMAGE:IMAGE

## FluxGuidance
module: comfy_extras.nodes_flux | category: model/conditioning/flux
- required:
  - conditioning: CONDITIONING
  - guidance: FLOAT default=3.5 min=0.0 max=100.0 step=0.1
- outputs: CONDITIONING:CONDITIONING

## FluxKontextImageScale
module: comfy_extras.nodes_flux | category: model/conditioning/flux
- required:
  - image: IMAGE
- outputs: IMAGE:IMAGE

## FluxKontextMaxImageNode
module: comfy_api_nodes.nodes_bfl | category: partner/image/BFL
- required:
  - prompt: STRING default=''
  - aspect_ratio: STRING default='16:9'
  - guidance: FLOAT default=3.0 min=0.1 max=99.0 step=0.1
  - steps: INT default=50 min=1 max=150
  - seed: INT default=1234 min=0 max=18446744073709551615
  - prompt_upsampling: BOOLEAN default=False
- optional:
  - input_image: IMAGE
- outputs: IMAGE:IMAGE

## FluxKontextMultiReferenceLatentMethod
module: comfy_extras.nodes_flux | category: model/conditioning/flux
- required:
  - conditioning: CONDITIONING
  - reference_latents_method: COMBO[offset, index, uxo/uno, index_timestep_zero]
- outputs: CONDITIONING:CONDITIONING

## FluxKontextProImageNode
module: comfy_api_nodes.nodes_bfl | category: partner/image/BFL
- required:
  - prompt: STRING default=''
  - aspect_ratio: STRING default='16:9'
  - guidance: FLOAT default=3.0 min=0.1 max=99.0 step=0.1
  - steps: INT default=50 min=1 max=150
  - seed: INT default=1234 min=0 max=18446744073709551615
  - prompt_upsampling: BOOLEAN default=False
- optional:
  - input_image: IMAGE
- outputs: IMAGE:IMAGE

## FluxKVCache
module: comfy_extras.nodes_flux | category: experimental
- required:
  - model: MODEL
- outputs: MODEL:MODEL

## FluxProExpandNode
module: comfy_api_nodes.nodes_bfl | category: partner/image/BFL
- required:
  - image: IMAGE
  - prompt: STRING default=''
  - prompt_upsampling: BOOLEAN default=False
  - top: INT default=0 min=0 max=2048
  - bottom: INT default=0 min=0 max=2048
  - left: INT default=0 min=0 max=2048
  - right: INT default=0 min=0 max=2048
  - guidance: FLOAT default=60 min=1.5 max=100
  - steps: INT default=50 min=15 max=50
  - seed: INT default=0 min=0 max=18446744073709551615
- outputs: IMAGE:IMAGE

## FluxProFillNode
module: comfy_api_nodes.nodes_bfl | category: partner/image/BFL
- required:
  - image: IMAGE
  - mask: MASK
  - prompt: STRING default=''
  - prompt_upsampling: BOOLEAN default=False
  - guidance: FLOAT default=60 min=1.5 max=100
  - steps: INT default=50 min=15 max=50
  - seed: INT default=0 min=0 max=18446744073709551615
- outputs: IMAGE:IMAGE

## FluxProUltraImageNode
module: comfy_api_nodes.nodes_bfl | category: partner/image/BFL
- required:
  - prompt: STRING default=''
  - prompt_upsampling: BOOLEAN default=False
  - seed: INT default=0 min=0 max=18446744073709551615
  - aspect_ratio: STRING default='16:9'
  - raw: BOOLEAN default=False
- optional:
  - image_prompt: IMAGE
  - image_prompt_strength: FLOAT default=0.1 min=0.0 max=1.0 step=0.01
- outputs: IMAGE:IMAGE

## FluxSamplerParams+
module: custom_nodes.ComfyUI_essentials | category: essentials/sampling
- required:
  - model: MODEL
  - conditioning: CONDITIONING
  - latent_image: LATENT
  - seed: STRING default='?'
  - sampler: STRING default='euler'
  - scheduler: STRING default='simple'
  - steps: STRING default='20'
  - guidance: STRING default='3.5'
  - max_shift: STRING default=''
  - base_shift: STRING default=''
  - denoise: STRING default='1.0'
- optional:
  - loras: LORA_PARAMS
- outputs: latent:LATENT, params:SAMPLER_PARAMS

## FluxVideoEditNode
module: comfy_api_nodes.nodes_bfl | category: partner/video/BFL
- required:
  - video: VIDEO
  - prompt: STRING default=''
  - auto_downscale: BOOLEAN default=True
  - safety_tolerance: INT default=4 min=0 max=4
  - seed: INT default=42 min=0 max=4294967295
- outputs: VIDEO:VIDEO

## FluxVideoUpscaleNode
module: comfy_api_nodes.nodes_bfl | category: partner/video/BFL
- required:
  - video: VIDEO
  - upscale_factor: FLOAT default=2.0 min=1.5 max=3.0 step=0.1
  - mode: COMBO[creative, precise] default='creative'
  - prompt: STRING default=''
  - auto_downscale: BOOLEAN default=True
  - safety_tolerance: INT default=2 min=0 max=4
  - seed: INT default=42 min=0 max=4294967295
- outputs: VIDEO:VIDEO

## FluxVTONode
module: comfy_api_nodes.nodes_bfl | category: partner/image/BFL
- required:
  - person: IMAGE
  - garment: IMAGE
  - prompt: STRING default=''
  - seed: INT default=0 min=0 max=18446744073709551615
- outputs: IMAGE:IMAGE

## FolderSearch
module: custom_nodes.ControlFlowUtils | category: 🐺 VykosX-ControlFlowUtils
- required:
  - folder_path: STRING default='/'
  - search_mask: STRING default='*.*'
  - output_type: BOOLEAN default=False
  - recursive: BOOLEAN default=True
  - include_directories: BOOLEAN default=False
  - return_full_path: BOOLEAN default=False
  - relative_filenames: BOOLEAN default=False
- optional:
  - save_output_to: STRING default=''
- outputs: output:*

## FrameInterpolate
module: comfy_extras.nodes_frame_interpolation | category: video
- required:
  - interp_model: INTERP_MODEL
  - images: IMAGE
  - multiplier: INT default=2 min=2 max=16
- outputs: IMAGE:IMAGE

## FrameInterpolationModelLoader
module: comfy_extras.nodes_frame_interpolation | category: model/loaders
- required:
  - model_name: COMBO[]
- outputs: INTERP_MODEL:INTERP_MODEL

## FreeU
module: comfy_extras.nodes_freelunch | category: model/patch/unet
- required:
  - model: MODEL
  - b1: FLOAT default=1.1 min=0.0 max=10.0 step=0.01
  - b2: FLOAT default=1.2 min=0.0 max=10.0 step=0.01
  - s1: FLOAT default=0.9 min=0.0 max=10.0 step=0.01
  - s2: FLOAT default=0.2 min=0.0 max=10.0 step=0.01
- outputs: MODEL:MODEL

## FreeU_V2
module: comfy_extras.nodes_freelunch | category: model/patch/unet
- required:
  - model: MODEL
  - b1: FLOAT default=1.3 min=0.0 max=10.0 step=0.01
  - b2: FLOAT default=1.4 min=0.0 max=10.0 step=0.01
  - s1: FLOAT default=0.9 min=0.0 max=10.0 step=0.01
  - s2: FLOAT default=0.2 min=0.0 max=10.0 step=0.01
- outputs: MODEL:MODEL

## FreSca
module: comfy_extras.nodes_fresca | category: experimental
- required:
  - model: MODEL
  - scale_low: FLOAT default=1.0 min=0 max=10 step=0.01
  - scale_high: FLOAT default=1.25 min=0 max=10 step=0.01
  - freq_cutoff: INT default=20 min=1 max=10000 step=1
- outputs: MODEL:MODEL

## GarbageCollector
module: custom_nodes.ControlFlowUtils | category: 🐺 VykosX-ControlFlowUtils
- required:
  - Input: *
  - RAM: BOOLEAN default=True
  - Mode: BOOLEAN default=False
- outputs: Output:*

## GeminiImage2Node
module: comfy_api_nodes.nodes_gemini | category: partner/image/Gemini
- required:
  - prompt: STRING default=''
  - model: COMBO[gemini-3-pro-image-preview, Nano Banana 2 (Gemini 3.1 Flash Image)]
  - seed: INT default=42 min=0 max=18446744073709551615
  - aspect_ratio: COMBO[auto, 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, ... +1] default='auto'
  - resolution: COMBO[1K, 2K, 4K]
  - response_modalities: COMBO[IMAGE+TEXT, IMAGE]
- optional:
  - images: IMAGE
  - files: GEMINI_INPUT_FILES
  - system_prompt: STRING default='You are an expert image-generation engine. You must ALWAYS p...'
- outputs: IMAGE:IMAGE, STRING:STRING

## GeminiImageNode
module: comfy_api_nodes.nodes_gemini | category: partner/image/Gemini
- required:
  - prompt: STRING default=''
  - model: COMBO[gemini-2.5-flash-image]
  - seed: INT default=42 min=0 max=18446744073709551615
- optional:
  - images: IMAGE
  - files: GEMINI_INPUT_FILES
  - aspect_ratio: COMBO[auto, 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, ... +1] default='auto'
  - response_modalities: COMBO[IMAGE+TEXT, IMAGE]
  - system_prompt: STRING default='You are an expert image-generation engine. You must ALWAYS p...'
- outputs: IMAGE:IMAGE, STRING:STRING

## GeminiInputFiles
module: comfy_api_nodes.nodes_gemini | category: partner/text/Gemini
- required:
  - file: COMBO[]
- optional:
  - GEMINI_INPUT_FILES: GEMINI_INPUT_FILES
- outputs: GEMINI_INPUT_FILES:GEMINI_INPUT_FILES

## GeminiNanoBanana2
module: comfy_api_nodes.nodes_gemini | category: partner/image/Gemini
- required:
  - prompt: STRING default=''
  - model: COMBO[Nano Banana 2 (Gemini 3.1 Flash Image)]
  - seed: INT default=42 min=0 max=18446744073709551615
  - aspect_ratio: COMBO[auto, 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, ... +1] default='auto'
  - resolution: COMBO[1K, 2K, 4K]
  - response_modalities: COMBO[IMAGE, IMAGE+TEXT]
  - thinking_level: COMBO[MINIMAL, HIGH]
- optional:
  - images: IMAGE
  - files: GEMINI_INPUT_FILES
  - system_prompt: STRING default='You are an expert image-generation engine. You must ALWAYS p...'
- outputs: IMAGE:IMAGE, STRING:STRING, thought_image:IMAGE

## GeminiNanoBanana2V2
module: comfy_api_nodes.nodes_gemini | category: partner/image/Gemini
- required:
  - prompt: STRING default=''
  - model: COMFY_DYNAMICCOMBO_V3
  - seed: INT default=42 min=0 max=18446744073709551615
  - response_modalities: COMBO[IMAGE, IMAGE+TEXT]
- optional:
  - system_prompt: STRING default='You are an expert image-generation engine. You must ALWAYS p...'
  - temperature: FLOAT default=1.0 min=0.0 max=2.0 step=0.01
  - top_p: FLOAT default=0.95 min=0.0 max=1.0 step=0.01
- outputs: IMAGE:IMAGE, STRING:STRING, thought_image:IMAGE

## GeminiNode
module: comfy_api_nodes.nodes_gemini | category: partner/text/Gemini
- required:
  - prompt: STRING default=''
  - model: COMBO[gemini-2.5-pro, gemini-2.5-flash, gemini-3-pro-preview, gemini-3-1-pro, gemini-3-1-flash-lite] default='gemini-3-1-pro'
  - seed: INT default=42 min=0 max=18446744073709551615
- optional:
  - images: IMAGE
  - audio: AUDIO
  - video: VIDEO
  - files: GEMINI_INPUT_FILES
  - system_prompt: STRING default=''
- outputs: STRING:STRING

## GeminiNodeV2
module: comfy_api_nodes.nodes_gemini | category: partner/text/Gemini
- required:
  - prompt: STRING default=''
  - model: COMFY_DYNAMICCOMBO_V3
  - seed: INT default=42 min=0 max=2147483647
- optional:
  - system_prompt: STRING default=''
- outputs: STRING:STRING

## GeminiNodeV3
module: comfy_api_nodes.nodes_gemini | category: partner/text/Gemini
- required:
  - model: COMFY_DYNAMICCOMBO_V3
- outputs: STRING:STRING

## GeminiVideoOmni
module: comfy_api_nodes.nodes_gemini | category: partner/video/Gemini
- required:
  - model: COMFY_DYNAMICCOMBO_V3
  - seed: INT default=42 min=0 max=2147483647
- outputs: VIDEO:VIDEO, STRING:STRING

## GeminiVideoOmniV2
module: comfy_api_nodes.nodes_gemini | category: partner/video/Gemini
- required:
  - model: COMFY_DYNAMICCOMBO_V3
- outputs: VIDEO:VIDEO, STRING:STRING

## GenerateNoise
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/noise
- required:
  - width: INT default=512 min=16 max=4096 step=1
  - height: INT default=512 min=16 max=4096 step=1
  - batch_size: INT default=1 min=1 max=4096
  - seed: INT default=123 min=0 max=18446744073709551615 step=1
  - multiplier: FLOAT default=1.0 min=0.0 max=4096 step=0.01
  - constant_batch_noise: BOOLEAN default=False
  - normalize: BOOLEAN default=False
- optional:
  - model: MODEL
  - sigmas: SIGMAS
  - latent_channels: COMBO[4, 16]
  - shape: COMBO[BCHW, BCTHW, BTCHW]
- outputs: LATENT:LATENT

## GenerateTracks
module: comfy_extras.nodes_wanmove | category: model/conditioning/wan/move
- required:
  - width: INT default=832 min=16 max=4096 step=16
  - height: INT default=480 min=16 max=4096 step=16
  - start_x: FLOAT default=0.0 min=0.0 max=1.0 step=0.01
  - start_y: FLOAT default=0.0 min=0.0 max=1.0 step=0.01
  - end_x: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - end_y: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - num_frames: INT default=81 min=1 max=1024
  - num_tracks: INT default=5 min=1 max=100
  - track_spread: FLOAT default=0.025 min=0.0 max=1.0 step=0.001
  - bezier: BOOLEAN default=False
  - mid_x: FLOAT default=0.5 min=0.0 max=1.0 step=0.01
  - mid_y: FLOAT default=0.5 min=0.0 max=1.0 step=0.01
  - interpolation: COMBO[linear, ease_in, ease_out, ease_in_out, constant]
- optional:
  - track_mask: MASK
- outputs: TRACKS:TRACKS, track_length:INT

## Get resolution [Crystools]
module: custom_nodes.ComfyUI-Crystools | category: crystools 🪛/Image
- required:
  - image: IMAGE
- outputs: width:INT, height:INT

## Get3DComponents
module: comfy_extras.nodes_mesh_io | category: 3d
- required:
  - model_3d: FILE_3D_GLB,FILE_3D_GLTF,FILE_3D_OBJ,FILE_3D_STL,FILE_3D
- outputs: mesh:MESH

## GetICLoRAParameters
module: comfy_extras.nodes_lt | category: model/conditioning/ltxv
- required:
  - iclora_model: MODEL
- outputs: iclora_parameters:IC_LORA_PARAMETERS

## GetImageRangeFromBatch
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - start_index: INT default=0 min=-1 max=4096 step=1
  - num_frames: INT default=1 min=1 max=4096 step=1
- optional:
  - images: IMAGE
  - masks: MASK
- outputs: IMAGE:IMAGE, MASK:MASK

## GetImagesFromBatchIndexed
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - images: IMAGE
  - indexes: STRING default='0, 1, 2'
- outputs: IMAGE:IMAGE

## GetImageSize
module: comfy_extras.nodes_images | category: image
- required:
  - image: IMAGE
- outputs: width:INT, height:INT, batch_size:INT

## GetImageSize+
module: custom_nodes.ComfyUI_essentials | category: essentials/image utils
- required:
  - image: IMAGE
- outputs: width:INT, height:INT, count:INT

## GetImageSizeAndCount
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - image: IMAGE
- outputs: image:IMAGE, width:INT, height:INT, count:INT

## GetItemFromList
module: comfy_extras.nodes_toolkit | category: utilities
- required:
  - list: *
  - index: INT default=0
- outputs: *:*

## GetLatentRangeFromBatch
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/latents
- required:
  - latents: LATENT
  - start_index: INT default=0 min=-1 max=4096 step=1
  - num_frames: INT default=1 min=-1 max=4096 step=1
- outputs: LATENT:LATENT

## GetLatentsFromBatchIndexed
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/latents
- required:
  - latents: LATENT
  - indexes: STRING default='0, 1, 2'
  - latent_format: COMBO[BCHW, BTCHW, BCTHW] default='BCHW'
- outputs: LATENT:LATENT

## GetLatentSizeAndCount
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - latent: LATENT
- outputs: latent:LATENT, batch_size:INT, channels:INT, frames:INT, height:INT, width:INT

## GetMaskSizeAndCount
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking
- required:
  - mask: MASK
- outputs: mask:MASK, width:INT, height:INT, count:INT

## GetMeshInfo
module: comfy_extras.nodes_save_3d | category: 3d/mesh
- required:
  - mesh: MESH
- outputs: mesh:MESH, info:STRING

## GetPreviewOverrideFramesKJ
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/sampling
- required:
  - model: MODEL
  - after_sample: LATENT,IMAGE
- outputs: frames:IMAGE

## GetSplatCount
module: comfy_extras.nodes_gaussian_splat | category: 3d/splat
- required:
  - splat: SPLAT
- outputs: splat:SPLAT, count:INT

## GetTrackRange
module: custom_nodes.ComfyUI-KJNodes | category: conditioning/video_models
- required:
  - tracks: TRACKS
  - start_index: INT default=24 min=-10000 max=10000 step=1
  - num_frames: INT default=10 min=1 max=10000 step=1
- outputs: TRACKS:TRACKS

## GetVideoComponents
module: comfy_extras.nodes_video | category: video
- required:
  - video: VIDEO
- outputs: images:IMAGE, audio:AUDIO, fps:FLOAT, bit_depth:COMBO, color_space:COMBO

## GGUFLoaderKJ
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/model_loaders
- required:
  - model_name: COMBO[]
  - extra_model_name: COMBO[none] default='none'
  - dequant_dtype: COMBO[default, target, float32, float16, bfloat16] default='default'
  - patch_dtype: COMBO[default, target, float32, float16, bfloat16] default='default'
  - patch_on_device: BOOLEAN default=False
  - enable_fp16_accumulation: BOOLEAN default=False
  - attention_override: COMBO[none, sdpa, sageattn, xformers, flashattn] default='none'
- outputs: MODEL:MODEL

## GITSScheduler
module: comfy_extras.nodes_gits | category: model/sampling/schedulers
- required:
  - coeff: FLOAT default=1.2 min=0.8 max=1.5 step=0.05
  - steps: INT default=10 min=2 max=1000
  - denoise: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: SIGMAS:SIGMAS

## GLIGENLoader
module: nodes | category: model/loaders
- required:
  - gligen_name: COMBO[]
- outputs: GLIGEN:GLIGEN

## GLIGENTextBoxApply
module: nodes | category: model/conditioning/gligen
- required:
  - conditioning_to: CONDITIONING
  - clip: CLIP
  - gligen_textbox_model: GLIGEN
  - text: STRING
  - width: INT default=64 min=8 max=16384 step=8
  - height: INT default=64 min=8 max=16384 step=8
  - x: INT default=0 min=0 max=16384 step=8
  - y: INT default=0 min=0 max=16384 step=8
- outputs: CONDITIONING:CONDITIONING

## GLIGENTextBoxApplyBatchCoords
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/experimental
- required:
  - conditioning_to: CONDITIONING
  - latents: LATENT
  - clip: CLIP
  - gligen_textbox_model: GLIGEN
  - coordinates: STRING
  - text: STRING
  - width: INT default=128 min=8 max=4096 step=8
  - height: INT default=128 min=8 max=4096 step=8
- optional:
  - size_multiplier: FLOAT default=[1.0]
- outputs: conditioning:CONDITIONING, coord_preview:IMAGE

## GLSLShader
module: comfy_extras.nodes_glsl | category: image/shader
- required:
  - fragment_shader: STRING default='#version 300 es\nprecision highp float;\n\nuniform sampler2D u_...'
  - size_mode: COMFY_DYNAMICCOMBO_V3
  - images: COMFY_AUTOGROW_V3
  - floats: COMFY_AUTOGROW_V3
  - ints: COMFY_AUTOGROW_V3
  - bools: COMFY_AUTOGROW_V3
  - curves: COMFY_AUTOGROW_V3
- outputs: IMAGE0:IMAGE, IMAGE1:IMAGE, IMAGE2:IMAGE, IMAGE3:IMAGE

## GradientToFloat
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - image: IMAGE
  - steps: INT default=10 min=2 max=10000 step=1
- outputs: float_x:FLOAT, float_y:FLOAT

## GrokImageEditNode
module: comfy_api_nodes.nodes_grok | category: partner/image/Grok
- required:
  - model: COMBO[grok-imagine-image-quality, grok-imagine-image-pro, grok-imagine-image]
  - image: IMAGE
  - prompt: STRING
  - resolution: COMBO[1K, 2K]
  - number_of_images: INT default=1 min=1 max=10 step=1
  - seed: INT default=0 min=0 max=2147483647 step=1
- optional:
  - aspect_ratio: COMBO[auto, 1:1, 2:3, 3:2, 3:4, 4:3, 9:16, 16:9, 9:19.5, 19.5:9, ... +4]
- outputs: IMAGE:IMAGE

## GrokImageEditNodeV2
module: comfy_api_nodes.nodes_grok | category: partner/image/Grok
- required:
  - prompt: STRING default=''
  - model: COMFY_DYNAMICCOMBO_V3
  - seed: INT default=0 min=0 max=2147483647 step=1
- outputs: IMAGE:IMAGE

## GrokImageNode
module: comfy_api_nodes.nodes_grok | category: partner/image/Grok
- required:
  - model: COMBO[grok-imagine-image-2.0, grok-imagine-image-quality, grok-imagine-image-pro, grok-imagine-image]
  - prompt: STRING
  - aspect_ratio: COMBO[1:1, 2:3, 3:2, 3:4, 4:3, 9:16, 16:9, 9:19.5, 19.5:9, 9:20, ... +3]
  - number_of_images: INT default=1 min=1 max=10 step=1
  - seed: INT default=0 min=0 max=2147483647 step=1
- optional:
  - resolution: COMBO[1K, 2K]
  - quality: COMBO[medium, low]
- outputs: IMAGE:IMAGE

## GrokVideoEditNode
module: comfy_api_nodes.nodes_grok | category: partner/video/Grok
- required:
  - model: COMBO[grok-imagine-video]
  - prompt: STRING
  - video: VIDEO
  - seed: INT default=0 min=0 max=2147483647 step=1
- outputs: VIDEO:VIDEO

## GrokVideoExtendNode
module: comfy_api_nodes.nodes_grok | category: partner/video/Grok
- required:
  - prompt: STRING
  - video: VIDEO
  - model: COMFY_DYNAMICCOMBO_V3
  - seed: INT default=0 min=0 max=2147483647 step=1
- outputs: VIDEO:VIDEO

## GrokVideoNode
module: comfy_api_nodes.nodes_grok | category: partner/video/Grok
- required:
  - model: COMBO[grok-imagine-video, grok-imagine-video-1.5]
  - prompt: STRING
  - resolution: COMBO[480p, 720p, 1080p]
  - aspect_ratio: COMBO[auto, 16:9, 4:3, 3:2, 1:1, 2:3, 3:4, 9:16]
  - duration: INT default=6 min=1 max=15 step=1
  - seed: INT default=0 min=0 max=2147483647 step=1
- optional:
  - image: IMAGE
- outputs: VIDEO:VIDEO

## GrokVideoReferenceNode
module: comfy_api_nodes.nodes_grok | category: partner/video/Grok
- required:
  - prompt: STRING
  - model: COMFY_DYNAMICCOMBO_V3
  - seed: INT default=0 min=0 max=2147483647 step=1
- outputs: VIDEO:VIDEO

## GrowMask
module: comfy_extras.nodes_mask | category: image/mask
- required:
  - mask: MASK
  - expand: INT default=0 min=-16384 max=16384 step=1
  - tapered_corners: BOOLEAN default=True
- outputs: MASK:MASK

## GrowMaskWithBlur
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking
- required:
  - mask: MASK
  - expand: INT default=0 min=-16384 max=16384 step=1
  - incremental_expandrate: FLOAT default=0.0 min=0.0 max=100.0 step=0.1
  - tapered_corners: BOOLEAN default=True
  - flip_input: BOOLEAN default=False
  - blur_radius: FLOAT default=0.0 min=0.0 max=100 step=0.1
  - lerp_alpha: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - decay_factor: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- optional:
  - fill_holes: BOOLEAN default=False
- outputs: mask:MASK, mask_inverted:MASK

## GuidanceTimestepping+
module: custom_nodes.ComfyUI_essentials | category: essentials/sampling
- required:
  - model: MODEL
  - value: FLOAT default=2.0 min=0.0 max=100.0 step=0.05
  - start_at: FLOAT default=0.2 min=0.0 max=1.0 step=0.01
  - end_at: FLOAT default=0.8 min=0.0 max=1.0 step=0.01
- outputs: MODEL:MODEL

## H3AdalnModality
module: custom_nodes.ComfyUI-H3-PowerLoraStack | category: MiniMax-H3/lora
- required:
  - video: FLOAT default=1.0 min=0.0 max=2.0 step=0.05
  - text: FLOAT default=1.0 min=0.0 max=2.0 step=0.05
  - audio: FLOAT default=1.0 min=0.0 max=2.0 step=0.05
- outputs: adaln_modality:H3_MODALITY, info:STRING

## H3AnySwitch
module: custom_nodes.ComfyUI-H3-Multishot | category: H3/episode
- required:
  - use_on: BOOLEAN
- optional:
  - off_path: *
  - on_path: *
- outputs: value:*

## H3AudioTrimStart
module: custom_nodes.ComfyUI-H3-Multishot | category: audio
- required:
  - audio: AUDIO
  - seconds: FLOAT default=0.04167 min=0.0 max=10.0 step=1e-05
- outputs: AUDIO:AUDIO

## H3AutoRefs
module: custom_nodes.ComfyUI-H3-Multishot | category: video/minimax
- required:
  - max_per_character: INT default=3 min=1 max=9
- optional:
  - prompt_text: STRING
  - refs_root: STRING default=''
  - characters: STRING default=''
  - overrides: STRING default=''
  - on_no_match: COMBO[error, no_reference] default='no_reference'
  - enabled: BOOLEAN
  - extra_text: STRING
- outputs: ref_1:IMAGE, ref_2:IMAGE, ref_3:IMAGE, ref_4:IMAGE, ref_5:IMAGE, ref_6:IMAGE, ref_7:IMAGE, ref_8:IMAGE, ref_9:IMAGE, prompt_out:STRING, report:STRING, refs_batch:IMAGE, found:BOOLEAN

## H3CartridgeLoader
module: custom_nodes.ComfyUI-H3-Multishot | category: loaders/minimax
- required:
  - cartridge: COMBO[(no cartridges in input/riftcast/)]
  - max_refs: INT default=9 min=1 max=9
- optional:
  - manual_path: STRING default=''
- outputs: ref_1:IMAGE, ref_2:IMAGE, ref_3:IMAGE, ref_4:IMAGE, ref_5:IMAGE, ref_6:IMAGE, ref_7:IMAGE, ref_8:IMAGE, ref_9:IMAGE, voice:AUDIO, subject_block:STRING, dna_text:STRING, speaker_tag:STRING, accent_line:STRING, rooms_text:STRING, ref_count:INT, report:STRING

## H3ChainNormalize
module: custom_nodes.ComfyUI-H3-Multishot | category: video/minimax
- required:
  - images: IMAGE
  - baseline_seconds: FLOAT default=10.0 min=2.0 max=30.0 step=0.5
  - skip_seconds: FLOAT default=2.0 min=0.0 max=10.0 step=0.5
  - fps: FLOAT default=24.0 min=1.0 max=120.0
  - strength: FLOAT default=1.0 min=0.0 max=2.0 step=0.05
  - deadband: FLOAT default=1.06 min=1.0 max=1.5 step=0.01
  - ema: FLOAT default=0.1 min=0.01 max=1.0 step=0.01
  - colour_match: BOOLEAN default=True
- outputs: images:IMAGE

## H3ClipLoaderAny
module: custom_nodes.ComfyUI-H3-Multishot | category: loaders/minimax
- required:
  - clip_name: COMBO[clip_l.safetensors, qwen3vl_32b_minimax_h3_int4_convrot.safetensors, qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors, qwen_3_4b.safetensors, qwen_3_8b_fp8mixed.safetensors, umt5_xxl_fp8_e4m3fn_scaled.safetensors]
  - type: COMBO[stable_diffusion, stable_cascade, sd3, stable_audio, mochi, ltxv, pixart, cosmos, lumina2, wan, ... +19]
- optional:
  - mmproj_name: COMBO[(auto)] default='(auto)'
- outputs: CLIP:CLIP

## H3ConcatAV
module: custom_nodes.ComfyUI-H3-Multishot | category: video/minimax
- required:
  - images_a: IMAGE
  - audio_a: AUDIO
- optional:
  - images_b: IMAGE
  - audio_b: AUDIO
  - match_b: COMBO[match_to_a, off] default='match_to_a'
- outputs: images:IMAGE, audio:AUDIO

## H3ConditionStrength
module: custom_nodes.ComfyUI-H3-Multishot | category: conditioning/video_models
- required:
  - conditioning: CONDITIONING
  - visual_strength: FLOAT default=0.999 min=0.0 max=1.0 step=0.001
  - audio_strength: FLOAT default=1.0 min=0.0 max=1.0 step=0.001
- outputs: CONDITIONING:CONDITIONING

## H3ContinuumAssembleSeamV35
module: custom_nodes.ComfyUI-H3-Continuum | category: MiniMax H3/Continuum
- required:
  - images: IMAGE
  - audio: AUDIO
  - assembly_plan: H3_CONTINUUM_ASSEMBLY_PLAN
  - exact_total_duration: BOOLEAN default=True
  - audio_seam: COMBO[Off, Auto] default='Auto'
  - video_seam: COMBO[Auto, Auto 2, Analyze Only, Off] default='Auto'
  - buffer_backend: COMBO[Auto, RAM, Disk-backed] default='Auto'
  - diagnostics: COMBO[Basic, Detailed Report, Off] default='Basic'
- optional:
  - driving_audio: AUDIO
- outputs: images:IMAGE, audio:AUDIO, report:STRING

## H3ContinuumLoadVideo
module: custom_nodes.ComfyUI-H3-Continuum | category: MiniMax H3/Continuum
- required:
  - enable_video: BOOLEAN default=True
  - file: COMBO[5slock_ext_SB1r3.mp4, 5slock_lcv_SB1r3_24fps.mp4, MAX5S_ORC_B0_ST6_1344x768_noRIFE_s2015873178_00001_.mp4, MAXOPT_R3b_full_simple_sA_s43029049_00001_.mp4, MAXOPT_R3b_sA_tail2s_for_hop.mp4, MAX_1MIN_T0_PRIOR.mp4, MAX_REF_ORC_BJ_OPT_SCH_WARM_BETA_s25102401_00001_.mp4, c04_cell1_native.mp4, c04_cell1_tail22.mp4, c04_cell2_native.mp4, ... +66]
  - force_rate: FLOAT default=24.0 min=0.0 max=120.0 step=0.01
- outputs: images:IMAGE, audio:AUDIO

## H3ContinuumReferenceAudios
module: custom_nodes.ComfyUI-H3-Continuum | category: MiniMax H3/Continuum/Input
- optional:
  - reference_audio_1: AUDIO
  - reference_audio_2: AUDIO
  - reference_audio_3: AUDIO
  - reference_audio_vae: VAE
- outputs: audio_references:H3_CONTINUUM_AUDIO_REFERENCES

## H3ContinuumReferenceImages
module: custom_nodes.ComfyUI-H3-Continuum | category: MiniMax H3/Continuum/Input
- optional:
  - reference_image_4: IMAGE
  - reference_image_5: IMAGE
  - reference_image_6: IMAGE
  - reference_image_7: IMAGE
  - reference_image_8: IMAGE
  - reference_image_9: IMAGE
- outputs: image_references:H3_CONTINUUM_IMAGE_REFERENCES

## H3ContinuumReferenceImagesV39
module: custom_nodes.ComfyUI-H3-Continuum | category: MiniMax H3/Continuum/Input
- required:
  - reference_use: COMBO[All chunks, Per chunk] default='All chunks'
  - reference_r1_chunks: STRING default='off'
  - reference_r2_chunks: STRING default='off'
  - reference_r3_chunks: STRING default='off'
  - reference_r4_chunks: STRING default='off'
  - reference_r5_chunks: STRING default='off'
  - reference_r6_chunks: STRING default='off'
  - reference_r7_chunks: STRING default='off'
  - reference_r8_chunks: STRING default='off'
  - reference_r9_chunks: STRING default='off'
- optional:
  - reference_image_1: IMAGE
  - reference_image_2: IMAGE
  - reference_image_3: IMAGE
  - reference_image_4: IMAGE
  - reference_image_5: IMAGE
  - reference_image_6: IMAGE
  - reference_image_7: IMAGE
  - reference_image_8: IMAGE
  - reference_image_9: IMAGE
- outputs: reference_images:H3_CONTINUUM_REFERENCE_IMAGES_V39

## H3ContinuumSamplerV38
module: custom_nodes.ComfyUI-H3-Continuum | category: MiniMax H3/Continuum
- required:
  - model: MODEL
  - clip: CLIP
  - video_vae: VAE
  - sampler: SAMPLER
  - sigmas: SIGMAS
  - sequence_prompt: STRING
  - prompt_mode: COMBO[Auto, Fixed, List, Timeline] default='Auto'
  - chunks: INT default=3 min=1 max=16 step=1
  - chunk_seconds: FLOAT default=5.0 min=4.0 max=30.0 step=0.1
  - aspect: COMBO[Auto from First Image, Landscape 16:9, Portrait 9:16, Square 1:1] default='Auto from First Image'
  - preset: COMBO[Draft — 0.30 MP, Balanced — 0.60 MP, Native 768, Custom] default='Draft — 0.30 MP'
  - custom_mp: FLOAT default=0.3 min=0.1 max=16.0 step=0.01
  - continuity: COMBO[Auto — conservative, Balanced — 22 frames, Fast — 5 frames, Strong — 39 frames (Experimental)] default='Balanced — 22 frames'
  - base_seed: INT default=0 min=0 max=18446744073709551615
  - audio_continuity: BOOLEAN default=True
  - diagnostics: COMBO[Basic, Detailed Report, Off] default='Basic'
  - reroll_from_chunk: COMBO[Auto, Chunk 1, Chunk 2, Chunk 3, Chunk 4, Chunk 5, Chunk 6, Chunk 7, Chunk 8, Chunk 9, ... +7] default='Auto'
  - reroll_nonce: INT default=0 min=0 max=4294967295 step=1
  - strict_compatibility: BOOLEAN default=True
  - debug: BOOLEAN default=False
  - show_preview: BOOLEAN default=True
  - run_storage: COMBO[Off, Save + Auto Resume] default='Off'
  - run_name: STRING default=''
  - reference_size: COMBO[Match Output, Max Identity] default='Match Output'
  - project_id: STRING default=''
  - video_reference_size: COMBO[Efficient - 0.4 MP, Balanced - 0.6 MP, Match Output] default='Efficient - 0.4 MP'
  - continuation_backend: COMBO[Standard, Compatibility] default='Standard'
  - generation_mode: COMBO[Full Run, Review Each Chunk] default='Full Run'
  - review_action: COMBO[Continue / Next, Regenerate Current, Finish Remaining] default='Continue / Next'
  - take_group: INT default=0 min=0 max=16 step=1
  - take_revision_id: STRING default=''
  - take_action: COMBO[Automatic, Use This Take, Continue From Here] default='Automatic'
  - size_source: COMBO[First Image, Manual, Legacy Aspect] default='Legacy Aspect'
  - width: INT default=736 min=32 max=16384 step=32
  - height: INT default=416 min=32 max=16384 step=32
- optional:
  - first_frame: IMAGE
  - last_frame: IMAGE
  - reference_image_1: IMAGE
  - reference_image_2: IMAGE
  - reference_image_3: IMAGE
  - reference_video_1: IMAGE
  - driving_audio: AUDIO
  - audio_vae: VAE
  - reference_audio_1: AUDIO
  - reference_audio_vae: VAE
  - guide: H3_CONTINUUM_STILL_IMAGE_GUIDE
  - audio_references: H3_CONTINUUM_AUDIO_REFERENCES
  - image_references: H3_CONTINUUM_IMAGE_REFERENCES
  - video_reference_mode: COMBO[Follow Timeline, Repeat Reference] default='Repeat Reference'
- outputs: video_latents:LATENT, audio_latents:LATENT, assembly_plan:H3_CONTINUUM_ASSEMBLY_PLAN, status:STRING, driving_audio:AUDIO, refine_context:H3_CONTINUUM_REFINE_CONTEXT

## H3ContinuumSamplerV39
module: custom_nodes.ComfyUI-H3-Continuum | category: MiniMax H3/Continuum
- required:
  - model: MODEL
  - clip: CLIP
  - video_vae: VAE
  - sampler: SAMPLER
  - sigmas: SIGMAS
  - sequence_prompt: STRING
  - prompt_mode: COMBO[Auto, Fixed, List, Timeline] default='Auto'
  - chunks: INT default=3 min=1 max=16 step=1
  - chunk_seconds: FLOAT default=5.0 min=4.0 max=30.0 step=0.1
  - aspect: COMBO[Auto from First Image, Landscape 16:9, Portrait 9:16, Square 1:1] default='Auto from First Image'
  - preset: COMBO[Draft — 0.30 MP, Balanced — 0.60 MP, Native 768, Custom] default='Draft — 0.30 MP'
  - custom_mp: FLOAT default=0.3 min=0.1 max=16.0 step=0.01
  - continuity: COMBO[Auto — conservative, Balanced — 22 frames, Fast — 5 frames, Strong — 39 frames (Experimental)] default='Balanced — 22 frames'
  - base_seed: INT default=0 min=0 max=18446744073709551615
  - audio_continuity: BOOLEAN default=True
  - diagnostics: COMBO[Basic, Detailed Report, Off] default='Basic'
  - reroll_from_chunk: COMBO[Auto, Chunk 1, Chunk 2, Chunk 3, Chunk 4, Chunk 5, Chunk 6, Chunk 7, Chunk 8, Chunk 9, ... +7] default='Auto'
  - reroll_nonce: INT default=0 min=0 max=4294967295 step=1
  - strict_compatibility: BOOLEAN default=True
  - debug: BOOLEAN default=False
  - show_preview: BOOLEAN default=True
  - run_storage: COMBO[Off, Save + Auto Resume] default='Off'
  - run_name: STRING default=''
  - reference_size: COMBO[Match Output, Max Identity] default='Match Output'
  - project_id: STRING default=''
  - video_reference_size: COMBO[Efficient - 0.4 MP, Balanced - 0.6 MP, Match Output] default='Efficient - 0.4 MP'
  - continuation_backend: COMBO[Standard, Compatibility] default='Standard'
  - generation_mode: COMBO[Full Run, Review Each Chunk] default='Full Run'
  - review_action: COMBO[Continue / Next, Regenerate Current, Finish Remaining] default='Continue / Next'
  - take_group: INT default=0 min=0 max=16 step=1
  - take_revision_id: STRING default=''
  - take_action: COMBO[Automatic, Use This Take, Continue From Here] default='Automatic'
  - size_source: COMBO[First Image, Manual, Legacy Aspect] default='Legacy Aspect'
  - width: INT default=736 min=32 max=16384 step=32
  - height: INT default=416 min=32 max=16384 step=32
- optional:
  - first_frame: IMAGE
  - last_frame: IMAGE
  - reference_video_1: IMAGE
  - driving_audio: AUDIO
  - audio_vae: VAE
  - reference_audio_1: AUDIO
  - reference_audio_vae: VAE
  - guide: H3_CONTINUUM_STILL_IMAGE_GUIDE
  - audio_references: H3_CONTINUUM_AUDIO_REFERENCES
  - video_reference_mode: COMBO[Follow Timeline, Repeat Reference] default='Repeat Reference'
  - reference_images: H3_CONTINUUM_REFERENCE_IMAGES_V39
- outputs: video_latents:LATENT, audio_latents:LATENT, assembly_plan:H3_CONTINUUM_ASSEMBLY_PLAN, status:STRING, driving_audio:AUDIO, refine_context:H3_CONTINUUM_REFINE_CONTEXT

## H3ContinuumSecondPassV35
module: custom_nodes.ComfyUI-H3-Continuum | category: MiniMax H3/Continuum/Advanced
- required:
  - model: MODEL
  - clip: CLIP
  - sampler: SAMPLER
  - sigmas: SIGMAS
  - video_latents: LATENT
  - audio_latents: LATENT
  - assembly_plan: H3_CONTINUUM_ASSEMBLY_PLAN
  - refine_seed: INT default=0 min=0 max=18446744073709551615
- optional:
  - refine_context: H3_CONTINUUM_REFINE_CONTEXT
  - video_vae: VAE
- outputs: refined_video_latents:LATENT, audio_latents:LATENT, updated_assembly_plan:H3_CONTINUUM_ASSEMBLY_PLAN, status:STRING

## H3ContinuumVideoAdapter
module: custom_nodes.ComfyUI-H3-Continuum | category: MiniMax H3/Continuum/Input
- required:
  - video: VIDEO
  - force_rate: FLOAT default=24.0 min=0.0 max=120.0 step=0.01
- outputs: images:IMAGE, audio:AUDIO

## H3DecodeCacheHelper
module: custom_nodes.ComfyUI-H3-Continuum | category: MiniMax H3/Continuum/Helpers
- required:
  - cache_mode: COMBO[Auto, RAM, Off] default='Auto'
  - ram_budget_mb: INT default=256 min=0 max=8192 step=128
  - disk_budget_gb: INT default=8 min=0 max=128 step=1
  - reset_token: INT default=0 min=0 max=2147483647
- optional:
  - video_samples: LATENT
  - video_vae: VAE
  - audio_samples: LATENT
  - audio_vae: VAE
- outputs: images:IMAGE, audio:AUDIO, report:STRING

## H3EasyLoadAudio
module: custom_nodes.ComfyUI-H3-Continuum | category: MiniMax H3/Continuum
- required:
  - audio: COMBO[5slock_ext_SB1r3.mp4, 5slock_lcv_SB1r3_24fps.mp4, MAX5S_ORC_B0_ST6_1344x768_noRIFE_s2015873178_00001_.mp4, MAXOPT_R3b_full_simple_sA_s43029049_00001_.mp4, MAXOPT_R3b_sA_tail2s_for_hop.mp4, MAX_1MIN_T0_PRIOR.mp4, MAX_REF_ORC_BJ_OPT_SCH_WARM_BETA_s25102401_00001_.mp4, c04_cell1_native.mp4, c04_cell1_tail22.mp4, c04_cell2_native.mp4, ... +66]
- outputs: AUDIO:AUDIO

## H3EasyLoadImage
module: custom_nodes.ComfyUI-H3-Continuum | category: MiniMax H3/Continuum
- required:
  - image: COMBO[01_BEDROOM_LINGERIE.jpg, 32.jpg, 33.jpg, 5slock_B07ref.jpg, 5slock_E10.jpg, 5slock_E10ref.jpg, 5slock_O3.png, 5slock_ORIG01ref.png, 5slock_POOLref.jpg, 5slock_chain_O1_twoshot.png, ... +2817]
- outputs: IMAGE:IMAGE, MASK:MASK

## H3EpisodeSplit
module: custom_nodes.ComfyUI-H3-Multishot | category: video/minimax
- required:
  - script: STRING default=''
  - bindings: STRING default=''
- outputs: block1_prompt:STRING, rest_script:STRING, info:STRING

## H3ExtendTake
module: custom_nodes.ComfyUI-H3-Multishot | category: H3/episode
- required:
  - take_seconds: FLOAT default=30.0 min=3.0 max=600.0 step=0.5
  - window: COMBO[auto, 243, 226, 209, 192, 175, 158, 141, 124, 107, ... +1] default='auto'
  - width: INT default=736 min=64 max=2048 step=16
  - height: INT default=1280 min=64 max=2048 step=16
  - fps: INT default=24 min=1 max=60
  - pin_frames: INT default=22 min=0 max=56
- optional:
  - model: MODEL
- outputs: num_shots:INT, frames_per_shot:INT, total_frames:INT, summary:STRING

## H3FreeTextEncoder
module: custom_nodes.ComfyUI-H3-Multishot | category: conditioning/video_models
- required:
  - conditioning: CONDITIONING
  - clip: CLIP
- outputs: CONDITIONING:CONDITIONING

## H3InfiniteTakeSampler
module: custom_nodes.ComfyUI-H3-Multishot | category: sampling/minimax
- required:
  - model: MODEL
  - clip: CLIP
  - video_vae: VAE
  - audio_vae: VAE
  - script: STRING default=''
  - width: INT default=768 min=32 max=4096 step=32
  - height: INT default=1344 min=32 max=4096 step=32
  - total_frames: INT default=719 min=39 max=3600 step=17
  - window_frames: INT default=243 min=90 max=480 step=17
  - overlap_frames: INT default=34 min=17 max=170 step=17
  - seed: INT default=0 min=0 max=18446744073709551615
  - steps: INT default=10 min=1 max=100
  - sampler_name: COMBO[euler, euler_cfg_pp, euler_ancestral, euler_ancestral_cfg_pp, heun, heunpp2, exp_heun_2_x0, exp_heun_2_x0_sde, dpm_2, dpm_2_ancestral, ... +35] default='euler'
  - scheduler: COMBO[simple, sgm_uniform, karras, exponential, ddim_uniform, beta, normal, linear_quadratic, kl_optimal] default='simple'
  - activation_reserve_gb: FLOAT default=8.0 min=2.0 max=22.0 step=0.5
- optional:
  - derive_length_from_script: BOOLEAN default=False
- outputs: frames:IMAGE, audio:AUDIO, windows:INT

## H3IntScale
module: custom_nodes.ComfyUI-H3-Multishot | category: H3/episode
- required:
  - value: INT
  - divide_by: FLOAT default=1.5 min=0.1 max=16.0 step=0.05
  - multiple: INT default=32 min=1 max=256
- outputs: value:INT

## H3KeyframeInject
module: custom_nodes.ComfyUI-H3-Multishot | category: model/conditioning/minimax
- required:
  - conditioning: CONDITIONING
  - vae: VAE
  - start_image: IMAGE
  - width: INT default=544 min=32 max=4096 step=32
  - height: INT default=960 min=32 max=4096 step=32
  - length: INT default=362 min=5 max=3600 step=17
- optional:
  - end_image: IMAGE
- outputs: CONDITIONING:CONDITIONING

## H3Keyframes
module: custom_nodes.ComfyUI-H3-Multishot | category: conditioning/video_models
- required:
  - clip: CLIP
  - vae: VAE
  - prompt: STRING default=''
  - width: INT default=960 min=32 max=4096 step=32
  - height: INT default=544 min=32 max=4096 step=32
  - length: INT default=243 min=5 max=3600 step=17
  - positions: STRING default='0%, 50%'
- optional:
  - image_1: IMAGE
  - image_2: IMAGE
  - image_3: IMAGE
  - image_4: IMAGE
  - image_5: IMAGE
  - image_6: IMAGE
  - images_batch: IMAGE
- outputs: positive:CONDITIONING, latent:LATENT, info:STRING

## H3LastFrame
module: custom_nodes.ComfyUI-H3-Multishot | category: image/batch
- required:
  - images: IMAGE
- outputs: IMAGE:IMAGE

## H3LoraInspector
module: custom_nodes.ComfyUI-H3-PowerLoraStack | category: MiniMax-H3/lora
- required:
  - lora_name: COMBO[FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, FC_KIERNAN_h3_face_v1.safetensors, ... +48]
- outputs: info:STRING

## H3LoraSchedule
module: custom_nodes.ComfyUI-H3-PowerLoraStack | category: MiniMax-H3/lora
- required:
  - rows: STRING default='all'
  - start_strength: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - end_strength: FLOAT default=0.1 min=-10.0 max=10.0 step=0.01
  - curve: COMBO[linear, cosine, smoothstep, power, step, explicit]
  - curve_power: FLOAT default=2.0 min=0.01 max=20.0 step=0.05
  - explicit_strengths: STRING default=''
  - start_percent: FLOAT default=0.0 min=0.0 max=100.0 step=1.0
  - end_percent: FLOAT default=100.0 min=0.0 max=100.0 step=1.0
  - domain: COMBO[steps, sigma]
- optional:
  - schedule: H3_SCHEDULE
- outputs: schedule:H3_SCHEDULE, info:STRING

## H3LoraStack
module: custom_nodes.ComfyUI-H3-Multishot | category: loaders/minimax
- required:
  - model: MODEL
  - lora_1: COMBO[None, FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, ... +49] default='None'
  - strength_1: FLOAT default=1.0 min=-2.0 max=2.0 step=0.05
  - lora_2: COMBO[None, FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, ... +49] default='None'
  - strength_2: FLOAT default=1.0 min=-2.0 max=2.0 step=0.05
  - lora_3: COMBO[None, FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, ... +49] default='None'
  - strength_3: FLOAT default=1.0 min=-2.0 max=2.0 step=0.05
  - lora_4: COMBO[None, FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, ... +49] default='None'
  - strength_4: FLOAT default=1.0 min=-2.0 max=2.0 step=0.05
- outputs: model:MODEL

## H3LTXTakeControls
module: custom_nodes.ComfyUI-H3-Multishot | category: H3/episode
- required:
  - width: INT default=960 min=256 max=1920 step=32
  - height: INT default=544 min=256 max=1920 step=32
  - take_seconds: FLOAT default=8.0 min=1.0 max=60.0 step=0.5
  - beat_seconds: FLOAT default=8.0 min=3.0 max=20.0 step=0.5
  - upscale: COMBO[auto, x2, x1.5, none] default='auto'
- optional:
  - vram_gb: FLOAT default=0.0 min=0.0 max=200.0 step=1.0
- outputs: pass1_width:INT, pass1_height:INT, frames:INT, two_pass:BOOLEAN, use_x15:BOOLEAN, beats:INT, beat_frames:INT, summary:STRING

## H3ModelLoaderAny
module: custom_nodes.ComfyUI-H3-Multishot | category: loaders/minimax
- required:
  - model_name: COMBO[10Eros_Max_h3_8stepTURBO_beta7_activation_learned_HQ.safetensors, 10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors, FLUX-KLEIN-9B-FP8-NSFW.safetensors, flux-2-klein-9b-kv-fp8.safetensors]
- optional:
  - activation_reserve_gb: FLOAT default=0.0 min=-1.0 max=128.0 step=0.5
- outputs: MODEL:MODEL

## H3MultishotMemorySampler
module: custom_nodes.ComfyUI-H3-Multishot | category: sampling/minimax
- required:
  - model: MODEL
  - clip: CLIP
  - video_vae: VAE
  - audio_vae: VAE
  - script: STRING default=''
  - shot_count: INT default=0 min=0 max=64
  - width: INT default=768 min=32 max=4096 step=32
  - height: INT default=1344 min=32 max=4096 step=32
  - frames_per_shot: INT default=243 min=5 max=1450 step=17
  - seed: INT default=0 min=0 max=18446744073709551615
  - steps: INT default=20 min=1 max=50
  - seed_per_shot: BOOLEAN default=True
  - memory_frames: INT default=0 min=0 max=3
  - anchor_frames: INT default=1 min=0 max=9
- optional:
  - start_image: IMAGE
  - keyframe_images: IMAGE
  - guide_audio: AUDIO
  - sampler_name: COMBO[euler, euler_cfg_pp, euler_ancestral, euler_ancestral_cfg_pp, heun, heunpp2, exp_heun_2_x0, exp_heun_2_x0_sde, dpm_2, dpm_2_ancestral, ... +35] default='res_multistep'
  - scheduler: COMBO[simple, sgm_uniform, karras, exponential, ddim_uniform, beta, normal, linear_quadratic, kl_optimal] default='simple'
  - bank_pinned: INT default=1 min=0 max=3
  - chain_gain_control: COMBO[off, flatten, match_output, flatten_pin, refresh_pin, level_pin] default='off'
  - continuity: COMBO[cut, seamless, seamless_tail, latent_handoff, first_frame, flf_chain, context_pin] default='cut'
  - bank_clip_frames: INT default=22 min=5 max=124 step=17
  - color_level: COMBO[off, scene, mvgd] default='off'
  - join_anchor_noise: FLOAT default=0.0 min=0.0 max=0.05 step=0.005
  - join_blend: BOOLEAN default=False
  - handoff_release: FLOAT default=0.3 min=0.0 max=1.0 step=0.05
  - bank_ref_noise: FLOAT default=0.0 min=0.0 max=0.05 step=0.005
  - end_anchor: BOOLEAN default=False
  - join_fx: COMBO[off, vhs_glitch] default='off'
  - audio_lock: BOOLEAN default=True
  - handoff_taper: INT default=0 min=0 max=10
  - handoff_depth: COMBO[block, bootstrap] default='block'
  - reference_images: IMAGE
  - voice_ref: AUDIO
  - sampler_override: STRING
  - scheduler_override: STRING
  - self_anchor_voice: BOOLEAN default=False
  - reference_image_size: COMBO[match, max] default='match'
  - preview_first_shot: BOOLEAN default=False
  - output_scale: FLOAT default=1.0 min=1.0 max=4.0 step=0.05
  - sigmas: SIGMAS
  - save_every_shot: BOOLEAN default=False
  - upscale_model_name: COMBO[(none), (H3 latent x2), (H3 latent x1.5), 4x-UltraSharp.pth, 4x-UltraSharp.safetensors, 4x_foolhardy_Remacri.pth] default='(none)'
  - master_normalize: COMBO[off, luma, luma+contrast] default='luma+contrast'
  - pin_frames: COMBO[22, 5, 39, 56] default='22'
  - pin_noise: FLOAT default=0.05 min=0.0 max=0.1 step=0.005
  - pin_renorm: BOOLEAN default=True
  - reference_subjects: STRING default=''
  - reference_video: IMAGE
  - reference_video_audio: AUDIO
  - low_ram_master: BOOLEAN default=False
  - audio_pin_frames: INT default=0 min=0 max=240 step=1
  - pin_noise_audio: BOOLEAN default=False
  - audio_tone_control: BOOLEAN default=False
  - x0_texture_clamp: FLOAT default=0.0 min=0.0 max=0.3 step=0.005
  - refresh_renoise: BOOLEAN default=False
  - pin_noise_ramp: BOOLEAN default=False
  - auto_chunk_ffn: BOOLEAN default=False
  - x0_clamp_window: FLOAT default=0.3 min=0.1 max=0.7 step=0.05
  - sampler_2: STRING default='(off)'
  - sampler_2_at: FLOAT default=0.4 min=0.05 max=0.95 step=0.05
  - voice_ref_2: AUDIO
  - voice_ref_3: AUDIO
- outputs: master_frames:IMAGE, master_audio:AUDIO, shots_rendered:INT, video_latents:LATENT, audio_latents:LATENT, head_frames:INT, master_path:STRING

## H3MultishotSampler
module: custom_nodes.ComfyUI-H3-Multishot | category: sampling/minimax
- required:
  - model: MODEL
  - clip: CLIP
  - video_vae: VAE
  - audio_vae: VAE
  - script: STRING default='Shot 1 prompt goes here.\n---\nShot 2 prompt goes here.\n---\nSh...'
  - shot_count: INT default=0 min=0 max=8
  - width: INT default=768 min=32 max=4096 step=32
  - height: INT default=1344 min=32 max=4096 step=32
  - frames_per_shot: INT default=243 min=5 max=481 step=17
  - seed: INT default=0 min=0 max=18446744073709551615
  - steps: INT default=20 min=1 max=50
  - seed_per_shot: BOOLEAN default=True
- optional:
  - start_image: IMAGE
  - reference_images: IMAGE
  - voice_ref: AUDIO
  - sampler_name: COMBO[euler, euler_cfg_pp, euler_ancestral, euler_ancestral_cfg_pp, heun, heunpp2, exp_heun_2_x0, exp_heun_2_x0_sde, dpm_2, dpm_2_ancestral, ... +35] default='res_multistep'
  - scheduler: COMBO[simple, sgm_uniform, karras, exponential, ddim_uniform, beta, normal, linear_quadratic, kl_optimal] default='simple'
  - sampler_override: STRING
  - scheduler_override: STRING
  - self_anchor_voice: BOOLEAN default=False
  - output_scale: FLOAT default=1.0 min=1.0 max=4.0 step=0.05
  - upscale_model: UPSCALE_MODEL
  - sigmas: SIGMAS
  - save_every_shot: BOOLEAN default=False
  - voice_ref_2: AUDIO
  - voice_ref_3: AUDIO
- outputs: master_frames:IMAGE, master_audio:AUDIO, shots_rendered:INT, first_shot_frames:IMAGE, first_shot_audio:AUDIO

## H3OptionalImage
module: custom_nodes.ComfyUI-H3-Multishot | category: utils/minimax
- required:
  - enabled: BOOLEAN default=True
- optional:
  - image: IMAGE
- outputs: image:IMAGE

## H3PowerLoraStack
module: custom_nodes.ComfyUI-H3-PowerLoraStack | category: MiniMax-H3/lora
- optional:
  - model: MODEL
  - quantized_layers: COMBO[auto, branch, merge] default='auto'
  - adaln_port: COMBO[auto, strip, off] default='auto'
  - adaln_modality: H3_MODALITY
  - schedule: H3_SCHEDULE
- outputs: MODEL:MODEL, report:STRING

## H3QGraftPatch
module: custom_nodes.ComfyUI-H3-Multishot | category: H3/experimental
- required:
  - model: MODEL
  - gains_file: STRING default=''
  - dose: FLOAT default=0.0 min=0.0 max=1.5 step=0.05
- outputs: MODEL:MODEL

## H3RefBatch
module: custom_nodes.ComfyUI-H3-Multishot | category: video/minimax
- required:
  - prompt: STRING
- optional:
  - reference_image: IMAGE
  - picked_path: STRING default=''
- outputs: ref_1:IMAGE, ref_2:IMAGE, ref_3:IMAGE, ref_4:IMAGE, ref_5:IMAGE, ref_6:IMAGE, ref_7:IMAGE, ref_8:IMAGE, ref_9:IMAGE, prompt_out:STRING, report:STRING

## H3ReferenceAudio
module: custom_nodes.ComfyUI-H3-Multishot | category: conditioning/video_models
- required:
  - audio: AUDIO
  - max_seconds: FLOAT default=10.0 min=0.5 max=60.0 step=0.5
- outputs: AUDIO:AUDIO

## H3ReferenceVideo
module: custom_nodes.ComfyUI-H3-Multishot | category: video/minimax
- required:
  - frames: IMAGE
  - start_seconds: FLOAT default=0.0 min=0.0 max=600.0 step=0.5
  - seconds: FLOAT default=3.0 min=0.5 max=20.0 step=0.5
  - source_fps: FLOAT default=24.0 min=1.0 max=120.0 step=1.0
- optional:
  - audio: AUDIO
- outputs: ref_frames:IMAGE, ref_audio:AUDIO, info:STRING

## H3RefFolder
module: custom_nodes.ComfyUI-H3-Multishot | category: loaders/minimax
- required:
  - refs_root: STRING default=''
  - pick: COMBO[first_n, by_seed, newest] default='first_n'
  - seed: INT default=0 min=0 max=18446744073709551615
  - max_refs: INT default=3 min=1 max=9
- optional:
  - character: STRING default=''
- outputs: ref_1:IMAGE, ref_2:IMAGE, ref_3:IMAGE, ref_4:IMAGE, ref_5:IMAGE, ref_6:IMAGE, ref_7:IMAGE, ref_8:IMAGE, ref_9:IMAGE, count:INT, picked:STRING

## H3RemoteTextEncoderClip
module: custom_nodes.ComfyUI-H3-Multishot | category: loaders/minimax
- required:
  - endpoint: STRING default='http://OTHER-PC:8188'
  - clip_name: STRING default='qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors'
  - timeout_seconds: INT default=600 min=30 max=86400
  - clip_type: STRING default='minimax'
- outputs: clip:CLIP

## H3Retake
module: custom_nodes.ComfyUI-H3-Multishot | category: conditioning/minimax
- required:
  - model: MODEL
  - clip: CLIP
  - video_vae: VAE
  - audio_vae: VAE
  - images: IMAGE
  - audio: AUDIO
  - prompt: STRING default=''
  - start_seconds: FLOAT default=0.0 min=0.0 max=600.0 step=0.1
  - end_seconds: FLOAT default=3.0 min=0.1 max=600.0 step=0.1
  - mode: COMBO[video + audio (redo the moment), video only (keep the performance), audio only (keep the picture)] default='video + audio (redo the moment)'
  - seed: INT default=0 min=0 max=18446744073709551615
  - sampler: SAMPLER
  - sigmas: SIGMAS
- outputs: images:IMAGE, audio:AUDIO, info:STRING

## H3SamplerByName
module: custom_nodes.ComfyUI-H3-Multishot | category: video/minimax
- required:
  - sampler_name: STRING
- outputs: SAMPLER:SAMPLER

## H3ScriptSplit
module: custom_nodes.ComfyUI-H3-Multishot | category: conditioning/minimax
- required:
  - script: STRING default='Shot 1 prompt goes here.\n---\nShot 2 prompt goes here.\n---\nSh...'
  - shot_count: INT default=0 min=0 max=3
- outputs: shot_1:STRING, shot_2:STRING, shot_3:STRING, shot_4:STRING, shot_count:INT

## H3SigmasByName
module: custom_nodes.ComfyUI-H3-Multishot | category: video/minimax
- required:
  - model: MODEL
  - scheduler: STRING
  - steps: INT default=12 min=1 max=100
  - denoise: FLOAT default=1.0 min=0.0 max=1.0
- outputs: SIGMAS:SIGMAS

## H3SpeedBoosters
module: custom_nodes.ComfyUI-H3-Multishot | category: video/minimax
- required:
  - model: MODEL
  - spectrum: BOOLEAN default=False
  - teacache: BOOLEAN default=False
  - teacache_strength: FLOAT default=0.15 min=0.0 max=0.5 step=0.01
  - blockcache: BOOLEAN default=False
  - easycache: BOOLEAN default=False
  - blockcache_threshold: FLOAT default=0.12 min=0.0 max=1.0 step=0.01
- outputs: MODEL:MODEL

## H3StudioControls
module: custom_nodes.ComfyUI-H3-Multishot | category: video/minimax
- required:
  - width: INT default=768 min=32 max=4096 step=32
  - height: INT default=1344 min=32 max=4096 step=32
  - frames_per_shot: INT default=362 min=5 max=481 step=17
  - steps: INT default=12 min=1 max=50
  - sampler_name: COMBO[euler, euler_cfg_pp, euler_ancestral, euler_ancestral_cfg_pp, heun, heunpp2, exp_heun_2_x0, exp_heun_2_x0_sde, dpm_2, dpm_2_ancestral, ... +35] default='euler'
  - scheduler: COMBO[simple, sgm_uniform, karras, exponential, ddim_uniform, beta, normal, linear_quadratic, kl_optimal] default='beta'
- optional:
  - shot_count: INT default=0 min=0 max=30
  - use_file_prompts: BOOLEAN default=False
  - take_seconds: FLOAT default=0.0 min=0.0 max=600.0 step=0.5
  - window: COMBO[auto, fit this card (VRAM auto), 243, 226, 209, 192, 175, 158, 141, 124, ... +2] default='auto'
  - model: MODEL
- outputs: width:INT, height:INT, frames_per_shot:INT, steps:INT, sampler_name:STRING, scheduler:STRING, shot_count:INT, use_file_prompts:BOOLEAN

## H3StudioSwitches
module: custom_nodes.ComfyUI-H3-Multishot | category: H3/episode
- required:
  - sol_attn: BOOLEAN default=False
  - chunk_ffn: BOOLEAN default=False
  - remote_encoder: BOOLEAN default=False
- outputs: two_pass (removed):BOOLEAN, sol_attn:BOOLEAN, chunk_ffn:BOOLEAN, spectrum (see Speed Boosters):BOOLEAN, block_cache (see Speed Boosters):BOOLEAN, dual_clock (removed):BOOLEAN, hybrid_cond (removed):BOOLEAN, remote_encoder:BOOLEAN

## H3TAEDecode
module: custom_nodes.ComfyUI-H3-Multishot | category: video/minimax
- required:
  - samples: LATENT
  - tae_name: COMBO[taeh3.safetensors]
- outputs: frames:IMAGE

## HaltExecution
module: custom_nodes.ControlFlowUtils | category: 🐺 VykosX-ControlFlowUtils
- required:
  - disable: BOOLEAN default=False
  - method: BOOLEAN default=False
  - clear_queue: BOOLEAN default=False
  - alert_on_trigger: BOOLEAN default=False
  - input: *
- optional:
  - run_after: *
- outputs: *:*

## HappyHorseImageToVideoApi
module: comfy_api_nodes.nodes_wan | category: partner/video/Wan
- required:
  - model: COMFY_DYNAMICCOMBO_V3
  - first_frame: IMAGE
  - seed: INT default=0 min=0 max=2147483647 step=1
  - watermark: BOOLEAN default=False
- outputs: VIDEO:VIDEO

## HappyHorseReferenceVideoApi
module: comfy_api_nodes.nodes_wan | category: partner/video/Wan
- required:
  - model: COMFY_DYNAMICCOMBO_V3
  - seed: INT default=0 min=0 max=2147483647 step=1
  - watermark: BOOLEAN default=False
- outputs: VIDEO:VIDEO

## HappyHorseTextToVideoApi
module: comfy_api_nodes.nodes_wan | category: partner/video/Wan
- required:
  - model: COMFY_DYNAMICCOMBO_V3
  - seed: INT default=0 min=0 max=2147483647 step=1
  - watermark: BOOLEAN default=False
- outputs: VIDEO:VIDEO

## HappyHorseVideoEditApi
module: comfy_api_nodes.nodes_wan | category: partner/video/Wan
- required:
  - model: COMFY_DYNAMICCOMBO_V3
  - video: VIDEO
  - seed: INT default=0 min=0 max=2147483647 step=1
  - watermark: BOOLEAN default=False
- outputs: VIDEO:VIDEO

## HDRPreviewKJ
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - image: IMAGE
  - exposure: FLOAT default=0.0 min=-10.0 max=10.0 step=0.01
  - saturation: FLOAT default=1.0 min=0.0 max=2.0 step=0.01
- optional:
  - fps: FLOAT default=24.0 min=1.0 max=120.0 step=0.1
  - input_space: COMBO[logc3, linear, srgb] default='logc3'
- outputs: image:IMAGE

## HEDPreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Line Extractors
- required:
  - image: IMAGE
- optional:
  - safe: COMBO[enable, disable] default='enable'
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## HeyGenAvatarVideoNode
module: comfy_api_nodes.nodes_heygen | category: partner/video/HeyGen
- required:
  - engine: COMFY_DYNAMICCOMBO_V3
  - speech: COMFY_DYNAMICCOMBO_V3
- optional:
  - custom_avatar_id: STRING default=''
  - resolution: COMBO[720p, 1080p] default='1080p'
  - aspect_ratio: COMBO[auto, 16:9, 9:16, 1:1, 4:5, 5:4] default='auto'
  - background_color: STRING default=''
  - seed: INT default=42 min=0 max=2147483647
- outputs: VIDEO:VIDEO

## HeyGenCreateAvatarNode
module: comfy_api_nodes.nodes_heygen | category: partner/video/HeyGen
- required:
  - source: COMFY_DYNAMICCOMBO_V3
- outputs: avatar_id:STRING, preview:IMAGE

## HeyGenTalkingPhotoNode
module: comfy_api_nodes.nodes_heygen | category: partner/video/HeyGen
- required:
  - image: IMAGE
  - speech: COMFY_DYNAMICCOMBO_V3
- optional:
  - resolution: COMBO[720p, 1080p] default='1080p'
  - aspect_ratio: COMBO[auto, 16:9, 9:16, 1:1, 4:5, 5:4] default='auto'
  - expressiveness: COMBO[low, medium, high] default='low'
  - seed: INT default=42 min=0 max=2147483647
- outputs: VIDEO:VIDEO

## HeyGenTextToSpeechNode
module: comfy_api_nodes.nodes_heygen | category: partner/audio/HeyGen
- required:
  - text: STRING default=''
  - voice: COMBO[Chill Brian (English, male), Zain (English, female), Narrator Mateo - Excited 🤩 (Spanish, male), Aria (English, female), Caryns (English, female), Klara (English, female), Bold Kasia - Excited 🤩 (Polish, female), Shaun (English, male), Senthil (English, male), Cody (English, male), ... +57]
- optional:
  - custom_voice_id: STRING default=''
  - speed: FLOAT default=1.0 min=0.5 max=2.0 step=0.05
  - ssml: BOOLEAN default=False
  - seed: INT default=42 min=0 max=2147483647
- outputs: AUDIO:AUDIO

## HeyGenVideoTranslateNode
module: comfy_api_nodes.nodes_heygen | category: partner/video/HeyGen
- required:
  - video: VIDEO
  - output_language: COMBO[English, Spanish, Spanish (Spain), Spanish (Mexico), French, French (France), German, German (Germany), Portuguese, Portuguese (Brazil), ... +180]
  - mode: COMBO[speed, precision] default='speed'
- optional:
  - translate_audio_only: BOOLEAN default=False
  - speaker_count: INT default=0 min=0 max=10
  - seed: INT default=42 min=0 max=2147483647
- outputs: VIDEO:VIDEO

## HiDreamO1PatchSeamSmoothing
module: comfy_extras.nodes_hidream_o1 | category: model/patch/hidream
- required:
  - model: MODEL
  - start_percent: FLOAT default=0.8 min=0.0 max=1.0 step=0.01
  - end_percent: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - pattern: COMBO[single_shift, symmetric] default='single_shift'
  - passes: COMBO[2, 4, ramp_2_4, ramp_2_4_8] default='2'
  - blend: COMBO[average, window, median] default='average'
  - strength: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: MODEL:MODEL

## HiDreamO1ReferenceImages
module: comfy_extras.nodes_hidream_o1 | category: model/conditioning/hidream
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
- optional:
  - images: COMFY_AUTOGROW_V3
- outputs: positive:CONDITIONING, negative:CONDITIONING

## HintImageEnchance
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors
- required:
  - hint_image: IMAGE
  - image_gen_width: INT default=512 min=64 max=8192 step=8
  - image_gen_height: INT default=512 min=64 max=8192 step=8
  - resize_mode: COMBO[Just Resize, Crop and Resize, Resize and Fill] default='Just Resize'
- outputs: IMAGE:IMAGE

## HitPawGeneralImageEnhance
module: comfy_api_nodes.nodes_hitpaw | category: partner/image/HitPaw
- required:
  - model: COMBO[generative_portrait, generative]
  - image: IMAGE
  - upscale_factor: COMBO[1, 2, 4]
  - auto_downscale: BOOLEAN default=False
- outputs: IMAGE:IMAGE

## HitPawVideoEnhance
module: comfy_api_nodes.nodes_hitpaw | category: partner/video/HitPaw
- required:
  - model: COMFY_DYNAMICCOMBO_V3
  - video: VIDEO
- outputs: VIDEO:VIDEO

## Hunyuan3Dv2Conditioning
module: comfy_extras.nodes_hunyuan3d | category: model/conditioning/hunyuan 3d
- required:
  - clip_vision_output: CLIP_VISION_OUTPUT
- outputs: positive:CONDITIONING, negative:CONDITIONING

## Hunyuan3Dv2ConditioningMultiView
module: comfy_extras.nodes_hunyuan3d | category: model/conditioning/hunyuan 3d
- optional:
  - front: CLIP_VISION_OUTPUT
  - left: CLIP_VISION_OUTPUT
  - back: CLIP_VISION_OUTPUT
  - right: CLIP_VISION_OUTPUT
- outputs: positive:CONDITIONING, negative:CONDITIONING

## HunyuanImageEditApi
module: comfy_api_nodes.nodes_hunyuan_image | category: partner/image/Tencent
- required:
  - model: COMFY_DYNAMICCOMBO_V3
- outputs: IMAGE:IMAGE

## HunyuanImageTextToImageApi
module: comfy_api_nodes.nodes_hunyuan_image | category: partner/image/Tencent
- required:
  - model: COMFY_DYNAMICCOMBO_V3
- outputs: IMAGE:IMAGE

## HunyuanImageToVideo
module: comfy_extras.nodes_hunyuan | category: model/conditioning/hunyuan video
- required:
  - positive: CONDITIONING
  - vae: VAE
  - width: INT default=848 min=16 max=16384 step=16
  - height: INT default=480 min=16 max=16384 step=16
  - length: INT default=53 min=1 max=16384 step=4
  - batch_size: INT default=1 min=1 max=4096
  - guidance_type: COMBO[v1 (concat), v2 (replace), custom]
- optional:
  - start_image: IMAGE
- outputs: positive:CONDITIONING, latent:LATENT

## HunyuanRefinerLatent
module: comfy_extras.nodes_hunyuan | category: model/conditioning/hunyuan video
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - latent: LATENT
  - noise_augmentation: FLOAT default=0.1 min=0.0 max=1.0 step=0.01
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## HunyuanVideo15ImageToVideo
module: comfy_extras.nodes_hunyuan | category: model/conditioning/hunyuan video
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - width: INT default=848 min=16 max=16384 step=16
  - height: INT default=480 min=16 max=16384 step=16
  - length: INT default=33 min=1 max=16384 step=4
  - batch_size: INT default=1 min=1 max=4096
- optional:
  - start_image: IMAGE
  - clip_vision_output: CLIP_VISION_OUTPUT
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## HunyuanVideo15LatentUpscaleWithModel
module: comfy_extras.nodes_hunyuan | category: model/latent/hunyuan video
- required:
  - model: LATENT_UPSCALE_MODEL
  - samples: LATENT
  - upscale_method: COMBO[nearest-exact, bilinear, area, bicubic, bislerp] default='bilinear'
  - width: INT default=1280 min=0 max=16384 step=8
  - height: INT default=720 min=0 max=16384 step=8
  - crop: COMBO[disabled, center]
- outputs: LATENT:LATENT

## HunyuanVideo15SuperResolution
module: comfy_extras.nodes_hunyuan | category: model/conditioning/hunyuan video
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - latent: LATENT
  - noise_augmentation: FLOAT default=0.7 min=0.0 max=1.0 step=0.01
- optional:
  - vae: VAE
  - start_image: IMAGE
  - clip_vision_output: CLIP_VISION_OUTPUT
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## HunyuanVideoBlockLoraSelect
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/hunyuanvideo
- required:
  - double_blocks.0.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.1.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.2.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.3.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.4.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.5.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.6.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.7.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.8.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.9.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.10.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.11.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.12.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.13.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.14.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.15.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.16.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.17.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.18.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - double_blocks.19.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.0.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.1.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.2.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.3.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.4.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.5.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.6.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.7.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.8.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.9.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.10.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.11.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.12.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.13.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.14.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.15.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.16.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.17.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.18.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.19.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.20.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.21.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.22.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.23.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.24.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.25.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.26.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.27.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.28.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.29.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.30.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.31.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.32.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.33.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.34.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.35.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.36.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.37.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.38.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - single_blocks.39.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
- outputs: blocks:SELECTEDDITBLOCKS

## HunyuanVideoEncodeKeyframesToCond
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/hunyuanvideo
- required:
  - model: MODEL
  - positive: CONDITIONING
  - vae: VAE
  - start_frame: IMAGE
  - end_frame: IMAGE
  - num_frames: INT default=33 min=2 max=4096 step=1
  - tile_size: INT default=512 min=64 max=4096 step=64
  - overlap: INT default=64 min=0 max=4096 step=32
  - temporal_size: INT default=64 min=8 max=4096 step=4
  - temporal_overlap: INT default=8 min=4 max=4096 step=4
- optional:
  - negative: CONDITIONING
- outputs: model:MODEL, positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## HypernetworkLoader
module: comfy_extras.nodes_hypernetwork | category: model/loaders
- required:
  - model: MODEL
  - hypernetwork_name: COMBO[]
  - strength: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
- outputs: MODEL:MODEL

## HyperTile
module: comfy_extras.nodes_hypertile | category: model/patch/unet
- required:
  - model: MODEL
  - tile_size: INT default=256 min=1 max=2048
  - swap_size: INT default=2 min=1 max=128
  - max_depth: INT default=0 min=0 max=10
  - scale_depth: BOOLEAN default=False
- outputs: MODEL:MODEL

## Ideogram4OptimizationsKJ
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/experimental
- required:
  - model: MODEL
  - chunk_ffn: BOOLEAN default=True
  - ffn_chunks: INT default=2 min=1 max=64 step=1
  - ffn_seq_threshold: INT default=1024 min=256 max=65536 step=256
  - bf16_rope: BOOLEAN default=True
- outputs: model:MODEL

## Ideogram4PromptBuilderKJ
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/text
- required:
  - width: INT default=1024 min=64 max=16384 step=16
  - height: INT default=1024 min=64 max=16384 step=16
  - high_level_description: STRING default=''
  - background: STRING default=''
  - style: COMFY_DYNAMICCOMBO_V3
  - aesthetics: STRING default=''
  - lighting: STRING default=''
  - medium: STRING default=''
  - style_palette_data: STRING default=''
  - elements_data: STRING default=''
  - bg_brightness: INT default=25 min=0 max=100
  - import_mode: COMBO[when empty, always] default='when empty'
  - output_format: STRING default='compact'
  - coord_mode: STRING default='normalized'
  - bbox_order: STRING default='yx'
- optional:
  - image: IMAGE
  - import_json: STRING default=''
  - bboxes: BOUNDING_BOX default={'x': 0, 'y': 0, 'width': 512, 'height': 512}
- outputs: prompt:STRING, preview:IMAGE, bboxes:BOUNDING_BOX, width:INT, height:INT

## Ideogram4Scheduler
module: comfy_extras.nodes_ideogram4 | category: model/sampling/schedulers
- required:
  - steps: INT default=20 min=1 max=200
  - width: INT default=1024 min=256 max=8192 step=16
  - height: INT default=1024 min=256 max=8192 step=16
  - mu: FLOAT default=0.0 min=-10.0 max=10.0 step=0.05
  - std: FLOAT default=1.75 min=0.1 max=5.0 step=0.05
- outputs: SIGMAS:SIGMAS

## IdeogramPImage
module: comfy_api_nodes.nodes_ideogram | category: partner/image/Ideogram
- required:
  - prompt: STRING default=''
  - quality: COMBO[VERY_LOW, LOW, MEDIUM, HIGH] default='MEDIUM'
  - resolution: COMBO[1K, 2K] default='1K'
  - aspect_ratio: COMBO[1:3, 3:1, 1:2, 2:1, 9:16, 16:9, 10:16, 16:10, 2:3, 3:2, ... +5] default='1:1'
  - prompt_upsampling: COMBO[AUTO, ON, OFF] default='AUTO'
- optional:
  - seed: INT default=42 min=0 max=2147483647 step=1
- outputs: IMAGE:IMAGE, final_prompt:STRING

## IdeogramV3
module: comfy_api_nodes.nodes_ideogram | category: partner/image/Ideogram
- required:
  - prompt: STRING default=''
- optional:
  - image: IMAGE
  - mask: MASK
  - aspect_ratio: COMBO[1:3, 3:1, 1:2, 2:1, 9:16, 16:9, 10:16, 16:10, 2:3, 3:2, ... +5] default='1:1'
  - resolution: COMBO[Auto, 512x1536, 576x1408, 576x1472, 576x1536, 640x1344, 640x1408, 640x1472, 640x1536, 704x1152, ... +60] default='Auto'
  - magic_prompt_option: COMBO[AUTO, ON, OFF] default='AUTO'
  - seed: INT default=0 min=0 max=2147483647 step=1
  - num_images: INT default=1 min=1 max=8 step=1
  - rendering_speed: COMBO[DEFAULT, TURBO, QUALITY] default='DEFAULT'
  - character_image: IMAGE
  - character_mask: MASK
- outputs: IMAGE:IMAGE

## IdeogramV4
module: comfy_api_nodes.nodes_ideogram | category: partner/image/Ideogram
- required:
  - prompt: STRING default=''
  - resolution: COMBO[Auto, 2048x2048 (1:1), 1440x2880 (1:2), 2880x1440 (2:1), 1664x2496 (2:3), 2496x1664 (3:2), 1792x2240 (4:5), 2240x1792 (5:4), 1440x2560 (9:16), 2560x1440 (16:9), ... +12] default='Auto'
  - rendering_speed: COMBO[DEFAULT, TURBO, QUALITY] default='DEFAULT'
  - seed: INT default=0 min=0 max=2147483647 step=1
- outputs: IMAGE:IMAGE

## IfConditionSelector
module: custom_nodes.ControlFlowUtils | category: 🐺 VykosX-ControlFlowUtils
- required:
  - condition: COMBO[A is TRUE, B is TRUE, A is NONE, B is NONE, A == B, A != B, A > B, A >= B, A < B, A <= B, ... +8]
  - require_inputs: BOOLEAN default=True
  - NOT: BOOLEAN
  - custom_expression: STRING default='2*a == 5*b+2'
- optional:
  - A: *
  - B: *
  - TRUE_IN: *
  - FALSE_IN: *
- outputs: *:*

## Image Comparer (rgthree)
module: custom_nodes.rgthree-comfy | category: rgthree
- optional:
  - image_a: IMAGE
  - image_b: IMAGE
- outputs: images:IMAGE

## Image Inset Crop (rgthree)
module: custom_nodes.rgthree-comfy | category: rgthree
- required:
  - image: IMAGE
  - measurement: COMBO[Pixels, Percentage]
  - left: INT default=0 min=0 max=16384 step=8
  - right: INT default=0 min=0 max=16384 step=8
  - top: INT default=0 min=0 max=16384 step=8
  - bottom: INT default=0 min=0 max=16384 step=8
- outputs: IMAGE:IMAGE

## Image or Latent Size (rgthree)
module: custom_nodes.rgthree-comfy | category: rgthree
- outputs: WIDTH:INT, HEIGHT:INT

## Image Resize (rgthree)
module: custom_nodes.rgthree-comfy | category: rgthree
- required:
  - image: IMAGE
  - measurement: COMBO[pixels, percentage]
  - width: INT default=0 min=0 max=16384 step=1
  - height: INT default=0 min=0 max=16384 step=1
  - fit: COMBO[crop, pad, contain]
  - method: COMBO[nearest-exact, bilinear, area, bicubic, lanczos]
- outputs: IMAGE:IMAGE, WIDTH:INT, HEIGHT:INT

## ImageAddMulti
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - inputcount: INT default=2 min=2 max=1000 step=1
  - image_1: IMAGE
  - image_2: IMAGE
  - blending: COMBO[add, subtract, multiply, difference] default='add'
  - blend_amount: FLOAT default=0.5 min=0 max=1 step=0.01
- outputs: images:IMAGE

## ImageAddNoise
module: comfy_extras.nodes_images | category: image/filters
- required:
  - image: IMAGE
  - seed: INT default=0 min=0 max=18446744073709551615
  - strength: FLOAT default=0.5 min=0.0 max=1.0 step=0.01
- outputs: IMAGE:IMAGE

## ImageAndMaskPreview
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking
- required:
  - mask_opacity: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - mask_color: STRING default='255, 255, 255'
  - pass_through: BOOLEAN default=False
- optional:
  - image: IMAGE
  - mask: MASK
- outputs: composite:IMAGE

## ImageApplyLUT+
module: custom_nodes.ComfyUI_essentials | category: essentials/image processing
- required:
  - image: IMAGE
  - lut_file: COMBO[put_luts_files_here.txt]
  - gamma_correction: BOOLEAN default=True
  - clip_values: BOOLEAN default=True
  - strength: FLOAT default=1.0 min=0.0 max=1.0 step=0.1
- outputs: IMAGE:IMAGE

## ImageBatch
module: nodes | category: image/batch
- required:
  - image1: IMAGE
  - image2: IMAGE
- outputs: IMAGE:IMAGE

## ImageBatchExtendWithOverlap
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - source_images: IMAGE
  - overlap: INT default=13 min=1 max=4096 step=1
  - overlap_side: COMBO[source, new_images] default='source'
  - overlap_mode: COMBO[cut, linear_blend, ease_in_out, filmic_crossfade, perceptual_crossfade] default='linear_blend'
- optional:
  - new_images: IMAGE
- outputs: source_images:IMAGE, start_images:IMAGE, extended_images:IMAGE

## ImageBatchFilter
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - images: IMAGE
  - empty_color: STRING default='0, 0, 0'
  - empty_threshold: FLOAT default=0.01 min=0.0 max=1.0 step=0.01
- optional:
  - replacement_image: IMAGE
- outputs: images:IMAGE, removed_indices:STRING

## ImageBatchJoinWithTransition
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - images_1: IMAGE
  - images_2: IMAGE
  - start_index: INT default=0 min=-10000 max=10000 step=1
  - interpolation: COMBO[linear, ease_in, ease_out, ease_in_out, bounce, elastic, glitchy, exponential_ease_out]
  - transition_type: COMBO[horizontal slide, vertical slide, box, circle, horizontal door, vertical door, fade]
  - transitioning_frames: INT default=1 min=1 max=4096 step=1
  - blur_radius: FLOAT default=0.0 min=0.0 max=100.0 step=0.1
  - reverse: BOOLEAN default=False
  - device: COMBO[CPU, GPU] default='CPU'
- outputs: IMAGE:IMAGE

## ImageBatchMulti
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - inputcount: INT default=2 min=2 max=1000 step=1
  - image_1: IMAGE
- optional:
  - image_2: IMAGE
- outputs: images:IMAGE

## ImageBatchMultiple+
module: custom_nodes.ComfyUI_essentials | category: essentials/image batch
- required:
  - image_1: IMAGE
  - method: COMBO[nearest-exact, bilinear, area, bicubic, lanczos] default='lanczos'
- optional:
  - image_2: IMAGE
  - image_3: IMAGE
  - image_4: IMAGE
  - image_5: IMAGE
- outputs: IMAGE:IMAGE

## ImageBatchRepeatInterleaving
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - images: IMAGE
  - repeats: INT default=1 min=1 max=4096
- optional:
  - mask: MASK
- outputs: IMAGE:IMAGE, MASK:MASK

## ImageBatchTestPattern
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/text
- required:
  - batch_size: INT default=1 min=1 max=4096 step=1
  - start_from: INT default=0 min=0 max=4096 step=1
  - text_x: INT default=256 min=0 max=4096 step=1
  - text_y: INT default=256 min=0 max=4096 step=1
  - width: INT default=512 min=16 max=4096 step=1
  - height: INT default=512 min=16 max=4096 step=1
  - font: COMBO[FreeMono.ttf, FreeMonoBoldOblique.otf, TTNorms-Black.otf]
  - font_size: INT default=255 min=8 max=4096 step=1
- outputs: image:IMAGE

## ImageBatchToList+
module: custom_nodes.ComfyUI_essentials | category: essentials/image batch
- required:
  - image: IMAGE
- outputs: IMAGE:IMAGE

## ImageBlend
module: comfy_extras.nodes_post_processing | category: image/filters
- required:
  - image1: IMAGE
  - image2: IMAGE
  - blend_factor: FLOAT default=0.5 min=0.0 max=1.0 step=0.01
  - blend_mode: COMBO[normal, multiply, screen, overlay, soft_light, difference]
- outputs: IMAGE:IMAGE

## ImageBlur
module: comfy_extras.nodes_post_processing | category: image/filters
- required:
  - image: IMAGE
  - blur_radius: INT default=1 min=1 max=31 step=1
  - sigma: FLOAT default=1.0 min=0.1 max=10.0 step=0.1
- outputs: IMAGE:IMAGE

## ImageCASharpening+
module: custom_nodes.ComfyUI_essentials | category: essentials/image processing
- required:
  - image: IMAGE
  - amount: FLOAT default=0.8 min=0 max=1 step=0.05
- outputs: IMAGE:IMAGE

## ImageColorMatch+
module: custom_nodes.ComfyUI_essentials | category: essentials/image processing
- required:
  - image: IMAGE
  - reference: IMAGE
  - color_space: COMBO[LAB, YCbCr, RGB, LUV, YUV, XYZ]
  - factor: FLOAT default=1.0 min=0.0 max=1.0 step=0.05
  - device: COMBO[auto, cpu, gpu]
  - batch_size: INT default=0 min=0 max=1024 step=1
- optional:
  - reference_mask: MASK
- outputs: IMAGE:IMAGE

## ImageColorMatchAdobe+
module: custom_nodes.ComfyUI_essentials | category: essentials/image processing
- required:
  - image: IMAGE
  - reference: IMAGE
  - color_space: COMBO[RGB, LAB]
  - luminance_factor: FLOAT default=1.0 min=0.0 max=2.0 step=0.05
  - color_intensity_factor: FLOAT default=1.0 min=0.0 max=2.0 step=0.05
  - fade_factor: FLOAT default=1.0 min=0.0 max=1.0 step=0.05
  - neutralization_factor: FLOAT default=0.0 min=0.0 max=1.0 step=0.05
  - device: COMBO[auto, cpu, gpu]
- optional:
  - reference_mask: MASK
- outputs: IMAGE:IMAGE

## ImageColorSpace
module: comfy_extras.nodes_images | category: image/color
- required:
  - image: IMAGE
  - source: COMBO[sRGB, HDR, HDR PQ, linear, HDR LogC3, HDR ACEScct] default='sRGB'
  - destination: COMBO[sRGB, HDR, HDR PQ, linear, HDR LogC3, HDR ACEScct] default='sRGB'
- outputs: IMAGE:IMAGE

## ImageColorToMask
module: comfy_extras.nodes_mask | category: image/mask
- required:
  - image: IMAGE
  - color: INT default=0 min=0 max=16777215 step=1
- outputs: MASK:MASK

## ImageCompare
module: comfy_extras.nodes_image_compare | category: image
- required:
  - compare_view: IMAGECOMPARE
- optional:
  - image_a: IMAGE
  - image_b: IMAGE
- outputs: 

## ImageComposite+
module: custom_nodes.ComfyUI_essentials | category: essentials/image manipulation
- required:
  - destination: IMAGE
  - source: IMAGE
  - x: INT default=0 min=-16384 max=16384 step=1
  - y: INT default=0 min=-16384 max=16384 step=1
  - offset_x: INT default=0 min=-16384 max=16384 step=1
  - offset_y: INT default=0 min=-16384 max=16384 step=1
- optional:
  - mask: MASK
- outputs: IMAGE:IMAGE

## ImageCompositeFromMaskBatch+
module: custom_nodes.ComfyUI_essentials | category: essentials/image manipulation
- required:
  - image_from: IMAGE
  - image_to: IMAGE
  - mask: MASK
- outputs: IMAGE:IMAGE

## ImageCompositeMasked
module: comfy_extras.nodes_mask | category: image/compositing
- required:
  - destination: IMAGE
  - source: IMAGE
  - x: INT default=0 min=0 max=16384 step=1
  - y: INT default=0 min=0 max=16384 step=1
  - resize_source: BOOLEAN default=False
- optional:
  - mask: MASK
- outputs: IMAGE:IMAGE

## ImageCompositor
module: comfy_extras.nodes_compositor | category: image
- required:
  - layers: LAYERS
  - compositor: COMPOSITOR default={}
- outputs: IMAGE:IMAGE, MASK:MASK

## ImageConcanate
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - image1: COMFY_MATCHTYPE_V3
  - image2: IMAGE,MASK
  - direction: COMBO[right, down, left, up] default='right'
  - match_image_size: BOOLEAN default=True
- outputs: output:COMFY_MATCHTYPE_V3

## ImageConcatFromBatch
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - images: IMAGE
  - num_columns: INT default=3 min=1 max=255 step=1
  - match_image_size: BOOLEAN default=False
  - max_resolution: INT default=4096
- outputs: IMAGE:IMAGE

## ImageConcatMulti
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - inputcount: INT default=2 min=2 max=1000 step=1
  - image_1: COMFY_MATCHTYPE_V3
  - direction: COMBO[right, down, left, up] default='right'
  - match_image_size: BOOLEAN default=False
- optional:
  - image_2: IMAGE,MASK
- outputs: output:COMFY_MATCHTYPE_V3

## ImageCrop
module: comfy_extras.nodes_images | category: image/transform
- required:
  - image: IMAGE
  - width: INT default=512 min=1 max=16384 step=1
  - height: INT default=512 min=1 max=16384 step=1
  - x: INT default=0 min=0 max=16384 step=1
  - y: INT default=0 min=0 max=16384 step=1
- outputs: IMAGE:IMAGE

## ImageCrop+
module: custom_nodes.ComfyUI_essentials | category: essentials/image manipulation
- required:
  - image: IMAGE
  - width: INT default=256 min=0 max=16384 step=8
  - height: INT default=256 min=0 max=16384 step=8
  - position: COMBO[top-left, top-center, top-right, right-center, bottom-right, bottom-center, bottom-left, left-center, center]
  - x_offset: INT default=0 min=-99999 step=1
  - y_offset: INT default=0 min=-99999 step=1
- outputs: IMAGE:IMAGE, x:INT, y:INT

## ImageCropByMask
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - image: IMAGE
  - mask: MASK
- outputs: image:IMAGE

## ImageCropByMaskAndResize
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - image: IMAGE
  - mask: MASK
  - base_resolution: INT default=512 min=0 max=16384 step=8
  - padding: INT default=0 min=0 max=16384 step=1
  - min_crop_resolution: INT default=128 min=0 max=16384 step=8
  - max_crop_resolution: INT default=512 min=0 max=16384 step=8
- outputs: images:IMAGE, masks:MASK, bbox:BBOX

## ImageCropByMaskBatch
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - image: IMAGE
  - masks: MASK
  - width: INT default=512 min=0 max=16384 step=8
  - height: INT default=512 min=0 max=16384 step=8
  - padding: INT default=0 min=0 max=4096 step=1
  - preserve_size: BOOLEAN default=False
  - bg_color: STRING default='0, 0, 0'
- outputs: images:IMAGE, masks:MASK

## ImageCropToMask
module: comfy_extras.nodes_images | category: image/transform
- required:
  - images: IMAGE
  - masks: MASK
  - width: INT default=1024 min=64 max=4096 step=8
  - height: INT default=1024 min=64 max=4096 step=8
  - pad_factor: FLOAT default=1.0 min=1.0 max=2.0 step=0.01
  - grow_mask: INT default=0 min=-32 max=32 step=1
  - background: COLOR default='#000000'
- outputs: images:IMAGE

## ImageCropV2
module: comfy_extras.nodes_images | category: image/transform
- required:
  - image: IMAGE
  - crop_region: BOUNDING_BOX default={'x': 0, 'y': 0, 'width': 512, 'height': 512}
- outputs: IMAGE:IMAGE

## ImageDeduplication
module: comfy_extras.nodes_dataset | category: image/batch
- required:
  - images: IMAGE
  - similarity_threshold: FLOAT default=0.95 min=0.0 max=1.0
- outputs: images:IMAGE

## ImageDesaturate+
module: custom_nodes.ComfyUI_essentials | category: essentials/image processing
- required:
  - image: IMAGE
  - factor: FLOAT default=1.0 min=0.0 max=1.0 step=0.05
  - method: COMBO[luminance (Rec.709), luminance (Rec.601), average, lightness]
- outputs: IMAGE:IMAGE

## ImageEnhanceDifference+
module: custom_nodes.ComfyUI_essentials | category: essentials/image analysis
- required:
  - image1: IMAGE
  - image2: IMAGE
  - exponent: FLOAT default=0.75 min=0.0 max=1.0 step=0.05
- outputs: IMAGE:IMAGE

## ImageExpandBatch+
module: custom_nodes.ComfyUI_essentials | category: essentials/image batch
- required:
  - image: IMAGE
  - size: INT default=16 min=1 step=1
  - method: COMBO[expand, repeat all, repeat first, repeat last]
- outputs: IMAGE:IMAGE

## ImageFlip
module: comfy_extras.nodes_images | category: image/transform
- required:
  - image: IMAGE
  - flip_method: COMBO[x-axis: vertically, y-axis: horizontally]
- outputs: IMAGE:IMAGE

## ImageFlip+
module: custom_nodes.ComfyUI_essentials | category: essentials/image manipulation
- required:
  - image: IMAGE
  - axis: COMBO[x, y, xy]
- outputs: IMAGE:IMAGE

## ImageFromBatch
module: comfy_extras.nodes_images | category: image/batch
- required:
  - image: IMAGE
  - batch_index: INT default=0 min=-16384 max=16384
  - length: INT default=1 min=1 max=4096
- outputs: IMAGE:IMAGE

## ImageFromBatch+
module: custom_nodes.ComfyUI_essentials | category: essentials/image batch
- required:
  - image: IMAGE
  - start: INT default=0 min=0 step=1
  - length: INT default=-1 min=-1 step=1
- outputs: IMAGE:IMAGE

## ImageGenResolutionFromImage
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors
- required:
  - image: IMAGE
- outputs: IMAGE_GEN_WIDTH (INT):INT, IMAGE_GEN_HEIGHT (INT):INT

## ImageGenResolutionFromLatent
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors
- required:
  - latent: LATENT
- outputs: IMAGE_GEN_WIDTH (INT):INT, IMAGE_GEN_HEIGHT (INT):INT

## ImageGrabPIL
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - x: INT default=0 min=0 max=4096 step=1
  - y: INT default=0 min=0 max=4096 step=1
  - width: INT default=512 min=0 max=4096 step=1
  - height: INT default=512 min=0 max=4096 step=1
  - num_frames: INT default=1 min=1 max=255 step=1
  - delay: FLOAT default=0.1 min=0.0 max=10.0 step=0.01
- outputs: image:IMAGE

## ImageGrid
module: comfy_extras.nodes_dataset | category: image/batch
- required:
  - images: IMAGE
  - columns: INT default=4 min=1 max=20
  - cell_width: INT default=256 min=32 max=2048
  - cell_height: INT default=256 min=32 max=2048
  - padding: INT default=4 min=0 max=50
- outputs: images:IMAGE

## ImageGridComposite2x2
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - image1: IMAGE
  - image2: IMAGE
  - image3: IMAGE
  - image4: IMAGE
- outputs: IMAGE:IMAGE

## ImageGridComposite3x3
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - image1: IMAGE
  - image2: IMAGE
  - image3: IMAGE
  - image4: IMAGE
  - image5: IMAGE
  - image6: IMAGE
  - image7: IMAGE
  - image8: IMAGE
  - image9: IMAGE
- outputs: IMAGE:IMAGE

## ImageGridtoBatch
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - image: IMAGE
  - columns: INT default=3 min=1 max=8
  - rows: INT default=0 min=1 max=8
- outputs: IMAGE:IMAGE

## ImageHistogram
module: comfy_extras.nodes_curve | category: utilities
- required:
  - image: IMAGE
- outputs: rgb:HISTOGRAM, luminance:HISTOGRAM, red:HISTOGRAM, green:HISTOGRAM, blue:HISTOGRAM

## ImageHistogramMatch+
module: custom_nodes.ComfyUI_essentials | category: essentials/image processing
- required:
  - image: IMAGE
  - reference: IMAGE
  - method: COMBO[pytorch, skimage]
  - factor: FLOAT default=1.0 min=0.0 max=1.0 step=0.05
  - device: COMBO[auto, cpu, gpu]
- outputs: IMAGE:IMAGE

## ImageIntensityDetector
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Recolor
- required:
  - image: IMAGE
- optional:
  - gamma_correction: FLOAT default=1.0 min=0.1 max=2.0 step=0.01
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## ImageInvert
module: nodes | category: image/color
- required:
  - image: IMAGE
- outputs: IMAGE:IMAGE

## ImageListToBatch+
module: custom_nodes.ComfyUI_essentials | category: essentials/image batch
- required:
  - image: IMAGE
- outputs: IMAGE:IMAGE

## ImageLuminanceDetector
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Recolor
- required:
  - image: IMAGE
- optional:
  - gamma_correction: FLOAT default=1.0 min=0.1 max=2.0 step=0.01
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## ImageMergeTileList
module: comfy_extras.nodes_images | category: image/batch
- required:
  - image_list: IMAGE
  - final_width: INT default=1024 min=64 max=32768
  - final_height: INT default=1024 min=64 max=32768
  - overlap: INT default=128 min=0 max=4096
- outputs: IMAGE:IMAGE

## ImageNoiseAugmentation
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - image: IMAGE
  - noise_aug_strength: FLOAT default=None min=0.0 max=100.0 step=0.001
  - seed: INT default=123 min=0 max=18446744073709551615 step=1
- outputs: IMAGE:IMAGE

## ImageNormalize_Neg1_To_1
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - images: IMAGE
- outputs: IMAGE:IMAGE

## ImageOnlyCheckpointLoader
module: comfy_extras.nodes_video_model | category: model/loaders
- required:
  - ckpt_name: COMBO[]
- outputs: MODEL:MODEL, CLIP_VISION:CLIP_VISION, VAE:VAE

## ImageOnlyCheckpointSave
module: comfy_extras.nodes_video_model | category: model/merging
- required:
  - model: MODEL
  - clip_vision: CLIP_VISION
  - vae: VAE
  - filename_prefix: STRING default='checkpoints/ComfyUI'
- outputs: 

## ImagePadForOutpaint
module: nodes | category: image/transform
- required:
  - image: IMAGE
  - left: INT default=0 min=0 max=16384 step=8
  - top: INT default=0 min=0 max=16384 step=8
  - right: INT default=0 min=0 max=16384 step=8
  - bottom: INT default=0 min=0 max=16384 step=8
  - feathering: INT default=40 min=0 max=16384 step=1
- outputs: IMAGE:IMAGE, MASK:MASK

## ImagePadForOutpaintMasked
module: custom_nodes.ComfyUI-KJNodes | category: image
- required:
  - image: IMAGE
  - left: INT default=0 min=0 max=16384 step=8
  - top: INT default=0 min=0 max=16384 step=8
  - right: INT default=0 min=0 max=16384 step=8
  - bottom: INT default=0 min=0 max=16384 step=8
  - feathering: INT default=0 min=0 max=16384 step=1
- optional:
  - mask: MASK
- outputs: IMAGE:IMAGE, MASK:MASK

## ImagePadForOutpaintTargetSize
module: custom_nodes.ComfyUI-KJNodes | category: image
- required:
  - image: IMAGE
  - target_width: INT default=0 min=0 max=16384 step=8
  - target_height: INT default=0 min=0 max=16384 step=8
  - feathering: INT default=0 min=0 max=16384 step=1
  - upscale_method: COMBO[nearest-exact, bilinear, area, bicubic, lanczos]
- optional:
  - mask: MASK
- outputs: IMAGE:IMAGE, MASK:MASK

## ImagePadKJ
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - image: IMAGE
  - left: INT default=0 min=0 max=16384 step=1
  - right: INT default=0 min=0 max=16384 step=1
  - top: INT default=0 min=0 max=16384 step=1
  - bottom: INT default=0 min=0 max=16384 step=1
  - extra_padding: INT default=0 min=0 max=16384 step=1
  - pad_mode: COMBO[edge, edge_pixel, color, pillarbox_blur]
  - color: STRING default='0, 0, 0'
- optional:
  - mask: MASK
  - target_width: INT default=512 min=0 max=16384 step=1
  - target_height: INT default=512 min=0 max=16384 step=1
- outputs: images:IMAGE, masks:MASK

## ImagePass
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- optional:
  - image: IMAGE
- outputs: IMAGE:IMAGE

## ImagePosterize+
module: custom_nodes.ComfyUI_essentials | category: essentials/image processing
- required:
  - image: IMAGE
  - threshold: FLOAT default=0.5 min=0.0 max=1.0 step=0.05
- outputs: IMAGE:IMAGE

## ImagePrepForICLora
module: custom_nodes.ComfyUI-KJNodes | category: image
- required:
  - reference_image: IMAGE
  - output_width: INT default=1024 min=1 max=4096 step=1
  - output_height: INT default=1024 min=1 max=4096 step=1
  - border_width: INT default=0 min=0 max=4096 step=1
- optional:
  - latent_image: IMAGE
  - latent_mask: MASK
  - reference_mask: MASK
- outputs: IMAGE:IMAGE, MASK:MASK

## ImagePreviewFromLatent+
module: custom_nodes.ComfyUI_essentials | category: essentials/image utils
- required:
  - latent: LATENT
  - vae: VAE
  - tile_size: INT default=0 min=0 max=4096 step=64
- optional:
  - image: COMBO[none]
- outputs: IMAGE:IMAGE, MASK:MASK, width:INT, height:INT

## ImageQuantize
module: comfy_extras.nodes_post_processing | category: image/filters
- required:
  - image: IMAGE
  - colors: INT default=256 min=1 max=256 step=1
  - dither: COMBO[none, floyd-steinberg, bayer-2, bayer-4, bayer-8, bayer-16]
- outputs: IMAGE:IMAGE

## ImageRandomTransform+
module: custom_nodes.ComfyUI_essentials | category: essentials/image manipulation
- required:
  - image: IMAGE
  - seed: INT default=0 min=0 max=18446744073709551615
  - repeat: INT default=1 min=1 max=256 step=1
  - variation: FLOAT default=0.1 min=0.0 max=1.0 step=0.05
- outputs: IMAGE:IMAGE

## ImageRemoveAlpha+
module: custom_nodes.ComfyUI_essentials | category: essentials/image utils
- required:
  - image: IMAGE
- outputs: IMAGE:IMAGE

## ImageRemoveBackground+
module: custom_nodes.ComfyUI_essentials | category: essentials/image manipulation
- required:
  - rembg_session: REMBG_SESSION
  - image: IMAGE
- outputs: IMAGE:IMAGE, MASK:MASK

## ImageResize+
module: custom_nodes.ComfyUI_essentials | category: essentials/image manipulation
- required:
  - image: IMAGE
  - width: INT default=512 min=0 max=16384 step=1
  - height: INT default=512 min=0 max=16384 step=1
  - interpolation: COMBO[nearest, bilinear, bicubic, area, nearest-exact, lanczos]
  - method: COMBO[stretch, keep proportion, fill / crop, pad]
  - condition: COMBO[always, downscale if bigger, upscale if smaller, if bigger area, if smaller area]
  - multiple_of: INT default=0 min=0 max=512 step=1
- outputs: IMAGE:IMAGE, width:INT, height:INT

## ImageResizeKJ
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - image: IMAGE
  - width: INT default=512 min=0 max=16384 step=1
  - height: INT default=512 min=0 max=16384 step=1
  - upscale_method: COMBO[nearest-exact, bilinear, area, bicubic, lanczos]
  - keep_proportion: BOOLEAN default=False
  - divisible_by: INT default=2 min=0 max=512 step=1
- optional:
  - get_image_size: IMAGE
  - crop: COMBO[disabled, center, 0]
- outputs: IMAGE:IMAGE, width:INT, height:INT

## ImageResizeKJv2
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - image: IMAGE
  - width: INT default=512 min=0 max=16384 step=1
  - height: INT default=512 min=0 max=16384 step=1
  - upscale_method: COMBO[nearest-exact, bilinear, area, bicubic, lanczos, nvidia_rtx_vsr]
  - keep_proportion: COMBO[stretch, resize, pad, pad_edge, pad_edge_pixel, crop, pillarbox_blur, total_pixels] default=False
  - pad_color: STRING default='0, 0, 0'
  - crop_position: COMBO[center, top, bottom, left, right] default='center'
  - divisible_by: INT default=2 min=0 max=512 step=1
- optional:
  - mask: MASK
  - device: COMBO[cpu, gpu]
- outputs: IMAGE:IMAGE, width:INT, height:INT, mask:MASK

## ImageResolutionAdjust
module: custom_nodes.ControlFlowUtils | category: 🐺 VykosX-ControlFlowUtils
- required:
  - source_width: INT default=512 min=16 max=8192 step=8
  - source_height: INT default=512 min=16 max=8192 step=8
  - scaling_factor: FLOAT default=1.0 min=0.1 max=10 step=0.1
  - target_width: INT default=512 min=16 max=8192 step=8
  - target_height: INT default=512 min=16 max=8192 step=8
  - tolerance: INT default=32 min=16 max=1024
- outputs: Adj. Width:INT, Adj. Height:INT, Result:STRING

## ImageRGBToYUV
module: comfy_extras.nodes_morphology | category: image/color
- required:
  - image: IMAGE
- outputs: Y:IMAGE, U:IMAGE, V:IMAGE

## ImageRotate
module: comfy_extras.nodes_images | category: image/transform
- required:
  - image: IMAGE
  - rotation: COMBO[none, 90 degrees, 180 degrees, 270 degrees]
- outputs: IMAGE:IMAGE

## ImageScale
module: nodes | category: image/upscaling
- required:
  - image: IMAGE
  - upscale_method: COMBO[nearest-exact, bilinear, area, bicubic, lanczos]
  - width: INT default=512 min=0 max=16384 step=1
  - height: INT default=512 min=0 max=16384 step=1
  - crop: COMBO[disabled, center]
- outputs: IMAGE:IMAGE

## ImageScaleBy
module: nodes | category: image/upscaling
- required:
  - image: IMAGE
  - upscale_method: COMBO[nearest-exact, bilinear, area, bicubic, lanczos]
  - scale_by: FLOAT default=1.0 min=0.01 max=8.0 step=0.01
- outputs: IMAGE:IMAGE

## ImageScaleToMaxDimension
module: comfy_extras.nodes_images | category: image/upscaling
- required:
  - image: IMAGE
  - upscale_method: COMBO[area, lanczos, bilinear, nearest-exact, bilinear, bicubic]
  - largest_size: INT default=512 min=0 max=16384 step=1
- outputs: IMAGE:IMAGE

## ImageScaleToTotalPixels
module: comfy_extras.nodes_post_processing | category: image/upscaling
- required:
  - image: IMAGE
  - upscale_method: COMBO[nearest-exact, bilinear, area, bicubic, lanczos]
  - megapixels: FLOAT default=1.0 min=0.01 max=16.0 step=0.01
  - resolution_steps: INT default=1 min=1 max=256
- outputs: IMAGE:IMAGE

## ImageSeamCarving+
module: custom_nodes.ComfyUI_essentials | category: essentials/image manipulation
- required:
  - image: IMAGE
  - width: INT default=512 min=1 max=16384 step=1
  - height: INT default=512 min=1 max=16384 step=1
  - energy: COMBO[backward, forward]
  - order: COMBO[width-first, height-first]
- optional:
  - keep_mask: MASK
  - drop_mask: MASK
- outputs: IMAGE:IMAGE

## ImageSharpen
module: comfy_extras.nodes_post_processing | category: image/filters
- required:
  - image: IMAGE
  - sharpen_radius: INT default=1 min=1 max=31 step=1
  - sigma: FLOAT default=1.0 min=0.1 max=10.0 step=0.01
  - alpha: FLOAT default=1.0 min=0.0 max=5.0 step=0.01
- outputs: IMAGE:IMAGE

## ImageSharpenKJ
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - image: COMFY_MATCHTYPE_V3
  - method: COMFY_DYNAMICCOMBO_V3
- outputs: output:COMFY_MATCHTYPE_V3

## ImageSmartSharpen+
module: custom_nodes.ComfyUI_essentials | category: essentials/image processing
- required:
  - image: IMAGE
  - noise_radius: INT default=7 min=1 max=25 step=1
  - preserve_edges: FLOAT default=0.75 min=0.0 max=1.0 step=0.05
  - sharpen: FLOAT default=5.0 min=0.0 max=25.0 step=0.5
  - ratio: FLOAT default=0.5 min=0.0 max=1.0 step=0.1
- outputs: IMAGE:IMAGE

## ImageStitch
module: comfy_extras.nodes_images | category: image/transform
- required:
  - image1: IMAGE
  - direction: COMBO[right, down, left, up] default='right'
  - match_image_size: BOOLEAN default=True
  - spacing_width: INT default=0 min=0 max=1024 step=2
  - spacing_color: COMBO[white, black, red, green, blue] default='white'
- optional:
  - image2: IMAGE
- outputs: IMAGE:IMAGE

## ImageTensorList
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - image1: IMAGE
  - image2: IMAGE
- outputs: IMAGE:IMAGE

## ImageTile+
module: custom_nodes.ComfyUI_essentials | category: essentials/image manipulation
- required:
  - image: IMAGE
  - rows: INT default=2 min=1 max=256 step=1
  - cols: INT default=2 min=1 max=256 step=1
  - overlap: FLOAT default=0 min=0 max=0.5 step=0.01
  - overlap_x: INT default=0 min=0 max=8192 step=1
  - overlap_y: INT default=0 min=0 max=8192 step=1
- outputs: IMAGE:IMAGE, tile_width:INT, tile_height:INT, overlap_x:INT, overlap_y:INT

## ImageToDevice+
module: custom_nodes.ComfyUI_essentials | category: essentials/image utils
- required:
  - image: IMAGE
  - device: COMBO[auto, cpu, gpu]
- outputs: IMAGE:IMAGE

## ImageToMask
module: comfy_extras.nodes_mask | category: image/mask
- required:
  - image: IMAGE
  - channel: COMBO[red, green, blue, alpha]
- outputs: MASK:MASK

## ImageTransformByNormalizedAmplitude
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/audio
- required:
  - normalized_amp: NORMALIZED_AMPLITUDE
  - zoom_scale: FLOAT default=0.0 min=-1.0 max=1.0 step=0.001
  - x_offset: INT default=0 min=-16383 max=16384 step=1
  - y_offset: INT default=0 min=-16383 max=16384 step=1
  - cumulative: BOOLEAN default=False
  - image: IMAGE
- outputs: IMAGE:IMAGE

## ImageTransformKJ
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - image: COMFY_MATCHTYPE_V3
  - target_width: INT default=0 min=0 max=16384 step=1
  - target_height: INT default=0 min=0 max=16384 step=1
  - upscale_method: COMBO[nearest-exact, bilinear, area, bicubic, lanczos] default='lanczos'
  - keep_proportion: COMFY_DYNAMICCOMBO_V3
  - divisible_by: INT default=2 min=0 max=512 step=1
  - extra_padding: COMFY_DYNAMICCOMBO_V3
  - invert_crop: COMFY_DYNAMICCOMBO_V3
  - bboxes: STRING default=''
- optional:
  - mask: MASK
- outputs: output:COMFY_MATCHTYPE_V3, output_mask:MASK, bbox:BBOX, bbox_mask:MASK, width:INT, height:INT

## ImageUncropByMask
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - destination: IMAGE
  - source: IMAGE
  - mask: MASK
  - bbox: BBOX
- outputs: image:IMAGE

## ImageUntile+
module: custom_nodes.ComfyUI_essentials | category: essentials/image manipulation
- required:
  - tiles: IMAGE
  - overlap_x: INT default=0 min=0 max=8192 step=1
  - overlap_y: INT default=0 min=0 max=8192 step=1
  - rows: INT default=2 min=1 max=256 step=1
  - cols: INT default=2 min=1 max=256 step=1
- outputs: IMAGE:IMAGE

## ImageUpscaleWithModel
module: comfy_extras.nodes_upscale_model | category: image/upscaling
- required:
  - upscale_model: UPSCALE_MODEL
  - image: IMAGE
- outputs: IMAGE:IMAGE

## ImageUpscaleWithModelBatched
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - upscale_model: UPSCALE_MODEL
  - images: IMAGE
  - per_batch: INT default=16 min=1 max=4096 step=1
- optional:
  - downscale_ratio: FLOAT default=1.0 min=0.01 max=1.0 step=0.01
  - downscale_method: COMBO[nearest-exact, bilinear, area, bicubic, lanczos] default='lanczos'
  - precision: COMBO[float32, float16, bfloat16] default='float32'
- outputs: IMAGE:IMAGE

## ImageYUVToRGB
module: comfy_extras.nodes_morphology | category: image/color
- required:
  - Y: IMAGE
  - U: IMAGE
  - V: IMAGE
- outputs: IMAGE:IMAGE

## InjectLatentNoise+
module: custom_nodes.ComfyUI_essentials | category: essentials/sampling
- required:
  - latent: LATENT
  - noise_seed: INT default=0 min=0 max=18446744073709551615
  - noise_strength: FLOAT default=1.0 min=-20.0 max=20.0 step=0.01
  - normalize: COMBO[false, true] default='false'
- optional:
  - mask: MASK
- outputs: LATENT:LATENT

## InjectNoiseToLatent
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/noise
- required:
  - latents: LATENT
  - strength: FLOAT default=0.1 min=0.0 max=200.0 step=0.0001
  - noise: LATENT
  - normalize: BOOLEAN default=False
  - average: BOOLEAN default=False
- optional:
  - mask: MASK
  - mix_randn_amount: FLOAT default=0.0 min=0.0 max=1000.0 step=0.001
  - seed: INT default=123 min=0 max=18446744073709551615 step=1
- outputs: LATENT:LATENT

## InpaintModelConditioning
module: nodes | category: model/conditioning
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - pixels: IMAGE
  - mask: MASK
  - noise_mask: BOOLEAN default=True
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## InpaintPreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/others
- required:
  - image: IMAGE
  - mask: MASK
- optional:
  - black_pixel_for_xinsir_cn: BOOLEAN default=False
- outputs: IMAGE:IMAGE

## InsertImageBatchByIndexes
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - images: IMAGE
  - images_to_insert: IMAGE
  - insert_indexes: INDEXES
- outputs: images_after_insert:IMAGE

## InsertImagesToBatchIndexed
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - original_images: IMAGE
  - images_to_insert: IMAGE
  - indexes: STRING default='0, 1, 2'
- optional:
  - mode: COMBO[replace, insert]
- outputs: IMAGE:IMAGE

## InsertLatentToIndexed
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/latents
- required:
  - source: LATENT
  - destination: LATENT
  - index: INT default=0 min=-1 max=4096 step=1
- outputs: LATENT:LATENT

## InstructPixToPixConditioning
module: comfy_extras.nodes_ip2p | category: model/conditioning/instructpix2pix
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - pixels: IMAGE
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## INTConstant
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/constants
- required:
  - value: INT default=0 min=-18446744073709551615 max=18446744073709551615
- outputs: value:INT

## InterpolateCoords
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/experimental
- required:
  - coordinates: STRING
  - interpolation_curve: FLOAT
- outputs: coordinates:STRING

## InvertCondition
module: custom_nodes.ControlFlowUtils | category: 🐺 VykosX-ControlFlowUtils
- required:
  - input: *
  - mode: BOOLEAN default=True
- outputs: output:*

## InvertMask
module: comfy_extras.nodes_mask | category: image/mask
- required:
  - mask: MASK
- outputs: MASK:MASK

## JoinAudioChannels
module: comfy_extras.nodes_audio | category: audio
- required:
  - audio_left: AUDIO
  - audio_right: AUDIO
- outputs: audio:AUDIO

## JoinImageWithAlpha
module: comfy_extras.nodes_compositing | category: image/compositing
- required:
  - image: IMAGE
  - alpha: MASK
- outputs: IMAGE:IMAGE

## JoinStringMulti
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/text
- required:
  - inputcount: INT default=2 min=2 max=1000 step=1
  - string_1: STRING default=''
  - delimiter: STRING default=' '
  - return_list: BOOLEAN default=False
- optional:
  - string_2: STRING default=''
- outputs: string:STRING

## JoinStrings
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/text
- required:
  - delimiter: STRING default=' '
- optional:
  - string1: STRING default=''
  - string2: STRING default=''
- outputs: STRING:STRING

## JoyEcho_PromptSource
module: custom_nodes.ComfyUI-H3-Multishot | category: H3/script
- required:
  - source_file: COMBO[(no prompt files found)]
- optional:
  - load_cap: INT default=0 min=0
  - start_index: INT default=0 min=0
  - character_override: STRING default=''
  - manual_path: STRING default=''
  - folder: COMBO[(all)] default='(all)'
  - walk_folder: BOOLEAN default=False
- outputs: story_idea:STRING, character:STRING, count:INT

## JoyEcho_ScriptPicker
module: custom_nodes.ComfyUI-H3-Multishot | category: H3/script
- required:
  - script: COMBO[(no .json in input/joyecho_prompts)]
- outputs: prompts_json:STRING, path:STRING, speakers:STRING

## JSON comparator [Crystools]
module: custom_nodes.ComfyUI-Crystools | category: crystools 🪛/Utils
- required:
  - json_old: JSON
  - json_new: JSON
- outputs: json_compared:JSON

## JSON extractor [Crystools]
module: custom_nodes.ComfyUI-Crystools | category: crystools 🪛/Utils
- required:
  - json: JSON
- optional:
  - key: STRING default=''
  - default: STRING default=''
- outputs: any:*, string:STRING, int:INT, float:FLOAT, boolean:BOOLEAN

## JsonExtractString
module: comfy_extras.nodes_string | category: text
- required:
  - json_string: STRING
  - key: STRING
- outputs: STRING:STRING

## Kandinsky5ImageToVideo
module: comfy_extras.nodes_kandinsky5 | category: model/conditioning/kandinsky
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - width: INT default=768 min=16 max=16384 step=16
  - height: INT default=512 min=16 max=16384 step=16
  - length: INT default=121 min=1 max=16384 step=4
  - batch_size: INT default=1 min=1 max=4096
- optional:
  - start_image: IMAGE
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT, cond_latent:LATENT

## KarrasScheduler
module: comfy_extras.nodes_custom_sampler | category: model/sampling/schedulers
- required:
  - steps: INT default=20 min=1 max=10000
  - sigma_max: FLOAT default=14.614642 min=0.0 max=5000.0 step=0.01
  - sigma_min: FLOAT default=0.0291675 min=0.0 max=5000.0 step=0.01
  - rho: FLOAT default=7.0 min=0.0 max=100.0 step=0.01
- outputs: SIGMAS:SIGMAS

## KlingAvatarNode
module: comfy_api_nodes.nodes_kling | category: partner/video/Kling
- required:
  - image: IMAGE
  - sound_file: AUDIO
  - mode: COMBO[std, pro]
  - seed: INT default=0 min=0 max=2147483647
- optional:
  - prompt: STRING default=''
- outputs: VIDEO:VIDEO

## KlingFirstLastFrameNode
module: comfy_api_nodes.nodes_kling | category: partner/video/Kling
- required:
  - prompt: STRING default=''
  - duration: INT default=5 min=3 max=15
  - first_frame: IMAGE
  - end_frame: IMAGE
  - generate_audio: BOOLEAN default=True
  - model: COMFY_DYNAMICCOMBO_V3
  - seed: INT default=0 min=0 max=2147483647
- outputs: VIDEO:VIDEO

## KlingImage2VideoNode
module: comfy_api_nodes.nodes_kling | category: partner/video/Kling
- required:
  - start_frame: IMAGE
  - prompt: STRING
  - negative_prompt: STRING
  - model_name: COMBO[kling-v2-5-turbo]
  - cfg_scale: FLOAT default=0.8 min=0.0 max=1.0
  - mode: COMBO[pro]
  - aspect_ratio: COMBO[16:9, 9:16, 1:1] default='16:9'
  - duration: COMBO[5, 10] default='5'
- outputs: VIDEO:VIDEO, video_id:STRING, duration:STRING

## KlingImageGenerationNode
module: comfy_api_nodes.nodes_kling | category: partner/image/Kling
- required:
  - prompt: STRING
  - negative_prompt: STRING
  - image_type: COMBO[subject, face]
  - image_fidelity: FLOAT default=0.5 min=0.0 max=1.0 step=0.01
  - human_fidelity: FLOAT default=0.45 min=0.0 max=1.0 step=0.01
  - model_name: COMBO[kling-v3]
  - aspect_ratio: COMBO[16:9, 9:16, 1:1, 4:3, 3:4, 3:2, 2:3, 21:9] default='16:9'
  - n: INT default=1 min=1 max=9
- optional:
  - image: IMAGE
  - seed: INT default=0 min=0 max=2147483647
- outputs: IMAGE:IMAGE

## KlingImageToVideoWithAudio
module: comfy_api_nodes.nodes_kling | category: partner/video/Kling
- required:
  - model_name: COMBO[kling-v2-6]
  - start_frame: IMAGE
  - prompt: STRING
  - mode: COMBO[pro]
  - duration: COMBO[5, 10]
  - generate_audio: BOOLEAN default=True
- outputs: VIDEO:VIDEO

## KlingLipSyncAudioToVideoNode
module: comfy_api_nodes.nodes_kling | category: partner/video/Kling
- required:
  - video: VIDEO
  - audio: AUDIO
  - voice_language: COMBO[zh, en] default='en'
- outputs: VIDEO:VIDEO, video_id:STRING, duration:STRING

## KlingLipSyncTextToVideoNode
module: comfy_api_nodes.nodes_kling | category: partner/video/Kling
- required:
  - video: VIDEO
  - text: STRING
  - voice: COMBO[Melody, Sunny, Sage, Ace, Blossom, Peppy, Dove, Shine, Anchor, Lyric, ... +51] default='Melody'
  - voice_speed: FLOAT default=1 min=0.8 max=2.0
- outputs: VIDEO:VIDEO, video_id:STRING, duration:STRING

## KlingMotionControl
module: comfy_api_nodes.nodes_kling | category: partner/video/Kling
- required:
  - prompt: STRING
  - reference_image: IMAGE
  - reference_video: VIDEO
  - keep_original_sound: BOOLEAN default=True
  - character_orientation: COMBO[video, image]
  - mode: COMBO[pro, std]
- optional:
  - model: COMBO[kling-v3, kling-v2-6]
- outputs: VIDEO:VIDEO

## KlingOmniProEditVideoNode
module: comfy_api_nodes.nodes_kling | category: partner/video/Kling
- required:
  - model_name: COMBO[kling-v3-omni, kling-video-o1]
  - prompt: STRING
  - video: VIDEO
  - keep_original_sound: BOOLEAN default=True
- optional:
  - reference_images: IMAGE
  - resolution: COMBO[1080p, 720p]
  - seed: INT default=0 min=0 max=2147483647
- outputs: VIDEO:VIDEO

## KlingOmniProFirstLastFrameNode
module: comfy_api_nodes.nodes_kling | category: partner/video/Kling
- required:
  - model_name: COMBO[kling-v3-omni, kling-video-o1]
  - prompt: STRING
  - duration: INT default=5 min=3 max=15
  - first_frame: IMAGE
- optional:
  - end_frame: IMAGE
  - reference_images: IMAGE
  - resolution: COMBO[4k, 1080p, 720p] default='1080p'
  - storyboards: COMFY_DYNAMICCOMBO_V3
  - generate_audio: BOOLEAN default=False
  - seed: INT default=0 min=0 max=2147483647
- outputs: VIDEO:VIDEO

## KlingOmniProImageNode
module: comfy_api_nodes.nodes_kling | category: partner/image/Kling
- required:
  - model_name: COMBO[kling-v3-omni, kling-image-o1]
  - prompt: STRING
  - resolution: COMBO[1K, 2K, 4K]
  - aspect_ratio: COMBO[16:9, 9:16, 1:1, 4:3, 3:4, 3:2, 2:3, 21:9]
  - series_amount: COMBO[disabled, 2, 3, 4, 5, 6, 7, 8, 9]
- optional:
  - reference_images: IMAGE
  - seed: INT default=0 min=0 max=2147483647
- outputs: IMAGE:IMAGE

## KlingOmniProImageToVideoNode
module: comfy_api_nodes.nodes_kling | category: partner/video/Kling
- required:
  - model_name: COMBO[kling-v3-omni, kling-video-o1]
  - prompt: STRING
  - aspect_ratio: COMBO[16:9, 9:16, 1:1]
  - duration: INT default=5 min=3 max=15
  - reference_images: IMAGE
- optional:
  - resolution: COMBO[4k, 1080p, 720p] default='1080p'
  - storyboards: COMFY_DYNAMICCOMBO_V3
  - generate_audio: BOOLEAN default=False
  - seed: INT default=0 min=0 max=2147483647
- outputs: VIDEO:VIDEO

## KlingOmniProTextToVideoNode
module: comfy_api_nodes.nodes_kling | category: partner/video/Kling
- required:
  - model_name: COMBO[kling-v3-omni, kling-video-o1]
  - prompt: STRING
  - aspect_ratio: COMBO[16:9, 9:16, 1:1]
  - duration: INT default=5 min=3 max=15
- optional:
  - resolution: COMBO[4k, 1080p, 720p] default='1080p'
  - storyboards: COMFY_DYNAMICCOMBO_V3
  - generate_audio: BOOLEAN default=False
  - seed: INT default=0 min=0 max=2147483647
- outputs: VIDEO:VIDEO

## KlingOmniProVideoToVideoNode
module: comfy_api_nodes.nodes_kling | category: partner/video/Kling
- required:
  - model_name: COMBO[kling-v3-omni, kling-video-o1]
  - prompt: STRING
  - aspect_ratio: COMBO[16:9, 9:16, 1:1]
  - duration: INT default=3 min=3 max=10
  - reference_video: VIDEO
  - keep_original_sound: BOOLEAN default=True
- optional:
  - reference_images: IMAGE
  - resolution: COMBO[1080p, 720p]
  - seed: INT default=0 min=0 max=2147483647
- outputs: VIDEO:VIDEO

## KlingStartEndFrameNode
module: comfy_api_nodes.nodes_kling | category: partner/video/Kling
- required:
  - start_frame: IMAGE
  - end_frame: IMAGE
  - prompt: STRING
  - negative_prompt: STRING
  - cfg_scale: FLOAT default=0.5 min=0.0 max=1.0
  - aspect_ratio: COMBO[16:9, 9:16, 1:1]
  - mode: COMBO[pro mode / 5s duration / kling-v2-5-turbo, pro mode / 10s duration / kling-v2-5-turbo] default='pro mode / 5s duration / kling-v2-5-turbo'
- outputs: VIDEO:VIDEO, video_id:STRING, duration:STRING

## KlingTextToVideoNode
module: comfy_api_nodes.nodes_kling | category: partner/video/Kling
- required:
  - prompt: STRING
  - negative_prompt: STRING
  - cfg_scale: FLOAT default=1.0 min=0.0 max=1.0
  - aspect_ratio: COMBO[16:9, 9:16, 1:1] default='16:9'
  - mode: COMBO[pro mode / 5s duration / kling-v2-5-turbo, pro mode / 10s duration / kling-v2-5-turbo] default='pro mode / 5s duration / kling-v2-5-turbo'
- outputs: VIDEO:VIDEO, video_id:STRING, duration:STRING

## KlingTextToVideoWithAudio
module: comfy_api_nodes.nodes_kling | category: partner/video/Kling
- required:
  - model_name: COMBO[kling-v2-6]
  - prompt: STRING
  - mode: COMBO[pro]
  - aspect_ratio: COMBO[16:9, 9:16, 1:1]
  - duration: COMBO[5, 10]
  - generate_audio: BOOLEAN default=True
- outputs: VIDEO:VIDEO

## KlingVideoNode
module: comfy_api_nodes.nodes_kling | category: partner/video/Kling
- required:
  - multi_shot: COMFY_DYNAMICCOMBO_V3
  - generate_audio: BOOLEAN default=True
  - model: COMFY_DYNAMICCOMBO_V3
  - seed: INT default=0 min=0 max=2147483647
- optional:
  - start_frame: IMAGE
- outputs: VIDEO:VIDEO

## Krea2ImageNode
module: comfy_api_nodes.nodes_krea | category: partner/image/Krea
- required:
  - prompt: STRING default=''
  - model: COMFY_DYNAMICCOMBO_V3
  - seed: INT default=0 min=0 max=2147483647
- outputs: IMAGE:IMAGE

## Krea2StyleReferenceNode
module: comfy_api_nodes.nodes_krea | category: partner/image/Krea
- required:
  - image: IMAGE
  - strength: FLOAT default=1.0 min=-2.0 max=2.0 step=0.05
- optional:
  - style_reference: KREA_STYLE_REF
- outputs: style_reference:KREA_STYLE_REF

## KSampler
module: nodes | category: model/sampling
- required:
  - model: MODEL
  - seed: INT default=0 min=0 max=18446744073709551615
  - steps: INT default=20 min=1 max=10000
  - cfg: FLOAT default=8.0 min=0.0 max=100.0 step=0.1
  - sampler_name: COMBO[euler, euler_cfg_pp, euler_ancestral, euler_ancestral_cfg_pp, heun, heunpp2, exp_heun_2_x0, exp_heun_2_x0_sde, dpm_2, dpm_2_ancestral, ... +35]
  - scheduler: COMBO[simple, sgm_uniform, karras, exponential, ddim_uniform, beta, normal, linear_quadratic, kl_optimal]
  - positive: CONDITIONING
  - negative: CONDITIONING
  - latent_image: LATENT
  - denoise: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: LATENT:LATENT

## KSampler Config (rgthree)
module: custom_nodes.rgthree-comfy | category: rgthree
- required:
  - steps_total: INT default=30 min=1 max=16384 step=1
  - refiner_step: INT default=24 min=1 max=16384 step=1
  - cfg: FLOAT default=8.0 min=0.0 max=100.0 step=0.5
  - sampler_name: COMBO[euler, euler_cfg_pp, euler_ancestral, euler_ancestral_cfg_pp, heun, heunpp2, exp_heun_2_x0, exp_heun_2_x0_sde, dpm_2, dpm_2_ancestral, ... +35]
  - scheduler: COMBO[simple, sgm_uniform, karras, exponential, ddim_uniform, beta, normal, linear_quadratic, kl_optimal]
- outputs: STEPS:INT, REFINER_STEP:INT, CFG:FLOAT, SAMPLER:['euler', 'euler_cfg_pp', 'euler_ancestral', 'euler_ancestral_cfg_pp', 'heun', 'heunpp2', 'exp_heun_2_x0', 'exp_heun_2_x0_sde', 'dpm_2', 'dpm_2_ancestral', 'lms', 'dpm_fast', 'dpm_adaptive', 'dpmpp_2s_ancestral', 'dpmpp_2s_ancestral_cfg_pp', 'dpmpp_sde', 'dpmpp_sde_gpu', 'dpmpp_2m', 'dpmpp_2m_cfg_pp', 'dpmpp_2m_sde', 'dpmpp_2m_sde_gpu', 'dpmpp_2m_sde_heun', 'dpmpp_2m_sde_heun_gpu', 'dpmpp_3m_sde', 'dpmpp_3m_sde_gpu', 'ddpm', 'lcm', 'ipndm', 'ipndm_v', 'deis', 'cfgpp_ud10_ab', 'res_multistep', 'res_multistep_cfg_pp', 'res_multistep_ancestral', 'res_multistep_ancestral_cfg_pp', 'gradient_estimation', 'gradient_estimation_cfg_pp', 'er_sde', 'seeds_2', 'seeds_3', 'sa_solver', 'sa_solver_pece', 'ddim', 'uni_pc', 'uni_pc_bh2'], SCHEDULER:['simple', 'sgm_uniform', 'karras', 'exponential', 'ddim_uniform', 'beta', 'normal', 'linear_quadratic', 'kl_optimal']

## KSamplerAdvanced
module: nodes | category: model/sampling
- required:
  - model: MODEL
  - add_noise: COMBO[enable, disable]
  - noise_seed: INT default=0 min=0 max=18446744073709551615
  - steps: INT default=20 min=1 max=10000
  - cfg: FLOAT default=8.0 min=0.0 max=100.0 step=0.1
  - sampler_name: COMBO[euler, euler_cfg_pp, euler_ancestral, euler_ancestral_cfg_pp, heun, heunpp2, exp_heun_2_x0, exp_heun_2_x0_sde, dpm_2, dpm_2_ancestral, ... +35]
  - scheduler: COMBO[simple, sgm_uniform, karras, exponential, ddim_uniform, beta, normal, linear_quadratic, kl_optimal]
  - positive: CONDITIONING
  - negative: CONDITIONING
  - latent_image: LATENT
  - start_at_step: INT default=0 min=0 max=10000
  - end_at_step: INT default=10000 min=0 max=10000
  - return_with_leftover_noise: COMBO[disable, enable]
- outputs: LATENT:LATENT

## KSamplerSelect
module: comfy_extras.nodes_custom_sampler | category: model/sampling/samplers
- required:
  - sampler_name: COMBO[euler, euler_cfg_pp, euler_ancestral, euler_ancestral_cfg_pp, heun, heunpp2, exp_heun_2_x0, exp_heun_2_x0_sde, dpm_2, dpm_2_ancestral, ... +35]
- outputs: SAMPLER:SAMPLER

## KSamplerVariationsStochastic+
module: custom_nodes.ComfyUI_essentials | category: essentials/sampling
- required:
  - model: MODEL
  - latent_image: LATENT
  - noise_seed: INT default=0 min=0 max=18446744073709551615
  - steps: INT default=25 min=1 max=10000
  - cfg: FLOAT default=7.0 min=0.0 max=100.0 step=0.1
  - sampler: COMBO[euler, euler_cfg_pp, euler_ancestral, euler_ancestral_cfg_pp, heun, heunpp2, exp_heun_2_x0, exp_heun_2_x0_sde, dpm_2, dpm_2_ancestral, ... +35]
  - scheduler: COMBO[simple, sgm_uniform, karras, exponential, ddim_uniform, beta, normal, linear_quadratic, kl_optimal]
  - positive: CONDITIONING
  - negative: CONDITIONING
  - variation_seed: INT:seed default=0 min=0 max=18446744073709551615
  - variation_strength: FLOAT default=0.2 min=0.0 max=1.0 step=0.05
  - cfg_scale: FLOAT default=1.0 min=0.0 max=1.0 step=0.05
- outputs: LATENT:LATENT

## KSamplerVariationsWithNoise+
module: custom_nodes.ComfyUI_essentials | category: essentials/sampling
- required:
  - model: MODEL
  - latent_image: LATENT
  - main_seed: INT:seed default=0 min=0 max=18446744073709551615
  - steps: INT default=20 min=1 max=10000
  - cfg: FLOAT default=8.0 min=0.0 max=100.0 step=0.1
  - sampler_name: COMBO[euler, euler_cfg_pp, euler_ancestral, euler_ancestral_cfg_pp, heun, heunpp2, exp_heun_2_x0, exp_heun_2_x0_sde, dpm_2, dpm_2_ancestral, ... +35]
  - scheduler: COMBO[simple, sgm_uniform, karras, exponential, ddim_uniform, beta, normal, linear_quadratic, kl_optimal]
  - positive: CONDITIONING
  - negative: CONDITIONING
  - variation_strength: FLOAT default=0.17 min=0.0 max=1.0 step=0.01
  - variation_seed: INT:seed default=12345 min=0 max=18446744073709551615
  - denoise: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: LATENT:LATENT

## LaplaceScheduler
module: comfy_extras.nodes_custom_sampler | category: model/sampling/schedulers
- required:
  - steps: INT default=20 min=1 max=10000
  - sigma_max: FLOAT default=14.614642 min=0.0 max=5000.0 step=0.01
  - sigma_min: FLOAT default=0.0291675 min=0.0 max=5000.0 step=0.01
  - mu: FLOAT default=0.0 min=-10.0 max=10.0 step=0.1
  - beta: FLOAT default=0.5 min=0.0 max=10.0 step=0.1
- outputs: SIGMAS:SIGMAS

## LatentAdd
module: comfy_extras.nodes_latent | category: model/latent/advanced
- required:
  - samples1: LATENT
  - samples2: LATENT
- outputs: LATENT:LATENT

## LatentApplyOperation
module: comfy_extras.nodes_latent | category: model/latent/advanced/operations
- required:
  - samples: LATENT
  - operation: LATENT_OPERATION
- outputs: LATENT:LATENT

## LatentApplyOperationCFG
module: comfy_extras.nodes_latent | category: model/latent/advanced/operations
- required:
  - model: MODEL
  - operation: LATENT_OPERATION
- outputs: MODEL:MODEL

## LatentBatch
module: comfy_extras.nodes_latent | category: model/latent/batch
- required:
  - samples1: LATENT
  - samples2: LATENT
- outputs: LATENT:LATENT

## LatentBatchSeedBehavior
module: comfy_extras.nodes_latent | category: model/latent/advanced
- required:
  - samples: LATENT
  - seed_behavior: COMBO[random, fixed] default='fixed'
- outputs: LATENT:LATENT

## LatentBlend
module: nodes | category: experimental
- required:
  - samples1: LATENT
  - samples2: LATENT
  - blend_factor: FLOAT default=0.5 min=0 max=1 step=0.01
- outputs: LATENT:LATENT

## LatentComposite
module: nodes | category: model/latent
- required:
  - samples_to: LATENT
  - samples_from: LATENT
  - x: INT default=0 min=0 max=16384 step=8
  - y: INT default=0 min=0 max=16384 step=8
  - feather: INT default=0 min=0 max=16384 step=8
- outputs: LATENT:LATENT

## LatentCompositeMasked
module: comfy_extras.nodes_mask | category: model/latent
- required:
  - destination: LATENT
  - source: LATENT
  - x: INT default=0 min=0 max=16384 step=8
  - y: INT default=0 min=0 max=16384 step=8
  - resize_source: BOOLEAN default=False
- optional:
  - mask: MASK
- outputs: LATENT:LATENT

## LatentConcat
module: comfy_extras.nodes_latent | category: model/latent/advanced
- required:
  - samples1: LATENT
  - samples2: LATENT
  - dim: COMBO[x, -x, y, -y, t, -t]
- outputs: LATENT:LATENT

## LatentCrop
module: nodes | category: model/latent/transform
- required:
  - samples: LATENT
  - width: INT default=512 min=64 max=16384 step=8
  - height: INT default=512 min=64 max=16384 step=8
  - x: INT default=0 min=0 max=16384 step=8
  - y: INT default=0 min=0 max=16384 step=8
- outputs: LATENT:LATENT

## LatentCrossFadeAutoConcat
module: custom_nodes.10S-Comfy-nodes | category: 10S Nodes/Latents
- required:
  - frames_0: LATENT
  - frames_1: LATENT
- optional:
  - match_spatial: BOOLEAN default=True
  - interpolate_mode: COMBO[nearest-exact, bilinear, bicubic] default='nearest-exact'
  - cross_fade_frames: INT default=6 min=0 max=24 step=1
  - fade_curve: COMBO[linear, ease_in, ease_out, ease_in_out] default='linear'
- outputs: latent:LATENT

## LatentCut
module: comfy_extras.nodes_latent | category: model/latent/advanced
- required:
  - samples: LATENT
  - dim: COMBO[x, y, t]
  - index: INT default=0 min=-16384 max=16384 step=1
  - amount: INT default=1 min=1 max=16384 step=1
- outputs: LATENT:LATENT

## LatentCutToBatch
module: comfy_extras.nodes_latent | category: model/latent/advanced
- required:
  - samples: LATENT
  - dim: COMBO[t, x, y]
  - slice_size: INT default=1 min=1 max=16384 step=1
- outputs: LATENT:LATENT

## LatentFlip
module: nodes | category: model/latent/transform
- required:
  - samples: LATENT
  - flip_method: COMBO[x-axis: vertically, y-axis: horizontally]
- outputs: LATENT:LATENT

## LatentFromBatch
module: nodes | category: model/latent/batch
- required:
  - samples: LATENT
  - batch_index: INT default=0 min=-16384 max=16384
  - length: INT default=1 min=1 max=64
- outputs: LATENT:LATENT

## LatentInpaintTTM
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/experimental
- required:
  - model: MODEL
  - steps: INT default=7 min=0 max=888 step=1
- optional:
  - mask: MASK
- outputs: MODEL:MODEL

## LatentInterpolate
module: comfy_extras.nodes_latent | category: model/latent/advanced
- required:
  - samples1: LATENT
  - samples2: LATENT
  - ratio: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: LATENT:LATENT

## LatentMotionRetime
module: custom_nodes.10S-Comfy-nodes | category: 10S Nodes/Latents
- required:
  - latent: LATENT
- optional:
  - source_fps: FLOAT default=24.0 min=1.0 max=120.0 step=0.1
  - target_fps: FLOAT default=30.0 min=1.0 max=120.0 step=0.1
  - strength: FLOAT default=1.0 min=0.0 max=1.0 step=0.05
  - manual_scale: FLOAT default=0.0 min=0.0 max=2.0 step=0.05
- outputs: latent:LATENT

## LatentMotionSharpener
module: custom_nodes.10S-Comfy-nodes | category: 10S Nodes/Latents
- required:
  - latent: LATENT
- optional:
  - base_sharpen: FLOAT default=0.08 min=0.0 max=1.0 step=0.01
  - motion_sharpen: FLOAT default=0.55 min=0.0 max=2.0 step=0.05
  - motion_thresh: FLOAT default=0.04 min=0.0 max=0.5 step=0.01
  - temporal_smooth_mask: BOOLEAN default=True
- outputs: latent:LATENT

## LatentMultiply
module: comfy_extras.nodes_latent | category: model/latent/advanced
- required:
  - samples: LATENT
  - multiplier: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
- outputs: LATENT:LATENT

## LatentOperationSharpen
module: comfy_extras.nodes_latent | category: model/latent/advanced/operations
- required:
  - sharpen_radius: INT default=9 min=1 max=31 step=1
  - sigma: FLOAT default=1.0 min=0.1 max=10.0 step=0.1
  - alpha: FLOAT default=0.1 min=0.0 max=5.0 step=0.01
- outputs: LATENT_OPERATION:LATENT_OPERATION

## LatentOperationTonemapReinhard
module: comfy_extras.nodes_latent | category: model/latent/advanced/operations
- required:
  - multiplier: FLOAT default=1.0 min=0.0 max=100.0 step=0.01
- outputs: LATENT_OPERATION:LATENT_OPERATION

## LatentRotate
module: nodes | category: model/latent/transform
- required:
  - samples: LATENT
  - rotation: COMBO[none, 90 degrees, 180 degrees, 270 degrees]
- outputs: LATENT:LATENT

## LatentSubtract
module: comfy_extras.nodes_latent | category: model/latent/advanced
- required:
  - samples1: LATENT
  - samples2: LATENT
- outputs: LATENT:LATENT

## LatentTemporalInpainter
module: custom_nodes.10S-Comfy-nodes | category: 10S Nodes/Latents
- required:
  - latent: LATENT
- optional:
  - anchor_sigma: FLOAT default=0.05 min=0.0 max=0.3 step=0.01
  - ghost_sigma: FLOAT default=0.35 min=0.05 max=0.8 step=0.01
  - score_gamma: FLOAT default=2.0 min=0.01 max=5.0 step=0.01
  - anchor_blend: FLOAT default=0.4 min=0.0 max=1.0 step=0.05
  - seed: INT default=0 min=0 max=2147483648 step=1
  - debug_scores: BOOLEAN default=False
- outputs: latent:LATENT

## LatentTemporalUpsampler
module: custom_nodes.10S-Comfy-nodes | category: 10S Nodes/Latents
- required:
  - latent: LATENT
  - source_fps: FLOAT default=24.0 min=1.0 max=120.0 step=0.1
  - target_fps: FLOAT default=30.0 min=1.0 max=120.0 step=0.1
- optional:
  - interp_mode: COMBO[hermite, linear, nearest] default='hermite'
  - auto_retime: BOOLEAN default=True
  - motion_scale: FLOAT default=1.0 min=0.0 max=3.0 step=0.05
  - spatial_sharpen: FLOAT default=0.15 min=0.0 max=1.0 step=0.05
  - ltx_safe: BOOLEAN default=False
  - override_frames: INT default=0 min=0 max=4096 step=1
- outputs: latent:LATENT

## LatentUpscale
module: nodes | category: model/latent
- required:
  - samples: LATENT
  - upscale_method: COMBO[nearest-exact, bilinear, area, bicubic, bislerp]
  - width: INT default=512 min=0 max=16384 step=8
  - height: INT default=512 min=0 max=16384 step=8
  - crop: COMBO[disabled, center]
- outputs: LATENT:LATENT

## LatentUpscaleBy
module: nodes | category: model/latent
- required:
  - samples: LATENT
  - upscale_method: COMBO[nearest-exact, bilinear, area, bicubic, bislerp]
  - scale_by: FLOAT default=1.5 min=0.01 max=8.0 step=0.01
- outputs: LATENT:LATENT

## LatentUpscaleModelLoader
module: comfy_extras.nodes_hunyuan | category: model/loaders
- required:
  - model_name: COMBO[minimax_h3_latent_upscaler_3d_conv_v1_bf16.safetensors, minimax_h3_latent_upscaler_3d_fp16.safetensors]
- outputs: LATENT_UPSCALE_MODEL:LATENT_UPSCALE_MODEL

## LayersFromBoundingBoxes
module: comfy_extras.nodes_compositor | category: image
- required:
  - image: IMAGE
  - bboxes: BOUNDING_BOX,ARRAY,STRING
- optional:
  - mask: MASK
  - layers: LAYERS
  - crop_to_content: BOOLEAN default=True
  - canvas_width: INT default=0 min=0 max=16384
  - canvas_height: INT default=0 min=0 max=16384
- outputs: LAYERS:LAYERS

## LazyCache
module: comfy_extras.nodes_easycache | category: advanced/debug
- required:
  - model: MODEL
  - reuse_threshold: FLOAT default=0.2 min=0.0 max=3.0 step=0.01
  - start_percent: FLOAT default=0.15 min=0.0 max=1.0 step=0.01
  - end_percent: FLOAT default=0.95 min=0.0 max=1.0 step=0.01
  - verbose: BOOLEAN default=False
- outputs: MODEL:MODEL

## LazySwitchKJ
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/misc
- required:
  - switch: BOOLEAN
  - on_false: *
  - on_true: *
- outputs: *:*

## LeapfusionHunyuanI2VPatcher
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/hunyuanvideo
- required:
  - model: MODEL
  - latent: LATENT
  - index: INT default=0 min=-1 max=1000 step=1
  - start_percent: FLOAT default=0.0 min=0.0 max=1.0 step=0.01
  - end_percent: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - strength: FLOAT default=1.0 min=-10.0 max=10.0 step=0.001
- outputs: MODEL:MODEL

## LeReS-DepthMapPreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Normal and Depth Estimators
- required:
  - image: IMAGE
- optional:
  - rm_nearest: FLOAT default=0 min=0 max=100.0 step=0.01
  - rm_background: FLOAT default=0 min=0 max=100.0 step=0.01
  - boost: COMBO[disable, enable] default='disable'
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## LineArtPreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Line Extractors
- required:
  - image: IMAGE
- optional:
  - coarse: COMBO[disable, enable] default='disable'
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## LineartStandardPreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Line Extractors
- required:
  - image: IMAGE
- optional:
  - guassian_sigma: FLOAT default=6.0 min=0 max=100.0 step=0.01
  - intensity_threshold: INT default=8 min=0 max=16 step=1
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## List of any [Crystools]
module: custom_nodes.ComfyUI-Crystools | category: crystools 🪛/List
- optional:
  - any_1: *
  - any_2: *
  - any_3: *
  - any_4: *
  - any_5: *
  - any_6: *
  - any_7: *
  - any_8: *
- outputs: any_list:['*']

## List of strings [Crystools]
module: custom_nodes.ComfyUI-Crystools | category: crystools 🪛/List
- optional:
  - string_1: STRING default=''
  - string_2: STRING default=''
  - string_3: STRING default=''
  - string_4: STRING default=''
  - string_5: STRING default=''
  - string_6: STRING default=''
  - string_7: STRING default=''
  - string_8: STRING default=''
  - delimiter: STRING default=' '
- outputs: concatenated:STRING, list_string:ListString

## Load image with metadata [Crystools]
module: custom_nodes.ComfyUI-Crystools | category: crystools 🪛/Image
- required:
  - image: COMBO[01_BEDROOM_LINGERIE.jpg, 32.jpg, 33.jpg, 5slock_B07ref.jpg, 5slock_E10.jpg, 5slock_E10ref.jpg, 5slock_O3.png, 5slock_ORIG01ref.png, 5slock_POOLref.jpg, 5slock_chain_O1_twoshot.png, ... +3069]
- outputs: image:IMAGE, mask:MASK, prompt:JSON, Metadata RAW:METADATA_RAW

## Load3D
module: comfy_extras.nodes_load_3d | category: 3d
- required:
  - model_file: COMBO[none]
  - image: LOAD_3D
  - width: INT default=1024 min=1 max=4096 step=1
  - height: INT default=1024 min=1 max=4096 step=1
- outputs: image:IMAGE, mask:MASK, mesh_path:STRING, normal:IMAGE, camera_info:LOAD3D_CAMERA, recording_video:VIDEO, model_3d:FILE_3D, model_3d_info:LOAD3D_MODEL_INFO

## Load3DAdvanced
module: comfy_extras.nodes_load_3d | category: 3d
- required:
  - model_file: COMBO[none]
  - viewport_state: LOAD_3D
  - width: INT default=1024 min=1 max=4096 step=1
  - height: INT default=1024 min=1 max=4096 step=1
- outputs: model_3d:FILE_3D, model_3d_info:LOAD3D_MODEL_INFO, camera_info:LOAD3D_CAMERA, width:INT, height:INT

## LoadAndResizeImage
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - image: COMBO[01_BEDROOM_LINGERIE.jpg, 32.jpg, 33.jpg, 5slock_B07ref.jpg, 5slock_E10.jpg, 5slock_E10ref.jpg, 5slock_O3.png, 5slock_ORIG01ref.png, 5slock_POOLref.jpg, 5slock_chain_O1_twoshot.png, ... +2895]
  - resize: BOOLEAN default=False
  - width: INT default=512 min=0 max=16384 step=8
  - height: INT default=512 min=0 max=16384 step=8
  - repeat: INT default=1 min=1 max=4096 step=1
  - keep_proportion: BOOLEAN default=False
  - divisible_by: INT default=2 min=0 max=512 step=1
  - mask_channel: COMBO[alpha, red, green, blue]
  - background_color: STRING default=''
- outputs: image:IMAGE, mask:MASK, width:INT, height:INT, image_path:STRING

## LoadAudio
module: comfy_extras.nodes_audio | category: audio
- required:
  - audio: COMBO[5slock_ext_SB1r3.mp4, 5slock_lcv_SB1r3_24fps.mp4, MAX5S_ORC_B0_ST6_1344x768_noRIFE_s2015873178_00001_.mp4, MAXOPT_R3b_full_simple_sA_s43029049_00001_.mp4, MAXOPT_R3b_sA_tail2s_for_hop.mp4, MAX_1MIN_T0_PRIOR.mp4, MAX_REF_ORC_BJ_OPT_SCH_WARM_BETA_s25102401_00001_.mp4, c04_cell1_native.mp4, c04_cell1_tail22.mp4, c04_cell2_native.mp4, ... +66]
- outputs: AUDIO:AUDIO

## LoadBackgroundRemovalModel
module: comfy_extras.nodes_bg_removal | category: model/loaders
- required:
  - bg_removal_name: COMBO[]
- outputs: bg_model:BACKGROUND_REMOVAL

## LoadCLIPSegModels+
module: custom_nodes.ComfyUI_essentials | category: essentials/segmentation
- outputs: CLIP_SEG:CLIP_SEG

## LoadDA3Model
module: comfy_extras.nodes_depth_anything_3 | category: model/loaders
- required:
  - model_name: COMBO[]
  - weight_dtype: COMBO[default, fp16, bf16, fp32] default='default'
- outputs: DA3_MODEL:DA3_MODEL

## LoadImage
module: nodes | category: image
- required:
  - image: COMBO[01_BEDROOM_LINGERIE.jpg, 32.jpg, 33.jpg, 5slock_B07ref.jpg, 5slock_E10.jpg, 5slock_E10ref.jpg, 5slock_O3.png, 5slock_ORIG01ref.png, 5slock_POOLref.jpg, 5slock_chain_O1_twoshot.png, ... +2817]
- outputs: IMAGE:IMAGE, MASK:MASK

## LoadImageDataSetFromFolder
module: comfy_extras.nodes_dataset | category: image
- required:
  - folder: COMBO[3d, community, community/2026-10-31_klein_explicit_0010, community/bj_pov_20261030, community/bj_pov_20261102, community/flux_p1_20261030, community/flux_redo_20261030, community/hc, community/lora_conv_e10_20261103, community/p15_poses, ... +10]
- outputs: images:IMAGE

## LoadImageMask
module: nodes | category: image
- required:
  - image: COMBO[01_BEDROOM_LINGERIE.jpg, 32.jpg, 33.jpg, 5slock_B07ref.jpg, 5slock_E10.jpg, 5slock_E10ref.jpg, 5slock_O3.png, 5slock_ORIG01ref.png, 5slock_POOLref.jpg, 5slock_chain_O1_twoshot.png, ... +2817]
  - channel: COMBO[alpha, red, green, blue]
- outputs: MASK:MASK

## LoadImageOutput
module: nodes | category: image
- required:
  - image: COMBO
- outputs: IMAGE:IMAGE, MASK:MASK

## LoadImagesFromFolderKJ
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - folder: STRING default=''
  - width: INT default=1024 min=-1 step=1
  - height: INT default=1024 min=-1 step=1
  - keep_aspect_ratio: COMBO[crop, pad, stretch]
- optional:
  - image_load_cap: INT default=0 min=0 step=1
  - start_index: INT default=0 min=0 step=1
  - include_subfolders: BOOLEAN default=False
- outputs: image:IMAGE, mask:MASK, count:INT, image_path:STRING

## LoadImageTextDataSetFromFolder
module: comfy_extras.nodes_dataset | category: image
- required:
  - folder: COMBO[3d, community, community/2026-10-31_klein_explicit_0010, community/bj_pov_20261030, community/bj_pov_20261102, community/flux_p1_20261030, community/flux_redo_20261030, community/hc, community/lora_conv_e10_20261103, community/p15_poses, ... +10]
- outputs: images:IMAGE, texts:STRING

## LoadLatent
module: nodes | category: model/latent
- required:
  - latent: COMBO[]
- outputs: LATENT:LATENT

## LoadMediaPipeFaceLandmarker
module: comfy_extras.nodes_mediapipe | category: model/loaders
- required:
  - model_name: COMBO[]
- outputs: FACE_DETECTION_MODEL:FACE_DETECTION_MODEL

## LoadMoGeModel
module: comfy_extras.nodes_moge | category: model/loaders
- required:
  - model_name: COMBO[]
- outputs: MOGE_MODEL:MOGE_MODEL

## LoadText|pysssss
module: custom_nodes.ComfyUI-Custom-Scripts | category: utils
- required:
  - root_dir: COMBO[input, output, temp]
  - file: COMBO[[none]]
- outputs: STRING:STRING

## LoadTrainingDataset
module: comfy_extras.nodes_dataset | category: model/training
- required:
  - folder_name: COMBO[]
- outputs: latents:LATENT, conditioning:CONDITIONING

## LoadVideo
module: comfy_extras.nodes_video | category: video
- required:
  - file: COMBO[5slock_ext_SB1r3.mp4, 5slock_lcv_SB1r3_24fps.mp4, MAX5S_ORC_B0_ST6_1344x768_noRIFE_s2015873178_00001_.mp4, MAXOPT_R3b_full_simple_sA_s43029049_00001_.mp4, MAXOPT_R3b_sA_tail2s_for_hop.mp4, MAX_1MIN_T0_PRIOR.mp4, MAX_REF_ORC_BJ_OPT_SCH_WARM_BETA_s25102401_00001_.mp4, c04_cell1_native.mp4, c04_cell1_tail22.mp4, c04_cell2_native.mp4, ... +66]
- outputs: VIDEO:VIDEO

## LoadVideoDataSetFromFolder
module: comfy_extras.nodes_dataset | category: video
- required:
  - folder: COMBO[3d, community, community/2026-10-31_klein_explicit_0010, community/bj_pov_20261030, community/bj_pov_20261102, community/flux_p1_20261030, community/flux_redo_20261030, community/hc, community/lora_conv_e10_20261103, community/p15_poses, ... +10]
- outputs: videos:VIDEO

## LoadVideosFromFolder
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/misc
- required:
  - video: STRING default='X://insert/path/'
  - force_rate: FLOAT default=0 min=0 max=60 step=1
  - custom_width: INT default=0 min=0 max=4096
  - custom_height: INT default=0 min=0 max=4096
  - frame_load_cap: INT default=0 min=0 max=10000 step=1
  - skip_first_frames: INT default=0 min=0 max=10000 step=1
  - select_every_nth: INT default=1 min=1 max=1000 step=1
  - output_type: COMBO[batch, grid] default='batch'
  - grid_max_columns: INT default=4 min=1 max=16 step=1
  - add_label: BOOLEAN default=False
- outputs: IMAGE:IMAGE

## LoadVideoTextDataSetFromFolder
module: comfy_extras.nodes_dataset | category: video
- required:
  - folder: COMBO[3d, community, community/2026-10-31_klein_explicit_0010, community/bj_pov_20261030, community/bj_pov_20261102, community/flux_p1_20261030, community/flux_redo_20261030, community/hc, community/lora_conv_e10_20261103, community/p15_poses, ... +10]
- outputs: videos:VIDEO, texts:STRING

## LokkenVideoPostProcessing
module: custom_nodes.ComfyUI-Lokken-VideoTools | category: Lokken/Video
- required:
  - upscale: BOOLEAN default=True
  - upscale_method: COMBO[lanczos] default='lanczos'
  - upscale_by: FLOAT default=2.0 min=0.01 max=8.0 step=0.01
  - interpolate: BOOLEAN default=True
  - original_fps: FLOAT default=24.0 min=0.1 max=240.0 step=0.1
  - interpolate_by: INT default=2 min=2 max=10 step=1
  - dual_pass_rife: BOOLEAN default=False
  - grain: BOOLEAN default=True
  - grain_intensity: FLOAT default=0.025 min=0.001 max=1.0 step=0.001
  - saturation_mix: FLOAT default=0.25 min=0.0 max=1.0 step=0.01
  - compress: BOOLEAN default=True
  - crf: INT default=18 min=0 max=51 step=1
  - batching_mode: COMBO[full sequence, normal (64), low vram (16), custom] default='normal (64)'
  - custom_batch_size: INT default=16 min=1 max=2147483647 step=1
  - encoder_preset: COMBO[ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow] default='medium'
  - h264_profile: COMBO[auto, baseline, main, high] default='auto'
- optional:
  - video: VIDEO
  - images: IMAGE
  - audio_pass: AUDIO
- outputs: VIDEO:VIDEO, FPS:FLOAT, stats:STRING

## LoopClose
module: custom_nodes.ControlFlowUtils | category: 🐺 VykosX-ControlFlowUtils
- required:
  - LOOP: *
  - condition: STRING default='True'
- optional:
  - data: *
  - aux: *
  - aux2: *
  - aux3: *
  - aux4: *
  - aux5: *
- outputs: FINISHED?:BOOLEAN, data:*, aux:*, aux2:*, aux3:*, aux4:*, aux5:*

## LoopIteration
module: comfy_extras.nodes_loop | category: sd
- required:
  - iteration_index: INT
  - is_first: BOOLEAN
  - is_last: BOOLEAN
  - reuse_cache: BOOLEAN
- optional:
  - list_item: *
  - current_iteration_value: *
- outputs: INT:INT, BOOLEAN:BOOLEAN, BOOLEAN:BOOLEAN, *:*, *:*

## LoopOpen
module: custom_nodes.ControlFlowUtils | category: 🐺 VykosX-ControlFlowUtils
- required:
  - start: INT default=1
  - step: INT default=1
  - end: INT default=10
  - condition: STRING default='True'
- optional:
  - index_override: *
  - data: *
  - aux: *
  - aux2: *
  - aux3: *
  - aux4: *
  - aux5: *
- outputs: LOOP:*, data:*, aux:*, aux2:*, aux3:*, aux4:*, aux5:*

## LoopProgress
module: comfy_extras.nodes_loop | category: sd
- required:
  - start_id: STRING
  - position: INT
  - total: INT
- outputs: INT:INT

## LoopResult
module: comfy_extras.nodes_loop | category: sd
- required:
  - close_id: STRING
- outputs: 

## Lora Loader Stack (rgthree)
module: custom_nodes.rgthree-comfy | category: rgthree
- required:
  - model: MODEL
  - clip: CLIP
  - lora_01: COMBO[None, FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, ... +49]
  - strength_01: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - lora_02: COMBO[None, FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, ... +49]
  - strength_02: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - lora_03: COMBO[None, FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, ... +49]
  - strength_03: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - lora_04: COMBO[None, FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, ... +49]
  - strength_04: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
- outputs: MODEL:MODEL, CLIP:CLIP

## LoraExtractKJ
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/lora
- required:
  - finetuned: MODEL,CLIP
  - original: MODEL,CLIP
  - filename_prefix: STRING default='loras/ComfyUI_extracted_lora'
  - rank: INT default=64 min=1 max=4096 step=1
  - lora_type: COMBO[standard, full, adaptive_ratio, adaptive_quantile, adaptive_energy, adaptive_fro]
  - algorithm: COMBO[svd_linalg, svd_lowrank] default='svd_lowrank'
  - lowrank_iters: INT default=7 min=1 max=100 step=1
  - output_dtype: COMBO[fp16, bf16, fp32] default='fp16'
  - bias_diff: BOOLEAN default=True
  - adaptive_param: FLOAT default=0.15 min=0.0 max=1.0 step=0.01
  - clamp_quantile: BOOLEAN default=False
- outputs: 

## LoraLoader
module: nodes | category: model/loaders
- required:
  - model: MODEL
  - clip: CLIP
  - lora_name: COMBO[FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, FC_KIERNAN_h3_face_v1.safetensors, ... +48]
  - strength_model: FLOAT default=1.0 min=-100.0 max=100.0 step=0.01
  - strength_clip: FLOAT default=1.0 min=-100.0 max=100.0 step=0.01
- outputs: MODEL:MODEL, CLIP:CLIP

## LoraLoaderBypass
module: comfy_extras.nodes_lora_debug | category: model/loaders
- required:
  - model: MODEL
  - clip: CLIP
  - lora_name: COMBO[FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, FC_KIERNAN_h3_face_v1.safetensors, ... +48]
  - strength_model: FLOAT default=1.0 min=-100.0 max=100.0 step=0.01
  - strength_clip: FLOAT default=1.0 min=-100.0 max=100.0 step=0.01
- outputs: MODEL:MODEL, CLIP:CLIP

## LoraLoaderBypassModelOnly
module: comfy_extras.nodes_lora_debug | category: model/loaders
- required:
  - model: MODEL
  - lora_name: COMBO[FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, FC_KIERNAN_h3_face_v1.safetensors, ... +48]
  - strength_model: FLOAT default=1.0 min=-100.0 max=100.0 step=0.01
- outputs: MODEL:MODEL

## LoraLoaderModelOnly
module: nodes | category: model/loaders
- required:
  - model: MODEL
  - lora_name: COMBO[FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, FC_KIERNAN_h3_face_v1.safetensors, ... +48]
  - strength_model: FLOAT default=1.0 min=-100.0 max=100.0 step=0.01
- outputs: MODEL:MODEL

## LoraLoader|pysssss
module: custom_nodes.ComfyUI-Custom-Scripts | category: model/loaders
- required:
  - model: MODEL
  - clip: CLIP
  - lora_name: COMBO[FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, FC_KIERNAN_h3_face_v1.safetensors, ... +48]
  - strength_model: FLOAT default=1.0 min=-100.0 max=100.0 step=0.01
  - strength_clip: FLOAT default=1.0 min=-100.0 max=100.0 step=0.01
- optional:
  - prompt: STRING
- outputs: MODEL:MODEL, CLIP:CLIP, example:STRING

## LoraModelLoader
module: comfy_extras.nodes_train | category: model/loaders
- required:
  - model: MODEL
  - lora: LORA_MODEL
  - strength_model: FLOAT default=1.0 min=-100.0 max=100.0
  - bypass: BOOLEAN default=False
- outputs: model:MODEL

## LoraReduceRankKJ
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/lora
- required:
  - lora_name: COMBO[FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, FC_KIERNAN_h3_face_v1.safetensors, ... +48]
  - new_rank: INT default=8 min=1 max=4096 step=1
  - dynamic_method: COMBO[disabled, sv_ratio, sv_cumulative, sv_fro, sv_knee] default='disabled'
  - dynamic_param: FLOAT default=0.2 min=0.0 max=2.0 step=0.01
  - output_dtype: COMBO[match_original, fp16, bf16, fp32] default='match_original'
  - verbose: BOOLEAN default=True
- outputs: 

## LoraSave
module: comfy_extras.nodes_lora_extract | category: experimental
- required:
  - filename_prefix: STRING default='loras/ComfyUI_extracted_lora'
  - rank: INT default=8 min=1 max=4096 step=1
  - lora_type: COMBO[standard, full_diff]
  - bias_diff: BOOLEAN default=True
- optional:
  - model_diff: MODEL
  - text_encoder_diff: CLIP
- outputs: 

## LoraSelector
module: custom_nodes.ControlFlowUtils | category: 🐺 VykosX-ControlFlowUtils
- required:
  - lora_name: COMBO[aidmaNSFWunlock_v2.safetensors, bfs_head_v1_flux-klein_9b_step3750_rank64.safetensors, clothes_remover_v0.safetensors, FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, ... +48]
- optional:
  - run_after: * default=''
- outputs: LoRA:*

## LorasForFluxParams+
module: custom_nodes.ComfyUI_essentials | category: essentials/sampling
- required:
  - lora_1: COMBO[FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, FC_KIERNAN_h3_face_v1.safetensors, ... +48]
  - strength_model_1: STRING default='1.0'
- outputs: LORA_PARAMS:LORA_PARAMS

## LossGraphNode
module: comfy_extras.nodes_train | category: model/training
- required:
  - loss: LOSS_MAP
  - filename_prefix: STRING default='loss_graph'
- outputs: 

## LotusConditioning
module: comfy_extras.nodes_lotus | category: model/conditioning/lotus
- outputs: conditioning:CONDITIONING

## LTX25MultishotSampler
module: custom_nodes.ComfyUI-H3-Multishot | category: video/ltx
- required:
  - model: MODEL
  - clip: CLIP
  - video_vae: VAE
  - audio_vae: VAE
  - prompts: STRING default=''
  - negative: STRING default='pc game, console game, video game, cartoon, childish, ugly'
  - width: INT default=960 min=256 max=1920 step=32
  - height: INT default=544 min=256 max=1920 step=32
  - frames_per_shot: INT default=193 min=25 max=1441 step=8
  - shot_count: INT default=0 min=0 max=64
  - join: COMBO[continue (AV extend: seamless take), cut (voice extends, new picture), fresh (independent shots)] default='continue (AV extend: seamless take)'
  - overlap: INT default=3 min=1 max=12
  - seed: INT default=553010 min=0 max=18446744073709551615
  - seed_per_shot: BOOLEAN default=True
  - sampler_name: COMBO[euler, euler_cfg_pp, euler_ancestral, euler_ancestral_cfg_pp, heun, heunpp2, exp_heun_2_x0, exp_heun_2_x0_sde, dpm_2, dpm_2_ancestral, ... +35] default='euler_ancestral'
  - sigmas_pass1: STRING default='1.0, 0.99375, 0.9875, 0.98125, 0.975, 0.909375, 0.725, 0.421...'
  - two_pass: BOOLEAN default=True
  - sigmas_pass2: STRING default='0.85, 0.7250, 0.4219, 0.0'
  - video_cfg: FLOAT default=1.0 min=0.0 max=20.0 step=0.05
  - audio_cfg: FLOAT default=1.0 min=0.0 max=20.0 step=0.05
  - frame_rate: FLOAT default=24.0 min=12.0 max=60.0 step=1.0
  - save_every_shot: BOOLEAN default=False
- optional:
  - upscale_model: LATENT_UPSCALE_MODEL
  - start_image: IMAGE
  - shot_images: IMAGE
  - image_strength: FLOAT default=1.0 min=0.0 max=1.0 step=0.05
- outputs: images:IMAGE, audio:AUDIO, info:STRING

## LTX2_NAG
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/ltxv
- required:
  - model: MODEL
  - nag_scale: FLOAT default=11.0 min=0.0 max=100.0 step=0.001
  - nag_alpha: FLOAT default=0.25 min=0.0 max=1.0 step=0.001
  - nag_tau: FLOAT default=2.5 min=0.0 max=10.0 step=0.001
- optional:
  - nag_cond_video: CONDITIONING
  - nag_cond_audio: CONDITIONING
  - inplace: BOOLEAN default=True
- outputs: model:MODEL

## LTX2AttentionTunerPatch
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/ltxv
- required:
  - model: MODEL
  - blocks: STRING default=''
  - video_scale: FLOAT default=1.0 min=0.0 max=100 step=0.01
  - audio_scale: FLOAT default=1.0 min=0.0 max=100 step=0.01
  - audio_to_video_scale: FLOAT default=1.0 min=0.0 max=100 step=0.01
  - video_to_audio_scale: FLOAT default=1.0 min=0.0 max=100 step=0.01
  - triton_kernels: BOOLEAN default=True
- outputs: model:MODEL

## LTX2AudioLatentNormalizingSampling
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/ltxv
- required:
  - model: MODEL
  - audio_normalization_factors: STRING default='1,1,0.25,1,1,0.25,1,1'
- outputs: MODEL:MODEL

## LTX2BlockLoraSelect
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/ltxv
- required:
  - blocks.0.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.1.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.2.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.3.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.4.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.5.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.6.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.7.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.8.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.9.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.10.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.11.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.12.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.13.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.14.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.15.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.16.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.17.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.18.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.19.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.20.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.21.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.22.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.23.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.24.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.25.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.26.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.27.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.28.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.29.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.30.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.31.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.32.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.33.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.34.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.35.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.36.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.37.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.38.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.39.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.40.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.41.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.42.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.43.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.44.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.45.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.46.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - blocks.47.: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
- outputs: blocks:SELECTEDDITBLOCKS

## LTX2LoraLoaderAdvanced
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/ltxv
- required:
  - lora_name: COMBO[FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, FC_KIERNAN_h3_face_v1.safetensors, ... +48]
  - model: MODEL
  - strength_model: FLOAT default=1.0 min=-100.0 max=100.0 step=0.01
  - video: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - video_to_audio: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - audio: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - audio_to_video: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - other: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- optional:
  - opt_lora_path: STRING
  - blocks: SELECTEDDITBLOCKS
- outputs: model:MODEL, rank:STRING, loaded_keys_info:STRING

## LTX2MemoryEfficientSageAttentionPatch
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/ltxv
- required:
  - model: MODEL
  - triton_kernels: BOOLEAN default=True
- outputs: model:MODEL

## LTX2SamplingPreviewOverride
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/ltxv
- required:
  - model: MODEL
  - preview_rate: INT default=8 min=1 max=60 step=1
- optional:
  - latent_upscale_model: LATENT_UPSCALE_MODEL
  - vae: VAE
- outputs: MODEL:MODEL

## LTX2STGGuider
module: custom_nodes.10S-Comfy-nodes | category: 10S Nodes/Sampling
- required:
  - model: MODEL
  - positive: CONDITIONING
  - negative: CONDITIONING
  - sigmas: SIGMAS
  - cfg_per_step: STRING default='2.0, 1.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, ...'
  - stg_scale_per_step: STRING default='2.0, 1.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, ...'
  - stg_rescale_per_step: STRING default='1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, ...'
- optional:
  - cfg_mode: COMBO[per_step_list, sigma_curve] default='per_step_list'
  - cfg_min: FLOAT default=1.0 min=0.0 max=30.0 step=0.05
  - cfg_max: FLOAT default=3.0 min=0.0 max=30.0 step=0.05
  - stg_mode: COMBO[per_step_list, sigma_curve] default='per_step_list'
  - stg_min: FLOAT default=0.0 min=0.0 max=30.0 step=0.05
  - stg_max: FLOAT default=2.0 min=0.0 max=30.0 step=0.05
  - stg_rescale_mode: COMBO[per_step_list, sigma_curve] default='per_step_list'
  - stg_rescale_min: FLOAT default=1.0 min=0.0 max=2.0 step=0.05
  - stg_rescale_max: FLOAT default=1.0 min=0.0 max=2.0 step=0.05
  - block_indices: STRING default='14, 19'
  - skip_steps_sigma_threshold: FLOAT default=1.0 min=0.0 max=100.0 step=0.01
  - debug: BOOLEAN default=False
- outputs: GUIDER:GUIDER

## LTXActionAmplifier
module: custom_nodes.10S-Comfy-nodes | category: 10S Nodes/Conditioning
- required:
  - model: MODEL
  - clip: CLIP
  - positive: CONDITIONING
  - amplification_strength: FLOAT default=0.3 min=0.0 max=1.0 step=0.05
- optional:
  - action_vocabulary_text: STRING default='moving, walking, running, turning, lifting, reaching, pushin...'
  - scale_ceiling: FLOAT default=0.3 min=0.05 max=1.0 step=0.05
  - auto_threshold: COMBO[disabled, p90, p95, p98, p99] default='p95'
  - similarity_threshold: FLOAT default=0.55 min=0.0 max=1.0 step=0.01
  - similarity_sharpness: FLOAT default=16.0 min=1.0 max=64.0 step=0.5
  - amplification_floor: FLOAT default=0.3 min=0.0 max=0.9 step=0.05
  - top_k: INT default=3 min=1 max=16 step=1
  - bypass: BOOLEAN default=False
  - debug: BOOLEAN default=False
- outputs: MODEL:MODEL

## LtxApi25AudioToVideo
module: comfy_api_nodes.nodes_ltxv | category: partner/video/LTXV
- required:
  - audio: AUDIO
  - model: COMFY_DYNAMICCOMBO_V3
  - prompt: STRING default=''
  - seed: INT default=42 min=0 max=4294967295
- optional:
  - image: IMAGE
- outputs: VIDEO:VIDEO

## LtxApi25ImageToVideo
module: comfy_api_nodes.nodes_ltxv | category: partner/video/LTXV
- required:
  - image: IMAGE
  - model: COMFY_DYNAMICCOMBO_V3
  - prompt: STRING default=''
  - seed: INT default=42 min=0 max=4294967295
- optional:
  - last_frame: IMAGE
- outputs: VIDEO:VIDEO

## LtxApi25TextToVideo
module: comfy_api_nodes.nodes_ltxv | category: partner/video/LTXV
- required:
  - model: COMFY_DYNAMICCOMBO_V3
  - prompt: STRING default=''
  - seed: INT default=42 min=0 max=4294967295
- outputs: VIDEO:VIDEO

## LTXAVTextEncoderLoader
module: comfy_extras.nodes_lt_audio | category: model/loaders
- required:
  - text_encoder: COMBO[clip_l.safetensors, qwen3vl_32b_minimax_h3_int4_convrot.safetensors, qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors, qwen_3_4b.safetensors, qwen_3_8b_fp8mixed.safetensors, umt5_xxl_fp8_e4m3fn_scaled.safetensors]
  - ckpt_name: COMBO[]
  - device: COMBO[default, cpu]
- outputs: CLIP:CLIP

## LTXFaceDetector
module: custom_nodes.10S-Comfy-nodes | category: 10S Nodes/Identity
- required:
  - image: IMAGE
- optional:
  - padding: FLOAT default=0.15 min=0.0 max=0.5 step=0.05
  - fallback_bbox: STRING default=''
  - debug: BOOLEAN default=False
- outputs: face_bbox:STRING

## LTXLatentAnchor
module: custom_nodes.10S-Comfy-nodes | category: 10S Nodes/Identity
- required:
  - model: MODEL
- optional:
  - sigmas: SIGMAS
  - strength: FLOAT default=0.1 min=0.0 max=5.0 step=0.01
  - cache_at_step: INT default=6 min=0 max=100 step=1
  - similarity_threshold: FLOAT default=0.5 min=0.0 max=1.0 step=0.01
  - decay_with_distance: FLOAT default=0.0 min=0.0 max=1.0 step=0.05
  - bypass: BOOLEAN default=False
  - advanced_mode: BOOLEAN default=False
  - cache_mode: COMBO[schedule, live_extraction, manual_calls] default='schedule'
  - forwards_per_step: INT default=1 min=1 max=8 step=1
  - cache_warmup: INT default=144 min=0 max=5000 step=1
  - anchor_frame: INT default=0 min=0 max=256 step=1
  - depth_curve: COMBO[flat, ramp_up, ramp_down, late_focus, middle] default='flat'
  - block_index_filter: STRING default=''
  - debug: BOOLEAN default=False
- outputs: model:MODEL

## LTXLatentAnchorAware
module: custom_nodes.10S-Comfy-nodes | category: 10S Nodes/Identity
- required:
  - model: MODEL
- optional:
  - reference_image: IMAGE
  - vae: VAE
  - energy_latent: LATENT
  - sigmas: SIGMAS
  - strength: FLOAT default=0.1 min=0.0 max=5.0 step=0.01
  - cache_at_step: INT default=6 min=0 max=100 step=1
  - similarity_threshold: FLOAT default=0.5 min=0.0 max=1.0 step=0.01
  - decay_with_distance: FLOAT default=0.0 min=0.0 max=1.0 step=0.05
  - energy_threshold: FLOAT default=0.3 min=0.0 max=1.0 step=0.05
  - bypass: BOOLEAN default=False
  - debug: BOOLEAN default=False
  - advanced_mode: BOOLEAN default=False
  - cache_mode: COMBO[schedule, live_extraction, manual_calls] default='schedule'
  - forwards_per_step: INT default=1 min=1 max=8 step=1
  - cache_warmup: INT default=144 min=0 max=5000 step=1
  - anchor_frame: INT default=0 min=0 max=256 step=1
  - depth_curve: COMBO[flat, ramp_up, ramp_down, late_focus, middle] default='flat'
  - block_index_filter: STRING default=''
- outputs: model:MODEL

## LTXLikenessAnchor
module: custom_nodes.10S-Comfy-nodes | category: 10S Nodes/Identity
- required:
  - model: MODEL
  - strength: FLOAT default=0.1 min=0.0 max=0.8 step=0.01
- optional:
  - reference_info: REFERENCE_INFO
  - reference_source: COMBO[auto, guide, latent_frame_0] default='auto'
  - frame_0_bbox: STRING default=''
  - similarity_threshold: FLOAT default=0.5 min=0.0 max=1.0 step=0.01
  - decay_with_distance: FLOAT default=0.0 min=0.0 max=1.0 step=0.05
  - bypass: BOOLEAN default=False
  - debug: BOOLEAN default=False
  - advanced_mode: BOOLEAN default=False
  - depth_curve: COMBO[flat, ramp_up, ramp_down, late_focus, middle] default='flat'
  - block_index_filter: STRING default=''
  - similarity_sharpness: FLOAT default=8.0 min=1.0 max=32.0 step=0.5
  - override_face_bbox: STRING default=''
  - skip_when_sigma_above: FLOAT default=0.0 min=0.0 max=1.0 step=0.05
  - pull_mode: COMBO[directional, additive] default='directional'
  - late_block_falloff: FLOAT default=0.0 min=0.0 max=1.0 step=0.05
- outputs: MODEL:MODEL

## LTXLikenessCrop
module: custom_nodes.10S-Comfy-nodes | category: 10S Nodes/Identity
- required:
  - latent: LATENT
- optional:
  - reference_info: REFERENCE_INFO
  - debug: BOOLEAN default=False
- outputs: LATENT:LATENT

## LTXLikenessGuide
module: custom_nodes.10S-Comfy-nodes | category: 10S Nodes/Identity
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - latent: LATENT
  - image: IMAGE
- optional:
  - strength: FLOAT default=1.0 min=0.0 max=1.0 step=0.05
  - placement_mode: COMBO[silent_reference, keyframe] default='silent_reference'
  - face_detect: COMBO[auto, manual, none] default='auto'
  - reference_mask_mode: COMBO[whole_frame, bbox_only, bbox_softfade] default='bbox_softfade'
  - face_padding: FLOAT default=0.15 min=0.0 max=0.5 step=0.05
  - crf: INT default=29 min=0 max=51
  - blur_radius: INT default=0 min=0 max=7
  - interpolation: COMBO[lanczos, bislerp, nearest, bilinear, bicubic, area, nearest-exact] default='lanczos'
  - crop: COMBO[center, disabled] default='center'
  - attention_strength: FLOAT default=1.0 min=0.0 max=2.0 step=0.05
  - face_bbox_within_reference: STRING default=''
  - emit_latent: COMBO[passthrough, extended] default='passthrough'
  - debug: BOOLEAN default=False
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT, reference_info:REFERENCE_INFO

## LTXLikenessSemanticClamp
module: custom_nodes.10S-Comfy-nodes | category: 10S Nodes/Identity
- required:
  - model: MODEL
  - clip: CLIP
  - positive: CONDITIONING
  - suppression_strength: FLOAT default=0.5 min=0.0 max=1.0 step=0.05
- optional:
  - reference_info: REFERENCE_INFO
  - face_modifier_text: STRING default='smiling, frowning, laughing, open mouth, closed mouth, eyes ...'
  - similarity_threshold: FLOAT default=0.65 min=0.0 max=1.0 step=0.01
  - auto_threshold: COMBO[disabled, p90, p95, p98, p99] default='p95'
  - similarity_sharpness: FLOAT default=16.0 min=1.0 max=64.0 step=0.5
  - suppression_floor: FLOAT default=0.3 min=0.0 max=0.9 step=0.05
  - top_k: INT default=3 min=1 max=16 step=1
  - soft_edge_frac: FLOAT default=0.15 min=0.0 max=0.5 step=0.05
  - override_face_bbox: STRING default=''
  - bypass: BOOLEAN default=False
  - debug: BOOLEAN default=False
- outputs: MODEL:MODEL

## LTXLoraStackAV
module: custom_nodes.10S-Comfy-nodes | category: 10S Nodes/LoRA
- required:
  - model: MODEL
  - num_loras: INT default=1 min=1 max=12 step=1
- optional:
  - lora_1: COMBO[None, FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, ... +49] default='None'
  - strength_1: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - audio_weight_1: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - video_weight_1: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - lora_2: COMBO[None, FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, ... +49] default='None'
  - strength_2: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - audio_weight_2: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - video_weight_2: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - lora_3: COMBO[None, FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, ... +49] default='None'
  - strength_3: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - audio_weight_3: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - video_weight_3: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - lora_4: COMBO[None, FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, ... +49] default='None'
  - strength_4: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - audio_weight_4: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - video_weight_4: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - lora_5: COMBO[None, FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, ... +49] default='None'
  - strength_5: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - audio_weight_5: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - video_weight_5: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - lora_6: COMBO[None, FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, ... +49] default='None'
  - strength_6: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - audio_weight_6: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - video_weight_6: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - lora_7: COMBO[None, FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, ... +49] default='None'
  - strength_7: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - audio_weight_7: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - video_weight_7: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - lora_8: COMBO[None, FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, ... +49] default='None'
  - strength_8: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - audio_weight_8: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - video_weight_8: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - lora_9: COMBO[None, FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, ... +49] default='None'
  - strength_9: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - audio_weight_9: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - video_weight_9: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - lora_10: COMBO[None, FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, ... +49] default='None'
  - strength_10: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - audio_weight_10: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - video_weight_10: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - lora_11: COMBO[None, FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, ... +49] default='None'
  - strength_11: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - audio_weight_11: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - video_weight_11: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - lora_12: COMBO[None, FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, ... +49] default='None'
  - strength_12: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - audio_weight_12: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - video_weight_12: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
- outputs: MODEL:MODEL

## LTXModelInspector
module: custom_nodes.10S-Comfy-nodes | category: 10S Nodes/Identity
- required:
  - model: MODEL
- optional:
  - name_filter: STRING default=''
  - focus_path: STRING default='transformer_blocks.0'
  - max_modules_listed: INT default=100 min=1 max=4000 step=1
  - trace_path_contains: STRING default=''
  - max_modules_traced: INT default=8 min=0 max=200 step=1
  - trace_calls_per_module: INT default=1 min=1 max=10 step=1
  - print_top_level: BOOLEAN default=False
- outputs: model:MODEL

## LTXReferenceBypass
module: custom_nodes.10S-Comfy-nodes | category: 10S Nodes/LTX2
- required:
  - model: MODEL
- outputs: model:MODEL

## LTXReferenceConditioning
module: custom_nodes.10S-Comfy-nodes | category: 10S Nodes/LTX2
- required:
  - model: MODEL
  - vae: VAE
  - image: IMAGE
- optional:
  - target_latent: LATENT
  - strength: FLOAT default=1.0 min=0.0 max=2.0 step=0.05
  - position_mode: COMBO[reference, prefix_continuous] default='reference'
  - verbose: BOOLEAN default=False
- outputs: model:MODEL

## LTXReferenceEnable
module: custom_nodes.10S-Comfy-nodes | category: 10S Nodes/LTX2
- required:
  - model: MODEL
- optional:
  - zero_ref_timesteps: BOOLEAN default=False
  - verbose: BOOLEAN default=False
- outputs: model:MODEL

## LTXReferenceProbe
module: custom_nodes.10S-Comfy-nodes | category: 10S Nodes/Debug
- required:
  - model: MODEL
- outputs: model:MODEL, report:STRING

## LTXTextAttentionAmplifier
module: custom_nodes.10S-Comfy-nodes | category: 10S Nodes/Identity
- required:
  - model: MODEL
- optional:
  - text_amplification: FLOAT default=1.3 min=1.0 max=3.0 step=0.01
  - spatial_focus: FLOAT default=0.0 min=0.0 max=1.0 step=0.05
  - block_index_filter: STRING default=''
  - bypass: BOOLEAN default=False
  - debug: BOOLEAN default=False
- outputs: model:MODEL

## LTXTiledSampler
module: custom_nodes.10S-Comfy-nodes | category: 10S Nodes/Sampling
- required:
  - noise: NOISE
  - guider: GUIDER
  - sampler: SAMPLER
  - sigmas: SIGMAS
  - latent_image: LATENT
- optional:
  - bypass_tiling: BOOLEAN default=False
  - tile_axis: COMBO[auto, H, W] default='auto'
  - n_tiles: INT default=2 min=1 max=8 step=1
  - tile_overlap: INT default=8 min=0 max=32 step=1
  - max_size_for_no_tile: INT default=24 min=8 max=256 step=1
  - audio_pass: COMBO[passthrough, tile_carrying] default='passthrough'
  - audio_carrier_tile: COMBO[first, middle, last] default='first'
  - debug: BOOLEAN default=False
- outputs: output:LATENT, denoised_output:LATENT

## LTXVAddGeneratedKeyframes
module: comfy_extras.nodes_lt_keyframes | category: model/conditioning/ltxv
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - latent: LATENT
- optional:
  - interval_frames: INT default=24 min=1 max=1024
  - keyframes: LATENT
  - frame_indices: STRING default=''
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## LTXVAddGuide
module: comfy_extras.nodes_lt | category: model/conditioning/ltxv
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - latent: LATENT
  - image: IMAGE
  - frame_idx: INT default=0 min=-9999 max=9999
  - strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
- optional:
  - attention_mask: MASK
  - iclora_parameters: IC_LORA_PARAMETERS
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## LTXVAddGuideMulti
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/ltxv
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - latent: LATENT
  - num_guides: COMFY_DYNAMICCOMBO_V3
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## LTXVAddGuidesFromBatch
module: custom_nodes.ComfyUI-KJNodes | category: conditioning/ltxv
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - latent: LATENT
  - images: IMAGE
  - strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## LTXVAddLatentGuide
module: comfy_extras.nodes_lt | category: model/conditioning/ltxv
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - latent: LATENT
  - guiding_latent: LATENT
  - latent_idx: INT default=0 min=-9999 max=9999
  - strength: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- optional:
  - attention_mask: MASK
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## LTXVAudioVAEDecode
module: comfy_extras.nodes_lt_audio | category: model/latent/ltxv
- required:
  - samples: LATENT
  - audio_vae: VAE
- outputs: Audio:AUDIO

## LTXVAudioVAEEncode
module: comfy_extras.nodes_lt_audio | category: model/latent/ltxv
- required:
  - audio: AUDIO
  - audio_vae: VAE
- outputs: Audio Latent:LATENT

## LTXVAudioVAELoader
module: comfy_extras.nodes_lt_audio | category: model/loaders
- required:
  - ckpt_name: COMBO[]
- outputs: Audio VAE:VAE

## LTXVAudioVideoMask
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/ltxv
- required:
  - video_fps: FLOAT default=25 min=0.0 max=100.0 step=0.01
  - video_start_time: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - video_end_time: FLOAT default=5.0 min=0.0 max=10000.0 step=0.01
  - audio_start_time: FLOAT default=0.0 min=0.0 max=10000.0 step=0.01
  - audio_end_time: FLOAT default=5.0 min=0.0 max=10000.0 step=0.01
  - max_length: COMBO[truncate, pad, partial] default='truncate'
- optional:
  - video_latent: LATENT
  - audio_latent: LATENT
  - existing_mask_mode: COMBO[add, subtract, overwrite] default='add'
- outputs: video_latent:LATENT, audio_latent:LATENT

## LTXVChunkFeedForward
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/ltxv
- required:
  - model: MODEL
  - chunks: INT default=2 min=1 max=100 step=1
  - dim_threshold: INT default=4096 min=0 max=16384 step=256
- outputs: model:MODEL

## LTXVConcatAVLatent
module: comfy_extras.nodes_lt | category: model/latent/ltxv
- required:
  - video_latent: LATENT
  - audio_latent: LATENT
- outputs: latent:LATENT

## LTXVConditioning
module: comfy_extras.nodes_lt | category: model/conditioning/ltxv
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - frame_rate: FLOAT default=25.0 min=0.0 max=1000.0 step=0.01
- outputs: positive:CONDITIONING, negative:CONDITIONING

## LTXVContextWindows
module: comfy_extras.nodes_context_windows | category: model/patch/ltxv
- required:
  - model: MODEL
  - context_length: INT default=145 min=1 max=16384 step=8
  - context_overlap: INT default=40 min=0 step=8
  - context_schedule: COMBO[standard_static, standard_uniform, looped_uniform, batched] default='standard_uniform'
  - context_stride: INT default=1 min=1
  - closed_loop: BOOLEAN default=False
  - fuse_method: COMBO[pyramid, relative, flat, overlap-linear] default='pyramid'
  - freenoise: BOOLEAN default=True
  - retain_first_frame: BOOLEAN default=False
  - split_conds_to_windows: BOOLEAN default=False
- outputs: MODEL:MODEL

## LTXVCropGuides
module: comfy_extras.nodes_lt | category: model/conditioning/ltxv
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - latent: LATENT
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## LTXVDualCFGGuider
module: comfy_extras.nodes_lt | category: model/sampling/guiders
- required:
  - model: MODEL
  - positive: CONDITIONING
  - negative: CONDITIONING
  - video_cfg: FLOAT default=3.0 min=0.0 max=100.0 step=0.1
  - audio_cfg: FLOAT default=7.0 min=0.0 max=100.0 step=0.1
- outputs: GUIDER:GUIDER

## LTXVDurationPredictor
module: comfy_extras.nodes_lt | category: model/conditioning/ltxv
- required:
  - model: MODEL
  - positive: CONDITIONING
  - duration_head: MODEL_PATCH
  - frame_rate: FLOAT default=24.0 min=1.0 max=120.0 step=0.01
  - min_seconds: FLOAT default=1.0 min=0.5 max=120.0 step=0.1
  - max_seconds: FLOAT default=20.0 min=0.5 max=120.0 step=0.1
- outputs: num_frames:INT, seconds:FLOAT

## LTXVEmptyLatentAudio
module: comfy_extras.nodes_lt_audio | category: model/latent/ltxv
- required:
  - frames_number: INT default=97 min=1 max=1000 step=1
  - frame_rate: FLOAT,INT default=25.0 min=1.0 max=1000.0 step=0.01
  - batch_size: INT default=1 min=1 max=4096
  - audio_vae: VAE
- outputs: Latent:LATENT

## LTXVEnhanceAVideoKJ
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/ltxv
- required:
  - model: MODEL
  - latent: LATENT
  - weight: FLOAT default=4.0 min=0.0 max=100.0 step=0.001
- outputs: model:MODEL

## LTXVFreezeLatent
module: comfy_extras.nodes_lt_keyframes | category: model/latent/ltxv
- required:
  - latent: LATENT
- outputs: latent:LATENT

## LTXVGeneratedKeyframesToGuides
module: comfy_extras.nodes_lt_keyframes | category: model/conditioning/ltxv
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - latent: LATENT
  - keyframes: LATENT
  - strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
- optional:
  - override_frame_indices: STRING default=''
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## LTXVImgToVideo
module: comfy_extras.nodes_lt | category: model/conditioning/ltxv
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - image: IMAGE
  - width: INT default=768 min=64 max=16384 step=32
  - height: INT default=512 min=64 max=16384 step=32
  - length: INT default=97 min=9 max=16384 step=8
  - batch_size: INT default=1 min=1 max=4096
  - strength: FLOAT default=1.0 min=0.0 max=1.0
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## LTXVImgToVideoInplace
module: comfy_extras.nodes_lt | category: model/conditioning/ltxv
- required:
  - vae: VAE
  - image: IMAGE
  - latent: LATENT
  - strength: FLOAT default=1.0 min=0.0 max=1.0
  - bypass: BOOLEAN default=False
- outputs: latent:LATENT

## LTXVImgToVideoInplaceKJ
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/ltxv
- required:
  - vae: VAE
  - latent: LATENT
  - num_images: COMFY_DYNAMICCOMBO_V3
- outputs: latent:LATENT

## LTXVLatentUpsampler
module: comfy_extras.nodes_lt_upsampler | category: model/latent/ltxv
- required:
  - samples: LATENT
  - upscale_model: LATENT_UPSCALE_MODEL
  - vae: VAE
- outputs: LATENT:LATENT

## LTXVLatentUpsamplerTiled
module: custom_nodes.10S-Comfy-nodes | category: 10S Nodes/Latent
- required:
  - samples: LATENT
  - upscale_model: LATENT_UPSCALE_MODEL
  - vae: VAE
- optional:
  - tile_size: INT default=24 min=8 max=128 step=1
  - overlap: INT default=8 min=2 max=32 step=1
  - max_size_for_no_tile: INT default=32 min=8 max=256 step=1
  - rotate_for_landscape: BOOLEAN default=False
  - debug: BOOLEAN default=False
- outputs: LATENT:LATENT

## LTXVModalityGuidance
module: comfy_extras.nodes_lt | category: advanced/guidance
- required:
  - model: MODEL
  - modality_scale: FLOAT default=3.0 min=1.0 max=100.0 step=0.1
  - start_percent: FLOAT default=0.0 min=0.0 max=1.0 step=0.001
  - end_percent: FLOAT default=1.0 min=0.0 max=1.0 step=0.001
- outputs: MODEL:MODEL

## LTXVPreprocess
module: comfy_extras.nodes_lt | category: video/preprocessors
- required:
  - image: IMAGE
  - img_compression: INT default=35 min=0 max=100
- outputs: output_image:IMAGE

## LTXVReferenceAudio
module: comfy_extras.nodes_lt | category: model/conditioning/ltxv
- required:
  - model: MODEL
  - positive: CONDITIONING
  - negative: CONDITIONING
  - reference_audio: AUDIO
  - audio_vae: VAE
  - identity_guidance_scale: FLOAT default=3.0 min=0.0 max=100.0 step=0.01
  - start_percent: FLOAT default=0.0 min=0.0 max=1.0 step=0.001
  - end_percent: FLOAT default=1.0 min=0.0 max=1.0 step=0.001
- outputs: MODEL:MODEL, positive:CONDITIONING, negative:CONDITIONING

## LTXVScheduler
module: comfy_extras.nodes_lt | category: model/sampling/schedulers
- required:
  - steps: INT default=20 min=1 max=10000
  - max_shift: FLOAT default=2.05 min=0.0 max=100.0 step=0.01
  - base_shift: FLOAT default=0.95 min=0.0 max=100.0 step=0.01
  - stretch: BOOLEAN default=True
  - terminal: FLOAT default=0.1 min=0.0 max=0.99 step=0.01
- optional:
  - latent: LATENT
- outputs: SIGMAS:SIGMAS

## LTXVSeparateAVLatent
module: comfy_extras.nodes_lt | category: model/latent/ltxv
- required:
  - av_latent: LATENT
- outputs: video_latent:LATENT, audio_latent:LATENT

## LTXVSeparateGeneratedKeyframes
module: comfy_extras.nodes_lt_keyframes | category: model/conditioning/ltxv
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - latent: LATENT
  - keyframes_to_batch: BOOLEAN default=False
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT, keyframes:LATENT

## LTXVSpatioTemporalGuidance
module: comfy_extras.nodes_lt | category: advanced/guidance
- required:
  - model: MODEL
  - scale: FLOAT default=1.0 min=0.0 max=100.0 step=0.01
  - blocks: STRING default='29'
  - start_percent: FLOAT default=0.0 min=0.0 max=1.0 step=0.001
  - end_percent: FLOAT default=1.0 min=0.0 max=1.0 step=0.001
- outputs: MODEL:MODEL

## LumaConceptsNode
module: comfy_api_nodes.nodes_luma | category: partner/video/Luma
- required:
  - concept1: COMBO[None, truck_left, pan_right, pedestal_down, low_angle, pedestal_up, selfie, pan_left, roll_right, zoom_in, ... +25]
  - concept2: COMBO[None, truck_left, pan_right, pedestal_down, low_angle, pedestal_up, selfie, pan_left, roll_right, zoom_in, ... +25]
  - concept3: COMBO[None, truck_left, pan_right, pedestal_down, low_angle, pedestal_up, selfie, pan_left, roll_right, zoom_in, ... +25]
  - concept4: COMBO[None, truck_left, pan_right, pedestal_down, low_angle, pedestal_up, selfie, pan_left, roll_right, zoom_in, ... +25]
- optional:
  - luma_concepts: LUMA_CONCEPTS
- outputs: luma_concepts:LUMA_CONCEPTS

## LumaImageEditNode2
module: comfy_api_nodes.nodes_luma | category: partner/image/Luma
- required:
  - source: IMAGE
  - prompt: STRING default=''
  - model: COMFY_DYNAMICCOMBO_V3
  - seed: INT default=0 min=0 max=2147483647
- outputs: IMAGE:IMAGE

## LumaImageModifyNode
module: comfy_api_nodes.nodes_luma | category: partner/image/Luma
- required:
  - image: IMAGE
  - prompt: STRING default=''
  - image_weight: FLOAT default=0.1 min=0.0 max=0.98 step=0.01
  - model: COMBO[photon-1, photon-flash-1]
  - seed: INT default=0 min=0 max=18446744073709551615
- outputs: IMAGE:IMAGE

## LumaImageNode
module: comfy_api_nodes.nodes_luma | category: partner/image/Luma
- required:
  - prompt: STRING default=''
  - model: COMBO[photon-1, photon-flash-1]
  - aspect_ratio: COMBO[1:1, 16:9, 9:16, 4:3, 3:4, 21:9, 9:21] default='16:9'
  - seed: INT default=0 min=0 max=18446744073709551615
  - style_image_weight: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- optional:
  - image_luma_ref: LUMA_REF
  - style_image: IMAGE
  - character_image: IMAGE
- outputs: IMAGE:IMAGE

## LumaImageNode2
module: comfy_api_nodes.nodes_luma | category: partner/image/Luma
- required:
  - prompt: STRING default=''
  - model: COMFY_DYNAMICCOMBO_V3
  - seed: INT default=0 min=0 max=2147483647
- outputs: IMAGE:IMAGE

## LumaImageToVideoNode
module: comfy_api_nodes.nodes_luma | category: partner/video/Luma
- required:
  - prompt: STRING default=''
  - model: COMBO[ray-2, ray-flash-2, ray-1-6]
  - resolution: COMBO[540p, 720p, 1080p, 4k] default='540p'
  - duration: COMBO[5s, 9s]
  - loop: BOOLEAN default=False
  - seed: INT default=0 min=0 max=18446744073709551615
- optional:
  - first_image: IMAGE
  - last_image: IMAGE
  - luma_concepts: LUMA_CONCEPTS
- outputs: VIDEO:VIDEO

## LumaRay32ExtendVideoNode
module: comfy_api_nodes.nodes_luma | category: partner/video/Luma
- required:
  - source_generation_id: STRING default=''
  - direction: COMFY_DYNAMICCOMBO_V3
  - prompt: STRING default=''
  - resolution: COMBO[540p, 720p, 1080p] default='720p'
  - seed: INT default=0 min=0 max=18446744073709551615
- outputs: VIDEO:VIDEO, generation_id:STRING

## LumaRay32ImageToVideoNode
module: comfy_api_nodes.nodes_luma | category: partner/video/Luma
- required:
  - prompt: STRING default=''
  - resolution: COMBO[360p, 540p, 720p, 1080p] default='720p'
  - loop: BOOLEAN default=False
  - seed: INT default=0 min=0 max=18446744073709551615
- optional:
  - start_frame: IMAGE
  - end_frame: IMAGE
- outputs: VIDEO:VIDEO, generation_id:STRING

## LumaRay32KeyframeNode
module: comfy_api_nodes.nodes_luma | category: partner/video/Luma
- required:
  - image: IMAGE
  - position: COMFY_DYNAMICCOMBO_V3
- optional:
  - keyframes: LUMA_RAY32_KEYFRAME
- outputs: keyframes:LUMA_RAY32_KEYFRAME

## LumaRay32KeyframesToVideoNode
module: comfy_api_nodes.nodes_luma | category: partner/video/Luma
- required:
  - prompt: STRING default=''
  - resolution: COMBO[360p, 540p, 720p, 1080p] default='720p'
  - duration: COMBO[5s, 10s]
  - seed: INT default=0 min=0 max=18446744073709551615
  - keyframes: LUMA_RAY32_KEYFRAME
- outputs: VIDEO:VIDEO, generation_id:STRING

## LumaRay32TextToVideoNode
module: comfy_api_nodes.nodes_luma | category: partner/video/Luma
- required:
  - prompt: STRING default=''
  - aspect_ratio: COMBO[16:9, 9:16, 1:1, 4:3, 3:4, 21:9]
  - resolution: COMBO[360p, 540p, 720p, 1080p] default='720p'
  - duration: COMBO[5s, 10s]
  - loop: BOOLEAN default=False
  - seed: INT default=0 min=0 max=18446744073709551615
- outputs: VIDEO:VIDEO, generation_id:STRING

## LumaRay32VideoEditNode
module: comfy_api_nodes.nodes_luma | category: partner/video/Luma
- required:
  - video: VIDEO
  - prompt: STRING default=''
  - resolution: COMBO[360p, 540p, 720p, 1080p] default='720p'
  - strength: COMBO[auto, adhere_1, adhere_2, adhere_3, flex_1, flex_2, flex_3, reimagine_1, reimagine_2, reimagine_3] default='auto'
  - seed: INT default=0 min=0 max=18446744073709551615
- outputs: VIDEO:VIDEO, generation_id:STRING

## LumaRay32VideoReframeNode
module: comfy_api_nodes.nodes_luma | category: partner/video/Luma
- required:
  - video: VIDEO
  - prompt: STRING default=''
  - aspect_ratio: COMBO[16:9, 9:16, 1:1, 4:3, 3:4, 21:9]
  - resolution: COMBO[360p, 540p, 720p, 1080p] default='720p'
  - seed: INT default=0 min=0 max=18446744073709551615
- outputs: VIDEO:VIDEO, generation_id:STRING

## LumaReferenceNode
module: comfy_api_nodes.nodes_luma | category: partner/image/Luma
- required:
  - image: IMAGE
  - weight: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- optional:
  - luma_ref: LUMA_REF
- outputs: luma_ref:LUMA_REF

## LumaVideoNode
module: comfy_api_nodes.nodes_luma | category: partner/video/Luma
- required:
  - prompt: STRING default=''
  - model: COMBO[ray-2, ray-flash-2, ray-1-6]
  - aspect_ratio: COMBO[1:1, 16:9, 9:16, 4:3, 3:4, 21:9, 9:21] default='16:9'
  - resolution: COMBO[540p, 720p, 1080p, 4k] default='540p'
  - duration: COMBO[5s, 9s]
  - loop: BOOLEAN default=False
  - seed: INT default=0 min=0 max=18446744073709551615
- optional:
  - luma_concepts: LUMA_CONCEPTS
- outputs: VIDEO:VIDEO

## M-LSDPreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Line Extractors
- required:
  - image: IMAGE
- optional:
  - score_threshold: FLOAT default=0.1 min=0.01 max=2.0 step=0.01
  - dist_threshold: FLOAT default=0.1 min=0.01 max=20.0 step=0.01
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## MagnificImageRelightNode
module: comfy_api_nodes.nodes_magnific | category: partner/image/Magnific
- required:
  - image: IMAGE
  - prompt: STRING default=''
  - light_transfer_strength: INT default=100 min=0 max=100
  - style: COMBO[standard, darker_but_realistic, clean, smooth, brighter, contrasted_n_hdr, just_composition]
  - interpolate_from_original: BOOLEAN default=False
  - change_background: BOOLEAN default=True
  - preserve_details: BOOLEAN default=True
  - advanced_settings: COMFY_DYNAMICCOMBO_V3
- optional:
  - reference_image: IMAGE
- outputs: IMAGE:IMAGE

## MagnificImageSkinEnhancerNode
module: comfy_api_nodes.nodes_magnific | category: partner/image/Magnific
- required:
  - image: IMAGE
  - sharpen: INT default=0 min=0 max=100
  - smart_grain: INT default=2 min=0 max=100
  - mode: COMFY_DYNAMICCOMBO_V3
- outputs: IMAGE:IMAGE

## MagnificImageStyleTransferNode
module: comfy_api_nodes.nodes_magnific | category: partner/image/Magnific
- required:
  - image: IMAGE
  - reference_image: IMAGE
  - prompt: STRING default=''
  - style_strength: INT default=100 min=0 max=100
  - structure_strength: INT default=50 min=0 max=100
  - flavor: COMBO[faithful, gen_z, psychedelia, detaily, clear, donotstyle, donotstyle_sharp]
  - engine: COMBO[balanced, definio, illusio, 3d_cartoon, colorful_anime, caricature, real, super_real, softy]
  - portrait_mode: COMFY_DYNAMICCOMBO_V3
  - fixed_generation: BOOLEAN default=True
- outputs: IMAGE:IMAGE

## MagnificImageUpscalerCreativeNode
module: comfy_api_nodes.nodes_magnific | category: partner/image/Magnific
- required:
  - image: IMAGE
  - prompt: STRING default=''
  - scale_factor: COMBO[2x, 4x, 8x, 16x]
  - optimized_for: COMBO[standard, soft_portraits, hard_portraits, art_n_illustration, videogame_assets, nature_n_landscapes, films_n_photography, 3d_renders, science_fiction_n_horror]
  - creativity: INT default=0 min=-10 max=10
  - hdr: INT default=0 min=-10 max=10
  - resemblance: INT default=0 min=-10 max=10
  - fractality: INT default=0 min=-10 max=10
  - engine: COMBO[automatic, magnific_illusio, magnific_sharpy, magnific_sparkle]
  - auto_downscale: BOOLEAN default=False
- outputs: IMAGE:IMAGE

## MagnificImageUpscalerPreciseV2Node
module: comfy_api_nodes.nodes_magnific | category: partner/image/Magnific
- required:
  - image: IMAGE
  - scale_factor: COMBO[2x, 4x, 8x, 16x]
  - flavor: COMBO[sublime, photo, photo_denoiser]
  - sharpen: INT default=7 min=0 max=100
  - smart_grain: INT default=7 min=0 max=100
  - ultra_detail: INT default=30 min=0 max=100
  - auto_downscale: BOOLEAN default=False
- outputs: IMAGE:IMAGE

## Mahiro
module: comfy_extras.nodes_mahiro | category: experimental
- required:
  - model: MODEL
- outputs: patched_model:MODEL

## MakeTrainingDataset
module: comfy_extras.nodes_dataset | category: model/training
- required:
  - images: IMAGE
  - vae: VAE
  - clip: CLIP
- optional:
  - texts: STRING
- outputs: latents:LATENT, conditioning:CONDITIONING

## Manga2Anime_LineArt_Preprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Line Extractors
- required:
  - image: IMAGE
- optional:
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## ManualSigmas
module: comfy_extras.nodes_custom_sampler | category: model/sampling/sigmas
- required:
  - sigmas: STRING default='1, 0.5'
- outputs: SIGMAS:SIGMAS

## MarigoldV2PostProcess
module: comfy_extras.nodes_marigold | category: image/geometry estimation
- required:
  - image: IMAGE
  - prediction: COMBO[depth, normals, albedo]
- outputs: IMAGE:IMAGE

## MaskBatch+
module: custom_nodes.ComfyUI_essentials | category: essentials/mask batch
- required:
  - mask1: MASK
  - mask2: MASK
- outputs: MASK:MASK

## MaskBatchMulti
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking
- required:
  - inputcount: INT default=2 min=2 max=1000 step=1
  - mask_1: MASK
  - mask_2: MASK
- outputs: masks:MASK

## MaskBlur+
module: custom_nodes.ComfyUI_essentials | category: essentials/mask
- required:
  - mask: MASK
  - amount: INT default=6 min=0 max=256 step=1
  - device: COMBO[auto, cpu, gpu]
- outputs: MASK:MASK

## MaskBoundingBox+
module: custom_nodes.ComfyUI_essentials | category: essentials/mask
- required:
  - mask: MASK
  - padding: INT default=0 min=0 max=4096 step=1
  - blur: INT default=0 min=0 max=256 step=1
- optional:
  - image_optional: IMAGE
- outputs: MASK:MASK, IMAGE:IMAGE, x:INT, y:INT, width:INT, height:INT

## MaskComposite
module: comfy_extras.nodes_mask | category: image/mask
- required:
  - destination: MASK
  - source: MASK
  - x: INT default=0 min=0 max=16384 step=1
  - y: INT default=0 min=0 max=16384 step=1
  - operation: COMBO[multiply, add, subtract, and, or, xor]
- outputs: MASK:MASK

## MaskExpandBatch+
module: custom_nodes.ComfyUI_essentials | category: essentials/mask batch
- required:
  - mask: MASK
  - size: INT default=16 min=1 step=1
  - method: COMBO[expand, repeat all, repeat first, repeat last]
- outputs: MASK:MASK

## MaskFix+
module: custom_nodes.ComfyUI_essentials | category: essentials/mask
- required:
  - mask: MASK
  - erode_dilate: INT default=0 min=-256 max=256 step=1
  - fill_holes: INT default=0 min=0 max=128 step=1
  - remove_isolated_pixels: INT default=0 min=0 max=32 step=1
  - smooth: INT default=0 min=0 max=256 step=1
  - blur: INT default=0 min=0 max=256 step=1
- outputs: MASK:MASK

## MaskFlip+
module: custom_nodes.ComfyUI_essentials | category: essentials/mask
- required:
  - mask: MASK
  - axis: COMBO[x, y, xy]
- outputs: MASK:MASK

## MaskFromBatch+
module: custom_nodes.ComfyUI_essentials | category: essentials/mask batch
- required:
  - mask: MASK
  - start: INT default=0 min=0 step=1
  - length: INT default=1 min=1 step=1
- outputs: MASK:MASK

## MaskFromColor+
module: custom_nodes.ComfyUI_essentials | category: essentials/mask
- required:
  - image: IMAGE
  - red: INT default=255 min=0 max=255 step=1
  - green: INT default=255 min=0 max=255 step=1
  - blue: INT default=255 min=0 max=255 step=1
  - threshold: INT default=0 min=0 max=127 step=1
- outputs: MASK:MASK

## MaskFromList+
module: custom_nodes.ComfyUI_essentials | category: essentials/mask
- required:
  - width: INT default=32 min=0 max=16384 step=8
  - height: INT default=32 min=0 max=16384 step=8
- optional:
  - values: * default=0.0 min=0.0 max=1.0
  - str_values: STRING default=''
- outputs: MASK:MASK

## MaskFromRGBCMYBW+
module: custom_nodes.ComfyUI_essentials | category: essentials/mask
- required:
  - image: IMAGE
  - threshold_r: FLOAT default=0.15 min=0.0 max=1 step=0.01
  - threshold_g: FLOAT default=0.15 min=0.0 max=1 step=0.01
  - threshold_b: FLOAT default=0.15 min=0.0 max=1 step=0.01
- outputs: red:MASK, green:MASK, blue:MASK, cyan:MASK, magenta:MASK, yellow:MASK, black:MASK, white:MASK

## MaskFromSegmentation+
module: custom_nodes.ComfyUI_essentials | category: essentials/mask
- required:
  - image: IMAGE
  - segments: INT default=6 min=1 max=16 step=1
  - remove_isolated_pixels: INT default=0 min=0 max=32 step=1
  - remove_small_masks: FLOAT default=0.0 min=0.0 max=1.0 step=0.01
  - fill_holes: BOOLEAN default=False
- outputs: MASK:MASK

## MaskOptFlow
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Optical Flow
- required:
  - optical_flow: OPTICAL_FLOW
  - mask: MASK
- outputs: OPTICAL_FLOW:OPTICAL_FLOW, PREVIEW_IMAGE:IMAGE

## MaskOrImageToWeight
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/weights
- required:
  - output_type: COMBO[list, pandas series, tensor, string] default='list'
- optional:
  - images: IMAGE
  - masks: MASK
- outputs: FLOAT:FLOAT, STRING:STRING

## MaskPreview
module: comfy_extras.nodes_mask | category: image/mask
- required:
  - mask: MASK
- outputs: mask:MASK

## MaskPreview+
module: custom_nodes.ComfyUI_essentials | category: essentials/mask
- required:
  - mask: MASK
- outputs: images:IMAGE

## MaskSmooth+
module: custom_nodes.ComfyUI_essentials | category: essentials/mask
- required:
  - mask: MASK
  - amount: INT default=0 min=0 max=127 step=1
- outputs: MASK:MASK

## MaskToImage
module: comfy_extras.nodes_mask | category: image/mask
- required:
  - mask: MASK
- outputs: IMAGE:IMAGE

## MathExpression|pysssss
module: custom_nodes.ComfyUI-Custom-Scripts | category: utils
- required:
  - expression: STRING
- optional:
  - a: *
  - b: *
  - c: *
- outputs: INT:INT, FLOAT:FLOAT

## MediaPipe-FaceMeshPreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Faces and Poses Estimators
- required:
  - image: IMAGE
- optional:
  - max_faces: INT default=10 min=1 max=50 step=1
  - min_confidence: FLOAT default=0.5 min=0.1 max=1 step=0.01
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## MediaPipeFaceLandmarker
module: comfy_extras.nodes_mediapipe | category: image/detection
- required:
  - face_detection_model: FACE_DETECTION_MODEL
  - image: IMAGE
  - detector_variant: COMBO[short, full, both] default='short'
  - num_faces: INT default=1 min=0 max=16 step=1
  - min_confidence: FLOAT default=0.5 min=0.0 max=1.0 step=0.01
  - missing_frame_fallback: COMBO[empty, previous, interpolate] default='empty'
- outputs: face_landmarks:FACE_LANDMARKS, bboxes:BOUNDING_BOX

## MediaPipeFaceMask
module: comfy_extras.nodes_mediapipe | category: image/detection
- required:
  - face_landmarks: FACE_LANDMARKS
  - regions: COMFY_DYNAMICCOMBO_V3
- outputs: MASK:MASK

## MediaPipeFaceMeshVisualize
module: comfy_extras.nodes_mediapipe | category: image/detection
- required:
  - face_landmarks: FACE_LANDMARKS
  - connections: COMFY_DYNAMICCOMBO_V3
  - color: COLOR default='#00ff00'
  - thickness: INT default=1 min=0 max=8 step=1
  - point_size: INT default=2 min=0 max=16 step=1
- optional:
  - image: IMAGE
- outputs: IMAGE:IMAGE

## MemoryStorage
module: custom_nodes.ControlFlowUtils | category: 🐺 VykosX-ControlFlowUtils
- required:
  - Name: STRING
- optional:
  - Input: *
  - Reset: BOOLEAN
  - AcceptNulls: BOOLEAN
- outputs: Output:*

## MergeImageChannels
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - red: IMAGE
  - green: IMAGE
  - blue: IMAGE
- optional:
  - alpha: MASK default=None
- outputs: image:IMAGE

## MergeImageLists
module: comfy_extras.nodes_dataset | category: image/batch
- required:
  - images: IMAGE
- outputs: images:IMAGE

## MergeMeshes
module: comfy_extras.nodes_save_3d | category: 3d/mesh
- required:
  - meshes: COMFY_AUTOGROW_V3
- outputs: mesh:MESH

## MergeSplat
module: comfy_extras.nodes_gaussian_splat | category: 3d/splat
- required:
  - splats: COMFY_AUTOGROW_V3
- outputs: splat:SPLAT

## MergeTextLists
module: comfy_extras.nodes_dataset | category: text
- required:
  - texts: STRING
- outputs: texts:STRING

## MeshGraphormer+ImpactDetector-DepthMapPreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Normal and Depth Estimators
- required:
  - image: IMAGE
  - bbox_detector: BBOX_DETECTOR
- optional:
  - bbox_threshold: FLOAT default=0.5 min=0.1 max=1 step=0.01
  - bbox_dilation: INT default=10 min=-512 max=512 step=1
  - bbox_crop_factor: FLOAT default=3.0 min=1.0 max=10.0 step=0.01
  - drop_size: INT default=10 min=1 max=16384 step=1
  - mask_bbox_padding: INT default=30 min=0 max=100 step=1
  - mask_type: COMBO[based_on_depth, tight_bboxes, original] default='based_on_depth'
  - mask_expand: INT default=5 min=-16384 max=16384 step=1
  - rand_seed: INT default=88 min=0 max=18446744073709551615 step=1
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE, INPAINTING_MASK:MASK

## MeshGraphormer-DepthMapPreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Normal and Depth Estimators
- required:
  - image: IMAGE
- optional:
  - mask_bbox_padding: INT default=30 min=0 max=100
  - resolution: INT default=512 min=64 max=16384 step=64
  - mask_type: COMBO[based_on_depth, tight_bboxes, original] default='based_on_depth'
  - mask_expand: INT default=5 min=-16384 max=16384 step=1
  - rand_seed: INT default=88 min=0 max=18446744073709551615 step=1
  - detect_thr: FLOAT default=0.6 min=0.1 max=1 step=0.01
  - presence_thr: FLOAT default=0.6 min=0.1 max=1 step=0.01
- outputs: IMAGE:IMAGE, INPAINTING_MASK:MASK

## MeshSmoothNormals
module: comfy_extras.nodes_mesh_postprocess | category: 3d/mesh
- required:
  - mesh: MESH
  - crease_angle: FLOAT default=180.0 min=0.0 max=180.0 step=1.0
- outputs: mesh:MESH

## MeshTextureToImage
module: comfy_extras.nodes_mesh_postprocess | category: 3d/texturing
- required:
  - mesh: MESH
- outputs: base_color:IMAGE, metallic:IMAGE, roughness:IMAGE, occlusion:IMAGE, normal_map:IMAGE

## MeshToFile3D
module: comfy_extras.nodes_save_3d | category: 3d
- required:
  - mesh: MESH
- outputs: model_3d:FILE_3D_GLB

## MeshyAnimateModelNode
module: comfy_api_nodes.nodes_meshy | category: partner/3d/Meshy
- required:
  - rig_task_id: MESHY_RIGGED_TASK_ID
  - action_id: INT default=0 min=0 max=696
- outputs: model_file:STRING, GLB:FILE_3D_GLB, FBX:FILE_3D_FBX

## MeshyImageToModelNode
module: comfy_api_nodes.nodes_meshy | category: partner/3d/Meshy
- required:
  - model: COMBO[meshy-7.1, meshy-7, meshy-6, latest]
  - image: IMAGE
  - should_remesh: COMFY_DYNAMICCOMBO_V3
  - symmetry_mode: COMBO[auto, on, off]
  - should_texture: COMFY_DYNAMICCOMBO_V3
  - pose_mode: COMBO[, A-pose, T-pose]
  - seed: INT default=0 min=0 max=2147483647
  - ultra_mode: BOOLEAN default=False
- optional:
  - ultra_resolution: COMBO[2k, 4k]
- outputs: model_file:STRING, meshy_task_id:MESHY_TASK_ID, GLB:FILE_3D_GLB, FBX:FILE_3D_FBX

## MeshyMultiImageToModelNode
module: comfy_api_nodes.nodes_meshy | category: partner/3d/Meshy
- required:
  - model: COMBO[meshy-7.1, meshy-7, meshy-6, latest]
  - images: COMFY_AUTOGROW_V3
  - should_remesh: COMFY_DYNAMICCOMBO_V3
  - symmetry_mode: COMBO[auto, on, off]
  - should_texture: COMFY_DYNAMICCOMBO_V3
  - pose_mode: COMBO[, A-pose, T-pose]
  - seed: INT default=0 min=0 max=2147483647
- optional:
  - ultra_mode: BOOLEAN default=False
- outputs: model_file:STRING, meshy_task_id:MESHY_TASK_ID, GLB:FILE_3D_GLB, FBX:FILE_3D_FBX

## MeshyRefineNode
module: comfy_api_nodes.nodes_meshy | category: partner/3d/Meshy
- required:
  - model: COMBO[meshy-7.1, meshy-7, meshy-6, latest]
  - meshy_task_id: MESHY_TASK_ID
  - enable_pbr: BOOLEAN default=False
  - texture_prompt: STRING default=''
  - texture_resolution: COMBO[2k, 4k, 8k]
- optional:
  - texture_image: IMAGE
- outputs: model_file:STRING, meshy_task_id:MESHY_TASK_ID, GLB:FILE_3D_GLB, FBX:FILE_3D_FBX

## MeshyRigModelNode
module: comfy_api_nodes.nodes_meshy | category: partner/3d/Meshy
- required:
  - meshy_task_id: MESHY_TASK_ID
  - height_meters: FLOAT default=1.7 min=0.1 max=15.0
- optional:
  - texture_image: IMAGE
- outputs: model_file:STRING, rig_task_id:MESHY_RIGGED_TASK_ID, GLB:FILE_3D_GLB, FBX:FILE_3D_FBX

## MeshyTextToModelNode
module: comfy_api_nodes.nodes_meshy | category: partner/3d/Meshy
- required:
  - model: COMBO[meshy-7.1, meshy-7, meshy-6, latest]
  - prompt: STRING default=''
  - style: COMBO[realistic]
  - should_remesh: COMFY_DYNAMICCOMBO_V3
  - symmetry_mode: COMBO[auto, on, off]
  - pose_mode: COMBO[, A-pose, T-pose]
  - seed: INT default=0 min=0 max=2147483647
  - ultra_mode: BOOLEAN default=False
- optional:
  - ultra_resolution: COMBO[2k, 4k]
- outputs: model_file:STRING, meshy_task_id:MESHY_TASK_ID, GLB:FILE_3D_GLB, FBX:FILE_3D_FBX

## MeshyTextureMultiViewNode
module: comfy_api_nodes.nodes_meshy | category: partner/3d/Meshy
- required:
  - model: COMBO[meshy-7]
  - meshy_task_id: MESHY_TASK_ID
  - multiview_images: COMFY_AUTOGROW_V3
  - enable_original_uv: BOOLEAN default=True
  - pbr: BOOLEAN default=False
  - texture_resolution: COMBO[2k, 4k, 8k]
- outputs: model_file:STRING, meshy_task_id:MESHY_TASK_ID, GLB:FILE_3D_GLB, FBX:FILE_3D_FBX

## MeshyTextureNode
module: comfy_api_nodes.nodes_meshy | category: partner/3d/Meshy
- required:
  - model: COMBO[meshy-7, meshy-6, latest]
  - meshy_task_id: MESHY_TASK_ID
  - enable_original_uv: BOOLEAN default=True
  - pbr: BOOLEAN default=False
  - text_style_prompt: STRING default=''
  - texture_resolution: COMBO[2k, 4k, 8k]
- optional:
  - image_style: IMAGE
- outputs: model_file:STRING, meshy_task_id:MESHY_TASK_ID, GLB:FILE_3D_GLB, FBX:FILE_3D_FBX

## Metadata comparator [Crystools]
module: custom_nodes.ComfyUI-Crystools | category: crystools 🪛/Metadata
- required:
  - metadata_raw_old: METADATA_RAW
  - metadata_raw_new: METADATA_RAW
  - what: COMBO[Prompt, Workflow, Fileinfo]
- outputs: diff:JSON

## Metadata extractor [Crystools]
module: custom_nodes.ComfyUI-Crystools | category: crystools 🪛/Metadata
- required:
  - metadata_raw: METADATA_RAW
- outputs: prompt:JSON, workflow:JSON, file info:JSON, raw to JSON:JSON, raw to property:STRING, raw to csv:STRING

## MetaMuseImageEditApi
module: comfy_api_nodes.nodes_meta | category: partner/image/Meta
- required:
  - model: COMFY_DYNAMICCOMBO_V3
- outputs: IMAGE:IMAGE

## MetaMuseImageTextToImageApi
module: comfy_api_nodes.nodes_meta | category: partner/image/Meta
- required:
  - model: COMFY_DYNAMICCOMBO_V3
- outputs: IMAGE:IMAGE

## Metric3D-DepthMapPreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Normal and Depth Estimators
- required:
  - image: IMAGE
- optional:
  - backbone: COMBO[vit-small, vit-large, vit-giant2] default='vit-small'
  - fx: INT default=1000 min=1 max=16384 step=1
  - fy: INT default=1000 min=1 max=16384 step=1
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## Metric3D-NormalMapPreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Normal and Depth Estimators
- required:
  - image: IMAGE
- optional:
  - backbone: COMBO[vit-small, vit-large, vit-giant2] default='vit-small'
  - fx: INT default=1000 min=1 max=16384 step=1
  - fy: INT default=1000 min=1 max=16384 step=1
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## MiDaS-DepthMapPreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Normal and Depth Estimators
- required:
  - image: IMAGE
- optional:
  - a: FLOAT default=6.283185307179586 min=0.0 max=15.707963267948966 step=0.01
  - bg_threshold: FLOAT default=0.1 min=0 max=1 step=0.01
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## MiDaS-NormalMapPreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Normal and Depth Estimators
- required:
  - image: IMAGE
- optional:
  - a: FLOAT default=6.283185307179586 min=0.0 max=15.707963267948966 step=0.01
  - bg_threshold: FLOAT default=0.1 min=0 max=1 step=0.01
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## MiniMaxH3AddGuide
module: comfy_extras.nodes_minimax_h3 | category: model/conditioning/minimax
- required:
  - positive: CONDITIONING
  - latent: LATENT
  - frame_idx: INT default=0 min=-9999 max=9999
- optional:
  - vae: VAE
  - audio_vae: VAE
  - image: IMAGE
  - audio: AUDIO
- outputs: positive:CONDITIONING

## MiniMaxH3AppendContinuation
module: custom_nodes.comfyui-minimax-h3-continuation | category: MiniMax H3/continuation
- required:
  - previous_av_latent: LATENT
  - sampled_window: LATENT
  - overlap_video_tokens: INT min=1
  - overlap_audio_tokens: INT min=1
  - transition_video_tokens: INT min=0
  - transition_audio_tokens: INT min=0
- outputs: latent:LATENT, total_length:INT

## MiniMaxH3Cache
module: custom_nodes.ComfyUI-DaSiWa-Nodes | category: DaSiWa/MiniMax H3
- required:
  - model: MODEL
  - reuse_threshold: FLOAT default=0.05 min=0.0 max=1.0 step=0.01
  - start_percent: FLOAT default=0.15 min=0.0 max=1.0 step=0.01
  - end_percent: FLOAT default=0.9 min=0.0 max=1.0 step=0.01
  - max_steps: INT default=2 min=1 max=10
  - device: COMBO[auto, cuda, cpu] default='auto'
  - verbose: BOOLEAN default=False
- outputs: MODEL:MODEL

## MiniMaxH3Director
module: custom_nodes.ComfyUI-DaSiWa-Nodes | category: DaSiWa/MiniMax H3
- required:
  - mode: COMBO[T2VA, I2VA, FL2VA, L2VA, REF2VA, Image Inpaint] default='FL2VA'
  - prompt: STRING default=''
  - width: INT default=1344 min=16 max=8192 step=16
  - height: INT default=768 min=16 max=8192 step=16
  - duration: FLOAT default=5.0 min=0.1 max=1000 step=0.01
  - ref_image_size: COMBO[match, max] default='match'
  - timeline_data: STRING default='{"version":1,"items":[],"prompt_blocks":[]}'
  - builder_state: STRING default=''
  - frame_rate: FLOAT default=24.0 min=0.1 max=240.0 step=0.01
- optional:
  - fl2va_model: MODEL
  - ref2va_model: MODEL
  - external_width_overwrite: INT min=1 max=8192 step=1
  - external_height_overwrite: INT min=1 max=8192 step=1
  - external_prompt_overwrite: STRING default=''
- outputs: guide:MINIMAX_H3_DIRECTOR_GUIDE, duration:INT, positive_prompt:STRING, width:INT, height:INT, model:MODEL, fl2va_requested:BOOLEAN, inpaint_requested:BOOLEAN, frame_rate:FLOAT

## MiniMaxH3DirectorGuide
module: custom_nodes.ComfyUI-DaSiWa-Nodes | category: DaSiWa/MiniMax H3
- required:
  - clip: CLIP
  - vae: VAE
  - guide: MINIMAX_H3_DIRECTOR_GUIDE
- optional:
  - audio_vae: VAE
- outputs: positive:CONDITIONING, latent:LATENT, continuity_context:DF_H3_CONTINUITY_CONTEXT

## MiniMaxH3EffectEmbeddings
module: custom_nodes.MiniMax-H3-Prompt-Rewriter-ComfyUI | category: MiniMax-H3
- required:
  - prompt: STRING
  - placement: COMBO[start of the description, top of the prompt, end of the prompt] default='start of the description'
- optional:
  - effects: STRING default='{}'
  - bypass: BOOLEAN default=False
- outputs: prompt:STRING, tokens:INT, findings:STRING

## MiniMaxH3Extender
module: custom_nodes.ComfyUI_MiniMax_H3_Extender | category: MiniMax H3
- required:
  - model: MODEL
  - clip: CLIP
  - vae: VAE
  - run_mode: COMBO[clip_by_clip, full_batch] default='clip_by_clip'
  - width: INT default=896 min=32 max=4096 step=32
  - height: INT default=576 min=32 max=4096 step=32
  - ref_image_size: COMBO[match, max] default='match'
  - steps: INT default=4 min=1 max=10000 step=1
  - sampler_name: COMBO[euler, euler_cfg_pp, euler_ancestral, euler_ancestral_cfg_pp, heun, heunpp2, exp_heun_2_x0, exp_heun_2_x0_sde, dpm_2, dpm_2_ancestral, ... +35] default='euler'
  - scheduler: COMBO[simple, sgm_uniform, karras, exponential, ddim_uniform, beta, normal, linear_quadratic, kl_optimal] default='simple'
  - denoise: FLOAT default=1.0 min=0.01 max=1.0 step=0.01
  - context_length: COMBO[22, 5, 39, 56] default='22'
  - audio_context_length: INT default=0 min=0 max=240 step=1
  - clips_json: STRING default='{"version":2,"clips":[{"id":"clip_1","name":"","prompt":"","...'
  - resolution_mode: COMBO[auto_from_ref, manual] default='auto_from_ref'
  - megapixels: FLOAT default=0.4 min=0.01 max=16.0 step=0.01
  - refs_json: STRING default='{"version":2,"refs":[null,null,null,null,null,null,null,null...'
  - generation_mode: COMBO[ref2va, fl2va] default='ref2va'
  - motion_context: BOOLEAN default=True
  - refine_enabled: BOOLEAN default=False
  - refine_scale: FLOAT default=1.5 min=1.0 max=2.0 step=0.05
  - refine_steps: INT default=4 min=1 max=100 step=1
  - refine_denoise: FLOAT default=0.3 min=0.01 max=1.0 step=0.01
- optional:
  - fl2va_model: MODEL
  - audio_vae: VAE
  - ref_audio: AUDIO
  - ref_audio_1: AUDIO
  - ref_audio_2: AUDIO
  - ref_audio_3: AUDIO
  - ref_video_1: IMAGE
  - ref_video_fps_1: FLOAT
  - ref_video_audio_1: AUDIO
  - ref_video_2: IMAGE
  - ref_video_fps_2: FLOAT
  - ref_video_audio_2: AUDIO
  - ref_video_3: IMAGE
  - ref_video_fps_3: FLOAT
  - ref_video_audio_3: AUDIO
  - ref_pack: H3_REF_PACK
  - prompt_pack: H3_PROMPT_PACK
  - sigmas: SIGMAS
  - continue_existing_video: VIDEO
- outputs: cache:H3_MOTION_DISK_CACHE, clip_count:INT, validated_count:INT, status:STRING, cache_size_mb:FLOAT, build:STRING

## MiniMaxH3FantasticEditComposite
module: custom_nodes.ComfyUI-Fantastic-MiniMaxH3-PromptBuilder | category: conditioning/video_models
- required:
  - images: IMAGE
  - references: H3_REFS
  - blend: INT default=8 min=0 max=64 step=1
  - max_size: INT default=0 min=0 max=8192 step=32
- outputs: images:IMAGE

## MiniMaxH3FantasticObjectMask
module: custom_nodes.ComfyUI-Fantastic-MiniMaxH3-PromptBuilder | category: conditioning/video_models
- required:
  - model: MODEL
  - clip: CLIP
  - video: STRING default=''
  - text: STRING default=''
  - points: STRING default=''
  - start: FLOAT default=0.0 min=0.0 max=36000.0 step=0.001
  - end: FLOAT default=0.0 min=0.0 max=36000.0 step=0.001
  - threshold: FLOAT default=0.5 min=0.05 max=0.95 step=0.05
  - max_objects: INT default=4 min=1 max=16
- optional:
  - mode: COMBO[replace, add, subtract] default='replace'
  - base: STRING default=''
  - every_frame: BOOLEAN default=False
  - subject: BOOLEAN default=False
  - max_frames: INT default=0 min=0 max=100000
  - pictures: STRING default=''
- outputs: 

## MiniMaxH3FantasticReferenceCache
module: custom_nodes.ComfyUI-Fantastic-MiniMaxH3-PromptBuilder | category: conditioning/video_models
- required:
  - model: MODEL
  - cache: COMBO[references, references and prompt] default='references'
  - refresh_every: INT default=2 min=2 max=16
  - store_8bit: BOOLEAN default=False
- outputs: MODEL:MODEL

## MiniMaxH3FantasticReferenceMap
module: custom_nodes.ComfyUI-Fantastic-MiniMaxH3-PromptBuilder | category: conditioning/video_models
- optional:
  - mods: H3_REF_MODS
  - references: H3_REFS
- outputs: reference_map:STRING

## MiniMaxH3FantasticRefModApply
module: custom_nodes.ComfyUI-Fantastic-MiniMaxH3-PromptBuilder | category: conditioning/video_models
- required:
  - conditioning: CONDITIONING
  - mods: H3_REF_MODS
  - retention: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - max_total_tokens: INT default=0 min=0 max=2147483647
- outputs: conditioning:CONDITIONING

## MiniMaxH3FantasticRefModCreate
module: custom_nodes.ComfyUI-Fantastic-MiniMaxH3-PromptBuilder | category: conditioning/video_models
- required:
  - name: STRING default=''
  - subfolder: STRING default=''
  - mode: COMBO[Full Reference, Compressed Reference] default='Full Reference'
  - ref_resolution: INT default=768 min=256 max=2048 step=32
  - grid: INT default=16 min=2 max=64 step=2
  - latent_frames: INT default=22 min=1 max=1024
  - refinement_steps: INT default=500 min=0 max=5000
  - max_tokens: INT default=5120 min=0 max=1048576
  - audio_max_seconds: FLOAT default=30.0 min=0.5 max=600.0 step=0.5
  - concept_type: COMBO[generic, identity, pose_motion, clothing, background, voice, singing, music_style, sound_fx, ambience, ... +1] default='generic'
  - description: STRING default=''
  - write_preview: BOOLEAN default=True
  - source: STRING default=''
- optional:
  - subject_name: STRING default=''
  - appearance: STRING default=''
  - voice_description: STRING default=''
  - retained_attributes: STRING default=''
  - image: IMAGE
  - audio: AUDIO
  - vae: VAE
  - audio_vae: VAE
- outputs: mods:H3_REF_MODS, saved:STRING

## MiniMaxH3FantasticRefModEdit
module: custom_nodes.ComfyUI-Fantastic-MiniMaxH3-PromptBuilder | category: conditioning/video_models
- required:
  - file: STRING default=''
  - frames: STRING default=''
  - add: STRING default=''
  - voice: STRING default=''
  - latent_frames: INT default=22 min=1 max=1024
  - audio_max_seconds: FLOAT default=30.0 min=0.5 max=600.0 step=0.5
  - save_as: STRING default=''
- optional:
  - vae: VAE
  - audio_vae: VAE
  - subject_name: STRING default=''
  - appearance: STRING default=''
  - voice_description: STRING default=''
  - retained_attributes: STRING default=''
  - stored_blur: STRING default=''
- outputs: saved:STRING

## MiniMaxH3FantasticRefModInspect
module: custom_nodes.ComfyUI-Fantastic-MiniMaxH3-PromptBuilder | category: conditioning/video_models
- required:
  - file: STRING default=''
  - view: COMBO[frames, video] default='frames'
  - strength: FLOAT default=1.0 min=0.0 max=1.0 step=0.05
  - audio_seconds: FLOAT default=30.0 min=0.5 max=600.0 step=0.5
- optional:
  - mods: H3_REF_MODS
  - index: INT default=0 min=0 max=10000
  - vae: VAE
  - audio_vae: VAE
  - stored_blur: STRING default=''
- outputs: details:STRING, frames:IMAGE, audio:AUDIO

## MiniMaxH3FantasticRefModStoreFrames
module: custom_nodes.ComfyUI-Fantastic-MiniMaxH3-PromptBuilder | category: conditioning/video_models
- required:
  - files: STRING default=''
  - vae: VAE
- outputs: 

## MiniMaxH3FantasticRefModTextEncode
module: custom_nodes.ComfyUI-Fantastic-MiniMaxH3-PromptBuilder | category: conditioning/video_models
- required:
  - clip: CLIP
  - prompt: STRING
  - width: INT default=1344 min=32 max=16384 step=32
  - height: INT default=768 min=32 max=16384 step=32
  - length: INT default=124 min=5 max=3600 step=17
  - ref_image_size: COMBO[match, max] default='match'
  - reference_fps: FLOAT default=24.0 min=1.0 max=120.0
  - max_total_tokens: INT default=0 min=0 max=2147483647
- optional:
  - mods: H3_REF_MODS
  - references: H3_REFS
  - vae: VAE
  - audio_vae: VAE
  - voice_description_at_label: BOOLEAN default=False
  - stack_pictures: COMBO[every 4th, up to N, all] default='every 4th'
  - stack_pictures_n: INT default=8 min=1 max=1024
- outputs: conditioning:CONDITIONING, reference_map:STRING, latent:LATENT

## MiniMaxH3FantasticVideoEditLatent
module: custom_nodes.ComfyUI-Fantastic-MiniMaxH3-PromptBuilder | category: conditioning/video_models
- required:
  - vae: VAE
  - images: IMAGE
  - mask: MASK
  - grow: INT default=16 min=0 max=256 step=1
  - keep_audio: BOOLEAN default=True
- optional:
  - audio_vae: VAE
  - audio: AUDIO
  - megapixels: FLOAT default=0.98 min=0.0 max=16.0 step=0.01
- outputs: latent:LATENT, width:INT, height:INT, length:INT

## MiniMaxH3FilenamePrefix
module: custom_nodes.ComfyUI-Fantastic-MiniMaxH3-PromptBuilder | category: conditioning/video_models
- required:
  - folder: STRING default=''
  - subfolder: STRING default=''
  - date_folder: COMBO[off, YYYY-MM-DD, YYYY_MM_DD, YYYYMMDD, YYYY-MM, YYYY/MM/DD, YYYY-MM-DD_HH-MM] default='YYYY-MM-DD'
  - filename: STRING default='vid'
- outputs: filename_prefix:STRING

## MiniMaxH3FunControlNetApply
module: comfy_extras.nodes_minimax_h3 | category: model/patch/minimax
- required:
  - model: MODEL
  - model_patch: MODEL_PATCH
  - vae: VAE
  - strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - start_percent: FLOAT default=0.0 min=0.0 max=1.0 step=0.001
  - end_percent: FLOAT default=1.0 min=0.0 max=1.0 step=0.001
- optional:
  - control_video: IMAGE
  - mask: MASK
  - source_video: IMAGE
- outputs: MODEL:MODEL

## MiniMaxH3GuidedContinuationWindow
module: custom_nodes.comfyui-minimax-h3-continuation | category: MiniMax H3/continuation
- required:
  - previous_av_latent: LATENT
  - overlap_frames: INT default=22 min=5 max=3600 step=17
  - extension_frames: INT default=119 min=17 max=3570 step=17
- outputs: latent:LATENT, window_length:INT, overlap_video_tokens:INT, overlap_audio_tokens:INT, transition_video_tokens:INT, transition_audio_tokens:INT

## MiniMaxH3GuidedWriter
module: custom_nodes.MiniMax-H3-Prompt-Rewriter-ComfyUI | category: MiniMax-H3
- required:
  - prompt: STRING default=''
  - model: COMBO[Qwen3.5-4B · 2.6 GB download · ~5 GB with the guide in context — smallest that still holds the format; start here on an 8 GB card, Qwen3.5-9B · 5.3 GB download · ~8 GB with the guide in context — best writing per gigabyte; lower gpu_layers if 8 GB is tight, Qwen3.5-9B Uncensored (HauhauCS) · 5.2 GB download · ~8 GB with the guide in context — abliterated fine-tune: does not refuse scenes the stock model declines to describe, Gemma 3 12B Instruct · 6.8 GB download · ~10 GB with the guide in context — non-Qwen alternative; its chat template takes no system role, which the node handles, Mistral Small 3.2 24B Instruct · 13.4 GB download · ~17 GB with the guide in context — for a 16 GB card and up, when the 9B's prose is not enough, Qwen3.8-27B Q2_K_XL · 9.2 GB download · ~13 GB with the guide in context — the 27B's prose on a 16 GB card; unsloth's dynamic 2-bit, rougher than the Q4 but still the biggest writer this side of it, Qwen3.8-27B Q3_K_XL · 12.2 GB download · ~16 GB with the guide in context — the middle road: most of the Q4's quality, three gigabytes less to hold, Qwen3.8-27B Q4_K_M · 15.3 GB download · ~19 GB with the guide in context — the strongest prose in the list, for a 24 GB card; newer than the rewriter's own base, but its extra layer is why the 27B LoRA cannot ride it, Qwen3.8-27B Q6_K_XL · 23.6 GB download · ~27 GB with the guide in context — near-lossless, for a 32 GB card - and little room for the video model beside it; lower gpu_layers if it will not fit, Hemmingway-1 Heretic IQ3_M (local) · 12.6 GB download · ~13-14 GB, fit untested on 16 GB — 5s-lock test 2026-10-16, ... +2]
  - task: COMBO[T2VA, I2VA, FL2VA, L2VA] default='T2VA'
  - resolution: COMBO[48:9, 32:9, 21:9, 16:9, 4:3, 1:1, 3:4, 9:16] default='16:9'
  - duration: FLOAT,INT default=10.0 min=0.1 max=600.0 step=0.1
  - greedy: BOOLEAN default=True
  - seed: INT default=42 min=0 max=4294967295
  - keep_model_loaded: BOOLEAN default=False
- optional:
  - aspect_ratio: STRING,COMBO default=''
  - reference_material: STRING default=''
  - options: H3_REWRITER_OPTIONS
  - bypass: BOOLEAN default=False
  - system_prompt: STRING default=''
  - repeat_last: BOOLEAN default=False
  - library_pick: STRING default=''
- outputs: rewritten_prompt:STRING, integrated_multimodal_description:STRING, overall_soundscape:STRING, non_diegetic_music:STRING

## MiniMaxH3GuidedWriterRef
module: custom_nodes.MiniMax-H3-Prompt-Rewriter-ComfyUI | category: MiniMax-H3
- required:
  - prompt: STRING default=''
  - reference_assets: STRING default=''
  - model: COMBO[Qwen3.5-4B · 2.6 GB download · ~5 GB with the guide in context — smallest that still holds the format; start here on an 8 GB card, Qwen3.5-9B · 5.3 GB download · ~8 GB with the guide in context — best writing per gigabyte; lower gpu_layers if 8 GB is tight, Qwen3.5-9B Uncensored (HauhauCS) · 5.2 GB download · ~8 GB with the guide in context — abliterated fine-tune: does not refuse scenes the stock model declines to describe, Gemma 3 12B Instruct · 6.8 GB download · ~10 GB with the guide in context — non-Qwen alternative; its chat template takes no system role, which the node handles, Mistral Small 3.2 24B Instruct · 13.4 GB download · ~17 GB with the guide in context — for a 16 GB card and up, when the 9B's prose is not enough, Qwen3.8-27B Q2_K_XL · 9.2 GB download · ~13 GB with the guide in context — the 27B's prose on a 16 GB card; unsloth's dynamic 2-bit, rougher than the Q4 but still the biggest writer this side of it, Qwen3.8-27B Q3_K_XL · 12.2 GB download · ~16 GB with the guide in context — the middle road: most of the Q4's quality, three gigabytes less to hold, Qwen3.8-27B Q4_K_M · 15.3 GB download · ~19 GB with the guide in context — the strongest prose in the list, for a 24 GB card; newer than the rewriter's own base, but its extra layer is why the 27B LoRA cannot ride it, Qwen3.8-27B Q6_K_XL · 23.6 GB download · ~27 GB with the guide in context — near-lossless, for a 32 GB card - and little room for the video model beside it; lower gpu_layers if it will not fit, Hemmingway-1 Heretic IQ3_M (local) · 12.6 GB download · ~13-14 GB, fit untested on 16 GB — 5s-lock test 2026-10-16, ... +2]
  - resolution: COMBO[48:9, 32:9, 21:9, 16:9, 4:3, 1:1, 3:4, 9:16] default='16:9'
  - duration: FLOAT,INT default=10.0 min=0.1 max=600.0 step=0.1
  - greedy: BOOLEAN default=True
  - seed: INT default=42 min=0 max=4294967295
  - keep_model_loaded: BOOLEAN default=False
- optional:
  - aspect_ratio: STRING,COMBO default=''
  - options: H3_REWRITER_OPTIONS
  - bypass: BOOLEAN default=False
  - system_prompt: STRING default=''
  - repeat_last: BOOLEAN default=False
  - library_pick: STRING default=''
- outputs: rewritten_prompt:STRING, subject_definitions:STRING, summary:STRING, retention_analysis:STRING, detailed_description:STRING, overall_soundscape:STRING, non_diegetic_music:STRING

## MiniMaxH3GuidePrompt
module: custom_nodes.MiniMax-H3-Prompt-Rewriter-ComfyUI | category: MiniMax-H3
- required:
  - prompt: STRING default=''
  - task: COMBO[T2VA, I2VA, FL2VA, L2VA, Ref2VA] default='T2VA'
  - resolution: COMBO[48:9, 32:9, 21:9, 16:9, 4:3, 1:1, 3:4, 9:16] default='16:9'
  - duration: FLOAT,INT default=10.0 min=0.1 max=600.0 step=0.1
- optional:
  - aspect_ratio: STRING,COMBO default=''
  - reference_material: STRING default=''
  - auto_download: BOOLEAN default=True
  - format: COMBO[plain, chatml] default='plain'
- outputs: system_prompt:STRING, user_prompt:STRING, prompt:STRING

## MiniMaxH3ImageToVideo
module: comfy_extras.nodes_minimax_h3 | category: model/conditioning/minimax
- required:
  - clip: CLIP
  - vae: VAE
  - prompt: STRING
  - width: INT default=1344 min=32 max=16384 step=32
  - height: INT default=768 min=32 max=16384 step=32
  - length: INT default=124 min=5 max=3600 step=17
- optional:
  - first_frame: IMAGE
  - last_frame: IMAGE
- outputs: positive:CONDITIONING, LATENT:LATENT

## MiniMaxH3LatentBlur
module: custom_nodes.ComfyUI-MiniMaxH3_LatentUpscaler | category: latent/minimax_h3
- required:
  - samples: LATENT
  - radius: FLOAT default=0.0 min=0.0 max=64.0 step=0.05
- outputs: latent:LATENT

## MiniMaxH3LatentContrast
module: custom_nodes.ComfyUI-MiniMaxH3_LatentUpscaler | category: latent/minimax_h3
- required:
  - samples: LATENT
  - contrast: FLOAT default=1.0 min=0.0 max=3.0 step=0.05
  - preserve_norm: BOOLEAN default=True
- outputs: latent:LATENT

## MiniMaxH3LatentSharpen
module: custom_nodes.ComfyUI-MiniMaxH3_LatentUpscaler | category: latent/minimax_h3
- required:
  - samples: LATENT
  - amount: FLOAT default=0.2 min=0.0 max=2.0 step=0.05
  - radius: FLOAT default=1.0 min=0.05 max=8.0 step=0.05
- outputs: latent:LATENT

## MiniMaxH3LatentTailGuide
module: custom_nodes.comfyui-minimax-h3-continuation | category: MiniMax H3/continuation
- required:
  - positive: CONDITIONING
  - previous_av_latent: LATENT
  - target_av_latent: LATENT
  - overlap_video_tokens: INT min=1
  - overlap_audio_tokens: INT min=1
- outputs: positive:CONDITIONING

## MiniMaxH3LatentUpscaleCombined
module: custom_nodes.ComfyUI-MiniMaxH3_LatentUpscaler | category: latent/minimax_h3
- required:
  - samples: LATENT
  - method: COMBO[learned model, mamad8-learned, nearest-exact, nearest, bilinear, bicubic, area, bislerp] default='learned model'
  - learned_model: COMBO[h3_clean_latent_upscaler_film_epoch200.safetensors, h3_clean_latent_upscaler_v1_mamad8.safetensors]
  - model: MODEL
  - noise: NOISE
  - sigmas: SIGMAS
  - audio_denoise: FLOAT default=0.0 min=0.0 max=1.0 step=0.05
  - noise_resample: COMBO[upscale, independent] default='independent'
- optional:
  - learned_upscaler: H3_LATENT_UPSCALER
  - match_stats: FLOAT default=0.0 min=0.0 max=1.0 step=0.05
  - positive: CONDITIONING
  - negative: CONDITIONING
- outputs: latent:LATENT, positive:CONDITIONING, negative:CONDITIONING

## MinimaxH3LatentUpscaler3D
module: custom_nodes.Comfyui_Minimax_h3_latent_Upscaler | category: video/MinimaxH3
- required:
  - latent: *
  - model_name: COMBO[minimax_h3_latent_upscaler_3d_conv_v1_bf16.safetensors, minimax_h3_latent_upscaler_3d_fp16.safetensors]
  - mode: COMFY_DYNAMICCOMBO_V3
  - align: INT default=32 min=1 max=512 step=1
  - enable_temporal_chunking: BOOLEAN default=True
  - force_unload: BOOLEAN default=True
  - device: COMBO[cuda, rocm, cpu] default='cuda'
  - precision: COMBO[fp32, fp16, bf16] default='fp16'
- outputs: latent:*

## MinimaxH3LatentUpscalerNode2D
module: custom_nodes.Comfyui_Minimax_h3_latent_Upscaler | category: video/MinimaxH3
- required:
  - latent: LATENT
  - model_name: COMBO[minimax_h3_latent_upscaler_3d_conv_v1_bf16.safetensors, minimax_h3_latent_upscaler_3d_fp16.safetensors]
  - scale: FLOAT default=2.0 min=1.0 max=4.0 step=0.1
  - device: COMBO[cuda, cpu] default='cuda'
  - precision: COMBO[fp32, fp16, bf16] default='fp32'
- outputs: LATENT:LATENT

## MiniMaxH3LoraTriggers
module: custom_nodes.MiniMax-H3-Prompt-Rewriter-ComfyUI | category: MiniMax-H3
- required:
  - prompt: STRING
- optional:
  - triggers: STRING default='[]'
  - bypass: BOOLEAN default=False
- outputs: prompt:STRING, added:STRING, findings:STRING

## MiniMaxH3LQPackageLoad
module: custom_nodes.ComfyUI-MiniMaxH3_LatentUpscaler | category: latent/minimax_h3
- required:
  - selection_json: STRING default=''
  - load_source: COMBO[selection list, timeline order, timeline order and crops] default='selection list'
  - chunk_mode: COMBO[direct load, scene aware chunks (experimental)] default='direct load'
  - scene_threshold: FLOAT default=27.0 min=1.0 max=100.0 step=0.5
  - min_scene_seconds: FLOAT default=1.0 min=0.1 max=30.0 step=0.1
  - max_scene_seconds: FLOAT default=5.0 min=0.5 max=120.0 step=0.5
  - index: INT default=0 min=0 max=2147483647
  - index_mode: COMBO[increment, fixed] default='increment'
  - edit_json: STRING default=''
- outputs: latent:LATENT, positive:CONDITIONING, negative:CONDITIONING, meta:STRING, package_name:STRING, selected_count:INT, package_pipe:H3_PACKAGE_PIPE

## MiniMaxH3LQPackageSave
module: custom_nodes.ComfyUI-MiniMaxH3_LatentUpscaler | category: latent/minimax_h3
- required:
  - samples: LATENT
  - positive: CONDITIONING
  - filename_prefix: STRING default='h3_lq'
- optional:
  - negative: CONDITIONING
  - project: STRING default=''
  - note: STRING default=''
  - prompt: STRING default=''
  - seed: INT default=-1 min=-1 max=18446744073709551615
  - images: IMAGE
  - audio: AUDIO
- outputs: latent:LATENT, positive:CONDITIONING, negative:CONDITIONING, package_path:STRING

## MiniMaxH3MediaLoader
module: custom_nodes.ComfyUI-Fantastic-MiniMaxH3-PromptBuilder | category: conditioning/video_models
- required:
  - media_state: STRING default='[]'
- outputs: references:H3_REFS

## MiniMaxH3MotionContextDiskFinalDecode
module: custom_nodes.ComfyUI_MiniMax_H3_Extender | category: MiniMax H3
- required:
  - cache: H3_MOTION_DISK_CACHE
  - vae: VAE
  - audio_vae: VAE
  - fps: FLOAT default=24.0 min=1.0 max=240.0 step=0.001
  - filename_prefix: STRING default='MiniMax_H3_cached'
  - output_directory: STRING default=''
  - codec: COMBO[H.264, H.264 CPU (libx264), H.265 / HEVC, FFV1 lossless] default='H.264'
  - crf: INT default=17 min=0 max=51 step=1
  - preset: COMBO[ultrafast, superfast, veryfast, faster, fast, medium, slow] default='fast'
  - audio_bitrate: COMBO[128k, 192k, 256k, 320k] default='192k'
  - autoplay: BOOLEAN default=True
  - auto_save_project: BOOLEAN default=False
  - save_individual_clips: BOOLEAN default=False
- outputs: video:VIDEO, editor_batch:VIDEO_EDITOR_BATCH

## MiniMaxH3MotionContextDiskJoin
module: custom_nodes.ComfyUI_MiniMax_H3_Extender | category: MiniMax H3
- required:
  - samples: LATENT
  - validated: BOOLEAN default=False
  - run_mode: COMBO[full_batch, clip_by_clip] default='full_batch'
  - fps: FLOAT default=24.0 min=1.0 max=240.0 step=0.001
- optional:
  - previous_cache: H3_MOTION_DISK_CACHE
  - trim_frames: INT
- outputs: cache:H3_MOTION_DISK_CACHE, cached_samples:LATENT, clip_count:INT, frame_count:INT, status:STRING, cache_size_mb:FLOAT, cache_path:STRING, build:STRING

## MiniMaxH3MotionContextRAM
module: custom_nodes.ComfyUI_MiniMax_H3_Extender | category: MiniMax H3
- required:
  - conditioning: CONDITIONING
  - latent: LATENT
  - context_latent: LATENT
  - context_length: COMBO[22, 5, 39, 56] default='22'
  - audio_context_length: INT default=0 min=0 max=240 step=1
- outputs: conditioning:CONDITIONING, trim_frames:INT, video_context_tokens:INT, audio_context_tokens:INT, build:STRING

## MiniMaxH3MultiReferenceCaption
module: custom_nodes.MiniMax-H3-Prompt-Rewriter-ComfyUI | category: MiniMax-H3
- required:
  - model: COMBO[Qwen2.5-Omni-3B · 3.4 GB download · ~5 GB — image, audio and video in one small model; verified against this pack, Qwen2.5-Omni-7B · 5.8 GB download · ~8 GB — same modalities, better prose; step up when the 3B's captions are too plain, Dark Roast Q8 (vl_judge) · ~11 GB — local file, same weights llama-swap serves as vl_judge; vision only, Qwen3-VL-8B abliterated Q8 (local) · 11 GB download · ~12 GB — 5s-lock test, Dark Roast 9B Q8 (local) · 10.4 GB download · ~12 GB — 5s-lock test]
  - length: COMBO[brief, standard, detailed] default='standard'
  - seed: INT default=42 min=0 max=4294967295
- optional:
  - subjects: COMFY_AUTOGROW_V3
  - pictures: COMFY_AUTOGROW_V3
  - videos: COMFY_AUTOGROW_V3
  - audios: COMFY_AUTOGROW_V3
  - previous: STRING
  - clip: CLIP
  - options: H3_REWRITER_OPTIONS
  - enabled_mask: STRING default='{}'
  - max_frames: INT default=8 min=1 max=64
  - context_size: INT default=0 min=0 max=131072 step=1024
  - bypass: BOOLEAN default=False
  - reference_instructions: STRING default='{}'
  - repeat_last: BOOLEAN default=False
- outputs: reference_assets:STRING, captions:STRING

## MiniMaxH3Pass2StaggeredScheduler
module: custom_nodes.ComfyUI-MiniMaxH3_LatentUpscaler | category: latent/minimax_h3
- required:
  - model: MODEL
  - steps: INT default=4 min=1 max=100
  - denoise: FLOAT default=0.45 min=0.0 max=1.0 step=0.01
  - rho: FLOAT default=7.0 min=0.5 max=30.0 step=0.5
  - shape: COMBO[karras, exponential, polyexponential] default='karras'
- optional:
  - reference_steps: INT default=8 min=1 max=10000
  - base_scheduler: COMBO[simple, sgm_uniform, karras, exponential, ddim_uniform, beta, normal, linear_quadratic, kl_optimal] default='normal'
- outputs: SIGMAS:SIGMAS

## MiniMaxH3PromptBuilder
module: custom_nodes.ComfyUI-Fantastic-MiniMaxH3-PromptBuilder | category: conditioning/video_models
- required:
  - prompt_text: STRING default=''
  - builder_state: STRING default='{}'
- optional:
  - references: H3_REFS
  - mods: H3_REF_MODS
  - picture_1: IMAGE
  - picture_2: IMAGE
  - picture_3: IMAGE
  - picture_4: IMAGE
  - picture_5: IMAGE
  - picture_6: IMAGE
  - picture_7: IMAGE
  - picture_8: IMAGE
  - picture_9: IMAGE
  - video_1: IMAGE
  - video_2: IMAGE
  - video_3: IMAGE
  - video_audio_1: AUDIO
  - video_audio_2: AUDIO
  - video_audio_3: AUDIO
  - audio_1: AUDIO
  - audio_2: AUDIO
  - audio_3: AUDIO
- outputs: prompt:STRING, picture_1:IMAGE, picture_2:IMAGE, picture_3:IMAGE, picture_4:IMAGE, picture_5:IMAGE, picture_6:IMAGE, picture_7:IMAGE, picture_8:IMAGE, picture_9:IMAGE, video_1:IMAGE, video_2:IMAGE, video_3:IMAGE, video_audio_1:AUDIO, video_audio_2:AUDIO, video_audio_3:AUDIO, audio_1:AUDIO, audio_2:AUDIO, audio_3:AUDIO, references:H3_REFS, mods:H3_REF_MODS

## MiniMaxH3PromptCheck
module: custom_nodes.MiniMax-H3-Prompt-Rewriter-ComfyUI | category: MiniMax-H3
- required:
  - prompt: STRING
  - task: COMBO[T2VA, I2VA, FL2VA, L2VA, Ref2VA] default='T2VA'
  - duration: FLOAT,INT default=10.0 min=0.1 max=600.0 step=0.1
- optional:
  - options: H3_REWRITER_OPTIONS
  - references: COMFY_AUTOGROW_V3
- outputs: prompt:STRING, integrated_multimodal_description:STRING, subject_definitions:STRING, summary:STRING, retention_analysis:STRING, detailed_description:STRING, overall_soundscape:STRING, non_diegetic_music:STRING, findings:STRING

## MiniMaxH3PromptPackBridge
module: custom_nodes.ComfyUI_MiniMax_H3_Extender | category: MiniMax H3
- required:
  - prompt_1: STRING
- optional:
  - prompt_2: STRING
  - prompt_3: STRING
  - prompt_4: STRING
  - prompt_5: STRING
  - prompt_6: STRING
  - prompt_7: STRING
  - prompt_8: STRING
  - prompt_9: STRING
  - prompt_10: STRING
  - prompt_11: STRING
  - prompt_12: STRING
  - prompt_13: STRING
  - prompt_14: STRING
  - prompt_15: STRING
  - prompt_16: STRING
  - prompt_17: STRING
  - prompt_18: STRING
  - prompt_19: STRING
  - prompt_20: STRING
  - prompt_21: STRING
  - prompt_22: STRING
  - prompt_23: STRING
  - prompt_24: STRING
  - prompt_25: STRING
  - prompt_26: STRING
  - prompt_27: STRING
  - prompt_28: STRING
  - prompt_29: STRING
  - prompt_30: STRING
  - prompt_31: STRING
  - prompt_32: STRING
  - prompt_33: STRING
  - prompt_34: STRING
  - prompt_35: STRING
  - prompt_36: STRING
  - prompt_37: STRING
  - prompt_38: STRING
  - prompt_39: STRING
  - prompt_40: STRING
  - prompt_41: STRING
  - prompt_42: STRING
  - prompt_43: STRING
  - prompt_44: STRING
  - prompt_45: STRING
  - prompt_46: STRING
  - prompt_47: STRING
  - prompt_48: STRING
  - prompt_49: STRING
  - prompt_50: STRING
  - prompt_51: STRING
  - prompt_52: STRING
  - prompt_53: STRING
  - prompt_54: STRING
  - prompt_55: STRING
  - prompt_56: STRING
  - prompt_57: STRING
  - prompt_58: STRING
  - prompt_59: STRING
  - prompt_60: STRING
  - prompt_61: STRING
  - prompt_62: STRING
  - prompt_63: STRING
  - prompt_64: STRING
  - prompt_65: STRING
  - prompt_66: STRING
  - prompt_67: STRING
  - prompt_68: STRING
  - prompt_69: STRING
  - prompt_70: STRING
  - prompt_71: STRING
  - prompt_72: STRING
  - prompt_73: STRING
  - prompt_74: STRING
  - prompt_75: STRING
  - prompt_76: STRING
  - prompt_77: STRING
  - prompt_78: STRING
  - prompt_79: STRING
  - prompt_80: STRING
  - prompt_81: STRING
  - prompt_82: STRING
  - prompt_83: STRING
  - prompt_84: STRING
  - prompt_85: STRING
  - prompt_86: STRING
  - prompt_87: STRING
  - prompt_88: STRING
  - prompt_89: STRING
  - prompt_90: STRING
  - prompt_91: STRING
  - prompt_92: STRING
  - prompt_93: STRING
  - prompt_94: STRING
  - prompt_95: STRING
  - prompt_96: STRING
  - prompt_97: STRING
  - prompt_98: STRING
  - prompt_99: STRING
  - prompt_100: STRING
  - prompt_101: STRING
  - prompt_102: STRING
  - prompt_103: STRING
  - prompt_104: STRING
  - prompt_105: STRING
  - prompt_106: STRING
  - prompt_107: STRING
  - prompt_108: STRING
  - prompt_109: STRING
  - prompt_110: STRING
  - prompt_111: STRING
  - prompt_112: STRING
  - prompt_113: STRING
  - prompt_114: STRING
  - prompt_115: STRING
  - prompt_116: STRING
  - prompt_117: STRING
  - prompt_118: STRING
  - prompt_119: STRING
  - prompt_120: STRING
  - prompt_121: STRING
  - prompt_122: STRING
  - prompt_123: STRING
  - prompt_124: STRING
  - prompt_125: STRING
  - prompt_126: STRING
  - prompt_127: STRING
  - prompt_128: STRING
- outputs: prompt_pack:H3_PROMPT_PACK, prompt_count:INT

## MiniMaxH3PromptPresets
module: custom_nodes.MiniMax-H3-Prompt-Rewriter-ComfyUI | category: MiniMax-H3
- required:
  - preset: STRING default=''
- outputs: prompt:STRING, integrated_multimodal_description:STRING, overall_soundscape:STRING, non_diegetic_music:STRING, seconds:FLOAT, width:INT, height:INT, source:STRING

## MiniMaxH3PromptReducer
module: custom_nodes.MiniMax-H3-Prompt-Rewriter-ComfyUI | category: MiniMax-H3
- required:
  - prompt: STRING
  - model: COMBO[Qwen3.5-4B · 2.6 GB download · ~5 GB with the guide in context — smallest that still holds the format; start here on an 8 GB card, Qwen3.5-9B · 5.3 GB download · ~8 GB with the guide in context — best writing per gigabyte; lower gpu_layers if 8 GB is tight, Qwen3.5-9B Uncensored (HauhauCS) · 5.2 GB download · ~8 GB with the guide in context — abliterated fine-tune: does not refuse scenes the stock model declines to describe, Gemma 3 12B Instruct · 6.8 GB download · ~10 GB with the guide in context — non-Qwen alternative; its chat template takes no system role, which the node handles, Mistral Small 3.2 24B Instruct · 13.4 GB download · ~17 GB with the guide in context — for a 16 GB card and up, when the 9B's prose is not enough, Qwen3.8-27B Q2_K_XL · 9.2 GB download · ~13 GB with the guide in context — the 27B's prose on a 16 GB card; unsloth's dynamic 2-bit, rougher than the Q4 but still the biggest writer this side of it, Qwen3.8-27B Q3_K_XL · 12.2 GB download · ~16 GB with the guide in context — the middle road: most of the Q4's quality, three gigabytes less to hold, Qwen3.8-27B Q4_K_M · 15.3 GB download · ~19 GB with the guide in context — the strongest prose in the list, for a 24 GB card; newer than the rewriter's own base, but its extra layer is why the 27B LoRA cannot ride it, Qwen3.8-27B Q6_K_XL · 23.6 GB download · ~27 GB with the guide in context — near-lossless, for a 32 GB card - and little room for the video model beside it; lower gpu_layers if it will not fit, Hemmingway-1 Heretic IQ3_M (local) · 12.6 GB download · ~13-14 GB, fit untested on 16 GB — 5s-lock test 2026-10-16, ... +2]
  - detail: COMBO[idea, sentence, paragraph] default='sentence'
  - subjects: COMBO[as written, age and gender, impersonal] default='as written'
  - keep_camera: BOOLEAN default=False
  - keep_audio: BOOLEAN default=False
  - keep_style: BOOLEAN default=False
  - language: STRING default=''
  - greedy: BOOLEAN default=True
  - seed: INT default=42 min=0 max=4294967295
  - keep_model_loaded: BOOLEAN default=False
- optional:
  - options: H3_REWRITER_OPTIONS
  - bypass: BOOLEAN default=False
  - system_prompt: STRING default=''
- outputs: short_prompt:STRING, scene:STRING

## MiniMaxH3PromptRewriter
module: custom_nodes.MiniMax-H3-Prompt-Rewriter-ComfyUI | category: MiniMax-H3
- required:
  - prompt: STRING default=''
  - model: COMBO[Qwen3.6-27B (official, bf16) · 51.8 GB download · 16 GB as nf4 / 28 GB as int8 / 54 GB as bf16, Qwen3.6-27B bnb-4bit (samajlouis) · 17.3 GB download · ~16 GB, nothing extra to install — third-party repack, not published by Qwen, Qwen3.6-27B bnb-4bit (wyzxxywl) · 16.8 GB download · ~16 GB, nothing extra to install — third-party repack, not published by Qwen, Qwen3.6-27B FP8 · 28.8 GB download · ~29 GB — advanced: needs the 'kernels' package plus a Triton kernel download, and leaves no room for the video model beside it, Qwen3.6-27B GGUF Q8_0 · 26.6 GB download · ~30 GB with the adapter — needs ~30 GB of VRAM; lower gpu_layers if it will not fit, Qwen3.6-27B GGUF Q6_K · 21 GB download · ~25 GB with the adapter, Qwen3.6-27B GGUF Q5_K_M · 18.2 GB download · ~22 GB with the adapter, Qwen3.6-27B GGUF Q4_K_M · 15.7 GB download · ~19 GB with the adapter, less if you offload fewer layers, Qwen3.6-27B GGUF IQ4_XS · 14.4 GB download · ~18 GB with the adapter, Qwen3.6-27B GGUF UD-Q3_K_XL · 13.5 GB download · ~17 GB with the adapter, ... +6]
  - resolution: COMBO[48:9, 32:9, 21:9, 16:9, 4:3, 1:1, 3:4, 9:16] default='16:9'
  - duration: FLOAT,INT default=10.0 min=0.1 max=600.0 step=0.1
  - quantization: COMBO[nf4, int8, bfloat16, float16] default='nf4'
  - greedy: BOOLEAN default=True
  - seed: INT default=42 min=0 max=4294967295
  - keep_model_loaded: BOOLEAN default=False
- optional:
  - aspect_ratio: STRING,COMBO default=''
  - options: H3_REWRITER_OPTIONS
  - bypass: BOOLEAN default=False
  - repeat_last: BOOLEAN default=False
  - library_pick: STRING default=''
- outputs: rewritten_prompt:STRING, integrated_multimodal_description:STRING, overall_soundscape:STRING, non_diegetic_music:STRING

## MiniMaxH3PromptWriter8B
module: custom_nodes.MiniMax-H3-Prompt-Rewriter-ComfyUI | category: MiniMax-H3
- required:
  - prompt: STRING default=''
  - model: COMBO[Qwen3-VL-8B-Instruct (official, bf16) · 17.5 GB download · ~8 GB as nf4 / ~13 GB as int8 / ~20 GB as bf16, Qwen3-VL-8B-Instruct GGUF Q4_K_M · 5.4 GB download · ~9 GB with the adapter, Qwen3-VL-8B-Instruct GGUF Q8_0 · 8.8 GB download · ~13 GB with the adapter]
  - task: COMBO[T2VA, I2VA, FL2VA, L2VA] default='T2VA'
  - resolution: COMBO[48:9, 32:9, 21:9, 16:9, 4:3, 1:1, 3:4, 9:16] default='16:9'
  - duration: FLOAT,INT default=10.0 min=0.1 max=600.0 step=0.1
  - quantization: COMBO[nf4, int8, bfloat16, float16] default='nf4'
  - greedy: BOOLEAN default=True
  - seed: INT default=42 min=0 max=4294967295
  - keep_model_loaded: BOOLEAN default=False
- optional:
  - aspect_ratio: STRING,COMBO default=''
  - first_frame: IMAGE
  - last_frame: IMAGE
  - options: H3_REWRITER_OPTIONS
  - bypass: BOOLEAN default=False
  - repeat_last: BOOLEAN default=False
  - library_pick: STRING default=''
- outputs: rewritten_prompt:STRING, integrated_multimodal_description:STRING, overall_soundscape:STRING, non_diegetic_music:STRING

## MiniMaxH3PromptWriterOmni
module: custom_nodes.MiniMax-H3-Prompt-Rewriter-ComfyUI | category: MiniMax-H3
- required:
  - reference_layout: STRING default='{}'
  - task: COMBO[T2AV, I2AV, L2AV, FL2AV, REF2AV] default='T2AV'
  - resolution: COMBO[48:9, 32:9, 21:9, 16:9, 4:3, 1:1, 3:4, 9:16] default='16:9'
  - duration: FLOAT,INT default=10.0 min=0.1 max=600.0 step=0.1
  - prompt: STRING default=''
  - model: COMBO[Qwen2.5-Omni-7B (official, bf16) · 22.4 GB download · ~9 GB as nf4 / ~13 GB as int8 / ~24 GB as bf16, Qwen2.5-Omni-7B GGUF Q4_K_M · 6.2 GB download · ~9 GB with the adapter and a 12k context, Qwen2.5-Omni-7B GGUF Q8_0 · 9.7 GB download · ~13 GB - closer to the bf16 rewrite on a card that has room]
  - quantization: COMBO[nf4, int8, bfloat16, float16] default='nf4'
  - greedy: BOOLEAN default=True
  - seed: INT default=42 min=0 max=4294967295
  - keep_model_loaded: BOOLEAN default=False
- optional:
  - options: H3_REWRITER_OPTIONS
  - references: COMFY_AUTOGROW_V3
  - max_frames: INT default=8 min=1 max=64
  - bypass: BOOLEAN default=False
  - aspect_ratio: STRING,COMBO default=''
  - repeat_last: BOOLEAN default=False
  - library_pick: STRING default=''
- outputs: rewritten_prompt:STRING, integrated_multimodal_description:STRING, subject_definitions:STRING, summary:STRING, retention_analysis:STRING, detailed_description:STRING, overall_soundscape:STRING, non_diegetic_music:STRING, references:H3_REWRITER_REFERENCES

## MiniMaxH3ReducePrompt
module: custom_nodes.MiniMax-H3-Prompt-Rewriter-ComfyUI | category: MiniMax-H3
- required:
  - prompt: STRING
  - detail: COMBO[idea, sentence, paragraph] default='sentence'
  - subjects: COMBO[as written, age and gender, impersonal] default='as written'
  - keep_camera: BOOLEAN default=False
  - keep_audio: BOOLEAN default=False
  - keep_style: BOOLEAN default=False
  - language: STRING default=''
- optional:
  - format: COMBO[plain, chatml] default='plain'
  - system_prompt: STRING default=''
- outputs: system_prompt:STRING, user_prompt:STRING, prompt:STRING, scene:STRING

## MiniMaxH3ReferenceAdapter
module: custom_nodes.MiniMax-H3-Prompt-Rewriter-ComfyUI | category: MiniMax-H3
- required:
  - split_batches: BOOLEAN default=True
- optional:
  - items: *
  - bundle: H3_REFS
- outputs: picture_1:IMAGE, picture_2:IMAGE, picture_3:IMAGE, picture_4:IMAGE, picture_5:IMAGE, picture_6:IMAGE, picture_7:IMAGE, picture_8:IMAGE, picture_9:IMAGE, video_1:VIDEO, video_2:VIDEO, video_3:VIDEO, audio_1:AUDIO, audio_2:AUDIO, audio_3:AUDIO, summary:STRING

## MiniMaxH3ReferenceCaption
module: custom_nodes.MiniMax-H3-Prompt-Rewriter-ComfyUI | category: MiniMax-H3
- required:
  - role: COMBO[Subject, Picture, Video, Audio] default='Picture'
  - model: COMBO[Qwen2.5-Omni-3B · 3.4 GB download · ~5 GB — image, audio and video in one small model; verified against this pack, Qwen2.5-Omni-7B · 5.8 GB download · ~8 GB — same modalities, better prose; step up when the 3B's captions are too plain, Dark Roast Q8 (vl_judge) · ~11 GB — local file, same weights llama-swap serves as vl_judge; vision only, Qwen3-VL-8B abliterated Q8 (local) · 11 GB download · ~12 GB — 5s-lock test, Dark Roast 9B Q8 (local) · 10.4 GB download · ~12 GB — 5s-lock test]
  - length: COMBO[brief, standard, detailed] default='standard'
  - seed: INT default=42 min=0 max=4294967295
- optional:
  - image: IMAGE
  - audio: AUDIO
  - video: VIDEO
  - clip: CLIP
  - previous: STRING
  - description: STRING default=''
  - instruction: STRING default=''
  - max_frames: INT default=8 min=1 max=64
  - context_size: INT default=0 min=0 max=131072 step=1024
  - options: H3_REWRITER_OPTIONS
  - bypass: BOOLEAN default=False
  - repeat_last: BOOLEAN default=False
- outputs: reference_assets:STRING, caption:STRING

## MiniMaxH3ReferencePackBridge
module: custom_nodes.ComfyUI_MiniMax_H3_Extender | category: MiniMax H3
- optional:
  - ref_1: IMAGE
  - ref_2: IMAGE
  - ref_3: IMAGE
  - ref_4: IMAGE
  - ref_5: IMAGE
  - ref_6: IMAGE
  - ref_7: IMAGE
  - ref_8: IMAGE
  - ref_9: IMAGE
- outputs: ref_pack:H3_REF_PACK, ref_count:INT

## MiniMaxH3ReferenceSlots
module: custom_nodes.MiniMax-H3-Prompt-Rewriter-ComfyUI | category: MiniMax-H3
- required:
  - references: H3_REWRITER_REFERENCES
  - soundtracks: BOOLEAN default=False
- outputs: picture_1:IMAGE, picture_2:IMAGE, picture_3:IMAGE, picture_4:IMAGE, picture_5:IMAGE, picture_6:IMAGE, picture_7:IMAGE, picture_8:IMAGE, picture_9:IMAGE, video_1:IMAGE, video_2:IMAGE, video_3:IMAGE, video_audio_1:AUDIO, video_audio_2:AUDIO, video_audio_3:AUDIO, audio_1:AUDIO, audio_2:AUDIO, audio_3:AUDIO, summary:STRING

## MiniMaxH3ReferenceSplitter
module: custom_nodes.ComfyUI-Fantastic-MiniMaxH3-PromptBuilder | category: conditioning/video_models
- required:
  - references: H3_REFS
- outputs: picture_1:IMAGE, picture_2:IMAGE, picture_3:IMAGE, picture_4:IMAGE, picture_5:IMAGE, picture_6:IMAGE, picture_7:IMAGE, picture_8:IMAGE, picture_9:IMAGE, video_1:IMAGE, video_2:IMAGE, video_3:IMAGE, video_audio_1:AUDIO, video_audio_2:AUDIO, video_audio_3:AUDIO, audio_1:AUDIO, audio_2:AUDIO, audio_3:AUDIO

## MiniMaxH3ReferenceToVideo
module: comfy_extras.nodes_minimax_h3 | category: model/conditioning/minimax
- required:
  - clip: CLIP
  - prompt: STRING
  - width: INT default=1344 min=32 max=16384 step=32
  - height: INT default=768 min=32 max=16384 step=32
  - length: INT default=124 min=5 max=3600 step=17
  - ref_image_size: COMBO[match, max] default='match'
- optional:
  - vae: VAE
  - audio_vae: VAE
  - ref_images: COMFY_AUTOGROW_V3
  - ref_videos: COMFY_AUTOGROW_V3
  - ref_video_audios: COMFY_AUTOGROW_V3
  - ref_audios: COMFY_AUTOGROW_V3
- outputs: positive:CONDITIONING, LATENT:LATENT

## MiniMaxH3RefLoRAApply
module: custom_nodes.ComfyUI-MiniMaxH3RefLoRA | category: MiniMax-H3/reflora
- required:
  - conditioning: CONDITIONING
  - mods: H3_REF_MODS
  - retention: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- optional:
  - max_total_tokens: INT default=0 min=0 max=1048576
- outputs: conditioning:CONDITIONING

## MiniMaxH3RefLoRAInspect
module: custom_nodes.ComfyUI-MiniMaxH3RefLoRA | category: MiniMax-H3/reflora
- required:
  - reflora_name: COMBO[FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, FC_KIERNAN_h3_face_v1.safetensors, ... +48]
  - verify_bytes: BOOLEAN default=False
- outputs: report:STRING

## MiniMaxH3RefLoRALoader
module: custom_nodes.ComfyUI-MiniMaxH3RefLoRA | category: MiniMax-H3/reflora
- required:
  - model: MODEL
  - reflora_name: COMBO[FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, FC_KIERNAN_h3_face_v1.safetensors, ... +48]
  - lora_strength: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - refmod_retention: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - members: STRING default='all'
  - attach_to_model: BOOLEAN default=False
- optional:
  - clip: CLIP
  - lora_strength_clip: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - components: COMBO[All, Visual, Audio] default='All'
  - max_total_tokens: INT default=0 min=0 max=1048576
  - show_info: BOOLEAN default=True
- outputs: model:MODEL, clip:CLIP, mods:H3_REF_MODS, info:STRING

## MiniMaxH3RefLoRAPack
module: custom_nodes.ComfyUI-MiniMaxH3RefLoRA | category: MiniMax-H3/reflora
- required:
  - lora_name: COMBO[FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, FC_KIERNAN_h3_face_v1.safetensors, ... +48]
  - output_name: STRING default=''
  - subfolder: STRING default='MinimaxH3/reflora'
  - overwrite: BOOLEAN default=False
  - refmod_1: COMBO[(none), minimaxh3_aaliyah_v1_refmod.safetensors, minimaxh3_aarontaylorjohnson_v1_refmod.safetensors, minimaxh3_abbiecornish_v1_refmod.safetensors, minimaxh3_abby_v1_refmod.safetensors, minimaxh3_abbyshapiro_v1_refmod.safetensors, minimaxh3_abigailcowen_v1_refmod.safetensors, minimaxh3_abigailratchford_v1_refmod.safetensors, minimaxh3_abigailspencer_v1_refmod.safetensors, minimaxh3_acropolis_v1_refmod.safetensors, ... +1486]
  - refmod_2: COMBO[(none), minimaxh3_aaliyah_v1_refmod.safetensors, minimaxh3_aarontaylorjohnson_v1_refmod.safetensors, minimaxh3_abbiecornish_v1_refmod.safetensors, minimaxh3_abby_v1_refmod.safetensors, minimaxh3_abbyshapiro_v1_refmod.safetensors, minimaxh3_abigailcowen_v1_refmod.safetensors, minimaxh3_abigailratchford_v1_refmod.safetensors, minimaxh3_abigailspencer_v1_refmod.safetensors, minimaxh3_acropolis_v1_refmod.safetensors, ... +1486]
  - refmod_3: COMBO[(none), minimaxh3_aaliyah_v1_refmod.safetensors, minimaxh3_aarontaylorjohnson_v1_refmod.safetensors, minimaxh3_abbiecornish_v1_refmod.safetensors, minimaxh3_abby_v1_refmod.safetensors, minimaxh3_abbyshapiro_v1_refmod.safetensors, minimaxh3_abigailcowen_v1_refmod.safetensors, minimaxh3_abigailratchford_v1_refmod.safetensors, minimaxh3_abigailspencer_v1_refmod.safetensors, minimaxh3_acropolis_v1_refmod.safetensors, ... +1486]
  - refmod_4: COMBO[(none), minimaxh3_aaliyah_v1_refmod.safetensors, minimaxh3_aarontaylorjohnson_v1_refmod.safetensors, minimaxh3_abbiecornish_v1_refmod.safetensors, minimaxh3_abby_v1_refmod.safetensors, minimaxh3_abbyshapiro_v1_refmod.safetensors, minimaxh3_abigailcowen_v1_refmod.safetensors, minimaxh3_abigailratchford_v1_refmod.safetensors, minimaxh3_abigailspencer_v1_refmod.safetensors, minimaxh3_acropolis_v1_refmod.safetensors, ... +1486]
  - refmod_5: COMBO[(none), minimaxh3_aaliyah_v1_refmod.safetensors, minimaxh3_aarontaylorjohnson_v1_refmod.safetensors, minimaxh3_abbiecornish_v1_refmod.safetensors, minimaxh3_abby_v1_refmod.safetensors, minimaxh3_abbyshapiro_v1_refmod.safetensors, minimaxh3_abigailcowen_v1_refmod.safetensors, minimaxh3_abigailratchford_v1_refmod.safetensors, minimaxh3_abigailspencer_v1_refmod.safetensors, minimaxh3_acropolis_v1_refmod.safetensors, ... +1486]
  - refmod_6: COMBO[(none), minimaxh3_aaliyah_v1_refmod.safetensors, minimaxh3_aarontaylorjohnson_v1_refmod.safetensors, minimaxh3_abbiecornish_v1_refmod.safetensors, minimaxh3_abby_v1_refmod.safetensors, minimaxh3_abbyshapiro_v1_refmod.safetensors, minimaxh3_abigailcowen_v1_refmod.safetensors, minimaxh3_abigailratchford_v1_refmod.safetensors, minimaxh3_abigailspencer_v1_refmod.safetensors, minimaxh3_acropolis_v1_refmod.safetensors, ... +1486]
  - refmod_7: COMBO[(none), minimaxh3_aaliyah_v1_refmod.safetensors, minimaxh3_aarontaylorjohnson_v1_refmod.safetensors, minimaxh3_abbiecornish_v1_refmod.safetensors, minimaxh3_abby_v1_refmod.safetensors, minimaxh3_abbyshapiro_v1_refmod.safetensors, minimaxh3_abigailcowen_v1_refmod.safetensors, minimaxh3_abigailratchford_v1_refmod.safetensors, minimaxh3_abigailspencer_v1_refmod.safetensors, minimaxh3_acropolis_v1_refmod.safetensors, ... +1486]
  - refmod_8: COMBO[(none), minimaxh3_aaliyah_v1_refmod.safetensors, minimaxh3_aarontaylorjohnson_v1_refmod.safetensors, minimaxh3_abbiecornish_v1_refmod.safetensors, minimaxh3_abby_v1_refmod.safetensors, minimaxh3_abbyshapiro_v1_refmod.safetensors, minimaxh3_abigailcowen_v1_refmod.safetensors, minimaxh3_abigailratchford_v1_refmod.safetensors, minimaxh3_abigailspencer_v1_refmod.safetensors, minimaxh3_acropolis_v1_refmod.safetensors, ... +1486]
- outputs: path:STRING, report:STRING

## MiniMaxH3RefModApply
module: custom_nodes.ComfyUI-MiniMaxH3Mod | category: MiniMax-H3/mod
- required:
  - conditioning: COMFY_MATCHTYPE_V3
  - mods: H3_REF_MODS
  - override: BOOLEAN default=False
  - retention: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - curve_direction: COMBO[constant, concept_at_start, concept_at_middle, concept_at_end, concept_at_ends] default='constant'
  - scramble_seed: INT default=-1 min=-1 max=2147483647 step=1
  - curve_shape: COMBO[linear, ease, sigmoid, tanh, quadratic, cubic, exponential, stair, elastic, bump, ... +1] default='linear'
  - curve_value: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- optional:
  - graph_preset: COMBO[(none)] default='(none)'
  - scramble_mode: COMBO[shuffle, subset, legacy_subset] default='shuffle'
  - scramble_keep: INT default=1 min=1 max=80
  - max_total_tokens: INT default=0 min=0 max=1048576
  - save_preset_as: STRING default=''
- outputs: conditioning:COMFY_MATCHTYPE_V3, curve graph:IMAGE

## MiniMaxH3RefModAudioExtract
module: custom_nodes.ComfyUI-MiniMaxH3Mod | category: MiniMax-H3/mod
- required:
  - audio: AUDIO
  - audio_vae: VAE
  - name: STRING default='audio_refmod'
  - max_seconds: FLOAT default=30.0 min=0.025 max=600.0
  - max_tokens: INT default=5120 min=0 max=2147483647
  - budget_policy: COMBO[error, truncate]
  - concept_type: COMBO[voice, singing, music_style, sound_fx, ambience]
  - description: STRING default=''
  - subfolder: STRING default=''
  - save: BOOLEAN default=True
- outputs: H3_REF_MODS:H3_REF_MODS

## MiniMaxH3RefModBridgeDisarm
module: custom_nodes.ComfyUI-MiniMaxH3Mod | category: MiniMax-H3/mod
- required:
  - trigger: INT default=0 min=0 max=4294967295
- outputs: status:STRING

## MiniMaxH3RefModBundleSave
module: custom_nodes.ComfyUI-MiniMaxH3Mod | category: MiniMax-H3/mod
- required:
  - mods: H3_REF_MODS
  - name: STRING default='character'
  - subfolder: STRING default=''
- outputs: mods:H3_REF_MODS, saved_path:STRING

## MiniMaxH3RefModConfig
module: custom_nodes.ComfyUI-MiniMaxH3Mod | category: MiniMax-H3/mod
- required:
  - mods: H3_REF_MODS
  - retention: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - curve_direction: COMBO[constant, concept_at_start, concept_at_middle, concept_at_end, concept_at_ends] default='concept_at_end'
  - curve_shape: COMBO[linear, ease, sigmoid, tanh, quadratic, cubic, exponential, stair, elastic, bump, ... +1] default='ease'
  - curve_value: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - step_curve_direction: COMBO[constant, concept_at_start, concept_at_middle, concept_at_end, concept_at_ends] default='concept_at_end'
  - step_curve_shape: COMBO[linear, ease, sigmoid, tanh, quadratic, cubic, exponential, stair, elastic, bump, ... +1] default='ease'
  - step_curve_value: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: mods:H3_REF_MODS

## MiniMaxH3RefModContinuumBridge
module: custom_nodes.ComfyUI-MiniMaxH3Mod | category: MiniMax-H3/mod
- required:
  - model: MODEL
  - mods: H3_REF_MODS
  - enable: BOOLEAN default=True
  - retention: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - curve_direction: COMBO[constant, concept_at_start, concept_at_middle, concept_at_end, concept_at_ends] default='constant'
  - curve_shape: COMBO[linear, ease, sigmoid, tanh, quadratic, cubic, exponential, stair, elastic, bump, ... +1] default='linear'
  - curve_value: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - scramble_seed: INT default=-1 min=-1 max=2147483647 step=1
- optional:
  - scramble_mode: COMBO[shuffle, subset, legacy_subset] default='shuffle'
  - scramble_keep: INT default=1 min=1 max=80
  - max_total_tokens: INT default=0 min=0 max=1048576
- outputs: model:MODEL, mods:H3_REF_MODS, status:STRING

## MiniMaxH3RefModExtract
module: custom_nodes.ComfyUI-MiniMaxH3Mod | category: MiniMax-H3/mod
- required:
  - name: STRING default='my_concept'
  - mode: COMBO[Compressed Reference, Full Reference, training, encode] default='Compressed Reference'
  - concept_type: COMBO[generic, identity, pose_motion, clothing, background, voice, singing, music_style, sound_fx, ambience, ... +1] default='generic'
  - background_retention: FLOAT default=0.0 min=0.0 max=1.0 step=0.05
  - ref_resolution: INT default=1024 min=256 max=2048 step=64
  - pool_h: INT default=16 min=2 max=64 step=2
  - pool_w: INT default=16 min=2 max=64 step=2
  - latent_frames: INT default=16 min=1 max=2147483647
  - identity: INT default=500 min=0 max=2000 step=50
  - merge: BOOLEAN default=False
  - motion_only: BOOLEAN default=False
  - multiplier: INT default=1 min=1 max=10 step=1
  - max_tokens: INT default=5120 min=0 max=2147483647 step=512
  - description: STRING default=''
  - save: BOOLEAN default=True
- optional:
  - refs_image: COMFY_AUTOGROW_V3
  - refs_video: COMFY_AUTOGROW_V3
  - refs_bundle: H3_REF_LIST
  - mask: MASK
  - av_encoder: MINIMAX_H3_AV_ENCODER
  - vae: VAE
  - extraction_preset: COMBO[manual, identity_encode, style_experimental, motion_sequence] default='manual'
  - subfolder: STRING default=''
  - mask_list: H3_MASK_LIST
  - budget_policy: COMBO[truncate, error] default='truncate'
- outputs: mods:H3_REF_MODS, details:STRING

## MiniMaxH3RefModFolderLoader
module: custom_nodes.ComfyUI-MiniMaxH3Mod | category: MiniMax-H3/mod
- required:
  - folder: STRING default=''
  - max_items: INT default=32 min=1 max=256 step=1
  - max_frames: INT default=240 min=2 max=4800 step=1
  - max_edge: INT default=1024 min=256 max=4096 step=64
- outputs: refs:H3_REF_LIST, count:INT

## MiniMaxH3RefModInspect
module: custom_nodes.ComfyUI-MiniMaxH3Mod | category: MiniMax-H3/mod
- required:
  - mods: H3_REF_MODS
  - index: INT default=0 min=0 max=10000
  - preview: COMBO[off, stored, compare_strength]
  - strength: FLOAT default=0.5 min=0.0 max=1.0
- optional:
  - vae: VAE
  - visual_preview: COMBO[first_frame, full_video] default='first_frame'
- outputs: details:STRING, image_preview:IMAGE, audio_preview:AUDIO, reference_map:STRING

## MiniMaxH3RefModMaskList
module: custom_nodes.ComfyUI-MiniMaxH3Mod | category: MiniMax-H3/mod
- required:
  - masks: MASK
- outputs: mask_list:H3_MASK_LIST

## MiniMaxH3RefModMasterExtract
module: custom_nodes.ComfyUI-MiniMaxH3Mod | category: MiniMax-H3/mod
- required:
  - name: STRING default='my_concept'
  - mode: COMBO[Compressed Reference, Full Reference, training, encode] default='Compressed Reference'
  - concept_type: COMBO[generic, identity, pose_motion, clothing, background, voice, singing, music_style, sound_fx, ambience, ... +1] default='generic'
  - background_retention: FLOAT default=0.0 min=0.0 max=1.0 step=0.05
  - ref_resolution: INT default=1024 min=256 max=2048 step=64
  - pool_h: INT default=16 min=2 max=64 step=2
  - pool_w: INT default=16 min=2 max=64 step=2
  - latent_frames: INT default=16 min=1 max=2147483647
  - identity: INT default=500 min=0 max=2000 step=50
  - merge: BOOLEAN default=False
  - motion_only: BOOLEAN default=False
  - multiplier: INT default=1 min=1 max=10 step=1
  - max_tokens: INT default=5120 min=0 max=2147483647 step=512
  - description: STRING default=''
  - save: BOOLEAN default=True
  - audio_max_seconds: FLOAT default=30.0 min=0.025 max=600.0
  - audio_max_tokens: INT default=5120 min=0 max=2147483647
  - audio_budget_policy: COMBO[error, truncate] default='error'
  - audio_concept_type: COMBO[voice, singing, music_style, sound_fx, ambience] default='voice'
  - max_total_tokens: INT default=0 min=0 max=1048576
- optional:
  - refs_image: COMFY_AUTOGROW_V3
  - refs_video: COMFY_AUTOGROW_V3
  - refs_bundle: H3_REF_LIST
  - mask: MASK
  - av_encoder: MINIMAX_H3_AV_ENCODER
  - vae: VAE
  - extraction_preset: COMBO[manual, identity_encode, style_experimental, motion_sequence] default='manual'
  - subfolder: STRING default=''
  - mask_list: H3_MASK_LIST
  - audio: AUDIO
  - audio_vae: VAE
  - budget_policy: COMBO[truncate, error] default='truncate'
  - save_layout: COMBO[separate_files, bundle] default='separate_files'
- outputs: mods:H3_REF_MODS, details:STRING

## MiniMaxH3RefModSave
module: custom_nodes.ComfyUI-MiniMaxH3Mod | category: MiniMax-H3/mod
- required:
  - mods: H3_REF_MODS
  - filename_prefix: STRING default=''
  - subfolder: STRING default=''
- outputs: mods:H3_REF_MODS, saved_paths:STRING

## MiniMaxH3RefModsAxis
module: custom_nodes.ComfyUI-MiniMaxH3Mod | category: MiniMax-H3/mod
- required:
  - show_info: BOOLEAN default=False
  - mod_a_1: COMBO[(none), minimaxh3_aaliyah_v1_refmod, minimaxh3_aarontaylorjohnson_v1_refmod, minimaxh3_abbiecornish_v1_refmod, minimaxh3_abby_v1_refmod, minimaxh3_abbyshapiro_v1_refmod, minimaxh3_abigailcowen_v1_refmod, minimaxh3_abigailratchford_v1_refmod, minimaxh3_abigailspencer_v1_refmod, minimaxh3_acropolis_v1_refmod, ... +1475]
  - mod_b_1: COMBO[(none), minimaxh3_aaliyah_v1_refmod, minimaxh3_aarontaylorjohnson_v1_refmod, minimaxh3_abbiecornish_v1_refmod, minimaxh3_abby_v1_refmod, minimaxh3_abbyshapiro_v1_refmod, minimaxh3_abigailcowen_v1_refmod, minimaxh3_abigailratchford_v1_refmod, minimaxh3_abigailspencer_v1_refmod, minimaxh3_acropolis_v1_refmod, ... +1475]
  - value_1: FLOAT default=0.0 min=-1.0 max=1.0 step=0.01
  - mod_a_2: COMBO[(none), minimaxh3_aaliyah_v1_refmod, minimaxh3_aarontaylorjohnson_v1_refmod, minimaxh3_abbiecornish_v1_refmod, minimaxh3_abby_v1_refmod, minimaxh3_abbyshapiro_v1_refmod, minimaxh3_abigailcowen_v1_refmod, minimaxh3_abigailratchford_v1_refmod, minimaxh3_abigailspencer_v1_refmod, minimaxh3_acropolis_v1_refmod, ... +1475]
  - mod_b_2: COMBO[(none), minimaxh3_aaliyah_v1_refmod, minimaxh3_aarontaylorjohnson_v1_refmod, minimaxh3_abbiecornish_v1_refmod, minimaxh3_abby_v1_refmod, minimaxh3_abbyshapiro_v1_refmod, minimaxh3_abigailcowen_v1_refmod, minimaxh3_abigailratchford_v1_refmod, minimaxh3_abigailspencer_v1_refmod, minimaxh3_acropolis_v1_refmod, ... +1475]
  - value_2: FLOAT default=0.0 min=-1.0 max=1.0 step=0.01
  - mod_a_3: COMBO[(none), minimaxh3_aaliyah_v1_refmod, minimaxh3_aarontaylorjohnson_v1_refmod, minimaxh3_abbiecornish_v1_refmod, minimaxh3_abby_v1_refmod, minimaxh3_abbyshapiro_v1_refmod, minimaxh3_abigailcowen_v1_refmod, minimaxh3_abigailratchford_v1_refmod, minimaxh3_abigailspencer_v1_refmod, minimaxh3_acropolis_v1_refmod, ... +1475]
  - mod_b_3: COMBO[(none), minimaxh3_aaliyah_v1_refmod, minimaxh3_aarontaylorjohnson_v1_refmod, minimaxh3_abbiecornish_v1_refmod, minimaxh3_abby_v1_refmod, minimaxh3_abbyshapiro_v1_refmod, minimaxh3_abigailcowen_v1_refmod, minimaxh3_abigailratchford_v1_refmod, minimaxh3_abigailspencer_v1_refmod, minimaxh3_acropolis_v1_refmod, ... +1475]
  - value_3: FLOAT default=0.0 min=-1.0 max=1.0 step=0.01
  - mod_a_4: COMBO[(none), minimaxh3_aaliyah_v1_refmod, minimaxh3_aarontaylorjohnson_v1_refmod, minimaxh3_abbiecornish_v1_refmod, minimaxh3_abby_v1_refmod, minimaxh3_abbyshapiro_v1_refmod, minimaxh3_abigailcowen_v1_refmod, minimaxh3_abigailratchford_v1_refmod, minimaxh3_abigailspencer_v1_refmod, minimaxh3_acropolis_v1_refmod, ... +1475]
  - mod_b_4: COMBO[(none), minimaxh3_aaliyah_v1_refmod, minimaxh3_aarontaylorjohnson_v1_refmod, minimaxh3_abbiecornish_v1_refmod, minimaxh3_abby_v1_refmod, minimaxh3_abbyshapiro_v1_refmod, minimaxh3_abigailcowen_v1_refmod, minimaxh3_abigailratchford_v1_refmod, minimaxh3_abigailspencer_v1_refmod, minimaxh3_acropolis_v1_refmod, ... +1475]
  - value_4: FLOAT default=0.0 min=-1.0 max=1.0 step=0.01
  - mod_a_5: COMBO[(none), minimaxh3_aaliyah_v1_refmod, minimaxh3_aarontaylorjohnson_v1_refmod, minimaxh3_abbiecornish_v1_refmod, minimaxh3_abby_v1_refmod, minimaxh3_abbyshapiro_v1_refmod, minimaxh3_abigailcowen_v1_refmod, minimaxh3_abigailratchford_v1_refmod, minimaxh3_abigailspencer_v1_refmod, minimaxh3_acropolis_v1_refmod, ... +1475]
  - mod_b_5: COMBO[(none), minimaxh3_aaliyah_v1_refmod, minimaxh3_aarontaylorjohnson_v1_refmod, minimaxh3_abbiecornish_v1_refmod, minimaxh3_abby_v1_refmod, minimaxh3_abbyshapiro_v1_refmod, minimaxh3_abigailcowen_v1_refmod, minimaxh3_abigailratchford_v1_refmod, minimaxh3_abigailspencer_v1_refmod, minimaxh3_acropolis_v1_refmod, ... +1475]
  - value_5: FLOAT default=0.0 min=-1.0 max=1.0 step=0.01
  - mod_a_6: COMBO[(none), minimaxh3_aaliyah_v1_refmod, minimaxh3_aarontaylorjohnson_v1_refmod, minimaxh3_abbiecornish_v1_refmod, minimaxh3_abby_v1_refmod, minimaxh3_abbyshapiro_v1_refmod, minimaxh3_abigailcowen_v1_refmod, minimaxh3_abigailratchford_v1_refmod, minimaxh3_abigailspencer_v1_refmod, minimaxh3_acropolis_v1_refmod, ... +1475]
  - mod_b_6: COMBO[(none), minimaxh3_aaliyah_v1_refmod, minimaxh3_aarontaylorjohnson_v1_refmod, minimaxh3_abbiecornish_v1_refmod, minimaxh3_abby_v1_refmod, minimaxh3_abbyshapiro_v1_refmod, minimaxh3_abigailcowen_v1_refmod, minimaxh3_abigailratchford_v1_refmod, minimaxh3_abigailspencer_v1_refmod, minimaxh3_acropolis_v1_refmod, ... +1475]
  - value_6: FLOAT default=0.0 min=-1.0 max=1.0 step=0.01
  - mod_a_7: COMBO[(none), minimaxh3_aaliyah_v1_refmod, minimaxh3_aarontaylorjohnson_v1_refmod, minimaxh3_abbiecornish_v1_refmod, minimaxh3_abby_v1_refmod, minimaxh3_abbyshapiro_v1_refmod, minimaxh3_abigailcowen_v1_refmod, minimaxh3_abigailratchford_v1_refmod, minimaxh3_abigailspencer_v1_refmod, minimaxh3_acropolis_v1_refmod, ... +1475]
  - mod_b_7: COMBO[(none), minimaxh3_aaliyah_v1_refmod, minimaxh3_aarontaylorjohnson_v1_refmod, minimaxh3_abbiecornish_v1_refmod, minimaxh3_abby_v1_refmod, minimaxh3_abbyshapiro_v1_refmod, minimaxh3_abigailcowen_v1_refmod, minimaxh3_abigailratchford_v1_refmod, minimaxh3_abigailspencer_v1_refmod, minimaxh3_acropolis_v1_refmod, ... +1475]
  - value_7: FLOAT default=0.0 min=-1.0 max=1.0 step=0.01
  - mod_a_8: COMBO[(none), minimaxh3_aaliyah_v1_refmod, minimaxh3_aarontaylorjohnson_v1_refmod, minimaxh3_abbiecornish_v1_refmod, minimaxh3_abby_v1_refmod, minimaxh3_abbyshapiro_v1_refmod, minimaxh3_abigailcowen_v1_refmod, minimaxh3_abigailratchford_v1_refmod, minimaxh3_abigailspencer_v1_refmod, minimaxh3_acropolis_v1_refmod, ... +1475]
  - mod_b_8: COMBO[(none), minimaxh3_aaliyah_v1_refmod, minimaxh3_aarontaylorjohnson_v1_refmod, minimaxh3_abbiecornish_v1_refmod, minimaxh3_abby_v1_refmod, minimaxh3_abbyshapiro_v1_refmod, minimaxh3_abigailcowen_v1_refmod, minimaxh3_abigailratchford_v1_refmod, minimaxh3_abigailspencer_v1_refmod, minimaxh3_acropolis_v1_refmod, ... +1475]
  - value_8: FLOAT default=0.0 min=-1.0 max=1.0 step=0.01
- optional:
  - max_total_tokens: INT default=0 min=0 max=1048576
  - components_1: COMBO[All, Visual, Audio] default='All'
  - visual_strength_1: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - audio_strength_1: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - components_2: COMBO[All, Visual, Audio] default='All'
  - visual_strength_2: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - audio_strength_2: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - components_3: COMBO[All, Visual, Audio] default='All'
  - visual_strength_3: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - audio_strength_3: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - components_4: COMBO[All, Visual, Audio] default='All'
  - visual_strength_4: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - audio_strength_4: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - components_5: COMBO[All, Visual, Audio] default='All'
  - visual_strength_5: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - audio_strength_5: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - components_6: COMBO[All, Visual, Audio] default='All'
  - visual_strength_6: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - audio_strength_6: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - components_7: COMBO[All, Visual, Audio] default='All'
  - visual_strength_7: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - audio_strength_7: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - components_8: COMBO[All, Visual, Audio] default='All'
  - visual_strength_8: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - audio_strength_8: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: mods:H3_REF_MODS, prompt_hint:STRING

## MiniMaxH3RefModsLoader
module: custom_nodes.ComfyUI-MiniMaxH3Mod | category: MiniMax-H3/mod
- required:
  - show_info: BOOLEAN default=False
  - mod_1: COMBO[(none), minimaxh3_aaliyah_v1_refmod, minimaxh3_aarontaylorjohnson_v1_refmod, minimaxh3_abbiecornish_v1_refmod, minimaxh3_abby_v1_refmod, minimaxh3_abbyshapiro_v1_refmod, minimaxh3_abigailcowen_v1_refmod, minimaxh3_abigailratchford_v1_refmod, minimaxh3_abigailspencer_v1_refmod, minimaxh3_acropolis_v1_refmod, ... +1475]
  - strength_1: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - copies_1: INT default=1 min=1 max=10 step=1
  - mod_2: COMBO[(none), minimaxh3_aaliyah_v1_refmod, minimaxh3_aarontaylorjohnson_v1_refmod, minimaxh3_abbiecornish_v1_refmod, minimaxh3_abby_v1_refmod, minimaxh3_abbyshapiro_v1_refmod, minimaxh3_abigailcowen_v1_refmod, minimaxh3_abigailratchford_v1_refmod, minimaxh3_abigailspencer_v1_refmod, minimaxh3_acropolis_v1_refmod, ... +1475]
  - strength_2: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - copies_2: INT default=1 min=1 max=10 step=1
  - mod_3: COMBO[(none), minimaxh3_aaliyah_v1_refmod, minimaxh3_aarontaylorjohnson_v1_refmod, minimaxh3_abbiecornish_v1_refmod, minimaxh3_abby_v1_refmod, minimaxh3_abbyshapiro_v1_refmod, minimaxh3_abigailcowen_v1_refmod, minimaxh3_abigailratchford_v1_refmod, minimaxh3_abigailspencer_v1_refmod, minimaxh3_acropolis_v1_refmod, ... +1475]
  - strength_3: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - copies_3: INT default=1 min=1 max=10 step=1
  - mod_4: COMBO[(none), minimaxh3_aaliyah_v1_refmod, minimaxh3_aarontaylorjohnson_v1_refmod, minimaxh3_abbiecornish_v1_refmod, minimaxh3_abby_v1_refmod, minimaxh3_abbyshapiro_v1_refmod, minimaxh3_abigailcowen_v1_refmod, minimaxh3_abigailratchford_v1_refmod, minimaxh3_abigailspencer_v1_refmod, minimaxh3_acropolis_v1_refmod, ... +1475]
  - strength_4: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - copies_4: INT default=1 min=1 max=10 step=1
  - mod_5: COMBO[(none), minimaxh3_aaliyah_v1_refmod, minimaxh3_aarontaylorjohnson_v1_refmod, minimaxh3_abbiecornish_v1_refmod, minimaxh3_abby_v1_refmod, minimaxh3_abbyshapiro_v1_refmod, minimaxh3_abigailcowen_v1_refmod, minimaxh3_abigailratchford_v1_refmod, minimaxh3_abigailspencer_v1_refmod, minimaxh3_acropolis_v1_refmod, ... +1475]
  - strength_5: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - copies_5: INT default=1 min=1 max=10 step=1
  - mod_6: COMBO[(none), minimaxh3_aaliyah_v1_refmod, minimaxh3_aarontaylorjohnson_v1_refmod, minimaxh3_abbiecornish_v1_refmod, minimaxh3_abby_v1_refmod, minimaxh3_abbyshapiro_v1_refmod, minimaxh3_abigailcowen_v1_refmod, minimaxh3_abigailratchford_v1_refmod, minimaxh3_abigailspencer_v1_refmod, minimaxh3_acropolis_v1_refmod, ... +1475]
  - strength_6: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - copies_6: INT default=1 min=1 max=10 step=1
  - mod_7: COMBO[(none), minimaxh3_aaliyah_v1_refmod, minimaxh3_aarontaylorjohnson_v1_refmod, minimaxh3_abbiecornish_v1_refmod, minimaxh3_abby_v1_refmod, minimaxh3_abbyshapiro_v1_refmod, minimaxh3_abigailcowen_v1_refmod, minimaxh3_abigailratchford_v1_refmod, minimaxh3_abigailspencer_v1_refmod, minimaxh3_acropolis_v1_refmod, ... +1475]
  - strength_7: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - copies_7: INT default=1 min=1 max=10 step=1
  - mod_8: COMBO[(none), minimaxh3_aaliyah_v1_refmod, minimaxh3_aarontaylorjohnson_v1_refmod, minimaxh3_abbiecornish_v1_refmod, minimaxh3_abby_v1_refmod, minimaxh3_abbyshapiro_v1_refmod, minimaxh3_abigailcowen_v1_refmod, minimaxh3_abigailratchford_v1_refmod, minimaxh3_abigailspencer_v1_refmod, minimaxh3_acropolis_v1_refmod, ... +1475]
  - strength_8: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - copies_8: INT default=1 min=1 max=10 step=1
- optional:
  - max_total_tokens: INT default=0 min=0 max=1048576
  - components_1: COMBO[All, Visual, Audio] default='All'
  - visual_strength_1: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - audio_strength_1: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - components_2: COMBO[All, Visual, Audio] default='All'
  - visual_strength_2: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - audio_strength_2: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - components_3: COMBO[All, Visual, Audio] default='All'
  - visual_strength_3: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - audio_strength_3: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - components_4: COMBO[All, Visual, Audio] default='All'
  - visual_strength_4: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - audio_strength_4: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - components_5: COMBO[All, Visual, Audio] default='All'
  - visual_strength_5: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - audio_strength_5: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - components_6: COMBO[All, Visual, Audio] default='All'
  - visual_strength_6: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - audio_strength_6: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - components_7: COMBO[All, Visual, Audio] default='All'
  - visual_strength_7: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - audio_strength_7: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - components_8: COMBO[All, Visual, Audio] default='All'
  - visual_strength_8: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - audio_strength_8: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: mods:H3_REF_MODS, prompt_hint:STRING

## MiniMaxH3RefModStack
module: custom_nodes.ComfyUI-Fantastic-MiniMaxH3-PromptBuilder | category: conditioning/video_models
- required:
  - stack_state: STRING default='{}'
- optional:
  - mods: H3_REF_MODS
- outputs: mods:H3_REF_MODS, labels:STRING

## MiniMaxH3RefModStepCurve
module: custom_nodes.ComfyUI-MiniMaxH3Mod | category: MiniMax-H3/mod
- required:
  - model: MODEL
  - override: BOOLEAN default=False
  - curve_direction: COMBO[constant, concept_at_start, concept_at_middle, concept_at_end, concept_at_ends] default='constant'
  - curve_shape: COMBO[linear, ease, sigmoid, tanh, quadratic, cubic, exponential, stair, elastic, bump, ... +1] default='linear'
  - curve_value: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- optional:
  - mods: H3_REF_MODS
- outputs: model:MODEL

## MiniMaxH3RefModTextEncode
module: custom_nodes.ComfyUI-MiniMaxH3Mod | category: MiniMax-H3/mod
- required:
  - clip: CLIP
  - mods: H3_REF_MODS
  - prompt: STRING
  - reference_fps: FLOAT default=24.0 min=1.0 max=120.0
  - max_total_tokens: INT default=0 min=0 max=2147483647
- optional:
  - vae: VAE
- outputs: conditioning:CONDITIONING, reference_map:STRING

## MiniMaxH3RewriterOptions
module: custom_nodes.MiniMax-H3-Prompt-Rewriter-ComfyUI | category: MiniMax-H3
- required:
  - max_new_tokens: INT default=2048 min=64 max=16384 step=64
  - temperature: FLOAT default=0.7 min=0.0 max=2.0 step=0.01
  - top_p: FLOAT default=0.8 min=0.0 max=1.0 step=0.01
  - top_k: INT default=20 min=0 max=200
  - repetition_penalty: FLOAT default=1.05 min=1.0 max=2.0 step=0.01
  - attn_implementation: COMBO[sdpa, eager, flash_attention_2] default='sdpa'
- optional:
  - adapter: COMBO[lightx2v/MiniMax-H3-Prompt-Rewriter-LoRA, MiniMax-H3-Prompt-Rewriter-LoRA-F16.gguf · 3.48 GB download, MiniMax-H3-Prompt-Rewriter-LoRA-Q8_0.gguf · 1.85 GB download — half the size, same rewrite behaviour, MiniMax-H3-Prompt-Rewriter-LoRA-8B-F16.gguf · 1.3 GB download, MiniMax-H3-Prompt-Rewriter-LoRA-8B-Q8_0.gguf · 0.69 GB download — half the size, same rewrite behaviour, MiniMax-H3-Prompt-Rewriter-LoRA-Omni-F16.gguf · 0.65 GB download, MiniMax-H3-Prompt-Rewriter-LoRA-Omni-Q8_0.gguf · 0.34 GB download — half the size, same rewrite behaviour, on disk: MiniMax-H3-Prompt-Rewriter-LoRA-Omni-Q8_0.gguf [qwen2vl, 0.3 GB]] default='lightx2v/MiniMax-H3-Prompt-Rewriter-LoRA'
  - use_lora: BOOLEAN default=True
  - merge_lora: COMBO[auto, on, off] default='auto'
  - auto_download: BOOLEAN default=True
  - gpu_layers: INT default=-1 min=-1 max=999
  - n_ctx: INT default=8192 min=2048 max=131072 step=1024
  - gguf_runtime: COMBO[auto, llama-cpp-python, llama.cpp] default='auto'
  - device: COMBO[auto, cuda:0, cpu] default='auto'
  - llama_backend: COMBO[auto, vulkan, cuda, cpu] default='auto'
  - trust_remote_code: BOOLEAN default=False
  - prompt_file: COMBO[global] default='global'
  - self_check: COMBO[warnings and notes, warnings only, off] default='warnings and notes'
  - fix_once: BOOLEAN default=False
  - downloader: COMBO[built-in, huggingface_hub] default='built-in'
- outputs: options:H3_REWRITER_OPTIONS

## MiniMaxH3SigmaShift
module: comfy_extras.nodes_minimax_h3 | category: model/patch/minimax
- required:
  - model: MODEL
  - shift_video: FLOAT default=12.0 min=0.01 max=100.0 step=0.01
  - shift_audio: FLOAT default=3.0 min=0.01 max=100.0 step=0.01
- outputs: MODEL:MODEL

## MiniMaxH3TailFromLatent
module: custom_nodes.ComfyUI_MiniMax_H3_Extender | category: MiniMax H3
- required:
  - samples: LATENT
  - vae: VAE
  - audio_vae: VAE
  - tail_seconds: FLOAT default=0.5 min=0.1 max=15.0 step=0.05
  - align_to_h3_grid: BOOLEAN default=True
- outputs: ref_video:IMAGE, ref_video_audio:AUDIO, last_frame:IMAGE, frame_count:INT, duration_seconds:FLOAT

## MiniMaxH3UniversalRewriter
module: custom_nodes.MiniMax-H3-Prompt-Rewriter-ComfyUI | category: MiniMax-H3
- required:
  - lora: COMBO[27B LoRA, 8B LoRA, Omni LoRA] default='27B LoRA'
  - task: COMBO[T2VA, I2VA, FL2VA, L2VA, Ref2VA] default='T2VA'
  - resolution: COMBO[48:9, 32:9, 21:9, 16:9, 4:3, 1:1, 3:4, 9:16] default='16:9'
  - duration: FLOAT,INT default=10.0 min=0.1 max=600.0 step=0.1
  - prompt: STRING default=''
  - model_27b: COMBO[Qwen3.6-27B (official, bf16) · 51.8 GB download · 16 GB as nf4 / 28 GB as int8 / 54 GB as bf16, Qwen3.6-27B bnb-4bit (samajlouis) · 17.3 GB download · ~16 GB, nothing extra to install — third-party repack, not published by Qwen, Qwen3.6-27B bnb-4bit (wyzxxywl) · 16.8 GB download · ~16 GB, nothing extra to install — third-party repack, not published by Qwen, Qwen3.6-27B FP8 · 28.8 GB download · ~29 GB — advanced: needs the 'kernels' package plus a Triton kernel download, and leaves no room for the video model beside it, Qwen3.6-27B GGUF Q8_0 · 26.6 GB download · ~30 GB with the adapter — needs ~30 GB of VRAM; lower gpu_layers if it will not fit, Qwen3.6-27B GGUF Q6_K · 21 GB download · ~25 GB with the adapter, Qwen3.6-27B GGUF Q5_K_M · 18.2 GB download · ~22 GB with the adapter, Qwen3.6-27B GGUF Q4_K_M · 15.7 GB download · ~19 GB with the adapter, less if you offload fewer layers, Qwen3.6-27B GGUF IQ4_XS · 14.4 GB download · ~18 GB with the adapter, Qwen3.6-27B GGUF UD-Q3_K_XL · 13.5 GB download · ~17 GB with the adapter, ... +6]
  - model_8b: COMBO[Qwen3-VL-8B-Instruct (official, bf16) · 17.5 GB download · ~8 GB as nf4 / ~13 GB as int8 / ~20 GB as bf16, Qwen3-VL-8B-Instruct GGUF Q4_K_M · 5.4 GB download · ~9 GB with the adapter, Qwen3-VL-8B-Instruct GGUF Q8_0 · 8.8 GB download · ~13 GB with the adapter]
  - quantization_27b: COMBO[nf4, int8, bfloat16, float16] default='nf4'
  - quantization_8b: COMBO[nf4, int8, bfloat16, float16] default='nf4'
  - greedy: BOOLEAN default=True
  - seed: INT default=42 min=0 max=4294967295
  - keep_model_loaded: BOOLEAN default=False
- optional:
  - options: H3_REWRITER_OPTIONS
  - first_frame: IMAGE
  - last_frame: IMAGE
  - frame_switches: STRING default='{}'
  - bypass: BOOLEAN default=False
  - model_omni: COMBO[Qwen2.5-Omni-7B (official, bf16) · 22.4 GB download · ~9 GB as nf4 / ~13 GB as int8 / ~24 GB as bf16, Qwen2.5-Omni-7B GGUF Q4_K_M · 6.2 GB download · ~9 GB with the adapter and a 12k context, Qwen2.5-Omni-7B GGUF Q8_0 · 9.7 GB download · ~13 GB - closer to the bf16 rewrite on a card that has room]
  - quantization_omni: COMBO[nf4, int8, bfloat16, float16] default='nf4'
  - reference_video: VIDEO
  - reference_audio: AUDIO
  - aspect_ratio: STRING,COMBO default=''
  - repeat_last: BOOLEAN default=False
  - library_pick: STRING default=''
- outputs: rewritten_prompt:STRING, integrated_multimodal_description:STRING, overall_soundscape:STRING, non_diegetic_music:STRING, subject_definitions:STRING, summary:STRING, retention_analysis:STRING, detailed_description:STRING, references:H3_REWRITER_REFERENCES

## MiniMaxH3UniversalWriter
module: custom_nodes.MiniMax-H3-Prompt-Rewriter-ComfyUI | category: MiniMax-H3
- required:
  - reference_layout: STRING default='{}'
  - task: COMBO[T2VA, I2VA, FL2VA, L2VA, Ref2VA] default='T2VA'
  - resolution: COMBO[48:9, 32:9, 21:9, 16:9, 4:3, 1:1, 3:4, 9:16] default='16:9'
  - duration: FLOAT,INT default=10.0 min=0.1 max=600.0 step=0.1
  - prompt: STRING default=''
  - caption_model: COMBO[Qwen2.5-Omni-3B · 3.4 GB download · ~5 GB — image, audio and video in one small model; verified against this pack, Qwen2.5-Omni-7B · 5.8 GB download · ~8 GB — same modalities, better prose; step up when the 3B's captions are too plain, Dark Roast Q8 (vl_judge) · ~11 GB — local file, same weights llama-swap serves as vl_judge; vision only, Qwen3-VL-8B abliterated Q8 (local) · 11 GB download · ~12 GB — 5s-lock test, Dark Roast 9B Q8 (local) · 10.4 GB download · ~12 GB — 5s-lock test]
  - caption_length: COMBO[brief, standard, detailed] default='standard'
  - writer_model: COMBO[Qwen3.5-4B · 2.6 GB download · ~5 GB with the guide in context — smallest that still holds the format; start here on an 8 GB card, Qwen3.5-9B · 5.3 GB download · ~8 GB with the guide in context — best writing per gigabyte; lower gpu_layers if 8 GB is tight, Qwen3.5-9B Uncensored (HauhauCS) · 5.2 GB download · ~8 GB with the guide in context — abliterated fine-tune: does not refuse scenes the stock model declines to describe, Gemma 3 12B Instruct · 6.8 GB download · ~10 GB with the guide in context — non-Qwen alternative; its chat template takes no system role, which the node handles, Mistral Small 3.2 24B Instruct · 13.4 GB download · ~17 GB with the guide in context — for a 16 GB card and up, when the 9B's prose is not enough, Qwen3.8-27B Q2_K_XL · 9.2 GB download · ~13 GB with the guide in context — the 27B's prose on a 16 GB card; unsloth's dynamic 2-bit, rougher than the Q4 but still the biggest writer this side of it, Qwen3.8-27B Q3_K_XL · 12.2 GB download · ~16 GB with the guide in context — the middle road: most of the Q4's quality, three gigabytes less to hold, Qwen3.8-27B Q4_K_M · 15.3 GB download · ~19 GB with the guide in context — the strongest prose in the list, for a 24 GB card; newer than the rewriter's own base, but its extra layer is why the 27B LoRA cannot ride it, Qwen3.8-27B Q6_K_XL · 23.6 GB download · ~27 GB with the guide in context — near-lossless, for a 32 GB card - and little room for the video model beside it; lower gpu_layers if it will not fit, Hemmingway-1 Heretic IQ3_M (local) · 12.6 GB download · ~13-14 GB, fit untested on 16 GB — 5s-lock test 2026-10-16, ... +2]
  - greedy: BOOLEAN default=True
  - seed: INT default=42 min=0 max=4294967295
  - keep_model_loaded: BOOLEAN default=False
- optional:
  - options: H3_REWRITER_OPTIONS
  - references: COMFY_AUTOGROW_V3
  - clip: CLIP
  - previous: STRING
  - max_frames: INT default=8 min=1 max=64
  - context_size: INT default=0 min=0 max=131072 step=1024
  - bypass: BOOLEAN default=False
  - reference_instructions: STRING default='{}'
  - system_prompt: STRING default=''
  - aspect_ratio: STRING,COMBO default=''
  - repeat_last: BOOLEAN default=False
  - library_pick: STRING default=''
- outputs: rewritten_prompt:STRING, integrated_multimodal_description:STRING, subject_definitions:STRING, summary:STRING, retention_analysis:STRING, detailed_description:STRING, overall_soundscape:STRING, non_diegetic_music:STRING, reference_assets:STRING, captions:STRING, references:H3_REWRITER_REFERENCES

## MiniMaxH3UpscaleCollect
module: custom_nodes.ComfyUI-MiniMaxH3_LatentUpscaler | category: latent/minimax_h3
- required:
  - package_pipe: H3_PACKAGE_PIPE
  - images: IMAGE
- optional:
  - audio: AUDIO
  - crf: INT default=18 min=0 max=51
- outputs: saved_path:STRING

## MiniMaxH3VAEDecodeFast
module: custom_nodes.ComfyUI-MiniMaxH3_LatentUpscaler | category: latent/minimax_h3
- required:
  - samples: LATENT
  - vae: VAE
  - tiling: BOOLEAN default=True
  - tile_size: INT default=256 min=256 max=4096 step=16
  - tile_overlap: INT default=64 min=16 max=1024 step=16
  - output_device: COMBO[cpu, gpu] default='cpu'
- outputs: images:IMAGE

## MinimaxHailuo03ContextIRNode
module: comfy_api_nodes.nodes_minimax | category: partner/video/MiniMax
- required:
  - model: COMFY_DYNAMICCOMBO_V3
- optional:
  - first_frame: IMAGE
  - last_frame: IMAGE
- outputs: STRING:STRING

## MinimaxHailuo03FirstLastFrameNode
module: comfy_api_nodes.nodes_minimax | category: partner/video/MiniMax
- required:
  - model: COMFY_DYNAMICCOMBO_V3
  - first_frame: IMAGE
  - seed: INT default=42 min=0 max=4294967295 step=1
  - watermark: BOOLEAN default=False
- optional:
  - last_frame: IMAGE
- outputs: VIDEO:VIDEO

## MinimaxHailuo03ReferenceNode
module: comfy_api_nodes.nodes_minimax | category: partner/video/MiniMax
- required:
  - model: COMFY_DYNAMICCOMBO_V3
  - seed: INT default=42 min=0 max=4294967295 step=1
  - watermark: BOOLEAN default=False
- outputs: VIDEO:VIDEO

## MinimaxHailuo03RegenerateNode
module: comfy_api_nodes.nodes_minimax | category: partner/video/MiniMax
- required:
  - model: COMFY_DYNAMICCOMBO_V3
  - video: VIDEO
  - watermark: BOOLEAN default=False
- optional:
  - first_frame: IMAGE
  - last_frame: IMAGE
- outputs: VIDEO:VIDEO

## MinimaxHailuo03TextToVideoNode
module: comfy_api_nodes.nodes_minimax | category: partner/video/MiniMax
- required:
  - model: COMFY_DYNAMICCOMBO_V3
  - seed: INT default=42 min=0 max=4294967295 step=1
  - watermark: BOOLEAN default=False
- outputs: VIDEO:VIDEO

## MinimaxHailuoVideoNode
module: comfy_api_nodes.nodes_minimax | category: partner/video/MiniMax
- required:
  - prompt_text: STRING default=''
- optional:
  - seed: INT default=0 min=0 max=18446744073709551615 step=1
  - first_frame_image: IMAGE
  - prompt_optimizer: BOOLEAN default=True
  - duration: COMBO[6, 10] default=6
  - resolution: COMBO[768P, 1080P] default='768P'
- outputs: VIDEO:VIDEO

## MinimaxImageToVideoNode
module: comfy_api_nodes.nodes_minimax | category: partner/video/MiniMax
- required:
  - image: IMAGE
  - prompt_text: STRING default=''
  - model: COMBO[I2V-01-Director, I2V-01, I2V-01-live] default='I2V-01'
- optional:
  - seed: INT default=0 min=0 max=18446744073709551615 step=1
- outputs: VIDEO:VIDEO

## MiniMaxMusic3TextEncode
module: comfy_extras.nodes_minimax_music | category: model/conditioning/minimax music
- required:
  - clip: CLIP
  - caption: STRING
  - lyrics: STRING
  - seed: INT default=0 min=0 max=18446744073709551615
  - max_duration: FLOAT default=120.0 min=0.04 max=360.0 step=0.04
  - cfg_scale: FLOAT default=1.5 min=0.0 max=100.0 step=0.1
  - top_k: INT default=50 min=1 max=16384
- outputs: CONDITIONING:CONDITIONING, seconds:FLOAT

## MinimaxTextToVideoNode
module: comfy_api_nodes.nodes_minimax | category: partner/video/MiniMax
- required:
  - prompt_text: STRING default=''
  - model: COMBO[T2V-01, T2V-01-Director] default='T2V-01'
- optional:
  - seed: INT default=0 min=0 max=18446744073709551615 step=1
- outputs: VIDEO:VIDEO

## MMH3SpatialSplitParamsV10
module: custom_nodes.Comfyui_Minimax_h3_latent_Upscaler | category: latent/upscale/minimax
- required:
  - tile_width: INT default=512 min=64 max=16384 step=32
  - tile_height: INT default=512 min=64 max=16384 step=32
  - overlap_ratio: FLOAT default=0.25 min=0.0 max=0.9 step=0.05
  - fade_ratio: FLOAT default=0.5 min=0.0 max=1.0 step=0.05
  - min_tile_size: INT default=256 min=0 max=16384 step=32
  - seam_denoise: FLOAT default=1.0 min=0.1 max=1.0 step=0.05
- outputs: spatial_split_param:H3_SPATIAL_PARAM_V10, grid_preview:STRING

## MMH3SplitUpscale
module: custom_nodes.Comfyui_Minimax_h3_latent_Upscaler | category: latent/upscale/minimax
- required:
  - model: MODEL
  - conditioning: CONDITIONING
  - latent: LATENT
  - noise: NOISE
  - sampler: SAMPLER
  - sigmas: SIGMAS
  - cfg: FLOAT default=1.0 min=0.0 max=100.0 step=0.1
  - seam_polish: COMBO[off, auto, all] default='off'
  - color_match: BOOLEAN default=True
- optional:
  - negative: CONDITIONING
  - temporal_split_param: H3_TEMPORAL_PARAM_V10
  - spatial_split_param: H3_SPATIAL_PARAM_V10
- outputs: latent:LATENT

## MMH3TemporalSplitParamsV10
module: custom_nodes.Comfyui_Minimax_h3_latent_Upscaler | category: latent/upscale/minimax
- required:
  - chunk_frames: INT default=73 min=5 max=100000 step=1
  - temporal_overlap_frames: INT default=22 min=0 max=100000 step=1
  - anchor_strength: FLOAT default=0.999 min=0.0 max=1.0 step=0.001
  - motion_anchor_frames: COMBO[0, 5, 22, 39] default='22'
  - identity_anchor_frames: INT default=24 min=0 max=240 step=1
- outputs: temporal_split_param:H3_TEMPORAL_PARAM_V10

## ModelAttentionBackend
module: comfy_extras.nodes_model_advanced | category: model/patch
- required:
  - model: MODEL
  - attention: COMBO[pytorch attention, comfy kitchen attention] default='pytorch attention'
- outputs: model:MODEL

## ModelCompile+
module: custom_nodes.ComfyUI_essentials | category: essentials/utilities
- required:
  - model: MODEL
  - fullgraph: BOOLEAN default=False
  - dynamic: BOOLEAN default=False
  - mode: COMBO[default, reduce-overhead, max-autotune, max-autotune-no-cudagraphs]
- outputs: MODEL:MODEL

## ModelComputeDtype
module: comfy_extras.nodes_model_advanced | category: advanced/debug
- required:
  - model: MODEL
  - dtype: COMBO[default, fp32, fp16, bf16]
- outputs: MODEL:MODEL

## ModelForwardProbe
module: custom_nodes.10S-Comfy-nodes | category: 10S Nodes/Debug
- required:
  - model: MODEL
- optional:
  - kwargs_to_check: STRING default='memory_video, paired_audio_memory, memory_audio, prior_video...'
  - substring_search: STRING default='memory, shot, prior, bank, paired'
  - max_depth: INT default=6 min=1 max=12
- outputs: model:MODEL, report:STRING

## ModelMemoryUsageFactorOverride
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/memory
- required:
  - model: MODEL
  - memory_usage_factor: FLOAT default=1.0 min=0.0 max=100.0 step=0.001
- outputs: MODEL:MODEL

## ModelMemoryUseReportPatch
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/memory
- required:
  - model: MODEL
- outputs: MODEL:MODEL

## ModelMergeAdd
module: comfy_extras.nodes_model_merging | category: model/merging
- required:
  - model1: MODEL
  - model2: MODEL
- outputs: MODEL:MODEL

## ModelMergeAuraflow
module: comfy_extras.nodes_model_merging_model_specific | category: model/merging/model specific
- required:
  - model1: MODEL
  - model2: MODEL
  - init_x_linear.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - positional_encoding: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - cond_seq_linear.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - register_tokens: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - t_embedder.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - double_layers.0.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - double_layers.1.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - double_layers.2.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - double_layers.3.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_layers.0.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_layers.1.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_layers.2.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_layers.3.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_layers.4.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_layers.5.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_layers.6.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_layers.7.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_layers.8.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_layers.9.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_layers.10.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_layers.11.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_layers.12.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_layers.13.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_layers.14.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_layers.15.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_layers.16.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_layers.17.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_layers.18.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_layers.19.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_layers.20.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_layers.21.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_layers.22.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_layers.23.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_layers.24.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_layers.25.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_layers.26.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_layers.27.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_layers.28.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_layers.29.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_layers.30.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_layers.31.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - modF.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - final_linear.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: MODEL:MODEL

## ModelMergeBlocks
module: comfy_extras.nodes_model_merging | category: model/merging
- required:
  - model1: MODEL
  - model2: MODEL
  - input: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - middle: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - out: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: MODEL:MODEL

## ModelMergeCosmos14B
module: comfy_extras.nodes_model_merging_model_specific | category: model/merging/model specific
- required:
  - model1: MODEL
  - model2: MODEL
  - pos_embedder.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - extra_pos_embedder.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - x_embedder.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - t_embedder.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - affline_norm.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block0.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block1.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block2.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block3.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block4.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block5.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block6.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block7.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block8.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block9.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block10.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block11.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block12.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block13.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block14.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block15.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block16.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block17.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block18.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block19.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block20.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block21.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block22.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block23.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block24.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block25.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block26.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block27.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block28.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block29.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block30.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block31.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block32.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block33.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block34.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block35.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - final_layer.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: MODEL:MODEL

## ModelMergeCosmos7B
module: comfy_extras.nodes_model_merging_model_specific | category: model/merging/model specific
- required:
  - model1: MODEL
  - model2: MODEL
  - pos_embedder.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - extra_pos_embedder.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - x_embedder.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - t_embedder.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - affline_norm.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block0.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block1.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block2.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block3.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block4.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block5.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block6.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block7.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block8.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block9.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block10.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block11.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block12.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block13.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block14.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block15.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block16.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block17.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block18.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block19.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block20.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block21.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block22.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block23.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block24.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block25.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block26.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.block27.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - final_layer.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: MODEL:MODEL

## ModelMergeCosmosPredict2_14B
module: comfy_extras.nodes_model_merging_model_specific | category: model/merging/model specific
- required:
  - model1: MODEL
  - model2: MODEL
  - pos_embedder.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - x_embedder.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - t_embedder.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - t_embedding_norm.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.0.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.1.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.2.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.3.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.4.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.5.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.6.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.7.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.8.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.9.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.10.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.11.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.12.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.13.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.14.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.15.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.16.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.17.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.18.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.19.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.20.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.21.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.22.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.23.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.24.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.25.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.26.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.27.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.28.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.29.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.30.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.31.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.32.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.33.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.34.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.35.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - final_layer.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: MODEL:MODEL

## ModelMergeCosmosPredict2_2B
module: comfy_extras.nodes_model_merging_model_specific | category: model/merging/model specific
- required:
  - model1: MODEL
  - model2: MODEL
  - pos_embedder.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - x_embedder.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - t_embedder.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - t_embedding_norm.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.0.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.1.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.2.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.3.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.4.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.5.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.6.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.7.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.8.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.9.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.10.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.11.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.12.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.13.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.14.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.15.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.16.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.17.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.18.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.19.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.20.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.21.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.22.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.23.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.24.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.25.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.26.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.27.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - final_layer.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: MODEL:MODEL

## ModelMergeFlux1
module: comfy_extras.nodes_model_merging_model_specific | category: model/merging/model specific
- required:
  - model1: MODEL
  - model2: MODEL
  - img_in.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - time_in.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - guidance_in: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - vector_in.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - txt_in.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - double_blocks.0.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - double_blocks.1.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - double_blocks.2.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - double_blocks.3.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - double_blocks.4.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - double_blocks.5.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - double_blocks.6.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - double_blocks.7.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - double_blocks.8.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - double_blocks.9.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - double_blocks.10.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - double_blocks.11.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - double_blocks.12.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - double_blocks.13.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - double_blocks.14.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - double_blocks.15.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - double_blocks.16.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - double_blocks.17.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - double_blocks.18.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.0.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.1.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.2.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.3.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.4.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.5.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.6.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.7.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.8.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.9.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.10.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.11.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.12.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.13.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.14.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.15.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.16.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.17.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.18.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.19.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.20.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.21.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.22.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.23.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.24.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.25.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.26.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.27.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.28.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.29.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.30.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.31.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.32.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.33.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.34.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.35.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.36.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - single_blocks.37.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - final_layer.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: MODEL:MODEL

## ModelMergeKrea2
module: comfy_extras.nodes_model_merging_model_specific | category: model/merging/model specific
- required:
  - model1: MODEL
  - model2: MODEL
  - first.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - tmlp.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - txtmlp.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - tproj.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - txtfusion.layerwise_blocks.0.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - txtfusion.layerwise_blocks.1.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - txtfusion.projector.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - txtfusion.refiner_blocks.0.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - txtfusion.refiner_blocks.1.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.0.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.1.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.2.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.3.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.4.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.5.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.6.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.7.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.8.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.9.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.10.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.11.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.12.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.13.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.14.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.15.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.16.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.17.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.18.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.19.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.20.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.21.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.22.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.23.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.24.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.25.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.26.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.27.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - last.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: MODEL:MODEL

## ModelMergeLTXV
module: comfy_extras.nodes_model_merging_model_specific | category: model/merging/model specific
- required:
  - model1: MODEL
  - model2: MODEL
  - patchify_proj.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - adaln_single.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - caption_projection.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.0.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.1.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.2.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.3.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.4.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.5.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.6.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.7.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.8.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.9.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.10.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.11.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.12.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.13.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.14.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.15.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.16.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.17.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.18.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.19.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.20.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.21.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.22.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.23.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.24.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.25.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.26.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.27.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - scale_shift_table: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - proj_out.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: MODEL:MODEL

## ModelMergeMochiPreview
module: comfy_extras.nodes_model_merging_model_specific | category: model/merging/model specific
- required:
  - model1: MODEL
  - model2: MODEL
  - pos_frequencies.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - t_embedder.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - t5_y_embedder.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - t5_yproj.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.0.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.1.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.2.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.3.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.4.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.5.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.6.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.7.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.8.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.9.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.10.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.11.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.12.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.13.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.14.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.15.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.16.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.17.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.18.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.19.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.20.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.21.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.22.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.23.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.24.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.25.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.26.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.27.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.28.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.29.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.30.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.31.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.32.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.33.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.34.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.35.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.36.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.37.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.38.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.39.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.40.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.41.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.42.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.43.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.44.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.45.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.46.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.47.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - final_layer.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: MODEL:MODEL

## ModelMergeQwenImage
module: comfy_extras.nodes_model_merging_model_specific | category: model/merging/model specific
- required:
  - model1: MODEL
  - model2: MODEL
  - pos_embeds.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - img_in.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - txt_norm.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - txt_in.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - time_text_embed.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.0.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.1.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.2.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.3.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.4.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.5.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.6.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.7.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.8.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.9.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.10.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.11.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.12.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.13.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.14.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.15.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.16.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.17.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.18.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.19.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.20.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.21.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.22.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.23.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.24.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.25.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.26.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.27.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.28.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.29.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.30.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.31.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.32.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.33.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.34.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.35.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.36.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.37.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.38.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.39.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.40.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.41.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.42.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.43.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.44.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.45.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.46.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.47.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.48.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.49.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.50.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.51.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.52.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.53.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.54.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.55.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.56.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.57.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.58.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - transformer_blocks.59.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - proj_out.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: MODEL:MODEL

## ModelMergeSD1
module: comfy_extras.nodes_model_merging_model_specific | category: model/merging/model specific
- required:
  - model1: MODEL
  - model2: MODEL
  - time_embed.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - label_emb.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - input_blocks.0.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - input_blocks.1.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - input_blocks.2.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - input_blocks.3.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - input_blocks.4.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - input_blocks.5.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - input_blocks.6.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - input_blocks.7.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - input_blocks.8.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - input_blocks.9.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - input_blocks.10.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - input_blocks.11.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - middle_block.0.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - middle_block.1.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - middle_block.2.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - output_blocks.0.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - output_blocks.1.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - output_blocks.2.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - output_blocks.3.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - output_blocks.4.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - output_blocks.5.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - output_blocks.6.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - output_blocks.7.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - output_blocks.8.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - output_blocks.9.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - output_blocks.10.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - output_blocks.11.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - out.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: MODEL:MODEL

## ModelMergeSD2
module: comfy_extras.nodes_model_merging_model_specific | category: model/merging/model specific
- required:
  - model1: MODEL
  - model2: MODEL
  - time_embed.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - label_emb.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - input_blocks.0.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - input_blocks.1.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - input_blocks.2.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - input_blocks.3.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - input_blocks.4.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - input_blocks.5.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - input_blocks.6.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - input_blocks.7.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - input_blocks.8.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - input_blocks.9.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - input_blocks.10.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - input_blocks.11.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - middle_block.0.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - middle_block.1.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - middle_block.2.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - output_blocks.0.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - output_blocks.1.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - output_blocks.2.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - output_blocks.3.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - output_blocks.4.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - output_blocks.5.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - output_blocks.6.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - output_blocks.7.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - output_blocks.8.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - output_blocks.9.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - output_blocks.10.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - output_blocks.11.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - out.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: MODEL:MODEL

## ModelMergeSD35_Large
module: comfy_extras.nodes_model_merging_model_specific | category: model/merging/model specific
- required:
  - model1: MODEL
  - model2: MODEL
  - pos_embed.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - x_embedder.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - context_embedder.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - y_embedder.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - t_embedder.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.0.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.1.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.2.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.3.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.4.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.5.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.6.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.7.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.8.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.9.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.10.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.11.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.12.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.13.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.14.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.15.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.16.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.17.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.18.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.19.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.20.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.21.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.22.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.23.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.24.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.25.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.26.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.27.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.28.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.29.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.30.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.31.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.32.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.33.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.34.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.35.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.36.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.37.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - final_layer.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: MODEL:MODEL

## ModelMergeSD3_2B
module: comfy_extras.nodes_model_merging_model_specific | category: model/merging/model specific
- required:
  - model1: MODEL
  - model2: MODEL
  - pos_embed.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - x_embedder.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - context_embedder.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - y_embedder.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - t_embedder.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.0.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.1.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.2.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.3.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.4.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.5.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.6.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.7.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.8.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.9.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.10.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.11.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.12.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.13.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.14.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.15.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.16.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.17.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.18.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.19.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.20.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.21.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.22.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - joint_blocks.23.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - final_layer.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: MODEL:MODEL

## ModelMergeSDXL
module: comfy_extras.nodes_model_merging_model_specific | category: model/merging/model specific
- required:
  - model1: MODEL
  - model2: MODEL
  - time_embed.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - label_emb.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - input_blocks.0: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - input_blocks.1: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - input_blocks.2: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - input_blocks.3: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - input_blocks.4: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - input_blocks.5: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - input_blocks.6: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - input_blocks.7: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - input_blocks.8: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - middle_block.0: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - middle_block.1: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - middle_block.2: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - output_blocks.0: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - output_blocks.1: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - output_blocks.2: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - output_blocks.3: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - output_blocks.4: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - output_blocks.5: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - output_blocks.6: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - output_blocks.7: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - output_blocks.8: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - out.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: MODEL:MODEL

## ModelMergeSimple
module: comfy_extras.nodes_model_merging | category: model/merging
- required:
  - model1: MODEL
  - model2: MODEL
  - ratio: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: MODEL:MODEL

## ModelMergeSubtract
module: comfy_extras.nodes_model_merging | category: model/merging
- required:
  - model1: MODEL
  - model2: MODEL
  - multiplier: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
- outputs: MODEL:MODEL

## ModelMergeWAN2_1
module: comfy_extras.nodes_model_merging_model_specific | category: model/merging/model specific
- required:
  - model1: MODEL
  - model2: MODEL
  - patch_embedding.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - time_embedding.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - time_projection.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - text_embedding.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - img_emb.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.0.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.1.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.2.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.3.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.4.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.5.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.6.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.7.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.8.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.9.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.10.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.11.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.12.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.13.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.14.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.15.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.16.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.17.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.18.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.19.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.20.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.21.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.22.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.23.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.24.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.25.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.26.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.27.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.28.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.29.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.30.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.31.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.32.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.33.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.34.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.35.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.36.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.37.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.38.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - blocks.39.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - head.: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: MODEL:MODEL

## ModelNoiseScale
module: comfy_extras.nodes_model_advanced | category: model/patch
- required:
  - model: MODEL
  - noise_scale: FLOAT default=1.0 min=0.0 max=64.0 step=0.01
- outputs: MODEL:MODEL

## ModelPassThrough
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/misc
- optional:
  - model: MODEL
- outputs: model:MODEL

## ModelPatchLoader
module: comfy_extras.nodes_model_patch | category: model/loaders
- required:
  - name: COMBO[]
- outputs: MODEL_PATCH:MODEL_PATCH

## ModelPatchTorchSettings
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/experimental
- required:
  - model: MODEL
  - enable_fp16_accumulation: BOOLEAN default=False
- outputs: MODEL:MODEL

## ModelPreviewOverrideKJ
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/sampling
- required:
  - model: MODEL
  - max_resolution: INT default=1024 min=0 max=8192 step=8
  - jpeg_quality: INT default=80 min=30 max=100 step=1
  - suppress_default_preview: BOOLEAN default=True
  - preview_frames: INT default=1 min=1 max=1024 step=1
  - preview_fps: INT default=12 min=1 max=60 step=1
- optional:
  - vae: VAE
- outputs: MODEL:MODEL

## ModelSamplingAuraFlow
module: comfy_extras.nodes_model_advanced | category: model/patch
- required:
  - model: MODEL
  - shift: FLOAT default=1.73 min=0.0 max=100.0 step=0.01
- optional:
  - sampling: COMBO[flow, img_to_img_velocity] default='flow'
- outputs: MODEL:MODEL

## ModelSamplingContinuousEDM
module: comfy_extras.nodes_model_advanced | category: model/patch
- required:
  - model: MODEL
  - sampling: COMBO[v_prediction, edm, edm_playground_v2.5, eps, cosmos_rflow]
  - sigma_max: FLOAT default=120.0 min=0.0 max=1000.0 step=0.001
  - sigma_min: FLOAT default=0.002 min=0.0 max=1000.0 step=0.001
- outputs: MODEL:MODEL

## ModelSamplingContinuousV
module: comfy_extras.nodes_model_advanced | category: model/patch
- required:
  - model: MODEL
  - sampling: COMBO[v_prediction]
  - sigma_max: FLOAT default=500.0 min=0.0 max=1000.0 step=0.001
  - sigma_min: FLOAT default=0.03 min=0.0 max=1000.0 step=0.001
- outputs: MODEL:MODEL

## ModelSamplingDiscrete
module: comfy_extras.nodes_model_advanced | category: model/patch
- required:
  - model: MODEL
  - sampling: COMBO[eps, v_prediction, lcm, x0, img_to_img, img_to_img_flow]
  - zsnr: BOOLEAN default=False
- outputs: MODEL:MODEL

## ModelSamplingFlux
module: comfy_extras.nodes_model_advanced | category: model/patch/flux
- required:
  - model: MODEL
  - max_shift: FLOAT default=1.15 min=0.0 max=100.0 step=0.01
  - base_shift: FLOAT default=0.5 min=0.0 max=100.0 step=0.01
  - width: INT default=1024 min=16 max=16384 step=8
  - height: INT default=1024 min=16 max=16384 step=8
- outputs: MODEL:MODEL

## ModelSamplingLTXV
module: comfy_extras.nodes_lt | category: model/patch/ltxv
- required:
  - model: MODEL
  - max_shift: FLOAT default=2.05 min=0.0 max=100.0 step=0.01
  - base_shift: FLOAT default=0.95 min=0.0 max=100.0 step=0.01
- optional:
  - latent: LATENT
- outputs: MODEL:MODEL

## ModelSamplingSD3
module: comfy_extras.nodes_model_advanced | category: model/patch/stable diffusion
- required:
  - model: MODEL
  - shift: FLOAT default=3.0 min=0.0 max=100.0 step=0.01
- outputs: MODEL:MODEL

## ModelSamplingSD3Advanced+
module: custom_nodes.ComfyUI_essentials | category: essentials/sampling
- required:
  - model: MODEL
  - shift: FLOAT default=3.0 min=0.0 max=100.0 step=0.01
  - cut_off: FLOAT default=0.5 min=0.0 max=1.0 step=0.05
  - shift_multiplier: FLOAT default=2 min=0 max=10 step=0.05
- outputs: MODEL:MODEL

## ModelSamplingStableCascade
module: comfy_extras.nodes_model_advanced | category: model/patch/stable cascade
- required:
  - model: MODEL
  - shift: FLOAT default=2.0 min=0.0 max=100.0 step=0.01
- outputs: MODEL:MODEL

## ModelSave
module: comfy_extras.nodes_model_merging | category: model/merging
- required:
  - model: MODEL
  - filename_prefix: STRING default='diffusion_models/ComfyUI'
- outputs: 

## ModelSaveKJ
module: custom_nodes.ComfyUI-KJNodes | category: advanced/model_merging
- required:
  - model: MODEL
  - filename_prefix: STRING default='diffusion_models/ComfyUI'
  - model_key_prefix: STRING default='model.diffusion_model.'
- outputs: 

## ModelSelector
module: custom_nodes.ControlFlowUtils | category: 🐺 VykosX-ControlFlowUtils
- required:
  - checkpoints: COMBO[]
- optional:
  - run_after: * default=''
- outputs: Checkpoint:*

## MoGeGeometryToFOV
module: comfy_extras.nodes_moge | category: image/geometry estimation
- required:
  - moge_geometry: MOGE_GEOMETRY
  - axis: COMBO[vertical, horizontal, diagonal] default='vertical'
  - unit: COMBO[degrees, radians] default='degrees'
- outputs: fov:FLOAT, focal_pixels:FLOAT

## MoGeInference
module: comfy_extras.nodes_moge | category: image/geometry estimation
- required:
  - moge_model: MOGE_MODEL
  - image: IMAGE
  - resolution_level: INT default=9 min=0 max=9
  - fov_x_degrees: FLOAT default=0.0 min=0.0 max=170.0 step=0.1
  - batch_size: INT default=4 min=1 max=64
  - force_projection: BOOLEAN default=True
  - apply_mask: BOOLEAN default=True
  - refine_steps: INT default=3 min=0 max=8
- outputs: moge_geometry:MOGE_GEOMETRY

## MoGePanoramaInference
module: comfy_extras.nodes_moge | category: image/geometry estimation
- required:
  - moge_model: MOGE_MODEL
  - image: IMAGE
  - resolution_level: INT default=9 min=0 max=9
  - split_resolution: INT default=512 min=256 max=1024
  - merge_resolution: INT default=1920 min=256 max=8192
  - batch_size: INT default=4 min=1 max=12
  - refine_steps: INT default=3 min=0 max=8
- outputs: moge_geometry:MOGE_GEOMETRY

## MoGePointMapToMesh
module: comfy_extras.nodes_moge | category: image/geometry estimation
- required:
  - moge_geometry: MOGE_GEOMETRY
  - batch_index: INT default=0 min=0 max=4096
  - decimation: INT default=1 min=1 max=8
  - discontinuity_threshold: FLOAT default=0.04 min=0.0 max=1.0 step=0.01
  - texture: BOOLEAN default=True
- outputs: MESH:MESH

## MoGeRender
module: comfy_extras.nodes_moge | category: image/geometry estimation
- required:
  - moge_geometry: MOGE_GEOMETRY
  - output: COMBO[depth, depth_colored, normal_opengl, normal_directx, mask] default='depth'
- outputs: IMAGE:IMAGE

## Morphology
module: comfy_extras.nodes_morphology | category: image/filters
- required:
  - image: IMAGE
  - operation: COMBO[erode, dilate, open, close, gradient, bottom_hat, top_hat]
  - kernel_size: INT default=3 min=3 max=999 step=1
- outputs: IMAGE:IMAGE

## MultiGPU_WorkUnits
module: comfy_extras.nodes_multigpu | category: advanced/multigpu
- required:
  - model: MODEL
  - max_gpus: INT default=2 min=1 step=1
- outputs: MODEL:MODEL

## NABLA_AttentionKJ
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/experimental
- required:
  - model: MODEL
  - latent: LATENT
  - window_time: INT default=11 min=1
  - window_width: INT default=3 min=1
  - window_height: INT default=3 min=1
  - sparsity: FLOAT default=0.9 min=0.0 max=1.0 step=0.01
  - torch_compile: BOOLEAN default=True
- outputs: MODEL:MODEL

## NAGuidance
module: comfy_extras.nodes_nag | category: advanced/guidance
- required:
  - model: MODEL
  - nag_scale: FLOAT default=5.0 min=0.0 max=50.0 step=0.1
  - nag_alpha: FLOAT default=0.5 min=0.0 max=1.0 step=0.01
  - nag_tau: FLOAT default=1.5 min=1.0 max=10.0 step=0.01
- outputs: MODEL:MODEL

## NoiseFromImage+
module: custom_nodes.ComfyUI_essentials | category: essentials/image utils
- required:
  - image: IMAGE
  - noise_strenght: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - noise_size: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - color_noise: FLOAT default=0.2 min=0.0 max=1.0 step=0.01
  - mask_strength: FLOAT default=0.5 min=0.0 max=1.0 step=0.01
  - mask_scale_diff: FLOAT default=0.0 min=0.0 max=1.0 step=0.01
  - mask_contrast: FLOAT default=1.0 min=0.0 max=100.0 step=0.1
  - saturation: FLOAT default=2.0 min=0.0 max=100.0 step=0.1
  - contrast: FLOAT default=1.0 min=0.0 max=100.0 step=0.1
  - blur: FLOAT default=1.0 min=0.0 max=10.0 step=0.1
- optional:
  - noise_mask: IMAGE
- outputs: IMAGE:IMAGE

## NormalizedAmplitudeToFloatList
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/audio
- required:
  - normalized_amp: NORMALIZED_AMPLITUDE
- outputs: FLOAT:FLOAT

## NormalizedAmplitudeToMask
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/audio
- required:
  - normalized_amp: NORMALIZED_AMPLITUDE
  - width: INT default=512 min=16 max=4096 step=1
  - height: INT default=512 min=16 max=4096 step=1
  - frame_offset: INT default=0 min=-255 max=255 step=1
  - location_x: INT default=256 min=0 max=4096 step=1
  - location_y: INT default=256 min=0 max=4096 step=1
  - size: INT default=128 min=8 max=4096 step=1
  - shape: COMBO[none, circle, square, triangle] default='none'
  - color: COMBO[white, amplitude] default='amplitude'
- outputs: MASK:MASK

## NormalizeImages
module: comfy_extras.nodes_dataset | category: image/color
- required:
  - images: IMAGE
  - mean: FLOAT default=0.5 min=0.0 max=1.0
  - std: FLOAT default=0.5 min=0.001 max=1.0
- outputs: images:IMAGE

## NormalizeVideoLatentStart
module: comfy_extras.nodes_kandinsky5 | category: model/conditioning
- required:
  - latent: LATENT
  - start_frame_count: INT default=4 min=1 max=16384 step=1
  - reference_frame_count: INT default=5 min=1 max=16384 step=1
- outputs: latent:LATENT

## NullInput
module: custom_nodes.ControlFlowUtils | category: 🐺 VykosX-ControlFlowUtils
- required:
  - NULL: *
- optional:
  - NULL2: *
  - NULL3: *
  - NULL4: *
  - NULL5: *
  - NULL6: *
- outputs: 

## NullOutput
module: custom_nodes.ControlFlowUtils | category: 🐺 VykosX-ControlFlowUtils
- outputs: NULL:*

## OffsetMask
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking
- required:
  - mask: MASK
  - x: INT default=0 min=-4096 max=16384 step=1
  - y: INT default=0 min=-4096 max=16384 step=1
  - angle: INT default=0 min=-360 max=360 step=1
  - duplication_factor: INT default=1 min=1 max=1000 step=1
  - roll: BOOLEAN default=False
  - incremental: BOOLEAN default=False
  - padding_mode: COMBO[empty, border, reflection] default='empty'
- outputs: mask:MASK

## OffsetMaskByNormalizedAmplitude
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/audio
- required:
  - normalized_amp: NORMALIZED_AMPLITUDE
  - mask: MASK
  - x: INT default=0 min=-4096 max=16384 step=1
  - y: INT default=0 min=-4096 max=16384 step=1
  - rotate: BOOLEAN default=False
  - angle_multiplier: FLOAT default=0.0 min=-1.0 max=1.0 step=0.001
- outputs: mask:MASK

## OneFormer-ADE20K-SemSegPreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Semantic Segmentation
- required:
  - image: IMAGE
- optional:
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## OneFormer-COCO-SemSegPreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Semantic Segmentation
- required:
  - image: IMAGE
- optional:
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## OpenAIChatConfig
module: comfy_api_nodes.nodes_openai | category: partner/text/OpenAI
- required:
  - truncation: COMBO[auto, disabled] default='auto'
- optional:
  - max_output_tokens: INT default=4096 min=16 max=16384
  - instructions: STRING
  - reasoning_effort: COMBO[default, none, minimal, low, medium, high, xhigh, max] default='default'
- outputs: OPENAI_CHAT_CONFIG:OPENAI_CHAT_CONFIG

## OpenAIChatNode
module: comfy_api_nodes.nodes_openai | category: partner/text/OpenAI
- required:
  - prompt: STRING default=''
  - persist_context: BOOLEAN default=False
  - model: COMBO[gpt-6-astra, gpt-6-sol, gpt-6-luna, gpt-5.6-sol, gpt-5.6-terra, gpt-5.6-luna, gpt-5.5-pro, gpt-5.5, gpt-5, gpt-5-mini, ... +8]
- optional:
  - images: IMAGE
  - files: OPENAI_INPUT_FILES
  - advanced_options: OPENAI_CHAT_CONFIG
- outputs: STRING:STRING

## OpenAIGPTImage1
module: comfy_api_nodes.nodes_openai | category: partner/image/OpenAI
- required:
  - prompt: STRING default=''
- optional:
  - seed: INT default=0 min=0 max=2147483647 step=1
  - quality: COMBO[low, medium, high] default='low'
  - background: COMBO[auto, opaque, transparent] default='auto'
  - size: COMBO[auto, 1024x1024, 1024x1536, 1536x1024, 2048x2048, 2048x1152, 1152x2048, 3840x2160, 2160x3840, Custom] default='auto'
  - n: INT default=1 min=1 max=8 step=1
  - image: IMAGE
  - mask: MASK
  - model: COMBO[gpt-image-1, gpt-image-1.5, gpt-image-2] default='gpt-image-2'
  - custom_width: INT default=1024 min=1024 max=3840 step=16
  - custom_height: INT default=1024 min=1024 max=3840 step=16
- outputs: IMAGE:IMAGE

## OpenAIGPTImageNodeV2
module: comfy_api_nodes.nodes_openai | category: partner/image/OpenAI
- required:
  - prompt: STRING default=''
  - model: COMFY_DYNAMICCOMBO_V3
  - n: INT default=1 min=1 max=8 step=1
  - seed: INT default=0 min=0 max=2147483647 step=1
- outputs: IMAGE:IMAGE

## OpenAIInputFiles
module: comfy_api_nodes.nodes_openai | category: partner/text/OpenAI
- required:
  - file: COMBO[]
- optional:
  - OPENAI_INPUT_FILES: OPENAI_INPUT_FILES
- outputs: OPENAI_INPUT_FILES:OPENAI_INPUT_FILES

## OpenposePreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Faces and Poses Estimators
- required:
  - image: IMAGE
- optional:
  - detect_hand: COMBO[enable, disable] default='enable'
  - detect_body: COMBO[enable, disable] default='enable'
  - detect_face: COMBO[enable, disable] default='enable'
  - resolution: INT default=512 min=64 max=16384 step=64
  - scale_stick_for_xinsr_cn: COMBO[disable, enable] default='disable'
- outputs: IMAGE:IMAGE, POSE_KEYPOINT:POSE_KEYPOINT

## OpenRouterImageNode
module: comfy_api_nodes.nodes_openrouter | category: partner/image/OpenRouter
- required:
  - model: COMFY_DYNAMICCOMBO_V3
- outputs: IMAGE:IMAGE

## OpenRouterLLMNode
module: comfy_api_nodes.nodes_openrouter | category: partner/text/OpenRouter
- required:
  - prompt: STRING default=''
  - model: COMFY_DYNAMICCOMBO_V3
  - seed: INT default=0 min=0 max=2147483647
- optional:
  - system_prompt: STRING default=''
- outputs: STRING:STRING

## OpticalFlowLoader
module: comfy_extras.nodes_void | category: model/loaders
- required:
  - model_name: COMBO[]
- outputs: OPTICAL_FLOW:OPTICAL_FLOW

## OptimalStepsScheduler
module: comfy_extras.nodes_optimalsteps | category: model/sampling/schedulers
- required:
  - model_type: COMBO[FLUX, Wan, Chroma]
  - steps: INT default=20 min=3 max=1000
  - denoise: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: SIGMAS:SIGMAS

## PadImageBatchInterleaved
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - images: IMAGE
  - empty_frames_per_image: INT default=1 min=0 max=4096 step=1
  - pad_frame_value: FLOAT default=0.0 min=0.0 max=1.0 step=0.01
  - add_after_last: BOOLEAN default=False
- outputs: images:IMAGE, masks:MASK

## Painter
module: comfy_extras.nodes_painter | category: image
- required:
  - mask: STRING default=''
  - width: INT default=512 min=64 max=4096 step=64
  - height: INT default=512 min=64 max=4096 step=64
  - bg_color: COLOR default='#000000'
- optional:
  - image: IMAGE
- outputs: IMAGE:IMAGE, MASK:MASK

## PaintMesh
module: comfy_extras.nodes_mesh_postprocess | category: 3d/mesh
- required:
  - mesh: MESH
  - voxel_colors: VOXEL
- outputs: mesh:MESH

## PairConditioningCombine
module: comfy_extras.nodes_hooks | category: advanced/hooks/cond pair
- required:
  - positive_A: CONDITIONING
  - negative_A: CONDITIONING
  - positive_B: CONDITIONING
  - negative_B: CONDITIONING
- outputs: positive:CONDITIONING, negative:CONDITIONING

## PairConditioningSetDefaultCombine
module: comfy_extras.nodes_hooks | category: advanced/hooks/cond pair
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - positive_DEFAULT: CONDITIONING
  - negative_DEFAULT: CONDITIONING
- optional:
  - hooks: HOOKS
- outputs: positive:CONDITIONING, negative:CONDITIONING

## PairConditioningSetProperties
module: comfy_extras.nodes_hooks | category: advanced/hooks/cond pair
- required:
  - positive_NEW: CONDITIONING
  - negative_NEW: CONDITIONING
  - strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - set_cond_area: COMBO[default, mask bounds]
- optional:
  - mask: MASK
  - hooks: HOOKS
  - timesteps: TIMESTEPS_RANGE
- outputs: positive:CONDITIONING, negative:CONDITIONING

## PairConditioningSetPropertiesAndCombine
module: comfy_extras.nodes_hooks | category: advanced/hooks/cond pair
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - positive_NEW: CONDITIONING
  - negative_NEW: CONDITIONING
  - strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - set_cond_area: COMBO[default, mask bounds]
- optional:
  - mask: MASK
  - hooks: HOOKS
  - timesteps: TIMESTEPS_RANGE
- outputs: positive:CONDITIONING, negative:CONDITIONING

## PatchFlashAttentionKJ
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/experimental
- required:
  - model: MODEL
- optional:
  - allow_compile: BOOLEAN default=False
- outputs: MODEL:MODEL

## PatchModelAddDownscale
module: comfy_extras.nodes_model_downscale | category: model/patch/unet
- required:
  - model: MODEL
  - block_number: INT default=3 min=1 max=32 step=1
  - downscale_factor: FLOAT default=2.0 min=0.1 max=9.0 step=0.001
  - start_percent: FLOAT default=0.0 min=0.0 max=1.0 step=0.001
  - end_percent: FLOAT default=0.35 min=0.0 max=1.0 step=0.001
  - downscale_after_skip: BOOLEAN default=True
  - downscale_method: COMBO[bicubic, nearest-exact, bilinear, area, bislerp]
  - upscale_method: COMBO[bicubic, nearest-exact, bilinear, area, bislerp]
- outputs: MODEL:MODEL

## PatchModelPatcherOrder
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/deprecated
- required:
  - model: MODEL
  - patch_order: COMBO[object_patch_first, weight_patch_first] default='weight_patch_first'
  - full_load: COMBO[enabled, disabled, auto] default='auto'
- outputs: MODEL:MODEL

## PatchTritonVAE
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/experimental
- required:
  - vae: VAE
  - fuse_norm_silu: BOOLEAN default=True
  - channels_last: BOOLEAN default=True
  - autotune: BOOLEAN default=False
- outputs: vae:VAE

## PathchSageAttentionKJ
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/experimental
- required:
  - model: MODEL
  - sage_attention: COMBO[disabled, auto, sageattn_qk_int8_pv_fp16_cuda, sageattn_qk_int8_pv_fp16_triton, sageattn_qk_int8_pv_fp8_cuda, sageattn_qk_int8_pv_fp8_cuda++, sageattn3, sageattn3_per_block_mean] default=False
- optional:
  - allow_compile: BOOLEAN default=False
- outputs: MODEL:MODEL

## PerpNeg
module: comfy_extras.nodes_perpneg | category: experimental
- required:
  - model: MODEL
  - empty_conditioning: CONDITIONING
  - neg_scale: FLOAT default=1.0 min=0.0 max=100.0 step=0.01
- outputs: MODEL:MODEL

## PerpNegGuider
module: comfy_extras.nodes_perpneg | category: experimental
- required:
  - model: MODEL
  - positive: CONDITIONING
  - negative: CONDITIONING
  - empty_conditioning: CONDITIONING
  - cfg: FLOAT default=8.0 min=0.0 max=100.0 step=0.1
  - neg_scale: FLOAT default=1.0 min=0.0 max=100.0 step=0.01
- outputs: GUIDER:GUIDER

## PerturbedAttentionGuidance
module: comfy_extras.nodes_pag | category: model/patch/unet
- required:
  - model: MODEL
  - scale: FLOAT default=3.0 min=0.0 max=100.0 step=0.01
- outputs: MODEL:MODEL

## PhotoMakerEncode
module: comfy_extras.nodes_photomaker | category: model/conditioning/photomaker
- required:
  - photomaker: PHOTOMAKER
  - image: IMAGE
  - clip: CLIP
  - text: STRING default='photograph of photomaker'
- outputs: CONDITIONING:CONDITIONING

## PhotoMakerLoader
module: comfy_extras.nodes_photomaker | category: model/loaders
- required:
  - photomaker_model_name: COMBO[]
- outputs: PHOTOMAKER:PHOTOMAKER

## PiDColorBiasCorrection
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/experimental
- required:
  - model: MODEL
  - strength: FLOAT default=1.0 min=-20.0 max=20.0 step=0.01
  - backbone: COMBO[flux2] default='flux2'
- outputs: MODEL:MODEL

## PiDConditioning
module: comfy_extras.nodes_pid | category: model/conditioning
- required:
  - positive: CONDITIONING
  - latent: LATENT
  - latent_format: COMBO[flux, sd3, sdxl, qwenimage] default='flux'
  - degrade_sigma: FLOAT default=0.0 min=0.0 max=1.0 step=0.01
- outputs: CONDITIONING:CONDITIONING

## PiDiNetPreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Line Extractors
- required:
  - image: IMAGE
- optional:
  - safe: COMBO[enable, disable] default='enable'
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## Pipe from any [Crystools]
module: custom_nodes.ComfyUI-Crystools | category: crystools 🪛/Pipe
- required:
  - CPipeAny: CPipeAny
- outputs: CPipeAny:CPipeAny, any_1:*, any_2:*, any_3:*, any_4:*, any_5:*, any_6:*

## Pipe to/edit any [Crystools]
module: custom_nodes.ComfyUI-Crystools | category: crystools 🪛/Pipe
- optional:
  - CPipeAny: CPipeAny
  - any_1: *
  - any_2: *
  - any_3: *
  - any_4: *
  - any_5: *
  - any_6: *
- outputs: CPipeAny:CPipeAny

## Pixal3DConditioning
module: comfy_extras.nodes_trellis2 | category: model/conditioning/trellis
- required:
  - clip_vision_model: CLIP_VISION
  - image: IMAGE
  - camera_angle_x: FLOAT default=49.13 min=1.0 max=170.0 step=0.01
- outputs: positive:CONDITIONING, negative:CONDITIONING

## Pixal3DMultiViewConditioning
module: comfy_extras.nodes_trellis2 | category: model/conditioning/trellis
- required:
  - clip_vision_model: CLIP_VISION
  - fov: FLOAT default=20.0 min=1.0 max=170.0 step=0.01
- optional:
  - front: IMAGE
  - left: IMAGE
  - back: IMAGE
  - right: IMAGE
- outputs: positive:CONDITIONING, negative:CONDITIONING

## PixelOEPixelize+
module: custom_nodes.ComfyUI_essentials | category: essentials/image processing
- required:
  - image: IMAGE
  - downscale_mode: COMBO[contrast, bicubic, nearest, center, k-centroid]
  - target_size: INT default=128 min=0 max=16384 step=8
  - patch_size: INT default=16 min=4 max=32 step=2
  - thickness: INT default=2 min=1 max=16 step=1
  - color_matching: BOOLEAN default=True
  - upscale: BOOLEAN default=True
- outputs: IMAGE:IMAGE

## PixelPerfectResolution
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors
- required:
  - original_image: IMAGE
  - image_gen_width: INT default=512 min=64 max=8192 step=8
  - image_gen_height: INT default=512 min=64 max=8192 step=8
  - resize_mode: COMBO[Just Resize, Crop and Resize, Resize and Fill] default='Just Resize'
- outputs: RESOLUTION (INT):INT

## PixverseImageToVideoNode
module: comfy_api_nodes.nodes_pixverse | category: partner/video/PixVerse
- required:
  - image: IMAGE
  - prompt: STRING default=''
  - quality: COMBO[360p, 540p, 720p, 1080p] default='540p'
  - duration_seconds: COMBO[5, 8]
  - motion_mode: COMBO[normal, fast]
  - seed: INT default=0 min=0 max=2147483647
- optional:
  - negative_prompt: STRING default=''
  - pixverse_template: PIXVERSE_TEMPLATE
- outputs: VIDEO:VIDEO

## PixverseTemplateNode
module: comfy_api_nodes.nodes_pixverse | category: partner/video/PixVerse
- required:
  - template: COMBO[Microwave, Suit Swagger, Anything, Robot, Subject 3 Fever, kiss kiss]
- outputs: pixverse_template:PIXVERSE_TEMPLATE

## PixverseTextToVideoNode
module: comfy_api_nodes.nodes_pixverse | category: partner/video/PixVerse
- required:
  - prompt: STRING default=''
  - aspect_ratio: COMBO[16:9, 4:3, 1:1, 3:4, 9:16]
  - quality: COMBO[360p, 540p, 720p, 1080p] default='540p'
  - duration_seconds: COMBO[5, 8]
  - motion_mode: COMBO[normal, fast]
  - seed: INT default=0 min=0 max=2147483647
- optional:
  - negative_prompt: STRING default=''
  - pixverse_template: PIXVERSE_TEMPLATE
- outputs: VIDEO:VIDEO

## PixverseTransitionVideoNode
module: comfy_api_nodes.nodes_pixverse | category: partner/video/PixVerse
- required:
  - first_frame: IMAGE
  - last_frame: IMAGE
  - prompt: STRING default=''
  - quality: COMBO[360p, 540p, 720p, 1080p] default='540p'
  - duration_seconds: COMBO[5, 8]
  - motion_mode: COMBO[normal, fast]
  - seed: INT default=0 min=0 max=2147483647
- optional:
  - negative_prompt: STRING default=''
- outputs: VIDEO:VIDEO

## PixverseV6ExtendVideoNode
module: comfy_api_nodes.nodes_pixverse | category: partner/video/PixVerse
- required:
  - video: VIDEO
  - model: COMFY_DYNAMICCOMBO_V3
- outputs: VIDEO:VIDEO

## PixverseV6FirstLastFrameNode
module: comfy_api_nodes.nodes_pixverse | category: partner/video/PixVerse
- required:
  - first_frame: IMAGE
  - last_frame: IMAGE
  - model: COMFY_DYNAMICCOMBO_V3
- outputs: VIDEO:VIDEO

## PixverseV6FusionVideoNode
module: comfy_api_nodes.nodes_pixverse | category: partner/video/PixVerse
- required:
  - subjects: COMFY_AUTOGROW_V3
  - backgrounds: COMFY_AUTOGROW_V3
  - videos: COMFY_AUTOGROW_V3
  - model: COMFY_DYNAMICCOMBO_V3
- outputs: VIDEO:VIDEO

## PixverseV6ImageToVideoNode
module: comfy_api_nodes.nodes_pixverse | category: partner/video/PixVerse
- required:
  - image: IMAGE
  - model: COMFY_DYNAMICCOMBO_V3
- outputs: VIDEO:VIDEO

## PixverseV6TextToVideoNode
module: comfy_api_nodes.nodes_pixverse | category: partner/video/PixVerse
- required:
  - model: COMFY_DYNAMICCOMBO_V3
- outputs: VIDEO:VIDEO

## PlaySoundKJ
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/audio
- required:
  - audio_path: STRING default=''
  - mode: COMBO[always, on_empty_queue, on_change] default='always'
  - volume: FLOAT default=0.5 min=0.0 max=1.0 step=0.01
  - duration: FLOAT default=5.0 min=0.0 max=300.0 step=0.1
- optional:
  - any_input: *
  - audio: AUDIO
- outputs: any_output:*

## PlaySound|pysssss
module: custom_nodes.ComfyUI-Custom-Scripts | category: utils
- required:
  - any: *
  - mode: COMBO[always, on empty queue]
  - volume: FLOAT default=0.5 min=0 max=1 step=0.1
  - file: STRING default='notify.mp3'
- outputs: *:*

## PlotCoordinates
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/experimental
- required:
  - coordinates: STRING
  - text: STRING default='title'
  - width: INT default=512 min=8 max=4096 step=8
  - height: INT default=512 min=8 max=4096 step=8
  - bbox_width: INT default=128 min=8 max=4096 step=8
  - bbox_height: INT default=128 min=8 max=4096 step=8
- optional:
  - size_multiplier: FLOAT default=[1.0]
- outputs: images:IMAGE, width:INT, height:INT, bbox_width:INT, bbox_height:INT

## PlotParameters+
module: custom_nodes.ComfyUI_essentials | category: essentials/sampling
- required:
  - images: IMAGE
  - params: SAMPLER_PARAMS
  - order_by: COMBO[none, time, seed, steps, denoise, sampler, scheduler, guidance, max_shift, base_shift, ... +1]
  - cols_value: COMBO[none, time, seed, steps, denoise, sampler, scheduler, guidance, max_shift, base_shift, ... +1]
  - cols_num: INT default=-1 min=-1 max=1024
  - add_prompt: COMBO[false, true, excerpt]
  - add_params: COMBO[false, true, changes only] default='true'
- outputs: IMAGE:IMAGE

## PointsEditor
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/experimental
- required:
  - points_store: STRING
  - coordinates: STRING
  - neg_coordinates: STRING
  - bbox_store: STRING
  - bboxes: STRING
  - bbox_format: COMBO[xyxy, xywh]
  - width: INT default=512 min=8 max=4096 step=8
  - height: INT default=512 min=8 max=4096 step=8
  - normalize: BOOLEAN default=False
- optional:
  - bg_image: IMAGE
- outputs: positive_coords:STRING, negative_coords:STRING, bbox:BBOX, bbox_mask:MASK, cropped_image:IMAGE

## PolyexponentialScheduler
module: comfy_extras.nodes_custom_sampler | category: model/sampling/schedulers
- required:
  - steps: INT default=20 min=1 max=10000
  - sigma_max: FLOAT default=14.614642 min=0.0 max=5000.0 step=0.01
  - sigma_min: FLOAT default=0.0291675 min=0.0 max=5000.0 step=0.01
  - rho: FLOAT default=1.0 min=0.0 max=100.0 step=0.01
- outputs: SIGMAS:SIGMAS

## PorterDuffImageComposite
module: comfy_extras.nodes_compositing | category: image/compositing
- required:
  - source: IMAGE
  - source_alpha: MASK
  - destination: IMAGE
  - destination_alpha: MASK
  - mode: COMBO[ADD, CLEAR, DARKEN, DST, DST_ATOP, DST_IN, DST_OUT, DST_OVER, LIGHTEN, MULTIPLY, ... +8] default='DST'
- outputs: IMAGE:IMAGE, MASK:MASK

## Power Lora Loader (rgthree)
module: custom_nodes.rgthree-comfy | category: rgthree
- optional:
  - model: MODEL
  - clip: CLIP
- outputs: MODEL:MODEL, CLIP:CLIP

## Power Primitive (rgthree)
module: custom_nodes.rgthree-comfy | category: rgthree
- outputs: *:*

## Power Prompt (rgthree)
module: custom_nodes.rgthree-comfy | category: rgthree
- required:
  - prompt: STRING
- optional:
  - opt_model: MODEL
  - opt_clip: CLIP
  - insert_lora: COMBO[CHOOSE, DISABLE LORAS, FC_ACE_h3_face_v1, FC_ALAN_h3_face_v1, FC_ANYA_h3_face_v1, FC_ARIANA_h3_face_v1, FC_BETTY_h3_face_v1, FC_CHUCK_h3_face_v1, FC_DOLLY_h3_face_v1, FC_DUDE_h3_face_v1, ... +50]
  - insert_embedding: COMBO[CHOOSE]
  - insert_saved: COMBO[CHOOSE]
- outputs: CONDITIONING:CONDITIONING, MODEL:MODEL, CLIP:CLIP, TEXT:STRING

## Power Prompt - Simple (rgthree)
module: custom_nodes.rgthree-comfy | category: rgthree
- required:
  - prompt: STRING
- optional:
  - opt_clip: CLIP
  - insert_embedding: COMBO[CHOOSE]
  - insert_saved: COMBO[CHOOSE]
- outputs: CONDITIONING:CONDITIONING, TEXT:STRING

## Power Puter (rgthree)
module: custom_nodes.rgthree-comfy | category: rgthree
- outputs: *:*

## Preview from image [Crystools]
module: custom_nodes.ComfyUI-Crystools | category: crystools 🪛/Image
- optional:
  - image: IMAGE
- outputs: Metadata RAW:METADATA_RAW

## Preview from metadata [Crystools]
module: custom_nodes.ComfyUI-Crystools | category: crystools 🪛/Image
- optional:
  - metadata_raw: METADATA_RAW
- outputs: Metadata RAW:METADATA_RAW

## Preview3D
module: comfy_extras.nodes_load_3d | category: 3d
- required:
  - model_file: STRING,FILE_3D_GLB,FILE_3D_GLTF,FILE_3D_FBX,FILE_3D_OBJ,FILE_3D_STL,FILE_3D_USDZ,FILE_3D default=''
- optional:
  - camera_info: LOAD3D_CAMERA
  - bg_image: IMAGE
- outputs: 

## Preview3DAdvanced
module: comfy_extras.nodes_load_3d | category: 3d
- required:
  - model_3d: FILE_3D_GLB,FILE_3D_GLTF,FILE_3D_FBX,FILE_3D_OBJ,FILE_3D_STL,FILE_3D_USDZ,FILE_3D
  - viewport_state: LOAD_3D
  - width: INT default=1024 min=1 max=4096 step=1
  - height: INT default=1024 min=1 max=4096 step=1
- optional:
  - model_3d_info: LOAD3D_MODEL_INFO
  - camera_info: LOAD3D_CAMERA
- outputs: model_3d:FILE_3D, model_3d_info:LOAD3D_MODEL_INFO, camera_info:LOAD3D_CAMERA, width:INT, height:INT

## PreviewAnimation
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - fps: FLOAT default=8.0 min=0.01 max=1000.0 step=0.01
- optional:
  - images: IMAGE
  - masks: MASK
- outputs: 

## PreviewAny
module: comfy_extras.nodes_preview_any | category: utilities
- required:
  - source: *
- outputs: STRING:STRING

## PreviewAudio
module: comfy_extras.nodes_audio | category: audio
- required:
  - audio: AUDIO
- outputs: audio:AUDIO

## PreviewGaussianSplat
module: comfy_extras.nodes_load_3d | category: 3d
- required:
  - model_3d: FILE_3D_SPLAT_ANY,FILE_3D_PLY,FILE_3D_SPLAT,FILE_3D_SPZ,FILE_3D_KSPLAT
  - viewport_state: LOAD_3D
  - width: INT default=1024 min=1 max=4096 step=1
  - height: INT default=1024 min=1 max=4096 step=1
- optional:
  - model_3d_info: LOAD3D_MODEL_INFO
  - camera_info: LOAD3D_CAMERA
- outputs: model_3d:FILE_3D_SPLAT_ANY, model_3d_info:LOAD3D_MODEL_INFO, camera_info:LOAD3D_CAMERA, width:INT, height:INT

## PreviewImage
module: nodes | category: image
- required:
  - images: IMAGE
- outputs: images:IMAGE

## PreviewImageOrMask
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/misc
- required:
  - input: IMAGE,MASK
- outputs: 

## PreviewLatentNoiseMask
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/latents
- required:
  - latent: LATENT
- outputs: mask:MASK

## PreviewPointCloud
module: comfy_extras.nodes_load_3d | category: 3d
- required:
  - model_3d: FILE_3D_POINT_CLOUD_ANY,FILE_3D_PLY
  - viewport_state: LOAD_3D
  - width: INT default=1024 min=1 max=4096 step=1
  - height: INT default=1024 min=1 max=4096 step=1
- optional:
  - model_3d_info: LOAD3D_MODEL_INFO
  - camera_info: LOAD3D_CAMERA
- outputs: model_3d:FILE_3D_POINT_CLOUD_ANY, model_3d_info:LOAD3D_MODEL_INFO, camera_info:LOAD3D_CAMERA, width:INT, height:INT

## Primitive boolean [Crystools]
module: custom_nodes.ComfyUI-Crystools | category: crystools 🪛/Primitive
- required:
  - boolean: BOOLEAN default=True
- outputs: boolean:BOOLEAN

## Primitive float [Crystools]
module: custom_nodes.ComfyUI-Crystools | category: crystools 🪛/Primitive
- required:
  - float: FLOAT default=1 min=-1.7976931348623157e+308 max=1.7976931348623157e+308 step=0.01
- outputs: float:FLOAT

## Primitive integer [Crystools]
module: custom_nodes.ComfyUI-Crystools | category: crystools 🪛/Primitive
- required:
  - int: INT default=1 min=-9223372036854775807 max=9223372036854775807 step=1
- outputs: int:INT

## Primitive string [Crystools]
module: custom_nodes.ComfyUI-Crystools | category: crystools 🪛/Primitive
- required:
  - string: STRING default=''
- outputs: string:STRING

## Primitive string multiline [Crystools]
module: custom_nodes.ComfyUI-Crystools | category: crystools 🪛/Primitive
- required:
  - string: STRING default=''
- outputs: string:STRING

## PrimitiveBoolean
module: comfy_extras.nodes_primitive | category: utilities/primitive
- required:
  - value: BOOLEAN
- outputs: BOOLEAN:BOOLEAN

## PrimitiveBoundingBox
module: comfy_extras.nodes_images | category: utilities/primitive
- required:
  - x: INT default=0 min=0 max=16384
  - y: INT default=0 min=0 max=16384
  - width: INT default=512 min=1 max=16384
  - height: INT default=512 min=1 max=16384
- outputs: BOUNDING_BOX:BOUNDING_BOX

## PrimitiveFloat
module: comfy_extras.nodes_primitive | category: utilities/primitive
- required:
  - value: FLOAT min=-9223372036854775807 max=9223372036854775807 step=0.1
- outputs: FLOAT:FLOAT

## PrimitiveInt
module: comfy_extras.nodes_primitive | category: utilities/primitive
- required:
  - value: INT min=-9223372036854775807 max=9223372036854775807
- outputs: INT:INT

## PrimitiveString
module: comfy_extras.nodes_primitive | category: utilities/primitive
- required:
  - value: STRING
- outputs: STRING:STRING

## PrimitiveStringMultiline
module: comfy_extras.nodes_primitive | category: utilities/primitive
- required:
  - value: STRING
- outputs: STRING:STRING

## Prompts Everywhere
module: custom_nodes.cg-use-everywhere | category: everywhere/deprecated
- optional:
  - positive: *
  - negative: *
- outputs: 

## PrunaImageToVideoNode
module: comfy_api_nodes.nodes_pruna | category: partner/video/Pruna
- required:
  - model: COMFY_DYNAMICCOMBO_V3
- outputs: VIDEO:VIDEO

## PrunaTextToVideoNode
module: comfy_api_nodes.nodes_pruna | category: partner/video/Pruna
- required:
  - model: COMFY_DYNAMICCOMBO_V3
- outputs: VIDEO:VIDEO

## PuLIDEVACLIPLoader
module: custom_nodes.ComfyUI-PuLID-Flux2 | category: PuLID-Flux2
- outputs: EVA_CLIP:EVA_CLIP

## PuLIDFacePreview
module: custom_nodes.ComfyUI-PuLID-Flux2 | category: PuLID-Flux2
- required:
  - face_analysis: INSIGHTFACE
  - image: IMAGE
- optional:
  - show_confidence: BOOLEAN default=True
- outputs: IMAGE:IMAGE

## PulidFluxEvaClipLoader
module: custom_nodes.ComfyUI_PuLID_Flux_ll | category: pulid
- outputs: EVA_CLIP:EVA_CLIP

## PulidFluxFaceDetector
module: custom_nodes.ComfyUI_PuLID_Flux_ll | category: pulid
- required:
  - face_analysis: FACEANALYSIS
  - image: IMAGE
  - options: OPTIONS
- outputs: embed_face:IMAGE, align_face:IMAGE, face_bbox_image:IMAGE

## PulidFluxFaceNetLoader
module: custom_nodes.ComfyUI_PuLID_Flux_ll | category: pulid
- required:
  - provider: COMBO[CPU, CUDA]
- outputs: FACEANALYSIS:FACEANALYSIS

## PulidFluxInsightFaceLoader
module: custom_nodes.ComfyUI_PuLID_Flux_ll | category: pulid
- required:
  - provider: COMBO[CPU, CUDA, ROCM]
- outputs: FACEANALYSIS:FACEANALYSIS

## PulidFluxModelLoader
module: custom_nodes.ComfyUI_PuLID_Flux_ll | category: pulid
- required:
  - pulid_file: COMBO[pulid_flux2_klein_v2.safetensors]
- outputs: PULIDFLUX:PULIDFLUX

## PulidFluxOptions
module: custom_nodes.ComfyUI_PuLID_Flux_ll | category: pulid
- required:
  - input_faces_order: COMBO[left-right, right-left, top-bottom, bottom-top, small-large, large-small] default='large-small'
  - input_faces_index: INT default=0 min=0 max=1000 step=1
  - input_faces_align_mode: INT default=1 min=0 max=1 step=1
- outputs: OPTIONS:OPTIONS

## PuLIDInsightFaceLoader
module: custom_nodes.ComfyUI-PuLID-Flux2 | category: PuLID-Flux2
- required:
  - provider: COMBO[CPU, CUDA, ROCM]
- outputs: INSIGHTFACE:INSIGHTFACE

## PuLIDModelLoader
module: custom_nodes.ComfyUI-PuLID-Flux2 | category: PuLID-Flux2
- required:
  - pulid_file: COMBO[pulid_flux2_klein_v2.safetensors]
- outputs: PULID_MODEL:PULID_MODEL

## PyraCannyPreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Line Extractors
- required:
  - image: IMAGE
- optional:
  - low_threshold: INT default=64 min=0 max=255 step=1
  - high_threshold: INT default=128 min=0 max=255 step=1
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## QuadrupleCLIPLoader
module: comfy_extras.nodes_hidream | category: model/loaders
- required:
  - clip_name1: COMBO[clip_l.safetensors, qwen3vl_32b_minimax_h3_int4_convrot.safetensors, qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors, qwen_3_4b.safetensors, qwen_3_8b_fp8mixed.safetensors, umt5_xxl_fp8_e4m3fn_scaled.safetensors]
  - clip_name2: COMBO[clip_l.safetensors, qwen3vl_32b_minimax_h3_int4_convrot.safetensors, qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors, qwen_3_4b.safetensors, qwen_3_8b_fp8mixed.safetensors, umt5_xxl_fp8_e4m3fn_scaled.safetensors]
  - clip_name3: COMBO[clip_l.safetensors, qwen3vl_32b_minimax_h3_int4_convrot.safetensors, qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors, qwen_3_4b.safetensors, qwen_3_8b_fp8mixed.safetensors, umt5_xxl_fp8_e4m3fn_scaled.safetensors]
  - clip_name4: COMBO[clip_l.safetensors, qwen3vl_32b_minimax_h3_int4_convrot.safetensors, qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors, qwen_3_4b.safetensors, qwen_3_8b_fp8mixed.safetensors, umt5_xxl_fp8_e4m3fn_scaled.safetensors]
- outputs: CLIP:CLIP

## QuadrupleCLIPLoaderGGUF
module: custom_nodes.ComfyUI-GGUF | category: bootleg
- required:
  - clip_name1: COMBO[clip_l.safetensors, qwen3vl_32b_minimax_h3_int4_convrot.safetensors, qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors, qwen_3_4b.safetensors, qwen_3_8b_fp8mixed.safetensors, umt5_xxl_fp8_e4m3fn_scaled.safetensors]
  - clip_name2: COMBO[clip_l.safetensors, qwen3vl_32b_minimax_h3_int4_convrot.safetensors, qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors, qwen_3_4b.safetensors, qwen_3_8b_fp8mixed.safetensors, umt5_xxl_fp8_e4m3fn_scaled.safetensors]
  - clip_name3: COMBO[clip_l.safetensors, qwen3vl_32b_minimax_h3_int4_convrot.safetensors, qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors, qwen_3_4b.safetensors, qwen_3_8b_fp8mixed.safetensors, umt5_xxl_fp8_e4m3fn_scaled.safetensors]
  - clip_name4: COMBO[clip_l.safetensors, qwen3vl_32b_minimax_h3_int4_convrot.safetensors, qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors, qwen_3_4b.safetensors, qwen_3_8b_fp8mixed.safetensors, umt5_xxl_fp8_e4m3fn_scaled.safetensors]
- outputs: CLIP:CLIP

## QuiverImageToSVGNode
module: comfy_api_nodes.nodes_quiver | category: partner/image/Quiver
- required:
  - image: IMAGE
  - auto_crop: BOOLEAN default=False
  - model: COMFY_DYNAMICCOMBO_V3
  - seed: INT default=0 min=0 max=2147483647
- optional:
  - reasoning_effort: COMBO[low, medium, high, xhigh] default='high'
- outputs: SVG:SVG

## QuiverTextToSVGNode
module: comfy_api_nodes.nodes_quiver | category: partner/image/Quiver
- required:
  - prompt: STRING default=''
  - model: COMFY_DYNAMICCOMBO_V3
  - seed: INT default=0 min=0 max=2147483647
- optional:
  - instructions: STRING default=''
  - reference_images: COMFY_AUTOGROW_V3
  - reasoning_effort: COMBO[low, medium, high, xhigh] default='high'
- outputs: SVG:SVG

## QwenImage21Cache
module: comfy_extras.nodes_qwen | category: model/conditioning/qwen image
- required:
  - model: MODEL
  - device: COMBO[auto, gpu, cpu, off] default='auto'
  - dtype: COMBO[default, int8, int4] default='default'
- outputs: MODEL:MODEL

## QwenImageDiffsynthControlnet
module: comfy_extras.nodes_model_patch | category: model/patch/qwen
- required:
  - model: MODEL
  - model_patch: MODEL_PATCH
  - vae: VAE
  - image: IMAGE
  - strength: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
- optional:
  - mask: MASK
  - start_percent: FLOAT default=0.0 min=0.0 max=1.0 step=0.001
  - end_percent: FLOAT default=1.0 min=0.0 max=1.0 step=0.001
- outputs: MODEL:MODEL

## QwenImageEditApi
module: comfy_api_nodes.nodes_qwen | category: partner/image/Qwen
- required:
  - model: COMFY_DYNAMICCOMBO_V3
  - size: COMFY_DYNAMICCOMBO_V3
  - n: INT default=1 min=1 max=6
  - seed: INT default=42 min=0 max=2147483647 step=1
  - prompt_extend: BOOLEAN default=True
  - watermark: BOOLEAN default=False
- outputs: IMAGE:IMAGE

## QwenImageTextToImageApi
module: comfy_api_nodes.nodes_qwen | category: partner/image/Qwen
- required:
  - model: COMFY_DYNAMICCOMBO_V3
  - n: INT default=1 min=1 max=6
  - seed: INT default=42 min=0 max=2147483647 step=1
  - prompt_extend: BOOLEAN default=True
  - watermark: BOOLEAN default=False
- outputs: IMAGE:IMAGE

## RandomCropImages
module: comfy_extras.nodes_dataset | category: image/transform
- required:
  - images: IMAGE
  - width: INT default=512 min=1 max=8192
  - height: INT default=512 min=1 max=8192
  - seed: INT default=0 min=0 max=18446744073709551615
- outputs: images:IMAGE

## RandomImageFromBatch
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - input: COMFY_MATCHTYPE_V3
  - start_index: INT default=0 min=-4096 max=4096
  - end_index: INT default=-1 min=-4096 max=4096
  - num_frames: INT default=1 min=1 max=4096
  - randomness: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - min_distance: INT default=0 min=0 max=4096
  - max_distance: INT default=0 min=0 max=4096
  - seed: INT default=0 min=0 max=18446744073709551615 step=1
- outputs: output:COMFY_MATCHTYPE_V3

## RandomNoise
module: comfy_extras.nodes_custom_sampler | category: model/sampling/noise
- required:
  - noise_seed: INT default=0 min=0 max=18446744073709551615
- outputs: NOISE:NOISE

## Read JSON file [Crystools]
module: custom_nodes.ComfyUI-Crystools | category: crystools 🪛/Utils
- optional:
  - path_to_json: STRING default=''
- outputs: json:JSON

## ReadTextFile
module: custom_nodes.ControlFlowUtils | category: 🐺 VykosX-ControlFlowUtils
- required:
  - file: STRING default='file.txt'
- optional:
  - line: INT default=0
  - on_eof: BOOLEAN default=True
- outputs: STRING:STRING

## RebatchImages
module: comfy_extras.nodes_rebatch | category: image/batch
- required:
  - images: IMAGE
  - batch_size: INT default=1 min=1 max=4096
- outputs: IMAGE:IMAGE

## RebatchLatents
module: comfy_extras.nodes_rebatch | category: model/latent/batch
- required:
  - latents: LATENT
  - batch_size: INT default=1 min=1 max=4096
- outputs: LATENT:LATENT

## RecordAudio
module: comfy_extras.nodes_audio | category: audio
- required:
  - audio: AUDIO_RECORD
- outputs: AUDIO:AUDIO

## RecraftColorRGB
module: comfy_api_nodes.nodes_recraft | category: partner/image/Recraft
- required:
  - r: INT default=0 min=0 max=255
  - g: INT default=0 min=0 max=255
  - b: INT default=0 min=0 max=255
- optional:
  - recraft_color: RECRAFT_COLOR
- outputs: recraft_color:RECRAFT_COLOR

## RecraftControls
module: comfy_api_nodes.nodes_recraft | category: partner/image/Recraft
- optional:
  - colors: RECRAFT_COLOR
  - background_color: RECRAFT_COLOR
- outputs: recraft_controls:RECRAFT_CONTROLS

## RecraftCreateStyleNode
module: comfy_api_nodes.nodes_recraft | category: partner/image/Recraft
- required:
  - style: COMBO[realistic_image, digital_illustration]
  - images: COMFY_AUTOGROW_V3
- outputs: style_id:STRING

## RecraftCreativeUpscaleNode
module: comfy_api_nodes.nodes_recraft | category: partner/image/Recraft
- required:
  - image: IMAGE
- outputs: IMAGE:IMAGE

## RecraftCrispUpscaleNode
module: comfy_api_nodes.nodes_recraft | category: partner/image/Recraft
- required:
  - image: IMAGE
- outputs: IMAGE:IMAGE

## RecraftImageInpaintingNode
module: comfy_api_nodes.nodes_recraft | category: partner/image/Recraft
- required:
  - image: IMAGE
  - mask: MASK
  - prompt: STRING default=''
  - n: INT default=1 min=1 max=6
  - seed: INT default=0 min=0 max=18446744073709551615
- optional:
  - recraft_style: RECRAFT_V3_STYLE
  - negative_prompt: STRING default=''
- outputs: IMAGE:IMAGE

## RecraftImageToImageNode
module: comfy_api_nodes.nodes_recraft | category: partner/image/Recraft
- required:
  - image: IMAGE
  - prompt: STRING default=''
  - n: INT default=1 min=1 max=6
  - strength: FLOAT default=0.5 min=0.0 max=1.0 step=0.01
  - seed: INT default=0 min=0 max=18446744073709551615
- optional:
  - recraft_style: RECRAFT_V3_STYLE
  - negative_prompt: STRING default=''
  - recraft_controls: RECRAFT_CONTROLS
- outputs: IMAGE:IMAGE

## RecraftRemoveBackgroundNode
module: comfy_api_nodes.nodes_recraft | category: partner/image/Recraft
- required:
  - image: IMAGE
- outputs: IMAGE:IMAGE, MASK:MASK

## RecraftReplaceBackgroundNode
module: comfy_api_nodes.nodes_recraft | category: partner/image/Recraft
- required:
  - image: IMAGE
  - prompt: STRING default=''
  - n: INT default=1 min=1 max=6
  - seed: INT default=0 min=0 max=18446744073709551615
- optional:
  - recraft_style: RECRAFT_V3_STYLE
  - negative_prompt: STRING default=''
- outputs: IMAGE:IMAGE

## RecraftStyleV3DigitalIllustration
module: comfy_api_nodes.nodes_recraft | category: partner/image/Recraft
- required:
  - substyle: COMBO[None, 2d_art_poster, 2d_art_poster_2, antiquarian, bold_fantasy, child_book, child_books, cover, crosshatch, digital_engraving, ... +32]
- outputs: recraft_style:RECRAFT_V3_STYLE

## RecraftStyleV3InfiniteStyleLibrary
module: comfy_api_nodes.nodes_recraft | category: partner/image/Recraft
- required:
  - style_id: STRING default=''
- outputs: recraft_style:RECRAFT_V3_STYLE

## RecraftStyleV3LogoRaster
module: comfy_api_nodes.nodes_recraft | category: partner/image/Recraft
- required:
  - substyle: COMBO[emblem_graffiti, emblem_pop_art, emblem_punk, emblem_stamp, emblem_vintage]
- outputs: recraft_style:RECRAFT_V3_STYLE

## RecraftStyleV3RealisticImage
module: comfy_api_nodes.nodes_recraft | category: partner/image/Recraft
- required:
  - substyle: COMBO[None, b_and_w, enterprise, evening_light, faded_nostalgia, forest_life, hard_flash, hdr, motion_blur, mystic_naturalism, ... +10]
- outputs: recraft_style:RECRAFT_V3_STYLE

## RecraftTextToImageNode
module: comfy_api_nodes.nodes_recraft | category: partner/image/Recraft
- required:
  - prompt: STRING default=''
  - size: COMBO[1024x1024, 1365x1024, 1024x1365, 1536x1024, 1024x1536, 1820x1024, 1024x1820, 1024x2048, 2048x1024, 1434x1024, ... +5] default='1024x1024'
  - n: INT default=1 min=1 max=6
  - seed: INT default=0 min=0 max=18446744073709551615
- optional:
  - recraft_style: RECRAFT_V3_STYLE
  - negative_prompt: STRING default=''
  - recraft_controls: RECRAFT_CONTROLS
- outputs: IMAGE:IMAGE

## RecraftTextToVectorNode
module: comfy_api_nodes.nodes_recraft | category: partner/image/Recraft
- required:
  - prompt: STRING default=''
  - substyle: COMBO[None, bold_stroke, chemistry, colored_stencil, contour_pop_art, cosmics, cutout, depressive, editorial, emotional_flat, ... +15]
  - size: COMBO[1024x1024, 1365x1024, 1024x1365, 1536x1024, 1024x1536, 1820x1024, 1024x1820, 1024x2048, 2048x1024, 1434x1024, ... +5] default='1024x1024'
  - n: INT default=1 min=1 max=6
  - seed: INT default=0 min=0 max=18446744073709551615
- optional:
  - negative_prompt: STRING default=''
  - recraft_controls: RECRAFT_CONTROLS
- outputs: SVG:SVG

## RecraftV4CreateStyleNode
module: comfy_api_nodes.nodes_recraft | category: partner/image/Recraft
- required:
  - model: COMBO[recraftv4_styles, recraftv4_styles_vector, recraftv4_styles_pro, recraftv4_styles_pro_vector]
  - images: COMFY_AUTOGROW_V3
- outputs: style_id:STRING

## RecraftV4TextToImageNode
module: comfy_api_nodes.nodes_recraft | category: partner/image/Recraft
- required:
  - prompt: STRING
  - negative_prompt: STRING
  - model: COMFY_DYNAMICCOMBO_V3
  - n: INT default=1 min=1 max=6
  - seed: INT default=0 min=0 max=18446744073709551615
- optional:
  - recraft_controls: RECRAFT_CONTROLS
  - style_id: STRING default=''
  - style_match: COMBO[precise, flexible]
  - style_references: COMFY_AUTOGROW_V3
- outputs: IMAGE:IMAGE, style_id:STRING

## RecraftV4TextToVectorNode
module: comfy_api_nodes.nodes_recraft | category: partner/image/Recraft
- required:
  - prompt: STRING
  - negative_prompt: STRING
  - model: COMFY_DYNAMICCOMBO_V3
  - n: INT default=1 min=1 max=6
  - seed: INT default=0 min=0 max=18446744073709551615
- optional:
  - recraft_controls: RECRAFT_CONTROLS
  - style_id: STRING default=''
  - style_match: COMBO[precise, flexible]
  - style_references: COMFY_AUTOGROW_V3
- outputs: SVG:SVG, style_id:STRING

## RecraftVectorizeImageNode
module: comfy_api_nodes.nodes_recraft | category: partner/image/Recraft
- required:
  - image: IMAGE
- outputs: SVG:SVG

## ReferenceLatent
module: comfy_extras.nodes_edit_model | category: model/conditioning
- required:
  - conditioning: CONDITIONING
- optional:
  - latent: LATENT
- outputs: CONDITIONING:CONDITIONING

## ReferenceTimbreAudio
module: comfy_extras.nodes_ace | category: model/conditioning
- required:
  - conditioning: CONDITIONING
- optional:
  - latent: LATENT
- outputs: CONDITIONING:CONDITIONING

## RegexExtract
module: comfy_extras.nodes_string | category: text
- required:
  - string: STRING
  - regex_pattern: STRING
  - mode: COMBO[First Match, All Matches, First Group, All Groups]
  - case_insensitive: BOOLEAN default=True
  - multiline: BOOLEAN default=False
  - dotall: BOOLEAN default=False
  - group_index: INT default=1 min=0 max=100
- outputs: STRING:STRING

## RegexMatch
module: comfy_extras.nodes_string | category: text
- required:
  - string: STRING
  - regex_pattern: STRING
  - case_insensitive: BOOLEAN default=True
  - multiline: BOOLEAN default=False
  - dotall: BOOLEAN default=False
- outputs: matches:BOOLEAN

## RegexReplace
module: comfy_extras.nodes_string | category: text
- required:
  - string: STRING
  - regex_pattern: STRING
  - replace: STRING
- optional:
  - case_insensitive: BOOLEAN default=True
  - multiline: BOOLEAN default=False
  - dotall: BOOLEAN default=False
  - count: INT default=0 min=0 max=100
- outputs: STRING:STRING

## RemapImageRange
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - image: IMAGE
  - min: FLOAT default=0.0 min=-10.0 max=1.0 step=0.01
  - max: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - clamp: BOOLEAN default=True
- outputs: IMAGE:IMAGE

## RemapMaskRange
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking
- required:
  - mask: MASK
  - min: FLOAT default=0.0 min=-10.0 max=1.0 step=0.01
  - max: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
- outputs: mask:MASK

## RemBGSession+
module: custom_nodes.ComfyUI_essentials | category: essentials/image manipulation
- required:
  - model: COMBO[u2net: general purpose, u2netp: lightweight general purpose, u2net_human_seg: human segmentation, u2net_cloth_seg: cloths Parsing, silueta: very small u2net, isnet-general-use: general purpose, isnet-anime: anime illustrations, sam: general purpose]
  - providers: COMBO[CPU, CUDA, ROCM, DirectML, OpenVINO, CoreML, Tensorrt, Azure]
- outputs: REMBG_SESSION:REMBG_SESSION

## RemeshMesh
module: comfy_extras.nodes_mesh_postprocess | category: 3d/mesh
- required:
  - mesh: MESH
  - resolution: INT default=512 min=32 max=2048
  - sign_mode: COMFY_DYNAMICCOMBO_V3
  - band: FLOAT default=1.0 min=0.5 max=4.0 step=0.1
  - project_back: FLOAT default=0.0 min=0.0 max=1.0 step=0.05
  - fix_poles: BOOLEAN default=False
  - smooth_iters: INT default=0 min=0 max=20
  - drop_small_components: FLOAT default=0.01 min=0.0 max=0.5 step=0.005
  - precluster_max_verts: INT default=20000000 min=0 max=100000000
- outputs: mesh:MESH

## RemoveBackground
module: comfy_extras.nodes_bg_removal | category: image/background removal
- required:
  - bg_removal_model: BACKGROUND_REMOVAL
  - image: IMAGE
- outputs: mask:MASK

## RemoveLatentMask+
module: custom_nodes.ComfyUI_essentials | category: essentials/utilities
- required:
  - samples: LATENT
- outputs: LATENT:LATENT

## RenderAnimalKps
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Pose Keypoint Postprocess
- required:
  - kps: POSE_KEYPOINT
- outputs: IMAGE:IMAGE

## RenderMesh
module: comfy_extras.nodes_mesh_postprocess | category: 3d/mesh
- required:
  - mesh: MESH
  - mode: COMBO[auto, texture, vertex colors, solid, normal, depth]
  - width: INT default=1024 min=64 max=4096 step=8
  - height: INT default=1024 min=64 max=4096 step=8
  - background: COLOR default='#000000'
- optional:
  - model_3d_info: LOAD3D_MODEL_INFO
  - camera_info: LOAD3D_CAMERA
- outputs: image:IMAGE, mask:MASK

## RenderPeopleKps
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Pose Keypoint Postprocess
- required:
  - kps: POSE_KEYPOINT
  - render_body: BOOLEAN default=True
  - render_hand: BOOLEAN default=True
  - render_face: BOOLEAN default=True
- outputs: IMAGE:IMAGE

## RenderSplat
module: comfy_extras.nodes_gaussian_splat | category: 3d/splat
- required:
  - splat: SPLAT
  - width: INT default=1024 min=64 max=2048 step=8
  - height: INT default=1024 min=64 max=2048 step=8
  - frames: INT default=1 min=-240 max=240
  - splat_scale: FLOAT default=1.0 min=0.1 max=5.0 step=0.05
  - sharpen: FLOAT default=2.0 min=1.0 max=8.0 step=0.5
  - headlight_shading: FLOAT default=0.0 min=0.0 max=3.0 step=0.05
  - opacity_threshold: FLOAT default=0.0 min=0.0 max=1.0 step=0.01
  - render_style: COMBO[color, clay, depth, normal]
  - background: COLOR default='#000000'
- optional:
  - bg_image: IMAGE
  - camera_info: LOAD3D_CAMERA
- outputs: image:IMAGE, mask:MASK

## RenderUVAtlas
module: comfy_extras.nodes_mesh_postprocess | category: 3d/texturing
- required:
  - mesh: MESH
  - resolution: INT default=1024 min=64 max=4096 step=64
- outputs: image:IMAGE

## RenormCFG
module: comfy_extras.nodes_lumina2 | category: model/patch
- required:
  - model: MODEL
  - cfg_trunc: FLOAT default=100 min=0.0 max=100.0 step=0.01
  - renorm_cfg: FLOAT default=1.0 min=0.0 max=100.0 step=0.01
- outputs: MODEL:MODEL

## Repeater|pysssss
module: custom_nodes.ComfyUI-Custom-Scripts | category: utils
- required:
  - source: *
  - repeats: INT default=2 min=0 max=5000
  - output: COMBO[single, multi]
  - node_mode: COMBO[reuse, create]
- outputs: *:*

## RepeatImageBatch
module: comfy_extras.nodes_images | category: image/batch
- required:
  - image: IMAGE
  - amount: INT default=1 min=1 max=4096
- outputs: IMAGE:IMAGE

## RepeatLatentBatch
module: nodes | category: model/latent/batch
- required:
  - samples: LATENT
  - amount: INT default=1 min=1 max=64
- outputs: LATENT:LATENT

## ReplaceImagesInBatch
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - start_index: INT default=1 min=0 max=4096 step=1
- optional:
  - original_images: IMAGE
  - replacement_images: IMAGE
  - original_masks: MASK
  - replacement_masks: MASK
- outputs: IMAGE:IMAGE, MASK:MASK

## ReplaceText
module: comfy_extras.nodes_dataset | category: text
- required:
  - texts: STRING
  - find: STRING default=''
  - replace: STRING default=''
- outputs: texts:STRING

## ReplaceVideoLatentFrames
module: comfy_extras.nodes_latent | category: model/latent/batch
- required:
  - destination: LATENT
  - index: INT default=0 min=-16384 max=16384 step=1
- optional:
  - source: LATENT
- outputs: LATENT:LATENT

## ReroutePrimitive|pysssss
module: custom_nodes.ComfyUI-Custom-Scripts | category: __hidden__
- required:
  - value: *
- outputs: *:*

## RescaleCFG
module: comfy_extras.nodes_model_advanced | category: model/patch
- required:
  - model: MODEL
  - multiplier: FLOAT default=0.7 min=0.0 max=1.0 step=0.01
- outputs: MODEL:MODEL

## ResizeAndPadImage
module: comfy_extras.nodes_images | category: image/transform
- required:
  - image: IMAGE
  - target_width: INT default=512 min=1 max=16384 step=1
  - target_height: INT default=512 min=1 max=16384 step=1
  - padding_color: COMBO[white, black]
  - interpolation: COMBO[area, bicubic, nearest-exact, bilinear, lanczos]
- outputs: IMAGE:IMAGE

## ResizeImageMaskNode
module: comfy_extras.nodes_post_processing | category: image/transform
- required:
  - input: COMFY_MATCHTYPE_V3
  - resize_type: COMFY_DYNAMICCOMBO_V3
  - scale_method: COMBO[nearest-exact, bilinear, area, bicubic, lanczos] default='area'
- outputs: resized:COMFY_MATCHTYPE_V3

## ResizeImagesByLongerEdge
module: comfy_extras.nodes_dataset | category: image/transform
- required:
  - images: IMAGE
  - longer_edge: INT default=1024 min=1 max=8192
- outputs: images:IMAGE

## ResizeImagesByShorterEdge
module: comfy_extras.nodes_dataset | category: image/transform
- required:
  - images: IMAGE
  - shorter_edge: INT default=512 min=1 max=8192
- outputs: images:IMAGE

## ResizeMask
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking
- required:
  - mask: MASK
  - width: INT default=512 min=0 max=16384 step=1
  - height: INT default=512 min=0 max=16384 step=1
  - keep_proportions: BOOLEAN default=False
  - upscale_method: COMBO[nearest-exact, bilinear, area, bicubic, lanczos]
  - crop: COMBO[disabled, center]
- outputs: mask:MASK, width:INT, height:INT

## ResolutionBucket
module: comfy_extras.nodes_dataset | category: model/training
- required:
  - latents: LATENT
  - conditioning: CONDITIONING
- outputs: latents:LATENT, conditioning:CONDITIONING

## ResolutionSelector
module: comfy_extras.nodes_resolution | category: utilities
- required:
  - aspect_ratio: COMBO[1:1 (Square), 2:3 (Portrait Photo), 3:2 (Photo), 3:4 (Portrait Standard), 4:3 (Standard), 9:16 (Portrait Widescreen), 16:9 (Widescreen), 21:9 (Ultrawide)] default='1:1 (Square)'
  - megapixels: FLOAT default=1.0 min=0.1 max=16.0 step=0.1
  - multiple: INT default=8 min=8 max=128 step=4
- optional:
  - preview: RESOLUTION_PREVIEW
- outputs: width:INT, height:INT

## ReveImageCreateNode
module: comfy_api_nodes.nodes_reve | category: partner/image/Reve
- required:
  - prompt: STRING default=''
  - model: COMFY_DYNAMICCOMBO_V3
  - upscale: COMFY_DYNAMICCOMBO_V3
  - remove_background: BOOLEAN default=False
  - seed: INT default=0 min=0 max=2147483647
- outputs: IMAGE:IMAGE

## ReveImageEditNode
module: comfy_api_nodes.nodes_reve | category: partner/image/Reve
- required:
  - image: IMAGE
  - edit_instruction: STRING default=''
  - model: COMFY_DYNAMICCOMBO_V3
  - upscale: COMFY_DYNAMICCOMBO_V3
  - remove_background: BOOLEAN default=False
  - seed: INT default=0 min=0 max=2147483647
- outputs: IMAGE:IMAGE

## ReveImageRemixNode
module: comfy_api_nodes.nodes_reve | category: partner/image/Reve
- required:
  - reference_images: COMFY_AUTOGROW_V3
  - prompt: STRING default=''
  - model: COMFY_DYNAMICCOMBO_V3
  - upscale: COMFY_DYNAMICCOMBO_V3
  - remove_background: BOOLEAN default=False
  - seed: INT default=0 min=0 max=2147483647
- outputs: IMAGE:IMAGE

## ReverseImageBatch
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - images: IMAGE
- outputs: IMAGE:IMAGE

## RiftEngineScript
module: custom_nodes.ComfyUI-H3-Multishot | category: H3/script
- required:
  - script: STRING default=''
- optional:
  - ltx_shot_label: STRING default='Then, without moving the camera,'
- outputs: h3_script:STRING, ltx_prompt:STRING, shot_count:INT

## RiftPromptSource
module: custom_nodes.ComfyUI-H3-Multishot | category: H3/script
- required:
  - source_file: COMBO[(no prompt files found)]
- optional:
  - load_cap: INT default=0 min=0
  - start_index: INT default=0 min=0
  - character_override: STRING default=''
  - manual_path: STRING default=''
  - folder: COMBO[(all)] default='(all)'
  - walk_folder: BOOLEAN default=False
- outputs: story_idea:STRING, character:STRING, count:INT

## RiftScriptPicker
module: custom_nodes.ComfyUI-H3-Multishot | category: H3/script
- required:
  - script: COMBO[(no .json in input/joyecho_prompts)]
- outputs: prompts_json:STRING, path:STRING, speakers:STRING

## Rodin3D_Detail
module: comfy_api_nodes.nodes_rodin | category: partner/3d/Rodin
- required:
  - Images: IMAGE
- optional:
  - Seed: INT default=0 min=0 max=65535
  - Material_Type: COMBO[PBR, Shaded] default='PBR'
  - Polygon_count: COMBO[4K-Quad, 8K-Quad, 18K-Quad, 50K-Quad, 200K-Triangle] default='18K-Quad'
- outputs: 3D Model Path:STRING, GLB:FILE_3D_GLB

## Rodin3D_Gen2
module: comfy_api_nodes.nodes_rodin | category: partner/3d/Rodin
- required:
  - Images: IMAGE
  - TAPose: BOOLEAN default=False
- optional:
  - Seed: INT default=0 min=0 max=65535
  - Material_Type: COMBO[PBR, Shaded] default='PBR'
  - Polygon_count: COMBO[4K-Quad, 8K-Quad, 18K-Quad, 50K-Quad, 2K-Triangle, 20K-Triangle, 150K-Triangle, 500K-Triangle] default='500K-Triangle'
- outputs: 3D Model Path:STRING, GLB:FILE_3D_GLB

## Rodin3D_Gen25_Image
module: comfy_api_nodes.nodes_rodin | category: partner/3d/Rodin
- required:
  - images: COMFY_AUTOGROW_V3
  - mode: COMFY_DYNAMICCOMBO_V3
  - material: COMBO[PBR, Shaded, All, None] default='Shaded'
  - geometry_file_format: COMBO[glb, fbx, obj, stl] default='glb'
- optional:
  - texture_mode: COMBO[Default, legacy, extreme-low, low, medium, high] default='Default'
  - seed: INT default=0 min=0 max=65535
  - TAPose: BOOLEAN default=False
  - hd_texture: BOOLEAN default=False
  - texture_delight: BOOLEAN default=False
  - use_original_alpha: BOOLEAN default=False
  - addon_highpack: BOOLEAN default=False
  - bbox_width: INT default=0 min=0 max=300
  - bbox_height: INT default=0 min=0 max=300
  - bbox_length: INT default=0 min=0 max=300
  - height_cm: INT default=0 min=0 max=10000
- outputs: model_file:FILE_3D

## Rodin3D_Gen25_Text
module: comfy_api_nodes.nodes_rodin | category: partner/3d/Rodin
- required:
  - prompt: STRING default=''
  - mode: COMFY_DYNAMICCOMBO_V3
  - material: COMBO[PBR, Shaded, All, None] default='Shaded'
  - geometry_file_format: COMBO[glb, fbx, obj, stl] default='glb'
- optional:
  - texture_mode: COMBO[Default, legacy, extreme-low, low, medium, high] default='Default'
  - seed: INT default=0 min=0 max=65535
  - TAPose: BOOLEAN default=False
  - hd_texture: BOOLEAN default=False
  - texture_delight: BOOLEAN default=False
  - addon_highpack: BOOLEAN default=False
  - bbox_width: INT default=0 min=0 max=300
  - bbox_height: INT default=0 min=0 max=300
  - bbox_length: INT default=0 min=0 max=300
  - height_cm: INT default=0 min=0 max=10000
- outputs: model_file:FILE_3D

## Rodin3D_Regular
module: comfy_api_nodes.nodes_rodin | category: partner/3d/Rodin
- required:
  - Images: IMAGE
- optional:
  - Seed: INT default=0 min=0 max=65535
  - Material_Type: COMBO[PBR, Shaded] default='PBR'
  - Polygon_count: COMBO[4K-Quad, 8K-Quad, 18K-Quad, 50K-Quad, 200K-Triangle] default='18K-Quad'
- outputs: 3D Model Path:STRING, GLB:FILE_3D_GLB

## Rodin3D_Sketch
module: comfy_api_nodes.nodes_rodin | category: partner/3d/Rodin
- required:
  - Images: IMAGE
- optional:
  - Seed: INT default=0 min=0 max=65535
- outputs: 3D Model Path:STRING, GLB:FILE_3D_GLB

## Rodin3D_Smooth
module: comfy_api_nodes.nodes_rodin | category: partner/3d/Rodin
- required:
  - Images: IMAGE
- optional:
  - Seed: INT default=0 min=0 max=65535
  - Material_Type: COMBO[PBR, Shaded] default='PBR'
  - Polygon_count: COMBO[4K-Quad, 8K-Quad, 18K-Quad, 50K-Quad, 200K-Triangle] default='18K-Quad'
- outputs: 3D Model Path:STRING, GLB:FILE_3D_GLB

## RotateMesh
module: comfy_extras.nodes_save_3d | category: 3d/mesh
- required:
  - mesh: MESH
  - mode: COMFY_DYNAMICCOMBO_V3
- outputs: mesh:MESH

## RoundMask
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking
- required:
  - mask: MASK
- outputs: MASK:MASK

## RTDETR_detect
module: comfy_extras.nodes_rtdetr | category: image/detection
- required:
  - model: MODEL
  - image: IMAGE
  - threshold: FLOAT default=0.5
  - class_name: COMBO[all, person, bicycle, car, motorcycle, airplane, bus, train, truck, boat, ... +71] default='all'
  - max_detections: INT default=100
- outputs: bboxes:BOUNDING_BOX

## RTXVideoSuperResolution
module: custom_nodes.Nvidia_RTX_Nodes_ComfyUI | category: image/upscaling
- required:
  - images: IMAGE
  - resize_type: COMFY_DYNAMICCOMBO_V3
  - quality: COMBO[LOW, MEDIUM, HIGH, ULTRA] default='ULTRA'
- outputs: upscaled_images:IMAGE

## RunwayAleph2KeyframeNode
module: comfy_api_nodes.nodes_runway | category: partner/video/Runway
- required:
  - image: IMAGE
  - timing: COMFY_DYNAMICCOMBO_V3
- optional:
  - keyframes: RUNWAY_ALEPH2_KEYFRAME
- outputs: keyframes:RUNWAY_ALEPH2_KEYFRAME

## RunwayAleph2PromptImageNode
module: comfy_api_nodes.nodes_runway | category: partner/video/Runway
- required:
  - image: IMAGE
  - position: COMFY_DYNAMICCOMBO_V3
- optional:
  - prompt_images: RUNWAY_ALEPH2_PROMPT_IMAGE
- outputs: prompt_images:RUNWAY_ALEPH2_PROMPT_IMAGE

## RunwayAleph2VideoToVideoNode
module: comfy_api_nodes.nodes_runway | category: partner/video/Runway
- required:
  - prompt: STRING default=''
  - video: VIDEO
  - seed: INT default=0 min=0 max=4294967295 step=1
  - public_figure_threshold: COMBO[auto, low] default='low'
- optional:
  - keyframes: RUNWAY_ALEPH2_KEYFRAME
  - prompt_images: RUNWAY_ALEPH2_PROMPT_IMAGE
- outputs: VIDEO:VIDEO

## RunwayFirstLastFrameNode
module: comfy_api_nodes.nodes_runway | category: partner/video/Runway
- required:
  - prompt: STRING default=''
  - start_frame: IMAGE
  - end_frame: IMAGE
  - duration: COMBO[5, 10]
  - ratio: COMBO[768:1280, 1280:768]
  - seed: INT default=0 min=0 max=4294967295 step=1
- outputs: VIDEO:VIDEO

## RunwayImageToVideoNodeGen3a
module: comfy_api_nodes.nodes_runway | category: partner/video/Runway
- required:
  - prompt: STRING default=''
  - start_frame: IMAGE
  - duration: COMBO[5, 10]
  - ratio: COMBO[768:1280, 1280:768]
  - seed: INT default=0 min=0 max=4294967295 step=1
- outputs: VIDEO:VIDEO

## RunwayImageToVideoNodeGen4
module: comfy_api_nodes.nodes_runway | category: partner/video/Runway
- required:
  - prompt: STRING default=''
  - start_frame: IMAGE
  - duration: COMBO[5, 10]
  - ratio: COMBO[1280:720, 720:1280, 1104:832, 832:1104, 960:960, 1584:672]
  - seed: INT default=0 min=0 max=4294967295 step=1
- outputs: VIDEO:VIDEO

## RunwayTextToImageNode
module: comfy_api_nodes.nodes_runway | category: partner/image/Runway
- required:
  - prompt: STRING default=''
  - ratio: COMBO[1920:1080, 1080:1920, 1024:1024, 1360:768, 1080:1080, 1168:880, 1440:1080, 1080:1440, 1808:768, 2112:912]
- optional:
  - reference_image: IMAGE
- outputs: IMAGE:IMAGE

## SAM3_Detect
module: comfy_extras.nodes_sam3 | category: image/detection
- required:
  - model: MODEL
  - image: IMAGE
  - threshold: FLOAT default=0.5 min=0.0 max=1.0 step=0.01
  - refine_iterations: INT default=2 min=0 max=5
  - individual_masks: BOOLEAN default=False
- optional:
  - conditioning: CONDITIONING
  - bboxes: BOUNDING_BOX default={'x': 0, 'y': 0, 'width': 512, 'height': 512}
  - positive_coords: STRING
  - negative_coords: STRING
- outputs: masks:MASK, bboxes:BOUNDING_BOX

## SAM3_TrackPreview
module: comfy_extras.nodes_sam3 | category: image/detection
- required:
  - track_data: SAM3_TRACK_DATA
  - opacity: FLOAT default=0.5 min=0.0 max=1.0 step=0.05
  - fps: FLOAT default=24.0 min=1.0 max=120.0 step=1.0
- optional:
  - images: IMAGE
- outputs: 

## SAM3_TrackToMask
module: comfy_extras.nodes_sam3 | category: image/detection
- required:
  - track_data: SAM3_TRACK_DATA
  - object_indices: STRING default=''
- outputs: masks:MASK

## SAM3_VideoTrack
module: comfy_extras.nodes_sam3 | category: image/detection
- required:
  - images: IMAGE
  - model: MODEL
  - detection_threshold: FLOAT default=0.5 min=0.0 max=1.0 step=0.01
  - max_objects: INT default=4 min=0 max=64
  - detect_interval: INT default=1 min=1
- optional:
  - initial_mask: MASK
  - conditioning: CONDITIONING
- outputs: track_data:SAM3_TRACK_DATA

## SAM3DBody_FaceExpression
module: comfy_extras.nodes_sam3d_body | category: image/detection
- required:
  - sam3d_body_model: SAM3D_BODY_MODEL
  - mhr_pose_data: MHR_POSE_DATA
  - image: IMAGE
  - strength: FLOAT default=1.0 min=0.0 max=4.0 step=0.05
  - mouth_strength: FLOAT default=1.0 min=0.0 max=4.0 step=0.05
  - eye_strength: FLOAT default=2.0 min=0.0 max=4.0 step=0.05
  - brow_strength: FLOAT default=2.0 min=0.0 max=4.0 step=0.05
  - input_threshold: FLOAT default=0.02 min=0.0 max=0.5 step=0.01
  - blendshape_smooth_window: INT default=7 min=1 max=31 step=2
- outputs: mhr_pose_data:MHR_POSE_DATA

## SAM3DBody_Loader
module: comfy_extras.nodes_sam3d_body | category: image/detection
- required:
  - model_file: COMBO[]
- outputs: sam3d_body_model:SAM3D_BODY_MODEL

## SAM3DBody_Predict
module: comfy_extras.nodes_sam3d_body | category: image/detection
- required:
  - sam3d_body_model: SAM3D_BODY_MODEL
  - image: IMAGE
  - run_hand_refinement: BOOLEAN default=True
  - fov: FLOAT
  - batch_size: INT default=64 min=1 max=512 step=1
- optional:
  - track_data: SAM3_TRACK_DATA
  - bboxes: BOUNDING_BOX default={'x': 0, 'y': 0, 'width': 512, 'height': 512}
- outputs: mhr_pose_data:MHR_POSE_DATA

## SAM3DBody_Render
module: comfy_extras.nodes_sam3d_body | category: image/detection
- required:
  - pose_data: MHR_POSE_DATA,KIMODO_POSE_DATA
  - width: INT default=0 min=0 max=16384 step=8
  - height: INT default=0 min=0 max=16384 step=8
  - render_style: COMFY_DYNAMICCOMBO_V3
- optional:
  - background: IMAGE
  - camera_info: LOAD3D_CAMERA
- outputs: image:IMAGE

## SAM3DBody_Smooth
module: comfy_extras.nodes_sam3d_body | category: image/detection
- required:
  - mhr_pose_data: MHR_POSE_DATA
  - strength: FLOAT default=1.0 min=0.0 max=1.0 step=0.05
  - method: COMBO[gaussian, savgol] default='savgol'
  - window: INT default=7 min=1 max=51 step=2
  - rotation_threshold_degrees: FLOAT default=30.0 min=0.0 max=90.0 step=1.0
- outputs: mhr_pose_data:MHR_POSE_DATA

## SamplerARVideo
module: comfy_extras.nodes_ar_video | category: model/sampling/samplers
- required:
  - num_frame_per_block: INT default=1 min=1 max=64
- outputs: SAMPLER:SAMPLER

## SamplerCustom
module: comfy_extras.nodes_custom_sampler | category: model/sampling/custom
- required:
  - model: MODEL
  - add_noise: BOOLEAN default=True
  - noise_seed: INT default=0 min=0 max=18446744073709551615
  - cfg: FLOAT default=8.0 min=0.0 max=100.0 step=0.1
  - positive: CONDITIONING
  - negative: CONDITIONING
  - sampler: SAMPLER
  - sigmas: SIGMAS
  - latent_image: LATENT
- outputs: output:LATENT, denoised_output:LATENT

## SamplerCustomAdvanced
module: comfy_extras.nodes_custom_sampler | category: model/sampling/custom
- required:
  - noise: NOISE
  - guider: GUIDER
  - sampler: SAMPLER
  - sigmas: SIGMAS
  - latent_image: LATENT
- outputs: output:LATENT, denoised_output:LATENT

## SamplerDPMAdaptative
module: comfy_extras.nodes_custom_sampler | category: model/sampling/samplers
- required:
  - order: INT default=3 min=2 max=3
  - rtol: FLOAT default=0.05 min=0.0 max=100.0 step=0.01
  - atol: FLOAT default=0.0078 min=0.0 max=100.0 step=0.01
  - h_init: FLOAT default=0.05 min=0.0 max=100.0 step=0.01
  - pcoeff: FLOAT default=0.0 min=0.0 max=100.0 step=0.01
  - icoeff: FLOAT default=1.0 min=0.0 max=100.0 step=0.01
  - dcoeff: FLOAT default=0.0 min=0.0 max=100.0 step=0.01
  - accept_safety: FLOAT default=0.81 min=0.0 max=100.0 step=0.01
  - eta: FLOAT default=0.0 min=0.0 max=100.0 step=0.01
  - s_noise: FLOAT default=1.0 min=0.0 max=100.0 step=0.01
- outputs: SAMPLER:SAMPLER

## SamplerDPMPP_2M_SDE
module: comfy_extras.nodes_custom_sampler | category: model/sampling/samplers
- required:
  - solver_type: COMBO[midpoint, heun]
  - eta: FLOAT default=1.0 min=0.0 max=100.0 step=0.01
  - s_noise: FLOAT default=1.0 min=0.0 max=100.0 step=0.01
  - noise_device: COMBO[gpu, cpu]
- outputs: SAMPLER:SAMPLER

## SamplerDPMPP_2S_Ancestral
module: comfy_extras.nodes_custom_sampler | category: model/sampling/samplers
- required:
  - eta: FLOAT default=1.0 min=0.0 max=100.0 step=0.01
  - s_noise: FLOAT default=1.0 min=0.0 max=100.0 step=0.01
- outputs: SAMPLER:SAMPLER

## SamplerDPMPP_3M_SDE
module: comfy_extras.nodes_custom_sampler | category: model/sampling/samplers
- required:
  - eta: FLOAT default=1.0 min=0.0 max=100.0 step=0.01
  - s_noise: FLOAT default=1.0 min=0.0 max=100.0 step=0.01
  - noise_device: COMBO[gpu, cpu]
- outputs: SAMPLER:SAMPLER

## SamplerDPMPP_SDE
module: comfy_extras.nodes_custom_sampler | category: model/sampling/samplers
- required:
  - eta: FLOAT default=1.0 min=0.0 max=100.0 step=0.01
  - s_noise: FLOAT default=1.0 min=0.0 max=100.0 step=0.01
  - r: FLOAT default=0.5 min=0.0 max=100.0 step=0.01
  - noise_device: COMBO[gpu, cpu]
- outputs: SAMPLER:SAMPLER

## SamplerER_SDE
module: comfy_extras.nodes_custom_sampler | category: model/sampling/samplers
- required:
  - solver_type: COMBO[ER-SDE, Reverse-time SDE, ODE]
  - max_stage: INT default=3 min=1 max=3
  - eta: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - s_noise: FLOAT default=1.0 min=0.0 max=100.0 step=0.01
- outputs: SAMPLER:SAMPLER

## SamplerEulerAncestral
module: comfy_extras.nodes_custom_sampler | category: model/sampling/samplers
- required:
  - eta: FLOAT default=1.0 min=0.0 max=100.0 step=0.01
  - s_noise: FLOAT default=1.0 min=0.0 max=100.0 step=0.01
- outputs: SAMPLER:SAMPLER

## SamplerEulerAncestralCFGPP
module: comfy_extras.nodes_custom_sampler | category: model/sampling/samplers
- required:
  - eta: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - s_noise: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
- outputs: SAMPLER:SAMPLER

## SamplerEulerCFGpp
module: comfy_extras.nodes_advanced_samplers | category: experimental
- required:
  - version: COMBO[regular, alternative]
- outputs: SAMPLER:SAMPLER

## SamplerLCM
module: comfy_extras.nodes_advanced_samplers | category: model/sampling/samplers
- required:
  - s_noise: FLOAT default=1.0 min=0.0 max=64.0 step=0.01
  - s_noise_end: FLOAT default=1.0 min=0.0 max=64.0 step=0.01
  - noise_clip_std: FLOAT default=0.0 min=0.0 max=10.0 step=0.01
- outputs: SAMPLER:SAMPLER

## SamplerLCMUpscale
module: comfy_extras.nodes_advanced_samplers | category: model/sampling/samplers
- required:
  - scale_ratio: FLOAT default=1.0 min=0.1 max=20.0 step=0.01
  - scale_steps: INT default=-1 min=-1 max=1000 step=1
  - upscale_method: COMBO[bislerp, nearest-exact, bilinear, area, bicubic]
- outputs: SAMPLER:SAMPLER

## SamplerLMS
module: comfy_extras.nodes_custom_sampler | category: model/sampling/samplers
- required:
  - order: INT default=4 min=1 max=100
- outputs: SAMPLER:SAMPLER

## SamplerSASolver
module: comfy_extras.nodes_custom_sampler | category: model/sampling/samplers
- required:
  - model: MODEL
  - eta: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - sde_start_percent: FLOAT default=0.2 min=0.0 max=1.0 step=0.001
  - sde_end_percent: FLOAT default=0.8 min=0.0 max=1.0 step=0.001
  - s_noise: FLOAT default=1.0 min=0.0 max=100.0 step=0.01
  - predictor_order: INT default=3 min=1 max=6
  - corrector_order: INT default=4 min=0 max=6
  - use_pece: BOOLEAN
  - simple_order_2: BOOLEAN
- outputs: SAMPLER:SAMPLER

## SamplerSEEDS2
module: comfy_extras.nodes_custom_sampler | category: model/sampling/samplers
- required:
  - solver_type: COMBO[phi_1, phi_2]
  - eta: FLOAT default=1.0 min=0.0 max=100.0 step=0.01
  - s_noise: FLOAT default=1.0 min=0.0 max=100.0 step=0.01
  - r: FLOAT default=0.5 min=0.01 max=1.0 step=0.01
- outputs: SAMPLER:SAMPLER

## SamplerSelectHelper+
module: custom_nodes.ComfyUI_essentials | category: essentials/sampling
- required:
  - euler: BOOLEAN default=False
  - euler_cfg_pp: BOOLEAN default=False
  - euler_ancestral: BOOLEAN default=False
  - euler_ancestral_cfg_pp: BOOLEAN default=False
  - heun: BOOLEAN default=False
  - heunpp2: BOOLEAN default=False
  - exp_heun_2_x0: BOOLEAN default=False
  - exp_heun_2_x0_sde: BOOLEAN default=False
  - dpm_2: BOOLEAN default=False
  - dpm_2_ancestral: BOOLEAN default=False
  - lms: BOOLEAN default=False
  - dpm_fast: BOOLEAN default=False
  - dpm_adaptive: BOOLEAN default=False
  - dpmpp_2s_ancestral: BOOLEAN default=False
  - dpmpp_2s_ancestral_cfg_pp: BOOLEAN default=False
  - dpmpp_sde: BOOLEAN default=False
  - dpmpp_sde_gpu: BOOLEAN default=False
  - dpmpp_2m: BOOLEAN default=False
  - dpmpp_2m_cfg_pp: BOOLEAN default=False
  - dpmpp_2m_sde: BOOLEAN default=False
  - dpmpp_2m_sde_gpu: BOOLEAN default=False
  - dpmpp_2m_sde_heun: BOOLEAN default=False
  - dpmpp_2m_sde_heun_gpu: BOOLEAN default=False
  - dpmpp_3m_sde: BOOLEAN default=False
  - dpmpp_3m_sde_gpu: BOOLEAN default=False
  - ddpm: BOOLEAN default=False
  - lcm: BOOLEAN default=False
  - ipndm: BOOLEAN default=False
  - ipndm_v: BOOLEAN default=False
  - deis: BOOLEAN default=False
  - cfgpp_ud10_ab: BOOLEAN default=False
  - res_multistep: BOOLEAN default=False
  - res_multistep_cfg_pp: BOOLEAN default=False
  - res_multistep_ancestral: BOOLEAN default=False
  - res_multistep_ancestral_cfg_pp: BOOLEAN default=False
  - gradient_estimation: BOOLEAN default=False
  - gradient_estimation_cfg_pp: BOOLEAN default=False
  - er_sde: BOOLEAN default=False
  - seeds_2: BOOLEAN default=False
  - seeds_3: BOOLEAN default=False
  - sa_solver: BOOLEAN default=False
  - sa_solver_pece: BOOLEAN default=False
  - ddim: BOOLEAN default=False
  - uni_pc: BOOLEAN default=False
  - uni_pc_bh2: BOOLEAN default=False
- outputs: STRING:STRING

## SamplerSelfRefineVideo
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/samplers
- required:
  - input_mode: COMFY_DYNAMICCOMBO_V3
  - certain_percentage: FLOAT default=0.999 min=0.0 max=1.0 step=0.001
  - uncertainty_threshold: FLOAT default=0.2 min=0.0 max=1.0 step=0.01
  - verbose: BOOLEAN default=False
  - seed: INT default=0 min=0 max=18446744073709551615 step=1
- optional:
  - latent: LATENT
- outputs: SAMPLER:SAMPLER

## SamplingPercentToSigma
module: comfy_extras.nodes_custom_sampler | category: model/sampling/sigmas
- required:
  - model: MODEL
  - sampling_percent: FLOAT default=0.0 min=0.0 max=1.0 step=0.0001
  - return_actual_sigma: BOOLEAN default=False
- outputs: sigma_value:FLOAT

## SAMPreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/others
- required:
  - image: IMAGE
- optional:
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## Save image with extra metadata [Crystools]
module: custom_nodes.ComfyUI-Crystools | category: crystools 🪛/Image
- required:
  - image: IMAGE
  - filename_prefix: STRING default='ComfyUI'
  - with_workflow: BOOLEAN default=True
- optional:
  - metadata_extra: STRING default='{\n  "Title": "Image generated by Crystian",\n  "Description":...'
- outputs: Metadata RAW:METADATA_RAW

## Save3DAdvanced
module: comfy_extras.nodes_save_3d | category: 3d
- required:
  - model_3d: FILE_3D_GLB,FILE_3D_GLTF,FILE_3D_FBX,FILE_3D_OBJ,FILE_3D_STL,FILE_3D_USDZ,FILE_3D
  - filename_prefix: STRING default='3d/ComfyUI'
  - viewport_state: LOAD_3D
  - width: INT default=1024 min=1 max=4096 step=1
  - height: INT default=1024 min=1 max=4096 step=1
- optional:
  - model_3d_info: LOAD3D_MODEL_INFO
  - camera_info: LOAD3D_CAMERA
- outputs: model_3d:FILE_3D, model_3d_info:LOAD3D_MODEL_INFO, camera_info:LOAD3D_CAMERA, width:INT, height:INT

## SaveAnimatedPNG
module: comfy_extras.nodes_images | category: image
- required:
  - images: IMAGE
  - filename_prefix: STRING default='ComfyUI'
  - fps: FLOAT default=6.0 min=0.01 max=1000.0 step=0.01
  - compress_level: INT default=4 min=0 max=9
- outputs: images:IMAGE

## SaveAnimatedWEBP
module: comfy_extras.nodes_images | category: image
- required:
  - images: IMAGE
  - filename_prefix: STRING default='ComfyUI'
  - fps: FLOAT default=6.0 min=0.01 max=1000.0 step=0.01
  - lossless: BOOLEAN default=True
  - quality: INT default=80 min=0 max=100
  - method: COMBO[default, fastest, slowest]
- outputs: images:IMAGE

## SaveAudio
module: comfy_extras.nodes_audio | category: audio
- required:
  - audio: AUDIO
  - filename_prefix: STRING default='audio/ComfyUI'
- outputs: audio:AUDIO

## SaveAudioAdvanced
module: comfy_extras.nodes_audio | category: audio
- required:
  - audio: AUDIO
  - filename_prefix: STRING default='audio/ComfyUI'
  - format: COMFY_DYNAMICCOMBO_V3
- outputs: audio:AUDIO

## SaveAudioMP3
module: comfy_extras.nodes_audio | category: audio
- required:
  - audio: AUDIO
  - filename_prefix: STRING default='audio/ComfyUI'
  - quality: COMBO[V0, 128k, 320k] default='V0'
- outputs: audio:AUDIO

## SaveAudioOpus
module: comfy_extras.nodes_audio | category: audio
- required:
  - audio: AUDIO
  - filename_prefix: STRING default='audio/ComfyUI'
  - quality: COMBO[64k, 96k, 128k, 192k, 320k] default='128k'
- outputs: audio:AUDIO

## SaveConditioning
module: comfy_extras.nodes_cond | category: model/conditioning
- required:
  - conditioning: CONDITIONING
  - filename_prefix: STRING default='conditioning/ComfyUI'
- outputs: conditioning:CONDITIONING

## SaveGaussianSplat
module: comfy_extras.nodes_save_3d | category: 3d
- required:
  - model_3d: FILE_3D_SPLAT_ANY,FILE_3D_PLY,FILE_3D_SPLAT,FILE_3D_SPZ,FILE_3D_KSPLAT
  - filename_prefix: STRING default='3d/ComfyUI'
  - viewport_state: LOAD_3D
  - width: INT default=1024 min=1 max=4096 step=1
  - height: INT default=1024 min=1 max=4096 step=1
- optional:
  - model_3d_info: LOAD3D_MODEL_INFO
  - camera_info: LOAD3D_CAMERA
- outputs: model_3d:FILE_3D_SPLAT_ANY, model_3d_info:LOAD3D_MODEL_INFO, camera_info:LOAD3D_CAMERA, width:INT, height:INT

## SaveGLB
module: comfy_extras.nodes_save_3d | category: 3d
- required:
  - mesh: MESH,FILE_3D_GLB,FILE_3D_GLTF,FILE_3D_OBJ,FILE_3D_FBX,FILE_3D_STL,FILE_3D_USDZ,FILE_3D_PLY,FILE_3D_SPLAT,FILE_3D_SPZ,FILE_3D_KSPLAT,FILE_3D_SPLAT_ANY,FILE_3D_POINT_CLOUD_ANY,FILE_3D
  - filename_prefix: STRING default='3d/ComfyUI'
- outputs: 

## SaveImage
module: nodes | category: image
- required:
  - images: IMAGE
  - filename_prefix: STRING default='ComfyUI'
- outputs: images:IMAGE

## SaveImageAdvanced
module: comfy_extras.nodes_images | category: image
- required:
  - images: IMAGE
  - filename_prefix: STRING default='ComfyUI'
  - format: COMFY_DYNAMICCOMBO_V3
- outputs: images:IMAGE

## SaveImageDataSetToFolder
module: comfy_extras.nodes_dataset | category: image
- required:
  - images: IMAGE
  - folder_name: STRING default='dataset'
  - filename_prefix: STRING default='image'
  - mode: COMBO[overwrite, increment] default='overwrite'
- outputs: 

## SaveImageKJ
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - images: IMAGE
  - filename_prefix: STRING default='ComfyUI'
  - output_folder: STRING default='output'
- optional:
  - caption_file_extension: STRING default='.txt'
  - caption: STRING
- outputs: filename:STRING

## SaveImageTextDataSetToFolder
module: comfy_extras.nodes_dataset | category: image
- required:
  - images: IMAGE
  - folder_name: STRING default='dataset'
  - filename_prefix: STRING default='image'
  - mode: COMBO[overwrite, increment] default='overwrite'
- optional:
  - texts: STRING
- outputs: 

## SaveImageWebsocket
module: custom_nodes.websocket_image_save | category: image
- required:
  - images: IMAGE
- outputs: 

## SaveImageWithAlpha
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - images: IMAGE
  - mask: MASK
  - filename_prefix: STRING default='ComfyUI'
- outputs: 

## SaveLatent
module: nodes | category: model/latent
- required:
  - samples: LATENT
  - filename_prefix: STRING default='latents/ComfyUI'
- outputs: samples:LATENT

## SaveLoRA
module: comfy_extras.nodes_train | category: model/merging
- required:
  - lora: LORA_MODEL
  - prefix: STRING default='loras/ComfyUI_trained_lora'
- optional:
  - steps: INT
- outputs: 

## SavePointCloud
module: comfy_extras.nodes_save_3d | category: 3d
- required:
  - model_3d: FILE_3D_POINT_CLOUD_ANY,FILE_3D_PLY
  - filename_prefix: STRING default='3d/ComfyUI'
  - viewport_state: LOAD_3D
  - width: INT default=1024 min=1 max=4096 step=1
  - height: INT default=1024 min=1 max=4096 step=1
- optional:
  - model_3d_info: LOAD3D_MODEL_INFO
  - camera_info: LOAD3D_CAMERA
- outputs: model_3d:FILE_3D_POINT_CLOUD_ANY, model_3d_info:LOAD3D_MODEL_INFO, camera_info:LOAD3D_CAMERA, width:INT, height:INT

## SavePoseKpsAsJsonFile
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Pose Keypoint Postprocess
- required:
  - pose_kps: POSE_KEYPOINT
  - filename_prefix: STRING default='PoseKeypoint'
- outputs: 

## SaveStringKJ
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/misc
- required:
  - string: STRING
  - filename_prefix: STRING default='text'
  - output_folder: STRING default='output'
- optional:
  - file_extension: STRING default='.txt'
- outputs: filename:STRING

## SaveSVGNode
module: comfy_extras.nodes_images | category: image
- required:
  - svg: SVG
  - filename_prefix: STRING default='svg/ComfyUI'
- outputs: svg:SVG

## SaveText
module: comfy_extras.nodes_text | category: text
- required:
  - text: STRING
  - filename_prefix: STRING default='ComfyUI'
  - format: COMBO[txt, csv, md, json] default='txt'
- outputs: text:STRING

## SaveTextFile
module: custom_nodes.ControlFlowUtils | category: 🐺 VykosX-ControlFlowUtils
- required:
  - file_path: STRING default='out.txt'
  - mode: COMBO[append, overwrite, new only]
  - terminator: BOOLEAN default=True
  - text: STRING
- outputs: SUCCESS?:BOOLEAN

## SaveText|pysssss
module: custom_nodes.ComfyUI-Custom-Scripts | category: utils
- required:
  - root_dir: COMBO[input, output, temp]
  - file: STRING default='file.txt'
  - append: COMBO[append, overwrite, new only]
  - insert: BOOLEAN default=True
  - text: STRING
- outputs: STRING:STRING

## SaveTrainingDataset
module: comfy_extras.nodes_dataset | category: model/training
- required:
  - latents: LATENT
  - conditioning: CONDITIONING
  - folder_name: STRING default='training_dataset'
  - shard_size: INT default=1000 min=1 max=100000
- outputs: 

## SaveVideo
module: comfy_extras.nodes_video | category: video
- required:
  - video: VIDEO
  - filename_prefix: STRING default='video/ComfyUI'
  - format: COMFY_DYNAMICCOMBO_V3
- optional:
  - codec: COMFY_DYNAMICCOMBO_V3
- outputs: video:VIDEO

## SaveWEBM
module: comfy_extras.nodes_video | category: video
- required:
  - images: IMAGE
  - filename_prefix: STRING default='ComfyUI'
  - codec: COMBO[vp9, av1]
  - fps: FLOAT default=24.0 min=0.01 max=1000.0 step=0.01
  - crf: FLOAT default=32.0 min=0 max=63.0 step=1
- outputs: images:IMAGE

## SCAIL2ColoredMask
module: comfy_extras.nodes_scail | category: model/conditioning/wan/scail
- required:
  - driving_track_data: SAM3_TRACK_DATA
  - object_indices: STRING default=''
  - sort_by: COMBO[none, left_to_right, area] default='left_to_right'
  - replacement_mode: BOOLEAN default=False
- optional:
  - ref_track_data: SAM3_TRACK_DATA,MASK
- outputs: pose_video_mask:IMAGE, reference_image_mask:IMAGE

## ScaleBatchPromptSchedule
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/misc
- required:
  - input_str: STRING default='0:(0.0),\n7:(1.0),\n15:(0.0)\n'
  - old_frame_count: INT default=1 min=1 max=4096 step=1
  - new_frame_count: INT default=1 min=1 max=4096 step=1
- outputs: STRING:STRING

## ScaleROPE
module: comfy_extras.nodes_rope | category: model/patch
- required:
  - model: MODEL
  - scale_x: FLOAT default=1.0 min=0.0 max=100.0 step=0.1
  - shift_x: FLOAT default=0.0 min=-256.0 max=256.0 step=0.1
  - scale_y: FLOAT default=1.0 min=0.0 max=100.0 step=0.1
  - shift_y: FLOAT default=0.0 min=-256.0 max=256.0 step=0.1
  - scale_t: FLOAT default=1.0 min=0.0 max=100.0 step=0.1
  - shift_t: FLOAT default=0.0 min=-256.0 max=256.0 step=0.1
- outputs: MODEL:MODEL

## ScheduledCFGGuidance
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/experimental
- required:
  - model: MODEL
  - positive: CONDITIONING
  - negative: CONDITIONING
  - cfg: FLOAT default=6.0 min=0.0 max=100.0 step=0.01
  - start_percent: FLOAT default=0.0 min=0.0 max=1.0 step=0.01
  - end_percent: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: GUIDER:GUIDER

## SchedulerSelectHelper+
module: custom_nodes.ComfyUI_essentials | category: essentials/sampling
- required:
  - simple: BOOLEAN default=False
  - sgm_uniform: BOOLEAN default=False
  - karras: BOOLEAN default=False
  - exponential: BOOLEAN default=False
  - ddim_uniform: BOOLEAN default=False
  - beta: BOOLEAN default=False
  - normal: BOOLEAN default=False
  - linear_quadratic: BOOLEAN default=False
  - kl_optimal: BOOLEAN default=False
- outputs: STRING:STRING

## Screencap_mss
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - x: INT default=0 min=0 max=10000 step=1
  - y: INT default=0 min=0 max=10000 step=1
  - width: INT default=512 min=0 max=10000 step=1
  - height: INT default=512 min=0 max=10000 step=1
  - num_frames: INT default=1 min=1 max=255 step=1
  - delay: FLOAT default=0.1 min=0.0 max=10.0 step=0.01
- outputs: image:IMAGE

## ScreencapStream
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - frame_data: STRING default=''
  - crop_width: INT default=1 min=1 max=16384 step=1
  - crop_height: INT default=1 min=1 max=16384 step=1
- outputs: image:IMAGE

## Scribble_PiDiNet_Preprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Line Extractors
- required:
  - image: IMAGE
- optional:
  - safe: COMBO[enable, disable]
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## Scribble_XDoG_Preprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Line Extractors
- required:
  - image: IMAGE
- optional:
  - threshold: INT default=32 min=1 max=64 step=1
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## ScribblePreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Line Extractors
- required:
  - image: IMAGE
- optional:
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## SD3AttentionSeekerLG+
module: custom_nodes.ComfyUI_essentials | category: essentials/conditioning
- required:
  - clip: CLIP
  - apply_to_query: BOOLEAN default=True
  - apply_to_key: BOOLEAN default=True
  - apply_to_value: BOOLEAN default=True
  - apply_to_out: BOOLEAN default=True
  - clip_l_0: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_l_1: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_l_2: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_l_3: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_l_4: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_l_5: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_l_6: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_l_7: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_l_8: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_l_9: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_l_10: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_l_11: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_g_0: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_g_1: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_g_2: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_g_3: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_g_4: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_g_5: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_g_6: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_g_7: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_g_8: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_g_9: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_g_10: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_g_11: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_g_12: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_g_13: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_g_14: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_g_15: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_g_16: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_g_17: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_g_18: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_g_19: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_g_20: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_g_21: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_g_22: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_g_23: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_g_24: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_g_25: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_g_26: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_g_27: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_g_28: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_g_29: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_g_30: FLOAT default=1.0 min=0 max=5 step=0.05
  - clip_g_31: FLOAT default=1.0 min=0 max=5 step=0.05
- outputs: CLIP:CLIP

## SD3AttentionSeekerT5+
module: custom_nodes.ComfyUI_essentials | category: essentials/conditioning
- required:
  - clip: CLIP
  - apply_to_query: BOOLEAN default=True
  - apply_to_key: BOOLEAN default=True
  - apply_to_value: BOOLEAN default=True
  - apply_to_out: BOOLEAN default=True
  - t5xxl_0: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_1: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_2: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_3: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_4: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_5: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_6: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_7: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_8: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_9: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_10: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_11: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_12: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_13: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_14: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_15: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_16: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_17: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_18: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_19: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_20: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_21: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_22: FLOAT default=1.0 min=0 max=5 step=0.05
  - t5xxl_23: FLOAT default=1.0 min=0 max=5 step=0.05
- outputs: CLIP:CLIP

## SD3NegativeConditioning+
module: custom_nodes.ComfyUI_essentials | category: essentials/conditioning
- required:
  - conditioning: CONDITIONING
  - end: FLOAT default=0.1 min=0.0 max=1.0 step=0.001
- outputs: CONDITIONING:CONDITIONING

## SD_4XUpscale_Conditioning
module: comfy_extras.nodes_sdupscale | category: model/conditioning/stable diffusion upscaler
- required:
  - images: IMAGE
  - positive: CONDITIONING
  - negative: CONDITIONING
  - scale_ratio: FLOAT default=4.0 min=0.0 max=10.0 step=0.01
  - noise_augmentation: FLOAT default=0.0 min=0.0 max=1.0 step=0.001
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## SDPoseDrawKeypoints
module: comfy_extras.nodes_sdpose | category: image/detection
- required:
  - keypoints: POSE_KEYPOINT
  - draw_body: BOOLEAN default=True
  - draw_hands: BOOLEAN default=True
  - draw_face: BOOLEAN default=True
  - draw_feet: BOOLEAN default=False
  - stick_width: INT default=4 min=1 max=10 step=1
  - face_point_size: INT default=3 min=1 max=10 step=1
  - score_threshold: FLOAT default=0.3 min=0.0 max=1.0 step=0.01
  - draw_head: BOOLEAN default=True
- outputs: IMAGE:IMAGE

## SDPoseFaceBBoxes
module: comfy_extras.nodes_sdpose | category: image/detection
- required:
  - keypoints: POSE_KEYPOINT
  - scale: FLOAT default=1.5 min=1.0 max=10.0 step=0.1
  - force_square: BOOLEAN default=True
- outputs: bboxes:BOUNDING_BOX

## SDPoseKeypointExtractor
module: comfy_extras.nodes_sdpose | category: image/detection
- required:
  - model: MODEL
  - vae: VAE
  - image: IMAGE
  - batch_size: INT default=16 min=1 max=10000 step=1
- optional:
  - bboxes: BOUNDING_BOX default={'x': 0, 'y': 0, 'width': 512, 'height': 512}
- outputs: keypoints:POSE_KEYPOINT

## SDTurboScheduler
module: comfy_extras.nodes_custom_sampler | category: model/sampling/schedulers
- required:
  - model: MODEL
  - steps: INT default=1 min=1 max=10
  - denoise: FLOAT default=1.0 min=0 max=1.0 step=0.01
- outputs: SIGMAS:SIGMAS

## SDXL Empty Latent Image (rgthree)
module: custom_nodes.rgthree-comfy | category: rgthree
- required:
  - dimensions: COMBO[1536 x 640   (landscape), 1344 x 768   (landscape), 1216 x 832   (landscape), 1152 x 896   (landscape), 1024 x 1024  (square),  896 x 1152  (portrait),  832 x 1216  (portrait),  768 x 1344  (portrait),  640 x 1536  (portrait)] default='1024 x 1024  (square)'
  - clip_scale: FLOAT default=2.0 min=1.0 max=10.0 step=0.5
  - batch_size: INT default=1 min=1 max=64
- outputs: LATENT:LATENT, CLIP_WIDTH:INT, CLIP_HEIGHT:INT

## SDXL Power Prompt - Positive (rgthree)
module: custom_nodes.rgthree-comfy | category: rgthree
- required:
  - prompt_g: STRING
  - prompt_l: STRING
- optional:
  - opt_model: MODEL
  - opt_clip: CLIP
  - opt_clip_width: INT default=1024.0 min=0 max=16384
  - opt_clip_height: INT default=1024.0 min=0 max=16384
  - insert_lora: COMBO[CHOOSE, DISABLE LORAS, FC_ACE_h3_face_v1, FC_ALAN_h3_face_v1, FC_ANYA_h3_face_v1, FC_ARIANA_h3_face_v1, FC_BETTY_h3_face_v1, FC_CHUCK_h3_face_v1, FC_DOLLY_h3_face_v1, FC_DUDE_h3_face_v1, ... +50]
  - insert_embedding: COMBO[CHOOSE]
  - insert_saved: COMBO[CHOOSE]
  - target_width: INT default=-1 min=-1 max=16384
  - target_height: INT default=-1 min=-1 max=16384
  - crop_width: INT default=-1 min=-1 max=16384
  - crop_height: INT default=-1 min=-1 max=16384
- outputs: CONDITIONING:CONDITIONING, MODEL:MODEL, CLIP:CLIP, TEXT_G:STRING, TEXT_L:STRING

## SDXL Power Prompt - Simple / Negative (rgthree)
module: custom_nodes.rgthree-comfy | category: rgthree
- required:
  - prompt_g: STRING
  - prompt_l: STRING
- optional:
  - opt_clip: CLIP
  - opt_clip_width: INT default=1024.0 min=0 max=16384
  - opt_clip_height: INT default=1024.0 min=0 max=16384
  - insert_embedding: COMBO[CHOOSE]
  - insert_saved: COMBO[CHOOSE]
  - target_width: INT default=-1 min=-1 max=16384
  - target_height: INT default=-1 min=-1 max=16384
  - crop_width: INT default=-1 min=-1 max=16384
  - crop_height: INT default=-1 min=-1 max=16384
- outputs: CONDITIONING:CONDITIONING, TEXT_G:STRING, TEXT_L:STRING

## SDXLEmptyLatentSizePicker+
module: custom_nodes.ComfyUI_essentials | category: essentials/utilities
- required:
  - resolution: COMBO[704x1408 (0.5), 704x1344 (0.52), 768x1344 (0.57), 768x1280 (0.6), 832x1216 (0.68), 832x1152 (0.72), 896x1152 (0.78), 896x1088 (0.82), 960x1088 (0.88), 960x1024 (0.94), ... +16] default='1024x1024 (1.0)'
  - batch_size: INT default=1 min=1 max=4096
  - width_override: INT default=0 min=0 max=16384 step=8
  - height_override: INT default=0 min=0 max=16384 step=8
- outputs: LATENT:LATENT, width:INT, height:INT

## Seed (rgthree)
module: custom_nodes.rgthree-comfy | category: rgthree
- required:
  - seed: INT default=0 min=-1125899906842624 max=1125899906842624
- outputs: SEED:INT

## Seed Everywhere
module: custom_nodes.cg-use-everywhere | category: everywhere/deprecated
- required:
  - seed: INT default=0 min=0 max=18446744073709551615
- outputs: int:INT

## SeedNode
module: comfy_extras.nodes_seed | category: utilities
- required:
  - seed: INT min=0 max=9223372036854775807
- outputs: seed:INT

## SeedVR2Conditioning
module: comfy_extras.nodes_seedvr | category: model/conditioning
- required:
  - model: MODEL
  - vae_conditioning: LATENT
- outputs: positive:CONDITIONING, negative:CONDITIONING

## SeedVR2PostProcessing
module: comfy_extras.nodes_seedvr | category: image/post-processors
- required:
  - images: IMAGE
  - original_resized_images: IMAGE
  - color_correction_method: COMBO[lab, wavelet, adain, none] default='lab'
- outputs: images:IMAGE

## SeedVR2Preprocess
module: comfy_extras.nodes_seedvr | category: image/pre-processors
- required:
  - resized_images: IMAGE
- outputs: images:IMAGE

## SeedVR2TemporalChunk
module: comfy_extras.nodes_seedvr | category: model/latent/seedvr
- required:
  - latent: LATENT
  - temporal_overlap: INT default=0 min=0 max=16384
  - chunking_mode: COMFY_DYNAMICCOMBO_V3
- outputs: latents:LATENT, temporal_overlap:INT

## SeedVR2TemporalMerge
module: comfy_extras.nodes_seedvr | category: model/latent/seedvr
- required:
  - latents: LATENT
  - temporal_overlap: INT default=0 min=0 max=16384
- outputs: latent:LATENT

## SelectCLIPDevice
module: comfy_extras.nodes_multigpu | category: advanced/multigpu
- required:
  - clip: CLIP
  - device: COMBO[default, cpu]
- outputs: CLIP:CLIP

## SelectModelDevice
module: comfy_extras.nodes_multigpu | category: advanced/multigpu
- required:
  - model: MODEL
  - device: COMBO[default, cpu]
- outputs: MODEL:MODEL

## SelectVAEDevice
module: comfy_extras.nodes_multigpu | category: advanced/multigpu
- required:
  - vae: VAE
  - device: COMBO[default]
- outputs: VAE:VAE

## SelfAttentionGuidance
module: comfy_extras.nodes_sag | category: experimental
- required:
  - model: MODEL
  - scale: FLOAT default=0.5 min=-2.0 max=5.0 step=0.01
  - blur_sigma: FLOAT default=2.0 min=0.0 max=10.0 step=0.1
- outputs: MODEL:MODEL

## SelfLiftH3Sampler
module: custom_nodes.comfyui-SelfLift | category: selflift
- required:
  - model: MODEL
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - latent_image: LATENT
  - sampler: SAMPLER
  - sigmas: SIGMAS
  - seed: INT default=0 min=0 max=18446744073709551615
  - cfg: FLOAT default=5.0 min=0.0 max=100.0 step=0.1
  - transition_step: INT default=6 min=1 max=10000
  - lowres_scale: FLOAT default=0.5 min=0.25 max=1.0 step=0.05
  - rho: FLOAT default=0.0 min=0.0 max=1.0 step=0.05
  - w_min: FLOAT default=0.5 min=0.0 max=1.0 step=0.05
  - w_max: FLOAT default=1.0 min=0.0 max=1.0 step=0.05
  - upscaler_model: COMBO[none, minimax_h3_latent_upscaler_3d_conv_v1_bf16.safetensors, minimax_h3_latent_upscaler_3d_fp16.safetensors] default='minimax_h3_latent_upscaler_3d_conv_v1_bf16.safetensors'
- optional:
  - model_hires: MODEL
  - highres_tiling: BOOLEAN default=False
  - upscaler_unload: BOOLEAN default=True
- outputs: LATENT:LATENT

## SelfLiftH3TST
module: custom_nodes.comfyui-SelfLift | category: selflift
- required:
  - model: MODEL
  - tau: FLOAT default=0.2 min=0.0 max=1.0 step=0.05
  - log_diagnostics: BOOLEAN default=True
- outputs: MODEL:MODEL

## SelfLiftImageSampler
module: custom_nodes.comfyui-SelfLift | category: selflift
- required:
  - model: MODEL
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - latent_image: LATENT
  - sampler: SAMPLER
  - sigmas: SIGMAS
  - seed: INT default=0 min=0 max=18446744073709551615
  - cfg: FLOAT default=1.0 min=0.0 max=100.0 step=0.1
  - transition_step: INT default=6 min=1 max=10000
  - lowres_scale: FLOAT default=0.5 min=0.25 max=1.0 step=0.05
  - rho: FLOAT default=0.3 min=0.0 max=1.0 step=0.05
  - w_min: FLOAT default=0.5 min=0.0 max=1.0 step=0.05
  - w_max: FLOAT default=1.0 min=0.0 max=1.0 step=0.05
  - latent_upsample: COMBO[nearest, bilinear] default='nearest'
- optional:
  - model_hires: MODEL
- outputs: LATENT:LATENT

## SemSegPreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Semantic Segmentation
- required:
  - image: IMAGE
- optional:
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## SenseNovaSamplingOptions
module: comfy_extras.nodes_sensenova | category: model/patch/sensenova
- required:
  - model: MODEL
  - shift: FLOAT default=3.0 step=0.01
- outputs: MODEL:MODEL

## SeparateMasks
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking
- required:
  - mask: MASK
  - size_threshold_width: INT default=256 min=0.0 max=4096 step=1
  - size_threshold_height: INT default=256 min=0.0 max=4096 step=1
  - mode: COMBO[convex_polygons, area, box]
  - max_poly_points: INT default=8 min=3 max=32 step=1
- outputs: mask:MASK

## SetClipHooks
module: comfy_extras.nodes_hooks | category: advanced/hooks/clip
- required:
  - clip: CLIP
  - apply_to_conds: BOOLEAN default=True
  - schedule_clip: BOOLEAN default=False
- optional:
  - hooks: HOOKS
- outputs: CLIP:CLIP

## SetFirstSigma
module: comfy_extras.nodes_custom_sampler | category: model/sampling/sigmas
- required:
  - sigmas: SIGMAS
  - sigma: FLOAT default=136.0 min=0.0 max=20000.0 step=0.001
- outputs: SIGMAS:SIGMAS

## SetHookKeyframes
module: comfy_extras.nodes_hooks | category: advanced/hooks/scheduling
- required:
  - hooks: HOOKS
- optional:
  - hook_kf: HOOK_KEYFRAMES
- outputs: HOOKS:HOOKS

## SetLatentNoiseMask
module: nodes | category: model/latent
- required:
  - samples: LATENT
  - mask: MASK
- outputs: LATENT:LATENT

## SetShakkerLabsUnionControlNetType
module: custom_nodes.ComfyUI-KJNodes | category: conditioning/controlnet
- required:
  - control_net: CONTROL_NET
  - type: COMBO[auto, canny, tile, depth, blur, pose, gray, low quality]
- outputs: CONTROL_NET:CONTROL_NET

## SetUnionControlNetType
module: comfy_extras.nodes_controlnet | category: model/conditioning/controlnet
- required:
  - control_net: CONTROL_NET
  - type: COMBO[auto, openpose, depth, hed/pidi/scribble/ted, canny/lineart/anime_lineart/mlsd, normal, segment, tile, repaint]
- outputs: CONTROL_NET:CONTROL_NET

## SheetSage2AudioToABC
module: comfy_extras.nodes_audio_encoder | category: model/conditioning/yue2
- required:
  - audio_encoder: AUDIO_ENCODER
  - audio: AUDIO
  - mode: COMBO[melody, full]
- outputs: abc:STRING

## Show any [Crystools]
module: custom_nodes.ComfyUI-Crystools | category: crystools 🪛/Debugger
- optional:
  - any_value: *
  - console: BOOLEAN default=False
  - display: BOOLEAN default=True
  - prefix: STRING default=''
- outputs: 

## Show any to JSON [Crystools]
module: custom_nodes.ComfyUI-Crystools | category: crystools 🪛/Debugger
- optional:
  - any_value: *
- outputs: string:STRING

## ShowText|pysssss
module: custom_nodes.ComfyUI-Custom-Scripts | category: utils
- required:
  - text: STRING
- outputs: STRING:STRING

## ShuffleDataset
module: comfy_extras.nodes_dataset | category: image/batch
- required:
  - images: IMAGE
  - seed: INT default=0 min=0 max=18446744073709551615
- outputs: images:IMAGE

## ShuffleImageBatch
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - images: IMAGE
  - seed: INT default=123 min=0 max=18446744073709551615 step=1
- outputs: IMAGE:IMAGE

## ShuffleImageTextDataset
module: comfy_extras.nodes_dataset | category: image/batch
- required:
  - images: IMAGE
  - texts: STRING
  - seed: INT default=0 min=0 max=18446744073709551615
- outputs: images:IMAGE, texts:STRING

## ShufflePreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/T2IAdapter-only
- required:
  - image: IMAGE
- optional:
  - resolution: INT default=512 min=64 max=16384 step=64
  - seed: INT default=0 min=0 max=18446744073709551615
- outputs: IMAGE:IMAGE

## ShuffleVideoDataset
module: comfy_extras.nodes_dataset | category: video/batch
- required:
  - videos: VIDEO
  - seed: INT default=0 min=0 max=18446744073709551615
- outputs: videos:VIDEO

## ShuffleVideoTextDataset
module: comfy_extras.nodes_dataset | category: video/batch
- required:
  - videos: VIDEO
  - texts: STRING
  - seed: INT default=0 min=0 max=18446744073709551615
- outputs: videos:VIDEO, texts:STRING

## SigmasToFloat
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/noise
- required:
  - sigmas: SIGMAS
- outputs: float:FLOAT

## Simple String
module: custom_nodes.cg-use-everywhere | category: everywhere/deprecated
- required:
  - string: STRING default=''
- outputs: stringout:STRING

## SimpleCalculatorKJ
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/misc
- required:
  - expression: STRING default='a + b'
  - variables: COMFY_AUTOGROW_V3
- outputs: FLOAT:FLOAT, INT:INT, BOOLEAN:BOOLEAN

## SimpleComparison+
module: custom_nodes.ComfyUI_essentials | category: essentials/utilities
- required:
  - a: * default=0
  - b: * default=0
  - comparison: COMBO[==, !=, <, <=, >, >=]
- outputs: BOOLEAN:BOOLEAN

## SimpleCondition+
module: custom_nodes.ComfyUI_essentials | category: essentials/utilities
- required:
  - evaluate: * default=0
  - on_true: * default=0
- optional:
  - on_false: * default=None
- outputs: result:*

## SimpleMath+
module: custom_nodes.ComfyUI_essentials | category: essentials/utilities
- required:
  - value: STRING default=''
- optional:
  - a: * default=0.0
  - b: * default=0.0
  - c: * default=0.0
- outputs: INT:INT, FLOAT:FLOAT

## SimpleMathBoolean+
module: custom_nodes.ComfyUI_essentials | category: essentials/utilities
- required:
  - value: BOOLEAN default=False
- outputs: BOOLEAN:BOOLEAN

## SimpleMathCondition+
module: custom_nodes.ComfyUI_essentials | category: essentials/utilities
- required:
  - evaluate: * default=0
  - on_true: STRING default=''
  - on_false: STRING default=''
- optional:
  - a: * default=0.0
  - b: * default=0.0
  - c: * default=0.0
- outputs: INT:INT, FLOAT:FLOAT

## SimpleMathDual+
module: custom_nodes.ComfyUI_essentials | category: essentials/utilities
- required:
  - value_1: STRING default=''
  - value_2: STRING default=''
- optional:
  - a: * default=0.0
  - b: * default=0.0
  - c: * default=0.0
  - d: * default=0.0
- outputs: int_1:INT, float_1:FLOAT, int_2:INT, float_2:FLOAT

## SimpleMathFloat+
module: custom_nodes.ComfyUI_essentials | category: essentials/utilities
- required:
  - value: FLOAT default=0.0 min=-18446744073709551615 max=18446744073709551615 step=0.05
- outputs: FLOAT:FLOAT

## SimpleMathInt+
module: custom_nodes.ComfyUI_essentials | category: essentials/utilities
- required:
  - value: INT default=0 min=-18446744073709551615 max=18446744073709551615 step=1
- outputs: INT:INT

## SimpleMathPercent+
module: custom_nodes.ComfyUI_essentials | category: essentials/utilities
- required:
  - value: FLOAT default=0.0 min=0 max=1 step=0.05
- outputs: FLOAT:FLOAT

## SimpleMathSlider+
module: custom_nodes.ComfyUI_essentials | category: essentials/utilities
- required:
  - value: FLOAT default=0.5 min=0.0 max=1.0 step=0.001
  - min: FLOAT default=0.0 min=-18446744073709551615 max=18446744073709551615 step=0.001
  - max: FLOAT default=1.0 min=-18446744073709551615 max=18446744073709551615 step=0.001
  - rounding: INT default=0 min=0 max=10 step=1
- outputs: FLOAT:FLOAT, INT:INT

## SimpleMathSliderLowRes+
module: custom_nodes.ComfyUI_essentials | category: essentials/utilities
- required:
  - value: INT default=5 min=0 max=10 step=1
  - min: FLOAT default=0.0 min=-18446744073709551615 max=18446744073709551615 step=0.001
  - max: FLOAT default=1.0 min=-18446744073709551615 max=18446744073709551615 step=0.001
  - rounding: INT default=0 min=0 max=10 step=1
- outputs: FLOAT:FLOAT, INT:INT

## SimpleToggle
module: custom_nodes.ControlFlowUtils | category: 🐺 VykosX-ControlFlowUtils
- required:
  - toggle: BOOLEAN default=True
- optional:
  - run_after: *
- outputs: out:BOOLEAN

## SkipLayerGuidanceDiT
module: comfy_extras.nodes_slg | category: advanced/guidance
- required:
  - model: MODEL
  - double_layers: STRING default='7, 8, 9'
  - single_layers: STRING default='7, 8, 9'
  - scale: FLOAT default=3.0 min=0.0 max=10.0 step=0.1
  - start_percent: FLOAT default=0.01 min=0.0 max=1.0 step=0.001
  - end_percent: FLOAT default=0.15 min=0.0 max=1.0 step=0.001
  - rescaling_scale: FLOAT default=0.0 min=0.0 max=10.0 step=0.01
- outputs: MODEL:MODEL

## SkipLayerGuidanceDiTSimple
module: comfy_extras.nodes_slg | category: advanced/guidance
- required:
  - model: MODEL
  - double_layers: STRING default='7, 8, 9'
  - single_layers: STRING default='7, 8, 9'
  - start_percent: FLOAT default=0.0 min=0.0 max=1.0 step=0.001
  - end_percent: FLOAT default=1.0 min=0.0 max=1.0 step=0.001
- outputs: MODEL:MODEL

## SkipLayerGuidanceSD3
module: comfy_extras.nodes_sd3 | category: advanced/guidance
- required:
  - model: MODEL
  - layers: STRING default='7, 8, 9'
  - scale: FLOAT default=3.0 min=0.0 max=10.0 step=0.1
  - start_percent: FLOAT default=0.01 min=0.0 max=1.0 step=0.001
  - end_percent: FLOAT default=0.15 min=0.0 max=1.0 step=0.001
- outputs: MODEL:MODEL

## SkipLayerGuidanceWanVideo
module: custom_nodes.ComfyUI-KJNodes | category: advanced/guidance
- required:
  - model: MODEL
  - blocks: STRING default='10'
  - start_percent: FLOAT default=0.2 min=0.0 max=1.0 step=0.001
  - end_percent: FLOAT default=1.0 min=0.0 max=1.0 step=0.001
- outputs: MODEL:MODEL

## Sleep
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/misc
- required:
  - input: *
  - minutes: INT default=0 min=0 max=1439
  - seconds: FLOAT default=0.0 min=0.0 max=59.99 step=0.01
- outputs: *:*

## SolidMask
module: comfy_extras.nodes_mask | category: image/mask
- required:
  - value: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - width: INT default=512 min=1 max=16384 step=1
  - height: INT default=512 min=1 max=16384 step=1
- outputs: MASK:MASK

## SomethingToString
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/text
- required:
  - input: *
- optional:
  - prefix: STRING default=''
  - suffix: STRING default=''
- outputs: STRING:STRING

## SoniloTextToMusic
module: comfy_api_nodes.nodes_sonilo | category: partner/audio/Sonilo
- required:
  - prompt: STRING default=''
  - duration: INT default=30 min=1 max=360
  - seed: INT default=0 min=0 max=18446744073709551615
- outputs: AUDIO:AUDIO

## SoniloVideoToMusic
module: comfy_api_nodes.nodes_sonilo | category: partner/audio/Sonilo
- required:
  - video: VIDEO
  - prompt: STRING default=''
  - seed: INT default=0 min=0 max=18446744073709551615
- outputs: AUDIO:AUDIO

## SoundReactive
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/audio
- required:
  - sound_level: FLOAT default=1.0 min=0.0 max=99999 step=0.01
  - start_range_hz: INT default=150 min=0 max=9999 step=1
  - end_range_hz: INT default=2000 min=0 max=9999 step=1
  - multiplier: FLOAT default=1.0 min=0.01 max=99999 step=0.01
  - smoothing_factor: FLOAT default=0.5 min=0.0 max=1.0 step=0.01
  - normalize: BOOLEAN default=False
- outputs: sound_level:FLOAT, sound_level_int:INT

## SplatToFile3D
module: comfy_extras.nodes_gaussian_splat | category: 3d/splat
- required:
  - splat: SPLAT
  - format: COMBO[ply, ksplat, spz]
- outputs: model_3d:FILE_3D_SPLAT_ANY

## SplatToMesh
module: comfy_extras.nodes_gaussian_splat | category: 3d/splat
- required:
  - splat: SPLAT
  - resolution: INT default=384 min=64 max=768 step=16
  - kernel: INT default=5 min=1 max=8
  - smooth: INT default=0 min=0 max=60
  - level: FLOAT default=0.4 min=0.0 max=2.0 step=0.01
  - min_component: INT default=500 min=0 max=100000 step=50
  - min_opacity: FLOAT default=0.02 min=0.0 max=1.0 step=0.01
  - color_sharpen: FLOAT default=2.0 min=1.0 max=8.0 step=0.5
- outputs: mesh:MESH

## SplineEditor
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/weights
- required:
  - points_store: STRING
  - coordinates: STRING
  - mask_width: INT default=512 min=8 max=4096 step=8
  - mask_height: INT default=512 min=8 max=4096 step=8
  - points_to_sample: INT default=16 min=2 max=1000 step=1
  - sampling_method: COMBO[path, time, controlpoints, speed] default='time'
  - interpolation: COMBO[cardinal, monotone, basis, linear, step-before, step-after, polar, polar-reverse, bezier] default='cardinal'
  - tension: FLOAT default=0.5 min=0.0 max=1.0 step=0.01
  - repeat_output: INT default=1 min=1 max=4096 step=1
  - float_output_type: COMBO[list, pandas series, tensor] default='list'
- optional:
  - min_value: FLOAT default=0.0 min=-10000.0 max=10000.0 step=0.01
  - max_value: FLOAT default=1.0 min=-10000.0 max=10000.0 step=0.01
  - bg_image: IMAGE
- outputs: mask:MASK, coord_str:STRING, float:FLOAT, count:INT, normalized_str:STRING

## SplitAudioChannels
module: comfy_extras.nodes_audio | category: audio
- required:
  - audio: AUDIO
- outputs: left:AUDIO, right:AUDIO

## SplitBboxes
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/masking
- required:
  - bboxes: BBOX
  - index: INT default=0 min=0 max=99999999 step=1
- outputs: bboxes_a:BBOX, bboxes_b:BBOX

## SplitImageChannels
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - image: IMAGE
- outputs: red:IMAGE, green:IMAGE, blue:IMAGE, mask:MASK

## SplitImageToTileList
module: comfy_extras.nodes_images | category: image/batch
- required:
  - image: IMAGE
  - tile_width: INT default=1024 min=64 max=16384
  - tile_height: INT default=1024 min=64 max=16384
  - overlap: INT default=128 min=0 max=4096
- outputs: IMAGE:IMAGE

## SplitImageWithAlpha
module: comfy_extras.nodes_compositing | category: image/compositing
- required:
  - image: IMAGE
- outputs: IMAGE:IMAGE, MASK:MASK

## SplitSigmas
module: comfy_extras.nodes_custom_sampler | category: model/sampling/sigmas
- required:
  - sigmas: SIGMAS
  - step: INT default=0 min=0 max=10000
- outputs: high_sigmas:SIGMAS, low_sigmas:SIGMAS

## SplitSigmasDenoise
module: comfy_extras.nodes_custom_sampler | category: model/sampling/sigmas
- required:
  - sigmas: SIGMAS
  - denoise: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: high_sigmas:SIGMAS, low_sigmas:SIGMAS

## StableCascade_EmptyLatentImage
module: comfy_extras.nodes_stable_cascade | category: model/latent/stable cascade
- required:
  - width: INT default=1024 min=256 max=16384 step=8
  - height: INT default=1024 min=256 max=16384 step=8
  - compression: INT default=42 min=4 max=128 step=1
  - batch_size: INT default=1 min=1 max=4096
- outputs: stage_c:LATENT, stage_b:LATENT

## StableCascade_StageB_Conditioning
module: comfy_extras.nodes_stable_cascade | category: model/conditioning/stable cascade
- required:
  - conditioning: CONDITIONING
  - stage_c: LATENT
- outputs: CONDITIONING:CONDITIONING

## StableCascade_StageC_VAEEncode
module: comfy_extras.nodes_stable_cascade | category: model/latent/stable cascade
- required:
  - image: IMAGE
  - vae: VAE
  - compression: INT default=42 min=4 max=128 step=1
- outputs: stage_c:LATENT, stage_b:LATENT

## StableCascade_SuperResolutionControlnet
module: comfy_extras.nodes_stable_cascade | category: experimental/stable cascade
- required:
  - image: IMAGE
  - vae: VAE
- outputs: controlnet_input:IMAGE, stage_c:LATENT, stage_b:LATENT

## StableZero123_BatchSchedule
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/experimental
- required:
  - clip_vision: CLIP_VISION
  - init_image: IMAGE
  - vae: VAE
  - width: INT default=256 min=16 max=16384 step=8
  - height: INT default=256 min=16 max=16384 step=8
  - batch_size: INT default=1 min=1 max=4096
  - interpolation: COMBO[linear, ease_in, ease_out, ease_in_out]
  - azimuth_points_string: STRING default='0:(0.0),\n7:(1.0),\n15:(0.0)\n'
  - elevation_points_string: STRING default='0:(0.0),\n7:(0.0),\n15:(0.0)\n'
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## StableZero123_Conditioning
module: comfy_extras.nodes_stable3d | category: model/conditioning/stable zero123
- required:
  - clip_vision: CLIP_VISION
  - init_image: IMAGE
  - vae: VAE
  - width: INT default=256 min=16 max=16384 step=8
  - height: INT default=256 min=16 max=16384 step=8
  - batch_size: INT default=1 min=1 max=4096
  - elevation: FLOAT default=0.0 min=-180.0 max=180.0 step=0.1
  - azimuth: FLOAT default=0.0 min=-180.0 max=180.0 step=0.1
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## StableZero123_Conditioning_Batched
module: comfy_extras.nodes_stable3d | category: model/conditioning/stable zero123
- required:
  - clip_vision: CLIP_VISION
  - init_image: IMAGE
  - vae: VAE
  - width: INT default=256 min=16 max=16384 step=8
  - height: INT default=256 min=16 max=16384 step=8
  - batch_size: INT default=1 min=1 max=4096
  - elevation: FLOAT default=0.0 min=-180.0 max=180.0 step=0.1
  - azimuth: FLOAT default=0.0 min=-180.0 max=180.0 step=0.1
  - elevation_batch_increment: FLOAT default=0.0 min=-180.0 max=180.0 step=0.1
  - azimuth_batch_increment: FLOAT default=0.0 min=-180.0 max=180.0 step=0.1
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## StartLoop
module: comfy_extras.nodes_loop | category: utilities/looping
- required:
  - mode: COMFY_DYNAMICCOMBO_V3
  - cache_iterations: BOOLEAN default=False
- optional:
  - parent_iteration: INT
  - initial_iteration_value: COMFY_MATCHTYPE_V3
- outputs: iteration_index:INT, is_first:BOOLEAN, is_last:BOOLEAN, list_item:COMFY_MATCHTYPE_V3, current_iteration_value:COMFY_MATCHTYPE_V3

## StartRecordCUDAMemoryHistory
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/memory
- required:
  - input: *
  - enabled: COMBO[all, state, None] default='all'
  - context: COMBO[all, state, alloc, None] default='all'
  - stacks: COMBO[python, all] default='all'
  - max_entries: INT default=100000 min=1000 max=10000000
- outputs: input:*

## Stats system [Crystools]
module: custom_nodes.ComfyUI-Crystools | category: crystools 🪛/Utils
- required:
  - latent: LATENT
- outputs: latent:LATENT

## StoryboardImageGen
module: custom_nodes.comfyui-storyboard | category: Storyboard
- required:
  - model: MODEL
  - seed: INT default=0 min=0 max=18446744073709551615
  - steps: INT default=20 min=1 max=10000
  - cfg: FLOAT default=8.0 min=0.0 max=100.0
  - sampler_name: COMBO[euler, euler_cfg_pp, euler_ancestral, euler_ancestral_cfg_pp, heun, heunpp2, exp_heun_2_x0, exp_heun_2_x0_sde, dpm_2, dpm_2_ancestral, ... +35]
  - scheduler: COMBO[simple, sgm_uniform, karras, exponential, ddim_uniform, beta, normal, linear_quadratic, kl_optimal]
  - positive: CONDITIONING
  - negative: CONDITIONING
  - latent_image: LATENT
  - denoise: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
- outputs: LATENT:LATENT

## StringCompare
module: comfy_extras.nodes_string | category: text
- required:
  - string_a: STRING
  - string_b: STRING
  - mode: COMBO[Starts With, Ends With, Equal]
  - case_sensitive: BOOLEAN default=True
- outputs: BOOLEAN:BOOLEAN

## StringConcatenate
module: comfy_extras.nodes_string | category: text
- required:
  - string_a: STRING
  - string_b: STRING
  - delimiter: STRING default=''
- outputs: STRING:STRING

## StringConstant
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/constants
- required:
  - string: STRING default=''
- outputs: STRING:STRING

## StringConstantMultiline
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/constants
- required:
  - string: STRING default=''
  - strip_newlines: BOOLEAN default=True
- outputs: STRING:STRING

## StringContains
module: comfy_extras.nodes_string | category: text
- required:
  - string: STRING
  - substring: STRING
  - case_sensitive: BOOLEAN default=True
- outputs: contains:BOOLEAN

## StringFormat
module: comfy_extras.nodes_string | category: text
- required:
  - values: COMFY_AUTOGROW_V3
  - f_string: STRING default='{a}'
- outputs: STRING:STRING

## StringFunction|pysssss
module: custom_nodes.ComfyUI-Custom-Scripts | category: utils
- required:
  - action: COMBO[append, replace]
  - tidy_tags: COMBO[yes, no]
- optional:
  - text_a: STRING
  - text_b: STRING
  - text_c: STRING
- outputs: STRING:STRING

## StringLength
module: comfy_extras.nodes_string | category: text
- required:
  - string: STRING
- outputs: length:INT

## StringOperation
module: custom_nodes.ControlFlowUtils | category: 🐺 VykosX-ControlFlowUtils
- required:
  - input: *
  - operation: COMBO[COMPARE, CONCATENATE, COUNT, ENDS_WITH, EXTRACT_BETWEEN, FIND, GENERATE, GET_LINE, IS_ALPHA, IS_NUMERIC, ... +17]
  - start_from_end: BOOLEAN
  - case_insensitive: BOOLEAN
- optional:
  - aux1: *
  - aux2: *
  - aux3: *
  - param1: STRING
  - param2: STRING
  - param3: STRING
- outputs: output:*, result:*

## StringReplace
module: comfy_extras.nodes_string | category: text
- required:
  - string: STRING
  - find: STRING
  - replace: STRING
- outputs: STRING:STRING

## StringSubstring
module: comfy_extras.nodes_string | category: text
- required:
  - string: STRING
  - start: INT
  - end: INT
- outputs: STRING:STRING

## StringToFloatList
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/misc
- required:
  - string: STRING default='1, 2, 3'
- outputs: FLOAT:FLOAT

## StringTrim
module: comfy_extras.nodes_string | category: text
- required:
  - string: STRING
  - mode: COMBO[Both, Left, Right]
- outputs: STRING:STRING

## StripWhitespace
module: comfy_extras.nodes_dataset | category: text
- required:
  - texts: STRING
- outputs: texts:STRING

## StyleModelApply
module: nodes | category: model/conditioning
- required:
  - conditioning: CONDITIONING
  - style_model: STYLE_MODEL
  - clip_vision_output: CLIP_VISION_OUTPUT
  - strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.001
  - strength_type: COMBO[multiply, attn_bias]
- outputs: CONDITIONING:CONDITIONING

## StyleModelApplyAdvanced
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/experimental
- required:
  - conditioning: CONDITIONING
  - style_model: STYLE_MODEL
  - clip_vision_output: CLIP_VISION_OUTPUT
  - strength: FLOAT default=1.0 min=-10.0 max=10.0 step=0.001
- outputs: CONDITIONING:CONDITIONING

## StyleModelLoader
module: nodes | category: model/loaders
- required:
  - style_model_name: COMBO[]
- outputs: STYLE_MODEL:STYLE_MODEL

## Superprompt
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/text
- required:
  - instruction_prompt: STRING default='Expand the following prompt to add more detail'
  - prompt: STRING default=''
  - max_new_tokens: INT default=128 min=1 max=4096 step=1
- outputs: STRING:STRING

## SUPIRApply
module: comfy_extras.nodes_model_patch | category: model/patch/supir
- required:
  - model: MODEL
  - model_patch: MODEL_PATCH
  - vae: VAE
  - image: IMAGE
  - strength_start: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - strength_end: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - restore_cfg: FLOAT default=4.0 min=0.0 max=20.0 step=0.1
  - restore_cfg_s_tmin: FLOAT default=0.05 min=0.0 max=1.0 step=0.01
- outputs: MODEL:MODEL

## SV3D_BatchSchedule
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/experimental
- required:
  - clip_vision: CLIP_VISION
  - init_image: IMAGE
  - vae: VAE
  - width: INT default=576 min=16 max=16384 step=8
  - height: INT default=576 min=16 max=16384 step=8
  - batch_size: INT default=21 min=1 max=4096
  - interpolation: COMBO[linear, ease_in, ease_out, ease_in_out]
  - azimuth_points_string: STRING default='0:(0.0),\n9:(180.0),\n20:(360.0)\n'
  - elevation_points_string: STRING default='0:(0.0),\n9:(0.0),\n20:(0.0)\n'
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## SV3D_Conditioning
module: comfy_extras.nodes_stable3d | category: model/conditioning/stable video 3d
- required:
  - clip_vision: CLIP_VISION
  - init_image: IMAGE
  - vae: VAE
  - width: INT default=576 min=16 max=16384 step=8
  - height: INT default=576 min=16 max=16384 step=8
  - video_frames: INT default=21 min=1 max=4096
  - elevation: FLOAT default=0.0 min=-90.0 max=90.0 step=0.1
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## SVD_img2vid_Conditioning
module: comfy_extras.nodes_video_model | category: model/conditioning/stable video
- required:
  - clip_vision: CLIP_VISION
  - init_image: IMAGE
  - vae: VAE
  - width: INT default=1024 min=16 max=16384 step=8
  - height: INT default=576 min=16 max=16384 step=8
  - video_frames: INT default=14 min=1 max=4096
  - motion_bucket_id: INT default=127 min=1 max=1023
  - fps: INT default=6 min=1 max=1024
  - augmentation_level: FLOAT default=0.0 min=0.0 max=10.0 step=0.01
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## Switch any [Crystools]
module: custom_nodes.ComfyUI-Crystools | category: crystools 🪛/Switch
- required:
  - on_true: *
  - on_false: *
  - boolean: BOOLEAN default=True
- outputs: *:*

## Switch conditioning [Crystools]
module: custom_nodes.ComfyUI-Crystools | category: crystools 🪛/Switch
- required:
  - on_true: CONDITIONING
  - on_false: CONDITIONING
  - boolean: BOOLEAN default=True
- outputs: conditioning:CONDITIONING

## Switch from any [Crystools]
module: custom_nodes.ComfyUI-Crystools | category: crystools 🪛/Switch
- required:
  - any: *
  - boolean: BOOLEAN default=True
- outputs: on_true:*, on_false:*

## Switch image [Crystools]
module: custom_nodes.ComfyUI-Crystools | category: crystools 🪛/Switch
- required:
  - on_true: IMAGE
  - on_false: IMAGE
  - boolean: BOOLEAN default=True
- outputs: image:IMAGE

## Switch latent [Crystools]
module: custom_nodes.ComfyUI-Crystools | category: crystools 🪛/Switch
- required:
  - on_true: LATENT
  - on_false: LATENT
  - boolean: BOOLEAN default=True
- outputs: latent:LATENT

## Switch mask [Crystools]
module: custom_nodes.ComfyUI-Crystools | category: crystools 🪛/Switch
- required:
  - on_true: MASK
  - on_false: MASK
  - boolean: BOOLEAN default=True
- outputs: mask:MASK

## Switch string [Crystools]
module: custom_nodes.ComfyUI-Crystools | category: crystools 🪛/Switch
- required:
  - on_true: STRING default=''
  - on_false: STRING default=''
  - boolean: BOOLEAN default=True
- outputs: string:STRING

## SyncLipSyncNode
module: comfy_api_nodes.nodes_sync_so | category: partner/video/sync.so
- required:
  - video: VIDEO
  - audio: AUDIO
  - seed: INT default=42 min=0 max=2147483647
  - model: COMFY_DYNAMICCOMBO_V3
- outputs: VIDEO:VIDEO

## SyncTalkingImageNode
module: comfy_api_nodes.nodes_sync_so | category: partner/video/sync.so
- required:
  - image: IMAGE
  - audio: AUDIO
  - prompt: STRING default=''
  - seed: INT default=0 min=0 max=2147483647
  - model: COMFY_DYNAMICCOMBO_V3
- outputs: VIDEO:VIDEO

## SystemNotification|pysssss
module: custom_nodes.ComfyUI-Custom-Scripts | category: utils
- required:
  - message: STRING default='Your notification has triggered.'
  - any: *
  - mode: COMBO[always, on empty queue]
- outputs: *:*

## T5TokenizerOptions
module: comfy_extras.nodes_cond | category: model/conditioning
- required:
  - clip: CLIP
  - min_padding: INT default=0 min=0 max=10000 step=1
  - min_length: INT default=0 min=0 max=10000 step=1
- outputs: CLIP:CLIP

## TCFG
module: comfy_extras.nodes_tcfg | category: advanced/guidance
- required:
  - model: MODEL
- outputs: patched_model:MODEL

## TEEDPreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Line Extractors
- required:
  - image: IMAGE
- optional:
  - safe_steps: INT default=2 min=0 max=10 step=1
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## TemporalScoreRescaling
module: comfy_extras.nodes_eps | category: model/patch/unet
- required:
  - model: MODEL
  - tsr_k: FLOAT default=0.95 min=0.01 max=100.0 step=0.001
  - tsr_sigma: FLOAT default=1.0 min=0.01 max=100.0 step=0.001
- outputs: patched_model:MODEL

## Tencent3DPartNode
module: comfy_api_nodes.nodes_hunyuan3d | category: partner/3d/Tencent
- required:
  - model_3d: FILE_3D_FBX,FILE_3D
  - seed: INT default=0 min=0 max=2147483647
- outputs: FBX:FILE_3D_FBX

## Tencent3DTextureEditNode
module: comfy_api_nodes.nodes_hunyuan3d | category: partner/3d/Tencent
- required:
  - model_3d: FILE_3D_FBX,FILE_3D
  - prompt: STRING default=''
  - seed: INT default=0 min=0 max=2147483647
- outputs: GLB:FILE_3D_GLB, OBJ:FILE_3D_OBJ, texture_image:IMAGE

## TencentImageToModelNode
module: comfy_api_nodes.nodes_hunyuan3d | category: partner/3d/Tencent
- required:
  - model: COMBO[3.0, 3.1]
  - image: IMAGE
  - face_count: INT default=500000 min=3000 max=1500000
  - generate_type: COMFY_DYNAMICCOMBO_V3
  - seed: INT default=0 min=0 max=2147483647
- optional:
  - image_left: IMAGE
  - image_right: IMAGE
  - image_back: IMAGE
- outputs: model_file:STRING, GLB:FILE_3D_GLB, OBJ:FILE_3D_OBJ, texture_image:IMAGE, optional_metallic:IMAGE, optional_normal:IMAGE, optional_roughness:IMAGE

## TencentModelTo3DUVNode
module: comfy_api_nodes.nodes_hunyuan3d | category: partner/3d/Tencent
- required:
  - model_3d: FILE_3D_GLB,FILE_3D_OBJ,FILE_3D_FBX,FILE_3D
  - seed: INT default=1 min=0 max=2147483647
- outputs: OBJ:FILE_3D_OBJ, FBX:FILE_3D_FBX, uv_image:IMAGE

## TencentSmartTopologyNode
module: comfy_api_nodes.nodes_hunyuan3d | category: partner/3d/Tencent
- required:
  - model_3d: FILE_3D_GLB,FILE_3D_OBJ,FILE_3D
  - polygon_type: COMBO[triangle, quadrilateral]
  - face_level: COMBO[medium, high, low]
  - seed: INT default=0 min=0 max=2147483647
- outputs: OBJ:FILE_3D_OBJ

## TencentTextToModelNode
module: comfy_api_nodes.nodes_hunyuan3d | category: partner/3d/Tencent
- required:
  - model: COMBO[3.0, 3.1]
  - prompt: STRING default=''
  - face_count: INT default=500000 min=3000 max=1500000
  - generate_type: COMFY_DYNAMICCOMBO_V3
  - seed: INT default=0 min=0 max=2147483647
- outputs: model_file:STRING, GLB:FILE_3D_GLB, OBJ:FILE_3D_OBJ, texture_image:IMAGE

## TextEncodeAceStepAudio
module: comfy_extras.nodes_ace | category: model/conditioning/ace
- required:
  - clip: CLIP
  - tags: STRING
  - lyrics: STRING
  - lyrics_strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
- outputs: CONDITIONING:CONDITIONING

## TextEncodeAceStepAudio1.5
module: comfy_extras.nodes_ace | category: model/conditioning/ace
- required:
  - clip: CLIP
  - tags: STRING
  - lyrics: STRING
  - seed: INT default=0 min=0 max=18446744073709551615
  - bpm: INT default=120 min=10 max=300
  - duration: FLOAT default=120.0 min=0.0 max=2000.0 step=0.1
  - timesignature: COMBO[2, 3, 4, 6]
  - language: COMBO[ar, az, bg, bn, ca, cs, da, de, el, en, ... +41] default='en'
  - keyscale: COMBO[C major, C# major, Db major, D major, D# major, Eb major, E major, F major, F# major, Gb major, ... +24]
  - generate_audio_codes: BOOLEAN default=True
  - cfg_scale: FLOAT default=2.0 min=0.0 max=100.0 step=0.1
  - temperature: FLOAT default=0.85 min=0.0 max=2.0 step=0.01
  - top_p: FLOAT default=0.9 min=0.0 max=2000.0 step=0.01
  - top_k: INT default=0 min=0 max=100
  - min_p: FLOAT default=0.0 min=0.0 max=1.0 step=0.001
- outputs: CONDITIONING:CONDITIONING

## TextEncodeBooguEdit
module: comfy_extras.nodes_boogu | category: model/conditioning/boogu
- required:
  - clip: CLIP
  - prompt: STRING
  - negative_prompt: STRING
  - vae: VAE
  - images: COMFY_AUTOGROW_V3
- outputs: positive:CONDITIONING, negative:CONDITIONING

## TextEncodeForSamplerParams+
module: custom_nodes.ComfyUI_essentials | category: essentials/sampling
- required:
  - text: STRING default='Separate prompts with at least three dashes\n---\nLike so'
  - clip: CLIP
- outputs: CONDITIONING:CONDITIONING

## TextEncodeHunyuanVideo_ImageToVideo
module: comfy_extras.nodes_hunyuan | category: model/conditioning/hunyuan video
- required:
  - clip: CLIP
  - clip_vision_output: CLIP_VISION_OUTPUT
  - prompt: STRING
  - image_interleave: INT default=2 min=1 max=512
- outputs: CONDITIONING:CONDITIONING

## TextEncodeJoyImageEdit
module: comfy_extras.nodes_joyimage | category: model/conditioning/joyimage
- required:
  - clip: CLIP
  - prompt: STRING
- optional:
  - vae: VAE
  - images: COMFY_AUTOGROW_V3
- outputs: CONDITIONING:CONDITIONING

## TextEncodeMageFlowEdit
module: comfy_extras.nodes_mage | category: model/conditioning/mage
- required:
  - clip: CLIP
  - prompt: STRING
  - negative_prompt: STRING
  - images: COMFY_AUTOGROW_V3
  - width: INT default=0 min=0 max=8192 step=16
  - height: INT default=0 min=0 max=8192 step=16
  - batch_size: INT default=1 min=1 max=4096
- optional:
  - vae: VAE
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## TextEncodeMingImageEdit
module: comfy_extras.nodes_ming | category: model/conditioning/ming image
- required:
  - clip: CLIP
  - prompt: STRING
  - images: COMFY_AUTOGROW_V3
- optional:
  - vae: VAE
- outputs: CONDITIONING:CONDITIONING

## TextEncodeQwenImage21
module: comfy_extras.nodes_qwen | category: model/conditioning/qwen image
- required:
  - clip: CLIP
  - prompt: STRING
  - negative_prompt: STRING
  - resolution: INT default=1024 min=0 max=4096 step=32
  - images: COMFY_AUTOGROW_V3
- optional:
  - vae: VAE
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## TextEncodeQwenImageEdit
module: comfy_extras.nodes_qwen | category: model/conditioning/qwen image
- required:
  - clip: CLIP
  - prompt: STRING
- optional:
  - vae: VAE
  - image: IMAGE
- outputs: CONDITIONING:CONDITIONING

## TextEncodeQwenImageEditPlus
module: comfy_extras.nodes_qwen | category: model/conditioning/qwen image
- required:
  - clip: CLIP
  - prompt: STRING
- optional:
  - vae: VAE
  - image1: IMAGE
  - image2: IMAGE
  - image3: IMAGE
- outputs: CONDITIONING:CONDITIONING

## TextEncodeZImageOmni
module: comfy_extras.nodes_zimage | category: model/conditioning/z-image
- required:
  - clip: CLIP
  - prompt: STRING
  - auto_resize_images: BOOLEAN default=True
- optional:
  - image_encoder: CLIP_VISION
  - vae: VAE
  - image1: IMAGE
  - image2: IMAGE
  - image3: IMAGE
- outputs: CONDITIONING:CONDITIONING

## TextGenerate
module: comfy_extras.nodes_textgen | category: text
- required:
  - clip: CLIP
  - prompt: STRING default=''
  - max_length: INT default=512 min=1 max=32768
  - sampling_mode: COMFY_DYNAMICCOMBO_V3
- optional:
  - image: IMAGE
  - video: IMAGE
  - audio: AUDIO
  - thinking: BOOLEAN default=False
  - use_default_template: BOOLEAN default=True
  - mtp: COMBO[auto, off, 2, 3, 4, 5] default='auto'
  - system_prompt: STRING
- outputs: generated_text:STRING, thinking:STRING

## TextGenerateLTX2Prompt
module: comfy_extras.nodes_textgen | category: text
- required:
  - clip: CLIP
  - prompt: STRING default=''
  - max_length: INT default=512 min=1 max=32768
  - sampling_mode: COMFY_DYNAMICCOMBO_V3
- optional:
  - image: IMAGE
  - video: IMAGE
  - audio: AUDIO
  - thinking: BOOLEAN default=False
  - use_default_template: BOOLEAN default=True
  - mtp: COMBO[auto, off, 2, 3, 4, 5] default='auto'
  - system_prompt: STRING
- outputs: generated_text:STRING, thinking:STRING

## TextOverlay
module: comfy_extras.nodes_text_overlay | category: text
- required:
  - images: IMAGE
  - text: STRING default=''
  - font_size: FLOAT default=5.0 min=0.5 max=50.0 step=0.5
  - color: COLOR default='#ffffff'
  - position: COMBO[top, bottom] default='top'
  - align: COMBO[left, center, right] default='left'
  - outline: BOOLEAN default=True
- outputs: images:IMAGE

## TextToLowercase
module: comfy_extras.nodes_dataset | category: text
- required:
  - texts: STRING
- outputs: texts:STRING

## TextToUppercase
module: comfy_extras.nodes_dataset | category: text
- required:
  - texts: STRING
- outputs: texts:STRING

## ThresholdMask
module: comfy_extras.nodes_mask | category: image/mask
- required:
  - mask: MASK
  - value: FLOAT default=0.5 min=0.0 max=1.0 step=0.01
- outputs: MASK:MASK

## TilePreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/tile
- required:
  - image: IMAGE
- optional:
  - pyrUp_iters: INT default=3 min=1 max=10 step=1
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## TimerNodeKJ
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/misc
- required:
  - any_input: *
  - mode: COMBO[start, stop]
  - name: STRING default='Timer'
- optional:
  - timer: TIMER
- outputs: any_output:*, timer:TIMER, time:INT

## TomePatchModel
module: comfy_extras.nodes_tomesd | category: model/patch/unet
- required:
  - model: MODEL
  - ratio: FLOAT default=0.3 min=0.0 max=1.0 step=0.01
- outputs: MODEL:MODEL

## TopazImageEnhance
module: comfy_api_nodes.nodes_topaz | category: partner/image/Topaz
- required:
  - model: COMBO[Reimagine]
  - image: IMAGE
- optional:
  - prompt: STRING default=''
  - subject_detection: COMBO[All, Foreground, Background]
  - face_enhancement: BOOLEAN default=True
  - face_enhancement_creativity: FLOAT default=0.0 min=0.0 max=1.0 step=0.01
  - face_enhancement_strength: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - crop_to_fill: BOOLEAN default=False
  - output_width: INT default=0 min=0 max=32000 step=1
  - output_height: INT default=0 min=0 max=32000 step=1
  - creativity: INT default=3 min=1 max=9 step=1
  - face_preservation: BOOLEAN default=True
  - color_preservation: BOOLEAN default=True
- outputs: IMAGE:IMAGE

## TopazImageEnhanceV2
module: comfy_api_nodes.nodes_topaz | category: partner/image/Topaz
- required:
  - image: IMAGE
  - model: COMFY_DYNAMICCOMBO_V3
- optional:
  - output_width: INT default=0 min=0 max=32000 step=1
  - output_height: INT default=0 min=0 max=32000 step=1
- outputs: IMAGE:IMAGE

## TopazVideoEnhance
module: comfy_api_nodes.nodes_topaz | category: partner/video/Topaz
- required:
  - video: VIDEO
  - upscaler_enabled: BOOLEAN default=True
  - upscaler_model: COMBO[Starlight (Astra) Fast, Starlight (Astra) Creative, Starlight Precise 2.5]
  - upscaler_resolution: COMBO[FullHD (1080p), 4K (2160p)]
- optional:
  - upscaler_creativity: COMBO[low, middle, high] default='low'
  - interpolation_enabled: BOOLEAN default=False
  - interpolation_model: COMBO[apo-8] default='apo-8'
  - interpolation_slowmo: INT default=1 min=1 max=16
  - interpolation_frame_rate: INT default=60 min=15 max=240
  - interpolation_duplicate: BOOLEAN default=False
  - interpolation_duplicate_threshold: FLOAT default=0.01 min=0.001 max=0.1 step=0.001
  - dynamic_compression_level: COMBO[Low, Mid, High] default='Low'
- outputs: VIDEO:VIDEO

## TopazVideoEnhanceV2
module: comfy_api_nodes.nodes_topaz | category: partner/video/Topaz
- required:
  - video: VIDEO
  - upscaler_model: COMFY_DYNAMICCOMBO_V3
  - interpolation_model: COMFY_DYNAMICCOMBO_V3
- optional:
  - dynamic_compression_level: COMBO[Low, Mid, High] default='Low'
- outputs: VIDEO:VIDEO

## TorchCompileControlNet
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/torchcompile
- required:
  - controlnet: CONTROL_NET
  - backend: COMBO[inductor, cudagraphs]
  - fullgraph: BOOLEAN default=False
  - mode: COMBO[default, max-autotune, max-autotune-no-cudagraphs, reduce-overhead] default='default'
- outputs: CONTROL_NET:CONTROL_NET

## TorchCompileCosmosModel
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/deprecated
- required:
  - model: *
- outputs: *:*

## TorchCompileLTXModel
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/deprecated
- required:
  - model: *
- outputs: *:*

## TorchCompileModel
module: comfy_extras.nodes_torch_compile | category: experimental
- required:
  - model: MODEL
  - backend: COMBO[inductor, cudagraphs]
- outputs: MODEL:MODEL

## TorchCompileModelAdvanced
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/torchcompile
- required:
  - model: MODEL
  - backend: COMBO[inductor, cudagraphs] default='inductor'
  - fullgraph: BOOLEAN default=False
  - mode: COMBO[default, max-autotune, max-autotune-no-cudagraphs, reduce-overhead] default='default'
  - dynamic: COMBO[auto, true, false] default='auto'
  - compile_transformer_blocks_only: BOOLEAN default=True
  - dynamo_cache_size_limit: INT default=64 min=0 max=1024 step=1
  - debug_compile_keys: BOOLEAN default=False
- optional:
  - disable_dynamic_vram: BOOLEAN default=False
- outputs: MODEL:MODEL

## TorchCompileModelFluxAdvanced
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/deprecated
- required:
  - model: *
- outputs: *:*

## TorchCompileModelFluxAdvancedV2
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/torchcompile
- required:
  - model: MODEL
  - backend: COMBO[inductor, cudagraphs]
  - fullgraph: BOOLEAN default=False
  - mode: COMBO[default, max-autotune, max-autotune-no-cudagraphs, reduce-overhead] default='default'
  - double_blocks: BOOLEAN default=True
  - single_blocks: BOOLEAN default=True
  - dynamic: BOOLEAN default=False
- optional:
  - dynamo_cache_size_limit: INT default=64 min=0 max=1024 step=1
  - force_parameter_static_shapes: BOOLEAN default=True
- outputs: MODEL:MODEL

## TorchCompileModelHyVideo
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/deprecated
- required:
  - model: *
- outputs: *:*

## TorchCompileModelQwenImage
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/deprecated
- required:
  - model: *
- outputs: *:*

## TorchCompileModelWanVideo
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/deprecated
- required:
  - model: *
- outputs: *:*

## TorchCompileModelWanVideoV2
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/torchcompile
- required:
  - model: MODEL
  - backend: COMBO[inductor, cudagraphs] default='inductor'
  - fullgraph: BOOLEAN default=False
  - mode: COMBO[default, max-autotune, max-autotune-no-cudagraphs, reduce-overhead] default='default'
  - dynamic: BOOLEAN default=False
  - compile_transformer_blocks_only: BOOLEAN default=True
  - dynamo_cache_size_limit: INT default=64 min=0 max=1024 step=1
- optional:
  - force_parameter_static_shapes: BOOLEAN default=True
- outputs: MODEL:MODEL

## TorchCompileVAE
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/torchcompile
- required:
  - vae: VAE
  - backend: COMBO[inductor, cudagraphs]
  - fullgraph: BOOLEAN default=False
  - mode: COMBO[default, max-autotune, max-autotune-no-cudagraphs, reduce-overhead] default='default'
  - compile_encoder: BOOLEAN default=True
  - compile_decoder: BOOLEAN default=True
- outputs: VAE:VAE

## TrainLoraNode
module: comfy_extras.nodes_train | category: model/training
- required:
  - model: MODEL
  - latents: LATENT
  - positive: CONDITIONING
  - batch_size: INT default=1 min=1 max=10000
  - grad_accumulation_steps: INT default=1 min=1 max=1024
  - steps: INT default=16 min=1 max=100000
  - learning_rate: FLOAT default=0.0005 min=1e-07 max=1.0 step=1e-07
  - rank: INT default=8 min=1 max=128
  - optimizer: COMBO[AdamW, Adam, SGD, RMSprop] default='AdamW'
  - loss_function: COMBO[MSE, L1, Huber, SmoothL1] default='MSE'
  - seed: INT default=0 min=0 max=18446744073709551615
  - training_dtype: COMBO[bf16, fp32, none] default='bf16'
  - lora_dtype: COMBO[bf16, fp32] default='bf16'
  - quantized_backward: BOOLEAN default=False
  - algorithm: COMBO[LoRA, LoHa, LoKr, OFT] default='LoRA'
  - gradient_checkpointing: BOOLEAN default=True
  - checkpoint_depth: INT default=1 min=1 max=5
  - offloading: BOOLEAN default=False
  - existing_lora: COMBO[FC_ACE_h3_face_v1.safetensors, FC_ALAN_h3_face_v1.safetensors, FC_ANYA_h3_face_v1.safetensors, FC_ARIANA_h3_face_v1.safetensors, FC_BETTY_h3_face_v1.safetensors, FC_CHUCK_h3_face_v1.safetensors, FC_DOLLY_h3_face_v1.safetensors, FC_DUDE_h3_face_v1.safetensors, FC_JENNIFER_h3_face_v1.safetensors, FC_KIERNAN_h3_face_v1.safetensors, ... +49] default='[None]'
  - bucket_mode: BOOLEAN default=False
  - bypass_mode: BOOLEAN default=False
- outputs: lora:LORA_MODEL, loss_map:LOSS_MAP, steps:INT

## TransformSplat
module: comfy_extras.nodes_gaussian_splat | category: 3d/splat
- required:
  - splat: SPLAT
  - translate_x: FLOAT default=0.0 min=-100.0 max=100.0 step=0.01
  - translate_y: FLOAT default=0.0 min=-100.0 max=100.0 step=0.01
  - translate_z: FLOAT default=0.0 min=-100.0 max=100.0 step=0.01
  - rotate_x: FLOAT default=0.0 min=-360.0 max=360.0 step=1.0
  - rotate_y: FLOAT default=0.0 min=-360.0 max=360.0 step=1.0
  - rotate_z: FLOAT default=0.0 min=-360.0 max=360.0 step=1.0
  - scale_x: FLOAT default=1.0 min=0.01 max=100.0 step=0.01
  - scale_y: FLOAT default=1.0 min=0.01 max=100.0 step=0.01
  - scale_z: FLOAT default=1.0 min=0.01 max=100.0 step=0.01
- outputs: splat:SPLAT

## TransitionImagesInBatch
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - images: IMAGE
  - interpolation: COMBO[linear, ease_in, ease_out, ease_in_out, bounce, elastic, glitchy, exponential_ease_out]
  - transition_type: COMBO[horizontal slide, vertical slide, box, circle, horizontal door, vertical door, fade]
  - transitioning_frames: INT default=1 min=0 max=4096 step=1
  - blur_radius: FLOAT default=0.0 min=0.0 max=100.0 step=0.1
  - reverse: BOOLEAN default=False
  - device: COMBO[CPU, GPU] default='CPU'
- outputs: IMAGE:IMAGE

## TransitionImagesMulti
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/image
- required:
  - inputcount: INT default=2 min=2 max=1000 step=1
  - image_1: IMAGE
  - interpolation: COMBO[linear, ease_in, ease_out, ease_in_out, bounce, elastic, glitchy, exponential_ease_out]
  - transition_type: COMBO[horizontal slide, vertical slide, box, circle, horizontal door, vertical door, fade]
  - transitioning_frames: INT default=2 min=2 max=4096 step=1
  - blur_radius: FLOAT default=0.0 min=0.0 max=100.0 step=0.1
  - reverse: BOOLEAN default=False
  - device: COMBO[CPU, GPU] default='CPU'
- optional:
  - image_2: IMAGE
- outputs: IMAGE:IMAGE

## TransitionMask+
module: custom_nodes.ComfyUI_essentials | category: essentials/mask
- required:
  - width: INT default=512 min=1 max=16384 step=1
  - height: INT default=512 min=1 max=16384 step=1
  - frames: INT default=16 min=1 max=9999 step=1
  - start_frame: INT default=0 min=0 step=1
  - end_frame: INT default=9999 min=0 step=1
  - transition_type: COMBO[horizontal slide, vertical slide, horizontal bar, vertical bar, center box, horizontal door, vertical door, circle, fade]
  - timing_function: COMBO[linear, in, out, in-out]
- outputs: MASK:MASK

## TransparentBGSession+
module: custom_nodes.ComfyUI_essentials | category: essentials/image manipulation
- required:
  - mode: COMBO[base, fast, base-nightly]
  - use_jit: BOOLEAN default=True
- outputs: REMBG_SESSION:REMBG_SESSION

## Trellis2Conditioning
module: comfy_extras.nodes_trellis2 | category: model/conditioning/trellis
- required:
  - clip_vision_model: CLIP_VISION
  - image: IMAGE
- outputs: positive:CONDITIONING, negative:CONDITIONING

## Trellis2ShapeStage
module: comfy_extras.nodes_trellis2 | category: model/conditioning/trellis
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - voxel: VOXEL
- outputs: positive:CONDITIONING, negative:CONDITIONING, LATENT:LATENT

## Trellis2TextureStage
module: comfy_extras.nodes_trellis2 | category: model/conditioning/trellis
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - shape_latent: LATENT
- outputs: positive:CONDITIONING, negative:CONDITIONING, LATENT:LATENT

## Trellis2UpsampleStage
module: comfy_extras.nodes_trellis2 | category: model/conditioning/trellis
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - shape_latent: LATENT
  - vae: VAE
  - target_resolution: INT default=1024 min=1024 max=2048 step=128
- outputs: positive:CONDITIONING, negative:CONDITIONING, LATENT:LATENT

## TrimAudioDuration
module: comfy_extras.nodes_audio | category: audio
- required:
  - audio: AUDIO
  - start_index: FLOAT default=0.0 min=-18446744073709551615 max=18446744073709551615 step=0.01
  - duration: FLOAT default=60.0 min=0.0 step=0.01
- outputs: AUDIO:AUDIO

## TrimVideoLatent
module: comfy_extras.nodes_wan | category: model/latent
- required:
  - samples: LATENT
  - trim_amount: INT default=0 min=0 max=99999
- outputs: LATENT:LATENT

## TripleCLIPLoader
module: comfy_extras.nodes_sd3 | category: model/loaders
- required:
  - clip_name1: COMBO[clip_l.safetensors, qwen3vl_32b_minimax_h3_int4_convrot.safetensors, qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors, qwen_3_4b.safetensors, qwen_3_8b_fp8mixed.safetensors, umt5_xxl_fp8_e4m3fn_scaled.safetensors]
  - clip_name2: COMBO[clip_l.safetensors, qwen3vl_32b_minimax_h3_int4_convrot.safetensors, qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors, qwen_3_4b.safetensors, qwen_3_8b_fp8mixed.safetensors, umt5_xxl_fp8_e4m3fn_scaled.safetensors]
  - clip_name3: COMBO[clip_l.safetensors, qwen3vl_32b_minimax_h3_int4_convrot.safetensors, qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors, qwen_3_4b.safetensors, qwen_3_8b_fp8mixed.safetensors, umt5_xxl_fp8_e4m3fn_scaled.safetensors]
- outputs: CLIP:CLIP

## TripleCLIPLoaderGGUF
module: custom_nodes.ComfyUI-GGUF | category: bootleg
- required:
  - clip_name1: COMBO[clip_l.safetensors, qwen3vl_32b_minimax_h3_int4_convrot.safetensors, qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors, qwen_3_4b.safetensors, qwen_3_8b_fp8mixed.safetensors, umt5_xxl_fp8_e4m3fn_scaled.safetensors]
  - clip_name2: COMBO[clip_l.safetensors, qwen3vl_32b_minimax_h3_int4_convrot.safetensors, qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors, qwen_3_4b.safetensors, qwen_3_8b_fp8mixed.safetensors, umt5_xxl_fp8_e4m3fn_scaled.safetensors]
  - clip_name3: COMBO[clip_l.safetensors, qwen3vl_32b_minimax_h3_int4_convrot.safetensors, qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors, qwen_3_4b.safetensors, qwen_3_8b_fp8mixed.safetensors, umt5_xxl_fp8_e4m3fn_scaled.safetensors]
- outputs: CLIP:CLIP

## TripoConversionNode
module: comfy_api_nodes.nodes_tripo | category: partner/3d/Tripo
- required:
  - original_model_task_id: MODEL_TASK_ID,RIG_TASK_ID,RETARGET_TASK_ID,SEGMENT_TASK_ID
  - format: COMBO[GLTF, USDZ, FBX, OBJ, STL, 3MF]
- optional:
  - quad: BOOLEAN default=False
  - face_limit: INT default=-1 min=-1 max=2000000
  - texture_size: INT default=4096 min=128 max=8192
  - texture_format: COMBO[BMP, DPX, HDR, JPEG, OPEN_EXR, PNG, TARGA, TIFF, WEBP] default='JPEG'
  - force_symmetry: BOOLEAN default=False
  - flatten_bottom: BOOLEAN default=False
  - flatten_bottom_threshold: FLOAT default=0.01 min=0.01 max=1.0
  - pivot_to_center_bottom: BOOLEAN default=False
  - scale_factor: FLOAT default=1.0 min=0.01
  - with_animation: BOOLEAN default=True
  - pack_uv: BOOLEAN default=False
  - bake: BOOLEAN default=True
  - part_names: STRING default=''
  - fbx_preset: COMBO[blender, mixamo, 3dsmax, bake_scale] default='blender'
  - export_vertex_colors: BOOLEAN default=False
  - export_orientation: COMBO[default, +x, -x, +y, -y] default='default'
  - animate_in_place: BOOLEAN default=False
- outputs: model_3d:FILE_3D

## TripoEditMultiviewNode
module: comfy_api_nodes.nodes_tripo | category: partner/3d/Tripo
- required:
  - multiview_task_id: MULTIVIEW_TASK_ID
- optional:
  - front_prompt: STRING default=''
  - left_prompt: STRING default=''
  - back_prompt: STRING default=''
  - right_prompt: STRING default=''
- outputs: front:IMAGE, left:IMAGE, back:IMAGE, right:IMAGE

## TripoImageToModelNode
module: comfy_api_nodes.nodes_tripo | category: partner/3d/Tripo
- required:
  - image: IMAGE
- optional:
  - model_version: COMBO[v3.1-20260211, v3.0-20250812, v2.5-20250123]
  - style: COMBO[person:person2cartoon, animal:venom, object:clay, object:steampunk, object:christmas, object:barbie, gold, ancient_bronze, None] default='None'
  - texture: BOOLEAN default=True
  - pbr: BOOLEAN default=True
  - model_seed: INT default=42 min=0 max=2147483647
  - orientation: COMBO[align_image, default] default='default'
  - texture_seed: INT default=42 min=0 max=2147483647
  - texture_quality: COMBO[standard, detailed, extreme] default='standard'
  - texture_alignment: COMBO[original_image, geometry] default='original_image'
  - face_limit: INT default=-1 min=-1 max=2000000
  - quad: BOOLEAN default=False
  - geometry_quality: COMBO[standard, detailed] default='standard'
  - smart_low_poly: BOOLEAN default=False
  - auto_size: BOOLEAN default=True
- outputs: model_file:STRING, model task_id:MODEL_TASK_ID, GLB:FILE_3D_GLB, FBX:FILE_3D_FBX

## TripoImageToModelNodeV2
module: comfy_api_nodes.nodes_tripo | category: partner/3d/Tripo
- required:
  - image: IMAGE
- optional:
  - model_version: COMBO[v3.1-20260211, v3.0-20250812, v2.5-20250123]
  - texture: BOOLEAN default=True
  - pbr: BOOLEAN default=True
  - model_seed: INT default=42 min=0 max=2147483647
  - orientation: COMBO[align_image, default] default='default'
  - texture_seed: INT default=42 min=0 max=2147483647
  - texture_quality: COMBO[standard, detailed, extreme] default='standard'
  - texture_alignment: COMBO[original_image, geometry] default='original_image'
  - face_limit: INT default=-1 min=-1 max=2000000
  - quad: BOOLEAN default=False
  - geometry_quality: COMBO[standard, detailed] default='standard'
  - smart_low_poly: BOOLEAN default=False
  - auto_size: BOOLEAN default=True
- outputs: model task_id:MODEL_TASK_ID, GLB:FILE_3D_GLB, FBX:FILE_3D_FBX

## TripoImageToMultiviewNode
module: comfy_api_nodes.nodes_tripo | category: partner/3d/Tripo
- required:
  - image: IMAGE
- outputs: multiview task_id:MULTIVIEW_TASK_ID, front:IMAGE, left:IMAGE, back:IMAGE, right:IMAGE

## TripoImportModelNode
module: comfy_api_nodes.nodes_tripo | category: partner/3d/Tripo
- required:
  - model_3d: FILE_3D_GLB,FILE_3D_FBX,FILE_3D_OBJ,FILE_3D_STL,FILE_3D
- outputs: model task_id:MODEL_TASK_ID

## TripoMeshCompleteNode
module: comfy_api_nodes.nodes_tripo | category: partner/3d/Tripo
- required:
  - segment_task_id: SEGMENT_TASK_ID
- optional:
  - part_names: STRING default=''
- outputs: model_file:STRING, model task_id:MODEL_TASK_ID, GLB:FILE_3D_GLB

## TripoMultiviewToModelNode
module: comfy_api_nodes.nodes_tripo | category: partner/3d/Tripo
- required:
  - image: IMAGE
- optional:
  - image_left: IMAGE
  - image_back: IMAGE
  - image_right: IMAGE
  - model_version: COMBO[v3.1-20260211, v3.0-20250812, v2.5-20250123]
  - orientation: COMBO[align_image, default] default='default'
  - texture: BOOLEAN default=True
  - pbr: BOOLEAN default=True
  - model_seed: INT default=42 min=0 max=2147483647
  - texture_seed: INT default=42 min=0 max=2147483647
  - texture_quality: COMBO[standard, detailed, extreme] default='standard'
  - texture_alignment: COMBO[original_image, geometry] default='original_image'
  - face_limit: INT default=-1 min=-1 max=2000000
  - quad: BOOLEAN default=False
  - geometry_quality: COMBO[standard, detailed] default='standard'
  - smart_low_poly: BOOLEAN default=False
  - auto_size: BOOLEAN default=False
- outputs: model_file:STRING, model task_id:MODEL_TASK_ID, GLB:FILE_3D_GLB, FBX:FILE_3D_FBX

## TripoP1ImageToModelNode
module: comfy_api_nodes.nodes_tripo | category: partner/3d/Tripo
- required:
  - image: IMAGE
  - output_mode: COMFY_DYNAMICCOMBO_V3
- optional:
  - enable_image_autofix: BOOLEAN default=False
  - face_limit: INT default=-1 min=-1 max=20000
  - model_seed: INT default=42 min=0 max=2147483647
  - auto_size: BOOLEAN default=False
  - export_uv: BOOLEAN default=True
  - compress_geometry: BOOLEAN default=False
- outputs: model_file:STRING, model task_id:MODEL_TASK_ID, GLB:FILE_3D_GLB

## TripoP1MultiviewToModelNode
module: comfy_api_nodes.nodes_tripo | category: partner/3d/Tripo
- required:
  - image: IMAGE
  - output_mode: COMFY_DYNAMICCOMBO_V3
- optional:
  - image_left: IMAGE
  - image_back: IMAGE
  - image_right: IMAGE
  - face_limit: INT default=-1 min=-1 max=20000
  - model_seed: INT default=42 min=0 max=2147483647
  - auto_size: BOOLEAN default=False
  - export_uv: BOOLEAN default=True
  - compress_geometry: BOOLEAN default=False
- outputs: model_file:STRING, model task_id:MODEL_TASK_ID, GLB:FILE_3D_GLB

## TripoP1TextToModelNode
module: comfy_api_nodes.nodes_tripo | category: partner/3d/Tripo
- required:
  - prompt: STRING
  - output_mode: COMFY_DYNAMICCOMBO_V3
- optional:
  - negative_prompt: STRING
  - image_seed: INT default=42 min=0 max=2147483647
  - face_limit: INT default=-1 min=-1 max=20000
  - model_seed: INT default=42 min=0 max=2147483647
  - auto_size: BOOLEAN default=False
  - export_uv: BOOLEAN default=True
  - compress_geometry: BOOLEAN default=False
- outputs: model_file:STRING, model task_id:MODEL_TASK_ID, GLB:FILE_3D_GLB

## TripoPSeriesImageToModelNode
module: comfy_api_nodes.nodes_tripo | category: partner/3d/Tripo
- required:
  - model: COMFY_DYNAMICCOMBO_V3
- outputs: model task_id:MODEL_TASK_ID, GLB:FILE_3D_GLB, FBX:FILE_3D_FBX

## TripoPSeriesMultiviewToModelNode
module: comfy_api_nodes.nodes_tripo | category: partner/3d/Tripo
- required:
  - model: COMFY_DYNAMICCOMBO_V3
- outputs: model task_id:MODEL_TASK_ID, GLB:FILE_3D_GLB, FBX:FILE_3D_FBX

## TripoPSeriesTextToModelNode
module: comfy_api_nodes.nodes_tripo | category: partner/3d/Tripo
- required:
  - model: COMFY_DYNAMICCOMBO_V3
- outputs: model task_id:MODEL_TASK_ID, GLB:FILE_3D_GLB, FBX:FILE_3D_FBX

## TripoRetargetNode
module: comfy_api_nodes.nodes_tripo | category: partner/3d/Tripo
- required:
  - original_model_task_id: RIG_TASK_ID
  - animation: COMBO[preset:idle, preset:walk, preset:run, preset:dive, preset:climb, preset:jump, preset:slash, preset:shoot, preset:hurt, preset:fall, ... +106]
- optional:
  - out_format: COMBO[glb, fbx] default='glb'
  - export_with_geometry: BOOLEAN default=True
  - animate_in_place: BOOLEAN default=False
- outputs: model_file:STRING, retarget task_id:RETARGET_TASK_ID, GLB:FILE_3D_GLB, FBX:FILE_3D_FBX

## TripoRetopologyNode
module: comfy_api_nodes.nodes_tripo | category: partner/3d/Tripo
- required:
  - model_task_id: MODEL_TASK_ID,SEGMENT_TASK_ID
  - face_limit: INT default=-1 min=-1 max=20000
  - quad: BOOLEAN default=False
- optional:
  - bake: BOOLEAN default=True
  - part_names: STRING default=''
- outputs: model_file:STRING, model task_id:MODEL_TASK_ID, GLB:FILE_3D_GLB, FBX:FILE_3D_FBX

## TripoRigCheckNode
module: comfy_api_nodes.nodes_tripo | category: partner/3d/Tripo
- required:
  - model_task_id: MODEL_TASK_ID
- outputs: riggable:BOOLEAN, rig_type:STRING

## TripoRigNode
module: comfy_api_nodes.nodes_tripo | category: partner/3d/Tripo
- required:
  - original_model_task_id: MODEL_TASK_ID
- optional:
  - model_version: COMBO[v1.0-20240301, v2.5-20260210] default='v1.0-20240301'
  - rig_type: COMBO[auto, biped, quadruped, hexapod, octopod, avian, serpentine, aquatic] default='auto'
  - spec: COMBO[mixamo, tripo] default='tripo'
  - out_format: COMBO[glb, fbx] default='glb'
- outputs: model_file:STRING, rig task_id:RIG_TASK_ID, GLB:FILE_3D_GLB, FBX:FILE_3D_FBX

## TripoSegmentNode
module: comfy_api_nodes.nodes_tripo | category: partner/3d/Tripo
- required:
  - model_task_id: MODEL_TASK_ID
- outputs: model_file:STRING, segment task_id:SEGMENT_TASK_ID, GLB:FILE_3D_GLB, part_names:STRING

## TripoSmartSegmentNode
module: comfy_api_nodes.nodes_tripo | category: partner/3d/Tripo
- required:
  - source: COMFY_DYNAMICCOMBO_V3
- outputs: segment task_id:SEGMENT_TASK_ID, model task_id:MODEL_TASK_ID, GLB:FILE_3D_GLB, part_names:STRING, parts:STRING, mask:IMAGE

## TripoSplatConditioning
module: comfy_extras.nodes_triposplat | category: model/conditioning/triposplat
- required:
  - clip_vision: CLIP_VISION
  - vae: VAE
  - image: IMAGE
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## TripoSplatPreprocessImage
module: comfy_extras.nodes_triposplat | category: model/conditioning/triposplat
- required:
  - image: IMAGE
  - mask: MASK
  - erode_radius: INT default=1 min=0 max=16
  - size: INT default=1024 min=256 max=4096 step=16
- outputs: image:IMAGE

## TripoSplatSamplingPreview
module: comfy_extras.nodes_triposplat | category: model/latent/triposplat
- required:
  - model: MODEL
  - vae: VAE
  - octree_level: INT default=5 min=2 max=8
  - num_gaussians: INT default=16384 min=1024 max=262144 step=32
  - yaw: FLOAT default=90.0 min=-360.0 max=360.0 step=1.0
  - pitch: FLOAT default=15.0 min=-89.0 max=89.0 step=1.0
  - point_size: INT default=3 min=1 max=16
- outputs: MODEL:MODEL

## TripoTextToModelNode
module: comfy_api_nodes.nodes_tripo | category: partner/3d/Tripo
- required:
  - prompt: STRING
- optional:
  - negative_prompt: STRING
  - model_version: COMBO[v3.1-20260211, v3.0-20250812, v2.5-20250123] default='v3.1-20260211'
  - style: COMBO[person:person2cartoon, animal:venom, object:clay, object:steampunk, object:christmas, object:barbie, gold, ancient_bronze, None] default='None'
  - texture: BOOLEAN default=True
  - pbr: BOOLEAN default=True
  - image_seed: INT default=42 min=0 max=2147483647
  - model_seed: INT default=42 min=0 max=2147483647
  - texture_seed: INT default=42 min=0 max=2147483647
  - texture_quality: COMBO[standard, detailed, extreme] default='standard'
  - face_limit: INT default=-1 min=-1 max=2000000
  - quad: BOOLEAN default=False
  - geometry_quality: COMBO[standard, detailed] default='standard'
  - smart_low_poly: BOOLEAN default=False
  - auto_size: BOOLEAN default=True
- outputs: model_file:STRING, model task_id:MODEL_TASK_ID, GLB:FILE_3D_GLB, FBX:FILE_3D_FBX

## TripoTextToModelNodeV2
module: comfy_api_nodes.nodes_tripo | category: partner/3d/Tripo
- required:
  - prompt: STRING
- optional:
  - negative_prompt: STRING
  - model_version: COMBO[v3.1-20260211, v3.0-20250812, v2.5-20250123] default='v3.1-20260211'
  - texture: BOOLEAN default=True
  - pbr: BOOLEAN default=True
  - image_seed: INT default=42 min=0 max=2147483647
  - model_seed: INT default=42 min=0 max=2147483647
  - texture_seed: INT default=42 min=0 max=2147483647
  - texture_quality: COMBO[standard, detailed, extreme] default='standard'
  - face_limit: INT default=-1 min=-1 max=2000000
  - quad: BOOLEAN default=False
  - geometry_quality: COMBO[standard, detailed] default='standard'
  - smart_low_poly: BOOLEAN default=False
  - auto_size: BOOLEAN default=True
- outputs: model task_id:MODEL_TASK_ID, GLB:FILE_3D_GLB, FBX:FILE_3D_FBX

## TripoTextureNode
module: comfy_api_nodes.nodes_tripo | category: partner/3d/Tripo
- required:
  - model_task_id: MODEL_TASK_ID,SEGMENT_TASK_ID
- optional:
  - texture: BOOLEAN default=True
  - pbr: BOOLEAN default=True
  - texture_seed: INT default=42 min=0 max=2147483647
  - texture_quality: COMBO[standard, detailed, extreme] default='standard'
  - texture_alignment: COMBO[original_image, geometry] default='original_image'
  - texture_prompt: STRING default=''
  - model_version: COMBO[v3.0-20250812, v2.5-20250123] default='v3.0-20250812'
  - style_image: IMAGE
  - reference: COMFY_DYNAMICCOMBO_V3
  - part_names: STRING default=''
- outputs: model_file:STRING, model task_id:MODEL_TASK_ID, GLB:FILE_3D_GLB, FBX:FILE_3D_FBX

## TripoTextureNodeV2
module: comfy_api_nodes.nodes_tripo | category: partner/3d/Tripo
- required:
  - model_task_id: MODEL_TASK_ID,SEGMENT_TASK_ID
- optional:
  - pbr: BOOLEAN default=True
  - texture_seed: INT default=42 min=0 max=2147483647
  - texture_quality: COMBO[standard, detailed, extreme] default='standard'
  - texture_alignment: COMBO[original_image, geometry] default='original_image'
  - texture_prompt: STRING default=''
  - model_version: COMBO[v3.0-20250812, v2.5-20250123] default='v3.0-20250812'
  - style_image: IMAGE
  - reference: COMFY_DYNAMICCOMBO_V3
  - part_names: STRING default=''
- outputs: model task_id:MODEL_TASK_ID, GLB:FILE_3D_GLB, FBX:FILE_3D_FBX

## TruncateText
module: comfy_extras.nodes_dataset | category: text
- required:
  - texts: STRING
  - max_length: INT default=77 min=1 max=10000
- outputs: texts:STRING

## TTPlanet_TileGF_Preprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/tile
- required:
  - image: IMAGE
- optional:
  - scale_factor: FLOAT default=1.0 min=1.0 max=8.0 step=0.01
  - blur_strength: FLOAT default=2.0 min=1.0 max=10.0 step=0.01
  - radius: INT default=7 min=1 max=20 step=1
  - eps: FLOAT default=0.01 min=0.001 max=0.1 step=0.001
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## TTPlanet_TileSimple_Preprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/tile
- required:
  - image: IMAGE
- optional:
  - scale_factor: FLOAT default=1.0 min=1.0 max=8.0 step=0.01
  - blur_strength: FLOAT default=2.0 min=1.0 max=10.0 step=0.01
- outputs: IMAGE:IMAGE

## UltimateSDUpscale
module: custom_nodes.ComfyUI_UltimateSDUpscale | category: image/upscaling
- required:
  - image: IMAGE
  - model: MODEL
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - upscale_by: FLOAT default=2 min=0.05 max=4 step=0.05
  - seed: INT default=0 min=0 max=18446744073709551615
  - steps: INT default=20 min=1 max=10000 step=1
  - cfg: FLOAT default=8.0 min=0.0 max=100.0
  - sampler_name: COMBO[euler, euler_cfg_pp, euler_ancestral, euler_ancestral_cfg_pp, heun, heunpp2, exp_heun_2_x0, exp_heun_2_x0_sde, dpm_2, dpm_2_ancestral, ... +35]
  - scheduler: COMBO[simple, sgm_uniform, karras, exponential, ddim_uniform, beta, normal, linear_quadratic, kl_optimal]
  - denoise: FLOAT default=0.2 min=0.0 max=1.0 step=0.01
  - upscale_model: UPSCALE_MODEL
  - mode_type: COMBO[Linear, Chess, None]
  - tile_width: INT default=512 min=64 max=8192 step=8
  - tile_height: INT default=512 min=64 max=8192 step=8
  - mask_blur: INT default=8 min=0 max=64 step=1
  - tile_padding: INT default=32 min=0 max=8192 step=8
  - seam_fix_mode: COMBO[None, Band Pass, Half Tile, Half Tile + Intersections]
  - seam_fix_denoise: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - seam_fix_width: INT default=64 min=0 max=8192 step=8
  - seam_fix_mask_blur: INT default=8 min=0 max=64 step=1
  - seam_fix_padding: INT default=16 min=0 max=8192 step=8
  - force_uniform_tiles: BOOLEAN default=True
  - tiled_decode: BOOLEAN default=False
  - batch_size: INT default=1 min=1 max=4096 step=1
- outputs: IMAGE:IMAGE

## UltimateSDUpscaleCustomSample
module: custom_nodes.ComfyUI_UltimateSDUpscale | category: image/upscaling
- required:
  - image: IMAGE
  - model: MODEL
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - upscale_by: FLOAT default=2 min=0.05 max=4 step=0.05
  - seed: INT default=0 min=0 max=18446744073709551615
  - steps: INT default=20 min=1 max=10000 step=1
  - cfg: FLOAT default=8.0 min=0.0 max=100.0
  - sampler_name: COMBO[euler, euler_cfg_pp, euler_ancestral, euler_ancestral_cfg_pp, heun, heunpp2, exp_heun_2_x0, exp_heun_2_x0_sde, dpm_2, dpm_2_ancestral, ... +35]
  - scheduler: COMBO[simple, sgm_uniform, karras, exponential, ddim_uniform, beta, normal, linear_quadratic, kl_optimal]
  - denoise: FLOAT default=0.2 min=0.0 max=1.0 step=0.01
  - mode_type: COMBO[Linear, Chess, None]
  - tile_width: INT default=512 min=64 max=8192 step=8
  - tile_height: INT default=512 min=64 max=8192 step=8
  - mask_blur: INT default=8 min=0 max=64 step=1
  - tile_padding: INT default=32 min=0 max=8192 step=8
  - seam_fix_mode: COMBO[None, Band Pass, Half Tile, Half Tile + Intersections]
  - seam_fix_denoise: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - seam_fix_width: INT default=64 min=0 max=8192 step=8
  - seam_fix_mask_blur: INT default=8 min=0 max=64 step=1
  - seam_fix_padding: INT default=16 min=0 max=8192 step=8
  - force_uniform_tiles: BOOLEAN default=True
  - tiled_decode: BOOLEAN default=False
  - batch_size: INT default=1 min=1 max=4096 step=1
- optional:
  - upscale_model: UPSCALE_MODEL
  - custom_sampler: SAMPLER
  - custom_sigmas: SIGMAS
- outputs: IMAGE:IMAGE

## UltimateSDUpscaleNoUpscale
module: custom_nodes.ComfyUI_UltimateSDUpscale | category: image/upscaling
- required:
  - upscaled_image: IMAGE
  - model: MODEL
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - seed: INT default=0 min=0 max=18446744073709551615
  - steps: INT default=20 min=1 max=10000 step=1
  - cfg: FLOAT default=8.0 min=0.0 max=100.0
  - sampler_name: COMBO[euler, euler_cfg_pp, euler_ancestral, euler_ancestral_cfg_pp, heun, heunpp2, exp_heun_2_x0, exp_heun_2_x0_sde, dpm_2, dpm_2_ancestral, ... +35]
  - scheduler: COMBO[simple, sgm_uniform, karras, exponential, ddim_uniform, beta, normal, linear_quadratic, kl_optimal]
  - denoise: FLOAT default=0.2 min=0.0 max=1.0 step=0.01
  - mode_type: COMBO[Linear, Chess, None]
  - tile_width: INT default=512 min=64 max=8192 step=8
  - tile_height: INT default=512 min=64 max=8192 step=8
  - mask_blur: INT default=8 min=0 max=64 step=1
  - tile_padding: INT default=32 min=0 max=8192 step=8
  - seam_fix_mode: COMBO[None, Band Pass, Half Tile, Half Tile + Intersections]
  - seam_fix_denoise: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - seam_fix_width: INT default=64 min=0 max=8192 step=8
  - seam_fix_mask_blur: INT default=8 min=0 max=64 step=1
  - seam_fix_padding: INT default=16 min=0 max=8192 step=8
  - force_uniform_tiles: BOOLEAN default=True
  - tiled_decode: BOOLEAN default=False
  - batch_size: INT default=1 min=1 max=4096 step=1
- outputs: IMAGE:IMAGE

## unCLIPCheckpointLoader
module: nodes | category: model/loaders
- required:
  - ckpt_name: COMBO[]
- outputs: MODEL:MODEL, CLIP:CLIP, VAE:VAE, CLIP_VISION:CLIP_VISION

## unCLIPConditioning
module: nodes | category: model/conditioning
- required:
  - conditioning: CONDITIONING
  - clip_vision_output: CLIP_VISION_OUTPUT
  - strength: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - noise_augmentation: FLOAT default=0.0 min=0.0 max=1.0 step=0.01
- outputs: CONDITIONING:CONDITIONING

## UNetCrossAttentionMultiply
module: comfy_extras.nodes_attention_multiply | category: experimental/attention_experiments
- required:
  - model: MODEL
  - q: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - k: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - v: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - out: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
- outputs: MODEL:MODEL

## UNETLoader
module: nodes | category: model/loaders
- required:
  - unet_name: COMBO[10Eros_Max_h3_8stepTURBO_beta7_activation_learned_HQ.safetensors, 10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors, FLUX-KLEIN-9B-FP8-NSFW.safetensors, flux-2-klein-9b-kv-fp8.safetensors]
  - weight_dtype: COMBO[default, fp8_e4m3fn, fp8_e4m3fn_fast, fp8_e5m2]
- outputs: MODEL:MODEL

## UnetLoaderGGUF
module: custom_nodes.ComfyUI-GGUF | category: bootleg
- required:
  - unet_name: COMBO[]
- outputs: MODEL:MODEL

## UnetLoaderGGUFAdvanced
module: custom_nodes.ComfyUI-GGUF | category: bootleg
- required:
  - unet_name: COMBO[]
  - dequant_dtype: COMBO[default, target, float32, float16, bfloat16] default='default'
  - patch_dtype: COMBO[default, target, float32, float16, bfloat16] default='default'
  - patch_on_device: BOOLEAN default=False
- outputs: MODEL:MODEL

## UNetSelfAttentionMultiply
module: comfy_extras.nodes_attention_multiply | category: experimental/attention_experiments
- required:
  - model: MODEL
  - q: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - k: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - v: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - out: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
- outputs: MODEL:MODEL

## UNetTemporalAttentionMultiply
module: comfy_extras.nodes_attention_multiply | category: experimental/attention_experiments
- required:
  - model: MODEL
  - self_structural: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - self_temporal: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - cross_structural: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - cross_temporal: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
- outputs: MODEL:MODEL

## UniBlockSwap
module: custom_nodes.ComfyUI_UniBlockSwap | category: model/loaders
- required:
  - model: MODEL
- optional:
  - num_blocks: INT default=-1 min=-1 max=10000 step=1
- outputs: model:MODEL

## UniBlockSwapCacheControl
module: custom_nodes.ComfyUI_UniBlockSwap | category: model/loaders
- required:
  - model: MODEL
- outputs: model:MODEL

## UniBlockSwapTE
module: custom_nodes.ComfyUI_UniBlockSwap | category: model/loaders
- required:
  - clip: CLIP
- optional:
  - num_blocks: INT default=-1 min=-1 max=10000 step=1
- outputs: clip:CLIP

## UniFormer-SemSegPreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Semantic Segmentation
- required:
  - image: IMAGE
- optional:
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## Unimatch_OptFlowPreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Optical Flow
- required:
  - image: IMAGE
  - ckpt_name: COMBO[gmflow-scale1-mixdata.pth, gmflow-scale2-mixdata.pth, gmflow-scale2-regrefine6-mixdata.pth] default='gmflow-scale2-regrefine6-mixdata.pth'
  - backward_flow: BOOLEAN default=False
  - bidirectional_flow: BOOLEAN default=False
- outputs: OPTICAL_FLOW:OPTICAL_FLOW, PREVIEW_IMAGE:IMAGE

## UniversalSwitch
module: custom_nodes.ControlFlowUtils | category: 🐺 VykosX-ControlFlowUtils
- required:
  - input1: *
  - mode: COMBO[SWITCH, PASSTHROUGH, CYCLE, SORT, REVERSE]
  - selection_in: INT default=1 min=-1 max=6 step=1
  - selection_out: INT default=1 min=-1 max=6 step=1
  - validate_typing: BOOLEAN
- optional:
  - input2: *
  - input3: *
  - input4: *
  - input5: *
  - input6: *
- outputs: *:*, *:*, *:*, *:*, *:*, *:*

## UnloadModels
module: custom_nodes.ControlFlowUtils | category: 🐺 VykosX-ControlFlowUtils
- required:
  - Passthrough: *
  - ForceUnload: BOOLEAN default=False
- outputs: Output:*

## UnwrapMesh
module: comfy_extras.nodes_mesh_postprocess | category: 3d/texturing
- required:
  - mesh: MESH
  - segmenter: COMBO[pec, adaptive] default='pec'
  - resolution: INT default=1024 min=0 max=8192 step=256
  - padding: INT default=1 min=0 max=16
  - weld_distance: FLOAT default=0.0 min=0.0 max=1.0 step=0.0001
- outputs: mesh:MESH

## UpperBodyTrackingFromPoseKps
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Pose Keypoint Postprocess
- required:
  - pose_kps: POSE_KEYPOINT
  - id_include: STRING default=''
  - Head_width_height: STRING default='256, 256'
  - Neck_width_height: STRING default='100, 100'
  - Shoulder_width_height: STRING default=''
  - Torso_width_height: STRING default='350, 450'
  - RArm_width_height: STRING default='128, 256'
  - RForearm_width_height: STRING default='128, 256'
  - LArm_width_height: STRING default='128, 256'
  - LForearm_width_height: STRING default='128, 256'
- outputs: tracking:TRACKING, prompt:STRING

## UpscaleModelLoader
module: comfy_extras.nodes_upscale_model | category: model/loaders
- required:
  - model_name: COMBO[4x-UltraSharp.pth, 4x-UltraSharp.safetensors, 4x_foolhardy_Remacri.pth]
- outputs: UPSCALE_MODEL:UPSCALE_MODEL

## USOStyleReference
module: comfy_extras.nodes_model_patch | category: model/patch/flux
- required:
  - model: MODEL
  - model_patch: MODEL_PATCH
  - clip_vision_output: CLIP_VISION_OUTPUT
- outputs: MODEL:MODEL

## VAEDecode
module: nodes | category: model/latent
- required:
  - samples: LATENT
  - vae: VAE
- outputs: IMAGE:IMAGE

## VAEDecodeAudio
module: comfy_extras.nodes_audio | category: model/latent
- required:
  - samples: LATENT
  - vae: VAE
- outputs: AUDIO:AUDIO

## VAEDecodeAudioTiled
module: comfy_extras.nodes_audio | category: model/latent
- required:
  - samples: LATENT
  - vae: VAE
  - tile_size: INT default=512 min=32 max=8192 step=8
  - overlap: INT default=64 min=0 max=1024 step=8
- outputs: AUDIO:AUDIO

## VAEDecodeHunyuan3D
module: comfy_extras.nodes_hunyuan3d | category: model/latent/hunyuan 3d
- required:
  - samples: LATENT
  - vae: VAE
  - num_chunks: INT default=8000 min=1000 max=500000
  - octree_resolution: INT default=256 min=16 max=512
- outputs: VOXEL:VOXEL

## VAEDecodeLoopKJ
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/vae
- required:
  - samples: LATENT
  - vae: VAE
  - overlap_latent_frames: INT default=2 min=2 max=8 step=1
- outputs: IMAGE:IMAGE

## VaeDecodeShapeTrellis
module: comfy_extras.nodes_trellis2 | category: model/latent/trellis
- required:
  - samples: LATENT
  - vae: VAE
- outputs: mesh:MESH, shape_subdivides:SHAPE_SUBDIVIDES

## VaeDecodeStructureTrellis2
module: comfy_extras.nodes_trellis2 | category: model/latent/trellis
- required:
  - samples: LATENT
  - vae: VAE
  - resolution: COMBO[32, 64] default='32'
- outputs: voxel:VOXEL

## VaeDecodeTextureTrellis
module: comfy_extras.nodes_trellis2 | category: model/latent/trellis
- required:
  - samples: LATENT
  - vae: VAE
  - shape_subdivides: SHAPE_SUBDIVIDES
- outputs: voxel_colors:VOXEL

## VAEDecodeTiled
module: nodes | category: model/latent
- required:
  - samples: LATENT
  - vae: VAE
  - tile_size: INT default=512 min=64 max=4096 step=32
  - overlap: INT default=64 min=0 max=4096 step=32
  - temporal_size: INT default=64 min=8 max=4096 step=4
  - temporal_overlap: INT default=8 min=4 max=4096 step=4
- outputs: IMAGE:IMAGE

## VAEDecodeTripoSplat
module: comfy_extras.nodes_triposplat | category: model/latent/triposplat
- required:
  - samples: LATENT
  - vae: VAE
  - num_gaussians: INT default=262144 min=32768 max=1048576 step=32
  - seed: INT default=0 min=0 max=18446744073709551615
- outputs: splat:SPLAT

## VAEEncode
module: nodes | category: model/latent
- required:
  - pixels: IMAGE
  - vae: VAE
- outputs: LATENT:LATENT

## VAEEncodeAudio
module: comfy_extras.nodes_audio | category: model/latent
- required:
  - audio: AUDIO
  - vae: VAE
- outputs: LATENT:LATENT

## VAEEncodeForInpaint
module: nodes | category: model/latent
- required:
  - pixels: IMAGE
  - vae: VAE
  - mask: MASK
  - grow_mask_by: INT default=6 min=0 max=64 step=1
- outputs: LATENT:LATENT

## VAEEncodeTiled
module: nodes | category: model/latent
- required:
  - pixels: IMAGE
  - vae: VAE
  - tile_size: INT default=512 min=64 max=4096 step=64
  - overlap: INT default=64 min=0 max=4096 step=32
  - temporal_size: INT default=64 min=8 max=4096 step=4
  - temporal_overlap: INT default=8 min=4 max=4096 step=4
- outputs: LATENT:LATENT

## VAELoader
module: nodes | category: model/loaders
- required:
  - vae_name: COMBO[flux2-vae-128ch.safetensors, flux2-vae.FAKE_FLUX1_AE.safetensors, flux2-vae.safetensors, lumina2_vae_fp32.safetensors, minimax_h3_audio_vae_fp32.safetensors, minimax_h3_video_vae_int8_convrot.safetensors, sdxl_vae.safetensors, taeh3.safetensors, pixel_space]
- outputs: VAE:VAE

## VAELoaderKJ
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/vae
- required:
  - vae_name: COMBO[flux2-vae-128ch.safetensors, flux2-vae.FAKE_FLUX1_AE.safetensors, flux2-vae.safetensors, lumina2_vae_fp32.safetensors, minimax_h3_audio_vae_fp32.safetensors, minimax_h3_video_vae_int8_convrot.safetensors, sdxl_vae.safetensors, pixel_space]
  - device: COMBO[main_device, cpu]
  - weight_dtype: COMBO[bf16, fp16, fp32]
- outputs: VAE:VAE

## VAEMergeKJ
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/vae
- required:
  - vae_1: VAE
  - vae_2: VAE
  - ratio: FLOAT default=0.5 min=0.0 max=1.0 step=0.01
- outputs: vae:VAE

## VAESave
module: comfy_extras.nodes_model_merging | category: model/merging
- required:
  - vae: VAE
  - filename_prefix: STRING default='vae/ComfyUI_vae'
- outputs: 

## VAESelector
module: custom_nodes.ControlFlowUtils | category: 🐺 VykosX-ControlFlowUtils
- required:
  - vae: COMBO[flux2-vae-128ch.safetensors, flux2-vae.FAKE_FLUX1_AE.safetensors, flux2-vae.safetensors, lumina2_vae_fp32.safetensors, minimax_h3_audio_vae_fp32.safetensors, minimax_h3_video_vae_int8_convrot.safetensors, sdxl_vae.safetensors, taesd, taesdxl]
- optional:
  - run_after: * default=''
- outputs: VAE Name:*

## Veo3FirstLastFrameNode
module: comfy_api_nodes.nodes_veo2 | category: partner/video/Veo
- required:
  - prompt: STRING default=''
  - negative_prompt: STRING default=''
  - resolution: COMBO[720p, 1080p, 4k]
  - aspect_ratio: COMBO[16:9, 9:16] default='16:9'
  - duration: INT default=8 min=4 max=8 step=2
  - seed: INT default=0 min=0 max=4294967295 step=1
  - first_frame: IMAGE
  - last_frame: IMAGE
  - model: COMBO[veo-3.1-generate, veo-3.1-fast-generate, veo-3.1-lite]
  - generate_audio: BOOLEAN default=True
- outputs: VIDEO:VIDEO

## Veo3VideoGenerationNode
module: comfy_api_nodes.nodes_veo2 | category: partner/video/Veo
- required:
  - prompt: STRING default=''
  - aspect_ratio: COMBO[16:9, 9:16] default='16:9'
- optional:
  - resolution: COMBO[720p, 1080p, 4k] default='720p'
  - negative_prompt: STRING default=''
  - duration_seconds: INT default=8 min=4 max=8 step=2
  - enhance_prompt: BOOLEAN default=True
  - person_generation: COMBO[ALLOW, BLOCK] default='ALLOW'
  - seed: INT default=0 min=0 max=4294967295 step=1
  - image: IMAGE
  - model: COMBO[veo-3.1-generate, veo-3.1-fast-generate, veo-3.1-lite]
  - generate_audio: BOOLEAN default=False
- outputs: VIDEO:VIDEO

## VHS_AudioToVHSAudio
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢/audio
- required:
  - audio: AUDIO
- outputs: vhs_audio:VHS_AUDIO

## VHS_BatchManager
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢
- required:
  - frames_per_batch: INT default=16 min=1 max=9007199254740991 step=1
- outputs: meta_batch:VHS_BatchManager

## VHS_DuplicateImages
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢/image
- required:
  - images: IMAGE
  - multiply_by: INT default=1 min=1 max=9007199254740991 step=1
- outputs: IMAGE:IMAGE, count:INT

## VHS_DuplicateLatents
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢/latent
- required:
  - latents: LATENT
  - multiply_by: INT default=1 min=1 max=9007199254740991 step=1
- outputs: LATENT:LATENT, count:INT

## VHS_DuplicateMasks
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢/mask
- required:
  - mask: MASK
  - multiply_by: INT default=1 min=1 max=9007199254740991 step=1
- outputs: MASK:MASK, count:INT

## VHS_GetImageCount
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢/image
- required:
  - images: IMAGE
- outputs: count:INT

## VHS_GetLatentCount
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢/latent
- required:
  - latents: LATENT
- outputs: count:INT

## VHS_GetMaskCount
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢/mask
- required:
  - mask: MASK
- outputs: count:INT

## VHS_LoadAudio
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢/audio
- required:
  - audio_file: STRING default='input/'
- optional:
  - seek_seconds: FLOAT default=0 min=0
  - duration: FLOAT default=0 min=0 max=10000000 step=0.01
- outputs: audio:AUDIO, duration:FLOAT

## VHS_LoadAudioUpload
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢/audio
- required:
  - audio: COMBO[5slock_ext_SB1r3.mp4, 5slock_lcv_SB1r3_24fps.mp4, MAX5S_ORC_B0_ST6_1344x768_noRIFE_s2015873178_00001_.mp4, MAXOPT_R3b_full_simple_sA_s43029049_00001_.mp4, MAXOPT_R3b_sA_tail2s_for_hop.mp4, MAX_1MIN_T0_PRIOR.mp4, MAX_REF_ORC_BJ_OPT_SCH_WARM_BETA_s25102401_00001_.mp4, c04_cell1_native.mp4, c04_cell1_tail22.mp4, c04_cell2_native.mp4, ... +66]
- optional:
  - start_time: FLOAT default=0 min=0 max=10000000 step=0.01
  - duration: FLOAT default=0 min=0 max=10000000 step=0.01
- outputs: audio:AUDIO, duration:FLOAT

## VHS_LoadImagePath
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢
- required:
  - image: STRING
  - custom_width: INT default=0 min=0 max=8192 step=8
  - custom_height: INT default=0 min=0 max=8192 step=8
- optional:
  - vae: VAE
- outputs: IMAGE:IMAGE, mask:MASK

## VHS_LoadImages
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢
- required:
  - directory: COMBO[3d, community, joyecho_prompts, max_fair_cond, reference_images, rift_prompts]
- optional:
  - image_load_cap: INT default=0 min=0 max=9007199254740991 step=1
  - skip_first_images: INT default=0 min=0 max=9007199254740991 step=1
  - select_every_nth: INT default=1 min=1 max=9007199254740991 step=1
  - meta_batch: VHS_BatchManager
- outputs: IMAGE:IMAGE, MASK:MASK, frame_count:INT

## VHS_LoadImagesPath
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢
- required:
  - directory: STRING
- optional:
  - image_load_cap: INT default=0 min=0 max=9007199254740991 step=1
  - skip_first_images: INT default=0 min=0 max=9007199254740991 step=1
  - select_every_nth: INT default=1 min=1 max=9007199254740991 step=1
  - meta_batch: VHS_BatchManager
- outputs: IMAGE:IMAGE, MASK:MASK, frame_count:INT

## VHS_LoadVideo
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢
- required:
  - video: COMBO[5slock_ext_SB1r3.mp4, 5slock_lcv_SB1r3_24fps.mp4, MAX5S_ORC_B0_ST6_1344x768_noRIFE_s2015873178_00001_.mp4, MAXOPT_R3b_full_simple_sA_s43029049_00001_.mp4, MAXOPT_R3b_sA_tail2s_for_hop.mp4, MAX_1MIN_T0_PRIOR.mp4, MAX_REF_ORC_BJ_OPT_SCH_WARM_BETA_s25102401_00001_.mp4, c04_cell1_native.mp4, c04_cell1_tail22.mp4, c04_cell2_native.mp4, ... +66]
  - force_rate: FLOAT default=0 min=0 max=60 step=1
  - custom_width: INT default=0 min=0 max=8192
  - custom_height: INT default=0 min=0 max=8192
  - frame_load_cap: INT default=0 min=0 max=9007199254740991 step=1
  - skip_first_frames: INT default=0 min=0 max=9007199254740991 step=1
  - select_every_nth: INT default=1 min=1 max=9007199254740991 step=1
- optional:
  - meta_batch: VHS_BatchManager
  - vae: VAE
  - format: COMBO[None, AnimateDiff, Mochi, LTXV, Hunyuan, Cosmos, Wan] default='AnimateDiff'
- outputs: IMAGE:IMAGE, frame_count:INT, audio:AUDIO, video_info:VHS_VIDEOINFO

## VHS_LoadVideoFFmpeg
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢
- required:
  - video: COMBO[5slock_ext_SB1r3.mp4, 5slock_lcv_SB1r3_24fps.mp4, MAX5S_ORC_B0_ST6_1344x768_noRIFE_s2015873178_00001_.mp4, MAXOPT_R3b_full_simple_sA_s43029049_00001_.mp4, MAXOPT_R3b_sA_tail2s_for_hop.mp4, MAX_1MIN_T0_PRIOR.mp4, MAX_REF_ORC_BJ_OPT_SCH_WARM_BETA_s25102401_00001_.mp4, c04_cell1_native.mp4, c04_cell1_tail22.mp4, c04_cell2_native.mp4, ... +66]
  - force_rate: FLOAT default=0 min=0 max=60 step=1
  - custom_width: INT default=0 min=0 max=8192
  - custom_height: INT default=0 min=0 max=8192
  - frame_load_cap: INT default=0 min=0 max=9007199254740991 step=1
  - start_time: FLOAT default=0 min=0 max=9007199254740991 step=0.001
- optional:
  - meta_batch: VHS_BatchManager
  - vae: VAE
  - format: COMBO[None, AnimateDiff, Mochi, LTXV, Hunyuan, Cosmos, Wan] default='AnimateDiff'
- outputs: IMAGE:IMAGE, mask:MASK, audio:AUDIO, video_info:VHS_VIDEOINFO

## VHS_LoadVideoFFmpegPath
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢
- required:
  - video: STRING
  - force_rate: FLOAT default=0 min=0 max=60 step=1
  - custom_width: INT default=0 min=0 max=8192
  - custom_height: INT default=0 min=0 max=8192
  - frame_load_cap: INT default=0 min=0 max=9007199254740991 step=1
  - start_time: FLOAT default=0 min=0 max=9007199254740991 step=0.001
- optional:
  - meta_batch: VHS_BatchManager
  - vae: VAE
  - format: COMBO[None, AnimateDiff, Mochi, LTXV, Hunyuan, Cosmos, Wan] default='AnimateDiff'
- outputs: IMAGE:IMAGE, mask:MASK, audio:AUDIO, video_info:VHS_VIDEOINFO

## VHS_LoadVideoPath
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢
- required:
  - video: STRING
  - force_rate: FLOAT default=0 min=0 max=60 step=1
  - custom_width: INT default=0 min=0 max=8192
  - custom_height: INT default=0 min=0 max=8192
  - frame_load_cap: INT default=0 min=0 max=9007199254740991 step=1
  - skip_first_frames: INT default=0 min=0 max=9007199254740991 step=1
  - select_every_nth: INT default=1 min=1 max=9007199254740991 step=1
- optional:
  - meta_batch: VHS_BatchManager
  - vae: VAE
  - format: COMBO[None, AnimateDiff, Mochi, LTXV, Hunyuan, Cosmos, Wan] default='AnimateDiff'
- outputs: IMAGE:IMAGE, frame_count:INT, audio:AUDIO, video_info:VHS_VIDEOINFO

## VHS_MergeImages
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢/image
- required:
  - images_A: IMAGE
  - images_B: IMAGE
  - merge_strategy: COMBO[match A, match B, match smaller, match larger]
  - scale_method: COMBO[nearest-exact, bilinear, area, bicubic, bislerp]
  - crop: COMBO[disabled, center]
- outputs: IMAGE:IMAGE, count:INT

## VHS_MergeLatents
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢/latent
- required:
  - latents_A: LATENT
  - latents_B: LATENT
  - merge_strategy: COMBO[match A, match B, match smaller, match larger]
  - scale_method: COMBO[nearest-exact, bilinear, area, bicubic, bislerp]
  - crop: COMBO[disabled, center]
- outputs: LATENT:LATENT, count:INT

## VHS_MergeMasks
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢/mask
- required:
  - mask_A: MASK
  - mask_B: MASK
  - merge_strategy: COMBO[match A, match B, match smaller, match larger]
  - scale_method: COMBO[nearest-exact, bilinear, area, bicubic, bislerp]
  - crop: COMBO[disabled, center]
- outputs: MASK:MASK, count:INT

## VHS_PruneOutputs
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢
- required:
  - filenames: VHS_FILENAMES
  - options: COMBO[Intermediate, Intermediate and Utility]
- outputs: 

## VHS_SelectEveryNthImage
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢/image
- required:
  - images: IMAGE
  - select_every_nth: INT default=1 min=1 max=9007199254740991 step=1
  - skip_first_images: INT default=0 min=0 max=9007199254740991 step=1
- outputs: IMAGE:IMAGE, count:INT

## VHS_SelectEveryNthLatent
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢/latent
- required:
  - latents: LATENT
  - select_every_nth: INT default=1 min=1 max=9007199254740991 step=1
  - skip_first_latents: INT default=0 min=0 max=9007199254740991 step=1
- outputs: LATENT:LATENT, count:INT

## VHS_SelectEveryNthMask
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢/mask
- required:
  - mask: MASK
  - select_every_nth: INT default=1 min=1 max=9007199254740991 step=1
  - skip_first_masks: INT default=0 min=0 max=9007199254740991 step=1
- outputs: MASK:MASK, count:INT

## VHS_SelectFilename
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢
- required:
  - filenames: VHS_FILENAMES
  - index: INT default=-1 min=-1 step=1
- outputs: Filename:STRING

## VHS_SelectImages
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢/image
- required:
  - image: IMAGE
  - indexes: STRING default='0'
  - err_if_missing: BOOLEAN default=True
  - err_if_empty: BOOLEAN default=True
- outputs: IMAGE:IMAGE

## VHS_SelectLatents
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢/latent
- required:
  - latent: LATENT
  - indexes: STRING default='0'
  - err_if_missing: BOOLEAN default=True
  - err_if_empty: BOOLEAN default=True
- outputs: LATENT:LATENT

## VHS_SelectLatest
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢
- required:
  - filename_prefix: STRING default='output/AnimateDiff'
  - filename_postfix: STRING
- outputs: Filename:STRING

## VHS_SelectMasks
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢/mask
- required:
  - mask: MASK
  - indexes: STRING default='0'
  - err_if_missing: BOOLEAN default=True
  - err_if_empty: BOOLEAN default=True
- outputs: MASK:MASK

## VHS_SplitImages
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢/image
- required:
  - images: IMAGE
  - split_index: INT default=0 min=-9007199254740991 max=9007199254740991 step=1
- outputs: IMAGE_A:IMAGE, A_count:INT, IMAGE_B:IMAGE, B_count:INT

## VHS_SplitLatents
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢/latent
- required:
  - latents: LATENT
  - split_index: INT default=0 min=-9007199254740991 max=9007199254740991 step=1
- outputs: LATENT_A:LATENT, A_count:INT, LATENT_B:LATENT, B_count:INT

## VHS_SplitMasks
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢/mask
- required:
  - mask: MASK
  - split_index: INT default=0 min=-9007199254740991 max=9007199254740991 step=1
- outputs: MASK_A:MASK, A_count:INT, MASK_B:MASK, B_count:INT

## VHS_Unbatch
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢
- required:
  - batched: *
- outputs: unbatched:*

## VHS_VAEDecodeBatched
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢/batched nodes
- required:
  - samples: LATENT
  - vae: VAE
  - per_batch: INT default=16 min=1
- outputs: IMAGE:IMAGE

## VHS_VAEEncodeBatched
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢/batched nodes
- required:
  - pixels: IMAGE
  - vae: VAE
  - per_batch: INT default=16 min=1
- outputs: LATENT:LATENT

## VHS_VHSAudioToAudio
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢/audio
- required:
  - vhs_audio: VHS_AUDIO
- outputs: audio:AUDIO

## VHS_VideoCombine
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢
- required:
  - images: IMAGE
  - frame_rate: FLOAT default=8 min=1 step=1
  - loop_count: INT default=0 min=0 max=100 step=1
  - filename_prefix: STRING default='AnimateDiff'
  - format: COMBO[image/gif, image/webp, video/16bit-png, video/8bit-png, video/av1-webm, video/ffmpeg-gif, video/ffv1-mkv, video/h264-mp4, video/h265-mp4, video/nvenc_av1-mp4, ... +4]
  - pingpong: BOOLEAN default=False
  - save_output: BOOLEAN default=True
- optional:
  - audio: AUDIO
  - meta_batch: VHS_BatchManager
  - vae: VAE
- outputs: Filenames:VHS_FILENAMES

## VHS_VideoInfo
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢
- required:
  - video_info: VHS_VIDEOINFO
- outputs: source_fps🟨:FLOAT, source_frame_count🟨:INT, source_duration🟨:FLOAT, source_width🟨:INT, source_height🟨:INT, loaded_fps🟦:FLOAT, loaded_frame_count🟦:INT, loaded_duration🟦:FLOAT, loaded_width🟦:INT, loaded_height🟦:INT

## VHS_VideoInfoLoaded
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢
- required:
  - video_info: VHS_VIDEOINFO
- outputs: fps🟦:FLOAT, frame_count🟦:INT, duration🟦:FLOAT, width🟦:INT, height🟦:INT

## VHS_VideoInfoSource
module: custom_nodes.ComfyUI-VideoHelperSuite | category: Video Helper Suite 🎥🅥🅗🅢
- required:
  - video_info: VHS_VIDEOINFO
- outputs: fps🟨:FLOAT, frame_count🟨:INT, duration🟨:FLOAT, width🟨:INT, height🟨:INT

## Video Slice
module: comfy_extras.nodes_video | category: video
- required:
  - video: VIDEO
  - start_time: FLOAT default=0.0 min=-100000.0 max=100000.0 step=0.001
  - duration: FLOAT default=0.0 min=0.0 step=0.001
  - strict_duration: BOOLEAN default=False
- outputs: VIDEO:VIDEO

## VideoCrop
module: comfy_extras.nodes_video | category: video
- required:
  - video: VIDEO
  - crop: VIDEO_EDIT default={'crop': {'x': 0, 'y': 0, 'width': 0, 'height': 0}}
- outputs: VIDEO:VIDEO

## VideoFrameSample
module: comfy_extras.nodes_dataset | category: video
- required:
  - video: VIDEO
  - num_frames: INT default=16 min=1 max=9999
  - strategy: COMBO[uniform, head, tail, random] default='uniform'
  - seed: INT default=0 min=0 max=18446744073709551615
- outputs: video:VIDEO

## VideoLinearCFGGuidance
module: comfy_extras.nodes_video_model | category: model/sampling/guiders
- required:
  - model: MODEL
  - min_cfg: FLOAT default=1.0 min=0.0 max=100.0 step=0.5
- outputs: MODEL:MODEL

## VideoRandomTemporalCrop
module: comfy_extras.nodes_dataset | category: video/transform
- required:
  - video: VIDEO
  - length: INT default=16 min=1 max=99999
  - seed: INT default=0 min=0 max=18446744073709551615
- outputs: video:VIDEO

## VideoTemporalCrop
module: comfy_extras.nodes_dataset | category: video/transform
- required:
  - video: VIDEO
  - start_frame: INT default=0 min=0 max=99999
  - length: INT default=16 min=1 max=99999
- outputs: video:VIDEO

## VideoTriangleCFGGuidance
module: comfy_extras.nodes_video_model | category: model/sampling/guiders
- required:
  - model: MODEL
  - min_cfg: FLOAT default=1.0 min=0.0 max=100.0 step=0.5
- outputs: MODEL:MODEL

## VideoTrim
module: comfy_extras.nodes_video | category: video
- required:
  - video: VIDEO
  - trim: VIDEO_EDIT default={'trim': {'start_time': 0.0, 'duration': 0.0}}
  - strict_duration: BOOLEAN default=False
- outputs: VIDEO:VIDEO

## Vidu2ImageToVideoNode
module: comfy_api_nodes.nodes_vidu | category: partner/video/Vidu
- required:
  - model: COMBO[viduq2-pro-fast, viduq2-pro, viduq2-turbo]
  - image: IMAGE
  - prompt: STRING default=''
  - duration: INT default=5 min=1 max=10 step=1
  - seed: INT default=1 min=0 max=2147483647 step=1
  - resolution: COMBO[720p, 1080p]
  - movement_amplitude: COMBO[auto, small, medium, large]
- outputs: VIDEO:VIDEO

## Vidu2ReferenceVideoNode
module: comfy_api_nodes.nodes_vidu | category: partner/video/Vidu
- required:
  - model: COMBO[viduq2]
  - subjects: COMFY_AUTOGROW_V3
  - prompt: STRING
  - audio: BOOLEAN default=False
  - duration: INT default=5 min=1 max=10 step=1
  - seed: INT default=1 min=0 max=2147483647 step=1
  - aspect_ratio: COMBO[16:9, 9:16, 4:3, 3:4, 1:1]
  - resolution: COMBO[720p, 1080p]
  - movement_amplitude: COMBO[auto, small, medium, large]
- outputs: VIDEO:VIDEO

## Vidu2StartEndToVideoNode
module: comfy_api_nodes.nodes_vidu | category: partner/video/Vidu
- required:
  - model: COMBO[viduq2-pro-fast, viduq2-pro, viduq2-turbo]
  - first_frame: IMAGE
  - end_frame: IMAGE
  - prompt: STRING
  - duration: INT default=5 min=2 max=8 step=1
  - seed: INT default=1 min=0 max=2147483647 step=1
  - resolution: COMBO[720p, 1080p]
  - movement_amplitude: COMBO[auto, small, medium, large]
- outputs: VIDEO:VIDEO

## Vidu2TextToVideoNode
module: comfy_api_nodes.nodes_vidu | category: partner/video/Vidu
- required:
  - model: COMBO[viduq2]
  - prompt: STRING
  - duration: INT default=5 min=1 max=10 step=1
  - seed: INT default=1 min=0 max=2147483647 step=1
  - aspect_ratio: COMBO[16:9, 9:16, 3:4, 4:3, 1:1]
  - resolution: COMBO[720p, 1080p]
  - background_music: BOOLEAN default=False
- outputs: VIDEO:VIDEO

## Vidu3ImageToVideoNode
module: comfy_api_nodes.nodes_vidu | category: partner/video/Vidu
- required:
  - model: COMFY_DYNAMICCOMBO_V3
  - image: IMAGE
  - prompt: STRING default=''
  - seed: INT default=1 min=0 max=2147483647 step=1
- outputs: VIDEO:VIDEO

## Vidu3StartEndToVideoNode
module: comfy_api_nodes.nodes_vidu | category: partner/video/Vidu
- required:
  - model: COMFY_DYNAMICCOMBO_V3
  - first_frame: IMAGE
  - end_frame: IMAGE
  - prompt: STRING
  - seed: INT default=1 min=0 max=2147483647 step=1
- outputs: VIDEO:VIDEO

## Vidu3TextToVideoNode
module: comfy_api_nodes.nodes_vidu | category: partner/video/Vidu
- required:
  - model: COMFY_DYNAMICCOMBO_V3
  - prompt: STRING
  - seed: INT default=1 min=0 max=2147483647 step=1
- outputs: VIDEO:VIDEO

## ViduExtendVideoNode
module: comfy_api_nodes.nodes_vidu | category: partner/video/Vidu
- required:
  - model: COMFY_DYNAMICCOMBO_V3
  - video: VIDEO
  - prompt: STRING default=''
  - seed: INT default=1 min=0 max=2147483647 step=1
- optional:
  - end_frame: IMAGE
- outputs: VIDEO:VIDEO

## ViduImageToVideoNode
module: comfy_api_nodes.nodes_vidu | category: partner/video/Vidu
- required:
  - model: COMBO[viduq1]
  - image: IMAGE
- optional:
  - prompt: STRING default=''
  - duration: INT default=5 min=5 max=5 step=1
  - seed: INT default=0 min=0 max=2147483647 step=1
  - resolution: COMBO[1080p]
  - movement_amplitude: COMBO[auto, small, medium, large]
- outputs: VIDEO:VIDEO

## ViduMultiFrameVideoNode
module: comfy_api_nodes.nodes_vidu | category: partner/video/Vidu
- required:
  - model: COMBO[viduq2-pro, viduq2-turbo]
  - start_image: IMAGE
  - seed: INT default=1 min=0 max=2147483647 step=1
  - resolution: COMBO[720p, 1080p]
  - frames: COMFY_DYNAMICCOMBO_V3
- outputs: VIDEO:VIDEO

## ViduReferenceVideoNode
module: comfy_api_nodes.nodes_vidu | category: partner/video/Vidu
- required:
  - model: COMBO[viduq1]
  - images: IMAGE
  - prompt: STRING
- optional:
  - duration: INT default=5 min=5 max=5 step=1
  - seed: INT default=0 min=0 max=2147483647 step=1
  - aspect_ratio: COMBO[16:9, 9:16, 1:1]
  - resolution: COMBO[1080p]
  - movement_amplitude: COMBO[auto, small, medium, large]
- outputs: VIDEO:VIDEO

## ViduStartEndToVideoNode
module: comfy_api_nodes.nodes_vidu | category: partner/video/Vidu
- required:
  - model: COMBO[viduq1]
  - first_frame: IMAGE
  - end_frame: IMAGE
- optional:
  - prompt: STRING
  - duration: INT default=5 min=5 max=5 step=1
  - seed: INT default=0 min=0 max=2147483647 step=1
  - resolution: COMBO[1080p]
  - movement_amplitude: COMBO[auto, small, medium, large]
- outputs: VIDEO:VIDEO

## ViduTextToVideoNode
module: comfy_api_nodes.nodes_vidu | category: partner/video/Vidu
- required:
  - model: COMBO[viduq1]
  - prompt: STRING
- optional:
  - duration: INT default=5 min=5 max=5 step=1
  - seed: INT default=0 min=0 max=2147483647 step=1
  - aspect_ratio: COMBO[16:9, 9:16, 1:1]
  - resolution: COMBO[1080p]
  - movement_amplitude: COMBO[auto, small, medium, large]
- outputs: VIDEO:VIDEO

## VisualizeCUDAMemoryHistory
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/memory
- required:
  - snapshot_path: STRING
- outputs: output_path:STRING

## VisualizeSigmasKJ
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/misc
- required:
  - sigmas: SIGMAS
  - start_step: INT default=0 min=-1 max=1000 step=1
  - end_step: INT default=-1 min=-1 max=1000 step=1
- outputs: sigmas_out:SIGMAS, image:IMAGE

## VOIDInpaintConditioning
module: comfy_extras.nodes_void | category: model/conditioning/void
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - video: IMAGE
  - quadmask: MASK
  - width: INT default=672 min=16 max=16384 step=8
  - height: INT default=384 min=16 max=16384 step=8
  - length: INT default=45 min=1 max=16384 step=1
  - batch_size: INT default=1 min=1 max=64
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## VOIDQuadmaskPreprocess
module: comfy_extras.nodes_void | category: image/mask
- required:
  - mask: MASK
  - dilate_width: INT default=0 min=0 max=50 step=1
- outputs: quadmask:MASK

## VOIDSampler
module: comfy_extras.nodes_void | category: model/sampling/samplers
- outputs: SAMPLER:SAMPLER

## VOIDWarpedNoise
module: comfy_extras.nodes_void | category: model/latent/void
- required:
  - optical_flow: OPTICAL_FLOW
  - video: IMAGE
  - width: INT default=672 min=16 max=16384 step=8
  - height: INT default=384 min=16 max=16384 step=8
  - length: INT default=45 min=1 max=16384 step=1
  - batch_size: INT default=1 min=1 max=64
- outputs: warped_noise:LATENT

## VOIDWarpedNoiseSource
module: comfy_extras.nodes_void | category: model/latent/void
- required:
  - warped_noise: LATENT
- outputs: NOISE:NOISE

## VoxelToMesh
module: comfy_extras.nodes_hunyuan3d | category: 3d
- required:
  - voxel: VOXEL
  - algorithm: COMBO[surface net, basic]
  - threshold: FLOAT default=0.6 min=-1.0 max=1.0 step=0.01
- outputs: MESH:MESH

## VoxelToMeshBasic
module: comfy_extras.nodes_hunyuan3d | category: 3d
- required:
  - voxel: VOXEL
  - threshold: FLOAT default=0.6 min=-1.0 max=1.0 step=0.01
- outputs: MESH:MESH

## VPScheduler
module: comfy_extras.nodes_custom_sampler | category: model/sampling/schedulers
- required:
  - steps: INT default=20 min=1 max=10000
  - beta_d: FLOAT default=19.9 min=0.0 max=5000.0 step=0.01
  - beta_min: FLOAT default=0.1 min=0.0 max=5000.0 step=0.01
  - eps_s: FLOAT default=0.001 min=0.0 max=1.0 step=0.0001
- outputs: SIGMAS:SIGMAS

## VRAM_Debug
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/memory
- required:
  - empty_cache: BOOLEAN default=True
  - gc_collect: BOOLEAN default=True
  - unload_all_models: BOOLEAN default=False
- optional:
  - any_input: *
  - image_pass: IMAGE
  - model_pass: MODEL
- outputs: any_output:*, image_pass:IMAGE, model_pass:MODEL, freemem_before:INT, freemem_after:INT

## Wait
module: custom_nodes.ControlFlowUtils | category: 🐺 VykosX-ControlFlowUtils
- required:
  - Delay: FLOAT default=5.0
- optional:
  - Input: *
- outputs: Output:*

## Wan21BlockLoraSelect
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/wan
- required:
  - blocks.0.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.1.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.2.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.3.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.4.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.5.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.6.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.7.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.8.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.9.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.10.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.11.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.12.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.13.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.14.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.15.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.16.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.17.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.18.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.19.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.20.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.21.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.22.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.23.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.24.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.25.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.26.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.27.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.28.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.29.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.30.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.31.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.32.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.33.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.34.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.35.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.36.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.37.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.38.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
  - blocks.39.: FLOAT default=0.0 min=0.0 max=1000.0 step=0.01
- outputs: blocks:SELECTEDDITBLOCKS

## Wan22FunControlToVideo
module: comfy_extras.nodes_wan | category: model/conditioning/wan/fun control
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - width: INT default=832 min=16 max=16384 step=16
  - height: INT default=480 min=16 max=16384 step=16
  - length: INT default=81 min=1 max=16384 step=4
  - batch_size: INT default=1 min=1 max=4096
- optional:
  - ref_image: IMAGE
  - control_video: IMAGE
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## Wan22ImageToVideoLatent
module: comfy_extras.nodes_wan | category: model/conditioning/wan
- required:
  - vae: VAE
  - width: INT default=1280 min=32 max=16384 step=32
  - height: INT default=704 min=32 max=16384 step=32
  - length: INT default=49 min=1 max=16384 step=4
  - batch_size: INT default=1 min=1 max=4096
- optional:
  - start_image: IMAGE
- outputs: LATENT:LATENT

## Wan2ImageToVideoApi
module: comfy_api_nodes.nodes_wan | category: partner/video/Wan
- required:
  - model: COMFY_DYNAMICCOMBO_V3
  - first_frame: IMAGE
  - seed: INT default=0 min=0 max=2147483647 step=1
  - prompt_extend: BOOLEAN default=True
  - watermark: BOOLEAN default=False
- optional:
  - last_frame: IMAGE
  - audio: AUDIO
- outputs: VIDEO:VIDEO

## Wan2ReferenceVideoApi
module: comfy_api_nodes.nodes_wan | category: partner/video/Wan
- required:
  - model: COMFY_DYNAMICCOMBO_V3
  - seed: INT default=0 min=0 max=2147483647 step=1
  - watermark: BOOLEAN default=False
- outputs: VIDEO:VIDEO

## Wan2TextToVideoApi
module: comfy_api_nodes.nodes_wan | category: partner/video/Wan
- required:
  - model: COMFY_DYNAMICCOMBO_V3
  - seed: INT default=0 min=0 max=2147483647 step=1
  - prompt_extend: BOOLEAN default=True
  - watermark: BOOLEAN default=False
- optional:
  - audio: AUDIO
- outputs: VIDEO:VIDEO

## Wan2VideoContinuationApi
module: comfy_api_nodes.nodes_wan | category: partner/video/Wan
- required:
  - model: COMFY_DYNAMICCOMBO_V3
  - first_clip: VIDEO
  - seed: INT default=0 min=0 max=2147483647 step=1
  - prompt_extend: BOOLEAN default=True
  - watermark: BOOLEAN default=False
- optional:
  - last_frame: IMAGE
- outputs: VIDEO:VIDEO

## Wan2VideoEditApi
module: comfy_api_nodes.nodes_wan | category: partner/video/Wan
- required:
  - model: COMFY_DYNAMICCOMBO_V3
  - video: VIDEO
  - seed: INT default=0 min=0 max=2147483647 step=1
  - audio_setting: COMBO[auto, origin] default='auto'
  - watermark: BOOLEAN default=False
- outputs: VIDEO:VIDEO

## Wan3ImageToVideoApi
module: comfy_api_nodes.nodes_wan | category: partner/video/Wan
- required:
  - model: COMFY_DYNAMICCOMBO_V3
  - first_frame: IMAGE
  - seed: INT default=42 min=0 max=2147483647 step=1
  - watermark: BOOLEAN default=False
- optional:
  - last_frame: IMAGE
- outputs: VIDEO:VIDEO

## Wan3ReferenceToVideoApi
module: comfy_api_nodes.nodes_wan | category: partner/video/Wan
- required:
  - model: COMFY_DYNAMICCOMBO_V3
  - seed: INT default=42 min=0 max=2147483647 step=1
  - watermark: BOOLEAN default=False
- outputs: VIDEO:VIDEO

## WanAnimate2Cache
module: comfy_extras.nodes_wan | category: model/conditioning/wan/animate
- required:
  - model: MODEL
  - device: COMBO[cpu, gpu] default='cpu'
  - dtype: COMBO[default, int8, int4] default='default'
- outputs: MODEL:MODEL

## WanAnimate2ToVideo
module: comfy_extras.nodes_wan | category: model/conditioning/wan/animate
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - width: INT default=832 min=16 max=16384 step=16
  - height: INT default=480 min=16 max=16384 step=16
  - length: INT default=81 min=1 max=16384 step=4
  - batch_size: INT default=1 min=1 max=4096
  - video_frame_offset: INT default=0 min=0 max=16384 step=1
  - pose_strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - pose_start_percent: FLOAT default=0.0 min=0.0 max=1.0 step=0.01
  - pose_end_percent: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - reference_image_strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
- optional:
  - reference_image: IMAGE
  - pose_video: IMAGE
  - clip_vision_output: CLIP_VISION_OUTPUT
  - positive_pose: CONDITIONING
  - clip_vision_output_pose: CLIP_VISION_OUTPUT
  - continue_motion: IMAGE
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT, trim_latent:INT, trim_image:INT, video_frame_offset:INT

## WanAnimateToVideo
module: comfy_extras.nodes_wan | category: model/conditioning/wan/animate
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - width: INT default=832 min=16 max=16384 step=16
  - height: INT default=480 min=16 max=16384 step=16
  - length: INT default=77 min=1 max=16384 step=4
  - batch_size: INT default=1 min=1 max=4096
  - continue_motion_max_frames: INT default=5 min=1 max=16384 step=4
  - video_frame_offset: INT default=0 min=0 max=16384 step=1
- optional:
  - clip_vision_output: CLIP_VISION_OUTPUT
  - reference_image: IMAGE
  - face_video: IMAGE
  - pose_video: IMAGE
  - background_video: IMAGE
  - character_mask: MASK
  - continue_motion: IMAGE
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT, trim_latent:INT, trim_image:INT, video_frame_offset:INT

## wanBlockSwap
module: comfy_extras.nodes_nop | category: 
- required:
  - model: MODEL
- outputs: MODEL:MODEL

## WanCameraEmbedding
module: comfy_extras.nodes_camera_trajectory | category: model/conditioning/wan/camera
- required:
  - camera_pose: COMBO[Static, Pan Up, Pan Down, Pan Left, Pan Right, Zoom In, Zoom Out, Anti Clockwise (ACW), ClockWise (CW)] default='Static'
  - width: INT default=832 min=16 max=16384 step=16
  - height: INT default=480 min=16 max=16384 step=16
  - length: INT default=81 min=1 max=16384 step=4
- optional:
  - speed: FLOAT default=1.0 min=0 max=10.0 step=0.1
  - fx: FLOAT default=0.5 min=0 max=1 step=1e-09
  - fy: FLOAT default=0.5 min=0 max=1 step=1e-09
  - cx: FLOAT default=0.5 min=0 max=1 step=0.01
  - cy: FLOAT default=0.5 min=0 max=1 step=0.01
- outputs: camera_embedding:WAN_CAMERA_EMBEDDING, width:INT, height:INT, length:INT

## WanCameraImageToVideo
module: comfy_extras.nodes_wan | category: model/conditioning/wan/camera
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - width: INT default=832 min=16 max=16384 step=16
  - height: INT default=480 min=16 max=16384 step=16
  - length: INT default=81 min=1 max=16384 step=4
  - batch_size: INT default=1 min=1 max=4096
- optional:
  - clip_vision_output: CLIP_VISION_OUTPUT
  - start_image: IMAGE
  - camera_conditions: WAN_CAMERA_EMBEDDING
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## WanChunkFeedForward
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/wan
- required:
  - model: MODEL
  - chunks: INT default=2 min=1 max=100 step=1
  - dim_threshold: INT default=4096 min=1024 max=16384 step=256
- outputs: model:MODEL

## WanContextWindowsManual
module: comfy_extras.nodes_context_windows | category: model/patch/wan
- required:
  - model: MODEL
  - context_length: INT default=81 min=1 max=16384 step=4
  - context_overlap: INT default=30 min=0
  - context_schedule: COMBO[standard_static, standard_uniform, looped_uniform, batched] default='standard_uniform'
  - context_stride: INT default=1 min=1
  - closed_loop: BOOLEAN default=False
  - fuse_method: COMBO[pyramid, relative, flat, overlap-linear] default='pyramid'
  - freenoise: BOOLEAN default=True
  - retain_first_frame: BOOLEAN default=False
  - split_conds_to_windows: BOOLEAN default=False
- outputs: MODEL:MODEL

## WanDancerEncodeAudio
module: comfy_extras.nodes_wandancer | category: model/conditioning/wan/dancer
- required:
  - audio: AUDIO
  - video_frames: INT default=149 min=1 max=16384 step=4
  - audio_inject_scale: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
- outputs: audio_encoder_output:AUDIO_ENCODER_OUTPUT, fps_string:STRING

## WanDancerPadKeyframes
module: comfy_extras.nodes_wandancer | category: image/video
- required:
  - images: IMAGE
  - segment_length: INT default=149 min=1 max=10000
  - segment_index: INT default=0 min=0 max=100
  - audio: AUDIO
- outputs: keyframes_sequence:IMAGE, keyframes_mask:MASK, audio_segment:AUDIO

## WanDancerPadKeyframesList
module: comfy_extras.nodes_wandancer | category: image/video
- required:
  - images: IMAGE
  - segment_length: INT default=149 min=1 max=10000
  - num_segments: INT default=1 min=1 max=100
  - audio: AUDIO
- outputs: keyframes_sequence:IMAGE, keyframes_mask:MASK, audio_segment:AUDIO

## WanDancerVideo
module: comfy_extras.nodes_wandancer | category: model/conditioning/wan/dancer
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - width: INT default=480 min=16 max=16384 step=16
  - height: INT default=832 min=16 max=16384 step=16
  - length: INT default=149 min=1 max=16384 step=4
- optional:
  - clip_vision_output: CLIP_VISION_OUTPUT
  - clip_vision_output_ref: CLIP_VISION_OUTPUT
  - start_image: IMAGE
  - mask: MASK
  - audio_encoder_output: AUDIO_ENCODER_OUTPUT
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## WanFirstLastFrameToVideo
module: comfy_extras.nodes_wan | category: model/conditioning/wan
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - width: INT default=832 min=16 max=16384 step=16
  - height: INT default=480 min=16 max=16384 step=16
  - length: INT default=81 min=1 max=16384 step=4
  - batch_size: INT default=1 min=1 max=4096
- optional:
  - clip_vision_start_image: CLIP_VISION_OUTPUT
  - clip_vision_end_image: CLIP_VISION_OUTPUT
  - start_image: IMAGE
  - end_image: IMAGE
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## WanFunControlToVideo
module: comfy_extras.nodes_wan | category: model/conditioning/wan/fun control
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - width: INT default=832 min=16 max=16384 step=16
  - height: INT default=480 min=16 max=16384 step=16
  - length: INT default=81 min=1 max=16384 step=4
  - batch_size: INT default=1 min=1 max=4096
- optional:
  - clip_vision_output: CLIP_VISION_OUTPUT
  - start_image: IMAGE
  - control_video: IMAGE
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## WanFunInpaintToVideo
module: comfy_extras.nodes_wan | category: model/conditioning/wan/fun inpaint
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - width: INT default=832 min=16 max=16384 step=16
  - height: INT default=480 min=16 max=16384 step=16
  - length: INT default=81 min=1 max=16384 step=4
  - batch_size: INT default=1 min=1 max=4096
- optional:
  - clip_vision_output: CLIP_VISION_OUTPUT
  - start_image: IMAGE
  - end_image: IMAGE
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## WanHuMoImageToVideo
module: comfy_extras.nodes_wan | category: model/conditioning/wan/humo
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - width: INT default=832 min=16 max=16384 step=16
  - height: INT default=480 min=16 max=16384 step=16
  - length: INT default=97 min=1 max=16384 step=4
  - batch_size: INT default=1 min=1 max=4096
- optional:
  - audio_encoder_output: AUDIO_ENCODER_OUTPUT
  - ref_image: IMAGE
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## WanImageToImageApi
module: comfy_api_nodes.nodes_wan | category: partner/image/Wan
- required:
  - model: COMBO[wan2.5-i2i-preview] default='wan2.5-i2i-preview'
  - image: IMAGE
  - prompt: STRING default=''
- optional:
  - negative_prompt: STRING default=''
  - seed: INT default=0 min=0 max=2147483647 step=1
  - watermark: BOOLEAN default=False
- outputs: IMAGE:IMAGE

## WanImageToVideo
module: comfy_extras.nodes_wan | category: model/conditioning/wan
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - width: INT default=832 min=16 max=16384 step=16
  - height: INT default=480 min=16 max=16384 step=16
  - length: INT default=81 min=1 max=16384 step=4
  - batch_size: INT default=1 min=1 max=4096
- optional:
  - clip_vision_output: CLIP_VISION_OUTPUT
  - start_image: IMAGE
  - ref_pad_image: IMAGE
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## WanImageToVideoApi
module: comfy_api_nodes.nodes_wan | category: partner/video/Wan
- required:
  - model: COMBO[wan2.5-i2v-preview, wan2.6-i2v] default='wan2.6-i2v'
  - image: IMAGE
  - prompt: STRING default=''
- optional:
  - negative_prompt: STRING default=''
  - resolution: COMBO[480P, 720P, 1080P] default='720P'
  - duration: INT default=5 min=5 max=15 step=5
  - audio: AUDIO
  - seed: INT default=0 min=0 max=2147483647 step=1
  - generate_audio: BOOLEAN default=False
  - prompt_extend: BOOLEAN default=True
  - watermark: BOOLEAN default=False
  - shot_type: COMBO[single, multi]
- outputs: VIDEO:VIDEO

## WanImageToVideoSVIPro
module: custom_nodes.ComfyUI-KJNodes | category: conditioning/video_models
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - length: INT default=81 min=1 max=16384 step=4
  - anchor_samples: LATENT
  - motion_latent_count: INT default=1 min=0 max=128 step=1
- optional:
  - prev_samples: LATENT
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## WanInfiniteTalkToVideo
module: comfy_extras.nodes_wan | category: model/conditioning/wan/infinite talk
- required:
  - mode: COMFY_DYNAMICCOMBO_V3
  - model: MODEL
  - model_patch: MODEL_PATCH
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - width: INT default=832 min=16 max=16384 step=16
  - height: INT default=480 min=16 max=16384 step=16
  - length: INT default=81 min=1 max=16384 step=4
  - audio_encoder_output_1: AUDIO_ENCODER_OUTPUT
  - motion_frame_count: INT default=9 min=1 max=33 step=1
  - audio_scale: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
- optional:
  - clip_vision_output: CLIP_VISION_OUTPUT
  - start_image: IMAGE
  - previous_frames: IMAGE
- outputs: model:MODEL, positive:CONDITIONING, negative:CONDITIONING, latent:LATENT, trim_image:INT

## WanMoveConcatTrack
module: comfy_extras.nodes_wanmove | category: model/conditioning/wan/move
- required:
  - tracks_1: TRACKS
- optional:
  - tracks_2: TRACKS
- outputs: TRACKS:TRACKS

## WanMoveTracksFromCoords
module: comfy_extras.nodes_wanmove | category: model/conditioning/wan/move
- optional:
  - track_coords: STRING default='[]'
  - track_mask: MASK
- outputs: TRACKS:TRACKS, track_length:INT

## WanMoveTrackToVideo
module: comfy_extras.nodes_wanmove | category: model/conditioning/wan/move
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - strength: FLOAT default=1.0 min=0.0 max=100.0 step=0.01
  - width: INT default=832 min=16 max=16384 step=16
  - height: INT default=480 min=16 max=16384 step=16
  - length: INT default=81 min=1 max=16384 step=4
  - batch_size: INT default=1 min=1 max=4096
  - start_image: IMAGE
- optional:
  - tracks: TRACKS
  - clip_vision_output: CLIP_VISION_OUTPUT
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## WanMoveVisualizeTracks
module: comfy_extras.nodes_wanmove | category: model/conditioning/wan/move
- required:
  - images: IMAGE
  - line_resolution: INT default=24 min=1 max=1024
  - circle_size: INT default=12 min=1 max=128
  - opacity: FLOAT default=0.75 min=0.0 max=1.0 step=0.01
  - line_width: INT default=16 min=1 max=128
- optional:
  - tracks: TRACKS
- outputs: IMAGE:IMAGE

## WanPhantomSubjectToVideo
module: comfy_extras.nodes_wan | category: model/conditioning/wan/phantom subject
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - width: INT default=832 min=16 max=16384 step=16
  - height: INT default=480 min=16 max=16384 step=16
  - length: INT default=81 min=1 max=16384 step=4
  - batch_size: INT default=1 min=1 max=4096
- optional:
  - images: IMAGE
- outputs: positive:CONDITIONING, negative_text:CONDITIONING, negative_img_text:CONDITIONING, latent:LATENT

## WanReferenceVideoApi
module: comfy_api_nodes.nodes_wan | category: partner/video/Wan
- required:
  - model: COMBO[wan2.6-r2v]
  - prompt: STRING default=''
  - negative_prompt: STRING default=''
  - reference_videos: COMFY_AUTOGROW_V3
  - size: COMBO[720p: 1:1 (960x960), 720p: 16:9 (1280x720), 720p: 9:16 (720x1280), 720p: 4:3 (1088x832), 720p: 3:4 (832x1088), 1080p: 1:1 (1440x1440), 1080p: 16:9 (1920x1080), 1080p: 9:16 (1080x1920), 1080p: 4:3 (1632x1248), 1080p: 3:4 (1248x1632)]
  - duration: INT default=5 min=5 max=10 step=5
  - seed: INT default=0 min=0 max=2147483647 step=1
  - shot_type: COMBO[single, multi]
  - watermark: BOOLEAN default=False
- outputs: VIDEO:VIDEO

## WanSCAILToVideo
module: comfy_extras.nodes_scail | category: model/conditioning/wan/scail
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - width: INT default=512 min=32 max=16384 step=32
  - height: INT default=896 min=32 max=16384 step=32
  - length: INT default=81 min=1 max=16384 step=4
  - batch_size: INT default=1 min=1 max=4096
  - pose_strength: FLOAT default=1.0 min=0.0 max=10.0 step=0.01
  - pose_start: FLOAT default=0.0 min=0.0 max=1.0 step=0.01
  - pose_end: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - video_frame_offset: INT default=0 min=0 max=16384 step=1
  - previous_frame_count: INT default=5 min=1 max=16384 step=4
- optional:
  - pose_video: IMAGE
  - pose_video_mask: IMAGE
  - replacement_mode: BOOLEAN default=False
  - reference_image: IMAGE
  - reference_image_mask: IMAGE
  - clip_vision_output: CLIP_VISION_OUTPUT
  - previous_frames: IMAGE
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT, video_frame_offset:INT

## WanSoundImageToVideo
module: comfy_extras.nodes_wan | category: model/conditioning/wan/sound
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - width: INT default=832 min=16 max=16384 step=16
  - height: INT default=480 min=16 max=16384 step=16
  - length: INT default=77 min=1 max=16384 step=4
  - batch_size: INT default=1 min=1 max=4096
- optional:
  - audio_encoder_output: AUDIO_ENCODER_OUTPUT
  - ref_image: IMAGE
  - control_video: IMAGE
  - ref_motion: IMAGE
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## WanSoundImageToVideoExtend
module: comfy_extras.nodes_wan | category: model/conditioning/wan/sound
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - length: INT default=77 min=1 max=16384 step=4
  - video_latent: LATENT
- optional:
  - audio_encoder_output: AUDIO_ENCODER_OUTPUT
  - ref_image: IMAGE
  - control_video: IMAGE
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## WanTextToImageApi
module: comfy_api_nodes.nodes_wan | category: partner/image/Wan
- required:
  - model: COMBO[wan2.5-t2i-preview]
  - prompt: STRING default=''
- optional:
  - negative_prompt: STRING default=''
  - width: INT default=1024 min=768 max=1440 step=32
  - height: INT default=1024 min=768 max=1440 step=32
  - seed: INT default=0 min=0 max=2147483647 step=1
  - prompt_extend: BOOLEAN default=True
  - watermark: BOOLEAN default=False
- outputs: IMAGE:IMAGE

## WanTextToVideoApi
module: comfy_api_nodes.nodes_wan | category: partner/video/Wan
- required:
  - model: COMBO[wan2.5-t2v-preview, wan2.6-t2v] default='wan2.6-t2v'
  - prompt: STRING default=''
- optional:
  - negative_prompt: STRING default=''
  - size: COMBO[480p: 1:1 (624x624), 480p: 16:9 (832x480), 480p: 9:16 (480x832), 720p: 1:1 (960x960), 720p: 16:9 (1280x720), 720p: 9:16 (720x1280), 720p: 4:3 (1088x832), 720p: 3:4 (832x1088), 1080p: 1:1 (1440x1440), 1080p: 16:9 (1920x1080), ... +3] default='720p: 1:1 (960x960)'
  - duration: INT default=5 min=5 max=15 step=5
  - audio: AUDIO
  - seed: INT default=0 min=0 max=2147483647 step=1
  - generate_audio: BOOLEAN default=False
  - prompt_extend: BOOLEAN default=True
  - watermark: BOOLEAN default=False
  - shot_type: COMBO[single, multi]
- outputs: VIDEO:VIDEO

## WanTrackToVideo
module: comfy_extras.nodes_wan | category: model/conditioning/wan/move
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - tracks: STRING default='[]'
  - width: INT default=832 min=16 max=16384 step=16
  - height: INT default=480 min=16 max=16384 step=16
  - length: INT default=81 min=1 max=16384 step=4
  - batch_size: INT default=1 min=1 max=4096
  - temperature: FLOAT default=220.0 min=1.0 max=1000.0 step=0.1
  - topk: INT default=2 min=1 max=10
  - start_image: IMAGE
- optional:
  - clip_vision_output: CLIP_VISION_OUTPUT
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT

## WanUni3CControlnetApply
module: comfy_extras.nodes_model_patch | category: model/patch/wan
- required:
  - model: MODEL
  - model_patch: MODEL_PATCH
  - vae: VAE
  - render_video: IMAGE
  - strength: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
  - start_percent: FLOAT default=0.0 min=0.0 max=1.0 step=0.001
  - end_percent: FLOAT default=1.0 min=0.0 max=1.0 step=0.001
- outputs: MODEL:MODEL

## WanVaceToVideo
module: comfy_extras.nodes_wan | category: model/conditioning/wan/vace
- required:
  - positive: CONDITIONING
  - negative: CONDITIONING
  - vae: VAE
  - width: INT default=832 min=16 max=16384 step=16
  - height: INT default=480 min=16 max=16384 step=16
  - length: INT default=81 min=1 max=16384 step=4
  - batch_size: INT default=1 min=1 max=4096
  - strength: FLOAT default=1.0 min=0.0 max=1000.0 step=0.01
- optional:
  - control_video: IMAGE
  - control_masks: MASK
  - reference_image: IMAGE
- outputs: positive:CONDITIONING, negative:CONDITIONING, latent:LATENT, trim_latent:INT

## WanVideoEnhanceAVideoKJ
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/wan
- required:
  - model: MODEL
  - latent: LATENT
  - weight: FLOAT default=2.0 min=0.0 max=10.0 step=0.001
- outputs: model:MODEL

## WanVideoMemoryEfficientSageAttentionPatch
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/wan
- required:
  - model: MODEL
- outputs: model:MODEL

## WanVideoNAG
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/wan
- required:
  - model: MODEL
  - conditioning: CONDITIONING
  - nag_scale: FLOAT default=11.0 min=0.0 max=100.0 step=0.001
  - nag_alpha: FLOAT default=0.25 min=0.0 max=1.0 step=0.001
  - nag_tau: FLOAT default=2.5 min=0.0 max=10.0 step=0.001
- optional:
  - input_type: COMBO[default, batch]
  - inplace: BOOLEAN default=False
- outputs: model:MODEL

## WanVideoTeaCacheKJ
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/deprecated
- required:
  - model: MODEL
  - rel_l1_thresh: FLOAT default=0.275 min=0.0 max=10.0 step=0.001
  - start_percent: FLOAT default=0.1 min=0.0 max=1.0 step=0.01
  - end_percent: FLOAT default=1.0 min=0.0 max=1.0 step=0.01
  - cache_device: COMBO[main_device, offload_device] default='offload_device'
  - coefficients: COMBO[disabled, 1.3B, 14B, i2v_480, i2v_720] default='i2v_480'
- outputs: model:MODEL

## WavespeedFlashVSRNode
module: comfy_api_nodes.nodes_wavespeed | category: partner/video/WaveSpeed
- required:
  - video: VIDEO
  - target_resolution: COMBO[720p, 1080p, 2K, 4K]
- outputs: VIDEO:VIDEO

## WavespeedImageUpscaleNode
module: comfy_api_nodes.nodes_wavespeed | category: partner/image/WaveSpeed
- required:
  - model: COMBO[SeedVR2, Ultimate]
  - image: IMAGE
  - target_resolution: COMBO[2K, 4K, 8K]
- outputs: IMAGE:IMAGE

## WebcamCapture
module: comfy_extras.nodes_webcam | category: image
- required:
  - image: WEBCAM
  - width: INT default=0 min=0 max=16384 step=1
  - height: INT default=0 min=0 max=16384 step=1
  - capture_on_queue: BOOLEAN default=True
- outputs: IMAGE:IMAGE

## WebcamCaptureCV2
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/experimental
- required:
  - x: INT default=0 min=0 max=4096 step=1
  - y: INT default=0 min=0 max=4096 step=1
  - width: INT default=512 min=0 max=4096 step=1
  - height: INT default=512 min=0 max=4096 step=1
  - cam_index: INT default=0 min=0 max=255 step=1
  - release: BOOLEAN default=False
- outputs: image:IMAGE

## WeightScheduleConvert
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/weights
- required:
  - input_values: FLOAT default=0.0
  - output_type: COMBO[match_input, list, pandas series, tensor] default='list'
  - invert: BOOLEAN default=False
  - repeat: INT default=1 min=1 max=255 step=1
- optional:
  - remap_to_frames: INT default=0
  - interpolation_curve: FLOAT
  - remap_values: BOOLEAN default=False
  - remap_min: FLOAT default=0.0 min=-100000 max=100000.0 step=0.01
  - remap_max: FLOAT default=1.0 min=-100000 max=100000.0 step=0.01
- outputs: FLOAT:FLOAT, STRING:STRING, INT:INT

## WeightScheduleExtend
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/weights
- required:
  - input_values_1: FLOAT default=0.0
  - input_values_2: FLOAT default=0.0
  - output_type: COMBO[match_input, list, pandas series, tensor] default='match_input'
- outputs: FLOAT:FLOAT

## WeldVertices
module: comfy_extras.nodes_mesh_postprocess | category: 3d/mesh
- required:
  - mesh: MESH
  - epsilon_rel: FLOAT default=1e-05 min=0.0 step=1e-06
  - epsilon_abs: FLOAT default=0.0 min=0.0 step=1e-06
- outputs: mesh:MESH

## WidgetToString
module: custom_nodes.ComfyUI-KJNodes | category: KJNodes/text
- required:
  - id: INT default=0 min=0 max=100000 step=1
  - widget_name: STRING
  - return_all: BOOLEAN default=False
- optional:
  - any_input: *
  - node_title: STRING
  - allowed_float_decimals: INT default=2 min=0 max=10
- outputs: STRING:STRING

## YuE2GenerateABC
module: comfy_extras.nodes_yue2 | category: model/conditioning/yue2
- required:
  - clip: CLIP
  - style: STRING
  - lyrics: STRING
  - seed: INT default=0 min=0 max=18446744073709551615
  - mode: COMBO[full, melody]
  - max_abc_tokens: INT default=8192 min=1 max=20000
  - temperature: FLOAT default=0.7 min=0.0 max=5.0 step=0.05
  - top_p: FLOAT default=0.9 min=0.01 max=1.0 step=0.01
  - top_k: INT default=30 min=1 max=32768
  - repetition_penalty: FLOAT default=1.005 min=0.01 max=10.0 step=0.005
  - penalty_window: INT default=100 min=1 max=20000
- outputs: abc:STRING

## YuE2GenerateMusic
module: comfy_extras.nodes_yue2 | category: model/conditioning/yue2
- required:
  - clip: CLIP
  - style: STRING
  - lyrics: STRING
  - abc: STRING default=''
  - seed: INT default=0 min=0 max=18446744073709551615
  - mode: COMBO[full, melody]
  - max_duration: FLOAT default=360.0 min=0.04 max=900.0 step=0.04
  - temperature: FLOAT default=1.0 min=0.0 max=5.0 step=0.05
  - top_p: FLOAT default=0.95 min=0.01 max=1.0 step=0.01
  - top_k: INT default=100 min=1 max=32768
  - repetition_penalty: FLOAT default=1.2 min=0.01 max=10.0 step=0.01
- optional:
  - cfg_scale: FLOAT default=1.0 min=0.0 max=100.0 step=0.01
- outputs: CONDITIONING:CONDITIONING, seconds:FLOAT

## ZImageFunControlnet
module: comfy_extras.nodes_model_patch | category: model/patch
- required:
  - model: MODEL
  - model_patch: MODEL_PATCH
  - vae: VAE
  - strength: FLOAT default=1.0 min=-10.0 max=10.0 step=0.01
- optional:
  - image: IMAGE
  - inpaint_image: IMAGE
  - mask: MASK
  - start_percent: FLOAT default=0.0 min=0.0 max=1.0 step=0.001
  - end_percent: FLOAT default=1.0 min=0.0 max=1.0 step=0.001
- outputs: MODEL:MODEL

## Zoe-DepthMapPreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Normal and Depth Estimators
- required:
  - image: IMAGE
- optional:
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## Zoe_DepthAnythingPreprocessor
module: custom_nodes.comfyui_controlnet_aux | category: ControlNet Preprocessors/Normal and Depth Estimators
- required:
  - image: IMAGE
- optional:
  - environment: COMBO[indoor, outdoor] default='indoor'
  - resolution: INT default=512 min=64 max=16384 step=64
- outputs: IMAGE:IMAGE

## AIO workflow coverage (civitai 2906001)
Node types used: 32; found in object_info: 26.
Used and installed: BasicScheduler, BlockSparseAttention, CLIPLoader, ComfyMathExpression, ComfySwitchNode, ConditioningZeroOut, KSamplerSelect, LoadImage, LoraLoaderModelOnly, MiniMaxH3ReferenceToVideo, MiniMaxH3SigmaShift, ModelAttentionBackend, ModelPreviewOverrideKJ, PrimitiveBoolean, PrimitiveFloat, PrimitiveStringMultiline, ResolutionSelector, SelfLiftH3Sampler, UNETLoader, UniBlockSwap, VAEDecode, VAEDecodeAudio, VAELoader, VHS_LoadAudioUpload, VHS_LoadVideo, VHS_VideoCombine

### NOT in object_info (not installed)
- Fast Groups Bypasser (rgthree)
- GetNode
- Label (rgthree)
- SetNode
