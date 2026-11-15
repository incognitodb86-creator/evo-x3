# EVO-X3 Orchestrator: implement the whole plan (Max Architect 3, Nov 14 2026)
Derrick t1589u/t1591u: "use antigravity x3 to implement the plan" and "give it the entire plan and have it implement all of it".

You are Antigravity running ON the EVO-X3 (Windows 11 now, user derek). Source of truth:
- C:\evo-x3\2026-11-11-evo-x3-setup-plan.md (plan rev 8)
- C:\evo-x3\2026-11-13-antigravity-evo-x3-stage-brief.md (brief rev 5; its "Hard stops" are binding; brief wins on conflict)

Implement every unit of the plan, in the plan's order, as far as this machine allows. Keep going on later steps that don't depend on a blocked step. Record each unit's pass test with America/Chicago times in C:\evo-x3\records\. Never invent sizes, digests, tok/s or menu labels: measure or leave a hole.

## Order
0. FIRST, connectivity and backup (Derrick t1592u: "setup tailscale gitea ect on the computer so we can backup everything to qnap"):
   a. Clock: this PC reads about 15 h ahead and the Windows Time service (w32time) is stopped. Set the time zone to Central Standard Time, start w32time, and run `w32tm /resync`. These need admin: try with `Start-Process -Verb RunAs` (Derrick will click the UAC prompt on this screen). If it is still not elevated, record the exact commands as BLOCKED-ON-DERRICK and continue.
   b. Install Git (`winget install -e --id Git.Git`) and Tailscale (`winget install -e --id Tailscale.Tailscale`) from official winget sources, accepting agreements. Then run `tailscale up` (or open the Tailscale app). Derrick completes the sign-in in the browser on this screen; never use or create an auth key yourself. Wait up to 15 min, polling `tailscale status`, for the tailnet tailf242b2.ts.net and for `qnap.tailf242b2.ts.net` to resolve.
   c. `git init` C:\evo-x3 (with a .gitignore excluding iso\, drivers\, *.img, *.gguf, runs\*\agy.log). Commit the plan, brief, stage and records as "EVO-X3 Orchestrator". Add the remote `gitea` = https://qnap.tailf242b2.ts.net/derrick/evo-x3.git. Push only if the repo exists and Git Credential Manager gets credentials Derrick types; otherwise record BLOCKED (Household is creating the repo). Never write credentials into files or onto command lines.
   d. QNAP backup target: once Household names the SMB share, it goes in C:\evo-x3\records\qnap-target.md. Until then, record the backup steps (drivers export, stage tree, the later Clonezilla image) as waiting on that share. Do not guess a share name or space.
1. Phase A (A1, A2, A4) -> C:\evo-x3\stage\. A3 model downloads: DEFERRED (QNAP space unconfirmed); put the download list in the runbook.
2. B0/U1 inventory (read-only): RAM, BIOS version, disk, partitions, ESP free, C: used, BitLocker/device-encryption state, Secure Boot, Fast Startup/hibernation, NICs + link speed, Windows build.
3. U2 prep you can do safely: `pnputil /export-driver * C:\evo-x3\drivers`; download (official sources, verify published checksums) the Fedora 44 Server x86_64 ISO and the current stable Clonezilla live ISO into C:\evo-x3\iso\; write exact USB/imaging steps for Derrick.
4. B2 reversible Windows prep: Fast Startup off, `powercfg /h off`, RTC UTC (`RealTimeIsUniversal=1`), Windows Update to manual/paused. Record before/after values so each can be undone.
5. Write C:\evo-x3\stage\fedora-bootstrap.sh: on first Fedora boot it installs agy via `curl -fsSL https://antigravity.google/cli/install.sh | bash`, copies the stage tree, and lists exactly which plan units (U5 onward incl. U6 bake-off, U7, U9-U20) to run next, so the next Orchestrator run on Fedora continues from there.
6. Secret scan of C:\evo-x3\stage (gitleaks from the official release, else the brief's dry grep). Record it.
7. C:\evo-x3\RESULT.md: every plan unit with status DONE / BLOCKED-ON-DERRICK / NOT-YET (Fedora), pass test results, and a numbered list of exactly what Derrick must do next, in order.

## STOP points (do not do these; list them for Derrick)
- Anything with BitLocker (decrypt) before Derrick confirms its recovery key is in Vaultwarden. Never print or copy a recovery key.
- Writing any USB stick (recovery USB, Clonezilla, Fedora installer): needs Derrick to plug in and name the drive.
- The full-disk image (needs Clonezilla boot + QNAP folder from Household).
- Shrinking C: / any partition change: needs Derrick's resize card after a verified image.
- BIOS changes, boot order, bcdedit, installing Fedora.
- Tailscale Serve/ACL, API keys (Derrick types them), the tools port.
- Model downloads (QNAP space), anything costing money.
- Do not touch AlienPc, the QNAP or other machines. Write only under C:\evo-x3\ (plus the reversible Windows settings in step 4).
