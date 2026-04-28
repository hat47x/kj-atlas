# Issue Draft: CE1 ContextQuery/ContextBundle Foundation（Stream D / CE1専任 / contract-only planning）

- Type: Feature request
- Status: Open
- Priority: P1
- Owner: Stream D（CE1 ContextQuery/ContextBundle Foundation）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Editable: `issue-CE1-context-query-bundle-foundation.md` のみ
- Related Backlog: `CE-1`
- Related ADR/Spec: `ADR-0028`, `02_Architecture/schemas.md`
- Verification: `docs-check`

## 目的（contract-only）
- ContextQuery / ContextBundle の最小I/F契約を固定する。
- deterministic hash 条件（`queryCanonicalHash` / `bundleHash`）を固定する。
- preview gate 条件（`previewConfirmed` 必須確認）を固定する。
- 実装詳細（handler/UI/DB/worker）は記述せず、契約I/Fに限定する。

## Lane guard（独立性）

## Stream C latest run（2026-04-28 / CE1 Context foundation freeze）

### Phase 1 Read
- CE1 v1 I/F（`CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`）と CE0 read-only 境界を再確認。
- 現行schema境界とエラー語彙固定（`preview_required` / `unknown_contract_key` / `nondeterministic_bundle`）を確認。

### Phase 2 Plan
- 契約先行でデータ型・必須属性を固定：`ContextQueryV1` / `ContextBundleV1` の closed-world。
- 互換ルールを固定：v1のキー集合とエラー意味論は変更禁止、拡張は v2 のみ許可。

### Phase 3 Execute
- mock-first（実装未着手）で A2 実行条件を整備：`previewConfirmed=false -> 422 preview_required`、同一canonical queryで hash一致必須。
- CE2/CE4 handoff キー（`sourceBundleHash === bundleHash`、`equivalenceKey + bundleHash`）を維持。

### Phase 4 Verify
- 下流実装向けシグネチャ一覧を固定：`ContextQueryV1` / `ContextBundleV1` / `ProposalPatchV1` / `AuditEventV1`。
- fail-safe 判定：破壊的schema変更なし、互換性喪失なし、他ストリーム編集要求なし。

### Phase 5 Proceed
- 判定: **Contract Freeze Declared（CE1 Context foundation）**。
- 追加要求は `held` へ移送し、承認まで v1 契約を凍結維持。

- CE1はCE0 SSOT参照レーン。CE0を上位SSOTとしてread-only参照し、CE1側で再定義しない。
- CE1は **I/F凍結のみ**。実装記述（handler/UI/DB/worker）は扱わない。
- 参照方向は `CE0 -> (CE1, CE2, CE4)` の一方向に固定し、CE1からCE0契約本文への逆流再定義を禁止する。
- 強制ワークフローは `Phase 1 Read → Phase 2 ADR/CDC → Phase 3 Plan → Phase 4 Execute → Phase 5 Verify → Phase 6 Proceed`。
- 各Phaseの冒頭で本対象ファイルを再読し、前提差分を再確認する。

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

### CDC最小テンプレート（衝突時のみ記入）
- Status: `held`
- Context: `CE0参照ID` / `衝突語彙` / `検知ログID`
- Decision: `v1で固定するI/F差分（再定義なし）`
- Consequences: `CE2/CE4 handoff影響` / `safeMode回帰リスク`
- Approval: `Security Officer + System Owner` の2者承認（両者`approved`でのみProceed再開）

### ADR/CDC quick record（今回）
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
- 3回超過（4回目相当）は停止し、Statusを `held` としてProceedへ進まない。
- self-correction counter運用:
  - `attempt=1..3`: 修復と再検証を許可
  - `attempt=4`: 即停止（`held`固定）

## Phase 6 Proceed（CE2/CE4連携キー handoff）
- Phase sync: 本対象ファイルを再読し、前Phaseとの差分がないことを確認。
- 前提: Phase 5が成功し、`held` 項目が残っていないこと。

### Fixed contract handoff
- Contract IDs: `CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`
- 禁止事項: preview bypass / safeMode緩和 / 未定義キー黙認
- 検証条件: hash決定論一致, preview gate強制, docs-check pass
