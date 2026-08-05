# Issue Draft: SAAS-TENANT-UX-01 getProviderStatusがtenant session generation guard外

- Type: Process
- Status: Draft
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/App.tsx` (line ~1495), `03_Implement/frontend/src/api/client.ts` (`getProviderStatus`)
- Related ADR/Spec: `01_Plans/issues/issue-SAAS-TENANT-01-tenant-context-and-storage-foundation.md`
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

- [ ] provider-statusがtenant単位の設定になり得るか（現在および将来計画）を確認する。
- [ ] tenant単位になり得ないなら、`getProviderStatus`をgeneration guard対象外とする理由をコードコメントまたはissueへ明記して完了とする。
- [ ] tenant単位になり得るなら、他のtenant資源呼び出しと同様generation guardへ組み込む。

## Validation

- 判断内容をコードコメントまたは本issueへ記録し、`test_tenant_session_precondition`系の網羅性テストの exemption 理由と整合させる。
