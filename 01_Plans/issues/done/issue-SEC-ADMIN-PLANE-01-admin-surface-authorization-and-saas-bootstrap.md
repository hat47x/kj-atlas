# Issue: SEC-ADMIN-PLANE-01 管理APIに業務面と分離された認可がなく、かつSaaSではブートストラップ不能

- Type: Security / Bug
- Status: Done
- Source Issue: `SAAS-TENANT-AUTHEDGE-01`
- Priority: P0
- Owner: Maintainer
- Scope: `01_Plans/adr/ADR-0072-control-plane-authorization-separation.md`, `03_Implement/backend/src/kj_atlas_api/routes/admin.py`, `03_Implement/backend/src/kj_atlas_api/main.py`, `03_Implement/backend/src/kj_atlas_api/settings.py`, `04_Documentation/security.md`, `04_Documentation/configuration.md`, `THREAT_MODEL.md`, `02_Architecture/enterprise_architecture.html`
- Related ADR/Spec: `01_Plans/adr/ADR-0072-control-plane-authorization-separation.md`, `01_Plans/adr/ADR-0020-oidc-saml-mock-idp-sp-profile.md`, `01_Plans/adr/ADR-0062-explicit-http-integration-fail-fast.md`, `02_Architecture/enterprise_architecture.html`
- Expected verification level: `integration`

> **2026-08-13: `ADR-0072` は Accepted（D1=A+B の二段 / D2=A / D3=A）。着手可能。**
>
> 採択内容と、採択時に加えられた D2 の profile 差の分離（`enterprise-production` は静的 bearer で閉じるが `saas-multitenant` は閉じない）は `ADR-0072`「採択記録（2026-08-13）」を正とする。D3=A（本番相当 profile で認証手段未設定なら `Settings()` 構築時に fail-fast）が、本issueが扱う「`enterprise-production` が既定で完全無認証起動する」欠陥の直接の対策にあたる。

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

`ADR-0072` の D1 / D2 / D3 の決定に従う。**2026-08-13 に D1=A+B の二段 / D2=A / D3=A が採択された**（推奨どおり）。加えて D2=A の実装は profile 差で2段に分ける——`enterprise-production` は静的 admin bearer による bootstrap で閉じるが、`saas-multitenant` は「組織の実在確認を伴う別工程」を前提とするため、テナント発行経路は運用手順として閉じたままとし API の到達性のみ D1 の認可で担保する。詳細は `ADR-0072`「採択記録」。

実装時の注意:

- `require_single_tenant_provisioning_surface` を「profile による到達可否」から「認可判定」へ置き換える場合、`local-dev` / `evaluation` の開発利便性を壊さないこと。
- ブートストラップ経路（IdP 未登録状態で使える経路）と通常運用経路を、コード上でも文書上でも区別すること。
- 秘密値（admin bearer、JWKS URI 以外の資格情報）をレスポンス・ログへ反射しないこと。既存の `_validate_canonical_bearer`（`settings.py:70-76`）の作法に合わせる。

## 受入条件

- [x] AC-1: `enterprise-production` および `saas-multitenant` は、認証手段が未設定なら起動時に fail-fast する（D3=A）。`Settings()` 構築時に `ValueError`。`test_control_plane_authorization.py` で固定。
- [x] AC-2: `/admin/provision/**` が業務API と分離された認可を要求し、業務面の資格情報だけでは到達できない。3ルート全てについて `X-Api-Key` 提示時に 401 `control_plane_unauthorized` を返すことを固定。
- [x] AC-3: `saas-multitenant` で IdP 登録が実行可能な経路が存在する（D2=A。旧実装は 404 だった）。手順は `04_Documentation/security.md`「管理面（Control Plane）の保護」に記載。**空DBから認証成立までの通し検証は未実施**（下記「残作業」）。
- [x] AC-4: `trusted_saas_runtime.py` の起動時警告が、実際に到達可能な手順を案内している。`X-Admin-Api-Key` と `KJ_ATLAS_ADMIN_API_KEY` を明記し、業務面キーが使えないことも記載。文言と実装の一致をテストで固定。
- [x] AC-5: 管理面操作の監査証跡（主体・時刻・対象）。→ **`issue-SEC-ADMIN-PLANE-03` で完了**（2026-08-15・iteration 40）。`admin_audit_events` テーブル＋記録middleware＋`GET /admin/provision/audit`（allowlist・composite cursor）。`verify_api_admin.sh` 実走行10/10。
- [x] AC-6: `THREAT_MODEL.md` と `04_Documentation/security.md` に管理面の保護要件を追記した。アプリ側保証と前段委譲（D1=C）の責務境界、および SaaS でのテナント発行の業務的正当性が範囲外であることを明記。
- [x] AC-7: 越境の negative matrix を integration テストで固定した — 業務面キーで到達不可、資格情報なしで到達不可、誤った資格情報で到達不可、拒否応答が「未設定」と「誤り」を区別しない、提示値・設定値を反射しない、未知 profile が open へ fall through しない。

## 残作業（Done 化の注記）

- **AC-5（管理面の監査証跡）**: **`issue-SEC-ADMIN-PLANE-03` で完了**（iteration 40・2026-08-15）。`admin_audit_events` テーブル＋記録middleware＋`GET /admin/provision/audit`（allowlist・composite cursor）。`verify_api_admin.sh` 実走行10/10。
- **AC-3 の通し検証**: 空DBから `saas-multitenant` を起動し、制御プレーン資格情報で IdP 登録 → テナント紐付け → 実JWT で認証成立まで到達する E2E は未実施。**`QA-E2E-SAAS-01`（tenant session coverage gap）の範囲へ寄せる**（iteration 72 の棚卸しで決定）。AC-3 自体は経路の存在と分離認可をテストで固定済みであり、本issueは Done 化。

## 依存関係

- `01_Plans/issues/done/issue-SAAS-TENANT-AUTHEDGE-01-no-concrete-trusted-auth-edge-implementation.md`（本件が露出した実装の親）

## 検証

- `python -m pytest tests/test_admin_identity_provider_registration.py tests/test_saas_e2e_tenant_isolation.py -q`
- `python -m pytest tests/ -q`（backend 全体回帰）
- `python 01_Plans/docs_check.py`
