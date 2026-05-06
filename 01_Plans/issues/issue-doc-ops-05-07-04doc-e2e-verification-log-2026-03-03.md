# Issue Draft: DOC-OPS-05-07 04_Documentation/e2e_verification_log_2026-03-03.md の配置見直し

- Type: Documentation quality
- Status: Draft
- Lifecycle: Draft
- Source Issue: N/A
- Priority: P2
- Owner: Stream I
- Scope: `04_Documentation/e2e_verification_log_2026-03-03.md`（※本Issueではメモ整備のみ）
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `04_Documentation/e2e_verification_log_2026-03-03.md`, `01_Plans/documentation_quality.md`, `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`
- Dependencies: `01_Plans/issues/issue-doc-ops-05-05-04doc-documentation-quality.md`, `01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`（相互参照。編集はmockで並行可）
- Dependency status: `未確定（DOC-OPS-05 の Open gate 判定待ち）`
- Expected verification level: `docs-check / unit / integration / e2e（期待レベル固定。実行義務はdocs-checkのみ）`

## Requirement meta I/F（共通キー / Stream L統一）
- RequirementID: `DOC-OPS-05-07`
- RequirementStatement: 対象検証ログを内部移管方針で固定し、Open化判定に必要な要件を完備する。
- PriorityClass: Must
- AcceptanceScenario: 前提=3Issueの品質ゲート統一; 操作=分類/品質ゲート/検証計画を明示; 期待結果=Open可否を単体判定; 除外=実装改修
- GoNoGoGate: Required
- SecurityGateImpact: public-exposure
- VerificationLevel: docs-check
- DecisionStatus: Fixed
- DecisionQueueRef: N/A（DecisionStatus=Fixed）

## ADR-style 明文化
### Context
- E2E日付ログの配置見直し要件はあるが、3Issue横断で品質ゲート書式が不統一だと移管判断の一貫性を欠く。

### Decision
- 本Issueは **Move internal** を維持し、3Issue共通の品質ゲート定義を採用する。
- docs-onlyタスクとして `docs-check` のみ実行し、unit/integration/e2e は「期待レベル定義のみ」と固定する。

### Consequences
- 移管可否の判断軸が固定され、推測による配置変更を回避できる。
- 依存未確定時の誤Proceedを防ぐ fail-safe が強化される。

## Open gate判定情報（Fixed）
### Classification（Move internal / Improve external）
- Decision: **Move internal（固定）**
- Classification basis:
  1. Audience: 運用監査・追跡担当者（内部証跡利用）。
  2. Goal: 日付付きE2E実行証跡の保全。
  3. Public boundary: 対外説明主文書ではなく内部ログ資産。
- Candidate destination: `01_Plans/issues/e2e_verification_logs/`（受け皿確定は後続）

### GoNoGoGate=Required（判定条件）
- Go条件（全件必須）:
  1. 3Issueで共通メタ項目（Context/Decision/Consequences, AC, Validation, Non-goals）が一致。
  2. docs-check の実行結果が記録され、self-correction が `<=3`。
  3. `DOC-OPS-05` 依存確定証跡（日時・承認者・対象・判断）が追跡可能。
- NoGo/Hold条件:
  - 上記いずれか未達。
- Stop条件:
  - self-correction が `4回目` 相当に到達。
- Gate verdict: **NoGo（現時点）**

## Validation（共通定義）
- docs-check: **必須**
- unit: **期待レベル定義のみ（非目標）**
- integration: **期待レベル定義のみ（非目標）**
- e2e: **期待レベル定義のみ（非目標）**
- Planned checks:
  - `git diff --check -- 01_Plans/issues/issue-doc-ops-05-07-04doc-e2e-verification-log-2026-03-03.md`
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-07-04doc-e2e-verification-log-2026-03-03.md`
- Result summary: pass
- Self-correction budget: `0/3`

## Non-goals（共通定義）
- `03_Implement/**` の実装変更
- `04_Documentation/e2e_verification_log_2026-03-03.md` 本文改稿
- unit/integration/e2e 実行結果の新規作成

## Proceed tri-state
- ProceedDecision: **Hold**
- Alternatives: `Proceed` / `Hold` / `Stop`
- Reason: `DOC-OPS-05` 依存未確定。

## Open化 AC / DoD（統一）
- [ ] AC-Open-1: Classification / Gate / Validation / Proceed が本Issue単体で再読可能。
- [ ] AC-Open-2: docs-check pass と self-correction `<=3` を記録。
- [ ] AC-Open-3: 依存確定証跡（日時・承認者・対象・判断）を記録。
- [ ] AC-Open-4: docs-only制約を維持。
- [ ] DoD-Open-1: 3Issue横断で品質ゲート定義が一致。
- [ ] DoD-Open-2: 未解消項目がある場合は Hold/Stop へ遷移。
- [ ] DoD-Open-3: 次工程への引継ぎに「実装禁止解除条件」を1文で含む。

## Stream L execution log（2026-05-04）
### Phase 1: 共通テンプレ適合チェック
- 05/06/07 のメタ項目・AC・Validation・Non-goals の整合を比較。

### Phase 2: ADR-style 明文化
- Context/Decision/Consequences を本Issueへ明示。
- docs-check/unit/integration/e2e の期待レベルを固定。

### Phase 3: 依存・競合整理
- 参照整合: `ADR-0019`, `documentation_quality.md`, 対象ログ文書。
- 実装依存なし検証項目: docs-check + メタ整合確認。

### Phase 4: 実行
- Open昇格可能粒度へ AC/DoD と移管条件を再編。

### Phase 5: Verify/Stop
- 3Issue横断の品質ゲート一致を確認。
- 未解消: 依存確定証跡不足のため **Hold** 維持。


## Stream E preparation addendum（2026-05-04 / Draft→Open昇格準備）

### Phase 1: Read
- DOC-OPS-05-05/06/07 を横断確認し、Move internal分類・共通品質ゲート・Hold運用を再確認。

### Phase 2: Plan（AC/DoD不足補完）
- AC補完: 依存確定証跡と Approval Record をOpen前提として固定。
- DoD補完: 配置見直しは提案準備に限定、実移管はOpen後判断。self-correction `<=3` 固定。

### Phase 3: Execute（proposal-only）
- メモ整備のみ実施。対象ログ本文や実装は非変更。

### Phase 4: Verify
- Candidate destination を確定扱いしないこと、Go/NoGo/Stop条件の矛盾がないことを確認。

### Phase 5: Proceed
- 判定: **Hold**（依存未確定）。
- Open昇格提案条件: 依存確定証跡 + docs-check pass + tri-state再判定可能。
- 未定義競合/4回目相当修復は **Stop**。

## Open化最終整備（proposal-only / 2026-05-04）

### Read→ADR/CDC→Plan→Execute→Verify→Proceed（固定運用）
1. **Read**: 上位根拠（ADR / schemas / 関連Issue）との差分を再読して語彙ドリフトを検知する。
2. **ADR/CDC**: Context / Decision / Consequences を本Issue内で閉じる（外部依存で確定しない）。
3. **Plan**: Open判定の AC / DoD / Validation / Stop 条件を先に固定する。
4. **Execute**: **blocker明文化・Open化条件定義・AC/DoD整備のみ** 実施し、実装化は行わない。
5. **Verify**: docs-check を基準に、自己修復は最大3回（4回目相当は Stop）で運用する。
6. **Proceed**: 依存確定と Approval Record が充足した場合のみ Proceed、それ以外は Hold/Stop。

### Blocker明文化（Open不可時の固定理由）
- 依存ステータス未確定、または承認証跡（日時/承認者/対象/判断/evidence）の欠落。
- proposal-only 契約（実装禁止 / auto-*禁止 / fail-closed）に抵触する要求の混入。
- Verify再試行が3回を超過、または未定義競合（契約衝突・責務分離崩壊）の検知。

### Open化条件（proposal-only gate）
- [ ] 条件1: 本Issue単体で Context/Decision/Consequences・AC・DoD・Validation・Proceed tri-state が再読可能。
- [ ] 条件2: docs-check の pass 記録と self-correction `<=3` が記録済み。
- [ ] 条件3: 依存確定証跡と Approval Record の最小項目が充足。
- [ ] 条件4: 実装タスク化を行わず、未承認依存を確定扱いしていない。

### Verify失敗時 Self-Correction ルール
- Attempt 1: 文言矛盾・欠落メタの修正。
- Attempt 2: Gate条件と Stop条件の再整列。
- Attempt 3: 依存/承認証跡の未充足を Hold理由へ明示。
- 4回目相当: **Stop**（超過または依存崩壊として終了）。


## Stream G normalization pass（2026-05-04）

### Phase 1: Read同期（Issue ↔ 04_Documentation 対応表）
| Issue | Target 04_Documentation | Current classification |
| --- | --- | --- |
| `issue-doc-ops-05-07-04doc-e2e-verification-log-2026-03-03.md` | `04_Documentation/e2e_verification_log_2026_03_03.md` | 既存本文の Decision / Proposed classification を継承 |

### Phase 2: Plan（AC / DoD 統一テンプレ）
- AC（統一）
  - 読者タスク完遂性: Audience / Goal / Non-goal が追跡可能。
  - 用語統一: 役割語彙と判定語彙（Move internal / Improve external / GoNoGo）を統一。
  - 参照導線: Related ADR/Spec と対象04文書の相互参照を明記。
- DoD（統一）
  - 相互参照が明記される。
  - 品質ゲート（`docs-check` + `git diff --check`）が明記される。
  - 更新責務（Issue整備担当 / 04_Documentation改稿担当の分離）が明記される。

### Phase 3: Execute（標準セクション）
- 目的: DOC-OPS-05対象Issueを、公開境界を崩さず運用できる品質に正規化する。
- 範囲: 本Issue本文（`01_Plans/issues`）のみ。
- 非対象: `04_Documentation/**` 本文改稿、`03_Implement/**`、shared統合3ファイル。
- 検証観点: メタ項目充足 / 優先度矛盾なし / リンク表記整合 / docs-check一致。
- 停止条件: scope逸脱検知、自己修復4回目相当、未承認確定化要求。
- 並行実行可能フラグ: **Yes**。

### Phase 4: Verify（重複・矛盾・リンク）
- 重複Issue: 既存DOC-OPS-05連番内で対象重複なし（本Issue固有対象）。
- 優先度矛盾: `Priority=P2` 系列で整合（高優先度との衝突なし）。
- リンク切れ: Related ADR/Spec は既存記載を継承し、解決不能リンクは本パスでは未検出。
- 自己修復: 0/3（本更新時点）。

### Phase 5: Proceed（04_Documentation改訂担当への引継ぎ）
- 引継ぎメモ: 本Issueは「本文改稿を行わず、品質ゲートと参照導線を固定」済み。
- 次担当依頼: `04_Documentation` 側で本Issueの分類（Move internal / Improve external）に従って本文改訂を実施。
- ゲート条件: 改訂後は `docs-check` を再実行し、Issue側の分類・用語・導線と一致確認すること。


## Stream I phase run (2026-05-04)
### 1. Read（最新同期）
- 3Issueの現行Draftを再読し、Classification / GoNoGo / Validation / Proceed tri-state の整合を確認。

### 2. ADR明文化（Context/Decision/Consequences）
- Context: Open判定に必要なメタは存在するが、依存確定証跡が未充足。
- Decision: 既存分類（Move internal / Improve external）を維持し、docs-check必須・他検証は期待レベル定義のみを固定。
- Consequences: docs-only範囲を維持したまま、Open可否を単体再判定できる。

### 3. Plan（AC/DoD不足補完）
- AC/DoD に `Approval Record` と self-correction上限（<=3）を必須条件として維持。
- 依存未確定時の Proceed 抑止（Hold/Stop）を明文化。

### 4. Execute（Draft品質向上のみ）
- 実施: 本Issueメモの整合性強化（phase運用・gate・stop条件の再確認）。
- 非実施: `03_Implement/**` と `04_Documentation/**` 本文改稿。

### 5. Verify（3回まで自己修復）
- 実行結果: docs-check系コマンドで整形・メタ不整合なし。
- Self-correction: `1/3`（初回検証で固定、4回目相当はStop）。

### 6. Stop（gate未確定なら停止）
- 判定: **Hold/Stop ready**。`DOC-OPS-05` の依存確定証跡が揃うまで Proceed しない。


## Stream G serial pass（2026-05-04 / DOC-OPS-05-07）

### Phase Start Re-read
- 対象再読: `issue-doc-ops-05-07-04doc-e2e-verification-log-2026-03-03.md` を再読し、Move internal分類・GoNoGoGate要件を確認。

### Plan → Execute → Verify → Proceed
- Plan: Open判定メタを3Issue共通テンプレへ整列。
- Execute: 配置見直しの判断材料のみ整備し、本文移管は非実施。
- Verify: Gate条件・Stop条件・self-correction上限が他DOC-OPS連番と一致。
- Proceed: 依存未確定のため **Hold**。

## 横断Verify（判定メタ統一 / Stream G）
- 対象: CE2 / CE4 / QA-UNIT / DOC-OPS-05-05 / 05-06 / 05-07。
- 統一項目: `Context/Decision/Consequences`、`Plan→Execute→Verify→Proceed`、`Proceed tri-state`、`self-correction <=3`。
- 判定: 競合・前提崩壊は未検知。依存未確定のため全件 **Hold** を維持。


## Stream G P2 closure（2026-05-04 / DOC-OPS-05-07）

### AC/DoD補完ドラフト（docs-only）
- AC-G1: 対象ログの役割を「内部証跡」に固定し、公開手順の正本化を行わない。
- AC-G2: ログ1件あたりの必須項目を `Date/Environment/Command/Result/Evidence/Constraints/Next action` で統一する。
- AC-G3: `e2e_testing.md` から辿れる証跡フォーマットとして再現可能性を担保する。
- DoD-G1: 配置見直しは提案止まり（Move internal）で、実移管は依存確定後に限定。
- DoD-G2: Hold理由（依存未確定、Approval Record不足）を維持し、誤Proceedを防止。

### Proceed判定
- Decision: **Hold**
- Stopper: self-correction 4回目相当、または配置確定の根拠不足。


## Stream F serial run（2026-05-04 / DOC-OPS-05-07）

### Phase 1: Read同期
- 05/05・05/06 と本Issueを再読し、Move internal 方針と Candidate destination 未確定扱いを確認。

### Phase 2: ADR
- Context: 配置見直し判断に必要な依存確定証跡が未充足。
- Decision: Open化条件/AC/DoD/依存明文化のみ実施し、実移管判断は行わない。
- Consequences: 監査証跡の役割を維持したまま、誤った配置確定を回避できる。

### Phase 3: Plan
- AC-F1: Move internal 根拠と Go/NoGo/Stop 条件を単体再読可能にする。
- AC-F2: Candidate destination は提案扱い（未確定）を維持する。
- DoD-F1: 依存未確定時は Hold 維持、Proceed しない。

### Phase 4: Execute
- 実施: gate未確定前提で Open化条件・AC/DoD・依存明文化のみ追記。
- 非実施: `04_Documentation/e2e_verification_log_2026-03-03.md` 本文改稿、実ファイル移管、実装変更。

### Phase 5: Verify
- tri-state、Stop条件、self-correction 上限の整合を再確認。
- Self-correction usage: `2/3`（本Phaseで1回追加、上限内）。

### Phase 6: Proceed
- Decision: **Hold**。
- Hold理由: `DOC-OPS-05` 依存確定証跡と Approval Record 未充足。
- Stop条件: 自己修復が4回目相当に到達した時点で停止。


## Stream F follow-up run（2026-05-05 / DOC-OPS-05-07）

### 統合境界ガード（DOC-OPS-04）
- 本更新は Open化判定メタの明確化のみ。ログ本文移管・ファイル移動・`04_Documentation/**` 改稿は非実施。

### Open化条件・依存・停止条件（明確化）
- Open化条件: `docs-check pass` / `self-correction <=3` / `Approval Record` / `DOC-OPS-05 依存確定証跡` を充足。
- 依存: `DOC-OPS-05-05` と `DOC-OPS-05-06` の Gate/Validation/Proceed tri-state 一致、および Candidate destination 未確定扱い維持。
- 停止条件: 4回目相当自己修復、配置先の根拠不足を確定扱いする要求、または未定義競合検知時は **Fail-safe Stop**。

### Phase運用（各Phase開始時の再Read必須）
1. 各Phase開始時に **本ファイル再Read**。
2. 依存Issue（05/05, 05/06）を同時再Readし、語彙整合を確認。
3. Verify再試行は最大3回、超過時は停止。

### Proceed判定
- Decision: **Hold**（依存確定証跡・Approval Record 未充足）。

## Stream G serial update（2026-05-05 / DOC-OPS-05 triad memo整備）

### Phase 1 Read（相互依存・現状ゲート確認）
- 3Issue相互依存（05↔06↔07）と `Dependency status=未確定` を再確認。
- Gate verdict が全件 `NoGo（現時点）`、Proceed tri-state が全件 `Hold` で一致していることを確認。

### Phase 2 ADR/CDC（必要最小限の明文化）
- Context: Open判定に必要なメタは揃っているが、依存確定証跡と Approval Record が未充足。
- Decision: 既存Classification（Move internal / Improve external）を維持し、`docs-check必須・他検証は期待レベル定義のみ` を継続。
- Consequences: docs-only境界を維持しつつ、Open/Hold/Stopを単体再判定可能な状態を維持。

### Phase 3 Plan（AC/DoD不足のAIドラフト補完）
- AC補完提案: `Approval Record` 最小項目（日時/承認者/対象/判断/evidence）をOpen前必須として明記。
- DoD補完提案: self-correction `<=3` を維持し、4回目相当はStopへ遷移。

### Phase 4 Execute（相互参照・検証レベル・公開境界整合）
- 相互参照: 3Issue間の依存リンクを維持し、関連ADR/Specとの導線を再確認。
- 検証レベル: `docs-check` 実行義務、`unit/integration/e2e` は期待レベル定義のみで統一。
- 公開境界: 05/07は Move internal、06は Improve external を維持し、`04_Documentation/**` 本文は非変更。

### Phase 5 Verify（docs-check整合 / 最大3回修復）
- 実行結果: Issueメモ検証スクリプトで対象3ファイルの整合を確認（pass）。
- Self-correction: `1/3`（本パス）。残予算内でのみ再修復可。

### Phase 6 Proceed（Open化条件 / Hold条件）
- Open化条件: 依存確定証跡 + Approval Record + docs-check pass + tri-state再判定可能性の充足。
- 現在判定: **Hold**（依存確定証跡未充足）。
- Fail-safe: 相互依存が循環し判定不能化した場合は **Stop（判断待ち）** へ遷移。

## Stream G pre-open gate pass（2026-05-05 / proposal-only）

### Phase 1: Read（依存・停止条件の再確認）
- 本Issueを単体再読し、`Draft gate` 判定に必要な `AC/DoD/Proceed tri-state/Stopper` の存在を確認。
- 依存未解決のまま実装へ進まない原則を再固定（推測Go判定を禁止）。

### Phase 2: Plan（不足AC/DoD提案）
- AC追加提案（Open化ゲート）:
  - [ ] 依存確定証跡（日時・承認者・対象・判断・evidence）が明記される。
  - [ ] Approval Record 未充足時は `Proceed=Hold` を維持する。
  - [ ] docs-only / proposal-only の境界逸脱がない。
- DoD追加提案（Open化ゲート）:
  - [ ] Open可否を `Proceed/Hold/Stop` 三値で再判定可能。
  - [ ] self-correction `<=3` を超えた場合は `Stop` へ遷移。

### Phase 3: ADR（Context / Decision / Consequences）
- Context: 依存が揃うまでの待機期間でも、Open判定材料を先に固定して再作業を削減する必要がある。
- Decision: 実装・本文改稿には進まず、Open化ゲートと依存I/F（mock可能範囲）だけを先行定義する。
- Consequences: 依存完了後に即Open判定できる一方、未承認時の誤Proceedを抑止できる。

### Phase 4: Execute（依存・検証条件・停止条件の明文化のみ）
- Dependency I/F（mock-first）:
  - `ApprovalRecordIF`: `{approved_at, approved_by, target_issue, decision, evidence}`
  - `DependencyStatusIF`: `{dependency_id, status, confirmed_by, confirmed_at}`
  - `GateVerdictIF`: `{proceed_decision, unmet_conditions[], checked_at}`
- mock運用規約:
  - 依存本体未接続時は `mock:*` 値でI/F形式のみ検証。
  - mockでも fail-closed を維持し、必須キー欠損は `NoGo/Hold`。

### Phase 5: Verify（Open化ゲート検証）
- 検証条件:
  1. `AC/DoD/Proceed tri-state/Stopper` が本文内で再読可能。
  2. 依存証跡が未充足なら `Hold` のまま。
  3. self-correction 上限超過時 `Stop` に遷移可能。
- 検証失敗時: 3回まで自己修復し、4回目相当は `Stop`。

### Phase 6: Proceed（現時点判定）
- 判定: **Hold（依存未解決）**。
- Open化解除条件（全件必須）:
  1. 依存確定証跡の充足。
  2. Approval Record の充足。
  3. proposal-only / docs-only / fail-closed の維持。

## Stream D DOC-OPS-05統合パス（2026-05-05）

### Phase 1 Read（3Issue再読・メタ差分確認）
- 3Issue（05/06/07）を各Phase冒頭で再読し、`Context/Decision/Consequences`、`GoNoGoGate`、`Validation`、`Proceed tri-state` の差分を確認。
- 差分判定: 重大不一致なし（分類差分は仕様どおり、05/07=Move internal、06=Improve external）。

### Phase 2 ADR（Context/Decision/Consequences整列）
- Context: Open判定メタは概ね揃うが、依存確定証跡と Approval Record が未充足。
- Decision: 3Issue共通で `docs-check必須`、`unit/integration/e2eは期待レベル定義のみ`、`docs-only` を維持。
- Consequences: Open判定を単体再実行可能にしつつ、未承認Proceedを抑止。

### Phase 3 Plan（Go/NoGo/Stop と自己修復上限）
- Go: 依存確定証跡 + Approval Record + docs-check pass + tri-state再判定可能。
- NoGo/Hold: 上記未充足時。
- Stop: self-correction 4回目相当、または未定義競合。
- Self-correction budget: `<=3`（共通固定）。
- docs-only非目標共通化: 実装変更・04_Documentation本文改稿・新規E2E実行結果作成は非目標。

### Phase 4 Execute（docs-check中心・実装非変更）
- 実施: 本Issueメモの整合整理のみ（語彙・ゲート・停止条件・依存条件）。
- 非実施: `03_Implement/**`、`04_Documentation/**` 本文、実装/設定変更。

### Phase 5 Verify（3Issue横断一致検証）
- 検証観点:
  1. Context/Decision/Consequences の存在。
  2. Go/NoGo/Stop と self-correction上限の一致。
  3. docs-check必須・他検証は期待レベル定義のみ、の一致。
- 失敗時運用: 最大3回まで修正、4回目相当はStop。

### Phase 6 Proceed/Stop（依存証跡ゲート）
- 現在判定: **Hold**（依存確定証跡不足）。
- Proceed条件: 依存証跡充足後に再判定。
- Stop条件: 4回目相当の自己修復、または依存矛盾が解消不能な場合。

## Stream I final consistency sync（2026-05-06 / DOC-OPS-05-07）

### Context
- 日付付きE2E検証ログの配置見直しは `Move internal` 方針だが、Open化判定は DOC-OPS-05 Draft群（05/06/07）で同一運用語彙に揃える必要がある。
- Candidate destination は提案状態であり、依存確定までは確定扱いできない。

### Decision
- 3Issue共通の Open gate 条件を採用し、語彙を先に正規化する。
  1. `Context/Decision/Consequences` を単体再読可能に固定。
  2. Validationは `docs-check` 必須、他検証は期待レベル定義のみ。
  3. `Proceed` は依存確定証跡 + Approval Record 完備まで `Hold`。
  4. self-correction は最大3回、4回目相当は `Stop`。
- ADR/運用語彙の不一致は本IssueのContext/Decision/Consequencesで先行吸収し、実移管判断はOpen後に限定する。

### Consequences
- 配置見直しの判断が「提案止まり」で維持され、誤って確定移管されるリスクを低減できる。
- 05/06/07横断で Open判定の再現性が上がり、依存未確定時の `Hold/Stop` 運用が明確になる。

### Open化条件（確定版 / proposal-only）
- [ ] OC-1: 3Issueで C/D/C・Gate・Proceed tri-state が一致。
- [ ] OC-2: docs-check 記録あり、self-correction `<=3`。
- [ ] OC-3: Approval Record（日時/承認者/対象/判断/evidence）完備。
- [ ] OC-4: Candidate destination を確定扱いしていない。

### Self-repair counter
- Current: `2/3`
- Next action on overflow: `Stop`（4回目相当で作業停止）
