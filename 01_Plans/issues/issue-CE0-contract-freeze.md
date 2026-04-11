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

## 3) 受入条件 / Acceptance criteria

- [ ] ACCIの5段手順が 01/02/04 で同語彙定義される。
- [ ] Guard-01〜05 の意味が文書間で一致し、禁止事項に矛盾がない。
- [ ] CG-01〜05（Consensus/Working契約）が Architecture と Ops に反映される。
- [ ] `safeMode` と `unreviewed` の後退表現が 0 件。
- [ ] Go/NoGo判定を1行で実施できる（Yes/No）。

## 4) 実装タスク分解 / Task breakdown

- [ ] T1: 契約IDマトリクス表を ADR-0028 に追加（ID, 意味, 適用層, 検証コマンド）。
- [ ] T2: `02_Architecture` の関連文書へ語彙同期（Core→Consensus, Working, autonomous mode）。
- [ ] T3: `04_Documentation/operations.md` に運用上の禁止事項（auto-apply禁止・review昇格禁止）を明文化。
- [ ] T4: ドリフト検知コマンド結果をIssue末尾へ記録。

## 5) 検証計画 / Validation plan

- 実行コマンド:
  - `rg -n "Guard-0[1-5]|CG-0[1-5]|Consensus Graph|Working Graph|autonomous" 01_Plans/adr 02_Architecture 04_Documentation`
  - `python 01_Plans/issues/validate_active_issue_memos.py`
- 期待結果:
  - 用語不一致がなく、validatorが成功する。
- 未実施時の理由・代替検証:
  - 未実施不可（CE-0 Gate条件）。

## 6) リスクとロールバック / Risks & rollback

- 失敗モード: 語彙同期不足によりCE-1以降のI/Fが多義化する。
- ロールバック: 変更文書を契約ID単位でrevertし、ADR-0028を正本として再同期。
