# Issue: SEC-HTTP-02 tenant切替で同一の「membership非activeチェック」が403と404に分岐

- Type: Security
- Status: Draft
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/tenant_context.py`, `03_Implement/backend/src/kj_atlas_api/session_context.py`
- Related ADR/Spec: `02_Architecture/api.md:406,720`, `ADR-0059-saas-tenant-authorization-boundary.md`
- Expected verification level: `unit`

## 課題

- 現在の問題: `tenant_context.py:95-129`の`_active_membership_context`は、「user・tenant・membershipがすべてactiveか」という単一の判定を、呼び出し元が渡す`unavailable_status`引数（`"forbidden"`または`"not_found"`）に応じて`403`（`tenant_membership_inactive`）または`404`（`tenant_not_available`）のどちらかに変換する。`session_context.py`の`switch_tenant_session_context`（`POST /session/active-tenant`の実処理）は、同一関数内で、呼び出し元（現在のtenant）に対しては`recheck_trusted_tenant_context`経由で403、切替先（要求されたtenant）に対しては`select_active_tenant_context`経由で404という、全く同じ判定条件に対して異なるステータスコードを返す。
- 判断が必要な理由: `api.md:720`は「不明tenant・他利用者のtenant・停止membershipは存在を推測させない404相当とする」と、切替**先**tenantについてのみ明示的にanti-enumeration方針を定めている。現在のtenantに対する403は`api.md:406`の一般的な認可境界違反の方針と整合するが、両者を意図的なペアとして文書化した記述はない。これが「切替先だけ列挙攻撃を防ぐ意図的な設計」なのか「単なる実装の不統一」なのかは、セキュリティ上の意図を確認しないと判断できない。
- 利用者または開発への影響: 実害は不明。誤って統一すると、意図的なanti-enumeration保護を破壊する可能性がある。

## 対応方針

- 実施すること: 現在のtenantに対する403と、切替先tenantに対する404の使い分けが意図的な設計かどうかをMaintainerが確認し、意図的であれば`api.md`にペアとして明記する。単なる不統一であれば、どちらか一方に揃える。
- 実施しないこと: どちらか一方への機械的な統一。anti-enumeration方針を誤って破壊するリスクがあるため、セキュリティ判断を経ずに変更しない。

## 受入条件

- [ ] 403/404の使い分けが意図的か否かが確認される。
- [ ] 意図的な場合、`api.md`にその設計意図が明記される。

## 検証計画

- 実行する確認: 対応後、`python3 -m pytest`（backend、tenant切替関連テスト）。
- 期待結果: 既存のtenant切替テストが新しい方針と整合する。

## 補足

- 発見経緯: 第12ラウンドの棚卸し（HTTPステータスコード一貫性観点）で発見。
