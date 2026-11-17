#!/usr/bin/env bash
# Backed-up EVO-X3 installer for the U56 + Halogen concurrency bundle.
# Never reads or prints secrets (/etc/evo-x3/*.env, ~/.config/evo-x3/llm.env). Every overwritten file is first
# copied to <dir>/_archive/<name>.bak-20261117-u56bundle.
#
#   bash apply-on-x3.sh evo-preview          # as evo: diff bundle ralph.sh vs your live copy (live has uncommitted edits)
#   bash apply-on-x3.sh evo                  # as evo: install ralph.sh, run-u56-pass.sh, fix_plan.u56-item0.md
#   bash apply-on-x3.sh evo --with-tests     # as evo: also install the 3 fixed U56 test files into ~/AI/community + run them
#   bash apply-on-x3.sh evo --with-render    # as evo: install ALL U56 + Render pipeline + skills + OPERATOR.md + config.yaml + writer_prompt.md fixes & verify
#   sudo bash apply-on-x3.sh root-preview    # show the exact llama-swap.yaml change (read-only)
#   sudo bash apply-on-x3.sh root-apply      # after Derrick's yes: patch llama-swap.yaml (4-slot + vision tower + ttl:300), refresh stage files
set -euo pipefail

BUNDLE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STAMP="20261117-u56bundle"
MODE="${1:-help}"
OPT="${2:-}"
FORGE_RC="/home/evo/AI/forge/ralph-community"
LS_LIVE="/etc/evo-x3/llama-swap.yaml"
LS_PATCH="$BUNDLE_ROOT/x3-pi-config/scripts/patch-llama-swap-u56.py"

backup_to_archive() {
  local target="$1" dir base
  [ -f "$target" ] || return 0
  dir="$(dirname "$target")"; base="$(basename "$target")"
  mkdir -p "$dir/_archive"
  cp -p "$target" "$dir/_archive/${base}.bak-${STAMP}"
  echo "  backup -> $dir/_archive/${base}.bak-${STAMP}"
}

need_user() {
  if [ "$(id -un)" != "$1" ]; then echo "ERROR: run this mode as user '$1'." >&2; exit 1; fi
}

stray_check() {
  if ps -eo pid,ppid,pgid,etime,cmd | grep -E "ralph\.sh|pi .*PROMPT\.md" | grep -v grep; then
    echo "ERROR: a ralph.sh loop or headless pi pass (listed above) is still running; stop it first (kill -- -<pgid>)." >&2
    exit 2
  fi
}

evo_preview() {
  need_user evo
  echo "=== ralph.sh: live (-) vs bundle (+). Live has uncommitted edits; make sure nothing below is lost. ==="
  diff -u "$FORGE_RC/ralph.sh" "$BUNDLE_ROOT/x3-forge/ralph-community/ralph.sh" || true
}

apply_evo() {
  need_user evo
  stray_check
  echo "=== [evo] Installing into $FORGE_RC ==="
  backup_to_archive "$FORGE_RC/ralph.sh"
  install -m 0755 "$BUNDLE_ROOT/x3-forge/ralph-community/ralph.sh" "$FORGE_RC/ralph.sh"
  install -m 0755 "$BUNDLE_ROOT/x3-forge/ralph-community/run-u56-pass.sh" "$FORGE_RC/run-u56-pass.sh"
  install -m 0644 "$BUNDLE_ROOT/x3-forge/ralph-community/fix_plan.u56-item0.md" "$FORGE_RC/fix_plan.u56-item0.md"
  echo "  Forge .pi/settings.json is NOT touched (live already pins flash-next-uncensored + 131K compaction)."

  if [ "$OPT" = "--with-tests" ] || [ "$OPT" = "--with-render" ]; then
    local par="/home/evo/AI/community/scripts/parody"
    echo "=== [evo] Installing the 3 fixed U56 test files into $par ==="
    for f in render-master-rules-20261113.json test_writer_pipeline.py test_modular_s3_and_writer_sys.py; do
      backup_to_archive "$par/$f"
      install -m 0644 "$BUNDLE_ROOT/x3-community/scripts/parody/$f" "$par/$f"
    done
  fi

  if [ "$OPT" = "--with-render" ]; then
    local par="/home/evo/AI/community/scripts/parody"
    local skroot="/home/evo/AI/community/skills"
    local ren="/home/evo/AI/render"
    echo "=== [evo --with-render] Installing Render pipeline scripts, skills, OPERATOR.md, config.yaml & writer_prompt.md ==="
    for f in aliases.json render_writer_pipeline.py wp_lint.py wp_router.py fill_request.py resolve.py test_u52_e2e_passthrough.py test_u54_named_e2e.py test_u55_clip_types_e2e.py; do
      backup_to_archive "$par/$f"
      install -m 0644 "$BUNDLE_ROOT/x3-community/scripts/parody/$f" "$par/$f"
    done
    for sk in h3-parody-identity/SKILL.md h3-prompting/SKILL.md h3-prompting/references/wording.md h3-prompting/references/longclip-beat-sheet.md h3-hc-render/SKILL.md video-render/SKILL.md; do
      backup_to_archive "$skroot/$sk"
      install -m 0644 "$BUNDLE_ROOT/x3-community/skills/$sk" "$skroot/$sk"
    done
    for rf in AGENTS.md OPERATOR.md RUN_ME.md writer_pipeline/personas/current.md writer_pipeline/config.yaml writer_pipeline/writer_prompt.md; do
      backup_to_archive "$ren/$rf"
      install -m 0644 "$BUNDLE_ROOT/x3-render/$rf" "$ren/$rf"
    done
    for rx in x3/render-pi.sh x3/queue-remote.sh; do
      backup_to_archive "$ren/$rx"
      install -m 0755 "$BUNDLE_ROOT/x3-render/$rx" "$ren/$rx"
    done
    if [ -L /home/evo/evo-x3/pi-chats/render-pi.sh ]; then
      ln -sfn /home/evo/AI/render/x3/render-pi.sh /home/evo/evo-x3/pi-chats/render-pi.sh
    elif [ -f /home/evo/evo-x3/pi-chats/render-pi.sh ]; then
      backup_to_archive /home/evo/evo-x3/pi-chats/render-pi.sh
      install -m 0755 "$BUNDLE_ROOT/x3-render/x3/render-pi.sh" /home/evo/evo-x3/pi-chats/render-pi.sh
    fi
    if [ -f /home/evo/.pi/agent/models.json ]; then
      backup_to_archive /home/evo/.pi/agent/models.json
      python3 - /home/evo/.pi/agent/models.json <<'PY'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1])
d = json.loads(p.read_text(encoding="utf-8"))
models = d.get("providers", {}).get("x3-local", {}).get("models", [])
has_sub = any(m.get("id") == "flash-next-uncensored-sub" for m in models)
for m in models:
    if m.get("id") == "flash-next-uncensored":
        m["input"] = ["text", "image"]
        if not has_sub:
            sub = dict(m)
            sub["id"] = "flash-next-uncensored-sub"
            sub["name"] = "X3 local Huihui Qwen3.8-Flash-Next abliterated HGN subagent 128K/8K"
            sub["input"] = ["text"]
            sub["contextWindow"] = 131072
            sub["maxTokens"] = 8192
            models.append(sub)
        break
p.write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8")
PY
      chmod 0600 /home/evo/.pi/agent/models.json
      echo "  updated /home/evo/.pi/agent/models.json (flash-next-uncensored input=['text','image'] + flash-next-uncensored-sub)"
    fi
    echo "=== [evo --with-render] Verifying 77-rule compiler gate & U56 parody pytest suite ==="
    /home/evo/AI/render/x3/.venv/bin/python3 "$par/check_writer_prompt_rules.py" "$par/render-master-rules-20261113.json" "$ren/writer_pipeline/writer_prompt.md" --quiet
    ( cd /home/evo/AI/community/scripts
      PYTHONDONTWRITEBYTECODE=1 uv run --no-project \
        --with pytest --with pyyaml --with pillow --with numpy --with pysbd --with opencv-python-headless \
        python -m pytest -q -p no:cacheprovider \
        parody/test_modular_s3_and_writer_sys.py::test_contact_regex_and_prompt_compiler_77_rules \
        parody/test_writer_pipeline.py \
        parody/test_u52_e2e_passthrough.py \
        parody/test_u54_named_e2e.py \
        parody/test_u55_clip_types_e2e.py \
        parody/test_u37_builder_fixes.py )
  elif [ "$OPT" = "--with-tests" ]; then
    ( cd /home/evo/AI/community/scripts
      PYTHONDONTWRITEBYTECODE=1 uv run --no-project \
        --with pytest --with pyyaml --with pillow --with numpy --with pysbd --with opencv-python-headless \
        python -m pytest -q -p no:cacheprovider \
        parody/test_modular_s3_and_writer_sys.py::test_contact_regex_and_prompt_compiler_77_rules \
        parody/test_writer_pipeline.py::test_talk_rules )
    echo "  Item 0 is now done in the live tree: mark '- [x] 0' in $FORGE_RC/fix_plan.md and start the loop at item 1."
  fi
  echo "=== [evo] Done. ==="
}

root_preview() {
  local tmp; tmp="$(mktemp)"
  python3 "$LS_PATCH" "$LS_LIVE" "$tmp"
  diff -u "$LS_LIVE" "$tmp" || true
  rm -f "$tmp"
}

root_apply() {
  if [ "$EUID" -ne 0 ]; then echo "ERROR: run 'sudo bash apply-on-x3.sh root-apply'." >&2; exit 1; fi
  local tmp; tmp="$(mktemp)"
  python3 "$LS_PATCH" "$LS_LIVE" "$tmp"
  echo "=== Validating patched llama-swap.yaml (keys loaded in a subshell, never printed) ==="
  ( set -a; [ -f /etc/evo-x3/llm.env ] && . /etc/evo-x3/llm.env; set +a
    /usr/local/bin/llama-swap -config "$tmp" -validate )
  backup_to_archive "$LS_LIVE"
  install -m 0644 -o root -g root "$tmp" "$LS_LIVE"
  rm -f "$tmp"

  local owc=/etc/containers/systemd/open-webui.container
  if [ -f "$owc" ] && grep -q -- '--forwarded-allow-ips \*' "$owc"; then
    backup_to_archive "$owc"
    sed -i 's/--forwarded-allow-ips \*/--forwarded-allow-ips 127.0.0.1/' "$owc"
    echo "  open-webui: --forwarded-allow-ips * -> 127.0.0.1 (takes effect on next open-webui restart)"
  fi

  # Staged-only (not running) U14/U17/U18 files: refresh so a later setup-fedora.sh run gets the fixed versions.
  local st=/opt/evo-x3/stage/config
  if [ -d "$st" ]; then
    for rel in proxy/evo-rate-proxy.py proxy/evo-mcp-proxy.py sandbox/evo-sandbox-run.sh \
               playwright/playwright-egress-firewall.sh playwright/playwright-mcp.container; do
      backup_to_archive "$st/$rel"
      install -m 0755 "$BUNDLE_ROOT/x3-pi-config/stage-src/config/$rel" "$st/$rel"
    done
    chmod 0644 "$st/playwright/playwright-mcp.container"
  fi

  cat <<'EOF'
=== root-apply done. Nothing was restarted. ===
Next, when no request is in flight (curl the llama-swap /running endpoint):
  sudo systemctl restart llama-swap
Then, as evo, add "flash-next-uncensored-sub" to ~/.pi/agent/models.json (copy the entry from
x3-pi-config/config/pi-evo/models.json.example) before pointing any subagents.defaultModel at it.
EOF
}

case "$MODE" in
  evo-preview) evo_preview ;;
  evo) apply_evo ;;
  root-preview) root_preview ;;
  root-apply) root_apply ;;
  *) sed -n '2,11p' "$0" ;;
esac
