from __future__ import annotations

from unittest.mock import Mock

import pytest

from kj_atlas_api.tenant_context import TenantContext
from kj_atlas_api.tenant_db_guard import apply_database_tenant_context


def _tenant(tenant_id: str = "tenant-a") -> TenantContext:
    return TenantContext(
        tenant_id=tenant_id,
        membership_id="membership-a",
        resolved_by="verified_claim",
    )


def _session_for_dialect(dialect_name: str) -> Mock:
    session = Mock()
    session.get_bind.return_value.dialect.name = dialect_name
    return session


def test_postgres_context_uses_bound_transaction_local_set_config() -> None:
    session = _session_for_dialect("postgresql")

    apply_database_tenant_context(db=session, tenant=_tenant("tenant-a' OR true --"))

    session.execute.assert_called_once()
    statement, parameters = session.execute.call_args.args
    assert "set_config('kj_atlas.tenant_id', :tenant_id, true)" in str(statement)
    assert parameters == {"tenant_id": "tenant-a' OR true --"}
    assert "tenant-a" not in str(statement)


def test_sqlite_context_is_noop() -> None:
    session = _session_for_dialect("sqlite")

    apply_database_tenant_context(db=session, tenant=_tenant())

    session.execute.assert_not_called()


def test_blank_tenant_context_is_rejected_before_database_access() -> None:
    session = _session_for_dialect("postgresql")

    with pytest.raises(ValueError, match="tenant_id must be non-empty"):
        apply_database_tenant_context(db=session, tenant=_tenant("   "))

    session.execute.assert_not_called()
