# Cognitive Dogfood Case Portfolio — Execution Freeze Register

- Status: Frozen before first valid Case 001 arm run
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

## Change boundary after first valid raw run

最初の有効なCase 001 raw result保存後は、Cases 001–003のfixed question、Round 1 source manifest、product/skill snapshot、arm treatment、required outputを結果に合わせて変更しない。

実行不能になる実装変更、資料破損、重大な安全/権限上の理由がある場合は、既存入力を上書きせずdeviation/revisionとして別記録し、旧条件と理由を残す。