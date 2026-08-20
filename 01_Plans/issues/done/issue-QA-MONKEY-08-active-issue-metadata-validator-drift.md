# Issue Draft: QA-MONKEY-08 Active issue metadata validator drift

- Type: Process / Documentation quality
- Status: Done
- Source Issue: N/A
- Priority: P2
- Owner: Codex
- Scope: `01_Plans/issues`
- Related Backlog: `QA-MONKEY-08`
- Related ADR/Spec: `01_Plans/adr/ADR-0000-adr-governance.md`, `01_Plans/issues/README.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: QA-MONKEY-08
- RequirementStatement: Active issue memo index and memo metadata must validate cleanly so new internal issues can be triaged reliably.
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=current active issue table / 操作=`python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` / 期待結果=no missing required fields and no index status/source mismatch / 除外=completed issue memos not listed in the active table.
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A

## 1) 課題 / Problem statement

- Running the active issue memo validator during monkey-test issue creation failed on existing HIL-RS active rows.
- Failures include missing required metadata fields and README index status/source mismatches.
- The new QA-MONKEY issue memos were adjusted to satisfy the validator, but the overall validator remains red due to pre-existing active memo drift.

## 2) 背景 / Context

- `ADR-0000` requires issue memo metadata and active index consistency.
- `01_Plans/issues/README.md` identifies the active table as the index source.
- The validator checks only active rows, so a red result blocks reliable active issue hygiene.

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: Internal issue management should be restartable and machine-checkable.
- 安全（THREAT_MODEL / SafeMode）: No direct safety impact, but process drift can hide safety-critical issue state.
- 企業・行政要件（enterprise_architecture）: Traceable issue state is needed for controlled operations.
- 後方互換（schemas）: Documentation/process metadata only.

## 4) 提案する解決策 / Proposed solution

- 変更対象: `01_Plans/issues` active HIL-RS memos and README active table.
- 変更の最小単位: Align required fields and index status/source for existing active rows without changing issue scope or decisions.
- 非目標: Re-deciding HIL-RS plan status or changing implementation tasks.

## 5) 受入条件 / Acceptance criteria

- [x] Active HIL-RS memos include required validator fields.
- [x] README active table status/source values match memo metadata.
- [x] `validate_active_issue_memos.py --root 01_Plans/issues` passes.
- [x] Validator unit tests pass.
- [x] Changes are limited to metadata/index hygiene, with no unapproved decision changes.

## 6) 実装タスク分解 / Task breakdown

- [x] T1 Review each validator failure and identify metadata-only fixes.
- [x] T2 Update active memo metadata or README rows consistently.
- [x] T3 Run validator and unit tests.
- [x] T4 Record any status decision ambiguity as a separate human decision queue item if needed.

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
- 期待結果:
  - Active issue memo validation passes with no metadata/index drift.
- 完了時の検証:
  - Active issue memo validator and validator unit tests pass on the current active table.

## 8) 代替案 / Alternatives considered

- 代替案A: Patch README rows to match current memo statuses immediately. Deferred because some statuses encode hold/approval semantics that may need owner confirmation.
- 代替案B: Ignore validator failures. Rejected because it weakens internal issue management.

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: Metadata cleanup could accidentally imply a status decision.
- 影響範囲: Internal issue triage and dashboard synchronization.
- ロールバック手順: Revert metadata/index changes and keep this issue Open until an owner resolves ambiguity.

## 10) Additional context

- ADR化が必要になる条件: Active issue lifecycle/status vocabulary is redefined.

## 11) Closeout

- Completed by: PR #2131 and PR #2132 resolved the active HIL-RS metadata/index drift; this memo is closed by the follow-up issue index cleanup.
- Result: active issue memo validation passes with no metadata/index drift on the remaining active rows.
- Validation:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` -> `ok: validated 7 active issue memos`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` -> `Ran 10 tests ... OK`
  - `git diff --check` -> no whitespace errors

---
