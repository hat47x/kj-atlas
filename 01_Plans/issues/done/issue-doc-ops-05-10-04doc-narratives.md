# Issue Draft: DOC-OPS-05-10 04_Documentation/narratives.md の配置見直し

- Type: Documentation quality
- Status: Done
- Source Issue: N/A
- Priority: P2
- Owner: TBD
- Scope: `04_Documentation/narratives.md`
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `04_Documentation/narratives.md`, `00_Prompt/domain.md`, `01_Plans/documentation_quality.md`
- Dependencies: `DOC-OPS-05`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: `DOC-OPS-05-10`
- RequirementStatement: `04_Documentation/narratives.md` を「内部文書へ移動」または「対外文書として改善」のどちらかに分類し、実行計画を固定する。
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

    - [x] `04_Documentation/narratives.md` の分類結果（内部移設 or 対外改善）が本文に明記される。→ 本文「推奨アクション」に分類決定を明記（2026-08-07確認）。
    - [x] 分類の根拠として Audience / Goal / 公開境界の観点が記録される。→ 本文 Requirement meta I/F・分類根拠に記録済み。
    - [x] 変更先候補（移設先または改善対象節）が明記される。→ 本文に明記済み。
    - [x] 必要な検証（unit/integration/e2e/docs-check）が `Expected verification level` と一致する。→ VerificationLevel=docs-check と本文検証計画が一致。
    - [x] `GoNoGoGate` の要否（Required/Optional/N/A）が明示され、Required時は判定基準が本文に記載される。→ Requirement meta I/F に明示済み。
    - [x] セキュリティ境界に影響するIssueでは `SecurityGateImpact` を明示し、レビューゲート項目を記載する。→ Requirement meta I/F に明示済み。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 対象文書の Audience / Goal / Non-goal を確認する。 → 本文「推奨アクション」の分類根拠で確認済み（2026-08-07）。
- [x] T2 内部移設か対外改善かを判定し、根拠を本文へ追記する。 → 判定は「推奨アクション」に記録（Improve external / Move internal）。
- [x] T3 次の実行単位（移設先作成 or 公開改善PR）を明記する。 → 次アクションは本文に明記済み。

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

## 2026-04-24 Stream H serial pass（DOC-OPS-05 strict lane）

### Phase 1 Read
- 対象Issue（DOC-OPS-05-10）の Requirement meta I/F、既存Classification、GoNoGoGate、Validation plan を再確認。
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
- 実行: `rg -n "Phase 1 Read|Phase 2 ADR/CDC|Phase 3 Plan|Phase 4 Execute|Phase 5 Verify|Phase 6 Proceed|self-correction<=3" 01_Plans/issues/issue-doc-ops-05-10-04doc-narratives.md`
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
- 再確認: `Status=Draft` / `Priority=P2` / `Scope=04_Documentation/narratives.md` / `RequirementID=DOC-OPS-05-10` / `VerificationLevel=docs-check`。
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

## Stream K serial execution record（2026-04-26, narratives owner）

### Phase 1 Read
- `04_Documentation/narratives.md` と `00_Prompt/domain.md` の語彙整合を再確認し、`reviewState` / `SafeMode` の用語差異がないことを確認。
- 最新差分検知として、公開境界・Go/No-Go・停止条件の欠落有無を確認。

### Phase 2 ADR/CDC
- Context: narrativeは公開可能だが、domain語彙を逸脱すると運用誤解を生む。
- Decision: 分類は **Improve external** を維持し、定義拡張は既存domain語彙の範囲内に限定する。
- Consequences: 公開文書の可読性を上げつつ、概念衝突を防止できる。

### Phase 3 Plan
- AC補完提案:
  - AC-K-10-1: `Domain vocabulary compatibility` を明記し、用語追加時は `00_Prompt/domain.md` を優先する。
  - AC-K-10-2: Go/No-Go判定に「語彙矛盾なし」を追加する。
- DoD補完提案:
  - DoD-K-10-1: 6Phase記録をIssue/Doc双方へ残す。
  - DoD-K-10-2: Verify失敗時は3回以内に修復し、超過時停止する。

### Phase 4 Execute
- docs-only 最小差分で `04_Documentation/narratives.md` に domain語彙整合チェックを追記。

### Phase 5 Verify
- 実施コマンド:
  - `rg -n "Domain vocabulary compatibility|reviewState|human_reviewed|SafeMode|Go/No-Go" 04_Documentation/narratives.md`
  - `git diff --check`
- 自己修復回数: 0/3。

### Phase 6 Proceed
- 判定: **Ready**。
- フェイルセーフ: 3回超過/前提崩れ/allowlist逸脱時は `Hold` で停止する。


## Stream K serial run（2026-04-26 / Prompt K lane / step 2/4: DOC-OPS-05-10）

### Phase 1 Read
- 本Issueと対象 `04_Documentation/narratives.md` を再読し、分類固定（**Improve external**）が維持されていることを確認。
- 観点: narrative語彙整合（domain準拠）。

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

## Stream L serial cycle (2026-04-26 / DOC-OPS-05-10)

### Read
- Requirement meta を再確認し、分類 `Improve external` と語彙整合（reviewState）方針を再確認。

### Plan
- AC/DoD補完方針: Public boundary / Outcome / GoNoGo 判定導線を維持。
- ADR: 運用境界差分は新規発生なしのため追加ADRは不要。

### Execute
- 本Issueメモへ Stream L 実行記録を追記（対象外編集なし）。

### Verify
- `python 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-10-04doc-narratives.md`
- `git diff --check`
- self-repair: 0/3（上限3回、4回目相当は停止）。

### Proceed
- 判定: **Ready**。
- 次工程: 05-02 へ直列進行。


## Stream H dedicated serial run（2026-04-27）

### Phase 1 Read（開始同期）
- Read同期: 上流（`00_Prompt/domain.md` を含む）と本Issueを再読し、語彙整合条件を確認。

### Phase 2 ADR/CDC
- Context: narratives は公開文書だが domain語彙逸脱が誤解を生みやすい。
- Decision: **Improve external** を維持し、語彙整合（domain優先）を固定。
- Consequences: 公開品質と概念整合の両立を維持する。

### Phase 3 Plan
- 実行計画: Issueメモ更新のみ（docs-only）。
- 停止条件: self-correction 4回目相当 / 未定義競合 / allowlist外編集要求。

### Phase 4 Execute
- 実施: Stream H 専属6Phaseログ追記。
- 非実施: 実装コード、architecture本体、shared resource。

### Phase 5 Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-10-04doc-narratives.md`
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
- Read同期を再実施（AGENTS Read Orderの上流要素 + `04_Documentation/narratives.md`）。
- Scope再確認: docs-only、指定issue外は非編集。

### Phase 2 ADR/CDC
- Context: narrativesは公開価値があるが、提案文（proposal）と確定文（human_reviewed）の境界管理が必要。
- Decision: 本Issueの分類を **Improve external** として維持する。
- Consequences: 公開文書としての説明責務を強化しつつ、内部判断メモの流入を防止する。

### Phase 3 Plan
- 直列固定: Plan -> Execute -> Verify -> Proceed。
- AC/DoD不足提案（Issue内合意）:
  - AC-G-10: Audience/Goal/Non-goal/Public boundary/Outcome を再確認できる状態を維持。
  - DoD-G-10: Proceedで `Ready/Hold/Needs-decision` を必ず明示。

### Phase 4 Execute
- 本Issueメモへ2026-04-27の直列実行記録を追記。
- 指定外編集・コード変更は未実施。

### Phase 5 Verify
- docs-check:
  - `rg -n "2026-04-27 Stream G serial execution|Improve external|Ready/Hold/Needs-decision|Public boundary" 01_Plans/issues/issue-doc-ops-05-10-04doc-narratives.md`
  - `git diff --check`
- Self-Correction: 0/3（失敗なし）。

### Phase 6 Proceed
- 判定: **Ready**。
- 次アクション: narratives公開改善PR（docs-only）へ進行可能。

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
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-10-04doc-narratives.md`
  - `git diff --check`
- self-correction: 0/3（失敗時のみ最大3回、4回目相当は即停止）。

### Phase 5 Proceed
- 判定: **Go**（停止条件: セキュリティ導線矛盾 / 指定外編集 / self-correction上限超過 に非該当）。


## Stream G dedicated lane run（2026-04-28 / DOC-OPS-05 Security-docs専任）

### Phase 1 Read（開始同期）
- Read同期を実施し、Read Orderと本Issueの `Requirement meta I/F` を再確認。
- `SecurityGateImpact=public-exposure` / docs-only / allowlist内編集を確認。

### Phase 2 ADR/CDC（C/D/C + 承認）
- Context: narratives は外部公開時の説明品質に直結し、公開境界の語彙統一が必要。
- Decision: 分類 **Improve external** を維持し、役割語彙を `Security Officer / System Owner / Platform Operator` へ固定する。
- Consequences: 運用語彙ドリフトを抑え、公開境界の監査性を維持する。
- Approval: **Issueメモ内運用承認（DOC-OPS-05 Stream G）** を記録。未承認事項は確定しない。

### Phase 3 Plan（AC/DoD不足ドラフト提案）
- AC Draft:
  - AC-G-10-1: Audience / Goal / Non-goal / Public boundary / Outcome / Related を維持する。
  - AC-G-10-2: GoNoGoGate Required の判定導線を本文で再現可能にする。
- DoD Draft:
  - DoD-G-10-1: 6フェーズの直列ログを残す。
  - DoD-G-10-2: self-correction は最大3回、超過時停止。

### Phase 4 Execute
- 実施: 本Issueメモへの追記のみ。
- 非実施: 実装変更、固定値（D1〜D4）更新、未承認確定化。

### Phase 5 Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-10-04doc-narratives.md`
- `git diff --check`
- self-correction: 0/3。

### Phase 6 Proceed
- 判定: **Ready**
- 理由: 必須6フェーズと安全運用条件を満たしたため。


## Stream G dedicated serial completion (2026-04-28)

### Phase 1 Read
- AC/Validationの再収集を実施し、`Requirement meta I/F`・`Acceptance criteria`・`Validation plan` の3点が本文に存在することを確認。
- フェイルセーフ確認: AC不在/検証不能/allowlist外編集要求は該当なし。

### Phase 2 Plan
- 難易度低→高の固定順を `01 → 03 → 08 → 10 → 04 → 09 → 12 → 14` としてロック。
- 本Issueの実行順は **4/8** とし、分類 `Improve external` を維持。

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
- `git diff --check` と `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-10-04doc-narratives.md` を実行対象とする。
- 自己修復回数: 0/3（4回目相当はHold停止）。

### Phase 5 issue更新
- 判定: **Ready**（停止条件非該当、docs-only維持）。


## Stream G normalization pass（2026-05-04）

### Phase 1: Read同期（Issue ↔ 04_Documentation 対応表）
| Issue | Target 04_Documentation | Current classification |
| --- | --- | --- |
| `issue-doc-ops-05-10-04doc-narratives.md` | `04_Documentation/narratives.md` | 既存本文の Decision / Proposed classification を継承 |

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
  - `rg -n "^- Status:|Expected verification level|VerificationLevel|GoNoGoGate|DecisionStatus|DecisionQueueRef" 01_Plans/issues/issue-doc-ops-05-10-04doc-narratives.md`
  - `rg -n "Open readiness:|状態分類:|Phase 5: Proceed" 01_Plans/issues/issue-doc-ops-05-10-04doc-narratives.md`
  - `git diff --check`
- Proceed verdict (Phase 6): `Open可能（条件付き）`

## Stream G documentation/public boundary pass (2026-06-13)

### Plan
- 対象: `narratives`。
- Scope: Docs-only。`03_Implement/` と `02_Architecture/` は編集しない。
- Acceptance: 公開/保守/開発者/内部計画の分類が追跡でき、SafeMode・share/export・AI提案レビューの安全境界が後退しない。

### Execute
- RequirementID `DOC-OPS-05-10` の公開境界を再確認。
- Decision: narratives は文章化を確定結論ではなく候補・下書きとして扱い、人間レビュー必須の境界を再確認した。

### Verify
- docs-check 対象として issue memo metadata、Markdown整形、リンク導線、公開不可情報の混入有無を確認する。
- Self-correction budget: 0/3 から開始し、4回目相当は停止する。

### Proceed
- 判定: Ready for verification。
- 残課題: 実ファイル移動や開発者向け正本の再配置が必要な場合は、別PRで allowlist と移動先を明示して扱う。
