from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    if new in text:
        return
    if old not in text:
        raise SystemExit(f"marker not found in {path}: {old[:120]!r}")
    path.write_text(text.replace(old, new, 1))


# Central persistence-shape governance.
shapes = ROOT / "03_Implement/backend/src/kj_atlas_api/persistence_shapes.py"
replace_once(
    shapes,
    '    "guest_principals.tenant_id": INTERNAL_ID,\n',
    '    "guest_auth_sessions.session_key_hash": _bounded(\n'
    '        256, "server-owned keyed hash of the opaque guest session cookie value"\n'
    '    ),\n'
    '    "guest_auth_sessions.tenant_id": INTERNAL_ID,\n'
    '    "guest_auth_sessions.guest_principal_id": INTERNAL_ID,\n'
    '    "guest_auth_sessions.issuer": _bounded(\n'
    '        OIDC_ISSUER_MAX_CHARS, "verified guest session issuer acceptance bound"\n'
    '    ),\n'
    '    "guest_auth_sessions.subject": EXTERNAL_ID,\n'
    '    "guest_auth_sessions.created_at": TIMESTAMP,\n'
    '    "guest_auth_sessions.last_used_at": TIMESTAMP,\n'
    '    "guest_auth_sessions.absolute_expires_at": TIMESTAMP,\n'
    '    "guest_auth_sessions.revoked_at": TIMESTAMP,\n'
    '    "guest_principals.tenant_id": INTERNAL_ID,\n',
)

# Alembic autogenerate must see the late-defined guest session table.
env = ROOT / "03_Implement/backend/alembic/env.py"
replace_once(
    env,
    "from kj_atlas_api import guest_admission_models as _guest_admission_models  # noqa: E402,F401\n",
    "from kj_atlas_api import guest_admission_models as _guest_admission_models  # noqa: E402,F401\n"
    "from kj_atlas_api import guest_auth_session_models as _guest_auth_session_models  # noqa: E402,F401\n",
)

# A guest session is trusted tenant evidence, but explicitly not membership.
tenant_context = ROOT / "03_Implement/backend/src/kj_atlas_api/tenant_context.py"
replace_once(
    tenant_context,
    '    "trusted_host_mapping",\n]\n',
    '    "trusted_host_mapping",\n    "guest_session",\n]\n',
)

# Runtime store lifecycle. Reuse the deployment's keyed-session-hash secret,
# but not the member session table/cookie/identity semantics.
main = ROOT / "03_Implement/backend/src/kj_atlas_api/main.py"
replace_once(
    main,
    "from kj_atlas_api.generation_repository import (\n",
    "from kj_atlas_api.guest_auth_state import DatabaseGuestAuthSessionStore\n"
    "from kj_atlas_api.generation_repository import (\n",
)
replace_once(
    main,
    "        _saas_auth_session_store.preflight()\n",
    "        _saas_auth_session_store.preflight()\n"
    "        _guest_auth_session_store.preflight()\n",
)
replace_once(
    main,
    "_saas_auth_session_store = DatabaseSaasAuthSessionStore(SessionLocal)\n",
    "_saas_auth_session_store = DatabaseSaasAuthSessionStore(SessionLocal)\n"
    "_guest_auth_session_store = DatabaseGuestAuthSessionStore(SessionLocal)\n",
)
replace_once(
    main,
    "    app.state.saas_auth_session_hash_key = _saas_auth_session_hash_key\n",
    "    app.state.saas_auth_session_hash_key = _saas_auth_session_hash_key\n"
    "    app.state.guest_auth_session_store = _guest_auth_session_store\n"
    "    app.state.guest_auth_session_hash_key = _saas_auth_session_hash_key\n",
)

# Exact-grant guest branch runs before member tenant/session resolution. A
# presented guest cookie is authoritative: invalid guest state never falls
# through into the member resolver.
docs = ROOT / "03_Implement/backend/src/kj_atlas_api/routes/docs.py"
replace_once(
    docs,
    "from kj_atlas_api.generation_repository import RevisionHeadConflict\n",
    "from kj_atlas_api.generation_repository import RevisionHeadConflict\n"
    "from kj_atlas_api.guest_admission_repository import GuestAdmissionRepository\n"
    "from kj_atlas_api.guest_request_auth import resolve_guest_request_session\n",
)
needle = '''    tenant_scoped_session_required = tenant_session_precondition_required(request)\n'''
guest_branch = '''    guest_session = resolve_guest_request_session(request=request)\n    if guest_session is not None:\n        # ADR-0080 D3: the guest principal itself conveys zero document\n        # visibility. R2a intentionally supports read only; broader guest\n        # actions remain closed until separately designed and tested.\n        if action != "read":\n            raise HTTPException(\n                status_code=403,\n                detail={\n                    "code": "guest_write_not_enabled",\n                    "message": "Guest write access is not enabled.",\n                },\n            )\n        guest_repo = GuestAdmissionRepository(db, tenant_id=guest_session.tenant_id)\n        if not guest_repo.can_read_document(\n            guest_principal_id=guest_session.guest_principal_id,\n            doc_id=doc_id,\n        ):\n            # Preserve resource anti-enumeration: an ungranted existing doc is\n            # indistinguishable from a non-existent/cross-tenant doc.\n            raise HTTPException(\n                status_code=404,\n                detail={\n                    "code": "guest_document_not_granted",\n                    "message": "Document is not available.",\n                },\n            )\n        tenant = TenantContext(\n            tenant_id=guest_session.tenant_id,\n            membership_id=None,\n            resolved_by="guest_session",\n        )\n        resource_resolver: DocumentAccessResourceResolver = getattr(\n            request.app.state,\n            "document_access_resource_resolver",\n            SingleTenantHeaderResourceResolver(),\n        )\n        resource = resource_resolver.resolve(\n            db=db,\n            request=request,\n            tenant=tenant,\n            action=action,\n            doc_id=doc_id,\n        )\n        access_request = AccessRequest(\n            action=action,\n            safe_mode=safe_mode,\n            read_only=True,\n            auth=AuthContext(\n                actor_ref=guest_session.guest_principal_id,\n                user_id=None,\n                provider="guest_session",\n                external_uid=guest_session.guest_principal_id,\n                trace_id=request.headers.get("x-trace-id"),\n            ),\n            tenant=tenant,\n            resource=resource,\n        )\n        tenant_boundary = apply_tenant_boundary_guard(access_request, required=True)\n        if tenant_boundary is not None:\n            enforce_access(tenant_boundary, action=action)\n        return (\n            access_request,\n            AccessDecision(allow=True, read_only=True, reason="guest_document_grant"),\n            tenant,\n        )\n\n    tenant_scoped_session_required = tenant_session_precondition_required(request)\n'''
replace_once(docs, needle, guest_branch)

# Persistence coverage imports the late-defined table and pins its bounded
# shapes, preventing future metadata/autogenerate drift.
persistence_test = ROOT / "03_Implement/backend/tests/test_persistence_shapes.py"
replace_once(
    persistence_test,
    "from kj_atlas_api.guest_admission_models import GuestDocumentGrantRow, GuestPrincipalRow\n",
    "from kj_atlas_api.guest_admission_models import GuestDocumentGrantRow, GuestPrincipalRow\n"
    "from kj_atlas_api.guest_auth_session_models import GuestAuthSessionRow\n",
)
text = persistence_test.read_text()
if "def test_guest_auth_session_shapes_are_centrally_governed()" not in text:
    text = text.rstrip() + '''\n\n\ndef test_guest_auth_session_shapes_are_centrally_governed() -> None:\n    assert GuestAuthSessionRow.__table__.metadata is Base.metadata\n    expected = {\n        "guest_auth_sessions.session_key_hash": 256,\n        "guest_auth_sessions.tenant_id": 128,\n        "guest_auth_sessions.guest_principal_id": 128,\n        "guest_auth_sessions.issuer": 512,\n        "guest_auth_sessions.subject": 512,\n    }\n    for qualified_name, max_chars in expected.items():\n        assert PERSISTENT_TEXT_SPECS[qualified_name].proposed_max_chars == max_chars\n        table_name, column_name = qualified_name.split(".", 1)\n        assert Base.metadata.tables[table_name].columns[column_name].type.length == max_chars'''
    persistence_test.write_text(text.rstrip() + "\n")

# The repository pins a single Alembic head to catch stream merge conflicts.
lineage = ROOT / "03_Implement/backend/tests/test_alembic_lineage.py"
replace_once(
    lineage,
    '    assert heads == ["20260906_0033"], (\n',
    '    assert heads == ["20260906_0034"], (\n',
)
replace_once(
    lineage,
    '    assert "20260906_0033" in history_ids\n    assert (\n        history_ids.index("20260906_0033")\n',
    '    assert "20260906_0033" in history_ids\n    assert "20260906_0034" in history_ids\n    assert (\n        history_ids.index("20260906_0034")\n        < history_ids.index("20260906_0033")\n',
)
