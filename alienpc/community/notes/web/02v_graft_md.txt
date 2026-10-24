# H3 Cross-Model Graft Methodology

Technical write-up of the graft toolchain for the 10Eros H3 checkpoints. Covers the architecture-level graft operations for Krea 2 and Wan 2.2 donors into the H3 (Minimax) video model, the unfusing/refusing process, band-level empirical findings, and the mathematical case for why the results are structured character transfer rather than arbitrary weight perturbation.

## What This Is (and Isn't)

**What it is:** a structured cross-architecture transfer of learned weight subspaces from source video/image models (Krea 2, Wan 2.2) into H3's parameter space, respecting H3's architectural decomposition (attention heads, MLP inner dimensions, block ranges) and preserving H3's operational magnitudes.

**What it isn't:** random weight noise dressed up as fine-tuning. Every operation targets an architecturally meaningful substructure. The graft mappers know that Krea Q has 48 heads × 128 dims, that Wan MLP is standard `ffn.0/ffn.2` not SwiGLU, that H3's token refiner is fused QKV but main blocks are unfused triplets. Random perturbation cannot preserve base capabilities, cannot compose across donors, and cannot show the differential band sensitivity we observe empirically.

The output artifacts are unambiguously honest: safetensors files with metadata identifying the graft source, patch files that record exactly which base tensors were modified, LoRAs extracted via well-defined SVD operations, and merge scripts whose math is inspectable. Nothing is a black box.

---

## Architecture Summary

### H3 (target)

- **Token refiner** (text refinement stack, 2 blocks): FUSED attention `token_refiner.blocks.N.attn.qkv_proj` (single tensor with Q, K, V concatenated), MLP with SwiGLU (`mlp.fc1` produces both value_half and gate_half in rows 0-14335 and 14336-28671, `mlp.fc2` is the down projection). 5376 hidden, 56 heads × 128 head_dim.
- **Main blocks** (denoising stack, 50 blocks): UNFUSED attention (separate `blocks.N.attn.q_proj`, `k_proj`, `v_proj`, `out_proj`). Same 5376 hidden × 56 heads × 128 head_dim.

Different attention layouts in the same model are unusual but real. The token refiner is small enough that fused QKV batched matmul is efficient; main blocks are large enough that fusion adds no gain.

### Krea 2 (donor)

- 28 blocks × 6144 hidden × 48 Q heads with **grouped-query attention (GQA 4:1)** — K and V have only 12 heads (1536 rows each).
- Attention naming: `attn.wq`, `attn.wk`, `attn.wv`, `attn.wo` (LLM-style).
- SwiGLU MLP: `mlp.up`, `mlp.gate`, `mlp.down`.

### Wan 2.2 (donor)

- 40 blocks × 5120 hidden × 40 heads × 128 head_dim (no GQA).
- Attention naming: `self_attn.q`, `self_attn.k`, `self_attn.v`, `self_attn.o` (no `_proj` suffix).
- Standard MLP: `ffn.0` (up), `ffn.2` (down). Also has bias tensors on attention and MLP; H3 has `bias=False` throughout, so Wan biases are discarded during graft.

### Coverage into H3

Real dimensions matter for honesty about what a graft can and cannot transfer:

| Donor | H3 refiner cols | H3 refiner Q heads | H3 refiner K/V heads |
|-------|-----------------|--------------------|----------------------|
| Wan 2.2 | 95% (5120/5376) | 71% (40/56) | 71% |
| Krea 2 | 87% (5376/6144, truncated) | 86% (48/56) | 21% (12/56, GQA limits us) |

Krea's 6144 hidden > H3's 5376 forces column truncation: Krea's cols 5376-6143 are dropped during graft. This is stated in the mapper docstring, not hidden. Krea's SwiGLU MLP inner is 16384 vs H3's 14336 — same truncation applies to MLP tensors.

---

## The Unfusing Process

H3 ships two forms of the same checkpoint:

- **Fused** (`minimax_h3_fl2va_pruned_bf16.safetensors`): production runtime file with fused attention where the architecture permits, loaded by ComfyUI's H3 nodes.
- **Unfused**: separate Q/K/V tensors even in the token refiner. This is the form the graft mappers write to.

Working unfused matters because per-head and per-band grafts require addressable Q, K, V tensors. You cannot graft only Q while leaving K and V untouched if the base file stores them concatenated.

### The refuse step

After grafting into the unfused base, `apply_patch_and_refuse.py` reads the modified unfused tensors and produces a fused runtime file:

```
token_refiner.blocks.0.attn.q_proj  ┐
token_refiner.blocks.0.attn.k_proj  ├─→ token_refiner.blocks.0.attn.qkv_proj
token_refiner.blocks.0.attn.v_proj  ┘
```

This is a `torch.cat` on axis 0 (Q rows | K rows | V rows). Mathematically equivalent to the original fused layout, but the intermediate unfused form allowed selective per-band modification.

For main blocks (unfused in both forms), no refuse is needed.

### patches_to_lora.py fused-base auto-detection

When extracting a LoRA that will apply to the fused runtime base, the extractor detects that base has `attn.qkv_proj.weight` (single tensor) and automatically fuses the separate patch tensors before SVD extraction:

```python
if fused_qkv_in_base:
    delta_q = base_q - patch_q
    delta_k = base_k - patch_k  
    delta_v = base_v - patch_v
    delta_qkv_fused = torch.cat([delta_q, delta_k, delta_v], dim=0)
    # SVD on the fused delta produces one LoRA module per attention block
```

This is why the extracted LoRAs contain `lora_unet_token_refiner_blocks_0_attn_qkv_proj` (fused) even though the graft operated on separate q/k/v tensors — the LoRA targets the fused runtime base.

---

## Band-Level Grafts: Q, K, V, out_proj, MLP

Each attention band and MLP path is grafted independently with its own strength, mode, and orthogonality settings.

### Per-band function structure

From `graft_wan_to_h3_mainblock_unfused.py` and equivalents:

```python
def graft_single_band(h_band, donor_band, strength, mode, orthogonal, dev):
    # h_band: (7168, 5376) = 56 heads × 128 rows × 5376 cols
    # donor_band (Wan): (5120, 5120) = 40 heads × 128 rows × 5120 cols
    donor_view = donor_band.view(WAN_HEADS, WAN_HEAD_DIM, WAN_HIDDEN)
    for h in range(WAN_HEADS):
        r0, r1 = h * H3_HEAD_DIM, (h+1) * H3_HEAD_DIM
        c0, c1 = 0, WAN_HIDDEN
        h_patch = out[r0:r1, c0:c1].clone()
        d_patch = donor_view[h]
        blended, arc, rel = blend_patch(h_patch, d_patch, strength, mode, orthogonal)
        out[r0:r1, c0:c1] = blended
```

Each donor head is grafted into an H3 head slot as a rectangular subpatch. Slots beyond the donor's head count stay native. Columns beyond the donor's hidden dim stay native. This is per-head-per-column locality.

### Empirical band sensitivity

Findings from A/B testing across grafts:

- **K (main-block)**: breaks audio quality even at low strengths. Attention key projection controls what queries attend to; overwriting it with donor character disrupts H3's learned audio-token attention patterns. `--k-strength 0` is default.
- **K (refiner)**: empirical exception — at linear-mag mode, K graft on refiner blocks 0/1 does not audibly degrade output. Different structural role in the smaller refiner stack.
- **Q**: affects audio noticeably but recoverably. Query projection controls what representations query for. Grafting shifts what H3 looks for but doesn't corrupt the attended-to material.
- **V**: does not visibly affect audio. Value projection carries the semantic content of attention. Grafting V is the safest attention band for character transfer.
- **out_proj**: half-strength default (0.2 vs 0.45 for Q/V). Structural mixer — affects how head outputs combine into the residual stream. Sensitive at full strength.

**Sensitivity ranking**: K > out_proj (half-strength) > Q > V.

This differential sensitivity is definitive evidence that the graft is architecture-aware. If it were pure weight noise, every band would behave equivalently.

### MLP grafts

For Wan (standard MLP): `ffn.0` → H3 fc1 value_half (rows 0-14335), truncating Wan's inner dim if needed. Optional `ffn.2` → H3 fc2. H3 gate_half stays native since Wan has no gate.

For Krea (SwiGLU): `mlp.up` → H3 fc1 value_half, `mlp.gate` → H3 fc1 gate_half, `mlp.down` → H3 fc2. Both halves receive Krea character.

The `fc2` observation: grafting fc2 provides very impactful character transfer BUT fc2 carries dialogue/speech pattern encoding — grafting it degrades speech quality. Similar structural role to K but on a different pathway. `--include-fc2` off by default.

---

## Head Slots and Block Ranges

Attention head placement into H3's 56 slots is explicit and configurable.

```
--head-slots 10:50    # H3 heads 10 through 49 receive donor content
--h3-blocks 20:50     # H3 blocks 20 through 49 are grafted
--h3-peak 34          # ramp peak strength at block 34
--donor-shift 6       # donor blocks start at index 6
```

Head slot placement lets you position Wan character on slots 10:50 while a Krea graft on slots 0:15 doesn't overlap. Cross-model composition without collision.

Block range restriction matters for detail preservation. Grafting the last 6 blocks of H3 (44-49) — which specialize in fine detail synthesis matching H3's VAE — with donor MLP tensors that don't match H3's VAE causes aliasing/resolution loss without changing character. Empirically confirmed: restricting `--mlp-blocks` to 20:38 while keeping attention on 20:50 preserves character AND fixes aliasing.

### Ramp shapes

Strength ramping across the block range: `uniform`, `linear`, `linear-up`, `linear-down`, `gaussian` centered at `--h3-peak`. Late-block emphasis is typical because that's where character rendering happens; early-block heavy grafts disrupt structural formation.

---

## Graft Modes

Each per-band call selects a blend mode:

### `linear` mode

```python
blended = h_patch + strength * donor_patch
```

Standard additive perturbation. Fastest, but donor magnitude can dominate H3 magnitude at high strengths, causing cross-tensor amplitude imbalance.

### `residual` mode

```python
diff = donor_patch - h_patch
blended = h_patch + strength * diff
```

Adds only the delta between donor and base. When donor and base are similar, residual mode has less effect than linear at the same strength (because `diff` is smaller). When they differ, effect is similar. Useful for cross-model grafts where donor and base weights are structurally different.

### `linear-mag` mode (the empirical favorite)

```python
donor_norm = donor / (||donor|| + eps)
h_norm = h_patch / (||h_patch|| + eps)
blended_direction = (1-s) * h_norm + s * donor_norm
blended = blended_direction * ||h_patch||   # preserve h_patch magnitude
```

Rotates the H3 patch in the direction of the donor while preserving the H3 patch's original magnitude. Prevents amplitude cascade through the network (small magnitude drift per block compounds through 50 blocks into visible degradation). Empirically produced the cleanest character transfers in TenStrip's A/B testing.

The user-observed pattern: linear at strength 0.45 produces character transfer with amplitude drift and aliasing. Linear-mag at the same strength produces the same character transfer without drift.

---

## Orthogonal Projection

Optional per-band, applied inside `blend_patch`:

```python
if orthogonal:
    # Project donor perpendicular to h_patch
    proj = (donor · h_patch / ||h_patch||²) * h_patch
    donor_perp = donor - proj
    donor_effective = donor_perp
```

The intent: strip the component of donor that aligns with H3's existing direction, keeping only what donor knows that H3 doesn't. Prevents redundant reinforcement.

Compose with linear-mag: `--orthogonal --mode linear-mag` gives a magnitude-preserving rotation into donor's directions that don't already exist in H3.

**Empirical measurement across a 14-pass Anima cycle**: arc between donor and H3 = 90°, relative residual = 0.35, constant across all passes. Cross-model deltas are inherently near-perpendicular to H3's principal directions in weight space (this is what "cross-model" means — the models learned different feature bases). Orthogonal projection has small effect when donors are already perpendicular; it becomes significant only when donor and base share structural directions.

---

## Cycle Mode

`--cycle-all`: iterate the donor's block range over the target's block range in overlapping pairs. Example with Anima (28 blocks) → H3 refiner (2 blocks):

- Pass 1: Anima blocks (0,1) → H3 refiner (0,1)
- Pass 2: Anima blocks (2,3) → H3 refiner (0,1)  (accumulates on Pass 1's output)
- ...
- Pass 14: Anima blocks (26,27) → H3 refiner (0,1)

Each pass sees the accumulated state from previous passes. Total effective magnitude ≈ √N × per-pass magnitude for orthogonal contributions (random walk geometry). 14 passes at strength 0.35 per pass gives ~1.3 effective total magnitude spread across a broad donor-blocks subspace.

Result: rather than cramming one donor block's character into H3 at high strength, cycle mode distributes character extracted from the donor's full block range at moderate strength. Empirically produces more balanced character transfer than single-pass concentrated grafts.

Similar cycle counts: Wan (40 blocks) → 20 passes, LTX (8 blocks) → 4 passes, Krea (28 blocks) → 14 passes.

---

## The Patch Workflow

The full pipeline:

```
graft_wan_to_h3_mainblock_unfused.py
  ↓ produces
wan_mainblock_patch.safetensors    (only modified tensors + metadata)
  ↓
graft_krea_to_h3_refiner_unfused.py --output-format patch
  ↓ produces  
krea_refiner_patch.safetensors     (only modified tensors + metadata)
  ↓
patches_to_lora.py --patch wan_mainblock_patch.safetensors krea_refiner_patch.safetensors
  ↓ produces
combined_lora.safetensors          (kohya-format LoRA)
  ↓
h3_loramerge.py base.safetensors loras.txt output.safetensors --merge-mode linear-mag-rowwise
  ↓ produces
final_h3_grafted.safetensors       (deliverable model)
```

### Patch files

Each mapper writes only the tensors it modified, tagged with metadata:

```python
patch_metadata = {
    "graft_source": "wan22_mainblock_to_h3",
    "wan_donor": "wan2.2_high_noise.safetensors",
    "h3_base": "minimax_h3_unfused.safetensors",
    "blocks": "20:50",
    "head_slots": "10:50",
    "donor_shift": "6",
    "cycles": "1",
    "modified_tensor_count": "150",
}
save_file(modified, args.output, metadata=patch_metadata)
```

Anyone can inspect these metadata fields with a safetensors reader. They record the actual graft parameters used.

### LoRA extraction via SVD

`patches_to_lora.py` computes `delta = base - patch`, then decomposes each delta via SVD:

```python
U, S, Vh = torch.linalg.svd(delta, full_matrices=False, driver='gesvd')
# Keep top-r singular components
lora_up = U[:, :r] * S[:r].sqrt()           # (out_dim, r)
lora_down = S[:r].sqrt().unsqueeze(1) * Vh[:r]  # (r, in_dim)
# Reconstruction: lora_up @ lora_down ≈ delta
```

Standard truncated SVD. `driver='gesvd'` is the stable LAPACK algorithm; the default `gesvdj` driver has a known Windows cuSOLVER crash on large tensors. `--fast` flag enables `torch.svd_lowrank` (randomized truncated SVD, ~10× faster) for iteration; `--fast` output should not be used for production because approximation error appears as high-frequency noise → aliasing in decoded output. Verified empirically.

The alpha value: `alpha = rank` produces `scale = 1.0` (kohya convention where `scale = alpha / rank`). At merge time, the LoRA is applied as `base + strength × scale × (up @ down)`.

---

## Merge Modes in h3_loramerge.py

Analogous to graft modes, but applied at the LoRA merge step:

### `linear` mode (standard)

```python
new_base = base + strength × depth_scale × (up @ down)
```

### `linear-mag` mode

```python
tmp = base + strength × depth_scale × (up @ down)
new_base = tmp × (||base|| / ||tmp||)   # rescale to preserve base magnitude
```

Rotation-with-magnitude-preservation at the merge level. When delta is perpendicular to base and strength=1, rotation is 45°; approaches 90° max as strength → ∞. Bounded rotation semantics for the strength parameter.

### `linear-mag-rowwise` mode

Same as `linear-mag` but applied independently per output row:

```python
tmp = base + delta
base_norms = base.norm(dim=1, keepdim=True)      # per-row base norm
tmp_norms = tmp.norm(dim=1, keepdim=True)         # per-row post-add norm  
new_base = tmp * (base_norms / tmp_norms)         # per-row rescale
```

For attention tensors laid out as (n_heads × head_dim, hidden), each row is one output dim within one attention head. Per-row magnitude preservation = per-head-per-dim magnitude preservation. Finest-grained preservation, cleanest character transfer, minimal aliasing.

Verified numerically: linear mode causes ~11% total magnitude drift under random perpendicular delta; linear-mag exactly preserves total magnitude (ratio = 1.0000); linear-mag-rowwise exactly preserves EVERY row's magnitude (ratios all = 1.0000, std = 0).

Per-LoRA overridable via the 5th column of loras.txt:
```
krea_char.safetensors 0.93 1.0:1.0 mag
wan_char.safetensors  0.69 0.8:1.2 mag-row
```

---

## Machine Learning Case

The core claim being challenged: is this real character transfer or dressed-up weight noise?

### 1. Weight matrices are learned bilinear maps, not opaque parameter bags

An attention weight tensor `W_Q ∈ ℝ^(d_out × d_in)` maps input activations `x ∈ ℝ^(d_in)` to query vectors `q ∈ ℝ^(d_out)` via `q = W_Q x`. The rows of `W_Q` define directions in input space that the query cares about. Reshaping into per-head slices `W_Q ∈ ℝ^(n_heads × head_dim × d_in)` makes each head's queries live in a `head_dim`-dimensional subspace.

Substituting a donor's per-head slice into a target's per-head slot replaces the direction basis that specific head uses. That's not noise. That's targeted subspace replacement.

### 2. Attention heads are (approximately) independent subspaces

This is the theoretical basis for multi-head attention. Heads specialize on different pattern types (positional, semantic, syntactic in language; spatial, temporal, textural in video). Replacing head `h` with a donor's head `h` at the same slot index means head `h` now attends to the patterns the donor's head `h` learned to attend to.

Sequential head slots are not interchangeable — head 3's slot is not the same as head 15's slot. Empirically confirmed by the `--head-slots` flag producing markedly different character depending on which target slots receive donor content.

### 3. Character transfer as directional rotation in weight space

Character in a generative model is not localized in specific parameter values. It's encoded in the directions that weight matrices attend to and produce. Two weight matrices with the same magnitude but different singular directions produce completely different outputs on the same input.

The linear-magnitude modes are designed around this fact: preserve the target's operational scale (magnitude), rotate the target's directions toward the donor's directions. The result is a weight matrix that operates on the same input scale as the original but responds to donor-like patterns.

Mathematically: for base `B` and delta `D`, the linear-mag merged result is `(B + D) × ||B||/||B + D||`. When `D ⊥ B`, this simplifies to `(B + D) / √(1 + ||D||²/||B||²)`, which is a rotation of `B` toward `D` by angle `arctan(||D||/||B||)`. Bounded, well-defined geometric operation.

### 4. Orthogonal projection preserves base capabilities

For orthogonal-projected delta `D_⊥ = D - (D · B / ||B||²) × B`, we have `D_⊥ · B = 0`. Adding `D_⊥` to `B` cannot reduce the response magnitude in any direction B was previously responsive to (Pythagorean theorem: `||B + D_⊥||² = ||B||² + ||D_⊥||²`).

This means orthogonal merges strictly ADD to base capabilities, they don't overwrite them. The base model retains its learned responses; the merged model additionally responds to donor directions perpendicular to base's principal directions.

### 5. Cycle mode: broad-subspace donor character via mutual orthogonality

Empirical measurement across a 14-pass Anima cycle showed arc = 90° and rel-res = 0.35 constant across all passes. Interpretation: donor blocks are mutually near-perpendicular in weight space. A single donor block occupies a narrow subspace; cycling through 14 blocks lets the donor character occupy a 14-dimensional (or thereabouts) subspace instead.

At per-pass strength `s` with N mutually orthogonal contributions, total effective magnitude scales as `s × √N` (random walk geometry) rather than `s × N` (colinear addition). For N=14, s=0.35, effective total ≈ 1.31 — spread across a 14-dim subspace.

Result: character grafted from cycle mode is broader and less concentrated than character grafted from a single high-strength pass. This produces the empirical difference users observe between cycle-mode outputs (balanced character across many styling aspects) and single-block outputs (concentrated character in one styling aspect).

### 6. The empirical band-sensitivity pattern proves architecture-awareness

If this were random weight perturbation:
- K vs Q vs V would behave identically (they're all attention projection matrices)
- Refiner K would behave identically to main-block K (same tensor type)
- out_proj would behave identically to Q at same strength

Instead we observe: K breaks audio, V is safe, out_proj is half-strength sensitive, refiner K is safer than main-block K. Every one of these differentials maps to the specific role that band plays in attention computation. Values carry semantic content, keys carry attention routing, queries carry query patterns. Different roles → different sensitivity to donor substitution.

No random-perturbation account can explain differential band behavior. Architecture-aware character transfer can.

---

## Honest Limitations

- **Cross-model graft LoRAs are not trained** — they don't have the calibrated magnitude of Kohya-trained LoRAs. Standard `linear` merge (what community LoRAs assume) produces amplitude drift. This is why the linear-mag modes exist.
- **Truncation is real information loss.** Krea's 6144 hidden > H3's 5376 forces dropping Krea's last 768 dimensions. Krea character encoded in those dimensions doesn't transfer.
- **GQA constrains Krea K/V coverage to 21% of H3 slots.** If your character work benefits from K/V-band grafts, Krea provides much less K/V surface area than Wan (71% coverage).
- **fc2 grafting degrades speech quality** (empirically). Default off. Enabling it produces stronger character but hurts audio.
- **Approximate SVD (`--fast`) produces aliasing.** Verified empirically. Iteration-only flag; production LoRAs use exact SVD.
- **Bias tensors are dropped.** Wan and Krea have attention/MLP biases; H3 doesn't. Bias character content is lost during graft.
- **The unfused base is a preprocessing artifact.** The runtime model is the fused base. All merging happens against the fused runtime file; the unfused form only exists for the graft operations themselves.

---

## Reproducibility

Every operation described here is exposed through CLI flags with documented semantics. The patch files carry metadata identifying every parameter used. LoRA files are standard safetensors in kohya format. The merger script accepts standard loras.txt input with per-LoRA overrides for strength, layer scale, normalize, and merge mode.

The full toolchain:

- `graft_wan_to_h3_refiner_unfused.py` / `_mainblock_unfused.py`
- `graft_krea_to_h3_refiner_unfused.py` / `graft_krea_to_h3.py`
- `apply_patch_and_refuse.py`
- `patches_to_lora.py`
- `h3_loramerge.py`

Anyone reproducing these operations with the same donor and base files will get equivalent output (modulo SVD's rank-truncation approximation, which is deterministic given the same driver and rank).

---

## Conclusion

The 10Eros H3 checkpoints are not the product of random weight noise applied to H3. They are the product of a structured cross-architecture transfer that respects H3's architectural decomposition (fused vs unfused attention, SwiGLU vs standard MLP, per-head geometry, block-range specialization), preserves H3's operational magnitudes (via linear-magnitude modes), and empirically demonstrates the band-differential sensitivity that only architecture-aware transfer can produce.

The math is standard linear algebra applied to well-understood transformer weight structures. The code is inspectable, the patch files carry provenance metadata, and the empirical findings (K breaks audio, V is safe, cycle mode broadens subspace occupation) are reproducible on any H3 base with any of the supported donor models.

This isn't a claim about state-of-the-art performance. It's a claim about honest methodology: what the toolchain does, why it does it that way, and what mathematical properties the results have. The results themselves should be judged on their own outputs.
