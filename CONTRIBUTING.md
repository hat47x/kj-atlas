# Contributing Guide / コントリビューションガイド

この文書は、`kj-atlas` への変更提案・実装・レビューの最小ルールを定義します。

## リポジトリ構成 / Repository Structure

本リポジトリは階層化方針で運用します。

- `00_Prompt/`: 最上位の開発制約・用語定義
- `01_Plans/`: 実装計画
- `02_Architecture/`: 構造・インターフェース定義
- `03_Implement/`: 実装コード（frontend/backend/deploy）
- `04_Documentation/`: 利用者向けドキュメント

## ローカル実行 / Local Development

### 1) フルスタック（推奨）

```bash
cd 03_Implement/deploy
docker compose up --build
```

### 2) フロントエンド

```bash
cd 03_Implement/frontend
npm ci
npm run dev
```

### 3) バックエンド

```bash
cd 03_Implement/backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
export PYTHONPATH=src
alembic upgrade head
pytest
```

## コーディング規約 / Coding Conventions

詳細規約は [`01_Plans/coding_standards.md`](01_Plans/coding_standards.md) を正本として参照してください。

最低限の必須ルール:

- **識別子（変数名・関数名・型名・ファイル名）は英語**で記述する。
- 上位階層（`00_`〜`02_`）と矛盾する仕様変更は、実装前にIssue/PRで合意する。
- 1ファイル1責務を守り、重複ロジック・重複スタイルを増やさない。
- `except Exception` などの広域例外捕捉は原則禁止（期待例外を明示する）。
- SafeMode既定ONやshare/exportの安全既定を壊す変更は禁止。

## テスト方針 / Test Policy

- 差分に対するテスト追加・更新を原則とします。
- 特に以下の領域は回帰防止を重視します。
  - diff / merge
  - import（ZIP / markdown / schema validation）
- 既存テストを壊す変更は、意図と移行方針をPRに明記してください。
- `03_Implement/*` 変更時は、原則として `docker compose` によるE2E確認（`web + api + db`）を実施してください。
  - `docker compose up --build -d`
  - `docker compose ps`
  - `curl -fsS http://localhost:8080/api/health`
- Docker未導入の場合は、SQLite代替E2E（`backend:8000` + `frontend:4173`）を実施してください。
  - `curl -fsS http://localhost:8000/healthz`
  - `curl -fsS http://localhost:4173/api/healthz`
  - `PUT /docs/{doc_id}` と `GET /docs/{doc_id}` 往復確認
- それでもE2E実行不能な場合のみ、PR本文に「ブロッカー」「代替検証」「後続手順」を必ず記載してください。
- UI変更を含む場合は、原則として Playwright E2E テストの追加/更新（最低1ケース）を行ってください。



## Issue と ADR の使い分け（必須）

IssueとADRは混在させず、次の基準で分離して運用します。

### 目的の違い

- **Issue**: Action管理（What/How）。バグ修正・実装タスク・運用作業の進捗追跡。
- **ADR**: Decision & Context管理（Why）。重要な設計判断とトレードオフの記録。

### ADR化のトリガー（いずれかを満たす）

1. 複数案の比較（トレードオフ）がある。
2. 非機能要件（性能・セキュリティ・保守性・可用性）へ影響が大きい。
3. 将来参加メンバーに背景説明が必要な判断である。

### 連携フロー

- Issueで議論した結果、設計判断が必要になったらADRを起票して合意を固定する。
- ADRがAcceptedになったら、実装・検証・移行はIssueへ分解して管理する。
- ADR本文を進捗管理ボード代わりに使わない（進捗はIssueで管理）。


### GitHub Issue と `01_Plans` issue 記述の位置づけ

- 対外的な課題管理（公開トラッキング）は **GitHub Issues** を正本として運用します。
- `01_Plans` 配下の issue 記述は、AIエージェントが文脈を保持して再開しやすくするための補助メモであり、公開課題の正本ではありません。
- 正本判断が難しい論点は GitHub Issue で管理し、合意後に ADR とドキュメントへ反映してください。


## コミット規約（軽量） / Commit Convention

- 1コミット1目的を推奨します。
- 例: `docs: OSS公開向けポリシー文書を追加`
- 破壊的変更は本文に明記してください。

## 変更提案フロー / How to Propose Changes

1. まず **GitHub Issue** で背景・目的・影響範囲を共有
2. 合意後にブランチを作成して実装
3. Pull Request で変更理由・テスト結果・懸念点を提示

小さな typo 修正などは、Issue なしで直接 PR して構いません。

## ラベル運用ガイド / Labeling guidance

### 標準ラベル

- `bug`: 不具合・回帰
- `enhancement`: 機能改善・機能追加
- `good first issue`: 初回貢献に適した小さく明確な課題
- `help wanted`: 担当者を広く募集したい課題
- `security`: セキュリティ関連（詳細は `SECURITY.md` 優先）
- `docs`: ドキュメント修正・追記

### `good first issue` の付与目安

- 変更範囲が限定的（目安: 1〜3ファイル）
- 完了条件が箇条書きで明確
- 前提知識が少なくても着手可能（参考リンクあり）
- ローカルで再現・確認しやすい

### メンテナのトリアージ方針（簡易）

1. 新規 Issue を `bug` / `enhancement` / `docs` のいずれかに一次分類
2. 初学者向け条件を満たすものへ `good first issue` を追加
3. 担当募集が必要なものへ `help wanted` を追加
4. セキュリティ懸念は `security` を付与し、詳細取り扱いは `SECURITY.md` に誘導


### E2Eドキュメント整合ルール

- E2E手順の正本は `04_Documentation/e2e_testing.md` です。
- E2Eのコマンド・受入基準・代替経路（Docker未導入時）を変更する場合は、同一PRで `04_Documentation/installation.md` と `04_Documentation/operations.md` も同期更新してください。
- 不足・不整合を見つけたら「あるべき状態」を先に明文化し、正本へ合わせて同期してください。正本判断が難しい場合はIssueを起票して管理してください。
- PR本文には、更新したE2E関連文書の一覧を記載してください。
