# Issue Draft: CE0 Contract Freeze（ACCI + Graph Contract）

- Type: Process
- Status: Draft
- Source Issue: N/A
- Priority: P1
- Owner: Plan Owner
- Scope: `01_Plans/`, `02_Architecture/`, `04_Documentation/`
- Related Backlog: `CE-0`
- Related ADR/Spec: `ADR-0028`, `00_Prompt/ai_cognitive_externalization_requirements.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）
- RequirementID: `CE0-CONTRACT-FREEZE`
- RequirementStatement: ACCI方式・Guard-01〜05・CG-01〜05 を文書横断で凍結する。
- PriorityClass: Must
- AcceptanceScenario: 前提=ADR-0028更新済 / 操作=契約ID同期 / 期待結果=定義衝突0件 / 除外=実装コード変更
- GoNoGoGate: Required
- SecurityGateImpact: SafeMode / share-export
- VerificationLevel: docs-check
- DecisionStatus: Fixed
- DecisionQueueRef: `UNC-VSC-CE-01-01`, `UNC-VSC-CE-02-01`

## 1) 課題 / Problem statement

- CE-1以降の実装で参照する契約が複数文書に散在しており、語彙ズレ（Core/Consensus、reviewed/unreviewed、safeMode）が発生しやすい。
- このIssueは契約語彙の「固定」と「参照元の一本化」を目的とする。

## 2) 背景 / Context

- ADR-0028 D9/D10/D11 で AI運用方式とCore Graph再定義が追記された。
- 00/01/02/04で語彙がズレると、検証不能な実装差分が発生する。

## 3) CE0固定契約（Contract Freeze）

### 3.1 責務境界（Responsibility）

- CE0が固定する対象:
  - 認知外在化AIの最小契約（ContextQuery/ContextBundle/PatchProposal）
  - Graph責務境界（Working / Projection / Consensus）
  - 安全境界（safeMode既定ON・unreviewed保護・auto-apply禁止）
- CE0が固定しない対象:
  - API詳細スキーマ・CLI引数・UI配置・モデル選定・RBAC実装

### 3.2 入出力境界（Input / Output）

- 入力（許可）:
  - `document/view/patch` の正規入力のみ
  - ContextQuery（`goal/scope/depth/constraints/reviewFilter/safeModePolicy/outputMode`）
- 出力（許可）:
  - Patch Proposal（`proposalId + diff + rationale`）
  - 監査4点セット（`query/bundle/proposal/apply`）
- 出力（禁止）:
  - Consensus Graphへの直接書込
  - `human_reviewed` の自動昇格
  - Query Previewを通さない送信経路

### 3.3 影響範囲 / 非対象範囲

- 影響範囲:
  - `ADR-0028`, `02_Architecture/architecture.md`, CE0 issueメモ群
  - 後続CE-1〜CE-4で参照する契約ID・Go/NoGo判定
- 非対象範囲:
  - 実装コード変更
  - 既存SafeModeポリシー自体の再設計
  - 運用手順の詳細化（CE-3/CE-4で実施）

## 4) 受入条件 / Acceptance criteria

- [ ] ACCIの5段手順が 01/02/04 で同語彙定義される。
- [ ] Guard-01〜05 の意味が文書間で一致し、禁止事項に矛盾がない。
- [ ] CG-01〜05（Consensus/Working契約）が Architecture と Ops に反映される。
- [ ] `safeMode` と `unreviewed` の後退表現が 0 件。
- [ ] Go/NoGo判定を1行で実施できる（Yes/No）。

## 5) 実装タスク分解 / Task breakdown

- [ ] T1: 契約IDマトリクス表を ADR-0028 に追加（ID, 意味, 適用層, 検証コマンド）。
- [ ] T2: `02_Architecture` の関連文書へ語彙同期（Core→Consensus, Working, autonomous mode）。
- [ ] T3: `04_Documentation/operations.md` に運用上の禁止事項（auto-apply禁止・review昇格禁止）を明文化。
- [ ] T4: ドリフト検知コマンド結果をIssue末尾へ記録。

## 6) 検証計画 / Validation plan

- 実行コマンド:
  - `rg -n "Guard-0[1-5]|CG-0[1-5]|Consensus Graph|Working Graph|autonomous" 01_Plans/adr 02_Architecture 04_Documentation`
  - `python 01_Plans/issues/validate_active_issue_memos.py`
- 期待結果:
  - 用語不一致がなく、validatorが成功する。
- 未実施時の理由・代替検証:
  - 未実施不可（CE-0 Gate条件）。

## 7) リスクとロールバック / Risks & rollback

- 失敗モード: 語彙同期不足によりCE-1以降のI/Fが多義化する。
- ロールバック: 変更文書を契約ID単位でrevertし、ADR-0028を正本として再同期。
