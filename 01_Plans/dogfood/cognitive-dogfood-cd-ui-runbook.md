# 認知dogfood — Arm C/D 共通UI実行手順

- 状態: 最初の有効なCase 001 raw runより前に凍結済み
- 対象: Case 001〜003 Round 1 Arm C / D
- 製品runtimeの参照基準: 各Caseで固定したproduct snapshotと、preflightで確認済みの同一UI contract
- 関連: Case固有launch packet、`cognitive-dogfood-run-record-template.md`, `cognitive-dogfood-case-portfolio-freeze.md`

## 1. 目的

Arm C/Dでは、KJ Atlasを**完成後の清書場所ではなく、分析している最中の外部表象**として実際に使用する。

本書は、その際に「どこを操作すればよいか」を探す負担を、KJ Atlasの認知摩擦M9やInquiryJourneyのT9へ誤って計上しないための、操作者専用の手順である。

各Caseの答え、カード、束、表札、価値仮説、AI境界案、local / collaboration境界案は本書で与えない。分析内容は各Caseのlaunch packetを正本とし、本書ではUIと記録操作だけを固定する。

## 2. Caseごとの入力

開始時は対象Caseだけを選び、他Caseのlaunch packetや成果物を同じfresh contextへ渡さない。

| Case | Product evidence bundle | Empty starter | C launch | D launch |
|---|---|---|---|---|
| 001 | `case-001-r1-product@2232b3bb26647e5c4a083f55bdbf83c161698649` | `doc_cognitive_case_001_starter.json` | `cognitive-dogfood-case-001-launch-atlas.md` | `cognitive-dogfood-case-001-launch-atlas-skill.md` |
| 002 | `case-002-r1-product@2232b3bb26647e5c4a083f55bdbf83c161698649` | `doc_cognitive_case_002_starter.json` | `cognitive-dogfood-case-002-launch-atlas.md` | `cognitive-dogfood-case-002-launch-atlas-skill.md` |
| 003 | `case-003-r1-product@2232b3bb26647e5c4a083f55bdbf83c161698649` | `doc_cognitive_case_003_starter.json` | `cognitive-dogfood-case-003-launch-atlas.md` | `cognitive-dogfood-case-003-launch-atlas-skill.md` |

Arm Dだけに、固定済みの共通canonical skill bundle `3988e12e5f7f316f377d3391e9486c8467a111d5 / src/ja-JP`を追加する。Arm Cへskill sourceを渡さない。


### 2.1 KJ Atlas runtimeも固定product commitを使う

formal Round 1のC/Dで操作するKJ Atlas runtimeは、evidence bundleと同じ `hat47x/kj-atlas@2232b3bb26647e5c4a083f55bdbf83c161698649` を基準とする。Arm packageはruntime本体を同梱しないため、操作者が固定commitのcheckout / worktreeからKJ Atlasを起動する。

current mainや別commitのUIを、同じformal runのruntimeとして黙って代用しない。固定commitで本書の必要操作経路を実行できない場合は、UI探索時間をM9へ算入して帳尻を合わせるのではなく、そのrunを`blocked / invalid / partial`として理由を残し、別revisionが必要かを判断する。

この明示はproduct snapshotやtreatmentを変更するものではない。`cognitive-dogfood-case-portfolio-freeze.md`に既にある「3Caseで同じKJ Atlas product commitを使用する」という不変条件を、操作者が実行できる形へ展開したものである。

## 3. 実装上確認済みのUI経路

preflightで確認した現在の操作経路は次のとおり。

1. `DocumentV1` JSONを読み込み、現在のdocumentを置き換える。
2. Advancedを開く。
3. Work modeを有効にする。
4. Inquiry tabを開く。
5. 現在のdocumentからInquiryJourneyを開始する。
6. 人間が意味上の節目だと判断したときだけroundを記録する。
7. handoff候補を1件ずつ、Adopt / edited / Hold / Skip / unansweredのまま扱う。
8. inquiry fileを保存し、再度読み込む。
9. resume briefから、問い、理解の変化、未解決点、次の観察、以前の成果へ戻る。
10. card lineageから、元カードと元出典へ戻る。
11. 2 round以上ある場合だけ、round間を比較する。
12. 必要であれば過去roundから非破壊branchを作り、元のbranchを保持する。
13. branch全体をUndoできることを確認する。

実装上の代表的な英語locatorは次のとおり。UIのlocaleはtreatment条件にしない。

```text
Load document file / Load document.json
Replace current document
Advanced
Work mode
Inquiry
Start from the current document
Record R1 Problem setting, iteration 1
Review handoff
Save current handoff
Save inquiry file
Review resume brief
Trace a card's sources
Compare rounds
Start the next record from
Stage to explore next
Undo this branch
```

## 4. 分析を始める前の確認

1. fresh contextで開始したことをrun recordへ記録する。
2. 対象Caseのsanitized product evidence bundleだけが、製品に関する証拠として与えられていることを確認する。
3. Arm Cでは、cultural-substrate-weavingがコンテキストへ入っていないことを確認する。
4. Arm Dでは、固定済みの共通canonical skill bundleだけが追加されていることを確認する。
5. 対象Case starterのcards / islands / evidenceLinks / readingOrder / narrativesが空であることを確認する。
6. starterをKJ Atlasへ読み込み、現在のdocumentを置き換える。
7. ここまでに生じるUI探索、ファイル選択、locale確認、bundle配置の負担は`operator/setup friction`としてrun recordへ分離し、M9 / T9へ算入しない。

## 5. 生カード化とInquiryJourneyの起点

1. Case固有のfixed question / required outputを分析AIへ渡す。
2. frozen evidence bundleから生カード候補を作る。
3. source path / stable identifier / evidence timeを可能な限り残す。
4. 必要に応じて、fact / inference / uncertainty、古い状態 / 訂正済み状態 / 条件付き・未実装契約を区別する。
5. 結論を先取りしたカテゴリへカードを入れない。
6. model提案を人間が修正・棄却・保留した場合は、proposal ledgerへ残す。
7. 最初の生カード集合を人間が確認し、KJ Atlasへ入れた直後を標準のInquiryJourney originとする。

`Start from the current document`は、「その瞬間から思考を始める」という意味ではない。その時点までに外部化された意味状態を、探究のoriginとして固定する操作である。この標準originは比較実験上の操作を揃えるためのもので、W型stageの意味を変更しない。

## 6. 束ね・表札・関係を扱うときの原則

- カードの訴えや意味の近さから束ねる。既成カテゴリやCase文書の見出しを、そのまま島にしない。
- 表札は一般的な分類名ではなく、束全体が何を訴えているかを表す候補として扱う。
- 対立、孤立、空白、未確定の材料を残す。
- AIによる束ね、表札、反対視点、要約等はproposalとして扱い、人間がAdopt / modify / Reject / Holdする。
- 正式なproposal APIを使った場合は、既存product auditへ人間の判断を記録し、実験ledgerから参照する。
- product auditでは表せないmodify理由やlater verdictは、experiment ledger側にだけ残す。
- 採用後も、主要主張から元カード・sourceへ戻れることを確認する。

## 7. RoundSnapshot / handoffを作る条件

experiment Round 1が終わったこと、一定枚数のカードに達したこと、AIが「まとまった」と述べたことは、snapshotを作る理由にしない。

次のような変化が起き、人間が「後からこの状態へ戻る意味がある」と判断した場合だけ記録する。

- 問いの理解が変わった。
- 主要な束や関係を組み替えた。
- 強い反証によって仮説や境界判断を修正した。
- 保留や未解決点を残して中断する。
- 外部資料または次の観察へ問いを渡す。
- 後の段階から戻る可能性がある判断点が生じた。

handoff reviewでは、すべての欄を埋めることを求めない。空欄を埋めるために推測しない。

## 8. 自然な中断・再開の確認

M6およびT9の実使用証拠を得るため、自然な中断点がある場合に1回だけ次を行う。比較の都合だけで不自然なroundを追加しない。

1. `Save inquiry file`で保存する。
2. 同じCaseの資料は維持したまま、いったん作業状態を閉じる。
3. inquiry fileを再度読み込む。
4. `Review resume brief`を使い、問い、理解の変化、未解決点、次に確かめること、以前の成果を、人間の記憶だけに頼らず復元できるかを記録する。
5. `Trace a card's sources`で主要主張1件を元カード・出典へ戻す。
6. roundが2件以上ある場合だけ`Compare rounds`を使う。

「機能が存在した」という事実ではなく、再開、訂正、判断に実際に寄与したかを記録する。

## 9. A型からB型へ移るときの保持監査

1. 空間構造、束、関係、対立、空白を確認してから、Case固有のrequired outputへ文章化する。
2. 文章化した後で元カードへ戻る。
3. 孤立、異論、不確実性、時点差、条件付き設計、未実装状態等が消えていないかを確認する。
4. card / island数、AI proposal数、snapshot数、操作数を成果指標にしない。

## 10. M9へ含める負担と、含めない負担

### M9へ含める

- カードを外部表象へ移すこと自体の負担。
- 束ね、表札、配置を人間が検査する負担。
- evidence / dissent / holdを残すために必要だった認知操作。
- A型からB型へ移るときに生じた、有益または無益な往復。
- InquiryJourneyを意味上の節目で使うか判断する負担。
- resume / compare / lineageが役立たないのに、操作だけが増えた場合の負担。

### M9へ含めない

- 操作者がボタンの場所を知らずに探した時間。
- test用ファイルやbundleを配置する時間。
- GitHub connector、browser、local環境の準備時間。
- 実験用run recordを記入する管理時間。
- preflight / runbookを作成した時間。

後者の作業から、一般の製品利用者にも再現しそうな問題を発見した場合は、M9へ後付けで入れない。F0〜F2のfindingとして別に振り分ける。

## 11. T9へ返す証拠

`DOMAIN-W-ITERATION-01` T9へ返すのは、InquiryJourneyの手動中核を実際に使ったことで発生した反復摩擦だけとする。

たとえば次のようなものを対象にする。

- resume briefに必要な材料を毎回探し直す。
- handoff前の見落とし確認が、何度も同じ負担になる。
- compare後に重要な差分を人間が繰り返し探す。
- stale evidenceの検査を毎回同じ手順で行う。

「AIでできたら便利そう」という発想、一度だけ迷った操作、UI locator探索、通常のカード編集摩擦、実験管理だけの作業はT9へ返さない。

単一run / CaseだけでT9をDoneにしない。portfolioで固定したcross-case gateを維持する。

## 12. Findingの振り分け

- **F0**: 単発の所見、仮説、再現待ち。run / cardに残す。
- **F1**: 既存issueの未完了判断が、その種類の証拠を待っている。既存issueへ戻す。
- **F2**: 実際のrunで再現し、既存issueでは扱えず、acceptance criteriaを書ける。新しいissue memoの候補。
- **F3**: `ADR-0047`の実トリガーを満たす長期的なdecision。ADR候補。

単一Caseの「便利そう」「深く見えた」という印象だけを理由に、新機能、skill規則、ADRへ昇格させない。

## 13. 変更してよい範囲

最初の有効なCase 001 raw outputを保存する前は、実装照合によるlocator、操作導線、operator setup説明の補正だけを許容する。

最初の有効なraw outputを保存した後は、Case 001〜003のanalysis treatment、fixed question、required output、snapshot、source manifestを、結果に合わせて変更しない。UI名の変更等で実行不能になった場合は、deviationとして別に記録し、旧条件を上書きしない。