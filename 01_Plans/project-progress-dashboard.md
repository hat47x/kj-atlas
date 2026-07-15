# Project Status

> Status: Retired as a manually synchronized dashboard on 2026-07-15.

個人OSS・プレリリース段階では、手書きの件数、Decision Queue、rerunログを維持しない。これらは実態からずれやすく、生成AIの通常コンテキストを圧迫するため、`ADR-0039` と `OPS-LEAN-01` に基づいて廃止した。

## 現在の確認先

| 確認したいこと | 参照先 |
|---|---|
| 実行中の内部タスク | `01_Plans/issues/README.md` と対象issue memo |
| 機械的なタスク候補 | `python 01_Plans/triage_actionable_plans.py` |
| 長期的な設計判断 | 対象の `01_Plans/adr/ADR-*.md` |
| 公開ロードマップ | `ROADMAP.md` |
| 実装済み状態 | 対象コード、テスト、Git履歴 |
| CI状態 | 対象PRのGitHub Actions |

## 運用ルール

- このファイルへActive件数、完了件数、rerun番号、Stream、テスト件数を追記しない。
- 状態変更は対象issue memoだけに記録する。
- 同じ情報を複数文書で集計しない。
- 過去のdashboard内容が必要な場合は、2026-07-15以前のGit履歴を参照する。

複数メンテナや実ユーザーが増え、横断ダッシュボードが必要になった場合は、手書きではなくissueメタデータから生成する。
