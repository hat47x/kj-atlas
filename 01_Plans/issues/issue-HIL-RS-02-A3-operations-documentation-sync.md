# Issue Draft: HIL-RS-02 A3 Operations/Documentation 同期

- Type: Documentation Planning
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: TBD
- Priority: P2
- Owner: Operations Owner (Stream B planning)
- Scope: `01_Plans/issues/issue-HIL-RS-02-A3-operations-documentation-sync.md`（issue本文のみ）
- Related Backlog: `HIL-RS-02`
- Related ADR/Spec: `ADR-0027`, `ADR-0019`, `02_Architecture/strict_mode_exception_approval_flow.md`
- Expected verification level: `docs-check`

## 1) 背景

A3は運用同期タスクだが、Stream Bは planning only のため、実体文書（`02_Architecture/*`, `04_Documentation/*`）を編集せず、Open化判定に必要な契約条件のみを issue 側で固定する。

## 2) 目的

A3のOpen化条件・停止条件・検証条件を **状態遷移契約** として明文化し、A1依存を実装待ちにしない。

## 3) Mock Contract Snapshot（固定識別子参照）

- Snapshot ID: `MOCK-CONTRACT-SNAPSHOT-HIL-RS-v1`
- Freeze Pack ID: `HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- Fixed Contract IDs:
  - `A1-CRITIQUE-IF`
  - `A1-REDIFF-IF`
  - `A1-ATTR-IF`
  - `A1-ERROR-IF`
- Fixed values:
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`

## 4) ADR CDC（Phase 2）

- Context:
  - A3は運用同期の出口だが、契約基準が曖昧だとOpen判定が人依存になる。
- Decision:
  - A3は `A1 Done && pendingDecisionQueueCount==0` のときのみ `Draft -> Open` を許可する。
- Consequences:
  - A3はA1契約をread-only参照し、契約変更要求はA1へ差し戻す。

## 5) State Transition Contract

- Allowed:
  - `A3: Draft -> Open` only if `A1==Done && Pending==0`
  - `DecisionQueue: Pending -> Approved | Rejected`
- Forbidden:
  - Pending bypass
  - A1未完了でのA3 Open
  - A3 issue内での契約再定義

## 6) 受入条件（AC）/ DoD

- AC-1: CDC（Context/Decision/Consequences）が明文化されている。
- AC-2: A3 Open化条件が機械判定式で示されている。
- AC-3: Decision Queue許可/禁止遷移が示されている。
- AC-4: 安全境界（SafeMode既定ON / share-export漏えい防止 / `human_dual_control_only`）後退禁止が明示されている。
- AC-5: Verify失敗時の自己修復上限3回が定義されている。
- AC-6: Stream Bの編集境界（issue本文のみ）が明示されている。

## 7) Stream B 強制サイクル（各Phase開始時に再Read）

### Phase 1 Read
- 対象5 issue再Read、依存・識別子・遷移条件を棚卸し。

### Phase 2 ADR CDC
- CDCを固定。上位ADR改定が必要なら停止（承認待ち）。

### Phase 3 Plan
- AC/DoD不足を補完。Open化条件と停止条件を明文化。

### Phase 4 Execute
- 本issue本文のみ更新（契約識別子、遷移、禁止事項、Proceed条件）。

### Phase 5 Verify
- `python 01_Plans/issues/validate_active_issue_memos.py`
- `rg -n "A1 Done|pendingDecisionQueueCount|Pending -> Approved|Pending -> Rejected|human_dual_control_only|schemaVersion=1.0.0" 01_Plans/issues/issue-HIL-RS-02-A3-operations-documentation-sync.md`
- 検証失敗は自己修復最大3回。超過で停止。

### Phase 6 Proceed
- Open化条件を満たした場合のみA3をOpen候補に進める。未確定はDecision Queueへ戻す。

## 8) Open化条件（明文化）

1. `A1==Done`
2. `pendingDecisionQueueCount==0`
3. Mock snapshot固定識別子一致
4. 安全境界後退要求なし

## 9) 停止条件

1. 検証失敗の自己修復3回超過
2. 未承認決定の確定化
3. 固定識別子不一致
4. 編集境界違反（issue本文以外を変更しようとした場合）
