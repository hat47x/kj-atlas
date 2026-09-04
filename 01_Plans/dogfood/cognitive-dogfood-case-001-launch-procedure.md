# Cognitive Dogfood Case 001 — 分離実行手順

- 状態: 最初のraw run実行前に準備済み
- 対象: Case 001 Round 1 / P1
- 事前登録済みの実行順: **C → D → B → A**
- Product bundle ID: `case-001-r1-product@2232b3bb26647e5c4a083f55bdbf83c161698649`
- 操作者専用skill manifest ID: `case-001-skill-ja@3988e12e5f7f316f377d3391e9486c8467a111d5`
- B/Dから見えるskill bundle ID: `cognitive-dogfood-skill-ja@3988e12e5f7f316f377d3391e9486c8467a111d5`

## 1. 操作者側の準備

この手順書と操作者専用manifest類は、各Armを実行する独立した新規コンテキストには渡さない。

### 1.0 原則として使用する実行パッケージ — Actions artifact

有効なrunでは、`Cognitive dogfood freeze` workflowが生成した、対象Case・Arm専用のartifactを新規コンテキストへの入力パッケージとして使用する。

Case 001のartifact名は次のとおり。

- A: `cognitive-dogfood-case-001-arm-a`
- B: `cognitive-dogfood-case-001-arm-b`
- C: `cognitive-dogfood-case-001-arm-c`
- D: `cognitive-dogfood-case-001-arm-d`

各パッケージには、そのArmへ見せてよい資料だけを入れる。

- 全Arm: sanitized product evidence と、そのArm専用の`launch.md`。
- B/D: 上記に加えて、固定済みのcanonical skill bundle。
- C/D: 上記に加えて、空の`starter.json`。

run開始前に、Actions artifactのmetadataから次の値を操作者側で保存し、`cognitive-dogfood-run-record-template.md`へ転記する。

- artifact name。
- workflow head SHA。
- artifact digest（`sha256:<64 hex>`）。

artifactの保持期間である14日を過ぎた後、同じ固定入力からパッケージを再生成した場合でも、過去のrun recordを新しいartifact identityへ書き換えない。各runについて、実際に使用したパッケージのidentityをそのまま残す。

以下の1.1、1.2に示す手動bundle生成は、Actions artifactを再現するための**診断・復旧・同等性確認専用**とする。Round 1の有効な比較runにはActions artifactを使用する。Actions artifactを利用できない状態で手動bundleだけを用いたrunは、artifact name / workflow head / digestを持たないためstatic intakeを通さず、`partial` または `invalid` として理由を記録する。

比較条件そのものを改訂し、手動パッケージを有効な入力として扱う必要が生じた場合は、既存条件を上書きしない。別revisionまたはdeviationとして、実行前に記録する。

### 1.1 Product evidence bundle

完全な`kj-atlas`のgit checkoutまたはworktreeから、全Arm共通のbundleを一度だけ生成する。Case 001専用の旧builderは使用せず、全cognitive-dogfood Case共通のsanitized frozen-source builderを使用する。

```bash
python 01_Plans/dogfood/prepare_cognitive_frozen_source_bundle.py \
  --repo-root /path/to/kj-atlas \
  --manifest 01_Plans/dogfood/cognitive-dogfood-case-001-round1-source-manifest.json \
  --output /path/to/operator-workspace/case001-product
```

成功条件は次のとおり。

- 20件すべてが固定commitから抽出される。
- 各Git blob SHAが操作者専用manifestと一致する。
- bundle内の`_experiment/bundle-manifest.json`に`sourceCount: 20`が記録される。
- `bundleId`が`case-001-r1-product@2232b3bb26647e5c4a083f55bdbf83c161698649`と一致する。
- `operatorOnlyMetadataCopied=false`であり、excluded input、skill treatment、cross-arm情報など、操作者だけが知るmetadataがArm側のbundleへコピーされていない。
- bundle外のplan、PR、Case 0資料をArmへ追加しない。

同じproduct bundleをA/B/C/Dのすべてへ渡す。Armごとに作り直す必要はない。

### 1.2 Canonical skill bundle — B/Dのみ

完全な`cultural-substrate-weaving`のgit checkoutまたはworktreeから、B/D共通の日本語正本bundleを一度だけ生成する。

```bash
python 01_Plans/dogfood/prepare_cognitive_case001_skill_bundle.py \
  --skill-repo-root /path/to/cultural-substrate-weaving \
  --output /path/to/operator-workspace/case001-skill-ja
```

成功条件は次のとおり。

- `src/ja-JP`の正本12件だけが固定commitから抽出される。
- 各Git blob SHAが操作者専用manifestと一致する。
- `_experiment/skill-bundle-manifest.json`に`sourceCount: 12`が記録される。
- Arm側から見える`manifestId`が`cognitive-dogfood-skill-ja@3988e12e5f7f316f377d3391e9486c8467a111d5`である。
- `caseScopedMetadataIncluded=false`であり、Arm側から見えるskill subtreeに`case-001` / `Case 001`を含めない。
- docs、evals、plugins、adapters、AGENTS、README、PR discussionを含めない。

操作者専用skill manifestがCase 001に由来する事実は、Case 001の結果を見る前に固定した履歴として保持する。ただし、そのCase identityはB/DのArm側bundleへコピーしない。A/Cにはskill bundleもskill manifestも渡さない。


### 1.3 Frozen KJ Atlas runtime — C/Dのみ

C/Dで実際に操作するKJ Atlasは、formal product snapshotと同じ `2232b3bb26647e5c4a083f55bdbf83c161698649` のcheckout / worktreeから起動する。Actions artifactは分析入力を隔離するためのpackageであり、KJ Atlas runtimeそのものを含まない。

run開始前に、操作者は固定commitでC/D共通runbookの必要UI経路を使用できることを確認する。現在mainや別commitしか起動できない場合、それを元のRound 1へ黙って代用しない。固定runtimeで実行不能なら`blocked / invalid / partial`として理由を保存し、別revisionとして扱う。

A/BはKJ Atlas UIをtreatmentとして使用しないため、このruntime起動手順の対象外である。

## 2. Armの実行順と入力

| 実行順 | Arm | 新規コンテキストへ渡すもの | KJ Atlas UI | Skill bundle |
|---:|---|---|---|---|
| 1 | C | `cognitive-dogfood-case-001-arm-c` package | 使用する | なし |
| 2 | D | `cognitive-dogfood-case-001-arm-d` package | 使用する | あり |
| 3 | B | `cognitive-dogfood-case-001-arm-b` package | 使用しない | あり |
| 4 | A | `cognitive-dogfood-case-001-arm-a` package | 使用しない | なし |

新規コンテキストには、この表やArm名をあえて伝えない。artifact内の`launch.md`だけを実行指示として渡し、run recordを作成するときに操作者がArm metadataとartifact identityを補う。

## 3. C/DでのKJ Atlas実行

C/Dでは、操作者だけが`cognitive-dogfood-case-001-cd-ui-runbook.md`を参照する。分析を行うAIへrunbook全体を見せる必要はない。

最低限、次の順序で進める。

1. artifact内の空の`starter.json`を起点にする。
2. `launch.md`に従い、AIが生カード候補を作る。
3. 人間が最初の生カード集合を確認し、KJ Atlasへ入れる。
4. その後にInquiryJourneyの起点を作る。
5. KJ統合、必要なproposal、人間による採否、意味上のsnapshot / handoffを進める。
6. required outputを作成する。
7. 元カードへ戻り、保持監査を行う。
8. 無理のない中断点があれば一度resumeを試し、M6 / M9 / T9に関係する観察だけを操作者側の記録へ残す。

Dでは、skill frameworkが束や表札を先回りして決めていないかも操作者が確認する。

## 4. Raw artifactの凍結

各runは評価を始める前に、reviewerから見えない操作者用workspaceへ次のファイルを凍結する。

```text
<alias>-raw.md
<alias>-result.md
<alias>-record.md
<alias>-canvas.json       # C/D
<alias>-inquiry-ref.md    # C/D
```

運用上の原則は次のとおり。

- raw / resultを、後の評価結果に合わせて書き換えない。
- invalid / partial runも削除しない。
- blind verdictが確定する前に、Arm identityを含むartifactをpublic PR branchへpushしない。
- run recordには、実際に使用したActions artifactのname / workflow head / digestを残す。

## 5. Static intake

run recordを完成させ、中立なblind aliasを割り当てた後で実行する。

```bash
python 01_Plans/dogfood/validate_cognitive_run_records.py \
  /path/to/operator-workspace/<alias>-record.md
```

`PASS`しないrunはBR1へ送らない。失敗理由がexperiment recordの不足なのか、実際のproduct / manual-core defectなのかを分けて記録する。

validatorは、Case / Armから期待されるartifact名と、workflow head / digestの書式も検査する。さらに、Case 001では`6.1`〜`6.9`、Case 002/003では`6.1`〜`6.10`のrequired outputが、連続・重複なし・過不足なしで存在することを確認する。各項目には実質的な本文が必要であり、見出しだけや空のテンプレートは有効な結果として扱わない。

また、訂正・時点差チェックには解釈本文を、M1〜M9には観察内容または`not measurable`とその理由を残す。validatorはこれらの記録が存在することだけを確認し、認知的な質そのものは採点しない。

## 6. Blind package

static intakeに合格した後で生成する。

```bash
python 01_Plans/dogfood/build_cognitive_blind_package.py \
  /path/to/operator-workspace/<alias>-record.md \
  /path/to/operator-workspace/blind/package-<alias>.md
```

builder自身もstatic intakeを実行するため、invalid / contaminated / incompleteなrecordからblind packageは生成できない。

warningが出た場合は、本文からmethod identityを推測できないかを人間が確認する。ただし、隠すために主張・根拠・反証を言い換えない。

blind reviewは`cognitive-dogfood-blind-review-protocol.md`に従い、BR1 → BR2 → verdict freeze → unblindの順で進める。

## 7. 汚染を検出した場合の停止条件

次のいずれかが起きた場合、そのrunを無理に有効化しない。

- 新規コンテキストが、操作者専用manifest、Case 0、PR #2805の評価議論、Round 2資料を読んだ。
- 新規コンテキストが、bundle外のKJ Atlas repositoryを探索した。
- B/Dが、skill bundle外のskill repository資料を探索した。
- A/Cへ、skill bundleまたはskill評価情報が渡った。
- 一部のArmだけが、外部Web検索や追加sourceを行った。
- 現在の比較設計を行った会話を、そのままArm実行へ再利用した。

該当する場合はinvalid / partialの理由を記録し、結果を比較へ混ぜない。

## 8. 現在の次工程

最初に実行する有効runは **C** である。

操作者は、現在の比較設計を行ったコンテキストとは別に新規コンテキストを作り、そこへ`cognitive-dogfood-case-001-arm-c` artifactの内容だけを渡す。KJ Atlas UIは人間の操作者が実際に使用する。

起動時点では、Case 0 outcome、T1〜T3の評価意図、M1〜M9、他Arm、cultural-substrate-weaving、Round 2外部比較の情報を、新規の分析コンテキストへ与えない。