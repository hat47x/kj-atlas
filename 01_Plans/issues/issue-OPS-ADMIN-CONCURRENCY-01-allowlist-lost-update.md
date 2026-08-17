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
- [ ] 直接APIの無条件PUTを廃止し、revisionを必須化する。
- [ ] 独立管理consoleで競合差分・再読込UXを固定する。
- [ ] PostgreSQL実DBで2transactionを並行させる競合E2EをCIへ追加する。

## 部分対応記録（2026-08-17）

APIのrevision契約、409、row lock、CLIの自動引継ぎ、逐次stale revision testを実装した。既存automationとの移行互換性のため未指定PUTは現時点で許容しており、issueは`In Progress`を維持する。
