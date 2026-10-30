# Standard H3 Beta7 Turbo: activation-guided learned quantization

This overview describes the operator-accepted **18.69 GB Beta7 HQ** transformer.
It explains how its weights were learned, what was measured, and the limits of
the quality comparison. A W4-based compact Beta7 checkpoint is forthcoming;
its final size, precision map and acceptance are pending. No compact Beta7
measurements are included here.

This is a personal hobby project developed on consumer hardware, aiming for
useful H3 output with a smaller weight storage and memory footprint. The
release is not presented as equivalent to the approximately 40 GB BF16 source.
The operator reports HQ quality near or equal to the matching native INT8 HQ
companion in several ComfyUI generations, with lower observed memory use and
faster generation. These are subjective observations without a quantified
inference-memory or throughput benchmark.

## Source and scope

The source is the Beta7 transformer from
[TenStrip/10Eros-Max](https://huggingface.co/TenStrip/10Eros-Max), with embedded
eight-step Turbo. Its recorded campaign filename is
`10Eros_Max_h3_8stepTURBO_beta7_test3.safetensors`; the publisher/operator
subsequently promoted the source and accepted quantization to full Beta7.
Source size is 40,222,934,448 bytes and its verified recorded SHA-256 is
`b1361691a953ff7623e5dc628a76e338d592da12e3c9d5652cecb7eeaaa4aa94`.

Header inspection and campaign records identify 532 BF16 tensors and the
standard 50-block H3 layout, without compression-gate tensors. Blocks are
numbered 0–49, with four target matrices each:

| Family | Function |
|---|---|
| QKV | Produces the query, key and value vectors used by attention |
| OUT | Projects attention output back into the hidden representation |
| FC1 | Expands the feed-forward representation before its gated nonlinearity |
| FC2 | Projects the feed-forward result back into the hidden representation |

All 200 targets are learned at the precision selected by the HQ map. The
remaining **332 tensors are preserved byte-for-byte in BF16**, including
non-target source parameters. This source does not inherit Beta6's mixture
of BF16/F16/F32 non-target dtypes.

The release contains the transformer only. The H3 text encoder, video/audio
VAEs and workflow are separate. BigVGAN waveform decoding is integrated into
H3's audio VAE, rather than supplied as another vocoder checkpoint. Upstream
source notes own the model recipe and generation recommendations; a gate-free
header alone does not determine ancestry or validate an attention sparsity.

## Representations

Quantization stores compact codes and scales that decode to approximate source
weights. A candidate is one source matrix in a particular format. The precision
map selects one candidate for each of the 200 matrices. Native means the initial
unlearned quantization; learned means codes or parameters optimized using
captured activation inputs.

All HQ targets use ConvRot, a weight/input coordinate rotation in groups of
256 channels supported by the inference runtime. W6 g16 stores packed six-bit
codes, FP8 E4M3 relative scales per group of 16 weights and FP32 channel scales.
INT8 stores signed codes in [-128,127] with FP32 row scales. The scaling group
length is separate from ConvRot's group 256. Packed storage containers alone
do not identify a matrix's effective precision.

W6 starts from native scale-search quantization and holds its scales fixed.
The approved learner can use all stored codes 0–63, including the additional
negative endpoint represented by code 0; native symmetric initialization is
unchanged. INT8 holds row scales fixed while learning rounding, then refits
those scales once with the selected hard codes before full-candidate scoring.
The tail keeps scales fixed in both formats.

The checkpoint is weight-only: captured activations are not bundled or required
at inference. W6A8 runtime kernels also use eight-bit activations during matrix
multiplication. The prospective W4 format is not part of this accepted HQ map.

## Source-specific activation capture

The proxy was the source-matched native companion
`10Eros_Max_h3_8stepTURBO_beta7_test3-native_int8_HQ.safetensors`,
22,893,150,024 bytes, with recorded SHA-256
`8a51ca3f7d290a799d89fefcde4ede60962256955a91dfe4746d3cc07814fd6e`.
Its 180 interior main matrices use native INT8 ConvRot; all matrices at
blocks 0/1/47/48/49 and all non-target tensors retain source BF16.

The companion supplied matrix-input vectors during generation. The original
BF16 source weights supplied the reconstruction targets. This proxy made
capture feasible on an RTX 4080 with 16 GB VRAM and about 32 GB system RAM;
direct approximately 40 GB BF16-source capture exceeded the available resources.
Proxy inputs may differ from BF16-model inputs. This campaign does not measure
that discrepancy or establish equivalence to exact BF16-teacher capture.

| Capture property | Actual Beta7 campaign |
|---|---|
| Resolution / duration | 640×480; 226 frames at 24 fps |
| Turbo steps / sigma shifts | 8; video/audio shifts 12/3 |
| Sampler/scheduler pairs | `euler/simple`, `er_sde/sgm_uniform` |
| Step groups | Early 0–2; middle 3–4; late 5–7 |
| Calibration | 12 prompts, 48 trajectories; 24 per sampler pair |
| Development | 8 disjoint prompts, 24 trajectories; 12 per sampler pair |
| Conditioning | Cached positive-only text; joint audio/video trajectories |
| Coverage | All 200 main matrices; fresh source-specific seeds and captures |
| Evidence | Rank32 rounding sketches + exact diagonal residual; sampled raw rows |

Calibration supplies training inputs and all decisions. Development is audit-only
and excluded from training, penalty selection, candidate admission and polish
acceptance. No activation or learned-weight payload from an earlier source version supplies
this release's results. The capture resolution describes the measured envelope and
is not a generation-resolution limit.

To limit capture storage, rank32 sketches retain principal input directions,
with an exact diagonal residual for omitted input energy. Separate sampled
raw rows retain actual input vectors for another reconstruction measurement.
Capture also retains a rank16 diagnostic sketch, 64 selected rows and eight
raw rows per call, modality supplements and rank64 FC2 audit controls.

## What learning minimizes

Let E = Q - W, with source weights W and decoded weights Q in the same source
coordinates. Let B hold retained activation directions, r the residual
input-energy diagonal, d the full input-energy diagonal and R sampled input
vectors. The measured local losses are:

```text
L_rank(E) = ||E Bᵀ||²_F + Σᵢⱼ Eᵢⱼ² rⱼ
L_diag(E) = Σᵢⱼ Eᵢⱼ² dⱼ
L_raw(E)  = ||E Rᵀ||²_F
NRMSE    = sqrt(L(E) / L(W))
```

Each trajectory uses its own full-source projection-energy denominator.
NRMSE is normalized root mean square error; lower is better. Rank32-plus-residual
error is the primary ranking metric. Raw rows and diagonal weighting provide
separate views. Mean, p90, p99 and maximum trajectory errors are retained.
Weight safety measurements compare decoded weights directly with the source,
including overall relative L2 error and output-row p99/maximum relative L2 error.

A raw weight-reconstruction penalty balances the activation objective against
ordinary weight error. Local projection losses do not directly measure error
propagation through nonlinear layers, final denoising or generated-video quality.

## Unified learner design

A single production learner supplies the common optimizer, screening, full
selection and polish path. This is matrix-local learning rather than end-to-end
retraining. For this release the two format parameterizations differ in storage,
rounding representation and the INT8 scale refit described above.

Learning, probes and polish use one width-dependent chunk rule, where K is
matrix width:

```text
chunk_rows = max(1, (64 * 1024 * 1024) // (K * 4 * 16))
```

The rule bounds an estimate of temporary work, rather than guaranteeing a
64 MiB peak GPU allocation. All calculations account for decoded stored scales.
Reconstruction uses FP32 with FP64 score reductions; development never guides
optimization.

1. **Sampled96 screening.** Each penalty receives a fresh 96-step AdamW run
   on approximately 1/16 of whole matrix chunks, spread over output rows.
   Scores retain full-source trajectory denominators. Every tensor initially
   tests zero and three positive penalties. Each family has approved default
   starting values; later tensors inherit the preceding same-family/group
   tensor's three best admitted positive penalties from initial screening.
   Only penalty values carry forward, never scores, optimizer state or weights.
2. **Bounded adaptive search and refinement.** Boundary winners can trigger
   upward or downward extensions. If zero wins the initial four, missing
   default positives are checked instead of extensions. The initial search
   uses at most seven distinct penalties. Up to three initially admitted
   winners receive a fresh96 probe on a disjoint approximately 1/16 chunk
   sample. The equal mean of the two calibration scores chooses the full96
   penalty, retaining initial admission. Refinement does not add an admission
   filter or change the initial scores used for handoff.
3. **Fresh full learning.** Zero always receives a full-matrix 64-step run.
   The refined winner receives a separate full-matrix 96-step run, even when
   its penalty is also zero. Both start from native. The candidate must pass
   native-relative admission and strictly improve primary calibration error;
   exact full-candidate ties retain the earlier 64-step result. If neither
   qualifies, native remains selected and polish is skipped.
4. **Separate polish penalty.** The tail uses the initially admitted positive
   probe with lowest ordinary weight NRMSE, including any extension/default
   probes. If no positive probe qualifies, it retains the selected main
   penalty. This changes the tail's search objective without rerunning AdamW
   or letting anticipated polish affect full-candidate selection.
5. **Guarded discrete polish.** Adjacent-code proposals use fixed scales and
   gradient/curvature estimates, with rowwise move budgets. The common total
   budget is ceil(0.005 × matrix elements), with a minimum of one, divided
   over refreshes. Four-refresh passes continue until one is rejected; the
   last accepted weights then continue with single-refresh passes until
   rejection or the common 36-attempt limit. Rejected states never replace
   the selected weights.

Completed compatible tensor results are reused by the campaign's existing
recovery path. Interrupted work and prior reports are preserved. On resume,
recorded starts and the latest preceding family report supply adaptive values;
missing predecessor data falls back to the family seeds.

## Guarded polish safeguards

Neither primary calibration mean may worsen in an accepted pass. The average
relative improvement across rank32-plus-residual and raw-row means must be at
least 0.05%. Each metric must improve on at least 36/48 calibration trajectories
and 18/24 within each sampler. Whole-matrix admission against native still applies.

Cumulative secondary drift is measured from the selected pre-polish state.
The allowance benefit credits the smaller rank/raw improvement from native
to the candidate, including main learning. Thus AdamW gains can support further
polish, while the hard ceilings remain fixed. The common allowances have zero
intercepts and use min(hard ceiling, slope × credited benefit):

| Metric | Benefit slope | Hard ceiling on cumulative increase |
|---|---:|---:|
| Mean diagonal-weighted activation error | 0.075 | 0.14% |
| Ordinary weight NRMSE | 0.15 | 0.21% |
| Maximum output-row relative error | 1.0 | 1.40% |
| Row-p99 relative error | 0.175 | 0.28% |
| Worst trajectory rank32 or diagonal error | 0.15 | 0.1625% |
| Worst trajectory raw-row error | 0.15 | 0.35% |

These are tail limits relative to pre-polish, distinct from admission of the
whole learned state against native. There is no additional incremental
secondary budget. Primary trajectory-win checks still compare each proposal
with the last accepted state. Every final tensor passed its native admission.

## Measured learning gains

The accepted HQ map contains exactly 90 W6 g16 and 110 INT8 candidates. All
200 improve the three calibration activation metrics against native at the
same selected precision.

| Format | Matrices | Native mean primary NRMSE | Final mean primary NRMSE | Mean paired reduction |
|---|---:|---:|---:|---:|
| W6 g16 | 90 | 0.016150 | 0.010153 | 37.29% |
| INT8 | 110 | 0.008286 | 0.005405 | 35.88% |

Percentage reductions are computed per matrix and then averaged equally.
The two absolute-error columns are separate arithmetic means, so their ratio
need not reproduce the mean paired reduction. Format populations differ;
these numbers do not rank precision formats or measure perceptual gains.

| Format / family | Matrices | Primary reduction | Raw-row reduction | Diagonal reduction |
|---|---:|---:|---:|---:|
| W6 g16 QKV | 45 | 37.39% | 47.72% | 14.20% |
| W6 g16 FC1 | 45 | 37.19% | 46.91% | 11.82% |
| INT8 QKV | 5 | 38.06% | 48.67% | 15.05% |
| INT8 OUT | 50 | 36.54% | 47.37% | 6.71% |
| INT8 FC1 | 5 | 37.34% | 47.60% | 10.11% |
| INT8 FC2 | 50 | 34.85% | 38.41% | 26.23% |

Before polish, mean primary reductions were 36.05% W6 and 34.56% INT8. Polish
reduced the remaining primary error by a mean 1.97% W6 and 2.02% INT8, contributing
accepted changes on all 200 tensors. Ordinary weight NRMSE increased relative
to native by a mean 3.91% W6 and 4.74% INT8. This is a disclosed tradeoff within
the existing guards rather than an improvement of every weight metric.

Development final scores are recorded, but matching native development
baselines are unavailable in these reports. The native-to-learned percentage
gains above are calibration evidence and must not be relabeled as held-out gains.

Testing during the Beta7 development period informed improvements to penalty
screening, the shared optimizer and guarded polish, with gains in local
reconstruction and search efficiency. The measurements above describe the
completed release; generated-output quality was separately assessed through
the operator's ComfyUI acceptance.

## Actual accepted map

| HQ matrix family | W6 g16 | INT8 |
|---|---:|---:|
| QKV | 45 | 5 |
| OUT | 0 | 50 |
| FC1 | 45 | 5 |
| FC2 | 0 | 50 |
| Total | 90 | 110 |

All OUT/FC2 and every main matrix at blocks 0/1/47/48/49 use INT8. QKV/FC1 at
blocks 2–46 use W6 g16. This is a fixed HQ map; no compact allocation or W4
candidate contributes to this artifact. The forthcoming compact release needs
its own completed map, measurements and acceptance.

## Artifacts, validation and acceptance

| Property | Accepted Beta7 HQ |
|---|---|
| File | `10Eros_Max_h3_8stepTURBO_beta7_activation_learned_HQ.safetensors` |
| Bytes / decimal GB | 18,691,644,302 / 18.691644302 |
| Reduction from source | 53.53% |
| SHA-256 | `01a696efc96708f3edd15ff20fa3f56068974ba08a1b4c5801cef2bd49600ad7` |
| Acceptance | Operator ComfyUI testing, 2026-10-28 |

Mechanical validation passed for source binding, selected candidate identities,
serialized layout/metadata, preserved tensors and output integrity. Assembly
consumed learned candidate caches without additional optimization. The operator
then tested several ComfyUI generations and accepted runtime behavior and
perceived quality near or equal to the native INT8 HQ companion. Observed
memory/speed benefits were not quantified. There was no blinded multi-rater,
PSNR/SSIM or exact BF16-teacher generated-output comparison.

The checkpoint and `.conversion.log`, `.progress.json`, `.quantization.json`
and `.sha256` sidecars were renamed from the Test3 prefix to the final Beta7
name. Checkpoint bytes, JSON records and digest were preserved; only the checksum
sidecar's filename field changed. Historical campaign inputs and stage records
retain the Test3 paths, mapped in the campaign guide. No payload hash was rerun
for the rename or this documentation update.

Source-specific evidence remains in the project under `campaigns/h3/beta7-test3/`
and `benchmarks/h3/beta7-test3/successor/stages/`: W6 population `f0c407db0d67254e`,
INT8 population `6bc7b08b1869516e`, and the assembly, validation and operator
acceptance stage records. The campaign guide records the final release rename.

## Runtime and attribution

Use ComfyUI with native W6A8 and INT8 ConvRot support, and compatible upstream
H3 text encoder, video/audio VAEs and Turbo workflow. W6 support is documented in
[Comfy Kitchen PR #191](https://github.com/Comfy-Org/comfy-kitchen/pull/191) and
[ComfyUI PR #16483](https://github.com/Comfy-Org/ComfyUI/pull/16483), available from
ComfyUI v0.38.0. Use the source's current workflow guidance rather than assuming
capture resolution restricts generation.

The recorded learning/acceptance runtime was Python 3.13.12, PyTorch 2.14.1+cu132,
comfy-kitchen 0.2.39, safetensors 0.8.0 and Triton Windows 3.8.0.post29.
These identify the campaign environment, not exact inference dependencies.
The [sample workflow folder](https://huggingface.co/LokkenJP/TenEros_Max_optimized_learned/tree/main/SampleWorkFlowTwoPassOptimized)
provides two-pass video/audio generation and refinement workflows. H3 audio
waveform decoding uses the integrated decoder in its audio VAE.

Licensing and content designation follow the upstream source and its applicable
terms, including the
[MiniMax H3 Community License Agreement](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE).
The [model card](https://huggingface.co/LokkenJP/TenEros_Max_optimized_learned/blob/main/README.md)
provides checkpoint downloads and usage guidance. The
[quantization project](https://github.com/LordLocksley/ltx23-10eros-fp8-quantization)
retains implementation and source-specific evidence. This release's results
must not be transferred to other sources or the pending compact checkpoint.
