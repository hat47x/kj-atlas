# AGENTS.md

> **目的 / Purpose**
> **このファイルは生成AIエージェント（Codex等）のための最短航路（Project Map）です。**
> 人間向けの入口は `README.md`。AIはまず本書を読み、必要な文書へ自律的に辿ってください。

**English summary**
This file is the navigation index for AI agents (Codex, etc.). Start here, then follow the read order to locate the single sources of truth for requirements, architecture, plans, implementation, and ops.

---

## 0. ゴールデンルール（最重要）

1. **作業開始時は必ず後述の `Read Order` を上から順に読む。**
2. **単一の変更タスクは“範囲を絞って”実施する。**（Docsのみ / Frontendのみ 等）
3. **仕様・設計は 00〜02 が上流。実装 03 は下流。** 上流に矛盾があれば上流を直してから下流を直す。
4. **安全設計が最優先。** SafeMode の既定ONと漏洩防止（share/export）が破られる変更は禁止。
5. **完遂条件を満たすまで継続して作業する。**（テスト・受入条件・回帰なし）

---

## 1. Read Order（AIが読む順序）

作業に入る前に、必ずこの順に参照：

1) **AI行動規範**: `00_Prompt/system_prompt.md`
2) **用語・概念**: `00_Prompt/domain.md`
3) **申し送り（重複排除済）**: `00_Prompt/handoff.md`
4) **AI開発引き継ぎ運用**: `00_Prompt/agent_handover.md`
5) **Codex+GSD運用ルール**: `00_Prompt/codex_gsd_skill_ops.md`
6) **価値→要件**: `01_Plans/adr/ADR-0001-value-to-requirements.md`
7) **全体アーキテクチャ**: `02_Architecture/architecture.md`
8) **スキーマ**: `02_Architecture/schemas.md`（関連: `02_Architecture/schemas_review_attribution.md`）
9) **該当フェーズ計画（ADR）**: `01_Plans/adr/ADR-0002`〜`ADR-0026`
10) **実装（03_Implement）**: 対象領域のソースへ
11) **運用・手順**: `04_Documentation/*`（必要に応じて）
12) **E2E確認方針**: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`

---

## 2. Project Map（ファイル構造インデックス）

> **ここがAGENTS.mdの中核です。**
> AIはこのマップを使って「どこに何があるか」を迷わず辿ってください。

### 2.1 リポジトリ直下（Public / OSS）

- `README.md`：人間向け入口（目的・導入・概要）。AIは必要時に参照。
- `ROADMAP.md`：公開ロードマップ（将来課題含む）。
- `THREAT_MODEL.md`：脅威モデル（zip import / markdown / supply chain / safeMode）。
- `SECURITY.md`：脆弱性報告方針。
- `SUPPORT.md`：利用者サポート導線。
- `DISCUSSIONS.md`：GitHub Discussions の運用窓口。
- `CONTRIBUTING.md`：開発参加の手引き。
- `GOVERNANCE.md`：運営方針。
- `CODE_OF_CONDUCT.md`：行動規範。
- `LICENSE`：ライセンス。
- `CHANGELOG.md`：変更履歴。

### 2.2 `.github/`（CI / テンプレ）

- `.github/workflows/ci.yml`：CI（lint/test/build）。
- `.github/workflows/release.yml`：リリース補助。
- `.github/ISSUE_TEMPLATE/*`：Issueテンプレ。
- `.github/pull_request_template.md`：PRテンプレ。

---

## 3. 00〜04 レイヤ構造（AI開発スタイル）

### 3.1 `00_Prompt/`（Why & Rules：AIへの指令・憲法）

- `00_Prompt/system_prompt.md`：**AIエージェントの行動規範（最優先）**。
- `00_Prompt/domain.md`：ドメイン用語・概念定義（KJ法概念、safeMode、レビュー等）。
- `00_Prompt/handoff.md`：申し送り（設計思想、注意点、B型文章化の扱い等）。
- `00_Prompt/agent_handover.md`：AIエージェント開発引き継ぎ（共通DoD/戦略/継続進行）。
- `00_Prompt/codex_gsd_skill_ops.md`：CodexにおけるGet Shit Done導入評価と運用ルール。
- `00_Prompt/strategic_phase_meta_prompt.md`：課題枯渇時に「現フェーズ完了 + 次フェーズ企画」を自走させるメタプロンプト。
- `00_Prompt/human_judgement_virtual_stakeholder_meta_prompt.md`：人間判断待ち処理を仮想ステークホルダー会議へ移管し、最小人間承認で運用するためのメタプロンプト。
- `00_Prompt/skills/gsd-kj-atlas/SKILL.md`：`codex_gsd_skill_ops.md` に準拠した Codex スキル定義（配布テンプレート）。
- `00_Prompt/skills/markdown-mermaid-docops/SKILL.md`：Markdown + Mermaid.js 文書整備とMCP確認の補助スキル（配布テンプレート）。

**注意**：AIの挙動規範は原則ここに集約。READMEには最小限の誘導のみ。

**補足**：Codex の実行時スキルは `/opt/codex/skills/.system` または `$CODEX_HOME/skills`（既定 `~/.codex/skills`）から読み込まれる。リポジトリ内 `00_Prompt/skills/*` は配布元（テンプレート）として扱う。

### 3.2 `01_Plans/`（How to Process：計画・タスク分割）

- `01_Plans/adr/ADR-0000-adr-governance.md`：ADR運用方針（採番・更新規約）。

- `01_Plans/adr/TEMPLATE.md`：ADR標準テンプレート（人間/生成AI共通）。

- `01_Plans/adr/ADR-0002-internal-roadmap.md`：開発内部向けロードマップ（公開版は直下 `ROADMAP.md`）。
- `01_Plans/adr/ADR-0001-value-to-requirements.md`：価値観→要件の変換（判断基準）。
- `01_Plans/adr/ADR-0003-phase0-bootstrap.md`：初期立ち上げ・環境。
- `01_Plans/adr/ADR-0004-phase1-canvas-mvp.md`：Canvas MVP。
- `01_Plans/adr/ADR-0005-phase2-qualitative-integration.md`：質的統合（KJ的機能拡張）。
- `01_Plans/adr/ADR-0006-phase3-review-governance.md`：レビュー・監査・統治。
- `01_Plans/adr/ADR-0007-future-backlog.md`：将来課題の保管庫。
- `01_Plans/adr/ADR-0008-cli-tooling-plan.md`：CLI導入計画（運用・統治・自動化）。
- `01_Plans/adr/ADR-0009-local-llm-integration.md`：ローカルLLM統合（抽象化・運用）。
- `01_Plans/adr/ADR-0010-ADR-0017*.md`：粗粒度ADRを分割した詳細ADR群（価値/要件/Phase2/CLI）。
- `01_Plans/adr/ADR-0018-coding-standards-and-smell-remediation.md`：バッドスメル是正と規約運用方針。
- `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`：E2E確認方針とCompose運用。
- `01_Plans/adr/ADR-0020-oidc-saml-mock-idp-sp-profile.md`：OIDC/SAMLのMock IdP + SP実装/検証プロファイル。
- `01_Plans/adr/ADR-0021-env-var-global-prefix-migration.md`：環境変数のグローバルプレフィックス移行方針。
- `01_Plans/adr/ADR-0022-doc-ops-04-documentation-information-interface.md`：DOC-OPS-04後続ADRの共通I/F（用語・見出し・判定メタ）先行定義。
- `01_Plans/adr/ADR-0023-ADR-0025*.md`：DOC-OPS-04の可読性/品質ゲート境界/変更統治の確定。
- `01_Plans/adr/ADR-0026-next-phase-human-in-the-loop-reversible-synthesis.md`：次フェーズ（HIL-RS-01）の計画ADR。
- `01_Plans/issues/README.md`：Issue補助メモのActive一覧（Draft/Open/In Progress）。
- `01_Plans/issues/*.md`：GitHub Issue運用を補助する短命メモ（Done時は原則削除）。
- `01_Plans/issues/TEMPLATE.md`：Issue補助メモの標準記述テンプレ（人間/生成AI共通）。

### 3.3 `02_Architecture/`（Structure：設計・I/F・デプロイ）

- `02_Architecture/architecture.md`：全体構成（最上位）。
- `02_Architecture/schemas.md`：データスキーマ（document/view/pack等）。
- `02_Architecture/api.md`：API設計。
- `02_Architecture/deployment.md`：デプロイ構成（コンテナ・DB等）。
- `02_Architecture/runtime_parameter_registry.md`：環境変数/実行パラメータの単一正本（命名規約・既定値）。
- `02_Architecture/enterprise_architecture.md`：企業・行政運用（SSO/ACL/公開方式含む）。
- `02_Architecture/review_attribution.md`：レビュー帰属（人間レビュー済みフラグ等）。
- `02_Architecture/schemas_review_attribution.md`：上記のスキーマ詳細。
- `02_Architecture/island_shapes.md`：島形状（rect/polygon等）。
- `02_Architecture/coding_standards.md`：シンプル・セキュア開発のコーディング規約。
- `02_Architecture/strict_mode_exception_approval_flow.md`：strict mode例外緩和の承認フロー仕様（AUTH-OPS-03）。

**LLM関連（設計・制約・品質）**
- `02_Architecture/llm_provider_spec.md`：Provider抽象仕様。
- `02_Architecture/llm_input_ir_spec.md`：LLM投入IR（正規化・前処理・schema・切り詰め）。
- `02_Architecture/llm_runtime_constraints.md`：実行制約（IPC/fixture/CI）。
- `02_Architecture/llm_quality_strategy.md`：品質戦略（二段評価・回帰）。
- `02_Architecture/llm_escalation_policy.md`：Local-first + escalation方針。

### 3.4 `03_Implement/`（Code：実装）

#### Backend（Python）
- `03_Implement/backend/src/kj_atlas_api/main.py`：APIエントリ。
- `03_Implement/backend/src/kj_atlas_api/routes/`：ルーティング（docs/ai等）。
- `03_Implement/backend/src/kj_atlas_api/models*.py`：DB/AIモデル。
- `03_Implement/backend/src/kj_atlas_api/llm/provider.py`：LLM Provider抽象/実装。
- `03_Implement/backend/alembic/`：DBマイグレーション。
- `03_Implement/backend/tests/`：バックエンドテスト。

#### Frontend（React + TS）
- `03_Implement/frontend/src/App.tsx`：アプリルート。
- `03_Implement/frontend/src/ui/`：UIパネル（Import/Diff/Share/Side等）。
- `03_Implement/frontend/src/canvas/`：Canvas描画（cards/islands/edges/reading order）。
- `03_Implement/frontend/src/domain/`：ドメインロジック（差分/検証/メトリクス/ポリシー）。
- `03_Implement/frontend/src/export/`：エクスポート（bundle/png/svg/narratives等）。
- `03_Implement/frontend/src/import/`：インポート（zip/markdown sanitize/schema validate）。
- `03_Implement/frontend/src/worker/`：Web Workers（diff/diagnostics/trace）。
- `03_Implement/frontend/tests/fixtures/`：golden fixtures。

#### Deploy（compose）
- `03_Implement/deploy/docker-compose.yml`：統合起動。
- `03_Implement/deploy/nginx.conf`：リバプロ例。

### 3.5 `04_Documentation/`（Guide：運用・利用者向け）

- `04_Documentation/installation.md`：導入手順。
- `04_Documentation/configuration.md`：設定。
- `04_Documentation/operations.md`：運用。
- `04_Documentation/e2e_testing.md`：PlaywrightベースE2E方針。
- `04_Documentation/diagnostics.md`：diagnostics worker のschemaVersion/互換/フォールバック方針。
- `04_Documentation/security.md`：運用上のセキュリティ。
- `04_Documentation/security_operational_guidelines.md`：セキュリティ運用ガイドライン（プロファイル選択時の判断補助）。
- `04_Documentation/release.md`：リリース。
- `04_Documentation/narratives.md`：文章化/要約出力。
- `04_Documentation/canonicalization.md`：正規化/決定論。
- `04_Documentation/local_llm_ops_guide.md`：ローカルLLM運用。
- `04_Documentation/codex_skill_operations.md`：Codex skill 導入・運用手順。

---

## 4. AIエージェントの作業プロトコル

### 4.1 作業開始テンプレ

- 変更対象を明確化（Docs / Frontend / Backend / Schema）。
- `Read Order` に従い、必要な設計文書を先に読む。
- 受入条件（Acceptance criteria）を先に書き出す。
- 実装/修正 → テスト → 受入確認 → ドキュメント整合。

### 4.2 変更範囲の原則

- Docsのみタスクでは **コードを変更しない**。
- Schema変更時は：
  - `02_Architecture/schemas.md` を先に更新
  - import/export/validate/tests を追随
- SafeModeに影響する変更は：
  - `03_Implement/frontend/src/domain/policy/safe_mode.ts` と関連テストを必ず更新
  - share/export の既定ONを破らない

### 4.3 典型タスクの入口

- **Canvas/UIの変更**：`03_Implement/frontend/src/ui/` と `src/canvas/`
- **差分・レビュー**：`03_Implement/frontend/src/diff/` と `src/domain/patch/`
- **インポート/エクスポート**：`src/import/` と `src/export/`
- **Worker化**：`src/worker/`（protocol/client/compute を分離）
- **SSO/公開方式（企業・行政）**：`02_Architecture/enterprise_architecture.md`
- **LLM統合**：`02_Architecture/llm_*` と `backend/src/kj_atlas_api/llm/provider.py`

---

## 5. README.mdとの関係

- **人間向け入口**：`README.md`
- **AI向け入口**：`AGENTS.md`

---

## 6. 迷ったときの判断基準

1) 価値・判断軸：`01_Plans/adr/ADR-0001-value-to-requirements.md`
2) 安全：`THREAT_MODEL.md` と SafeModeポリシー
3) 企業・行政要件：`02_Architecture/enterprise_architecture.md`
4) 後方互換：`02_Architecture/schemas.md`

---

## 7. このファイルの更新ルール

- 新しい主要ドキュメントやディレクトリが増えたら **必ず Project Map を更新**。
- ファイル名変更・統合が発生したら Read Order と Project Map を同期。
- 長文の仕様本文はここに書かず、適切なドキュメントへ置き、ここから参照する。


### 4.4 文書横断ドリフト検知（DOC-OPS-02）

- AUTH-OPS-03 / DOC-OPS-02 の更新時は、`02_Architecture/strict_mode_exception_approval_flow.md` を起点に **`02_Architecture` → `04_Documentation` → `01_Plans` → `AGENTS.md`** の固定順序で同期する（`02_Architecture/enterprise_architecture.md` → `04_Documentation/operations.md` / `04_Documentation/security.md` → `01_Plans/project-progress-dashboard.md` / `01_Plans/issues/decision-pack-2026-03-human-judgement.md`）。
- 同期時は次の4観点を必ず確認する。
  1) 用語（Security Officer / System Owner / Platform Operator）
  2) 役割（2者承認と実行責務分離）
  3) 導線（相互リンク）
  4) 固定値（D1〜D4）
