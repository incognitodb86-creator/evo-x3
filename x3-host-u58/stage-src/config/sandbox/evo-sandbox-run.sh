#!/usr/bin/env bash
set -euo pipefail

# EVO-X3 U17 Rootless Podman Code Sandbox Wrapper (Fixed, Non-Overridable Flags)
# Adapted from amedeos/another-ai-sandbox (Plan P1-4, R12, KTD11).
#
# SECURITY PROPERTIES:
# - Must execute as dedicated unprivileged user `evosandbox` (NOT the llama-swap user)
# - `evosandbox` has NO read permissions on /etc/evo-x3/*, /srv/models, or ~/.ssh
# - Callers pass CODE/COMMAND ONLY inside a single bounded scratch dir; flags/mounts/images are fixed
# - Default seccomp + SELinux confinement kept active (NEVER seccomp=unconfined or label=disable)
# - Network disabled (--network=none)

SANDBOX_IMAGE="registry.fedoraproject.org/fedora-minimal:44@sha256:PIN_DIGEST_AT_BUILD_TIME"
SCRATCH_ROOT="/var/lib/evosandbox/scratch"
TIMEOUT_SECONDS=60
PIDS_LIMIT=64
MEM_LIMIT="2g"
CPU_LIMIT="2.0"

if [[ "$(id -un)" != "evosandbox" ]]; then
  echo "ERROR: evo-sandbox-run.sh must run as unprivileged user 'evosandbox'." >&2
  exit 1
fi

if [[ $# -lt 1 ]]; then
  echo "Usage: evo-sandbox-run.sh <script-filename-in-scratch>" >&2
  exit 2
fi

SCRIPT_NAME="$(basename "$1")"
HOST_SCRATCH="${SCRATCH_ROOT}/run-$(date +%s)-$$"
mkdir -p "$HOST_SCRATCH"
trap 'rm -rf "$HOST_SCRATCH"' EXIT

if [[ ! -f "${SCRATCH_ROOT}/incoming/${SCRIPT_NAME}" ]]; then
  echo "ERROR: Script not found in ${SCRATCH_ROOT}/incoming/${SCRIPT_NAME}" >&2
  exit 2
fi

cp "${SCRATCH_ROOT}/incoming/${SCRIPT_NAME}" "${HOST_SCRATCH}/task.sh"
chmod 0700 "${HOST_SCRATCH}/task.sh"

# Fixed, non-overridable rootless Podman execution
exec timeout --signal=KILL "${TIMEOUT_SECONDS}" \
  podman run --rm \
    --userns=keep-id \
    --user 65534:65534 \
    --cap-drop=ALL \
    --security-opt=no-new-privileges \
    --read-only \
    --tmpfs /tmp:rw,noexec,nosuid,size=256m \
    --network=none \
    --cpus="${CPU_LIMIT}" \
    --memory="${MEM_LIMIT}" \
    --pids-limit="${PIDS_LIMIT}" \
    -v "${HOST_SCRATCH}:/workspace:rw,Z" \
    -w /workspace \
    "$SANDBOX_IMAGE" \
    /bin/sh /workspace/task.sh
