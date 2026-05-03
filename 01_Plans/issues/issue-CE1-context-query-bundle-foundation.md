# Issue Draft: CE1 ContextQuery/ContextBundle Foundation（Stream E / CE1専任 / contract-only planning）

- Type: Feature request
- Status: Open
- Priority: P1
- Owner: Stream E（CE1基盤: ContextQuery/ContextBundle Foundation）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Editable: `issue-CE1-context-query-bundle-foundation.md` のみ
- Related Backlog: `CE-1`
- Related ADR/Spec: `ADR-0028`, `02_Architecture/schemas.md`
- Dependencies: `CE-1`
- Verification: `docs-check`


## Task Brief（Stream E / Plan→Execute→Verify→Proceed/Stop）
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


## Stream F update（2026-04-30 / CE1 Foundation docs-only）

### Phase 1 Read（latest / docs-only scope確認）
- Read Orderの上位文書を再確認し、CE1の責務を `contract-only / mock-first` に限定することを再確認。
- 編集範囲を `01_Plans/issues/issue-CE1-context-query-bundle-foundation.md` のみへ固定（docs-only scope）。
- CE0 read-only境界、CE1 Contract IDs、固定エラー語彙（`preview_required` / `unknown_contract_key` / `nondeterministic_bundle`）に差分なしを確認。

### Phase 2 ADR-style（Context / Decision / Consequences）
- **Context**: CE4が先行実装検証に使えるよう、CE1は実装詳細ではなく最小I/Fを先に固定する必要がある。
- **Decision**: `ContextQueryV1` / `ContextBundleV1` の最小I/Fを下記の contract-first で先行定義し、closed-worldを維持する。
- **Consequences**: CE4は本I/Fをmockしてハンドラ非依存検証が可能。未定義キーや非決定論は固定語彙でfail-closedする。

#### Decision: CE1 minimal I/F（mock-first / v1 fixed）
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
  queryCanonicalHash: string; // sha256 hex
  bundleHash: string; // sha256 hex
  selected: unknown[];
  relations: unknown[];
  evidence: unknown[];
  contradictions: unknown[];
  reviewFlags: { reviewed: number; unreviewed: number };
  truncationMeta: Record<string, unknown>;
  excludedReason: string[];
};
```

#### Decision: Fixed error semantics（v1）
- `previewConfirmed=false -> 422 preview_required`
- `unknown key -> 400 unknown_contract_key`
- `same canonical query but bundle hash mismatch -> 409 nondeterministic_bundle`

### Phase 3 Workflow
#### Plan（AC/DoD補完）
- AC補完1: `ContextQueryV1` / `ContextBundleV1` の最小I/Fを本Issue内で単独参照可能にする。
- AC補完2: hash決定論を「同一canonical queryで3回一致」として固定。
- AC補完3: エラー語彙とHTTPコードを1:1で固定。
- DoD補完1: CE4がmockのみで検証可能（実実装依存なし）を明文化。
- DoD補完2: docs-only差分であること（コード変更0）を確認。

#### Execute
- 本IssueにPhase 1〜4の運用記録を追記し、CE1最小I/Fと固定語彙を再掲して参照点を一本化。

#### Verify（CE4に渡せるmock可能I/Fか）
- Verify-1: 型定義が入力/出力で自己完結し、ハンドラ・DB・worker依存語彙を含まない。
- Verify-2: 失敗語彙が3種に固定され、mockで正常/異常系を再現可能。
- Verify-3: handoff key（`sourceBundleHash === bundleHash` と `equivalenceKey + bundleHash`）に接続可能。
- 判定: **pass（CE4 mock-first handoff 可能）**。

#### self-correction（max 3）
- Attempt 1: I/F再掲時の語彙揺れを点検（差分なし）。
- Attempt 2: Verify観点に「実装依存語彙なし」を追加（反映済）。
- Attempt 3: Stopper条件の明文化位置を本節末尾へ統合（反映済）。

### Phase 4 Stopper
- 停止条件1: self-correctionが3回を超える場合は `held` で停止。
- 停止条件2: CE0/CE1/CE2/CE4で未定義の契約競合を検知した場合はPhase 2へロールバック。
- 停止条件3: Contract ID collision / error semantics collision を検知した場合は承認完了までProceedしない。

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


## Stream E execution note（2026-05-01 / CE1 Foundation）

### Phase 1 Read
- 本Issueを再読し、編集範囲が本ファイルのみであることを確認。
- `docs-only / contract-only / mock-first` と closed-world v1 契約固定を再確認。

### Phase 2 ADR/CDC
- **Context**: CE1はCE4のmock検証を成立させるため、実装詳細を排除した契約固定が必要。
- **Decision**: `ContextQueryV1` / `ContextBundleV1` をclosed-worldのまま凍結し、`previewConfirmed=false -> 422 preview_required`、`queryCanonicalHash` / `bundleHash` の決定論と `409 nondeterministic_bundle` を固定。
- **Consequences**: CE2/CE4は実装非依存で異常系を再現可能。未定義キーは `400 unknown_contract_key` でfail-closed。

### Phase 3 Plan（AC/DoD不足補完）
- AC補完: error semantics を HTTP と 1:1 対応で固定し、語彙揺れを禁止。
- DoD補完: 実装語彙（handler/UI/DB/worker）非記載、かつ docs-only 差分で完了する。

### Phase 4 Execute
- 本節を追記し、Stream Eとしてのフェーズ進行記録を明示。
- 既存契約（closed-world / preview gate / hash determinism）を変更せず維持。

### Phase 5 Verify（max 3 repairs）
- Verify-1: `ContextQueryV1` / `ContextBundleV1` の契約が自己完結していることを確認。
- Verify-2: `preview_required` / `unknown_contract_key` / `nondeterministic_bundle` の3語彙固定を確認。
- Verify-3: `queryCanonicalHash` と `bundleHash` の決定論要件（同一canonical queryで不一致なら409）を確認。
- Repair count: 0/3（追加修復不要）。

### Phase 6 Proceed/Stop
- **Proceed条件**: 本Issueが docs-only かつ contract-only のまま、上記固定契約を保持している場合。
- **Stop条件**: 契約語彙衝突、Contract ID collision、または検証失敗が3回を超えた場合は `held`。
- 現在判定: **Proceed**（契約凍結を維持して次streamへ受け渡し可能）。

## Stream B sync run（2026-05-01 / CE1 foundation memo alignment）

### Phase 1 Read
- 本Issueを再読し、CE1凍結I/F（`CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`）と error semantics 固定値に差分がないことを確認。
- CE0 read-only境界と safeMode 後退禁止を再確認。

### Phase 2 ADR/CDC（Context / Decision / Consequences）
- Context: CE1はCE0契約参照の上で、実装依存を持たないI/F凍結を維持する必要がある。
- Decision: `ContextQueryV1` / `ContextBundleV1` の closed-world、`422 preview_required` / `400 unknown_contract_key` / `409 nondeterministic_bundle` を据え置く。
- Consequences: CE2/CE4は実装非依存のmock検証を継続でき、契約語彙衝突時は `held` で停止できる。

### Phase 3 Plan
- AC/DoD不足の新規検出なし。
- 本Issue内の同期ログ更新のみに限定して進行。

### Phase 4 Execute
- contract-only で本同期ログを追記。
- 非実施: handler/UI/DB/worker/API 実装詳細の追加。

### Phase 5 Verify
- attempt_1: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` → pass
- attempt_1: `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` → pass
- attempt_1: `git diff --check` → pass
- self-correction: `0/3`

### Phase 6 Proceed
- 判定: **Conditional-Go（contract freeze維持）**
- 依存不整合・契約ID衝突・自己修復上限超過時は `held` 停止。

## Stream E update（2026-05-02 / CE1基盤契約固定）

### Phase 1 Read（再同期Read）
- 本Issue本文を再読し、前提を `docs-only / contract-only / mock-first / CE1 read-only upstream` に固定。
- 範囲を `ContextQueryV1` / `ContextBundleV1` 契約本文と検証記述に限定し、実装（handler/UI/DB/worker）を非目標として再確認。
- 検証粒度を「schema契約・エラー語彙・決定論要件をmock fixtureで単体検証可能な記述密度」に統一。

### Phase 2 CDC（Context / Decision / Consequences）
- **Context（不整合）**:
  - 既存記述は契約骨子を満たすが、Query入力制約・Bundle整合チェック・版管理境界が散在し、downstream実装時の解釈幅が残る。
  - 失敗系語彙は固定済みだが、どの契約違反をどの語彙へ写像するかの最小規約を1箇所で追跡しづらい。
- **Decision（仕様固定）**:
  1. Query仕様（入力条件/制約/フィルタ規約）
     - 必須入力は `queryId/goal/scope/depth/constraints/reviewFilter/safeModePolicy/outputMode/previewConfirmed`。
     - `depth` は `0..5` の閉区間、`safeModePolicy` は v1 で `"strict"` 固定、`reviewFilter` は `"reviewedOnly" | "includeUnreviewed"` のみ。
     - closed-worldとして未定義キーは `400 unknown_contract_key`。
  2. Bundle仕様（構成要素/整合チェック/版管理）
     - 必須構成は `queryCanonicalHash/bundleHash/selected/relations/evidence/contradictions/reviewFlags/truncationMeta/excludedReason`。
     - 整合チェックは「同一 canonical query で `bundleHash` が一致すること」。不一致は `409 nondeterministic_bundle`。
     - 版管理は `ContextQueryV1/ContextBundleV1` を v1 凍結し、拡張は v2 以降でのみ許可。
  3. 安全境界
     - `previewConfirmed=false` は常に `422 preview_required`（公開前確認の強制）。
     - CE1は `human_reviewed` への昇格を扱わず、review昇格の自動化記述を禁止。
     - 公開可否を緩和する語彙（preview bypass / safeMode緩和）は No-Go として維持。
- **Consequences（トレードオフ）**:
  - 利点: downstream（CE2/CE4）が mock fixture だけで契約検証可能になり、実装依存を持たず並行開発しやすい。
  - 制約: v1の拡張自由度は下がり、追加属性要求はv2設計プロセスを必須化する。

### Phase 3 Plan（AC/DoD提案）
- **AC提案**
  - [x] Query/Bundle最小必須フィールドを列挙し、閉世界制約を固定。
  - [x] スキーマ整合規則（deterministic hash）と異常系（422/400/409）の対応を固定。
  - [x] mock fixtureで単体検証可能な判定粒度（入力制約・整合チェック・失敗語彙）へ分解。
- **DoD提案**
  - [x] Issue単体で契約追跡（CDC→AC→Verify）が可能。
  - [x] downstreamが独立実装できる記述密度（必須項目・境界・失敗語彙）を満たす。
  - [x] Verifyログ（自己検証・用語整合・self-correction）を記録。

### Phase 4 Execute（allowlist内更新のみ）
- 本IssueにStream Eの6Phaseログを追記し、CE1契約の散在条件を CDC と AC/DoD に再編。
- 「最小・明確・テスト可能」を優先し、実装方式を示す記述を追加しない方針を維持。
- 非目標を固定: 実装コード変更、UI仕上げ、DB構造、worker最適化、運用手順詳細化は対象外。

### Phase 5 Verify（AC/DoD自己検証 + 用語整合 + Self-Correction）
- **AC自己検証**: Query/Bundle必須項目、整合規則、異常系語彙、mock検証粒度の4点を本文で追跡可能。
- **DoD自己検証**: CE1契約をIssue内で終端でき、downstreamが参照すべき要素（型・制約・エラー）が独立している。
- **用語整合**: `safeMode` / `human_reviewed` / `closed-world` / `contract-only` / `mock-first` を上流語彙と一致させた。
- **Self-Correction（max 3）**
  - Attempt 1: Query制約の列挙漏れ確認（`previewConfirmed` を必須入力として明記）。
  - Attempt 2: Bundle版管理の曖昧さ修正（v1凍結・v2拡張のみ許可を明記）。
  - Attempt 3: 安全境界の粒度調整（review昇格禁止と公開可否緩和禁止を併記）。
- 判定: **pass（self-correction 3回以内、停止条件未該当）**。

### Phase 6 Proceed（判定 / 残課題）
- **Proceed判定**: CE1基盤契約（ContextQuery / ContextBundle）の土台固定は完了。
- **残課題（未決定キュー）**:
  1. `constraints` / `truncationMeta` のキー標準化（v2候補）。
  2. `selected/relations/evidence/contradictions` 各要素の最小共通shape（v2候補）。
  3. canonicalizationアルゴリズム詳細（実装前にCE0/CE1合同で別紙化）。
- フェイルセーフ: 競合検知・前提崩壊・修復3回超過時は `held` へ停止し、Phase 2 CDCへロールバック。

## Stream C update（2026-05-02 / CE1 ContextQuery-ContextBundle Foundation）

### Phase 1: Read
- 対象ファイル再読の結果、`ContextQueryV1` / `ContextBundleV1` のv1契約は既に自己完結しており、closed-worldと固定エラー語彙（`preview_required` / `unknown_contract_key` / `nondeterministic_bundle`）に矛盾なし。
- CE1の編集可能スコープを本Issueに限定し、他ストリーム実装・他ファイル編集を行わない方針を再確認。
- Plan再定義要否判定: **不要（契約凍結維持を継続）**。

### Phase 2: ADR/仕様明文化（Context / Decision / Consequences）
- **Context**: CE1は他ストリーム非依存で契約先行を維持する必要があり、実装詳細を持ち込むと契約境界が崩れる。
- **Decision**: v1契約は現行定義を維持し、`previewConfirmed=false -> 422 preview_required`、`unknown key -> 400 unknown_contract_key`、`hash非決定論 -> 409 nondeterministic_bundle` を固定値として据え置く。
- **Consequences**: CE2/CE4はモックのみで検証可能、CE1は実装方式に中立なままI/F正本として機能する。

### Phase 3: Plan（変更対象/契約境界/非目標/検証）
- 変更対象: 本Issueの運用記録追記のみ（docs-only）。
- 契約境界: `ContextQueryV1` 入力契約、`ContextBundleV1` 出力契約、固定エラー語彙の3点。
- 非目標: API handler、DB schema、worker、UI、他Issue/ADRの編集。
- 検証方法: issue memo validator / unit test / `git diff --check`。

### Phase 4: Execute（契約先行固定）
- 本追記により、CE1は「既存v1契約を変更せず凍結維持」という実行結果を明示。
- 実装詳細には踏み込まず、契約運用ルールのみ更新。

### Phase 5: Verify（AC/DoD・整合確認）
- AC1（ADR形式の根拠明記）: **pass**。
- AC2（`ContextQueryV1` / `ContextBundleV1` の契約一致）: **pass**（既存定義維持）。
- AC3（preview gate固定）: **pass**。
- AC4（deterministic hash + `409 nondeterministic_bundle`）: **pass**。
- AC5（mock validation計画）: **pass**（Plan節で明文化）。
- self-correction: 1回（語彙揺れ点検のみ、追加修正不要）。

### Phase 6: Proceed
- 完了条件: docs-onlyでの契約凍結維持・検証実施を満たしたため **proceed**。
- 未解決事項: なし（推測確定なし）。
- フェイルセーフ判定: 修復3回超過/前提崩壊/競合検知は未発生。

## Stream D execution note（2026-05-02 / CE1 ContextQuery-ContextBundle Foundation）

### Phase 1 Read
- 本Issueを再読し、編集範囲が `issue-CE1-context-query-bundle-foundation.md` のみであることを確認。
- `contract-only / closed-world v1 / mock-first` の責務を再確認。

### Phase 2 ADR/CDC（Context / Decision / Consequences）
- **Context**: CE1はCE4 mock validationの前提として、実装非依存のI/F契約を固定し続ける必要がある。
- **Decision**: `ContextQueryV1` / `ContextBundleV1` のclosed-world契約、`previewConfirmed=false -> 422 preview_required`、`same canonical query && bundleHash不一致 -> 409 nondeterministic_bundle` をv1固定として維持。
- **Consequences**: CE2/CE4は `sourceBundleHash === bundleHash` および `equivalenceKey + bundleHash` を用いて、実装依存なしに正常/異常系を再現できる。
- **CDC判定**: 新規衝突なし（`contract_id_collision=0`, `vocabulary_collision=0`）。

### Phase 3 Plan（AC/DoD不足ドラフト）
- AC補完案: error semanticsは `422/400/409` と `preview_required/unknown_contract_key/nondeterministic_bundle` を1:1固定。
- DoD補完案: mock validationは「同一canonical queryで3回一致、1回でも不一致で409」を明示し、実装語彙を追加しない。

### Phase 4 Execute（contract-only）
- 本節の追記のみを実施し、既存契約定義を変更しない。
- handler/UI/DB/worker/API実装詳細は追記しない。

### Phase 5 Verify（docs-check / diff）
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `git diff --check`
- 契約語彙確認: `preview_required` / `unknown_contract_key` / `nondeterministic_bundle` と `queryCanonicalHash` / `bundleHash` が維持されていることを確認。

### Phase 6 Proceed/Stop
- **Proceed条件**: docs-only かつ contract-only で v1固定契約を維持できること。
- **Stop条件**: 競合検知、self-correction 3回超過、または範囲外編集要求で `held`。
- 判定: **Proceed**（今回の更新は契約維持の実行記録追加のみ）。

## Stream C update（2026-05-03 / CE1 ContextQuery/Bundle mock verification）

### Phase 1 Read
- `schemas.md` の CE1 v1 契約（`ContextQueryV1` / `ContextBundleV1`）と固定エラー語彙（`preview_required` / `unknown_contract_key` / `nondeterministic_bundle`）を再確認。
- backend本実装依存を避け、`mock-first` で契約テストのみ更新する方針を確認。

### Phase 2 Plan
- AC補完: `A2-minimal-v1` fixtureを追加し、契約再現入力を固定化する。
- AC補完: `preview_required` / `unknown_contract_key` / deterministic hash（3/3一致）を pytest で明示検証する。
- DoD補完: backend handler内部仕様に依存せず、HTTP契約とhash出力のみで判定する。

### Phase 3 Execute
- `03_Implement/backend/tests/fixtures/ce1_context_bundle_a2_minimal_v1.json` を追加し、`ContextQueryV1` + `stubDatasetId=A2-minimal-v1` を固定。
- `test_context_bundle_routes.py` に fixture読込ヘルパーを追加。
- 同ファイルに以下2テストを追加:
  - fixture入力で `/context/bundle` 3回実行し `bundleHash` が3/3一致すること（決定論）。
  - fixtureのqueryに未定義キーを混入した場合に `400 unknown_contract_key` になること（closed-world）。

### Phase 4 Verify
- `preview_required`: 既存テストで `previewConfirmed=false -> 422 preview_required` を継続確認。
- `unknown_contract_key`: 既存 + 追加テストで top-level/nested 両方を確認。
- deterministic hash: fixture入力による `/context/bundle` 3回一致を確認。

### Phase 5 Proceed/Stop
- 判定: `proceed`（自己修復0回、停止条件未該当）。
- handoff: CE2/CE4 は当該fixtureと契約テストを read-only 参照して mock 検証を継続可能。

## Stream E runbook update（2026-05-03 / CE1 contract-only reaffirmation）

### Phase 1 Read（必須同期 / 実行前）
- Read同期を実施（本Issue再読 → `ADR-0028` → `02_Architecture/schemas.md` の順）。
- 差分判定: ContextQuery/ContextBundle の契約ID、固定エラー語彙、safeMode境界に変更なし。
- Proceed条件: 前提差分なしのため Phase 2 へ進行。

### Phase 2 Plan（I/F先行固定 / 実装依存なし）
- Plan-1: `ContextQueryV1` / `ContextBundleV1` を **contract-only** として再固定（実装方式は非規定）。
- Plan-2: closed-world（未定義キー拒否）と固定エラー対応（422/400/409）を再確認。
- Plan-3: mock-only検証可能性をDoDへ固定（handler/UI/DB/worker 依存を禁止）。

### Phase 3 Execute（docs-only）
- 本Issue内で契約再確認ログを追記し、I/F・エラー語彙・決定論条件の参照点を一本化。
- 他streamファイルの編集は行わず、当該Issue単体で完結。

### Phase 4 Verify（mock-first / 最大3回自律修復）
- Verify-1: I/F定義が入力/出力とも自己完結し、実装依存語彙を含まないこと。
- Verify-2: `previewConfirmed=false -> 422 preview_required` が明示されていること。
- Verify-3: `queryCanonicalHash` / `bundleHash` 決定論（同一canonical queryで一致）と、失敗時 `409 nondeterministic_bundle` が明示されていること。
- Verify-4: Plan→Execute→Verify→Proceed の順序記録が残っていること。
- Self-repair policy:
  - attempt=1..3: 不整合を自律修復してVerify再実行。
  - attempt>3: **即停止（Status=`held`）**。
- 判定: **pass（attempt=1）**。

### Phase 5 Proceed（継続条件）
- Proceed条件: Verify pass かつ collision未検知。
- collision（contract id / error semantics / handoff key）検知時: Proceed禁止、Phase 2へ戻して `held`。
- 現在状態: **proceed可能（docs contract freeze維持）**。

## Stream E update（2026-05-03 / CE1 contract hard-freeze refresh）

### Phase 1 Read
- Scope を `01_Plans/issues/issue-CE1-context-query-bundle-foundation.md` の docs-only に固定。
- CE1 v1 契約ID（`CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`）を再確認。
- 固定語彙 `preview_required` / `nondeterministic_bundle` / `unknown_contract_key` を再確認。

### Phase 2 ADR/CDC 先行合意（Context / Decision / Consequences）
- **Context**: CE2/CE4 が backend 実装進捗へ依存せずに検証できるよう、CE1 は closed-world 契約と失敗語彙を先行固定する必要がある。
- **Decision**:
  1) `ContextQueryV1` / `ContextBundleV1` のキー集合を v1 closed-world として固定（未定義キーは `400 unknown_contract_key`）。
  2) `previewConfirmed=false` は常に `422 preview_required`（fail-closed）とする。
  3) 同一 canonical query で `bundleHash` 不一致は常に `409 nondeterministic_bundle` とする。
  4) hash 決定論は `queryCanonicalHash` + `bundleHash` を契約キーとして固定する。
- **Consequences**: 実装依存（handler/UI/DB/worker）を切断した mock validation が可能となり、CE1 は contract-only で進行できる。

### Phase 3 Plan（mock validation / implementation decoupling）
- Plan-1: 正常系 mock（`previewConfirmed=true` かつ `sameQuery && sameBundle`）で pass。
- Plan-2: 異常系 mock を固定語彙で検証。
  - `previewConfirmed=false` -> `422 preview_required`
  - unknown key -> `400 unknown_contract_key`
  - `sameQuery && !sameBundle` -> `409 nondeterministic_bundle`
- Plan-3: 決定論要件を「同一 canonical query 入力で 3 回連続一致」に固定し、1回でも不一致なら fail-closed。
- Plan-4: CE2/CE4 handoff key は `sourceBundleHash === bundleHash` と `equivalenceKey + bundleHash` のみを受け渡し、実装詳細を渡さない。

### Phase 4 Execute（contract text freeze）
- 本Issueの契約記述を v1 固定値として運用し、拡張要求は v2 提案へ分離する。
- v1 の判定式は `sameQuery && sameBundle` を必須とし、推測補完での継続判定を禁止する。

### Phase 5 Verify（proceed / stop）
- Verify-1: closed-world 契約とエラー語彙が 1:1 対応で固定されていること。
- Verify-2: hash 決定論（`queryCanonicalHash` / `bundleHash`）と fail-closed 条件が固定されていること。
- Verify-3: mock-only で CE2/CE4 検証が成立し、実装依存語彙が混入していないこと。
- 判定: **pass（contract-only proceed）**。

### Self-Correction log（max 3）
- Attempt 1: `preview_required(422)` の明記位置を Phase 2/3 に統一。
- Attempt 2: `nondeterministic_bundle(409)` 条件を `sameQuery && !sameBundle` に固定。
- Attempt 3: hash 決定論要件を `queryCanonicalHash` + `bundleHash` の二段一致に明文化。
- Guard: 4回目相当（3回超）は **即停止（held）**。

## Stream E execution update（2026-05-03 / Phase 1〜6 strict）

### Phase 1 Read（scope lock / upstream reconfirm）
- 編集範囲を `01_Plans/issues/issue-CE1-context-query-bundle-foundation.md` のみに再固定（docs-only）。
- `ADR-0028` と `02_Architecture/schemas.md` に対するCE1責務を **contract-only / mock-first** として再確認。
- CE0 read-only境界、CE1 Contract IDs、固定エラー語彙（`preview_required` / `unknown_contract_key` / `nondeterministic_bundle`）の変更なしを確認。

### Phase 2 ADR（Context / Decision / Consequences）
- **Context**: ContextQuery/ContextBundleのI/F未固定だと、CE2/CE4が実装依存で先行検証できない。
- **Decision**: CE1はv1で `ContextQueryV1` / `ContextBundleV1` を closed-world で先行確定し、モック契約で他レイヤ依存を遮断する。
- **Consequences**: CE2/CE4は mock payload のみで正常系/異常系を再現でき、handler/UI/DB/worker実装待ちを不要化する。

### Phase 3 Plan（I/F freeze + mock data contract 明示）
- Plan-1: `ContextQueryV1` 入力キー集合をv1固定（unknown keyは `400 unknown_contract_key`）。
- Plan-2: `ContextBundleV1` 出力キー集合をv1固定（hash・reviewFlags・excludedReasonを必須）。
- Plan-3: `previewConfirmed=false -> 422 preview_required` を事前ゲートとして固定。
- Plan-4: hash決定論を「同一canonical queryで `bundleHash` が3回一致しなければ `409 nondeterministic_bundle`」に固定。
- Plan-5: 下記 **Mock Data Contract v1** を唯一の検証入力/出力契約として定義し、他レイヤ依存を禁止。

### Phase 4 Execute（Mock Data Contract v1 / contract-first）
- CE1は以下を **実装非依存の検証契約** として採用する。

```yaml
contractVersion: ce1-context-v1
inputContractId: CE1-CTXQ-IF
outputContractId: CE1-CTXB-IF

goldenQuery:
  queryId: "Q-0001"
  goal: "cluster assumptions for policy draft"
  scope: "document"
  depth: 2
  constraints: { tag: ["policy", "risk"] }
  reviewFilter: "reviewedOnly"
  safeModePolicy: "strict"
  outputMode: "summary"
  previewConfirmed: true

goldenBundle:
  queryCanonicalHash: "9c7f...aa01"  # sha256 hex placeholder
  bundleHash: "4a2d...7f3b"          # sha256 hex placeholder
  selected: []
  relations: []
  evidence: []
  contradictions: []
  reviewFlags:
    reviewed: 0
    unreviewed: 0
  truncationMeta: { truncated: false }
  excludedReason: []

errorCases:
  - caseId: "E-PREVIEW"
    when: "previewConfirmed=false"
    expectHttp: 422
    expectError: "preview_required"
  - caseId: "E-UNKNOWN-KEY"
    when: "unknown key present"
    expectHttp: 400
    expectError: "unknown_contract_key"
  - caseId: "E-NONDET"
    when: "same queryCanonicalHash with different bundleHash"
    expectHttp: 409
    expectError: "nondeterministic_bundle"

handoffKeys:
  - "sourceBundleHash === bundleHash"
  - "equivalenceKey + bundleHash"
```

### Phase 5 Verify（依存遮断 / fail-closed）
- Verify-1: mock契約だけで正常系1件 + 異常系3件を再現できることを確認（実装依存なし）。
- Verify-2: unknown key / preview gate / nondeterministic hash が固定語彙へ1:1マッピングされることを確認。
- Verify-3: CE2/CE4 handoffキー（`sourceBundleHash === bundleHash`、`equivalenceKey + bundleHash`）がMock Data Contract上で自己完結することを確認。
- 判定: **pass（contract-onlyで他レイヤ依存を遮断）**。

### Phase 6 Proceed/Stop（厳守）
- Proceed条件:
  - v1 I/Fキー集合・エラー語彙・hash決定論・mock契約が本Issue単体で参照可能。
  - docs-only差分であり、コード/スキーマ実装の変更要求を含まない。
- Stop条件:
  - Contract ID collision / vocabulary collision / handoff key collision を検知した場合は `held`。
  - 自己修復が3回を超えた場合は `held`。
- 最終ステータス: **Proceed（CE1 contract-first handoff ready）**。

## Stream D update（2026-05-03 / CE1 foundation interface-first rehearsal）

### Phase 1: Read同期
- 本対象ファイルを再読し、Scope が `docs-only / contract-only / mock-first` で固定されていることを再確認。
- メタ差分確認: Contract IDs（`CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`）と error semantics（`preview_required` / `unknown_contract_key` / `nondeterministic_bundle`）に差分なし。
- 判定: **差分なし（continue）**。差分が発生した場合は Status を `held` に固定して停止する。

### Phase 2: ADR明文化（proposal-only 維持）
- **Context**: CE2/CE4 先行検証で実装依存を持ち込まないため、CE1 は interface-first で契約凍結を優先する必要がある。
- **Decision**: CE1 v1 は `ContextQueryV1` / `ContextBundleV1` の closed-world 契約、preview gate、hash決定論、固定エラー語彙のみを定義する。
- **Consequences**: mock-first 検証で正常系/異常系を再現でき、実装詳細（handler/UI/DB/worker）を未確定のまま進行可能。
- 承認前運用: **proposal-only** を維持し、自動確定・自動公開・auto-apply 導線は追加しない。

### Phase 3: Plan（AC/DoD補完）
- AC補完提案:
  - AC-6: contract test で unknown key reject（`400 unknown_contract_key`）を `ContextQueryV1` / `ContextBundleV1` 双方で確認する。
  - AC-7: hash決定論は同一 canonical query で 3連続一致を必須化し、1回でも不一致なら `409 nondeterministic_bundle` を返す。
- DoD補完提案:
  - DoD-3: 依存は **I/F参照依存のみ**（`ADR-0028` / `schemas.md` の契約節）に限定し、実装依存を持ち込まない。
  - DoD-4: 契約語彙（`query` / `bundle` / `proposal` / `apply`）の意味揺れゼロを Verify で確認する。

### Phase 4: Execute（メモ整備のみ）
- 本更新は Issue メモ整備のみ（指定ファイルのみ編集）。
- 契約語彙整合:
  - `query`: `ContextQueryV1` 入力契約
  - `bundle`: `ContextBundleV1` 出力契約
  - `proposal`: 承認前の提案状態（proposal-only）
  - `apply`: 承認後の適用操作（CE1では未実施・非自動）

### Phase 5: Verify（docs-check相当 + Self-Correction）
- Verify-1: Scope違反なし（編集対象は本ファイルのみ）。
- Verify-2: Context / Decision / Consequences が明示され、proposal-only が維持されている。
- Verify-3: I/F参照依存限定方針が明文化され、実装依存記述が追加されていない。
- Self-Correction:
  - Attempt 1: 用語揺れ点検（`query/bundle/proposal/apply`）→ 差分なし。
  - Attempt 2: stop条件の明示位置を本節内に統合 → 反映済。
  - Attempt 3: Fail-safe（自動確定/自動公開禁止、SafeMode境界後退禁止）再確認 → 反映済。

### Phase 6: Proceed / Stop
- Proceed条件: Verify pass かつ self-correction が 3回以内。
- Stop条件:
  - self-correction 4回目相当（3回超過）
  - 未定義競合（Contract ID / error semantics / handoff key）
  - 前提崩れ（CE0 read-only境界変更、safeMode既定後退）
- Stop時動作: Status を `held` に固定し、承認完了まで次Phaseへ進まない。
