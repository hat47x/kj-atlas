"""SAAS-TENANT-SESSION-BINDING-01 AC-1 (ADR-0074 decision 1): confidential-
client OAuth 2.0 authorization-code+PKCE token exchange against the Broker.

Mirrors document_policy_binding.py's shape and rigor bar exactly: bounded
request/response, open_trusted_http() (no redirects), closed-world response
validation before any field is trusted, and HTTP errors bucketed into
"rejected" (broker said no) vs "unavailable" (broker unreachable) so a caller
never has to inspect an upstream status code directly.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from urllib import error as urllib_error
from urllib import request as urllib_request
from urllib.parse import urlencode

from kj_atlas_api.trusted_http import open_trusted_http

MAX_TOKEN_RESPONSE_BYTES = 64 * 1024
_ALLOWED_TOKEN_RESPONSE_KEYS = frozenset(
    {"access_token", "token_type", "expires_in", "refresh_token", "id_token", "scope"}
)
# Mirrors document_policy_binding.py's rejected/unavailable split, extended
# with 404 (the broker convention document_policy_binding.py already treats
# as "rejected", not "unavailable" -- an unknown token endpoint path is a
# broker-side rejection of this specific request, not a reachability issue).
_REJECTED_HTTP_STATUS_CODES = frozenset({400, 401, 403, 404, 409, 422})


class OauthBrokerUnavailableError(RuntimeError):
    """The Broker's token endpoint could not be reached."""


class OauthBrokerInvalidResponseError(ValueError):
    """The Broker rejected the code exchange or returned an unusable response."""


@dataclass(frozen=True, slots=True)
class ExternalOauthBrokerConfig:
    token_endpoint: str
    client_id: str
    client_secret: str
    redirect_uri: str
    timeout_seconds: float = 5.0


@dataclass(frozen=True, slots=True)
class BrokerTokenResponse:
    access_token: str
    token_type: str
    expires_in: int
    id_token: str | None


def exchange_code_for_tokens(
    *,
    config: ExternalOauthBrokerConfig,
    code: str,
    code_verifier: str,
) -> BrokerTokenResponse:
    """Exchange an authorization code (+ PKCE verifier) for tokens.

    redirect_uri is sent explicitly (RFC 6749 SS4.1.3) as a defense against
    code injection -- PKCE covers most of this, but the client must still
    assert the redirect_uri it used when the code was issued.
    """
    body = urlencode(
        {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": config.redirect_uri,
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "code_verifier": code_verifier,
        }
    ).encode("utf-8")
    outbound = urllib_request.Request(
        config.token_endpoint,
        data=body,
        headers={
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )

    try:
        with open_trusted_http(outbound, timeout_seconds=config.timeout_seconds) as response:
            response_body = response.read(MAX_TOKEN_RESPONSE_BYTES + 1)
    except urllib_error.HTTPError as exc:
        if exc.code in _REJECTED_HTTP_STATUS_CODES:
            raise OauthBrokerInvalidResponseError("broker rejected the code exchange") from None
        raise OauthBrokerUnavailableError("broker token endpoint is unavailable") from None
    except (urllib_error.URLError, TimeoutError, OSError):
        raise OauthBrokerUnavailableError("broker token endpoint is unavailable") from None

    if len(response_body) > MAX_TOKEN_RESPONSE_BYTES:
        raise OauthBrokerInvalidResponseError("broker response exceeds the size limit")
    try:
        decoded = json.loads(response_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise OauthBrokerInvalidResponseError("broker response is not valid JSON") from None
    if not isinstance(decoded, dict) or not set(decoded).issubset(_ALLOWED_TOKEN_RESPONSE_KEYS):
        raise OauthBrokerInvalidResponseError("broker response contains unexpected fields")

    access_token = decoded.get("access_token")
    token_type = decoded.get("token_type")
    expires_in = decoded.get("expires_in")
    if (
        not isinstance(access_token, str)
        or not access_token
        or not isinstance(token_type, str)
        or not token_type
        or not isinstance(expires_in, int)
        or isinstance(expires_in, bool)
        or expires_in <= 0
    ):
        raise OauthBrokerInvalidResponseError("broker response is missing required token fields")

    # A real OIDC broker's id_token is a signed JWT string. The mock IdP
    # (tests/level2/mock_idp.py) instead nests a claims dict here for legacy
    # compatibility with an older SP integration; treat anything that isn't
    # a JWT-shaped string as absent rather than propagating the wrong type --
    # the caller falls back to verifying access_token, which the mock always
    # issues as a proper signed JWT.
    raw_id_token = decoded.get("id_token")
    id_token = raw_id_token if isinstance(raw_id_token, str) and raw_id_token else None

    return BrokerTokenResponse(
        access_token=access_token,
        token_type=token_type,
        expires_in=expires_in,
        id_token=id_token,
    )
