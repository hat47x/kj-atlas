# Cognitive Dogfood Case 001 — Isolated-arm launch procedure

- Status: Prepared before first raw run
- Scope: Case 001 Round 1 P1 execution
- Preregistered order: **C → D → B → A**
- Product bundle ID: `case-001-r1-product@2232b3bb26647e5c4a083f55bdbf83c161698649`
- Skill bundle ID for B/D: `case-001-skill-ja@3988e12e5f7f316f377d3391e9486c8467a111d5`

## 1. Operator-only preparation

この手順とoperator manifest類はfresh arm contextへ渡さない。

### 1.1 Product evidence bundle

完全な `kj-atlas` git checkout/worktreeから、全arm共通bundleを一度生成する。

```bash
python 01_Plans/dogfood/prepare_cognitive_case001_source_bundle.py \
  --repo-root /path/to/kj-atlas \
  --output /path/to/operator-workspace/case001-product
```

成功条件:

- 20件すべてが固定commitから抽出される。
- 各Git blob SHAがoperator manifestと一致する。
- bundleの `_experiment/bundle-manifest.json` に `sourceCount: 20` がある。
- `operatorManifestCopied=false`、`excludedInputsCopied=false`、`treatmentMetadataIncluded=false` である。
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
- docs/evals/plugins/adapters/AGENTS/README/PR discussionは入っていない。

A/Cへskill bundleまたはskill manifestを渡さない。

## 2. Arm launch matrix

| Execution | Arm | Fresh context receives | KJ Atlas UI | Skill bundle |
|---:|---|---|---|---|
| 1 | C | product bundle + `cognitive-dogfood-case-001-launch-atlas.md` | yes | no |
| 2 | D | product bundle + skill bundle + `cognitive-dogfood-case-001-launch-atlas-skill.md` | yes | yes |
| 3 | B | product bundle + skill bundle + `cognitive-dogfood-case-001-launch-skill.md` | no | yes |
| 4 | A | product bundle + `cognitive-dogfood-case-001-launch-ordinary.md` | no | no |

fresh contextにはこのmatrixやarm名をわざわざ教えず、該当するlaunch packetだけをtask instructionとして渡す。run record作成時にoperatorがarm metadataを補う。

## 3. C/D product execution

C/Dでは別途operator-onlyの `cognitive-dogfood-case-001-cd-ui-runbook.md` を人間operatorが参照する。分析AIへrunbook全体を見せる必要はない。

最低限:

1. 空の `doc_cognitive_case_001_starter.json` を起点にする。
2. launch packetに従ってAIが生カード候補を作る。
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

## 5. Static intake

run recordを完成させ、中立blind aliasを割り当ててから実行する。

```bash
python 01_Plans/dogfood/validate_cognitive_run_records.py \
  /path/to/operator-workspace/<alias>-record.md
```

`PASS`しないrunをBR1へ送らない。failの原因がexperiment record deficiencyか、実際のproduct/manual-core defectかを分ける。

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

operatorは現在の比較設計contextとは別のfresh contextを作り、そこへ次だけを渡す。

- sanitized product evidence bundle
- `cognitive-dogfood-case-001-launch-atlas.md`
- KJ Atlas UIへの人間operatorアクセス

この起動時点では、Case 0 outcome、T1〜T3の評価意図、M1〜M9、他arm、cultural-substrate-weaving、Round 2外部比較をfresh analysis contextへ教えない。
