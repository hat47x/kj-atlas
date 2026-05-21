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

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している（未運用時は `N/A`）。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
