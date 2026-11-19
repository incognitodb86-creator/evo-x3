# EVO-X3 Model Staging Manifest (Phase A3 — DEFERRED)

- **Status:** `DEFERRED` (Household QNAP SMB share name and free space are `NO_DATA`).
- **Brief rev 5 Rule:** Do not download EVO models until Household confirms free space on the QNAP for **both** `Gemma 4 26B A4B Heretic` and `Qwen3.8-Flash-Next` (plus the shared Q8 MTP head), alongside the U2 Clonezilla full-disk image (~118 GiB+ needed for 1.5x of 78.37 GiB used).

## Planned Model Inventory & Task Routing (Brief rev 5 — No Single Default Model)

| llama-swap ID | Model & Source | Expected Size | Routing Role | File Path on EVO (`/srv/models/...`) | SHA-256 |
|---|---|---|---|---|---|
| `flash-next` | `unsloth/Qwen3.8-Flash-Next-GGUF` (`UD-Q4_K_XL`) + shared `mtp-...-shared-Q8_0` | `111.3 GB` + `2.79 GB` | Coding, general, tools, long context | `/srv/models/flash-next/Qwen3.8-Flash-Next-UD-Q4_K_XL.gguf` + `/srv/models/flash-next/mtp-shared-Q8_0.gguf` | `VERIFY_ON_DOWNLOAD` |
| `gemma4-heretic` | `Gemma 4 26B A4B Heretic` (`gemma4_heretic_poly_think` / GGUF) | `NO_DATA` (measure live; do not invent) | Writing (prompts, fiction, uncensored) | `/srv/models/gemma4-heretic/gemma4-26b-a4b-heretic.gguf` | `VERIFY_ON_DOWNLOAD` |
| `qwen27b` | `unsloth/Qwen3.8-27B-GGUF` (`UD-Q4_K_XL`) | `17.6 GB` | Dense fallback & U6 DFlash2 test (optional on QNAP) | `/srv/models/qwen27b/Qwen3.8-27B-UD-Q4_K_XL.gguf` | `VERIFY_ON_DOWNLOAD` |
| `embed-small` (U13) | `nomic-embed-text-v1.5-Q8_0` or `Qwen3-Embedding` (after day-1 setup is live) | `NO_DATA` (measure live) | Persistent `small` embedding group | `/srv/models/embed-small/embed.gguf` | `VERIFY_ON_DOWNLOAD` |
