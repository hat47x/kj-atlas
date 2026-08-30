# Cognitive Dogfood — Shared Arm C/D UI Runbook

- Status: Frozen before first valid Case 001 raw run
- Applies to: Case 001〜003 Round 1 Arm C / D
- Product runtime reference: frozen Case product snapshot plus the same UI contract verified during preflight
- Related: case-specific launch packets, `cognitive-dogfood-run-record-template.md`, `cognitive-dogfood-case-portfolio-freeze.md`

## 1. 目的

Arm C/DでKJ Atlasを**完成後の清書ではなく分析中の外部表象**として実際に使い、その操作場所を探すための負担をKJ Atlasの認知摩擦M9やInquiryJourneyのT9へ誤計上しないためのoperator-only手順である。

このrunbookは各ケースの答え、カード、束、表札、価値仮説、AI境界案、local/collaboration境界案を与えない。分析内容は各caseのlaunch packetを正本とし、本書はUI/記録操作だけを固定する。

## 2. Case-specific inputs

開始時に対象caseだけを選び、他caseのlaunch packetや成果を同じfresh contextへ渡さない。

| Case | Product evidence bundle | Empty starter | C launch | D launch |
|---|---|---|---|---|
| 001 | `case-001-r1-product@2232b3bb26647e5c4a083f55bdbf83c161698649` | `doc_cognitive_case_001_starter.json` | `cognitive-dogfood-case-001-launch-atlas.md` | `cognitive-dogfood-case-001-launch-atlas-skill.md` |
| 002 | `case-002-r1-product@2232b3bb26647e5c4a083f55bdbf83c161698649` | `doc_cognitive_case_002_starter.json` | `cognitive-dogfood-case-002-launch-atlas.md` | `cognitive-dogfood-case-002-launch-atlas-skill.md` |
| 003 | `case-003-r1-product@2232b3bb26647e5c4a083f55bdbf83c161698649` | `doc_cognitive_case_003_starter.json` | `cognitive-dogfood-case-003-launch-atlas.md` | `cognitive-dogfood-case-003-launch-atlas-skill.md` |

Arm Dだけ、shared frozen canonical skill bundle `3988e12e5f7f316f377d3391e9486c8467a111d5 / src/ja-JP` を追加する。Arm Cへskill sourceを渡さない。

## 3. 実装上確認済みのUI経路

preflightで確認した現行経路は次である。

1. `DocumentV1` JSONを読み込み、現在documentを置換する。
2. Advancedを開く。
3. Work modeを有効化する。
4. Inquiry tabを開く。
5. 現在documentからInquiryJourneyを開始する。
6. 人間が意味上の節目と判断したときだけroundを記録する。
7. handoff候補を1件ずつ Adopt / edited / Hold / Skip / unanswered のまま扱う。
8. inquiry fileを保存し、再読込する。
9. resume briefから問い・理解変化・未解決点・次の観察・以前の成果へ戻る。
10. card lineageから元カード・元出典へ戻る。
11. 2 round以上ある場合にround間を比較する。
12. 必要なら過去roundから非破壊branchを作り、元branchを保持する。
13. branchを一括Undoできる。

代表的な英語locatorは以下である。localeをtreatment条件にはしない。

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

## 4. 分析開始前

1. fresh contextであることをrun recordへ記録する。
2. 対象caseのsanitized product evidence bundleだけが製品証拠として与えられていることを確認する。
3. Arm Cではcultural-substrate-weavingがcontextへ入っていないことを確認する。
4. Arm Dではshared frozen canonical skill bundleだけが追加されていることを確認する。
5. 対象case starterのcards / islands / evidenceLinks / readingOrder / narrativesが空であることを確認する。
6. starterをKJ Atlasへ読み込み、現在documentを置換する。
7. ここまでのUI探索・ファイル選択・locale確認・bundle配置はoperator/setup frictionとしてrun recordへ分離し、M9/T9へ算入しない。

## 5. 生カード化とInquiryJourney origin

1. case固有のfixed question / required outputを分析AIへ渡す。
2. frozen evidence bundleから生カード候補を作る。
3. source path / stable identifier / evidence timeを可能な限り残す。
4. fact / inference / uncertainty、古い状態 / 訂正済み状態 / 条件付き・未実装契約を必要に応じて区別する。
5. 結論を先取りしたカテゴリへ入れない。
6. model提案を人間が修正・棄却・保留した場合はproposal ledgerへ残す。
7. 最初の生カード集合を人間が一度確認しKJ Atlasへ入れた直後を標準InquiryJourney originとする。

`Start from the current document` は「その瞬間から思考を開始する」という意味ではなく、その時点の意味状態を探究originとして固定する操作である。この標準originは比較実験上の操作固定であり、W型stageの意味を変更しない。

## 6. 束ね・表札・関係

- 訴え・意味の近さから束ねる。既成カテゴリやcase文書の見出しをそのまま島へしない。
- 表札は一般分類名ではなく、束全体が何を訴えるかを表す候補とする。
- 対立・孤立・空白・未確定材料を残す。
- AIの束ね/表札/反対視点/要約等はproposalとして扱い、人間がAdopt / modify / Reject / Holdする。
- 正式proposal APIを使った場合は既存product auditへ人間判断を記録し、実験ledgerから参照する。
- product auditで表せないmodify理由やlater verdictはexperiment ledgerだけへ残す。
- 採用後も主要主張を元カード/sourceへ戻す。

## 7. RoundSnapshot / handoffを作る条件

experiment Round 1終了、一定カード枚数、AIが「まとまった」と述べたことはsnapshot条件にしない。

次のいずれかが起き、人間が後から戻る意味があると判断した場合だけ記録する。

- 問いの理解が変わった。
- 主要な束/関係が組み替わった。
- 強い反証で仮説・境界判断を修正した。
- 保留・未解決点を残して中断する。
- 外部資料または次の観察へ問いを渡す。
- 後段から戻る可能性がある判断点が生じた。

handoff reviewは全欄回答を要求しない。空欄を埋めるための推測をしない。

## 8. 意図的な中断・再開テスト

M6およびT9実使用証拠を得るため、自然な中断点がある場合に1回だけ次を行う。比較のためだけに不自然なroundを追加しない。

1. `Save inquiry file` で保存する。
2. 同じcase資料は維持したまま作業状態を閉じる。
3. inquiry fileを再読込する。
4. `Review resume brief` から、問い・理解変化・未解決点・次に確かめること・以前の成果を人間の記憶に頼らず復元できるか記録する。
5. `Trace a card's sources` で主要主張1件を元カード/出典へ戻す。
6. roundが2件以上ある場合だけ `Compare rounds` を使う。

「機能が存在した」ことではなく、再開・訂正・判断に実際に寄与したかを書く。

## 9. A型→B型と保持監査

1. 空間構造・束・関係・対立・空白を確認してからcase固有required outputへ文章化する。
2. 文章化後に元カードへ戻る。
3. 孤立、異論、不確実性、時点差、条件付き設計、未実装状態等が消えていないか監査する。
4. card/island数、AI proposal数、snapshot数、操作数を成果と数えない。

## 10. M9に含めるもの / 含めないもの

### M9へ含める

- カードを外部表象へ移すこと自体の負担。
- 束ね/表札/配置を人間が検査する負担。
- evidence/dissent/holdを残すために必要だった認知操作。
- A型からB型へ移るときに有益だった、または無駄だった往復。
- InquiryJourneyを意味上の節目で使う判断負担。
- resume/compare/lineageが役立たないのに操作だけ増えた場合の負担。

### M9へ含めない

- operatorがボタン位置を知らず探した時間。
- test用ファイルやbundleを配置する時間。
- GitHub connector / browser / local環境の準備時間。
- experiment用run recordを埋める管理時間。
- preflight/runbook作成時間。

後者で製品利用者にも再現しそうな問題を発見した場合は、M9へ後付けせずF0〜F2 findingとして別triageする。

## 11. T9へ返すもの

`DOMAIN-W-ITERATION-01` T9へ返すのは、InquiryJourneyの手動中核を実際に使って発生した反復摩擦だけとする。

- resume briefの材料を毎回探し直す。
- handoff前の見落とし確認が複数回同じ負担になる。
- compare後に重要差分を人間が繰り返し探索する。
- stale evidenceの検査を毎回同じ手順で行う。

AIでできたら便利そうという発想、一回だけ迷った操作、UI locator探索、通常のカード編集摩擦、experiment管理だけの作業はT9へ返さない。

単一run/caseでT9をDoneにしない。portfolioで固定したcross-case gateを維持する。

## 12. Finding triage

- **F0**: 単発、仮説、再現待ち。run/cardに残す。
- **F1**: 既存issueの未完了判断がその証拠を待っている。既存issueへ返す。
- **F2**: 現実のrunで再現し、既存issueで被覆できず、ACを書ける。新issue memo候補。
- **F3**: `ADR-0047` の実triggerを満たす長期decision。ADR候補。

単一ケースの「便利そう」「深く見えた」を理由に新機能/skill規則/ADRへ昇格させない。

## 13. 変更境界

最初の有効なCase 001 raw output保存前は、実装照合によるlocator・操作導線・operator setup説明の補正だけを許す。

最初の有効raw output保存後は、Cases 001〜003のanalysis treatment、fixed question、required output、snapshot、source manifestを結果に合わせて変えない。UI名変更等で実行不能になった場合はdeviationとして別記録し、旧条件を上書きしない。