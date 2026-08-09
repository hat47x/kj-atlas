# Issue: DATA-GENERATION-01 KJキャンバス世代管理と保持ポリシー

- Type: Architecture / Data
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: User request 2026-08-09
- Priority: P2
- Scope: generation metadata, Content Store, persistence migration, AI provenance, optional Git adapter
- Related ADR/Spec: `ADR-0070`, `ADR-0057`, `ADR-0066`, `02_Architecture/database_portability.md`
- Expected verification level: contract / integration / storage benchmark

## 課題

- KJキャンバスの長期編集、分岐、人間・AI協働を追跡しつつ、full snapshot複製と全操作event sourcingの両極端を避ける。
- schema version、ETag、探究snapshot、判断log、編集revisionを混同しない。
- 全世代へactor、AI provider、model、prompt等を複製せず、説明責任が必要な節目だけに適切なmetadataを付ける。
- Gitのdelta圧縮と交換性を評価しつつ、tenant認可・削除・RDB transactionをGit固有実装へ拘束しない。

## 受入条件

- [x] AC-1: ephemeral／checkpoint／governedの3 tierとreason分類が定義される。
- [x] AC-2: AI proposalとhuman acceptanceが別revisionとして関連付けられ、AIがhuman reviewへ昇格できない。
- [x] AC-3: ephemeral revisionがactor／AI run metadataを持たない契約テストがある。
- [x] AC-4: revision DAG、content object参照、head更新のDB schemaとmigrationが実装される。
- [x] AC-5: canonical JSON、full snapshot／delta選択、最大chain depth、復元検証が代表データでbenchmarkされる。
- [x] AC-6: retention pin、ephemeral GC、governed保持、tenant-scoped orphan回収が実装される。
- [x] AC-7: AI run metadataの最小契約、SafeMode、redaction、保持期間が実装される。
- [x] AC-8: Gitを標準runtimeから除外し、archive／交換限定の将来adapter候補と判断する。実装する場合はbare repo、hook禁止、tenant分離、GC、backup/restoreを別gateで検証する。
- [x] AC-9: revisionと物理blobの責務が分離され、object storage作業がrevision schema確定前に先行しない。

## 検証計画

- reasonからtierへの決定論的分類と不正metadataのfail-closed unit test。
- branch／merge／AI proposal／human acceptanceを含むDAG constraint test。
- 代表的な小・中・大キャンバスでfull JSON、圧縮full snapshot、delta chain、Git packを比較する。
- SafeMode付きshare/exportが元revisionを書き換えず、派生artifactだけを生成することを確認する。

## Phase 1 checkpoint 2026-08-09

- `generation_policy.py`へ3 tier、11 reason、4 origin、revision metadata、初期retention guardrailを定義した。
- autosaveはminimal metadata、AI proposalは別AI run参照、人間採用はsource proposal参照、人手reviewはopaque actor必須としてfail closedにした。
- 初期値はephemeral 50件／7日、delta chain 32、delta比率0.7だが、物理保存へ適用する前に代表データbenchmarkで確定する。
- Gitは標準runtime正本にせず、optional archive／exchange adapter候補とした。このcheckpoint時点ではADR-0070はProposedであり、Git adapter実装は未着手だった。

## Storage interaction checkpoint 2026-08-09

- 現行object referenceは「1 content ID = 1 locator」、revision DAGは「複数revision = 共有digest blob」であり、そのまま並行実装すると参照・retention・orphan GCが二重化すると確認した。
- 論理`canvas_revisions`と物理`content_blobs`へ責務を分離する方針へ修正した。database／NAS／S3／Gitはblob backend候補であり、revision正本の代替にはしない。
- NAS/S3 adapterは実験的実装として保持するが、runtime設定、coordinator、domain FKの優先度を下げて凍結する。大容量、複数instance共有、DB inline非対応等の実需が現れるまで外部storageは必須化しない。
- 合成300カード・100世代・5カード/世代更新の一次計測はraw 12,781,223 bytes、gzip full 476,633 bytes、gzip delta 41,446 bytes（初期full別）、Git aggressive GC後112,612 bytesだった。実データfixtureと復元時間を含まないため採用判定は保留する。
- 次はrevision／blob schema、branch headのcompare-and-swap、full／delta復元契約を先行する。既存`content_object_references`は最終schemaではなく、互換migrationまたは撤去候補として扱う。

## Revision DAG schema checkpoint 2026-08-09

- `content_blobs`を`tenant + SHA-256 digest`の物理identity、`canvas_revisions`を論理世代、`canvas_revision_parents`を順序付きDAG edge、`canvas_revision_heads`をdocument内branch headとして分離した。
- full JSON／gzip full／gzip deltaを区別し、deltaだけがbase digestと正のdepthを持つDB制約を追加した。既存Document本文は移動・backfillしていない。
- revision、blob、source revision、parent、head、Documentをtenant複合FKで接続し、PostgreSQLでは全4テーブルへFORCE RLSを追加した。
- headは`head_version`一致時だけ更新するcompare-and-swap repositoryを追加した。stale writerは`RevisionHeadConflict`で停止し、別tenantの同名document／headへ影響しない。
- ORM／lineage／分類／policy／CASの17件と、fresh SQLite upgrade／downgrade 2件を通過した。AC-4を完了し、次はAC-5のcanonical化・delta生成・復元benchmarkへ進む。

## Canonical full/delta codec checkpoint 2026-08-10

- JSONをUTF-8、key順、空白なし、NaN禁止でcanonical化し、そのSHA-256をrevisionのcontent identityとした。
- deterministic gzip fullと、base/currentの共通prefix・suffixに基づくgzip deltaを実装した。deltaがfullの設定比率以下で、chain depth上限未満の場合だけdeltaを採用する。
- 復元時はbase digest、復元後byte size、SHA-256をすべて照合し、圧縮破損、base不一致、改ざん、未知representationをfail closedにした。
- codec／policy／head CASの15件とRuffを通過した。合成fixtureでの可逆性は確認したが、実キャンバスfixtureの容量・復元時間benchmarkが残るためAC-5は未完了を維持する。

## Reproducible 300-card benchmark 2026-08-10

- `scripts/benchmark_generation_codec.py`を追加し、300カード、100世代、各世代5カード更新を再現可能にした。
- raw合計11,273,323 bytesに対しadaptive codecは447,181 bytes、encode約720ms、100世代restore合計約41msだった。
- full 100件、delta 0件となった。canonical JSON全体をgzipするだけで反復構造が十分圧縮され、このfixtureではdelta envelopeが比率閾値を満たさなかった。
- 当面はgzip fullを既定、deltaは有効性が実測された場合だけ使う。実利用由来fixture、branch／merge、1MiB級データ、Git pack同条件比較が残るためAC-5は未完了を維持する。

## Git pack comparison 2026-08-10

- 同じ100世代をGit commitへ保存し、aggressive GC後の`.git`全体、作成時間、0／50／99世代の`git show`復元をbenchmarkへ統合した。
- Gitは113,646 bytesでgzip full 447,181 bytesより約4倍小さかった。一方、100 commit＋GCは約37.8秒、3世代復元は約194msで、codecのencode約0.70秒、100世代restore約43msよりhot path costが大きい。
- Gitを標準runtime正本／blob backendにしない判断を確定し、AC-8を完了した。将来のarchive／交換adapterは、利用要求が生じた場合だけ別gateで実装する。
- AC-5には実利用由来fixture、branch／merge、1MiB級データが残る。現時点の標準候補はcontent-addressed revision DAG＋gzip full blobである。

## Retention pin and GC candidate checkpoint 2026-08-10

- `canvas_revision_pins`を追加し、tenant/revision複合FK、非空reason、PostgreSQL FORCE RLSで明示保持を表現した。
- GCは削除から始めず、期限超過ephemeralの候補列挙として実装した。current head、他revisionの親、human acceptance等のsource、明示pinは候補から除外する。checkpoint／governedはtier条件で除外する。
- 候補選定はtenant context必須、古い順、件数上限付きであり、別tenantの同名revisionを参照・選定しない。物理blob削除はrevision参照がなくなったことを別工程で確認するまで行わない。
- ORM／lineage／分類／fresh upgrade-downgrade／GC候補の9件とRuffを通過した。実削除、branch到達性に基づく件数保持、blob orphan回収が残るためAC-6は未完了を維持する。

## Conditional revision delete and blob sweep checkpoint 2026-08-10

- ephemeral revision削除は候補取得後の無条件deleteにせず、head／parent／source／pin不在と期限・tierを単一DELETE文で再評価する。候補選定後にpin等が追加された競合でも削除しない。
- blob sweep候補はtenant内でrevision参照もdelta base参照もなく、`failed|deleting`かつ保留期限超過のものだけに限定した。`ready` blobや他blobのbaseを物理削除候補にしない。
- repository／codec／policyの15件とRuffを通過した。外部objectの実削除、削除監査、branch到達性に基づく件数保持が残るためAC-6は未完了を維持する。

## AI generation run lineage checkpoint 2026-08-10

- `ai_generation_runs`を追加し、task、trace ID、入力IR digest、出力blob digest、policy version、SafeMode、作成時刻、保持期限だけを保存する最小契約とした。prompt、入力本文、生成本文、provider、model、transportの列は持たず、実行詳細は既存監査ログへtrace IDで接続する。
- SafeModeは常にtrueであることをDB制約で強制した。AI proposal revisionはAI run参照必須、非AI revisionは参照禁止とし、tenant複合FKにより別tenantのrun参照を拒否する。出力digestも同一tenantのcontent blobへ接続した。
- PostgreSQLでは新tableへFORCE RLSを適用し、SQLite fresh upgrade／downgradeを含むmigrationを追加した。lineage／SafeMode／payload非保持／列分類／migrationの26件を通過し、AC-7を完了した。

## Audited physical blob GC checkpoint 2026-08-10

- `generation_deletion_audit_events`を追加し、revision／blob GCについてtenant、対象IDまたはdigest、backend、executor、結果、時刻だけをappend-only evidenceとして保存する。本文と外部locatorは監査へ複製しない。PostgreSQLではFORCE RLSを適用した。
- revision削除は条件付きDELETEが成功した場合だけ同じtransactionへ監査rowを追加する。保護対象や別tenantを削除できない既存条件を維持した。
- blob GCは`ready|failed|deleting`の期限超過orphanを対象とし、row lock下でrevision参照とdelta base参照を再確認する。database blobはmetadataを、NAS／S3等は注入されたadapterで物理objectを削除してからmetadataを消す。object不在は冪等成功、削除例外は`deleting`状態と失敗監査を残す。
- migration fresh upgrade／downgrade、外部削除成功・失敗、監査、列分類、lineageを含む9件とRuffを通過した。

## DAG reachability retention checkpoint 2026-08-10

- 全head、pin、checkpoint／governed revision、human acceptance等のsource参照先を保持rootとし、各rootからparent pathごとに設定件数以内のephemeral revisionを保持するtenant-scoped pruningを追加した。
- 複数branchの保持集合をunionするため、merge共有祖先はどれか一つのrootから保持範囲内なら残る。範囲外は保持側との境界edgeを切断し、候補DAGをchild-firstで削除して各削除監査を残す。
- 欠損parent、DAG cycle、削除直前のhead／pin／parent／source保護変更は`GenerationGcConflict`としてtransaction全体をfail closedにする。checkpoint／governed自体は候補集合へ入らない。
- branch、merge、共有祖先、複数head、監査を含むrepositoryテストとRuffを通過した。これによりAC-6を完了した。

## Extended representative codec benchmark 2026-08-10

- `scripts/benchmark_generation_scenarios.py`を追加し、既存frontendの実Document fixture由来40世代、2 branch＋merge 4世代、1.15 MiB級20世代を再現可能にした。各世代はcanonical化、adaptive encode、親指定restore、digest検証を通す。
- adaptive保存量は順に22,625 B／1,977 B／11,794,985 Bで、全64世代がgzip full、delta 0、最大depth 0だった。現行prefix/suffix deltaは代表条件でgzip fullを上回らないため、容量設計はdelta効果を見込まず、比率0.7とdepth 32は将来の有利な入力だけを許可するguardrailとして維持する。
- 同条件のGit aggressive packは56,549 B／29,796 B／694,796 Bだったが、write＋GCは16.39 s／2.59 s／12.95 s、3世代restoreは185.46 ms／179.85 ms／295.09 msだった。大容量時の圧縮優位は確認した一方、runtime hot path不採用の判断は維持する。
- 実fixture、branch、merge、1 MiB超、Git同条件、復元時間まで揃ったためAC-5を完了した。これによりDATA-GENERATION-01の全受入条件が実装または判断済みとなった。
