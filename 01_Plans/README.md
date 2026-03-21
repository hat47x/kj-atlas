# 01_Plans ADR Index

`01_Plans` 配下の要件・計画は、すべて `01_Plans/adr/` の ADR で管理する。
本ファイルは **読む順番と目的別参照先を示すインデックス** として機能する。

## 1. まず最初に読む（必須）

1. ADR運用ルール
   - `01_Plans/adr/ADR-0000-adr-governance.md`
2. 価値→要件の統合ビュー
   - `01_Plans/adr/ADR-0001-value-to-requirements.md`
3. 内部ロードマップ（全体進行）
   - `01_Plans/adr/ADR-0002-internal-roadmap.md`

## 2. フェーズ計画を読む

- Phase 0: `01_Plans/adr/ADR-0003-phase0-bootstrap.md`
- Phase 1: `01_Plans/adr/ADR-0004-phase1-canvas-mvp.md`
- Phase 2: `01_Plans/adr/ADR-0005-phase2-qualitative-integration.md`
- Phase 3: `01_Plans/adr/ADR-0006-phase3-review-governance.md`
- Future backlog: `01_Plans/adr/ADR-0007-future-backlog.md`
- CLI plan: `01_Plans/adr/ADR-0008-cli-tooling-plan.md`
- Local LLM plan: `01_Plans/adr/ADR-0009-local-llm-integration.md`

## 3. 粒度分割ADR（詳細を読むとき）

以下は粗粒度ADRを分割した詳細ADR。仕様レビューや更新時はこちらを優先参照する。

### 3.1 価値・要件・起票

- `01_Plans/adr/ADR-0010-values-principles.md`（価値原則）
- `01_Plans/adr/ADR-0011-requirements-mapping.md`（価値→要求マッピング）
- `01_Plans/adr/ADR-0012-planning-ticketing-rules.md`（フェーズ運用/チケット化）

### 3.2 Phase2 分割


- `01_Plans/adr/ADR-0013-phase2-requirements-split.md`（要求・データ/UI影響）
- `01_Plans/adr/ADR-0014-phase2-acceptance-rollout-split.md`（受入基準・段階導入）

### 3.3 運用分割

- `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`（E2E確認方針）
- `01_Plans/adr/ADR-0021-env-var-global-prefix-migration.md`（環境変数プレフィックス移行方針）

### 3.4 CLI 分割

- `01_Plans/adr/ADR-0015-cli-scope-phasing.md`（対象範囲・段階導入）
- `01_Plans/adr/ADR-0016-cli-command-contract.md`（コマンド体系・共通I/F）
- `01_Plans/adr/ADR-0017-cli-security-ops-checks.md`（セキュリティ/運用受入）

## 4. 目的別クイックナビ

- 「価値判断の根拠を確認したい」
  - `ADR-0001` → `ADR-0010` / `ADR-0011`
- 「実装フェーズの受入条件を確認したい」
  - `ADR-0002` と該当 `ADR-0003`〜`ADR-0009`
- 「Phase2の要求とリリース判定を分けて確認したい」
  - `ADR-0013` / `ADR-0014`
- 「CLI仕様と運用条件を分けて確認したい」
  - `ADR-0016` / `ADR-0017`

## 5. ADR更新時の注意

- 新しい主要計画を追加したら、この README に必ず追記する。
- ADRを分割した場合は、
  - 親ADRに分割先を追記
  - この README の「粒度分割ADR」に分割先を追記
- 廃止ADRが出た場合は、`Superseded by` を明記し、インデックスの参照先も更新する。


## 6. ADR作成テンプレート

- 新規ADR作成時は `01_Plans/adr/TEMPLATE.md` を起点にする。
- Proposed -> Accepted への更新時は、Decision/Consequences/Traceability の差分が追跡できるよう追記優先で更新する。

## 7. Issue補助メモ運用（Action管理）

- `01_Plans/issues/README.md` を issue補助メモ一覧と作業開始手順の正本とする。
- `01_Plans/README.md` は導線のみを保持し、個別Issue運用ルールの本文は `01_Plans/issues/README.md` に集約する。
- Active（Draft/Open/In Progress）のみ `01_Plans/issues/README.md` に掲載し、Done は削除（必要時のみ archive）する。
- 運用ルールの詳細は `01_Plans/adr/ADR-0000-adr-governance.md` の「Issue補助メモのライフサイクル／配置・管理規約」を参照する。
- 未処理ADR/issueの最小読取手順は `01_Plans/minimal-context-triage.md`、機械抽出は `python 01_Plans/triage_actionable_plans.py` を正本とする。
