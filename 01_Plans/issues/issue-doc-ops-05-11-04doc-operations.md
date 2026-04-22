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

## 19) Stream E execution log（2026-04-20, DOC-OPS-05文書改訂のみ）

### Phase 1) Read（対象文書とissue memo同期確認）

- 対象: `04_Documentation/operations.md` と本Issueを再読し、Classification=`Improve external` / DecisionStatus=`Fixed` を確認。
- 同期確認: 既存のGo/No-Go、Gate C→D→E、Fail-safe（3回超過 / 前提崩れ / 未定義競合）記述が残っていることを確認。
- スコープ確認: docs-only を維持し、編集禁止対象（`03_Implement/**` 等）へ非接触で進行。

### Phase 2) Plan（AC/DoD起案）

- AC-E1: `operations.md` に **Known gap** を明示し、不足情報を推測で補完しないこと。
- AC-E2: 各 Known gap に「理由」と「委譲先」を明記し、次タスク導線を固定すること。
- DoD-E1: docs-check（`rg` / `validate_active_issue_memos.py` / `git diff --check`）で整合が再現可能であること。

### Phase 3) Execute（文書更新）

- `04_Documentation/operations.md` に `0.8 Known gap（DOC-OPS-05 / Stream E）` を追加。
- 追記内容は Gap-1〜Gap-3（環境別runbook詳細、KPIしきい値台帳連携、AUTH-OPS-03将来差分テンプレ未定義）を明示。
- 推測補完を避けるため、すべて「理由 + 委譲先」を付与した。

### Phase 4) Verify（docs-check, link整合）

- 実行:
  - `rg -n "Known gap|Gap-1|Gap-2|Gap-3|委譲先" 04_Documentation/operations.md 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `git diff --check`
- 判定: 失敗なし。自己修復は 0/3 回。

### Phase 5) Proceed（次タスク明記）

- 状態: **Ready**
- 次タスク:
  1. DOC-OPS-05-13 / 14 側で、operations の Known gap 参照リンクを追加して委譲導線を双方向化する。
  2. 環境別runbookの必要性を別Issue化（single-node / HA / air-gapped）し、公開境界を再判定する。
- フェイルセーフ: 規約不整合・未定義競合・自己修復3回超過を検知した場合は停止して保留化する。

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


## 18) Stream G rerun-03（2026-04-17, canonical語彙収束）

### Phase 1 Read
- `strict_mode_exception_approval_flow.md` を正本として D1〜D4 / 役割語彙 / 状態語彙を再読した。

### Phase 2 ADR CDC
- 方針変更なし（固定値維持）のため CDC/ADR 追加は不要と判断した。

### Phase 3 Plan（AC/DoD）
- AC: `operations.md` の状態語彙を canonical（DraftRequest/ApprovalPending/Approved/ActiveException/RollbackPending/Closed/StoppedForClarification）へ統一。
- DoD: 役割分離と固定値（4h/2h/代理承認なし/48h+15m/60m）を保持し、docs-check成功。

### Phase 4 Execute
- `Requested` / `ExceptionActive` の表記を canonical 状態語彙へ置換し、runbook時系列を再編成した。

### Phase 5 Verify
- `rg -n "Requested|ExceptionActive|DraftRequest|ApprovalPending|ActiveException|StoppedForClarification" 04_Documentation/operations.md`
- `git diff --check`

### Phase 6 Proceed
- 判定: **Ready**（語彙ドリフト0）。

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
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
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
- 次実行単位（固定）: `04_Documentation/operations.md` の運用runbookを公開向け最小手順 + 内部参照分離で改善するPRを起票する。

### Phase 5 Verify（docs-check整合 / 修復上限3回）
- 実行: `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
- 実行: `git diff --check`
- 判定: 失敗時は同Issue内修復を最大3回まで。4回目相当は Fail-safe に従い停止。

### Phase 6 Proceed（Ready化候補）
- 状態: **Ready**
- Ready化条件: Classification固定・AC/DoD不足ドラフト記録・次実行単位固定・Verification手順固定を満たす。
- Fail-safe確認: 分類不能/競合方針/scope外編集要求は未検出。

## 20) Stream G dedicated cycle（2026-04-19 / 1 issue : 1 doc）

### Phase 1 Read
- `issue-doc-ops-05-11-04doc-operations.md` と `04_Documentation/operations.md` のみ再Readし、担当外docは非参照・非編集を確認。

### Phase 2 Plan（内部移動 or 対外改善）
- 判定方針: 既存分類 `Improve external` を維持し、公開runbookとしての可読性/再現性を最小差分で補強する。
- スコープ固定: `1 issue : 1 doc` を維持し、同一PRで他docを混在させない。

### Phase 3 Execute（最小差分）
- issue側には本サイクルの証跡のみ追記し、分類・優先度・検証レベルなどの既存決定は変更しない。
- 追加方針変更なしのため、ADR新規起票は不要（既存 CDC を継続利用）。

### Phase 4 Verify（docs-check）
- 実行: `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
- 実行: `rg -n "DOC-OPS-05-11|Improve external|Phase 1 Read|Phase 5 Proceed" 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md 04_Documentation/operations.md`
- 実行: `git diff --check`
- 判定: 失敗時の自己修復は最大3回。3回超過時は `StoppedForClarification` で停止。

### Phase 5 Proceed（次担当への引継ぎメモ）
- 判定: **Ready**
- 引継ぎ: 次担当は `operations.md` 本文の既存runbook節を維持しつつ、内部限定情報混入の有無のみを重点監査する。
- フェイルセーフ: 担当外doc編集要求・分類未合意・検証3回超過のいずれかで停止する。

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
- `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go|Stream J（DOC-OPS-05 中盤2）" 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md 04_Documentation/operations.md`
- `git diff --check`

### Phase 6 Proceed
- 判定: **Ready**。
- 次アクション: 後続担当は本Issueと対応ドキュメントをPhase開始時に再読し、差分競合がある場合は即停止して判断依頼。

## Stream I phase execution record（2026-04-19 / DOC-OPS-05-11）

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
- Read Order の上流（`00_Prompt/system_prompt.md` / `00_Prompt/domain.md` / `01_Plans/adr/ADR-0001-value-to-requirements.md`）と、対象Scope（`04doc_operations.md`）の境界を突合。
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
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
  - `git diff --check`
- 失敗時ロールバック:
  1. 当該Issueのみ最小差分で自己修復（最大3回）。
  2. 4回目相当は **即停止** し、状態を `Hold` に変更。
  3. 停止理由を「公開境界の曖昧化」または「承認なし確定化の疑い」として記録。

### Phase 5) Verify / Proceed
- Verify判定: docs-checkで不整合がない場合のみ `Ready`。
- Proceed条件: 公開境界を曖昧化せず、承認なしで確定化していないこと。
- Fail-safe再掲: 公開境界の曖昧化・承認なし確定化を検知した時点で作業を停止する。

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
- `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
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
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
  - `git diff --check`
- 自己修復上限: 3回。4回目相当は Stopper に従い停止。

### Phase 5) Proceed（次の1手 / 未解決点）
- 次の1手: `04_Documentation/operations.md` に運用runbookの役割分離（Security Officer/System Owner/Platform Operator）導線を反映。
- 未解決点: 未解決なし（DecisionStatus=Fixed）。
- Stopper確認: 未定義競合なし / safeMode後退語彙なし / 自己修復回数は上限内。

## DOC-OPS-05 Lane Update (2026-04-20)

### Phase 1) Read（対象Issueの現状・関連Spec確認）
- 対象: `issue-doc-ops-05-11-04doc-operations.md`（Draft memoのみ）。
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

## 17) Stream Z fixed cycle（Phase 1 Read → Phase 5 Verify/Proceed）

### Phase 1 Read（operations/security系の相互参照と公開境界の再確認）

- 対象: `04_Documentation/operations.md`
- Cross-reference確認: `04_Documentation/security.md` / `04_Documentation/security_operational_guidelines.md` / `02_Architecture/strict_mode_exception_approval_flow.md`
- 公開境界確認: Audience / Goal / Non-goal / Public boundary が本文で追跡可能であること。

### Phase 2 ADR CDC（変更時のみ・承認待ち管理）

- Rule: **差分が発生した場合のみ** Context / Decision / Consequences を追記する。
- Rule: 変更提案は `DecisionStatus=Pending` とし、承認完了まで `Fixed` へ更新しない。
- Rule: 変更なしの場合は「CDC追加なし（既存合意を維持）」を明記する。

### Phase 3 Plan（固定キー）

- SecurityGateImpact: **public-exposure（固定）**
- GoNoGoGate: **Required（固定）**
- DecisionStatus: **Fixed / Pending の二値で管理（固定）**

### Phase 4 Execute（役割語彙 / 固定値 / 導線の整合）

- 役割語彙: `Security Officer / System Owner / Platform Operator` を統一する。
- 固定値: D1〜D4（4h / 2h / 代理承認なし / 48h + 15m/60m）と矛盾しないことを確認する。
- 導線: `strict_mode_exception_approval_flow.md -> security.md -> security_operational_guidelines.md -> e2e_testing.md` を保持し、`operations.md` は runbook 整合確認先として併記する。
- Execute outcome: operations.md を runbook 単一責務で維持しつつ、security系導線の公開境界を明確化する。

### Phase 5 Verify / Proceed（docs-check・停止条件）

- Verify command:
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
  - `git diff --check`
- Proceed条件: docs-check 成功かつ Go/No-Go 判定が Go の場合のみ次Issueへ進行する。
- 停止条件: **自己修復3回超過** または **前提崩壊（公開境界破綻 / 上流正本との矛盾）** を検知した場合は停止し、`StoppedForClarification` として記録する。

## 18) Stream J serial execution record（Phase 1-5 strict）

### Phase 1: Read（開始時Read必須）
- 開始時Read（Read Order上流）: `00_Prompt/system_prompt.md` → `00_Prompt/domain.md` → `00_Prompt/handoff.md` → `00_Prompt/agent_handover.md` → `00_Prompt/codex_gsd_skill_ops.md` → `00_Prompt/ai_cognitive_externalization_requirements.md`。
- 判断軸Read: `01_Plans/adr/ADR-0001-value-to-requirements.md` / `02_Architecture/architecture.md` / `02_Architecture/schemas.md`。
- Issue固有Read: `Scope=04_Documentation/operations.md` と `Related ADR/Spec`、`Requirement meta I/F` を再確認し、`VerificationLevel=docs-check` を固定。

### Phase 2: Plan
- 単一責務: `DOC-OPS-05-11` のIssueメモ品質を **Phase 1-5 直列処理** に正規化する。
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
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
  - `git diff --check`
- 判定基準: メタI/F欠落なし・体裁崩れなし・5Phase記録が同一Issue内で完結。

### Phase 5: Proceed
- 判定: **Ready**
- 理由: 開始時Read、Plan→Execute→Verify→Proceed の直列記録を同一Issueで完結済み。
- 次アクション: 対応する `04_Documentation/*` 本文改稿PRを docs-only で分離実施する。

## 17) Stream I execution log（DOC-OPS-05 後半 / serial）

### Phase 1 Read（Scope / Related ADR / Spec / DecisionStatus）
- Scope再確認: `04_Documentation/operations.md` の分類・公開境界の固定（docs-only）。
- Related再確認: `04_Documentation/operations.md` / `04_Documentation/security.md` / `01_Plans/documentation_quality.md`。
- DecisionStatus確認: `Fixed` を維持（分類再判定はしない）。

### Phase 2 Plan（AC/DoD不足提案の固定）
- AC追加固定:
  - `public-exposure` 観点で、公開対象/内部限定情報の境界を本文で追跡可能にする。
  - `GoNoGoGate=Required` の判定根拠（Audience / Goal / 公開境界 / 次アクション）を欠落なく記録する。
- DoD追加固定:
  - Proceed判定を `Ready / Hold / Needs-decision` の三値で明示する。
  - SafeMode既定ON・share/export漏えい防止を後退させる記述を追加しない。

### Phase 3 ADR CDC（必要時のみ）
- 判定: 追加ADRは **不要**（既存Issue内CDCで十分）。
- Context: 本Issueは分類メモ品質の固定であり、仕様変更は含まない。
- Decision: `Improve external` と `DecisionStatus=Fixed` を維持。
- Consequences: 後続の公開runbook改善PRで参照可能な判定証跡を確保。

### Phase 4 Execute（このIssueファイルのみ更新）
- 実施: Stream Iログを本Issueへ追記し、AC/DoD補強と安全境界維持条件を明文化。
- 非実施: `04_Documentation/*` 本文、shared resource、実装コード。

### Phase 5 Verify / Proceed
- docs-check: `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
- formatting: `git diff --check`
- 自己修復ポリシー: 不整合時は当該Issueのみ最大3回まで修復し、4回目相当で停止。
- Proceed判定: **Ready**（致命的矛盾・未定義競合・前提崩壊なし）。


## 18) Stream K execution log（Phase固定: Read→Plan→Execute→Verify→Proceed）

### Phase 1 Read（同期: 対象ファイル再読）
- 再読対象: `issue-doc-ops-05-11-04doc-operations.md`。
- 確認: Scope/Requirement meta I/F/DecisionStatus=Fixed/VerificationLevel=docs-check を再確認。

### Phase 2 Plan（AC/DoD補完）
- AC補完: Audience・Goal・公開境界・次アクションの4点が追跡可能であることを明文化。
- DoD補完: Proceed判定を `Ready / Hold / Needs-decision` で明示し、GoNoGoGate=Required の判定根拠を残す。

### Phase 3 Execute（指定範囲のみ）
- 実施: Stream K の5Phase証跡を本Issueへ追記。
- 非実施: 指定外ファイル編集、`04_Documentation/*` 本文改稿、実装コード変更。

### Phase 4 Verify（自己修復上限3回）
- 実行: `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
- 実行: `git diff --check`
- 自己修復規則: 不整合時は当該Issueのみ最大3回まで修復し、4回目相当は停止して指示待ち。

### Phase 5 Proceed
- 判定: **Ready**
- 理由: 5Phaseの直列実行・AC/DoD補完・docs-check整合を同一Issue内で完結。


## 16) DOC-OPS-05 back-half serial execution record（Phase 1〜5）

### Phase 1 Read
- `Requirement meta I/F`、既存分類（Improve external）、ValidationLevel（docs-check）を再確認。
- 関連正本（`01_Plans/documentation_quality.md` と `04_Documentation/operations.md` の対応）を確認。

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
- 実施コマンド: `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
- 結果: 体裁崩れなし、自己修復回数 0/3。

### Phase 5 Proceed
- 判定: **Ready**
- 次アクション: 本Issueに対応する docs-only PR へ進行可能。未定義競合・前提崩壊が発生した場合は即停止して指示待ち。

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

## 18) Stream専有 3点セット直列処理（Phase 1〜5）

### Phase 1 Read（3ファイル差分確認）

- 対象を本Issueを含む専有3ファイルに固定し、他Issue/他層は編集対象外とする。
- `DecisionStatus=Fixed` / `Classification=Improve external` / `VerificationLevel=docs-check` の現値を再確認。

### Phase 2 Plan（公開/内部分類の判断基準固定）

- 分類判定基準（固定）:
  1. Audience が外部利用者/運用担当者を含む場合は `Improve external` を優先。
  2. 内部承認メモ・秘密情報・実装詳細のみで成立する場合のみ `Move internal` を許可。
  3. SafeMode既定ON・share/export漏洩防止の後退を伴う分類変更は禁止。
- Proceed判定は `Ready / Hold / Needs-decision` の三値で記録する。

### Phase 3 Execute（方針整合）

- 本Issueの分類は **Improve external（Fixed）** を維持する。
- 実行方針: `04_Documentation/operations.md` を公開runbook改善対象として維持（Move internal へ再分類しない）。
- 非目標: 対象外ファイル編集、仕様正本（00〜02）改変、実装コード修正。

### Phase 4 Verify（docs-check）

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
  - `git diff --check`
- 失敗時ポリシー: 競合検知 / 前提崩壊 / 自己修復3回超過のいずれかで停止。

### Phase 5 Proceed

- 現在判定: **Ready**（分類基準固定・方針整合・docs-check実施可能）。
- 次アクション: 専有3ファイルの直列処理を維持し、対象外編集は実施しない。

## 17) Stream J lane execution log（DOC-OPS-05 security/ops, 2026-04-22）

### Phase 1 Read（Scope / Related ADR/Spec / 語彙・導線整合）

- 再読対象: `Scope`、`Related ADR/Spec`、既存の Stream H/F/G ログ。
- 前提差分: Classification=`Improve external` / DecisionStatus=`Fixed` は維持、`operations -> security -> security_operational_guidelines` の直列順を本laneで固定。
- 語彙・導線: Security Officer / System Owner / Platform Operator、および strict mode 参照導線を維持。

### Phase 2 ADR/CDC consensus（必須）

- Context: DOC-OPS-05 security/ops lane は公開境界を崩さず、Issueメモの運用手順を直列固定する必要がある。
- Decision: 本Issueは operations 先頭として、後段（05-13, 05-14）へ引き渡す基準（語彙・Gate・Verify上限）を定義する。
- Consequences: docs-check 失敗時の自己修復上限3回、未解決競合時停止を明示できる。
- Held/Pending（未承認事項）:
  - Pending-1: `Ready/Hold/Needs-decision` の最終運用ラベル名は横断運用で変更余地あり（本Issueでは確定しない）。

### Phase 3 Plan（AC/DoDドラフトと合意）

- AC/DoDドラフト提案:
  1. AC: operations は security/guide への直列引き渡し条件（語彙一致・固定値参照）を保持する。
  2. AC: Verify は docs-check + `git diff --check` を必須とする。
  3. DoD: 自己修復は最大3回、4回目相当で Stop を明記する。
- 合意状態: **Agreed**（本依頼の Stream J 専任指示を合意根拠として採用）。

### Phase 4 Execute（operations -> security -> guidelines の先頭）

- 実施内容: 本Issueに Stream J フェーズ記録を追加。
- スコープ確認: 本ファイルのみ更新（指定外ファイルは未編集）。

### Phase 5 Verify / Proceed / Stop

- Verify実行:
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
  - `git diff --check`
- Self-correction policy: 失敗時は本Issue内で最大3回まで修正、4回目相当で停止。
- Proceed判定: **Proceed（security へ）**。

## 16) DOC-OPS-05 dedicated serial run (2026-04-22)

### Phase 1 Read
- 対象Issue `DOC-OPS-05-11` の最新本文（Requirement meta I/F / AC / Validation plan）を再確認。
- Scope対象文書 `04_Documentation/operations.md` を read-only 参照し、公開境界・読者・目的の現状を確認。
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
