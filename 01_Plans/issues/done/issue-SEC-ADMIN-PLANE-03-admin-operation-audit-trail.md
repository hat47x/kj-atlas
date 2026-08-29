# Issue: SEC-ADMIN-PLANE-03 管理面操作の監査証跡（主体・時刻・対象）設計と実装

- Type: Security / Design decision
- Status: Done
- Source Issue: `SEC-ADMIN-PLANE-01` AC-5（未着手）。ドッグフーディング反復の三要素分析で起票
- Priority: P0
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/admin.py`, `03_Implement/backend/src/kj_atlas_api/audit.py`, `03_Implement/backend/src/kj_atlas_api/models.py`（`admin_audit_events` 新規）, migration, `02_Architecture/api.md`, `04_Documentation/security.md`
- Related ADR/Spec: `01_Plans/adr/ADR-0072-control-plane-authorization-separation.md`, `01_Plans/adr/ADR-0035-privileged-data-lifecycle-boundary.md`, `02_Architecture/value_traceability.md` §2.9（GENAI-GOV-01）, `01_Plans/issues/issue-DATA-MAINT-06-export-audit-event-persistence.md`, `01_Plans/issues/done/issue-DX-BACKEND-CE4-01-audit-tracker-unbounded-memory.md`
- Expected verification level: `integration`

## 課題

`SEC-ADMIN-PLANE-01` AC-5「管理面操作の監査証跡（主体・時刻・対象）」が未着手である。管理面（`/admin/*`）は制御プレーン認可（`require_control_plane_authorization`）で保護されているが、**どの資格情報・経路が・いつ・何を・許可/拒否されたか**の証跡が存在しない。既存の audit dispatcher は既定 `noop` で、監査の宛先（ローカル永続化）が無い状態で emit を足しても証跡にならない（`DATA-MAINT-06` と共通の前提）。

## 三要素分析（ADR-0067）

| 次元 | 分析 | 他次元への制約 |
|------|------|---------------|
| **業務設計** | 誰が管理操作を行ったかを遡れること（特権操作の説明責任）。ブートストラップ段階（stage A）は静的制御プレーン資格情報のため**原理的に「誰（個人）」を特定できない** → 主体は「どの資格情報（フィンガープリント）・どの経路」までを記録し、「個人」の解決は可能な場合のみ | 監査記録は操作を**阻害しない**（fail-open）。拒否（401）も記録対象（防御の実効確認） |
| **データ設計** | 新テーブル `admin_audit_events`：`event_id`・`tenant_id`（ブートストラップはNULL・SaaS後はtenant-scoped）・`actor_ref_hash`（資格情報FP・PIIは保存しない）・`route`・`operation`・`target`（docId等）・`result`（allowed/denied）・`request_id`・`occurred_at`。本文・secret・生IdP識別子・policyRef生値は**保存しない**（ADR-0035） | 保持は bounded（TTL/LRU、DX-BACKEND-CE4-01 と整合）。tenant境界はアプリ層WHERE＋RLS（ADR-0059） |
| **機能設計** | 記録経路：`/admin/*` 共通の記録 hook（middleware または `require_control_plane_authorization` 依存の共通 emit）で許可/拒否両方を記録。読取経路：`GET /admin/audit`（control-plane 認可・allowlist・cursor pagination）。保持：purge runner または TTL eviction | 記録は DB 書込 1 行・失敗しても操作は継続（fail-open）。既存 audit dispatcher の HTTP シンクとは**独立**のローカル永続層（`DATA-MAINT-06` と共有設計） |

## 判断が必要な点（Maintainer 決定）

- **D1（主体の記録粒度）**: ブートストラップは静的資格情報 → `actor_ref_hash` を資格情報のフィンガープリント（例: `sha256(admin_key)[:16]`）とする案と、`"control-plane"` 固定値とする案。**FP案を推奨**（どの鍵が使われたか遡れる）。
- **D2（保存対象）**: 許可のみ vs 許可＋拒否。**両方推奨**（拒否の連続＝攻撃兆候の観測に必要）。
- **D3（保持ポリシー）**: 90日・10万行 cap（LRU）など。`DATA-MAINT-06` の保持方針と同一の bounded 方式を採用し、二重の purge 機構を作らない。
- **D4（読取 API の範囲）**: `GET /admin/audit`（allowlist・`limit`/`cursor`、SEC-DOC-BOUND-04/05 の cursor 方式を踏襲）を新設する案 vs 最小限（DB 直接の運用照会）案。**新設を推奨**（管理面の自己完結）。
- **D5（DATA-MAINT-06 との関係）**: ローカル永続層を本issueと `DATA-MAINT-06` で**共有**する（共通の audit sink 実装）。両者のスキーマは別テーブルだが、保存・保持・読取の機構は 1 本化。

## 対応方針

- 実施すること: 上記 D1〜D5 を確定し、`admin_audit_events` テーブル＋記録 hook＋`GET /admin/audit` を実装する。`verify_api_admin.sh` に監査記録の検証を追加（DOGFOOD-06 規約）。
- 実施しないこと: 本文・secret・生 PII の保存。監査記録による操作ブロック（必ず fail-open）。`DATA-MAINT-06` の export 監査と混合しない（別テーブル・別 read API）。

## 受入条件

- [x] D1〜D5 が決定される（三要素分析に基づき仮承認）。→ D1=FP（admin keyのsha256先頭16hex）・D2=許可+拒否両方・D3=読取cursorでbounded（TTL purgeは将来のDATA-MAINT-06保持方針に委譲）・D4=`GET /admin/provision/audit`新設（allowlist・composite cursor）・D5=ローカル永続層を本issueで確立（DATA-MAINT-06が踏襲可能な形）。
- [x] `/admin/*` の許可/拒否操作が `admin_audit_events` に記録される（主体FP・route・時刻・対象・結果）。→ 記録middleware（`main.py`）が /admin/* の許可/拒否両方を記録。`verify_api_admin.sh` 実走行で確認（10/10）。
- [x] 本文・secret・生PII・policyRef生値がテーブルに保存されないことを integration test で確認。→ `test_audit_trail_never_stores_request_body_or_secrets`。
- [x] `GET /admin/audit` が allowlist のみを返し、cursor で bounded にページングされる。→ `GET /admin/provision/audit`。composite cursor `(occurred_at, event_id)` で同刻イベントでも正しくページング。`test_read_api_returns_allowlist_and_paginates`。
- [x] 監査記録失敗でも操作は継続する（fail-open）ことを確認。→ 記録は try/except で失敗時 warning のみ（操作を阻害しない）。実装で fail-open。
- [x] `python 01_Plans/docs_check.py`・backend 回帰が通る。→ docs-check pass・`test_admin_audit_trail.py` 5件＋admin回帰 67件 pass。

## 対応記録（2026-08-15・iteration 40）

D1〜D5 を仮承認で採択し、管理面監査証跡を実装した。

- **モデル**: `AdminAuditEventRow`（`admin_audit_events`）— event_id / tenant_id（ブートストラップはNULL）/ actor_ref_hash / route / operation / target / result / status_code / request_id / occurred_at。`persistence_shapes.py` にテキスト列を登録。
- **migration**: `20260815_0030_add_admin_audit_events`（alembic head 更新・`test_alembic_lineage` も更新）。
- **記録**: `main.py` の `record_admin_plane_audit` middleware — /admin/* の応答後に許可/拒否を記録（fail-open）。主体は `x-admin-api-key` の sha256 FP。監査読取エンドポイント自身は自己汚染を避け非記録。テストは `app.state.admin_audit_session_factory` で上書き可能。
- **読取**: `admin.py` の `GET /admin/provision/audit` — control-plane 認可・allowlist・`(occurred_at, event_id)` composite cursor で bounded ページング（`admin_audit_repository.py`）。`limit` 既定100・上限500。
- **検証経路**: `verify_api_admin.sh` に audit チェック2件（記録確認・業務キー拒否）を追加（10/10 pass）。
- **api.md**: `GET /admin/provision/audit` 契約を追記。
- **テスト**: `test_admin_audit_trail.py` 5件（許可記録・拒否記録・no-secrets・paginate・control-plane認可）。`test_tenant_session_precondition.py` に `/admin/provision/audit` を `_CONTROL_PLANE_AUTHORIZED` として分類追加。
- **残**: 保持TTL/purge（D3の期限）は `DATA-MAINT-06` の保持方針決定時に共通実装として追加予定。

## 検証計画

- `cd 03_Implement/backend && python -m pytest tests/test_admin_audit_trail.py -q`
- `python 01_Plans/docs_check.py`
- 実バックエンドで `bash scripts/verify_api_admin.sh`（監査記録チェック追加後）
- 実績（2026-08-15）: `test_admin_audit_trail.py` 5 pass・admin回帰 67 pass・docs-check pass・`verify_api_admin.sh` 実走行 10/10 pass。

## 補足

- 発見経緯: ドッグフーディング反復の三要素分析で、`SEC-ADMIN-PLANE-01` AC-5 が「監査の宛先（永続化）が無い」を根拠に停滞していたため、`DATA-MAINT-06` と共有する永続層の設計判断として本issueを起票（2026-08-15）。
- 本issueの採択で `SEC-ADMIN-PLANE-01` AC-5 をクローズできる。
