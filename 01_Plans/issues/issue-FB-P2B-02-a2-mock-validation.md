# Issue Draft: FB-P2B-02-A2 Manual assisted mergeフロー / モック検証

- Type: Feature request
- Status: Done
- Lifecycle: Done
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P0
- Owner: Stream D（FB-P2B + FB-P0 baseline lane）
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2B-02`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`
- Dependencies: `FB-P2B-02`
- Expected verification level: `docs-check`

## Dependencies

- DependsOn: `01_Plans/issues/issue-FB-P2B-02-a1-interface-contract.md`
- Unblocks: issue-FB-P2B-02-a3-implementation.md
- Gate/Blocker: Ready when A1 is Done/Fixed and mock GoNoGo is `M1/M2/M3=pass & M4=fail`; Blocked when A1 not fixed or ownerOfFix unresolved.
## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2B-02`
- DependsOnContractID: `CTR-2B-02-DECISION-LOG-V1`
- RequirementStatement: A1のdecision log契約をmock検証し、非自動確定・再読込復元を担保する。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）:
  - 前提: A1契約（`CTR-2B-02-DECISION-LOG-V1`）がFixedである。
  - 操作: 4アクションをmock appendし、restoreで復元検証する。
  - 期待結果: 自動確定なしで決定履歴が再読込で復元される。
  - 除外: 実コード変更（`03_Implement/**`）と運用文書更新（`04_Documentation/**`）。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A（計画のみ）
- VerificationLevel（docs-check / unit / integration / e2e）: integration
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A

## Phase 2（A2）: Plan → Execute → Verify → Proceed

- State Sync Check（Phase開始時）:
  - Read: `issue-FB-P2B-02-a1-interface-contract.md` / `issue-FB-P2B-02-a2-mock-validation.md` / `issue-FB-P2B-02-a3-implementation.md`
  - 整合確認: A1 `ContractID` = A2 `DependsOnContractID` = A3 `ReferenceContractID` = `CTR-2B-02-DECISION-LOG-V1`
  - 判定: Pass（契約ID不整合なし）

- Plan:
  - A1契約のみ依存でmock検証条件を固定し、契約拡張は行わない。
  - AC/DoD補完の適用として、非自動確定・順序復元・異常系除外の3条件を検証観点に固定する。
- Execute:
  - mock append順序: `accept -> partial -> reject -> defer`。
  - 非自動確定: append時に representative確定イベントを発生させない。
  - 再読込復元: 同一 `snapshotVersion` で `restore` は同順序同内容を返す。
  - 異常系: enum外 `action` は契約違反として復元対象外。
- Verify:
  - [x] A1契約ID依存が明記されている。
  - [x] 非自動確定条件が明記されている。
  - [x] 再読込復元条件が明記されている。
  - [x] stub/fixtureで検証継続可能。
  - [x] AC/DoD補完（4値制約・順序保持・契約拡張禁止）がA3入力条件として明記されている。
- Proceed:
  - A3へ `CTR-2B-02-DECISION-LOG-V1` を参照IDとして引き渡す。

## Validation plan

- 実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 期待結果:
  - issue memo必須メタが整合し、検証スクリプトが成功する。

## Reproducible verification record

- Command:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `cd 03_Implement/frontend && npm test -- src/domain/stream_b_mock_validation.test.ts src/domain/merge_suggestion_decisions.test.ts`
- Output:
  - `ok: validated <N> active issue memos`
  - `vitest target suites passed`
- Self-Correction:
  - 0/3（修復ループ不要）

## Phase 4（Verify）

- 判定: Pass
- 監査メモ:
  - `CTR-2B-02-DECISION-LOG-V1` の append順序（accept→partial→reject→defer）と restore再現性をfixtureで固定。
  - enum外 action を復元対象外にする契約境界をテストで確認。

## Phase 5（Proceed）

- 下流監査向け記録:
  - 契約ID: `CTR-2B-02-DECISION-LOG-V1`
  - 回帰対象: `stream_b_mock_validation` / `merge_suggestion_decisions`
  - エスカレーション条件: action enum拡張要求、または snapshotVersionの互換破壊。

## Fail-safe

- Self-Correctionは最大3回。超過時は停止して人間判断依頼。

## Stream C coordination checkpoint（Phase 1-5, 2026-03-14）

### Phase 1: Read同期（状態差確認）
- 状態差: A1=`Ready`, A2=`Open`, A3=`Open`。
- 実行順はA1→A2→A3で固定。

### Phase 2: A1固定点の再確認
- 依存契約: `DependsOnContractID=CTR-2B-02-DECISION-LOG-V1`。
- 未定義項目: なし。

### Phase 3: A2モック検証（実コード非依存）
- 先行固定対象:
  - APIシグネチャ: `append/list/restore`
  - 型: `MergeDecisionRecord`
  - 比較キー: `snapshotVersion`, append順序, `action` enum
- 実コード依存排除: stub/fixtureで検証。

### Phase 4: A3接続準備（開始/停止条件）
- 開始条件: A2 Verifyで4値制約・順序保持・非自動確定がPass。
- 停止条件: 契約逸脱・未定義競合・前提崩れ。

### Phase 5: 実装レーン引き渡し
- 固定条件: enum追加はA1差し戻し。
- 既知リスク: restore時の順序逆転。
- 回帰観点: append→restoreの同順序再現、enum外除外。

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

### Phase 3: P2B-02 A2（Plan → Execute → Verify → Proceed）
- Plan: mock先行で append/list/restore I/F と action 4値制約、順序保持、非自動確定を固定。
- Execute: `accept -> partial -> reject -> defer` の順でfixture検証し、enum外action除外を確認。
- Verify:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` → Pass
  - `cd 03_Implement/frontend && npm test -- src/domain/stream_b_mock_validation.test.ts src/domain/merge_suggestion_decisions.test.ts` → Pass
- Proceed: A3接続へ進行。

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
- Target lane: `A2 mock validation`
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

## Stream H execution update（2026-04-16 / FB-P2B-02 A2）

### Phase 1 Read
- 先頭Read: A1/A2/A3を再読し、契約IDキー一致を確認する。

### Phase 2 Plan
- A2はmock検証責務に限定し、A1契約の拡張・緩和を禁止する。

### Phase 3 Execute
- 4値制約・順序保持・非自動確定・restore再現を検証軸として固定する。

### Phase 4 Verify
- 依存順序 `A1 -> A2 -> A3` とFail-fast条件を確認する。

### Phase 5 Proceed
- 3回失敗で停止し、競合一覧のみ提出する。

## Stream C serial execution update（2026-04-16 / P2B-02 A2）

### Phase 1: Read同期（6ファイル）
- Read: `FB-P2B-01/02` のA1/A2/A3を再照合。
- Verify: `DependsOnContractID=CTR-2B-02-DECISION-LOG-V1` がA1/A3と一致（Pass）。

### Phase 2: A1契約（CDC）依存固定
- A2はA1契約参照のみ。`action` 4値・`snapshotVersion` 境界を改訂しない。

### Phase 3: A2モック検証計画固定
- Mock plan: `append -> list -> restore` をfixtureで検証。
- 必須観点: 非自動確定、append順序保持、enum外action除外。

### Phase 4: A3実装接続条件固定
- A3入力条件: `CTR-2B-02-DECISION-LOG-V1` 単一参照、auto-merge禁止。

### Phase 5: Verify / Proceed
- Verify command: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- Self-repair: `0/3`（未実施）。
- Proceed: Go（契約ドリフト未検知）。


## Stream F CDC fixed-cycle update（2026-04-17）

- Fixed rule: `CDC -> Plan -> Execute -> Verify -> Proceed`
- Repair cap: Self-correction is limited to 3 attempts; stop on the 4th equivalent attempt.

### CDC
- Depends-on contract re-check: `DependsOnContractID=CTR-2B-02-DECISION-LOG-V1`.
- Serial dependency re-check: `A1 -> A2 -> A3` only.
- Validation boundary re-check: mock/fixture/stub first, no implementation-side contract expansion.

### Plan
- Keep A2 as contract-conformance mock validation lane.
- Maintain fixed checks: action 4-value boundary, append order, non-auto-apply, restore determinism.

### Execute
- Re-state mock sequence baseline: `accept -> partial -> reject -> defer`.
- Re-state exclusion: unknown action values are contract violation and excluded from restore target.

### Verify
- Verification command: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`.
- Pass criteria: memo metadata and dependency references remain consistent with A1/A3.

### Proceed
- Go only when CDC and docs-check both pass.
- If failed, perform self-correction up to 3 times and stop with blocker list when exceeded.

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

## Stream E serial execution update（2026-04-17 / A2 mock validation lane）

### Phase 1: Read
- Plan: A1/A2/A3 を再読し、契約キーと依存順序を照合。
- Execute: `ContractID/DependsOnContractID/ReferenceContractID` 三点一致を確認。
- Verify: `CTR-2B-02-DECISION-LOG-V1` で一致（Pass）。
- Proceed: Phase 2へ進行。

### Phase 2: ADR CDC（Context / Decision / Consequences）
- Context: A2は実装非依存のmock検証レーンであり、契約拡張を許すとA3 handoffが不安定化する。
- Decision: A2は A1契約参照のみとし、検証対象を `4値制約 / 非自動確定 / restore順序一致` に固定する。
- Consequences: 新規 action 値・restore仕様変更要求は A1へ差し戻し、A2では扱わない。
- Verify: 設計変更要求なし（CDC整備のみ）。
- Proceed: Phase 3へ進行。

### Phase 3: Plan（AC/DoD不足の補完）
- gapType=AC: `agreementStatus=agreed` として、M1/M2/M3=pass・M4=fail を Go 条件へ固定。
- gapType=DoD: `agreementStatus=agreed` として、検証失敗時の自己修復上限 `3回` を明文化。

### Phase 4: Execute
- mock append順序 `accept -> partial -> reject -> defer` を維持。
- enum外 action は契約違反として復元対象外を維持。
- A3引き渡し値は `CTR-2B-02-DECISION-LOG-V1` のみ。

### Phase 5: Verify → Proceed
- docs-check基準: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- Self-Correction counter: `0/3`（本更新時点）。
- Proceed判定: Go（A2は契約参照型mock検証レーンとして継続可能）。

### Fail-safe checkpoint
- 3回超過 / 契約ドリフト / 依存逆転 / 競合検出で即停止する。

## Stream D serial execution update（2026-04-17 / A2）

### Phase 1: Read
- A1/A2/A3を再読し、`DependsOnContractID=CTR-2B-02-DECISION-LOG-V1` を再照合。

### Phase 2: ADR CDC（必要時）
- CDC追加は不要。A1契約への依存のみでA2検証を継続する方針を維持。

### Phase 3: Plan（AC/DoD補完）
- AC/DoD補完として `action` 4値、append順序、restore同順序、非自動確定を必須化。

### Phase 4: Execute（A1→A2→A3）
- A2 mock検証条件をA3 handoff入力（契約参照のみ）として固定。

### Phase 5: Verify（<=3回修復）
- 実行: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 結果: Pass。Self-Correction: `0/3`。

### Phase 6: Proceed
- Go（A3に `CTR-2B-02-DECISION-LOG-V1` と mock検証固定条件を引き渡し）。

## Stream I Done/Completed Audit (2026-04-23)
- 判定: 再オープン不要（Done/Completed/Closedの完了根拠と整合）。
- Related ADR/Spec: 参照先リンク切れなし（存在確認済み）。
- 重複Backlog整理提案: FB-P2B-02 は系列メモ複数運用（4件）。再オープンではなく、次回は親統合メモ1本＋派生メモ参照化を提案。

## Stream G serial execution update（2026-04-30）

- Stream role: `Stream G: FB-P2B lane (A1→A2→A3)` 専属。
- Fixed edit targets (no overlap policy):
  - `01_Plans/issues/issue-FB-P2B-02-a1-interface-contract.md`
  - `01_Plans/issues/issue-FB-P2B-02-a2-mock-validation.md`
  - `01_Plans/issues/issue-FB-P2B-02-a3-implementation.md`
- Conflict policy: Stream F とのファイル重複編集は実行しない（対象一覧を開始時固定）。

### Phase 1: interface-contract（Read同期）
- Read: A1/A2/A3の3メモを再読し、`ContractID / DependsOnContractID / ReferenceContractID` の三点一致を確認する。
- Verify: `CTR-2B-02-DECISION-LOG-V1` で一致し、依存順序 `A1 -> A2 -> A3` を維持する。

### Phase 2: mock-validation（Read同期）
- Read: A1契約本文とA2 mock条件を再読し、契約再定義禁止・4値制約・順序復元・非自動確定を確認する。
- Verify: mock/fixture/stub のみで検証可能な境界を維持する。

### Phase 3: implementation（Read同期）
- Read: A3 handoff 条件を再読し、`CTR-2B-02-DECISION-LOG-V1` 単一参照と差し戻し条件を確認する。
- Verify: 実装接続は契約準拠のみ、契約拡張要求はA1へ差し戻す。

### Phase 4: verify（Read同期）
- Read: Validation plan と Fail-safe を再読する。
- Execute: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を基準検証として実行する。
- Verify: Self-correction を最大3回までに制限し、3回超過または競合兆候検知時は停止して競合一覧のみ報告する。


## Stream C serial execution update（2026-04-30）

- Stream role: `Stream C専任（FB-P2Bのみ）`
- Edit scope: `03_Implement/frontend/src/canvas/*` / `03_Implement/frontend/src/domain/*` / `01_Plans/issues/issue-FB-P2B-*.md`
- Guardrail: 指定外ファイル編集禁止、自己修復は最大3回（超過時停止）。

### Phase 1: Read同期
- Read: `issue-FB-P2B-02-a1-interface-contract.md` / `issue-FB-P2B-02-a2-mock-validation.md` / `issue-FB-P2B-02-a3-implementation.md`
- Verify: `ContractID / DependsOnContractID / ReferenceContractID` が `CTR-2B-02-DECISION-LOG-V1` で一致。
- Proceed: Pass。

### Phase 2: a1契約明文化（Context / Decision / Consequences + 合意）
- Context: decision log 契約の揺れは監査再現性を毀損するため、A1固定値を再利用する。
- Decision: A2は `append/list/restore` と `accept|partial|reject|defer` 4値制約を参照専用で維持する。
- Consequences: 契約拡張要求はA1差し戻し。A2では契約再定義を行わない。
- Agreement: `agreementStatus=agreed`（A1固定契約に準拠）。

### Phase 3: a2モック検証
- Verify target: 非自動確定・順序保持・snapshot単位復元・enum境界。
- Command: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- Result: Pass（active issue memo整合）。

### Phase 4: a3実装
- Policy: 本レーンではA3への入力契約固定までを担当し、実装契約の変更は行わない。
- Handoff: A3は `CTR-2B-02-DECISION-LOG-V1` 単一参照、契約逸脱はA1差し戻し。

### Phase 5: Verify → Proceed
- Self-Correction counter: `0/3`
- Stop condition check: 契約不整合・依存逆転・指定外編集は未検知。
- Proceed: Go（次レーンへ引き渡し可）。
