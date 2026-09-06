# Issue: PGM-ITER-05-03 組織IdP外ゲスト受入プリミティブの要求確定

- Type: Design / Security
- Status: Open
- Source Issue: `02_Architecture/post-mvp-business-scope-design-program.html` §18（Maintainer直接指示、2026-08-25）, `01_Plans/issues/done/issue-PGM-ITER-05-02-cross-tenant-sharing-external-comparison.md`（外部比較調査）
- Priority: P2
- Owner: Maintainer
- Scope: `01_Plans/adr/`, `03_Implement/backend/src/kj_atlas_api/guest_admission_models.py`, `03_Implement/backend/src/kj_atlas_api/guest_admission_repository.py`, `03_Implement/backend/src/kj_atlas_api/tenant_db_guard.py`, `03_Implement/backend/src/kj_atlas_api/trusted_auth_edge.py`
- Related ADR/Spec: `01_Plans/adr/ADR-0059-saas-tenant-authorization-boundary.md`, `01_Plans/adr/ADR-0067-three-element-constraint-design-method.md`, `01_Plans/adr/ADR-0080-idp-independent-guest-admission-primitive.md`, `02_Architecture/cross-tenant-sharing-external-comparison-2026-08-25.html`
- Expected verification level: `integration`

## 課題

`issue-PGM-ITER-05-02`（組織境界を越えた共有パターンの外部比較調査）完了の直後、Maintainerから実運用フィードバックを待たずに直接、次の4要求が確定要求として示された（`post-mvp-business-scope-design-program.html` §18）。

1. 組織間だけでなく、小規模の**個人間**利用もサポートする。
2. 行政・企業等が、市民や外部協力者のような**受入先テナント自身の企業IdPに属さないユーザー**を受け入れられる。— **2026-08-26補正**: 「受入先テナント自身のIdPは不要」という意味であり、「ゲスト自身がいかなるIdPも持たない」ことまでは求めない。ゲスト自身の所属組織のIdP、または汎用個人アカウント（Google/Microsoft/GitHub等）を持つことは前提としてよい。
3. 組織IdP外ユーザーの受付可否を、**テナント全体より詳細な単位**で制御できる。
4. **既定は拒否**。既定の共有対象ドキュメントは**0件**。

現行の`resolve_verified_claim_tenant_context()`（`tenant_context.py`）は`tenant_identity_providers`が(tenant, IdP)単位でactiveであることだけを要求する、単一の粗い信頼プリミティブしか持たない。要求2は既存の三要素分析（§15.1・§15.2）の射程を超える——これまでの分析は「別テナントのIdP全体を信頼する」プリミティブ（`tenant_identity_providers`の粒度を細かくする方向）を前提にしていたが、要求2（補正後）が求めるのは**受入先テナント自身のIdPとは独立に、ゲスト個人単位で信頼を表現できるプリミティブ**である。

## 対応方針

- 実施すること:
  1. 上記4要求を確定した受入条件として本issueに固定する（既に確定済みであり、再検討の対象ではない）。
  2. `AGENTS.md` §1.1（三要素牽制設計法、`ADR-0067`）に従い、業務設計・データ設計・機能設計の三次元から、受入先テナント自身のIdPとは独立した個人単位の招待・許可プリミティブを分析する。着工前チェックリスト（`02_Architecture/three-element-constraint-checklist.html`）を通す。
  3. 三要素分析の結果を新規ADRとして起票し、Maintainerの承認（Accepted）を経てから実装に着手する。
- 実施しないこと:
  1. 三要素分析・ADR化を経ないプリミティブの実装。
  2. 4要求自体の再検討・縮小（Maintainerが確定要求として直接指示したものであり、本issueの論点は「どう実現するか」であって「実現するかどうか」ではない）。

## 論点（三要素分析で扱うべき問い）

- **個人単位の信頼レコードの形**: `tenant_identity_providers`のような(tenant, IdP)単位ではなく、個人identity本体と対象ドキュメントへのgrantを分離する必要がある。`ADR-0080`は`guest_principals`＋`guest_document_grants`を採択した。
- **ゲスト本人確認方法**: 受入先テナント自身の企業IdPは要求しない一方、ゲスト自身は所属組織IdPまたは汎用個人アカウントを利用する。`ADR-0080`はA1/A2の多方式対応を採択し、認証結果をserver-owned sessionへ交換する境界を要求する。
- **既定拒否・既定ゼロ件の実装位置**: guest principalの存在だけでは文書アクセスを一切導出せず、`guest_document_grants`のexact matchがある場合のみ許可する。tenant-wide fallbackは設けない。
- **取り消し・失効**: リソース側テナントがguest principalまたは個別grantを相手側状態と無関係に単独でrevokeでき、次の認可判定から反映されることを要求する。

## 実装進捗

### R1: 永続化・認可プリミティブ（2026-09-06）

`lane-c/guest-admission-primitive-r1-20260906`で、`ADR-0080` D2/D3/D4の下層primitiveを実装した。

- `guest_principals`と`guest_document_grants`を独立tableとして追加し、guestを`TenantMembershipRow`へ混在させない。
- `(tenant_id, invited_email)`のdedup、安定した`guest_principal_id`、verified issuer/subjectの一意性、principal/grantのtenant複合FK、documentのtenant複合FKをDDL/ORM双方で固定した。
- principal作成、redeem、exact document grant、grant revoke、principal revoke、`guest_can_read_document()`をrepository primitiveとして追加した。
- pending principalはgrantがあってもdeny、active後もexact grant以外はdeny、grant/principal revoke後は次のauthorization predicateからdenyする。
- guest repositoryは通常member用`TenantContext`を捏造せず、内部tenant-id DB guardを使う。PostgreSQLでは両guest tableを`ENABLE/FORCE ROW LEVEL SECURITY`とし、tenant context未設定・別tenant accessをfail closedにした。
- guest modelは中央`PERSISTENT_TEXT_SPECS`とAlembic `target_metadata`へ正式登録し、専用moduleだけautogenerate/portable persistence governanceから抜ける状態を防止した。
- verification run `34036961877`と最終governance run `34037370856`で、Ruff、focused pytest、PostgreSQL 16 restricted runtime roleによるRLS、migration lineage、persistence shape、diff hygieneを確認した。

R1は**外部IdP/OAuthからguest identityを検証してserver-owned sessionへ交換し、HTTP requestのdocument read/writeへ接続するtrusted-auth-edge経路までは実装しない**。そのためAC-3/AC-4はこの時点では完了扱いにしない。

### R2に残す境界

- `ADR-0080` D1=A1/A2に従うguest identity verification（home organization IdP / general personal account）。
- verified `(issuer, subject)`を、招待済み`guest_principal_id`へ安全にbindするredeem境界。
- member用`VerifiedTenantClaim` / `tenant_identity_providers`経路と構造的に混線しないguest auth/session境界。
- server-owned guest sessionからexact document grantを評価し、実HTTP requestでdefault zero / revoke immediateを固定するintegration test。
- SafeModeその他のdocument response制約は通常利用者と同じ既存境界を通し、本issueで別の抜け道を作らない。

## 受入条件

- [x] AC-1: 上記4要求への対応方針が三要素分析（`ADR-0067`）で決定され、着工前チェックリストを通過する。— 2026-08-25、`ADR-0080`とこのADRを反映した`post-mvp-business-scope-design-program.html` §19、`three-element-constraint-checklist.html`の適用記録を参照。D1（ゲスト本人確認）・D2（信頼レコードの形）・D3（既定拒否・既定ゼロ件の保証層）・D4（取り消しの独立性）の4論点を、基本チェック・クロスチェックを通した三要素分析として決定した。2026-08-26、保守者の指示によりD1（単一方式→多方式対応）・要求2の文言・D2（関数従属性再検査による`guest_principals`への精緻化）を補正した。
- [x] AC-2: 決定内容が新規ADRとして起票され、Maintainerの承認（Accepted）を得る。— 2026-08-26、`ADR-0080`がAcceptedとなった（D1=多方式対応、D2=A、D3=A、D4=A）。
- [ ] AC-3: ADR承認後、個人単位・IdP不問の招待・許可プリミティブが実装され、既定拒否・既定ゼロ件がintegration testで固定される。— 2026-09-06 R1で永続化・repository・RLSのdefault-zero/exact-grant primitiveまでは実装・integration test固定済み。残りはD1のverified guest identity→server-owned session→実HTTP document authorization接続（R2）。
- [ ] AC-4: 招待の取り消し・失効が、相手側（招待された個人の状態）と無関係にテナント側から単独で実行できることがtestで固定される。— 2026-09-06 R1でgrant/principal revokeと次のrepository authorization predicateでの即時denyまでは固定済み。残りはR2の実HTTP/session経路で、既発行sessionを含むrequest境界の挙動を固定すること。

## 検証

- `python 01_Plans/docs_check.py`
- `cd 03_Implement/backend && python -m ruff check ...`
- `cd 03_Implement/backend && python -m pytest -q tests/test_guest_admission_repository.py tests/test_guest_admission_postgres_rls.py tests/test_tenant_db_guard.py tests/test_alembic_lineage.py tests/test_persistence_shapes.py tests/test_database_support.py`
- PostgreSQL 16 restricted runtime roleでguest tableの`ENABLE/FORCE RLS`、contextなし0件、別tenant不可視・write拒否、transaction-local tenant scopeを確認
- R1 verification: GitHub Actions run `34036961877`, governance re-verification run `34037370856`
