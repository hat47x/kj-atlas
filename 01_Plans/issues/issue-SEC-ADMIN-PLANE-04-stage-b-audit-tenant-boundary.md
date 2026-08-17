# Issue: SEC-ADMIN-PLANE-04 Stage-B管理監査の主体・テナント属性欠落と越境読取

- Type: Security / Authorization
- Status: Done
- Source Issue: 管理UI・CLI・API・MCP協調モンキーテスト（2026-08-17）
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/control_plane_auth.py`, `03_Implement/backend/src/kj_atlas_api/main.py`, `03_Implement/backend/src/kj_atlas_api/admin_audit_repository.py`, `03_Implement/backend/src/kj_atlas_api/routes/admin.py`
- Related ADR/Spec: `ADR-0072`, `SEC-ADMIN-PLANE-03`, `ADR-0059`
- Expected verification level: `integration`

## 課題

Stage-Bの`tenant.provision` capabilityで管理操作は許可されるが、認証依存がtrusted sessionを真偽値へ潰していた。そのため監査行の`actor_ref_hash`と`tenant_id`がNULLとなり、誰がどのテナントで操作したか追跡できなかった。

さらに監査一覧は「tenant-scoped rows are already scoped」と説明していた一方、repository queryにtenant条件がなく、Stage-Bのテナント管理者が他テナントとbootstrapの監査メタデータを取得できた。応答からtenant ID自体を省いても、route、時刻、結果、主体fingerprintの越境可視化は残る。

## 対応方針

- trusted SaaS sessionから解決したprincipal IDとtenant IDを、caller headerではなくserver-owned request stateへ渡す。
- Stage-Bの許可／拒否操作はtrusted principalのfingerprintとtenant IDを監査行へ保存する。
- Stage-B監査一覧はactive tenantでqueryを絞り、bootstrap用静的admin keyだけをglobal readとする。
- `X-Actor-Ref`や`X-Tenant-Id`を監査の正本として受け入れない。

## 受入条件

- [x] Stage-B操作の監査行へtrusted principal fingerprintとtenant IDが記録される。
- [x] spoofした主体・tenant headerが監査属性へ影響しない。
- [x] Stage-B監査一覧は自テナント行だけを返し、他テナント／bootstrap行を返さない。
- [x] Stage-A静的admin keyはbootstrap運用のためglobal監査一覧を維持する。
- [x] 管理認証・監査回帰39件が通過する。

## 対応結果（2026-08-17）

認証依存がtrusted sessionを保持し、`ControlPlaneSubject`としてrequest stateへ伝播するよう変更した。監査middlewareはStage-Bならtrusted principalをhash化してtenant IDとともに保存し、Stage-Aなら従来どおり静的key fingerprint／tenant NULLを記録する。監査read APIはStage-B subjectのtenant IDをrepository filterへ渡し、cursor適用前にtenant境界を固定する。

integration testでは偽の`X-Actor-Ref`／`X-Tenant-Id`、tenant A/B/bootstrap混在行、Stage-A global readを含めて検証した。

## 検証計画

- `tests/test_admin_audit_trail.py`
- `tests/test_control_plane_authorization.py`
- `scripts/verify_admin_ops_flow_e2e.sh`
