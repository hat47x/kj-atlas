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

## 18) Convergence checkpoint 2026-06-03: UI/E2E gate sync merged and CI signal hygiene

### Observation

- Observed after `git fetch --prune origin`, `git pull --ff-only origin main`, GitHub connector open-PR search, and GitHub Actions recent-run inspection on 2026-06-03.
- `origin/main`: `181b077e6b4fb963d99bbd4439e78b3425ed902b`
- remote branch count: 2306
- `origin/codex/` remote branch count: 2283
- open PR count returned by GitHub connector search: 0
- internal issue triage on current `main`:
  - `active_issues=52`
  - `ready=15`
  - `blocked=37`
  - `actionable_adrs=1`
  - stopper: none
- Latest main CI:
  - GitHub Actions run `26877196688`
  - event: `push`
  - head branch: `main`
  - head SHA: `181b077e6b4fb963d99bbd4439e78b3425ed902b`
  - conclusion: `success`

### Recent PR lane resolution

| PR | State | Governance result |
| --- | --- | --- |
| #2304 | merged | Chrome UI operation evidence and human task queue are on `main`. |
| #2305 | merged | First-run sample E2E coverage and the frontend `setup-node` cache dependency path fix are on `main`. |
| #2306 | merged | Invalid locale fallback E2E coverage is on `main`; its old CI failure belongs to the pre-#2305 workflow state. |
| #2307 | merged | Latest main UI/E2E gate sync for `PROJECT-BASELINE-01`, `PRODUCT-QA-01`, and `MVP-EXIT-01` is on `main`. |

### CI signal hygiene classification

| Signal | Current classification | Operational treatment |
| --- | --- | --- |
| `main@181b077e` CI run `26877196688` | current canonical CI signal | Treat as the governing latest-main CI result for this checkpoint. |
| PR #2307 pull-request CI run `26875216218` | current PR evidence, now merged | Retain as supporting evidence for the merged gate-sync PR. |
| Branch `codex/i18n-invalid-locale-e2e-20260603` runs `26874271586` and `26874320457` | stale failure history | Do not treat as a current blocker after #2305/#2306/#2307 are merged and latest `main` CI is green. |
| Earlier `codex/first-run-sample-e2e-20260603@420d03ad...` failure runs | superseded failure history | Do not treat as a current blocker because the branch was later updated and PR #2305 merged with successful CI. |

### Decision

- The UI/E2E evidence lane from #2304 through #2307 is converged into `main`.
- Current latest-main CI is green. Historical red GitHub Actions runs remain visible in repository history, but they are not release or merge blockers unless they match the current candidate SHA, an open PR head SHA, or an intentionally tracked release-candidate SHA.
- When investigating a CI error, use this order before filing or fixing new work:
  1. identify the candidate SHA and whether it is `main`, an open PR head, a merge queue candidate, or a stale branch head;
  2. inspect the latest run for that exact SHA;
  3. classify older failing runs as `current blocker`, `superseded`, `stale history`, or `external/report-only`;
  4. only create implementation work when the current candidate still fails after the relevant workflow and branch have been refreshed.
- No branch deletion, PR closure, rerun, or ADR status change is executed from this checkpoint.
- No new ADR is required. ADR-0034 governs mainline convergence and branch hygiene; this update only clarifies CI signal interpretation inside that governance boundary.
- Full release shipment remains No-Go until product-value Open gates, release-candidate screenshot and physical keyboard evidence, full regression evidence, Compose startup evidence, and final program approval are recorded together.

### Cleanup candidate table

| Branch | Current classification | Cleanup recommendation |
| --- | --- | --- |
| `origin/codex/ui-evidence-human-task-queue-20260603` | merged UI evidence lane | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/first-run-sample-e2e-20260603` | merged E2E coverage lane; old failing run superseded | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/i18n-invalid-locale-e2e-20260603` | merged E2E coverage lane; old failing run superseded | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/latest-main-ui-e2e-gate-sync-20260603` | merged latest-main gate-sync lane | Delete only after repository maintainer confirms no post-merge audit need. |

### Updated recommendation

1. Start the next independent work from `origin/main@181b077e6b4fb963d99bbd4439e78b3425ed902b`.
2. Treat old red GitHub Actions runs as investigation inputs, not as blockers, until they are matched to the current candidate SHA.
3. If the user reports a CI error without a PR number or run URL, first inspect open PRs and the latest `main` run before changing files.
4. Continue recording branch cleanup candidates, but leave deletion to a maintainer-approved repository maintenance action.

## 19) Convergence checkpoint 2026-06-04: product value and baseline evidence draft lane

### Observation

- Observed after `git fetch --prune origin`, `git pull --ff-only`, GitHub connector open-PR search, PR metadata inspection, changed-file inspection, and head-SHA workflow inspection on 2026-06-04.
- `origin/main`: `cb277db730da9f91d22c08cee0cc8af348a92220`
- remote branch count: 2316
- `origin/codex/` remote branch count: 2292
- open PR count returned by GitHub connector search: 6
- internal issue triage on current `main`:
  - `active_issues=52`
  - `ready=15`
  - `blocked=37`
  - `actionable_adrs=1`
  - stopper: none

### Open PR inventory

| PR | Branch | Topic | Head CI | Governance classification | Recommended action |
| --- | --- | --- | --- | --- | --- |
| #2311 | `codex/release-screenshot-capture-20260603` | Reproducible release screenshot script and regenerated public screenshot assets | Success: run `26894285735` | canonical but order-sensitive | Rebase/regenerate after #2314 if #2314 changes the share panel screenshot surface; keep human screenshot approval as a separate release gate. |
| #2312 | `codex/keyboard-operation-evidence-20260604` | H-UI-02 keyboard evidence and `CanvasShell` Space handling fix | Success: run `26896299227` | canonical shared keyboard fix | Prefer before #2315 because both touch `03_Implement/frontend/src/canvas/CanvasShell.tsx`; #2315 should rebase after this PR and drop duplicate Space-handler changes if they become redundant. |
| #2313 | `codex/first-value-mouse-evidence-20260604` | PRODUCT-VALUE-01 first meaningful map mouse evidence | Success: run `26897242309` | canonical evidence candidate | Merge after #2312 or rebase after #2312 because both update PRODUCT-VALUE-01 evidence state; keep PRODUCT-VALUE-01 Draft until human acceptance and release-gate linkage are recorded. |
| #2314 | `codex/review-pack-trace-ui-20260604` | PRODUCT-VALUE-03 review-pack trace UI and E2E evidence | Success: run `26910917230` | canonical UI/evidence candidate | Review before #2311 so screenshot assets can reflect the latest share/export UI copy and layout. |
| #2315 | `codex/domain-expression-keyboard-evidence-20260604` | DOMAIN-EXPR-01 keyboard reachability evidence and the same `CanvasShell` Space-handler guard | Success: run `26917029876` | canonical but overlaps #2312 | Rebase after #2312, then keep only DOMAIN-EXPR-specific E2E/issue evidence plus any still-needed implementation delta. |
| #2316 | `codex/project-baseline-post-2310-20260604` | #2310 documentation-only mainline baseline sync | Success: run `26917382664` | canonical / low-risk docs-only | Merge first if reviewers want the latest `main` evidence baseline before reviewing the product-value and UI evidence lane. |

### Overlap and merge-order notes

| Overlap | PRs | Risk | Recommended handling |
| --- | --- | --- | --- |
| `03_Implement/frontend/src/canvas/CanvasShell.tsx` | #2312 / #2315 | Duplicate Space-handler guard and likely textual conflict if merged independently. | Treat #2312 as the broader keyboard-operation fix, then rebase #2315 on top and keep DOMAIN-EXPR evidence focused. |
| PRODUCT-QA / MVP-EXIT gate records | #2311 / #2312 / #2316 | Append-only planning sections can conflict during merge or produce confusing chronology if merged out of order. | Merge #2316 first as the post-#2310 baseline, then rebase later evidence PRs if the files conflict. |
| PRODUCT-VALUE-01 issue | #2312 / #2313 | Keyboard and mouse evidence for the same value gate may be recorded in separate candidate sections. | Merge or rebase #2312 before #2313 so PRODUCT-VALUE-01 can read as keyboard evidence first, mouse evidence second. |
| Share/export UI surface and screenshots | #2311 / #2314 | Screenshots in #2311 may become stale if #2314 changes share-panel copy or controls. | Review #2314 first; rerun #2311 screenshot capture if share/export screenshot content changes. |

### Recommended merge lane

1. Merge #2316 first if maintainers want the current #2310 documentation-only baseline on `main` before product-value evidence PRs.
2. Review #2314 before #2311, then rebase or regenerate #2311 screenshot assets if the share/export surface changed.
3. Review #2312 before #2315 because #2312 is the broader keyboard-operation fix for the shared `CanvasShell` Space handling.
4. Rebase #2315 after #2312 and treat it as DOMAIN-EXPR-01 evidence, not as a second copy of the generic keyboard fix.
5. Merge or rebase #2313 after #2312 so PRODUCT-VALUE-01 evidence chronology stays coherent.
6. Keep every PR as draft until the maintainer decides whether these evidence slices should be reviewed as release-candidate inputs or held for a bundled productization pass.

### Cleanup candidate table

| Branch | Current classification | Cleanup recommendation |
| --- | --- | --- |
| `origin/codex/release-screenshot-capture-20260603` | open canonical screenshot evidence PR | Keep until #2311 is merged/closed; delete only after maintainer confirms no post-merge audit need. |
| `origin/codex/keyboard-operation-evidence-20260604` | open canonical keyboard operation PR | Keep until #2312 is merged/closed; delete only after maintainer confirms no post-merge audit need. |
| `origin/codex/first-value-mouse-evidence-20260604` | open canonical PRODUCT-VALUE-01 mouse evidence PR | Keep until #2313 is merged/closed; delete only after maintainer confirms no post-merge audit need. |
| `origin/codex/review-pack-trace-ui-20260604` | open canonical PRODUCT-VALUE-03 review-pack evidence PR | Keep until #2314 is merged/closed; delete only after maintainer confirms no post-merge audit need. |
| `origin/codex/domain-expression-keyboard-evidence-20260604` | open canonical DOMAIN-EXPR-01 keyboard evidence PR with #2312 overlap | Keep until #2315 is merged/closed; rebase after #2312 if #2312 lands first. |
| `origin/codex/project-baseline-post-2310-20260604` | open canonical baseline-sync PR | Keep until #2316 is merged/closed; delete only after maintainer confirms no post-merge audit need. |

### Decision

- The current open PR lane is healthy from a CI perspective: all six open PR head SHAs have successful CI runs and are reported mergeable.
- The lane is not safe to merge blindly because there are known textual or evidence-order overlaps in `CanvasShell.tsx`, PRODUCT-QA/MVP-EXIT gate records, PRODUCT-VALUE-01, and release screenshot assets.
- No branch deletion, PR closure, ready-for-review transition, merge, rerun, or ADR status change is executed from this checkpoint.
- No new ADR is required. ADR-0034 governs mainline convergence and branch hygiene; this update only refreshes the active PR lane and recommended review order.
- Full release shipment remains No-Go until product-value Open gates, release-candidate screenshot and physical keyboard evidence, full regression evidence, Compose startup evidence, and final program approval are recorded together.

### Updated recommendation

1. Start new independent work from `origin/main@cb277db730da9f91d22c08cee0cc8af348a92220` unless intentionally updating one of #2311..#2316.
2. Before changing `CanvasShell.tsx`, inspect #2312 and #2315 because they already carry a shared Space-key fix.
3. Before regenerating release screenshots, inspect #2314 because it can change the share/export surface.
4. Treat the six open branches as cleanup candidates only after their PRs are merged or closed, and leave deletion to a maintainer-approved repository maintenance action.

---

## Post-2318 mainline convergence checkpoint

- Checkpoint date (JST): 2026-06-04
- Latest main: `origin/main@f04c45c473422047472af35cec1c431b835f621d`
- GitHub open PR search result: `0`
- Scope: refreshes the prior open-PR lane record after #2311, #2312, #2313, #2314, #2315, #2316, and #2318 were merged. This checkpoint supersedes the older merge-lane ordering guidance; it does not delete remote branches or change ADR status.

### Merged lane result

| PR | Former branch | Merge result | Governance outcome |
| --- | --- | --- | --- |
| #2311 | `codex/release-screenshot-capture-20260603` | Merged as `c2ec54680dd7907bbf77c329b4a386b97d034d17` | Screenshot capture lane is now canonical on `main`; human screenshot approval remains a release gate. |
| #2312 | `codex/keyboard-operation-evidence-20260604` | Merged as `fb22b7c6600fbb0871ca2f2caf15dee0d018e3f6` | Generic keyboard-operation evidence is canonical; physical-keyboard acceptance remains a release gate. |
| #2313 | `codex/first-value-mouse-evidence-20260604` | Merged as `cfeedc4635d47978e9f8f01f838d7490ddb2a62b` | PRODUCT-VALUE-01 mouse evidence candidate is canonical but not yet product-value Open approval. |
| #2314 | `codex/review-pack-trace-ui-20260604` | Merged as `0c5253fc252a4cbd1bd795252258993355cf933c` | Review-pack trace UI/evidence is canonical; PRODUCT-VALUE-03 remains issue-gated. |
| #2315 | `codex/domain-expression-keyboard-evidence-20260604` | Merged as `7514aeca94a615fa13e36598ea919ca1d0219b11` | DOMAIN-EXPR-01 keyboard evidence candidate is canonical; acceptance remains routed through DOMAIN-EXPR issue state. |
| #2316 | `codex/project-baseline-post-2310-20260604` | Merged as `46043beca958319d1345b7ff4ff908cde9a0f8db` | #2310 documentation-only baseline was canonical, then superseded by the post-2318 baseline sync. |
| #2318 | `codex/env-test-harness-prefix-20260604` | Merged as `f04c45c473422047472af35cec1c431b835f621d` | Env-prefix harness alignment and current frontend CI repair are canonical on `main`. |

### Residual branch hygiene

| Item | Current state | Recommended handling |
| --- | --- | --- |
| Open PR lane | No open PRs returned by GitHub connector search | Start new work from `origin/main@f04c45c473422047472af35cec1c431b835f621d`. |
| Previously overlapping `CanvasShell.tsx` fixes | Resolved by merged #2312/#2315 and repaired by #2318 | Inspect current `main` before further Space-key or canvas shortcut changes; do not resurrect branch-local handler variants. |
| Remote branch cleanup | Merged branch refs may still exist on `origin` | Treat deletion as a maintainer-owned repository maintenance action; do not delete branches from this checkpoint. |
| Release evidence records | PRODUCT-QA, MVP-EXIT, and PROJECT-BASELINE are aligned by the post-2318 records in this sync | Route release-readiness status through those issues; do not rely on the superseded #2310-only decision. |

### Decision

- The previous open-PR convergence lane is complete: all seven relevant PRs are merged, and the open PR count is now zero.
- No branch deletion, rerun, ADR status change, or release approval is executed from this checkpoint.
- No new ADR is required. ADR-0034 remains sufficient for mainline convergence and branch hygiene; this update only records the changed repository state.
- Full release shipment remains No-Go until product-value Open gates, release-candidate screenshot and physical keyboard approval, full regression evidence, Compose startup evidence, support diagnostics/recovery rehearsal, and final program approval are recorded together.

### Updated recommendation

1. Start new independent work from `origin/main@f04c45c473422047472af35cec1c431b835f621d`.
2. Treat #2311..#2316 and #2318 as mainline evidence, not candidate PR evidence.
3. Before opening new UI/E2E evidence work, check the current issue state for `PRODUCT-QA-01`, `MVP-EXIT-01`, `PROJECT-BASELINE-01`, and the relevant product-value/domain-expression issue.
4. Leave remote branch deletion to a maintainer-approved cleanup action after any required post-merge audit window.

---

## Post-2327 convergence checkpoint

- Checkpoint date (JST): 2026-06-06
- Latest main: `origin/main@0161e54f191ba2600796680bf605ec571d948b94`
- Remote branch count: 2327
- `origin/codex/` remote branch count: 2303
- GitHub open PR search result: `0`
- Internal issue triage:
  - `active_issues=52`
  - `ready=15`
  - `blocked=37`
  - `actionable_adrs=1`
  - stopper: none
- Scope: refreshes branch/PR governance after #2319 through #2327 were merged. This checkpoint does not delete remote branches, close PRs, change ADR status, change runtime behavior, or approve release readiness.

### Merged lane result

| PR | Former branch | Merge result | Governance outcome |
| --- | --- | --- | --- |
| #2319 | `codex/post-2318-mainline-gate-sync-20260604` | Merged as `d1dfa3a0c50892d8d7aa354a5e83ba760e043919` | Post-2318 PRODUCT-QA, MVP-EXIT, PROJECT-BASELINE, and PROJECT-GOV gate sync is canonical on `main`. |
| #2320 | `codex/product-value-01-mainline-evidence-intake-20260604` | Merged as `70b6269a24d01c6f4b386e5b7a724738dd02e2bd` | PRODUCT-VALUE-01 mainline evidence intake is canonical; product-value acceptance remains Draft-gated. |
| #2321 | `codex/product-value-03-mainline-evidence-intake-20260604` | Merged as `3037f4ae80d75eb1957f81d3d1039f8ffdaa94b7` | PRODUCT-VALUE-03 mainline evidence intake is canonical; reviewable outcome acceptance remains Draft-gated. |
| #2322 | `codex/domain-expr-01-mainline-evidence-intake-20260604` | Merged as `8f3ea92a36d080f278931393e727abf242ce6fb5` | DOMAIN-EXPR-01 mainline evidence intake is canonical; Phase 1 acceptance remains Draft-gated. |
| #2323 | `codex/product-value-02-evidence-gap-sync-20260604` | Merged as `0133c744b60e4cc5f0c48435a62c72fbb5ca9f52` | PRODUCT-VALUE-02 evidence gap sync is canonical; implementation remains gated by a complete value evidence packet. |
| #2324 | `codex/domain-expr-02-open-gate-sync-20260604` | Merged as `ba66911b55e70adff946e11fea7eecacd841807a` | DOMAIN-EXPR-02 open-gate sync is canonical; Hold/Shelf schema and workflow implementation remain unapproved. |
| #2325 | `codex/domain-expr-03-open-gate-sync-20260604` | Merged as `5b2aeb90ef7514797856b3bab57b74970d6bb9fc` | DOMAIN-EXPR-03 open-gate sync is canonical; critique/reproposal contracts remain pending. |
| #2326 | `codex/domain-expr-04-open-gate-sync-20260604` | Merged as `7bc630e50882985defeccc635bef6f61210942e3` | DOMAIN-EXPR-04 open-gate sync is canonical; evidence/claim/contradiction implementation remains contract-gated. |
| #2327 | `codex/project-baseline-post-2326-sync-20260606` | Merged as `0161e54f191ba2600796680bf605ec571d948b94` | PROJECT-BASELINE post-2326 internal evidence sync is canonical on `main`. |

### Cleanup candidate table

| Branch | Current classification | Cleanup recommendation |
| --- | --- | --- |
| `origin/codex/post-2318-mainline-gate-sync-20260604` | merged internal gate sync | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/product-value-01-mainline-evidence-intake-20260604` | merged product-value evidence intake | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/product-value-03-mainline-evidence-intake-20260604` | merged product-value evidence intake | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/domain-expr-01-mainline-evidence-intake-20260604` | merged domain-expression evidence intake | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/product-value-02-evidence-gap-sync-20260604` | merged product-value gap sync | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/domain-expr-02-open-gate-sync-20260604` | merged domain-expression open-gate sync | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/domain-expr-03-open-gate-sync-20260604` | merged domain-expression open-gate sync | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/domain-expr-04-open-gate-sync-20260604` | merged domain-expression open-gate sync | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/project-baseline-post-2326-sync-20260606` | merged latest-main baseline sync | Delete only after repository maintainer confirms no post-merge audit need. |

### Decision

- The post-2318 and post-2326 internal evidence lane is converged into `main`; the GitHub connector reports no open PRs.
- No branch deletion, PR closure, rerun, ADR status change, implementation authorization, or release approval is executed from this checkpoint.
- No new ADR is required. ADR-0034 remains sufficient for mainline convergence and branch hygiene; this update only records the changed repository state.
- Full release shipment remains No-Go until product-value Open gates, release-candidate screenshot and physical-keyboard approval, full regression evidence, Compose startup evidence, support diagnostics/recovery rehearsal, and final program approval are recorded together.

### Updated recommendation

1. Start new independent work from `origin/main@0161e54f191ba2600796680bf605ec571d948b94`.
2. Treat #2319..#2327 as mainline evidence, not open candidate PR evidence.
3. Keep branch deletion as a maintainer-approved repository maintenance action. The table above is an audit aid, not execution permission.
4. Route product-value and domain-expression implementation decisions through their Draft issues before changing schema, SafeMode/share-export behavior, or AI authority.

---

## Post-2334 convergence checkpoint

- Checkpoint date (JST): 2026-06-06
- Latest main: `origin/main@27862b21c71cbb1c26ddb58722e2f9dee3046b20`
- Remote branch count: 2335
- `origin/codex/` remote branch count: 2311
- GitHub open PR search result: 1
- Internal issue triage:
  - `active_issues=52`
  - `ready=15`
  - `blocked=37`
  - `actionable_adrs=1`
  - stopper: none
- Scope: refreshes repository governance after #2328 through #2334 were merged and while #2335 remains the single open PR. This checkpoint does not delete remote branches, close PRs, rerun CI, change ADR status, change runtime behavior, or approve release readiness.

### Merged lane result

| PR | Former branch | Merge result | Governance outcome |
| --- | --- | --- | --- |
| #2328 | `codex/project-gov-post-2327-checkpoint-20260606` | Merged as `4306ed1e` | Post-2327 project-governance checkpoint is canonical on `main`. |
| #2329 | `codex/project-baseline-post-2328-sync-20260606` | Merged as `cde40a54` | Post-2328 project-baseline sync is canonical on `main`. |
| #2330 | `codex/product-qa-post-2329-gate-sync-20260606` | Merged as `091e49cd` | PRODUCT-QA post-2329 gate sync is canonical on `main`. |
| #2331 | `codex/mvp-exit-data-lifecycle-boundary-sync-20260606` | Merged as `0fc84859` | MVP-EXIT high-privilege data lifecycle boundary sync is canonical on `main`. |
| #2332 | `codex/data-maint-04-open-readiness-20260606` | Merged as `ed29ea90` | DATA-MAINT-04 Open-readiness decision packet clarification is canonical on `main`; the issue remains Draft-gated. |
| #2333 | `codex/product-qa-post-2331-data-lifecycle-sync-20260606` | Merged as `3f894ca7` | PRODUCT-QA post-2332 data lifecycle release-gate interpretation is canonical on `main`. |
| #2334 | `codex/env-prefix-adr-readability-sync-20260606` | Merged as `27862b21` | ADR-0021 public-prefix readability sync is canonical on `main`; public env keys remain `KJ_ATLAS_*` only. |

### Open PR inventory

| PR | Branch | Topic | Governance classification | Recommended action |
| --- | --- | --- | --- | --- |
| #2335 | `codex/legacy-env-reference-adr-sync-20260606` | Historical ADR key-name normalization from legacy env examples to `KJ_ATLAS_*` | independent canonical / merge-ready | Review and merge independently. It is documentation-only and does not authorize runtime, SafeMode, share/export, LLM, audit, access-control, or Compose behavior changes. |

### Cleanup candidate table

| Branch | Current classification | Cleanup recommendation |
| --- | --- | --- |
| `origin/codex/project-gov-post-2327-checkpoint-20260606` | merged project-governance checkpoint | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/project-baseline-post-2328-sync-20260606` | merged project-baseline sync | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/product-qa-post-2329-gate-sync-20260606` | merged PRODUCT-QA gate sync | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/mvp-exit-data-lifecycle-boundary-sync-20260606` | merged MVP-EXIT boundary sync | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/data-maint-04-open-readiness-20260606` | merged DATA-MAINT-04 readiness clarification | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/product-qa-post-2331-data-lifecycle-sync-20260606` | merged PRODUCT-QA data lifecycle sync | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/env-prefix-adr-readability-sync-20260606` | merged ADR-0021 readability sync | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/legacy-env-reference-adr-sync-20260606` | open canonical documentation-only PR | Keep until #2335 is merged or closed. |

### Decision

- The post-2327 internal governance, baseline, product QA, MVP-EXIT, DATA-MAINT, and ADR-0021 readability lane is converged into `main`.
- The only open PR is #2335. It is independent and documentation-only, so it should not block unrelated work that starts from `origin/main@27862b21c71cbb1c26ddb58722e2f9dee3046b20`.
- No branch deletion, PR closure, rerun, ADR status change, implementation authorization, or release approval is executed from this checkpoint.
- No new ADR is required. ADR-0034 remains sufficient for mainline convergence and branch hygiene; this update only records the changed repository state.
- Full release shipment remains No-Go until product-value Open gates, release-candidate screenshot and physical-keyboard approval, full regression evidence, Compose startup evidence, support diagnostics/recovery rehearsal, and final program approval are recorded together.

### Updated recommendation

1. Start new independent work from `origin/main@27862b21c71cbb1c26ddb58722e2f9dee3046b20` unless intentionally updating #2335.
2. Treat #2328..#2334 as mainline evidence, not open candidate PR evidence.
3. Treat #2335 as the only current open PR lane and keep its branch until merge or closure.
4. Keep remote branch deletion as a maintainer-approved repository maintenance action. The cleanup table is an audit aid, not execution permission.

---

## Post-2366 convergence checkpoint

- Checkpoint date (JST): 2026-06-13
- Latest main: `origin/main@4a632f68cebd8888cfff1338d2ae7ca885177fb4`
- GitHub open PR search result: `0`
- Recent merged branch refs still present on origin:
  - `codex/data-maint-03-decision-freshness-20260613`
  - `codex/product-qa-data-lifecycle-gate-sync-20260613`
  - `codex/env-config-docker-handoff-20260613`
  - `codex/product-qa-env-config-docker-gate-20260613`
  - `codex/project-baseline-post-2365-20260613`
- Internal issue triage:
  - `active_issues=52`
  - `ready=15`
  - `blocked=37`
  - `actionable_adrs=1`
  - stopper: none
- Scope: refreshes repository governance after #2362 through #2366 were merged. This checkpoint records current mainline convergence and cleanup candidates only; it does not delete remote branches, close PRs, rerun CI, change ADR status, change runtime behavior, or approve release readiness.

### Merged lane result

| PR | Former branch | Merge result | Governance outcome |
| --- | --- | --- | --- |
| #2362 | `codex/data-maint-03-decision-freshness-20260613` | Merged as `dd5dfb8d` | High-privilege data-lifecycle decision handoff is canonical on `main`; `ADR-0035` and related issues remain decision-gated. |
| #2363 | `codex/product-qa-data-lifecycle-gate-sync-20260613` | Merged as `4c445b42` | PRODUCT-QA high-privilege lifecycle freshness gate is canonical; full release remains No-Go. |
| #2364 | `codex/env-config-docker-handoff-20260613` | Merged as `44b2256b` | ENV-CONFIG Docker-capable host handoff is canonical; `docker compose config` evidence remains platform-operator owned. |
| #2365 | `codex/product-qa-env-config-docker-gate-20260613` | Merged as `73d68c7e` | PRODUCT-QA environment-config handoff gate is canonical; live Compose rehearsal remains Hold. |
| #2366 | `codex/project-baseline-post-2365-20260613` | Merged as `4a632f68` | PROJECT-BASELINE post-2365 data-lifecycle and environment-handoff sync is canonical on `main`. |

### Cleanup candidate table

| Branch | Current classification | Cleanup recommendation |
| --- | --- | --- |
| `origin/codex/data-maint-03-decision-freshness-20260613` | merged data-lifecycle decision handoff | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/product-qa-data-lifecycle-gate-sync-20260613` | merged PRODUCT-QA gate sync | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/env-config-docker-handoff-20260613` | merged environment-config handoff | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/product-qa-env-config-docker-gate-20260613` | merged PRODUCT-QA environment gate sync | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/project-baseline-post-2365-20260613` | merged latest-main baseline sync | Delete only after repository maintainer confirms no post-merge audit need. |

### Decision

- The post-2362 data-lifecycle, PRODUCT-QA, environment-config, and PROJECT-BASELINE lane is converged into `main`.
- GitHub connector search reports no open PRs for the repository at this checkpoint.
- No branch deletion, PR closure, rerun, ADR status change, implementation authorization, or release approval is executed from this checkpoint.
- No new ADR is required. ADR-0034 remains sufficient for mainline convergence and branch hygiene; this update only records the changed repository state.
- Full release shipment remains No-Go until product-value Open gates, human release screenshots, physical keyboard acceptance, screen-reader acceptance, full Compose startup, support diagnostics/recovery rehearsal, accepted high-privilege lifecycle boundary decisions, environment rehearsal evidence, and final program approval are recorded together.

### Updated recommendation

1. Start new independent work from `origin/main@4a632f68cebd8888cfff1338d2ae7ca885177fb4`.
2. Treat #2362..#2366 as mainline evidence, not open candidate PR evidence.
3. Keep the five recent remote branch refs as cleanup candidates only; deletion remains a maintainer-approved repository maintenance action.
4. Route remaining release blockers through `PRODUCT-QA-01`, `MVP-EXIT-01`, `ENV-CONFIG-DRIFT-01`, `PRODUCT-OPS-01`, `PRODUCT-VALUE-01..03`, `ADR-0035`, and `DATA-MAINT-03/04`.

---

## Post-2372 convergence checkpoint

- Checkpoint date (JST): 2026-06-13
- Latest main: `origin/main@865e2514e266825bac9f504c1d27b65c5b76a533`
- GitHub open PR search result: `0`
- Recent merged branch refs still present on origin:
  - `codex/fb-p0-current-main-checkpoint-20260613`
  - `codex/product-qa-fb-p0-checkpoint-20260613`
  - `codex/project-baseline-fb-p0-checkpoint-20260613`
  - `codex/mvp-exit-fb-p0-boundary-20260613`
- Internal issue triage:
  - `active_issues=52`
  - `ready=15`
  - `blocked=37`
  - `actionable_adrs=1`
  - stopper: none
- Scope: refreshes repository governance after #2369 through #2372 were merged. This checkpoint records current mainline convergence and cleanup candidates only; it does not delete remote branches, close PRs, rerun CI, change ADR status, change runtime behavior, change FB-P0 approval state, or approve release readiness.

### Merged lane result

| PR | Former branch | Merge result | Governance outcome |
| --- | --- | --- | --- |
| #2369 | `codex/fb-p0-current-main-checkpoint-20260613` | Merged as `97194275` | FB-P0/P2C current-main checkpoint is canonical on `main`; `fixedKeyDrift=0` and `pendingBypassDetected=false` are recorded as planning-boundary evidence. |
| #2370 | `codex/product-qa-fb-p0-checkpoint-20260613` | Merged as `87272a3b` | PRODUCT-QA FB-P0 planning-boundary gate is canonical; full release remains No-Go. |
| #2371 | `codex/project-baseline-fb-p0-checkpoint-20260613` | Merged as `eea59739` | PROJECT-BASELINE FB-P0 checkpoint sync is canonical on `main`. |
| #2372 | `codex/mvp-exit-fb-p0-boundary-20260613` | Merged as `865e2514` | MVP-EXIT FB-P0 planning-boundary Program Gate intake is canonical; final shipment approval remains blocked. |

### Cleanup candidate table

| Branch | Current classification | Cleanup recommendation |
| --- | --- | --- |
| `origin/codex/fb-p0-current-main-checkpoint-20260613` | merged FB-P0 current-main checkpoint | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/product-qa-fb-p0-checkpoint-20260613` | merged PRODUCT-QA FB-P0 gate sync | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/project-baseline-fb-p0-checkpoint-20260613` | merged PROJECT-BASELINE FB-P0 sync | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/mvp-exit-fb-p0-boundary-20260613` | merged MVP-EXIT FB-P0 boundary sync | Delete only after repository maintainer confirms no post-merge audit need. |

### Decision

- The post-2369 FB-P0 planning-boundary lane is converged into `main`.
- GitHub connector search reports no open PRs for the repository at this checkpoint.
- No branch deletion, PR closure, rerun, ADR status change, implementation authorization, FB-P0 approval change, or release approval is executed from this checkpoint.
- No new ADR is required. ADR-0034 remains sufficient for mainline convergence and branch hygiene; this update only records the changed repository state.
- Full release shipment remains No-Go until product-value Open gates, human release screenshots, physical keyboard acceptance, screen-reader acceptance, full Compose startup, support diagnostics/recovery rehearsal, accepted high-privilege lifecycle boundary decisions, environment rehearsal evidence, FB-P0 approval/held decisioning, and final program approval are recorded together.

### Updated recommendation

1. Start new independent work from `origin/main@865e2514e266825bac9f504c1d27b65c5b76a533`.
2. Treat #2369..#2372 as mainline evidence, not open candidate PR evidence.
3. Keep the four recent FB-P0 remote branch refs as cleanup candidates only; deletion remains a maintainer-approved repository maintenance action.
4. Route remaining release blockers through `PRODUCT-QA-01`, `MVP-EXIT-01`, `FB-P0-2A2B2C`, `HIL-RS-02-GOV-EXCEPTION-01`, `ENV-CONFIG-DRIFT-01`, `PRODUCT-OPS-01`, `PRODUCT-VALUE-01..03`, `ADR-0035`, and `DATA-MAINT-03/04`.

---

## Post-2377 convergence checkpoint

- Checkpoint date (JST): 2026-06-14
- Latest main: `origin/main@76b3fe22c34a389fe30bfbaf45a3c8ef4d5aaf5c`
- Remote branch count: 2372
- `origin/codex/` remote branch count: 2348
- GitHub open PR search result: `0`
- Recent merged branch refs still present on origin:
  - `codex/start-panel-focus-scope-20260613`
  - `codex/product-qa-start-panel-focus-gate-20260614`
  - `codex/project-baseline-start-panel-focus-20260614`
  - `codex/mvp-exit-start-panel-focus-20260614`
- Prior governance checkpoint branch still present on origin:
  - `codex/project-gov-post-2372-checkpoint-20260613`
- Internal issue triage:
  - `active_issues=52`
  - `ready=15`
  - `blocked=37`
  - `actionable_adrs=1`
  - stopper: none
- Scope: refreshes repository governance after #2374 through #2377 were merged. This checkpoint records current mainline convergence and cleanup candidates only; it does not delete remote branches, close PRs, rerun CI, change ADR status, change runtime behavior, change UI behavior, or approve release readiness.

### Merged lane result

| PR | Former branch | Merge result | Governance outcome |
| --- | --- | --- | --- |
| #2374 | `codex/start-panel-focus-scope-20260613` | Merged as `cdbe4f9d` | First-run start-panel focus-scope repair is canonical on `main`; `QA-MONKEY-09` is Done for the targeted focus containment defect. |
| #2375 | `codex/product-qa-start-panel-focus-gate-20260614` | Merged as `44c3dcd3` | PRODUCT-QA start-panel focus gate record is canonical; full release remains No-Go. |
| #2376 | `codex/project-baseline-start-panel-focus-20260614` | Merged as `0d18a663` | PROJECT-BASELINE post-2375 start-panel focus sync is canonical on `main`. |
| #2377 | `codex/mvp-exit-start-panel-focus-20260614` | Merged as `76b3fe22` | MVP-EXIT post-2376 start-panel focus Program Gate intake is canonical; final shipment approval remains blocked. |

### Cleanup candidate table

| Branch | Current classification | Cleanup recommendation |
| --- | --- | --- |
| `origin/codex/start-panel-focus-scope-20260613` | merged first-run focus-scope repair | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/product-qa-start-panel-focus-gate-20260614` | merged PRODUCT-QA gate sync | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/project-baseline-start-panel-focus-20260614` | merged PROJECT-BASELINE sync | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/mvp-exit-start-panel-focus-20260614` | merged MVP-EXIT gate sync | Delete only after repository maintainer confirms no post-merge audit need. |
| `origin/codex/project-gov-post-2372-checkpoint-20260613` | merged prior governance checkpoint | Delete only after repository maintainer confirms no post-merge audit need. |

### Decision

- The post-2374 first-run focus-scope repair, PRODUCT-QA gate record, PROJECT-BASELINE sync, and MVP-EXIT Program Gate intake lane is converged into `main`.
- GitHub connector search reports no open PRs for the repository at this checkpoint.
- No branch deletion, PR closure, rerun, ADR status change, implementation authorization, UI redesign approval, accessibility acceptance, or release approval is executed from this checkpoint.
- No new ADR is required. ADR-0034 remains sufficient for mainline convergence and branch hygiene; ADR-0030 and ADR-0031 continue to govern broader UI operability and productization screen architecture.
- Full release shipment remains No-Go until product-value Open gates, human release screenshots, physical keyboard acceptance, screen-reader acceptance, full Compose startup, support diagnostics/recovery rehearsal, accepted high-privilege lifecycle boundary decisions, environment rehearsal evidence, FB-P0 approval/held decisioning, and final program approval are recorded together.

### Updated recommendation

1. Start new independent work from `origin/main@76b3fe22c34a389fe30bfbaf45a3c8ef4d5aaf5c`.
2. Treat #2374..#2377 as mainline evidence, not open candidate PR evidence.
3. Keep the four recent start-panel remote branch refs and the prior governance checkpoint branch as cleanup candidates only; deletion remains a maintainer-approved repository maintenance action.
4. Route remaining release blockers through `PRODUCT-QA-01`, `MVP-EXIT-01`, `PROJECT-BASELINE-01`, `FB-P0-2A2B2C`, `ENV-CONFIG-DRIFT-01`, `PRODUCT-OPS-01`, `PRODUCT-VALUE-01..03`, `ADR-0035`, and `DATA-MAINT-03/04`.

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している（未運用時は `N/A`）。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
- [x] PROJECT-GOV post-2380 branch reachability checkpoint appended below.

---

## Post-2380 codex branch reachability checkpoint

- Checkpoint date (JST): 2026-06-14
- Latest main: `origin/main@7cd251f0bc4943f14dd8c2c416c45083b783ca02`
- Integration PR: #2380 `[codex] Merge codex branches since 2026-06-06`
- Integration method: normal merge commit, not squash/rebase, so selected `codex/*` branch tips are reachable from `main`.
- Remote branch count: 2381
- `origin/codex/` remote branch count: 2356
- `origin/codex/*` branches updated on or after 2026-06-06: 54
- `origin/codex/*` branches updated on or after 2026-06-06 that are not ancestors of `origin/main`: 0
- GitHub open PR search result: `0`
- Internal issue triage at integration time:
  - `active_issues=52`
  - `ready=15`
  - `blocked=37`
  - `actionable_adrs=1`
  - stopper: none
- Scope: records the branch-reachability result after #2380 merged 34 previously non-ancestor `codex/*` branch tips from 2026-06-06 onward. This checkpoint does not delete remote branches, close PRs, rerun old branch CI, change ADR status, change runtime behavior, or approve release readiness.

### Merged lane result

| Merge group | Count | Merge behavior | Governance outcome |
| --- | ---: | --- | --- |
| Real content delta | 1 branch | Normal merge with conflict resolution | `codex/reapply-legacy-env-reference-sync-20260606` restored one historical finding line in `ENV-CONFIG-DRIFT-01`; no runtime behavior changed. |
| Squash-equivalent branch tips | 33 branches | `-s ours` merge commits after `git cherry origin/main <branch>` showed patch-equivalent content already present on `main` | Branch tips are now reachable from `main` without reapplying duplicate document/test changes. |
| Total integrated branch tips | 34 branches | Normal merge PR #2380 | 6/6-or-later `codex/*` branch reachability audit now reports zero non-ancestor branches. |

### Decision

- The 2026-06-06-or-later `codex/*` branch reachability lane is converged into `main`.
- GitHub connector search reports no open PRs for the repository at this checkpoint.
- No branch deletion is executed. The remote `codex/*` refs remain cleanup candidates until the repository maintainer explicitly approves deletion.
- No new ADR is required. ADR-0034 remains sufficient for mainline convergence and branch hygiene; this update records repository state rather than changing branch-governance policy.
- Full release shipment remains No-Go until product-value Open gates, human release screenshots, physical keyboard acceptance, screen-reader acceptance, full Compose startup, support diagnostics/recovery rehearsal, accepted high-privilege lifecycle boundary decisions, environment rehearsal evidence, FB-P0 approval/held decisioning, and final program approval are recorded together.

### Updated recommendation

1. Start new independent work from `origin/main@7cd251f0bc4943f14dd8c2c416c45083b783ca02`.
2. Treat #2380 as a reachability merge only. It makes selected branch tips ancestors of `main`; it does not re-open their old implementation or evidence decisions.
3. Before deleting any remote `codex/*` branch, require repository-maintainer approval and preserve a final audit list of deleted refs.
4. Continue routing release blockers through `PRODUCT-QA-01`, `MVP-EXIT-01`, `PROJECT-BASELINE-01`, `FB-P0-2A2B2C`, `ENV-CONFIG-DRIFT-01`, `PRODUCT-OPS-01`, `PRODUCT-VALUE-01..03`, `ADR-0035`, and `DATA-MAINT-03/04`.

---

## Post-2383 final branch-tip reachability checkpoint

- Checkpoint date (JST): 2026-06-14
- Latest main: `origin/main@0d7a90634f24c3a8fa738f4f8c68dc61f7ec646e`
- Integration PR: #2383 `[codex] Merge post-2381 branch tips`
- Integration method: normal merge commit, not squash/rebase.
- `origin/codex/*` branches updated on or after 2026-06-06: 57
- `origin/codex/*` branches updated on or after 2026-06-06 that are not ancestors of `origin/main`: 0
- Internal issue triage:
  - `active_issues=52`
  - `ready=15`
  - `blocked=37`
  - `actionable_adrs=1`
  - stopper: none
- Scope: records the final branch-tip reachability state after #2383 made the post-#2380 documentation branch tips reachable from `main`. This checkpoint does not delete branches, change release readiness, change runtime behavior, alter ADR status, or close any issue.

### Decision

- The 2026-06-06-or-later `codex/*` branch reachability audit is complete for the observed remote refs: no checked branch remains outside `main` ancestry.
- The remaining remote `codex/*` refs are cleanup candidates only. Deletion still requires repository-maintainer approval and a final deletion audit list.
- No new ADR is required. ADR-0034 remains sufficient for mainline convergence and branch hygiene.
- Future documentation PRs that exist only to record branch reachability should be normal-merged when the purpose is ancestry repair; otherwise they will recreate the same squash-merge reachability gap.

---

## Post-2388 governance reachability checkpoint

- Checkpoint date (JST): 2026-06-14
- Latest main: `origin/main@1f87e01c5a3c083b32997500435298c082158d2e`
- Recent normal-merge PRs included in this checkpoint:
  - #2384 `[codex] Record final branch reachability`
  - #2385 `[codex] Order project baseline reachability sections`
  - #2386 `[codex] Record branch reachability release gates`
  - #2387 `[codex] Refresh DATA-MAINT-03 decision status`
  - #2388 `[codex] Record post-2387 mainline baseline`
- Integration method: normal merge commits, not squash/rebase, so the related `codex/*` branch tips remain reachable from `main`.
- Remote branch count: 2364
- `origin/codex/*` branches updated on or after 2026-06-06: 44
- `origin/codex/*` branches updated on or after 2026-06-06 that are not ancestors of `origin/main`: 0
- GitHub open PR search result: `0`
- Internal issue validation:
  - `validate_active_issue_memos.py`: pass, `ok: validated 5 active issue memos`
  - `test_validate_active_issue_memos.py`: pass, 10 tests
- Scope: records repository governance after #2384 through #2388 were merged. This checkpoint does not delete remote branches, close PRs, change issue status, change ADR status, change runtime behavior, change UI/API behavior, or approve release readiness.

### Decision

- The observed 2026-06-06-or-later `codex/*` branch reachability state remains clean after the post-2383 documentation and release-gate records: no checked branch remains outside `main` ancestry.
- #2387 confirms the high-privilege data-lifecycle decision boundary is still human-owned: `DATA-MAINT-03` remains `DecisionStatus=Pending`, `ADR-0035` remains `Proposed`, and `DATA-MAINT-04` remains Draft.
- #2388 confirms the latest PROJECT-BASELINE record is canonical on `main`, with full release readiness still No-Go.
- The remaining remote `codex/*` refs are cleanup candidates only. Deletion still requires repository-maintainer approval and a final deletion audit list.
- No new ADR is required. ADR-0034 remains sufficient for mainline convergence and branch hygiene unless the project changes stale-ref retention, branch cleanup authority, or release authority.

### Updated recommendation

1. Start new independent work from `origin/main@1f87e01c5a3c083b32997500435298c082158d2e`.
2. Keep using normal merge commits for PRs whose purpose is to preserve `codex/*` branch-tip reachability.
3. Do not delete remote `codex/*` branches from this issue; route that action through repository-maintainer approval.
4. Route release blockers through `PRODUCT-QA-01`, `MVP-EXIT-01`, `PROJECT-BASELINE-01`, `FB-P0-2A2B2C`, `ENV-CONFIG-DRIFT-01`, `PRODUCT-OPS-01`, `PRODUCT-VALUE-01..03`, `ADR-0035`, and `DATA-MAINT-03/04`.

---

## Post-2399 governance reachability and CI recovery checkpoint

- Checkpoint date (JST): 2026-06-15
- Latest main: `origin/main@e2daa3b3120e30e0d39f5c7ac35ee1b4243b79d4`
- Recent normal-merge PRs included in this checkpoint:
  - #2395 `[codex] Refresh CE0 current-main checkpoint`
  - #2396 `[codex] Refresh CE1 contract handoff checkpoint`
  - #2397 `[codex] Record CE2 draft readiness after CE checkpoints`
  - #2398 `[codex] Record CE4 draft readiness after CE checkpoints`
  - #2399 `[codex] Refresh DATA-MAINT-03 governance checkpoint`
- Integration method: normal merge commits, not squash/rebase, so the related `codex/*` branch tips remain reachable from `main`.
- GitHub Actions CI:
  - #2399 initial CI run `9561`: failed in backend SQLite tests after dependency resolution selected `fastapi 0.137.0 / starlette 1.3.1`.
  - #2399 final CI run `9563`: passed after backend dependency was capped as `fastapi<0.137`.
- GitHub open PR search result: `0`.
- Remote branch count: 2375.
- `origin/codex/*` branches updated on or after 2026-06-06: 73.
- `origin/codex/*` branches updated on or after 2026-06-06 that are not ancestors of `origin/main`: 0.
- Internal issue validation:
  - `validate_active_issue_memos.py`: pass, `ok: validated 5 active issue memos`.
  - `triage_actionable_plans.py`: pass, `active_issues=52`, `ready=15`, `blocked=37`, `actionable_adrs=1`, stopper none.
- Scope: records repository governance after #2395 through #2399 were merged. This checkpoint does not delete remote branches, close PRs, change issue status, change ADR status, change runtime behavior beyond the already-merged dependency cap, change UI/API behavior, or approve release readiness.

### Decision

- The observed 2026-06-06-or-later `codex/*` branch reachability state remains clean: no checked branch remains outside `main` ancestry.
- The #2399 CI failure is classified as dependency drift, not an application-behavior failure in the docs-only DATA-MAINT changes. The canonical signal is CI run `9563` success on head `3f374d719bdea557b5168900f519d95e544bff96`.
- Backend FastAPI remains capped below `0.137` until a deliberate dependency-upgrade slice updates route-contract expectations against the newer FastAPI/Starlette route shape.
- #2399 confirms the high-privilege data-lifecycle decision boundary is still human-owned: `DATA-MAINT-03` remains `DecisionStatus=Pending`, `ADR-0035` remains `Proposed`, and `DATA-MAINT-04` remains Draft.
- The remaining remote `codex/*` refs are cleanup candidates only. Deletion still requires repository-maintainer approval and a final deletion audit list.
- No new ADR is required. ADR-0034 remains sufficient for mainline convergence and branch hygiene unless the project changes stale-ref retention, branch cleanup authority, CI signal authority, dependency-upgrade authority, or release authority.

### Updated recommendation

1. Start new independent work from `origin/main@e2daa3b3120e30e0d39f5c7ac35ee1b4243b79d4`.
2. Keep using normal merge commits for PRs whose purpose is to preserve `codex/*` branch-tip reachability.
3. Do not delete remote `codex/*` branches from this issue; route that action through repository-maintainer approval.
4. Treat FastAPI/Starlette upgrades past the current cap as a deliberate dependency-upgrade task, not an incidental CI repair.
5. Route release blockers through `PRODUCT-QA-01`, `MVP-EXIT-01`, `PROJECT-BASELINE-01`, `FB-P0-2A2B2C`, `ENV-CONFIG-DRIFT-01`, `PRODUCT-OPS-01`, `PRODUCT-VALUE-01..03`, `ADR-0035`, and `DATA-MAINT-03/04`.

---

## Post-2402 governance reachability and release-gate traceability checkpoint

- Checkpoint date (JST): 2026-06-15
- Latest main: `origin/main@9c9dbd68084e56d2a4d1430f0331bddf191b4d23`
- Recent normal-merge PRs included in this checkpoint:
  - #2400 `[codex] Record post-2399 project baseline`
  - #2401 `[codex] Sync HIL/FB hold gates after post-2400 baseline`
  - #2402 `[codex] Sync release gates after HIL/FB hold update`
- Integration method: normal merge commits, not squash/rebase, so the related `codex/*` branch tips remain reachable from `main`.
- GitHub Actions CI:
  - #2400 CI run `9566`: passed.
  - #2401 CI run `9569`: passed.
  - #2402 CI run `9572`: passed on head `e94fe7f0852720d91d1b1644e7b24ad4518552eb`.
- GitHub open PR search result: `0`.
- `origin/codex/*` branches updated on or after 2026-06-06: 76.
- `origin/codex/*` branches updated on or after 2026-06-06 that are not ancestors of `origin/main`: 0.
- Internal issue validation:
  - `validate_active_issue_memos.py`: pass, `ok: validated 5 active issue memos`.
  - `triage_actionable_plans.py`: pass, `active_issues=52`, `ready=15`, `blocked=37`, `actionable_adrs=1`, stopper none.
- Scope: records repository governance after #2400 through #2402 were merged. This checkpoint does not delete remote branches, close PRs, change issue status, change ADR status, change runtime behavior, change UI/API behavior, change SafeMode/share-export policy, approve HIL/FB held exceptions, or approve release readiness.

### Decision

- The observed 2026-06-06-or-later `codex/*` branch reachability state remains clean: no checked branch remains outside `main` ancestry.
- #2401 and #2402 align the HIL/FB hold-gate state across `HIL-RS-02-A1`, `FB-P0-2A2B2C`, `PRODUCT-QA-01`, and `MVP-EXIT-01`: `fixedKeyDrift=0`, `pendingBypassDetected=false`, `Approval Record=Pending`, `HIL-RS-02-GOV-EXCEPTION-01=held`, `pendingDecisionQueueCount>0`, and `executeAllowed=false`.
- The current governance interpretation is traceability-only. It is not approval to bypass held gates, start downstream A2/A3 work, weaken SafeMode defaults, change share/export policy, or ship the product.
- The remaining remote `codex/*` refs are cleanup candidates only. Deletion still requires repository-maintainer approval and a final deletion audit list.
- No new ADR is required. ADR-0034 remains sufficient for mainline convergence and branch hygiene unless the project changes stale-ref retention, branch cleanup authority, CI signal authority, dependency-upgrade authority, HIL/FB held-gate authority, or release authority.

### Updated recommendation

1. Start new independent work from `origin/main@9c9dbd68084e56d2a4d1430f0331bddf191b4d23`.
2. Keep using normal merge commits for PRs whose purpose is to preserve `codex/*` branch-tip reachability.
3. Do not delete remote `codex/*` branches from this issue; route that action through repository-maintainer approval.
4. Keep HIL/FB downstream execution blocked until the human-owned approval and held-gate decision records are explicitly resolved.
5. Route release blockers through `PRODUCT-QA-01`, `MVP-EXIT-01`, `PROJECT-BASELINE-01`, `HIL-RS-02-A1`, `FB-P0-2A2B2C`, `ENV-CONFIG-DRIFT-01`, `PRODUCT-OPS-01`, `PRODUCT-VALUE-01..03`, `ADR-0035`, and `DATA-MAINT-03/04`.

---

## Post-2407 governance reachability and canonical-summary checkpoint

- Checkpoint date (JST): 2026-06-15
- Latest main: `origin/main@68a1a792883fde21e95bd45034323c0eaa17ea43`
- Recent normal-merge PRs included in this checkpoint:
  - #2403 `[codex] Record post-2402 project baseline`
  - #2404 `[codex] Add CE1 canonical handoff summary`
  - #2405 `[codex] Add CE0 graph canonical handoff summary`
  - #2406 `[codex] Add CE0 freeze canonical handoff summary`
  - #2407 `[codex] Record post-2406 project baseline`
- Integration method: normal merge commits, not squash/rebase, so the related `codex/*` branch tips remain reachable from `main`.
- GitHub Actions CI:
  - #2403 CI run `9575`: passed.
  - #2404 CI run `9578`: passed.
  - #2405 CI run `9581`: passed.
  - #2406 CI run `9584`: passed.
  - #2407 CI run `9587`: passed on head `0a7e84d414ab963bd9e76f1b097041c6000a7671`.
- `origin/codex/*` branches updated on or after 2026-06-06: 81.
- `origin/codex/*` branches updated on or after 2026-06-06 that are not ancestors of `origin/main`: 0.
- Internal issue validation:
  - `validate_active_issue_memos.py`: pass, `ok: validated 5 active issue memos`.
  - `triage_actionable_plans.py`: pass, `active_issues=52`, `ready=15`, `blocked=37`, `actionable_adrs=1`, stopper none.
- Scope: records repository governance after #2403 through #2407 were merged. This checkpoint does not delete remote branches, close PRs, change issue status, change ADR status, change runtime behavior, change UI/API behavior, change SafeMode/share-export policy, approve CE0/CE1 implementation authority, or approve release readiness.

### Decision

- The observed 2026-06-06-or-later `codex/*` branch reachability state remains clean: no checked branch remains outside `main` ancestry.
- #2404, #2405, and #2406 improve CE1 and CE0 handoff readability by adding current canonical summaries to the upstream issue records. These summaries are governance/readability evidence only; they are not permission to redefine fixed IDs, relax SafeMode, bypass Query Preview, auto-promote review state, write directly to Consensus, auto-apply proposals, or publish unreviewed content.
- #2407 records the post-2406 baseline on `main` and preserves the release No-Go boundary.
- The remaining remote `codex/*` refs are cleanup candidates only. Deletion still requires repository-maintainer approval and a final deletion audit list.
- No new ADR is required. ADR-0034 remains sufficient for mainline convergence and branch hygiene unless the project changes stale-ref retention, branch cleanup authority, CI signal authority, CE0/CE1 contract authority, HIL/FB held-gate authority, or release authority.

### Updated recommendation

1. Start new independent work from `origin/main@68a1a792883fde21e95bd45034323c0eaa17ea43`.
2. Keep using normal merge commits for PRs whose purpose is to preserve `codex/*` branch-tip reachability.
3. Do not delete remote `codex/*` branches from this issue; route that action through repository-maintainer approval.
4. Treat CE0/CE1 canonical summaries as read-only planning SSOTs. Any fixed contract value or authority-boundary change needs an ADR or held issue path.
5. Keep release blockers routed through `PRODUCT-QA-01`, `MVP-EXIT-01`, `PROJECT-BASELINE-01`, `HIL-RS-02-A1`, `FB-P0-2A2B2C`, `ENV-CONFIG-DRIFT-01`, `PRODUCT-OPS-01`, `PRODUCT-VALUE-01..03`, `ADR-0035`, and `DATA-MAINT-03/04`.

---

## Post-2416 governance reachability and productization-gate sync checkpoint

- Checkpoint date (JST): 2026-06-16
- Latest main: `origin/main@22bcefb6b768dbb1a877fe028b7ad7b971504d43`
- Recent normal-merge PRs included in this checkpoint:
  - #2408 `[codex] Record post-2407 governance reachability`
  - #2409 `[codex] Sync Product QA after post-2408 governance`
  - #2410 `[codex] Sync MVP Exit after post-2409 Product QA`
  - #2411 `[codex] Update realistic journey E2E for Advanced UI toggle`
  - #2412 `[codex] Record post-2411 realistic journey evidence`
  - #2413 `[codex] Record post-2412 project baseline`
  - #2414 `[codex] Sync Product QA after post-2413 baseline`
  - #2415 `[codex] Sync MVP Exit after post-2414 Product QA`
  - #2416 `[codex] Record post-2415 project baseline`
- Additional mainline intake: `mvp-manual-authoring-ui` merge `0cffb2ec`, which made manual card authoring, canvas context-menu editing, Advanced UI, MVP verification docs, first-run Docker hardening, and DB password preservation canonical on `main`.
- Integration method: normal merge commits for the `codex/*` PRs, so the related branch tips remain reachable from `main`.
- GitHub Actions CI:
  - #2408 CI run `9590`: passed.
  - #2409 CI run `9593`: passed.
  - #2410 CI run `9599`: passed.
  - #2411 CI run `9602`: passed.
  - #2412 CI run `9605`: passed.
  - #2413 CI run `9608`: passed.
  - #2414 CI run `9611`: passed.
  - #2415 CI run `9614`: passed.
  - #2416 CI run `9617`: passed.
- `origin/codex/*` branches updated on or after 2026-06-06: 72.
- `origin/codex/*` branches updated on or after 2026-06-06 that are not ancestors of `origin/main`: 0.
- Internal issue validation:
  - `validate_active_issue_memos.py`: pass, `ok: validated 5 active issue memos`.
  - `triage_actionable_plans.py`: pass, `active_issues=52`, `ready=15`, `blocked=37`, `actionable_adrs=1`, stopper none.
- Scope: records repository governance after #2408 through #2416 and the manual-authoring mainline merge became canonical. This checkpoint does not delete remote branches, close PRs, change issue status, change ADR status, change runtime behavior, change UI/API behavior, change SafeMode/share-export policy, approve manual-authoring or Advanced UI authority changes, or approve release readiness.

### Decision

- The observed 2026-06-06-or-later `codex/*` branch reachability state remains clean: no checked branch remains outside `main` ancestry.
- #2411 through #2413 refresh the realistic-journey evidence after Advanced UI moved non-essential first-run controls out of the default surface.
- #2414 through #2416 align `PRODUCT-QA-01`, `MVP-EXIT-01`, and `PROJECT-BASELINE-01` around the same interpretation: manual authoring, canvas context-menu editing, Advanced UI, and realistic-journey evidence improve productization evidence but do not create release approval.
- The current governance interpretation is traceability-only. It is not approval to delete remote refs, weaken SafeMode defaults, change share/export policy, treat `QA-E2E-USE-01` as Open, bypass human acceptance, or ship the product.
- The remaining remote `codex/*` refs are cleanup candidates only. Deletion still requires repository-maintainer approval and a final deletion audit list.
- No new ADR is required. ADR-0034 remains sufficient for mainline convergence and branch hygiene unless the project changes stale-ref retention, branch cleanup authority, CI signal authority, manual-authoring authority, Advanced UI/default-surface policy, SafeMode/share-export policy, product-value authority, or release authority.

### Updated recommendation

1. Start new independent work from `origin/main@22bcefb6b768dbb1a877fe028b7ad7b971504d43`.
2. Keep using normal merge commits for PRs whose purpose is to preserve `codex/*` branch-tip reachability.
3. Do not delete remote `codex/*` branches from this issue; route that action through repository-maintainer approval.
4. Treat manual-authoring and Advanced UI evidence as productization freshness, not release approval.
5. Keep release blockers routed through `PRODUCT-QA-01`, `MVP-EXIT-01`, `PROJECT-BASELINE-01`, `QA-E2E-USE-01`, `HIL-RS-02-A1`, `FB-P0-2A2B2C`, `ENV-CONFIG-DRIFT-01`, `PRODUCT-OPS-01`, `PRODUCT-VALUE-01..03`, `ADR-0035`, and `DATA-MAINT-03/04`.

---

## Post-2423 governance reachability and Product Value evidence-foundation checkpoint

- Checkpoint date (JST): 2026-06-17
- Latest main: `origin/main@e91204f04fcbfdf2b1a50af923127adeef99a085`
- Recent normal-merge PRs included in this checkpoint:
  - #2417 `[codex] Record post-2416 governance reachability`
  - #2418 `[codex] Add Product Value 01 readiness summary`
  - #2419 `[codex] Add Product Value 02/03 readiness summaries`
  - #2420 `[codex] Sync Product QA after value readiness summaries`
  - #2421 `[codex] Share Product Value E2E fixtures`
  - #2422 `[codex] Sync Product QA after value E2E fixtures`
  - #2423 `[codex] Record post-2422 project baseline`
- Integration method: normal merge commits for the `codex/*` PRs, so the related branch tips remain reachable from `main`.
- GitHub Actions CI:
  - #2418 CI run `9623`: passed.
  - #2419 CI run `9626`: passed.
  - #2420 CI run `9629`: passed.
  - #2421 CI run `9632`: passed.
  - #2422 CI run `9635`: passed.
  - #2423 CI run `9638`: passed.
- GitHub open PR search result: `0`.
- `origin/codex/*` branches updated on or after 2026-06-06: 79.
- `origin/codex/*` branches updated on or after 2026-06-06 that are not ancestors of `origin/main`: 0.
- Internal issue validation:
  - `validate_active_issue_memos.py`: pass, `ok: validated 5 active issue memos`.
  - `test_validate_active_issue_memos.py`: pass, 10 tests.
  - `triage_actionable_plans.py`: pass, `active_issues=55`, `ready=15`, `blocked=40`, `actionable_adrs=1`, stopper none.
- Scope: records repository governance after #2417 through #2423 became canonical. This checkpoint does not delete remote branches, close PRs, change issue status, change ADR status, change runtime behavior, change UI/API behavior, change SafeMode/share-export policy, approve Product Value Open gates, or approve release readiness.

### Decision

- The observed 2026-06-06-or-later `codex/*` branch reachability state remains clean: no checked branch remains outside `main` ancestry.
- #2418 and #2419 make Product Value readiness easier to review by splitting PV01/PV02/PV03 into readable internal summaries instead of relying on scattered historical context.
- #2421 makes the next Product Value evidence-packet work more repeatable by sharing deterministic E2E fixtures for first meaningful map, ambiguity/evidence, and reviewable package flows.
- #2420, #2422, and #2423 align Product QA, MVP-EXIT, and PROJECT-BASELINE around the same interpretation: this is evidence-foundation and traceability work, not Product Value Open-gate acceptance or release approval.
- The current governance interpretation is traceability-only. It is not approval to delete remote refs, weaken SafeMode defaults, change share/export policy, treat Product Value Draft issues as Open, bypass human acceptance, or ship the product.
- The remaining remote `codex/*` refs are cleanup candidates only. Deletion still requires repository-maintainer approval and a final deletion audit list.
- No new ADR is required. ADR-0034 remains sufficient for mainline convergence and branch hygiene unless the project changes stale-ref retention, branch cleanup authority, CI signal authority, Product Value definitions, SafeMode/share-export policy, review attribution authority, public package contract, or release authority.

### Updated recommendation

1. Start new independent work from `origin/main@e91204f04fcbfdf2b1a50af923127adeef99a085`.
2. Keep using normal merge commits for PRs whose purpose is to preserve `codex/*` branch-tip reachability.
3. Do not delete remote `codex/*` branches from this issue; route that action through repository-maintainer approval.
4. Treat Product Value readiness summaries and shared E2E fixtures as evidence-foundation work. Product Value Open-gate acceptance still needs replayable evidence packets, screenshots or traces, and human acceptance.
5. Keep release blockers routed through `PRODUCT-QA-01`, `MVP-EXIT-01`, `PROJECT-BASELINE-01`, `QA-E2E-USE-01`, `HIL-RS-02-A1`, `FB-P0-2A2B2C`, `ENV-CONFIG-DRIFT-01`, `PRODUCT-OPS-01`, `PRODUCT-VALUE-01..03`, `ADR-0035`, and `DATA-MAINT-03/04`.

---

## Post-2426 governance reachability and release-gate baseline checkpoint

- Checkpoint date (JST): 2026-06-17
- Latest main: `origin/main@eab2ec6b0f99050437b7c2eee34d042b0b29699e`
- Recent normal-merge PRs included in this checkpoint:
  - #2424 `[codex] Record post-2423 governance reachability`
  - #2425 `[codex] Sync release gates after post-2424 governance`
  - #2426 `[codex] Record post-2425 project baseline`
- Integration method: normal merge commits for the `codex/*` PRs, so the related branch tips remain reachable from `main`.
- GitHub Actions CI:
  - #2424 CI run `9641`: passed.
  - #2425 CI run `9644`: passed.
  - #2426 CI run `9647`: passed.
- GitHub open PR search result: `0`.
- `origin/codex/*` branches updated on or after 2026-06-06: 82.
- `origin/codex/*` branches updated on or after 2026-06-06 that are not ancestors of `origin/main`: 0.
- Internal issue validation:
  - `validate_active_issue_memos.py`: pass, `ok: validated 5 active issue memos`.
  - `test_validate_active_issue_memos.py`: pass, 10 tests.
  - `triage_actionable_plans.py`: pass, `active_issues=55`, `ready=15`, `blocked=40`, `actionable_adrs=1`, stopper none.
- Scope: records repository governance after #2424 through #2426 became canonical. This checkpoint does not delete remote branches, close PRs, change issue status, change ADR status, change runtime behavior, change UI/API behavior, change SafeMode/share-export policy, approve Product Value Open gates, or approve release readiness.

### Decision

- The observed 2026-06-06-or-later `codex/*` branch reachability state remains clean: no checked branch remains outside `main` ancestry.
- #2424 keeps the branch-reachability and repository-governance state current after the Product Value evidence-foundation lane.
- #2425 aligns Product QA and MVP-EXIT with the post-2424 governance interpretation while preserving full-shipment No-Go.
- #2426 records the same interpretation in `PROJECT-BASELINE-01`, so latest-main health, repository governance, Product QA, and MVP-EXIT now point to the same post-2425 traceability boundary.
- The current governance interpretation is traceability-only. It is not approval to delete remote refs, weaken SafeMode defaults, change share/export policy, treat Product Value Draft issues as Open, bypass human acceptance, or ship the product.
- The remaining remote `codex/*` refs are cleanup candidates only. Deletion still requires repository-maintainer approval and a final deletion audit list.
- No new ADR is required. ADR-0034 remains sufficient for mainline convergence and branch hygiene unless the project changes stale-ref retention, branch cleanup authority, CI signal authority, Product Value definitions, SafeMode/share-export policy, review attribution authority, public package contract, or release authority.

### Updated recommendation

1. Start new independent work from `origin/main@eab2ec6b0f99050437b7c2eee34d042b0b29699e`.
2. Keep using normal merge commits for PRs whose purpose is to preserve `codex/*` branch-tip reachability.
3. Do not delete remote `codex/*` branches from this issue; route that action through repository-maintainer approval.
4. Treat #2424 through #2426 as governance and release-gate traceability work only. Product Value Open-gate acceptance still needs replayable evidence packets, screenshots or traces, and human acceptance.
5. Keep release blockers routed through `PRODUCT-QA-01`, `MVP-EXIT-01`, `PROJECT-BASELINE-01`, `QA-E2E-USE-01`, `HIL-RS-02-A1`, `FB-P0-2A2B2C`, `ENV-CONFIG-DRIFT-01`, `PRODUCT-OPS-01`, `PRODUCT-VALUE-01..03`, `ADR-0035`, and `DATA-MAINT-03/04`.

---

## Post-2430 governance reachability and Product Value fixture-summary checkpoint

- Checkpoint date (JST): 2026-06-17
- Latest main: `origin/main@18909809cf0465c880c23d3406f5a2814c22155c`
- Recent normal-merge PRs included in this checkpoint:
  - #2428 `[codex] Add Product Value fixture manifests`
  - #2429 `[codex] Sync Product Value fixture readiness summaries`
  - #2430 `[codex] Sync Product QA after fixture summaries`
- Integration method: normal merge commits for the `codex/*` PRs, so the related branch tips remain reachable from `main`.
- GitHub Actions CI:
  - #2428 CI run `9653`: passed.
  - #2429 CI run `9656`: passed.
  - #2430 CI run `9659`: passed.
- `origin/codex/*` branches updated on or after 2026-06-06: 104.
- `origin/codex/*` branches updated on or after 2026-06-06 that are not ancestors of `origin/main`: 0.
- Internal issue validation:
  - `validate_active_issue_memos.py`: pass, `ok: validated 5 active issue memos`.
  - `triage_actionable_plans.py`: pass, `active_issues=55`, `ready=15`, `blocked=40`, `actionable_adrs=1`, stopper none.
- Scope: records repository governance after #2428 through #2430 became canonical. This checkpoint does not delete remote branches, close PRs, change issue status, change ADR status, change runtime behavior, change UI/API behavior, change SafeMode/share-export policy, approve Product Value Open gates, or approve release readiness.

### Decision

- The observed 2026-06-06-or-later `codex/*` branch reachability state remains clean: no checked branch remains outside `main` ancestry.
- #2428 made Product Value fixture manifests canonical for PV01/PV02/PV03 while keeping the source issues Draft.
- #2429 aligned current-open readiness summaries so fixture definition is treated as complete but human value acceptance, screenshots/traces, SafeMode/share-export evidence, and read-only reviewer inspection remain open.
- #2430 aligned Product QA and MVP-EXIT with the same interpretation: traceability improved, full release shipment remains No-Go.
- The current governance interpretation is traceability-only. It is not approval to delete remote refs, weaken SafeMode defaults, change share/export policy, treat Product Value Draft issues as Open, bypass human acceptance, or ship the product.
- The remaining remote `codex/*` refs are cleanup candidates only. Deletion still requires repository-maintainer approval and a final deletion audit list.
- No new ADR is required. ADR-0034 remains sufficient for mainline convergence and branch hygiene unless the project changes stale-ref retention, branch cleanup authority, CI signal authority, Product Value definitions, fixture meaning, SafeMode/share-export policy, review attribution authority, public package contract, signature/approval semantics, or release authority.

### Updated recommendation

1. Start new independent work from `origin/main@18909809cf0465c880c23d3406f5a2814c22155c`.
2. Keep using normal merge commits for PRs whose purpose is to preserve `codex/*` branch-tip reachability.
3. Do not delete remote `codex/*` branches from this issue; route that action through repository-maintainer approval.
4. Treat #2428 through #2430 as fixture-summary and release-gate traceability work only. Product Value Open-gate acceptance still needs replayable evidence packets, release-suitable screenshots or traces, and Productization Program Owner / QA Lead acceptance.
5. Keep release blockers routed through `PRODUCT-QA-01`, `MVP-EXIT-01`, `PROJECT-BASELINE-01`, `QA-E2E-USE-01`, `HIL-RS-02-A1`, `FB-P0-2A2B2C`, `ENV-CONFIG-DRIFT-01`, `PRODUCT-OPS-01`, `PRODUCT-VALUE-01..03`, `ADR-0035`, and `DATA-MAINT-03/04`.
