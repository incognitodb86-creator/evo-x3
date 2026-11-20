# Max Architect 3, 2026-11-13 (Derrick t1355): archived .bak copies are not part of the suite.
import pytest

collect_ignore_glob = ["_archive/*", "bak-*"]


@pytest.fixture(autouse=True)
def _isolate_comfy_input_community(tmp_path_factory, monkeypatch):
    """Redirect build_request.COMFY_INPUT_COMMUNITY into tmp_path so tests never write PNGs into the repo."""
    try:
        import build_request as br
    except Exception:
        return
    monkeypatch.setattr(br, "COMFY_INPUT_COMMUNITY", tmp_path_factory.mktemp("comfy_in") / "community")
