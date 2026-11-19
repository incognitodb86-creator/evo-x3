"""Smoke tests for {{ cookiecutter.package_name }}."""
from __future__ import annotations

import {{ cookiecutter.package_name }}


def test_version_defined() -> None:
    assert {{ cookiecutter.package_name }}.__version__
