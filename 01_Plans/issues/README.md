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
5. 完了時は検証結果と `Status: Done` をmemoへ一度記録する。索引の手動更新は不要。

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

Active一覧は各memoの `Status` から生成する。READMEへ表を転記しない。

```powershell
python 01_Plans/triage_actionable_plans.py
```

`Draft / Open / In Progress` がActive、`Done` が完了である。特定領域だけを見る場合は、出力をBacklog ID、Priority、Scopeで絞り込む。

## 軽量ツール

- issue / docs変更の統一検証入口: `python 01_Plans/docs_check.py`（有効化済みruleだけをblocking実行し、未有効化ruleも表示）
- Active memo検証: `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`（README表ではなくmemoを直接走査）
- 検証ツールのテスト: `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- タスク候補の絞り込み: `python 01_Plans/triage_actionable_plans.py`

過去の同期ログ、件数、Decision Queue、RACI記録はGit履歴に残っている。現在の作業判断には使用しない。
