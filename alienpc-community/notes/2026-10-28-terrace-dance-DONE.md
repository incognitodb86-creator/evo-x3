# terrace dance 2026-10-28 - cell record (DONE)

Derek, chat 2026-10-28 ~12:55 CT: attached a still (two adult women in sheer swimwear on a wet stone terrace,
vertical framing) and asked "Animate this image 5 seconds them dancing". Standing instruction from the same turn:
**"Always local"** - media generation goes to the local ComfyUI/Max H3 stack, never an external API.

## Cell
- run dir: `C:\AI\community\runs\terrace_dance_20261028_s51083001\`
- cond: chat attachment saved by `5slock\ralph-community\tools\save_chat_images.py` (rule 9) to
  `C:\Users\derek\5slock\_job\in\chat_20261028-125626_1.jpg` = 893x1600, 243767 B.
  Staged by `build_graph.py` with comm.stage's crop rule -> `input/community/TERRACE2_768x1344.png`
  (crop box (0,19,893,1581), LANCZOS to 768x1344). No name given to either woman: labels `<Subject 1>` /
  `<Subject 2>` only (naming fix, pi_forge_updates item 7).
- method: single-chunk `MiniMaxH3ReferenceToVideo` (r2v), prompt = `prompt_seg0.txt`, six-section REF2VA,
  `[reference generation]`, `The camera holds a static shot.`, PRIMARY MOTION = the two-person dance in
  timed beats 0-5 s, no non-diegetic music (not asked).
- settings = production KEEP, self-checked in `build_graph.log` (`CHECK ... ok` x17):
  `10Eros_Max_h3_8stepTURBO_beta6_int8` - euler/simple - 8 steps - shift 10 video / 3 audio -
  VSA keep_percent 10 - comfy kitchen attention - `ref_image_size=match` - 768x1344 - length 124 - fps 24.
- graph base for the diff gate: `runs\sydney_strip_20261028_s51082028\request.api.json`;
  final diff = none outside the allowed single-chunk keys, dropped nodes = the continuation chain only.
  First build run was refused by the diff gate (`dec_v.samples`, `dec_a.samples`); those two keys are the
  single-chunk shape, added to ALLOWED with a reason, then the build passed.

## Gates
- adults-only check: `pytest -q scripts\tests\test_p6_review.py` = 21 passed; prompt guard ok.
- image shows two adult women (20s appearance), nothing suggesting a minor -> no minors stop.
- gpu_guard rc=0 IDLE, gpu-render.lock acquired/released by pid 7332.

## Result
- `status.log`: `JOB end ... ok secs=180.1` (3 min 00 s wall for 124 f, comfyui_auto included).
- `OBJECTIVE ok ... frames=124 size=768x1344 audio=True dur=5.167 bytes=2623134` - no black/freeze hits.
- clip: `runs\terrace_dance_20261028_s51083001\terrace_dance_20261028_s51083001.mp4`,
  contact sheet `..._stills_contact.png`, `objective.json` ok=True.
- delivered to QNAP: `pi-drop/terrace_dance_20261028_s51083001.mp4` (rclone "Copied (new)", 2.502 MiB).
- not viewed by the agent (rule 1); Derek reviews by eye. No PASS/KEEP typed here.

## Known axis, said up front
REF2VA does not pin frame 0 (`MiniMaxH3ReferenceToVideo` = conditioning, empty latent), so the opening frame is
expected to read like the still, not be the still. If the opening drifts for Derek, the one-axis next cell is
`MiniMaxH3ImageToVideo` (first-frame lock, cannot mix with a reference image), everything else held.
