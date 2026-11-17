---
license: other
license_name: minimax-h3-community-license-agreement
license_link: https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE
pipeline_tag: image-text-to-video
base_model_relation: quantized
base_model:
  - TenStrip/10Eros-Max
tags:
  - minimax-h3
  - comfyui
  - w4a8
  - w6a8
  - int8
  - convrot
  - quantization
  - activation-aware
  - text-to-video
  - image-text-to-video
  - image-to-video
  - not-for-all-audiences
---

# 10Eros Max H3 Beta7 eight-step Turbo — activation-guided learned quantization

The current release is an **18.69 GB HQ** weight-only quantization of the
H3 Beta7 transformer from
[TenStrip/10Eros-Max](https://huggingface.co/TenStrip/10Eros-Max).
It retains the source's embedded eight-step Turbo and uses learned W6 g16 and
INT8 ConvRot weights. The operator completed ComfyUI testing and accepted this
checkpoint on **2026-10-28**.

**A W4-based compact Beta7 checkpoint is forthcoming.** Its final size, precision
map and quality results will be added after completion and acceptance. The
older Beta6 compact checkpoint remains a separate source release.

Beta7 has the standard H3 tensor layout without compression-gate tensors.
The upstream author describes its merge as MLP-focused, preserving base
attention/reference behavior, and recommends Euler/simple or ER-SDE/SGM_uniform
for its Turbo sampling. See the
[upstream source notes](https://huggingface.co/TenStrip/10Eros-Max) for its recipe,
workflow settings and known limitations.

This is a personal hobby project aimed at making useful H3 output accessible
on consumer hardware with a smaller weight storage and memory footprint.
The goal is the best practical quality within those constraints. This release
is not presented as a quality-equivalent replacement for the approximately
40 GB BF16 source.

In the operator's ComfyUI tests, HQ worked correctly and appeared near or equal
in quality to the matching native INT8 HQ companion, with lower observed memory
use and faster generation. These are subjective observations from the tested
workflows; there is no quantified inference-memory or throughput benchmark.
**HQ identifies this campaign's high-quality precision map**; it does not
establish parity with BF16 or global optimality among quantization methods.

## Choose a checkpoint

| Release | Exact size | Learned matrix formats | Intended choice |
|---|---:|---|---|
| [Beta7 HQ](https://huggingface.co/LokkenJP/TenEros_Max_optimized_learned/resolve/main/10Eros_Max_h3_8stepTURBO_beta7_activation_learned_HQ.safetensors) | 18,691,644,302 bytes / 18.6916 GB | 90 W6 g16, 110 INT8 | Accepted high-quality release |
| Beta7 compact | Pending | W4-based map pending | Forthcoming; no accepted artifact yet |

Sizes are decimal disk GB, not required VRAM. Working memory, activations,
other model components and offloading affect the inference memory footprint.

HQ uses INT8 for every attention OUT and FC2 matrix and all four main matrices
at blocks 0/1/47/48/49. QKV and FC1 at blocks 2–46 use W6 g16.
All **332 non-target tensors remain byte-preserved in BF16**, their source
precision. This is transformer-only: the text encoder, video/audio VAEs and
workflow are separate. H3's BigVGAN waveform decoder is integrated into the
audio VAE; it is not an additional vocoder checkpoint to load.

## What activation-guided learning adds

> **Read the [Beta7 technical overview](https://huggingface.co/LokkenJP/TenEros_Max_optimized_learned/blob/main/H3_BETA7_TURBO_PROXY_ACTIVATION_TECHNICAL_OVERVIEW.md)**
> for the full methodology, learning gains by precision and tensor family,
> the HQ map, quality safeguards and comparison limits.

Offline proxy activation trajectories guide reconstruction of the original
BF16 source weights. The completed HQ population gives these results against
native quantization at each matrix's selected precision:

**Rank32-plus-residual activation NRMSE:**

| Format | Matrices | Native mean NRMSE | Learned mean NRMSE | Mean paired reduction |
|---|---:|---:|---:|---:|
| W6 g16 | 90 | 0.016150 | 0.010153 | 37.29% |
| INT8 | 110 | 0.008286 | 0.005405 | 35.88% |

**Raw activation NRMSE (sampled input rows):**

| Format | Matrices | Native mean NRMSE | Learned mean NRMSE | Mean paired reduction |
|---|---:|---:|---:|---:|
| W6 g16 | 90 | 0.015385 | 0.008140 | 47.31% |
| INT8 | 110 | 0.008202 | 0.004742 | 43.36% |

Each reduction column is the equal-matrix mean of paired percentage reductions
in the corresponding calibration trajectory metric. It differs from dividing
the two mean-error columns. Format populations differ, so these are not a
matched comparison between precisions or percentages of perceptual improvement.
All 200 matrices also improved their calibration raw-row and diagonal-weighted
activation errors relative to native.

One unified learner supplies the common screening, main optimization and
polish path. It uses fresh 96-step probes on approximately 1/16 of each
matrix's chunks, adaptive penalty values carried from the preceding same-family
matrix, and disjoint 1/16 refinement of the best three admitted candidates.
The main learner compares a fresh zero-penalty full64 run with the screened
winner's fresh full96 run. A guarded discrete polish tail uses a separately
selected positive penalty favoring weight reconstruction. All choices use
calibration only; native remains the fallback if no full candidate qualifies.

Learning used fresh Beta7 captures: 48 calibration trajectories from 12 prompts
and 24 development trajectories from 8 disjoint prompts, balanced between
`euler/simple` and `er_sde/sgm_uniform`. Capture was at 640×480, 226 frames,
24 fps, eight steps and video/audio sigma shifts **12/3**. Development was
recorded for audit and excluded from training and selection.

The proxy was a matching **22.89 GB native INT8 HQ companion** built from the
same source: 180 interior matrices INT8, with blocks 0/1/47/48/49 and all
non-target tensors preserved in BF16. It supplied activation inputs; the
original BF16 weights remained the reconstruction targets.

Proxy capture was a hardware-driven compromise. The author's machine has an
RTX 4080 with 16 GB VRAM and 32 GB system RAM; capturing directly from the
approximately 40 GB BF16 source was not feasible in that setup without
out-of-memory failures. Proxy inputs can differ from source-model inputs,
so this is not exact BF16-teacher capture. No activation cache is needed at
inference.

## Quality observations and validation

The operator tested several ComfyUI generations and reported correct operation,
quality near or equal to the matching native INT8 HQ companion, lower memory
use and faster generation. Acceptance was recorded on 2026-10-28. This was
manual, subjective evaluation by one operator in the tested workflows, without
a blinded multi-rater study, exact BF16-source A/B or objective video-quality
benchmark.

The [upstream author](https://huggingface.co/TenStrip/10Eros-Max) also reports
background/latent flickering in single-pass workflows, with two-pass spatial
refinement helping. The supplied two-pass workflow is linked below; this
quantization campaign does not establish behavior for every sampling setup.

The assembled checkpoint passed mechanical validation of the selected candidates,
source-preserved tensors, quantization metadata and output integrity. These
checks establish assembly integrity; local reconstruction measurements guide
learning but do not measure generated-video quality directly.

Activation gains have a disclosed tradeoff: mean ordinary weight NRMSE increased
**3.91% for W6 and 4.74% for INT8** relative to native, within the approved
admission and polish guards. The optimizer prioritizes captured activation
reconstruction while bounding weight and trajectory drift.

The numerical gains above describe calibration reconstruction. Matching native
development baselines were not saved, so these gains must not be described as
held-out improvements.

## Use in ComfyUI

Place the selected `.safetensors` in the diffusion-model/transformer folder
used by your H3 workflow and select it in the compatible loader. Use a ComfyUI
installation with native W4A8, W6A8 and INT8 ConvRot support. W6 support is
documented in [Comfy Kitchen PR #191](https://github.com/Comfy-Org/comfy-kitchen/pull/191)
and [ComfyUI PR #16483](https://github.com/Comfy-Org/ComfyUI/pull/16483).
Use ComfyUI v0.38.0 or later for the provided checkpoints.
Use the source's compatible H3 text encoder, video/audio VAEs and eight-step Turbo
workflow. Capture settings describe the calibration envelope; 640×480 is not
a restriction on generation resolution.

Keep the `.sha256` and `.quantization.json` companions for integrity and
provenance. They are not inference dependencies. These models are already
quantized; use their native formats rather than applying another quantization.

The [**workflows folder**](https://huggingface.co/LokkenJP/TenEros_Max_optimized_learned/tree/main/SampleWorkFlowTwoPassOptimized)
provides a customizable ComfyUI workflow for two-pass H3 video/audio generation
with learned latent upscaling and refinement. Additional features include
first-pass Preview with cache reuse, optional sparse attention, continuation mode
with video/audio guidance and stitched export, RTX super-resolution, and Normal-mode
RTX frame generation for high frame rate videos.
H3 generation and continuation remain at the native 24 FPS in this workflow.
Optional output grain and selectable H.264 encoder presets use
[Lokken VideoTools](https://registry.comfy.org/nodes/lokken-videotools),
available through ComfyUI-Manager.

The latest workflow is at the folder's top level; previous versions are archived
under `old/`. Check model selections and local paths against your installation,
and follow the usage notes included in the workflow. The configured
components are recommended.

## Exact identities

The accepted Beta7 source was captured under its pre-release filename
`10Eros_Max_h3_8stepTURBO_beta7_test3.safetensors`, 40,222,934,448 bytes.
That filename remains in the campaign records; the source and accepted
quantization were subsequently promoted to full Beta7.

```text
Source SHA-256
b1361691a953ff7623e5dc628a76e338d592da12e3c9d5652cecb7eeaaa4aa94

10Eros_Max_h3_8stepTURBO_beta7_activation_learned_HQ.safetensors
01a696efc96708f3edd15ff20fa3f56068974ba08a1b4c5801cef2bd49600ad7
```

HQ reduces source disk size by **53.53%**. The accepted checkpoint and four
sidecars were renamed from the Test3 filename without changing checkpoint
bytes. Only the checksum sidecar's filename field changed; historical campaign
evidence retains its original paths.

## Legacy Beta5 Turbo HQ references

Two native, unlearned Beta5 Turbo HQ references are also available in
[beta5/Beta5_HQRef](https://huggingface.co/LokkenJP/TenEros_Max_optimized_learned/tree/main/beta5/Beta5_HQRef):

| Checkpoint | Size | Main-matrix topology |
|---|---:|---|
| [Native INT8 / W6 g16 HQ](https://huggingface.co/LokkenJP/TenEros_Max_optimized_learned/resolve/main/beta5/Beta5_HQRef/10Eros_Max_h3_TURBO-hybrid_beta5_native_int8_w6a8g16_HQ.safetensors) | 18.69 GB | Blocks 0-1 and 47-49: all four families INT8. Blocks 2-46: QKV/FC1 W6 g16, OUT/FC2 INT8. |
| [Native INT8 with BF16 edges HQ](https://huggingface.co/LokkenJP/TenEros_Max_optimized_learned/resolve/main/beta5/Beta5_HQRef/10Eros_Max_h3_TURBO-hybrid_beta5_native_int8_bf16_edges_HQ.safetensors) | 22.89 GB | Blocks 0-1 and 47-49: all four families preserved BF16. Blocks 2-46: all four families INT8. |

Both retain the Beta5 source's embedded Turbo and copy all 334 non-target
tensors exactly in BF16. INT8 uses native ConvRot quantization; W6 g16 uses
native quantization with scale search. Neither uses activation captures or
learned weights, so the Beta7 learning gains above do not apply to them.
They are transformer-only references for the legacy Beta5 source.

## Previous releases

The accepted Beta6 releases remain historical references:

- [Beta6 learned HQ](https://huggingface.co/LokkenJP/TenEros_Max_optimized_learned/resolve/main/beta6/10Eros_Max_h3_8stepTURBO_beta6_pruned_activation_learned_int8_w6a8g16_HQ.safetensors), 18.6917 GB
- [Beta6 compact v1](https://huggingface.co/LokkenJP/TenEros_Max_optimized_learned/resolve/main/beta6/10Eros_Max_h3_8stepTURBO_beta6_pruned_activation_learned_14.6gb_v1.safetensors), 14.5985 GB
- [Beta6 technical overview](https://huggingface.co/LokkenJP/TenEros_Max_optimized_learned/blob/main/beta6/H3_BETA6_TURBO_PROXY_ACTIVATION_TECHNICAL_OVERVIEW.md)

Older Beta5 folders retain previously released checkpoints and evidence:

- [Beta5 final INT8/W6/W4 V8](https://huggingface.co/LokkenJP/TenEros_Max_optimized_learned/tree/main/beta5/Beta5_final_int8w6w4_hybrid)
- [Beta5 experimental W6/W4 V7](https://huggingface.co/LokkenJP/TenEros_Max_optimized_learned/tree/main/beta5/Beta5_experimental_w6a8)
- [Beta5 proxy activation V5](https://huggingface.co/LokkenJP/TenEros_Max_optimized_learned/tree/main/beta5/Beta5_proxy_activation_final_v5)
- [Beta5 first proxy-activation release](https://huggingface.co/LokkenJP/TenEros_Max_optimized_learned/tree/main/beta5/Beta5ProxyActivatedLearned_v1)
- [Beta5 basic learned / non-Turbo releases](https://huggingface.co/LokkenJP/TenEros_Max_optimized_learned/tree/main/beta5/Beta5BasicLearned)

They are different source campaigns. Beta7 gains, capture envelope and maps
must not be attributed to those artifacts.

## Attribution and evidence

Source model by [TenStrip](https://huggingface.co/TenStrip/10Eros-Max), based on
MiniMax H3. Licensing follows the
[MiniMax H3 Community License Agreement](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)
and the upstream source's terms. The source is designated Not-For-All-Audiences;
that designation also applies to this derivative.

The [quantization project](https://github.com/LordLocksley/ltx23-10eros-fp8-quantization) contains source-bound learner code,
frozen policies, allocation maps and acceptance evidence. See the
[Beta7 technical overview](https://huggingface.co/LokkenJP/TenEros_Max_optimized_learned/blob/main/H3_BETA7_TURBO_PROXY_ACTIVATION_TECHNICAL_OVERVIEW.md) for the
complete explanation of what was learned, measured and accepted.
