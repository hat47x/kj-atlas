# ADR-0070: KJキャンバス世代をcontent-addressed DAGで管理しGitを任意adapterとする

- Status: Accepted
- Date: 2026-08-09
- Deciders: Maintainer
- Scope: Document persistence, Content Store, inquiry snapshots, AI collaboration provenance

## Context

KJ法キャンバスは長期編集、分岐、統合、人間と生成AIの提案・採否、探究ラウンドの節目を持ち得る。全スナップショットを複製すると容量が増える一方、全操作イベントを永続化すると再生・移行・削除・SafeModeの複雑性が過大になる。Gitのcontent-addressed object、delta圧縮、DAG、merge、交換可能性は魅力があるが、Git commitをruntime正本にするとtenant認可、RDB transaction、retention、PII削除、object GC、同時更新をGitの意味へ拘束する。

現行には意味の異なる複数の「version」がある。`Document.version`はschema version、HTTP ETagは現在本文digest、`RoundSnapshotV1`は人が確認した探究成果、merge decision logは判断履歴であり、新しい編集世代と同一視できない。

## Decision candidate

1. キャンバス編集世代をGit非依存のcontent-addressed revision DAGとして定義する。revisionはcontent digestと親revisionを持ち、物理本文は既存Content Storeへ保存する。
2. 全操作のevent sourcingは採用しない。autosave、意味checkpoint、統治対象checkpointの3 tierだけを扱う。
3. `ephemeral`はautosave用で、親・digest・時刻・理由だけの最小metadataとする。actor、prompt、model、AI runを付けず、件数・期間で回収する。
4. `checkpoint`は手動保存、探究ラウンド、branch、merge、import、AI proposal、人によるproposal採用に使う。必要な由来参照だけを持つ。
5. `governed`はhuman review、share、export等、再現・説明・監査が必要な節目に使い、opaque actor、policy／schema参照、保持判断を別metadataで必須化する。
6. AI proposal revisionは`ai_run_ref`を必須とする。AI runのtask、入力IR digest、出力digest、policy version等は別recordへ置き、全revisionへprovider/model/promptを複製しない。raw promptや未レビュー本文を世代metadataへ保存しない。
7. 人がAI proposalを採用した場合は、人間originの新revisionを作り、source proposal revisionを参照する。AI proposalをhuman-authored／human-reviewedへ書き換えない。
8. 圧縮はcanonical JSONを前提に、content-addressed chunk／deltaと定期full snapshotを組み合わせる。delta chainは有界とし、復元costまたはdelta比率が閾値を超えたらfull snapshotへ戻す。具体値は代表データbenchmarkで確定する。
9. Gitはarchive／import-export／offline collaborationに限定した任意adapter候補とし、標準runtime正本またはhot-path blob backendにはしない。採用時もアプリrevision IDとSHA-256 digestを正本にし、Git object IDやbranch refを認可・真正性の根拠にしない。
10. Git adapterはbare repository、server-managed ref、hook無効、worktreeなしを前提とする。tenant分離、暗号化、GC、削除、pack backup/restore、同時書込を検証するまで有効化しない。
11. revisionと物理blobを分離する。複数revisionが同じ`tenant + content digest`のimmutable blobを参照でき、保存backendはdatabase／NAS／S3／将来Gitのいずれでもよい。revisionごとにobjectを複製しない。
12. NAS／S3はrevision DAGと競合する代替正本ではなく、full snapshot／delta／chunkの物理blob backend候補とする。ただしruntime切替、coordinator、domain FKの実装優先度を下げ、revision schemaと圧縮benchmarkが確定するまで凍結する。
13. 現行`content_object_references`は外部保存の先行metadataであり、最終schemaとは扱わない。revision導入時に`content_blobs`（digest identity）と`canvas_revisions`（論理世代）へ責務分離し、既存tableを互換migrationまたは撤去対象として再評価する。
14. canonical JSONはUTF-8、key辞書順、余分な空白なし、NaN/Infinity禁止とする。full/deltaの選択は保存backendではなくcodecが決め、delta chain上限または圧縮比閾値を超えた場合はfull gzipへ戻す。復元後digest検証に成功するまでDocumentとして解釈しない。
15. retention GCはmark-and-sweep型とし、まず候補だけを列挙する。head、DAG parent、source proposal、明示pinから到達するrevisionを削除せず、checkpoint／governedを自動期限削除しない。revision削除後も参照数ゼロと保留期間を確認するまで物理blobを削除しない。
16. revision削除時は保護条件を同じDELETE statementで再評価し、候補列挙後のpin/head追加競合をfail closedにする。blob sweepはrevision参照とdelta base参照がともにゼロで、`failed|deleting`の保留期限超過objectだけを対象とする。
17. AI実行は`ai_generation_runs`へ分離し、task、監査ログ接続用trace ID、入力IR digest、出力blob digest、policy version、SafeMode、作成・保持期限だけを保存する。prompt、入出力本文、provider、model、transportはrevision DAGへ複製しない。AI proposal revisionだけが同一tenantのAI runを参照でき、SafeMode無効のrunはDB制約で拒否する。
18. GCによるrevision／blob削除は本文を含まないappend-only監査を残す。blob GCは対象rowをlockしたトランザクション内で参照を再確認し、`deleting`へ遷移してから物理backendを削除し、metadata削除と成功監査を同じtransactionへ置く。物理削除失敗時はrowを`deleting`のまま残して失敗監査を記録し、retry可能にする。外部I/O中のrow lockはGC worker限定の安全性優先trade-offとして許容する。
19. ephemeral件数保持は単一branchの連番ではなくtenant内DAG到達性で計算する。全head、pin、checkpoint／governed revision、source参照先をrootとし、各rootから各parent path上で設定件数以内のephemeralをunionして保持する。保持範囲外との境界edgeを切断した後、候補部分DAGをchild-firstで削除する。共有祖先がいずれかのrootから保持範囲内なら削除せず、cycle、欠損parent、削除中の保護条件変更はtransaction全体をfail closedにする。

## Alternatives

| 方式 | 圧縮・重複排除 | 分岐 | tenant／認可 | 削除・retention | 判断 |
| --- | --- | --- | --- | --- | --- |
| 毎回full snapshot | 弱い | 可能 | 既存DBで容易 | 容易だが容量大 | 小規模fallback |
| 操作event sourcing | 強い | 強い | 実装可能 | 再生・削除が複雑 | 不採用継続 |
| Gitをruntime正本 | 強い | 強い | RLS／transactionと不整合 | GC・履歴改変が難しい | 標準不採用 |
| 独自revision DAG + Content Store | backend非依存 | 強い | DB metadataで維持 | policy制御可能 | 推奨候補 |
| 独自DAG + optional Git adapter | 上記 + Git交換性 | 強い | coreから分離 | adapter単位で管理 | 将来候補 |

## Consequences

- DB、NAS、S3、将来のGit保存で同じ論理世代を利用できる。
- autosaveへ重いAI・actor属性を付けないため、容量・PII・監査ノイズを抑えられる。
- AI提案と人間採用の系譜を保ちつつ、proposal-onlyとhuman review境界を維持できる。
- AI実行の再現・監査接続に必要な最小identityを保持しつつ、promptや生成本文の重複保存を避けられる。provider実行詳細は既存監査ログをtrace IDで参照する。
- revision DAG、delta生成、GC、保持pin、domain row参照、共有bundleの追加設計が必要になる。
- Gitの圧縮効果はJSON canonical化と変更局所性に依存するため、実データbenchmarkなしに採用効果を断定しない。
- object storageを先行実装しないことで二重参照・二重GCを避ける一方、大容量・低価格・共有storageが必要になった時点で同じblob contractへ追加できる。
- GC監査はrevision IDまたはdigest、backend、結果だけを保持し、削除済み本文やlocatorを複製しない。

## Preliminary benchmark 2026-08-09

実キャンバスの大規模fixtureが未整備のため、300カード、100世代、各世代5カード更新、安定key順の複数行JSONという合成条件で一次計測した。

| 方式 | 合計bytes | 備考 |
| --- | ---: | --- |
| raw full snapshot x100 | 12,781,223 | 最終1世代は130,103 bytes |
| gzip full snapshot x100 | 476,633 | 世代単位の独立復元が容易 |
| gzip delta x99 | 41,446 | 初期full snapshot分を加える必要がある |
| Git repository after aggressive GC | 112,612 | `.git`全体。worktree 130,103 bytesは別 |

この結果はGit packとdelta方式の両方に圧縮価値があることを示すが、実データ、分岐、並べ替え、巨大本文、復元時間を含まない。Git直接採用の根拠にはせず、revision／blob分離と代表fixture整備を先行する。

追試として実装codecを用いた同規模の再現可能benchmarkでは、raw 11,273,323 bytes、保存447,181 bytes、full 100、delta 0、encode約720ms、100世代restore合計約41msとなった。したがってgzip fullを当面の既定とし、deltaは常設前提にせず、実データでfullより有利な場合だけadaptiveに採用する。

同一fixtureを100 Git commitとして保存しaggressive GCした追試では、`.git`全体113,646 bytes、commit作成＋GC約37.8秒、3世代の`git show`復元約194msだった。Git packはgzip fullより約4倍小さいが、書込・GCと任意世代読取のhot-path costが大きい。したがって標準runtimeはgzip full＋DB metadataとし、Gitは明示的なarchive／交換処理でのみ再評価する。

## Extended representative benchmark 2026-08-10

既存frontendの実Document fixtureを起点にした40世代、同fixtureの2 branch＋merge、同じDocument形状を1.15 MiBへ拡張した20世代を`benchmark_generation_scenarios.py`で追試した。

| 条件 | 世代サイズ | raw合計 | adaptive保存 | full/delta | encode / 全restore | Git pack | Git write+GC / 3 restore |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fixture派生40世代 | 830–1,486 B | 46,192 B | 22,625 B | 40 / 0 | 14.73 / 1.43 ms | 56,549 B | 16.39 s / 185.46 ms |
| branch＋merge 4世代 | 814–834 B | 3,298 B | 1,977 B | 4 / 0 | 1.23 / 0.16 ms | 29,796 B | 2.59 s / 179.85 ms |
| 1.15 MiB級20世代 | 1,156,489–1,157,646 B | 23,140,981 B | 11,794,985 B | 20 / 0 | 2.91 s / 187.48 ms | 694,796 B | 12.95 s / 295.09 ms |

全条件でdeltaは選択されず最大depthは0だった。Git packは特に大容量反復データで高圧縮だが、metadata込み小規模履歴ではgzip fullより大きく、全条件でwrite／GCと任意世代restoreの固定costが顕著だった。よって`delta_chain_max_depth=32`と比率0.7は上限guardrailとして維持するが、runtimeの容量見積りはdeltaを前提にせずgzip fullで行う。Gitをhot pathから除外する判断も維持する。

## Non-goals

- 本ADRだけでGitをruntime保存先として有効化しない。
- 全キー入力、undo/redo、UI操作、LLM tokenを永続eventにしない。
- revision digestを署名、認可、human review証明として扱わない。
- 既存`RoundSnapshotV1`、merge decision log、audit eventをrevisionへ置換しない。

## Runtime integration amendment 2026-08-11

既存Document APIをrevision DAGへ段階移行する際の曖昧性を次のとおり解消する。

1. 現行frontendの`PUT /docs/{doc_id}`は利用者の明示的な保存操作からだけ呼ばれるため、`generation_reason=manual_save`、`generation_tier=checkpoint`、`generation_origin=human`として扱う。autosave、import、AI proposal、human acceptanceは既存PUTから推測せず、将来のserver-owned operation contextまたは専用APIで区別する。
2. 通常Documentの既定head名は`main`とする。既存headがないDocumentの最初のmaterializeでversion 1を作り、以後の変更保存は現在headを単一parentに持つ。
3. HTTP ETagは互換期間中も`documents.payload_json`のSHA-256を維持する。content digestはcanonical JSONのSHA-256、head versionはCAS用整数であり、三者を同じversionとして公開しない。
4. byte-for-byteの入力表現ではなくcanonical JSON digestが現在headと同一なら、PUTはprojectionの互換fieldを更新できるが、新revision作成とhead version増加を行わない。意味のない世代増加を避ける一方、同一本文を監査checkpointとして残す用途は将来の明示操作に分離する。
5. legacy DocumentはGETで暗黙に書き換えない。batch backfillまたは次回PUTのtransaction内で初期revisionを作る。headがない間だけ`documents.payload_json`をlegacy正本として読む。
6. headが存在するDocumentでは、revision blobの復元・digest検証を成功させ、互換projectionとのcanonical一致を確認する。不一致時は一方を黙って上書きせずfail closedとし、修復runbookへ送る。
7. PUTはDocument projection、blob、revision、parent、headを単一DB transactionへ置く。`If-Match`確認後の同時更新はhead CASで再検証し、stale writerへ409を返す。成功応答後の非同期dual writeは禁止する。

## Traceability

- Implementation: `01_Plans/issues/issue-DATA-GENERATION-01-content-generation-policy.md`
- Related: `01_Plans/adr/ADR-0057-w-type-cumulative-inquiry-model.md`
- Related: `01_Plans/adr/ADR-0066-database-portability-capability-registry.md`
- Related: `01_Plans/adr/ADR-0041-core-value-invariants-single-guard.md`
- Related: `02_Architecture/database_portability.md`
