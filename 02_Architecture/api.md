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

CE-1 は実装方式に依存しない契約固定フェーズとし、frontend/backend は mock を介して疎結合に開発できるものとする。
また、CE-2/CE-4 は CE-1 実装完了待ちを禁止し、本契約を満たす mock API で先行検証を継続する。

Phase 1〜6 fixed policy（各Phase先頭で Read を実施し、`Plan -> Execute -> Verify -> Proceed` を反復）:
1. Phase 1（Read）: `ContextQuery` / `ContextBundle` 最小I/Fを固定し、`previewConfirmed=true` を必須化する。
2. Phase 2（CDC）: `previewConfirmed=false` を常に `422 preview_required` として拒否する契約判定を固定する。
3. Phase 3（Plan）: canonical hash（`queryCanonicalHash`, `bundleHash`）の算出手順と AC/DoD を固定する。
4. Phase 4（Execute）: mock-first 連携で契約検証を進め、CE0/CE2/CE4 の完了待ち依存を作らない。
5. Phase 5（Verify）: `previewConfirmed=false -> 422 preview_required` と deterministic hash 契約の語彙整合を検証する。
6. Phase 6（Proceed）: CE2/CE4 へ固定I/F（`ContextQuery/ContextBundle/queryCanonicalHash/bundleHash/sourceBundleHash`）を引き渡し、実装待機を禁止する。

フェイルセーフ: Verify 失敗の自己修復は最大3回まで許可し、4回目失敗時は即停止して人間判断へエスカレーションする。

CE0境界（参照専用固定）:
- `CE0-SAFEMODE-IF`: safeMode既定ONと `allowUnreviewedText=false` 既定を緩和しない。
- `CE0-REVIEW-IF`: `unreviewed -> human_reviewed` 昇格は人手のみ（AI自動昇格禁止）。
- `CG-01..05`: Consensus Graph への direct write を禁止し、`patch + approval` 以外の適用経路を許可しない。

**POST** `/context/query`

- Purpose: Query Preview通過済みの `ContextQuery` を検証・正規化する。
- Request body (required):
  - `queryId: string (UUID)`
  - `goal: string`
  - `scope: "document" | "view" | "island"`
  - `depth: integer (0..5)`
  - `constraints: object`
  - `reviewFilter: "reviewedOnly" | "includeUnreviewed"`
  - `safeModePolicy: "strict"`
  - `outputMode: "summary" | "proposal" | "candidate"`
  - `previewConfirmed: true`
- Error:
  - `422 preview_required`: `previewConfirmed != true`
  - `400 unknown_contract_key`: CE1 v1 最小I/F外のキー、または enum/range違反を fail-closed で拒否

**POST** `/context/bundle`

- Purpose: Deterministic projection を実行し `ContextBundle` を返す。
- Request body: `{ "query": ContextQuery }`
- Response body (required keys):
  - `queryId`, `queryCanonicalHash`, `bundleHash`, `selected`, `relations`, `evidence`, `contradictions`, `reviewFlags`, `truncationMeta`, `excludedReason`

`bundleHash` canonicalization (normative):
1. 非決定論フィールド（timestamp/trace/latency）を除外。
2. 配列ソートを固定（selected=id asc, relations=(type,from,to) asc, evidence=cardId asc, contradictions=(weight desc,id asc)）。
3. canonical JSON 化（キー辞書順、UTF-8、余分な空白なし）。
4. `sha256(canonical_json)` を16進小文字で返す。

判定可能要件: 同一 canonical query に対し `bundleHash` が一致しない場合、サーバは `409 nondeterministic_bundle` を返し監査ログへ記録する。

CE1 v1 fixed vocabulary（closed-world）:
- `422 preview_required`
- `400 unknown_contract_key`
- `409 nondeterministic_bundle`

運用停止条件:
- `previewConfirmed` 必須ゲートが破られる実装差分を検知した場合は No-Go。
- Verify の自己修復が3回を超えた場合は即停止（自動再試行を継続しない）。


#### 2.8.1 Mock validation plan（実実装依存切断）
- Scope: CE1 I/F契約（`ContextQueryV1` / `ContextBundleV1`）のみ。
- Test harness: `stubDatasetId=A2-minimal-v1` を固定し、実DB/実LLM/worker依存を持ち込まない。
- Required checks:
  1. `previewConfirmed=false` は常に `422 preview_required`。
  2. unknown key は常に `400 unknown_contract_key`。
  3. 同一canonical queryを3回再実行して `queryCanonicalHash` と `bundleHash` が3/3一致。
  4. 不一致発生時は `409 nondeterministic_bundle` を返し fail-closed。
- Handoff keys: CE2/CE4へ `queryCanonicalHash`, `bundleHash`, `sourceBundleHash` をread-onlyで引き渡す。



### 2.10 Stream A Contract Freeze Log（2026-04-30, Architecture only）

本節は Stream A（Critical Path）の契約固定ログであり、下流レーン参照用の **read-only 正本** とする。

#### Fixed I/F list（mock利用可能な最小契約）

- `ContextQueryV1`
  - required: `queryId, goal, scope, depth, constraints, reviewFilter, safeModePolicy, outputMode, previewConfirmed`
  - invariant: `previewConfirmed=true` 必須（違反は `422 preview_required`）
- `ContextBundleV1`
  - required: `queryId, queryCanonicalHash, bundleHash, selected, relations, evidence, contradictions, reviewFlags, truncationMeta, excludedReason`
  - invariant: same canonical query で deterministic `bundleHash`（不一致は `409 nondeterministic_bundle`）
- `ProposalPatchV1`
  - required: `proposalId, diff, sourceBundleHash, rationale, status, reviewState`
  - invariant: proposal-only（auto-apply禁止）
- `AuditEventV1`
  - required: `eventType, equivalenceKey` + operation関連キー
  - invariant: `query/bundle/proposal/apply` の監査4点欠損を成功扱いしない

#### schemaVersion freeze

- CE系契約は `v1` を固定し、**必須キー集合とエラー意味論**（`preview_required`, `unknown_contract_key`, `nondeterministic_bundle`）の破壊的変更を禁止する。
- 拡張は `v2` 追加でのみ許可し、`v1` 互換を維持する。

#### 変更禁止境界（Non-regression boundary）

- `safeMode` 既定ONと `allowUnreviewedText=false` 既定を緩和しない。
- AIによる `human_reviewed` 自動昇格を禁止する。
- `Working -> Consensus` 直書きを禁止し、`patch + approval` 以外の適用経路を禁止する。
- `preview` 経路をバイパスした apply/request を禁止する。

#### Audit log

- Stream: `A (Critical Path)`
- Freeze date (UTC): `2026-04-30`
- Scope: `02_Architecture/**`（契約/I-F定義のみ）
- Downstream handoff: CE1/CE2/CE4 は本節のI/Fを read-only 参照し、実装都合で再定義しない。

### 2.9 CE4 API/CLI/GUI 同値性・監査契約（CE4-API-CLI-AUDIT）

CE-4 は API/CLI/GUI の操作同値性と監査導線を固定する契約フェーズであり、実装方式やUI差分よりも監査可能性を優先する。
また CE4 は proposal-only 境界を維持し、`accepted/rejected` の自動確定経路を許可しない。

#### 2.9.0 Stream E boundary（proposal-only + API/CLI監査責務分離）

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

### 2.7 Polygon Handoff Contract Verify（FB-P0-2A2B2C）

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

最小記録項目（PII非保存）:

- 必須: `eventType`, `eventVersion`, `occurredAt`, `docId`, `action`, `decision.allow`, `policyRefPresent`
- 任意: `decision.readOnly`, `decision.reason`, `visibility`, `adapterName`, `traceId`, `amr`, `acr`, `aal`, `authTime`
- 非保存: `policyRef` 生値、`roles/groups` 生値、token/assertion 生値、WebAuthn credential id、ドキュメント本文

### 8.5 実運用アダプタ設定（OIDC/SAML接続）

- `KJ_ATLAS_ACCESS_CONTROL_ADAPTER=external_http` で、APIは外部 policy 接続先（endpoint）へ `POST` 委譲する。
- request body は `AccessRequest` 契約そのまま（`auth.roles/groups` と `resource.policyRef` を透過転送）とし、意味解釈は行わない。
- request header には `x-acl-auth-mode: none|oidc|saml` を付与し、必要時のみ `Authorization: Bearer <static>` / `x-idp-issuer` / `x-trace-id` を付与する。
- 応答は `allow:boolean`（必須）+ `readOnly:boolean?` + `reason:string?` の最小契約。契約不整合は `policy_ref_invalid` として fail-safe を適用する。
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

- expand: `users` / `user_identities` 追加後、APIは `provider+external_uid` で `users.id` を解決する。
- contract: attribution APIは `reviewerRef` / `ownerRef` を `user:<users.id>` に統一し、外部subject直参照を受け付けない。
- strict modeは contract 側の強制条件として扱い、未登録subjectを `403` で拒否する。

#### 2.8.x CE1 v1 contract clarification（2026-05-03）

- CE1 `ContextQueryV1` / `ContextBundleV1` は v1 固定の closed-world 契約であり、required key の削除・意味変更を禁止する。
- v1 の最小エラー語彙は次の3つを固定する。
  - `422 preview_required`
  - `400 unknown_contract_key`
  - `409 nondeterministic_bundle`
- `422 invalid_query_contract` は enum/range の補助バリデーション語彙としては許可されるが、上記3語彙の置換には使えない。
- API利用者向けのフォールバック挙動は fail-closed とし、`previewConfirmed` 未確認・hash非決定論・unknown key を成功扱いしてはならない。
- versioning方針: v1は互換維持、拡張は v2 追加で行う。

#### 2.8.2 CE0 Contract Freeze handoff（2026-05-04 / Stream B）

- Scope: CE0/CE1 契約I/F凍結（implementation非依存、mock-first）。
- Fixed handoff signatures（read-only）:
  - `ContextQueryV1`
  - `ContextBundleV1`
  - `ProposalPatchV1`
  - `AuditEventV1`
- mock contract policy:
  - 未実装箇所は **mock contract** として先行検証し、実装完了待機を禁止する。
  - `POST /context/query` と `POST /context/bundle` は stub/fixture で同一エラー意味論を維持する。
- deprecate policy（非互換候補の扱い）:
  1. v1 required key の削除・改名・意味変更は非互換として禁止（`v2` 追加でのみ許可）。
  2. `preview_required` / `unknown_contract_key` / `nondeterministic_bundle` の意味変更は禁止。
  3. v1 から v2 への移行期間中も v1 endpoint contract は read-only 互換維持とする。


### 2.10 Contract Freeze & Mock-first Baseline（2026-05-04）

#### Context
- CE1/CE2/CE4 の依存順を維持しつつ、下流が実装待機で停止しないため、I/Fを先に固定する必要がある。

#### Decision
- 固定I/Fは `ContextQueryV1` / `ContextBundleV1` / `ProposalPatchV1` / `AuditEventV1` の4型に限定する。
- 本章のAPIは `schemas.md` の型を参照し、型語彙の追加・削除・意味変更を行わない。
- mock-first 前提として、未実装区間は `A1-CONTRACT-MOCK-v1` 準拠の入出力検証で代替し、実装完了待ちを禁止する。

#### Consequences
- 下流ストリームは APIシグネチャ境界を read-only 参照し、再定義なしで並行作業可能になる。
- 契約変更が必要な場合は CDC（Context/Decision/Consequences）で再起票し、v1を直接変更しない。

#### 2.8.3 Stream B CE0/CE1 foundation sync（2026-05-06 / contract-only）

- Phase固定順序: Read同期 → I/F先行定義（ContextQueryV1/ContextBundleV1）→ mock契約依存切断 → Plan/Execute/Verify/Proceed → Stopper。
- v1 fixed semantics:
  - `previewConfirmed=false -> 422 preview_required`
  - unknown key -> `400 unknown_contract_key`
  - deterministic hash violation -> `409 nondeterministic_bundle`
- Mock-first handoff（read-only）:
  - `queryCanonicalHash`
  - `bundleHash`
  - `sourceBundleHash`
- Stopper:
  - safeMode既定値後退、preview gate破壊、自己修復3回超過を検知した場合は即時 `held` 停止。

### 2.11 Stream A freeze excerpt（2026-05-07, read-only handoff）

Contract Freeze / minimum I/F agreement を下流へ渡す機械可読抜粋（参照専用）。

```yaml
contract_freeze:
  id: HIL-RS-02-A1-CONTRACT-FREEZE-v1
  schema_version: "1.0.0"
  immutable:
    - contract_ids
    - schema_version
    - safe_mode_default
    - safe_mode_boundary
    - decision_queue_transition
  contract_ids:
    - A1-CRITIQUE-IF
    - A1-REDIFF-IF
    - A1-ATTR-IF
    - A1-ERROR-IF
  compatibility:
    allowed_transition:
      - Pending->Approved
      - Pending->Rejected
    unknown_contract_key: 400
  open_gate: "a1Status==Done && pendingDecisionQueueCount==0"
  proceed_when_unapproved: Needs-decision
```
#### 2.9.0b CE4 mock/stub execution boundary（implementation-ready）

- APIは CE4 契約検証用に `sourceBundleHash=mock:<64hex>` を受理してよい。
- 未確定項目は次の stub を返して隔離する（fail-closed を優先）。
  - `501 ce4_stubbed_exit_code_mapping`
  - `501 ce4_stubbed_principal_masking`
  - `501 ce4_stubbed_audit_transport`
- stub 応答時も `equivalenceKey`, `queryCanonicalHash`, `bundleHash`, `schemaVersion` を監査イベントへ記録し、`result=ng` で終了する。
- 本節の stub は契約確定までの暫定隔離であり、成功系の代替として利用してはならない。

### 9.5 Stream E freeze note (2026-05-10)

- Interface-first fixed set: `AuthContext` 正規化、strict拒否（`403 + identity_not_provisioned`）、`POST /admin/provision/users` の request/success/conflict 分岐。
- Backward compatibility: 必須分岐キーは `status/code/provisioned` を維持し、追加フィールドは optional 拡張のみ許可。
- Audit minimum: API契約では「誰が何を実行したか」を `actorRef/requestId/result` で追跡し、PII生値は保存しない。

## CE1 v1 Freeze Addendum（2026-05-17 / Stream B）

- `ContextQueryV1` / `ContextBundleV1` は v1 closed-world。未定義キーは常に `400 unknown_contract_key`。
- Preview gate は `previewConfirmed=false -> 422 preview_required` で固定。
- 同一 canonical query の `bundleHash` 不一致は `409 nondeterministic_bundle`（fail-closed）。
- A2 検証は `stubDatasetId=A2-minimal-v1` 固定。実DB/実LLM/worker 依存を禁止。
- CE2/CE4 への連携は read-only handoff のみ許可し、v1 契約改変は許可しない。

## CE0 interface freeze handoff baseline（2026-05-19 / Stream A）

### Context
- CE0 完了条件として、下流ストリームが実装待ちなしで mock 検証を継続できる「固定契約面」の明示が必要。

### Decision
- Fixed I/F（read-only）:
  - `ContextQueryV1`
  - `ContextBundleV1`
  - `ProposalPatchV1`
  - `AuditEventV1`
- Error contract（closed-world）:
  - `400 unknown_contract_key`
  - `422 preview_required`
  - `409 nondeterministic_bundle`
- Compatibility policy:
  - v1 は optional 追記のみ許可。
  - required key 削除・意味変更・enum再解釈は v1 で禁止。
  - 破壊的変更は v2 起票 + migrate plan を必須とする。
- Mock-first baseline:
  - `stubDatasetId=A2-minimal-v1`
  - `sourceBundleHash=mock:<64hex>`
  - 実DB/実LLM/worker が未接続でも契約検証を継続可能とする。

### Consequences
- 下流は契約を再定義せず、固定I/Fに対する CDC / fixture / audit チェックを独立実行できる。
- 契約逸脱は `contract drift` として即検出し、実装差分へ持ち込む前に停止できる。
