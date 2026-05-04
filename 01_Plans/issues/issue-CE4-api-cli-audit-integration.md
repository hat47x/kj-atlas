# Issue Draft: CE4 API/CLI/監査統合（Stream J / CE4専任 / contract-only）

- Type: Feature request
- Status: Draft (Contract Freeze Candidate)
- Priority: P2
- Owner: Stream J（CE4専任）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Editable: `issue-CE4-api-cli-audit-integration.md` のみ
- Related Backlog: `CE-4`
- Related ADR/Spec: `ADR-0028`, `ADR-0016`, `ADR-0017`, `02_Architecture/api.md`
- Dependencies: `CE-4`
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


## Stream E preparation log（2026-05-04 / Draft→Open昇格準備, contract-only）

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
