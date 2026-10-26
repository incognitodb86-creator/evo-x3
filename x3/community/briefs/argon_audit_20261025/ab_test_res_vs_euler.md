# A/B Test Evaluation: res_multistep vs euler (Seed 51150011)

**Date:** 2026-10-26 08:44 CT  
**Target Graph:** `ali163_hc15_bd002`  
**Fixed Seed:** `51150011` (Noise seed: `51150001`)  
**Resolution:** 1344x768  
**Frame Count:** 362 frames (15.083 seconds @ 24 fps)  
**Attention Backend:** `pytorch attention` (official H3 community standard)  
**Hardware:** AlienPC (NVIDIA RTX 4080 / 16 GB VRAM)

---

## Technical Metrics Comparison

| Metric | `res_multistep` (`ali163_s8_pytorch_s51150011`) | `euler` (`ali163_s9_euler_s51150011`) | Delta / Notes |
| :--- | :--- | :--- | :--- |
| **Status** | OBJECTIVE OK (`rc=0`) | OBJECTIVE OK (`rc=0`) | Identical completion |
| **Sampling Runtime** | 780.4 s (13.01 min) | 780.3 s (13.00 min) | -0.1 s (<0.02% difference) |
| **Output Frames** | 362 frames | 362 frames | Exact match |
| **Output Duration** | 15.083 s | 15.083 s | Exact match |
| **Resolution** | 1344 x 768 | 1344 x 768 | Exact match |
| **File Size** | 6,260,213 bytes (6.26 MB) | 5,796,643 bytes (5.80 MB) | Euler is ~7.4% smaller file size |
| **Audio Track** | True | True | Audio generated and synced |
| **Black / Frozen Frames** | `[]` (0 detected) | `[]` (0 detected) | 0 defective frames |
| **Prompt ID** | `7e72d265-7526-4f4b-ac62-a05767f1d2cd` | `49ecf49e-cd10-4762-b909-2435ad75e62a` | Distinct runs |
| **Contact Sheet** | `runs\ali163_s8_pytorch_s51150011_stills_contact.png` | `runs\ali163_s9_euler_s51150011_stills_contact.png` | Valid |

---

## Technical Conclusion & Default Policy

1. **Performance:** Both samplers perform at virtually identical runtime speeds on this hardware (~780.3 seconds for 362 frames at 1344x768).
2. **Technical Quality:** Both produced valid, objective-passing MP4 files with zero black or frozen frames and complete 15.08s playback.
3. **Default Policy:** Per Derrick's explicit directive (Oct 25 6:48 PM: "Go back to Euler..."), `euler` remains the active default in `comm.py:107` (`g["ksel"] = {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}}`). Derrick retains final decision on whether to adopt `res_multistep`.
