from fastapi import FastAPI
import pytest

from kj_atlas_api.tenant_context import SingleTenantContextResolver
from kj_atlas_api.trusted_saas_runtime import (
    TrustedSaasRuntimeAdapters,
    initialize_trusted_saas_runtime,
    install_trusted_saas_runtime,
    release_trusted_saas_runtime,
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
        )
        is False
    )
    assert app.state.saas_identity_context_resolver is None
    assert isinstance(app.state.tenant_context_resolver, SingleTenantContextResolver)
    assert app.state.active_tenant_session_persister is None

    release_trusted_saas_runtime(app)


def test_complete_bundle_is_applied_atomically() -> None:
    app = FastAPI()
    adapters = _bundle()
    install_trusted_saas_runtime(app, adapters)

    assert (
        initialize_trusted_saas_runtime(
            app,
            runtime_profile="saas-multitenant",
        )
        is True
    )
    assert app.state.saas_identity_context_resolver is adapters.identity_context_resolver
    assert app.state.tenant_context_resolver is adapters.tenant_context_resolver
    assert app.state.active_tenant_session_persister is adapters.active_tenant_session_persister

    with pytest.raises(RuntimeError, match="before startup"):
        install_trusted_saas_runtime(app, adapters)
    release_trusted_saas_runtime(app)


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
        )

    assert not getattr(app.state, "_kj_atlas_runtime_started", False)
    assert not hasattr(app.state, "saas_identity_context_resolver")


def test_saas_profile_rejects_missing_trusted_bundle() -> None:
    app = FastAPI()

    with pytest.raises(RuntimeError, match="required by the runtime profile"):
        initialize_trusted_saas_runtime(
            app,
            runtime_profile="saas-multitenant",
        )

    assert not getattr(app.state, "_kj_atlas_runtime_started", False)


def test_unknown_profile_fails_before_adapter_activation() -> None:
    app = FastAPI()
    install_trusted_saas_runtime(app, _bundle())

    with pytest.raises(RuntimeError, match="runtime profile is invalid"):
        initialize_trusted_saas_runtime(app, runtime_profile="unknown")

    assert not getattr(app.state, "_kj_atlas_runtime_started", False)
    assert not hasattr(app.state, "saas_identity_context_resolver")


def test_corrupt_pre_start_state_fails_closed() -> None:
    app = FastAPI()
    app.state.trusted_saas_runtime_adapters = object()

    with pytest.raises(RuntimeError, match="bundle is invalid"):
        initialize_trusted_saas_runtime(
            app,
            runtime_profile="saas-multitenant",
        )
    assert not getattr(app.state, "_kj_atlas_runtime_started", False)
