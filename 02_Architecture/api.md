# kj-atlas MVP API I/F


> 環境変数・実行パラメータの正本は `02_Architecture/runtime_parameter_registry.md`。本書では必要最小限のみ記載し、追加/改名時は正本を先に更新する。
> 現行契約と Stream / freeze 履歴の読み分けは `02_Architecture/contract_reading_guide.md` を参照する。
> MVPのCRUDサポート表と運用保守境界は `02_Architecture/data_model_operations_overview.md` を参照する。
本ドキュメントは、kj-atlas の **MVP API（Documentの保存・取得）** を定義します。

- MVPでは **スナップショット保存** を基本とします
- Document の標準CRUDは **全体保存/取得** に絞ります
- 認証/認可、監査、Context/AI系APIは限定契約として別節で扱い、個別エンティティCRUDとは分けます
- APIはイントラ利用や組織導入を含むため、単純で監査しやすい境界を優先します

---

## 1. 基本方針

### 1.1 リソース単位

- 主リソース：`Document`
- 最小のCRUD：Create / Read / Update

DeleteはMVPおよび現製品化準備段階の標準APIに含めない（`ADR-0035` Accepted 2026-07-13）。必要性だけを理由に追加せず、削除方式・監査保持・復旧不能性を別ADRで先に固定する。
Card / Edge / Island / Narrative などは Document 内の論理構造であり、MVPでは個別リソースCRUDを正本にしません。

### 1.2 更新方式

- `PUT /docs/{doc_id}` で **Document全体** を置き換える
- クライアントは `updatedAt` を更新して送る
- サーバは検証後に保存し、保存後のDocumentを返す

### 1.3 競合

MVPでは以下のいずれかで簡素に扱う。

- Last Write Wins（デフォルト）
- `If-Match` / `ETag` による楽観ロック（任意ヘッダー。指定時は不一致を拒否）

`If-Match` が無い場合は LWW とし、`If-Match` がある場合は保存済み `ETag` と一致したときだけ更新する。

---

## 2. エンドポイント

### 2.1 Create

MVPの実装境界では、クライアントがIDを指定して **PUT** `/docs/{doc_id}` を呼び、対象IDが存在しない場合に作成として扱う。

- Request body：`DocumentV1`
- Response：保存後の `Document`

**POST** `/docs` は、サーバ採番の新規作成が必要になった場合の将来候補であり、MVPの必須APIではない。`POST /docs` を標準契約に昇格する場合は、`DATA-CONTRACT-01` で文書、実装、テストを同期する。

---

### 2.2 Read

**GET** `/docs/{doc_id}`

- Response：`DocumentV1`
- Not found：404

---

### 2.3 Update

**PUT** `/docs/{doc_id}`

- Request body：`DocumentV1`
- Response：保存後の `DocumentV1`
- Validation error：400

---

### 2.4 List（任意：MVPでは後回し可）

**GET** `/docs`

- Response：最小の一覧（id/title/updatedAt）

イントラ想定では一覧があると便利だが、MVPでは必須ではない。


### 2.5 Document監査イベント（FB-RM-PUB-05 / CE4）

Document 本体の標準CRUDとは別に、共有・Context操作の監査連携点を持つ。監査送信は本体処理を阻害しない fail-open dispatcher 方針を維持するが、各リクエスト自体は SafeMode/readOnly/access-control の判定対象になる。

**POST** `/docs/{doc_id}/export-audit`

- Request body: `{ "safeMode": boolean, "exportKind": string }`
- Response: `{ "status": "accepted" }`
- 目的: export完了通知を監査連携アダプタへ委譲（監査送信失敗でも本体機能を阻害しない）

**POST** `/docs/{doc_id}/context-audit`

- Request body:
  - `operation: "query" | "bundle" | "proposal" | "apply"`
  - `safeMode: boolean`
  - `equivalenceKey: <64hex>`
  - `bundleHash: <64hex>`
  - `sourceBundleHash?: <64hex> | mock:<64hex>`
  - `queryHash?: string`
  - `dryRun: boolean`
  - `sideEffect: "none"`
  - `rejectReasonCode?: "none" | "missing_event" | "equivalence_mismatch" | "dry_run_side_effect" | "safemode_regression"`
  - `command: string`
  - `channel: "api" | "cli" | "gui"`
  - `schemaVersion: "ce4.audit.v1"`
- Response: `{ "status": "accepted" }`
- Error:
  - 409: CE4の4点監査イベントが `apply` 時点で揃わない、または deterministic 判定が不成立
  - 422: operation/command不一致、`dryRun` 違反、`sourceBundleHash` 欠損などの契約違反
- 目的: `query -> bundle -> proposal -> apply` の監査4点を同一 `equivalenceKey` / `bundleHash` で接続し、proposal-only / dry-run の境界を検証する。


### 2.6 Merge Decision Log（CTR-2B-02-DECISION-LOG-V1）

Manual assisted merge の意思決定ログを、Document 本体とは分離して append/list/restore する。

**POST** `/docs/{doc_id}/merge-decision-logs`

- Request body:
  - `{ "record": MergeDecisionRecord }`
- Response: `MergeDecisionRecord`（201）
- Error:
  - 404: `doc_id` が存在しない
  - 409: 同一 `decisionId`（同一 `doc_id` 内）の重複
  - 422: `action` enum などの契約違反

**GET** `/docs/{doc_id}/merge-decision-logs/by-group/{group_id}`

- Response: `MergeDecisionRecord[]`（append 順）

**GET** `/docs/{doc_id}/merge-decision-logs/restore/{snapshot_version}`

- Response: `MergeDecisionRecord[]`（append 順）

`MergeDecisionRecord`:

- `decisionId: string`
- `groupId: string`
- `action: "accept" | "partial" | "reject" | "defer"`
- `selectedCardIds: string[]`
- `note: string`
- `decidedBy: string`
- `decidedAt: string (ISO 8601)`
- `snapshotVersion: string`



### 2.7 CE4 Audit Integration Contract（API/CLI equivalence）

CE4（API/CLI/監査統合）は CE1 契約を read-only 参照し、実装方式に依存しない接続契約のみを固定する。

#### 2.7.1 固定ルール（Normative）
- 同値判定成功条件: `equivalenceKey AND bundleHash` の同時一致（片方一致は失敗）。
- 実行モード: `mode=proposal-only` のみ許容（`auto-apply` / `auto-confirm` / `auto-publish` は禁止）。
- 監査イベント順序: `query -> bundle -> proposal -> apply` を固定し、欠損/逆順は fail-closed。
- 依存切断: CE1未整備時は `sourceBundleHash=mock:<64hex>` を許容し、realと同一規律で判定する。

#### 2.7.2 API Signature（contract-only）
- `POST /v1/audit/proposals:verify`
- Request必須: `mode`, `equivalenceKey`, `queryCanonicalHash`, `bundleHash`, `sourceBundleHash`, `events[4]`
- Response必須: `decision` (`go|no_go`), `classification` (`ok|validation_failed|audit_violation|equivalence_violation|policy_violation`), `equivalenceSatisfied` (boolean), `violations` (string[]), `traceId`

#### 2.7.3 CLI Signature（contract-only）
- `kj audit verify-proposal`
- 必須フラグ: `--mode proposal-only`, `--equivalence-key`, `--query-canonical-hash`, `--bundle-hash`, `--source-bundle-hash`, `--events-json`
- 契約: `classification != ok` は常に非0終了（数値割当は未固定）。

#### 2.7.4 監査イベント共通必須キー（API/CLI共通）
- `eventType` (`query|bundle|proposal|apply`)
- `timestamp` (RFC3339 UTC)
- `equivalenceKey`
- `queryCanonicalHash`
- `bundleHash`
- `sourceBundleHash` (`sha256:<64hex>` または `mock:<64hex>`)
- `actor` (`principalType`, `principalIdMasked`)
- `channel` (`api|cli`)
- `command`
- `result` (`ok|ng`)
- `schemaVersion` (SemVer)

#### 2.7.5 失敗分類と停止規律
- `validation_failed`: 入力契約違反
- `audit_violation`: 必須キー欠損 / 順序違反 / 重複矛盾
- `equivalence_violation`: `equivalenceKey` または `bundleHash` 不一致
- `policy_violation`: proposal-only違反（auto-*検出）
- fail-safe: 自己修復は最大3回。4回目相当は `StoppedForClarification`。

#### 2.7.6 責務境界（API / CLI / Audit）
- API責務: 契約検証要求を受理し、分類語彙と判定結果を返す。
- CLI責務: API同値語彙で入力を組み立て、失敗分類を終了ステータスへ反映する。
- Audit責務: 4イベント順序、必須キー、同一 `equivalenceKey` 連結可能性を検証する。

### 2.8 Context Query / Bundle Contract（CE1-CONTEXT-FOUNDATION）

CE-1のHTTP endpoint、status/error、副作用を本節の正本とする。型、required/optional key、列挙、canonicalization、version互換は [`schemas.md` §1.2](schemas.md#12-ce1ce2ce4-型契約実装非依存) を正本とし、本書では再定義しない。

logical type、HTTP envelope、下流handoffのkey所属は [`schemas.md` CE1 v1 layer ownership matrix](schemas.md#ce1-v1-layer-ownership-matrixlogical--transport--handoff) を正本とする。`queryId`は`ContextQueryV1`だけに属し、`schemaVersion="1.0.0"`はHTTP response metadata、`sourceBundleHash`はCE2/CE4のread-only handoff値である。

**POST** `/context/query`

- Purpose: Query Preview通過済みの `ContextQuery` を検証・正規化する。
- Request body: `ContextQueryV1`
- Response body: `ContextQueryValidationResponse`
- Error:
  - `422 preview_required`: `previewConfirmed != true`
  - `400 unknown_contract_key`: CE1 v1 最小I/F外のキー、または enum/range違反を fail-closed で拒否
  - `422 invalid_query_contract`: enum/rangeの補助バリデーション。上記2語彙を置換しない

**POST** `/context/bundle`

- Purpose: Deterministic projection を実行し `ContextBundle` を返す。
- Request body: `ContextBundleRequest`
- Response body: `ContextBundleResponse`。`schemaVersion`はtransport metadataでcanonical bundle hash対象外。`queryId` / `sourceBundleHash`はresponseへ含めない
- Error:
  - `409 nondeterministic_bundle`: 同一canonical queryでdeterministic `bundleHash`が成立しない
  - `400 unknown_contract_key`: closed-world envelopeまたは型の未定義キー

SafeMode既定ON、未レビュー本文保護、proposal-only、`human_reviewed`人手昇格、Consensus Graph直接更新禁止は [architecture.md §7A](architecture.md#7a-ce-0-責務信頼境界consensusworking-repositioning) を正本とする。


旧Phase手順、mock validation plan、Stream A freeze logは[形成履歴](history/api-contract-formation-2026-04-to-05.md)へ分離した。

### 2.9 CE4 API/CLI/GUI 同値性・監査契約（CE4-API-CLI-AUDIT）

CE-4 は API/CLI/GUI の操作同値性と監査導線を固定する契約フェーズであり、実装方式やUI差分よりも監査可能性を優先する。
また CE4 は proposal-only 境界を維持し、`accepted/rejected` の自動確定経路を許可しない。

#### 2.9.0 Proposal-only + API/CLI監査責務境界

- CE4 の責務は **I/F契約固定** に限定する（実装方式・アルゴリズム詳細・自動適用導線は扱わない）。
- API責務境界: 入力/出力/失敗時セマンティクスを固定する。
- CLI責務境界: API同値の入力面・出力面・終了コードを固定する。
- 監査責務境界: `query/bundle/proposal/apply` と `queryCanonicalHash` の記録を固定する。
- Fail-safe: proposal-only 逸脱（auto-apply/auto-confirm/auto-publish）または監査欠損成功扱いを検知した場合は fail-closed。

#### 2.9.0a CE4 API/CLI監査統合ゲート（Context / Decision / Consequences）

Context:
- CE4 は実装詳細を持ち込まず、API/CLI監査統合を contract-only で先行固定する必要がある。
- `ADR-0016` のCLI契約と `ADR-0017` のSecurity/Ops Gateを、監査イベント最小スキーマで接続する必要がある。

Decision:
1. 監査イベント最小スキーマ（全イベント共通必須キー）を `eventType`, `timestamp`, `equivalenceKey`, `queryCanonicalHash`, `bundleHash`, `actor`, `result`, `channel`, `command`, `schemaVersion`, `sourceBundleHash` に固定する。
2. API→CLI同値性は `equivalenceKey AND bundleHash` 成立のみ成功とし、部分一致成功を禁止する。
3. セキュリティ運用チェックは `eventType + equivalenceKey + queryCanonicalHash` の追跡成立を必須にする。
4. 契約未確定の実装依存点（終了コード数値割当、匿名化方式、監査転送基盤）は CE4 スコープ外として stub 隔離し、契約確定前に本番判定へ昇格しない。

Consequences:
- mock fixture（`sourceBundleHash=mock:<hash>`）のみで API/CLI監査整合の検証が可能になる。
- 監査欠損・同値不成立を成功扱いできなくなり、fail-closed境界が明確化される。
- 下流実装は proposal-only のまま契約準拠テストを先行でき、未確定点の混入を防げる。

#### 2.9.1 logical operation 同値性（固定）

- 対象 operation: `context-query` / `context-bundle` / `proposal-diff` / `apply --dry-run`
- 同値性判定は `equivalenceKey == same` かつ `bundleHash == same` の AND 条件で固定する。
- GUI は独自 operation を定義せず、上記 operation を API/CLI と同一語彙で呼び出す。
- 同値性判定は `query/bundle/proposal/apply` の全監査イベントで同一 `equivalenceKey` を共有していることを前提に評価する。

`equivalenceKey` 定義（normative）:
1. `ContextQuery` を canonical JSON 化（キー辞書順、UTF-8、余分な空白なし、非決定論フィールド除外）。
2. `equivalenceKey = sha256(canonical_query_json)` を16進小文字で生成。
3. API/CLI/GUI は同一 query 入力時に同一 `equivalenceKey` を返す。

#### 2.9.1a CE4 resolve endpoint（mock-first 契約）

- Endpoint（compat）: `POST /context/bundles:resolve`
- Endpoint（v1 alias）: `POST /context/v1/bundles:resolve`
- Required Request Fields:
  - `query`（non-empty string）
  - `dryRun`（boolean）
  - `sourceBundleHash`（`sha256:<64hex>` または `mock:<64hex>`）
  - `safeMode`（boolean, CE4では既定 `true`）
- Required Response Fields:
  - `equivalenceKey`
  - `bundleHash`
  - `queryCanonicalHash`
  - `proposalLifecycle`（`proposed | accepted | rejected | held`）
  - `sideEffect`
  - `auditChain.query|bundle|proposal|apply`
- Error Contract（fail-closed / 422）:
  - 監査4点欠損（空文字・空白のみを含む）
  - `queryCanonicalHash` 欠損
  - `dryRun=true` かつ `sideEffect!="none"`
  - safeMode後退（`safeMode=false`）

#### 2.9.2 監査4点セット（必須イベント）

同一 `equivalenceKey` について、次の4イベントを全て記録しない限り成功扱いにしてはならない（fail-closed）。

| eventType | Required keys |
| --- | --- |
| `query` | `queryId`, `timestamp`, `actor`, `safeMode`, `equivalenceKey` |
| `bundle` | `queryId`, `bundleHash`, `excludedReason[]`, `equivalenceKey` |
| `proposal` | `proposalId`, `sourceBundleHash`, `status`, `equivalenceKey` |
| `apply` | `proposalId`, `approver`, `dryRun`, `sideEffect`, `result`, `equivalenceKey` |

追加必須キー（全イベント共通メタ）: `channel`（`api|cli|gui`）, `command`, `schemaVersion`.
 `schemaVersion` は CE4 契約期間中に固定値を使用し、互換性変更時のみ明示的に更新する。
CE4固定値は `schemaVersion="ce4.audit.v1"` とする。

追加必須キー（同値判定の比較根拠）: `queryCanonicalHash`。
`queryCanonicalHash` が欠損する監査イベントは、4点が揃っていても成功扱いにしてはならない（fail-closed）。

`rejectReasonCode` は次の分類コードを最小集合として固定する（追加は後方互換でのみ許可）。
- `missing_event`
- `equivalence_mismatch`
- `dry_run_side_effect`
- `safemode_regression`

#### 2.9.3 dry-run 副作用境界（固定）

- `dryRun=true` の場合、`sideEffect` は常に `"none"`。
- `dryRun=true` で禁止される副作用:
  - DB永続化
  - 外部サービスとの共有（監査ログHTTP連携を除く。監査ログHTTP連携は fail-open dispatcher 方針）
  - review state の昇格（`unreviewed -> human_reviewed`）
- 上記を満たさない場合は契約違反として失敗扱い（fail-closed）。

proposal lifecycle は `proposed | accepted | rejected | held` の閉集合のみを許可する。
CE4 範囲での語彙追加・別名導入は禁止する。

CE4 フェイルセーフ（停止条件）:
- 監査4点セット欠損を成功扱いしようとする要求
- `dryRun=true` で `sideEffect="none"` を満たさない挙動
- safeMode 後退要求（share/export 保護緩和、未レビュー保護緩和）
- Consensus 直書き要求（proposal/apply 契約を迂回する更新）
- Verify の自己修復が 3回失敗した場合（4回目試行は行わない）
- 前提崩れ（同値性定義や固定 operation 契約の不成立）
- 未定義競合（必須キーの契約定義欠落、または同一キーの多重定義衝突）

#### 2.9.4 `sourceBundleHash` の受理境界（依存切離し）

- `proposal.sourceBundleHash` は次の両形式を受理する。
  - 本番 hash（`[0-9a-f]{64}`）
  - モック hash（`mock:[0-9a-f]{64}`）
- 形式差により同値性判定・監査手順を分岐させてはならない。
- CE3未完了時も `mock:<hash>` により CE4 の契約検証を継続可能とする。
- 運用runbook（`04_Documentation/local_llm_ops_guide.md`）でも `Plan -> Execute(同値性契約) -> Verify(max3) -> Proceed` の固定順序と同一契約を維持する。

#### 2.9.5 CE4 mock/stub execution boundary（implementation-ready）

- APIは CE4 契約検証用に `sourceBundleHash=mock:<64hex>` を受理してよい。
- 未確定項目は次の stub を返して隔離する（fail-closed を優先）。
  - `501 ce4_stubbed_exit_code_mapping`
  - `501 ce4_stubbed_principal_masking`
  - `501 ce4_stubbed_audit_transport`
- stub 応答時も `equivalenceKey`, `queryCanonicalHash`, `bundleHash`, `schemaVersion` を監査イベントへ記録し、`result=ng` で終了する。
- 本節の stub は契約確定までの暫定隔離であり、成功系の代替として利用してはならない。

### 2.10 Polygon Handoff Contract Verify（FB-P0-2A2B2C）

Polygon auto-fit の backend接続準備として、A2比較キーの最小契約を検証する。

**POST** `/docs/{doc_id}/polygon-handoff/verify-contract`

- Request body:
  - `input.gateApprovalRef: string`
  - `input.a2VerifyRef: string`
  - `input.inputHash: string`（sha256 hex / 64桁）
  - `input.deterministicTieBreakOrder: ["padding_compliance", "self_intersection_avoidance", "minimum_area_delta", "minimum_vertex_count"]`
  - `expectedOutput.outputPolygonHash: string`（sha256 hex / 64桁）
  - `expectedOutput.paddingViolationCount: number`（>=0）
  - `expectedOutput.tieBreakOrder: ["padding_compliance", "self_intersection_avoidance", "minimum_area_delta", "minimum_vertex_count"]`
  - `expectedOutput.tieBreakOrderChanged: boolean`（後方互換。`tieBreakOrder` 未送信時に必須）
- Response:
  - `status: "ok" | "rollback_required"`
  - `rollbackRequired: boolean`
  - `failureReasons: string[]`
  - `verificationKey: string`（`sha256(inputHash + ":" + outputPolygonHash)`）
- Error:
  - 404: `doc_id` が存在しない
  - 422: hash format などの契約違反

---

## 3. レスポンス例（概要）

### 3.1 DocumentV1（レスポンス）

```json
{
  "version": 1,
  "id": "doc_...",
  "title": "",
  "createdAt": "2026-02-10T00:00:00Z",
  "updatedAt": "2026-02-10T00:00:00Z",
  "transform": {"panX": 0, "panY": 0, "zoom": 1},
  "cards": [{"id": "c1", "text": "...", "x": 120, "y": 80}],
  "edges": [{"id": "e1", "fromId": "c1", "toId": "c2", "type": "related"}],
  "islands": []
}
```

---

## 4. エラー設計（最小）

MVPでは、エラーを過度に作り込まない。ただし、実装済みの安全境界と契約境界は区別して返す。

- 400：入力スキーマ不正（Pydanticのvalidation errorを整形）
- 403：認可、readOnly、review attribution identity などの安全境界違反
- 404：doc not found
- 409：`If-Match` 不一致、重複する判断ログなどの競合
- 422：A1契約フィールドや enum などの契約違反
- 500：内部エラー

---

## 5. 現行限定契約と将来拡張の境界

### 5.1 現行の限定契約

- `ETag` / `If-Match`: Document全体保存の楽観ロックとして実装済み。個別エンティティの差分同期ではない。
- 認証/認可: `AuthContext` 正規化、strict provisioning、access-control adapter、readOnly / SafeMode優先判定を提供する。完全な組織権限管理UIやRBACエンジンは含まない。
- 監査: view/export/context/proposal 系のイベント連携点を持つ。監査ログ閲覧UIや保持期限管理は含まない。
- AI/Context: proposal-only、mock-first、closed-world契約を中心に提供する。AI提案の自動適用や確定昇格は含まない。
- Merge decision / Similar candidate: append-read / derived の限定契約として提供する。Document内エンティティの個別CRUDではない。

### 5.2 非MVPまたは別Issueで扱う拡張

- Patch APIによる一般的な差分同期。
- サーバ採番の `POST /docs` 標準化。
- read-only link、公開URL、共有管理画面などの完全な共有機能。
- 管理者向け一覧、削除、アーカイブ、所有者移管、保管期限管理。高権限データライフサイクル操作はAccepted済み `ADR-0035` で標準機能外と固定され、本文を含まない監査メタデータ閲覧候補だけを `DATA-MAINT-04` でOpen管理する。本文閲覧、未レビュー情報閲覧、横断検索、保持期限、自動削除、所有者移管は、このAPI契約では提供しない。
- 大規模マルチテナント向けの権限管理UI、監査検索UI、SCIM連携。

---

## 6. 次に作るもの

- `02_Architecture/llm_provider_spec.md`
- `02_Architecture/llm_input_ir_spec.md`
- `02_Architecture/deployment.md`

---

## 7. Publishing metadata の扱い（FB-RM-PUB-01）

- `view.json` / `packs/index.json` の `visibility` は **公開範囲ラベル用メタデータ** として扱う。
- `visibility` の値は `Public | Unlisted | Org | Restricted` を採用し、不正値は validator で拒否する。
- 後方互換として、`view.json` 欠損時は `Restricted`、`packs/index.json` 欠損時は `Public` を補完する。
- `visibility` は APIの共有可否判定を上書きしない。外部サービスとの共有制御は引き続き SafeMode / share/export policy を正本とする。


## 8. AccessControlAdapter API契約（FB-RM-PUB-04）

roles/groups/policyRef に基づく認可判定は、API本体ではなく `AccessControlAdapter` へ外部委譲する。

### 8.1 入力（API → adapter/hook）

- `action`: `read | write | export | share`
- `auth.actorRef`: `x-actor-ref` ヘッダ（任意）
- `auth.roles`: `x-auth-roles` ヘッダ（`,` 区切り、任意）
- `auth.groups`: `x-auth-groups` ヘッダ（`,` 区切り、任意）
- `auth.traceId`: `x-trace-id` ヘッダ（任意）
- `resource.visibility`: `x-doc-visibility` ヘッダ（`Public | Unlisted | Org | Restricted`）
- `resource.policyRef`: `x-policy-ref` ヘッダ（任意）
- `safeMode`: ルート側のsafeMode（export-auditではpayload.safeMode）
- `readOnly`: `X-Read-Only` ヘッダ（`1`/`true`）

正規化ルール:

- `x-auth-roles` / `x-auth-groups` が未指定・空文字・`null` 相当値のときは `[]` として扱う。
- `x-policy-ref` は trim 後に空文字なら `null` として扱う。
- API本体は roles/groups/policyRef の意味解釈を行わない（外部委譲）。

上記visibility/policyRef headerはsingle-tenant互換resolverだけの契約である。SaaS profileでは公開headerを無視し、`tenantId + docId`で取得したserver-owned `document_access_metadata`のvisibilityと非秘密`policyBindingId/version`を使う。生のpolicyRefはDBへ保存せず、trusted runtime binding resolverがbinding IDから一時的に解決した値だけをPDPへ渡す。metadata、binding、runtime resolverのいずれかが欠損・不正・到達不能なら、`Restricted + policyRef欠損`としてdeny fail-safeへ倒す。

### 8.2 出力（adapter/hook → API）

```ts
type AccessDecision = {
  allow: boolean;
  readOnly?: boolean;
  reason?: string;
};
```

- `allow=false` の場合は API は `403` を返す。
- `reason` は `Access denied: <reason>` として観測可能。
- 本体は decision の解釈のみを行い、roles/groups の評価規則は持たない。

### 8.3 fail-safe

SafeMode/readOnly 優先順:

1. `safeMode=true` かつ `action in {export, share}` は常に拒否（`reason=safe_mode`）
2. `readOnly=true` かつ `action in {write, export, share}` は常に拒否（`reason=read_only`）
3. その後に adapter判定と policyRef fail-safe を評価


- 条件: `visibility in {Org, Restricted}` かつ `policyRef` 欠損。
- 既定 `read_only`: `read` のみ許可、`write/export/share` は `403`。
- オプション `deny`: 全アクション `403`。
- 実装パラメータ: `KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE=read_only|deny`。

fail-safe マトリクス:

- `policyRef` 欠損/空白（`visibility in {Org, Restricted}`）: `policy_ref_missing`
- `policyRef` 不達（接続失敗/timeout）: `policy_ref_unreachable`
- `policyRef` 無効（形式不正/失効/署名不正）: `policy_ref_invalid`
- adapter例外/想定外応答: `adapter_error`

上記4系統は `KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE` に従い `read_only` または `deny` へ倒す。`visibility` が `Public/Unlisted` の場合は欠損系の強制fail-safe対象外。

### 8.4 監査イベント連携点

- `GET /docs/{doc_id}` でアクセス許可後に `eventType=view` を送信。
- `POST /docs/{doc_id}/export-audit` でアクセス許可後に `eventType=export` を送信。
- `POST /docs/{doc_id}/context-audit` でアクセス許可後に `eventType=query|bundle|proposal|apply` を送信。
- 監査送信は既存の fail-open dispatcher 方針を維持する（監査送信失敗で本体機能は停止しない）。
- event envelopeの`tenantId`は、認可・repositoryと同じserver-resolved TenantContextから設定する必須fieldであり、自由形式metadataやclient入力から補完しない。欠損、空値、前後空白、制御文字、256文字超のtenantIdではeventを構築しない。
- HTTP送信payloadは64KiB以下、metadataは32 field以下、keyは128文字以下、文字列値は1,024文字以下に制限する。本文・credential系keyは固定値へredactし、過大値や非finite numberをそのままqueue／送信先へ渡さない。transport失敗時のfail-open方針はこの構造検証を迂回しない。

最小記録項目（PII非保存）:

- 必須: `eventType`, `schemaVersion`, `occurredAt`, `tenantId`, `docId`, `action`, `decision.allow`, `policyRefPresent`
- 任意: `decision.readOnly`, `decision.reason`, `visibility`, `adapterName`, `traceId`, `amr`, `acr`, `aal`, `authTime`
- 非保存: `policyRef` 生値、`roles/groups` 生値、token/assertion 生値、WebAuthn credential id、ドキュメント本文

### 8.5 実運用アダプタ設定（OIDC/SAML接続）

- `KJ_ATLAS_ACCESS_CONTROL_ADAPTER=external_http` で、APIは外部 policy 接続先（endpoint）へ `POST` 委譲する。
- endpointはcredential/query/fragmentを含まないHTTPS、またはloopback HTTPに限定し、固定bearerやIdP issuerだけが残る不完全設定、0以下または30秒超のtimeoutを起動時に拒否する。endpoint未設定時のsingle-tenant互換fallback自体は維持する。
- request body は `AccessRequest` 契約から構成し、`auth.roles/groups` と `resource.policyRef` の意味解釈は行わない。一方で送信前の安全境界として、UTF-8 JSON全体を64KiB以下、識別子を256文字以下、`policyRef`を2,048文字以下、roles/groupsを各64件以下の重複なしcanonical文字列に限定する。
- subject/resource欠損、制御文字・前後空白、未知のaction/visibility、型不正、上限超過を含むserver-composed requestはtransport前に拒否し、raw値をclient・logへ反射せず`adapter_error`としてfail-safeを適用する。
- request header には `x-acl-auth-mode: none|oidc|saml` を付与し、必要時のみ `Authorization: Bearer <static>` / `x-idp-issuer` / `x-trace-id` を付与する。
- 応答は `allow:boolean`（必須）+ `readOnly:boolean?` + `reason:string?` の最小契約。object以外、余分なfield、64KiB超、非UTF-8/非JSON、512文字超または制御文字を含むreasonは受理せず、応答値をclient・logへ反射せずに`policy_ref_invalid`としてfail-safeを適用する。
- `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_ENDPOINT` が未設定の場合、`external_http` 指定でも `noop` へフォールバックする（可用性優先）。

### 8.6 互換性

- adapter未設定（`noop`）では既存挙動を維持する。
- API本体にRBACエンジンは実装しない（非目標）。

## 9. AUTH-SCHEMA-01 API契約（JIT / strict provisioning）

### 9.1 AuthContext 正規化

- 入力ヘッダ（設定差し替え可）:
  - `KJ_ATLAS_AUTH_PROVIDER_FIELD`（既定 `x-auth-provider`）
  - `KJ_ATLAS_AUTH_USER_FIELD`（既定 `x-forwarded-user`）
  - `KJ_ATLAS_AUTH_SUBJECT_FIELD`（既定 `x-auth-subject`）
  - `KJ_ATLAS_AUTH_EMAIL_FIELD`（既定 `x-forwarded-email`）
  - `KJ_ATLAS_AUTH_NAME_FIELD`（既定 `x-forwarded-name`）
- 正規化後:
  - `AuthContext.userId`: `users.id`
  - `AuthContext.actorRef`: `user:<users.id>`
  - `AuthContext.provider` / `AuthContext.externalUid`
- reviewerRef解決:
  - `KJ_ATLAS_REVIEWER_REF_RESOLVER_ADAPTER`（既定: `user_id`）で `reviewerRef/ownerRef` を解決する。
  - adapter実装は `resolve(auth_context) -> { reviewerRef, ownerRef }` 契約を満たす。
  - profile:
    - `user_id`: `user:<users.id>`（未認証は `actorRef` → `null`）
    - `sso_subject`: `user:sso:<provider>:<externalUid>`（不足時は `user_id` フォールバック）
  - 責務境界: resolverは reviewerRef/ownerRef生成のみを行い、reviewEvents/export/import schemaを変更しない（opaque string互換維持）。
  - adapter未設定/不正値時は `user_id` フォールバック（既存 local運用維持）。
- 属性境界:
  - persist: `provider`, `external_uid`, `display_name`, `email`
  - transient only: `roles`, `groups`, `policyRef`, `amr`, `acr`, `aal`, `auth_time`, `trace_id`
  - forbidden: password/hash/secret, WebAuthn credential id, raw policy token

### 9.2 strict mode 拒否契約

- 条件: `KJ_ATLAS_ALLOW_JIT_PROVISIONING=false` かつ `provider+external_uid` が `user_identities` に未登録。
- 応答: `403 Forbidden`
- エラーボディ（最小契約）: `{ "code": "identity_not_provisioned", "message": "Identity not provisioned. Pre-provision via /admin/provision/users before access." }`

型契約（モック互換のための最小）:

```ts
export type StrictProvisioningError = {
  code: "identity_not_provisioned";
  message: string;
  requestId?: string;
};
```

- `code` は固定値。
- `message` は可読文（文言変更は許容、意味は固定）。
- `requestId` は任意（監査/追跡用途）。
- 追加フィールドは許容するが、依存実装は上記3項目のみで判定可能であること。

### 9.2.1 strict mode の運用責任境界（承認フロー固定）

- backend 実装責務:
  - strict mode 条件に一致した要求を例外なく `403` で拒否する。
  - 緊急時でもアプリ内の一時バイパス（特定ユーザー許可など）を実装しない。
- 例外承認責務:
  - `KJ_ATLAS_ALLOW_JIT_PROVISIONING` の切替承認は **Security Officer + System Owner の2者承認** を必須とする。
  - 実行（環境変数変更/再起動）は Platform Operator が行い、変更記録（時刻・理由・承認者）を監査証跡に残す。
- 承認なき例外は不許可:
  - 開発者判断のみで strict mode を緩和してはならない。
  - 監査時は「承認記録がない緩和設定」を設定不備として扱う。

### 9.3 事前プロビジョニング API（最小）

- `POST /admin/provision/users`
  - request: `{ provider, externalUid, displayName?, email? }`
  - `201` response (created): `{ userId, reviewerRef, ownerRef, provisioned=true }`
  - `200` response (idempotent retry): `{ userId, reviewerRef, ownerRef, provisioned=false }`
  - 冪等: 同一 `provider+externalUid` の再試行は `provisioned=false` を返す
  - `409` response: 既存subjectへ矛盾する `displayName` / `email` を再投入した場合は `identity_already_provisioned_conflict` と可読 `message` を返す

型契約（I/F固定）:

```ts
export type AdminProvisionUserRequest = {
  provider: string;
  externalUid: string;
  displayName?: string;
  email?: string;
};

export type AdminProvisionUserResponse = {
  userId: string;
  reviewerRef: `user:${string}`;
  ownerRef: `user:${string}`;
  provisioned: boolean;
};

export type AdminProvisionUserConflictError = {
  code: "identity_already_provisioned_conflict";
  message: string;
};
```

- 判定規約: クライアントは `2xx + provisioned`、`403 + code=identity_not_provisioned`、`409 + code=identity_already_provisioned_conflict` の3分岐のみを必須サポートとする。
- 非目標: 本契約ではページング・検索・一括削除・SCIM互換項目は定義しない。

本APIは将来の管理者CLI/SCIM連携の最小置換点として扱う。

### 9.4 移行契約（expand/contract）

- expand: `users` / `user_identities` 追加後、Alembic `20260717_0007`以降は作成処理で旧`provider+external_uid`と`identity_provider_id+subject`を二重書きし、解決時は後者を優先する。expand列が空の旧行だけは旧keyへbounded fallbackし、成功時に新bindingを補完する。両keyが異なるUserへ一致する場合や既存bindingと入力が不一致の場合は`identity_mapping_conflict`で拒否する。互換IdPはsingle-tenant移行用であり、検証済みissuer/audienceに基づくSaaS認証とは扱わない。
- contract: attribution APIは `reviewerRef` / `ownerRef` を `user:<users.id>` に統一し、外部subject直参照を受け付けない。
- strict modeは contract 側の強制条件として扱い、未登録subjectを `403` で拒否する。

## 10. SaaS TenantContext / capability契約（ADR-0059、L0 Planned）

本節はAccepted済みのtarget契約である。現行APIはsingle-tenant相当であり、`SAAS-TENANT-01`のstorage・認可・runtime gate・越境テストが完了するまでSaaS profileを有効化しない。`GET /session/context`のfail-closed route境界は実装済みだが、信頼済みauth edgeがidentity resolverを注入しない既定状態では503として閉じる。active tenant変更endpointとtenant switcherは未実装・非公開である。

### 10.1 session context（GET実装済み・SaaS runtime gated）

- `GET /session/context`
  - 現在の検証済みTenantContext、利用者がactive membershipを持つtenant候補、tenant-scoped capabilityを返す。
  - tenant候補はサーバーでallowlistされたmembershipだけとし、tenant検索や自由入力を提供しない。
  - identity、TenantContext、active membership、membership ID、capability snapshotをrequestごとに再確認する。membership IDはresolver値をそのままPDPへ渡さず、`principalId + tenantId`のactive membershipからserver-sideで再生成した値との一致を必須にする。信頼済みresolver欠損、single-tenant互換context、停止・差し替えmembership、不正・未知capabilityではfail-closedとする。
  - responseは64KiB以下、principal/tenant IDを256文字以下、tenant display nameを256文字以下、capability versionを128文字以下、available tenantを1〜256件の重複なし、effective capabilityを既知11件以下の重複なしへ限定する。server-side session値が不正・非表示・過大な場合は`503 session_context_unavailable`、capability snapshot違反は`503 capability_resolution_unavailable`として値を反射せず閉じる。
  - `Cache-Control: no-store`と`Pragma: no-cache`を付け、利用者表示名・email・外部IdP subject・membership ID・role/groupを返さない。
- `POST /session/active-tenant`
  - 計画中であり、認証sessionへactive tenantを保存・更新する契約が確定するまでrouteを追加しない。
  - request: `{ tenantId }`
  - backendがmembershipを再確認し、新TenantContextを確定した場合だけ更新後contextを返す。
  - 不明tenant、他利用者のtenant、停止membershipは存在を推測させない`404`相当とする。

```ts
export type TenantSessionContextV1 = {
  principalId: string;
  activeTenant: { id: string; displayName: string };
  availableTenants: Array<{ id: string; displayName: string }>;
  effectiveCapabilities: string[];
  capabilityVersion: string;
};

export type ActiveTenantRequestV1 = {
  tenantId: string;
};
```

`effectiveCapabilities`は表示補助であり、APIの再認可を代替しない。cacheする場合は`deployment + tenantId + principalId + capabilityVersion`で分離し、auth tokenの有効期限を越えて保持しない。

active tenant変更の成功responseはfrontend validatorを通過した後だけ遷移へ使用する。遷移時は進行中requestをabortし、workerをdisposeし、object URLと文書・選択・検索等のmemory stateを破棄し、旧browser storage scopeだけを削除してhard document replacementを行う。cleanup/storage削除の一部が失敗しても旧DOMを継続利用せずreplacementを優先する。未検証responseではcleanup、storage変更、navigationを開始しない。

`principalId`は認証済みUserに対応するserver-managed opaque IDであり、表示名やemail、外部IdP subjectを返さない。browser storage scopeのprincipal要素にはこの値だけを使う。

実装準備として、署名・issuer・audience検証後の証跡を受け取る内部resolver、IdP/tenant binding、UserIdentity、active membershipの再照合、active membershipだけのtenant候補列挙と切替選択serviceを実装済みである。session responseの内部builderと`GET /session/context` routeは、active tenantの再照合、opaque principalId、allowlist済みtenant候補、trusted capability resolverの既知capabilityだけを受理し、識別子・一覧件数・response sizeを上限内へ閉じる。不正・欠損したcapability snapshotは`503 capability_resolution_unavailable`、不正・過大なsession値は`503 session_context_unavailable`としてfail-closedにする。active tenant切替の内部境界も、現在のverified/trusted contextがまだ有効であること、要求tenantがcanonicalかつ同じprincipalのallowlistに含まれることを再確認し、成功後だけ新tenantのcapability snapshotを解決する。frontend側は`no-store`・same-originでGETし、64KiB以下のresponse validatorを通過し、active tenantがavailableTenantsと一致したcontextだけをbrowser storage scopeへ変換する。未知・重複capability、余分なfield、非表示・過大値は利用しない。strict external HTTP capability resolverとapplication lifecycleの既定unavailable配線は実装済みである。HTTP headerやqueryを直接verified evidenceへ変換する処理、trusted SaaS identity resolverの実runtime接続、`POST /session/active-tenant`、App起動時のsession bootstrap配線は未実装であり、SaaS profileは引き続き閉じる。

capability resolverは`principalId`、`tenantId`、DB再照合済み`membershipId`だけをtrusted endpointへPOSTし、各値を256文字以下のcanonicalなserver-owned ID、request全体を64KiB以下に限定する。不正・欠損・過大contextはtransport前に停止する。応答は`effectiveCapabilities`と`capabilityVersion`だけを受理し、capabilityは§10.2の既知値に限定して重複・未知値・roles/groups等の余分なfieldを拒否する。responseは64KiB以下、versionは128文字以下のopaque canonical IDとし、4xx、timeout、transport障害、非JSON、不正shapeは内部詳細を反射せず`capability_resolution_unavailable`へ正規化する。API keyと応答bodyはDB・監査・diagnosticsへ保存しない。

### 10.2 tenant-scoped access request

SaaS profileでAccessControlAdapterへ渡すrequestは、§8.1に加えて次を必須とする。

```ts
export type TenantScopedAccessRequestV1 = {
  action:
    | "document.read"
    | "document.write"
    | "document.export"
    | "document.share"
    | "document.policy.manage"
    | "membership.provision"
    | "agent.register"
    | "agent.revoke"
    | "audit.read";
  auth: AuthContext;
  tenant: TenantContextV1;
  resource: {
    tenantId: string;
    kind: "document" | "membership" | "agent_registration" | "audit";
    id: string;
    policyRef?: string;
  };
  safeMode: boolean;
  readOnly: boolean;
};
```

評価順はAuthContext解決、TenantContext解決、active membership確認、`tenantId + resourceId`によるserver-side lookup、主体tenantと資源tenantの一致、SafeMode/readOnly guard、外部PDP、API enforceとする。tenant不一致はPDPへ委譲せず常にdenyする。resourceのtenant/visibility/policyRefをclient headerやpayloadから採用しない。

### 10.3 SaaS fail-closed / response境界

- tenant不明・不一致、membership停止、adapter欠損、PDP timeout/無効応答ではreadを含めてdenyする。
- 他tenantのresource IDは`404`相当とし、list/search/count/paginationにも存在を混入させない。
- current tenant内でresourceの存在が認可済みだが操作capabilityが不足する場合は`403`を返してよい。
- `noop`、endpoint欠損時noop fallback、`read_only` fail-safeはSaaS profileで禁止する。§8.3〜8.6の互換挙動はsingle-tenant profileだけに適用する。
- auditにはtenantId、opaque actor/resource ID、action、decision、policy/capability version、correlation IDだけを記録し、本文、タイトル、role/group生値、tokenを記録しない。

Tenant-scoped access-control entry pointは、TenantContext欠損、resource tenant欠損、両tenant不一致をそれぞれ`tenant_context_missing`、`resource_tenant_missing`、`tenant_mismatch`として外部PDP呼出し前にdenyする。このguardは`read_only` fail-safeから独立し、tenant境界の不備をread許可へ変換しない。Document routeのresource解決もapplication lifecycleで設定するresolver境界とし、現行profileは公開headerを読む`SingleTenantHeaderResourceResolver`、将来SaaS profileはheaderを無視して`tenantId + docId`をDB lookupする`ServerOwnedDocumentResourceResolver`を使用する。後者は既存行のtenantを確認し、未整備のvisibility/policyRefを`Restricted`/欠損へ倒すためdeny modeで安全側に停止する。server-owned policy metadata storeと外部binding resolver adapterは実装済みだがSaaS runtime配線は未実装であり、単一テナント互換resolverをSaaS境界として扱わない。

`external_http` binding resolverは、server-owned metadataから得た`tenantId`、非秘密`bindingId`、`policyVersion`だけを信頼済みendpointへPOSTする。tenantIdは256文字以下、bindingId/policyVersionは128文字以下のcanonical ID、request全体は64KiB以下に限定し、不正・過大lookupはtransport前に解決失敗へ倒す。応答は`{"policyRef": string}`だけを受理し、64KiB超、余分なfield、空白・制御文字を含む値、2,048文字超、非JSON、4xx拒否、timeout/transport障害は解決失敗とする。raw request/responseや内部例外詳細をclient・監査・logへ反射しない。返却されたpolicyRefはAccessRequest内だけでPDPへ渡し、永続化しない。resolver未設定は従来どおりunavailableとして`Restricted + policy_ref_missing`へ倒す。

外部PDP、監査HTTP、binding/capability resolver、LLM providerのoutbound HTTPは3xx redirectを追跡しない。元のendpointに対するscheme/host検証やallowlistをredirectで迂回させず、Authorization header、tenant context、policyRef、promptを別接続先へ転送しない。redirect応答は各adapterの既存のHTTP/transport失敗契約へ正規化する。

### 10.4 文書アクセス設定管理API（実装済み・SaaS runtime gated）

Tenant Admin向けに次のrouteを実装する。ただし、application lifecycleへ信頼済みSaaS identity resolverとtenant capability resolverが明示注入されない限り`503`で閉じる。single-tenant互換context、公開headerのrole/group、Document owner、`document.write`、Platform operator capabilityを管理権限へ昇格させない。

- `GET /tenant-admin/document-access`
  - active tenant内の文書IDと`visibility`、設定有無、binding状態、policy version、更新時刻、opaque revisionだけを返す。
  - title、本文、card、review集計、tenantId、binding IDを一覧responseへ含めない。metadata未登録は`Restricted / unconfigured`として返す。
- `GET /tenant-admin/document-access/{doc_id}`
  - 一覧項目に加えて、編集対象の非秘密`policyBindingId`だけを返す。responseの`ETag`はbodyの`revision`と一致させる。
- `PUT /tenant-admin/document-access/{doc_id}`
  - bodyは`visibility`、`policyBindingId?`、`policyVersion`だけを受け付ける。extra fieldは拒否し、validation responseへ入力値を反射しない。
  - `policyBindingId`と`policyVersion`は128文字以下のopaque canonical IDに限定し、URL、token、raw policyRef、assertionを受け付けない。`Org/Restricted`はbinding必須、`Public/Unlisted`はbinding保存禁止とする。
  - 一覧または詳細で得たrevisionを`If-Match`へ必須指定する。欠損は`428 document_access_precondition_required`、不一致または同時更新は`409 document_access_conflict`とする。wildcardで競合検査を迂回できない。
  - metadata更新と`document_access_admin_audit_events`追加を同一transactionで確定する。auditはtenantId、opaque principal/doc ID、action/decision、policy/capability version、server-generated correlation ID、時刻だけを持ち、binding ID、raw policyRef、title、本文、tokenを保存しない。

他tenantにしか存在しないdocIdは`404`とし、list/detail/updateはすべて解決済みTenantContextでDB guardを設定する。APIで`document.policy.manage`を毎回再評価し、capability resolver欠損・不正応答は`503 capability_resolution_unavailable`へfail-closedにする。

本routeは管理APIとtransactional auditの境界を先行実装した状態である。検証済みauth edge、実PDP capability resolver、binding secret store resolver、SaaS profileのdeny-only配線、PostgreSQL RLS実地matrixが揃うまではfrontendから有効化せず、共有SaaS対応済みとは扱わない。

### 10.5 管理面の予約capability

Tenant Adminは`document.policy.manage`、`membership.provision`と`agent.register/revoke`、Platform Control Planeは`tenant.provision/suspend`を使用する。両者はroute surfaceと認可audienceを分離し、platform capabilityから`document.read`や`document.policy.manage`を暗黙導出しない。汎用role editor、tenant横断文書検索、support impersonationは追加しない。

### 10.6 single-tenant互換

既存profileは内部`local-default` TenantContextを注入する互換resolverを使用できる。認証済み利用者ではUser、Tenant、TenantMembershipがすべてactiveであることをrequestごとに確認し、停止・欠損時は`tenant_membership_inactive`で拒否する。匿名利用は既存single-tenant互換に限ってmembershipなしを維持する。Document routeはapplication lifecycleで設定された信頼済みresolverだけを呼び、公開Document APIへtenantIdを入力項目として追加せず、header・query・path・payloadのtenant値をresolverへ渡さない。URLのdocIdは解決済みTenantContext内で検索し、同じcontextを外部PDP payload、本文を含まないaudit metadata、PostgreSQL transaction-local DB settingへ伝播する。PostgreSQL RLSはsetting欠落時にread/writeとも行を許可せず、SQLiteではこのDB guardをSaaS境界として扱わない。exportされたtenantIdやmembershipをimport先の権限として採用しない。

## 11. 形成履歴（Informative）

2026-04-30〜2026-05-19のCE0/CE1/CE4 mock-first、Stream同期、freeze/handoff形成記録は [API contract formation history](history/api-contract-formation-2026-04-to-05.md) へ分離した。現在の型は`schemas.md`、責務・信頼境界は`architecture.md`、endpoint/status/error/認証/副作用は本書を正本とする。
