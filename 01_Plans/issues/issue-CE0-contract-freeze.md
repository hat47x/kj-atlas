# Issue Draft: CE0 Contract Freeze（Stream D / CE契約専任 / planning-only）

- Type: Process
- Status: Open
- Priority: P1
- Owner: Stream D（CE契約専任）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Related Backlog: `CE-0`
- Related ADR/Spec: `ADR-0028`, `02_Architecture/schemas.md`
- Verification: `docs-check`

## Lane guard（このレーンの絶対条件）
- 本Issueは**計画・契約先行のみ**を扱う。実装（`03_Implement/**`）は対象外。
- CE0契約IDは再定義禁止：`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`。
- 未承認決定を確定扱いしない（承認待ち論点は `held` 扱い）。
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

## Phase 2 CE0契約凍結（最優先）
- Contract ID collision = 0 を凍結条件とする。
- Vocabulary collision = 0 を凍結条件とする（`Consensus Graph / WorkingGraph / ContextProjectionGraph`）。
- CE1/CE2/CE4 は CE0契約を**参照のみ**で使用し、再定義しない。

## Phase 3 Plan（AC/DoD）
### Acceptance Criteria
- [ ] Contract ID collision = 0
- [ ] Vocabulary collision = 0
- [ ] SafeMode regression = 0
- [ ] No-Go語彙（direct write / auto-apply / preview bypass）一致

### Definition of Done
- [ ] 5 Issue間で契約語彙が単一正本化されている
- [ ] 実装依存記述を含まない
- [ ] `docs-check` で差分説明可能

## Phase 4 Verify（矛盾ゼロ検証）
- `docs-check`
- 5 Issue横断で `Contract ID / 禁止事項 / safeMode境界` の矛盾ゼロを確認。
- 自己修復は最大3回。4回目相当は停止。

## Phase 5 Proceed（実装ストリーム向けI/F配布）
### Implementation Input Freeze（I/F仕様書）
- `CE0-CTX-IF`
- `CE0-SAFEMODE-IF`
- `CE0-REVIEW-IF`
- `CG-01..05`

> Proceed条件: `collision=0` かつ `safeMode regression=0`。未達時は fail-safe 停止。
