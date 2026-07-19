# Issue: SAAS-TENANT-CAP-01 membership_idがNoneのcontextはtenant capability解決が常に失敗する

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Bug
- Status: Done
- Lifecycle: Done
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

- 実施したこと: 公開session／Tenant Adminのcapability解決経路と`SAAS-TENANT-01`のtrusted membership再確認契約を照合し、single-tenant互換contextはcapability resolverへ渡す前に`tenant_context_untrusted`で停止する境界を確認した。この境界を直接固定する単体テストを追加した。
- 実施しないこと: `_canonical_request_identifier`へ`None`許容を追加しない。外部capability serviceへ送る`membershipId`は、DBで再確認済みのactive membershipを表すserver-owned IDとして必須であり、欠損を許容するとSaaSのfail-closed契約を弱める。

## 受入条件

- [x] single-tenant既定contextはSaaS capability解決の入力ではなく、`single_tenant_adapter`をtrusted membership evidenceとして扱わずresolver呼出し前に`403 tenant_context_untrusted`へ停止する、と明文化した。
- [x] `membership_id=None`を直接渡した外部resolverもtransport前に`TenantCapabilityUnavailableError`へ停止する既存境界を維持し、fail-closed条件を弱めていない。

## 検証計画

- 実行結果: `python -m pytest -q tests/test_tenant_capability.py tests/test_session_context.py`、backend Ruff、docs-checkを実行して成功した。
- 期待結果: single-tenant互換contextとmembership欠損contextの両方が外部transport前に停止し、capability resolverへ到達しないことを単体テストで固定した。

## 補足

- 発見経緯: SaaSテナント対応マージ後の広範な棚卸し（第4ラウンド）で発見。新設resolverの入力値検証の厳格さそのものは既存の監査・アクセス制御adapterと同等かそれ以上であることを確認済みで、本issueはセキュリティ上の脆弱性ではなく可用性境界の設計確認。
- 完了判断: `build_tenant_session_context`はcapability解決前に`recheck_trusted_tenant_context`を必須実行し、`verified_claim`／`trusted_host_mapping`以外を拒否する。したがって`LOCAL_DEFAULT_TENANT_CONTEXT`が正規の呼出経路から外部resolverへ到達することはなく、直接誤用時も既存testがtransport非実行を保証する。コード修正が必要な可用性バグではなく、意図済みのSaaS信頼境界として完了する。
