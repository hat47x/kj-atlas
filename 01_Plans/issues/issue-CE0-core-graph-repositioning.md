# Issue Draft: CE0 Core Graph Repositioning（Stream D / CE契約群 / contract-only planning）

- Type: Process
- Status: Done
- Priority: P1
- Owner: Stream D（CE契約群）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Editable: `issue-CE0-core-graph-repositioning.md` のみ
- Related Backlog: `CE-0`
- Related ADR/Spec: `ADR-0028`, `ADR-0039`, `02_Architecture/schemas.md`
- Dependencies: `01_Plans/issues/issue-CE0-contract-freeze.md`（Done 2026-06-20）
- Verification: `docs-check`

## Resolution 2026-06-20

CE0 Core Graph repositioning is Done. Dependencies resolved:
- CE0-contract-freeze → Done (hold conditions cleared per ADR-0039)
- Graph vocabulary fixed: `WorkingGraph` / `ContextProjectionGraph` / `ConsensusGraph`
- `Core Graph` legacy alias preserved for history only
- Frontend tests: 4 passed (2026-06-15)
- Frontend CE0 contract: `ce0_core_graph_repositioning.test.ts` validates boundaries

## Current Canonical Summary 2026-06-15

This section is the current readable handoff point for CE0 Core Graph repositioning. Older execution records below are retained for audit history, but new work should start from this summary and the canonical references listed here.

### Purpose

CE0 fixes the graph responsibility boundary before downstream implementation work expands it. The issue is contract-only: it defines how working data, context projection, and consensus state are separated, and it prevents direct consensus writes, automatic application, review auto-promotion, and SafeMode relaxation.

### Canonical Vocabulary

- `WorkingGraph`: exploration and work-in-progress surface for humans, agents, and roles.
- `ContextProjectionGraph`: read-only projection surface used to build `ContextBundle` outputs.
- `ConsensusGraph`: the canonical graph term for approved integrated state.
- `Core Graph`: legacy/read-only explanatory alias only. It must not be reintroduced as the canonical product or schema term.

### Canonical Contract

- Contract references:
  - `02_Architecture/architecture.md` section `7A. CE-0`
  - `02_Architecture/schemas.md` section `1.1 CE0 Contract Freeze`
  - `01_Plans/issues/issue-CE0-contract-freeze.md`
- Contract IDs are read-only references:
  - `CE0-CTX-IF`
  - `CE0-SAFEMODE-IF`
  - `CE0-REVIEW-IF`
  - `CG-01..05`
- Allowed transition:
  - `WorkingGraph -> ConsensusGraph` only through `patch + approval`.
  - `WorkingGraph -> ContextProjectionGraph` only as read-only projection, not persistent update.
- No-Go canonical IDs:
  - `preview_bypass`
  - `consensus_direct_write`
  - `auto_apply_or_publish`
  - `ai_review_auto_promotion`
  - `safemode_default_relaxation`
- SafeMode boundary:
  - safeMode default remains ON.
  - `allowUnreviewedText=false` remains the protected default.
  - Graph repositioning must not relax SafeMode or make unreviewed text eligible for automatic AI input.

### Current Completion Assessment

| Item | Result | Evidence |
| --- | --- | --- |
| Graph vocabulary fixed | Pass | `WorkingGraph`, `ContextProjectionGraph`, `ConsensusGraph` are canonical; `Core Graph` is legacy alias only |
| Allowed transition fixed | Pass | `WorkingGraph -> ConsensusGraph` requires `patch + approval` |
| Direct write and auto-apply blocked | Pass | `consensus_direct_write` and `auto_apply_or_publish` remain No-Go IDs |
| Review auto-promotion blocked | Pass | `CE0-REVIEW-IF` keeps `human_reviewed` promotion human-owned |
| SafeMode boundary preserved | Pass | `CE0-SAFEMODE-IF`, safeMode default ON, and `allowUnreviewedText=false` remain unchanged |
| Implementation approval | Not granted | This issue does not authorize UI, API, worker, storage, or migration changes |
| Full product release readiness | Not granted | CE0 graph readiness does not resolve product-value gates, HIL/FB approvals, Compose evidence, or final release approval |

### Validation Evidence

- 2026-06-15 frontend CE0 graph contract: `npm run test -- src/domain/ce0_core_graph_repositioning.test.ts` -> 4 passed.
- 2026-06-15 planning metadata: `validate_active_issue_memos.py` -> pass.
- 2026-06-15 vocabulary trace: `rg` confirmed the current summary contains `WorkingGraph`, `ContextProjectionGraph`, `ConsensusGraph`, `patch + approval`, the No-Go canonical IDs, and `allowUnreviewedText=false`.

### Allowed Next Work

- Use this issue as a read-only contract handoff for CE1/CE2/CE4 planning and mock-first validation.
- Treat new terms, aliases, or transition shortcuts as drift unless an ADR explicitly changes the contract.
- Record any request for direct write, auto-apply, auto-publish, AI review promotion, SafeMode relaxation, or `Core Graph` re-canonicalization as `held`.
- Keep implementation work in a separate issue or PR with explicit validation evidence that it consumes these boundaries without redefining them.

### Recommended Closure Path

CE0 Core Graph repositioning can move toward closeout when these are recorded together:

1. Current-main checks confirm no drift in `architecture.md`, `schemas.md`, and `issue-CE0-contract-freeze.md`.
2. CE1/CE2/CE4 references use `ConsensusGraph` and the canonical No-Go IDs without introducing aliases.
3. Implementation-facing work has separate evidence that no direct write, auto-apply, auto-publish, review auto-promotion, or SafeMode relaxation path exists.
4. `PRODUCT-QA-01` and `MVP-EXIT-01` continue to classify this as contract readiness only, not release approval.

## Stream A Phase 1 Metadata Snapshot（2026-05-18）

| Issue | Status | Priority | Depends | Blockers | Delta vs prior run |
|---|---|---|---|---|---|
| HIL-RS-01 parent plan | In Progress | P1 | HIL-RS-01-A1, HIL-RS-02-A1 | `pendingDecisionQueueCount>0` | none |
| HIL-RS-01-A1 minimum I/F | In Progress | P1 | none | human approval pending | none |
| HIL-RS-02-A1 governance hardening | In Progress | P1 | HIL-RS-01-A1 freeze values | GOV exception held | none |
| CE0 contract freeze | Open | P1 | HIL-RS-01-A1 freeze vocabulary (read-only) | approval record pending | none |
| CE0 core-graph repositioning | Open | P1 | CE0 contract freeze | held items unresolved | none |

## Stream A Phase 2 ADR Clarification（Context / Decision / Consequences）

### Context
- Stream A の最短クリティカルパスは **A1契約凍結 → RS-02-A1統治硬化 → CE0 read-only handoff固定**。
- 承認待ち項目（Pending/held）が残る状態での下流着手は、`Pending bypass` と同義になり統治契約違反になる。

### Decision
- 依存グラフを以下に固定する（再定義禁止）。
  - `HIL-RS-01-A1` → `HIL-RS-02-A1` → `HIL-RS-01(parent Proceed Go)`
  - `HIL-RS-01-A1` → `CE0-contract-freeze` → `CE0-core-graph-repositioning`
- 要承認事項を明示し、承認前は `Proceed=Hold` を維持する。
  - `Approval Record`
  - `HIL-RS-02-GOV-EXCEPTION-01`

### Consequences
- Open化条件（Draft→Open）は「固定キーdrift=0 かつ 要承認事項がissue本文に在庫化済み」である。
- Go条件（Open→In Progress/Done）は `a1Status=="Done" && pendingDecisionQueueCount==0` を満たすまで禁止。
- 非互換変更要求は将来版隔離（`future-version backlog`）とし、現行凍結契約には混入させない。

## Stream A Phase 3 Contract Freeze Draft（Minimum I/F + Mock boundary）
- Minimum Input: `freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `safeModeDefault`, `safeModeBoundary`, `pendingDecisionQueueCount`, `approvalRecord`.
- Minimum Output: `decision(Proceed|Hold|Stop)`, `executeAllowed`, `reasonCodes`, `requiredHumanActions`, `auditEventRef`.
- Error surface: `NOGO_CONTRACT_DRIFT`, `NOGO_SAFE_MODE_REGRESSION`, `NOGO_OVERRIDE_POLICY_REGRESSION`, `HOLD_PENDING_QUEUE`.
- Audit event required fields: `timestamp`, `actor`, `phase`, `inputSnapshot`, `gateResult`, `reason`, `nextAction`.
- Mock boundary（UI先行可能範囲）: `decision/executeAllowed/reasonCodes` まで。`Pending -> Approved/Rejected` の実遷移確定は不可。
- Non-compatible change policy: 新規遷移・新規固定キー・承認主体変更は `future-version` に隔離。

## Stream A Phase 4-6 Execute / Verify / Proceed Rule（2026-05-18 fixed）
- Execute: AC/DoD と相互リンク整備のみ（docs-only, contract-only）。
- Verify command set: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` / `git diff --check`.
- Self-correction cap: 最大3回。4回目相当は `Stop`。
- Proceed output partition:
  - **完了**: fixedKeyDrift=0 かつ pendingDecisionQueueCount=0 を満たしたissue
  - **要承認**: Pending/held が残るissue
  - **保留**: 依存解決待ちでOpen化条件未達のissue

## Lane guard

## Stream D latest run（2026-05-06 / CE0 Core Graph repositioning freeze sync）

### Phase 1 Read
- `working` / `context_projection` / `consensus` の責務境界と CE0 canonical No-Go 5 IDs を再確認。
- 現行schema境界（`02_Architecture/schemas.md` CE0/CE1節）との整合を確認。

### Phase 2 Plan
- Contract-first で遷移規則を固定：許可は `working -> consensus` の `patch+approval` のみ。
- 必須属性・互換ルールを固定：proposal-only、direct write禁止、safeMode既定後退禁止。

### Phase 3 Execute
- mock前提で A2 実行可能条件を整備：Query Preview 必須、auto-apply/auto-publish 経路なし。
- 実装コード変更は行わず、契約文面のみ更新。

### Phase 4 Verify
- 下流実装に必要なシグネチャ参照を生成：`ContextQueryV1`、`ContextBundleV1`、`ProposalPatchV1`、`AuditEventV1`。
- 停止条件監視結果：schema破壊変更なし、互換性喪失なし、他ストリーム領域編集なし。

### Phase 5 Proceed
- 判定: **Contract Freeze Declared（CE0 Core Graph repositioning）**。
- 以降の変更は `held` 承認フローを経るまで凍結。

- CE0契約IDの再定義禁止（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）。
- Core Graph責務境界の**契約固定のみ**を扱う（実装禁止）。
- 未承認決定は `held` 扱いで確定しない。
- `role / transition / no-go` 語彙は本Issueで固定し、同義語への置換や拡張定義を禁止。
- 強制ワークフローは `Read同期 → Plan → Execute → Verify → Proceed`。
- **各Phase開始時に必ずReadを実施**し、直前Phaseとの差分有無（語彙・禁止事項・SafeMode境界）を確認してから進行する。

## Read同期（role / transition / no-go語彙確認）
### Read同期スナップショット
- Contract ID: CE0契約ID群を参照のみで利用（再定義禁止）
- No-Go語彙（CE0 canonical 5 IDs）: `preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`
- Scope: graph role/transition/audit 契約固定のみ

### Graph role I/F（固定）
- `working`: 編集作業領域
- `context_projection`: read-only投影
- `consensus`: 承認済み合意領域

### Transition / No-Go（固定）
- 許可: `working -> consensus` は `patch+approval` のみ
- 禁止: direct write / auto-apply / auto-publish

### safeMode境界（固定）
- `CE0-SAFEMODE-IF` を参照し、Graph再配置タスク側で緩和しない。
- SafeMode既定ONの後退を禁止する。

### Read同期 差分判定ルール
- 各Phase開始Readで `role / transition / no-go` に差分が1件でも検出された場合は即停止し、差分一覧を `held` で記録して指示待ちとする。

## Plan（Scope / Non-Goals / AC / DoD / Validation / Stop Conditions）
### Scope（このIssueで実施すること）
- CE0 Core Graphの責務境界（`working` / `context_projection` / `consensus`）を**契約文言として固定**する。
- `transition` と `no-go` を CE0 canonical語彙の範囲で整合化する。
- 未承認事項は `pending` または `held` で在庫化し、確定化しない。

### Non-Goals（このIssueで実施しないこと）
- 実装変更（handler/UI/DB/worker/API/Schema migration）
- CE0契約ID・No-Go語彙の再定義、拡張、別名化
- SafeMode既定ONを弱める記述
- 未承認事項の確定化

### Acceptance Criteria（AC）
- AC-1: Contract ID参照が `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05` の参照のみに限定される。
- AC-2: Graph roleが `working` / `context_projection` / `consensus` の3区分で固定される。
- AC-3: 許可遷移が `working -> consensus` の `patch+approval` のみで記述される。
- AC-4: No-Go語彙が canonical 5 IDs から逸脱しない。
- AC-5: 未承認事項が `held` または `pending` として保持され、確定扱いされない。
- AC-6: 検証手順として `docs-check` が明示される。
- AC-7: `role / transition / no-go` 語彙が同一語彙で一貫し、同義語への置換がない。
- AC-8: 禁止遷移として `direct write` / `auto-apply` / `auto-publish` が明示される。
- AC-9: 契約文面のみを更新し、実装依存の挙動記述を追加しない。

### Definition of Done（DoD）
- DoD-1: 本Issue本文だけを更新し、編集禁止ファイルに変更がない。
- DoD-2: Read同期〜Proceedの固定順序と停止条件が明文化されている。
- DoD-3: `docs-check` が成功し、失敗時自己修復上限（3回）が遵守される。
- DoD-4: Proceed判定が AC全充足時のみ `Done`、未承認事項は在庫記録で終了する。
- DoD-5: 禁止遷移（`direct write` / `auto-apply` / `auto-publish`）が本文内で明示され、否定されていない。

### Validation（docs-check）
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `git diff --check`
- （任意補助）`rg -n "preview_bypass|consensus_direct_write|auto_apply_or_publish|ai_review_auto_promotion|safemode_default_relaxation" 01_Plans/issues/issue-CE0-core-graph-repositioning.md`

### Stop Conditions（停止条件）
- SC-1: Phase開始Readで語彙差分を検出
- SC-2: CE0契約ID再定義、No-Go語彙変更、SafeMode既定ON後退の兆候を検出
- SC-3: docs-check失敗が3回以内に収束しない（4回目相当は禁止）

### AC/DoD不足時の扱い
- AC/DoD不足を検知した場合は、本Issue内にAIドラフトを追記して**明示合意まで `held` 維持**とする。

## Execute（contract-only）
- 本Issue本文内の契約記述（role / transition / no-go / stop条件 /判定条件）のみを修正対象とする。
- 実装記述（handler/UI/DB/worker/API挙動）は追加しない。
- 変更後に再読し、`Phase 1 Read` の固定語彙との不一致がないことを確認する。

## Verify（docs-check / 自己修復最大3回）
- 差分検知時は `held` で停止し、未承認のまま確定しない。
- 実行: `docs-check`。
- 失敗時: 原因を1点ずつ修正し再実行（最大3回）。
- 4回目相当は実施せず、`stopped_for_clarification` として停止する。

## Proceed（完了判定）
- Proceed条件: AC/DoD満了かつ docs-check pass。
- 未承認事項がある場合: `held` 在庫（未確定）を明記して終了。
- 完了時も contract-only の境界を維持し、実装タスクへ昇格しない。

## Phase Execution Record（2026-04-21 / Stream C）
### Phase 1 Read
- `role / transition / no-go` と SafeMode境界を再読し、差分なし（継続可）。
- CE0契約ID群は参照のみで利用し、再定義なし。

### Phase 2 Plan
- AC/DoD/Stop Conditions を再確認し、不足なし。
- 本作業の変更範囲を本Issueファイル内の進行記録追記のみに固定。

### Phase 3 ADR Consensus
- 判定: `No ADR delta`（方針差分なし）。

### Phase 4 Execute
- contract-only 境界を維持したまま、本Issueへ実行記録を追記。
- `working / context_projection / consensus`、`patch+approval`、canonical 5 IDs の語彙を維持。

### Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、問題なし。

### Proceed
- 判定: `Done`（AC/DoD充足、docs-check pass）。
- 未承認事項在庫: なし（新規 `held/pending` 追加なし）。

## Traceability Checklist
- [x] CE0契約IDの再定義をしていない。
- [x] No-Go語彙（canonical 5 IDs）を変更していない。
- [x] SafeMode既定ONを後退させていない。
- [x] 未承認事項を確定化していない（`held/pending` 維持）。
- [x] 実装記述（handler/UI/DB/worker）を追加していない。
- [x] `docs-check` を実行し結果を確認した。


## Phase Execution Record（2026-04-21 / Stream C / role-transition-no-go freeze update）
### Phase 1 Read
- 最新Readを実施し、`role / transition / no-go` 固定語彙とSafeMode境界に差分なし。
- CE0契約ID群（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）は参照のみで再定義なし。

### Phase 2 Plan
- 目的を「`role / transition / no-go` 語彙の契約固定（実装禁止）」に限定。
- AC/DoD不足は未検出のため追補提案は不要、既存AC/DoDで進行可能と判定。
- 変更範囲を本Issue文書の契約記述整合と実行記録追記のみに固定。

### Phase 3 ADR Consensus
- 最新Read後に判定し、`No ADR delta`（方針差分なし）。
- 追加ADR起票や仕様拡張は行わず、contract-only維持。

### Phase 4 Execute
- `role`: `working` / `context_projection` / `consensus` を固定語彙として維持。
- `transition`: 許可遷移を `working -> consensus` の `patch+approval` のみに固定。
- `no-go`: canonical 5 IDs（`preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`）以外を追加・置換しない。
- 実装記述（handler/UI/DB/worker/API/Schema migration）を追加しない。

### Verify
- 最新Read後に `docs-check` を実行し、pass。
- `git diff --check` を実行し、空白エラー等なし。

### Proceed
- 判定: `Done`（既存AC/DoDを満たし、docs-check pass）。
- 未承認事項在庫: なし（`held/pending` の新規発生なし）。

## Phase Execution Record（2026-04-22 / Stream C / contract-boundary lock + mock-pack input）
### Phase 1 Read
- `role / transition / no-go` 固定語彙、CE0契約ID read-only 制約、SafeMode境界を再読し、差分なし。
- 入力は mock contract pack を利用し、他ストリーム完了待ちを前提にしないことを確認。

### Phase 2 Plan
- Scope を本Issueの契約文言整合のみに固定（実装変更なし）。
- `role / transition / no-go` は既存固定語彙のみを使用し、再定義・同義語化・拡張を行わない。
- 致命条件（語彙差分、契約ID再定義、SafeMode既定ON後退、docs-check 4回目相当）発生時は推測実行せず停止報告する。

### Phase 3 ADR/CDC Consensus（Context/Decision/Consequences）
- Context: CE0 Core Graph責務境界の契約固定を、mock contract pack入力で先行検証する。
- Decision: `No ADR delta`。`working` / `context_projection` / `consensus`、`working -> consensus` + `patch+approval`、canonical 5 IDs を維持。
- Consequences: 未承認論点は `held` または `pending` の在庫として保持し、確定化しない。

### Phase 4 Execute
- contract-only 境界を維持し、本Issue本文の記述整合のみを実施。
- CE0契約IDは read-only 参照のみで利用し、再定義なし。

### Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- 自己修復回数は 0/3（追加修正なし）。

### Proceed
- 判定: `Done`（AC/DoD充足、docs-check pass、contract-only維持）。
- 致命条件の発生なし。発生時は `stopped_for_clarification` で停止報告する運用を再確認。

## Phase Execution Record（2026-04-22 / Stream C / independent-run strict single-file update）
### Phase 1 Read
- 本Issueの最新状態を実行直前にReadし、`role / transition / no-go` 語彙、SafeMode境界、停止条件を再確認。
- 事前想定との差分確認: 想定どおり固定語彙と契約境界は維持され、差分は検出されなかったため `held` 候補は新規発生なし。

### Phase 2 Plan
- Scope: 本Issue 1ファイル内での実行記録更新と、既存契約文言との整合確認のみ。
- Non-Goals: CE0契約ID再定義、実装変更（`03_Implement/**`）、未承認事項の確定化。
- AC/DoD/Validation/Stop Conditions を既存定義に準拠して再確認し、不足は検出されなかったため追加ドラフト提案は不要と判定。
- 編集対象が `01_Plans/issues/issue-CE0-core-graph-repositioning.md` のみであることを再確認。

### Phase 3 ADR/CDC Consensus
- 方針差分判定: `No ADR delta`（新規の Context/Decision/Consequences 追加承認は不要）。
- 未承認論点の確定化は行わず、必要時は `held/pending` 維持の方針を再確認。

### Phase 4 Execute
- 承認済みの既存Plan/契約境界に一致する最小差分として、本実行記録のみ追記。
- `role / transition / no-go` 語彙の追加・再定義は実施せず、SafeMode既定ONの後退を示唆する記述も追加しない。

### Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- 不一致は発生せず、自己修復回数は 0/3。

### Proceed
- 判定: `Done`（AC/DoD整合、docs-check pass、single-file/contract-only 制約を維持）。
- 未承認論点の新規発生なし。発生時は推測で進行せず `held` で停止する。

## Phase Execution Record（2026-04-22 / Stream C / core-graph contract freeze reaffirmation）
### Phase 1 Read
- 本Phase開始時に本Issueを再読し、`role / transition / no-go` 固定語彙、CE0契約ID read-only 制約、SafeMode既定ON境界を再確認。
- 差分判定: 固定語彙に変更なし、No-Go canonical 5 IDs に変更なし、`held` へ移行すべき差分なし。

### Phase 2 Plan
- Scope を「本Issueの契約固定記述と実行記録の更新」に限定し、single-file 制約を再確認。
- Non-Goals（実装記述追加、CE0契約ID再定義、No-Go語彙再定義、SafeMode後退記述）を再確認。
- AC/DoD不足の有無を確認し、不足は検出されなかったため `held` 追加は不要と判定。

### Phase 3 ADR Consensus
- 本Phase開始時に再読を実施し、方針差分の有無を再評価。
- 判定: `No ADR delta`。未承認論点の確定化は行わず、必要時 `held/pending` 維持方針を継続。

### Phase 4 Execute
- contract-only 境界を維持し、本Issue本文への実行記録追記のみ実施。
- `working` / `context_projection` / `consensus`、`working -> consensus` + `patch+approval`、canonical 5 IDs を固定語彙として維持。
- 実装記述（handler/UI/DB/worker/API）を追加しないことを再確認。

### Verify
- 本Phase開始時に再読し、語彙差分・SafeMode後退兆候・No-Go逸脱がないことを確認。
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- 自己修復回数は 0/3（>3 に達せず停止条件未発火）。

### Proceed
- 本Phase開始時に再読し、Proceed条件（AC/DoD充足 + docs-check pass）を確認。
- 判定: `Done`（contract-only / single-file / 語彙固定 / SafeMode境界維持）。
- 未承認事項在庫: なし。新規発生時は `held` で停止し人手合意待ちとする。

## Phase Execution Record（2026-04-22 / Stream C / CE0 vocabulary-lock compliance run）
### Phase 1 Read
- Phase開始前Readを実施し、`role / transition / no-go` 固定語彙の差分を確認した結果、差分 0 件。
- CE0契約ID（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）は read-only 参照のみで利用し、再定義なし。
- SafeMode境界（既定ON維持・緩和禁止）と canonical 5 IDs の不変条件を再確認。

### Phase 2 Plan
- Phase開始前Readを再実施し、直前Phaseとの差分（語彙・禁止事項・SafeMode境界）を確認、差分 0 件。
- Scopeを本Issue単体の契約文言/記録更新に限定し、single-file 制約を維持。
- AC/DoD不足の有無を点検し、不足は未検出のため「提案→合意」フローは未起動（`held` 新規なし）。

### Phase 3 ADR Consensus
- Phase開始前Readを実施し、固定語彙差分チェックを再実行、差分 0 件。
- 判定: `No ADR delta`。
- 方針差分が発生した場合のみ `pending` で起票し承認まで `held` 維持する既存ルールを継続。

### Phase 4 Execute
- Phase開始前Readを実施し、`role / transition / no-go` 固定語彙を再確認後に実行。
- `working` / `context_projection` / `consensus`、`working -> consensus` + `patch+approval`、canonical 5 IDs を固定したまま本Issueの追記のみ実施。
- 実装記述（handler/UI/DB/worker/API/Schema migration）を追加せず、contract-only 境界を維持。

### Verify
- Phase開始前Readを実施し、語彙差分とNo-Go逸脱がないことを確認。
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- Verify失敗時の自律修正上限は 3 回で運用し、本実行の自己修復回数は 0/3。

### Proceed
- Phase開始前Readを実施し、Proceed条件（AC/DoD + docs-check pass）を照合。
- 判定: `Done`（single-file / contract-only / 語彙固定 / CE0契約ID read-only / SafeMode境界維持）。
- 未承認事項在庫: なし。将来発生時は 3 回上限を超える前に `held` で停止し、4回目相当は `stopped_for_clarification` を適用。

## Phase Execution Record（2026-04-22 / Stream C / core-graph boundary contract lock only）
### Phase 1 Read
- Read再同期を実施し、`role / transition / no-go` 固定語彙、CE0契約ID read-only 制約、SafeMode既定ON境界を確認。
- 差分判定: 語彙衝突・再定義・後退兆候は 0 件（継続可）。

### Phase 2 Plan
- Phase開始時Readを再実施し、直前Phaseとの差分（role/transition/no-go, SafeMode, no-go制約）を再点検。
- Scopeを「Core Graph責務境界の契約固定記録」へ限定し、編集対象を本Issue単一ファイルのみに固定。
- AC/DoD不足は未検出。よってAIドラフト提案フェーズは未起動（`held` 新規なし）。

### Phase 3 ADR Consensus
- Phase開始時Readを再実施し、契約語彙の差分有無を再確認。
- 判定: `No ADR delta`（契約固定のみで遂行、方針追加なし）。
- 未承認論点は確定化せず、発生時は `held`/`pending` で在庫化する方針を維持。

### Phase 4 Execute
- Phase開始時Readを再実施後、contract-only で本Issueの実行記録を追記。
- `working` / `context_projection` / `consensus`、`working -> consensus` + `patch+approval`、canonical 5 IDs を固定維持。
- 禁止事項（CE0契約ID再定義、SafeMode後退、語彙衝突、指定外編集）に抵触しないことを確認。

### Verify
- Phase開始時Readを再実施し、語彙差分・No-Go逸脱・SafeMode後退がないことを確認。
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- Verify失敗は発生せず、自己修復回数は 0/3。

### Proceed
- Phase開始時Readを再実施し、Proceed条件（AC/DoD充足 + docs-check pass）を確認。
- 判定: `Done`（Stream C専任、single-file、contract-only、責務境界契約固定を維持）。
- 未承認事項在庫: なし。今後検出時は `held` で停止し、4回目相当のVerifyは実施しない。

## Phase Execution Record（2026-04-22 / Stream C専任 / core-graph責務再配置 proposal-only固定）
### 1. Read
- Phase開始時Readを実施し、`role / transition / no-go` 固定語彙、CE0契約ID read-only 制約、SafeMode既定ON境界を再確認。
- 差分判定: 語彙差分 0 件、契約ID再定義 0 件、SafeMode後退兆候 0 件。
- フェイルセーフ確認: `direct write` 許容が混入した場合は即時停止し `held` として記録する。

### 2. Plan（AC/DoD不足ドラフト提案）
- Scope: Core Graph責務再配置の契約固定（`working` / `context_projection` / `consensus`）のみ。
- Non-Goals: 実装変更、CE0契約ID再定義、No-Go語彙拡張、SafeMode既定緩和。
- AC/DoD不足点の点検結果:
  - AC追加ドラフト提案: `proposal-only` を明文化し、`direct write` を常時No-Goとして固定する。
  - DoD追加ドラフト提案: Verifyで「契約逸脱（Contract drift）」「責務混在（Role bleed）」の2観点チェックを必須化する。
- 上記は**ドラフト提案のみ**とし、承認までは `held` 扱いで確定化しない。

### 3. Execute（proposal-only運用、直接更新禁止方針を固定）
- 運用方針を `proposal-only` に固定し、`working -> consensus` は `patch+approval` 以外を許容しない。
- `consensus_direct_write` / `auto_apply_or_publish` を継続No-Goとして維持。
- `direct write` 許容記述の混入を検出した場合はフェイルセーフにより即停止（`stopped_for_clarification`）。

### 4. Verify（契約逸脱・責務混在チェック）
- チェックA（契約逸脱）: CE0契約IDの再定義有無、canonical 5 IDs逸脱有無、SafeMode後退有無を確認（逸脱 0 件）。
- チェックB（責務混在）: `working` / `context_projection` / `consensus` の役割混在、`patch+approval` 以外の遷移記述混入を確認（混在 0 件）。
- 実行: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`、`git diff --check`。
- 自己修復回数制限: 最大 3 回。4回目相当は実施せず停止する。

### 5. Proceed（mock前提で他ストリーム独立実行可能なI/F断面）
- 判定: `Done`（contract-only / proposal-only / single-file 制約維持）。
- mock前提I/F断面（他ストリーム独立実行用）:
  - I/F-1 `GraphRoleContract`: `working` / `context_projection` / `consensus` の語彙固定（read-only参照）。
  - I/F-2 `TransitionGate`: 許可遷移は `working -> consensus` + `patch+approval` のみ。
  - I/F-3 `NoGoGate`: `preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`。
  - I/F-4 `SafetyGate`: SafeMode既定ON・`allowUnreviewedText=false` を前提固定。
  - I/F-5 `AuditGate`: query/bundle/proposal/apply の監査4点セット欠損時は成功扱い禁止（mockでも同一判定）。
- 未承認事項は `held` 在庫で維持し、確定判断は行わない。

## Phase Execution Record（2026-04-23 / Stream C / CE0 core graph repositioning strict-phase rerun）
### Phase 1 Read
- 対象ファイルを再読し、`role / transition / no-go` 固定語彙（`working` / `context_projection` / `consensus`、`patch+approval`、canonical 5 IDs）を確認。
- 差分確認: 直前記録との差分は追記のみで、語彙・禁止事項・SafeMode境界（既定ON）に変更なし。
- CE0契約ID（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）は参照のみ、再定義なし。

### Phase 2 Plan
- 対象ファイルを再読し、Phase 1との差分がないことを確認。
- Scopeを本Issue 1ファイルの実行記録更新のみに限定（single-file / contract-only）。
- AC/DoD不足判定: 不足は未検出。不足発生時はドラフト提示→合意まで `held` 維持の運用を継続。

### Phase 3 ADR Consensus
- 対象ファイルを再読し、方針差分の有無を確認。
- 判定: `No ADR delta`（新規ADR合意要求なし）。
- 未承認論点は確定しない（必要時は `pending` / `held`）。

### Phase 4 Execute
- 対象ファイルを再読し、固定語彙と禁止事項に差分がないことを確認してから追記。
- `working -> consensus` は `patch+approval` のみを許可する契約を維持。
- 実装領域（handler/UI/DB/worker/API/Schema migration）への変更は実施しない。

### Verify
- 対象ファイルを再読し、語彙逸脱・SafeMode後退・契約ID再定義がないことを確認。
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- Self-Correction実績: 0/3（上限3回を超過していない）。

### Proceed
- 対象ファイルを再読し、Proceed条件（AC/DoD充足 + docs-check pass）を確認。
- 判定: `Done`（single-file / contract-only / 語彙固定 / CE0契約ID再定義禁止 / SafeMode既定ON維持）。
- 未承認事項在庫: なし。AC/DoD不足が将来検出された場合はドラフト提示後、合意まで `held` で停止する。

## Phase Execution Record（2026-04-24 / Stream C専任 / CE0 Core Graph Repositioning contract-only fixpoint）
### Phase 1 Read（role/transition/no-go差分確認）
- 実行開始時Readを実施し、`role`（`working` / `context_projection` / `consensus`）、`transition`（`working -> consensus` + `patch+approval`）、`no-go`（canonical 5 IDs）を再確認。
- 直前記録との差分判定: 語彙差分 0 件、禁止事項差分 0 件、SafeMode境界（既定ON維持）差分 0 件。
- フェイルセーフ前提を再確認: `direct write` 容認、SafeMode緩和、未定義競合の検出時は即時停止して `held` または `stopped_for_clarification` とする。

### Phase 2 Plan（AC/DoD不足補完）
- Scopeを本Issue単体の契約固定文言に限定（single-file / contract-only）。
- AC補完: 「`role / transition / no-go` の固定語彙を同義語置換せず維持する」を明記。
- DoD補完: 「Verifyで self-correction 回数を 3 回以内に制限し、4 回目相当を実施しない」を明記。
- 補完項目は本Issueの契約運用に反映し、実装依存（handler/UI/DB/worker/API/Schema migration）は追加しない。

### Phase 3 ADR Consensus（Context/Decision/Consequences承認）
- Context: CE0 Core Graph Repositioning を実装非依存の mock 前提で先行固定し、他ストリームが同一契約I/Fを参照可能にする。
- Decision: `No ADR delta` を承認。契約固定は `working` / `context_projection` / `consensus`、`working -> consensus` + `patch+approval`、canonical 5 IDs の維持に限定。
- Consequences: 未承認論点は `held/pending` 在庫化し、確定化しない。契約逸脱検出時は停止し、推測で進行しない。

### Phase 4 Execute（契約文言のみ）
- 実施内容を本Issue内の契約文言・実行記録更新のみに限定。
- `direct write` 容認につながる記述、SafeMode緩和記述、未定義競合の黙示許容は追加しない。
- mock活用方針として、実装依存を持たない transition/no-go 契約の先行固定のみを実施。

### Verify（self-correction <= 3）
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- self-correction 実績: 0/3。上限超過（4回目相当）は未実施。

### Proceed（handoff）
- 判定: `Done`（AC/DoD充足、docs-check pass、single-file / contract-only 制約維持）。
- handoff: 他ストリームは本Issueの固定契約（role/transition/no-go, SafeMode境界, fail-safe停止条件）を read-only 参照して実装側へ展開する。
- 未承認事項在庫: なし。将来検出時は `held` で停止し、人手合意まで確定化しない。

## Phase Execution Record（2026-04-24 / Stream C専任 / CE0 contract vocabulary freeze rerun）
### Phase 1 Read（語彙差分確認）
- 実行開始時Readを実施し、固定語彙 `working` / `context_projection` / `consensus` と遷移契約 `working -> consensus` + `patch+approval` を再確認。
- No-Go canonical 5語彙（`preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`）を再確認し、語彙差分 0 件。
- CE0契約ID（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）は参照のみ（再定義なし）。

### Phase 2 Plan（AC/DoD明文化）
- Scopeを本Issue単体（single-file / contract-only）に固定し、実装変更は行わない。
- AC明文化: role/transition/no-go語彙を固定し、同義語置換・拡張・再定義を禁止。
- DoD明文化: `docs-check` pass と self-correction 最大3回を必須とし、4回目相当は実施しない。
- AC/DoD不足が生じた場合はドラフト提案のみ実施し、承認まで `held` 維持とする。

### Phase 3 ADR（Context/Decision/Consequences）
- Context: Core Graph責務再配置を契約固定として扱い、他ストリーム連携時の境界揺れを防止する。
- Decision: `No ADR delta`。固定契約は `working` / `context_projection` / `consensus`、`working -> consensus` + `patch+approval`、No-Go canonical 5語彙を維持。
- Consequences: 未承認論点は `held/pending` の在庫で保持し、確定化しない。

### Phase 4 Execute（本Issueのみ更新）
- 更新対象を `01_Plans/issues/issue-CE0-core-graph-repositioning.md` のみに限定して実行記録を追記。
- SafeMode後退、No-Go語彙変更、CE0契約ID再定義、指定外編集は未実施。

### Verify（docs-check / 自己修復最大3回）
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- self-correction 実績: 0/3（4回目相当は未実施）。

### Proceed（未承認はheld維持）
- 判定: `Done`（AC/DoD充足、docs-check pass、single-file / contract-only 制約維持）。
- 未承認事項在庫: なし。将来の未承認論点は `held` のまま維持し、承認前に確定化しない。

## Phase Execution Record（2026-04-25 / Stream C専任 / CE0 independent contract-only rerun）
### Phase 1 Read
- Phase開始時に対象ファイルを再Readし、固定語彙 `working` / `context_projection` / `consensus`、許可遷移 `working -> consensus` + `patch+approval`、No-Go canonical 5 IDs を再確認。
- 独立性制約（CE0契約ID再定義禁止・実装変更禁止・No-Go語彙固定）を再確認し、差分 0 件。
- SafeMode境界（既定ON・緩和禁止）に変更がないことを確認。

### Phase 2 Plan
- Phase開始時に再Readし、Scopeを本Issue 1ファイルの実行記録追記のみに固定（single-file / contract-only）。
- AC/DoD不足判定を再実施し、不足は未検出。将来不足検出時はドラフト提案を追記し、明示合意まで `held` 維持とする。
- Stop Conditions（語彙差分、CE0契約ID再定義、SafeMode後退、self-correction 4回目相当）を再確認。

### Phase 3 ADR Consensus
- Phase開始時に再Readし、方針差分の有無を判定。
- 判定: `No ADR delta`（契約固定の範囲内で処理可能）。
- 未承認事項は確定化せず、必要時 `held/pending` で在庫化する方針を維持。

### Phase 4 Execute
- Phase開始時に再Readし、固定語彙・禁止事項との不一致がないことを確認してから追記。
- 実行内容は本Issue本文の記録更新のみ。実装変更（handler/UI/DB/worker/API/Schema migration）は未実施。
- CE0契約IDは read-only 参照のみで再定義なし、No-Go canonical 5 IDs への追加/置換なし。

### Verify
- Phase開始時に再Readし、語彙逸脱・SafeMode後退・契約ID再定義がないことを再確認。
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- `rg -n "preview_bypass|consensus_direct_write|auto_apply_or_publish|ai_review_auto_promotion|safemode_default_relaxation" 01_Plans/issues/issue-CE0-core-graph-repositioning.md` を実行し、canonical 5 IDs の固定参照を確認。
- self-correction 実績: 0/3（上限超過なし、4回目相当は未実施）。

### Proceed
- Phase開始時に再Readし、Proceed条件（AC/DoD充足 + docs-check pass）を確認。
- 判定: `Done`（独立性制約遵守、single-file / contract-only 維持）。
- 未承認事項在庫: なし。今後AC/DoD不足が検出された場合はドラフト提案を追記し、合意まで `held` で停止する。

## Phase Execution Record（2026-04-25 / Stream C専任 / CE0 scope-fixed contract-only run）
### Phase 1 Read（role / transition / no-go 再読）
- 実行開始時Readを実施し、`role`（`working` / `context_projection` / `consensus`）、`transition`（`working -> consensus` + `patch+approval`）、`no-go`（canonical 5 IDs）を再確認。
- 直前記録との差分確認: 語彙ドリフト 0 件、No-Go語彙変更 0 件、SafeMode境界（既定ON維持）差分 0 件。

### Plan（Scope / Non-Goals / AC / DoD / Validation / Stop Conditions）
- Scope: 本Issue単体の契約文言整合と実行記録追記のみ（single-file / contract-only）。
- Non-Goals: 実装変更、CE0契約ID再定義、No-Go語彙変更・拡張、SafeMode既定ON後退、未承認事項の確定化。
- AC/DoD: 既存定義（語彙固定・`patch+approval`固定・docs-check pass・self-correction 最大3回）を満たす方針を再確認。
- Validation: `docs-check` と `git diff --check` を実施。
- Stop Conditions: 語彙ドリフト検出、No-Go語彙変更検出、SafeMode後退兆候、Verify 3回超過で停止。

### Phase 3 ADR Consensus（方針差分時のみ CDC）
- 判定: `No ADR delta`（新規CDC起票不要）。
- 方針差分が発生した場合のみ `Context / Decision / Consequences` を `pending` で起票し、承認まで `held` を維持する。

### Phase 4 Execute（contract-only修正）
- 本Issue本文のみを更新し、実装領域（handler/UI/DB/worker/API/Schema migration）への変更は実施しない。
- 固定語彙（`role / transition / no-go`）とSafeMode境界の不変条件を維持。

### Verify（docs-check / diff check / 最大3回修復）
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- self-correction 実績: 0/3（上限超過なし）。

### Proceed（Go判定）
- 判定: `Done`（AC充足、docs-check pass、未承認事項の確定化なし）。
- フェイルセーフ再確認: 語彙ドリフト / No-Go語彙変更 / SafeMode後退 / 3回超過が発生した場合は即停止し、`held` または `stopped_for_clarification` とする。

## Phase Execution Record（2026-04-26 / Stream B read-sync witness for CE0 only）
### Phase 1 Read
- 実行開始時に `issue-CE0-contract-freeze.md` と本Issueを再読し、`role / transition / no-go` と CE0 canonical 5 IDs の差分を確認（差分なし）。
- 事前想定との差分: なし（`held` へ切替える事象なし）。

### Phase 2 Interface-first
- Core Graph側は CE0 SSOT を read-only 参照する前提を明文化し、I/F再定義を行わない。
- 判定キーは CE0 canonical IDs（`preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`）のみを利用する。

### Phase 3 Plan
- AC/DoD不足の有無を再確認し、不足は未検出。
- 不足発生時はドラフト追記のうえ `held` 維持、合意前に Execute確定しない方針を再確認。

### Phase 4 Execute / Verify
- 実施は contract-only の実行記録追記のみ（実装変更なし）。
- Verify attempt_1:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `git diff --check`
  - result: pass（self-correction 0/3）

### Phase 5 Proceed / Fail-safe
- 判定: `Done`（docs-check pass、語彙差分なし、safeMode後退なし）。
- 停止条件（競合・前提崩壊・自己修復4回目相当）は継続監視し、発火時は `held` / `stopped_for_clarification` とする。

## Phase Execution Record（2026-04-26 / Stream C / CE0 Core Graph Repositioning strict serial run）
### Phase 1 Read
- Read同期を実施し、`role / transition / no-go` 固定語彙（`working` / `context_projection` / `consensus`、`working -> consensus` + `patch+approval`、canonical 5 IDs）を再確認。
- CE0契約ID（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）は read-only 参照のみで、再定義なし。
- 差分判定: 直前Phaseとの差分 0 件（語彙・禁止事項・SafeMode境界に変更なし）。

### Phase 2 Plan
- Phase冒頭Read同期を再実施し、Phase 1 からの差分 0 件を確認。
- Scopeを本Issue 1ファイルの contract-only 記録更新のみに固定（実装変更禁止）。
- Plan→Execute→Verify→Proceed の直列遷移を明記し、未承認事項は `held/pending` 維持で確定化しない。

### Phase 3 ADR Consensus
- Phase冒頭Read同期を再実施し、語彙差分・No-Go逸脱・SafeMode後退兆候の有無を確認（差分 0 件）。
- 判定: `No ADR delta`（方針差分なし）。
- 方針差分が将来発生した場合は `pending` として記録し、承認完了まで `held` を維持する。

### Phase 4 Execute
- Phase冒頭Read同期を再実施し、固定語彙不変条件を再確認してから実施。
- 実行内容は本Issue本文への実行記録追記のみ。実装領域（handler/UI/DB/worker/API/Schema migration）は未変更。
- CE0契約ID再定義、No-Go語彙置換・拡張、SafeMode既定ON後退の記述追加は未実施。

### Verify
- Phase冒頭Read同期を再実施し、Phase 4 からの語彙差分 0 件を確認。
- Verify attempt_1: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` → pass。
- Verify attempt_1: `git diff --check` → pass。
- self-correction 実績は 0/3。失敗時は最大3回まで自己修復し、4回目相当は実施せず `stopped_for_clarification` で停止する。

### Proceed
- Phase冒頭Read同期を再実施し、Proceed条件（AC/DoD充足 + docs-check pass）を確認。
- 判定: `Done`（single-file / contract-only / CE0契約ID read-only / 語彙固定 / SafeMode境界維持）。
- 未承認事項在庫: なし。将来発生時は `held` へ遷移してエスカレーションする。

## Phase Execution Record（2026-04-26 / Stream C / CE0 core graph repositioning prompt-c sync）
### Phase 1 Read
- 開始時Read同期を実施し、`role / transition / no-go` 固定語彙、CE0契約ID read-only 制約、SafeMode既定ON境界を再確認。
- 差分判定: 固定語彙差分なし、canonical 5 IDs 差分なし、`held` へ移行すべき新規差分なし。

### Phase 2 Plan（ADR first: Context / Decision / Consequences）
- Context: CE0 Core Graph再配置は contract-only で実施し、`working` / `context_projection` / `consensus`、`working -> consensus` + `patch+approval`、canonical 5 IDs を固定維持する。
- Decision: `No ADR delta`。本作業は本Issue単一ファイル更新に限定し、実装変更（handler/UI/DB/worker/API/Schema migration）を禁止する。
- Consequences: 未承認論点は `held` または `pending` の在庫として保持し、確定化しない。語彙差分・SafeMode後退兆候・自己修復4回目相当は停止条件とする。
- Plan同期: AC/DoD/Validation/Stop Conditions を再確認し、不足なしのため既存契約定義を維持して進行。

### Phase 3 ADR Consensus
- 開始時Read同期を再実施し、Phase 2で明文化した Context/Decision/Consequences と本文契約定義の一致を確認。
- 判定: `No ADR delta` を維持。未承認事項の確定化は行わず、必要時 `held/pending` 維持。

### Phase 4 Execute
- 開始時Read同期を再実施し、contract-only 境界と single-file 制約を確認。
- 実施内容を本Issue内の実行記録追記に限定し、`role / transition / no-go` 語彙の同義語置換・再定義・拡張を実施しない。

### Verify
- 開始時Read同期を再実施し、検証コマンドと停止条件を再確認。
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- 自己修復回数: 0/3（追加修復不要）。

### Proceed
- 開始時Read同期を再実施し、Proceed条件（AC/DoD満了 + docs-check pass）を確認。
- 判定: `Done`（contract-only / single-file / 固定語彙維持 / docs-check pass）。
- 未承認事項在庫: なし（新規 `held/pending` 追加なし）。

## Phase Execution Record（2026-04-26 / Stream C / CE0 Core Graph Repositioning dedicated run）
### Phase 1 Read
- 開始時Readを実施し、`role` は `working` / `context_projection` / `consensus` の3区分固定、`transition` は `working->consensus` の `patch+approval` のみ、`no-go` は canonical 5 IDs 固定であることを確認。
- 差分判定: 語彙ドリフト 0 件、SafeMode既定ON後退 0 件、CE0契約再定義兆候 0 件。

### Phase 2 Plan
- Scopeを本Issue単体の契約記述整合と実行記録追記のみに固定（single-file / contract-only）。
- AC/DoD不足を点検し、不足なしと判定。将来不足を検出した場合はドラフト提案を追記し、明示合意完了まで `held` 維持とする。
- `working -> consensus` 遷移は `patch+approval` のみを許可し、その他遷移・同義語拡張を禁止する。

### Phase 3 ADR Consensus（必要時）
- 方針差分の有無を再確認し、判定は `No ADR delta`。
- 差分が発生した場合のみ `pending` で起票し、承認まで `held` のまま確定しない。

### Phase 4 Execute
- 本Issueファイル内の記録更新のみを実施し、実装変更（UI/DB/API/worker）は未実施。
- CE0 canonical No-Go語彙（`preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`）から逸脱しない。

### Verify
- verify attempt_1: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` → pass。
- verify attempt_1: `git diff --check` → pass。
- 自律修正回数: 0/3（4回目再試行なし）。

### Proceed
- 判定: `Done`（AC/DoD充足、docs-check pass、single-file / contract-only 維持）。
- 未承認事項在庫: なし。今後、語彙ドリフト・SafeMode後退・CE0契約再定義兆候・4回目再試行条件を検出した場合は即停止する。

## Phase Execution Record（2026-04-26 / Stream C / CE0 constrained single-file cycle）
### 1 Read
- 開始時Readを実施し、固定語彙 `working` / `context_projection` / `consensus`、許可遷移 `working -> consensus` + `patch+approval`、禁止 `direct write / auto-apply / auto-publish` を再確認。
- CE0契約ID（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）は参照のみで再定義なし。
- 停止条件の先行確認: 語彙差分、契約ID変異、SafeMode後退、未承認確定化の兆候なし。

### 2 Plan
- Scopeを本Issue単体の契約記述整合と実行記録追記のみに限定（single-file / contract-only）。
- AC/DoD不足は未検出。将来不足時はドラフト提示のみ行い、明示承認まで `held` を維持する。
- 実行サイクルを `Plan -> Execute -> Verify（<=3回自己修復） -> Proceed` に固定。

### 3 ADR Consensus
- 方針差分判定: `No ADR delta`。
- 方針差分が発生した場合のみ `Context / Decision / Consequences` を作成し、承認完了まで `held` 維持。

### 4 Execute
- 本Issue本文の追記のみを実施し、他ファイル編集なし。
- `role` は `working` / `context_projection` / `consensus` を維持し、`working -> consensus` は `patch+approval` のみを許可。
- no-go（`direct write / auto-apply / auto-publish`）を維持し、SafeMode既定ONを後退させる記述を追加しない。

### 5 Verify
- verify attempt_1: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` → pass。
- verify attempt_1: `git diff --check` → pass。
- 自己修復回数: 0/3（4回目相当は未実施）。

### 6 Proceed
- 判定: `Done`（AC/DoD整合、docs-check pass、single-file / contract-only 制約維持）。
- 未承認事項在庫: なし。将来、語彙差分・契約ID変異・SafeMode後退・4回目自己修復条件が発生した場合は即停止して `held` または `stopped_for_clarification` とする。

## Phase Execution Record（2026-04-26 / Stream C / CE0 single-file requested cycle）
### Read
- 開始時Read同期を実施し、`role`（`working` / `context_projection` / `consensus`）、`transition`（`working -> consensus` + `patch+approval`）、`no-go`（`direct write / auto-apply / auto-publish`）の固定語彙を確認。
- CE0契約ID（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）は参照のみで、再定義なし。
- 差分判定: 直前記録との差分なし（語彙・禁止事項・SafeMode境界の変更なし）。

### Plan
- Read同期を再実施し、Read結果との差分なしを確認してから計画を固定。
- Scopeを `01_Plans/issues/issue-CE0-core-graph-repositioning.md` のみへ限定し、contract-only（実装変更なし）を維持。
- `role / transition / no-go` の同義語置換・拡張・再定義は禁止。未承認事項は `held/pending` で保持し、確定しない。

### ADR/CDC
- Read同期を再実施し、方針差分の有無を確認（差分なし）。
- 判定: `No ADR delta`。
- もし方針差分が発生した場合は `pending` 記録に切り替え、承認完了まで `held` を維持する。

### Execute
- Read同期を再実施し、禁止条件（direct write / auto-apply / auto-publish）と SafeMode既定ON境界を再確認してから実施。
- 実施内容は本Issueの実行記録追記のみ。他ファイル変更、実装変更（handler/UI/DB/worker/API/Schema migration）は未実施。

### Verify/Proceed
- Read同期を再実施し、検証対象と停止条件を確認。
- verify attempt_1: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` → pass。
- verify attempt_1: `git diff --check` → pass。
- 自己修復回数: 0/3（上限3回、4回目相当は `stopped_for_clarification` で停止）。
- Proceed判定: `Done`（AC/DoD整合、docs-check pass、single-file / contract-only / 固定語彙維持）。
- 未承認事項在庫: なし（新規 `held/pending` なし）。

## Phase Execution Record（2026-04-27 / Stream C）
### Phase Read（最新Read同期）
- `00_Prompt/system_prompt.md` / `00_Prompt/domain.md` / `00_Prompt/handoff.md` / `00_Prompt/agent_handover.md` / `00_Prompt/ai_cognitive_externalization_requirements.md` / `01_Plans/adr/ADR-0001-value-to-requirements.md` / `02_Architecture/architecture.md` / `02_Architecture/schemas.md` / `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md` / 本Issueを再読した。
- `role / transition / no-go` と SafeMode境界の差分は検出されず、`held` 停止条件は未発火。

### Phase Plan（最新Read同期）
- Phase開始前に本Issueを再読し、固定語彙（`role / transition / no-go`）の差分なしを確認。
- AC/DoD不足の有無を確認し、不足は検出されなかったためドラフト提案は不要と判定。
- 変更範囲を「本Issueの進行記録追記のみ」に固定し、実装詳細や他Issue契約再定義は非対象とした。

### Phase Execute（最新Read同期）
- Phase開始前に本Issueを再読し、`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05` の参照限定を再確認。
- 本Issueに本レコードを追記（contract-only / docs-only）。
- Self-Correctionは不要（0/3）。

### Phase Verify（最新Read同期）
- Phase開始前に本Issueを再読し、No-Go canonical 5 IDs の保持を確認。
- `docs-check` と差分健全性チェックを実行し、いずれも pass（詳細は本PRの検証ログ参照）。
- Self-Correctionは不要（0/3）。

### Phase Proceed（最新Read同期）
- Phase開始前に本Issueを再読し、AC/DoDの充足判定を実施。
- 判定: Proceed可（AC-1〜AC-6 / DoD-1〜DoD-4 を満了）。
- 未承認事項の新規発生なし。`held` 在庫の追加なしで終了。

## Phase Execution Record（2026-04-27 / Stream C / strict Phase 1-6 rerun）
### Phase 1 Read（Read同期）
- Phase開始時に本IssueをRead同期し、`role`（`working` / `context_projection` / `consensus`）、`transition`（`working -> consensus` + `patch+approval`）、`no-go`（canonical 5 IDs）を再確認。
- 差分検知結果: 語彙・禁止事項・SafeMode境界の差分は 0 件。停止条件（差分検知時 `held`）は未発火。

### Phase 2 Plan（Read同期）
- Phase開始時に再Readし、Phase 1との差分がないことを確認してから計画を固定。
- Scopeを `01_Plans/issues/issue-CE0-core-graph-repositioning.md` の契約固定記述更新のみに限定（implementation禁止 / single-file）。
- 差分検知結果: 0 件。差分が発生した場合は即停止し承認待ちへ移行する条件を再確認。

### Phase 3 ADR/CDC（Read同期）
- Phase開始時に再Readし、方針差分（ADR/CDC起票要否）を確認。
- 判定: `No ADR delta`（契約固定の範囲で完了可能）。
- 差分検知結果: 0 件。差分が出た場合は `pending` 記録後に `held` で停止する。

### Phase 4 Execute（Read同期）
- Phase開始時に再Readし、固定語彙と禁止事項の不一致がないことを確認後に本記録のみ追記。
- `role / transition / no-go` の再定義・同義語置換・拡張は未実施。実装記述（handler/UI/DB/worker/API/Schema migration）追加なし。
- 差分検知結果: 0 件（契約境界の逸脱なし）。

### Verify（Read同期 / self-heal <= 3）
- Phase開始時に再Readし、検証対象と停止条件（4回目相当で停止）を確認。
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し pass。
- `git diff --check` を実行し pass。
- Self-Correction実績: 0/3（4回目相当なし）。

### Proceed（Read同期）
- Phase開始時に再Readし、Proceed条件（AC/DoD充足 + docs-check pass）を確認。
- 判定: `Done`（contract-only / implementation禁止 / single-file 制約維持）。
- 未承認事項在庫: なし。差分検知時停止ルールを維持したまま終了。

## Phase Execution Record（2026-04-27 / Stream C / requested Phase 1→2(ADR/CDC)→3→4→5→6）
### Phase 1 Read
- 開始時Readを実施し、`role`（`working` / `context_projection` / `consensus`）、`transition`（`working -> consensus` + `patch+approval`）、`no-go`（canonical 5 IDs）とSafeMode境界を再確認した。
- 差分判定: 語彙・禁止事項・SafeMode境界の差分は 0 件。停止条件（前提崩れ / 未定義競合）未発火。

### Phase 2 ADR/CDC確認
- 開始時Readを再実施し、方針差分の有無を確認した。
- 判定: `No ADR delta`（契約固定の範囲で継続可能）。
- 未承認論点を確定化せず、必要時は `pending` または `held` で在庫化する運用を維持。

### Phase 3 Plan（AC/DoD補完）
- 開始時Readを再実施し、直前Phaseとの差分なしを確認してから計画を固定した。
- AC/DoDは既存定義で充足可能と判断し、追加補完は不要（不足検知なし）。
- Scopeを本Issue単独の契約記述更新に限定し、実装変更・契約ID再定義・語彙拡張を非対象とした。

### Phase 4 Execute
- 開始時Readを再実施し、固定語彙と禁止事項の不一致がないことを確認したうえで本レコードのみ追記した。
- contract-only / docs-only / single-file 境界を維持し、他ファイル編集は未実施。

### Verify（自己修復最大3回）
- verify attempt_1: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` → pass。
- verify attempt_1: `git diff --check` → pass。
- 自己修復回数: 0/3。4回目相当は未実施。

### Proceed/Stop
- 判定: `Proceed=Done`（AC/DoD整合 + docs-check pass）。
- 停止条件（前提崩れ / 未定義競合 / 3回超過）は未発火。
- 未承認事項在庫: なし（新規 `held/pending` 追加なし）。

## Phase Execution Record（2026-04-27 / Stream C専任 / CE0 Core Graph contract-only phase-cycle sync）
### Phase 1 Read（role / transition / no-go 再同期）
- Phase開始時Readを実施し、固定語彙 `working` / `context_projection` / `consensus` を再確認。
- `working -> consensus` は `patch+approval` のみ許可であることを再確認。
- canonical No-Go 5 IDs（`preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`）を再確認し、差分 0 件。
- CE0契約ID（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）は参照のみで再定義なし。

### Phase 2 Plan（contract-only / single-file）
- Scopeを本Issue単体の契約記述と実行記録追記に限定。
- Non-Goals（実装変更、語彙再定義、SafeMode後退、未承認事項の確定化）を再確認。
- AC/DoD不足は未検出。新規ドラフト提案は不要と判定。

### Phase 3 ADR Consensus
- 方針差分判定を実施し、結果は `No ADR delta`。
- 方針差分が将来発生する場合のみ Context/Decision/Consequences を追記し、承認まで `held` を維持するルールを継続。

### Phase 4 Execute（contract文言のみ更新）
- 編集対象を `01_Plans/issues/issue-CE0-core-graph-repositioning.md` のみに固定して更新。
- `role / transition / no-go` 固定語彙を維持し、同義語置換・拡張定義を行わない。
- SafeMode既定ON境界を後退させる記述を追加しない。

### Verify（docs-check / self-repair <= 3）
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- Verify失敗は発生せず、自己修復回数は 0/3。

### Proceed
- Proceed条件（AC/DoD充足 + docs-check pass）を満たすことを確認。
- 判定: `Done`（contract-only / single-file / 語彙固定 / SafeMode境界維持）。
- 未承認事項在庫: なし。将来発生時は `held/pending` で在庫化し、確定しない。

## Phase Execution Record（2026-04-27 / Stream C / user-requested phase order strict run）
### Phase 1 Read（語彙差分チェック）
- Phase開始時に `role / transition / no-go` 語彙差分チェックを実施し、差分 0 件（`working` / `context_projection` / `consensus`、`working -> consensus` + `patch+approval`、canonical 5 IDs を維持）。
- CE0契約ID（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）は参照のみで再定義なし。
- SafeMode境界（既定ON維持、緩和禁止）に差分なし。

### Phase 2 Plan（語彙差分チェック）
- Phase開始時に再Readし、`role / transition / no-go` と禁止事項の差分を再確認、差分 0 件。
- Scopeを本Issue単体の記録追記に限定（docs-only / contract-only / single-file）。
- 禁止事項（実装変更、CE0契約ID再定義、No-Go語彙変更）を再確認。

### Phase 3 ADR Consensus（Context / Decision / Consequences、語彙差分チェック）
- Phase開始時に語彙差分チェックを実施し、差分 0 件。
- Context: CE0 Core Graph責務境界を契約固定のまま維持し、未承認事項の確定化を回避する必要がある。
- Decision: `No ADR delta`。既存契約（role/transition/no-go、SafeMode境界）を維持し、新規承認事項は追加しない。
- Consequences: 未承認論点が発生した場合は `held` または `pending` を維持し、承認完了まで確定しない。

### Phase 4 Execute（語彙差分チェック）
- Phase開始時に語彙差分チェックを実施し、差分 0 件。
- 本Issueへの実行記録追記のみを実施（実装記述追加なし、他ファイル編集なし）。
- contract-only 境界と固定語彙を維持。

### Verify（語彙差分チェック / 自己修復最大3回）
- Phase開始時に語彙差分チェックを実施し、差分 0 件。
- verify attempt_1: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` → pass。
- verify attempt_1: `git diff --check` → pass。
- 自己修復回数: 0/3（上限超過なし）。

### Proceed（語彙差分チェック）
- Phase開始時に語彙差分チェックを実施し、差分 0 件。
- 判定: `Done`（Read → Plan → ADR Consensus → Execute → Verify → Proceed の順序を満たし、docs-check pass）。
- 未承認事項在庫: なし（新規 `held/pending` 追加なし）。


## Phase Execution Record（2026-04-27 / Stream C / CE0 Core Graph Repositioning strict serial run）
### Phase 1 Read
- Phase開始時Read同期を実施し、`role / transition / no-go` 固定語彙、CE0契約ID read-only 制約、SafeMode既定ON境界を再確認した。
- 差分判定: 語彙・禁止事項・SafeMode境界の差分は 0 件で、停止条件は未発火。

### Phase 2 ADR/CDC（Context / Decision / Consequences）
- Phase開始時Read同期を再実施し、方針差分の有無を確認した。
- Context: CE0 Core Graph責務境界を proposal-only の契約固定として維持する必要がある。
- Decision: `No ADR delta`（契約語彙固定で継続、未承認事項は確定しない）。
- Consequences: 未承認事項が発生した場合は `pending` または `held` で在庫化し、承認まで確定化しない。

### Phase 3 Plan（契約境界・非目標・検証）
- Phase開始時Read同期を再実施し、Phase 2との差分なしを確認してから計画を固定した。
- Plan: single-file / docs-only / contract-only を維持し、Core Graph直接更新を許容しない（proposal-only前提を維持）。
- Non-Goals: 実装変更、CE0契約ID再定義、No-Go語彙拡張、SafeMode既定ON後退、未承認事項の確定化。
- Verification plan: `docs-check` と `git diff --check` を実行し、失敗時は自己修復最大3回で打ち切る。

### Phase 4 Execute（契約文面のみ）
- Phase開始時Read同期を再実施し、差分 0 件を確認してから本Issue本文の実行記録のみ追記した。
- 編集対象は `01_Plans/issues/issue-CE0-core-graph-repositioning.md` のみとし、他ファイル編集は行わない。

### Verify（安全境界と整合）
- Phase開始時Read同期を再実施し、語彙・禁止事項・SafeMode境界の差分 0 件を確認した。
- verify attempt_1: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` → pass。
- verify attempt_1: `git diff --check` → pass。
- Self-Correction実績: 0/3（上限超過なし）。

### Proceed（Go / Conditional / No-Go）
- Phase開始時Read同期を再実施し、Proceed判定条件（AC/DoD充足 + docs-check pass）を確認した。
- 判定: `Go=Done`（contract-only / proposal-only / single-file 制約を維持）。
- Conditional/No-Go該当: なし。未承認事項在庫: なし（新規 `held/pending` 追加なし）。

## Phase Execution Record（2026-04-27 / Stream C / CE0 strict serial rerun-2）
### Phase 1 Read
- Phase開始時Read同期を実施し、`role / transition / no-go` 固定語彙（`working` / `context_projection` / `consensus`、`working -> consensus` + `patch+approval`、canonical 5 IDs）を再確認。
- 差分判定: 語彙・禁止事項・SafeMode境界の差分は 0 件。ドリフトは未検出。

### Phase 2 ADR/CDC
- Phase開始時Read同期を再実施し、方針差分の有無を確認。
- Context: CE0 Core Graph Repositioning は contract-only で契約固定を継続する。
- Decision: `No ADR delta`（CE0契約ID再定義なし、語彙固定維持、未承認事項の確定化なし）。
- Consequences: 未承認事項が発生した場合は `held` または `pending` で管理し、承認まで確定しない。

### Phase 3 Plan
- Phase開始時Read同期を再実施し、Phase 2との差分なしを確認。
- Scope: 本Issue 1ファイルの実行記録追記のみ（single-file / docs-only / contract-only）。
- Non-Goals: 実装変更、CE0契約ID再定義、語彙同義語拡張、SafeMode既定ON後退、未承認事項の確定化。

### Phase 4 Execute
- Phase開始時Read同期を再実施し、固定語彙・禁止事項・SafeMode境界の差分なしを確認して実行。
- 実行内容は本Issue本文への追記のみ。実装ファイル・他ドキュメントは変更しない。

### Verify
- Phase開始時Read同期を再実施し、語彙差分・禁止事項逸脱・SafeMode境界ドリフトがないことを確認。
- verify attempt_1: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` → pass。
- verify attempt_1: `git diff --check` → pass。
- self-correction 実績: 0/3（上限超過なし）。

### Proceed
- Phase開始時Read同期を再実施し、Proceed条件（AC/DoD充足 + docs-check pass）を確認。
- 判定: `Done`（Read → ADR/CDC → Plan → Execute → Verify → Proceed の固定順序を満たす）。
- フェイルセーフ該当: なし（語彙・禁止事項・safeMode境界ドリフトなし、未承認事項確定化要求なし、self-correction上限超過なし）。

## Phase Execution Record（2026-04-28 / Stream C / CE0 core graph boundary contract freeze run）
### Phase 1 Read
- 固定語彙と既存契約との差分を再読し、`working` / `context_projection` / `consensus` の3語彙、`working -> consensus` + `patch+approval`、canonical 5 IDs の差分が 0 件であることを確認。
- CE0契約ID（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）は参照のみとし、再定義・拡張・別名化を行わないことを確認。

### Phase 2 ADR/CDC（Context / Decision / Consequences）
- Context: CE0 Core Graph Repositioning の目的は責務境界契約の固定であり、語彙再定義・拡張を禁止したまま運用する必要がある。
- Decision: `No ADR delta`。契約は既存固定を維持し、`working` は編集作業領域、`context_projection` は read-only投影、`consensus` は承認済み合意領域として責務境界を固定する。
- Consequences: 未承認論点は `held` または `pending` の在庫として扱い、推測確定を禁止する。

### Phase 3 Plan
- AC/DoD不足を点検し、契約境界・禁止事項・検証導線（docs-check）を満たすための追補は不要と判定。
- Planを single-file / docs-only / contract-only に固定し、実装変更・依存仕様の推測確定・指定外編集要求への追従を非目標として明示。

### Phase 4 Execute
- 契約文言整備のみを実施し、責務境界契約を以下で固定:
  - `working`: 編集作業領域（proposal生成は可、合意領域への直接反映は不可）
  - `context_projection`: read-only投影（直接編集不可）
  - `consensus`: 承認済み合意領域（`patch+approval` 経由のみ更新可）
- 語彙再定義・同義語置換・拡張定義は実施しない。

### Verify（docs-check）
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- 自己修復回数は 0/3。上限超過・前提崩れ・指定外編集要求は発生なし。

### Proceed（Go / Conditional / No-Go）
- 判定: `Go=Done`（AC/DoD整合、docs-check pass、contract-only維持）。
- Conditional: なし。
- No-Go: 該当なし（`preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation` の新規発生なし）。

## Phase Execution Record（2026-04-28 / Stream C / CE0責務境界契約専任 run-2）
### Phase 1 Read（語彙差分検知）
- `role` 固定語彙（`working` / `context_projection` / `consensus`）を再読し、差分 0 件を確認。
- `transition` 固定（`working -> consensus` は `patch+approval` のみ）を再読し、差分 0 件を確認。
- `no-go` は canonical 5 IDs（`preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`）固定で差分 0 件。

### Phase 2 ADR/CDC（必要時のみC/D/C+承認）
- 方針差分の有無を判定し、`No ADR delta` を確認。
- Context/Decision/Consequences の新規承認要求は発生していないため、承認フロー起動は不要。
- 未承認論点の推測確定を禁止し、必要時は `held` 維持方針を再確認。

### Phase 3 Plan（AC/DoD不足ドラフト提案）
- AC/DoD の不足有無を点検し、不足は未検出。
- 本実行の計画を single-file / docs-only / contract-only に固定。
- 停止条件（safeMode後退 / no-go語彙変更 / allowlist外編集）発火時は即停止する計画を再確認。

### Phase 4 Execute（契約文言のみ）
- 契約文言の整合確認と実行記録追記のみを実施。
- 実装変更（handler/UI/DB/worker/API/schema migration）は未実施。
- allowlist対象外ファイルの編集は未実施。

### Verify（最大3回自己修復）
- verify attempt_1: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` → pass。
- verify attempt_1: `git diff --check` → pass。
- 自己修復は 0/3（不整合未検出）。

### Proceed（Go / Conditional / No-Go）
- 判定: `Go=Done`。
- Conditional: なし（未承認事項の追加なし）。
- No-Go: 該当なし（safeMode後退なし / no-go語彙変更なし / allowlist外編集なし）。

## Phase Execution Record（2026-04-28 / Stream C / CE-0 contract freeze only run-3）
### Phase 1 Read
- 対象2ファイル（`issue-CE0-contract-freeze.md` / `issue-CE0-core-graph-repositioning.md`）の最新状態を再読。
- CE0契約ID（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）の再定義禁止、canonical No-Go 5 IDs 固定、safeMode境界固定（`safeMode=true` / `allowUnreviewedText=false`）を再確認。

### Phase 2 Plan（不足抽出ドラフト）
- 不足候補A: CE1/CE2へ渡すI/F freezeの最小受領条件が散在しがちだったため、受領条件を単一ノート化する必要を特定。
- 不足候補B: 禁止事項の機械判定キー（No-Go canonical IDs）を I/F freeze ノート側へ明示連結する必要を特定。
- 不足候補C: 検証項目の機械実行可否（`docs-check` / `git diff --check`）を Proceed 前提として明文化する必要を特定。
- ドラフト判定: いずれも新規ID追加不要で、既存契約ID参照のみで補完可能。

### Phase 3 Execute（contract-only / mocks-first 文言固定）
- 方針固定:
  - contract-only: 実装詳細（handler/UI/DB/worker/API/schema migration）を記述しない。
  - mocks-first: CE1/CE2は mock入力で I/F 検証し、実装確定を先行しない。
- 文言固定:
  - role: `working` / `context_projection` / `consensus` の3語彙のみ。
  - transition: `working -> consensus` は `patch+approval` のみ。
  - no-go: canonical 5 IDs 以外の追加・同義語置換を禁止。

### Phase 4 Verify（機械チェック可能性確認）
- AC/DoD/禁止事項は以下で機械チェック可能であることを確認:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `git diff --check`
  - `rg -n "preview_bypass|consensus_direct_write|auto_apply_or_publish|ai_review_auto_promotion|safemode_default_relaxation" 01_Plans/issues/issue-CE0-core-graph-repositioning.md`
- 自己修復ポリシーは最大3回。4回目相当は `stopped_for_clarification` で停止。

### Phase 5 Proceed（CE1/CE2向け I/F freeze note）
- freeze_note_id: `CE0-IF-FREEZE-2026-04-28-C`
- handoff_scope: CE1/CE2は以下を **read-only参照** する（再定義禁止）。
  1) Contract IDs: `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`
  2) role: `working` / `context_projection` / `consensus`
  3) transition: `working -> consensus` = `patch+approval` only
  4) No-Go canonical IDs: `preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`
- fail-safe:
  - 契約ID競合、禁止事項の曖昧化要求、自己修復4回目相当が発生した場合は即 `held` で停止。
- proceed_decision: `Conditional-Go`（I/F freezeは固定済み。未承認事項の確定化は継続禁止）。

## Phase Execution Record（2026-04-28 / Stream C専任 / CE0 strict serial Read→Plan→Execute→Verify→Proceed）
### Phase 1 Read（Read同期）
- 対象ファイルを冒頭から再読し、固定語彙 `working` / `context_projection` / `consensus`、許可遷移 `working -> consensus` + `patch+approval`、No-Go canonical 5 IDs を再確認。
- 直前記録との差分確認: 語彙差分 0 件、禁止事項差分 0 件、SafeMode既定ON境界の後退 0 件。
- API/Data型依存の扱いを再確認: mock I/F 定義を前提に依存切断し、実装変更は行わない。

### Phase 2 Plan（Read同期）
- Phase開始時にRead同期を再実施し、Phase 1 からの語彙・禁止事項・SafeMode境界差分が 0 件であることを確認。
- Scopeを `01_Plans/issues/issue-CE0-core-graph-repositioning.md` のみへ固定し、contract-only / docs-only / single-file を維持。
- Non-Goals: handler/UI/DB/worker/API/Schema migration を含む実装変更、CE0契約ID再定義、No-Go語彙変更、SafeMode既定緩和。
- Self-Correction方針: Verify失敗時の自己修復は最大3回、4回目相当は実施せず停止報告。

### Phase 3 Execute（Read同期）
- Phase開始時にRead同期を再実施し、固定語彙の不一致がないことを確認後に実行。
- 実施内容は本Issue内の実行記録追記のみ（他ファイル不干渉）。
- API/Data型依存は mock I/F 前提で記述し、実装側の変更提案・追加は行わない。

### Phase 4 Verify（Read同期）
- Phase開始時にRead同期を再実施し、`role / transition / no-go`・SafeMode境界・CE0契約ID read-only 制約の維持を確認。
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- Self-Correction実績: 0/3（上限超過なし）。

### Phase 5 Proceed（Read同期）
- Phase開始時にRead同期を再実施し、Proceed条件（AC/DoD充足 + docs-check pass）を照合。
- 判定: `Done`（Read→Plan→Execute→Verify→Proceed の直列フローを遵守）。
- ADR論点: 新規発生なし（`No ADR delta`）。発生時は `Context / Decision / Consequences` と承認完了まで `held` 維持。
- 未承認事項在庫: なし。将来発生時は self-correction 3回上限を超える前に停止報告する。


## Phase Execution Record（2026-04-29 / Stream B CE0 interface-freeze synchronized update）
### Phase 1 Read
- Phase開始時に本Issueを再読し、`role / transition / no-go` 固定語彙に差分なしを確認。
- AC/DoD不足として「イベント契約の明示」と「mock切断準備完了条件」の不足を検知。

### Phase 2 Interface Freeze
- `working -> consensus` の `patch+approval` をイベント契約として固定：
  - `proposal.submitted`
  - `proposal.approval_requested`
  - `proposal.approved`
  - `consensus.patch_applied`
- canonical 5 IDs と safeMode境界を不変として保持。

### Phase 3 Mock Decoupling
- 他実装は mock emitter/consumer により上記4イベントだけで進行可能と定義。
- direct write / auto-apply 系イベントは contract level で不許可。

### Phase 4 Verify（attempt_1）
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` pass。
- `git diff --check` pass。
- self-correction `0/3`。

### Phase 5 Gate
- 判定: `Conditional-Go`（契約凍結としては完了）。
- 未承認項目: HTTP API具体path/payloadの確定（CE1担当）を `pending` で保持。

## Phase Execution Record（2026-04-29 / Stream C専任 / CE0 Core Graph Repositioning strict serial run）
### Phase 1 Read
- Phase開始時Readを実施し、固定語彙 `working` / `context_projection` / `consensus`、許可遷移 `working -> consensus` + `patch+approval`、canonical No-Go 5 IDs、SafeMode既定ON境界の差分が 0 件であることを確認。
- 役割再配置契約の対象を `working` / `context_projection` / `consensus` に限定し、他領域は非対象であることを確認。

### Phase 2 Plan
- Phase開始時Readを再実施し、Phase 1から語彙・禁止事項・SafeMode境界の差分がないことを確認。
- 実行計画を Plan→Execute→Verify→Proceed の直列に固定し、対象ファイルを本Issueのみへ固定。
- 依存切断方針を mock-first とし、他stream参照は I/F 名（`ContextQueryV1` / `ContextBundleV1` / `ProposalPatchV1` / `AuditEventV1`）のみを許可。

### Phase 3 ADR/CDC Consensus（Context/Decision/Consequences 先行確定）
- Context: CE0 Core Graphの役割再配置契約を contract-only で維持し、未承認の仕様確定を防止する。
- Decision: `No ADR delta`。`working` / `context_projection` / `consensus` の責務境界、`working -> consensus` + `patch+approval`、canonical No-Go 5 IDs を不変として維持。
- Consequences: 本記録更新は承認済み契約の再確認に限定。未承認論点が発生した場合は `held` で停止し確定化しない。

### Phase 4 Execute
- Phase開始時Readを再実施し、合意済み Context/Decision/Consequences に一致することを確認後に実行。
- contract-only で本Issueの実行記録のみ更新し、実装変更・スキーマ変更・allowlist外編集は未実施。

### Verify
- Phase開始時Readを再実施し、固定語彙・禁止事項・SafeMode境界の維持を再確認。
- verify attempt_1: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- verify attempt_1: `git diff --check` を実行し、pass。
- Self-Correction実績: 0/3（上限超過なし）。

### Proceed
- Phase開始時Readを再実施し、Proceed条件（AC/DoD充足 + docs-check pass）を確認。
- 判定: `Done`（Plan→Execute→Verify→Proceed 直列、各Phase開始Read、Context/Decision/Consequences先行確定を満たす）。
- 未承認事項在庫: なし。将来発生時は `held` で停止し、Self-Correction 3回上限を超える前に停止報告する。

## Phase Execution Record（2026-04-29 / Stream C / serial Read→Plan→Execute→Verify→Proceed）
### Read（Phase start re-Read + diff check）
- 本Issueを再読し、固定語彙 `working` / `context_projection` / `consensus`、許可遷移 `working -> consensus` + `patch+approval`、canonical 5 IDs、SafeMode既定ON後退禁止に差分なし。
- 直前記録（2026-04-28 freeze）との差分を確認し、contract-only / mock-first 境界の逸脱なし。

### Plan（AC/DoD不足先行確認）
- AC/DoD不足の先行点検を実施し、不足は未検出（ドラフト追補不要）。
- 編集対象を `issue-CE0-core-graph-repositioning.md` のみに固定。
- I/F契約更新は mock-first の文言整合に限定し、実装経路（handler/UI/DB/worker/API/schema migration）を追加しない。

### Execute（I/F contract-only update）
- 本実行記録を追加し、直列ワークフロー（Read→Plan→Execute→Verify→Proceed）と再Read差分確認を明示。
- 既存I/F契約シグネチャ参照（`ContextQueryV1` / `ContextBundleV1` / `ProposalPatchV1` / `AuditEventV1`）の扱いを変更せず、mock-first 前提の契約整合のみ維持。

### Verify（docs-check / self-heal <= 3）
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass（自己修復 0/3）。
- `git diff --check` を実行し、pass。
- `git status --short` で他ファイル編集がないことを確認。

### Proceed
- 判定: `Done`（AC/DoD充足、docs-check pass、他ファイル編集なし、contract-only + mock-first 維持）。
- 停止条件該当なし。自己修復上限（3回）超過なし。

## Phase Execution Record（2026-04-30 / Stream E / CE0 Core Graph Repositioning 専任）
### Phase 1 Read（最新確認）
- 最新Run（2026-04-28）および本Issue全文を再読し、`role / transition / no-go` 固定語彙と SafeMode 境界に差分がないことを確認。
- 編集対象を `01_Plans/issues/issue-CE0-core-graph-repositioning.md` のみに固定し、他ストリーム対象ファイルを編集しない制約を再確認。
- インターフェース依存は実装参照ではなく mock contract で切断して記述する方針を再確認。

### Phase 2 Context / Decision / Consequences 明文化
- Context: CE0 Core Graph repositioning の契約固定を継続しつつ、他ストリーム依存を発火させないため interface coupling を mock contract に限定する必要がある。
- Decision: `No ADR delta`。`working / context_projection / consensus`、`working -> consensus` + `patch+approval`、canonical 5 IDs を維持し、I/F依存は `ContextQueryV1` / `ContextBundleV1` / `ProposalPatchV1` / `AuditEventV1` の mock contract 参照に限定。
- Consequences: 実装層（handler/UI/DB/worker/API）の変更・確定は行わず、未承認事項は `held/pending` のまま保持する。

### Phase 3 Plan → Execute → Verify → Proceed（self-correction 3回）
- Self-correction #1（Plan）: 変更範囲逸脱リスクを点検し、追記対象を実行記録セクションのみに再収束。
- Self-correction #2（Execute）: 文面中の実装示唆を除去し、contract-only / mock-first 表現へ統一。
- Self-correction #3（Verify）: no-go canonical 5 IDs と許可遷移表記を再照合し、語彙ドリフトがないことを確認。
- Execute: 本Issueへ当該記録を追記（他ファイル変更なし）。
- Verify: `docs-check` と `git diff --check` を実行し、エラーなしを確認。
- Proceed: AC/DoD を満たすため判定 `Done`、新規 `held/pending` 在庫は追加なし。

### Phase 4 致命エラー時停止
- 本実行では致命エラー（SC-1〜SC-3）未検出のため停止不要。
- 以後、語彙差分・CE0契約ID再定義・SafeMode既定ON後退・4回目相当再試行が発生した場合は `stopped_for_clarification` で即停止する。

## Phase Execution Record（2026-05-01 / Stream D / CE0 Core Graph Repositioning）
### Phase 1 Read同期
- 本Issueを起点に `role / transition / no-go` 固定語彙、CE0契約ID read-only 制約、SafeMode既定ON境界を再読。
- 差分判定: `working` / `context_projection` / `consensus`、`working -> consensus` + `patch+approval`、canonical 5 IDs に差分なし。

### Phase 2 ADR/CDC
- 判定: `No ADR delta`（方針差分なし）。
- contract-only planning を維持し、未承認事項の確定化を行わない。

### Phase 3 Plan（AC/DoD不足補完）
- AC/DoD/Validation/Stop Conditions を再点検し、不足は未検出。
- 補完ルール確認: 不足検知時はAIドラフト追記のみ実施し、承認まで `held` 維持。

### Phase 4 Execute
- single-file 制約を遵守し、本Issue内の実行記録追記のみを実施。
- 実装変更禁止（handler/UI/DB/worker/API/Schema migration への変更なし）。

### Verify（自己修復最大3回）
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- 自己修復回数: 0/3（追加修復なし）。

### Proceed/Stop
- 判定: `Done`（AC/DoD整合、docs-check pass、proposal-only と contract-only 境界維持）。
- 未定義競合: 検出なし。検出時は `stopped_for_clarification` として停止する。

## Stream B sync run（2026-05-01 / CE0 core graph memo alignment）

### Phase 1 Read
- 本Issueを再読し、`working / context_projection / consensus` と canonical No-Go 5 IDs の固定語彙に差分がないことを確認。
- 編集境界を本Issueファイルのみに固定し、他領域非干渉を再確認。

### Phase 2 ADR/CDC（Context / Decision / Consequences）
- Context: CE0 core graph契約は他CEの前提となるため、語彙揺れや遷移規則の変更を防ぐ必要がある。
- Decision: `working -> consensus` は `patch+approval` のみを許可し、direct write / auto-apply / auto-publish を禁止のまま維持。
- Consequences: 下流ストリームは同一契約語彙でmock検証でき、未承認差分は `held` で隔離される。

### Phase 3 Plan
- AC/DoD不足は検出されず、既存定義のまま進行。
- 実施範囲は contract-only の実行記録追記に限定。

### Phase 4 Execute
- 本Issueに同期ログを追記し、実装記述は追加しない。

### Verify
- attempt_1: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` → pass
- attempt_1: `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` → pass
- attempt_1: `git diff --check` → pass
- self-correction: `0/3`

### Proceed
- 判定: **Done（contract-only維持）**
- 逸脱要求・契約衝突・自己修復上限超過時は `held` 停止。

## Phase Execution Record（2026-05-02 / Stream D 専任 / CE0 Core Graph Repositioning independent completion）
### Phase 1 Read
- 本Issue最新状態を再読し、Scope/Dependencies/想定I/Fを抽出。
- Scope抽出: `working` / `context_projection` / `consensus` の責務固定、`working -> consensus` の `patch+approval` 固定、canonical No-Go 5 IDs 固定。
- Dependencies: `01_Plans/issues/issue-CE0-contract-freeze.md`（契約依存; mockで並行検証可能）
- 想定I/F抽出: `ContextQueryV1` / `ContextBundleV1` / `ProposalPatchV1` / `AuditEventV1`。
- Mock Contract Assumption:
  - `Assumption-CE0-IF-01`: `ContextQueryV1` は query preview 済み入力のみを受理する前提。
  - `Assumption-CE0-IF-02`: `ContextBundleV1` は deterministic `bundleHash` を返却する前提。
  - `Assumption-CE0-IF-03`: `ProposalPatchV1` は proposal-only（auto-apply不可）前提。
  - `Assumption-CE0-IF-04`: `AuditEventV1` は `query/patch/apply` の3イベント追跡が可能な前提。

### Phase 2 CDC（Context / Decision / Consequences）
- Context: Core Graph再配置では `ConsensusGraph` の直接更新を保護しつつ、`WorkingGraph` の提案を可逆に移送できる契約固定が必要。
- Decision:
  - 再配置規則: `working -> consensus` は `patch+approval` のみ許可。
  - 安定性条件: 同一入力・同一制約では同一 `bundleHash` と同一 `proposal diff` を再現可能。
  - 可逆条件: 採用済み提案は監査ログ付きで rollback 可能（proposal履歴が失われない）。
  - 競合規則（固定）:
    - 循環（cycle）: `held` として昇格停止、直接適用禁止。
    - 孤立（orphan）: `working` に留め、`consensus` 昇格禁止。
    - 重複（duplicate）: `proposal` を統合候補として扱い、単独自動採用禁止。
- Consequences:
  - 表示差異: Projection上で候補差分表示は増えるが、Consensus確定面は非破壊維持。
  - 計算コスト: 競合判定（cycle/orphan/duplicate）分の検証負荷が増加。
  - 後方互換: CE0契約IDとcanonical 5 IDsを維持するため破壊的変更は発生しない。

### Phase 3 Plan（AC/DoD補完と擬似テスト観点）
- AC補完提案:
  - AC-7: 再配置ルールは deterministic（同入力同結果）であること。
  - AC-8: 再配置ルールは reversible（rollback可能）であること。
  - AC-9: 競合ケース（cycle/orphan/duplicate）の期待挙動が `held/working/proposal統合候補` で定義済みであること。
  - AC-10: 監査イベント（query/patch/apply）が追跡可能であること。
- DoD補完提案:
  - DoD-5: mock入力群で expected outcome（normal/cycle/orphan/duplicate）を再現できる記述があること。
- 擬似テスト観点（mock cases）:
  - Case-Normal-01: 非競合提案が `patch+approval` 経由で `consensus` に反映。
  - Case-Cycle-01: 循環依存提案は `held` で停止。
  - Case-Orphan-01: 参照欠落提案は `working` に残置。
  - Case-Duplicate-01: 重複提案は統合候補として表示し自動採用しない。

### Phase 4 Execute
- allowlist内（本Issueのみ）で計画を固定し、他ファイル変更を行わない。
- Assumption差替え手順（実契約到着時）:
  1) `Assumption-CE0-IF-01..04` の該当行を実契約IDへ置換。
  2) 置換後に canonical語彙（role/transition/no-go）差分がないことを再確認。
  3) 差分が生じた場合は `held` 化し、承認まで確定しない。
- 他ファイルへの修正要求は提案止まりとし、本Issueからは編集しない。

### Verify（AC/DoD / minimal assumptions / self-correction）
- AC/DoDチェック: 既存AC/DoD + AC-7..10 / DoD-5 提案で contract-only 判定に不足がないことを確認。
- 最小仮定原則チェック: Assumptionは I/F欠落箇所（preview/bundleHash/proposal-only/audit追跡）に限定し、実装詳細の仮定を追加しない。
- Self-Correction:
  - #1: 競合規則に自動確定を含まないことを再点検（問題なし）。
  - #2: SafeMode既定ON後退表現が混入していないことを再点検（問題なし）。
  - #3: allowlist外編集がないことを再点検（問題なし）。

### Proceed
- 判定: **Ready**（Stream C 完了待ちなし、read-only契約参照 + Mock Contract Assumption明示で独立進行可能）。
- 不足契約は `Assumption-CE0-IF-01..04` に局所化済みで、実契約受領後の差替え手順を併記。
- Hold移行条件（将来）: 上流語彙矛盾、未定義競合、allowlist外必須編集、自己修復4回目相当のいずれかを検知した場合は `stopped_for_clarification` で停止。

## Phase Execution Record（2026-05-03 / Stream C / single-file docs-only contract-only strict run）
### Phase 1 Read（Scope/固定語彙/No-Go条件の再確認）
- Scope を `01_Plans/issues/issue-CE0-core-graph-repositioning.md` のみと再確認（single-file / docs-only / contract-only）。
- 固定語彙を再確認：`role`=`working` / `context_projection` / `consensus`、`transition`=`working -> consensus` + `patch+approval`。
- No-Go canonical 5 IDs（`preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`）の不変を再確認。
- 致命条件（未定義競合・依存循環・scope逸脱）監視を有効化し、検出なしのため継続。

### Phase 2 Plan（AC/DoD不足時補完案の先行合意）
- 既存 AC/DoD を再点検し、不足・矛盾は未検出。
- 補完案の新規提案は不要と判定し、既存 AC/DoD を合意済み基準として採用。
- 実施内容を「契約記述整合と実行記録更新のみ」に固定。

### Phase 3 ADR合意（必要時のみ Context/Decision/Consequences）
- 判定: `No ADR delta`（新規の方針差分なし）。
- `Context/Decision/Consequences` の追加起票は不要、未承認事項の確定化は行わない。

### Phase 4 Execute（契約記述と実行記録のみ更新）
- 本Issue本文に本実行記録を追記。
- 実装記述（handler/UI/DB/worker/API/schema migration）は追加しない。
- CE0契約IDは参照のみで利用し、再定義・同義語置換・拡張を実施しない。

### Verify（docs-check + diff整合、3回まで自己修正）
- attempt_1: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` → pass
- attempt_1: `git diff --check` → pass
- self-correction: `0/3`（追加修正なし）

### Proceed（Ready/Hold判定）
- 判定: **Ready**（AC/DoD整合、docs-check pass、single-file/docs-only/contract-only 維持）。
- 致命条件が将来検出された場合は即時 `stopped_for_clarification` へ遷移し `Hold` で停止する。

## Phase Execution Record（2026-05-03 / Stream C / contract boundary reaffirmation）
### Phase 1 Read
- 実行直前Readを実施し、`working` / `context_projection` / `consensus` の責務語彙、`working -> consensus` + `patch+approval`、canonical No-Go 5 IDs、SafeMode既定ON境界を再確認。
- 前Phaseとの差分確認を実施し、語彙差分・禁止事項差分・SafeMode境界差分は 0 件（継続可）。

### Phase 2 Plan（Context/Decision/Consequences）
- Context: CE0 Core Graph 再配置において、`working/context_projection/consensus` の責務境界を contract-only で再固定し、実装変更を禁止したまま運用可能性を維持する必要がある。
- Decision: 本Issue内の契約文言と実行記録の更新のみに限定し、実装変更（handler/UI/DB/worker/API/Schema migration）は行わない。Phase は直列実行とし、各Phase開始時Read同期を必須とする。
- Consequences: 下流実装は既存契約を read-only 参照し、未承認事項は `held/pending` で保持する。契約逸脱の疑いがあれば Proceed を停止する。

### Phase 3 ADR/CDC Consensus（Context/Decision/Consequences）
- Context: 既存CE0契約（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）との整合を維持しつつ責務境界のみ固定する。
- Decision: `No ADR delta`。契約ID再定義なし、語彙拡張なし、`working -> consensus` の `patch+approval` 以外の遷移を追加しない。
- Consequences: 合意待ち論点が発生した場合は確定化せず `held` で停止し、承認待ちへ移行する。

### Phase 4 Execute
- contract-only 境界を維持し、本Issue本文のみ更新。
- `role / transition / no-go` を固定語彙で再確認し、実装挙動を規定する新規記述は追加しない。

### Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- Verify失敗回数は 0/3。運用規律として「Verify失敗が3回を超過、または競合検知時は即停止」を再確認。

### Proceed
- 判定: `Done`（contract-only 境界維持、AC/DoD整合、docs-check pass）。
- 未承認事項在庫: なし（新規 `held/pending` 追加なし）。

## Phase Execution Record（2026-05-03 / Stream C / contract-vs-implementation diff separation）
### Phase 1 Read
- 実行直前Readを実施し、固定語彙（`working` / `context_projection` / `consensus`、`working -> consensus` + `patch+approval`）と canonical No-Go 5 IDs を再確認。
- Read同期〜Proceed の強制順序と、各Phase開始時Read義務を再確認。
- SafeMode既定ON境界（`CE0-SAFEMODE-IF`）に後退差分がないことを確認。

### Phase 2 Plan
- Scope を本Issue単体の契約記述整理に限定（single-file / docs-only / contract-only）。
- **差分分離方針を固定**:
  - Contract Diff: 契約語彙・遷移規則・No-Go・停止条件の変更/追記のみを記録対象とする。
  - Implementation Diff: handler/UI/DB/worker/API/schema migration 等の実装差分は本Issueでは扱わず、別タスクに分離する。
- 契約が曖昧な場合は実装へ進まず、`Context/Decision/Consequences` を先に確定する。

### Phase 3 ADR/CDC Consensus（Context/Decision/Consequences）
- Context: Core Graph再配置で契約と実装を混在させると、CE0凍結境界が崩れ検証不能になる。
- Decision: 本Issueでは Contract Diff のみ確定し、Implementation Diff は `pending` 管理で分離する。契約曖昧性がある場合は実装着手禁止。
- Consequences: 下流実装は承認済み契約を read-only 参照し、曖昧点は `held` として在庫化してから合意形成を行う。

### Phase 4 Execute
- 本Issueに「Contract Diff / Implementation Diff 分離」と「契約曖昧時は Context/Decision/Consequences 先行確定」の運用規則を明文化。
- 実装記述の追加・推測・代替設計の確定化は行わない。

### Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- 自己修復回数: 0/3（追加修正なし）。

### Proceed
- 判定: `Done`（Read同期〜Proceed順守、contract-only維持、差分分離方針を明記、docs-check pass）。
- 未承認事項在庫: なし（新規 `held/pending` 追加なし）。

## Phase Execution Record（2026-05-03 / Stream C / candidate-adr-clarification for contract-only）
### Phase 1 Read
- 対象ファイルを再読し、固定キー `Status / Priority / Scope / Dependencies / Related ADR/Spec` を確認。
- 差分判定: 想定差分なし（`Status: Open`、`Priority: P1`、`Scope: 01_Plans/issues（docs-only / contract-only / mock-first）`、`Dependencies: CE-0`、`Related ADR/Spec: ADR-0028, 02_Architecture/schemas.md`）。
- `role / transition / no-go` 固定語彙、SafeMode既定ON境界、single-file 制約に変更なし。

### Phase 2 ADR明文化（候補・未確定）
- Context（候補）: CE0 Core Graph Repositioning は contract-only / mock-first 前提で、`working / context_projection / consensus` の責務境界を実装非依存で参照可能に保つ必要がある。
- Decision（候補）: 本Issueでは契約記述整備のみを行い、`working -> consensus` の `patch+approval` 以外の遷移は追加しない。承認前は確定扱いにせず `候補` として保持する。
- Consequences（候補）: 後続実装は承認済み契約のみ参照し、未承認論点は `held` で停止管理する。SafeMode既定ONの後退を伴う変更は受理しない。

### Phase 3 Plan
- AC/DoD は既存定義で不足なし（追加ドラフト不要）。
- Non-goals を再明記: 実装変更禁止、指定外ファイル編集禁止、契約ID再定義禁止。
- 合意前確定禁止を適用し、Phase 2 は候補状態を維持。

### Phase 4 Execute
- 実施内容は本Issueへの実行記録追記のみ（single-file / docs-only / contract-only）。
- 契約語彙の一貫性（`role / transition / no-go`）を維持し、実装記述は追加しない。

### Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- Self-Correction: 0/3（失敗なし）。

### Proceed/Stop
- 判定: `Proceed (Ready)`（docs-check観点 pass、single-file 制約遵守、候補は未確定維持）。
- 停止条件発生時（語彙差分/前提崩壊/未定義競合/範囲外編集要求）は `held` で即停止する。

## Stream D Execution Record（2026-05-04 / Core Graph責務境界再配置 / proposal-only contract lock）

### Phase 1: As-Is整理（Read同期→抽出）
- Read同期を実施し、本Issueに固定済みの `role / transition / no-go` と SafeMode境界を再確認（差分なし）。
- Core Graph責務境界（As-Is）を以下で抽出。
  - `working`: 編集作業領域（提案生成の起点）。
  - `context_projection`: read-only投影（直接更新禁止）。
  - `consensus`: 承認済み合意領域（`patch+approval` 以外の経路禁止）。
- 禁止事項（proposal-only維持のための不変条件）を再確認。
  - `consensus_direct_write`（直接更新禁止）
  - `auto_apply_or_publish`（自動適用/公開禁止）
  - `preview_bypass`（Preview迂回禁止）
  - `ai_review_auto_promotion`（AIレビュー自動昇格禁止）
  - `safemode_default_relaxation`（SafeMode既定緩和禁止）

### Phase 2: ADR-style 明文化（Context / Decision / Consequences）
#### Context
- CE0 Core Graphの責務境界を再配置しても、proposal-only運用（提案→承認→反映）を壊さない契約が必要。
- 既存運用は contract-only であり、実装変更なしで監査可能性・可逆性を担保する必要がある。

#### Decision
- Core Graph再配置の契約は以下で固定する。
  1) `context_projection` と `consensus` への直接更新を禁止する（更新経路は `working -> consensus` の `patch+approval` のみ）。
  2) すべての反映候補は proposal（`ProposalPatchV1`）として生成し、Previewを経由して承認可否を判定する。
  3) 監査可能性のため、遷移イベントを `AuditEventV1` として記録し、ロールバック可能な差分単位を保持する。
  4) SafeMode既定ONを後退させる再配置案は受理しない。

#### Consequences
- 直接更新経路が遮断されるため、proposal-only契約は維持される。
- 実装待ち要素は mock I/F で先行検証可能となり、承認前の不可逆変更を回避できる。
- 監査ログと差分保持により、事後検証およびロールバック判断が可能となる。

### Phase 3: I/F先行・mock戦略（契約粒度の固定）
- CG入力契約（mock置換可能）
  - `ContextQueryV1`: 対象範囲、制約、SafeMode状態、実行者ロールを受領。
  - `ContextBundleV1`: `working/context_projection/consensus` の参照スナップショットを返却（read-only部を明示）。
- CG出力契約（proposal-only）
  - `ProposalPatchV1`: `working -> consensus` に適用可能な差分提案のみを返却。
  - `AuditEventV1`: `requested / previewed / approved / applied / rolled_back` のイベント境界を記録。
- イベント境界
  - 許可: `requested -> previewed -> approved -> applied`。
  - 禁止: `requested -> applied` の直行、`consensus` への直書き。
- 実装待ち箇所のmock分割
  - Query生成、Bundle取得、Patch生成、Audit記録を独立モジュール想定で分離し、各モジュールはfixtureで代替可能なI/Fに固定。

### Phase 4: 実行計画（直列Phase分割）
1. 契約確定Phase
   - `role / transition / no-go / SafeMode` を本Issue契約に固定。
2. 検証計画Phase
   - `docs-check` + 語彙逸脱チェック + direct write経路不在チェックを実施。
3. 受入基準Phase
   - AC/DoD満了時のみ `Done`。未承認論点は `held/pending` で終了。

### Phase 5: Verify（AC/DoD自己検証・未解消リスク・停止基準）
- AC/DoD自己検証
  - AC-1〜AC-6: 本追記はCE0契約ID参照限定、3 role固定、`patch+approval` 固定、canonical 5 IDs 維持、`held/pending` 原則維持、`docs-check` 手順維持を満たす。
  - DoD-1〜DoD-4: 単一ファイル更新、Phase順序明記、検証手順維持、Proceed条件維持を満たす。
- 未解消リスク一覧
  1) 実装層で将来 direct write 経路が混入するリスク（本Issueは契約固定のみで実装拘束は未実施）。
  2) `AuditEventV1` 永続化粒度の差異により、ロールバック証跡が不足するリスク。
  3) mock I/F と実装I/F の乖離リスク（統合時に再検証が必要）。
- 停止基準（再確認）
  - 語彙差分検出、CE0契約ID再定義兆候、SafeMode既定ON後退兆候、docs-check 4回目相当の再試行要求が発生した場合は即停止（`held` または `stopped_for_clarification`）。

## Stream B sync note（2026-05-04 / CE0 Core Graph / handoff consistency）

### Phase 1 Read
- `02_Architecture/api.md` / `02_Architecture/schemas.md` の I/F凍結追記と整合を確認。

### Phase 2 Plan
- Core Graph側は Contract Diff のみ参照し、Implementation Diff は継続して対象外とする。

### Phase 3 Execute
- 本Issueへ整合メモのみ追記（contract-only）。

### Phase 4 Verify
- `docs-check` 対象コマンドを issue-CE0-contract-freeze 側と同一で実施し整合確認。

### Phase 5 Proceed
- 判定: `Done`（role/transition/no-go 語彙に差分なし、proposal-only境界維持）。

## Phase Execution Record（2026-05-04 / Stream C / CE0-core-graph-repositioning plan-contract alignment）
### Read
- 本Issueを再読し、`role / transition / no-go` 固定語彙、CE0契約ID read-only 制約、SafeMode既定ON境界を確認。
- 差分判定: `working / context_projection / consensus`、`working -> consensus` + `patch+approval`、canonical 5 IDs に変更なし。

### ADR/CDC
- 判定: `No ADR delta`（方針差分なし）。
- Context/Decision/Consequences の新規確定は行わず、未承認論点は必要時 `held` 維持。
- mock I/F 定義のみ許可の制約に従い、下流参照用シグネチャは文書上の参照に限定。

### Plan
- 目的を「CE0 core graph repositioning の計画・契約整合」に限定。
- スコープを `01_Plans/issues/issue-CE0-core-graph-repositioning.md` 単一ファイルに固定。
- 禁止事項（実装変更、他issue参照更新、語彙再定義、SafeMode後退）を再確認。

### Execute
- contract-only で本実行記録を追記し、既存契約文言との整合のみ実施。
- mock I/F は `ContextQueryV1` / `ContextBundleV1` / `ProposalPatchV1` / `AuditEventV1` の参照定義のみを維持し、挙動実装を追加しない。

### Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- Self-Correction 実績: 0/3（再修正なし）。

### Proceed
- 判定: `Done`（AC/DoD整合、docs-check pass、single-file/contract-only 制約遵守）。
- 停止条件発生なし。失敗時は Self-Correction 最大3回、超過時 `stopped_for_clarification` で停止する。

## Stream E latest run（2026-05-04 / CE0 Core Graph prohibition clarity）

### Phase 1 Read同期
- A1上流契約との整合、safeMode非後退、Core Graph direct write禁止を再読確認。

### Phase 2 Plan（AC/DoD明確化）
- AC: CE0/CE1境界明示とA2/A3参照導線。
- DoD: 未承認確定ゼロ、依存リンク切れゼロ、停止条件明記。

### Phase 3 Execute（文書更新）
- Core Graph運用を contract-first で再明記: `working -> consensus` は `patch+approval` のみ。
- `ContextQuery/ContextBundle` は CE1契約I/Fとして参照し、実装確定は行わない。
- A2 mock-first先行可、A3接続は契約凍結順守を前提にする。

### Phase 4 Verify
- 3Issue横断で no-go語彙と proposal-only 表現を照合し不一致なし（self-fix 0/3）。

### Phase 5 Proceed（Stream B/C handoff）
- 固定I/F一覧: CE1 v1 contract IDs（`CE1-CTXQ-IF`/`CE1-CTXB-IF`/`CE1-HASH-DET-IF`/`CE1-PREVIEW-GATE-IF`）。
- 禁止事項一覧: direct write / auto-apply / auto-publish / preview bypass / safeMode緩和。
- 検証前提: mock-first + held運用（未承認事項は確定扱い禁止）。

## Phase Execution Record（2026-05-04 / Stream C / CE0 core graph role-transition-audit contract lock）
### Phase 1 Read
- 最新再読を実施し、`role / transition / no-go` 固定語彙、CE0契約ID read-only 制約、SafeMode既定ON境界を確認。
- 想定差異確認: 差分なし（`working` / `context_projection` / `consensus`、`working -> consensus` + `patch+approval`、canonical 5 IDs を維持）。

### Phase 2 ADR明文化（Context / Decision / Consequences）
- Context: CE0 Core Graph Repositioning は contract-only で進行し、実装変更なしで graph role / transition / audit 契約を固定する必要がある。
- Decision: `No ADR delta`。契約は `working` / `context_projection` / `consensus` の3役割、許可遷移は `working -> consensus` の `patch+approval` のみ、No-Go は canonical 5 IDs 固定とする。
- Consequences: 未承認論点は確定せず `held/pending` 維持。承認なしの語彙追加・再定義・SafeMode境界緩和は実施しない。

### Phase 3 Plan（AC/DoD補完提案）
- AC補完提案: `audit` 契約固定を明示し、遷移監査イベントは `AuditEventV1` 参照のみを許可（新規スキーマ導入はしない）。
- DoD補完提案: Verifyで `docs-check` pass かつ `git diff --name-only` が本Issue単一ファイルのみであることを確認する。
- 上記補完提案は既存契約と矛盾しないため、`held` 追加なしで適用可能と判定。

### Phase 4 Execute（graph role/transition/audit 契約固定のみ）
- 本Issue本文内で contract-only 記述を固定し、graph role/transition/audit 契約以外の追記を行わない。
- 実装記述（handler/UI/DB/worker/API/Schema migration）および他ファイル変更は実施しない。

### Verify（自己検証 + 失敗時3回まで修復）
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- `git diff --name-only` を実行し、`01_Plans/issues/issue-CE0-core-graph-repositioning.md` のみ変更であることを確認。
- 修復回数: 0/3（失敗なし）。

### Proceed/Stop
- 判定: `Done`（AC/DoD整合、contract-only維持、docs-check pass、single-file制約充足）。
- 競合・前提崩壊は未検出。検出時は `stopped_for_clarification` で停止する。

## Phase Execution Record（2026-05-04 / Stream C / CE0 Core Graph Repositioning contract-only）
### Phase 1 Read同期
- Phase開始前に本Issueを再読し、`role / transition / no-go` 固定語彙と CE0 canonical 5 IDs に差分がないことを確認。
- CE0契約ID（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）は参照専用であり、再定義禁止を再確認。
- SafeMode境界（既定ON・後退禁止）に変更兆候がないことを確認。

### Phase 2 ADR明文化（Context / Decision / Consequences）
- Context: CE0 Core Graph Repositioning を contract-only で進め、下流実装へは固定契約のみを引き渡す。
- Decision: `No ADR delta`。固定語彙は `working` / `context_projection` / `consensus`、許可遷移は `working -> consensus` + `patch+approval` のみ。
- Consequences: 未承認事項は確定せず `held/pending` 在庫を維持し、推測確定を禁止する。

### Phase 3 Plan（AC/DoD補完提案含む）
- Scope: 本Issue 1ファイル内の契約固定・進行記録更新のみ（single-file / docs-only / contract-only）。
- AC補完提案: 既存 AC-1〜AC-6 で充足しており、新規補完提案は不要（`held` 追加なし）。
- DoD補完提案: 既存 DoD-1〜DoD-4 で充足しており、新規補完提案は不要（自己修復上限3回を維持）。
- Stop Conditions再確認: 語彙差分検出、No-Go逸脱、SafeMode既定ON後退、docs-check 4回目相当は停止。

### Phase 4 Execute（遷移規則・禁止事項の契約固定）
- 遷移規則を契約固定: 許可は `working -> consensus` の `patch+approval` のみ。
- 禁止事項を契約固定: `preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`。
- 実装変更（handler/UI/DB/worker/API/Schema migration）は追加しない。

### Verify（No-Go / 安全境界整合）
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- 自己修復回数: 0/3（停止条件未発火）。

### Proceed/Stop
- 判定: `Proceed = Done`（AC/DoD充足、docs-check pass、No-Go逸脱なし、安全境界整合）。
- `Stop` 判定は不要（未承認の新規 `held/pending` なし）。


## Stream B Sync Snapshot（2026-05-04 / Read&Gap→ADR→Dependency-cut→Verify）

### 1) Dependency / Ready / Blocker 再検証
- dependency_state: `contract-first` を維持（実装完了待ちを Ready 条件に含めない）。
- ready_contract: `freezeContractId/schemaVersion/overridePolicy/safeModeDefault` 一致。
- ready_execution: `approved_by/approved_at/evidence` 充足かつ `Decision Queue Pending=0`。
- blockers_normalized:
  - `approval_pending`
  - `decision_queue_pending`
  - `contract_mismatch`
  - `out_of_scope_request`

### 2) AC/DoD 不足補完ドラフト（合意用）
- AC-draft-1: Ready 判定を `contract-ready` と `execution-ready` に二分し、両方の結果を記録する。
- AC-draft-2: Blocker は正規化4分類のみ使用し、自由記述のみで終わらせない。
- DoD-draft-1: `mock parallelizable items` を最低1件以上列挙する。
- DoD-draft-2: verify の自己修復回数を `<=3` で記録し、`>=4` は停止報告とする。

### 3) 依存切断（実装依存→契約依存）
- replace_rule: 実装依存の待ち条件は、同等の契約キー検証へ置換する。
- mock_parallelizable_items:
  1. Contract ID / fixed key 一致検証
  2. Gate 式（Go/Conditional/No-Go）の入力完全性検証
  3. Audit 4点セット（`query/bundle/proposal/apply`）欠損検知

### 4) Verify（triage再実行）
- command: `python 01_Plans/triage_actionable_plans.py`
- note: Ready/Blocked/Unlocks は triage 出力を正本とし、本Issue記録はその解釈補助とする。
- self_correction: `0/3`（本更新時点）

## Stream B run（2026-05-05 / CE0-core-graph-repositioning / contract-only）

### Phase 1 Read
- 本Issueを再読し、`working` / `context_projection` / `consensus` の固定語彙と `working -> consensus` + `patch+approval` の遷移制約を再確認。
- No-Go canonical 5 IDs と SafeMode既定ON境界の不変条件を再確認。

### Phase 2 Plan（mock前提I/F + AC/DoD補完提案）
- AC補完提案:
  - `ac_transition_guard_mock`: mock遷移で `patch+approval` 以外を拒否する検証観点を明記。
  - `ac_nogo_canonical_lock`: canonical 5 IDs 以外をNo-Goとして追加しないことを検証対象化。
- DoD補完提案:
  - `dod_contract_text_only`: 契約文面更新以外（実装語彙）を差分に含めない。
  - `dod_single_lane_trace`: Verifyで単一レーン（本Issue）更新根拠をログ化。

### Phase 3 ADR合意（Context / Decision / Consequences）
- Context: CE0 Core Graphの責務再配置は語彙/遷移/禁止事項の契約固定が先行条件。
- Decision: 既存固定語彙・遷移規則・No-Go canonical IDsを維持し、v1内拡張を行わない。
- Consequences: 下流streamはmockで遷移検証可能。語彙衝突時は `held` 停止。

### Phase 4 Execute
- 本Issueの実行記録更新のみを実施。
- 実装記述（handler/UI/DB/worker/API）追加は未実施。

### Verify
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` : pass
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` : pass
- `git diff --check` : pass
- 自己修復: 0/3。

### Proceed/Stop
- 判定: **Proceed = Done**（contract-only整合維持）。
- 停止条件: 語彙衝突、No-Go逸脱、SafeMode境界後退、自己修復4回目相当で `held`。


## Stream B run（2026-05-05 / CE0 core graph contract alignment）

### Phase 1 Read
- CE0 Contract Freeze と CE1 Foundation を再読し、Core Graph が **proposal-only** であることを再確認。
- CE0 Core Graph 側で確定できるのは契約I/F境界のみで、反映は承認済み契約経由に限定。

### Phase 2 ADR/CDC
- **Context**: Core Graph再配置が実装タスクへ直結すると、contract freeze の目的（先行I/F固定）が崩れる。
- **Decision**: CE0 Core Graph は `contract-only / mock-first` を維持し、CG系契約IDを「提案境界」として固定。直接反映・自動昇格を禁止。
- **Consequences**: CE1/CE2/CE4 は graph実装未確定でも契約検証を継続可能。競合時は `held` で停止。

### Phase 3 Plan
- AC補強:
  - `ac_core_graph_proposal_only`: Core Graph変更は proposal-only を維持。
  - `ac_no_direct_consensus_write`: Consensus 直接書き込み禁止を継続。
- DoD補強:
  - `dod_if_precedence`: Core Graphより先にCE0/CE1 I/F契約を固定。

### Phase 4 Execute
- CE0→CE1の順序を明記し、Core Graph再配置はI/F契約成立後の参照タスクとして位置づけ。
- 実装依存（UI/DB/worker/API反映）を本文対象外に維持。

### Verify
- docs-check観点自己検証: 1回で完了（self-correction 0/3）。
- 判定: `proposal_only_violation=0` / `dependency_cycle=0` / `scope_deviation=0`。

### Proceed
- CE2/CE4引き渡し前提:
  - Core Graphは契約参照のみ（実装確定なし）。
  - CE1の hash/preview/unknown-key 契約を先行条件として扱う。
  - 未承認確定化要求は `held`。

## Phase Execution Record（2026-05-05 / Stream C / independent-contract run with mock I/F）
### Phase 1 Read
- 本Issue全文を再読し、固定語彙 `role / transition / no-go`、SafeMode既定ON後退禁止、CE0契約ID read-only制約を確認。
- 差分判定: `working / context_projection / consensus`、`working -> consensus` + `patch+approval`、canonical 5 IDs に変更なし（継続可）。

### Phase 2 Plan（AC/DoD不足補完）
- 依存切断方針を明示: 他Stream成果物を前提にせず、必要I/Fは仮契約として扱い mock で検証可能な粒度へ固定。
- AC補完:
  - AC-7: 仮契約I/Fを `ContextQueryV1` / `ContextBundleV1` / `ProposalPatchV1` / `AuditEventV1` の参照名で固定し、実体実装前提の記述を追加しない。
  - AC-8: 競合検知時は推測実装を行わず `held` かつ `stopped_for_clarification` で停止する。
- DoD補完:
  - DoD-5: 検証結果に self-heal 回数（最大3回）を明記する。
  - DoD-6: 他ファイル無変更を `git status --short` で確認し、単一ファイル更新を担保する。

### Phase 3 ADR（Context / Decision / Consequences）
- Context: CE0 Core Graph 再配置の契約固定を継続しつつ、他Stream非依存で検証可能な仮契約I/Fを明文化する必要がある。
- Decision: `No ADR delta`。上流方針の変更は不要とし、既存契約境界の明確化（AC/DoD補完）に限定する。
- Consequences: 未承認事項は確定せず `held/pending` 在庫として扱い、承認まで contract-only を維持する。

### Phase 4 Execute（設計・手順明文化のみ）
- 実装変更は行わず、本Issue内で仮契約I/Fと停止条件運用（競合検知時即停止）を手順として追記。
- `preview_bypass` ほか canonical 5 IDs の語彙、`patch+approval` 以外禁止、SafeMode既定ON後退禁止を維持。

### Verify（docs-check / max 3 self-heal）
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass（self-heal 0/3）。
- `git diff --check` を実行し、pass。
- `git status --short` を実行し、対象ファイルのみ変更を確認。

### Proceed
- 判定: `Done`（AC/DoD充足、docs-check pass、単一ファイル更新、contract-only維持）。
- 未承認事項在庫: なし（新規 `held/pending` は発生せず）。
- 競合検知時即停止・推測実装禁止の fail-safe を再確認。

## Stream B latest run（2026-05-06 / CE0 Core Graph repositioning design progression）

- run_id: `stream-b-ce0-graph-2026-05-06-10`
- assignee: `Stream B（CE0/CE1基盤進行）`
- scope_guard: docs-only / contract-only

### Phase 1 Read（latest + AC/DoD）
- `working` / `context_projection` / `consensus` の3役割固定と、`patch+approval` 単一路遷移を再確認。
- AC/DoD・停止条件（自己修復3回上限）を再確認。

### Phase 2 CE0契約凍結整合
- CE0 canonical 5 No-Go IDs とSafeMode既定ON後退禁止を再確認。
- CE0 Contract IDsは参照のみで再定義なし。

### Phase 3 Core Graph再配置設計
- 再配置設計の契約境界を role/transition/no-go のみに限定し、実装記述は追加しない。
- `working -> consensus` は `patch+approval` のみ許可を維持。

### Phase 4 ContextQuery/Bundle基盤との整合
- CE1へ引き渡す境界を「graph role責務 + no-go + preview gate依存」の契約情報に限定。
- CE1実装詳細への拘束を持ち込まない方針を固定。

### Verify & handoff
- 判定: **Done（contract design freeze maintained）**。
- handoff（CE2/CE4）: graph責務境界の read-only 契約参照。
- self-correction usage: `0/3`。

## Stream B latest run（2026-05-06 / CE0 graph contract + CE1 bridge sync）

### Phase 1 Read同期
- Graph role語彙（`working` / `context_projection` / `consensus`）と `patch+approval` 単一路遷移を再確認。

### Phase 2 I/F先行定義整合
- `ContextQueryV1` / `ContextBundleV1` の I/F先行定義と衝突しないよう、Graph側は role/transition/no-go の契約語彙に限定。

### Phase 3 mock契約依存切断
- CE1未実装でも CE2/CE4 が read-only 契約参照で進行できるよう、Graph側は実装依存記述を追加しない。

### Phase 4 Plan/Execute/Verify/Proceed
- Plan/Execute: contract-only 更新のみ。
- Verify: docs-check前提、自己修復上限3回ルールを維持（本更新 0/3）。
- Proceed: **Done**（語彙・停止条件・safeMode境界の差分なし）。

### Phase 5 Stopper
- `safeMode_default_relaxation` / `consensus_direct_write` を含む canonical No-Go の逸脱があれば即 `held` 停止。

## Stream C update（2026-05-06 / Phase C Read→ADR→Plan→Execute→Verify→Proceed）

### Phase 1 Read（Status / Dependencies整合確認）
- Status再確認: 本Issueは `Open` を維持し、contract-only の凍結管理を継続する。
- Dependencies再確認: `issue-CE0-contract-freeze.md` 参照依存のみ。依存未確定の新規項目は検出なし。
- CE1契約参照境界: CE1関連は参照のみとし、CE1ファイル編集要求は受理しない。

### Phase 2 ADR C/D/C
- Context: CE0はCore Graphの語彙固定が目的であり、下流提案（CE2/CE4）の安全境界を先に守る必要がある。
- Decision: `working / context_projection / consensus`、`working -> consensus (patch+approval)`、canonical No-Go 5 IDs を継続固定する。
- Consequences: 依存未確定の状態遷移を防止できる一方、未承認論点は `held` 在庫として残す運用が必要。

### Phase 3 Plan→Execute（contract-only維持）
- Plan: CE0では契約境界の監視のみ実施し、新規実装I/Fや状態遷移を追加しない。
- Execute: 本Issueへの記録更新のみ実施（実装変更なし）。

### Phase 4 Verify（draft gate/Open移行/非目標）
- Draft gate条件: 語彙差分ゼロ・No-Go語彙不変・SafeMode既定ON後退ゼロ。
- Open移行条件: docs-check pass かつ依存衝突なし（依存未確定の新規発生時は移行停止）。
- 非目標: handler/UI/DB/worker/API実装、CE契約ID再定義、SafeMode緩和。

### Phase 5 Proceed 判定
- 判定: **Proceed（Open維持）**。
- 根拠: 依存追加の未確定要素なし、契約語彙の差分なし、contract-only境界を維持。

## Phase Execution Record（2026-05-06 / Stream C / CE0 core graph contract alignment read-only）
### Read
- CE0契約は `downstream_policy = read-only reference` の前提で再読し、契約ID再定義なしを確認。
- Query Preview 必須条件（`CE0-CTX-IF` の preview経由）を維持し、bypass を禁止する境界を再確認。

### ADR（Context / Decision / Consequences）
- Context: CE0契約依存を read-only 参照しつつ、Core Graph 側の role/transition/no-go 契約整合を固定する。
- Decision: `No ADR delta`。`working / context_projection / consensus` 分離、`working -> consensus` の `patch+approval` のみ許可、`auto_apply_or_publish` を No-Go として維持。
- Consequences: 実装は mock-first で先行可能と明記し、契約固定の範囲を超える論点は `held/pending` へ退避する。

### Plan
- 本Issueの contract-only 記述を維持し、Query Preview 必須・auto-apply/auto-publish 禁止・SafeMode後退禁止を継続条件として固定。
- 変更対象を本Issueファイルの実行記録追記のみに限定。

### Execute
- 契約文面の整合確認結果を追記（コード/スキーマ/運用手順ファイルは未変更）。
- mock 先行検証は許容しつつ、本Issueでは read-only 契約参照のみで完結させる。

### Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。

### Proceed
- 判定: `Done`（contract-only、Query Preview必須維持、auto-apply/auto-publish禁止維持、mock先行可能性を明記）。

## Phase Execution Record（2026-05-06 / Stream C / CE0 core-graph contract lock maintenance）
### Phase 1 Read
- `role / transition / no-go` 固定語彙と SafeMode 境界を再読し、差分なしを確認。
- `issue-CE0-contract-freeze.md` は read-only 契約参照に限定し、mock前提で並行検証可能な依存切断を維持。

### Phase 2 CDC（Context / Decision / Consequences）
- Context: CE0 Core Graph Repositioning の契約固定を single-file / contract-only で継続する。
- Decision: `working` / `context_projection` / `consensus`、`working -> consensus` + `patch+approval`、canonical 5 IDs を不変のまま維持する。
- Consequences: 契約ドリフトと SafeMode 境界後退を抑止し、未承認論点は `held` で確定化しない。

### Phase 3 Plan
- AC/DoD 不足を再点検し、新規不足は未検出（追加提案・合意は不要）。
- 変更範囲を本Issueの契約文面更新のみに固定し、実装変更を行わない。

### Phase 4 Execute
- contract-only 境界を維持し、本Issue本文に実行記録のみを追記。
- CE0契約ID再定義、No-Go語彙拡張、SafeMode既定ON後退を伴う記述は追加しない。

### Phase 5 Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- 自己修復回数は 0/3（超過なし）。

### Phase 6 Proceed
- 判定: `Ready`（AC/DoD整合、docs-check pass、allowlist逸脱なし）。
- 失敗条件（語彙差分、契約ID再定義、SafeMode後退、自己修復4回目相当）発生時は即時 `held` 停止を継続。

## Stream B latest run（2026-05-07 / CE0 core graph repositioning contract confirmation）

### Phase 1 Read
- 対象ファイルを再Readし、`working` / `context_projection` / `consensus` と `working -> consensus`=`patch+approval only` の固定を確認。
- Dependencies drift確認: `issue-CE0-contract-freeze.md` 参照は有効、語彙差分なし。

### Phase 2 ADR（Context / Decision / Consequences）
- Context: CE1契約凍結の前に、CE0 core graph責務境界の語彙固定を再確認する。
- Decision: role/transition/no-go を既存canonical語彙に固定し、同義語置換・追加・再定義を行わない。
- Consequences: CE1のContextQuery/Bundle契約は graph境界への依存が安定化し、CE2/CE4のmock統合条件が明確化される。

### Phase 3 Plan → Execute → Verify → Proceed
- Plan: 契約固定ログ追記のみ、実装/スキーマ更新は対象外。
- Execute: contract-only更新を実施し、safeMode既定境界後退なしを確認。
- Verify: `docs-check` 実施（self-correction 0/3）。
- Proceed: **Approved-to-Proceed（CE0 core graph contract frozen）**。


## Phase Execution Record（2026-05-08 / Stream D / role-transition-no-go contract lock）
### Phase 1 Read
- `working` / `context_projection` / `consensus` の責務境界、canonical No-Go 5 IDs、SafeMode境界を再読し、差分なし。
- 語彙確認結果: `role / transition / no-go` は既存固定語彙のみを使用し、追加拡張要求は未承認のため不採用。

### Phase 2 ADR/CDC Consensus（Context / Decision / Consequences）
- Context: 役割境界が未固定のままだと `consensus` への direct write や自動公開系遷移が混入しうる。
- Decision: 許可遷移を `working -> consensus` の `patch+approval` のみに固定し、禁止遷移を `direct write` / `auto-apply` / `auto-publish` として明示。No-Go語彙は canonical 5 IDs に固定。
- Consequences: 実装非依存の検証軸が安定し、下流実装は同一契約で再現検証できる。

### Phase 3 Plan
- AC/DoDへ「語彙の一貫性」「禁止遷移の明示」「契約のみ更新」を追加して判定軸を固定。
- Scopeは本Issue単一ファイルの契約文言整備のみに限定。

### Phase 4 Execute
- 重複する表現を契約語彙へ統一し、曖昧語（自動反映・自動公開等の同義語展開）を追加せずに整理。
- 実装記述（handler/UI/DB/worker/API）やrole定義拡張は追加しない。

### Phase 5 Verify
- 禁止遷移検証: `direct write` / `auto-apply` / `auto-publish` は禁止として本文に明示されていることを確認。
- 自己修復回数: 0/3（追加修正なしで整合）。

### Phase 6 Proceed
- 判定: `Done`（contract-only、single-file、AC/DoD更新を満たす）。
- 次アクション: 下流は本契約語彙を変更せず検証へ進む。未承認のrole拡張要求が出た場合は `held` で停止。

## Phase Execution Record（2026-05-08 / Stream C / CE0 core-graph repositioning planning freeze reaffirmation）
### Phase 1 Read
- 最新本文を再読し、`working` / `context_projection` / `consensus`、`working -> consensus` + `patch+approval`、canonical No-Go 5 IDs、SafeMode既定ON境界に差分がないことを確認。
- 依存の扱いは read-only 参照に限定し、外部レーン成果を前提にしない独立運用を維持。

### Phase 2 ADR（Context / Decision / Consequences）
- Context: CE0 core graph repositioning の計画固定を継続するには、語彙ドリフトと禁止遷移の混入を防ぐ必要がある。
- Decision: 既存契約を変更せず、`role / transition / no-go` を現行canonical語彙に固定する（No ADR delta）。
- Consequences: 下流実装への前提注入を避けたまま、contract-only の検証軸を維持できる。

### Phase 3 Plan
- AC/DoD不足を再点検し、新規不足なし。追加ドラフト提案は不要と合意。
- 実施内容を本Issue内の計画固定ログ追記のみに限定（single-file / docs-only）。

### Phase 4 Execute
- 計画文書の明確化として実行記録を追記し、契約ID再定義・No-Go拡張・SafeMode後退記述を追加しない。
- 実装依存の挙動記述（handler/UI/DB/worker/API/Schema migration）を追加しない。

### Phase 5 Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- 自己修復回数: 0/3（追加修正なし）。

### Phase 6 Proceed
- 判定: `Done`（AC/DoD充足、docs-check pass、contract-only 維持）。
- 失敗条件発生時は `held` で停止し、推測で依存補完しない運用を継続。

## Phase Execution Record（2026-05-08 / Stream C / CE0 Core Graph Repositioning 専任 run）
### Phase 1 Read
- Read同期を実施し、`role / transition / no-go` 固定語彙、CE0契約ID read-only 制約、SafeMode既定ON境界を再確認。
- 差分判定: 固定語彙・禁止事項・SafeMode境界に差分なし（継続可）。

### Phase 2 ADR
- Phase冒頭Read同期を再実施し、前Phaseとの差分なしを確認。
- ADR整合判定: `No ADR delta`（`ADR-0028` と既存契約固定方針に追加差分なし）。
- 未承認事項は確定せず、必要時 `held/pending` で在庫化する方針を維持。

### Phase 3 Plan
- Phase冒頭Read同期を再実施し、語彙差分なしを確認。
- 変更範囲を本Issue単体の実行記録追記に限定（single-file / contract-only）。
- AC/DoD不足確認: 不足は未検出のため、追加ドラフト提案は不要と判定（合意記録: 既存AC/DoDを採用）。

### Phase 4 Execute
- Phase冒頭Read同期を再実施し、差分なしを確認して実行。
- 本Issue本文への実行記録更新のみ実施し、`working` / `context_projection` / `consensus`、`working -> consensus` + `patch+approval`、canonical 5 IDs を維持。
- 実装変更（handler/UI/DB/worker/API/schema migration）および他ファイル編集は未実施。

### Phase 5 Verify
- Phase冒頭Read同期を再実施し、語彙・禁止事項・SafeMode境界に差分なし。
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- Verify失敗は発生せず、自己修復回数は 0/3。

### Phase 6 Proceed
- Phase冒頭Read同期を再実施し、Proceed前の差分なしを確認。
- 判定: `Done`（AC/DoD整合、docs-check pass、single-file/contract-only制約維持）。
- 停止条件（語彙差分、契約ID再定義、SafeMode既定ON後退、Verify 4回目相当）該当なし。

## Phase Execution Record（2026-05-09 / Stream C専任 / CE0 core graph repositioning planning-to-implementation-prep）
### 1) Read同期
- Phase開始時Readを実施し、`role / transition / no-go` 固定語彙、CE0契約ID read-only 制約、SafeMode既定ON境界を再確認。
- 差分判定: 語彙差分 0 件、No-Go canonical 5 IDs 逸脱 0 件、SafeMode後退兆候 0 件。
- 致命条件の監視対象（語彙差分、契約ID再定義、SafeMode後退、Verify 4回目相当）を再確認。

### 2) Plan（AC/DoD不足時は提案）
- Scopeを `01_Plans/issues/issue-CE0-core-graph-repositioning.md` の契約固定と実行記録更新のみに限定（single-file / contract-only）。
- AC/DoD不足判定: 既存AC-1〜AC-9、DoD-1〜DoD-5で実行可能。新規不足は未検出。
- 不足発生時の運用を再確認: AIドラフトを本Issueへ追記し、明示合意まで `held` を維持。

### 3) Execute（構造変更案・最小差分）
- 構造変更案: 既存5フェーズ（Read同期 → Plan → Execute → Verify → Proceed/Stop）の契約運用を維持し、実装準備は契約境界の再固定に限定。
- 最小差分実施: 本実行記録の追記のみ。`working` / `context_projection` / `consensus`、`working -> consensus` + `patch+approval`、canonical 5 IDs を不変維持。
- 実装記述（handler/UI/DB/worker/API/Schema migration）は追加しない。

### 4) Verify（自己修復最大3回）
- 実行: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`。
- 実行: `git diff --check`。
- 結果: pass。自己修復回数は 0/3（4回目相当は未実施）。

### 5) Proceed/Stop判定（致命条件で停止）
- Proceed判定: `Done`（AC/DoD充足、docs-check pass、single-file / contract-only維持）。
- Stop判定: 致命条件は未発火（語彙差分なし、契約ID再定義なし、SafeMode後退なし、修復上限超過なし）。
- 未承認事項在庫: なし。将来発生時は `held` または `stopped_for_clarification` で停止。

## Phase Execution Record（2026-05-09 / Stream D / CE0 contract-boundary confirmation）
### Phase 1 Read
- 現行メタ（Scope/Non-Goals/AC/DoD/Stop Conditions）と依存（`issue-CE0-contract-freeze.md`）を再読し、契約境界が `contract-only` で固定されていることを確認。
- 非目標（実装変更、Schema migration、契約ID再定義）を再抽出し、allowlist外編集要求は未検出。

### Phase 2 ADR CDC（Context / Decision / Consequences）
- Context: CE0 core graph repositioning を実装へ拡張せず、契約境界のみで確定する必要がある。
- Decision: `role` は `working` / `context_projection` / `consensus`、許可遷移は `working -> consensus` の `patch+approval` のみ、No-Go は canonical 5 IDs のみを維持。
- Consequences: 副作用として実装タスクの前倒し確定を防止し、未承認事項は `held/pending` 在庫のまま維持する。

### Phase 3 Plan（AC/DoD）
- AC再定義なしで既存 AC-1〜AC-9 を採用し、監査可能性は `docs-check` 実行記録と固定語彙トレースで担保。
- DoD再定義なしで既存 DoD-1〜DoD-5 を採用し、非競合性は single-file 更新と allowlist 準拠で担保。

### Phase 4 Execute
- 本Issue本文のみを更新し、他ファイル（実装/図面/スキーマ本体）は未編集。
- `role / transition / no-go` 語彙を固定したまま、契約境界確定の実行記録を追記。

### Phase 5 Verify
- 用語統一: `role / transition / no-go`、canonical 5 IDs、`patch+approval` の表記ゆれなし。
- 依存矛盾: `issue-CE0-contract-freeze.md` 依存前提との矛盾なし。
- allowlist逸脱: 編集対象は `01_Plans/issues/issue-CE0-core-graph-repositioning.md` のみ。
- Self-Correction: 0/3（追加修正不要）。

### Phase 6 Proceed
- 判定: **Ready**（AC/DoDとの矛盾なし、contract-only境界維持、allowlist逸脱なし）。
- 保留理由: なし（未承認事項の新規発生なし）。

## Phase Execution Record（2026-05-09 / Stream C専任 / Core Graph contract-boundary freeze only）
### Phase 1 Read（語彙/role/transition/no-go再確認）
- `role / transition / no-go` 固定語彙を再読し、`working` / `context_projection` / `consensus` の責務境界に差分がないことを確認。
- 許可遷移は `working -> consensus` の `patch+approval` のみ、禁止遷移は `direct write` / `auto-apply` / `auto-publish` のまま維持。
- canonical No-Go 5 IDs（`preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`）の不変を確認。

### Phase 2 ADR（C/D/C）
- Context: Core Graph責務境界は下流実装へ拡張せず、契約固定のみを継続する必要がある。
- Decision: `No ADR delta`。既存契約（role/transition/no-go、SafeMode既定ON後退禁止、direct write禁止）を変更しない。
- Consequences: 未承認/未定義競合は確定化せず `held` に退避し、推測実装を行わない。

### Phase 3 Plan（AC/DoD不足補完ドラフト）
- AC/DoD不足確認の結果、新規不足は未検出。既存 AC-1〜AC-9 / DoD-1〜DoD-5 で判定可能。
- 不足発生時の補完ドラフト方針を再確認: 本Issue内に追記し、明示合意まで `held` 維持。

### Phase 4 Execute（契約文面のみ）
- 実施内容を本Issueの実行記録追記のみに限定し、実装・スキーマ・他ストリームファイルへの変更は行わない。
- `role / transition / no-go` 語彙および fail-safe（safeMode後退禁止、allowlist外編集禁止、未定義競合時停止）を維持。

### Phase 5 Verify（自己修復は最大3回）
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass（self-heal 0/3）。
- `git diff --check` を実行し、pass。
- `git status --short` を実行し、編集対象が `01_Plans/issues/issue-CE0-core-graph-repositioning.md` のみであることを確認。

### Phase 6 Proceed
- 判定: `Ready`（contract-only / single-file / allowlist 準拠 / AC・DoD整合）。
- Stop条件: `direct write許容` / `safeMode後退` / `未定義競合` / `allowlist外編集要求` が発生した場合は即停止。

## Phase Execution Record（2026-05-09 / Stream G / CE0 Core Graph Repositioning 専任）
### 1) Read同期
- Read同期を実施し、`role / transition / no-go / safeMode境界` の固定語彙を再確認。
- 差分判定: `working` / `context_projection` / `consensus` の役割定義差分 0 件、canonical No-Go 5 IDs 逸脱 0 件、SafeMode既定ON後退兆候 0 件。
- Fail-safe前提を再確認: 未定義競合・承認欠落・前提崩れを検知した場合は即 `Stop`。

### 2) ADR明文化（Context / Decision / Consequences + 承認）
- Context: CE0のCore Graphは実装挙動ではなく契約境界（role/transition/no-go/safeMode）として固定し、下流はこの境界を破らず参照する必要がある。
- Decision: 許可遷移は `working -> consensus` の `patch+approval` のみ。禁止遷移は `direct write` / `auto-apply` / `auto-publish`。No-Go語彙は canonical 5 IDs に限定し、同義語置換や拡張を行わない。
- Consequences: 仕様漂流を抑止し、未承認事項は確定せず `held/pending` 在庫として維持する。実装への昇格判断は本Issue外で承認を要する。
- 承認: **contract-only freeze 承認状態を維持（No ADR delta / 追加承認要求なし）**。

### 3) Plan（AC/DoD不足時の補完提案）
- 既存 AC-1〜AC-9 / DoD-1〜DoD-5 を再評価し、不足は未検出。
- 補完提案ルールを再確認: 不足検出時は本Issueに補完ドラフトを追記し、明示合意まで `held` 維持。

### 4) Execute（docs-only）
- 実施内容を本Issueの実行記録追記のみに限定（single-file / docs-only / contract-only）。
- 実装依存記述（handler/UI/DB/worker/API/Schema migration）は追加しない。

### 5) Verify（最大3回 self-correction）
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行し、pass。
- `git diff --check` を実行し、pass。
- `git status --short` を実行し、編集対象が本Issueのみであることを確認。
- self-correction 実績: 0/3（4回目相当は未実施）。

### 6) Proceed / Stop
- 判定: **Proceed（Ready）**。AC/DoD整合、docs-check pass、contract-only境界維持。
- Stop条件監視: 未定義競合・承認欠落・前提崩れは未検出。今後検出時は `stopped_for_clarification` で停止する。


## Stream B execution update（2026-05-09 / CE0-CE1 contract baseline sync）

### Phase 1 Read同期
- 対象3Issueを再読し、編集範囲を `issue-CE0-contract-freeze.md` / `issue-CE0-core-graph-repositioning.md` / `issue-CE1-context-query-bundle-foundation.md` のみに固定。
- CE0 canonical No-Go 5 IDs、`working / context_projection / consensus`、`working -> consensus (patch+approval only)` を差分なしで確認。
- CE1 fixed error semantics（`422 preview_required` / `400 unknown_contract_key` / `409 nondeterministic_bundle`）と hash決定論要件（`queryCanonicalHash` / `bundleHash`）を差分なしで確認。

### Phase 2 Plan（AC/DoD補完提案）
- AC補完提案（CE0）: `preview_bypass` と `consensus_direct_write` が本文内で **禁止語彙として明示** されることを追加。
- AC補完提案（CE1）: closed-world 判定を「未定義キー検知時は常に `400 unknown_contract_key`」で1:1固定することを追加。
- DoD補完提案（共通）: handoff成果物を interface/type/signature のみに限定し、実装TODO・実装依存記述を含めない。

### Phase 3 Execute（契約定義先行 / mock前提分離）
- 実装依存項目は interface/type/signature へ切り出して先行固定し、mock-only検証前提で完了扱い可能な記述へ統一。
- CE0は contract-only boundary を維持し、実装経路（handler/UI/DB/worker/API migration）を追加しない。
- CE1は `ContextQueryV1` / `ContextBundleV1` と固定エラー語彙、hash規約のみを更新対象として維持。

### Phase 4 Verify（整合/依存確認）
- 依存切断確認: CE2/CE4 連携は handoff key（`sourceBundleHash === bundleHash` / `equivalenceKey + bundleHash`）のみで継続可能。
- 衝突確認: contract id collision / error semantics collision / vocabulary collision の新規発生なし。
- self-correction 実績: 0回（追加修正不要）。

### Phase 5 Proceed/Stop
- 判定: **Proceed**（直列フェーズ完了、scope逸脱なし、contract-only維持）。
- Stop条件の再掲: self-correction 3回超過・契約衝突・前提崩壊時は `held` で停止し問い合わせ。

## Stream B latest run（2026-05-10 / CE0 core graph repositioning mock-first implementation）

### Phase 1 Read
- `role / transition / no-go` 語彙と No-Go 5 IDs の固定を再読し、差分なしを確認。
- `CE0-SAFEMODE-IF`（safeMode既定ON維持）と `working -> consensus (patch+approval)` のみ許可を再確認。

### Phase 2 Plan
- Stream A 非依存の mock-first 進行として、固定シグネチャの contract mock 応答を Domain 層に追加する方針を確定。
- AC/DoD の不足は検出なし（既存 AC-1..AC-9 / DoD-1..DoD-5 で判定可能）。

### Phase 3 Execute
- `validateCoreGraphRepositioning` を再利用し、契約凍結バージョン付きの `createCoreGraphRepositionContractMock` を実装。
- 固定返却フィールド: `contractVersion / accepted / noGoId / transition`。

### Phase 4 Verify
- CE0関連の unit test を実行して成功。
- `git diff --check` でパッチ整合性を確認。

### Phase 5 Proceed
- 判定: **proceed**（自己修復 0/3、契約不整合なし、想定外競合なし）。
- 継続条件: UI 接続は別スコープ（本タスクでは contract mock と検証まで）。

## Phase Execution Record（2026-05-10 / Stream D / contract-only boundary refix with mock-first continuity）
### Phase 1 Read
- 本Issue最新状態を再読し、`role / transition / no-go` 固定語彙、canonical No-Go 5 IDs、SafeMode既定ON境界を確認。
- `CE0-contract-freeze` は read-only 参照のみとし、完了待ち依存を実行条件にしない（mock前提で並行可能）。
- 差分判定: 固定語彙・禁止事項・SafeMode境界の差分は検出されず、継続可。

### Phase 2 ADR/CDC（Context / Decision / Consequences）
- Context: CE0 core graph（`working` / `context_projection` / `consensus`）の責務境界を contract-only で再固定し、mock前提で下流実行可能性を維持する。
- Decision: 許可遷移は `working -> consensus` の `patch+approval` のみに固定し、`direct write` / `auto-apply` / `auto-publish` を禁止、proposal-only を維持する。
- Consequences: `consensus` への反映は承認付きパッチ経路に限定されるため、実装待ち局面でも契約整合を保ったまま下流検証を継続可能。未承認論点は `held/pending` 在庫として保持し確定化しない。

### Phase 3 Plan
- AC固定: `working -> consensus` は `patch+approval` のみ許可（他遷移は許可しない）。
- `context_projection` は read-only 投影として扱い、write経路を定義しない。
- direct write禁止、proposal-only維持、SafeMode既定ON後退禁止を受入条件として再固定。

### Phase 4 Execute
- docs-only / single-file 制約で契約記述のみ整理し、実装コード変更は実施しない。
- `role / transition / no-go` 語彙を canonical 範囲に維持し、同義語置換・拡張定義を行わない。

### Phase 5 Verify
- 検証観点: SafeMode既定ON後退なし、`consensus_direct_write`（direct write）禁止、proposal-only 維持。
- `docs-check` を実行し、失敗時 self-correction は最大3回までの運用を維持。

### Phase 6 Proceed
- 判定: `Proceed`（本記録時点で contract-only 境界、No-Go 5 IDs、遷移規則、proposal-only 条件を維持）。
- 以降、語彙差分またはSafeMode境界差分を検出した場合は `held` で停止し、4回目相当の再試行は行わず `Stop` とする。

## Stream D serial phase checkpoint（2026-05-10 / CE track, docs-only）

### Phase 1 Read Gate
- Read対象を再同期し、Status / Priority / Scope / Related ADR/Spec / Acceptance criteria / Validation plan を再確認。
- CE1のtriage必須メタ（Status/Priority）は本日時点で充足済み（欠落なし）として記録。
- 依存整理: `depends_on` を満たすまで下流は proposal-only を維持し、`unlocks` を本IssueのProceed条件に限定。

### Phase 2 Plan（AC/DoD合意）
- 目的: CE契約の固定語彙・fail-closed・mock-first境界を維持しつつ、下流が実装準備を継続できる状態を保つ。
- 非目標: 実装コード変更、共有ダッシュボード更新、他ストリーム専用ファイル編集。
- AC/DoD不足がある場合は本Issue内ドラフトで補完し、未合意項目はHold扱いで固定。
- 検証コマンド: `python 01_Plans/triage_actionable_plans.py --root . --format table`（存在時）/ `git diff -- <this issue file>`。

### Phase 3 ADR Gate
- 本Issueで新規ADR更新が必要な論点は Context / Decision / Consequences を先に明文化し、承認前は実装へ進まない。

### Phase 4 Execute→Verify
- 実行順序は CE0→CE1→CE2→CE3→CE4 を維持し、各Issueでは Plan→Execute→Verify を直列実施。
- Verifyは proposal-only / contract-only / fail-closed の後退が無いことを最優先で確認。

### Phase 5 Proceed
- AC/DoDが未成立、または依存解除条件未達の場合は Proceed せず Hold を維持する。
- 共有ファイル更新が必要な場合は本Issueからの「更新要求メモ」作成に留め、直接編集しない。

## Stream D execution memo（2026-05-10 / core graph only / Stream G contract reference, no contract edits）

### Phase 1 Read
- 本Issueと CE0 固定語彙（`working` / `context_projection` / `consensus`、`working -> consensus` + `patch+approval`、No-Go canonical 5 IDs）を再読し差分なしを確認。
- 参照契約は Stream G の既存 contract を **read-only 参照**とし、契約本文の編集を行わないことを再確認。

### Phase 2 Plan
- 対象範囲を本Issue（`issue-CE0-core-graph-repositioning.md`）と core graph 領域の契約記述に限定。
- 実装依存が必要な場合は local mock で依存切り離しを継続し、他ストリームの完了待ちを前提にしない。
- 競合兆候（語彙差分、契約ID再定義、SafeMode既定ON後退、禁止遷移の緩和）を検出した場合は即 `held` 停止。

### Phase 3 Execute
- contract-only / docs-only の境界で実行し、実装コード・契約本文（Stream G側）には変更を加えない。
- `role / transition / no-go` 語彙を既存 canonical に固定し、同義語拡張を実施しない。

### Phase 4 Verify
- `docs-check` を実行し、失敗時 self-correction は最大3回まで。
- 競合兆候が1件でも出た場合は 4回目試行に進まず `stopped_for_clarification` として停止。

### Phase 5 Proceed
- 判定: `Proceed`（本メモ時点で conflict signal なし、contract-only 維持、Stream G契約は read-only 参照）。


## Stream B synchronization note（2026-05-10 / CE-0 Contract Freeze alignment）

### Context
- Stream B指示に基づき、CE-0 Contract Freezeとの整合確認を docs-only で実施。
- Core Graph repositioning 文書は CE-0 fixed contract matrix の参照先として、I/F先行・mock-first 境界を再明示する。

### Decision
- 本Issueでは API署名・データ型・監査イベント名の固定参照のみを許可し、実装ロジックの確定記述を追加しない。
- `working -> consensus` の `patch+approval` 以外の遷移は引き続き No-Go とする。

### Consequences
- CE-1 が参照する契約境界（signature/type/event）を先行固定したまま、実装自由度を保持できる。
- 矛盾が発生した場合は是正案のみ提示し、本Issueでは確定変更しない（`held`）。

### CE-1 handoff interface snapshot（contract-only）
- API signatures: `POST /context/query`, `POST /context/bundle`
- Data types: `ContextQueryV1`, `ContextBundleV1`, `ProposalPatchV1`, `AuditEventV1`
- Audit event names (reserved): `contract_freeze_verified`, `contract_drift_detected`, `freeze_hold_invoked`


## Stream D execution update（2026-05-19 / CE0 Core Graph Repositioning contract lane）

### Phase 1 Read（差分抽出）
- 上位語彙を再確認し、`Core Graph` を履歴語として扱い、現行契約語彙を `ConsensusGraph` に統一する必要性を抽出。
- CE0 freeze（read-only）と CE1 foundation（mock-first）間で、語彙差分が契約衝突を生まないよう照合。

### Phase 2 契約定義（最小I/F固定）
- 本Issueの再配置契約は「語彙再マッピング」に限定し、実装・スキーマ拡張は行わない。
- 固定I/F: `WorkingGraph`（探索）, `ContextProjectionGraph`（読取専用投影）, `ConsensusGraph`（承認済差分の統合）。
- 旧称 `Core Graph` は履歴説明以外で新規導入しない。

### Phase 3 モック規約（境界・互換・後方互換）
- mock境界: 名称マッピングと契約キー整合の検証まで（データ永続・実行経路は非対象）。
- 互換ルール: 下流が `Core Graph` を参照する場合は「旧称→ConsensusGraph」の read-only alias 説明に限定。
- 後方互換方針: v1 では `ConsensusGraph` を正本語彙に固定し、旧称再導入は将来版 ADR 承認時のみ。

### Phase 4 検証（依存・影響）
- 依存関係: CE0 contract freeze の固定IDと矛盾なし。
- 他Issue影響: CE1/CE2/CE4 への handoff は語彙マッピング情報のみで実装依存を発生させない。
- self-repair: 0/3。

### Phase 5 受け渡し（Stream C/E向け）
- 参照仕様として引き渡す内容:
  1. Graph責務境界3点（Working / ContextProjection / Consensus）
  2. 旧称 `Core Graph` の扱い（履歴限定）
  3. 契約衝突時は `held` 停止
- Fail-safe判定: 用語不整合・契約衝突・未承認事項の確定化は未検知（`Proceed=Conditional-Go`）。


## Stream B execution update（2026-05-19 / CE0 graph責務境界 refresh）

### Phase 1 Read（Status/Priority/Depends/Unblocks/AC 再確認）
- Status=`Open` / Priority=`P1` を維持。
- Depends: `issue-CE0-contract-freeze.md`（契約依存）を再確認。
- Unblocks: CE1/CE2/CE4 下流の graph語彙参照（read-only）を維持。
- ACは「Working/ContextProjection/Consensus 分離」「Working→Consensus は patch+approval のみ」で欠落なし。

### Phase 2 Mock-First切断設計（共有リソース列挙 + 最小シグネチャ）
- 競合しうる共有リソース:
  - I/F名: `ContextQueryV1`, `ContextBundleV1`
  - schema名/語彙: `WorkingGraph`, `ContextProjectionGraph`, `ConsensusGraph`, `ProposalPatchV1`, `AuditEventV1`
  - API語彙: `preview_required`, `unknown_contract_key`, `nondeterministic_bundle`
- Mock Provider前提の切断手順:
  1) Core graph repositioning の検証入力は `ContextBundleV1.bundleHash` のみを受領（payload本文依存なし）。
  2) apply前に `sourceBundleHash===bundleHash` を照合し、不一致は fail-closed。
  3) `mode=autonomous` でも proposal-only を維持し、direct write を禁止。

### Phase 3 Plan→Execute→Verify
- Plan: AC/DoD不足なし。必要十分な契約語彙は既存固定値を採用。
- Execute: CE0→CE1 連結時の read-only handoff 条件を明文化。
- Verify: 依存逆転なし（CE0-contract-freeze が上流）と下流参照可能性（hashキー連携）を確認。

### Phase 4 Stopper
- 3回修復超過、または graph語彙再定義・safeMode後退・direct write 要求を検知した場合は停止して判断依頼。

## Stream D handoff readiness packet（2026-06-02 / CE0 graph role-transition-audit boundary）

### Context
- CE0 core graph repositioning は引き続き docs-only / contract-only / mock-first の graph role / transition / audit 契約として扱う。
- 上流 `issue-CE0-contract-freeze.md` は read-only 参照に限定し、`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05` を本Issue側で再定義しない。
- 本更新は実装許可ではなく、下流が参照してよい graph 境界、許可遷移、監査・停止条件を1か所にまとめる。

### Handoff evidence
| Handoff item | Frozen value / evidence | Downstream use | Stop condition |
| --- | --- | --- | --- |
| Graph roles | `working`, `context_projection`, `consensus` | UI/worker/API実装前の役割名を固定する | 追加/改名/削除/意味変更 |
| Canonical graph term | `ConsensusGraph` を正本、`Core Graph` は履歴・説明上の旧称に限定 | 用語の読み替えを read-only alias として扱う | `Core Graph` を新規正本名として再導入 |
| Allowed transition | `working -> consensus` only via `patch+approval` | 承認済みpatch経路だけを成功扱いする | direct write、auto-apply、auto-publish |
| Context projection | read-only projection only | ContextQuery/ContextBundleの参照先として副作用を持たせない | projection側のwrite経路定義 |
| No-Go canonical IDs | `preview_bypass`, `consensus_direct_write`, `auto_apply_or_publish`, `ai_review_auto_promotion`, `safemode_default_relaxation` | 失敗理由、テスト名、監査理由の固定語彙として使う | 同義語化、別名化、優先度変更 |
| SafeMode boundary | `CE0-SAFEMODE-IF`, safeMode default ON, `allowUnreviewedText=false` | graph反映時の安全既定を維持する | 既定OFF化、未レビュー本文許容、自動昇格 |
| Audit minimum | `timestamp`, `actor`, `phase`, `inputSnapshot`, `gateResult`, `reason`, `nextAction` | gate evidence と `held` 判断を再現する | 入力snapshotやreason欠落を成功扱い |

### Downstream readiness gates
- CE1/ContextQuery: graph role名は read-only 参照に限定し、`context_projection` から `consensus` への暗黙反映を許可しない。
- CE2/AI assist: AI出力は proposal-only とし、`consensus` への反映、`human_reviewed` 昇格、`patch+approval` 省略を自動化しない。
- CE4/API/CLI audit: `contract_freeze_verified`, `contract_drift_detected`, `freeze_hold_invoked` を監査イベント候補として参照できるが、実装時は `AuditEventV1` 正本との照合を必須にする。
- UI/worker/API implementation: 本Issueから実装詳細を開始せず、graph role / allowed transition / No-Go reason の fixture 化に限定する。

### Verify / Proceed
- Verify command remains docs-check only:
  - `03_Implement\backend\.venv\Scripts\python.exe 01_Plans\issues\validate_active_issue_memos.py`
  - `03_Implement\backend\.venv\Scripts\python.exe 01_Plans\triage_actionable_plans.py`
  - `git diff --check -- 01_Plans\issues\issue-CE0-core-graph-repositioning.md`
  - `rg -n "Stream D handoff readiness|working|context_projection|consensus|ConsensusGraph|patch\\+approval|consensus_direct_write|contract_freeze_verified|freeze_hold_invoked|allowUnreviewedText=false" 01_Plans\issues\issue-CE0-core-graph-repositioning.md`
- Proceed: Conditional-Go for downstream read-only graph role and transition reference.
- Stop: Contract ID mutation, graph role redefinition, `Core Graph` re-canonicalization, direct write, auto-apply/auto-publish, SafeMode default relaxation, or missing audit reason.

## Current-main checkpoint（2026-06-14 / post-2394 CE0 graph boundary）

### Context
- Baseline: `main@69fcafdeff23` after PR #2394.
- Scope: docs-only checkpoint for CE0 graph role / transition / audit vocabulary. This update does not approve implementation, add storage behavior, or change graph naming.
- Upstream: `issue-CE0-contract-freeze.md` remains the read-only SSOT for Contract IDs, No-Go IDs, SafeMode, decision I/F, and audit minimums.

### Frozen Graph Evidence
| Area | Current frozen value | Check result |
| --- | --- | --- |
| Graph roles | `working`, `context_projection`, `consensus` | no role addition / rename |
| Canonical term | `ConsensusGraph`; `Core Graph` remains a legacy/read-only explanatory alias | no re-canonicalization |
| Allowed transition | `working -> consensus` only through `patch+approval` | direct write remains No-Go |
| Context projection | read-only projection only | no projection-side write path |
| No-Go IDs | `preview_bypass`, `consensus_direct_write`, `auto_apply_or_publish`, `ai_review_auto_promotion`, `safemode_default_relaxation` | no alias / no priority change |
| SafeMode | default ON, `allowUnreviewedText=false` | `safeMode_regression=0` |
| Audit minimum | `timestamp`, `actor`, `phase`, `inputSnapshot`, `gateResult`, `reason`, `nextAction` | audit key set unchanged |

### Decision
- Proceed as Conditional-Go for downstream read-only graph role and transition reference only.
- Keep this issue Open until an implementation lane records evidence that UI, worker, and API surfaces consume these graph roles without creating direct write, auto-apply, or auto-publish paths.
- No ADR is required for this checkpoint because canonical naming, transition authority, SafeMode, audit evidence, and release authority remain unchanged.

### Stop Conditions
- Hold immediately if `Core Graph` is reintroduced as a canonical product term, if any code or document creates a `context_projection -> consensus` shortcut, or if `working -> consensus` is permitted without `patch+approval`.
- Hold immediately if a future implementation treats AI review as human approval or converts proposal-only output into consensus state without explicit review evidence.
