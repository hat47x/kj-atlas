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


## 11) 価値実現シリアル（Hypothesis → Action → Evidence → Decision）

- 価値仮説: 保留・違和感・根拠不足・反対意見を明示管理できると、早すぎる収束を防ぎレビュー品質が上がる。
- 行動:
  1. カード/島/関係に4状態（保留、違和感、根拠不足、反対意見）を付与する。
  2. 状態バッジと絞り込みで未確定項目を抽出する。
  3. 共有前確認で未確定情報の残存を確認する。
  4. AI提案入力境界で状態情報が制約として扱われることを確認する。
- 証拠:
  - E1: 状態付与と表示の検証結果（UIまたは仕様手順）。
  - E2: 絞り込み結果の再現記録。
  - E3: 共有前確認で未確定情報が表示された証拠。
  - E4: ContextBundle入力境界で状態が追跡可能な証拠。
- 判定（Go/No-Go）:
  - Go: E1〜E4が揃い、未確定状態抽出の再現率100%（同一条件3回で同一結果）。
  - No-Go: いずれかの状態が欠落、または再現率100%未満。

## 12) KPI定義（定義可能・再測定可能・比較可能）

- KPI-01 `ambiguity_state_coverage`
  - 定義: 4状態のうちUI語彙と証拠手順が定義済みの割合。
  - 再測定: issue本文と受入条件を照合する。
  - 比較: 版間で定義済み割合を比較する。
- KPI-02 `unresolved_extraction_reproducibility`
  - 定義: 同一条件で未確定項目抽出結果が一致する試行割合。
  - 再測定: 同一データで3回実行する。
  - 比較: 実装/仕様変更前後で割合比較する。
- KPI-03 `review_boundary_integrity`
  - 定義: `human_reviewed` が自動昇格しない検証項目の合格率。
  - 再測定: 固定チェックリストで確認する。
  - 比較: 回帰有無を版間で比較する。


---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。


## Stream I 要件契約固定パック（2026-05-18）

### Phase 1: Read同期サマリ
- 重複論点: 画面導線の分かりやすさ、SafeMode境界、検証証跡要件。
- 曖昧論点: Open化の判定条件と、依存関係が契約依存か実装依存かの境界。
- 欠落補完: 価値→要件→受入→測定の追跡行と、Draft→Open判定を明文化。

### Phase 2-3: ADR要素 + 要件契約
| Context | Decision | Consequences |
| --- | --- | --- |
| 上流価値定義（ADR-0001/0031/0032）を実装入口へ接続する必要がある。 | AC/DoDを機械検証可能な粒度で固定し、未確定はDecision Queueへ隔離する。 | 下流実装Streamは要件の再発明をせず、検証可能なIssue単位で着手できる。 |

### 価値→要件→受入→測定 対応表（最小）
| 価値仮説 | 要件（Requirement） | 受入条件（AC） | 測定（Evidence/KPI） |
| --- | --- | --- | --- |
| 利用者が安全に判断を共有できる。 | SafeMode境界を保持し、共有前確認を必須化する。 | SafeMode/公開範囲/未レビュー状態を実行前に提示できる。 | docs-check + E2E記録 + 文言一致確認。 |
| 要件から実装へ手戻りなく移行できる。 | AC/DoDをOpen前に固定し、未確定はPending化する。 | Draft→Open条件を満たしたIssueのみ実装に着手する。 | checklist充足率、No-Go件数、Pending解消件数。 |

### Phase 4: Draft→Open 条件（要件側ゲート）
- [ ] `DecisionStatus=Fixed` の要求のみでACが評価可能（PendingはDecision Queueへ退避済み）。
- [ ] 依存が `契約依存`（schema/api/policy/ops）と `実装依存`（UI/Backend/E2E）に分離されている。
- [ ] Validation plan のコマンドがこのIssue本文だけで再実行可能。

### Phase 5-6: Verify / Proceed 引き継ぎ条件
- Verify合格条件: 価値仮説とACの1対1追跡が可能で、非検証要件が残っていない。
- Proceed条件: 実装ストリームが「どのACをどのテストで満たすか」を追加解釈なしで決定できる。
- フェイルセーフ: 上流価値定義との矛盾・非検証要件・競合編集を検出した場合はOpen化を停止する。

## Open化判定メタ（Draft gate解除条件）

### Open化に必要な最小条件（全件必須）
- [ ] O-OPEN-01: `Owner` が `TBD` ではなく、実行責務者（個人またはロール）に確定している。
- [ ] O-OPEN-02: 依存Issue/ADRごとに `依存待ち理由` と `再開条件` が1:1で明示されている。
- [ ] O-OPEN-03: `Acceptance criteria` と `Validation plan` が `Expected verification level` と一致している。
- [ ] O-OPEN-04: docs-only範囲外の要求が本文に混入していない（本memoの範囲と矛盾しない）。

### 依存待ち理由（未解消時は Draft 維持）
| Dependency | 依存待ち理由 | 再開条件 | Owner |
|---|---|---|---|
| 上位ADR/関連Issue | 上位合意または境界仕様の最終確定待ち | 参照先に承認IDまたは確定コミットを追記 | Platform Architecture Owner / 各Issue Owner |
| QA検証経路 | `e2e`/`integration` の実行経路と証跡フォーマット未固定 | 実行経路（Compose/SQLite/例外）を1件固定し、判定ログ形式を定義 | QA Lead |
| 実行責務 | 実装担当とレビュー担当の分離未確定 | RACI（R/A）を本文に追記し通知記録を残す | PM/Triage |

### Proceed / Stop
- Proceed（Open化可）: O-OPEN-01〜04がすべて充足。
- Stop（Draft維持）: 依存先不明 / Status正規化不能 / 競合ファイル検出時は更新停止し、理由を `Additional context` に記録。

