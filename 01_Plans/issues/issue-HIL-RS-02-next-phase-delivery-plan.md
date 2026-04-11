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
- `rg -n "SafeMode|share/export|human_dual_control_only|A1→A2→A3|contractLinkLocked|sharedResourceFreeze" 01_Plans/issues/issue-HIL-RS-02-*.md 01_Plans/adr/ADR-0027-hil-rs-02-next-phase-execution-plan.md 02_Architecture/strict_mode_exception_approval_flow.md`

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
- A1 Decision Queue運用固定:
  - Queue項目は `Pending -> Approved|Rejected` 以外の遷移を許可しない。
  - `Pending` 項目が1件でも残る間はA2/A3をOpen化しない。
  - Queue更新時は `Owner / UTC timestamp / evidenceLink` を必須記録する。
- A2開始条件（Ready）:
  1. A1契約ID/`schemaVersion`/`overridePolicy`がSSOTと一致。
  2. `contractLinkLocked=true` / `sharedResourceFreeze=true` が維持。
  3. Decision QueueのPending項目に対する承認記録が揃う。
  4. A1で凍結した変更禁止項目（SafeMode既定ON / human_dual_control_only / share-export漏えい防止）をA2/A3が変更しない。
- Block理由:
  - 未承認の契約変更要求を確定扱いした場合。
  - SafeMode既定ONまたはshare/export漏えい防止後退が前提となる場合。
  - Decision Queue項目がPending管理を外れている場合。


## 11) A2/A3参照用「凍結契約パック」（read-only）

- Freeze-ID: `HIL-RS-01-A1-CONTRACT-FREEZE-v1`
- Package mode: read-only（A2/A3は参照のみ、変更要求はA1へ差し戻し）
- Contents:
  1. Invariant-01: SafeMode既定ONを維持。
  2. Invariant-02: share/export漏えい防止ポリシーを後退させない。
  3. Invariant-03: `human_dual_control_only` を維持し、単独承認へ緩和しない。
  4. Invariant-04: `contractLinkLocked=true` / `sharedResourceFreeze=true`。
  5. Invariant-05: `schemaVersion` / `overridePolicy` / 契約ID整合を維持。
  6. Invariant-06: `A1-ERROR-IF` のerrorCode列挙を固定し、A2/A3で拡張しない。
- Return path: 変更要求は必ず A1 issue の Decision Queue に `Pending` で登録して再判定する。

## 11.1) 変更理由・影響範囲・非対応範囲（固定）

- 変更理由:
  - HIL-RS-02で議論/実装導線が先行して契約解釈が分岐することを防ぐため。
- 影響範囲:
  - A2/A3のOpen判定、Decision Queue運用、A1差し戻し経路の運用判定。
- 非対応範囲:
  - `03_Implement/**` の変更。
  - `schemaVersion` / `overridePolicy` / 契約IDの再定義。


## 12) Context / Decision / Consequences（凍結I/F合意）

### Context

- HIL-RS-02 は A1で契約/統治を先に固定し、A2/A3を参照専用で進める前提である。
- A1未完了のまま A2/A3 を Open 化すると、契約ID・停止条件・Decision Queue運用の解釈が分岐する。

### Decision

- Freeze Pack `HIL-RS-01-A1-CONTRACT-FREEZE-v1` を本issueでも正本参照として固定する。
- A2/A3の `Draft -> Open` は `A1 Done` かつ `DecisionQueue Pending=0` のときのみ許可する。
- 変更禁止対象（契約ID/schemaVersion/overridePolicy/SSOT/stop条件）の変更要求は A1 へ差し戻す。

### Consequences

- 契約変更の窓口がA1へ一本化され、A2/A3の実装側での仕様分岐を抑止できる。
- Pendingが残る間はOpen化できないため、短期スループットより監査性を優先する。

## 13) Gate rule（machine-evaluable）

- `freezeContractId=="HIL-RS-01-A1-CONTRACT-FREEZE-v1"`
- `schemaVersion=="1.0.0"`
- `contractLinkLocked==true`
- `sharedResourceFreeze==true`
- `a1Status=="Done"`
- `pendingDecisionQueueCount==0`
- `hasUndefinedContractChangeRequest==false`
- `hasSafeModeRegressionRequest==false`
- `hasShareExportLeakageRelaxationRequest==false`

判定:
- Ready: 全条件が真。
- Block: 1条件でも偽。
