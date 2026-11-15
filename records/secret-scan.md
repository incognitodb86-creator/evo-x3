# Step 6: Secret Scan Record

- **Recorded:** 2026-11-15 (America/Chicago; system clock pre-sync reading, ~15 h ahead offset before `w32time` sync)
- **Tool:** Official `gitleaks` release `v8.30.1` (`gitleaks_8.30.1_windows_x64.zip`)
  - Official checksum verified: `d29144deff3a68aa93ced33dddf84b7fdc26070add4aa0f4513094c8332afc4e` (`Match: True`)

## 1. Stage Tree Scan (`gitleaks dir C:\evo-x3\stage --redact -v`)
- **Result:** **`PASS` (0 leaks found; exit code `0`)**
- **Summary output:**
  ```text
  INF scanned ~84055 bytes (84.06 KB) in 16.8ms
  INF no leaks found
  ```

## 2. Brief rev 5 Dry Grep Check (`C:\evo-x3\stage`)
Patterns checked: `sk-`, `tskey-`, `Bearer\s+[A-Za-z0-9_\-\.]+`, `LLM_KEY_.*=`.
- `sk-`: **0 matches**
- `tskey-`: **0 matches**
- `LLM_KEY_.*=`: **0 matches**
- `Bearer\s+[A-Za-z0-9_\-\.]+` (case-insensitive): **6 prose-only matches** (all English descriptions such as `"MCP Bearer Auth Proxy"`, `"MCP bearer token required"`, `"bearer keys"`, `"bearer proxy"`; **0 actual bearer token literals**).

## 3. Repository Scan (`gitleaks dir C:\evo-x3 --redact -v` & Post-Commit `gitleaks git`)
- Raw directory scan (`gitleaks dir C:\evo-x3 --redact -v`) scanned ~21.60 MB and flagged 2 `generic-api-key` log lines in `runs/h2_usb_backup_20261114/agy.log:72` and `runs/orch_full_20261114/agy.log:75` (`keyringAuth: loaded token, REDACTED ...`).
- Both `runs/*/agy.log` files are excluded from Git by `.gitignore` (`runs/*/agy.log`, `runs/*/agy.out`, `runs/*/agy.err`, `iso/`, `drivers/`, `*.img`, `*.gguf`).
- Post-commit `gitleaks git C:\evo-x3 --redact -v` result: **`PASS` (0 leaks found; exit code `0`)**
  ```text
  INF 1 commits scanned.
  INF scanned ~254890 bytes (254.89 KB) in 386ms
  INF no leaks found
  ```
