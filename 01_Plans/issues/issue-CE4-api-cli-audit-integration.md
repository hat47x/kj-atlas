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
- CE4は CE0 SSOT + CE1/CE2 read-only handoff を参照し、**CE0/CE1/CE2 を更新しない**。
- CE4は CE0/CE1/CE2 の契約語彙を再定義しない（read-only参照のみ）。
- CE4は API/CLI/監査の契約I/F固定のみ（実装詳細・アルゴリズム詳細は禁止）。
- CE0契約ID（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）は参照専用。
- 監査欠損は常に fail-closed（成功扱い禁止）。
- 検証失敗時の自己修復は最大3回。**3回超過（4回目着手）を禁止し、即停止する。**
- 強制ワークフローは `Phase 1 Read → Phase 2 Plan → Phase 3 Execute → Phase 4 Verify → Phase 5 Proceed` の固定順のみ許可（Phaseの追加・入替・省略を禁止）。
- **各Phase開始時に Read同期（CE0 contract IDs / 監査4点 / fail-closed 条項）を実施**し、差分検知時はそのPhase内で契約記述を先に補正してから次工程へ進む。

## Phase 1 Read（CE0 contract IDs と監査4点の参照整合確認）
### CE0 contract IDs（read-only）
- `CE0-CTX-IF`: ContextQuery/ContextBundle の最小I/Fと deterministic `bundleHash` を参照。
- `CE0-SAFEMODE-IF`: safeMode既定ON、`allowUnreviewedText=false` 既定を参照。
- `CE0-REVIEW-IF`: `human_reviewed` 昇格は人手のみを参照。
- `CG-01..05`: proposal-only / 監査4点 / fail-closed の統治境界を参照。

### CE1/CE2 handoff（read-only）
- CE1/CE2 は参照専用（差分確認のみ）とし、CE4から逆流更新しない。
- CE4では CE1/CE2 の実装詳細・運用手順を追記しない（契約I/F固定のみ）。

### 監査4点（read-only）
- 必須イベントは `query / bundle / proposal / apply` の4点で固定。
- `dryRun=true` 時は `sideEffect=none` を契約語彙として固定。
- `sourceBundleHash=mock:<hash>` は依存切断下でも同値検証を成立させる参照キーとして固定。

### No-Go
- CE4で語彙再定義をしない。
- 監査欠損を成功扱いしない。
- safeMode既定を緩和しない（`CE0-SAFEMODE-IF` 準拠）。

## Phase 2 Plan（API/CLI同値性・監査4点・fail-closed契約固定をAC化）
### Phase開始 Read同期ログ
- Read同期: 完了（CE0 contract IDs, 監査4点, fail-closed条項に差分なし）。

### AC/DoD不足提案と合意（contract-only）
- 提案P1: API/CLI同値判定の監査再現性を強化するため、`queryCanonicalHash` を監査必須項目へ昇格する。
  - 合意: 採用（語彙追加ではなく既存参照語彙の必須化として扱う）。
- 提案P2: proposal lifecycle の語彙拡張を抑止するため、閉集合（`proposed / accepted / rejected / held`）を明文化する。
  - 合意: 採用（contract boundary の固定のみ、挙動変更なし）。
- 提案P3: No-Go逸脱を防ぐため、CE4での禁止事項（語彙再定義・safeMode緩和・監査欠損成功扱い）を Verify でも再チェック対象にする。
  - 合意: 採用（Phase 4 checklist に反映）。

### 合意済みスコープ（contract-only）
- CE4は契約I/F固定のみを扱い、実装手段・アルゴリズム・内部最適化は記述しない。
- API/CLI同値判定は `equivalenceKey + bundleHash`（AND）を唯一の判定軸とする（片側一致の部分成功を禁止）。
- 監査4点欠損は常に fail-closed（成功扱い禁止）を適用する。
- `dryRun=true` は常に `sideEffect=none` を強制し、副作用を許容しない。
- `sourceBundleHash=mock:<hash>` は本番hashと同一の契約判定・監査導線を適用する。

### Acceptance Criteria（contract-only）
- [ ] API/CLI が同一 query 入力時に同一 `equivalenceKey` かつ同一 `bundleHash` を返す。
- [ ] `equivalenceKey` のみ一致、または `bundleHash` のみ一致は成功扱いにしない（AND欠損をfail-closed）。
- [ ] 監査4点（`query / bundle / proposal / apply`）の欠損は 0 件。
- [ ] 監査4点のいずれか欠損時は必ず fail-closed（成功応答を返さない）。
- [ ] `dryRun=true` は常に `sideEffect=none`。
- [ ] `sourceBundleHash=mock:<hash>` 入力でも同一判定規則（`equivalenceKey + bundleHash`）を維持。
- [ ] `CE0-SAFEMODE-IF` 参照導線を維持し、CE4で緩和しない。
- [ ] API/CLI同値判定の監査証跡に `queryCanonicalHash` を必須記録し、比較根拠を欠落させない。
- [ ] proposal lifecycle の遷移語彙は `proposed / accepted / rejected / held` のみを利用し、追加語彙を導入しない。

### Definition of Done（DoD）
- [ ] CE4の公開I/F記述は API/CLI/監査導線に限定され、実装詳細を含まない。
- [ ] CE0/CE1/CE2語彙の再定義がない。
- [ ] fail-closed 条件が監査4点欠損に対して明示されている。
- [ ] `equivalenceKey AND bundleHash` の両方一致を満たさない部分一致を成功扱いしないことが明示されている。
- [ ] `dryRun=true -> sideEffect=none` が契約条項として明示されている。
- [ ] `sourceBundleHash=mock:<hash>` の同値判定条項が明示されている。
- [ ] 同値判定の比較根拠（`queryCanonicalHash`）が監査証跡必須項目として明示されている。
- [ ] proposal lifecycle を read-only語彙に限定する条項が明示されている。

### CDC（Change Decision Clarification: Context / Decision / Consequences 必須）
> ADR作業が発生する場合、**Context / Decision / Consequences の承認完了前に確定記述へ進まない**。

- CDC-CE4-001: CE4契約に `queryCanonicalHash` 監査必須化を追加する。
  - Context: API/CLI同値判定の比較根拠が監査証跡に残らない場合、再現検証時の同値判定が不安定化する。
  - Decision: `queryCanonicalHash` を監査必須項目として固定し、`equivalenceKey + bundleHash` の同値判定根拠に紐づける。
  - Consequences: 契約語彙の追加は行わず、既存 read-only 語彙の必須化のみ実施する。
  - 承認状態: **承認済み（CE4 contract-only 範囲）**。
- CDC-CE4-002: CE4契約に proposal lifecycle 語彙の閉集合（`proposed / accepted / rejected / held`）を明文化する。
  - Context: CE4範囲で lifecycle 語彙が拡張されると、API/CLI同値性と監査4点の契約比較が分岐し得る。
  - Decision: proposal lifecycle は `proposed / accepted / rejected / held` の閉集合に固定し、read-only参照のみ許可する。
  - Consequences: 契約境界が明確化されるが、挙動変更は発生しない。
  - 承認状態: **承認済み（CE4 contract-only 範囲）**。

## Phase 3 Execute（I/F固定と監査導線のみ記述）
### Phase開始 Read同期ログ
- Read同期: 完了（CE0/CE1/CE2はread-only継続、再定義なし）。

### Fixed Contract IDs（CE4）
- `CE4-EQUIVALENCE-IF`
- `CE4-AUDIT-CHAIN-IF`
- `CE4-DRYRUN-SAFETY-IF`
- `CE4-MOCK-HASH-IF`

### I/F固定（実装詳細禁止）
- 判定軸は `equivalenceKey + bundleHash`（AND）に固定。
- 参照語彙は `equivalenceKey / bundleHash / sourceBundleHash / queryCanonicalHash` の read-only 利用に限定。
- 同値判定の監査証跡には `queryCanonicalHash` を必須記録し、欠損時は fail-closed とする。
- proposal lifecycle は `proposed / accepted / rejected / held` の read-only 利用に限定。

### CE4 Contract I/F Matrix（normative / contract-only）
| Contract ID | Input Surface | Output / Audit Obligation | Failure Semantics |
| --- | --- | --- | --- |
| `CE4-EQUIVALENCE-IF` | API/CLI共通 query | 同一 query では `equivalenceKey` と `bundleHash` を同値で返す | いずれか不一致時は fail-closed |
| `CE4-EQUIVALENCE-IF` | API/CLI共通 query | 同値比較の監査証跡として `queryCanonicalHash` を必須記録する | 欠損時は fail-closed |
| `CE4-AUDIT-CHAIN-IF` | `query -> bundle -> proposal -> apply` | 4点すべての監査イベント記録を必須化 | 1点でも欠損した時点で fail-closed |
| `CE4-DRYRUN-SAFETY-IF` | `dryRun=true` | 監査語彙 `sideEffect=none` を必須化 | `none` 以外は fail-closed |
| `CE4-MOCK-HASH-IF` | `sourceBundleHash=mock:<hash>` | 本番hashと同一の同値判定・監査導線を適用 | 分岐差分/欠損検出時は fail-closed |

### 監査導線固定（実装詳細禁止）
- 監査イベント導線は `query -> bundle -> proposal -> apply` の4点を必須化。
- `dryRun=true -> sideEffect=none` を監査イベント語彙として固定。
- `mock:<hash>` と本番hashで監査導線を分岐させない（同一fail-closed）。

## Phase 4 Verify（同一query同一bundle要件・ログ欠落ゼロを自己検証）
### Phase開始 Read同期ログ
- Read同期: 完了（監査4点固定・fail-closed条項を再確認）。

- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`
- 自己修復は最大3回。3回で解消しない場合は4回目に着手せず即停止する。

### Fail-closed Verification Matrix（監査欠損成功扱い禁止）
| Case ID | Preconditions | Expected Result |
| --- | --- | --- |
| `CE4-V-001` | `query/bundle/proposal/apply` が4点そろう | 成功判定してよい（契約準拠） |
| `CE4-V-002` | `query` 欠損 | **fail-closed**（成功応答禁止） |
| `CE4-V-003` | `bundle` 欠損 | **fail-closed**（成功応答禁止） |
| `CE4-V-004` | `proposal` 欠損 | **fail-closed**（成功応答禁止） |
| `CE4-V-005` | `apply` 欠損 | **fail-closed**（成功応答禁止） |
| `CE4-V-006` | `dryRun=true` かつ `sideEffect!=none` | **fail-closed**（成功応答禁止） |
| `CE4-V-007` | `sourceBundleHash=mock:<hash>` で監査導線が本番と不一致 | **fail-closed**（成功応答禁止） |
| `CE4-V-008` | `equivalenceKey` 一致 かつ `bundleHash` 不一致 | **fail-closed**（AND不成立の成功扱い禁止） |
| `CE4-V-009` | `equivalenceKey` 不一致 かつ `bundleHash` 一致 | **fail-closed**（AND不成立の成功扱い禁止） |
| `CE4-V-010` | 同値判定監査で `queryCanonicalHash` 欠損 | **fail-closed**（比較根拠欠損の成功扱い禁止） |

### Self Verification Checklist
- [ ] 同一 query に対して API/CLI の `equivalenceKey` と `bundleHash` が同値である。
- [ ] `equivalenceKey` 単独一致または `bundleHash` 単独一致の部分成功を許容していない。
- [ ] 監査ログは `query / bundle / proposal / apply` の欠落が 0 件。
- [ ] 監査欠損時に fail-closed 以外の遷移を許していない。
- [ ] `dryRun=true` で `sideEffect=none` を常に満たす。
- [ ] `sourceBundleHash=mock:<hash>` でも同一判定軸を維持する。
- [ ] 同値判定監査で `queryCanonicalHash` の欠損を許容していない。
- [ ] CE4で語彙再定義を行っていない（read-only参照維持）。
- [ ] `CE0-SAFEMODE-IF` の既定（safeMode既定ON / `allowUnreviewedText=false`）を緩和していない。

## Phase 5 Proceed（未承認事項は確定せず停止条件を維持）
### Phase開始 Read同期ログ
- Read同期: 完了（No-Go: 語彙再定義禁止 / safeMode緩和禁止 / 監査欠損成功扱い禁止）。

### Handoff（確定事項のみ）
- CE4は `CE4-EQUIVALENCE-IF` / `CE4-AUDIT-CHAIN-IF` / `CE4-DRYRUN-SAFETY-IF` / `CE4-MOCK-HASH-IF` を固定。
- CE0/CE1/CE2は read-only参照を維持し、再定義しない。
- 監査欠損 fail-closed を維持し、成功扱いを行わない。

### 未承認事項の扱い
- 未承認事項は `held` のまま据え置き、CE4では確定しない。
- 致命エラー（自己修復3回超過 / SafeMode後退兆候 / 契約矛盾検出）時は即停止し、指示待ちへ遷移する。

---

## Stream F Execution Record（2026-04-22）

### Phase Progress（Read → Plan → Execute → Verify → Proceed）
- Phase 1 Read: 完了（CE0 contract IDs / 監査4点 / CE0参照契約のread-only条件を再確認）。
- Phase 2 Plan: 完了（API/CLI同値性・監査4点・fail-closed契約固定をACへ反映）。
- Phase 3 Execute: 完了（contract-only I/F matrix と監査導線固定を記述）。
- Phase 4 Verify: 完了（監査4点欠損成功扱い禁止とAND不成立fail-closedを `CE4-V-001..010` で固定）。
- Phase 5 Proceed: 完了（未承認事項は `held` 維持、契約再定義禁止を維持）。

### Repair Attempt Ledger（自己修復上限）
- Attempt 1: pass
- Attempt 2: n/a
- Attempt 3: n/a
- Attempt 4+: **forbidden / stop**
- 未承認事項を `accepted` / `rejected` に遷移させない（`held` 固定）。
- CDC-CE4-001 / CDC-CE4-002 はCE4 contract-only範囲で承認済み。実装詳細への展開は継続して禁止。
- 未定義競合・SafeMode後退兆候・自己修復3回超過は即停止。
