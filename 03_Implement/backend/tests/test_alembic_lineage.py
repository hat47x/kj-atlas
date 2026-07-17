from __future__ import annotations

from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

BACKEND_DIR = Path(__file__).resolve().parents[1]


def _script_directory() -> ScriptDirectory:
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    return ScriptDirectory.from_config(cfg)


def test_alembic_has_single_head() -> None:
    script = _script_directory()
    heads = script.get_heads()

    assert heads == ["20260717_0010"], (
        "alembic migration graph must stay linear to avoid stream-merge conflicts: "
        f"unexpected heads={heads}"
    )


def test_auth_identity_migration_is_in_mainline_history() -> None:
    script = _script_directory()

    history_ids = [revision.revision for revision in script.walk_revisions(base="base", head="heads")]

    assert "20260303_0002" in history_ids
    assert "20260314_0005" in history_ids
    assert "20260716_0006" in history_ids
    assert "20260717_0007" in history_ids
    assert "20260717_0008" in history_ids
    assert "20260717_0009" in history_ids
    assert "20260717_0010" in history_ids
    assert (
        history_ids.index("20260717_0010")
        < history_ids.index("20260717_0009")
        < history_ids.index("20260717_0008")
        < history_ids.index("20260717_0007")
        < history_ids.index("20260716_0006")
        < history_ids.index("20260314_0005")
        < history_ids.index("20260303_0002")
        < history_ids.index("20260211_0001")
    )
