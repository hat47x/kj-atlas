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

### 実行中

- 他armの出力を引用しない。
- arm固有に外部検索させない。資料不足は `Candidate source request` として返させる。
- modelが資料外の一般知識を使った場合は、その箇所を明示させる。
- 途中で人間が誘導質問をする場合、質問をrun recordへ残す。
- C/DでAI提案を採用/修正/棄却した操作はproposal ledgerへ残す。

### 実行後

- raw outputを先に保存し、評価のために書き換えない。
- required outputを別artifactに整理してよいが、rawへの参照を残す。
- arm aliasを付け、blind reviewerへはA/B/C/D名を見せない。

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
3. 初期カテゴリへ入れず、訴えの近さから束ねる。
4. 表札候補を作り、元カードへ戻して検査する。
5. 対立・孤立・空白を残す。
6. 必要ならAIの束ね/表札/反対視点等をproposalとして使う。
7. 人間がproposalをaccept/modify/reject/deferする。
8. A型構造からrequired outputを作る。
9. 最終出力を元カードへ戻して保持監査する。

### Cで禁止すること

- cultural-substrate-weavingを使用する。
- 文化体系から探索方向を追加する。
- KJ Atlasを単なる最終図の清書に使う。

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

## 8. Prompt-equivalence audit

実行前に確認する。

- [ ] fixed questionは全arm完全一致。
- [ ] common required outputは全arm完全一致。
- [ ] product source listは全arm完全一致。
- [ ] A/BとC/Dで、方法以外の追加製品情報に差がない。
- [ ] A/Cにskill由来の探索規則を漏らしていない。
- [ ] B/Dのskill versionは一致。
- [ ] Round 2以前に外部競合/研究情報を混ぜていない。

## 9. Run artifact naming

```text
01_Plans/dogfood/cognitive-runs/case-001/
  round-1/
    <alias>-raw.md
    <alias>-result.md
    <alias>-record.md
    <alias>-canvas.json   # C/D only
  blind-review/
    package-<alias>.md
    verdict.md
  round-2/
    ...
```

A/B/C/Dをファイル名へ直接使わず、blind review完了まではランダムaliasを使用する。

## 10. Randomization

4armの実行順はCase IDから単純に固定せず、実行開始時にランダム化してrun recordへ記録する。

blind aliasも、operatorが評価者へ渡す前にランダム割当する。

## 11. Stop / invalidation

次ならrunを無理に採点せずinvalidまたはpartialとして残す。

- 他armの結果を参照した。
- product snapshotがarm間で異なった。
- Round 1中に一部armだけ外部検索を行った。
- B/Dで異なるskill versionを使用した。
- C/Dのcanvasが実際には外部表象として使われず、完成後の清書だけだった。
- 大きなcontext lossやtool failureで必要資料を読めなかった。

invalid runも削除しない。失敗理由を残す。