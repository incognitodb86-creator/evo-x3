#!/usr/bin/env bash
# Backed-up EVO-X3 installer for the U56 + Halogen concurrency bundle.
# Never reads or prints secrets (/etc/evo-x3/*.env, ~/.config/evo-x3/llm.env). Every overwritten file is first
# copied to <dir>/_archive/<name>.bak-20261117-u56bundle.
#
#   bash apply-on-x3.sh evo-preview          # as evo: diff bundle ralph.sh vs your live copy (live has uncommitted edits)
#   bash apply-on-x3.sh evo                  # as evo: install ralph.sh, run-u56-pass.sh, fix_plan.u56-item0.md
#   bash apply-on-x3.sh evo --with-tests     # as evo: also install the 3 fixed U56 test files into ~/AI/community + run them
#   bash apply-on-x3.sh evo --with-render    # as evo, AFTER root-apply + llama-swap restart: install ALL U56 Render pipeline/skills/OPERATOR.md fixes & verify
#   bash apply-on-x3.sh evo --with-forge     # as evo, AFTER root-apply + restart: Forge on flash-next-uncensored(-sub), thinking->effort map, grep/find tools, AGENTS.md
#   bash apply-on-x3.sh evo-rollback         # as evo: restore every file this bundle backed up (first backup is kept, never overwritten)
#   sudo bash apply-on-x3.sh root-preview    # show the exact llama-swap.yaml change (read-only)
#   sudo bash apply-on-x3.sh root-apply      # after Derrick's yes: patch llama-swap.yaml (4-slot + vision tower + ttl:300), refresh stage files, dnf install ripgrep fd-find
set -euo pipefail

BUNDLE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STAMP="20261117-u56bundle"
MODE="${1:-help}"
OPT="${2:-}"
FORGE_RC="/home/evo/AI/forge/ralph-community"
LS_LIVE="/etc/evo-x3/llama-swap.yaml"
LS_PATCH="$BUNDLE_ROOT/x3-pi-config/scripts/patch-llama-swap-u56.py"
MARKER="/var/lib/evo-x3/u56-root-applied"
VISION_FILE="/srv/models/flash-next-uncensored-hgn/qwen38-flash-next-vision.hgn"
ROLLBACK_ROOTS=(/home/evo/AI /home/evo/evo-x3 /home/evo/.pi)

backup_to_archive() {
  local target="$1" dir base dst added
  dir="$(dirname "$target")"; base="$(basename "$target")"
  dst="$dir/_archive/${base}.bak-${STAMP}"; added="$dir/_archive/${base}.added-${STAMP}"
  # Keep the FIRST record: a re-run must not replace the original with an already-updated copy.
  if [ -e "$dst" ] || [ -e "$added" ]; then echo "  backup kept -> $dir/_archive/${base}.*-${STAMP}"; return 0; fi
  mkdir -p "$dir/_archive"
  if [ -f "$target" ]; then
    cp -p "$target" "$dst"; echo "  backup -> $dst"
  else
    : > "$added"; echo "  new file (evo-rollback removes it) -> $target"
  fi
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

# Install lists, one "mode<TAB>bundle path<TAB>live path" per line; evo-preview and apply_evo both read them.
test_pairs() {
  local f
  for f in render-master-rules-20261113.json test_writer_pipeline.py test_modular_s3_and_writer_sys.py; do
    printf '0644\tx3-community/scripts/parody/%s\t/home/evo/AI/community/scripts/parody/%s\n' "$f" "$f"
  done
}
render_pairs() {
  local f
  for f in aliases.json render_writer_pipeline.py wp_lint.py wp_router.py fill_request.py resolve.py \
           test_u52_e2e_passthrough.py test_u54_named_e2e.py test_u55_clip_types_e2e.py; do
    printf '0644\tx3-community/scripts/parody/%s\t/home/evo/AI/community/scripts/parody/%s\n' "$f" "$f"
  done
  # Queue/ComfyUI side (AlienPc hardening): beta7_int8HQ templates, LOST_PROMPT abort, remote eviction harvest, 17k+5 snapping.
  for f in scripts/comm.py scripts/remote_comfy.py scripts/make_b2_request.py scripts/run_graph_job.py \
           scripts/tests/test_remote_comfy.py scripts/tests/test_alienpc_comfy_hardening.py sy_test_graph.json \
           templates/two_person.api.json templates/long_continuation.api.json templates/ref2va_16x9.api.json; do
    printf '0644\tx3-community/%s\t/home/evo/AI/community/%s\n' "$f" "$f"
  done
  for f in h3-parody-identity/SKILL.md h3-prompting/SKILL.md h3-prompting/references/wording.md \
           h3-prompting/references/longclip-beat-sheet.md h3-hc-render/SKILL.md video-render/SKILL.md; do
    printf '0644\tx3-community/skills/%s\t/home/evo/AI/community/skills/%s\n' "$f" "$f"
  done
  for f in AGENTS.md OPERATOR.md RUN_ME.md writer_pipeline/personas/current.md writer_pipeline/config.yaml \
           writer_pipeline/writer_prompt.md; do
    printf '0644\tx3-render/%s\t/home/evo/AI/render/%s\n' "$f" "$f"
  done
  for f in x3/render-pi.sh x3/queue-remote.sh; do
    printf '0755\tx3-render/%s\t/home/evo/AI/render/%s\n' "$f" "$f"
  done
}

forge_pairs() {
  printf '0644\tx3-community/agent-shared/AGENTS.md\t/home/evo/AI/community/agent-shared/AGENTS.md\n'
  printf '0644\tx3-community/agent-shared/skills/ralph-loop/SKILL.md\t/home/evo/AI/community/agent-shared/skills/ralph-loop/SKILL.md\n'
  printf '0644\tx3-forge/ralph-community/PROMPT.md\t/home/evo/AI/forge/ralph-community/PROMPT.md\n'
}

install_pairs() {
  local mode src dst
  while IFS=$'\t' read -r mode src dst; do
    backup_to_archive "$dst"
    install -m "$mode" "$BUNDLE_ROOT/$src" "$dst"
  done
}

evo_preview() {
  need_user evo
  echo "=== ralph.sh: live (-) vs bundle (+). Live has uncommitted edits; make sure nothing below is lost. ==="
  diff -u "$FORGE_RC/ralph.sh" "$BUNDLE_ROOT/x3-forge/ralph-community/ralph.sh" || true
  echo "=== --with-tests (first 3), --with-render and --with-forge (AGENTS.md, ralph-loop skill, PROMPT.md) targets ==="
  local mode src dst st note n_edit=0
  while IFS=$'\t' read -r mode src dst; do
    if [ ! -e "$dst" ]; then st="NEW"
    elif cmp -s "$BUNDLE_ROOT/$src" "$dst"; then st="same"
    else st="REPLACE"; fi
    note=""
    if [ -e "$dst" ] && [ -n "$(git -C "$(dirname "$dst")" status --porcelain -- "$(basename "$dst")" 2>/dev/null)" ]; then
      note="   <- uncommitted live edits; review: diff -u $dst $BUNDLE_ROOT/$src"; n_edit=$((n_edit+1))
    fi
    printf '  %-8s %s%s\n' "$st" "$dst" "$note"
  done < <(test_pairs; render_pairs; forge_pairs)
  echo "=== $n_edit target(s) have uncommitted live edits. All replaced files are backed up; evo-rollback restores them. ==="
}

# --with-render/--with-forge point panes at flash-next-uncensored(-sub) with image input. That is only safe once root-apply
# has enabled the vision tower and concurrencyLimit 4 AND llama-swap has been restarted onto that config.
require_root_applied() {
  if [ "${X3_SKIP_ROOT_CHECK:-0}" = 1 ]; then echo "  WARNING: X3_SKIP_ROOT_CHECK=1, skipping the root-apply check"; return 0; fi
  if [ ! -r "$MARKER" ]; then
    echo "ERROR: run 'sudo bash apply-on-x3.sh root-apply' and restart llama-swap before $OPT." >&2
    echo "       (Render would otherwise send images to a text-only engine limited to 1 request.)" >&2
    exit 3
  fi
  local started mark_s start_s
  started="$(systemctl show llama-swap.service -p ActiveEnterTimestamp --value 2>/dev/null || true)"
  if [ -n "$started" ]; then
    mark_s="$(stat -c %Y "$MARKER")"; start_s="$(date -d "$started" +%s 2>/dev/null || echo 0)"
    if [ "$start_s" -lt "$mark_s" ]; then
      echo "ERROR: llama-swap has not been restarted since root-apply ($(date -d "@$mark_s")). Restart it first:" >&2
      echo "       sudo systemctl restart llama-swap" >&2
      exit 3
    fi
  else
    echo "  WARNING: could not read llama-swap start time; make sure it was restarted after root-apply."
  fi
}

evo_rollback() {
  need_user evo
  local n=0 m=0 bak orig
  while IFS= read -r -d '' bak; do
    orig="$(dirname "$(dirname "$bak")")/$(basename "$bak" ".bak-${STAMP}")"
    cp -p "$bak" "$orig"; echo "  restored $orig"; n=$((n+1))
  done < <(find "${ROLLBACK_ROOTS[@]}" -path "*/_archive/*.bak-${STAMP}" -type f -print0 2>/dev/null)
  while IFS= read -r -d '' bak; do
    orig="$(dirname "$(dirname "$bak")")/$(basename "$bak" ".added-${STAMP}")"
    rm -f "$orig" "$bak"; echo "  removed added $orig"; m=$((m+1))
  done < <(find "${ROLLBACK_ROOTS[@]}" -path "*/_archive/*.added-${STAMP}" -type f -print0 2>/dev/null)
  echo "=== rollback restored $n file(s) and removed $m added file(s). run-u56-pass.sh and fix_plan.u56-item0.md are left in place (unused by the old ralph.sh). ==="
}

# Shared pi models.json (~/.pi/agent/models.json; the pane dirs symlink it). Ensures flash-next-uncensored-sub, raises
# flash-next* maxTokens to 65536 and maps pi thinking levels to Halogen reasoning_effort (pi 1.5.2 sends none on its
# own, so every level used to run at the server default "medium"). $1 = yes|no sets image input, keep leaves it.
patch_models_json() {
  local mj=/home/evo/.pi/agent/models.json
  [ -f "$mj" ] || { echo "  WARNING: $mj not found; skipped models.json update"; return 0; }
  backup_to_archive "$mj"
  python3 - "$mj" "$1" <<'PY'
import copy, json, pathlib, sys
p = pathlib.Path(sys.argv[1]); vision = sys.argv[2]
d = json.loads(p.read_text(encoding="utf-8"))
models = d.get("providers", {}).get("x3-local", {}).get("models", [])
base = next((m for m in models if m.get("id") == "flash-next-uncensored"), None)
if base is None:
    sys.exit("ERROR: models.json has no x3-local flash-next-uncensored entry; add it from models.json.example first")
if vision in ("yes", "no"):
    base["input"] = ["text", "image"] if vision == "yes" else ["text"]
effort = {"off": {"temperature": 0.7, "top_p": 0.8, "presence_penalty": 1.5},
          "minimal": {"reasoning_effort": "low"}, "low": {"reasoning_effort": "low"},
          "medium": {"reasoning_effort": "medium"}, "high": {"reasoning_effort": "xhigh"},
          "xhigh": {"reasoning_effort": "xhigh"}}
for m in models:
    if m.get("id") in ("flash-next", "flash-next-uncensored"):
        if int(m.get("maxTokens") or 0) < 65536:
            m["maxTokens"] = 65536
        m.setdefault("samplingParamsByThinkingLevel", effort)
if not any(m.get("id") == "flash-next-uncensored-sub" for m in models):
    sub = copy.deepcopy(base)
    sub.pop("samplingParamsByThinkingLevel", None)
    sub.update(id="flash-next-uncensored-sub", name="X3 local Huihui Qwen3.8-Flash-Next abliterated HGN subagent 128K/8K",
               input=["text"], contextWindow=131072, maxTokens=8192)
    models.append(sub)
p.write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8")
print(f"  updated models.json: flash-next-uncensored input={base['input']} maxTokens={base['maxTokens']}, "
      "thinking->reasoning_effort map, flash-next-uncensored-sub present")
PY
  chmod 0600 "$mj"
}

# --with-forge: one resident model for Forge, its subagents and Ralph; real reasoning effort; search tools; AGENTS.md.
apply_forge() {
  local f
  echo "=== [evo --with-forge] Forge coding setup ==="
  patch_models_json keep
  for f in /home/evo/AI/forge/launcher/forge-pi.sh /home/evo/evo-x3/pi-chats/forge-pi.sh; do
    [ -f "$f" ] && [ ! -L "$f" ] || continue
    if grep -q 'FORGE_MODEL:-x3-local/flash-next}\|FORGE_THINKING:-medium}' "$f"; then
      backup_to_archive "$f"
      sed -i 's|FORGE_MODEL:-x3-local/flash-next}|FORGE_MODEL:-x3-local/flash-next-uncensored}|; s|FORGE_THINKING:-medium}|FORGE_THINKING:-high}|' "$f"
    fi
    if grep -q 'FORGE_MODEL:-x3-local/flash-next-uncensored}' "$f" && grep -q 'FORGE_THINKING:-high}' "$f"; then
      echo "  $f: flash-next-uncensored, --thinking high"
    else
      echo "  WARNING: $f has a different model/thinking line; set flash-next-uncensored + --thinking high by hand"
    fi
  done
  for f in /home/evo/AI/render/x3/render-pi.sh /home/evo/evo-x3/pi-chats/render-pi.sh; do
    [ -f "$f" ] && [ ! -L "$f" ] || continue
    if grep -q 'RENDER_THINKING:-low}' "$f"; then
      backup_to_archive "$f"
      sed -i 's|RENDER_THINKING:-low}|RENDER_THINKING:-medium}|' "$f"
      echo "  $f: --thinking medium (keeps the effort it effectively had before the map)"
    fi
  done
  for f in /home/evo/AI/forge/.pi/settings.json /home/evo/.pi/panes/forge/settings.json; do
    [ -f "$f" ] || continue
    backup_to_archive "$f"
    python3 - "$f" <<'PY'
import json, pathlib, re, sys
p = pathlib.Path(sys.argv[1]); d = json.loads(p.read_text(encoding="utf-8"))
fix = lambda v: re.sub(r"flash-next(?!-uncensored)", "flash-next-uncensored", v) if isinstance(v, str) else v
if "defaultModel" in d:
    d["defaultModel"] = fix(d["defaultModel"])
sub = d.get("subagents")
if isinstance(sub, dict) and isinstance(sub.get("defaultModel"), str):
    v = fix(sub["defaultModel"])
    sub["defaultModel"] = v if v.endswith("-sub") else (v + "-sub" if v.endswith("flash-next-uncensored") else v)
if p.parts[-3:-1] == ("forge", ".pi"):
    tools = d.get("defaultTools")
    if not isinstance(tools, list):
        d["defaultTools"] = ["+grep", "+find", "+ls"]
    else:
        delta = all(isinstance(x, str) and x[:1] in "+-" for x in tools)
        for name in ("grep", "find", "ls"):
            entry = "+" + name if delta else name
            if entry not in tools:
                tools.append(entry)
p.write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8")
print(f"  {p}: defaultModel={d.get('defaultModel')} subagents={(d.get('subagents') or {}).get('defaultModel')} "
      f"defaultTools={d.get('defaultTools')}")
PY
  done
  install_pairs < <(forge_pairs)
  for f in rg fd; do command -v "$f" >/dev/null || echo "  WARNING: '$f' not installed (root-apply installs ripgrep/fd-find); pi grep/find need it"; done
  echo "=== [evo --with-forge] Verifying ==="
  local bad=0
  for f in /home/evo/AI/forge/launcher/forge-pi.sh /home/evo/evo-x3/pi-chats/forge-pi.sh /home/evo/AI/render/x3/render-pi.sh "$FORGE_RC/run-u56-pass.sh" "$FORGE_RC/ralph.sh"; do
    [ -f "$f" ] && { bash -n "$f" || bad=1; }
  done
  for f in /home/evo/.pi/agent/models.json /home/evo/AI/forge/.pi/settings.json /home/evo/.pi/panes/forge/settings.json; do
    [ -f "$f" ] && { python3 -m json.tool "$f" >/dev/null || { echo "  invalid JSON: $f" >&2; bad=1; }; }
  done
  if command -v pi >/dev/null && [ -d /home/evo/.pi/panes/forge ]; then
    ( cd /home/evo/AI/forge && PI_CODING_AGENT_DIR=/home/evo/.pi/panes/forge pi --offline --list-models 2>/dev/null ) \
      | grep -q 'flash-next-uncensored-sub' || { echo "  pi --list-models does not show flash-next-uncensored-sub" >&2; bad=1; }
  fi
  if [ "$bad" != 0 ]; then echo "VERIFY FAILED. Restore everything with: bash $0 evo-rollback" >&2; exit 4; fi
  echo "  OK. Restart the Forge and Render herdr panes to pick it up. Check what pi sends per level any time with:"
  echo "    bash $BUNDLE_ROOT/x3-pi-config/scripts/probe-pi-thinking.sh"
}

apply_evo() {
  need_user evo
  stray_check
  case "$OPT" in ""|--with-tests|--with-render|--with-forge) ;; *) echo "ERROR: unknown option $OPT" >&2; exit 5;; esac
  if [ "$OPT" = "--with-render" ] || [ "$OPT" = "--with-forge" ]; then require_root_applied; fi
  echo "=== [evo] Installing into $FORGE_RC ==="
  backup_to_archive "$FORGE_RC/ralph.sh"
  install -m 0755 "$BUNDLE_ROOT/x3-forge/ralph-community/ralph.sh" "$FORGE_RC/ralph.sh"
  install -m 0755 "$BUNDLE_ROOT/x3-forge/ralph-community/run-u56-pass.sh" "$FORGE_RC/run-u56-pass.sh"
  install -m 0644 "$BUNDLE_ROOT/x3-forge/ralph-community/fix_plan.u56-item0.md" "$FORGE_RC/fix_plan.u56-item0.md"
  backup_to_archive "$FORGE_RC/lint_changed.py"
  install -m 0644 "$BUNDLE_ROOT/x3-forge/ralph-community/lint_changed.py" "$FORGE_RC/lint_changed.py"
  echo "  Forge settings and launchers change only with --with-forge."

  if [ "$OPT" = "--with-tests" ] || [ "$OPT" = "--with-render" ]; then
    echo "=== [evo] Installing the 3 fixed U56 test files into /home/evo/AI/community/scripts/parody ==="
    install_pairs < <(test_pairs)
  fi

  if [ "$OPT" = "--with-render" ]; then
    local par="/home/evo/AI/community/scripts/parody"
    local ren="/home/evo/AI/render"
    echo "=== [evo --with-render] Installing Render pipeline scripts, skills, OPERATOR.md, config.yaml & writer_prompt.md ==="
    install_pairs < <(render_pairs)
    if [ -L /home/evo/evo-x3/pi-chats/render-pi.sh ]; then
      ln -sfn /home/evo/AI/render/x3/render-pi.sh /home/evo/evo-x3/pi-chats/render-pi.sh
    elif [ -f /home/evo/evo-x3/pi-chats/render-pi.sh ]; then
      backup_to_archive /home/evo/evo-x3/pi-chats/render-pi.sh
      install -m 0755 "$BUNDLE_ROOT/x3-render/x3/render-pi.sh" /home/evo/evo-x3/pi-chats/render-pi.sh
    fi
    local vision=yes
    grep -q '^vision=no' "$MARKER" 2>/dev/null && vision=no
    patch_models_json "$vision"
    # The render pane's own settings still pin Gemma subagents (U53); move them to the same resident model.
    local pane=/home/evo/.pi/panes/render/settings.json
    if [ -f "$pane" ] && grep -q 'gemma4-heretic' "$pane"; then
      backup_to_archive "$pane"
      python3 - "$pane" <<'PY'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1]); d = json.loads(p.read_text(encoding="utf-8"))
# Keep any provider prefix and the -sub suffix (gemma4-heretic-sub -> flash-next-uncensored-sub).
if "gemma4-heretic" in str(d.get("defaultModel", "")):
    d["defaultModel"] = d["defaultModel"].replace("gemma4-heretic", "flash-next-uncensored")
sub = d.get("subagents") if isinstance(d.get("subagents"), dict) else None
if sub is not None and "gemma4-heretic" in str(sub.get("defaultModel", "")):
    sub["defaultModel"] = sub["defaultModel"].replace("gemma4-heretic", "flash-next-uncensored")
p.write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8")
print("  updated render pane settings: Gemma pins -> flash-next-uncensored")
PY
    fi
    echo "=== [evo --with-render] Verifying 77-rule compiler gate & U56 parody pytest suite ==="
    if ! /home/evo/AI/render/x3/.venv/bin/python3 "$par/check_writer_prompt_rules.py" "$par/render-master-rules-20261113.json" "$ren/writer_pipeline/writer_prompt.md" --quiet \
       || ! ( cd /home/evo/AI/community/scripts
      PYTHONDONTWRITEBYTECODE=1 uv run --no-project \
        --with pytest --with pyyaml --with pillow --with numpy --with pysbd --with opencv-python-headless \
        python -m pytest -q -p no:cacheprovider \
        parody/test_modular_s3_and_writer_sys.py::test_contact_regex_and_prompt_compiler_77_rules \
        parody/test_writer_pipeline.py \
        parody/test_parody_ba5c.py \
        parody/test_parody_phase1.py \
        parody/test_u52_e2e_passthrough.py \
        parody/test_u54_named_e2e.py \
        parody/test_u55_clip_types_e2e.py \
        parody/test_u37_builder_fixes.py \
        tests/test_remote_comfy.py tests/test_alienpc_comfy_hardening.py tests/test_h3_fix_bcd.py \
        tests/test_run_queue_one_at_a_time.py ); then
      echo "VERIFY FAILED after install. Restore everything with: bash $0 evo-rollback" >&2
      exit 4
    fi
  elif [ "$OPT" = "--with-tests" ]; then
    ( cd /home/evo/AI/community/scripts
      PYTHONDONTWRITEBYTECODE=1 uv run --no-project \
        --with pytest --with pyyaml --with pillow --with numpy --with pysbd --with opencv-python-headless \
        python -m pytest -q -p no:cacheprovider \
        parody/test_modular_s3_and_writer_sys.py::test_contact_regex_and_prompt_compiler_77_rules \
        parody/test_writer_pipeline.py::test_talk_rules )
    echo "  Item 0 is now done in the live tree: mark '- [x] 0' in $FORGE_RC/fix_plan.md and start the loop at item 1."
  elif [ "$OPT" = "--with-forge" ]; then
    apply_forge
  fi
  echo "=== [evo] Done. ==="
}

root_preview() {
  local tmp nv=""; tmp="$(mktemp)"
  [ -f "$VISION_FILE" ] || { nv="--no-vision"; echo "NOTE: $VISION_FILE not found; the vision tower would be skipped."; }
  python3 "$LS_PATCH" $nv "$LS_LIVE" "$tmp"
  diff -u "$LS_LIVE" "$tmp" || true
  rm -f "$tmp"
  command -v rg >/dev/null && command -v fd >/dev/null || echo "root-apply would also run: dnf install -y ripgrep fd-find (for pi's grep/find tools)"
}

root_apply() {
  if [ "$EUID" -ne 0 ]; then echo "ERROR: run 'sudo bash apply-on-x3.sh root-apply'." >&2; exit 1; fi
  local tmp nv="" vision=yes; tmp="$(mktemp)"
  if [ ! -f "$VISION_FILE" ]; then
    nv="--no-vision"; vision=no
    echo "WARNING: $VISION_FILE not found; leaving flash-next-uncensored text-only (Render uses joycaption for stills)."
  fi
  python3 "$LS_PATCH" $nv "$LS_LIVE" "$tmp"
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

  # pi's grep/find tools use ripgrep and fd (Fedora package fd-find provides /usr/bin/fd).
  if ! command -v rg >/dev/null || ! command -v fd >/dev/null; then
    dnf install -y ripgrep fd-find || echo "WARNING: dnf install ripgrep fd-find failed; Forge falls back to bash grep/find"
  fi

  mkdir -p "$(dirname "$MARKER")"
  printf 'applied=%s\nvision=%s\n' "$(date -Is)" "$vision" > "$MARKER"
  chmod 0644 "$MARKER"

  cat <<EOF
=== root-apply done (vision=$vision). Nothing was restarted. ===
Next, when no request is in flight (curl the llama-swap /running endpoint):
  sudo systemctl restart llama-swap
Then check the slot came up (this loads flash-next-uncensored, ~25 s; the key goes over stdin, never argv):
  sudo bash -c '. /etc/evo-x3/llm.env; printf "Authorization: Bearer %s" "\$LLM_KEY_BOX"' \\
    | curl -s -H @- http://127.0.0.1:8080/upstream/flash-next-uncensored/health | jq '{status, slots, vision: .vision.enabled}'
  Expect status "ok", slots 4, vision $([ "$vision" = yes ] && echo true || echo false). If it fails to start, restore with:
  sudo cp /etc/evo-x3/_archive/llama-swap.yaml.bak-${STAMP} /etc/evo-x3/llama-swap.yaml && sudo systemctl restart llama-swap
Then, as evo: bash apply-on-x3.sh evo --with-render   and   bash apply-on-x3.sh evo --with-forge
EOF
}

case "$MODE" in
  evo-preview) evo_preview ;;
  evo) apply_evo ;;
  evo-rollback) evo_rollback ;;
  root-preview) root_preview ;;
  root-apply) root_apply ;;
  *) sed -n '2,13p' "$0" ;;
esac
