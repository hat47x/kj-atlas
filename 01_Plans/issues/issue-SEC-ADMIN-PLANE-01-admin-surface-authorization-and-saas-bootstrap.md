# Issue: SEC-ADMIN-PLANE-01 管理APIに業務面と分離された認可がなく、かつSaaSではブートストラップ不能

- Type: Security / Bug
- Status: Draft
- Source Issue: TBD
- Priority: P0
- Owner: Unassigned
- Scope: `01_Plans/adr/ADR-0072-control-plane-authorization-separation.md`, `03_Implement/backend/src/kj_atlas_api/routes/admin.py`, `03_Implement/backend/src/kj_atlas_api/main.py`, `03_Implement/backend/src/kj_atlas_api/settings.py`, `04_Documentation/security.md`, `04_Documentation/configuration.md`, `THREAT_MODEL.md`, `02_Architecture/enterprise_architecture.html`
- Related ADR/Spec: `01_Plans/adr/ADR-0072-control-plane-authorization-separation.md`, `01_Plans/adr/ADR-0020-oidc-saml-mock-idp-sp-profile.md`, `01_Plans/adr/ADR-0062-explicit-http-integration-fail-fast.md`, `02_Architecture/enterprise_architecture.html`
- Expected verification level: `integration`

> **本issueは `ADR-0072` の採択を前提とする。** ADR が Proposed の間は着手しないこと。ADR が Rejected の場合、本issueも取り下げる。

## 課題

### 課題1: 管理APIに業務面と区別された認可がない（Critical）

`/admin/provision/*` の唯一の保護はグローバル middleware `require_api_key`（`main.py:135-146`）である。`settings.py:263-266` により `api_key` の既定値は `None` で、その場合 middleware は素通りする。

```
$ KJ_ATLAS_RUNTIME_PROFILE=enterprise-production python3 -c \
  "from kj_atlas_api.settings import Settings; print(repr(Settings().api_key))"
None
```

**`enterprise-production` が完全無認証で起動する。** キー設定時も、文書API・AI API・管理APIが同一の共有静的キー1本で保護される。

`POST /admin/provision/identity-providers`（`routes/admin.py:324-417`）は**信頼するJWT発行者と JWKS URI を登録する**。到達できる主体は、自分の鍵で IdP を登録し `_resolve_identity_provider()`（`trusted_auth_edge.py:124-135`）に一致するトークンを自作して、**任意利用者・任意テナントとして認証できる**。`POST /admin/provision/tenant-identity-providers` は外部テナント参照→内部 `tenants.id` の対応を作るため越境の起点になる。

`02_Architecture/enterprise_architecture.html` §06 の自己要件（Workspace Data Plane / Tenant Admin / Platform Control Plane の分離）を満たしていない。

### 課題2: SaaS プロファイルがブートストラップ不能（Critical）

`require_single_tenant_provisioning_surface`（`routes/admin.py:75-94`）は `single-tenant` 以外で 404 を返す。`runtime_bootstrap.py:21-22` により `saas-multitenant` は該当する。

```
$ python3 -c "
from unittest.mock import MagicMock
from fastapi import HTTPException
from kj_atlas_api.routes.admin import require_single_tenant_provisioning_surface
for p in ['enterprise-production','saas-multitenant']:
    r = MagicMock(); r.app.state.runtime_profile = p
    try: require_single_tenant_provisioning_surface(r); print(f'{p} -> ALLOWED')
    except HTTPException as e: print(f'{p} -> HTTP {e.status_code} {e.detail}')"
enterprise-production -> ALLOWED
saas-multitenant      -> HTTP 404 {'code': 'strict_provisioning_unavailable', ...}
```

一方 `trusted_saas_runtime.py:298-304` の起動時警告は、この 404 になるエンドポイントの使用を指示している。

> Register at least one via `POST /admin/provision/identity-providers` before authentication requests will succeed.

**指示されたエンドポイントが、指示された状況で 404 を返す。** IdP 登録なしに認証は成立しないため、SaaS は DB 直接操作なしに起動できない。

### 利用者・運用への影響

- 企業・行政案件: 管理面の認可欠如は調達要件・監査で確実に指摘される。DB 直接投入を正規手順にすることも同様。
- SIer 視点: `enterprise-production` が無認証で起動できる既定は、構築ミスがそのまま全面公開になる。`ADR-0062` が access_control / audit に対して既に採った fail-fast 方針と不整合。

## 対応方針

`ADR-0072` の D1 / D2 / D3 の決定に従う。ADR の推奨は D1=A+B の二段、D2=A、D3=A だが、**採択された決定を正とする**。

実装時の注意:

- `require_single_tenant_provisioning_surface` を「profile による到達可否」から「認可判定」へ置き換える場合、`local-dev` / `evaluation` の開発利便性を壊さないこと。
- ブートストラップ経路（IdP 未登録状態で使える経路）と通常運用経路を、コード上でも文書上でも区別すること。
- 秘密値（admin bearer、JWKS URI 以外の資格情報）をレスポンス・ログへ反射しないこと。既存の `_validate_canonical_bearer`（`settings.py:70-76`）の作法に合わせる。

## 受入条件

- [ ] AC-1: `enterprise-production` および `saas-multitenant` は、認証手段が未設定なら起動時に fail-fast する（D3=A 採択時）。または採択された D3 案の挙動をテストで固定する。
- [ ] AC-2: `/admin/provision/**` が業務API と分離された認可を要求し、業務面の資格情報だけでは到達できないことを integration テストで固定する。
- [ ] AC-3: `saas-multitenant` で IdP 登録が実行可能な経路が存在し、その手順が `04_Documentation/` に記載されている。手順どおりに空DBから認証成立まで到達できることを検証する。
- [ ] AC-4: `trusted_saas_runtime.py` の起動時警告が、実際に到達可能な手順を案内している（文言と実装の一致）。
- [ ] AC-5: 管理面操作が監査証跡に記録される（主体・時刻・対象）。`SEC-LLM-AUDIT-01` と重複しない範囲で、既存 audit dispatcher を用いる。
- [ ] AC-6: `THREAT_MODEL.md` と `04_Documentation/security.md` に、管理面の保護要件（アプリ側保証と前段委譲の責務境界）を追記する。
- [ ] AC-7: 越境の negative matrix — 業務面キーで `/admin/provision/*` へ到達不可、他テナントの `tenant-identity-providers` を登録不可 — を integration テストで固定する。

## 依存関係

- `01_Plans/issues/issue-SAAS-TENANT-AUTHEDGE-01-no-concrete-trusted-auth-edge-implementation.md`（本件が露出した実装の親）

## 検証

- `python -m pytest tests/test_admin_identity_provider_registration.py tests/test_saas_e2e_tenant_isolation.py -q`
- `python -m pytest tests/ -q`（backend 全体回帰）
- `python 01_Plans/docs_check.py`
