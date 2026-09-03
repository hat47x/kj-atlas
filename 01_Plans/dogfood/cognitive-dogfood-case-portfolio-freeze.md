# 認知dogfood Case Portfolio — 実行条件凍結記録

- 状態: P0凍結・CI検証済み / Case 001〜003のArmパッケージ生成可能
- 日付: 2026-08-30
- 事前登録: `cognitive-dogfood-case-portfolio-preregistration.md`
- Case 001〜003共通の製品snapshot: `hat47x/kj-atlas@2232b3bb26647e5c4a083f55bdbf83c161698649`
- Case 001〜003のB/Dで使用するskill snapshot: `hat47x/cultural-substrate-weaving@3988e12e5f7f316f377d3391e9486c8467a111d5`

## 1. この記録の役割

Case 001の結果を見た後で、Case 002/003の問い、資料、方法条件を有利な方向へ調整しないよう、実行入力をどの状態で固定したかを記録する。

この記録自体は、事前登録した問いを変更しない。また、各Caseの答え、評価結果、実験者だけが知る訂正・時点差チェックの意図、Arm間の比較結果は含めない。

## 2. 3Case共通の不変条件

- Case 001〜003は、同じKJ Atlas product commitを使用する。
- B/Dは3Caseとも、同じcultural-substrate-weaving commitとcanonical `src/ja-JP` sourceを使用する。
- A/Cにはskill sourceを渡さない。
- Round 1では、特定のArmだけが外部Web検索を行わない。
- 追加資料が必要になっても、そのArmへ即時追加しない。後のcommon roundへ追加する候補として記録する。
- C/Dは空のstarterから開始し、結論、カード、束、表札を事前に入れない。
- raw resultは評価前に固定する。
- blind reviewをunblindより先に完了する。
- invalid / negative / no-incrementな結果も削除しない。
- Armの実行順は **C → D → B → A** を維持する。

## 3. 共通の実行・レビュー基盤

### Run record

`cognitive-dogfood-run-record-template.md`を3Case共通で使用する。

- Case固有のrequired outputと訂正・時点差チェックIDだけをlaunch / contractから差し込む。
- M1〜M9、proposal ledger、retention audit、T9、skill execution recordは3Case共通とする。

### Run validator

`validate_cognitive_run_records.py`を使用する。

- Case 001〜003ごとにfixed question / source manifest ID / conflict-check IDを選び分ける。
- Required outputの全項目と実質的な本文、各訂正・時点差チェックの解釈、M1〜M9の実質的な記録を、P2へ進む前にfail-closedで確認する。
- 方法の優劣そのものは採点しない。

### C/D共通UI手順

`cognitive-dogfood-cd-ui-runbook.md`を共通の正本とする。

InquiryJourney / snapshot / handoff / resume / lineage / compareを、操作者が実際に使うための手順をまとめる。

### Blind package builder

`build_cognitive_blind_package.py`を使用する。

- Arm / method metadataと実験者用test IDを除く。
- test IDは`source-check-N`へ中立化する。
- builder自身がrun validatorを通し、static intakeに合格しないrecordからP2用packageを生成しない。

### Blind review

- `cognitive-dogfood-blind-review-protocol.md`
- `cognitive-dogfood-blind-review-template.md`

fixed questionに応じてCaseごとの境界を評価する。Case 001のprimary-job問題へCase 002/003を引き戻さない。

### Launch treatment validator

`validate_cognitive_launch_packets.py`を使用する。

- 同一Caseの4Armでfixed question / required output / product snapshot / evidence bundleが一致することを確認する。
- cultural-substrate-weavingはB/Dだけ、KJ Atlas starterはC/Dだけに含まれることを検査する。

### 専用workflow

`.github/workflows/cognitive-dogfood-freeze.yml`を使用する。

- launch packet、product source manifest、skill manifest、starter、bundle builder、freeze validatorを変更したときにfail-closedでpreflightする。
- run intake / blind-packageのcontract testも実行し、記録契約が緩んでいないかを確認する。
- treatmentの同値性だけでなく、Case 001〜003のfrozen product evidence bundleと共通frozen skill bundleを、固定commitから実際に再生成する。
- Case 001〜003のA〜Dを個別artifactへ組み立て、新規コンテキストへ他Arm・他treatmentを混ぜずに渡せるようにする。

## 4. 実行パッケージの境界

3Case共通で次を守る。

- 全Armに、そのCaseの同一sanitized product evidenceを含める。
- B/Dだけにfrozen canonical skill bundleを含める。
- C/Dだけに空のstarter documentを含める。
- 各artifactには、そのArm専用の`launch.md`だけを含める。他Armのlaunch packetは入れない。
- B/Dから見えるskill metadataはCase非依存の`cognitive-dogfood-skill-ja@<skill SHA>`とし、操作者専用manifestがCase 001に由来する情報をコピーしない。
- packageを先に生成できることは、Caseの実行順を前倒ししてよいことを意味しない。実行順はCase 001 → 002 → 003を維持する。

## 5. Case 001

- 問い・evidence contract: `cognitive-dogfood-case-001-product-purpose.md`
- Product source manifest: `cognitive-dogfood-case-001-round1-source-manifest.json` — 20 sources
- 3Case共通の操作者専用skill manifest: `cognitive-dogfood-case-001-skill-manifest.json` — canonical ja-JP 12 sources
  - Case 001に由来する事前登録履歴として保持するが、Arm側metadataへCase identityをコピーしない。
- Starter: `doc_cognitive_case_001_starter.json`
- Launch packets:
  - `cognitive-dogfood-case-001-launch-ordinary.md`
  - `cognitive-dogfood-case-001-launch-skill.md`
  - `cognitive-dogfood-case-001-launch-atlas.md`
  - `cognitive-dogfood-case-001-launch-atlas-skill.md`
- Operator pack: `cognitive-dogfood-case-001-operator-pack.md`
- Case 001準備時のC/D preflight runbook: `cognitive-dogfood-case-001-cd-ui-runbook.md`
  - 現在の共通操作の正本は`cognitive-dogfood-cd-ui-runbook.md`とする。旧文書はCase 001準備時の実装照合記録として保持する。
- Actions artifact名:
  - `cognitive-dogfood-case-001-arm-a`
  - `cognitive-dogfood-case-001-arm-b`
  - `cognitive-dogfood-case-001-arm-c`
  - `cognitive-dogfood-case-001-arm-d`

## 6. Case 002

- 固定問い: AI提案と人間判断の境界
- 問い・evidence contract: `cognitive-dogfood-case-002-ai-human-boundary.md`
- Product source manifest: `cognitive-dogfood-case-002-round1-source-manifest.json` — 18 sources
- Starter: `doc_cognitive_case_002_starter.json`
- Launch packets:
  - `cognitive-dogfood-case-002-launch-ordinary.md`
  - `cognitive-dogfood-case-002-launch-skill.md`
  - `cognitive-dogfood-case-002-launch-atlas.md`
  - `cognitive-dogfood-case-002-launch-atlas-skill.md`
- Actions artifact名:
  - `cognitive-dogfood-case-002-arm-a`
  - `cognitive-dogfood-case-002-arm-b`
  - `cognitive-dogfood-case-002-arm-c`
  - `cognitive-dogfood-case-002-arm-d`

## 7. Case 003

- 固定問い: local / offline / self-host と collaboration の製品境界
- 問い・evidence contract: `cognitive-dogfood-case-003-local-collaboration-boundary.md`
- Product source manifest: `cognitive-dogfood-case-003-round1-source-manifest.json` — 18 sources
- Starter: `doc_cognitive_case_003_starter.json`
- Launch packets:
  - `cognitive-dogfood-case-003-launch-ordinary.md`
  - `cognitive-dogfood-case-003-launch-skill.md`
  - `cognitive-dogfood-case-003-launch-atlas.md`
  - `cognitive-dogfood-case-003-launch-atlas-skill.md`
- Actions artifact名:
  - `cognitive-dogfood-case-003-arm-a`
  - `cognitive-dogfood-case-003-arm-b`
  - `cognitive-dogfood-case-003-arm-c`
  - `cognitive-dogfood-case-003-arm-d`

## 8. Bundle生成時の境界

Round 1のproduct evidenceは、操作者用manifestを新規Armへ直接渡さない。`prepare_cognitive_frozen_source_bundle.py`でsanitized bundleを作る。

Arm側bundleへ含める情報:

- `commonSources`の実ファイル。
- Case / Round / product repository / frozen product commit。
- source path / Git blob SHA / content SHA-256。

Arm側bundleへ含めない情報:

- `round1ExcludedInputs`。
- skill treatment metadata。
- experimenter notes / correction tests / metrics。
- 他Arm・他Caseの存在を説明する情報。
- PR discussion。

B/Dへ渡すskill sourceもrepository全体ではなく、共通の操作者専用skill manifestで固定したcanonical `src/ja-JP`だけを使用する。生成後のArm側`_experiment/skill-bundle-manifest.json`はCase非依存とし、operator manifest ID / caseId / excluded-inputの説明をコピーしない。

## 9. CIによる凍結条件の検査

`validate_dogfood_docs.py`では、少なくとも次をfail-closedで検査する。

- Case 001〜003 product manifestのschema / Case / Round / commit / source count。
- manifest pathの安全性と重複。
- manifestへ固定した各source blob SHAが、frozen product commit上の実blobと一致すること。
- 共通の操作者専用skill manifestが、canonical ja-JP 12 sourceに固定されていること。
- Case 001〜003 starterのcards / islands / evidenceLinks / readingOrder / narrativesが空であること。
- cognitive experiment helperのPython構文。

`validate_cognitive_launch_packets.py`と`Cognitive dogfood freeze` workflowでは、12個のlaunch packetと12個のArm packageについて次をfail-closedで検査する。

- 同一Caseの4Armでfixed questionが完全一致する。
- 同一Caseの4Armでrequired outputが完全一致する。
- product snapshot / evidence bundleが4Armで一致する。
- skill treatmentはB/Dだけに入り、A/Cへ混入しない。
- KJ Atlas starterはC/Dだけに入り、A/Bへ混入しない。
- 全Armが追加資料を一方的に取り込まず、Candidate source requestへ送る経路を持つ。
- Case 001〜003のproduct bundleをfrozen commitから再生成できる。
- 共通skill bundleをfrozen cultural-substrate-weaving commitから再生成できる。
- Arm側skill metadataへCase 001 identityをコピーしない。
- Case 001〜003のA〜D package uploadがすべて成功する。
- run-intake contract testでRequired output、訂正・時点差チェックの解釈、M1〜M9の空記録がrejectされる。
- blind-package contract testで、static intake不合格recordをP2 packageへ変換できない。

## 10. P0で確認した実行可能性

P0終了前後に、次を実際に確認した。

1. Case 001〜003のproduct manifestについて、通常CIでfrozen product commit上のpath / Git blob SHAまで照合した。
2. `Cognitive dogfood freeze` workflowの`Frozen input preflight`で、12 launch packetのtreatment equivalenceが成功した。
3. 同preflightで、Case 001〜003のfrozen product evidence bundleを20 / 18 / 18 sourceから実際に再生成できた。
4. B/D用skill manifestの12 sourceについて、`cultural-substrate-weaving@3988e12e5f7f316f377d3391e9486c8467a111d5`のcanonical `src/ja-JP`現物とpath / Git blob SHAを照合し、全件一致した。
5. Case 001〜003のA〜D packageをActions artifactとして生成・uploadし、12件すべて成功した。初回のportfolio artifact化はworkflow run #23 / head `7737f2e488c43a1fb70a2e9e65358b3dbcfe39d5`。
6. package境界の代表確認として、Case 002 Arm Aはskill / starterなし、Case 003 Arm Cはstarterあり・skillなし、Case 002 Arm Dはstarterとcanonical skill 12件ありであることを、実ZIP展開で確認した。
7. Case非依存のskill metadataへ補正した後、workflow run #29 / head `2548b7ba09568c8a4f39a55ff6b96b13cbaeeec9`で12 packageを再生成し、全件成功した。Case 002 Arm Bの実ZIPを展開し、skill subtreeに`case-001` / `Case 001`がなく、Arm側`manifestId`が`cognitive-dogfood-skill-ja@3988e12e5f7f316f377d3391e9486c8467a111d5`であることを確認した。
8. 最初のraw run前にrun-intake / blind-package contract testを追加した。Required outputの連続した全項目と実質記録、各訂正・時点差チェックの解釈、M1〜M9の実質記録、artifact identity / contamination、P2 builderによるstatic-intake強制をsynthetic fixtureで検証した。workflow run #47 / head `fdf1bb68af1bbccdd4a97197aa557a1dcc2a02d8`でcontract testと12 package再生成がすべて成功した。

ここまででP0は完了とする。以後、最初の有効なraw runを実行するために必要な欠陥が見つからない限り、preflight機能を増やし続けない。次の正規工程はP1 / Case 001 / Arm Cである。

## 11. Raw run前に行った補正

最初の有効なraw runより前のfreeze検証で、次の入力不一致・比較完全性上の欠陥を検出し、補正した。いずれも実験結果を見てから変更したものではない。

1. **Case 003 source manifestのADRファイル名転記**

   ADR 7件について、意味上の資料選択は正しかったが、ファイル名が固定commit上の実blobと一致していなかった。`validate_dogfood_docs.py`の実commit照合で検出し、同じADR番号の正しいpathへ補正した。source件数、問い、snapshotは変更していない。

2. **Case 002の反証許容文のArm間差**

   Required output直後の反証許容文がOrdinaryだけ詳細で、B/C/Dでは短縮されていた。launch treatment validatorで検出し、4Armすべてを「現状維持・特定操作だけ自律化・AI支援削減のいずれも許容」に統一した。fixed question、10項目のrequired output、product / skill snapshot、treatmentは変更していない。

3. **共通skill bundleから別Caseの存在を推測できるmetadata**

   3Case共通B/D skill bundleの操作者専用manifestがCase 001由来であるため、builderが`manifestId=case-001-skill-ja@...`をArm側metadataへコピーすると、Case 002/003へ別Caseの存在が漏れることを12 artifact化後のpackage監査で発見した。canonical skill 12件、skill commit、B/D treatmentは変更せず、Arm側metadataだけを`cognitive-dogfood-skill-ja@<skill SHA>`へCase非依存化し、`caseScopedMetadataIncluded=false`とした。Case 002 Arm Bの実ZIPでCase identityが入っていないことを確認した。

4. **Run intakeとblind package入口の完全性**

   初期のrun intakeには、Required outputの一部見出しだけでも通る、見出しだけ・空template値でも通る、訂正・時点差チェックの`detected`フラグだけで解釈がなくても通る、M1〜M9が空でも通る余地があった。またblind package builderは、手順上はstatic intake必須でも、コード上は直接呼び出せた。最初のraw run前に、Case 001=9項目、Case 002/003=10項目の連続した全項目、各項目の実質記録、各test IDの`temporal/contract interpretation`、M1〜M9の実質記録、artifact identity / contaminationをfail-closed化し、builder自身にもstatic intakeを強制した。評価内容の良否やArm treatmentは変更していない。

これらの補正後も、fixed question、Round 1 evidence、product / skill snapshot、4Arm treatment、required outputは変更していない。

## 12. 最初の有効なraw run以後の変更境界

最初の有効なCase 001 raw resultを保存した後は、Case 001〜003のfixed question、Round 1 source manifest、product / skill snapshot、Arm treatment、required outputを、結果に合わせて変更しない。

実行不能となる実装変更、資料破損、重大な安全上・権限上の理由が生じた場合も、既存入力を上書きしない。deviation / revisionとして別に記録し、旧条件と変更理由を残す。