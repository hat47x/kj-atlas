# Issue Draft: SAAS-TENANT-SURFACE-01 frontend呼び出しを持たないtenant-guarded backend routeが9件

- Type: Process
- Status: Draft
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/docs.py`, `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/backend/src/kj_atlas_api/routes/context.py`
- Related ADR/Spec: `01_Plans/issues/issue-SAAS-TENANT-01-tenant-context-and-storage-foundation.md`
- Expected verification level: `docs-check`

## 課題

SAAS-TENANT-01の2件の監査（2026-08-06、backend全routeの網羅性監査とfrontend全fetch呼び出し箇所の監査）を突き合わせた結果、以下9件のtenant-guarded backend routeに対応するfrontend呼び出しが `03_Implement/frontend/src` 内に一切見つからなかった。

- `POST /docs/{doc_id}/context-audit`
- `merge-decision-logs` 系 3 route
- `similar-candidate-groups`
- `polygon-handoff/verify-contract`
- `POST /ai/suggest-island-summary`
- `/context/*` 4 route

いずれもbackend側の認可境界（`_authorize_request`／`require_tenant_scoped_api_precondition`）は正しく適用されており、セキュリティ上の穴ではない。

## 論点（人的判断が必要な理由）

未分類のAPI面である可能性が複数あり、コードだけでは判別できない。

(a) 死んだコード（過去に使われていたが、frontend側の実装変更で呼び出し元が消えた）。
(b) 外部消費者向け（MCP、将来のAgent連携等、frontend以外からの呼び出しを想定した契約）。
(c) 未実装のfrontend機能（backend契約は先行して用意されているが、対応するUIがまだない）。

判断によって対応が変わる: (a)なら削除候補としてDX-CLEANUP系issueへ、(b)ならcontractとして`api.md`に「外部消費者向け」と明記、(c)なら実装待ちのバックログとして扱う。

## 影響

低リスク（認可は正しく機能している）。ただし、使われていない、あるいは意図が不明なAPI面は、将来の変更時にテスト漏れや意図しない振る舞いを生みやすく、SAAS-TENANT-01のようなセキュリティ監査のたびに「本当に全部把握できているか」の確認コストを生む。

## Acceptance

- [ ] 9 routeそれぞれについて、(a)/(b)/(c)のいずれかに分類する。
- [ ] (a)と判定したものは別issueとして削除を検討する。
- [ ] (b)と判定したものは`api.md`へ「外部消費者向け」である旨を明記する。

## Validation

- 分類結果を本issueまたは`api.md`へ記録する。
