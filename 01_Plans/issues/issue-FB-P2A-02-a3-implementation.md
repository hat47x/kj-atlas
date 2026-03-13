# Issue Draft: FB-P2A-02-A3 Collapse/Expand操作 / 実装計画接続

- Type: Feature request
- Status: Draft (起票用)
- Priority: P0
- Owner: Stream C
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2A-02`
- Related ADR/Spec: `ADR-0007`, `issue-FB-P2A-02-a1-interface-contract.md`, `issue-FB-P2A-02-a2-mock-validation.md`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2A-02`
- RequirementStatement: A1/A2契約を逸脱せず、Collapse/Expand実装計画へ接続する。
- Phase: `A3 Implementation`
- PriorityClass: Must
- GoNoGoGate: Required
- VerificationLevel: integration
- DecisionStatus: Fixed

## Execution protocol（Plan→Execute→Verify→Proceed）

1. **Plan**
   - `isCollapsed` と `hidden*Ids` の更新責務を分離して作業計画化。
2. **Execute**
   - `state transition -> render filter -> hit-test filter` の順で設計反映。
3. **Verify**
   - A2 mockCaseを使って遷移前後の整合をチェック。
4. **Proceed**
   - GoNoGoを満たした観点のみ次タスクへ進行。

## Non-deviation rules

- A1契約をA3で再解釈しない。
- A2 Failケースを未解決のまま先送りしない。
- AC/DoD不足を検知した場合は、先にドラフト提案を追記して合意後に進行する。

## Phase 4 Verify/Handoff

- AC/DoD達成判定:
  - A1契約項目とA2モック結果がA3手順へトレース可能であること。
- 未達記録:
  - `mockCaseId`, `failurePoint`, `ownerOfFix`, `nextAction` を残す。
- ロールバック条件:
  - collapse/expandでdocument構造改変が発生した場合は実装接続を停止し巻き戻す。
- 次Phase入力:
  - `render/hit-test regression targets`, `remaining edge cases`, `handoff risks` を引き継ぐ。

## Acceptance criteria

- [ ] A1/A2契約IDで実装計画トレースが可能。
- [ ] Plan→Execute→Verify→Proceedの順序が固定される。
- [ ] AC/DoD不足時のドラフト提案手順が明文化される。
- [ ] Verify/Handoff（達成判定・未達・ロールバック・次入力）が記録される。

## State sync / conflict check

- Phase開始時Read対象:
  - `issue-FB-P2A-02-a1-interface-contract.md`
  - `issue-FB-P2A-02-a2-mock-validation.md`
  - `issue-FB-P2A-02-a3-implementation.md`

## Validation plan

- Command:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`

## Fail-safe

- 自己修復が3回連続で失敗、またはA1/A2契約リンク不整合を検出した場合は停止して指示待ち。
