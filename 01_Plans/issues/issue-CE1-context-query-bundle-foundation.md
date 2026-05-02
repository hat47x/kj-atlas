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
