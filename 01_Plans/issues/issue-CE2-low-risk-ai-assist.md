# Issue Draft: CE2 Low-Risk AI Assist（Stream E / proposal-only）

- Type: Feature request
- Status: Completed (contract freeze confirmed / docs-only)
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

## Stream E Completion Notes (2026-04-19)

### Phase 1 Read同期 + スコープ固定
- `AGENTS.md` Read Order（00→02）と本Issueを再読し、CE2は docs-only / contract-only lane で固定。
- 編集対象を `issue-CE2-low-risk-ai-assist.md` のみに固定し、codepath変更禁止を明記再確認。

### Phase 2 契約確認（CDC）
- CDC明文化:
  - Contract IDs: `CE2-PROPOSAL-IF / CE2-LIFECYCLE-IF / CE2-DRIFT-STOP-IF / CE2-NO-AUTOAPPLY-IF`
  - Required keys: `proposalId/diff/sourceBundleHash/rationale/status/reviewState`
  - Guardrail: auto-apply禁止、AIによる`human_reviewed`自動昇格禁止
- 上記契約は `02_Architecture/schemas.md` のCE2契約節と語彙衝突なし（再定義なし）を確認。

### Phase 3 Execute（CE2 lane）
- 実装追加は行わず、proposal-only契約の固定と停止条件（drift時`held`）を運用入力として確定。
- `sourceBundleHash=mock:<hash>` を許容する依存切断方針を維持。

### Phase 4 Verify（docs-check）
- docs-check として issue memo validator / unit test を実行し、契約語彙の構文整合を確認。

### Phase 5 Proceed/Stop
- Proceed 判定: ✅（契約衝突0 / 禁止経路混入0 / 再修復回数0）
- Stop 条件（3回超過）は未発火。
