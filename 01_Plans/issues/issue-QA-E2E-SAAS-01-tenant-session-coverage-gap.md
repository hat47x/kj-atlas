# Issue: QA-E2E-SAAS-01 TenantSession UIの実ブラウザ層と実backend縦断層を区別する

- Type: Bug / QA
- Status: Draft
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/e2e/tenant_session_multitab.spec.ts`, SaaS browser / backend integration境界
- Related ADR/Spec: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`, `01_Plans/issues/issue-SAAS-TENANT-01-tenant-context-and-storage-foundation.md`, `01_Plans/issues/done/issue-AUTH-ONE-TIME-JWT-01-request-token-supply-contract.md`, `01_Plans/issues/issue-SAAS-TENANT-E2E-01-ai-mutation-guard-instrumentation-gap.md`
- Expected verification level: `e2e`

## 課題

このIssueを起票した時点では、TenantSession UIを扱うPlaywright E2Eが存在せず、「E2Eカバレッジがゼロ」と整理していた。その前提は現在のmainでは成立しない。

`03_Implement/frontend/e2e/tenant_session_multitab.spec.ts`には、実ブラウザ上で次の境界を確認するSaaS向けscenarioが既にある。

- 別tabでtenantを切り替えた後、旧tabのDOMをblocked viewへ移し、遅延した旧tenant結果を表示しない。
- `BroadcastChannel`が使えない場合でも、staleなPUTを409で止め、自動再送や別tenantへのmutationを行わない。
- tenant切替時に旧tenantのbundle exportをcancelする。
- 読込途中のreview packが旧tenant文脈で完了しても採用しない。
- 390px・日本語・bfcache復元でも旧tenant内容を表示せず、回復状態へfocusする。
- AI narrative生成中のtenant切替でも、旧tenantのproposalを画面へ出さない。

したがって「TenantSession UIのブラウザE2Eが存在しない」こと自体は解消している。

一方、このspecはPlaywrightの`context.route()`で`/api/`を`ServerState`へ差し替えている。browserは実物だが、kj-atlas backend、PostgreSQL、Identity Brokerを同じscenario内では起動しない。このspec単体を、実backendのHTTP integrationまで含めた「SaaS E2E完了」と読み替えてはならない。

## 現在の証拠を三層に分ける

### 1. 実ブラウザ + mock API

`tenant_session_multitab.spec.ts`が担当する。cross-tab、bfcache、export/import、stale mutationなど、browser lifecycleとUIのfail-closed挙動を確認する。

### 2. 実PostgreSQL + 複数backend app

PR #2885の`test_saas_auth_session_postgres_multi_instance.py`とPR #2893のPostgreSQL障害testが担当する。migration往復、複数appからのsession共有、CAS競合、logout/expiry、DB不達時のresource lookup前停止などを確認済みで、`OPS-SAAS-SCALE-01`はDoneとなった。

### 3. 実frontendを含む認証縦断経路

`AUTH-ONE-TIME-JWT-01`で完了した。`saas_auth_browser_multi_instance.spec.ts`により、mock Brokerからloginし、実Vite frontendを経由し、共有PostgreSQLを使う2つの実backend worker間で認証sessionを引き継ぐ一続きの経路を固定した。この証拠は認証session境界の正本であり、本Issueでは同じharnessを二重実装しない。

## 近接Issueとの責務境界

- `AUTH-ONE-TIME-JWT-01`: Broker → frontend → 複数backend instanceという認証sessionの縦断E2Eを正本として完了した。
- `SAAS-TENANT-E2E-01`: delayed AI responseが汎用blocked viewで見えなくなるだけでなく、`TenantSessionGenerationGuard`自体が旧generationを破棄したことを観測できるかという、機構固有のE2E計装を追う。
- 本Issue: SaaS UIのPlaywright被覆を俯瞰し、browser lifecycle / tenant switch / cross-tenant残留の穴を追う。上の2件の専門的な条件を二重計上しない。

## 対応方針

- 既存`tenant_session_multitab.spec.ts`を「実backendまで含むE2E」と誤認しない。
- `SAAS-TENANT-01`の残ACに応じ、browser lifecycleやconsumer matrixに不足するscenarioだけを本Issueで追加する。
- 認証縦断harnessはDoneとなった`AUTH-ONE-TIME-JWT-01`を証拠として参照し、AI generation guardの計装判断は`SAAS-TENANT-E2E-01`へ委ねる。
- product codeへテスト専用hookを加えるかどうかは、本Issueでは決めない。

## 受入条件

- [x] Tenant切替を含む実ブラウザPlaywright scenarioが存在する。
- [x] cross-tab / stale mutation / bfcache / export-import系の主要browser lifecycle境界を少なくとも1本ずつ確認する。
- [ ] `SAAS-TENANT-01`の未完consumer matrixを再棚卸しし、本Issueが担うbrowser scenarioの残差を確定する。
- [x] 実frontendと実backendを結ぶ縦断E2Eの担当Issueを`AUTH-ONE-TIME-JWT-01`として明示し、本Issue側で同じ認証harnessを重複実装しない。
- [ ] 既存specの回帰がない。

## 検証計画

- browser層: `playwright.saas.config.ts`で`tenant_session_multitab.spec.ts`を実行する。
- backend層: PR #2885/#2893で固定したPostgreSQL integrationを維持する。
- 認証縦断層: Doneとなった`AUTH-ONE-TIME-JWT-01`の`saas_auth_browser_multi_instance.spec.ts`を正本として維持する。

## 補足

このIssueは「E2Eがゼロ」という古い棚卸し結果を保存するための台帳ではなく、現在も残るbrowser側の被覆差を追う台帳として維持する。実装済みの証拠は正しく完了扱いにし、別Issueが所有する条件を重複して進捗化しない。
