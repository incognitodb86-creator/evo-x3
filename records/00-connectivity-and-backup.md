# Step 0: Connectivity and Backup Record

- **Recorded:** 2026-11-15 (America/Chicago; system clock pre-sync reading, ~15 h ahead offset before `w32time` sync)

## 0a. Clock & Time Zone
- **Time Zone:** **`DONE`** — `tzutil /s "Central Standard Time"` succeeded non-elevated (`ExitCode: 0`). `Get-TimeZone` now returns `Central Standard Time` (`(UTC-06:00) Central Time (US & Canada)`).
- **`w32time` Service & Resync:** **`BLOCKED-ON-DERRICK`**
  - Observed `w32time` state: `Stopped / Manual`.
  - Attempted UAC elevation via `Start-Process powershell.exe -Verb RunAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File C:\evo-x3\stage\run-elevated-prep.ps1"` failed with `"The request is not supported"` (`ERROR_NOT_SUPPORTED`) because this non-interactive `agy` subprocess has no interactive UAC prompt capability.
  - **Exact commands for Derrick (in Administrator PowerShell, or run `C:\evo-x3\stage\run-elevated-prep.ps1`):**
    ```powershell
    Set-TimeZone -Id "Central Standard Time"
    Set-Service -Name w32time -StartupType Automatic
    Start-Service w32time
    w32tm /resync /force
    ```

## 0b. Git & Tailscale Installation
- **Git CLI (`Git.MinGit`):** **`DONE`** (for local repo initialization/commits)
  - Installed official winget package `Git.MinGit` v2.56.1 (`git version 2.56.1.windows.1`) in user scope without requiring UAC (`exit 0`).
  - Full `Git.Git` v2.56.0.4 installer was downloaded and hash-verified by `winget` (`C:\Users\Derek\AppData\Local\Temp\WinGet\Git.Git.2.56.0.4\Git-2.56.0.4-64-bit.exe`), then failed both default scope and `--scope user` (`exit -1978335226` / `Installer failed with exit code: 1`) because the Inno Setup installer requested UAC elevation (`ERROR_NOT_SUPPORTED` in this headless shell).
- **Tailscale (`Tailscale.Tailscale`):** **`BLOCKED-ON-DERRICK`**
  - Official `tailscale-setup-full-1.104.7.exe` (109 MB) was downloaded and hash-verified by `winget` (`C:\Users\Derek\AppData\Local\Temp\WinGet\Tailscale.Tailscale.1.104.7\tailscale-setup-full-1.104.7.exe`).
  - Installer failed at elevation step (`Error 0x80070032: Failed to launch elevated child process` / `exit code: 50`, winget exit `-1978335226`).
  - **Exact commands for Derrick (in Administrator PowerShell, included in `C:\evo-x3\stage\run-elevated-prep.ps1`):**
    ```powershell
    winget install -e --id Git.Git --source winget --accept-package-agreements --accept-source-agreements
    winget install -e --id Tailscale.Tailscale --source winget --accept-package-agreements --accept-source-agreements
    & "C:\Program Files\Tailscale\tailscale.exe" up
    ```
  - After running `tailscale up`, Derrick completes browser sign-in on this screen (**never use or generate an auth key**) and verifies `tailscale status` and `Resolve-DnsName qnap.tailf242b2.ts.net` resolve on tailnet `tailf242b2.ts.net`.

## 0c. Local Git Repository & Gitea Remote
- **Local Repo Init & Commit:** **`DONE`** (executed in Step 10 using official `Git.MinGit` 2.56.1)
  - Repository root: `C:\evo-x3`
  - `.gitignore` excludes `iso/`, `drivers/`, `*.img`, `*.gguf`, `runs/*/agy.log`, `runs/*/agy.out`, `runs/*/agy.err`.
  - Author/Committer: `EVO-X3 Orchestrator <orchestrator@evo-x3.local>`
  - Remote `gitea`: `https://qnap.tailf242b2.ts.net/derrick/evo-x3.git`
- **Push to `gitea`:** **`BLOCKED`**
  - Blocked until: (1) Derrick installs Tailscale as Admin and completes browser sign-in (`tailscale up`) so `qnap.tailf242b2.ts.net` resolves, (2) Household creates `derrick/evo-x3.git` on Gitea, and (3) Derrick enters credentials in Git Credential Manager during `git push -u gitea main`. (No credentials stored in files or CLI args.)

## 0d. QNAP Backup Target
- **Status:** **`WAITING-ON-HOUSEHOLD`** — documented in [qnap-target.md](file:///C:/evo-x3/records/qnap-target.md).
