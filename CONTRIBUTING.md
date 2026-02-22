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

- **識別子（変数名・関数名・型名・ファイル名）は英語**で記述してください。
- ドキュメント・Issue・PR説明は日本語を基本として問題ありません。
- 上位階層（`00_`〜`02_`）と矛盾する仕様変更は、実装前にIssue/PRで合意してください。

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

## 初学者向けタスクのラベリング / "Good first issue" guidance

- 初めての貢献者向けに、着手しやすい Issue へ `good first issue` ラベルを付与します。
- 目安:
  - 変更範囲が限定的（1〜3ファイル程度）
  - 受け入れ条件が明確（完了定義を箇条書きで記載）
  - 背景知識が少なくても進められる（必要情報へのリンクがある）
- 記載テンプレート（最小）:
  - 背景 / 目的
  - 完了条件（Doneの定義）
  - 参考リンク（関連ドキュメント・関連Issue/PR）
- メンテナは、必要に応じて `help wanted` と併用して構いません。
