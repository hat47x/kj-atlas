from __future__ import annotations

import re
from pathlib import Path

from kj_atlas_api.database_support import (
    registered_database_support,
    verified_database_backends,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = REPO_ROOT / "03_Implement" / "backend"


def test_verified_backend_message_order_comes_from_registry() -> None:
    registered = registered_database_support()

    assert verified_database_backends() == tuple(
        support.backend for support in registered if support.is_verified
    )


def test_every_external_verified_backend_declares_driver_and_real_db_marker() -> None:
    supports = registered_database_support()

    for support in supports:
        if support.backend == "sqlite":
            assert support.optional_dependency is None
            assert support.test_marker is None
            continue
        assert support.optional_dependency is not None, support.backend
        assert support.test_marker is not None, support.backend


def test_driver_extras_markers_tests_and_ci_stay_synchronized() -> None:
    pyproject = (BACKEND_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    workflow = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(
        encoding="utf-8"
    )
    test_sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (BACKEND_ROOT / "tests").glob("test_*.py")
    )
    dependencies = {
        support.optional_dependency
        for support in registered_database_support()
        if support.optional_dependency is not None
    }
    markers = {
        support.test_marker
        for support in registered_database_support()
        if support.test_marker is not None
    }

    for dependency in dependencies:
        assert re.search(rf"(?m)^{re.escape(dependency)}\s*=\s*\[", pyproject)
        assert re.search(rf'pip install -e "\.\[[^\]]*\b{re.escape(dependency)}\b', workflow)
    for marker in markers:
        assert f'"{marker}: tests that require ' in pyproject
        assert f"@pytest.mark.{marker}" in test_sources
        assert re.search(rf"pytest -m ['\"]?{re.escape(marker)}(?:['\"]|\s|$)", workflow)


def test_canonical_support_matrix_lists_every_registered_backend_once() -> None:
    matrix = (REPO_ROOT / "02_Architecture" / "database_portability.md").read_text(
        encoding="utf-8"
    )

    for support in registered_database_support():
        rows = re.findall(
            rf"(?m)^\|[^\n|]+\|\s*{re.escape(support.backend)}\s*\|\s*"
            rf"{re.escape(support.family)}\s*\|\s*{support.support_level.title()}\s*\|",
            matrix,
        )
        assert len(rows) == 1, support.backend
