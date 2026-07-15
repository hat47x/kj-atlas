# Issue Memo Index

このディレクトリは、現在の実行タスクを内部issue memoとして管理する。GitHub Issuesは未運用であり、`Source Issue: N/A` を使用する。

## 運用原則

- Actionはissue memo、長期的なDecisionはADR、実行履歴はGitとPRを正本とする。
- 現段階では `ADR-0039` を適用し、Maintainerが起票、実行、完了判断を担う。
- 同じ進捗をdashboard、decision-pack、READMEへ転記しない。
- rerun番号、Stream、固定5フェーズ、RACI通知、仮想役職、手動件数同期は使用しない。
- Done memoは通常のAIコンテキストへ入れず、履歴確認が必要な場合だけ検索する。
- GitHub Issues運用を将来開始する場合は、その時点で必要な移行手順を新たに決める。未使用の移行runbookは維持しない。

## 起票方法

1. `TEMPLATE.md` を使い、課題、対応方針、受入条件、検証計画を短く記載する。
2. `Status` は `Draft -> Open -> In Progress -> Done` の順で更新する。
3. `Expected verification level` は変更リスクに応じて `docs-check / unit / integration / e2e` から選ぶ。
4. ADRは長期的、横断的、破壊的、または安全境界を変える判断に限る。
5. 完了時は検証結果をmemoへ一度記録し、Active表から除く。

## 必須メタデータ

- `Type`
- `Status`
- `Lifecycle`
- `Source Issue`
- `Priority`
- `Scope`
- `Related ADR/Spec`
- `Expected verification level`

## Active issue memos

> この表は人間向けの短い索引である。状態の正本は各memoとGit履歴。表とfilesystemの完全一致検査は `DX-DOC-02`、既存Active memoの整理は `DOC-OPS-06` で扱う。

| Backlog ID | Memo | Status | Source Issue |
|---|---|---|---|
| DOC-USER-JOURNEY-01 | `issue-DOC-USER-JOURNEY-01-first-meaningful-map-guide.md` | In Progress | N/A |
| DOC-ARCH-02 | `issue-DOC-ARCH-02-current-contract-history-physical-separation.md` | In Progress | N/A |
| DOC-OPS-06 | `issue-DOC-OPS-06-current-view-history-and-contributor-route.md` | In Progress | N/A |
| DX-DOC-02 | `issue-DX-DOC-02-docs-contract-ci-and-index-completeness.md` | Draft | N/A |
| DOMAIN-CARD-QUALITY-01 | `issue-DOMAIN-CARD-QUALITY-01-qualitative-card-quality-assistance.md` | In Progress | N/A |
| DOMAIN-W-ITERATION-01 | `issue-DOMAIN-W-ITERATION-01-w-type-cumulative-inquiry-support.md` | In Progress | N/A |
| OPS-LEAN-01 | `issue-OPS-LEAN-01-small-oss-operations-reduction.md` | In Progress | N/A |

## 軽量ツール

- Active memo検証: `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 検証ツールのテスト: `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- タスク候補の絞り込み: `python 01_Plans/triage_actionable_plans.py`

過去の同期ログ、件数、Decision Queue、RACI記録はGit履歴に残っている。現在の作業判断には使用しない。
