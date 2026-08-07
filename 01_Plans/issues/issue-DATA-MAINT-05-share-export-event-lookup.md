# Issue Draft: DATA-MAINT-05 監査メタデータ閲覧の初期実装（A1: share/export event lookup）

- Type: Feature request / Security
- Status: Draft
- Source Issue: `01_Plans/issues/issue-DATA-MAINT-04-metadata-only-audit-viewing.md`
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/backend/`（監査メタデータread API）, `02_Architecture/api.md`, `02_Architecture/schemas.md`
- Related ADR/Spec: `01_Plans/adr/ADR-0035-privileged-data-lifecycle-boundary.md`, `02_Architecture/api.md`, `02_Architecture/schemas.md`, `01_Plans/issues/issue-DATA-MAINT-04-metadata-only-audit-viewing.md`
- Expected verification level: `integration`

## 課題

`DATA-MAINT-04`（A1-A4候補比較）は、監査メタデータ閲覧の初期実装候補として **A1 share/export event lookup** を推奨した。共有/エクスポートの発生有無と安全境界を、**本文を含まないメタデータのみ**で確認できるようにする。

- 操作主体: Audit operator
- 目的: 共有またはexportの発生有無と安全境界を確認する
- 返してよい情報: event type, timestamp, traceId, docId, exportKind, safeMode, result, rejectReasonCode

**Stop条件（本文を返す場合）**: review pack本文、カード本文、共有先個人情報、policyRef生値。

## 対応方針

- 本文を含まない監査メタデータの read-only 一覧/検索APIを実装する（`DATA-MAINT-04` A1の範囲）。
- 返却は allowlist に限定し、本文・未レビュー情報・secret・生IdP識別子・policyRef生値を一切返さない。
- `ADR-0035` の本文禁止・標準機能外境界を緩和しない。
- Support / Platform operator が本文を標準導線で閲覧できるようにしない。

## 受入条件

- [ ] 監査メタデータ一覧/検索が、本文・未レビュー情報・secret・生IdP識別子を返さないことを integration test で確認する。
- [ ] 返却項目が allowlist（event type, timestamp, traceId, docId, exportKind, safeMode, result, rejectReasonCode）に限定される。
- [ ] 検索条件が本文語句を受け付けない。
- [ ] SafeMode、`human_reviewed`、外部共有条件を緩和しない。
- [ ] `02_Architecture/api.md` / `schemas.md` に契約を先行固定する。
- [ ] `python 01_Plans/docs_check.py` が通る。

## 検証計画

- backend integration test（監査メタデータread、本文非返却のnegative test）
- `cd 03_Implement/backend && python -m pytest`
- `python 01_Plans/docs_check.py`

## 補足

- A2（CE4監査完全性）、A3（access-control判定レビュー）、A4（Support照合）は、本A1実装後に実運用知見が出てから別issueへ分割する（`DATA-MAINT-04` の方針）。
- UIは本issueの範囲外。`DATA-MAINT-04` は「APIまたはCLI優先、UIは後続」と定めている。
