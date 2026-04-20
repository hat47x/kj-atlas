# Issue Draft: CE4 API/CLI/監査統合（Stream F / CE4専任 / contract-only planning）

- Type: Feature request
- Status: Open
- Priority: P2
- Owner: Stream F（CE4専任）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Editable: `issue-CE4-api-cli-audit-integration.md` のみ
- Related Backlog: `CE-4`
- Related ADR/Spec: `ADR-0028`, `ADR-0008`, `02_Architecture/schemas.md`
- Verification: `docs-check`

## Lane guard（独立性・停止条件）
- CE4は CE0 SSOT + CE1/CE2 read-only handoff を参照し、契約語彙を再定義しない。
- CE4は API/CLI/監査の契約I/F固定のみ（実装詳細・アルゴリズム詳細は禁止）。
- CE0契約ID（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）は参照専用。
- 監査欠損は常に fail-closed（成功扱い禁止）。
- 検証失敗時の自己修復は最大3回。**3回超過（4回目着手）を禁止し、即停止する。**
- 強制ワークフローは `Phase 1 Read → Phase 2 Plan → Phase 3 Execute → Phase 4 Verify → Phase 5 Proceed` の固定順のみ許可（Phaseの追加・入替・省略を禁止）。

## Phase 1 Read（CE0 contract IDs と監査4点の参照整合確認）
### CE0 contract IDs（read-only）
- `CE0-CTX-IF`: ContextQuery/ContextBundle の最小I/Fと deterministic `bundleHash` を参照。
- `CE0-SAFEMODE-IF`: safeMode既定ON、`allowUnreviewedText=false` 既定を参照。
- `CE0-REVIEW-IF`: `human_reviewed` 昇格は人手のみを参照。
- `CG-01..05`: proposal-only / 監査4点 / fail-closed の統治境界を参照。

### 監査4点（read-only）
- 必須イベントは `query / bundle / proposal / apply` の4点で固定。
- `dryRun=true` 時は `sideEffect=none` を契約語彙として固定。
- `sourceBundleHash=mock:<hash>` は依存切断下でも同値検証を成立させる参照キーとして固定。

### No-Go
- CE4で語彙再定義をしない。
- 監査欠損を成功扱いしない。
- safeMode既定を緩和しない（`CE0-SAFEMODE-IF` 準拠）。

## Phase 2 Plan（API/CLI同値性・監査欠損fail-closedをAC化）
### 合意済みスコープ（contract-only）
- CE4は契約I/F固定のみを扱い、実装手段・アルゴリズム・内部最適化は記述しない。
- API/CLI同値判定は `equivalenceKey + bundleHash`（AND）を唯一の判定軸とする。
- 監査4点欠損は常に fail-closed（成功扱い禁止）を適用する。
- `dryRun=true` は常に `sideEffect=none` を強制し、副作用を許容しない。
- `sourceBundleHash=mock:<hash>` は本番hashと同一の契約判定・監査導線を適用する。

### Acceptance Criteria（contract-only）
- [ ] API/CLI が同一 query 入力時に同一 `equivalenceKey` かつ同一 `bundleHash` を返す。
- [ ] 監査4点（`query / bundle / proposal / apply`）の欠損は 0 件。
- [ ] 監査4点のいずれか欠損時は必ず fail-closed（成功応答を返さない）。
- [ ] `dryRun=true` は常に `sideEffect=none`。
- [ ] `sourceBundleHash=mock:<hash>` 入力でも同一判定規則（`equivalenceKey + bundleHash`）を維持。
- [ ] `CE0-SAFEMODE-IF` 参照導線を維持し、CE4で緩和しない。

### Definition of Done（DoD）
- [ ] CE4の公開I/F記述は API/CLI/監査導線に限定され、実装詳細を含まない。
- [ ] CE0/CE1/CE2語彙の再定義がない。
- [ ] fail-closed 条件が監査4点欠損に対して明示されている。
- [ ] `dryRun=true -> sideEffect=none` が契約条項として明示されている。
- [ ] `sourceBundleHash=mock:<hash>` の同値判定条項が明示されている。

## Phase 3 Execute（I/F固定と監査導線のみ記述）
### Fixed Contract IDs（CE4）
- `CE4-EQUIVALENCE-IF`
- `CE4-AUDIT-CHAIN-IF`
- `CE4-DRYRUN-SAFETY-IF`
- `CE4-MOCK-HASH-IF`

### I/F固定（実装詳細禁止）
- 判定軸は `equivalenceKey + bundleHash`（AND）に固定。
- 参照語彙は `equivalenceKey / bundleHash / sourceBundleHash / queryCanonicalHash` の read-only 利用に限定。
- proposal lifecycle は `proposed / accepted / rejected / held` の read-only 利用に限定。

### CE4 Contract I/F Matrix（normative / contract-only）
| Contract ID | Input Surface | Output / Audit Obligation | Failure Semantics |
| --- | --- | --- | --- |
| `CE4-EQUIVALENCE-IF` | API/CLI共通 query | 同一 query では `equivalenceKey` と `bundleHash` を同値で返す | いずれか不一致時は fail-closed |
| `CE4-AUDIT-CHAIN-IF` | `query -> bundle -> proposal -> apply` | 4点すべての監査イベント記録を必須化 | 1点でも欠損した時点で fail-closed |
| `CE4-DRYRUN-SAFETY-IF` | `dryRun=true` | 監査語彙 `sideEffect=none` を必須化 | `none` 以外は fail-closed |
| `CE4-MOCK-HASH-IF` | `sourceBundleHash=mock:<hash>` | 本番hashと同一の同値判定・監査導線を適用 | 分岐差分/欠損検出時は fail-closed |

### 監査導線固定（実装詳細禁止）
- 監査イベント導線は `query -> bundle -> proposal -> apply` の4点を必須化。
- `dryRun=true -> sideEffect=none` を監査イベント語彙として固定。
- `mock:<hash>` と本番hashで監査導線を分岐させない（同一fail-closed）。

## Phase 4 Verify（同一query同一bundle要件・ログ欠落ゼロを自己検証）
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`
- 自己修復は最大3回。3回で解消しない場合は4回目に着手せず即停止する。

### Self Verification Checklist
- [ ] 同一 query に対して API/CLI の `equivalenceKey` と `bundleHash` が同値である。
- [ ] 監査ログは `query / bundle / proposal / apply` の欠落が 0 件。
- [ ] 監査欠損時に fail-closed 以外の遷移を許していない。
- [ ] `dryRun=true` で `sideEffect=none` を常に満たす。
- [ ] `sourceBundleHash=mock:<hash>` でも同一判定軸を維持する。

## Phase 5 Proceed（未承認事項は確定せず停止条件を維持）
### Handoff（確定事項のみ）
- CE4は `CE4-EQUIVALENCE-IF` / `CE4-AUDIT-CHAIN-IF` / `CE4-DRYRUN-SAFETY-IF` / `CE4-MOCK-HASH-IF` を固定。
- CE0/CE1/CE2は read-only参照を維持し、再定義しない。
- 監査欠損 fail-closed を維持し、成功扱いを行わない。

### 未承認事項の扱い
- 未承認事項は `held` のまま据え置き、CE4では確定しない。
- 未承認事項を `accepted` / `rejected` に遷移させない（`held` 固定）。
- 未定義競合・SafeMode後退兆候・自己修復3回超過は即停止。
