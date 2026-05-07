# Issue Draft: CE4 API/CLI/監査統合（Stream H / CE4専任 / contract-only）

- Type: Feature request
- Status: Draft (Contract Freeze Candidate)
- Priority: P2
- Owner: Stream C（CE下流 proposal-only）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Editable: `issue-CE4-api-cli-audit-integration.md` のみ
- Related Backlog: `CE-4`
- Related ADR/Spec: `ADR-0028`, `ADR-0016`, `ADR-0017`, `02_Architecture/api.md`
- Dependencies: `01_Plans/issues/issue-CE0-contract-freeze.md`（契約依存）, `01_Plans/issues/issue-CE1-context-query-bundle-foundation.md`（ContextBundle I/F依存; mockで先行可能）
- Verification: `docs-check`

## Mission（実装非依存の契約固定）
- CE4 API/CLI/監査統合を、実装方式から独立した**契約レベル**で固定する。
- `proposal-only` を強制し、auto-apply / auto-confirm / auto-publish を禁止する。
- `fail-closed` を既定とし、監査必須項目の欠損は成功扱いしない。
- 監査イベント4点セット（`query` / `bundle` / `proposal` / `apply`）を必須契約として固定する。

---

## Phase 1: 要件抽出（Read同期済み）

### 1.1 API契約要件（実装非依存）
1. **同値性の成功条件**は `equivalenceKey AND bundleHash` の同時成立のみ。
2. APIは `proposal-only` 以外の実行モードを成功として扱わない。
3. 監査イベント4点セットの**順序整合**（`query -> bundle -> proposal -> apply`）を要求する。

### 1.2 CLI契約要件（実装非依存）
1. CLIは API と同一の同値条件（AND条件）を適用する。
2. CLI終了時は、少なくとも次の失敗種別を識別可能にする。
   - 入力違反
   - 監査違反（必須キー欠損・順序欠損・重複不整合）
   - 同値不成立（`equivalenceKey` または `bundleHash` 不一致）
3. CLIは監査違反時に常に fail-closed とし、成功コードを返さない。

### 1.3 監査ログ契約要件（実装非依存）
1. 各監査イベントに**共通必須キー**を持たせる（Phase 3で固定）。
2. APIとCLIは同一の `equivalenceKey` / `queryCanonicalHash` / `bundleHash` を共有参照する。
3. 監査ログは追跡可能性（traceability）・改ざん耐性（tamper-evidence）・再現性（reproducibility）を満たす。

---

## Phase 2: ADR-style 明文化（Context / Decision / Consequences）

### Context
- CE4 は API / CLI / 監査の3境界を跨ぐため、実装前に契約固定しないと後工程で解釈ずれが生じる。
- 既存文書には同値条件や監査ゲートの要素が存在するが、CE4最小契約として単一箇所に集約されていない。

### Decision
1. **契約優先方針**
   - 本Issueを CE4 API/CLI監査統合の契約固定ドラフトとして扱う。
   - 実装方式（転送基盤、保存先、内部フレームワーク）は本契約のスコープ外とする。
2. **追跡可能性要件**
   - 4イベントは同一 `equivalenceKey` で連結可能であること。
   - `queryCanonicalHash` と `bundleHash` により入力正規化系と成果物系を再結線できること。
3. **改ざん耐性要件**
   - 監査イベントは `schemaVersion` を含み、検証側で必須キー欠損を機械判定可能であること。
   - `sourceBundleHash` は `sha256:<64hex>` または `mock:<64hex>` を許容し、どちらも同じ fail-closed 規律で扱うこと。
4. **再現性要件**
   - 同一 `queryCanonicalHash` + `bundleHash` + `equivalenceKey` の組で、同一判定結果を再演算できること。

### Consequences
- 実装チームは mock fixture で契約適合性を先に検証できる。
- 監査欠損時の挙動が「失敗固定」となるため、運用判断のブレを抑制できる。
- ADR/API本文に反映する際の差分単位（同値条件・監査キー・失敗分類）が明瞭になる。

---

## Phase 3: 契約定義（Schema / ID連携 / 失敗時挙動）

### 3.1 監査イベント最小スキーマ（共通必須）
- `eventType` : enum [`query`,`bundle`,`proposal`,`apply`]
- `timestamp` : RFC3339 UTC
- `equivalenceKey` : string (非空)
- `queryCanonicalHash` : `sha256:<64hex>`
- `bundleHash` : `sha256:<64hex>`
- `actor` : object `{ principalType, principalIdMasked }`
- `result` : enum [`ok`,`ng`]
- `channel` : enum [`api`,`cli`]
- `command` : string (CLIは実行コマンド、APIはエンドポイント識別子)
- `schemaVersion` : string (SemVer)
- `sourceBundleHash` : `sha256:<64hex>` | `mock:<64hex>`

### 3.2 ID連携契約
1. 1トランザクション単位で `equivalenceKey` は一意。
2. `query` / `bundle` / `proposal` / `apply` の4イベントで `equivalenceKey` は不変。
3. `queryCanonicalHash` と `bundleHash` は API/CLI 間で一致しなければならない。
4. `proposal` が `ok` の場合でも `apply` 欠損は契約違反（No-Go）。

### 3.3 失敗時挙動（fail-closed）
- 必須キー欠損: **監査違反**として失敗。
- 順序欠損（例: `apply` が先行）: **監査違反**として失敗。
- 重複イベント（同一 `eventType` + `equivalenceKey` で矛盾結果）: **監査違反**として失敗。
- 不正操作（auto-apply / auto-confirm / auto-publish 検出）: **ポリシー違反**として失敗。
- 同値不成立（AND条件未達）: **同値違反**として失敗。

---

## Phase 4: mock検証（正常/欠損/重複/不正操作）

### 4.1 正常系
- Case N1: `query -> bundle -> proposal -> apply` 完備、共通必須キー完備、AND条件成立。
- 期待結果: 契約適合（Go）。

### 4.2 欠損系
- Case M1: `apply` 欠損。
- Case M2: `schemaVersion` 欠損。
- Case M3: `queryCanonicalHash` 欠損。
- 期待結果: すべて fail-closed（No-Go）。

### 4.3 重複系
- Case D1: 同一 `equivalenceKey` + `eventType=proposal` が2件で `result` 不一致。
- Case D2: 同一 `equivalenceKey` で `bundleHash` が複数値。
- 期待結果: 監査違反として No-Go。

### 4.4 不正操作系
- Case U1: `command` が auto-apply 相当。
- Case U2: `proposal-only=false` 相当の実行痕跡。
- 期待結果: ポリシー違反として No-Go。

### 4.5 mock fixture規約
- 実装依存を切り離すため `sourceBundleHash=mock:<64hex>` を許容。
- mock/real いずれも同一の必須キー検証と fail-closed を適用。

---

## Phase 5: Verify（AC/DoD監査 + 停止条件）

### Acceptance Criteria（AC）
- [x] API/CLI/監査ログの必要項目を抽出した。
- [x] ADR-style（Context / Decision / Consequences）を定義した。
- [x] 追跡可能性・改ざん耐性・再現性の要件を明記した。
- [x] 監査イベントスキーマ、ID連携、失敗時挙動を定義した。
- [x] 正常/欠損/重複/不正操作の mock 検証ケースを定義した。

### Definition of Done（DoD）
- [x] 本Issue単体で CE4契約を実装非依存に読解できる。
- [x] `proposal-only` / `fail-closed` / `safeMode既定ON` を後退させる記述がない。
- [x] 未確定点を明示し、確定済み事項と分離した。

### 未確定点（停止報告対象）
1. CLI終了コードの**具体値マッピング**（数値割当）は本Issueでは未固定。
2. `principalIdMasked` の不可逆化方式（ハッシュ/トークン化）は本Issueでは未固定。
3. 監査転送基盤（保存先・配送保証・署名方式）は本Issueでは未固定。

> 停止条件: 上記未確定点を確定仕様として扱う要求が来た場合、CE4契約の範囲逸脱として停止し、上位ADRでの判断を要請する。


## Stream C execution log（2026-05-05 / Draft gate解除準備, contract-only）

### Phase 1: Read
- `ADR-0028` / `ADR-0016` / `ADR-0017` / `02_Architecture/api.md` と本Issue契約を照合。
- `proposal-only`、監査4点、AND同値条件、fail-closed がDraft契約として一貫していることを確認。

### Phase 2: Plan（AC/DoD不足補完）
- AC補完:
  - [ ] Open前に「未確定点は実装仕様に昇格しない」境界を明示。
  - [ ] API/CLI共通で同値違反・監査違反・ポリシー違反の3分類が再読可能。
- DoD補完:
  - [ ] `proposal-only` 後退ゼロ、`auto-*` 禁止、`safeMode既定ON` 後退ゼロ。
  - [ ] self-correction `<=3`、4回目相当は `Stop`。

### Phase 3: Execute（proposal-only）
- 本Issueの契約文整理のみ実施（コード・ADR本文・API実装は非実施）。
- mock-first 原則を維持し、実装依存事項（終了コード数値/匿名化方式/転送基盤）は未確定のまま固定。

### Phase 4: Verify（gate条件整合）
- Verify観点:
  1. contract-only scope逸脱なし。
  2. 監査イベント最小スキーマ・ID連携・失敗時挙動の整合。
  3. 未確定点が「停止報告対象」として隔離されている。
- self-correction: `0/3`。

### Phase 5: Proceed（Open条件判定）
- 判定: **Hold**（依存 `CE-4` Open gate の確定証跡待ち）。
- 昇格提案条件:
  1. 依存確定証跡（日時/承認者/対象/判断）を記録。
  2. docs-check再実行で契約欠落ゼロを確認。
- 停止条件: 未確定点の仕様確定要求、self-correction超過、未定義競合発生時は **Stop**。

## Open化最終整備（proposal-only / 2026-05-04）

### Read→ADR/CDC→Plan→Execute→Verify→Proceed（固定運用）
1. **Read**: 上位根拠（ADR / schemas / 関連Issue）との差分を再読して語彙ドリフトを検知する。
2. **ADR/CDC**: Context / Decision / Consequences を本Issue内で閉じる（外部依存で確定しない）。
3. **Plan**: Open判定の AC / DoD / Validation / Stop 条件を先に固定する。
4. **Execute**: **blocker明文化・Open化条件定義・AC/DoD整備のみ** 実施し、実装化は行わない。
5. **Verify**: docs-check を基準に、自己修復は最大3回（4回目相当は Stop）で運用する。
6. **Proceed**: 依存確定と Approval Record が充足した場合のみ Proceed、それ以外は Hold/Stop。

### Blocker明文化（Open不可時の固定理由）
- 依存ステータス未確定、または承認証跡（日時/承認者/対象/判断/evidence）の欠落。
- proposal-only 契約（実装禁止 / auto-*禁止 / fail-closed）に抵触する要求の混入。
- Verify再試行が3回を超過、または未定義競合（契約衝突・責務分離崩壊）の検知。

### Open化条件（proposal-only gate）
- [ ] 条件1: 本Issue単体で Context/Decision/Consequences・AC・DoD・Validation・Proceed tri-state が再読可能。
- [ ] 条件2: docs-check の pass 記録と self-correction `<=3` が記録済み。
- [ ] 条件3: 依存確定証跡と Approval Record の最小項目が充足。
- [ ] 条件4: 実装タスク化を行わず、未承認依存を確定扱いしていない。

### Verify失敗時 Self-Correction ルール
- Attempt 1: 文言矛盾・欠落メタの修正。
- Attempt 2: Gate条件と Stop条件の再整列。
- Attempt 3: 依存/承認証跡の未充足を Hold理由へ明示。
- 4回目相当: **Stop**（超過または依存崩壊として終了）。


## Stream C update（2026-05-05 / Read Sync → Proceed準備）

### 1) Read Sync
- `ADR-0028` / `ADR-0016` / `ADR-0017` / `02_Architecture/api.md` と本Issueを再同期し、契約語彙を以下に固定した。
  - 同値判定: `equivalenceKey AND bundleHash`
  - 実行制約: `proposal-only`（auto-*禁止）
  - 失敗規律: `fail-closed`
  - 監査系列: `query -> bundle -> proposal -> apply`
- 判定: CE1/CE2 実装待ちなしで、mock I/F による検証観点固定が可能。

### 2) ADR（Context / Decision / Consequences）補強
- **Context**: CE1/CE2 未実装段階でも CE4 契約を先に凍結しないと API/CLI/監査の責務境界が後工程で分岐する。
- **Decision**:
  1. CE4 は contract-only を維持し、実装 I/F は `mock:<64hex>` を正規入力として検証対象化する。
  2. API/CLI 双方で監査欠損を成功扱いしない（監査欠落ゼロ主義）。
  3. 失敗分類は `入力違反 / 監査違反 / ポリシー違反 / 同値違反` の4区分で固定する。
- **Consequences**: 下流は CE1/CE2 完了前に fixture 駆動で判定器を先行実装できる。

### 3) Plan（AC/DoD補完提案）
#### AC補完
- [x] CE1/CE2 未実装でも成立する mock I/F 境界（`sourceBundleHash=mock:<64hex>`）を明記。
- [x] 失敗分類4区分（入力/監査/ポリシー/同値）を API/CLI 共通語彙として固定。
- [x] 監査欠落ゼロ観点（4イベント+必須キー欠損は全件No-Go）を明記。

#### DoD補完
- [x] fail-safe=fail-closed を明示（欠損・順序不整合・矛盾重複・auto-*検出を成功扱いしない）。
- [x] 再現性判定は `queryCanonicalHash + bundleHash + equivalenceKey` の組で決定論的に再演算可能。
- [x] 下流引継ぎ時に「未確定点を実装仕様へ昇格しない」境界が保持される。

### 4) Execute（監査キー・失敗時fail-safe定義）
#### 監査キー固定（共通必須）
- `eventType`, `timestamp`, `equivalenceKey`, `queryCanonicalHash`, `bundleHash`, `actor`, `result`, `channel`, `command`, `schemaVersion`, `sourceBundleHash`

#### fail-safe（=fail-closed）判定表
- `必須キー欠損` → 監査違反 / No-Go
- `イベント順序不整合` → 監査違反 / No-Go
- `矛盾重複（同一eventType+equivalenceKeyで結果矛盾）` → 監査違反 / No-Go
- `auto-apply|auto-confirm|auto-publish痕跡` → ポリシー違反 / No-Go
- `equivalenceKey AND bundleHash 未成立` → 同値違反 / No-Go

### 5) Verify（再現性・監査欠落ゼロ観点）
- 再現性: 同一3キー組で同一判定結果に収束することを mock fixture で再計算可能。
- 監査欠落ゼロ: 4イベントのどれか1つでも欠落した時点で No-Go。
- self-correction: `0/3`（超過なし）。

### 6) Proceed（下流引継ぎ）
- 状態: **Proceed (Contract Freeze for Downstream)**
- 引継ぎ入力:
  1. mock fixture は `mock:<64hex>` と `sha256:<64hex>` の双方を同一検証器に通す。
  2. CLI終了コードの数値割当は未確定のまま（分類語彙のみ固定）。
  3. 監査転送基盤・匿名化方式は CE4 契約外（上位ADR判断待ち）。

## Stream CE4 Draft昇格準備（2026-05-06 / Read→Plan→Execute→Verify→Proceed）

### Read（根拠再同期）
- 再同期対象: `ADR-0028` / `ADR-0016` / `ADR-0017` / `02_Architecture/api.md` / 本Issue契約定義。
- 整合確認:
  - 同値条件 `equivalenceKey AND bundleHash` を維持。
  - `proposal-only` と auto-*禁止を維持。
  - 監査4イベント欠損時 fail-closed を維持。

### Plan（Open判断材料の固定）
- AC明確化:
  - [ ] Context / Decision / Consequences、AC、DoD、Validation、tri-state が単一文書で再読可能。
  - [ ] 失敗分類4区分（入力/監査/ポリシー/同値）が API/CLI 共通語彙として明示。
  - [ ] 未確定点（終了コード数値/匿名化方式/転送基盤）が「未確定」のまま隔離されている。
- DoD明確化:
  - [ ] contract-only 境界（実装非依存、mock-first、推測実装禁止）を維持。
  - [ ] self-correction `<=3`、4回目相当は Stop を明記。
  - [ ] 依存証跡未充足時は Proceed 不可（Hold/Stop）を再現可能。
- Validation明確化:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-CE4-api-cli-audit-integration.md`
  - `git diff --check -- 01_Plans/issues/issue-CE4-api-cli-audit-integration.md`
  - `git diff -- 01_Plans/issues/issue-CE4-api-cli-audit-integration.md`

### Execute（文書整備のみ）
- 実施: Draft→Open判定の材料（AC/DoD/Validation/Stop条件）を明確化。
- 非実施: API/CLI実装、監査基盤選定、未確定点の確定化。

### Verify（停止条件付き）
- Verify結果: **Hold維持**（依存 `CE-4` Open gate の確定証跡待ち）。
- self-correction: `0/3`。
- Stop条件再掲: 未確定点を確定仕様として扱う要求、または修復4回目相当で Stop。

### Proceed判定（現時点）
- 判定: **Hold（Draft継続）**
- Open移行に不足する項目:
  1. 依存確定証跡（日時/承認者/対象/判断/evidence）。
  2. Approval Record 実値の記録。
- Stop再掲: allowlist外編集、契約語彙衝突、self-correction超過、safeMode後退要求を検知した場合は即停止。


## Stream H Draft Promotion Prep（2026-05-04 / proposal-only）

### Phase 1 Read
- 最新メタ確認: `Status=Draft`、`docs-only / contract-only`、`Verification=docs-check`。

### Phase 2 ADR明文化（Context / Decision / Consequences）
- Context: CE4はAPI/CLI/監査の境界横断であり、実装前に契約凍結が必要。
- Decision: Draft段階は契約文書の固定に限定し、実装仕様・実装指示を記載しない。
- Consequences: Open判定時の論点が `同値条件 / 監査キー / fail-closed` に収束する。

### Phase 3 Plan（Go / No-Go gate）
- Go: 4イベント契約、AND同値条件、禁止操作（auto-*）が矛盾なく記述され承認記録が揃う。
- No-Go: 承認欠落、監査キー欠落、契約語彙の衝突、Verify上限超過。
- Conditional(Hold): 契約整備は完了しているが承認待ち。

### Phase 4 Execute（proposal-only整備）
- 実施: 用語統一、CDC整備、Gate明文化。
- 非実施: API/CLI実装方法、終了コード数値の確定、監査基盤選定。

### Phase 5 Verify（最大3回修復）
- V1: 単一Issue内での整合。
- V2: proposal-only/fail-closed/auto-*禁止の残存。
- V3: Go/No-Go/Conditional 条件の相互排他性。

### Phase 6 Stopper
- 依存未確定、未承認確定化要求、契約競合疑義を検知した場合は停止して照会する。


## Stream G execution pass（2026-05-04 / CE4 P2）

### Phase Start Re-read
- 対象再読: `issue-CE4-api-cli-audit-integration.md` を再読し、API/CLI同値条件AND・監査4イベント・fail-closed契約を再確認。

### Plan → Execute → Verify → Proceed
- Plan: Open判定で必要な契約セット（C/D/Csq + AC/DoD + No-Go条件）を固定。
- Execute: 実装非依存の契約文言のみ整備し、コード/API変更は行わない。
- Verify: docs-check想定で契約矛盾（proposal-only逸脱/auto-*許容）を再点検。
- Proceed: 依存確定ログ未充足のため **Hold継続**。

### ADR task C / D / Csq
- Context: CE4はAPI/CLI/監査の3境界を跨ぎ、契約不一致が後工程障害に直結する。
- Decision: Draft段階で契約語彙と失敗分類を固定し、Open判断可能な記述密度へ統一する。
- Consequences: 実装着手前に同値判定と監査条件が安定し、再作業リスクを低減できる。


## Stream C (CE4) final handoff（2026-05-04 / 独立完了）

### Phase 1 Read（再Read + 契約参照キー整合）
- 参照対象を再Readし、契約参照キーを `equivalenceKey` / `queryCanonicalHash` / `bundleHash` / `sourceBundleHash` / `schemaVersion` に固定。
- CE1契約は **read-only参照** とし、CE4側では「参照キー整合のみ」を扱う（CE1本文の意味拡張は行わない）。
- 監査系列キーを `query -> bundle -> proposal -> apply` に固定し、順序欠損は監査違反で No-Go と再確認。

### Phase 2 ADR（Context / Decision / Consequences）
#### Context
- CE4はAPI/CLI/監査の境界横断タスクであり、実装前に接続計画（contract integration plan）を固定しないと下流で判定語彙が分岐する。
- CE1依存があっても、CE4は mock 前提で監査接続契約を先に確定できる。

#### Decision
1. CE4は **実装ではなく接続計画** を固定対象にする（contract-only）。
2. API/CLIの成功条件は `equivalenceKey AND bundleHash` を満たし、かつ監査4点セット完備時のみ成立。
3. `proposal-only` 強制、`auto-apply/auto-confirm/auto-publish` 禁止、違反時は fail-closed。
4. 失敗分類は `入力違反 / 監査違反 / ポリシー違反 / 同値違反` をAPI/CLI共通で保持。

#### Consequences
- 下流実装は CE1/CE2 完了前でも mock fixture で統合判定器を先行検証できる。
- 監査欠落を成功扱いしないため、運用時の判定揺れを抑止できる。
- CLI終了コードの数値、匿名化詳細、監査転送基盤は未確定のまま安全に分離できる。

### Phase 3 Plan（AC/DoD不足提案と合意）
#### AC追加提案（本Issueで合意）
- [x] CE1 read-only参照境界（CE4からCE1契約を再定義しない）を明記。
- [x] API/CLI監査統合は「4イベント完備 + 共通必須キー完備 + AND同値条件成立」を同時充足条件とする。
- [x] mock/real いずれも同一 fail-closed 判定規律を適用。

#### DoD追加提案（本Issueで合意）
- [x] 監査4点セットの欠損・順序不整合・矛盾重複をすべて No-Go で説明可能。
- [x] 未確定点（終了コード数値、匿名化方式、転送基盤）を実装仕様に昇格していない。
- [x] self-correction は最大3回、4回目相当は Stop を明記。

### Phase 4 Execute（mock前提 監査4点セット定義）
- `query`: 入力受理と `queryCanonicalHash` 確定イベント。
- `bundle`: `bundleHash` / `sourceBundleHash` 確定イベント（`sha256:<64hex>` または `mock:<64hex>`）。
- `proposal`: proposal-only 判定イベント（auto-*痕跡があれば即 No-Go）。
- `apply`: 実行可否の監査終端イベント（`proposal` 正常後のみ許可）。
- 4イベントすべてに共通必須キーを要求し、1件でも欠損なら fail-closed。

### Phase 5 Verify（Lint/整合 + 自己修復ルール）
- 検証対象: docs-check での文書整合、契約語彙整合、禁止事項（auto-*）不在。
- 自己修復: 失敗時は最大3回まで以下順で修復。
  1. 欠落キー/語彙ドリフト修正
  2. Gate条件（AC/DoD/Stop）再整列
  3. 依存未確定を Hold/Stop 理由として明示
- 4回目相当は **Stop**（致命的衝突または依存崩壊）。

### Phase 6 Proceed（handoff）
- 判定: **Proceed（CE4接続計画として独立完了）**。
- 下流への引継ぎ:
  1. CE1は read-only参照を維持し、CE4側で契約再定義を行わない。
  2. 監査判定器は mock/real 共通で4イベント完備性とAND同値条件を検証する。
  3. 未確定点の仕様確定要求が入った場合は CE4範囲逸脱として Stop し、上位ADR判断へエスカレーション。


## Draft gate解除準備（Open化判定の明文化 / 2026-05-05）

### Contract references（参照のみ・実装変更なし）
- `ADR-0028`（認知外在化フェーズ接続）
- `ADR-0016` / `ADR-0017`（契約境界・品質ゲート語彙）
- `02_Architecture/api.md`（API境界の単一正本）
- `01_Plans/issues/issue-CE0-contract-freeze.md`（契約依存）

### Open化条件（Draft gate解除の必要十分条件）
- [ ] O1: 本Issueの契約本文のみで、`proposal-only` / `fail-closed` / 監査4イベント順序が再読できる。
- [ ] O2: `equivalenceKey AND bundleHash` のAND同値条件が API/CLI 共通で明文化され、例外運用が記載されていない。
- [ ] O3: 未確定点（終了コード数値・匿名化方式・転送基盤）が「契約外」として隔離され、実装仕様へ昇格していない。
- [ ] O4: 依存証跡（CE0/関連ADRの更新日時・判断者・判断内容）を追記できる状態で、欠落時は Hold を維持する。
- [ ] O5: Verify の self-correction が `<=3` の範囲に収まり、4回目相当は Stop と明記されている。

### Proceed tri-state（Open判定）
- **Proceed**: O1〜O5 が全て充足し、依存証跡が記録済み。
- **Hold**: 契約本文は充足したが、依存証跡または docs-check 記録が未充足。
- **Stop**: self-correction 超過（4回目相当）、または契約衝突（proposal-only/ fail-closed 後退）を検知。


## Phase 6: Proceed（Open昇格）/ Hold（停止）

### Proceed（Open昇格）条件
- API/CLI/監査の契約が proposal-only 前提で閉じており、実装依存の記述を含まない。
- `equivalenceKey AND bundleHash`、4イベント順序、必須キー検証、fail-closed が同時に満たされる。
- 依存（CE0/CE1）は参照のみで、未確定項目を推測補完していない。

### Hold条件
- CE1の未確定仕様を前提にしないと CE4契約が成立しない。
- 監査イベント4点セット、または `proposal-only` / `auto-*禁止` のいずれかが欠落。
- 検証レベル（docs-check）を超える実装前提の確定要求が発生。

### Verify整合チェック（最終）
1. 依存表記（CE0/CE1）が read-only 参照に限定されている。
2. 検証レベルが `docs-check` で一貫している。
3. 停止条件が fail-safe（未確定=Hold）と一致している。

## Stream G pre-open gate pass（2026-05-05 / proposal-only）

### Phase 1: Read（依存・停止条件の再確認）
- 本Issueを単体再読し、`Draft gate` 判定に必要な `AC/DoD/Proceed tri-state/Stopper` の存在を確認。
- 依存未解決のまま実装へ進まない原則を再固定（推測Go判定を禁止）。

### Phase 2: Plan（不足AC/DoD提案）
- AC追加提案（Open化ゲート）:
  - [ ] 依存確定証跡（日時・承認者・対象・判断・evidence）が明記される。
  - [ ] Approval Record 未充足時は `Proceed=Hold` を維持する。
  - [ ] docs-only / proposal-only の境界逸脱がない。
- DoD追加提案（Open化ゲート）:
  - [ ] Open可否を `Proceed/Hold/Stop` 三値で再判定可能。
  - [ ] self-correction `<=3` を超えた場合は `Stop` へ遷移。

### Phase 3: ADR（Context / Decision / Consequences）
- Context: 依存が揃うまでの待機期間でも、Open判定材料を先に固定して再作業を削減する必要がある。
- Decision: 実装・本文改稿には進まず、Open化ゲートと依存I/F（mock可能範囲）だけを先行定義する。
- Consequences: 依存完了後に即Open判定できる一方、未承認時の誤Proceedを抑止できる。

### Phase 4: Execute（依存・検証条件・停止条件の明文化のみ）
- Dependency I/F（mock-first）:
  - `ApprovalRecordIF`: `{approved_at, approved_by, target_issue, decision, evidence}`
  - `DependencyStatusIF`: `{dependency_id, status, confirmed_by, confirmed_at}`
  - `GateVerdictIF`: `{proceed_decision, unmet_conditions[], checked_at}`
- mock運用規約:
  - 依存本体未接続時は `mock:*` 値でI/F形式のみ検証。
  - mockでも fail-closed を維持し、必須キー欠損は `NoGo/Hold`。

### Phase 5: Verify（Open化ゲート検証）
- 検証条件:
  1. `AC/DoD/Proceed tri-state/Stopper` が本文内で再読可能。
  2. 依存証跡が未充足なら `Hold` のまま。
  3. self-correction 上限超過時 `Stop` に遷移可能。
- 検証失敗時: 3回まで自己修復し、4回目相当は `Stop`。

### Phase 6: Proceed（現時点判定）
- 判定: **Hold（依存未解決）**。
- Open化解除条件（全件必須）:
  1. 依存確定証跡の充足。
  2. Approval Record の充足。
  3. proposal-only / docs-only / fail-closed の維持。


## Stream C 直列Phase運用ログ（2026-05-06）

1. **Read同期**: `ADR-0028` / `ADR-0016` / `ADR-0017` / `02_Architecture/api.md` を再参照し、CE4契約語彙を同期。
2. **CE1契約参照チェック**: `ContextQueryV1/ContextBundleV1` は参照のみ。CE1未確定時は CE4を proposal-only のまま固定。
3. **Plan→Execute→Verify→Proceed**: contract-only 文書整備を実施し、API/CLI実装変更は対象外。
4. **Self-Correction（最大3回）**: 検証失敗時は3回まで自己修復。超過時は `held` 停止。
5. **Stopper**: 工数超過、前提崩壊（CE1/CE0契約不成立）、他契約との競合検出時は即停止。

### ADRルール適用メモ（proposal-only）
- 本IssueでのADR相当記述は **Context / Decision / Consequences** を先に固定済み。
- 未承認の契約更新は提案に留め、Decision確定として扱わない。
- CE1契約が確定するまで `equivalenceKey AND bundleHash` 判定を運用導入しない（設計参照のみ）。

## Stream C update（2026-05-06 / Phase C Read→ADR→Plan→Execute→Verify→Proceed）

### Phase 1 Read（Status / Dependencies整合確認）
- Status再確認: `Draft` 維持（Contract Freeze Candidateのまま）。
- Dependencies再確認: CE0契約依存 + CE1 ContextBundle I/F依存（mockで先行可）。依存確定証跡は未充足。
- CE1参照制約: CE1契約は参照のみ。CE1側の実装詳細・定義変更は扱わない。

### Phase 2 ADR C/D/C
- Context: CE4はAPI/CLI/監査を跨ぐため、依存未確定下では実装仕様を固定せず、境界契約だけを保つ必要がある。
- Decision: proposal-only + fail-closed を維持し、mock前提のI/F接続条件のみを整理する。
- Consequences: 実装詳細の先走りは防げるが、Open判定は依存証跡が揃うまで `Hold` となる。

### Phase 3 Plan→Execute（mock前提I/F接続条件のみ）
- Plan（I/F接続条件）:
  1. API/CLI共通で `equivalenceKey AND bundleHash` を同値成立条件にする。
  2. 監査I/Fは `query -> bundle -> proposal -> apply` の4イベント連結を必須にする。
  3. `sourceBundleHash` は `mock:<64hex>` を許容しつつ real と同じ fail-closed で検証する。
- Execute: 本Issueの契約記述更新のみ（終了コード数値や転送基盤など実装詳細は未確定のまま維持）。

### Phase 4 Verify（draft gate/Open移行/非目標）
- Draft gate条件: 失敗分類（入力/監査/ポリシー/同値）維持、auto-*禁止、監査欠損fail-closed維持。
- Open移行条件: 依存確定証跡 + Approval Record充足 + docs-check pass + self-correction <=3。
- 非目標: CLI終了コードの数値固定、匿名化方式固定、監査転送基盤確定。

### Phase 5 Proceed 判定
- 判定: **Hold**。
- 根拠: 依存確定証跡・Approval Record未充足のため、依存未確定のままOpen化を実施しない。

## Stream H update（2026-05-06 / CE4 API/CLI Audit Integration Draft整備専任）

### Phase 1: Read（Status/Priority/Dependencies + CE0/CE1契約再確認）
- CE4現行メタを再確認: `Status=Draft (Contract Freeze Candidate)` / `Priority=P2` / `Dependencies=CE0契約・CE1 ContextBundle I/F`。
- CE0参照契約（read-only）を再確認:
  - CE0境界: `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`
  - No-Go canonical IDs: `preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`
- CE1参照契約（read-only）を再確認:
  - `ContextQueryV1` / `ContextBundleV1`（closed-world）
  - 固定語彙: `preview_required` / `unknown_contract_key` / `nondeterministic_bundle`
  - handoff keys: `sourceBundleHash === bundleHash`、`equivalenceKey + bundleHash`
- 判定: CE4はCE0/CE1契約参照のみでDraft整備を進行可能（実装変更不要）。

### Phase 2: ADR（Context / Decision / Consequences）
- **Context**: CE4はAPI/CLI/監査の下流統合であり、CE0/CE1契約未固定のまま実装着手すると監査整合と責務境界が破綻する。
- **Decision**:
  1. Draft段階のCE4は **契約参照固定 + 監査観点固定** のみを扱う（contract-only）。
  2. CE0/CE1契約をSSOT参照し、CE4側で再定義しない。
  3. `proposal-only` / `fail-closed` / `auto-*禁止` を実装非依存の判定規律として維持する。
- **Consequences**:
  - Open判定前に API/CLI/監査の検証粒度を揃えられる。
  - CE0/CE1に対する語彙ドリフトと責務衝突を事前に抑制できる。
  - 実装着手条件（契約整合）を明確化し、下流競合を低減できる。

### Phase 3: Plan（Open化判定AC/DoD）
#### AC（Open候補判定に必要な観点）
- [x] CE0/CE1参照契約（ID/語彙/handoff key）をCE4本文でread-only固定した。
- [x] API/CLI境界の責務分離（同値判定・失敗分類・proposal-only）を再読可能化した。
- [x] 監査ログ最小項目（4イベント + 共通必須キー）を維持し、非対象範囲（数値終了コード・匿名化方式・転送基盤）を明示した。

#### DoD（Draft整備完了条件）
- [x] CE0/CE1契約参照のみでCE4 Open判定可否を説明できる。
- [x] 実装タスク化/API実装変更/CLI実装変更/監査実装変更を含まない。
- [x] self-correction上限（3回）と超過時Stop条件を保持する。

### Phase 4: Execute（CE4 Draft本文のみ更新）
- 実施: 本 `issue-CE4-api-cli-audit-integration.md` へ Stream H運用記録を追記し、契約語彙・依存式・禁止事項をDraft判定向けに明文化。
- 非実施（範囲外）:
  - API/CLI/監査の実装変更
  - CE0/CE1本体Issue修正
  - Allowlist外ファイル編集

### Phase 5: Verify（整合確認 / self-correction）
- CE0整合: Contract ID・No-Go語彙との矛盾なし。
- CE1整合: I/F語彙・error semantics・handoff keyとの矛盾なし。
- CE4内部整合: `proposal-only` / `fail-closed` / 監査4イベント順序要件と衝突なし。
- 状態遷移整合: Draft整備として矛盾なし（実装要求へ昇格していない）。
- self-correction: `0/3`（修正再試行不要）。

### Phase 6: Proceed（Open候補可否 / blocking items）
- 判定: **Open候補（条件付きで可）**。
- 根拠: CE0/CE1参照契約のみでCE4契約の監査境界・責務分離・fail-safeを再読可能。

#### blocking items（未解決論点）
1. CLI終了コードの**数値割当**（分類語彙は固定済みだが値は未固定）。
2. `principalIdMasked` の不可逆化方式（hash/tokenizationの選定未確定）。
3. 監査転送基盤（保存先・配送保証・署名方式）の上位ADR確定待ち。

> 運用注記: 上記blocking itemsを実装確定要求として扱う場合は本レーン範囲外のため **Stop** とし、上位ADR/別Issueへエスカレーションする。

## Stream G update（2026-05-06 / CE4下流提案仕様化・実装着手前）

### Phase: Read同期 → ADR様式整理 → Plan → Execute（モック前提のI/F合意）→ Verify → Proceed

#### Read同期
- `ADR-0028` / `ADR-0016` / `ADR-0017` / `02_Architecture/api.md` を再照合し、CE4契約語彙を固定。
- 依存関係は **契約参照のみ** とし、CE1/CE2の実装有無に依存しない mock-first 判定境界を維持。

#### ADR様式整理（Context / Decision / Consequences）
- Context: API/CLI/監査の3境界で同値条件と失敗分類が一致しないと、実装着手後の監査整合が破綻する。
- Decision: CE4は contract-only を維持し、I/Fは mock値（`mock:<64hex>`）を正規入力として先行合意する。
- Consequences: 実装前に判定契約を固定でき、下流実装は監査欠損ゼロ・fail-closed を前提に開始できる。

#### Plan（実装前合意条件）
- AC-G1: API/CLI共通で `equivalenceKey AND bundleHash` のAND条件を成功条件として固定。
- AC-G2: 失敗分類 `入力違反 / 監査違反 / ポリシー違反 / 同値違反` を共通化。
- AC-G3: `proposal-only` 逸脱（auto-*含む）は常に No-Go。
- DoD-G1: 4イベント（`query/bundle/proposal/apply`）の順序・存在検査が本Issue単体で再読可能。
- DoD-G2: self-correction は **最大3回**、4回目相当は Stop。

#### Execute（モック前提のI/F合意）
- Mock API I/F:
  - request keys: `equivalenceKey`, `queryCanonicalHash`, `bundleHash`, `sourceBundleHash=mock:<64hex>`
  - response contract: `result=ok|ng`, `failureType`（4分類）
- Mock CLI I/F:
  - 入力はAPIと同一キー集合を要求
  - 終了時に `failureType` を必ず出力し、監査違反時は成功扱いしない
- Mock Audit I/F:
  - 4イベント全件に `schemaVersion`, `channel`, `command`, `actor` を必須化
  - 欠損・順序逆転・矛盾重複は fail-closed

#### Verify（3回自己修復上限）
- V1: editable scope（CE4ファイルのみ差分）
- V2: contract-only / proposal-only / fail-closed 文言整合
- V3: AC/DoD/未確定点/停止条件の一貫性
- self-correction: `0/3`（本更新時点）

#### Proceed
- 判定: **Hold**（依存確定証跡およびApproval Record待ち）。
- Proceed解除条件: 依存確定証跡（日時・承認者・対象・判断）を追記後、docs-check再実行で欠落ゼロ。


## Stream C update（2026-05-07 / CE4 Draft→Open準備 / proposal-only contract）

### Phase 1: Read（CE0/CE1参照条件の再確認）
- CE0 Contract Freeze を read-only 参照し、No-Go canonical IDs・safeMode既定後退禁止・fail-closed優先を再確認。
- CE1 Foundation を参照し、`queryCanonicalHash` / `bundleHash` / `equivalenceKey` の接続キーを mock前提で利用する境界を再確認。
- CE4は API/CLI/監査の **契約整備のみ** とし、実装非依存の判断軸に限定する。

### Phase 2: ADR（Context / Decision / Consequences 補強）
- **Context**: CE4は3境界（API/CLI/監査）を跨ぐため、Draft段階で失敗分類・同値条件・監査必須キーを固定しないと実装時に逸脱しやすい。
- **Decision**: `equivalenceKey AND bundleHash` 条件、4イベント順序、proposal-only、auto-*禁止、監査欠損fail-closedをOpen判定の必須軸として固定する。
- **Consequences**: 実装チームはmock fixtureで先行検証可能になる一方、監査欠損は成功扱い不可となり運用判断の恣意性を抑制できる。

### Phase 3: Plan（Open AC / DoD / Validation 明文化）
- AC追加:
  - [ ] API/CLI双方で同値条件（AND）が一致。
  - [ ] 監査4点セットの順序整合と必須キー検証が明記。
  - [ ] fail-closed / proposal-only / auto-*禁止が同時成立。
- DoD追加:
  - [ ] mock正常/欠損/重複/不正操作の4区分がNo-Go判定基準へ接続。
  - [ ] Open化判定を `Proceed / Hold / Stop` で再現可能。
- Validation（docs-check固定）:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-CE4-api-cli-audit-integration.md`
  - `git diff --check -- 01_Plans/issues/issue-CE4-api-cli-audit-integration.md`

### Phase 4: Execute（メモ整備のみ / mock I/F条件）
- 実施: 監査契約の実装非依存軸を再整理。
- mock I/F接続条件:
  1. `sourceBundleHash` は `mock:<64hex>` を許容するが検証規律は real と同一。
  2. `queryCanonicalHash` / `bundleHash` / `equivalenceKey` を API/CLI で共有参照。
  3. `proposal` が `ok` でも `apply` 欠損ならNo-Go（fail-closed）。
- 非実施: API/CLIハンドラ実装、DB永続化方式、ランタイム統合。

### Phase 5: Verify（AC/DoD・依存・語彙統一）
- self-repair attempt: `1/3`（失敗分類語彙を「監査違反/同値違反/ポリシー違反」に統一）。
- self-repair attempt: `2/3`（proposal-only と auto-*禁止の同時成立を再点検）。
- self-repair attempt: `3/3`（mock I/F条件とOpen gateの対応を補正）。
- 判定: 3回以内で整合完了、超過なし。

### Phase 6: Proceed / Stop（Open候補化の可否）
- 判定: **Open候補化は可（Conditional Open Candidate）**。
- Proceed前提:
  1. CE0/CE1参照契約との語彙衝突がないこと。
  2. AC/DoD/Validation が docs-check で再確認可能であること。
  3. proposal-only / fail-closed / no auto-* の不変性が保たれること。
- Stop条件: 前提不整合・契約競合・4回目修復要求を検知した場合は `held`。

## Stream E update（2026-05-07 / CE4 Draft契約下書きの独立整備）

### Phase 1 Read（最新再読）
- 再読対象: `ADR-0028` / `ADR-0016` / `ADR-0017` / `02_Architecture/api.md` / 本Issue現行契約。
- 再確認結果: `proposal-only`、`fail-closed`、同値AND条件、監査4イベント順序の4軸に矛盾なし。
- 判定: CE4 Draftは contract-only のまま独立整備可能（実装着手条件は未充足のまま維持）。

### Phase 2 Plan（AC/DoD不足提案）
- AC補強提案:
  1. API/CLI共通で失敗分類4区分（入力/監査/ポリシー/同値）を必須再読項目として固定。
  2. `sourceBundleHash` の `mock`/`real` 両経路で同一検証規律（必須キー・順序・同値AND）を明文化。
  3. 監査4イベントの欠落ゼロ（1件欠落でNo-Go）をOpen判定前提に固定。
- DoD補強提案:
  1. 未確定点（終了コード数値/匿名化方式/転送基盤）を実装仕様へ昇格しない境界を維持。
  2. self-correction 上限 `<=3`、4回目相当は Stop を明示維持。
  3. `safeMode既定ON` と `auto-*禁止` の後退ゼロを確認可能な記述粒度を維持。

### Phase 3 Execute（contract-only / mock-first）
- 実施内容: 本Issueの契約文のみを更新対象とし、コード・ADR本文・API/CLI実装は非変更。
- 固定内容:
  - 監査契約は `query -> bundle -> proposal -> apply` の順序整合を必須化。
  - 同値判定は `equivalenceKey AND bundleHash` の同時成立のみ成功。
  - `sourceBundleHash=mock:<64hex>` を正規入力として扱い、real経路と同一fail-closed判定を適用。

### Phase 4 Verify（self-correction 上限3）
- Verify観点:
  1. 編集許可範囲（本Issueのみ）逸脱なし。
  2. AC/DoD補強提案が contract-only 境界を越えていない。
  3. 未確定点が停止報告対象として分離維持されている。
- self-correction 実績: `0/3`（追加修復なし）。

### Phase 5 Stop（致命エラー時停止条件）
- Stop条件:
  1. 未確定点の即時仕様確定要求（契約範囲逸脱）が入った場合。
  2. self-correction が3回を超過した場合。
  3. `proposal-only` / `fail-closed` / `auto-*禁止` のいずれかに抵触する要求が混入した場合。
- 現在判定: **Proceed可能（contract draft整備完了）**。
