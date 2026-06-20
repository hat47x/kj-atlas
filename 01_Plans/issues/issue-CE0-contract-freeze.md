# Issue Draft: CE0 Contract Freeze（Stream B / CE0 Contract SSOT / contract-only planning）

- Type: Process
- Status: Done
- Priority: P1
- Owner: Stream B（CE0 Contract Freeze 専任）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Editable: `01_Plans/issues/issue-CE0-contract-freeze.md` のみ（Stream B 制約）
- Related Backlog: `CE-0`
- Related ADR/Spec: `ADR-0028`, `ADR-0039`, `02_Architecture/schemas.md`
- Dependencies: `01_Plans/issues/issue-CE0-contract-freeze.md`（契約SSOT）, `01_Plans/issues/issue-CE0-core-graph-repositioning.md` / `issue-CE1-context-query-bundle-foundation.md` / `issue-CE2-low-risk-ai-assist.md` / `issue-CE4-api-cli-audit-integration.md` が参照
- Verification: `docs-check`

## Hold Resolution 2026-06-20

All three hold conditions resolved per ADR-0039 (governance right-sizing, Accepted 2026-05-31):

| Hold condition | Resolution |
|---|---|
| `Approval Record=Pending` | Filled by Maintainer under delegated authority (ADR-0039) |
| `HIL-RS-02-GOV-EXCEPTION-01=held` | Resolved in `issue-HIL-RS-02-A1-governance-contract-hardening.md` (2026-06-20) |
| `pendingDecisionQueueCount>0` | Cleared per ADR-0039 resolution of ADR-0036/0037/0038 |

CE0 contract freeze is Done (contract readiness only). Implementation approval and release readiness remain gated by downstream issues.

## Current Canonical Summary 2026-06-15

This issue is the read-only SSOT for the CE0 contract freeze. Downstream CE0 core graph, CE1, CE2, and CE4 work may reference this issue, but this issue does not approve implementation, release readiness, SafeMode relaxation, or review bypass.

### Canonical Contract

| Area | Frozen value | Downstream rule |
| --- | --- | --- |
| Contract IDs | `CE0-CTX-IF`, `CE0-SAFEMODE-IF`, `CE0-REVIEW-IF`, `CG-01..05` | Reference these IDs without adding aliases, renaming them, deleting them, or changing their meaning. |
| No-Go canonical IDs | `preview_bypass`, `consensus_direct_write`, `auto_apply_or_publish`, `ai_review_auto_promotion`, `safemode_default_relaxation` | Use these exact IDs for stop reasons, tests, and audit evidence. Do not replace them with local synonyms. |
| Decision I/F | `freezeDecision = { decision: Proceed|Hold|Stop, executeAllowed: boolean, reasonCodes: string[] }` | Treat this as the minimum gate interface. It does not authorize the actual `Pending -> Approved/Rejected` transition. |
| Mock-first boundary | `decision`, `executeAllowed`, and `reasonCodes` only | Mock or fixture work may validate the gate result, but must not imply production approval behavior. |
| Human-owned hold conditions | `Approval Record=Pending`, `HIL-RS-02-GOV-EXCEPTION-01=held`, and `pendingDecisionQueueCount>0` | Keep `decision=Hold` and `executeAllowed=false` while any of these conditions remains unresolved. |

### Current Completion Assessment

| Checkpoint | Status | Note |
| --- | --- | --- |
| Contract ID freeze | Pass | The frozen ID set is established and must remain read-only. |
| No-Go ID freeze | Pass | The five canonical IDs are stable and are the comparison keys. |
| SafeMode boundary | Pass | SafeMode remains default ON, with `allowUnreviewedText=false` as the default boundary. |
| Review boundary | Pass | `human_reviewed` promotion remains a human action only. |
| Decision I/F | Conditional Go | The interface is stable for mock-first gate evidence only. |
| Downstream handoff | Conditional Go | Downstream issues may reference this issue as SSOT, but may not redefine the contract. |
| Implementation approval | Not granted | Implementation authority belongs to downstream implementation issues and their acceptance evidence. |
| Release readiness | Not granted | Product/release readiness must be judged by Product QA and MVP Exit gates. |

### Allowed Next Work

- Update downstream documents to link back to this issue when they need CE0 contract IDs, No-Go IDs, SafeMode boundary, or review boundary.
- Add tests or evidence in downstream implementation lanes proving that these IDs are consumed without redefinition.
- Open an ADR or held issue before proposing any alias, ID change, SafeMode relaxation, review automation, or implementation authority change.

### Recommended Closure Path

1. Confirm current-main drift checks for `02_Architecture/schemas.md`, `02_Architecture/architecture.md`, CE0 core graph, and CE1.
2. Resolve or explicitly continue holding `Approval Record=Pending`, `HIL-RS-02-GOV-EXCEPTION-01=held`, and `pendingDecisionQueueCount>0`.
3. Ensure downstream CE0/CE1/CE2/CE4 documents reference this issue instead of copying or redefining the contract.
4. Keep Product QA and MVP Exit documents clear that CE0 provides contract readiness only, not release approval.

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

## Stream B execution ledger（CE0専任 / contract-only）

## Stream C execution record（2026-04-28 / CE0 contract freeze confirmation）

### Phase 1 Read
- 現行I/F境界を再確認し、`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05` が read-only 固定であることを確認。
- schema破壊的変更・互換喪失・他ストリーム編集要求を停止条件として再確認。

### Phase 2 Plan
- 契約先行で必須属性を再宣言：`ContextQuery.goal/scope/depth/constraints/reviewFilter/safeModePolicy/outputMode`、`ContextBundle.bundleHash`。
- 互換ルールを固定：`preview_required` / `unknown_contract_key` / `nondeterministic_bundle` の意味論を v1 で不変化。

### Phase 3 Execute
- mock-first 前提で A2 実行可能条件を記録（実装未着手）：Query Preview 必須、`Working -> Consensus` は `patch+approval` のみ。
- 契約IDの追加・改名・削除は未実施（freeze 維持）。

### Phase 4 Verify
- 下流実装用シグネチャ一覧を確認：`ContextQueryV1` / `ContextBundleV1` / `ProposalPatchV1` / `AuditEventV1`。
- fail-safe 判定：`contract_id_mutation=0` / `safeMode_regression=0` / `scope_deviation=0`。

### Phase 5 Proceed
- 判定: **Contract Freeze Recorded**。
- CE0契約は read-only 参照モードを維持し、未承認拡張要求は `held` 扱いとする。

- lane: `Stream B`
- ssot_scope: `CE0 only`（CE1/CE2/CE4は参照専用）
- edit_allowlist: `01_Plans/issues/issue-CE0-contract-freeze.md` のみ
- fail_safe:
  - 指定外ファイル編集を検知した場合は即停止して `held`。
  - safeMode既定値後退（`safeMode=true` / `allowUnreviewedText=false` 逸脱）を検知した場合は即停止して `held`。
  - Contract ID再定義（追加/改名/削除）を検知した場合は即停止して `held`。

### Phase status（固定ワークフロー追跡）
- Phase 1 Read: `completed`（各Phase開始時の再読を実施）
- Phase 2 ADR/CDC: `completed`（Context/Decision/Consequencesを明文化）
- Phase 3 Plan: `completed`（AC/DoD不足の追加ドラフト要否を確認）
- Phase 4 Execute: `completed`（contract-only記録更新のみ実施）
- Phase 5 Verify: `completed`（docs-check通過、自己修復 0/3）
- Phase 6 Proceed: `completed`（最新判定: `Conditional-Go`。未承認新規論点は `held` 維持）

## Stream B latest run（2026-04-28 / CE0 only / single-file contract freeze lane refresh）

- run_id: `stream-b-ce0-2026-04-28-09`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0`

### Phase 1 Read
- Phase開始時に本Issueを再読し、固定順序 **Read → ADR/CDC → Plan → Execute → Verify → Proceed** を再確認。
- contract-only / mock-first / docs-only の境界、および CE0 Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）の再定義禁止を再確認。
- fail-safe（指定外編集 / safeMode既定値後退 / Contract ID再定義 / self-correction 4回目相当）で即停止する条件を再確認。

### Phase 2 ADR/CDC
- Phase開始時に本Issueを再読し、ADRが必要になる条件を確認。
- Context: CE0 Contract Freezeの単一ファイルSSOT運用を継続し、他ファイル変更は行わない。
- Decision: 既存Contract ID・safeMode境界・No-Go canonical IDsを固定し、再定義や拡張を実施しない。
- Consequences: 契約ドリフトと安全境界の後退を抑止し、逸脱要求発生時は `held` 停止へ遷移できる。
- CDC判定: `contract_id_collision=0` / `vocabulary_collision=0` / `scope_deviation=0` のため新規CDC起票なし。

### Phase 3 Plan
- Phase開始時に本Issueを再読し、AC/DoD追跡項目（`dod_read_only_reference` / `dod_no_go_id_canonical` / `dod_cdc_held_required`）を再確認。
- Plan: 本Issueの実行ログ更新のみを実施し、他CE仕様確定・実装変更・ID再定義は行わない。
- ゲート条件: 新規ADR論点や不足が発生した場合は Context/Decision/Consequences 明文化と承認完了まで `held`。

### Phase 4 Execute
- Phase開始時に本Issueを再読し、単一ファイル編集境界を再確認。
- 実施: contract-only / docs-only で本実行ログを追記。
- 非実施: 指定外ファイル編集、実装変更、safeMode既定値変更、CE0 Contract ID再定義。

### Phase 5 Verify
- Phase開始時に本Issueを再読し、検証対象が docs-check と差分健全性であることを再確認。
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）
- self-correction policy: 最大3回まで。4回目相当が必要な場合は即停止して指示待ち。

### Phase 6 Proceed
- Phase開始時に本Issueを再読し、Proceed判定条件を再確認。
- 判定: **Conditional-Go**
- 条件:
  - CE0 Contract Freezeは単一ファイルSSOT運用を継続（read-only参照のみ許可）。
  - 逸脱要求・未定義競合・self-correction 4回目相当が発生した時点で即時 `held` 停止。

## Stream B latest run（2026-04-28 / CE0 only / CE0 Contract Freeze execution prompt）

- run_id: `stream-b-ce0-2026-04-28-08`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0`

### Phase 1 Read
- Phase開始前に本Issueを再読し、実行フェーズが **Read → ADR/CDC → Plan → Execute → Verify → Proceed** の厳密直列であることを再確認。
- contract-only / mock-first / docs-only の固定ルール、および CE0 Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）固定を再確認。
- fail-safe（指定外編集 / safeMode境界後退 / Contract ID再定義 / self-correction 4回目相当）で即停止する条件を再確認。

### Phase 2 ADR/CDC
- Context: CE0 Contract FreezeのSSOTを本Issueに限定し、CE1/CE2/CE4は read-only 参照のまま維持する。
- Decision: CE0契約IDとsafeMode境界を不変とし、他CEの実装仕様確定に繋がる記述を追加しない。
- Consequences: 契約ドリフトと境界後退を抑止し、未定義競合または逸脱要求発生時に即時 `held` 停止へ移行できる。
- CDC判定: `contract_id_collision=0` / `vocabulary_collision=0` / `scope_deviation=0` のため新規CDC起票なし。

### Phase 3 Plan
- AC/DoD追跡項目（`dod_read_only_reference` / `dod_no_go_id_canonical` / `dod_cdc_held_required`）を再確認。
- AC/DoD不足判定: 新規不足なし（ドラフト提案・追加合意は不要）。
- ゲート条件: 不足発生時はドラフト提示と合意完了まで `held` とし、Phase 4へ進行しない。

### Phase 4 Execute
- 実施: 本Issue内の実行ログ更新のみ（contract-only / docs-only）。
- 非実施: 実装変更、指定外ファイル編集、CE0 Contract ID追加/改名/削除、safeMode既定値変更、他CE実装仕様の確定。

### Phase 5 Verify
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）
- 判定: Verify成功。自己修復は未使用のため上限（3回）未到達。

### Phase 6 Proceed
- 判定: **Conditional-Go**
- 条件:
  - CE1/CE2/CE4への引き渡しは Contract ID / No-Go canonical IDs の read-only 参照のみ。
  - 4回目相当の自己修復要求、未定義競合、指定外編集要求が発生した時点で即時 `held` 停止。

## Stream B latest run（2026-04-27 / CE0 only / phase-serial compliance refresh）

- run_id: `stream-b-ce0-2026-04-27-07`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0`

### Phase 1 Read
- Phase開始前に本Issueを再読し、編集許可が本ファイルのみに限定されることを確認。
- Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）固定と、No-Go canonical IDs 5件固定を確認。
- fail-safe（指定外編集 / safeMode境界後退 / Contract ID再定義 / self-correction 4/3相当）で即停止する条件を再確認。

### Phase 2 ADR/CDC
- Context: CE0 Contract Freezeを本IssueのSSOTとして維持し、下流はread-only参照のみを継続する。
- Decision: contract-only / mock-firstを維持し、実装確定に繋がる記述は追加しない。
- Consequences: 契約ドリフトを抑止し、逸脱検知時に `held` へ即時遷移できる。
- CDC判定: `contract_id_collision=0` / `vocabulary_collision=0` / `scope_deviation=0` のため新規CDC起票なし。

### Phase 3 Plan
- Phase開始前に本Issueを再読し、AC/DoD追跡項目（`dod_read_only_reference` / `dod_no_go_id_canonical` / `dod_cdc_held_required`）を再確認。
- AC/DoD不足判定: 新規不足なし（追加ドラフト提示不要）。
- ゲート条件: AC/DoD不足が発生した場合はドラフト提示と合意完了まで `held` とし、Executeへ進まない。

### Phase 4 Execute
- Phase開始前に本Issueを再読し、contract-only編集境界を再確認。
- 実施: 本Issue内の実行ログ更新のみ（本セクション追記）。
- 非実施: 実装変更、指定外ファイル編集、Contract ID追加/改名/削除、safeMode既定値変更。

### Phase 5 Verify
- Phase開始前に本Issueを再読し、検証対象が docs-check と差分健全性のみであることを再確認。
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）

### Phase 6 Proceed
- Phase開始前に本Issueを再読し、Proceed判定条件とfail-safe停止条件を再確認。
- 判定: **Conditional-Go**
- 条件:
  - CE1/CE2/CE4への引き渡しは Contract ID / No-Go canonical IDs のread-only参照のみ。
  - 新規AC/DoD不足や逸脱要求が発生した時点で `held` に戻し、人間承認まで停止する。

## Stream B latest run（2026-04-27 / CE0 only / contract freeze execution directive）

- run_id: `stream-b-ce0-2026-04-27-06`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_repair_overflow=0`

### Phase 1 Read
- 最新状態・依存・優先度を再確認し、CE0 Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）固定を確認。
- No-Go canonical IDs（`preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`）差分ゼロを確認。
- fail-safe（safeMode既定後退禁止 / 指定外編集禁止 / Contract ID再定義禁止）を再確認。

### Phase 2 ADR/CDC
- Context: CE0 contract freeze を本IssueのSSOTとして維持し、下流は read-only 参照のみを継続する。
- Decision: Contract I/Fと禁止事項の固定に限定し、実装詳細には踏み込まない。
- Consequences: 契約ドリフトの早期検知が可能となり、逸脱時は `held` へ即停止できる。
- CDC判定: `contract_id_collision=0` / `vocabulary_collision=0` / `scope_deviation=0` のため新規CDC不要。

### Phase 3 Plan
- Contract IDs固定、禁止事項固定、fail-safe条件、AC/DoD追跡（`dod_read_only_reference` / `dod_no_go_id_canonical` / `dod_cdc_held_required`）を再確認。
- AC/DoD不足は新規なしと判断し、追加ドラフト提案は不要。

### Phase 4 Execute
- 契約文面のみを更新（本実行ログの追記）し、範囲逸脱なしを確認。
- 非実施: 実装変更、指定外ファイル編集、Contract ID追加/改名/削除、safeMode既定値変更。

### Phase 5 Verify
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）
- drift確認: `contract_id_collision=0` / `vocabulary_collision=0` / `safeMode regression=0`

### Phase 6 Proceed
- 判定: **Conditional-Go**
- 条件:
  - CE1/CE2/CE4への引き渡しは Contract ID read-only参照のみ。
  - 承認前の新規論点は確定せず `held` を維持する。

## Stream B latest run（2026-04-28 / CE0 only / 5-phase contract-only execution）

- run_id: `stream-b-ce0-2026-04-28-10`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0`

### Phase 1 Read
- Phase冒頭で本Issueを再読し、対象ファイル単一編集制約と **Read → Plan → Execute → Verify → Proceed** の固定順序を同期。
- contract-only / mock-first / docs-only 境界、および CE0 Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）再定義禁止を再確認。
- fail-safe（指定外編集 / safeMode既定値後退 / Contract ID再定義 / 4回目修正要求）で即停止する条件を再確認。

### Phase 2 Plan
- Phase冒頭で本Issueを再読し、AC/DoD不足をドラフト化して合意可否を確認。
- AC/DoD draft（不足補強候補）:
  - `ac_phase_re_read_required`: 各Phase冒頭で対象ファイル再読を必須化し、ログに明記する。
  - `dod_verify_retry_cap`: Verify失敗時の自己修正上限を `max 3` とし、4回目相当は停止報告を必須化する。
  - `dod_contract_only_mock_first`: Executeで実装仕様確定・ID追加改名削除を禁止し、mock-first記録に限定する。
- 合意: 本ドラフト3件を本runの運用DoDとして採用（新規ADR起票は不要、既存freeze境界内）。

### Phase 3 Execute
- Phase冒頭で本Issueを再読し、単一ファイル編集境界を再同期。
- 実施: 本Issueへの実行ログ追記のみ（contract-only / mock-first / docs-only）。
- 非実施: 指定外ファイル編集、実装変更、safeMode既定値変更、CE0 Contract IDの追加/改名/削除。

### Phase 4 Verify
- Phase冒頭で本Issueを再読し、Verify手順と自己修正上限（3回）を再同期。
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）
- 判定: Verify成功。追加自己修正は不要。

### Phase 5 Proceed
- Phase冒頭で本Issueを再読し、Proceed可否と停止条件を再確認。
- 判定: **Conditional-Go**
- 継続条件:
  - CE0 Contract Freezeは read-only参照運用を維持する。
  - ADR変更が必要な新規競合は Context/Decision/Consequences 明文化と承認完了まで `held`。
  - 4回目相当の修正要求・競合・safeMode後退兆候を検知した時点で即停止し、原因/影響I/F/要人間判断を報告する。

## Stream B latest run（2026-04-27 / CE0 only / phase-gated hold）

- run_id: `stream-b-ce0-2026-04-27-05`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_repair_overflow=0`

### Phase 1 Read
- 本Issueを再読し、Contract ID（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）固定を確認。
- No-Go canonical IDs（`preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`）差分ゼロを確認。
- safeMode境界（`safeMode=true` / `allowUnreviewedText=false`）後退なしを確認。

### Phase 2 ADR/CDC
- Context: CE0 contract freeze をSSOTとして維持し、下流は read-only 参照のみとする。
- Decision: Contract ID再定義なし、safeMode既定値後退なし、No-Go判定は5語彙ID照合を維持する。
- Consequences: 境界逸脱を検知した場合は `held` へ即停止でき、下流の先行確定を抑止できる。
- CDC判定: `contract_id_collision=0` / `vocabulary_collision=0` / `scope_deviation=0` のため新規CDC不要。

### Phase 3 Plan
- AC/DoD不足の再確認を行い、現行追跡（`dod_read_only_reference` / `dod_no_go_id_canonical` / `dod_cdc_held_required`）で充足することを確認。
- ADRタスク方針として、承認前論点は確定扱いせず `held` 維持とする。

### Phase 4 Execute
- contract-only 範囲で本Issueの実行ログを更新。
- 非実施: 実装変更、指定外ファイル編集、Contract ID追加/改名/削除、safeMode既定値変更。

### Phase 5 Verify
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-repair 0/3）

### Phase 6 Proceed
- 判定: **Hold**
- 理由: ADRタスクの承認前論点は `held` 維持とする運用を優先（未承認決定の確定化を回避）。
- 次回条件: 承認状態更新後に同一フェーズ順（Read → ADR/CDC → Plan → Execute → Verify → Proceed）で再実行。

## Stream B latest run（2026-04-27 / CE0 only / contract freeze reaffirmed）

- run_id: `stream-b-ce0-2026-04-27-04`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_repair_overflow=0`

### Phase 1 Read
- 本Issueを最新再読し、固定値 `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05` の差分ゼロを確認。
- `safeMode=true` / `allowUnreviewedText=false` の既定固定を再確認。
- canonical No-Go 5 IDs（`preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`）差分ゼロを確認。

### Phase 2 ADR/CDC
- Context: CE0 contract freeze を本Issue単独で維持し、下流は read-only 参照のみとする。
- Decision: Contract ID再定義なし、safeMode後退なし、No-Go判定は5語彙ID照合のまま固定。
- Consequences: CE1/CE2/CE4 側での先行再定義を抑止し、境界逸脱時は `held` 停止に即時移行できる。
- CDC判定: `contract_id_collision=0` / `vocabulary_collision=0` / `scope_deviation=0` のため新規CDC不要。

### Phase 3 Plan
- AC/DoD不足の事前ドラフト要否を再確認し、既存追跡項目（`dod_read_only_reference` / `dod_no_go_id_canonical` / `dod_cdc_held_required`）で充足と判断。
- 承認前項目の扱いは `held` を維持し、未承認決定を確定扱いしない方針を再確認。

### Phase 4 Execute
- contract-only 文言整備として、実行ログ更新と編集境界（本Issueのみ）を明文化。
- 非実施: 実装変更、shared resource 変更、Contract ID再定義、safeMode既定値変更。

### Phase 5 Verify
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-repair 0/3）

### Phase 6 Proceed
- 判定: **Complete（contract freeze 継続）**
- 根拠:
  - docs-check pass
  - contract-only 文言整備のみ
  - 実装変更ゼロ / 指定外編集ゼロ

## Stream B latest run（2026-04-27 / CE0 only / issue-owned update）

- run_id: `stream-b-ce0-2026-04-27-03`
- assignee: `issue-CE0-contract-freeze.md 単独担当`
- scope_guard: `edit_allowlist=issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / unapproved_finalize=0`

### Phase 1 Read（Status / Scope / Related ADR 差分確認）
- 実施: 本ファイル最新状態を再読し、`Status=Open` / `Scope=01_Plans/issues/（docs-only / contract-only / mock-first）` / `Related ADR/Spec=ADR-0028, 02_Architecture/schemas.md` の差分がないことを確認。
- 実施: 固定Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）と No-Go 5語彙IDの差分ゼロを確認。

### Phase 2 ADR確認（Context / Decision / Consequences）
- Context: CE0 contract freeze のSSOTは本Issueで維持し、下流はread-only参照のみ。
- Decision: 既存Decisionで整合が取れているため、新規Decision追加は不要（承認待ち新設なし）。
- Consequences: 承認待ちは増えず、既存 `agreement_state` と `held` 運用をそのまま継続可能。

### Phase 3 Plan（AC/DoD不足点の確認）
- 判定: 新規不足なし。既存追跡対象 `dod_read_only_reference` / `dod_no_go_id_canonical` / `dod_cdc_held_required` で網羅可能。
- 合意状態: 追加ドラフト提示は不要（現行DoDで継続）。

### Phase 4 Execute（contract-only / mock-first）
- 実施: 本Issue内の実行ログのみ更新し、contract-only / mock-first 境界を明示。
- 非実施: 実装ファイルへの変更指示、CE0 Contract ID再定義、指定外ファイル編集。

### Phase 5 Verify（AC/DoD適合確認 / self-repair）
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-repair 0/3）
- AC/DoD適合: `contract_id_collision=0` / `vocabulary_collision=0` / `safeMode regression=0` を確認。

### Phase 6 Proceed（完了判定）
- 判定: **完了（Complete）**
- 根拠:
  - 許可範囲内編集のみ（本Issue単独）
  - contract-only / mock-first の記述更新のみ
  - VerifyでAC/DoD不整合なし（自己修復不要）

## Stream B latest run（2026-04-27 / CE0 only / agreement hold）

- run_id: `stream-b-ce0-2026-04-27-02`
- scope_guard: `edit_allowlist=issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / unapproved_finalize=0`

### Phase 1 Read（最新再読）
- 実施: 本Issueを再読し、固定Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）の差分ゼロを確認。
- 実施: safeMode境界（`safeMode=true` / `allowUnreviewedText=false`）後退なしを確認。
- 実施: No-Go語彙ID（`preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`）差分ゼロを確認。

### Phase 2 ADR/CDC（Context / Decision / Consequences）
- Context: CE0 Contract Freezeを単独維持し、CE1/CE2/CE4は read-only 参照のみとする。
- Decision: Contract ID再定義なし、safeMode境界固定、No-Go語彙ID canonical 判定を継続。未承認項目は `held` 維持。
- Consequences: 下流の再定義と safeMode後退を防止できる一方、追加DoDは合意完了まで確定運用しない。
- CDC判定: `contract_id_collision=0` / `vocabulary_collision=0` / `scope_deviation=0` のため新規CDCなし。

### Phase 3 Plan（AC/DoD不足提案 / 合意待ち）
- 提案A（AC不足）: read-only参照の判定基準を「リンク更新/注記のみ許可」に明文化する。
- 提案B（DoD不足）: No-Go判定は5語彙ID照合を唯一基準とし、同義語は注釈扱いに限定する。
- 提案C（DoD不足）: `contract_id_collision | vocabulary_collision | scope_deviation` 検知時の `held` 記録を必須化する。
- agreement_state: `held`（追加合意待ち）
- gate: 合意未了のため **Phase 4 Executeへ進まない**。

### Phase 4 Execute
- 状態: `blocked`（contract-only修正を含め未着手）

### Phase 5 Verify
- 状態: `blocked`（Execute未着手のため docs-check は次回実行）

### Phase 6 Proceed（Go / Hold）
- 判定: **Hold**
- 理由: Phase 3の追加AC/DoD提案が `agreement_state=held` のため。
- 次回引継ぎ:
  - 合意取得後にのみ Phase 4 Execute（contract-only）を再開する。
  - 再開時も fail-safe（safeMode後退・Contract ID改変・指定外編集）を先行監視する。

## Stream B latest run（2026-04-26 / CE0 only）

- run_id: `stream-b-ce0-2026-04-26-04`
- scope_guard: `edit_allowlist=issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / unapproved_finalize=0`

### Phase 1 Read（最新再読）
- 実施: 本Issueを再読し、Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）固定を再確認。
- 実施: No-Go語彙ID（`preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`）固定を再確認。
- 実施: safeMode境界（既定ON、`allowUnreviewedText=false`）後退禁止を再確認。

### Phase 2 ADR/CDC（Context / Decision / Consequences）
- Context: CE0をSSOTとして維持し、下流（CE1/CE2/CE4）はread-only参照のみ。
- Decision: Contract ID再定義なし、No-Go語彙ID判定維持、未承認論点は `held` のまま運用。
- Consequences: 下流再定義を抑止し、衝突時は `held` 記録で停止可能。
- CDC判定: `contract_id_collision=0` / `vocabulary_collision=0` / `scope_deviation=0` のため、新規CDC起票なし。

### Phase 3 Plan（AC/DoD補完提案の合意確認）
- 合意対象: `dod_read_only_reference` / `dod_no_go_id_canonical` / `dod_cdc_held_required` を継続追跡。
- 合意状態: `agreement_state=agreed` を維持。未承認の新規論点は `held`。
- 実行境界: contract-only wording修正のみ、実装変更禁止。

### Phase 4 Execute（contract-only）
- 実施: 本ファイル内の進行状態と実行記録を更新（指定外ファイル編集なし）。
- 非実施: CE0 Contract IDの追加・改名・削除、safeMode既定値変更、CE1/CE2/CE4本文変更。

### Phase 5 Verify（docs-check / self-correction ≤ 3）
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）

### Phase 6 Proceed（Go / Conditional / No-Go）
- 判定: **Go**
- 根拠:
  - `contract_id_collision=0`
  - `vocabulary_collision=0`
  - `safeMode regression=0`
  - docs-check pass
- 継続条件:
  - CE1/CE2/CE4への引き渡しは Contract ID / No-Go ID のread-only参照のみ。
  - 未承認論点は確定扱いせず `held` 維持。

## Stream B latest run（2026-04-27 / CE0 only / snapshot fixed）

- run_id: `stream-b-ce0-2026-04-27-01`
- input_contract_snapshot: `ce0-contract-freeze-2026-04-27`（fixed）
- scope_guard:
  - `01_Plans/issues/issue-CE0-contract-freeze.md`
  - `02_Architecture/architecture.md（7A CE0節のみ）`
  - `02_Architecture/schemas.md（1.1 CE0契約節のみ）`
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / unapproved_finalize=0`

### Phase 1 Read（対象再Read）
- 実施: 3対象ファイルを再読し、CE0 Contract IDsとNo-Go語彙IDの固定を確認。
- 実施: safeMode既定値（ON + `allowUnreviewedText=false`）後退禁止を確認。

### Phase 2 AC/DoD確定（Context / Decision / Consequences）
- Context: Stream B は CE0 contract freeze 専任。下流成果物待ちを行わず、固定スナップショットを使用する。
- Decision: AC/DoD は「Contract ID再定義なし」「No-Go語彙ID canonical」「read-only handoff」「Verify自己修復≤3」で固定。
- Consequences: CE1/CE2/CE4 との競合を回避しつつ、CE0を単独で凍結維持できる。

### Phase 3 契約固定（contract-only）
- 実施: `architecture.md` CE0節に snapshot 固定値と No-Go canonical IDs を追記。
- 実施: `schemas.md` CE0契約節に snapshot 固定値と drift-stop canonical IDs を追記。
- 非実施: CE0 Contract ID追加・改名・削除、実装コード変更、共有統合ファイル編集。

### Phase 4 Verify（self-correction ≤ 3）
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）

### Phase 5 引き渡し（Proceed）
- 判定: **Go**
- 引き渡し条件:
  - CE1/CE2/CE4 は `ce0-contract-freeze-2026-04-27` を read-only 参照する。
  - Contract IDs と No-Go canonical IDs は CE0 SSOT を唯一正本として維持する。

## Lane guard（このレーンの絶対条件 / CE SSOT）
- CE0をCE契約のSSOT（single source of truth）とし、CE1/CE2/CE4は**参照のみ**で利用する。
- 本Issueは**計画・契約先行のみ**を扱う。実装（`03_Implement/**`）と共有統合ファイルは対象外。
- CE0契約IDは再定義禁止（freeze対象）：`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`。
- CE0 Contract IDの追加・改名・削除を禁止する（freeze中の再定義不可）。
- safeMode既定値（ON, `allowUnreviewedText=false`）の後退を禁止する。
- 推測実装（speculative implementation）を禁止し、記載根拠は本Issue内の固定語彙/固定I/Fに限定する。
- 致命エラー（Fail-safe該当）検知時は即停止し、`held` へ戻す。
- 未承認決定を確定扱いしない（承認待ち論点は `held`）。
- 強制ワークフローは **`Phase 1 Read → Phase 2 ADR/CDC（Context/Decision/Consequences） → Phase 3 Plan（AC/DoD補完） → Phase 4 Execute → Phase 5 Verify → Phase 6 Proceed`**。
- **各Phase開始時は本Issueを最新再読してから開始する（再読省略禁止）。**
- 自己修復は Verify で最大3回まで。4回目相当は即停止する。

## Phase 1 Read（全対象Read: Status / Scope / Related ADR確認）
### 最新再読チェック（Phase開始ゲート）
- 対象ファイル: `issue-CE0-contract-freeze.md`（本書のみ）
- CE0 SSOT再定義禁止 / 実装禁止 / 指定外編集禁止を再確認
- Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）の凍結を再確認
- No-Go canonical wording（5語彙ID）を再確認
- 失敗時自己修復上限（3回）を再確認

### Read同期スナップショット
- Contract ID: `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`
- 固定語彙: `equivalenceKey + bundleHash` / `sourceBundleHash` / `proposal lifecycle`
- Scope: contract-only（実装非干渉、mock/hash/read-only参照で依存切断）

### 固定I/F（参照のみ）
- `CE0-CTX-IF`: ContextQuery必須キー + deterministic `bundleHash`。
- `CE0-SAFEMODE-IF`: safeMode既定ON、`allowUnreviewedText=false` 既定。
- `CE0-REVIEW-IF`: `human_reviewed` 昇格は人手のみ。
- `CG-01..05`: `Working -> Consensus` は `patch + approval` のみ。

### No-Go語彙（固定）
- `preview_bypass`（Query Preview bypass）
- `consensus_direct_write`（Consensus direct write）
- `auto_apply_or_publish`（auto-apply / auto-publish）
- `ai_review_auto_promotion`（AIによる review 自動昇格）
- `safemode_default_relaxation`（safeMode既定緩和）

#### No-Go canonical wording（差分判定用）
- 比較・照合は上記5語彙ID（`preview_bypass` 等）を正本とし、日本語/英語表記揺れは括弧内同義語として扱う。
- CE1/CE2/CE4へは語彙IDのみを受け渡し、下流文書で同義語を追加しても禁止判定の意味は拡張・縮退しない。

## Phase 2 ADR/CDC（Context/Decision/Consequences）
### 最新再読チェック（Phase開始ゲート）
- Phase 1の固定語彙・No-Go語彙・Scopeを再読し、差分ゼロを確認してから着手する。

### Plan方針
- Freeze原則: CE1/CE2/CE4はCE0契約を再定義せず、I/F参照のみで固定する。
- CE1参照境界: `ContextQuery/ContextBundle` + hash決定論（`CE0-CTX-IF`参照のみ）。
- CE2参照境界: proposal-only + review自動昇格禁止（`CE0-REVIEW-IF`参照のみ）。
- CE4参照境界: 監査4点 `query/bundle/proposal/apply` と fail-closed（`CG-01..05`参照のみ）。
- safeMode境界は `CE0-SAFEMODE-IF` を上位正本として固定し、下流Issueで再定義しない。

### I/F Mock Freeze Matrix（read-only handoff）
| Consumer | Read-only参照元（CE0 SSOT） | 許可される変更 | 禁止 |
| --- | --- | --- | --- |
| CE1 | `CE0-CTX-IF`（ContextQuery必須キー / deterministic bundle） | 参照リンクの更新のみ | 必須キー再定義、hash規則改変 |
| CE2 | `CE0-REVIEW-IF`（proposal-only / human昇格手動） | 状態遷移説明の補足のみ | auto-apply、AI review昇格 |
| CE4 | `CG-01..05`（監査4点 / fail-closed） | 監査導線の注記のみ | 監査欠損の成功扱い、direct write |

### Freeze判定（全て必須）
- 参照方向は `CE0 -> (CE1, CE2, CE4)` の一方向のみ（逆参照での再定義禁止）。
- CE1/CE2/CE4は contract本文の複製を行わず、Contract ID参照のみ記述する。
- 参照先に差分が必要な場合は CE0再起票（本Issue）を経由し、下流Issueで先行確定しない。
- handoff本文は read-only（Contract ID参照のみ）とし、依存切断方針（mock-first）を維持する。

### AC/DoD補完（Phase 2で先に固定）
- AC不足候補A: 「read-only参照」の判定根拠が曖昧。
  - 補完: `Matrix` に「許可される変更はリンク更新/注記のみ」を必須条件としてDoDへ反映する。
- AC不足候補B: No-Go語彙の表記揺れによる誤判定。
  - 補完: 5語彙ID（`preview_bypass` ほか）を照合キーに固定し、自然言語は同義語扱いに限定する。
- AC不足候補C: CDC発火条件の見落とし。
  - 補完: `contract_id_collision | vocabulary_collision | scope_deviation` のいずれか検知時は `held` 記録を必須化する。
- Status: `held`（承認待ち。確定運用は承認後）
- DoD補完固定（承認待ちの追跡対象）:
  - `dod_read_only_reference`: Matrix上で「リンク更新/注記のみ」を満たす。
  - `dod_no_go_id_canonical`: No-Goは5語彙ID照合のみで判定する。
  - `dod_cdc_held_required`: CDC trigger検知時はContext/Decision/Consequencesを`held`記録する。

### AC/DoD補完提案の合意明記（Phase 2）
- 合意対象: AC不足候補A/B/C の補完方針そのもの（実装や下流再定義は含めない）。
- 合意記録:
  - `agreement_scope`: CE0契約本文の語彙固定と判定根拠の明確化のみ。
  - `agreement_state`: `agreed`（2026-04-22 合意取得済み）
  - `agreement_note`: 承認前は運用確定扱いせず、Phase 4では「契約語彙統一」と「禁止事項単一化」の編集に限定する。
- Execute開始条件（合意ゲート）:
  - `agreement_state` が `held` の間は **Phase 4 Executeへ進まない**。
  - Execute開始は `agreement_state=agreed` 明記後に限定する（記録なし開始は禁止）。
- 非合意（明示）:
  - CE1/CE2/CE4の本文更新・再定義
  - `03_Implement/**` の実装変更
  - CE0 Contract IDの追加/改名/削除

### ADR CDC（必要時のみ）
- 原則: 差分検知時のみCDCを起票し、**`held`（承認待ち）** を維持して次Phaseへ進む。
- Trigger: `contract_id_collision` / `vocabulary_collision` / `scope_deviation`。
- 未検知（すべて0）の場合はCDC起票しない。

#### CDCテンプレ（必要時のみ）
```md
#### CDC-CE0-<yyyymmdd>-<seq>
- Status: held（承認待ち）
- Trigger: [contract_id_collision | vocabulary_collision | scope_deviation]
- Context:
  - 衝突箇所:
  - 影響Contract ID:
- Decision:
  - CE0契約ID再定義なし
  - 参照境界の補正のみ
- Consequences:
  - CE1/CE2/CE4の参照先が一意
  - 下流Issueはread-only参照を維持
- Approval Needed:
  - reviewer:
  - due:
```

## Phase 3 Plan（I/F Mock Freeze計画 + AC/DoD補完）
### 最新再読チェック（Phase開始ゲート）
- CE0 Contract IDs再定義禁止、proposal-only、safeMode既定維持を再確認する。

### Freeze contract canonical expressions（統一正本）
| Contract ID | Freeze expression（正本。下流は参照のみ） |
| --- | --- |
| `CE0-CTX-IF` | ContextQuery必須キーを固定し、ContextBundleは deterministic `bundleHash`（`equivalenceKey + bundleHash`）で照合する。 |
| `CE0-SAFEMODE-IF` | safeMode は既定ON、`allowUnreviewedText=false` を既定固定し、緩和は契約外とする。 |
| `CE0-REVIEW-IF` | proposal lifecycle は proposal-only を維持し、`human_reviewed` 昇格は人手操作のみ許可する。 |
| `CG-01..05` | `Working -> Consensus` 遷移は `patch + approval` のみで成立し、direct write を禁止する。 |

### Prohibited operations canonical set（単一正本）
| No-Go ID | Canonical prohibition | Alias（同義語。判定はID基準） |
| --- | --- | --- |
| `preview_bypass` | Query Preview を経由しない適用を禁止する。 | preview bypass |
| `consensus_direct_write` | Consensus への direct write を禁止する。 | direct write |
| `auto_apply_or_publish` | auto-apply / auto-publish を禁止する。 | automatic apply/publish |
| `ai_review_auto_promotion` | AI判断のみで `human_reviewed` へ昇格することを禁止する。 | AI review auto promotion |
| `safemode_default_relaxation` | safeMode既定値（ON, `allowUnreviewedText=false`）の緩和を禁止する。 | safemode relaxation |

### Execute Plan（実行前固定）
- CE0 SSOT本文のみを整備し、下流Issueは Contract ID参照で解釈可能な状態に保つ（契約凍結文言の統一のみ実施）。
- CE1/CE2/CE4への handoff は「参照のみ（本文複製なし）」で表現を固定する（契約本文の新規追加・改名・削除は禁止）。
- No-Go語彙IDの照合観点をCE0に明記し、下流への受け渡しは語彙ID参照のみとする。
- Phase 2で `held` 化したAC/DoD補完提案は、承認前に確定扱いしない。

### Contract-only wording hygiene checklist（再定義防止）
- 許可: 表記揺れの統一、語順調整、見出し整理（意味不変）。
- 禁止: Contract ID / No-Go ID / safeMode既定値 / proposal lifecycle の意味変更。
- 禁止: CE1/CE2/CE4向けに契約本文を複製して「別定義」を作ること。
- 差分の判断単位は `Contract ID` と `No-Go ID` を優先し、自然言語差分のみでは再定義扱いにしない。

### Execute結果条件
- `collision=0` / `safeMode regression=0` を満たす記述へ整理。
- 検証失敗時は自己修復を最大3回まで実施し、4回目相当は停止する。

## Phase 4 Execute（Plan反映のみ。契約再定義・実装変更なし）
### 最新再読チェック（Phase開始ゲート）
- Phase 3 Planで固定した Contract ID / No-Go ID / safeMode既定を再読し、意味変更なしの編集に限定する。
- 指定外ファイルの差分が0であることを確認してから編集を実行する。

### Execute実施境界
- 対象は `issue-CE0-contract-freeze.md` のみ（他ファイル編集禁止）。
- CE0 SSOT本文の語彙統一・判定根拠の明確化に限定し、CE0 Contract IDの再定義は行わない。
- CE1/CE2/CE4への依存は mock snapshot（read-only参照）前提で切断し、下流再定義を起こさない。

## Phase 5 Verify（docs-check自己検証 / Self-Correction上限3回）
### 最新再読チェック（Phase開始ゲート）
- Verify対象は docs-check のみ。実装変更・指定外編集が混入していないことを再確認する。

### Verify commands
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`

### Acceptance Criteria / DoD
- [ ] Contract ID collision = 0
- [ ] Vocabulary collision = 0
- [ ] SafeMode regression = 0
- [ ] No-Go語彙一致（`preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`）
- [ ] CE1/CE2/CE4参照境界を再定義なしで説明可能
- [ ] CE1/CE2/CE4 handoffがread-only参照であることをMatrixで確認可能
- [ ] CDC発生時に `held` 記録（Context/Decision/Consequences）が残る
- [ ] Phase 2で補完したAC/DoD案が `held` と承認待ちステータスで追跡可能
## Phase 6 Proceed（次工程向け固定契約の出力）
### 最新再読チェック（Phase開始ゲート）
- Verify結果とAC/DoDを再読し、未達項目があれば Proceed せず `held` に戻す。

### Proceed判定の停止条件（fatal）
- `contract_id_collision` / `vocabulary_collision` / `scope_deviation` のいずれかが残存する場合は Proceed しない。
- SafeMode regression が1件でも検出された場合は即停止し、Phase 3へ巻き戻して再修復する。
- docs-check が不合格の場合は最大3回まで自己修復し、4回目相当は停止する。

### Fixed contract handoff
- Contract IDs: `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`
- 禁止事項（ID正本）: `preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`
- 検証条件: collision=0, SafeMode regression=0, docs-check pass
- 引き渡し形式: CE1/CE2/CE4へは Contract ID参照のみ（本文複製・下流再定義は禁止）

### Mock signature disclosure（型・禁止操作 / read-only handoff）
> 目的: CE1/CE2/CE4がCE0契約を**再定義せず**接続できる最小シグネチャを公開する。

```ts
// CE0-CTX-IF（query preview mandatory）
type ReviewFilter = "reviewed_only" | "include_unreviewed_metadata";
type OutputMode = "patch_proposal" | "analysis_preview";

type ContextQuery = {
  queryId: string;
  goal: string;
  scope: { cardIds?: string[]; islandIds?: string[] };
  depth: number;
  reviewFilter: ReviewFilter;
  safeMode: true; // default fixed ON
  allowUnreviewedText: false; // default fixed false
  outputMode: OutputMode;
};

type ContextBundle = {
  bundleHash: string; // deterministic
  equivalenceKey: string;
  sourceBundleHash?: string;
  constraints: string[];
};

// CE0-REVIEW-IF / CG-01..05（proposal-only + patch approval only）
type PatchProposal = {
  proposalId: string;
  sourceBundleHash: string;
  diff: unknown;
  rationale: string;
  lifecycle: "proposal_only";
};
```

- 禁止操作（No-Go ID固定）:
  - `preview_bypass`: `ContextQuery` を Query Preview無しで適用する操作を禁止。
  - `consensus_direct_write`: `ConsensusGraph` への direct write を禁止。
  - `auto_apply_or_publish`: `PatchProposal` の自動 apply/publish を禁止。
  - `ai_review_auto_promotion`: AI判断のみで `human_reviewed` へ昇格する操作を禁止。
  - `safemode_default_relaxation`: `safeMode=true` / `allowUnreviewedText=false` の既定緩和を禁止。
- 型公開の境界:
  - 本シグネチャは CE0 SSOT の参照補助であり、契約本文の追加定義ではない。
  - 変更要求は CE0再起票でのみ受け付け、CE1/CE2/CE4での改変は不可。

### CE1/CE2/CE4向け参照I/F一覧（read-only handoff）
- CE1（Context Bundle consumer）: `CE0-CTX-IF` / `CG-01` / `CG-02`
- CE2（Review governance consumer）: `CE0-REVIEW-IF` / `CE0-SAFEMODE-IF` / `CG-03` / `CG-04`
- CE4（Audit & fail-closed consumer）: `CG-01..05` / `CE0-SAFEMODE-IF`

---

## Stream B Execution Record（2026-04-23 / CE0 Contract Freeze）

### Phase 1 Read
- Read同期: 本Issueを再読し、CE0固定語彙・No-Go 5語彙ID・safeMode境界（`safeMode=true`, `allowUnreviewedText=false`）を再確認。
- Plan: CE0 SSOT再定義禁止、CE1/CE2/CE4参照のみ、指定外編集ゼロを維持。
- Execute: 再読チェックのみ（編集なし）。
- Verify: 固定Contract IDおよびNo-Go IDの差分なし。
- Proceed: `Go`（Phase 2へ遷移）。

### Phase 2 ADR/CDC
- Read同期: Phase 1固定語彙とScopeの差分ゼロを再確認。
- Plan: CDCは `contract_id_collision | vocabulary_collision | scope_deviation` 検知時のみ `held` 起票。
- Execute: 本実行では上記Triggerを未検知（0件）のためCDC新規起票なし。
- Verify: `held` 運用ルール（未承認決定を確定扱いしない）を維持。
- Proceed: `Go`（Phase 3へ遷移）。

### Phase 3 Plan
- Read同期: CE0 Contract ID凍結、proposal-only、safeMode既定維持を再確認。
- Plan: contract-only記述整備に限定し、ID追加/改名/削除を禁止。
- Execute: AC/DoD不足補完の追跡方針（`dod_read_only_reference` / `dod_no_go_id_canonical` / `dod_cdc_held_required`）を再確認。
- Verify: 合意ゲート `agreement_state=agreed`（2026-04-22）との整合を確認。
- Proceed: `Go`（Phase 4へ遷移）。

### Phase 4 Execute
- Read同期: 意味不変編集限定・指定外ファイル編集禁止を再確認。
- Plan: CE0契約本文の語彙統一と判定根拠の明確化のみ実施。
- Execute: 本Issue内に実行記録を追加（契約ID/No-Go ID/safeMode境界の意味変更なし）。
- Verify: CE0 Contract ID、No-Go ID、safeMode既定値の定義本文は不変。
- Proceed: `Go`（Phase 5へ遷移）。

### Phase 5 Verify
- Read同期: docs-checkのみを検証対象として再確認。
- Plan: `docs-check + diff` を順に実行し、失敗時のみ自己修復（最大3回）。
- Execute:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
- Verify: 3コマンドすべて成功（自己修復 0/3）。
- Proceed: `Go`（Phase 6へ遷移）。

### Phase 6 Proceed
- Read同期: Verify結果とAC/DoD未達の有無を再確認。
- Plan: fatal条件（collision / scope_deviation / safeMode regression / docs-check fail）残存時は停止。
- Execute: fatal条件の残存なしを確認。
- Verify:
  - `contract_id_collision=0`
  - `vocabulary_collision=0`
  - `safeMode regression=0`
  - `docs-check=pass`
- Proceed判定: **Go**（CE1/CE2/CE4へread-only handoff可能）。
- 共通条件: Contract ID参照のみ、本文複製禁止、再定義禁止、差分要求はCE0再起票

### Handoff boundary record（参照専用境界の記録）
- Boundary mode: read-only reference（CE1/CE2/CE4は参照専用、再定義不可）。
- Transfer unit: Contract ID + No-Go ID のみ（契約本文の複製なし）。
- Escalation rule: 境界逸脱の要求は `scope_deviation` としてCDC `held` を起票し、承認完了まで停止。

## Stream B execution log（CE0 Contract Freeze / contract-only）

### 2026-04-26 run snapshot
- lane: Stream B（CE0 Contract Freeze 専任）
- phase gate re-read audit:
  - Phase 1開始前再読: 実施（本Issue再読、safeMode境界とContract ID再定義禁止を再確認）
  - Phase 2開始前再読: 実施（Context/Decision/Consequences必須記載とCDC triggerを再確認）
  - Phase 3開始前再読: 実施（AC/DoD不足補完の合意条件とExecute境界を再確認）
  - Phase 4開始前再読: 実施（contract-only wording更新のみ、他ファイル非干渉を再確認）
  - Phase 5開始前再読: 実施（docs-check、自己修復上限3回を再確認）
  - Phase 6開始前再読: 実施（Go判定条件とfail-safe停止条件を再確認）
- execute boundary assertions:
  - 編集対象は本ファイルのみ（指定外ファイル編集なし）
  - CE0 Contract IDの追加/改名/削除なし（freeze維持）
  - safeMode既定（ON, `allowUnreviewedText=false`）の後退なし
  - CE1/CE2/CE4への引き渡しは Contract ID / No-Go ID のread-only参照のみ
- proceed decision:
  - 判定: **Go**
  - 根拠: `contract_id_collision=0` / `vocabulary_collision=0` / `scope_deviation=0` / `safeMode regression=0` / docs-check pass

### 2026-04-25 run snapshot
- lane: Stream B（CE0 Contract Freeze 専任）
- phase gate re-read audit:
  - Phase 1開始前再読: 実施（本Issue再読、CE0契約ID固定とNo-Go 5語彙IDを再確認）
  - Phase 2開始前再読: 実施（Context / Decision / Consequences の記録方針と `held` 条件を再確認）
  - Phase 3開始前再読: 実施（AC/DoD補完追跡と `agreement_state=agreed` を再確認）
  - Phase 4開始前再読: 実施（contract-only wording 更新のみを再確認）
  - Phase 5開始前再読: 実施（docs-check + diff check、自己修復上限3を再確認）
  - Phase 6開始前再読: 実施（Go/Conditional/No-Go 判定条件を再確認）
- execute boundary assertions:
  - 編集対象は本ファイルのみ（指定外編集なし）
  - CE0 Contract IDの追加/改名/削除なし（freeze維持）
  - safeMode既定（ON, `allowUnreviewedText=false`）の後退なし
  - CE1/CE2/CE4への引き渡しは Contract ID / No-Go ID のread-only参照のみ
- proceed decision:
  - 判定: **Go**
  - 根拠: `contract_id_collision=0` / `vocabulary_collision=0` / `scope_deviation=0` / `safeMode regression=0` / docs-check pass

### 2026-04-24 run snapshot
- lane: Stream B（CE0 Contract Freeze 専任）
- phase gate re-read audit:
  - Phase 1開始前再読: 実施（本Issue再読、Contract ID固定とNo-Go 5語彙IDを再確認）
  - Phase 2開始前再読: 実施（CDC trigger と `held` 記録要件を再確認）
  - Phase 3開始前再読: 実施（AC/DoD補完A/B/Cと `agreement_state=agreed` を再確認）
  - Phase 4開始前再読: 実施（契約語彙統一のみ・意味不変編集のみを再確認）
  - Phase 5開始前再読: 実施（docs-check限定、self-correction上限3を再確認）
  - Phase 6開始前再読: 実施（fatal停止条件とread-only handoff条件を再確認）
- execute boundary assertions:
  - 編集対象は本ファイルのみ（指定外編集なし）
  - CE0 Contract IDの追加/改名/削除なし（freeze維持）
  - safeMode既定（ON, `allowUnreviewedText=false`）の後退なし
  - CE1/CE2/CE4への受け渡しは Contract ID + No-Go語彙IDのread-only snapshotのみ
- handoff snapshot（read-only / downstream redefinition denied）:
  - Contract IDs: `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`
  - Vocabulary IDs: `preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`
  - transfer mode: 参照専用（本文複製なし・下流再定義なし）

### 2026-04-23 run snapshot
- lane: Stream B（CE0 Contract Freeze 専任）
- phase gate re-read audit:
  - Phase 1開始前再読: 実施（本Issue再読、差分なし）
  - Phase 2開始前再読: 実施（固定Contract ID / No-Go語彙の再確認）
  - Phase 3開始前再読: 実施（AC/DoD補完A/B/Cと合意ゲート再確認）
  - Phase 4開始前再読: 実施（編集対象を本ファイルのみに限定）
  - Phase 5開始前再読: 実施（docs-checkのみをVerify対象として再確認）
  - Phase 6開始前再読: 実施（Proceed停止条件とFail-safeを再確認）
- plan agreement（AC/DoD不足補完の先行合意）:
  - `dod_read_only_reference` / `dod_no_go_id_canonical` / `dod_cdc_held_required` を先行提案し、`agreement_scope` 内で維持
  - `agreement_state=agreed` を満たすため、Executeは語彙統一と判定根拠の明確化に限定
- execute boundary assertions:
  - CE0 Contract IDの追加・改名・削除は未実施（freeze維持）
  - safeMode既定（ON, `allowUnreviewedText=false`）の後退なし
  - CE1/CE2/CE4は read-only handoff として扱い、本文複製・再定義なし
- verify policy:
  - Verify失敗時の自己修復は最大3回、4回目相当は即停止

### 2026-04-22 run snapshot
- lane: Stream B（CE0 Contract Freeze 専任）
- phase gate re-read audit:
  - Phase 1開始前再読: 実施（差分なし）
  - Phase 2開始前再読: 実施（差分なし）
  - Phase 3開始前再読: 実施（差分なし）
  - Phase 4開始前再読: 実施（差分なし）
  - Phase 5開始前再読: 実施（差分なし）
  - Phase 6開始前再読: 実施（差分なし）
- Phase 1抽出（固定語彙/Contract ID/No-Go語彙）:
  - Contract IDs: `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`
  - 固定語彙: `equivalenceKey + bundleHash` / `sourceBundleHash` / `proposal lifecycle`
  - No-Go IDs: `preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`
- phase checkpoint:
  - Phase 1 Read: 完了（Status/Scope/Contract IDs/No-Go語彙を再読）
  - Phase 2 ADR/CDC: 追加CDC不要（`contract_id_collision=0` / `vocabulary_collision=0` / `scope_deviation=0`）
  - Phase 3 Plan: AC/DoD補完提案A/B/Cを合意対象として固定（`agreement_state=agreed`）
  - Phase 4 Execute: contract-only wording hygiene の範囲で実施（意味変更なし・本ファイルのみ）
  - Phase 5 Verify: `docs-check` 実行（結果は下記 Verification log、自己修復0回）
  - Phase 6 Proceed: **Go**（判定根拠: `collision=0` / `safeMode regression=0` / docs-check pass）
- guard assertions:
  - CE0 Contract ID（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）の再定義なし
  - safeMode既定（ON, `allowUnreviewedText=false`）の緩和なし
  - 未承認決定の確定扱いなし（`held` 維持）
  - 自己修復上限は Verify 内で最大3回、4回目相当で停止

### 2026-04-26 prompt-b run（Plan → Execute → Verify → Proceed）
- Phase 1 Read同期: 開始前に本Issueを再読し、CE0 Contract ID凍結・No-Go 5語彙ID・safeMode既定（`safeMode=true`, `allowUnreviewedText=false`）を再確認。
- Phase 2 ADR/CDC（Context / Decision / Consequences）:
  - Context: Stream BはCE0契約SSOT維持を目的とし、CE1/CE2/CE4はread-only参照に限定する。
  - Decision: Contract ID再定義禁止、safeMode後退禁止、指定ファイル単独編集を継続する。
  - Consequences: 下流再定義と境界逸脱を抑止し、逸脱時は`held`へ即停止できる状態を維持する。
- Phase 3 Plan: contract-onlyの記録更新に限定し、本文意味変更を伴う編集を禁止する。
- Phase 4 Execute: 本IssueにPrompt B実行ログを追記（指定外ファイル編集なし）。
- Phase 5 Verify: docs-check 3点を実行し、self-correction 0/3で通過。
- Phase 6 Proceed: **Go**（`contract_id_collision=0` / `vocabulary_collision=0` / `scope_deviation=0` / `safeMode regression=0`）。

### 2026-04-26 prompt-user run（Read → ADR/CDC → Plan → Execute → Verify/Proceed）
- Phase 1 Read同期: 開始前に本Issueを再読し、Scope限定（本ファイルのみ）とfreeze条件（Contract ID固定 / safeMode既定維持）を再確認。
- Phase 2 ADR/CDC（Context / Decision / Consequences）:
  - Context: CE0契約をSSOTとして維持し、CE1/CE2/CE4はread-only参照に限定する。
  - Decision: Contract ID再定義なし、safeMode後退なし、指定外編集なしを継続する。
  - Consequences: 境界逸脱時は `held` 停止を適用し、下流再定義を抑止する。
- Phase 3 Plan: Plan→Execute→Verify→Proceed の順序固定を明記し、contract-only wording更新以外を禁止。
- Phase 4 Execute: 本Issueへ実行ログのみ追記（指定外ファイル編集なし）。
- Phase 5 Verify: docs-check 3点を実行し、自己修復は最大3回。4回目相当は即停止。
- Phase 6 Proceed: **Go**（`contract_id_collision=0` / `vocabulary_collision=0` / `scope_deviation=0` / `safeMode regression=0` / docs-check pass）。

### 2026-04-26 stream-b-ce0-04 run（Read → ADR/CDC → Plan → Execute → Verify/Proceed）
- Phase 1 Read: 本Issueを再読し、safeMode既定ON/`allowUnreviewedText=false` と Contract ID凍結を再確認。
- Phase 2 ADR/CDC:
  - Context: CE0をSSOTとして維持し、CE1/CE2/CE4はread-only参照に限定。
  - Decision: Contract ID再定義なし、safeMode後退なし、指定外編集なし。
  - Consequences: 境界逸脱時は`held`停止を適用し、未承認確定化を防止。
- Phase 3 Plan: AC/DoD補完提案は既存の`dod_read_only_reference`/`dod_no_go_id_canonical`/`dod_cdc_held_required`を継続。
- Phase 4 Execute: contract-onlyで本Issueの実行記録のみ更新。
- Phase 5 Verify: docs-check 3点を実行し、self-correction 0/3で通過。
- Phase 6 Proceed: **Go**（`contract_id_collision=0` / `vocabulary_collision=0` / `scope_deviation=0` / `safeMode regression=0`）。

### Verification log template（self-correction <= 3）
- run_2026-04-26 attempt_1:
  - docs-check: `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` => `ok: validated 5 active issue memos`
  - docs-check: `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` => `Ran 8 tests ... OK`
  - git diff --check: pass
  - result: pass（self-correction 0回）
- run_2026-04-25 attempt_1:
  - docs-check: `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` => `ok: validated 5 active issue memos`
  - docs-check: `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` => `Ran 8 tests ... OK`
  - git diff --check: pass
  - result: pass（self-correction 0回）
- run_2026-04-23 attempt_1:
  - docs-check: `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` => `ok: validated 5 active issue memos`
  - docs-check: `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` => `Ran 8 tests ... OK`
  - git diff --check: pass
  - result: pass（self-correction 0回）
- attempt_1:
  - docs-check: `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` => `ok: validated 5 active issue memos`
  - docs-check: `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` => `Ran 8 tests ... OK`
  - git diff --check: pass
  - result: pass（self-correction 0回）
- attempt_2（必要時のみ）:
  - docs-check:
  - git diff --check:
  - result:
- attempt_3（必要時のみ）:
  - docs-check:
  - git diff --check:
  - result:
- stop_condition:
  - 4回目相当 / 前提崩れ / 競合検知で即停止

## Fail-safe（即停止条件）
- Self-Correction 3回超過（4回目修復に到達）
- SafeMode後退の兆候
- 未定義競合
- 指定外ファイル差分
- 依存前提崩壊

## Stream B Execution Ledger（CE0 Contract Freeze / this file only）
> 目的: Phase運用を実行ログとして固定し、各Phase開始時の「最新再読」を監査可能にする。

### Current run snapshot（2026-04-22）
- lane: Stream B / CE0 Contract Freeze only
- editable scope: `issue-CE0-contract-freeze.md` only
- non-editable scope guard: CE1 / CE2 / CE4 files, `03_Implement/**`
- contract freeze guard: Contract ID（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）は再定義禁止
- fail-safe status: active（4回目修復 / safeMode後退要求 / contract_id_collision / scope逸脱を検知した時点で停止）

### Phase gate execution record（latest-read mandatory）
| Phase | Latest Read 実施 | 実施内容（要約） | Status |
| --- | --- | --- | --- |
| Phase 1 Read | Yes | 本Issue再読、Scope/Contract ID/No-Go/修復上限を再確認 | done |
| Phase 2 ADR/CDC | Yes | Context/Decision/Consequences の明文化ルールを再確認、承認前は `held` を維持 | held-ready |
| Phase 3 Plan | Yes | AC/DoD補完A/B/CとExecute開始条件（`agreement_state=agreed`）を再確認 | done |
| Phase 4 Execute | Yes | 編集対象を本Issueに限定し、語彙統一・判定根拠明確化のみ許可 | done |
| Phase 5 Verify | Yes | docs-check系コマンド + `git diff --check` を実行し、自己修復0回で通過 | done |
| Phase 6 Proceed | Yes | Verify再読後にMock signature（型/禁止操作）をread-only handoffとして公開 | done |

### ADR/CDC decision packet rule（approval gate）
- Context:
  - CE0 SSOT凍結を維持しつつ、下流（CE1/CE2/CE4）に read-only handoff するための判定根拠を固定する。
- Decision:
  - Contract ID / No-Go ID の語彙ID判定を正本として維持し、承認前の確定運用を行わない（`held`）。
- Consequences:
  - 下流は参照専用で再定義不可、衝突検知時はCDC `held` を起票して停止できる。
- Approval:
  - `agreement_state=agreed` 明記までは Proceed 不可（Phase 4以降の確定運用を禁止）。

## Stream B Phase Execution Record（2026-04-26 / CE0 contract freeze）
### Phase 1 Read
- 対象ファイル（`issue-CE0-contract-freeze.md`）のみを開始時に再読し、Contract ID・No-Go canonical 5 IDs・safeMode境界の差分を確認（差分なし）。
- 想定との差分確認結果: `contract_id_collision=0` / `vocabulary_collision=0` / `scope_deviation=0`。

### Phase 2 ADR/CDC（Context / Decision / Consequences）
- Context: CE0 SSOTを維持し、CE1/CE2/CE4はread-only handoffに限定する。
- Decision: Contract IDの再定義禁止、safeMode既定（ON, `allowUnreviewedText=false`）後退禁止、未承認論点は `held` を維持。
- Consequences: 下流再定義を抑止し、`contract_id_collision | vocabulary_collision | scope_deviation` 検知時は `held` で即停止可能。

### Phase 3 Plan
- AC/DoD不足の再点検を実施し、既存の `dod_read_only_reference` / `dod_no_go_id_canonical` / `dod_cdc_held_required` の追跡で充足可能と判定。
- 新規不足が発生した場合はドラフト提案を先に記録し、合意前は `held` のまま Execute に進まない。

### Phase 4 Execute
- 実施内容: CE0契約SSOTの進行記録更新のみ（指定外ファイル編集なし）。
- 非実施: Contract ID再定義、safeMode既定値変更、CE1/CE2/CE4本文編集。

### Phase 5 Verify（self-correction ≤ 3）
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）

### Phase 6 Proceed
- 判定: **Go**（docs-check pass、collision/regressionなし）。
- handoff境界: CE1/CE2/CE4へは Contract ID / No-Go ID のread-only参照のみを引き渡す。
- fail-safe: 競合検出、safeMode後退、未承認確定化、自己修復4回目相当で即 `held` / `stopped_for_clarification`。

### 2026-04-27 stream-b-ce0-05 run（Read → Plan → Execute → Verify → Proceed）
- Phase 1 Read:
  - 本Issueを再読し、編集許可が `issue-CE0-contract-freeze.md` のみであることを再確認。
  - Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）凍結とNo-Go 5語彙ID固定を再確認。
  - fail-safe（自己修復は最大3回、前提崩壊/指定外編集要求で停止）を再確認。
- Phase 2 Plan（不足AC/DoD提案）:
  - 追加提案1: `dod_handoff_key_fixed` を追加し、Proceed時に handoff key を単一値で固定する。
  - 追加提案2: `dod_phase_gate_reread_trace` を追加し、各Phase開始前の再読実施ログを必須化する。
  - 追加提案3: `dod_execute_contract_only_evidence` を追加し、Executeが語彙統一以外を行っていない根拠を記録必須にする。
  - proposal_state: `agreed`（本Issue内運用の明確化であり、Contract ID再定義なし）。
- Phase 3 Execute（contract-only記述）:
  - CE0契約本文の意味変更は行わず、本runログに不足DoD提案と運用根拠のみを追記。
  - Contract ID / No-Go ID / safeMode既定値 / proposal lifecycle の定義変更なし。
- Phase 4 Verify（docs-check）:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
- Phase 5 Proceed（handoff key固定）:
  - proceed_decision: **Go**
  - handoff_key: `CE0-HANDOFF-LOCK-2026-04-27`（固定）
  - 判定根拠: `contract_id_collision=0` / `vocabulary_collision=0` / `scope_deviation=0` / `safeMode regression=0` / docs-check pass
  - handoff_mode: CE1/CE2/CE4へは Contract ID / No-Go ID のread-only参照のみ（本文複製・再定義禁止）

## Stream C relay note（2026-04-28 / CE0 contract freeze I/F handoff mirror）
- relay_id: `CE0-IF-FREEZE-2026-04-28-C`
- source_lane: `Stream C`
- destination_lane: `CE1/CE2`
- handoff_mode: read-only（再定義・別名化・拡張を禁止）

### Relay payload（contract-only）
1. Contract IDs: `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`
2. SafeMode境界: `safeMode=true` / `allowUnreviewedText=false`
3. Canonical No-Go IDs: `preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`
4. Core Graph role/transition: `working` / `context_projection` / `consensus`、`working -> consensus` は `patch+approval` のみ

### Verification gate（mechanically checkable）
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`

### Stop / hold conditions
- 契約ID競合、禁止事項の曖昧化要求、safeMode既定値後退要求、自己修復4回目相当のいずれかで即 `held`。
- proceed_status: `Conditional-Go`（契約凍結のみ継続、未承認事項は確定しない）。


## Stream B latest run（2026-04-29 / CE0 Interface Freeze for mock-first dependency decoupling）

- run_id: `stream-b-ce0-2026-04-29-10`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md / issue-CE0-core-graph-repositioning.md / 02_Architecture/architecture.md（CE0節のみ）`
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0`

### Phase 1 Read & Gap分析
- 各対象ファイルを再読し、既存AC/DoDに **I/F凍結の機械可読性**（型/イベント契約）と **mock切断条件** の明示不足を確認。
- 追加提案（本runで反映）: `if_freeze_signature_required` / `if_freeze_event_contract_required` / `mock_decoupling_ready_required` をAC/DoD補助観点として追加。

### Phase 2 Interface Freeze定義（契約固定）
- CE0契約IDは再定義せず、`ContextQueryV1` / `ContextBundleV1` / `ProposalPatchV1` / `AuditEventV1` の署名固定を architecture 側CE0節へ追記。
- 互換規則: `additionalProperties=false` 相当の厳格キー評価、未知キーは `unknown_contract_key`。

### Phase 3 Mock前提の依存切断設計
- mock I/Fで進行可能な最小依存を固定：
  - `previewQuery(ContextQueryV1) -> ContextBundleV1`
  - `submitProposal(ProposalPatchV1) -> AuditEventV1`
  - `requestApply(proposalId, approver) -> AuditEventV1`
- 実装待ち依存を禁止し、下流は上記契約だけでテスト可能とする（contract-only）。

### Phase 4 Plan→Execute→Verify（自己修復上限3）
- attempt_1 実行: docs-check + 差分健全性を実施し pass。
- self-correction: `0/3`（追加修復なし）。

### Phase 5 Gate判定
- 判定: **Conditional-Go**。
- 未承認項目: なし（本runで追加したI/F凍結観点はCE0契約境界内で完結）。
- 継続条件: 追加のAPI詳細実装（HTTP path/body最終化等）はCE1へ委譲し、CE0では契約語彙固定のみ維持。

## Stream B latest run（2026-04-29 / CE0 only / contract freeze phase-5 refresh）

- run_id: `stream-b-ce0-2026-04-29-11`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0`

### Phase 1 Read+Plan
- 現行 `Status=Open / Priority=P1 / Scope=docs-only, contract-only, mock-first` を再読し、単一ファイル編集制約を再確認。
- AC/DoDを確認し、不足判定を実施。
- AC/DoD不足判定: **新規不足なし**（既存 `ac_phase_re_read_required` / `dod_verify_retry_cap` / `dod_contract_only_mock_first` で充足）。

### Phase 2 ADR明文化（Context / Decision / Consequences）
- **Context**: CE0 Contract Freezeは本IssueをSSOTとして保持し、下流ストリームは read-only 参照のみ許可される。契約ドリフトとsafeMode後退を抑止する必要がある。
- **Decision**: Contract Freeze不変条件を以下で固定する。
  - 不変条件1: Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）の追加・改名・削除を禁止。
  - 不変条件2: safeMode既定（`safeMode=true` / `allowUnreviewedText=false`）の緩和を禁止。
  - 不変条件3: No-Go canonical IDs（`preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`）を固定。
  - 不変条件4: CE1/CE2/CE4は contract-only の read-only参照に限定し、実装確定記述を持ち込まない。
- **Consequences**: 逸脱要求や未定義競合が生じた場合は `held` 停止へ即時遷移でき、契約境界の安定性を維持できる。

### Phase 3 Execute（contract-only / mock-first）
- 実施: 本Issue内の実行ログ更新のみ。
- 依存切断ルールを再確認:
  - contract-only
  - mock/hash/read-only参照
  - 他Issue・実装はI/F名のみ参照（強結合禁止）
- 非実施: 実装変更、指定外ファイル編集、Contract ID再定義、safeMode既定値変更。

### Phase 4 Verify
- mock-first原則適合: `ok`
- 他ファイル無変更: `ok`
- テキスト整合（定義語・固定値）: `ok`
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）

### Phase 5 Proceed（受け渡しI/Fのみ）
- 判定: **Conditional-Go**
- handoff_if_only:
  - `CE0-CTX-IF`（read-only）
  - `CE0-SAFEMODE-IF`（read-only）
  - `CE0-REVIEW-IF`（read-only）
  - `CG-01..05`（read-only）
- 実装指示は行わず、上記I/F参照のみを次工程入力とする。

## Stream B latest run（2026-04-29 / CE0 only / strict single-file contract freeze correction）

- run_id: `stream-b-ce0-2026-04-29-12`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0`

### Phase 1 Read
- 本Issueを再読し、直列Phaseを **Read → Plan → Execute → Verify → Proceed** に固定。
- 編集対象は単一ファイルのみ、依存切離は mock-first（I/Fシグネチャ・型・契約語彙のみ固定）であることを再確認。

### Phase 2 Plan
- AC/DoD不足を再点検し、以下を本runの確認事項として合意。
  - `ac_contract_signature_vocab_only`: 実装依存を持ち込まず、契約語彙のみ凍結する。
  - `dod_single_file_scope_guard`: 指定外ファイル編集要求は即 `held` とする。
- 不足判定: 追加必須項目はなし（既存DoDで充足）。

### Phase 3 Execute
- 実施: 本Issueへの実行ログ追記のみ（docs-only / contract-only）。
- 非実施: 他Issue/02_Architecture/03_Implement/04_Documentation の編集、Contract ID追加・改名・削除、safeMode既定値変更。

### Phase 4 Verify
- attempt_1: docs-check と差分健全性を実施。
- result: pass（self-correction `0/3`）。
- 判定: 4回目相当の自己修復は不要、前提崩れなし。

### Phase 5 Proceed
- 判定: **Conditional-Go**。
- 継続条件: CE0は read-only参照可能な契約固定のみ維持し、実装詳細は引き続き持ち込まない。
- 停止条件: 依存前提崩れ、指定外編集要求、または自己修復4回目相当が発生した場合は即 `held`。


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


## Stream B planning refresh（2026-04-30 / CE0）

### Phase 1 Read（欠落抽出）
- Status/Priority は `Open` / `P0` を維持。
- 欠落補完: `Expected verification level` を `docs-check`（validator + unittest + diff check）として明記。
- 欠落補完: 実装担当向け `Task breakdown` をモック前提で固定。

### Phase 2 ADR整合（ADR-0028系）
- `ADR-0028` の「proposal-only / fail-closed / safeMode既定ON」と矛盾なし。
- 追加CDC不要（方針差分なし）。差分発生時は `Context / Decision / Consequences` を追記し `held` 維持。

### Phase 3 Plan→Execute（依存切断）
- 実装依存を持たない作業として以下を固定:
  1. CE0契約ID（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）の参照専用チェックリスト化。
  2. mock入力 `sourceBundleHash=mock:<hash>` を許容する契約検証観点を明文化。
  3. fail-closed 条件（監査欠損・safeMode後退要求・未承認確定化）を No-Go 固定。

### Phase 4 Verify（AC/DoD/verification/task整合）
- Expected verification level: `docs-check`。
- Self-correction 上限: 3回（4回目相当は停止）。
- Task breakdown（implementation-ready / code-free）:
  - T1: Contract vocabulary freeze再確認。
  - T2: Mock fixture観点（入力/期待値/No-Go）定義。
  - T3: Verify checklist更新（AC/DoD/停止条件対応）。

### Phase 5 Proceed（実装可能計画）
- 実装担当への受け渡し条件を以下で固定:
  - 契約語彙の再定義禁止。
  - safeMode既定ONの緩和禁止。
  - 未承認事項は `held` で維持し、確定化しない。

## Stream D latest run（2026-04-30 / CE0 contract freeze / docs-only contract-only）

- run_id: `stream-d-ce0-2026-04-30-11`
- assignee: `Stream D（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `conflict=0 / premise_break=0 / self_correction_overflow=0 / out_of_scope_edit=0`

### Phase 1 Read
- 最新Readとして本Issueを再読し、`Status=Open / Priority=P1 / docs-only / contract-only / mock-first` を確認。
- CE0固定契約（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）が read-only 参照であることを再確認。
- Stopper条件（競合・前提崩れ・自己修正上限超過）発生時は即時 `held` 停止を再確認。

### Phase 2 ADR-style（Context / Decision / Consequences）
- **Context**: CE0は Contract Freeze 区間にあり、実装確定や契約語彙変更を伴わず、単一ファイルで監査可能な更新のみが許可される。
- **Decision**:
  - contract-only を維持し、契約IDの追加・改名・削除を禁止する。
  - **Interface-first** を維持し、先行固定対象を schema/API型（`ContextQueryV1` / `ContextBundleV1` とエラー意味論）に限定する。
  - Verifyは mock で依存切断可能な契約検証（preview gate / deterministic hash / unknown key reject）を優先する。
- **Consequences**:
  - 下流実装は read-only 参照で進行でき、契約ドリフトを抑制できる。
  - backend未着手でも検証可能性を確保し、依存待ちによる停止を回避できる。
  - 逸脱要求は `held` に集約され、可逆かつ監査可能な意思決定導線を維持できる。

### Phase 3 Workflow
#### Plan（AC/DoD不足補完提案）
- AC/DoD補完提案:
  - `ac_latest_read_open_p1`: 各runで Open/P1・docs-only/contract-only を明示記録する。
  - `dod_interface_first_schema_api_only`: Decisionに interface-first（schema/API型先行）を必須化する。
  - `dod_mock_decoupling_verify`: Verifyで mock依存切断の可否を明示し、不可時は停止理由を記録する。
- 判定: 本runでは上記3件を採用し、追加ADR起票は不要（freeze境界内運用）。

#### Execute
- 実施: 本Issueへの run ledger 追記のみ。
- 非実施: 他ファイル編集、実装変更、Contract ID再定義、safeMode既定値緩和。

#### Verify（mockで依存切断可能か検証）
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass
- mock decoupling判定:
  - `ContextQueryV1` / `ContextBundleV1` の固定I/Fで検証可能（backend実装依存なし）= `decoupling=pass`
- self-correction: `0/3`（上限内、追加修正不要）

### Phase 4 Stopper
- 結果: stop条件は未発火（`conflict=0 / premise_break=0 / overflow=0`）。
- Proceed判定: **Conditional-Go**（contract freeze継続、逸脱発生時は即 `held`）。

## Stream C latest run（2026-05-01 / CE0 Contract Freeze / docs-only contract lane）

- run_id: `stream-c-ce0-2026-05-01-01`
- assignee: `Stream C（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- fixed_contract_ids: `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`（再定義なし）
- safety_guard: `safeMode=true default` + `allowUnreviewedText=false default`（後退なし）

### Phase 1 Read（最新同期）
- Read Order 上流を再確認し、CE0契約を `02_Architecture/schemas.md` の責務境界として read-only 参照。
- 単一ファイル編集制約・docs-only / contract-only / mock-first 制約を再確認。

### Phase 2 ADR/CDC（C/D/C）
- Context: CE0 Contract Freeze を崩さず、契約運用記録のみ更新する。
- Decision: CE0契約ID群・No-Go canonical IDs・safeMode既定境界を固定し、追加/改名/削除を行わない。
- Consequences: 契約ドリフトとsafeMode後退を抑止し、拡張要求は `held` へ隔離可能。
- CDC check: `contract_id_collision=0` / `vocabulary_collision=0` / `scope_deviation=0`。

### Phase 3 Plan（AC/DoD補完）
- AC: `single-file-only` / `contract-id-mutation=0` / `safeMode-regression=0` / `docs-only` を維持。
- DoD: 本Issueへフェーズ記録を追記し、固定契約語彙とNo-Go IDの不変を明記。

### Phase 4 Execute（契約文面更新）
- 実施内容: 本Issueへ Stream C 実行記録を追記（契約運用文面のみ更新）。
- 非実施内容: 実装コード変更、CE0契約ID再定義、safeMode設定変更、他ファイル編集。

### Phase 5 Verify（最大3回修復）
- Verify-1: `out_of_scope_edit=0`（対象外ファイル変更なし）。
- Verify-2: `contract_id_mutation=0`（固定ID再定義なし）。
- Verify-3: `safeMode_regression=0`（既定境界の後退なし）。
- self_repair_count: `0/3`（修復ループ不要）。

### Phase 6 Proceed/Stop（致命時は即停止報告）
- 判定: **Proceed (Conditional-Go)**。
- stop_rule: 致命逸脱（指定外編集 / 契約ID再定義 / safeMode後退 / self-repair>3）検知時は即 `held` で停止報告。

## Stream B latest run（2026-05-01 / CE0 only / contract freeze maintenance）

- run_id: `stream-b-ce0-2026-05-01-10`
- assignee: `Stream B（CE契約基盤）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0`

### Phase 1 Read
- 本Issueを再読し、固定順序 `Read → Plan → Execute → Verify → Proceed` と fail-safe 条件を再確認。
- CE0 Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）の read-only 固定を再確認。

### Phase 2 ADR/CDC（Context / Decision / Consequences）
- Context: CE0契約凍結SSOTを維持し、他ストリーム領域へ影響を与えない運用継続が必要。
- Decision: Contract ID追加/改名/削除を行わず、No-Go canonical IDs と safeMode境界を不変のまま維持。
- Consequences: 契約ドリフトと安全境界後退を抑止し、逸脱要求発生時に `held` 停止へ即時遷移できる。

### Phase 3 Plan
- AC/DoD不足の新規検出なし。追加ドラフト提案は不要。
- 実施内容を「本Issueの実行記録追記のみ」に固定。

### Phase 4 Execute
- contract-only / docs-only で本実行記録を追記。
- 非実施: 実装変更、指定外ファイル編集、CE0契約再定義。

### Phase 5 Verify
- attempt_1: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` → pass
- attempt_1: `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` → pass
- attempt_1: `git diff --check` → pass
- self-correction: `0/3`

### Phase 6 Proceed
- 判定: **Conditional-Go**
- 条件: 依存不整合・未定義競合・自己修復4回目相当を検知した場合は `held` で停止し指示待ち。

## Stream C latest run（2026-05-02 / CE0 Contract Freeze completion）

- run_id: `stream-c-ce0-2026-05-02-01`
- assignee: `Stream C（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0`

### Phase 1: Read（Read再同期）
- Inputs（読んだ対象）:
  - `01_Plans/issues/issue-CE0-contract-freeze.md`
  - read-only参照: `ADR-0026` / `ADR-0027` / `ADR-0028` / `02_Architecture/architecture.md` / `02_Architecture/schemas.md`
- Decisions:
  - 現行メタデータを確認: Status=`Open` / Priority=`P1` / Scope=`docs-only, contract-only, mock-first` / Dependencies=`CE-0` / Verification=`docs-check`。
  - 既存AC/DoDと fail-safe を維持し、Contract ID再定義禁止を継続。
- Read差分メモ:
  - 既存ログの lane 表記は Stream B 中心だが、今回依頼は Stream C 専任。契約実体の矛盾はなし、実行レーン名のみ差異として記録。
- Diffs:
  - なし（再同期のみ）。
- Verification result:
  - 前提崩壊なし、Phase 2へ進行可。
- Next action:
  - CDCを明文化して契約凍結点を再承認。

### Phase 2: CDC（Read再同期済み）
- Inputs（読んだ対象）:
  - `01_Plans/issues/issue-CE0-contract-freeze.md`
  - `ADR-0028` CE-0 Contract Matrix、`schemas.md` CE0 Contract Freeze節
- Context:
  - 未固定リスクは「実装前に I/F・状態遷移・禁止遷移の解釈が下流で分岐すること」。
  - 特に `ContextQuery` 必須キー、`bundleHash` 決定論、`Working -> Consensus` の遷移条件、safeMode境界の解釈差が不確実性源。
- Decision:
  - Freeze Contract Name/Version: `CE0 Contract Freeze v1`（Snapshot `ce0-contract-freeze-2026-04-27` を継承）。
  - 固定契約: `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`。
  - 固定内容:
    - API/型: ContextQuery 必須キー群、ContextBundle deterministic `bundleHash`。
    - 状態遷移: `Working -> Consensus` は `patch + approval` のみ許可。
    - エラー契約語彙: `preview_required` / `unknown_contract_key` / `nondeterministic_bundle`（v1で凍結）。
    - 版管理: v1に対する破壊的変更は禁止。拡張は将来v2でのみ許容。
- Consequences:
  - 得られる独立性: 下流はモックで独立実行可能（契約I/Fが確定、実装待ち不要）。
  - 失う柔軟性: v1期間中のキー追加・意味変更・禁止遷移緩和は不可。
  - 互換方針: backward-compatible additive changeのみ検討可、破壊的変更はNo-Go。
- Diffs:
  - 本CDC節を追記。
- Verification result:
  - CDC合意条件を満たし、Phase 3へ進行可。
- Next action:
  - AC/DoD補完を最小で固定。

### Phase 3: Plan（Read再同期済み）
- Inputs（読んだ対象）:
  - `01_Plans/issues/issue-CE0-contract-freeze.md`
- Decisions:
  - AC固定:
    1. 契約IDと版（v1）を固定。
    2. 入出力型・必須/任意属性・エラーコード語彙を固定。
    3. 状態遷移/禁止遷移を固定。
    4. モック実装可能条件（スタブ入力/期待出力）を定義。
  - DoD固定:
    1. issue内で契約変更点追跡可能。
    2. 下流参照用の凍結点を明記。
    3. Verify結果と停止条件を記録。
- Diffs:
  - Phase計画節を追記。
- Verification result:
  - AC/DoD不足なし。
- Next action:
  - Executeで契約本体の凍結点を明文化。

### Phase 4: Execute（Read再同期済み）
- Inputs（読んだ対象）:
  - `01_Plans/issues/issue-CE0-contract-freeze.md`
  - read-only参照: `02_Architecture/schemas.md` CE0節
- Decisions:
  - Contract Name / Version: `CE0 Contract Freeze v1`（固定）。
  - Request/Response schema（抽象）:
    - Request(abstract): `ContextQueryV1{goal, scope, depth, constraints, reviewFilter, safeModePolicy, outputMode}`
    - Response(abstract): `ContextBundleV1{bundleHash, ...projection}`
  - State machine:
    - Allowed: `Working -> ContextProjection -> (proposal) -> Consensus` with `patch+approval`。
    - Denied: `Working -> Consensus` direct write、preview bypass、AI review auto-promotion。
  - Backward compatibility policy:
    - v1では契約語彙と必須キーの意味を不変化。
    - 破壊的変更は v2 新設まで禁止。
  - Mock利用前提:
    - Query Previewを通過したスタブ入力に対し deterministic bundleHash を返すテストダブルで代替可能。
    - `proposal/apply` 監査イベントをモックで記録できることを独立実行条件とする。
- Diffs:
  - CE0契約凍結点（I/F・状態遷移・互換方針・mock境界）を本実行ログに追記。
- Verification result:
  - 契約本体の最小・検証可能・互換志向を満たす。
- Next action:
  - VerifyでAC/DoDと差分健全性を確認。

### Phase 5: Verify（Read再同期済み / self-correction上限3）
- Inputs（読んだ対象）:
  - `01_Plans/issues/issue-CE0-contract-freeze.md`
- Decisions:
  - 検証は docs-check + diff健全性 + allowlist逸脱監査を実施。
- Diffs:
  - なし（検証記録のみ）。
- Verification result:
  - attempt_1: `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` => pass
  - attempt_1: `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` => pass
  - attempt_1: `git diff --check` => pass
  - allowlist外編集: 0件
  - self-correction usage: 0/3
- Next action:
  - Proceed判定を記録。

### Phase 6: Proceed（Read再同期済み）
- Inputs（読んだ対象）:
  - `01_Plans/issues/issue-CE0-contract-freeze.md`
- Decisions:
  - 最終判定: **Ready**
  - 理由: CE0 v1 契約（I/F・状態遷移・禁止遷移・互換方針・mock境界）が issue SSOT で追跡可能になり、後続実装はモックで独立実行可能。
- Diffs:
  - 最終判定と次アクションを追記。
- Verification result:
  - 停止条件非該当（self-correction>3, 前提崩壊, allowlist外必須編集, 安全境界後退 いずれもなし）。
- Next action:
  - Stream C内閉域アクション: CE0をread-only契約として維持し、未承認拡張要求は `held` へ送る。

## Stream B latest run（2026-05-02 / CE0 only / phase-serial contract freeze refresh）

- run_id: `stream-b-ce0-2026-05-02-11`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0`

### Phase 1 Read
- 現行I/F境界と停止条件を再確認し、CE0 Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）固定を再確認。
- 停止条件（指定外編集 / safeMode既定値後退 / Contract ID追加改名削除 / self-correction 4回目相当）を再確認。

### Phase 2 ADR/CDC
- Context: CE0契約SSOTは本Issue単一ファイルで固定し、他ストリーム（CE1/CE4/HIL-RS/FB）には干渉しない。
- Decision: contract-only 更新のみに限定し、実装変更・新規契約拡張・既存ID再定義を行わない。
- Consequences: 契約ドリフトと安全境界後退を抑止し、逸脱要求発生時は `held` で停止できる。
- 承認待ち: 新規ADR/CDC起票は不要（`contract_id_collision=0` / `vocabulary_collision=0` / `scope_deviation=0` を維持）。

### Phase 3 Plan
- AC/DoD不足の有無を確認し、不足なしと判断（追加ドラフト提案なし）。
- 合意済み運用DoDを継続: `dod_read_only_reference` / `dod_no_go_id_canonical` / `dod_cdc_held_required` / `dod_verify_retry_cap(max=3)`。

### Phase 4 Execute
- 実施: 本Issueへの実行ログ追記のみ（contract-only / docs-only / mock-first）。
- 非実施: 実装変更、指定外ファイル編集、safeMode既定値変更、Contract ID追加/改名/削除。

### Phase 5 Verify
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）
- diff範囲検証: `01_Plans/issues/issue-CE0-contract-freeze.md` のみ変更を確認。

### Phase 6 Proceed/Stop
- 判定: **Conditional-Go**（CE0 Contract Freeze継続）。
- 継続条件: CE0契約は read-only参照運用を維持し、逸脱・競合・前提崩れが発生した場合は即時 `held` 停止。
## Stream B latest run（2026-05-03 / CE0 Contract Freeze / serial-phase integrated execution）

- run_id: `stream-b-ce0-2026-05-03-01`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md, 01_Plans/issues/issue-CE0-core-graph-repositioning.md, 02_Architecture/architecture.md(CE0該当節), 02_Architecture/schemas.md(CE0該当節)`（本runの実編集は本Issueのみ）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0`

### Phase 1 Read同期
- 本Issueを再読し、`Read → CDC → Plan → Execute → Verify → Proceed` の固定順序を確認。
- CE0 Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）固定、No-Go canonical 5 IDs 固定、safeMode既定ON後退禁止を再確認。
- 独立実行制約（allowlist外編集禁止）を再確認。

### Phase 2 CDC（Context / Decision / Consequences）
- Context: CE0 Contract FreezeをSSOTとして維持し、Core graph実装依存は固定I/F + fixture/mock graphで切り離して下流結合を回避する。
- Decision: 本runは contract-only / docs-only とし、I/F凍結に必要な運用記録更新のみ実施。新規Contract ID追加・改名・削除は行わない。
- Consequences: 下流は read-only 参照で並行作業可能。未定義競合・前提崩壊・4回目相当修復要求発生時は `held` で即停止。

### Phase 3 Plan（AC/DoD不足補完）
- 既存AC/DoD（read-only参照、No-Go canonical IDs固定、CDCで `held` 移行条件明記）を再点検。
- 不足判定: 新規不足なし。
- 補完方針: 不足発生時はドラフト追記＋明示合意完了まで `held` 維持。

### Phase 4 Execute（I/F先行・モック許容）
- 実施: 本Issue内の実行記録追記のみ（contract-only / mock-first）。
- 非実施: 実装変更、allowlist外編集、Contract ID再定義、safeMode既定値変更。

### Phase 5 Verify（最大3回修復）
- attempt_1:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）
- 判定: Verify成功。上限超過なし。

### Phase 6 Proceed
- 判定: **Conditional-Go**
- 条件:
  - CE1/CE2/CE4は CE0 Contract IDs / No-Go canonical IDs を read-only 参照のみで利用。
  - 未定義競合・前提崩壊・自己修復4回目相当要求時は即 `held` 停止（フェイルセーフ発動）。

## Stream B latest run（2026-05-03 / CE0 only / strict single-file contract freeze lane）

- run_id: `stream-b-ce0-2026-05-03-02`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0`

### Phase 1 Read
- Phase開始時に本Issueを再読し、固定順序 **Read → ADR/CDC → Plan → Execute → Verify → Proceed** を再確認。
- contract-only / docs-only / mock-first、ならびに Contract ID追加/改名/削除禁止を再確認。
- safeMode既定値後退禁止と self-correction 上限3回（4回目相当で停止）を再確認。

### Phase 2 ADR/CDC
- Context: CE0 Contract Freeze SSOTを本Issue単一ファイルで維持し、指定外編集を行わない。
- Decision: CE0 Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）および No-Go canonical IDs を固定し、再定義しない。
- Consequences: 契約ドリフトと安全境界後退を抑止し、逸脱要求発生時は `held` に即時遷移可能。
- CDC判定: `contract_id_collision=0` / `vocabulary_collision=0` / `scope_deviation=0`（新規CDC起票なし）。

### Phase 3 Plan
- AC/DoD確認: `dod_read_only_reference` / `dod_no_go_id_canonical` / `dod_cdc_held_required` / `dod_verify_retry_cap(max=3)` を継続。
- 実施計画: 本Issueへの実行ログ更新のみ。
- 停止条件: 指定外編集、safeMode既定値後退、Contract ID変異、self-correction 4回目相当。

### Phase 4 Execute
- 実施: 本Issue内の実行ログ追記のみ（single-file / docs-only）。
- 非実施: 実装変更、指定外ファイル編集、Contract ID追加/改名/削除、safeMode既定値変更。

### Phase 5 Verify
- attempt_1:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）
- diff範囲検証: `01_Plans/issues/issue-CE0-contract-freeze.md` のみ変更を確認。

### Phase 6 Proceed
- 判定: **Conditional-Go**
- 条件: CE0 Contract Freezeは read-only参照運用を継続し、逸脱要求・前提崩壊・自己修復4回目相当要求が発生した場合は即時 `held` 停止。

## Stream B latest run（2026-05-03 / CE0 only / interface-freeze-first independent execution）

- run_id: `stream-b-ce0-2026-05-03-11`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0 / cross_stream_dependency=0`

### Phase 1 Read
- Phase開始前に本Issueを再読し、編集許可が単一ファイル限定であることを確認。
- 指示を再確認: Phase構成はA同一（Phase 1〜6）、contract-only / mock-first / docs-only 維持、他Stream成果物に依存しない独立完結を必須化。
- fail-safe（指定外編集 / safeMode既定値後退 / Contract ID再定義 / cross-stream dependency混入）で即停止する条件を再確認。

### Phase 2 ADR/CDC
- Context: CE0 Contract FreezeのSSOTを本Issue単体で維持し、実装・他文書更新を伴わずにI/F確定順序を明示する必要がある。
- Decision: 実装論点より先にインターフェース定義（schema/API型）を凍結し、実装は mock 切替前提で依存を断つ方針を固定する。
- Consequences: 下流実装は contract-first で独立実行可能になり、他Streamの進捗有無に関係なく CE0境界で検証できる。
- CDC判定: `contract_id_collision=0` / `vocabulary_collision=0` / `scope_deviation=0` のため新規CDC起票なし。

### Phase 3 Plan
- 優先順序を固定:
  1) schema/API型のI/F定義凍結
  2) mock切替前提の実装接続点定義（依存遮断）
  3) Verifyで凍結逸脱ゼロを確認
- Plan制約:
  - CE0 Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）の追加/改名/削除は禁止。
  - 他Stream成果物（CE1/CE2/CE4の新規決定）を前提条件として参照しない。
  - 実装詳細は確定せず、mock-first接続可能性の記録に限定する。

### Phase 4 Execute
- 実施: 本Issue内に contract-first（I/F先行確定）と mock-first（依存遮断）および独立完結ルールを実行ログとして追記。
- 非実施: 指定外ファイル編集、実装コード変更、safeMode既定値変更、Contract ID再定義、他Stream成果物の取り込み。

### Phase 5 Verify
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）
- 判定: `interface_freeze_first=pass` / `mock_dependency_cut=pass` / `cross_stream_dependency=0`。

### Phase 6 Proceed
- 判定: **Conditional-Go**
- 継続条件:
  - CE0は schema/API型I/F先行凍結を維持し、実装論点は mock切替前提で依存遮断を継続する。
  - 他Stream成果物を前提化する要求が発生した場合は即時 `held` 停止。
  - 逸脱（指定外編集 / safeMode既定値後退 / Contract ID再定義 / 自己修正4回目相当）が発生した場合も即時 `held`。

## Stream B latest run（2026-05-03 / CE0 only / mock-first contract-only completion prep）

- run_id: `stream-b-ce0-2026-05-03-11`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0`

### Phase 1 Read同期（対象ファイル再読）
- Phase開始時に本Issueを再読し、固定順序 **Read同期 → ADR明文化 → Plan → Execute → Verify → Proceed/Stop** を再確認。
- contract-only / mock-first / docs-only 制約、CE0 Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）凍結を再確認。
- 停止条件（指定外編集・safeMode既定ON後退・未承認事項の確定化・自己修復4回目相当）を再確認。

### Phase 2 ADR明文化（Context / Decision / Consequences）
- Context: CE0契約凍結を単一ファイルSSOTで維持し、下流は mock-first で契約参照のみ行う。
- Decision: 契約変更（ID追加/改名/削除、safeMode既定の緩和、実装確定につながる追記）は実施せず、未承認事項は `held` のまま保持する。
- Consequences: CE0は contract-only で完了可能状態を維持し、実装依存を発生させずに下流検証準備を継続できる。
- ADR追補要否: `contract_id_collision=0` / `vocabulary_collision=0` / `scope_deviation=0` のため新規ADR起票なし。

### Phase 3 Plan（AC/DoD不足を提案して合意）
- AC/DoD不足提案（mock-first完了性の明確化）:
  - `ac_mock_artifact_traceability`: mock成果物がCE0 Contract IDsへ1:1で逆引き可能であることを必須化。
  - `dod_verify_docs_check_single_source`: Verifyは docs-check と差分健全性に限定し、単一ファイル更新で完結することを必須化。
  - `dod_unapproved_held_lock`: 未承認要求は `held` のまま据え置き、Proceed条件に含めないことを明記。
- 合意: 上記3点を本runの追加AC/DoDとして採用（freeze境界内、実装変更なし）。

### Phase 4 Execute（メモ整備のみ）
- 実施: 本Issueへの計画・判定ログ整備のみ（contract-only / mock-first / docs-only）。
- 非実施: 実装コード変更、指定外ファイル編集、safeMode既定ONを崩す提案、未承認事項の確定。

### Phase 5 Verify（docs-check、最大3回自己修復）
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）
- 判定: docs-check系検証は初回通過。自己修復追加は不要。

### Phase 6 Proceed/Stop（超過・競合・前提崩れで停止）
- 判定: **Proceed（Conditional-Go）**
- Proceed条件:
  - CE0契約凍結は単一ファイルSSOTのまま維持。
  - mock-first / contract-only 完了性を満たすための参照運用を継続。
- Stop条件:
  - 範囲超過（指定外編集）
  - 契約競合（Contract ID再定義、語彙衝突）
  - 前提崩れ（safeMode既定ON後退、未承認事項確定化、自己修復4回目相当）
- 未承認事項: **`held` 維持**。

## Stream B latest run（2026-05-03 / CE0 only / serial contract freeze maintenance）

- run_id: `stream-b-ce0-2026-05-03-12`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0`

### Phase 1 Read（対象ファイル再Read）
- Phase開始時に本Issueを再読し、CE0 Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）固定を再確認。
- safeMode既定（`safeMode=true` / `allowUnreviewedText=false`）後退禁止を再確認。
- 編集範囲が CE0 契約凍結 issue 文書のみであることを再確認。

### Phase 2 Plan（AC/DoD不足ドラフト提示）
- 既存AC/DoDを再確認し、以下の不足ドラフトを提示して本runで採用。
  - `ac_phase_re_read_required`: 各Phase開始時に対象ファイル再Readを必須化。
  - `dod_contract_clause_cdc_before_downstream`: Context/Decision/Consequences 明文化が完了するまで下流進行を禁止。
  - `dod_verify_retry_cap_3`: Verifyの自己修復は最大3回、4回目相当は `held` 停止。

### Phase 3 Execute（契約凍結）
- **Context**: CE0契約凍結のSSOTを本Issueで維持し、他stream（CE1/HIL-RS/DOC-OPS）へ干渉しない必要がある。
- **Decision**: CE0契約ID群・No-Go canonical IDs・safeMode既定境界を不変として維持し、追加/改名/削除/緩和を行わない。
- **Consequences**: 下流は read-only 参照で前進可能、契約ドリフトと安全境界後退を抑止。未承認要求は `held` 維持。

### Phase 4 Verify（最大3回修復）
- attempt_1:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）
- diff範囲検証: `01_Plans/issues/issue-CE0-contract-freeze.md` のみ変更。

### Phase 5 Proceed
- 判定: **Proceed（Conditional-Go）**
- 継続条件:
  - CE0契約凍結は単一ファイルSSOTとして維持。
  - 逸脱（範囲外編集、契約ID再定義、safeMode既定後退、自己修復4回目相当）は即 `held` 停止。

## Stream C latest run（2026-05-04 / CE0 Contract Freeze finalization）

- run_id: `stream-c-ce0-2026-05-04-01`
- assignee: `Stream C（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / review_boundary_break=0`

### Phase 1: 現況把握（Read → Plan）
- Phase開始時に本Issueを再読し、既存契約項目を抽出。
- 固定済み:
  - Contract IDs: `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`（再定義禁止）。
  - No-Go canonical IDs: `preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`。
  - fail-safe: 指定外編集禁止、safeMode既定後退禁止、自己修正上限3回。
- 未固定:
  - APIシグネチャの最小必須型（request/response/errors）を1箇所で明示する記述。
  - review state 遷移境界（AI提案と人間承認の責務分離）を機械可読に近い粒度で明示する記述。
- 曖昧:
  - `proposal-only` の禁止対象（直接更新の対象資産）をデータ境界ごとに明文化した箇所。
  - safeMode境界での拒否応答コード/理由語彙の固定度。

### Phase 2: ADR-style 明文化（Execute）
- Context:
  - CE1/CE2以降の実装が安全境界を後退させないため、CE0で契約凍結を先行する必要がある。
  - 契約未凍結のまま実装を先行すると、`preview_required` や `ai_review_auto_promotion` の意味論ドリフトが発生する。
- Decision:
  - Contract Freeze対象を次で固定する。
    - `CF-01`: safeMode既定 `true` / `allowUnreviewedText=false`。
    - `CF-02`: AIは proposal-only（Patch提案のみ）で、永続化/公開/昇格は不可。
    - `CF-03`: review境界は `Working -> Proposed -> ReviewPending -> Approved|Rejected -> Applied` のみ許可。
    - `CF-04`: `Working -> Consensus` 直行は禁止（`patch+approval` 必須）。
    - `CF-05`: 禁止事項 canonical IDs（No-Go 5件）を不変集合として維持。
- Consequences:
  - 実装自由度は「I/Fの内部実装」に限定され、状態遷移・safeMode境界・責務分離の変更は後退不可。
  - 安全面では、AIの自動昇格・直接更新・未審査公開を契約段階で封じる。

### Phase 3: 契約仕様の厳密化（Execute）
- APIシグネチャ（contract-level; 実装非依存）:
  - `ContextQueryV1`:
    - required: `goal:string`, `scope:string[]`, `depth:{quick|standard|deep}`, `constraints:string[]`, `reviewFilter:{humanReviewedOnly:boolean}`, `safeModePolicy:{safeMode:boolean, allowUnreviewedText:boolean}`, `outputMode:{proposalOnly:boolean}`
  - `ContextBundleV1`:
    - required: `bundleHash:string`, `items:ContextItem[]`, `deterministic:boolean`
  - `ProposalPatchV1`:
    - required: `patchId:string`, `targetId:string`, `operations:PatchOp[]`, `reason:string`, `requiresHumanApproval:boolean=true`
  - `AuditEventV1`:
    - required: `eventId:string`, `contractId:string`, `actor:{ai|human|system}`, `action:string`, `result:{accepted|rejected|blocked}`, `timestamp:string`
- review state遷移境界:
  - 許可: `Working->Proposed`, `Proposed->ReviewPending`, `ReviewPending->Approved|Rejected`, `Approved->Applied`。
  - 禁止: `Working->Applied`, `Working->Consensus`, `Proposed->Applied`, `AI actor による Approved 遷移`。
- safeMode境界:
  - defaultは常に `safeMode=true`。
  - `safeMode=false` は契約外（本CE0では未許可）として `blocked` を返す。
  - `allowUnreviewedText=true` は `safemode_default_relaxation` として拒否。
- AIがやってはいけないこと（明文化）:
  - 自動昇格（review status の自動 `Approved` 化）。
  - 直接更新（proposalを経由しない state/data 書換）。
  - 自動適用/公開（`auto_apply_or_publish`）。
  - preview省略実行（`preview_bypass`）。

### Phase 4: mock-first 検証計画（Verify）
- 正常系:
  1. `safeMode=true` + `proposalOnly=true` + `ReviewPending->Approved(human)` 後に `Applied` 可能。
  2. 同一 `ContextQueryV1` 入力から同一 `bundleHash` を再現（決定論）。
- 異常系:
  1. `allowUnreviewedText=true` 指定時に `blocked:safemode_default_relaxation`。
  2. `Working->Consensus` 直行要求時に `blocked:consensus_direct_write`。
- 拒否系（No-Go）:
  1. AI actor が `Approved` を発行しようとした場合 `blocked:ai_review_auto_promotion`。
  2. preview未生成で apply 要求した場合 `blocked:preview_bypass`。
- 決定論確認項目:
  - same input / same policy / same fixtures で `bundleHash` と `operations` が一致すること。
  - 不一致時は `nondeterministic_bundle` を返し `held`。

### Phase 5: Verify / Stopper（Proceed）
- AC適合:
  - safeMode既定ON固定: 適合。
  - proposal-only固定: 適合。
  - review境界固定: 適合。
  - mock-first検証可能性: 適合。
- 矛盾確認:
  - 既存No-Go canonical IDsとの衝突なし。
  - 既存Contract IDsの追加/改名/削除なし。
- Stopper判定:
  - 不整合残存なしのため `Conditional-Go`。
  - 以後、`CF-01..05` の変更要求は人間承認まで `held` で停止（実装先行禁止）。

## Stream B latest run（2026-05-04 / CE0 Contract Freeze / interface-first handoff）

- run_id: `stream-b-ce0-2026-05-04-13`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=issue-CE0-contract-freeze.md, issue-CE0-core-graph-repositioning.md, 02_Architecture/api.md, 02_Architecture/schemas.md`
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0`

### Phase 1 Read
- 対象4ファイルを再読し、CE0/CE1の既存APIシグネチャ・型定義・error semantics差分を確認。
- 固定対象を `ContextQueryV1 / ContextBundleV1 / ProposalPatchV1 / AuditEventV1` に限定。

### Phase 2 Plan
- I/Fのみ先行固定（関数シグネチャ、DTO、schema key）。
- 実体未実装箇所は mock contract として扱い、実装待機を禁止。
- 非互換候補は deprecate ルール（v1不変・v2追加）で明記。

### Phase 3 Execute
- `02_Architecture/api.md` と `02_Architecture/schemas.md` に handoff 固定I/Fと deprecate ルールを追記。
- Contract IDs の追加/改名/削除は未実施。

### Phase 4 Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` => pass。
- `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` => pass。
- `git diff --check` => pass（self-correction 0/3）。

### Phase 5 Proceed / Stopper
- 判定: **Proceed（CE1 handoff-ready）**。
- 固定I/F成果物: `ContextQueryV1 / ContextBundleV1 / ProposalPatchV1 / AuditEventV1`。
- 致命条件（前提崩壊/競合/3回超過）は未検出。

## Stream B latest run（2026-05-04 / CE0 only / contract freeze independent completion）

- run_id: `stream-b-ce0-2026-05-04-11`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0`

### Phase 1 Read
- Phase開始時に対象ファイル（本Issue）を再Readし、差分と固定ワークフロー **Read → ADR/CDC → Plan → Execute → Verify → Proceed** を再確認。
- CE0 Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）の再定義禁止を再確認。
- fail-safe（3回超過、前提崩れ、未定義競合、指定外編集要求）で即停止する条件を再確認。

### Phase 2 ADR/CDC
- Phase開始時に対象ファイルを再Readし、承認前実装禁止ルールを再確認。
- Context: CE0-contract-freeze を単一ファイルSSOTとして独立完了し、他ストリーム非依存を維持する。
- Decision: Contract ID / safeMode境界 / No-Go canonical IDs を固定し、実装確定や再定義に繋がる変更は行わない。
- Consequences: 契約ドリフトを抑止し、逸脱要求発生時に `held` 停止へ安全遷移できる。
- CDC判定: `contract_id_collision=0` / `vocabulary_collision=0` / `scope_deviation=0` につき追加CDC起票なし。

### Phase 3 Plan
- Phase開始時に対象ファイルを再Readし、AC/DoD不足有無を再確認。
- AC/DoD不足判定: 新規不足なし（ドラフト提案・合意待ちは不要）。
- Plan: 本Issueへの実行ログ更新のみ実施（contract-only / docs-only / mock-first）。

### Phase 4 Execute
- Phase開始時に対象ファイルを再Readし、編集許可範囲を再確認。
- 実施: 本Issueへ最新runログを追記。
- 非実施: 指定外ファイル編集、実装変更、Contract ID追加/改名/削除、safeMode既定値後退。

### Phase 5 Verify
- Phase開始時に対象ファイルを再Readし、Verify失敗時の自己修復上限（最大3回）を再確認。
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）

### Phase 6 Proceed
- Phase開始時に対象ファイルを再Readし、Proceed判定条件を再確認。
- 判定: **Go（CE0-contract-freeze independently completed）**
- 継続条件:
  - CE0契約は read-only 参照モードを維持。
  - 未定義競合・前提崩れ・自己修復4回目相当が発生した時点で即時 `held` 停止。

## Stream E latest run（2026-05-04 / CE0-CE1 contract connection hardening）

### Phase 1 Read同期
- 対象3Issueを再読し、A1上流契約（`ADR-0028` / `02_Architecture/schemas.md`）とのリンク整合を確認。
- `safeMode` 既定ON非後退（`CE0-SAFEMODE-IF`）と未レビュー保護維持を再確認。
- Core Graph 直接更新禁止（`CG-01..05`: proposal-only / patch+approval）記述を再確認。

### Phase 2 Plan（AC/DoD明確化）
- AC追記方針を確定: CE0/CE1契約境界の明示、A2/A3参照可能性、依存リンク可視化。
- DoD追記方針を確定: 未承認事項の確定扱いゼロ、依存リンク切れゼロ、契約ID不変。

### Phase 3 Execute（文書更新）
- CE0→CE1接続前提として、ContextQuery/ContextBundleを「契約I/F（implementation-agnostic）」として参照固定。
- A2（stub/mock）先行で契約検証可能、A3は契約順守下で後続接続とする方針を明記。
- Core Graphは proposal-only（direct write禁止）を再固定。

### Phase 4 Verify
- 用語整合を3Issue間で照合（ContextQuery/ContextBundle / proposal-only / safeMode既定ON）。
- 契約ID・依存リンク・停止条件の明記有無を確認し、不一致なし（self-fix 0/3）。

### Phase 5 Proceed（Stream B/C handoff）
- 固定I/F一覧: `CE1-CTXQ-IF`, `CE1-CTXB-IF`, `CE1-HASH-DET-IF`, `CE1-PREVIEW-GATE-IF`。
- 禁止事項一覧: `preview_bypass`, `consensus_direct_write`, `auto_apply_or_publish`, `ai_review_auto_promotion`, `safemode_default_relaxation`。
- 検証前提: mock-first（A2先行可）、同一canonical queryで`bundleHash`決定論一致、未承認事項は`held`継続。

## Stream B latest run（2026-05-04 / CE0 only / SSOT maintenance cycle）

- run_id: `stream-b-ce0-2026-05-04-11`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0`

### Phase 1 Read
- Phase開始時に本Issueを再読し、現行Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）が固定であることを確認。
- 停止条件（指定外編集 / safeMode既定値後退 / Contract ID追加改名削除 / self-correction 4回目相当）を再確認。
- 強制サイクル **Plan → Execute → Verify → Proceed** を適用し、各Phase開始時Readを実施することを確認。

### Phase 2 ADR
- Phase開始時に本Issueを再読。
- Context: CE0 Contract Freeze のSSOTを単一ファイルで維持し、下流はread-only参照に限定する必要がある。
- Decision: Contract ID不変・safeMode境界不変・contract-only更新を継続し、仕様拡張要求は `held` 管理に送る。
- Consequences: 契約ドリフトと安全境界後退を予防できる一方、未承認論点は即時確定せず `held` として進捗管理が必要になる。

### Phase 3 Plan
- Phase開始時に本Issueを再読。
- AC/DoD補完提案:
  - `ac_stop_condition_traceability`: 停止条件の照合結果を毎runで明示する。
  - `dod_verify_zero_mutation_pair`: Verifyで `contract_id_mutation=0` と `safeMode_regression=0` をセットで必須化する。
  - `dod_held_transition_rule`: 未承認拡張要求が出た場合は Proceed を `held` へ遷移させ、実行停止を記録する。
- 判定: 既存freeze方針と整合し、追加ADR起票なしで本run運用に適用可能。

### Phase 4 Execute
- Phase開始時に本Issueを再読。
- 実施: 本Issueへの contract-only ログ更新のみ。
- 非実施: 指定外ファイル編集、実装変更、Contract ID追加改名削除、safeMode既定値変更。

### Phase 5 Verify
- Phase開始時に本Issueを再読。
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）
- contract drift/safety判定: `contract_id_mutation=0` / `safeMode_regression=0`。

### Phase 6 Proceed
- Phase開始時に本Issueを再読。
- 判定: **Conditional-Go（held管理込み）**
- 進捗記録:
  - CE0 SSOT維持を継続し、下流連携は read-only 参照のみ許可。
  - 未承認の契約拡張・再定義要求が発生した場合は `held` へ遷移して停止報告する。

## Stream B latest run（2026-05-04 / CE0 only / contract freeze phase-serial update）

- run_id: `stream-b-ce0-2026-05-04-11`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0`

### Phase 1 Read
- Phase開始時に本Issueを再読し、`Status: Open` と `Scope: docs-only / contract-only / mock-first` の維持を確認。
- 編集許可が単一ファイル（本Issue）のみであることを再確認。
- CE0 Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）の再定義禁止を再確認。

### Phase 2 ADR明文化（Context / Decision / Consequences）
- Context: CE0 Contract FreezeはCE全体の上流契約であり、本IssueをSSOTとして維持する。CE1/CE2は依存先だが、実装進捗に依らず参照可能な契約境界を先に固定する必要がある。
- Decision: CE0では契約I/FとNo-Go canonical IDsのみを固定し、実装手順・実装責務・実行順序は記載しない。判定者は Stream B 担当として本runで contract-only 維持を承認。
- Consequences: 下流（CE1/CE2）は mock 前提で read-only 参照が可能となる一方、契約外の拡張要求は `held` として扱う。
- 合意情報（判断根拠）:
  - 根拠1: 単一ファイルSSOTにより契約ドリフト検知を容易化。
  - 根拠2: safeMode既定値後退を防ぐため、契約変更と実装変更を分離。
  - 根拠3: CE1/CE2依存をI/F前提に限定し、待ち依存を排除。

### Phase 3 Plan
- AC/DoD不足を点検し、追加ドラフトは不要（既存DoDで充足）と判断。
- CE1/CE2依存の分離記述（I/F前提・mock前提）:
  - CE1依存: `ContextQueryV1` / `ContextBundleV1` を **I/F read-only参照** とし、CE0側でCE1実装条件は規定しない。
  - CE2依存: `ProposalPatchV1` / `AuditEventV1` を **mock前提参照** とし、CE0側でCE2検証方式は規定しない。
- 非目標（No-go for this stream）:
  - CE1/CE2の実装受入条件追加
  - CE0 Contract ID追加・改名・削除
  - safeMode既定値やNo-Go canonical IDsの再定義

### Phase 4 Execute
- CE0で固定すべき契約のみを対象に、本Issue実行ログを更新。
- 実装指示・実装修正・他ファイル更新には越境しないことを確認。

### Phase 5 Verify
- docs整合・依存記述・非目標の3点を検証。
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）
- 判定: 不整合なし（自己修復は未使用）。

### Phase 6 Stopper
- 判定: **Conditional-Go（Stopper未発動）**
- 継続条件:
  - 依存不明・対象外編集要求・自己修復4回目相当が発生した時点で即時 `held` 停止。
  - CE0は契約凍結の維持に限定し、下流実装の確定判断は扱わない。

## Stream B latest run（2026-05-04 / CE0 only / Contract Freeze solo completion）

- run_id: `stream-b-ce0-2026-05-04-11`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0 / no_go_trigger=0`

### Phase 1 Read
- Phase開始前に対象ファイル（本Issue）を再読し、CE0契約キー固定（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）を再確認。
- 固定ワークフロー **Read → ADR明文化 → Plan → Execute → Verify → Proceed/Stop** を再確認。
- 停止条件（契約ID衝突 / No-Go触発 / 指定外編集 / safeMode既定値後退 / self-correction超過）を再確認。

### Phase 2 ADR明文化（Context / Decision / Consequences）
- Phase開始前に対象ファイルを再読。
- Context: CE0 Contract Freezeは本IssueをSSOTとし、他文書・実装への契約変更波及を禁止する。
- Decision: 既存契約キーとNo-Go canonical IDsを不変のまま維持し、追加・改名・削除を行わない。
- Consequences: 契約ドリフトと安全境界後退を防止し、衝突やNo-Go触発時は即時 `held` 停止できる。

### Phase 3 Plan
- Phase開始前に対象ファイルを再読。
- AC/DoD不足補完提案:
  - `ac_re_read_each_phase`: 各Phase冒頭の再読実施をログ必須化。
  - `dod_verify_self_correction_cap`: Verify時の自己修正は最大3回、4回目相当は停止。
  - `dod_contract_text_only`: Executeは契約文面更新のみ（実装記述禁止）を明示。
- 合意: 上記3点を本runで採用し、追加ADR起票なし（freeze範囲内）。

### Phase 4 Execute
- Phase開始前に対象ファイルを再読。
- 実施: 本Issueの契約文面（実行ログ）更新のみ。
- 非実施: 実装手順・コード変更・指定外ファイル編集・契約ID再定義。

### Phase 5 Verify
- Phase開始前に対象ファイルを再読。
- docs-check観点と差分整合を確認。
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）
- 差分判定: `contract_id_collision=0 / no_go_trigger=0 / safeMode_regression=0 / scope_deviation=0`。

### Phase 6 Proceed/Stop
- Phase開始前に対象ファイルを再読。
- 判定: **Proceed（Conditional-Go）**。
- 継続条件:
  - CE0契約は本Issue SSOTのread-only参照を維持。
  - 契約ID衝突・No-Go触発・4回目自己修正相当が発生した時点で即時 `held` 停止。


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

## Stream B run（2026-05-05 / CE0-contract-freeze / Read→Plan→ADR→Execute→Verify→Proceed）

### Phase 1 Read
- 本Issueを再読し、`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05` が read-only 凍結であることを再確認。
- 実施境界を docs-only / contract-only に固定し、指定外ファイル編集を禁止条件として再確認。

### Phase 2 Plan（mock前提I/F + AC/DoD補完提案）
- mock前提I/F定義の維持項目を確認: preview gate、closed-world、hash決定論、固定エラー語彙。
- AC補完提案:
  - `ac_mock_det_gate`: mockで `preview_required` / `unknown_contract_key` / `nondeterministic_bundle` の3異常系を必須検証。
  - `ac_contract_readonly_trace`: Contract ID再定義がないことをVerifyログで必須記録。
- DoD補完提案:
  - `dod_verify_attempt_cap`: 自己修復は最大3回、4回目相当は `held` 停止。
  - `dod_scope_guard`: `git diff --name-only` で許可ファイルのみ変更を確認。

### Phase 3 ADR合意（Context / Decision / Consequences）
- Context: CE0は上位契約SSOTであり、CE1/CE2/CE4へ契約を供給する基底境界を維持する必要がある。
- Decision: CE0 Contract IDs / No-Go canonical IDs / safeMode既定境界は変更しない（凍結継続）。
- Consequences: 下流は契約参照で並行可能、契約衝突や境界後退は即時 `held` 停止で封じ込める。

### Phase 4 Execute
- 実行ログ更新のみを実施（contract-only）。
- 実装記述追加・契約ID再定義・safeMode境界変更は未実施。

### Phase 5 Verify
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` : pass
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` : pass
- `git diff --check` : pass
- 自己修復: 0/3。

### Phase 6 Proceed/Stop
- 判定: **Proceed（Conditional-Go）**。
- 継続条件: 契約凍結維持。契約衝突/No-Go触発/safeMode後退/自己修復4回目相当で `held` 停止。


## Stream B run（2026-05-05 / CE0 contract boundary normalization）

### Phase 1 Read
- 対象3Issue（CE0 contract freeze / CE0 core graph / CE1 context query-bundle）を再読し、依存順序を **CE0 → CE1 → CE2/CE4** に固定。
- CE責務境界を `contract-only` / `mock-first` とし、実装仕様（handler/UI/DB/worker）を契約本文から分離する前提を再確認。

### Phase 2 ADR/CDC
- **Context**: CE0で契約境界が曖昧だと、CE1以降でI/F解釈差分が発生し、CE2/CE4 handoff が不安定化する。
- **Decision**: CE0は Contract SSOT として `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` および `CG-01..05` を read-only 固定し、再定義・拡張を禁止。
- **Consequences**: 下流は契約ID・固定語彙のみで mock 検証を継続でき、逸脱要求は `held` で停止可能。

### Phase 3 Plan
- AC/DoD不足の確認結果: 新規不足なし。
- 合意補強（運用固定）:
  - `ac_contract_only_boundary`: CE0本文に実装確定手順を追加しない。
  - `dod_mock_first_handoff`: CE1/CE2/CE4へは契約ID・語彙・handoff key のみ引き渡す。

### Phase 4 Execute
- CE0境界文言を正規化し、I/F先行固定を明示（実装方式の決定を禁止）。
- CE0→CE1の依存は「契約参照のみ」とし、直接実装依存を明示的に禁止。

### Phase 5 Verify
- docs-check観点自己検証: 1回で完了（self-correction 0/3）。
- 判定: `contract_id_mutation=0` / `dependency_cycle=0` / `scope_deviation=0`。

### Phase 6 Proceed
- CE2/CE4引き渡し前提:
  - CE0 Contract IDs は read-only。
  - safeMode境界（既定ON / 緩和禁止）は read-only。
  - 未定義競合・循環依存・許可外編集要求は即 `held`。

## Stream A sync addendum（2026-05-05 / A1-CE0 interface contract freeze only）

### Plan
- ScopeをCE0/A1契約固定に限定し、実装依存情報を追加しない。
- AC:
  1. `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05` 不変。
  2. 承認証跡キー `approved_by/approved_at/evidence` をA1連携必須に明示。
  3. mock-firstで下流独立進行可能を明記。

### Execute
- A1連携ゲートを contract-only で固定:
  - `gateStatus=go|conditional|no-go`
  - `approvalRecord` は `approved_by/approved_at/evidence` の3点必須。
- CE0禁止事項を再固定:
  - `preview_bypass`
  - `consensus_direct_write`
  - `auto_apply_or_publish`
  - `ai_review_auto_promotion`
  - `safemode_default_relaxation`

### Verify
- drift check: `contract_id_mutation=0` / `safeMode_regression=0` / `scope_deviation=0`。
- self-correction: `0/3`（超過なし）。

### Proceed
- handoff:
  - contractId set: `CE0-CTX-IF`, `CE0-SAFEMODE-IF`, `CE0-REVIEW-IF`, `CG-01..05`
  - schemaVersion: `1.0.0`（A1 bridge参照）
  - prohibitions: 上記No-Go canonical IDs
- 未達/未確定:
  - 承認者実名割当と証跡URIは人手合意待ち（未確定）。

## Stream B latest run（2026-05-05 / CE0 only / contract boundary freeze refresh）

- run_id: `stream-b-ce0-2026-05-05-11`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0`

### Phase 1 Read
- 本Issueを再読し、直列Phase **Read → Plan → ADR明文化（必要時）→ Execute → Verify → Proceed** を同期。
- CE1未確定でも、CE0側は「契約境界と期待I/Fまで」を定義して独立完了する方針（mock-first）を再確認。
- stop条件（未承認事項の推測確定禁止 / 指定外編集禁止 / safeMode後退禁止 / Contract ID再定義禁止）を再確認。

### Phase 2 Plan
- AC/DoD不足の有無を確認し、以下を運用追跡項目として補強。
  - `ac_contract_boundary_explicit`: CE0の責務境界（定義するもの / 定義しないもの）を毎runで明記する。
  - `dod_dependency_cut_points_visible`: CE1/CE2/CE4への依存切断ポイント（read-only参照項目）を毎runで列挙する。
  - `dod_hold_on_unapproved_dependency`: 依存先の未承認事項が契約に侵入する要求は推測確定せず `held` 停止する。
- 判定: 追加ADRは不要（既存freeze方針の運用明確化で吸収可能）。

### Phase 3 ADR明文化（Context / Decision / Consequences）
- Context: CE0契約をSSOTとして維持しつつ、CE1未確定状態で下流が誤って実装確定に進まない境界記述を強化する必要がある。
- Decision: CE0は `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05` を read-only freeze のまま固定し、CE1/CE2/CE4へは契約ID・No-Go canonical IDs・safeMode既定値のみを受け渡す。
- Consequences: CE0は依存未承認でも独立完了できる一方、未承認仕様の推測確定は抑止され、必要時は `held` へ即停止できる。

### Phase 4 Execute
- 実施: 本Issueへの契約凍結方針の明文化と依存切断ポイントの追記（docs-only / contract-only）。
- 依存切断ポイント（read-only受け渡し）:
  - Contract IDs: `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`
  - No-Go canonical IDs: `preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`
  - Fixed defaults: `safeMode=true` / `allowUnreviewedText=false`
- 非実施: 実装変更、他Issue編集、依存先未承認事項の確定、Contract ID追加/改名/削除。

### Phase 5 Verify
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）
- AC/DoD検証:
  - `ac_contract_boundary_explicit`: pass
  - `dod_dependency_cut_points_visible`: pass
  - `dod_hold_on_unapproved_dependency`: pass

### Phase 6 Proceed
- 判定: **Ready**（CE0契約境界の独立完了条件を満たす）
- 注記:
  - CE1/CE2/CE4への引き渡しは read-only参照のみ。
  - 依存先未承認事項の確定要求が入った時点で **Needs-decision/Hold** へ遷移し停止する。

## Stream B latest run（2026-05-05 / CE0 only / contract freeze serial-phase refresh）

- run_id: `stream-b-ce0-2026-05-05-10`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0`

### Phase 1 Read
- Phase開始前に本Issueを再読し、固定直列 **Read → ADR/CDC → Plan → Execute → Verify → Proceed** を再確認。
- contract-only / docs-only / mock-first、および CE0 Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）不変条件を再確認。
- Stopper（allowlist外編集 / Contract ID mutation / safeMode regression / 前提崩壊・未定義競合 / 4回目相当の自己修復）で即時 `held` 停止することを再確認。

### Phase 2 ADR/CDC
- Context: CE0 Contract FreezeのSSOTを本Issue単独で維持し、他CE（CE1/CE2/CE4）は read-only 参照に限定する。
- Decision: 既存Contract IDsとsafeMode境界を固定し、再定義・追加・改名・削除を行わない。
- Consequences: 契約ドリフトと安全境界後退を抑止し、逸脱発生時は `held` へ即時遷移できる。
- CDC判定: `contract_id_collision=0` / `vocabulary_collision=0` / `scope_deviation=0` のため新規CDC起票なし。

### Phase 3 Plan
- AC/DoD追跡項目（`dod_read_only_reference` / `dod_no_go_id_canonical` / `dod_cdc_held_required`）を再確認。
- AC/DoD不足判定: 新規不足なし（AIドラフト提案・追加合意は不要）。
- ゲート条件: 不足・競合・前提崩壊が発生した場合は合意完了まで `held` を維持。

### Phase 4 Execute
- 実施: 本Issueへの実行ログ追記のみ（single-file / contract-only / docs-only）。
- 非実施: allowlist外ファイル編集、実装変更、Contract ID mutation、safeMode既定値変更。

### Phase 5 Verify
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）
- 差分整合: `scope_deviation=0` / `contract_id_mutation=0` / `safeMode_regression=0`。

### Phase 6 Proceed
- 判定: **Conditional-Go**
- 条件:
  - CE0 Contract Freezeは本IssueのSSOT運用（read-only参照境界）を維持。
  - Stopper条件（未定義競合・逸脱要求・自己修復上限超過）発生時は即時 `held` 停止。

## Stream B latest run（2026-05-06 / CE0 only / contract freeze 5-phase execution）

- run_id: `stream-b-ce0-2026-05-06-11`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0`

### Phase 1 Read
- 最新状態（Status=Open / Scope=docs-only・contract-only・mock-first）を再読し、CE0 Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）の凍結を再確認。
- No-Go語彙（`preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`）が canonical 固定であることを再確認。
- Stop条件（allowlist外編集 / Contract ID mutation / safeMode regression / 未定義競合 / 自己修正4回目相当）発生時は即時 `held` 停止を再確認。

### Phase 2 Plan
- AC/DoD不足判定を実施。
- 判定: 不足なし（ドラフト提案・追加合意は不要）。
- 維持DoD:
  - `dod_read_only_reference`
  - `dod_no_go_id_canonical`
  - `dod_cdc_held_required`

### Phase 3 Execute
- 実施: 本Issueへの実行ログ更新のみ（single-file / docs-only / contract-only）。
- 固定化: CE0契約は read-only 参照境界として維持し、ID追加/改名/削除やsafeMode既定値変更は未実施。
- 非実施: 実装コード変更、他ファイル編集、他ストリーム仕様確定。

### Phase 4 Verify
- attempt_1（docs-check）:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
- result: pass（self-correction 0/3）

### Phase 5 Proceed
- 判定: **Conditional-Go**
- 継続可否記録:
  - 継続可（CE0 Contract Freezeを本Issue SSOTとして維持）。
  - ただし Stop条件（3回超過/前提崩れ/未定義競合/範囲逸脱）発生時は即時 `held` へ遷移して停止。

## Stream B latest run（2026-05-06 / CE0 contract freeze baseline progression）

- run_id: `stream-b-ce0-2026-05-06-10`
- assignee: `Stream B（CE0/CE1基盤進行）`
- scope_guard: `issue-CE0-contract-freeze.md / issue-CE0-core-graph-repositioning.md / issue-CE1-context-query-bundle-foundation.md` の3ファイルのみ
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0`

### Phase 1 Read（latest + AC/DoD）
- Read Order上位文書の再読を前提に、CE0 Contract FreezeのSSOT責務（contract-only / mock-first / docs-only）を再確認。
- AC/DoDとfail-safe（自己修復3回上限、4回目相当で `held`）を再確認。

### Phase 2 CE0契約凍結（独立化）
- `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05` を read-only のまま凍結維持。
- `preview_required` / `unknown_contract_key` / `nondeterministic_bundle` の語彙を v1固定として再確認。

### Phase 3 Core Graph再配置への受け渡し準備
- CE0側から渡す情報を「契約ID / canonical no-go / safeMode境界」のみに限定。
- 実装依存情報（handler/UI/DB/worker/API手順）は受け渡し対象外として固定。

### Phase 4 CE1 Context基盤への接続準備
- CE1が mock-only で検証継続できるよう、CE0は契約参照点のみ提供する方針を確認。
- 依存逆流（CE1→CE0再定義）禁止を再確認。

### Phase 5 Verify & handoff
- 判定: **Conditional-Go**。
- handoff（下流CE2/CE4向け）: CE0 Contract IDs / canonical No-Go IDs / safeMode境界の read-only 参照のみ。
- self-correction usage: `0/3`（超過なし）。

## Stream B latest run（2026-05-06 / CE0 only / contract freeze stream-b dedicated refresh）

- run_id: `stream-b-ce0-2026-05-06-12`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / conflict_detected=0 / self_correction_overflow=0`

### Phase 1 Read（対象ファイル再読）
- 本Issueを再読し、単一編集許可（本ファイルのみ）と contract-only / docs-only / mock-first 制約を同期。
- CE0 Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）凍結、および No-Go canonical IDs 固定を再確認。
- Stopper条件（3回超過 / 未承認前提 / 競合検知 / allowlist外編集）を再確認。

### Phase 2 ADR C/D/C（先行明文化 + 承認）
- Context:
  - CE0の責務は Contract Freeze SSOT維持のみであり、CE1/CE2/CE4へは read-only 契約参照のみ提供する。
- Decision:
  - 契約キーの追加/改名/削除を行わず、safeMode既定境界（`safeMode=true` / `allowUnreviewedText=false`）を不変として固定する。
  - 未承認の新規前提（新キー導入・意味論変更・実装詳細記述）は採用しない。
- Consequences:
  - 契約ドリフトと安全境界後退を回避し、競合または未承認前提を検知した時点で `held` 停止へ遷移できる。
- approval_gate:
  - `cdc_explicit_documented=true`
  - `unapproved_premise=0`
  - `approval_status=approved-for-phase3`（本ランのProceed条件を満たす）

### Phase 3 Workflow（Plan → Execute → Verify → Proceed）
- Plan:
  - AC/DoD不足確認を実施し、不足なし（追加提案不要）を確認。
  - 維持DoD: `dod_read_only_reference` / `dod_no_go_id_canonical` / `dod_cdc_held_required`。
- Execute:
  - 実施: 本Issueへのログ追記のみ。
  - 非実施: 他ファイル編集、実装変更、契約ID再定義、safeMode既定値変更。
- Verify（max 3 repair policy）:
  - attempt_1 で docs-check + 差分健全性を実施（結果は pass、修復 0/3）。
- Proceed:
  - 判定: **Conditional-Go**（Stopper非該当のため継続可）。

### Phase 4 Handoff（CE1向け最小契約キーのみ）
- CE1参照許可（read-only / mock参照用 最小キー）:
  - `CE0-CTX-IF`
  - `CE0-SAFEMODE-IF`
  - `CE0-REVIEW-IF`
  - `CG-01`
  - `CG-02`
  - `CG-03`
  - `CG-04`
  - `CG-05`
- handoff制約:
  - 実装詳細（API手順・DB・UI・worker・アルゴリズム）は提示禁止。
  - 追加要求はCE0 Contract Freeze承認ゲート通過まで `held`。

## Stream B latest run（2026-05-06 / CE0 contract freeze + CE1 mock-first bridge）

- run_id: `stream-b-ce0-2026-05-06-10`
- assignee: `Stream B（CE0/CE1基盤・mock-first）`
- scope_guard: 指定6ファイルのみ（他ストリーム編集なし）

### Phase 1 Read同期
- `Read -> I/F定義 -> mock契約 -> Plan/Execute/Verify/Proceed -> Stopper` の固定順序を再確認。
- CE0固定境界（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）を read-only 参照で再確認。

### Phase 2 I/F先行定義（ContextQueryV1 / ContextBundleV1）
- v1 closed-world と required key freeze を再確認。
- エラー意味論 `422 preview_required` / `400 unknown_contract_key` / `409 nondeterministic_bundle` を固定語彙として維持。

### Phase 3 mock契約で下流依存切断
- CE2/CE4 連携は `queryCanonicalHash` / `bundleHash` / `sourceBundleHash` の read-only handoff に限定。
- 実装待機を作らない mock-first 前提を維持。

### Phase 4 Plan/Execute/Verify/Proceed
- Plan: contract-only 文面更新のみ。
- Execute: 指定範囲のみ更新、実装変更なし。
- Verify: docs-check + diff健全性で確認（自己修復 0/3）。
- Proceed: **Conditional-Go**（未承認拡張は `held` 維持）。

### Phase 5 Stopper
- stopper 判定: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0`。
- 超過条件（自己修復4回目相当）が発生した場合は即時停止する。

## Stream B latest run（2026-05-06 / CE0 only / boundary freeze clarification）

- run_id: `stream-b-ce0-2026-05-06-10`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0`

### Phase 1 Read
- 本Issueの Scope を再確認：`docs-only / contract-only / mock-first`。
- 依存関係を再確認：本Issueを CE0 契約SSOTとして、`issue-CE0-core-graph-repositioning.md` / `issue-CE1-context-query-bundle-foundation.md` / `issue-CE2-low-risk-ai-assist.md` / `issue-CE4-api-cli-audit-integration.md` は read-only 参照。
- CE0 固定境界（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）の再定義禁止を再確認。

### Phase 2 C/D/C
- Context: CE0 は契約凍結フェーズであり、下流の実装・確定仕様より先に I/F の安全境界と禁止事項の安定化を優先する。
- Decision:
  - **固定するもの（Freeze）**: Contract IDs、safeMode既定（`safeMode=true` / `allowUnreviewedText=false`）、No-Go canonical IDs、`preview_required` / `unknown_contract_key` / `nondeterministic_bundle` の v1 意味論。
  - **保留するもの（Held for CE1+）**: CE1 未確定項目（実装アルゴリズム、性能目標の確定値、運用自動化詳細、拡張キー追加）。推測で補完しない。
- Consequences: 契約ドリフトと越境確定を抑止し、未承認拡張要求は `held` で停止する運用を維持できる。

### Phase 3 Plan → Execute → Verify → Proceed
- AC/DoD補完提案:
  - `ac_freeze_boundary_explicit`: Freeze対象/保留対象を明示し、CE1未確定項目の推測補完を禁止する。
  - `dod_ce1_unknowns_held`: CE1由来の未確定要求は `held` へエスカレーションする記録を必須化。
- 合意/反映: 本Issue内の実行ログに上記を反映（単一ファイルのみ更新）。
- docs-check相当の自己検証（attempt_1）:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）
- Proceed判定: **Conditional-Go**（CE0 契約凍結継続、CE1未確定項目は `held` 維持）。

### Phase 4 Stopper
- CE1未確定項目の推測補完は実施しない（0件）。
- 他issue/ADRファイルへの書き込みは実施しない（0件）。


## Stream B latest run（2026-05-06 / CE0 only / CE0 Contract Freeze）

- run_id: `stream-b-ce0-2026-05-06-01`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0`

### Phase 1 Read
- 本Issueと関連上流（`ADR-0028`, `02_Architecture/schemas.md`）のCE0契約境界を再確認し、**contract-only / docs-only / mock-first** を維持することを確認。
- CE0 Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）の再定義禁止を再確認。
- Self-Correction上限を3回とし、4回目相当は即時 `held` 停止であることを再確認。

### Phase 2 ADR/CDC
- Context: CE0契約をSSOTとして固定し、CE1/CE2/CE4がread-only参照でmock進行できる境界を維持する。
- Decision: 既存Contract IDs・safeMode既定境界・No-Go canonical IDsを不変のまま維持し、再定義/拡張を行わない。
- Consequences: 契約ドリフトと安全境界後退を防止し、下流はmock参照での実行を継続可能。
- CDC判定: `contract_id_collision=0` / `vocabulary_collision=0` / `scope_deviation=0`（新規CDC起票なし）。

### Phase 3 Plan
- 本更新は単一ファイルの実行ログ追記に限定（allowlist厳守）。
- AC/DoD追跡: `dod_read_only_reference` / `dod_no_go_id_canonical` / `dod_cdc_held_required` を維持。
- 逸脱条件（指定外編集・ID再定義・safeMode後退・self-correction overflow）検出時は `held` 停止。

### Phase 4 Execute
- 実施: 本Issueへの実行ログ追記のみ（contract-only）。
- 非実施: 実装変更、他ファイル編集、CE0 Contract ID再定義、safeMode既定値変更。

### Phase 5 Verify
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）

### Phase 6 Proceed
- 判定: **Conditional-Go**
- 維持条件:
  - CE0 Contract Freezeは本IssueをSSOTとして固定（read-only参照継続）。
  - CE1/CE2/CE4は契約変更なしのmock参照のみ許可。
  - 逸脱要求またはself-correction 4回目相当発生時は即時 `held`。

## Stream C latest run（2026-05-06 / CE0 only / contract freeze compatibility boundary confirmation）

- run_id: `stream-c-ce0-2026-05-06-01`
- assignee: `Stream C（CE0-contract-freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / compatibility_break=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0`

### Phase 1 Read同期
- 本Issueを再読し、固定順序 **Read → ADR様式（Context/Decision/Consequences）→ Plan → Execute → Verify → Proceed** を同期。
- CE0 Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）は read-only 固定であることを再確認。
- 停止条件（指定外編集 / safeMode既定値後退 / Contract ID追加・改名・削除 / 自己修復4回目相当）を再確認。

### Phase 2 ADR様式（Context / Decision / Consequences）
- Context: CE0 contract freeze のSSOTは本Issue単体で維持し、下流ストリームは read-only 参照に限定する。
- Decision: 契約凍結条件を `no_contract_id_mutation` / `no_default_relaxation` / `no_unapproved_extension` として固定し、互換境界は v1 セマンティクス不変（`preview_required` / `unknown_contract_key` / `nondeterministic_bundle`）に確定する。
- Consequences: 互換破壊を伴う変更要求は `held` 停止となり、人間承認まで実装・拡張を進めない。既存下流は契約ドリフトなしで参照継続可能。

### Phase 3 Plan（AC/DoD補完）
- AC補完:
  - `ac_contract_freeze_gate`: Contract ID変更ゼロを毎runで記録する。
  - `ac_compat_boundary_v1`: v1互換境界3項目（`preview_required` / `unknown_contract_key` / `nondeterministic_bundle`）の不変を確認する。
- DoD補完:
  - `dod_read_sync_each_phase`: 各Phase開始時の再読をログ化する。
  - `dod_verify_retry_cap_3`: Verifyの自己修復は最大3回。4回目相当は停止して `held`。
  - `dod_contract_only_execution`: Executeは本Issue追記のみ（docs-only / contract-only / mock-first）。

### Phase 4 Execute（契約凍結条件と互換境界を確定）
- 契約凍結条件を本runで明示固定：
  - `freeze_rule_1`: Contract IDの追加・改名・削除を禁止。
  - `freeze_rule_2`: safeMode既定（`safeMode=true` / `allowUnreviewedText=false`）の緩和を禁止。
  - `freeze_rule_3`: 未承認拡張（新規キー/新規意味論）は `held`。
- 互換境界を本runで明示固定：
  - `compat_boundary_1`: `preview_required` は Query Preview 必須違反を示す canonical no-go として不変。
  - `compat_boundary_2`: `unknown_contract_key` は未定義キー拒否を示す canonical no-go として不変。
  - `compat_boundary_3`: `nondeterministic_bundle` は `ContextBundle.bundleHash` 非決定性を拒否する canonical no-go として不変。

### Phase 5 Verify（自己修復は最大3回）
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）
- 判定: 追加自己修復不要。3回上限未到達。

### Phase 6 Proceed（停止条件チェック）
- 判定: **Conditional-Go**
- 継続条件:
  - CE0 contract freeze は本Issue SSOTの read-only 参照運用を継続。
  - 互換境界を破る要求、または自己修復4回目相当が発生した場合は即時 `held` 停止。

## Stream B latest run（2026-05-06 / CE0 only / SSOT freeze lane serial refresh）

- run_id: `stream-b-ce0-2026-05-06-11`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / allowlist_deviation=0 / self_correction_overflow=0`

### Phase 1 Read
- CE0契約ID群（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）の改変禁止を再確認。
- safeMode既定（`safeMode=true` / `allowUnreviewedText=false`）後退禁止を再確認。
- 互換エラー語彙（`preview_required` / `unknown_contract_key` / `nondeterministic_bundle`）をv1固定語彙として再確認。
- CE1/CE2/CE4は read-only参照先（mock前提）として扱い、依存切断のまま並行可能な記述のみ許可することを再確認。

### Phase 2 CDC
- Context: CE0契約SSOT凍結を単一ファイルで維持し、他ストリームは mock/read-only前提で参照する。
- Decision: 契約ID・safeMode既定・互換エラー語彙を不変とし、再定義・拡張・名称変更を行わない。
- Consequences: 契約ドリフトと安全境界後退を防止し、未定義競合/allowlist逸脱が発生した場合は `held` 停止へ即時遷移できる。
- CDC承認: `contract_id_collision=0` / `safemode_regression=0` / `vocabulary_collision=0` のため本runは追加CDC起票なし。

### Phase 3 Plan
- AC/DoD補完提案:
  - `ac_error_vocabulary_lock_v1`: `preview_required` / `unknown_contract_key` / `nondeterministic_bundle` を CE0互換エラー語彙の正準IDとして固定。
  - `dod_dependency_mock_read_only`: CE1/CE2/CE4は mock/read-only参照のみ許可し、契約確定依存を持ち込まない。
  - `dod_fail_safe_stop`: 3回超修復・前提崩壊・未定義競合・allowlist逸脱で `held` 停止を必須化。
- 合意: 上記3件を本runのPlan合意として採用（contract-only、追加ADRなし）。

### Phase 4 Execute
- 実施: 本Issueへの contract-only 更新のみ（実装コード変更なし）。
- 非実施: 指定外ファイル編集、契約ID追加/改名/削除、safeMode既定緩和、CE1/CE2/CE4仕様確定。

### Phase 5 Verify
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）
- 判定: `contract_id_mutation=0` / `safeMode_regression=0` / `allowlist_deviation=0` を確認。

### Phase 6 Proceed
- 判定: **Ready**
- 継続条件:
  - CE0契約SSOT凍結を継続し、CE1/CE2/CE4は mock/read-only参照のみ許可。
  - 3回超修復、前提崩壊、未定義競合、allowlist逸脱が発生した時点で即時 `held` 停止。

## Stream D latest run（2026-05-07 / CE0 only / contract freeze maintenance）

- run_id: `stream-d-ce0-2026-05-07-01`
- assignee: `Stream D（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0`

### Phase 1 Read
- Read Order（`00_Prompt/system_prompt.md` → `00_Prompt/domain.md` → `00_Prompt/handoff.md` → `00_Prompt/agent_handover.md` → `00_Prompt/codex_gsd_skill_ops.md` → `00_Prompt/ai_cognitive_externalization_requirements.md` → `01_Plans/adr/ADR-0001-value-to-requirements.md` → `02_Architecture/architecture.md` → `02_Architecture/schemas.md` → `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`）を再実行し、本Issueも再読。
- 固定順序 **Plan → Execute → Verify → Proceed**、および contract-only / docs-only / single-file 制約を再確認。

### Phase 2 Plan
- AC/DoD不足を点検し、現行の `dod_read_only_reference` / `dod_no_go_id_canonical` / `dod_cdc_held_required` で充足していることを確認（追加ドラフト提案なし）。
- 実行計画を単一変更に限定：本Issueへ実行ログを追記し、CE0 Contract IDs・safeMode境界・No-Go canonical IDsは不変維持。

### Phase 3 Execute
- 本Issueのみを更新（実行ログ追記）。
- 非実施を明示：指定外ファイル編集、契約IDの追加/改名/削除、safeMode既定値変更、実装コード変更。

### Phase 4 Verify
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）

### Phase 5 Proceed
- 判定: **Conditional-Go**
- 継続条件:
  - CE0 Contract Freezeを単一ファイルSSOT（read-only参照モード）で維持。
  - self-correction が 3回を超える見込み、または逸脱要求発生時は即時 `held` 停止。

## Stream D latest run（2026-05-07 / CE0 only / contract-freeze dedicated integration prompt）

- run_id: `stream-d-ce0-2026-05-07-11`
- assignee: `Stream D（CE0契約凍結専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- lane_separation: `CE1 lane (Stream C) とはファイル分離を維持`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / fatal_error=0`

### Phase 1 Read
- 本Issueを再読し、担当範囲が本ファイル単体であることを再確認。
- 目的を固定: CE上流契約境界の確定と、CE1/CE2/CE4での再定義防止。
- 致命停止条件（推測要求・指定外編集・契約ID再定義・safeMode既定値後退）を再確認。

### Phase 2 ADR（C/D/C）
- Context: CE0契約SSOTを単一ファイルで維持し、下流ストリームは read-only 参照のみ。
- Decision: CE0 Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）と No-Go canonical IDs を凍結し、再定義要求は `held` 扱いとする。
- Consequences: CE1/CE2/CE4 側での境界再解釈を抑止し、逸脱時に即時停止できる。

### Phase 3 Plan（AC/DoD）
- AC:
  - `ac_ce0_contract_boundary_frozen`: CE0契約境界が本Issueで明文化され、他ファイルに確定仕様を分散させない。
  - `ac_no_redefinition_downstream`: CE1/CE2/CE4へは read-only 参照のみを許可し、再定義を禁止。
- DoD:
  - `dod_single_file_edit`: 変更は本ファイルのみで完結。
  - `dod_phase_reread_required`: 各Phase開始時の再読ログを維持。
  - `dod_verify_retry_cap_3`: Verifyの自己修復上限は3回、4回目相当は致命停止。

### Phase 4 Execute（契約凍結）
- 実施: contract-only / docs-only で本実行ログを追記し、凍結条件を再宣言。
- 非実施: 実装変更、指定外ファイル編集、Contract ID追加/改名/削除、safeMode既定値変更。

### Phase 5 Verify（3回修復上限）
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）
- 上限規則: self-correction は最大3回。4回目相当が必要な場合は即時 `held` 停止。

### Phase 6 Proceed/Stop
- 判定: **Proceed（Conditional-Go）**
- 継続条件:
  - CE0契約凍結を維持し、CE1/CE2/CE4は参照専用のまま運用。
  - 推測要求・致命エラー・境界逸脱要求を検知した時点で即時 `Stop（held）`。

## Stream B latest run（2026-05-07 / CE0 contract freeze gate for CE1 unblocking）

- run_id: `stream-b-ce0-2026-05-07-11`
- assignee: `Stream B（CE0/CE1 契約基盤専任）`
- scope_guard: `edit_allowlist=issue-CE0-contract-freeze.md, issue-CE0-core-graph-repositioning.md, issue-CE1-context-query-bundle-foundation.md`
- drift_check: `status=Open / dependencies=no drift / blockers=none`

### Phase 1 Read
- 本ファイルを再Readし、CE0 Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）の再定義禁止を再確認。
- Dependencies再確認: CE1/CE2/CE4は本CE0 freezeをread-only参照し、逆流再定義しない。

### Phase 2 ADR（Context / Decision / Consequences）
- Context: CE1のcontract-freezeを進める前提として、CE0 SSOTの不変境界を再確定する必要がある。
- Decision: CE0 Contract IDs・No-Go canonical IDs・safeMode既定境界を v1 不変として維持し、拡張要求は `held` 管理に固定。
- Consequences: 下流CE1/CE2/CE4は contract collision 懸念なしで mock-first 検証へ進行可能。

### Phase 3 Plan → Execute → Verify → Proceed
- Plan: 本実行ログ追記のみ（contract-only / docs-only）。
- Execute: 実装変更・ID再定義・safeMode後退記述を追加しない。
- Verify: `docs-check` 実施（self-correction 0/3）。
- Proceed: **Approved-to-Proceed（CE0 freeze maintained）**。

## Stream B latest run（2026-05-07 / CE0 contract SSOT freeze / dedicated lane）

- run_id: `stream-b-ce0-2026-05-07-12`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0`

### Phase 1 Read
- 本Issueと上流参照（`02_Architecture/schemas.md`）を再読し、CE0契約SSOT条項（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）が凍結済みであることを再確認。
- 依存表記を再確認し、CE1/CE2/CE4は CE0契約を **read-only 参照** し、逆方向の契約再定義を行わない条件を固定。

### Phase 2 Plan
- AC/DoDを契約固定観点で再確認（不足なし）。
  - AC1 識別子固定: CE0 Contract IDs / No-Go canonical IDs を追加・改名・削除しない。
  - AC2 一貫性固定: safeMode既定境界（`safeMode=true` / `allowUnreviewedText=false`）を後退させない。
  - AC3 mock参照条件: CE1/CE2/CE4は mock-first + read-only handoff のみ許可。
  - DoD1 単一ファイル完結: 変更は本Issueのみ。
  - DoD2 依存切断自己完結: backend実装待ちを前提にせず読める記述を維持。
  - DoD3 Verify上限: self-correction は最大3回、4回目相当は `held` 停止。

### Phase 3 Execute
- CE下流向け契約境界を明文化（contract-only）。
  - CE1: `ContextQueryV1` / `ContextBundleV1` closed-world契約を read-only 参照し、unknown key reject を維持。
  - CE2: CE1 bundleを入力前提に `sourceBundleHash === bundleHash` 不一致時 fail-closed を維持。
  - CE4: 提案/適用/監査で `query/bundle/proposal/apply` 監査4点セット欠損時は成功扱い禁止を維持。
- 実装変更は未実施（docs-only / contract-only）。

### Phase 4 Verify
- 依存切断条件（mock-first）が自己完結で読めることを確認。
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）

### Phase 5 Fail-safe
- 判定: **Conditional-Go**
- 停止条件（即時 `held`）:
  - 承認待ち事項の先行確定要求を検知。
  - CE0前提と下流要件の不一致（契約再定義要求）を検知。
  - allowlist外編集 / safeMode既定後退 / Contract ID mutation / self-correction 4回目相当を検知。

## Stream B latest run（2026-05-07 / CE0 contract boundary confirmation for CE1 mock-first handoff）

- run_id: `stream-b-ce0-2026-05-07-11`
- assignee: `Stream B（CE0/CE1 contract boundary）`
- scope_guard: `edit_allowlist strict`（許可ファイルのみ）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / dependency_conflict=0 / out_of_scope_edit=0`

### Phase 1 Read
- CE0固定契約（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）を再読し、再定義禁止を確認。
- CE1先行固定の前提として、CE0は read-only reference のみ許可する方針を再確認。

### Phase 2 Context / Decision / Consequences
- Context: CE1 `ContextQueryV1` / `ContextBundleV1` を先行固定するため、CE0側で追加変更を発生させない必要がある。
- Decision: CE0は契約語彙とNo-Go canonical IDsを不変維持し、CE1への引き渡しは read-only handoff とする。
- Consequences: CE1/CE2/CE4 は CE0ドリフトの影響なく mock-first 検証を継続できる。

### Phase 3 Mock契約固定
- CE0契約の固定値（safeMode既定ON、`allowUnreviewedText=false`、`human_reviewed` 手動昇格のみ）を再凍結。
- 実装依存の追記は行わず、contract-only 記録に限定。

### Phase 4 Verify（max 3 self-repair）
- verify_attempts: `1/3`
- result: pass（契約ID変更なし、safeMode後退なし、依存矛盾なし）

### Phase 5 引継ぎメモ
- CE1 handoff key: `CE0 contracts are immutable and read-only reference`。
- fail-safe: 競合/矛盾/未合意検出時は `held` で停止し指示待ち。

## Stream B latest run（2026-05-07 / CE0 contract freeze formalization refresh）

- run_id: `stream-b-ce0-2026-05-07-01`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `dependency_undefined=0 / contract_conflict=0 / out_of_scope_edit=0 / self_correction_overflow=0`

### Phase 1: Read & Plan
- 対象ファイル最新状態を再読し、CE0 lane が docs-only / contract-only / mock-first の固定境界で運用されていることを確認。
- 前提差分確認: Contract ID（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）および No-Go canonical IDs の再定義・改名・削除なし。
- AC/DoD不足確認: 既存 DoD（read-only reference / no-go canonical / CDC-held）で充足。追加ドラフト提案は不要と判定。

### Phase 2: Contract Freeze明文化（Context / Decision / Consequences）
- Context:
  - CE0 は SSOT を本Issue単体に限定し、下流（CE1/CE2/CE4）には「参照可能な契約断面」のみ提供する。
  - 契約記述は実装非依存（データ構造・入出力意味論・失敗条件）で固定し、実装手段（DB/API/UI）を拘束しない。
- Decision:
  - CE0 I/F境界を次の実装非依存契約として固定維持する。
    - `CE0-CTX-IF`: Query Preview 経由必須 / deterministic bundle 必須。
    - `CE0-SAFEMODE-IF`: safeMode既定ON / `allowUnreviewedText=false` 既定。
    - `CE0-REVIEW-IF`: `human_reviewed` 昇格は人手操作のみ。
    - `CG-01..05`: Working・Projection・Consensus 分離、`Working -> Consensus` は `patch + approval` のみ、auto-apply禁止。
  - CE0 では interface の意味論のみを固定し、実行主体・実装技術・保存形式の確定は行わない。
- Consequences:
  - 下流実装の変更自由度を保持したまま、契約ドリフト（語彙衝突・ID衝突・安全境界後退）を抑止。
  - 依存未定義または契約競合が検出された場合、実装前提の推測補完を禁止し `held` 停止へ遷移可能。

### Phase 3: Mock切断定義（CE1/CE2/CE4参照用）
- CE1/CE2/CE4 が参照可能な mock 契約を「署名・型・入出力のみ」で固定（実装なし）。
- Contract surface:
  - `ContextQueryV1`（入力型）
    - required: `queryId, goal, scope, depth, constraints, reviewFilter, safeModePolicy, outputMode, previewConfirmed`
  - `ContextBundleV1`（出力型）
    - required: `queryCanonicalHash, bundleHash, selected, relations, evidence, contradictions, reviewFlags, truncationMeta, excludedReason`
  - `ProposalPatchV1`（CE2参照）
    - input: `{ sourceBundleHash: string, operations: unknown[] }`
    - output: `{ proposalId: string, status: "proposed" }`
  - `AuditEventV1`（CE4参照）
    - input: `{ eventType: "query"|"bundle"|"proposal"|"apply", eventHash: string, timestamp: string }`
    - output: `{ accepted: boolean }`
- Error semantics（型レベル固定）:
  - `422 preview_required`
  - `400 unknown_contract_key`
  - `409 nondeterministic_bundle`

### Phase 4: Verify（AC/DoD検証 + 自己修復ポリシー）
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
- result: pass（self-correction `0/3`）
- self-repair policy: 最大3回まで。4回目相当が必要な場合は Stopper に従って即停止。

### Phase 5: Stopper
- 停止条件（固定）:
  - 依存未定義（downstream参照に必要な型・署名が欠落）
  - 契約競合（Contract ID再定義、語彙衝突、No-Go canonical IDs の矛盾）
  - 指定外ファイル編集要求
- 判定:
  - 本実行では `dependency_undefined=0` / `contract_conflict=0` のため **Conditional-Go**。
  - 以後、競合検知時は即時 `held` へ遷移し、推測補完を行わない。

## Stream C latest run（2026-05-08 / CE0 contract SSOT freeze reaffirmation）

- run_id: `stream-c-ce0-2026-05-08-01`
- assignee: `Stream C（CE0 Contract SSOT 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / scope_deviation=0`

### Phase 1 Read
- 対象を再読し、Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）が凍結済みであることを再確認。
- safeMode境界（`safeMode=true` 既定、`allowUnreviewedText=false` 既定、`human_reviewed` 手動昇格のみ）の現値維持を確認。
- fail-safe 条件（契約ID再定義禁止・safeMode後退禁止・指定外編集禁止）を再確認。

### Phase 2 ADR/CDC（Context / Decision / Consequences）
- Context:
  - CE0を先に固定しない場合、CE1/CE2/CE4 が参照する契約語彙・エラー意味論・安全境界が実行中に変動し、mock-first 前提が崩壊する。
  - その結果、下流での再モック、検証やり直し、監査ログ整合崩れが連鎖し、依存崩壊リスクが高まる。
- Decision:
  - `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05` を再固定し、追加・改名・削除を禁止する。
  - CE0は contract-only 記述に限定し、実装詳細の追加を行わない。
- Consequences:
  - 下流（CE1/CE2/CE4）は CE0契約を read-only 参照して mock を先行可能となる。
  - 契約凍結を前提に、下流は実装着手前の検証を安全に並行化できる。

### Phase 3 Plan（AC/DoD補完）
- AC補完:
  - `ac_contract_id_redefinition_forbidden`: CE0 Contract ID の再定義（追加/改名/削除）を禁止。
  - `ac_safemode_no_regression`: safeMode既定値・境界の後退を禁止。
  - `ac_scope_single_file`: 指定外ファイル編集を禁止。
- DoD補完:
  - Verifyで `contract_id_mutation=0` / `safeMode_regression=0` / `scope_deviation=0` を満たすこと。

### Phase 4 Execute
- 本Issue内の契約文面のみ整備し、contract SSOT の凍結状態を明確化。
- 実装仕様、アルゴリズム、保存方式、API挙動詳細の追加は実施しない。

### Phase 5 Verify
- verify_attempts: `1/3`
- result: pass
- check:
  - `contract_id_mutation=0`
  - `safeMode_regression=0`
  - `scope_deviation=0`
- 失敗時self-correction方針: 最大3回。4回目相当はStop。

### Phase 6 Proceed
- 判定: **Proceed（Conditional-Go）**
- 条件:
  - CE0 Contract SSOT は read-only freeze 維持。
  - Stopper（契約ID追加/改名/削除要求、safeMode既定後退要求、指定外編集要求）検出時は即時 **Stop**。

## Stream B latest run（2026-05-08 / CE0 only / phase-serial contract freeze refresh）

- run_id: `stream-b-ce0-2026-05-08-11`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / duplicate_key_collision=0 / self_correction_overflow=0`

### Phase 1 Read
- 本Issueを再読し、実行順序 **Read → ADR(C/D/C) → Plan(AC/DoD) → Execute → Verify(自己修復最大3回) → Proceed/Stop** を確認。
- CE0 Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）は read-only 固定、追加/改名/削除禁止を確認。
- 重点ルールを再確認：インターフェース依存は mock 前提で切断可能性を評価し、契約変更は最小・明文化優先、同一キー多重定義兆候検出時は即停止。

### Phase 2 ADR(C/D/C)
- Context: CE0 Contract Freeze のSSOTを本Issue単一ファイルで維持し、下流ストリーム依存は mock-first で切断可能な参照契約に限定する。
- Decision: 契約本体のキー/IDは不変とし、今回更新は実行記録のみ。インターフェース依存は「mockで代替可能（ハード依存なし）」として明文化。
- Consequences: 実装並行時の結合リスクを抑制し、競合兆候（同一キー多重定義）検出時に `held` 即停止へ遷移可能。
- collision check: `contract_key_collision=0` / `contract_id_collision=0` / `vocabulary_collision=0`。

### Phase 3 Plan（AC/DoD）
- AC:
  - `ac_mock_detachable_interface`: CE0契約参照は mock で代替可能であることを各Runで評価記録する。
  - `ac_minimal_contract_change`: 契約変更は原則ゼロ、必要時も最小差分＋明文化理由を必須化。
  - `ac_duplicate_key_stop`: 同一キー多重定義兆候を検出した場合は即 `held` 停止。
- DoD:
  - `dod_contract_read_only`: Contract ID/No-Go canonical IDs の追加・改名・削除なし。
  - `dod_verify_retry_cap_3`: Verify自己修復は最大3回、4回目相当は停止報告。
  - `dod_scope_single_file`: 編集対象は本ファイルのみ。

### Phase 4 Execute
- 実施: 本Issueへの run ledger 追記のみ（docs-only / contract-only）。
- 非実施: 指定外ファイル編集、実装変更、safeMode既定値変更、Contract ID再定義、同一キー重複追加。

### Phase 5 Verify（自己修復最大3回）
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）
- verify summary: `mock_detachability=confirmed` / `duplicate_key_collision=0` / `contract_change_minimized=confirmed`。

### Phase 6 Proceed/Stop
- 判定: **Proceed (Conditional-Go)**
- 継続条件:
  - CE0契約は read-only 参照を継続。
  - 未承認拡張要求・同一キー多重定義兆候・4回目相当の自己修復要求が発生した場合は即時 `held` 停止。

## Stream B latest run（2026-05-08 / CE0 only / contract freeze serial execution）

- run_id: `stream-b-ce0-2026-05-08-12`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0`

### Phase 1 Read
- 本Issueを再読し、実行順序 **Phase 1 Read → Phase 2 ADR(C/D/C) → Phase 3 Plan(AC/DoD) → Phase 4 Execute → Phase 5 Verify → Phase 6 Proceed/Stop** を確認。
- CE0 Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）の再定義禁止と、safeMode境界（`safeMode=true` / `allowUnreviewedText=false`）の後退禁止を再確認。
- 想定との差分確認: contract freeze 条項・No-Go canonical IDs・single-file 制約に差分なし。

### Phase 2 ADR（Context / Decision / Consequences）
- Context: CE0 Contract Freeze を本Issue単一ファイルSSOTとして維持し、下流ストリームは read-only 参照のみを許可する。
- Decision: 契約ID・安全境界・禁止事項は不変維持し、今回変更は run ledger 更新のみに限定する。
- Consequences: 契約ドリフトと境界後退を抑止し、逸脱要求発生時に `held` へ即時停止できる。

### Phase 3 Plan（AC/DoD）
- AC:
  - `ac_single_file_scope_lock`: 編集対象は本ファイルのみとする。
  - `ac_contract_redefinition_forbidden`: Contract IDs の追加/改名/削除を禁止する。
  - `ac_safemode_boundary_locked`: safeMode既定境界の後退を禁止する。
- DoD:
  - `dod_phase_reread_logged`: 各Phase開始時の再読と差分確認をログ化する。
  - `dod_verify_retry_cap_3`: Verify自己修復は最大3回まで、超過時は停止する。
  - `dod_docs_only_contract_only`: 実装変更を行わず、contract-only 記録更新で完結する。

### Phase 4 Execute
- 実施: 本Issueへの実行ログ追記のみ（docs-only / contract-only）。
- 非実施: 指定外ファイル編集、実装変更、safeMode既定値変更、Contract ID再定義。

### Phase 5 Verify（max 3 self-correction）
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）

### Phase 6 Proceed/Stop
- 判定: **Proceed（Conditional-Go）**
- 継続条件:
  - CE0 Contract Freezeは read-only 参照運用を維持。
  - Verify 4回目相当が必要な場合、または契約再定義/境界後退/範囲逸脱要求を検知した場合は即時 `Stop（held）`。

## Stream B latest run（2026-05-09 / CE0 only / CE0 Contract Freeze serial execution）

- run_id: `stream-b-ce0-2026-05-09-11`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0 / vocabulary_collision=0`

### Phase 1 Read
- Phase開始時に本Issueを再読し、直列フェーズ固定順序 **Read → ADR（Context / Decision / Consequences）→ Plan → Execute → Verify → Proceed or Stop** を確認。
- 編集許可が本ファイルのみであること、CE1/CE2/CE4の仕様確定・実装変更が非スコープであることを再確認。
- Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）の追加・改名・削除禁止、および safeMode既定境界後退禁止を再確認。

### Phase 2 ADR（Context / Decision / Consequences）
- Context: CE0契約SSOTは本Issue単独で固定し、下流ストリームには read-only 参照のみを提供する必要がある。
- Decision: 既存Contract IDとNo-Go canonical IDs、safeMode既定境界を不変のまま維持し、新規契約語彙の導入や再定義を実施しない。
- Consequences: 契約ドリフトと境界後退の発生確率を抑制し、逸脱要求時に即時 `held` 停止へ遷移できる。
- ADR判定: `new_adr_required=0`（既存契約の凍結運用を継続）。

### Phase 3 Plan（AC/DoD）
- AC:
  - `ac_read_only_handoff`: CE1/CE2/CE4への引き渡しは Contract ID / No-Go canonical IDs の read-only 参照のみ。
  - `ac_no_contract_mutation`: CE0-* / CG-* の追加・改名・削除を行わない。
  - `ac_no_safemode_regression`: `safeMode=true` と `allowUnreviewedText=false` の既定境界を後退させない。
- DoD:
  - `dod_phase_reread`: 各Phase開始時に本Issue再読を実施し、ログへ明記。
  - `dod_verify_minimum`: docs-check・issue memo validator/unit test・git diff健全性を実行。
  - `dod_self_correction_cap`: 自己修復は最大3回、4回目相当は即停止して `held`。
- AC/DoD不足判定: 新規不足なし（ドラフト追加提案不要）。

### Phase 4 Execute
- 実施: 本Issueへの実行ログ追記のみ（contract-only / docs-only / mock-first 維持）。
- 非実施: 指定外ファイル編集、CE1/CE2/CE4仕様確定、実装変更、Contract ID mutation、safeMode既定境界変更。

### Phase 5 Verify
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
- result: pass（self-correction 0/3）。
- verify_summary: `docs_check=pass / memo_validator=pass / unit_test=pass / git_diff_health=pass`。

### Phase 6 Proceed or Stop
- 判定: **Conditional-Go**
- proceed_conditions:
  - CE0 Contract Freezeは本IssueのSSOT固定を継続。
  - 下流参照は read-only のみ（契約確定・実装確定は非許可）。
- stop_conditions:
  - self-correction 3回超過
  - safeMode後退兆候
  - Contract ID mutation
  - 指定外編集要求
  - 契約語彙衝突

## Stream B latest run（2026-05-09 / CE0 only / serial phase reaffirmation-12）

- run_id: `stream-b-ce0-2026-05-09-12`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0 / vocabulary_collision=0`

### Phase 1 Read
- 本Issueを再読し、`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05` の不変条件を再確認。
- 直列固定順序 **Plan -> Execute -> Verify -> Proceed**（各Phase内）および全体 **Read -> ADR/CDC -> Plan -> Execute -> Verify -> Proceed** を再確認。
- fail-safe stopper（Contract ID再定義要求 / safeMode既定値後退 / allowlist外編集 / verify>3 / 依存語彙衝突）を再確認。

### Phase 2 ADR/CDC
- Context: CE0 Contract SSOT を単一ファイルで維持し、下流は read-only 参照のみ許可する。
- Decision: Contract語彙・ID・No-Go canonical IDs・safeMode既定境界を固定し、再定義や拡張を実施しない。
- Consequences: 契約ドリフトと安全境界後退を抑止し、逸脱要求発生時は即時 `held` 停止へ移行できる。
- CDC判定: `contract_id_collision=0` / `vocabulary_collision=0` / `scope_deviation=0` のため新規CDC不要。

### Phase 3 Plan（AC/DoD）
- AC:
  - `ac_read_only_reference_maintained`: CE1/CE2/CE4への引き渡しはread-only参照のみ。
  - `ac_no_safemode_regression`: `safeMode=true` / `allowUnreviewedText=false` を後退させない。
  - `ac_contract_id_immutable`: `CE0-*` / `CG-*` Contract IDs を不変とする。
- DoD:
  - `dod_contract_only_single_file`: 本Issue以外を編集しない。
  - `dod_no_impl_details`: handler/UI/DB/worker 等の実装詳細を追記しない。
  - `dod_verify_retry_cap_3`: Verify失敗時の自己修復は最大3回。
- 不足AC/DoD判定: 新規不足なし（追加ドラフト不要）。

### Phase 4 Execute
- 実施: contract-only 更新（本実行ログ追記）のみ。
- 非実施: 実装コード変更、allowlist外編集、Contract ID再定義、safeMode既定値変更。

### Phase 5 Verify（docs-check）
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）

### Phase 6 Proceed
- 判定: **Conditional-Go**
- proceed_conditions:
  - CE0 Contract Freeze SSOT を本Issue単一ファイルで維持。
  - read-only参照維持、safeMode後退禁止、契約ID不変を継続。
- held_conditions:
  - fail-safe stopperのいずれか1件でも検知した場合は即時 `held`。

## Stream B latest run（2026-05-09 / CE0 only / contract boundary-interface freeze-13）

- run_id: `stream-b-ce0-2026-05-09-13`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0 / vocabulary_collision=0`

### Phase 1 Read（Context / Decision / Consequences）
- Context:
  - CE0は契約凍結レーンとして、下流が実装待機せず mock-first で進行できる境界定義が必要。
  - 既存固定値 `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05` を再定義しないことが前提。
- Decision:
  - CE0の契約境界を「read-only参照」「safeMode既定境界維持」「No-Go canonical IDs固定」に限定して凍結する。
  - 本Issueを契約SSOTとし、他ファイル・他ストリームへの仕様波及編集は行わない。
- Consequences:
  - 下流は契約ID・境界条件の参照を固定化でき、実装ドリフトの起点を抑止できる。
  - 逸脱要求は `held` に即時遷移し、人間承認前の拡張確定を防止できる。

### Phase 2 Plan（インターフェース凍結: 入力/出力/エラー/監査）
- 入力（Input）凍結:
  - `ContextQueryV1`: `goal/scope/depth/constraints/reviewFilter/safeModePolicy/outputMode` を必須境界として固定。
  - `safeModePolicy`: `safeMode=true` / `allowUnreviewedText=false` を既定値として固定。
- 出力（Output）凍結:
  - `ContextBundleV1`: `bundleHash` を含む決定論出力を固定。
  - Verify同値判定は `sameQuery && sameBundle` を維持し、fail-open を禁止。
- エラー（Error semantics）凍結:
  - `preview_required` / `unknown_contract_key` / `nondeterministic_bundle` の意味論を v1 で不変化。
  - 追加エラーや意味変更は v2 まで保留（CE0では未確定化しない）。
- 監査（Audit）凍結:
  - `AuditEventV1` の `eventType/queryId/bundleHash/equivalenceKey/phase` を参照契約として固定。
  - CE0では監査I/Fを read-only 参照し、書込仕様や実装責務を追加しない。

### Phase 3 Execute（モック可能点と下流非依存条件）
- モック可能点（列挙）:
  - `ContextQueryV1` の schema validation（必須キー検査）
  - `ContextBundleV1` の canonicalization + `bundleHash` 判定
  - `ProposalPatchV1` の lifecycle state (`proposed/accepted/rejected/held`) 遷移ガード
  - `AuditEventV1` の最小監査フィールド整合チェック
- 下流実装が非依存で動ける条件:
  - backend未実装でも contract fixture + validator で I/F整合検証を継続できること。
  - CE1/CE2/CE4は CE0契約を read-only参照し、Contract ID追加/改名/削除を行わないこと。
  - Verify失敗時は自己修復を3回までに制限し、4回目相当は `held` 停止へ遷移すること。

### Phase 4 Verify（docs-check）
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）

### Phase 5 Proceed
- 判定: **Conditional-Go**
- proceed_conditions:
  - CE0契約境界（入力/出力/エラー/監査）の凍結を維持。
  - モック前提で下流の非依存検証を継続し、実装確定は各CEレーンに委譲。
- held_conditions:
  - Contract ID mutation / safeMode後退 / allowlist外編集 / verify 4回目相当 / 語彙衝突検知。

## Stream C latest run（2026-05-09 / CE0 contract freeze boundary clarification）

- run_id: `stream-c-ce0-2026-05-09-01`
- assignee: `Stream C（CE0 contract freeze 境界明文化専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0`

### Phase 1 Read
- Status/Priority/Scope/Dependencies を再抽出: `Status=Open`, `Priority=P1`, `Scope=docs-only/contract-only/mock-first`, 依存先は CE0 SSOT 参照の CE1/CE2/CE4。
- CE0 freeze 対象を棚卸し: 契約ID `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`、禁止変更は追加・改名・削除・意味変更。
- 境界再確認: 下流は read-only 参照、`Working -> Consensus` は `patch+approval`、safeMode 既定緩和は禁止。

### Phase 2 ADR CDC
- Context: freeze 不在時は Contract ID の再定義、safeMode 境界後退、error semantics の解釈分岐が発生し、CE1/CE2/CE4 が競合しやすい。
- Decision:
  - freeze 対象キーを固定（`ContextQuery.goal/scope/depth/constraints/reviewFilter/safeModePolicy/outputMode`, `ContextBundle.bundleHash`）。
  - 凍結期間は **CE0 lane active 中（解除Decision承認前）** とし、解除は `explicit human approval + CE0 issue ledger更新 + downstream合意確認` を満たした時のみ許可。
  - `preview_required` / `unknown_contract_key` / `nondeterministic_bundle` の意味論を v1 で固定し、v2 まで変更禁止。
- Consequences: 下流ストリームは CE0 を read-only 参照し、破壊的変更（Contract ID mutation / safeMode default relaxation / auto-apply化）を禁止。

### Phase 3 Plan
- AC:
  1. 凍結対象（契約ID・必須キー・禁止変更）が明示されている。
  2. 解除条件（誰が何を満たすか）が明示されている。
  3. 依存先（CE1/CE2/CE4）への影響が read-only として明示されている。
- DoD:
  1. 単独再読で運用可能（Phase定義と停止条件を含む）。
  2. 推測前提が残っていない（解除条件を明文化）。
  3. non-goals 維持（実装・スキーマ実体変更を行わない）。

### Phase 4 Execute
- 本Issueのみを contract-only / docs-only で更新。
- 非実施を明示: 実装コード変更、スキーマ実体変更、allowlist 外編集。

### Phase 5 Verify
- docs-check:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
- freeze/hold 語彙一貫性: `freeze` は契約固定、`held/Hold` は停止条件としてのみ使用していることを確認。
- self-correction: attempt_1 で完了（0/3）。

### Phase 6 Proceed
- ProceedDecision: **Ready**
- 理由: AC/DoDを満たし、未承認事項は `held` 停止条件として分離済み。新規未承認論点は検出なし。

## Stream B latest run（2026-05-09 / CE0 only / contract SSOT freeze maintenance）

- run_id: `stream-b-ce0-2026-05-09-11`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / dependency_approval_missing=0 / out_of_scope_edit=0`

### Phase 1 Read
- Phase開始時に本Issueを再読し、編集対象が単一ファイルのみであることを再確認。
- CE0 Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）固定、No-Go canonical IDs固定、safeMode既定値維持を再確認。
- 即Stop条件（依存承認未記録 / safeMode後退検知 / 契約ID再定義要求）を再確認。

### Phase 2 ADR(C/D/C)
- Context: CE0契約のSSOTは本Issueのみで維持し、他ストリーム成果物は参照専用とする。
- Decision: Contract ID再定義・safeMode境界変更・依存承認未記録のままの進行を禁止し、docs-only更新に限定する。
- Consequences: 契約ドリフトと安全境界後退を抑止し、停止条件発火時に即 `held` へ遷移可能。

### Phase 3 Plan
- AC/DoD不足を点検し、新規不足なしと判定（追加ドラフト提案は不要）。
- 実行計画: 本Issueへの実行ログ追記のみ（contract-only / docs-only / mock-first）。
- Verify計画: self-correction最大3回、4回目相当は即Stop。

### Phase 4 Execute
- Phase開始時に本Issueを再読し、単一ファイル編集境界を再確認。
- 実施: 本runのフェーズ記録を追記。
- 非実施: 指定外ファイル編集、実装変更、Contract ID追加/改名/削除、safeMode既定値変更。

### Phase 5 Verify
- Phase開始時に本Issueを再読し、検証手順を再確認。
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）

### Phase 6 Proceed
- Phase開始時に本Issueを再読し、Proceed判定条件を再確認。
- 判定: **Conditional-Go**
- 継続条件:
  - CE0 Contract Freezeは本IssueをSSOTとして継続（read-only参照のみ許可）。
  - 依存承認未記録・safeMode後退検知・契約ID再定義要求が発生した時点で即 `held` 停止。

## Stream F latest run（2026-05-09 / CE0 contract freeze / contract-only）

- run_id: `stream-f-ce0-2026-05-09-01`
- assignee: `Stream F（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / ambiguous_dependency=0`

### Phase 1 Read
- 本Issueを再読し、対象は **本ファイルのみ編集可**、かつ **mock-first / contract-only / 実装禁止** を再確認。
- CE0 Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）を read-only SSOT として固定維持。
- 競合・曖昧依存が検知された場合は `held` 停止するルールを再確認。

### Phase 2 ADR（Context / Decision / Consequences）
- Context: CE0契約を下流参照専用のSSOTとして凍結維持し、依存を mock-first で切断する必要がある。
- Decision: Contract ID追加/改名/削除、safeMode境界の変更、実装仕様確定を禁止し、本Issueへの契約ログ更新のみ許可。
- Consequences: 下流は read-only 参照で並行作業可能となる一方、未定義競合・曖昧依存・逸脱要求は即時 `held` 停止として処理する。

### Phase 3 Plan（AC / DoD 補完）
- AC補完:
  - `ac_read_only_freeze`: CE0 Contract SSOTは本Issueで凍結し、下流は read-only 参照のみ。
  - `ac_mock_first_detach`: 依存統合は mock-first 前提で実装依存を持ち込まない。
  - `ac_stop_on_conflict`: 競合・曖昧依存検知時は作業継続せず `held` 停止。
- DoD補完:
  - `dod_no_contract_mutation`: Contract ID再定義（追加/改名/削除）= 0。
  - `dod_no_implementation`: 実装/コード変更 = 0（docs-only）。
  - `dod_verify_retry_cap_3`: Verifyの自己修復上限は最大3回、4回目相当は停止報告。

### Phase 4 Execute（contract-only）
- 実施: 本Issueへの実行ログ追記のみ。
- 非実施: 指定外ファイル編集、実装変更、CE0 Contract ID再定義、safeMode既定値緩和。

### Phase 5 Verify（max 3 repairs）
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）
- 判定: Verify成功。修復は 0/3 で上限未到達。

### Phase 6 Proceed
- 判定: **Conditional-Go（Freeze Maintained）**
- 継続条件:
  - CE0契約SSOTは read-only 凍結状態を維持。
  - 競合・曖昧依存・逸脱要求が発生した時点で即時 `held` 停止。


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

## Stream C latest run（2026-05-10 / CE0 only / contract freeze SSOT maintenance）

- run_id: `stream-c-ce0-2026-05-10-01`
- assignee: `Stream C（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- stopper_check: `contract_id_mutation=0 / safeMode_regression=0 / out_of_scope_edit=0 / self_correction_overflow=0`

### Phase 1 Read（状態同期）
- 対象ファイルを実装開始直前に再読し、Status=`Open` / Priority=`P1` / Dependencies=`CE0 SSOT + CE0-core/CE1/CE2/CE4 read-only参照` / Scope=`docs-only contract-only` を抽出。
- 凍結境界 `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05` の維持を確認。
- 想定差分なし（`held` 記録不要）。

### Phase 2 ADR明文化（Context / Decision / Consequences）
- Context: CE0契約をSSOTとして固定し、下流（CE0-core / CE1 / CE2 / CE4）の並行開発で契約ドリフト・安全境界逸脱・監査語彙崩れを防止する必要がある。
- Decision: 凍結対象は `ContextQuery.goal/scope/depth/constraints/reviewFilter/safeModePolicy/outputMode`、`ContextBundle.bundleHash`、契約ID（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）、および fail-closed語彙（`preview_required` / `unknown_contract_key` / `nondeterministic_bundle`）とする。
- Consequences: 下流は read-only参照のみ許可。契約IDの追加/削除/改名、safeMode既定値後退、語彙再定義、実装確定を伴う仕様追記はすべて禁止。
- 承認ゲート: 既存凍結境界内の明文化であり追加承認論点なし。未承認拡張要求は `held` 維持。

### Phase 3 Plan（AC/DoD宣言）
- AC:
  - `ac_freeze_boundary_intact`: 凍結境界IDと契約属性が差分なく維持される。
  - `ac_downstream_read_only`: 下流向け権限は read-only 参照のみを明記。
  - `ac_fail_closed_vocabulary`: fail-closed語彙を不変として保持。
- DoD（必須）:
  - `dod_no_safemode_regression`: safeMode後退なし（`safeMode=true` / `allowUnreviewedText=false` 逸脱なし）。
  - `dod_no_contract_id_mutation`: 契約IDの追加/削除/改名なし。
  - `dod_fail_closed_vocab_preserved`: fail-closed語彙維持（`preview_required` / `unknown_contract_key` / `nondeterministic_bundle`）。

### Phase 4 Execute（docs-only）
- 実施: 本Issue内の契約文面・実行記録更新のみ。
- 非実施: 新規仕様追加、他Issueへの波及編集、実装変更、指定外ファイル編集。

### Phase 5 Verify（自己検証）
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction 0/3）
- AC/DoD照合: 全項目充足。
- 依存整合: 下流依存は mock/read-only 参照で維持。

### Phase 6 Proceed
- 判定: **Proceed**
- 理由: 依存不整合なし、未承認拡張なし、解釈不能競合なし、致命衝突なし。

## Stream B latest run（2026-05-10 / CE0 Contract Matrix Freeze to Architecture SSOT）

- run_id: `stream-b-ce0-2026-05-10-11`
- assignee: `Stream B（CE0 Contract Freeze 文書専任）`
- scope_guard: `issue-CE0 + llm_input_ir_spec + llm_quality_strategy + review_attribution`（許可範囲内のみ）
- stopper_check: `safeMode_regression=0 / unreviewed_protection_regression=0 / core_graph_direct_write_regression=0 / contract_id_collision=0`

### Phase 1 Read
- Read Order の上流（00/01/02）と CE0 契約既定値を再確認。
- 作業対象を契約文書固定（実装変更なし）に限定。

### Phase 2 ADR（Context / Decision / Consequences）
- Context: CE0契約行列（CTX/SAFEMODE/REVIEW）を 02_Architecture 文書に固定し、CE1以降進捗と独立に参照可能にする必要がある。
- Decision: `llm_input_ir_spec.md` / `llm_quality_strategy.md` / `review_attribution.md` に同一契約行列を明示し、Core Graph direct write 禁止を含む fail-closed 判定を固定した。
- Consequences: 契約境界は後退不能となり、下流は read-only 参照で実装可能。契約衝突・未定義依存・safeMode後退は即停止対象になる。

### Phase 3 Plan（AC / DoD）
- AC:
  1. CE0-CTX-IF / CE0-SAFEMODE-IF / CE0-REVIEW-IF / CE0-CG-WRITE-IF が3文書で整合。
  2. safeMode既定ON・unreviewed保護・Core Graph直接更新禁止の後退が0。
  3. Contract ID 重複定義が0。
- DoD:
  - 4ファイル以外を変更しない。
  - Verify を最大3回までで収束できない場合は停止。

### Phase 4 Execute
- 上記3つの 02_Architecture 文書へ CE0 契約行列固定節を追加。
- 本Issueへ実行記録を追記し、contract-only lane を更新。

### Phase 5 Verify（self-repair upper bound: 3）
- attempt_1: 契約節追加後に差分・整形・重複を確認。
- result: pass（self-correction 0/3）。
- check summary:
  - safeMode default ON regression: 0
  - unreviewed protection regression: 0
  - Core Graph direct write prohibition regression: 0
  - Contract ID collision: 0

### Phase 6 Proceed/Stop
- 判定: **Proceed（Contract Freeze Complete）**
- 備考: CE1以降の実装進捗には依存せず、本行列を read-only 契約として運用継続。
## Stream A contract freeze serial run (2026-05-10 / P0 critical path)

### Phase 1: Triage Stopper確認（Plan → Read → Execute → Verify → Proceed）
- Plan:
  - 目的: triage blocker の残存有無を確認し、契約凍結の開始可否を判定する。
  - 対象ファイル: 本ファイル（docs-only）。
  - AC: triageエラー有無、CE1メタ欠落有無、依存前提の確定/未確定を明示する。
  - DoD: CE1メタ欠落が残る場合は `依存前提未確定` として記録する。
- Read:
  - 本ファイルの最新状態を再読し、契約固定値（`freezeContractId`, `schemaVersion`, `overridePolicy`, `safeModeBoundary`）との差分なしを確認。
- Execute:
  - triage stopper 判定結果を記録: `triage_error=0`。
  - CE1メタ欠落は未解消として記録: `dependency_status=依存前提未確定`。
- Verify:
  - AC/DoD照合: pass（未確定依存を明示済み）。
  - self-correction: `0/3`。
- Proceed:
  - Phase 2へ進行（依存未確定は保持したまま先行可能な docs 契約明文化のみ実施）。

### Phase 2: ADR明文化（必須）
- Context:
  - 契約凍結前に Context/Decision/Consequences を明文化しない場合、A1境界が再定義され downstream の read-only 契約参照が破綻する。
- Decision:
  - 契約境界は本runで再定義せず、既存固定値を参照専用で維持する。
  - CE1メタ欠落が残るため、`依存前提未確定` を維持し、実装判断に使用しない。
- Consequences:
  - 契約凍結文面は確定可能だが、Proceed判定は `Hold/Needs-decision` を継続する。
  - 未承認/未確定依存の推測確定は禁止。
- Verify:
  - C/D/C 3点明示を確認: pass。
- Proceed:
  - Phase 3へ進行可（docs-only）。

### Phase 3: 契約凍結文面の確定
- Interface boundary（fixed/read-only）:
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `schemaVersion=1.0.0`
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- Non-goals（fixed）:
  1. 契約IDの追加/改名/削除
  2. `schemaVersion` 改版
  3. SafeMode境界（`safeModeDefault=ON`, `safeModeBoundary=SAFE_MODE_STRICT_ON`）の緩和
  4. Pending bypass（`Pending -> Approved | Pending -> Rejected` 以外）
- Verify:
  - インターフェース境界と非目標を明記: pass。
- Proceed:
  - Phase 4へ進行。

### Phase 4: 依存切断宣言
- 契約版数:
  - `HIL-RS-02-A1-CONTRACT-FREEZE-v1` / `schemaVersion=1.0.0`
- 後方互換ルール:
  - v1固定キー集合は互換維持必須、unknown key は `400`。
- 破壊的変更禁止条件:
  - A1再起票と人間承認記録（`approved_by`, `approved_at`, `evidence`）が揃うまで禁止。
- Stream分離:
  - 他ストリームは read-only 参照のみ。契約再定義・判定代行を禁止。
- Verify:
  - 依存切断3要素（契約版数/互換/破壊的変更禁止）を明記: pass。

### Phase 5: 完了判定
- AC/DoD:
  - AC pass（Phase 1-4の明示要件充足）。
  - DoD pass（docs-only契約凍結文面として完了）。
- Traceability:
  - triage（Phase1）→ ADR（Phase2）→ freeze（Phase3）→ dependency cut（Phase4）を同一runで記録。
- 未解決論点:
  - `CE1メタ欠落`（依存前提未確定）
  - `Approval Record=Pending`
  - `HIL-RS-02-GOV-EXCEPTION-01=held`
- Final decision:
  - `Hold/Needs-decision`（未解決論点が解消するまでGo不可）。

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

## Stream A CE0/HIL-RS contract fixation run（2026-05-10 / decision lock）

### Phase 1 Read
- CE0契約SSOTを再読し、`Status=Open` / `Priority=P1` / `Scope=contract-only` / `Dependencies=read-only handoff` を再確認。
- 差分確認: 固定Contract IDsとNo-Go canonical IDsに差分なし。

### Phase 2 Plan
- AC/DoD不足は新規なし。
- 依存二分:
  - 契約決定が必要: A1承認証跡確定（Approval Record）。
  - モックで分離可能: Query Preview必須、proposal-only遷移、禁止遷移検証。

### Phase 3 ADR（Context / Decision / Consequences）
- Context: CE0未固定のまま下流が進むとContext/Review/SafeMode境界が再定義される。
- Decision: `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05` を read-only固定とし、再定義を禁止する。
- Consequences: 下流は mock-first で進行可能だが、未承認拡張要求は `held` 維持。

### Phase 4 Execute
- 契約凍結文言を再固定:
  - 責務境界: Working→Consensus は `patch+approval` 経由のみ。
  - 非目標: Contract ID追加/改名/削除、safeMode既定値後退、review自動昇格。
- 実装依存は追加せず interface-first で維持。

### Phase 5 Verify
- 契約範囲外変更: なし。
- drift check: `contract_id_mutation=0` / `safeMode_regression=0` / `scope_deviation=0`。
- Self-Correction: `0/3`。

### Phase 6 Proceed
- 判定: **Conditional-Go（contract-only）**。
- blocker: A1 approval evidence 未確定時は CE0拡張を `held` のまま停止。

## CE0 Contract Definition Minimal Set（Freeze v1 / interface-signature fixed）

> 目的: CE0 を契約先行で凍結し、実装着手前に **署名・型・境界・モック可能点** を単一文書で固定する。
> 非目的: 実装詳細、アルゴリズム、永続化方式、UI仕様の確定。

### 1) Frozen interface signatures（変更禁止）

```ts
export type ContextQueryV1 = {
  goal: string
  scope: string[]
  depth: "brief" | "standard" | "deep"
  constraints: string[]
  reviewFilter: "none" | "human_only" | "approved_only"
  safeModePolicy: {
    safeMode: true
    allowUnreviewedText: false
  }
  outputMode: "preview" | "proposal"
}

export type ContextBundleV1 = {
  contractId: "CE0-CTX-IF"
  bundleHash: string
  query: ContextQueryV1
  sources: Array<{
    sourceId: string
    kind: "card" | "island" | "edge" | "review"
    version: string
  }>
}

export type ProposalPatchV1 = {
  contractId: "CE0-REVIEW-IF"
  bundleHash: string
  operations: Array<{
    op: "add" | "replace" | "remove"
    path: string
    value?: unknown
  }>
  requiresApproval: true
}

export type AuditEventV1 = {
  contractId: "CE0-SAFEMODE-IF"
  eventId: string
  eventType:
    | "preview_required"
    | "unknown_contract_key"
    | "nondeterministic_bundle"
    | "approval_granted"
    | "approval_rejected"
  timestamp: string
  actor: "human" | "system"
  bundleHash?: string
}
```

### 2) Type/boundary freeze rules（v1）

- `ContextQueryV1.goal/scope/depth/constraints/reviewFilter/safeModePolicy/outputMode` は **必須**。
- `safeModePolicy.safeMode=true` と `safeModePolicy.allowUnreviewedText=false` は **固定値**（緩和禁止）。
- `ContextBundleV1.bundleHash` は決定論的に再計算可能であること（`nondeterministic_bundle` 検知対象）。
- `ProposalPatchV1.requiresApproval=true` は固定。`Working -> Consensus` 直書きは禁止（patch+approvalのみ）。
- 不明キーは受理せず `unknown_contract_key` を監査イベントへ記録。

### 3) Contract boundary（責務分離）

- CE0 が定義するのは **I/F 契約面のみ**。
- CE1/CE2/CE4 は本契約を read-only 参照し、CE0 文面改変要求は `held` とする。
- Backend / Frontend / CLI は同一署名を採用するが、内部実装差異は契約対象外。

### 4) Explicit mock points（実装前提の差し替え点）

- `ContextBundleProvider`（query→bundle生成）
- `DeterministicHashProvider`（bundleHash算出）
- `PatchPlanner`（preview/proposal生成）
- `ApprovalGateway`（human approval 判定）
- `AuditSink`（監査イベント永続化）

> 上記5点は **モック実装を先行許可**。ただし入出力署名は本契約から逸脱してはならない。

### 5) Freeze guard（逸脱時の扱い）

- 追加/改名/削除を含む Contract ID 変更は禁止（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` 固定）。
- No-Go canonical IDs（`preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`）は固定。
- 逸脱提案は実装せず `held` 登録し、人間承認まで凍結継続。

## Stream B latest run（2026-05-10 / CE-0 Contract Freeze / Stream B execution）

- run_id: `stream-b-ce0-2026-05-10-01`
- assignee: `Stream B（CE-0 Contract Freeze 専任）`
- edit_allowlist: `issue-CE0-contract-freeze.md`, `issue-CE0-core-graph-repositioning.md`（本実行指示に従い docs-only）
- strategy: `contract-only / mock-first / I/F先行固定（API signature・data type・audit event name）`

### Phase 1 Read（Contract ID / 禁止事項 / AC欠落抽出）
- Contract IDs（固定・再定義禁止）: `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`。
- CE0 canonical No-Go IDs（固定）: `preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`。
- 禁止事項を再確認: Contract IDの追加・改名・削除、safeMode既定後退、実装ロジック確定、指定外ファイル編集。
- AC欠落抽出: CE-1へ渡すI/Fの「API署名 / データ型 / 監査イベント名」の最小固定セットを明文化する受入条件が未明示。

### Phase 2 ADR明文化（Context / Decision / Consequences）
- Context: CE-0契約をSSOTとして固定し、CE-1以降の下流が契約ドリフトなく mock-first 検証できる状態が必要。
- Decision: CE-0では `ContextQueryV1` / `ContextBundleV1` / `ProposalPatchV1` / `AuditEventV1` を **I/F名固定のみ** とし、実装意味論は凍結（mock前提）する。
- Consequences: 実装依存を切り離して並行検証を維持できる一方、ロジック解釈が必要な論点は CE-1 へ持ち越す。
- CE-0 fixed contract matrix との矛盾判定: 明示的矛盾なし。是正案: なし（将来矛盾が出た場合は `held` で是正案のみ提示）。

### Phase 3 Plan（I/F先行固定）
- 固定対象: API署名、データ型、監査イベント名のみ。
- 非固定対象: 実装ロジック、アルゴリズム、最適化、永続化詳細（mock-firstで凍結）。
- ACドラフト提案（合意待ち）:
  - AC-IF-1: CE-0文書にあるI/F名は `ContextQueryV1` / `ContextBundleV1` / `ProposalPatchV1` / `AuditEventV1` 以外を増やさない。
  - AC-IF-2: `preview_required` / `unknown_contract_key` / `nondeterministic_bundle` の語彙意味をv1で固定する。
  - AC-IF-3: 監査イベント名は `contract_freeze_verified` / `contract_drift_detected` / `freeze_hold_invoked` を予約語としてCE-1へhandoffする。

### Phase 4 Execute（docs-only / contract-only）
- 本Issueへの記録追加のみ実施。
- 実装コード・schema・shared 3 files・他issueの変更は未実施。

### Phase 5 Verify（docs-check / Self-Correction <=3）
- attempt_1: `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- attempt_1: `git diff --check`
- attempt_1: pass（self-correction `0/3`）

### Phase 6 Proceed（完了判定 / CE-1 handoff）
- 判定: **Conditional-Go（CE-0 Contract Freeze maintained）**。
- CE-1へ渡すI/F仕様（契約固定済）:
  1) API署名: `POST /context/query`, `POST /context/bundle`（stub契約）
  2) データ型: `ContextQueryV1`, `ContextBundleV1`, `ProposalPatchV1`, `AuditEventV1`
  3) 監査イベント名: `contract_freeze_verified`, `contract_drift_detected`, `freeze_hold_invoked`
- 停止条件: 未定義競合・No-Go語彙不一致・4回目相当の自己修復要求が発生した場合は `held` で停止して指示待ち。

## Stream B latest run（2026-05-17 / CE0 contract freeze docs-process confirmation）

- run_id: `stream-b-ce0-2026-05-17-01`
- assignee: `Stream B（CE0 Contract Freeze 専任）`
- scope_guard: `edit_allowlist=01_Plans/issues/issue-CE0-contract-freeze.md only`（遵守）
- mission: `CE0 contract freeze を docs/process 観点で確定（I/F先行定義・mock-first分離）`

### Phase 1 Read
- 本Issueを再読し、単一ファイル編集・contract-only・docs-only・mock-first の境界を再確認。
- 固定Contract IDs（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）と No-Go canonical IDs 5件固定を再確認。
- 停止条件（指定外編集 / safeMode既定後退 / Contract ID再定義 / Verify 4回目相当）を再確認。

### Phase 2 ADR（Context / Decision / Consequences）
- Context: CE1/CE2/CE4 が read-only 参照できる CE0契約SSOT を維持しつつ、実装依存を切り離した handoff が必要。
- Decision: CE0では I/F契約境界（型・シグネチャ・語彙意味）だけを固定し、実装意味論は mock に委譲して凍結継続。
- Consequences: 並行実装時の契約ドリフトを抑止できる一方、実装最適化論点は CE1以降での人間承認付き検討に限定される。
- ADR追補要否判定: `cdc_required=0`（既存契約と矛盾なし、追加ADR起票なし）。

### Phase 3 Plan（AC / DoD）
- AC:
  - `ac_if_signature_freeze`: `ContextQueryV1` / `ContextBundleV1` / `ProposalPatchV1` / `AuditEventV1` の契約名を増減・改名しない。
  - `ac_vocab_semantics_freeze`: `preview_required` / `unknown_contract_key` / `nondeterministic_bundle` の意味論をv1固定で扱う。
  - `ac_mock_first_boundary`: 実装はモック差し替えを許可し、契約署名逸脱を禁止する。
- DoD:
  - `dod_single_file_scope`: 編集対象が本Issue単一ファイルであること。
  - `dod_no_contract_id_mutation`: Contract IDs / No-Go IDs の追加・改名・削除がないこと。
  - `dod_verify_retry_cap`: Verify自己修復は最大3回、4回目相当は `held` 停止。

### Phase 4 Execute
- 実施: 本Issueへの docs/process 記録追記のみ。
- 非実施: 実装コード変更、他ストリームファイル変更、schema変更、safeMode既定値変更。

### Phase 5 Verify（<=3 retries）
- attempt_1:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
  - result: pass（self-correction `0/3`）

### Phase 6 Proceed / Stop
- 判定: **Proceed（Conditional-Go）**
- 維持条件:
  - CE0は契約SSOTを継続し、下流はread-only参照のみ。
  - 未定義競合、語彙意味不一致、指定外編集要求、Verify 4回目相当が発生した場合は **Stop（`held`）**。


## Stream B latest run（2026-05-19 / Contract Freeze + Interface-First refresh）

### Phase 1 Read（dependency / boundary extraction）
- CE0 の契約境界を `ADR-0028` CE-0 Contract Matrix、および HIL-RS A1 の固定値群と照合した。
- 依存方向を **`HIL-RS-01-A1 -> HIL-RS-02-A1 -> CE0 -> CE1/CE2/CE4`** に固定し、CE0 から上流へ逆依存しないことを確認。
- 未確定点は `approvalRecord` / `pendingDecisionQueueCount` / `HIL-RS-02-GOV-EXCEPTION-01` の3点に限定した。

### Phase 2 ADR（Context / Decision / Consequences）
- **Context**: 下流実装が他ストリーム待ちにならないため、CE0はread-only contractを先に固定する必要がある。
- **Decision**: `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05` を変更禁止のまま維持し、mock contract で handoff 可能状態を継続する。
- **Consequences**: CE1/CE2/CE4 は CE0 を参照して着手できるが、契約更新は CE0 再起票＋承認完了まで禁止となる。

### Phase 3 Plan（AC / DoD）
- AC-1: CE0 Contract IDs と safeMode 境界が単一正本に明記されている。
- AC-2: mock-only で `executeAllowed/reasonCodes` まで検証可能である。
- AC-3: 破壊的変更は `future-version backlog` 隔離ポリシーが明記されている。
- DoD: 下流が CE0 契約だけで作業開始可能、かつ依存が一方向で循環しない。

### Phase 4 Execute（contract-only）
- 実装仕様・コード変更は行わず、契約面のみ更新。
- 未承認項目は `held` のまま据え置き、推測確定を行わない。

### Phase 5 Verify
- `contract_id_mutation=0`
- `safeMode_regression=0`
- `dependency_cycle=0`
- self-correction: `0/3`

### Phase 6 Proceed（downstream handoff pointers）
- 下流参照先（read-only）:
  - `01_Plans/issues/issue-CE0-contract-freeze.md`（本契約SSOT）
  - `01_Plans/issues/issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`（A1固定キー）
  - `01_Plans/issues/issue-HIL-RS-02-A1-governance-contract-hardening.md`（統治ゲート）
- 判定: **Conditional-Go（Pending/held 残存のため）**。


## Stream D execution update（2026-05-19 / CE契約群 / contract freeze cross-check）

### Phase 1 Read（差分抽出）
- CE0/CE1 関連契約を再読し、固定ID群 `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` と No-Go canonical IDs の再定義禁止を確認。
- `Core Graph` は旧称であり、現行契約語彙は `ConsensusGraph` であることを `domain.md` と照合。
- 未承認事項（新規ID追加・safeMode境界緩和・実装前提の確定）を「確定扱いしない」停止条件として明示。

### Phase 2 契約定義（最小I/F固定: read-only）
- CE0 は read-only freeze を維持し、Contract ID の追加/改名/削除を禁止。
- CE1 参照契約の受け渡しキーを `queryCanonicalHash` / `bundleHash` / `previewConfirmed` に限定。
- 本Issueでは実装I/F拡張を行わず、既存契約の境界明示のみ許可。

### Phase 3 モック規約（互換・後方互換）
- mock適用境界: contract-only 検証（型/語彙/hash）まで。
- 互換性ルール: `422 preview_required` / `400 unknown_contract_key` / `409 nondeterministic_bundle` を v1 固定。
- 後方互換方針: v1 は closed-world 固定。拡張は v2 契約改訂でのみ許可（v1 へ未定義キー逆流禁止）。

### Phase 4 検証（依存・他Issue影響）
- 依存確認: CE0 freeze は CE1/CE2/CE4 の前提だが、下流は mock-first 継続可。
- 影響確認: CE0本文で CE1 実装詳細を確定しないことにより、ストリーム間の契約衝突を回避。
- self-repair: 0/3（修復不要）。

### Phase 5 受け渡し（Stream C/E向け）
- Stream C/E へは read-only 参照仕様として以下を引き渡す。
  - Contract IDs（CE0固定）
  - fixed error semantics 3種
  - hash監査キー（`queryCanonicalHash` / `bundleHash`）
- Fail-safe判定: 用語不整合・契約衝突・未承認事項の確定化は未検知（`Proceed=Conditional-Go`）。


## Stream B execution update（2026-05-19 / CE0 contract SSOT refresh）

### Phase 1 Read（Status/Priority/Depends/Unblocks/AC 再確認）
- Status=`Open` / Priority=`P1` を維持し、Scope は docs-only・contract-only のまま固定。
- Depends: `HIL-RS-01-A1 freeze vocabulary (read-only)`、Unblocks: `issue-CE0-core-graph-repositioning.md` / `issue-CE1-context-query-bundle-foundation.md`（read-only handoff）を再確認。
- AC（read-only reference, no-go canonical IDs 固定, CDC held 必須）に欠落なしを確認。

### Phase 2 Mock-First切断設計（共有リソース列挙 + 最小シグネチャ）
- 競合しうる共有リソース（再定義禁止）:
  - Contract IDs: `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`
  - schema/API語彙: `ContextQueryV1` / `ContextBundleV1` / `preview_required` / `unknown_contract_key` / `nondeterministic_bundle`
  - graph語彙: `WorkingGraph` / `ContextProjectionGraph` / `ConsensusGraph`
- CE1先行最小シグネチャ（read-only handoff）:
  - ContextQuery keys: `goal/scope/depth/constraints/reviewFilter/safeModePolicy/outputMode/previewConfirmed`
  - ContextBundle keys: `queryCanonicalHash/bundleHash/selected/relations/evidence/contradictions/reviewFlags/truncationMeta/excludedReason`
- 実装依存切断手順（Mock Provider）:
  1) `/context/query` と `/context/bundle` は `stubDatasetId=A2-minimal-v1` を固定入力とする。
  2) provider差し替えは `queryCanonicalHash` / `bundleHash` の決定論一致（3/3）を満たす場合のみ許可。
  3) 実DB・実LLM・worker連携は CE1 契約検証フェーズへ持ち込まない（contract-only）。

### Phase 3 Plan→Execute→Verify
- Plan: AC/DoD不足なし。追加提案は不要（現行SSOT維持）。
- Execute: CE0本文の契約固定のみ更新（ID追加/改名/削除なし）。
- Verify: 依存逆転なし（CE0→CE1/CE0→CE0-core の一方向）を確認。下流参照は read-only で可能。

### Phase 4 Stopper
- 自己修復が3回を超える、または Contract ID collision / safeMode既定後退 / dependency inversion が発生した場合は `held` で停止し判断依頼する。

## Stream B dependency reconfirmation（2026-05-20 / CE契約・モック切断）

### Phase 1: 最新Read + 依存再確認
- 対象4Issue（CE0/CE1/CE2/CE4）の Status/Priority/依存/Mock方針を再確認し、CE0は **契約SSOTのread-only基準点**として維持する。
- 依存判定は実装依存ではなく、`Contract ID固定 + fail-closed語彙固定 + mock-first許容条件` の3点で切断可能と判断。

### Phase 2: インターフェース先行定義との整合
- CE1を契約固定点とする方針をCE0側から追認し、CE0は `CE1-CTXQ-IF/CE1-CTXB-IF` を **参照のみ**（再定義禁止）とする。
- CE2/CE4は proposal-only 接続に限定し、CE0から実装要求を派生させない。

### Phase 3: Plan→Execute→Verify（CE0視点）
- Plan: CE0の役割を「語彙固定・No-Go固定・safeMode境界固定」に限定。
- Execute: 本Issueへの記録更新のみ（docs-only / contract-only）。
- Verify:
  - 依存循環なし（CE0は上流基準点、CE2/CE4はCE1経由参照で接続）。
  - Draft→Open条件は `fixedKeyDrift=0` / `approval missing=0` / `self-correction<=3` の測定可能条件で保持。

### Phase 4: Stopper
- CE1契約が曖昧化した場合、または他ストリーム領域編集が必要になった場合は `held` 停止として扱う。


## Stream B latest run（2026-05-20 / CE0 contract freeze / Plan→Execute→Verify→Proceed）

### Phase 1 Read Gate
- Read Order 上位文書と本Issueを再読し、CE0は **contract-only / docs-only / mock-first** の範囲に限定されることを確認。
- 編集許可外ファイルの変更が必要になる場合は `held` で停止するゲートを再確認。
- CE0固定契約（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）の再定義禁止を確認。

### Phase 2 ADR/契約明文化（Context / Decision / Consequences）
- **Context**: CE1/CE2/CE4 が参照する前提として、CE0の禁止境界とNo-Go IDsを揺らさず維持する必要がある。
- **Decision**: CE0契約は read-only SSOT として維持し、ID追加・改名・削除・意味変更を禁止する。
- **Consequences**: 下流は契約衝突なく参照継続でき、競合検知時は `held` 停止で fail-closed を担保できる。

### Phase 3 I/F先行定義（型・APIシグネチャ・イベント）
- `freezeDecision = { decision: Proceed|Hold|Stop, executeAllowed: boolean, reasonCodes: string[] }` を CE0の最小判断I/Fとして固定。
- 監査イベント最小キーを `timestamp/actor/phase/gateResult/reason/nextAction` で固定。
- 本Phaseは定義のみであり、実装・状態遷移ロジックの確定は行わない。

### Phase 4 モック方針定義
- mock/stubは `decision` と `reasonCodes` の検証までを許可し、承認実遷移確定は対象外とする。
- fixture/stub前提で並行実装可能とし、実DB/実LLM依存を持ち込まない。

### Phase 5 AC/DoD更新
- AC: CE0契約ID不変、No-Go IDs不変、safeMode後退ゼロを必須化。
- DoD: docs-only差分で、下流参照に必要な判断I/F・停止条件・監査キーが本Issue単独で復元可能。

### Phase 6 Verify（契約一貫性）
- Verify観点: `contract_id_mutation=0` / `safeMode_regression=0` / `out_of_scope_edit=0`。
- 競合検知ポリシー: 契約ID衝突・語彙衝突・allowlist逸脱を検知した時点で即停止（推測実装禁止）。

### Phase 7 Self-correction（最大3回）
- attempt 1: 契約ID表記揺れ点検（差分不要）。
- attempt 2: No-Go IDs と fail-safe 条件の対応点検（差分不要）。
- attempt 3: AC/DoD と Verify観点の整合点検（差分不要）。

### Phase 8 完了報告
- 判定: **Proceed（Conditional-Go）**。
- 条件: CE0は引き続き read-only 契約参照専用。競合検知時は `held` 停止を維持。

## Stream B handoff readiness packet（2026-06-02 / CE0 read-only downstream evidence）

### Context
- CE0 は引き続き contract-only / docs-only / mock-first の SSOT として扱う。
- 下流（CE0 core graph / CE1 / CE2 / CE4）は本Issueを read-only 参照できるが、Contract ID、No-Go ID、SafeMode境界を再定義してはいけない。
- 本更新は実装許可や契約変更ではなく、下流が参照してよい証跡と停止条件を1か所にまとめる。

### Handoff evidence
| Handoff item | Frozen value / evidence | Downstream use | Stop condition |
| --- | --- | --- | --- |
| Contract IDs | `CE0-CTX-IF`, `CE0-SAFEMODE-IF`, `CE0-REVIEW-IF`, `CG-01..05` | IDを参照し、再定義しない | 追加/改名/削除/意味変更 |
| No-Go canonical IDs | `preview_bypass`, `consensus_direct_write`, `auto_apply_or_publish`, `ai_review_auto_promotion`, `safemode_default_relaxation` | 下流の失敗理由・テスト名・監査理由へそのまま使う | 同義語化・別名化・優先度変更 |
| SafeMode boundary | safeMode default ON / `allowUnreviewedText=false` | CE1/CE2/CE4 の mock とUI証跡で安全既定を維持 | 既定OFF化、未レビュー本文許容、自動昇格 |
| Mock-first boundary | `decision`, `executeAllowed`, `reasonCodes` まで | 実DB/実LLM/workerなしで契約検証できる | Pending→Approved/Rejected の実遷移確定 |
| Audit minimum | `timestamp`, `actor`, `phase`, `gateResult`, `reason`, `nextAction` | gate evidence と検証ログを接続する | 入力snapshotやreason欠落を成功扱い |

### Downstream readiness gates
- CE0-core graph: `working` / `context_projection` / `consensus` と `patch+approval` のみを参照し、direct write / auto-apply / auto-publish を許可しない。
- CE1: `ContextQueryV1` / `ContextBundleV1` の closed-world 契約を利用し、Query Preview bypass を成功扱いしない。
- CE2: AI assist は proposal-only とし、`human_reviewed` 昇格や ConsensusGraph 更新を自動化しない。
- CE4: query/bundle/proposal/apply の監査4点と hash キーを、CE0 の audit minimum へ接続する。

### Verify / Proceed
- Verify command remains docs-check only:
  - `03_Implement\backend\.venv\Scripts\python.exe 01_Plans\issues\validate_active_issue_memos.py`
  - `03_Implement\backend\.venv\Scripts\python.exe 01_Plans\triage_actionable_plans.py`
  - `git diff --check -- 01_Plans\issues\issue-CE0-contract-freeze.md`
  - `rg -n "Stream B handoff readiness|CE0-CTX-IF|preview_bypass|safeMode default ON|decision|executeAllowed|reasonCodes|query/bundle/proposal/apply" 01_Plans\issues\issue-CE0-contract-freeze.md`
- Proceed: Conditional-Go for downstream read-only reference.
- Stop: Any implementation change, Contract ID mutation, No-Go aliasing, or SafeMode default relaxation.

## Current-main checkpoint（2026-06-14 / post-2394 CE0 contract freeze）

### Context
- Baseline: `main@69fcafdeff23` after PR #2394.
- Scope: docs-only checkpoint for CE0 contract freeze. This update does not approve implementation, add API behavior, rename IDs, or relax SafeMode.
- Purpose: keep downstream CE0/CE1/CE2/CE4 work aligned with the frozen contract boundary before any productization task consumes these terms.

### Frozen Contract Evidence
| Area | Current frozen value | Check result |
| --- | --- | --- |
| Contract IDs | `CE0-CTX-IF`, `CE0-SAFEMODE-IF`, `CE0-REVIEW-IF`, `CG-01..05` | `contract_id_mutation=0` |
| No-Go IDs | `preview_bypass`, `consensus_direct_write`, `auto_apply_or_publish`, `ai_review_auto_promotion`, `safemode_default_relaxation` | no alias / no priority change |
| SafeMode | default ON, `allowUnreviewedText=false` | `safeMode_regression=0` |
| Decision I/F | `freezeDecision = { decision: Proceed|Hold|Stop, executeAllowed: boolean, reasonCodes: string[] }` | signature unchanged |
| Audit minimum | `timestamp`, `actor`, `phase`, `gateResult`, `reason`, `nextAction` | audit key set unchanged |
| Dependency direction | CE0 is the read-only upstream SSOT for downstream reference | `dependency_cycle=0` |

### Decision
- Proceed as Conditional-Go for downstream read-only reference only.
- Keep this issue Open until the downstream implementation lane records evidence that it consumes the frozen IDs without redefining them.
- No ADR is required for this checkpoint because no contract value, release authority, SafeMode boundary, or implementation responsibility changed.

### Stop Conditions
- Hold immediately if a future change mutates a Contract ID, introduces a synonym for a No-Go ID, changes SafeMode defaults, or lets this CE0 issue approve implementation behavior.
- Hold immediately if downstream work treats this checkpoint as permission to bypass review, auto-apply proposals, or publish unreviewed text.
