# Issue Draft: SAAS-TENANT-AUTHEDGE-01 実trusted auth edgeが未着手のまま7件のACを塞いでいる

- Type: Feature request / Security boundary
- Status: Draft
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/auth_context.py`, `03_Implement/backend/src/kj_atlas_api/trusted_saas_runtime.py`, `03_Implement/backend/src/kj_atlas_api/tenant_context.py`, `03_Implement/backend/src/kj_atlas_api/main.py`, `03_Implement/backend/src/kj_atlas_api/settings.py`
- Related Backlog: `SAAS-TENANT-01`
- Related ADR/Spec: `01_Plans/issues/issue-SAAS-TENANT-01-tenant-context-and-storage-foundation.md`, `01_Plans/adr/ADR-0059-saas-tenant-authorization-boundary.md`, `01_Plans/adr/ADR-0020-oidc-saml-mock-idp-sp-profile.md`
- Expected verification level: `e2e`

## 課題

`SAAS-TENANT-01`のAC-1〜3/5/11は完了しているが、AC-4/6/7/8/9/10/12/13は未完了のまま残っている。issueの実装チェックポイント（2026-07-17以降、30箇所以上）は毎回同じ一文で終わる——「実trusted auth edge...は未完了であり、AC-4...とSaaS profile起動拒否を継続する」。この一文が繰り返され続けている一方、「実auth edgeを作る」という作業自体は一度も独立したissueやADRへ分解されていない。

コード上の裏付け:

- `SaasIdentityContextResolver`（`auth_context.py:35`）は`Protocol`として定義されているだけで、具象実装が存在しない。
- `install_trusted_saas_runtime()`（`trusted_saas_runtime.py:203`）は自身の定義以外から一度も呼ばれていない（`grep "install_trusted_saas_runtime\(|TrustedSaasRuntimeAdapters\("`で確認、呼び出し元ゼロ）。
- 一方、検証済みclaimからtenant contextを解決する純粋関数`resolve_verified_claim_tenant_context()`（`tenant_context.py:150-189`）と、その関数が実装するはずのAC-4「tenant不明→deny」ロジック自体は完全に実装・unit testされている（`test_verified_tenant_context.py`）。つまり**ロジックはあるが、実際のHTTPリクエストからそのロジックへ到達する経路が存在しない**。
- `access_control.py`の`ExternalPolicyAccessControlAdapter`（capability/policy-ref判定＝AC-4本文の「PDP」相当）は実装・e2e検証済みだが、これは「すでにtenant contextが解決済みのリクエスト」を前提にしており、identity検証（誰がこのリクエストを送っているか）は別の層である。今回のissueが指すのはこの手前の層——IdPが発行した実トークンを検証してtenant/principalへ写す層——が未着手であること。

## なぜ人的判断（ADR）が必要か

AGENTS.md §6は「長期的・横断的・破壊的な契約変更、安全境界変更、複数の合理的選択肢が残る場合」にADRを要求する。実auth edgeの実装は複数の未決定点を含み、コードだけでは選べない。

- プロトコル選択: OIDCのみか、`ADR-0020`のタイトルが示すSAMLも実装するか。`identity_providers`/`tenant_identity_providers`テーブルは既にプロトコル非依存の形で存在するが、実装順序は未決定。
- ライブラリ選択: JWT検証・JWKS取得・鍵ローテーションを自前実装するか、既存ライブラリ（`python-jose`、`authlib`等）に依存するか。
- IdP到達不能時の扱い: `AccessControlAdapter`側で確立済みのfail-closed（`access_control_fail_safe_mode=deny`）パターンをidentity検証層でも踏襲するか、別の失敗モードを設けるか。
- 本番投入の前提条件: 実SaaS顧客が存在しない現段階で、本格的なIdP統合に投資する優先度。

## 影響

`SAAS-TENANT-01`のAC-4（tenant不明のdeny）は resolver 単体では証明済みだが、実HTTPリクエスト経由では検証不可能——テストでしか到達しない経路のため、本番同等の検証ができない。AC-6（`GET /session/context`のmembership allowlist）、AC-7（capability/audience分離）、AC-8（tenantId伝播）、AC-9（export/import再認可）、AC-10（越境negative matrix）、AC-12/13（実画面回帰）も、実質的に「本物のauthenticated principal」を前提としており、この層が無い限りe2eでの本番同等証明ができない。settings-level fail-fast（saas-multitenant profileの起動拒否）は、この欠落を理由に維持されている——このissueが解決されるまで、その起動拒否を緩めてはならない。

## Acceptance

- [ ] ADRが起票され、プロトコル範囲（OIDC先行か、SAML同時か）、ライブラリ、鍵ローテーション、IdP到達不能時の失敗モードが受理されている。
- [ ] `SaasIdentityContextResolver`の具象実装が存在し、JWT/SAML assertion検証、issuer/audience検証、期限切れ、署名不正をfail-closedで拒否するunit testを持つ。
- [ ] `install_trusted_saas_runtime()`が実際の起動経路（`main.py`）から呼ばれ、`resolve_verified_claim_tenant_context()`へ実リクエストが到達する。
- [ ] AC-4の「tenant不明→deny」が、resolver単体testではなく実HTTPリクエスト（ローカルIdPスタブ経由でよい）を通したintegration/e2e testで証明されている。
- [ ] 上記が揃った時点で、saas-multitenant profileの起動拒否を緩める条件を`SAAS-TENANT-01`側で再評価する（本issueでは緩めない）。

## Validation

- ADR受理: `python 01_Plans/issues/validate_active_issue_memos.py`、`python 01_Plans/docs_check.py`
- 実装後: `cd 03_Implement/backend && python -m pytest tests/test_trusted_saas_runtime.py tests/test_verified_tenant_context.py tests/test_tenant_session_precondition.py`
- e2e: 実IdP相当のローカルスタブを用いたHTTPレベルのtenant解決テスト（`ADR-0020`のmock IdP/SP profileが既存の出発点）
