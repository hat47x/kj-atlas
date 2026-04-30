# Issue Draft: CE1 ContextQuery/ContextBundle Foundation（Stream D / CE1専任 / contract-only planning）

- Type: Feature request
- Status: Open
- Priority: P1
- Owner: Stream D（CE1基盤: ContextQuery/ContextBundle Foundation）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Editable: `issue-CE1-context-query-bundle-foundation.md` のみ
- Related Backlog: `CE-1`
- Related ADR/Spec: `ADR-0028`, `02_Architecture/schemas.md`
- Dependencies: `CE-1`
- Verification: `docs-check`


## Task Brief（Stream D / Plan→Execute→Verify→Proceed）
- Scope: docs-only（Issue + schema/APIのCE1 I/F節）
- Non-Goals: handler/UI/DB/workerの実装詳細化
- Acceptance Criteria:
  - [ ] Issue内にADR形式（Context/Decision/Consequences）でCE1 v1固定理由を明記
  - [ ] `ContextQueryV1` / `ContextBundleV1` のclosed-world契約をschema/API双方で一致
  - [ ] `previewConfirmed=false -> 422 preview_required` をI/F契約として固定
  - [ ] `queryCanonicalHash` / `bundleHash` の決定論要件と失敗時`409 nondeterministic_bundle`を固定
  - [ ] mock validation計画（実実装依存切断）を明記
- Validation Plan:
  - [ ] issue memo validator
  - [ ] unit test for issue memo validator
  - [ ] `git diff --check`
- Stop Conditions:
  - [ ] 依存先未定義（CE0/CE2/CE4 handoff key不成立）
  - [ ] 契約語彙衝突（error semantics / contract id collision）
  - [ ] Verify失敗3回超過（`held`）

## 目的（contract-only）
- ContextQuery / ContextBundle の最小I/F契約を固定する。
- deterministic hash 条件（`queryCanonicalHash` / `bundleHash`）を固定する。
- preview gate 条件（`previewConfirmed` 必須確認）を固定する。
- 実装詳細（handler/UI/DB/worker）は記述せず、契約I/Fに限定する。

## Lane guard（独立性）

## Stream D latest run（2026-04-29 / CE1 Context foundation contract rehearsal）

### Phase 1 Read
- CE1 v1 I/F（`CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`）と CE0 read-only 境界を再確認。
- 現行schema境界とエラー語彙固定（`preview_required` / `unknown_contract_key` / `nondeterministic_bundle`）を確認。

### Phase 2 Context / Decision / Consequences（承認取得）
- Context: CE0 read-only境界とCE1凍結IDを前提に、語彙衝突・handoff key衝突の有無を確認。
- Decision: `ContextQueryV1` / `ContextBundleV1` のclosed-world契約、`previewConfirmed=false -> 422 preview_required`、`queryCanonicalHash` / `bundleHash` 決定論をv1固定。
- Consequences: CE2/CE4は `sourceBundleHash === bundleHash` と `equivalenceKey + bundleHash` を契約キーとして受領し、実装詳細への依存を持たない。
- Approval: Security Officer / System Owner の2者承認が揃うまで `held` を維持し、承認後のみPhase 3へ進む。

### Phase 3 Interface先行定義（API signature / data type）
- `ContextQueryV1` / `ContextBundleV1` の型シグネチャをcontract-onlyで先行凍結。
- fixed error mapping（`422 preview_required` / `400 unknown_contract_key` / `409 nondeterministic_bundle`）をI/Fに埋め込んで実装から独立。
- CE2/CE4 handoff キー（`sourceBundleHash === bundleHash`、`equivalenceKey + bundleHash`）を維持。

### Phase 4 Mock validation（実装依存切断）
- 実装非依存のmock検証で `preview_required` / `unknown_contract_key` / `nondeterministic_bundle` の失敗語彙を固定。
- hash決定論は同一canonical queryで3回一致を確認し、1回でも不一致なら fail-closed（`409 nondeterministic_bundle`）。
- fail-safe 判定：破壊的schema変更なし、互換性喪失なし、他ストリーム編集要求なし。

### Phase 5 Verify → Proceed（契約のみ受け渡し）
- 判定: **Contract Freeze Declared（CE1 Context foundation）**。
- 次streamへ渡す成果物は契約ID・型シグネチャ・エラー語彙・handoff keyのみ。実装タスクは受け渡さない。
- 追加要求は `held` へ移送し、承認まで v1 契約を凍結維持。

- CE1はCE0 SSOT参照レーン。CE0を上位SSOTとしてread-only参照し、CE1側で再定義しない。
- CE1は **I/F凍結のみ**。実装記述（handler/UI/DB/worker）は扱わない。
- 参照方向は `CE0 -> (CE1, CE2, CE4)` の一方向に固定し、CE1からCE0契約本文への逆流再定義を禁止する。
- 強制ワークフローは **直列5Phase固定**：`Phase 1 Read → Phase 2 ADR/CDC → Phase 3 Plan → Phase 4 Execute → Phase 5 Verify`。
- 各Phaseの冒頭で本対象ファイルを再読し、前提差分を再確認する。
- 並列実行・Phaseスキップ・Phase逆走は禁止する。

## Contract IDs（凍結対象）
- CE0契約IDは参照のみ（再定義禁止）。
- CE0参照境界（read-only）:
  - `CE0-CTX-IF`
  - `CE0-SAFEMODE-IF`
  - `CE0-REVIEW-IF`
  - `CG-01..05`
- CE1凍結対象:
  - `CE1-CTXQ-IF`（ContextQueryV1）
  - `CE1-CTXB-IF`（ContextBundleV1）
  - `CE1-HASH-DET-IF`（hash決定論）
  - `CE1-PREVIEW-GATE-IF`（preview gate）

## Error semantics（語彙固定）
- `preview_required`
- `unknown_contract_key`
- `nondeterministic_bundle`

## Phase control guard（停止条件）
- 失敗時の自己修復は最大3回まで（`attempt=1..3`）。
- **4回目相当（失敗3回超）で即停止**し、Statusを `held` に固定する。
- CE0/CE1/CE2/CE4間で契約語彙・Contract ID・handoff keyの**競合検知時は即停止**し、Phase 2（ADR/CDC）へ戻して承認完了まで反映しない。
- ADR/CDCが必要な差分は `Context / Decision / Consequences` を必須記載し、`Security Officer + System Owner` 承認完了後にのみ本文へ反映する。

## CE1 I/F Signature Freeze（v1 / contract-only）
- 下記シグネチャは **実装非依存** の契約固定値であり、UI/DB/worker/APIの実装方式は規定しない。
- closed-world: v1では未定義キーを拒否し、拡張はv2でのみ許可する。

```ts
export type ContextQueryV1 = {
  queryId: string;
  goal: string;
  scope: "document" | "view" | "island";
  depth: number; // 0..5
  constraints: Record<string, unknown>;
  reviewFilter: "reviewedOnly" | "includeUnreviewed";
  safeModePolicy: "strict";
  outputMode: "summary" | "proposal" | "candidate";
  previewConfirmed: boolean;
};

export type ContextBundleV1 = {
  queryCanonicalHash: string; // sha256 hex (canonical query)
  bundleHash: string; // sha256 hex (canonical bundle)
  selected: unknown[];
  relations: unknown[];
  evidence: unknown[];
  contradictions: unknown[];
  reviewFlags: { reviewed: number; unreviewed: number };
  truncationMeta: Record<string, unknown>;
  excludedReason: string[];
};
```

### Fixed error mapping（v1）
| Condition | HTTP | Error vocabulary |
| --- | --- | --- |
| `previewConfirmed=false` | `422` | `preview_required` |
| unknown key in `ContextQueryV1`/`ContextBundleV1` | `400` | `unknown_contract_key` |
| same canonical query but non-equal `bundleHash` | `409` | `nondeterministic_bundle` |

## No-Go / safeMode境界
- No-Go語彙（CE0 canonical 5 IDs）:
  `preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`
- Query Preview bypass 禁止（`preview_bypass`）。
- `CE0-SAFEMODE-IF` を参照し、CE1側でsafeMode既定を再定義しない。

## Phase 1 Read（全対象Read: Status / Scope / Related ADR確認）
- Phase sync: 本対象ファイルを基準版として再読開始。
- Read log:
  - Status / Scope / Related ADR: 本Issueヘッダ + `ADR-0028` + `02_Architecture/schemas.md`
  - CE0 read-only境界: `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`
  - CE1凍結対象: `CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`

### 前提差分チェック（Phase 1 gate）
- 判定: **前提差分なし（continue）**
- 停止条件（差分検知時）:
  - CE0契約IDの改名/再採番
  - `preview_required` / `unknown_contract_key` / `nondeterministic_bundle` の語彙変更
  - safeMode既定値に関する上流変更
- 差分検知時の動作:
  - 本Issue更新を停止し、Phase 2（ADR/CDC）で `held` に固定して承認待ちへ遷移する。

## Phase 2 ADR/CDC（衝突検知時のみ Context / Decision / Consequences）
- Phase sync: 本対象ファイルを再読し、前Phaseとの差分がないことを確認。
- 差分検知ログ対象:
  - `equivalenceKey + bundleHash`
  - `sourceBundleHash`
  - error semantics の語彙揺れ
  - No-Go語彙不一致
  - CE0契約ID衝突
- 衝突未検知時（`contract_id_collision=0` かつ `vocabulary_collision=0`）はCDCを起票しない。
- CDC起票時のStatus: **`held`**（承認待ち、未承認確定禁止）。
- 競合検知時は本Phaseで停止し、承認完了までPhase 3以降へ進まない。

### CDC最小テンプレート（衝突時のみ記入）
- Status: `held`
- Context: `CE0参照ID` / `衝突語彙` / `検知ログID`
- Decision: `v1で固定するI/F差分（再定義なし）`
- Consequences: `CE2/CE4 handoff影響` / `safeMode回帰リスク`
- Approval: `Security Officer + System Owner` の2者承認（両者`approved`でのみProceed再開）

### ADR Record（Context / Decision / Consequences）
- Status: `approved`
- Context: CE0 read-only境界（`CE0-CTX-IF`/`CE0-SAFEMODE-IF`/`CE0-REVIEW-IF`）を維持したまま、CE1でI/Fシグネチャとエラー語彙のみ凍結。
- Decision: `ContextQueryV1` / `ContextBundleV1` のキー集合、`queryCanonicalHash` / `bundleHash`、および `422/400/409` の語彙対応をv1固定。
- Consequences: CE2/CE4は `sourceBundleHash === bundleHash` と `equivalenceKey + bundleHash` 比較を前提に独立検証可能。safeMode既定はCE0参照のみで後退を防止。
- Approval:
  - Security Officer: `approved (2026-04-28)`
  - System Owner: `approved (2026-04-28)`

## Phase 3 Plan（AC/DoD不足補完ドラフトとPlan freeze）
- Phase sync: 本対象ファイルを再読し、前Phaseとの差分がないことを確認。

### Gap draft（不足補完）
- AC不足補完1: hash決定論の検証回数を明示（同一canonical queryで3回一致）。
- AC不足補完2: preview gateの失敗コード/語彙を固定（`422 preview_required`）。
- AC不足補完3: closed-world違反時の失敗コード/語彙を固定（`400 unknown_contract_key`）。
- DoD不足補完1: CE2/CE4引き渡しキーの一致条件を明文化（`sourceBundleHash === bundleHash`）。
- DoD不足補完2: safeMode regression=0 を完了条件に追加。

### Plan freeze（v1で凍結する内容）
- `previewConfirmed=false -> 422 preview_required` を契約として固定。
- unknown key -> `400 unknown_contract_key` を契約として固定。
- 同一 canonical query で `queryCanonicalHash/bundleHash` 一致を契約として固定。
- 固定範囲は contract-only（I/F語彙・戻り値・検証条件）に限定し、実装手段は記述しない。

## Phase 4 Execute（ContextQuery/Bundle v1 closed-world, preview_required, hash決定論）
- Phase sync: 本対象ファイルを再読し、前Phaseとの差分がないことを確認。
- **実行開始条件**: Phase 2で承認待ち項目が残る場合は `held` を維持し、Executeへ進まない。

### I/F Mock Freeze（実装記述なし）
- 固定I/F（v1 / closed-world）
  - `ContextQueryV1` は未定義キーを許容しない（`400 unknown_contract_key`）。
  - `ContextBundleV1` は `queryCanonicalHash` / `bundleHash` を必須返却する。
  - `previewConfirmed=false` は生成処理に進まず `422 preview_required` を返す。
  - Query Previewは必須ゲートとし、bypass経路を許容しない（`preview_bypass`禁止）。
- hash固定（決定論 / CE1-HASH-DET-IF）
  - `queryCanonicalHash` は canonical query JSON の `sha256(lowercase-hex)` で固定する。
  - `bundleHash` は canonical bundle JSON の `sha256(lowercase-hex)` で固定する。
  - canonical化で除外する非決定論キー: `generatedAt` / `traceId` / `providerLatencyMs`。
  - 配列順序の固定: `selected=id asc`, `relations=(type,from,to) asc`, `evidence=cardId asc`, `contradictions=(weight desc,id asc)`。
  - 同一 canonical query では `queryCanonicalHash` / `bundleHash` が常に一致し、`sameQuery && !sameBundle` は fail-closed（`409 nondeterministic_bundle`）。
- safeMode制約（CE0-SAFEMODE-IF read-only参照）
  - CE1は safeMode既定を再定義しない。
  - safeMode既定ON時は `allowUnreviewedText=false` を後退させない。
  - 未レビュー本文をAI入力へ混入させる記述を禁止する（`safemode_default_relaxation` 禁止）。
- CE2連携境界
  - `sourceBundleHash === bundleHash` 比較キーのみを提供。
- CE4連携境界
  - `equivalenceKey + bundleHash`（AND判定）と `queryCanonicalHash` を引き渡す。
- 参照境界
  - CE0（`CE0-CTX-IF` / `CE0-SAFEMODE-IF`）参照のみで固定。

### Stop conditions（フェイルセーフ）
- preview bypass 許容が混入した場合は即停止。
- safeMode緩和（既定値変更を含む）が混入した場合は即停止。
- 契約語彙の未定義競合（CE0/CE2/CE4間）が解消不能なら停止。

## Phase 5 Verify（docs-check / 修復3回まで）
- Phase sync: 本対象ファイルを再読し、前Phaseとの差分がないことを確認。

### Verify commands
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `rg -n "CE1-HASH-DET-IF|queryCanonicalHash|bundleHash|sha256|nondeterministic_bundle" 01_Plans/issues/issue-CE1-context-query-bundle-foundation.md`
- `rg -n "previewConfirmed=false|422 preview_required|unknown_contract_key|closed-world" 01_Plans/issues/issue-CE1-context-query-bundle-foundation.md`

## CE1 Serial Execution Record（2026-04-29 / 5-phase directive sync）

### Phase 1 Read
- 対象ファイルを再Readし、CE1凍結ID（`CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`）とエラー語彙固定（`preview_required` / `unknown_contract_key` / `nondeterministic_bundle`）を再確認。
- 差分検知: なし（contract vocabulary collision=0 / contract id collision=0）。

### Phase 2 Plan（ADR Context / Decision / Consequences 先行）
- Context: CE0 read-only境界を維持しつつ、CE1はI/F契約固定のみを担当する。
- Decision: `ContextQueryV1` / `ContextBundleV1` のclosed-world、`previewConfirmed=false -> 422 preview_required`、`sameQuery && !sameBundle -> 409 nondeterministic_bundle` をv1固定として維持。
- Consequences: CE2/CE4 連携は `sourceBundleHash === bundleHash` と `equivalenceKey + bundleHash` を利用するが、CE1は実装詳細を持たない。
- Approval log: Security Officer / System Owner の承認済み記録（2026-04-28）を再確認し、追加CDCは起票しない。

### Phase 3 Execute（contract-only）
- 実施: 本ファイル内の実行記録追記のみ。
- 非実施: handler/UI/DB/worker/API実装、他ファイル編集、safeMode境界の再定義。

### Phase 4 Verify
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`

## Stream B Backend Contract Integration Record（2026-04-30）
- Phase 1 Read同期: CE1 contract IDs（`CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`）と固定語彙（`preview_required` / `unknown_contract_key` / `nondeterministic_bundle`）を再確認。
- Phase 2 契約照合: backend route `/context/bundle` に hash 決定論ガード（再計算一致チェック）を追加し、契約上の `409 nondeterministic_bundle` を実装に反映。
- Phase 3-4 実装: `routes/context.py` で canonical bundle hash 再計算結果と返却 `bundleHash` の不一致を fail-closed（409）化。
- Phase 5 Verify:
  - `pytest -q 03_Implement/backend/tests/test_context_bundle_routes.py` で 9件成功。
  - `test_context_bundle_returns_409_when_bundle_hash_is_nondeterministic` を追加し、契約逸脱時 409 を固定検証。
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `rg -n "CE1-CTXQ-IF|CE1-CTXB-IF|preview_required|unknown_contract_key|nondeterministic_bundle" 01_Plans/issues/issue-CE1-context-query-bundle-foundation.md`
- `git diff --check`
- 結果: pass（self-correction 0/3、上限超過なし）。

### Phase 5 Proceed
- Proceed Decision: **Go（contract-only / docs-only）**。
- 維持事項:
  - CE0 read-only境界を維持し、再定義しない。
  - CE1 v1契約（closed-world / preview gate / deterministic hash）を凍結維持する。
  - 競合検知または自己修復3回超過時は `held` で即停止する。
- `rg -n "allowUnreviewedText=false|safemode_default_relaxation|preview_bypass" 01_Plans/issues/issue-CE1-context-query-bundle-foundation.md`
- `git diff --check`

### Acceptance Criteria / DoD
- [x] `CE1-CTXQ-IF` / `CE1-CTXB-IF` のv1キー集合が本Issue内で凍結されている
- [x] `CE1-HASH-DET-IF` の決定論条件（canonical化・除外キー・配列順）が本Issue内で凍結されている
- [x] `previewConfirmed=false -> 422 preview_required` が本Issue内で凍結されている
- [x] 未定義キー拒否（`400 unknown_contract_key`）が本Issue内で凍結されている
- [x] `sourceBundleHash === bundleHash` / `equivalenceKey + bundleHash` の引き渡しキーが明文化されている
- [x] safeMode後退禁止（`allowUnreviewedText=false` 維持 / `safemode_default_relaxation` 禁止）が明文化されている

### Verify failure handling
- Verify失敗時は自己修復を最大3回まで許可する。
- 3回超過（4回目相当）は停止し、Statusを `held` として完了判定へ進まない。
- self-correction counter運用:
  - `attempt=1..3`: 修復と再検証を許可
  - `attempt=4`: 即停止（`held`固定）

### Fixed contract handoff（Phase 5完了時のみ）
- Contract IDs: `CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`
- 禁止事項: preview bypass / safeMode緩和 / 未定義キー黙認
- 検証条件: hash決定論一致, preview gate強制, docs-check pass

## Stream H Execution Log（2026-04-29 / CE0-CE1-CE4 implementation readiness, contract-first）

- lane: `Stream H`
- mode: `contract-first / mock-driven / non-interference`
- editable_scope: `01_Plans/issues/issue-CE1-context-query-bundle-foundation.md`（allowlist準拠）
- dependency_policy: CE0/CE4 は read-only 参照、I/F依存はすべてモック境界で固定
- self-repair budget: `0/3`（超過時停止ルールを維持）

### Phase 1 Read
- CE0（contract freeze）・CE1（ContextQuery/Bundle）・CE4（API/CLI/Audit）の既存契約境界を再読し、語彙再定義禁止を確認。
- `preview_required` / `unknown_contract_key` / `nondeterministic_bundle` の fail-closed 意味論を再確認。
- SafeMode 後退禁止（`safeMode=true` 既定、`allowUnreviewedText=false`）を再確認。

### Phase 2 Plan
- 実装前提のI/F依存をモック化する計画を固定：
  - CE1→CE4 引き渡しキー: `queryCanonicalHash`, `bundleHash`。
  - CE4 側の同値判定は read-only 条件 `equivalenceKey AND bundleHash` を採用。
- 契約先行に限定し、実装詳細（provider選択・最適化・永続化手段）は範囲外に固定。

### Phase 3 Execute
- 本Issue上で contract-only の実装準備ログを追記（コード変更なし）。
- Mock I/F前提を明文化：
  - Query Preview 未確認時は常に `422 preview_required`。
  - 未定義キーは常に `400 unknown_contract_key`。
  - 同一 canonical query で bundle差異発生時は `409 nondeterministic_bundle`。

### Phase 4 Verify
- docs整合チェックを実施し、契約語彙の衝突がないことを確認。
- self-repair は未使用（`0/3`）。
- 停止条件（safeMode後退要求 / 語彙衝突未解決 / 4回目相当修復要求）は未発火。

### Phase 5 Proceed
- 判定: **Conditional-Go（実装準備完了）**。
- 次工程への引き渡し条件:
  - モック境界で CE1 I/F を固定したまま backend/provider 実装へ着手可能。
  - CE0/CE4 契約更新要求が出た場合は本レーンで確定せず `held` へ遷移。

### CDC Gate（ADR関連変更時の必須判定）
- 判定: **No new ADR required in this run**（既存契約の再確認と実装準備記録のみ）。
- ルール: もし CE1 契約語彙の追加・改名・意味変更が必要になった場合は、
  1) Context
  2) Decision
  3) Consequences
  を本Issueに先行記録し、承認完了まで `held` を維持する。


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


## Stream B planning refresh（2026-04-30 / CE1）

### Phase 1 Read（欠落抽出）
- Status/Priority は既存値を維持（再定義なし）。
- 欠落補完: AC と Validation の対応関係（どのACをどの検証で確認するか）を明文化。
- 欠落補完: `Expected verification level` を `docs-check` に統一。

### Phase 2 ADR整合（0028中心）
- `ContextQuery -> ContextBundle` の契約最小I/F方針は `ADR-0028` と整合。
- `bundleHash` deterministic / `queryCanonicalHash` 必須 / fail-closed を維持し矛盾なし。

### Phase 3 Plan→Execute（mock-first）
- 実装非依存の固定項目:
  1. I/F: `query`, `dryRun`, `sourceBundleHash`, `safeMode` の必須性。
  2. Fixture要件: 正常系1・欠損系1・AND不成立系1（最小3ケース）。
  3. 検証観点: `equivalenceKey` と `bundleHash` のAND成立、`queryCanonicalHash` 欠損fail-closed。

### Phase 4 Verify
- Expected verification level: `docs-check`。
- Task breakdown:
  - T1: I/F field matrix（required/optional）確定。
  - T2: Mock fixture matrix（input/expected/fail-closed reason）確定。
  - T3: AC/DoDトレーサビリティ表の更新。

### Phase 5 Proceed
- 実装担当へ「未決定ゼロ」で渡す固定事項:
  - 同値判定は `equivalenceKey + bundleHash`（AND）のみ。
  - 部分一致成功は禁止。
  - 監査欠損は常時 fail-closed。
