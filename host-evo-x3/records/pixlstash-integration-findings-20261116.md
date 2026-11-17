# PixlStash × Render integration findings

Written Mon Nov 16, 2026, 10:00 AM CT, by a Max Architect executor. Read-only: no edits, installs, restarts, or new keys. No PixlStash library images, captions, sidecars, or face groups were opened or described. Counts, schema/column and property names, tag *name* capability, and aggregate process facts only. Secrets were not printed. The original ComfyUI folder was not touched.

**Question:** What context does PixlStash store per image, how does the community use it in a ComfyUI pipeline, what are we not doing, and how should Render on the EVO-X3 get access?

**Community way:** Official REST API + ComfyUI-PixlStash nodes ([pixlstash.dev/comfyui.html](https://pixlstash.dev/comfyui.html), [github.com/Pikselkroken/ComfyUI-PixlStash](https://github.com/Pikselkroken/ComfyUI-PixlStash), accessed 2026-11-16 CT) → **adapt**. Render on the X3 should call the official API with a scoped read-only token over Tailscale (tag / character / set search, then fetch the chosen still by id into a job staging folder). Do not copy `vault.db` or the library to the X3, and do not point the official MCP at Render until `view_picture` / `get_picture` are disabled (those tools conflict with the no-view rule). Official ComfyUI nodes are the community pipeline *on AlienPc* if we later wire the H3 graph; they are not required for the X3 writer to pick a still.

research-core used: yes · window: official docs current as of 2026-11-16 plus maintainer posts from 2026 · STANDARD (over budget; searching stopped after OpenAPI path extract and X3/AlienPc status probes) · accessed 2026-11-16 CT

---

## TLDR

PixlStash is a self-hosted image database that auto-tags, captions, embeds (CLIP), groups faces into named people, reads ComfyUI/A1111/Forge recipes out of image metadata, and talks to ComfyUI both ways (nodes in the graph, and runs from inside PixlStash). The community loads stills by project, set, or character (or by semantic / face likeness), then saves results back with metadata. Render on the X3 does none of that: it picks from the 104-image POOL folder with `--character` / `--names`. The AlienPc-era builder still does a direct sqlite character-name lookup, but the two `vault.db` paths it expects under `~/AI/5slock` are not on the X3 (`~/AI/5slock` is empty). Live index counts could not be read: `/api/v1/pictures/count`, `/import/status`, `/tag_health`, and `/dedup/counts` all return **401** without a token. **Top recommendation:** Derrick mints a read-only API token, stores it in an X3 0600 secret file, binds PixlStash to localhost, and keeps Tailscale Serve `:8445` as the only door. Then teach `submit_parody_run.py` to search tags/characters over that API instead of sqlite.

---

## 1. What PixlStash stores per image (official)

Sources: [Features](https://pixlstash.dev/features.html), [AI features](https://pixlstash.dev/ai.html), [Getting started](https://pixlstash.dev/introduction.html), [What's New 2.0](https://pixlstash.dev/whatsnew.html), [GitHub README](https://github.com/Pikselkroken/pixlstash) (raw, this session), [API overview](https://pixlstash.dev/api.html). AlienPc's live OpenAPI (`GET http://alienpc:9537/openapi.json`, unauthenticated, title "PixlStash API", version **2.0.0**, 278 paths) was used only for endpoint and property *names*.

Per picture, the product is built to hold:

| Kind of context | What it is | Engine / notes (official) |
|---|---|---|
| Tags | Auto + manual tags, confidence, accept/reject, tag groups (2.0 files tags into groups such as Hair, Clothing, Pose) | PixlStash Tagger (wd-convnext-tagger-v3 finetune), WD14, Florence-2, or JoyCaption, chosen per request. Plugins: Moondream2, OpenAI-compatible vision/Ollama/LM Studio |
| Captions / descriptions | Natural-language descriptions, usable as caption files on dataset export | JoyCaption, Florence-2 |
| Semantic embeddings | CLIP image embeddings; SBERT embeddings of descriptions; text-in-image OCR is also searched | OpenCLIP ViT-B-32 `laion2b_s34b_b79k`; Florence-2 OCR |
| Faces / characters | Detected faces, embeddings, grouped into people *you name*; character likeness scores; reverse face search | InsightFace SCRFD-10G, buffalo_l (default) or AuraFace |
| Quality | Smart score (aesthetics + calibrated anomaly penalty for malformed anatomy / render defects) | CLIP anchors + ViT anomaly classifier |
| Objects | Detection / segmentation boxes, exportable as COCO or Ideogram JSON | Florence-2 |
| Organization | Project, picture set (lockable), stack, library membership; favourites | Sets can nest under a person (2.0) |
| ComfyUI / A1111 / Forge recipe | Workflow, prompt, models, LoRA strengths, settings, seed, read from the file; optional workflow embedding on save | Recipe tab; `GET /api/v1/pictures/{id}/metadata` schema names include `id`, `format`, `score`, `tags`, `smartScore`, `metadata`, `frame_count`, `locked`, `locked_by_sets`, `prompt_match`, `looks_like_prompt` |
| Export | ZIP or folder of images paired with tag or description captions; full images or face crops | Official "Export a dataset" path |

Official quote, AI features: "Tags, descriptions, faces and embeddings, so the library is searchable by what is in the pictures."

Nothing from our library's actual tag values, captions, or face groups was read.

---

## 2. How the community uses PixlStash with ComfyUI

Primary: the maintainer's docs and repos, plus the maintainer's own Reddit posts (sentiment + announcement; the posts are primary for "what the author shipped").

### Official ComfyUI-PixlStash nodes

[pixlstash.dev/comfyui.html](https://pixlstash.dev/comfyui.html) and [github.com/Pikselkroken/ComfyUI-PixlStash](https://github.com/Pikselkroken/ComfyUI-PixlStash):

- Install: PixlStash **Settings › ComfyUI › Connect** (finds local ComfyUI, installs nodes, restarts via ComfyUI-Manager, mints a key so there is no token to copy), or ComfyUI Manager / manual clone. URL + API token live in **ComfyUI Settings > PixlStash**, never in saved workflow JSON.
- **Loaders:** Project, Set, Character, Picture Loader (picker thumbnails, or headless browse-mode fetch by wired filters).
- **Search:** Semantic Search (text), Likeness Search (face or combined reference images). Needs PixlStash v1.4+.
- **Gates:** Face Likeness Gate and Picture Likeness Gate split a batch into accepted / rejected.
- **Savers:** Picture Saver and Video Saver write back under a project, set, and/or character, with optional embedded workflow metadata.
- **Model shelf (v1.10+ / 1.12+):** Adapter (LoRA), Multi Adapter, Checkpoint, VAE, CLIP, ControlNet, Upscale, Workflow Set loaders, with trigger-word output and "people who fit."
- Example workflows in the repo: load & save round-trip, search → edit → save, outpaint, upscale, face-likeness-gate → upscale.

Official quote, ComfyUI page: "Load images by project, set, or character; search by face, picture, or meaning; gate generations by likeness; and save the results back with full metadata."

### Other official / community pipeline pieces

- **Folder watch / import:** "Folder monitoring for automatic import of your ComfyUI creations" (1.0 announcement, r/comfyui). Background imports complete on the server. API: `GET /api/v1/pictures/import/status` (property names: `status`, `stage`, `total`, `processed`, `progress`, `results`, `imported_count`, `duplicate_count`, `scrapheaped_count`, …).
- **Recipe on every generated picture:** read and copy the Comfy workflow from the PNG; rerun from a Run window; several ComfyUI connections ("this PC and a render box").
- **Dataset export + tag review queue** before LoRA training; lock a set so tags, captions, and scores freeze ([r/StableDiffusion, 2026-07-21](https://www.reddit.com/r/StableDiffusion/comments/1v2ipv4/a_tagreview_queue_for_cleaning_tags_before/), maintainer).
- **Train LoRA** from a person or set via ai-toolkit on the local GPU; finished LoRA lands on the model shelf and is attached to them (2.0, [whatsnew](https://pixlstash.dev/whatsnew.html)).
- **REST API + scoped tokens** for scripts ([api.html](https://pixlstash.dev/api.html)). List / filter pictures with `tag`, `character_id`, `set_id`, `project_id`, score buckets, `file_path_prefix`, `comfyui_model`, `workflow`, etc. (`GET /api/v1/pictures` query param names from the live OpenAPI). Semantic search: `GET /api/v1/pictures/search?query=`.
- **MCP for agents:** `pixlstash-mcp`, token from **API Tokens → Connect AI agent**. Default tools (README): `search_pictures`, `list_pictures`, `count_pictures`, `get_picture`, `view_picture`, `list_tags`, `list_sets`, `list_characters`, `list_projects`, `list_picture_workflows`, `get_recipe`. Write mode (`--allow-write` + full-access token) can edit workflows and start runs. Maintainer warning: do not give a read-only agent a full-access token. Point at another machine with `PIXLSTASH_URL` / `--url`.
- **LM Studio** chat integration and an **ai-toolkit fork** that pulls a curated dataset from the vault are listed on the API page as first-party examples.

Maintainer, r/comfyui 2026-05-30: load pictures "based on project, character or picture set or search for pictures semantically or by face or picture likeness," then "load all the pictures of a particular character and then do a Character LoRA."

---

## 3. What we are doing vs what the community does

### What we have today

- PixlStash 2.0.0 desktop app on AlienPc (installed 2026-11-12 10:06:50 CT). Running since at least 2026-11-13 8:31 PM CT (prior process fact). Listens on **`0.0.0.0:9537`** and `127.0.0.1:62466`. Tailscale Serve `:8445` also proxies `127.0.0.1:9537`. External server was left on so the phone can connect over Tailscale (memory, 2026-11-14).
- From the X3 this session: `GET http://alienpc:9537/api/v1/pictures/count` (and import/status, tag_health, dedup/counts) → **401**. `GET /openapi.json` → **200** (schema only). `https://alienpc:8445/...` → TLS error (`tlsv1 alert internal error`); `http://alienpc:8445/...` → 400. So the API is reachable on the tailnet via the `0.0.0.0` bind, and data routes are auth-gated.
- Render writer now lives on the X3. Stills on the X3: `~/AI/render/stills/approved_characters/POOL` only (**104** image files, names/count only). `~/AI/5slock` is empty. PixlStash vaults were never copied, by rule.
- Live builder: `/home/derekboone/AI/community/scripts/parody/submit_parody_run.py`. `_PIXLSTASH_VAULTS` is sqlite at `~/AI/5slock/approved_characters/vault.db` and `~/AI/5slock/libraries/vault.db`. `pixlstash_character_names_for_still()` joins `face` → `character` → `picture` and returns character *names* for a still path. On the X3 both databases are missing, so this is a no-op. AGENTS.md / RUN_ME.md already tell the writer to pass `--character` / `--names` and not to browse PixlStash contents. One AGENTS.md line also names `stills/approved_characters/vault.db`, which the live `_PIXLSTASH_VAULTS` list does not include.
- Still selection for the current render test / probes is the POOL folder (and `--character` / RefMods), not a PixlStash tag search. That is the missed integration, not a typo in the recently updated skills: the skills *mention* PixlStash tags, but the X3 path cannot resolve them.

### Gaps (community / official capabilities we are not using)

1. Official REST API from Render on the X3 (tag / character / set / semantic search, then fetch a still by id).
2. Official ComfyUI-PixlStash nodes in the MiniMax-H3 graph (Picture Loader by character/set, Semantic / Likeness Search, Face Likeness Gate, Picture/Video Saver). **Install status on AlienPc: NO_DATA this session** (would need a process/folder check on AlienPc or an API token; not done).
3. Saving H3 outputs back into PixlStash with project/set/character and embedded workflow metadata.
4. Official dataset export (images + tag or description captions) for RefMod / LoRA training.
5. Built-in Train LoRA / ai-toolkit jobs from a person or set (`/api/v1/training/jobs`, including `quit-comfyui`).
6. Tag review queue and tag health as a pre-training step (`GET /api/v1/tag_health`).
7. Semantic search or face-likeness search to pick stills (we use folder path + `--character`).
8. `pixlstash-mcp` for the writer or Max (and a wrapper that would drop `view_picture`).
9. Watch-folder auto-import of ComfyUI outputs — **whether it is configured: NO_DATA**.
10. Using recipe / workflow metadata (prompt, LoRAs, seed) as context for the H3 writer — and we should not paste recipe prompt text into chat anyway.
11. Confirmed auto-tagger engine (PixlStash Tagger vs WD14 vs Florence-2 vs JoyCaption) — **NO_DATA** without settings or a token.
12. Bind / exposure: official default `host` is `"localhost"`; `"0.0.0.0"` is the "expose on the local network or internet" setting. We are on `0.0.0.0`. Derrick wanted tailnet-only. A prior AlienPc audit also flagged broad Windows Firewall Python Allow rules.
13. Scoped API tokens for scripts and for the ComfyUI nodes (if nodes are not already linked via Settings › ComfyUI).

The "already updated the skills" work documented the AlienPc sqlite lookup and the X3 workaround. It did not give the X3 writer a PixlStash search path. A separate PM item on PixlStash tagging was left blocked by the no-view rule; an API that returns *tag names and picture ids only* is how to unblock that without viewing images.

---

## 4. Ranked ways to give Render on the X3 PixlStash access

Do not implement any of these until Derrick says yes. No new keys were created this session.

### Rank 1 — Official REST API over Tailscale, scoped read-only token (recommended)

**How it would work.** Render on the X3 keeps a base URL and a token in an X3 0600 file under the existing secrets pattern (`/etc/evo-x3/*` or an evo 0600 file; never a command line, never git, never chat, never the brain). The builder replaces the sqlite `vault.db` lookup with official calls, for example:

- `GET /api/v1/pictures/count`, `GET /api/v1/pictures/import/status`, `GET /api/v1/tag_health` — index / health (counts and job state only).
- `GET /api/v1/tags`, `GET /api/v1/characters`, `GET /api/v1/picture_sets` — name lists.
- `GET /api/v1/pictures?tag=…` or `character_id=…` or `set_id=…` (and `fields=` limited to id / path / tag names, never caption bodies).
- Optional later: `GET /api/v1/pictures/search?query=…` (semantic), still returning ids only.
- Fetch the chosen still by id into a *job* staging directory for ComfyUI, then queue as today. Agents must not open, thumbnail, or describe that file in chat.

**Risks.** Token leakage if it is committed or pasted. A full-access / ALL-scope token would authorize writes, deletes, and local-only filesystem routes (official MCP README warning). `require_local_for_write` defaults to true and official docs say it allows full login only from RFC 1918 / loopback; Tailscale `100.64/10` is CGNAT (RFC 6598), not RFC 1918, so a **READ-only share token** is the right kind for the X3 (docs: read-only share tokens are accepted from any IP). After binding to localhost, `:9537` on the tailnet will stop working; X3 must use Serve `:8445` (or a tailnet-only listen). This session, HTTPS to `:8445` from the X3 failed TLS, so Serve needs a check before it becomes the only door. Fetching a still copies that one file to the X3 for the job — that is expected for a render, and is not a library mirror.

**What needs Derrick.**

- In PixlStash: **API Tokens → New token**, read-only, scoped to the approved-characters library / set / people if possible. If several libraries stay in use, turn on **Use in every library** or mint one token per library. Put the value in the vault or type it into the X3 0600 file himself (bots do not create keys).
- Bind change: set `host` to `127.0.0.1` / `localhost` in the desktop server settings / `server-config.json`, keep Serve `:8445` as the only remote door. Bots should not open the app to do this.
- Confirm or tighten Tailscale ACLs so only the X3 (and the phone, if he still wants it) can reach `:8445`. Tighten the broad Python firewall Allows (prior audit).
- Confirm Serve `:8445` TLS from the X3 before turning off `0.0.0.0:9537`.
- Yes to a small builder change: API client in `submit_parody_run.py`, X3 docs (`AGENTS.md`, `RUN_ME.md`, `x3/README-X3.md`) updated to "search by tag via API, never sqlite, never view images."

### Rank 2 — Periodic read-only sync of a sanitized tag index + selected stills

**How it would work.** A scheduled job on AlienPc (or from the X3 over the API) writes a sanitized tag→id→path index (no captions, no face embeddings, no sidecars) plus the still files already approved for Render, into an X3 folder. The builder keeps a local lookup.

**Risks.** Goes stale the moment tags change. Easy to accidentally copy `vault.db` (which holds captions and faces) or a large slice of the library — and the standing rule is that PixlStash vaults are never copied. Disk and QNAP budget. Worse than the official API, and it does not give live import/tag-health status.

**What needs Derrick.** Yes to which stills may be synced, a destination path, and a clear ban on copying `vault.db` / captions. No API token strictly required if the job runs locally on AlienPc, but the official API is still the cleaner extractor.

### Rank 3 — Official `pixlstash-mcp` on the X3 (optional later, not first)

**How it would work.** Install or PATH the official `pixlstash-mcp`, set `PIXLSTASH_URL` at AlienPc Serve `:8445` and `PIXLSTASH_TOKEN` from **Connect AI agent**. Useful for Max status checks (`count_pictures`, `list_tags`, `list_characters`).

**Risks.** Default tools include `view_picture` and `get_picture`, which conflict with "never view library contents." `get_recipe` can surface prompt text. A full-access token plus `--allow-write` can start ComfyUI runs and edit workflows. MCP is a poor fit for the deterministic builder script (REST is). Only safe after a wrapper or client allow-list that exposes count / tag / character / id search and hides view / recipe / write tools.

**What needs Derrick.** The same read-only token and bind/ACL work as Rank 1, plus an explicit yes that MCP may be added with view tools disabled.

### Not recommended as the X3 path

- Copying `vault.db` to the X3 and keeping the sqlite join. It is unofficial, races the live app, and the database contains captions and face data we should not replicate.
- Teaching the H3 graph to use ComfyUI-PixlStash Picture Loader as the *only* still source, without an X3 API. That can be a later AlienPc improvement (needs Derrick's yes, and the picker UI shows thumbnails). It does not help the writer on the X3 choose a still before queueing.

---

## 5. Index status

**Current status: not determined.** Live data endpoints from the X3 to `http://alienpc:9537` returned 401 (unauthenticated). No login or API token was used. No library pages were opened.

**Last observed counts (not current, NOT CHECKED as live this session):** 2026-11-12 10:44 AM CT, during the official GPU categorize pass, the Approved characters library at `C:\Users\derek\5slock\approved_characters` had finished captions, image embeddings, and text embeddings: **489 pictures, 869 faces, 0 automatic character names**. Next planned libraries were ComfyUI input, Render inputs, then Grok downloads. GPU categorize was later put on hold for bakeoffs, then a "Stills libraries GPU pass" was left running the evening of 2026-11-12; by 10:21 PM CT that day notes say "PixlStash stays on CPU." The process has been up since 2026-11-13 8:31 PM CT. Whether those later libraries finished is **NO_DATA**.

**What is needed to read the index (counts and job state only):** a PixlStash login in the vault, or a read-only API token stored the same way (Derrick types it). Then, without opening pictures or captions:

- `GET /api/v1/libraries` (library names only)
- `GET /api/v1/pictures/count` → `{ count }`
- `GET /api/v1/pictures/import/status` → `status`, `stage`, `total`, `processed`, `progress`, `imported_count`, `duplicate_count` (do not print `results` or id lists)
- `GET /api/v1/tag_health` → `building`, `progress`, `computed_at`, `stale` (not per-picture rows)
- `GET /api/v1/dedup/counts`, `GET /api/v1/tagger-runs`, `GET /api/v1/training/ai-toolkit/status` if useful
- `GET /api/v1/tags` / `GET /api/v1/characters` for *name lists and counts only*

---

## 6. Evidence table (research-core)

| claim | source (publisher) | URL | published | accessed CT | class | quote ≤25w | status | hedge |
|---|---|---|---|---|---|---|---|---|
| Auto tags + captions; engines selectable per request (PixlStash Tagger, WD14, Florence-2, JoyCaption) | PixlStash official | https://pixlstash.dev/ai.html | UNDATED page; product 2.0 | 2026-11-16 10:00 AM CT | primary | "Choose the tagger per request rather than per install" | SUPPORTED | soft on which engine AlienPc uses (NO_DATA) |
| CLIP semantic search and named face groups | PixlStash official | https://pixlstash.dev/features.html | UNDATED | 2026-11-16 10:00 AM CT | primary | "CLIP embeddings, computed locally." / "grouped into people you name" | SUPPORTED | hard for product capability |
| Recipe (workflow, prompt, models, LoRAs, seed) on ComfyUI/A1111/Forge pictures | PixlStash official / README | https://pixlstash.dev/features.html ; GitHub README | 2.0 docs | 2026-11-16 10:00 AM CT | primary | "The workflow, prompt, models, LoRA strengths, settings and seed behind a picture" | SUPPORTED | hard |
| Dataset export of images + tag or description captions | PixlStash official | https://pixlstash.dev/introduction.html | UNDATED | 2026-11-16 10:00 AM CT | primary | "Export the current view as a ZIP of images paired with tag or description captions." | SUPPORTED | hard |
| ComfyUI nodes load by project/set/character and save back with metadata | PixlStash official + ComfyUI-PixlStash README | https://pixlstash.dev/comfyui.html ; https://github.com/Pikselkroken/ComfyUI-PixlStash | current main | 2026-11-16 10:00 AM CT | primary | "Load images by project, set, or character" | SUPPORTED | hard |
| Scoped API tokens for other apps | PixlStash official | https://pixlstash.dev/introduction.html | UNDATED | 2026-11-16 10:00 AM CT | primary | "Create a scoped API token to use PixlStash from other applications." | SUPPORTED | hard |
| Official MCP can search and read pictures, tags, and recipes; tools include view_picture | PixlStash README | https://github.com/Pikselkroken/pixlstash | current main | 2026-11-16 10:00 AM CT | primary | "an agent can search the library and read pictures, tags and ComfyUI recipes" / "Tools: … view_picture" | SUPPORTED | hard |
| Default server bind is localhost; 0.0.0.0 exposes the server | PixlStash README | https://github.com/Pikselkroken/pixlstash | current main | 2026-11-16 10:00 AM CT | primary | "Address the server binds to. Change to \"0.0.0.0\" to expose the server" | SUPPORTED | hard |
| Read-only share tokens accepted from any IP; full login limited to local/RFC1918 when require_local_for_write is true | PixlStash README | https://github.com/Pikselkroken/pixlstash | current main | 2026-11-16 10:00 AM CT | primary | "READ-only share tokens are always accepted from any IP." | SUPPORTED | soft on whether Tailscale 100.64/10 counts as local (docs say RFC 1918 / loopback) |
| Train LoRA from a person or set via ai-toolkit (2.0) | PixlStash official | https://pixlstash.dev/whatsnew.html | 2.0 notes | 2026-11-16 10:00 AM CT | primary | "Select a person or a set and press Train LoRA." | SUPPORTED | hard |
| Community / maintainer: load by project, character, set, or semantic/face search in ComfyUI | Maintainer Reddit | https://www.reddit.com/r/comfyui/comments/1trvory/search_edit_store_the_usefulness_of_databases_in/ | 2026-05-30 | 2026-11-16 10:00 AM CT | community (maintainer) | "load pictures based on project, character or picture set or search … semantically or by face" | SUPPORTED | hard for intent; usage volume beyond the author is not measured |
| Tag review queue before training; lock a set | Maintainer Reddit | https://www.reddit.com/r/StableDiffusion/comments/1v2ipv4/a_tagreview_queue_for_cleaning_tags_before/ | 2026-07-21 | 2026-11-16 10:00 AM CT | community (maintainer) | "you can lock it so its tags, captions, and scores freeze" | SUPPORTED | hard |
| Live AlienPc API is 2.0.0; count/import/status/tag_health/dedup/counts need auth (401); openapi.json is public | This session, X3 curl to alienpc:9537 | http://alienpc:9537/openapi.json (schema only) | live 2026-11-16 | 2026-11-16 10:00 AM CT | primary (this install) | HTTP 401 on count and import/status; OpenAPI title/version 2.0.0 | SUPPORTED | hard for auth; no live counts |
| X3 has 104 POOL stills, empty 5slock, sqlite vaults missing; builder points at 5slock vault.db paths | This session, X3 find/grep | n/a (local) | live 2026-11-16 | 2026-11-16 10:00 AM CT | primary (our tree) | `_PIXLSTASH_VAULTS` → `5slock/approved_characters/vault.db` and `5slock/libraries/vault.db` | SUPPORTED | hard |
| Last index snapshot 489 pictures / 869 faces / captions done on Approved characters | Prior lease note | /workspace/cos/brain-staging/30_handoff/status/2026-11-12-1044-alienpc-lease-updated-max3-pixlstash-gpu-categorize.md | 2026-11-12 10:44 AM CT | 2026-11-16 10:00 AM CT | secondary (prior agent note) | "489 pictures, 869 faces, 0 automatic character names" | NOT CHECKED THIS SESSION as live | stale; not current index |

Conflicts: none on product capability. Bind practice conflicts with official default and with Derrick's tailnet-only preference (`0.0.0.0:9537` is currently reachable on the tailnet). AGENTS.md mentions `stills/approved_characters/vault.db`; live `_PIXLSTASH_VAULTS` does not.

Not checked this session: ComfyUI-PixlStash installed on AlienPc; watch-folder config; current tagger engine; Tailscale ACL file; whether a PixlStash token already exists in the vault (not searched, to avoid handling secrets); live picture counts.

Searched, not found: `https://pixlstash.dev/api/v1/` → 404; `https://pixlstash.dev/api/v1.7/` and `https://pixlstash.dev/api/v2.0/` fetched with empty body (index page redirects to v2.0). Live install OpenAPI used instead. No public independent write-up of "typical user" H3+PixlStash pipelines beyond the maintainer's nodes and posts.

Open questions / next (need Derrick) are in §9. Vision inventory, celebrity tagging, and the NSFW/parody pipeline design follow.


---

## 7. Vision models, celebrity/person tagging (t1904u–t1908u)

Rules reused only (already approved; no new gates): 18+ is the only content rule; any Grok/Flow still is allowed; all adult RefMods and voice refs are allowed; PixlStash is the approved_characters pool. Max never views library images. Tagging is a local, unattended pass.

### (a) What we have

**X3 llama-swap** (`/etc/evo-x3/llama-swap.yaml`, `/srv/models`, exclusive swap among the three big slots; names, quants, sizes only):

| Slot | Weights | Vision? |
|---|---|---|
| **gemma4-heretic** (live) | `gemma-4-26B-A4B-it-heretic.Q8_0.gguf` 25.02 GiB + **unsloth mmproj BF16** 1.11 GiB (`--image-min-tokens 560 --image-max-tokens 1120`) | Yes, uncensored (Heretic). Spare unused: `Gemma-4-26B-A4B-Heretic.mmproj-Q8_0.gguf` 769.05 MiB and a second 25.02 GiB heretic copy |
| qwen27b | `Qwen3.8-27B-UD-Q8_K_XL.gguf` 29.30 GiB + DFlash2 draft 1.06 GiB (also a UD-Q4_K_XL 16.45 GiB on disk) | No mmproj in the slot or folder — text, not a VLM as installed |
| flash-next / flash-next-uncensored | Qwen3.8-Flash-Next UD-Q4_K_XL shards (~103.7 GiB) + shared MTP Q8 2.60 GiB | No mmproj (not downloaded). Coding slot. Do not use for library tagging |
| embed-small | nomic-embed-text-v1.5 Q8_0 139.38 MiB | Text embeddings only |

**PixlStash built-in** (official docs, names only; which engine is selected on AlienPc is NO_DATA without a token/settings read): taggers — PixlStash Tagger, WD14, Florence-2, JoyCaption (per request); captions — JoyCaption, Florence-2; plugins — `moondream2_captioner`, `openai_compatible_captioner` (Ollama / LM Studio / llama-server / vLLM). Faces — InsightFace SCRFD-10G + buffalo_l (default) or AuraFace; faces are grouped, and **people get names when someone names them** (our Nov 12 snapshot had 0 automatic character names). buffalo_l is published for non-commercial research only; PixlStash offers AuraFace when a commercial pack is needed.

### (b) Celebrity / person recognition (local only)

This is two different jobs. Do not use a VLM to replace face matching for people we already have named refs for.

| Rank | Approach | Celebrity/person evidence | Fits | Uncensored? |
|---|---|---|---|---|
| 1 (named people we already have) | **PixlStash InsightFace (buffalo_l / ArcFace) matched to a named gallery** (INDEX / RefMod / already-named PixlStash people) | Official zoo: buffalo_l **LFW 99.83%**, **IJB-C 97.25** TAR@FAR 1e-4. Identifies by match to enrolled names; it will not invent a legal name with no gallery entry | Already on AlienPc | N/A (embeddings, not a chat VLM) |
| 2 (open-world name for unmatched faces) | **Qwen 3.5 / 3.6 VL or Qwen3-VL** (not installed) | ImageBench 2026-06-21, 90 Wikimedia portraits: Qwen 3.5 122B **46/90**, Qwen 3.6 35B **44/90**, Qwen3-VL **40/90** (30/30 global icons). Official Qwen3-VL README: pretraining is able to “recognize everything”—celebrities, anime, products, landmarks, flora/fauna. Qwen3-VL size in that ImageBench table is not stated | 4B–8B on AlienPc 16 GB; 27B/35B/122B-Q4 on X3 128 GB | Community Heretic builds exist (e.g. Qwen3-VL-4B-Heretic). Not on disk here |
| 3 (what we already run) | **gemma4-heretic** on the X3 | Same ImageBench: stock Gemma 4 26B **34/90** (29/30 global icons; missed Jackie Chan; 0/30 long-tail). Heretic keeps vision and drops refusals, which is what we want for NSFW tagging. Not the best open-world namer, but it is local, uncensored, and already wired | Yes, X3. Q8 26B does not fit the 5070 Ti 16 GB | Yes — this is our uncensored vision slot |
| Not for person names | WD14 / PixlStash Tagger / Florence-2 / JoyCaption | Built for tags, captions, defects — not legal-name ID | Already in PixlStash | N/A |
| InternVL / MiniCPM-V | Capable general VLMs; PhotoPrism compared MiniCPM for *labels* | No primary celebrity-naming score opened this session (NO_DATA). Do not add a new model family for this | — | — |

### (c) Can PixlStash use a custom local VLM? How do faces get names?

Yes. Official path: `pixlstash-cli plugins install openai_compatible_captioner`, then Settings → Auto-tagging, endpoint + model. The plugin posts each image to an OpenAI `/v1/chat/completions` server (llama-swap on the X3 is that API). Images go to whatever endpoint is set; point it at the X3 over the tailnet, not a public host. Official 2.0 docs advertise this; the plugin README still has a stale “needs 1.10 / no release loads captioning plugins yet” warning. We are on **2.0.0**. Confirm with `pixlstash-cli plugins list` after Derrick’s yes. If the plugin will not load, a sidecar script can write the same tags through the API — same pipeline, no new rule.

Face grouping is already InsightFace: detect, embed, cluster. Names are applied when a person is named (UI or API character membership). A VLM does not replace that; it only proposes names for unnamed clusters, written back as person tags / character membership. Max does not look at the pictures.

### (d) Recommendation (lean)

**Model pick:** use **gemma4-heretic on the X3** now (uncensored local VLM we already have). Optional later, only if Derrick wants better long-tail names: add an uncensored Qwen3-VL (4B/8B can live on AlienPc; larger on the X3). Do not retask flash-next or qwen27b.

**Where it runs:** PixlStash stays on AlienPc. The VLM stays on the X3 llama-swap slot. A tagging pass loads gemma4-heretic and will evict flash-next / qwen27b while it runs — schedule it off the Forge/coding slot. InsightFace tagging/grouping stays on AlienPc (already in PixlStash).

**Hands-off tagging pipeline (no Max, no new gates):**

1. PixlStash (plugin) or a small sidecar sends each approved_characters image to `gemma4-heretic` on the X3 and/or matches faces to the named INDEX/RefMod gallery with InsightFace.
2. It writes **person/character tags and membership** back through the PixlStash API (`/api/v1/pictures/{id}/tags`, character membership). No sqlite writes, no chat, no thumbnails in logs.
3. Render later searches PixlStash by that person tag and attaches RefMods through the existing resolver (section 8). Same NSFW writer path as today.

**Risks:** VLMs mis-name people (Gemma 4 26B confidently missed Jackie Chan on ImageBench). Prefer InsightFace match when a named ref exists; use the VLM only for unmatched faces. buffalo_l license is non-commercial research; use AuraFace if that matters. Plugin settings store an API key in plain text — leave the key empty if the X3 endpoint is open on the tailnet, or put the PixlStash token only in an X3 0600 file for the sidecar. gemma4-heretic evicts the coding model during a pass.

---

## 8. NSFW / parody pipeline integration (t1906u–t1908u)

Same flow as today: `submit_parody_run.py` / `build_request.py`, locked single-pass INDEX + RefMod template. No new gates, lints, or check steps. The 18+ rule, “any Grok/Flow still,” “all adult RefMods and voice refs,” and “PixlStash = approved_characters pool” stay as they are.

### What already works

`resolve_writer_refmods()` already accepts a PixlStash character tag and resolves it the same way as `--character` / `--names`:

- `_stems_for_character_name()` → `resolve.find_refmods_for_name()` (normalized name as a substring of the RefMod stem, e.g. `emiliaclarke` in `minimaxh3_emiliaclarke_v1_refmod`) plus `aliases.json` and `_OC_PATH_COMPONENT_ALIASES` (e.g. `pool` → poolclub / FCSydny; `fcmegan` → meganfox).
- `resolve_identities()` against `INDEX_DIR` (`community/index/h3-known-characters/INDEX.md` + `INDEX_BAD.md`) and `aliases.json` (15 aliases).
- OC: `trained_oc_subject_keys()` reads `subject_name` from `minimaxh3_oc_*_refmod_visual.safetensors` (e.g. FCSydny → poolclub) and attaches `minimaxh3_oc_poolclub_v1_refmod_visual` + `_audio`.

Normalization already in code (reuse, do not add a third scheme): `resolve._normalize_key()` strips to `[a-z0-9]` (filename match). `submit._norm_ident()` lowercases and keeps spaces (INDEX field match). The tag-to-RefMod map should key on `_normalize_key`.

**Live RefMod files** (`~/AI/comfy-alienpc/models/refmods`, 1500 `.safetensors`): **1458** are `minimaxh3_<name>_v1_refmod.safetensors` (plus a few v2+ / style variants). INDEX assets are **one file per name**, not a `_visual`/`_audio` pair. Only the OC poolclub pair uses `_refmod_visual` / `_refmod_audio` (v1 and v2 on disk). INDEX.md holds **1484** rows (503 good, 82 onthefence, 899 bad). The builder already loads whatever stems the resolver finds, including voice refs when those files exist.

`pixlstash_character_names_for_still()` already reads PixlStash character names for a still (sqlite `face` → `character` → `picture`) and feeds them into that resolver (`source: "pixlstash"`). That is the “tag links to INDEX / OC RefMod” path. It is just not reachable on the X3.

### What is missing on the X3

- `~/AI/5slock` is empty. Live `_PIXLSTASH_VAULTS` is `~/AI/5slock/approved_characters/vault.db` and `~/AI/5slock/libraries/vault.db`. The sqlite lookup is a no-op.
- Render picks stills from the 104-image POOL folder (or a named path), not `GET /api/v1/pictures?character_id=` / `?tag=`.
- PixlStash people are largely unnamed, so even a working lookup has little to resolve until the unattended tagging pass (section 7) writes person tags.

Do not copy `vault.db`. Use the official API (section 4, Rank 1).

### Spoofs / parodies vs OC (same path, no new fork)

- **INDEX parody / spoof:** a PixlStash person tag (actor or character name) normalizes and hits `minimaxh3_<name>_v1_refmod` via INDEX + `aliases.json`, same as `--character "Emilia Clarke"`.
- **OC:** a PixlStash tag or trigger (FCSydny) hits `minimaxh3_oc_<key>_v1_refmod_visual` + `_audio`, same as today.
- If both could match, keep today’s resolver order (explicit `--character` / `--names`, then OC path/trigger, then PixlStash tags). No new disambiguation rule.

### Tag-to-RefMod map (where it lives)

Do not invent a parallel rule file. Generate a lookup from what already exists, next to the aliases:

- Path: `community/scripts/parody/pixlstash_person_refmods.json` (generated; or extend `aliases.json` if we want zero new files).
- Contents: `{normalized_person_tag: refmod_stem}` from INDEX character + actor names, existing aliases, and OC `subject_name` metadata. Rebuild when INDEX or RefMods change.
- Runtime still falls back to `find_refmods_for_name` + `resolve_identities`, so the file is a convenience, not a new gate.

### Minimal file change list (design only, no code in this pass)

1. `community/scripts/parody/submit_parody_run.py` — replace sqlite `_PIXLSTASH_VAULTS` with a PixlStash API client (tag / character_id / names only). Add still pick-by-person-tag using `GET /api/v1/pictures`. Keep `resolve_writer_refmods()` as the RefMod attach path.
2. Optional thin helper: `community/scripts/parody/pixlstash_client.py`.
3. `community/scripts/parody/aliases.json` and/or generated `pixlstash_person_refmods.json` as above.
4. Docs only: `render/AGENTS.md`, `render/RUN_ME.md`, `render/x3/README-X3.md` — search by person tag via API; vault.db is not on the X3.
5. Tests: extend `community/scripts/parody/test_t1109_writer_index_refmods.py` (and a small API-lookup unit test with fixtures, no live library).
6. Optional sidecar (AlienPc or X3): unattended tag writer calling gemma4-heretic + PixlStash API. Not a render hook.
7. AlienPc, after Derrick’s yes: install `openai_compatible_captioner`, point Endpoint at the X3 gemma4-heretic slot, restart PixlStash. If 2.0 will not load the plugin, the sidecar alone is enough.

Do **not** change `writer_sys.py`, `wp_lint.py`, stills-pool rules, or add checks to `build_request.py`.

### What Derrick must supply

- A PixlStash **API token** he types himself (read is enough for Render still search; **write** is required for the tagging pass). Store it in an X3 0600 secrets file, never in chat, git, or the plugin’s plain-text key field if we can avoid it.
- Yes to bind PixlStash to localhost and keep Serve `:8445` as the only door (confirm TLS from the X3 first; it failed this session).
- Yes to run the unattended tagging pass (loads gemma4-heretic; evicts flash-next for that window).
- No new keys created by a bot. No Max viewing. Optional later: a Qwen3-VL Heretic download if global-icon accuracy is not enough.

## 9. Open questions / next (need Derrick)

1. API token + bind / Serve yes (sections 4 and 8).
2. Yes to the unattended gemma4-heretic tagging pass.
3. After a token exists, read index counts only (`/pictures/count`, `/import/status`, `/tag_health`).
4. Optional later: Qwen3-VL Heretic, ComfyUI-PixlStash nodes, or save H3 outputs back to a set — each a separate yes.
