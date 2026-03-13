# Issue Draft: FB-P2A-02-A2 Collapse/Expand操作 / モック検証

- Type: Feature request
- Status: Draft (起票用)
- Priority: P0
- Owner: Stream C
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2A-02`
- Related ADR/Spec: `ADR-0007`, `issue-FB-P2A-02-a1-interface-contract.md`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2A-02`
- RequirementStatement: A1で固定した `IslandVisibilityContractV1` をモックで検証する。
- Phase: `A2 Mock Validation`
- PriorityClass: Must
- GoNoGoGate: Required
- VerificationLevel: integration
- DecisionStatus: Fixed

## Mock validation scope

- 入力モック:
  - M1: 親island collapse（子island + cardsが非表示になる）
  - M2: expand復帰（非表示対象が復元）
  - M3: 二重collapse要求（冪等）
  - M4: 存在しないislandへのcollapse要求（拒否）
- 期待判定:
  - M1/M2/M3は契約適合。
  - M4はFail Fastで拒否。

## Fail Fast boundary（明文化）

- 不正対象IDは state transition 実行前に拒否する。
- M4は `validationResult=Rejected` を固定し、描画系ロジックへ入力しない。
- 判定不能（仕様不備）の場合のみ `ownerOfFix=A1` とし、それ以外はA2で即時修正する。

## Responsibility split（失敗時責務分離）

- 契約修正責務（A1）:
  - `hidden*Ids` 定義不足で期待挙動を一意に決められない。
- モック修正責務（A2）:
  - モック前提の不備、または判定期待値の誤設定。
- 実装修正責務（A3）:
  - 契約とモックは成立しているが実装計画に落ちていない。

## Acceptance criteria

- [ ] collapse/expandの正常系・異常系モックが揃う。
- [ ] 失敗時責務分離ルールが明文化される。
- [ ] A3へ渡す検証ログ項目が定義される。

## A3 handoff I/F

- Handoff payload:
  - `contractVersion`
  - `mockCaseId`
  - `validationResult`
  - `ownerOfFix`

## State sync / conflict check

- Phase開始時Read対象:
  - `issue-FB-P2A-02-a1-interface-contract.md`
  - `issue-FB-P2A-02-a2-mock-validation.md`
  - `issue-FB-P2A-02-a3-implementation.md`

## Validation plan

- Command:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`

## Fail-safe

- 自己修復が3回連続で失敗、またはA1契約リンク切れを検出した場合は停止して指示待ち。
