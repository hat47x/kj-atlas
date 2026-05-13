# 04_Documentation

`04_Documentation` は、kj-atlas を導入・設定・運用する人のための公開ガイドです。内部の作業ログ、issue 管理、設計判断の詳細はこの階層には置かず、利用者が再現できる手順と判断基準だけを残します。

対象読者: kj-atlas を初めて使う人、検証環境を起動する人、日常運用や安全確認を担当する人。

読後にできること: 自分の目的に合う文書を選び、最初に読むべき順番と、困ったときの参照先を判断できます。

## はじめて読む人へ

kj-atlas の文書は、まず「安全に起動できること」、次に「どの情報を外部サービスと共有する可能性があるか」、最後に「変更後にどう確認するか」の順で読むと迷いにくくなります。すべてを一度に読む必要はありません。

| あなたの状況 | 読む順番 |
| --- | --- |
| とにかく動かしたい | [installation.md](installation.md) -> [configuration.md](configuration.md) |
| 運用担当になった | [installation.md](installation.md) -> [operations.md](operations.md) -> [security.md](security.md) |
| セキュリティ確認をしたい | [security.md](security.md) -> [security_operational_guidelines.md](security_operational_guidelines.md) -> [configuration.md](configuration.md) |
| データの保存先・共有範囲を確認したい | [data_handling.md](data_handling.md) -> [security.md](security.md) -> [configuration.md](configuration.md) |
| 変更後の確認をしたい | [e2e_testing.md](e2e_testing.md) -> [diagnostics.md](diagnostics.md) |
| AI 提案機能を使いたい | [ce2_low_risk_ai_assist.md](ce2_low_risk_ai_assist.md) -> [local_llm_ops_guide.md](local_llm_ops_guide.md) -> [security.md](security.md) |

迷った場合は、[installation.md](installation.md) と [configuration.md](configuration.md) から読んでください。起動できることと安全な既定値を先に確認すると、他の文書も読みやすくなります。

## 画面例を含む文書

画面操作を伴う文書には、標準サンプル `doc_phase1_canvas` を使ったスクリーンショットを掲載します。画像は `assets/screenshots/` に置き、UI が変わった場合は同じ文脈で撮り直します。秘密情報、API key、組織固有の承認履歴、顧客データを含む画面は使いません。

| 掲載先 | 画面例 | 読み取りポイント |
| --- | --- | --- |
| [installation.md](installation.md) | `app-canvas-overview.png` | 起動後に表示される標準画面、SafeMode、ヘッダー、キャンバス、右側パネル |
| [operations.md](operations.md) | `app-canvas-overview.png` | 運用確認で見る入口と、画面/API/保存確認の位置づけ |
| [data_handling.md](data_handling.md) | `share-export-safe-mode.png` | share/export 前に確認する SafeMode、visibility、reviewerRef、出力範囲 |
| [security.md](security.md) | `share-export-safe-mode.png` | SafeMode と外部サービスとの共有前に見る安全境界 |
| [e2e_testing.md](e2e_testing.md) | `view-controls-safe-mode.png`, `mobile-toolbar-smoke-390.png` | 手動 smoke test、表示設定、狭い viewport でのヘッダー確認 |
| [diagnostics.md](diagnostics.md) | `diagnostics-quality-report.png` | 診断 worker の実行結果、品質レポート、再現記録の入口 |

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
| 保存、外部サービスとの共有、export、share の判断 | [data_handling.md](data_handling.md) |
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

## Gist 公開の考え方

`04_Documentation` を Gist で公開するときは、読み手がリポジトリ構成を知らなくても追えるように、複数の Markdown を1つの公開用文書へまとめます。Gist は共有用の写しであり、正本はこのリポジトリの `04_Documentation` です。Gist だけを直接直さず、先にこの階層を更新してから公開用文書を作り直します。

公開用文書には次の情報を含めます。

- どの repository、branch、commit から作ったか。
- この README と、`04_Documentation` 直下の利用者向け Markdown。
- 画面例を読むためのスクリーンショット。画像は Gist 内へ再編集せず、固定 commit の `raw.githubusercontent.com` URL を使います。
- 画像やリンクが切れていないことを確認した手順。
- 秘密情報、API key、token、password、未加工の顧客情報を含めていないこと。

公開前には次の順に確認します。

```bash
git status --short
git rev-parse HEAD
rg -n "ghp_\\w+|github_pat_\\w+|AKIA[0-9A-Z]{16}|BEGIN [A-Z ]*PRIVATE KEY|password\\s*=|token\\s*=" 04_Documentation
rg -n "assets/screenshots/|\\.md\\)" 04_Documentation -g "*.md"
```

1つ目の検索は、公開対象に明らかな秘密情報の文字列が混ざっていないかを確認する簡易チェックです。文書上の用語説明として `token` や `password` を使う場合は、実値ではないことを確認します。2つ目の検索では、Gist 用に変換する画像リンクと文書リンクを洗い出します。

公開手順は次の通りです。

1. 変更を commit し、公開に使う commit hash を決める。
2. `04_Documentation` 直下の Markdown を公開用の1ファイルへ連結する。
3. `assets/screenshots/...` の画像リンクを、手順1の commit hash を含む raw GitHub URL に置き換える。
4. `04_Documentation` 内の相互リンクは、連結後の見出しへ置き換える。
5. `02_Architecture` など別階層へのリンクは、手順1の commit hash を含む GitHub の `blob` URL に置き換える。
6. 生成した Markdown を読み、画像リンク、見出し、コードブロック、公開範囲の説明を確認する。
7. public Gist として公開し、公開先 URL と元 commit hash を作業記録または PR に残す。

更新時も同じ手順を繰り返します。公開済み Gist を更新する場合は、前回の Gist URL を保ったまま内容を差し替え、元 commit hash も新しい値に更新します。

## 最小用語集

| 用語 | 意味 |
| --- | --- |
| Docker Compose | 複数のサービスをまとめて起動する仕組みです。kj-atlas では `web`、`api`、`db` をまとめて起動します。 |
| API | 画面と backend がやり取りする入口です。通常は `/api/...` で呼び出されます。 |
| SafeMode | 未レビュー情報の混入や外部サービスとの共有を避けるための安全側の動作です。 |
| LLM | 文章生成や要約を行う AI モデルです。kj-atlas では既定で無効です。 |
| provider | LLM の接続先種別です。`none`、`local`、`large-scale` などがあります。 |
| E2E | 画面から実際に操作して、利用者の流れ全体を確認するテストです。 |
| audit | 後から確認できるように残す操作記録です。秘密情報を含めないことが前提です。 |
| export | アプリ内の情報をファイルとして取り出す操作です。共有前に秘密情報や不要な identity 情報がないか確認します。 |
| share | 他の人が閲覧できるように共有する操作です。公開範囲、SafeMode、readOnly の状態を確認してから使います。 |
| visibility | 公開範囲の意図を示す分類です。SafeMode や readOnly の拒否結果を上書きするものではありません。 |
