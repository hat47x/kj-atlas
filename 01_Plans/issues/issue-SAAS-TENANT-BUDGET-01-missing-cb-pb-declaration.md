# Issue: SAAS-TENANT-BUDGET-01 SaaSテナント作業に複雑性・性能予算申告がない

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Process
- Status: Done
- Source Issue: N/A
- Priority: P2
- Owner: Maintainer
- Scope: `01_Plans/issues/issue-SAAS-TENANT-01-tenant-context-and-storage-foundation.md`
- Related ADR/Spec: `01_Plans/adr/ADR-0043-complexity-budget-for-cognitive-load.md`, `01_Plans/adr/ADR-0046-responsiveness-performance-budget.md`
- Expected verification level: `docs-check`

## 課題

- 現在の問題: `01_Plans/issues/TEMPLATE.md`の`## 予算申告`節（CB-1..4/PB-1..5の自己申告欄）はコミット`182bf101`（2026-07-16 04:48）で追加され、`issue-SAAS-TENANT-01`はその後（同日16:02、コミット`69f22e28`）に起票された。つまりテンプレートは起票時点で既に予算申告を求めていた。しかし`issue-SAAS-TENANT-01`（347行、2026-07-19時点で30件以上のcheckpointを持つ）には「予算」「CB-」「PB-」のいずれも一度も出現しない — 未記入のプレースホルダーではなく、節そのものが存在しない。
- 利用者または開発への影響: この作業はテナント切替UI（`TenantSessionControl.tsx`、`App.tsx`の`headerRight`内、`data-ui-complexity-tier="core-toolbar"`とタグ付けされた常設ツールバー領域）と、`saas-multitenant`プロファイル下での初回描画前の逐次非同期ゲート（`TenantSessionRuntimeGate` → `TenantSessionBootstrapGate`、`verifyTenantSessionRuntimePolicy`後に`bootstrapTenantSession`）という、まさにCB-1/CB-3（常設UI要素の追加）・PB-2（初回表示予算）が想定する種類の変更を実際に導入している。他の最近の機能（`EXT-AGENT-01`/`EXT-AGENT-02`）は`03_Implement/frontend/src/ui/ux_operability_regression.test.ts`にCB-1適合の理由コメントを残しているが、本作業には同種の申告・コメント・テストが一切ない。

## 対応方針

- 実施したこと: `issue-SAAS-TENANT-01`へ`## 予算申告`を追加した。CB-1/CB-3は検証済みSaaS sessionだけに表示する安全上必要な常設要素`+1`、保留距離不変として許容した。PB-2は逐次2 requestの所要時間が未計測のため要改善とし、AC-12の実ブラウザ検証へ計測と超過時対応を明記した。
- 実施しないこと: 製品挙動・実装の変更、および未計測の初期表示を適合済みとみなすこと。

## 受入条件

- [x] `issue-SAAS-TENANT-01`に予算申告節を追記し、CB-1/CB-3を許容、PB-2を要改善と明記する。
- [x] 製品挙動・実装は変更しない。

## 検証計画

- 実行する確認: `python3 01_Plans/docs_check.py`。
- 期待結果: 予算申告が記録された後も既存の文書契約チェックが通過する。

## Validation

- `python 01_Plans/docs_check.py --root .`
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`

## 補足

- 発見経緯: SaaSテナント対応マージ後の広範な棚卸し（第3ラウンド）で発見。`issue-SAAS-TENANT-01`は執筆時点で他セッションにより活発に編集され続けているため、本issueは独立ファイルとして記録し、当該issueの直接編集は避けた。
