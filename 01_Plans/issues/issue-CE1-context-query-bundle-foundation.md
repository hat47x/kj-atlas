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

## Lane guard（独立性）
- CE1はCE0 SSOT参照レーン。CE0を上位SSOTとしてread-only参照し、CE1側で再定義しない。
- CE1は **I/F凍結のみ**。実装記述（handler/UI/DB/worker）は扱わない。
- CE0契約参照は必須、CE1側で再定義しない。
- 参照方向は `CE0 -> (CE1, CE2, CE4)` の一方向に固定し、CE1からCE0契約本文への逆流再定義を禁止する。
- 強制ワークフローは `Phase 1 Read → Phase 2 Plan → Phase 3 Execute → Phase 4 Verify → Phase 5 Proceed`。
- 各Phaseの冒頭で本対象ファイルを再読し、前提差分を再確認する。

## Phase 1 Read（全対象Read: Status / Scope / Related ADR確認）
- Phase sync: 本対象ファイルを基準版として再読開始。
### Read log（このIssueで参照確認した対象）
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
  - 本Issue更新を停止し、Phase 3（CDC held）へ遷移して承認待ちに固定する。

### Contract IDs（凍結対象）
- CE0契約IDは参照のみ（再定義禁止）。
- CE0参照境界（read-only）:
  - `CE0-CTX-IF`
  - `CE0-SAFEMODE-IF`
  - `CE0-REVIEW-IF`
  - `CG-01..05`
- `CE1-CTXQ-IF`（ContextQueryV1）
- `CE1-CTXB-IF`（ContextBundleV1）
- `CE1-HASH-DET-IF`（hash決定論）
- `CE1-PREVIEW-GATE-IF`（preview gate）

### Error semantics（語彙固定）
- `preview_required`
- `unknown_contract_key`
- `nondeterministic_bundle`

### No-Go / safeMode境界
- No-Go語彙（CE0 canonical 5 IDs）: `preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`
- Query Preview bypass 禁止（`preview_bypass`）。
- `CE0-SAFEMODE-IF` を参照し、CE1側でsafeMode既定を再定義しない。

## Phase 2 Plan（AC/DoD不足ドラフト）
- Phase sync: 本対象ファイルを再読し、前Phaseとの差分がないことを確認。
### Gap draft（不足補完）
- AC不足補完1: hash決定論の検証回数を明示（同一canonical queryで3回一致）。
- AC不足補完2: preview gateの失敗コード/語彙を固定（`422 preview_required`）。
- AC不足補完3: closed-world違反時の失敗コード/語彙を固定（`400 unknown_contract_key`）。
- DoD不足補完1: CE2/CE4引き渡しキーの一致条件を明文化（`sourceBundleHash === bundleHash`）。
- DoD不足補完2: safeMode regression=0 を完了条件に追加。

### 合意後固定（Plan freeze）
- 本Issueでは上記Gap draftを **CE1 v1契約の固定候補** として扱う。
- 固定は contract-only（I/F語彙・戻り値・検証条件）に限定し、実装手段は記述しない。
- 依存切断方針としてモック前提を維持する:
  - `sourceBundleHash` は CE1 `bundleHash` の受け渡し専用キーとして扱う。
  - hash検証は deterministic mock（同一canonical queryを3回）で成立判定する。

### Plan outputs（v1で凍結する内容）
- `previewConfirmed=false -> 422 preview_required` を契約として固定。
- unknown key -> `400 unknown_contract_key` を契約として固定。
- 同一 canonical query で `queryCanonicalHash/bundleHash` 一致を契約として固定。

## ADR CDC（衝突検知時のみ Context / Decision / Consequences を起票し承認待ち）
- 差分検知ログ対象: `equivalenceKey + bundleHash` / `sourceBundleHash` / error semantics の語彙揺れ / No-Go語彙不一致 / CE0契約ID衝突。
- 衝突未検知時（contract_id_collision=0 かつ vocabulary_collision=0）はCDCを起票しない。
- CDC起票時のStatus: `held`（承認待ち、未承認確定禁止）。
- CDCが必要になった場合のみ、以下3項目を **その場で明文化して `held`** に遷移する（未承認のまま確定しない）。
  - **Context**: どの契約/語彙で何が衝突したか（CE0参照ID・語彙差分・検知ログ）。
  - **Decision**: v1で固定する解決策（I/F凍結範囲のみ。再定義禁止）。
  - **Consequences**: CE2/CE4 handoff への影響と回帰リスク。
- 本Issue時点では CDC未起票（衝突未検知）として扱う。

### CDC最小テンプレート（衝突時のみ記入）
- Status: `held`
- Context: `CE0参照ID` / `衝突語彙` / `検知ログID`
- Decision: `v1で固定するI/F差分（再定義なし）`
- Consequences: `CE2/CE4 handoff影響` / `safeMode回帰リスク`

## Phase 3 Execute（ContextQuery/Bundle v1 closed-world, preview_required, hash決定論）
- Phase sync: 本対象ファイルを再読し、前Phaseとの差分がないことを確認。
### I/F Mock Freeze（実装記述なし）
- 固定I/F（v1 / closed-world）
  - `ContextQueryV1` は未定義キーを許容しない（`400 unknown_contract_key`）。
  - `ContextBundleV1` は `queryCanonicalHash` / `bundleHash` を必須返却する。
  - `previewConfirmed=false` は生成処理に進まず `422 preview_required` を返す。
  - Query Previewは必須ゲートとし、bypass経路を許容しない（`preview_bypass`禁止）。
- hash固定（決定論）
  - 同一 canonical query では `queryCanonicalHash` が常に一致。
  - 同一 canonical query では `bundleHash` が常に一致。
- CE2連携境界
  - `sourceBundleHash === bundleHash` 比較キーのみを提供。
- CE4連携境界
  - `equivalenceKey + bundleHash`（AND判定）と `queryCanonicalHash` を引き渡す。
- 参照境界
  - CE0 (`CE0-CTX-IF`/`CE0-SAFEMODE-IF`) 参照のみで固定。

### Stop conditions（フェイルセーフ）
- preview bypass 許容が混入した場合は即停止。
- safeMode緩和（既定値変更を含む）が混入した場合は即停止。
- 契約語彙の未定義競合（CE0/CE2/CE4間）が解消不能なら停止。
- Self-Correction 3回超過で停止。

## Phase 4 Verify（docs-check / 修復3回まで）
- Phase sync: 本対象ファイルを再読し、前Phaseとの差分がないことを確認。
### Verify commands
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`

### Acceptance Criteria / DoD
- [ ] 同一 canonical query 3回で `queryCanonicalHash` が一致
- [ ] 同一 canonical query 3回で `bundleHash` が一致
- [ ] `previewConfirmed=false` は常に `422 preview_required`
- [ ] 未定義キー入力は常に `400 unknown_contract_key`
- [ ] `sourceBundleHash === bundleHash` 比較語彙がCE2/CE4と一致
- [ ] SafeMode regression = 0

## Phase 5 Proceed（CE2/CE4連携キー handoff）
- Phase sync: 本対象ファイルを再読し、前Phaseとの差分がないことを確認。
### Fixed contract handoff
- Contract IDs: `CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`
- 禁止事項: preview bypass / safeMode緩和 / 未定義キー黙認
- 検証条件: hash決定論一致, preview gate強制, docs-check pass
- 契約語彙整合: `preview_required` / `unknown_contract_key` / `nondeterministic_bundle` を固定継承
- SafeMode後退: 0（既定緩和なし）

### Read-only handoff（CE2 / CE4向け）
- handoff matrixはread-only維持とし、下流（CE2/CE4）での契約再定義を禁止する。
- CE2向け:
  - 比較語彙は `sourceBundleHash === bundleHash` のみ利用可（再定義禁止）。
  - `sourceBundleHash` の供給元は CE1 `ContextBundleV1` の `bundleHash` 固定値のみ。
- CE4向け:
  - 監査照合は `equivalenceKey + bundleHash`（AND）と `queryCanonicalHash` を必須入力とする。
  - `preview_required` / `unknown_contract_key` / `nondeterministic_bundle` のエラー語彙をそのまま監査ログ語彙に継承する。

## Fail-safe（即停止条件）
- Self-Correction 3回超過
- 未定義ファイル競合
- SafeMode後退の兆候
- 依存前提崩壊

---

## Stream D Execution Record（2026-04-21 / docs-only）

### Phase 1 Read（対象ファイル再読）
- 再読対象: `issue-CE1-context-query-bundle-foundation.md`（本ファイル）
- 判定: Scopeは `01_Plans/issues/issue-CE1-context-query-bundle-foundation.md` のみで維持。
- 独立性チェック: 指定外ファイル編集なし。

### Phase 2 Plan（AC/DoD補完）
- AC/DoD補完方針を再確認し、v1契約の固定対象を以下で維持:
  - `previewConfirmed=false -> 422 preview_required`
  - unknown key -> `400 unknown_contract_key`
  - 同一canonical queryで `queryCanonicalHash` / `bundleHash` の決定論一致（3回）
  - CE2/CE4 handoff key: `sourceBundleHash === bundleHash`
  - safeMode regression = 0
- CDC起票要否: 衝突未検知のため **起票不要**（`held`遷移なし）。

### Phase 3 Execute（contract-only整備）
- 実施内容: 本Issue内の運用記録を追加（実装記述は追加しない）。
- 禁止事項再確認: preview bypass / safeMode既定緩和 / 契約再定義を未実施。

### Phase 4 Verify（最大3回自己修復ルール）
- Attempt 1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` => pass
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` => pass
  - `git diff --check` => pass
- Self-Correction: 0回（再試行不要）。

### Phase 5 Proceed（次レーン引き渡し条件）
- CE1固定契約語彙は維持し、CE2/CE4へは read-only handoff を継続。
- 停止条件監視:
  - Self-Correction 3回超過: 該当なし
  - 未定義競合: 該当なし
  - 前提崩壊: 該当なし
