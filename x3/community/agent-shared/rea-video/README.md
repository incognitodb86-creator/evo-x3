# REA-Video User Capabilities (`RV1`)

Upgrade-safe `rea-video` user capability files for `minimax-h3-10eros-beta7`.

## Apply on EVO-X3 (Max / X3 Forge)

```bash
mkdir -p ~/.rea-video/capabilities/models
cp agent-shared/rea-video/capabilities/models/video.yaml ~/.rea-video/capabilities/models/video.yaml
cp agent-shared/rea-video/capabilities/prompting.yaml ~/.rea-video/capabilities/prompting.yaml
```

## Verify on EVO-X3 (after `RV0` installs `rea-video`)

```bash
rea-video models minimax-h3-10eros-beta7
python3 ~/AI/tools/rea-video/scripts/validate_capabilities.py
```

## Rollback

```bash
rm -f ~/.rea-video/capabilities/models/video.yaml ~/.rea-video/capabilities/prompting.yaml
```
