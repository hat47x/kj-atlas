# Issue Draft: CE0 Core Graph Repositioning（Consensus/Working model）

- Type: Process
- Status: Draft
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
- DecisionStatus: Pending
- DecisionQueueRef: `UNC-VSC-CE-02-01`, `UNC-VSC-CE-02-02`, `UNC-VSC-CE-02-03`

## 1) 課題 / Problem statement

- 従来Core Graphは「唯一正本」前提だったが、AI単独運用・主体別キャンバス要件を吸収できない。
- 本Issueは、Graph層の責務境界を再配置し、作業者が設計判断できる状態にする。

## 2) 具体仕様（実装者向け）

- Graph種別:
  - `WorkingGraph`: actor/role単位の探索グラフ（未確定許容）。
  - `ConsensusGraph`: 合意済み差分のみを保持する統合グラフ。
- 遷移ルール:
  - `Working -> Consensus` は `patch + approval` のみ。
  - `mode=autonomous` でも監査ログ4点セットを必須。
- メタ分離:
  - `actor` と `modelTier` を別フィールドで記録（混同禁止）。

## 3) 受入条件 / Acceptance criteria

- [ ] `Core Graph` 用語が対象文書で `Consensus Graph` に置換/追記される。
- [ ] Working/Consensusの責務境界を1テーブルで提示（read/write責務を明示）。
- [ ] `autonomous mode` の許可条件と禁止条件が明文化される。
- [ ] KJ法構造（card/island/relation/pending）との整合原則が明記される。
- [ ] DecisionQueueの3項目（UNC-VSC-CE-02-01..03）がOpen/Pendingで追跡可能。

## 4) 実装タスク分解 / Task breakdown

- [ ] T1: `02_Architecture/architecture.md` にGraph層責務表を追加。
- [ ] T2: `02_Architecture/schemas.md` にGraph種別メタ（actor/modelTier/mode）の予約項目を追加。
- [ ] T3: `04_Documentation/operations.md` にautonomous mode運用制約を追加。
- [ ] T4: DecisionQueue項目を `decision-pack-2026-03-human-judgement.md` に連携。

## 5) 検証計画 / Validation plan

- 実行コマンド:
  - `rg -n "Consensus Graph|Working Graph|autonomous|modelTier|patch \+ approval" 01_Plans/adr 02_Architecture 04_Documentation`
  - `python 01_Plans/issues/validate_active_issue_memos.py`
- 期待結果:
  - Graph定義の二重化なし、Queue参照切れなし。

## 6) リスクとロールバック / Risks & rollback

- 失敗モード: Graph責務が曖昧で実装側が独自解釈する。
- ロールバック: D11決定前の定義に戻し、VSC再審議で再起票。
