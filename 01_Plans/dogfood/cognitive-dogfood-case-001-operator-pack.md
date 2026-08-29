# Cognitive Dogfood Case 001 — Operator Pack

- Status: Prepared
- Case: `cognitive-dogfood-case-001-product-purpose.md`
- Record template: `cognitive-dogfood-run-record-template.md`
- Rule: Arm A〜Dは**別コンテキスト**で実行する。同一会話の中でroleだけ切り替えない。

## 0. Operator rules

### 実行前

1. `cognitive-dogfood-case-001-product-purpose.md` のうち、armへ渡してよい範囲だけを確認する。
2. KJ Atlas product snapshotを `2232b3bb26647e5c4a083f55bdbf83c161698649` へ固定する。
3. B/Dでは cultural-substrate-weaving を `3988e12e5f7f316f377d3391e9486c8467a111d5` へ固定する。
4. PR #2805 の価値仮説、Case 0 audit、framework notes、Round 2 manifestをRound 1モデルへ見せない。
5. 各arm用に新しい会話/agent/sessionを用意する。
6. C/Dでは、認知dogfood用の別履歴方式を作らず、KJ Atlasに実装済みのInquiryJourneyを利用できる実行環境を優先する。

### 実行中

- 他armの出力を引用しない。
- arm固有に外部検索させない。資料不足は `Candidate source request` として返させる。
- modelが資料外の一般知識を使った場合は、その箇所を明示させる。
- 途中で人間が誘導質問をする場合、質問をrun recordへ残す。
- C/Dで正式AI proposal APIを使った場合は既存product auditへ人間判断を記録し、experiment proposal ledgerから参照する。
- product auditで表現しない `modify`、採否理由、`later_verdict` はexperiment ledgerへだけ残す。
- C/Dで意味上の節目が来た場合はInquiryJourney snapshot/handoffを使う。実験Roundの切替だけを理由にW型stageを変更しない。

### 実行後

- raw outputを先に保存し、評価のために書き換えない。
- required outputを別artifactに整理してよいが、rawへの参照を残す。
- arm aliasを付け、blind reviewerへはA/B/C/D名を見せない。
- C/Dでは、InquiryJourneyから再開したときに問い・未解決点・根拠へ戻れたかをrun recordへ記録する。

## 1. Common product source list — Round 1

全armへ同一snapshotの次を与える。

```text
README.md
ROADMAP.md
00_Prompt/kj_technique.md
01_Plans/adr/ADR-0032-product-value-realization-model.md
01_Plans/adr/ADR-0042-value-realness-validation-and-notice-exit.md
01_Plans/adr/ADR-0047-design-decision-adr-saturation-and-execution-first.md
01_Plans/adr/ADR-0057-w-type-cumulative-inquiry-model.md
01_Plans/issues/TEMPLATE.md
01_Plans/issues/issue-VALUE-MEASURE-01-measurement-harness-and-evidence-artifacts.md
01_Plans/issues/issue-VR-ROADMAP-01-value-to-social-goal-phase-baseline.md
01_Plans/issues/issue-DOMAIN-W-ITERATION-01-w-type-cumulative-inquiry-support.md
01_Plans/dogfood/doc_kj_atlas_dogfood_r1.json
01_Plans/dogfood/doc_kj_atlas_dogfood_r2.json
01_Plans/dogfood/doc_kj_atlas_dogfood_r3.json
01_Plans/dogfood/doc_kj_atlas_dogfood_r4.json
01_Plans/dogfood/doc_kj_atlas_dogfood_r5.json
01_Plans/issues/issue-DOGFOOD-17-opposing-viewpoint-ignores-target-claim.md
01_Plans/issues/issue-DOGFOOD-20-card-groups-not-theme-based.md
01_Plans/issues/issue-DOGFOOD-31-two-hundred-card-scale-exceeds-ai-operation-limits.md
01_Plans/issues/issue-DOGFOOD-32-one-line-heading-hierarchy-missing-for-large-canvases.md
```

`DOMAIN-W-ITERATION-01` を追加した理由は、ADR本文の `L0: Planned` だけを読んで現在実装を過小評価しないためである。このissueは2026-08-25時点でAC-1〜AC-13が完了し、T9/T10だけが外部トリガー待ちである。

## 2. Common question

全armで文字列を変えない。

```text
KJ Atlasは、既存のAIチャット、ホワイトボード、質的分析ツール、文書/issue管理では十分に満たしにくい、どの利用仕事のために存在するべきか。現在の設計・実装・dogfoodは、その価値をどこまで実現し、何をまだ実証できていないか。
```

## 3. Common required output

全armへ同じ内容を要求する。

```text
上記の問いを、与えられた資料だけを製品についての共通証拠として分析してください。

次を必ず含めてください。

1. KJ Atlasが解こうとしている利用者の仕事。
2. 既存手段で十分な領域と、不十分になり得る領域。
3. 現在のKJ Atlasが既に実現している価値。
4. 実証されていない価値仮説。
5. 最重要の反証、またはKJ Atlasが不要かもしれない条件。
6. 次に実施すべき検証/issue。
7. 主要主張ごとの根拠と、その根拠が示す時点。
8. 資料の中で、古い状態・後で訂正された状態・相互に緊張する記述を見つけた場合は、そのまま並べず現在状態との関係を示してください。
9. 判断を保留する箇所と、追加で必要な証拠。

資料外の一般知識を使う場合は、資料由来の主張と分けてください。
与えられていない外部資料を新たに検索せず、必要なら候補だけを挙げてください。
結論をKJ Atlasに好意的にする必要はありません。既存手段で十分、対象市場が狭い、価値仮説を棄却すべき、という結論も許容されます。
```

## 4. Arm A prompt — ordinary AI / ordinary document

Common question + common required outputに、次だけを追加する。

```text
通常の分析として進めてください。KJ法、KJ Atlasキャンバス、cultural-substrate-weaving等の追加方法は使用しません。
必要なメモや見出しは自由ですが、特定の方法論の手順を模倣する必要はありません。
```

### Aで禁止すること

- KJカード/島/表札をoperatorが要求する。
- cultural-substrate-weavingの規則をsystem/contextへ入れる。
- C/Dの出力を見せる。

## 5. Arm B prompt — ordinary document + cultural-substrate-weaving

Common question + common required outputに、次を追加する。

```text
KJ Atlasキャンバスは使いません。
指定された cultural-substrate-weaving の方法を適用してください。
領域固有のソフトウェア/プロダクト判断は与えられた資料と通常の領域知識で行い、文化体系由来の所見は来歴を保ち、対象へ戻して検証してください。
体系語を除いた後も成立する所見だけを最終成果へ残してください。
方法が増分を生まない場合は、その旨を明示してください。
```

### Bの記録追加

- activation判定
- framework candidates
- selected/rejected framework and reason
- removal/substitution result
- skill-specific surviving findings

## 6. Arm C operator procedure — KJ Atlas + ordinary AI

Common question + common required outputを分析AIへ渡す前後で、KJ Atlasを実際の外部表象として使用する。

### 最小手順

1. 共通資料から生カードを作る。
2. カードにsourceと事実/推論/不確実性を可能な範囲で保持する。
3. 既存文書からInquiryJourneyを開始し、作業文書と長期探究状態を分離する。
4. 初期カテゴリへ入れず、訴えの近さから束ねる。
5. 表札候補を作り、元カードへ戻して検査する。
6. 対立・孤立・空白を残す。
7. 必要ならAIの束ね/表札/反対視点等をproposalとして使う。
8. 正式proposal APIを使う場合、人間がAdopt/Reject/Holdを既存`/ai/proposals/audit`へ記録する。部分修正はexperiment ledger側で `modify` と元proposalへの参照を残す。
9. 人が「ここまでの意味状態を残す価値がある」と判断した節目でRoundSnapshot/handoffを作る。experiment Round 1終了を自動的なstage完了にしない。
10. A型構造からrequired outputを作る。
11. 最終出力を元カードへ戻して保持監査する。
12. 一度中断/再開する機会がある場合、InquiryJourneyの再開ブリーフ・比較・lineageが実際に役立つかを観察する。

### Cで禁止すること

- cultural-substrate-weavingを使用する。
- 文化体系から探索方向を追加する。
- KJ Atlasを単なる最終図の清書に使う。
- experiment metadataをInquiryJourneyのdomain contractへ詰め込む。
- 実験RoundをW型stageへ機械対応する。

## 7. Arm D operator procedure — KJ Atlas + cultural-substrate-weaving

Arm Cの手順に加え、指定commitのcultural-substrate-weavingを使用する。

```text
文化体系をKJカードの分類器として使わないでください。
体系は対象単独では出にくい位置・関係・状態・遷移候補を探索するために使い、その来歴を保持してください。
体系由来の問い/仮説は対象資料へ戻して検証し、体系語を除去しても成立するものだけを最終成果へ残してください。
KJ統合では体系から得た材料も他の生材料と同様に扱い、体系が束の構造を先に決めないようにしてください。
増分がなければ増分なしとしてください。
```

### Dの記録追加

BとCの追加項目を両方残す。

特に次を監査する。

- frameworkがキャンバス構造を先に決めなかったか。
- framework名を消すと消える所見を成果扱いしていないか。
- KJ Atlasとskillが同じ原理を二重に強化しただけではないか。
- framework由来の追加探索がInquiryJourneyのstage/iterationを不必要に増やしていないか。

## 8. T9 feedback capture — InquiryJourney AI support

C/Dの実利用中に、`DOMAIN-W-ITERATION-01` T9へ返せる材料を記録する。

AI支援候補を思いついた回数ではなく、**手動中核で実際に発生した反復摩擦**だけを対象にする。

| Observation | Record |
|---|---|
| operation | 問い / 引継ぎ / 差分 / 反証 / 再開 / その他 |
| manual burden | 何を人間が繰り返し行い、何が難しかったか |
| cognitive risk | omission / anchoring / stale evidence / loss of dissent / other |
| non-AI workaround | 現行機能でどう処理できたか |
| proposed AI help | proposal-onlyなら何を候補提示できるか |
| automation risk | 自動化すると何を先取り/上書きするか |
| verdict | needed / manual sufficient / conditional / unresolved |

複数ケースで同じ不足が再現するまでは、T9のPhase 3別issue化を急がない。

## 9. Prompt-equivalence audit

実行前に確認する。

- [ ] fixed questionは全arm完全一致。
- [ ] common required outputは全arm完全一致。
- [ ] product source listは全arm完全一致。
- [ ] A/BとC/Dで、方法以外の追加製品情報に差がない。
- [ ] A/Cにskill由来の探索規則を漏らしていない。
- [ ] B/Dのskill versionは一致。
- [ ] Round 2以前に外部競合/研究情報を混ぜていない。
- [ ] C/DだけがInquiryJourneyを使うことは「KJ Atlas外部表象というtreatment」の一部として事前登録されている。

## 10. Run artifact naming

```text
01_Plans/dogfood/cognitive-runs/case-001/
  round-1/
    <alias>-raw.md
    <alias>-result.md
    <alias>-record.md
    <alias>-canvas.json   # C/D only; product export/reference
    <alias>-inquiry-ref.md # C/D only; journey/bundle/snapshot IDsとproduct audit参照
  blind-review/
    package-<alias>.md
    verdict.md
  round-2/
    ...
```

A/B/C/Dをファイル名へ直接使わず、blind review完了まではランダムaliasを使用する。

## 11. Randomization

4armの実行順はCase IDから単純に固定せず、実行開始時にランダム化してrun recordへ記録する。

blind aliasも、operatorが評価者へ渡す前にランダム割当する。

## 12. Stop / invalidation

次ならrunを無理に採点せずinvalidまたはpartialとして残す。

- 他armの結果を参照した。
- product snapshotがarm間で異なった。
- Round 1中に一部armだけ外部検索を行った。
- B/Dで異なるskill versionを使用した。
- C/Dのcanvasが実際には外部表象として使われず、完成後の清書だけだった。
- C/DでInquiryJourneyが利用可能だったのに、実験都合だけで別履歴方式を発明した。
- experiment metadataをproduct schemaへ追加しないと実験できないような手順差が生じた。
- 大きなcontext lossやtool failureで必要資料を読めなかった。

invalid runも削除しない。失敗理由を残す。