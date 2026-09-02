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
- `01_Plans/adr/ADR-0033-mvp-data-support-and-maintenance-boundary.md`（MVPデータサポート境界と保守方針）
- `01_Plans/adr/ADR-0035-privileged-data-lifecycle-boundary.md`（高権限データライフサイクル操作の製品境界）

### 3.5 計画・mainline収束

- `01_Plans/adr/ADR-0034-mainline-convergence-and-branch-hygiene.md`（最新main収束とブランチ衛生の運用統治）

### 3.6 CLI 分割

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

## 8. 計画・設計文書の日本語品質

ADR、Issue補助メモ、dogfood記録、設計検討などの内部文書も、内容を正しく記録するだけでなく、後から人間が自然に読める日本語で仕上げる。

- まず内容、構造、契約、受入条件を固める。その後に、**意味や仕様を変えず、自然な日本語として全文を読み直して整える工程**を必ず通す。
- API名、スキーマ名、ファイル名、識別子、固定メタデータなど、正確な表記が必要な名称は変更しない。一方、説明文では不要な英語の断片や直訳調を避け、日本語だけでも判断の流れを追えるようにする。
- 「英語を日本語へ機械的に置き換える」ことを目的にしない。文の主語・述語・修飾関係を確認し、日本語として不自然な語順や、省略しすぎて意味が飛ぶ箇所を直す。
- 既存文書を更新した場合も、変更箇所だけでなく前後を通読し、追加文が周囲の文章から浮いていないかを確認する。
- 比較実験などで入力や文面を凍結した後は、**文体改善だけを理由に凍結済み成果物を書き換えない**。日本語品質の見直しは凍結前に行い、凍結後に必要になった修正は、実験上の逸脱または次版として明示的に扱う。
- 公開文書については、上記に加えて `01_Plans/documentation_quality.md` の品質基準を適用する。
