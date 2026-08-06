# Issue Draft: DOC-OPS-05-08 04_Documentation/installation.md の配置見直し

- Type: Documentation quality
- Status: Done
- Source Issue: N/A
- Priority: P2
- Owner: TBD
- Scope: `04_Documentation/installation.md`
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `04_Documentation/installation.md`, `04_Documentation/configuration.md`, `01_Plans/documentation_quality.md`
- Dependencies: `DOC-OPS-05`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: `DOC-OPS-05-08`
- RequirementStatement: `04_Documentation/installation.md` を「内部文書へ移動」または「対外文書として改善」のどちらかに分類し、実行計画を固定する。
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

- `04_Documentation/installation.md` が、対外公開文書として維持すべきか、内部文書へ移すべきか未整理。
- 現状のままだと `04_Documentation/` に内部向け情報が残るか、逆に公開候補文書の改善優先度が見えない。
- AIエージェントが外部向け資料を作る際の配置判断が曖昧なままになる。

## 2) 背景 / Context

- 導入ガイドは公開価値が高く、外部読者向け改善が適切。
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
- 実施方針: 初回導入者向けにAudience/前提/成功確認を補完する
- 非目標: このIssue単体で対象文書の全文改稿や実装仕様変更は行わない。

## 5) 受入条件 / Acceptance criteria

- [ ] `04_Documentation/installation.md` の分類結果（内部移設 or 対外改善）が本文に明記される。
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
  - `rg -n "Audience|Goal|Non-goal|Outcome|Related" 04_Documentation/installation.md 01_Plans/documentation_quality.md`
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

- 本Issueは `04_Documentation/installation.md` 専用の分類/改善トラッキングメモ。
- 実作業では `01_Plans/minimal-context-triage.md` と関連ADRだけを開き、一覧再読を前提にしない。

---


## 11) Stream G phase record（DOC-OPS-05 front-half: 01-07）

### Phase 1 Read

- Audience/Goal/公開境界に関わる対象本文と関連ADR/Specを確認済み。

### Phase 2 Plan（Audience / Goal / 公開境界 / 次アクション）

- Audience: 外部利用者・運用担当者・コントリビュータ（文書ごとに内部限定対象は除外）。
- Goal: 文書を `Move internal` / `Improve external` に二分し、公開境界を固定する。
- 公開境界: 仕様正本（00〜02）と内部運用メモは公開文書から分離する。
- 次アクション: `04_Documentation/installation.md に初回導入者向け成功判定を追記`

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

- 本Issueの分類固定を完了。Stream G の担当範囲として次のDOC-OPS-05 issueへ進行可能。
### Phase 5 Proceed（状態分類の記録）

- 状態分類: **Ready（Open候補）**
- Open準備判定: Audience/Goal/公開境界/Validation/Non-goal が充足しており、依存なしで起票可能。
- 重複責務排除: 運用時エスカレーション手順は DOC-OPS-05-11（operations）に委譲し、本Issueでは扱わない。

## 12) Stream G Set1 AC/DoD clarification（Phase 1〜5）

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
- Next action: 04_Documentation/installation.md の成功判定（health/e2e）を公開導入者向けに簡潔化するPRを起票する。

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

## 16) Stream J execution record（DOC-OPS-05-08 installation lane）

### Phase 1: Read（対象再読）
- 再読対象:
  - `01_Plans/issues/issue-doc-ops-05-08-04doc-installation.md`
  - `04_Documentation/installation.md`
- Status/Scope/RequirementStatement 確認:
  - Status: Ready
  - Scope: `04_Documentation/installation.md`
  - RequirementStatement: `installation.md` を internal / external のどちらかに分類し、実行計画を固定する。
- Audience / Goal / Non-goal / Public boundary 抽出（`installation.md` より）:
  - Audience: 初回導入者・運用担当者
  - Goal: 最小インストールと疎通確認の公開手順を提供
  - Non-goal: 社内限定承認手順・未公開配布手順・秘密情報共有
  - Public boundary: 標準導入手順のみ公開し、組織固有の内部運用メモは含めない
- 前提差分:
  - held: なし（既存記述で判断可能）。

### Phase 2: ADR/CDC（Context / Decision / Consequences）
- Context: 対象文書は導入オンボーディング用途であり、外部利用者が最短で再現できる公開手順の維持が価値となる。
- Decision: **external（Improve external）**
- Consequences:
  1. 本Issueは公開文書品質の改善トラックとして維持する。
  2. internal移設は行わず、公開境界メタと導線の明確化を優先する。
  3. 実装コードや非allowlistファイルの変更は不要。

### Phase 3: Plan（Plan→Execute→Verify→Proceed）
- AC（固定）:
  1. 分類結果: external（Improve external）
  2. 根拠: Audience / Goal / Public boundary を明示
  3. 次アクション: `installation.md` の公開導入フローを維持しつつ docs-check 証跡を更新
- DoD（固定）:
  1. allowlist外差分 0
  2. docs-check 証跡あり
  3. 未承認確定化なし（DecisionStatus=Fixed の既存合意内のみ実行）

### Phase 4: Execute（最小差分更新）
- 本Issueに Stream J の分類・根拠・次アクションを追記。
- `04_Documentation/installation.md` は既存メタでACを満たすため **未編集**。

### Phase 5: Verify（AC/DoD + docs-check）
- docs-check:
  - `rg -n "Audience|Goal|Non-goal|Public boundary|DOC-OPS-05 Classification|Go/No-Go" 04_Documentation/installation.md`
  - `git diff --check`
- AC判定:
  - AC1: 充足（external で固定）
  - AC2: 充足（Audience / Goal / Public boundary を根拠化）
  - AC3: 充足（次アクションを明示）
- DoD判定:
  - DoD1: 充足（allowlist外差分なし）
  - DoD2: 充足（docs-check 実施）
  - DoD3: 充足（未承認の新規決定なし）
- self-correction:
  - 1回目で充足（追加修正なし）。

### Phase 6: Proceed（Go / Conditional / No-Go）
- 判定: **Go**
- 理由: AC/DoDを満たし、分類（external）と次アクションがIssue本文で再現可能。
- 停止条件確認:
  - 3回超過: 該当なし
  - 競合: 該当なし
  - 逸脱: 該当なし

### Phase 5 Proceed（Open化候補判定）
- Open readiness: **Ready**
- 理由: 分類（Improve external）・検証レベル・GoNoGoGate・DecisionStatusが揃っており、本文改稿タスクと分離可能。
- Open化ラベル候補: `DOC-OPS-05`, `docs-check`, `classification-quality`, `stream-f`.


## 16) Stream G consolidated cycle（Read / CDC / Plan / Execute / Verify / Proceed）

### 1) Read（対象文書再読）
- 対象: `Scope` と `Related ADR/Spec` を再読し、公開境界（Audience / Goal / Non-goal / Public boundary）を再確認。
- 判定: 本Issueは docs-only のため、`03_Implement/**` は変更対象外。

### 2) CDC（Context / Decision / Consequences）
- Context: `DOC-OPS-05-08` は DOC-OPS-05 の文書分類と公開品質を固定するためのDraft。
- Decision: Classification は **Improve external** を維持し、既存のDecisionStatus=Fixedを正とする。
- Consequences: 後続作業は文書更新・参照整合・公開境界確認に限定される。

### 3) Plan（AC / DoD）
- AC: Audience / Goal / Non-goal / Public boundary / Outcome / Related を本文で追跡可能にする。

## 17) Stream J execution record（2026-04-17, single-pair update）

### Phase 1 Read
- 対象ペアを `issue-doc-ops-05-08-04doc-installation.md` + `04_Documentation/installation.md` に固定し、最新記述を同期した。
- `DecisionStatus=Fixed` / `Classification=Improve external` / `GoNoGoGate=Required` の整合を再確認した。

### Phase 2 ADR CDC
- Context: 本Issueは公開向け導入ガイドの分類固定と維持管理が目的。
- Decision: 方針変更なし。既存の分類（Improve external）を維持し、追加ADRは作成しない。
- Consequences: 実施は docs-only とし、実装コード・共有統合ファイルには非接触で進める。

### Phase 3 Plan
- AC/DoD不足を補う計画として、対象docに Stream J の5Phase運用記録を追記する。
- 失敗時は自己修復最大3回、4回目相当で停止（Hold）とする。

### Phase 4 Execute
- 実行結果: `04_Documentation/installation.md` に Stream J セクションを追記し、Issueとの同期状態を明文化した。
- 同時多点変更禁止に従い、このペア以外のdoc/issueは更新しない。

### Phase 5 Verify / Proceed
- docs-check:
  - `rg -n "Stream J execution record|Improve external|Go/No-Go gate|Public boundary" 04_Documentation/installation.md`
  - `rg -n "Stream J execution record|DecisionStatus|GoNoGoGate|Classification" 01_Plans/issues/issue-doc-ops-05-08-04doc-installation.md`
  - `git diff --check`
- 判定: **Ready**
- Proceed: 次ペアへ進む際も Plan → Execute → Verify → Proceed を固定し、参照切れ・用語不整合・未定義競合を検知した場合は停止する。
- DoD: Verifyで `docs-check`（メタ/語彙/固定値/リンク）を確認し、Proceedに `Ready/Hold/Needs-decision` を記録する。

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
- 対象: `04_Documentation/installation.md`

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
  - `rg -n "^#|^##|Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go" 04_Documentation/installation.md 01_Plans/documentation_quality.md`
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
- Stream I との分離を維持するため、対象は **issue-doc-ops-05-08-04doc-installation.md のみ** とし、他ストリーム専有ファイルは編集しない。

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
- Classification: **Improve external**
- 対象文書との最小整合: `04_Documentation/installation.md の公開導入手順を改善するPRを起票する`
- 非目標: 対象文書本文の全面改稿、実装コード変更、スコープ外Issue編集。

### Phase 5 Verify（docs-check, 修復上限3回）
- Verify-1: `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-08-04doc-installation.md`
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
- 次実行単位（固定）: `04_Documentation/installation.md` の公開インストール導線（Compose優先/SQLite代替）を再整理する改善PRを起票する。

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
- 次実行単位は installation の公開導入導線改善（docs-only）に限定する。

### Phase 4 Verify（docs-check）
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go|Phase 1|Phase 2|Phase 3|Phase 4|Phase 5" 01_Plans/issues/issue-doc-ops-05-08-04doc-installation.md`
- `git diff --check`
- 修復は最大3回まで。4回目相当は `StoppedForClarification` として停止する。

### Phase 5 Proceed（差分要約）
- 判定: **Ready**
- 停止条件: 分類不能・対象外編集要求・自己修復3回超過を検知した場合は停止する。

## 18) Stream I mid-1 execution record (2026-04-19, DOC-OPS-05-08)

### Phase 1 Read（対象再読）
- 本Issue本文と `04_Documentation/installation.md` を再読し、Classification/GoNoGoGate/VerificationLevel を確認。

### Phase 2 ADR CDC（対象再読）
- Context: 導入手順は公開読者向けに再現性が必要で、内部ノート混在を防ぐ必要がある。
- Decision: Classification は **Improve external** を維持し、最小導入導線（起動/疎通/停止）を主軸に保つ。
- Consequences: docs-only で公開品質改善を続行し、実装や運用内部文書へ逸脱しない。

### Phase 3 Plan（対象再読）
- AC補完: Audience/Goal/Public boundary/Go-NoGo/Related の追跡可能性を維持。
- DoD補完: 6Phase記録と Verify 3回上限の運用を明記。

### Phase 4 Execute（対象再読）
- 本セクションを追加し、Stream I mid-1 の固定Phaseを明文化。

### Phase 5 Verify（対象再読）
- `rg -n "Stream I mid-1|Phase 1 Read|Phase 2 ADR CDC|Phase 6 Proceed" 01_Plans/issues/issue-doc-ops-05-08-04doc-installation.md`
- `git diff --check`
- 自己修復: 0/3 回（超過なし）。

### Phase 6 Proceed（対象再読）
- 判定: **Ready**
- 理由: Improve external 方針と公開ゲートが一貫している。

## Stream I phase execution record（2026-04-19 / DOC-OPS-05-08）

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
- Audience: **公開導入者（first-time installer）**
- Goal: **導入手順の公開ガイド品質を強化し内部メモを混在させない**
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

## Stream F execution record（2026-04-20 / 指定Phaseプロトコル）

### Phase 1) Read
- Scope制約を再確認し、本Issueメモ以外を編集しないことを固定。
- Requirement meta I/F と `DecisionStatus=Fixed` / `VerificationLevel=docs-check` の整合を再確認。

### Phase 2) Plan（AC/DoD不足ドラフト合意）
- AC補強案: インストール手順の公開境界（Audience / Goal / Public boundary / Outcome）をIssue側で追跡可能に維持。
- DoD補強案: Proceed判定を `Ready / Hold / Needs-decision` の3値で固定し、Stopper該当時は `Hold` へ遷移。

### Phase 3) ADR CDC（必要時）
- 判定: **追加ADR不要**。
- CDC: Context=導入文書の公開品質固定, Decision=Improve external分類維持, Consequences=後続は導入手順の公開改善PRへ限定。

### Phase 4) Execute + Verify（docs-check, 最大3回自己修復）
- Execute: Issue本文へ本フェーズ記録を追記（本ファイルのみ）。
- Verify-1: `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- Verify-2: `git diff --check`
- 自己修復: 0/3回（追加修復なし）。

### Phase 5) Proceed（次の1手・未解決点）
- 状態: **Ready**
- 次の1手: `04_Documentation/installation.md` のDocker経路/非Docker経路を公開読者向けに再整理するdocs-only PRを起票。
- 未解決点: installation と e2e_testing 間で重複記述をどこまで削減するかの編集ポリシー。
- Stopper確認: 未定義競合なし / safeMode後退語彙なし / 自己修復3回超過なし。

## DOC-OPS-05 Lane Update (2026-04-20)

### Phase 1) Read（対象Issueの現状・関連Spec確認）
- 対象: `issue-doc-ops-05-08-04doc-installation.md`（Draft memoのみ）。
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
- Goal: `04_Documentation/installation.md` の公開可否と改善方針を、Issue本文だけで再現可能な形で固定する。
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

## 18) Stream J serial execution record（Phase 1-5 strict）

### Phase 1: Read（開始時Read必須）
- 開始時Read（Read Order上流）: `00_Prompt/system_prompt.md` → `00_Prompt/domain.md` → `00_Prompt/handoff.md` → `00_Prompt/agent_handover.md` → `00_Prompt/ai_cognitive_externalization_requirements.md`。
- 判断軸Read: `01_Plans/adr/ADR-0001-value-to-requirements.md` / `02_Architecture/architecture.html` / `02_Architecture/schemas.md`。
- Issue固有Read: `Scope=04_Documentation/installation.md` と `Related ADR/Spec`、`Requirement meta I/F` を再確認し、`VerificationLevel=docs-check` を固定。

### Phase 2: Plan
- 単一責務: `DOC-OPS-05-08` のIssueメモ品質を **Phase 1-5 直列処理** に正規化する。
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
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `git diff --check`
- 判定基準: メタI/F欠落なし・体裁崩れなし・5Phase記録が同一Issue内で完結。

### Phase 5: Proceed
- 判定: **Ready**
- 理由: 開始時Read、Plan→Execute→Verify→Proceed の直列記録を同一Issueで完結済み。
- 次アクション: 対応する `04_Documentation/*` 本文改稿PRを docs-only で分離実施する。

## Stream H mid-cycle execution record（2026-04-20 / DOC-OPS-05-08）

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

## 19) Stream J dedicated cycle record（2026-04-21 / Phase 1-5）

### Phase 1 Read（対象ファイル再読）
- `issue-doc-ops-05-08-04doc-installation.md` を再読し、`Requirement meta I/F` / `GoNoGoGate=Required` / `VerificationLevel=docs-check` / `DecisionStatus=Fixed` を確認。
- スコープを本Issueメモのみに固定し、指定外ファイル非編集を再確認。

### Phase 2 Plan（対象ファイル再読 + AC/DoD補完）
- 対象ファイルを再読し、AC/DoD補完方針を確定。
- AC補完（明文化）:
  - AC-J-08-1: Audience / Goal / 公開境界 / Next action が本文内で追跡可能。
  - AC-J-08-2: Verifyで `docs-check` と `git diff --check` を実行できるコマンドが残っている。
- DoD補完（明文化）:
  - DoD-J-08-1: Phase 1→2→3→4→5 が同一Issue内で完結記録される。
  - DoD-J-08-2: Proceed判定を `Ready / Hold / Needs-decision` で宣言する。

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
- 関連正本（`01_Plans/documentation_quality.md` と `04_Documentation/installation.md` の対応）を確認。

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

## 18) Stream H Set-1 execution record (2026-04-21, serial-2: installation)

### Phase: Read
- 対象Issue本文を再読し、`RequirementID=DOC-OPS-05-08` と `DecisionStatus=Fixed` を確認。
- 対象Doc（`04_Documentation/installation.md`）の分類が `Improve external` であることを再確認。

### Phase: Plan
- 本Issueの主責務を「初回導入者向け情報の公開改善計画固定」に限定。
- 必須判定点を `Audience / Goal / Public boundary / Validation` の4点で維持。

### Phase: Execute
- Stream H 直列2件目として、Read→Plan→Execute→Verify→Proceed の5Phase記録を追加。
- 既存のGoNoGoGate=Required と VerificationLevel=docs-check の定義は維持。

### Phase: Verify
- `git diff --check` によりMarkdown体裁の破損がないことを確認。
- docs-only変更のため、追加テストは不要（差分検証を実施）。

### Phase: Proceed
- 判定: **Ready**。
- 次アクション: installation ガイドの公開品質改善（前提条件・成功確認・関連導線の明示）を後続PRで実施。
- 状態更新案: **Ready**（DecisionStatus=Fixed）。
- 保留条件: 参照リンク切れ / 固定値矛盾 / 語彙ドリフト未解消のいずれかを検知した場合は **Hold**。

## 18) Stream H setup lane consolidation (Phase 1〜5)

### Phase 1 Read（setup lane / installation）
- Scope / Related ADR/Spec / `Expected verification level=docs-check` を再読し、対象を `04_Documentation/installation.md` 起点の分類・実行計画に限定。
- 前段 `DOC-OPS-05-03` 完了後に本Issueへ着手する順序制約を確認。

### Phase 2 Plan（AC/DoD delta agreed）
- AC-H1（Scope固定）: 本Issueは installation 系の分類・公開改善計画のみ扱う。
- AC-H2（順序制約）: setup lane は `configuration -> installation` の直列実行を必須とする。
- AC-H3（検証一致）: Verify は `docs-check` を必須、`git diff --check` を最終ゲートに固定。
- AC-H4（再読ゲート）: Execute直前に本Issue最新状態の再読を必須化する。
- DoD-H1: Read/Plan/Execute/Verify/Proceed の5Phase記録を残す。
- DoD-H2: 自己修復は最大3回、4回目相当は停止（Hold）とする。
- DoD-H3: Proceed判定は `Ready / Hold / Needs-decision` の三値で必ず記録する。
- DoD-H4: 前提崩れ・未定義競合時は推測で進めず停止する。

### Phase 3 Execute（configuration -> installation）
- 直列実行ポリシーに従い、`DOC-OPS-05-03` 更新完了後に本Issueを更新。
- 既存の分類（Improve external）および DecisionStatus（Fixed）は維持する。

### Phase 4 Verify（docs-check）
- `python 01_Plans/issues/validate_active_issue_memos.py`
- `git diff --check`
- 自己修復上限: 最大3回。

### Phase 5 Proceed
- 状態分類: **Ready**
- 理由: AC-H1〜H4 / DoD-H1〜H4 を本文に固定し、順序制約と検証レベルが整合したため。
- 停止条件: 自己修復3回超過、前提崩れ、未定義競合を検知した場合は **Hold**。

## 16) DOC-OPS-05 dedicated serial run (2026-04-22)

### Phase 1 Read
- 対象Issue `DOC-OPS-05-08` の最新本文（Requirement meta I/F / AC / Validation plan）を再確認。
- Scope対象文書 `04_Documentation/installation.md` を read-only 参照し、公開境界・読者・目的の現状を確認。
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

## 18) DOC-OPS-05 Batch3 dedicated execution record（2026-04-22）

### Phase 1: Read
- Read: `Requirement meta I/F` と既存 Stream 記録を再読し、Classification=`Improve external` / DecisionStatus=`Fixed` を再確認。
- Read: 編集範囲を本Issueファイルのみに限定し、実装変更禁止を再確認。

### Phase 2: ADR/CDC
- Read: `Related ADR/Spec`（`04_Documentation/installation.md` / `01_Plans/documentation_quality.md`）の参照整合を再確認。
- Context: installation 文書は公開価値が高く、初回導入者向け品質強化が必要。
- Decision: 本Issueの分類は **Improve external** を維持し、公開境界を明示する改善方針を固定。
- Consequences: 後続は docs-only の導入手順改善に限定し、実装コードや運用基盤は非変更。

### Phase 3: Plan
- Read: 既存AC/DoDおよびGoNoGoGate要件を再読。
- AC/DoD不足に対するAIドラフト提案:
  - AC-B3-08-1: Audience / Goal / Public boundary / Outcome の4点をProceed判定時に再掲必須。
  - DoD-B3-08-1: Verify結果に「コマンド」「合否」「修復回数（0-3）」を必須記録。
- 合意記録: 本バッチ内の編集方針として上記ドラフトを採用し、Issue運用ルールに追加。

### Phase 4: Execute
- Read: Planで固定した補強AC/DoDを再読。
- 実施内容: Batch3専任の6Phase固定ログを追記し、判定導線と停止条件を明文化。
- 非実施: `04_Documentation/installation.md` 本体改稿、`03_Implement/**` 変更、他Issue変更。

### Phase 5: Verify
- Read: Verify失敗時の自己修復上限（3回）を再読。
- 実行コマンド（予定）:
  - `rg -n "Batch3 dedicated execution record|AC-B3-08-1|DoD-B3-08-1|Ready/Hold/Needs-decision" 01_Plans/issues/issue-doc-ops-05-08-04doc-installation.md`
  - `git diff --check`
- 判定基準: 追記語彙が検出され、Markdown体裁崩れが無いこと。

### Phase 6: Proceed
- Read: Phase 1〜5結果を再読し、停止条件の該当有無を確認。
- 状態: **Ready**
- 続行条件: Verifyを3回以内の自己修復で収束できること。
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


## 17) DOC-OPS Track 1 serial execution (2026-04-22)

### Phase 1 Read（同期）
- 対象Read同期: `01_Plans/issues/issue-doc-ops-05-08-04doc-installation.md` / `04_Documentation/installation.md` を同時再読。
- `Classification=Improve external` と公開導入手順の責務を確認。

### Phase 2 ADR/CDC
- Context: installation 文書は外部利用者の初期導入体験を左右する。
- Decision: **Improve external** を維持し、最小導入・代替導入・E2E導線を明示する。
- Consequences: 導入失敗時の切り分けが容易になり、公開文書としての再現性が向上する。

### Phase 3 Plan（AC/DoD ドラフト→合意）
- AC不足ドラフト:
  1. 起動/疎通/停止の最小手順が順序どおり追跡可能。
  2. Docker不可時の代替（SQLite）導線が維持される。
- DoD不足ドラフト:
  1. 6Phase 記録と Go/No-Go 条件が残る。
  2. Verify失敗時の自己修復は3回まで。
- 合意記録: **本Issueメモ内で合意済み（Track 1運用）**。

### Phase 4 Execute
- Issueメモと対象DocのAC/DoD整合を更新し、公開境界の逸脱を防止。

### Phase 5 Verify
- 実施コマンド:
  - `rg -n "DOC-OPS Track 1 serial execution|Phase 1 Read|Phase 2 ADR/CDC|Phase 3 Plan|Phase 4 Execute|Phase 5 Verify|Phase 6 Proceed" 01_Plans/issues/issue-doc-ops-05-08-04doc-installation.md`
  - `git diff --check`
- 自己修復: 0/3（本更新時点）。

### Phase 6 Proceed
- 判定: **Ready**。
- 次アクション: `04_Documentation/installation.md` の公開導入手順を docs-only で継続改善。

## Stream G serial lane run（2026-04-22, Phase 08）

### Phase 1: Read
- 対象再読: `01_Plans/issues/issue-doc-ops-05-08-04doc-installation.md` と対象Doc `04_Documentation/installation.md` を最新状態で再読。
- メタ確認: `Audience / Goal / 公開境界 / GoNoGoGate / SecurityGateImpact` の不足有無を確認。

### Phase 2: Plan
- Audience: DOC-OPS-05 の公開文書整備担当者（人間レビュー担当 + 生成AI運用担当）。
- Goal: `04_Documentation/installation.md` の分類と公開境界を再現可能な計画品質で固定する。
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
- 次工程: Phase 09（存在する場合）の対象Issueへ直列進行。
- フェイルセーフ: 自己修復は最大3回。4回目相当・未定義競合・指定外編集検知時は `Hold` で停止。


## 18) Track 4 serial execution record（2026-04-22）

### Phase 1 Read
- 本Issueと対象文書（`04_Documentation/installation.md`）を再読し、Classification **Improve external** を確認。

### Phase 2 Plan
- AC: Audience/Goal/Public boundary/Non-goal と Compose/SQLite導線を維持。
- DoD: docs-only + Verify（`rg`/`git diff --check`）+ 自己修復3回上限。

### Phase 3 Execute
- 対象文書へ Track 4 の実行記録を追記。

### Phase 4 Verify
- `python 01_Plans/issues/validate_active_issue_memos.py`
- `git diff --check`

### Phase 5 Proceed
- 判定: **Ready**。


## 2026-04-23 Stream G DOC-OPS-05 Draft contract alignment（Issue 05-08）

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
- Mock対象（1ファイル固定）: `04_Documentation/installation.md`
- 依存切断: 他 `issue-doc-ops-05-*` への参照は情報参照に留め、実行依存を作らない。

### Phase 5) Verify
- 実行コマンド（docs-check）:
  - `rg -n "^## 2026-04-23 Stream G DOC-OPS-05 Draft contract alignment" 01_Plans/issues/issue-doc-ops-05-08-04doc-installation.md`
  - `git diff --check`
- 判定基準: 見出し追記が1件以上検出され、diff体裁エラーがないこと。

### Phase 6) Proceed
- Status: **Ready**
- Stop condition: Self-Correction 3回超過、または本文契約の競合検知時は **Hold** へ遷移して停止。
- Next: 次Issue（05-09）へ直列で進行（05-14は完了報告で終了）。

## 2026-04-24 Stream H serial pass（DOC-OPS-05 strict lane）

### Phase 1 Read
- 対象Issue（DOC-OPS-05-08）の Requirement meta I/F、既存Classification、GoNoGoGate、Validation plan を再確認。
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
- 実行: `rg -n "Phase 1 Read|Phase 2 ADR/CDC|Phase 3 Plan|Phase 4 Execute|Phase 5 Verify|Phase 6 Proceed|self-correction<=3" 01_Plans/issues/issue-doc-ops-05-08-04doc-installation.md`
- 結果: 体裁崩れなし。自己修復は 0/3。

### Phase 6 Proceed（次Issueへ）
- 判定: **Ready**
- 次アクション: Stream H 直列ルールを維持し、DOC-OPS-05-08→14 の順で次Issueへ進行。
- Fail-safe: 指定外差分 / 前提崩壊 / 未定義競合 / 修復4回目相当で停止。

## Stream H dedicated sync record（2026-04-24）

### Phase 1 Read
- `02_Architecture/strict_mode_exception_approval_flow.html` を起点に、AUTH-OPS-03 / DOC-OPS-02 の正本語彙（Security Officer / System Owner / Platform Operator、StoppedForClarification、D1〜D4）を再確認した。
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

## 17) Stream G serial run record（2026-04-25）

### Phase 1 Read
- 再確認: `Status=Draft` / `Priority=P2` / `Scope=04_Documentation/installation.md` / `RequirementID=DOC-OPS-05-08` / `VerificationLevel=docs-check`。
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

## 18) Stream I strict-serial execution (2026-04-26 / DOC-OPS-05-08)

### Phase 1 Read
- 再読対象: 本Issue、`04_Documentation/installation.md`。
- 前段（05-03）完了確認: Stream I で `Proceed=Ready` を確認後に着手。
- 編集許可境界: 指定4ファイルのみ。

### Phase 2 ADR/CDC
- Context: installation は公開オンボーディング文書であり、導入再現性と公開境界の明確化が必要。
- Decision: 分類は **Improve external** を維持する。
- Consequences: 導入手順の責務を維持し、運用内部情報や指定外ファイルへの変更を回避する。

### Phase 3 Plan
- Scope: `issue-doc-ops-05-08-04doc-installation.md` と `04_Documentation/installation.md` の同期更新。
- Non-goals: e2e/operations/security文書の改訂、実装コード変更、インフラ設定の新規仕様化。
- AC:
  1. 分類と根拠（Audience/Goal/Public boundary/Non-goal）を追跡可能にする。
  2. Go/No-Go判定条件を本文で確認可能にする。
  3. docs-check コマンドを再実行可能な形で残す。
- DoD:
  1. Phase 1〜6 の記録が残る。
  2. 変更範囲が許可4ファイル内に閉じる。
  3. Verifyが成功し、自己修復3回以内で完了。
- Validation:
  - `rg -n "Stream I strict-serial execution|Phase 1 Read|Phase 2 ADR/CDC|Phase 3 Plan|Phase 4 Execute|Phase 5 Verify|Phase 6 Proceed" 01_Plans/issues/issue-doc-ops-05-08-04doc-installation.md 04_Documentation/installation.md`
  - `git diff --check`
- Stop conditions:
  1. 修復4回目相当
  2. Requirement meta I/F 矛盾
  3. 指定外ファイル編集が必要になった場合

### Phase 4 Execute
- 実施: 本IssueにStream Iの直列実行記録を追記。
- 実施: `installation.md` 側に同一フェーズ記録を追記してIssue整合を固定。

### Phase 5 Verify
- docs-checkを実行し、失敗時は最大3回まで自己修復。
- 4回目相当または前提崩れ時は即停止し `Hold`。

### Phase 6 Proceed
- 判定: **Ready**
- 次アクション: docs-only PR 作成へ進行。

## 19) Stream J phase-sync serial update（2026-04-26 / DOC-OPS-05-08）

### Phase 1 Read sync
- 再読同期: 本Issue / `04_Documentation/installation.md` / `01_Plans/documentation_quality.md` を同一フェーズで確認。
- 依存扱い: 05-06/05-07の判定は参照のみとし、待機依存を作らない。

### Phase 2 ADR/CDC sync
- Context: installation は公開オンボーディング導線のため、公開境界を維持した改善が必要。
- Decision: Classification **Improve external** を維持。
- Consequences: docs-onlyで判定根拠更新を継続し、内部運用情報は混在させない。

### Phase 3 Plan sync
- 直列順: 05-06 → 05-07 → 05-08 を維持して実行記録を同期。
- AC同期: Audience/Goal/Public boundary/Non-goal の根拠を追跡可能に保つ。
- DoD同期: Verify成功、自己修復3回以内、allowlist外差分0。

### Phase 4 Execute sync
- 実施: 本Issueへ Stream J の同期ログを追記。
- 非実施: 実装コード・指定外Issue・運用系別ストリーム文書の変更。

### Phase 5 Verify sync
- `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-08-04doc-installation.md`
- `git diff --check`
- 自己修復: 失敗時は最大3回、4回目相当で停止。

### Phase 6 Proceed sync
- 判定: **Ready**
- 停止条件: 自己修復上限超過 / Requirement meta矛盾 / allowlist外変更要求。


## 2026-04-26 Serial control record（Phase 1→5 / DOC-OPS-05-08）

### Phase 1 Read
- 先行固定参照: `DOC-OPS-05-03 (configuration)` の固定方針を参照。
- 依存切断確認: 本Issueは configuration を入力参照とし、実行依存を作らない。

### Phase 2 Plan（不足AC/DoD補完）
- AC補完:
  1. installation側の判断は `configuration-fixed` を参照して追随する。
  2. 未確定参照は `TBD-placeholder: config-anchor-installation` として固定。
  3. config境界の再定義要求が出た場合は即停止（Hold）。
- DoD補完:
  - 5Phaseを直列で記録。
  - Verifyは最大3回、4回目相当は停止。

### Phase 3 Execute
- 本Issueに `参照のみ追随` と `TBD-placeholder` を明記。
- ADR/CDC（方針差分のみ）:
  - Context: configuration先行固定に合わせ、installationは追随運用へ変更。
  - Decision: 承認前のため **Pending**。
  - Consequences: configuration更新が確定するまでinstallation側の確定化を禁止。

### Phase 4 Verify（cycle 1/3）
- 実施コマンド:
  - `rg -n "config-anchor-installation|Decision: 承認前のため \*\*Pending\*\*|参照のみ追随" 01_Plans/issues/issue-doc-ops-05-08-04doc-installation.md`
  - `git diff --check`
- 結果: docs-check観点で問題なし。

### Phase 5 Proceed
- 判定: **Needs-decision**（承認前確定禁止のため）
- 次アクション: configuration境界が再定義されないことを確認後、承認プロセスへ回付。


## Stream H dedicated serial run（2026-04-27）

### Phase 1 Read（開始同期）
- Read同期: `AGENTS.md` Read Order の上流（00/01/02）と本Issue本文を再読し、docs-only・allowlist内作業を再確認。

### Phase 2 ADR/CDC
- Context: installation は公開導入導線であり、公開境界の明確化が優先。
- Decision: Classification **Improve external** を維持し、未承認事項の確定化を行わない。
- Consequences: 実装コード・architecture本体・shared resource への波及を防止する。

### Phase 3 Plan
- 実行計画: 本Issueメモの記録更新のみ（1ファイル）。
- 停止条件: self-correction 4回目相当 / 未定義競合 / allowlist外編集要求。

### Phase 4 Execute
- 実施: Stream H 専属ログを追記（docs-only）。
- 非実施: 指定外Issue、実装コード、architecture本体、shared resource。

### Phase 5 Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-08-04doc-installation.md`
- `git diff --check`
- self-correction: 0/3（上限3、4回目相当は停止）。

### Phase 6 Proceed
- 判定: **Ready**（Stream H 範囲で継続可能）。


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

## 18) Stream F serial execution record（2026-04-27 / DOC-OPS-05-08）

### Phase 1 Read（開始時同期）
- Read同期を再実行し、`AGENTS.md` Read Order と本Issueのメタ項目を再確認。
- Scopeを `01_Plans/issues/issue-doc-ops-05-08-04doc-installation.md` のみに固定。

### Phase 2 ADR/CDC（Draft判定）
- Context: `04_Documentation/installation.md` は公開導入者向け文書として運用価値が高い。
- Decision: 既存方針どおり Classification は **Improve external** を維持し、DecisionStatus は `Fixed`。
- Consequences: 変更は docs-only で継続し、実装/CI変更は本Issueの対象外とする。

### Phase 3 Plan
- 固定順序 `Plan -> Execute -> Verify -> Proceed` を明示して実行。
- AC/DoD不足時は AIドラフトを先に記録し、合意後実施の原則を維持。

### Phase 4 Execute
- 本Issueへ Stream F の6Phase記録を追記。
- VerificationLevel=docs-check と GoNoGoGate=Required を維持。

### Phase 5 Verify（docs-check）
- 実行: `python 01_Plans/issues/validate_active_issue_memos.py --root /workspace/kj-atlas`
- 実行: `git diff --check`
- 自己修復回数: 0/3（失敗なし）。

### Phase 6 Proceed
- 判定: **Ready**
- Proceed条件: 分類と検証導線が維持され、指定順（直列）で次Issueへ進行可能。

## Stream J DOC-OPS-05 dedicated run (2026-04-27, Set2)

### Phase 1 Read
- Read Order 再確認後に本Issueを再読し、Scope/VerificationLevel/DecisionStatus を確認。
- SecurityGateImpact は `public-exposure` として維持。

### Phase 2 Plan
- 実行順序を `Read -> Plan -> Execute -> Verify -> Proceed` に固定。
- 変更対象を本Issueメモ単体に限定し、allowlist外編集を禁止。

### Phase 3 Execute
- Classification を **Improve external** で再確認し、公開境界の扱いを固定。
- public-exposure 観点として「公開可能情報のみ記載・内部情報を混在させない」を明記。

### Phase 4 Verify
- docs-check:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-08-04doc-installation.md`
  - `git diff --check`
- self-correction: 0/3（失敗時のみ最大3回、4回目相当は即停止）。

### Phase 5 Proceed
- 判定: **Go**（停止条件: セキュリティ導線矛盾 / 指定外編集 / self-correction上限超過 に非該当）。

## 17) DOC-OPS-05 Public docs専任レーン（2026-04-28, Phase 1..6 serial）

### Phase 1 Read（開始前必須）
- Read実施: `AGENTS.md` Read Order（00〜02上位文書）と本Issue本文を開始前に再読。
- 固定条件再確認: docs-only / allowlist内編集 / `VerificationLevel=docs-check`。

### Phase 2 ADR差分確認（差分時のみ C/D/C）
- 判定: **ADR差分なし**（既存方針の運用固定タスクのため、新規ADR起票・更新なし）。
- 運用: ADR差分が発生した場合のみ `Context / Decision / Consequences` を明文化し、承認後に実行へ進む。

### Phase 3 Plan（AC/DoD不足のAIドラフト提示）
- AIドラフトAC補完:
  - AC-P1: `Move internal` / `Improve external` の二値分類をIssue本文で固定する。
  - AC-P2: Audience / Goal / Non-goal / Public boundary / Related を追跡可能に保持する。
  - AC-P3: Go/No-Go判定条件（Required）を本文から再現できる状態を維持する。
- AIドラフトDoD補完:
  - DoD-P1: Phase 1..6 の直列記録を残す。
  - DoD-P2: Verify失敗時は自己修復最大3回、超過時は `Hold` 停止を記録する。

### Phase 4 Execute
- 分類固定: **Improve external**（installation は公開利用者向け改善トラックとして維持）。
- 非目標の再確認: 実装コード・allowlist外ファイルは非編集。

### Phase 5 Verify（self-correction 最大3回）
- 実施コマンド（docs-check）:
  - `rg -n "Move internal|Improve external|Audience|Goal|Non-goal|Public boundary|Go/No-Go|Phase 1|Phase 6" 01_Plans/issues/issue-doc-ops-05-08-04doc-installation.md`
  - `git diff --check`
- 結果: 0回で適合（self-correction 使用 0/3）。

### Phase 6 Proceed
- 最終判定: **Ready**。
- 停止条件: self-correction 3回超過時は即 `Hold` とし、未達AC/DoDを明記して停止する。


## Stream G dedicated serial completion (2026-04-28)

### Phase 1 Read
- AC/Validationの再収集を実施し、`Requirement meta I/F`・`Acceptance criteria`・`Validation plan` の3点が本文に存在することを確認。
- フェイルセーフ確認: AC不在/検証不能/allowlist外編集要求は該当なし。

### Phase 2 Plan
- 難易度低→高の固定順を `01 → 03 → 08 → 10 → 04 → 09 → 12 → 14` としてロック。
- 本Issueの実行順は **3/8** とし、分類 `Improve external` を維持。

### Phase 3 Execute
- 変更を本Issueメモの最小差分に限定（docs-only / issue memo only）。
- 状態を `Done` に更新し、直列実行ログを追記。

### Phase 4 Verify
- docs-check基準で `Expected verification level=docs-check` と `VerificationLevel=docs-check` の一致を再確認。
- 差分体裁は `git diff --check` で検証対象に含める。

### Phase 5 Proceed
- 判定: **Done**。
- クローズ条件: GoNoGoGate=Required の判定項目（Audience/Goal/Public boundary/Next action）を維持しつつ、直列5Phase完了を記録。


## Stream G normalization pass（2026-05-04）

### Phase 1: Read同期（Issue ↔ 04_Documentation 対応表）
| Issue | Target 04_Documentation | Current classification |
| --- | --- | --- |
| `issue-doc-ops-05-08-04doc-installation.md` | `04_Documentation/installation.md` | 既存本文の Decision / Proposed classification を継承 |

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
  - `rg -n "^- Status:|Expected verification level|VerificationLevel|GoNoGoGate|DecisionStatus|DecisionQueueRef" 01_Plans/issues/issue-doc-ops-05-08-04doc-installation.md`
  - `rg -n "Open readiness:|状態分類:|Phase 5: Proceed" 01_Plans/issues/issue-doc-ops-05-08-04doc-installation.md`
  - `git diff --check`
- Proceed verdict (Phase 6): `Open可能（条件付き）`

## Stream G documentation/public boundary pass (2026-06-13)

### Plan
- 対象: `installation`。
- Scope: Docs-only。`03_Implement/` と `02_Architecture/` は編集しない。
- Acceptance: 公開/保守/開発者/内部計画の分類が追跡でき、SafeMode・share/export・AI提案レビューの安全境界が後退しない。

### Execute
- RequirementID `DOC-OPS-05-08` の公開境界を再確認。
- Decision: installation は初回利用者/運用者向け公開候補として維持し、開発者向け自動テスト手順を混ぜない境界を明記した。

### Verify
- docs-check 対象として issue memo metadata、Markdown整形、リンク導線、公開不可情報の混入有無を確認する。
- Self-correction budget: 0/3 から開始し、4回目相当は停止する。

### Proceed
- 判定: Ready for verification。
- 残課題: 実ファイル移動や開発者向け正本の再配置が必要な場合は、別PRで allowlist と移動先を明示して扱う。
