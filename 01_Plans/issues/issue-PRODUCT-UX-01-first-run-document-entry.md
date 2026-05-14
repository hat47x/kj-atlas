# Issue Draft: PRODUCT-UX-01 初回利用と文書入口の製品化

- Type: Feature request
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: TBD
- Scope: `03_Implement/frontend/src/`, `04_Documentation/installation.md`, `04_Documentation/operations.md`, `04_Documentation/public_index.md`
- Related Backlog: `PRODUCT-UX-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`, `01_Plans/issues/issue-MVP-EXIT-01-productization-readiness.md`, `ROADMAP.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: PRODUCT-UX-01
- RequirementStatement: 初回利用者が、起動後に新規作成、サンプル確認、既存文書読み込み、安全状態確認へ迷わず到達できる文書入口を用意する。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=ブラウザでkj-atlasを初回起動する / 操作=新規作成、サンプルを開く、document.jsonを読み込む、SafeMode状態を確認する / 期待結果=内部管理用語やレガシー導線に迷わず、現在の作業開始方法が分かる / 除外=認証付きポータルやクラウド同期の実装。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / import-sanitize
- VerificationLevel（docs-check / unit / integration / e2e）: e2e
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef（未確定時の参照先）: `ADR-0031`

## 1) 課題 / Problem statement

- 現行アプリは標準サンプルまたは既定文書へ直接入る前提が強く、初回利用者が「何から始めるか」を画面上で判断しづらい。
- 主要ツールバーにはレガシーJSON操作が目立ち、文書の作成・読み込み・共有前確認の関係が分かりにくい。
- 公開文書では利用開始手順が整備されつつあるが、画面上の入口が同じ概念で整理されていない。

## 2) 背景 / Context

- `04_Documentation/public_index.md` は一般利用者向けの入口として整理済み。
- `04_Documentation/installation.md` と `operations.md` は起動・日常運用を説明するが、画面上の開始状態はMVP期の実装都合が残る。
- `ADR-0031` は開始/文書入口を製品化UIの基本領域として定義する。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 初回に迷わず作業面へ入れることは、思考整理に集中する前提である。
- 安全（THREAT_MODEL / SafeMode）: 起動時からSafeModeと取り込み時の検証状態を見せることで、誤った共有や不正な取り込みを防ぎやすい。
- 企業・行政要件（enterprise_architecture）: 組織導入では、利用者が教育なしでも標準操作を開始できる画面が必要になる。
- 後方互換（schemas）: document/view/pack スキーマは変更せず、入口と説明を整理する。

## 4) 提案する解決策 / Proposed solution

- 変更対象:
  - 起動直後の文書選択/作成状態。
  - サンプル、最近使った文書、document.json取り込み、レビューパック取り込みの配置。
  - SafeMode と読み取り専用状態の初期表示。
  - 公開文書のスクリーンショットと操作説明。
- 変更の最小単位:
  - 既定文書へ入る前に、開始状態または開始パネルを追加する。
  - レガシーJSON操作は補助導線として残し、推奨入口と区別する。
- 非目標:
  - 認証、ユーザープロファイル、クラウド上の最近使った文書一覧。
  - 既存のdocument読み込み形式の破壊的変更。

## 5) 受入条件 / Acceptance criteria

- [ ] 初回起動時に、新規作成、サンプル、既存document.json、レビューパック取り込みの違いが分かる。
- [ ] SafeModeの状態が、作業開始前に確認できる。
- [ ] 取り込み系操作は検証・置換・復元の違いが画面上で分かる。
- [ ] レガシーJSON操作が主要な推奨入口として誤認されない。
- [ ] `Tab` / `Enter` / `Space` で開始操作に到達できる。
- [ ] 公開文書の導入手順と画面上の文言が一致する。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 起動直後に必要な開始操作を利用者視点で分類する。
- [ ] T2 開始状態または開始パネルのワイヤーフローを作成する。
- [ ] T3 SafeMode、読み取り専用、取り込み検証の状態表示を追加する。
- [ ] T4 キーボード操作と小画面表示をE2Eで確認する。
- [ ] T5 `04_Documentation/installation.md` と `operations.md` の手順・スクリーンショットを同期する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `cd 03_Implement/frontend && node .\\node_modules\\typescript\\bin\\tsc --noEmit`
  - `cd 03_Implement/frontend && node .\\node_modules\\vitest\\vitest.mjs run src/i18n/ui_hardcode_guard.test.ts src/ui/i18n_equivalence.integration.test.ts`
  - `cd 03_Implement/frontend && node .\\node_modules\\playwright\\cli.js test e2e/header_toolbar_layout.spec.ts --reporter=line`
- 期待結果:
  - 初回入口、取り込み、SafeMode確認がマウスとキーボードで到達可能で、公開文書と矛盾しない。
- 未実施時の理由・代替検証:
  - 自動E2E追加前は、Playwright script のTab順序ログとスクリーンショットで代替する。

## 8) 代替案 / Alternatives considered

- 代替案A: 既定文書を直接開き、文書だけで使い方を説明する。画面上の迷いが残るため採用しない。
- 代替案B: 完全なプロジェクト管理ダッシュボードを作る。製品化の初期段階としては過大であり、文書入口に絞る。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 起動直後の選択肢が増えすぎ、かえって初回利用者が迷う。
- 影響範囲: frontend shell、文書読み込み、公開文書。
- ロールバック手順: 開始パネルを機能フラグまたはルーティング単位で戻し、既定文書直接表示へ戻す。

## 10) Additional context

- ADR化が必要になる条件: 起動ルーティング、ローカル履歴保持、公開版と編集版の分離を再定義する場合。

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
