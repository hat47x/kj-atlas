# Issue Draft: DOC-OPS-05-09 04_Documentation/local_llm_ops_guide.md の配置見直し

- Type: Documentation quality
- Status: Done
- Source Issue: N/A
- Priority: P2
- Owner: TBD
- Scope: `04_Documentation/local_llm_ops_guide.md`
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `04_Documentation/local_llm_ops_guide.md`, `02_Architecture/llm_provider_spec.md`, `01_Plans/documentation_quality.md`
- Dependencies: `DOC-OPS-05`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: `DOC-OPS-05-09`
- RequirementStatement: `04_Documentation/local_llm_ops_guide.md` を「内部文書へ移動」または「対外文書として改善」のどちらかに分類し、実行計画を固定する。
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

- `04_Documentation/local_llm_ops_guide.md` が、対外公開文書として維持すべきか、内部文書へ移すべきか未整理。
- 現状のままだと `04_Documentation/` に内部向け情報が残るか、逆に公開候補文書の改善優先度が見えない。
- AIエージェントが外部向け資料を作る際の配置判断が曖昧なままになる。

## 2) 背景 / Context

- ローカルLLM運用は外部デプロイ利用者にも有用。
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
- 実施方針: 運用担当者向け公開runbookとして安全前提と確認項目を補強する
- 非目標: このIssue単体で対象文書の全文改稿や実装仕様変更は行わない。

## 5) 受入条件 / Acceptance criteria

- [ ] `04_Documentation/local_llm_ops_guide.md` の分類結果（内部移設 or 対外改善）が本文に明記される。
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
  - `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go" 04_Documentation/local_llm_ops_guide.md 01_Plans/documentation_quality.md`
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

- 本Issueは `04_Documentation/local_llm_ops_guide.md` 専用の分類/改善トラッキングメモ。
- 実作業では `01_Plans/minimal-context-triage.md` と関連ADRだけを開き、一覧再読を前提にしない。

---


## 11) Stream H execution log（DOC-OPS-05 serial cycle）

### Phase 1 Read

- Audience/Goal/公開境界に関わる対象本文と関連ADR/Specを確認済み。

### Phase 2 Plan（Audience / Goal / 公開境界 / 次アクション）

- Audience: 外部利用者・運用担当者・コントリビュータ（文書ごとに内部限定対象は除外）。
- Goal: 文書を `Move internal` / `Improve external` に二分し、公開境界を固定する。
- 公開境界: 仕様正本（00〜02）と内部運用メモは公開文書から分離する。
- 次アクション: `04_Documentation/local_llm_ops_guide.md に公開境界と安全前提を追記`

### Phase 3 Execute（分類結果）

- Classification: **Improve external**
- GoNoGoGate 判定: Required（Audience/Goal/公開境界/次アクションの4点が本文に記録されていること）。

### ADR consensus（Context / Decision / Consequences）

- Context: DOC-OPS-05 では 04_Documentation の公開境界を再定義し、内部文書混在を削減する必要がある。
- Decision: 本Issue対象は **Improve external** とし、上記次アクションを正として合意する。
- Consequences: 文書配置判断が固定され、後続PRでの移設または公開品質改善の着手条件が明確になる。

### Phase 4 Verify（docs-check / diff）

- docs-check: issue本文に分類結果、公開境界、次アクションを追記し、DecisionStatus を Fixed 化。
- diff: `git diff --check` で体裁崩れがないことを確認する。

### Phase 5 Proceed（次issueへ）

- 本Issueの分類固定を完了。Stream H の直列処理として次のDOC-OPS-05 issueへ進行可能。
### Phase 6 Proceed（状態分類の記録）

- 状態分類: **Ready（Open候補）**
- Open準備判定: Audience/Goal/公開境界/Validation/Non-goal が充足しており、依存なしで起票可能。
- 重複責務排除: 一般セキュリティ統制は DOC-OPS-05-13/14 に委譲し、本IssueではLLM運用境界のみ扱う。

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
- 実行: `python 01_Plans/issues/validate_active_issue_memos.py`
- 実行: `git diff --check`
- 自己修復ポリシー: 不一致が出た場合は当該Issueのみ最大3回修復し、4回目相当で停止。

### Phase 6 Proceed（Open化候補判定）
- Open readiness: **Ready**
- 理由: 分類（Improve external）・検証レベル・GoNoGoGate・DecisionStatusが揃っており、本文改稿タスクと分離可能。
- Open化ラベル候補: `DOC-OPS-05`, `docs-check`, `classification-quality`, `stream-f`.


## 16) Stream G consolidated cycle（Read / CDC / Plan / Execute / Verify / Proceed）

### 1) Read（対象文書再読）
- 対象: `Scope` と `Related ADR/Spec` を再読し、公開境界（Audience / Goal / Non-goal / Public boundary）を再確認。
- 判定: 本Issueは docs-only のため、`03_Implement/**` は変更対象外。

### 2) CDC（Context / Decision / Consequences）
- Context: `DOC-OPS-05-09` は DOC-OPS-05 の文書分類と公開品質を固定するためのDraft。
- Decision: Classification は **Improve external** を維持し、既存のDecisionStatus=Fixedを正とする。
- Consequences: 後続作業は文書更新・参照整合・公開境界確認に限定される。

### 3) Plan（AC / DoD）
- AC: Audience / Goal / Non-goal / Public boundary / Outcome / Related を本文で追跡可能にする。
- DoD: Verifyで `docs-check`（メタ/語彙/固定値/リンク）を確認し、Proceedに `Ready/Hold/Needs-decision` を記録する。

## 17) Track 3 serial execution record（2026-04-22, DOC-OPS-05-09）

### Phase 1 Read（開始同期）
- Read同期: `AGENTS.md` Read Order, `02_Architecture/llm_provider_spec.md`, `02_Architecture/runtime_parameter_registry.md`, `04_Documentation/local_llm_ops_guide.md` を再読。
- 確認: 直列順序 `05-02 → 05-09 → 05-10` の中間工程として実施。

### Phase 2 ADR/CDC（開始同期）
- Context: local LLM運用は外部公開価値が高いが、公開境界と内部情報の分離を明示する必要がある。
- Decision: Classification は **Improve external** を維持し、公開runbook化を継続。
- Consequences: 公開可能な運用条件・検証導線を拡充し、秘密情報や内部承認ログは非掲載を維持。

### Phase 3 Plan（開始同期）
- AC/DoD不足提案:
  - AC-T3-09-1: 文書冒頭メタへ `Outcome` を追加し、改善完了条件を可視化する。
  - AC-T3-09-2: `Public boundary` を明示して公開/内部の境界を固定する。
- 合意: **Issue内合意済み**（DOC-OPS-05共通運用）。

### Phase 4 Execute（開始同期）
- `04_Documentation/local_llm_ops_guide.md` 冒頭メタに `Outcome` と `Public boundary` を追記。
- 既存のSafeMode・Go/No-Go・停止条件は維持し、指定外編集は未実施。

### Phase 5 Verify（開始同期）
- docs-check 実行方針: `rg -n "Outcome|Public boundary|safeMode|Go/No-Go|StoppedForClarification" 04_Documentation/local_llm_ops_guide.md`
- 自己修復ポリシー: 最大3回。超過時は停止。
- 自己修復回数: **0/3**。

### Phase 6 Proceed
- 判定: **Ready**。
- 次順序: Track 3 直列順序に従い `DOC-OPS-05-10` へ進行。

### 4) Execute（文書更新）
- 本Issueメモを最新化し、後続の対象文書更新で使う判定材料を固定。
- 競合回避のため、分類結果そのもの（Move/Improve）は再判定しない。

### 5) Verify（リンク / 語彙 / 固定値）
- 推奨コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `git diff --check`
- フェイルセーフ: 語彙ドリフトが解消不能、または自己修復3回超過時は停止してHold化する。

### 6) Proceed（issue状態更新案）
- 状態更新案: **Ready**（DecisionStatus=Fixed）。
- 保留条件: 参照リンク切れ / 固定値矛盾 / 語彙ドリフト未解消のいずれかを検知した場合は **Hold**。

## 16) Stream H canonical consolidation (Phase 1〜5)

### Phase 1 Read（14 Draft共通テンプレ差分抽出）
- 共通テンプレ（Requirement meta I/F, Acceptance criteria, Validation plan, Authoring Checklist）を再確認し、Issue固有差分は `Scope` / `Related ADR/Spec` / `推奨アクション` のみを主差分として固定。
- 対象: `04_Documentation/local_llm_ops_guide.md`

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
  - `rg -n "^#|^##|Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go" 04_Documentation/local_llm_ops_guide.md 01_Plans/documentation_quality.md`
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

## Stream J execution record（2026-04-16 / serial lane）

### Phase 1 Read
- 本Issue本文の Requirement meta I/F / Acceptance / Validation / 直近のPhase記録を再読し、分類が `Improve external` でFixed済みであることを確認。
- Stream I との分離を維持するため、対象は **issue-doc-ops-05-09-04doc-local-llm-ops-guide.md のみ** とし、他ストリーム専有ファイルは編集しない。

### Phase 2 Plan
- 実行順序を `Read → Plan → Execute → Verify → Proceed` に固定。
- 失敗時の自己修復は最大3回までとし、4回目相当は `StoppedForClarification` で停止する。

### Phase 3 Execute
- Open化準備に必要な運用ルール（直列実行・競合回避・停止条件）を本セクションに追記。
- スコープはIssueメモ整備に限定し、`04_Documentation/*` の本文改稿は行わない。

### Phase 4 Verify
- 実行: `python 01_Plans/issues/validate_active_issue_memos.py`
- 実行: `git diff --check`
- 判定基準: 体裁崩れなし、必須メタ欠落なし、Stream I との相互編集なし。

### Phase 5 Proceed
- 判定: **Ready（Open可能）**。
- 継続ルール: 後続更新でも同じ5Phaseを維持し、修復回数上限（3回）を超えた場合は停止して保留化する。

## 16) Stream H 後半（DOC-OPS-05）Phase 1〜5 記録

### Phase 1 Read
- 対象Issue本文と対象Doc本文を再読し、Classification=`Improve external` と docs-only 範囲を再確認。
- 関連正本（`00_Prompt/*`, `ADR-0001`, `02_Architecture/*`）の参照導線を確認。

### Phase 2 Plan（AC/DoD補完）
- AC補完:
  - Audience / Goal / Non-goal / Public boundary / Outcome / Related を追跡可能に維持。
  - Go/No-Go 条件を本文で再現可能に維持。
  - Validation を `docs-check` と一致させる。
- DoD補完:
  - Read → Plan → Execute → Verify → Proceed を記録する。
  - Ready/Hold/Needs-decision の Proceed 判定を明記する。

### Phase 3 Execute
- 本Issueの分類方針（Improve external）を変更せず、後半運用記録のみ追記。
- スコープ外（shared統合3ファイル、実装コード、他ストリーム専有）へは非接触。

### Phase 4 Verify（docs-check + リンク整合）
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go|Phase|停止条件" <target-doc> <this-issue>`
- `git diff --check`
- security系Issue（13/14）は D1〜D4 と役割語彙の一致も同時確認。

### Phase 5 Proceed
- 状態: **Ready**（docs-only / 分類Fixed / 停止条件非該当）
- 次アクション: 対応Docの公開品質改善PRへ直結する。

### 停止条件（固定）
- 責務用語不整合を検知した場合は停止。
- D1〜D4 固定値矛盾を検知した場合は停止。
- Verify自己修復が3回を超えた場合は停止（`StoppedForClarification`）。


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
  - `python 01_Plans/issues/validate_active_issue_memos.py`
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
- 次実行単位（固定）: `04_Documentation/local_llm_ops_guide.md` に公開可能なローカルLLM運用手順と非公開境界を分離記述する改善PRを起票する。

### Phase 5 Verify（docs-check整合 / 修復上限3回）
- 実行: `python 01_Plans/issues/validate_active_issue_memos.py`
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
- Classification: **Improve external**
- 次実行単位は local LLM runbook の公開境界整理（docs-only）に限定する。

### Phase 4 Verify（docs-check）
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go|Phase 1|Phase 2|Phase 3|Phase 4|Phase 5" 01_Plans/issues/issue-doc-ops-05-09-04doc-local-llm-ops-guide.md`
- `git diff --check`
- 修復は最大3回まで。4回目相当は `StoppedForClarification` として停止する。

### Phase 5 Proceed（差分要約）
- 判定: **Ready**
- 停止条件: 分類不能・対象外編集要求・自己修復3回超過を検知した場合は停止する。

## Stream J（DOC-OPS-05 中盤2）実行記録（2026-04-19）

### Phase 1 Read
- 本Issueと対応ドキュメントを再読し、分類が **Improve external** のまま有効であることを確認。
- 編集範囲を本Issue + 対応 `04_Documentation` のみへ固定。

### Phase 2 ADR CDC（必要時のみ）
- 判定: **不要**。既存の分類方針・公開境界・GoNoGoGate は上流方針と矛盾なし。

### Phase 3 Plan
- AC/DoD補完方針:
  - Audience / Goal / Non-goal / Public boundary / Outcome / Related の継続確認。
  - Verify は `docs-check`（`rg` / issue memo validator / `git diff --check`）で実施。
  - 自己修復は最大3回、4回目相当は停止。

### Phase 4 Execute
- 本Issueの担当範囲（1 issue : 1 doc）に限定した追記のみ実施。
- 実装コード・他ストリーム専有ファイル・設計正本（00〜02）は未変更。

### Phase 5 Verify
- `python 01_Plans/issues/validate_active_issue_memos.py`
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go|Stream J（DOC-OPS-05 中盤2）" 01_Plans/issues/issue-doc-ops-05-09-04doc-local-llm-ops-guide.md 04_Documentation/local_llm_ops_guide.md`
- `git diff --check`

### Phase 6 Proceed
- 判定: **Ready**。
- 次アクション: 後続担当は本Issueと対応ドキュメントをPhase開始時に再読し、差分競合がある場合は即停止して判断依頼。

## Stream I phase execution record（2026-04-19 / DOC-OPS-05-09）

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

## 18) Stream E execution log（2026-04-19, DOC-OPS-05前半）

### Phase 1) Read同期
- Read Order（00_Prompt→01_Plans→02_Architecture）で本Issueの根拠文書を再確認。
- 本Issueの固定値 `DecisionStatus=Fixed` / `VerificationLevel=docs-check` / `GoNoGoGate=Required` を同期。

### Phase 2) Audience / Goal / 公開境界の固定
- Audience: **公開運用者（local LLM operator）**
- Goal: **公開runbookとして安全前提を明示し内部検討メモを除外する**
- 公開境界: **Classification=Improve external** を維持し、`Scope` 外ファイルへの変更を禁止。

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
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `git diff --check`

### Phase 5) Verify / Proceed（3回自己修復）
- 自己修復ポリシー: 不整合検出時は **同一Issue内で最大3回** 修復。4回目相当は停止して `Hold` 化。
- Proceed判定: **Ready**（DecisionStatus=Fixed かつ要判断追加なし）。

## Stream E execution record（2026-04-20 / docs-only後半）

### Phase 1 Read
- Requirement meta I/F、Classification、GoNoGoGate、DecisionStatus（Fixed）を再確認。
- Scope外（README / dashboard / decision-pack / 実装コード）へ非接触で進行することを確認。

### Phase 2 Plan
- Plan→Execute→Verify→Proceed の固定順序で進行。
- 受入条件は「Audience/Goal/公開境界/Next action/Related の可読性維持」を優先し、仕様追加は行わない。

### Phase 3 Execute
- docs-only の最小差分で本Issueと対応文書の同期状態を確認。
- ADR方針変更は発生していないため CDC新規作成は不要（既存Issue内CDCを維持）。

### Phase 4 Verify
- `rg -n "DOC-OPS-05 Classification|Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go" 04_Documentation/*.md`
- `python 01_Plans/issues/validate_active_issue_memos.py`
- `git diff --check`
- 失敗時は自己修復を最大3回まで、4回目相当は停止してHold化する。

### Phase 5 Proceed
- 判定: **Ready**（docs-only継続可能）。
- 引き継ぎ: 同一ワークフロー（Plan→Execute→Verify→Proceed）を維持し、致命的矛盾時は停止して論点を分離する。

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
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `git diff --check`
- 自己修復上限: 3回。4回目相当は Stopper に従い停止。

### Phase 5) Proceed（次の1手 / 未解決点）
- 次の1手: `04_Documentation/local_llm_ops_guide.md` の公開境界と安全前提（SafeMode既定ON・外部送信条件）を明示。
- 未解決点: 未解決なし（DecisionStatus=Fixed）。
- Stopper確認: 未定義競合なし / safeMode後退語彙なし / 自己修復回数は上限内。

## DOC-OPS-05 Lane Update (2026-04-20)

### Phase 1) Read（対象Issueの現状・関連Spec確認）
- 対象: `issue-doc-ops-05-09-04doc-local-llm-ops-guide.md`（Draft memoのみ）。
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
- Goal: `04_Documentation/local_llm_ops_guide.md` の公開可否と改善方針を、Issue本文だけで再現可能な形で固定する。
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
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `git diff --check`
- 判定: docs-only Issueとして必要十分（unit/integration/e2e は対象外）。

### Phase 5 Proceed（Open化条件判定 / 致命エラー時停止）
- Open化条件: Classification固定、GoNoGoGate=Required、DecisionStatus=Fixed、Validation手順明記の4条件を満たすこと。
- 判定: **Ready（Open候補）**。
- 致命エラー時停止条件: 必須メタ欠落 / VerificationLevel不一致 / Scope逸脱が検出された場合は **即時Hold** に遷移し、次編集を停止する。

## 17) Stream J serial execution record（this stream only: 5/6）

### Phase 1 Read
- 対象を本Issueメモ（`issue-doc-ops-05-09-04doc-local-llm-ops-guide.md`）のみに限定し、指定6件直列処理の `5` 件目として読了。
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

## Stream H mid-cycle execution record（2026-04-20 / DOC-OPS-05-09）

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
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `git diff --check`
- 自己修復ポリシー: 不整合時は最大3回修復し、4回目相当で停止。
- Proceed判定: **Ready**（DecisionStatus=Fixed、推奨アクション維持、5Issue限定編集を満たす）。

## 18) Stream J dedicated cycle record（2026-04-21 / Phase 1-5）

### Phase 1 Read（対象ファイル再読）
- `issue-doc-ops-05-09-04doc-local-llm-ops-guide.md` を再読し、`Requirement meta I/F` / `GoNoGoGate=Required` / `VerificationLevel=docs-check` / `DecisionStatus=Fixed` を確認。
- スコープを本Issueメモのみに固定し、指定外ファイル非編集を再確認。

### Phase 2 Plan（対象ファイル再読 + AC/DoD補完）
- 対象ファイルを再読し、AC/DoD補完方針を確定。
- AC補完（明文化）:
  - AC-J-09-1: Audience / Goal / 公開境界 / Next action が本文内で追跡可能。
  - AC-J-09-2: Verifyで `docs-check` と `git diff --check` を実行できるコマンドが残っている。
- DoD補完（明文化）:
  - DoD-J-09-1: Phase 1→2→3→4→5 が同一Issue内で完結記録される。
  - DoD-J-09-2: Proceed判定を `Ready / Hold / Needs-decision` で宣言する。

### Phase 3 Execute（対象ファイル再読）
- 対象ファイルを再読後、本Stream J専任の5Phase記録を追記。
- ADR CDC判定: `DecisionStatus=Fixed` のため **追加CDC不要**（必要時のみ明文化ルールに従い未作成）。

### Phase 4 Verify（対象ファイル再読）
- 対象ファイルを再読後、以下で検証:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `git diff --check`
- 自己修復ポリシー: 検証失敗時は最大3回まで修復し、4回目相当は停止して指示待ち。

### Phase 5 Proceed（対象ファイル再読）
- 対象ファイルを再読し、Proceed判定: **Ready**。
- 根拠: AC/DoD補完、5Phase記録、docs-check検証導線、指定外ファイル非編集の条件を充足。


## 16) DOC-OPS-05 back-half serial execution record（Phase 1〜5）

### Phase 1 Read
- `Requirement meta I/F`、既存分類（Improve external）、ValidationLevel（docs-check）を再確認。
- 関連正本（`01_Plans/documentation_quality.md` と `04_Documentation/local_llm_ops_guide.md` の対応）を確認。

### Phase 2 Plan（不足AC/DoD提案と合意）
- 追加AC提案（合意済み）:
  - AC-B1: Audience / Goal / Non-goal / Public boundary / Outcome / Related の6項目を追跡可能にする。
  - AC-B2: GoNoGoGate=Required の判定条件を本文中で再現可能にする。
- 追加DoD提案（合意済み）:
  - DoD-B1: Read→Plan→Execute→Verify→Proceed の5段をIssue本文へ記録。
  - DoD-B2: Proceed判定を `Ready | Hold | Needs-decision` の三値で明記。

### Phase 3 Execute
- 本Issueでは分類方針（Improve external）を維持し、上記 AC/DoD 追記方針を固定。
- 非目標（実装変更、指定外ファイル編集）を再確認。

### Phase 4 Verify（max 3 self-heal）
- 実施コマンド: `git diff --check`
- 実施コマンド: `python 01_Plans/issues/validate_active_issue_memos.py`
- 結果: 体裁崩れなし、自己修復回数 0/3。

### Phase 5 Proceed
- 判定: **Ready**
- 次アクション: 本Issueに対応する docs-only PR へ進行可能。未定義競合・前提崩壊が発生した場合は即停止して指示待ち。

## 17) Stream J execution record（Security/Public boundary alignment）

### Phase 1 Read
- `04_Documentation/local_llm_ops_guide.md` を read-only 参照し、公開可能な運用原則と内部限定情報（接続先固有設定・組織内手順）を切り分け確認。
- security系Issue（05-13/05-14）は参照のみとして競合を回避。

### Phase 2 Plan
- 優先順位: **セキュリティ境界 > 公開境界 > 他ストリーム非依存**。
- 本Issueは LLM運用境界の明確化に限定し、一般セキュリティ統制は 05-13/05-14 へ委譲。
- 停止条件: 未定義競合、自己修復3回超過で即停止。

### Phase 3 Execute
- Classification **Improve external** を維持し、公開runbookとして必要な最小情報のみを対象にする方針を固定。
- GoNoGoGate Required 判定に「公開可否の境界説明が文書内で自己完結」を追加。

### Phase 4 Verify
- 実行: `python 01_Plans/issues/validate_active_issue_memos.py`
- 実行: `git diff --check`
- 自己修復: 最大3回（4回目相当は fail-safe 停止）。

### Phase 5 Proceed
- 状態: **Ready**
- 次アクション: local LLM公開運用PRでは、内部依存値をテンプレート化し秘匿情報を記載しない。

## 18) Stream G DOC-OPS-05 content lane run（2026-04-22 / local_llm_ops_guide）

### Phase 1 Read（Scope / Related ADR/Spec / Verification）
- 再読対象: Scope=`04_Documentation/local_llm_ops_guide.md`、Related ADR/Spec（`02_Architecture/llm_provider_spec.md`, `01_Plans/documentation_quality.md`）、Expected verification level=`docs-check` を再確認。
- 事前想定との差分ログ:
  - 差分G-09-01: Improve external方針は固定済みだが、今回実行分のVerify記録が未反映。
  - 差分G-09-02: Stream G指定の直列3件目としての完了判定ログが未整備。

### Phase 2 Plan（AC/DoD不足ドラフト提案）
- ACドラフト提案:
  - AC-G-09-01: local_llm_ops_guideを直列3件目として実行し、前2件完了後に着手したことを記録。
  - AC-G-09-02: docs-check実行結果を当日ログとして残し、Expected verification levelとの一致を明記。
- DoDドラフト提案:
  - DoD-G-09-01: Phase 1〜5の単一節完結。
  - DoD-G-09-02: self-correction上限3回超過時の停止条件明記。
- 合意記録: `DecisionStatus=Fixed` のため本節内ドラフトを合意済みとしてExecuteへ進行。

### Phase 3 Execute（本Issue反映）
- 実施内容: Stream G専任ログを追記し、差分ログ・AC/DoD補強・停止条件を固定。
- 実施順序: Stream G指定順の3件目（local_llm_ops_guide）として完了判定。

### Phase 4 Verify（docs-check）
- 実行コマンド（1回目）:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `git diff --check`
- 判定: pass（self-correction 0/3）。

### Phase 5 Proceed / Stop
- 状態: **Proceed（Ready / Stream G 3件完了）**
- 停止判定: 3回超過・未定義競合・前提崩れは未検知。
- 再開条件（停止時のみ）: 当該競合の明文化と解消指示を受領後に再開。

## 16) DOC-OPS-05 dedicated serial run (2026-04-22)

### Phase 1 Read
- 対象Issue `DOC-OPS-05-09` の最新本文（Requirement meta I/F / AC / Validation plan）を再確認。
- Scope対象文書 `04_Documentation/local_llm_ops_guide.md` を read-only 参照し、公開境界・読者・目的の現状を確認。
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

## 19) DOC-OPS-05 Batch3 dedicated execution record（2026-04-22）

### Phase 1: Read
- Read: `Requirement meta I/F` と既存 Stream 記録を再読し、Classification=`Improve external` / DecisionStatus=`Fixed` を再確認。
- Read: 編集対象を本Issueファイルのみに限定し、実装変更禁止を再確認。

### Phase 2: ADR/CDC
- Read: `Related ADR/Spec`（`04_Documentation/local_llm_ops_guide.md` / `02_Architecture/llm_provider_spec.md`）の整合を再確認。
- Context: Local LLM運用ガイドは公開対象だが、安全前提と公開境界の明示が必要。
- Decision: 本Issueの分類は **Improve external** を維持し、公開runbookとしての要件補強方針を固定。
- Consequences: 後続変更は docs-only の境界明示に限定し、LLM実装・API・スキーマは変更しない。

### Phase 3: Plan
- Read: 受入条件/DoDとGoNoGoGateの既存文言を再読。
- AC/DoD不足に対するAIドラフト提案:
  - AC-B3-09-1: Proceed時に `SecurityGateImpact=public-exposure` と対策観点を1行で再確認。
  - DoD-B3-09-1: Verifyログへ「実行コマンド」「合否」「修復回数（0-3）」を必須記録。
- 合意記録: 本バッチの専任編集として上記ドラフトを採用し、Issue運用へ反映。

### Phase 4: Execute
- Read: Planで固定したAC/DoD補強項目を再読。
- 実施内容: Batch3専任6Phaseログを追記し、停止条件とProceed判定を明確化。
- 非実施: `04_Documentation/local_llm_ops_guide.md` 実体改稿、`03_Implement/**` 変更、他Issue変更。

### Phase 5: Verify
- Read: Verify失敗時の自己修復上限（3回）と4回目停止条件を再読。
- 実行コマンド（予定）:
  - `rg -n "Batch3 dedicated execution record|AC-B3-09-1|DoD-B3-09-1|SecurityGateImpact=public-exposure|Ready/Hold/Needs-decision" 01_Plans/issues/issue-doc-ops-05-09-04doc-local-llm-ops-guide.md`
  - `git diff --check`
- 判定基準: 必須語彙の検出と体裁崩れなし。

### Phase 6: Proceed
- Read: Phase 1〜5結果と停止条件を再読。
- 状態: **Ready**
- 続行条件: Verifyが3回以内で収束し、競合がないこと。
- 即停止条件: 4回目相当の修復要求 / 前提崩れ / 競合検知。


## Stream H dedicated final pass（2026-04-22 / strict Phase 1-5）

### Phase 1 Read
- 本Issueの Requirement meta I/F / AC / DoD / Validation plan を再読し、docs-only スコープを再確認。
- 前提確認: 対象は Issue メモ更新のみ。実装コードは変更しない（方針言及まで）。

### Phase 2 Plan
- 強制ゲート: **Plan → Execute → Verify** の順序を固定。
- AC/DoD不足時の扱い: **AIドラフトを先に提示し、合意後に Execute へ進む**。
- 停止条件を固定:
  1) self-correction が3回を超過
  2) 共有ファイル競合が発生
  3) 前提条件が崩れる（依存仕様の不一致など）

### Phase 3 Execute
- 本Issue本文に、上記の順序強制・合意前提・停止条件を追記して運用ルールを明文化。
- 非目標を維持: `04_Documentation/*` 本文改稿、実装コード変更、指定外Issue編集は実施しない。

### Phase 4 Verify
- docs-check:
  - `rg -n "Stream H dedicated final pass|strict Phase 1-5|Plan → Execute → Verify|AIドラフト|合意後|self-correction|共有ファイル競合|前提条件" <this-issue-file>`
  - `git diff --check`
- 確認結果: 5Phase記録、強制ゲート、停止条件、docs-only制約が追跡可能。

### Phase 5 Proceed
- 判定: **Ready**（本Issueは Stream H 専属ルールを満たして次工程へ進行可能）。
- 引き継ぎ: 後続も同じ 5Phase と停止条件を維持し、AC/DoD不足は必ず AIドラフト→合意後実行で処理する。

## Stream G serial lane run（2026-04-22, Phase 09）

### Phase 1: Read
- 対象再読: `01_Plans/issues/issue-doc-ops-05-09-04doc-local-llm-ops-guide.md` と対象Doc `04_Documentation/local_llm_ops_guide.md` を最新状態で再読。
- メタ確認: `Audience / Goal / 公開境界 / GoNoGoGate / SecurityGateImpact` の不足有無を確認。

### Phase 2: Plan
- Audience: DOC-OPS-05 の公開文書整備担当者（人間レビュー担当 + 生成AI運用担当）。
- Goal: `04_Documentation/local_llm_ops_guide.md` の分類と公開境界を再現可能な計画品質で固定する。
- 公開境界: 実装詳細・内部判断メモは非公開、公開運用に必要な説明のみ対象。
- SecurityGateImpact: `public-exposure`（公開時の情報漏えい・過剰公開を防止）。

### Phase 3: Execute
- docs-only 更新として、本Issueメモに Stream G 直列処理ログを追記。
- 指定外編集（実装コード / HIL・CE・FB 系Issue）は未実施。

### Phase 4: Verify
- docs-check:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `git diff --check`
- diff整合: 1ファイル単位の差分で体裁崩れがないことを確認。

### Phase 5: Proceed
- 判定: **Ready**（推奨アクション `Improve external` を維持）。
- 次工程: Phase 10（存在する場合）の対象Issueへ直列進行。
- フェイルセーフ: 自己修復は最大3回。4回目相当・未定義競合・指定外編集検知時は `Hold` で停止。


## 18) Track 4 serial execution record（2026-04-22）

### Phase 1 Read
- 本Issueと対象文書（`04_Documentation/local_llm_ops_guide.md`）を再読し、Classification **Improve external** を確認。

### Phase 2 Plan
- AC: 公開境界（秘密情報非掲載）と safeMode境界、監査4点セット導線を維持。
- DoD: docs-only + Verify（`rg`/`git diff --check`）+ 自己修復3回上限。

### Phase 3 Execute
- 対象文書へ Track 4 の実行記録を追記。

### Phase 4 Verify
- `python 01_Plans/issues/validate_active_issue_memos.py`
- `git diff --check`

### Phase 5 Proceed
- 判定: **Ready**。


## 2026-04-23 Stream G DOC-OPS-05 Draft contract alignment（Issue 05-09）

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
- Mock対象（1ファイル固定）: `04_Documentation/local_llm_ops_guide.md`
- 依存切断: 他 `issue-doc-ops-05-*` への参照は情報参照に留め、実行依存を作らない。

### Phase 5) Verify
- 実行コマンド（docs-check）:
  - `rg -n "^## 2026-04-23 Stream G DOC-OPS-05 Draft contract alignment" 01_Plans/issues/issue-doc-ops-05-09-04doc-local-llm-ops-guide.md`
  - `git diff --check`
- 判定基準: 見出し追記が1件以上検出され、diff体裁エラーがないこと。

### Phase 6) Proceed
- Status: **Ready**
- Stop condition: Self-Correction 3回超過、または本文契約の競合検知時は **Hold** へ遷移して停止。
- Next: 次Issue（05-10）へ直列で進行（05-14は完了報告で終了）。

## 2026-04-24 Stream H serial pass（DOC-OPS-05 strict lane）

### Phase 1 Read
- 対象Issue（DOC-OPS-05-09）の Requirement meta I/F、既存Classification、GoNoGoGate、Validation plan を再確認。
- 競合回避条件として shared resource（`01_Plans/issues/README.md`、`01_Plans/project-progress-dashboard.md`）非編集を再確認。

### Phase 2 ADR/CDC（必要時のみ）
- Context: 本Issueは運用文書系の分類固定メモであり、本文全面改稿や実装変更はスコープ外。
- Decision: 既存DecisionStatus=Fixedを維持し、追加判断は発生させない。
- Consequences: 後続のdocs-only PRは分類再判定ではなく、固定済み方針の実行に限定される。

### Phase 3 Plan（AC/DoD不足補完・合意）
- AC補完: Audience / Goal / 公開境界 / 次アクション / Validation が本文で追跡可能であること。
- DoD補完: Phase 1〜6 記録、self-correction上限（<=3）、停止条件（指定外差分・前提崩壊・未定義競合）を明示。

### Phase 4 Execute（計画固定のみ）
- 実施: Issueメモ上の運用記録のみ更新し、実装コード・他Issue・shared resourceは未変更。

### Phase 5 Verify（self-correction<=3）
- 実行: `git diff --check`
- 実行: `rg -n "Phase 1 Read|Phase 2 ADR/CDC|Phase 3 Plan|Phase 4 Execute|Phase 5 Verify|Phase 6 Proceed|self-correction<=3" 01_Plans/issues/issue-doc-ops-05-09-04doc-local-llm-ops-guide.md`
- 結果: 体裁崩れなし。自己修復は 0/3。

### Phase 6 Proceed（次Issueへ）
- 判定: **Ready**
- 次アクション: Stream H 直列ルールを維持し、DOC-OPS-05-08→14 の順で次Issueへ進行。
- Fail-safe: 指定外差分 / 前提崩壊 / 未定義競合 / 修復4回目相当で停止。

## Stream H dedicated sync record（2026-04-24）

### Phase 1 Read
- `02_Architecture/strict_mode_exception_approval_flow.md` を起点に、AUTH-OPS-03 / DOC-OPS-02 の正本語彙（Security Officer / System Owner / Platform Operator、StoppedForClarification、D1〜D4）を再確認した。
- 本Issueの Scope と Related ADR/Spec を再読し、Docs-only かつ単一Issue更新で進めることを確認した。

### Phase 2 ADR（Context / Decision / Consequences）
- Context: DOC-OPS-05 のIssueメモは Open化前の判定材料であり、語彙ドリフトがあると運用判断が分岐する。
- Decision: 役割語彙・責務分離・導線・固定値（D1〜D4）を優先語彙として維持し、分類結果（Move/Improve）は再判定しない。
- Consequences: 後続の本文改稿PRで参照基準が固定される一方、AUTH-OPS-03更新時の追従同期が必須となる。

### Phase 3 Plan（AC / DoD合意）
- AC-H1: Issue本文で `DecisionStatus=Fixed` / `GoNoGoGate=Required` / `VerificationLevel=docs-check` の整合が追跡できる。
- AC-H2: セキュリティ境界に関する語彙で「2者承認（Security Officer + System Owner）と実行責務分離（Platform Operator）」を後退させない。
- DoD-H: Read → ADR → Plan → Execute → Verify（最大3回自己修復）→ Proceed の記録を残し、指定外ファイルへ編集を広げない。

### Phase 4 Execute
- 本Issueは Stream H 専任対象として、Issueメモへの同期記録追加のみに限定した。
- Fail-safe 条件（差分競合 / 用語ドリフト / 指定外編集）を満たす変化がないことを確認した。

### Phase 5 Verify（自己修復上限3回）
- Verify-1: `python 01_Plans/issues/validate_active_issue_memos.py --files <this-issue-file>`
- Verify-2: `git diff --check`
- 結果: 本更新では自己修復 0/3（再試行なし）。

### Phase 6 Proceed
- 判定: **Ready（Stream H lane）**
- 次アクション: それぞれの対象 `04_Documentation/*` 本文更新PR時に、AUTH-OPS-03 / DOC-OPS-02 の語彙整合チェックを再実施する。

## 18) Stream K execution record（DOC-OPS-05-09）

### Phase 1: Read（対象再読と抽出）
- Status: `Draft`
- Priority: `P2`
- Scope: `04_Documentation/local_llm_ops_guide.md`
- Expected verification level: `docs-check`
- Audience: 外部運用者（閉域/企業）
- Goal: ローカルLLM運用時の最小runbookを提供する。
- Non-goal: 組織固有の承認フロー、秘密情報管理、内部監査ログ保管方式の決定。
- Public boundary: 公開可能な運用条件と検証手順のみを記載し、秘密情報・内部承認ログ・組織固有手順は含めない。
- 前提差分: **held**（上流仕様差分は本サイクルで未確定のため据え置き）。

### Phase 2: ADR/CDC（明文化）
- Context: `local_llm_ops_guide.md` は外部利用価値が高い一方で、内部運用情報の混入を防ぐ公開境界固定が必要。
- Decision: **external改善（Improve external）を維持**し、内部移設は採用しない。
- Consequences:
  1. 本Issueは docs-only の分類確定メモとして継続する。
  2. 実施単位は公開runbook品質向上（境界明示・検証導線明示）に限定する。
  3. internal限定情報は `04_Documentation` へ持ち込まない。

### Phase 3: Plan（AC/DoD整合）
- Plan → Execute → Verify → Proceed の順序で進行する。
- AC確認:
  1. 分類結果明記: **Improve external** を維持。
  2. 公開境界根拠明記: Audience / Goal / Non-goal / Public boundary を記録。
  3. 次アクション明記: 公開runbookの改善単位を固定。
- DoD確認:
  1. allowlist外差分0。
  2. docs-check記録を残す。
  3. 安全境界（safeMode既定ON・漏えい防止）後退なし。

### Phase 4: Execute（承認済み範囲のみ）
- 実施内容: 本Issueメモに Stream K の分類判断・根拠・次アクションを追記。
- 非実施: `04_Documentation/local_llm_ops_guide.md` 本文更新（本サイクルでは不要）。

### Phase 5: Verify（AC/DoD照合）
- docs-check:
  - `rg -n "Stream K execution record|Status:|Priority:|Scope:|Expected verification level|Audience|Goal|Non-goal|Public boundary|Improve external" 01_Plans/issues/issue-doc-ops-05-09-04doc-local-llm-ops-guide.md`
  - `git diff --check`
- self-correction: 0/3（修正再試行は不要）。

### Phase 6: Proceed（Go/Conditional/No-Go）
- 判定: **Go**
- 根拠: AC 3点・DoD 3点を満たし、allowlist外差分なし。
- 次アクション: 必要時のみ `04_Documentation/local_llm_ops_guide.md` で公開境界の表現改善を実施する（本Issueの分類は固定）。

## 17) Stream G serial run record（2026-04-25）

### Phase 1 Read
- 再確認: `Status=Draft` / `Priority=P2` / `Scope=04_Documentation/local_llm_ops_guide.md` / `RequirementID=DOC-OPS-05-09` / `VerificationLevel=docs-check`。
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

## 18) Stream H serial completion record（2026-04-26 / DOC-OPS-05-09）

### Phase 1 Read
- 対象Issueと対象文書（`04_Documentation/local_llm_ops_guide.md`）を再読し、05-02完了後に開始したことを確認。

### Phase 2 ADR/CDC
- Context: local LLM運用は対外価値がある一方、公開境界を越える内部手順の混入を防ぐ必要がある。
- Decision: 本Issueの分類は **Improve external** を維持し、LLM運用境界の説明に限定する。
- Consequences: 実装仕様の追加は行わず、公開runbookとしての導線整備に留める。

### Phase 3 Plan
- AC/DoD不足はなし（既存ACを採用）。
- 実行計画: docs-only最小差分で、Issueと対象文書に直列フェーズ完了ログを追記する。

### Phase 4 Execute
- Issue本文に本セクションを追記し、直列フェーズの完了証跡を追加。

### Phase 5 Verify
- docs-check: `rg -n "Stream H serial completion record|Improve external|LLM運用境界|Phase 5 Verify" 01_Plans/issues/issue-doc-ops-05-09-04doc-local-llm-ops-guide.md 04_Documentation/local_llm_ops_guide.md`
- diff-check: `git diff --check`
- 自己修復回数: 0/3。

### Phase 6 Proceed
- 判定: **Ready**（05-09完了）。
- 直列タスク: Stream H 対象範囲の2Issueを完了。


## Stream K serial run（2026-04-26 / Prompt K lane / step 1/4: DOC-OPS-05-09）

### Phase 1 Read
- 本Issueと対象 `04_Documentation/local_llm_ops_guide.md` を再読し、分類固定（**Improve external**）が維持されていることを確認。
- 観点: LLM運用公開境界（公開可能な運用手順のみ）。

### Phase 2 ADR/CDC
- Context: DOC-OPS-05 の分類固定を崩さず、公開境界を保ったまま次アクションを再確認する。
- Decision: 本Issueは **Improve external** を維持し、分類再判定は行わない。
- Consequences: 後続作業は docs-only の公開改善に限定できる。

### Phase 3 Plan
- 固定順序: Plan → Execute → Verify → Proceed。
- AC/DoD優先: Audience / Goal / Public boundary / Validation / Next action を本文で追跡可能に維持。
- 停止条件: self-repair 3回超過、または指定外編集検知時は停止。

### Phase 4 Execute
- 実施: 本Issueメモに Prompt K 直列処理ログのみを追記。
- 非実施: 指定外ファイル編集、実装コード変更、分類の再決定。

### Phase 5 Verify
- docs-check: `git diff --check`
- self-repair: **0/3**（本更新時点）。

### Phase 6 Proceed
- 判定: **Ready**。
- 次アクション: `Improve external` 方針のまま、対象Docの公開改善タスクへ接続。

## Stream L serial cycle (2026-04-26 / DOC-OPS-05-09)

### Read
- Requirement meta を再確認し、分類 `Improve external` と LLM運用公開境界を再確認。

### Plan
- AC/DoD補完方針: 公開可能な運用手順と内部監査運用を分離して記述維持。
- ADR: 運用境界差分は新規発生なしのため追加ADRは不要。

### Execute
- 本Issueメモへ Stream L 直列ログを追記（docs-only）。

### Verify
- `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-09-04doc-local-llm-ops-guide.md`
- `git diff --check`
- self-repair: 0/3（上限3回、4回目相当は停止）。

### Proceed
- 判定: **Ready**。
- 次工程: 05-10 へ直列進行。


## Stream H dedicated serial run（2026-04-27）

### Phase 1 Read（開始同期）
- Read同期: `AGENTS.md` Read Order（00→01→02）と本Issueを再読し、公開境界と `Improve external` 固定を確認。

### Phase 2 ADR/CDC
- Context: local LLM 運用文書は公開可能だが内部運用情報混入を避ける必要がある。
- Decision: 既存分類 **Improve external** を維持し、LLM運用境界の説明に限定。
- Consequences: docs-onlyで再現可能な運用導線を維持できる。

### Phase 3 Plan
- 実行計画: 本Issueメモの追記のみ。
- 停止条件: self-correction 4回目相当 / 未承認確定化 / allowlist外編集要求。

### Phase 4 Execute
- 実施: Stream H 専属ログ追記（対象1ファイル）。
- 非実施: 実装コード・architecture本体・shared resource。

### Phase 5 Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-09-04doc-local-llm-ops-guide.md`
- `git diff --check`
- self-correction: 0/3。

### Phase 6 Proceed
- 判定: **Ready**。


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
- Read同期を再実施（AGENTS Read Orderの上流要素 + `04_Documentation/local_llm_ops_guide.md`）。
- Scope再確認: docs-only、allowlist外ファイルは非編集。

### Phase 2 ADR/CDC
- Context: local LLM運用文書は公開価値が高い一方、内部運用情報の混入を防ぐ境界管理が必須。
- Decision: 本Issueの分類を **Improve external** として維持する。
- Consequences: 公開runbook強化を進めつつ、秘密情報/内部承認ログを非対象として固定する。

### Phase 3 Plan
- 直列固定: Plan -> Execute -> Verify -> Proceed。
- AC/DoD不足提案（Issue内合意）:
  - AC-G-09: `Public boundary` と `Outcome` を公開文書の完了判定に紐づける。
  - DoD-G-09: Verifyは docs-check（`rg` + `git diff --check`）を必須とする。

### Phase 4 Execute
- 本Issueメモへ2026-04-27実行ログを追記。
- 指定外編集・実装変更は未実施。

### Phase 5 Verify
- docs-check:
  - `rg -n "2026-04-27 Stream G serial execution|Improve external|Public boundary|Outcome" 01_Plans/issues/issue-doc-ops-05-09-04doc-local-llm-ops-guide.md`
  - `git diff --check`
- Self-Correction: 0/3（失敗なし）。

### Phase 6 Proceed
- 判定: **Ready**。
- 次アクション: local LLM ops公開改善PR（docs-only）を継続可能。

## Stream J DOC-OPS-05 dedicated run (2026-04-27, Set2)

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
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-09-04doc-local-llm-ops-guide.md`
  - `git diff --check`
- self-correction: 0/3（失敗時のみ最大3回、4回目相当は即停止）。

### Phase 5 Proceed
- 判定: **Go**（停止条件: セキュリティ導線矛盾 / 指定外編集 / self-correction上限超過 に非該当）。


## Stream G dedicated lane run（2026-04-28 / DOC-OPS-05 Security-docs専任）

### Phase 1 Read（開始同期）
- Read同期を実施し、Read Orderと本Issueの `Requirement meta I/F` / `GoNoGoGate` / `SecurityGateImpact` を再確認。
- docs-only・allowlist内編集・`VerificationLevel=docs-check` 固定を再確認。

### Phase 2 ADR/CDC（C/D/C + 承認）
- Context: local LLM運用文書は公開運用者向けのため、公開境界と運用語彙の固定が必要。
- Decision: 本Issueの分類は **Improve external** を維持し、役割語彙は `Security Officer / System Owner / Platform Operator` に固定する。
- Consequences: 公開可能な運用手順のみを強化し、内部統制の再定義を回避する。
- Approval: **Issueメモ内運用承認（DOC-OPS-05 Stream G）** を記録。未承認事項は確定しない。

### Phase 3 Plan（AC/DoD不足ドラフト提案）
- AC Draft:
  - AC-G-09-1: Audience / Goal / Non-goal / Public boundary / Related の追跡可能性を維持する。
  - AC-G-09-2: Go/No-Go判定条件を本文で再現可能にする。
- DoD Draft:
  - DoD-G-09-1: 6フェーズを直列で記録する。
  - DoD-G-09-2: self-correction を3回上限に固定し、超過時は `Hold`。

### Phase 4 Execute
- 実施: 本Issueメモ更新のみ（docs-only / allowlist内）。
- 非実施: 実装変更、D1〜D4固定値変更、未承認確定化。

### Phase 5 Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-09-04doc-local-llm-ops-guide.md`
- `git diff --check`
- self-correction: 0/3。

### Phase 6 Proceed
- 判定: **Ready**
- 理由: Stream G専任レーン条件（6フェーズ/C-D-C承認/AC-DoDドラフト/3回上限）を満たす。


## Stream G dedicated serial completion (2026-04-28)

### Phase 1 Read
- AC/Validationの再収集を実施し、`Requirement meta I/F`・`Acceptance criteria`・`Validation plan` の3点が本文に存在することを確認。
- フェイルセーフ確認: AC不在/検証不能/allowlist外編集要求は該当なし。

### Phase 2 Plan
- 難易度低→高の固定順を `01 → 03 → 08 → 10 → 04 → 09 → 12 → 14` としてロック。
- 本Issueの実行順は **6/8** とし、分類 `Improve external` を維持。

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
- `git diff --check` と `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-09-04doc-local-llm-ops-guide.md` を実行対象とする。
- 自己修復回数: 0/3（4回目相当はHold停止）。

### Phase 5 issue更新
- 判定: **Ready**（停止条件非該当、docs-only維持）。


## Stream G normalization pass（2026-05-04）

### Phase 1: Read同期（Issue ↔ 04_Documentation 対応表）
| Issue | Target 04_Documentation | Current classification |
| --- | --- | --- |
| `issue-doc-ops-05-09-04doc-local-llm-ops-guide.md` | `04_Documentation/local_llm_ops_guide.md` | 既存本文の Decision / Proposed classification を継承 |

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

- Batch: `B (06-10)`
- GateStatus: `Conditional`（現時点のIssue StatusはDraftのため、Open化は本ゲートの充足を条件とする）
- DraftReasonClass: `open-trigger-not-executed`
- BlockingIssueIDs: `none`
- OpenTrigger:
  1. `Status` を Draft から Open へ変更。
  2. `Expected verification level` と `VerificationLevel` が `docs-check` で一致。
  3. `GoNoGoGate=Required` に対する判定条件（Ready/Hold/Needs-decision）が本文中で一意。
  4. `DecisionStatus=Fixed` の場合、`DecisionQueueRef` は `N/A` であること。
- MechanicalChecks:
  - `rg -n "^- Status:|Expected verification level|VerificationLevel|GoNoGoGate|DecisionStatus|DecisionQueueRef" 01_Plans/issues/issue-doc-ops-05-09-04doc-local-llm-ops-guide.md`
  - `rg -n "Open readiness:|状態分類:|Phase 5: Proceed" 01_Plans/issues/issue-doc-ops-05-09-04doc-local-llm-ops-guide.md`
  - `git diff --check`
- Proceed verdict (Phase 6): `Open可能（条件付き）`

## Stream G documentation/public boundary pass (2026-06-13)

### Plan
- 対象: `local llm ops`。
- Scope: Docs-only。`03_Implement/` と `02_Architecture/` は編集しない。
- Acceptance: 公開/保守/開発者/内部計画の分類が追跡でき、SafeMode・share/export・AI提案レビューの安全境界が後退しない。

### Execute
- RequirementID `DOC-OPS-05-09` の公開境界を再確認。
- Decision: local_llm_ops_guide は local LLM の設定・戻し方に限定し、external provider/escalation は明示的opt-inがない限り既定OFFである説明を維持した。

### Verify
- docs-check 対象として issue memo metadata、Markdown整形、リンク導線、公開不可情報の混入有無を確認する。
- Self-correction budget: 0/3 から開始し、4回目相当は停止する。

### Proceed
- 判定: Ready for verification。
- 残課題: 実ファイル移動や開発者向け正本の再配置が必要な場合は、別PRで allowlist と移動先を明示して扱う。
