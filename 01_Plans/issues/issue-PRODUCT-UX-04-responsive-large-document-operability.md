# Issue Draft: PRODUCT-UX-04 小画面・大規模文書・低速環境での操作性確認

- Type: Feature request
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: TBD
- Scope: `03_Implement/frontend/src/`, `03_Implement/frontend/e2e/`, `04_Documentation/acceptance_check.md`, `04_Documentation/diagnostics.md`
- Related Backlog: `PRODUCT-UX-04`
- Related ADR/Spec: `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`, `01_Plans/issues/issue-QA-MONKEY-06-header-toolbar-responsive-overlap.md`, `01_Plans/issues/issue-UX-OPERABILITY-01-pointer-keyboard-flow-review.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: PRODUCT-UX-04
- RequirementStatement: 製品化対象として、狭い画面、大きな文書、低速環境でも主要操作が見切れず、待機状態と復帰方法が理解できる状態にする。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=標準サンプルと大きめの文書を複数viewportで開く / 操作=検索、選択、表示切替、共有前確認、診断を実行する / 期待結果=見切れ、重なり、反応なしに見える状態、フォーカス迷子がない / 除外=モバイル専用ネイティブUI。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / public-exposure）: SafeMode / share-export
- VerificationLevel（docs-check / unit / integration / e2e）: e2e
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef（未確定時の参照先）: `ADR-0031`

## 1) 課題 / Problem statement

- MVP期の画面はデスクトップ広幅での利用を中心に増築されており、狭い画面や右側パネルの長いラベルで見切れが起きやすい。
- 大きな文書や低速環境では、検索、表示切替、診断、エクスポートの待機状態が分かりにくい可能性がある。
- 製品化では、代表的な画面幅とデータ規模での操作感を品質ゲートに入れる必要がある。

## 2) 背景 / Context

- `QA-MONKEY-06` でヘッダーツールバーのレスポンシブ崩れは修正済み。
- `UX-OPERABILITY-01` の代表確認では、390px / 960px / 1440pxで共有パネル右端見切れは再発していないが、画面構造変更後も継続検証が必要である。
- `ADR-0031` は小画面・大規模文書・低速環境を製品化UIの必須条件とした。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 思考整理の作業中に画面崩れや反応不明が起きると、利用者は内容ではなく操作に注意を奪われる。
- 安全（THREAT_MODEL / SafeMode）: 共有前確認やSafeMode状態が見切れると誤共有のリスクになる。
- 企業・行政要件（enterprise_architecture）: 支給端末、リモート環境、VDIなど画面幅や性能が揺れる環境での利用が想定される。
- 後方互換（schemas）: 表示・パフォーマンス・E2Eの課題であり、データ契約は維持する。

## 4) 提案する解決策 / Proposed solution

- 変更対象:
  - ヘッダー、主要ツールバー、右側パネル、SharePanel、ViewControlsPanel。
  - 大きな文書の検索、表示切替、診断、エクスポートの待機表示。
  - E2E viewport matrix と手動受け入れ確認。
- 変更の最小単位:
  - 390px / 768px / 960px / 1440px の代表幅で主要操作を確認する。
  - 大きめfixtureを用意し、検索・選択・共有前確認の操作時間と待機表示を確認する。
- 非目標:
  - スマートフォン専用アプリ化。
  - リアルタイム共同編集や差分同期の導入。

## 5) 受入条件 / Acceptance criteria

- [ ] 390px、768px、960px、1440pxの代表幅で、主要ボタンとSafeMode状態が見切れない。
- [ ] 右側パネルと共有パネルの長い日本語ラベルが、横スクロール前提にならず読める。
- [ ] 大きな文書で検索、選択、表示切替、共有前確認を行っても、処理中状態や次の操作が分かる。
- [ ] 低速またはbackend待機時に、利用者が保存・再読み込み・診断のどれを行うべきか判断できる。
- [ ] E2EまたはPlaywright scriptで代表viewportと主要操作が記録される。
- [ ] `acceptance_check.md` と `diagnostics.md` が製品化後の確認観点を説明する。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 代表viewportと代表データ規模を定義する。
- [ ] T2 大きめfixtureまたは既存サンプル拡張を用意する。
- [ ] T3 主要パネルのレイアウト崩れ、長いラベル、フォーカス順序を検証する。
- [ ] T4 待機表示、エラー表示、診断導線を確認する。
- [ ] T5 E2Eと公開文書の受け入れ確認を更新する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `cd 03_Implement/frontend && node .\\node_modules\\playwright\\cli.js test e2e/header_toolbar_layout.spec.ts --reporter=line`
  - `cd 03_Implement/frontend && node .\\node_modules\\typescript\\bin\\tsc --noEmit`
  - `rg -n "390|768|960|1440|viewport|大きな文書|低速" 04_Documentation 03_Implement/frontend/e2e`
- 期待結果:
  - 代表viewportと大きめ文書で主要操作が見切れず、待機・エラー・復帰導線が分かる。
- 未実施時の理由・代替検証:
  - 大きめfixture未整備時は、既存fixtureを複製した検証用データで暫定確認する。

## 8) 代替案 / Alternatives considered

- 代替案A: デスクトップ広幅のみを公式サポートにする。公開配布や組織導入の期待と合わない。
- 代替案B: 小画面では機能を大幅に削る。SafeModeや共有前確認など削れない操作があるため、表示優先順位で整理する。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 小画面最適化でデスクトップの作業効率が下がる。
- 影響範囲: frontend layout、E2E、公開文書。
- ロールバック手順: レスポンシブ変更をコンポーネント単位で戻し、代表viewportテストだけを残して再設計する。

## 10) Additional context

- ADR化が必要になる条件: モバイル専用UI、別ルート、キャンバスレンダリング方式の変更を決める場合。

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
