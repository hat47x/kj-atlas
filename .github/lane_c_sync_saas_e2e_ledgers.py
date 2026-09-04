from __future__ import annotations

import re
from pathlib import Path

AUTH = Path("01_Plans/issues/issue-AUTH-ONE-TIME-JWT-01-request-token-supply-contract.md")
QA = Path("01_Plans/issues/issue-QA-E2E-SAAS-01-tenant-session-coverage-gap.md")
DONE = Path("01_Plans/issues/done/issue-DOC-SAAS-E2E-LEDGER-SYNC-01-current-evidence-boundaries.md")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {text.count(old)}")
    return text.replace(old, new, 1)


auth = AUTH.read_text(encoding="utf-8")
auth = replace_once(
    auth,
    "- Related ADR/Spec: `ADR-0064`, `ADR-0074`（Proposed）, `OPS-SAAS-SCALE-01`, `SEC-AUTH-REPLAY-01`",
    "- Related ADR/Spec: `ADR-0064`, `ADR-0074`（Accepted）, `OPS-SAAS-SCALE-01`, `SEC-AUTH-REPLAY-01`",
    "ADR status",
)

auth, count = re.subn(
    r"  \*\*是正\*\*: 本AC調査を委任した指示は`test_saas_auth_session_postgres_multi_instance\.py`がPR #2885で\n"
    r"  着地済みと述べていたが、実際のPR #2885（`2885fdbc`）は無関係な内容（`hil-rs-01`のADR参照正規化）であり、\n"
    r"  該当ファイル名のテストはリポジトリに存在しない。この誤参照は本issueの追跡対象ではないため上記の\n"
    r"  実在するテストで代替確認した。",
    "  **2026-09-04 再同期**: その後mainへ入ったPR #2885では、実PostgreSQLと複数FastAPI appを使うHTTP integration test\n"
    "  `test_saas_auth_session_postgres_multi_instance.py`が実際に追加された。migrationのupgrade / downgrade / re-upgrade、\n"
    "  app間のactive tenant・version共有、別login非干渉、logout・idle expiry・hash key不一致時のfail-closedまで確認している。\n"
    "  したがって、以前の「PR #2885は無関係で該当testも存在しない」という記録は現在のmainには当てはまらない。\n"
    "  本ACは既存の共有DB/CAS/revoke検証で満たした判断を維持しつつ、cluster-levelの追加証拠としてPR #2885を参照する。",
    auth,
    count=1,
)
if count != 1:
    raise RuntimeError(f"AC-5 stale correction: expected one replacement, got {count}")

start = auth.index("- [ ] mock Broker、frontend統合、最低2 backend workerのE2Eで契約を固定する。")
end = auth.index("\n\n## 暫定運用", start)
new_ac8 = """- [ ] mock Broker、frontend統合、最低2 backend workerのE2Eで契約を固定する。
  — 2026-09-04 再同期。**未充足のまま**。周辺の実証は大きく進んだが、このACが要求する縦断経路はまだ1本につながっていない。

  PR #2885では、実PostgreSQLと複数FastAPI appを使ったHTTP integration testにより、migration往復、複数app間のsession共有、
  stale version拒否、別login非干渉、logout・idle expiry・hash key不一致時のfail-closedを確認した。続くPR #2893では、実PostgreSQLを
  切断した状態でもtenant-scoped resource lookupより前に503で停止することと、frontendが409/503を利用者操作なしに自動再送しないことを
  固定し、`OPS-SAAS-SCALE-01`の全ACを完了させた。以前の「OPS-SAAS-SCALE-01 AC-7も未実装」という記録は現在のmainには当てはまらない。

  一方、`03_Implement/frontend/e2e/tenant_session_multitab.spec.ts`は実ブラウザを使うものの、backend APIはPlaywrightの`context.route()`で
  `ServerState`へ差し替えており、実backendやmock Identity Brokerを起動しない。このため、PR #2885/#2893のbackend側実証と既存Playwright
  suiteは相互補完にはなるが、**mock Broker → 実frontend → 共有PostgreSQLを使う最低2 backend instance**という一続きのE2Eにはなっていない。

  残作業はこの縦断経路を1本固定することに限定する。`QA-E2E-SAAS-01`はSaaS UI全体のブラウザE2E台帳、
  `SAAS-TENANT-E2E-01`はAI mutation固有generation guardの観測精度を扱うため、本ACの代替とはしない。逆に、本ACで既に完了した
  PostgreSQL複数app実証を再実装しない。"""
auth = auth[:start] + new_ac8 + auth[end:]

old_temp = """## 暫定運用

本issueと`SAAS-TENANT-SESSION-BINDING-01`の方式決定までは、PostgreSQLが共有するのはprincipal単位versionだけであり、認証session単位のactive tenantを伴う多worker本番運用は未保証とする。JWT replay防御済みとも表明しない。Bearer tokenの保証範囲は短命、署名検証、issuer/audience制限、TLS、browser storage不使用までとする。"""
new_temp = """## 暫定運用

`ADR-0074`のBFF方式と`SAAS-TENANT-SESSION-BINDING-01`、`OPS-SAAS-SCALE-01`の実装・実証は完了している。SaaSのBFF経路では、browserへaccess tokenを渡さず、認証session単位のactive tenantとversionをPostgreSQL正本として複数appから共有する。

ただし本issueの最後のACである「mock Broker → 実frontend → 最低2 backend instance」の縦断E2Eが未完のため、その一続きの経路まで検証済みとは表明しない。また、BFF採用を「Bearer access token自体のreplayを一般に防御した」と言い換えない。互換Bearer経路について表明できる保証は、短命、署名検証、issuer/audience制限、TLS、browser storage不使用の範囲に留める。"""
auth = replace_once(auth, old_temp, new_temp, "temporary operation")
AUTH.write_text(auth, encoding="utf-8")

QA.write_text(
    """# Issue: QA-E2E-SAAS-01 TenantSession UIの実ブラウザ層と実backend縦断層を区別する

- Type: Bug / QA
- Status: Draft
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/e2e/tenant_session_multitab.spec.ts`, SaaS browser / backend integration境界
- Related ADR/Spec: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`, `01_Plans/issues/issue-SAAS-TENANT-01-tenant-context-and-storage-foundation.md`, `01_Plans/issues/issue-AUTH-ONE-TIME-JWT-01-request-token-supply-contract.md`, `01_Plans/issues/issue-SAAS-TENANT-E2E-01-ai-mutation-guard-instrumentation-gap.md`
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

一方、このspecはPlaywrightの`context.route()`で`/api/`を`ServerState`へ差し替えている。browserは実物だが、kj-atlas backend、PostgreSQL、Identity Brokerを同じscenario内では起動しない。ここを、実backendのHTTP integrationまで含めて「SaaS E2E完了」と読み替えてはならない。

## 現在の証拠を三層に分ける

### 1. 実ブラウザ + mock API

`tenant_session_multitab.spec.ts`が担当する。cross-tab、bfcache、export/import、stale mutationなど、browser lifecycleとUIのfail-closed挙動を確認する。

### 2. 実PostgreSQL + 複数backend app

PR #2885の`test_saas_auth_session_postgres_multi_instance.py`とPR #2893のPostgreSQL障害testが担当する。migration往復、複数appからのsession共有、CAS競合、logout/expiry、DB不達時のresource lookup前停止などを確認済みで、`OPS-SAAS-SCALE-01`はDoneとなった。

### 3. 実frontendを含む縦断経路

まだ不足している。特に`AUTH-ONE-TIME-JWT-01`の最後のACが要求する、mock Brokerからloginし、実frontendを操作し、共有PostgreSQLを使う最低2 backend instanceへ到達する一続きのE2Eは未実装である。

## 近接Issueとの責務境界

- `AUTH-ONE-TIME-JWT-01`: Broker → frontend → 複数backend instanceという認証sessionの縦断E2Eを正本として追う。
- `SAAS-TENANT-E2E-01`: delayed AI responseが汎用blocked viewで見えなくなるだけでなく、`TenantSessionGenerationGuard`自体が旧generationを破棄したことを観測できるかという、機構固有のE2E計装を追う。
- 本Issue: SaaS UIのPlaywright被覆を俯瞰し、browser lifecycle / tenant switch / cross-tenant残留の穴を追う。上の2件の専門的な残条件を二重計上しない。

## 対応方針

- 既存`tenant_session_multitab.spec.ts`を「実backendまで含むE2E」と誤認しない。
- `SAAS-TENANT-01`の残ACに応じ、browser lifecycleやconsumer matrixに不足するscenarioだけを本Issueで追加する。
- 認証縦断harnessは`AUTH-ONE-TIME-JWT-01`、AI generation guardの計装判断は`SAAS-TENANT-E2E-01`へ委ねる。
- product codeへテスト専用hookを加えるかどうかは、本Issueでは決めない。

## 受入条件

- [x] Tenant切替を含む実ブラウザPlaywright scenarioが存在する。
- [x] cross-tab / stale mutation / bfcache / export-import系の主要browser lifecycle境界を少なくとも1本ずつ確認する。
- [ ] `SAAS-TENANT-01`の未完consumer matrixを再棚卸しし、本Issueが担うbrowser scenarioの残差を確定する。
- [ ] 実frontendと実backendを結ぶ縦断E2Eの担当Issueを明示し、本Issueの完了時に未検証領域を「E2E済み」と表明しない。
- [ ] 既存specの回帰がない。

## 検証計画

- browser層: `playwright.saas.config.ts`で`tenant_session_multitab.spec.ts`を実行する。
- backend層: PR #2885/#2893で固定したPostgreSQL integrationを維持する。
- 縦断層: `AUTH-ONE-TIME-JWT-01`のACに従い、mock Broker → 実frontend → 最低2 backend instanceの経路を別途固定する。

## 補足

このIssueは「E2Eがゼロ」という古い棚卸し結果を保存するための台帳ではなく、現在も残るbrowser側の被覆差を追う台帳として維持する。実装済みの証拠は正しく完了扱いにし、別Issueが所有する未完条件を重複して進捗化しない。
""",
    encoding="utf-8",
)

DONE.write_text(
    """# Issue: DOC-SAAS-E2E-LEDGER-SYNC-01 SaaS E2E台帳を現在の実証境界へ同期する

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
""",
    encoding="utf-8",
)
