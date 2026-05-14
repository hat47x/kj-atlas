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

### 3.4 製品化・価値実現

- `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`（UI操作性・段階的開示）
- `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`（製品化画面情報設計）
- `01_Plans/adr/ADR-0032-product-value-realization-model.md`（プロダクト価値実現モデル）

### 3.5 CLI 分割

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

- 作業開始時の一次導線は `01_Plans/minimal-context-triage.md` と `python 01_Plans/triage_actionable_plans.py` を正本とする。
- `01_Plans/issues/README.md` は issue memo 運用ルールの参照先とし、一覧の再読を前提にしない。
- 個別 issue memo は triage 出力、対象Backlog ID、または関連ADRから必要最小限だけ開く。
- 運用ルールの詳細は `01_Plans/adr/ADR-0000-adr-governance.md` の「Issue補助メモのライフサイクル／配置・管理規約」を参照する。
- 対外文書の内部品質基準は `01_Plans/documentation_quality.md` を参照する。
