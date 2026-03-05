# 全体アーキテクチャ


> 環境変数・実行パラメータの正本は `02_Architecture/runtime_parameter_registry.md`。本書では必要最小限のみ記載し、追加/改名時は正本を先に更新する。
このドキュメントは、kj-atlas の**全体アーキテクチャ（構成要素・責務境界・デプロイ形態）**を定義します。

- 上位層（README / 00_Prompt / 01_Plans）を前提とします
- ここでは思想や要件の追加はせず、**実装可能な構造**に落とします
- 最小MVPは Phase 0〜3 を主対象とします（AIは後付け可能な境界だけ先に定義）

---

## 1. アーキテクチャの目標

### 1.1 ポータビリティ（多様な環境で動く）

- インターネット上の一般環境
- 企業・行政のイントラネット
- 自前ホスティング（オンプレ／仮想マシン）

を想定し、**Docker（Compose）で完結する構成**を第一級に扱います。

### 1.2 低コストでのスモールスタート

- ローカルで完結した検証（SQLite）
- 小規模運用（PostgreSQL）

を自然に移行できるよう、DBは **SQLite ⇄ PostgreSQL** を切替可能にします。

### 1.3 将来のローカルLLM連携

- 外部API（OpenAI等）を前提にしない
- 社内サーバ上のLocal LLM（HTTP）を叩ける

ことを想定し、AI連携は **Provider抽象（設定で切替）** を採用します。

---

## 2. コンポーネント概要

kj-atlas は以下の3要素で構成します。

1. **Web（Frontend）**
2. **API（Backend）**
3. **DB（Persistence）**

将来、必要に応じて AI を別サービスとして分離できます。

---


## 2.5 採用技術スタック（正本）

本プロジェクトの実装スタックは以下を基準とする。

- Frontend: React 18 + Vite + TypeScript
- Backend: Python 3.10+ + FastAPI + SQLAlchemy + Alembic
- DB: SQLite（ローカル）/ PostgreSQL（推奨）
- E2E: Playwright
- 単体テスト: Vitest（Frontend）/ Pytest（Backend）

---

## 3. フロントエンド（Web）

### 3.1 技術

- React + Vite + TypeScript
- 描画：DOM（カード） + SVG（線・囲み等）
- 編集：キャンバス直編集は必須としない（選択 → 下部パネル／ポップアップ）

### 3.2 責務

- A型図解の表示（座標系、パン／ズーム、選択、（必要なら）ドラッグ）
- ドキュメントのロード／保存（API呼び出し）
- UI状態（選択・フィルタ・パネル開閉等）の管理

### 3.3 内部境界（重要）

フロント内部は、将来の差し替えを容易にするため、次の境界を明確にします。

- **Domain Model**（kj-atlasの意味構造：Card/Edge/Transform/Doc…）
- **Canvas Engine**（座標変換・ヒットテスト等の純TSロジック）
- **Renderer**（DOM+SVGの具体表現）

Reactは主に Renderer / UI Shell を担い、
Canvas Engine は React に依存しない純モジュールとして実装します。

---

## 4. バックエンド（API）

### 4.1 技術

- Python + FastAPI
- ORM：SQLAlchemy
- マイグレーション：Alembic

### 4.2 責務（MVP）

- ドキュメントCRUD（保存・取得）
- 最低限のバリデーション（スキーマ整合）
- 将来の認証・共有機能の受け皿

### 4.3 AI連携の責務（後付け）

MVPではAIを必須としません。
ただし将来のため、API側に以下の抽象を用意します。

- **LLMProvider**：設定で切替可能なLLM呼び出し層
- **AI Use Cases**：Draft生成／再配置提案／類似カード統合／画像生成（将来）

AI処理は同一サービスに実装しても良いし、
需要に応じて **別コンテナ（ai-service）** として分離しても良い構造にします。

---

## 5. 永続化（DB）

### 5.1 開発・検証

- SQLite（ローカルで完結）

### 5.2 本番・運用

- PostgreSQL（推奨）

### 5.3 切替方針

接続先は **設定ファイル／環境変数** で切替可能にします。

- `DATABASE_URL=sqlite+aiosqlite:///...`
- `DATABASE_URL=postgresql+asyncpg://...`

DB依存をAPI層の末端に隔離し、上位のユースケースはDB種別を意識しません。

---

## 6. APIのI/F方針（MVP）

### 6.1 保存単位

MVPでは差分同期ではなく、**ドキュメントのスナップショット保存**を基本とします。

- カード数が百数十程度であれば、実装とデバッグが簡単
- 将来必要になればパッチ（差分）を追加する

### 6.2 代表エンドポイント（例）

- `GET /docs/{doc_id}`
- `PUT /docs/{doc_id}`（スナップショット保存）
- `POST /docs`（新規）

認証・共有は後回し。

---

## 7. LLM連携（Provider抽象）

### 7.1 目的

- 外部API依存を前提にしない
- イントラ内のLocal LLMを利用可能にする

### 7.2 設計

`LLMProvider` は「どのLLMを叩くか」を隠蔽します。

- `NoOpProvider`（`none` / 既定・AI無効）
- `LocalProvider`（`local` / 社内LLM）
- `LargeScaleProvider`（`large-scale` / 任意の強モデル）

選択は環境変数で行います。

- `LLM_PROVIDER=none|fixture|local|external`
- `LOCAL_LLM_BASE_URL=...`（local時）
- `LOCAL_LLM_MODEL=...`（local時）
- `LLM_ESCALATION_ENABLED=false`（既定）

MVPでは Provider 抽象の枠だけ用意し、実装は最小でよい。

Provider列挙は信頼境界（none/fixture/local/external）で固定し、通信差異は `LLM_TRANSPORT`（in_process/ipc/http）で分離する。

---

## 8. デプロイ形態

### 8.1 最優先：Docker Compose（推奨）

- `web`：静的配信（Nginx等）
- `api`：FastAPI
- `db`：PostgreSQL

必要に応じて
- `ai`：AI専用サービス

を追加。

### 8.2 クラウドへの載せ替え

- Cloud Run / ECS / 低価格VM など

コンテナ境界を保つことで、運用先に依存しない。

---

## 9. セキュリティ・コンプライアンス（最小方針）

MVPでは高度な権限管理は後回し。
ただしイントラ利用を想定し、次を前提とします。

- 外部送信（LLM含む）は設定で無効化できる
- LLMの接続先は明示設定（デフォルトで外部へ送らない）
- strict mode例外承認フローは `strict_mode_exception_approval_flow.md` を正本とする

---

## 10. 非目標（MVPでやらない）

- 協調編集（CRDT等）
- 高度な権限管理（SSO等）
- 差分同期（リアルタイム）
- B型文章化（要約・説明文生成）
- 自動最適配置（正解クラスタ提示）

---

## 11. 公開/アクセス可視性メタデータ（FB-RM-PUB-01）

公開pack（`packs/index.json`）とview metadata（`view.json`）は、共通の `visibility` 列挙値を持つ。

- `"Public" | "Unlisted" | "Org" | "Restricted"`

互換性と安全性の原則:

- 旧 `view.json` で `visibility` 未設定時は `Restricted` として解釈する。
- 旧 `packs/index.json` で `visibility` 未設定時は `Public` として解釈する。
- `visibility` は表示/配布メタデータであり、MVP時点ではRBAC判定ロジックを担わない。
- SafeMode既定ONとshare/export漏えい防止ポリシーを優先し、`visibility` 導入で既存安全制御を弱めない。

## 12. AUTH-ARCH-01 境界（AuthContext / JIT / strict）

- 認証境界の正本は `ADR-0020` とし、実装契約は `schemas.md` / `api.md` / `review_attribution.md` を同一論点で同期する。
- `ALLOW_JIT_PROVISIONING=true` では未登録subjectをJITで `users` + `user_identities` 作成、`false` では `403` 拒否して事前プロビジョニング導線へ誘導する。
- attribution の正規キーは `users.id` で、外部subjectは `user_identities` でのみ解決する。
