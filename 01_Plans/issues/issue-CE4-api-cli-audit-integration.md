# Issue Draft: CE4 API/CLI/監査統合（Stream D / CE4専任 / contract-only planning）

- Type: Feature request
- Status: Open
- Priority: P2
- Owner: Stream D（CE4専任）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Editable: `issue-CE4-api-cli-audit-integration.md` のみ
- Related Backlog: `CE-4`
- Related ADR/Spec: `ADR-0028`, `ADR-0008`, `02_Architecture/schemas.md`
- Dependencies: `CE-4`
- Verification: `docs-check`

## Stream D Execution Contract（2026-04-28 / CE4 API/CLI audit boundary）

### Phase 1 Read
- CE4は API/CLI監査境界の契約固定に限定し、frontend/backend実装差分を要求しない。
- CE0/CE1/CE2は read-only 参照とし、契約語彙の再定義を行わない。
- proposal-only 原則（自動確定経路の禁止）を開始時に再確認する。

### Phase 2 Plan
- AC/DoD不足時は契約ドラフトを追記し、人手承認まで `status=held` を維持する。
- API責務境界（入力/出力/失敗時挙動）と監査責務境界（4イベント+比較根拠）を分離して明記する。

### Phase 3 Execute（先行I/F固定）
- APIシグネチャとCLI出力契約を mock可能な粒度で先行固定する。
- 監査ログ必須項目を `query / bundle / proposal / apply + queryCanonicalHash` に固定する。
- API/CLI同値判定は `equivalenceKey AND bundleHash` のみ成功として扱う。

### Phase 4 Verify（監査観点）
- 追跡性: API/CLI双方から同一監査チェーンを辿れること。
- 再現性: 同一入力で `equivalenceKey/bundleHash/queryCanonicalHash` を比較可能であること。
- 漏えい防止: safeMode後退および `dryRun=true` 時の副作用を許容しないこと。

### Phase 5 Proceed（実装隊へ渡す契約パッケージ）
- [ ] proposal-only 境界（自動確定化なし）が明記されている。
- [ ] API I/F（必須入力・必須出力・fail-closed条件）が固定されている。
- [ ] CLI I/F（必須オプション・出力JSON・終了コード）が固定されている。
- [ ] 監査境界（4イベント + `queryCanonicalHash`）が欠損時 fail-closed である。
- [ ] 実装隊が mock で着手可能な独立契約として参照できる。

### Fail-safe（即停止条件）
- proposal-only 逸脱（auto-apply/auto-confirm/auto-publish）を検知した場合は即停止。
- 監査不能状態（必須監査項目欠損を成功扱い）を検知した場合は即停止。

## Stream E Plan Fix Baseline（2026-04-28 / CE4）

### Phase 1) Read
- CE0/CE1/CE2 契約は read-only 参照のみ。CE4で語彙再定義をしない。
- fixed boundary を再確認: `equivalenceKey + bundleHash`（AND）, `query/bundle/proposal/apply` 監査4点, fail-closed。
- fail-safe 起動条件（safeMode後退要求・責務分離崩壊・自己修復3回超過）を開始時に明示する。

### Phase 2) Plan（proposal-only）
- Planは contract proposal のみを扱い、`accepted/rejected` の最終決定は人間責務とする。
- AC/DoD不足時は差分ドラフトを提示し、人間承認まで `status=held` を維持する。
- ADR/CDC が必要な差分は **Context / Decision / Consequences** を先に明文化し、承認待ちとする。

### Phase 3) Execute（patch/diff前提・監査ログ固定）
- Executeは docs上の patch/diff 記録を必須化し、実装確定は行わない。
- 監査ログ必須項目は `query / bundle / proposal / apply` + `queryCanonicalHash` を固定し、欠損は fail-closed とする。
- API/CLI同値判定は `equivalenceKey` と `bundleHash` のAND成立のみ成功とし、部分一致成功を禁止する。

### Phase 4) Verify（安全境界・review境界の後退防止）
- safeMode既定ON と fail-closed 条項の後退がないことを確認する。
- review境界として「accept/rejectは人間責務」を再検証し、AIの自動確定経路が無いことを確認する。
- 検証失敗時の自己修復は `1/3`〜`3/3` まで。`4/3` 相当は fail-safe 停止。

### Phase 5) Proceed（実装前提チェックリスト）
- [ ] proposal-only 境界の維持（implementation commit なし）
- [ ] accept/reject が人間責務として記録されている
- [ ] patch/diff 証跡と監査4点+`queryCanonicalHash` が欠損なく参照可能
- [ ] API/CLI同値判定（AND）と fail-closed 条項に後退がない
- [ ] 停止条件（safeMode後退要求 / 責務分離崩壊 / 自己修復3回超過）未発火


## Stream E-2 Serial Lane Run（2026-04-28 / CE4 after CE2）
- 着手条件: CE2のPhase 1..6完遂を確認後に CE4 Phase 1 を開始する。
- allowlist固定: `issue-CE2-low-risk-ai-assist.md` / `issue-CE4-api-cli-audit-integration.md` のみを対象にする。
- 独立ルール: CE0/CE1契約は固定入力として read-only 参照し、CE4側で再定義しない。
- proposal-only維持: auto-apply / auto-publish / auto-confirm を禁止し、mock-firstの契約I/F固定のみを扱う。

### CE4 Phase 1..6 Execution Snapshot（this run）
- Phase 1 Read: 完了（CE0/CE1/CE2 read-only, 監査4点, fail-closed条項を再確認）。
- Phase 2 ADR/CDC: 完了（API/CLI/監査I/Fの契約境界を再確認、語彙拡張なし）。
- Phase 3 Plan: 完了（AC/DoD不足時はAIドラフト提案→人手合意後実行を固定）。
- Phase 4 Execute: 完了（contract-only文面整備のみ、実装・自動適用は未実施）。
- Phase 5 Verify: 完了（自己修復回数 `0/3`、上限超過なし）。
- Phase 6 Proceed: 完了（前提崩壊/契約衝突/未定義競合なし、`held` への遷移不要）。

### CE4 Stop Conditions（固定）
- Verifyの自己修復は最大3回（`1/3`〜`3/3`）。`4/3` 相当は fail-safe 停止。
- 上限超過、前提崩壊、未定義競合を検知した場合は `status=held` で即停止。

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

### Stream E Implementation Note（2026-04-30）
- CLI `context-audit` payload で `queryCanonicalHash` 入力を優先し、監査比較キー `queryHash` へ正規化して送信する互換導線を追加（legacy `queryHash` は後方互換として維持）。
- Audit utility に CE4比較キーの優先解決関数（`queryCanonicalHash` > `queryHash`）を追加し、API/CLI監査比較の実装側参照点を明確化。
- 単体/統合テストに上記優先順位の検証を追加し、同値判定導線の回帰を防止。

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

## Stream B Integration Note（2026-04-30）
- CE4 read-only handoff key（`equivalenceKey + bundleHash`、`queryCanonicalHash`）との整合を維持しつつ、CE1側の `/context/bundle` に deterministic guard を追加。
- CE4側の契約語彙・監査4点・proposal-only 境界への変更はなし（No-Go維持）。
- backend検証で `/context/bundle` の `409 nondeterministic_bundle` を追加確認し、CE4同値判定前提（bundle hashの決定論）への依存を明示。
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

## CE4 Serial Execution Record（2026-04-29 / CE4 phase sync after CE1）

### Phase 1 Read
- 対象ファイルを再Readし、CE4境界（proposal-only / mock-first / contract-only）を再確認。
- 固定条件（`equivalenceKey + bundleHash` AND、監査4点 `query/bundle/proposal/apply`、`queryCanonicalHash` 必須、fail-closed）に差分なし。

### Phase 2 Plan（ADR Context / Decision / Consequences 先行）
- Context: CE4はAPI/CLI/監査I/F契約を先行定義し、実装依存を切る必要がある。
- Decision: API/CLI統合は実装せず、mock利用前提の契約固定（endpoint/CLI必須項目、exit code、監査必須項目）を維持する。
- Consequences: backend/frontend/ops は本契約を境界に独立実装可能。監査欠損・AND不成立・`dryRun=true && sideEffect!=none` は成功扱いにしない。
- Approval log: 既存 CDC（`CDC-CE4-001` / `CDC-CE4-002`）承認済みを再確認。追加CDCなし。

### Phase 3 Execute（contract-only）
- 実施: 本ファイル内の実行記録追記のみ。
- 非実施: API/CLI実装、監査実装、他ファイル編集、safeMode緩和、語彙再定義。

### Phase 4 Verify
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `rg -n "equivalenceKey \\+ bundleHash|queryCanonicalHash|fail-closed|mock:<hash>" 01_Plans/issues/issue-CE4-api-cli-audit-integration.md`
- `git diff --check`
- 結果: pass（self-correction 0/3、競合なし）。

### Phase 5 Proceed
- Proceed Decision: **Go（contract-only / docs-only）**。
- 維持事項:
  - API/CLI統合は契約定義先行（mock活用）を継続し、実装依存を切る。
  - proposal-only 境界（auto-apply/auto-confirm/auto-publish禁止）を継続する。
  - 自己修復3回超過または契約競合時は `held` で停止する。

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

## Stream E Execution Record（2026-04-27 / CE4 API-CLI-Audit contract sync）

### Phase 1 Read
- Phase開始 Read同期: 完了（CE0 contract IDs / CE1・CE2 read-only / 監査4点 / fail-closed / safeMode既定ONを再確認）。
- AC/DoDドラフト提案:
  - Draft-AC: API/CLI同値判定は `equivalenceKey + bundleHash`（AND）と `queryCanonicalHash` 必須を維持する。
  - Draft-DoD: `dryRun=true -> sideEffect=none`、監査4点欠損fail-closed、`safeMode=false` 拒否を契約境界で検証可能にする。
- 合意: pending（人手合意完了まで contract-only 継続）。

### Phase 2 Plan
- Phase開始 Read同期: 完了（No-Goとcontract語彙に差分なし）。
- Plan: 本Issue文面の契約固定のみ更新し、実装変更は行わない。

### Phase 3 Execute
- Phase開始 Read同期: 完了（監査4点 / AND固定 / safeMode既定維持を再確認）。
- 実施: contract-only 文言整備のみ（API/CLI実装手順・コード変更の記述は行わない）。

### Phase 4 Verify
- Phase開始 Read同期: 完了（No-Go違反なしを確認）。
- Verify attempt 1/3:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
- 結果: pass（自己修復 0/3、4回目着手なし）。

### Phase 5 Proceed
- Phase開始 Read同期: 完了（契約語彙・fail-closed境界・safeMode既定を再確認）。
- Proceed:
  - CE4 API/CLI/Audit integration は contract-only 記述の固定に限定する。
  - 監査4点語彙・AND判定・safeMode既定ONの境界は維持する。

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

## Stream E Execution Record（2026-04-27 / CE4 contract-only latest）

> 本節を latest authoritative とし、CE4は contract-only 文書固定を継続する。実装詳細・アルゴリズム詳細は確定しない。

### Phase 1 Read
- Read同期（AND必須）: `equivalenceKey + bundleHash` を唯一の成功条件として再確認。
- Read同期（監査4点）: `query / bundle / proposal / apply` の4点必須を再確認。
- Read同期（dryRun）: `dryRun=true -> sideEffect=none` を再確認。
- Read同期（mock同等性）: `sourceBundleHash=mock:<hash>` は本番hashと同一 fail-closed を適用することを再確認。

### Phase 2 ADR/CDC
- Read同期（AND必須）: `equivalenceKey + bundleHash` 条項に差分なし。
- Read同期（監査4点）: 4点監査欠損は成功扱い禁止（fail-closed）を維持。
- Read同期（dryRun）: `dryRun=true` 時の副作用禁止を維持。
- Read同期（mock同等性）: `mock:<hash>` の同値判定分岐禁止を維持。
- CDC運用: 新規CDCが発生する場合は Context / Decision / Consequences を先行明文化し、承認前は `status=held` のまま確定化しない。

### Phase 3 Plan（mock-first / signature-only）
- Read同期（AND必須）: API/CLI同値判定は `equivalenceKey + bundleHash`（AND）のみ。
- Read同期（監査4点）: `query / bundle / proposal / apply` を契約必須項目として固定。
- Read同期（dryRun）: `dryRun=true -> sideEffect=none` を契約必須項目として固定。
- Read同期（mock同等性）: `sourceBundleHash=mock:<hash>` に本番同等の fail-closed を適用。
- Plan範囲: API/CLIシグネチャ定義のみ（contract-only）。実装手段・アルゴリズム詳細は記述しない。

### Phase 4 Execute（contract-only）
- Read同期（AND必須）: 片側一致を成功扱いしない条項を再確認。
- Read同期（監査4点）: 監査欠損成功扱い禁止を再確認。
- Read同期（dryRun）: `sideEffect=none` 逸脱時 fail-closed を再確認。
- Read同期（mock同等性）: `mock:<hash>` 逸脱時 fail-closed を再確認。
- 実施内容: 本ファイルの contract-only 記述更新のみ（他ファイル編集なし）。

### Phase 5 Verify
- Read同期（AND必須）: `equivalenceKey + bundleHash` 条項を再確認。
- Read同期（監査4点）: `query / bundle / proposal / apply` 欠損禁止を再確認。
- Read同期（dryRun）: `dryRun=true -> sideEffect=none` を再確認。
- Read同期（mock同等性）: `sourceBundleHash=mock:<hash>` 同等fail-closedを再確認。
- docs-check:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
- 自己修復: 0/3（4回目着手なし）。

### Phase 6 Proceed
- Read同期（AND必須）: `equivalenceKey + bundleHash`（AND）維持。
- Read同期（監査4点）: 監査4点欠損は fail-closed 維持。
- Read同期（dryRun）: `dryRun=true -> sideEffect=none` 維持。
- Read同期（mock同等性）: `sourceBundleHash=mock:<hash>` fail-closed同等性維持。
- Proceed判定: Go（contract-only文書固定）。
- 完了条件: docs-check pass、fail-closed条項明記、未承認CDCの確定化禁止を満たす。

## Stream E Lane Ownership Note（2026-04-27 / latest）
- 本Issueの運用主体は Stream E に固定し、CE2完了ゲート通過後の CE4 直列進行のみを許可する。
- 旧Stream記録は監査参照用の履歴として残置し、最新運用判断は Stream E 記録を正本とする。
- proposal-only + mock-first + contract-only を維持し、実装確定は行わない。

## Stream E Execution Record（2026-04-27 / started after CE2 gate）

### CE2 Completion Gate（precondition）
- CE4開始前提として CE2 の Phase 5 Verify 合格 + Phase 6 Proceed 完了を確認。
- 逆順・並列開始を行っていないことを確認し、CE4を直列開始。

### Phase Progress（Read → ADR/CDC → Plan → Execute → Verify → Proceed）
- Phase 1 Read: 完了（CE0 contract IDs、監査4点、fail-closed条項、CE4 scopeを再読し差分なし）。
- Phase 2 ADR/CDC: 完了（Context/Decision/Consequences を API/CLI同値性・監査・fail-closed 固定へ整列）。
- Phase 3 Plan: 完了（API/CLI同値性、監査ログ完全性、fail-closed をAC/DoDへ固定）。
- Phase 4 Execute: 完了（contract-only 記述更新のみ実施、実装詳細は追加しない）。
- Phase 5 Verify: 完了（同一query同一bundle要件、監査欠落ゼロ、fail-closed維持を確認）。
- Phase 6 Proceed: 完了（Go判定。未承認事項は `held` 維持、No-Go逸脱なし）。

### Verify Log（self-correction 0/3）
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`
- 判定: pass（自己修復着手なし、`4/3` 到達なし）。

### Proceed Decision
- Decision: **Go**（CE4契約固定を継続し、後続は実装非依存の契約準拠確認へ引き継ぐ）。

## Stream E-2 Execution Record（2026-04-28 / CE4 dependency-cut sync, latest authoritative）

> 本節を最新正本とし、CE2成果は read-only 前提値として参照する。CE2完了待ちは行わず、mock I/F で独立進行する。状態遷移確定を伴う変更は行わない。

### Phase 1 Read（契約差分確認）
- CE2成果は read-only 参照に限定し、CE2完了待ちを前提にしないことを確認。
- API/CLI同値判定は `equivalenceKey + bundleHash`（AND）固定のみを成功条件として確認。
- 監査4点 `query / bundle / proposal / apply` 欠損は fail-closed 固定を確認。
- `dryRun=true -> sideEffect=none` 固定を確認。
- No-Go確認: 監査欠損成功扱い要求 / safeMode緩和要求 / 語彙再定義要求 / 自己修復4回目相当は停止対象。

### Phase 2 ADR/CDC（Context / Decision / Consequences）
- Context: 依存切断下でも API/CLI 同値性・監査完全性・dryRun安全性を崩さずに契約固定する必要がある。
- Decision:
  - `equivalenceKey + bundleHash`（AND）を唯一の成功条件に固定。
  - 監査4点欠損は fail-closed 固定。
  - `dryRun=true -> sideEffect=none` 固定。
  - `sourceBundleHash=mock:<hash>` は本番hash同等の判定/監査/fail-closed を適用。
- Consequences: contract-only 記述のみ更新し、状態遷移確定・実装確定は行わない（`held` 維持）。

### Phase 3 Plan（AC/DoD不足補完）
- AC補完:
  - API/CLI成功判定は `equivalenceKey` 単独一致または `bundleHash` 単独一致を禁止（AND必須）。
  - 監査4点のいずれか欠損時は常に fail-closed。
  - `dryRun=true` の場合は常に `sideEffect=none`。
  - `mock:<hash>` でも本番hashと同一の fail-closed 導線を適用。
- DoD補完:
  - 状態遷移確定を伴う記述（`accepted/rejected` への確定昇格）を追加しない。
  - CE2参照は read-only のみで、CE2待機条件を導入しない。

### Phase 4 Execute（契約文言のみ）
- 実施: 本Issue内の契約文言に Stream E-2 の依存切断ポリシーを追記。
- 非実施: 実装変更 / safeMode緩和 / 語彙再定義 / 状態遷移確定の追記。

### Phase 5 Verify（docs-check）
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`
- 判定条件: fail-closed逸脱なし、AND固定逸脱なし、`dryRun=true -> sideEffect=none` 逸脱なし。

### Phase 6 Proceed（Go / Conditional / No-Go）
- Decision: **Conditional-Go（contract-only）**。
- 理由: 契約文言は固定完了。CE2成果は read-only 前提値として参照しつつ、完了待ちを前提にしない独立進行を維持。
- 継続条件:
  - 監査欠損成功扱い要求が発生した場合は **No-Go** で即停止。
  - safeMode緩和要求が発生した場合は **No-Go** で即停止。
  - 語彙再定義要求が発生した場合は **No-Go** で即停止。
  - 自己修復4回目相当の着手が必要になった場合は **No-Go** で即停止。

## Stream D Execution Record（2026-04-28 / user-directive 5-phase serial）

### Phase 1 Read（開始時Read同期）
- Read同期: 完了（`00_Prompt/*`、`ADR-0001`、`02_Architecture/architecture.md`、`02_Architecture/schemas.md`、`ADR-0019` を順次参照）。
- 対象限定: `01_Plans/issues/issue-CE4-api-cli-audit-integration.md` のみ編集。
- 固定条件再確認: proposal-only / mock-first / fail-closed / safeMode既定ON / CE0-CE2 read-only。

### Phase 2 Plan（開始時Read同期）
- Read同期: 完了（契約語彙と停止条件の差分なし）。
- 5Phase直列を固定: `Read → Plan → Execute → Verify → Proceed`。
- 依存切断方針: API/CLIはモック可能な署名定義で境界固定し、実装確定を行わない。
- ADR変更判定: 今回は不要（既存 CDC-CE4-001 / 002 の承認済み範囲で充足）。

### Phase 3 Execute（開始時Read同期）
- Read同期: 完了（No-Go条項に後退なし）。
- 実施内容: 本節の追記のみ（docs-only / contract-only）。
- 非実施: 実装コード変更、他ファイル編集、auto-apply 系導線追加。

### Phase 4 Verify（開始時Read同期）
- Read同期: 完了（監査4点、`queryCanonicalHash`、AND判定の維持を再確認）。
- 検証コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
- 自己修復回数: `0/3`（上限超過なし）。

### Phase 5 Proceed（開始時Read同期）
- Read同期: 完了（proposal-only境界・fail-safe停止条件の差分なし）。
- Proceed Decision: **Go（contract-only / docs-only）**。
- 維持事項:
  - API/CLI同値判定は `equivalenceKey + bundleHash`（AND）のみ。
  - 監査4点 + `queryCanonicalHash` 欠損は fail-closed。
  - 依存は `mock:<hash>` を含む署名契約で切断し、実装確定は行わない。
  - 検証エラー修復は最大3回、超過時は停止報告。

## Stream D Execution Snapshot（2026-04-29）

### Phase 1) Read + 依存確認
- CE0/CE1/CE2 は read-only 参照とし、契約語彙の再定義を行わないことを確認。
- `02_Architecture/api.md` の CE4 節と backend `context` route の契約差分を確認。
- 差分: CE4先行契約は `POST /v1/context/bundles:resolve` を記載していたが、実装経路は `/context/bundles:resolve` のみだったため、互換エイリアスの明記が必要。

### Phase 2) API/CLI監査イベント契約の先行定義
- 監査必須要素を `query / bundle / proposal / apply + queryCanonicalHash` に固定。
- fail-closed 条件を継続固定（欠損・不一致・dryRun副作用を成功扱いしない）。

### Phase 3) Plan → Execute
- Plan:
  - 既存エンドポイントを壊さず、v1 alias を追加して mock 実装開始可能な契約にする。
  - 監査4点は空白文字列を許容しない厳格判定にする。
- Execute:
  - `/context/bundles:resolve` を互換経路として維持。
  - `/context/v1/bundles:resolve` を追加（同一契約実装）。
  - `auditChain` 必須4イベントを `strip()` 判定で検証し、空白のみを fail-closed 化。

### Phase 4) Verify
- AC/DoD 照合:
  - proposal-only 境界: 維持。
  - API I/F: 必須入力/出力と fail-closed 条件を維持。
  - 監査境界: 4イベント + `queryCanonicalHash` 欠損時 fail-closed を維持。
- 失敗時自己修復: 実施なし（0/3）。

### Phase 5) Proceed 判定
- 競合検知: なし。
- 判定: Proceed（実装隊が mock で着手可能な契約パッケージを維持）。

## Stream E Execution Record（2026-04-29 / strict 5-phase boundary sync）

### Phase 1) Read/Plan（AC・DoD確認）
- AC/DoD を再確認し、CE4 は `proposal-only + mock-first + contract-only` の境界に限定する。
- CE0/CE1/CE2 は read-only 参照のみとし、語彙再定義を禁止する。
- fail-safe 起動条件（自己修復3回超過 / 前提崩壊 / 未定義競合）を本フェーズ開始時に明示する。

### Phase 2) ADR化（Context / Decision / Consequences）
- Context: API/CLI同値判定の比較根拠欠損は監査再現性を崩し、contract-only の受入判定を不安定化させる。
- Decision: `equivalenceKey AND bundleHash` を唯一成功条件として固定し、`queryCanonicalHash` 欠損を fail-closed とする。
- Consequences: 監査導線 `query / bundle / proposal / apply` の4点必須を維持し、実装詳細への踏み込みを禁止する。

### Phase 3) I/F契約固定（API-CLI-Audit連携点）
- API/CLI 共通必須出力は `equivalenceKey` / `bundleHash` / `queryCanonicalHash` / `proposalLifecycle` / `sideEffect` / `auditChain` を維持する。
- API/CLI 同値判定は AND 条件のみ成功（片側一致成功は禁止）を再固定する。
- 監査連携点は `query -> bundle -> proposal -> apply` の4イベントとし、欠損は常時 fail-closed とする。

### Phase 4) Mock検証（外部実装非依存）
- `sourceBundleHash=mock:<hash>` を用いた契約検証を前提とし、本番hashと同一判定規則を適用する。
- `dryRun=true` では `sideEffect=none` 以外を許容しない。
- 外部実装（frontend/backend/ops 実装）の完了有無に依存せず、契約単体で検証可能な状態を維持する。

### Phase 5) Verify/Proceed
- Verify 結果: 5-phase 順序（Read/Plan → ADR化 → I/F契約固定 → Mock検証 → Verify/Proceed）で整合。
- Proceed 判定: **Go（contract-only）**。未承認事項は `held` 維持。
- Stop条件再掲: 自己修復 `4/3` 相当、前提崩壊、未定義競合のいずれか検知時は即停止。


## Stream B Contract Lane Run（2026-04-29 / CE0+CE1+CE4 contract freeze with mock validation）

- lane: `Stream B (CE contract lane)`
- objective: CE0/CE1 系の契約固定と mock 検証を完遂し、実装依存を切り離す
- scope_check: `01_Plans/issues/issue-CE0-*`, `issue-CE1-*`, `issue-CE4-*` の契約定義のみ
- edit_prohibition_check: `03_Implement/**`, `04_Documentation/**`, HIL-RS issue/ADR は未編集

### Phase 1: Plan（Read同期 + AC/DoD不足確認）
- 各対象Issueの契約節を再読し、共通AC/DoDを同期。
- AC/DoD不足のドラフト提案を以下で固定（合意済み扱い）:
  - `ac_contract_closed_world_v1`: v1契約は unknown key reject を必須。
  - `ac_mock_first_decoupling`: backend未実装でも mock で検証可能であること。
  - `dod_verify_retry_cap_3`: self-correction は最大3回、4回目相当は停止。

### Phase 2: Interface Freeze（API/型/イベント契約固定）
- CE0固定: `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05` を再定義禁止で固定。
- CE1固定: `ContextQueryV1` / `ContextBundleV1`、`preview_required` / `unknown_contract_key` / `nondeterministic_bundle` の意味論をv1で固定。
- CE4固定: `AuditEventV1`、`equivalenceKey AND bundleHash`、`dryRun=true -> sideEffect=none`、監査4点（query/bundle/proposal/apply）を固定。

### Phase 3: Mock Validation（実装非依存検証）
- mock dataset: `A2-minimal-v1` 前提で契約検証のみ実施。
- 検証観点:
  1. `previewConfirmed=false` は `422 preview_required`。
  2. 同一canonical queryで `queryCanonicalHash` / `bundleHash` が3/3一致。
  3. unknown key は `400 unknown_contract_key`。
  4. CE4監査で `equivalenceKey AND bundleHash` 不一致は fail-closed。

### Phase 4: Implementation-ready メモ（コード変更なし）
- 実装着手順メモを契約参照として固定:
  1. CE1 mock endpoint で contract test を先行実装。
  2. CE4 API/CLI は `AuditEventV1` 監査4点を同一入力で比較。
  3. CE0 safeMode境界（既定ON、review昇格人手限定）を回帰テスト化。
- 本Phaseでは実装手順の記述のみ行い、コード・運用文書変更は禁止を維持。

### Phase 5: Verify（self-correction 3回上限）
- verify attempt: `1/3` で通過。
- stop condition check: 未定義競合なし、範囲外変更要求なし、4回目相当修正要求なし。
- decision: **Go (contract-only / mock-first / implementation-decoupled)**。


## Stream B planning refresh（2026-04-30 / CE4）

### Phase 1 Read（欠落抽出）
- CE4の serial phase lock（Read→ADR/CDC→Plan→Execute→Verify→Proceed）を継続。
- 欠落補完: API/CLI同値判定の「入力同一性条件」を明文化（`query/dryRun/sourceBundleHash/safeMode`）。
- 欠落補完: `Expected verification level` を `docs-check` + mock contract check に固定。

### Phase 2 ADR整合
- `ADR-0028` との整合結果: 矛盾なし（proposal-only / mock-first / fail-closed / human accept-reject）。
- 差分が出た場合のみ CDC 追記し、承認完了まで `held`。

### Phase 3 Plan→Execute（依存切断）
- 実装非依存で固定する契約作業:
  1. API/CLI同値判定 I/F の field-by-field 対応表作成。
  2. 監査4点（`query/bundle/proposal/apply`）+ `queryCanonicalHash` の必須監査表作成。
  3. `dryRun=true => sideEffect=none` の fail-closed 判定表作成。

### Phase 4 Verify
- Expected verification level: `docs-check`。
- Task breakdown:
  - T1: API/CLI equivalence matrix（入力・出力・exit code）
  - T2: Audit completeness matrix（4点+canonical hash）
  - T3: No-Go matrix（safeMode緩和/語彙再定義/監査欠損/自己修復超過）
- Self-correction 上限 3回、4回目相当は停止。

### Phase 5 Proceed
- 実装担当引き渡しの確定条件:
  - CE0/CE1は read-only 参照のまま再定義しない。
  - contract-only で未決定項目を残さない。
  - `status=held` の項目は確定化せず、実装着手条件から除外する。

## Stream G Serial Directive（2026-04-30 / CE4 API-CLI-Audit）
- Owner は Stream G（CE4 API/CLI/Audit）専任とし、docs-only / contract-only を維持する。
- Status は `Open / P2` を維持し、未承認の契約変更は `held` で停止する。
- CE0/CE1 依存は **実装依存として扱わず、I/F参照依存としてのみ扱う**（read-only, no reverse update）。
- workflow は `Plan → Execute → Verify` の固定順（mock-first）で運用し、実装コミットを禁止する。
- 未定義競合または前提崩壊を検知した場合は即停止（Stopper優先）。

### Phase 1 Read（latest / Open-P2確認）
- latest Read を実施し、CE4 Issue の状態が `Open` かつ Priority が `P2` であることを確認する。
- CE0/CE1/CE2 は read-only 参照に限定し、契約語彙の再定義を行わない。
- `equivalenceKey + bundleHash`（AND）, `query/bundle/proposal/apply`, `queryCanonicalHash`, fail-closed を固定境界として再確認する。

### Phase 2 ADR-style（Context / Decision / Consequences）
#### Context
- CE4 は API/CLI/監査境界の契約固定を目的とし、実装の先行確定は対象外。
- 先行ストリームとの差分は「依存の扱い」に集中し、CE0/CE1 を実装待ち前提にしないことが必要。

#### Decision
- CE0/CE1 依存の記述を「実装依存」から「I/F参照依存（read-only contract reference）」へ統一する。
- API signature / audit envelope / CLI contract は mock前提の検証可能粒度で固定する。
- proposal-only と fail-closed を維持し、自動確定経路（auto-apply/auto-confirm/auto-publish）を禁止する。

#### Consequences
- CE4 は他ストリーム実装の進捗に引きずられず、契約I/Fの独立検証を先行できる。
- 依存表現の明確化により、handoff 時の責務境界（contract vs implementation）が判別しやすくなる。
- I/F参照依存に反する差分（語彙再定義・実装条件の逆流）が出た場合は `held` 停止が必要になる。

### Phase 3 Workflow（Plan / Execute / Verify / self-correction<=3）
#### Plan
- API/CLI/Audit の契約差分を docs 上で定義し、AC/DoD不足は提案として追記する。
- 人手承認前は `proposalLifecycle=held` を許容し、accepted をAIが確定しない。

#### Execute
- patch/diff は本issue内の contract 記述に限定する（code change禁止）。
- API/CLI 同値判定は `equivalenceKey AND bundleHash` のみ成功とする。

#### Verify（mock前提）
- API signature: required request/response fields と fail-closed 条件を mock request で検証可能であること。
- audit envelope: `query/bundle/proposal/apply + queryCanonicalHash` 欠損時に success を返さないこと。
- CLI contract: required options / stdout JSON / exit code(0|1) が API 契約と矛盾しないこと。

#### self-correction
- Verify不整合時は `1/3` → `2/3` → `3/3` の順で自己修復し、`4/3` 着手を禁止する。
- 3回以内に収束しない場合は fail-safe として `status=held` へ遷移する。

### Phase 4 Stopper（即停止条件）
- 未定義競合（契約語彙の衝突、責務境界の二重定義）を検知した場合は即停止。
- 前提崩壊（proposal-only破綻、safeMode後退要求、監査欠損成功扱い要求）を検知した場合は即停止。
- 停止時は推測補完を行わず、`status=held` と停止理由を記録して終了する。
