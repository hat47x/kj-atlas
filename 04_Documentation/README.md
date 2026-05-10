# 04_Documentation

`04_Documentation` は、kj-atlas を導入・設定・運用する人のための公開ガイドです。内部の作業ログ、issue 管理、設計判断の詳細はこの階層には置かず、利用者が再現できる手順と判断基準だけを残します。

## まず読む文書

| 目的 | 文書 |
| --- | --- |
| 初回起動 | [installation.md](installation.md) |
| 環境変数と安全な既定値 | [configuration.md](configuration.md) |
| 日常運用、更新、バックアップ | [operations.md](operations.md) |
| セキュリティ境界と SafeMode | [security.md](security.md) |
| 受け入れ確認と E2E | [e2e_testing.md](e2e_testing.md) |
| リリース前確認 | [release.md](release.md) |

## 機能別リファレンス

| 領域 | 文書 |
| --- | --- |
| 診断 worker と障害調査 | [diagnostics.md](diagnostics.md) |
| ローカル LLM 運用 | [local_llm_ops_guide.md](local_llm_ops_guide.md) |
| AI 提案の扱い | [ce2_low_risk_ai_assist.md](ce2_low_risk_ai_assist.md) |
| ナラティブ生成とレビュー | [narratives.md](narratives.md) |
| 正規化と決定論的比較 | [canonicalization.md](canonicalization.md) |
| Codex skill の位置づけ | [codex_skill_operations.md](codex_skill_operations.md) |
| セキュリティ運用判断 | [security_operational_guidelines.md](security_operational_guidelines.md) |
| E2E 実施記録テンプレート | [e2e_verification_log_2026-03-03.md](e2e_verification_log_2026-03-03.md) |

## 文書品質のルール

- 1文書は、対象読者、目的、範囲外、完了状態を本文の冒頭で分かるようにします。
- コマンドはコピーして実行できる形で示します。
- 環境固有の秘密情報、社内 URL、承認履歴、生の監査ログは含めません。
- 実装・設計の正本をここで再定義しません。必要な場合は `02_Architecture` または `03_Implement` にリンクします。
- 内部作業ログは `01_Plans` 側で管理し、利用者向け文書には混在させません。
