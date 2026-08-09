# ADR-0070: KJキャンバス世代をcontent-addressed DAGで管理しGitを任意adapterとする

- Status: Proposed
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
9. Gitは任意のarchive／import-export／offline collaboration adapter候補とし、標準runtime正本にはしない。採用時もアプリrevision IDとSHA-256 digestを正本にし、Git object IDやbranch refを認可・真正性の根拠にしない。
10. Git adapterはbare repository、server-managed ref、hook無効、worktreeなしを前提とする。tenant分離、暗号化、GC、削除、pack backup/restore、同時書込を検証するまで有効化しない。
11. revisionと物理blobを分離する。複数revisionが同じ`tenant + content digest`のimmutable blobを参照でき、保存backendはdatabase／NAS／S3／将来Gitのいずれでもよい。revisionごとにobjectを複製しない。
12. NAS／S3はrevision DAGと競合する代替正本ではなく、full snapshot／delta／chunkの物理blob backend候補とする。ただしruntime切替、coordinator、domain FKの実装優先度を下げ、revision schemaと圧縮benchmarkが確定するまで凍結する。
13. 現行`content_object_references`は外部保存の先行metadataであり、最終schemaとは扱わない。revision導入時に`content_blobs`（digest identity）と`canvas_revisions`（論理世代）へ責務分離し、既存tableを互換migrationまたは撤去対象として再評価する。
14. canonical JSONはUTF-8、key辞書順、余分な空白なし、NaN/Infinity禁止とする。full/deltaの選択は保存backendではなくcodecが決め、delta chain上限または圧縮比閾値を超えた場合はfull gzipへ戻す。復元後digest検証に成功するまでDocumentとして解釈しない。

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
- revision DAG、delta生成、GC、保持pin、domain row参照、共有bundleの追加設計が必要になる。
- Gitの圧縮効果はJSON canonical化と変更局所性に依存するため、実データbenchmarkなしに採用効果を断定しない。
- object storageを先行実装しないことで二重参照・二重GCを避ける一方、大容量・低価格・共有storageが必要になった時点で同じblob contractへ追加できる。

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

## Non-goals

- 本ADRだけでGitをruntime保存先として有効化しない。
- 全キー入力、undo/redo、UI操作、LLM tokenを永続eventにしない。
- revision digestを署名、認可、human review証明として扱わない。
- 既存`RoundSnapshotV1`、merge decision log、audit eventをrevisionへ置換しない。

## Traceability

- Implementation: `01_Plans/issues/issue-DATA-GENERATION-01-content-generation-policy.md`
- Related: `01_Plans/adr/ADR-0057-w-type-cumulative-inquiry-model.md`
- Related: `01_Plans/adr/ADR-0066-database-portability-capability-registry.md`
- Related: `01_Plans/adr/ADR-0041-core-value-invariants-single-guard.md`
- Related: `02_Architecture/database_portability.md`
