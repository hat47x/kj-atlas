# Release

対象読者: kj-atlas のリリース、検証版配布、公開前確認を担当する人。

目的: リリース前に確認する品質、安全性、文書、受け入れ確認の最小手順と、タグ push 後に `.github/workflows/release.yml` が実際に生成する成果物の契約をまとめます。

範囲外: 組織固有の承認システム、配布先ごとの秘密設定、マーケティング告知、container/package registry・自動 deploy・署名基盤の新設。

公開区分: リリース/04文書保守者向け管理文書。一般利用者向け Gist の本文には原則含めず、公開前確認と安全境界レビューのチェックリストとして使います。

## 前提: 検証用タグビルドであり、正式配布ではない

`.github/workflows/release.yml` が `vX.Y.Z` タグの push で作る成果物は、**検証用ビルド**です。container/package registry への公開、GitHub Release の作成、installer や source archive の生成は行いません。この境界を利用者・運用者へ案内するときに、一般公開済みの配布物と混同しないでください。継続的な公開配布を始める場合は、公開channel、artifact構成、保持期間、checksum/provenance/SBOM/署名、backend imageのregistry、撤回方法を別Issueまたは ADR で判断します（現時点では未実施）。

## リリース前チェック

```bash
git status -sb
git diff --check
```

この文書でいうリリースは、利用者が触れる状態へ変更を出すことです。正式版だけでなく、検証版や社内配布でも同じ考え方を使います。

## 前提知識

リリース担当者は、すべての実装詳細を理解している必要はありません。ただし、次の違いは確認できるようにしておきます。

| 用語 | 意味 |
| --- | --- |
| build | 利用者が実行できる形に frontend などを組み立てること |
| test | 期待した動作を機械的に確認すること |
| smoke test | 主要操作だけを短時間で手動確認すること |
| rollback | 問題が出たときに前の状態へ戻すこと |

## リリース判断の流れ

`release.yml` は frontend test、backend test、docs check、E2E を再実行しません。次のコマンドは、タグを打つ**前**に、タグ対象にする予定のcommit SHAに対して自分で実行し、結果をリリース記録に残します。

1. 差分の範囲を確認する。
2. 影響するテストを実行する（下記コマンド）。
3. 手動 smoke test で利用者の主要操作を確認する。
4. security / SafeMode / 外部サービスとの共有の安全境界が後退していないことを確認する。
5. data handling の観点で export、share、ログ、外部サービスとの共有の扱いを確認する。
6. `01_Plans/issues/done/issue-PRODUCT-QA-01-release-readiness-quality-gates.md` のG0〜G7と価値ゲートに未解消のBlockerがないことを確認する。
7. rollback 方針を確認する。

frontend:

```bash
cd 03_Implement/frontend
npm ci
npm run typecheck
npm run test
npm run build
```

backend:

```bash
cd 03_Implement/backend
python -m pytest
```

Docker Compose:

```bash
cd 03_Implement/deploy
docker compose up --build -d
curl -fsS http://localhost:8080/api/healthz
```

## タグ作成手順

1. 上記「リリース判断の流れ」を対象commit SHAに対して実行し、全て成功することを確認する。失敗する場合はタグを作らない。
2. `CHANGELOG.md` の `[Unreleased]` を、タグと同じバージョン番号・当日日付の見出しへ切り出す（下記「CHANGELOG との対応」参照）。
3. タグ名は SemVer 形式 `vX.Y.Z` とし、対象は手順1で確認済みのcommit SHAに限る。
4. 一度作成したタグは強制更新（force push / re-tag）しない。誤りがあった場合は新しいバージョン番号で再実行し、誤ったタグは withdrawn として記録する。
5. タグを push し、`.github/workflows/release.yml` の実行結果（成功/失敗）を確認する。
6. 下記「リリース記録に残す項目」を記録する。

## workflow が生成する成果物（現行契約）

`.github/workflows/release.yml` は `vX.Y.Z` タグの push で起動し、次の2つのjobだけを実行します。

| Job | 生成物 | 配布するか |
| --- | --- | --- |
| `backend-docker-build` | `kj-atlas-api:<tag>` という名前のDocker image（ローカルbuildのみ） | しない。`push: false`。registry送信もimage archiveの保存もない。build自体が壊れていないことの検証だけが目的。 |
| `frontend-build` | `frontend-dist-<tag>` という名前のGitHub Actions artifact（`03_Implement/frontend/dist`の内容） | GitHub Actionsの当該workflow run画面からのみ取得可能。保持期間はリポジトリ/組織のActions設定（Settings → Actions → General → Artifact and log retention）に従う。設定を変更していない限りGitHubの既定値が適用される。期限切れ後は同じcommitから再buildしない限り取得できない。 |

上記いずれも、checksum、provenance、SBOM、署名は生成しません。取得したartifactの完全性を保証する追加の仕組みは現時点でありません。

対象tag/SHAの取得場所は、GitHubリポジトリの Actions タブから `Release Build` workflowの該当run（tag pushで起動したrun）を開き、そのrunのartifact一覧から確認します。

## CHANGELOG との対応

`CHANGELOG.md` は [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/) 形式・SemVer準拠です。`[Unreleased]` から版を切る条件は次のとおりです。

- タグを作成する直前に、`[Unreleased]` の内容を `## [X.Y.Z] - YYYY-MM-DD`（タグと同じバージョン番号、当日日付）へ書き換える。
- 新しい空の `[Unreleased]` セクションを見出しだけ残す。
- `[Unreleased]` のまま tag を push しない。版とタグは1:1で対応させる。

## リリース記録に残す項目

- tag（`vX.Y.Z`）
- 対象 commit SHA
- CI run（「リリース判断の流れ」を実行したCIまたはローカル実行の記録）
- release workflow run（`.github/workflows/release.yml` の実行URL）
- gate decision（`PRODUCT-QA-01` のGo/No-Go判断）
- artifact（`frontend-dist-<tag>` の取得場所）
- 保持境界（Actions artifactの失効予定）
- 既知の制限
- rollback / withdrawal 方針

## 手動確認

- [ ] アプリが開く。
- [ ] 新規ドキュメントを作成できる。
- [ ] カードを追加・移動できる。
- [ ] 保存して再読み込みしても内容が残る。
- [ ] share/export に秘密情報や内部作業ログが含まれない。
- [ ] SafeMode の既定動作が緩んでいない。
- [ ] LLM provider が意図した値になっている。
- [ ] 監査ログの HTTP 連携や外部アクセス制御を有効にした場合、連携先と失敗時の動作が説明できる。

## 文書確認

- [ ] [installation.md](installation.md) の起動手順が現行実装と合っている。
- [ ] [configuration.md](configuration.md) の環境変数が `settings.py` と矛盾していない。
- [ ] [data_handling.md](data_handling.md) の保存・外部サービスとの共有・共有前確認が現行実装と矛盾していない。
- [ ] [security.md](security.md) の外部サービスとの共有の境界が維持されている。
- [ ] [acceptance_check.md](acceptance_check.md) の確認手順が再現できる。
- [ ] README や 04 文書に内部 issue 記録や秘密情報が混ざっていない。

## 失敗時の扱い

次のいずれかに当てはまる場合、リリースを止めます。

- build、test、typecheck の失敗理由が説明できない。
- SafeMode、share/export、LLM provider の安全境界が後退している。
- 秘密情報、内部 URL、生の顧客情報が文書や export に混ざっている。
- 受け入れ確認の主要操作が再現できない。

止めることは失敗ではありません。利用者に影響する不確実性を見つけた状態なので、原因、回避策、再開条件を記録してから次の確認に進みます。誤って作成したタグは強制更新せず、withdrawn として記録し、新しいバージョン番号で再実行します。

## 関連文書

- [acceptance_check.md](acceptance_check.md)
- [data_handling.md](data_handling.md)
- [operations.md](operations.md)
- [security.md](security.md)
- [installation.md](installation.md)

2026-03-03時点のE2E検証ログ（形成履歴）はGit履歴から参照します。現在のリリース判断の証跡としては、対象commit SHAに対して都度実行した確認結果を使います。
