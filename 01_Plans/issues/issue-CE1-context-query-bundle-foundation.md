# Issue Draft: CE1 ContextQuery/ContextBundle Foundation（Stream D / planning-only）

- Type: Feature request
- Status: Open
- Priority: P1
- Owner: Stream D
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Related Backlog: `CE-1`
- Related ADR/Spec: `ADR-0028`, `02_Architecture/schemas.md`
- Verification: `docs-check`

## Lane guard
- CE1は最小I/F凍結タスク。実装記述（handler/UI/DB）は扱わない。
- 実装指示混入時は停止。

## Phase 1 Read（契約I/F抽出）
### Contract IDs
- `CE1-CTXQ-IF`
- `CE1-CTXB-IF`
- `CE1-HASH-DET-IF`
- `CE1-PREVIEW-GATE-IF`

### 固定仕様
- Query Preview必須（`previewConfirmed=false -> 422 preview_required`）
- closed-world（未定義キーは `400 unknown_contract_key`）
- deterministic hash（同一canonical queryで再実行一致）

## Phase 2 Plan（AC/DoD不足ドラフト）
### AC Draft
- [ ] 同一query 3回で `queryCanonicalHash` 一致
- [ ] 同一query 3回で `bundleHash` 一致
- [ ] `previewConfirmed=false` は常に422
- [ ] unknown key は常に400

### DoD Draft
- [ ] CE2/CE4 が `sourceBundleHash===bundleHash` 比較可能
- [ ] v1に未定義キー追加なし（拡張はv2のみ）

## Phase 3 Execute（依存正規化）
- CE2/CE4は mock `ContextQuery/ContextBundle` で先行可能（実装待機禁止）。
- CE1の成果物は read-only handoff 契約として固定。

## Phase 4 Verify
- `docs-check`
- 5 Issue横断で CE1 error semantics と hash決定論の語彙不一致=0。

## Phase 5 Proceed（実装入力固定）
### I/F仕様書固定
- `ContextQueryV1`
- `ContextBundleV1`
- Error semantics: `preview_required` / `nondeterministic_bundle` / `unknown_contract_key`
