#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise SystemExit(f"anchor mismatch in {path}: {old[:120]!r} count={text.count(old)}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


# Backend: session-bound CSRF protection. The browser-readable token is an HMAC
# over the opaque HttpOnly auth-session cookie, domain-separated from the hash
# used as the DB key. No new persisted secret or schema is introduced.
(ROOT / "03_Implement/backend/src/kj_atlas_api/session_csrf.py").write_text(
'''from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from urllib.parse import urlsplit

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from kj_atlas_api.active_tenant_session import tenant_session_cookie_is_secure
from kj_atlas_api.trusted_auth_edge import _extract_bearer_token

AUTH_SESSION_COOKIE = "Kj-Atlas-Auth-Session"
CSRF_COOKIE = "Kj-Atlas-Csrf"
CSRF_HEADER = "X-Kj-Atlas-Csrf"
CSRF_TOKEN_MAX_AGE_SECONDS = 3600
_MAX_AUTH_SESSION_COOKIE_LENGTH = 256
_SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "TRACE"})
_CSRF_DOMAIN_SEPARATOR = b"kj-atlas-session-csrf-v1\\x00"


@dataclass(frozen=True, slots=True)
class CsrfFailure:
    status_code: int
    code: str
    message: str


def derive_session_csrf_token(raw_session_id: str, *, key: bytes) -> str:
    if (
        not raw_session_id
        or len(raw_session_id) > _MAX_AUTH_SESSION_COOKIE_LENGTH
        or raw_session_id.strip() != raw_session_id
        or any(not character.isprintable() for character in raw_session_id)
    ):
        raise ValueError("auth session cookie is not canonical")
    return hmac.new(
        key,
        _CSRF_DOMAIN_SEPARATOR + raw_session_id.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def set_session_csrf_cookie(
    *, response: Response, raw_session_id: str, key: bytes, runtime_profile: str
) -> None:
    response.set_cookie(
        key=CSRF_COOKIE,
        value=derive_session_csrf_token(raw_session_id, key=key),
        httponly=False,
        secure=tenant_session_cookie_is_secure(runtime_profile),
        samesite="strict",
        max_age=CSRF_TOKEN_MAX_AGE_SECONDS,
        path="/",
    )


def clear_session_csrf_cookie(*, response: Response, runtime_profile: str) -> None:
    response.delete_cookie(
        key=CSRF_COOKIE,
        httponly=False,
        secure=tenant_session_cookie_is_secure(runtime_profile),
        samesite="strict",
        path="/",
    )


def _same_origin_host(request: Request) -> bool:
    origin = request.headers.get("origin")
    host = request.headers.get("host")
    if (
        origin is None
        or host is None
        or not origin
        or not host
        or origin.strip() != origin
        or host.strip() != host
        or len(origin) > 2048
        or len(host) > 255
        or any(not character.isprintable() for character in origin + host)
    ):
        return False
    parsed = urlsplit(origin)
    try:
        parsed.port
    except ValueError:
        return False
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path not in {"", "/"}
        or parsed.query
        or parsed.fragment
    ):
        return False
    return (
        parsed.netloc.lower() == host.lower()
        and parsed.scheme.lower() == request.url.scheme.lower()
    )


def validate_bff_csrf_request(request: Request, *, key: bytes | None) -> CsrfFailure | None:
    if request.method.upper() in _SAFE_METHODS:
        return None
    # The trusted auth edge gives an explicitly-present bearer credential
    # priority over the BFF cookie. Preserve that compatibility boundary until
    # the separate SPA bearer cutover is completed.
    if _extract_bearer_token(request) is not None:
        return None

    raw_session_id = request.cookies.get(AUTH_SESSION_COOKIE)
    if not raw_session_id:
        # No BFF credential: leave normal authentication/authorization to the
        # route. This middleware is not a replacement auth mechanism.
        return None
    if key is None:
        return CsrfFailure(
            503,
            "csrf_protection_unavailable",
            "Session request protection is unavailable.",
        )
    try:
        expected = derive_session_csrf_token(raw_session_id, key=key)
    except ValueError:
        return CsrfFailure(403, "csrf_validation_failed", "Request validation failed.")

    if not _same_origin_host(request):
        return CsrfFailure(403, "csrf_validation_failed", "Request validation failed.")
    presented = request.headers.get(CSRF_HEADER)
    if (
        presented is None
        or len(presented) != 64
        or any(character not in "0123456789abcdef" for character in presented)
        or not hmac.compare_digest(presented, expected)
    ):
        return CsrfFailure(403, "csrf_validation_failed", "Request validation failed.")
    return None


class BffCsrfProtectionMiddleware(BaseHTTPMiddleware):
    """ADR-0074 decision 5: protect unsafe BFF-cookie requests globally.

    SameSite=Strict remains the first browser boundary. For any unsafe request
    that actually relies on the BFF cookie, this middleware also requires a
    same-origin Origin/Host pair and a session-bound synchronizer header.
    """

    async def dispatch(self, request: Request, call_next):
        failure = validate_bff_csrf_request(
            request,
            key=getattr(request.app.state, "saas_auth_session_hash_key", None),
        )
        if failure is not None:
            return JSONResponse(
                status_code=failure.status_code,
                content={"detail": {"code": failure.code, "message": failure.message}},
                headers={"Cache-Control": "no-store", "Pragma": "no-cache"},
            )
        return await call_next(request)
''', encoding="utf-8")

(ROOT / "03_Implement/backend/tests/test_saas_session_csrf.py").write_text(
'''from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from kj_atlas_api.session_csrf import (
    AUTH_SESSION_COOKIE,
    CSRF_COOKIE,
    CSRF_HEADER,
    BffCsrfProtectionMiddleware,
    derive_session_csrf_token,
)

KEY = bytes.fromhex("11" * 32)


def _app(*, key: bytes | None = KEY) -> FastAPI:
    app = FastAPI()
    app.state.saas_auth_session_hash_key = key
    app.add_middleware(BffCsrfProtectionMiddleware)

    @app.get("/resource")
    def read_resource():
        return {"ok": True}

    @app.post("/resource", status_code=204)
    def mutate_resource():
        return None

    return app


def _csrf(raw_session_id: str) -> str:
    return derive_session_csrf_token(raw_session_id, key=KEY)


def _cookie_client(raw_session_id: str = "session-a", *, key: bytes | None = KEY) -> TestClient:
    client = TestClient(_app(key=key))
    client.cookies.set(AUTH_SESSION_COOKIE, raw_session_id)
    client.cookies.set(CSRF_COOKIE, _csrf(raw_session_id))
    return client


def test_valid_same_origin_session_bound_header_allows_unsafe_request() -> None:
    client = _cookie_client()
    response = client.post(
        "/resource",
        headers={"Origin": "http://testserver", CSRF_HEADER: _csrf("session-a")},
    )
    assert response.status_code == 204


def test_missing_csrf_header_is_rejected() -> None:
    client = _cookie_client()
    response = client.post("/resource", headers={"Origin": "http://testserver"})
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "csrf_validation_failed"


def test_token_from_another_session_is_rejected() -> None:
    client = _cookie_client("session-a")
    response = client.post(
        "/resource",
        headers={"Origin": "http://testserver", CSRF_HEADER: _csrf("session-b")},
    )
    assert response.status_code == 403


def test_tampered_token_is_rejected() -> None:
    client = _cookie_client()
    token = _csrf("session-a")
    response = client.post(
        "/resource",
        headers={"Origin": "http://testserver", CSRF_HEADER: token[:-1] + ("0" if token[-1] != "0" else "1")},
    )
    assert response.status_code == 403


def test_cross_site_origin_is_rejected_even_with_correct_token() -> None:
    client = _cookie_client()
    response = client.post(
        "/resource",
        headers={"Origin": "https://evil.example", CSRF_HEADER: _csrf("session-a")},
    )
    assert response.status_code == 403


def test_missing_origin_is_rejected_even_with_correct_token() -> None:
    client = _cookie_client()
    response = client.post("/resource", headers={CSRF_HEADER: _csrf("session-a")})
    assert response.status_code == 403


def test_safe_method_does_not_require_csrf_header() -> None:
    client = _cookie_client()
    assert client.get("/resource").status_code == 200


def test_bearer_priority_path_does_not_require_cookie_csrf() -> None:
    client = _cookie_client()
    response = client.post(
        "/resource",
        headers={"X-Kj-Atlas-Authorization": "Bearer malformed-but-present"},
    )
    assert response.status_code == 204


def test_unsafe_cookie_request_fails_closed_when_server_key_is_unavailable() -> None:
    client = _cookie_client(key=None)
    response = client.post(
        "/resource",
        headers={"Origin": "http://testserver", CSRF_HEADER: _csrf("session-a")},
    )
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "csrf_protection_unavailable"


def test_no_auth_session_cookie_leaves_auth_decision_to_route() -> None:
    client = TestClient(_app())
    response = client.post("/resource")
    assert response.status_code == 204
''', encoding="utf-8")

# Frontend: read the non-HttpOnly CSRF cookie and attach it as a custom header.
(ROOT / "03_Implement/frontend/src/session/csrf.ts").write_text(
'''export const CSRF_COOKIE = "Kj-Atlas-Csrf";
export const CSRF_HEADER = "X-Kj-Atlas-Csrf";
const CSRF_TOKEN_PATTERN = /^[0-9a-f]{64}$/;

export function csrfTokenFromCookie(cookieSource: string): string | undefined {
  for (const part of cookieSource.split(";")) {
    const trimmed = part.trim();
    const separator = trimmed.indexOf("=");
    if (separator <= 0) {
      continue;
    }
    const name = trimmed.slice(0, separator);
    const value = trimmed.slice(separator + 1);
    if (name === CSRF_COOKIE && CSRF_TOKEN_PATTERN.test(value)) {
      return value;
    }
  }
  return undefined;
}

export function csrfHeader(): Record<string, string> {
  const cookieSource = typeof document === "undefined" ? "" : document.cookie;
  const token = csrfTokenFromCookie(cookieSource);
  return token ? { [CSRF_HEADER]: token } : {};
}
''', encoding="utf-8")

(ROOT / "03_Implement/frontend/src/session/csrf.test.ts").write_text(
'''import { describe, expect, it } from "vitest";

import { CSRF_HEADER, csrfTokenFromCookie } from "./csrf";

const TOKEN = "a".repeat(64);

describe("session CSRF cookie", () => {
  it("extracts only the canonical bound token cookie", () => {
    expect(csrfTokenFromCookie(`other=x; Kj-Atlas-Csrf=${TOKEN}; tail=y`)).toBe(TOKEN);
  });

  it("rejects missing, malformed, and non-hex token values", () => {
    expect(csrfTokenFromCookie("other=x")).toBeUndefined();
    expect(csrfTokenFromCookie("Kj-Atlas-Csrf=short")).toBeUndefined();
    expect(csrfTokenFromCookie(`Kj-Atlas-Csrf=${"g".repeat(64)}`)).toBeUndefined();
  });

  it("keeps the wire header name stable", () => {
    expect(CSRF_HEADER).toBe("X-Kj-Atlas-Csrf");
  });
});
''', encoding="utf-8")

(ROOT / "03_Implement/frontend/src/api/client_csrf_contract.test.ts").write_text(
'''import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const source = readFileSync(new URL("./client.ts", import.meta.url), "utf8");

describe("API client CSRF contract", () => {
  it("keeps every unsafe API fetch near the shared tenant/CSRF header path", () => {
    const methodPattern = /method:\\s*"(?:POST|PUT|PATCH|DELETE)"/g;
    const matches = [...source.matchAll(methodPattern)];
    expect(matches.length).toBeGreaterThan(0);
    for (const match of matches) {
      const offset = match.index ?? 0;
      const window = source.slice(Math.max(0, offset - 900), Math.min(source.length, offset + 900));
      expect(
        window.includes("tenantSessionPreconditionHeaders") || window.includes("csrfHeader"),
        `unsafe fetch near offset ${offset} bypasses the CSRF header path`,
      ).toBe(true);
    }
  });
});
''', encoding="utf-8")

# oauth_bff: issue and clear the session-bound CSRF cookie alongside auth session.
replace_once(
    "03_Implement/backend/src/kj_atlas_api/oauth_bff.py",
    "from kj_atlas_api.settings import settings\n",
    "from kj_atlas_api.settings import settings\nfrom kj_atlas_api.session_csrf import clear_session_csrf_cookie, set_session_csrf_cookie\n",
)
replace_once(
    "03_Implement/backend/src/kj_atlas_api/oauth_bff.py",
    '''    redirect.set_cookie(\n        key=_AUTH_SESSION_COOKIE,\n        value=raw_session_id,\n        httponly=True,\n        secure=tenant_session_cookie_is_secure(request.app.state.runtime_profile),\n        samesite="strict",\n        max_age=_AUTH_SESSION_MAX_AGE_SECONDS,\n        path="/",\n    )\n    return redirect\n''',
    '''    redirect.set_cookie(\n        key=_AUTH_SESSION_COOKIE,\n        value=raw_session_id,\n        httponly=True,\n        secure=tenant_session_cookie_is_secure(request.app.state.runtime_profile),\n        samesite="strict",\n        max_age=_AUTH_SESSION_MAX_AGE_SECONDS,\n        path="/",\n    )\n    set_session_csrf_cookie(\n        response=redirect,\n        raw_session_id=raw_session_id,\n        key=hash_key,\n        runtime_profile=request.app.state.runtime_profile,\n    )\n    return redirect\n''',
)
replace_once(
    "03_Implement/backend/src/kj_atlas_api/oauth_bff.py",
    '''    response.delete_cookie(\n        key=_AUTH_SESSION_COOKIE,\n        httponly=True,\n        secure=tenant_session_cookie_is_secure(request.app.state.runtime_profile),\n        samesite="strict",\n        path="/",\n    )\n''',
    '''    response.delete_cookie(\n        key=_AUTH_SESSION_COOKIE,\n        httponly=True,\n        secure=tenant_session_cookie_is_secure(request.app.state.runtime_profile),\n        samesite="strict",\n        path="/",\n    )\n    clear_session_csrf_cookie(\n        response=response,\n        runtime_profile=request.app.state.runtime_profile,\n    )\n''',
)

# Install the global unsafe-method guard. It is conditional on a BFF auth cookie,
# so single-tenant/admin/no-cookie and bearer-priority compatibility paths stay unchanged.
replace_once(
    "03_Implement/backend/src/kj_atlas_api/main.py",
    "from kj_atlas_api.request_body_safety import JsonRequestBodySafetyMiddleware\n",
    "from kj_atlas_api.request_body_safety import JsonRequestBodySafetyMiddleware\nfrom kj_atlas_api.session_csrf import BffCsrfProtectionMiddleware\n",
)
replace_once(
    "03_Implement/backend/src/kj_atlas_api/main.py",
    "app.add_middleware(JsonRequestBodySafetyMiddleware)\n",
    "app.add_middleware(JsonRequestBodySafetyMiddleware)\napp.add_middleware(BffCsrfProtectionMiddleware)\n",
)

# Existing persister commentary incorrectly says anti-forgery belongs to each
# persister. AC-9 is now enforced at the BFF request boundary instead.
replace_once(
    "03_Implement/backend/src/kj_atlas_api/active_tenant_session.py",
    '''    Implementations own anti-forgery validation and the auth-edge-specific session\n    format. ``persist`` must atomically compare the expected version, update the\n''',
    '''    The BFF request boundary owns anti-forgery validation; persisters own the\n    auth-edge-specific session format. ``persist`` must atomically compare the expected version, update the\n''',
)
replace_once(
    "03_Implement/backend/src/kj_atlas_api/active_tenant_session.py",
    "    - Adds CSRF token binding (currently SameSite=strict cookie only)\n",
    "    - Uses the shared BFF CSRF middleware when cookie authentication is active\n",
)

# Frontend common header path. Bearer-priority calls deliberately do not copy the
# browser-readable CSRF token into a request that authenticates with bearer.
replace_once(
    "03_Implement/frontend/src/api/client.ts",
    'import { authorizationHeader } from "../session/token_store";\n',
    'import { authorizationHeader } from "../session/token_store";\nimport { csrfHeader } from "../session/csrf";\n',
)
replace_once(
    "03_Implement/frontend/src/api/client.ts",
    '''function tenantSessionPreconditionHeaders(\n  options: TenantScopedRequestOptions,\n): Record<string, string> {\n  const headers: Record<string, string> = { ...authorizationHeader() };\n''',
    '''function tenantSessionPreconditionHeaders(\n  options: TenantScopedRequestOptions,\n): Record<string, string> {\n  const authHeaders = authorizationHeader();\n  const headers: Record<string, string> = {\n    ...authHeaders,\n    ...(Object.keys(authHeaders).length === 0 ? csrfHeader() : {}),\n  };\n''',
)
replace_once(
    "03_Implement/frontend/src/api/client.ts",
    '''    headers: {\n      Accept: "application/json",\n      "Content-Type": "application/json",\n    },\n''',
    '''    headers: {\n      Accept: "application/json",\n      "Content-Type": "application/json",\n      ...csrfHeader(),\n    },\n''',
)

# API contract: document the already-Accepted ADR-0074 boundary next to session routes.
replace_once(
    "02_Architecture/api.md",
    '''**GET** `/session/context`\n\n- Response: `TenantSessionContextResponse`\n''',
    '''BFFの `Kj-Atlas-Auth-Session` cookieで認証するunsafe method（POST/PUT/PATCH/DELETE）は、ADR-0074 Decision 5に従い、SameSite=Strictだけに依存しない。`Origin` のscheme/hostが現在のrequest `Host` と一致し、かつsession cookieへHMAC束縛して `Kj-Atlas-Csrf`（非HttpOnly）で払い出した値を `X-Kj-Atlas-Csrf` headerで返送した場合だけ処理する。欠落・別session・改ざん・cross-site Originはresource lookup前に403で拒否する。明示Bearer credentialがある互換経路はtrusted auth edgeと同じ優先順位でこのcookie用guardの対象外とし、SPA Bearer廃止そのものは別のcutover境界として扱う。\n\n**GET** `/session/context`\n\n- Response: `TenantSessionContextResponse`\n''',
)

# Close the issue only after the workflow has run the tests/validators. The
# working tree move happens now, but no branch commit is made until validation succeeds.
issue = ROOT / "01_Plans/issues/issue-SAAS-TENANT-SESSION-BINDING-01-principal-keyed-session-state.md"
done = ROOT / "01_Plans/issues/done/issue-SAAS-TENANT-SESSION-BINDING-01-principal-keyed-session-state.md"
text = issue.read_text(encoding="utf-8")
for old, new in [
    ("- Status: Open", "- Status: Done"),
    (
        "- [ ] AC-9: cookieを採用する場合はserver-side session ownershipとanti-forgery契約を固定し、未提示・別session・改ざん・cross-site要求を拒否する。採用しない場合は現在のversion cookieとanti-forgery達成表現を削除する。",
        "- [x] AC-9: cookieを採用する場合はserver-side session ownershipとanti-forgery契約を固定し、未提示・別session・改ざん・cross-site要求を拒否する。採用しない場合は現在のversion cookieとanti-forgery達成表現を削除する。\n  — 2026-09-04。ADR-0074は既に案2（server-owned BFF session）をAcceptedとしており、判断待ちではなかった。unsafe methodをBFF cookieで認証する場合だけ、SameSite=Strictに加えてOrigin/Host一致とsession-bound `X-Kj-Atlas-Csrf`を共通middlewareで要求する。CSRF tokenはopaque auth-session cookieへserver keyでHMAC束縛し、非HttpOnly `Kj-Atlas-Csrf` cookieからfrontendがheaderへ複写する。未提示・別session・改ざん・cross-siteは403、server key欠落は503でfail-closed。Bearer優先の互換経路は別cutoverまで維持する。",
    ),
]:
    if text.count(old) != 1:
        raise SystemExit(f"issue anchor mismatch: {old[:80]!r} count={text.count(old)}")
    text = text.replace(old, new, 1)
checkpoint = """\n### Implementation checkpoint 2026-09-04: AC-9 cookie/anti-CSRF境界を実装\n\n`ADR-0074` のAcceptance Gate回答案2を再確認すると、cookie採用・synchronizer token・Origin/Host検証は2026-08-13にMaintainer承認済みだった。そこで新たな設計判断は起こさず、既存session hash keyをdomain separationしてauth-session cookieへHMAC束縛したCSRF tokenを払い出す。unsafe requestは、BFF cookieを実際に認証に使う場合だけOrigin/Hostとheader tokenを共通middlewareで検証する。Bearer credentialが明示される現行互換経路はtrusted auth edgeと同じ優先順位で除外し、SPA Bearer cutoverを本Issueへ混ぜない。\n\nこの方式ではCSRF token自体をDBへ追加保存せず、Document/tenant/sessionの正本データも増やさない。tokenはbrowser-readableだがauth-session cookieはHttpOnlyのままで、別sessionのtokenはHMAC一致しない。logoutではauth cookieと同時にCSRF cookieも削除する。\n"""
marker = "\n## 検証計画\n"
if marker not in text:
    raise SystemExit("issue validation-plan marker missing")
text = text.replace(marker, checkpoint + marker, 1)
done.parent.mkdir(parents=True, exist_ok=True)
done.write_text(text, encoding="utf-8")
issue.unlink()

print("patched SaaS session CSRF contract")
