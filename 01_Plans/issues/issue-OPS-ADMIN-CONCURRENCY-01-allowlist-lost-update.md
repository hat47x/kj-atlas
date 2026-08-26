# Issue: OPS-ADMIN-CONCURRENCY-01 allowlist管理APIの無条件更新にlost update余地がある

- Type: Operations / Correctness
- Status: In Progress
- Source Issue: 管理UI・CLI・API協調モンキーテスト（2026-08-17）
- Priority: P1
- Owner: Maintainer
- Scope: tenant model allowlist API, admin CLI, future administrator console
- Related ADR/Spec: `ADR-0072`, `AI-MODEL-GOVERNANCE-01`, `02_Architecture/api.md`
- Expected verification level: `e2e`

## 課題

管理CLIはGETで現行allowlistを表示した後にPUTするが、その間に別管理者が更新しても検知せず、後勝ちで新しい設定を失わせた。model許可の意図しない拡大・縮小と、利用者UI・生成AI操作の突然の変化につながる。

## 対応方針

- GET応答へmodelIdsから導出したcontent revisionを含める。
- PUTは`expectedRevision`指定時にtenant rowをlockして比較し、不一致を`409 model_allowlist_conflict`で拒否する。
- 正式CLIは常にrevisionを引き継ぎ、競合時に上書きしない。
- 将来の管理consoleは409時に自動再送せず、現行値を再読込して差分確認を求める。
- 互換性期間終了後、直接APIの`expectedRevision`未指定を428で拒否する。

## 受入条件

- [x] 正式CLI経路で古いrevisionによる更新を拒否し、新しいallowlistを保持する。
- [x] 競合errorに秘密値・他tenant情報を含めない。
- [x] PostgreSQL等の対応RDBでtenant row lockを取得して比較する。
- [x] 直接APIの無条件PUTを廃止し、revisionを必須化する。— 2026-08-26、Maintainer決定に基づく**意図的な破壊的変更**（移行期間なし）。`PUT /admin/provision/models/tenants/{tenant_id}/allowlist`は`expectedRevision`省略時に`428 Precondition Required`（`{"code": "model_allowlist_expected_revision_required", "message": "expectedRevision is required to update the tenant model allowlist."}`）を返し、更新を行わない（`03_Implement/backend/src/kj_atlas_api/routes/model_registry.py` `put_tenant_allowlist()`）。`inquiry_bundles.py`のPUT/DELETEが`If-Match`欠落時に返す428と同じ契約形状に揃えた。`expectedRevision`不一致時の`409 model_allowlist_conflict`は変更していない。正式CLI（`cli.py` `model-allowlist-set`）は元々常にGETで取得したrevisionを送っており、この変更による影響を受けない（確認済み）。既存テスト（`test_model_governance.py`の複数ケース、`admin_lifecycle.py`、`verify_business_flow_e2e.sh`、frontend e2eの`ai_model_ux_available_models_reason.spec.ts`）のうち、未指定PUTに依存していた箇所をGET-then-PUTへ更新。新規テスト`test_tenant_allowlist_put_without_expected_revision_is_rejected_428`で「未指定→428・非mutation」「正しいrevision→200」「stale revision→409（既存挙動維持）」を確認。変異検査（428ガードを一時的に無効化＝pre-AC-4の無条件accept挙動へ戻す）で対象テストのみが失敗（`428 expected, got 200`）することを確認、復元後`test_model_governance.py`19件全pass。`02_Architecture/api.md`のPUT契約記述も更新済み。
- [ ] 独立管理consoleで競合差分・再読込UXを固定する。
- [x] PostgreSQL実DBで2transactionを並行させる競合E2EをCIへ追加する。— 2026-08-25、`test_model_governance_postgres_concurrency.py`。隔離Postgres DBで実際に重なる2スレッド（writer A/B）を使い、writer Bの`SELECT ... FOR UPDATE`がwriter Aのcommitまで実際にブロックすること（`unblocked_after_a_committed`）、ブロック解除後にAの書き込みを観測すること、その結果readしたrevisionが事前revisionと一致しないこと（＝実際にPUTすればconflictになる）を確認した。変異検査で`with_for_update()`を一時除去し、対応テストのみが失敗することを確認、復元後19件全pass（CIの`Backend lint + test`ジョブ内`Test (PostgreSQL)`ステップで自動実行）。

## 部分対応記録（2026-08-17）

APIのrevision契約、409、row lock、CLIの自動引継ぎ、逐次stale revision testを実装した。既存automationとの移行互換性のため未指定PUTは現時点で許容しており、issueは`In Progress`を維持する。

## 部分対応記録2（2026-08-25）

PostgreSQL実DBでの並行E2E（上記チェックリスト参照）を追加した。残るAC（直接APIの無条件PUT廃止・独立管理consoleの競合差分UX）は、既存automationとの互換性という運用判断とUI実装を要するため未着手のまま、issueは引き続き`In Progress`を維持する。

## 部分対応記録3（2026-08-26）

AC-4（直接APIの無条件PUT廃止）を実装した。詳細は上記チェックリストのAC-4行を参照。残るAC-5（独立管理consoleの競合差分・再読込UX）はUI実装を要し未着手のため、issueは引き続き`In Progress`を維持する。
