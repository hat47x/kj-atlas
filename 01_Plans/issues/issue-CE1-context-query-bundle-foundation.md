# Issue Draft: CE1 ContextQuery/ContextBundle Foundation（Stream D / planning-only）

- Type: Feature request
- Status: Open
- Priority: P1
- Owner: Stream D（CE1専属）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Related Backlog: `CE-1`
- Related ADR/Spec: `ADR-0028`, `02_Architecture/schemas.md`
- Verification: `docs-check`

## Lane guard（独立性）
- CE1は **I/F凍結のみ**。実装記述（handler/UI/DB/worker）は扱わない。
- 編集許可は本Issueのみ。指定外編集が必要になった時点で停止・報告。
- モック依存切断: 実装待ちを禁止し、mock hash前提で契約検証を完了させる。

---

## Phase 1 Read（契約IDと error semantics 確認）

### Contract IDs（凍結対象）
- `CE1-CTXQ-IF`（ContextQueryV1）
- `CE1-CTXB-IF`（ContextBundleV1）
- `CE1-HASH-DET-IF`（hash決定論）
- `CE1-PREVIEW-GATE-IF`（preview gate）

### Error semantics（語彙固定）
- `preview_required`
- `unknown_contract_key`
- `nondeterministic_bundle`

### 判定原則
- Query Preview必須: `previewConfirmed=false` は常に `422 preview_required`。
- closed-world: 未定義キーが1つでも存在した場合は常に `400 unknown_contract_key`。
- deterministic hash: 同一 canonical query は再実行しても `queryCanonicalHash` / `bundleHash` が一致。

---

## Phase 2 ADR CDC（必要時のみ）
- 現時点は ADR 更新不要（CDCなし）。
- ただし以下のいずれかが発生した場合のみ ADR CDC を起票:
  - v1契約に新規キーを追加する必要が生じた場合
  - error semantics の語彙追加/変更が必要な場合
  - hash決定論の前提（canonicalization規則）に変更が必要な場合

---

## Phase 3 Plan（AC/DoD補完）

### Acceptance Criteria（AC）
- [ ] 同一 canonical query を3回評価し、`queryCanonicalHash` が完全一致する。
- [ ] 同一 canonical query を3回評価し、`bundleHash` が完全一致する。
- [ ] `previewConfirmed=false` は入力差分に関係なく常に `422 preview_required` を返す。
- [ ] v1未定義キーを含む入力は常に `400 unknown_contract_key` を返す。
- [ ] `nondeterministic_bundle` は「同一 canonical query で hash 不一致」が観測されたときのみ使用する。

### Definition of Done（DoD）
- [ ] CE2/CE4 が `sourceBundleHash === bundleHash` 比較で依存可能な契約が明文化されている。
- [ ] `ContextQueryV1` / `ContextBundleV1` の語彙は本Issue内で一意（同義語/別名なし）。
- [ ] v1契約は closed-world とし、拡張は v2 でのみ実施する方針を明文化。
- [ ] mock hash を使った検証手順で、実装待機なしに契約確認できる。

---

## Phase 4 Execute（I/F凍結: closed-world / preview gate / hash決定論）

### ContextQueryV1（契約制約）
- 必須ゲート: `previewConfirmed=true` のときのみ評価可能。
- closed-world: 許可キー集合外のキーは受理しない。
- canonicalization: 同一意味のqueryは同一 canonical form に正規化される前提で hash算出する。

### ContextBundleV1（契約制約）
- `bundleHash` は canonical query と deterministic 生成規則から一意決定される。
- `sourceBundleHash` 比較対象として downstream（CE2/CE4）が参照できる。
- hash不一致検出時は `nondeterministic_bundle` を返し、成功レスポンスにフォールバックしない。

### Mock-first 契約検証（実装待ち禁止）
- 検証入力は mock `ContextQuery/ContextBundle` を用いる。
- 判定は hash一致性と error semantics のみで実施し、実データ生成可否を判定条件に含めない。
- CE1成果物は read-only handoff 契約として固定する。

---

## Phase 5 Verify / Proceed（語彙衝突ゼロで実装入力固定）

### Verify
- `docs-check`
- 5 Issue横断レビュー時、CE1関連語彙（contract ID / error semantics / hash用語）の衝突数を `0` にする。

### Proceed（実装入力）
- I/F仕様書入力名を以下で固定:
  - `ContextQueryV1`
  - `ContextBundleV1`
- Error semantics を以下3語で固定:
  - `preview_required`
  - `unknown_contract_key`
  - `nondeterministic_bundle`

---

## Fail-safe
- 自己修復は最大3回まで。
- 3回超過時は作業停止し、失敗要因（語彙衝突/契約未確定/外部依存）を明示して報告する。
