# Issue: SAAS-TENANT-UX-01 getProviderStatusがtenant session generation guard外

- Type: Process
- Status: Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/App.tsx` (line ~1495), `03_Implement/frontend/src/api/client.ts` (`getProviderStatus`)
- Related ADR/Spec: `01_Plans/issues/done/issue-SAAS-TENANT-01-tenant-context-and-storage-foundation.md`
- Expected verification level: `unit`

## 課題

SAAS-TENANT-01のフロントエンド側監査（2026-08-06）で判明: `getProviderStatus()`（`GET /ai/provider-status`）はtenant資源を扱わないため`KJ-Atlas-Tenant-Session-Version`ヘッダーの対象外（正しい判断、`no-tenant-resource`）である一方、`App.tsx:1495`の呼び出しは**tenant session generation guard**（tenant切替時に古いresponseのcommitを防ぐ仕組み）の外にある唯一のclient呼び出しである。

これにより、tenant切替の最中またはその直後にprovider-status応答が遅延到着した場合、古いgenerationからの応答でも`setProviderKind`が呼ばれる。provider種別（none/local/large-scale等）はtenant固有の秘匿情報ではなく表示専用の設定echoだが、切替直後に旧tenantのprovider表示が一瞬残る可能性がある。

## 論点（人的判断が必要な理由）

- 現状のまま（generation guard外）で問題ない、という判断も成立する: provider-statusはグローバルなruntime設定であり、tenant固有ではない可能性が高い（要確認）。その場合、generation guardの対象外であることは意図的な設計として正しい。
- 一方、将来providerがtenant単位で設定可能になった場合（現時点ではそうなっていない）、この境界は見直しが必要になる。
- 「意図的に対象外」なのか「単に見落とされていた」のかは、この監査だけでは判別できない。

## 影響

低リスク（表示のみ、秘匿情報の漏えいではない）。ただし本項目は「意識的な決定」として記録されるべきで、暗黙のままにしない。

## Acceptance

- [x] provider-statusがtenant単位の設定になり得るか（現在および将来計画）を確認する。→ 確認済み（下記実装記録）。現状不可能・将来計画も無し。
- [x] tenant単位になり得ないなら、`getProviderStatus`をgeneration guard対象外とする理由をコードコメントまたはissueへ明記して完了とする。→ `App.tsx`へコメント追記済み。
- [x] tenant単位になり得るなら、他のtenant資源呼び出しと同様generation guardへ組み込む。→ 上記の確認結果により非該当（現状不可能・将来計画も無し。conditional branchが成立しないため完了扱い）。

## Validation

- 判断内容をコードコメントまたは本issueへ記録し、`test_tenant_session_precondition`系の網羅性テストの exemption 理由と整合させる。→ 整合確認済み（下記実装記録）。

## 実装記録（2026-08-06）

- `getProviderStatus()`の実体（`GET /ai/provider-status`、`routes/ai.py:496`）を確認した。`def get_provider_status() -> ProviderStatusResponse:`はrequest・db・tenant等のパラメータを一切受け取らず、`get_provider().provider_kind`（プロセス全体で単一の`Settings`インスタンスから解決されるグローバルなprovider設定）をそのまま返すだけである。
- `settings.py`全体に`tenant`という語は一切出現しない（grep確認）。つまり`Settings`（および`get_provider()`が読む設定）はアーキテクチャ上tenant非依存であり、現状「tenant単位のprovider設定」という概念自体が存在しない。
- frontend側`client.ts:429`の`getProviderStatus(): Promise<ProviderKind>`も、他のtenant-scoped関数と異なり`TenantScopedRequestOptions`（`tenantSessionContext`を含む）を一切受け取らない引数無しの関数であり、generation guardへ接続する経路がそもそも型として存在しない。
- 将来計画の確認: `GENAI-GOV-01`のLane B（LLMProvider経路）を含め、本セッションで確認した生成AI関連の計画文書のいずれにも「providerをtenant単位で設定可能にする」という記載は無い。
- `client.test.ts:220`の既存exemption table（`"GET /ai/provider-status": NO_TENANT_RESOURCE`）は既にこの経路を`no-tenant-resource`として正しく分類しており、本issueの確認結果と整合している。テスト側の変更は不要。
- 対応: `App.tsx`の該当`useEffect`（`getProviderStatus()`呼び出しの直前）へ、上記確認結果に基づくコメントを追記した。「見落とし」ではなく「確認済みの意図的な設計」であることを将来の読者へ明示する。
- 検証: `npx tsc --noEmit`、既存のprovider-status関連テストに変更無し（テストファイル自体を変更していないため回帰リスクは無い）。
