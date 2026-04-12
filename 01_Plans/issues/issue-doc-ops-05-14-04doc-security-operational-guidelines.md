# Issue Draft: DOC-OPS-05-14 04_Documentation/security_operational_guidelines.md の配置見直し

- Type: Documentation quality
- Status: Draft
- Source Issue: N/A
- Priority: P2
- Owner: TBD
- Scope: `04_Documentation/security_operational_guidelines.md`
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `04_Documentation/security_operational_guidelines.md`, `04_Documentation/security.md`, `01_Plans/documentation_quality.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: `DOC-OPS-05-14`
- RequirementStatement: `04_Documentation/security_operational_guidelines.md` を「内部文書へ移動」または「対外文書として改善」のどちらかに分類し、実行計画を固定する。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=`04_Documentation` の文書分類を棚卸し済み`; 操作=対象文書の読者・目的・配置先を判定する; 期待結果=分類結果と次の変更方針が issue と関連文書に残る; 除外=本文の全面改稿や実装修正`
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: docs-check
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A（DecisionStatus=Fixed）

## 1) 課題 / Problem statement

- `04_Documentation/security_operational_guidelines.md` が、対外公開文書として維持すべきか、内部文書へ移すべきか未整理。
- 現状のままだと `04_Documentation/` に内部向け情報が残るか、逆に公開候補文書の改善優先度が見えない。
- AIエージェントが外部向け資料を作る際の配置判断が曖昧なままになる。

## 2) 背景 / Context

- 運用ガイドは外部利用者向けに整備できるが、内部承認情報の切り分けが必要。
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
- 実施方針: 運用判断補助ガイドとして公開可能な範囲へ整形する
- 非目標: このIssue単体で対象文書の全文改稿や実装仕様変更は行わない。

## 5) 受入条件 / Acceptance criteria

- [ ] `04_Documentation/security_operational_guidelines.md` の分類結果（内部移設 or 対外改善）が本文に明記される。
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
  - `rg -n "Audience|Goal|Non-goal|Outcome|Related" 04_Documentation/security_operational_guidelines.md 01_Plans/documentation_quality.md`
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

- 本Issueは `04_Documentation/security_operational_guidelines.md` 専用の分類/改善トラッキングメモ。
- 実作業では `01_Plans/minimal-context-triage.md` と関連ADRだけを開き、一覧再読を前提にしない。

---

## 11) Stream H execution log（DOC-OPS-05 serial cycle）

### Phase 1 Read

- Audience/Goal/公開境界に関わる対象本文と関連ADR/Specを確認済み。

### Phase 2 Plan（Audience / Goal / 公開境界 / 次アクション）

- Audience: 外部利用者・運用担当者・コントリビュータ（文書ごとに内部限定対象は除外）。
- Goal: 文書を `Move internal` / `Improve external` に二分し、公開境界を固定する。
- 公開境界: 仕様正本（00〜02）と内部運用メモは公開文書から分離する。
- 次アクション: `04_Documentation/security_operational_guidelines.md に公開版運用判断フローと内部専用情報の分離基準を追記`
- 重複責務排除: 基底脅威モデルの説明は DOC-OPS-05-13 に委譲し、本Issueでは運用判断ガイドの公開可否のみ扱う。

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

- 状態分類: **Open候補（Securityレビュー前提）**
- Open準備判定: Audience/Goal/公開境界/Validation/Non-goal が充足しており、依存なしで起票可能。

## 12) Stream J 棚卸し（Set 3: Issue Open化条件整備）

### 12.1 対象Issue棚卸し（依存整理）

- DOC-OPS-05-14（本Issue / `security_operational_guidelines.md`）: **本ストリームでOpen条件を明文化**。
- DOC-OPS-05-09（`local_llm_ops_guide.md`）: F担当領域のため **読み取りのみ**（編集しない）。
- DOC-OPS-05-13（`security.md`）: G担当領域のため **編集禁止**（依存先として参照のみ）。

### 12.2 Open化ゲート（J確定）

- Gate J-1（Scope固定）: 本Issueの変更対象は「Issue本文のOpen条件整備」に限定し、`04_Documentation/security_operational_guidelines.md` 本文改稿は行わない。
- Gate J-2（競合回避）: `DOC-OPS-05-09` / `DOC-OPS-05-13` の本文編集を行わない。
- Gate J-3（受入整合）: Audience / Goal / 公開境界 / Validation / Non-goal がIssue本文で追跡可能。
- Gate J-4（依存整合）: 基底方針は `DOC-OPS-05-13`、LLM運用境界は `DOC-OPS-05-09` に委譲し、重複改稿を避ける。
- Gate J-5（起票準備）: Open後は「公開向け運用判断フローの改善PR」に限定して着手し、分類再判定（Move/Improve）は行わない。

### 12.3 Open判定（Stream J）

- 判定: **Ready（Open可能）**
- 理由: 分類は `Improve external` でFixed済み、かつJゲート（J-1〜J-5）により競合回避と依存分離を確認。

## Authoring Checklist（人間/生成AI 共通）

- [ ] `Source Issue` が運用状態と整合している（未運用時は `N/A`、運用時はURL）。
- [ ] `Related ADR/Spec` が最低1件ある。
- [ ] 受入条件に「安全」「互換」「検証」が含まれる。
- [ ] `Validation plan` に具体コマンドがある。
- [ ] 非目標が明記されスコープ逸脱を防いでいる。


## 13) Stream F update（security/ops 同期）

### Phase 1) Read同期

- `strict_mode_exception_approval_flow.md` を起点に、security/operations との責務分離と導線を突合。

### Phase 2) Context / Decision / Consequences 明文化

- Context: 本Issue対象は運用判断ガイドであり、承認フロー仕様の再定義を避ける必要がある。
- Decision: 文書冒頭に DOC-OPS-05 分類と CDC を追加し、D1〜D4 を確認項目として固定する。
- Consequences: 運用判断時に「どの文書を正本にするか」の迷いを削減できる。

### Phase 3) 用語・役割・導線・固定値整合

- 用語統一: Security Officer / System Owner / Platform Operator。
- 役割分離: 2者承認と実行責務分離を維持。
- 導線: `security.md`（基底方針）と `operations.md`（実行runbook）へ接続。
- 固定値: D1〜D4 チェック節を新設し、停止条件（StoppedForClarification）を明記。

### Phase 4) docs-check

- 実行予定: `rg -n "Context|Decision|Consequences|D1|D2|D3|D4|Security Officer|System Owner|Platform Operator" 04_Documentation/security_operational_guidelines.md 04_Documentation/security.md 04_Documentation/operations.md`
- 実行予定: `git diff --check`

### Phase 5) Proceed

- 判定: Ready（DOC-OPS-05-14 は security/ops 系の公開ガイドとしてOpen可能）。

## 14) Stream H rerun-02（Phase 1〜6）

### Phase 1 Read（役割語彙・状態遷移・D1〜D4）

- `strict_mode_exception_approval_flow.md` と `security_operational_guidelines.md`、関連3文書を再読。

### Phase 2 ADR明文化（Context / Decision / Consequences）

- Context: ガイド文書は運用判断の参照起点であり、固定値や状態名の不一致が判断ブレを生む。
- Decision: D1〜D4 と `StoppedForClarification` を含む状態語彙を明示し、security/operations/e2e への導線を固定する。
- Consequences: プロファイル選択時の判断差は減るが、AUTH-OPS-03更新時の同期責務が増える。

### Phase 3 Plan（AC/DoD不足提案）

- 提案-1: ACへ「役割語彙3種の一致確認」を追加。
- 提案-2: DoDへ「相互リンク + 固定値同値表記」を追加。

### Phase 4 Execute（直列同期の補助ガイド段）

- operations -> security 更新後の整合状態を受け、guidelines で運用判断チェック項目を同期。

### Phase 5 Verify（docs-check + rg + diff）

- docs-check と rg照合で不一致なし、修復回数 0/3 を確認。

### Phase 6 Proceed（証跡記録）

- 本Issueへ rerun-02 同期証跡を追記し、次回同期の再利用基準を固定。

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
- 実行: `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-14-04doc-security-operational-guidelines.md`
- 実行: `git diff --check`
- 自己修復ポリシー: 不一致が出た場合は当該Issueのみ最大3回修復し、4回目相当で停止。

### Phase 6 Proceed（Open化候補判定）
- Open readiness: **Ready**
- 理由: 分類（Improve external）・検証レベル・GoNoGoGate・DecisionStatusが揃っており、本文改稿タスクと分離可能。
- Open化ラベル候補: `DOC-OPS-05`, `docs-check`, `classification-quality`, `stream-f`.

## 16) 同一ワークフロー固定（safeMode/漏洩防止後退禁止）

- Workflow固定: **Plan → Execute → Verify → Proceed**
- Verify失敗時: 最小差分で自己修復し、**最大3回**まで再試行。4回目相当は fail-safe 停止。
- 後退禁止:
  - safeMode既定ONを弱める記述
  - share/export 漏洩防止を緩和する記述
  - review自動昇格 / auto-apply を許容する記述

## 17) Stream H 専任サイクル（DOC-OPS-05-14 / P1→P6）

### P1 Read（対象文書再読・必須）

- 再読対象: `04_Documentation/security_operational_guidelines.md`（本Issueの単一対象）。
- 再読確認点: Classification=`Improve external`、Audience/Goal/Non-goal/Public boundary の明示、D1〜D4固定値、SafeMode後退禁止。

### P2 ADR CDC（Context / Decision / Consequences）

- Context: 公開可能な運用ガイドとして維持しつつ、承認フロー正本の再定義は回避する必要がある。
- Decision: 本Issueは docs-only の公開品質改善に限定し、設計正本は `02_Architecture/strict_mode_exception_approval_flow.md` を参照する。
- Consequences: security/operations との責務分離が明確になり、Open化時の差し戻し理由を「公開境界/固定値不一致」に限定できる。

### P3 Plan

- AC固定:
  1. Audience/Goal/Non-goal/Public boundary を対象文書に保持。
  2. D1〜D4・役割語彙3種（Security Officer / System Owner / Platform Operator）を維持。
  3. Verify失敗時の自己修復上限3回を明記。
- Non-goal: 実装コード変更、`operations.md` 変更、他Issue改稿。

### P4 Execute

- 実施内容: 本Issueへ Stream H のP1〜P6記録を追記し、運用手順をフェーズ名で固定。
- スコープ適合: `issue-doc-ops-05-14-*` と単一対象文書のみ。

### P5 Verify

- 実行コマンド:
  - `rg -n "^## 17\\) Stream H 専任サイクル|^## 9\\. DOC-OPS-05 Stream H 専任サイクル|P1 Read|P2 ADR CDC|P3 Plan|P4 Execute|P5 Verify|P6 Proceed" 01_Plans/issues/issue-doc-ops-05-14-04doc-security-operational-guidelines.md 04_Documentation/security_operational_guidelines.md`
  - `git diff --check`
- 判定: docs-check の範囲で差分整合を確認。

### P6 Proceed

- 判定: **Ready**
- フェイルセーフ:
  - 3回超過（自己修復4回目相当）で停止。
  - 用語ドリフト（役割語彙/D1〜D4）未収束で停止。
  - スコープ競合（03_Implement、`operations.md`、他Stream専有領域）検出時は停止。
