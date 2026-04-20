# Issue Draft: CE1 ContextQuery/ContextBundle Foundation（Stream B / CE契約群 / contract-only planning）

- Type: Feature request
- Status: Open
- Priority: P1
- Owner: Stream B（CE契約群）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Editable: `issue-CE1-context-query-bundle-foundation.md` のみ
- Related Backlog: `CE-1`
- Related ADR/Spec: `ADR-0028`, `02_Architecture/schemas.md`
- Verification: `docs-check`

## Lane guard（独立性）
- CE1は **I/F凍結のみ**。実装記述（handler/UI/DB/worker）は扱わない。
- CE0契約参照は必須、CE1側で再定義しない。
- 強制ワークフローは `Phase 1 Read → Phase 2 I/F Mock Freeze → Phase 3 ADR CDC → Phase 4 Plan→Execute→Verify → Phase 5 Proceed`。

## Phase 1 Read（全対象Read: Status / Scope / Related ADR確認）
### Contract IDs（凍結対象）
- `CE1-CTXQ-IF`（ContextQueryV1）
- `CE1-CTXB-IF`（ContextBundleV1）
- `CE1-HASH-DET-IF`（hash決定論）
- `CE1-PREVIEW-GATE-IF`（preview gate）

### Error semantics（語彙固定）
- `preview_required`
- `unknown_contract_key`
- `nondeterministic_bundle`

### No-Go / safeMode境界
- Query Preview bypass 禁止。
- `CE0-SAFEMODE-IF` を参照し、CE1側でsafeMode既定を再定義しない。

## Phase 2 I/F Mock Freeze（ContextQuery / ContextBundle / Review 境界をI/Fのみ固定）
- CE2連携境界: `sourceBundleHash === bundleHash` 比較キーのみを提供。
- CE4連携境界: `equivalenceKey/queryCanonicalHash/bundleHash` を引き渡す。
- CE1 v1 は closed-world を維持し、拡張は v2再起票のみ。
- 参照境界は CE0 (`CE0-CTX-IF`/`CE0-SAFEMODE-IF`) 参照のみで固定。

## Phase 3 ADR CDC（方針差分時のみ Context / Decision / Consequences を記録し承認待ち）
- **Context**: hash決定論・preview gate・closed-world の衝突有無。
- **Decision**: v1語彙固定、未定義キー拒否、preview必須を維持。
- **Consequences**: CE2/CE4 が `sourceBundleHash === bundleHash` に依存可能。
- **Approval**: 差分発生時の反映状態は `held`。

## Phase 4 Plan→Execute→Verify（AC/DoD補完 + docs-check自己検証）
### Plan
- `previewConfirmed=false -> 422 preview_required` を明示。
- unknown key -> `400 unknown_contract_key` を明示。
- 同一 canonical query で `queryCanonicalHash/bundleHash` 一致を要件化。

### Execute
- collision=0 / safeMode regression=0 を満たす記述へ整理。
- 検証失敗時は自己修復を最大3回まで、4回目相当は停止。

### Verify
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`

### Acceptance Criteria / DoD
- [ ] 同一 canonical query 3回で `queryCanonicalHash` が一致
- [ ] 同一 canonical query 3回で `bundleHash` が一致
- [ ] `previewConfirmed=false` は常に `422 preview_required`
- [ ] 未定義キー入力は常に `400 unknown_contract_key`
- [ ] SafeMode regression = 0

## Phase 5 Proceed（次工程向け固定契約の出力）
### Fixed contract handoff
- Contract IDs: `CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`
- 禁止事項: preview bypass / safeMode緩和 / 未定義キー黙認
- 検証条件: hash決定論一致, preview gate強制, docs-check pass

## Fail-safe（即停止条件）
- Self-Correction 3回超過
- 未定義ファイル競合
- SafeMode後退の兆候
- 依存前提崩壊
