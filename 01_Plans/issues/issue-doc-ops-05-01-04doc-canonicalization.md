# Issue Draft: DOC-OPS-05-01 04_Documentation/canonicalization.md の配置見直し

- Type: Documentation quality
- Status: Draft
- Source Issue: N/A
- Priority: P2
- Owner: TBD
- Scope: `04_Documentation/canonicalization.md`
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `04_Documentation/canonicalization.md`, `02_Architecture/schemas.md`, `02_Architecture/architecture.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: `DOC-OPS-05-01`
- RequirementStatement: `04_Documentation/canonicalization.md` を「内部文書へ移動」または「対外文書として改善」のどちらかに分類し、実行計画を固定する。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=`04_Documentation` の文書分類を棚卸し済み`; 操作=対象文書の読者・目的・配置先を判定する; 期待結果=分類結果と次の変更方針が issue と関連文書に残る; 除外=本文の全面改稿や実装修正`
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: docs-check
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A（DecisionStatus=Fixed）

## 1) 課題 / Problem statement

- `04_Documentation/canonicalization.md` が、対外公開文書として維持すべきか、内部文書へ移すべきか未整理。
- 現状のままだと `04_Documentation/` に内部向け情報が残るか、逆に公開候補文書の改善優先度が見えない。
- AIエージェントが外部向け資料を作る際の配置判断が曖昧なままになる。

## 2) 背景 / Context

- 正規化/決定論の説明は設計寄りであり、外部利用者ガイドとしては前提が重い。
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
- 実施方針: `02_Architecture/` or `01_Plans/` へ移設して設計正本として整理する
- 非目標: このIssue単体で対象文書の全文改稿や実装仕様変更は行わない。

## 5) 受入条件 / Acceptance criteria

- [ ] `04_Documentation/canonicalization.md` の分類結果（内部移設 or 対外改善）が本文に明記される。
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
  - `rg -n "Audience|Goal|Non-goal|Outcome|Related" 04_Documentation/canonicalization.md 01_Plans/documentation_quality.md`
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

- 本Issueは `04_Documentation/canonicalization.md` 専用の分類/改善トラッキングメモ。
- 実作業では `01_Plans/minimal-context-triage.md` と関連ADRだけを開き、一覧再読を前提にしない。

---

## 11) Stream G phase record（DOC-OPS-05 front-half: 01-07）

### Phase 1: Read
- メタ抽出結果: `Status=Draft`, `Priority=P2`, `Scope` と `VerificationLevel=docs-check` を確認。
- 重複/矛盾/不足:
  - 重複: 01〜07で同一テンプレのため、判定項目は共通化可能。
  - 矛盾: 本Issue固有の分類方針（Move internal / Improve external）は本文と整合。
  - 不足: Proceed判定（Phase 5）のOpen可否記録が未定義だったため追加。

### Phase 2: Plan
- 1issue 1主責務: **文書配置判定（canonicalization の公開/内部境界固定）**
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
  - `02_Architecture/canonicalization_workflow.md` 新設 + `04_Documentation/canonicalization.md` は参照stub化案を起票する。

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


## 12) Stream H Set1 AC/DoD clarification（Phase 1〜5）

### Phase 1 Read
- 対象Docの現行分類・公開境界・検証レベル（docs-check）を再確認。

### Phase 2 Plan
- AC明確化: Classification / Audience / Public boundary / Validation を必須4点として固定。
- DoD明確化: Phase 1〜5 の記録、Ready/Hold/Needs-decision のProceed判定を必須化。

### Phase 3 Execute
- Issue本文に沿って対象Docへ AC/DoD とPhase記録を追記する実施方針を確定。

### Phase 4 Verify
- `Expected verification level=docs-check` と一致する差分検証（`git diff --check`）を実施。

### Phase 5 Proceed
- 判定: **Ready**（DecisionStatus=Fixed のため追加判断待ちなし）。

### Phase 5 Proceed（次アクション固定）
- Next action: 02_Architecture/canonicalization_workflow.md 新設 + 04_Documentation/canonicalization.md を概要stub化する移設PRを起票する。

## 13) Stream I execution record（DOC-OPS-05 non-conflict lane）

### Phase 1 Read
- 本Issueの Requirement meta I/F、Classification、ValidationLevel を再確認。
- Stream H 専有対象（operations / security / e2e_testing）には非接触で進行することを確認。

### Phase 2 ADR明文化
- Context: 04_Documentation の公開境界と内部向け記述の混在を解消し、公開可能文書の判定を固定する。
- Decision: 本Issueの Classification（Move internal / Improve external）を維持し、AC/DoDの不足はIssue本文で補う。
- Consequences: 後続PRは docs-only で実施し、設計正本（00〜02）を上書きしない。

### Phase 3 Plan
- AC/DoD不足のドラフト提案（合意済み扱い）:
  - AC-I1: Audience / Goal / Non-goal / Public boundary / Outcome / Related を対象文書冒頭に明示。
  - AC-I2: GoNoGoGate=Required の判定条件を本文で再現可能にする。
  - DoD-I1: Read→Plan→Execute→Verify→Proceed の5Phase記録を残す。
- 非目標: 実装コード・CI・Stream H専有ファイルの変更は行わない。

### Phase 4 Execute
- 本Issueの分類方針に沿い、対応する対象文書へ公開境界メタとGo/No-Go判定導線を反映。

### Phase 5 Verify
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

### Phase 2 ADR CDC（必要時のみ）
- 判定: **追加ADR不要**（既存Issue内CDCで十分）。
- Context: DOC-OPS-05は文書本文改稿ではなく「分類判定の品質固定」が主目的。
- Decision: 本Issueの分類は **Move internal** を維持し、判定メタの再現性を優先する。
- Consequences: Open化時の差し戻し理由を「分類メタ不足」に限定できる。

### Phase 3 Plan（AC/DoD不足の補完）
- AC補強: Go/No-Go判定条件（Audience / Goal / 公開境界 / 次アクション）が本文で追跡可能であること。
- DoD補強: Proceed判定を `Ready / Hold / Needs-decision` の三値で明示すること。

### Phase 4 Execute（issue本文整備）
- 既存本文の分類方針を変更せず、メタ整合（DecisionQueueRef正規化・Open判定基準）のみ整備。
- 対象外（`04_Documentation/*` 実体、実装コード、他ストリームIssue）は未変更。

### Phase 5 Verify（docs-check / 自己修復上限3回）
- 実行: `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`
- 実行: `git diff --check`
- 自己修復ポリシー: 不一致が出た場合は当該Issueのみ最大3回修復し、4回目相当で停止。

### Phase 5 Proceed（Open化候補判定）
- Open readiness: **Ready**
- 理由: 分類（Move internal）・検証レベル・GoNoGoGate・DecisionStatusが揃っており、本文改稿タスクと分離可能。
- Open化ラベル候補: `DOC-OPS-05`, `docs-check`, `classification-quality`, `stream-f`.


## 16) Stream G consolidated cycle（Read / CDC / Plan / Execute / Verify / Proceed）

### 1) Read（対象文書再読）
- 対象: `Scope` と `Related ADR/Spec` を再読し、公開境界（Audience / Goal / Non-goal / Public boundary）を再確認。
- 判定: 本Issueは docs-only のため、`03_Implement/**` は変更対象外。

### 2) CDC（Context / Decision / Consequences）
- Context: `DOC-OPS-05-01` は DOC-OPS-05 の文書分類と公開品質を固定するためのDraft。
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
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`
  - `git diff --check`
- フェイルセーフ: 語彙ドリフトが解消不能、または自己修復3回超過時は停止してHold化する。

### 6) Proceed（issue状態更新案）
- 状態更新案: **Ready**（DecisionStatus=Fixed）。
- 保留条件: 参照リンク切れ / 固定値矛盾 / 語彙ドリフト未解消のいずれかを検知した場合は **Hold**。

## 16) Stream H canonical consolidation (Phase 1〜5)

### Phase 1 Read（14 Draft共通テンプレ差分抽出）
- 共通テンプレ（Requirement meta I/F, Acceptance criteria, Validation plan, Authoring Checklist）を再確認し、Issue固有差分は `Scope` / `Related ADR/Spec` / `推奨アクション` のみを主差分として固定。
- 対象: `04_Documentation/canonicalization.md`

### Phase 2 ADR CDC必要性判定
- 判定: **追加ADR不要**（Issue本文の CDC 記録で十分）。
- 条件: 既存ADR/Specへの参照で判断根拠が追跡可能な場合、ADR新設は行わない。

### Phase 3 Plan（優先順）
1. Priority 1: 分類決定（Move internal / Improve external）を本文で固定。
2. Priority 2: Audience / Goal / Public boundary / Outcome / Related の追跡可能性を確認。
3. Priority 3: docs-check（`rg` / `git diff --check`）で体裁と導線を検証。

### Phase 4 Execute（文書配置見直し）
- Classification execution: **Move internal**
- 実行境界: Docs-only（`03_Implement/**` 非変更）。
- Move internal の場合は公開スタブ化と内部正本導線を優先し、Improve external の場合は公開可読性・公開境界の明示を優先。

### Phase 5 Verify（リンク・見出し・品質ゲート）
- Verify command set:
  - `rg -n "^#|^##|Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go" 04_Documentation/canonicalization.md 01_Plans/documentation_quality.md`
  - `git diff --check`
- 自己修復ポリシー: 不整合は最大3回まで修復し、4回目相当は停止してブロッカー化する。

## 17) Stream J execution record（DOC-OPS-05 target 05-01..05）

### Phase 1 Read（再Read実施）
- Date: 2026-04-16
- 再Read対象: `04_Documentation/canonicalization.md` と `01_Plans/documentation_quality.md`（QG-1〜QG-6）
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
- docs-check: `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go" 04_Documentation/canonicalization.md 01_Plans/documentation_quality.md`
- formatting-check: `git diff --check`
- Fail-safe: 自己修復は最大3回。3回超過時は停止して Hold 化する。

### Phase 5 Proceed（再Read実施）
- Date: 2026-04-16
- 状態: **Ready**（検証通過時）。
- 次アクション: 同一5件セット（05-01..05）の残差分と整合を保ったまま次サイクルへ進行。


## 18) Stream I serial execution (Phase 1..5 fixed, 2026-04-16, DOC-OPS-05-01)

### Phase 1: Read
- Read: Requirement meta I/F・Scope・Related ADR/Spec・推奨アクション（Move internal）を再確認。
- Read: 既存のStream記録との差分を確認し、本実行は **Phase 1..5固定** で進行することを明記。
- Read outcome: 対象は docs-only、`04_Documentation/canonicalization.md` の分類・改善計画に限定。

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
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`
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
- 推奨確認: `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go" 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`
- 体裁確認: `git diff --check`

### Phase 5: Proceed（対象ファイル再読）
- 本ファイルを再読したうえで状態を判定し、`Ready / Hold / Needs-decision` を記録。
- 判定: **Ready**（現時点で保留なし）。

## 17) Stream G serial pass（2026-04-16, docs-only）

### Phase 1: Read
- Read target pair: `issue-doc-ops-05-01-04doc-canonicalization.md` + `04_Documentation/canonicalization.md`.
- Reconfirmed scope guard: docs-only（`03_Implement/**` と `02_Architecture/**` は参照のみ）。

### Phase 2: Classification decision
- Decision: **Move internal**（維持、再判定なし）。
- Rationale snapshot:
  - Audience は公開向け概要のみで十分。
  - canonicalization の詳細運用/契約は内部正本（設計/計画）管理が妥当。
  - public-exposure 境界の誤解を避けるため、公開文書は stub 方針を継続。

### Phase 3: ADR CDC（必要時のみ）
- 判定: **追加ADR不要**。
- 既存の Context/Decision/Consequences を本Issue内CDCとして維持。

### Phase 4: Verify（docs-check）
- `rg -n "DOC-OPS-05 Classification|Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go" 04_Documentation/canonicalization.md`
- `git diff --check`
- 自己修復上限: 3回（4回目相当は停止/Hold）。

### Phase 5: Proceed
- Status: **Ready**
- Next issue handoff condition: 公開境界未確定/責務分離矛盾/指定外編集要求が発生した場合は停止。


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

### Phase 6) Proceed（次Issueへ）
- 判定: **Proceed可能**（致命競合なし）。
- 次Issueへ進む前提: 同一ルール（Scope固定 / docs-check / 3回上限）をそのまま適用する。

## 17) 2026-04-17 Focused cycle（Target限定: issue + canonicalization）

- Target files: `01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`, `04_Documentation/canonicalization.md`
- Prohibition: **他4xドキュメント編集禁止**

### Read
- 本IssueのClassification（Move internal）と `04_Documentation/canonicalization.md` の公開境界メタを再確認。

### CDC（必要時）
- 判定: **今回は追加CDC不要**（DecisionStatus=Fixed / 既存CDCで充足）。

### Plan
- 変更を2ファイルに限定し、公開境界の再確認記録のみを追記する。

### Execute
- 本Issueに本フェーズ記録を追加し、対象文書に同一フェーズ記録を同期する。

### Verify（<=3）
- Verify-1: `rg -n "Focused cycle|Phase|Verify（<=3）|他4xドキュメント編集禁止" 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md 04_Documentation/canonicalization.md`
- Verify-2: `git diff --check`
- Verify-3: `git diff -- 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md 04_Documentation/canonicalization.md`

### Proceed
- 判定: **Ready**
- 次アクション: Move internal方針は維持し、公開文書は概要stubとして継続。

## Stream H dedicated cycle (2026-04-18)

### Phase 1 Read
- Scope固定を再確認（許可: 本Issueファイルのみ更新、実装コード変更なし）。
- 分類/配置方針の既存記録を再読し、分類不能要素がないことを確認。

### Phase 2 ADR-CDC（必要時のみ）
- 判定: **不要**（DecisionStatus=Fixed を維持）。

### Phase 3 Plan（AC/DoDドラフト→合意）
- AC: Classification / Audience / Public boundary / Validation（docs-check）の4点を満たす。
- DoD: Plan → Execute → Verify → Proceed を本Issue内に記録する。

### Phase 4 Execute（分類/配置方針の確定）
- Classification: **Move internal**
- 対象文書との最小整合: `04_Documentation/canonicalization.md は概要stub化を維持し、内部正本への移設PRを起票する`
- 非目標: 対象文書本文の全面改稿、実装コード変更、スコープ外Issue編集。

### Phase 5 Verify（docs-check, 修復上限3回）
- Verify-1: `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`
- Verify-2: `git diff --check`
- フェイルセーフ: 失敗時は同一Issueで最大3回まで修復し、4回目相当は停止。

### Phase 6 Proceed
- 状態: **Ready**
- 停止条件: 分類不能・対象外編集要求・修復3回超過を検知した場合は停止。

## 16) Stream G DOC-OPS-05 triage fix（2026-04-18）

### Phase 1 Read（Scope / Priority / AC 抽出）
- Scope/Priority/Requirement meta I/F を再読し、`推奨アクション`・`VerificationLevel=docs-check`・`DecisionStatus=Fixed` の一致を確認。
- AC未充足として「分類根拠の明文化」「次実行単位の固定」「GoNoGoGate判定条件の再現性」を抽出。

### Phase 2 ADR CDC（新方針要否）
- 判定: **追加ADRなし（Issue内CDCで固定）**。
- Context: DOC-OPS-05 は文書本文の全面改稿ではなく、公開境界の分類決定と実行順序固定が目的。
- Decision: 本Issueの分類を **Move internal** として確定し、後続は docs-only 変更単位に限定。
- Consequences: 実装/他Issueへ波及させず、Open化判定を分類メタの充足可否で一意に判断可能。

### Phase 3 Plan（AC/DoD不足ドラフト）
- AC-G1: Audience / Goal / Public boundary / Related を対象文書に追記するタスクを次PR要件に固定。
- AC-G2: GoNoGoGate=Required の判定条件（上記4点 + Validation + Non-goal）をIssue本文で追跡可能化。
- DoD-G1: Proceed判定を `Ready / Hold / Needs-decision` の三値で残す。
- DoD-G2: Validationは docs-check（メタ確認・参照整合・`git diff --check`）を必須実行手順に固定。

### Phase 4 Execute（分類根拠・次実行単位の固定）
- Classification（確定）: **Move internal**
- 分類根拠: AudienceとPublic boundaryを基準に、内部運用正本と外部公開導線の混在解消を優先。
- 次実行単位（固定）: `02_Architecture/canonicalization_workflow.md` を新設し、`04_Documentation/canonicalization.md` は概要と参照リンクのみのstubへ縮退する docs-only PR を起票する。

### Phase 5 Verify（docs-check整合 / 修復上限3回）
- 実行: `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`
- 実行: `git diff --check`
- 判定: 失敗時は同Issue内修復を最大3回まで。4回目相当は Fail-safe に従い停止。

### Phase 6 Proceed（Ready化候補）
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
- 次実行単位は canonicalization 公開stub維持 + 内部正本導線固定を継続する。

### Phase 4 Verify（docs-check）
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go|Phase 1|Phase 2|Phase 3|Phase 4|Phase 5" 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`
- `git diff --check`
- 修復は最大3回まで。4回目相当は `StoppedForClarification` として停止する。

### Phase 5 Proceed（差分要約）
- 判定: **Ready**
- 停止条件: 分類不能・対象外編集要求・自己修復3回超過を検知した場合は停止する。


## Stream H serial execution record（2026-04-19, DOC-OPS-05-01）

### Phase 1 Read
- 対象Issueと `04_Documentation/canonicalization.md` を再Readし、`Scope / RequirementID / DecisionStatus=Fixed` を確認。
- Classification は **Move internal** を維持し、docs-only スコープを再確認。

### Phase 2 ADR CDC
- 判定: **ADR追加不要**。既存CDC（Issue本文）で方針変更なし。
- Context / Decision / Consequences は既存記録を正本とし、承認待ちは発生しない。

### Phase 3 Plan
- AC/DoD不足なし。既存AC（Audience / Goal / Public boundary / Validation）を採用。
- 未合意の新規仕様は追加しない。

### Phase 4 Execute
- 「内部文書へ移動（Move internal）」分類を維持。
- 実行方針: 公開stubを維持し、詳細運用は内部正本参照へ固定。

### Phase 5 Verify
- docs-check: 必須メタ整合・公開境界メタ整合・差分整形を確認。
- Self-Correction 上限は3回、超過時は停止報告。

### Phase 6 Proceed
- 判定: **Ready**
- 停止条件未該当（自己修復3回超過 / 前提条件崩れ / 未定義競合なし）。


## DOC-OPS-05-01 Serial execution record（2026-04-19 / Stream doc-ops-05-01..05）

### Phase 1 Read
- Read対象: `01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`, `04_Documentation/canonicalization.md`
- 判定: Requirement meta I/F / Audience / Goal / Public boundary / VerificationLevel=docs-check を再確認。

### Phase 2 Plan
- 直列実行順序を固定: 05-01 → 05-02 → 05-03 → 05-04 → 05-05。
- 編集範囲を本Issue対応の2ファイルに限定し、`doc-ops-05-06`以降・共有統合3ファイル・コードは非編集。

### Phase 3 Execute
- 分類方針 `Move internal` を維持し、対象文書へ最新の実行記録を反映。
- 既存の安全境界（SafeMode既定ON / share-export境界）を変更しない。

### Phase 4 Verify
- `rg -n "DOC-OPS-05-01 Serial execution record|Phase 1 Read|Phase 2 Plan|Phase 3 Execute|Phase 4 Verify|Phase 5 Proceed" 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md 04_Documentation/canonicalization.md`
- `git diff --check`

### Phase 5 Proceed
- 判定: **Ready**
- 残課題: なし（DecisionStatus=Fixed 維持）

## 18) Stream E execution log（2026-04-19, DOC-OPS-05前半）

### Phase 1) Read同期
- Read Order（00_Prompt→01_Plans→02_Architecture）で本Issueの根拠文書を再確認。
- 本Issueの固定値 `DecisionStatus=Fixed` / `VerificationLevel=docs-check` / `GoNoGoGate=Required` を同期。

### Phase 2) Audience / Goal / 公開境界の固定
- Audience: **内部設計/運用担当（maintainer/AI contributor）**
- Goal: **公開導入者向けではなく内部正本へ誘導する境界を固定する**
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
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`
  - `git diff --check`

### Phase 5) Verify / Proceed（3回自己修復）
- 自己修復ポリシー: 不整合検出時は **同一Issue内で最大3回** 修復。4回目相当は停止して `Hold` 化。
- Proceed判定: **Ready**（DecisionStatus=Fixed かつ要判断追加なし）。

## Stream D execution log（2026-04-20 / DOC-OPS-05-01）

### Phase 1 Read
- 対象: `04_Documentation/canonicalization.md` と対応Issueの Requirement meta I/F を再読し、docs-only 境界を確認。
- 判定: Classification=`Move internal` を維持し、編集禁止範囲（README / dashboard / decision-pack / 実装コード）へ非接触。

### Phase 2 Plan（AC/DoD不足補完）
- AC補完: Audience / Goal / Non-goal / Public boundary / Outcome / Related と Go/No-Go 判定導線が追跡可能であること。
- DoD補完: Read → Plan → Execute → Verify → Proceed の5Phase記録を残し、Verifyは docs-check 手順を明示すること。

### Phase 3 Execute
- 既存の分類方針と公開境界メタを維持し、DOC-OPS-05前半（01〜05）の同期記録を本節へ追加。
- 非目標を維持し、仕様正本（00〜02）の上書き・実装変更は行わない。

### Phase 4 Verify（docs-check）
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go|Stream D execution log" 04_Documentation/canonicalization.md 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`
- `git diff --check`
- 失敗時は自己修復を最大3回まで。4回目相当は停止して Hold とする。

### Phase 5 Proceed（残課題記録）
- 状態: **Ready**
- 残課題: 内部移設PRで `02_Architecture/canonicalization_workflow.md`（または同等の設計正本）を確定し、本書は公開スタブ維持。

## Stream F execution record（2026-04-20 / 指定Phaseプロトコル）

### Phase 1) Read
- Scope制約を再確認し、本Issueメモ以外を編集しないことを固定。
- Requirement meta I/F と `DecisionStatus=Fixed` / `VerificationLevel=docs-check` の整合を再確認。

### Phase 2) Plan（AC/DoD不足ドラフト合意）
- AC補強案: `GoNoGoGate=Required` 判定の根拠（Audience / Goal / Public boundary / Next action）を本文内で追跡可能に維持。
- DoD補強案: Proceed判定を `Ready / Hold / Needs-decision` の3値で固定し、Stopper該当時は `Hold` へ遷移。

### Phase 3) ADR CDC（必要時）
- 判定: **追加ADR不要**。
- CDC: Context=公開境界整理の継続運用, Decision=Move internal分類維持, Consequences=後続はdocs-only移設PRへ限定。

### Phase 4) Execute + Verify（docs-check, 最大3回自己修復）
- Execute: Issue本文へ本フェーズ記録を追記（本ファイルのみ）。
- Verify-1: `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- Verify-2: `git diff --check`
- 自己修復: 0/3回（追加修復なし）。

### Phase 5) Proceed（次の1手・未解決点）
- 状態: **Ready**
- 次の1手: `04_Documentation/canonicalization.md` のstub化＋`02_Architecture` 側への移設PRをdocs-onlyで起票。
- 未解決点: 移設先を `02_Architecture` と `01_Plans` のどちらに最終固定するかは起票時に最終選定。
- Stopper確認: 未定義競合なし / safeMode後退語彙なし / 自己修復3回超過なし。

## DOC-OPS-05 Lane Update (2026-04-20)

### Phase 1) Read（対象Issueの現状・関連Spec確認）
- 対象: `issue-doc-ops-05-01-04doc-canonicalization.md`（Draft memoのみ）。
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

### Phase 6) Proceed（Open化準備リスト）
- Open readiness: **Ready**（Draft→Open候補）。
- Open化準備リスト:
  - [ ] Classification（Move internal / Improve external）が固定されている。
  - [ ] Audience / Goal / Public boundary / Next action が本文で追跡可能。
  - [ ] docs-check 手順が本文に明示されている。
  - [ ] 共有統合ファイルを更新しない独立レーン条件を満たしている。
  - [ ] 実装コード非変更（docs-only）を満たしている。
