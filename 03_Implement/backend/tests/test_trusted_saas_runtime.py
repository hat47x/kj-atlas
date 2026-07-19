import asyncio

from fastapi import FastAPI
import pytest

import kj_atlas_api.main as main_module
from kj_atlas_api.document_access_resource import (
    ServerOwnedDocumentResourceResolver,
    SingleTenantHeaderResourceResolver,
)
from kj_atlas_api.tenant_context import SingleTenantContextResolver
from kj_atlas_api.trusted_saas_runtime import (
    TrustedSaasRuntimeAdapters,
    TrustedSaasRuntimePolicy,
    initialize_trusted_saas_runtime,
    install_trusted_saas_runtime,
    release_trusted_saas_runtime,
    validate_trusted_saas_runtime_policy,
)


class IdentityResolver:
    def resolve(self, **_: object) -> object:
        return object()


class TenantResolver:
    def resolve(self, **_: object) -> object:
        return object()


class SessionPersister:
    def current_version(self, **_: object) -> str:
        return "session-v1"

    def persist(self, **_: object) -> str:
        return "session-v2"


def _bundle() -> TrustedSaasRuntimeAdapters:
    return TrustedSaasRuntimeAdapters(
        identity_context_resolver=IdentityResolver(),
        tenant_context_resolver=TenantResolver(),
        active_tenant_session_persister=SessionPersister(),
    )


def _runtime_policy(**overrides: object) -> TrustedSaasRuntimePolicy:
    values: dict[str, object] = {
        "database_backend": "postgresql",
        "allow_jit_provisioning": False,
        "access_control_adapter": "external_http",
        "access_control_fail_safe_mode": "deny",
        "document_policy_binding_resolver": "external_http",
        "tenant_capability_resolver": "external_http",
    }
    values.update(overrides)
    return TrustedSaasRuntimePolicy(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "runtime_profile",
    ["local-dev", "evaluation", "enterprise-production"],
)
def test_single_tenant_runtime_keeps_session_routes_closed(
    runtime_profile: str,
) -> None:
    app = FastAPI()

    assert (
        initialize_trusted_saas_runtime(
            app,
            runtime_profile=runtime_profile,
            runtime_policy=_runtime_policy(),
        )
        is False
    )
    assert app.state.saas_identity_context_resolver is None
    assert isinstance(app.state.tenant_context_resolver, SingleTenantContextResolver)
    assert app.state.active_tenant_session_persister is None
    assert isinstance(
        app.state.document_access_resource_resolver,
        SingleTenantHeaderResourceResolver,
    )

    release_trusted_saas_runtime(app)


def test_complete_bundle_is_applied_atomically() -> None:
    app = FastAPI()
    adapters = _bundle()
    install_trusted_saas_runtime(app, adapters)

    assert (
        initialize_trusted_saas_runtime(
            app,
            runtime_profile="saas-multitenant",
            runtime_policy=_runtime_policy(),
        )
        is True
    )
    assert app.state.saas_identity_context_resolver is adapters.identity_context_resolver
    assert app.state.tenant_context_resolver is adapters.tenant_context_resolver
    assert app.state.active_tenant_session_persister is adapters.active_tenant_session_persister
    assert isinstance(
        app.state.document_access_resource_resolver,
        ServerOwnedDocumentResourceResolver,
    )

    with pytest.raises(RuntimeError, match="before startup"):
        install_trusted_saas_runtime(app, adapters)
    release_trusted_saas_runtime(app)

    assert app.state.saas_identity_context_resolver is None
    assert isinstance(app.state.tenant_context_resolver, SingleTenantContextResolver)
    assert app.state.active_tenant_session_persister is None
    assert isinstance(
        app.state.document_access_resource_resolver,
        SingleTenantHeaderResourceResolver,
    )
    assert not app.state._kj_atlas_runtime_started

    assert initialize_trusted_saas_runtime(
        app,
        runtime_profile="saas-multitenant",
        runtime_policy=_runtime_policy(),
    )
    assert app.state.saas_identity_context_resolver is adapters.identity_context_resolver
    assert app.state.tenant_context_resolver is adapters.tenant_context_resolver
    assert app.state.active_tenant_session_persister is adapters.active_tenant_session_persister
    assert isinstance(
        app.state.document_access_resource_resolver,
        ServerOwnedDocumentResourceResolver,
    )


def test_released_bundle_can_only_be_reactivated_by_a_matching_profile() -> None:
    app = FastAPI()
    adapters = _bundle()
    install_trusted_saas_runtime(app, adapters)
    initialize_trusted_saas_runtime(
        app,
        runtime_profile="saas-multitenant",
        runtime_policy=_runtime_policy(),
    )
    release_trusted_saas_runtime(app)

    with pytest.raises(RuntimeError, match="single-tenant profile"):
        initialize_trusted_saas_runtime(
            app,
            runtime_profile="enterprise-production",
            runtime_policy=_runtime_policy(),
        )

    assert app.state.saas_identity_context_resolver is None
    assert isinstance(app.state.tenant_context_resolver, SingleTenantContextResolver)
    assert app.state.active_tenant_session_persister is None
    assert isinstance(
        app.state.document_access_resource_resolver,
        SingleTenantHeaderResourceResolver,
    )
    assert not app.state._kj_atlas_runtime_started


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("identity_context_resolver", object()),
        ("tenant_context_resolver", object()),
        ("active_tenant_session_persister", object()),
    ],
)
def test_incomplete_bundle_is_rejected(field: str, value: object) -> None:
    values = {
        "identity_context_resolver": IdentityResolver(),
        "tenant_context_resolver": TenantResolver(),
        "active_tenant_session_persister": SessionPersister(),
    }
    values[field] = value

    with pytest.raises(ValueError, match="bundle is incomplete"):
        TrustedSaasRuntimeAdapters(**values)  # type: ignore[arg-type]


class PersistOnlySessionAdapter:
    def persist(self, **_: object) -> str:
        return "session-v2"


def test_bundle_rejects_session_adapter_without_version_resolution() -> None:
    with pytest.raises(ValueError, match="bundle is incomplete"):
        TrustedSaasRuntimeAdapters(
            identity_context_resolver=IdentityResolver(),
            tenant_context_resolver=TenantResolver(),
            active_tenant_session_persister=PersistOnlySessionAdapter(),  # type: ignore[arg-type]
        )


def test_bundle_cannot_be_replaced_on_the_same_app() -> None:
    app = FastAPI()
    adapters = _bundle()
    install_trusted_saas_runtime(app, adapters)
    install_trusted_saas_runtime(app, adapters)

    with pytest.raises(RuntimeError, match="cannot be replaced"):
        install_trusted_saas_runtime(app, _bundle())


def test_single_tenant_profile_rejects_trusted_saas_bundle() -> None:
    app = FastAPI()
    install_trusted_saas_runtime(app, _bundle())

    with pytest.raises(RuntimeError, match="single-tenant profile"):
        initialize_trusted_saas_runtime(
            app,
            runtime_profile="enterprise-production",
            runtime_policy=_runtime_policy(),
        )

    assert not getattr(app.state, "_kj_atlas_runtime_started", False)
    assert not hasattr(app.state, "saas_identity_context_resolver")


def test_saas_profile_rejects_missing_trusted_bundle() -> None:
    app = FastAPI()

    with pytest.raises(RuntimeError, match="required by the runtime profile"):
        initialize_trusted_saas_runtime(
            app,
            runtime_profile="saas-multitenant",
            runtime_policy=_runtime_policy(),
        )

    assert not getattr(app.state, "_kj_atlas_runtime_started", False)


def test_unknown_profile_fails_before_adapter_activation() -> None:
    app = FastAPI()
    install_trusted_saas_runtime(app, _bundle())

    with pytest.raises(RuntimeError, match="runtime profile is invalid"):
        initialize_trusted_saas_runtime(
            app,
            runtime_profile="unknown",
            runtime_policy=_runtime_policy(),
        )

    assert not getattr(app.state, "_kj_atlas_runtime_started", False)
    assert not hasattr(app.state, "saas_identity_context_resolver")


def test_corrupt_pre_start_state_fails_closed() -> None:
    app = FastAPI()
    app.state.trusted_saas_runtime_adapters = object()

    with pytest.raises(RuntimeError, match="bundle is invalid"):
        initialize_trusted_saas_runtime(
            app,
            runtime_profile="saas-multitenant",
            runtime_policy=_runtime_policy(),
        )
    assert not getattr(app.state, "_kj_atlas_runtime_started", False)


@pytest.mark.parametrize(
    ("override", "expected_requirement"),
    [
        ({"database_backend": "sqlite"}, "PostgreSQL tenant DB guard"),
        ({"allow_jit_provisioning": True}, "disabled JIT provisioning"),
        ({"access_control_adapter": "noop"}, "external access control"),
        ({"access_control_fail_safe_mode": "read_only"}, "deny fail-safe mode"),
        (
            {"document_policy_binding_resolver": "none"},
            "external document policy binding",
        ),
        ({"tenant_capability_resolver": "none"}, "external tenant capability"),
    ],
)
def test_saas_policy_rejects_each_unsafe_runtime_dependency(
    override: dict[str, object],
    expected_requirement: str,
) -> None:
    with pytest.raises(RuntimeError, match=expected_requirement):
        validate_trusted_saas_runtime_policy(
            runtime_profile="saas-multitenant",
            runtime_policy=_runtime_policy(**override),
        )


def test_initialize_rechecks_saas_policy_before_adapter_activation() -> None:
    app = FastAPI()
    install_trusted_saas_runtime(app, _bundle())

    with pytest.raises(RuntimeError, match="external access control"):
        initialize_trusted_saas_runtime(
            app,
            runtime_profile="saas-multitenant",
            runtime_policy=_runtime_policy(access_control_adapter="mock"),
        )

    assert not getattr(app.state, "_kj_atlas_runtime_started", False)
    assert not hasattr(app.state, "saas_identity_context_resolver")


def test_saas_profile_rejects_unvalidated_runtime_policy_object() -> None:
    with pytest.raises(RuntimeError, match="runtime policy is invalid"):
        validate_trusted_saas_runtime_policy(
            runtime_profile="saas-multitenant",
            runtime_policy=object(),  # type: ignore[arg-type]
        )


def test_lifespan_rejects_unsafe_saas_policy_before_database_initialization(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    init_db_called = False

    def record_init_db() -> None:
        nonlocal init_db_called
        init_db_called = True

    monkeypatch.setattr(main_module, "_assert_linear_migration_history", lambda: None)
    monkeypatch.setattr(main_module, "init_db", record_init_db)
    monkeypatch.setattr(main_module.settings, "runtime_profile", "saas-multitenant")
    monkeypatch.setattr(main_module.settings, "database_url", "sqlite:///unsafe.db")
    monkeypatch.setattr(main_module.settings, "allow_jit_provisioning", False)
    monkeypatch.setattr(main_module.settings, "access_control_adapter", "external_http")
    monkeypatch.setattr(main_module.settings, "access_control_fail_safe_mode", "deny")
    monkeypatch.setattr(
        main_module.settings,
        "document_policy_binding_resolver",
        "external_http",
    )
    monkeypatch.setattr(main_module.settings, "tenant_capability_resolver", "external_http")

    async def start_lifespan() -> None:
        async with main_module.lifespan(FastAPI()):
            raise AssertionError("unsafe SaaS lifespan must not start")

    with pytest.raises(RuntimeError, match="PostgreSQL tenant DB guard"):
        asyncio.run(start_lifespan())

    assert init_db_called is False
