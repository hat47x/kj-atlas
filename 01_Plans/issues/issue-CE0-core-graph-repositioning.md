# Issue Draft: CE0 Core Graph Repositioning（Consensus/Working model）

- Type: Process
- Status: Open
- Source Issue: N/A
- Priority: P1
- Owner: Architecture Owner
- Scope: `01_Plans/issues/`, `00_Prompt/`（Stream B: Contracts only）
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
- 再抽出結果（CG責務境界）: `WorkingGraph=探索` / `ContextProjectionGraph=read-only投影` / `ConsensusGraph=合意済み統合`。
- 再抽出結果（禁止事項）: Core Graph単独モデル回帰 / direct write / projection永続上書き / auto-apply / AI review自動昇格。

### Phase 1 Workflow（Plan -> Execute -> Verify -> Proceed）

- **Plan**: Core語彙の契約上の正本を `Consensus Graph` に統一し、旧称は履歴注記へ限定する。
- **Execute**: Graph責務境界と禁止事項を抽出し、mock-first依存切断（CE1/CE2/CE4待機禁止）を明記した。
- **Verify**: Contract ID Matrix再定義禁止と語彙固定の境界を確認した。
- **Proceed**: Phase 2でContext/Decision/Consequencesの不足補完だけを行う。

## 0.1) Phase 2 ADR明文化（不足補完のみ）

- ADR-0028は参照注記のみとし、Core/Consensus再定義を本Issueで上書きしない。
- Context/Decision/Consequences の不足記述のみを補完対象に限定する。

### Phase 2 Workflow（Plan -> Execute -> Verify -> Proceed）

- **Plan**: Graph再配置の根拠を「責務境界」と「禁止事項」に限定して追記する。
- **Execute**: 旧Core語彙の扱い（履歴注記のみ）と契約語彙（Consensus固定）を分離明記した。
- **Verify**: ADR本文再定義禁止と不足補完のみの原則を確認した。
- **Proceed**: Phase 3でAC/DoD不足を契約ゲートへ接続する。

## 0.2) Phase 3 Plan（AC/DoD不足補完）

- AC/DoDは `Query Preview必須` / `direct write禁止` / `proposal-only` / `監査4点セット必須` を同時成立させる。
- CE0契約固定に不要な実装詳細（API/CLI/UI具体）は追加しない。

### Phase 3 Workflow（Plan -> Execute -> Verify -> Proceed）

- **Plan**: Graph責務表を検証可能な判定文へ落とし込み、No-Go条件を明示する。
- **Execute**: CG-01..05をAC/DoDの検査可能単位として整理した。
- **Verify**: 実装依存の待機条件を排除し、docs-checkで完結することを確認した。
- **Proceed**: Phase 4で依存切断と停止条件を固定する。

## 0.3) Phase 4 Execute（mock-first依存切断）

- CE1/CE2/CE4の進捗待機なしで、CE0契約検証を独立実行する。
- Fail-safe（safeMode後退 / auto-apply許容 / review自動昇格許容）を即停止条件に固定する。

### Phase 4 Workflow（Plan -> Execute -> Verify -> Proceed）

- **Plan**: 依存待機を禁止し、契約固定タスク単体で完了可能にする。
- **Execute**: mock I/F前提の独立検証方針を記述した。
- **Verify**: 停止条件に安全後退3項目を含め、見逃しを許容しないことを確認した。
- **Proceed**: Phase 5で契約ID/語彙/SafeModeの3点ゼロ衝突検証へ進む。

## 0.4) Phase 5 Verify（衝突ゼロ検証）

- Contract ID collision=0 / 語彙 collision=0 / SafeMode後退=0 を同時成立させる。
- 自己修復は最大3回まで。4回目相当は即停止する。

### Phase 5 Workflow（Plan -> Execute -> Verify -> Proceed）

- **Plan**: 固定語彙と契約IDの検査コマンドを明示し、結果をProceed判定へ直結する。
- **Execute**: 衝突ゼロを満たさない場合はNo-Go停止とする運用を記述した。
- **Verify**: 3回修復上限を超えた継続を禁止することを再確認した。
- **Proceed**: Phase 6でCE1/CE2参照専用のContract Matrixを固定する。

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

### 2.6 Drift-stop 固定（Phase 4 Execute）

- Contract ID collision は **0件固定**（CE0契約IDの再定義禁止）。
- 語彙 collision は **0件固定**（契約語彙は `Consensus Graph` / `WorkingGraph` / `ContextProjectionGraph` に固定）。
- safeMode後退 / auto-apply許容 / review自動昇格許容は 1件でも検知時点で即 No-Go 停止。
- Verify自己修復は最大3回。4回目相当は停止し、推測継続を禁止する。

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
- [ ] Contract ID collision=0 / 語彙 collision=0 が検証ログで確認できる。

## 5) タスク分解（Stream B: 編集許可ファイル限定）

- [ ] T1: 本Issueと `issue-CE0-contract-freeze.md` の CG-01..05 定義を一致させる（再定義禁止）。
- [ ] T2: `00_Prompt/ai_cognitive_externalization_requirements.md` の三層語彙を Consensus/Working/ContextProjection に同期する。
- [ ] T3: CE1/CE2向け参照専用 Graph Contract Matrix を固定し、上書き禁止を明記する。
- [ ] T4: DecisionQueue 参照（`UNC-VSC-CE-02-01..03`）の追跡可能性を本Issue内で維持する。

## 6) 検証計画 / Validation plan

- 実行コマンド:
  - `rg -n "Consensus Graph|WorkingGraph|ContextProjectionGraph|autonomous|patch \\+ approval|Query Preview|direct write|proposal-only|safeMode|human_reviewed|auto-apply|CG-0[1-5]" 01_Plans/issues/issue-CE0-contract-freeze.md 01_Plans/issues/issue-CE0-core-graph-repositioning.md 00_Prompt/ai_cognitive_externalization_requirements.md`
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

### Phase 6 Workflow（Plan -> Execute -> Verify -> Proceed）

- **Plan**: CE1/CE2にはGraph責務境界の固定値のみを引き渡し、再定義を禁止する。
- **Execute**: Working/Projection/Consensus + CG-01..05 を参照専用I/Fとして固定した。
- **Verify**: 実装詳細や新規契約IDが混入していないことを確認する。
- **Proceed**: 追加変更はCE0再起票で処理し、Stream Bの契約凍結を維持する。

## 9) CE1/CE2 引き渡し Graph Contract Matrix（固定）

| Consumer | Graph Contract | Required IDs | Blockers (No-Go) |
| --- | --- | --- | --- |
| CE1 | `Working -> ContextProjection(read-only) -> Bundle -> Proposal` | `CE0-CTX-IF`, `CG-01`, `CG-03`, `CG-05` | Projection永続上書き / Query Preview bypass / 監査欠損成功扱い |
| CE2 | `Working -> Proposal-only -> Human Approval -> Consensus` | `CE0-REVIEW-IF`, `CE0-SAFEMODE-IF`, `CG-02`, `CG-04` | auto-apply / review自動昇格 / safeMode既定緩和 |

> ADR-0028は参照注記のみ（本文再定義禁止）。本MatrixはCE0 Core Graph Repositioningの参照専用固定値とする。
