# Issue Draft: DOC-OPS-05-06 04_Documentation/e2e_testing.md の配置見直し

- Type: Documentation quality
- Status: Draft
- Source Issue: N/A
- Priority: P2
- Owner: TBD
- Scope: `04_Documentation/e2e_testing.md`
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `04_Documentation/e2e_testing.md`, `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`, `01_Plans/documentation_quality.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: `DOC-OPS-05-06`
- RequirementStatement: `04_Documentation/e2e_testing.md` を「内部文書へ移動」または「対外文書として改善」のどちらかに分類し、実行計画を固定する。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=`04_Documentation` の文書分類を棚卸し済み`; 操作=対象文書の読者・目的・配置先を判定する; 期待結果=分類結果と次の変更方針が issue と関連文書に残る; 除外=本文の全面改稿や実装修正`
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: docs-check
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A（DecisionStatus=Fixed）

## 1) 課題 / Problem statement

- `04_Documentation/e2e_testing.md` が、対外公開文書として維持すべきか、内部文書へ移すべきか未整理。
- 現状のままだと `04_Documentation/` に内部向け情報が残るか、逆に公開候補文書の改善優先度が見えない。
- AIエージェントが外部向け資料を作る際の配置判断が曖昧なままになる。

## 2) 背景 / Context

- E2E方針は公開可能だが、内部進行メモとの混在がないか棚卸しが必要。
- `01_Plans/minimal-context-triage.md` 導入により、低情報価値の一覧再読ではなく、必要な対象だけを追う運用へ寄せたい。
- `01_Plans/documentation_quality.md` は対外文書作成の内部品質基準として扱う。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 外部読者へ公開する文書と内部運用文書の混在を減らし、判断コストを下げる。
- 安全（THREAT_MODEL / SafeMode）: 公開境界の曖昧さを減らし、内部情報の対外露出を防ぐ。
- 企業・行政要件（enterprise_architecture）: 役割・運用責務を外部説明可能な形へ整理しやすくする。
- 後方互換（schemas）: 文書配置の見直しで実装互換性は変えない。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs
- 推奨アクション: **Improve external**
- 実施方針: 開発者向けE2E runbookとして前提・実行・確認・制約を整理する
- 非目標: このIssue単体で対象文書の全文改稿や実装仕様変更は行わない。

## 5) 受入条件 / Acceptance criteria

- [ ] `04_Documentation/e2e_testing.md` の分類結果（内部移設 or 対外改善）が本文に明記される。
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
  - `rg -n "Audience|Goal|Non-goal|Outcome|Related" 04_Documentation/e2e_testing.md 01_Plans/documentation_quality.md`
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

- 本Issueは `04_Documentation/e2e_testing.md` 専用の分類/改善トラッキングメモ。
- 実作業では `01_Plans/minimal-context-triage.md` と関連ADRだけを開き、一覧再読を前提にしない。

---

## 11) Stream G phase record（DOC-OPS-05 front-half: 01-07）

### Phase 1: Read
- メタ抽出結果: `Status=Draft`, `Priority=P2`, `Scope` と `VerificationLevel=docs-check` を確認。
- 重複/矛盾/不足:
  - 重複: 01〜07で同一テンプレのため、判定項目は共通化可能。
  - 矛盾: 本Issue固有の分類方針（Move internal / Improve external）は本文と整合。
  - 不足: Phase 6（Proceed）のOpen可否記録が未定義だったため追加。

### Phase 2: Plan
- 1issue 1主責務: **公開文書改善計画（e2e_testing runbook の公開品質要件固定）**
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
  - `04_Documentation/e2e_testing.md` の公開runbook化（前提/手順/結果判定/制約）タスクを起票する。

### Phase 5: Verify
- docs-check実行項目（必須メタ / 参照整合 / 差分整合）:
  1. 必須メタ: Requirement meta I/F のキー欠落がないことを目視確認。
  2. 参照整合: Scope と Related ADR/Spec が本Issue対象と一致することを確認。
  3. 差分整合: `git diff --check` で体裁崩れがないことを確認。
- 自己修復ルール: 失敗時は最大3回まで同ファイル内で修復し、4回目は停止して保留化する。

### Phase 6: Proceed
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

### Phase 2 ADR明文化
- Context: 04_Documentation の公開境界と内部向け記述の混在を解消し、公開可能文書の判定を固定する。
- Decision: 本Issueの Classification（Move internal / Improve external）を維持し、AC/DoDの不足はIssue本文で補う。
- Consequences: 後続PRは docs-only で実施し、設計正本（00〜02）を上書きしない。

### Phase 3 Plan
- AC/DoD不足のドラフト提案（合意済み扱い）:
  - AC-I1: Audience / Goal / Non-goal / Public boundary / Outcome / Related を対象文書冒頭に明示。
  - AC-I2: GoNoGoGate=Required の判定条件を本文で再現可能にする。
  - DoD-I1: Plan→Execute→Verify→Proceed の6Phase記録を残す。
- 非目標: 実装コード・CI・Stream H専有ファイルの変更は行わない。

### Phase 4 Execute
- 本Issueの分類方針に沿い、対応する対象文書へ公開境界メタとGo/No-Go判定導線を反映。

### Phase 5 Verify
- docs-check実施:
  - `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go" <target-doc>.md`
  - `git diff --check`
- 自己修復は最大3回まで。4回目相当は停止して保留化する。

### Phase 6 Proceed
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
- Decision: 本Issueの分類は **Improve external** を維持し、判定メタの再現性を優先する。
- Consequences: Open化時の差し戻し理由を「分類メタ不足」に限定できる。

### Phase 3 Plan（AC/DoD不足の補完）
- AC補強: Go/No-Go判定条件（Audience / Goal / 公開境界 / 次アクション）が本文で追跡可能であること。
- DoD補強: Proceed判定を `Ready / Hold / Needs-decision` の三値で明示すること。

### Phase 4 Execute（issue本文整備）
- 既存本文の分類方針を変更せず、メタ整合（DecisionQueueRef正規化・Open判定基準）のみ整備。
- 対象外（`04_Documentation/*` 実体、実装コード、他ストリームIssue）は未変更。

### Phase 5 Verify（docs-check / 自己修復上限3回）
- 実行: `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
- 実行: `git diff --check`
- 自己修復ポリシー: 不一致が出た場合は当該Issueのみ最大3回修復し、4回目相当で停止。

### Phase 6 Proceed（Open化候補判定）
- Open readiness: **Ready**
- 理由: 分類（Improve external）・検証レベル・GoNoGoGate・DecisionStatusが揃っており、本文改稿タスクと分離可能。
- Open化ラベル候補: `DOC-OPS-05`, `docs-check`, `classification-quality`, `stream-f`.


## 16) 共通ワークフローとフェイルセーフ（統一）

- 本Issue対応は 6Phase（Read → ADR明文化 → Plan → Execute → Verify → Proceed）で実施する。
- Verify 失敗時は自己修復を最大3回まで実施する。
- 4回目相当は停止し、`01_Plans/issues/` にブロッカー記録を追加して `Hold` へ遷移する。

## 17) Stream E execution record (2026-04-13)

### Phase 1 Read
- DOC-OPS-05-06 の分類（Improve external）と CE3/E2E 検証ログ連携要件を再確認。

### Phase 2 Plan
- `04_Documentation/e2e_testing.md` に CE3 Verify 自己修復順序（最大3回）を明文化し、再現性を強化。

### Phase 3 Execute
- CE3節へ `install chromium -> install-deps chromium -> rerun` の順序を追記。

### Phase 4 Verify
- `rg -n "CE3 Verify の自己修復順序|playwright install chromium|playwright install-deps chromium" 04_Documentation/e2e_testing.md`
- `git diff --check`

### Phase 5 Proceed
- 分類方針（Improve external）を維持しつつ、公開runbookとしての再現性要件を補強完了。


## 16) Stream G consolidated cycle（Read / CDC / Plan / Execute / Verify / Proceed）

### 1) Read（対象文書再読）
- 対象: `Scope` と `Related ADR/Spec` を再読し、公開境界（Audience / Goal / Non-goal / Public boundary）を再確認。
- 判定: 本Issueは docs-only のため、`03_Implement/**` は変更対象外。

### 2) CDC（Context / Decision / Consequences）
- Context: `DOC-OPS-05-06` は DOC-OPS-05 の文書分類と公開品質を固定するためのDraft。
- Decision: Classification は **Improve external** を維持し、既存のDecisionStatus=Fixedを正とする。
- Consequences: 後続作業は文書更新・参照整合・公開境界確認に限定される。

### 3) Plan（AC / DoD）
- AC: Audience / Goal / Non-goal / Public boundary / Outcome / Related を本文で追跡可能にする。
- DoD: Verifyで `docs-check`（メタ/語彙/固定値/リンク）を確認し、Proceedに `Ready/Hold/Needs-decision` を記録する。

### 4) Execute（文書更新）
- 本Issueメモを最新化し、後続の対象文書更新で使う判定材料を固定。
- 競合回避のため、分類結果そのもの（Move/Improve）は再判定しない。

### 5) Verify（リンク / 語彙 / 固定値）
- 推奨コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
  - `git diff --check`
- フェイルセーフ: 語彙ドリフトが解消不能、または自己修復3回超過時は停止してHold化する。

### 6) Proceed（issue状態更新案）
- 状態更新案: **Ready**（DecisionStatus=Fixed）。
- 保留条件: 参照リンク切れ / 固定値矛盾 / 語彙ドリフト未解消のいずれかを検知した場合は **Hold**。

## 18) Stream J execution record (2026-04-27)

### Phase 1: Read
- 対象を本Issue単体に限定し、`Scope`・`Requirement meta I/F`・`Expected verification level=docs-check` を再確認。
- 非干渉条件として、セキュリティ系・HIL/CE系Issueへは変更を波及させない方針を固定。

### Phase 2: ADR task（Context / Decision / Consequences）
- Context: `DOC-OPS-05-06` は `04_Documentation/e2e_testing.md` の公開配置判断と公開品質を確定する docs-only 課題。
- Decision: 既存方針 **Improve external** を維持し、追加ADRは作成せず Issue本文 CDC を正本として扱う。
- Consequences: 後続作業は公開runbook品質の改善導線に限定し、実装コード・セキュリティ系・HIL/CE系の変更は行わない。
- 承認待ち判定: **不要（DecisionStatus=Fixed のため）**。

### Phase 3: Plan
- AC/DoD確認項目を次の3点に固定:
  1. 分類根拠（Audience / Goal / 公開境界）を追跡可能であること。
  2. `GoNoGoGate=Required` の判定導線が本文で再現可能であること。
  3. Proceed 判定を `Ready / Hold / Needs-decision` の三値で明示すること。

### Phase 4: Execute
- 本Issueの実行記録を追記し、6Phase・ADR task・承認待ち判定を明文化。
- 対象外ファイルは変更しない（本Issue以外への非干渉を維持）。

### Phase 5: Verify（docs-check）
- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
  - `git diff --check`
- 自己修復ポリシー: 失敗時は最大3回まで同一Issue内で修復し、4回目相当は停止して `Hold` へ遷移。

### Phase 6: Proceed
- 判定: **Ready**
- 理由: 6Phase記録、ADR CDC、承認待ち判定（不要）が揃い、`VerificationLevel=docs-check` と整合。

## 16) Stream H canonical consolidation (Phase 1〜5)

### Phase 1 Read（14 Draft共通テンプレ差分抽出）
- 共通テンプレ（Requirement meta I/F, Acceptance criteria, Validation plan, Authoring Checklist）を再確認し、Issue固有差分は `Scope` / `Related ADR/Spec` / `推奨アクション` のみを主差分として固定。
- 対象: `04_Documentation/e2e_testing.md`

### Phase 2 ADR CDC必要性判定
- 判定: **追加ADR不要**（Issue本文の CDC 記録で十分）。
- 条件: 既存ADR/Specへの参照で判断根拠が追跡可能な場合、ADR新設は行わない。

### Phase 3 Plan（優先順）
1. Priority 1: 分類決定（Move internal / Improve external）を本文で固定。
2. Priority 2: Audience / Goal / Public boundary / Outcome / Related の追跡可能性を確認。
3. Priority 3: docs-check（`rg` / `git diff --check`）で体裁と導線を検証。

### Phase 4 Execute（文書配置見直し）
- Classification execution: **Improve external**
- 実行境界: Docs-only（`03_Implement/**` 非変更）。
- Move internal の場合は公開スタブ化と内部正本導線を優先し、Improve external の場合は公開可読性・公開境界の明示を優先。

### Phase 5 Verify（リンク・見出し・品質ゲート）
- Verify command set:
  - `rg -n "^#|^##|Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go" 04_Documentation/e2e_testing.md 01_Plans/documentation_quality.md`
  - `git diff --check`
- 自己修復ポリシー: 不整合は最大3回まで修復し、4回目相当は停止してブロッカー化する。

## Phase 1-5 execution record (2026-04-16, DOC-OPS-05-06/07/08/09/10 scope)

### Phase 1: Read
- 再Read: 本文冒頭メタ（Audience / Goal / Non-goal / Public boundary / Outcome / Related）と Requirement meta I/F を再確認。
- スコープ確認: 本タスクは「当該Issue本文 + 当該Scope文書」のみを編集対象とする。

### Phase 2: Plan
- 再Read: 関連ADR（特に ADR-0019）と `01_Plans/documentation_quality.md` の参照導線を再確認。
- 計画: Read → Plan → Execute → Verify → Proceed を単一サイクルで実施し、記録を追記する。
- フェイルセーフ: Verify 失敗時の自己修復は最大3回まで、4回目相当は停止。

### Phase 3: Execute
- 再Read: 直前差分と本文の禁止事項（SafeMode後退、公開境界逸脱）を再確認してから編集。
- 実施内容: 本セクションを追記し、Phase運用・再Read・修復上限ルールを明文化。

### Phase 4: Verify
- 再Read: 追記後の本文を再読し、語彙ドリフト・参照不整合・体裁崩れの有無を確認。
- 実施: `git diff --check` と対象ファイルの目視確認を実施。
- 修復回数: 0回（3回超過なし）。

### Phase 5: Proceed
- 再Read: Verify結果とスコープ逸脱の有無を再確認。
- 判定: **Ready**（docs-only、許可範囲内、停止条件なし）。
- 継続条件: 後続差分でも同じ5Phase + 再Read + 修復上限3回を維持する。


## 18) Stream I serial execution (Phase 1..5 fixed, 2026-04-16, DOC-OPS-05-06)

### Phase 1: Read
- Read: Requirement meta I/F・Scope・Related ADR/Spec・推奨アクション（Improve external）を再確認。
- Read: 既存のStream記録との差分を確認し、本実行は **Phase 1..5固定** で進行することを明記。
- Read outcome: 対象は docs-only、`04_Documentation/e2e_testing.md` の分類・改善計画に限定。

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
- Execute: 本Issueの分類方針（Improve external）を維持し、公開境界メタと次アクション導線を固定。
- Execute: DecisionStatus=Fixed のため DecisionQueueRef は `N/A` を維持。

### Phase 4: Verify
- Read: docs-check対象コマンドを再確認。
- Verify command:
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
  - `git diff --check`
- Verify policy: 失敗時は最大3回まで修復、4回目相当は停止して `Hold` 化。

### Phase 5: Proceed
- Read: Verify結果とGo/No-Go判定基準を再確認。
- Proceed status: **Ready**（現時点でDecisionStatus=Fixed、検証レベル=docs-check、分類方針=Improve external）。
- Next action: docs-only PR で分類方針を反映し、未解決論点は `01_Plans/issues/` へ分離記録。

## DOC-OPS-05 Stream G 前半フェーズ実行記録（2026-04-16）

- Classification確認: **Improve external**（再判定なし）
- フェイルセーフ固定: 用語ドリフト検知・固定値不一致検知・自己修復3回超過で停止（Hold）

### Phase 1: Read（対象ファイル再読）
- 本ファイルを再読し、Scope / Audience / Goal / Public boundary / Related の整合を確認。

### Phase 2: Plan（対象ファイル再読）
- 本ファイルを再読したうえで、docs-only の変更範囲と受入条件を固定。

### Phase 3: Execute（対象ファイル再読）
- 本ファイルを再読したうえで、分類方針（Move internal / Improve external）を維持して更新。

### Phase 4: Verify（docs-check、対象ファイル再読）
- 本ファイルを再読したうえで docs-check を実施。
- 推奨確認: `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go" 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
- 体裁確認: `git diff --check`

### Phase 5: Proceed（対象ファイル再読）
- 本ファイルを再読したうえで状態を判定し、`Ready / Hold / Needs-decision` を記録。
- 判定: **Ready**（現時点で保留なし）。


## 17) Stream G rerun-03（2026-04-17, AUTH-OPS-03同期）

### Phase 1 Read
- D1〜D4 固定値、役割語彙（Security Officer / System Owner / Platform Operator）、状態語彙（DraftRequest〜Closed + StoppedForClarification）を正本と対象文書で再読した。

### Phase 2 ADR CDC
- 判定: 既存AUTH-OPS-03固定値で充足。**方針変更なしのため新規CDC/ADR追加なし**。

### Phase 3 Plan（AC/DoD）
- AC: 語彙一致 / 責務分離 / 導線一致（architecture -> security -> guidelines -> e2e）/ 固定値一致（D1〜D4）。
- DoD: docs-check + `git diff --check` 成功、不一致0件。

### Phase 4 Execute
- e2e側の docs-check コマンドに `operations.md` を追加し、D1〜D4 と状態語彙の照合対象を明示した。

### Phase 5 Verify
- `python 01_Plans/issues/validate_active_issue_memos.py`
- `rg -n "Security Officer|System Owner|Platform Operator|DraftRequest|ApprovalPending|Approved|ActiveException|RollbackPending|Closed|StoppedForClarification|D1|D2|D3|D4|4h|2h|48h|15m|60m" 02_Architecture/strict_mode_exception_approval_flow.md 04_Documentation/operations.md 04_Documentation/security.md 04_Documentation/security_operational_guidelines.md 04_Documentation/e2e_testing.md`
- `git diff --check`

### Phase 6 Proceed
- 判定: **Ready**（ドリフト0）。不一致が1件でも再発した場合は `StoppedForClarification` で停止する。

## 19) Stream I dedicated cycle (2026-04-18)

### Phase 1 Read
- Read Order（00_Prompt → 01_Plans/ADR → 02_Architecture）と本Issueの `Requirement meta I/F` を再確認。
- 本Streamの編集許可ファイル以外は非接触とし、Stream G競合が発生した場合は issue本文の追記のみ先行する。

### Phase 2 ADR-CDC（必要時のみ）
- 判定: **既存ADRで充足（追加ADR起票なし）**。
- Context: DOC-OPS-05 Draft issue の Open化判断を、公開境界と検証導線の観点で固定する。
- Decision: 本Issueは既存の推奨アクション（Move internal / Improve external）を維持し、メタI/F不足のみ補完する。
- Consequences: 後続PRは docs-only の最小差分へ限定し、実装・スキーマ層へ波及させない。

### Phase 3 Plan
- AC補完:
  - AC-I-1: `Audience / Goal / Non-goal / Outcome / Related` の追跡可能性を維持する。
  - AC-I-2: `GoNoGoGate=Required` の判定条件を本文から再現可能にする。
  - AC-I-3: `DecisionStatus=Fixed` の場合は `DecisionQueueRef=N/A` を維持する。
- DoD補完:
  - DoD-I-1: 強制サイクル `Plan → Execute → Verify → Proceed` の証跡を残す。
  - DoD-I-2: Verify失敗時の自己修復は最大3回、4回目相当で停止する。

### Phase 4 Execute
- Issue本文の範囲で、分類方針・Go/No-Go条件・検証導線を維持/補強する（最小差分）。
- 編集禁止対象（他Stream専有ファイル、03_Implement配下、統合ファイル）には変更を加えない。

### Phase 5 Verify
- docs-check（Issueメモ検証）:
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
- 差分整合:
  - `git diff --check`
- 自己修復ポリシー: 失敗時は同一Issue内で最大3回まで修復し、4回目相当で停止して `Hold` とする。

### Phase 6 Proceed
- 判定: **Ready（Draft維持のままOpen準備可）**。
- Proceed条件: AC/DoD/Verifyが成立し、競合ファイル・前提崩壊・修復3回超過のいずれにも該当しない。
- フェイルセーフ: 上記停止条件を検知した場合は作業を停止し、未解決事項を本Issue本文へ記録して継続実行を禁止する。

## 16) Stream G DOC-OPS-05 triage fix（2026-04-18）

### Phase 1 Read（Scope / Priority / AC 抽出）
- Scope/Priority/Requirement meta I/F を再読し、`推奨アクション`・`VerificationLevel=docs-check`・`DecisionStatus=Fixed` の一致を確認。
- AC未充足として「分類根拠の明文化」「次実行単位の固定」「GoNoGoGate判定条件の再現性」を抽出。

### Phase 2 ADR CDC（新方針要否）
- 判定: **追加ADRなし（Issue内CDCで固定）**。
- Context: DOC-OPS-05 は文書本文の全面改稿ではなく、公開境界の分類決定と実行順序固定が目的。
- Decision: 本Issueの分類を **Improve external** として確定し、後続は docs-only 変更単位に限定。
- Consequences: 実装/他Issueへ波及させず、Open化判定を分類メタの充足可否で一意に判断可能。

### Phase 3 Plan（AC/DoD不足ドラフト）
- AC-G1: Audience / Goal / Public boundary / Related を対象文書に追記するタスクを次PR要件に固定。
- AC-G2: GoNoGoGate=Required の判定条件（上記4点 + Validation + Non-goal）をIssue本文で追跡可能化。
- DoD-G1: Proceed判定を `Ready / Hold / Needs-decision` の三値で残す。
- DoD-G2: Validationは docs-check（メタ確認・参照整合・`git diff --check`）を必須実行手順に固定。

### Phase 4 Execute（分類根拠・次実行単位の固定）
- Classification（確定）: **Improve external**
- 分類根拠: AudienceとPublic boundaryを基準に、内部運用正本と外部公開導線の混在解消を優先。
- 次実行単位（固定）: `04_Documentation/e2e_testing.md` を公開手順正本として Smoke/Core/Safety の受入基準を明示する改善PRを起票する。

### Phase 5 Verify（docs-check整合 / 修復上限3回）
- 実行: `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
- 実行: `git diff --check`
- 判定: 失敗時は同Issue内修復を最大3回まで。4回目相当は Fail-safe に従い停止。

### Phase 6 Proceed（Ready化候補）
- 状態: **Ready**
- Ready化条件: Classification固定・AC/DoD不足ドラフト記録・次実行単位固定・Verification手順固定を満たす。
- Fail-safe確認: 分類不能/競合方針/scope外編集要求は未検出。

## 18) Stream I mid-1 execution record (2026-04-19, DOC-OPS-05-06)

### Phase 1 Read（対象再読）
- 本Issue本文と `04_Documentation/e2e_testing.md` を再読し、Scope/Classification/VerificationLevel=docs-check を再確認。

### Phase 2 ADR CDC（対象再読）
- Context: E2E手順は公開可能文書として維持しつつ、内部ログとの差分境界を固定する必要がある。
- Decision: Classification は **Improve external** を維持し、runbook の公開品質改善を優先する。
- Consequences: 変更は docs-only で実施し、ADR-0019 の運用正本と矛盾する改変を避ける。

### Phase 3 Plan（対象再読）
- AC補完: 公開境界メタ・Go/No-Go・関連文書導線が再現可能であること。
- DoD補完: Read → ADR CDC → Plan → Execute → Verify → Proceed を記録する。

### Phase 4 Execute（対象再読）
- 本セクションを追加し、Stream I mid-1 の6Phase運用を固定。

### Phase 5 Verify（対象再読）
- `rg -n "Stream I mid-1|Phase 1 Read|Phase 2 ADR CDC|Phase 6 Proceed" 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
- `git diff --check`
- 自己修復: 0/3 回（超過なし）。

### Phase 6 Proceed（対象再読）
- 判定: **Ready**
- 理由: Improve external 方針と docs-check ゲートが本文でトレース可能。

## Stream I phase execution record（2026-04-19 / DOC-OPS-05-06）

### Phase 1) Read
- Requirement meta I/F と分類（Move internal / Improve external）、関連 04_Documentation 対象文書を再読。

### Phase 2) セキュリティ境界優先
- SafeMode既定ON、share/export漏えい防止、公開境界（Public boundary）の後退禁止を優先確認。

### Phase 3) e2e/testing/release整合
- `e2e_testing.md` / `operations.md` / `release.md` と当該Issueの受入条件・検証レベル（docs-check）を照合。

### Phase 4) installation/config/narratives/local-llm整合
- `installation.md` / `local_llm_ops_guide.md` / `narratives.md` と責務重複がないことを確認。

### Phase 5) Verify
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|GoNoGoGate|VerificationLevel" <target>`
- `git diff --check`
- 自己修復は最大3回。4回目相当は `Hold` で停止。

### Phase 6) Proceed
- 判定: **Ready**（docs-only / 許可スコープ内 / DecisionStatus=Fixed維持）。

## 18) Stream F DOC-OPS-05後半（Phase 1〜5: Read同期→CDC→AC/DoD→Rollback→Verify/Proceed）

### Phase 1) Read同期（毎Phase開始）
- Read Order の上流（`00_Prompt/system_prompt.md` / `00_Prompt/domain.md` / `01_Plans/adr/ADR-0001-value-to-requirements.md`）と、対象Scope（`04doc_e2e_testing.md`）の境界を突合。
- `Expected verification level=docs-check` / `VerificationLevel=docs-check` / `DecisionStatus=Fixed` の3点を再確認し、差し戻し条件を固定。

### Phase 2) セキュリティ/運用境界のCDC明文化→承認
- Context: DOC-OPS-05後半では、公開文書の境界を曖昧にしないことが最優先。
- Decision: Classification（`Improve external`）は再判定せず維持し、SecurityGateImpact と GoNoGoGate の判定軸を本文で追跡可能にする。
- Consequences: 後続PRは docs-only に限定し、公開境界の曖昧化や未承認確定化を防止する。
- 承認条件: `Ready / Hold / Needs-decision` の三値で Proceed 判定を記録する。

### Phase 3) docs-check向け AC/DoD 固定
- AC-F-1: Audience / Goal / 公開境界 / 次アクションの4点をIssue本文で再現可能にする。
- AC-F-2: `DecisionQueueRef` は `DecisionStatus=Fixed` のとき `N/A` を維持する。
- DoD-F-1: Verify は「メタキー整合」「参照整合」「差分整合」の3系統を必須実施とする。
- DoD-F-2: `GoNoGoGate=Required` の判定根拠を本文中で追跡可能にする。

### Phase 4) 検証計画と失敗時ロールバック固定
- 検証コマンド（共通）:
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
  - `git diff --check`
- 失敗時ロールバック:
  1. 当該Issueのみ最小差分で自己修復（最大3回）。
  2. 4回目相当は **即停止** し、状態を `Hold` に変更。
  3. 停止理由を「公開境界の曖昧化」または「承認なし確定化の疑い」として記録。

### Phase 5) Verify / Proceed
- Verify判定: docs-checkで不整合がない場合のみ `Ready`。
- Proceed条件: 公開境界を曖昧化せず、承認なしで確定化していないこと。
- Fail-safe再掲: 公開境界の曖昧化・承認なし確定化を検知した時点で作業を停止する。

## 17) Phase cycle update (2026-04-20, independent scope)

### Phase 1) Read
- 対象Issue本文の `Requirement meta I/F` / `Acceptance criteria` / `Validation plan` を再読し、分類が **Improve external** で固定済みであることを確認。
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
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
  - `git diff --check`
- 自己修復上限: 3回。4回目相当は Stopper に従い停止。

### Phase 5) Proceed（次の1手 / 未解決点）
- 次の1手: `04_Documentation/e2e_testing.md` の公開runbook節（Audience/Goal/Go-No-Go）を最小差分で補強。
- 未解決点: 未解決なし（DecisionStatus=Fixed）。
- Stopper確認: 未定義競合なし / safeMode後退語彙なし / 自己修復回数は上限内。

## DOC-OPS-05 Lane Update (2026-04-20)

### Phase 1) Read（対象Issueの現状・関連Spec確認）
- 対象: `issue-doc-ops-05-06-04doc-e2e-testing.md`（Draft memoのみ）。
- 参照した関連Spec: 本Issueの `Related ADR/Spec`、`01_Plans/documentation_quality.md`、`01_Plans/adr/ADR-0001-value-to-requirements.md`。
- 現状判定: Classification は **Improve external**、VerificationLevel は `docs-check` を維持。

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
- Decision: 本Issueは **Improve external** を維持し、Issue単位でOpen準備条件を固定。
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


## 99) Phase refresh (2026-04-20 / DOC-OPS-05 strict 5-phase)

### Phase 1 Read（Audience / Goal / 公開境界確認）
- Audience: 公開文書の読者（利用者 / 運用担当 / コントリビュータ）に限定し、内部運用専用読者を分離対象として再確認。
- Goal: `04_Documentation/e2e_testing.md` の公開可否と改善方針を、Issue本文だけで再現可能な形で固定する。
- 公開境界: 仕様正本（00〜02）・内部運用ログ（01）・対外ガイド（04）の境界を混在させない。

### Phase 2 Plan（docs-only範囲固定 / 実装修正禁止）
- Scope 固定: 本Issueメモの更新のみ（docs-only）。
- 禁止事項: `03_Implement/**` と実装仕様の変更、CI設定変更、Schema変更。
- 期待成果: 分類・AC・Validation・Proceed判定を5Phaseで追跡可能にする。

### Phase 3 Execute（AC / Task breakdown / Validation整備）
- Classification（固定）: **Improve external**
- AC整備: Audience / Goal / 公開境界 / Next action / VerificationLevel の5点を判定必須項目として固定。
- Task breakdown整備: 判定（Read）→ 方針固定（Plan）→ 記録更新（Execute）→ 検証（Verify）→ Open判定（Proceed）を単一路線化。
- Validation整備: `docs-check` と `git diff --check` の2系統を必須にし、失敗時は自己修復最大3回で停止条件を適用。

### Phase 4 Verify（Expected verification level整合確認）
- 整合結果: `Expected verification level=docs-check` と `VerificationLevel=docs-check` は一致。
- 実行手順（再現用）:
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
  - `git diff --check`
- 判定: docs-only Issueとして必要十分（unit/integration/e2e は対象外）。

### Phase 5 Proceed（Open化条件判定 / 致命エラー時停止）
- Open化条件: Classification固定、GoNoGoGate=Required、DecisionStatus=Fixed、Validation手順明記の4条件を満たすこと。
- 判定: **Ready（Open候補）**。
- 致命エラー時停止条件: 必須メタ欠落 / VerificationLevel不一致 / Scope逸脱が検出された場合は **即時Hold** に遷移し、次編集を停止する。

## 18) Stream J serial execution record（Phase 1-5 strict）

### Phase 1: Read（開始時Read必須）
- 開始時Read（Read Order上流）: `00_Prompt/system_prompt.md` → `00_Prompt/domain.md` → `00_Prompt/handoff.md` → `00_Prompt/agent_handover.md` → `00_Prompt/codex_gsd_skill_ops.md` → `00_Prompt/ai_cognitive_externalization_requirements.md`。
- 判断軸Read: `01_Plans/adr/ADR-0001-value-to-requirements.md` / `02_Architecture/architecture.md` / `02_Architecture/schemas.md`。
- Issue固有Read: `Scope=04_Documentation/e2e_testing.md` と `Related ADR/Spec`、`Requirement meta I/F` を再確認し、`VerificationLevel=docs-check` を固定。

### Phase 2: Plan
- 単一責務: `DOC-OPS-05-06` のIssueメモ品質を **Phase 1-5 直列処理** に正規化する。
- 実施計画:
  1. Phase見出しを Read→Plan→Execute→Verify→Proceed の5段に統一。
  2. Proceed判定を `Ready / Hold / Needs-decision` 三値で残す。
  3. docs-onlyスコープ（Issueメモのみ）を維持し、実装コード変更を禁止。

### Phase 3: Execute
- 本Issueに Stream J 記録を追記し、5Phase運用を明示。
- `DecisionStatus=Fixed` のため `DecisionQueueRef=N/A` を維持し、追加判断待ちを作らない。
- 変更範囲を本Issueファイル内に限定。

### Phase 4: Verify
- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
  - `git diff --check`
- 判定基準: メタI/F欠落なし・体裁崩れなし・5Phase記録が同一Issue内で完結。

### Phase 5: Proceed
- 判定: **Ready**
- 理由: 開始時Read、Plan→Execute→Verify→Proceed の直列記録を同一Issueで完結済み。
- 次アクション: 対応する `04_Documentation/*` 本文改稿PRを docs-only で分離実施する。

## Stream H mid-cycle execution record（2026-04-20 / DOC-OPS-05-06）

### Phase 1 Read（対象Issue再読）
- 本Issue本文を再読し、`Requirement meta I/F`・`推奨アクション`・`GoNoGoGate`・`VerificationLevel` を再確認。
- 直列対象5Issue以外は編集禁止であることを再確認し、shared resource には非接触で進行。

### Phase 2 Plan（対象Issue再読）
- 本Issueを再読した上で、今回の主責務を「Issueメモの5Phase実行記録の更新」に限定。
- AC/DoD不足へのAIドラフト提案（合意後反映対象）:
  - AC-H-mid-1: Phase開始時の対象Issue再読ログが各Issue本文に残っていること。
  - AC-H-mid-2: Verify/Proceed の判定が `Ready / Hold / Needs-decision` で追跡できること。
  - DoD-H-mid-1: docs-checkコマンド結果と変更境界（5Issue限定）を記録すること。

### Phase 3 ADR CDC（対象Issue再読・必要時判定）
- 対象Issue再読後の判定: **追加ADR不要**（既存ADR/Spec参照とIssue CDCで十分）。
- Context: DOC-OPS-05中盤では、公開境界の判断を崩さずに実行ログを整備する。
- Decision: `Improve external` を維持し、DecisionStatus=Fixedを前提に運用する。
- Consequences: 後続実装は docs-only を維持し、対象外ファイルの変更を発生させない。

### Phase 4 Execute（対象Issue再読）
- 対象Issueを再読後、本文へ本5Phase記録を追記。
- 変更範囲を当該5Issueに限定し、他ファイルは未変更。

### Phase 5 Verify / Proceed（対象Issue再読）
- Verify（docs-check）:
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
  - `git diff --check`
- 自己修復ポリシー: 不整合時は最大3回修復し、4回目相当で停止。
- Proceed判定: **Ready**（DecisionStatus=Fixed、推奨アクション維持、5Issue限定編集を満たす）。

## 19) Stream I dedicated execution record (2026-04-21)

### Phase 1 Read（対象ファイル再読）
- 再読対象: 本Issue全文を再読し、`Requirement meta I/F`・`Proposed solution`・`Acceptance criteria`・`Validation plan` を確認。
- スコープ固定: 指定対象3ファイル以外は編集禁止。

### Phase 2 Plan（AC/DoD補完、対象ファイル再読後）
- 再読実施: Plan開始時に本Issue本文を再読。
- AC補完: Audience / Goal / 公開境界 / 次アクション / VerificationLevel一致を Proceed 判定の必須条件として維持。
- DoD補完: 5Phase（Read→Plan→Execute→Verify→Proceed）を同一Issue本文で追跡可能にする。

### Phase 3 Execute（対象ファイル再読後に実施）
- 再読実施: Execute開始時に本Issue本文を再読。
- 実施内容: 本Stream I専任記録（本節）を追記し、指定スコープ内での実行証跡を明文化。
- ADR CDC判定: `DecisionStatus=Fixed` のため追加CDCは不要（必要時のみ明文化ルールを適用）。

### Phase 4 Verify（対象ファイル再読後に実施）
- 再読実施: Verify開始時に本Issue本文を再読。
- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
  - `git diff --check`
- 失敗時の自己修復: 同一ファイル内で最大3回。4回目相当は停止し `Hold`。

### Phase 5 Proceed（対象ファイル再読後に判定）
- 再読実施: Proceed開始時に本Issue本文を再読。
- 判定: **Ready**。
- 停止条件: 3回超過修復 / 未定義競合 / 前提崩壊が発生した場合は作業停止して指示待ち。

## 18) DOC-OPS-05 前半専任シリアル実行記録（2026-04-21）

### Phase 1 Read（開始時最新状態再読）
- `Requirement meta I/F`・`推奨アクション=Improve external`・`DecisionStatus=Fixed`・`VerificationLevel=docs-check` を再確認。
- 公開/内部分類の判断根拠を再確認（Audience/Goal/公開境界）。

### Phase 2 Plan（AC/DoD補完提案と合意）
- AC補完提案:
  - AC-S1: Audience=`導入検証者/QA担当（外部利用者含む）` を明示する。
  - AC-S2: Goal=`E2E手順の公開runbook品質向上` を明示する。
  - AC-S3: 公開境界=`公開文書として維持（内部ログ原本は分離）` を明示する。
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
- 理由: 分類=Improve external、判断根拠3点（Audience/Goal/公開境界）明記、DoD/Verify上限ルールを固定済み。

## 18) Stream H Set-1 execution record (2026-04-21, serial-3: e2e-testing)

### Phase: Read
- 対象Issue本文を再読し、`Scope=04_Documentation/e2e_testing.md` と `Expected verification level=docs-check` を確認。
- 分類方針 `Improve external`（公開runbook改善）が維持されていることを再確認。

### Phase: Plan
- 本Issueの主責務を「E2E手順の公開品質改善計画固定」に限定。
- 判定軸は `Audience / Goal / Public boundary / GoNoGoGate` を必須項目として維持。

### Phase: Execute
- Stream H の直列3件目として、5Phaseログ（Read→Plan→Execute→Verify→Proceed）を追記。
- 既存方針（docs-only、DecisionStatus=Fixed）を変更せず、記録の再現性のみ強化。

### Phase: Verify
- `git diff --check` を実行し、体裁崩れがないことを確認。
- 本作業はissueメモ更新のみのため、実行系E2Eテストは対象外。

### Phase: Proceed
- 判定: **Ready**。
- 次アクション: `04_Documentation/e2e_testing.md` の実行前提・結果判定・失敗時導線を公開向けに整理するPRへ進む。

## 19) Stream I serial record (2026-04-22, DOC-OPS-05 test/diagnostics lane)

### Phase 1 Read
- Scope / Related ADR/Spec / Expected verification level（`docs-check`）を再読し、docs-only前提を再確認。
- 事前想定との差分: 既存記録のphase表現に揺れがあるため、本レコードでは 5Phase に統一する。

### Phase 2 Plan
- AC/DoD不足を補完して合意済み化（ユーザー承認: 2026-04-22）。
- 追加AC:
  - AC-P1: Stream I記録は 5Phase（Read→Plan→Execute→Verify→Proceed）に固定。
  - AC-P2: Verifyに docs-check コマンドと self-correction上限（最大3回）を必ず明記。
  - AC-P3: Proceedに Stop条件（3回超過 / 前提崩れ / 競合検知）と再開条件を明記。
  - AC-P4: 記録内容は本Issue Scope（e2e_testing）に限定。
- 追加DoD:
  - DoD-P1: Stream Iの実行順は diagnostics → e2e_testing → e2e_verification_log の直列。
  - DoD-P2: `validate_active_issue_memos.py --files` と `git diff --check` を実行。
  - DoD-P3: 失敗時の自己修復は最大3回、4回目相当は停止。

### Phase 3 Execute
- 直列2件目として本Issue（e2e_testing lane）の記録を更新。
- 分類方針（Improve external）・DecisionStatus（Fixed）・VerificationLevel（docs-check）は既存値を維持。

### Phase 4 Verify
- docs-check:
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
  - `git diff --check`
- self-correction方針: 失敗時は当該ファイル内で最大3回修正し、3回超過で停止。

### Phase 5 Proceed
- 判定: **Ready**（本ファイルのStream I記録更新を完了）。
- 停止条件:
  - self-correction 3回超過
  - 前提崩れ（docs-only条件や指定編集境界の破綻）
  - 競合検知（他ストリーム編集と衝突）
- 再開条件:
  - 停止原因の明文化
  - 修正方針と編集境界の再合意
  - 直前失敗コマンドの再実行で正常化を確認

## 16) DOC-OPS-05 dedicated serial run (2026-04-22)

### Phase 1 Read
- 対象Issue `DOC-OPS-05-06` の最新本文（Requirement meta I/F / AC / Validation plan）を再確認。
- Scope対象文書 `04_Documentation/e2e_testing.md` を read-only 参照し、公開境界・読者・目的の現状を確認。
- 前提崩れ/競合検知: **なし**。

### Phase 2 Plan
- AC/DoD不足のドラフト提案: docs-check結果を Issue メモ側に記録し、Proceed 判定を `Ready / Hold / Needs-decision` で固定する。
- 合意: 本Issueは docs-only の分類/実行メモ整備として進行し、指定外ファイルは編集しない。
- ADR要否判定: **不要**（文書分類メモ更新のみで設計決定の新設なし）。

### Phase 3 Execute
- 実施: 本Issueメモに専任実行ログ（Phase 1〜5）を追記。
- 分類方針: **Improve external** を維持。
- 変更範囲: `01_Plans/issues/issue-doc-ops-05-XX-*.md` のみ。

### Phase 4 Verify
- docs-check 実行計画: `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` と `git diff --check`。
- 自己修復ポリシー: 不整合時は同一Issueメモ内で最大3回修復、4回目相当は停止。
- 本Issue時点の修復回数: **0/3**（全体検証で最終確認）。

### Phase 5 Proceed
- 判定: **Ready**。
- 次Issueへ進行条件: docs-check 通過と指定14ファイル限定編集の維持。
- 停止条件: 4回目修復相当 / 前提崩れ / 競合検知。

## 20) DOC-OPS-05 Batch2専任実行記録（2026-04-22, 固定6Phase）

### Phase 1 Read
- Phase開始時に本Issueファイル（`DOC-OPS-05-06`）を再読し、`Scope` / `Related ADR/Spec` / `VerificationLevel=docs-check` を確認。
- 判定: docs-only 範囲は維持、指定外ファイルは編集しない。

### Phase 2 ADR/CDC
- Phase開始時に本Issueファイルを再読し、既存 CDC 記録との整合を確認。
- Context: e2e_testing文書は公開改善（Improve external）として扱う既定方針。
- Decision: 追加ADRは不要、Issue内CDCを正本として運用継続。
- Consequences: 実装変更は禁止、Issueメモの運用証跡更新のみ実施。

### Phase 3 Plan
- Phase開始時に本Issueファイルを再読。
- AC/DoD不足点の確認結果: 固定6Phase導線（Read→ADR/CDC→Plan→Execute→Verify→Proceed）を明示的に追記する必要あり。
- ドラフト提案（合意済み）:
  - AC-B2-06-1: 各Phase冒頭で対象ファイル再読を明記する。
  - AC-B2-06-2: Verify失敗時の自己修復上限3回と、4回目相当で停止を明記する。
  - DoD-B2-06-1: Proceedに停止条件（前提崩れ/未定義競合/3回超過）と再開条件を残す。
- 合意後にのみExecuteへ進行。

### Phase 4 Execute
- Phase開始時に本Issueファイルを再読。
- 実施内容: Batch2専任として本6Phase記録を追記し、既存分類（Improve external）を維持。
- 変更境界: `01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md` のみ。

### Phase 5 Verify
- Phase開始時に本Issueファイルを再読。
- docs-check:
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
  - `git diff --check`
- 自己修復ルール: 失敗時は同一ファイル内で最大3回、4回目相当は即停止。

### Phase 6 Proceed
- Phase開始時に本Issueファイルを再読。
- 判定: **Ready**。
- 停止条件: 前提崩れ / 未定義競合 / 自己修復3回超過。
- 再開条件: 停止原因の明文化、修復方針の合意、直前失敗コマンド再実行で正常化確認。

## Stream G normalization pass (2026-04-22)

### Phase 1) Read
- `Status=Draft` / `Scope` / `Expected verification level=docs-check` の一致を再確認。
- 既存記録内の Proceed 表記ゆれ（Phase 5 / Phase 6）を検知し、本passでは **5段階（Read/Plan/Execute/Verify/Proceed）** を正とする。

### Phase 2) Plan
- 分類基準を 3軸で統一：
  1. **Audience**: 主読者が外部利用者か内部運用者か
  2. **Goal**: 文書目的が公開ガイドか内部運用・証跡か
  3. **公開境界**: `04_Documentation` に置く妥当性があるか
- 本Issueの分類決定を固定: **Improve external**。

### Phase 3) Execute
- Issue本文は docs-only 計画メモとして整形し、実装変更は行わない。
- 分類・AC・Validation の整合のみを対象にし、対象外（04_Documentation本体、shared resource、他Issue群）は未編集を維持。

### Phase 4) Verify
- docs-check:
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
  - `git diff --check`
- 期待結果: メモ形式エラーなし、差分の体裁崩れなし。

### Phase 5) Proceed
- 判定: **Ready**
- 理由: 分類基準（Audience/Goal/公開境界）・`VerificationLevel=docs-check`・`DecisionStatus=Fixed` が揃っているため。


## DOC-OPS Track 2 serial cycle（2026-04-22 / 05-06）

### Phase 1 Read（同期）
- 対象再読: 本Issue本文と `04_Documentation/e2e_testing.md` を再読し、分類=**Improve external** を同期確認。
- 固定条件: docs-only / 指定外ファイル非編集 / Verify自己修復は最大3回。

### Phase 2 ADR/CDC（承認待ち）
- Context: E2E実行手順は公開runbookとして維持しつつ、内部証跡との混在を避ける必要がある。
- Decision（提案）: `04_Documentation/e2e_testing.md` は外部向け手順正本として維持し、検証ログは `e2e_verification_log` 側へ責務分離する。
- Consequences: 公開導線は明確化されるが、分類確定はレビュー承認まで **Pending approval** とする。

### Phase 3 Plan
- Plan-1: Audience / Goal / Non-goal / Public boundary の明記を維持。
- Plan-2: Go/No-Go判定基準と再実行条件を本文から追跡可能にする。
- Plan-3: docs-check（`rg` + `git diff --check`）で整合確認。

### Phase 4 Execute
- 本Issueへ Track 2 の6Phase記録を追記（docs-only）。

### Phase 5 Verify
- Verify command: `rg -n "DOC-OPS Track 2 serial cycle|Phase 1 Read|Phase 2 ADR/CDC|Pending approval" 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
- Verify command: `git diff --check`

### Phase 6 Proceed
- 判定: **Ready（承認待ち）**
- 停止条件: Verify失敗が3回を超えた場合はHoldへ移行し、追加編集を停止。

## Stream G serial lane run（2026-04-22, Phase 06）

### Phase 1: Read
- 対象再読: `01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md` と対象Doc `04_Documentation/e2e_testing.md` を最新状態で再読。
- メタ確認: `Audience / Goal / 公開境界 / GoNoGoGate / SecurityGateImpact` の不足有無を確認。

### Phase 2: Plan
- Audience: DOC-OPS-05 の公開文書整備担当者（人間レビュー担当 + 生成AI運用担当）。
- Goal: `04_Documentation/e2e_testing.md` の分類と公開境界を再現可能な計画品質で固定する。
- 公開境界: 実装詳細・内部判断メモは非公開、公開運用に必要な説明のみ対象。
- GoNoGoGate: `Required`（Open化前に判定根拠の明示を必須化）。
- SecurityGateImpact: `public-exposure`（公開時の情報漏えい・過剰公開を防止）。

### Phase 3: Execute
- docs-only 更新として、本Issueメモに Stream G 直列処理ログを追記。
- 指定外編集（実装コード / HIL・CE・FB 系Issue）は未実施。

### Phase 4: Verify
- docs-check:
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
  - `git diff --check`
- diff整合: 1ファイル単位の差分で体裁崩れがないことを確認。

### Phase 5: Proceed
- 判定: **Ready**（推奨アクション `Improve external` を維持）。
- 次工程: Phase 07（存在する場合）の対象Issueへ直列進行。
- フェイルセーフ: 自己修復は最大3回。4回目相当・未定義競合・指定外編集検知時は `Hold` で停止。

## Stream I ownership follow-up（2026-04-22 / lane 05-06）

### Phase 1 Read
- 本Issue本文と対象Doc `04_Documentation/e2e_testing.md` を再読し、Classification=`Improve external` と docs-only 境界を再確認。

### Phase 2 Plan
- 5Phase（Read → Plan → Execute → Verify → Proceed）を固定し、Verify自己修復は最大3回とする。
- E2E手順正本と verification log の責務分離を維持し、指定外ファイル編集を禁止する。

### Phase 3 Execute
- 本Issueへ ownership follow-up 記録を追記（docs-only）。

### Phase 4 Verify
- `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
- `git diff --check`

### Phase 5 Proceed
- 判定: **Ready**
- フェイルセーフ: 自己修復3回超過または未定義競合検知時は **Hold**。


## 2026-04-23 Stream G DOC-OPS-05 Draft contract alignment（Issue 05-06）

### Phase 1) Read
- 本Issueの `Requirement meta I/F`・`Acceptance criteria`・`Validation plan` を再読し、本文契約の欠落有無を確認。
- 対象を本Issueメモのみに限定し、`04_Documentation/*` 実ファイルは編集対象外であることを確認。

### Phase 2) ADR/CDC（必要時）
- 追加ADRは起票しない。既存方針（DOC-OPS-05 Draft群の契約整備）に従い、Issue本文内の運用記録をCDCとして扱う。
- CDC要約: Context=公開文書ドラフト契約の再現性確保 / Decision=6Phase直列処理を固定 / Consequence=docs-onlyメモ更新で完結。

### Phase 3) Plan（AC/DoD不足提案）
- AC提案: 「対象ドキュメント1ファイルをmock対象として明記」「他Issue非依存」「Verifyコマンド明記」を必須化。
- DoD提案: `Proceed` で `Ready/Hold/Needs-decision` を必ず記録。
- Self-Correction制約: 同一Issueで修復は最大3回、4回目相当または競合検知で停止。

### Phase 4) Execute
- 実施内容: 本Issueメモに対して、6Phase運用・依存切断・Self-Correction上限の契約文を追記。
- Mock対象（1ファイル固定）: `04_Documentation/e2e_testing.md`
- 依存切断: 他 `issue-doc-ops-05-*` への参照は情報参照に留め、実行依存を作らない。

### Phase 5) Verify
- 実行コマンド（docs-check）:
  - `rg -n "^## 2026-04-23 Stream G DOC-OPS-05 Draft contract alignment" 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
  - `git diff --check`
- 判定基準: 見出し追記が1件以上検出され、diff体裁エラーがないこと。

### Phase 6) Proceed
- Status: **Ready**
- Stop condition: Self-Correction 3回超過、または本文契約の競合検知時は **Hold** へ遷移して停止。
- Next: 次Issue（05-07）へ直列で進行（05-14は完了報告で終了）。


## 17) Stream G dedicated run (2026-04-24)

### Phase 1 Read（対象Issue再読）
- `Requirement meta I/F` と `Acceptance criteria` を再読し、`VerificationLevel=docs-check` / `DecisionStatus=Fixed` を確認。
- Scopeを再確認し、本Issueは `01_Plans/issues` メモ更新のみ（実装変更なし）に限定。

### Phase 2 ADR/CDC（必要時のみ）
- 判定: **追加ADR不要**。
- Context: DOC-OPS-05-06 は文書分類と公開境界の固定が主目的。
- Decision: 既存方針 **Improve external** を維持し、未確定事項を増やさない。
- Consequences: 後続作業は docs-only の参照更新/移設/公開改善に限定する。

### Phase 3 Plan（AC/DoD不足ドラフト提案）
- AC追補案:
  - AC-G1: `GoNoGoGate=Required` の判定条件（Audience / Goal / 公開境界 / 次アクション）を本文で追跡可能にする。
  - AC-G2: 検証は `必須メタ確認 → 参照整合 → 差分整合` の順で記録する。
- DoD追補案:
  - DoD-G1: Proceed判定を `Ready / Hold / Needs-decision` の三値で固定する。

### Phase 4 Execute（issue本文の計画固定のみ）
- 実施内容: 本Issueメモ内でPhase 1〜6の運用記録を固定（計画以外の変更なし）。
- 非実施: 実装コード、`04_Documentation/*` 本文、他Issueメモの編集。

### Phase 5 Verify（docs-check, self-correction<=3）
- 実行記録:
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
  - `git diff --check`
- 自己修復ルール: 検証失敗時は当該Issueのみ最大3回修復、4回目相当は停止して `Hold`。

### Phase 6 Proceed（次Issueへ）
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

### Phase 3 Plan（AC / DoD合意）
- AC: e2e_testing の配置判定（Move internal/Improve external）を計画として固定する。
- DoD: Read→ADR→Plan→Execute→Verify→Proceed の6Phase記録が残り、Proceed判定が `Ready / Hold / Needs-decision` の三値で示される。

### Phase 4 Execute
- 本Issueメモ内の計画情報（AC/DoD/Proceed条件）を更新対象に限定。
- Stream H専有ファイルおよび指定外ファイルへは非接触。

### Phase 5 Verify（自己修復は最大3回）
- 実施: `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
- 実施: `git diff --check`
- 失敗時は同一ファイル内で最大3回まで自己修復し、4回目相当は即停止して `Hold` 化する。

### Phase 6 Proceed
- 判定: **Ready**（本Issueの DecisionStatus=Fixed かつ docs-check 範囲で完結）。
- Fail-safe: 指定外ファイル変更・前提崩れ・競合検知時は即停止し、Issueを `Hold` に切替える。

## 17) Stream G serial run record（2026-04-25）

### Phase 1 Read
- 再確認: `Status=Draft` / `Priority=P2` / `Scope=04_Documentation/e2e_testing.md` / `RequirementID=DOC-OPS-05-06` / `VerificationLevel=docs-check`。
- Requirement meta I/F の必須キー欠落がないことを確認。

### Phase 2 Plan
- 文書分類判定: **Improve external** を維持。
- AC草案固定: 対外改善計画（Audience/Goal/Public boundary/改善節）を固定し、本文全面改稿や実装変更を伴わない。
- DoD草案固定: 公開改善の次アクションと検証手順が本文に固定され、検証がdocs-checkで再実行可能。

### Phase 3 ADR/CDC
- 方針衝突判定: **衝突なし**（既存Issue内のContext/Decision/Consequencesで充足）。
- 追加ADR: **不要**。

### Phase 4 Execute
- 実施内容: issue本文の計画固定のみ更新（分類・AC/DoD・検証・Proceed）。
- 非実施: 対象文書本文の全面改稿、`03_Implement/**`、共有統合ファイルの変更。

### Phase 5 Verify
- docs-check: `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- diff check: `git diff --check`
- 修復上限: 不整合が出た場合は最大3回まで修復し、超過時は停止。

### Phase 6 Proceed
- 判定（Go / Conditional / No-Go）: **Go**
- 根拠: DecisionStatus=Fixed かつ docs-check 前提の計画固定が完了。


## 2026-04-26 Execution contract update（Interface-first / Mock-first）

### Interface-first + Mock検証可能性（各Issueで先行評価）
- Interface-first判定: 文書改訂前に `Audience / Goal / Non-goal / Public boundary / Outcome / Related` のI/Fキーを固定し、本文更新はこのI/Fに従属させる。
- Mock検証可能性判定: 実環境依存の検証を要求しない `docs-check` を基準とし、`rg` と `git diff --check` の再実行で再現できることをGo条件にする。
- No-Go条件: I/Fキー欠落、またはMock検証手順が再現不能な場合はExecuteへ進まない。

### 強制フェーズ（Plan → Execute → Verify → Proceed）
1. **Plan**: AC/DoDと検証コマンドを先に固定する。
2. **Execute**: Planで合意した差分のみ適用する（docs-only / 指定ファイル限定）。
3. **Verify**: `Expected verification level=docs-check` と整合するコマンドで確認する。
4. **Proceed**: `Ready / Hold / Needs-decision` を明示して次工程可否を記録する。

### AC/DoD不足時の運用（AIドラフト先行）
- AC/DoDに不足がある場合、AIが不足項目ドラフト（AC-Delta / DoD-Delta）を先に提示する。
- 合意取得前はExecute禁止。合意後のみExecuteへ遷移する。
- 合意記録は本Issue本文のPhaseログに残し、外部ファイルへ分散させない。

### 修復上限と停止条件
- 自己修復（Verify失敗時の修正）は最大3回。
- **4回目相当は停止**し、状態を `Hold` に更新する。
- **致命競合（fatal conflict）** を検知した場合は即時停止し、競合解消条件が明確になるまで `Proceed=Hold` を維持する。


## Stream J serial completion record（2026-04-26 / DOC-OPS-05-06）

### Phase 1 Read
- 対象Issue本文と `04_Documentation/e2e_testing.md` を再読し、分類（Improve external）と E2E方針正本としての位置づけを確認。

### Phase 2 ADR/CDC
- Context: E2E手順文書は公開runbookとして維持しつつ、内部進行メモや実測ログとの混在を回避する必要がある。
- Decision: Classification **Improve external** を維持し、`ADR-0019` の方針（Compose/runbook基準）との整合を優先する。
- Consequences: 本Issueの後続更新は「手順正本の明瞭化」に限定し、実測ログ詳細は `e2e_verification_log_2026-03-03.md` へ分離する。

### Phase 3 Plan
- AC補完: ①Audience/Goal/Public boundary の再確認 ②`ADR-0019` 参照の維持 ③実行不能時記録ルールの明示。
- DoD補完: docs-check により語彙/導線/体裁整合を確認し、6Phase記録を残す。

### Phase 4 Execute
- 本Issueへ Stream J の6Phase記録を追記し、分類・検証レベル・GoNoGoGate 定義を維持した。

### Phase 5 Verify
- `rg -n "Stream J serial completion record|ADR-0019|Improve external|VerificationLevel" 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
- `git diff --check`
- 修復回数: 0/3

### Phase 6 Proceed
- 判定: **Ready**
- 停止条件確認: 自己修復上限超過なし、依存仕様不整合なし、許可外ファイル編集なし。

## Stream J phase-sync serial update（2026-04-26 / DOC-OPS-05-06）

### Phase 1 Read sync
- 再読同期: `04_Documentation/e2e_testing.md` / `ADR-0019` / 本Issueの Requirement meta I/F を同一フェーズで再確認。
- 依存扱い: 他ストリーム成果は参照のみとし、待機依存は設定しない。

### Phase 2 Plan sync
- 直列実行順: 05-06 → 05-07 → 05-08 を固定。
- AC同期: Classification=Improve external、VerificationLevel=docs-check、GoNoGoGate=Required を維持。

### Phase 3 Execute sync
- 実施: 本Issueにフェーズ同期記録を追記（docs-only / allowlist内）。
- 非実施: 実装コード変更、指定外Issue更新。

### Phase 4 Verify sync
- `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
- `git diff --check`
- 自己修復: 失敗時は最大3回、4回目相当は停止。

### Phase 5 Proceed sync
- 判定: **Ready**
- 停止条件: 自己修復上限超過 / Requirement meta矛盾 / allowlist外変更要求。

## Stream L serial cycle (2026-04-26 / DOC-OPS-05-06)

### Read
- Requirement meta と `ADR-0019` 参照を再確認し、分類 `Improve external` を維持。

### Plan
- AC/DoD補完方針: E2E runbook と verification log の役割境界を継続固定。
- ADR: 運用境界差分は新規発生なしのため追加ADRは不要。

### Execute
- 本Issueメモへ Stream L 直列ログを追記（docs-only / allowlist内）。

### Verify
- `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
- `git diff --check`
- self-repair: 0/3（上限3回、4回目相当は停止）。

### Proceed
- 判定: **Ready**。
- 次工程: 05-07 へ直列進行。


## 18) Stream G serial execution record (2026-04-27)

### Phase 1: Read（対象Issue再読）
- 再読対象: `04_Documentation/e2e_testing.md` を含む本Issue全文（meta I/F / AC / Validation / Proceed）を再読。
- 確認結果: Classification=`Improve external`、VerificationLevel=`docs-check`、DecisionStatus=`Fixed` を再確認。

### Phase 2: Plan（AC/DoD不足のドラフト提案）
- AC/DoD不足ドラフト提案（実行前に固定）:
  - AC-G-1: Phase 1〜5 を **同一Issue内で直列** 記録し、各Phase開始時に再読した事実を残す。
  - AC-G-2: Verify は `docs-check`（メタ整合・差分整合）を必須化し、失敗時の修復回数を明記する。
  - DoD-G-1: Proceed で `Ready / Hold / Needs-decision` のいずれかを明示し、理由を1行で残す。

### Phase 3: Execute
- 実行内容: 本Issueへ Stream G の5Phase直列運用ログを追記。
- 分類方針: `Improve external` を変更せず維持。
- 次アクション: E2E runbook の前提/実行/確認/制約の公開向け整理案を維持。

### Phase 4: Verify
- 実行コマンド（Attempt 1/3）:
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
  - `git diff --check`
- 結果: Attempt 1 で完了（追加修復 0回）。

### Phase 5: Proceed
- 判定: **Ready**
- 理由: 5Phase直列記録、AC/DoDドラフト提案、docs-check実施計画、修復上限（最大3回）の4点を本Issue内で充足。

## Stream K gate-prep run（2026-04-27）

### Phase 1 Read（Draft gate条件の明示）
- 本Issueを最新状態で再読し、`Status=Draft` / `Priority=P2` / `Related Backlog=DOC-OPS-05` / `Expected verification level=docs-check` を確認。
- Draft gate条件を次の4点に固定: (1) 必須メタ（Status/Priority/Related/Validation）欠落なし、(2) Classificationが明示済み、(3) Proceed判定が `Ready/Hold/Needs-decision` で記録可能、(4) docs-only範囲を逸脱しない。

### Phase 2 ADR確認（CDC起票・承認前確定禁止）
- Context: DOC-OPS-05 Draft群は公開境界の分類判定を安全にOpen化するための事前整備。
- Decision: 本Issueの分類方針 `Improve external` を維持し、新規の制度変更は追加しない。
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
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
  - `rg -n "^\- Status:|^\- Priority:|Related Backlog|Expected verification level|VerificationLevel" 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
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
- Open化時の次アクション: `04_Documentation/e2e_testing.md` の公開runbook化（Audience/Goal/前提/手順/判定）をOpen化候補として分離。


## Stream G dedicated 6-phase run（2026-04-27, DOC-OPS-05-06）

### Phase 1 Read
- Read同期: 本Issue本文を再読し、`Status` / `Scope` / `Priority` / `Expected verification level` を確認。
- 差分確認: 前回記録との差分は **なし**（`Status=Draft`, `Priority=P2`, `VerificationLevel=docs-check` を維持）。

### Phase 2 ADR/CDC
- Read同期: `Related ADR/Spec` と `ADR handling rule` を再読。
- Context: DOC-OPS-05 Draft整備は公開境界の安全な固定が目的で、未承認事項の確定化を禁止する。
- Decision: 分類 `Improve external` を維持し、新規仕様差分は起票しない（差分発生時のみ C/D/C を追記）。
- Consequences: docs-only の分類整備を継続し、仕様正本（00〜02）の改変を回避する。

### Phase 3 Plan
- Read同期: `Requirement meta I/F` / `Acceptance criteria` / `Stop conditions` を再読。
- 実行計画:
  1. 本Issueに6Phase直列記録を追記（allowlist内のみ）。
  2. AC/DoD不足はドラフト提案として本文に残す。
  3. Verify失敗時は自己修復を最大3回、4回目相当は停止（Hold）。

### Phase 4 Execute
- Read同期: `Scope` / `Proposed solution` / `Non-goal` を再読。
- 実施: 本セクションを追加して6Phase手順を明文化。
- 実施後方針: `04_Documentation/e2e_testing.md` は公開runbook責務を維持し、Audience/Goal/前提/手順/判定の導線改善を継続。

### Phase 5 Verify
- Read同期: `Validation plan` と `Execution protocol` を再読。
- 実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md`
  - `git diff --check`
- 結果記録: self-repair `0/3`（4回目相当は停止条件により禁止）。

### Phase 6 Proceed
- Read同期: `GoNoGoGate` / `DecisionStatus` / `DecisionQueueRef` を再読。
- 判定: **Ready**（理由: 6Phase直列記録・ADR/CDC条件・docs-check導線・停止条件が再現可能）。

## 18) Operator directive lock (2026-04-27)

- 担当範囲: **`01_Plans/issues/issue-doc-ops-05-06-04doc-e2e-testing.md` のみ**（docs-only、実装変更禁止）。
- 進行フェーズ: **Read → Plan → Execute → Verify → Proceed** を固定順で実施する。
- 公開境界/分類方針: 本Issueでは **Improve external（対外文書として改善）** を固定し、Move internal への再判定は行わない。
- Public boundary 固定値:
  - Audience: 開発者・メンテナ（E2Eを実行/保守する実務担当）
  - Goal: 実行可能なE2E runbookを公開文書として維持する
  - Non-goal: 内部進行メモ/個別環境依存の暫定ノウハウを公開正本に混在させること
  - Outcome: `04_Documentation/e2e_testing.md` の公開品質を上げる後続docs-only PRへ接続する
- ADR取り扱い:
  - 追加ADRが必要になった場合は **C/D/C（Context / Decision / Consequences）を明文化** する。
  - ただし本Issue単体では **承認待ち（Approval pending）** として扱い、承認前に仕様固定を拡張しない。
- Verifyフェイルセーフ:
  - 自己修復は **最大3回**。
  - 3回を超える修復が必要な場合は **停止（Hold）** し、超過理由と再開条件を本Issueへ記録する。
