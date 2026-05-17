# Issue Draft: PRODUCT-UX-03 共有・エクスポート・レビューパック導線の製品化

- Type: Feature request
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: TBD
- Scope: `03_Implement/frontend/src/ui/SharePanel.tsx`, `03_Implement/frontend/src/i18n/`, `04_Documentation/data_handling.md`, `04_Documentation/security.md`, `04_Documentation/acceptance_check.md`
- Related Backlog: `PRODUCT-UX-03`
- Related ADR/Spec: `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`, `01_Plans/issues/issue-QA-MONKEY-01-safemode-export-boundary.md`, `01_Plans/issues/issue-UX-OPERABILITY-04-panel-dismissal-focus-scope.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: PRODUCT-UX-03
- RequirementStatement: 共有、エクスポート、レビューパック取り込みを、SafeModeと公開範囲を確認してから実行する利用目的起点のフローへ整理する。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=標準サンプルを開きSafeMode ONで作業する / 操作=共有と再現を開き、出力目的、公開範囲、未レビュー情報、出力形式を確認してエクスポートする / 期待結果=何を共有するか、誰に見せるか、安全状態は何かが実行前に分かる / 除外=新しい共有サービス連携。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / public-exposure）: SafeMode / share-export / public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: e2e
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef（未確定時の参照先）: `ADR-0031`

## 1) 課題 / Problem statement

- 現行の `共有と再現` は、エクスポート、view復元、document読み込み、パッチ、適用ログ、Diff/Verify などが実装順に近い形で並ぶ。
- 画面右側のパネルタイトルは「レビューパックを取り込む」で始まるが、同じパネル内に「パッケージをエクスポート」以降の共有操作も含まれ、利用目的が分かりにくい。
- SafeModeの保護文言は改善済みだが、製品品質では「共有前に何を確認すべきか」を利用者が自然に通れる必要がある。

## 2) 背景 / Context

- `QA-MONKEY-01` はSafeMode export境界を扱う。
- `UX-OPERABILITY-04` は共有パネルの閉じ方とフォーカス復帰を扱う。
- `ADR-0031` は共有前確認面を製品化UIの基本領域として定義する。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 判断を共有しやすくするには、共有物の範囲と前提が利用者に伝わる必要がある。
- 安全（THREAT_MODEL / SafeMode）: 未レビュー本文、公開範囲、SafeMode OFF の状態は誤共有の直接リスクである。
- 企業・行政要件（enterprise_architecture）: 共有前確認、監査、公開範囲の説明は組織導入時に必須になりやすい。
- 後方互換（schemas）: 出力形式とpack/view metadataの互換性を維持する。

## 4) 提案する解決策 / Proposed solution

- 変更対象:
  - SharePanelの情報順序、見出し、タブ/ステップ構造。
  - SafeMode、公開範囲、未レビュー情報、出力形式の事前確認。
  - レビューパック取り込みと共有/エクスポートの入口分離。
  - 公開文書のデータ取り扱い・セキュリティ説明。
- 変更の最小単位:
  - 共有パネルの入口を「共有する」「取り込む」「差分を確認する」などの利用目的へ分ける。
  - エクスポート前にSafeMode・公開範囲・未レビュー情報の確認行を置く。
- 非目標:
  - ストレージサービスやSNSへの直接投稿。
  - 認証付き公開基盤の実装。
  - pack/view/documentスキーマの破壊的変更。

## 5) 受入条件 / Acceptance criteria

- [ ] パネルの起点が「取り込み」だけに見えず、共有・取り込み・差分確認の目的が分かる。
- [ ] エクスポート前にSafeMode、公開範囲、未レビュー情報、出力形式が確認できる。
- [ ] SafeMode ON/OFF の警告が日本語として自然で、共有前確認の文脈に合っている。
- [ ] `Escape` と明示的な閉じる操作で共有パネルを閉じ、起点ボタンへフォーカスが戻る。
- [ ] 狭い画面でボタン、入力、長いラベルが見切れない。
- [ ] `data_handling.md`、`security.md`、`acceptance_check.md` の説明と画面文言が一致する。

### 5.1 初期フロー案

| Step | 画面で利用者に聞くこと | 主な操作 | 必須表示 | No-Go条件 |
| --- | --- | --- | --- | --- |
| S0 目的選択 | 何をしたいか | 共有用に出力 / レビューパックを取り込む / 差分を確認 / patchを扱う | 現在のSafeMode状態 | 目的が分からないままファイル形式一覧へ進む |
| S1 共有前確認 | 誰に見せる想定か、何を含めるか | 公開範囲、未レビュー含有、出力粒度を確認 | SafeMode、公開範囲、未レビュー情報、出力形式 | SafeMode OFFや未レビュー含有が警告なしで進む |
| S2 プレビュー | 出力内容を確認できるか | ファイル一覧、概要、除外情報を確認 | 共有物の範囲、含まれない情報、注意点 | 何が出力されるか分からない |
| S3 実行 | 出力または取り込みを実行するか | ダウンロード、取り込み検証、差分確認 | 処理中状態、成功/失敗、次アクション | 失敗時に再試行・中止・診断の導線がない |
| S4 記録 | 後から説明できるか | 要約コピー、診断確認、文書への戻り | 実行結果、警告、再現に必要な最小情報 | 機微情報を含むログ共有を促す |

### 5.2 操作の分類

| 分類 | 主導線に置くもの | 補助導線に置くもの |
| --- | --- | --- |
| 共有用に出力 | PNG/SVG/view.json/bundle、SafeMode確認、公開範囲確認 | 詳細粒度、診断同梱、trace同梱 |
| 取り込み | レビューパック、document.json検証、置換確認 | view復元、baseline読み込み |
| 差分確認 | Diff/Verify、比較対象読み込み | 詳細配列、legacy検証 |
| patch | patch読み込み、lint、競合確認、適用前確認 | trust label、適用ログ、修正候補 |

## 6) 実装タスク分解 / Task breakdown

- [x] T1 SharePanelの現行操作を目的別に分類する。
- [x] T2 共有前確認のステップまたはタブ構成を設計する。
- [ ] T3 SafeMode、公開範囲、未レビュー情報、出力形式の確認UIを追加する。
- [ ] T4 取り込み、patch、Diff/Verifyの入口を補助または別タブとして整理する。
- [ ] T5 E2Eと公開文書を同期する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `cd 03_Implement/frontend && node .\\node_modules\\vitest\\vitest.mjs run src/ui/SharePanel.test.ts src/ui/i18n_equivalence.integration.test.ts`
  - `cd 03_Implement/frontend && node .\\node_modules\\playwright\\cli.js test e2e/header_toolbar_layout.spec.ts --reporter=line`
  - `rg -n "共有前|レビューパックを取り込む|セーフモード|公開範囲" 03_Implement/frontend/src 04_Documentation`
- 期待結果:
  - 共有前確認が実行前に表示され、SafeMode/公開範囲/未レビュー情報の境界が画面と文書で一致する。
- 未実施時の理由・代替検証:
  - 自動E2E更新前は、SharePanel単体テストとスクリーンショットで代替する。

## 8) 代替案 / Alternatives considered

- 代替案A: 見出し文言だけ直す。機能の並びが目的に沿わないため不十分。
- 代替案B: 共有/取り込み/差分を完全に別画面へ分ける。状態共有と移行コストが大きいため、まずパネル内の目的別整理を行う。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 手順化しすぎて、熟練利用者の素早いエクスポートが遅くなる。
- 影響範囲: SharePanel、i18n、E2E、公開文書。
- ロールバック手順: 目的別タブ/ステップを戻し、既存セクション順序へ復帰する。

## 10) Additional context

- ADR化が必要になる条件: 静的公開、認証付き公開、公開範囲メタデータの意味、SafeMode解除条件を変更する場合。

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
