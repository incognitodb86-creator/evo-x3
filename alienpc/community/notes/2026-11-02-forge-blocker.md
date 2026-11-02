# 2026-11-02 L6 blocker (Forge, ralph loop pass) - blind pack delivery to the QNAP needs an approval the loop cannot get

**What**: item L6 (fix_plan.md LORA block) asks for the blind pack to be delivered to QNAP
`pi-drop/h3-lora-ab-2026-11-02/` through `C:\AI\community\scripts\pi_qnap.py put`, and the delivered
filename named in chat. The pack is built and verified locally; the QNAP copy did not run.

**Evidence**: the pass ran `C:/AI/director/.venv/Scripts/python.exe C:/AI/community/scripts/pi_qnap.py ls
/pi-drop/h3-lora-ab-2026-11-02` (a read) and the harness answered
`Running bash command '...' requires approval, but no interactive UI is available.` - the loop pass has no
approval UI, and AGENTS.md puts QNAP access behind pi_qnap.py with ask-first rules, so I did not use raw
rclone, a UNC path, `powershell` Copy-Item, or any other route around the gate. Nothing was written to the NAS.

**Staged, ready to ship**: `C:\AI\community\review\h3-lora-ab-2026-11-02\pack\{a01,a02,a03}.mp4`
(2,558,369 / 2,318,348 / 2,304,919 B, == the delivered clips, sizes in `key.csv`) and `key.csv`
(blind ids from the documented shuffle `PACK_RNG_SEED = "h3-lora-ab-2026-11-02"`). The target folder does
not exist on the NAS, so this is all new files, no overwrite.

**The ask**: Derrick's yes to run the recorded lines `C:\Users\derek\5slock\ralph-community\notes\_lora_l6\qnap_put.sh`
(one `mkdir` + four `pi_qnap.py put` + one `ls` to verify sizes). With the yes, the only step is that file.
Everything else in L6 (objective proof, identity table, judge flags, DONE note, records) is done and needs
no NAS access.

No GPU work ran in this pass; `C:\AI\locks\` has only `_removed` and `comfy_ctl.py status` is IDLE.
