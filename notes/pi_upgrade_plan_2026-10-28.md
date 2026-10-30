# Pi upgrade plan (saved 2026-10-28 10:12 AM CT)
Nothing below is applied until Derek says go. No Pi restart mid-test. One change at a time, with a backup first.

Phase 1: models.json context/max_tokens/sampling, YOLO mode (config saved, loads at next Pi restart), safety rules.
Phase 1b: Humble Pi server flags and pi-plate, only when no render is running.
Phase 1c (added 2026-10-28, media to chat) - PLAN ONLY:
  - Stills: Pi uses `read` on the finished PNG/JPEG; pi-mobile 0.4.0 shows it inline (Pi downsizes to 2000px/4.5MiB and the image costs model tokens). Nothing to install.
  - Video and full-quality files: Tailscale-served dedicated folder, e.g. C:\renders\share:
      tailscale serve --bg --https=443 --set-path=/renders C:\renders\share   (use --https=8443 if it clashes with pi-mobile's serve)
      off: tailscale serve --https=443 --set-path=/renders off
    Add one AGENTS.md line: copy finished files into that folder and reply with https://<pc>.<tailnet>.ts.net/renders/<file>.
    Risk: every tailnet device can read the folder; use ACLs if others are on the tailnet. Untested alongside pi-mobile's serve.
  - Own-fictional-character clips only; nothing goes to anyone else; nobody views the files.
  - Skip: Telegram bridges (pi-telegram, pi-telegram-plus, @comput/pi-telegram), pi-web-ui, Clever Cloud relay, NAS/SMB links.
  - Optional later: ~20-line extension tool returning an image block (self-written, reviewable); no video.
Phase 2: cc-safety-net, rpiv-todo, pi-plan-mode, pi-lsp, one test at a time with backups.
Phase 3: pi-ralph-wiggum, pi-llama-cpp, pi-memory, pi-fff, finally the @gotgenes permission-system fork. pi-subagents capped at one at a time; skip pi-task and cloud-leaning packages.
