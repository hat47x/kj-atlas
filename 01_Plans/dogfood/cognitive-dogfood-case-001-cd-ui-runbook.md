# Cognitive Dogfood Case 001 — Arm C/D UI Runbook

- Status: Prepared / operator-only
- Date: 2026-08-30
- Scope: Case 001 Round 1 Arm C / D
- Product source snapshot: `main@2232b3bb26647e5c4a083f55bdbf83c161698649`
- Related: `cognitive-dogfood-case-001-operator-pack.md`, `cognitive-dogfood-run-record-template.md`, `cognitive-dogfood-case-001-preflight.md`

## 1. 目的

Arm C/Dの実行者がKJ Atlasの操作場所を探すために費やした時間を、KJ Atlasそのものの認知摩擦（M9）やInquiryJourneyの手動摩擦（T9）へ誤計上しないためのoperator-only runbookである。

この文書はCase 001の問いへの答え、カード、束、表札、価値仮説、反証候補を一切与えない。方法treatmentの操作入口だけを固定する。

比較armへ渡す分析promptは `cognitive-dogfood-case-001-operator-pack.md` を正本とし、本書の操作説明を分析内容へ追加しない。

## 2. 実装上確認済みの経路

現行E2Eでは次の経路が通っている。

1. `DocumentV1` JSONを読み込み、現在documentを置換する。
2. Advancedを開く。
3. Work modeを有効化する。
4. Inquiry tabを開く。
5. 現在documentからInquiryJourneyを開始する。
6. 人間が意味上の節目と判断したときだけroundを記録する。
7. handoff候補を1件ずつ Adopt / edited / Hold / Skip / unanswered のまま扱う。
8. inquiry fileを保存し、再読込できる。
9. resume briefから問い・理解変化・未解決点・次の観察・以前の成果へ戻る。
10. card lineageから元カード・元出典へ戻る。
11. 2 round間を比較する。
12. 過去roundから非破壊branchを作り、元branchを保持する。
13. branchを一括でUndoできる。

英語localeのE2E上の代表locator名は次のとおり。

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

実runでは利用者に自然なUI localeを使ってよい。上記英語名は操作位置を一意に照合するための実装参照であり、英語UI使用をtreatment条件にしない。

## 3. Arm C/D開始手順

### 3.1 分析開始前

1. fresh contextであることをrun recordに記録する。
2. common product source 20件が固定snapshotから与えられていることを確認する。
3. Arm Cではcultural-substrate-weavingがcontextへ入っていないことを確認する。
4. Arm Dでは指定skill snapshotだけが追加されていることを確認する。
5. `doc_cognitive_case_001_starter.json` は空documentであり、結論やカードが事前投入されていないことを確認する。
6. starterをKJ Atlasへ読み込む。初回start panelから読む場合も、Share & Reproduce経由で読む場合も、validation後に現在documentを置換する。
7. この時点までのUI探索・ファイル選択・locale確認は **operator setup** として記録し、M9/T9へ算入しない。

### 3.2 生カード化

1. common questionとcommon required outputを分析AIへ渡す。
2. common sourceから生カード候補を作る。
3. カード本文へ結論を先取りしたカテゴリ名を付けない。
4. source / 時点 / fact-inference-uncertaintyを可能な範囲で残す。
5. model提案を人間が修正・棄却・保留した場合はproposal ledgerへ残す。
6. 生カードをKJ Atlasへ入れた後に、InquiryJourneyを現在documentから開始する。

`Start from the current document` は「この瞬間から分析を始める」という意味ではなく、現在の意味状態を探究のoriginとして固定する操作である。生カード化前に開始しても契約違反ではないが、Case 001では比較可能性のため **最初の生カード集合を一度人間確認した直後** を標準originとする。

この標準originは実験上の操作固定であり、W型stageの意味を変更しない。

## 4. RoundSnapshot / handoffを作る条件

experiment Round 1終了、一定カード枚数、AIが「まとまった」と述べたことはsnapshot条件にしない。

次のいずれかが起き、人間が後から戻る意味があると判断した場合だけ記録する。

- 問いの理解が変わった。
- 主要な束/関係が組み替わった。
- 強い反証で仮説を修正した。
- 保留・未解決点を残して中断する。
- 外部資料または次の観察へ問いを渡す。
- 後段から戻る可能性がある判断点が生じた。

handoff reviewは全欄回答を要求しない。E2Eではunanswered candidateを残した状態で保存可能である。空欄を埋めるための推測をしない。

## 5. 意図的な中断・再開テスト

M6およびT9実使用証拠を得るため、自然な中断点がある場合に1回だけ次を行う。比較のためだけに不自然なroundを追加しない。

1. `Save inquiry file` で保存する。
2. 同じCase 001資料は維持したまま作業状態を閉じる。
3. inquiry fileを再読込する。
4. `Review resume brief` を開き、次が人間の記憶に頼らず復元できるか記録する。
   - 現在の問い。
   - 理解の変化。
   - 未解決点。
   - 次に確かめること。
   - 以前の成果。
5. `Trace a card's sources` で主要主張1件を元カード/出典へ戻す。
6. roundが2件以上ある場合のみ `Compare rounds` を使用する。

「機能が存在した」ことではなく、**再開・訂正・判断に実際に寄与したか**をrun recordへ書く。

## 6. M9に含めるもの / 含めないもの

### M9へ含める

- カードを外部表象へ移すこと自体の負担。
- 束ね/表札/配置を人間が検査する負担。
- evidence/dissent/holdを残すために必要だった認知操作。
- A型からB型へ移るときに有益だった、または無駄だった往復。
- InquiryJourneyを意味上の節目で使う判断負担。
- resume/compare/lineageが役立たないのに操作だけ増えた場合の負担。

### M9へ含めない

- operatorがボタン位置を知らず探した時間。
- test用ファイルをどこへ保存するか決める時間。
- GitHub connector / browser / local環境の準備時間。
- experiment用run recordを埋める管理時間。
- 本runbook作成以前のpreflight時間。

後者で製品利用者にも再現しそうな問題を発見した場合は、M9へ後付けせずfindingとしてF0〜F2判定する。

## 7. T9へ返すもの

`DOMAIN-W-ITERATION-01` T9へ返すのは、InquiryJourneyの手動中核を実際に使って発生した反復摩擦だけとする。

例:

- resume briefの材料を毎回人間が同じ形で探し直した。
- handoff候補を作る前段の見落とし確認が複数回同じ負担になった。
- compare後に重要な差分を人間が繰り返し探索した。
- stale evidenceの検査を毎回同じ手順で行った。

次はT9へ返さない。

- AIでできたら便利そう、という発想だけ。
- 一回だけ迷った操作。
- UI locatorを知らなかったための探索。
- KJ Atlas一般のカード編集/配置摩擦。
- experiment管理上だけ必要な作業。

## 8. finding triage

run中の所見は `cognitive-dogfood-execution-plan.md` のF0〜F3を適用する。

- **F0**: 単発、仮説、再現待ち。run/cardに残す。
- **F1**: 既存issueの未完了判断がその証拠を待っている。既存issueへ返す。
- **F2**: 現実のrunで再現し、既存issueで被覆できず、ACを書ける。新issue memo。
- **F3**: `ADR-0047` R-1〜R-4を満たす長期decision。ADR候補。

Case 001単独でT9をDoneにしない。Case 001〜003の少なくとも2ケースで同型摩擦が再現するという事前登録条件を維持する。

## 9. このrunbook自体の変更境界

最初のArm C raw output保存前は、実装照合による操作名・導線の補正を許す。

最初のraw output保存後は、分析treatmentや成功条件を変えない。UI名変更等で実行不能になった場合だけdeviationを記録し、比較結果とは分けて補正する。
