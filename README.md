# EVO-X3 Monorepo (`mono`)

Consolidated home-lab repository for the EVO-X3 (Fedora 44, Strix Halo) and AlienPc (Windows, ComfyUI) setups, built per [records/monorepo-consolidation/PLAN.md](records/monorepo-consolidation/PLAN.md).

## Layout

| Path | Source branch | Live path (after S5/S6 switchover) |
|---|---|---|
| `/` | `u58` (host config, `hosts/`, `records/`, `scripts/`, `config/`) | `/home/derekboone/evo-x3` |
| `x3/render/` | `x3-render` | `/home/evo/AI/render` (symlink) |
| `x3/community/` | `x3-community` (`= x3-linux`) | `/home/evo/AI/community` (symlink) |
| `x3/forge/` | `u58-chat-read-plan` | `/home/evo/AI/forge` (symlink) |
| `alienpc/render/` | `alienpc-render` | `C:\AI\render` (junction) |
| `alienpc/community/` | `alienpc-community` | `C:\AI\community` (junction) |

Full per-file git history is preserved under each prefix (`git log -- <prefix>/<file>`). See [hosts/SETUP-MAP.md](hosts/SETUP-MAP.md) for the live-host inventory and [records/monorepo-consolidation/FREEZE.md](records/monorepo-consolidation/FREEZE.md) for the exact build SHAs and verification proofs.

## Windows clone note

`hosts/x3/live/systemd` contains 4 systemd unit filenames with literal `\x2d` escaping that Git for Windows cannot check out. On Windows, clone with cone sparse-checkout:

```powershell
git clone --no-checkout --filter=blob:none <repo-url> <dir>
git -C <dir> sparse-checkout init --cone --sparse-index
git -C <dir> sparse-checkout set alienpc hosts/alienpc records
git -C <dir> checkout mono
```

## Notes

- Downloads on X3 use `aria2c` with the config at `/home/evo/.config/aria2/aria2.conf`.
- Gitea `derrick/evo-x3` is primary; GitHub `incognitodb86-creator/evo-x3` is the mirror.
