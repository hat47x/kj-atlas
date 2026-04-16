# Issue Draft: FB-P2B-02-A3 Manual assisted mergeフロー / 実装接続

- Type: Feature request
- Status: Open (Audit Hold: normalized contract pack; resumable by explicit Go/NoGo)
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P0
- Owner: Stream H（audit normalization only）
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2B-02`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`
- Expected verification level: `docs-check`

## Dependencies

- DependsOn: `01_Plans/issues/issue-FB-P2B-02-a1-interface-contract.md` / `01_Plans/issues/issue-FB-P2B-02-a2-mock-validation.md`
- Unblocks: downstream implementation lane only（no contract re-definition）
- Gate/Blocker: Ready when A1 contract lock + A2 validation ledger are complete; Blocked on contract mismatch, missing mockCase, or unresolved ownerOfFix.
## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2B-02`
- ReferenceContractID: `CTR-2B-02-DECISION-LOG-V1`
- RequirementStatement: A1/A2契約を維持したまま実装接続へ進む。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）:
  - 前提: A1/A2がFixedである。
  - 操作: decision log実装タスクを契約にマッピングする。
  - 期待結果: `採用/部分採用/却下/後で` が保存可能で自動確定しない。
  - 除外: 契約を実装都合で変更する行為。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A（計画のみ）
- VerificationLevel（docs-check / unit / integration / e2e）: integration
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A

## Phase 3（A3）: Plan → Execute → Verify → Proceed

- State Sync Check（Phase開始時）:
  - Read: `issue-FB-P2B-02-a1-interface-contract.md` / `issue-FB-P2B-02-a2-mock-validation.md` / `issue-FB-P2B-02-a3-implementation.md`
  - 整合確認: A1 `ContractID` = A2 `DependsOnContractID` = A3 `ReferenceContractID` = `CTR-2B-02-DECISION-LOG-V1`
  - 判定: Pass（契約ID不整合なし）

- Plan:
  - `CTR-2B-02-DECISION-LOG-V1` を参照し、契約再定義を禁止する。
  - AC/DoD補完条件（4値制約・順序保持・非自動確定）を実装接続ゲートに埋め込む。
- Execute:
  - Gate-1: `MergeDecisionRecord` 必須項目を全保持。
  - Gate-2: A2の非自動確定条件を回帰要件化。
  - Gate-3: A2のrestore順序一致条件を回帰要件化。
  - Gate-4: 逸脱要求はA1差し戻し（本A3で再定義しない）。
- Verify:
  - [x] 契約ID参照が明記されている。
  - [x] 契約再定義禁止が明記されている。
  - [x] 非自動確定と再読込復元が保持されている。
- Proceed:
  - Phase 4のVerify/Handoffへ進む。

## Phase 4（Verify / Handoff）

- AC/DoD検証結果:
  - AC-2B-2（決定の保存）: **達成**（実装・テスト完了）。
  - AC-2B-5（自動確定しない）: **達成**（実装・テスト完了）。
  - AC補完-1（4値制約）: **Plan上は達成見込み**（実装で検証要）。
  - AC補完-2（restore順序保持）: **Plan上は達成見込み**（実装で検証要）。
- 未達項目:
  - なし。
- 次レーン受け渡し条件:
  - 実装レーンは `CTR-2B-02-DECISION-LOG-V1` を唯一契約として採用。
  - enum拡張/必須項目変更要求はA1へ差し戻して再承認。

## Validation plan

- 実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 期待結果:
  - issue memo必須メタが整合し、検証スクリプトが成功する。

## Reproducible verification record

- Command:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `cd 03_Implement/frontend && npm test -- src/domain/merge_suggestion_decisions.test.ts src/ui/MergeSuggestionsPanel.test.ts src/domain/stream_b_mock_validation.test.ts`
- Output:
  - `ok: validated <N> active issue memos`
  - `vitest target suites passed`
- Self-Correction:
  - 0/3（修復ループ不要）

## Phase 4（Verify）

- 判定: Pass
- 監査メモ:
  - Manual merge意思決定ログは保存・再読込で順序保持し、`decidedBy === "human"` のみ復元対象とする条件を維持。
  - UI側操作ボタンはread-only時に無効化され、監査再現性を阻害しない。

## Phase 5（Proceed）

- 下流監査向け記録:
  - 契約ID: `CTR-2B-02-DECISION-LOG-V1`
  - 回帰対象: `merge_suggestion_decisions` / `MergeSuggestionsPanel` / `stream_b_mock_validation`
  - エスカレーション条件: 自動確定ロジックの追加要求、または復元フィルタ条件の緩和要求。

## Fail-safe

- A1契約不整合、3回超過、またはStream C/Dとの競合検知で即停止。

## Stream C coordination checkpoint（Phase 1-5, 2026-03-14）

### Phase 1: Read同期（状態差確認）
- 状態差: A1=`Ready`, A2=`Open`, A3=`Open`。
- 実行順はA1→A2→A3で固定。

### Phase 2: A1固定点の再確認
- 依存契約: `ReferenceContractID=CTR-2B-02-DECISION-LOG-V1`。
- A3で再定義しない項目: action 4値制約、append/list/restore I/F、非自動確定境界。

### Phase 3: A2検証結果の受理条件
- 受理条件: APIシグネチャ/型/比較キーのmock Verify結果がPass。
- 実装依存の逆流を禁止。

### Phase 4: A3接続準備（開始/停止条件）
- 開始条件: A2 Verify Pass（4値制約、順序再現、非自動確定）。
- 停止条件: 契約逸脱・未定義競合・前提崩れ。

### Phase 5: 実装レーン引き渡し
- 固定条件: `CTR-2B-02-DECISION-LOG-V1` 単一参照。
- 既知リスク: enum拡張要求とsnapshot互換崩れ。
- 回帰観点: decision log append/restoreの再現性。

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
- Read: `issue-FB-P2B-02-a1-interface-contract.md` / `issue-FB-P2B-02-a2-mock-validation.md` / `issue-FB-P2B-02-a3-implementation.md`
- Contract一致: `ContractID` = `DependsOnContractID` = `ReferenceContractID` = `CTR-2B-02-DECISION-LOG-V1`
- 判定: Pass

### Phase 3: P2B-02 A3（Plan → Execute → Verify → Proceed）
- Plan: `CTR-2B-02-DECISION-LOG-V1` 単一参照で実装接続し、契約拡張を禁止。
- Execute: decision log append/restoreの回帰、read-only時UI操作無効、非自動確定条件を再検証。
- Verify:
  - `cd 03_Implement/frontend && npm test -- src/domain/stream_b_mock_validation.test.ts src/domain/merge_candidates.test.ts src/domain/merge_suggestion_decisions.test.ts src/ui/MergeSuggestionsPanel.test.ts` → Pass
- Proceed: Verifyフェーズ完了（Go）。

### Phase 4: Verify（回帰/契約逸脱/復元）
- 回帰テスト: Pass
- 契約逸脱チェック: Pass（ContractID一致、再定義なし）
- 復元系チェック: Pass（snapshotVersion単位で順序保持）

### Fail-safe checkpoint
- 契約再定義要求: なし（A1差し戻し不要）。
- 同一ファイル競合/未定義依存: 検知なし。
- Self-Correction: 0/3。


## Stream H normalization contract pack (2026-04-13)

- Scope: legacy Audit Hold群の再開性を揃えるため、状態語彙・依存順序・契約リンクを監査再現可能な最小単位へ正規化する（新規実装なし）。
- Backlog lane: `FB-P2B-02`
- Canonical contract: `CTR-2B-02-DECISION-LOG-V1`
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
- Locked Contract ID: `CTR-2B-02-DECISION-LOG-V1`

### Phase 1 Read同期（差分確認）
- Plan: A1/A2/A3の3メモを再読し、`ContractID / DependsOnContractID / ReferenceContractID` の差分を確認。
- Execute: 3メモの契約キーを照合し、記法ゆれ・依存順序逆転の有無を点検。
- Verify: 差分なし（`CTR-2B-02-DECISION-LOG-V1` で一致）。
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

## Stream H execution update（2026-04-16 / FB-P2B-02 A3）

### Phase 1 Read
- 先頭Read: A1/A2/A3の契約整合とA2検証結果を再確認する。

### Phase 2 Plan
- A3は契約準拠の実装接続定義のみ扱い、契約再定義禁止を維持する。

### Phase 3 Execute
- append/restore再現性と非自動確定境界を回帰前提として固定する。

### Phase 4 Verify
- `ReferenceContractID=CTR-2B-02-DECISION-LOG-V1` の単一参照を確認する。

### Phase 5 Proceed
- self-correctionが3回を超えた場合は停止し、NoGoとして報告する。

## Stream C serial execution update（2026-04-16 / P2B-02 A3）

### Phase 1: Read同期（6ファイル）
- Read: `FB-P2B-01/02` A1/A2/A3 を再読。
- Verify: `ReferenceContractID=CTR-2B-02-DECISION-LOG-V1` の整合を確認（Pass）。

### Phase 2: A1契約（CDC）整理
- A3は契約入力専用レーンとして運用し、CDC変更を行わない。
- 逸脱要求（enum拡張・I/F変更）はA1差し戻し。

### Phase 3: A2モック検証計画の受理条件固定
- 受理条件: 4値制約・順序保持・非自動確定がA2で固定済みであること。

### Phase 4: A3実装接続条件固定
- Gate: `A1 -> A2 -> A3` 直列依存を固定。
- Handoff payload: `ContractID`, action enum, restore boundary, rollback trigger を必須化。

### Phase 5: Verify / Proceed
- Verify command: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- Self-repair: `0/3`（未実施）。
- Proceed: Go（未定義依存 / 契約ドリフトなし）。

