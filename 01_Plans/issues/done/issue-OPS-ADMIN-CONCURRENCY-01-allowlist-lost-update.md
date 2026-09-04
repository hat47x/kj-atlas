# Issue: OPS-ADMIN-CONCURRENCY-01 allowlist管理APIの無条件更新にlost update余地がある

- Type: Operations / Correctness
- Status: Done
- Source Issue: 管理UI・CLI・API協調モンキーテスト（2026-08-17）
- Priority: P1
- Owner: Maintainer
- Scope: tenant model allowlist API, admin CLI, administrator console
- Related ADR/Spec: `ADR-0072`, `AI-MODEL-GOVERNANCE-01`, `02_Architecture/api.md`
- Expected verification level: `e2e`

## 課題

管理CLIはGETで現行allowlistを表示した後にPUTするが、その間に別管理者が更新しても検知せず、後勝ちで新しい設定を失わせた。model許可の意図しない拡大・縮小と、利用者UI・生成AI操作の突然の変化につながる。

## 対応方針

- GET応答へmodelIdsから導出したcontent revisionを含める。
- PUTは`expectedRevision`指定時にtenant rowをlockして比較し、不一致を`409 model_allowlist_conflict`で拒否する。
- 正式CLIは常にrevisionを引き継ぎ、競合時に上書きしない。
- 独立管理consoleは409時に自動再送せず、現行値を再読込して差分確認を求める。
- 直接APIの`expectedRevision`未指定は428で拒否する。

## 受入条件

- [x] 正式CLI経路で古いrevisionによる更新を拒否し、新しいallowlistを保持する。
- [x] 競合errorに秘密値・他tenant情報を含めない。
- [x] PostgreSQL等の対応RDBでtenant row lockを取得して比較する。
- [x] 直接APIの無条件PUTを廃止し、revisionを必須化する。— 2026-08-26、Maintainer決定に基づく**意図的な破壊的変更**（移行期間なし）。`PUT /admin/provision/models/tenants/{tenant_id}/allowlist`は`expectedRevision`省略時に`428 Precondition Required`（`{"code": "model_allowlist_expected_revision_required", "message": "expectedRevision is required to update the tenant model allowlist."}`）を返し、更新を行わない（`03_Implement/backend/src/kj_atlas_api/routes/model_registry.py` `put_tenant_allowlist()`）。`inquiry_bundles.py`のPUT/DELETEが`If-Match`欠落時に返す428と同じ契約形状に揃えた。`expectedRevision`不一致時の`409 model_allowlist_conflict`は変更していない。正式CLI（`cli.py` `model-allowlist-set`）は元々常にGETで取得したrevisionを送っており、この変更による影響を受けない（確認済み）。既存テストのうち未指定PUTに依存していた箇所をGET-then-PUTへ更新し、新規テスト`test_tenant_allowlist_put_without_expected_revision_is_rejected_428`で「未指定→428・非mutation」「正しいrevision→200」「stale revision→409」を確認した。
- [x] 独立管理consoleで競合差分・再読込UXを固定する。— 2026-09-04、主キャンバスの`App.tsx`へ管理機能を混ぜず、`03_Implement/frontend/admin.html`を別entryとする最小control-plane consoleを追加した。専用API clientはStage Aの`X-Admin-Api-Key`を入力中のメモリからだけ送り、永続ストレージへ保存しない。Stage Bのtrusted same-origin sessionを使う場合はkeyを空欄にできる。Saveは読み込んだ`revision`を必ず`expectedRevision`として送る。409 `model_allowlist_conflict`時はPUTを1回で止め、GETで現在のallowlistを再読込し、「自分のdraftだけ」「現在のサーバーだけ」の差分を表示する。競合表示中はSaveを無効化し、管理者が「現在値を採用」または「現在revisionを新しい編集基準としてdraftを維持」を明示選択するまで再送できない。後者を選んでも保存は行わず、もう一度Saveを押した時だけ新revisionで2回目のPUTを行う。`model_allowlist_admin.test.ts`で409時PUT 1回＋GET 1回、非409時の非再読込、重複ID非自動補正を固定し、`admin_model_allowlist_conflict.spec.ts`で実画面の差分表示・Save無効化・明示基準更新・二度目のSaveをChromium E2Eで確認した。branch-only GitHub Actions Run `33873424617`でfull TypeScript typecheck、production build（`dist/admin.html`生成）、unit 5件、Playwright 1件、Issue/docs/diff契約がすべて成功し、一時workflowは成功後に削除した。
- [x] PostgreSQL実DBで2transactionを並行させる競合E2EをCIへ追加する。— 2026-08-25、`test_model_governance_postgres_concurrency.py`。隔離Postgres DBで実際に重なる2スレッド（writer A/B）を使い、writer Bの`SELECT ... FOR UPDATE`がwriter Aのcommitまで実際にブロックすること（`unblocked_after_a_committed`）、ブロック解除後にAの書き込みを観測すること、その結果readしたrevisionが事前revisionと一致しないことを確認した。変異検査で`with_for_update()`を一時除去すると対応テストだけが失敗することも確認した。

## 完了記録

- 2026-08-17: APIのrevision契約、409、row lock、CLIの自動引継ぎ、逐次stale revision testを実装した。
- 2026-08-25: PostgreSQL実DBでの並行E2Eを追加した。
- 2026-08-26: `expectedRevision`未指定PUTを428で拒否し、無条件更新経路を廃止した。
- 2026-09-04: 独立`admin.html` consoleと競合差分・再読込・非自動再送UXをunit/E2Eで固定し、全受入条件を完了した。

## 境界

- 409を受けた管理consoleは、管理者の確認なしにPUTを再送しない。
- server側の現在値を自動的にdraftへ統合しない。差分を見せ、どの編集基準を採るかを管理者が決める。
- admin keyをlocalStorage/sessionStorage等へ保存しない。
- control planeの認証境界はADR-0072を維持し、business-plane credentialで代替しない。
