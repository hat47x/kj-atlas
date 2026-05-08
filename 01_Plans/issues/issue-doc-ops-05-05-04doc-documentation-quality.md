# Issue Draft: DOC-OPS-05-05 01_Plans/documentation_quality.md のOpen化準備

- Type: Documentation quality
- Status: Draft
- Lifecycle: Draft
- Source Issue: N/A
- Priority: P2
- Owner: Stream J (DOC-OPS-05-05 Draft整備)
- Scope: `01_Plans/documentation_quality.md`（※本Issueではメモ整備のみ）
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `01_Plans/documentation_quality.md`, `01_Plans/adr/ADR-0023-doc-ops-04-readability-baseline.md`, `01_Plans/adr/ADR-0024-doc-ops-04-quality-gates-boundary.md`, `01_Plans/adr/ADR-0025-doc-ops-04-change-governance.md`, `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`
- Dependencies: なし（先行固定）
- Dependency status: `先行固定（他Issueの着手前提）`


## Fixed execution order（DOC-OPS-05 Stream I proposal-only）
- Step 1 (Gate-A): `DOC-OPS-05-05` を先行実行し、語彙・Gate・停止条件を基準化する。
- Step 2 (Gate-B): `DOC-OPS-05-06` を実行し、05-05で固定した語彙とGateを継承する。
- Step 3 (Gate-C): `DOC-OPS-05-07` を実行し、05-06確定後に監査ログ方針を整合させる。
- Cycle break rule: 後続Issueから先行Issueへの「完了前依存」を禁止し、逆参照は informational link のみ許可する。
- Stopper: Gate-A/B/C のいずれかで未解決競合が発生した場合、`ProceedDecision: Stop` で停止し次段へ進めない。

## Requirement meta I/F
- RequirementID: `DOC-OPS-05-05`
- RequirementStatement: 内部品質基準文書としての扱いを固定し、Open化審査に必要な判断情報を揃える。
- GoNoGoGate: Required
- VerificationLevel: docs-check
- DecisionStatus: Fixed

## Classification（Fixed）
- Decision: **Move internal**
- Basis: 内部審査用の品質統制基準であり、対外公開本文ではない。

## Phase Run（Plan→Execute→Verify→Proceed）

### Phase 1: Read同期（現状抽出と依存棚卸し）
- 現状:
  - 05-05 は `Move internal` 判定で統一済み。
  - Proceed は依存未確定のため `Hold` 継続が必要。
- 依存関係:
  - 05-06: 公開導線文書（Improve external）としての Open 判定要件。
  - 05-07: 検証ログ（Move internal）としての配置見直し判定要件。
- 棚卸し結果:
  - 3Issue 共通で `VerificationLevel: docs-check`、`ProceedDecision: Hold`、`self-correction <=3` を維持する必要がある。

### Phase 2: ADR（C/D/C）整合
- Context:
  - ADR-0023: 可読性基線（Audience / Goal / Non-goal / Outcome / 用語整合）を最低要件とする。
  - ADR-0024: docs-check を必須境界として扱い、CI拡張とは分離する。
  - ADR-0025: 変更統治・例外承認は責務分離し、停止条件を明示する。
- Decision:
  - 本Issueは品質ゲート目的・適用範囲・例外境界を **Issueメモ上で再読可能** に固定する。
  - 適用範囲は「Issueメモ整備のみ」。`04_Documentation/**` 本文改稿および実装変更は対象外。
  - 例外は「依存証跡未確定時の Hold 継続」のみを認め、Open化確定は行わない。
- Consequences:
  - 05-06/05-07との判定語彙不一致を抑止できる。
  - Open gate 判定時に必要な証跡欠落（Approval Record不足）を事前に検知できる。

### Phase 3: Plan（AC/DoD: 判定可能な品質評価軸）
- AC-1（可読性 / Readability）:
  - `Requirement meta I/F`、`Classification`、`Phase Run`、`Proceed tri-state` が1ファイル内で追跡可能。
- AC-2（一貫性 / Consistency）:
  - 05-06/05-07 と `Proceed/Hold/Stop`、`GoNoGoGate`、`VerificationLevel` の語彙が一致。
- AC-3（検証可能性 / Verifiability）:
  - docs-check 実施計画と `Approval Record` 5項目（日時/承認者/対象/判断/evidence）記録欄が存在。

- DoD-1:
  - 依存未確定時の判定を `ProceedDecision: Hold` で固定し、解除条件を明記。
- DoD-2:
  - `Self-Correction <=3` を明示し、4回目相当で停止（Stop）する。
- DoD-3:
  - Non-goals に「実装変更なし」「04_Documentation本文更新なし」を明記。

### Phase 4: Execute（本Issue Draft本文のみ更新）
- 実施内容:
  - Phase 1〜6 の直列フローを再編し、評価軸（可読性・一貫性・検証可能性）を AC/DoD に追加。
  - 05-06/05-07 と整合する判定語彙を固定。
  - Open候補化条件を `U1〜U3` として明文化。
- 非実施:
  - 05-06/05-07 への編集。
  - `04_Documentation/**` の本文更新。

### Phase 5: Verify（依存Issue整合とテスト可能性確認）
- 依存Issue整合:
  - 05-06/05-07 と `Dependency status: 未確定`、`ProceedDecision: Hold`、`docs-check必須` が矛盾しないこと。
- テスト可能性:
  - 下記 Validation plan で項目存在確認と体裁検証が可能。
- 判定:
  - **Hold維持**（依存証跡未確定のため）。

### Phase 6: Proceed（Open候補化条件と残課題）
- Open候補化条件:
  - U1: 05/06/07 で `ProceedDecision` 語彙が完全一致。
  - U2: 本Issueに `Approval Record` 5項目が記録済み。
  - U3: `Dependency status` が未確定以外へ更新され、根拠リンクが追記済み。
- 残課題:
  1. DOC-OPS-05 Open gate 判定証跡の確定待ち。
  2. 3Issue横断での再判定日時同期。
  3. Hold解除時の承認ログ追記責務者の明確化（ADR-0025責務境界に準拠）。

## Approval Record（Open化判定入力）
- 日時: `TBD`
- 承認者: `TBD`
- 対象: `DOC-OPS-05-05`
- 判断: `TBD (Go/NoGo)`
- Evidence: `TBD`

## Validation
- docs-check: **必須**
- unit/integration/e2e: **期待レベル定義のみ（非目標）**

### Validation plan（コマンド）
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-05-04doc-documentation-quality.md`
- `rg -n "Phase 1:|Phase 2:|Phase 3:|Readability|Consistency|Verifiability|Approval Record|ProceedDecision|Dependency status" 01_Plans/issues/issue-doc-ops-05-05-04doc-documentation-quality.md`
- `git diff --check -- 01_Plans/issues/issue-doc-ops-05-05-04doc-documentation-quality.md`

## Non-goals
- `03_Implement/**` の実装変更
- `04_Documentation/**` 本文改稿
- 05-06 / 05-07 Issue本文の編集
- unit/integration/e2e 実行結果の新規作成

## Proceed tri-state
- ProceedDecision: **Hold**
- Reason: `DOC-OPS-05` 依存確定証跡待ち。
- Proceed判定日: `2026-05-06`
- Stop条件: self-correction が4回目相当に到達、または05-06/05-07と矛盾し解消不能になった場合。

## Stream H Ready化 pass（2026-05-06 / DOC-OPS-05-05）

### Ready判定の固定化
- Ready gate（全件必須）:
  - [ ] RG-0505-1: AC-1/AC-2/AC-3 の証跡欄が埋まっている。
  - [ ] RG-0505-2: DoD-1/DoD-2/DoD-3 の判定結果（done/pending/hold）が記録されている。
  - [ ] RG-0505-3: Approval Record 5項目（日時/承認者/対象/判断/evidence）が記入済み。
  - [ ] RG-0505-4: 05-06/05-07 との `ProceedDecision` 語彙一致が確認済み。

### 品質ゲート（docs-check）
- Gate-D1: `validate_active_issue_memos.py` で本Issue単体検証が通る。
- Gate-D2: `rg` により `Readability/Consistency/Verifiability` の3軸記述が存在する。
- Gate-D3: `git diff --check` で整形異常がない。

### E2E導線の扱い
- 本Issueは内部品質基準（Move internal）であり、E2E実行手順本文の更新判断は `05-06` へ委譲。

### Proceed
- ProceedDecision: **Hold（Ready gate定義完了、依存証跡待ち）**
- Ready化状態: **判定基準はReady、Open化は未実施**

## Stream E Open化準備 pass（2026-05-07 / DOC-OPS-05-05）

### Phase 1 Start Re-read
- 対象再読: 本Issueのみを再読し、`Move internal` / `docs-check` / `ProceedDecision: Hold` を再確認。
- 依存再確認: 05-06/05-07 の依存証跡が未確定のため、Open gateは未成立。

### Phase 2 Plan（AC/DoD不足提案）
- AC/DoD不足提案（合意前提）:
  - 提案A: `Approval Record` に evidence link の保存先（issue comment / artifact）を明示する。
  - 提案B: `DoD-2` の self-correction 上限到達時の停止メッセージ定型を固定する。
- 合意状態: 本Draftでは「提案として記録」、依存確定時に反映可否を最終合意する。

### Phase 3 ADR明文化（C/D/C）
- Context: 内部品質基準を公開導線と混在させると判定責務が曖昧化する。
- Decision: `Move internal` を維持し、Open化判定は依存Issue同期完了まで実施しない。
- Consequences: 品質基準の内部統制を維持しつつ、誤公開リスクを抑制する。

### Phase 4 Execute（docs-only）
- 実施: 本Issueメモへの整備追記のみ。
- 非実施: `01_Plans/documentation_quality.md` 本文改稿、他Issue編集、実装変更。

### Phase 5 Verify
- 判定: `Hold` 維持（gate未成立）。
- self-correction: `1/3`（上限内）。
- 失敗時方針: 3回以内で修復、4回目相当は `Stop`。

### Phase 6 Proceed
- ProceedDecision: **Hold**
- Stop条件（再確認）:
  1. 依存Issueとの語彙不一致が解消不能。
  2. self-correction 4回目相当が必要。


## Stream F targeted quality uplift (2026-05-07)

### Read → Plan(AC/DoD補完) → Execute → Verify → Proceed
- Read: 本文の判定語彙（Go/NoGo, Proceed/Hold/Stop, pass/fail/blocked）と依存状態を再確認した。
- Plan: AC/DoD の不足項目を「単体再読で判定できるか」「docs-checkで検証できるか」に限定した。
- Execute: 本文の目的・非目的・停止条件を明示し、推測での gate確定を禁止した。
- Verify: docs-check 前提を維持し、自己修復上限を 3 回に固定した。
- Proceed: gate未確定事項は Hold 維持、Assumption/TODO を明示して停止する。

### AC/DoD delta（補完）
- AC-Delta-1: 判定語彙を 1 セット（Go/NoGo, Proceed/Hold/Stop, pass/fail/blocked）に固定。
- AC-Delta-2: 依存未確定時の扱いを `ProceedDecision: Hold` として明示。
- DoD-Delta-1: `self-correction <= 3` を超える場合は `Stop`。
- DoD-Delta-2: gate未確定事項は推測せず、TODO/Assumptionを残して停止。

### Stopper handling（推測禁止）
- TODO: `DOC-OPS-05` Open gate の最終承認証跡（日時/承認者/evidence link）確定待ち。
- TODO: 05-05/05-06/05-07 の Proceed 再判定日の同期。
- Assumption: 依存Issueの最終合意までは本Draftの分類（Move internal / Improve external）を暫定維持する。

## Stream M phase-sync pass（2026-05-07 / DOC-OPS-05-05）

### Phase 1: Read同期
- 対象限定: 本Issueメモのみ更新（docs-only）を再確認。
- 依存確認: 05-06/05-07 は承認証跡未確定のため `ProceedDecision: Hold` を維持。
- 語彙確認: `Go/NoGo` / `Proceed/Hold/Stop` / `pass/fail/blocked` / `self-correction <= 3` を固定語彙として再確認。

### Phase 2: Context / Decision / Consequences
- Context: 内部品質基準（Move internal）の判定情報は、Open導線文書と分離して管理しないと責務境界が曖昧になる。
- Decision: 本Issueは `Move internal` を維持し、Open化判定は依存証跡確定まで実施しない。
- Consequences:
  1. 内部品質基準の誤公開リスクを抑止できる。
  2. 05-06/05-07 とのProceed語彙不一致を事前に検知できる。
  3. Hold継続時の説明責務（理由・停止条件・再開条件）を明文化できる。

### Phase 3: Draft解除条件（品質ゲート / 証跡 / 責務）
- 品質ゲート:
  - Gate-M1: `validate_active_issue_memos.py` pass。
  - Gate-M2: `Classification` / `Dependency status` / `ProceedDecision` / `Approval Record` が記載済み。
  - Gate-M3: `git diff --check` pass。
- 証跡:
  - E1: Approval Record 5項目（日時/承認者/対象/判断/evidence）。
  - E2: 05-06/05-07 との Proceed 判定語彙一致ログ。
  - E3: docs-check 実行コマンドと結果記録。
- 責務:
  - System Owner: Go/NoGo判定と承認記録確定。
  - Platform Operator: docs-check実行結果の記録と追跡リンク管理。
  - Security Officer: Move internal 境界（公開除外）の最終確認。

### Phase 4: Verify（最大3回）
- Verify-1: 実施（本pass）。`Hold` 維持。
- Verify-2: 依存Issue更新後に再判定（予定）。
- Verify-3: 承認証跡確定後に最終再判定（予定）。
- 逸脱条件: 4回目相当の修正が必要になった場合は `ProceedDecision: Stop`。

## Stream L serial gate pass（2026-05-08 / Gate-A: DOC-OPS-05-05）

### Phase 1 Read
- Status/Lifecycle: `Draft / Draft` を再確認。
- Dependencies: `なし（先行固定）` だが、05-06/05-07 は後続依存として informational のみ許可。
- AC/DoD/Proceed 条件: `docs-check 必須`、`ProceedDecision: Hold`、`self-correction <= 3`、4回目相当は `Stop`。

### Phase 2 ADR/CDC
- Context: 本Issueは内部品質基準の判定情報を固定する起点Gate。
- Decision: Classification は `Move internal` 維持。未承認項目（Approval Record未記入）は `Hold` 維持。
- Consequences: 後続Gateが同一語彙（Go/NoGo, Proceed/Hold/Stop, docs-check）を継承できる。

### Phase 3 Plan
- AC/DoD 補完方針:
  - ACは `Readability / Consistency / Verifiability` の3軸で判定。
  - DoDは `依存未確定=Hold` と `self-correction上限` を停止条件として固定。
- 用語統一宣言: `Go/NoGo`、`Proceed/Hold/Stop`、`docs-check` を本Gateの固定語彙とする。

### Phase 4 Execute
- 実施: Gate-A対象（本ファイル）のみ更新。
- 非実施: 05-06/05-07 への波及編集。

### Phase 5 Verify
- docs-check観点: 必須キー（Requirement meta / Classification / Proceed tri-state / Validation）が本文内に存在。
- self-correction: `1/3`（上限内）。

### Phase 6 Proceed
- ProceedDecision: **Hold**
- 判定理由: Approval Record と依存証跡が未確定のため。
- Gate-A 終了判定: **Hold（Gate-B へは情報継承のみ、確定依存は作らない）**
