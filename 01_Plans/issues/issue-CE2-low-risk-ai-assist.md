# Issue Draft: CE2 Low-Risk AI Assist（Stream E専任 / CE契約群 / proposal-only / contract-only planning）

- Type: Feature request
- Status: Open
- Priority: P1
- Owner: Stream E（CE2専任 / proposal-only契約固定）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Editable: `issue-CE2-low-risk-ai-assist.md` のみ
- Related Backlog: `CE-2`
- Related ADR/Spec: `ADR-0028`, `02_Architecture/schemas.md`
- Verification: `docs-check`

## Lane guard（固定）
- proposal lifecycle は `proposed | accepted | rejected | held` を固定し、再定義しない。
- CE2 proposal lifecycle は `proposed | accepted | rejected | held` 以外を許可しない（固定）。
- CE2は **proposal-only 契約固定**（実装禁止）。
- CE1/CE0契約は参照専用（CE2で再定義しない）。
- auto-apply は常時禁止。
- `reviewState=human_reviewed` のAI自動昇格は禁止（人手のみ）。
- 強制ワークフローは `Phase 1 Read → Phase 2 Plan（AC/DoD補完）→ Phase 3 Execute → Phase 4 Verify → Phase 5 Proceed` に固定する。
- 編集許可は `issue-CE2-low-risk-ai-assist.md` のみ。実装コード・共有統合・他CE issue編集は禁止。

## Phase 1 Read（全対象Read: Status / Scope / Related ADR確認）
### Read同期スナップショット
- 固定語彙: `sourceBundleHash` / proposal lifecycle / `equivalenceKey + bundleHash`（CE4同値判定参照）
- No-Go語彙: `auto-apply` / AI review自動昇格 / `preview bypass` / `safeMode既定緩和`
- `reviewState` 語彙: `unreviewed | human_reviewed`（昇格は人手のみ）

### Contract IDs
- `CE2-PROPOSAL-IF`
- `CE2-LIFECYCLE-IF`
- `CE2-DRIFT-STOP-IF`
- `CE2-NO-AUTOAPPLY-IF`

### Proposal I/F
- 必須: `proposalId/diff/sourceBundleHash/rationale/status/reviewState`
- `status`: `proposed | accepted | rejected | held`
- `reviewState`: `unreviewed | human_reviewed`

### No-Go / safeMode境界
- auto-apply 禁止
- AIによる `human_reviewed` 自動昇格禁止
- `CE0-SAFEMODE-IF` を参照し、CE2側で緩和しない

## Phase 2 Plan（AC/DoD補完：候補提示限定・自動採用禁止・review自動昇格禁止を固定）
- CE1参照境界: `sourceBundleHash` 比較キーのみ依存。
- CE4参照境界: `proposal/apply` 監査語彙を共通化し、同値判定は `equivalenceKey + bundleHash` を参照のみで利用。
- I/F固定項目: `proposalId` / `diff` / `sourceBundleHash` / `rationale` / `status` / `reviewState`
- CE2のAI支援は候補提示（proposal）に限定し、採用判定は人手のみ。
- `status=accepted` は人手承認の結果としてのみ遷移し、AIの自動採用は禁止。
- `reviewState=human_reviewed` は人手操作のみで遷移可能（AI提案は `unreviewed` 固定）。
- drift検知時は `status=held` で停止。
- CE2独自のquery語彙追加は禁止（再定義防止）。

### ADR/CDC（必要時のみ実施）
- 条件: CE2契約語彙（lifecycle / `sourceBundleHash` / `reviewState` / No-Go語彙）に変更要求が出た場合。
- 手順: CDCを明文化し、`status=held` で承認待ちに遷移してから次Phaseへ進む。
- 比較対象: `CE0-REVIEW-IF`, `CE0-SAFEMODE-IF`, `CE1-CTXB-IF`（参照のみ）。
- 判定: 不一致が1件でもあれば差分理由のみ記録し、CE2で再定義しない。

## Phase 3 Execute（patch/diff追跡可能性を明文化）
- 実行内容は proposal-only 契約文言の更新に限定し、実装手順・実行権限の記述は行わない。
- 差分検知ログ: proposal lifecycle、`sourceBundleHash`、No-Go語彙の不一致。
- **Context**: proposal lifecycle / review遷移 / drift-stop の衝突有無。
- **Decision**: proposal-only + no-auto-apply + human-only昇格を維持。
- **Consequences**: CE4監査で proposal/apply の追跡可能性が固定化。
- **Approval**: 差分発生時の反映状態は `held`。
- 追跡可能性要件: すべての提案変更は `proposalId` をキーに `patch/diff` と `sourceBundleHash` を紐付け、監査時に再現可能であること。
- 監査導線: `proposal` と `apply` の監査トレースを分離し、CE2は proposal-only 契約境界を維持する。

## Phase 4 Verify（safeMode後退ゼロを検証）
- lifecycleを `proposed/accepted/rejected/held` に固定。
- `held` を fail-safe停止語彙として統一。
- `sourceBundleHash === bundleHash` を参照整合キーとして明示。
- AC/DoD不足ドラフトを先に固定し、実行中の契約再定義を禁止。
- proposal-only を維持し、実装・auto-apply 経路の作成/示唆を禁止。
- collision=0 / safeMode regression=0 を満たす整理を実施。
- 検証失敗時は自己修復を最大3回まで、4回目相当は停止。
- 契約再定義要求または safeMode 後退要求を受けた場合は即停止（Fail-safe）。
- lifecycle は常に `proposed|accepted|rejected|held` のみを許可し、別名語彙を導入しない。
- `reviewState=human_reviewed` は人手操作のみで遷移可能（AI提案は `unreviewed` に固定）。

### Verify commands
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`
- safeMode検証観点: `CE0-SAFEMODE-IF` の既定（safeMode ON / `allowUnreviewedText=false`）を参照し、CE2追記が緩和・迂回を作っていないことを差分で確認する。

### Acceptance Criteria / DoD
- [ ] auto-apply経路0件
- [ ] 候補提示（proposal）限定であり、自動採用経路0件
- [ ] AI自動昇格0件
- [ ] CE1 drift検知時は `status=held`
- [ ] `sourceBundleHash === bundleHash` 比較語彙がCE1と一致
- [ ] SafeMode regression = 0
- [ ] lifecycle語彙が `proposed|accepted|rejected|held` 以外を含まない
- [ ] CE4 handoff は read-only を維持する
- [ ] docs-check（3点セット）を実行し、自己修復は最大3回以内で収束
- [ ] 変更対象ファイルが `issue-CE2-low-risk-ai-assist.md` のみである
- [ ] 未確定項目は `held` のまま次工程へ渡し、確定語彙へ昇格させない

## Phase 5 Proceed（未確定は保留、3回超過や前提崩壊で停止）
### Fixed contract handoff
- Contract IDs: `CE2-PROPOSAL-IF` / `CE2-LIFECYCLE-IF` / `CE2-DRIFT-STOP-IF` / `CE2-NO-AUTOAPPLY-IF`
- 禁止事項: auto-apply / AI review昇格 / safeMode緩和
- 検証条件: lifecycle固定, drift-stop有効, docs-check pass
- handoff先: CE4監査（read-only）
- 未確定事項は `held` を維持し、確定扱いで次工程へ渡さない。

## Fail-safe（即停止条件）
- Self-Correction 3回超過
- 契約再定義要求の発生
- 未定義ファイル競合
- SafeMode後退の兆候
- 依存前提崩壊（参照契約の欠損・整合不能を含む）
