# ADR-0071: Document DBをRDB正本の代替ではなく再構築可能な派生projection候補とする

- Status: Accepted
- Date: 2026-08-10
- Deciders: Maintainer
- Scope: persistence architecture, realtime collaboration, offline/read projection, revision DAG

## Context

KJキャンバスはJSON documentとして扱いやすく、FirestoreやDynamoDBには柔軟なdocument model、managed scaling、realtime/offline連携という採用価値がある。一方、kj-atlasの永続化はcanvas本文だけでなく、tenant認可、複合FK、identity一意性、監査、AI lineage、content-addressed revision DAG、保持pin、GCを同じ整合性境界で管理する。

現在の代表canvasは1 MiB超を実DBmatrixで検証している。Firestoreのdocument上限は1 MiB、DynamoDBのitem上限はattribute名を含め400 KiBであり、canvas全体を単一document/itemへ保存できない。Firestore transactionは競合時に再実行され、offlineでは失敗し、request上限10 MiB・lock期限20秒・全体270秒の制約を持つ。DynamoDB transactionは同一account/Region内の最大100 item・合計4 MiBで、Global Tablesへの反映はRegion間transactionではない。

本文を分割すれば保存自体は可能だが、chunk、manifest、原子的head更新、orphan回収、tenant認可、世代GCが既存のcontent-addressed DAGと二重化する。Document DBをSQLAlchemy dialectのように扱うこともできず、RDB promotion matrixとは別のrepository・migration・transaction・backup契約が必要になる。

## Decision

1. RDBをtenant認可、document head、revision DAG、監査、AI lineage、retention/GC metadataの正本として維持する。Firestore/DynamoDBをRDB代替backendとしてDB能力レジストリへ登録しない。
2. canvas本文・revision blobの物理保存は既存`ContentStore`境界で扱う。Document DB固有のchunkingを追加してrevision DAGを複製しない。
3. Document DBの採用候補を、正本から再構築でき、消失しても権限・履歴・監査を失わない派生用途に限定する。
   - online presence、cursor、selection、typing indicator等の短命なcollaboration state
   - inbox／最近使った文書／検索候補等のread projection
   - offline取得を高速化する暗号化済みcache manifest。ただし未同期編集の正本化は別ADRを必須とする
4. 派生更新はRDB transaction内のoutboxを起点に非同期反映する。application transactionからRDBとDocument DBへのdual writeを行わない。
5. projectionは`tenant_id + projection_kind + source_version`を持ち、RDBの認可判定後だけ配信する。projection側のsecurity rule/IAMだけを正本認可として信頼しない。
6. stale projectionは明示できるようsource versionを返し、更新遅延・欠落時はRDBへfallbackする。projectionからRDB正本を逆生成しない。
7. TTL、削除要求、tenant退会、SafeMode、暗号化、リージョン、backup、費用上限をprovider別promotion gateで実証するまでruntime設定を公開しない。
8. FirestoreとDynamoDBを一つの抽象的「Document DB adapter」に早期統合しない。具体的access patternが成立した時点で、用途別portに対する最小adapterとして比較する。

## Provider assessment

| 観点 | Firestore | DynamoDB | kj-atlas判断 |
| --- | --- | --- | --- |
| 単一object上限 | document 1 MiB | item 400 KiB | canvas／revision blob正本には不適合 |
| 複数object transaction | 競合時retry、10 MiB request、offline失敗 | 最大100 item・4 MiB・同一account/Region | 既存RDB transactionの置換理由にならない |
| realtime/offline | client SDKとの統合価値が高い | Streams/AppSync等の追加構成が必要 | presence/read projectionならFirestoreを先に評価可能 |
| access pattern | collection/query/index設計 | partition/sort keyを先に固定 | 汎用repository化せず用途別に評価 |
| vendor portability | Google/Firebase固有 | AWS固有 | 再構築可能projectionに限定してlock-inを封じる |

## Promotion gate for a future pilot

1. 実際のaccess patternとSLOを先に固定し、RDBのみのbaselineより価値があることを計測する。
2. projection再構築、重複event、順序逆転、遅延、provider outage、rate limitをfixtureで再現する。
3. tenant A/B越境、認可失効、削除、TTL、backup/restore、リージョン境界を実serviceまたは公式emulatorと本番相当IAMで検証する。
4. source version不一致時のstale表示とRDB fallbackを確認する。
5. SDK、credential、cost telemetry、health checkをoptional integrationへ閉じ込め、core runtime dependencyにしない。

## Three-Element Verification（ADR-0067 遡及適用）

| 次元 | このADRでの主張 | 他次元への制約 |
|------|----------------|---------------|
| **業務設計** | キャンバスはJSONとして扱いやすいが、永続化は本文だけでなくtenant認可・複合FK・identity一意性・監査・AI lineage・revision DAGを同じ整合性境界で管理する必要がある。JSON形状との相性だけで検証済みのtransaction/constraint/revision DAGを捨てない | 機能: RDBを正本として維持しDocument DBをDB能力レジストリへ登録しない。データ: realtime需要が生じたらDocument DBの強みだけを利用 |
| **データ設計** | canvas本文・revision blobの物理保存は既存`ContentStore`境界で扱い、Document DB固有のchunkingを追加してrevision DAGを複製しない。Document DB採用候補は正本から再構築でき消失しても権限・履歴・監査を失わない派生用途（presence/read projection/cache manifest）に限定 | 業務: projectionは`tenant_id + projection_kind + source_version`を持ちRDB認可判定後だけ配信。機能: stale projectionはsource versionを返し更新遅延・欠落時はRDBへfallback |
| **機能設計** | 派生更新はRDB transaction内のoutboxを起点に非同期反映しdual writeを行わない。projection側のsecurity rule/IAMだけを正本認可として信頼しない。Firestore/DynamoDBを抽象的Document DB adapterへ早期統合しない | 業務: outbox・projection worker・staleness表示・provider別障害試験が必要なため需要とSLO未確定の現時点では実装しない。データ: TTL・削除・tenant退会・SafeMode・暗号化・backup・費用上限をpromotion gateで実証するまでruntime設定を公開しない |

## Consequences

- JSONとの形状上の相性だけで、既に検証済みのtransaction・constraint・revision DAGを捨てずに済む。
- realtime collaborationの具体的需要が生じた場合、Document DBの強みだけを利用できる。
- outbox、projection worker、staleness表示、provider別障害試験が必要になるため、需要とSLOが未確定の現時点では実装しない。
- RDB、NAS/S3、Git、Document DBの責務が分離され、複数の「正本」が競合する状態を避けられる。

## Evidence

- [Firestore usage and limits](https://firebase.google.com/docs/firestore/quotas)
- [Firestore transactions](https://firebase.google.com/docs/firestore/manage-data/transactions)
- [DynamoDB constraints](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Constraints.html)
- [DynamoDB transactions](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/transaction-apis.html)

## Traceability

- `01_Plans/issues/issue-DB-DOCUMENT-01-document-database-derived-projection.md`
- `01_Plans/adr/ADR-0066-database-portability-capability-registry.md`
- `01_Plans/adr/ADR-0070-content-addressed-generation-dag-and-git-adapter.md`
- `02_Architecture/database_portability.md`
