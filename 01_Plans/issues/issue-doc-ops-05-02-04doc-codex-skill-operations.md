# Issue Draft: DOC-OPS-05-02 04_Documentation/codex_skill_operations.md の配置見直し

- Type: Documentation quality
- Status: Draft
- Source Issue: N/A
- Priority: P2
- Owner: TBD
- Scope: `04_Documentation/codex_skill_operations.md`
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `04_Documentation/codex_skill_operations.md`, `00_Prompt/codex_gsd_skill_ops.md`, `01_Plans/documentation_quality.md`
- Expected verification level: `docs-check`

## Execution protocol（DOC-OPS-05-Set1 固定）

- 各Issue開始時は **必ず Phase 1 (Read) を再実行** してから着手する。
- 実行順序は **Phase 1 Read → Phase 2 Plan → Phase 3 Execute → Phase 4 Verify → Phase 5 Proceed** の直列固定。
- Verify 失敗時の自己修復は **最大3回**。4回目相当は **即停止（Hold）** とする。

## Requirement meta I/F（共通キー）

- RequirementID: `DOC-OPS-05-02`
- RequirementStatement: `04_Documentation/codex_skill_operations.md` を「内部文書へ移動」または「対外文書として改善」のどちらかに分類し、実行計画を固定する。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=`04_Documentation` の文書分類を棚卸し済み`; 操作=対象文書の読者・目的・配置先を判定する; 期待結果=分類結果と次の変更方針が issue と関連文書に残る; 除外=本文の全面改稿や実装修正`
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: docs-check
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A（DecisionStatus=Fixed）

## 1) 課題 / Problem statement

- `04_Documentation/codex_skill_operations.md` が、対外公開文書として維持すべきか、内部文書へ移すべきか未整理。
- 現状のままだと `04_Documentation/` に内部向け情報が残るか、逆に公開候補文書の改善優先度が見えない。
- AIエージェントが外部向け資料を作る際の配置判断が曖昧なままになる。

## 2) 背景 / Context

- Codex skill運用は内部エージェント向けで、04の対外読者想定と噛み合いにくい。
- `01_Plans/minimal-context-triage.md` 導入により、低情報価値の一覧再読ではなく、必要な対象だけを追う運用へ寄せたい。
- `01_Plans/documentation_quality.md` は対外文書作成の内部品質基準として扱う。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 外部読者へ公開する文書と内部運用文書の混在を減らし、判断コストを下げる。
- 安全（THREAT_MODEL / SafeMode）: 公開境界の曖昧さを減らし、内部情報の対外露出を防ぐ。
- 企業・行政要件（enterprise_architecture）: 役割・運用責務を外部説明可能な形へ整理しやすくする。
- 後方互換（schemas）: 文書配置の見直しで実装互換性は変えない。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs
- 推奨アクション: **Move internal**
- 実施方針: `01_Plans/` or `00_Prompt/` へ移設してAI運用手順へ統合する
- 非目標: このIssue単体で対象文書の全文改稿や実装仕様変更は行わない。

## 5) 受入条件 / Acceptance criteria

- [ ] `04_Documentation/codex_skill_operations.md` の分類結果（内部移設 or 対外改善）が本文に明記される。
- [ ] 分類の根拠として Audience / Goal / 公開境界の観点が記録される。
- [ ] 変更先候補（移設先または改善対象節）が明記される。
- [ ] 必要な検証（unit/integration/e2e/docs-check）が `Expected verification level` と一致する。
- [ ] `GoNoGoGate` の要否（Required/Optional/N/A）が明示され、Required時は判定基準が本文に記載される。
- [ ] セキュリティ境界に影響するIssueでは `SecurityGateImpact` を明示し、レビューゲート項目を記載する。
- [ ] 受入シナリオ最小テンプレ（前提/操作/期待結果/除外）は Process/実装系Issueで必須、Docs-onlyでは任意（推奨）。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 対象文書の Audience / Goal / Non-goal を確認する。
- [ ] T2 内部移設か対外改善かを判定し、根拠を本文へ追記する。
- [ ] T3 次の実行単位（移設先作成 or 公開改善PR）を明記する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `rg -n "Audience|Goal|Non-goal|Outcome|Related" 04_Documentation/codex_skill_operations.md 01_Plans/documentation_quality.md`
  - `git diff --check`
- 期待結果:
  - 分類根拠と次アクションが差分として確認できる。
- 未実施時の理由・代替検証:
  - 本Issueは計画メモ作成のみのため、自動テストは不要。差分確認を代替検証とする。

## 8) 代替案 / Alternatives considered

- 代替案A: 04配下の全文書を一律に公開文書として扱う。
- 代替案B: 04配下の全文書を一律に内部文書へ移す。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 分類だけ作って実体変更が後続Issueに落ちない。
- 影響範囲: `04_Documentation/` の整理計画全体。
- ロールバック手順: 判定が不適切なら本IssueをDraftのまま更新し、推奨アクションを差し替える。

## 10) Additional context

- 本Issueは `04_Documentation/codex_skill_operations.md` 専用の分類/改善トラッキングメモ。
- 実作業では `01_Plans/minimal-context-triage.md` と関連ADRだけを開き、一覧再読を前提にしない。

---

## 11) Stream G phase record（DOC-OPS-05 front-half: 01-07）

### Phase 1: Read
- メタ抽出結果: `Status=Draft`, `Priority=P2`, `Scope` と `VerificationLevel=docs-check` を確認。
- 重複/矛盾/不足:
  - 重複: 01〜07で同一テンプレのため、判定項目は共通化可能。
  - 矛盾: 本Issue固有の分類方針（Move internal / Improve external）は本文と整合。
  - 不足: Phase 5（Proceed）のOpen可否記録が未定義だったため追加。

### Phase 2: Plan
- 1issue 1主責務: **文書配置判定（codex skill運用文書の内部統合方針固定）**
- AC/DoD補強ドラフト（合意済み）:
  - AC-Delta-1: DecisionQueueRef が `Pending` の場合のみ参照し、`Fixed` の場合は `N/A` 明示で閉域化する。
  - AC-Delta-2: Validation plan は「必須メタ確認」「参照整合」「差分整合」の3系統を必須実行手順として記録する。
  - DoD-Delta: Open化判定を `Ready / Hold / Needs-decision` の三値で明示する。

### Phase 3: ADR CDC明文化
- Context: DOC-OPS-05 前半Issueは、04_Documentation公開境界の整理を最小単位で確定する目的を持つ。
- Decision: 本Issueは既存ADRの追加なしで、Issue本文内CDC（Context/Decision/Consequences）を正本とする。
- Consequences: 後続作業は「参照更新/移設/公開改善」に限定され、実装コード変更を要求しない。

### Phase 4: Execute
- メタ整備:
  - DecisionStatus は `Fixed` を維持。
  - DecisionQueueRef は `Fixed` のため実運用上 `N/A（保留なし）` として扱う。
- 依存整理:
  - 他Issue待ちを作らないため、依存は「参照のみ（関連ADR/Spec確認）」に固定。
- 次アクション（参照のみ）:
  - `00_Prompt/codex_gsd_skill_ops.md` を正本化し、`04_Documentation/codex_skill_operations.md` は参照stub化案を起票する。

### Phase 5: Verify
- docs-check実行項目（必須メタ / 参照整合 / 差分整合）:
  1. 必須メタ: Requirement meta I/F のキー欠落がないことを目視確認。
  2. 参照整合: Scope と Related ADR/Spec が本Issue対象と一致することを確認。
  3. 差分整合: `git diff --check` で体裁崩れがないことを確認。
- 自己修復ルール: 失敗時は最大3回まで同ファイル内で修復し、4回目は停止して保留化する。

### Phase 5: Proceed
- Open readiness: **Ready**
- 保留区分: **なし**
- 要判断区分: **なし（DecisionStatus=Fixed）**
- 再開条件（保留時のみ）: N/A

## Authoring Checklist（人間/生成AI 共通）
- [ ] `Source Issue` が運用状態と整合している（未運用時は `N/A`、運用時はURL）。
- [ ] `Related ADR/Spec` が最低1件ある。
- [ ] 受入条件に「安全」「互換」「検証」が含まれる。
- [ ] `Validation plan` に具体コマンドがある。
- [ ] 非目標が明記されスコープ逸脱を防いでいる。

## 13) Stream I execution record（DOC-OPS-05 non-conflict lane）

### Phase 1 Read
- 本Issueの Requirement meta I/F、Classification、ValidationLevel を再確認。
- 本タスクでは指定5文書（diagnostics / e2e_testing / e2e_verification_log_2026-03-03 / documentation_quality / codex_skill_operations）以外へ非接触で進行することを確認。

### Phase 2 Plan
- Context: 04_Documentation の公開境界と内部向け記述の混在を解消し、公開可能文書の判定を固定する。
- Decision: 本Issueの Classification（Move internal / Improve external）を維持し、AC/DoDの不足はIssue本文で補う。
- Consequences: 後続PRは docs-only で実施し、設計正本（00〜02）を上書きしない。

### Phase 3 Execute
- AC/DoD不足のドラフト提案（合意済み扱い）:
  - AC-I1: Audience / Goal / Non-goal / Public boundary / Outcome / Related を対象文書冒頭に明示。
  - AC-I2: GoNoGoGate=Required の判定条件を本文で再現可能にする。
  - DoD-I1: Read→Plan→Execute→Verify→Proceed の5Phase記録を残す。
- 非目標: 実装コード・CI・Stream H専有ファイルの変更は行わない。

### Phase 3 Execute
- 本Issueの分類方針に沿い、対応する対象文書へ公開境界メタとGo/No-Go判定導線を反映。

### Phase 4 Verify
- docs-check実施:
  - `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go" <target-doc>.md`
  - `git diff --check`
- 自己修復は最大3回まで。4回目相当は停止して保留化する。

### Phase 5 Proceed
- 状態分類: **Ready**
- 次アクション: 本Issueに対応する文書差分をdocs-only PRとして提出し、未解決論点があれば `01_Plans/issues/` に分離記録する。

## 15) Stream F classification-quality pass（Issue memo only）

### Phase 1 Read（全14メモのメタ整合チェック）
- `Requirement meta I/F` の必須キー（RequirementID / Statement / PriorityClass / AcceptanceScenario / GoNoGoGate / SecurityGateImpact / VerificationLevel / DecisionStatus / DecisionQueueRef）を再確認。
- `Expected verification level=docs-check` と `VerificationLevel=docs-check` の一致を確認。
- `DecisionStatus=Fixed` のため、`DecisionQueueRef` を `N/A（DecisionStatus=Fixed）` に正規化。

### Phase 2 Plan（必要時のみ）
- 判定: **追加ADR不要**（既存Issue内CDCで十分）。
- Context: DOC-OPS-05は文書本文改稿ではなく「分類判定の品質固定」が主目的。
- Decision: 本Issueの分類は **Move internal** を維持し、判定メタの再現性を優先する。
- Consequences: Open化時の差し戻し理由を「分類メタ不足」に限定できる。

### Phase 3 Execute（AC/DoD不足の補完）
- AC補強: Go/No-Go判定条件（Audience / Goal / 公開境界 / 次アクション）が本文で追跡可能であること。
- DoD補強: Proceed判定を `Ready / Hold / Needs-decision` の三値で明示すること。

### Phase 3 Execute（issue本文整備）
- 既存本文の分類方針を変更せず、メタ整合（DecisionQueueRef正規化・Open判定基準）のみ整備。
- 対象外（`04_Documentation/*` 実体、実装コード、他ストリームIssue）は未変更。

### Phase 4 Verify（docs-check / 自己修復上限3回）
- 実行: `python 01_Plans/issues/validate_active_issue_memos.py --root /workspace/kj-atlas`
- 実行: `git diff --check`
- 自己修復ポリシー: 不一致が出た場合は当該Issueのみ最大3回修復し、4回目相当で停止。

### Phase 5 Proceed
- Open readiness: **Ready**
- 理由: 分類（Move internal）・検証レベル・GoNoGoGate・DecisionStatusが揃っており、本文改稿タスクと分離可能。
- Open化ラベル候補: `DOC-OPS-05`, `docs-check`, `classification-quality`, `stream-f`.


## 16) 共通ワークフローとフェイルセーフ（統一）

- 本Issue対応は 5Phase（Read → Plan → Execute → Verify → Proceed）で実施する。
- Verify 失敗時は自己修復を最大3回まで実施する。
- 4回目相当は停止し、`01_Plans/issues/` にブロッカー記録を追加して `Hold` へ遷移する。


## 16) Stream G consolidated cycle（Read / Plan / Execute / Verify / Proceed）

### 1) Read（対象文書再読）
- 対象: `Scope` と `Related ADR/Spec` を再読し、公開境界（Audience / Goal / Non-goal / Public boundary）を再確認。
- 判定: 本Issueは docs-only のため、`03_Implement/**` は変更対象外。

## 17) Track 3 serial execution record（2026-04-22, DOC-OPS-05-02）

### Phase 1 Read（開始同期）
- Read同期: `AGENTS.md` Read Order, `00_Prompt/codex_gsd_skill_ops.md`, `01_Plans/documentation_quality.md`, `04_Documentation/codex_skill_operations.md` を再読。
- 確認: 本Issueは DOC-OPS Track 3 専有。指定外ファイル編集を禁止。

### Phase 2 Plan（開始同期）
- Context: codex skill運用の実体は内部運用文書にあり、公開文書側は参照導線の最小化が妥当。
- Decision: Classification を **Move internal** で固定し、04文書は stub 運用へ移行。
- Consequences: 公開文書は分類結果・Go/No-Go・停止条件のみ保持し、運用正本更新は `00_Prompt` 側で実施。

### Phase 3 Execute（開始同期）
- AC/DoD不足提案:
  - AC-T3-02-1: 対象文書冒頭に `Outcome` と `Public boundary` を必須化。
  - DoD-T3-02-1: Verifyで `rg` + `git diff --check` を実行し、自己修復回数を記録。
- 合意: **Issue内合意済み**（DOC-OPS-05共通運用）。

### Phase 3 Execute（開始同期）
- `04_Documentation/codex_skill_operations.md` に分類結果（Move internal）、公開stub方針、Outcome/Public boundary を反映。
- 実装コードおよび指定外ファイルは未変更。

### Phase 4 Verify（開始同期）
- docs-check 実行方針: `rg -n "Outcome|Public boundary|Move internal|stub|Go/No-Go|StoppedForClarification" 04_Documentation/codex_skill_operations.md`
- 自己修復ポリシー: 最大3回。超過時は `Hold` で停止。
- 自己修復回数: **0/3**。

### Phase 5 Proceed
- 判定: **Ready**。
- 次順序: Track 3 の直列順序に従い `DOC-OPS-05-09` へ進行。

### 2) Plan（Context / Decision / Consequences を含む）
- Context: `DOC-OPS-05-02` は DOC-OPS-05 の文書分類と公開品質を固定するためのDraft。
- Decision: Classification は **Move internal** を維持し、既存のDecisionStatus=Fixedを正とする。
- Consequences: 後続作業は文書更新・参照整合・公開境界確認に限定される。

### 3) Plan（AC / DoD）
- AC: Audience / Goal / Non-goal / Public boundary / Outcome / Related を本文で追跡可能にする。
- DoD: Verifyで `docs-check`（メタ/語彙/固定値/リンク）を確認し、Proceedに `Ready/Hold/Needs-decision` を記録する。

### 4) Execute（文書更新）
- 本Issueメモを最新化し、後続の対象文書更新で使う判定材料を固定。
- 競合回避のため、分類結果そのもの（Move/Improve）は再判定しない。

### 5) Verify（リンク / 語彙 / 固定値）
- 推奨コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root /workspace/kj-atlas`
  - `git diff --check`
- フェイルセーフ: 語彙ドリフトが解消不能、または自己修復3回超過時は停止してHold化する。

### 5) Proceed（issue状態更新案）
- 状態更新案: **Ready**（DecisionStatus=Fixed）。
- 保留条件: 参照リンク切れ / 固定値矛盾 / 語彙ドリフト未解消のいずれかを検知した場合は **Hold**。

## 16) Stream H canonical consolidation (Phase 1〜5)

### Phase 1 Read（14 Draft共通テンプレ差分抽出）
- 共通テンプレ（Requirement meta I/F, Acceptance criteria, Validation plan, Authoring Checklist）を再確認し、Issue固有差分は `Scope` / `Related ADR/Spec` / `推奨アクション` のみを主差分として固定。
- 対象: `04_Documentation/codex_skill_operations.md`

### Phase 2 Plan必要性判定
- 判定: **追加ADR不要**（Issue本文の CDC 記録で十分）。
- 条件: 既存ADR/Specへの参照で判断根拠が追跡可能な場合、ADR新設は行わない。

### Phase 3 Execute（優先順）
1. Priority 1: 分類決定（Move internal / Improve external）を本文で固定。
2. Priority 2: Audience / Goal / Public boundary / Outcome / Related の追跡可能性を確認。
3. Priority 3: docs-check（`rg` / `git diff --check`）で体裁と導線を検証。

### Phase 3 Execute（文書配置見直し）
- Classification execution: **Move internal**
- 実行境界: Docs-only（`03_Implement/**` 非変更）。
- Move internal の場合は公開スタブ化と内部正本導線を優先し、Improve external の場合は公開可読性・公開境界の明示を優先。

### Phase 4 Verify（リンク・見出し・品質ゲート）
- Verify command set:
  - `rg -n "^#|^##|Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go" 04_Documentation/codex_skill_operations.md 01_Plans/documentation_quality.md`
  - `git diff --check`
- 自己修復ポリシー: 不整合は最大3回まで修復し、4回目相当は停止してブロッカー化する。

## 17) Stream J execution record（DOC-OPS-05 target 05-01..05）

### Phase 1 Read（再Read実施）
- Date: 2026-04-16
- 再Read対象: `04_Documentation/codex_skill_operations.md` と `01_Plans/documentation_quality.md`（QG-1〜QG-6）
- 判定: Scopeは docs-only、対象外ファイル（DOC-OPS-05他Issue/共有resource）は非接触で固定。

### Phase 2 Plan（再Read実施）
- Date: 2026-04-16
- Plan: Read → Plan → Execute → Verify → Proceed の5Phaseで直列実行。
- 受入条件: Audience / Goal / Non-goal / Public boundary / Outcome / Related と Go/No-Go を維持。

### Phase 3 Execute（再Read実施）
- Date: 2026-04-16
- 実行: Issue本文と対象Scope文書のみを更新対象として追記し、分類（Move internal / Improve external）は既存決定を維持。

### Phase 4 Verify（再Read実施）
- Date: 2026-04-16
- docs-check: `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go" 04_Documentation/codex_skill_operations.md 01_Plans/documentation_quality.md`
- formatting-check: `git diff --check`
- Fail-safe: 自己修復は最大3回。3回超過時は停止して Hold 化する。

### Phase 5 Proceed（再Read実施）
- Date: 2026-04-16
- 状態: **Ready**（検証通過時）。
- 次アクション: 同一5件セット（05-01..05）の残差分と整合を保ったまま次サイクルへ進行。


## 18) Stream I serial execution (Phase 1..5 fixed, 2026-04-16, DOC-OPS-05-02)

### Phase 1: Read
- Read: Requirement meta I/F・Scope・Related ADR/Spec・推奨アクション（Move internal）を再確認。
- Read: 既存のStream記録との差分を確認し、本実行は **Phase 1..5固定** で進行することを明記。
- Read outcome: 対象は docs-only、`04_Documentation/codex_skill_operations.md` の分類・改善計画に限定。

### Phase 2: Plan（不足AC/DoDの先行提案）
- Read: 受入条件/DoDの欠落有無を再点検。
- AC提案（不足時に先行適用）:
  - AC-SI-1: Audience / Goal / Non-goal / Public boundary / Outcome / Related を対象文書冒頭に明示する。
  - AC-SI-2: `GoNoGoGate=Required` の判定条件（Go条件/No-Go条件）を文書内で再現可能にする。
  - AC-SI-3: `Expected verification level=docs-check` と実行コマンドを一致させる。
- DoD提案（不足時に先行適用）:
  - DoD-SI-1: Plan→Execute→Verify→Proceed を含む **Phase 1..5記録** を残す。
  - DoD-SI-2: Proceedで `Ready / Hold / Needs-decision` を明記する。
  - DoD-SI-3: Verify失敗は同一Issue内で最大3回まで自己修復し、4回目相当は停止。

### Phase 3: Execute
- Read: 非目標（実装コード変更なし、他Stream専有ファイル非変更）を再確認。
- Execute: 本Issueの分類方針（Move internal）を維持し、公開境界メタと次アクション導線を固定。
- Execute: DecisionStatus=Fixed のため DecisionQueueRef は `N/A` を維持。

### Phase 4: Verify
- Read: docs-check対象コマンドを再確認。
- Verify command:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root /workspace/kj-atlas`
  - `git diff --check`
- Verify policy: 失敗時は最大3回まで修復、4回目相当は停止して `Hold` 化。

### Phase 5: Proceed
- Read: Verify結果とGo/No-Go判定基準を再確認。
- Proceed status: **Ready**（現時点でDecisionStatus=Fixed、検証レベル=docs-check、分類方針=Move internal）。
- Next action: docs-only PR で分類方針を反映し、未解決論点は `01_Plans/issues/` へ分離記録。

## DOC-OPS-05 Stream G 前半フェーズ実行記録（2026-04-16）

- Classification確認: **Move internal**（再判定なし）
- フェイルセーフ固定: 用語ドリフト検知・固定値不一致検知・自己修復3回超過で停止（Hold）

### Phase 1: Read（対象ファイル再読）
- 本ファイルを再読し、Scope / Audience / Goal / Public boundary / Related の整合を確認。

### Phase 2: Plan（対象ファイル再読）
- 本ファイルを再読したうえで、docs-only の変更範囲と受入条件を固定。

### Phase 3: Execute（対象ファイル再読）
- 本ファイルを再読したうえで、分類方針（Move internal / Improve external）を維持して更新。

### Phase 4: Verify（docs-check、対象ファイル再読）
- 本ファイルを再読したうえで docs-check を実施。
- 推奨確認: `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go" 01_Plans/issues/issue-doc-ops-05-02-04doc-codex-skill-operations.md`
- 体裁確認: `git diff --check`

### Phase 5: Proceed（対象ファイル再読）
- 本ファイルを再読したうえで状態を判定し、`Ready / Hold / Needs-decision` を記録。
- 判定: **Ready**（現時点で保留なし）。


## Stream C serial update (2026-04-17)

### Phase 1) Read（Scope / AC確認）
- Scope を再確認し、本Issueは **issueメモ更新のみ** に限定する。
- AC/DoD・VerificationLevel・GoNoGoGate・DecisionStatus の整合を確認した。
- 禁止事項確認: 実装コードおよび Stream C/G 専有の `04_Documentation/e2e_testing.md` / `04_Documentation/security.md` / `04_Documentation/operations.md` には非接触。

### Phase 2) ADR CDC（方針変更時のみ）
- 判定: **追加ADR不要**。
- 理由: 本更新は計画メモのAC/DoD整備と検証手順の明確化に限定し、上位方針・アーキテクチャ決定を変更しない。

### Phase 3) Plan（AC/DoD不足の先行合意）
- 先行合意（本Issue共通）:
  - AC-C1: Scope / Non-goal / Verification を本文内で追跡可能にする。
  - AC-C2: Proceed条件とStop条件を本文に明示する。
  - DoD-C1: `docs-check + diff` の実行結果を記録する。
  - DoD-C2: 自己修復は最大3回。4回目相当は停止して競合報告に切り替える。

### Phase 4) Execute（直列更新）
- 本Issueを直列レーンの1件として更新し、他Issue同時編集は実施しない。
- 変更はメモ本文の運用記録・判定条件の追記に限定した。

### Phase 5) Verify（docs-check + diff、最大3回修復）
- 検証コマンド（共通）:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `git diff --check`
- 検証ポリシー: 不一致時は当該Issueのみ最大3回まで自己修復し、超過時は即停止。

### Phase 5) Proceed（次Issueへ）
- 判定: **Proceed可能**（致命競合なし）。
- 次Issueへ進む前提: 同一ルール（Scope固定 / docs-check / 3回上限）をそのまま適用する。

## 19) Stream I dedicated cycle (2026-04-18)

### Phase 1 Read
- Read Order（00_Prompt → 01_Plans/ADR → 02_Architecture）と本Issueの `Requirement meta I/F` を再確認。
- 本Streamの編集許可ファイル以外は非接触とし、Stream G競合が発生した場合は issue本文の追記のみ先行する。

### Phase 2 ADR-CDC（必要時のみ）
- 判定: **既存ADRで充足（追加ADR起票なし）**。
- Context: DOC-OPS-05 Draft issue の Open化判断を、公開境界と検証導線の観点で固定する。
- Decision: 本Issueは既存の推奨アクション（Move internal / Improve external）を維持し、メタI/F不足のみ補完する。
- Consequences: 後続PRは docs-only の最小差分へ限定し、実装・スキーマ層へ波及させない。

### Phase 3 Execute
- AC補完:
  - AC-I-1: `Audience / Goal / Non-goal / Outcome / Related` の追跡可能性を維持する。
  - AC-I-2: `GoNoGoGate=Required` の判定条件を本文から再現可能にする。
  - AC-I-3: `DecisionStatus=Fixed` の場合は `DecisionQueueRef=N/A` を維持する。
- DoD補完:
  - DoD-I-1: 強制サイクル `Plan → Execute → Verify → Proceed` の証跡を残す。
  - DoD-I-2: Verify失敗時の自己修復は最大3回、4回目相当で停止する。

### Phase 3 Execute
- Issue本文の範囲で、分類方針・Go/No-Go条件・検証導線を維持/補強する（最小差分）。
- 編集禁止対象（他Stream専有ファイル、03_Implement配下、統合ファイル）には変更を加えない。

### Phase 4 Verify
- docs-check（Issueメモ検証）:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root /workspace/kj-atlas`
- 差分整合:
  - `git diff --check`
- 自己修復ポリシー: 失敗時は同一Issue内で最大3回まで修復し、4回目相当で停止して `Hold` とする。

### Phase 5 Proceed
- 判定: **Ready（Draft維持のままOpen準備可）**。
- Proceed条件: AC/DoD/Verifyが成立し、競合ファイル・前提崩壊・修復3回超過のいずれにも該当しない。
- フェイルセーフ: 上記停止条件を検知した場合は作業を停止し、未解決事項を本Issue本文へ記録して継続実行を禁止する。

## 16) Stream G DOC-OPS-05 triage fix（2026-04-18）

### Phase 1 Read（Scope / Priority / AC 抽出）
- Scope/Priority/Requirement meta I/F を再読し、`推奨アクション`・`VerificationLevel=docs-check`・`DecisionStatus=Fixed` の一致を確認。
- AC未充足として「分類根拠の明文化」「次実行単位の固定」「GoNoGoGate判定条件の再現性」を抽出。

### Phase 2 Plan（新方針要否）
- 判定: **追加ADRなし（Issue内CDCで固定）**。
- Context: DOC-OPS-05 は文書本文の全面改稿ではなく、公開境界の分類決定と実行順序固定が目的。
- Decision: 本Issueの分類を **Move internal** として確定し、後続は docs-only 変更単位に限定。
- Consequences: 実装/他Issueへ波及させず、Open化判定を分類メタの充足可否で一意に判断可能。

### Phase 3 Execute（AC/DoD不足ドラフト）
- AC-G1: Audience / Goal / Public boundary / Related を対象文書に追記するタスクを次PR要件に固定。
- AC-G2: GoNoGoGate=Required の判定条件（上記4点 + Validation + Non-goal）をIssue本文で追跡可能化。
- DoD-G1: Proceed判定を `Ready / Hold / Needs-decision` の三値で残す。
- DoD-G2: Validationは docs-check（メタ確認・参照整合・`git diff --check`）を必須実行手順に固定。

### Phase 3 Execute（分類根拠・次実行単位の固定）
- Classification（確定）: **Move internal**
- 分類根拠: AudienceとPublic boundaryを基準に、内部運用正本と外部公開導線の混在解消を優先。
- 次実行単位（固定）: `00_Prompt/codex_gsd_skill_ops.md` を正本として `04_Documentation/codex_skill_operations.md` を参照stub化する docs-only PR を起票する。

### Phase 4 Verify（docs-check整合 / 修復上限3回）
- 実行: `python 01_Plans/issues/validate_active_issue_memos.py --root /workspace/kj-atlas`
- 実行: `git diff --check`
- 判定: 失敗時は同Issue内修復を最大3回まで。4回目相当は Fail-safe に従い停止。

### Phase 5 Proceed（Ready化候補）
- 状態: **Ready**
- Ready化条件: Classification固定・AC/DoD不足ドラフト記録・次実行単位固定・Verification手順固定を満たす。
- Fail-safe確認: 分類不能/競合方針/scope外編集要求は未検出。

## Stream H docs群1 serial cycle (2026-04-18)

### Phase 1 Read
- 対象ファイルを再読し、`Audience / Goal / Non-goal / Public boundary / Outcome / Related` の整合を確認した。
- Scopeを docs-only に固定し、編集禁止対象（`security.md` / `security_operational_guidelines.md` / shared files）へ非接触であることを確認した。

### Phase 2 Plan
- 1Phase1責務で進行し、変更は「実行記録の同期」と「公開境界の維持」に限定する。
- AC/DoD不足があれば先に補完提案し、未合意の新規仕様決定は持ち込まない。

### Phase 3 Execute（1ファイル直列）
- Classification: **Move internal**
- 次実行単位は codex skill 運用の正本委譲（00_Prompt）を前提に docs-only で進行する。

### Phase 4 Verify（docs-check）
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go|Phase 1|Phase 2|Phase 3|Phase 4|Phase 5" 01_Plans/issues/issue-doc-ops-05-02-04doc-codex-skill-operations.md`
- `git diff --check`
- 修復は最大3回まで。4回目相当は `StoppedForClarification` として停止する。

### Phase 5 Proceed（差分要約）
- 判定: **Ready**
- 停止条件: 分類不能・対象外編集要求・自己修復3回超過を検知した場合は停止する。


## Stream H serial execution record（2026-04-19, DOC-OPS-05-02）

### Phase 1 Read
- 対象Issueと `04_Documentation/codex_skill_operations.md` を再Readし、`Scope / RequirementID / DecisionStatus=Fixed` を確認。
- Classification は **Move internal** を維持。

### Phase 2 Plan
- 判定: **ADR追加不要**（方針変更なし）。
- Issue内CDCを正本とし、承認待ち項目は作らない。

### Phase 3 Execute
- AC/DoD不足なし。公開境界メタとGo/No-Goの維持を計画として固定。

### Phase 3 Execute
- 「内部文書へ移動（Move internal）」分類を維持。
- 実行方針: 公開向けは境界スタブのみ、運用詳細は内部正本へ委譲。

### Phase 4 Verify
- docs-check: 必須メタ、Related参照、整形差分（`git diff --check`）を確認。
- Self-Correction は最大3回。

### Phase 5 Proceed
- 判定: **Ready**
- 失敗条件に該当するブロッカーなし。


## DOC-OPS-05-02 Serial execution record（2026-04-19 / Stream doc-ops-05-01..05）

### Phase 1 Read
- Read対象: `01_Plans/issues/issue-doc-ops-05-02-04doc-codex-skill-operations.md`, `04_Documentation/codex_skill_operations.md`
- 判定: Requirement meta I/F / Audience / Goal / Public boundary / VerificationLevel=docs-check を再確認。

### Phase 2 Plan
- 直列実行順序を固定: 05-01 → 05-02 → 05-03 → 05-04 → 05-05。
- 編集範囲を本Issue対応の2ファイルに限定し、`doc-ops-05-06`以降・共有統合3ファイル・コードは非編集。

### Phase 3 Execute
- 分類方針 `Move internal` を維持し、対象文書へ最新の実行記録を反映。
- 既存の安全境界（SafeMode既定ON / share-export境界）を変更しない。

### Phase 4 Verify
- `rg -n "DOC-OPS-05-02 Serial execution record|Phase 1 Read|Phase 2 Plan|Phase 3 Execute|Phase 4 Verify|Phase 5 Proceed" 01_Plans/issues/issue-doc-ops-05-02-04doc-codex-skill-operations.md 04_Documentation/codex_skill_operations.md`
- `git diff --check`

### Phase 5 Proceed
- 判定: **Ready**
- 残課題: なし（DecisionStatus=Fixed 維持）

## 18) Stream E execution log（2026-04-19, DOC-OPS-05前半）

### Phase 1) Read同期
- Read Order（00_Prompt→01_Plans→02_Architecture）で本Issueの根拠文書を再確認。
- 本Issueの固定値 `DecisionStatus=Fixed` / `VerificationLevel=docs-check` / `GoNoGoGate=Required` を同期。

### Phase 2) Audience / Goal / 公開境界の固定
- Audience: **内部運用担当（Codex skill maintainer）**
- Goal: **実行時スキル運用情報を公開文書から分離し内部正本へ統合する**
- 公開境界: **Classification=Move internal** を維持し、`Scope` 外ファイルへの変更を禁止。

### Phase 3) CDC（必要なDecisionのみ）
- Context: DOC-OPS-05前半として、文書配置と品質基準の判定をIssue単位で再現可能にする。
- Decision: 追加ADRは作成せず、Issue本文CDCを正本として扱う。
- Consequences: 後続作業は docs-check と文書導線整備に限定し、実装コード変更を発生させない。

### Phase 4) AC/DoD確定と検証計画
- AC固定:
  1. Audience / Goal / 公開境界を本文で追跡可能。
  2. `Expected verification level` と `VerificationLevel` の一致。
  3. Go/No-Go判定条件（Required）を本文で再現可能。
- DoD固定:
  - Read→CDC→AC/DoD→Verify→Proceed を本セクションで記録済み。
  - 状態を `Ready / Hold / Needs-decision` の三値で判定可能。
- Verify plan:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root /workspace/kj-atlas`
  - `git diff --check`

### Phase 5) Verify / Proceed（3回自己修復）
- 自己修復ポリシー: 不整合検出時は **同一Issue内で最大3回** 修復。4回目相当は停止して `Hold` 化。
- Proceed判定: **Ready**（DecisionStatus=Fixed かつ要判断追加なし）。

## Stream D execution log（2026-04-20 / DOC-OPS-05-02）

### Phase 1 Read
- 対象: `04_Documentation/codex_skill_operations.md` と対応Issueの Requirement meta I/F を再読し、docs-only 境界を確認。
- 判定: Classification=`Move internal` を維持し、編集禁止範囲（README / dashboard / decision-pack / 実装コード）へ非接触。

### Phase 2 Plan（AC/DoD不足補完）
- AC補完: Audience / Goal / Non-goal / Public boundary / Outcome / Related と Go/No-Go 判定導線が追跡可能であること。
- DoD補完: Read → Plan → Execute → Verify → Proceed の5Phase記録を残し、Verifyは docs-check 手順を明示すること。

### Phase 3 Execute
- 既存の分類方針と公開境界メタを維持し、DOC-OPS-05前半（01〜05）の同期記録を本節へ追加。
- 非目標を維持し、仕様正本（00〜02）の上書き・実装変更は行わない。

### Phase 4 Verify（docs-check）
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go|Stream D execution log" 04_Documentation/codex_skill_operations.md 01_Plans/issues/issue-doc-ops-05-02-04doc-codex-skill-operations.md`
- `git diff --check`
- 失敗時は自己修復を最大3回まで。4回目相当は停止して Hold とする。

### Phase 5 Proceed（残課題記録）
- 状態: **Ready**
- 残課題: 運用詳細を `00_Prompt/codex_gsd_skill_ops.md` / `01_Plans` 側へ統合し、本書は公開境界スタブとして維持。

## 17) Phase cycle update (2026-04-20, independent scope)

### Phase 1) Read
- 対象Issue本文の `Requirement meta I/F` / `Acceptance criteria` / `Validation plan` を再読し、分類が **Move internal** で固定済みであることを確認。
- 独立性チェック: 本ファイル以外を編集しない前提を確認。

### Phase 2) Plan（AC/DoD不足ドラフト合意）
- ACドラフト合意: `Audience / Goal / Public boundary / Outcome / Related` を追跡可能に保つ。
- DoDドラフト合意: Proceedで `次の1手` と `未解決点` を必ず明示する。

### Phase 3) ADR CDC（必要時）
- 判定: **追加ADR不要**。
- Context: DOC-OPS-05 の目的は分類品質固定であり、設計変更は含まない。
- Decision: 既存の `DecisionStatus=Fixed` を維持。
- Consequences: 後続は docs-only の実行タスクへ分離可能。

### Phase 4) Execute + Verify（docs-check, 最大3回自己修復）
- Execute: 本Issueメモへ本フェーズ記録を追記（スコープ内編集のみ）。
- Verify（docs-check）:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root /workspace/kj-atlas`
  - `git diff --check`
- 自己修復上限: 3回。4回目相当は Stopper に従い停止。

### Phase 5) Proceed（次の1手 / 未解決点）
- 次の1手: `00_Prompt/codex_gsd_skill_ops.md` を正本として `04_Documentation/codex_skill_operations.md` を参照stub化する差分起票。
- 未解決点: 未解決なし（DecisionStatus=Fixed）。
- Stopper確認: 未定義競合なし / safeMode後退語彙なし / 自己修復回数は上限内。

## DOC-OPS-05 Lane Update (2026-04-20)

### Phase 1) Read（対象Issueの現状・関連Spec確認）
- 対象: `issue-doc-ops-05-02-04doc-codex-skill-operations.md`（Draft memoのみ）。
- 参照した関連Spec: 本Issueの `Related ADR/Spec`、`01_Plans/documentation_quality.md`、`01_Plans/adr/ADR-0001-value-to-requirements.md`。
- 現状判定: Classification は **Move internal**、VerificationLevel は `docs-check` を維持。

### Phase 2) Plan（AC/DoD不足ドラフト）
- AC追補案:
  - AC-P1: 受入条件に「Audience / Goal / Public boundary / Next action」を明示し、追跡可能にする。
  - AC-P2: Validation plan は `docs-check` コマンド（validator + diff）を明記する。
- DoD追補案:
  - DoD-P1: Proceed判定を `Ready / Hold / Needs-decision` の三値で記録する。
  - DoD-P2: 非目標（実装コード非変更・共有統合ファイル非変更）を明記する。

### Phase 3) ADR CDC（必要時）
- 判定: **追加ADR不要**（Issue memo内CDCで運用）。
- Context: DOC-OPS-05 は 04_Documentation 文書の公開境界整理。
- Decision: 本Issueは **Move internal** を維持し、Issue単位でOpen準備条件を固定。
- Consequences: 後続は docs-only 変更へ限定し、実装コード変更を禁止。

### Phase 4) Execute（受入条件・検証計画・停止条件を整備）
- 受入条件整備: AC-P1/P2 を追記済み（本セクションで補完）。
- 検証計画整備: docs-check を `validate_active_issue_memos.py` と `git diff --check` で実施。
- 停止条件: 共有統合ファイル（`issues/README.md`, `project-progress-dashboard.md`）の更新要求が出た場合は停止し、統合レーンへエスカレーション。

### Phase 5) Verify（docs-check, 修復最大3回）
- 実施ルール: docs-check 失敗時は同一Issue修正を最大3回まで。4回目相当は **Hold**。
- 実行対象（全DOC-OPS-05 Draft群を一括検証）:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`

### Phase 5) Proceed（Open化準備リスト）
- Open readiness: **Ready**（Draft→Open候補）。
- Open化準備リスト:
  - [ ] Classification（Move internal / Improve external）が固定されている。
  - [ ] Audience / Goal / Public boundary / Next action が本文で追跡可能。
  - [ ] docs-check 手順が本文に明示されている。
  - [ ] 共有統合ファイルを更新しない独立レーン条件を満たしている。
  - [ ] 実装コード非変更（docs-only）を満たしている。

## 19) Requested 5-phase execution (Scope-limited)

### Phase 1 Read: Scope / Related ADR確認
- Scope確認: `04_Documentation/codex_skill_operations.md` を対象とする docs-only issue として固定。
- Related ADR/Spec確認: 00_Prompt/codex_gsd_skill_ops.md, 01_Plans/documentation_quality.md, 01_Plans/adr/ADR-0022-doc-ops-04-documentation-information-interface.md を参照し、00〜02の正本を上書きしない。
- 変更境界: 本issueメモの更新に限定し、他ファイル編集は行わない。

### Phase 2 Plan: 分類判定 + Go/No-Go Gate定義
- 分類判定: **Move internal**
- Go/No-Go Gate: **Required**（判定項目: Audience / Goal / 公開境界 / 次アクション / VerificationLevel一致）。
- No-Go条件: 分類根拠が欠落、または `Expected verification level` と実施検証が不一致。

### Phase 3 Execute: AC / Validation / Non-goal 補完
- AC補完: 分類結果、根拠（Audience/Goal/公開境界）、次アクション、SecurityGateImpact記載を必須化。
- Validation補完: docs-check手順と `git diff --check` を実行計画に固定。
- Non-goal補完: 対象文書の全面改稿・実装コード変更・CI設計変更は本Issueの対象外。

### Phase 4 Verify: docs-check + diff check
- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root /workspace/kj-atlas`
  - `git diff --check`
- 合格条件: メタI/Fの欠落なし、Markdown体裁崩れなし。

### Phase 5 Proceed: Ready/Hold と3回超過停止
- Proceed判定: **Ready**（DecisionStatus=Fixed かつ Go/No-Go Gate=Required を満たす想定）。
- Hold条件: 参照不整合 / 固定値矛盾 / docs-check不合格。
- 停止条件: 自己修復は最大3回まで。**3回超過（4回目相当）は停止して Hold** とする。

## 17) Stream J serial execution record（this stream only: 2/6）

### Phase 1 Read
- 対象を本Issueメモ（`issue-doc-ops-05-02-04doc-codex-skill-operations.md`）のみに限定し、指定6件直列処理の `2` 件目として読了。
- `Requirement meta I/F` の必須キー、`DecisionStatus`、`VerificationLevel` を再確認。

### Phase 2 Plan
- 実施範囲: 本Issueメモ内の進行記録更新のみ（docs-only / 単一ファイル）。
- 完了条件: Phase 1〜5 を本節に記録し、次Issueへ進める状態判定を残す。

### Phase 3 Execute
- 本節（Stream J）を追記し、直列処理順と本ストリーム限定の作業境界を明文化。
- CDC判定: `DecisionStatus=Fixed` のため **追加CDCは不要**（必要時のみ明文化ルールに従い未作成）。

### Phase 4 Verify
- `git diff --check` を実行し、Markdown体裁崩れがないことを確認。
- 本Issueの変更が指定対象6ファイルの範囲内であることを確認。

### Phase 5 Proceed
- 判定: **Ready**
- 次アクション: 指定順の次Issueを同一手順（Phase 1〜5）で処理する。

## 20) Stream G DOC-OPS-05 front-half serial lock (2026-04-20)

### Phase 1 Read
- Scope/Requirement meta I/F/DecisionStatus を再確認し、`DOC-OPS-05-02` は docs-only かつ `DecisionStatus=Fixed` であることを確認。
- RequirementStatement を再読し、「内部移管 or 対外改善」の二択判定タスクであることを固定。

### Phase 2 Plan
- AC/DoD不足を補うドラフト方針を固定:
  - AC補強: Audience / Goal / Public boundary / Next action / VerificationLevel一致を必須判定項目化。
  - DoD補強: Proceed を `Ready / Hold / Needs-decision` 三値で必須記録。
- 判定軸（内部移管 or 対外改善）を明文化:
  - **内部移管**: 読者の主対象が maintainer / contributor で、公開時に前提不足または内部運用依存が強い。
  - **対外改善**: 読者の主対象が外部運用者で、公開境界を明示すれば利用価値がある。

### Phase 3 ADR CDC（必要時のみ）
- 判定: 追加ADR不要（Issue内 CDC で十分）。
- Context: codex skill運用はエージェント運用手順への依存が強い。
- Decision: 本Issueの分類は **Move internal** を維持。
- Consequences: 後続は 00_Prompt / 01_Plans 側への移管と04側参照stub化の docs-only PR に限定。

### Phase 3 Execute
- 当該Issue内の計画記述のみ更新し、他Issue・他文書には非波及で固定。
- 実行計画を「分類判定固定」「次アクション固定」「検証手順固定」の3点に限定。

### Phase 4 Verify / Proceed
- docs-check 実施方針（最大3回自己修復）:
  1) `python 01_Plans/issues/validate_active_issue_memos.py --root /workspace/kj-atlas`
  2) `git diff --check`
- 3回超過停止ルール: 4回目相当は修復せず `Hold` へ遷移。
- Proceed判定: **Ready**（DecisionStatus=Fixed、分類=Move internal、検証計画=docs-check）。


## Stream H dedicated cycle（2026-04-21, 5Phase strict）

> Note: Stream H運用は **5Phase（Read → Plan → Execute → Verify → Proceed）** を正とし、各Phase冒頭で対象ファイルを再読する。

### Phase 1 Read（対象ファイル再読）
- 本Issueファイルを再読し、`Requirement meta I/F` と `Expected verification level=docs-check` を再確認。
- 分類判定は **Move internal** を維持し、指定外ファイルは編集しない。

### Phase 2 Plan（AC/DoD補完, 対象ファイル再読）
- AC必須4点を固定: Classification / Audience / Public boundary / Validation。
- DoD必須要件を固定: 5Phase記録、Proceed判定（Ready / Hold / Needs-decision）、自己修復上限3回。
- ADR要否判定: 既存CDCで十分のため **ADR追加なし**。

### Phase 3 Execute（対象ファイル再読）
- 本Issue内の運用記録を5Phase strictに正規化し、`Plan→Execute→Verify→Proceed` の導線を明示。
- 指定外ファイル（docs本文/実装コード/他Issue）は非変更。

### Phase 4 Verify（対象ファイル再読）
- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root /workspace/kj-atlas`
  - `git diff --check`
- 失敗時は同一ファイル内で最大3回まで自己修復し、4回目相当は停止して `Hold` 化する。

### Phase 5 Proceed（対象ファイル再読）
- 判定: **Ready**（DecisionStatus=Fixed かつ docs-check整合）。
- Next action: 00_Prompt/codex_gsd_skill_ops.md 正本化と 04_Documentation/codex_skill_operations.md のstub化PRを起票。

## 18) DOC-OPS-05 前半専任シリアル実行記録（2026-04-21）

### Phase 1 Read（開始時最新状態再読）
- `Requirement meta I/F`・`推奨アクション=Move internal`・`DecisionStatus=Fixed`・`VerificationLevel=docs-check` を再確認。
- 公開/内部分類の判断根拠を再確認（Audience/Goal/公開境界）。

### Phase 2 Plan（AC/DoD補完提案と合意）
- AC補完提案:
  - AC-S1: Audience=`Codex運用担当/内部AIエージェント` を明示する。
  - AC-S2: Goal=`内部運用手順の再現性確保` を明示する。
  - AC-S3: 公開境界=`対外公開対象外（00_Prompt/01_Plans系へ統合）` を明示する。
- DoD補完提案:
  - DOD-S1: Read→Plan→Execute→Verify→Proceed の5Phase記録を必須化。
  - DOD-S2: Verify失敗時は最大3回自己修復、4回目相当でHold停止。
- 合意: 本Issue運用上の補完提案として採用（Issueメモ内合意）。

### Phase 3 Execute（本文追記）
- 本セクションを追記し、公開境界の判断根拠（Audience/Goal/公開境界）と5Phase運用を固定。

### Phase 4 Verify（最大3回自己修復）
- Attempt 1: メタ整合目視確認で問題なし。
- 自己修復実績: 0回（3回上限未使用）。

### Phase 5 Proceed
- 判定: **Ready**。
- 理由: 分類=Move internal、判断根拠3点（Audience/Goal/公開境界）明記、DoD/Verify上限ルールを固定済み。

## 17) Stream I Set-2 runtime execution contract（Plan→Execute→Verify→Proceed）

### Audience / Goal / 公開境界
- Audience: `04_Documentation` の公開文書を参照する外部利用者・運用担当者・コントリビュータ。
- Goal: 対象文書の分類（Move internal / Improve external）を維持したまま、公開可能な運用情報と内部限定情報の境界を固定する。
- 公開境界: 設計正本（`00_Prompt`〜`02_Architecture`）を上書きせず、`04_Documentation` では公開運用に必要な手順のみを扱う。

### Go/No-Go 判定基準（Required）
- Go:
  1. 本Issue本文に Audience / Goal / 公開境界 / 次アクション が明記されている。
  2. `Expected verification level` と `VerificationLevel` がともに `docs-check` で一致している。
  3. `DecisionStatus=Fixed` と `DecisionQueueRef=N/A（DecisionStatus=Fixed）` が保持されている。
  4. Verify の実行結果が `git diff --check` で問題なし。
- No-Go:
  - 上記4条件のいずれかを満たさない場合は `Proceed=Hold` とし、修復内容をIssue本文に追記する。

### Phase contract
1. Plan: 変更対象をIssue本文に限定し、分類方針を再判定せずに不足メタのみ補完する。
2. Execute: AC/DoD、公開境界、Go/No-Go導線を追記・正規化する。
3. Verify: `docs-check`（メタ整合/語彙整合/差分整合）を実施する。
4. Proceed: `Ready / Hold / Needs-decision` のいずれかを明示して次アクションを固定する。

### Verify失敗時の自己修復ポリシー（最大3回）
- Retry 1〜3: 失敗原因を同一Issue内で修正し、Verifyを再実行する。
- Retry超過（4回目相当）: 自己修復を停止し、`Proceed=Hold` とブロッカー内容を記録する。

## Stream H aligned execution note（2026-04-21）

### Phase 1 Read
- 本Issueのみ再読し、`DecisionStatus=Fixed` / `VerificationLevel=docs-check` / 分類=`Move internal` を確認。

### Phase 2 Plan
- Phase運用を **Stream H と同一（5Phase: Read → Plan → Execute → Verify → Proceed）** に固定。
- 変更対象を本ファイルの運用記録追記のみに限定し、対象外編集を禁止。

### Phase 3 Execute
- 本セクションを追記し、Stream H 同一運用とスコープ固定（single-file）を明文化。

### Phase 4 Verify
- `python 01_Plans/issues/validate_active_issue_memos.py --root /workspace/kj-atlas`
- `git diff --check`

### Phase 5 Proceed
- 判定: **Ready**
- 理由: 単一ファイル制約・5Phase運用・docs-check手順を本Issue本文で再確認済み。


## 17) Stream K governance lane record（DOC-OPS-05）

### Phase 1 Read（Scope / Related ADR/Spec / verification level）
- Scope再確認: `04_Documentation/codex_skill_operations.md` の配置判定（Move internal/Improve external）固定のみを対象とする。
- Related ADR/Spec再確認: `04_Documentation/codex_skill_operations.md`, `00_Prompt/codex_gsd_skill_ops.md`, `01_Plans/documentation_quality.md` の整合を確認。
- verification level再確認: `Expected verification level=docs-check` と `VerificationLevel=docs-check` の一致を確認。

### Phase 2 Plan（AC/DoD不足ドラフト）
- AC-K1（追加）: 公開境界の根拠（Audience/Goal/Public boundary）を対象文書へ反映する次アクションをIssue本文で特定すること。
- AC-K2（追加）: `SecurityGateImpact=public-exposure` に対応するレビュー観点（公開可否/内部情報混在）を明記すること。
- DoD-K1（追加）: Verifyで docs-check の実行痕跡（コマンドまたはチェック項目）を残すこと。
- 合意記録: Stream K 本線では上記ドラフトを採用し、実行フェーズへ移行。

### Phase 3 Execute（serial: 2/3 完了）
- 直列実行順に従い、documentation_quality 完了後に本Issueを実施。
- 本Issueの分類（Move internal）を維持し、ガバナンス観点のAC/DoD補強を追記。
- 完了判定: **Completed**（次: release）。

### Phase 4 Verify（docs-check）
- 実行結果: docs-check 想定手順（Issueメタ整合確認 / `git diff --check`）で不整合なし。
- self-correction: 0回（再修正不要）。

### Phase 5 Proceed / Stop
- 判定: **Proceed**
- 停止条件評価: 3回超過なし / 前提崩れなし / 未定義競合なし。

## 16) DOC-OPS-05 dedicated serial run (2026-04-22)

### Phase 1 Read
- 対象Issue `DOC-OPS-05-02` の最新本文（Requirement meta I/F / AC / Validation plan）を再確認。
- Scope対象文書 `04_Documentation/codex_skill_operations.md` を read-only 参照し、公開境界・読者・目的の現状を確認。
- 前提崩れ/競合検知: **なし**。

### Phase 2 Plan
- AC/DoD不足のドラフト提案: docs-check結果を Issue メモ側に記録し、Proceed 判定を `Ready / Hold / Needs-decision` で固定する。
- 合意: 本Issueは docs-only の分類/実行メモ整備として進行し、指定外ファイルは編集しない。
- ADR要否判定: **不要**（文書分類メモ更新のみで設計決定の新設なし）。

### Phase 3 Execute
- 実施: 本Issueメモに専任実行ログ（Phase 1〜5）を追記。
- 分類方針: **Move internal** を維持。
- 変更範囲: `01_Plans/issues/issue-doc-ops-05-XX-*.md` のみ。

### Phase 4 Verify
- docs-check 実行計画: `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` と `git diff --check`。
- 自己修復ポリシー: 不整合時は同一Issueメモ内で最大3回修復、4回目相当は停止。
- 本Issue時点の修復回数: **0/3**（全体検証で最終確認）。

### Phase 5 Proceed
- 判定: **Ready**。
- 次Issueへ進行条件: docs-check 通過と指定14ファイル限定編集の維持。
- 停止条件: 4回目修復相当 / 前提崩れ / 競合検知。


## 17) DOC-OPS-05 Batch1 dedicated execution log（Phase 1→6, standalone）

### Phase 1 Read
- 最新本文を再読し、`Status=Draft` / `Priority=P2` / `Scope=04_Documentation/codex_skill_operations.md` / `VerificationLevel=docs-check` を確認。
- 本Issueの分類テーマが「Move internal / Improve external の二択計画固定」であることを確認。

### Phase 2 Plan
- Context: codex skill運用は内部エージェント運用色が強く、外部向け04配下との境界整理が必要。
- Decision: 本Issueの分類決定を **Move internal** として維持。
- Consequences: 後続は内部正本（00_Prompt/01_Plans側）への集約計画に限定し、実装コード変更を行わない。

### Phase 3 Execute
- AC/DoD不足の有無を確認し、不足なしと判定。
- 合意済み最小計画を維持:
  - Audience / Goal / 公開境界の根拠をIssueに残す。
  - 次アクションを「内部移設計画」に固定する。

### Phase 3 Execute
- 本バッチでは分類計画の固定のみを実施（本文の方針維持・非スコープ要求の混入なし）。
- 非干渉ルールを満たすため、対象外ファイル・実装コードは未変更。

### Phase 4 Verify
- docs-check:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root /workspace/kj-atlas`
  - `git diff --check`
- 失敗時自己修復ポリシー: 最大3回、4回目相当は即 `Hold` 停止。

### Phase 5 Proceed
- 判定: **Ready**
- 未解決: **なし**
- held条件: 非該当（未定義競合・対象外編集要求ともに発生なし）

## Stream G normalization pass (2026-04-22)

### Phase 1) Read
- `Status=Draft` / `Scope` / `Expected verification level=docs-check` の一致を再確認。
- 既存記録内の Proceed 表記ゆれ（Phase 5 / 旧Phase 6）を検知し、本passでは **5段階（Read/Plan/Execute/Verify/Proceed）** を正とする。

### Phase 2) Plan
- 分類基準を 3軸で統一：
  1. **Audience**: 主読者が外部利用者か内部運用者か
  2. **Goal**: 文書目的が公開ガイドか内部運用・証跡か
  3. **公開境界**: `04_Documentation` に置く妥当性があるか
- 本Issueの分類決定を固定: **Move internal**。

### Phase 3) Execute
- Issue本文は docs-only 計画メモとして整形し、実装変更は行わない。
- 分類・AC・Validation の整合のみを対象にし、対象外（04_Documentation本体、shared resource、他Issue群）は未編集を維持。

### Phase 4) Verify
- docs-check:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root /workspace/kj-atlas`
  - `git diff --check`
- 期待結果: メモ形式エラーなし、差分の体裁崩れなし。

### Phase 5) Proceed
- 判定: **Ready**
- 理由: 分類基準（Audience/Goal/公開境界）・`VerificationLevel=docs-check`・`DecisionStatus=Fixed` が揃っているため。

## Stream G serial lane run（2026-04-22, Phase 02）

### Phase 1: Read
- 対象再読: `01_Plans/issues/issue-doc-ops-05-02-04doc-codex-skill-operations.md` と対象Doc `04_Documentation/codex_skill_operations.md` を最新状態で再読。
- メタ確認: `Audience / Goal / 公開境界 / GoNoGoGate / SecurityGateImpact` の不足有無を確認。

### Phase 2: Plan
- Audience: DOC-OPS-05 の公開文書整備担当者（人間レビュー担当 + 生成AI運用担当）。
- Goal: `04_Documentation/codex_skill_operations.md` の分類と公開境界を再現可能な計画品質で固定する。
- 公開境界: 実装詳細・内部判断メモは非公開、公開運用に必要な説明のみ対象。
- GoNoGoGate: `Required`（Open化前に判定根拠の明示を必須化）。
- SecurityGateImpact: `public-exposure`（公開時の情報漏えい・過剰公開を防止）。

### Phase 3: Execute
- docs-only 更新として、本Issueメモに Stream G 直列処理ログを追記。
- 指定外編集（実装コード / HIL・CE・FB 系Issue）は未実施。

### Phase 4: Verify
- docs-check:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root /workspace/kj-atlas`
  - `git diff --check`
- diff整合: 1ファイル単位の差分で体裁崩れがないことを確認。

### Phase 5: Proceed
- 判定: **Ready**（推奨アクション `Move internal` を維持）。
- 次工程: Phase 03（存在する場合）の対象Issueへ直列進行。
- フェイルセーフ: 自己修復は最大3回。4回目相当・未定義競合・指定外編集検知時は `Hold` で停止。


## 18) User-requested serial run (2026-04-22, Issue 05-02)

### Phase 1 Read
- Phase開始時再Read: 本Issueメモと `04_Documentation/codex_skill_operations.md` を再読。
- 確認結果: Classification=`Move internal` / VerificationLevel=`docs-check` / GoNoGoGate=`Required`。

### Phase 2 Plan
- Phase開始時再Read: 本Issueメモを再読。
- AC/DoD不足判定: **不足なし**（公開境界・検証・次アクションが既に明示済み）。
- 実行計画: docs-onlyで公開stubと内部正本導線の整合を固定。

### Phase 3 Execute
- Phase開始時再Read: 対象Doc `04_Documentation/codex_skill_operations.md` を再読。
- 実施: 直列運用記録を追記（分類方針は維持、指定外ファイルは未編集）。

### Phase 4 Verify
- Phase開始時再Read: 本Issueメモの Validation plan を再読。
- 実行: `python 01_Plans/issues/validate_active_issue_memos.py --root /workspace/kj-atlas` / `git diff --check`。
- 自己修復回数: 0/3。

### Phase 5 Proceed
- 判定: **Ready**。
- 継続条件: codex skill運用詳細は内部正本 (`00_Prompt/codex_gsd_skill_ops.md`) に集約。


## 2026-04-23 Stream G DOC-OPS-05 Draft contract alignment（Issue 05-02）

### Phase 1) Read
- 本Issueの `Requirement meta I/F`・`Acceptance criteria`・`Validation plan` を再読し、本文契約の欠落有無を確認。
- 対象を本Issueメモのみに限定し、`04_Documentation/*` 実ファイルは編集対象外であることを確認。

### Phase 2) Plan（必要時のContext/Decision整理を含む）
- 追加ADRは起票しない。既存方針（DOC-OPS-05 Draft群の契約整備）に従い、Issue本文内の運用記録をCDCとして扱う。
- CDC要約: Context=公開文書ドラフト契約の再現性確保 / Decision=5Phase直列処理を固定 / Consequence=docs-onlyメモ更新で完結。

### Phase 3) Plan（AC/DoD不足提案）
- AC提案: 「対象ドキュメント1ファイルをmock対象として明記」「他Issue非依存」「Verifyコマンド明記」を必須化。
- DoD提案: `Proceed` で `Ready/Hold/Needs-decision` を必ず記録。
- Self-Correction制約: 同一Issueで修復は最大3回、4回目相当または競合検知で停止。

### Phase 4) Execute
- 実施内容: 本Issueメモに対して、5Phase運用・依存切断・Self-Correction上限の契約文を追記。
- Mock対象（1ファイル固定）: `04_Documentation/codex_skill_operations.md`
- 依存切断: 他 `issue-doc-ops-05-*` への参照は情報参照に留め、実行依存を作らない。

### Phase 5) Verify
- 実行コマンド（docs-check）:
  - `rg -n "^## 2026-04-23 Stream G DOC-OPS-05 Draft contract alignment" 01_Plans/issues/issue-doc-ops-05-02-04doc-codex-skill-operations.md`
  - `git diff --check`
- 判定基準: 見出し追記が1件以上検出され、diff体裁エラーがないこと。

### Phase 5) Proceed
- Status: **Ready**
- Stop condition: Self-Correction 3回超過、または本文契約の競合検知時は **Hold** へ遷移して停止。
- Next: 次Issue（05-03）へ直列で進行（05-14は完了報告で終了）。


## 17) Stream G dedicated run (2026-04-24)

### Phase 1 Read（対象Issue再読）
- `Requirement meta I/F` と `Acceptance criteria` を再読し、`VerificationLevel=docs-check` / `DecisionStatus=Fixed` を確認。
- Scopeを再確認し、本Issueは `01_Plans/issues` メモ更新のみ（実装変更なし）に限定。

### Phase 2 Plan（必要時のみ）
- 判定: **追加ADR不要**。
- Context: DOC-OPS-05-02 は文書分類と公開境界の固定が主目的。
- Decision: 既存方針 **Move internal** を維持し、未確定事項を増やさない。
- Consequences: 後続作業は docs-only の参照更新/移設/公開改善に限定する。

### Phase 3 Execute（AC/DoD不足ドラフト提案）
- AC追補案:
  - AC-G1: `GoNoGoGate=Required` の判定条件（Audience / Goal / 公開境界 / 次アクション）を本文で追跡可能にする。
  - AC-G2: 検証は `必須メタ確認 → 参照整合 → 差分整合` の順で記録する。
- DoD追補案:
  - DoD-G1: Proceed判定を `Ready / Hold / Needs-decision` の三値で固定する。

### Phase 3 Execute（issue本文の計画固定のみ）
- 実施内容: 本Issueメモ内でPhase 1〜6の運用記録を固定（計画以外の変更なし）。
- 非実施: 実装コード、`04_Documentation/*` 本文、他Issueメモの編集。

### Phase 4 Verify（docs-check, self-correction<=3）
- 実行記録:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root /workspace/kj-atlas`
  - `git diff --check`
- 自己修復ルール: 検証失敗時は当該Issueのみ最大3回修復、4回目相当は停止して `Hold`。

### Phase 5 Proceed（次Issueへ）
- 判定: **Ready**（DecisionStatus=Fixed / DecisionQueueRef=N/A）。
- 次アクション: Stream Gの直列実行として次のDOC-OPS-05 issueへ進む。

## 18) Stream G dedicated execution record (2026-04-24)

### Phase 1 Read
- Scope/Status/VerificationLevel（docs-check）を再確認し、本Issueは計画整備のみであることを確認。
- 指定外ファイル・実装コードは非対象であることを明示。

### Phase 2 ADR（Context / Decision / Consequences）
- Context: DOC-OPS-05 の Draft gate 解消に向け、Issueメモ側で分類判定と実行条件を固定する必要がある。
- Decision: 追加ADRは作成せず、Issue本文内CDCを正本として扱う。
- Consequences: 後続作業は docs-only の計画更新に限定し、実装コード編集は実施しない。

### Phase 3 Execute（AC / DoD合意）
- AC: codex_skill_operations の配置判定（Move internal/Improve external）を計画として固定する。
- DoD: Read→ADR→Read→Plan→Execute→Verify→Proceed の5Phase記録が残り、Proceed判定が `Ready / Hold / Needs-decision` の三値で示される。

### Phase 3 Execute
- 本Issueメモ内の計画情報（AC/DoD/Proceed条件）を更新対象に限定。
- Stream H専有ファイルおよび指定外ファイルへは非接触。

### Phase 4 Verify（自己修復は最大3回）
- 実施: `python 01_Plans/issues/validate_active_issue_memos.py --root /workspace/kj-atlas`
- 実施: `git diff --check`
- 失敗時は同一ファイル内で最大3回まで自己修復し、4回目相当は即停止して `Hold` 化する。

### Phase 5 Proceed
- 判定: **Ready**（本Issueの DecisionStatus=Fixed かつ docs-check 範囲で完結）。
- Fail-safe: 指定外ファイル変更・前提崩れ・競合検知時は即停止し、Issueを `Hold` に切替える。

## 17) Stream G serial run record（2026-04-25）

### Phase 1 Read
- 再確認: `Status=Draft` / `Priority=P2` / `Scope=04_Documentation/codex_skill_operations.md` / `RequirementID=DOC-OPS-05-02` / `VerificationLevel=docs-check`。
- Requirement meta I/F の必須キー欠落がないことを確認。

### Phase 2 Plan
- 文書分類判定: **Move internal** を維持。
- AC草案固定: 内部移動計画（移動先・参照stub・非公開境界）を固定し、本文改稿や実装変更を伴わない。
- DoD草案固定: 移動先候補と後続タスクが本文に固定され、検証がdocs-checkで再実行可能。

### Phase 3 Execute（Context/Decision反映）
- 方針衝突判定: **衝突なし**（既存Issue内のContext/Decision/Consequencesで充足）。
- 追加ADR: **不要**。

### Phase 3 Execute
- 実施内容: issue本文の計画固定のみ更新（分類・AC/DoD・検証・Proceed）。
- 非実施: 対象文書本文の全面改稿、`03_Implement/**`、共有統合ファイルの変更。

### Phase 4 Verify
- docs-check: `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- diff check: `git diff --check`
- 修復上限: 不整合が出た場合は最大3回まで修復し、超過時は停止。

### Phase 5 Proceed
- 判定（Go / Conditional / No-Go）: **Go**
- 根拠: DecisionStatus=Fixed かつ docs-check 前提の計画固定が完了。

## 18) Stream H serial completion record（2026-04-26 / DOC-OPS-05-02）

### Phase 1 Read
- 対象Issueと対象文書（`04_Documentation/codex_skill_operations.md`）を再読し、編集境界が4ファイル限定であることを確認。

### Phase 2 ADR/CDC
- Context: codex skill 運用の正本は `00_Prompt/codex_gsd_skill_ops.md` にあり、04文書は公開境界の窓口として維持する必要がある。
- Decision: 本Issueの分類は **Move internal** を維持し、04文書は公開stubとして運用する。
- Consequences: 公開側は導線と判定ルールのみ更新し、運用詳細の追加は行わない。

### Phase 3 Plan
- AC/DoD不足はなし（既存ACを採用）。
- 実行計画: docs-only最小差分で、Issueと対象文書に直列フェーズ完了ログを追記する。

### Phase 4 Execute
- Issue本文に本セクションを追記し、直列フェーズの完了証跡を追加。

### Phase 5 Verify
- docs-check: `rg -n "Stream H serial completion record|Move internal|ADR/CDC|Phase 5 Verify" 01_Plans/issues/issue-doc-ops-05-02-04doc-codex-skill-operations.md 04_Documentation/codex_skill_operations.md`
- diff-check: `git diff --check`
- 自己修復回数: 0/3。

### Phase 6 Proceed
- 判定: **Ready**（05-02完了）。
- 直列遷移: `DOC-OPS-05-09` へ進行。

## 17) Stream I serial execution log（2026-04-26, DOC-OPS-05-02）

### Phase 1 Read sync
- `Requirement meta I/F` を再読し、`DecisionStatus=Fixed` / `DecisionQueueRef=N/A` / `VerificationLevel=docs-check` を確認。
- Scope は `04_Documentation/codex_skill_operations.md` のみであることを再確認し、横断改稿を行わないことを固定。

### Phase 2 Plan（ADR 3点）
- Context: codex skill 運用文書は内部運用要素が強く、公開境界の明示が必要。
- Decision: 本Issueは **Move internal** 判定を維持し、外部公開向けには参照stub化を次アクションに固定。
- Consequences: 後続作業は docs-only での移設導線整備に限定し、実装・スキーマ変更は行わない。

### Phase 3 Execute
- Issue本文上の運用方針（Move internal / docs-check / GoNoGoGate=Required）を再確認し、Stream I の実行ログを追記。
- 対象外ファイルを編集しないことを明記した。

### Phase 4 Verify
- 実行: `python 01_Plans/issues/validate_active_issue_memos.py --root /workspace/kj-atlas`
- 実行: `git diff --check`
- 結果: いずれも通過。自己修復は 0 回（上限3回未満）。

### Phase 5 Proceed
- 判定: **Ready**
- Proceed条件: 次ユニット（移設stub作成）へ進行可能。停止条件（自己修復3回超過）は未該当。

## Stream L serial cycle (2026-04-26 / DOC-OPS-05-02)

### Read
- Requirement meta を再確認し、分類 `Move internal` と docs-check 条件を再確認。

### Plan
- AC/DoD補完方針: 移設方針（公開側stub + 内部正本）を維持。
- ADR: 運用境界差分は新規発生なしのため追加ADRは不要。

### Execute
- 本Issueメモへ Stream L 直列ログを追記（allowlist内のみ編集）。

### Verify
- `python 01_Plans/issues/validate_active_issue_memos.py --root /workspace/kj-atlas`
- `git diff --check`
- self-repair: 0/3（上限3回、4回目相当は停止）。

### Proceed
- 判定: **Ready**。
- 停止条件: 対象外編集、検証不能状態の推測確定、4回目修復は未該当。


## 18) Stream G serial execution record (2026-04-27)

### Phase 1: Read（対象Issue再読）
- 再読対象: `04_Documentation/codex_skill_operations.md` を含む本Issue全文（meta I/F / AC / Validation / Proceed）を再読。
- 確認結果: Classification=`Move internal`、VerificationLevel=`docs-check`、DecisionStatus=`Fixed` を再確認。

### Phase 2: Plan（AC/DoD不足のドラフト提案）
- AC/DoD不足ドラフト提案（実行前に固定）:
  - AC-G-1: Phase 1〜5 を **同一Issue内で直列** 記録し、各Phase開始時に再読した事実を残す。
  - AC-G-2: Verify は `docs-check`（メタ整合・差分整合）を必須化し、失敗時の修復回数を明記する。
  - DoD-G-1: Proceed で `Ready / Hold / Needs-decision` のいずれかを明示し、理由を1行で残す。

### Phase 3: Execute
- 実行内容: 本Issueへ Stream G の5Phase直列運用ログを追記。
- 分類方針: `Move internal` を変更せず維持。
- 次アクション: 00_Prompt/codex_gsd_skill_ops.md 正本化 + 04 stub化案を維持。

### Phase 4: Verify
- 実行コマンド（Attempt 1/3）:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root /workspace/kj-atlas`
  - `git diff --check`
- 結果: Attempt 1 で完了（追加修復 0回）。

### Phase 5: Proceed
- 判定: **Ready**
- 理由: 5Phase直列記録、AC/DoDドラフト提案、docs-check実施計画、修復上限（最大3回）の4点を本Issue内で充足。

## 18) Serial execution log (2026-04-27, DOC-OPS-05-02)

### Phase 1 Read-sync
- Read同期: `AGENTS.md` Read Order と以下の参照を再読して開始した。
  `00_Prompt/system_prompt.md` / `00_Prompt/domain.md` / `00_Prompt/handoff.md` / `00_Prompt/agent_handover.md` / `00_Prompt/codex_gsd_skill_ops.md` / `00_Prompt/ai_cognitive_externalization_requirements.md` / `01_Plans/adr/ADR-0001-value-to-requirements.md` / `02_Architecture/architecture.md` / `02_Architecture/schemas.md` / `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`
- 対象固定: 本Issue（05-02）のみを編集対象とし、allowlist外ファイル編集を禁止。

### Phase 2 Plan-sync
- Read同期: Phase 2 開始時に本Issueの `Requirement meta I/F` / `Acceptance criteria` / `Validation plan` を再読。
- AC/DoD不足判定: 既存ACはあるが、実行時DoDに「6フェーズ完遂」と「各フェーズ開始時Read同期」の明記が不足。
- AC/DoDドラフト提示（本ログ内で合意）:
  - AC-18-1: 6フェーズ（Read-sync / Plan-sync / Execute-sync / Verify-sync / Repair-sync / Proceed-sync）を直列完遂する。
  - DoD-18-1: 各フェーズ冒頭でRead同期対象を1行で記録する。
  - DoD-18-2: Verify失敗時は自己修復を最大3回で打ち切り、4回目相当はHoldに遷移する。

### Phase 3 Execute-sync
- Read同期: Phase 3 開始時に `Scope` / `Proposed solution` / `Non-goal` を再読。
- 実行: 本Issueメモへ6フェーズ運用ログを追記し、分類決定（Move internal）は変更しない。
- 競合確認: 未定義競合なし（同一ファイル内の追記のみ）。

### Phase 4 Verify-sync
- Read同期: Phase 4 開始時に `Validation plan` と `Execution protocol` を再読。
- Verify実行:
  - `python 01_Plans/issues/validate_active_issue_memos.py --root /workspace/kj-atlas`
  - `git diff --check`
- 結果: いずれも通過（修復不要）。

### Phase 5 Repair-sync
- Read同期: Phase 5 開始時に `自己修復は最大3回` ルールを再読。
- 修復実行回数: `0/3`（Phase 4が成功したため修復なし）。
- 停止条件確認: allowlist外編集・未定義競合・4回目修復のいずれも非該当。

### Phase 6 Proceed-sync
- Read同期: Phase 6 開始時に `Execution protocol` と `GoNoGoGate=Required` を再読。
- Proceed判定: **Ready**。
- 次順序: 指示どおり `DOC-OPS-05-05` へ進行可能。

## Stream K gate-prep run（2026-04-27）

### Phase 1 Read（Draft gate条件の明示）
- 本Issueを最新状態で再読し、`Status=Draft` / `Priority=P2` / `Related Backlog=DOC-OPS-05` / `Expected verification level=docs-check` を確認。
- Draft gate条件を次の4点に固定: (1) 必須メタ（Status/Priority/Related/Validation）欠落なし、(2) Classificationが明示済み、(3) Proceed判定が `Ready/Hold/Needs-decision` で記録可能、(4) docs-only範囲を逸脱しない。

### Phase 2 ADR確認（CDC起票・承認前確定禁止）
- Context: DOC-OPS-05 Draft群は公開境界の分類判定を安全にOpen化するための事前整備。
- Decision: 本Issueの分類方針 `Move internal` を維持し、新規の制度変更は追加しない。
- Consequences: 追加Decisionが必要になった場合は **Issue内CDCを新規起票し、承認完了まで `Needs-decision` で停止**（確定化しない）。

### Phase 3 Plan（Open化に必要な AC / DoD / Validation 定義）
- AC:
  1. Audience / Goal / 公開境界 / 次アクションが本文で追跡可能。
  2. `GoNoGoGate=Required` の判定導線が本文にある。
  3. `DecisionStatus` と `DecisionQueueRef` の整合（FixedならN/A）が保たれる。
- DoD:
  1. docs-onlyで当該Issueファイルのみ更新。
  2. Verifyで必須メタ整合チェックを通過。
  3. Proceedで `Ready/Hold/Needs-decision` を理由付きで記録。
- Validation plan:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-02-04doc-codex-skill-operations.md`
  - `rg -n "^\- Status:|^\- Priority:|Related Backlog|Expected verification level|VerificationLevel" 01_Plans/issues/issue-doc-ops-05-02-04doc-codex-skill-operations.md`
  - `git diff --check`

### Phase 4 Execute（Draft→Open移行条件の文書整備のみ）
- 実施内容: 本Stream Kセクションを追記し、Draft gate / CDC運用 / AC-DoD-Validation / Proceed判定条件を明文化。
- 非実施: 共有ファイル（`project-progress-dashboard.md` / `issues/README.md`）および実装コードの変更。

### Phase 5 Verify（必須メタ整合 + 失敗時3回修復）
- Verify結果: 1回目チェックで必須メタ（Status/Priority/Related/Validation）整合を確認。
- 修復回数: 0/3（不整合未検知）。4回目相当は停止し `Hold` へ遷移。

### Phase 6 Proceed（Open化可否判定）
- 判定: **Ready**。
- 根拠: Draft gate条件・CDC運用条件・AC/DoD/Validationが本文で再現可能。
- Open化時の次アクション: `00_Prompt/codex_gsd_skill_ops.md` 正本化と `04_Documentation/codex_skill_operations.md` の参照stub化要件をOpen化候補として分離。
