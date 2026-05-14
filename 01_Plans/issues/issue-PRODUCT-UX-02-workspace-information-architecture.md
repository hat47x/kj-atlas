# Issue Draft: PRODUCT-UX-02 ワークスペース画面構造の製品化

- Type: Feature request
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: TBD
- Scope: `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/src/ui/`, `03_Implement/frontend/src/canvas/`, `04_Documentation/acceptance_check.md`
- Related Backlog: `PRODUCT-UX-02`
- Related ADR/Spec: `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`, `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`, `01_Plans/issues/issue-UX-OPERABILITY-03-contextual-selection-panel.md`, `01_Plans/issues/issue-UX-OPERABILITY-05-primary-toolbar-task-prioritization.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: PRODUCT-UX-02
- RequirementStatement: キャンバス、選択コンテキスト、作業モード、共有前確認を画面上で整理し、一般利用者が主作業と高度機能を混同しない状態にする。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=標準サンプルをブラウザで開く / 操作=カード選択、島選択、表示切替、レビュー、共有パネル表示を行う / 期待結果=選択対象の確認が現在表示範囲に出て、高度機能は明示的なモードまたはタブとして分離される / 除外=全コンポーネントの見た目刷新。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export
- VerificationLevel（docs-check / unit / integration / e2e）: e2e
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef（未確定時の参照先）: `ADR-0031`

## 1) 課題 / Problem statement

- 右側パネルにレビュー、差分、ナラティブ、候補比較、CE3、批評、カード確認などが縦に並び、利用者の現在の作業文脈が分かりにくい。
- カードを選択しても、選択対象の確認領域が現在表示範囲外にあり、マウス操作の結果が直感的に伝わらない。
- 主要ツールバーには基本操作、共有、安全確認、レガシー操作が混在し、初回利用者が優先すべき操作を判断しづらい。

## 2) 背景 / Context

- `UX-OPERABILITY-03` はカード選択後の文脈表示不足を個別課題として起票済み。
- `UX-OPERABILITY-05` はレガシー/高度操作が主要ツールバーに混在する問題を扱う。
- 本Issueは、それらを画面構造全体の製品化作業として束ねる。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 俯瞰と詳細の往復を支援するには、選択したものの意味と次の操作が近くにある必要がある。
- 安全（THREAT_MODEL / SafeMode）: 共有・AI提案・未レビュー情報は、通常編集と同列に混在すると誤操作につながる。
- 企業・行政要件（enterprise_architecture）: 操作説明や教育資料で説明できる画面構造が必要になる。
- 後方互換（schemas）: 表示構造の整理を優先し、データ契約は維持する。

## 4) 提案する解決策 / Proposed solution

- 変更対象:
  - 右側パネルのセクション順序、折りたたみ、タブ化。
  - ツールバーの基本/補助/高度操作の分類。
  - 選択対象のカード/島/関係線インスペクター。
  - 表示パネル、共有と再現パネルの開閉・フォーカス復帰。
- 変更の最小単位:
  - 選択コンテキストを最上位に移す。
  - 高度機能を作業モード単位に分ける。
  - 主要ツールバーの推奨操作を整理する。
- 非目標:
  - 全画面のビジュアル刷新。
  - AI提案やパッチ仕様の変更。
  - レガシー導線の削除。

## 5) 受入条件 / Acceptance criteria

- [ ] カードまたは島を選択した直後、対象の確認・編集・レビュー状態が現在表示範囲で分かる。
- [ ] 高度機能はタブ、折りたたみ、または作業モードとして区別される。
- [ ] 起動直後の主要ツールバーでは、推奨される基本操作が先に見える。
- [ ] `表示`、`共有と再現`、作業モード面は `Escape` または明示的な閉じる操作で戻れる。
- [ ] `Tab` 順序が現在の作業文脈を優先する。
- [ ] `04_Documentation/acceptance_check.md` が新しい画面構造を前提に更新される。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 現行画面を「開始/キャンバス/選択/作業モード/共有前確認」に分類する。
- [ ] T2 右側パネルのセクション順序と折りたたみ/タブ化方針を作成する。
- [ ] T3 ツールバー操作を基本、補助、高度、レガシーに分類する。
- [ ] T4 選択コンテキストの表示位置とフォーカス順序を実装する。
- [ ] T5 Playwrightで代表操作を検証し、スクリーンショットを公開文書へ同期する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `cd 03_Implement/frontend && node .\\node_modules\\typescript\\bin\\tsc --noEmit`
  - `cd 03_Implement/frontend && node .\\node_modules\\playwright\\cli.js test e2e/header_toolbar_layout.spec.ts --reporter=line`
  - `rg -n "legacy|JSON取り込み|JSON書き出し|共有と再現|カードの確認" 03_Implement/frontend/src`
- 期待結果:
  - 選択、編集、表示、共有前確認の導線が画面上で分離され、見切れやフォーカス迷子がない。
- 未実施時の理由・代替検証:
  - UI大変更前は、Playwrightの操作ログとスクリーンショットで画面構造案をレビューする。

## 8) 代替案 / Alternatives considered

- 代替案A: 現行右側パネルをそのまま維持し、説明文だけ追加する。画面上の認知負荷が残る。
- 代替案B: 画面を完全に別アプリのように再設計する。既存機能とE2Eへの影響が大きいため段階移行する。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: タブ化や折りたたみにより、熟練利用者が既存機能を見つけにくくなる。
- 影響範囲: frontend shell、side panel、SharePanel、E2E、公開文書。
- ロールバック手順: セクション配置変更をコンポーネント単位で戻し、既存の縦積みパネルへ一時復帰する。

## 10) Additional context

- ADR化が必要になる条件: ナビゲーション階層、URLルーティング、作業モードの永続化、ショートカット体系を確定する場合。

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
