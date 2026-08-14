# Issue: SEC-AUTH-ATTRIB-01 クライアント供給の x-auth-roles / x-auth-groups が外部PDPへ転送される

- Type: Security
- Status: In Progress
- Source Issue: `QA-TENANT-ISOLATION-01` の周辺観測（別issue化推奨）
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/docs.py`（`_authorize_request`）
- Related ADR/Spec: `01_Plans/adr/ADR-0059-saas-tenant-authorization-boundary.md`, `01_Plans/adr/ADR-0063-saas-multitenant-trusted-auth-edge.md`, `THREAT_MODEL.md`
- Expected verification level: `integration`

## 課題

`_authorize_request`（`routes/docs.py:278-279`）は、リクエストヘッダ `x-auth-roles` / `x-auth-groups` をそのまま `AuthContext.roles` / `groups` へ入れ、外部HTTP PDP（`external_http` adapter）へ転送する。

```python
roles=parse_csv_header(request.headers.get("x-auth-roles")),
groups=parse_csv_header(request.headers.get("x-auth-groups")),
```

`access_control.py:290-291` がこれを PDP リクエストの `"roles"` / `"groups"` として送る。

- 単一tenant（`resolve_identity_context`）も SaaS（`trusted_auth_edge.py` の JWT resolver）も、AuthContext の roles/groups は**空**で構築される。したがって `x-auth-roles` ヘッダは、サーバがPDPへ渡す**唯一のroles供給源**である。
- クライアントは任意の値を自由に送れるため、外部PDPが roles/groups を認可判断に使う場合（例: `role=admin` → allow）、**テナント内の権限昇格**が可能になる（tenant 境界 guard は PDP より先に走るため越境は防がれるが、テナント内の昇格は防がれない）。
- 既定 adapter は `noop`（全許可・local-dev）だが、`external_http`（enterprise-production / saas-multitenant）では実質的な影響がある。

## 対応方針

- 実施すること（D-a）:
  1. **クライアントヘッダからの roles/groups 読取をやめる**。`_authorize_request` は `identity.auth_context.roles` / `.groups`（検証済みidentity由来）を使う。
  2. 現状は単一tenant・SaaSとも roles/groups が空のため、PDP へは空で送る（fail-closed — サーバが検証できない属性を主張しない）。
  3. 将来、roles をサーバ側で導出する場合は、JWT claim またはプロビジョン済み user のロールを正本にする（別issue）。
- 実施しないこと:
  1. `external_http` PDP の要求仕様変更（PDP 側は「サーバが検証した属性」のみ受け取る前提へ）。
  2. 単一tenant で roles をヘッダから許容し続ける。

## 受入条件

- [x] AC-1: `_authorize_request` が `x-auth-roles` / `x-auth-groups` を読み取らない。
- [x] AC-2: PDP へ送る `roles` / `groups` が空（検証済みidentity由来のみ）。
- [x] AC-3: 既存テストが更新され、クライアント供給rolesがPDPに到達しないことを固定する。

## 検証

- `python -m pytest tests/test_docs_access_control_integration.py tests/test_docs_roundtrip.py -q`
- `python 01_Plans/docs_check.py`

## 対応記録（2026-08-14）

D-a を実装した。

- `routes/docs.py::_authorize_request`: `roles=identity.auth_context.roles` / `groups=identity.auth_context.groups` へ変更し、クライアントヘッダ読取を削除（`parse_csv_header` import も削除）。
- テスト: `CapturingAdapter` を追加し、クライアント供給 `x-auth-roles` / `x-auth-groups` が PDP へ到達しない（roles/groups が空）ことを固定。
- 既存の roles/groups ヘッダ送信テスト（`test_adapter_denial_prevents_role_header_privilege_escalation` 他）はすべて PASS（403 断言のため挙動不変）。
- 単一tenant・SaaSとも roles/groups は空のため fail-closed（PDP は検証済み属性のみ受領）。回帰 85 tests pass。
