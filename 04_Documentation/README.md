# 04_Documentation

`04_Documentation` は、kj-atlas を導入・設定・運用する人のための公開ガイドです。内部の作業ログ、issue 管理、設計判断の詳細はこの階層には置かず、利用者が再現できる手順と判断基準だけを残します。

対象読者: kj-atlas を初めて使う人、検証環境を起動する人、日常運用や安全確認を担当する人。

読後にできること: 自分の目的に合う文書を選び、最初に読むべき順番と、困ったときの参照先を判断できます。

## はじめて読む人へ

kj-atlas の文書は、まず「安全に起動できること」、次に「何を外部へ送る可能性があるか」、最後に「変更後にどう確認するか」の順で読むと迷いにくくなります。すべてを一度に読む必要はありません。

| あなたの状況 | 読む順番 |
| --- | --- |
| とにかく動かしたい | [installation.md](installation.md) -> [configuration.md](configuration.md) |
| 運用担当になった | [installation.md](installation.md) -> [operations.md](operations.md) -> [security.md](security.md) |
| セキュリティ確認をしたい | [security.md](security.md) -> [security_operational_guidelines.md](security_operational_guidelines.md) -> [configuration.md](configuration.md) |
| データの保存・外部送信・共有範囲を確認したい | [data_handling.md](data_handling.md) -> [security.md](security.md) -> [configuration.md](configuration.md) |
| 変更後の確認をしたい | [e2e_testing.md](e2e_testing.md) -> [diagnostics.md](diagnostics.md) |
| AI 提案機能を使いたい | [ce2_low_risk_ai_assist.md](ce2_low_risk_ai_assist.md) -> [local_llm_ops_guide.md](local_llm_ops_guide.md) -> [security.md](security.md) |

迷った場合は、[installation.md](installation.md) と [configuration.md](configuration.md) から読んでください。起動できることと安全な既定値を先に確認すると、他の文書も読みやすくなります。

## まず読む文書

| 目的 | 文書 |
| --- | --- |
| 初回起動 | [installation.md](installation.md) |
| 環境変数と安全な既定値 | [configuration.md](configuration.md) |
| データ取り扱いと共有前確認 | [data_handling.md](data_handling.md) |
| 日常運用、更新、バックアップ | [operations.md](operations.md) |
| セキュリティ境界と SafeMode | [security.md](security.md) |
| 受け入れ確認と E2E | [e2e_testing.md](e2e_testing.md) |
| リリース前確認 | [release.md](release.md) |

## 機能別リファレンス

| 領域 | 文書 |
| --- | --- |
| 診断 worker と障害調査 | [diagnostics.md](diagnostics.md) |
| 保存、外部送信、export、share の判断 | [data_handling.md](data_handling.md) |
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

文書を読んでいて、前提知識が必要すぎる、手順の成功条件が分からない、どの文書に進めばよいか分からない場合は、その文書自体を改善対象にします。

## 最小用語集

| 用語 | 意味 |
| --- | --- |
| Docker Compose | 複数のサービスをまとめて起動する仕組みです。kj-atlas では `web`、`api`、`db` をまとめて起動します。 |
| API | 画面と backend がやり取りする入口です。通常は `/api/...` で呼び出されます。 |
| SafeMode | 未レビュー情報の混入や外部送信を避けるための安全側の動作です。 |
| LLM | 文章生成や要約を行う AI モデルです。kj-atlas では既定で無効です。 |
| provider | LLM の接続先種別です。`none`、`local`、`large-scale` などがあります。 |
| E2E | 画面から実際に操作して、利用者の流れ全体を確認するテストです。 |
| audit | 後から確認できるように残す操作記録です。秘密情報を含めないことが前提です。 |
| export | アプリ内の情報をファイルとして外へ出す操作です。共有前に秘密情報や不要な identity 情報がないか確認します。 |
| share | 他の人が閲覧できるように共有する操作です。公開範囲、SafeMode、readOnly の状態を確認してから使います。 |
| visibility | 公開範囲の意図を示す分類です。SafeMode や readOnly の拒否結果を上書きするものではありません。 |
