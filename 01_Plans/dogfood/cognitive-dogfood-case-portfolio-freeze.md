# Cognitive Dogfood Case Portfolio — Execution Freeze Register

- Status: P0 frozen and CI-verified before first valid Case 001 arm run
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
  - 方法の優劣は採点しない。
- Shared C/D UI runbook: `cognitive-dogfood-cd-ui-runbook.md`
  - InquiryJourney / snapshot / handoff / resume / lineage / compareのoperator手順を共通化する。
- Blind package builder: `build_cognitive_blind_package.py`
  - arm/method metadataとexperimenter test IDを除き、test IDは`source-check-N`へ中立化する。
- Blind review protocol/template:
  - `cognitive-dogfood-blind-review-protocol.md`
  - `cognitive-dogfood-blind-review-template.md`
  - fixed questionに応じたcase境界を評価し、Case 001のprimary-job問題へCase 002/003を引き戻さない。
- Launch treatment validator: `validate_cognitive_launch_packets.py`
  - Cases 001〜003の4armでfixed question / required output / product snapshot / evidence bundleを一致させる。
  - cultural-substrate-weaving treatmentはB/Dだけ、KJ Atlas starterはC/Dだけに存在することを検査する。
- Dedicated workflow: `.github/workflows/cognitive-dogfood-freeze.yml`
  - launch packet / product source manifest / bundle builder / freeze validator変更時にfail-closedでpreflightする。
  - treatment equivalenceだけでなく、Cases 001〜003のfrozen product evidence bundleを固定commitから実際に再生成する。

## Case 001

- Question/evidence contract: `cognitive-dogfood-case-001-product-purpose.md`
- Product source manifest: `cognitive-dogfood-case-001-round1-source-manifest.json` — 20 sources
- Shared skill manifest: `cognitive-dogfood-case-001-skill-manifest.json` — 12 canonical ja-JP sources
- Starter: `doc_cognitive_case_001_starter.json`
- Launch packets:
  - `cognitive-dogfood-case-001-launch-ordinary.md`
  - `cognitive-dogfood-case-001-launch-skill.md`
  - `cognitive-dogfood-case-001-launch-atlas.md`
  - `cognitive-dogfood-case-001-launch-atlas-skill.md`
- Operator pack: `cognitive-dogfood-case-001-operator-pack.md`
- Original Case 001 C/D preflight runbook: `cognitive-dogfood-case-001-cd-ui-runbook.md`
  - 以後の共通操作正本は`cognitive-dogfood-cd-ui-runbook.md`とし、この文書はCase 001準備時の実装照合記録として保持する。

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

B/Dへ渡すskill sourceもrepository全体ではなく、shared skill manifestで固定したcanonical `src/ja-JP`だけとする。

## CI freeze guard

`validate_dogfood_docs.py` は少なくとも次をfail-closedで検査する。

- Cases 001–003 product manifestsのschema / case / round / commit / source count。
- manifest pathの安全性と重複。
- manifestに固定した各source blob SHAが、frozen product commit上の実blobと一致すること。
- shared skill manifestが12 canonical ja-JP sourceに固定されていること。
- Cases 001–003 starterのcards / islands / evidenceLinks / readingOrder / narrativesが空であること。
- cognitive experiment helperのPython構文。

`validate_cognitive_launch_packets.py` / `Cognitive dogfood freeze` workflowは、12個のlaunch packetについて次をfail-closedで検査する。

- 同一caseの4armでfixed questionが完全一致すること。
- 同一caseの4armでrequired outputが完全一致すること。
- product snapshot / evidence bundleが4armで一致すること。
- skill treatmentがB/Dだけに入り、A/Cへ混入しないこと。
- KJ Atlas starterがC/Dだけに入り、A/Bへ混入しないこと。
- 全armが追加資料を一方的に取り込まずCandidate source requestへ送る経路を持つこと。
- Cases 001〜003のproduct bundleがfrozen commitから再生成可能であること。

## P0 verification evidence

P0終了前に次を確認した。

1. Cases 001〜003のproduct manifestは、通常CIでfrozen product commit上のpath / Git blob SHAまで実照合済み。
2. `Cognitive dogfood freeze` workflowの`Frozen input preflight`で、12 launch packetのtreatment equivalenceが成功した。
3. 同preflightで、Cases 001〜003のfrozen product evidence bundleを20 / 18 / 18 sourceから実際に再生成できた。
4. B/D用skill manifestの12 sourceは、`cultural-substrate-weaving@3988e12e5f7f316f377d3391e9486c8467a111d5` のcanonical `src/ja-JP`現物とpath / Git blob SHAを照合し、全件一致した。

ここまででP0を閉じる。以後、最初のvalid raw runに必要な欠陥が見つからない限り、preflight機能を追加し続けない。次の正規工程はP1 Case 001 Arm Cである。

## Pre-run correction log

最初のvalid raw runより前のfreeze検証で、次の入力不一致を検出・補正した。これは実験結果を見てからの変更ではない。

1. Case 003 source manifestのADR 7件で、意味上の資料選択は正しかったがファイル名転記が実blobと一致していなかった。`validate_dogfood_docs.py` の実commit照合で検出し、同じADR番号の固定commit上の正しいpathへ補正した。source件数・問い・snapshotは変更していない。
2. Case 002のRequired output直後の反証許容文がOrdinaryだけ詳細で、B/C/Dでは短縮されていた。launch treatment validatorで検出し、4armすべて「現状維持・特定操作だけ自律化・AI支援削減のいずれも許容」に統一した。fixed question、10項目のrequired output、product/skill snapshot、treatmentは変更していない。

補正後、通常CIのdogfood/docs contractと`Cognitive dogfood freeze`のlaunch treatment equivalenceはともに成功した。

## Change boundary after first valid raw run

最初の有効なCase 001 raw result保存後は、Cases 001〜003のfixed question、Round 1 source manifest、product/skill snapshot、arm treatment、required outputを結果に合わせて変更しない。

実行不能になる実装変更、資料破損、重大な安全/権限上の理由がある場合は、既存入力を上書きせずdeviation/revisionとして別記録し、旧条件と理由を残す。