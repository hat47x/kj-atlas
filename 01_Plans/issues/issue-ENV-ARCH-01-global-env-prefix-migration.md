# Issue Draft: ENV-ARCH-01 グローバル環境変数プレフィックス移行計画

- Type: Process
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Platform Architecture Owner
- Scope: `02_Architecture/`, `03_Implement/backend/`, `03_Implement/deploy/`, `04_Documentation/`
- Related Backlog: N/A
- Related ADR/Spec: `ADR-0021`, `02_Architecture/runtime_parameter_registry.md`, `02_Architecture/deployment.md`
- Expected verification level: `integration`

## 1) 課題 / Problem statement

- 同一サーバ共存時、一般名の環境変数（例: `DATABASE_URL`, `API_KEY`）が他アプリと衝突し得る。
- 現行実装はプレフィックスなし前提のため、運用者がシェル/CI変数を誤注入するリスクが残る。
- 実装変更を伴う移行手順（互換期間、優先順位、廃止時期）が未定義で、着手単位が不明瞭。

## 2) 背景 / Context

- `ADR-0021` で `KJ_ATLAS_*` への段階移行方針を採用予定。
- `runtime_parameter_registry.md` はSSOTだが、移行テーブルと期限管理をまだ持たない。
- `settings.py` / `docker-compose.yml` / 各運用文書に同時反映しないと実運用で混乱が生じる。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 運用再現性と事故予防に直結し、長期保守性を改善する。
- 安全（THREAT_MODEL / SafeMode）: 変数衝突は誤接続や誤送信の温床になりうるため予防優先。
- 企業・行政要件（enterprise_architecture）: 共存環境での責務境界と監査識別性を強化する。
- 後方互換（schemas）: データスキーマ非変更。ただし設定I/F互換期間の設計が必須。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs + Backend settings + Deploy設定。
- 最小単位:
  - `runtime_parameter_registry.md` に旧→新移行表と期限を追加。
  - `settings.py` で `KJ_ATLAS_*` を正規キーとして受理し、旧キーは互換alias扱いにする。
  - `docker-compose.yml` / README / operationsを新キーへ更新。
  - テストで「新キー優先、旧キー互換、期限超過時失敗」を固定。
- 非目標:
  - 一回のPRで全周辺スクリプトを完全更新する。
  - SafeMode/認可/監査の仕様変更。

## 5) 受入条件 / Acceptance criteria

- [ ] `KJ_ATLAS_*` キーが実装上の正規キーとして定義される。
- [ ] 互換期間中、旧キーは受理されるが新キーが優先される。
- [ ] 互換期限と廃止ポリシーが registry と運用文書に明記される。
- [ ] compose/runbook/README の実行例が新キーで統一される。
- [ ] integrationレベル検証（起動 + 設定反映 + 優先順位）が再現可能なコマンドで示される。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1: 旧→新キーのマッピング表と廃止期限案を確定する。
- [ ] T2: backend settings の正規キーを `KJ_ATLAS_*` に移行し、互換aliasを実装する。
- [ ] T3: compose/README/ops文書を新キーへ更新する。
- [ ] T4: 単体/結合テストで優先順位と互換期限を固定する。
- [ ] T5: 互換廃止フェーズの実施条件（リリース条件・告知条件）を定義する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `rg -n "KJ_ATLAS_|互換|deprecation|廃止" 01_Plans/adr/ADR-0021-env-var-global-prefix-migration.md 01_Plans/issues/issue-ENV-ARCH-01-global-env-prefix-migration.md`
- 期待結果:
  - issue memo 形式検証が成功し、移行計画が具体コマンド付きで追跡可能。
- 未実施時の理由・代替検証:
  - Python未導入環境では `rg` と `git diff --check` で体裁・必須項目を代替確認する。

## 8) 代替案 / Alternatives considered

- 代替案A: 新規キーのみプレフィックスし、既存キーは維持。
  - 却下理由: 最重要リスク（既存キー衝突）を残す。
- 代替案B: 文書のみ更新し、実装は据え置き。
  - 却下理由: 実害はランタイムで発生するため、ドキュメントだけでは防げない。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 互換実装不備で起動失敗、または旧環境で設定未反映。
- 影響範囲: backend起動、deploy運用、CI設定。
- ロールバック手順: 旧キー優先モードへ一時復帰するホットフィックスを用意し、移行期限を再設定する。

## 10) Additional context

- 関連Issue/PR/議論ログ: N/A
- ADR化が必要になる条件: prefix形式（`KJ_ATLAS_`）自体を変更する要求が出た場合、または互換期間ポリシーを変更する場合。
