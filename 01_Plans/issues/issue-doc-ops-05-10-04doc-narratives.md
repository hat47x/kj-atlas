# Issue Draft: DOC-OPS-05-10 04_Documentation/narratives.md の配置見直し

- Type: Documentation quality
- Status: Draft
- Source Issue: N/A
- Priority: P2
- Owner: TBD
- Scope: `04_Documentation/narratives.md`
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `04_Documentation/narratives.md`, `00_Prompt/domain.md`, `01_Plans/documentation_quality.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: `DOC-OPS-05-10`
- RequirementStatement: `04_Documentation/narratives.md` を「内部文書へ移動」または「対外文書として改善」のどちらかに分類し、実行計画を固定する。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=`04_Documentation` の文書分類を棚卸し済み`; 操作=対象文書の読者・目的・配置先を判定する; 期待結果=分類結果と次の変更方針が issue と関連文書に残る; 除外=本文の全面改稿や実装修正`
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: docs-check
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A（DecisionStatus=Fixed）

## 1) 課題 / Problem statement

- `04_Documentation/narratives.md` が、対外公開文書として維持すべきか、内部文書へ移すべきか未整理。
- 現状のままだと `04_Documentation/` に内部向け情報が残るか、逆に公開候補文書の改善優先度が見えない。
- AIエージェントが外部向け資料を作る際の配置判断が曖昧なままになる。

## 2) 背景 / Context

- 文章化ガイドは公開可能だが、内部概念との橋渡しが必要。
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
- 実施方針: 出力物の用途・制約・例示を明確化し外部読者向けに再構成する。
- 非目標: このIssue単体で対象文書の全文改稿や実装修正は行わない。

## 5) 受入条件 / Acceptance criteria

- [ ] `04_Documentation/narratives.md` の分類結果（内部移設 or 対外改善）が本文に明記される。
- [ ] 分類の根拠として Audience / Goal / 公開境界の観点が記録される。
- [ ] 変更先候補（移設先または改善対象節）が明記される。
- [ ] 必要な検証（unit/integration/e2e/docs-check）が `Expected verification level` と一致する。
- [ ] `GoNoGoGate` の要否（Required/Optional/N/A）が明示され、Required時は判定基準が本文に記載される。
- [ ] セキュリティ境界に影響するIssueでは `SecurityGateImpact` を明示し、レビューゲート項目を記載する。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 対象文書の Audience / Goal / Non-goal を確認する。
- [ ] T2 内部移設か対外改善かを判定し、根拠を本文へ追記する。
- [ ] T3 次の実行単位（移設先作成 or 公開改善PR）を明記する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `rg -n "Audience|Goal|Non-goal|Outcome|Related" 04_Documentation/narratives.md 01_Plans/documentation_quality.md`
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

- 本Issueは `04_Documentation/narratives.md` 専用の分類/改善トラッキングメモ。
- 実作業では `01_Plans/minimal-context-triage.md` と関連ADRだけを開き、一覧再読を前提にしない。

## 11) Serial execution record（Read -> ADR/CDC -> Plan -> Execute -> Verify -> Proceed）

### Phase 1 Read（latest）
- 最新Read: `AGENTS.md` Read Order と `04_Documentation/narratives.md` / 関連ADRを再確認済み。

### Phase 2 ADR/CDC
- Context: 公開文書と内部運用メモの混在が分類判断を曖昧化している。
- Decision: Classification は **Improve external** を固定する。
- Consequences: 後続PRは docs-only で公開境界の明確化に集中できる。

### Phase 3 Plan
- AC/DoD不足へのドラフト提案:
  - AC-D1: Audience / Goal / Non-goal / Outcome / Related の明示を必須化。
  - DoD-D1: docs-check と `git diff --check` が成功し、Proceed判定を三値（Ready/Hold/Needs-decision）で残す。
- 合意状態: **DOC-OPS-05 共通合意済み（Issueメモ内運用）**。

### Phase 4 Execute
- 本Issueメモを重複ログ削減・単一シリアル記録へ再編し、分類判断と検証導線を固定。

### Phase 5 Verify
- 検証結果: `Expected verification level=docs-check` と `VerificationLevel=docs-check` の一致を確認。
- 自己修復回数: 0/3（失敗時のみ最大3回まで自己修復し、超過時は停止）。

### Phase 6 Proceed
- 状態分類: **Ready（Open候補）**。
- 次アクション: `04_Documentation/narratives.md` 公開改善PRを docs-only で起票する。

---

## Authoring Checklist（人間/生成AI 共通）

- [ ] `Source Issue` が運用状態と整合している（未運用時は `N/A`、運用時はURL）。
- [ ] `Related ADR/Spec` が最低1件ある。
- [ ] 受入条件に「安全」「互換」「検証」が含まれる。
- [ ] `Validation plan` に具体コマンドがある。
- [ ] 非目標が明記されスコープ逸脱を防いでいる。


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

## 12) Track 3 serial execution record（2026-04-22, DOC-OPS-05-10）

### Phase 1 Read（開始同期）
- Read同期: `AGENTS.md` Read Order, `00_Prompt/domain.md`, `02_Architecture/schemas.md`, `04_Documentation/narratives.md` を再読。
- 確認: Track 3 の直列最終工程。指定外編集は禁止。

### Phase 2 ADR/CDC（開始同期）
- Context: narrative文書は公開価値がある一方、AI生成物の扱いを誤ると公開時リスクが高い。
- Decision: Classification は **Improve external** を維持し、公開境界とレビュー責務を明文化する。
- Consequences: reviewState運用とSafeMode境界を公開文書として再現可能に維持する。

### Phase 3 Plan（開始同期）
- AC/DoD不足提案:
  - AC-T3-10-1: 冒頭メタに `Outcome` を追加して公開改善の到達点を明示する。
  - AC-T3-10-2: `Public boundary` を追加し、内部承認・監査実装を非対象と明示する。
- 合意: **Issue内合意済み**（DOC-OPS-05共通運用）。

### Phase 4 Execute（開始同期）
- `04_Documentation/narratives.md` 冒頭メタに `Outcome` / `Public boundary` を反映。
- reviewState semantics、proposal-only原則、停止条件は既存方針を維持。

### Phase 5 Verify（開始同期）
- docs-check 実行方針: `rg -n "Outcome|Public boundary|reviewState|proposal|SafeMode|No-Go" 04_Documentation/narratives.md`
- 自己修復ポリシー: 最大3回。超過時は停止。
- 自己修復回数: **0/3**。

### Phase 6 Proceed
- 判定: **Ready（Track 3 serial completed）**。
- 次アクション: docs-only 差分としてPR化し、必要ならOpen化時に関連issueへリンクする。

## Stream G serial lane run（2026-04-22, Phase 10）

### Phase 1: Read
- 対象再読: `01_Plans/issues/issue-doc-ops-05-10-04doc-narratives.md` と対象Doc `04_Documentation/narratives.md` を最新状態で再読。
- メタ確認: `Audience / Goal / 公開境界 / GoNoGoGate / SecurityGateImpact` の不足有無を確認。

### Phase 2: Plan
- Audience: DOC-OPS-05 の公開文書整備担当者（人間レビュー担当 + 生成AI運用担当）。
- Goal: `04_Documentation/narratives.md` の分類と公開境界を再現可能な計画品質で固定する。
- 公開境界: 実装詳細・内部判断メモは非公開、公開運用に必要な説明のみ対象。
- GoNoGoGate: `Required`（Open化前に判定根拠の明示を必須化）。
- SecurityGateImpact: `public-exposure`（公開時の情報漏えい・過剰公開を防止）。

### Phase 3: Execute
- docs-only 更新として、本Issueメモに Stream G 直列処理ログを追記。
- 指定外編集（実装コード / HIL・CE・FB 系Issue）は未実施。

### Phase 4: Verify
- docs-check:
  - `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-10-04doc-narratives.md`
  - `git diff --check`
- diff整合: 1ファイル単位の差分で体裁崩れがないことを確認。

### Phase 5: Proceed
- 判定: **Ready**（推奨アクション `Improve external` を維持）。
- 次工程: Phase 11（存在する場合）の対象Issueへ直列進行。
- フェイルセーフ: 自己修復は最大3回。4回目相当・未定義競合・指定外編集検知時は `Hold` で停止。

## Stream J serial lane run（2026-04-22, Narratives owner）

### Phase 1: Read
- `04_Documentation/narratives.md` と本Issueを再読し、review state語彙が `unreviewed/human_reviewed` と一致するかを確認。

### Phase 2: Plan
- docs-only で `reviewed` 表記を `human_reviewed` に正規化し、公開境界・Go/No-Go観点は維持する。

### Phase 3: Execute
- `04_Documentation/narratives.md` の昇格条件・ワークフロー記述を `human_reviewed` へ統一。

### Phase 4: Verify
- `rg -n "human_reviewed|unreviewed|proposal|SafeMode" 04_Documentation/narratives.md`
- `git diff --check`

### Phase 5: Proceed
- 判定: **Ready**（語彙ドリフトを解消し、公開改善方針 `Improve external` を維持）。


## 2026-04-23 Stream G DOC-OPS-05 Draft contract alignment（Issue 05-10）

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
- Mock対象（1ファイル固定）: `04_Documentation/narratives.md`
- 依存切断: 他 `issue-doc-ops-05-*` への参照は情報参照に留め、実行依存を作らない。

### Phase 5) Verify
- 実行コマンド（docs-check）:
  - `rg -n "^## 2026-04-23 Stream G DOC-OPS-05 Draft contract alignment" 01_Plans/issues/issue-doc-ops-05-10-04doc-narratives.md`
  - `git diff --check`
- 判定基準: 見出し追記が1件以上検出され、diff体裁エラーがないこと。

### Phase 6) Proceed
- Status: **Ready**
- Stop condition: Self-Correction 3回超過、または本文契約の競合検知時は **Hold** へ遷移して停止。
- Next: 次Issue（05-11）へ直列で進行（05-14は完了報告で終了）。
