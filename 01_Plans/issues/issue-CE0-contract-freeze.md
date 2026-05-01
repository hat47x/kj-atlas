# Issue Draft: CE0 Contract Freeze（Stream B / CE0 Contract SSOT / contract-only planning）

- Type: Process
- Status: Open
- Priority: P1
- Owner: Stream B（CE0 Contract Freeze 専任）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Editable: `01_Plans/issues/issue-CE0-contract-freeze.md` のみ（Stream B 制約）
- Related Backlog: `CE-0`
- Related ADR/Spec: `ADR-0028`, `02_Architecture/schemas.md`
- Dependencies: `CE-0`
- Verification: `docs-check`

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
