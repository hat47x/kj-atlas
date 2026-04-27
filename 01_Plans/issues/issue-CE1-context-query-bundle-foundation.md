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

---

## Stream D Execution Record（2026-04-21 / contract freeze re-check）

### Phase 1 Read（CE0参照境界・差分ゲート確認）
- CE0 read-only境界（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）を再確認。
- 差分ゲート判定: **前提差分なし（continue）**。
- 停止監視対象（改名・語彙変更・safeMode既定変更）: 未検知。

### Phase 2 Plan（AC/DoDドラフト合意の再確認）
- 固定対象を再確認:
  - `previewConfirmed=false -> 422 preview_required`
  - unknown key -> `400 unknown_contract_key`
  - hash決定論（同一canonical queryで3回一致）
  - `sourceBundleHash === bundleHash`
  - safeMode regression = 0

### Phase 3 Execute（CE1固定契約のみ）
- 固定契約IDを維持:
  - `CE1-CTXQ-IF`
  - `CE1-CTXB-IF`
  - `CE1-HASH-DET-IF`
  - `CE1-PREVIEW-GATE-IF`
- contract-only範囲を維持し、実装記述の追加なし。

### Phase 4 Verify（語彙/禁止事項/safeMode境界）
- `preview_required` / `unknown_contract_key` / `nondeterministic_bundle` の語彙固定を再確認。
- No-Go語彙（`preview_bypass` ほかCE0 canonical 5 IDs）の不許容を再確認。
- safeMode既定緩和なし（回帰兆候なし）。

### Phase 5 Proceed（CE2/CE4連携参照メモ）
- CE2向け連携キーは `sourceBundleHash === bundleHash` のみを参照。
- CE4向け連携キーは `equivalenceKey + bundleHash`（AND）と `queryCanonicalHash` を参照。
- フェイルセーフ監視: preview bypass許容化なし / Self-Correction 3回超過なし。

---

## Stream D Execution Record（2026-04-21 / CE1 I/F freeze reaffirmation）

### Phase 1 Read（Status/Scope/Related ADR + 差分ゲート）
- Read対象を再確認:
  - 本Issueの Status / Scope / Related ADR
  - `ADR-0028`（CE0→CE1依存順序、stop条件）
  - `02_Architecture/schemas.md`（CE1 I/F語彙、error semantics、determinism要件）
- 差分ゲート結果: **前提差分なし（continue）**。
- CE0 read-only参照を再確認し、CE1側での再定義を禁止状態で維持。

### Phase 2 Plan（AC/DoD不足提案・合意）
- AC/DoD固定候補を再確認し、以下の不足補完を維持合意:
  - 同一canonical queryで3回一致（`queryCanonicalHash` / `bundleHash`）
  - `previewConfirmed=false -> 422 preview_required`
  - unknown key -> `400 unknown_contract_key`
  - `sourceBundleHash === bundleHash`
  - safeMode regression = 0
- ADR CDC起票要否: 衝突未検知のため **起票不要**（`held`遷移なし）。

### Phase 3 Execute（CE1契約語彙固定）
- CE1契約語彙を再固定（contract-only、実装記述なし）:
  - Contract IDs: `CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`
  - Error semantics: `preview_required` / `unknown_contract_key` / `nondeterministic_bundle`
- 逆流再定義禁止を明文化維持:
  - CE0は read-only SSOT 参照のみ。
  - CE1→CE0本文への再定義・再採番は禁止。

### Phase 4 Verify（docs-check、自己修復上限3）
- Attempt 1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` => pass
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` => pass
  - `git diff --check` => pass
- Self-Correction: 0 / 3（再試行不要）。

### Phase 5 Proceed（handoff）
- CE2/CE4への handoff は read-only 契約参照のまま継続。
- 下流利用キーを固定維持:
  - CE2: `sourceBundleHash === bundleHash`
  - CE4: `equivalenceKey + bundleHash`（AND）と `queryCanonicalHash`
- 停止条件監視結果:
  - preview bypass 許容化なし
  - safeMode既定緩和なし
  - 依存前提崩壊なし

### ADR変更要求時の停止ルール（再確認）
- ADR変更が必要になった場合は、**Context / Decision / Consequences を先に明文化し、承認待ち `held` で停止**する。
- 未承認状態での契約確定・下流反映は禁止。

---

## Stream D Execution Record（2026-04-21 / phase-loop refresh）

### Phase 1 Read（再読）
- 本ファイルをPhase冒頭で再読し、Scope/Editableが `01_Plans/issues/issue-CE1-context-query-bundle-foundation.md` のみであることを再確認。
- CE0 read-only境界（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）の再定義禁止を再確認。
- 前提差分ゲート結果: **差分なし（continue）**。

### Phase 2 Plan（AC/DoD補完の合意再確認）
- AC/DoD固定ポイントを再確認:
  - preview gate: `previewConfirmed=false -> 422 preview_required`
  - closed-world: unknown keyは `400 unknown_contract_key`
  - hash決定論: 同一canonical queryで `queryCanonicalHash` / `bundleHash` 3回一致
  - エラー意味論固定: `preview_required` / `unknown_contract_key` / `nondeterministic_bundle`
- mock-first依存切断を維持し、実装待ち依存を追加しないことを再確認。

### Phase 3 Execute（I/F契約固定のみ）
- contract-onlyとして以下を再固定（実装記述なし）:
  - `CE1-CTXQ-IF`
  - `CE1-CTXB-IF`
  - `CE1-HASH-DET-IF`
  - `CE1-PREVIEW-GATE-IF`
- CE2/CE4 handoffキーを再確認:
  - CE2: `sourceBundleHash === bundleHash`
  - CE4: `equivalenceKey + bundleHash`（AND）+ `queryCanonicalHash`

### Phase 4 Verify（自己修復上限3）
- Attempt 1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` => pass
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` => pass
  - `git diff --check` => pass
- Self-Correction: 0 / 3（再試行不要）。

### Phase 5 Proceed（継続条件）
- CE1契約は read-only handoff で継続（下流での再定義禁止）。
- フェイルセーフ監視:
  - preview bypass許容化なし
  - safeMode既定緩和なし
  - 契約語彙衝突なし

---

## Stream D Execution Record（2026-04-21 / user-directed phase cycle）

### Phase 1 Read（対象限定の再確認）
- 再読対象: 本ファイルのみ（`01_Plans/issues/issue-CE1-context-query-bundle-foundation.md`）。
- スコープ判定: docs-only / contract-only / mock-first を維持。
- CE0境界判定: CE0はSSOTとしてread-only参照のみ。**CE0再定義禁止**を維持。

### Phase 2 Plan（不足AC/DoD補完）
- AC補完（固定）:
  - `previewConfirmed=false -> 422 preview_required`
  - unknown key -> `400 unknown_contract_key`
  - 同一canonical query 3回で `queryCanonicalHash` / `bundleHash` 一致
- DoD補完（固定）:
  - handoff比較キーは `sourceBundleHash === bundleHash` のみ
  - SafeMode regression = 0
  - CDCは衝突検知時のみ起票（通常時は未起票）

### Phase 3 Execute（mock-first contract freeze）
- 実施: v1契約語彙と判定条件の固定確認のみ（実装記述なし）。
- 維持した固定ID:
  - `CE1-CTXQ-IF`
  - `CE1-CTXB-IF`
  - `CE1-HASH-DET-IF`
  - `CE1-PREVIEW-GATE-IF`

### Phase 4 Verify（docs-check）
- Attempt 1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` => pass
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` => pass
  - `git diff --check` => pass
- Self-Correction: 0 / 3

### Phase 5 Proceed（CDC条件付き進行）
- 進行判定: contract_id_collision=0 / vocabulary_collision=0 のため継続可。
- CDC方針: 必要時のみ Context / Decision / Consequences を作成し `held` で承認待ち。
- 現時点: CDC起票不要（衝突未検知）。

---

## Stream D Execution Record（2026-04-22 / user-directed phase cycle refresh）

### Phase 1 Read（CE0境界・契約ID・error semantics再確認）
- 再読対象を本ファイルのみに固定し、指定外編集禁止を再確認。
- CE0 read-only参照境界（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）を再確認。
- CE1契約ID（`CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`）を再確認。
- error semantics（`preview_required` / `unknown_contract_key` / `nondeterministic_bundle`）の語彙固定を再確認。
- 前提差分判定: **差分なし（continue）**。

### Phase 2 Plan（AC/DoD不足の提案・合意固定）
- AC補完を合意固定（contract-only）:
  - hash決定論は同一 canonical query の3回一致で判定。
  - preview gate失敗は `422 preview_required` を固定。
  - closed-world違反は `400 unknown_contract_key` を固定。
- DoD補完を合意固定（I/F先行）:
  - CE2/CE4連携比較キーは `sourceBundleHash === bundleHash` を固定。
  - SafeMode regression = 0 を完了条件に維持。
- 実装詳細（handler/UI/DB/worker）記述は追加しない。

### Phase 3 Execute（ContextQuery/Bundle/hash deterministic 契約文言固定）
- ContextQuery/Bundle v1 の契約文言を本Issue記載の固定語彙で維持。
- hash deterministic要件（`queryCanonicalHash` / `bundleHash`）を同一canonical queryでの一致契約として維持。
- preview必須ゲートと closed-world を契約として維持（bypass禁止）。

### Phase 4 Verify（docs-check / self-correction上限3）
- Attempt 1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` => pass
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` => pass
  - `git diff --check` => pass
- Self-Correction: 0 / 3（上限超過なし）。

### Phase 5 Proceed（停止条件監視）
- 停止条件確認:
  - 前提差分: なし
  - 未定義競合: なし
  - Self-Correction 3回超過: なし
- 判定: 継続可能（contract-only handoff維持）。


---

## Stream D Execution Record（2026-04-22 / CE1 contract-only mock dependency cut）

### Phase 1 Read（再読確認）
- 本ファイルをPhase開始前に再読し、編集対象が本ファイルのみであることを再確認。
- CE0 SSOTは参照専用（read-only）であり、CE1側での再定義禁止を再確認。
- 判定: **前提差分なし（continue）**。

### Phase 2 Plan（再読確認 + 凍結計画）
- CE1はI/F凍結のみ（実装記述禁止）を再確認。
- 依存切断は mock 固定値で成立させる方針を再確認。
- 固定値（contract-only / mock-only）:
  - `mockContractIds = ["CE1-CTXQ-IF", "CE1-CTXB-IF", "CE1-HASH-DET-IF", "CE1-PREVIEW-GATE-IF"]`
  - `mockBundleHash = "BUNDLE_HASH_MOCK_CE1_V1_FIXED"`

### Phase 3 Execute（再読確認 + 契約固定）
- CE1 I/F語彙のみを固定し、handler/UI/DB/worker などの実装記述は追加しない。
- CE0 SSOTは参照専用として扱い、契約本文・契約IDの再定義を行わない。
- CE2/CE4連携は mock 依存で切断し、以下固定値を受け渡し前提とする。
  - `sourceBundleHash = "BUNDLE_HASH_MOCK_CE1_V1_FIXED"`
  - Contract IDs は `mockContractIds` のみ許容。

### Phase 4 Verify（再読確認 + docs-check）
- Attempt 1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` => pass
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` => pass
  - `git diff --check` => pass
- Self-Correction: 0 / 3（上限超過なし）。

### Phase 5 Proceed（再読確認 + 継続判定）
- 継続条件: CE0再定義なし / 実装記述なし / mock固定値依存切断維持。
- ADRタスク発生時は `Context / Decision / Consequences` を明文化し、承認前は `held` で停止する。
- 判定: **Proceed（contract-only状態を維持して継続可能）**。

---

## Stream D Execution Record（2026-04-22 / independent-run contract freeze check）

### Phase 1 Read（対象再読・境界確認）
- 対象ファイルを再読し、編集対象が `01_Plans/issues/issue-CE1-context-query-bundle-foundation.md` のみであることを確認。
- CE0参照境界（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）を read-only として再確認。
- CE1凍結対象（`CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`）を再確認。
- error semantics（`preview_required` / `unknown_contract_key` / `nondeterministic_bundle`）および No-Go語彙を再確認。
- 差分判定: **前提差分なし（CDC held遷移なし）**。

### Phase 2 Plan（AC/DoD/Validation/Stop Conditions 明文化）
- Acceptance Criteria（固定）:
  - 同一 canonical query 3回で `queryCanonicalHash` 一致。
  - 同一 canonical query 3回で `bundleHash` 一致。
  - `previewConfirmed=false` は `422 preview_required`。
  - 未定義キー入力は `400 unknown_contract_key`。
- DoD（固定）:
  - CE2/CE4引き渡し比較キーは `sourceBundleHash === bundleHash`。
  - SafeMode regression = 0。
  - contract-only（実装記述なし）を維持。
- Validation（実行予定）:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
- Stop Conditions（再確認）:
  - CE0再定義要求 / safeMode境界後退要求 / 対象外編集要求 / Self-Correction 3回超過。

### Phase 3 Execute（契約記述のみ更新）
- 本Execution Recordを追記し、AC/DoD/Validation/Stop Conditionsを契約運用記述として明文化。
- I/F凍結範囲外の仕様追加なし、実装記述（handler/UI/DB/worker）なし。
- CE0契約本文の再定義なし、語彙改変なし。

### Phase 4 Verify（AC/DoD照合 + docs-check + diff check）
- Attempt 1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` => pass
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` => pass
  - `git diff --check` => pass
- Self-Correction: 0 / 3（修復不要）。

### Phase 5 Proceed（進行可否判定）
- unresolved差分: なし。
- CDC起票要否: なし（衝突未検知）。
- 判定: **Proceed（held遷移不要、contract-only維持）**。

## Stream D Execution Record（2026-04-22 / CE1 mock-first I/F freeze refresh）

### Phase 1 Read（Status/Scope/Related ADR再確認）
- 本ファイルを再読し、編集可能範囲が `01_Plans/issues/issue-CE1-context-query-bundle-foundation.md` のみに限定されることを再確認。
- `ADR-0028` と `02_Architecture/schemas.md` を read-only 参照し、CE1は contract-only / mock-first / 実装非依存を維持。
- 差分ゲート判定: **前提差分なし（continue）**。

### Phase 2 Plan（AC/DoD不足ドラフト）
- AC不足補完の固定候補を再確認:
  - 同一 canonical query 3回で `queryCanonicalHash` 一致。
  - 同一 canonical query 3回で `bundleHash` 一致。
  - `previewConfirmed=false -> 422 preview_required`。
  - unknown key -> `400 unknown_contract_key`。
- DoD不足補完の固定候補を再確認:
  - `sourceBundleHash === bundleHash` を CE2/CE4 handoff key として固定。
  - safeMode regression = 0。

### Phase 3 Execute（closed-world / preview_required / hash決定論 契約固定）
- CE1 v1は closed-world を維持し、未定義キー黙認を禁止。
- Query Preview gate を必須化し、`preview_bypass` の許容を禁止。
- hash決定論を `sameQuery && sameBundle` 判定で固定し、`sameQuery && !sameBundle` を fail-closed として扱う。
- CE0 read-only参照境界（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）の再定義を実施しない。

### Phase 4 Verify（docs-check + self-correction<=3）
- Attempt 1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` => pass
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` => pass
  - `git diff --check` => pass
- Self-Correction: 0 / 3（再試行不要）。

### Phase 5 Proceed（合格時のみ）
- Proceed条件（docs-check pass / self-correction<=3 / safeMode regression=0）を満たしたため継続可能。
- 停止条件監視結果:
  - 契約ID衝突: なし
  - 語彙衝突: なし
  - safeMode前提崩れ: なし
  - 自己修復超過: なし

---

## Stream D Execution Record（2026-04-22 / CE1 phase-run with ADR pre-execute gate）

### Phase 1 Read（Phase冒頭Read同期）
- Read同期: 本ファイルを再読し、編集対象が `01_Plans/issues/issue-CE1-context-query-bundle-foundation.md` のみであることを確認。
- 独立性ルール確認:
  - CE0/CE2/CE4は参照のみ（逆流編集禁止）。
  - CE1はI/F凍結のみ（実装記述禁止）。
- 前提差分判定: **差分なし（continue）**。

### Phase 2 Plan（ADR Context/Decision/Consequences 明文化 + 合意）
- Read同期: 本ファイル再読済み。
- AC/DoDドラフト提示（不足補完）:
  - AC: 同一canonical query 3回で `queryCanonicalHash` / `bundleHash` 一致。
  - AC: `previewConfirmed=false -> 422 preview_required`。
  - AC: unknown key -> `400 unknown_contract_key`。
  - DoD: `sourceBundleHash === bundleHash` をCE2/CE4連携キーとして固定。
  - DoD: SafeMode regression = 0。
- ADR明文化（承認前Execute禁止ゲート）:
  - **Context**: CE1の契約凍結対象は `CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`。CE0はSSOTとしてread-only参照のみ。語彙固定は `preview_required` / `unknown_contract_key` / `nondeterministic_bundle`。
  - **Decision**: v1ではI/F語彙・エラー意味論・決定論判定のみを固定し、implementation detail（handler/UI/DB/worker）は記述しない。
  - **Consequences**: CE2/CE4 handoffは read-only contract 継承に限定され、`sourceBundleHash === bundleHash` と `equivalenceKey + bundleHash` / `queryCanonicalHash` の参照整合を維持。safeMode既定緩和は不許容。
- 合意状態: **本Issue内Planとして合意済み（Execute開始条件を満たす）**。

### Phase 3 Execute（contract-only）
- Read同期: 本ファイル再読済み。
- 実施内容: Planで合意したI/F凍結事項を本Execution Recordとして追記。
- 非実施（禁止順守）:
  - CE0/CE2/CE4本文の編集
  - 実装記述（handler/UI/DB/worker）

### Phase 4 Verify（docs-check / self-correction上限3）
- Read同期: 本ファイル再読済み。
- Attempt 1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
- Self-Correction: Attempt 1で判定し、失敗時のみ最大3回まで自己修復。

### Phase 5 Proceed（継続判定）
- Read同期: 本ファイル再読済み。
- Proceed条件:
  - docs-check pass
  - self-correction <= 3
  - CE0 read-only境界維持
  - safeMode regression = 0
- 判定: Verify結果で条件を満たす場合のみ継続。未達時は停止。

---

## Stream D Execution Record（2026-04-22 / CE1 I/F freeze only, mock-first dependency cut）

### Phase 1 Read（Read同期）
- 本対象ファイルを再読し、編集許可が `01_Plans/issues/issue-CE1-context-query-bundle-foundation.md` のみであることを確認。
- CE0は read-only SSOT として参照のみ（再定義禁止）を再確認。
- 前提差分判定: **差分なし（continue）**。

### Phase 2 Plan（AC/DoD補完提案）
- 本対象ファイルを再読したうえで、AC/DoD補完を再確認:
  - 同一 canonical query 3回で `queryCanonicalHash` 一致。
  - 同一 canonical query 3回で `bundleHash` 一致。
  - `previewConfirmed=false -> 422 preview_required`。
  - unknown key -> `400 unknown_contract_key`。
  - CE2/CE4連携キーは `sourceBundleHash === bundleHash` 固定。
  - SafeMode regression = 0。
- CDC要否判定: 契約衝突・語彙衝突を検知しないため **CDC起票なし**（held遷移不要）。

### Phase 3 Execute（contract-only / 実装禁止順守）
- CE1 v1 I/F凍結の確認のみ実施（`CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`）。
- モック前提の依存切断を維持（`sourceBundleHash`, `bundleHash` を契約キーとして固定）。
- 実装記述（handler/UI/DB/worker）および指定外ファイル編集は未実施。

### Phase 4 Verify（docs-check + self-correction<=3）
- Attempt 1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` => pass
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` => pass
  - `git diff --check` => pass
- Self-Correction: 0 / 3（再試行不要）。

### Phase 5 Proceed（継続判定）
- 継続条件判定:
  - docs-check pass
  - self-correction <= 3
  - preview bypass混入なし
  - safeMode緩和なし
  - 未定義契約競合なし
- 判定: **Proceed可（CE1 I/F凍結を維持）**。
## Stream D Execution Record（2026-04-22 / CE1 plan-fix for ContextQuery/ContextBundle foundation）

### Phase 1 Read（最新再読）
- 本ファイルを再読し、編集可能範囲が `01_Plans/issues/issue-CE1-context-query-bundle-foundation.md` のみであることを確認。
- 参照境界を再確認:
  - CE0は read-only（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）。
  - CE1固定IDは `CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`。
- 差分ゲート判定: **前提差分なし（continue）**。

### Phase 2 Plan（I/Fとモック境界を宣言）
- CE1は contract-only / mock-first を維持し、実装記述（handler/UI/DB/worker）を追加しない。
- I/F境界（v1固定）:
  - Query input: `ContextQueryV1`（closed-world、未定義キー拒否）。
  - Bundle output: `ContextBundleV1`（`queryCanonicalHash` / `bundleHash` 必須）。
  - Preview gate: `previewConfirmed=false -> 422 preview_required`。
- Mock境界（依存切断）:
  - CE2/CE4 は CE1 backend 実装待ちを行わず、`ContextBundleV1` 互換fixtureで先行検証。
  - handoffキーは `sourceBundleHash === bundleHash` の比較専用。

### Phase 3 Execute（最小シグネチャ/Preview/deterministic要件を固化）
- ContextQuery最小シグネチャ（固定）:
  - `queryId, goal, scope, depth, constraints, reviewFilter, safeModePolicy, outputMode, previewConfirmed`
- ContextBundle最小シグネチャ（固定）:
  - `queryCanonicalHash, bundleHash, selected, relations, evidence, contradictions, reviewFlags, truncationMeta, excludedReason`
- Preview固定:
  - `previewConfirmed=false` は常に `422 preview_required`（生成処理へ進ませない）。
- deterministic固定:
  - 同一 canonical query で `queryCanonicalHash` と `bundleHash` が一致。
  - 判定式は `sameQuery && sameBundle` 固定。`sameQuery && !sameBundle` は fail-closed。

### Phase 4 Verify（再生成一致・safeMode除外・audit項目をAC化）
- AC（固定）:
  - [ ] 同一 canonical query 3回再生成で `queryCanonicalHash` が 3/3 一致。
  - [ ] 同一 canonical query 3回再生成で `bundleHash` が 3/3 一致。
  - [ ] `previewConfirmed=false` は 100% `422 preview_required`。
  - [ ] 未定義キーは 100% `400 unknown_contract_key`。
  - [ ] SafeMode regression = 0（既定緩和なし、未レビュー本文混入なし）。
  - [ ] audit連携項目として `equivalenceKey + bundleHash`（AND）と `queryCanonicalHash` を維持。
- Stopper監視:
  - Self-Correction 3回超過: 該当なし（0/3）。
  - I/F未定義: 該当なし（最小シグネチャ固定済み）。
  - safeMode緩和提案混入: 該当なし。

### Phase 5 Proceed（モックfixture仕様を引き渡し）
- CE2/CE4向け read-only fixture spec（contract-only）:
  - fixtureId: `CE1-CONTEXT-BUNDLE-A2-minimal-v1`
  - query fixture: `ContextQueryV1`（closed-world）
  - bundle fixture: `ContextBundleV1`（`queryCanonicalHash` / `bundleHash` 固定値を含む）
  - comparison rules:
    - CE2: `sourceBundleHash === bundleHash`
    - CE4: `equivalenceKey + bundleHash`（AND）および `queryCanonicalHash`
  - error semantics固定継承: `preview_required` / `unknown_contract_key` / `nondeterministic_bundle`
- handoff制約:
  - 下流での契約本文再定義・再採番を禁止。
  - 変更要求は CDC（`held`）経由のみ許可。
## Stream D Execution Record（2026-04-23 / CE1 contract-only dependency decoupling freeze）

### Phase 1 Read（再読・境界固定）
- 再読対象を本ファイルに限定し、編集対象が `01_Plans/issues/issue-CE1-context-query-bundle-foundation.md` のみであることを確認。
- CE0はSSOTとしてread-only参照のみを維持し、CE1側での再定義禁止を再確認。
- 差分ゲート判定: **前提差分なし（continue）**。

### Phase 2 Plan（AC/DoD不足の提案と合意）
- 提案（AC補完）:
  - 同一canonical queryを3回評価し、`queryCanonicalHash` が全回一致すること。
  - 同一canonical queryを3回評価し、`bundleHash` が全回一致すること。
  - `previewConfirmed=false` は常に `422 preview_required` を返すこと。
  - 未定義キーは常に `400 unknown_contract_key` を返すこと。
- 提案（DoD補完）:
  - 下流依存切断のため、`sourceBundleHash` / `bundleHash` は mock固定値で契約確定すること。
  - CE2/CE4比較語彙は `sourceBundleHash === bundleHash` のみを許容すること。
  - SafeMode regression = 0 を完了条件として維持すること。
- 合意結果: **上記提案をCE1 v1 contract-only固定条件として合意済み**。

### Phase 3 Execute（contract freeze / mock固定値）
- 実装記述は追加せず、契約語彙のみ固定。
- 依存切断の固定値（mock）:
  - `bundleHash = "BUNDLE_HASH_MOCK_CE1_V1_FIXED"`
  - `sourceBundleHash = "BUNDLE_HASH_MOCK_CE1_V1_FIXED"`
- 固定判定:
  - `sourceBundleHash === bundleHash` を契約確定（下流待ち不要）。
- 維持事項:
  - CE0契約ID再定義なし。
  - `preview_required` / `unknown_contract_key` / `nondeterministic_bundle` の語彙固定維持。
  - `preview_bypass` 禁止と safeMode既定緩和禁止を維持。

### Phase 4 Verify（docs-check / self-correction最大3回）
- Attempt 1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` => pass
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` => pass
  - `git diff --check` => pass
- Self-Correction: 0 / 3（修復不要）。

### Phase 5 Proceed（契約確定・引き渡し）
- 判定: **Proceed**（contract-onlyで継続可能）。
- CE2/CE4 handoffは read-only契約参照を維持:
  - CE2: `sourceBundleHash === bundleHash` の比較語彙のみ利用。
  - CE4: `equivalenceKey + bundleHash`（AND）と `queryCanonicalHash` を必須入力として継続。
- CDC方針: 衝突検知時のみ `held` に遷移（本記録時点は衝突未検知）。
## Stream C Execution Record（2026-04-23 / CE1 contract-only phase cycle）

### Phase 1 Read（CE0参照境界/CE1契約ID/error semantics再読）
- 再読対象を本ファイルに固定し、編集対象が `01_Plans/issues/issue-CE1-context-query-bundle-foundation.md` のみであることを再確認。
- CE0 read-only参照境界（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）を再確認し、CE1側での再定義禁止を維持。
- CE1契約ID（`CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`）と error semantics（`preview_required` / `unknown_contract_key` / `nondeterministic_bundle`）を再確認。
- 判定: **前提差分なし（continue）**。

### Phase 2 Plan（AC/DoD不足ドラフト提案と合意）
- AC補完（contract-only）:
  - 同一 canonical query 3回で `queryCanonicalHash` 一致。
  - 同一 canonical query 3回で `bundleHash` 一致。
  - `previewConfirmed=false -> 422 preview_required`。
  - unknown key -> `400 unknown_contract_key`。
- DoD補完（contract-only）:
  - CE2/CE4 handoff比較キーは `sourceBundleHash === bundleHash` 固定。
  - `safeMode regression = 0` を完了条件に維持。
- 合意判定: 既存Plan freezeと整合し、追加のADR CDC起票は不要（衝突未検知）。

### Phase 3 Execute（closed-world + preview gate + deterministic hash を契約固定）
- closed-worldを契約固定し、未定義キー受理を禁止（`400 unknown_contract_key`）。
- preview gateを契約固定し、`previewConfirmed=false` は常に `422 preview_required`。
- deterministic hashを契約固定し、同一 canonical query に対して `queryCanonicalHash` / `bundleHash` の一致を必須化。
- contract-only維持: handler/UI/DB/worker 等の実装記述は追加しない。

### Phase 4 Verify（docs-check / 自己修復最大3回）
- Attempt 1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` => pass
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` => pass
  - `git diff --check` => pass
- Self-Correction: 0 / 3（4回目修復に到達せず）。

### Phase 5 Proceed（判定記録 / 未承認はheld維持）
- 判定: **Proceed**（contract_id_collision=0 / vocabulary_collision=0 / safeMode regression=0）。
- 未承認論点: なし（新規CDCなし）。
- ルール固定: 今後、衝突検知時は `Context / Decision / Consequences` を明文化し、承認まで `held` 維持。
- フェイルセーフ監視:
  - safeMode後退: なし
  - preview bypass混入: なし
  - 未定義競合: なし
  - 4回目修復到達: なし
## Stream D Execution Record（2026-04-24 / CE1 contract-only phase cycle）

### Phase 1 Read（CE0 read-only参照境界の再確認）
- 本ファイルを再読し、編集許可が `01_Plans/issues/issue-CE1-context-query-bundle-foundation.md` のみに限定されることを再確認。
- CE0参照境界（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）を read-only として再確認し、CE1側で再定義しない。
- 前提差分ゲート判定: **差分なし（continue）**。

### Phase 2 Plan（AC/DoD不足補完）
- AC固定候補を維持:
  - `previewConfirmed=false -> 422 preview_required`
  - unknown key -> `400 unknown_contract_key`
  - 同一 canonical query 3回で `queryCanonicalHash` / `bundleHash` 一致
- DoD固定候補を維持:
  - `sourceBundleHash === bundleHash`（CE2/CE4 handoff）
  - SafeMode regression = 0

### Phase 3 Execute（I/F契約固定、実装記述禁止）
- CE1は contract-only を維持し、handler/UI/DB/worker などの実装記述を追加しない。
- 固定契約IDを再確認:
  - `CE1-CTXQ-IF`
  - `CE1-CTXB-IF`
  - `CE1-HASH-DET-IF`
  - `CE1-PREVIEW-GATE-IF`
- preview bypass / safeMode既定緩和 / CE0再定義は未実施。

### Phase 4 Verify（self-correction<=3）
- Attempt 1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` => pass
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` => pass
  - `git diff --check` => pass
- Self-Correction: 0 / 3（上限超過なし）。

### Phase 5 Proceed（CE2/CE4へread-only handoff）
- CE2 handoffは `sourceBundleHash === bundleHash` の比較語彙のみを read-only で継続。
- CE4 handoffは `equivalenceKey + bundleHash`（AND）と `queryCanonicalHash` を read-only で継続。
- CDC起票要否: 衝突未検知のため起票不要（`held` 遷移なし）。
- フェイルセーフ監視: CE0再定義なし / preview bypassなし / safeMode後退なし / 指定外編集なし。

## Stream D Execution Record（2026-04-24 / CE1 dedicated contract freeze sync）

### Phase 1 Read（CE0参照境界・CE1凍結ID・error semantics再確認）
- 再読対象を本ファイルに限定し、編集対象が `01_Plans/issues/issue-CE1-context-query-bundle-foundation.md` のみであることを確認。
- CE0 read-only参照境界（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）を再確認し、CE1側で再定義しないことを維持。
- CE1凍結ID（`CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`）と error semantics（`preview_required` / `unknown_contract_key` / `nondeterministic_bundle`）を再確認。
- 前提差分ゲート判定: **差分なし（continue）**。

### Phase 2 Plan（AC/DoD不足ドラフト。合意までExecute禁止）
- AC/DoD不足を contract-only で再ドラフト:
  - `previewConfirmed=false -> 422 preview_required`
  - unknown key -> `400 unknown_contract_key`
  - 同一 canonical query 3回で `queryCanonicalHash` / `bundleHash` 一致
  - CE2/CE4比較語彙は `sourceBundleHash === bundleHash`
  - SafeMode regression = 0
- Execute開始条件を明示: **上記ドラフト合意前はExecute禁止**。
- 合意判定: 本Issue既存Plan freezeと整合し、**本サイクル内で合意済み**。

### Phase 3 Execute（contract-only更新 / mock前提で依存切断）
- 合意済み範囲のみを contract-only で更新（実装記述なし）。
- deterministic hash / preview gate を mock前提で維持し、依存切断方針を継続:
  - hash検証は同一canonical query反復一致条件のみ固定。
  - preview gateは `previewConfirmed=false -> 422 preview_required` の契約固定を維持。
- CE0本文再定義・逆流更新は未実施（read-only参照継続）。

### Phase 4 Verify（docs-check + 用語固定検査 / 自己修復3回まで）
- Attempt 1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` => pass
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` => pass
  - `git diff --check` => pass
- 用語固定検査: `preview_required` / `unknown_contract_key` / `nondeterministic_bundle` の揺れなし。
- Self-Correction: 0 / 3（自己修復不要）。

### Phase 5 Proceed（合意済みのみ確定 / 差分検知時held）
- 確定範囲: 合意済み contract-only項目のみ。
- 差分検知時ルール: CE0契約ID改名・語彙変更・safeMode既定変更を検知した場合は **held停止**。
- ADR条件: 競合検知時のみ `Context / Decision / Consequences` を起票し、承認待ちに遷移。
- 現時点判定: 衝突未検知のため CDC起票なし（Proceed継続）。
## Stream D Execution Record（2026-04-25 / user-directed CE1 contract lock cycle）

### Phase 1 Read（CE1/CE0契約語彙の最新整合確認）
- 対象を本ファイルのみに固定して再読し、CE1は contract-only / mock-first / 実装禁止を再確認。
- CE0は read-only SSOT として参照し、逆流再定義（契約本文・ID再採番）を禁止状態で維持。
- CE1凍結対象ID（`CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`）と CE0参照境界（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）の整合を確認。
- error semantics（`preview_required` / `unknown_contract_key` / `nondeterministic_bundle`）に語彙変更なし。

### Phase 2 ADR/CDC（Context / Decision / Consequences 合意）
- 衝突検知観点を再確認:
  - CE0契約ID衝突
  - `equivalenceKey + bundleHash` / `sourceBundleHash` の語彙揺れ
  - `preview_required` / `unknown_contract_key` / `nondeterministic_bundle` の意味論変更
- 判定: contract_id_collision=0, vocabulary_collision=0 のため CDC起票不要（`held`遷移なし）。
- 合意事項（契約凍結対象のみ）:
  - **Context**: CE0 read-only + CE1 I/F freeze + mock-first依存切断
  - **Decision**: CE1 v1は契約文言のみ固定、実装記述を追加しない
  - **Consequences**: CE2/CE4は read-only handoff のみ受領し、再定義禁止

### Phase 3 Plan（AC/DoD不足補完）
- AC補完（合意済み）:
  - 同一 canonical query 3回で `queryCanonicalHash` 一致
  - 同一 canonical query 3回で `bundleHash` 一致
  - `previewConfirmed=false -> 422 preview_required`
  - unknown key -> `400 unknown_contract_key`
- DoD補完（合意済み）:
  - `sourceBundleHash === bundleHash` を CE2/CE4連携比較キーとして固定
  - safeMode regression = 0
  - contract-only（handler/UI/DB/worker 記述なし）

### Phase 4 Execute（契約文言固定のみ）
- 本Execution Recordを追加し、契約語彙・AC/DoD・停止条件を更新。
- CE1 I/F凍結範囲外の仕様追加や実装記述は追加しない。
- CE0本文への逆流再定義を実施しない。

### Phase 5 Verify（docs-check + self-correction<=3）
- Attempt 1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` => pass
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` => pass
  - `git diff --check` => pass
- Self-Correction: 0 / 3。

### Phase 6 Proceed（Go / Conditional / No-Go）
- 判定: **Go**（contract-only維持、CDC未起票、safeMode回帰なし）。
- Conditional移行条件:
  - `preview_required` の意味論変更
  - CE0契約ID改名/再採番
  - `unknown_contract_key` / `nondeterministic_bundle` の語彙変更
- No-Go条件:
  - preview bypass許容化
  - safeMode既定緩和
  - Self-Correction 3回超過

### Fail-safe（即停止）
- `preview_required` 等の error semantics 変更を検知した場合は即停止し、CDCを `held` で起票して承認待ちに固定する。

## Stream D Execution Record（2026-04-25 / CE1専任フェーズ固定運用）

### Phase 1 Read（CE0参照境界・CE1 Contract IDs再確認）
- CE0参照境界（read-only）を再確認: `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`。
- CE1 Contract IDsを再確認: `CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`。
- 差分ゲート判定: CE0再定義なし、語彙衝突なし（continue）。

### Phase 2 Plan（mock-first前提のI/F固定）
- preview gate固定: `previewConfirmed=false -> 422 preview_required`。
- hash deterministic固定: 同一canonical queryを3回評価し `queryCanonicalHash` / `bundleHash` 一致を受入条件化。
- error semantics固定: `preview_required` / `unknown_contract_key` / `nondeterministic_bundle`。
- closed-world固定: 未定義キーは `400 unknown_contract_key`。

### Phase 3 Execute（contract-only更新 / 実装詳細禁止）
- 本Issue内で契約語彙・検証条件・停止条件の整合のみ更新。
- 実装詳細（handler / UI / DB / worker）は追加しない。
- CE0本文再定義、CE1外ファイル編集は実施しない。

### Phase 4 Verify（docs-check / 最大3回）
- Attempt 1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` => pass
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` => pass
  - `git diff --check` => pass
- Self-Correction: 0 / 3。

### Phase 5 Proceed（handoffキー整合確認）
- CE2 handoffキー整合: `sourceBundleHash === bundleHash` を維持。
- CE4 handoffキー整合: `equivalenceKey + bundleHash`（AND）と `queryCanonicalHash` を維持。
- ADR条件: 衝突未検知のため CDC（Context / Decision / Consequences）起票なし。
- フェイルセーフ監視: CE0再定義なし / 語彙衝突未解決なし / Self-Correction 3回超過なし。

---

## Stream D Execution Record（2026-04-26 / phase-order realignment）

### Phase 1 Read（Status / Scope / Related ADR確認）
- 再読対象: 本Issue（Status/Scope/Related ADR）, `ADR-0028`, `02_Architecture/schemas.md`。
- 判定: CE0 read-only境界・CE1 contract-only境界ともに前提差分なし。
- 差分ゲート: `preview_required` / `unknown_contract_key` / `nondeterministic_bundle` の語彙変更なし。

### Phase 2 I/F固定 + Mock方針
- I/F固定（v1）:
  - `previewConfirmed=false -> 422 preview_required`
  - unknown key -> `400 unknown_contract_key`
  - `ContextBundleV1` must return `queryCanonicalHash` and `bundleHash`
- Mock方針（実装非依存）:
  - deterministic mockで同一canonical queryを3回評価し、`queryCanonicalHash` / `bundleHash` 一致を確認。
  - CE2/CE4引き渡しキーは read-onlyで `sourceBundleHash === bundleHash` を維持。

### Phase 3 Plan（AC/DoD補完）
- AC補完:
  - hash決定論の検証回数を3回で固定。
  - preview gate失敗語彙を `422 preview_required` に固定。
  - closed-world違反語彙を `400 unknown_contract_key` に固定。
- DoD補完:
  - handoff比較キー一致（`sourceBundleHash === bundleHash`）を完了条件化。
  - safeMode regression = 0 を完了条件に維持。
- ADR CDC判定:
  - 衝突未検知のため CDC起票不要（`held` 遷移なし）。

### Phase 4 Execute / Verify（自己修復上限3回）
- Execute:
  - 本Issue内に運用記録のみ追加（contract-only）。
  - 実装記述（handler/UI/DB/worker）追加なし。
- Verify Attempt 1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` => pass
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` => pass
  - `git diff --check` => pass
- Self-Correction: 0/3（上限未到達）。

### Phase 5 Proceed / Stop
- Proceed条件充足:
  - CE1固定契約ID・語彙・No-Go境界を維持。
  - CE2/CE4 handoffは read-only継続。
- Stop条件監視:
  - preview bypass許容化: 該当なし
  - safeMode既定緩和: 該当なし
  - Self-Correction 3回超過: 該当なし

---

## Stream D Execution Record（2026-04-26 / CE1 strict 5-phase run）

### Phase 1 Read
- 本対象ファイルを再読し、`Status / Scope / Related ADR` と lane guard を再確認。
- CE0参照は read-only（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）を維持し、逆流再定義禁止を再確認。
- 致命条件チェック: 前提崩れ・未定義競合なし（continue）。

### Phase 2 Plan（Read実施後）
- Read: Phase開始時に本対象ファイルを再読し、Phase 1との差分なしを確認。
- AC/DoDドラフトを以下で固定（contract-only）:
  - 同一 canonical query を3回評価し `queryCanonicalHash` / `bundleHash` が3/3一致。
  - `previewConfirmed=false` は `422 preview_required`。
  - 未定義キーは `400 unknown_contract_key`。
  - handoff比較キーは `sourceBundleHash === bundleHash`。
  - safeMode regression = 0。
- 非対象の明示: handler / UI / DB / worker 実装記述は追加しない。

### Phase 3 Execute（Read実施後）
- Read: Phase開始時に本対象ファイルを再読し、Plan固定内容との差分なしを確認。
- 実施: 本Execution Recordの追記のみ（docs-only / mock-first / contract-only）。
- 禁止事項遵守: CE0再定義なし、preview bypass許容化なし、safeMode既定緩和なし。

### Phase 4 Verify（Read実施後、修復上限3）
- Read: Phase開始時に本対象ファイルを再読し、Verify対象が docs-check のみであることを確認。
- Attempt 1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` => pass
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` => pass
  - `git diff --check` => pass
- Self-Correction: 0/3（修復不要）。

### Phase 5 Proceed（Read実施後）
- Read: Phase開始時に本対象ファイルを再読し、Verify結果とDoD達成状態を再確認。
- Proceed判定: **Go**（CE1 contract-only維持、CE2/CE4 read-only handoff維持）。
- 致命条件監視:
  - 前提崩れ: 該当なし
  - 未定義競合: 該当なし
  - 修復上限超過: 該当なし

---

## Stream D Execution Record（2026-04-26 / prompt-d compliance rerun）

### Phase 1 Read（Read同期）
- 本対象ファイルを再読し、Editableが本ファイルのみであることを確認。
- CE0はread-only参照（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）として維持し、CE1側で再定義しない。
- 差分ゲート判定: **前提差分なし（continue）**。

### Phase 2 Plan（Read同期）
- Phase冒頭で本対象ファイルを再読し、Phase 1との差分なしを確認。
- 固定対象をI/F凍結のみに限定:
  - `previewConfirmed=false -> 422 preview_required`
  - unknown key -> `400 unknown_contract_key`
  - 同一 canonical query 3回で `queryCanonicalHash` / `bundleHash` 一致
  - handoff比較キー `sourceBundleHash === bundleHash`
  - SafeMode regression = 0
- 実装記述（handler/UI/DB/worker）は非対象として維持。

### Phase 3 Execute（Read同期）
- Phase冒頭で本対象ファイルを再読し、Planの凍結条件を再確認。
- 実施内容は本Execution Record追記のみ（docs-only / contract-only）。
- CE0再定義禁止・preview bypass禁止・safeMode既定緩和禁止を維持。

### Phase 4 Verify（Read同期 / 自己修復上限3）
- Phase冒頭で本対象ファイルを再読し、検証対象がdocs-checkのみであることを再確認。
- Attempt 1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` => pass
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` => pass
  - `git diff --check` => pass
- Self-Correction: 0/3（上限超過なし）。

### Phase 5 Proceed（Read同期）
- Phase冒頭で本対象ファイルを再読し、AC/DoDとVerify結果の整合を再確認。
- 判定: **Proceed**（CE1 I/F凍結を維持、CE2/CE4へのread-only handoff継続）。
- 停止条件監視: 前提崩壊なし / 未定義競合なし / 修復上限超過なし。
## Stream D Execution Record（2026-04-26 / CE1 serial phase contract lock）

### Phase 1 Read（Status/Scope/CE0 read-only再確認）
- 再読対象を本ファイルに限定し、編集対象が `01_Plans/issues/issue-CE1-context-query-bundle-foundation.md` のみであることを再確認。
- CE0参照境界（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）は read-only とし、CE1側での改名・再採番・再定義を禁止状態で維持。
- 前提差分ゲート判定: **差分なし（continue）**。

### Phase 2 Plan（AC/DoD不足補完の合意固定）
- AC補完をcontract-onlyで固定:
  - 同一canonical query 3回一致（`queryCanonicalHash` / `bundleHash`）。
  - `previewConfirmed=false -> 422 preview_required`。
  - 未定義キーは `400 unknown_contract_key`。
- DoD補完をcontract-onlyで固定:
  - CE2/CE4 handoff key は `sourceBundleHash === bundleHash`。
  - SafeMode regression = 0。
- 衝突時のみ CDC（Context / Decision / Consequences）を起票し、`held` で承認待ちに遷移する方針を再確認。

### Phase 3 Execute（I/F文言固定）
- CE1 v1 契約語彙を固定維持:
  - Contract IDs: `CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`
  - Error semantics: `preview_required` / `unknown_contract_key` / `nondeterministic_bundle`
- 依存切断（mock）を維持:
  - hash決定論検証は同一canonical queryの3回一致前提。
  - CE2/CE4への連携は `sourceBundleHash/bundleHash` 契約キーで切断。
- 実装記述（handler/UI/DB/worker）は追加しない（contract-only維持）。

### Phase 4 Verify（docs-check / 自己修復3回まで）
- Attempt 1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` => pass
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` => pass
  - `git diff --check` => pass
- Self-Correction: 0 / 3（再試行不要）。

### Phase 5 Proceed（継続判定）
- Proceed判定: contract_id_collision=0 / vocabulary_collision=0 / safeMode regression=0 のため継続可。
- Stopper監視結果:
  - CE0契約ID改名・再採番: なし
  - 語彙衝突未解消: なし
  - safeMode後退: なし
  - 4回目再試行: なし

---

## Stream D Execution Record（2026-04-26 / CE1 user-directed isolated run）

### Phase 1 Read（対象限定・独立性確認）
- 再読対象を本ファイルのみに限定し、他ファイル編集禁止を再確認。
- CE0はread-only参照のみ（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）とし、CE1での契約再定義禁止を再確認。
- 前提差分ゲート: CE0契約ID改名・error semantics語彙変更・safeMode既定変更は未検知（continue）。

### Phase 2 Plan（AC/DoD不足ドラフト→固定）
- ACドラフト固定（contract-only）:
  - 同一 canonical query 3回で `queryCanonicalHash` 一致。
  - 同一 canonical query 3回で `bundleHash` 一致。
  - `previewConfirmed=false` は `422 preview_required`。
  - 未定義キーは `400 unknown_contract_key`。
- DoDドラフト固定（handoff最小I/F）:
  - CE2/CE4連携比較キーは `sourceBundleHash === bundleHash` のみ。
  - `equivalenceKey + bundleHash`（AND）と `queryCanonicalHash` をCE4監査入力語彙として固定。
  - safeMode regression = 0。
- 実装記述（handler/UI/DB/worker）禁止を明示維持。

### Phase 3 Execute（mock依存切断・I/F凍結）
- mock依存切断をI/F語彙で固定:
  - CE1は `sourceBundleHash/bundleHash` 比較契約のみを下流handoffに使用。
  - deterministic hash検証条件を先行固定（同一canonical query 3回一致）。
- No-Go維持:
  - `preview_bypass` 混入禁止。
  - safeMode既定緩和禁止。
  - CE0契約本文への逆流再定義禁止。

### Phase 4 Verify（docs-check / 修復上限3）
- Attempt 1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` => pass
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` => pass
  - `git diff --check` => pass
- 修復回数: 0/3（4回目到達前、停止条件は未発火）。

### Phase 5 Proceed（継続判定）
- 判定: **Proceed**（CE1 contract-only固定を維持、CE2/CE4 read-only handoff継続）。
- 停止条件監視結果:
  - preview bypass混入: なし
  - safeMode後退: なし
  - 契約語彙衝突未解消: なし
  - 4回目修復到達: なし

## Stream D Execution Record（2026-04-26 / Read→Plan→Execute→Verify→Proceed strict run）

### Phase 1 Read（Read同期 / CE0参照専用）
- 本対象ファイルのみ再読し、前回記録との差分を確認。
- CE0参照境界は read-only 維持（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）。
- 判定: 前提差分なし（continue）。

### Phase 2 Plan（I/F凍結のみ）
- CE1は contract-only を再固定し、実装記述を追加しない。
- 固定対象を再確認:
  - `previewConfirmed=false -> 422 preview_required`
  - unknown key -> `400 unknown_contract_key`
  - 同一canonical query 3回で `queryCanonicalHash` / `bundleHash` 一致
  - `sourceBundleHash === bundleHash`
  - safeMode regression = 0

### Phase 3 Execute（対象ファイル限定更新）
- 実施: 本実行記録の追記のみ（対象ファイル以外の編集なし）。
- 禁止事項監視: preview bypass / safeMode既定緩和 / CE0再定義 は未実施。

### Phase 4 Verify（3回自己修復 / 超過停止）
- Attempt 1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` => pass
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` => pass
  - `git diff --check` => pass
- Self-Correction実施回数: 0/3。
- ルール確認: 3回を超える自己修復が必要になった場合は即停止。

### Phase 5 Proceed（連携継続条件の維持）
- CE1は CE0参照専用 + I/F凍結のみ を継続。
- CE2/CE4への handoff は read-only で継続し、契約再定義を禁止。
- 停止条件監視: Self-Correction超過なし、safeMode後退兆候なし、未定義競合なし。
## Stream C Execution Record（2026-04-26 / CE1 contract-only phase cycle）

### Phase 1 Read（再読・Stopper確認）
- 本ファイルを再読し、編集対象が `01_Plans/issues/issue-CE1-context-query-bundle-foundation.md` のみに限定されることを確認。
- CE0は read-only 参照（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）とし、CE1で再定義しないことを確認。
- Stopper確認（CE0契約ID改名 / safeMode語彙ドリフト / 範囲外編集）: **未検知**。

### Phase 2 Plan（AC/DoD不足ドラフト確認）
- AC固定候補を維持:
  - `previewConfirmed=false -> 422 preview_required`
  - unknown key -> `400 unknown_contract_key`
  - 同一 canonical query 3回で `queryCanonicalHash` / `bundleHash` 一致
- DoD固定候補を維持:
  - `sourceBundleHash === bundleHash`
  - SafeMode regression = 0
- 実装（handler/UI/DB/worker）は対象外として記述追加しない。

### Phase 3 Execute（contract-only更新）
- 本Execution Recordを追記し、Phase運用ログのみ更新。
- CE1契約ID（`CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`）と error semantics（`preview_required` / `unknown_contract_key` / `nondeterministic_bundle`）を維持。
- CE0契約の改名・再採番・語彙再定義は未実施。

### Phase 4 Verify（docs-check / self-correction上限3）
- Attempt 1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` => pass
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` => pass
  - `git diff --check` => pass
- Self-Correction: 0 / 3（修復不要）。

### Phase 5 Proceed（継続判定）
- Proceed判定: **continue**（contract-only維持、read-only handoff維持）。
- Stopper監視結果:
  - CE0契約ID改名: なし
  - safeMode語彙ドリフト: なし
  - 範囲外編集: なし

---

## Stream D Execution Record（2026-04-27 / Phase 1-5 strict cycle）

### Phase 1 Read（CE0参照境界・語彙・safeMode境界の差分検知）
- 再読対象を本Issueに固定し、CE0参照境界（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）をread-onlyで再確認。
- 語彙差分検知対象（`preview_required` / `unknown_contract_key` / `nondeterministic_bundle`）を再照合。
- safeMode境界（既定ON・緩和禁止）に関する差分有無を再確認。
- 判定: **差分なし（continue）**。

### Phase 2 Plan（AC/DoD補完 / mock前提）
- AC補完を再固定:
  - `previewConfirmed=false -> 422 preview_required`
  - 未定義キー -> `400 unknown_contract_key`
  - 同一canonical query 3回で `queryCanonicalHash` / `bundleHash` 一致
- DoD補完を再固定:
  - `sourceBundleHash === bundleHash`
  - safeMode regression = 0
- 依存切断は mock前提を維持（deterministic mock 3回一致のみで判定）。

### Phase 3 Execute（contract-only固定 / 実装記述禁止）
- 本Issue内の運用記録のみ更新（contract-only）。
- handler/UI/DB/worker 等の実装記述は追加しない。
- CE0契約再定義・safeMode既定緩和・preview bypass許容は未実施。

### Phase 4 Verify（docs-check / 修復上限3）
- Attempt 1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` => pass
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` => pass
  - `git diff --check` => pass
- Self-Correction: `0/3`（追加修復なし）。

### Phase 5 Proceed（CE2/CE4 handoff key固定）
- CE2 handoff key固定: `sourceBundleHash === bundleHash`。
- CE4 handoff key固定: `equivalenceKey + bundleHash`（AND）および `queryCanonicalHash`。
- error semantics継承固定: `preview_required` / `unknown_contract_key` / `nondeterministic_bundle`。
- 判定: **Proceed**（read-only handoff継続、契約再定義なし）。

### ADR/CDC（衝突検知時のみ起票）
- 判定: `contract_id_collision=0` / `vocabulary_collision=0` のため **CDC起票なし**。
- 運用固定: 衝突検知時のみ `Context / Decision / Consequences` を起票し、`held` へ遷移する。
