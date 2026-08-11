from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker

from kj_atlas_api.models import Base
from kj_atlas_api.saas_auth_state import DatabaseSaasAuthStateStore


def _stores(tmp_path) -> tuple[DatabaseSaasAuthStateStore, DatabaseSaasAuthStateStore]:
    engine = create_engine(
        f"sqlite:///{tmp_path / 'shared-auth.db'}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)
    return DatabaseSaasAuthStateStore(factory), DatabaseSaasAuthStateStore(factory)


def test_two_instances_share_and_atomically_rotate_session_version(tmp_path) -> None:
    worker_a, worker_b = _stores(tmp_path)

    initial = worker_a.current_or_create_session_version(
        principal_id="principal-1", new_version="version-a"
    )
    observed = worker_b.current_or_create_session_version(
        principal_id="principal-1", new_version="version-b"
    )

    assert observed == initial == "version-a"
    assert worker_b.rotate_session_version(
        principal_id="principal-1",
        expected_version="version-a",
        new_version="version-c",
    )
    assert not worker_a.rotate_session_version(
        principal_id="principal-1",
        expected_version="version-a",
        new_version="version-d",
    )


def test_preflight_fails_when_shared_auth_tables_are_missing(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'unmigrated.db'}")
    factory = sessionmaker(bind=engine, class_=Session)

    with pytest.raises(OperationalError):
        DatabaseSaasAuthStateStore(factory).preflight()
