# Issue Draft: CE2 Low-Risk AI Assist（Stream D / proposal-only / planning-only）

- Type: Feature request
- Status: Open
- Priority: P1
- Owner: Stream D（CE契約専任）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Related Backlog: `CE-2`
- Related ADR/Spec: `ADR-0028`, `02_Architecture/schemas.md`
- Verification: `docs-check`

## Lane guard
- CE2は proposal-only 契約固定が目的。自動適用実装は対象外。
- CE1/CE0 契約は参照専用（CE2で再定義しない）。
- 未承認決定は `held` とし、確定扱いしない。
- `reviewState=human_reviewed` へのAI自動昇格は禁止。

## Phase 1 Read（契約I/F抽出）
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

## Phase 2 契約参照正規化（CE1/CE0参照固定）
- `sourceBundleHash` は CE1 `bundleHash` を参照する比較キーとしてのみ扱う。
- CE0 `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` を参照し、CE2側でsafeModeやreview遷移を再定義しない。
- CE1 drift検知時は `status=held` で停止する。

## Phase 3 Plan（AC/DoD）
### Acceptance Criteria
- [ ] auto-apply経路0件
- [ ] AI自動昇格0件
- [ ] CE1 drift検知時は `status=held`
- [ ] `sourceBundleHash === bundleHash` 比較語彙がCE1と一致

### Definition of Done
- [ ] proposal語彙が単一正本
- [ ] `held` 停止条件がNo-Goとして明記済み
- [ ] `Read → Freeze/Normalize → Plan → Verify → Proceed` の順序を維持

## Phase 4 Verify
- `docs-check`
- Proposal I/F必須キー欠落0、状態遷移衝突0、禁止経路混入0。
- 自己修復は最大3回。4回目相当は停止。

## Phase 5 Proceed（実装ストリーム向けI/F配布）
### I/F仕様書固定
- `ProposalDraftV1`
- Lifecycle: `proposed -> accepted/rejected/held`
- Fail-safe: drift時 `held` 固定
- Dependency: `sourceBundleHash` は CE1契約参照のみ
