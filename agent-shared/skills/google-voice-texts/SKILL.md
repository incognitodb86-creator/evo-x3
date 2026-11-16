---
name: google-voice-texts
description: Use when Derrick asks to read his Google Voice texts, send one text, or look up a contact. Texts only, one at a time, each after his exact yes. pi does not place Voice calls.
---

# Google Voice texts + contacts (read-only)

Plan: brain 40_projects/max-fix-tests/plans/2026-10-30-pi-google-voice-plan.md (approved 8:47 PM CT 2026-10-30). Derrick 8:49 PM CT: "pi skips calls and only sends texts".

- Route: your browser (pi-browser-use, the pi-only Chrome profile C:\Users\derek\.pi\browser-profile) at https://voice.google.com/u/0/messages. No Grok/Imagine sign-in in that profile; never open Imagine.
- No calls: pi does not place Voice calls (no dialing, no call button), even if asked. Say so.
- Read: list threads; inbound texts are read only, never auto-replied.
- Send one text: 1) draft the recipient and the exact text; 2) show both to Derrick and ask "Send this exact text?"; 3) only after his exact yes for THAT message, click Send once; 4) confirm it shows as sent. Any change to the text = ask again. No loops, no bulk, no scheduled or follow-up texts.
- If Voice shows a sign-in page, stop and tell Derrick to sign in himself in that browser window; never type his password.
- Not while /home/evo/AI/locks/gpu-render.lock exists if the step needs desktop control.
- Privacy: never write phone numbers, contact names or message text into logs, notes, actions.log or files. Records say only "text sent (approved)" or "contact found / not found".
- Contacts: read-only Google Contacts MCP (workspace-mcp --tools contacts --read-only) once Derrick finishes the Google sign-in; until then say contacts are not connected.
- Google's rules ban automated messaging; Derrick accepted that risk only for texts he approves one at a time.