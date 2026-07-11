# Issue: DOC-OPS-06 現行ビュー・履歴・貢献者導線の分離

- Type: Documentation quality / Process
- Status: In Progress
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer / Documentation contributor
- Scope: `01_Plans/project-progress-dashboard.md`, `01_Plans/issues/README.md`, `01_Plans/documentation_quality.md`, `CONTRIBUTING.md`, `04_Documentation/e2e_testing.md`, `03_Implement/frontend/docs/e2e_testing.md`, `README.md`, `AGENTS.md`（導線のみ）
- Related Backlog: `DOC-OPS-04`, `DOC-PUBLIC-BOUNDARY-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0024-doc-ops-04-quality-gates-boundary.md`, `01_Plans/adr/ADR-0039-governance-right-sizing-personal-oss.md`, `01_Plans/adr/ADR-0045-agent-division-of-labor-cowork-code-codex.md`, `01_Plans/adr/ADR-0047-design-decision-adr-saturation-and-execution-first.md`, `01_Plans/issues/issue-DOC-PUBLIC-BOUNDARY-01-developer-doc-relocation.md`, `01_Plans/issues/README.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: DOC-OPS-06
- RequirementStatement: 新規メンバーとAIが、反復実行ログや旧運用に遮られず、現在の課題正本、優先作業、貢献開始手順、E2E正本、文書品質基準へ最短で到達できるようにする。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=fresh cloneの新規参加者またはAI / 操作=READMEから課題を選び、貢献手順と検証手順を辿る / 期待結果=現行issue memo運用、現在のActive集合、唯一のE2E手順、Normativeな文書品質基準へ5分以内に到達する / 除外=過去issue本文の全修正、役割分離の再導入。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export / public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: docs-check
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A

## 1) 課題 / Problem statement

現行情報を示すはずの文書に、過去のrerun/Streamログ、解消済みQueue、旧正本宣言が大量に残り、現在の指示と履歴を初見で分けられない。

- `ADR-0039` はper-rerunログ追記を停止し、dashboardをcurrent snapshotだけにする方針をAccepted済みだが、`project-progress-dashboard.md` はcurrent宣言の後に大量の旧ログを保持する。
- `01_Plans/issues/README.md` はissue memo正本と宣言する一方、監査開始時のActive表は空だった。新規5件の起票・1件完了後も、triage基準のDraft/Open/In Progress 29件（Draft 15 / Open 7 / In Progress 7）に対してActive表は4件で、25件が未掲載のまま、その後に古い同期ログとCompleted台帳が続く。
- 一部memoは `Draft (Open-Readiness Prepared / Execution Hold)` のようにlifecycleとhold理由を同じStatus値へ詰めており、triageとvalidatorでActive判定が一致しない。
- `documentation_quality.md` はNormative/Informativeを区別するが、QG本文と統一判定の間にStream実行ログが挟まり、基準自身を読み切りにくい。
- `CONTRIBUTING.md` はGitHub Issuesを最初の起票先・正本として案内する箇所があり、現行の「GitHub Issues未運用、内部issue memo正本」と矛盾する。
- E2Eの正本は `03_Implement/frontend/docs/e2e_testing.md` と決められているが、`04_Documentation/e2e_testing.md` も独立内容とSSOT表現を持ち、手順が二重化している。

この状態では、新規メンバー/AIが古いQueue、誤った起票先、古いE2E手順を現行として選び、作業の再開性と安全確認を落とす。

## 2) 背景 / Context

- `ADR-0039` はsolo/pre-release段階に合わせ、ダッシュボード履歴の凍結とcurrent snapshot化を決定済みである。
- `DOC-PUBLIC-BOUNDARY-01` は開発者向け文書の移管を後続作業として残した。
- `ADR-0019` とAGENTSは `03_Implement/frontend/docs/e2e_testing.md` をE2E実務手順の正本とする。
- 本Issueは既存決定の実行と明白な正本矛盾の解消であり、新規ADRは不要である。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 開発者が現行Actionを誤読すると、価値実装より管理ログの追認へ時間を使う。
- 安全（THREAT_MODEL / SafeMode）: 古い安全手順・起票先を現行と誤認する経路を減らす。
- 企業・行政要件（enterprise_architecture）: 現行手順と履歴を分け、監査説明と日常運用を両立する。
- 後方互換（schemas）: 文書構成・導線だけを変更し、契約と実装は変えない。

## 4) 提案する解決策 / Proposed solution

### Current-only surfaces

- `project-progress-dashboard.md`: 最終確認日時/根拠コマンド、現在のActive/Blocked、次の1手、AIだけで確定できないゲートだけを残す。
- `issues/README.md`: 現行運用ルール、機械的に再計算できるActive view、triage入口、履歴の所在だけを残す。
- `documentation_quality.md`: NormativeなQG-1〜QG-6、適用matrix、統一判定手順、停止条件を連続配置する。
- `CONTRIBUTING.md`: 現行のissue memo正本へ合わせ、README→CONTRIBUTING→issue index/triage→Task Brief→branch→checksのfirst-task runbookを1本化する。
- E2E: `03_Implement/frontend/docs/e2e_testing.md` だけをSSOTにし、旧 `04_Documentation/e2e_testing.md` の固有で有効な内容を統合後、短いSuperseded stubまたは削除+参照更新とする。

### History policy

- git履歴で復元できる反復同期ログはcurrent文書から除く。
- git履歴だけでは失われる一次証拠を残す場合のみInformative archiveへ移し、対象期間、Retention reason、現行正本への逆リンクを付ける。
- 解消済みDecision Queueや過去件数を現行の停止条件として再掲しない。

非目標:

- 過去issue memo本文の全書換え。
- 履歴の破壊的消去、監査一次データの削除。
- ガバナンス役割、Decision Queue、KPIの再導入。
- UI、API、E2Eテスト実装の変更。

## 5) 受入条件 / Acceptance criteria

- [ ] fresh cloneの読者がREADMEから5分以内に、現行課題正本、triage、issue template、branch規律、検証入口へ到達できる。
- [x] `CONTRIBUTING.md` と `issues/README.md` でGitHub Issues/内部issue memoの現行正本が矛盾しない。
- [ ] dashboardとissue indexのcurrent領域に、resolved Queue、過去件数、per-rerunログを現行指示として含めない。
- [ ] Active viewがfilesystem上のDraft/Open/In Progress集合と一致する。
- [x] Statusはtemplateの正規値へ統一し、Open-readinessやhold理由は別メタデータへ分離して、triageとvalidatorの判定集合が一致する。
- [ ] `documentation_quality.md` のNormative QGと判定手順が連続して読め、Stream実行ログを読まずに適用できる。
- [x] E2E実務手順のSSOT宣言が `03_Implement/frontend/docs/e2e_testing.md` の1箇所だけになる。
- [x] 旧04 E2E文書の有効情報が失われず、旧pathは反対の規範を持たない。
- [ ] currentから分離した一次履歴にはInformative、対象期間、Retention reason、現行正本への逆リンクがある。
- [ ] SafeMode、share/export、provider=none、proposal-onlyの現行説明を落としていない。
- [ ] README / AGENTS / CONTRIBUTING / 04管理index / issue indexのリンクが有効である。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 current文書ごとに「残す現行情報 / git履歴へ委譲 / archiveする一次証拠」の移動表を作る。
- [ ] T2 dashboardをcurrent snapshotへ縮約する。
- [ ] T3 issue READMEを運用ルール+current Active view+triage入口へ縮約し、Status拡張表現を正規化したうえで実ファイル集合と同期する。
- [ ] T4 documentation qualityのNormative本文を連続化し、実行ログを分離する。
- [x] T5 CONTRIBUTINGを現行issue memo運用とfirst-task runbookへ同期する。
- [x] T6 E2E手順を03のSSOTへ統合し、旧04pathと全参照を整理する。
- [ ] T7 fresh-clone想定の人間/AI dry-runとdocs-checkを行う。
- [ ] T8 再発防止を `DX-DOC-02` へ引き渡す。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `rg -n "GitHub Issues.*正本|まず.*GitHub Issue|Source Issue" CONTRIBUTING.md 01_Plans/issues/README.md`
  - `rg -n "single source of truth|E2E.*正本|E2E実務手順" AGENTS.md CONTRIBUTING.md 01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md 03_Implement/frontend/docs/e2e_testing.md 04_Documentation/e2e_testing.md`
  - `rg -n "Stream [A-Z].*rerun|rerun-[0-9]+" 01_Plans/project-progress-dashboard.md 01_Plans/issues/README.md 01_Plans/documentation_quality.md`
  - `python 01_Plans/triage_actionable_plans.py`
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py 01_Plans/tests/test_triage_actionable_plans.py`
  - `git diff --check`
- 期待結果:
  - 競合正本宣言とcurrent領域のrerunログが0件。Active集合・リンク・手順正本が一致する。
- 目視確認:
  - リポジトリを知らない人または別AIがREADMEから1件のReady issueと検証入口を選び、参照経路を記録する。
- 未実施時の理由・代替検証:
  - fresh-clone dry-runができない場合は、未実施理由と再開条件を残し、Doneにしない。

## 8) 代替案 / Alternatives considered

- 現在の文書に「古いログ」と注記するだけ: 読解コストと検索ノイズが残るため不採用。
- 全履歴をarchiveへ複製する: 重複と保守コストが増えるため、一次証拠だけを残す。
- GitHub Issues運用を再開して矛盾を解く: 明示的な開始宣言がなく、ADR-0039の現段階方針にも反するため不採用。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: current情報の削り過ぎ、一次証拠の喪失、旧リンク切れ、Active集合の誤生成。
- 影響範囲: 新規貢献者、AI Read Order、課題選択、E2E実行、公開品質判定。
- ロールバック手順: 文書単位の小さなcommitで進め、削除前に移動表とgit履歴から復元可能性を確認する。誤りがあれば対象スライスだけrevertする。
- Stop条件: 現行と履歴を上位根拠から判定できない場合、一次証拠の保持義務が不明な場合は削除せず、専用子Issueへ分ける。

## 10) Additional context

- 本件はADR-0039のoptional cleanupが、空Active表・起票先矛盾・E2E SSOT二重化という実害へ進んだためP1へ引き上げる。
- ADR化が必要になる条件: GitHub Issuesを正本運用へ切り替える、issue lifecycleを変更する、E2E責務を別レイヤへ再定義する場合。

## 進捗記録 2026-07-11: contributor route / E2E SSOT slice

- `CONTRIBUTING.md`、`README.md`、`SUPPORT.md`、`DISCUSSIONS.md`を、GitHub Issues未運用・内部issue memo正本・外部受付はDiscussionsという現行方針へ同期した。
- `04_Documentation/e2e_testing.md` の有効な実行経路、PR証跡、Compose差分リスク、認証Level 2、fixture境界を `03_Implement/frontend/docs/e2e_testing.md` へ統合し、旧pathをSuperseded stubへ縮約した。
- 拡張Statusを持っていたQA Draft 3件を `Status: Draft` / `Open Readiness` / `Execution`へ分離し、active statusの非正規値を0件にした。
- 未完了: dashboard/issue index/documentation qualityのcurrent/history分離、Active view 25件の未掲載解消、fresh-clone dry-run。これらを完了するまでIssueはIn Progressを維持する。
