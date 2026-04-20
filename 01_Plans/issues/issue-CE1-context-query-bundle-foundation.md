# Issue Draft: CE1 ContextQuery/ContextBundle Foundation（Stream C / contract-only planning）

- Type: Feature request
- Status: Open
- Priority: P1
- Owner: Stream C（CE1専属）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Editable: `issue-CE1-context-query-bundle-foundation.md` のみ
- Related Backlog: `CE-1`
- Related ADR/Spec: `ADR-0028`, `02_Architecture/schemas.md`
- Verification: `docs-check`

## Lane guard（独立性）
- CE1は **I/F凍結のみ**。実装記述（handler/UI/DB/worker）は扱わない。
- CE0契約参照は必須、CE1側で再定義しない。
- safeMode後退、auto-apply許容、未承認確定化を検知したら即停止。
- 強制ワークフローは `Plan → Execute → Verify → Proceed`。

## Phase 1) Read（CE0契約ID群・NoGo語彙・safeMode境界の再確認）
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

## Phase 2) Plan（CE1/CE2/CE4への参照境界を再定義なしで設計）
- CE2連携境界: `sourceBundleHash === bundleHash` 比較キーのみを提供。
- CE4連携境界: `equivalenceKey/queryCanonicalHash/bundleHash` を引き渡す。
- CE1 v1 は closed-world を維持し、拡張は v2再起票のみ。
- 参照境界は CE0 (`CE0-CTX-IF`/`CE0-SAFEMODE-IF`) 参照のみで固定。

## Phase 3) ADR CDC（変更時のみ Context / Decision / Consequences を明文化）
- **Context**: hash決定論・preview gate・closed-world の衝突有無。
- **Decision**: v1語彙固定、未定義キー拒否、preview必須を維持。
- **Consequences**: CE2/CE4 が `sourceBundleHash === bundleHash` に依存可能。
- 変更がない場合は CDC更新を行わない。

## Phase 4) Execute（collision=0 / safeMode regression=0 を満たす整理）
- `previewConfirmed=false -> 422 preview_required` を明示。
- unknown key -> `400 unknown_contract_key` を明示。
- 同一 canonical query で `queryCanonicalHash/bundleHash` 一致を要件化。
- 検証失敗時は自己修復を最大3回まで、4回目相当は停止。

## Phase 5) Verify / Proceed（docs-check と再開条件の記録）
### Acceptance Criteria
- [ ] 同一 canonical query 3回で `queryCanonicalHash` が一致
- [ ] 同一 canonical query 3回で `bundleHash` が一致
- [ ] `previewConfirmed=false` は常に `422 preview_required`
- [ ] 未定義キー入力は常に `400 unknown_contract_key`
- [ ] SafeMode regression = 0

### Verify
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`

### Proceed（再開条件）
- 再開条件1: CE2/CE4連携キーが再定義なしで参照可能。
- 再開条件2: hash決定論とpreview gateが衝突ゼロ。
- 再開条件3: fail-safe検知時は停止→原因切り分け→3回以内に自己修復。
