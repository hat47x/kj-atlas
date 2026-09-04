# Issue: DOC-SAAS-E2E-LEDGER-SYNC-01 SaaS E2E台帳を現在の実証境界へ同期する

- Type: Documentation / Planning Integrity
- Status: Done
- Source Issue: `QA-E2E-SAAS-01`
- Priority: P2
- Owner: Maintainer
- Scope: `AUTH-ONE-TIME-JWT-01`, `QA-E2E-SAAS-01`
- Related ADR/Spec: `ADR-0074`, PR #2885, PR #2893
- Expected verification level: `docs-check`

## 課題

SaaS認証・tenant sessionの実証が短期間に進んだ一方、Active/Draft Issueには過去時点の棚卸し結果が残っていた。

- `AUTH-ONE-TIME-JWT-01`は、PR #2885のPostgreSQL複数app testを「存在しない」とする古い是正記録と、`OPS-SAAS-SCALE-01` AC-7が未実装という記録を保持していた。
- `QA-E2E-SAAS-01`は、`tenant_session_multitab.spec.ts`が既に存在する現在も「TenantSession UI E2Eがゼロ」を前提としていた。

いずれもIssueを閉じる根拠にはならない。問題は、完了した証拠と本当に残る縦断E2Eを同じ「未実装」に見せていたことである。

## 対応

- PR #2885/#2893で成立した実PostgreSQL・複数backend appの証拠を`AUTH-ONE-TIME-JWT-01`へ同期した。
- `AUTH-ONE-TIME-JWT-01`の最後の未完境界を、mock Broker → 実frontend → 最低2 backend instanceの一続きのE2Eとして明確化した。
- `QA-E2E-SAAS-01`を、実ブラウザ+mock API / 実PostgreSQL+複数backend app / 実frontendを含む縦断経路の三層で整理し直した。
- `SAAS-TENANT-E2E-01`はAI generation guardの機構固有計装を扱う別責務として維持した。

## 受入条件

- [x] 完了済みのPostgreSQL複数app実証を未実装と記述しない。
- [x] `tenant_session_multitab.spec.ts`の存在と、そのmock API境界を同時に明記する。
- [x] `AUTH-ONE-TIME-JWT-01`を誤ってDoneへせず、縦断E2Eだけを未完として残す。
- [x] `QA-E2E-SAAS-01`と`SAAS-TENANT-E2E-01`の責務を分離する。
- [x] 同じ未完作業を複数Issueの進捗として重複計上しない。
- [x] 自然な日本語として読み直し、古い事実の訂正と現在の未完境界を区別する。

## 完了境界

product/runtime codeやE2E harness自体は変更しない。今回行うのはplanning正本の事実同期であり、実frontendを含む縦断E2Eの実装は別途残る。
