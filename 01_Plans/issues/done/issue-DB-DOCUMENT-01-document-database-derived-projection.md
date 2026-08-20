# Issue: DB-DOCUMENT-01 Document DBの採用境界を確定する

- Type: Architecture / Research
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: User request 2026-08-09
- Priority: P2
- Scope: persistence architecture, realtime collaboration, revision DAG
- Related ADR/Spec: `ADR-0066`, `ADR-0070`, `ADR-0071`, `02_Architecture/database_portability.md`
- Expected verification level: documentation / primary-source constraint review

## 課題

- JSON documentとしての形状上の相性と、tenant認可・監査・revision DAGを含む正本要件を分けて評価する。
- Firestore/DynamoDBをRDB代替として導入した場合の二重transaction・二重chunking・vendor lock-inを避ける。
- realtime/offlineという採用価値を将来利用できる境界は残す。

## 受入条件

- [x] AC-1: FirestoreとDynamoDBのobject/item、transaction、整合性境界を公式資料で比較する。
- [x] AC-2: RDB、Content Store、revision DAG、Document DBの正本責務を定義する。
- [x] AC-3: Document DBを採用できる用途と採用しない用途を明記する。
- [x] AC-4: dual writeを禁止し、outbox起点の再構築可能projection契約を定義する。
- [x] AC-5: tenant分離、staleness、削除、障害、費用を含む将来pilot gateを定義する。
- [x] AC-6: 現段階でSDK・runtime設定・schemaを追加しない。

## 完了証跡 2026-08-10

- Firestore 1 MiB document上限とDynamoDB 400 KiB item上限が、既に1 MiB超を検証するcanvas正本に適合しないことを確認した。
- RDBを認可・head・監査・DAG metadataの正本、Content Storeをblob境界、Document DBを消失しても再構築できるpresence/read projection候補とした。
- RDBとDocument DBへの同期dual writeを禁止し、transactional outbox、source version、stale表示、RDB fallbackを必須化した。
- 具体的なrealtime collaboration SLOが未確定のため実装を見送り、Firestoreをpresence/read projectionの先行評価候補、DynamoDBをAWS access patternが明確な場合の候補とした。
