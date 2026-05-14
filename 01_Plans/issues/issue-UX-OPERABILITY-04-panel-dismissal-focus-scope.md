# Issue Draft: UX-OPERABILITY-04 表示/共有パネルをキーボードで自然に閉じられない

- Type: Bug
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: TBD
- Scope: `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/src/ui/SharePanel.tsx`, `03_Implement/frontend/e2e/`
- Related Backlog: `UX-OPERABILITY-04`
- Related ADR/Spec: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`, `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`, `04_Documentation/acceptance_check.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: UX-OPERABILITY-04
- RequirementStatement: 一時的に開く表示/共有パネルは、キーボードだけで開閉でき、閉じた後に起点へ自然に戻れる。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=標準サンプル `doc_phase1_canvas` を開く / 操作=キーボードで `表示` または `共有と再現` を開き、`Escape` または明示的な閉じる操作で閉じる / 期待結果=パネルが閉じ、フォーカスが起点ボタンまたは次の自然な操作へ戻る / 除外=ブラウザ標準ファイルピッカーの挙動。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: share-export
- VerificationLevel（docs-check / unit / integration / e2e）: e2e
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef（未確定時の参照先）: `ADR-0030`

## 1) 課題 / Problem statement

- `表示` と `共有と再現` はキーボード操作で開けるが、2026-05-14 の検証では `Escape` を押しても閉じなかった。
- 共有パネルは縦に長く、内部スクロール自体は機能するが、キーボード利用者が閉じるには長いフォーカス順序を戻るか、起点ボタンへ再到達する必要がある。
- `共有と再現` は SafeMode / export / review pack を含む安全境界なので、開閉とフォーカス復帰が曖昧だと誤操作や確認漏れにつながる。

## 2) 背景 / Context

- `QA-MONKEY-06` によりヘッダーのレスポンシブ重なりは改善済み。
- `SharePanel` の横見切れは修正済みで、今回の検証でも `390px` と `960px` で右端見切れは再発しなかった。
- 残る課題は、開いた後にキーボードで安全に閉じる操作とフォーカススコープの設計である。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 操作を試して戻れることは、視点制御と探索の基本である。
- 安全（THREAT_MODEL / SafeMode）: share/export パネルは安全確認の場であり、キーボードでも閉じる/戻る導線が必要。
- 企業・行政要件（enterprise_architecture）: キーボード操作、フォーカス復帰、閉じる操作はアクセシビリティ要件に近い。
- 後方互換（schemas）: UI操作モデルの改善であり、データ契約は変更しない。

## 4) 提案する解決策 / Proposed solution

- 変更対象:
  - `表示` と `共有と再現` の一時パネルに `Escape` close を追加する。
  - 明示的な「閉じる」ボタンをパネル先頭に置く。
  - パネルを閉じた後、起点ボタンへフォーカスを戻す。
  - 可能であれば、開いているパネル内のTabスコープまたは先頭/末尾の戻り導線を整える。
- 変更の最小単位:
  - まず `Escape` close とフォーカス復帰を `表示` / `共有と再現` の2パネルで固定する。
- 非目標:
  - すべてのサブパネルを完全なモーダルダイアログへ変更すること。
  - ファイル選択ダイアログ内部の挙動を制御すること。

## 5) 受入条件 / Acceptance criteria

- [ ] キーボードで `表示` を開き、`Escape` で閉じられる。
- [ ] キーボードで `共有と再現` を開き、`Escape` で閉じられる。
- [ ] 閉じた後、フォーカスが起点ボタンへ戻る。
- [ ] パネル先頭に明示的な閉じる操作があり、スクリーンリーダー向け名前を持つ。
- [ ] 共有パネル内の縦スクロールと右端見切れ対策は維持される。
- [ ] Playwrightで開く、閉じる、フォーカス復帰を検証する。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 現在のパネル開閉状態管理とフォーカス保持箇所を確認する。
- [ ] T2 `Escape` close と起点フォーカス復帰を実装する。
- [ ] T3 パネル先頭に閉じるボタンを追加する。
- [ ] T4 390px / 960px / 1280px の viewport で見切れが再発しないことを確認する。
- [ ] T5 Playwright E2Eを追加する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `cd 03_Implement/frontend && node .\\node_modules\\typescript\\bin\\tsc --noEmit`
  - `cd 03_Implement/frontend && node .\\node_modules\\vitest\\vitest.mjs run src/ui/SharePanel.test.ts src/ui/i18n_equivalence.integration.test.ts`
  - `cd 03_Implement/frontend && node .\\node_modules\\playwright\\cli.js test <new-panel-focus-spec> --reporter=line`
- 期待結果:
  - `Escape` でパネルが閉じ、起点ボタンへフォーカスが戻る。
- 未実施時の理由・代替検証:
  - 自動E2E追加前は、Playwright script で `viewStillOpen=false` / `shareStillOpen=false` と activeElement を確認する。

## 8) 代替案 / Alternatives considered

- 代替案A: 起点ボタンをもう一度押す操作だけを閉じる方法とする。長いパネル内から戻りにくいため、キーボード利用者には不十分。
- 代替案B: パネル外クリックだけで閉じる。マウス前提になり、キーボード操作の問題を解決しない。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: `Escape` がテキスト入力やファイル選択のキャンセルと競合する。
- 影響範囲: 表示パネル、共有パネル、SafeMode/export確認、E2E。
- ロールバック手順: `Escape` handler と閉じるボタン追加を戻し、既存のトグル開閉へ戻す。

## 10) Additional context

- 2026-05-14 検証:
  - Edge Chromium（Chrome代替） / `http://127.0.0.1:5173/?locale=ja`
  - viewport `960x720` で `表示` を開き `Escape` を押しても `視点プリセット` が残った。
  - viewport `960x720` で `共有と再現` を開き `Escape` を押しても `1) パッケージをエクスポート` が残った。
  - viewport `390x844` と `960x720` で共有パネルの右端見切れは検出なし。縦方向は内部スクロールで表示される。

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
