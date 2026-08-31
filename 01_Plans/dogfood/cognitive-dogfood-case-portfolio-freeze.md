# Cognitive Dogfood Case Portfolio — Execution Freeze Register

- Status: P0 frozen and CI-verified / Cases 001–003 arm packages ready
- Date: 2026-08-30
- Pre-registration: `cognitive-dogfood-case-portfolio-preregistration.md`
- Product snapshot for Cases 001–003: `hat47x/kj-atlas@2232b3bb26647e5c4a083f55bdbf83c161698649`
- Skill snapshot for B/D in Cases 001–003: `hat47x/cultural-substrate-weaving@3988e12e5f7f316f377d3391e9486c8467a111d5`

## Purpose

Case 001の結果を見てからCase 002/003の問い、資料、方法条件を有利な方向へ調整しないため、実行入力の固定状態だけを記録する。

このregisterは事前登録の問いを変更しない。各ケースの答え、評価、experimenter-only conflict/correction test、Arm間比較結果は含めない。

## Shared invariants

- Cases 001–003は同じKJ Atlas product commitを使う。
- B/Dは3ケースとも同じcultural-substrate-weaving commitとcanonical `src/ja-JP` sourceを使う。
- A/Cへskill sourceを渡さない。
- Round 1でarm固有の外部Web検索を行わない。
- source requestはそのarmへ即時追加せず、後のcommon round候補にする。
- C/Dは空starterから開始し、結論・カード・束・表札を事前投入しない。
- raw resultを評価前に固定する。
- blind reviewをunblindより前に完了する。
- invalid / negative / no-increment resultを削除しない。
- arm execution orderはC → D → B → Aを維持する。

## Shared execution / review infrastructure

- Common run record: `cognitive-dogfood-run-record-template.md`
  - case固有required outputとconflict/correction IDだけをlaunch/contractから差し込む。
  - M1〜M9、proposal ledger、retention、T9、skill execution recordは3ケース共通。
- Run validator: `validate_cognitive_run_records.py`
  - Case 001〜003のfixed question / source manifest ID / conflict-check IDを選び分ける。
  - Required outputの全項目、各項目の実質記録、conflict/correctionの時点・契約解釈、M1〜M9の実質記録をP2前にfail-closedで確認する。
  - 方法の優劣は採点しない。
- Shared C/D UI runbook: `cognitive-dogfood-cd-ui-runbook.md`
  - InquiryJourney / snapshot / handoff / resume / lineage / compareのoperator手順を共通化する。
- Blind package builder: `build_cognitive_blind_package.py`
  - arm/method metadataとexperimenter test IDを除き、test IDは`source-check-N`へ中立化する。
  - builder自身がrun validatorを通し、static intake不合格recordからP2 packageを生成しない。
- Blind review protocol/template:
  - `cognitive-dogfood-blind-review-protocol.md`
  - `cognitive-dogfood-blind-review-template.md`
  - fixed questionに応じたcase境界を評価し、Case 001のprimary-job問題へCase 002/003を引き戻さない。
- Launch treatment validator: `validate_cognitive_launch_packets.py`
  - Cases 001〜003の4armでfixed question / required output / product snapshot / evidence bundleを一致させる。
  - cultural-substrate-weaving treatmentはB/Dだけ、KJ Atlas starterはC/Dだけに存在することを検査する。
- Dedicated workflow: `.github/workflows/cognitive-dogfood-freeze.yml`
  - launch packet / product source manifest / skill manifest / starter / bundle builder / freeze validator変更時にfail-closedでpreflightする。
  - run intake / blind-package contract testsも実行し、記録契約の緩みを検出する。
  - treatment equivalenceだけでなく、Cases 001〜003のfrozen product evidence bundleと共通frozen skill bundleを固定commitから実際に再生成する。
  - Cases 001〜003のA〜Dを個別artifactへ組み立て、fresh sessionへ他arm/他treatmentを混入させずに渡せるようにする。

## Shared package boundary

3ケース共通で次を守る。

- 全armに、そのcaseの同一sanitized product evidenceを含める。
- B/Dだけにfrozen canonical skill bundleを含める。
- C/Dだけにempty starter documentを含める。
- 各artifactにはそのarm専用の`launch.md`だけを含め、他armのlaunch packetを含めない。
- B/Dのarm-visible skill metadataはcase非依存の `cognitive-dogfood-skill-ja@<skill SHA>` とし、operator-only manifestのCase 001由来情報をコピーしない。
- package生成済みであることは実行順の前倒しを意味しない。実行はCase 001→002→003を維持する。

## Case 001

- Question/evidence contract: `cognitive-dogfood-case-001-product-purpose.md`
- Product source manifest: `cognitive-dogfood-case-001-round1-source-manifest.json` — 20 sources
- Shared operator-only skill manifest: `cognitive-dogfood-case-001-skill-manifest.json` — 12 canonical ja-JP sources
  - Case 001に由来する事前登録履歴として保持するが、arm-visible metadataへcase identityをコピーしない。
- Starter: `doc_cognitive_case_001_starter.json`
- Launch packets:
  - `cognitive-dogfood-case-001-launch-ordinary.md`
  - `cognitive-dogfood-case-001-launch-skill.md`
  - `cognitive-dogfood-case-001-launch-atlas.md`
  - `cognitive-dogfood-case-001-launch-atlas-skill.md`
- Operator pack: `cognitive-dogfood-case-001-operator-pack.md`
- Original Case 001 C/D preflight runbook: `cognitive-dogfood-case-001-cd-ui-runbook.md`
  - 以後の共通操作正本は`cognitive-dogfood-cd-ui-runbook.md`とし、この文書はCase 001準備時の実装照合記録として保持する。
- CI artifact names:
  - `cognitive-dogfood-case-001-arm-a`
  - `cognitive-dogfood-case-001-arm-b`
  - `cognitive-dogfood-case-001-arm-c`
  - `cognitive-dogfood-case-001-arm-d`

## Case 002

- Fixed question: AI提案と人間判断の境界
- Question/evidence contract: `cognitive-dogfood-case-002-ai-human-boundary.md`
- Product source manifest: `cognitive-dogfood-case-002-round1-source-manifest.json` — 18 sources
- Starter: `doc_cognitive_case_002_starter.json`
- Launch packets:
  - `cognitive-dogfood-case-002-launch-ordinary.md`
  - `cognitive-dogfood-case-002-launch-skill.md`
  - `cognitive-dogfood-case-002-launch-atlas.md`
  - `cognitive-dogfood-case-002-launch-atlas-skill.md`
- CI artifact names:
  - `cognitive-dogfood-case-002-arm-a`
  - `cognitive-dogfood-case-002-arm-b`
  - `cognitive-dogfood-case-002-arm-c`
  - `cognitive-dogfood-case-002-arm-d`

## Case 003

- Fixed question: local/offline/self-hostとcollaborationの製品境界
- Question/evidence contract: `cognitive-dogfood-case-003-local-collaboration-boundary.md`
- Product source manifest: `cognitive-dogfood-case-003-round1-source-manifest.json` — 18 sources
- Starter: `doc_cognitive_case_003_starter.json`
- Launch packets:
  - `cognitive-dogfood-case-003-launch-ordinary.md`
  - `cognitive-dogfood-case-003-launch-skill.md`
  - `cognitive-dogfood-case-003-launch-atlas.md`
  - `cognitive-dogfood-case-003-launch-atlas-skill.md`
- CI artifact names:
  - `cognitive-dogfood-case-003-arm-a`
  - `cognitive-dogfood-case-003-arm-b`
  - `cognitive-dogfood-case-003-arm-c`
  - `cognitive-dogfood-case-003-arm-d`

## Bundle preparation

Round 1 product evidenceは、operator manifestをfresh armへ直接渡さず、`prepare_cognitive_frozen_source_bundle.py` でsanitized bundleを作る。

arm-visible bundleへ含めるのは次だけとする。

- `commonSources`の実ファイル。
- case / round / product repository / frozen product commit。
- source path / Git blob SHA / content SHA-256。

次はarm-visible bundleへコピーしない。

- `round1ExcludedInputs`。
- skill treatment metadata。
- experimenter notes / correction tests / metrics。
- 他arm・他caseの存在を説明する情報。
- PR discussion。

B/Dへ渡すskill sourceもrepository全体ではなく、shared operator-only skill manifestで固定したcanonical `src/ja-JP`だけとする。生成後のarm-visible `_experiment/skill-bundle-manifest.json` はcase非依存とし、operator manifest ID / caseId / excluded-input説明をコピーしない。

## CI freeze guard

`validate_dogfood_docs.py` は少なくとも次をfail-closedで検査する。

- Cases 001–003 product manifestsのschema / case / round / commit / source count。
- manifest pathの安全性と重複。
- manifestに固定した各source blob SHAが、frozen product commit上の実blobと一致すること。
- shared operator-only skill manifestが12 canonical ja-JP sourceに固定されていること。
- Cases 001–003 starterのcards / islands / evidenceLinks / readingOrder / narrativesが空であること。
- cognitive experiment helperのPython構文。

`validate_cognitive_launch_packets.py` / `Cognitive dogfood freeze` workflowは、12個のlaunch packetと12個のarm packageについて次をfail-closedで検査する。

- 同一caseの4armでfixed questionが完全一致すること。
- 同一caseの4armでrequired outputが完全一致すること。
- product snapshot / evidence bundleが4armで一致すること。
- skill treatmentがB/Dだけに入り、A/Cへ混入しないこと。
- KJ Atlas starterがC/Dだけに入り、A/Bへ混入しないこと。
- 全armが追加資料を一方的に取り込まずCandidate source requestへ送る経路を持つこと。
- Cases 001〜003のproduct bundleがfrozen commitから再生成可能であること。
- shared skill bundleがfrozen cultural-substrate-weaving commitから再生成可能であること。
- arm-visible skill metadataへCase 001 identityをコピーしないこと。
- Cases 001〜003のA〜D package uploadが全件成功すること。
- run intake contract testでRequired output / conflict interpretation / M1〜M9の空記録がrejectされること。
- blind-package contract testでstatic intake不合格recordがP2 package化されないこと。

## P0 verification evidence

P0終了前後の実行可能性確認として次を確認した。

1. Cases 001〜003のproduct manifestは、通常CIでfrozen product commit上のpath / Git blob SHAまで実照合済み。
2. `Cognitive dogfood freeze` workflowの`Frozen input preflight`で、12 launch packetのtreatment equivalenceが成功した。
3. 同preflightで、Cases 001〜003のfrozen product evidence bundleを20 / 18 / 18 sourceから実際に再生成できた。
4. B/D用skill manifestの12 sourceは、`cultural-substrate-weaving@3988e12e5f7f316f377d3391e9486c8467a111d5` のcanonical `src/ja-JP`現物とpath / Git blob SHAを照合し、全件一致した。
5. Cases 001〜003のA〜D packageをActions artifactとして実際に生成・uploadし、12件すべて成功した。初回portfolio artifact化はworkflow run #23 / head `7737f2e488c43a1fb70a2e9e65358b3dbcfe39d5`。
6. package境界の代表実検査として、Case 002 Arm Aはskill/starterなし、Case 003 Arm Cはstarterありskillなし、Case 002 Arm Dはstarterとcanonical skill 12件ありであることをZIP展開で確認した。
7. case-neutral skill metadata補正後のworkflow run #29 / head `2548b7ba09568c8a4f39a55ff6b96b13cbaeeec9` で12 packageを再生成し全件成功した。Case 002 Arm Bの実ZIPを展開し、skill subtreeに `case-001` / `Case 001` がなく、arm-visible `manifestId` が `cognitive-dogfood-skill-ja@3988e12e5f7f316f377d3391e9486c8467a111d5` であることを確認した。
8. first raw run前にrun-intake / blind-package contract testsを追加し、Required outputの連続全項目・実質記録、各conflict/correction testの時点/契約解釈、M1〜M9の実質記録、artifact identity / contamination、およびP2 builderのstatic-intake強制をsynthetic fixtureで検証した。workflow run #47 / head `fdf1bb68af1bbccdd4a97197aa557a1dcc2a02d8` でcontract testと12 package再生成が全件成功した。

ここまででP0を閉じたまま維持する。以後、最初のvalid raw runに必要な欠陥が見つからない限り、preflight機能を追加し続けない。次の正規工程はP1 Case 001 Arm Cである。

## Pre-run correction log

最初のvalid raw runより前のfreeze検証で、次の入力不一致・比較完全性上の欠陥を検出・補正した。これは実験結果を見てからの変更ではない。

1. Case 003 source manifestのADR 7件で、意味上の資料選択は正しかったがファイル名転記が実blobと一致していなかった。`validate_dogfood_docs.py` の実commit照合で検出し、同じADR番号の固定commit上の正しいpathへ補正した。source件数・問い・snapshotは変更していない。
2. Case 002のRequired output直後の反証許容文がOrdinaryだけ詳細で、B/C/Dでは短縮されていた。launch treatment validatorで検出し、4armすべて「現状維持・特定操作だけ自律化・AI支援削減のいずれも許容」に統一した。fixed question、10項目のrequired output、product/skill snapshot、treatmentは変更していない。
3. 3ケース共通B/D skill bundleのoperator-only manifestがCase 001由来であるため、builderがその `manifestId=case-001-skill-ja@...` をarm-visible metadataへコピーするとCase 002/003へ別Caseの存在が漏れることを、12 artifact化後のpackage監査で発見した。canonical skill 12件、skill commit、B/D treatmentは変更せず、arm-visible metadataだけを `cognitive-dogfood-skill-ja@<skill SHA>` へcase-neutral化し、`caseScopedMetadataIncluded=false` とした。Case 002 Arm Bの実ZIPでcase identity非混入を確認した。
4. run intakeは当初、Required outputの見出しが一部だけでも通る、見出しだけ/空template値でも通る、conflict testの`detected`フラグだけで解釈がなくても通る、M1〜M9が空でも通る余地があった。またblind package builderは手順上static intake必須でもコード上は直接呼べた。first raw run前に、Case 001=9項目・Case 002/003=10項目の連続全項目、各項目の実質記録、各test IDの`temporal/contract interpretation`、M1〜M9の実質記録、artifact identity / contaminationをfail-closed化し、builder自身にもstatic intakeを強制した。評価内容の良否やarm treatmentは変更していない。

補正後もfixed question、Round 1 evidence、product/skill snapshot、4arm treatment、required outputは変更していない。

## Change boundary after first valid raw run

最初の有効なCase 001 raw result保存後は、Cases 001〜003のfixed question、Round 1 source manifest、product/skill snapshot、arm treatment、required outputを結果に合わせて変更しない。

実行不能になる実装変更、資料破損、重大な安全/権限上の理由がある場合は、既存入力を上書きせずdeviation/revisionとして別記録し、旧条件と理由を残す。