# Issue: SAAS-TENANT-E2E-01 AI mutation向けtenant session generation guardの機構固有E2E計装が無い

- Type: Process
- Status: Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/e2e/tenant_session_multitab.spec.ts`, `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/src/session/tenant_session_generation.ts`
- Related ADR/Spec: `01_Plans/issues/done/issue-SAAS-TENANT-01-tenant-context-and-storage-foundation.md`
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

- [x] 選択肢(b)に相当するtest-harness-only観測を採用する。PR #2917でPlaywright page側から `StaleTenantSessionResultError` の生成を直接観測し、production codeへtest専用hookを追加せず機構固有E2Eを成立させた。
- [x] narrative generation 1種をshared `TenantSessionGenerationGuard` の機構代表とする。残り6種へ同一probeを複製せず、各tenant-scoped callが共通guard境界を通ることは既存のfail-closed frontend call-site/session-header契約で担保する。これは各AI機能の業務意味や全越境matrixの完了を主張するものではない。

## Validation

- PR #2917（merge `3d6ed603a4cd9d19aed5287525dc544602367f23`）でreal Chromium SaaS baseline 8/8とprobe付きmatrix 8/8が成功した。
- tenant switch前とblocked直後はprobe count=0、遅延AI narrative response解放後にcount=1となることを固定し、generic blocked viewだけでは満たせないassertへ分離した。
- mutation proofとして `TenantSessionGenerationGuard.run()` のstale throwを一時無効化すると、対象scenarioが `generation guard must reject the stale AI result` で失敗することを確認した。production source復元後のbuildも成功した。
- probeはPlaywright harness内で `Error.prototype.name` を観測するため、production code/API/schemaへtest専用surfaceを追加していない。

## 完了判断（2026-09-05）

- 元Issueの欠落は「汎用blocked viewとは独立にgeneration guard固有の発火を観測できない」ことであり、PR #2917のprobe＋mutation proofで解消した。
- shared guardそのものの判別力を1つの実ブラウザ経路で固定できたため、同一機構の確認だけを目的として7種類すべてへprobeを複製する必要はない。route/call-siteのguard包含は既存のfail-closed contract testに委ねる。
- `SAAS-TENANT-01` のAC-10は別責務であり、API/MCP/worker/browser cacheを含むsame-docId越境negative matrix全体が未完のため、親Issueは引き続きactiveとする。
