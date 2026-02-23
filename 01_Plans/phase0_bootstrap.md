# Phase 0 実装ブートストラップ

このドキュメントは、`01_Plans/roadmap.md` に定義された **Phase 0（プロジェクト骨格の確立）** を実行するための
**実装ブートストラップ手順書**です。

- 本リポジトリは **00〜04 の5階層構造を厳守**します
- `03_Implement` には **実装コードのみ** を配置します
- 本書は **人間および生成AI（Codex等）への作業指示書**です

---

## 1. Phase 0 の位置づけ

Phase 0 の目的は「機能を作ること」ではありません。

- 実装を安全に進められる **足場（scaffold）** を作る
- フロント・バックエンド・デプロイの
  - 起動
  - 接続
  - 最小疎通

を確認することがゴールです。

この段階では、**kj-atlas 固有の機能（KJ法・Canvas・AI）には踏み込みません**。

---

## 2. 完了条件（Definition of Done）

Phase 0 は、以下をすべて満たした時点で完了とします。

- [x] バックエンドが `uvicorn` で起動する
- [x] `GET /healthz` が HTTP 200 を返す
- [x] フロントエンドが `npm run dev` で起動する
- [x] ブラウザに kj-atlas の最小UI（ヘッダ等）が表示される
- [x] （任意）`docker compose up` で API + DB が起動する

### 2.1 進捗記入（2026-02-23 確認）

- 状態: **完了（Done）**
- 確認メモ:
  - backend の `/healthz` と docs API の回帰テストが通過。
  - frontend のテストスイートが通過し、Vite + React 基盤が継続運用されている。

---

## 3. 推奨ディレクトリ構成（Phase 0 時点）

```
/project-root
  ├── 00_Prompt/
  ├── 01_Plans/
  │   ├── roadmap.md
  │   └── phase0_bootstrap.md
  ├── 02_Architecture/
  ├── 03_Implement/
  │   ├── frontend/
  │   ├── backend/
  │   └── deploy/
  └── 04_Documentation/
```

---

## 4. Backend ブートストラップ

### 4.1 技術スタック（固定）

- Python
- FastAPI
- SQLAlchemy（まだDB接続は必須でない）

### 4.2 初期ファイル構成（案）

```
03_Implement/backend/
  ├── pyproject.toml
  ├── Dockerfile
  ├── src/
  │   └── kj_atlas_api/
  │       ├── __init__.py
  │       ├── main.py        # FastAPI app
  │       ├── settings.py    # 環境変数ロード
  │       └── health.py      # /healthz
  └── README.md
```

### 4.3 最小実装要件

- `FastAPI()` アプリケーションが起動すること
- `GET /healthz` が常に 200 を返すこと
- `DATABASE_URL` / `LLM_PROVIDER` を設定ファイル経由で読めること
- DB未接続でも起動できること

> **注意**：CRUD・ORM・マイグレーションは Phase 1 以降

---

## 5. Frontend ブートストラップ

### 5.1 技術スタック（固定）

- React
- Vite
- TypeScript

### 5.2 初期ファイル構成（案）

```
03_Implement/frontend/
  ├── package.json
  ├── vite.config.ts
  ├── tsconfig.json
  ├── index.html
  ├── src/
  │   ├── main.tsx
  │   ├── App.tsx
  │   └── ui/
  │       └── Shell.tsx
  └── Dockerfile
```

### 5.3 最小実装要件

- 画面に "kj-atlas" のタイトルが表示されること
- ローカル開発時に `GET /healthz` を叩けること（表示のみで可）

> **注意**：Canvas・カード・状態管理は Phase 1 以降

---

## 6. Deploy（任意・補助）

### 6.1 位置づけ

- Phase 0 では **必須ではない**
- ただし「どこでも動く」ことを担保するため、
  早期に雛形を置く価値は高い

### 6.2 対象

- Docker Compose（api + db）
- web は Phase 1 以降に統合してもよい

---

## 7. 作業の分割単位（AIに渡す順序）

Phase 0 は、以下の単位でAIに渡すことを推奨します。

1. backend 雛形（FastAPI / healthz / settings）
2. backend Dockerfile
3. frontend 雛形（Vite + React）
4. frontend healthz 疎通
5. （任意）docker-compose 雛形

---

## 8. やらないこと（明示）

Phase 0 では以下を **意図的に行いません**。

- DBスキーマ定義
- API CRUD 実装
- Canvas / KJ法ロジック
- AI / LLM 呼び出し
- テストの充実（空でよい）

---

## 9. 次フェーズへの引き継ぎ

Phase 0 完了後、次に進むのは **Phase 1（Canvas MVP）** です。

- 座標系（Transform）
- Card 表示（DOM）
- pan / zoom

はすべて Phase 1 で扱います。

本書は Phase 0 専用であり、
Phase 1 以降は新しい計画書を `01_Plans/` に追加します。
