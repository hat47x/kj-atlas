# Issue Draft: CE0 Core Graph Repositioning（Stream B / CE契約専任 / planning-only）

- Type: Process
- Status: Open
- Priority: P1
- Owner: Stream B（CE契約専任）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Related Backlog: `CE-0`
- Related ADR/Spec: `ADR-0028`, `02_Architecture/schemas.md`
- Verification: `docs-check`

## Lane guard
- 本Issueは Core Graph責務境界の**契約固定のみ**を扱う（実装禁止）。
- 未承認決定は `held` 扱いとし、確定扱いしない。
- safeMode後退・自動確定化（auto-apply/auto-publish）を禁止する。
- 実装指示混入時は停止。

## Phase 1) Read同期（ADR-0028整合確認）
### Graph role I/F
- `working`: 編集作業領域
- `context_projection`: read-only投影
- `consensus`: 承認済み合意領域

### Transition I/F
- 許可: `working -> consensus` は `patch+approval` のみ
- 禁止: direct write / auto-apply

### Audit I/F
- 必須4点: `query / bundle / proposal / apply`

## Phase 2) Plan（AC/DoD不足時の提案）
- AC不足時は「役割一致」「遷移一致」「監査欠損ゼロ」「safeMode後退ゼロ」を補強する。
- DoD不足時は「語彙二重定義なし」「3層説明可能（役割/遷移/監査）」「3回以内の自己修復」を補強する。
- 補強提案は CE0既存契約 `CG-01..05` の参照に限定し、再定義しない。

## Phase 3) ADR CDC（必要時のみ: CE0契約凍結）
- `CG-01..05` を本Issue側で再定義せず参照に統一する。
- Vocabulary固定: `WorkingGraph / ContextProjectionGraph / Consensus Graph`。
- 承認前は `held`、承認後のみ `frozen` と記録する。

## Phase 4) Execute（Issue粒度・依存・検証計画の確定）
### CE1/CE2のmock前提I/F分離
- CE1: `context_projection` は read-only参照のみ（生成元変更不可）。
- CE2: proposal lifecycle は `working` 領域に限定し、`consensus` 直更新禁止。
- mock検証時も遷移規則（patch+approval only）を省略しない。

### CE4連携契約（API/CLI/Audit）定義
- API/CLI/GUIの監査導線は `query/bundle/proposal/apply` を共通必須。
- `dryRun=true` は `sideEffect=none` に固定。
- `context_projection` の書換操作は監査失敗として扱う（fail-closed）。

## Phase 5) Verify / Proceed（検証可能性・再開可能性チェック）
### Acceptance Criteria
- [ ] `working -> consensus = patch+approval only` が全Issue一致
- [ ] `context_projection` read-only が全Issue一致
- [ ] 監査4点欠損=0
- [ ] SafeMode regression = 0

### Definition of Done
- [ ] Core/Consensus語彙の二重定義なし
- [ ] 役割・遷移・監査の3層で説明可能
- [ ] self-heal 3回以内

### Verify
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`

### Proceed（実装ストリーム向けI/F配布）
- GraphRole: `working | context_projection | consensus`
- Transition: `working -> consensus via patch+approval`
- AuditEnvelope: `query/bundle/proposal/apply` 必須
