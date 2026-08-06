# Schema contract formation history (2026-05)

Status: Informative history

Source document: [`02_Architecture/schemas.md`](../schemas.md)

Source anchors: former §1.0.1 Stream D drift audit gate、former §11.1 Migration alignment snapshot、former CE1 v1 clarification、former §1.3以降のfreeze manifest / memo / Stream log / reaffirmation

Covered period: 2026-05-03〜2026-05-20

Snapshot / source revision: `49d48487`（DOC-ARCH-02 H-C移動直前）

Retention reason: CE0/CE1/CE2/CE4の型契約、Document version、migration、support levelを凍結・照合した形成経緯を、現在の型・validation・version互換規則と誤認されない形で保持する。

Current normative anchors:

- [CE0 responsibility-boundary meta-contract](../schemas.md#11-ce0-責務境界メタ契約)
- [CE1/CE2/CE4 type contracts](../schemas.md#12-ce1ce2ce4-型契約実装非依存)
- [Document versioning and support levels](../schemas.md#61-document-versioning--support-level運用ルールdata-contract-01固定)
- [Current data operations boundary](../data_model_operations_overview.html)
- [CE1 v1 reconciliation issue](../../01_Plans/issues/issue-CE1-CONTRACT-01-v1-keyset-and-envelope-reconciliation.md)

この文書は形成履歴であり、現在の型、required/optional key、列挙、validation、version、migration、support level、SafeMode境界を上書きしない。以下の`固定`、`freeze`、`Decision`、`Stop`は当時の記録である。

## Former §1.0.1 Stream D drift audit gate（2026-05-20）

本書の運用境界は `02_Architecture/data_model_operations_overview.html` と対で解釈する。次のいずれかを満たした場合は drift として `Stop` 判定にする。

1. `L1/L1.5/L2/L2.5/L3/L0` の語彙または意味が文書間で不一致。
2. `PUT /docs/{doc_id}` create-if-absent をMVP標準Create契約とする記述が不一致。
3. `Document.version` の非互換変更に version gate が伴わない。
4. Verify自己修復回数が3回を超えたまま継続しようとする。

## Former §11.1 Migration alignment snapshot（2026-05-20 / Stream D）

現行の物理スキーマは Alembic revision `20260314_0005` までで確定しており、本章の契約と次の対応で一致する。

- `20260211_0001_create_documents.py`:
  - `documents(id, version, updated_at, payload_json)`
- `20260303_0002_create_users_identities.py`:
  - `users(id, display_name, email, lifecycle_state, created_at, updated_at)`
  - `user_identities(id, user_id, provider, external_uid, created_at)`
  - `UNIQUE(provider, external_uid)`
- `20260313_0003_create_merge_decision_logs.py`:
  - `merge_decision_logs(id, doc_id, decision_id, group_id, snapshot_version, decided_at, payload_json)`
  - `UNIQUE(doc_id, decision_id)`
- `20260313_0004_add_merge_decision_log_indexes.py`:
  - `ix_merge_decision_logs_doc_group_id(doc_id, group_id, id)`
  - `ix_merge_decision_logs_doc_snapshot_id(doc_id, snapshot_version, id)`
- `20260314_0005_enforce_identity_lookup_uniqueness.py`:
  - `uq_user_identities_provider_lower_external_uid(lower(provider), lower(external_uid))`

互換性判定（2026-05-20時点）:

- **互換あり（backward-compatible）**
  - 読み取り経路へ影響しない index 追加。
  - `provider/external_uid` の case-insensitive uniqueness 強化（重複データがない前提）。
- **互換なし（backward-incompatible）**
  - 既存列の削除、必須化、意味変更は未実施。
  - `Document.version` の意味変更を伴う migration は未実施。
  - dry-run: `python -m kj_atlas_api.backfill_identity_refs --database-url <KJ_ATLAS_DATABASE_URL> --mapping-json mapping.json --dry-run`
  - apply: `python -m kj_atlas_api.backfill_identity_refs --database-url <KJ_ATLAS_DATABASE_URL> --mapping-json mapping.json`

属性境界（persist/transient/forbidden）:

- persist: `provider`, `external_uid`, `display_name`, `email`（最小）
- transient: `amr`, `acr`, `aal`, `auth_time`, `roles`, `groups`, `trace_id`
- forbidden: password/hash/secret, WebAuthn credential id, raw policy tokens

## Former CE1 v1 clarification（2026-05-03 / contract-only sync）

- `ContextQueryV1` / `ContextBundleV1` は CE1 の **closed-world最小契約** とする。
- `ContextBundleV1` の optional field は v1 では定義しない（required only）。
- 追加フィールド・列挙拡張・エラー語彙追加は **v2 契約改訂** でのみ許可する。
- エラー意味論の最小固定は `preview_required` / `unknown_contract_key` / `nondeterministic_bundle`。
- `invalid_query_contract` のような補助バリデーション語彙を導入する場合でも、上記最小固定語彙を置換してはならない。
- フォールバックは fail-open 禁止（fail-closed 固定）。

## Former §1.3 CE0 handoff frozen I/F（2026-05-04 / Stream B）

CE1 への受け渡し固定I/Fを次で成果物化する（contract-only / mock-first）。

- `ContextQueryV1`
- `ContextBundleV1`
- `ProposalPatchV1`
- `AuditEventV1`

mock contract明記:
- backend未実装でも、上記4型を契約正本として stub/fixture で検証可能とする。
- 実装差し替え時も key set / enum / error semantics を v1 互換で固定する。

Deprecateルール（v1固定）:
1. v1 必須キーの削除/改名/意味変更は deprecate 不可（禁止）。
2. 拡張は v2追加のみ許可し、v1 は read-only contract として保持する。
3. `preview_required` / `unknown_contract_key` / `nondeterministic_bundle` の語彙と判定条件は不変。

## Former CE Contract Freeze Addendum（2026-05-04 / minimal delta）

### Context
- CE1/CE2/CE4 の並行進行で契約ドリフトを防ぐため、4型の責務境界を固定する。

### Decision
- SSOT対象を `ContextQueryV1` / `ContextBundleV1` / `ProposalPatchV1` / `AuditEventV1` に固定。
- v1では unknown key reject（closed-world）を維持し、契約の拡張は v2 でのみ扱う。
- mock-first 前提として `A1-CONTRACT-MOCK-v1` を契約検証入力に許可し、実装依存を持ち込まない。

### Consequences
- 下流は interface-only で先行でき、backend/frontend の完了待機を不要化できる。
- 契約変更要求は CDC再承認が必須となり、無断拡張を防止できる。

## Former Stream B Contract Annotation（Phase 2/3 alignment）

### Context
- CE系契約は実装前に type/signature を固定し、mock payload で下流連携を維持する必要がある。
- A系契約IDの一部は確定待ちがありうるため、参照は conditional を許可する。

### Decision
- v1契約は closed-world を維持し、必須キーとエラー語彙（`preview_required` / `unknown_contract_key` / `nondeterministic_bundle`）を固定する。
- mock payload 例（`A2-minimal-v1`）を正規の検証入力として扱い、実装値を契約へ持ち込まない。
- conditional 参照中の契約IDは再定義せず、確定時に参照更新のみ実施する。

### Consequences
- CE2/CE4 は backend未完了でも契約テストを継続できる。
- 状態遷移（`unreviewed -> human_reviewed` の人手限定）と safeMode 境界の侵害を schema 検証で早期検出できる。
- 互換性判断は v1固定を基準に fail-closed で統一される。

## Former §1.3 Stream A contract freeze manifest（2026-05-07）

Contract Freeze と最小I/F合意の固定マニフェスト（read-only handoff）。

```yaml
hil_rs_a1_manifest_v1:
  freezeContractId: HIL-RS-02-A1-CONTRACT-FREEZE-v1
  schemaVersion: "1.0.0"
  overridePolicy: human_dual_control_only
  safeModeDefault: ON
  safeModeBoundary: SAFE_MODE_STRICT_ON
  contractIds:
    - A1-CRITIQUE-IF
    - A1-REDIFF-IF
    - A1-ATTR-IF
    - A1-ERROR-IF
  immutable_scope:
    - api_signature
    - major_data_types
    - compatibility_semantics
  extensible_scope:
    - v2_additive_fields_only
    - additional_audit_metadata
  decisionQueueTransition:
    - Pending->Approved
    - Pending->Rejected
  gate:
    a2a3_open_allowed: "a1Status==Done && pendingDecisionQueueCount==0"
    otherwise: Hold
```

## Former §1.2.1 CE1 freeze confirmation update（2026-05-07 / Stream B）

- Context contracts are frozen as v1 (`CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`) and remain mock-first.
- Required `ContextQueryV1` key set is fixed to:
  - `goal/scope/depth/constraints/reviewFilter/safeModePolicy/outputMode/previewConfirmed`
- Required `ContextBundleV1` key set is fixed to:
  - `queryCanonicalHash/bundleHash/selected/relations/evidence/contradictions/reviewFlags/truncationMeta/excludedReason`
- Error semantics are frozen in v1:
  - `422 preview_required`
  - `400 unknown_contract_key`
  - `409 nondeterministic_bundle`
- Verify gate is frozen as `sameQuery && sameBundle`; mismatch is fail-closed and self-repair is capped at max 3.
- Conflict-safe rule: agreement missing / dependency contradiction / collision detected => `held` and stop for instruction.

## Former §10.4 Stream E freeze note (2026-05-10)

- Contract freeze: `users` / `user_identities` 分離、strict時 `identity_not_provisioned`、admin provisioning 導線を AUTH 系の最小互換契約として固定。
- Compatibility rule: 判定必須キーは `status/code/provisioned` の3点を保持し、将来拡張は後方互換（追加のみ・既存キー意味変更禁止）で行う。
- Audit boundary: identity 生値（`provider/external_uid/email`）は監査最小項目へ保存しない。

## Former CE1 Contract Freeze Memo（2026-05-17 / Stream B）

- Contract IDs固定: `CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`。
- Error vocabulary固定: `preview_required` / `unknown_contract_key` / `nondeterministic_bundle`。
- `ContextQueryV1` / `ContextBundleV1` の v1 必須キー集合は closed-world（追加は v2 のみ）。
- Mock-first: `stubDatasetId=A2-minimal-v1` の契約検証のみ許可（実DB/実LLM/worker 禁止）。
- Proceed条件: CE2/CE4 は `sourceBundleHash` 参照整合を read-only で受け取る。

## Former CE1 Stream C handoff lock（2026-05-17 / interface-first）

- `ContextQueryV1` / `ContextBundleV1` の v1 必須キー集合は固定（closed-world; v2まで追加禁止）。
- Error semantics は `422 preview_required` / `400 unknown_contract_key` / `409 nondeterministic_bundle` の3種固定。
- roundtrip contract test は `A2-minimal-v1` で実施し、同一 canonical query 3回の `queryCanonicalHash` / `bundleHash` 一致を合格条件とする。
- CE2/CE4 handoff は read-only で `sourceBundleHash === bundleHash` を比較可能であることのみを要件とし、実装依存（DB/LLM/worker）を含めない。
- Verify失敗時 self-correction は最大3回。超過時は `held` 停止を必須とする。

## Former §11 Stream D execution log (2026-05-19)

Phase直列実行（Read必須）で Data Contract & Model Ops を確認した。

1. Contract drift抽出: `DATA-CONTRACT-01` の観点（frontend/backend/api/schema）で `DocumentV2` 契約差分を再確認し、`version gate` 優先の fail-closed を維持。
2. Support level定義: `L1/L1.5/L2/L2.5/L3/L0` の語彙を本書の正本として再固定。新規フィールドは未分類なら `L2.5` 扱い。
3. CRUD境界更新（参照）: 個別CRUDの可否は `02_Architecture/data_model_operations_overview.html` の表を正本とし、本書は型契約に限定。
4. Admin maintenance/recovery境界更新（参照）: 管理・復旧の実装可否は `DATA-MAINT-01` で管理し、契約変更を先行条件に据える。
5. Verify: `schemas.md` / `schemas_review_attribution.md` / `02_Architecture/data_model_operations_overview.html` 間で support level 語彙と責務分離の矛盾がないことを確認。

## Former §12 Stream D reaffirmation (2026-05-19)

### Context
- `DocumentV2` には実装済み項目と契約先行項目が混在しており、型定義のみで運用CRUD保証と誤読されるリスクがある。

### Decision
- `L1/L1.5/L2/L2.5/L3/L0` を support level の唯一語彙として維持し、新規フィールドは未分類のまま導入しない。
- `PUT /docs/{doc_id}` create-if-absent をMVPの標準Create契約として維持し、`POST /docs` はversion gate導入まで契約候補（L0）に据え置く。

### Consequences
- 後方互換判定を version gate 基準で統一でき、feature flag による暫定互換運用を抑止できる。
- `02_Architecture/data_model_operations_overview.html` / `schemas_review_attribution.md` / `issue-DATA-CONTRACT-01` と同一語彙で運用責務境界を同期できる。

## Former §13 Stream B contract lock sync (2026-05-20)

### Context
- `DocumentV2` の support level と backward compatibility 判定が、契約文書と運用境界文書で同時に固定されていない場合、実装側で「型=運用保証」と誤読される。

### Decision
- `DocumentV2` support level は `L1/L1.5/L2/L2.5/L3/L0` を唯一語彙として維持し、未分類フィールドは `L2.5` 扱いを継続する。
- backward compatibility は `version gate` 優先で固定し、`version: 2` の破壊的変更（必須化/意味変更/削除）は `version: 3` 以降でのみ許可する。
- CE1/CE2/CE4 連携I/Fは read-only contract（`queryCanonicalHash` / `bundleHash` / `sourceBundleHash`）として扱い、DB/API依存実装を混在させない。

### Consequences
- Stream B から下流への引き渡しは mock-first で再現可能になり、実装進捗待ちなしで契約検証を継続できる。
- CRUD保証の主張は `02_Architecture/data_model_operations_overview.html` 側に限定され、契約文書単体の誤読リスクを抑制できる。
