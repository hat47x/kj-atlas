# Issue: SAAS-TENANT-CAP-01 membership_idがNoneのcontextはtenant capability解決が常に失敗する

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Bug
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/tenant_capability.py`
- Related ADR/Spec: `01_Plans/issues/issue-SAAS-TENANT-01-tenant-context-and-storage-foundation.md`
- Expected verification level: `unit`

## 課題

- 現在の問題: `TenantContext.membership_id`は`str | None`型であり、`LOCAL_DEFAULT_TENANT_CONTEXT`（`resolve_single_tenant_context`が`user_id is None`で呼ばれた場合に返るsingle-tenant既定context）では実際に`membership_id=None`になる。既存の`ExternalPolicyAccessControlAdapter`（`access_control.py`）は`_validate_policy_request_string(request.tenant.membership_id)`をデフォルト`optional=True`で呼び出しており、`None`を正しく許容する。しかし新設の`ExternalHttpTenantCapabilityResolver`（`tenant_capability.py`）の`_canonical_request_identifier(value: str | None)`は`optional`引数を持たず、`None`を渡すと無条件に例外を送出する。`tenant_capability.py`は`tenant.membership_id`をそのままこの関数へ渡している。
- 利用者または開発への影響: `KJ_ATLAS_TENANT_CAPABILITY_RESOLVER=external_http`を設定した状態で、single-tenant既定contextから本resolverが呼び出されると、実際のHTTP呼び出しに至る前に必ず`TenantCapabilityUnavailableError`で失敗する。これがバグなのか、意図的な境界（single-tenant既定contextではtenant capability解決自体を想定しない設計）なのかは、呼び出し経路の全体設計を把握していないと判断できない。

## 対応方針

- 実施すること: single-tenant既定context（`membership_id=None`）からtenant capability解決が呼ばれる経路が実際に存在するかを確認し、存在する場合は`_canonical_request_identifier`に`access_control.py`と同様の`optional`許容パスを追加するかどうかを判断する。
- 実施しないこと: `_canonical_request_identifier`の変更そのもの。single-tenant既定contextでこのresolverが呼ばれることを想定しているかどうかは製品設計判断であり、本issueでは先取りしない。

## 受入条件

- [ ] single-tenant既定contextからのtenant capability解決呼び出しについて、意図した挙動（fail-closedのまま/Noneを許容する）が明文化される。
- [ ] 実装変更を行う場合、既存のfail-closed境界（不正・不完全設定時は必ず拒否）を弱めない。

## 検証計画

- 実行する確認: 方針決定後、`python3 -m pytest tests/`で関連テストがgreenであることを確認する。
- 期待結果: 意図した挙動が単体テストで固定される。

## 補足

- 発見経緯: SaaSテナント対応マージ後の広範な棚卸し（第4ラウンド）で発見。新設resolverの入力値検証の厳格さそのものは既存の監査・アクセス制御adapterと同等かそれ以上であることを確認済みで、本issueはセキュリティ上の脆弱性ではなく可用性境界の設計確認。
