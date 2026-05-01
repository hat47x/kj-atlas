# Issue Draft: AUTH-API-02 strict provisioning contract and admin API implementation

- Type: Feature request
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Auth Architecture Lead（Security/Identity）
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/`, `02_Architecture/api.md`, `04_Documentation/security.md`
- Related Backlog: N/A
- Related ADR/Spec: `ADR-0020`, `issue-AUTH-ARCH-01-authcontext-jit-provisioning-data-boundary.md`, `02_Architecture/api.md`, `02_Architecture/review_attribution.md`
- Dependencies: N/A
- Expected verification level: `integration`

## RACI（簡易）

| 区分 | Role |
|---|---|
| R (Responsible) | Auth Architecture Lead（Security/Identity） |
| A (Accountable) | Platform Architecture Owner |
| C (Consulted) | Backend Lead, Compliance/Security Officer |
| I (Informed) | PM/Triage, QA Lead |

## 1) 課題 / Problem statement

- strict mode（`ALLOW_JIT_PROVISIONING=false`）時の `403 + code=identity_not_provisioned` 契約が実装追跡されていない。
- `POST /admin/provision/users` を正本契約として定義したが、実装/運用ドキュメントの紐付けが不足。
- 運用者が「拒否時に何を実行すれば解消できるか」を迷う状態。

## 2) 背景 / Context

- AUTH-ARCH-01 で strict mode の責務境界（API正本、CLIはラッパ）を決裁済み。
- AUTH-SCHEMA-01 で 403 エラーコード最小契約を決裁済み。
- API設計と backend route 実装、運用ドキュメントを同一粒度で追跡する必要がある。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 認証失敗時の回復導線が明確でないと導入障壁が高い。
- 安全（THREAT_MODEL / SafeMode）: 未登録主体を許可しない strict 動作は最重要の安全境界。
- 企業・行政要件（enterprise_architecture）: 事前プロビジョニング運用は監査可能な管理導線が前提。
- 後方互換（schemas）: 既定ON/OFF切替時の API 応答契約を破らず段階導入が必要。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Backend API + Architecture/Ops docs 同期。
- 最小単位:
  - strict拒否ハンドラの実装
  - `POST /admin/provision/users` の最小契約実装
  - 監査ログ/エラーコード整備
- 非目標:
  - フルSCIM実装
  - 管理UI実装
  - IdP製品固有ロジックの追加

## 5) 受入条件 / Acceptance criteria

- [x] strict mode + 未登録subject で `403` と `identity_not_provisioned` を返す。
- [x] `POST /admin/provision/users` の最小入力/応答/冪等性が文書と実装で一致する。
- [x] CLI（存在する場合）はAPIラッパとして同一契約を使用し、独自分岐を持たない。
- [x] integration レベルのテストで許可経路・拒否経路・再試行経路を確認する。

## 6) 実装タスク分解 / Task breakdown

- [x] T1: strict mode 判定ロジックとエラーコード（`identity_not_provisioned`）を実装する。
- [x] T2: 管理者プロビジョニング API の request/response schema を固定する。
- [x] T3: API route test（403/200/409 等の境界）を追加する。
- [x] T4: `02_Architecture/api.md` と `04_Documentation/security.md` を同期更新する。
- [x] T5: RACI-I 通知テンプレを PR本文へ適用し、Status変更トリガーを記録する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `pytest 03_Implement/backend/tests -k "provision or auth or strict"`
  - `curl -fsS http://localhost:8000/healthz`
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `rg -n "identity_not_provisioned|/admin/provision/users|ALLOW_JIT_PROVISIONING" 02_Architecture/api.md 04_Documentation/security.md 03_Implement/backend/src/kj_atlas_api`
- 期待結果:
  - strict拒否契約と管理導線が docs/API実装/テストで一致する。
- 未実施時の理由・代替検証:
  - ローカルAPI起動不能時は test double で route 単体テストを先行し、未実施理由をPRに残す。

## 8) 代替案 / Alternatives considered

- 代替案A: strict mode でも未登録subjectを自動作成する。
  - 却下理由: 決裁済み安全境界に反する。
- 代替案B: 管理導線をCLI専用にする。
  - 却下理由: API正本方針と監査一貫性を損なう。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 誤判定により正当ユーザーを拒否、または未登録ユーザーを許可。
- 影響範囲: backend auth route, 運用手順, 監査証跡。
- ロールバック手順: feature flag (`ALLOW_JIT_PROVISIONING`) により運用回避し、直前安定版へ戻す。

## 10) Additional context

- 関連Issue/PR/議論ログ: N/A
- Source Issue記載方針: GitHub Issues正本運用の開始宣言までは `N/A` を維持し、開始宣言後の次回更新PRで対応URLへ切替する。
- ADR化が必要になる条件: strict mode の拒否コード体系を複数化する等、外部契約へ互換影響が出る場合。

## 11) Phase execution record（2026-03-03）

### Plan

- strict拒否契約（`403` + `identity_not_provisioned`）と `POST /admin/provision/users` 契約を API正本として固定。
- AC 対応表:
  - strict拒否/許可/再行: `auth_context.py` + `test_auth_jit_provisioning.py`
  - provisioning request/response/冪等性: `routes/admin.py` + `02_Architecture/api.md`
  - docs同期: `02_Architecture/api.md` / `04_Documentation/security.md`
  - CLI方針: API正本（CLI はラッパ）を architecture/security 文書に固定

### Verify

- 実行コマンド:
  - `pytest 03_Implement/backend/tests -k "provision or auth or strict"`（auth_level2 の外部SP未起動ケースを除き契約テストは通過）
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `rg -n "identity_not_provisioned|/admin/provision/users|ALLOW_JIT_PROVISIONING" 02_Architecture/api.md 04_Documentation/security.md 03_Implement/backend/src/kj_atlas_api`
- 判定:
  - strict境界は維持され、運用回避手段として `ALLOW_JIT_PROVISIONING` フラグが残存。
  - docs / 実装 / テストの契約差分はなし。

### Proceed

- Phase 2 完了判定: **完了**（Phase 1 完了後に着手）。

## 12) Follow-up execution record（API/Schema contract refinement, docs-only）

### Plan（AC/DoD補完ドラフト）

- AC-1: `02_Architecture/api.md` に strict拒否と admin provisioning の **型契約**（request/success/conflict）を明示する。
- AC-2: `02_Architecture/schemas.md` に上記契約と整合する **最小分岐キー**（status/code/provisioned）を明示する。
- AC-3: 依存先実装が mock 追従可能な最小契約（必須キー最小・追加キー許容）を定義する。
- DoD: 実装変更なしで、API正本とSchema正本の I/F 記述が相互参照なしで解釈可能。

### Execute

- docsのみ更新（`02_Architecture/api.md`, `02_Architecture/schemas.md`）。
- 実装ファイル（`03_Implement/*`）の変更は行わない。

### Verify

- `rg` で `identity_not_provisioned` / `identity_already_provisioned_conflict` / `provisioned` の3軸が API+Schema 双方に存在することを確認。
- mock観点: 分岐に必要なキーを `status` + `code` + `provisioned` に限定したため、test double での追従が可能。

## Stream I Done/Completed Audit (2026-04-23)
- 判定: 再オープン不要（Done/Completed/Closedの完了根拠と整合）。
- Related ADR/Spec: 参照先リンク切れなし（存在確認済み）。
- 重複Backlog: 該当なし。

## Stream E serial execution log (2026-05-01)

- Phase 1 Read同期: AUTH-SCHEMA-01 の strict 契約（`identity_not_provisioned`）を前提に API/IMPL 依存を確認。
- Phase 2 ADR/CDC: 未承認仕様の確定化は行わず、既存契約の追認に限定。
- Phase 3 Plan: AC/DoD 不足なし。mock追従キー（`status`/`code`/`provisioned`）を境界として固定。
- Phase 4 Execute: Stream E の固定順序 3/5（API/IMPL）を完了。
- Phase 5 Verify: strict拒否・管理者導線・API正本/CLIラッパ方針に矛盾なし。
- Phase 6 Proceed: **Go**（E2Eフェーズへ進行）。

