# API contract formation history (2026-04 to 2026-05)

Status: Informative history

Source document: [`02_Architecture/api.md`](../api.md)

Source anchors: former §2.8 Phase 1〜6 / §2.8.1 mock validation / §2.10 Stream A log / §2.8.x〜§2.11 handoff and freeze notes / §9.5 / CE1 addendum / CE0 handoff baseline

Covered period: 2026-04-30〜2026-05-19

Snapshot / source revision: `f0b1525d`（DOC-ARCH-02 H-B移動直前）

Retention reason: CE0/CE1/CE4のendpoint、error、mock-first検証を形成したPhase手順、Stream同期、freeze/handoffを、現在のAPI契約と誤認されない形で保持する。

Current normative anchors:

- [Context Query / Bundle endpoints and errors](../api.md#28-context-query--bundle-contractce1-context-foundation)
- [CE4 API/CLI/GUI equivalence and audit](../api.md#29-ce4-apicligui-同値性監査契約ce4-api-cli-audit)
- [Auth and strict provisioning API](../api.md#9-auth-schema-01-api契約jit--strict-provisioning)
- [Schema contracts](../schemas.md#12-ce1ce2ce4-型契約実装非依存)
- [Architecture responsibility and trust boundaries](../design/architecture.html#ce0-boundary)
- [CE1 v1 reconciliation issue](../../01_Plans/issues/issue-CE1-CONTRACT-01-v1-keyset-and-envelope-reconciliation.md)

この文書は形成履歴であり、現在のrequired/optional key、HTTP envelope、endpoint、status/error、認証、副作用、安全境界を上書きしない。以下の`fixed`、`freeze`、`Decision`、`read-only 正本`は当時の記録である。

## Former §2.8 formation workflow and CE0 boundary

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

## Former §2.8 request/response type restatement

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

## Former §2.8.1 Mock validation plan（実実装依存切断）

- Scope: CE1 I/F契約（`ContextQueryV1` / `ContextBundleV1`）のみ。
- Test harness: `stubDatasetId=A2-minimal-v1` を固定し、実DB/実LLM/worker依存を持ち込まない。
- Required checks:
  1. `previewConfirmed=false` は常に `422 preview_required`。
  2. unknown key は常に `400 unknown_contract_key`。
  3. 同一canonical queryを3回再実行して `queryCanonicalHash` と `bundleHash` が3/3一致。
  4. 不一致発生時は `409 nondeterministic_bundle` を返し fail-closed。
- Handoff keys: CE2/CE4へ `queryCanonicalHash`, `bundleHash`, `sourceBundleHash` をread-onlyで引き渡す。

## Former §2.10 Stream A Contract Freeze Log（2026-04-30, Architecture only）

本節は Stream A（Critical Path）の契約固定ログであり、下流レーン参照用の **read-only 正本** とする。

### Fixed I/F list（mock利用可能な最小契約）

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

### schemaVersion freeze

- CE系契約は `v1` を固定し、**必須キー集合とエラー意味論**（`preview_required`, `unknown_contract_key`, `nondeterministic_bundle`）の破壊的変更を禁止する。
- 拡張は `v2` 追加でのみ許可し、`v1` 互換を維持する。

### 変更禁止境界（Non-regression boundary）

- `safeMode` 既定ONと `allowUnreviewedText=false` 既定を緩和しない。
- AIによる `human_reviewed` 自動昇格を禁止する。
- `Working -> Consensus` 直書きを禁止し、`patch + approval` 以外の適用経路を禁止する。
- `preview` 経路をバイパスした apply/request を禁止する。

### Audit log

- Stream: `A (Critical Path)`
- Freeze date (UTC): `2026-04-30`
- Scope: `02_Architecture/**`（契約/I-F定義のみ）
- Downstream handoff: CE1/CE2/CE4 は本節のI/Fを read-only 参照し、実装都合で再定義しない。

## Former §2.8.x CE1 v1 contract clarification（2026-05-03）

- CE1 `ContextQueryV1` / `ContextBundleV1` は v1 固定の closed-world 契約であり、required key の削除・意味変更を禁止する。
- v1 の最小エラー語彙は次の3つを固定する。
  - `422 preview_required`
  - `400 unknown_contract_key`
  - `409 nondeterministic_bundle`
- `422 invalid_query_contract` は enum/range の補助バリデーション語彙としては許可されるが、上記3語彙の置換には使えない。
- API利用者向けのフォールバック挙動は fail-closed とし、`previewConfirmed` 未確認・hash非決定論・unknown key を成功扱いしてはならない。
- versioning方針: v1は互換維持、拡張は v2 追加で行う。

## Former §2.8.2 CE0 Contract Freeze handoff（2026-05-04 / Stream B）

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

## Former §2.10 Contract Freeze & Mock-first Baseline（2026-05-04）

### Context

- CE1/CE2/CE4 の依存順を維持しつつ、下流が実装待機で停止しないため、I/Fを先に固定する必要がある。

### Decision

- 固定I/Fは `ContextQueryV1` / `ContextBundleV1` / `ProposalPatchV1` / `AuditEventV1` の4型に限定する。
- 本章のAPIは `schemas.md` の型を参照し、型語彙の追加・削除・意味変更を行わない。
- mock-first 前提として、未実装区間は `A1-CONTRACT-MOCK-v1` 準拠の入出力検証で代替し、実装完了待ちを禁止する。

### Consequences

- 下流ストリームは APIシグネチャ境界を read-only 参照し、再定義なしで並行作業可能になる。
- 契約変更が必要な場合は CDC（Context/Decision/Consequences）で再起票し、v1を直接変更しない。

## Former §2.8.3 Stream B CE0/CE1 foundation sync（2026-05-06 / contract-only）

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

## Former §2.11 Stream A freeze excerpt（2026-05-07, read-only handoff）

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

## Former §9.5 Stream E freeze note (2026-05-10)

- Interface-first fixed set: `AuthContext` 正規化、strict拒否（`403 + identity_not_provisioned`）、`POST /admin/provision/users` の request/success/conflict 分岐。
- Backward compatibility: 必須分岐キーは `status/code/provisioned` を維持し、追加フィールドは optional 拡張のみ許可。
- Audit minimum: API契約では「誰が何を実行したか」を `actorRef/requestId/result` で追跡し、PII生値は保存しない。

## Former CE1 v1 Freeze Addendum（2026-05-17 / Stream B）

- `ContextQueryV1` / `ContextBundleV1` は v1 closed-world。未定義キーは常に `400 unknown_contract_key`。
- Preview gate は `previewConfirmed=false -> 422 preview_required` で固定。
- 同一 canonical query の `bundleHash` 不一致は `409 nondeterministic_bundle`（fail-closed）。
- A2 検証は `stubDatasetId=A2-minimal-v1` 固定。実DB/実LLM/worker 依存を禁止。
- CE2/CE4 への連携は read-only handoff のみ許可し、v1 契約改変は許可しない。

## Former CE0 interface freeze handoff baseline（2026-05-19 / Stream A）

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
