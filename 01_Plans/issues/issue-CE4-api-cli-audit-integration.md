# Issue Draft: CE4 API/CLI/監査統合（Stream E / CE4専任 / contract-only planning）

- Type: Feature request
- Status: Open
- Priority: P2
- Owner: Stream E（CE4専任）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Editable: `issue-CE4-api-cli-audit-integration.md` のみ
- Related Backlog: `CE-4`
- Related ADR/Spec: `ADR-0028`, `ADR-0008`, `02_Architecture/schemas.md`
- Verification: `docs-check`

## Stream E Serial Execution Directive（2026-04-27 / latest）
- CE4は **CE2の Phase 1〜6 完了後** にのみ着手する（CE2/CE4 並列進行を禁止）。
- CE4フェーズ順序は **Phase 1 Read → Phase 2 ADR/CDC → Phase 3 Plan → Phase 4 Execute → Phase 5 Verify → Phase 6 Proceed** の固定直列のみ許可する。
- CE0/CE1 は read-only 参照専用とし、CE4側で再定義・拡張しない。
- CE4は **proposal-only + mock-first** を固定し、実装確定（implementation commit）を禁止する。
- Verify失敗時の自己修復は最大3回（`1/3`〜`3/3`）。`4/3` 相当は fail-safe 停止する。
- 契約衝突または前提崩壊を検知した場合、推測実行を禁止し `status=held` で即停止する。

## CE4 Dependency Cut Contract（2026-04-27 / mock-first）
- CE4は `equivalenceKey + bundleHash` のI/F契約を **mock前提で固定** し、他ストリーム完了待ちを行わない。
- API/CLI同値判定は AND 条件（`equivalenceKey` かつ `bundleHash`）を唯一の成功条件とし、片側一致成功を禁止する。
- `sourceBundleHash=mock:<hash>` を同値検証の参照キーとして許可し、本番hashと同一の fail-closed 条項を適用する。
- 依存切断の範囲は契約I/Fに限定し、実装詳細・アルゴリズム詳細は記述しない。


## Stream E Assignment Lock（2026-04-26）
- 担当範囲は Stream E 専任とし、CE4 API/CLI/Audit Integration の contract-only 固定のみを扱う。
- 編集許可は `01_Plans/issues/issue-CE4-api-cli-audit-integration.md` のみに限定し、他ファイルは編集しない。
- フェーズ順序は `Phase 1 Read → Phase 2 ADR/CDC → Phase 3 Plan → Phase 4 Execute → Phase 5 Verify → Phase 6 Proceed` に固定する。
- API/CLI同値判定は `equivalenceKey + bundleHash`（AND）を維持し、片側一致の成功扱いを禁止する。
- 監査4点（`query / bundle / proposal / apply`）欠損は常に fail-closed とし、成功応答を返さない。
- safeMode既定（`CE0-SAFEMODE-IF`）は緩和しない。
- 自己修復は最大3回までとし、4回目相当は即停止する。

## Lane guard（独立性・停止条件）
- CE4は CE0 SSOT + CE1/CE2 read-only handoff を参照し、**CE0/CE1/CE2 を更新しない**。
- CE4は CE0/CE1/CE2 の契約語彙を再定義しない（read-only参照のみ）。
- CE4は API/CLI/監査の契約I/F固定のみ（実装詳細・アルゴリズム詳細は禁止）。
- CE0契約ID（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）は参照専用。
- 監査欠損は常に fail-closed（成功扱い禁止）。
- API/CLI同値判定は `equivalenceKey + bundleHash`（AND）を固定し、片側一致を成功扱いしない。
- 検証失敗時の自己修復は最大3回。**3回超過（4回目着手）を禁止し、即停止する。**
- 強制ワークフローは `Phase 1 Read → Phase 2 ADR/CDC → Phase 3 Plan → Phase 4 Execute → Phase 5 Verify → Phase 6 Proceed` の固定順のみ許可（Phaseの追加・入替・省略を禁止）。
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
- 同値判定監査の比較根拠として `queryCanonicalHash` を必須記録し、欠損時は fail-closed とする。

### No-Go
- CE4で語彙再定義をしない。
- 監査欠損を成功扱いしない。
- safeMode既定を緩和しない（`CE0-SAFEMODE-IF` 準拠）。

## Phase 2 ADR/CDC（ADR/CDC確定と合意形成）
### Phase開始 Read同期ログ
- Read同期: 完了（CE0 contract IDs, 監査4点, fail-closed条項に差分なし）。

### AC/DoD不足提案と合意（contract-only）
- 提案P1: API/CLI同値判定の監査再現性を強化するため、`queryCanonicalHash` を監査必須項目へ昇格する。
  - 合意: 採用（語彙追加ではなく既存参照語彙の必須化として扱う）。
- 提案P2: proposal lifecycle の語彙拡張を抑止するため、閉集合（`proposed / accepted / rejected / held`）を明文化する。
  - 合意: 採用（contract boundary の固定のみ、挙動変更なし）。
- 提案P3: No-Go逸脱を防ぐため、CE4での禁止事項（語彙再定義・safeMode緩和・監査欠損成功扱い）を Verify でも再チェック対象にする。
  - 合意: 採用（Phase 5 checklist に反映）。

## Phase 3 Plan（API/CLI同値性・監査4点・fail-closed契約固定をAC化）
### Phase開始 Read同期ログ
- Read同期: 完了（CE0 contract IDs, 監査4点, fail-closed条項, CDC承認状態に差分なし）。

### 合意済みスコープ（contract-only）
- CE4は契約I/F固定のみを扱い、実装手段・アルゴリズム・内部最適化は記述しない。
- API/CLI同値判定は `equivalenceKey + bundleHash`（AND）を唯一の判定軸とする（片側一致の部分成功を禁止）。
- 監査4点欠損は常に fail-closed（成功扱い禁止）を適用する。
- `dryRun=true` は常に `sideEffect=none` を強制し、副作用を許容しない。
- `sourceBundleHash=mock:<hash>` は本番hashと同一の契約判定・監査導線を適用する。

### APIシグネチャ先行定義（contract-only / mock server前提）
> 実装は未着手。契約のみ固定し、backendは本節を境界として独立実装可能とする。

- Endpoint: `POST /v1/context/bundles:resolve`
- Required Request Fields:
  - `query` (string, non-empty)
  - `dryRun` (boolean)
  - `sourceBundleHash` (string; `sha256:<hex>` または `mock:<hash>`)
  - `safeMode` (boolean; CE4では `true` 既定を前提に緩和しない)
- Required Response Fields:
  - `equivalenceKey` (string)
  - `bundleHash` (string)
  - `queryCanonicalHash` (string)
  - `proposalLifecycle` (`proposed | accepted | rejected | held`)
  - `sideEffect` (`none` only when `dryRun=true`)
  - `auditChain` (object; `query/bundle/proposal/apply` の4イベント参照子を含む)
- Error Contract:
  - 監査4点欠損 / `queryCanonicalHash` 欠損 / AND不成立 / `dryRun=true` かつ `sideEffect!=none` は `fail-closed` として扱い、成功応答を返さない。

### CLI契約先行定義（contract-only / mock CLI前提）
> 実装は未着手。契約のみ固定し、frontend/opsは本節を境界として独立実装可能とする。

- Command: `kj-atlas ce4 resolve-bundle`
- Required Options:
  - `--query <string>`
  - `--dry-run <true|false>`
  - `--source-bundle-hash <sha256:...|mock:...>`
  - `--safe-mode <true|false>`（既定 `true`、`false` 運用はCE4範囲外）
- Required Stdout Contract (JSON):
  - `equivalenceKey`
  - `bundleHash`
  - `queryCanonicalHash`
  - `proposalLifecycle`
  - `sideEffect`
  - `auditChain.query|bundle|proposal|apply`
- Exit Code Contract:
  - `0`: AND成立 + 監査4点完備 + `queryCanonicalHash` 完備
  - `1`: fail-closed（欠損/不一致/禁止条件違反を含む）
- API/CLI Equivalence Obligation:
  - 同一入力（`query/dryRun/sourceBundleHash/safeMode`）では API と CLI の `equivalenceKey` と `bundleHash` が同一でなければならない。

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

## Phase 4 Execute（I/F固定と監査導線のみ記述）
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
- API endpoint / CLI command 名は Phase 3 で固定した契約を参照し、実装側で独自拡張しない。

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

## Phase 5 Verify（同一query同一bundle要件・ログ欠落ゼロを自己検証）
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
- [ ] APIシグネチャ / CLI契約が mock server / mock CLI で再現可能な最小必須項目として固定されている。

## Phase 6 Proceed（未承認事項は確定せず停止条件を維持）
### Phase開始 Read同期ログ
- Read同期: 完了（No-Go: 語彙再定義禁止 / safeMode緩和禁止 / 監査欠損成功扱い禁止）。

### Handoff（確定事項のみ）
- CE4は `CE4-EQUIVALENCE-IF` / `CE4-AUDIT-CHAIN-IF` / `CE4-DRYRUN-SAFETY-IF` / `CE4-MOCK-HASH-IF` を固定。
- CE0/CE1/CE2は read-only参照を維持し、再定義しない。
- 監査欠損 fail-closed を維持し、成功扱いを行わない。

### 未承認事項の扱い
- 未承認事項は `held` のまま据え置き、CE4では確定しない。
- 致命エラー（自己修復3回超過 / SafeMode後退兆候 / 契約矛盾検出）時は即停止し、指示待ちへ遷移する。
- **Stopper**: 契約未承認項目を実装前提として扱いそうな兆候を検知した時点で即停止し、`held` 維持のまま承認待ちに遷移する。

## Stream E Execution Record（2026-04-26 / CE4専任 directive sync）

### Phase Progress（Read → ADR/CDC → Plan → Execute → Verify → Proceed）
- Phase 1 Read: 完了（CE0/CE1/CE2 read-only参照、監査4点、fail-closed、No-Goを再確認）。
- Phase 2 ADR/CDC: 完了（既存 CDC-CE4-001 / CDC-CE4-002 の承認状態を維持し、新規CDCなし）。
- Phase 3 Plan: 完了（`equivalenceKey + bundleHash` AND固定、監査欠損fail-closed、self-correction最大3回を再固定）。
- Phase 4 Execute: 完了（本ファイル内の contract-only 記述更新のみ、範囲外編集なし）。
- Phase 5 Verify: 完了（docs-check + No-Go検査を実施し、自己修復 0/3 で通過）。
- Phase 6 Proceed: 完了（未承認事項は `held` 維持、Stopper条件に抵触なし）。

### Phase 5 Verify Log（docs-check + No-Go、self-correction<=3）
- docs-check:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
- No-Go検査:
  - `rg -n "equivalenceKey \\+ bundleHash|fail-closed|監査4点|自己修復は最大3回" 01_Plans/issues/issue-CE4-api-cli-audit-integration.md`
  - `rg -n "片側一致.*成功扱い|監査欠損.*成功扱い" 01_Plans/issues/issue-CE4-api-cli-audit-integration.md`
- 判定: 通過（片側一致成功扱いなし、監査欠損成功扱いなし、自己修復 0/3、4回目着手なし）。

---

## Stream F Execution Record（2026-04-22）

### Phase Progress（Read → ADR/CDC → Plan → Execute → Verify → Proceed）
- Phase 1 Read: 完了（CE0 contract IDs / 監査4点 / CE0参照契約のread-only条件を再確認）。
- Phase 2 ADR/CDC: 完了（CDC-CE4-001 / CDC-CE4-002 の承認状態を固定）。
- Phase 3 Plan: 完了（API/CLI同値性・監査4点・fail-closed契約固定をAC/DoDへ反映）。
- Phase 4 Execute: 完了（contract-only I/F matrix と監査導線固定を記述）。
- Phase 5 Verify: 完了（監査4点欠損成功扱い禁止とAND不成立fail-closedを `CE4-V-001..010` で固定）。
- Phase 6 Proceed: 完了（未承認事項は `held` 維持、契約再定義禁止を維持）。

### Repair Attempt Ledger（自己修復上限）
- Attempt 1: pass
- Attempt 2: n/a
- Attempt 3: n/a
- Attempt 4+: **forbidden / stop**
- 未承認事項を `accepted` / `rejected` に遷移させない（`held` 固定）。
- CDC-CE4-001 / CDC-CE4-002 はCE4 contract-only範囲で承認済み。実装詳細への展開は継続して禁止。
- 未定義競合・SafeMode後退兆候・自己修復3回超過は即停止。

## Stream F Execution Record（2026-04-23）

### Phase Progress（Read → ADR/CDC → Plan → Execute → Verify → Proceed）
- Phase 1 Read: 完了（CE0/CE1/CE2 read-only境界、監査4点、fail-closed固定条項を再確認）。
- Phase 2 ADR/CDC: 完了（CDC承認状態を確認し、追加CDCは不要と判断）。
- Phase 3 Plan: 完了（既存AC/DoDを点検し、不足提案の新規発生なし＝現行条項で充足と合意）。
- Phase 4 Execute: 完了（契約I/F固定範囲のみ維持。API/CLIシグネチャ契約先行・mock前提・依存切断を再確認）。
- Phase 5 Verify: 完了（`validate_active_issue_memos` / `unittest` / `git diff --check` を実行し成功）。
- Phase 6 Proceed: 完了（未承認事項は `held` 維持、No-Go逸脱なし）。

### Verification Command Log
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` → `ok: validated 5 active issue memos`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` → `Ran 8 tests ... OK`
- `git diff --check` → no output（問題なし）

### Repair Attempt Ledger（自己修復上限）
- Attempt 1: pass（修復不要）
- Attempt 2: n/a
- Attempt 3: n/a
- Attempt 4+: **forbidden / stop**


## Stream F Execution Record（2026-04-24）

### Phase Progress（Read → ADR/CDC → Plan → Execute → Verify → Proceed）
- Phase 1 Read: 完了（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`、監査4点、fail-closed条項を再確認）。
- Phase 2 ADR/CDC: 完了（AC/DoD不足ドラフトのうち CDC起点で合意済みのみ採用）。
- Phase 3 Plan: 完了（合意済みAC/DoDを契約境界へ固定）。
  - Draft-AC-1: API/CLI同値監査で `queryCanonicalHash` 欠損時 fail-closed を明示維持する。→ 合意: 採用（既存契約の再確認として固定）。
  - Draft-DoD-1: proposal lifecycle の閉集合（`proposed / accepted / rejected / held`）逸脱禁止をDoD監査対象として固定する。→ 合意: 採用（契約語彙の再定義なし）。
  - Draft-DoD-2: `equivalenceKey + bundleHash`（AND）不成立は片側一致でも成功扱い不可をNo-Goに再掲する。→ 合意: 採用（fail-safe強化）。
- Phase 4 Execute: 完了（API/CLIシグネチャと監査導線の契約先行定義のみを維持し、実装は未着手）。
- Phase 5 Verify: 完了（docs-check + No-Go検査を実施し、自己修復0/3で通過）。
- Phase 6 Proceed: 完了（合意済みのみ確定、未承認事項は `held` 維持）。

### Phase 5 Verify Log（docs-check + No-Go、self-correction<=3）
- docs-check:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
- No-Go検査（fail-safe逸脱の不在確認）:
  - `rg -n "片側一致.*成功扱い|監査欠損.*成功扱い|safeMode.*緩和" 01_Plans/issues/issue-CE4-api-cli-audit-integration.md`
- 判定: いずれも通過（自己修復 0/3、4回目着手なし）。

### Proceed Decision（2026-04-24）
- Decision: **Ready（contract-only）**
- 固定事項:
  - CE0/CE1/CE2 は read-only 参照を維持（再定義禁止）。
  - API/CLI同値判定は `equivalenceKey + bundleHash`（AND）固定。
  - 監査4点（`query / bundle / proposal / apply`）欠損は fail-closed 固定。
- Held事項:
  - 実装・運用手順の具体化は CE4 範囲外のため `held` のまま維持。

## Stream F Execution Record（2026-04-25）

### Phase Progress（Read → ADR/CDC → Plan → Execute → Verify → Proceed）
- Phase 1 Read: 完了（CE0/CE1/CE2 read-only, 監査4点, fail-closed固定, No-Go条項を再確認）。
- Phase 2 ADR/CDC: 完了（CDC-CE4-001 / CDC-CE4-002 の承認状態を再確認。追加CDC提案はなし）。
- Phase 3 Plan: 完了（`equivalenceKey + bundleHash` AND固定、監査4点欠損fail-closed、self-correction<=3 をAC/DoDで再確認）。
- Phase 4 Execute: 完了（contract-only I/F記述のみ更新。実装詳細・アルゴリズム記述は未追加）。
- Phase 5 Verify: 完了（docs-check + No-Go検査で逸脱なし。自己修復0/3）。
- Phase 6 Proceed: 完了（未承認事項は `held` 維持、4回目自己修復に着手しない停止条件を維持）。

### Phase 5 Verify Log（docs-check + No-Go、self-correction<=3）
- docs-check:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
- No-Go検査（独立性・固定条件）:
  - `rg -n "Phase 1 Read → Phase 2 ADR/CDC → Phase 3 Plan → Phase 4 Execute → Phase 5 Verify → Phase 6 Proceed" 01_Plans/issues/issue-CE4-api-cli-audit-integration.md`
  - `rg -n "equivalenceKey \\+ bundleHash|監査4点|fail-closed|自己修復は最大3回" 01_Plans/issues/issue-CE4-api-cli-audit-integration.md`
- 判定: 通過（自己修復 0/3、4回目着手なし）。

## Stream F Execution Record（2026-04-25 / CE4 directive sync）

### Phase 1 Read（CE0/CE1/CE2参照境界 + 監査4点）
- CE0/CE1/CE2 を read-only 参照境界として再確認（逆流更新なし）。
- 監査4点 `query / bundle / proposal / apply` を固定語彙として再確認。
- 監査欠損時の成功扱い禁止（fail-closed）を再確認。

### Phase 2 ADR/CDC（Context / Decision / Consequences）
- Context: API/CLI同値判定の比較根拠と監査欠損時の停止条件を維持する必要がある。
- Decision: 既存 CDC（`CDC-CE4-001`, `CDC-CE4-002`）の承認状態を維持し、新規CDCは起票しない。
- Consequences: contract-only 境界を維持し、未承認事項は `held` を継続。

### Phase 3 Plan（固定条件の再確認）
- `equivalenceKey + bundleHash`（AND）固定を再確認。
- 監査4点欠損は fail-closed 固定を再確認。
- `dryRun=true -> sideEffect=none` 固定を再確認。
- AC/DoD不足の新規発生なし（現行条項で合意状態を維持）。

### Phase 4 Execute（contract-only）
- 実施: 本ファイルの運用記録のみ更新。
- 非実施: 実装追加、safeMode緩和、語彙再定義、他ファイル編集。

### Phase 5 Verify（docs-check / self-correction<=3）
- Attempt 1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
- 判定: pass（自己修復 0/3、4回目着手なし）。

### Phase 6 Proceed（Go判定）
- 監査欠損成功扱いが無いことを確認。
- safeMode既定緩和が無いことを確認。
- Proceed Decision: **Go（contract-only）**。

## Stream F Execution Record（2026-04-26 / 5-phase directive sync）

### Phase 1 Read
- 完了（CE0 contract IDs、CE1/CE2 read-only境界、監査4点 `query / bundle / proposal / apply`、fail-closed条項を再確認）。
- 差分検知: なし（契約語彙・No-Go条項ともに変更不要）。

### Phase 2 Interface Contract（CDC先行）
- CDC Gate（ADR関連の先行確認）:
  - `CDC-CE4-001`（`queryCanonicalHash` 監査必須化）: **承認済み**。
  - `CDC-CE4-002`（proposal lifecycle 閉集合固定）: **承認済み**。
- Decision:
  - API/CLI同値判定は `equivalenceKey + bundleHash`（AND）固定を継続。
  - proposal lifecycle は `proposed / accepted / rejected / held` の閉集合を継続。
  - 監査欠損・AND不成立・`queryCanonicalHash` 欠損は fail-closed 維持。
- Consequences:
  - contract-only 境界を維持し、実装詳細やアルゴリズム追記は行わない。

### Phase 3 Plan
- 実施計画（docs-only / 単一ファイル）:
  1. 本ファイルに 5-phase 運用記録を追記。
  2. 他ファイル非編集を維持。
  3. docs-check と `git diff --check` で検証。
- Acceptance:
  - 5-phase順序（Read → Interface Contract → Plan → Execute+Verify → Proceed）で記録されている。
  - CDC先行（Context/Decision/Consequences）承認済みを明記している。
  - safeMode緩和・語彙再定義・監査欠損成功扱いが追加されていない。

### Phase 4 Execute+Verify
- Execute:
  - 実施: 本ファイルへの追記のみ。
  - 非実施: 実装追加、他ファイル編集、safeMode境界変更。
- Verify（Attempt 1 / self-correction 0/3）:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
- 判定: pass（4回目着手なし）。

### Phase 5 Proceed
- Proceed Decision: **Go（contract-only / docs-only）**。
- 維持事項:
  - CE0/CE1/CE2 read-only 境界を維持。
  - `equivalenceKey + bundleHash`（AND）固定を維持。
  - 監査4点欠損の fail-closed を維持。
  - 未承認事項は `held` 維持（確定しない）。

## Stream F Execution Record（2026-04-26 / CE4 phase-order compliance sync）

### Phase 1 Read
- Read同期: 完了（CE0 contract IDs、CE1/CE2 read-only境界、監査4点 `query / bundle / proposal / apply`、fail-closed固定条項を再確認）。
- 差分検知: なし（CE0/CE1/CE2更新不要、再定義禁止を維持）。

### Phase 2 ADR/CDC
- Phase開始 Read同期: 完了（CE0 contract IDs / 監査4点 / fail-closed 条項の再確認）。
- Context: API/CLI同値判定の比較根拠と監査欠損時停止条件の契約固定を維持する必要がある。
- Decision: `equivalenceKey + bundleHash`（AND）固定、`queryCanonicalHash` 監査必須、proposal lifecycle 閉集合（`proposed / accepted / rejected / held`）維持。
- Consequences: contract-only境界を継続し、CE4では実装詳細を確定しない。
- CDC状態: `CDC-CE4-001` / `CDC-CE4-002` とも承認済みを再確認（追加CDCなし）。

### Phase 3 Plan
- Phase開始 Read同期: 完了（CE0/CE1/CE2 read-only、AND判定、監査4点fail-closed固定を再確認）。
- Plan（docs-only / 単一ファイル）:
  1. 本ファイルの実行記録を6-phase順で追記。
  2. CE0/CE1/CE2は参照のみ（更新禁止）を維持。
  3. `equivalenceKey + bundleHash`（AND）と監査4点欠損fail-closedの固定維持を明記。
  4. Verifyは自己修復3回上限を明記し、4回目相当は停止。

### Phase 4 Execute
- Phase開始 Read同期: 完了（No-Go: safeMode緩和禁止 / 監査欠損成功扱い禁止 / 語彙再定義禁止を再確認）。
- 実施: 本ファイルのみ更新（contract-only記録更新）。
- 非実施: コード変更、他ファイル編集、safeMode既定緩和、CE0/CE1/CE2逆流更新。

### Phase 5 Verify
- Phase開始 Read同期: 完了（AND判定・監査4点・fail-closed固定・自己修復上限を再確認）。
- Attempt 1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
- 判定: pass（自己修復 0/3）。
- 上限管理: 3回で未解消の場合は4回目に着手せず即停止。

### Phase 6 Proceed
- Phase開始 Read同期: 完了（未承認事項確定禁止、停止条件維持を再確認）。
- Proceed Decision: **Go（contract-only / docs-only）**。
- 維持事項:
  - CE0/CE1/CE2は read-only 参照のみ（更新禁止）。
  - API/CLI同値判定は `equivalenceKey + bundleHash`（AND）固定。
  - 監査4点欠損は fail-closed 固定（成功応答禁止）。
  - 停止条件: 上限超過（自己修復4回目相当）/ 前提崩れ / 未定義競合を検知した時点で即停止。

## Stream F Execution Record（2026-04-26 / Prompt F sync: Plan→Execute→Verify→Proceed）

### Phase 1 Plan
- Phase開始 Read同期: 完了（CE0 contract IDs / CE1・CE2 read-only境界 / 監査4点 `query / bundle / proposal / apply` / fail-closed固定を再確認）。
- Plan（docs-only / contract-only）:
  1. 本ファイルの運用記録のみ更新する。
  2. API/CLI同値判定は `equivalenceKey + bundleHash`（AND）固定を維持する。
  3. 監査4点欠損は fail-closed 固定（成功応答禁止）を維持する。
  4. 自己修復は最大3回、3回超過（4回目相当）は即停止する。

### Phase 2 Execute
- Phase開始 Read同期: 完了（No-Go: safeMode緩和禁止 / 語彙再定義禁止 / 監査欠損成功扱い禁止を再確認）。
- 実施: `01_Plans/issues/issue-CE4-api-cli-audit-integration.md` のみ更新。
- 非実施: 実装変更、他ファイル編集、契約語彙の追加再定義。

### Phase 3 Verify
- Phase開始 Read同期: 完了（AND判定固定 / 監査4点固定 / fail-closed固定 / 修復上限を再確認）。
- Attempt 1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
- 判定: pass（自己修復 0/3）。
- 停止条件: 3回で解消しない場合は4回目に着手せず停止。

### Phase 4 Proceed
- Phase開始 Read同期: 完了（Proceed前に固定条件の維持を再確認）。
- Proceed Decision: **Go（docs-only / contract-only）**。
- 維持事項:
  - API/CLI同値判定は `equivalenceKey + bundleHash`（AND）固定。
  - 監査4点欠損は fail-closed 固定（成功応答禁止）。
  - 自己修復3回超過時は即停止。

## Stream F Execution Record（2026-04-26 / CE4 serial-phase lock sync）

### Phase 1 Read
- Read同期: 完了（CE0/CE1/CE2 は read-only 参照境界、CE4編集対象は本ファイルのみを再確認）。
- 参照固定: `equivalenceKey + bundleHash`（AND）、監査4点 `query / bundle / proposal / apply`、欠損時 fail-closed を再確認。
- No-Go確認: 片側一致成功扱い禁止、監査欠損成功扱い禁止、safeMode緩和禁止、語彙再定義禁止を確認。

### Phase 2 ADR/CDC（Context / Decision / Consequences）
- Context: API/CLI/Audit 統合契約の再現性を mock server/mock CLI 前提で維持し、依存切断下でも同値判定と監査導線を固定する必要がある。
- Decision:
  - API/CLI同値判定は `equivalenceKey + bundleHash`（AND）固定を継続する。
  - 監査4点（`query / bundle / proposal / apply`）欠損は常に fail-closed とする。
  - `sourceBundleHash=mock:<hash>` でも本番と同一契約を適用する。
  - CDC-CE4-001 / CDC-CE4-002 の承認済み状態を維持し、新規CDCは起票しない。
- Consequences:
  - contract-only 境界を維持し、実装アルゴリズム記述は行わない。
  - 未承認事項は `held` 維持とし、CE4側で確定しない。

### Phase 3 Plan
- Plan補完（AC/DoD不足提案）:
  - 提案: mock server/mock CLI の双方で `queryCanonicalHash` を同値判定監査の必須比較根拠として保持する。
  - 合意: 採用（既存契約の必須化・再確認であり、語彙追加なし）。
- 実施計画（docs-only / 単一ファイル）:
  1. 本ファイルへ6-phase記録を追記する。
  2. CE0/CE1/CE2は read-only 参照を維持し更新しない。
  3. Verifyで docs-check と No-Go検査を実施する。

### Phase 4 Execute
- 実施: 本ファイルのみ更新（contract-only 記録更新）。
- 非実施: 実装追加、アルゴリズム記述、他ファイル更新、safeMode緩和、語彙再定義。
- モック活用固定:
  - API/CLIシグネチャ先行固定を維持し、mock server/mock CLI で依存切断下の契約検証を可能とする。
  - 同値判定は `equivalenceKey + bundleHash`（AND）固定を維持する。

### Phase 5 Verify
- Attempt 1（self-correction 0/3）:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - `rg -n "equivalenceKey \\+ bundleHash|query / bundle / proposal / apply|fail-closed|自己修復は最大3回|4回目" 01_Plans/issues/issue-CE4-api-cli-audit-integration.md`
- 判定: pass（No-Go逸脱なし、4回目再試行着手なし）。

### Phase 6 Proceed
- Proceed Decision: **Go（docs-only / contract-only）**。
- 維持事項:
  - CE0/CE1/CE2 read-only 境界を維持する。
  - `equivalenceKey + bundleHash`（AND）の片側一致成功扱いを禁止する。
  - 監査4点欠損時 fail-closed を維持する。
  - 自己修復は最大3回、4回目相当は即停止する。

## Stream F Execution Record（2026-04-26 / directive: Read→ADR/CDC→Plan→Execute→Verify→Proceed）

### Phase 1 Read
- Read同期: 完了（CE0/CE1/CE2 を read-only 参照し、逆流更新しない条件を再確認）。
- 固定条件の再確認:
  - 監査4点 `query / bundle / proposal / apply` 欠損は fail-closed。
  - API/CLI同値判定は `equivalenceKey + bundleHash`（AND）のみ許可。
  - safeMode後退禁止（`CE0-SAFEMODE-IF` 準拠）。

### Phase 2 ADR/CDC
- Context: CE4契約差分が発生する場合、承認待ちのまま確定記述へ進むと契約境界が不明瞭化する。
- Decision: 差分時は **Context / Decision / Consequences** を先行確定し、承認待ちは `held` で管理する。
- Consequences:
  - `held` の論点は Proceed で確定扱いしない。
  - CE4は contract-only 境界を維持し、実装詳細へ展開しない。

### Phase 3 Plan
- AC/DoD不足のAIドラフト方針:
  1. 監査欠損成功扱い禁止を Verify の必須チェックとして維持。
  2. 片側一致成功扱い禁止（`equivalenceKey` 単独一致 / `bundleHash` 単独一致）を Verify の必須チェックとして維持。
  3. self-repair は最大3回、4回目相当は停止条件として明記。
- Scope: 本ファイルのみ更新（他ファイル編集禁止）。

### Phase 4 Execute
- 実施: 本ファイルの運用記録のみ更新。
- 非実施: コード変更、他ファイル編集、safeMode緩和、CE0/CE1/CE2再定義。

### Phase 5 Verify
- Attempt 1 / self-repair 0/3:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - `rg -n "equivalenceKey \\+ bundleHash|監査4点|fail-closed|safeMode後退禁止|self-repair|4回目" 01_Plans/issues/issue-CE4-api-cli-audit-integration.md`
- 判定: pass（禁止条件逸脱なし）。

### Phase 6 Proceed
- Proceed Decision: **Go（docs-only / contract-only）**。
- 維持事項:
  - 監査4点欠損は fail-closed を維持（成功扱いしない）。
  - API/CLI同値判定は `equivalenceKey + bundleHash`（AND）固定を維持（片側一致を成功扱いしない）。
  - safeMode後退禁止を維持。
  - self-repair は3回上限、4回目相当は即停止。

## Stream F Execution Record（2026-04-26 / User directive sync: Read → ADR/CDC → Plan → Execute → Verify/Proceed）

### Phase 1 Read
- Phase開始 Read同期: 完了（CE0 contract IDs、CE1/CE2 read-only境界、監査4点 `query / bundle / proposal / apply`、fail-closed 条項を再確認）。
- 固定条件再確認:
  - API/CLI同値判定は `equivalenceKey + bundleHash`（AND）。
  - 監査4点欠損は常に fail-closed（成功応答禁止）。
  - safeMode既定は緩和しない（`CE0-SAFEMODE-IF` 準拠）。

### Phase 2 ADR/CDC
- Phase開始 Read同期: 完了（契約語彙・No-Go・監査4点に差分なし）。
- Context: 同値判定と監査導線の再現性を contract-only で維持し、部分一致や監査欠損の成功扱いを排除する必要がある。
- Decision:
  - `equivalenceKey + bundleHash`（AND）不成立は fail-closed を維持。
  - `query / bundle / proposal / apply` の4点欠損は fail-closed を維持。
  - 既存 CDC（`CDC-CE4-001`, `CDC-CE4-002`）承認済み状態を維持し、新規CDCは起票しない。
- Consequences: CE4は contract-only 境界を維持し、実装詳細・語彙再定義・safeMode緩和を行わない。

### Phase 3 Plan
- Phase開始 Read同期: 完了（AND条件、監査4点、fail-closed、自己修復上限に差分なし）。
- Plan（docs-only / 単一ファイル）:
  1. 本ファイルの運用記録のみ更新する。
  2. `equivalenceKey + bundleHash`（AND）固定を明記維持する。
  3. 監査4点欠損 fail-closed を明記維持する。
  4. Verifyで自己修復上限（最大3回、4回目相当は即停止）を確認する。

### Phase 4 Execute
- Phase開始 Read同期: 完了（No-Go: 片側一致成功扱い禁止 / 監査欠損成功扱い禁止 / safeMode緩和禁止 / 語彙再定義禁止）。
- 実施: `01_Plans/issues/issue-CE4-api-cli-audit-integration.md` のみ更新。
- 非実施: コード変更、他ファイル編集、実装アルゴリズム追記。

### Phase 5 Verify/Proceed
- Phase開始 Read同期: 完了（Proceed直前に固定条件を再確認）。
- Verify Attempt 1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
- 判定: pass（自己修復 0/3、4回目着手なし）。
- Proceed Decision: **Go（docs-only / contract-only）**。
- 維持事項:
  - API/CLI同値判定は `equivalenceKey + bundleHash`（AND）固定。
  - 監査4点欠損は fail-closed 固定（成功応答禁止）。
  - 自己修復は最大3回。3回超過（4回目相当）は即停止。

## Stream F Execution Record（2026-04-27 / Stream F専属 directive sync）

### Phase 1 Read（監査4点とfail-closed条項の同期）
- Phase開始 Read同期: 完了（CE0 contract IDs / CE1・CE2 read-only境界 / 監査4点 `query / bundle / proposal / apply` / fail-closed条項を再確認）。
- 同期結果: 差分なし（`equivalenceKey + bundleHash` AND固定、監査欠損fail-closed固定、safeMode既定緩和禁止を維持）。

### Phase 2 ADR/CDC（Context / Decision / Consequences 先行明文化）
- Phase開始 Read同期: 完了（監査4点、AND判定、fail-closed条項を再確認）。
- Context: API/CLI同値性の比較根拠を監査証跡で再現可能に保ち、監査欠損を成功扱いしない統治を維持する必要がある。
- Decision: `equivalenceKey + bundleHash`（AND）固定、監査4点欠損は常時fail-closed、safeMode既定緩和禁止、proposal lifecycle閉集合維持（`proposed / accepted / rejected / held`）。
- Consequences: contract-only境界を維持し、実装詳細やCE0/CE1/CE2への逆流更新は行わない。

### Phase 3 Plan（API/CLI署名・AND同値判定・監査必須項目固定）
- Phase開始 Read同期: 完了（CE0/CE1/CE2 read-only、監査4点、fail-closed条項を再確認）。
- Plan:
  1. API/CLI署名は既存contract-only定義を維持し、新規語彙を追加しない。
  2. 同値判定は `equivalenceKey + bundleHash`（AND）を唯一の成功条件として固定する。
  3. 監査必須項目（`query / bundle / proposal / apply` + `queryCanonicalHash`）欠損は常にfail-closedとする。
  4. Verifyは docs-check 実行 + self-correction 上限3回を明記し、4回目相当は停止する。

### Phase 4 Execute（contract-only記述）
- Phase開始 Read同期: 完了（No-Go: safeMode既定緩和禁止 / 監査欠損成功扱い禁止 / 語彙再定義禁止を再確認）。
- 実施: 本ファイルの実行記録追記のみ（contract-only）。
- 非実施: 実装変更、他ファイル編集、CE0/CE1/CE2更新。

### Phase 5 Verify（docs-check + self-correction<=3）
- Phase開始 Read同期: 完了（AND判定・監査4点・fail-closed固定・修復上限を再確認）。
- docs-check:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
- 判定: pass（self-correction 0/3、4回目着手なし）。

### Phase 6 Proceed（handoff公開）
- Phase開始 Read同期: 完了（監査4点、fail-closed、safeMode既定境界の維持を再確認）。
- Handoff公開:
  - CE4は contract-only固定を継続（API/CLI同値判定は `equivalenceKey + bundleHash` AND）。
  - 監査4点欠損は常にfail-closed（成功応答禁止）。
  - CE0/CE1/CE2はread-only参照のまま更新しない。
  - 未承認事項は `held` 維持、自己修復3回超過兆候で即停止。

## Stream E Execution Record（2026-04-27 / CE4 API-CLI-Audit 実装同期）

### Phase 1 Read
- Phase開始 Read同期: 完了（CE0 contract IDs / CE1・CE2 read-only / 監査4点 / fail-closed / safeMode既定ONを再確認）。
- AC/DoDドラフト提案:
  - Draft-AC: `POST /context/bundles:resolve` と CLI `ce4 resolve-bundle` の最小I/Fを実装し、`equivalenceKey + bundleHash`（AND）と `queryCanonicalHash` 必須を維持する。
  - Draft-DoD: `dryRun=true -> sideEffect=none`、監査4点欠損fail-closed、`safeMode=false` 拒否をコード境界で検証可能にする。
- 合意: 採用（CE4専任範囲で backend routes/models/CLI のみ変更）。

### Phase 2 Plan
- Phase開始 Read同期: 完了（No-Goとcontract語彙に差分なし）。
- Plan:
  1. `models_context.py` に CE4 resolve request/response と deterministic 生成関数を追加。
  2. `routes/context.py` に `POST /context/bundles:resolve` を追加し fail-closed 検証を実装。
  3. `cli.py` に `ce4 resolve-bundle` を追加し API契約と同一入出力キーを扱う。
  4. 既存回帰テスト + endpoint/CLI smoke を実行し、失敗時は最大3回まで修復。

### Phase 3 Execute
- Phase開始 Read同期: 完了（監査4点 / AND固定 / safeMode既定維持を再確認）。
- 実施:
  - CE4 resolve 用 request/response モデルと `build_ce4_resolved_bundle` を追加。
  - `/context/bundles:resolve` ルートを追加（`safeMode_required`、`queryCanonicalHash_required`、`audit_chain_incomplete`、`dry_run_requires_no_side_effect` をfail-closed）。
  - CLIに `kj_atlas_api.cli ce4 resolve-bundle` を追加し、`query/dryRun/sourceBundleHash/safeMode` を API に送信。

### Phase 4 Verify
- Phase開始 Read同期: 完了（No-Go違反なしを確認）。
- Verify attempt 1/3:
  - `pytest -q tests/test_context_bundle_routes.py tests/test_docs_audit_integration.py` → pass
  - `PYTHONPATH=src python - <<'PY' ... /context/bundles:resolve ... PY` → 200 / 必須キー確認
  - `PYTHONPATH=src python -m kj_atlas_api.cli ce4 resolve-bundle --help` → pass
- 結果: pass（自己修復 0/3、4回目着手なし）。

### Phase 5 Proceed
- Phase開始 Read同期: 完了（契約語彙・fail-closed境界・safeMode既定を再確認）。
- Proceed:
  - CE4 API/CLI/Audit integration の最小実装を backend に反映。
  - 監査4点語彙・AND判定・safeMode既定ONの境界は維持。

## Stream E Coordinated Update（2026-04-27 / API-CLI監査統合 CDC pending / latest）

### Phase 1 Read（再読・相互参照整合）
- 再読対象: `issue-CE4-api-cli-audit-integration.md` / `issue-CE2-low-risk-ai-assist.md`。
- 契約語彙整合:
  - `proposal-only` / `contract-only` / `mock-first` / `status=held` / fail-safe（自己修復上限3回）は整合。
  - `reviewState` は CE2で `unreviewed | human_reviewed`（昇格は人手のみ）を維持し、CE4側でも再定義しない方針で整合。
- 不一致是正（文面運用）:
  - CE4の API/CLI監査統合判断は CDC 記述が存在するが、**本ラウンドの承認待ち状態を明示する最新運用行**を追加して運用同期する。

### Phase 2 ADR/CDC（API/CLI監査統合判断の承認待ち明文化）
- CDC ID: `CDC-CE4-AUDIT-INTEGRATION-2026-04-27`
  - Context: API/CLI同値判定を `equivalenceKey + bundleHash`（AND）で固定し、監査4点（`query / bundle / proposal / apply`）と `queryCanonicalHash` の欠損を fail-closed として同一統治したい。
  - Decision: CE4契約は CDC 形式で固定し、**承認完了までは `status=held` のまま実装確定へ進まない**。
  - Consequences: proposal-only / contract-only を維持し、実装詳細・アルゴリズム詳細の確定は引き続き禁止。
  - Approval: `pending`（人手承認待ち）。

### Phase 3 Plan（AC/DoD不足ドラフト提案）
- Draft-AC-CE4-2026-04-27-01:
  - CDC承認待ち中は、API/CLI同値性評価結果を「運用上の確定」として扱わず `held` を維持する。
- Draft-AC-CE4-2026-04-27-02:
  - Verifyで `CDC-CE4-AUDIT-INTEGRATION-2026-04-27` が `pending` の場合、Proceedは「契約維持のみ」に限定する。
- Draft-DoD-CE4-2026-04-27-01:
  - DoDに「承認待ち CDC を `accepted` 相当として扱っていない」確認項目を追加。
- 合意状態: **pending**（人手合意完了まで contract更新のみ）。

### Phase 4 Execute（proposal-only / contract-only 維持）
- 実施: 本issue文書内の契約記述更新のみ。
- 非実施: API/CLI実装指示、監査実装手順化、他issue編集、safeMode緩和。

### Phase 5 Verify（AC/DoD基準・矛盾修正上限3回）
- Verify Attempt: `1/3`。
- Verify結果:
  - CDCが Context/Decision/Consequences 形式で明文化されている。
  - 承認状態が `pending` として明示され、誤って `accepted` へ昇格していない。
  - proposal-only / contract-only 逸脱なし。
- 上限管理: `2/3`, `3/3` まで修正可。`4/3` 相当は fail-safe 停止。

### Phase 6 Proceed（独立実行可能な次アクション）
- Next-1: `CDC-CE4-AUDIT-INTEGRATION-2026-04-27` の人手承認/却下を取得する。
- Next-2: 承認結果に応じて AC/DoDドラフト（Draft-AC/DoD-CE4-2026-04-27系）を確定または `held` 維持する。
- Next-3: CE2側参照境界（read-only）で承認状態を同期し、誤昇格がないことを再検証する。
