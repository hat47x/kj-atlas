# Issue Draft: PROJECT-GOV-01 最新main収束とブランチ衛生の棚卸し

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: TBD
- Scope: `01_Plans/`, repository branch/PR workflow
- Related Backlog: `PROJECT-GOV-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0034-mainline-convergence-and-branch-hygiene.md`, `01_Plans/adr/ADR-0000-adr-governance.md`, `01_Plans/issues/issue-PRODUCT-QA-01-release-readiness-quality-gates.md`, `01_Plans/issues/issue-DOC-OPS-03-project-progress-dashboard-planning.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: PROJECT-GOV-01
- RequirementStatement: 最新mainに収束した状態を前提に、remote branch、open PR、内部issue、ADRの重複・停滞・正本不明状態を棚卸しし、今後の作業開始時に誤った入力を使わない運用へ整える。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=2026-05-21時点で `origin/main` が `2a93c95e` まで取得済み / 操作=branch/PR/issue/ADRを棚卸しし、canonical/duplicate/stale/unknownへ分類する / 期待結果=新規作業が最新mainと内部issue/ADRの正本を入力にできる / 除外=このIssue単体で全branchを削除すること。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: docs-check
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A

## 1) 課題 / Problem statement

- 2026-05-21 の `git fetch --prune` 後、remote branch が 2247 件、そのうち `codex/` を含む branch が 2227 件存在した。
- branch名には、環境変数、文書統治、UX操作性、契約凍結、E2E、データ境界など、最新mainにすでに取り込まれた可能性のある作業テーマが多数残っている。
- `triage_actionable_plans.py` は `active_issues=43 / ready=15 / blocked=28 / actionable_adrs=1` を返しており、issue/ADR側の機械判定は成立しているが、branch/PRの残存状態までは管理対象にしていない。
- このままでは、古いbranchを根拠にした再修正、同一テーマの二重ADR、最新mainに反映済みの内容を未対応と誤認するリスクがある。

## 2) 背景 / Context

- `AGENTS.md` は 00〜02 を上流、03 を下流として扱い、内部issueを正本のタスク管理に使うよう定めている。
- `DOC-OPS-03` は進捗ダッシュボードを整備済みだが、remote branch / PR の衛生管理は明示的な対象外だった。
- `PRODUCT-QA-01` の G0 計画整合では、製品化候補が個別issueへ分かれ、ADR判断と実装作業が混在していないことが求められる。
- `MVP-EXIT-01` の Program Gate では、candidate単位の証跡不足が真のブロッカーとして扱われる。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 人間が何を判断すべきかを明確にするため、古い作業単位と最新正本を分離する必要がある。
- 安全（THREAT_MODEL / SafeMode）: branch drift が SafeMode/share-export 関連の古い実装や文書を再導入すると、安全境界の回帰につながる。
- 企業・行政要件（enterprise_architecture）: 組織導入では、判断根拠、変更履歴、未解決リスクの説明可能性が必要になる。
- 後方互換（schemas）: branch整理自体はスキーマ非影響だが、古いschema変更案の再導入防止に寄与する。

## 4) 提案する解決策 / Proposed solution

- 変更対象:
  - `01_Plans` の運用メモ、進捗ダッシュボード、必要に応じたbranch/PR棚卸し記録。
  - GitHub上のremote branch / PRの分類案（削除実行は権限者判断）。
- 変更の最小単位:
  - 最新main SHA、branch件数、open PR件数、内部issue/ADRの対応関係を1つの棚卸し記録にまとめる。
  - 類似テーマは canonical issue/ADR を1つ決め、duplicate/stale は参照のみまたはclose候補にする。
- 非目標:
  - branch削除やPR closeをこのIssueの文書変更だけで実行すること。
  - プロダクト仕様、UI仕様、SafeMode既定値、データモデルを変更すること。

## 5) 受入条件 / Acceptance criteria

- [ ] `origin/main` の対象SHA、観測日時、branch件数、open PR件数が記録されている。
- [ ] remote branch の棚卸しが、少なくとも `canonical / duplicate / stale / unknown` の4分類で行われている。
- [ ] `codex/` branch の上位テーマが集計され、既存の内部issue/ADRへ対応付けられている。
- [ ] duplicate/stale と判断したbranch/PRについて、削除・close・保持の推奨判断と理由が記録されている。
- [ ] 新規issue/ADR作成時の intake 手順に、既存検索と重複分類の記載が含まれる。
- [ ] SafeMode、share-export、public exposure に関する古いbranchを削除候補にする場合は、最新main上の正本と検証証跡が確認されている。
- [ ] 必要な検証（docs-check）が `Expected verification level` と一致する。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 `git branch -r` と GitHub PR一覧から、remote branch / open PR の棚卸し表を作る。
- [ ] T2 branch名を主要テーマ別に分類し、対応する内部issue/ADRを付与する。
- [ ] T3 merged / duplicate / stale / unknown の分類基準を明文化する。
- [ ] T4 `01_Plans/project-progress-dashboard.md` または専用記録へ、最新main収束状態と未解決項目を反映する。
- [ ] T5 権限者が実行できる branch cleanup / PR close の推奨リストを作る。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `git fetch --prune origin`
  - `git branch -r | Measure-Object`
  - `git branch -r | Select-String -Pattern "codex/" | Measure-Object`
  - `python 01_Plans/triage_actionable_plans.py`
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `git diff --check`
- 期待結果:
  - branch/PRの残存状態と内部issue/ADRの現在状態を、candidate単位で説明できる。
  - triage stopper がない状態で、最新mainを入力にした作業開始ができる。
- 未実施時の理由・代替検証:
  - GitHub PR一覧を取得できない場合は、remote branch件数と内部issue/ADRの分類だけを一次証跡として残し、PR一覧は権限者確認へ回す。

## 8) 代替案 / Alternatives considered

- 代替案A: branch数を問題視せず、各作業者が必要に応じて判断する。却下理由: 最新mainと古いbranchの区別が作業者ごとに揺れ、重複起票や仕様回帰を防げない。
- 代替案B: すべての古いbranchを即削除する。却下理由: 未統合の知見や未完了PRを誤って失う可能性がある。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: cleanup候補の分類が粗く、必要な作業branchを stale と誤判定する。
- 影響範囲: 内部issue/ADR、PR運用、製品化ゲートの計画整合。
- ロールバック手順: branch削除前に分類表をレビューし、削除済みbranchは GitHub の復旧可能範囲または保持forkから復元する。

## 10) Additional context

- 2026-05-21観測:
  - `origin/main`: `2a93c95e`
  - remote branch: 2247
  - `codex/` remote branch: 2227
  - triage: `active_issues=43 / ready=15 / blocked=28 / actionable_adrs=1`
  - triage stopper: none
- ADR化済み: `ADR-0034`

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している（未運用時は `N/A`）。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
