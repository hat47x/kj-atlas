# Cognitive Dogfood Case 001 — Isolated-arm launch procedure

- Status: Prepared before first raw run
- Scope: Case 001 Round 1 P1 execution
- Preregistered order: **C → D → B → A**
- Product bundle ID: `case-001-r1-product@2232b3bb26647e5c4a083f55bdbf83c161698649`
- Operator-only skill manifest ID: `case-001-skill-ja@3988e12e5f7f316f377d3391e9486c8467a111d5`
- Arm-visible skill bundle ID for B/D: `cognitive-dogfood-skill-ja@3988e12e5f7f316f377d3391e9486c8467a111d5`

## 1. Operator-only preparation

この手順とoperator manifest類はfresh arm contextへ渡さない。

### 1.0 Preferred execution package — Actions artifact

有効runでは、`Cognitive dogfood freeze` workflowが生成した当該case/arm専用artifactをfresh contextへの入力packageとして使う。

Case 001のartifact名:

- A: `cognitive-dogfood-case-001-arm-a`
- B: `cognitive-dogfood-case-001-arm-b`
- C: `cognitive-dogfood-case-001-arm-c`
- D: `cognitive-dogfood-case-001-arm-d`

packageには、そのarmへ見せてよいものだけが入る。

- 全arm: sanitized product evidence + 自armの`launch.md`。
- B/D: 上記に加えfrozen canonical skill bundle。
- C/D: 上記に加えempty `starter.json`。

run開始前にActions artifact metadataから次をoperator側で保存し、`cognitive-dogfood-run-record-template.md`へ転記する。

- artifact name。
- workflow head SHA。
- artifact digest (`sha256:<64 hex>`)。

artifactの14日retention後に同じfrozen inputから再生成した場合も、古いrun recordを新しいartifact identityへ書き換えない。各runが実際に使ったpackage identityを残す。

以下1.1/1.2の手動bundle生成は、Actions artifactを再現するための**診断・復旧・同等性確認専用**である。Round 1のvalid比較runにはActions artifactを使用する。Actions artifactを利用できない状態で手動bundleだけを使ったrunは、artifact name / workflow head / digestを持たないためstatic intakeをPASSさせず、`partial` または `invalid` として理由を残す。比較条件自体を改訂して手動packageをvalid化する必要が生じた場合は、既存条件を上書きせず別revision/deviationとして事前に記録する。

### 1.1 Product evidence bundle

完全な `kj-atlas` git checkout/worktreeから、全arm共通bundleを一度生成する。Case固有の旧builderではなく、全cognitive-dogfood caseで共通のsanitized frozen-source builderを使用する。

```bash
python 01_Plans/dogfood/prepare_cognitive_frozen_source_bundle.py \
  --repo-root /path/to/kj-atlas \
  --manifest 01_Plans/dogfood/cognitive-dogfood-case-001-round1-source-manifest.json \
  --output /path/to/operator-workspace/case001-product
```

成功条件:

- 20件すべてが固定commitから抽出される。
- 各Git blob SHAがoperator manifestと一致する。
- bundleの `_experiment/bundle-manifest.json` に `sourceCount: 20` がある。
- `bundleId` が `case-001-r1-product@2232b3bb26647e5c4a083f55bdbf83c161698649` と一致する。
- `operatorOnlyMetadataCopied=false` であり、excluded input、skill treatment、cross-arm情報などoperator-only metadataがarm-visible bundleへコピーされていない。
- bundle外のplan/PR/Case 0資料をarmへ追加しない。

この同一product bundleをA/B/C/Dすべてへ渡す。armごとに作り直す必要はない。

### 1.2 Canonical skill bundle — B/D only

完全な `cultural-substrate-weaving` git checkout/worktreeから、B/D共通の日本語正本bundleを一度生成する。

```bash
python 01_Plans/dogfood/prepare_cognitive_case001_skill_bundle.py \
  --skill-repo-root /path/to/cultural-substrate-weaving \
  --output /path/to/operator-workspace/case001-skill-ja
```

成功条件:

- `src/ja-JP` 正本12件だけが固定commitから抽出される。
- 各Git blob SHAがoperator manifestと一致する。
- `_experiment/skill-bundle-manifest.json` に `sourceCount: 12` がある。
- arm-visible `manifestId` は `cognitive-dogfood-skill-ja@3988e12e5f7f316f377d3391e9486c8467a111d5` である。
- `caseScopedMetadataIncluded=false` であり、arm-visible skill subtreeに `case-001` / `Case 001` を含めない。
- docs/evals/plugins/adapters/AGENTS/README/PR discussionは入っていない。

operator-only skill manifestがCase 001に由来することは、Case 001結果を見る前に固定した履歴として保持する。ただし、そのcase identityはB/Dのarm-visible bundleへコピーしない。A/Cへskill bundleまたはskill manifestを渡さない。

## 2. Arm launch matrix

| Execution | Arm | Fresh context receives | KJ Atlas UI | Skill bundle |
|---:|---|---|---|---|
| 1 | C | `cognitive-dogfood-case-001-arm-c` package | yes | no |
| 2 | D | `cognitive-dogfood-case-001-arm-d` package | yes | yes |
| 3 | B | `cognitive-dogfood-case-001-arm-b` package | no | yes |
| 4 | A | `cognitive-dogfood-case-001-arm-a` package | no | no |

fresh contextにはこのmatrixやarm名をわざわざ教えず、artifact内の`launch.md`をtask instructionとして渡す。run record作成時にoperatorがarm metadataとartifact identityを補う。

## 3. C/D product execution

C/Dでは別途operator-onlyの `cognitive-dogfood-case-001-cd-ui-runbook.md` を人間operatorが参照する。分析AIへrunbook全体を見せる必要はない。

最低限:

1. artifact内の空`starter.json`を起点にする。
2. `launch.md`に従ってAIが生カード候補を作る。
3. humanが最初の生カード集合をレビューしKJ Atlasへ入れる。
4. その後にInquiryJourney originを作る。
5. KJ統合、必要なproposal、人間の採否、意味上のsnapshot/handoffを進める。
6. required outputを作成する。
7. 元カードへ戻す保持監査をする。
8. 可能なら自然な中断点で一度resumeを試し、M6/M9/T9用の観察だけをoperator recordへ残す。

Dではskill frameworkが束・表札を先に決めていないかもoperatorが監査する。

## 4. Raw artifact freeze

各runは評価前に、reviewerから見えないoperator workspaceへ次を凍結する。

```text
<alias>-raw.md
<alias>-result.md
<alias>-record.md
<alias>-canvas.json       # C/D
<alias>-inquiry-ref.md    # C/D
```

- raw/resultを後の評価に合わせて書き換えない。
- invalid/partial runも削除しない。
- public PR branchへarm identity付きartifactをblind verdict前にpushしない。
- run recordには実際に使用したActions artifactのname / workflow head / digestを残す。

## 5. Static intake

run recordを完成させ、中立blind aliasを割り当ててから実行する。

```bash
python 01_Plans/dogfood/validate_cognitive_run_records.py \
  /path/to/operator-workspace/<alias>-record.md
```

`PASS`しないrunをBR1へ送らない。failの原因がexperiment record deficiencyか、実際のproduct/manual-core defectかを分ける。

validatorは、case/armから期待されるartifact名と、workflow head/digestの書式も検査する。さらにCase 001は`6.1`〜`6.9`、Case 002/003は`6.1`〜`6.10`のrequired outputが連続・重複なし・過不足なしで存在することを確認する。artifact内容そのものの認知品質は採点しない。

## 6. Blind package

static intake後に生成する。

```bash
python 01_Plans/dogfood/build_cognitive_blind_package.py \
  /path/to/operator-workspace/<alias>-record.md \
  /path/to/operator-workspace/blind/package-<alias>.md
```

warningが出た場合はmethod identityが本文から推測可能かを人手で確認する。主張・根拠・反証を言い換えて隠さない。

blind reviewは `cognitive-dogfood-blind-review-protocol.md` に従い、BR1 → BR2 → verdict freeze → unblindの順で行う。

## 7. Contamination stop

次が起きたら、そのrunを無理に有効化しない。

- fresh contextがoperator manifest、Case 0、PR #2805の評価議論、Round 2資料を読んだ。
- fresh contextがbundle外のKJ Atlas repoを探索した。
- B/Dがskill bundle外のskill repo資料を探索した。
- A/Cへskill bundleまたはskill評価情報が渡った。
- 一部armだけ外部Web検索や追加sourceを行った。
- current comparison-design conversationをそのままarm実行へ再利用した。

## 8. Current next action

最初の有効runは **C**。

operatorは現在の比較設計contextとは別のfresh contextを作り、そこへ`cognitive-dogfood-case-001-arm-c` artifactの内容だけを渡し、KJ Atlas UIを人間operatorとして使用する。

この起動時点では、Case 0 outcome、T1〜T3の評価意図、M1〜M9、他arm、cultural-substrate-weaving、Round 2外部比較をfresh analysis contextへ教えない。
