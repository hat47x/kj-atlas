from __future__ import annotations

import os
import sqlite3
import subprocess
from pathlib import Path

import pytest

from kj_atlas_api.models import (
    LOCAL_DEFAULT_TENANT_ID,
    DocumentAccessAdminAuditEventRow,
)


BACKEND_DIR = Path(__file__).resolve().parents[1]
TIMESTAMP = "2026-07-17T00:00:00Z"


def _run_alembic(db_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["KJ_ATLAS_DATABASE_URL"] = f"sqlite:///{db_path}"
    return subprocess.run(
        ["alembic", *args],
        cwd=BACKEND_DIR,
        env=env,
        check=False,
        text=True,
        capture_output=True,
    )


def _insert_tenant(con: sqlite3.Connection, tenant_id: str) -> None:
    con.execute(
        """
        INSERT INTO tenants (id, display_name, lifecycle_state, created_at, updated_at)
        VALUES (?, ?, 'active', ?, ?)
        """,
        (tenant_id, tenant_id, TIMESTAMP, TIMESTAMP),
    )


def _insert_document(con: sqlite3.Connection, tenant_id: str, doc_id: str) -> None:
    con.execute(
        """
        INSERT INTO documents (tenant_id, id, version, updated_at, payload_json)
        VALUES (?, ?, 1, ?, '{}')
        """,
        (tenant_id, doc_id, TIMESTAMP),
    )


def _insert_audit_event(
    con: sqlite3.Connection,
    *,
    event_id: str,
    tenant_id: str,
    doc_id: str,
) -> None:
    con.execute(
        """
        INSERT INTO document_access_admin_audit_events (
            event_id, tenant_id, principal_id, doc_id, action, decision,
            policy_version, capability_version, correlation_id, occurred_at
        ) VALUES (?, ?, 'user-1', ?, 'document.policy.update', 'allowed',
                  'policy-v1', 'capability-v1', ?, ?)
        """,
        (event_id, tenant_id, doc_id, f"correlation-{event_id}", TIMESTAMP),
    )


def test_model_declares_tenant_document_composite_foreign_key() -> None:
    constraints = DocumentAccessAdminAuditEventRow.__table__.foreign_key_constraints
    document_constraints = [
        constraint
        for constraint in constraints
        if {element.target_fullname for element in constraint.elements}
        == {"documents.tenant_id", "documents.id"}
    ]
    assert len(document_constraints) == 1
    assert document_constraints[0].ondelete == "RESTRICT"


def test_migration_upgrades_existing_valid_audit_rows_without_loss(tmp_path: Path) -> None:
    db_path = tmp_path / "document-access-admin-audit-existing.sqlite3"
    upgrade = _run_alembic(db_path, "upgrade", "20260717_0011")
    assert upgrade.returncode == 0, upgrade.stderr

    con = sqlite3.connect(db_path)
    try:
        _insert_document(con, LOCAL_DEFAULT_TENANT_ID, "existing-doc")
        _insert_audit_event(
            con,
            event_id="existing-audit",
            tenant_id=LOCAL_DEFAULT_TENANT_ID,
            doc_id="existing-doc",
        )
        con.commit()
    finally:
        con.close()

    upgrade = _run_alembic(db_path, "upgrade", "head")
    assert upgrade.returncode == 0, upgrade.stderr

    con = sqlite3.connect(db_path)
    try:
        assert con.execute(
            "SELECT event_id, tenant_id, doc_id FROM document_access_admin_audit_events"
        ).fetchall() == [("existing-audit", LOCAL_DEFAULT_TENANT_ID, "existing-doc")]
    finally:
        con.close()


def test_migration_stops_without_deleting_orphaned_audit_rows(tmp_path: Path) -> None:
    db_path = tmp_path / "document-access-admin-audit-orphan.sqlite3"
    upgrade = _run_alembic(db_path, "upgrade", "20260717_0011")
    assert upgrade.returncode == 0, upgrade.stderr

    con = sqlite3.connect(db_path)
    try:
        _insert_audit_event(
            con,
            event_id="orphan-audit",
            tenant_id=LOCAL_DEFAULT_TENANT_ID,
            doc_id="missing-doc",
        )
        con.commit()
    finally:
        con.close()

    upgrade = _run_alembic(db_path, "upgrade", "head")
    assert upgrade.returncode != 0
    assert "orphaned or cross-tenant audit event exists" in upgrade.stderr

    con = sqlite3.connect(db_path)
    try:
        assert con.execute(
            "SELECT event_id, tenant_id, doc_id FROM document_access_admin_audit_events"
        ).fetchall() == [("orphan-audit", LOCAL_DEFAULT_TENANT_ID, "missing-doc")]
    finally:
        con.close()


def test_migration_creates_minimal_tenant_scoped_admin_audit_table(tmp_path: Path) -> None:
    db_path = tmp_path / "document-access-admin-audit.sqlite3"
    upgrade = _run_alembic(db_path, "upgrade", "head")
    assert upgrade.returncode == 0, upgrade.stderr

    con = sqlite3.connect(db_path)
    con.execute("PRAGMA foreign_keys = ON")
    try:
        columns = {
            row[1]
            for row in con.execute(
                "PRAGMA table_info('document_access_admin_audit_events')"
            )
        }
        assert columns == {
            "event_id",
            "tenant_id",
            "principal_id",
            "doc_id",
            "action",
            "decision",
            "policy_version",
            "capability_version",
            "correlation_id",
            "occurred_at",
        }
        assert not columns.intersection(
            {"policy_binding_id", "policy_ref", "token", "secret", "title", "content"}
        )
        document_foreign_key_pairs = {
            (row[3], row[4])
            for row in con.execute(
                "PRAGMA foreign_key_list('document_access_admin_audit_events')"
            )
            if row[2] == "documents"
        }
        assert document_foreign_key_pairs == {
            ("tenant_id", "tenant_id"),
            ("doc_id", "id"),
        }

        _insert_document(con, LOCAL_DEFAULT_TENANT_ID, "doc-1")
        con.execute(
            """
            INSERT INTO document_access_admin_audit_events (
                event_id, tenant_id, principal_id, doc_id, action, decision,
                policy_version, capability_version, correlation_id, occurred_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "audit-1",
                LOCAL_DEFAULT_TENANT_ID,
                "user-1",
                "doc-1",
                "document.policy.update",
                "allowed",
                "policy-v1",
                "capability-v1",
                "correlation-1",
                TIMESTAMP,
            ),
        )
        con.commit()

        _insert_tenant(con, "tenant-b")
        _insert_document(con, "tenant-b", "tenant-b-only-doc")
        with pytest.raises(sqlite3.IntegrityError):
            con.execute(
                """
                INSERT INTO document_access_admin_audit_events (
                    event_id, tenant_id, principal_id, doc_id, action, decision,
                    policy_version, capability_version, correlation_id, occurred_at
                ) VALUES ('audit-cross-tenant', ?, 'user-1', 'tenant-b-only-doc',
                          'document.policy.update', 'allowed', 'policy-v1',
                          'capability-v1', 'correlation-cross-tenant', ?)
                """,
                (LOCAL_DEFAULT_TENANT_ID, TIMESTAMP),
            )
        con.rollback()

        with pytest.raises(sqlite3.IntegrityError):
            con.execute(
                """
                INSERT INTO document_access_admin_audit_events (
                    event_id, tenant_id, principal_id, doc_id, action, decision,
                    policy_version, capability_version, correlation_id, occurred_at
                ) VALUES ('audit-2', ?, 'user-1', 'doc-1', 'document.read',
                          'allowed', 'policy-v1', 'capability-v1', 'correlation-2', ?)
                """,
                (LOCAL_DEFAULT_TENANT_ID, TIMESTAMP),
            )
        con.rollback()
    finally:
        con.close()


def test_migration_downgrade_removes_only_admin_audit_table(tmp_path: Path) -> None:
    db_path = tmp_path / "document-access-admin-audit-downgrade.sqlite3"
    upgrade = _run_alembic(db_path, "upgrade", "head")
    assert upgrade.returncode == 0, upgrade.stderr

    downgrade = _run_alembic(db_path, "downgrade", "20260717_0010")
    assert downgrade.returncode == 0, downgrade.stderr

    con = sqlite3.connect(db_path)
    try:
        tables = {
            row[0]
            for row in con.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }
        assert "document_access_admin_audit_events" not in tables
        assert "document_access_metadata" in tables
    finally:
        con.close()
