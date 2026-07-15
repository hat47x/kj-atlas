from __future__ import annotations

import json
import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from kj_atlas_api.db import get_db
from kj_atlas_api.main import app
from kj_atlas_api.models import Base
from kj_atlas_api.settings import settings
from tests.level2.mock_idp import app as mock_idp_app
from tests.level2.mock_sp import MockSpRuntime

FIXTURE_DIR = Path(__file__).parent / "level2" / "fixtures"
DIAG_DIR_ENV = "KJ_ATLAS_LEVEL2_DIAG_DIR"
pytestmark = pytest.mark.auth_level2


@contextmanager
def _sqlite_client(tmp_path) -> Iterator[TestClient]:
    db_path = tmp_path / "auth_level2.sqlite3"
    engine = create_engine(f"sqlite:///{db_path}")
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    def _get_test_db():
        db = session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_test_db
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def _sample_payload(doc_id: str) -> dict[str, object]:
    return {
        "version": 1,
        "id": doc_id,
        "title": "auth-level2-test",
        "createdAt": "2026-02-11T00:00:00Z",
        "updatedAt": "2026-02-11T00:00:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [{"id": "card-1", "text": "alpha", "x": 0, "y": 0}],
        "edges": [],
        "islands": [],
    }


def _load_profile(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_diag(profile_name: str, result: dict[str, object]) -> None:
    configured_dir = os.getenv(DIAG_DIR_ENV)
    if not configured_dir:
        return

    diag_dir = Path(configured_dir)
    diag_dir.mkdir(parents=True, exist_ok=True)
    (diag_dir / f"{profile_name}.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def test_level2_diagnostics_require_explicit_canonical_path(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv(DIAG_DIR_ENV, raising=False)

    _write_diag("disabled", {"status": "ok"})
    assert not (tmp_path / ".tmp").exists()

    diag_dir = tmp_path / ".artifacts" / "auth-level2" / "legacy-federation"
    monkeypatch.setenv(DIAG_DIR_ENV, str(diag_dir))
    _write_diag("enabled", {"status": "ok"})

    assert json.loads((diag_dir / "enabled.json").read_text(encoding="utf-8")) == {
        "status": "ok"
    }


@pytest.mark.parametrize(
    "profile_path",
    sorted(FIXTURE_DIR.glob("provider_profile_*.json")),
    ids=lambda p: p.stem,
)
def test_auth_federation_level2_profiles(profile_path: Path, tmp_path) -> None:
    profile = _load_profile(profile_path)

    original_allow_jit = settings.allow_jit_provisioning
    original_auth_user_field = settings.auth_user_field
    original_auth_provider_field = settings.auth_provider_field
    original_auth_email_field = settings.auth_email_field
    original_auth_name_field = settings.auth_name_field
    original_auth_subject_field = settings.auth_subject_field

    settings.allow_jit_provisioning = True
    settings.auth_user_field = profile["settingsOverride"]["auth_user_field"]
    settings.auth_provider_field = profile["settingsOverride"]["auth_provider_field"]
    settings.auth_email_field = profile["settingsOverride"]["auth_email_field"]
    settings.auth_name_field = profile["settingsOverride"]["auth_name_field"]
    settings.auth_subject_field = profile["settingsOverride"]["auth_subject_field"]

    try:
        with _sqlite_client(tmp_path) as _:
            runtime = MockSpRuntime(backend_app=app, idp_app=mock_idp_app)
            with TestClient(runtime.app) as sp_client:
                response = sp_client.post(
                    "/proxy/docs",
                    json={
                        "provider": profile["provider"],
                        "claims": profile["claims"],
                        "profile": profile,
                        "document_id": f"doc-{profile['name']}",
                        "payload": _sample_payload(f"doc-{profile['name']}"),
                    },
                )

                assert response.status_code == 200
                body = response.json()
                _write_diag(str(profile["name"]), body)

                assert body["putStatus"] == 200
                assert body["getStatus"] == 200

                forwarded_headers = body["forwardedHeaders"]
                assert profile["headerMap"]["user"] in forwarded_headers
                assert profile["headerMap"]["groups"] in forwarded_headers

                if profile.get("includeAmrAcr", True):
                    assert profile["headerMap"]["amr"] in forwarded_headers
                    assert profile["headerMap"]["acr"] in forwarded_headers
                else:
                    assert profile["headerMap"]["amr"] not in forwarded_headers
                    assert profile["headerMap"]["acr"] not in forwarded_headers
    finally:
        settings.allow_jit_provisioning = original_allow_jit
        settings.auth_user_field = original_auth_user_field
        settings.auth_provider_field = original_auth_provider_field
        settings.auth_email_field = original_auth_email_field
        settings.auth_name_field = original_auth_name_field
        settings.auth_subject_field = original_auth_subject_field
