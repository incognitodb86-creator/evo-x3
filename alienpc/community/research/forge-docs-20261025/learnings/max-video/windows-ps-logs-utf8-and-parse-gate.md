---
title: AlienPc PowerShell 5.1 writes UTF-16 logs, and every .ps1 needs a parse check before launch
tags: [max, harness]
date: 2026-10-09
source: 60_reviews/2026-10-09-max-60s-continuity-plan-review.md
---
- In Windows PowerShell 5.1, Tee-Object -Append and *>> write UTF-16LE, so UTF-8 readers (Python, rg) can miss markers (review R24). Use Add-Content -Encoding UTF8 and Out-File -Append -Encoding utf8.
- The box has no pwsh, so a .ps1 can't be parse-checked here. The hard gate is [System.Management.Automation.Language.Parser]::ParseFile on AlienPc by the lease holder with 0 errors before Start-Process (R9). Today's earlier $P/$p variable clash shows why.
- Small script traps found in the same review: a stale glob prefix (MAXRIFE_ vs MAXDYN_), an unguarded cands[-1], --only with no done predecessor, a dry run writing into the real Comfy input folder, and apad silence when the pick is the last frame (R15-R19).
