---
title: One holder for the AlienPc Shell lease and each browser seat, named before use
applies_when:
  - running commands on AlienPc or queueing local video work
  - using a browser seat or Chrome profile for Imagine
  - handing Max work to another bot
tags: [max, lease, shell, seat, alienpc]
---

Only the holder named in the latest AlienPc lease file (brain-staging/30_handoff/status/*lease*) runs Shell on AlienPc; Sydney/Max Architect (24f66698) is the AlienPc lease holder and Forge's director: Max sets up, briefs, tunes and checks Forge; Forge does the work, including renders; Max never renders, kills passes, or ticks Forge items himself, and if Forge is stuck Max writes one brief line and reports (Derrick, Oct 22 3:21 PM and Oct 23 9:56 AM, 12:31 PM, 1:48 PM CT; moved here from old the standing rules on 2026-10-23, moved here when the rules were cut to 5). Max takes the lease for Forge's runs, then releases it cleanly with work saved; no second bot runs Shell on that PC at the same time. Each browser seat has one named holder, and a handoff says if a lease or seat moves. Production KEEP files, argv and locks are never swapped, stripped or "improved" without Derrick's GO. Lease procedure: alienpc-local-exec-lease.

Exception (2026-10-23 10:37 AM CT, Derrick: "Yes, give Household finance-only AlienPc access and move the rebuild fully", then "Also for unifi project"): Household (81ae1a53) may work on AlienPc only in the finance app folders (live D:\Apps\finance-app on :3100; rebuild D:\Apps\finance-app-rebuild and scratch D:\Apps\_forge\finance-rebuild on :3101) and the UniFi project folder (name it on ALI-164 before first use). It takes the lease first every run (alienpc-local-exec-lease), waits for Max's release line, and hands back after. Never ComfyUI, llama-swap, GPU jobs, Forge GPU runs or the video stack.

Update (2026-10-25 8:26 AM CT, Derrick via Household widget answer: "Yes: the finance exception covers the C:\Apps finance-app folders, and the daily import gets a standing 7:00-7:30 AM AlienPc window"): the finance exception also covers C:\Apps\finance-app-rebuild, C:\Apps\_forge\finance-rebuild\import and staging C:\Users\derek\_finance_import_stage. Household's daily Shoebox import holds a standing AlienPc lease window from 7:00 to 7:30 AM CT for that importer only; outside it, Household asks Max for a lease.
