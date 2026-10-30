"""All paths and constants for the flux-edit Phase A harness. Override any NAME with env FLUX_EDIT_<NAME>.

No host, address or credential lives in this file. AlienPc values come from env only.
"""
import os

_D = {
    # llama-swap base URL, e.g. http://<ALIENPC_HOST>:8080. Required for live runs; no default on purpose.
    "LS_URL": "",
    "COMFY_PATH": "/comfyui",          # KTD9: BASE = LS + "/comfyui"
    "ROOT": "",                        # run root, e.g. <COMM>\flux_edit_<YYYYMMDD>
    "APPROVED_DIR": "",                # <APPROVED_DIR>\<ID>\*.png|jpg
    "ANNOTATIONS": "",                 # annotations.csv (Forge/MA): one row per candidate still, required
    "REAL_NAMED": "",                  # file: one excluded real-named ID per line (required, may be empty)
    "PRIOR_RUN": "",                   # file: sha256,path lines of every image used in the 10-17 run (required)
    "LOCK_PATH": "",                   # gpu-render.lock path
    "COMFY_INPUT": "",                 # <COMFY>\input
    "COMFY_OUTPUT": "",                # <COMFY>\output
}
EXCLUDED_IDS = ("E10",)                 # C-E10: "leave E10 out, test the others"
EXCLUDED_DIRS = ("_needs_derrick", "_dropped")
SEEDS = (432262096973493, 20261028)     # KTD2
N_BODIES = 30
MIN_PER_ASPECT = 3
ASPECTS = {(768, 1344): "9:16", (1344, 768): "16:9"}
WINDOW_ARMS = {"1": ("L", "E", "CTRL"), "1b": ("E8", "L-FULL")}
ARM_UNITS = {"L": 1, "E": 1, "CTRL": 1, "E8": 2, "L-FULL": 1}   # E8 = 8 steps = 2 units (unverified)
WINDOW_S = 1800
WAKE_MAX_S = 420
BUDGET_S_PER_UNIT = 7.6                 # (1800 - 420) / 181 = 7.62
SPLIT_MARGIN_S = 120
WARM_JOBS_BEFORE_PROJECTION = 5
JOB_TIMEOUT_S = 300
DISK_START_GB = 12                      # C7
DISK_STOP_GB = 8                        # C7
LLM_IDLE_WAIT_S = 600                   # wait for "no LLM request in flight"
COMFY_VERSION_PREFIX = "0.38."
C8_BAR = 6                              # 6/30 usable panels (C8, C8-R)

# NEEDS_DEREK: C8 approved a min head-crop size and a B1 misalignment threshold but no number was ever
# written (audit B-P1-3). These are placeholders. They are reported as notes and NEVER gate a run.
NEEDS_DEREK = {"HEAD_CROP_MIN_PX": 256, "B1_MISALIGN_MEAN_ABS": 2.0}


def get(name):
    return os.environ.get("FLUX_EDIT_" + name, _D.get(name, ""))


def require(name):
    v = get(name)
    if not v:
        raise SystemExit(f"STOP: env FLUX_EDIT_{name} is not set")
    return v
