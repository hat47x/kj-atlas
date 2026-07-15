# 01_Plans Issue Memo Index

- Status: Normative for the current issue-memo workflow and Active view
- Last verified: 2026-07-15 JST
- Upstream: `AGENTS.md`, `01_Plans/adr/ADR-0039-governance-right-sizing-personal-oss.md`
- Downstream: `01_Plans/triage_actionable_plans.py`, `01_Plans/issues/validate_active_issue_memos.py`, `CONTRIBUTING.md`

## Audience

Issueを選ぶMaintainer、Contributor、生成AI、および状態整合を確認するReviewerを対象とする。

## Goal

現在実行すべきActionの正本、着手順、必須メタ、Active集合を、過去の同期ログを読まずに判断できる状態にする。

## Non-goal

- 設計判断の本文を置くこと。Decisionの正本はADRとする。
- GitHub Issues運用を暗黙に開始すること。
- Done memoを自動削除すること。
- 過去のrerun件数や解消済みDecision Queueを現在の停止条件として再掲すること。

## Outcome

読者はこの文書から、Ready issueの抽出、対象memoの確認、作業開始、必要な検証まで進める。Active表はfilesystem上の `Draft / Open / In Progress` memoを漏れなく示す。

## Current operating decision

- **Action SSOT**: `01_Plans/issues/issue-*.md`
- **Decision SSOT**: `01_Plans/adr/ADR-*.md`
- **GitHub Issues**: 未運用。明示的な開始宣言までは内部issue memoを正本とする。
- **外部からの受付**: GitHub Discussions。MaintainerがAction化するときに内部issue memoへ変換する。
- **安全上の不変条件**: SafeMode既定ON、`provider=none`既定、proposal-only、`human_reviewed`の人手昇格、share/export境界を緩和しない。

## Fast path

1. Active全体ではなく、まずtriageを実行する。

   ```bash
   python 01_Plans/triage_actionable_plans.py
   ```

2. `Ready issues` に出たmemoと、そこから参照されるADRだけを読む。
3. `TEMPLATE.md` の受入条件と検証計画を満たしてから変更する。
4. 完了前に次を実行する。

   ```bash
   python 01_Plans/issues/validate_active_issue_memos.py
   python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py
   python -m unittest 01_Plans/tests/test_triage_actionable_plans.py
   ```

詳細な絞り込み規則は `../minimal-context-triage.md` を参照する。

## Lifecycle and status

正規ライフサイクルは `Draft -> Open -> In Progress -> Done` とする。

| Status | 意味 | 着手可否 |
|---|---|---|
| Draft | 受入条件、依存、責務のいずれかが未確定 | 着手しない |
| Open | 着手条件を満たし、未着手 | triage結果に従い着手可 |
| In Progress | 実作業または検証中 | 継続対象 |
| Done | 受入条件と必要検証を完了 | Active対象外 |

- Hold理由やOpen準備度は `Status` へ追記せず、`Execution`、`Open Readiness`、`Progress`、`Blockers` などの別メタへ記録する。
- Statusの更新責任は、`Draft -> Open` と `In Progress -> Done` がMaintainer、`Open -> In Progress` が実行担当とする。個人OSS運用ではMaintainerが兼務できるが、根拠と検証結果をmemoへ残す。

## Required metadata

Active memoは先頭メタに次を持つ。

- `Type`
- `Status`
- `Lifecycle`
- `Source Issue`
- `Priority`
- `Scope`
- `Related ADR/Spec`
- `Expected verification level`

`Expected verification level` は `docs-check / unit / integration / e2e` のいずれかとする。高いレベルは低いレベルの確認を含む。新規起票は `TEMPLATE.md` をコピーし、受入条件とValidation planを先に確定する。

## Source Issue policy

現行ではGitHub Issuesを正本としていないため、`Source Issue` は次のいずれかとする。

- 外部・上流の起点がない: `N/A`
- リポジトリ内の明示的な起点がある: そのmemo、research、Backlog IDなどの参照

GitHub Issue URLへの一括移行は、Maintainerが開始日時と対象範囲を宣言した場合だけ行う。その際はActive memoと本表を同じ変更で更新し、Status・Owner・受入条件を同時に変更しない。開始宣言がない限り、GitHub URLの欠如をblockerにしない。

## Active issue memos

2026-07-15 JST時点のfilesystem走査結果は **31件**（Draft 17 / Open 8 / In Progress 6）。表のStatusとSource Issueは各memoの先頭メタと一致させる。

| Backlog ID | Memo | Status | Source Issue |
|---|---|---|---|
| BUDGET-OPS-01 | `issue-BUDGET-OPS-01-budget-self-declaration-operationalization.md` | Draft | N/A |
| CARD-META-UI-01 | `issue-CARD-META-UI-01-card-provenance-metadata-ui-boundary.md` | Draft | N/A |
| CE1-CONTRACT-01 | `issue-CE1-CONTRACT-01-v1-keyset-and-envelope-reconciliation.md` | Open | `DOC-ARCH-02`（`CI-CE1-01`〜`CI-CE1-03` の異義定義を分離） |
| DATA-MAINT-04 | `issue-DATA-MAINT-04-metadata-only-audit-viewing.md` | Open | N/A |
| DATA-MODEL-OPS-02 | `issue-DATA-MODEL-OPS-02-management-plane-data-boundary.md` | Open | `01_Plans/research-2026-07-12-master-data-design-review.md`（maintainer 提示「マスタデータ管理UIの前にデータ設計の見直し」） |
| DOC-ARCH-02 | `issue-DOC-ARCH-02-current-contract-history-physical-separation.md` | In Progress | N/A |
| DOC-USER-JOURNEY-01 | `issue-DOC-USER-JOURNEY-01-first-meaningful-map-guide.md` | In Progress | N/A |
| DX-DOC-02 | `issue-DX-DOC-02-docs-contract-ci-and-index-completeness.md` | Draft | N/A |
| EXT-CONN-01 | `issue-EXT-CONN-01-readonly-mcp-server.md` | In Progress | N/A（`ADR-0054` 段階1） |
| EXT-CONN-02 | `issue-EXT-CONN-02-webhook-proposal-ingest.md` | Draft | N/A（`ADR-0054` 段階2） |
| EXT-CONN-03 | `issue-EXT-CONN-03-critique-constraint-export.md` | Draft | N/A（`ADR-0054` 段階3） |
| EXT-CONN-04 | `issue-EXT-CONN-04-evidence-trail-landing-view.md` | Draft | N/A（`ADR-0054` 役割B。Claude Design P32 先行相談 B-2 の回答で新設が確定） |
| GENAI-GOV-01 | `issue-GENAI-GOV-01-generative-ai-lane-boundary-and-readiness.md` | Draft | N/A |
| MVP-EXIT-01 | `issue-MVP-EXIT-01-productization-readiness.md` | Open | N/A |
| PRODUCT-QA-01 | `issue-PRODUCT-QA-01-release-readiness-quality-gates.md` | Open | N/A |
| PRODUCT-VALUE-01-SUMMARY | `issue-PRODUCT-VALUE-01-current-open-readiness-summary.md` | Open | `01_Plans/issues/issue-PRODUCT-VALUE-01-first-meaningful-map-activation.md`（Open 2026-06-20） |
| PRODUCT-VALUE-01 | `issue-PRODUCT-VALUE-01-first-meaningful-map-activation.md` | In Progress | N/A |
| PRODUCT-VALUE-02 | `issue-PRODUCT-VALUE-02-ambiguity-evidence-workflow.md` | In Progress | N/A |
| PRODUCT-VALUE-02-SUMMARY | `issue-PRODUCT-VALUE-02-current-open-readiness-summary.md` | Open | `01_Plans/issues/issue-PRODUCT-VALUE-02-ambiguity-evidence-workflow.md`（Open 2026-06-20） |
| PRODUCT-VALUE-03-SUMMARY | `issue-PRODUCT-VALUE-03-current-open-readiness-summary.md` | Open | `01_Plans/issues/issue-PRODUCT-VALUE-03-reviewable-outcome-package.md`（Open 2026-06-20） |
| PRODUCT-VALUE-03 | `issue-PRODUCT-VALUE-03-reviewable-outcome-package.md` | In Progress | N/A |
| QA-E2E-USE-01 | `issue-QA-E2E-USE-01-realistic-user-journey-expansion.md` | Draft | N/A |
| QA-PUB-01-I18N-03 | `issue-QA-PUB-01-I18N-03-e2e-boundary.md` | Draft | N/A |
| QA-UNIT-01 | `issue-QA-UNIT-01-unit-test-coverage-improvement.md` | Draft | N/A |
| SOCIAL-DIFFUSION-01 | `issue-SOCIAL-DIFFUSION-01-multi-reviewer-reproducibility.md` | Draft | N/A |
| SOCIAL-DIFFUSION-02 | `issue-SOCIAL-DIFFUSION-02-consensus-revisability-over-time.md` | Draft | N/A |
| SOCIAL-DIFFUSION-03 | `issue-SOCIAL-DIFFUSION-03-evidence-anchored-safe-diffusion.md` | Draft | N/A |
| SOCIAL-DIFFUSION-04 | `issue-SOCIAL-DIFFUSION-04-non-surveillance-adoption-signals.md` | Draft | N/A |
| VALUE-MEASURE-01 | `issue-VALUE-MEASURE-01-measurement-harness-and-evidence-artifacts.md` | Draft | N/A |
| VALUE-MEASURE-02 | `issue-VALUE-MEASURE-02-two-axis-value-governance-scorecard.md` | Draft | N/A |
| VR-ROADMAP-01 | `issue-VR-ROADMAP-01-value-to-social-goal-phase-baseline.md` | Draft | N/A |

## Keeping the Active view current

Statusを変更する変更では、memo本体とこの表を同時に更新する。

1. triageのActive件数を確認する。
2. 表のpath、Status、Source Issueをmemo先頭メタと照合する。
3. validatorとunit testを実行する。
4. `In Progress -> Done` では受入条件と検証結果をmemoへ記録してから表から除く。

現在のvalidatorは表からmemoへの整合を検証する。filesystemから表への逆向き完全性は `DX-DOC-02` でfail-closed化する。それまではtriage件数との一致を必須の手動照合とする。

## Completed and historical records

- Done memoは同じディレクトリに保持し、`Status: Done` で検索する。固定のCompleted表は、二重更新と陳腐化を避けるため維持しない。
- 反復同期ログ、過去件数、解消済みQueueはgit履歴から復元する。現在の実行判断へ持ち込まない。
- git履歴だけでは失われる一次証拠を別archiveへ移す場合は、`Informative`、対象期間、Retention reason、現行正本への逆リンクを必須とする。
- 人間判断が必要な場合は、対象memoの `DecisionQueueRef` を起点に `decision-pack-2026-03-human-judgement.md` を参照する。解消済み項目を再度blockerにしない。

## Review checklist

- [ ] Statusは正規値だけを使い、補足を同じ行へ混ぜていない。
- [ ] Active表とmemoのpath、Status、Source Issueが一致する。
- [ ] ScopeとNon-goalが変更範囲を限定している。
- [ ] Related ADR/Specが存在し、上流判断と矛盾しない。
- [ ] Acceptance criteriaとValidation planが具体的である。
- [ ] SafeMode、share/export、proposal-only、人手レビュー境界を緩和していない。
- [ ] 過去の同期ログや解消済みQueueをcurrent指示へ再混入させていない。
