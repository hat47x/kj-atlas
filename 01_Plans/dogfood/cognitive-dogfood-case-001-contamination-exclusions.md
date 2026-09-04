# 認知dogfood Case 001 — 入力汚染の除外条件

- 状態: 最初のprospective raw Arm実行前に凍結済み
- 日付: 2026-08-30
- 対象: Case 001 Round 1 A/B/C/D
- 関連: `cognitive-dogfood-case-001-operator-pack.md`, `cognitive-dogfood-case-001-preflight.md`

## 1. 目的

Case 001は、同じ問いと同じproduct source snapshotを複数Armへ与え、方法の違いによって生じる増分を比較するprospective experimentである。

そのため、実験設計後に作成された「問いへの答えに近い監査・仮説・評価」をArmのコンテキストへ混ぜない。本書は操作者・評価者だけが使用する除外一覧であり、分析を行うArmへ本文を渡さない。

## 2. Round 1のArmへ渡さないKJ Atlas側資料

少なくとも次を、A/B/C/Dの分析コンテキストへ入れない。

```text
01_Plans/dogfood/cognitive-dogfood-case-000-r1-r5-audit.md
01_Plans/dogfood/cognitive-dogfood-case-000-outcome-trace.md
01_Plans/issues/issue-PRODUCT-POSITION-01-primary-job-and-switch-reason.md
01_Plans/issues/issue-VALUE-REALNESS-01-third-party-beachhead-validation.md
01_Plans/issues/issue-PRACTICE-CULTURE-01-cultural-fit-and-product-invariants.md
01_Plans/issues/issue-COGNITIVE-DOGFOOD-01-product-development-cognitive-workbench.md
01_Plans/issues/issue-COGNITIVE-EVAL-01-factorial-human-ai-cognitive-control-evaluation.md
```

これらは操作者・評価者が実験を運用するために参照してよいが、Armが製品を分析するための資料ではない。

PR #2805のconversation comment、現在の設計者チャットで作られた価値仮説、Case 0の下流判定、M1〜M9の評価結果、F0〜F3の判定も同様にArmへ渡さない。

## 3. cultural-substrate-weaving側の除外条件

B/Dには、指定commitのcanonical skillをmethod treatmentとして与えてよい。

一方、次は実験運用や評価設計を含むため、B/Dの分析method inputへ混ぜない。

```text
cultural-substrate-weaving PR #5 のdiscussion/comment
KJ Atlas Case 0 attribution checkpoint
Case 001の4Arm比較結果（発生後）
blind review結果（発生後）
```

PR #5のmaintainer protocol全体を分析agentへ渡す必要はない。B/Dへ与えるのは、事前登録済みのskill snapshotと、operator packで定めたArm固有の実行指示だけとする。

## 4. Armへ渡してよいもの

Round 1で全Armへ渡すproduct evidenceは、`cognitive-dogfood-case-001-operator-pack.md`のCommon product source listを正本とする。

B/Dだけに加えるmethod treatmentは、同operator packで固定した`cultural-substrate-weaving` snapshotとArm固有の指示に限る。

C/DのKJ Atlas UI runbookは、操作者が操作入口を確認するために使用してよい。ただし、そこへ分析上の結論や価値仮説を追加しない。

## 5. 実行中に新しい資料が必要になった場合

Armの実行中に不足資料が見つかっても、そのArmだけへ追加しない。

1. `Candidate source request`としてrun recordへ残す。
2. Round 1は固定済みの資料だけで完了する。
3. 評価者が、全Arm共通で追加すべき資料かを判断する。
4. 採用する場合は、次のcommon roundで全Armへ同じsnapshotを追加する。

これにより、特定の方法だけが追加検索によって有利になることを避ける。

## 6. 入力汚染が起きた場合

誤って除外資料をArmへ見せた場合は、「忘れたこと」にしてそのまま継続しない。

- run recordの`Known contamination`へ、資料名と投入時点を記録する。
- そのrunをprimary comparisonから外す。
- 必要であれば、別のfresh contextで同じ条件のrunをやり直す。
- 汚染されたrun自体も削除せず、negative / operational evidenceとして残す。

## 7. 凍結後の変更規則

最初のprospective raw Armを保存した後は、結果を見て除外一覧を都合よく変更しない。

その後に作られた評価・比較・結論artifactは、原則として「後から生じた評価資料」とみなし、同じRoundの残りのArmへ追加しない。次のRoundのcommon sourceへ昇格させる場合だけ、全Arm共通・事前固定の条件で追加する。