# Issue Draft: CE4 API/CLI/監査統合（Stream H / CE4専任 / contract-only）

- Type: Feature request
- Status: Draft (Contract Freeze Candidate)
- Priority: P2
- Owner: Stream H（CE4専任）
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


## Stream H execution log（2026-05-04 / contract-freeze, mock-first）

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


## Stream H update（2026-05-04 / Read Sync → Proceed）

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
