# Issue Draft: PRODUCT-VALUE-02 保留・違和感・根拠不足を扱う作業フロー

- Type: Feature request
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: TBD
- Scope: `03_Implement/frontend/src/`, `03_Implement/frontend/e2e/`, `02_Architecture/schemas.md`, `02_Architecture/value_traceability.md`
- Related Backlog: `PRODUCT-VALUE-02`
- Related ADR/Spec: `01_Plans/adr/ADR-0032-product-value-realization-model.md`, `00_Prompt/domain.md`, `00_Prompt/ai_cognitive_externalization_requirements.md`, `02_Architecture/llm_input_ir_spec.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: PRODUCT-VALUE-02
- RequirementStatement: 利用者が、保留、違和感、根拠不足、反対意見を、削除や失敗ではなく作業状態として記録、確認、再提案の制約に使えるようにする。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=カード、島、関係がある文書を開く / 操作=対象に保留、違和感、根拠不足、反対意見を付け、表示と絞り込みを確認する / 期待結果=未確定状態が残り、共有やAI提案時にもレビュー状態と安全境界が維持される / 除外=自動採点、正解判定、AIによる保留解除。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export
- VerificationLevel（docs-check / unit / integration / e2e）: e2e
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef（未確定時の参照先）: `ADR-0032`

## 1) 課題 / Problem statement

- `domain.md` は保留と違和感を中核概念として定義しているが、製品化UI上で日常操作としてどう扱うかがまだ薄い。
- `llm_input_ir_spec.md` は evidence / contradiction をAI文脈に含めているが、利用者が画面上で根拠不足や反対意見を記録する作業単位が十分に固定されていない。
- この不足により、kj-atlas が単なるカード配置ツールに見え、認知外在化ツールとしての価値が伝わりにくい。

## 2) 背景 / Context

- `ADR-0032` は V1/V2/V3 として、外在化、構造化、レビューを価値ループへ位置づけた。
- `CE0-REVIEW-IF` と `CE0-SAFEMODE-IF` は、未レビュー情報の保護と人手レビュー昇格を固定している。
- `PRODUCT-UX-02` は画面構造を扱うが、保留や根拠不足の操作語彙までは十分に分解していない。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 保留と違和感を記録できないと、P-01/P-04の価値がUIで成立しない。
- 安全（THREAT_MODEL / SafeMode）: 未レビュー・根拠不足の情報が共有物で確定事項に見えると誤共有につながる。
- 企業・行政要件（enterprise_architecture）: 判断根拠、反対意見、未解決点を残せることは説明責任に直結する。
- 後方互換（schemas）: 既存スキーマへ破壊的変更を入れず、必要なら新規issue/ADRで拡張案を分離する。

## 4) 提案する解決策 / Proposed solution

- 変更対象:
  - カード/島/関係の選択コンテキスト、状態バッジ、絞り込み、共有前確認、AI Context Query入力。
- 変更の最小単位:
  - 保留、違和感、根拠不足、反対意見を利用者向け状態語彙として定義する。
  - これらの状態が表示、絞り込み、共有前確認、AI提案制約に現れることを確認する。
- 非目標:
  - 正解判定、採点、ランキング。
  - AIによる保留解除やレビュー済み昇格。
  - 証拠能力を持つ監査証跡の実装。

## 5) 受入条件 / Acceptance criteria

- [ ] カード、島、関係のいずれかに、保留または違和感を理由なしで付けられる。
- [ ] 根拠不足と反対意見を、確定済み情報と区別して表示できる。
- [ ] 状態バッジや絞り込みで、未整理、未レビュー、根拠不足を見つけられる。
- [ ] 共有前確認で、保留点、未レビュー情報、根拠不足が残っていることを確認できる。
- [ ] AI提案に渡す場合は、ContextBundle上で制約または除外理由として追跡できる。
- [ ] `human_reviewed` は人間操作でのみ昇格し、AI/worker/APIで自動昇格しない。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 保留、違和感、根拠不足、反対意見のUI語彙とデータ責務を整理する。
- [ ] T2 現行スキーマで表現できる範囲と、追加スキーマが必要な範囲を分離する。
- [ ] T3 選択コンテキスト、絞り込み、共有前確認に表示するワイヤーフローを作成する。
- [ ] T4 ContextQuery/ContextBundleへの受け渡し境界を確認する。
- [ ] T5 E2Eまたは統合テストで状態付与、表示、共有前確認を検証する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `rg -n "保留|違和感|根拠不足|反対意見|human_reviewed|unreviewed" 00_Prompt 01_Plans 02_Architecture 03_Implement/frontend 04_Documentation`
  - `cd 03_Implement/frontend && node .\\node_modules\\vitest\\vitest.mjs run`
  - `cd 03_Implement/frontend && node .\\node_modules\\playwright\\cli.js test --reporter=line`
- 期待結果:
  - 保留・違和感・根拠不足が操作、表示、共有前確認、AI入力境界で一貫して扱われる。
- 未実施時の理由・代替検証:
  - スキーマ拡張判断前は、ワイヤーフローとContextBundle境界レビューで代替する。

## 8) 代替案 / Alternatives considered

- 代替案A: コメント欄だけで保留や違和感を表現する。検索、共有前確認、AI制約に接続しにくいため採用しない。
- 代替案B: AIが保留点を自動解消する。プロジェクト価値とCE0契約に反するため採用しない。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 状態語彙が増えすぎて、カード編集が重くなる。
- 影響範囲: frontend selection context、schemas、ContextBundle、share/export。
- ロールバック手順: 状態語彙を表示専用の補助メタデータへ戻し、スキーマ拡張は別ADRに切り出す。

## 10) Additional context

- ADR化が必要になる条件: document/view/packスキーマへ新しい永続状態を追加する場合、またはEvidenceLink/ClaimTypeの製品UI責務を固定する場合。

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
