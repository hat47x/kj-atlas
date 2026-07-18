# 全体アーキテクチャ


> 環境変数・実行パラメータの正本は `02_Architecture/runtime_parameter_registry.md`。本書では必要最小限のみ記載し、追加/改名時は正本を先に更新する。
このドキュメントは、kj-atlas の**全体アーキテクチャ（構成要素・責務境界・デプロイ形態）**を定義します。

- 上位層（README / 00_Prompt / 01_Plans）を前提とします
- ここでは思想や要件の追加はせず、**実装可能な構造**に落とします
- 最小MVPは Phase 0〜3 を主対象とします（AIは後付け可能な境界だけ先に定義）

価値判断と設計要素の対応は [value_traceability.md](value_traceability.md) を参照します。本書で新しい思想や要件を直接追加せず、上流文書で定義された価値を実装可能な責務境界へ落とします。
`02_Architecture` 内の現行契約と履歴ログの読み分けは [contract_reading_guide.md](contract_reading_guide.md) を参照します。
本書から分離したCE0/CE1 freeze形成記録は [Architecture contract-freeze formation history](history/architecture-contract-freeze-formation-2026-04-to-05.md) に保持します。
MVPで運用サポートするデータ構造、埋め込み限定の構造、契約のみの構造は [data_model_operations_overview.md](data_model_operations_overview.md) を参照します。

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

### 1.4 プロダクト価値実現の責務境界

製品化では、単に機能が存在するだけでなく、利用者が価値を受け取る流れを構造として支える必要があります。
価値実現ループの正本は `02_Architecture/value_traceability.md` と `01_Plans/adr/ADR-0032-product-value-realization-model.md` とし、本書では責務境界だけを固定します。

- Frontend は、開始、カード化、保留/違和感の記録、選択コンテキスト、共有前確認を利用者の主要導線として扱う。
- Backend は、保存、検証、ContextBundle、proposal、監査イベントを扱うが、AI提案の自動確定や `human_reviewed` 自動昇格を行わない。
- DB は、作業状態、表示状態、レビュー状態、共有用メタデータを破壊的に混在させず、共有時に削除・抑制できる境界を維持する。
- AI連携は任意機能であり、`KJ_ATLAS_LLM_PROVIDER=none` の既定構成でも、開始、外在化、構造化、共有前確認の主要価値が成立する。
- 共有/export は単なるファイル出力ではなく、確定点、保留点、未レビュー情報、根拠への戻り方を安全に伝える成果物化の責務を持つ。

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
- **AI Use Cases**：Draft生成／再配置提案／類似カード統合／代表視覚手掛かりの候補生成（将来）

代表視覚手掛かりは生成AIだけに依存しません。通信不要の絵文字・同梱プリセット、権利確認済み外部素材、proposal-only画像生成を別経路とし、意味境界と段階導入は `00_Prompt/representative_visual_cue_requirements.md`、供給・保存の判断は `ADR-0059` を参照します。現行MVPに画像生成APIまたは永続契約が実装済みであることを示すものではありません。

AI処理は同一サービスに実装しても良いし、
需要に応じて **別コンテナ（ai-service）** として分離しても良い構造にします。

---

## 5. 永続化（DB）

MVPの永続化は、細かい論理エンティティを全て正規化する設計ではありません。ドキュメント本体はスナップショットとして保存し、補助ログや認証主体の対応表だけを別テーブルで扱います。物理ER、論理ER、CRUD可否、ステークホルダー別の保守責任は [data_model_operations_overview.md](data_model_operations_overview.md) を正本として参照します。

### 5.1 開発・検証

- SQLite（ローカルで完結）

### 5.2 本番・運用

- PostgreSQL（推奨）

### 5.3 切替方針

接続先は **設定ファイル／環境変数** で切替可能にします。

- `KJ_ATLAS_DATABASE_URL=sqlite+aiosqlite:///...`
- `KJ_ATLAS_DATABASE_URL=postgresql+asyncpg://...`

DB依存をAPI層の末端に隔離し、上位のユースケースはDB種別を意識しません。

---

## 6. APIのI/F方針（MVP）

### 6.1 保存単位

MVPでは差分同期ではなく、**ドキュメントのスナップショット保存**を基本とします。

- カード数が百数十程度であれば、実装とデバッグが簡単
- 将来必要になればパッチ（差分）を追加する

### 6.2 代表エンドポイント（例）

- `GET /docs/{doc_id}`
- `PUT /docs/{doc_id}`（スナップショット保存。現行MVPでは存在しないIDへのPUTを作成として扱う）
- `POST /docs`（サーバ採番の新規作成候補。MVP必須ではなく、実装契約化は `DATA-CONTRACT-01` で扱う）

認証・共有の詳細は、文書保存APIとは分けて `enterprise_architecture.md`、`review_attribution.md`、share/export関連仕様で扱う。

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

- `KJ_ATLAS_LLM_PROVIDER=none|local|local_http|large-scale|large_scale|external`
- `KJ_ATLAS_LOCAL_LLM_BASE_URL=...`（local時）
- `KJ_ATLAS_LOCAL_LLM_MODEL=...`（local時）
- `KJ_ATLAS_LLM_ESCALATION_ENABLED=false`（既定）

MVPでは Provider 抽象の枠だけ用意し、実装は最小でよい。

Provider列挙は信頼境界（none/fixture/local/external）で固定し、通信差異は環境変数ではなく内部の transport 抽象（in_process/ipc/http）で分離する。

## 7A. CE-0 責務・信頼境界（Consensus/Working Repositioning）

CEフェーズ開始時点の最小契約として、Graph責務・I/O・禁止事項を次で固定する（**責務境界のみを対象**。API/CLI/UI の実装詳細はCE-1以降）。

### 7A.0 Contract Definition Check（CDC）固定

- CE0/CE1の Contract ID は参照専用固定値として扱い、再採番・異義定義を禁止する。
- CE1/CE2/CE4 は mock I/F を前提に依存待機せず検証を継続する。
- 本章の契約は責務境界のみを扱い、推測で実装要件（API詳細/CLI/UI具体）を追加しない。
- CE0入力snapshotの識別子と当時のfreeze運用は[形成履歴](history/architecture-contract-freeze-formation-2026-04-to-05.md#former-7a0-input-contract-snapshot-固定ce0)へ分離する。現行の責務境界は§7A.1〜§7A.4を正とする。


### 7A.1 責務境界（CE0-CTX-IF / CE0-SAFEMODE-IF / CE0-REVIEW-IF / CG-01..05）

- `WorkingGraph`: 主体（human/agent/role）ごとの探索・未確定保持を担う作業面。
- `ContextProjectionGraph`: 問い合わせ目的へ投影する読取専用面。ContextBundle生成にのみ使用。
- `Consensus Graph`（実装上の識別子: `ConsensusGraph`, 旧Core Graph）: `patch + approval` 済み差分のみを保持する統合面。

| Contract ID | Responsibility boundary |
| --- | --- |
| `CE0-CTX-IF` | ContextQuery / ContextBundleの安全境界、Query Preview必須経路、決定論的bundle生成。具体的なキーは`schemas.md`を参照 |
| `CE0-SAFEMODE-IF` | safeMode 既定ON、`allowUnreviewedText=false` 既定、未レビュー本文保護 |
| `CE0-REVIEW-IF` | `unreviewed/human_reviewed` の遷移境界（昇格は人手のみ） |
| `CG-01..05` | Working/ContextProjection/Consensus 分離、`patch + approval` のみ、proposal-only、監査4点セット必須 |

### 7A.2 入出力境界

- 入力（許可）:
  - KJ構造（card/island/relation/pending）と query constraints（scope/depth/reviewFilter/safeModePolicy）。
- 出力（許可）:
  - deterministic `bundleHash` を持つ ContextBundle。
  - `proposalId + diff + rationale` を満たす Patch Proposal。
- 適用経路:
  - `Working -> Consensus` は `applyPatch` 承認経路のみ。
  - `Working -> ContextProjection` は読取専用投影のみ（永続更新なし）。



### 7A.2.1 Interface contract references

本書は型シグネチャ、required/optional key、endpoint、status/errorを再定義しない。現行値は責務別に次を正本とする。

- 型、キー、列挙、version互換: [schemas.md §1.2 CE1/CE2/CE4 型契約](schemas.md#12-ce1ce2ce4-型契約実装非依存)
- endpoint、認証、status/error、副作用: [api.md §2.7〜§2.9](api.md#27-ce4-audit-integration-contractapicli-equivalence)
- CE1 v1のlogical / transport / handoff所属: [schemas.md layer ownership matrix](schemas.md#ce1-v1-layer-ownership-matrixlogical--transport--handoff)

旧Interface Freezeの型・method・event-order再掲は[形成履歴](history/architecture-contract-freeze-formation-2026-04-to-05.md#former-7a21-interface-freezeapiシグネチャ--データ型--イベント契約)へ移した。責務境界、禁止事項、Go/No-Goは本書§7A.1〜§7A.4を正とする。

### 7A.3 禁止事項（Non-Regression）

- AIは `Consensus Graph` を直接更新してはならない。
- `human_reviewed` 状態をAIが自動付与してはならない。
- safeMode既定ON時、未レビュー本文をAI入力へ含めてはならない。
- `mode=autonomous` でも proposal-only を維持し、監査4点セット（query/bundle/proposal/apply）欠損時は失敗扱いとする。
- `Core Graph` を契約語彙へ再導入してはならない（履歴注記用途のみ許可）。

### 7A.4 Go/NoGo Key（実装着手ゲート）

- **Go条件**
  - Query Preview を必須経路として維持する。
  - `Working -> Consensus` の更新経路は `patch + approval` のみ。
  - `mode=autonomous` でも proposal-only（auto-apply禁止）を維持する。
- **No-Go条件**
  - Query Preview bypass を許容する導線が存在する。
  - `Consensus Graph`（`ConsensusGraph` 識別子）への direct write を許容する導線が存在する。
  - AI単独で `human_reviewed` へ遷移させる。
  - safeMode既定ONまたは `allowUnreviewedText=false` 既定を後退させる。

No-Go 判定は次の canonical ID を正本とし、表記揺れは同義語扱いに限定する。

- `preview_bypass`
- `consensus_direct_write`
- `auto_apply_or_publish`
- `ai_review_auto_promotion`
- `safemode_default_relaxation`


### 7A.5 Drift-stop 固定（CE0）

- Contract ID collision は 0 件固定（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05` の重複再定義禁止）。
- 語彙 collision は 0 件固定（契約語彙は `Consensus Graph` / `WorkingGraph` / `ContextProjectionGraph` に統一）。
- Verify自己修復は最大3回。4回目相当で停止し、推測継続を禁止する。

---


## 7B. CE-1/CE-2/CE-4 責務境界（mock-first）

本節は各CEが守る責務と信頼境界だけを定義する。型、required/optional key、列挙、version互換は`schemas.md`、endpoint、status/error、副作用は`api.md`を正本とし、本書では再定義しない。

### 7B.1 CE1-CONTEXT-FOUNDATION

- Contract IDs: `CE1-CTXQ-IF` / `CE1-CTXB-IF` / `CE1-HASH-DET-IF` / `CE1-PREVIEW-GATE-IF`
- 責務: Query Previewを必須経路とし、同一queryから決定論的なContext Bundleを生成する。CE2/CE4はbackend完了を待たずmock-firstで検証し、受け渡しをread-onlyに保つ。
- 禁止: Preview bypass、非決定論bundleの成功扱い、下流によるCE1契約の暗黙変更。
- 正本: [schema type contracts and layer matrix](schemas.md#ce1-context-foundation)、[HTTP contract](api.md#28-context-query--bundle-contractce1-context-foundation)。

### 7B.2 CE2-LOW-RISK-AI-ASSIST

- Contract IDs: `CE2-PROPOSAL-IF` / `CE2-LIFECYCLE-IF` / `CE2-DRIFT-STOP-IF` / `CE2-NO-AUTOAPPLY-IF`
- 責務: AI出力をproposal-onlyとして管理し、CE1由来bundleとの整合を確認してから人間の判断へ渡す。
- 禁止: API/UI/workerからのauto-apply、AIによるreview昇格、契約差異を推測で補った継続。
- 正本: [proposal type and lifecycle contracts](schemas.md#ce2-low-risk-ai-assist)、[proposal-only HTTP boundary](api.md#290-proposal-only--apicli監査責務境界)。

### 7B.3 CE4-API-CLI-AUDIT

- 責務: API/CLI/GUIの同値性、監査4点セット、dry-runの無副作用を横断して検証する。
- 禁止: 監査欠損の成功扱い、dry-runでの永続化・外部共有・review昇格、未実装依存を理由とする契約検証停止。
- 正本: [audit type contracts](schemas.md#ce4-api-cli-audit)、[channel equivalence and side-effect contract](api.md#29-ce4-apicligui-同値性監査契約ce4-api-cli-audit)。

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

- 外部サービスとの共有（LLM含む）は設定で無効化できる
- LLMの接続先は明示設定（既定では外部サービスにデータを渡さない）
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
- `KJ_ATLAS_ALLOW_JIT_PROVISIONING=true` では未登録subjectをJITで `users` + `user_identities` 作成、`false` では `403` 拒否して事前プロビジョニング導線へ誘導する。
- attribution の正規キーは `users.id` で、外部subjectは `user_identities` でのみ解決する。


## 13. 形成履歴（Informative）

2026-05-04のinterface-only baselineとStream B反映メモは、現行契約と誤認されないよう[Architecture contract-freeze formation history](history/architecture-contract-freeze-formation-2026-04-to-05.md)へ分離した。現行の責務境界は本書、型は`schemas.md`、endpoint/status/errorは`api.md`を正本とする。
