from __future__ import annotations

import pytest

from sui_sensemaking_api.settings import Settings


@pytest.mark.parametrize(
    ("settings_overrides", "expected_endpoint"),
    [
        (
            {
                "SUI_ACCESS_CONTROL_ADAPTER": "external_http",
                "SUI_ACCESS_CONTROL_EXTERNAL_HTTP_ENDPOINT": (
                    "https://pdp.example.invalid/v1/decide"
                ),
            },
            "https://pdp.example.invalid/v1/decide",
        ),
        (
            {
                "SUI_AUDIT_TRANSPORT": "http",
                "SUI_AUDIT_HTTP_ENDPOINT": "http://127.0.0.1:9000/audit",
            },
            "http://127.0.0.1:9000/audit",
        ),
    ],
)
def test_optional_http_integrations_accept_https_or_loopback_http(
    settings_overrides: dict[str, object],
    expected_endpoint: str,
) -> None:
    configured = Settings(**settings_overrides)

    assert expected_endpoint in {
        configured.access_control_external_http_endpoint,
        configured.audit_http_endpoint,
    }


@pytest.mark.parametrize(
    "endpoint",
    [
        "http://pdp.example.invalid/decide",
        "https://user:password@pdp.example.invalid/decide",
        "https://pdp.example.invalid/decide?token=secret",
        "https://pdp.example.invalid/decide?",
        "https://pdp.example.invalid/decide#fragment",
        "https://pdp.example.invalid/decide#",
        "https://pdp.example.invalid:invalid/decide",
        " https://pdp.example.invalid/decide",
        "https://pdp.example.invalid\\@other.invalid/decide",
    ],
)
def test_external_pdp_rejects_untrusted_endpoint_shapes(endpoint: str) -> None:
    with pytest.raises(ValueError) as exc_info:
        Settings(
            SUI_ACCESS_CONTROL_ADAPTER="external_http",
            SUI_ACCESS_CONTROL_EXTERNAL_HTTP_ENDPOINT=endpoint,
        )

    assert "secret" not in str(exc_info.value)
    assert "password" not in str(exc_info.value)


def test_http_integration_rejects_orphaned_endpoint_and_bearer() -> None:
    with pytest.raises(ValueError):
        Settings(
            SUI_ACCESS_CONTROL_ADAPTER="noop",
            SUI_ACCESS_CONTROL_EXTERNAL_HTTP_ENDPOINT=(
                "https://pdp.example.invalid/decide"
            ),
        )
    with pytest.raises(ValueError) as exc_info:
        Settings(
            SUI_AUDIT_TRANSPORT="http",
            SUI_AUDIT_HTTP_API_KEY="orphan-secret",
        )
    assert "orphan-secret" not in str(exc_info.value)
    with pytest.raises(ValueError):
        Settings(
            SUI_ACCESS_CONTROL_ADAPTER="external_http",
            SUI_ACCESS_CONTROL_EXTERNAL_HTTP_IDP_ISSUER="issuer-without-endpoint",
        )


@pytest.mark.parametrize(
    ("settings_overrides", "required_key"),
    [
        (
            {"SUI_ACCESS_CONTROL_ADAPTER": "external_http"},
            "SUI_ACCESS_CONTROL_EXTERNAL_HTTP_ENDPOINT",
        ),
        (
            {"SUI_AUDIT_TRANSPORT": "http"},
            "SUI_AUDIT_HTTP_ENDPOINT",
        ),
    ],
)
def test_enabled_http_integration_requires_endpoint(
    settings_overrides: dict[str, object],
    required_key: str,
) -> None:
    with pytest.raises(ValueError) as exc_info:
        Settings(**settings_overrides)

    assert required_key in str(exc_info.value)


@pytest.mark.parametrize("secret", ["", "has whitespace", "control\nvalue", "bidi\u202evalue"])
def test_http_integration_rejects_noncanonical_bearer_without_reflection(
    secret: str,
) -> None:
    with pytest.raises(ValueError) as exc_info:
        Settings(
            SUI_ACCESS_CONTROL_ADAPTER="external_http",
            SUI_ACCESS_CONTROL_EXTERNAL_HTTP_ENDPOINT=(
                "https://pdp.example.invalid/decide"
            ),
            SUI_ACCESS_CONTROL_EXTERNAL_HTTP_STATIC_BEARER_TOKEN=secret,
        )

    if secret:
        assert secret not in str(exc_info.value)


@pytest.mark.parametrize(
    "issuer",
    [" issuer", "issuer with space", "control\nissuer", "bidi\u202eissuer"],
)
def test_external_pdp_rejects_noncanonical_issuer_without_reflection(
    issuer: str,
) -> None:
    with pytest.raises(ValueError) as exc_info:
        Settings(
            SUI_ACCESS_CONTROL_ADAPTER="external_http",
            SUI_ACCESS_CONTROL_EXTERNAL_HTTP_ENDPOINT=(
                "https://pdp.example.invalid/decide"
            ),
            SUI_ACCESS_CONTROL_EXTERNAL_HTTP_IDP_ISSUER=issuer,
        )

    assert issuer not in str(exc_info.value)


@pytest.mark.parametrize(
    "settings_overrides",
    [
        {"SUI_ACCESS_CONTROL_EXTERNAL_HTTP_TIMEOUT_SECONDS": 0},
        {"SUI_ACCESS_CONTROL_EXTERNAL_HTTP_TIMEOUT_SECONDS": 30.1},
        {"SUI_AUDIT_HTTP_TIMEOUT_SECONDS": 0},
        {"SUI_AUDIT_HTTP_TIMEOUT_SECONDS": 30.1},
        {"SUI_AUDIT_QUEUE_SIZE": 0},
    ],
)
def test_http_integration_rejects_unsafe_bounds(
    settings_overrides: dict[str, object],
) -> None:
    with pytest.raises(ValueError):
        Settings(**settings_overrides)


def test_http_integration_normalizes_transport_and_rejects_unknown_value() -> None:
    configured = Settings(
        SUI_AUDIT_TRANSPORT="  HTTP ",
        SUI_AUDIT_HTTP_ENDPOINT="http://127.0.0.1:9000/audit",
    )

    assert configured.audit_transport == "http"

    with pytest.raises(ValueError):
        Settings(SUI_AUDIT_TRANSPORT="syslog")
