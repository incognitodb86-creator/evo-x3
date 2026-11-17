---
description: Render stills or a video from an approved still, e.g. /render still pick 4 or /render video B01 2
---
For `still`: if Derrick asked for a pose, angle or scene, first load the `alienpc-stills-pose-edit-prompting` skill and write the pass-1 prompt per it (change -> keep -> light/style), and add it to the command below as `--words "..."`.

Then queue the render batch in the background with this one command:

```
/home/evo/AI/director/.venv/Scripts/python.exe /home/evo/AI/community/scripts/make_render.py $@
```

Then reply with the job id and queue log path (`<run_dir>\_render_queue.log`) so the next message still gets answered. Keep every /media/... link on its own line, unchanged, so it shows inline in the phone chat. Do nothing else: no other commands, checks or comments.
