# Issue Draft: PROJECT-CI-01 GitHub Actions checkout/auth blocker

- Type: Bug
- Status: Done
- Source Issue: N/A
- Priority: P0
- Owner: TBD
- Scope: `.github/workflows/`, GitHub repository/account operations
- Related Backlog: `PROJECT-CI-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0034-mainline-convergence-and-branch-hygiene.md`, `01_Plans/issues/done/issue-PRODUCT-QA-01-release-readiness-quality-gates.md`, `01_Plans/issues/done/issue-PROJECT-BASELINE-01-latest-mainline-health-baseline.md`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: PROJECT-CI-01
- RequirementStatement: GitHub Actions が pull request の merge ref を checkout できず、CI がコード実行前に失敗する状態を解消する。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=PR 上で GitHub Actions CI が実行される / 操作=Actions が `actions/checkout` で PR merge ref を取得する / 期待結果=checkout が成功し、frontend/backend の各 job が実テストへ進む / 除外=本Issueでアプリケーション実装、SafeMode方針、リリース判定権限を変更すること。
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: public-exposure

## 1) 課題 / Problem statement

- PR #2271 の GitHub Actions `CI` run #9141 で、複数 job が `actions/checkout@v4` の段階で失敗した。
- 失敗ログには GitHub から `Your account is suspended. Please visit https://support.github.com for more information.` が返り、`git fetch` が 403 で終了している。
- checkout 前に失敗しているため、CI は frontend/backend の実テスト結果を返せず、製品化ゲートの G7 回帰証跡として利用できない。
- その後の同一PR最新コミット `5fd1a304dc0577678b3d2afe4ed18642512e4286` に対する CI run #9143 は checkout を含む全 job が成功したため、本件は継続ブロッカーではなく一時的な repository/account operation incident としてクローズする。

## 2) 背景 / Context

- `PRODUCT-QA-01` は release readiness の必須入力として CI / local command evidence を要求している。
- `PROJECT-BASELINE-01` は candidate 単位の健康状態を記録するが、CI が checkout で止まる場合は、コードの成否ではなく repository/account operations のブロッカーとして切り分ける必要がある。
- ローカルでは 2026-05-26 に frontend typecheck、full Vitest、backend pytest、Playwright E2E、production build、WSL2 Compose config が通っている。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: CI がPRごとに実行できないと、利用者に渡す前の判断証跡が再現できない。
- 安全（THREAT_MODEL / SafeMode）: SafeMode/share-export 回帰があっても CI で検出できない状態は、公開前検査の信頼性を下げる。
- 企業・行政要件（enterprise_architecture）: 組織導入では、変更候補ごとの自動検証結果と失敗理由を説明できる必要がある。
- 後方互換（schemas）: 直接のスキーマ影響はないが、schema/backend/frontend 回帰検知の入口が止まる。

## 4) 提案する解決策 / Proposed solution

- 変更対象:
  - GitHub repository/account operations.
  - 必要に応じて `.github/workflows/ci.yml` の checkout/auth 前提。
- 変更の最小単位:
  - repository/account owner が GitHub account suspension / token / repository access state を確認し、PR merge ref checkout が成功する状態へ戻す。
  - その後、失敗した CI run を re-run する。
- 非目標:
  - CI provider の変更。
  - checkout token 権限を広げる設計変更。
  - アプリケーションコードや文書正本の方針変更。

## 5) 受入条件 / Acceptance criteria

- [x] PR の GitHub Actions が `actions/checkout@v4` で 403 にならない。
- [x] `Frontend typecheck`, `Frontend test + build`, `Backend lint + test`, i18n/regression guard jobs が checkout 後の実ステップまで進む。
- [x] 失敗が残る場合は、checkout/auth ではなく具体的な test/build failure として分類できる。
- [x] `PRODUCT-QA-01` の G7 回帰証跡として、CI run の成功またはテスト由来の失敗を参照できる。
- [x] 必要な検証（integration）が `Expected verification level` と一致する。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 GitHub account/repository owner が suspension / repository permission / token state を確認する。後続 run #9143 の checkout 成功をもって、少なくともPR実行経路の復旧を確認した。
- [x] T2 CI run #9141 または後続 run を re-run し、checkout が成功するか確認する。
- [x] T3 checkout 成功後に残る test/build failure があれば、通常の CI failure として別issueまたは当該PRで処理する。run #9143 では残存失敗なし。
- [x] T4 `PRODUCT-QA-01` と `PROJECT-BASELINE-01` の release gate record へ、CI復旧後の結果を追記する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - GitHub Actions CI rerun
  - `git fetch` / `actions/checkout@v4` step log confirmation
- 期待結果:
  - checkout が成功し、CI が実テストへ進む。
- 実施結果:
  - GitHub Actions CI run #9143 が `actions/checkout@v4`、frontend i18n guard、frontend typecheck、frontend test/build、frontend lint、frontend regression guards、backend lint/test をすべて成功させた。
  - run #9141 の checkout 403 は継続再現していない。再発時は本Issueを再オープンする。

## 8) 代替案 / Alternatives considered

- 代替案A: ローカル検証だけでCI必須ゲートを代替する。却下理由: release readiness の再現性が不足する。
- 代替案B: checkout を別の認証方式に変更する。却下理由: まず account/repository 状態の確認が必要で、設計変更は過剰。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: suspension / permission 問題をアプリケーション回帰と誤分類し、不要なコード修正を行う。
- 影響範囲: すべてのPR CI、release readiness gate、mainline convergence。
- ロールバック手順: workflow 変更を行った場合は revert 可能にする。ただし account suspension 解除はGitHub account ownerの管理操作であり、リポジトリ差分では戻せない。

## 10) Additional context

- Evidence:
  - PR #2271 CI run #9141
  - Failed step: `actions/checkout@v4`
  - Error class: GitHub 403 before repository checkout
  - PR #2271 CI run #9143
  - Resolution evidence: all jobs succeeded after checkout, including frontend/backend test jobs.
- ADR化が必要になる条件:
  - CI provider を変更する場合。
  - checkout credential / token 権限モデルをプロジェクト方針として変更する場合。
  - release gate で GitHub Actions CI を必須から任意へ下げる場合。

---
