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
    def persist(self, **_: object) -> None:
        return


def _bundle() -> TrustedSaasRuntimeAdapters:
    return TrustedSaasRuntimeAdapters(
        identity_context_resolver=IdentityResolver(),
        tenant_context_resolver=TenantResolver(),
        active_tenant_session_persister=SessionPersister(),
    )


def test_default_runtime_keeps_session_routes_closed() -> None:
    app = FastAPI()

    assert initialize_trusted_saas_runtime(app) is False
    assert app.state.saas_identity_context_resolver is None
    assert isinstance(app.state.tenant_context_resolver, SingleTenantContextResolver)
    assert app.state.active_tenant_session_persister is None

    release_trusted_saas_runtime(app)


def test_complete_bundle_is_applied_atomically() -> None:
    app = FastAPI()
    adapters = _bundle()
    install_trusted_saas_runtime(app, adapters)

    assert initialize_trusted_saas_runtime(app) is True
    assert app.state.saas_identity_context_resolver is adapters.identity_context_resolver
    assert app.state.tenant_context_resolver is adapters.tenant_context_resolver
    assert (
        app.state.active_tenant_session_persister
        is adapters.active_tenant_session_persister
    )

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


def test_bundle_cannot_be_replaced_on_the_same_app() -> None:
    app = FastAPI()
    adapters = _bundle()
    install_trusted_saas_runtime(app, adapters)
    install_trusted_saas_runtime(app, adapters)

    with pytest.raises(RuntimeError, match="cannot be replaced"):
        install_trusted_saas_runtime(app, _bundle())


def test_corrupt_pre_start_state_fails_closed() -> None:
    app = FastAPI()
    app.state.trusted_saas_runtime_adapters = object()

    with pytest.raises(RuntimeError, match="bundle is invalid"):
        initialize_trusted_saas_runtime(app)
    assert not getattr(app.state, "_kj_atlas_runtime_started", False)
