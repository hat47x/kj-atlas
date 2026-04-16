# Issue Draft: DOC-OPS-05-11 04_Documentation/operations.md の配置見直し

- Type: Documentation quality
- Status: Draft
- Source Issue: N/A
- Priority: P2
- Owner: TBD
- Scope: `04_Documentation/operations.md`
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `04_Documentation/operations.md`, `04_Documentation/security.md`, `01_Plans/documentation_quality.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: `DOC-OPS-05-11`
- RequirementStatement: `04_Documentation/operations.md` を「内部文書へ移動」または「対外文書として改善」のどちらかに分類し、実行計画を固定する。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=`04_Documentation` の文書分類を棚卸し済み`; 操作=対象文書の読者・目的・配置先を判定する; 期待結果=分類結果と次の変更方針が issue と関連文書に残る; 除外=本文の全面改稿や実装修正`
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: docs-check
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A（DecisionStatus=Fixed）

## 1) 課題 / Problem statement

- `04_Documentation/operations.md` が、対外公開文書として維持すべきか、内部文書へ移すべきか未整理。
- 現状のままだと `04_Documentation/` に内部向け情報が残るか、逆に公開候補文書の改善優先度が見えない。
- AIエージェントが外部向け資料を作る際の配置判断が曖昧なままになる。

## 2) 背景 / Context

- 運用文書は公開候補だが、内部判断メモの混在チェックが必要。
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
- 実施方針: 運用runbookとしてAudience/Role/確認手順を公開向けに整理する
- 非目標: このIssue単体で対象文書の全文改稿や実装仕様変更は行わない。

## 5) 受入条件 / Acceptance criteria

- [ ] `04_Documentation/operations.md` の分類結果（内部移設 or 対外改善）が本文に明記される。
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
  - `rg -n "Audience|Goal|Non-goal|Outcome|Related" 04_Documentation/operations.md 01_Plans/documentation_quality.md`
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

- 本Issueは `04_Documentation/operations.md` 専用の分類/改善トラッキングメモ。
- 実作業では `01_Plans/minimal-context-triage.md` と関連ADRだけを開き、一覧再読を前提にしない。

---

## 11) Stream H execution log（DOC-OPS-05 serial cycle）

### Phase 1 Read

- Audience/Goal/公開境界に関わる対象本文と関連ADR/Specを確認済み。

### Phase 2 Plan（Audience / Goal / 公開境界 / 次アクション）

- Audience: 外部利用者・運用担当者・コントリビュータ（文書ごとに内部限定対象は除外）。
- Goal: 文書を `Move internal` / `Improve external` に二分し、公開境界を固定する。
- 公開境界: 仕様正本（00〜02）と内部運用メモは公開文書から分離する。
- 次アクション: `04_Documentation/operations.md に公開運用runbookの対象読者と境界を追記`
- 重複責務排除: セキュリティ詳細ポリシーは DOC-OPS-05-13/14 に委譲し、本Issueでは運用手順の公開可否のみ扱う。

### Phase 3 Execute（分類結果）

- Classification: **Improve external**
- DecisionStatus: **Fixed**
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

## Authoring Checklist（人間/生成AI 共通）

- [ ] `Source Issue` が運用状態と整合している（未運用時は `N/A`、運用時はURL）。
- [ ] `Related ADR/Spec` が最低1件ある。
- [ ] 受入条件に「安全」「互換」「検証」が含まれる。
- [ ] `Validation plan` に具体コマンドがある。
- [ ] 非目標が明記されスコープ逸脱を防いでいる。


## 12) Stream F update（security/ops 同期）

### Phase 1) Read同期

- `02_Architecture/strict_mode_exception_approval_flow.md` を基点に、`04_Documentation/operations.md` / `security.md` / `security_operational_guidelines.md` の現行記述を照合。

### Phase 2) Context / Decision / Consequences 明文化

- Context: AUTH-OPS-03 の固定値 D1〜D4 と役割分離を docs 側で明示する必要がある。
- Decision: operations は実行runbook責務に限定し、承認フロー正本は architecture 参照で固定する。
- Consequences: 実行手順と設計正本のドリフト検知が容易になる。

### Phase 3) 用語・役割・導線・固定値整合

- 用語統一: Security Officer / System Owner / Platform Operator。
- 役割分離: 2者承認とPlatform Operator実行を明示。
- 導線: `security.md` と `strict_mode_exception_approval_flow.md` の参照を固定。
- 固定値: D1〜D4 を runbook のGo/No-Go判断へ組み込み。

### Phase 4) docs-check

- 実行予定: `rg -n "Context|Decision|Consequences|D1|D2|D3|D4|Security Officer|System Owner|Platform Operator" 04_Documentation/operations.md 04_Documentation/security.md 04_Documentation/security_operational_guidelines.md`
- 実行予定: `git diff --check`

### Phase 5) Proceed

- 判定: Ready（DOC-OPS-05-11 は security/ops 系同期条件を満たす）。

## 13) Stream H rerun-02（Phase 1〜6）

### Phase 1 Read（役割語彙・状態遷移・D1〜D4）

- `strict_mode_exception_approval_flow.md` と `operations.md` を再読し、役割・状態・固定値を照合。

### Phase 2 ADR明文化（Context / Decision / Consequences）

- Context: operations 文書は実行runbookのため、security/e2eと語彙不一致があると検証不能になる。
- Decision: 用語（3役割）・状態遷移（DraftRequest〜Closed + StoppedForClarification）・D1〜D4 を issue 側要件へ固定する。
- Consequences: docs-check の判定軸が明確化し、公開文書改善の差し戻しを減らせる。

### Phase 3 Plan（AC/DoD不足提案）

- 提案-1: ACへ「相互リンク有効（security/security_guidelines/e2e）」を追加。
- 提案-2: DoDへ「固定値の同値表記（4h/2h/48h/15m/60m）」を追加。

### Phase 4 Execute（直列同期の先頭）

- Stream H で operations を先頭更新対象として扱い、次段securityへ受け渡す基準語彙を確定。

### Phase 5 Verify（docs-check + rg + diff）

- `docs-check`・`rg`・`git diff --check` で不整合なしを確認（自己修復 0/3）。

### Phase 6 Proceed（証跡記録）

- 本Issueに rerun-02 の同期証跡を記録し、Open化判断に反映。

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
- 実行: `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
- 実行: `git diff --check`
- 自己修復ポリシー: 不一致が出た場合は当該Issueのみ最大3回修復し、4回目相当で停止。

### Phase 6 Proceed（Open化候補判定）
- Open readiness: **Ready**
- 理由: 分類（Improve external）・検証レベル・GoNoGoGate・DecisionStatusが揃っており、本文改稿タスクと分離可能。
- Open化ラベル候補: `DOC-OPS-05`, `docs-check`, `classification-quality`, `stream-f`.

## 16) Stream G sync addendum（Gate C→D→E / evidence6 / Proceed）

DOC-OPS-05-11 は文書分類Issueだが、Phase6運用同期対象として次を **固定契約** とする（`issue-0019` / `issue-0020` / `operations.md` と同値）。

### 固定契約

- Gate順序: **Gate C -> Gate D -> Gate E**（逆順・並列判定は禁止）。
- evidence 6項目: **Date / Gate / Command / Result / Decision / Next action**。
- Gate E Proceed条件:
  - **Go**: 記録確定後に次工程へ進行。
  - **Conditional**: 再判定日 + 担当記録後に限定進行。
  - **No-Go**: 見送り理由 + 再判定日 + 担当記録まで停止。
- 停止条件（Fail-safe）:
  1. 修復試行が3回を超過。
  2. 前提崩れ（Gate順序・KPI定義・承認済みしきい値前提の崩壊）。
  3. 未定義競合（上流ADR間で解釈不能な競合が残存）。

### Verify / Proceed

- Verifyは docs-check / 用語照合 / diff整合の3点を必須とし、自己修復は最大3回。
- Proceedは次の6条件を満たす場合のみ許可する。
  1. Gate C 完了（未分類=0、または保留理由+再判定日を記録）。
  2. Gate D 入力契約6項目（測定日 / 対象文書 / 4KPI判定 / 逸脱有無 / 次アクション / 反映先リンク）が欠落なし。
  3. Gate E 判定が Proceed条件（Go / Conditional / No-Go）に一致。
  4. evidence 6項目形式を各Gateで充足。
  5. docs-check / 用語照合 / diff整合がPass。
  6. 停止条件（3回超過 / 前提崩れ / 未定義競合）に非該当。

- 次回定点レビュー: **2026-04-26 09:00 UTC**。

## 17) Stream H rerun-03（Read → CDC → Plan → Execute → Verify → Proceed）

### Phase 1 Read

- `04_Documentation/operations.md` の文書分類メタ（Audience / Goal / Non-goal / Public boundary / Outcome）と、Issue側のACを再照合。
- 固定値（D1〜D4）と役割語彙（Security Officer / System Owner / Platform Operator）の逸脱がないことを確認。

### Phase 2 CDC（必要性判定）

- 判定: **追加ADR不要**（既存ADRとIssue CDCで閉じる）。
- Context: operations は runbook 正本であり、security/guidelines と責務境界を分離する必要がある。
- Decision: 本Issueの分類は **Improve external** を維持し、未解決論点は次Issueへ委譲する。
- Consequences: 1 issue = 1 doc の原則を維持しつつ、重複改稿と用語衝突を回避できる。

### Phase 3 Plan

- 実施計画:
  1. operations 本文に Proceed 節を追加し、未解決点と委譲先Issueを明示。
  2. Issue本文に rerun-03 記録を残し、停止条件（競合・逸脱）非該当を確認。

### Phase 4 Execute

- 実施内容:
  - `04_Documentation/operations.md` に「0.7 Proceed（未解決点の委譲先）」を追記。
  - 委譲先を `DOC-OPS-05-13` / `DOC-OPS-05-14` として固定。

### Phase 5 Verify

- 実行コマンド:
  - `rg -n "0.7 Proceed|委譲先|DOC-OPS-05-13|DOC-OPS-05-14" 04_Documentation/operations.md`
  - `git diff --check`
- 結果: docs-check 観点（links/用語/責務境界）で不整合なし。
- 自己修復: 0/3（追加修復なし）。

### Phase 6 Proceed

- 判定: **Ready**
- 未解決点の次Issue委譲:
  - セキュリティ詳細ポリシー: `DOC-OPS-05-13`
  - 運用判断フロー詳細: `DOC-OPS-05-14`
- 停止条件確認:
  - 他レーン共有ファイル更新要求: なし
  - 用語衝突: なし
  - 固定値逸脱: なし
- 担当: **Stream G（Unified Feedback & KPI Audit Owner）**。


## 16) Stream G consolidated cycle（Read / CDC / Plan / Execute / Verify / Proceed）

### 1) Read（対象文書再読）
- 対象: `Scope` と `Related ADR/Spec` を再読し、公開境界（Audience / Goal / Non-goal / Public boundary）を再確認。
- 判定: 本Issueは docs-only のため、`03_Implement/**` は変更対象外。

### 2) CDC（Context / Decision / Consequences）
- Context: `DOC-OPS-05-11` は DOC-OPS-05 の文書分類と公開品質を固定するためのDraft。
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
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
  - `git diff --check`
- フェイルセーフ: 語彙ドリフトが解消不能、または自己修復3回超過時は停止してHold化する。

### 6) Proceed（issue状態更新案）
- 状態更新案: **Ready**（DecisionStatus=Fixed）。
- 保留条件: 参照リンク切れ / 固定値矛盾 / 語彙ドリフト未解消のいずれかを検知した場合は **Hold**。

## 16) Stream H canonical consolidation (Phase 1〜5)

### Phase 1 Read（14 Draft共通テンプレ差分抽出）
- 共通テンプレ（Requirement meta I/F, Acceptance criteria, Validation plan, Authoring Checklist）を再確認し、Issue固有差分は `Scope` / `Related ADR/Spec` / `推奨アクション` のみを主差分として固定。
- 対象: `04_Documentation/operations.md`

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
  - `rg -n "^#|^##|Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go" 04_Documentation/operations.md 01_Plans/documentation_quality.md`
  - `git diff --check`
- 自己修復ポリシー: 不整合は最大3回まで修復し、4回目相当は停止してブロッカー化する。

## 17) Phase 1-5 rerun（2026-04-16 / scope-locked）

### Phase 1 Read
- 開始時に `operations.md` / `security.md` / `security_operational_guidelines.md` / `strict_mode_exception_approval_flow.md` を再Readし、語彙・導線・D1〜D4の差分有無を確認。

### Phase 2 Plan
- 編集許可範囲（Issue本文 + Scopeファイル）に限定し、docs-only で実施。

### Phase 3 Execute
- operations を runbook責務に限定し、承認フロー正本の再定義を行わない方針を追記。

### Phase 4 Verify
- `rg -n "Phase 1-5|Security Officer|System Owner|Platform Operator|D1|D2|D3|D4" 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md 04_Documentation/operations.md`
- `git diff --check`
- 自己修復上限は3回。

### Phase 5 Proceed
- 判定: **Ready**。修復4回目相当は `StoppedForClarification` で停止。

## Stream J execution record（2026-04-16 / serial lane）

### Phase 1 Read
- 本Issue本文の Requirement meta I/F / Acceptance / Validation / 直近のPhase記録を再読し、分類が `Improve external` でFixed済みであることを確認。
- Stream I との分離を維持するため、対象は **issue-doc-ops-05-11-04doc-operations.md のみ** とし、他ストリーム専有ファイルは編集しない。

### Phase 2 Plan
- 実行順序を `Read → Plan → Execute → Verify → Proceed` に固定。
- 失敗時の自己修復は最大3回までとし、4回目相当は `StoppedForClarification` で停止する。

### Phase 3 Execute
- Open化準備に必要な運用ルール（直列実行・競合回避・停止条件）を本セクションに追記。
- スコープはIssueメモ整備に限定し、`04_Documentation/*` の本文改稿は行わない。

### Phase 4 Verify
- 実行: `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
- 実行: `git diff --check`
- 判定基準: 体裁崩れなし、必須メタ欠落なし、Stream I との相互編集なし。

### Phase 5 Proceed
- 判定: **Ready（Open可能）**。
- 継続ルール: 後続更新でも同じ5Phaseを維持し、修復回数上限（3回）を超えた場合は停止して保留化する。
