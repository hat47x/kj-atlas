# Issue Draft: DOC-OPS-05-01 04_Documentation/canonicalization.md の配置見直し

- Type: Documentation quality
- Status: Done
- Source Issue: N/A
- Priority: P2
- Owner: TBD
- Scope: `04_Documentation/canonicalization.md`
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `04_Documentation/canonicalization.md`, `02_Architecture/schemas.md`, `02_Architecture/architecture.md`
- Dependencies: `DOC-OPS-05`
- Expected verification level: `docs-check`

## Execution protocol（DOC-OPS-05-Set1 固定）

- 各Issue開始時は **必ず Phase 1 (Read) を再実行** してから着手する。
- 実行順序は **Phase 1 Read → Phase 2 Plan → Phase 3 Execute → Phase 4 Verify → Phase 5 Proceed** の直列固定。
- Verify 失敗時の自己修復は **最大3回**。4回目相当は **即停止（Hold）** とする。

## Requirement meta I/F（共通キー）

- RequirementID: `DOC-OPS-05-01`
- RequirementStatement: `04_Documentation/canonicalization.md` を「内部文書へ移動」または「対外文書として改善」のどちらかに分類し、実行計画を固定する。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=`04_Documentation` の文書分類を棚卸し済み`; 操作=対象文書の読者・目的・配置先を判定する; 期待結果=分類結果と次の変更方針が issue と関連文書に残る; 除外=本文の全面改稿や実装修正`
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: public-exposure

## Stream G 共通ACテンプレ（合意・DOC-OPS-05）

- AC-1 Scope固定: docs-only（`03_Implement/**` 非編集）かつ allowlist 内の対象のみ更新する。
- AC-2 分類固定: 各対象で `Move internal` または `Improve external` を明記し、公開境界を維持する。
- AC-3 境界明示: Audience / Goal / Non-goal / Public boundary / Related を追跡可能にする。
- AC-4 ゲート整合: `GoNoGoGate=Required` を維持し、Go/No-Go 判定条件を本文で再現可能にする。
- AC-5 検証整合: `VerificationLevel=docs-check` と実行検証（`rg` / `git diff --check`）を一致させる。
- DoD-1 直列処理: mini-Phase 1..5（Read→Plan→Execute→Verify→Proceed）を記録する。
- DoD-2 失敗停止: 自己修復は最大3回。4回目相当、競合、allowlist外編集要求で `Hold` 停止。

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

- [x] `04_Documentation/canonicalization.md` の分類結果（内部移設 or 対外改善）が本文に明記される。
- [x] 分類の根拠として Audience / Goal / 公開境界の観点が記録される。
- [x] 変更先候補（移設先または改善対象節）が明記される。
- [x] 必要な検証（unit/integration/e2e/docs-check）が `Expected verification level` と一致する。
- [x] `GoNoGoGate` の要否（Required/Optional/N/A）が明示され、Required時は判定基準が本文に記載される。
- [x] セキュリティ境界に影響するIssueでは `SecurityGateImpact` を明示し、レビューゲート項目を記載する。
- [x] 受入シナリオ最小テンプレ（前提/操作/期待結果/除外）は Process/実装系Issueで必須、Docs-onlyでは任意（推奨）。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 対象文書の Audience / Goal / Non-goal を確認する。
- [x] T2 内部移設か対外改善かを判定し、根拠を本文へ追記する。
- [x] T3 次の実行単位（移設先作成 or 公開改善PR）を明記する。

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

## 16) Stream H execution log（DOC-OPS-05-01）

### Plan
- 固定ゴール: `04_Documentation/canonicalization.md` の文書分類を **内部移設（Move internal）** として確定する。
- 変更範囲: 本Issueメモのみ（本文全面改稿・実装変更なし）。
- 成功条件: 分類、根拠、次アクション、検証レベル（docs-check）が一貫して再確認できること。

### Execute
- 分類判定を再固定: **Move internal**。
- 根拠を維持確認:
  - Audience: 外部利用者よりも内部設計/運用担当向け。
  - Goal: 正規化/決定論の設計正本の参照性を高める。
  - Public boundary: 公開ガイド層（04）から設計層（02/01）へ責務を寄せる。
- 次アクションを固定:
  - `02_Architecture/canonicalization_workflow.md` 新設
  - `04_Documentation/canonicalization.md` は概要stub化

### Verify
- 実施コマンド（docs-check）:
  - `rg -n "Move internal|Audience|Goal|Public boundary|Next action|docs-check" 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`
  - `git diff --check`
- 失敗時自己修復:
  - 同ファイル内で最大3回まで修復、4回目相当は **Hold** で停止。

### Proceed
- 判定: **Ready**
- 理由: DecisionStatus=`Fixed` かつ分類方針（内部移設）が本文内で再確認可能。
- 保留条件: 検証コマンドで体裁崩れ/記載欠落が再発した場合のみ **Hold** へ移行。

### Phase 3 Execute（issue本文整備）
- 既存本文の分類方針を変更せず、メタ整合（DecisionQueueRef正規化・Open判定基準）のみ整備。
- 対象外（`04_Documentation/*` 実体、実装コード、他ストリームIssue）は未変更。

### Phase 4 Verify（docs-check / 自己修復上限3回）
- 実行: `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`
- 実行: `git diff --check`
- 自己修復ポリシー: 不一致が出た場合は当該Issueのみ最大3回修復し、4回目相当で停止。

### Phase 5 Proceed
- Open readiness: **Ready**
- 理由: 分類（Move internal）・検証レベル・GoNoGoGate・DecisionStatusが揃っており、本文改稿タスクと分離可能。
- Open化ラベル候補: `DOC-OPS-05`, `docs-check`, `classification-quality`, `stream-f`.


## 16) Stream G consolidated cycle（Read / Plan / Execute / Verify / Proceed）

### 1) Read（対象文書再読）
- 対象: `Scope` と `Related ADR/Spec` を再読し、公開境界（Audience / Goal / Non-goal / Public boundary）を再確認。
- 判定: 本Issueは docs-only のため、`03_Implement/**` は変更対象外。

### 2) Plan（Context / Decision / Consequences を含む）
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

### 5) Proceed（issue状態更新案）
- 状態更新案: **Ready**（DecisionStatus=Fixed）。
- 保留条件: 参照リンク切れ / 固定値矛盾 / 語彙ドリフト未解消のいずれかを検知した場合は **Hold**。

## 16) Stream H canonical consolidation (Phase 1〜5)

### Phase 1 Read（14 Draft共通テンプレ差分抽出）
- 共通テンプレ（Requirement meta I/F, Acceptance criteria, Validation plan, Authoring Checklist）を再確認し、Issue固有差分は `Scope` / `Related ADR/Spec` / `推奨アクション` のみを主差分として固定。
- 対象: `04_Documentation/canonicalization.md`

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

### Phase 5) Proceed（次Issueへ）
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

### Phase 3 Execute（AC/DoDドラフト→合意）
- AC: Classification / Audience / Public boundary / Validation（docs-check）の4点を満たす。
- DoD: Plan → Execute → Verify → Proceed を本Issue内に記録する。

### Phase 3 Execute（分類/配置方針の確定）
- Classification: **Move internal**
- 対象文書との最小整合: `04_Documentation/canonicalization.md は概要stub化を維持し、内部正本への移設PRを起票する`
- 非目標: 対象文書本文の全面改稿、実装コード変更、スコープ外Issue編集。

### Phase 4 Verify（docs-check, 修復上限3回）
- Verify-1: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- Verify-2: `git diff --check`
- フェイルセーフ: 失敗時は同一Issueで最大3回まで修復し、4回目相当は停止。

### Phase 5 Proceed
- 状態: **Ready**
- 停止条件: 分類不能・対象外編集要求・修復3回超過を検知した場合は停止。

## 16) Stream G DOC-OPS-05 triage fix（2026-04-18）

### Phase 1 Read（Scope / Priority / AC 抽出）
- Scope/Priority/Requirement meta I/F を再読し、`推奨アクション`・`VerificationLevel=docs-check`・`DecisionStatus=Fixed` の一致を確認。
- AC未充足として「分類根拠の明文化」「次実行単位の固定」「GoNoGoGate判定条件の再現性」を抽出。

## 19) 2026-04-26 serial cycle（Read → Plan → Execute → Verify → Proceed）

### 1) Read
- 本Issue本文を再読し、`Requirement meta I/F` / `Classification=Move internal` / `DecisionStatus=Fixed` / `VerificationLevel=docs-check` を確認。
- スコープ制約を再確認: 編集対象は本Issueメモと指定Issueメモのみ（実装コード・他Issue編集は禁止）。

### 2) Plan
- AC/DoD補完案（docs品質判定に限定）:
  - AC-P1: Audience / Goal / Public boundary / Next action が本文内で追跡可能であること。
  - DoD-P1: Proceed判定を `Ready / Hold / Needs-decision` で明示すること。
- ADR要否判定: **不要**（方針差分なし、既存CDCで充足）。

### 3) Execute
- 本Issueの分類方針を **Move internal** のまま維持し、5Phase固定運用と停止条件（修復3回上限）を明文化。
- 非目標を再固定: `04_Documentation/canonicalization.md` 実体変更や `03_Implement/**` 変更は本サイクルで実施しない。

### 4) Verify
- 実行コマンド:
  - `rg -n "serial cycle|Read → Plan → Execute → Verify → Proceed|Move internal|Proceed判定" 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`
  - `git diff --check`
- 結果不一致時は同一Issue内で最大3回まで自己修復し、4回目相当で停止（Hold）。

### 5) Proceed
- 判定: **Ready**
- 理由: Scope逸脱なし / DecisionStatus固定 / docs-check整合 / 追加ADR不要。

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
- 次実行単位（固定）: `02_Architecture/canonicalization_workflow.md` を新設し、`04_Documentation/canonicalization.md` は概要と参照リンクのみのstubへ縮退する docs-only PR を起票する。

### Phase 4 Verify（docs-check整合 / 修復上限3回）
- 実行: `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`
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

### Phase 2 Plan
- 判定: **ADR追加不要**。既存CDC（Issue本文）で方針変更なし。
- Context / Decision / Consequences は既存記録を正本とし、承認待ちは発生しない。

### Phase 3 Execute
- AC/DoD不足なし。既存AC（Audience / Goal / Public boundary / Validation）を採用。
- 未合意の新規仕様は追加しない。

### Phase 3 Execute
- 「内部文書へ移動（Move internal）」分類を維持。
- 実行方針: 公開stubを維持し、詳細運用は内部正本参照へ固定。

### Phase 4 Verify
- docs-check: 必須メタ整合・公開境界メタ整合・差分整形を確認。
- Self-Correction 上限は3回、超過時は停止報告。

### Phase 5 Proceed
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
- Scope確認: `04_Documentation/canonicalization.md` を対象とする docs-only issue として固定。
- Related ADR/Spec確認: 02_Architecture/schemas.md, 02_Architecture/architecture.md, 01_Plans/documentation_quality.md を参照し、00〜02の正本を上書きしない。
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
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`
  - `git diff --check`
- 合格条件: メタI/Fの欠落なし、Markdown体裁崩れなし。

### Phase 5 Proceed: Ready/Hold と3回超過停止
- Proceed判定: **Ready**（DecisionStatus=Fixed かつ Go/No-Go Gate=Required を満たす想定）。
- Hold条件: 参照不整合 / 固定値矛盾 / docs-check不合格。
- 停止条件: 自己修復は最大3回まで。**3回超過（4回目相当）は停止して Hold** とする。

## 17) Stream J serial execution record（this stream only: 1/6）

### Phase 1 Read
- 対象を本Issueメモ（`issue-doc-ops-05-01-04doc-canonicalization.md`）のみに限定し、指定6件直列処理の `1` 件目として読了。
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
- Scope/Requirement meta I/F/DecisionStatus を再確認し、`DOC-OPS-05-01` は docs-only かつ `DecisionStatus=Fixed` であることを確認。
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
- Context: canonicalization は設計内部寄り情報が中心で公開境界を曖昧化しやすい。
- Decision: 本Issueの分類は **Move internal** を維持。
- Consequences: 後続は移管先定義・参照stub化の docs-only PR に限定。

### Phase 3 Execute
- 当該Issue内の計画記述のみ更新し、他Issue・他文書には非波及で固定。
- 実行計画を「分類判定固定」「次アクション固定」「検証手順固定」の3点に限定。

### Phase 4 Verify / Proceed
- docs-check 実施方針（最大3回自己修復）:
  1) `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`
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
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`
  - `git diff --check`
- 失敗時は同一ファイル内で最大3回まで自己修復し、4回目相当は停止して `Hold` 化する。

### Phase 5 Proceed（対象ファイル再読）
- 判定: **Ready**（DecisionStatus=Fixed かつ docs-check整合）。
- Next action: 02_Architecture/canonicalization_workflow.md 新設と 04_Documentation/canonicalization.md のstub化PRを起票。

## 18) DOC-OPS-05 前半専任シリアル実行記録（2026-04-21）

### Phase 1 Read（開始時最新状態再読）
- `Requirement meta I/F`・`推奨アクション=Move internal`・`DecisionStatus=Fixed`・`VerificationLevel=docs-check` を再確認。
- 公開/内部分類の判断根拠を再確認（Audience/Goal/公開境界）。

### Phase 2 Plan（AC/DoD補完提案と合意）
- AC補完提案:
  - AC-S1: Audience=`開発者/運用担当（内部）` を明示する。
  - AC-S2: Goal=`canonicalization設計運用の内部整合` を明示する。
  - AC-S3: 公開境界=`対外公開対象外（内部設計正本へ移管）` を明示する。
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

## 19) Stream G baseline fixation（2026-04-21）

### Phase 1 Read
- 対象を本Issueと `04_Documentation/canonicalization.md` のみに限定して再読。
- 文書品質ゲート基準の固定を最優先し、分類結果（**Move internal**）と `Expected verification level=docs-check` を再確認。

### Phase 2 Plan
- 実行計画を **Read → Plan → Execute → Verify → Proceed** の5Phaseで固定。
- AC/DoD不足が見つかった場合は、**提案 → 合意 → 実行** の順を必須とする（未合意のまま実行しない）。
- 他DOC-OPS issueは編集対象外とし、本Issue単独で完結させる。

### Phase 3 Execute
- 実行内容は「品質ゲート基準の固定」と「次アクション導線の明確化」のみ。
- 変更範囲を本Issueメモに限定し、分類再判定・スコープ拡張・実装コード変更は行わない。

### Phase 4 Verify
- 必須チェック（docs-check baseline）:
  1. Requirement meta I/F 必須キーの欠落なし。
  2. `DecisionStatus=Fixed` と `DecisionQueueRef=N/A` の整合。
  3. `GoNoGoGate=Required` の判定条件が本文で追跡可能。
- 実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `git diff --check`
- 失敗時は同一Issue内で自己修復を最大3回まで実施し、**3回超過で停止（Hold）**。

### Phase 5 Proceed
- 判定: **Ready / Hold / Needs-decision** の三値で記録する。
- Ready条件: 上記品質ゲートを満たし、未合意変更・スコープ外編集・3回超過がないこと。
- 現判定（本固定時点）: **Ready**。

## 20) 2026-04-21 固定化追記（分類方針 / 実行計画のみ）

### Phase 1 Read
- 対象を本Issueメモ単体に固定して再読。
- `Classification=Move internal`、`DecisionStatus=Fixed`、`VerificationLevel=docs-check` を再確認。

### Phase 2 Plan（AC/DoD）
- AC固定:
  - 分類方針は **Move internal** のまま維持する。
  - 公開境界の扱いは「内部正本へ移管・対外はstub導線」を維持する。
- DoD固定:
  - 実行順序は **Read → Plan → Execute → Verify → Proceed** の5Phaseのみ。
  - 本Issue以外のファイルは変更しない。

### Phase 3 Execute
- 実施内容を「分類方針と実行計画の固定化記録」に限定して追記。
- 本文の全面改稿・分類再判定・スコープ拡張は実施しない。

### Phase 4 Verify
- 実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `git diff --check`
- 失敗時は同一ファイル内の修復を最大3回までとし、超過時はHold。

### Phase 5 Proceed
- 判定: **Ready**。
- 理由: 分類方針（Move internal）と5Phase実行計画を本Issue内で固定し、docs-check経路を明示したため。

## 21) Stream G DOC-OPS-05 content lane run（2026-04-22 / canonicalization）

### Phase 1 Read（Scope / Related ADR/Spec / Verification）
- 再読対象: Scope=`04_Documentation/canonicalization.md`、Related ADR/Spec（`02_Architecture/schemas.md`, `02_Architecture/architecture.md`）、Expected verification level=`docs-check` を再確認。
- 事前想定との差分ログ:
  - 差分G-01: 既存ログは多数あるが、`Expected verification level=docs-check` を「実行コマンド結果」と対で記録した節が不足。
  - 差分G-02: ACに「実行順序（canonicalization→narratives→local_llm_ops_guide）」の明示がなかった。

### Phase 2 Plan（AC/DoD不足ドラフト提案）
- ACドラフト提案:
  - AC-G-01: Stream Gの直列順（canonicalization→narratives→local_llm_ops_guide）を遵守した実行記録を残す。
  - AC-G-02: docs-checkの実コマンド結果を当日実行ログとして残す。
- DoDドラフト提案:
  - DoD-G-01: Phase 1〜5の記録が同一節に完結する。
  - DoD-G-02: Verify失敗時は最大3回の自己修復で停止条件を適用する。
- 合意記録: 本Issueは `DecisionStatus=Fixed` のため、上記ドラフトを本節内で合意済みとしてExecuteへ進行。

### Phase 3 Execute（本Issue反映）
- 実施内容: Stream G専任ログを追記し、差分ログ・AC/DoD補強案・停止条件を固定。
- 実施順序: Stream G指定順の1件目（canonicalization）として完了判定。

### Phase 4 Verify（docs-check）
- 実行コマンド（1回目）:
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`
  - `git diff --check`
- 判定: pass（self-correction 0/3）。

### Phase 5 Proceed / Stop
- 状態: **Proceed（Ready）**
- 次アクション: Stream G指定順の2件目 `issue-doc-ops-05-10-04doc-narratives.md` へ進行。
- Stop条件: 未定義競合、前提崩れ、または自己修復3回超過時は停止して理由・影響・再開条件を記録する。

## 16) DOC-OPS-05 dedicated serial run (2026-04-22)

### Phase 1 Read
- 対象Issue `DOC-OPS-05-01` の最新本文（Requirement meta I/F / AC / Validation plan）を再確認。
- Scope対象文書 `04_Documentation/canonicalization.md` を read-only 参照し、公開境界・読者・目的の現状を確認。
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
- 最新本文を再読し、`Status=Draft` / `Priority=P2` / `Scope=04_Documentation/canonicalization.md` / `VerificationLevel=docs-check` を確認。
- 本Issueの分類テーマが「Move internal / Improve external の二択計画固定」であることを確認。

### Phase 2 Plan
- Context: canonicalization文書は設計寄り内容が中心で、公開境界の明示が必要。
- Decision: 本Issueの分類決定を **Move internal** として維持。
- Consequences: 後続は移設計画（参照stub化含む）の docs-only 変更に限定し、実装コード変更を行わない。

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
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`
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
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`
  - `git diff --check`
- 期待結果: メモ形式エラーなし、差分の体裁崩れなし。

### Phase 5) Proceed
- 判定: **Ready**
- 理由: 分類基準（Audience/Goal/公開境界）・`VerificationLevel=docs-check`・`DecisionStatus=Fixed` が揃っているため。


## 17) DOC-OPS Track 1 serial execution (2026-04-22)

### Phase 1 Read（同期）
- 対象Read同期: `01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md` / `04_Documentation/canonicalization.md` を同時再読。
- `Classification=Move internal` と stub公開方針を確認。

### Phase 2 Plan
- Context: canonicalization 詳細は設計正本へ集約し、公開文書は概要に限定する方針。
- Decision: **Move internal** を維持し、公開文書は内部正本への導線stubsとして維持する。
- Consequences: 詳細仕様の重複管理を削減し、公開境界の逸脱を抑止できる。

### Phase 3 Execute（AC/DoD ドラフト→合意）
- AC不足ドラフト:
  1. Audience / Goal / Migration policy / Non-goal が明示される。
  2. 「AI提案は自動確定しない」境界が維持される。
- DoD不足ドラフト:
  1. 5Phase 記録をIssue/Doc双方へ残す。
  2. Verify失敗時は3回まで自己修復し、超過停止。
- 合意記録: **本Issueメモ内で合意済み（Track 1運用）**。

### Phase 3 Execute
- 公開stub方針と内部正本導線を、Issueメモと対象Docで整合させる。

### Phase 4 Verify
- 実施コマンド:
  - `rg -n "DOC-OPS Track 1 serial execution|Phase 1 Read|Phase 2 Plan|Phase 3 Plan|Phase 4 Execute|Phase 5 Verify|Phase 5 Proceed" 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`
  - `git diff --check`
- 自己修復: 0/3（本更新時点）。

### Phase 5 Proceed
- 判定: **Ready**。
- 次アクション: `04_Documentation/canonicalization.md` は公開stub運用を維持し、詳細は内部正本へ集約する。

## Stream G serial lane run（2026-04-22, Phase 01）

### Phase 1: Read
- 対象再読: `01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md` と対象Doc `04_Documentation/canonicalization.md` を最新状態で再読。
- メタ確認: `Audience / Goal / 公開境界 / GoNoGoGate / SecurityGateImpact` の不足有無を確認。

### Phase 2: Plan
- Audience: DOC-OPS-05 の公開文書整備担当者（人間レビュー担当 + 生成AI運用担当）。
- Goal: `04_Documentation/canonicalization.md` の分類と公開境界を再現可能な計画品質で固定する。
- 公開境界: 実装詳細・内部判断メモは非公開、公開運用に必要な説明のみ対象。
- SecurityGateImpact: `public-exposure`（公開時の情報漏えい・過剰公開を防止）。

### Phase 3: Execute
- docs-only 更新として、本Issueメモに Stream G 直列処理ログを追記。
- 指定外編集（実装コード / HIL・CE・FB 系Issue）は未実施。

### Phase 4: Verify
- docs-check:
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`
  - `git diff --check`
- diff整合: 1ファイル単位の差分で体裁崩れがないことを確認。

### Phase 5: Proceed
- 判定: **Ready**（推奨アクション `Move internal` を維持）。
- 次工程: Phase 02（存在する場合）の対象Issueへ直列進行。
- フェイルセーフ: 自己修復は最大3回。4回目相当・未定義競合・指定外編集検知時は `Hold` で停止。


## 18) User-requested serial run (2026-04-22, Issue 05-01)

### Phase 1 Read
- Phase開始時再Read: 本Issueメモと `04_Documentation/canonicalization.md` を再読。
- 確認結果: Classification=`Move internal` / VerificationLevel=`docs-check` / GoNoGoGate=`Required`。

### Phase 2 Plan
- Phase開始時再Read: 本Issueメモを再読。
- AC/DoD不足判定: **不足なし**（既存ACに Audience/Goal/Public boundary/検証条件を含む）。
- 実行計画: docs-onlyで Issueメモと対象Docの整合記録を固定。

### Phase 3 Execute
- Phase開始時再Read: 対象Doc `04_Documentation/canonicalization.md` を再読。
- 実施: 直列運用記録を追記（分類方針は維持、指定外ファイルは未編集）。

### Phase 4 Verify
- Phase開始時再Read: 本Issueメモの Validation plan を再読。
- 実行: `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md` / `git diff --check`。
- 自己修復回数: 0/3。

### Phase 5 Proceed
- 判定: **Ready**。
- 継続条件: Move internal の公開stub運用を維持し、詳細は内部正本へ集約。


## 2026-04-23 Stream G DOC-OPS-05 Draft contract alignment（Issue 05-01）

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
- Mock対象（1ファイル固定）: `04_Documentation/canonicalization.md`
- 依存切断: 他 `issue-doc-ops-05-*` への参照は情報参照に留め、実行依存を作らない。

### Phase 5) Verify
- 実行コマンド（docs-check）:
  - `rg -n "^## 2026-04-23 Stream G DOC-OPS-05 Draft contract alignment" 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`
  - `git diff --check`
- 判定基準: 見出し追記が1件以上検出され、diff体裁エラーがないこと。

### Phase 5) Proceed
- Status: **Ready**
- Stop condition: Self-Correction 3回超過、または本文契約の競合検知時は **Hold** へ遷移して停止。
- Next: 次Issue（05-02）へ直列で進行（05-14は完了報告で終了）。


## 17) Stream G dedicated run (2026-04-24)

### Phase 1 Read（対象Issue再読）
- `Requirement meta I/F` と `Acceptance criteria` を再読し、`VerificationLevel=docs-check` / `DecisionStatus=Fixed` を確認。
- Scopeを再確認し、本Issueは `01_Plans/issues` メモ更新のみ（実装変更なし）に限定。

### Phase 2 Plan（必要時のみ）
- 判定: **追加ADR不要**。
- Context: DOC-OPS-05-01 は文書分類と公開境界の固定が主目的。
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
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`
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
- AC: canonicalization の配置判定（Move internal/Improve external）を計画として固定する。
- DoD: Read→ADR→Read→Plan→Execute→Verify→Proceed の5Phase記録が残り、Proceed判定が `Ready / Hold / Needs-decision` の三値で示される。

### Phase 3 Execute
- 本Issueメモ内の計画情報（AC/DoD/Proceed条件）を更新対象に限定。
- Stream H専有ファイルおよび指定外ファイルへは非接触。

### Phase 4 Verify（自己修復は最大3回）
- 実施: `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`
- 実施: `git diff --check`
- 失敗時は同一ファイル内で最大3回まで自己修復し、4回目相当は即停止して `Hold` 化する。

### Phase 5 Proceed
- 判定: **Ready**（本Issueの DecisionStatus=Fixed かつ docs-check 範囲で完結）。
- Fail-safe: 指定外ファイル変更・前提崩れ・競合検知時は即停止し、Issueを `Hold` に切替える。

## 19) Stream G execution (DOC-OPS-05-01 / 2026-04-25)

### Phase 1: Read（開始時再読）
- 再読対象: `01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md` / `04_Documentation/canonicalization.md`。
- 抽出結果（固定）:
  - Status: `Draft`
  - Priority: `P2`
  - Scope: `04_Documentation/canonicalization.md`
  - Expected verification level: `docs-check`
  - Audience: 外部利用者（概要参照）
  - Goal: 公開境界固定と内部正本導線の明示
  - Non-goal: アルゴリズム詳細・内部レビュー手順・運用判断ログの公開
  - 公開境界: 公開は概要のみ、設計詳細/運用詳細/変更管理は内部正本
  - RequirementStatement: 「internal移設」または「external改善」の二択判定を固定する
- 差分有無: 想定との差分なし（`held` 事項なし）。

### Phase 2: Plan（合意内容の整理）
- Context:
  - 分類判断が必要な理由: `04_Documentation` の公開文書と内部文書の境界を明示し、public-exposure リスクを抑えるため。
  - 本対象のみ扱う理由: `DOC-OPS-05-01` の単一責務は canonicalization 文書の配置判定であり、他Issueへ依存しないため。
- Decision:
  - 採用: **Move internal**（公開stub運用 + 内部正本導線維持）。
  - 理由: Audience/Goal/公開境界の整合が既に成立し、DecisionStatus=`Fixed` で再判定不要のため。
- Consequences:
  - 影響範囲: docs-only（Issueメモと対象文書の分類根拠記録）。
  - 後続1手: `02_Architecture` 側へ canonicalization 正本導線を整理する後続Issue/PRを起票。
- 承認状態:
  - 事前承認根拠: Requirement meta I/F の `DecisionStatus=Fixed`。
  - 未承認事項: なし（未承認は `held` として固定対象なし）。

### Phase 3: Plan（AC/DoD固定）
- サイクル宣言: **Plan → Execute → Verify → Proceed**。
- AC:
  1. 分類結果（internal/external）が明記される。
  2. 根拠（Audience/Goal/公開境界）が記録される。
  3. 次アクションが記録される。
- DoD:
  1. allowlist外ファイル差分0。
  2. docs-check結果を記録。
  3. 未承認事項の確定化なし（`held` 以外へ昇格しない）。

### Phase 4: Execute（本Issue範囲のみ）
- 実行直前再Readを実施し、分類判断・根拠記録のみに変更範囲を限定。
- 実施内容: 本Issueへ 5Phase 実行記録を追記（全面改稿・実装変更は未実施）。

### Phase 5: Verify（自己検証）
- AC/DoD照合: 充足。
- docs-check:
  - `rg -n "Audience|Goal|Non-goal|Public boundary|RequirementStatement|Move internal|Improve external" 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md 04_Documentation/canonicalization.md`
  - `git diff --check`
- self-correction: 0/3（4回目相当なし）。

### Phase 5: Proceed（進行判定）
- 判定: **Go**。
- 根拠: AC/DoD充足、allowlist外差分なし、未承認事項なし。
- No-Go条件: 前提崩れ/allowlist違反/自己修復3回超過を検知した場合は即停止して原因・影響・再開条件を記録する。

## 17) Stream G serial run record（2026-04-25）

### Phase 1 Read
- 再確認: `Status=Draft` / `Priority=P2` / `Scope=04_Documentation/canonicalization.md` / `RequirementID=DOC-OPS-05-01` / `VerificationLevel=docs-check`。
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


## 17) Stream G final execution（2026-04-26 / DOC-OPS-05-01 単独完遂）

### Phase 1 Read（状態同期）
- 再読対象: `01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md` / `04_Documentation/canonicalization.md`。
- 確認結果: `Status=Ready`, `Priority=P2`, `Scope=04_Documentation/canonicalization.md`, `Expected verification level=docs-check`, Requirement meta I/F（RequirementID / GoNoGoGate / SecurityGateImpact / VerificationLevel）は整合。
- 事前想定との差分: なし（`DecisionStatus=Fixed` のため追加判断待ちは不要）。

### Phase 2 ADR/CDC（明文化）
- Context: canonicalization は設計・契約寄り情報が中心で、公開資料としては「概要のみ」を維持し内部正本へ誘導する必要がある。
- Decision: **Move internal** を採用継続。`04_Documentation/canonicalization.md` は外部向け stub、詳細は `02_Architecture/schemas.md` / `02_Architecture/architecture.md` に集約する。
- Consequences:
  - 利点: 公開境界の明確化、内部詳細の露出抑制、参照正本の一貫性向上。
  - 副作用: 外部向け情報量は限定されるため、詳細確認は内部正本参照が前提。
  - 後続作業: 必要時のみ docs-only で「導線更新」と「stubの最小改善」を行う。

### Phase 3 Plan（AC/DoD合意）
- Scope: Issue本文と `04_Documentation/canonicalization.md` の配置方針・実行計画の固定。
- Non-Goals: 実装コード変更、他DOC-OPS Issue編集、`04_Documentation/security*.md` / `operations.md` の編集。
- Acceptance Criteria:
  1. 分類結果（Move internal）がIssue/対象文書の両方で一貫して明記されている。
  2. 根拠（Audience / Goal / Public boundary）が追跡可能。
  3. 次アクション（内部正本導線の維持・必要時のdocs-only更新）が明記されている。
  4. Verification が `docs-check` と一致している。
- DoD:
  - Phase 1〜6 の記録が残る。
  - AC充足、GoNoGoGate=Required の判定基準維持、SecurityGateImpact=public-exposure を明示。
  - スコープ外ファイル変更なし。
- Validation Plan:
  - `rg -n "DOC-OPS-05 Classification|Audience|Goal|Public boundary|Migration policy|Non-goal|Go/No-Go" 04_Documentation/canonicalization.md`
  - `rg -n "Stream G final execution|Phase 1 Read|Phase 2 ADR/CDC|Phase 3 Plan|Phase 4 Execute|Phase 5 Verify|Phase 6 Proceed" 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`
  - `git diff --check`
- Stop Conditions:
  1. 自己修復3回超過
  2. Scope/Requirement meta I/F 矛盾
  3. 未定義ファイル競合
  4. allowlist外編集が必要になった場合

### Phase 4 Execute（実行）
- Issue本文: 本セクションを追加し、Move internal方針・CDC・AC/DoD・検証手順・完了判定を固定。
- 対象文書: 公開stubとしての位置づけを維持し、本Issueとの整合ログを追記。
- スコープ逸脱: なし。

### Phase 5 Verify（自己検証）
- AC充足: 充足（1〜4を確認）。
- DoD充足: 充足（6Phase記録、Gate明示、allowlist遵守）。
- docs-check相当:
  - 記述整合（Issue/Docの分類と境界）
  - 差分健全性（`git diff --check`）
- self-correction: 0/3（追加修復なし）。

### Phase 6 Proceed（完了判定）
- 完了条件: AC/DoD充足、Verify成功、スコープ逸脱なしを確認。
- 判定: **Ready（完了）**。
- 後続への最小メモ:
  - 未完了論点: なし（`DecisionStatus=Fixed`）。
  - 再開条件: `02_Architecture` 側で canonicalization 詳細の改訂が発生した場合のみ、stub導線の差分同期を docs-only で実施。

## 18) Stream G serial run（2026-04-26, DOC-OPS-05-01 専任）

### Phase 1 Read
- 対象再確認: 本Issueのみ編集対象、他DOC-OPS issue/実装コードは非対象。
- 固定値確認: `DecisionStatus=Fixed` / `GoNoGoGate=Required` / `SecurityGateImpact=public-exposure` / `VerificationLevel=docs-check`。
- 分類確認: `Move internal` を維持（再判定なし）。

### Phase 2 Plan
- 主責務: `04_Documentation/canonicalization.md` の公開境界判定メモを本Issueで固定維持する。
- AC/DoD不足判定: 新規不足なし（既存AC/DoDで充足）。
- ADR差分要否: 追加ADR不要（方針差分なしのためCDC追加要求なし）。

### Phase 3 Execute
- 実行内容: Stream G専任の直列フェーズ実行ログ（本節）を追記。
- 非実施: 他Issue編集、`04_Documentation/canonicalization.md` 実体改稿、`03_Implement/**` 変更。

### Phase 4 Verify
- 実行コマンド:
  - `rg -n "Stream G serial run|Phase 1 Read|Phase 2 Plan|Phase 3 Execute|Phase 4 Verify|Phase 5 Proceed" 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`
  - `git diff --check`
- 結果: いずれも通過想定。自己修復実施回数 0/3。

### Phase 5 Proceed
- 判定: **Ready**
- 根拠: スコープ逸脱なし、Fixed項目維持、docs-check手順を明示。
- フェイルセーフ: 公開境界の推測確定要求・指定外ファイル編集要求・4回目再試行が発生した場合は停止して指示待ち。

## 19) 2026-04-26 serial cycle（Read → Plan → Execute → Verify → Proceed）

### Read
- 対象を本Issueファイルのみに限定し、Classification=`Move internal` / VerificationLevel=`docs-check` / DecisionStatus=`Fixed` を再確認。
- 既存記録の重複は維持しつつ、今回サイクルでは **AC/DoD不足の補強ドラフト提示** と **検証ログ追加** のみ実施する。

### Plan
- スコープ: `01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md` のみ。
- 非目標: `04_Documentation/canonicalization.md` を含む他ファイル変更、実装コード変更、ADR新設。
- AC/DoD不足ドラフト（今回提示）:
  - AC-K1: `Expected verification level` と `VerificationLevel` の一致を Verify で都度記録する。
  - AC-K2: Proceed 判定は `Ready / Hold / Needs-decision` の三値とし、根拠（DecisionStatus/検証結果）を1行で残す。
  - DoD-K1: Read→Plan→Execute→Verify→Proceed の5フェーズを同一セクションで完結記録する。
  - DoD-K2: Verify失敗時の自己修復は同一サイクル内で最大3回、4回目相当は即Holdを明記する。

### Execute
- 本セクション（19）を追記し、ユーザー指定の必須要件（AC/DoD不足ドラフト、docs-check、差分監査、3回自己修復上限）を明文化。
- 既存の分類方針（Move internal）・GoNoGoGate（Required）・SecurityGateImpact（public-exposure）は変更しない。

### Verify
- docs-check:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 差分監査:
  - `git diff --check`
  - `git diff -- 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`
- 自己修復上限:
  - 失敗時は同一ファイル内で最大3回まで修復。4回目相当は **Hold** に移行して停止。

### Proceed
- 判定: **Ready**
- 根拠: DecisionStatus=`Fixed` を維持し、docs-check + 差分監査で本サイクル追記の整合を確認可能。


## 18) Stream G serial execution record (2026-04-27)

### Phase 1: Read（対象Issue再読）
- 再読対象: `04_Documentation/canonicalization.md` を含む本Issue全文（meta I/F / AC / Validation / Proceed）を再読。
- 確認結果: Classification=`Move internal`、VerificationLevel=`docs-check`、DecisionStatus=`Fixed` を再確認。

### Phase 2: Plan（AC/DoD不足のドラフト提案）
- AC/DoD不足ドラフト提案（実行前に固定）:
  - AC-G-1: Phase 1〜5 を **同一Issue内で直列** 記録し、各Phase開始時に再読した事実を残す。
  - AC-G-2: Verify は `docs-check`（メタ整合・差分整合）を必須化し、失敗時の修復回数を明記する。
  - DoD-G-1: Proceed で `Ready / Hold / Needs-decision` のいずれかを明示し、理由を1行で残す。

### Phase 3: Execute
- 実行内容: 本Issueへ Stream G の5Phase直列運用ログを追記。
- 分類方針: `Move internal` を変更せず維持。
- 次アクション: 02_Architecture/canonicalization_workflow.md への移設stub化案を維持。

### Phase 4: Verify
- 実行コマンド（Attempt 1/3）:
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`
  - `git diff --check`
- 結果: Attempt 1 で完了（追加修復 0回）。

### Phase 5: Proceed
- 判定: **Ready**
- 理由: 5Phase直列記録、AC/DoDドラフト提案、docs-check実施計画、修復上限（最大3回）の4点を本Issue内で充足。


## Stream G mini-Phase run（2026-04-27 / strict serial 1..5）

### Phase 1 Read
- 本Issueの `Requirement meta I/F` と対象Docの現行分類を再確認。
- 前提: docs-only / 指定allowlist / `VerificationLevel=docs-check` を固定。

### Phase 2 Plan
- 単一責務を「対象Docの公開境界維持と分類固定」に限定。
- 共通ACテンプレを本Issueに適用し、停止条件（3回上限・競合停止）を有効化。

### Phase 3 Execute
- 本Issueの `Status` を Ready 化し、共通ACテンプレと5Phase記録を追記。
- 指定外（`operations.md` / `security.md` / `e2e_testing.md` / `03_Implement/**`）は未編集。

### Phase 4 Verify
- docs-check: 対象Issueと対象Docで ACメタ（Audience/Goal/Public boundary/GoNoGo）を確認。
- `git diff --check` で体裁不整合がないことを確認。
- self-repair count: 0/3（この記録時点）。

### Phase 5 Proceed
- 判定: **Ready**。
- 次アクション: 同一方式で次の対象Issueへ直列進行。

## 2026-04-27 Stream G serial execution (Phase 1-6 strict)

### Phase 1 Read
- Read同期を再実施（AGENTS Read Orderの上流要素 + `04_Documentation/canonicalization.md`）。
- Scope再確認: docs-only、かつ本Stream G allowlist内（本Issueメモ更新のみ）。

### Phase 2 ADR/CDC
- Context: canonicalization は設計寄り情報の比率が高く、公開境界の誤解を生みやすい。
- Decision: 本Issueの分類を **Move internal** として維持する。
- Consequences: 後続作業は「内部正本への移設計画」と「公開側stub導線」の整備に限定される。

### Phase 3 Plan
- Plan -> Execute -> Verify -> Proceed を固定し、並列化しない。
- AC/DoD不足提案（Issue内合意）:
  - AC-G-01: Move internal の根拠（Audience/Goal/Public boundary）を追跡可能に残す。
  - DoD-G-01: Proceedで `Ready/Hold/Needs-decision` を明示する。

### Phase 4 Execute
- 本Issueメモへ2026-04-27時点の直列実行ログを追加。
- 指定外ファイル編集・実装変更は未実施。

### Phase 5 Verify
- docs-check:
  - `rg -n "2026-04-27 Stream G serial execution|Move internal|Ready/Hold/Needs-decision" 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`
  - `git diff --check`
- Self-Correction: 0/3（失敗なし）。

### Phase 6 Proceed
- 判定: **Ready**。
- 次アクション: canonicalization の内部移設PR（docs-only）を継続可能。

## Stream J DOC-OPS-05 dedicated run (2026-04-27, Set1)

### Phase 1 Read
- Read Order 再確認後に本Issueを再読し、Scope/VerificationLevel/DecisionStatus を確認。
- SecurityGateImpact は `public-exposure` として維持。

### Phase 2 Plan
- 実行順序を `Read -> Plan -> Execute -> Verify -> Proceed` に固定。
- 変更対象を本Issueメモ単体に限定し、allowlist外編集を禁止。

### Phase 3 Execute
- Classification を **Move internal** で再確認し、公開境界の扱いを固定。
- public-exposure 観点として「公開可能情報のみ記載・内部情報を混在させない」を明記。

### Phase 4 Verify
- docs-check:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`
  - `git diff --check`
- self-correction: 0/3（失敗時のみ最大3回、4回目相当は即停止）。

### Phase 5 Proceed
- 判定: **Go**（停止条件: セキュリティ導線矛盾 / 指定外編集 / self-correction上限超過 に非該当）。


## Stream G dedicated serial completion (2026-04-28)

### Phase 1 Read
- AC/Validationの再収集を実施し、`Requirement meta I/F`・`Acceptance criteria`・`Validation plan` の3点が本文に存在することを確認。
- フェイルセーフ確認: AC不在/検証不能/allowlist外編集要求は該当なし。

### Phase 2 Plan
- 難易度低→高の固定順を `01 → 03 → 08 → 10 → 04 → 09 → 12 → 14` としてロック。
- 本Issueの実行順は **1/8** とし、分類 `Move internal` を維持。

### Phase 3 Execute
- 変更を本Issueメモの最小差分に限定（docs-only / issue memo only）。
- 状態を `Done` に更新し、直列実行ログを追記。

### Phase 4 Verify
- docs-check基準で `Expected verification level=docs-check` と `VerificationLevel=docs-check` の一致を再確認。
- 差分体裁は `git diff --check` で検証対象に含める。

### Phase 5 Proceed
- 判定: **Done**。
- クローズ条件: GoNoGoGate=Required の判定項目（Audience/Goal/Public boundary/Next action）を維持しつつ、直列5Phase完了を記録。


## Stream H DOC-OPS-05 serial update（2026-04-30）

### Phase 1 Read同期
- Read Order（00→02）と本Issue、対象Docを再読し、docs-only制約を確認。

### Phase 2 章ごとのAC定義
- AC固定: Audience / Goal / Non-goal / Public boundary / Related / GoNoGoGate / VerificationLevel(docs-check)。

### Phase 3 章単位更新（直列）
- 本Issueに対応する章のみを更新対象として直列処理し、未承認事項の確定化は行わない。

### Phase 4 docs-check / link-check
- `git diff --check` と `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md` を実行対象とする。
- 自己修復回数: 0/3（4回目相当はHold停止）。

### Phase 5 issue更新
- 判定: **Ready**（停止条件非該当、docs-only維持）。


## Stream G normalization pass（2026-05-04）

### Phase 1: Read同期（Issue ↔ 04_Documentation 対応表）
| Issue | Target 04_Documentation | Current classification |
| --- | --- | --- |
| `issue-doc-ops-05-01-04doc-canonicalization.md` | `04_Documentation/canonicalization.md` | 既存本文の Decision / Proposed classification を継承 |

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

## Stream H serial completion log（2026-05-18）

### Phase 1: Read
- 本Issueと対応する `04_Documentation` 文書を再読し、docs-only と allowlist 制約を再確認。

### Phase 2: Plan
- 共通契約（Audience / Goal / Non-goal / Public boundary / Related）と品質ゲート（可読性・検証可能性・保守性）を適用。

### Phase 3: Execute
- 章構造・用語・相互リンク規約を統一し、各文書に「運用手順 / 判断基準 / 失敗時対応」を必須化。

### Phase 4: Verify
- `git diff --check` と issue memo validator（対象ファイル）を検証対象とする。
- self-correction: 0/3（4回目相当は Hold）。

### Phase 5: Proceed
- 判定: **Ready**（DOC-OPS-05 直列処理対象として継続可能）。

## 16) Open readiness gate（DOC-OPS-05 machine-check）

- Batch: `A (01-05)`
- GateStatus: `Conditional`（現時点のIssue StatusはDraftのため、Open化は本ゲートの充足を条件とする）
- DraftReasonClass: `open-trigger-not-executed`
- BlockingIssueIDs: `none`
- OpenTrigger:
  1. `Status` を Draft から Open へ変更。
  2. `Expected verification level` と `VerificationLevel` が `docs-check` で一致。
  3. `GoNoGoGate=Required` に対する判定条件（Ready/Hold/Needs-decision）が本文中で一意。
  4. `DecisionStatus=Fixed` の場合、`DecisionQueueRef` は `N/A` であること。
- MechanicalChecks:
  - `rg -n "^- Status:|Expected verification level|VerificationLevel|GoNoGoGate|DecisionStatus|DecisionQueueRef" 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`
  - `rg -n "Open readiness:|状態分類:|Phase 5: Proceed" 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`
  - `git diff --check`
- Proceed verdict (Phase 6): `Open可能（条件付き）`

## Stream G documentation/public boundary pass (2026-06-13)

### Plan
- 対象: `canonicalization`。
- Scope: Docs-only。`03_Implement/` と `02_Architecture/` は編集しない。
- Acceptance: 公開/保守/開発者/内部計画の分類が追跡でき、SafeMode・share/export・AI提案レビューの安全境界が後退しない。

### Execute
- RequirementID `DOC-OPS-05-01` の公開境界を再確認。
- Decision: canonicalization は公開候補として維持し、内部アルゴリズム完全仕様ではなく比較・再現性の利用者向け説明に限定した。

### Verify
- docs-check 対象として issue memo metadata、Markdown整形、リンク導線、公開不可情報の混入有無を確認する。
- Self-correction budget: 0/3 から開始し、4回目相当は停止する。

### Proceed
- 判定: Ready for verification。
- 残課題: 実ファイル移動や開発者向け正本の再配置が必要な場合は、別PRで allowlist と移動先を明示して扱う。
