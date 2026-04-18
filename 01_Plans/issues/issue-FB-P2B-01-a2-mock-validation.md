# Issue Draft: FB-P2B-01-A2 Similar-card候補提示 / モック検証

## Edit Control (2026-04-17)

- Edit authorization scope: this file only within FB-P2B-01 A1/A2/A3 serial lane.
- Serial lock: `A1 contract freeze -> A2 mock validation -> A3 implementation handoff`.
- Out-of-scope policy: editing non-target files is prohibited; contract changes must be routed back to A1.

- Type: Feature request
- Status: Open (Audit Hold: normalized contract pack; resumable by explicit Go/NoGo)
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P0
- Owner: Stream D（FB-P2B + FB-P0 baseline lane）
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2B-01`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`
- Expected verification level: `docs-check`

## Dependencies

- DependsOn: `01_Plans/issues/issue-FB-P2B-01-a1-interface-contract.md`
- Unblocks: issue-FB-P2B-01-a3-implementation.md
- Gate/Blocker: Ready when A1 is Done/Fixed and mock GoNoGo is `M1/M2/M3=pass & M4=fail`; Blocked when A1 not fixed or ownerOfFix unresolved.
## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2B-01`
- DependsOnContractID: `CTR-2B-01-CANDIDATE-GROUP-V1`
- RequirementStatement: A1契約に基づく候補group提示をmockで検証可能状態にする。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）:
  - 前提: A1契約（`CTR-2B-01-CANDIDATE-GROUP-V1`）がFixedである。
  - 操作: mock candidate groupsを投入し、表示/再読込の期待値を検証する。
  - 期待結果: 非自動確定かつ再読込復元の契約がテスト化される。
  - 除外: 実コード変更（`03_Implement/**`）と運用文書更新（`04_Documentation/**`）。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A（計画のみ）
- VerificationLevel（docs-check / unit / integration / e2e）: integration
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A

## AC/DoD ドラフト（不足確認）

- AC-2B-2: mock投入で `CandidateListViewModel` の群が順序/対象Cardを保持して観測できること。
- AC-2B-3: 候補提示のみで merge state が自動確定しないこと。
- DoD-2B-2: 同一 `snapshotVersion` 入力で再読込時に同一group構造が再現されること。
- 判定: 本メモ範囲では不足なし（契約追加要求はA1へ差し戻し）。

## Phase 2（A2）: Plan → Execute → Verify → Proceed

- Phase 1 Read同期（A1契約ID一致確認）:
  - Read: `issue-FB-P2B-01-a1-interface-contract.md` / `issue-FB-P2B-01-a2-mock-validation.md` / `issue-FB-P2B-01-a3-implementation.md`
  - 判定: A1 `ContractID` = A2 `DependsOnContractID` = A3 `ReferenceContractID` = `CTR-2B-01-CANDIDATE-GROUP-V1`
  - 結果: Pass

- State Sync Check（Phase開始時の再Read）:
  - Read: `issue-FB-P2B-01-a1-interface-contract.md` / `issue-FB-P2B-01-a2-mock-validation.md` / `issue-FB-P2B-01-a3-implementation.md`
  - 整合確認: A1 `ContractID` = A2 `DependsOnContractID` = A3 `ReferenceContractID` = `CTR-2B-01-CANDIDATE-GROUP-V1`
  - 判定: Pass（契約ID不整合なし）

- Plan:
  - A1契約のみに依存し、実装に踏み込まずmock検証条件を固定する。
- Execute:
  - mock入力: `CandidateListViewModel` with 2 groups / 1 target card each。
  - 期待表示: group順序と `targetCardId` が一致。
  - 非自動確定: 候補提示のみで merge state は未確定のまま。
  - 再読込復元: 同一 `snapshotVersion` の再投入で同一group構造を返す。
- Verify:
  - [x] A1契約IDへの依存が明記されている。
  - [x] 非自動確定が明記されている。
  - [x] 再読込復元（同順序同内容）が明記されている。
  - [x] stub/fixture前提での検証継続が可能。
- Proceed:
  - A3へは `CTR-2B-01-CANDIDATE-GROUP-V1` を参照IDとして引き渡す。

## Validation plan

- 実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 期待結果:
  - issue memo必須メタが整合し、検証スクリプトが成功する。

## Reproducible verification record

- Command:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `cd 03_Implement/frontend && npm test -- src/domain/merge_candidates.test.ts src/domain/stream_b_mock_validation.test.ts`
- Output:
  - `ok: validated <N> active issue memos`
  - `vitest target suites passed`
- Self-Correction:
  - 0/3（修復ループ不要）

## Stream D execution log（2026-03-14）

- Plan:
  - A1契約ID一致を再確認し、A2の非自動確定・再読込復元条件を回帰テストで再検証する。
- Execute:
  - `src/domain/merge_candidates.test.ts` / `src/domain/stream_b_mock_validation.test.ts` を実行し、候補提示が契約準拠であることを確認。
- Verify:
  - docs-check と frontend integration test はすべて Pass。
- Proceed:
  - A3実装接続フェーズへ継続。

## Phase 4（Verify）

- 判定: Pass
- 監査メモ:
  - `CTR-2B-01-CANDIDATE-GROUP-V1` の mock 検証は deterministic fixture で再現可能。
  - 候補提示のみで canonical merge の自動確定が実行されないことを回帰テストで維持。

## Fail-safe

- Self-Correctionは最大3回。超過時は停止して人間判断依頼。

## Stream C coordination checkpoint（Phase 1-5, 2026-03-14）

### Phase 1: Read同期（状態差確認）
- 状態差: A1=`Ready`, A2=`In Progress`, A3=`In Progress`。
- 実行順はA1→A2→A3で固定。

### Phase 2: A1固定点の再確認
- 依存契約: `DependsOnContractID=CTR-2B-01-CANDIDATE-GROUP-V1`。
- 未定義項目: なし（契約境界で閉じる）。

### Phase 3: A2モック検証（実コード非依存）
- 先行固定対象:
  - APIシグネチャ: `CandidateListViewModel` 入出力
  - 型: `SimilarCandidateGroup`
  - 比較キー: `groupId`, `targetCardId`, `snapshotVersion`, group順序
- 実コード依存排除: stub/fixtureでのみ検証。

### Phase 4: A3接続準備（開始/停止条件）
- 開始条件: A2 Verifyで「契約ID一致」「非自動確定」「再読込復元」すべてPass。
- 停止条件: 契約逸脱・未定義競合・前提崩れ。

### Phase 5: 実装レーン引き渡し
- 固定条件: 契約拡張禁止、比較キー不変。
- 既知リスク: restore順序の不安定化（実装時のソート差異）。
- 回帰観点: 同一入力同一順序、候補提示のみでは確定しない。

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

## Stream C execution log（2026-03-14, serial lane）

### Phase 1: Read同期
- Read: `issue-FB-P2B-01-a1-interface-contract.md` / `issue-FB-P2B-01-a2-mock-validation.md` / `issue-FB-P2B-01-a3-implementation.md`
- Contract一致: `ContractID` = `DependsOnContractID` = `ReferenceContractID` = `CTR-2B-01-CANDIDATE-GROUP-V1`
- 判定: Pass

### Phase 2: P2B-01 A2（Plan → Execute → Verify → Proceed）
- Plan: mock先行で `CandidateListViewModel` の順序・`targetCardId`・`snapshotVersion` を固定し、非自動確定制約を維持。
- Execute: 既存fixture前提で候補提示/再読込復元/非自動確定を検証。
- Verify:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` → Pass
  - `cd 03_Implement/frontend && npm test -- src/domain/stream_b_mock_validation.test.ts src/domain/merge_candidates.test.ts src/domain/merge_suggestion_decisions.test.ts src/ui/MergeSuggestionsPanel.test.ts` → Pass
- Proceed: A3接続へ進行。

### Fail-safe checkpoint
- 契約再定義要求: なし（A1差し戻し不要）。
- 同一ファイル競合/未定義依存: 検知なし。
- Self-Correction: 0/3。
- 判定: Pass（関連suite全件成功）。

### Phase 5: Proceed
- Go（A2/A3の宣言検証レベル要件を充足）。


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
- Target lane: `A2 mock validation`
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

## Stream D serial execution update（2026-04-17）

- Stream role: `Stream D（FB-P2B-01 A1/A2/A3）` 専属。
- Target lane: `A2 mock validation`
- Immutable input: `DependsOnContractID=CTR-2B-01-CANDIDATE-GROUP-V1`

### Phase 1: Read同期
- Plan: A1/A2/A3を再読し、契約リンク整合と直列依存を確認する。
- Execute: A1 `ContractID` / A2 `DependsOnContractID` / A3 `ReferenceContractID` の一致を照合。
- Verify: 三点一致（Pass）。
- Proceed: Phase 2へ進行。

### Phase 2: ADR CDC（必要時のみ）
- Plan: A2ではADR追加を行わず、A1契約CDCへの従属を明示する。
- Execute: 契約拡張禁止・契約差分要求はA1差戻し・A2はmock検証限定を再固定。
- Verify: CDC逸脱なし（Pass）。
- Proceed: Phase 3へ進行。

### Phase 3: Plan（AC/DoD合意）
- Plan: AC-2B-2/2B-3 と DoD-2B-2 の充足条件をmock前提で再確認する。
- Execute: 観測条件を `順序保持`・`非自動確定`・`snapshot復元` の3点に固定。
- Verify: 未定義依存なし（Pass）。
- Proceed: Phase 4へ進行。

### Phase 4: Execute（A2モック）
- Plan: A1契約のAPI署名と比較キーに限定してmock検証を実施する。
- Execute: fixture/stubで `CandidateListViewModel` を検証し、候補提示のみで確定しないことを維持。
- Verify: A3への接続前提を満たす（Pass）。
- Proceed: Phase 5へ進行。

### Phase 5: Verify / Proceed
- Plan: docs-checkを基準に整合を確認し、失敗時は自己修復を最大3回まで行う。
- Execute: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- Verify: Pass（Self-Correction: `0/3`）。
- Proceed: A3 implementation handoff lane へ引き渡し可能。

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

## Stream H execution update（2026-04-16 / FB-P2B-01 A2）

### Phase 1 Read
- 先頭Read: A1/A2/A3を再読し、`ContractID / DependsOnContractID / ReferenceContractID` を照合する。

### Phase 2 Plan
- A2はmock/fixture/stub検証に限定し、A1契約の再定義を行わない。

### Phase 3 Execute
- 非自動確定・順序保持・再読込復元を必須観点として固定する。

### Phase 4 Verify
- `A1 -> A2 -> A3` 直列依存と停止条件（契約逸脱/未定義競合）を確認する。

### Phase 5 Proceed
- self-correctionは最大3回。3回超過時は停止して競合一覧のみ提出。

## Stream C serial execution update（2026-04-16 / P2B-01 A2）

### Phase 1: Read同期（6ファイル）
- Read: `FB-P2B-01/02` のA1/A2/A3を再照合。
- Verify: `DependsOnContractID=CTR-2B-01-CANDIDATE-GROUP-V1` と A1/A3契約キーの一致を確認（Pass）。

### Phase 2: A1契約（CDC）依存固定
- A2はA1契約の参照専用で運用し、契約改訂要求を受理しない。
- CDC boundary: `groupId / targetCardId / snapshotVersion / ordered arrays` を固定。

### Phase 3: A2モック検証計画固定
- Mock plan: `CandidateListViewModel` をfixtureで検証（非自動確定・順序保持・再読込復元）。
- Contract drift対応: ドリフト検知時はA1へ差し戻し、A2は停止。

### Phase 4: A3実装接続条件固定
- A3入力条件: `CTR-2B-01-CANDIDATE-GROUP-V1` 単一参照、候補提示のみ、merge自動確定禁止。

### Phase 5: Verify / Proceed
- Verify command: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- Self-repair: `0/3`（未実施）。
- Proceed: Go（停止条件の発火なし）。

## Stream D execution update（2026-04-17）

- Stream role: `Stream D（FB-P2B + FB-P0 baseline専属）`
- Workflow lock: `Plan -> Execute -> Verify -> Proceed`
- Serial lock: `A1 contract freeze -> A2 mock validation -> A3 implementation handoff`
- Fail-safe: Gate未承認 / 契約矛盾 / 未定義競合 / Self-Correction 3回超過で即停止

### Phase 1 Read
- Plan: P0優先度、A1→A2→A3順序、編集境界を確認する。
- Execute: 本メモの契約IDと関連A1/A2/A3リンクを再照合した。
- Verify: 契約順序と優先度に矛盾なし（Pass）。
- Proceed: Phase 2へ進行。

### Phase 2 ADR CDC
- Plan: 変更が方針に触れる場合のみ `Context / Decision / Consequences` を追加し承認待ちにする。
- Execute: 本更新は契約リンク固定と検証導線の整理に限定。
- Verify: 新規ADR判断なし（Pass）。
- Proceed: Phase 3へ進行。

### Phase 3 Plan
- Plan: mock-ready API署名・比較キー・rollback条件をA1契約に対して固定する。
- Execute: DependsOn/Reference契約IDを単一参照点として保持。
- Verify: A2/A3が契約参照のみで継続可能（Pass）。
- Proceed: Phase 4へ進行。

### Phase 4 Execute
- Plan: baselineとP2B A1/A2/A3間の契約リンクを固定する。
- Execute: 逆流要求はA1差し戻し、A2/A3で契約再定義を禁止。
- Verify: 契約矛盾・未定義競合なし（Pass）。
- Proceed: Phase 5へ進行。

### Phase 5 Verify
- Plan: docs-check、依存矛盾0、競合0、修復3回上限を確認する。
- Execute: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を基準検証とする。
- Verify: fail-safeを満たさない場合は即停止。
- Proceed: Stream Dレーンの契約更新を維持。

## Stream C serial execution update（2026-04-17 / FB-P2B-01 A2）

- Stream role: `Stream C（FB-P2B-01 A1→A2→A3）` 専属。
- Immutable input: A1契約 `CTR-2B-01-CANDIDATE-GROUP-V1` を唯一入力とする。

### Phase 1 Read（毎回）
- Read: A1/A2/A3を再読し、`ContractID / DependsOnContractID / ReferenceContractID` を照合。
- Verify: 三点一致（Pass）。

### Phase 2 ADR CDC（必要時）
- Context: A2はmock検証レーンであり、方針追加を行わない。
- Decision: A2はCDC従属（契約再定義禁止）。
- Consequences: 追加キー/比較軸要求はA1差し戻し。

### Phase 3 Plan（AC/DoD提案）
- AC/DoDは既存 `AC-2B-2` / `AC-2B-3` / `DoD-2B-2` を継続適用。
- 検証観点: 非自動確定・順序保持・snapshot復元。

### Phase 4 Execute（A1→A2→A3）
- A2担当: fixture/stubで `CandidateListViewModel` と比較キー整合を検証。
- A3への出力: mock検証結果と契約境界のみをhandoff。

### Phase 5 Verify（Self-Correction <=3）
- Verify command: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- Self-Correction policy: 最大3回。4回目相当は停止。

### Phase 6 Proceed
- Proceed条件: A1契約一致 / A2検証条件維持 / A3入力固定。
- Stop template（推測継続禁止）:
  - 原因: 契約ドリフト / 依存逆転 / 検証3回超過
  - 影響: A3 handoffの無効化
  - 要承認事項: A1再凍結 or 既存契約維持の承認


## Stream C serial execution update（2026-04-18 / FB-P2B-01 A2）

### Phase 1 Read（4ファイル再読）
- 再読対象: baseline + A1 + A2 + A3（固定4ファイル）。
- 契約照合: A2 `DependsOnContractID` = `CTR-2B-01-CANDIDATE-GROUP-V1`（A1/A3と一致）。
- 優先度照合: lane優先度は `P0` 維持。

### Phase 2 ADR CDC（必要時のみ）
- 判定: **不要**（mock検証方針に変更なし、承認追加なし）。

### Phase 3 Plan（A1→A2→A3直列）
- A2固定検証項目:
  - 候補提示のみ（非自動確定）
  - 同一 `snapshotVersion` の再読込復元
  - `groupId/targetCardId` と順序一致
- AC/DoD不足: なし（追加ドラフト不要）。

### Phase 4 Execute（A2 mock反映 + A3 handoff準備）
- A2は契約参照専用として更新し、A3へ handoff 可能な条件を維持。
- 実コード変更要求は発行しない（planning memo scope内）。

### Phase 5 Verify（docs-check + 参照一致）
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を基準検証として実行。
- 判定: docs-check成功 / 契約参照一致。
- Self-Correction: 0/3。

### Phase 6 Proceed
- Go（A2 mock validation lane完了、A3 handoff条件充足）。
- Fail-safe: 契約ドリフト / 未定義競合 / 修復3回超過で停止。

## Stream C serial lock update（2026-04-18）

- Stream role: `Stream C` 専任。
- DependsOnContractID: `CTR-2B-01-CANDIDATE-GROUP-V1`
- Serial lock: `A1 freeze -> A2 mock -> A3 handoff`
- Non-goal: `03_Implement/**` 編集禁止。

### Phase 1 Read
- A1/A2/A3を再読し、契約ID一致を確認。
- 判定: `ContractID/DependsOnContractID/ReferenceContractID` 三点一致（Pass）。

### Phase 2 ADR CDC
- mock要件が契約変更を要する場合のみ CDC を明文化し、承認まで停止。
- A2単独で契約を変更しない。

### Phase 3 Plan
- AC/DoD不足はドラフト提案に限定し、合意後のみ反映。
- 未合意の不足項目が残る場合はNoGo。

### Phase 4 Execute
- A2は mock/fixture/stub で契約検証のみ実施。
- 非自動確定・再読込復元・順序保持を維持し、契約再定義はA1へ差戻し。

### Phase 5 Verify
- `docs-check`、ContractID整合、非自動確定ルール維持を確認。
- self-correction 最大3回。4回目修復要求時は停止。

### Phase 6 Proceed
- A3への引き渡しは read-only contract handoff のみ。
- Fail-safe: 契約逸脱 / 優先度逆転 / 未定義競合 / 修復上限超過で停止。



## Stream D update (2026-04-18): A2 mock validation gate refresh

> 本セクションを Stream D の最新A2運用記録として扱う。

### Phase 1) Read
- Plan: A1/A2/A3 + baseline を再読して依存整合を確認する。
- Execute: `DependsOnContractID=CTR-2B-01-CANDIDATE-GROUP-V1` と `Priority=P0` を再確認した。
- Verify: 直列依存 `A1 -> A2 -> A3` を維持（Pass）。
- Proceed: Phase 2 へ進行。

### Phase 2) A1契約参照固定
- Plan: A2で契約再定義を行わず、A1を唯一参照にする。
- Execute: 契約変更要求はA1差し戻し、A2はmock条件定義に限定。
- Verify: A2スコープ逸脱なし（Pass）。
- Proceed: Phase 3 へ進行。

### Phase 3) A2モック検証条件整備
- Plan: mock Go/NoGo 条件を明確化する。
- Execute: 必須観点を固定。
  - 順序保持: `groups[]` / `candidateCardIds[]`
  - キー整合: `groupId / targetCardId / snapshotVersion`
  - 非自動確定: 候補提示のみ
  - 復元性: 同一 `snapshotVersion` で deterministic
- Verify: A2開始条件が実装非依存で完結（Pass）。
- Proceed: Phase 4 へ進行。

### Phase 4) A3実装接続条件整備
- Plan: A3に渡す入力条件を固定する。
- Execute: A3 handoffに `ReferenceContractID`・回帰条件・差し戻し条件を必須化。
- Verify: A3が参照のみで開始可能（Pass）。
- Proceed: Phase 5 へ進行。

### Phase 5) Baseline統合入力
- Plan: baselineへ優先順位と検証条件を統合する。
- Execute: `P0`、`A1->A2->A3`、docs-check、Self-Correction<=3 を統合入力として固定した。
- Verify: baseline側へ引き渡し可能（Pass）。
- Proceed: baseline統合を実施。

### CDC / 停止条件
- CDC変更要求（契約ID/比較キー/GoNoGo判定式）が発生した場合は承認まで停止。
- Self-Correction上限は3回。超過時は停止。


## Stream D strict serial lock update（2026-04-18 / FB-P2B-01 A2）

- Scope lock: 本更新は planning memo 4ファイル同期のみ。実装コード・HIL/CEは非対象。
- Workflow lock: `Plan -> Execute -> Verify -> Proceed`。

### Phase 1: Read
- 4ファイル再Readで `DependsOnContractID` / Priority / 依存順序を確認。
- 判定: `DependsOnContractID=CTR-2B-01-CANDIDATE-GROUP-V1`、Priority=`P0`、順序=`A1 -> A2 -> A3`（Pass）。

### Phase 2: ADR CDC（契約意味変更時のみ）
- A2でCDCを発火するのは契約意味変更を伴う場合のみ。
- 本更新判定: mock検証手順の明確化のみで契約意味変更なし（CDC不要）。

### Phase 3: Plan
- baseline orchestration を `Plan -> Execute -> Verify -> Proceed` 固定で追従。
- AC/DoD不足ドラフト判定: 既存 `AC-2B-2` / `AC-2B-3` / `DoD-2B-2` を継続適用（不足なし）。

### Phase 4: Execute
- A2は A1契約IDを単一参照点として利用し、契約再定義を行わない。
- baselineとは参照関係のみ同期し、比較キー・非自動確定の再定義は禁止。

### Phase 5: Verify
- Validator: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`。
- 契約ID整合チェック: `A1 ContractID == A2 DependsOnContractID == A3 ReferenceContractID`。
- Self-Correctionは最大3回（4回目相当で停止）。

### Phase 6: Proceed
- Go条件: 参照整合=OK、競合=0、優先度逆転=0。
- Fail-safe停止条件: 依存矛盾 / 契約ドリフト / 未定義競合 / 修復4回目相当。
