# 2026-10-29 - Research: showing images inside the chat on a phone (pi + pi-mobile), and how the community does it

Asked by Derek at ~19:11 CT ("how can you embed images in pi chat so I can see on mobile? How does the community
do that"). Talk-lane research, read-only, no GPU, nothing installed, no config changed. Versions on this box at the
time of writing: pi `1.4.0` (`pi --version`), `pi-mobile@0.4.0` (Jarno Keskikangas, github.com/jkeskikangas/pi-mobile),
declared in `C:\Users\derek\.pi\agent\settings.json` `packages`.

## 1. How pi itself carries an image (the part that makes it visible anywhere)

An image is a content block, not a markdown link. `docs/message-types.md` L27-37:

```ts
interface ImageContent { type: "image"; data: string /* base64 */; mimeType: string }
// content: string | (TextContent | ImageContent)[]   // user, assistant and toolResult messages
```

Anything that puts an `ImageContent` block into the session transcript is "embedded" for every UI that reads the
session (the TUI, the pi-mobile web app, a JSON export). The producers available on this box:

- `read` on an image path - returns it as an image attachment (this is the simplest one; the tool description says
  images come back as attachments, and it is what I used in the live test in §5).
- MCP tools that return image content, e.g. `browser_take_screenshot` from the playwright MCP server.
- Codemode: `image(block)` in a script, `tools.read()` on an image, and `models.generateImages()`
  (`docs/codemode.md` L26, L45, L186-219). "Show generated images with `image(block)`. Do not print `data` with
  `text()`" - base64 in text is large and the model cannot read it.
- The user's own pasted/attached images.

Settings that matter (`docs/settings.md` L106-114, `docs/terminal-setup.md` L209-214):

| key | default | what it does |
|---|---|---|
| `terminal.showImages` | `true` | display inline images when the terminal supports it |
| `terminal.imageWidthCells` | `60` | preferred inline width in cells |
| `terminal.images` | `"auto"` | force `"kitty"` / `"iterm2"` / `false`; env `PI_IMAGE_PROTOCOL=kitty\|iterm2\|none\|auto` |
| `images.autoResize` | `true` | resize to at most 2000x2000 before sending to a model |
| `images.blockImages` | `false` | do not send images to models (this box: `false` in `settings.json`) |

pi auto-detects OSC 8 links, inline image protocols and truecolor; a proxy/multiplexer can break detection, so the
override exists. In the TUI, `Image` is a real component (`docs/tui.md` L34).

## 2. How pi-mobile shows them (the mobile answer, already installed here)

From the shipped source, `C:\Users\derek\.pi\agent\npm\node_modules\pi-mobile\` v0.4.0:

- `src/protocol.ts` L97-98, L135, L157-166: a transcript item carries only a **count** -
  `images: content.filter(c => c.type === "image").length`. The picture bytes do not ride in the transcript push.
- `web/app.js` L732-780 ("images in the transcript"): `thumbs()` builds a thumbnail strip for `item.images`, and
  each image is fetched lazily with `call("image", { id, ts, i })`, cached per `(agent, id, ts, i)`, and turned into
  `data:${mimeType};base64,${data}`. L782+ `openViewer()` is a modal viewer with prev/next, a counter and zoom.
- `src/bridge.ts` L396-401: the `image` method calls `findImage(sessionManager.getBranch(), id, i, ts)`
  (`src/protocol.ts` L208-225) and returns `{ data, mimeType }`, i.e. the picture is read out of the session
  transcript on demand, sealed with the device key.
- CSP (`src/hub.ts` L522): `img-src 'self' data: blob:` - so data-URI images are allowed to render.
- Size ceiling (`src/hub.ts` L64): base64 in JSON is 4/3, sealed and base64url'd again 4/3, so a single sealed
  payload of about 35 MB is the practical bound. Keep frames far below that.
- Out from the phone: the composer accepts images (`web/app.js` L1348-1402), downscales them to JPEG q0.85
  (L1372-1373) and sends them as image blocks (`bridge.ts` L530-541 filters to `png|jpeg|gif|webp`).
- **Video is not in the transcript UI**: no `<video>`, no `video/` MIME, no mp4 handling anywhere in `web/app.js`
  (grep result: zero hits). So a rendered clip cannot be watched in pi-mobile; images can.

Net: on this box, images already reach the phone. No extension, no code, no server, no config change is needed.
The rule is only: put the image in the transcript, and keep it small.

## 3. How the community does it (the wider pattern)

- **Terminal graphics protocols**, the classic answer on a desktop: the kitty graphics protocol
  (sw.kovidgoyal.net/kitty/graphics-protocol) and the iTerm2 inline-image protocol, plus sixel. Tools in that family:
  `kitty +kitten icat`, `chafa`, `timg`, `term-image` (github.com/AnonymouX47/term-image - needs a kitty/iTerm2
  terminal), `bicat`, `blackcat`. pi implements kitty and iTerm2 natively with capability detection and text
  fallback; in tmux, escaping needs `set -g allow-passthrough all` (tmux 3.3a+) because tmux does not pass graphics.
- **pi extensions that do this in the terminal**: `pi-image-preview` (`pi install npm:pi-image-preview`, v0.1.5,
  35.3 KB, MIT, by rielj) renders thumbnails above the editor with the kitty protocol, pane-aware via kitty's Unicode
  placeholder protocol (U+10EEEE), auto-cleanup, and inlines screenshot tool results; limits from its own README:
  **kitty only** (not iTerm2/Alacritty/WezTerm), **macOS/Linux only - kitty does not run on Windows natively**,
  **not over SSH**, ≤50 MB, GIF first frame only, thumbnail size fixed. Same shape in
  `github.com/jnsahaj/pi-agent-browser-screenshot` (kitty + tmux DCS passthrough + Unicode placeholders).
- **Phone/terminal is the dead end**: pi's own `docs/termux.md` supports text, file tools and shell on Termux and
  says the Termux clipboard API is text-only (no image attach), and the kitty protocol does not cross SSH. So
  "SSH from the phone into the terminal and see the picture" is not the community's route.
- **What people do instead for phones**: a web/bridge UI over the session (the pi-mobile pattern, E2E sealed,
  no server, images fetched on demand), a shared folder / NAS / photo sync to drop files on the phone, or a small
  file server (Tailscale Serve / a LAN share) and open a link. For video, the last two are the only options.

## 4. Recipe for this box (render work → his phone)

1. After a render, pull a few frames, not the clip, and keep them small. On this box ffmpeg is
   `C:\Users\derek\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_...\bin\ffmpeg.exe` (8.0.1-full):
   `ffmpeg -i clip.mp4 -vf "select='eq(n,0)+eq(n,60)+eq(n,120)+eq(n,180)+eq(n,240)',scale=384:-2" -vsync vfr -q:v 6 f_%02d.jpg`
   (3-6 frames: front / mid / tail, ~30-100 KB each).
2. `read` each frame path. The tool result becomes an `ImageContent` block in the transcript, and pi-mobile shows a
   thumbnail strip at that tool step; tap for the full viewer, swipe/prev/next for the rest.
3. Keep the payload modest: the phone fetches base64 through a sealed channel, so 3-6 small frames per call is the
   comfortable size, not a 2 MB contact sheet per frame.
4. Text-only models: `images.blockImages` is the documented switch for "keep the pictures out of the model, keep
   them in the transcript". This box runs `coding_swift15_iq3s_esp`, used in the judge test as a vision reader, so
   images in context are accepted here; `settings.json` currently has `blockImages: false`. **Inference to verify,
   not proven by docs**: that blocks stay in the transcript when `blockImages` is `true`. If we ever want it, that is
   a shared-box config change (propose, do not edit).
5. Clips: the existing path stays the answer - the QNAP drop (`C:\AI\community\scripts\pi_qnap.py`, `/pi-drop/`)
   for full video, and frames in chat for a look. pi-mobile has no video player (verified in §2).

## 5. Live test done for this note (19:1x CT, read-only, no GPU)

`read` of `C:\AI\community\runs\rtx_smoke_20261028\rtx_smoke_20261028_stills_contact.png`, 52,714 B. The tool result
came back as an attached image and is now an image block in this session's transcript, so the transcript item for
that tool step carries `images: 1` and pi-mobile renders a thumbnail for it. One frame, plumbing test only, no
content judgement, and the source file was not modified.

## 6. Not done (needs Derek)

- No install: `pi install npm:pi-image-preview` is kitty-only and macOS/Linux, so it is the wrong tool for this
  Windows box and for a phone; not proposed for install.
- No config change: `images.blockImages`, `terminal.*` keys stay as they are; shared config is proposed in words.
- No new frame-ship script: a `frames_to_chat.py` (ffmpeg + read list) is a small build if he wants it as a step in
  the render flow; not started.
