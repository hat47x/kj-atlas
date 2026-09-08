# Issue: FE-CONTRACT-REGRESSION-01 fresh npm suiteで露出したfrontend transport/mergeMethod契約ドリフト

- Type: QA
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/api/client.test.ts`, `03_Implement/frontend/src/admin/model_allowlist_api.ts`, `03_Implement/frontend/src/ui/MergeSuggestionsPanel.tsx`
- Related ADR/Spec: N/A
- Expected verification level: frontend unit + build + planning checks

## 課題

2026-09-05、`DX-CI-PNPM-01` / `DX-ENV-01` のstale性をfresh checkout + `npm ci` で検証したところ、pnpm混在とは無関係なfrontend full unit suiteの失敗を3件検出した。

1. `src/api/client.test.ts` の静的transport inventoryが、PR #2898で意図的に導入された独立control-plane consoleの `admin/model_allowlist_api.ts` を未分類のbackend fetchとして拒否した。
2. `MergeSuggestionsPanel.merge_method.test.ts` の2件が、`mergeMethod` の日本語/英語表示消失を検出した。`merge_method_label.ts` と固定テストは残っていたが、panel側のimport・locale解決・表示行が失われていた。

## 判断

### Admin transport

PR #2898は `admin.html` を主キャンバスから分離し、business-plane credentialへcontrol-plane権限を広げない独立consoleとして実装している。そのためadmin requestを `api/client.ts` へ無条件に吸収するのではなく、静的inventoryへ **明示的なreviewed transport** として登録する。

同時に、admin transportのfetchが以下を満たすことを静的に固定する。

- `${API_BASE}/admin/provision/models/tenants/...` 名前空間に限定される。
- `credentials: "same-origin"` を維持する。
- business-planeの `tenantSessionPreconditionHeaders` を暗黙に流用しない。

### mergeMethod表示

`mergeMethod` はbackend contract・frontend parser・label helper・既存regression testで保持されている。表示assertionを削るのではなく、`0f693a...` で固定されていた方式表示を現行partial-accept UIへ復元する。

## Acceptance

- [x] admin control-plane transportがstatic fetch inventoryで未分類にならず、admin provisioning namespace / same-origin境界を検証される。
- [x] `MergeSuggestionsPanel` が `near_duplicate` / `kernel_fusion` をrationaleとは別フィールドとして日本語・英語で再表示する。
- [x] fresh `npm ci` 後のfrontend full unit suiteがpassする。
- [x] frontend production buildがpassする。
- [x] planning lifecycle / docs / triage / stale reintroduction / diff checksがpassする。

## 境界

- admin consoleをbusiness-planeのtenant-session clientへ統合しない。
- `mergeMethod` のbackend/API/schema値は変更しない。
- `DX-CI-TEST-01` のrepo外fixture依存問題は別Issueとしてactiveのまま扱う。
- pnpm/npmローカル混在の整理は、本回帰修復の成功後に別PRで再検証して閉じる。
