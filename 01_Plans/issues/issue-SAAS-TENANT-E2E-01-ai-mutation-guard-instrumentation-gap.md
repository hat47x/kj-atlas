# Issue Draft: SAAS-TENANT-E2E-01 AI mutation向けtenant session generation guardの機構固有E2E計装が無い

- Type: Process
- Status: Draft
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/e2e/tenant_session_multitab.spec.ts`, `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/src/session/tenant_session_generation.ts`
- Related ADR/Spec: `01_Plans/issues/issue-SAAS-TENANT-01-tenant-context-and-storage-foundation.md`
- Expected verification level: `e2e`

## 課題

`tenant_session_multitab.spec.ts`の6件目のtest（2026-08-06追加、"cross-tab switch discards a delayed AI narrative proposal for the old tenant"）は、多視点の敵対的レビューで「証明している内容が名称・commit messageより弱い」と判明した。

`tenantSwitchUiState.status === "blocked"`になると`App.tsx`（11346-11353行目）は`<TenantSessionBlockedView>`へ即時early-returnし、`NarrativesPanel`を含む`<Shell>`以下を一切renderしない。testの実行順序は、`blockedHeading`の可視性を`releaseDelayedNarrative()`呼び出しの**前**にassertしている——つまり保留中のAI応答が解放される前に、汎用のcross-tab BroadcastChannel通知だけでtabAは既にblocked viewへ遷移済みである。

したがって本testが実際に証明しているのは「narrative生成中でも汎用のtenant切替blocking機構（test 1と同型）は機能する」ことだけであり、「narrative生成に固有の`TenantSessionGenerationGuard.run()`（2026-07-20チェックポイント）が遅延応答を実際に破棄した」ことではない。後者の仕組みが完全に欠落していても、本testは同じ理由（blocked viewがNarrativesPanelをそもそもrenderしない）でpassし続ける。

対比として、既存test 3（`window.__kjTenantBundleZipCancelled`）・test 4（`__kjTenantPackReadFinished`）は、DOM表示に依存しない機構固有の観測点を持ち、汎用blockingとは独立に自分の対象機構が実際に発火したことを証明している。今回追加したAI mutation testにはこの水準の計装が無い。

## 論点（人的判断が必要な理由）

test 3・4の観測点は、production codeが元々持つ低レベルAPI境界（`window.Worker`のpostMessage、`File.prototype.arrayBuffer`）をtest harness側で`addInitScript`により差し替えて実現している。AI mutationには相当するbrowser API境界が無く（`fetch`→React state更新のみ）、同水準の計装をtest harness側だけで実現する方法が自明ではない。選択肢:

(a) production codeに`TenantSessionGenerationGuard.run()`が実際に`StaleTenantSessionResultError`を投げたことを示す、テスト時だけ観測可能なhook（例: `window.__kjTenantGenerationGuardRejected`相当）を追加する。production codeへのtest専用計装追加になるため、既存の「test harnessは production codeを変更しない」という本セッションの一貫した方針からの逸脱を伴う。
(b) `fetch`のresponse解放タイミングと、React state（`narrativeGenerationError`／`lastAiCallOutcome`）の変化を、blocked viewへの遷移とは別の経路で観測する方法を探す（現時点で具体的な実現方法は未検討）。
(c) 現状のtestを「汎用blocking機構がAI mutation中でも機能することの確認」として commit message・checkpoint記述のとおり弱い主張に留め、AI mutation固有経路の実ブラウザ確認は行わない（unit testでの確認に留める）という判断を明示的に下す。

どちらを選ぶかは、テスト計装のためにproduction codeへ手を入れることの是非という価値判断であり、機械的な修正ではない。

## 影響

低リスク。production codeの挙動に影響しない（防御的検証の記述精度の問題）。ただしSAAS-TENANT-01のAcceptance Criteria（AC-8/10/12/13）が要求する「全consumerの越境matrix」の実態を正確に把握するために、この記述精度は重要である。

## Acceptance

- [ ] 上記(a)/(b)/(c)のいずれかを選択する。
- [ ] (a)または(b)を選ぶ場合、AI mutation 7種のうち残り6種（layout、merge、island summary、proposal audit、relation summary、narrative check）にも同水準の計装を展開するか、narrative generationの1種で代表させて十分とするかを判断する。

## Validation

- 選択した対応を実装した場合、「production codeの該当行を削除・無効化してもtestが失敗しなくなる」ことを1回確認する（ミューテーションテスト）ことで、testが実際に対象機構を検証していることを示す。
