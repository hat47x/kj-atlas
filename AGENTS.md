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
3) **定性情報カード品質要件**: `00_Prompt/qualitative_card_quality_requirements.md`
4) **申し送り（重複排除済）**: `00_Prompt/handoff.md`
5) **AI開発引き継ぎ運用**: `00_Prompt/agent_handover.md`
6) **Codex+GSD運用ルール**: `00_Prompt/codex_gsd_skill_ops.md`
7) **Codex+RTK token saving運用**: `00_Prompt/codex_rtk_token_saving_ops.md`
8) **認知外在化AI要件（新規中核）**: `00_Prompt/ai_cognitive_externalization_requirements.md`
9) **価値→要件**: `01_Plans/adr/ADR-0001-value-to-requirements.md`
10) **全体アーキテクチャ**: `02_Architecture/architecture.md`
11) **スキーマ**: `02_Architecture/schemas.md`（関連: `02_Architecture/schemas_review_attribution.md`）
12) **MVPデータ運用境界**: `02_Architecture/data_model_operations_overview.md`
13) **該当フェーズ計画（ADR）**: `01_Plans/adr/ADR-0002`〜`ADR-0057`（価値→社会的目標の実現フェーズ索引は `ADR-0036`、ガバナンス適正化方針は `ADR-0039`、ドメイン表現第一級化は `ADR-0040`、根幹価値の保護は `ADR-0041`〜`ADR-0043`、UI/UX品質基準は `ADR-0044`、エージェント分担は `ADR-0045`、性能予算は `ADR-0046`、設計判断ADRの飽和とexecution-first転換は `ADR-0047`、視覚言語/コマンド到達/KJ法語彙は `ADR-0048`、W型累積KJ法の反復的探究モデルは `ADR-0057`）
14) **実装（03_Implement）**: 対象領域のソースへ
15) **運用・手順**: `04_Documentation/*`（必要に応じて）
16) **E2E確認方針**: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`

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

### 2.3 `.claude/`（Claude Code プロジェクト設定）

- `.claude/README.md`：Claude Code 導入手順の正本（推奨 permission・MCP拡張・検証前提。`ADR-0045` / `agent_collaboration.md`）。
- `.claude/settings.json`：プロジェクト共有設定（秘匿情報なし。`KJ_ATLAS_LLM_PROVIDER=none` 既定）。
- `.claude/settings.local.json`：個人ローカル設定（git管理外、`.gitignore`）。

---

## 3. 00〜04 レイヤ構造（AI開発スタイル）

### 3.1 `00_Prompt/`（Why & Rules：AIへの指令・憲法）

- `00_Prompt/system_prompt.md`：**AIエージェントの行動規範（最優先）**。
- `00_Prompt/domain.md`：ドメイン用語・概念定義（KJ法概念、safeMode、レビュー等）。
- `00_Prompt/qualitative_card_quality_requirements.md`：KJ法カードに記述する定性情報の品質、低負担な確認UX、AI支援境界の正本。
- `00_Prompt/w_type_iterative_inquiry_requirements.md`：6ラウンド累積KJ法の反復・引継ぎ・停止再開・分岐を扱うProposed要件。`ADR-0057` 受理前は現行契約として実装しない。
- `00_Prompt/handoff.md`：申し送り（設計思想、注意点、B型文章化の扱い等）。
- `00_Prompt/agent_handover.md`：AIエージェント開発引き継ぎ（共通DoD/戦略/継続進行）。
- `00_Prompt/codex_gsd_skill_ops.md`：CodexにおけるGet Shit Done導入評価と運用ルール。
- `00_Prompt/codex_rtk_token_saving_ops.md`：CodexにおけるRTK token-saving CLI proxyの使い分け、検証、ロールバック手順。
- `00_Prompt/ai_cognitive_externalization_requirements.md`：生成AIの認知外在化フレームワーク要件（ContextQuery/ContextBundle/safeMode統治）。
- `00_Prompt/meta_prompt.md`：ショートハンド（フェーズ完了判定 / 次フェーズ企画 / 並列実行 / 開発継続）を展開する自律進行メタプロンプト。
- `00_Prompt/virtual_stakeholder_consensus.md`：人間判断待ち論点を扱う仮想ステークホルダー会議プロトコル。
- `00_Prompt/agent_collaboration.md`：Cowork/Claude Code/Codex の責務分担と協働プロトコル（`ADR-0045` の運用正本）。並行作業の衝突回避（CP-1..6）と Claude Code 拡張導入の入口。
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
- `01_Plans/adr/ADR-0027-hil-rs-02-next-phase-execution-plan.md`：次フェーズ（HIL-RS-02）の実行計画ADR。
- `01_Plans/adr/ADR-0028-ai-cognitive-externalization-phase-plan.md`：認知外在化要件を実装フェーズへ接続する計画ADR。
- `01_Plans/adr/ADR-0029-ADR-0034*.md`：runtime境界、製品化、価値実現、データ運用、最新main収束/branch衛生の後続ADR群。
- `01_Plans/adr/ADR-0036-value-to-social-goal-realization-roadmap.md`：プロダクト価値(V0–V4)→社会的目標を VR0–VR5 として並べた実現フェーズ索引（親ADR）。
- `01_Plans/adr/ADR-0037-value-measurement-harness-and-scorecard.md`：価値観測ハーネスと二軸スコアカード運用（VR4）。
- `01_Plans/adr/ADR-0038-social-diffusion-of-explainable-consensus.md`：説明可能な合意形成の社会的普及モデル（VR5）。
- `01_Plans/adr/ADR-0039-governance-right-sizing-personal-oss.md`：個人OSS・プレリリース段階のガバナンス適正化（KEEP/RELAX-DEFER/緩和禁止の不変条件、多役割→Maintainer集約）。
- `01_Plans/adr/ADR-0040-domain-expression-first-class-strategy.md`：中核ドメイン概念（保留/違和感/根拠/矛盾）の第一級化戦略。`DOMAIN-EXPR-01..04` へ段階分割し、`ADR-0032` Accepted化と `PRODUCT-VALUE-02` 循環デッドロックを解消。
- `01_Plans/adr/ADR-0041-core-value-invariants-single-guard.md`：根幹価値の非後退不変条件（CVI-1..7）を単一の砦（横断テスト）で守る。正本は `value_traceability.md` §2.5。
- `01_Plans/adr/ADR-0042-value-realness-validation-and-notice-exit.md`：価値実在の最小ドッグフード検証と README NOTICE の段階的脱却基準（段階A/B/C）。
- `01_Plans/adr/ADR-0043-complexity-budget-for-cognitive-load.md`：機能増加が認知負荷で根幹価値を侵さないための複雑性予算（CB-1..4）と追加時の自己申告。
- `01_Plans/adr/ADR-0044-ui-ux-quality-baseline-and-verification.md`：UI/UX品質基準（UQ-1..6：操作到達性/a11y/i18n等価性/レイアウト堅牢性/状態可視性/認知負荷節度）と検証観点の統合。正本は `value_traceability.md` §2.7。
- `01_Plans/adr/ADR-0045-agent-division-of-labor-cowork-code-codex.md`：Cowork/Claude Code/Codex の責務分担と協働プロトコル（CP-1..6：ブランチ消失・採番衝突の恒久対策）。運用正本は `00_Prompt/agent_collaboration.md`。
- `01_Plans/adr/ADR-0046-responsiveness-performance-budget.md`：応答性の性能予算（PB-1..5：代表規模/worker化100ms基準/劣化可視化）。`ADR-0043` 認知負荷予算と対をなす計算負荷の予算。正本は `value_traceability.md` §2.8。
- `01_Plans/adr/ADR-0047-design-decision-adr-saturation-and-execution-first.md`：設計判断ADRが現段階で飽和したことの記録と、execution-first への転換・ADR再起票基準（R-1..4）。新規ADRは R-1..4 該当時のみ。
- `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`：Claude Design 壁打ち成果の採択（R-1）。D1 視覚言語(4チャネル・amber=保留/違和感予約・hypothesis=violet)／D2 コマンド到達5層＋ショートカット原則／D3 KJ法設計憲章＋関係記号(契約先行)。派生: `UX-VISUAL-01/02` `UX-CMDK-01` `UX-SHORTCUT-01` `UX-SCALE-01` `DOMAIN-KJ-01` `DOMAIN-KA-01` `DOMAIN-TRACE-01`。
- `01_Plans/documentation_quality.md`：AIエージェントが対外文書を作成する際の内部品質基準。
- `01_Plans/research-2026-07-12-trigger-ai-external-integration.md`：トリガー型AI時代の外部接続戦略リサーチ（検証済ランドスケープ＋4役割: ガラス箱共有記憶/監査・根拠層/訂正蓄積/ブリーフ堆積→意味形成）。外部接続ADR起票時の Context 参照元。
- `01_Plans/minimal-context-triage.md`：未処理ADR/issueを最小読取で抽出する手順。
- `01_Plans/triage_actionable_plans.py`：ADR/issueメタデータだけを走査して Ready/保留/関連ADR を抽出する軽量CLI。
- `01_Plans/issues/`：GitHub Issue運用を補助する短命メモ置き場。AIは triage 出力や対象Backlog IDで必要なメモだけ読む。
- `01_Plans/issues/TEMPLATE.md`：Issue補助メモの標準記述テンプレ（人間/生成AI共通）。
- `01_Plans/adr/ADR-0051-bulk-critique-reason-recording.md`：複数選択カードへの理由追記と履歴・AI非依存の扱いを定義する提案ADR。
- `01_Plans/adr/ADR-0057-w-type-cumulative-inquiry-model.md`：W型累積KJ法を任意の高度機能として扱い、段階/反復、非破壊成果、引継ぎ、分岐、永続化候補を定義する提案ADR。
- `01_Plans/issues/issue-DOMAIN-W-ITERATION-01-w-type-cumulative-inquiry-support.md`：6ラウンドの反復的探究支援を、通常利用非回帰と永続契約判断を前提に追跡するissue。
- `01_Plans/issues/issue-DX-DOC-01-crlf-markdown-fence-parser.md`：MarkdownのJSONコードブロック抽出をLF/CRLF両対応にしたテスト portability 修正。
- `01_Plans/issues/issue-UX-LABEL-01-retention-vocabulary-consistency.md`：保留・違和感・理由の画面横断ラベルを標準化するUX issue。
- `01_Plans/issues/issue-DX-E2E-02-canvas-legend-heading-drift.md`：Canvas凡例の現行見出しとE2E期待値のずれを修正したテストissue。
- `01_Plans/issues/issue-CARD-META-UI-01-card-provenance-metadata-ui-boundary.md`：カードの記録情報表示と起票者・責任主体メタデータの保存/共有境界を分離するUX・セキュリティissue。
- `01_Plans/issues/issue-UX-STATE-01-selection-target-consistency-after-bulk-island.md`：複数カードから島を作成した直後の主対象を、マウスとキーボードで一貫させるUX issue。
- `01_Plans/issues/issue-UI-QUALITY-A11Y-03-structural-aria-findings.md`：axeで検出したARIA構造の設計課題と、対応済みの見出し・コントラスト修正を追跡するissue。
- `01_Plans/adr/ADR-0052-canvas-and-menu-aria-semantics.md`：自由配置キャンバスとメニュー内フォームのARIA意味付けを決める提案ADR。
- `01_Plans/issues/issue-UX-SHARE-02-visibility-scope-plain-language.md`：viewとレビューパックの公開範囲の違いを共有前に説明するUX issue。
- `01_Plans/issues/issue-DX-E2E-03-visibility-flow-backend-fixture-portability.md`：公開範囲E2Eのfixture境界とバックエンド依存を明確にするDX issue。
- `01_Plans/issues/issue-DX-E2E-04-critique-label-assertion-drift.md`：UX-LABEL-01の正本語彙と複雑度E2E期待値のずれを修正したDX issue。
- `01_Plans/issues/issue-DX-E2E-05-first-run-start-panel-contract-drift.md`：開始パネルE2Eのimport/selector/SafeMode構造ドリフトを修正したテストissue。
- `01_Plans/issues/issue-DX-E2E-06-playwright-cli-path-portability.md`：現行依存配置に合わせてPlaywright直接実行例を可搬化したDX issue。
- `01_Plans/issues/issue-DX-E2E-07-current-ui-contract-drift-batch.md`：現行UI住所と17件のPlaywright期待値ドリフトを収束させるP1 E2E issue。
- `01_Plans/issues/issue-DX-DOC-03-healthz-runbook-endpoint-drift.md`：ADR-0019のComposeヘルス確認例を現行`/api/healthz`へ同期した文書issue。
- `01_Plans/issues/issue-DX-CI-PG-01-postgresql-ci-canonical-env-contract.md`：PostgreSQL CIが旧環境変数で全skipする偽陽性を防止したCI issue。
- `01_Plans/issues/issue-DX-AUTH-L2-01-level2-marker-and-diagnostics-contract.md`：Auth Level2 marker・診断出力・統合ハーネスを正準化したDX issue。

### 3.3 `02_Architecture/`（Structure：設計・I/F・デプロイ）

- `02_Architecture/architecture.md`：全体構成（最上位）。
- `02_Architecture/value_traceability.md`：価値→設計→受入条件→検証観点の対応表。§2.4 は プロダクト価値/UI-UX/ドメイン表現の要件被覆マトリクス（フェーズ・担当issueへの接続を1表で確認し、新規起票の要否を判定する正本）。
- `02_Architecture/contract_reading_guide.md`：02層の現行契約と履歴ログの読み分けガイド。
- `02_Architecture/contract_consolidation_inventory.md`：DOC-ARCH-02の現行契約候補・異義定義・履歴移動batchの作業inventory（契約値の正本ではない）。
- `02_Architecture/history/README.md`：freeze/Stream/checkpoint等のInformative形成履歴を現行契約から分離する収録規律と索引。
- `02_Architecture/schemas.md`：データスキーマ（document/view/pack等）。
- `02_Architecture/data_model_operations_overview.md`：MVPデータモデル、論理ER、CRUDサポート表、ステークホルダー別運用境界。
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

- `04_Documentation/public_index.md`：一般公開向け入口。Gist 等の外部共有ではこの文書を先頭にし、管理情報を含めない。
- `04_Documentation/README.md`：04文書のメンテナ向け管理入口。一般公開向け入口ではない。
- `04_Documentation/installation.md`：導入手順。
- `04_Documentation/configuration.md`：設定。
- `04_Documentation/operations.md`：運用。
- `04_Documentation/data_handling.md`：保存・外部サービスとの共有・export/share・ログ共有前確認。
- `04_Documentation/acceptance_check.md`：利用者向けの受け入れ確認。
- `03_Implement/frontend/docs/e2e_testing.md`：開発者向けのPlaywrightベースE2E方針。
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
- シェル出力が長くなりそうな確認は `00_Prompt/codex_rtk_token_saving_ops.md` に従い、RTK経由で要約する。ただし正確な全文や状態変更が必要な操作では通常コマンドを使う。
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
