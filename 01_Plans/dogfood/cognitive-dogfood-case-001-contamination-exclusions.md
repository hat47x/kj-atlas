# Cognitive Dogfood Case 001 — Contamination Exclusions

- Status: Locked before first prospective raw arm
- Date: 2026-08-30
- Scope: Case 001 Round 1 A/B/C/D
- Related: `cognitive-dogfood-case-001-operator-pack.md`, `cognitive-dogfood-case-001-preflight.md`

## 1. 目的

Case 001は、同じ問い・同じproduct source snapshotを複数armへ与えて、方法差による増分を比較するprospective experimentである。

そのため、実験設計後に作られた「問いへの答えに近い監査・仮説・評価」をarm contextへ混ぜない。本書はoperator-onlyのexclusion listであり、分析armへ本文を渡さない。

## 2. Round 1 armへ渡してはいけないKJ Atlas側資料

少なくとも次をA/B/C/Dの分析contextへ入れない。

```text
01_Plans/dogfood/cognitive-dogfood-case-000-r1-r5-audit.md
01_Plans/dogfood/cognitive-dogfood-case-000-outcome-trace.md
01_Plans/issues/issue-PRODUCT-POSITION-01-primary-job-and-switch-reason.md
01_Plans/issues/issue-VALUE-REALNESS-01-third-party-beachhead-validation.md
01_Plans/issues/issue-PRACTICE-CULTURE-01-cultural-fit-and-product-invariants.md
01_Plans/issues/issue-COGNITIVE-DOGFOOD-01-product-development-cognitive-workbench.md
01_Plans/issues/issue-COGNITIVE-EVAL-01-factorial-human-ai-cognitive-control-evaluation.md
```

これらはoperator / evaluatorが実験を運用するためには参照してよいが、armの製品分析材料ではない。

PR #2805のconversation comment、現在のチャットで作られた価値仮説、Case 0の下流判定、M1–M9評価結果、F0–F3判定も同様にarmへ渡さない。

## 3. cultural-substrate-weaving側の除外

B/Dでは指定commitのcanonical skillをmethod treatmentとして与えてよい。

一方、次は実験運用・評価を知っているため、B/Dの分析method inputへ混ぜない。

```text
cultural-substrate-weaving PR #5 のdiscussion/comment
KJ Atlas Case 0 attribution checkpoint
Case 001の4-arm比較結果（発生後）
blind review結果（発生後）
```

PR #5のmaintainer protocol自体を分析agentへ丸ごと与える必要はない。B/Dには事前登録された指定skill snapshotと、operator packに定めたarm-specific instructionだけを与える。

## 4. 渡してよいもの

Round 1で全armへ渡すproduct evidenceは `cognitive-dogfood-case-001-operator-pack.md` の Common product source list を正本とする。

B/Dだけに追加するmethod treatmentは、同operator packで固定した `cultural-substrate-weaving` snapshotとarm instructionに限る。

C/DのKJ Atlas UI runbookはoperatorが操作入口を確認するために使用できるが、そこに分析結論・価値仮説を追加してはならない。

## 5. 新しい資料が見つかった場合

arm実行中に不足資料を発見しても、そのarmだけへ追加しない。

1. `Candidate source request` としてrun recordへ残す。
2. Round 1をそのまま完了する。
3. evaluatorが全arm共通で追加すべきか判断する。
4. 採用する場合は次のcommon roundで全armへ同一snapshotを追加する。

これにより、ある方法だけが追加検索によって有利になることを避ける。

## 6. Contamination incident

誤って除外資料をarmへ見せた場合は、内容を忘れたことにして継続しない。

- run recordの `Known contamination` に資料名と投入時点を記録する。
- 当該runをprimary comparisonから外す。
- 必要ならfresh contextでrunをやり直す。
- contaminated run自体は削除せず、negative/operational evidenceとして残す。

## 7. Lock rule

最初のprospective raw arm保存後は、結果を見てexclusion listを都合よく変更しない。

新たに作られた評価・比較・結論artifactは原則として自動的に「後発評価資料」とみなし、そのroundの他armへ追加しない。次roundのcommon sourceへ昇格させる場合だけ、全arm共通・事前固定で行う。
