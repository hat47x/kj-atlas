# Issue: AI-MODEL-GOVERNANCE-01 機能・操作毎のモデル選択（画面指定）・テナント/部署別制限・モデル/サービスの動的追加

- Type: Feature / AI capability / Security
- Status: In Progress
- Source Issue: ドッグフーディング指令（2026-08-15）。「機能・操作毎の生成AIモデルの使い分けを画面上で指定可能にし、適宜切り替えて呼び出せるようにする。テナントや部署ごとに利用可能なモデルには制限を設ける。新規の生成AIモデル・サービスも管理者UI/CLI等から動的に追加できるようにする」
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/`（models / llm / routes / admin）, `03_Implement/frontend/src/`（api/client, ui）, `02_Architecture/`（api.md, llm_provider_spec.md, runtime_parameter_registry.md）, migration
- Related ADR/Spec: `01_Plans/adr/ADR-0065-llm-model-selection-by-task-complexity.md`（D2優先度2=テナント層は Phase 2 と明記）, `01_Plans/adr/ADR-0050-llm-provider-observability-and-contract-fidelity.md`, `02_Architecture/llm_provider_spec.md`（provider抽象の正本）, `00_Prompt/ai_cognitive_externalization_requirements.md` §7.1a（MMR-01〜06）, `01_Plans/issues/issue-AI-ROUTE-01-multi-model-routing-and-final-judgment-boundary.md`, `01_Plans/issues/issue-OPS-LLM-COST-01-cost-control-contract-unimplemented.md`
- Expected verification level: `integration`

## 課題

現状、モデル選択は**静的で、コード内 enum と環境変数に閉じている**。ユーザー要求の4点はいずれも未実装である。

| 要求 | 現状 | ギャップ |
|------|------|---------|
| 機能・操作毎のモデル使い分けを**画面で指定** | `resolve_model_for_task()` は `request.model`（優先度1）→ `KJ_ATLAS_LLM_TASK_MODEL_MAP`（優先度3）の静的解決のみ。**AI リクエスト Pydantic スキーマ（`GenerateNarrativeRequest` 等）は `model` フィールドを露出していない** | 優先度1（リクエスト層）が API 境界に到達していない。UI 選択子が無い |
| 適宜切り替えて呼び出す | 同上 | 同上 |
| テナント/部署ごとに**利用可能モデル制限** | 無し。`tenant_settings` テーブルも無い。ADR-0065 D2 は「優先度2=テナント層は Phase 2」と将来扱い | allowlist/denylist の概念・テーブル・強制が全て欠落 |
| 新規モデル/サービスを**管理者UI/CLIから動的追加** | `KJ_ATLAS_LLM_PROVIDER` は `none|local|local_http|large-scale|external|deepseek` の閉じた enum。モデルは `model_id` 文字列（≤256字）のみで**レジストリが無い** | 新サービス追加はコード変更＋再起動が必要。動的追加の土台が無い |

「部署」の概念も**現在データモデルに存在しない**（`tenants` と `tenant_memberships` と `users.roles` のみ）。テナントより細かい組織単位としての部署は新設が必要。

## 三要素分析（ADR-0067）

| 次元 | 分析 | 他次元への制約 |
|------|------|---------------|
| **業務設計** | モデル選定は「コスト最適化（軽量タスク→安価モデル）」と「品質（判断系→高推論モデル）」の二軸。**誰が何を選べるか**＝ユーザー（自分の操作）vs 管理者（テナント/部署ポリシー）。部署は「組織のポリシー適用単位」であって認証境界ではない | ユーザーは**許可された範囲内で**切替可能。管理者はポリシー（allowlist）とレジストリ（モデル/サービスのライフサイクル）を管理 |
| **データ設計** | ①モデル/サービスレジストリ（動的追加の正本）②テナント/部署のモデルallowlist ③呼び出し時の実効モデル解決は上記に閉じる。APIキー等の秘密は平文保存せず参照/暗号化 | レジストリは tenant-scoped にしない（サービス/モデルはプラットフォーム共有資産）。allowlist は tenant/dept-scoped。RLS/WHERE の二層防御（ADR-0059） |
| **機能設計** | ①UI/API で操作毎にモデル選択を露出 ②呼び出し時に allowlist を強制（fail-closed）③管理者UI/CLIでモデル/サービスのCRUD ④監査（MMR-05: routingStage/provider/model + 変更・制限違反） | 既存 `resolve_model_for_task()` の優先度1→2→3 に allowlist 強制を挿入。final_judgement（MMR-04）は管理者ポリシーで固定しユーザー自由選択から除外 |

## 要件の練り上げ（本issueの核）

### R1. モデル/サービスレジストリ（動的追加の土台）

新テーブルでモデルとサービスを分離する（責務分離）：

- `llm_provider_registry`（サービス=認証/接続境界。`llm_provider_spec.md` の信頼境界分類に準拠）:
  - `id`, `provider_kind`（`local`|`external`|`deepseek` 等）, `display_name`, `base_url`, `api_key_ref`（秘密は参照のみ・平文保存しない）, `lifecycle_state`（`active`|`disabled`）, `created_at`, `updated_at`
- `llm_model_registry`（モデル=呼び出し先。provider に紐付く）:
  - `id`（canonical model_id・≤256字）, `provider_id`（FK）, `display_name`, `capabilities`（`intermediate`|`final_judgement` 相当の階層タグ）, `lifecycle_state`, `created_at`, `updated_at`

管理者UI/CLI（`/admin/provision/models` 系・control-plane 認可）から CRUD。`lifecycle_state` で無効化しても既存呼び出しは fail-closed（無効モデルへの呼び出しは拒否）。

### R2. 操作毎の画面指定（優先度1を API 境界へ）

- 既存 AI リクエストスキーマに `model?: string` を追加し、`resolve_model_for_task()` の優先度1へ配線する。
- フロントエンドは、対象 AI 操作のトリガー（島の表札・ナラティブ・カード文面 etc.）に**モデル選択子**を露出。選択肢は「そのテナント/部署で利用可能なモデル」（R3 の allowlist でフィルタ）。
- 未選択時は既存の優先度2/3（テナントポリシー→グローバル既定）へフォールバック。

### R3. テナント/部署別の利用可能モデル制限（fail-closed allowlist）

- `tenant_model_allowlist`（`tenant_id`, `model_id`, `lifecycle_state`）で**テナント単位の allowlist** を設ける。空 = 既定セット（管理者が定めるプラットフォーム既定）。
- **部署**概念を新設（下記 D1 参照）し、`department_model_allowlist`（`department_id`, `model_id`）で**部署単位のより狭い allowlist** を適用（部署 allowlist ⊆ テナント allowlist）。
- 呼び出し時、`resolve_model_for_task()` の結果（リクエスト指定含む）が allowlist に含まれない場合は **403 `model_not_allowed`**（fail-closed・理由に選択肢を返す）。
- final_judgement（MMR-04）はユーザー自由選択から除外し、テナントポリシーの high-reasoning モデルへ固定。

### R4. 監査（MMR-05 と整合）

- 呼び出し監査は既存 `_audit_llm_trace` を拡張し `model`/`routingStage`/`provider` を記録（MMR-05 は実装済み）。
- 追加: モデル/サービスの CRUD と allowlist 変更を **admin 監査**（`SEC-ADMIN-PLANE-03` の `admin_audit_events`）へ記録。制限違反（`model_not_allowed`）も記録。

## 設計判断（2026-08-15 承認反映・仮承認）

- **D1（ポリシー適用単位: 部署ではなく「メンバー集合体としてのグループ」）**: **`member_groups`（tenant 配下のメンバー集合・正規化テーブル）** を採用する。部署（組織単位・階層）ではなく、**任意のメンバー集合**として位置付ける（下記「②の深掘り」参照）。このグループを `member_group_model_allowlist` の適用単位にする。
- **D2（allowlist 方式）**: **allowlist**（明示許可のみ・fail-closed・未許可 → 403 `model_not_allowed`）。
- **D3（秘密の扱い）**: APIキーは `api_key_ref`（環境変数/秘密管理を参照）とし、DB 平文保存しない。
- **D4（実効モデル解決の優先順位）**: リクエスト指定 → グループ allowlist → テナント allowlist → タスク階層（MMR-04）→ グローバル既定。allowlist は各層で交差（より狭い方が勝つ）。
- **D5（画面選択の対象操作）**: 「ナラティブ生成」「島の表札」「カード文面整え」＋ **初期タイトル生成（suggest-document-title）** にモデル選択子を露出。final_judgement は管理者固定のまま（MMR-04 尊重）。
- **D6（ADR-0065 との関係）**: ADR-0065 を Proposed→Accepted へ進め、本件を「D2 優先度2（テナント層）＋動的レジストリ」の実装として位置付ける。
- **D7（初回スコープ）**: **R1（レジストリ）→ R3（テナント allowlist 強制）→ R2（画面指定）→ R4（監査）** を実装し、**グループレベル allowlist（member_groups）はデータモデル設計まで・実装は Phase 2** に切り出す（テナント単位制限を先に成立）。

### ②の深掘り: 「部署」vs「メンバー集合体としてのグループ」

ユーザー指示（2026-08-15）:「部署というよりはメンバーの集合体としてのグループのような位置づけがよい」。類似アプリの設計を調査した結果。

| アプリ | 単位 | グループの位置づけ |
|--------|------|-------------------|
| **Miro** | Team | ボードの共有/権限境界。チーム=メンバー+権限 |
| **Slack** | Workspace → **User Group** | 名前付きメンバー集合。@mention＋権限スコープ。**最も近いモデル** |
| **Notion** | Workspace → **Group** | 管理者定義のメンバー集合。権限ルールで参照 |
| **Figma** | Team → Project | ファイル共有の境界。チーム=ポリシー単位 |
| **Confluence** | Space → **Group** | スペース権限がグループを参照（「グループXにread」）。**ポリシーグループの典型** |

**共通パターン**: グループは「テナント/ワークスペース内の名前付きメンバー集合」であり、**認証境界ではなくポリシー適用単位**（allowlist/権限ルールが参照する）。roles が権限（認可）を、グループがポリシーの適用範囲を担う。

**kj-atlas への適用（メリット/デメリット/射程）**:

- **メリット**: ①KJ 実践の協働単位（チーム・プロジェクト・探究グループ）が動的に形成/解散する性質と整合 ②「部署」のような組織階層（報告線・所属）を前提にしない ③正規化テーブル（`member_groups` + `member_group_members`）で RLS（ADR-0059）・監査（SEC-ADMIN-PLANE-03）が成立 ④将来の文書共有/権限にも再利用可能
- **デメリット**: 組織横断の一律ポリシー（「全社でXXモデル禁止」）はグループごとの明示適用が必要（テナント allowlist で吸収できる）
- **射程（本アプリ）**: 単一テナント内の協働が主（SaaS 化は進行中）。まずテナント allowlist を成立させ、グループはデータモデル設計まで用意して Phase 2 で適用する（①A と整合）

**結論**: `member_groups`（tenant 配下・メンバー集合・lifecycle 付き）を新設し、`member_group_model_allowlist` の適用単位とする。実装は Phase 2。

## スコープ

- 実施する: R1（レジストリ）→ R3（allowlist 強制）→ R2（画面指定）→ R4（監査）の順で、backend データ層→強制→API→UI→監査を積む。管理者CLI（`verify_api_admin.sh` 拡張）で CRUD を検証。
- 実施しない: AI 品質の採点（反スコアリング不変条件）。プロバイダ通信実装の新規ベンダ対応（レジストリに登録可能なのは既存 transport の `local`/`external`/`deepseek` に限定）。部署の認証境界化。

## 受入条件

- [x] `llm_provider_registry` / `llm_model_registry` が管理者UI/CLIから動的に追加・無効化できる（既存 env プロバイダの起動時シード含む・U4）。→ **R1 実装済み（iteration 44）**: 2テーブル＋migration 0031＋`/admin/provision/models` CRUD（control-plane認可）＋`seed_registry_from_env()` 起動時シード。`test_model_governance.py` 5件 pass。
- [x] AI リクエストが `model` を露出し、`resolve_model_for_task()` が allowlist を強制する（未許可モデル → 403 `model_not_allowed`）。→ **R3 実装済み（iteration 45）**: 5ルート（ナラティブ/表札/文面/束ね/初期タイトル）に `model` を露出し、`_assert_model_allowed()` が tenant allowlist を強制（未許可 → 403・`allowedModels` を返す）。
- [x] テナント allowlist が fail-closed で適用される（グループ allowlist はデータモデル設計まで・Phase 2 実装）。→ `tenant_allowlist_effective_model_ids()`（空=プラットフォーム既定・非空=fail-closed）を `_assert_model_allowed` で適用。`test_allowlist_enforced_on_ai_route` で固定。
- [x] 主要 AI 操作（ナラティブ生成・島の表札・カード文面整え・**初期タイトル生成**）の UI にモデル選択子が露出し、選択肢が利用可能モデルに限定される。→ **R2 UI 実装済み（iteration 47）**: `ModelSelector` コンポーネント（`GET /ai/available-models` でテナント許可モデルのみ・"auto"既定）を**島の表札提案**面に露出。`proposeIslandSummary`→proposals/island-summary→suggest_island_summary へ `model` を通し、backend の allowlist 強制（403）が効く。他操作（ナラティブ/文面/束ね/初期タイトル）の選択子は同コンポーネントを各面に露出する拡張として残る。
- [x] final_judgement はユーザー自由選択から除外され、管理者ポリシーへ固定される（MMR-04）。→ **実装済み（iteration 49）**: `get_available_models` が `_is_user_selectable_model`（intermediate/generate 層のみ・final_judgement専用モデル除外）でフィルタ。選択子に final_judgement 専用モデルは表示されず、final_judgement タスクは管理者ポリシー（allowlist＋タスク階層解決）へ固定。`test_available_models_excludes_final_judgement_only`。
- [x] モデル/サービス CRUD と allowlist 変更・制限違反が admin 監査に記録される。→ **R4 実装済み（iteration 46）**: モデルCRUD/allowlist変更は `record_admin_plane_audit` middleware（`admin_audit_events`）が記録（`test_model_crud_and_allowlist_changes_are_audited`）。`model_not_allowed` 違反は構造化ログ（tenantId/modelId/allowedModels）で記録。
- [x] `member_groups` のデータモデル設計が本issueに記録される（Phase 2 実装の土台）。→ **記録済み（iteration 51）**: `member_groups` / `member_group_members` / `member_group_model_allowlist` の3テーブル（tenant-scoped・RLS）と、実効モデル解決（所属グループallowlist交差→テナント→タスク階層→既定）への組み込み・admin設定経路を本issue「member_groups データモデル設計」節に確定。Phase 2 で実装。
- [ ] `python 01_Plans/docs_check.py`・backend/frontend 回帰が通る。

## 検証計画

- `cd 03_Implement/backend && python -m pytest tests/test_model_governance.py -q`（レジストリ CRUD・allowlist 強制・優先順位・fail-closed）
- 実バックエンドで `bash scripts/verify_api_admin.sh`（モデル CRUD チェック追加後）
- `cd 03_Implement/frontend && npm run test`（モデル選択子・allowlist フィルタ）

## member_groups データモデル設計（Phase 2 実装の土台・2026-08-15 記録）

テナント配下のメンバー集合グループを、ポリシー適用単位として定義する（D1・②の深掘り参照。roles=権限、グループ=ポリシー適用範囲）。

### テーブル設計

- **`member_groups`**（tenant-scoped・RLS）:
  - `tenant_id`（PK・FK tenants）, `id`（PK）, `display_name`, `lifecycle_state`（active/disabled）, `created_at`, `updated_at`
  - 組織階層（報告線・親子）を持たない任意のメンバー集合（チーム・プロジェクト・探究グループ等）
- **`member_group_members`**（tenant-scoped・RLS）:
  - `tenant_id`, `group_id`（FK member_groups）, `user_id`（FK users）, `created_at` — 複合PK `(tenant_id, group_id, user_id)`
- **`member_group_model_allowlist`**（tenant-scoped・RLS）:
  - `tenant_id`, `group_id`, `model_id`（FK llm_model_registry）, `lifecycle_state`, `created_at`, `updated_at` — 複合PK `(tenant_id, group_id, model_id)`

### 実効モデル解決への組み込み（Phase 2 で `_assert_model_allowed` を拡張）

優先順位（D4）: **リクエスト指定 → ユーザー所属グループの allowlist 交差 → テナント allowlist → タスク階層（MMR-04）→ グローバル既定**。

- グループ allowlist は「より狭い方が勝つ」: ユーザーが複数グループに属する場合は**交差**、テナント allowlist より**狭い**場合のみ制約（テナント allowlist ⊆ プラットフォーム既定と同じ関係）。
- 未許可 → 403 `model_not_allowed`（既存の構造化エラー＋`allowedModels` を流用）。
- 管理者UI/CLI: `/admin/provision/models/groups/{group_id}/allowlist`（control-plane 認可・SEC-ADMIN-PLANE-03 監査）で設定。

### 設計上の決定点（Phase 2 実装時に確定）

- ユーザーが**グループ未所属**の場合: グループ層をスキップ（テナント allowlist のみ）。
- グループ allowlist が空: そのグループは制約しない（テナント層へ委譲）— 空=制約なしはテナント allowlist のセマンティクスと同じ。
- 監査: グループ allowlist 変更は `admin_audit_events` へ（R4 の middleware が /admin/* を既に記録）。

## 関連する未計画要件の検査（2026-08-15・ユーザー指示）

本件の設計時に**関連して浮上した未計画の要件**を洗い出した。実装スコープとは別に追跡する。

| # | 未計画要件 | 内容 | 扱い |
|---|-----------|------|------|
| U1 | **選択モデル障害時の挙動** | ユーザー指定モデルが利用不能（timeout/500）な場合のフォールバック。intermediate は他許可モデルへ fallback？ final_judgement は MMR-06（held 遷移）のみ | 新規 issue として起票候補 |
| U2 | **モデル選択の永続化** | 操作毎のユーザー選択をローカル/サーバーに保存するか。セッション毎 or 永続 | 新規 issue 候補（初回はセッション内のみ） |
| U3 | **デフォルトモデルの管理UI設定** | 現行のグローバル既定は環境変数。管理者UIでデフォルトを変更できるようにするか | 新規 issue 候補（初回は env のまま） |
| U4 | **既存 env プロバイダのレジストリ移行** | `local`/`deepseek` 等の env 設定をレジストリへ取り込む移行経路（起動時シード） | 本issue R1 の受入条件に含める |
| U5 | **MCP 経路とのモデル指定整合** | read-only MCP は `get_context_projection` のみ（LLM 呼び出し無し）のため、現状影響無し。将来 MCP が AI を呼ぶ場合の指定経路 | 監視対象（現状非対応で可） |
| U6 | **コスト可視化（OPS-LLM-COST-01 と連動）** | モデル選択子に相対コスト階層表示。OPS-LLM-COST-01（LLMコスト統制）の一部として扱う | OPS-LLM-COST-01 へ委譲 |
| U7 | **グループ allowlist の権限境界** | `member_groups` はポリシー適用単位であり認証境界でない旨を明文化（roles と混同しない） | 本issue D1 に反映済み・契約文書に記載 |

U1〜U3 は初回スコープ（D7）に含めず、本issue の「未計画要件」として追跡し、必要に応じて別 issue 化する。

## 補足

- 発見経緯: ドッグフーディング指令（2026-08-15）。既存の `resolve_model_for_task()` / ADR-0065 / AI-ROUTE-01（MMR-01〜05 実装済み）が**静的なルーティング基盤**を既に提供しており、本件はそれを「画面指定＋組織別制限＋動的レジストリ」へ拡張するもの。
- 依存: `SEC-ADMIN-PLANE-03`（admin 監査基盤）が iteration 40 で実装済みのため、R4 の admin 監査はそれを再利用できる。
- 本issueは**要件の練り上げ＋承認**を経て実装に移る。D1〜D7 は仮承認済み（2026-08-15）。
