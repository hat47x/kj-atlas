# Issue Draft: CE2 Low-Risk AI Assist（Stream B / proposal-only / planning-only）

- Type: Feature request
- Status: Open
- Priority: P1
- Owner: Stream B（CE契約専任）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Related Backlog: `CE-2`
- Related ADR/Spec: `ADR-0028`, `02_Architecture/schemas.md`
- Verification: `docs-check`

## Lane guard
- CE2は proposal-only 契約固定が目的。自動適用実装は対象外。
- CE1/CE0 契約は参照専用（CE2で再定義しない）。
- 未承認決定は `held` とし、確定扱いしない。
- `reviewState=human_reviewed` へのAI自動昇格は禁止。

## Phase 1) Read同期（ADR-0028整合確認）
### Contract IDs
- `CE2-PROPOSAL-IF`
- `CE2-LIFECYCLE-IF`
- `CE2-DRIFT-STOP-IF`
- `CE2-NO-AUTOAPPLY-IF`

### Proposal I/F
- 必須: `proposalId/diff/sourceBundleHash/rationale/status/reviewState`
- `status`: `proposed | accepted | rejected | held`
- `reviewState`: `unreviewed | human_reviewed`

### 禁止
- auto-apply
- AIによる `human_reviewed` 自動昇格

## Phase 2) Plan（AC/DoD不足時の提案）
- AC不足時は「auto-apply経路ゼロ」「AI自動昇格ゼロ」「drift時held停止」を補強する。
- DoD不足時は「proposal語彙単一正本」「No-Goの明記」「順序遵守（Read→Plan→Execute→Verify→Proceed）」を補強する。
- 補強提案は CE0/CE1既存契約参照に限定し、CE2で再定義しない。

## Phase 3) ADR CDC（必要時のみ: CE2契約凍結）
- CE0 `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` を参照し、CE2側でsafeModeやreview遷移を再定義しない。
- CE1 `bundleHash` を参照し、`sourceBundleHash` は比較キーとしてのみ扱う。
- CE1 drift検知時は `status=held` で停止する。

## Phase 4) Execute（Issue粒度・依存・検証計画の確定）
### CE1/CE2のmock前提I/F分離
- CE2が必要とするCE1依存は `sourceBundleHash` のみ（query語彙を持ち込まない）。
- mock hash検証でも lifecycle (`proposed/accepted/rejected/held`) を変更しない。
- proposal評価とreview昇格判定を分離し、後者は人手操作のみ許可。

### CE4連携契約（API/CLI/Audit）定義
- CE4監査導線に `proposal/apply` を必須提供。
- `dryRun=true` では `apply` を「実行試行ログのみ・副作用なし」で記録。
- fail-closed: 監査欠損またはhash不整合は成功扱い禁止。

## Phase 5) Verify / Proceed（検証可能性・再開可能性チェック）
### Acceptance Criteria
- [ ] auto-apply経路0件
- [ ] AI自動昇格0件
- [ ] CE1 drift検知時は `status=held`
- [ ] `sourceBundleHash === bundleHash` 比較語彙がCE1と一致

### Definition of Done
- [ ] proposal語彙が単一正本
- [ ] `held` 停止条件がNo-Goとして明記済み
- [ ] `Read → Freeze/Normalize → Plan → Verify → Proceed` の順序を維持

### Verify
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`
- Proposal I/F必須キー欠落0、状態遷移衝突0、禁止経路混入0。
- 自己修復は最大3回。4回目相当は停止。

### Proceed（実装ストリーム向けI/F配布）
- `ProposalDraftV1`
- Lifecycle: `proposed -> accepted/rejected/held`
- Fail-safe: drift時 `held` 固定
- Dependency: `sourceBundleHash` は CE1契約参照のみ
