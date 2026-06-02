# Issue Draft: PROJECT-GOV-01 最新main収束とブランチ衛生の棚卸し

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Codex (Project governance evidence steward; accountable cleanup owner remains Repository Maintainer)
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

## 11) Convergence checkpoint 2026-05-24: DATA/OPS open PR lane

### Observation

- Observed after `git fetch --prune origin` on 2026-05-24.
- `origin/main`: `512714e3a9935f91f085b3b9d0d0053943ad2841`
- remote branch count: 2261
- `origin/codex/` remote branch count: 2239
- open PR count returned by GitHub search: 4
- internal issue triage:
  - `active_issues=46`
  - `ready=18`
  - `blocked=28`
  - `actionable_adrs=1`
  - stopper: none
  - note: #2264 adds `PRODUCT-OPS-02` on a PR branch, so it is not counted in this `origin/main`-based triage until merged.

### Open PR inventory

| PR | Branch | Topic | Governance classification | Recommended action |
| --- | --- | --- | --- | --- |
| #2261 | `codex/data-maint-results-gate-sync` | DATA-MAINT-01 parent handoff for recovery evidence | canonical / merge-ready | Merge before #2262 because #2262 references this handoff. |
| #2262 | `codex/mvp-exit-recovery-evidence-intake` | MVP-EXIT Program Gate intake for recovery evidence | canonical / merge-ready after #2261 | Merge after #2261, then re-check conflict because both are planning-layer only but semantically ordered. |
| #2263 | `codex/product-qa-recovery-evidence-gate` | PRODUCT-QA Gate Record for the same recovery evidence | canonical / merge-ready after #2262 | Merge after #2262 so QA record can point to the accepted Program Gate trail. |
| #2264 | `codex/support-bundle-follow-up-issue` | PRODUCT-OPS-02 Draft issue split from PRODUCT-OPS-01 | independent canonical / merge-ready | Can merge independently; low conflict risk with DATA/MVP/QA lane. |

### Closed stacked PRs used as evidence

| PR | State | Note |
| --- | --- | --- |
| #2259 | merged into stacked branch | Adds representative SQLite recovery exercise evidence. |
| #2260 | merged into stacked branch | Records PostgreSQL rehearsal boundary and Docker restart condition. |

### Decision

- Treat #2261 -> #2262 -> #2263 as a single ordered evidence lane: parent data-maintenance handoff, program gate intake, then QA gate record.
- Treat #2264 as an independent support/diagnostics policy lane. It should not be blocked on the DATA lane unless reviewers want a single release-readiness bundle.
- Do not close or delete remote branches from this issue update. Branch cleanup remains a separate permissioned operation after PR merge/close confirmation.
- Do not create a new ADR for this checkpoint. ADR-0034 already governs mainline convergence and branch hygiene; this update only records current inventory and merge order.

### Follow-up

- After each merge, run `git fetch --prune origin` and re-check `origin/main`, open PR count, and triage stopper state.
- After #2261..#2264 are merged or closed, create a cleanup candidate table for the four corresponding `origin/codex/*` branches.
- Full branch hygiene still requires a broader canonical / duplicate / stale / unknown classification across the 2239 `origin/codex/` branches; this checkpoint only covers the active open PR lane.

## 12) Convergence checkpoint 2026-05-25: refreshed PR lane after baseline/recovery evidence

### Observation

- Observed after `git fetch --prune origin` on 2026-05-25.
- `origin/main`: `512714e3a9935f91f085b3b9d0d0053943ad2841`
- remote branch count: 2264
- `origin/codex/` remote branch count: 2242
- open PR count returned by GitHub search: 7
- internal issue triage:
  - `active_issues=46`
  - `ready=18`
  - `blocked=28`
  - `actionable_adrs=1`
  - stopper: none

### Open PR inventory

| PR | Branch | Topic | Governance classification | Recommended action |
| --- | --- | --- | --- | --- |
| #2261 | `codex/data-maint-results-gate-sync` | DATA-MAINT-01 parent handoff for earlier recovery evidence | duplicate/superseded candidate | Prefer #2267 as the canonical DATA-MAINT recovery evidence because it includes the executable integration test and parent handoff. If #2267 merges, close or rebase #2261 instead of merging stale evidence. |
| #2262 | `codex/mvp-exit-recovery-evidence-intake` | MVP-EXIT Program Gate intake for #2267 recovery evidence | canonical / merge-ready after #2267 | Refreshed at `5661f1fa90c1e65da2c21736f4d46f4d55533668` and CI run 9114 passed. Merge after #2267 so the Program Gate intake points to the accepted representative recovery evidence. |
| #2263 | `codex/product-qa-recovery-evidence-gate` | PRODUCT-QA recovery evidence gate | duplicate/superseded candidate | #2267 already adds a PRODUCT-QA Gate Record for DATA-MAINT-02. If #2267 merges, close or rebase #2263 to avoid two QA records for the same evidence. |
| #2264 | `codex/support-bundle-follow-up-issue` | PRODUCT-OPS-02 support diagnostics bundle policy split | independent canonical / merge-ready | Can merge independently. It creates a follow-up policy issue and does not depend on the DATA recovery lane. |
| #2265 | `codex/project-gov-open-pr-convergence` | This PROJECT-GOV convergence checkpoint | canonical / update-in-place | Keep this PR as the active PR-lane inventory and update it rather than opening duplicate governance checkpoint PRs. |
| #2266 | `codex/project-baseline-20260525` | Latest-main health baseline | time-boxed canonical / merge-ready | Can merge as a dated baseline record. Re-run a new baseline only after the DATA/OPS lane changes `main` materially. |
| #2267 | `codex/data-maint-02-recovery-exercise` | Executable DATA-MAINT-02 SQLite and temporary PostgreSQL recovery exercise plus issue/doc/QA evidence | primary canonical / merge-ready | Treat as the current canonical DATA-MAINT recovery evidence. Refreshed at `f230ea6b9d86f46478c029290175d9f4e7d9cb74` and CI run 9112 passed. Merge before #2262 and before deciding whether #2261/#2263 should be closed or rebased. |

### Updated merge / close recommendation

1. Merge or review #2267 first as the canonical DATA-MAINT-02 recovery evidence PR.
2. After #2267, merge or review #2262 as the refreshed MVP-EXIT Program Gate intake for the accepted recovery evidence.
3. After #2267, either close #2261/#2263 as superseded or rebase them to contain only evidence not already present in #2267.
4. Merge #2264 independently when reviewers are ready.
5. Merge #2266 as a dated baseline record, or create a fresh baseline if #2267 is merged before #2266 is reviewed.
6. Keep #2265 as the active governance checkpoint and avoid creating additional PROJECT-GOV inventory PRs unless `origin/main` changes first.

### Cleanup candidate table

| Branch | Current classification | Cleanup recommendation |
| --- | --- | --- |
| `origin/codex/data-maint-results-gate-sync` | duplicate/superseded candidate | Delete after #2261 is closed or merged/rebased. |
| `origin/codex/mvp-exit-recovery-evidence-intake` | canonical / refreshed MVP-EXIT evidence intake | Keep until #2262 is merged/closed after #2267. |
| `origin/codex/product-qa-recovery-evidence-gate` | duplicate/superseded candidate | Delete after #2263 is closed or merged/rebased. |
| `origin/codex/support-bundle-follow-up-issue` | independent canonical | Keep until #2264 is merged/closed. |
| `origin/codex/project-gov-open-pr-convergence` | active governance checkpoint | Keep until #2265 is merged/closed. |
| `origin/codex/project-baseline-20260525` | dated baseline | Keep until #2266 is merged/closed. |
| `origin/codex/data-maint-02-recovery-exercise` | primary DATA-MAINT recovery evidence | Keep until #2267 is merged/closed. |

### Decision

- No branch deletion or PR closure is executed from this checkpoint.
- No new ADR is required. ADR-0034 already defines the mainline convergence policy; this update only refreshes the open PR lane.
- The canonical DATA recovery lane changes from the older #2261/#2263 planning-only records to #2267, because #2267 includes executable SQLite evidence, temporary PostgreSQL dump/restore evidence, restored SQL readback, and CI success.
- #2262 has been refreshed to consume #2267 at `f230ea6b9d86f46478c029290175d9f4e7d9cb74` as its primary evidence candidate; it is no longer a pending refresh item.

## 13) Convergence checkpoint 2026-05-26: evidence lane merged, DX lane isolated

### Observation

- Observed after `git fetch --prune origin` on 2026-05-26.
- `origin/main`: `1a8ecd575e830f5fa51e537b75875840c69c7096`
- remote branch count: 2267
- `origin/codex/` remote branch count: 2245
- open PR count returned by GitHub search: 1
- internal issue triage:
  - `active_issues=47`
  - `ready=18`
  - `blocked=29`
  - `actionable_adrs=1`
  - stopper: none

### PR lane resolution

| PR | State | Merge commit | Governance result |
| --- | --- | --- | --- |
| #2261 | merged | `1a8ecd575e830f5fa51e537b75875840c69c7096` | DATA-MAINT-01 parent handoff is now on `main`. |
| #2262 | merged | `4e6c57078cfed0a2057a313731e298a6648ccf05` | MVP-EXIT recovery evidence intake is now on `main`. |
| #2263 | merged | `6b5289723cb6216e214ef87c4847ddf967f7e66d` | PRODUCT-QA recovery evidence gate is now on `main`. |
| #2264 | merged | `e72efc42c7dd689c805054379f2180513987c125` | PRODUCT-OPS-02 follow-up issue split is now on `main`. |
| #2265 | merged | `1814d853147ed1e8cca4fd14e15707e3ab88e754` | Prior governance checkpoint is now on `main`. |
| #2266 | merged | `5a242b5e16945b15b167f6c34c61ce5a3a668320` | 2026-05-25 latest-main baseline record is now on `main`. |
| #2267 | merged | `e9c354f4cb8f76e7a35f8d51fd1ab6eca3c88f69` | DATA-MAINT-02 recovery exercise evidence is now on `main`. |
| #2270 | open draft | N/A | Independent DX lane for Codex RTK token-saving runbook. It must not be treated as product/runtime release evidence. |

### Decision

- The DATA/MVP/QA/OPS evidence lane from #2261 through #2267 is considered converged into `main`.
- #2270 is an independent developer-experience documentation lane. It is mergeable from a repository-governance perspective, but it does not change product runtime, SafeMode behavior, public user documentation, data maintenance evidence, or release readiness.
- No new ADR is required. ADR-0034 already covers the mainline convergence policy, and the current change only records the updated inventory.
- Branch deletion remains a permissioned cleanup action and is not executed from this issue update.

### Updated recommendation

1. Treat `origin/main@1a8ecd575e830f5fa51e537b75875840c69c7096` as the current planning input.
2. Review or merge #2270 independently of product release gates because it is Codex local-operations guidance.
3. After #2270 is merged or closed, add `origin/codex/rtk-agent-runbook` to the cleanup candidate table.
4. Do not create another PROJECT-GOV checkpoint unless `origin/main`, the open PR set, or the active issue triage materially changes.

## 14) Convergence checkpoint 2026-05-31: productization evidence PR lane

### Observation

- Observed after `git fetch --prune origin` on 2026-05-31.
- `origin/main`: `6a64b707d2944e24bcd9fa01614eacfdaea1bac1`
- remote branch count: 2274
- `origin/codex/` remote branch count: 2252
- open PR count returned by GitHub search: 4
- internal issue triage on current `main`:
  - `active_issues=46`
  - `ready=21`
  - `blocked=25`
  - `actionable_adrs=1`
  - stopper: none

### Open PR inventory

| PR | Branch | Topic | Changed-file overlap | Governance classification | Recommended action |
| --- | --- | --- | --- | --- | --- |
| #2273 | `codex/responsive-operability-docs-20260531` | `PRODUCT-UX-04` responsive/large-document operability closeout and public diagnostics/acceptance docs | overlaps #2275 on `04_Documentation/acceptance_check.md`; otherwise docs/issue only | canonical / reviewable | Merge before or after #2275 with a quick docs conflict check; it is productization evidence, not a runtime policy change. |
| #2274 | `codex/first-run-document-entry-20260531` | `PRODUCT-UX-01` first-run document entry panel, i18n, E2E, screenshot, and public docs | overlaps #2275 on i18n locale files and screenshot README | primary UX implementation lane / reviewable | Review as the largest runtime UX change. If merged first, rebase #2275 for i18n/docs overlap before merge. |
| #2275 | `codex/workspace-ia-context-20260531` | `PRODUCT-UX-02` workspace selection context summary, i18n, E2E, screenshot, and acceptance docs | overlaps #2273 on acceptance docs and #2274 on locale/screenshot README | companion UX implementation lane / reviewable | Merge after #2274 or rebase after #2274 to avoid locale/docs conflicts; keep as separate PR because it owns selection context rather than first-run entry. |
| #2276 | `codex/product-ops-01-closeout-20260531` | `PRODUCT-OPS-01` recovery guidance issue closeout | no overlap with #2273..#2275 | independent planning closeout / reviewable | Can merge independently. Until it merges, `PRODUCT-OPS-01` remains active in `main` triage. |

### Decision

- Treat #2274 and #2275 as a paired product UX lane. They are semantically separate but both touch locale files and user-facing screenshots, so one should be merged first and the other rebased if conflicts appear.
- Treat #2273 as a documentation/evidence lane for responsive operability. It can merge independently, but `04_Documentation/acceptance_check.md` overlap with #2275 requires a light conflict check.
- Treat #2276 as an independent governance closeout for `PRODUCT-OPS-01`. It has no file overlap with the UX PRs and can be reviewed or merged separately.
- No branch deletion or PR closure is executed from this checkpoint.
- No new ADR is required. The checkpoint records PR-lane inventory under ADR-0034 governance and does not change product architecture, SafeMode policy, or release authority.

### Cleanup candidate table

| Branch | Current classification | Cleanup recommendation |
| --- | --- | --- |
| `origin/codex/responsive-operability-docs-20260531` | canonical productization evidence | Delete only after #2273 is merged or closed. |
| `origin/codex/first-run-document-entry-20260531` | primary UX implementation evidence | Delete only after #2274 is merged or closed. |
| `origin/codex/workspace-ia-context-20260531` | companion UX implementation evidence | Delete only after #2275 is merged or closed. |
| `origin/codex/product-ops-01-closeout-20260531` | independent planning closeout | Delete only after #2276 is merged or closed. |

### Updated recommendation

1. Review #2274 first if reviewers want to settle the first-run entry behavior before the side-panel context summary.
2. Rebase or conflict-check #2275 after #2274 because both touch `03_Implement/frontend/src/i18n/locales/*.json` and screenshot index documentation.
3. Merge #2273 and #2276 independently when their docs/issue evidence is accepted.
4. After any merge, rerun `git fetch --prune origin`, `validate_active_issue_memos.py`, and `triage_actionable_plans.py` before starting the next productization slice from `main`.

## 15) Convergence checkpoint 2026-06-01: merged PR lane drained

### Observation

- Observed after `git fetch --prune origin` on 2026-06-01.
- `origin/main`: `01fea1bb2724356f53077d4df52a296d21ed2f67`
- remote branch count: 2284
- `origin/codex/` remote branch count: 2261
- open PR count returned by GitHub connector search: 0
- internal issue triage on current `main`:
  - `active_issues=41`
  - `ready=16`
  - `blocked=25`
  - `actionable_adrs=1`
  - stopper: none

### Recent PR lane resolution

| PR | State | Governance result |
| --- | --- | --- |
| #2273 | merged | PRODUCT-UX-04 responsive/large-document operability evidence is on `main`. |
| #2274 | merged | PRODUCT-UX-01 first-run document entry evidence is on `main`. |
| #2275 | merged | PRODUCT-UX-02 workspace selection context summary evidence is on `main`. |
| #2276 | merged | PRODUCT-OPS-01 recovery guidance closeout is on `main`. |
| #2277 | merged | Previous 2026-05-31 PR-lane checkpoint is on `main`. |
| #2278 | merged | CE3 Japanese E2E locator fix is on `main`. |
| #2279 | merged | Latest-main release gate intake is on `main`. |
| #2280 | merged | DATA-MODEL-OPS-01 closeout is on `main`. |
| #2281 | merged | DATA-CONTRACT-01 verification intake is on `main`. |
| #2282 | merged | DATA-MAINT-03 high-privilege lifecycle issue split is on `main`. |
| #2283 | merged | DATA-MAINT-02 recovery exercise closeout is on `main`. |
| #2284 | merged | Latest-main lightweight baseline record is on `main`. |
| #2285 | merged | Proposed ADR-0035 high-privilege lifecycle boundary is on `main`. |

### Decision

- The open productization PR lane recorded on 2026-05-31 is now drained; no open PRs were found by the GitHub connector search.
- `origin/main@01fea1bb2724356f53077d4df52a296d21ed2f67` is the current planning input for the next productization slice.
- No new ADR is required for this checkpoint. The current change records repository governance state under ADR-0034; product/data lifecycle decision authority remains in ADR-0035 and value-gate decision authority remains in ADR-0032.
- Branch deletion remains a permissioned repository maintenance action and is not executed from this checkpoint.

### Cleanup candidate table

| Branch | Current classification | Cleanup recommendation |
| --- | --- | --- |
| `origin/codex/responsive-operability-docs-20260531` | merged productization evidence | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/first-run-document-entry-20260531` | merged productization evidence | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/workspace-ia-context-20260531` | merged productization evidence | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/product-ops-01-closeout-20260531` | merged planning closeout | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/project-baseline-20260531` | merged E2E locator fix | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/release-gate-20260531-intake` | merged release-gate intake | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/data-model-ops-01-closeout-20260531` | merged data-model closeout | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/data-contract-01-review-20260531` | merged contract verification intake | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/data-maint-01-review-20260531` | merged high-privilege issue split | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/data-maint-02-closeout-20260531` | merged recovery closeout | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/project-baseline-20260531-refresh` | merged lightweight baseline | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/data-privileged-lifecycle-adr-20260601` | merged ADR-0035 proposal | Delete only after repository maintainer confirms no post-merge audit need. |

### Updated recommendation

1. Start the next productization work from `origin/main@01fea1bb2724356f53077d4df52a296d21ed2f67`.
2. Prioritize ADR-0035 decisioning for `DATA-MAINT-03`, because the implementation boundary remains intentionally stopped until that ADR is accepted or replaced.
3. Keep full release shipment No-Go until `PRODUCT-VALUE-01..03`, full release-candidate E2E/viewport/screenshot evidence, and full Compose startup evidence are recorded.
4. Do not create another PROJECT-GOV checkpoint unless `origin/main`, the open PR set, or active issue triage materially changes.

## 16) Convergence checkpoint 2026-06-01: data-contract closeout lane merged, productization gate sync open

### Observation

- Observed after `git fetch --prune origin` and GitHub connector open-PR search on 2026-06-01.
- `origin/main`: `b38c7ac7a318acd94ab7da7b090976ed9059c2c7`
- remote branch count: 2290
- `origin/codex/` remote branch count: 2267
- open PR count returned by GitHub connector search: 1
- internal issue triage on current `main`:
  - `active_issues=41`
  - `ready=15`
  - `blocked=26`
  - `actionable_adrs=1`
  - stopper: none

### Recent PR lane resolution

| PR | State | Governance result |
| --- | --- | --- |
| #2286 | merged | Latest-main gate sync for `origin/main@01fea1bb...` is on `main`. |
| #2287 | merged | Draft `DATA-MAINT-04` metadata-only audit viewing issue split is on `main`. |
| #2288 | merged | `DATA-CONTRACT-01` is closed for the current DocumentV2/API/support-level baseline. |
| #2289 | merged | `DATA-MAINT-01` unresolved decision routing now points to `ADR-0035`, `DATA-MAINT-03`, and `DATA-MAINT-04`. |
| #2290 | merged | `DATA-MAINT-04` audit metadata baseline and boundary wording are on `main`. |
| #2291 | open draft | Productization gate sync after the data-contract closeout lane; keep as the current review lane rather than duplicating its file changes. |

### Open PR inventory

| PR | Branch | Topic | Governance classification | Recommended action |
| --- | --- | --- | --- | --- |
| #2291 | `codex/productization-data-contract-gate-sync-20260601` | `PRODUCT-QA-01` and `MVP-EXIT-01` gate sync after `DATA-CONTRACT-01` closeout and DATA-MAINT routing updates | canonical / reviewable | Review or merge as the single open productization gate sync. If `main` changes first, update #2291 in place instead of opening a duplicate gate record. |

### Decision

- `origin/main@b38c7ac7a318acd94ab7da7b090976ed9059c2c7` is the current planning input for work that does not intentionally build on #2291.
- #2291 is the current canonical open PR lane for productization gate wording after `DATA-CONTRACT-01` closeout. This checkpoint must not be treated as a substitute for that gate record.
- No branch deletion or PR closure is executed from this checkpoint. Branch cleanup remains a permissioned repository maintenance action after maintainer confirmation.
- No new ADR is required. ADR-0034 governs mainline convergence and branch hygiene, while product/data lifecycle decision authority remains with ADR-0035 and value/release gate authority remains with ADR-0032 and the associated issues.
- Full release shipment remains No-Go until product-value evidence, release-candidate E2E/viewport/screenshot evidence, Compose startup evidence, and final program approval are recorded.

### Cleanup candidate table

| Branch | Current classification | Cleanup recommendation |
| --- | --- | --- |
| `origin/codex/latest-main-gate-sync-20260601` | merged latest-main gate sync | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/data-maint-audit-metadata-issue-20260601` | merged `DATA-MAINT-04` issue split | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/data-contract-01-closeout-20260601` | merged `DATA-CONTRACT-01` closeout | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/data-maint-01-adr35-routing-20260601` | merged `DATA-MAINT-01` decision routing sync | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/data-maint-04-audit-metadata-baseline-20260601` | merged `DATA-MAINT-04` audit metadata baseline | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/productization-data-contract-gate-sync-20260601` | open productization gate sync PR #2291 | Keep until #2291 is merged, closed, or intentionally superseded. |

### Updated recommendation

1. Review or merge #2291 before starting another productization gate PR that touches `PRODUCT-QA-01` or `MVP-EXIT-01`.
2. Start independent planning or implementation work from `origin/main@b38c7ac7a318acd94ab7da7b090976ed9059c2c7` and explicitly note when it does or does not depend on #2291.
3. After #2291 merges or closes, rerun `git fetch --prune origin`, GitHub open-PR search, `validate_active_issue_memos.py`, and `triage_actionable_plans.py`.
4. Treat the listed stale branches as cleanup candidates only; do not delete them without repository maintainer confirmation.

## 17) Convergence checkpoint 2026-06-02: gate sync lane drained after merge

### Observation

- Observed after `git pull --ff-only origin main` and GitHub connector open-PR search on 2026-06-02.
- `origin/main`: `44d9c526a83f1fad60a172895a9bbe7e1db02365`
- remote branch count: 2291
- `origin/codex/` remote branch count: 2268
- open PR count returned by GitHub connector search: 0
- internal issue triage on current `main`:
  - `active_issues=41`
  - `ready=15`
  - `blocked=26`
  - `actionable_adrs=1`
  - stopper: none

### Recent PR lane resolution

| PR | State | Governance result |
| --- | --- | --- |
| #2288 | merged | `DATA-CONTRACT-01` closeout is on `main`. |
| #2289 | merged | `DATA-MAINT-01` decision routing sync is on `main`. |
| #2290 | merged | `DATA-MAINT-04` audit metadata baseline is on `main`. |
| #2291 | merged | Productization gate sync after data-contract closeout is on `main`. |
| #2292 | merged | Previous 2026-06-01 PROJECT-GOV checkpoint is on `main`. |

### Decision

- The open productization gate sync lane recorded in checkpoint 16 is now drained; no open PRs were found by the GitHub connector search.
- `origin/main@44d9c526a83f1fad60a172895a9bbe7e1db02365` is the current planning input for new work unless a future PR intentionally builds on another branch.
- No branch deletion, PR closure, or ADR status change is executed from this checkpoint. Branch cleanup remains a permissioned repository maintenance action after maintainer confirmation.
- No new ADR is required. ADR-0034 already governs mainline convergence and branch hygiene; this update only refreshes the repository inventory after #2291/#2292 merged.
- Full release shipment remains No-Go until product-value evidence, full release-candidate E2E/viewport/screenshot evidence, Compose startup evidence, and final program approval are recorded.

### Cleanup candidate table

| Branch | Current classification | Cleanup recommendation |
| --- | --- | --- |
| `origin/codex/data-contract-01-closeout-20260601` | merged `DATA-CONTRACT-01` closeout | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/data-maint-01-adr35-routing-20260601` | merged `DATA-MAINT-01` decision routing sync | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/data-maint-04-audit-metadata-baseline-20260601` | merged `DATA-MAINT-04` audit metadata baseline | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/productization-data-contract-gate-sync-20260601` | merged productization gate sync | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/project-gov-20260601-contract-gate-checkpoint` | merged governance checkpoint | Delete only after repository maintainer confirms no post-merge audit need. |

### Updated recommendation

1. Start the next independent work from `origin/main@44d9c526a83f1fad60a172895a9bbe7e1db02365`.
2. Do not open another PROJECT-GOV checkpoint unless `origin/main`, the open PR set, branch cleanup decision, or active issue triage materially changes.
3. Keep branch deletion as a maintainer-approved cleanup task; this issue records candidates but does not perform deletion.
4. Continue routing full release readiness through `PRODUCT-QA-01` and `MVP-EXIT-01`, because the drained PR lane does not itself approve shipment.

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している（未運用時は `N/A`）。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
