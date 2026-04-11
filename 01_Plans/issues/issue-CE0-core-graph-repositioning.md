# Issue Draft: CE0 Core Graph Repositioning（Consensus/Working model）

- Type: Process
- Status: Open
- Source Issue: N/A
- Priority: P1
- Owner: Architecture Owner
- Scope: `01_Plans/`, `02_Architecture/`, `04_Documentation/`
- Related Backlog: `CE-0`
- Related ADR/Spec: `ADR-0028` (D11), `00_Prompt/virtual_stakeholder_consensus.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）
- RequirementID: `CE0-CORE-GRAPH-REPOSITION`
- RequirementStatement: Core GraphをConsensus Graphへ再定義し、Working Graphとの責務境界を固定する。
- PriorityClass: Must
- AcceptanceScenario: 前提=VSC-CE-02実施 / 操作=Architecture同期 / 期待結果=Core定義の二重化なし / 除外=RBAC実装
- GoNoGoGate: Required
- SecurityGateImpact: SafeMode / public-exposure
- VerificationLevel: docs-check
- DecisionStatus: Fixed
- DecisionQueueRef: `UNC-VSC-CE-02-01`, `UNC-VSC-CE-02-02`, `UNC-VSC-CE-02-03`
- Stream: `B` (Contracts only / Docs-Plan only)

## 0) Phase 1 Read（最新メタ）

- Core Graph 契約語彙は `Consensus Graph` に固定し、旧称 `Core Graph` は履歴注記用途のみに限定。
- CE1/CE2/CE4 連携は mock I/F 前提で待機しない（依存切断）。
- CE3/HIL-RS 系の実装・計画へは本Issueから変更を波及させない。
- Contract ID Matrix（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）は再定義せず参照専用で扱う。

## 1) Context

- 従来Core Graphは「唯一正本」前提だったが、AI単独運用・主体別キャンバス要件を吸収できない。
- CE-0でグラフ責務を固定しないと、CE-1以降で projection と consensus の更新経路が混線する。

## 2) Decision

### 2.1 責務境界（Responsibility）

- Graph種別:
  - `WorkingGraph`: actor/role単位の探索グラフ（未確定許容）。
  - `ContextProjectionGraph`: 問合せ目的へ投影する読取専用グラフ（ContextBundle生成専用）。
  - `ConsensusGraph`: 合意済み差分のみを保持する統合グラフ（旧Core Graph）。
- 遷移ルール:
  - `Working -> Consensus` は `patch + approval` のみ。
  - `Working -> ContextProjection` は read-only projection のみ（書込禁止）。
  - `mode=autonomous` でも監査ログ4点セットを必須。
- メタ分離:
  - `actor` と `modelTier` を別フィールドで記録（混同禁止）。

### 2.2 入出力境界（Input / Output）

- 入力（許可）:
  - WorkingGraphのKJ構造（card/island/relation/pending）
  - Query constraints（safeMode/reviewFilter/depth/scope）
- 出力（許可）:
  - ContextBundle（deterministic hash付き）
  - PatchProposal（Consensus適用前提）
- 出力（禁止）:
  - ConsensusGraph直接更新
  - Projection結果の永続化上書き
  - review状態のAI自動変更

### 2.3 I/F固定表（実装レーン引き渡し用）

| Layer | Must | Must Not |
| --- | --- | --- |
| Graph model | Working/Projection/Consensusを分離し、read/write責務を明示 | Core Graph単独モデルで責務を兼務させる |
| Transition | `patch + approval` 以外でConsensus更新しない | direct write / auto-merge |
| Audit | `query/bundle/proposal/apply` を必須化 | 欠損時に成功扱い |
| Safety | safeMode既定ON時は未レビュー本文をprojectionへ投入しない | safeMode緩和を既定化 |

### 2.4 CG-01..05 固定定義（Phase 1 Read 抽出）

- `CG-01`: Graph責務分離を固定（Working / ContextProjection / Consensus の3層）。
- `CG-02`: 遷移は `Working -> Consensus = patch + approval only` を固定（direct write禁止）。
- `CG-03`: Projectionは read-only（永続書込禁止、bundle生成専用）を固定。
- `CG-04`: `mode=autonomous` でも proposal-only を固定（auto-apply禁止）。
- `CG-05`: 監査4点セット（`query/bundle/proposal/apply`）欠損時は成功扱い禁止を固定。

### 2.5 Go/NoGo Key（固定）

- **Go**:
  - Core Graph表現が契約語彙としては `Consensus Graph` に一本化される（旧称は注記のみ）。
  - Working/Projection/Consensus の read/write 境界が表形式で追跡可能。
  - Query Preview bypass 禁止・direct write 禁止・auto-apply 禁止が同時成立。
- **No-Go**:
  - Core Graph 単独モデルへ責務を再集約する記述が残る。
  - Projection の永続上書きや review 自動遷移を許容する記述が残る。
  - `UNC-VSC-CE-02-01..03` の追跡不能状態を放置する。

## 3) Consequences

- `Core Graph` の語彙は履歴説明用の別名としてのみ残し、契約語彙は `Consensus Graph` に統一する。
- `autonomous mode` は proposal-only を維持し、自動適用モードとして扱わない。
- 3項目のDecision QueueがCloseされるまで、実装での責務緩和は禁止する。
- Fail-safe: SafeMode後退、auto-apply許容、review自動昇格の兆候を検知した場合は即停止する。

## 4) 受入条件 / Acceptance criteria

- [ ] `Core Graph` 用語が対象文書で `Consensus Graph` に置換/追記される。
- [ ] Working/Consensusの責務境界を1テーブルで提示（read/write責務を明示）。
- [ ] `autonomous mode` の許可条件と禁止条件が明文化される。
- [ ] KJ法構造（card/island/relation/pending）との整合原則が明記される。
- [ ] DecisionQueueの3項目（UNC-VSC-CE-02-01..03）がOpen/Pendingで追跡可能。
- [ ] Query Preview必須 / direct write禁止 / proposal-only / 監査4点セット必須 の4条件が同時成立する。

## 5) タスク分解（文書限定）

- [ ] T1: `02_Architecture/architecture.md` にGraph層責務表を追加。
- [ ] T2: `02_Architecture/schemas.md` にGraph種別メタ（actor/modelTier/mode）の予約項目を追加。
- [ ] T3: `04_Documentation/local_llm_ops_guide.md` にautonomous mode運用制約を同期。
- [ ] T4: DecisionQueue項目を本Issue群（CE0/CE1/CE2/CE4）へ参照リンクとして同期（本Stream外ファイルは編集しない）。

## 6) 検証計画 / Validation plan

- 実行コマンド:
  - `rg -n "Consensus Graph|WorkingGraph|ContextProjectionGraph|autonomous|patch \\+ approval|Query Preview|direct write|proposal-only|safeMode|unreviewed|CG-0[1-5]" 01_Plans/issues/issue-CE0-contract-freeze.md 01_Plans/issues/issue-CE0-core-graph-repositioning.md 02_Architecture/architecture.md 02_Architecture/schemas.md`
  - `python 01_Plans/issues/validate_active_issue_memos.py`
- 期待結果:
  - Graph定義の二重化なし、Queue参照切れなし。
- 実行ポリシー:
  - ドリフト検知→修正→再検証を最大3回まで自律実行する。
  - SafeMode後退 / auto-apply許容 / review自動昇格許容を検知した時点で即 No-Go 停止する。

## 7) リスクとロールバック / Risks & rollback

- 失敗モード: Graph責務が曖昧で実装側が独自解釈する。
- ロールバック: D11決定前の定義に戻し、VSC再審議で再起票。


## 8) Phase 6 Proceed（CE3向け参照専用）

- Graph責務: `WorkingGraph`（探索）/`ContextProjectionGraph`（read-only）/`ConsensusGraph`（合意済み）を固定。
- 遷移責務: `Working -> Consensus = patch + approval only`。
- 安全責務: `mode=autonomous` でも proposal-only、auto-apply禁止、review自動昇格禁止。

フェイルセーフ（即停止）: SafeMode後退 / auto-apply許容 / 未レビュー昇格許容。
