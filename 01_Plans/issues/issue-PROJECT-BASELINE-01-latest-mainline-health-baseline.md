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
| Frontend unit/regression | bundled `node.exe .\node_modules\vitest\vitest.mjs run` | Pass: 160 files / 732 tests | G1 / G3 / G7 |
| Full frontend Playwright E2E | bundled `node.exe .\node_modules\playwright\cli.js test --reporter=line` with Vite already running on `127.0.0.1:4173` | Pass: 29 tests | G2 / G3 / G4 / G7 |
| Canvas/polygon E2E focus | `e2e/polygon_vertex_edit.spec.ts e2e/polygon_autofit_qa_boundary.spec.ts` | Pass: 4 tests | G2 / G4 |
| Header panel viewport/keyboard focus | bundled `node.exe .\node_modules\playwright\cli.js test e2e/header_toolbar_layout.spec.ts --reporter=line` | Pass: 7 tests covering 1440px / 1280px / 920px / 768px / 390px fit and 1440px / 768px Enter/Escape focus return | G2 / G4 |
| Polygon edit keyboard focus | bundled `node.exe .\node_modules\playwright\cli.js test e2e/polygon_vertex_edit.spec.ts --reporter=line` | Pass: 2 tests covering pointer drag plus keyboard nudge/removal persistence | G2 / G4 |
| Large-document operability | bundled `node.exe .\node_modules\playwright\cli.js test e2e/large_document_operability.spec.ts --reporter=line` | Pass: 1 test covering 120 cards / 12 islands at 768px, search, hide non-matches, panel fit, and bundle diagnostics export | G2 / G4 / G7 |
| Ops recovery guidance | bundled `node.exe .\node_modules\playwright\cli.js test e2e/ops_recovery_guidance.spec.ts --reporter=line` | Pass: 2 tests covering API load failure and save failure at 390px, recovery text, JSON preservation, safe diagnostic sharing, and status viewport fit | G4 / G6 / G7 |

### Findings and routing

- Resolved defect: `primary-flow` had `height: 0px`, so canvas content was visible through overflow while pointer hit-testing did not reliably reach polygon vertex handles. The fix gives the primary canvas flow a real height, renders polygon edit controls above cards, and gives the edit layer a non-zero hit-test area.
- Resolved keyboard focus gap: View controls now move focus into the dialog on open and restore focus to the trigger on Escape, matching Share dialog behavior.
- Resolved polygon keyboard gap: polygon vertex handles are focusable and support Arrow-key movement plus Delete/Backspace removal, with E2E export persistence evidence.
- Resolved E2E drift: affected Playwright specs now use shared bilingual label helpers for current Japanese/English UI labels, including share/export/read-only/visibility/polygon-edit actions.
- No ADR required: the change restores the existing interaction contract and does not alter product policy, public contract, or architecture.
- Remaining follow-up: slow worker/API delay evidence remains routed to `PRODUCT-UX-04` and `PRODUCT-OPS-01`.

### Gate classification delta

| Gate | 2026-05-22 delta | Reason |
| --- | --- | --- |
| G2 荳ｻ隕∵桃菴・| Go for covered frontend flows | full Playwright suite covers document replacement, visibility selection, read-only safety, bundle export, polygon vertex drag, and polygon vertex keyboard nudge/removal. |
| G3 譌･譛ｬ隱朸I | Go for covered frontend flows | stale English-only/mojibake expectations were centralized and updated in E2E helpers. |
| G4 逕ｻ髱｢閠先ｧ | Conditional Go | 390px/768px/920px/1280px/1440px header-panel fit, Share/View keyboard focus return, canvas hit-testing, synthetic large-document operability, and 390px API/save recovery status fit are now covered; slow-environment matrix remains open. |
| G7 蝗槫ｸｰ | Go for frontend scope | typecheck, targeted regression, full Vitest, and full Playwright pass. |

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している（未運用時は `N/A`）。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
