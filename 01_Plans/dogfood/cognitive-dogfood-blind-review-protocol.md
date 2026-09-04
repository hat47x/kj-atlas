# 認知dogfood ブラインドレビュー手順

- 状態: Case 001で最初の有効なraw runを得る前に準備済み
- 対象: `COGNITIVE-EVAL-01` P2 ブラインドレビュー
- 適用範囲: Case 001〜003。各Caseの事前登録で明示的に狭めた場合を除く
- 関連文書: `cognitive-dogfood-execution-plan.md`, `cognitive-dogfood-run-record-template.md`, `cognitive-dogfood-case-portfolio-preregistration.md`, `cognitive-dogfood-case-portfolio-freeze.md`

## 1. 目的

4Armを比較するとき、reviewerが「KJ Atlasを使った」「cultural-substrate-weavingを使った」と知ること自体によって、期待、反感、方法論への先入観を持ち込む可能性をできるだけ減らす。

ここでいうブラインドレビューは、臨床試験のような完全なblindを意味しない。成果物の文体や構造から、用いた方法を推測できる場合がある。そのため本手順の目的は、**Arm identityとmethod metadataを直接知らせないこと**、そして**成果物の根拠、反証、訂正可能性を方法名より先に読むこと**に置く。

## 2. 公開repositoryにおける情報漏洩の境界

KJ Atlas repositoryは公開されている。A/B/C/Dを明記したraw record、canvas、InquiryJourney参照、skill execution recordをblind verdict確定前に同じ公開branchへcommitすると、reviewerがrepositoryを探索するだけでunblindできてしまう。

そのため、Case 001〜003のRound 1では次を守る。

1. raw / result / record / canvas / inquiry-ref と Arm↔alias mappingは、blind verdictを凍結するまでreviewerから見えない操作者用workspaceに保持する。
2. どうしてもGitHubへ先に保存する必要がある場合は、blind reviewerをrepositoryへアクセスできない独立した新規コンテキストに限定し、blind package以外のrepository閲覧やtool利用を禁止する。ただし原則として1を優先する。
3. blind verdictを凍結した後で、raw evidence、record、mapping、blind verdictをまとめてrepositoryへ保存し、再現可能性を回復する。
4. invalid runも削除せず、blind review後に記録として残す。

blindを守るためにraw evidenceを永久に隠すことはしない。可視性を遅らせるのはblind期間だけである。

## 3. Aliasの割り当て

aliasには、A/B/C/Dと意味上の関係を持たない中立な文字列を使う。

- Armの実行順は、事前登録した **C → D → B → A** から変更しない。
- alias mappingは、最初のblind packageを生成する前に操作者用workspaceで作る。
- mappingをblind reviewerへ渡さない。
- mappingはblind verdictを凍結した後に公開する。
- 成果物の内容を見て、意味のある名前をaliasとして付けない。

たとえば`opal-17`、`cedar-42`、`linen-08`、`quartz-31`のような、意味を持たない識別子を使う。これらの例示名そのものを固定割当として使う必要はない。

## 4. Blind packageに含めるもの

packageは、そのCaseに共通するrequired outputを比較するために必要な情報だけへ絞る。

含めるもの:

- Case ID / Round / neutral alias。
- fixed question。
- §6 Required outputの内容。
- 主要主張のsource path / stable identifier / evidence time。
- counterevidence / uncertainty / deferred points。
- Candidate source requests。
- Caseごとに事前登録された訂正・時点差チェックについて、runが残したinterpretation。`T1` / `C2-T1` / `C3-T1`等のexperimenter用test IDは、package生成時に`source-check-N`へ中立化する。
- raw artifactへ戻るための操作者専用reference ID。ただしreviewerがそこからraw artifactを直接開けない形式にする。

原則として含めないもの:

- Arm A/B/C/D。
- KJ Atlas canvasを使用したかどうかというtreatment metadata。
- cultural-substrate-weavingを使用したかどうか、framework名、activation判定。
- model / provider名。Arm間でmodelが異なるdeviationがある場合は、blind packageで説明して帳尻を合わせるのではなく、blind review前のrun validityで処理する。
- KJカード数、島数、操作回数。
- M1〜M9についてrun自身が付けた評価。
- T9 / InquiryJourneyに関するmethod-friction記録。
- 操作者の感想や「このrunは良かった」などの評価語。
- 事前登録したtest IDや、experimenterだけが知る「何を発見するべきか」という説明。

required output本文に方法固有の自己言及が混ざっている場合は、意味を変えずに削除できる部分だけpackage化時に除く。削除すると主張の意味が変わる場合は改変せず、`method identity may be inferable`と記録する。

## 5. Packageの完全性

blind packageを作る過程で、raw resultを都合よく改善してはならない。

**P2への入口はfail-closedとする。** `build_cognitive_blind_package.py`はpackageを生成する前に、`validate_cognitive_run_records.py`と同等のstatic intakeを内部で実行する。run validity、fresh-context / contamination、固定artifact identity、Case固有Required outputの完全性、訂正・時点差チェックの記録などにerrorがあるrecordからはpackageを生成しない。

そのため、操作者がvalidatorの単独実行を省略してbuilderを直接呼んでも、このgateを迂回できない。static intakeのwarningだけではpackage生成を止めないが、builder自身が出すmethod-identity warningと合わせて、人間による確認へ回す。

Required outputは、Case 001では`6.1`〜`6.9`、Case 002/003では`6.1`〜`6.10`が、連続・重複なし・過不足なしで存在することをstatic intakeで確認する。各項目には実質的な本文が必要であり、見出しだけや空のテンプレートは有効な成果として扱わない。この件数は、凍結済みlaunch packetとcontract testで同期させる。

操作者はpackageごとに次を記録する。

- source result artifact ID。
- package生成日時。
- 含めたsectionの一覧。
- method-identity redactionの一覧。
- その他の編集。原則は`none`。
- package digest。SHA-256を推奨する。

主張、根拠、反証、confidence、deferを言い換えてはならない。許容するのは、formatの整形とmethod metadata / preregistered test IDの除去だけとする。

## 6. BR1 — Packageごとの独立レビュー

各packageを、**それぞれ別の新規reviewer context**で個別に評価する。他のpackageは見せない。

reviewerへ渡すものは次だけとする。

- fixed common source bundle、または同じsnapshotへ戻れる資料集合。
- 1つのblind package。
- `cognitive-dogfood-blind-review-template.md`の評価指示。

BR1では相対順位を付けない。

主に確認する点:

- 主要主張がsourceへ戻って確認できるか。
- 古い状態、訂正済み状態、条件付き設計、未実装契約を、現在の確定状態として誤採用していないか。
- 反証が形式だけでなく、実際に結論を変え得る内容になっているか。
- 不確実性と保留が適切に残っているか。
- unsupported leapや重要な見落としがないか。
- fixed questionに対する境界案と次の検証が、実証不足の内容に対応しているか。

## 7. BR2 — Package間の統合レビュー

4件のBR1が揃った後、別の新規reviewer contextでpackage間の比較を行う。

入力:

- 4つのblind package。
- 4つのBR1 review。
- 同一のcommon source bundle。
- Arm mappingは渡さない。

BR2で初めて、package間の差を見る。

最低限、次を区別する。

1. 全packageに共通して生き残った所見。
2. 一部packageにだけあり、sourceへ戻っても生き残った所見。
3. 一部packageにだけあるunsupported / overclaim。
4. temporal / contract correction、dissent、uncertaintyの保持に関する差。
5. fixed questionへの中核回答や境界が実質的に同じで、表現だけが異なる場合。
6. 結論は同じでも、decision / revisit可能性に差がある場合。
7. 方法上の工程が増えていても、成果物上の増分が確認できない場合。

BR2の段階でも、まだA/B/C/Dへunblindしない。

## 8. Verdictの凍結とUnblind

BR2のverdictをartifactとして保存し、内容を凍結した後にArm mappingを開示する。

unblind後に行うこと:

- BR2で見えた差をA/B/C/Dへ対応付ける。
- M1〜M9のrun recordと照合する。
- KJ Atlas increment、skill increment、D interaction、method-induced harmの候補を分類する。
- C/DのM9 / T9を、この時点で初めて成果差と併読する。
- findingをF0 / F1 / F2 / F3へ振り分ける。

unblindした後で、BR1 / BR2の元verdictを書き換えない。追加の解釈は`post-unblind synthesis`として別に残す。

## 9. Blind reviewの無効化・制約として記録する条件

次のいずれかが起きた場合、blindの制約として記録する。

- reviewerがArm mapping、raw record、PR #2805の比較仮説を事前に見た。
- package内に方法名が大量に残り、Armをほぼ特定できた。
- packageごとに異なるsource集合を与えた。
- BR1 reviewerが他のpackageを知っていた。
- BR2より前にArm mappingを開示した。
- reviewerへ事前登録済みの訂正・時点差チェックの意図を先に見せ、特定のfindingを探すよう誘導した。

この場合もreview自体は削除しない。`partial blind` / `unblinded`として残し、証拠の強さを下げて扱う。

## 10. この手順では直接測らないもの

blind reviewは、KJ AtlasのUI操作性、cultural-substrate-weavingを実行する負担、InquiryJourneyの認知摩擦を直接評価するものではない。これらはrun recordのM9 / T9と、product findingの振り分けで扱う。

また、blind reviewerの好みを「認知能力」の単一スコアへ変換しない。このレビューは、成果物が対象となる証拠へどの程度耐えられるかを確認するための一層である。