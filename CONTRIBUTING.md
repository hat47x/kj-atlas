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

詳細規約は [`04_Documentation/coding_standards.md`](04_Documentation/coding_standards.md) を正本として参照してください。

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

## コミット規約（軽量） / Commit Convention

- 1コミット1目的を推奨します。
- 例: `docs: OSS公開向けポリシー文書を追加`
- 破壊的変更は本文に明記してください。

## 変更提案フロー / How to Propose Changes

1. まず Issue で背景・目的・影響範囲を共有
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
