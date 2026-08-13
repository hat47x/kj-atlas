import asyncio

from fastapi import FastAPI
import pytest

import kj_atlas_api.main as main_module
from kj_atlas_api.access_control import (
    ExternalPolicyAccessControlAdapter,
    ExternalPolicyAdapterConfig,
    NoopAccessControlAdapter,
)
from kj_atlas_api.document_access_resource import (
    ServerOwnedDocumentResourceResolver,
    SingleTenantHeaderResourceResolver,
    UnavailableDocumentPolicyBindingResolver,
)
from kj_atlas_api.document_policy_binding import (
    ExternalDocumentPolicyBindingConfig,
    ExternalHttpDocumentPolicyBindingResolver,
)
from kj_atlas_api.tenant_capability import (
    ExternalHttpTenantCapabilityResolver,
    ExternalTenantCapabilityConfig,
    UnavailableTenantCapabilityResolver,
)
from kj_atlas_api.tenant_context import SingleTenantContextResolver
from kj_atlas_api.trusted_saas_runtime import (
    TrustedSaasRuntimeAdapters,
    TrustedSaasRuntimeComponents,
    TrustedSaasRuntimePolicy,
    initialize_trusted_saas_runtime,
    install_trusted_saas_runtime,
    release_trusted_saas_runtime,
    validate_trusted_saas_runtime_preflight,
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

    def clear(self, **_: object) -> None:
        return None


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


def _runtime_components(**overrides: object) -> TrustedSaasRuntimeComponents:
    values: dict[str, object] = {
        "access_control_adapter": ExternalPolicyAccessControlAdapter(
            config=ExternalPolicyAdapterConfig(endpoint="https://pdp.invalid/authorize")
        ),
        "tenant_capability_resolver": ExternalHttpTenantCapabilityResolver(
            config=ExternalTenantCapabilityConfig(endpoint="https://capability.invalid/resolve")
        ),
        "document_policy_binding_resolver": ExternalHttpDocumentPolicyBindingResolver(
            config=ExternalDocumentPolicyBindingConfig(endpoint="https://binding.invalid/resolve")
        ),
    }
    values.update(overrides)
    return TrustedSaasRuntimeComponents(**values)  # type: ignore[arg-type]


def _configure_main_saas_policy(
    monkeypatch: pytest.MonkeyPatch,
    *,
    database_url: str,
) -> None:
    monkeypatch.setattr(main_module.settings, "runtime_profile", "saas-multitenant")
    monkeypatch.setattr(main_module.settings, "database_url", database_url)
    monkeypatch.setattr(main_module.settings, "allow_jit_provisioning", False)
    monkeypatch.setattr(main_module.settings, "access_control_adapter", "external_http")
    monkeypatch.setattr(main_module.settings, "access_control_fail_safe_mode", "deny")
    monkeypatch.setattr(
        main_module.settings,
        "access_control_external_http_endpoint",
        "https://pdp.invalid/authorize",
    )
    monkeypatch.setattr(
        main_module.settings,
        "document_policy_binding_resolver",
        "external_http",
    )
    monkeypatch.setattr(
        main_module.settings,
        "document_policy_binding_http_endpoint",
        "https://binding.invalid/resolve",
    )
    monkeypatch.setattr(main_module.settings, "tenant_capability_resolver", "external_http")
    monkeypatch.setattr(
        main_module.settings,
        "tenant_capability_http_endpoint",
        "https://capability.invalid/resolve",
    )


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
            runtime_components=_runtime_components(),
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
            runtime_components=_runtime_components(),
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
        runtime_components=_runtime_components(),
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
        runtime_components=_runtime_components(),
    )
    release_trusted_saas_runtime(app)

    with pytest.raises(RuntimeError, match="single-tenant profile"):
        initialize_trusted_saas_runtime(
            app,
            runtime_profile="enterprise-production",
            runtime_policy=_runtime_policy(),
            runtime_components=_runtime_components(),
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
            runtime_components=_runtime_components(),
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
            runtime_components=_runtime_components(),
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
            runtime_components=_runtime_components(),
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
            runtime_components=_runtime_components(),
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
            runtime_components=_runtime_components(),
        )

    assert not getattr(app.state, "_kj_atlas_runtime_started", False)
    assert not hasattr(app.state, "saas_identity_context_resolver")


def test_saas_profile_rejects_unvalidated_runtime_policy_object() -> None:
    with pytest.raises(RuntimeError, match="runtime policy is invalid"):
        validate_trusted_saas_runtime_policy(
            runtime_profile="saas-multitenant",
            runtime_policy=object(),  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    ("override", "expected_requirement"),
    [
        (
            {"access_control_adapter": NoopAccessControlAdapter()},
            "external access-control component",
        ),
        (
            {"tenant_capability_resolver": UnavailableTenantCapabilityResolver()},
            "external tenant capability component",
        ),
        (
            {"document_policy_binding_resolver": UnavailableDocumentPolicyBindingResolver()},
            "external document binding component",
        ),
    ],
)
def test_saas_preflight_rejects_mismatched_runtime_components(
    override: dict[str, object],
    expected_requirement: str,
) -> None:
    app = FastAPI()
    install_trusted_saas_runtime(app, _bundle())

    with pytest.raises(RuntimeError, match=expected_requirement):
        validate_trusted_saas_runtime_preflight(
            app,
            runtime_profile="saas-multitenant",
            runtime_policy=_runtime_policy(),
            runtime_components=_runtime_components(**override),
        )

    assert not getattr(app.state, "_kj_atlas_runtime_started", False)
    assert not hasattr(app.state, "saas_identity_context_resolver")


def test_saas_preflight_rejects_unvalidated_runtime_components_object() -> None:
    app = FastAPI()
    install_trusted_saas_runtime(app, _bundle())

    with pytest.raises(RuntimeError, match="runtime components are invalid"):
        validate_trusted_saas_runtime_preflight(
            app,
            runtime_profile="saas-multitenant",
            runtime_policy=_runtime_policy(),
            runtime_components=object(),  # type: ignore[arg-type]
        )


def test_preflight_does_not_activate_validated_saas_adapters() -> None:
    app = FastAPI()
    install_trusted_saas_runtime(app, _bundle())

    validate_trusted_saas_runtime_preflight(
        app,
        runtime_profile="saas-multitenant",
        runtime_policy=_runtime_policy(),
        runtime_components=_runtime_components(),
    )

    assert not getattr(app.state, "_kj_atlas_runtime_started", False)
    assert not hasattr(app.state, "saas_identity_context_resolver")


def test_lifespan_rejects_unsafe_saas_policy_before_database_initialization(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    init_db_called = False

    def record_init_db() -> None:
        nonlocal init_db_called
        init_db_called = True

    monkeypatch.setattr(main_module, "_assert_linear_migration_history", lambda: None)
    monkeypatch.setattr(main_module, "init_db", record_init_db)
    _configure_main_saas_policy(monkeypatch, database_url="sqlite:///unsafe.db")

    async def start_lifespan() -> None:
        async with main_module.lifespan(FastAPI()):
            raise AssertionError("unsafe SaaS lifespan must not start")

    with pytest.raises(RuntimeError, match="PostgreSQL tenant DB guard"):
        asyncio.run(start_lifespan())

    assert init_db_called is False


def test_lifespan_rejects_missing_saas_bundle_before_database_initialization(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    init_db_called = False

    def record_init_db() -> None:
        nonlocal init_db_called
        init_db_called = True

    monkeypatch.setattr(main_module, "_assert_linear_migration_history", lambda: None)
    monkeypatch.setattr(main_module, "init_db", record_init_db)
    _configure_main_saas_policy(
        monkeypatch,
        database_url="postgresql+psycopg://db.invalid/kj_atlas",
    )

    async def start_lifespan() -> None:
        async with main_module.lifespan(FastAPI()):
            raise AssertionError("SaaS lifespan without trusted adapters must not start")

    with pytest.raises(RuntimeError, match="required by the runtime profile"):
        asyncio.run(start_lifespan())

    assert init_db_called is False


def test_lifespan_rejects_mismatched_component_before_database_initialization(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = FastAPI()
    install_trusted_saas_runtime(app, _bundle())
    init_db_called = False

    def record_init_db() -> None:
        nonlocal init_db_called
        init_db_called = True

    monkeypatch.setattr(main_module, "_assert_linear_migration_history", lambda: None)
    monkeypatch.setattr(main_module, "init_db", record_init_db)
    monkeypatch.setattr(
        main_module,
        "build_access_control_adapter",
        lambda **_: NoopAccessControlAdapter(),
    )
    _configure_main_saas_policy(
        monkeypatch,
        database_url="postgresql+psycopg://db.invalid/kj_atlas",
    )

    async def start_lifespan() -> None:
        async with main_module.lifespan(app):
            raise AssertionError("SaaS lifespan with mismatched components must not start")

    with pytest.raises(RuntimeError, match="external access-control component"):
        asyncio.run(start_lifespan())

    assert init_db_called is False
    assert not getattr(app.state, "_kj_atlas_runtime_started", False)


def test_docs_endpoints_disabled_on_production_profiles() -> None:
    """SEC-HEADERS-01 (option a): /docs, /redoc, /openapi.json are disabled on
    production runtime profiles and kept for dev/evaluation convenience. Uses a
    subprocess so the module-level FastAPI construction is exercised with a
    clean profile env (the in-process main is imported under the test profile)."""
    import os
    import subprocess
    import sys

    cases = [
        ("local-dev", True),
        ("evaluation", True),
        ("enterprise-production", False),
        ("saas-multitenant", False),
    ]
    for profile, expected_enabled in cases:
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from kj_atlas_api.main import app; print(app.docs_url, app.openapi_url)",
            ],
            capture_output=True,
            text=True,
            env={
                **os.environ,
                "KJ_ATLAS_RUNTIME_PROFILE": profile,
                "KJ_ATLAS_LLM_PROVIDER": "none",
                # ADR-0072 D3=A: production profiles refuse to start without an
                # authentication means. This test is about docs/openapi exposure,
                # so satisfy the requirement instead of relaxing it.
                "KJ_ATLAS_ADMIN_API_KEY": "admin-key",
                "KJ_ATLAS_API_KEY": "business-key",
            },
            timeout=30,
        )
        assert result.returncode == 0, f"{profile}: import failed: {result.stderr}"
        stdout = result.stdout.strip()
        if expected_enabled:
            assert "/docs" in stdout, f"{profile}: docs should be enabled, got {stdout!r}"
            assert "/openapi.json" in stdout, f"{profile}: openapi should be enabled, got {stdout!r}"
        else:
            assert stdout == "None None", f"{profile}: docs should be disabled, got {stdout!r}"
