# Issue Draft: PRODUCT-QA-01 製品化リリース準備の品質ゲート定義

- Type: Process
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: TBD
- Scope: `01_Plans/`, `03_Implement/frontend/`, `03_Implement/backend/`, `04_Documentation/`
- Related Backlog: `PRODUCT-QA-01`
- Related ADR/Spec: `01_Plans/issues/issue-MVP-EXIT-01-productization-readiness.md`, `01_Plans/issues/issue-QA-E2E-USE-01-realistic-user-journey-expansion.md`, `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`, `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: PRODUCT-QA-01
- RequirementStatement: MVP脱却時に必要な品質ゲートを、UI/UX、i18n、SafeMode、E2E、文書、リリース、診断の観点で定義し、リリース判断に使える状態にする。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=製品化候補のPRまたはリリース候補がある / 操作=品質ゲートを順に実行し、Go/No-Goを判定する / 期待結果=不足している検証、文書、画面設計課題が個別issueへ戻される / 除外=すべての将来機能の完了。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export / import-sanitize / public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: integration
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef（未確定時の参照先）: `MVP-EXIT-01`

## 1) 課題 / Problem statement

- MVP脱却には、単一のテスト合格だけでなく、画面、文書、安全境界、公開範囲、運用、診断を横断したGo/No-Go基準が必要である。
- 現行のissue群は個別課題を扱っているが、製品化リリース候補を判定する横断チェックリストが未整備である。
- 一般公開向け文書、開発者向けE2E、内部issue/ADR、実装テストの境界をそろえないと、公開時に説明と実装がずれる。

## 2) 背景 / Context

- `MVP-EXIT-01` は製品化準備の親issueとして存在する。
- `QA-E2E-USE-01` は実利用ケースのE2E拡充を定義している。
- `ADR-0031` は製品化UIの画面情報設計を提案している。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 製品化の価値は、利用者が継続的に安心して使える品質で初めて実現する。
- 安全（THREAT_MODEL / SafeMode）: SafeMode、取り込み、共有、公開文書はリリース前に必ず照合する必要がある。
- 企業・行政要件（enterprise_architecture）: 組織導入では検証記録、障害時対応、公開範囲説明が求められる。
- 後方互換（schemas）: リリース判定では既存データの読み込みと旧導線の到達性を確認する。

## 4) 提案する解決策 / Proposed solution

- 変更対象:
  - 製品化リリース準備チェックリスト。
  - CIまたは手動検証で確認するコマンド一覧。
  - E2Eユーザージャーニーと公開文書の照合。
  - SafeMode、share/export、import sanitize、public exposureのGo/No-Go基準。
- 変更の最小単位:
  - 既存issue群を参照するリリースゲートを `01_Plans` に定義する。
  - 必須ゲートと推奨ゲートを分ける。
- 非目標:
  - すべての品質改善を本Issueで実装すること。
  - 将来の認証・認可・共同編集をリリース必須にすること。

## 5) 受入条件 / Acceptance criteria

- [ ] 製品化リリース候補のGo/No-Go基準が、UI/UX、i18n、SafeMode、import/export、E2E、文書、診断で定義されている。
- [ ] 各ゲートに具体コマンド、手動確認、証跡の残し方がある。
- [ ] 未達の場合に戻す個別issueまたはADRが分かる。
- [ ] 公開文書と実装画面のスクリーンショットが一致していることを確認できる。
- [ ] 環境変数、SafeMode、共有、取り込み、公開範囲の説明が設計文書と矛盾しない。
- [ ] 既存データとレガシー導線の互換性確認が含まれる。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 製品化ゲートのカテゴリと必須/推奨を定義する。
- [ ] T2 既存issue/ADRをゲートに紐付ける。
- [ ] T3 自動テスト、手動Playwright確認、文書チェックの実行手順を定義する。
- [ ] T4 Go/No-Go判定の記録形式を定義する。
- [ ] T5 リリース前に不足した観点を個別issueへ戻す運用を決める。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `cd 03_Implement/frontend && node .\\node_modules\\typescript\\bin\\tsc --noEmit`
  - `cd 03_Implement/frontend && node .\\node_modules\\vitest\\vitest.mjs run src/i18n/ui_hardcode_guard.test.ts src/ui/i18n_equivalence.integration.test.ts`
  - `cd 03_Implement/frontend && node .\\node_modules\\playwright\\cli.js test --reporter=line`
  - `git diff --check`
- 期待結果:
  - 製品化リリース候補の品質ゲートを実行でき、未達項目が個別issueへ追跡できる。
- 未実施時の理由・代替検証:
  - 全E2Eが環境依存で実行できない場合は、対象scenario、失敗分類、再開条件を記録する。

## 8) 代替案 / Alternatives considered

- 代替案A: 既存CI合格のみをリリース判定にする。文書・操作性・公開範囲のずれを拾えない。
- 代替案B: すべての将来機能完了を製品化条件にする。範囲が広すぎてMVP脱却の現実的な判断ができない。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 品質ゲートが重すぎて、通常の改善PRが停滞する。
- 影響範囲: CI、E2E、リリース手順、公開文書。
- ロールバック手順: ゲートを必須/推奨へ再分類し、リリース阻害になっている項目を個別issueへ分離する。

## 10) Additional context

- ADR化が必要になる条件: リリース判定権限、公開配布方式、サポート範囲、公開配布のGo/No-Goをプロジェクト方針として固定する場合。

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
