# Issue Draft: CE2 Low-Risk AI Assist（Stream E / proposal-only）

- Type: Feature request
- Status: Open
- Priority: P1
- Owner: Stream E（CE2専属）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Related Backlog: `CE-2`
- Related ADR/Spec: `ADR-0028`
- Verification: `docs-check`

## Lane guard
- CE2は proposal-only 契約固定が目的。自動適用実装は対象外。
- 実装指示混入時は停止。
- 編集許可は本ファイルのみ（`issue-CE2-low-risk-ai-assist.md`）。
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

## Phase 1.5 ADR CDC（必要時のみ）
- 参照元（ADR/Architecture）と契約語彙が衝突する場合のみ差分メモを作成。
- 未定義競合は解決せず、CE2 lane を `held` として停止。

## Phase 2 Plan（AC/DoD不足ドラフト）
### AC Draft
- [ ] auto-apply経路0件
- [ ] AI自動昇格0件
- [ ] CE1 drift検知時は `status=held`
- [ ] 各Phase開始前に本ファイル再Readを実施

### DoD Draft
- [ ] proposal語彙が単一正本
- [ ] `held` 停止条件がNo-Goとして明記済み
- [ ] `Read → ADR CDC(必要時) → Plan → Execute → Verify → Proceed` の順序を維持

## Phase 3 Execute（依存正規化）
- CE1未完了でも `sourceBundleHash=mock:<hash>` で契約検証継続。
- CE0/CE4は read-only参照として扱い、CE2で再定義しない。
- auto-apply 実装・review自動昇格実装は追加しない（proposal-only固定）。

## Phase 4 Verify
- `docs-check`
- Proposal I/Fの必須キー欠落0、状態遷移衝突0。
- 禁止経路（auto-apply / review自動昇格）混入0。

## Phase 5 Proceed（実装入力固定）
### I/F仕様書固定
- `ProposalDraftV1`
- Lifecycle: `proposed -> accepted/rejected/held`
- Fail-safe: drift時 `held` 固定
- フェイルセーフ: 3回超過・禁止経路混入・未定義競合で停止。
