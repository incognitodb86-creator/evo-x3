# Step 0d: QNAP Backup Target

- **Recorded:** 2026-11-15 (America/Chicago; system clock pre-sync reading, ~15 h ahead offset before `w32time` sync)
- **Status:** `WAITING-ON-HOUSEHOLD`
- **Target Share Name:** `NO_DATA` (waiting on Household to name the SMB share and confirm free space)
- **Pool Condition (Brief rev 5 Hard Stop):** QNAP Data pool is **degraded until HDD2 is replaced**. A **second copy of backup images** must be kept somewhere else off the degraded pool. Do not fill the last of the pool.

## Backup & Staging Items Waiting on Household Share Confirmation
1. **Exported Windows drivers (`C:\evo-x3\drivers\`):** copy alongside the U2 image once `pnputil /export-driver` completes with Admin rights and share is named.
2. **Staged Fedora setup tree (`C:\evo-x3\stage\`):** copy to QNAP staged folder once share is named.
3. **U2 Full-Disk Clonezilla Image (`nvme0n1` — all 5 partitions incl. ESP & Recovery):**
   - Factory `C:` used space measured at **78.37 GiB** (`1831.46 GiB` total, `1753.09 GiB` free), plus `BACKUP_OS` (30.27 GiB, ~0.43 GiB used), `Recovery` (1.17 GiB, ~0.82 GiB used), and ESP (100 MiB).
   - Plan Q11/U2 requires **≥ ~100 GB** (or ≥ 1.5× `C:` used ≈ **118 GiB**), **plus** a second off-pool copy location.
4. **A3 Deferred Model Downloads (copy/download only after Household confirms space on top of U2 image):**
   - `Qwen3.8-Flash-Next` (`unsloth/Qwen3.8-Flash-Next-GGUF`, `UD-Q4_K_XL`): **111.3 GB** + shared Q8_0 MTP head **2.79 GB** (Plan U10 noted ~130 GB for cold copy).
   - `Gemma 4 26B A4B Heretic`: **NO_DATA** (measure actual file size on Hugging Face / local download before copying; do not invent size).
   - `Qwen3.8-27B` (`unsloth/Qwen3.8-27B-GGUF`, `UD-Q4_K_XL` fallback): **17.6 GB** (optional on QNAP if space allows).
