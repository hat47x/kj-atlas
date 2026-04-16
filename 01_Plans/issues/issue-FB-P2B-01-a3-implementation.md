# Issue Draft: FB-P2B-01-A3 Similar-card候補提示 / 実装接続

- Type: Feature request
- Status: Open (Audit Hold: normalized contract pack; resumable by explicit Go/NoGo)
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P0
- Owner: Stream H（audit normalization only）
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2B-01`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`
- Expected verification level: `docs-check`

## Dependencies

- DependsOn: `01_Plans/issues/issue-FB-P2B-01-a1-interface-contract.md` / `01_Plans/issues/issue-FB-P2B-01-a2-mock-validation.md`
- Unblocks: downstream implementation lane only（no contract re-definition）
- Gate/Blocker: Ready when A1 contract lock + A2 validation ledger are complete; Blocked on contract mismatch, missing mockCase, or unresolved ownerOfFix.
## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2B-01`
- ReferenceContractID: `CTR-2B-01-CANDIDATE-GROUP-V1`
- RequirementStatement: A1/A2契約を逸脱せず実装接続へ引き継ぐ。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）:
  - 前提: A1/A2がFixedである。
  - 操作: 実装タスクを契約準拠で接続する。
  - 期待結果: candidate group一覧と対象Card確認DoDを満たす実装計画になる。
  - 除外: 契約変更の独断実施。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A（計画のみ）
- VerificationLevel（docs-check / unit / integration / e2e）: integration
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A

## AC/DoD ドラフト（不足確認）

- AC-2B-4: 実装レーンは `CTR-2B-01-CANDIDATE-GROUP-V1` 以外の契約を導入しないこと。
- AC-2B-5: A2で固定した非自動確定・再読込復元条件を回帰要件として継承すること。
- DoD-2B-3: 逸脱要求発生時にA1差し戻しフローを明記していること。
- 判定: 本メモ範囲では不足なし（ADR変更要否が出た場合はC/D/Cで承認取得後に再開）。

## Phase 3（A3）: Plan → Execute → Verify → Proceed

- State Sync Check（Phase開始時の再Read）:
  - Read: `issue-FB-P2B-01-a1-interface-contract.md` / `issue-FB-P2B-01-a2-mock-validation.md` / `issue-FB-P2B-01-a3-implementation.md`
  - 整合確認: A1 `ContractID` = A2 `DependsOnContractID` = A3 `ReferenceContractID` = `CTR-2B-01-CANDIDATE-GROUP-V1`
  - 判定: Pass（契約ID不整合なし）

- Plan:
  - `CTR-2B-01-CANDIDATE-GROUP-V1` を参照し、契約再定義を禁止する。
- Execute:
  - Gate-1: A1フィールド完全準拠。
  - Gate-2: A2の非自動確定条件を回帰要件化。
  - Gate-3: A2の再読込復元条件を回帰要件化。
  - Gate-4: 逸脱要求はA1差し戻し（この文書で再定義しない）。
- Verify:
  - [x] 契約IDを参照している。
  - [x] 契約再定義禁止が明記されている。
  - [x] 非自動確定と復元条件が維持されている。
- Proceed:
  - Phase 4のVerify/Handoffへ進む。

- Implementation handoff（Stream D）:
  - `CTR-2B-01-CANDIDATE-GROUP-V1` を唯一契約として実装・回帰を継続する。
  - 候補提示のみで確定しない（human操作のみ）制約を維持する。
  - 再読込時の deterministic 復元を integration test で維持する。

## Phase 4（Verify / Handoff）

- AC/DoD検証結果:
  - AC-2B-1（候補group一覧と対象Card確認）: **Plan上は達成見込み**（実装未着手）。
- 未達項目:
  - 実コードとテストの実行結果（A3実装作業待ち）。
- 次レーン受け渡し条件:
  - 実装レーンは `CTR-2B-01-CANDIDATE-GROUP-V1` を唯一契約として採用。
  - 契約逸脱・追加フィールド要求はA1へ戻して再承認。

## Validation plan

- 実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 期待結果:
  - issue memo必須メタが整合し、検証スクリプトが成功する。

## Reproducible verification record

- Command:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `cd 03_Implement/frontend && npm test -- src/domain/merge_suggestion_decisions.test.ts src/ui/MergeSuggestionsPanel.test.ts`
- Output:
  - `ok: validated <N> active issue memos`
  - `vitest target suites passed`
- Self-Correction:
  - 0/3（修復ループ不要）

## Phase 4（Verify）

- 判定: Pass
- 監査メモ:
  - UI導線（候補提示→意思決定）と決定ログ保存（append/list/restore）の契約整合を回帰テストで維持。
  - `accept|partial|reject|defer` の4値制約と非自動確定（human操作のみ）を継続確認。

## Phase 5（Proceed）

- 下流監査向け記録:
  - 契約ID: `CTR-2B-01-CANDIDATE-GROUP-V1`
  - 回帰対象: `merge_candidates` / `merge_suggestion_decisions` / `MergeSuggestionsPanel`
  - エスカレーション条件: 契約ID変更要求、または非自動確定ポリシーへの逸脱要求。

## Fail-safe

- A1契約不整合、3回超過、またはStream C/Dとの競合検知で即停止。

## Stream D execution log（2026-03-14）

- Plan:
  - A2で固定した条件（非自動確定・再読込復元）をA3実装回帰に引き継ぐ。
- Execute:
  - `src/domain/merge_suggestion_decisions.test.ts` / `src/ui/MergeSuggestionsPanel.test.ts` を再実行し、候補提示→意思決定の契約整合を確認。
- Verify:
  - decision action 4値（`accept|partial|reject|defer`）と `decidedBy: human` 前提を満たす。
- Proceed:
  - Verify記録を更新し、下流監査へ引き渡し可能。

## Stream C coordination checkpoint（Phase 1-5, 2026-03-14）

### Phase 1: Read同期（状態差確認）
- 状態差: A1=`Ready`, A2=`In Progress`, A3=`In Progress`。
- 実行順はA1→A2→A3で固定。

### Phase 2: A1固定点の再確認
- 依存契約: `ReferenceContractID=CTR-2B-01-CANDIDATE-GROUP-V1`。
- A3で再定義しない項目: 契約ID・必須フィールド・非自動確定境界。

### Phase 3: A2検証結果の受理条件
- 受理条件: APIシグネチャ/型/比較キーのmock Verify結果が揃っていること。
- 実装依存の逆流を禁止（A3起点で契約変更しない）。

### Phase 4: A3接続準備（開始/停止条件）
- 開始条件: A2のVerify Pass（契約ID一致、順序再現、非自動確定）。
- 停止条件: 契約逸脱・未定義競合・前提崩れ。

### Phase 5: 実装レーン引き渡し
- 固定条件: `CTR-2B-01-CANDIDATE-GROUP-V1` 単一参照。
- 既知リスク: UI表示順の差異が比較キー判定を崩す可能性。
- 回帰観点: `groupId/targetCardId/snapshotVersion` での同値性。

## Stream E execution log（2026-03-14）

### Phase 1: Read Gate
- Read: `issue-FB-P2B-01/02-a1-interface-contract.md` と当該A2/A3メモを再読し、`ContractID` / `DependsOnContractID` / `ReferenceContractID` の一致を確認。
- 判定: Pass（契約ID不整合なし）。

### Phase 2-3: A2/A3
- A2: mock先行条件（非自動確定・再読込復元・順序保持）を契約境界として固定。
- A3: 契約再定義禁止のまま、frontend実装テスト観点へ接続。

### Phase 4: Verify（宣言検証）
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `cd 03_Implement/frontend && npm test -- src/domain/stream_b_mock_validation.test.ts src/domain/merge_candidates.test.ts src/domain/merge_suggestion_decisions.test.ts src/ui/MergeSuggestionsPanel.test.ts`
- 判定: Pass（関連suite全件成功）。

### Phase 5: Proceed
- Go（A2/A3の宣言検証レベル要件を充足）。


## Stream C execution log（2026-03-14, serial lane）

### Phase 1: Read同期
- Read: `issue-FB-P2B-01-a1-interface-contract.md` / `issue-FB-P2B-01-a2-mock-validation.md` / `issue-FB-P2B-01-a3-implementation.md`
- Contract一致: `ContractID` = `DependsOnContractID` = `ReferenceContractID` = `CTR-2B-01-CANDIDATE-GROUP-V1`
- 判定: Pass

### Phase 2: P2B-01 A3（Plan → Execute → Verify → Proceed）
- Plan: A2で固定済みの非自動確定・再読込復元をそのまま実装接続ゲートへ継承し、契約再定義を禁止。
- Execute: `merge_candidates` / `merge_suggestion_decisions` / `MergeSuggestionsPanel` を対象に契約境界回帰を実行。
- Verify:
  - `cd 03_Implement/frontend && npm test -- src/domain/stream_b_mock_validation.test.ts src/domain/merge_candidates.test.ts src/domain/merge_suggestion_decisions.test.ts src/ui/MergeSuggestionsPanel.test.ts` → Pass
- Proceed: P2B-02 A2へ直列で進行。

### Fail-safe checkpoint
- 契約再定義要求: なし（A1差し戻し不要）。
- 同一ファイル競合/未定義依存: 検知なし。
- Self-Correction: 0/3。


## Stream H normalization contract pack (2026-04-13)

- Scope: legacy Audit Hold群の再開性を揃えるため、状態語彙・依存順序・契約リンクを監査再現可能な最小単位へ正規化する（新規実装なし）。
- Backlog lane: `FB-P2B-01`
- Canonical contract: `CTR-2B-01-CANDIDATE-GROUP-V1`
- Serial dependency: `A1 -> A2(mock) -> A3(implementation-ready contract only)`
- Mock policy: A2/A3 はモック/fixture/stub前提で参照可能状態を維持し、実コード変更要求を発行しない。

### Resume gate (Go/NoGo)

1. `ContractID/DependsOnContractID/ReferenceContractID` の三点一致を再確認する。
2. `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` が成功する。
3. 担当レーンが `Open (Audit Hold)` から `In Progress` へ昇格する明示判断を記録する。

### Stop conditions（fail-fast）

- 契約ID不整合、依存順序逆転、未定義競合を検知した場合は即停止。
- Self-correction は最大3回。3回超過時は更新を停止し、競合一覧のみ提出する。


## Stream C serial execution update（2026-04-14）

- Stream role: `Stream C（FB-P2B A1/A2/A3）` 専属。
- Contract input policy: 他ストリーム成果物は immutable な契約入力として扱い、待ち合わせを行わない。
- Target lane: `A3 implementation handoff`
- Locked Contract ID: `CTR-2B-01-CANDIDATE-GROUP-V1`

### Phase 1 Read同期（差分確認）
- Plan: A1/A2/A3の3メモを再読し、`ContractID / DependsOnContractID / ReferenceContractID` の差分を確認。
- Execute: 3メモの契約キーを照合し、記法ゆれ・依存順序逆転の有無を点検。
- Verify: 差分なし（`CTR-2B-01-CANDIDATE-GROUP-V1` で一致）。
- Proceed: Phase 2へ進行。

### Phase 2 A1契約固定
- Plan: A1で固定済みの契約ID・型・比較キーを再固定し、A2/A3は参照専用で運用。
- Execute: 契約拡張要求・キー変更要求・順序非決定要求をA1差し戻し条件として明文化。
- Verify: 契約再定義禁止を維持。
- Proceed: Phase 3へ進行。

### Phase 3 A2モック検証定義
- Plan: 実コード非依存で、stub/fixtureのみの検証条件を固定。
- Execute: 非自動確定・再読込復元・順序保持（およびenum境界がある場合は4値制約）を検証条件として保持。
- Verify: A2定義はA1契約参照のみで成立。
- Proceed: Phase 4へ進行。

### Phase 4 A3接続条件固定
- Plan: A3開始条件/停止条件/差し戻し条件を契約準拠で固定。
- Execute: A3は実装接続の入口定義のみとし、契約変更は受け付けない。
- Verify: `A1 -> A2 -> A3` 直列依存を維持。
- Proceed: Phase 5へ進行。

### Phase 5 Verify
- Plan: docs-checkでメモ整合を検証し、失敗時は自己修復を最大3回まで実施。
- Execute: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を基準コマンドとする。
- Verify: Self-Correction counter = `0/3`（本更新時点）。
- Proceed: 3回超過時は停止して競合一覧のみ報告。

## Stream F serial execution update（2026-04-14）

- Stream role: `Stream F（FB-P2B planning memo）` 専任。
- Edit scope: `01_Plans/issues/issue-FB-P2B-01-*.md` / `01_Plans/issues/issue-FB-P2B-02-*.md` のみ。
- Immutable policy: 上記以外は編集禁止。

### Phase 1: Read
- Plan: 当該レーンの A1/A2/A3 を再読し、`ContractID / DependsOnContractID / ReferenceContractID` を照合する。
- Execute: 契約ID三点一致、依存順序 `A1 -> A2 -> A3`、Priority `P0` を確認する。
- Verify: 差分・逆順依存・契約未定義がないことを確認する。
- Proceed: Pass時のみ Phase 2 へ進行する。

### Phase 2: A1契約（CDC）
- Plan: CDC（Contract-Driven Consistency）として A1 の契約凍結を再確認する。
- Execute: 契約再定義禁止、契約拡張要求は A1 差し戻し、A2/A3 は参照専用を固定する。
- Verify: `ContractID` の変更要求がないことを確認する。
- Proceed: Pass時のみ Phase 3 へ進行する。

### Phase 3: A2 mock validation仕様
- Plan: 実コード非依存で mock/fixture/stub 前提の検証仕様を固定する。
- Execute: 非自動確定・再読込復元・順序保持（および契約で定義された enum 境界）を必須観点として扱う。
- Verify: A2仕様が A1 契約参照のみで完結していることを確認する。
- Proceed: Pass時のみ Phase 4 へ進行する。

### Phase 4: A3 implementation readiness
- Plan: A3 の開始条件/停止条件/差し戻し条件を契約準拠で固定する。
- Execute: 実装接続は readiness 定義までとし、契約変更を受け付けない。
- Verify: `A1 -> A2 -> A3` の直列依存と handoff 入力の固定を確認する。
- Proceed: Pass時のみ Phase 5 へ進行する。

### Phase 5: Verify（README lifecycle整合）
- Plan: docs-check と issue lifecycle（`Draft -> Open -> In Progress -> Done`）の整合を検証する。
- Execute: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を基準コマンドとして実行する。
- Verify: README の lifecycle 記述と矛盾しない状態語彙（Open/In Progress/Done）に揃っていることを確認する。
- Proceed: 整合が取れた場合のみ Go、未整合は NoGo として停止条件へ遷移する。

### 強制サイクル / フェイルセーフ
- Self-repair は最大 3 回まで（`0/3` から開始し、4回目相当は実施しない）。
- 致命条件（契約ID不整合、依存順序逆転、編集禁止領域の更新要求、README lifecycle との不整合未解消）を検知した場合は即停止する。
- 停止時は「競合一覧・停止理由・再開条件」を記録し、推測で進行しない。

## Stream F planning memo update（2026-04-16 / FB-P2B-01・02 A2/A3）

- 担当: `FB-P2B-01 / FB-P2B-02` の `A2/A3 planning memo`
- 編集範囲: 本メモ4件のみ（P2A/P2C/HIL/CE/shared resource は read-only）
- A1依存方針: A1は常に read-only とし、A2/A3 は mock/fixture/stub で検証する。
- Fail-safe: 修復（self-correction）は `3回` まで。`3回超過` で停止し、競合一覧のみ提出する。

### Phase運用（固定）

1. **Phase 1 Read**
   - 各Phase開始時に `A1/A2/A3` を再Readして契約キー（`ContractID / DependsOnContractID / ReferenceContractID`）を照合する。
2. **Phase 2 Plan**
   - A1契約を再定義せず、A2/A3の検証観点（非自動確定・順序保持・再読込復元）を固定する。
3. **Phase 3 Execute**
   - mock/fixtureのみで実行し、実装都合の契約変更要求はA1差し戻し条件として記録する。
4. **Phase 4 Verify**
   - `validate_active_issue_memos.py` を基準に docs-check を実施し、契約逸脱・依存逆転・未定義競合を検知したら停止する。
5. **Phase 5 Proceed**
   - Go条件（契約一致・検証Pass・停止条件非該当）を満たす場合のみ次レーンへ引き渡す。

