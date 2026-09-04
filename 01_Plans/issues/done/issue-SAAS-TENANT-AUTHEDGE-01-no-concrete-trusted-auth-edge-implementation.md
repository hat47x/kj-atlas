# Issue Draft: SAAS-TENANT-AUTHEDGE-01 実trusted auth edgeが未着手のまま7件のACを塞いでいる

- Type: Feature request / Security boundary
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/auth_context.py`, `03_Implement/backend/src/kj_atlas_api/trusted_saas_runtime.py`, `03_Implement/backend/src/kj_atlas_api/tenant_context.py`, `03_Implement/backend/src/kj_atlas_api/main.py`, `03_Implement/backend/src/kj_atlas_api/settings.py`
- Related Backlog: `SAAS-TENANT-01`
- Related ADR/Spec: `01_Plans/issues/issue-SAAS-TENANT-01-tenant-context-and-storage-foundation.md`, `01_Plans/adr/ADR-0059-saas-tenant-authorization-boundary.md`, `01_Plans/adr/ADR-0020-oidc-saml-mock-idp-sp-profile.md`, `01_Plans/adr/ADR-0063-saas-multitenant-trusted-auth-edge.md`
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

> 2026-08-08: ADR-0063 が Accepted となり、D9-1〜D9-8 の全ステップが実装された。

- [x] ADR-0063 が Accepted。プロトコル範囲（OIDC/JWT only, SAML は broker で吸収）、PyJWT + cryptography、JWKS キャッシュ・ローテーション、IdP 到達不能時の fail-closed（D6）。
- [x] `SaasIdentityContextResolver` の具象実装 `JwtSaasIdentityContextResolver`（`trusted_auth_edge.py`）が、RS256/ES256 JWT 検証、issuer/audience 検証、期限切れ、署名不正を fail-closed で拒否。unit test 完備（`test_trusted_auth_edge.py`: 9 tests）。
- [x] `install_trusted_saas_runtime()` が `main.py` module scope から呼ばれ、`ClaimBasedTenantContextResolver` → `resolve_verified_claim_tenant_context()` へ実リクエストが到達する。`InMemoryActiveTenantSessionPersister` が実装済み。
- [x] AC-4「tenant不明→deny」が HTTP レベル E2E test（`test_saas_e2e_tenant_isolation.py`: 10 tests）で証明済み。AC-8（tenantId 伝播）、AC-10（越境 negative matrix）も同ファイルでカバー。
- [x] saas-multitenant profile の起動拒否を緩める条件を `SAAS-TENANT-01` 側で再評価した。本 issue では緩めず、親issueの後続checkpointでも実auth edge以外の未充足ゲートを理由に起動拒否を維持している。`settings.py` の無条件 `ValueError` は削除済みで、`TrustedSaasRuntimePolicy.validate()` と lifespan preflight が必須設定の完備を検証する。

## Validation

- ADR受理: `python 01_Plans/issues/validate_active_issue_memos.py`、`python 01_Plans/docs_check.py`
- 実装後: `cd 03_Implement/backend && python -m pytest tests/test_trusted_saas_runtime.py tests/test_verified_tenant_context.py tests/test_tenant_session_precondition.py tests/test_trusted_auth_edge.py tests/test_jwks_store.py tests/test_claim_tenant_resolver.py tests/test_active_tenant_session_persister.py tests/test_saas_e2e_tenant_isolation.py`
- e2e: `test_saas_e2e_tenant_isolation.py` が実 RS256 署名 JWT を用いた HTTP レベルの tenant 解決テストを実装済み

## 完了整理（2026-09-04）

- 2026-08-08の記録どおり、ADR-0063受理、`JwtSaasIdentityContextResolver`、trusted runtime配線、HTTP-level tenant isolation E2Eまで本issue固有の実装は完了している。
- 唯一未チェックだった項目は「SaaS起動拒否の解除」ではなく、親`SAAS-TENANT-01`で解除条件を再評価することだった。親issueは後続checkpointでこの判断を繰り返し更新し、auth edge以外の未充足ゲートが残るため起動拒否を維持している。
- したがって残存作業は親issueおよび個別follow-upの所管であり、本issueをDraftのままactive triageへ残す根拠にはならない。
