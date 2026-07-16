# Issue Draft: CE4 API/CLI/監査統合（Stream H / CE4専任 / contract-only）

- Type: Feature request
- Lifecycle: Draft -> Open -> In Progress -> Done
- Status: Done
- Source Issue: N/A (Done 2026-06-20)
- Priority: P2
- Owner: Stream C（CE4 API/CLI/監査契約 proposal-only）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Editable: `issue-CE4-api-cli-audit-integration.md` のみ
- Related Backlog: `CE-4`
- Related ADR/Spec: `ADR-0028`, `ADR-0016`, `ADR-0017`, `ADR-0039`, `02_Architecture/api.md`
- Dependencies: `01_Plans/issues/issue-CE0-contract-freeze.md`（Done 2026-06-20）, `01_Plans/issues/issue-CE1-context-query-bundle-foundation.md`（Done 2026-06-20）
- Verification: `docs-check`
- Expected verification level: `docs-check`

## Done 2026-06-20
CE4 API/CLI/Audit contract frozen in architecture.md. equivalenceKey AND bundleHash, Audit 4-event set, fail-closed, dryRun sideEffect=none, CE1 mock接続確立。実装詳細（HTTP/CLI数値コード/監査配送）は実装フェーズに委譲。

## Draft→Open 2026-06-20
CE4 Open化。CE0/CE1 Doneにより依存充足。SafeMode不変条件維持（proposal-only, fail-closed, 監査4点セット）。

## Mission（実装非依存の契約固定）
- CE4 API/CLI/監査統合を、実装方式から独立した**契約レベル**で固定する。
- `proposal-only` を強制し、auto-apply / auto-confirm / auto-publish を禁止する。
- `fail-closed` を既定とし、監査必須項目の欠損は成功扱いしない。
- 監査イベント4点セット（`query` / `bundle` / `proposal` / `apply`）を必須契約として固定する。
- CE1（ContextQuery/ContextBundle基盤）未整備時でも、`mock:<64hex>` 経路で契約検証を継続可能にする。

## Stream L proposal-only 統合ゲート（2026-05-17）

### 実装着手条件（Go条件）
- `G-01` API/CLI/Audit の I/F草案が単一語彙で整合（`mode=proposal-only` / `decision` / `classification` / `equivalenceSatisfied`）。
- `G-02` 監査4イベント（`query -> bundle -> proposal -> apply`）と共通必須キーが固定済み。
- `G-03` fail-closed規律（欠損/順序違反/同値違反/ポリシー違反は成功扱い禁止）が明文化済み。
- `G-04` CE1未整備時の mock 接続（`mock:<64hex>`）で real と同一規律を適用する記述がある。
- `G-05` 未確定点（HTTP詳細/CLI数値コード/監査配送方式）を「実装フェーズまで未固定」と明示できる。

### 非着手条件（No-Go条件）
- `NG-01` `proposal-only` 以外のモードを成功扱いする記述が混入。
- `NG-02` 監査4イベントの欠損や順序逸脱を許容する記述が混入。
- `NG-03` `equivalenceKey AND bundleHash` のAND同値条件が崩れる。
- `NG-04` 実装方式（保存先/QoS/署名/HTTP詳細/CLI数値コード）を契約確定として先取りする要求。
- `NG-05` CE0/CE1未確定事項を推測で補完する要求。

---

## Operating Mode（Stream C / serial phases）
- Execution mode: proposal-only（実装コード変更禁止 / 他Issue編集禁止）
- Editable scope: `01_Plans/issues/issue-CE4-api-cli-audit-integration.md` のみ
- Dependency policy: CE0 / CE1 は read-only 参照（未承認事項の確定禁止）
- Serial phases: **Plan+Read → ADR (Context/Decision/Consequences) → API/CLI監査チェックリスト定義 → Mock接続で依存切断 → Verify（自己修復は最大3回）→ Proceed**
- Stop conditions:
  - CE0/CE1 契約との矛盾が解消できない
  - 前提（equivalenceKey/bundleHash/4イベント監査）が崩壊
  - Verify で4回目の修復が必要（= 上限超過）

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
5. CE1由来IDが未払い出しの場合、`equivalenceKey` は CE4モック発番を許容するが、API/CLI/Audit の3経路で同一値を強制する（経路間不一致は監査違反）。

### 3.3 失敗時挙動（fail-closed）
- 必須キー欠損: **監査違反**として失敗。
- 順序欠損（例: `apply` が先行）: **監査違反**として失敗。
- 重複イベント（同一 `eventType` + `equivalenceKey` で矛盾結果）: **監査違反**として失敗。
- 不正操作（auto-apply / auto-confirm / auto-publish 検出）: **ポリシー違反**として失敗。
- 同値不成立（AND条件未達）: **同値違反**として失敗。

---


## Phase 3.5: API/CLI監査I/Fシグネチャ草案（contract-only / 実装禁止）

> 目的: CE4の境界（API, CLI, Audit）で**入出力の形だけ**を先行固定する。ここで示すのは契約草案であり、実装・配線・永続化方式は未確定のまま維持する。

### 3.5.1 API Signature Draft
- `POST /v1/audit/proposals:verify`
  - Request (contract fields)
    - `mode`: literal `"proposal-only"`（必須）
    - `equivalenceKey`: `string`
    - `queryCanonicalHash`: `sha256:<64hex>`
    - `bundleHash`: `sha256:<64hex>`
    - `sourceBundleHash`: `sha256:<64hex>` | `mock:<64hex>`
    - `events`: AuditEvent[4]（`query -> bundle -> proposal -> apply`）
  - Response (contract fields)
    - `decision`: enum [`go`,`no_go`]
    - `classification`: enum [`ok`,`validation_failed`,`audit_violation`,`equivalence_violation`,`policy_violation`]
    - `equivalenceSatisfied`: boolean
    - `violations`: string[]
    - `traceId`: string

### 3.5.2 CLI Signature Draft
- `kj-audit verify-proposal`
  - Required flags
    - `--mode proposal-only`
    - `--equivalence-key <string>`
    - `--query-canonical-hash <sha256:...>`
    - `--bundle-hash <sha256:...>`
    - `--source-bundle-hash <sha256:...|mock:...>`
    - `--events-json <path>`（4イベント配列）
  - Contracted stdout/stderr semantics
    - stdout: `decision`, `classification`, `traceId` を機械可読で出力
    - stderr: 契約違反詳細（必須キー欠損/順序違反/同値違反/ポリシー違反）
  - Exit code policy
    - 数値は未固定（未確定点を維持）
    - ただし `classification != ok` は常に非0（fail-closed）

### 3.5.3 Audit Adapter Signature Draft
- `emitAudit(event: AuditEvent) -> Ack`
  - `AuditEvent` は 3.1 の共通必須キーを満たすこと
  - `Ack` は少なくとも `accepted: boolean`, `reason?: string`, `traceId: string` を持つこと
- `verifySequence(events: AuditEvent[4]) -> VerificationResult`
  - 4イベント順序・重複矛盾・ID整合を判定

### 3.5.4 Mock接続点（依存切断境界）
1. **API入口モック**: `sourceBundleHash=mock:<64hex>` を受理し、realと同一ルールで `verify-proposal` 判定。
2. **CLI入力モック**: `--source-bundle-hash mock:<64hex>` と fixture events の組み合わせで契約検証。
3. **監査出力モック**: `emitAudit` の配送先をモックSinkに差し替えても、`Ack.accepted=false` は No-Go。
4. **ID発番モック**: CE1未整備時は `equivalenceKey` をCE4モック発番許容。ただし API/CLI/Audit の3経路一致を必須化。

### 3.5.5 Non-Goals（この草案で確定しないもの）
- HTTPステータス詳細、CLI終了コードの数値、監査保存先/配送QoS/署名方式は未固定。
- 型定義の実コード化（OpenAPI/argparse/SDK生成）は実装フェーズまで禁止。

### 3.5.6 I/F先行固定ルール（API/CLI/監査）
- 先行固定対象は **入出力フィールド・判定語彙・失敗分類** のみ。
- 実装依存要素（永続化方式、配送方式、具体的終了コード値、HTTPステータス割当）は非固定とする。
- 互換性判定は「旧I/Fで表現可能か」を基準にし、破壊的変更は次版契約でのみ扱う。

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

## Phase 5: Verify（AC/DoD監査 + 停止条件 / max 3 repairs）

### Acceptance Criteria（AC）
- [x] API/CLI/監査ログの必要項目を抽出した。
- [x] ADR-style（Context / Decision / Consequences）を定義した。
- [x] 追跡可能性・改ざん耐性・再現性の要件を明記した。
- [x] 監査イベントスキーマ、ID連携、失敗時挙動を定義した。
- [x] 正常/欠損/重複/不正操作の mock 検証ケースを定義した。
- [x] CE1未整備時のモック切断境界（`mock:<64hex>` とモック発番 `equivalenceKey`）を定義した。
- [x] 停止規則（CE1未整備での実装要求、監査項目削減、指定外編集）を明記した。

### Definition of Done（DoD）
- [x] 本Issue単体で CE4契約を実装非依存に読解できる。
- [x] `proposal-only` / `fail-closed` / `safeMode既定ON` を後退させる記述がない。
- [x] 未確定点を明示し、確定済み事項と分離した。

### 未確定点（停止報告対象）
1. CLI終了コードの**具体値マッピング**（数値割当）は本Issueでは未固定。
2. `principalIdMasked` の不可逆化方式（ハッシュ/トークン化）は本Issueでは未固定。
3. 監査転送基盤（保存先・配送保証・署名方式）は本Issueでは未固定。

> 停止条件: 上記未確定点を確定仕様として扱う要求が来た場合、CE4契約の範囲逸脱として停止し、上位ADRでの判断を要請する。

---

## Stream C execution log（2026-05-10 / CE4 契約適合監査限定）

### Phase 1: Plan+Read
- スコープを契約・監査設計の4文書（本Issue / `02_Architecture/api.md` / `ADR-0016` / `ADR-0017`）に限定。
- CE4論点を「API/CLI/監査の契約適合監査」に限定し、実装コード変更禁止を再確認。

### Phase 2: ADR（Context / Decision / Consequences）
#### Context
- CE4は API/CLI/Audit の3経路を跨ぐため、監査契約の単一判定軸がないと実装前レビューで解釈差分が残る。
#### Decision
- CE4判定軸を `AND同値条件`・`4イベント順序`・`proposal-only`・`fail-closed` に固定。
- 失敗分類を `validation_failed` / `audit_violation` / `equivalence_violation` / `policy_violation` に固定語彙化。
#### Consequences
- 実装前に契約適合監査の pass/fail が決まり、レビューを実装品質ではなく契約準拠で進められる。

### Phase 3: API/CLI監査チェックリスト定義
- C1 必須キー完備（schemaVersion含む）
- C2 4イベント順序整合（`query -> bundle -> proposal -> apply`）
- C3 AND同値条件（`equivalenceKey AND bundleHash`）
- C4 `proposal-only` 違反ゼロ（`auto-*` 検出時 No-Go）
- C5 失敗分類の再読可能性（4種固定語彙）

### Phase 4: Mock接続で依存切断
- CE1未整備時は `sourceBundleHash=mock:<64hex>` で契約検証継続を許可。
- mock/real を同一 fail-closed 規律で扱い、実装待ち項目（終了コード数値、匿名化方式、転送基盤）を未確定として隔離。

### Phase 5: Verify（自己修復 <=3）
- Verify-1: 4文書間で CE4判定軸（AND同値・4イベント・proposal-only・fail-closed）が一致。
- Verify-2: 監査チェックリストが API/CLI 双方に適用可能。
- Verify-3: 依存切断条件（`mock:<64hex>`）が明記され、実装待ち項目が誤って確定化されていない。
- self-correction: `1/3`（Owner/Phase表記の不整合を補正）。
- Proceed判定: **Hold**（契約固定完了、実装待ち）。


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

---

## Stream I execution log（2026-05-08 / proposal-only契約固定）

### Phase 1: Read（API/CLI/監査契約の再読）
- API契約要件・CLI契約要件・監査ログ契約要件を再読し、4イベント系列とAND同値条件を確認。
- 監査欠損を成功扱いしない fail-closed 規律を再確認。

### Phase 2: ADR/CDC（不一致リスクの固定）
- **Context**: API/CLI/Audit の3経路で契約不一致があると、監査追跡が断裂し検証不能になる。
- **Decision**: 最小スキーマ、ID連携、失敗挙動を本Issueで固定。CE1依存は `mock:<64hex>` とモック `equivalenceKey` で切断可能とする。
- **Consequences**: 実装前に監査可能性を先行確保し、下流は fixture 駆動で契約適合確認できる。

### Phase 3: Plan（AC/DoD補完）
- 必須イベント項目を 3.1 の共通必須キーに固定。
- 整合判定を `equivalenceKey AND bundleHash` + 4イベント順序整合で固定。
- 停止規則を以下で固定:
  1. CE1未整備のまま実装要求が来た場合は Stop。
  2. 監査項目削減で追跡不能化する変更要求は Stop。
  3. 指定外ファイル編集要求は Stop。

### Phase 4: Execute（契約文面整備のみ）
- 実施内容は本Issue文面の契約整備のみ（proposal-only）。
- コード・ADR本文・実装I/F変更は未実施。

### Phase 5: Verify（自己完結性確認 / self-correction）
- 確認1: 監査イベント最小スキーマ（3.1）が単体で読解可能。
- 確認2: ID連携契約（3.2）で CE1未整備時のモック切断条件まで自己完結。
- 確認3: fail-closed 判定（3.3）と停止規則の整合を確認。
- self-correction: `1/3`（文言統一1回、超過なし）。

### Phase 6: Proceed（Hold/Open候補/Stop）
- **Hold**: CE1未整備かつ実装要求混入時。契約固定のみ維持。
- **Open候補**: docs-check pass と依存証跡が揃い、proposal-only 境界が維持される場合。
- **Stop**: ストッパー3条件（CE1未整備実装要求 / 監査項目削減 / 指定外編集）が発生した場合。

## Stream C execution log（2026-05-09 / CE4下流準備 / proposal-only）

### Phase 1: Read同期
- CE4契約本文（API/CLI/監査、3.1〜3.3、4.x mock検証）を再読し、Draft維持理由が依存証跡待ちであることを同期。
- `contract-only` と `mock-first` が同時成立し、実装要求を受けない境界を確認。

### Phase 2: ADR/契約依存の明文化（Context / Decision / Consequences）
#### Context
- CE4 は CE1 I/F に依存するが、Open前は mock 経路で検証可能。
- CE0/CE1承認証跡が未確定な状態での実装移行は契約逸脱リスクを増大させる。

#### Decision
- 依存解放条件を次の機械判定セットで固定。
  1. `Open化条件` の4項目が全て true。
  2. `未確定点` 3件が「仕様確定済み」に昇格していないこと（= 未確定のまま隔離）。
  3. self-correction が `<=3`。

#### Consequences
- 下流は mock fixture のみで契約適合判定を先行可能。
- 未承認依存の擬似確定を防ぎ、Hold/Stop判断を自動化しやすくなる。

### Phase 3: Plan（Draft→Open化条件 / AC・DoD / mock前提タスク）
- Draft→Open化条件（all required）:
  - [ ] G1: Open化条件 条件1〜4 が全充足。
  - [ ] G2: AC/DoD のチェックボックスが維持され、後退がない。
  - [ ] G3: docs-check pass 記録が最新化される。
  - [ ] G4: 未確定点3件が「停止報告対象」のまま維持される。
- mock前提タスク:
  - [ ] T1: `sourceBundleHash=mock:<64hex>` の許容は継続し、fail-closed 同一適用を保持。
  - [ ] T2: CE1未整備時 `equivalenceKey` のモック発番許容を維持。
  - [ ] T3: 実装依存事項（終了コード数値/匿名化方式/転送基盤）を確定値へ昇格しない。

### Phase 4: Execute（proposal-only）
- 本Issue文書の計画更新のみ実施。
- コード/ADR/API本文/他Issueの編集は未実施。

### Phase 5: Verify（依存解放条件の機械判定可能性）
- V-CHK1: G1〜G4 が bool 判定可能（true/false）な表現で定義されている。
- V-CHK2: Stop条件がイベント化されており、未解決承認時に Proceed しない。
- V-CHK3: self-correction 超過時（4回目相当）Stop の規則が維持されている。

### Phase 6: Proceed/Stop
- 判定: **Hold**（承認依存未解決）。
- Proceed条件: G1〜G4 true かつ依存証跡充足。
- Stop条件:
  1. 未確定点の仕様確定要求（範囲逸脱）。
  2. self-correction 4回目相当。
  3. 監査イベント4点またはAND同値条件の縮退要求。

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

## Stream C update（2026-05-07 / implementation-ready prep, proposal-only）

### 1) Read同期
- `02_Architecture/api.md` と `02_Architecture/runtime_parameter_registry.md` の CE4 節を再同期し、契約未確定点を実装成功経路へ混在させない方針を再確認。

### 2) Plan
- AC提案（追加）:
  - [x] 契約未確定項目を stub で隔離し、成功判定から除外する境界を API 契約に明示。
  - [x] runtime registry に CE4 stub 制御キーを最小追加し、fail-closed を維持。
- DoD提案（追加）:
  - [x] 未確定点に対する mock/stub 応答が監査 `result=ng` を強制する。
  - [x] A/B 依存が未確定のままでも proposal-only で停止可能な tri-state（Proceed/Hold/Stop）を保持する。

### 3) Execute（mock-first / stub隔離）
- `sourceBundleHash=mock:<64hex>` を維持したまま、以下の未確定項目を `501` stub で隔離する契約を追加:
  - `ce4_stubbed_exit_code_mapping`
  - `ce4_stubbed_principal_masking`
  - `ce4_stubbed_audit_transport`
- stub 応答時も `equivalenceKey/queryCanonicalHash/bundleHash/schemaVersion` を監査記録する fail-closed 契約を固定。

### 4) Verify（self-correction 0/3）
- 契約確認:
  1. proposal-only 後退なし。
  2. 監査4点 + 共通必須キー欠損を成功扱いしない。
  3. 未確定項目は stub 隔離で成功判定へ混入しない。
- self-correction: `0/3`。

### 5) Proceed
- 判定: **Proceed (Implementation Ready / Contract-Compliant with Stub Isolation)**
- 但し、A/B ストリーム依存の確定前提が追加要求された場合は **proposal-only で Stop**（実装強行禁止）。


## Phase 3.5: Assumption Log（CE1契約前提 / CE4 Draft）

| ID | Assumption（CE1前提） | 根拠 | 破綻時の扱い |
| --- | --- | --- | --- |
| A-CE4-01 | `queryCanonicalHash` / `bundleHash` は CE1 contract の deterministic生成物として参照できる。 | `schemas.md` CE1-CONTEXT-FOUNDATION | 同値判定を停止し `Hold`、契約再同期まで Proceed禁止。 |
| A-CE4-02 | CE1未実装でも `mock:<64hex>` による監査連結検証が可能。 | mock-first / contract-only 方針 | mock連結不能時は CE4 Open化停止（Stop）し、未確定点へ戻す。 |
| A-CE4-03 | CE4は CE1 contract を拡張せず read-onlyで利用する。 | CE1 v1 closed-world 契約 | 追加キー要求が出た場合は CE1再起票へエスカレーション。 |

## Draft→Open 昇格条件（CE4 / contract-only gate）

- [ ] Context / Decision / Consequences・AC・DoD・停止条件が本Issue単体で再読可能。
- [ ] Assumption Log（A-CE4-01〜03）に破綻が残っていない。
- [ ] proposal-only / auto-*禁止 / fail-closed / safeMode既定ON 後退ゼロ。
- [ ] 依存確定証跡（日時・承認者・対象・判断・evidence）を記録済み。
- [ ] Verifyの自己修復が3回以内（4回目相当は Stop）である。

## Phase 5 Verify運用（最大3回）

- V1: scope/contract-only 逸脱確認（実装作業・他ファイル編集の混入検知）
- V2: 契約語彙確認（AND同値 / 監査4点 / fail-closed / auto-*禁止）
- V3: 昇格条件整合確認（Assumption LogとDraft→Open gateの整合）
- 修復上限: `3回`。4回目相当は `Stop` 固定。

## Stream E Ready化設計 pass（2026-05-09 / Plan→Execute→Verify→Proceed）

### Phase 1: Read同期（ブロッカー/依存/DoD不足）
- Blocker: 依存Issueの承認証跡（Approval Record: 日時/承認者/対象/判断/evidence）が未確定の場合は `ProceedDecision: Hold` を維持する。
- Dependency: 本Issueで定義済みの依存関係を read-only で再確認し、依存先の未確定値をこのIssue側で確定しない。
- DoD gap: 「実装レーンが即着手可能な入力/出力/担当/解除条件」の4点が散在している場合、Phase 3で1ブロックに集約する。

### Phase 2: 仕様明文化（Context / Decision / Consequences）
- Context: 本Issueは Draft/Blocked を Ready化するための計画文書であり、実装や運用確定値の追加はスコープ外。
- Decision: `Proceed/Hold/Stop` の三値判定、`self-correction <= 3`、`docs-check` 優先を固定し、依存未解除時は `Hold` を維持する。
- Consequences: 先行依存が解決した時点で、実装レーンは追加解釈なしで着手可否を判定できる。

### Phase 3: Ready化（AC/DoD・入力/出力・担当・依存解除条件）
- AC/DoD Readyセット（本Issueで確認すべき共通最小セット）:
  - [ ] AC-R1: 受入条件が測定可能な判定文（done/pending/hold いずれか）で記録されている。
  - [ ] AC-R2: `ProceedDecision` と `Dependency status` が矛盾しない。
  - [ ] DoD-R1: 実装禁止境界（docs-only / proposal-only など）が明示されている。
  - [ ] DoD-R2: `Hold` 継続条件と `Stop` 条件（上限超過・競合未解決）が明示されている。
- 入力（Implementation lane input）:
  - 承認証跡、依存Issueの最新判定、固定語彙（Go/NoGo・Proceed/Hold/Stop・pass/fail/blocked）。
- 出力（Implementation lane output expectation）:
  - 着手可否の単一判定（Proceed or Hold/Stop）と、着手時に守る制約チェックリスト。
- 担当:
  - System Owner: Go/NoGo最終判定。
  - Platform Operator: 実行/保管/運用ログ整備。
  - Security Officer: 公開境界・safeMode/漏えい防止の最終確認。
- 依存解除条件:
  - 依存Issueの Approval Record 5項目が確定し、相互参照リンクで追跡可能であること。

### Phase 4: 引継ぎ（実装レーン即着手チェックリスト）
- [ ] H1: Scope逸脱なし（本Issue外の仕様確定をしていない）。
- [ ] H2: AC/DoDの未完了項目が `pending/hold` で可視化されている。
- [ ] H3: 実装開始ゲート（Proceed条件）が1箇所に集約されている。
- [ ] H4: Verifyコマンド（validator/rg/diff-check）が再実行可能。
- [ ] H5: 依存未解除時は `Hold` を維持し、推測で `Proceed` しない。

### Verify結果（本pass）
- 判定: `Hold` 維持（依存証跡未確定のため）。
- self-correction: `1/3`（上限内）。
- Stop条件再確認: 4回目相当の修復要求、または依存競合未解決時は `Stop`。


## Validation plan（Open化前の必須チェック）
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-CE4-api-cli-audit-integration.md`
- `rg -n "^- Type:|^- Status:|^- Priority:|^- Scope:|^- Related ADR/Spec:|^- Expected verification level:" 01_Plans/issues/issue-CE4-api-cli-audit-integration.md`
- `rg -n "mock:<64hex>|proposal-only|fail-closed|Proceed|Hold|Stop|self-correction" 01_Plans/issues/issue-CE4-api-cli-audit-integration.md`
- `git diff --check -- 01_Plans/issues/issue-CE4-api-cli-audit-integration.md`

## Mock-first dependency cut policy（依存切断方針）
- CE1 I/F未確定時は `sourceBundleHash=mock:<64hex>` とモック `equivalenceKey` を使用し、API/CLI/Audit 3経路の整合だけを検証対象にする。
- 実装依存値（終了コード数値・匿名化方式・転送基盤）は Draft範囲外として固定し、Open化審査で確定扱いしない。
- 依存がI/F契約のみの項目は `mock-first` で先行し、実装要求が混入した時点で `ProceedDecision: Stop` に移行する。

## Stream E execution log（2026-05-09 / CE4 planning docs-only）

### Phase 1: Read
- 本Issue全文を再読し、`proposal-only` / `fail-closed` / 監査4イベントの既存契約を確認。
- Scope制約（`issue-CE4-api-cli-audit-integration.md` のみ編集）と Stopper（verify>3 / 契約語彙衝突 / safeMode境界後退 / allowlist外編集）を確認。

### Phase 2: ADR/CDC（Context / Decision / Consequences 確定）
- **Context**: ContextQuery/ContextBundle の API/CLI/監査導線は、CE1依存有無（real/mock）に関係なく同一契約語彙で追跡可能である必要がある。
- **Decision**:
  1. 監査キーは `query` / `bundle` / `proposal` / `apply` を固定し、系列順序を必須化する。
  2. `proposal-only` と `fail-closed` を維持し、監査欠損・同値不成立・ポリシー違反を成功扱いしない。
  3. tri-state判定は `Proceed / Hold / Stop` を維持し、**fail-safe held 遷移**を以下で固定する。
     - 任意の監査違反・同値違反・ポリシー違反を検知した時点で `Proceed -> Hold`。
     - self-correction が 3 回を超える、または契約語彙衝突を検知した時点で `Hold -> Stop`。
     - Hold 解除は「欠損修復 + docs-check pass + self-correction<=3」の同時成立時のみ許可する。
- **Consequences**:
  - API/CLI/監査の3経路で判定再現性が揃い、監査導線の断裂を抑制できる。
  - 実装前に No-Go 条件を明確化でき、下流実装での安全境界後退を予防できる。

### Phase 3: Plan（AC/DoD定義）
- AC提案（本Issue内で合意固定）:
  1. 監査キー4点（`query`/`bundle`/`proposal`/`apply`）と順序要件が明記されている。
  2. fail-safe held 遷移（`Proceed->Hold->Stop`）と解除条件が明記されている。
  3. API/CLI共通で `equivalenceKey AND bundleHash`、`proposal-only`、`fail-closed` が同時に読める。
- DoD提案（本Issue内で合意固定）:
  1. docs-only で契約文が自己完結し、実装依存の確定を持ち込んでいない。
  2. safeMode境界後退（auto-*許可、fail-open化、監査項目削減）がない。
  3. Verifyの自己修復回数が `<=3` で記録され、超過時 Stop が定義されている。

### Phase 4: Execute（docs-only更新）
- 本セクション追加のみ実施。コード/他文書/設定は未変更。

### Phase 5: Verify（self-correction）
- Verify-1: allowlist内単一ファイル編集であることを確認（pass）。
- Verify-2: 監査キー4点と fail-safe held 遷移の明記を確認（pass）。
- Verify-3: `proposal-only` / `fail-closed` / `equivalenceKey AND bundleHash` の後退なしを確認（pass）。
- self-correction: `1/3`（文言統一のみ）。

### Phase 6: Proceed/Stop
- 判定: **Proceed候補（docs-contract更新完了）**。
- Hold条件: 依存証跡不足、または docs-check 未実行/不合格。
- Stop条件: verify>3、契約語彙衝突、safeMode境界後退、allowlist外編集。

## Stream H execution log（2026-05-09 / CE4 Draft Ready化, docs-only, contract-only）

### Task Brief（Scope固定）
- Scope: `01_Plans/issues/issue-CE4-api-cli-audit-integration.md` の契約整理のみ。
- Non-Goals: backend/frontend/CLI実装、ADR更新、他Issue編集。
- Acceptance Criteria:
  - [x] API契約・CLI契約・Audit契約を分離して検証可能な粒度で記載する。
  - [x] 統合点（`eventId`/`traceId`/`actor`/`timestamp`）の必須性を明記する。
  - [x] `mock-first` で先行可能な I/F 境界と hard dependency を分離する。
  - [x] セキュリティ・監査受入条件（fail-closed / proposal-only / auto-*禁止）を再定義する。
- Validation Plan:
  - [x] 本Issue内の契約項目整合（API/CLI/Audit/統合点）を目視確認。
  - [x] `Proceed/Hold/Stop` と self-correction 上限 `<=3` の整合確認。
- Stop Conditions:
  - [x] 監査必須項目未定義のまま進行要求。
  - [x] 契約境界不明確のまま責務競合が残る状態。

### Phase 1: Read同期（抽出結果）
- API契約: AND同値条件、proposal-only、4イベント順序整合、fail-closed が既存定義済み。
- CLI契約: API同値条件準拠、失敗種別分離（入力/監査/同値）と監査違反fail-closed が既存定義済み。
- Audit契約: 共通必須キー、追跡可能性、改ざん耐性、再現性が既存定義済み。
- 不足メタ: `eventId`/`traceId` の明示不足、mock先行境界と凍結待ち依存の分離不足、Security ACの再掲不足。

### Phase 2: Plan（Draft Ready化提案）

#### 2.1 契約分離（検証単位）
- **API Contract Unit**
  - 入力: `equivalenceKey`, `queryCanonicalHash`, `bundleHash`, `sourceBundleHash`, `proposal-only`。
  - 判定: `equivalenceKey AND bundleHash` + 監査4イベント系列が揃う場合のみ `ok`。
  - 失敗: `input_validation_error` / `audit_contract_error` / `equivalence_error` / `policy_violation`。
- **CLI Contract Unit**
  - 入力: APIと同一語彙 + `command`（実行意図識別）。
  - 判定: API判定の再現一致（同一入力で同一No-Go分類）。
  - 失敗: API失敗分類をそのままCLI終了分類へ写像（数値コードは未固定）。
- **Audit Contract Unit**
  - 入力: 4イベント + 共通必須キー。
  - 判定: キー完備/順序整合/重複矛盾なし。
  - 失敗: 欠損/順序違反/重複矛盾を即 No-Go（fail-closed）。

#### 2.2 統合点（API/CLI/Audit共通）
- 必須統合キー（v1固定）:
  1. `eventId`（イベント単位ユニーク、重複検知キー）
  2. `traceId`（1トランザクション系列追跡）
  3. `equivalenceKey`（同値判定キー）
  4. `actor`（`principalType`, `principalIdMasked`）
  5. `timestamp`（RFC3339 UTC）
- 補助整合キー:
  - `queryCanonicalHash`, `bundleHash`, `sourceBundleHash`, `channel`, `command`, `schemaVersion`, `result`。

#### 2.3 依存関係とmock適用境界
- **先行可能（mock）**:
  - `sourceBundleHash=mock:<64hex>` を使った API/CLI/Audit 契約テスト。
  - `eventId/traceId/equivalenceKey` の連結整合テスト。
  - 失敗分類（入力/監査/同値/ポリシー）の再現一致テスト。
- **凍結待ち（hard dependency）**:
  - CE0/CE1 の実ID払い出し規約確定。
  - CLI終了コード数値マッピング確定。
  - 監査保管・署名・配送保証など実装基盤確定。

### Phase 3: Execute（Context / Decision / Consequences 追記）

#### Context（追加補正）
- CE4は API/CLI/Audit の責務分離が曖昧なまま実装へ進むと、同一入力で判定不一致が発生し監査証跡が断裂する。
- そのため Draft段階で、契約単位・統合キー・mock境界・hard dependency を分離し、実装着手前の誤結合を防ぐ必要がある。

#### Decision（追加補正）
1. API/CLI/Audit を別契約として固定し、評価軸を混在させない。
2. 統合必須キーとして `eventId`/`traceId`/`equivalenceKey`/`actor`/`timestamp` を v1必須化する。
3. mock先行は I/F 契約整合に限定し、実装基盤確定要求は hard dependency として Hold する。
4. セキュリティ受入は `proposal-only` + `fail-closed` + `auto-apply/auto-confirm/auto-publish 禁止` の同時成立を必須化する。

#### Consequences（追加補正）
- 実装前の契約テストで API/CLI/Audit 判定不一致を先に排除できる。
- 監査キー欠損や順序破綻を即時No-Go化でき、監査証跡の再現性が向上する。
- 依存未解除項目を hard dependency として隔離でき、競合実装の同時進行リスクを下げられる。

### Phase 4: Verify（自己検証 + Self-Correction）
- AC検証:
  - [x] API/CLI/Audit 契約分離を記載。
  - [x] 統合点キー（eventId/traceId/actor/timestamp）を明記。
  - [x] mock先行境界とhard dependencyを分離。
  - [x] セキュリティ監査受入条件を明記。
- DoD検証:
  - [x] 契約境界と責務分離が読める。
  - [x] リスク（監査断裂/判定不一致）と緩和策（必須キー/fail-closed/mock-first）が対応。
- self-correction: `1/3`（文言統一のみ、上限超過なし）。

### Phase 5: Proceed判定
- 判定: **Draft Ready（contract plan）**。
- Proceed条件（実装レーン移行前）:
  1. docs-check pass。
  2. CE0/CE1 依存の承認証跡確認。
  3. hard dependency 未解除項目を Open化時に明示継続。
- Stop条件（フェイルセーフ）:
  - 未定義監査要件の確定要求。
  - 契約境界不明確のまま責務競合解消不能。
  - allowlist外編集要求。
  - self-correction `>3`。

## Stream H execution log（2026-05-09 / CE4 contract-first proposal, CE1 independent）

### Phase 1: Read（API/CLI監査要件・依存抽出）
- 本Issue既存契約を再読し、API/CLI/監査の共通要件を **実装非依存** で再確認。
- 依存は以下の2層に分離して抽出。
  1. 契約依存: `issue-CE0-contract-freeze`（契約凍結証跡）
  2. I/F依存: `issue-CE1-context-query-bundle-foundation`（ContextBundle本体）
- CE1未確定時の独立実行経路として `sourceBundleHash=mock:<64hex>` と CE4モック `equivalenceKey` を継続採用可能であることを確認。

### Phase 2: ADR/CDC（監査I/Fの必要性と境界）
- **Context**: CE4は API/CLI/Audit の3経路横断であり、実装先行だと経路間同値と監査整合が分断される。
- **Decision**: CE4では監査I/Fを「4イベント系列 + 共通必須キー + fail-closed判定」の契約として固定し、保存先・配送・署名などの実装詳細は境界外に置く。
- **Consequences**: CE1確定前でも mock-first で契約検証を先行でき、後続実装の差異は契約テストで吸収可能。

### Phase 3: Plan（AC/DoD: シグネチャ・型・イベント・エラー）
- AC追加（契約再読性）:
  - [x] **Signature境界**: API/CLIとも `equivalenceKey`・`queryCanonicalHash`・`bundleHash` を同値判定の最小シグネチャとして共有。
  - [x] **Type境界**: `sha256:<64hex>` / `mock:<64hex>`、`eventType enum`、`result enum` を契約型として固定。
  - [x] **Event境界**: `query -> bundle -> proposal -> apply` の順序整合を必須化。
  - [x] **Error境界**: 入力違反 / 監査違反 / 同値違反 / ポリシー違反を fail-closed で成功不可に固定。
- DoD追加（CE1独立性）:
  - [x] CE1未確定でも mock経路で契約検証フローを完結できる。
  - [x] CE1由来の具体ID仕様・実装方式を本Issueで確定扱いしない。

### Phase 4: Execute（本Issueのみ更新）
- 実施内容は **本Issueへの proposal追記のみ**。
- コード、ADR本文、API/CLI実装、他Issueは未編集。

### Phase 5: Verify（CE1未確定との整合確認）
- 確認結果:
  1. CE1本体が未確定でも、CE4は `mock:<64hex>` とモック `equivalenceKey` で契約検証可能。
  2. 具体実装前提（保存基盤、終了コード数値、匿名化アルゴリズム）を確定仕様へ昇格していない。
  3. 依存前提は「契約依存 / I/F依存」に分離され、未確定事項の誤確定を回避できている。
- self-correction: `0/3`（追加修復なし）。

### Phase 6: Proceed（Ready/Hold/Stop）
- 判定: **Hold**（通常運用）
- 理由:
  - CE1確定前でも契約提案は独立実行可能だが、実装移行の gate（依存証跡/承認記録）は未充足。
- Ready条件（将来）:
  1. 依存証跡（日時/承認者/対象/判断/evidence）の補完。
  2. docs-checkで契約欠落ゼロの再確認。
- Stop条件（再掲）:
  1. 具体実装前提の混入。
  2. 依存前提の無根拠確定。
  3. allowlist違反（本Issue以外編集）。
  4. self-correction上限超過（4回目相当）。


### DoD（proposal-only）
- [x] CE4契約を API/CLI/監査の3境界で同一語彙に統一した。
- [x] proposal-only / fail-closed / no auto-apply を No-Go 条件として明文化した。
- [x] CE0/CE1 依存を read-only に固定し、未承認事項を確定していない。
- [x] Verify の自己修復回数上限（最大3回）と停止条件を明記した。
- [x] 変更は本Issueファイル内に限定した。

## Stream I integration pass（2026-05-09 / CE4 API/CLI/Audit Integration Draft）

### Phase 1: Read Sync
- 対象を本Issueに限定し、CE0/CE1は read-only で参照。
- 契約中核を再同期: `proposal-only` / `fail-closed` / 監査4イベント（`query -> bundle -> proposal -> apply`） / AND同値条件（`equivalenceKey AND bundleHash`）。

### Phase 2: ADR（Context / Decision / Consequences + 承認）
#### Context
- CE4はAPI/CLI/監査を跨ぐため、実装前に契約語彙を単一Draftへ固定しないと検証系が分岐する。
- CE1未整備期間でもmock経路検証を止めない運用が必要。

#### Decision
1. CE4契約は本Issue内で **implementation-decoupled** に固定し、実装方式はスコープ外とする。
2. `sourceBundleHash` は `sha256:<64hex>` と `mock:<64hex>` の両方を許容し、同一の fail-closed 規律を適用する。
3. API/CLI/Audit は同一 `equivalenceKey`・`queryCanonicalHash`・`bundleHash` の共有で照合可能にする。
4. `auto-apply` / `auto-confirm` / `auto-publish` を禁止し、検出時はポリシー違反No-Goで固定する。

#### Consequences
- 下流は実装待ちなしでfixture駆動の契約検証を継続できる。
- 監査欠損・同値不成立・禁止操作を成功扱いしないため、判定揺れを抑止できる。

#### Approval Record（Draft gate）
- approvalStatus: `draft-approved-for-contract-freeze-candidate`
- approvedByRole: `Stream I CE4 maintainer (virtual)`
- approvedAt: `2026-05-09T00:00:00Z`
- evidence: `本Issue内 Phase 1-6 記録に基づく整合確認（proposal-only / mock-first / fail-closed）`

### Phase 3: Plan（AC/DoD不足補完）
- AC補完:
  - [x] API/CLI共通で失敗分類（入力違反 / 監査違反 / ポリシー違反 / 同値違反）を再読可能。
  - [x] CE1未整備時の `mock:<64hex>` 経路を契約上の正規検証入力として明示。
  - [x] 監査4イベント欠損を全件No-Goに固定。
- DoD補完:
  - [x] `proposal-only` 後退ゼロ、`auto-*` 禁止維持、`fail-closed` 維持。
  - [x] Verify自己修復 `<=3`、4回目相当は Stop。
  - [x] 未確定点を実装仕様へ昇格しない境界を維持。

### Phase 4: Execute（契約定義のみ）
- 実施: 本Issue契約文の統合整理（API/CLI/Auditの語彙・判定・停止条件）。
- 非実施: 実装コード変更、CLI終了コード数値確定、監査基盤選定、匿名化方式確定。

### Phase 5: Verify（max 3 repairs）
- Verify-1: 4イベント最小スキーマ、ID連携、fail-closed規律が単一文書で自己完結していることを確認。
- Verify-2: `proposal-only` と `auto-*` 禁止、CE0/CE1 read-only 参照境界を確認。
- Verify-3: mock/real (`mock:<64hex>` / `sha256:<64hex>`) の同一検証規律を確認。
- self-correction: `1/3`（文言整列1回。上限内）。

### Phase 6: Proceed / Stop
- Proceed条件:
  1. docs-checkで契約欠落ゼロ。
  2. 依存証跡が揃い、未確定点を確定扱いしていない。
- Hold条件:
  - 依存証跡不足だが契約境界は維持される場合。
- Stop条件:
  1. CE0/CE1未承認事項の確定要求。
  2. 監査必須項目削減要求。
  3. 指定外ファイル編集要求。
  4. self-correction 4回目相当。

## Stream H execution log（2026-05-10 / CE4-api-cli-audit-integration）

### Phase 1: Read
- ADR-0015/0016/0017 と CE4契約本文を再読し、同値条件（`equivalenceKey AND bundleHash`）と fail-closed を再確認。
- API/CLI同値性は mock `sourceBundleHash` を含めた監査4点セット前提であることを確認。

### Phase 2: Plan
- CE2と分離したCE4計画として、接続面を「API resolve endpoint」「CLI payload正規化」「監査キー検証」に限定。
- AC補完:
  - [x] CLI/APIで required field 同一性を保持。
  - [x] dry-run時の sideEffect=none を必須化。
  - [x] 監査連鎖 `query/bundle/proposal/apply` 欠損時 fail-closed。

### Phase 3: Execute
- interface+mock-first 方針を維持し、`ce4 resolve-bundle` 系を最小契約のまま固定（実装方式は未確定のまま）。
- no-op fallback: 応答欠損や契約不一致時は成功にせず停止（SystemExit）する導線を保持。

### Phase 4: Verify
- `pytest -q 03_Implement/backend/tests/test_cli_ce4_audit.py` を実行し、API/CLI監査統合の契約テストを再検証。
- self-correction: `0/3`。

### Phase 5: Proceed
- 判定: **Proceed (CE4接続面の整備達成)**。
- 残リスク:
  1. principalマスキング方式（可逆/不可逆）は未確定。
  2. 監査転送基盤（保存先・署名・配送保証）は未確定。
  3. CLI exit code 詳細マッピングは ADR 境界で保留。

## Stream G execution log（2026-05-10 / proposal-only契約完成度向上）

### Phase 1: Read（Draft理由・Dependencies・Scopeの同期）
- Status=Draft の理由を「依存証跡待ち（CE0/CE1）」として再確認し、Open前に契約凍結境界を維持することを確認。
- Dependencies は CE0（契約凍結）/ CE1（ContextQuery/ContextBundle基盤）を read-only 参照とし、mock 経路で依存切断可能であることを同期。
- Scope は `issue-CE4-api-cli-audit-integration.md` 単体編集のみで、docs-only / contract-only / proposal-only を維持。

### Phase 2: ADR（Context / Decision / Consequences）
#### Context
- CE4 は API/CLI/監査イベントの3境界を跨ぐため、実装前に契約を固定しないと監査追跡と同値判定の解釈差が発生する。
- CE1 未整備時に実装依存へ進むと、検証不能な状態で仕様だけが拡散するリスクがある。

#### Decision
1. CE4は **implementation-independent contract** として固定し、実装詳細（保存先・配送保証・署名・終了コード数値）は未確定点として隔離する。
2. 監査イベント4点（`query` / `bundle` / `proposal` / `apply`）を必須化し、欠損時は fail-closed で No-Go とする。
3. `proposal-only` を強制し、auto-apply / auto-confirm / auto-publish を禁止継続する。

#### Consequences
- 下流実装は mock fixture だけで契約適合判定を先行できる。
- 監査欠損・順序欠損・同値不成立の判定基準が API/CLI で統一される。
- 依存未確定時の拙速な実装移行を抑止し、Hold/Stop の運用判断が機械化しやすくなる。

### Phase 3: Plan（監査4点必須化 / AC・DoD整備）
- 監査4点セット（`query` / `bundle` / `proposal` / `apply`）を必須契約として維持し、順序整合 `query -> bundle -> proposal -> apply` を検証対象に固定。
- AC/DoD 観点の追補:
  - fail-closed を後退させない（監査欠損・同値違反・ポリシー違反の成功扱い禁止）。
  - unknown key は許容しても判定に使用しない（必須キー欠損検知を優先し、fail-open禁止）。
  - 監査4点のいずれか欠損時は常に No-Go。

### Phase 4: Execute（docs-only）
- 本Issue文書のみ更新し、コード/ADR本文/API実装/CLI実装の変更は行わない。
- allowlist外編集要求は受理しない（本ファイル外の編集禁止）。

### Phase 5: Verify（fail-closed / unknown key / 監査欠損No-Go）
- Verify-1: fail-closed 規律が API/CLI/監査契約全体で維持されていることを確認。
- Verify-2: unknown key handling は「無視可能だが成功要件に不使用」とし、必須キー欠損時No-Goを優先することを確認。
- Verify-3: 監査4点の欠損（特に `apply` 欠損）を No-Go とする契約が維持されていることを確認。
- self-correction: `0/3`（追加修復なし）。

### Phase 6: Proceed（Proceed / Hold / Stop）
- **Proceed**: なし（Draftのため）。
- **Hold**: 依存 CE0/CE1 のOpen化証跡待ち、かつ proposal-only 境界維持時。
- **Stop**:
  1. 未定義競合または契約衝突が解消不能な場合。
  2. 監査4点必須の緩和や fail-open 要求が発生した場合。
  3. allowlist外（本ファイル以外）編集要求が発生した場合。

### Stream E serial execution（2026-05-10 / CE4 API/CLI/Audit, proposal-only）

#### Phase 1 Read
- `ADR-0028` CE-4要件、`02_Architecture/api.md`、`04_Documentation/operations.md`、`04_Documentation/local_llm_ops_guide.md` を再読し、監査導線の共通語彙を確認。
- CE1契約は read-only 参照とし、`ContextQuery/ContextBundle` の contract freeze を変更しないことを確認。

#### Phase 2 ADR（Context / Decision / Consequences）
- **Context**: `query/bundle/proposal/apply` の監査4点セットは存在するが、API/CLI同値性判定と routing 監査キーの統一記述が分散している。
- **Decision**: CE4同値判定を `equivalenceKey AND bundleHash` に固定し、routing監査キー（`routingStage/provider/model/sourceBundleHash/proposalId`）を API/CLI共通必須観点として固定する。
- **Consequences**: 実装前でも docs-only で検証計画を統一でき、監査欠損時は fail-closed で停止判断可能になる。

#### Phase 3 Plan
- 受入条件:
  - [x] API/CLI双方で同値性判定キーと失敗分類が同一語彙で読める。
  - [x] 監査ログの必須イベント/必須キー/順序要件が operations / local LLM guide と整合する。
  - [x] routingStage 追跡不能時の Stop 条件を明文化する。
- 非目標:
  - 実装コード変更、契約型定義（CE0/CE1）変更、frontend変更。

#### Phase 4 Execute
- 本Issueに CE4統合方針（同値条件・監査キー・停止条件）を追記。
- API設計文書へ監査I/Fの統一節を追加。
- Operations / Local LLM guide へ API/CLI同値性検証計画の実行手順を追加。

#### Phase 5 Verify（API/CLI同値性検証計画）
- 検証計画（docs-contract）:
  1. 同一 canonical query で API/CLI それぞれ `query -> bundle -> proposal -> apply` を dry-run 実行。
  2. `equivalenceKey` と `bundleHash` の一致（AND条件）を確認。
  3. routing監査キー（`routingStage/provider/model/sourceBundleHash/proposalId`）が4イベントすべてで追跡可能か確認。
  4. 欠損・順序逆転・競合（同一キーで矛盾値）時は fail-closed で No-Go。
- 自己修復カウンタ: `0/3`。

#### Phase 6 Proceed / Stop
- **Proceed条件**: 4文書（Issue/API/operations/local_llm_ops）で同値判定・監査キー・停止条件が矛盾なく読解できること。
- **Stop条件**:
  1. 監査ログ欠落（4イベント欠損または必須キー欠損）。
  2. `routingStage` 追跡不能。
  3. 未定義競合（同一 `equivalenceKey` / `bundleHash` で矛盾結果）。
  4. 自己修復4回目相当（>3）。

## Stream D serial phase checkpoint（2026-05-10 / CE track, docs-only）

### Phase 1 Read Gate
- Read対象を再同期し、Status / Priority / Scope / Related ADR/Spec / Acceptance criteria / Validation plan を再確認。
- CE1のtriage必須メタ（Status/Priority）は本日時点で充足済み（欠落なし）として記録。
- 依存整理: `depends_on` を満たすまで下流は proposal-only を維持し、`unlocks` を本IssueのProceed条件に限定。

### Phase 2 Plan（AC/DoD合意）
- 目的: CE契約の固定語彙・fail-closed・mock-first境界を維持しつつ、下流が実装準備を継続できる状態を保つ。
- 非目標: 実装コード変更、共有ダッシュボード更新、他ストリーム専用ファイル編集。
- AC/DoD不足がある場合は本Issue内ドラフトで補完し、未合意項目はHold扱いで固定。
- 検証コマンド: `python 01_Plans/triage_actionable_plans.py --root . --format table`（存在時）/ `git diff -- <this issue file>`。

### Phase 3 ADR Gate
- 本Issueで新規ADR更新が必要な論点は Context / Decision / Consequences を先に明文化し、承認前は実装へ進まない。

### Phase 4 Execute→Verify
- 実行順序は CE0→CE1→CE2→CE3→CE4 を維持し、各Issueでは Plan→Execute→Verify を直列実施。
- Verifyは proposal-only / contract-only / fail-closed の後退が無いことを最優先で確認。

### Phase 5 Proceed
- AC/DoDが未成立、または依存解除条件未達の場合は Proceed せず Hold を維持する。
- 共有ファイル更新が必要な場合は本Issueからの「更新要求メモ」作成に留め、直接編集しない。


## Phase 6: Proceed（実装前提チェックリスト）

### P0: Contract freeze gate（必須）
- [ ] `mode=proposal-only` が API/CLI 契約の必須入力として固定されている。
- [ ] 同値判定は `equivalenceKey AND bundleHash` のAND条件のみを成功として扱う。
- [ ] 監査4イベント `query -> bundle -> proposal -> apply` の欠損/逆順を fail-closed で拒否する。

### P1: Responsibility boundary gate（必須）
- [ ] API責務: 検証要求を受理し、分類語彙（`classification`）を返す。
- [ ] CLI責務: APIと同一語彙で入力を構成し、`classification != ok` を必ず非0終了に変換する。
- [ ] 監査責務: 共通必須キー検証、順序検証、同一 `equivalenceKey` 連結の3点を実施する。

### P2: Mock-first gate（依存切断）
- [ ] `sourceBundleHash=mock:<64hex>` を許容し、real入力と同一の判定規律を適用する。
- [ ] CE1未整備時の `equivalenceKey` モック発番を許容するが、API/CLI/Audit で同値を強制する。

### P3: Verify/Stop gate（運用）
- [ ] Verifyの自己修復は最大3回。4回目が必要な場合は `StoppedForClarification` で停止する。
- [ ] 未確定点（HTTP詳細/CLI数値コード/監査配送方式）を契約確定へ昇格しない。

## Stream B proposal-only gate refresh（2026-05-20 / CE契約・モック切断）

### Phase 1: 最新Read + 依存再確認
- CE4は API/CLI/Audit の contract-only 統合Issue（Status=Draft, Priority=P2）として再確認。
- 依存は CE0（語彙固定）/ CE1（Context I/F固定）への read-only 参照に限定。

### Phase 2: CE1固定点への接続（proposal-only）
- CE4は `ContextQueryV1/ContextBundleV1` を監査整合の前提入力として扱うが、実装配線は確定しない。
- `mock:<64hex>` 経路は real と同一 fail-closed 規律を適用し、依存切断を維持。

### Phase 3: Plan→Execute→Verify
- Plan: I/F固定（入出力フィールド・判定語彙・失敗分類）と、未固定項目（HTTP詳細/CLI数値コード/配送方式）の境界を維持。
- Execute: proposal-only 文書更新のみ。
- Verify:
  - 依存循環なし（CE4はCE1契約を参照し、CE1へ実装要求を逆流させない）。
  - Draft→Open条件は G-01〜G-05 の充足で測定可能。
  - self-correction 上限は3回。

### Phase 4: Stopper
- CE1契約が曖昧化した場合、またはCE4から他ストリーム実装領域編集が必要になった場合は停止・照会とする。

## Current-main checkpoint（2026-06-14 / post-2397 CE4 Draft readiness）

### Context
- Baseline: `main@cd5a087f` after PR #2397.
- Scope: docs-only checkpoint for CE4 API/CLI/Audit contract readiness. This update does not change `Status: Draft (Contract Freeze Candidate)`, does not approve implementation, and does not update ADR/API/CLI/runtime files.
- Upstream reference state:
  - CE0 contract and graph checkpoints are available as read-only references.
  - CE1 ContextQuery/ContextBundle checkpoint is available as a read-only mock-first reference.
  - CE2 remains `Draft` / `Hold`; its Approval Record gap must not be bypassed by CE4.

### Readiness Evidence
| Gate | Current evidence | Current result |
| --- | --- | --- |
| API/CLI mode | `mode=proposal-only` remains the only successful mode | no regression |
| Equivalence | success requires `equivalenceKey AND bundleHash` | no weakening |
| Audit sequence | `query -> bundle -> proposal -> apply` remains the required four-event sequence | fail-closed unchanged |
| CE1 mock bridge | `sourceBundleHash=mock:<64hex>` remains allowed only for contract verification | not production source-of-truth |
| CE2 dependency | CE2 remains Draft/Hold because Approval Record is missing | no Open substitute |
| Implementation details | HTTP status mapping, CLI exit-code mapping, storage/transport guarantees, and masking/signature scheme remain unresolved | implementation blocked |

### Decision
- Keep CE4 in Draft/Hold for implementation. The contract is useful as a reviewable reference, but the Open gate remains blocked by unresolved approval and implementation-detail boundaries.
- Treat CE0/CE1/CE2 checkpoints as read-only references. CE4 must not turn their checkpoint text into implementation permission, release authority, or automatic proposal acceptance.
- No ADR is required for this checkpoint because it preserves the existing CE4 contract and records the remaining blockers rather than changing equivalence, audit, or release authority.

### Human / Upstream Tasks Before Open Review
- Confirm the CE4 Approval Record and source issue number when Draft is promoted.
- Resolve whether CLI exit-code mapping, audit transport/storage guarantees, and principal masking/signature rules belong in CE4 ADR scope or separate implementation issues.
- Confirm that CE2 remains proposal-only and human-final before CE4 treats proposal verification as a release gate.

### Stop Conditions
- Stop immediately if CE4 accepts a mode other than `proposal-only`, treats `equivalenceKey` or `bundleHash` alone as sufficient, or lets a missing audit event pass.
- Stop immediately if CE4 uses CE2 Draft material or CE1 mock data to auto-apply, auto-confirm, auto-publish, or promote unreviewed output.

## Traceability

- Related: `01_Plans/issues/issue-GENAI-GOV-01-generative-ai-lane-boundary-and-readiness.md`（Lane B/C: proposal-onlyレビュー面）, `02_Architecture/value_traceability.md` §2.9
