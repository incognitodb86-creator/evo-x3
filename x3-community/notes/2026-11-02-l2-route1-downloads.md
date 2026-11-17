# L2 - Route 1 H3 community LoRA set: downloaded, hashed, installed (2026-11-02)

Item: `fix_plan.md` LORA block item **L2** (Derek's GO 2026-11-02 chat "Go do ot" = the Route 1 downloads, nothing else).
Scope honoured: no new base model, no FLUX.1-dev, no Z-Image, nothing paid, official sources only, no delete, no write to
`approved_characters/INDEX.csv`, no GPU, no render, ComfyUI not started, no LoRA loaded.
No render skill route applies (download item, no GPU). The facts gate is the Oct 29 catalog survey
(`2026-10-29-h3-lora-catalog-survey.md`) plus each file's own model page. Evidence scripts/logs: `C:\Users\derek\5slock\ralph-community\notes\_lora_l2\`
(`download.log`, `dl_hf.sh`, `hf_*_api.json`, `civitai_2940916.json`, `civitai-download-login-page-9787B.html`).

## 1. The three HuggingFace files - exact URL, size, sha256, licence

Method: `curl -L --fail` over the public `resolve/main` URL (no token, no auth, all three public and ungated);
`certutil.exe -hashfile <f> SHA256` for the hash (the item's instrument); the size expectation is the Oct 29 catalog survey
(§2/§3) and, independently, the repo's own file metadata from `GET https://huggingface.co/api/models/<repo>?blobs=true`
(`siblings[].size`, `lfs.oid` = the source-side SHA-256); for the two akatz repos the repo's own `SHA256SUMS` file is a
third, human-written copy of the same hash. Tolerance 0 bytes: **all three match exactly, 3/3.**

| # | file on disk | exact URL | bytes (expected / got) | sha256 (certutil) | source-side hash | result |
|---|---|---|---|---|---|---|
| 1 | `h3_character_swap_v1.5.safetensors` | `https://huggingface.co/akatz-ai/MiniMax-H3-Character-Swap-LoRA/resolve/main/h3_character_swap_v1.5.safetensors` | 155,110,792 / 155,110,792 | `8f2c3c3eba161df8d0c6099598b4730f641f5ce01e04cd16d2427cff8a35218f` | LFS oid **equal**, repo `SHA256SUMS` **equal** | **MATCH** |
| 2 | `h3-realism-people-t2v-i2v-r2v.safetensors` | `https://huggingface.co/fal/MiniMax-H3-Realism-People-LoRA/resolve/main/h3-realism-people-t2v-i2v-r2v.safetensors` | 131,229,656 / 131,229,656 | `acc529601d2da117fb81179e76c56e488a3beab1171659d305f04fa3655b787e` | LFS oid **equal** (no `SHA256SUMS` in that repo) | **MATCH** |
| 3 | `H3-Person-Remover-V1.safetensors` | `https://huggingface.co/akatz-ai/MiniMax-H3-Person-Remover-LoRA/resolve/main/H3-Person-Remover-V1.safetensors` | 155,110,584 / 155,110,584 | `b01dc9fe888c2f4e455a8eb3b4878dfd4038ee0e2320a7b186c7935e65c93ba5` | LFS oid **equal**, repo `SHA256SUMS` **equal** | **MATCH** |

Download log lines (`_lora_l2\download.log`, all `http=200 rc=0`): 155,110,792 B in 3.4 s (45.5 MB/s), 131,229,656 B in
3.9 s (33.8 MB/s), 155,110,584 B in 5.6 s (27.5 MB/s); `url_effective` = `us.aws.cdn.hf.co/xet-bridge-us/...` (HF Xet CDN),
i.e. the public CDN path, no token. Total 441,451,032 B = 0.44 GB, and C: free went 254,880,546,816 -> (measured after)
see §5.

Repo state at download time (API): #1 `akatz-ai/MiniMax-H3-Character-Swap-LoRA` gated=False, repo sha `96ea3407b230b6f7df71c58c70e31df96bd7e533`, lastModified 2026-10-17T23:41:56Z;
#2 `fal/MiniMax-H3-Realism-People-LoRA` gated=False, sha `039cc8579d7aa357a882d7f4111b25da4f72dccc`, lastModified 2026-08-12T20:46:37Z;
#3 `akatz-ai/MiniMax-H3-Person-Remover-LoRA` gated=False, sha `fe136b3dc93aea993b9f194d48ea9859fdc2de14`, lastModified 2026-10-17T23:41:46Z.
Pages/cards saved under `C:\AI\community\notes\web\` as `l2_hf_*_README.md`, `l2_hf_akatz_*_LICENSE.txt`,
`l2_hf_akatz_*_SHA256SUMS.txt`, `l2_hf_akatz_charswap_NOTICE.txt`, `l2_hf_minimax_h3_BASE_LICENSE.txt` (one fetch per URL;
`check_web_saves.py` run at the end of this note's work).

### Licence as stated on each model page (this is the licence text, not our opinion)

- **#1 Character-Swap v1.5 (akatz-ai)** - card frontmatter `license: other`, `license_name: minimax-h3-community-license-agreement`,
  `license_link: LICENSE`. The repo's `LICENSE` is verbatim the **MiniMax H3 Community License Agreement** (MiniMax H3 release
  /license date **2026-08-02**, © 2026 MiniMax, licensor "Nanonoble Pte. Ltd."). Its `NOTICE` states it is an **Akatz Labs
  modification, not an official MiniMax release**, adapter weights only.
- **#2 Realism-People (fal)** - card frontmatter `license: other`, `license_name: minimax-h3-community-license`,
  `license_link: https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE` = the same MiniMax H3 Community License
  Agreement. Proof it is the same text: all three LICENSE copies fetched (both repos + the base MiniMaxAI/MiniMax-H3 file)
  are **byte-identical, sha256 `59b99642b95ea21630e311198ddbfffbfe05aadba0c2f5d884cbdf4efcc90f44`**, 17,604 B.
- **#3 Person-Remover V1 (akatz-ai)** - identical to #1 (`license: other` / `minimax-h3-community-license-agreement` /
  in-repo `LICENSE`), and its own card says it in prose: "distributed under the MiniMax H3 Community License Agreement;
  see NOTICE... Its territorial, use, redistribution, and commercial provisions apply. The standard territorial grant excludes
  the US, EU, UK, and Republic of Korea... This repository does not expand those terms."
- **The terms that a reader must not miss (quoted from the licence, §II/§IV):** "Applicable Territory" = **worldwide excluding
  the European Union, the United Kingdom, the Republic of Korea and the United States of America**; "You may not use,
  reproduce, modify, distribute, or display the MiniMax H3 Works or any of their Outputs or results outside the Applicable
  Territory"; a person in an Excluded Territory is invited to contact MiniMax about obtaining a licence; a separate prior
  written authorization (api@minimax.io, subject "MiniMax H3 licensing - authorization request") is required above
  **$20M/yr** revenue; commercial products must display "MiniMax H3"; the MiniMax Acceptable Use Policy applies.
  **Flag for Derrick (fact, not legal advice): this box is in the United States, which that licence names as an Excluded
  Territory, so these three files are downloaded under a licence whose territorial grant does not extend here without
  MiniMax's separate authorization.** That is true of the base model we already run (10Eros-Max is built on MiniMax H3), so
  it is not new - it is now on the record because these are new files. Personal, non-commercial, on-box testing is the
  current use.
- **#4 Civitai FaceSwap - no licence stated** (not downloaded, see §2). Civitai's API returns `licence: null`,
  `allowDerivatives: false`, `allowDifferentLicense: true`, `allowNoCredit: true`, `allowCommercialUse: ["Image","RentCivit"]`,
  availability Public.

### Author strength / trigger words (from each model page, for L3/L4; L4 builds no new prompt and uses no trigger)

- #1 Character-Swap v1.5: **no trigger word**; the mechanism is the reference contract - "Replace the selected person in
  `<Video 1>` with the character in `<Picture 1>`", strength **1.0**, model-chain LoRA loader only. Published recipe
  8 steps / CFG 1 / **`er_sde`** / `normal` stacked with the `minimax_h3_fl2v_turbo_8step_v1.0_768p_comfyui_bf16` turbo LoRA
  - **not adopted**: TenStrip's sampler warning governs, our Euler/simple 8-step beta7 dials stay, and beta7 is already a
  distill (the Oct 29 survey skips turbo stacking).
- #2 Realism-People: **trigger `r34l1sm`** (synthetic token, no person word), intended **scale 1.0**, 0.6-0.8 for a lighter
  touch, t2v + i2v + r2v; rank 32, 1500 steps, high-resolution bucket.
- #3 Person-Remover V1: **no trigger word**; strength **1.0**, and its own recipe is a windowed relay: 22-frame windows
  (H3 `17n+5` lengths), **12 steps**, `er_sde`/`simple`, CFG 1, sigma shift 12/3, mask expansion 5 px, 24 fps, and it needs
  **SAM 3.1** + an external first-frame edit as inputs. So its published recipe needs two things this box does not use
  (er_sde, SAM 3.1); it is installed for the fit test (L3), and no cell in L4 uses it.

## 2. Civitai model 2940916 - tried once, blocked, recorded, skipped (as the item instructs)

- The **detail** API works keyless from this box: `GET https://civitai.com/api/v1/models/2940916` → **http 200, 5,541 B**
  (`_lora_l2\civitai_2940916.json`). It gives the file facts: model "FaceSwap - MiniMax REF2VA", type LORA, creator **pgc**,
  version 3329609 v1.0, `trainedWords: ["Faceswap"]`, `baseModel: "MiniMax H3"`, published 2026-09-15; file
  `SS_FaceSwap_MiniMax_H3_REF2VA.safetensors` `sizeKB 64085.84375` = **65,623,904 B expected** (the item's 65.6 MB),
  `hashes.SHA256 = 1E032CF519CC143F434E67516D8AD0AACF4C6E146315B2DCC3B1C2800470326D`, downloadUrl
  `https://civitai.com/api/download/models/3329609?fileId=3215656`.
- **The download is the gated endpoint.** One attempt: `curl -L --fail` → `http=200` but `url_effective` =
  `https://auth.civitai.com/login?returnUrl=...&reason=download-auth` and the body written is **9,787 B of HTML login page**,
  not a 65.6 MB model. So: 200 + a redirected body is not the file; the endpoint needs a signed-in session / API token
  (`reason=download-auth`). No browser session loop, no second attempt, **skipped**, and the 9,787 B body is kept as
  evidence at `notes\_lora_l2\civitai-download-login-page-9787B.html` (moved, not deleted).
- Consequence: no `H3_faceswap_ref2va_v1.safetensors` in `models\loras`, and L4's three cells are unaffected (they use
  #1/#2 + the resident face LoRA). The **Civitai API token ask stays open** (it is ask 3 of L6's four).

## 3. Install into ComfyUI `models\loras` (copy, neutral names, nothing touched)

`cp -n` (no-clobber) of the verified files into `C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\models\loras\`:

| destination | source | bytes | sha256 == source |
|---|---|---|---|
| `H3_charswap_v15.safetensors` | `h3_character_swap_v1.5.safetensors` | 155,110,792 | True |
| `H3_realism_people_v1.safetensors` | `h3-realism-people-t2v-i2v-r2v.safetensors` | 131,229,656 | True |
| `H3_person_remover_v1.safetensors` | `H3-Person-Remover-V1.safetensors` | 155,110,584 | True |

Pre-copy check: all four target names **absent** (so no overwrite risk); entry count **40 -> 43** (+3, exactly the three
copies). No file in `models\loras` was moved, renamed, overwritten or deleted; `FC_SYDNEY_h3_face_v1.safetensors` untouched.
Post-copy verification recomputed sha256 **on the copies** and matched the source hashes (3/3).

## 4. ComfyUI / GPU state (read-only proof)

`C:\AI\director\.venv\Scripts\python.exe C:\AI\community\scripts\comfy_ctl.py status` at 12:48:07 CT:
`comfy_ok=False queue=None guard=(0, ['IDLE']) running=['comfyui_auto']` - ComfyUI is **not started**, so no LoRA is
loaded. `C:\AI\locks\` = only `_removed` (no lock, no GPU job). No model load, no render, no GPU work: the downloads are
net + disk only.

## 5. Disk

C: free before: 254,880,546,816 B (237.38 GiB). Files written: 441,451,032 B in `C:\AI\lora\community_h3_2026-11-02\`
plus 441,451,032 B of copies in `models\loras` = 0.88 GB total. Nothing deleted.

## 6. Done-line check

- Files on disk in **both** places: yes (`C:\AI\lora\community_h3_2026-11-02\` = 3 files; `models\loras` = 3 copies under
  neutral names).
- sha256 recorded: yes (certutil on the originals, re-computed on the copies, cross-checked against HF LFS oids and the
  repos' own `SHA256SUMS`).
- Sizes match the Oct 29 catalog expectation at 0 tolerance: **3/3**.
- This note names the licence for each file: yes (§1); the one file not obtained (Civitai) is named with its reason.
- ComfyUI not started, no LoRA loaded: proved (§4). No download, delete, move, config write, model load, render outside this item.
- Next item is **L3** (header fit probe, read-only, no GPU). The web saves L3 needs are already in `notes\web\` from §1.
