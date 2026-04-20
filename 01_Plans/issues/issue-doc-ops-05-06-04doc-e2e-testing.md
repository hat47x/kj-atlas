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
