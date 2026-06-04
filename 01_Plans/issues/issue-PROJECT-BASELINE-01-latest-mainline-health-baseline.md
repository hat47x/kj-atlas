# Issue Draft: PROJECT-BASELINE-01 最新mainの健康状態ベースライン確定

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: TBD
- Scope: `01_Plans/`, `02_Architecture/`, `03_Implement/`, `04_Documentation/`
- Related Backlog: `PROJECT-BASELINE-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0034-mainline-convergence-and-branch-hygiene.md`, `01_Plans/issues/issue-MVP-EXIT-01-productization-readiness.md`, `01_Plans/issues/issue-PRODUCT-QA-01-release-readiness-quality-gates.md`, `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`, `02_Architecture/architecture.md`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: PROJECT-BASELINE-01
- RequirementStatement: 最新mainに大きな変更が取り込まれた後、製品化判断に使える candidate 単位の健康状態ベースラインを作成し、既知の未達項目を既存issueまたは新規issueへ戻せる状態にする。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=ローカル `main` が `origin/main` の最新SHAへfast-forward済み / 操作=docs, frontend, backend, E2Eまたは代替smokeの最小ゲートを実行する / 期待結果=最新mainのGo/Conditional/No-Go材料が `PRODUCT-QA-01` へ渡せる / 除外=検出した不具合をすべて本Issueで修正すること。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export / import-sanitize / public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: integration
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A

## 1) 課題 / Problem statement

- 最新mainは 2026-05-21 に `2a93c95e` へ更新され、173ファイル規模のfast-forward差分が取り込まれた。
- `04_Documentation`、`02_Architecture`、frontend/backend、issue/ADRにまたがる更新が同時に入っており、現時点の「動く範囲」「未達範囲」「製品化ゲート上の戻し先」が一枚で確認できない。
- `PRODUCT-QA-01` は品質ゲートを定義済みだが、最新main candidate に対する実行結果レコードが不足している。
- この状態で個別修正を進めると、すでにmainで解消済みの課題や、逆に新しく発生した回帰を見落とす可能性がある。

## 2) 背景 / Context

- `MVP-EXIT-01` は Program Gate として、`PRODUCT-QA-01` と `ENV-CONFIG-DRIFT-01` の最新結果を必要としている。
- `PRODUCT-QA-01` は `G0..G7 + Value gates + E1..E3` の判定モデルを持つ。
- `ADR-0019` はE2EをPR必須証跡または未実施理由つき代替証跡として扱う方針を定めている。
- `ADR-0034` は、最新mainを唯一の開発入力にする intake 統治を提案している。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 利用者価値を実現するには、現在のmainで開始、外在化、構造化、共有前確認がどこまで成立するかを測定する必要がある。
- 安全（THREAT_MODEL / SafeMode）: SafeMode既定ON、share/export前確認、import sanitize はリリース阻害になり得るため、baselineで最初に確認する。
- 企業・行政要件（enterprise_architecture）: 組織導入では、候補バージョンごとに検証結果、未達項目、再判定条件を説明できる必要がある。
- 後方互換（schemas）: 最新mainで既存fixtureやレビューパック、document/view/pack互換が壊れていないか確認する。

## 4) 提案する解決策 / Proposed solution

- 変更対象:
  - 最新main candidate の baseline record。
  - 検証コマンド、手動smoke、失敗分類、戻し先issueの記録。
- 変更の最小単位:
  - `PRODUCT-QA-01` の Gate Record に渡せる形式で、最新mainの状態を1回分記録する。
  - 失敗は Blocker/Critical/Major/Minor に分類し、既存issueがあれば戻し先へ紐付ける。
- 非目標:
  - このIssue単体でUI再設計、データモデル拡張、全E2E安定化を完了すること。
  - 仕様判断をテスト結果だけで確定すること。

## 5) 受入条件 / Acceptance criteria

- [ ] 対象candidateとして `origin/main` SHA、取得日時、検証者、検証環境が記録されている。
- [ ] docs-check、frontend typecheck/unit、backend unit/settings、import/exportまたはshare/export安全境界の最小検証結果が記録されている。
- [ ] E2Eを実行した場合はシナリオと結果、実行できない場合は未実施理由、代替smoke、再開条件が記録されている。
- [ ] SafeMode、share/export、import sanitize、public exposure の結果が `PRODUCT-QA-01` の G1/G5/G7 へ対応付けられている。
- [ ] 失敗や未確認項目が、既存issueまたは新規issueへ戻されている。
- [ ] 最終判定が Go / Conditional Go / No-Go のいずれかで記録され、Conditional/No-Goの場合は owner/due/re-decision date がある。
- [ ] 必要な検証（integration）が `Expected verification level` と一致する。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 最新main candidate record を作成する。
- [ ] T2 `validate_active_issue_memos.py` と `triage_actionable_plans.py` を実行し、計画整合を確認する。
- [ ] T3 frontend/backend/docs の最小回帰コマンドを実行し、pass/fail/未実施理由を記録する。
- [ ] T4 ChromeまたはPlaywrightで代表操作をsmokeし、開始、カード操作、共有前確認、SafeMode表示を観測する。
- [ ] T5 未達項目を `PRODUCT-QA-01`, `PRODUCT-UX-*`, `ENV-CONFIG-DRIFT-01`, `QA-*` などへ戻す。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python 01_Plans/triage_actionable_plans.py`
  - `cd 03_Implement/frontend && node .\\node_modules\\typescript\\bin\\tsc --noEmit`
  - `cd 03_Implement/frontend && node .\\node_modules\\vitest\\vitest.mjs run`
  - `cd 03_Implement/backend && .\\.venv\\Scripts\\python.exe -m pytest`
  - `git diff --check`
- 期待結果:
  - 最新mainの健康状態が candidate 単位で記録され、製品化ゲートの入力として使える。
  - 失敗が未分類のまま残らない。
- 未実施時の理由・代替検証:
  - npm/node/python環境や外部依存で一部コマンドが実行できない場合は、実行不能理由、代替コマンド、再開条件を記録する。

## 8) 代替案 / Alternatives considered

- 代替案A: 個別issueごとに都度テストを実行し、baselineを作らない。却下理由: 最新main全体の既知状態が残らず、製品化判定に使いにくい。
- 代替案B: CI結果だけを正本にする。却下理由: UI手動smoke、公開文書、SafeMode表示など、CIだけでは観測しにくい利用者視点が残る。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: baseline実行範囲が広すぎて、修正作業と混線する。
- 影響範囲: 製品化ゲート、公開文書、frontend/backend回帰、E2E証跡。
- ロールバック手順: baseline recordは削除せず、誤分類だけを追記訂正する。実装修正は別issue/PRへ分離する。

## 10) Additional context

- 2026-05-21 intake:
  - `git pull --ff-only origin main`: local `main` を `2a93c95e` へ更新。
  - `python 01_Plans/issues/validate_active_issue_memos.py`: `ok: validated 5 active issue memos`
  - `python 01_Plans/triage_actionable_plans.py`: `active_issues=43 / ready=15 / blocked=28 / actionable_adrs=1`
  - triage stopper: none
- ADR化済み: `ADR-0034`

## 11) Baseline Record 2026-05-21: latest main + PR #2251 planning branch

### Candidate

- Target main: `origin/main` = `2a93c95e`
- Baseline branch: `codex/current-project-risk-analysis-issues`
- Baseline commit: `50f43e4c`
- Scope note: `50f43e4c` は `01_Plans` / `AGENTS.md` の計画・起票差分のみで、`03_Implement` の実装コード差分はない。
- Reviewer/executor: Codex
- Environment: Windows / PowerShell / bundled Node (`C:\Users\yhata\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe`) / backend `.venv`

### Command evidence

| Area | Command | Result | Gate mapping |
| --- | --- | --- | --- |
| Planning metadata | `03_Implement/backend/.venv/Scripts/python.exe 01_Plans/issues/validate_active_issue_memos.py` | Pass: `ok: validated 5 active issue memos` | G0 |
| Planning triage | `03_Implement/backend/.venv/Scripts/python.exe 01_Plans/triage_actionable_plans.py` | Pass: `active_issues=45 / ready=17 / blocked=28 / stopper=none` | G0 |
| Frontend typecheck | bundled `node.exe .\node_modules\typescript\bin\tsc --noEmit` | Pass | G7 |
| Frontend unit/regression | bundled `node.exe .\node_modules\vitest\vitest.mjs run` | Pass: 160 files / 732 tests | G1 / G3 / G7 |
| Backend pytest | `.venv\Scripts\python.exe -m pytest --basetemp ... -p no:cacheprovider` with `.venv\Scripts` prepended to `PATH` | Pass: 256 passed / 19 skipped | G7 / E2 |
| Playwright mock E2E | bundled `node.exe .\node_modules\playwright\cli.js test e2e/ce3_patch_workspace.spec.ts e2e/auth_context_level1_smoke.spec.ts --reporter=line` | Pass: 2 passed after installing Playwright Chromium and starting Vite manually | G2 / G4 |
| Browser smoke | Codex in-app browser against `http://127.0.0.1:4173/` | Conditional pass: app title `kj-atlas`, `セーフモード: ON`, `共有と再現` dialog, Japanese fixed mask text visible, browser warning/error logs empty | G1 / G2 / G3 |
| Public documentation boundary | `rg -n "04_Documentation|AGENTS.md|01_Plans|ADR-|PUBLICATION_MANIFEST|内部管理|作業ログ|issue-|Issue|PRODUCT-|MVP|Stream [A-Z]|Draft Proposal|DOC-OPS|AUTH-OPS|Gate Record|Productization" <public target 04 docs>` | Pass: no matches after separating user-facing text from maintainer/project-management content | G5 |

### Environment findings

- `npm` is not available in the current PowerShell `PATH`. Direct `node.exe` invocation works for `tsc`, `vitest`, `vite`, and `playwright`.
- Playwright config uses `webServer.command = "npm run dev -- --host 127.0.0.1 --port 4173"`, so E2E startup fails in this environment unless Vite is started manually or `npm` is made available.
- Playwright browsers were installed during this baseline pass with bundled `node.exe .\node_modules\playwright\cli.js install chromium`; the initial blocker is resolved for this workstation.
- `ce3_patch_workspace.spec.ts` initially failed after browser install because the test expected English-only `Collect candidates` while the current UI shows `候補を収集`. The test was updated to accept both English and Japanese labels for the same operation contract.
- Standalone frontend smoke produced a Vite proxy warning for `/docs/doc_phase1_canvas` because backend was not running. This aligns with `PRODUCT-OPS-01` backend未接続 recovery scope and does not by itself indicate a frontend regression.
- The first backend pytest run failed due `PermissionError` under `C:\Users\yhata\AppData\Local\Temp\pytest-of-hat47x`; rerunning with an explicit repo-external `--basetemp` resolved the environment limitation.
- Backend migration/index tests require `alembic` on `PATH`; prepending `.venv\Scripts` fixed the remaining subprocess failures.

### Gate classification

| Gate | Baseline result | Reason |
| --- | --- | --- |
| G0 計画整合 | Go | issue metadata and triage pass with no stopper. |
| G1 安全既定 | Conditional Go | unit coverage, browser smoke, and auth smoke E2E pass; full share/export E2E is still outside this slice. |
| G2 主要操作 | Go for sampled mock E2E | CE3 workspace and auth read-only smoke pass after i18n-tolerant E2E fix. |
| G3 日本語UI | Go | frontend i18n/UI tests pass, and share panel smoke shows Japanese labels for observed flow. |
| G4 画面耐性 | Conditional | Playwright browser execution works, but viewport matrix was not executed in this baseline pass. |
| G5 公開文書 | Go for public-target boundary scan | public-target 04 docs no longer contain internal management terms in the forbidden-term scan; GitHub links to design specs are allowed where they clarify source-of-truth details. |
| G6 診断とサポート | Conditional Go | backend未接続 proxy warning is classified under `PRODUCT-OPS-01`; user-facing recovery path still needs product gate evidence. |
| G7 回帰 | Go | frontend typecheck/test and backend pytest pass after environment normalization. |

### Decision

- Baseline decision: **Conditional** for latest-main health baseline.
- Release readiness decision: **No-Go** until viewport matrix and full release-candidate E2E evidence are recorded.
- Follow-up routing:
  - E2E evidence gap: `QA-E2E-USE-01` remains for realistic journey expansion beyond the two mock scenarios verified here.
  - Backend未接続 recovery messaging: `PRODUCT-OPS-01`
  - E2E runtime ergonomics: create a dedicated DX issue if `npm` PATH absence continues to make `playwright.config.ts` unusable without manual Vite startup.

## 12) Baseline Record 2026-05-22: frontend E2E recovery on PR #2251 branch

### Candidate

- Target main: `origin/main` = `2a93c95e`
- Baseline branch: `codex/current-project-risk-analysis-issues`
- Scope note: this update covers frontend operability and E2E drift found while continuing PR #2251. It does not replace the backend pytest evidence in section 11.
- Executor: Codex
- Environment: Windows / PowerShell / bundled Node (`C:\Users\yhata\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe`) / Vite manually running on `127.0.0.1:4173`

### Command evidence

| Area | Command | Result | Gate mapping |
| --- | --- | --- | --- |
| Frontend typecheck | bundled `node.exe .\node_modules\typescript\bin\tsc --noEmit` | Pass | G7 |
| Targeted frontend regression | bundled `node.exe .\node_modules\vitest\vitest.mjs run src/ui/SharePanel.test.ts src/domain/geometry/polygon_edit.test.ts` | Pass: 13 tests | G1 / G3 / G7 |
| Frontend unit/regression | bundled `node.exe .\node_modules\vitest\vitest.mjs run` | Pass: 160 files / 734 tests | G1 / G3 / G7 |
| Full frontend Playwright E2E | bundled `node.exe .\node_modules\playwright\cli.js test --reporter=line` with Vite already running on `127.0.0.1:4173` | Pass: 32 tests | G2 / G3 / G4 / G7 |
| Canvas/polygon E2E focus | `e2e/polygon_vertex_edit.spec.ts e2e/polygon_autofit_qa_boundary.spec.ts` | Pass: 4 tests | G2 / G4 |
| Header panel viewport/keyboard focus | bundled `node.exe .\node_modules\playwright\cli.js test e2e/header_toolbar_layout.spec.ts --reporter=line` | Pass: 7 tests covering 1440px / 1280px / 920px / 768px / 390px fit and 1440px / 768px Enter/Escape focus return | G2 / G4 |
| Polygon edit keyboard focus | bundled `node.exe .\node_modules\playwright\cli.js test e2e/polygon_vertex_edit.spec.ts --reporter=line` | Pass: 2 tests covering pointer drag plus keyboard nudge/removal persistence | G2 / G4 |
| Canvas focus-order breadth | bundled `node.exe .\node_modules\playwright\cli.js test e2e/canvas_focus_order.spec.ts --reporter=line` | Pass: 1 test covering keyboard card selection, Tab reachability to card action, keyboard island selection, Japanese island-editor labels, and Tab reachability to island action | G2 / G3 / G4 |
| Large-document operability | bundled `node.exe .\node_modules\playwright\cli.js test e2e/large_document_operability.spec.ts --reporter=line` | Pass: 1 test covering 120 cards / 12 islands at 768px, search, hide non-matches, panel fit, and bundle diagnostics export | G2 / G4 / G7 |
| Ops recovery guidance | bundled `node.exe .\node_modules\playwright\cli.js test e2e/ops_recovery_guidance.spec.ts --reporter=line` | Pass: 4 tests covering API load failure, save failure, slow diagnostics cancellation, and slow review-pack export cancellation at 390px, recovery text, progress/cancel state, JSON preservation, safe diagnostic sharing, and status viewport fit | G4 / G6 / G7 |

### Findings and routing

- Resolved defect: `primary-flow` had `height: 0px`, so canvas content was visible through overflow while pointer hit-testing did not reliably reach polygon vertex handles. The fix gives the primary canvas flow a real height, renders polygon edit controls above cards, and gives the edit layer a non-zero hit-test area.
- Resolved keyboard focus gap: View controls now move focus into the dialog on open and restore focus to the trigger on Escape, matching Share dialog behavior.
- Resolved polygon keyboard gap: polygon vertex handles are focusable and support Arrow-key movement plus Delete/Backspace removal, with E2E export persistence evidence.
- Resolved canvas focus-order gap: card selection, island selection, and right-side selection-panel actions are reachable through keyboard focus in the representative E2E flow.
- Resolved E2E drift: affected Playwright specs now use shared bilingual label helpers for current Japanese/English UI labels, including share/export/read-only/visibility/polygon-edit actions.
- Resolved residual label drift: island canvas labels and island-editor labels are i18n-backed, with hardcode guards for the affected user-facing English strings.
- No ADR required: the change restores the existing interaction contract and does not alter product policy, public contract, or architecture.
- Remaining follow-up: broader slow worker/API delay evidence beyond diagnostics and review-pack export remains routed to `PRODUCT-UX-04` and `PRODUCT-OPS-01`.

### Gate classification delta

| Gate | 2026-05-22 delta | Reason |
| --- | --- | --- |
| G2 主要操作 | Go for covered frontend flows | full Playwright suite covers document replacement, visibility selection, read-only safety, bundle export, polygon vertex drag, polygon vertex keyboard nudge/removal, keyboard card selection, keyboard island selection, and side-panel focus reachability. |
| G3 日本語UI | Go for covered frontend flows | stale English-only/mojibake expectations were centralized and updated in E2E helpers, and residual island/side-panel labels are i18n-backed. |
| G4 画面耐性 | Conditional Go | 390px/768px/920px/1280px/1440px header-panel fit, Share/View keyboard focus return, canvas hit-testing, synthetic large-document operability, 390px API/save recovery status fit, slow diagnostics progress/cancel, and slow review-pack export progress/cancel are now covered; broader slow worker/API delay states remain open. |
| G7 回帰 | Go for frontend scope | typecheck, targeted regression, full Vitest, and full Playwright pass. |

## 13) Baseline Record 2026-05-25: latest main health refresh

### Candidate

- Target main: `origin/main` = `512714e3a9935f91f085b3b9d0d0053943ad2841`
- Baseline branch: `codex/project-baseline-20260525`
- Scope note: this record refreshes the health baseline from the current `origin/main` before merging the open evidence PR lane. It does not supersede the release-gate records in `MVP-EXIT-01` or `PRODUCT-QA-01`.
- Executor: Codex
- Environment: Windows / PowerShell / bundled Node (`C:\Users\yhata\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe`) / backend `.venv`

### Command evidence

| Area | Command | Result | Gate mapping |
| --- | --- | --- | --- |
| Planning metadata | `03_Implement/backend/.venv/Scripts/python.exe 01_Plans/issues/validate_active_issue_memos.py` | Pass: `ok: validated 5 active issue memos` | G0 |
| Planning triage | `03_Implement/backend/.venv/Scripts/python.exe 01_Plans/triage_actionable_plans.py` | Pass: `active_issues=46 / ready=18 / blocked=28 / actionable_adrs=1 / stopper=none` | G0 |
| Frontend typecheck | bundled `node.exe .\node_modules\typescript\bin\tsc --noEmit` | Pass | G7 |
| Frontend unit/regression | bundled `node.exe .\node_modules\vitest\vitest.mjs run` | Pass: 160 files / 734 tests | G1 / G3 / G7 |
| Backend pytest | `.venv\Scripts\python.exe -m pytest --basetemp .pytest_tmp_project_baseline_20260525 -p no:cacheprovider` with `.venv\Scripts` prepended to `PATH` | Pass: 256 passed / 19 skipped | G7 / E2 |
| Full frontend Playwright E2E | bundled `node.exe .\node_modules\playwright\cli.js test --reporter=line` with Vite already running on `127.0.0.1:4173` | Pass: 33 tests | G2 / G3 / G4 / G7 |
| Test server cleanup | PowerShell `Get-NetTCPConnection -LocalPort 4173` and `Stop-Process` for the listener | Pass: manual Vite listener was stopped after the run | G7 |

### Findings and routing

- No blocker was found in the tested latest-main scope. Frontend typecheck, full Vitest, backend pytest, and full Playwright all passed.
- Full Playwright used a manually started Vite server, consistent with the prior Windows/PowerShell baseline. During the run, Vite emitted `/docs/doc_phase1_canvas` proxy connection-refused logs because the backend was not running in the frontend-only E2E setup; the tests passed and this remains covered by existing backend/recovery routing rather than a new blocker.
- Open PR convergence remains the largest release-management risk. The evidence lane recorded in `PROJECT-GOV` should continue to merge in dependency order: DATA-MAINT recovery evidence, MVP-EXIT intake, PRODUCT-QA gate record, and the independent support-bundle follow-up issue.
- No new ADR is required for this baseline record. The result is evidence capture and release-routing confirmation, not a policy or architecture change.

### Gate classification

| Gate | 2026-05-25 result | Reason |
| --- | --- | --- |
| G0 計画整合 | Go | active issue validation and triage pass with no stopper. |
| G1 安全既定 | Go for tested scope | full frontend regression and Playwright pass, including current share/export and read-only safety coverage in the suite. |
| G2 主要操作 | Go for tested scope | full Playwright pass covers representative authoring, import/visibility, read-only, canvas, diagnostics, and sharing flows. |
| G3 日本語UI | Go for tested scope | full frontend regression and Playwright pass after the current Japanese UI/i18n hardening. |
| G4 画面耐性 | Conditional Go | full Playwright pass includes the current viewport and keyboard scenarios, but release-candidate breadth still depends on the open product QA lane. |
| G5 公開文書 | N/A for this run | this refresh changed internal baseline evidence only and did not republish public documentation. |
| G6 診断とサポート | Conditional Go | diagnostics and recovery tests pass, while support-bundle policy follow-up remains tracked separately. |
| G7 回帰 | Go | frontend typecheck, full Vitest, backend pytest, and full Playwright pass. |

### Decision

- Baseline decision: **Conditional Go** for the latest-main health baseline.
- Release readiness decision: **No-Go** until the open evidence PR lane is merged or explicitly rejected, and the remaining DATA-MAINT/PRODUCT-OPS release conditions have a final product gate result.
- Follow-up routing:
  - Open PR convergence: `PROJECT-GOV-01`
  - Recovery evidence and PostgreSQL rehearsal: `DATA-MAINT-01`
  - Productization gate intake: `MVP-EXIT-01`
  - Release quality gate record: `PRODUCT-QA-01`
  - Support diagnostics bundle scope: `PRODUCT-OPS-01` / `PRODUCT-OPS-02`

## 14) Baseline delta 2026-05-26: governance-only refresh

### Candidate

- Target main: `origin/main` = `1a8ecd575e830f5fa51e537b75875840c69c7096`
- Baseline branch: `codex/project-gov-20260526-convergence`
- Scope note: this is a governance and planning delta after #2261..#2267 merged. It does not replace the 2026-05-25 full health baseline because no product runtime, frontend, backend, or public-documentation behavior is changed by this record.
- Executor: Codex
- Environment: Windows / PowerShell / backend `.venv`

### Command evidence

| Area | Command | Result | Gate mapping |
| --- | --- | --- | --- |
| Mainline intake | `git fetch --prune origin` and `git rev-parse origin/main` | Pass: `1a8ecd575e830f5fa51e537b75875840c69c7096` | G0 |
| Branch inventory | `git branch -r` count checks | Pass: remote branch count 2267, `origin/codex/` count 2245 | G0 |
| Open PR inventory | GitHub PR search | Pass: open PR count 1, #2270 only | G0 |
| Planning metadata | `03_Implement/backend/.venv/Scripts/python.exe 01_Plans/issues/validate_active_issue_memos.py` | Pass: `ok: validated 5 active issue memos` | G0 |
| Planning triage | `03_Implement/backend/.venv/Scripts/python.exe 01_Plans/triage_actionable_plans.py` | Pass: `active_issues=47 / ready=18 / blocked=29 / actionable_adrs=1 / stopper=none` | G0 |

### Findings and routing

- #2261..#2267 are now merged into `main`, so the prior "open evidence PR lane" release-management risk is resolved as a convergence issue.
- The only open PR is #2270, a Codex RTK token-saving runbook lane. It is developer-experience guidance and must not be counted as product runtime evidence, public user documentation, or release-candidate approval.
- No new blocker was found in planning metadata or triage. No full regression suite was rerun in this delta because the change is an internal governance record rather than application code or public documentation.

### Decision

- Baseline delta decision: **Go for planning convergence / unchanged for full release readiness**.
- Release readiness decision remains **No-Go** until a release-candidate gate record combines the merged recovery evidence with current SafeMode/share-export smoke evidence, representative user-operation E2E, value/UX evidence, and environment contract results.
- Follow-up routing:
  - Current open PR governance: `PROJECT-GOV-01`
  - DX/rtk adoption: `DX-CODEX-03`
  - Full release gate: `PRODUCT-QA-01`
  - Program release decision: `MVP-EXIT-01`

## 15) Baseline Record 2026-05-26: release-candidate evidence refresh

### Candidate

- Target main: `origin/main` = `1a8ecd575e830f5fa51e537b75875840c69c7096`
- Baseline branch: `codex/project-gov-20260526-convergence`
- Scope note: this record refreshes current release-candidate evidence after the DATA/MVP/QA/OPS evidence lane merged. It includes automated frontend/backend/browser/build/config checks, but it does not replace the need for final product value/UX owner decisions.
- Executor: Codex
- Environment: Windows / PowerShell / bundled Node (`C:\Users\yhata\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe`) / backend `.venv` / WSL2 Docker Compose

### Command evidence

| Area | Command | Result | Gate mapping |
| --- | --- | --- | --- |
| Planning metadata | `03_Implement/backend/.venv/Scripts/python.exe 01_Plans/issues/validate_active_issue_memos.py` | Pass: `ok: validated 5 active issue memos` | G0 |
| Planning triage | `03_Implement/backend/.venv/Scripts/python.exe 01_Plans/triage_actionable_plans.py` | Pass: `active_issues=47 / ready=18 / blocked=29 / actionable_adrs=1 / stopper=none` | G0 |
| Frontend typecheck | bundled `node.exe .\node_modules\typescript\bin\tsc --noEmit` | Pass | G7 |
| Targeted i18n/share/UX regression | bundled `node.exe .\node_modules\vitest\vitest.mjs run src/i18n/translate.test.ts src/i18n/key_consistency.test.ts src/i18n/ui_hardcode_guard.test.ts src/i18n/catalog_integrity.test.ts src/ui/SharePanel.test.ts src/ui/ux_operability_regression.test.ts` | Pass: 6 files / 39 tests | G1 / G2 / G3 / G7 |
| Frontend unit/regression | bundled `node.exe .\node_modules\vitest\vitest.mjs run` | Pass: 160 files / 734 tests | G1 / G3 / G7 |
| Frontend production build | bundled `node.exe .\node_modules\vite\bin\vite.js build` | Pass; existing chunk-size warning only | G7 / E1 |
| Backend pytest | `.venv\Scripts\python.exe -m pytest --basetemp .pytest_tmp_rc_20260526_full_path -p no:cacheprovider` with `.venv\Scripts` prepended to `PATH` | Pass: 260 passed / 19 skipped | G7 / E2 |
| Full frontend Playwright E2E | bundled `node.exe .\node_modules\playwright\cli.js test --reporter=line` with Vite manually running on `127.0.0.1:4173` | Pass: 33 tests | G1 / G2 / G3 / G4 / G6 / G7 |
| Compose version | WSL2 `docker compose version` | Pass: `Docker Compose version v2.39.1` | E3 |
| Compose config | WSL2 `docker compose config` in `03_Implement/deploy` | Pass; public `KJ_ATLAS_*` inputs render and private `POSTGRES_*` adapter env names remain internal to the PostgreSQL service | E3 |
| Public env contract scan | `rg` scan for non-prefixed env names across 04/02/deploy | Pass for public contract; hits are private-boundary notes or `KJ_ATLAS_*` public settings | E1 / G5 |
| Test server cleanup | `Stop-Process` for Vite listener on port 4173 | Pass: no listener remains | G7 |

### Environment findings

- The default PowerShell `node.exe` resolved to the Codex WindowsApps shim and failed with `Access is denied`. Bundled Node.js by absolute path worked for typecheck, Vitest, build, and Playwright.
- PowerShell `docker` was not on `PATH`, but WSL2 Docker Compose was available and rendered the Compose config successfully.
- The first backend pytest run failed only because subprocess `alembic` was not visible on `PATH`. Rerunning with backend `.venv\Scripts` prepended to `PATH` passed.
- GitHub Actions CI run #9141 failed at `actions/checkout@v4` with a GitHub 403 account/repository operation error before code checkout. This was not an application test failure. Subsequent CI run #9143 on `5fd1a304dc0577678b3d2afe4ed18642512e4286` passed all jobs, so `PROJECT-CI-01` is closed as a transient checkout/auth incident and #9143 is the current PR G7 evidence.
- No generated test artifacts were retained; `.pytest_tmp_*` and frontend `test-results/` were removed after verification.

### Gate classification

| Gate | 2026-05-26 result | Reason |
| --- | --- | --- |
| G0 計画整合 | Go | active issue validation and triage pass with no stopper. |
| G1 安全既定 | Go for tested scope | targeted SharePanel/i18n/UX regression, full Vitest, and Playwright safe-mode/read-only/safe-sharing flows pass. |
| G2 主要操作 | Go for tested scope | full Playwright pass covers realistic journey, authoring continuity, safe sharing gate, keyboard focus, canvas/polygon operations, visibility, and recovery paths. |
| G3 日本語UI | Go for tested scope | targeted i18n checks and full frontend regression pass. |
| G4 画面耐性 | Go for tested scope | full Playwright includes header layout, 390px recovery paths, large document, progress/cancel, and focus return coverage. |
| G5 公開文書/設定契約 | Conditional Go | public env contract scan and Compose config pass; public documentation was not republished. |
| G6 診断とサポート | Conditional Go | recovery guidance E2E passes; support diagnostics bundle policy remains a follow-up boundary. |
| G7 回帰 | Go | frontend typecheck/full Vitest/build, backend pytest, and full Playwright pass after environment normalization. |
| E1..E3 環境契約 | Conditional Go | settings tests/build/env scan/Compose config pass; full running Compose service startup was not executed. |

### Decision

- Baseline decision: **Conditional Go** for the current release-candidate evidence refresh.
- Release readiness decision: **No-Go** until product value/UX Draft gates have assigned owners and explicit evidence routes, and a final release-candidate gate record is approved.
- Follow-up routing:
  - Historical CI checkout/auth incident: `PROJECT-CI-01` (Done after CI run #9143 success)
  - Product value and UX gates: `PRODUCT-VALUE-01..03`, `PRODUCT-UX-01..04`
  - Release quality gate: `PRODUCT-QA-01`
  - Program release decision: `MVP-EXIT-01`
  - Support bundle policy: `PRODUCT-OPS-02`

## 16) Baseline Record 2026-05-31: latest main lightweight refresh

### Candidate

- Target main: `origin/main` = `0d705c2ed6d92b01346edebc406058e4ea09a9bb`
- Baseline branch: `codex/project-baseline-20260531-refresh`
- Scope note: this record refreshes latest-main evidence after the 2026-05-31 planning/evidence lane merged to main. It is a lightweight release-candidate baseline, not a full shipment approval.
- Open PRs not included in this main baseline: #2282 (`DATA-MAINT-03` high-privilege lifecycle policy) and #2283 (`DATA-MAINT-02` closeout).
- Executor: Codex
- Environment: Windows / PowerShell / bundled Node (`C:\Users\yhata\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe`) / backend `.venv` / manual Vite server on `127.0.0.1:4173`

### Command evidence

| Area | Command | Result | Gate mapping |
| --- | --- | --- | --- |
| Mainline intake | `git checkout main; git pull --ff-only origin main; git rev-parse HEAD` | Pass: `0d705c2ed6d92b01346edebc406058e4ea09a9bb` | G0 |
| Planning metadata | `03_Implement/backend/.venv/Scripts/python.exe 01_Plans/issues/validate_active_issue_memos.py` | Pass: `ok: validated 5 active issue memos` | G0 |
| Planning triage | `03_Implement/backend/.venv/Scripts/python.exe 01_Plans/triage_actionable_plans.py` | Pass: `active_issues=41 / ready=16 / blocked=25 / actionable_adrs=1 / stopper=none` | G0 |
| Frontend typecheck | bundled `node.exe .\node_modules\typescript\bin\tsc --noEmit` | Pass | G7 |
| Targeted i18n/share/UX/import/export regression | bundled `node.exe .\node_modules\vitest\vitest.mjs run ...` for SharePanel, SafeMode status, i18n guards, UX operability, import/export, diff workflow, and validation tests | Pass: 16 files / 139 tests | G1 / G2 / G3 / G7 |
| Frontend production build | bundled `node.exe .\node_modules\vite\bin\vite.js build` | Pass; existing chunk-size warning only | G7 / E1 |
| Backend selected regression | `.venv\Scripts\python.exe -m pytest test_settings_env_prefix_migration.py test_docs_roundtrip.py test_docs_audit_integration.py test_docs_access_control_integration.py test_data_maintenance_recovery_exercise.py -q --basetemp ... -p no:cacheprovider` | Pass: 65 passed / 16 skipped | G5 / G6 / G7 |
| Representative Playwright smoke | manual Vite server + bundled `node.exe .\node_modules\playwright\cli.js test ce3_patch_workspace.spec.ts auth_context_level1_smoke.spec.ts ops_recovery_guidance.spec.ts --reporter=line` | Pass: 7 tests | G2 / G4 / G6 / G7 |
| Test server cleanup | `Get-NetTCPConnection -LocalPort 4173` + `Stop-Process` | Pass: stopped PID 30920; no listener remains | G7 |
| Artifact cleanup | removed `.pytest_tmp_baseline_20260531`, `frontend/test-results`, and `frontend/dist` after verification | Pass: working tree clean before documentation edit | G7 |

### Environment findings

- Bundled Node by absolute path was used for frontend typecheck, Vitest, build, and Playwright. This avoids relying on the host `npm` command in PowerShell.
- Playwright config uses `npm run dev` for its `webServer`. To keep the baseline independent of host `npm`, Vite was started manually with bundled Node and Playwright reused the existing server.
- The first Playwright command used path patterns that did not match the configured `testDir`; it returned "No tests found". Re-running with `testDir`-relative file names passed and is the recorded smoke result.
- No application regression was found in the tested scope.

### Gate classification

| Gate | 2026-05-31 result | Reason |
| --- | --- | --- |
| G0 計画整合 | Go | latest main intake, active issue validation, and triage pass with no stopper. |
| G1 安全既定 | Go for tested scope | SharePanel, SafeMode status, import/export, and targeted regression tests pass. |
| G2 主要操作 | Go for tested scope | representative Playwright smoke covers CE3 patch workspace, read-only auth boundary, and recovery guidance flows. |
| G3 日本語UI | Go for tested scope | targeted i18n guard and catalog tests pass. |
| G4 画面耐性 | Go for tested scope | representative Playwright smoke passes; full viewport matrix was not rerun. |
| G5 公開文書/設定契約 | Conditional Go | settings/env-prefix and docs contract tests pass; public documentation was not republished in this run. |
| G6 診断とサポート | Conditional Go | recovery guidance smoke and data-maintenance recovery tests pass; support diagnostics bundle policy remains a follow-up boundary. |
| G7 回帰 | Go for tested scope | frontend typecheck, targeted Vitest, build, backend selected regression, and Playwright smoke pass. |
| E1..E3 環境契約 | Conditional Go | frontend build and env-prefix tests pass; full running Compose stack was not started in this run. |

### Decision

- Baseline decision: **Conditional Go** for latest-main lightweight evidence refresh.
- Release readiness decision: **No-Go** for full shipment until product value/UX gates, full release-candidate E2E evidence, and environment/operations gates are approved together.
- Follow-up routing:
  - High-privilege data lifecycle policy: PR #2282 / `DATA-MAINT-03`
  - DATA-MAINT-02 closeout: PR #2283
  - Product value and UX gates: `PRODUCT-VALUE-01..03`, `PRODUCT-UX-01..04`
  - Full release gate: `PRODUCT-QA-01`
  - Program release decision: `MVP-EXIT-01`

### Follow-up accountability

| Item | Owner | Due | Re-decision date |
| --- | --- | --- | --- |
| Product value / UX evidence routes | Productization Program Owner + Codex evidence steward | 2026-06-07 | 2026-06-10 |
| Full release-candidate E2E and viewport matrix | QA owner + Codex evidence steward | 2026-06-07 | 2026-06-10 |
| Open data-maintenance PR lane (#2282/#2283) | Codex author / Repository Maintainer reviewer | 2026-06-03 | 2026-06-05 |
| Full Compose service startup and operations gate | Platform operator + Codex evidence steward | 2026-06-07 | 2026-06-10 |

## 17) Baseline Record 2026-06-01: merged planning and data-maintenance lane refresh

### Candidate

- Target main: `origin/main` = `01fea1bb2724356f53077d4df52a296d21ed2f67`
- Baseline branch: `codex/latest-main-gate-sync-20260601`
- Scope note: this record refreshes the latest-main baseline after PR #2282, #2283, #2284, and #2285 were merged. It is a planning/gate synchronization record only; no frontend, backend, runtime configuration, SafeMode, or public documentation behavior is changed in this slice.
- Executor: Codex
- Environment: Windows / PowerShell / backend `.venv` / RTK used only for compact read-only command output where exact output was not required.

### Command evidence

| Area | Command | Result | Gate mapping |
| --- | --- | --- | --- |
| Mainline intake | `git checkout main`; `git pull --ff-only origin main`; `git rev-parse origin/main` | Pass: `01fea1bb2724356f53077d4df52a296d21ed2f67` | G0 |
| Planning metadata | `03_Implement/backend/.venv/Scripts/python.exe 01_Plans/issues/validate_active_issue_memos.py` | Pass: `ok: validated 5 active issue memos` | G0 |
| Planning triage | `03_Implement/backend/.venv/Scripts/python.exe 01_Plans/triage_actionable_plans.py` | Pass: `active_issues=41 / ready=16 / blocked=25 / actionable_adrs=1 / stopper=none` | G0 |
| Issue validator tests | `03_Implement/backend/.venv/Scripts/python.exe -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` | Pass: 10 tests | G0 / G7 |
| Triage tests | `03_Implement/backend/.venv/Scripts/python.exe -m unittest 01_Plans/tests/test_triage_actionable_plans.py` | Pass: 1 test | G0 / G7 |
| GitHub PR inventory | GitHub connector recent/open PR search | Open PRs: 0; recent merged PRs include #2282, #2283, #2284, #2285 | G0 |

### Incorporated mainline changes

| PR | Mainline result | Baseline impact |
| --- | --- | --- |
| #2282 `DATA-MAINT-03` high-privilege lifecycle policy split | Merged into `main` before this refresh | High-privilege delete/archive/owner-transfer/admin-body-access/retention decisions are now tracked as a dedicated Open issue. |
| #2283 `DATA-MAINT-02` recovery exercise closeout | Merged into `main` before this refresh | Representative recovery exercise evidence is closed out; organization-specific backup policy remains outside that issue. |
| #2284 latest-main lightweight baseline | Merged into `main` before this refresh | 2026-05-31 lightweight baseline record is now canonical on `main`. |
| #2285 ADR-0035 proposal | Merged into `main` before this refresh | High-privilege data lifecycle product-boundary proposal is now recorded as Proposed ADR-0035. |

### Gate classification

| Gate | 2026-06-01 result | Reason |
| --- | --- | --- |
| G0 計画整合 | Go | latest main intake, active issue validation, triage, validator unit tests, and triage unit test pass with no stopper. |
| G1 安全既定 | Unchanged / Conditional Go | This slice does not change SafeMode, share/export, import sanitize, or data access behavior. ADR-0035 keeps high-privilege body/destructive operations outside standard MVP/productization behavior unless a future ADR changes that boundary. |
| G2 主要操作 | Unchanged / Conditional Go | No browser or application workflow was re-tested in this planning-only refresh. Prior evidence remains valid for its recorded scope. |
| G3 日本語UI | Unchanged | No UI copy changed. |
| G4 画面耐性 | Unchanged / Conditional Go | No viewport matrix or screenshot run was executed in this refresh. |
| G5 公開文書/設定契約 | Unchanged / Conditional Go | Public documentation and runtime configuration were not republished or changed in this refresh. |
| G6 診断とサポート | Conditional Go | DATA-MAINT-02 recovery evidence is closed out on `main`; support diagnostics bundle policy remains a separate follow-up boundary. |
| G7 回帰 | Go for planning checks | Planning validators and their unit tests pass. Runtime/frontend/backend regression suites were intentionally not rerun because this slice records merged planning and ADR state only. |
| E1..E3 環境契約 | Unchanged / Conditional Go | Full running Compose service startup was not executed. |

### Decision

- Baseline decision: **Conditional Go** for the latest-main planning and data-maintenance lane refresh.
- Release readiness decision: **No-Go** for full shipment until product value gates, full release-candidate E2E/viewport evidence, environment/operations gates, and final program approval are recorded together.
- Follow-up routing:
  - `DATA-MAINT-03`: remains Open until ADR-0035 is accepted or replaced by a later decision.
  - `PRODUCT-VALUE-01..03`: remain Draft until ADR-0032 is accepted or Productization Program Owner approval explicitly authorizes provisional value-gate execution.
  - Full release-candidate evidence: `PRODUCT-QA-01`.
  - Program release decision: `MVP-EXIT-01`.
  - Branch cleanup: `PROJECT-GOV-01`; open PR lane is drained, but branch deletion remains a permissioned maintenance action.

### Follow-up accountability

| Item | Owner | Due | Re-decision date |
| --- | --- | --- | --- |
| ADR-0035 decision for high-privilege data lifecycle boundary | Project Maintainers + Codex evidence steward | 2026-06-05 | 2026-06-07 |
| Product value gate approval or provisional execution decision | Productization Program Owner + Codex evidence steward | 2026-06-07 | 2026-06-10 |
| Full release-candidate E2E, viewport, and screenshot evidence | QA owner + Codex evidence steward | 2026-06-07 | 2026-06-10 |
| Full Compose service startup and operations gate | Platform operator + Codex evidence steward | 2026-06-07 | 2026-06-10 |

## 18) Baseline delta 2026-06-02: gate sync and governance checkpoint merged

### Candidate

- Target main: `origin/main` = `44d9c526a83f1fad60a172895a9bbe7e1db02365`
- Baseline branch: `codex/latest-main-20260602-baseline-governance-sync`
- Scope note: this is a lightweight planning/governance baseline delta after #2291 and #2292 merged. It confirms that the latest productization gate sync and repository-governance checkpoint are now on `main`; it does not rerun browser, frontend, backend, Compose, SafeMode, share/export, import sanitize, or public documentation checks.
- Executor: Codex
- Environment: Windows / PowerShell / backend `.venv` / GitHub connector / RTK used only for compact read-only output where exact output was not required.

### Command evidence

| Area | Command | Result | Gate mapping |
| --- | --- | --- | --- |
| Mainline intake | `git checkout main`; `git pull --ff-only origin main`; `git rev-parse origin/main` | Pass: `44d9c526a83f1fad60a172895a9bbe7e1db02365` | G0 |
| Planning metadata | `03_Implement/backend/.venv/Scripts/python.exe 01_Plans/issues/validate_active_issue_memos.py` | Pass: `ok: validated 5 active issue memos` | G0 |
| Planning triage | `03_Implement/backend/.venv/Scripts/python.exe 01_Plans/triage_actionable_plans.py` | Pass: `active_issues=41 / ready=15 / blocked=26 / actionable_adrs=1 / stopper=none` | G0 |
| Issue validator tests | `03_Implement/backend/.venv/Scripts/python.exe -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` | Pass: 10 tests | G0 / G7 |
| Triage tests | `03_Implement/backend/.venv/Scripts/python.exe -m unittest 01_Plans/tests/test_triage_actionable_plans.py` | Pass: 1 test | G0 / G7 |
| GitHub PR inventory | GitHub connector open PR search | Pass: open PRs 0 | G0 |

### Incorporated mainline changes

| PR | Mainline result | Baseline impact |
| --- | --- | --- |
| #2288 | Merged into `main` before this refresh | `DATA-CONTRACT-01` is closed for the current DocumentV2/API/support-level baseline. |
| #2289 | Merged into `main` before this refresh | `DATA-MAINT-01` unresolved decision routing now points to `ADR-0035`, `DATA-MAINT-03`, and `DATA-MAINT-04`. |
| #2290 | Merged into `main` before this refresh | `DATA-MAINT-04` audit metadata baseline and boundary wording are now on `main`. |
| #2291 | Merged into `main` before this refresh | `PRODUCT-QA-01` and `MVP-EXIT-01` now record that data-contract closeout is Conditional Go for the contract slice, while full shipment remains No-Go. |
| #2292 | Merged into `main` before this refresh | `PROJECT-GOV-01` now records the prior open productization gate sync lane and cleanup candidates. |

### Gate classification

| Gate | 2026-06-02 result | Reason |
| --- | --- | --- |
| G0 險育判謨ｴ蜷・| Go | latest main intake, active issue validation, triage, validator unit tests, triage unit test, and open PR inventory pass with no stopper. |
| G1 螳牙・譌｢螳・| Unchanged / Conditional Go | This delta records merged planning and governance evidence only. SafeMode, share/export, import sanitize, and data-access behavior were not changed or re-tested. |
| G2 荳ｻ隕∵桃菴・| Unchanged / Conditional Go | No browser or representative user workflow was re-tested in this delta. Prior evidence remains valid only for its recorded scope. |
| G3 譌･譛ｬ隱朸I | Unchanged | No UI copy changed in this baseline delta. |
| G4 逕ｻ髱｢閠先ｧ | Unchanged / Conditional Go | No viewport matrix, screenshot run, or mouse/keyboard operation review was executed in this delta. |
| G5 蜈ｬ髢区枚譖ｸ/險ｭ螳壼･醍ｴ・| Unchanged / Conditional Go | Public documentation and runtime configuration were not republished or changed in this delta. |
| G6 險ｺ譁ｭ縺ｨ繧ｵ繝昴・繝・| Unchanged / Conditional Go | Support diagnostics and operations behavior were not re-tested; prior follow-up boundaries remain in force. |
| G7 蝗槫ｸｰ | Go for planning checks | Planning validators and their unit tests pass. Runtime/frontend/backend regression suites were intentionally not rerun because this delta only records merged gate/governance state. |
| E1..E3 迺ｰ蠅・･醍ｴ・| Unchanged / Conditional Go | Full running Compose service startup was not executed. |

### Decision

- Baseline delta decision: **Conditional Go** for latest-main planning and governance convergence.
- Release readiness decision remains **No-Go** for full shipment. The merged #2291 gate record closes the current data-contract slice for the documented baseline, but it does not provide product value evidence, full release-candidate E2E/viewport/screenshot evidence, full Compose startup evidence, or final program approval.
- Follow-up routing:
  - Product value gates: `PRODUCT-VALUE-01..03`.
  - Full release-candidate evidence and approval: `PRODUCT-QA-01` and `MVP-EXIT-01`.
  - Repository branch cleanup: `PROJECT-GOV-01`; no branch deletion is executed by this baseline delta.
  - High-privilege data lifecycle and audit metadata follow-up: `DATA-MAINT-03`, `DATA-MAINT-04`, and `ADR-0035`.

### Follow-up accountability

| Item | Owner | Due | Re-decision date |
| --- | --- | --- | --- |
| Product value gate approval or provisional execution decision | Productization Program Owner + Codex evidence steward | 2026-06-07 | 2026-06-10 |
| Full release-candidate E2E, viewport, and screenshot evidence | QA owner + Codex evidence steward | 2026-06-07 | 2026-06-10 |
| Full Compose service startup and operations gate | Platform operator + Codex evidence steward | 2026-06-07 | 2026-06-10 |
| Post-merge branch cleanup decision for #2288..#2292 branches | Repository Maintainer + Codex evidence steward | 2026-06-05 | 2026-06-07 |

## 19) Baseline delta 2026-06-03: UI evidence and targeted E2E merged

### Candidate

- Target main: `origin/main` = `455dc1bea8d2d9b4190daf4c47820a9be9ed49f8`
- Scope note: this is a lightweight post-merge baseline after #2304, #2305, and #2306 landed. It records UI evidence and targeted E2E checks only; it does not grant release shipment approval, rerun full frontend/backend regression, publish public documentation, or execute full Compose startup.
- Executor: Codex
- Environment: Windows / PowerShell / bundled Node / manual Vite server on `127.0.0.1:4173` / RTK used for compact command output where exact failure detail was not needed.

### Command evidence

| Area | Command | Result | Gate mapping |
| --- | --- | --- | --- |
| Mainline intake | `git pull --ff-only origin main`; `git rev-parse HEAD origin/main` | Pass: both resolve to `455dc1bea8d2d9b4190daf4c47820a9be9ed49f8` | G0 |
| Planning metadata | `python 01_Plans/issues/validate_active_issue_memos.py` | Pass: `ok: validated 5 active issue memos` | G0 |
| Planning triage | `python 01_Plans/triage_actionable_plans.py --root 01_Plans --format text` | Pass: `active_issues=52 / ready=15 / blocked=37 / actionable_adrs=1 / stopper=none` | G0 |
| Targeted UI E2E | `node .\node_modules\playwright\cli.js test e2e/first_run_document_entry.spec.ts e2e/i18n_locale_query_equivalence.spec.ts --reporter=line` | Pass: 7 tests | G2 / G3 / G7 |

### Incorporated mainline changes

| PR | Mainline result | Baseline impact |
| --- | --- | --- |
| #2304 | Merged into `main` before this refresh | Focused Chrome UI evidence and human-owned task queue are now canonical release-gate input. |
| #2305 | Merged into `main` before this refresh | First-run sample entry E2E and frontend CI lockfile cache-path fix are now on `main`. |
| #2306 | Merged into `main` before this refresh | Invalid `?locale=zz` fallback E2E and `Draft-AC-G2` I18N evidence note are now on `main`. |

### Gate classification

| Gate | 2026-06-03 result | Reason |
| --- | --- | --- |
| G0 planning integrity | Go | Latest main intake, active issue validation, and triage pass with no stopper. |
| G1 safety defaults | Conditional Go / unchanged | This delta does not change SafeMode, share/export, import sanitize, or access-control behavior. The #2304 UI evidence remains the latest observed SafeMode/share preflight evidence. |
| G2 primary user operations | Conditional Go improved | First-run sample entry, file-entry validation, selection context, and keyboard activation E2E now pass on `main`; release-candidate physical keyboard traversal and screenshots remain human tasks. |
| G3 Japanese UI / i18n | Go for tested scope | `?locale=en` shell labels, invalid `?locale=zz` Japanese fallback, and English document replace flow pass in targeted E2E. |
| G4 viewport and operability | Conditional Go / unchanged | #2304 records 390px measurement evidence, but this delta does not add release screenshots or a full viewport matrix. |
| G5 public docs and config | Unchanged / Conditional Go | No public documentation publication or Compose evidence was produced in this slice. |
| G6 diagnostics and support | Unchanged / Conditional Go | No new support diagnostics or recovery behavior was tested. |
| G7 regression | Go for targeted UI E2E and planning checks | Targeted Playwright and planning checks pass; full frontend/backend regression was not rerun in this lightweight delta. |

### Decision

- Baseline delta decision: **Conditional Go** for latest-main UI evidence and targeted E2E intake.
- Release readiness decision remains **No-Go** for full shipment until release screenshots, physical keyboard evidence, product value Open gates, full release-candidate regression, Compose startup, and final program approval are recorded together.
- Follow-up routing:
  - Release screenshots and physical keyboard traversal: `PRODUCT-QA-01` human task queue from #2304.
  - Product value gates: `PRODUCT-VALUE-01..03`.
  - Full release-candidate evidence and approval: `PRODUCT-QA-01` and `MVP-EXIT-01`.
  - Full Compose service startup and environment rehearsal: `ENV-CONFIG-DRIFT-01` / platform operator lane.

## 20) Baseline Record 2026-06-03: full local regression and Chrome smoke refresh

### Candidate

- Target main: `origin/main` = `92b4e3f2bdf91d185f56ab3b7a54cb458b7d4e33`
- Baseline branch: `codex/project-baseline-20260603`
- Scope note: this record refreshes latest-main health after #2309 was merged. It records full local frontend/backend regression, production build, full Playwright E2E, and a focused full-stack Chrome smoke. It does not change runtime behavior, UI copy, SafeMode defaults, schema/API contracts, public documentation, release authority, or Compose configuration.
- Executor: Codex
- Environment: Windows / PowerShell / bundled Node / backend `.venv` / manual Vite on `127.0.0.1:4173` / manual Uvicorn on `127.0.0.1:8000` / RTK used for compact verbose output where exact failure detail was not required.

### Command evidence

| Area | Command | Result | Gate mapping |
| --- | --- | --- | --- |
| Mainline intake | `git pull --ff-only origin main`; `git rev-parse HEAD` | Pass: `92b4e3f2bdf91d185f56ab3b7a54cb458b7d4e33` | G0 |
| Planning metadata | `python 01_Plans/issues/validate_active_issue_memos.py` | Pass: `ok: validated 5 active issue memos` | G0 |
| Planning triage | `python 01_Plans/triage_actionable_plans.py --root 01_Plans --format text` | Pass: `active_issues=52 / ready=15 / blocked=37 / actionable_adrs=1 / stopper=none` | G0 |
| Frontend typecheck | bundled `node.exe .\node_modules\typescript\bin\tsc --noEmit` | Pass | G7 |
| Frontend unit/regression | bundled `node.exe .\node_modules\vitest\vitest.mjs run` | Pass: 160 files / 734 tests | G1 / G3 / G7 |
| Backend pytest | `.venv\Scripts\python.exe -m pytest --basetemp ..\..\.pytest_tmp_project_baseline_20260603 -p no:cacheprovider` with `.venv\Scripts` prepended to `PATH` | Pass: 260 passed / 19 skipped | G7 / E2 |
| Full frontend Playwright E2E | bundled `node.exe .\node_modules\playwright\cli.js test --reporter=line` with Vite already running on `127.0.0.1:4173` | Pass: 38 tests | G2 / G3 / G4 / G7 |
| Backend migration | `.venv\Scripts\python.exe -m alembic upgrade head` | Pass on local SQLite | E2 |
| Backend health | `GET http://127.0.0.1:8000/healthz` | Pass: `{"status":"ok"}` | G6 / E2 |
| Frontend production build | bundled `node.exe .\node_modules\vite\bin\vite.js build` | Pass; existing chunk-size warning only | G7 |
| Server cleanup | stopped temporary Vite and Uvicorn processes; verified ports 4173 and 8000 had no listeners | Pass | G7 |

### Chrome smoke evidence

- Target: `http://127.0.0.1:4173/`
- Browser title: `kj-atlas`
- Full-stack startup: backend `/healthz` returned `ok`; after reload the initial page showed no `HTTP 500` document-load error.
- Initial UI: SafeMode ON was visible; first-run choices were visible, including creating a new document, opening the sample, loading `document.json`, importing a review pack, and opening the previous document.
- Mouse operation: clicking the sample-open button loaded sample content with SafeMode still ON.
- Share/export operation: clicking the share/reproduce button opened the share dialog with export, review-pack, import/recovery, patch-check, and diff controls.
- Share dialog fit: viewport `{ width: 562, height: 694, scrollWidth: 562 }`; dialog rectangle `{ x: 16, y: 227, right: 356, bottom: 678, width: 340, height: 451 }`; right and bottom clipping were both false.
- Safe share copy: fixed-mask copy for Share / Review Pack was present in the share dialog.
- Keyboard close: pressing `Escape` on the dialog closed it (`dialogCount=0`) and returned focus toward the share trigger area.
- Console: browser error log count was 0 during the focused full-stack smoke.
- Screenshot limitation: in-app browser screenshot capture timed out twice at `Page.captureScreenshot`; this is treated as evidence-capture limitation, not as a UI defect. Release screenshots remain human-owned evidence.

### Gate classification

| Gate | 2026-06-03 result | Reason |
| --- | --- | --- |
| G0 planning integrity | Go | Latest main intake, active issue validation, and triage pass with no stopper. |
| G1 safety defaults | Go for tested scope | Full Vitest passes, SafeMode ON is visible in Chrome, and fixed-mask share/review-pack copy is present in the share dialog. |
| G2 primary user operations | Go for tested scope | Full Playwright E2E passes and the focused Chrome smoke covers first-run entry, sample open, share/export preflight, and keyboard close. |
| G3 Japanese UI / i18n | Go for tested scope | Full Vitest and full Playwright pass; observed Chrome surfaces were Japanese for the tested flow. |
| G4 viewport and operability | Conditional Go improved | Full Playwright viewport/operability coverage passes, and the focused Chrome share dialog did not clip at the observed 562px viewport. Release screenshot capture still remains human-owned because in-app screenshot capture timed out. |
| G5 public docs and config | Unchanged / Conditional Go | No public documentation was republished and no configuration contract was changed in this refresh. |
| G6 diagnostics and support | Conditional Go improved | Backend health passed and the full-stack Chrome smoke had no console errors. Support diagnostics bundle policy and final operational rehearsal remain separate gates. |
| G7 regression | Go | Frontend typecheck, full Vitest, backend pytest, production build, full Playwright E2E, and cleanup all pass. |
| E1..E3 environment contract | Conditional Go | Local Vite/Uvicorn startup and backend migration pass, but full Docker Compose startup was not executed. |

### Decision

- Baseline decision: **Conditional Go** for latest-main full local regression and focused full-stack Chrome smoke.
- Release readiness decision remains **No-Go** for full shipment until human release screenshots, physical keyboard evidence, product value Open gates, full Compose startup, and final program approval are recorded together.
- Follow-up routing:
  - H-UI-01 release screenshots and H-UI-02 physical keyboard traversal: `PRODUCT-QA-01`.
  - Product value gates and evidence packets: `PRODUCT-VALUE-01..03`.
  - Full release-candidate evidence and approval: `PRODUCT-QA-01` and `MVP-EXIT-01`.
  - Full Compose startup and environment rehearsal: `ENV-CONFIG-DRIFT-01` / platform operator lane.

## 21) Baseline delta 2026-06-04: #2310 documentation-only main sync

### Candidate

- Target main: `origin/main` = `cb277db730da9f91d22c08cee0cc8af348a92220`
- Previous full-regression baseline: `origin/main@92b4e3f2bdf91d185f56ab3b7a54cb458b7d4e33` in section 20.
- Merged PR: #2310 `[codex] Record latest main regression baseline`.
- Scope note: #2310 only merged internal evidence records in `01_Plans/issues`. This delta records the post-merge main state and CI health for that documentation-only merge. It does not change runtime behavior, UI copy, SafeMode defaults, schema/API contracts, public documentation, release authority, or Compose configuration.
- Executor: Codex
- Environment: Windows / PowerShell / bundled Python / GitHub connector for CI inspection / RTK used for compact status output where exact command text was not required.

### Command and CI evidence

| Area | Command or source | Result | Gate mapping |
| --- | --- | --- | --- |
| Mainline intake | `git pull --ff-only`; `git rev-parse origin/main`; `git log -1 --format="%h %cI %s" origin/main` | Pass: `cb277db7` at `2026-06-03T22:01:31+09:00`, merge commit for #2310 | G0 |
| Mainline diff boundary | `git diff --name-status 92b4e3f2bdf91d185f56ab3b7a54cb458b7d4e33..origin/main` | Pass: only `issue-MVP-EXIT-01-productization-readiness.md`, `issue-PRODUCT-QA-01-release-readiness-quality-gates.md`, and this issue changed | G0 / G7 |
| PR #2310 CI | GitHub Actions run `26881310930` on head `35e1eed54d27db52d469dfe26d6245697acf254e` | Pass: frontend lint, typecheck, frontend test/build, i18n guards, import/serialization/shape regression guards, and backend lint/test all succeeded | G1 / G3 / G7 |
| Planning metadata | `python 01_Plans/issues/validate_active_issue_memos.py` | Pass: `ok: validated 5 active issue memos` | G0 |
| Planning triage | `python 01_Plans/triage_actionable_plans.py --root 01_Plans --format text` | Pass: `active_issues=52 / ready=15 / blocked=37 / actionable_adrs=1 / stopper=none` | G0 |

### Incorporated mainline change

| PR | Mainline result | Baseline impact |
| --- | --- | --- |
| #2310 | Merged into `main` as `cb277db730da9f91d22c08cee0cc8af348a92220` | Section 20 full local regression evidence is now canonical on `main`; no implementation, runtime, public-doc, or configuration files changed after that full-regression candidate. |

### Gate classification

| Gate | 2026-06-04 result | Reason |
| --- | --- | --- |
| G0 planning integrity | Go | Latest main intake, documentation-only diff boundary, active issue validation, and triage pass with no stopper. |
| G1 safety defaults | Unchanged / Go for previously tested scope | #2310 did not change SafeMode, share/export, import sanitize, or access-control behavior. Section 20 remains the latest runtime evidence. |
| G2 primary user operations | Unchanged / Go for previously tested scope | #2310 did not change frontend behavior. Section 20 remains the latest full Playwright and Chrome smoke evidence. |
| G3 Japanese UI / i18n | Unchanged / Go for previously tested scope | #2310 did not change UI strings. PR #2310 CI i18n guard jobs succeeded. |
| G4 viewport and operability | Unchanged / Conditional Go | No new viewport, screenshot, or physical-keyboard evidence was added. Section 20 remains the latest automated and Chrome-smoke evidence. |
| G5 public docs and config | Unchanged / Conditional Go | No public documentation publication or runtime configuration change occurred in #2310. |
| G6 diagnostics and support | Unchanged / Conditional Go | No support diagnostics or operational recovery behavior changed in #2310. |
| G7 regression | Go for this delta | PR #2310 CI succeeded and the post-merge diff is limited to internal planning evidence records. Full local regression is not rerun because no implementation files changed after section 20. |
| E1..E3 environment contract | Unchanged / Conditional Go | Full Docker Compose startup remains outside this documentation-only sync. |

### Decision

- Baseline decision: **Conditional Go** for the #2310 documentation-only main sync.
- Release readiness decision remains **No-Go** for full shipment until human release screenshots, physical keyboard evidence, product value Open gates/evidence packets, full Compose startup, and final program approval are recorded together.
- Open-PR note: draft PR #2315 (`codex/domain-expression-keyboard-evidence-20260604`) is not included in this mainline baseline. Its DOMAIN-EXPR-01 keyboard evidence should be treated as candidate evidence until merged.
- Follow-up routing:
  - H-UI-01 release screenshots and H-UI-02 physical keyboard traversal: `PRODUCT-QA-01`.
  - Product value gates and evidence packets: `PRODUCT-VALUE-01..03`.
  - DOMAIN-EXPR-01 keyboard evidence intake after merge: `issue-DOMAIN-EXPR-01-readonly-state-surfacing.md`.
  - Full Compose startup and environment rehearsal: `ENV-CONFIG-DRIFT-01` / platform operator lane.

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している（未運用時は `N/A`）。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
