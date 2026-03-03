# Issue Draft: AUTH-IMPL-01 users / user_identities schema migration implementation

- Type: Feature request
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Data Schema Lead（Backend/DB）
- Scope: `03_Implement/backend/`, `02_Architecture/schemas.md`, `02_Architecture/schemas_review_attribution.md`
- Related Backlog: N/A
- Related ADR/Spec: `ADR-0020`, `issue-AUTH-SCHEMA-01-identity-schema-planning.md`, `02_Architecture/schemas.md`, `02_Architecture/schemas_review_attribution.md`
- Expected verification level: `integration`

## RACI（簡易）

| 区分 | Role |
|---|---|
| R (Responsible) | Data Schema Lead（Backend/DB） |
| A (Accountable) | Platform Architecture Owner |
| C (Consulted) | Auth Architecture Lead, Backend Lead, Compliance/Security Officer |
| I (Informed) | PM/Triage, QA Lead |

## 1) 課題 / Problem statement

- AUTH-SCHEMA-01 で決定した `users` + `user_identities` 分離を実装へ落とし込む migration 手順が未追跡。
- `reviewerRef/ownerRef = user:<users.id>` 正規化に必要な backfill と整合検証の作業順が未確定。
- 実装担当が expand/contract のどこから着手すべきか判断しづらい。

## 2) 背景 / Context

- ADR-0020 は認証境界を固定済みで、schema 論点は follow-up issue 管理に分離済み。
- AUTH-SCHEMA-01 は設計決定を完了したが、実装タスク（alembic/モデル/API読替）は別issueで追跡が必要。
- 互換性を維持するため、段階移行（expand → dual-read/write → backfill → contract）が必要。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 認証由来ユーザーの識別一貫性が欠けるとレビュー帰属と監査が破綻するため優先度高。
- 安全（THREAT_MODEL / SafeMode）: 認証境界の誤実装は誤帰属/権限混線リスクを上げる。
- 企業・行政要件（enterprise_architecture）: 監査証跡における主体同定（who did what）を担保する前提作業。
- 後方互換（schemas）: 既存 `reviewerRef` 参照を壊さない段階移行が必須。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Backend実装 + schema整合ドキュメント追随。
- 最小単位:
  - migration（DDL）
  - repository/model dual-read/write
  - backfill script
  - contract cleanup
- 非目標:
  - SCIM連携導入
  - UI上の管理画面追加
  - 認可モデル（RBAC）全面刷新

## 5) 受入条件 / Acceptance criteria

- [x] `users` / `user_identities` の migration が expand/contract 手順で定義され、ロールバック手順を含む。
- [x] `reviewerRef/ownerRef` の既存データが `user:<users.id>` へ backfill できる。
- [x] 旧経路と新経路の dual-read/write 期間を検証できるテストがある。
- [x] integration レベルの検証（docs-check + unit + DB/API結合）が実施される。

## 6) 実装タスク分解 / Task breakdown

- [x] T1: alembic で `users` / `user_identities` と制約（`UNIQUE(provider, external_uid)`）を追加する。
- [x] T2: backend model/repository を dual-read/write 対応にする。
- [x] T3: `reviewerRef/ownerRef` backfill 手順（dry-run付き）を追加する。
- [x] T4: integration test（identity 解決 + attribution 往復）を追加/更新する。
- [x] T5: contract 段階で旧参照経路の除去条件をドキュメント化する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `pytest 03_Implement/backend/tests -k "identity or attribution"`
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `rg -n "user_identities|UNIQUE\(provider, external_uid\)|reviewerRef|ownerRef" 02_Architecture/schemas.md 02_Architecture/schemas_review_attribution.md 03_Implement/backend`
- 期待結果:
  - migration/モデル/テスト/architecture参照が一致し、回帰なく integration 条件を満たす。
- 未実施時の理由・代替検証:
  - DB統合環境がない場合は sqlite 経路で migration + API往復を実行し、制約差分を記録する。

## 8) 代替案 / Alternatives considered

- 代替案A: 新スキーマへ一括切替（big bang）。
  - 却下理由: 既存帰属データの破壊リスクが高い。
- 代替案B: schema追加のみでアプリ参照は旧方式維持。
  - 却下理由: 技術的負債が固定化し、監査整合が遅延する。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: backfill 誤変換で帰属リンクが崩れる。
- 影響範囲: backend DB, API, review attribution, 運用手順。
- ロールバック手順: contract前なら dual-read/write を維持して旧参照へ戻す。migration は down script で巻き戻す。

## 10) Additional context

- 関連Issue/PR/議論ログ: N/A
- ADR化が必要になる条件: tenant境界を一意制約へ含める等、互換影響を伴う仕様変更が発生した場合。

## 11) Phase execution record（2026-03-03）

### Plan

- expand → dual-read/write → backfill → contract を固定順で実施し、contract前は旧経路へ復帰可能なことを維持。
- AC 対応表:
  - migration + rollback: `alembic/versions/20260303_0002_create_users_identities.py`
  - backfill: `kj_atlas_api/backfill_identity_refs.py`
  - dual-read/write: `auth_context.py`（旧 `x-actor-ref` と新 identity 解決の併存）
  - integration: `test_auth_jit_provisioning.py` / `test_backfill_identity_refs.py`

### Verify

- 実行コマンド:
  - `pytest 03_Implement/backend/tests -k "identity or attribution"`
  - `python 01_Plans/issues/validate_active_issue_memos.py`
- 判定:
  - AC / Task breakdown は全件達成。
  - contract 前ロールバック条件（dual-read/write 維持 + migration downgrade）を満たす。

### Proceed

- Phase 1 完了判定: **完了**。
