# Issue Draft: HIL-RS-02 次フェーズ実行計画（議論→意思決定→文書化→同期）

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Plan Owner
- Scope: `01_Plans/`, `02_Architecture/`, `04_Documentation/`
- Related Backlog: `HIL-RS-02`
- Related ADR/Spec: `ADR-0027`, `ADR-0026`, `00_Prompt/domain.md`, `02_Architecture/architecture.md`, `02_Architecture/schemas.md`
- Expected verification level: `docs-check`

## 1) 背景

- HIL-RS-01で契約先行は固定済みだが、次フェーズの会議ログ→ADR→Issue→dashboard同期の実行導線が分散している。

## 2) 目的

- 次フェーズの意思決定を実行可能な最小単位へ分解し、依存順（A1→A2→A3）を固定する。

## 3) スコープ

- 議事録作成、ADR起票、Issue分解、dashboard/README同期。

## 4) 非スコープ

- frontend/backendの実装変更。
- SafeMode・漏洩防止・責務分離ルールの緩和。

## 5) 受入条件

- AC-1: 議事録が作成され、論点ごとに「提案/懸念/反証/結論」がある。
- AC-2: ADR-0027が Accepted で、Exit Criteriaを含む。
- AC-3: HIL-RS-02-A1/A2/A3 issueが作成され、依存順が明示される。
- AC-4: `issues/README.md` と `project-progress-dashboard.md` の件数・Decision Queue・次の1手が同期される。

## 6) 検証方法

- `python 01_Plans/issues/validate_active_issue_memos.py`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`

## 7) 依存関係

- `ADR-0026`（上位方針）
- `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`（契約固定）

## 8) リスク

- Active issue増加に伴う同期漏れ。
- 人間承認前にDraftを確定扱いする運用逸脱。

## 9) 着手順（クリティカルパス）

1. 議事録作成
2. ADR-0027固定
3. A1 issue Open
4. A2/A3 issue Draft
5. dashboard同期


## 10) Stream A A1 gate（固定）

- 依存順の強制: A1→A2→A3 を厳守し、A1完了前にA2/A3をOpen化しない。
- A1停止条件:
  - 未承認の契約変更要求を確定扱いした場合。
  - SafeMode既定ON / share-export漏えい防止 / `human_dual_control_only` の後退が前提となる場合。
- A1再開条件:
  - 変更要求がDecision Queueへ `Pending` 登録され、承認ログが追記された場合。
  - A1差し戻し経路（A1 issue記載）で再判定が完了した場合。
- A2開始条件（Ready）:
  1. A1契約ID/`schemaVersion`/`overridePolicy`がSSOTと一致。
  2. `contractLinkLocked=true` / `sharedResourceFreeze=true` が維持。
  3. Decision QueueのPending項目に対する承認記録が揃う。
  4. A1で凍結した変更禁止項目（SafeMode既定ON / human_dual_control_only / share-export漏えい防止）をA2/A3が変更しない。
- Block理由:
  - 未承認の契約変更要求を確定扱いした場合。
  - SafeMode既定ONまたはshare/export漏えい防止後退が前提となる場合。
  - Decision Queue項目がPending管理を外れている場合。
