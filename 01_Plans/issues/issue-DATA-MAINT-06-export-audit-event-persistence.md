# Issue Draft: DATA-MAINT-06 export監査イベントの永続化設計

- Type: Design decision / Security
- Status: Draft
- Source Issue: `01_Plans/issues/issue-DATA-MAINT-05-share-export-event-lookup.md`
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/audit.py`, `03_Implement/backend/src/kj_atlas_api/routes/docs.py`, `03_Implement/backend/src/kj_atlas_api/models.py`, `02_Architecture/schemas.md`, `02_Architecture/api.md`
- Related ADR/Spec: `01_Plans/adr/ADR-0035-privileged-data-lifecycle-boundary.md`, `02_Architecture/value_traceability.md` §2.9（GENAI-GOV-01）, `01_Plans/issues/done/issue-DX-BACKEND-CE4-01-audit-tracker-unbounded-memory.md`
- Expected verification level: `integration`

## 課題

`DATA-MAINT-05`（A1: export event lookup）は、export監査イベントの **永続化** が前提である。現状の監査構成はemit-only（Noop/Http transport）で、read APIが照会できるローカル保存を持たない。ローカル唯一の監査テーブル `document_access_admin_audit_events` は `document.policy.update` のみを保持する。

exportイベントを保存するには、保存先・保持ポリシー・tenant境界・監査完全性の設計判断が必要であり、これは `ADR-0035` の監査境界と `GENAI-GOV-01`（value_traceability §2.9）の適用対象である。実装PRより先にADRまたは内部issueで確定する。

## 検討項目

- **保存先**: 新テーブル（`audit_export_events` 等） vs ローカルtransport実装 vs 既存 `document_access_admin_audit_events` の拡張。
- **保持ポリシー**: 保持期間、保持件数上限、削除手順。`ADR-0035` の本文禁止・標準機能外境界を緩和しない。
- **tenant境界**: `tenant_id` + `doc_id` の複合キーで保存し、別tenant contextからの照会を拒否する（`ADR-0059` SaaS境界と整合）。
- **監査完全性**: `DX-BACKEND-CE4-01`（CE4 tracker無制限メモリ蓄積）との関係。監査4イベント完全性チェック（query/bundle/proposal/apply）は維持しつつ、exportイベント保存と混ぜない。
- **返却allowlist**: event type, timestamp, traceId, docId, exportKind, safeMode, result, rejectReasonCode（`DATA-MAINT-04` A1）。本文・secret・生IdP識別子・policyRef生値を返さない。

## 対応方針（案）

- ADRを起票するか、`ADR-0035` の監査境界節を更新して保存設計を確定する。
- 確定後、`DATA-MAINT-05` のA1実装（read-only allowlist API）を進める。

## 受入条件

- [ ] exportイベントの保存先・保持ポリシー・tenant境界が確定し、ADRまたは契約文書に反映される。
- [ ] `DATA-MAINT-05` のA1 read APIが、保存されたイベントからallowlistのみを返す。
- [ ] 本文・未レビュー情報・secret・生IdP識別子・policyRef生値が返らないことを integration test で確認する。
- [ ] `python 01_Plans/docs_check.py` が通る。

## 検証計画

- `cd 03_Implement/backend && python -m pytest`（監査永続化・A1 readのintegration test）
- `python 01_Plans/docs_check.py`
