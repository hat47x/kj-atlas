# Issue Draft: FB-P2A-01-A2 Island階層モデル導入 / モック検証

- Type: Feature request
- Status: Draft (起票用)
- Priority: P0
- Owner: Stream B
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2A-01`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`, `issue-FB-P2A-01-a1-interface-contract.md`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2A-01`
- RequirementStatement: A1で固定した `IslandHierarchyContractV1` の妥当性をモックで検証する。
- Phase: `A2 Mock Validation`
- PriorityClass（Must / Should / Could）: Must
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact: N/A（計画のみ）
- VerificationLevel: integration
- DecisionStatus: Fixed

## Mock validation scope

- 入力モック:
  - M1: root island（`parentIslandId=null`）
  - M2: 3階層ネスト（root→child→grandchild）
  - M3: 不正参照（存在しない`parentIslandId`）
  - M4: 循環参照（A→B→A）
- 期待判定:
  - M1/M2は契約適合。
  - M3/M4はFail Fastで拒否。

## Responsibility split（失敗時責務分離）

- 契約修正責務（A1へ戻す）:
  - Required fieldsやInvariant自体が不足/矛盾している。
- モック修正責務（A2内で完結）:
  - モックデータが契約条件を満たしていない、またはテスト観点漏れ。
- 実装修正責務（A3へ引き継ぎ）:
  - 契約・モックは妥当だが、実装計画に反映されていない。

## Acceptance criteria

- [ ] A1契約を変更せずにモック検証ケースを定義できる。
- [ ] 正常系/異常系の判定基準が明示される。
- [ ] 失敗時に「契約修正 or モック修正」の切り分けルールが記録される。
- [ ] A3へ渡す検証ログ項目（入力/期待/結果/責務）が定義される。

## A3 handoff I/F

- Handoff payload:
  - `contractVersion`
  - `mockCaseId`
  - `validationResult`
  - `ownerOfFix`（`A1` / `A2` / `A3`）

## State sync / conflict check

- Phase開始時Read対象:
  - `issue-FB-P2A-01-a1-interface-contract.md`
  - `issue-FB-P2A-01-a2-mock-validation.md`
  - `issue-FB-P2A-01-a3-implementation.md`

## Validation plan

- Command:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`

## Fail-safe

- 自己修復が3回連続で失敗、またはA1契約リンク切れを検出した場合は停止して指示待ち。
