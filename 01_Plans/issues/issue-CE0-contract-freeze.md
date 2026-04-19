# Issue Draft: CE0 Contract Freeze（Stream D / planning-only）

- Type: Process
- Status: Open
- Priority: P1
- Owner: Stream D
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Related Backlog: `CE-0`
- Related ADR/Spec: `ADR-0028`, `02_Architecture/schemas.md`
- Verification: `docs-check`

## Lane guard（このレーンの絶対条件）
- 本Issueは**計画・契約先行のみ**を扱う。実装（`03_Implement/**`）は対象外。
- CE0契約IDは再定義禁止：`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`。
- 実装指示が混入した場合は **Stop**（planning lane fail-safe）。

## Phase 1 Read（契約I/F抽出）
### 固定I/F
- `CE0-CTX-IF`: ContextQuery必須キーと deterministic `bundleHash`。
- `CE0-SAFEMODE-IF`: safeMode既定ON、`allowUnreviewedText=false` 既定。
- `CE0-REVIEW-IF`: `human_reviewed` 昇格は人手のみ。
- `CG-01..05`: `Working -> Consensus` は `patch + approval` のみ。

### 禁止事項
- Query Preview bypass
- Consensus direct write
- auto-apply
- AIによる review 自動昇格
- safeMode既定緩和

## Phase 2 Plan（AC/DoD不足の補強案）
### AC Draft
- [ ] Contract ID collision = 0
- [ ] Vocabulary collision = 0（`Consensus Graph/WorkingGraph/ContextProjectionGraph`）
- [ ] SafeMode regression = 0
- [ ] No-Go語彙（direct write / auto-apply / preview bypass）一致

### DoD Draft
- [ ] 5 Issue間で契約語彙が単一正本化されている
- [ ] 実装依存記述を含まない
- [ ] docs-checkで差分説明可能

## Phase 3 Execute（依存のI/F正規化・mock前提）
- CE1/CE2/CE4は `sourceBundleHash=mock:<hash>` を許容し、CE0は待機しない。
- CE0は「参照専用契約」のみ提供し、下流からの契約再定義要求を受理しない。

## Phase 4 Verify（矛盾ゼロ検証）
- `docs-check`
- 5 Issue横断で `Contract ID / 禁止事項 / safeMode境界` の矛盾ゼロを確認。
- 自己修復は最大3回。4回目相当は停止。

## Phase 5 Proceed（次の実装入力を固定）
### Implementation Input Freeze（I/F仕様書）
- `CE0-CTX-IF`
- `CE0-SAFEMODE-IF`
- `CE0-REVIEW-IF`
- `CG-01..05`

> Proceed条件: `collision=0` かつ `safeMode regression=0`。未達時は fail-safe 停止。
