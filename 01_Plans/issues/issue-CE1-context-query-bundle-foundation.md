# Issue Draft: CE1 ContextQuery/ContextBundle Foundation（Stream E / CE1専任 / contract-only planning）

- Type: Feature request
- Status: Open
- Priority: P1
- Owner: Stream E（CE1基盤: ContextQuery/ContextBundle Foundation）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Editable: `issue-CE1-context-query-bundle-foundation.md` のみ
- Related Backlog: `CE-1`
- Related ADR/Spec: `ADR-0028`, `02_Architecture/schemas.md`
- Dependencies: `01_Plans/issues/issue-CE0-contract-freeze.md`（契約依存; ContextBundle payloadはmockで先行可能）
- Verification: `docs-check`
- Dependency meta: `blockers=none; depends_on=CE0-contract-freeze,FB-P2C-01-a1-interface-contract; unlocks=CE2-low-risk-ai-assist,CE4-api-cli-audit-integration`


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




## Stream C update（2026-05-06 / CE1 ContextQuery/ContextBundle Foundation 専任）

### Phase 1 Read（対象ファイル再読: I/F・hash決定論・preview gate）
- 本issueを再読し、`ContextQueryV1` / `ContextBundleV1` のclosed-world契約を再確認。
- hash決定論要件を `queryCanonicalHash` / `bundleHash` の同一canonical query 3回一致で再確認。
- preview gateを `previewConfirmed=false -> 422 preview_required` として再確認。
- 編集範囲を本ファイルのみに固定し、CE2/CE4・backend/frontend・他issue非編集を確認。

### Phase 2 ADR C/D/C（実装前の明文化・承認）
- **Context**: CE2/CE4がCE1未実装でもmockのみで前進するため、CE1はI/F契約とエラー語彙を先行凍結する必要がある。
- **Decision**: `ContextQueryV1` / `ContextBundleV1`、`preview_required` / `unknown_contract_key` / `nondeterministic_bundle`、およびhash決定論失敗時`409`をv1固定する。
- **Consequences**: 下流は契約ID・型・語彙だけでmock検証を継続でき、実装依存の待機が不要になる。
- 承認ゲート: Contract collision検知時は本文反映を停止し `held` で承認待ちに遷移する。

### Phase 3 Plan → Execute → Verify → Proceed
#### Plan（AC/DoD不足の補完提案）
- AC追加提案1: CE2向けに `sourceBundleHash === bundleHash` を検証可能な最小フィールドセットをDoDへ固定。
- AC追加提案2: CE4向けに `equivalenceKey + bundleHash` の監査再現キー接続性をDoDへ固定。
- DoD追加提案: handoff成果物を「Contract IDs / 型 / error semantics / hash rule / handoff keys」のみとし、実装TODOを含めない。

#### Execute（contract-only整備）
- `ContextQueryV1` / `ContextBundleV1` をv1固定契約として維持（unknown keyは `400 unknown_contract_key`）。
- error semanticsを以下で固定:
  - `422 preview_required`
  - `400 unknown_contract_key`
  - `409 nondeterministic_bundle`
- mock-first handoffを明文化し、CE2/CE4が実装なしで検証継続できる受け渡し単位を固定。

#### Verify（CE2/CE4がmockのみで前進可能か）
- Verify-1 (CE2): `sourceBundleHash === bundleHash` 比較のみで入力整合性確認が可能。
- Verify-2 (CE4): `equivalenceKey + bundleHash` で再現監査キーを構成可能。
- Verify-3 (共通): 正常系/異常系（3固定語彙）をmockだけで再現可能。
- 結果: **pass**（CE2/CE4ともmock-onlyでProceed可能）。

#### self-repair log（失敗時最大3回）
- attempt 1: 契約語彙揺れ点検（差分なし）。
- attempt 2: handoff keyのDoD表記を統一（反映済）。
- attempt 3: Verify観点をCE2/CE4別に分離（反映済）。

### Phase 4 Stopper
- Stopper-1: self-repairが3回超過した場合は即時 `held` 停止。
- Stopper-2: contract collision（Contract ID / error semantics / handoff key衝突）検知時は即時停止してPhase 2へロールバック。
- Stopper-3: scope逸脱要求（CE2/CE4/backend/frontend/他issue編集）が発生した場合は作業停止し、本issueへの追記のみ維持。

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

## Stream D update（2026-05-03 / CE1 ContextQuery-ContextBundle Foundation）

### Phase 1: Read & Sync
- Read対象: 本issue, `02_Architecture/schemas.md` CE1節, `02_Architecture/api.md` CE1節, `02_Architecture/llm_input_ir_spec.md` CE1接続節。
- 事前想定との差分:
  - 既存文書はすでに CE1 v1 の closed-world 契約を固定済み（`ContextQueryV1` / `ContextBundleV1`）。
  - エラー語彙は `preview_required` / `unknown_contract_key` / `nondeterministic_bundle` で一致。
  - API側に `invalid_query_contract` が併記されているため、v1最小固定語彙との差分は「補助バリデーション語彙」であることを明示する必要がある。
- 重大不一致判定: なし（継続）。

### Phase 2: ADR/契約明文化ゲート（Context / Decision / Consequences）
- Context:
  - CE1は CE2/CE4 の mock-first 検証を成立させるため、実装詳細ではなく I/F 契約を先に凍結する必要がある。
- Decision（v1最小固定）:
  1. 入出力型:
     - 入力: `ContextQueryV1`（必須 `previewConfirmed=true`、unknown key reject）
     - 出力: `ContextBundleV1`（必須 `queryCanonicalHash` / `bundleHash`）
  2. ContextBundle構造:
     - 必須: `queryCanonicalHash`, `bundleHash`, `selected`, `relations`, `evidence`, `contradictions`, `reviewFlags`, `truncationMeta`, `excludedReason`
     - 任意: なし（v1は closed-world、拡張は v2 のみ）
     - versioning: `v1` は破壊変更禁止、追加は `v2` でのみ許可
  3. エラー/フォールバック:
     - `422 preview_required`（preview gate違反）
     - `400 unknown_contract_key`（未定義キー）
     - `409 nondeterministic_bundle`（同一canonical queryで bundleHash 不一致）
     - フォールバックは fail-open禁止、fail-closed を固定
- Consequences:
  - CE2/CE4 は backend 実装待ちなしで mock 検証可能。
  - 実装依存は契約依存から分離され、変更要求は CE1再起票へ集約される。
- Approval gate:
  - 本更新時点では「契約ゲート承認待ち（held可能）」を許容し、承認前に実装仕様を追加しない。

### Phase 3: Plan（AC / DoD / 依存分離）
- Acceptance Criteria（確定）:
  - [x] Context/Decision/Consequences で CE1最小契約を明文化
  - [x] `ContextQueryV1` 入出力契約と `ContextBundleV1` 構造を required/optional で明示
  - [x] versioning 方針（v1凍結、v2拡張）を明示
  - [x] error semantics と fail-closed を固定
  - [x] 契約依存と実装依存を分離し、mock-first を明示
- DoD（CE1 docs-only）:
  - [x] schemas/api/issue の CE1語彙が同一
  - [x] コード変更なし（docs-only）
  - [x] CE2/CE4 handoff用固定契約キーを明示
- Dependency split:
  - 契約依存: `ContextQueryV1`, `ContextBundleV1`, hash規則, error語彙
  - 実装依存: handler/DB/worker/LLM runtime（本issueの非対象）

### Phase 4: Execute
- 実施内容:
  - issue内に CE1最小契約の再固定を追記。
  - schemas/api 側の CE1節に「v1最小固定」「補助エラー語彙」「versioning」を同期。
- Non-goals（再確認）:
  - handler/UI/DB/worker 実装の追加記述は行わない。

### Phase 5: Verify
- AC/DoD自己検証: pass
- 用語整合チェック: `ContextQuery` / `ContextBundle` の表記揺れなし
- Self-correction count: 1/3（`invalid_query_contract` の位置づけ注記を追加）

### Phase 6: Proceed
- 完了判定: **CE1 contract docs update 完了（docs-only）**
- 未解決事項:
  - `invalid_query_contract` を v1補助語彙として維持するか、将来v2で統合するかの最終承認
- 次ストリーム引継ぎ（固定契約 / mock仕様）:
  - 固定契約: `ContextQueryV1`, `ContextBundleV1`, `queryCanonicalHash`, `bundleHash`
  - mock仕様: `A2-minimal-v1` + `422/400/409` 固定エラー検証

## Stream E run（2026-05-04 / contract-first refresh for mock decoupling）

### Phase 1: 現状分析（Read同期）
- Read同期を実施し、本Issue・`ADR-0028`・`02_Architecture/schemas.md` 参照前提で CE1 の責務が **contract-only / mock-first / closed-world** であることを再確認。
- ContextQuery 入力要素として `queryId` / `goal` / `scope` / `depth(0..5)` / `constraints` / `reviewFilter` / `safeModePolicy=strict` / `outputMode` / `previewConfirmed` を抽出。
- ContextBundle 出力要素として `queryCanonicalHash` / `bundleHash` / `selected` / `relations` / `evidence` / `contradictions` / `reviewFlags` / `truncationMeta` / `excludedReason` を抽出。
- 制約は closed-world（未知キー拒否）・決定論hash（同一canonical queryで同一bundleHash）・preview gate（`previewConfirmed=false` 拒否）・safeMode統治（strict固定, bypass禁止）。

### Phase 2: ADR-style 明文化（Context / Decision / Consequences）
**Context**
- CE2/CE4 が実装未確定状態でも前進するには、ContextQuery/ContextBundle の契約を先行凍結し mock で依存切断する必要がある。
- 契約語彙の揺れは handoff key 衝突を誘発するため、Error semantics と hash 規則を固定する必要がある。

**Decision**
- `CE1-CTXQ-IF` と `CE1-CTXB-IF` を v1 固定として採用し、unknown key は fail-closed（`400 unknown_contract_key`）。
- preview gate を必須化し、`previewConfirmed=false` は常に `422 preview_required`。
- bundle 生成の決定論規則を固定:
  1. Query canonicalization を先に実行し `queryCanonicalHash(sha256 hex)` を算出。
  2. canonical query を入力に bundle を構成し canonical bundle representation を生成。
  3. canonical bundle representation から `bundleHash(sha256 hex)` を算出。
  4. 同一canonical queryで `bundleHash` が不一致の場合は `409 nondeterministic_bundle`。
- safeMode除外規則を固定:
  - `safeModePolicy` は v1 で `"strict"` のみ許可。
  - `excludedReason` には safeMode 由来の除外理由を記録するが、bypass（`preview_bypass` 等 No-Go語彙）は許可しない。

**Consequences**
- CE2/CE4 は API/DB/worker 実装を待たず mock 入出力で検証を開始できる。
- 失敗語彙が固定されるため、監査・diff・再実行時の判定が安定する。
- v1 で拡張が必要な場合は v2 契約として扱い、v1 へ後方互換破壊を持ち込まない。

### Phase 3: インターフェース定義（signature / type / error / audit）
#### ContextQueryV1（入力）
- 必須:
  - `queryId: string`
  - `goal: string`
  - `scope: "document" | "view" | "island"`
  - `depth: number`（0..5）
  - `constraints: Record<string, unknown>`
  - `reviewFilter: "reviewedOnly" | "includeUnreviewed"`
  - `safeModePolicy: "strict"`
  - `outputMode: "summary" | "proposal" | "candidate"`
  - `previewConfirmed: boolean`
- 任意: なし（v1 closed-world）

#### ContextBundleV1（出力）
- 必須:
  - `queryCanonicalHash: string`（sha256 hex）
  - `bundleHash: string`（sha256 hex）
  - `selected: unknown[]`
  - `relations: unknown[]`
  - `evidence: unknown[]`
  - `contradictions: unknown[]`
  - `reviewFlags: { reviewed: number; unreviewed: number }`
  - `truncationMeta: Record<string, unknown>`
  - `excludedReason: string[]`
- 任意: なし（v1 closed-world）

#### Error code / semantics（固定）
- `422 preview_required`: `previewConfirmed=false`
- `400 unknown_contract_key`: ContextQueryV1/ContextBundleV1 の未定義キー検知
- `409 nondeterministic_bundle`: 同一canonical queryで`bundleHash`不一致

#### 監査属性（audit attributes）
- 監査最小属性:
  - `queryId`
  - `queryCanonicalHash`
  - `bundleHash`
  - `reviewFilter`
  - `safeModePolicy`
  - `previewConfirmed`
  - `excludedReason[]`
  - `errorVocabulary`（正常時は空、異常時は上記固定語彙）
- 監査要件: 同一query再実行時に hash・excludedReason・errorVocabulary の差分可視化を可能にする。

#### preview確認フロー（仕様）
1. Query受領時に contract key validation（closed-world）を先行。
2. `previewConfirmed` を評価し、`false` の場合は処理中断して `422 preview_required`。
3. `true` の場合のみ canonicalization / bundle生成へ進む。
4. 完了時に audit attributes を出力し、後続 stream が diff 可能な形式で保持する。

### Phase 4: mock-first 検証計画（実装依存切断）
- Scenario A: 同一query再現性
  - 同一 `ContextQueryV1` を3回投入。
  - 期待値: `queryCanonicalHash` と `bundleHash` が3回一致。
  - 不一致時: `409 nondeterministic_bundle` を返す。
- Scenario B: safeMode除外ルール
  - `safeModePolicy="strict"` 下で除外対象データを含む入力を模擬。
  - 期待値: bypassせず `excludedReason[]` に理由を記録。
  - No-Go語彙（`preview_bypass` 等）が出力・受理されないこと。
- Scenario C: preview gate
  - `previewConfirmed=false` を投入。
  - 期待値: 常に `422 preview_required`、bundle生成未実行。
- Scenario D: unknown key
  - v1未定義キーを投入。
  - 期待値: `400 unknown_contract_key`。
- Scenario E: diff/audit 出力
  - 正常系と異常系の監査属性を比較し、`queryCanonicalHash` / `bundleHash` / `excludedReason` / `errorVocabulary` が差分トレース可能。

### Phase 5: Verify / Stop
#### AC/DoDチェック
- [x] ADR-style（Context/Decision/Consequences）を本Issue内に明文化。
- [x] `ContextQueryV1` / `ContextBundleV1` の closed-world 契約を固定。
- [x] `previewConfirmed=false -> 422 preview_required` を固定。
- [x] `queryCanonicalHash` / `bundleHash` 決定論と `409 nondeterministic_bundle` を固定。
- [x] mock-first 検証シナリオを定義し、実装依存を切断。

#### Proceed判定
- 判定: **Proceed（contract-onlyで次streamへ受け渡し可能）**。
- 受け渡し対象: 契約型、決定論規則、previewフロー、固定エラー語彙、監査属性。

#### Stop条件評価
- 依存未確定箇所（CE0/CE2/CE4 handoff key）: 現時点で新規競合検知なし。
- 契約語彙衝突: 新規衝突なし。
- Self-Correction上限: 未到達（0/3）。
- 致命条件: なし。

## Stream E update（2026-05-04 / CE1 contract freeze mock-first, implementation-decoupled）

### Phase 1 Read
- Scopeを `01_Plans/issues/issue-CE1-context-query-bundle-foundation.md` のみに再固定（docs-only）。
- CE1の責務を **ContextQueryV1/ContextBundleV1 のI/F先行固定** に限定し、実装手順（handler/UI/DB/worker）は別タスク扱いで本Issueから分離。
- CE0 read-only境界と固定語彙（`preview_required` / `unknown_contract_key` / `nondeterministic_bundle`）の継続を確認。

### Phase 2 ADR/CDC
- **Context**: CE2/CE4がbackend実装待ちで停滞しないよう、CE1はmock-firstで契約を先に凍結する必要がある。
- **Decision**: `ContextQueryV1` / `ContextBundleV1` のキー集合・エラー語彙・hash決定論を v1で固定し、実装依存を切断する。
- **Consequences**:
  - 下流は `sourceBundleHash === bundleHash` と `equivalenceKey + bundleHash` をmockで検証継続できる。
  - 追加キー/語彙はv1へ混在させず、後方互換を壊さない形でv2に隔離する。
  - 承認未了の確定化要求は `held` で停止する。

### Phase 3 Plan
- AC-1: `ContextQueryV1` / `ContextBundleV1` を **contract-first** で固定（実装手順は記載しない）。
- AC-2: Verify項目を `I/F固定キー一致` `後方互換条件` `safeMode後退なし` に限定して明文化。
- AC-3: mock validationを正常系+異常系（`preview_required` / `unknown_contract_key` / `nondeterministic_bundle`）で再現可能に固定。

### Phase 4 Execute
- v1 closed-worldを継続固定（未定義キーは `400 unknown_contract_key`）。
- preview gateを継続固定（`previewConfirmed=false -> 422 preview_required`）。
- hash決定論を継続固定（同一canonical queryで3回一致、失敗時 `409 nondeterministic_bundle` fail-closed）。
- 実装依存切断を明示（本Issueでは実装順序・実装方式・運用手順を確定しない）。

### Phase 5 Verify
- Verify-1（I/F固定キー一致）: `queryCanonicalHash` / `bundleHash` / `sourceBundleHash` / `equivalenceKey` の引き渡しキー整合を維持。
- Verify-2（後方互換条件）: v1キー集合・固定エラー語彙・Contract IDsに変更なし（互換破壊なし）。
- Verify-3（safeMode後退なし）: `safeModePolicy: "strict"` を維持し、share/export既定安全境界を弱める記述を追加しない。
- 判定: **pass（contract freeze維持、mock-first継続可能）**。

### Phase 6 Proceed
- Handoff（契約のみ）:
  - Contract IDs: `CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`
  - I/F keys: `queryCanonicalHash` / `bundleHash` / `sourceBundleHash` / `equivalenceKey`
  - Error semantics: `preview_required` / `unknown_contract_key` / `nondeterministic_bundle`
- Implementation sequencingは別Issue/別ADRで扱い、本Issueでは扱わない（依存切断を維持）。

### Stop conditions（再掲）
- 失敗3回超過（4回目相当）で `held` 停止。
- 未承認の確定化要求（Security Officer / System Owner の承認不成立）で `held`。
- 未定義競合（Contract ID / error semantics / handoff key collision）検知時は即停止し、Phase 2へ戻す。

## Stream E latest run（2026-05-04 / CE1 contract I/F hardening）

### Phase 1 Read同期
- 対象3Issueを再読し、A1契約参照・safeMode既定ON・Core Graph proposal-onlyを再確認。

### Phase 2 Plan（AC/DoD明確化）
- AC追加: CE0/CE1契約境界明示、A2/A3参照導線、ContextQuery/Bundleの契約I/F固定。
- DoD追加: 未承認事項確定ゼロ、依存リンク切れゼロ、契約ID/エラー語彙固定。

### Phase 3 Execute（文書更新）
- `ContextQueryV1` / `ContextBundleV1` を implementation-agnostic contract として明記。
- A2はstub/mockで先行検証可、A3は同一契約ID・同一語彙を維持して接続する前提を明文化。
- Core Graph更新は proposal-only、CE1からの直接反映を禁止する注記を追加。

### Phase 4 Verify
- 用語一致（queryCanonicalHash/bundleHash、preview_required、unknown_contract_key、nondeterministic_bundle）を3Issue横断確認。
- 契約ID・依存リンク・停止条件を確認し、欠落なし（self-fix 0/3）。

### Phase 5 Proceed（Stream B/C handoff）
- 固定I/F一覧: `ContextQueryV1` keyset, `ContextBundleV1` keyset, hash/equivalence前提。
- 禁止事項一覧: unknown key許容、preview bypass、non-deterministic bundle、consensus direct write。
- 検証前提: mock-first A2先行、A3接続時は fail-closed / held 運用を継続。

## Stream C update（2026-05-04 / CE1最小I/F契約固定 / contract-only）

### Phase 1 Read Sync
- 対象を `issue-CE1-context-query-bundle-foundation.md` のみに限定し、他ファイル非編集を再確認。
- 既存凍結契約 `CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF` を再読。
- fail-safe 停止条件（未定義競合 / 非対象編集要求 / self-correction>3）を再確認。

### Phase 2 ADR
- **Context**: CE2/CE4 が CE1 実装待ちで停止しないよう、CE1 は最小I/F・hash決定論・preview gate を contract-only で先に固定する必要がある。
- **Decision**:
  - `ContextQueryV1` / `ContextBundleV1` は v1 closed-world（unknown key は拒否）を維持。
  - `previewConfirmed=false -> 422 preview_required` を入力ゲートとして固定。
  - `queryCanonicalHash` / `bundleHash` は同一 canonical query で3回一致を必須化し、不一致は `409 nondeterministic_bundle` で fail-closed。
- **Consequences**:
  - CE2 は `sourceBundleHash === bundleHash` のみで mock 検証を継続可能。
  - CE4 は `equivalenceKey + bundleHash`（AND）で監査再現性を担保可能。
  - backend/frontend/worker 実装詳細への依存を持ち込まない。

### Phase 3 Plan（AC/DoD不足補完）
- AC補完:
  1. v1キー集合の閉域性（closed-world）を固定。
  2. preview gate のコード/語彙対応（422/`preview_required`）を固定。
  3. hash決定論（3回一致）と不一致時の 409/`nondeterministic_bundle` を固定。
- DoD補完:
  1. CE2/CE4 は CE1未実装でも mock 契約で検証継続可能。
  2. 引き渡し成果物は契約ID・型・エラー語彙・handoff key のみ。
  3. 実装タスク（handler/UI/DB/worker）を本Issueに含めない。

### Phase 4 Execute（closed-world key / error semantics 固定）
- 固定キー契約:
  - `ContextQueryV1` / `ContextBundleV1` は未定義キーを許可しない（`400 unknown_contract_key`）。
- 固定エラー意味論:
  - `422 preview_required`
  - `400 unknown_contract_key`
  - `409 nondeterministic_bundle`
- hash決定論:
  - `queryCanonicalHash` / `bundleHash` は canonical JSON + sha256(lowercase-hex) を採用。
  - 同一 canonical query で 3/3 一致しない場合は fail-closed。

### Phase 5 Verify（determinism / preview / safeMode boundary）
- determinism: `sameQuery && !sameBundle -> 409 nondeterministic_bundle` を維持。
- preview: `previewConfirmed=false -> 422 preview_required` を維持。
- safeMode境界: CE1では `CE0-SAFEMODE-IF` を read-only 参照し、既定ON/緩和禁止を維持。
- 判定: **pass（contract-only / mock-first / dependency-decoupled）**。

### Phase 6 Proceed（handoff package）
- Contract IDs:
  - `CE1-CTXQ-IF`
  - `CE1-CTXB-IF`
  - `CE1-HASH-DET-IF`
  - `CE1-PREVIEW-GATE-IF`
- Handoff keys:
  - `queryCanonicalHash`
  - `bundleHash`
  - `sourceBundleHash`
  - `equivalenceKey`
- Error semantics:
  - `preview_required`
  - `unknown_contract_key`
  - `nondeterministic_bundle`
- 注記: CE1は契約固定のみ。下流実装依存は mock 契約で切断し、進捗待ち禁止。

## Stream D update（2026-05-04 / CE1 Foundation docs-only contract freeze）

### Phase 1 Read
- 上位文書（`AGENTS.md` Read Order 1〜6）と当該Issueを再読し、編集対象を本ファイルのみに限定することを再確認。
- Interface-first / mock-first を適用し、`ContextQueryV1` / `ContextBundleV1` を実装非依存の契約として先行固定する前提を確認。

### Phase 2 ADR明文化（Context / Decision / Consequences）
- **Context**: CE2/CE4 が CE1 実装完了待ちで停止しないよう、契約I/Fを先に固定して依存を切断する必要がある。
- **Decision**: `ContextQueryV1` / `ContextBundleV1` を closed-world 契約として固定し、未定義キーは `400 unknown_contract_key`、preview gate は `previewConfirmed=false -> 422 preview_required`、決定論不一致は `409 nondeterministic_bundle` とする。
- **Consequences**: 下流は mock contract で並行検証可能。CE1 は docs-only で契約凍結を維持し、handler/UI/DB/worker の実装判断を持ち込まない。

### Phase 3 Plan（AC/DoD不足補完）
- AC補完:
  - `ContextQueryV1` / `ContextBundleV1` のv1キー集合を固定し、unknown key の失敗条件を明文化。
  - `queryCanonicalHash` / `bundleHash` の決定論チェックを「同一canonical queryで3回一致」に固定。
  - `previewConfirmed` の入力ゲートを契約上の必須条件として固定。
- DoD補完:
  - 引き渡し物は契約ID、I/F型、エラー語彙、handoff key のみ。
  - 下流検証は mock-only で再現可能（実実装依存なし）。

### Phase 4 Execute（docs-only契約固定）
- 本Issue内の契約記述を正本として CE1 v1 契約を凍結。
- Contract IDs: `CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF` を維持。
- 追加仕様（新キー/新エラー/新HTTP語彙）は本フェーズでは導入しない。

### Phase 5 Verify（最大3回自己修復）
- Verify-1: `git diff --check`（フォーマット不整合なし）。
- Verify-2: `rg -n "Stream D update|ContextQueryV1|ContextBundleV1|preview_required|unknown_contract_key|nondeterministic_bundle" 01_Plans/issues/issue-CE1-context-query-bundle-foundation.md`（契約語彙の存在確認）。
- Verify-3: `git status --short`（編集対象が本ファイルのみであることを確認）。
- 失敗時は原因を本ファイル内で修正し再検証、3回超過時は `held`。

### Phase 6 Stopper（致命条件）
- 非許可ファイル編集要求が発生した場合は即 `held` 停止。
- 契約語彙衝突（error semantics / contract id collision）を検知した場合は `held` 停止。
- Verify失敗が3回を超えた場合は `held` 停止。

## Stream D update（2026-05-04 / CE1 ContextQuery/ContextBundle I/F freeze）

### Phase 1 Read同期
- Read Order 1〜13 のうち、CE1契約固定に必要な上流（`00_Prompt/*`, `ADR-0001`, `ADR-0028`, `02_Architecture/architecture.md`, `02_Architecture/schemas.md`, `ADR-0019`）を再確認。
- Scope を docs-only / single-file（本Issueのみ）に再固定し、実装レイヤ（handler/UI/DB/worker）非編集を再確認。
- 既存凍結語彙（`preview_required` / `unknown_contract_key` / `nondeterministic_bundle`）と Contract IDs（`CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`）に衝突がないことを確認。

### Phase 2 ADR明文化（Context / Decision / Consequences）
- **Context**: CE2/CE4 が CE1 実装待ちで停止しないため、I/F（型・必須キー・決定論hash）を先に固定する必要がある。
- **Decision**:
  - `ContextQueryV1` / `ContextBundleV1` を closed-world 契約として固定（未定義キーは `400 unknown_contract_key`）。
  - `previewConfirmed=false -> 422 preview_required` を preview gate の必須エラー条件として固定。
  - `queryCanonicalHash` / `bundleHash` は同一canonical queryで3回一致を決定論条件とし、不一致時は `409 nondeterministic_bundle` で fail-closed。
- **Consequences**:
  - CE2/CE4 は mock contract のみで正/異常系検証を継続可能。
  - CE1 実装詳細が未定でも、handoff key（`sourceBundleHash === bundleHash`, `equivalenceKey + bundleHash`）の接続契約は維持される。

### Phase 3 Plan（AC/DoD不足補完）
- AC補完:
  - [x] 型・必須キー・固定エラー条件を本Issue単体で参照可能に維持。
  - [x] hash決定論（3回一致）と失敗条件（409）を明示。
  - [x] mock-first 前提で CE2/CE4 の依存切断を明示。
- DoD補完:
  - [x] 成果物は契約ID / I/F型 / 固定語彙 / handoff key のみ。
  - [x] 実装方式・内部アルゴリズム・ランタイム詳細は非対象。
  - [x] Verify は mock validation 前提の整合確認で完了判定する。

### Phase 4 Execute（closed-world契約・エラー条件固定）
- `ContextQueryV1` / `ContextBundleV1` の v1 キー集合凍結を継続適用。
- 未定義キー拒否（`400 unknown_contract_key`）を v1 契約の境界条件として再固定。
- preview gate（`422 preview_required`）と hash非決定論（`409 nondeterministic_bundle`）を fail-closed の固定条件として再掲。
- 契約語彙衝突を防ぐため、v1拡張は明示的にv2以降へ延期（v1内の暗黙拡張を禁止）。

### Phase 5 Verify（mock validation前提の整合）
- Verify-1: mock input で `previewConfirmed=false` を与えた場合、`422 preview_required` に一意マップできること。
- Verify-2: mock query/bundle に未定義キーを注入した場合、`400 unknown_contract_key` に一意マップできること。
- Verify-3: 同一canonical queryの3回試行で `bundleHash` 不一致を1回でも検知した場合、`409 nondeterministic_bundle` へ fail-closed できること。
- Verify-4: CE2/CE4 引き渡しキー（`sourceBundleHash === bundleHash`, `equivalenceKey + bundleHash`）が契約上読み取れること。
- 判定: **pass（mock-first整合成立 / 実装依存なし）**。

### Phase 6 Proceed / Stop
- **Proceed条件**: 上記Verify-1〜4がすべて満たされ、契約語彙衝突なし。
- **Stop条件**:
  1. Self-Correction が3回上限を超過（4回目相当）した場合は `held`。
  2. 依存先未定義（CE0/CE2/CE4 handoff key未成立）を検知した場合は停止。
  3. 契約語彙衝突（error semantics / contract id collision）を検知した場合は停止。
- 本更新は docs-only の契約固定であり、実装タスクの追加・移譲は行わない。


## Stream B update（2026-05-04 / CE1契約基盤 / mock-first固定）

### Phase 1: Read同期（対象ファイル再Read）
- 契約ID現状: `CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF` を維持。
- error語彙現状: `preview_required` / `unknown_contract_key` / `nondeterministic_bundle` を維持。
- hash要件現状: `queryCanonicalHash` / `bundleHash` は同一canonical queryで決定論一致（3回一致、fail-closed）を維持。
- 判定: 前提差分なし（continue）。

### Phase 2: ADR明文化（Context / Decision / Consequences）
- **Context**: CE1を先行固定しない場合、CE2（assist）/CE4（API+CLI監査）が実装待ち依存で停止する。よってCE1は実装より先に最小I/F契約を固定し、mock-onlyで下流の検証を可能にする必要がある。
- **Decision**:
  1. `ContextQueryV1` / `ContextBundleV1` をv1 closed-world契約として固定し、未定義キーは拒否する。
  2. preview gateを固定し、`previewConfirmed=false -> 422 preview_required` を必須挙動とする。
  3. hash決定論を固定し、同一canonical queryに対して `bundleHash` が不一致なら `409 nondeterministic_bundle` でfail-closedする。
  4. 契約解釈はclosed-world（v1外拡張禁止、拡張はv2のみ）とする。
- **Consequences**:
  - CE2/CE4がmockで進める範囲: 契約ID、型I/F、固定エラー語彙、hash検証条件、handoff key接続検証。
  - CE2/CE4が進めない範囲: handler/UI/DB/worker実装、永続化戦略、実ランタイム最適化。

### Phase 3: Plan（AC/DoD + handoff artifact）
- AC再掲（不足なし）:
  - ADR形式でCE1先行固定理由を記述。
  - `ContextQueryV1` / `ContextBundleV1` のclosed-world整合を維持。
  - `422 preview_required` / `400 unknown_contract_key` / `409 nondeterministic_bundle` を固定。
  - hash決定論要件（3回一致）を固定。
  - mock validation計画（実装依存切断）を維持。
- DoD:
  - docs-only差分であること。
  - CE2/CE4がmock-onlyで検証継続可能であること。
- handoff artifact（read-only）:
  - 契約ID: `CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`
  - 型: `ContextQueryV1` / `ContextBundleV1`
  - エラー語彙: `preview_required` / `unknown_contract_key` / `nondeterministic_bundle`
  - 検証条件: `sourceBundleHash === bundleHash`、`equivalenceKey + bundleHash`、同一canonical queryで3回一致

### Phase 4: Execute（契約固定）
- `previewConfirmed=false -> 422 preview_required` を固定。
- unknown key -> `400 unknown_contract_key` を固定。
- nondeterministic bundle -> `409 nondeterministic_bundle` を固定。
- いずれも実装方式に依存しない契約要件として維持。

### Phase 5: Verify（mock-only自己点検）
- CE2 mock検証可否: `sourceBundleHash === bundleHash` 比較でpass/failを再現可能（pass）。
- CE4 mock検証可否: `equivalenceKey + bundleHash` を監査キーとして固定検証可能（pass）。
- 異常系再現可否: `422/400/409` の固定語彙をmock応答で再現可能（pass）。
- Self-Correction: 0/3（追加修正不要）。

### Phase 6: Proceed（read-only handoff）
- Handoff（編集依頼なし / 依存断ち）:
  - CE1契約はv1凍結維持。
  - 下流は契約参照のみで並行進行し、実装依存要求を行わない。
  - 未定義競合・前提崩壊・許可外ファイル要求が発生した場合は `held` で即停止する。

## Stream B run（2026-05-05 / CE1-context-query-bundle-foundation / interface freeze）

### Phase 1 Read
- 本Issue再読により、`CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF` の凍結状態を確認。
- 固定エラー語彙 `preview_required` / `unknown_contract_key` / `nondeterministic_bundle` を再確認。

### Phase 2 Plan（mock前提I/F定義 + AC/DoD補完）
- mock前提I/F定義（維持）:
  - `ContextQueryV1` 入力ゲート: `previewConfirmed=false -> 422 preview_required`
  - closed-world: 未定義キーは `400 unknown_contract_key`
  - hash決定論: 同一canonical queryで不一致時 `409 nondeterministic_bundle`
- AC補完提案:
  - `ac_signature_freeze_trace`: `ContextQueryV1` / `ContextBundleV1` のキー集合不変を毎runで記録。
  - `ac_mock_handoff_ready`: CE2/CE4向けに `sourceBundleHash === bundleHash` / `equivalenceKey + bundleHash` を必須確認。
- DoD補完提案:
  - `dod_closed_world_enforced`: v1外拡張を本文で禁止明記。
  - `dod_error_semantics_1to1`: 422/400/409と語彙の1:1対応を維持。

### Phase 3 ADR合意（Context / Decision / Consequences）
- Context: CE1の型・署名が先行固定されないと、CE2/CE4が実装待ちで停止する。
- Decision: `ContextQueryV1` / `ContextBundleV1` を契約先行で凍結し、preview/hash/unknown-keyの失敗語彙をv1固定。
- Consequences: 下流はmock-onlyで並行検証可能。契約衝突検知時は `held` 停止。

### Phase 4 Execute（型・署名固定の運用記録）
- ContextQuery/ContextBundleの型・署名は既存凍結値を維持（追加/改名/削除なし）。
- 実装詳細（handler/UI/DB/worker/API behavior）は非対象として維持。

### Phase 5 Verify（自己検証 + 整合）
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` : pass
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` : pass
- `git diff --check` : pass
- 整合判定: `contract_id_collision=0 / error_semantics_collision=0 / scope_deviation=0`。
- 自己修復: 0/3。

### Phase 6 Proceed/Stop
- 判定: **Proceed（Interface Freeze Maintained）**。
- 停止条件: 未定義競合、自己修復4回目相当、許可外ファイル要求で `held`。


## Stream B run（2026-05-05 / CE1 interface-first freeze handoff）

### Phase 1 Read
- CE0 freeze / CE0 core graph / CE1 foundation の3Issue再読により、CE1が CE2/CE4 の共通I/F前提であることを再確認。
- `ContextQueryV1` / `ContextBundleV1` と固定語彙（422/400/409）の凍結状態を確認。

### Phase 2 ADR/CDC
- **Context**: CE2/CE4の並行進行には、CE1の型・キー・エラー意味論を実装前に固定する必要がある。
- **Decision**: CE1を `contract-only / mock-first` で維持し、`preview_required` / `unknown_contract_key` / `nondeterministic_bundle` を1:1固定語彙として継続。
- **Consequences**: 下流は mock-only で検証継続可能。v1拡張要求は `held` として分離。

### Phase 3 Plan
- AC/DoD補強（合意）:
  - `ac_if_freeze_precedes_impl`: I/F固定を実装決定より常に先行。
  - `dod_handoff_keys_explicit`: `queryCanonicalHash` / `bundleHash` / `sourceBundleHash` / `equivalenceKey` を handoff 必須項目として明示。

### Phase 4 Execute
- CE0→CE1順で文言・依存・ゲート条件を正規化。
- `previewConfirmed=false -> 422 preview_required`、unknown key -> `400 unknown_contract_key`、非決定論 -> `409 nondeterministic_bundle` を維持。
- I/F先行固定（interface-first freeze）を明示し、実装順序確定は対象外を再宣言。

### Phase 5 Verify
- docs-check観点自己検証: 1回で完了（self-correction 0/3）。
- 判定: `contract_id_collision=0` / `error_semantics_collision=0` / `dependency_cycle=0`。

### Phase 6 Proceed
- CE2/CE4引き渡し前提（read-only）:
  - Contract IDs: `CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`
  - Handoff keys: `queryCanonicalHash` / `bundleHash` / `sourceBundleHash` / `equivalenceKey`
  - 固定語彙: `preview_required` / `unknown_contract_key` / `nondeterministic_bundle`
- 停止条件: 自己修復4回目相当、未定義競合、許可外編集要求で `held`。

## Stream D run（2026-05-05 / CE1基盤 contract-first rehearsal）

### Phase 1 Read同期
- Read Order準拠で `00_Prompt` → `01_Plans/adr/ADR-0001` → `02_Architecture/{architecture,schemas}` を再確認し、本Issueの編集スコープ（docs-only）を再固定。
- CE1凍結対象 `CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF` と、固定エラー語彙 `preview_required` / `unknown_contract_key` / `nondeterministic_bundle` の不変性を確認。

### Phase 2 Plan（AC/DoD提案）
- AC提案:
  - `ac_closed_world_v1`: `ContextQueryV1` / `ContextBundleV1` は v1 で unknown key reject（`400 unknown_contract_key`）。
  - `ac_preview_gate_strict`: `previewConfirmed=false` は常に `422 preview_required`。
  - `ac_hash_deterministic_3of3`: 同一 canonical query で `queryCanonicalHash` / `bundleHash` が3/3一致。
  - `ac_downstream_decoupled`: CE2/CE4 が mock I/F のみで検証継続可能（実装依存なし）。
- DoD提案:
  - docs-only差分（実装コード変更なし）。
  - handoff成果物を「Contract ID / 型I/F / error semantics / hash gate / handoff key」に限定。

### Phase 3 ADR C/D/C明文化と合意
- Context: CE2/CE4の停止要因は実装待ちではなく契約不確定であるため、CE1は契約先行固定が必須。
- Decision: `ContextQueryV1` / `ContextBundleV1` を closed-world v1 として凍結し、`422/400/409` の固定語彙を変更禁止とする。
- Consequences: 下流は read-only handoff（`queryCanonicalHash` / `bundleHash` / `sourceBundleHash` / `equivalenceKey`）で並行可能。v1拡張要求は v2 起票まで `held`。

### Phase 4 Execute（契約・モック定義）
- mock I/F boundary（実装非依存）を明示:
  - `POST /context/query`: `ContextQueryV1` を受理し、preview gate と unknown key を検証。
  - `POST /context/bundle`: `{ query: ContextQueryV1, stubDatasetId }` を受理し、deterministic hash を検証。
- mock validation手順（契約テスト）:
  1. preview gate異常系: `previewConfirmed=false` で `422 preview_required` を確認。
  2. closed-world異常系: 未定義キー入力で `400 unknown_contract_key` を確認。
  3. deterministic系: 同一canonical queryで3回実行し、`queryCanonicalHash` と `bundleHash` の3/3一致を確認。
  4. 不一致系: same query で `bundleHash` 不一致時に `409 nondeterministic_bundle` を確認（fail-closed）。

### Phase 5 Verify（self-correction 最大3回）
- Attempt 1: Contract ID衝突チェック（結果: 競合なし）。
- Attempt 2: schema語彙揺れチェック（結果: 競合なし）。
- Attempt 3: handoff key完全性チェック（`sourceBundleHash === bundleHash` 比較可能、結果: pass）。
- Verify総合: `contract_version_mismatch=0` / `schema_conflict=0` / `self_correction_count=3以内`。

### Phase 6 Proceed（Go/No-Go判定）
- 判定: **Go（CE1 contract-first mock handoff ready）**。
- No-Go移行条件:
  - 契約version不整合
  - 未定義schema競合
  - self-correction 3回超過（4回目相当）
- No-Go時動作: 状態を `held` に固定し、Phase 3（ADR C/D/C）へロールバック。

## Stream C run（2026-05-05 / CE1基盤 contract-first formalization）

### Phase 1 Read（CE0固定契約の再読）
- `issue-CE0-contract-freeze.md` を read-only で再読し、`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` と No-Go canonical IDs の固定を再確認。
- 本Stream Cの編集許可が `01_Plans/issues/issue-CE1-context-query-bundle-foundation.md` のみであることを再確認。

### Phase 2 ADR明文化（Context / Decision / Consequences）
- **Context**: CE2/CE4 が実装待ちで停止しないためには、CE1で ContextQuery/ContextBundle/Preview gate を実装非依存の契約として先行固定する必要がある。
- **Decision**:
  - `ContextQueryV1` / `ContextBundleV1` は v1 closed-world を維持し、未定義キーは `400 unknown_contract_key`。
  - `previewConfirmed=false` は常に `422 preview_required`（preview bypass 禁止）。
  - 同一 canonical query で hash 不一致を検知した場合は `409 nondeterministic_bundle` で fail-closed。
- **Consequences**:
  - 下流は mock-only で検証継続可能。
  - safeMode 境界は CE0 の read-only 契約に従い、既定ON/緩和禁止を維持。

### Phase 3 Plan（ContextQuery/Bundle/Preview の AC/DoD 確定）
- **AC**:
  1. `ContextQueryV1` / `ContextBundleV1` のキー集合は v1 で凍結（closed-world）。
  2. Preview gate は `previewConfirmed=false -> 422 preview_required` を固定。
  3. hash 決定論は同一 canonical query 3回一致、破綻時 `409 nondeterministic_bundle`。
  4. handoff key は `queryCanonicalHash` / `bundleHash` / `sourceBundleHash` / `equivalenceKey` を必須。
- **DoD**:
  1. docs-only（本ファイルのみ）であること。
  2. CE2/CE4 が mock 契約のみで正常系/異常系を再現できること。
  3. safeMode 除外・緩和を導入しないこと（CE0境界維持）。

### Phase 4 Execute（計画文書の具体化）
- AC/DoD を本Issueへ具体化し、契約固定の運用記録として追記。
- 実装詳細（handler/UI/DB/worker）や他ストリーム領域の変更は実施しない。

### Phase 5 Verify（決定論・safeMode除外ルール・audit観点）
- 決定論: `same canonical query` に対し `bundleHash` 不一致は `409 nondeterministic_bundle` を返す fail-closed を維持。
- safeMode除外ルール: `CE0-SAFEMODE-IF` を read-only 参照し、既定ON・`allowUnreviewedText=false` 境界を逸脱しない。
- audit観点: CE4連携キー `equivalenceKey + bundleHash` と CE2連携条件 `sourceBundleHash === bundleHash` の追跡可能性を維持。
- 自己修正回数: 0/3（上限3回未満）。

### Phase 6 Proceed
- 判定: **Proceed（CE1 foundation contract maintained）**。
- Stop条件（発生時は `held`）:
  1. 未定義契約衝突（contract id / error semantics collision）。
  2. safeMode 既定値緩和要求。
  3. 自己修正4回目相当（>3回）。

## Stream C run（2026-05-05 / CE1 Foundation contract-only hardening）

### Phase 1 Read（対象再読・差分確認）
- 本対象ファイルをフェーズ開始時に再読し、CE1編集範囲が本Issue単体であることを再確認。
- 既存凍結ID（`CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`）と固定語彙（`preview_required` / `unknown_contract_key` / `nondeterministic_bundle`）に差分なし。

### Phase 2 ADR（Context / Decision / Consequences）
- **Context**: CE2/CE4が外部ストリーム完了待ちなしで進行するため、CE1は実装ではなく契約だけを固定する必要がある。
- **Decision**: `contract-only / mock-first` を維持し、`ContextQueryV1` / `ContextBundleV1` の closed-world 契約、`previewConfirmed=false -> 422 preview_required`、hash非決定論時 `409 nondeterministic_bundle` を変更不可として固定。
- **Consequences**: 下流は mock 契約だけで検証継続できる。handler/UI/DB/worker 仕様は CE1で扱わず、依存を切断したまま並行実行可能。

### Phase 3 Plan（AC/DoD確定）
- **AC**:
  1. `ContextQueryV1` / `ContextBundleV1` は v1 closed-world（unknown key は `400 unknown_contract_key`）。
  2. preview gate は `previewConfirmed=false -> 422 preview_required` を必須化。
  3. 決定論条件は同一canonical queryで `queryCanonicalHash` / `bundleHash` が3回一致。
  4. 不一致時は `409 nondeterministic_bundle` で fail-closed。
- **DoD**:
  1. handoff成果物は「契約ID / I/F型 / エラー語彙 / handoff key」のみ。
  2. CE2/CE4は mock 契約で検証可能（外部ストリーム完了待ち禁止）。
  3. 実装詳細（handler/UI/DB/worker）へ逸脱しない。

### Phase 4 Execute（契約固定）
- `previewConfirmed` gate を固定し、bypassを許容しない。
- closed-world違反（unknown key）は `400 unknown_contract_key` に固定。
- same canonical query で bundle不一致は `409 nondeterministic_bundle` に固定。
- 追加キー・追加語彙・実装方式の記述は導入しない。

### Phase 5 Verify（自己検証）
- AC/DoD充足を本Issue内で再確認し、契約衝突なしを確認。
- self-correction: 0/3（修復不要）。

### Phase 6 Proceed / Stop
- 判定: **Proceed（CE1 Foundation contract maintained）**。
- Stop条件（即 `held`）:
  1. contract id / error semantics の衝突。
  2. preview語彙・決定論語彙の変更要求。
  3. 自己修復4回目相当（>3回）。

## Stream CE1 update（2026-05-06 / ContextQuery-ContextBundle Foundation contract-only）

### Phase 1 Read（latest mandatory read）
- 本Issueを基準に、Read Order上流（`00_Prompt/*`、`ADR-0001`、`02_Architecture/architecture.md`、`02_Architecture/schemas.md`、`ADR-0028`、`ADR-0019`）を再読し、CE1の責務を **contract-only / docs-only / mock-first** に固定した。
- 編集許可が `issue-CE1-context-query-bundle-foundation.md` のみであることを再確認し、実装層（backend/frontend/worker/DB）を非対象として分離した。

### Phase 2 ADR（Context / Decision / Consequences）
- **Context**: CE2/CE4の先行検証を維持するため、CE1は実装依存を導入せず、I/F契約のみを先に確定する必要がある。
- **Decision**: `ContextQueryV1` / `ContextBundleV1` のclosed-world契約、固定エラー語彙、hash決定論（同一canonical queryで3回一致）をv1固定として継続する。
- **Consequences**: CE2/CE4はmockで正常/異常系を検証可能とし、CE1実装待ちを依存条件にしない。

### Phase 3 Contract-first plan（implementation dependency separation）
- I/F先行: 引き渡し成果物を `Contract IDs + Type signature + Error semantics + handoff keys` に限定する。
- mock-first: 検証対象を `preview_required` / `unknown_contract_key` / `nondeterministic_bundle` の3異常系と正常系最小ケースに固定する。
- 依存切断: handler/UI/DB/worker/API実装詳細は本Issueに記述しない。

### Phase 4 Verify（contract consistency）
- `previewConfirmed=false -> 422 preview_required` を入力ゲートとして維持。
- `queryCanonicalHash` / `bundleHash` の決定論違反を `409 nondeterministic_bundle` で fail-closed 維持。
- `sourceBundleHash === bundleHash` と `equivalenceKey + bundleHash` のhandoff key整合を維持。
- 判定: **pass（contract-only consistency maintained）**。

### Phase 5 Proceed/Stop
- Proceed条件: docs-only差分でCE1 v1契約に矛盾がないこと。
- Stop条件: 自己修復が3回を超えた時点で `held` に固定して停止（4回目に進まない）。
- 本更新の自己修復回数: `0/3`（追加修復なし）。

## Stream B latest run（2026-05-06 / CE1 ContextQuery-Bundle foundation progression）

- run_id: `stream-b-ce1-foundation-2026-05-06-10`
- assignee: `Stream B（CE0/CE1基盤進行）`
- scope_guard: docs-only / contract-only / mock-first

### Phase 1 Read（latest + AC/DoD）
- CE1凍結対象（`CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`）とCE0 read-only境界を再確認。
- AC/DoDおよび停止条件（自己修復3回上限）を再確認。

### Phase 2 CE0契約凍結前提の独立化
- `previewConfirmed=false -> 422 preview_required`、unknown key、hash不一致の固定失敗語彙を再確認。
- CE0再定義を行わず、CE1は契約受領側として整合維持。

### Phase 3 ContextQuery/Bundle基盤整備
- `ContextQueryV1` / `ContextBundleV1` の closed-world と v1 key freeze を維持。
- `queryCanonicalHash` / `bundleHash` の決定論要件（不一致時 `409 nondeterministic_bundle`）を再固定。

### Phase 4 Mock-first validation alignment
- CE2/CE4が mock-only で進行可能な handoff key（`sourceBundleHash === bundleHash`、`equivalenceKey + bundleHash`）を再確認。
- 実装非依存の契約成果物に限定。

### Phase 5 Verify & handoff
- 判定: **Conditional-Go**（CE1 foundation contract maintained）。
- handoff（CE2/CE4）: Contract IDs / fixed error semantics / hash keys の read-only 契約パッケージ。
- self-correction usage: `0/3`。
