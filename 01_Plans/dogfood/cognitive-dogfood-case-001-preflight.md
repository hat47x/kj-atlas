# Cognitive Dogfood Case 001 — Preflight Record

- Status: Passed / ready for isolated-arm execution
- Date: 2026-08-30
- Related: `cognitive-dogfood-execution-plan.md`, `cognitive-dogfood-case-001-operator-pack.md`, `cognitive-dogfood-case-001-product-purpose.md`
- Product snapshot: `hat47x/kj-atlas@2232b3bb26647e5c4a083f55bdbf83c161698649`
- Skill snapshot: `hat47x/cultural-substrate-weaving@3988e12e5f7f316f377d3391e9486c8467a111d5`

## 1. 目的

Case 001の最初のraw runを保存する前に、比較条件が実際に再現可能かを確認した記録である。

この文書はCase 001の問いへの回答を含めず、A〜Dの成果比較にも使用しない。preflightで確認するのは、sourceの存在、固定snapshot、実行順、自然発生conflict testの成立、既知contaminationだけである。

## 2. Frozen source manifest verification

operator packで指定したRound 1共通入力20件を、すべてproduct snapshot `2232b3bb26647e5c4a083f55bdbf83c161698649` から取得できることを確認した。

| # | Source | Frozen blob SHA | Result |
|---:|---|---|---|
| 1 | `README.md` | `e9a98fd727d553739dbe404104793ace6e5c9cdf` | present |
| 2 | `ROADMAP.md` | `e93a3dbb24e5058a6e3b07cb63bf85a8d66842fb` | present |
| 3 | `00_Prompt/kj_technique.md` | `1e202ceb833b35a35eca842919d7bbf1404d5d89` | present |
| 4 | `01_Plans/adr/ADR-0032-product-value-realization-model.md` | `98a09a5dcd34d02fcc3d64fdf8cfa423b7f3143f` | present |
| 5 | `01_Plans/adr/ADR-0042-value-realness-validation-and-notice-exit.md` | `e1cd3af831a0f2982c2fa476069d9206fa3aa93a` | present |
| 6 | `01_Plans/adr/ADR-0047-design-decision-adr-saturation-and-execution-first.md` | `6b068e48ba28823a3214ee4ba4c0aac7a05c281b` | present |
| 7 | `01_Plans/adr/ADR-0057-w-type-cumulative-inquiry-model.md` | `2b0055afcfca9e29955c2bc012794da06e40fcb9` | present |
| 8 | `01_Plans/issues/TEMPLATE.md` | `186902acb4ae2bffb61761b5c71474566e1c8ce5` | present |
| 9 | `01_Plans/issues/issue-VALUE-MEASURE-01-measurement-harness-and-evidence-artifacts.md` | `948561157ea716ccbf6f3dba789dbde929d45035` | present |
| 10 | `01_Plans/issues/issue-VR-ROADMAP-01-value-to-social-goal-phase-baseline.md` | `245b62c3479ea5810fb841dca9de499ce6d6b217` | present |
| 11 | `01_Plans/issues/issue-DOMAIN-W-ITERATION-01-w-type-cumulative-inquiry-support.md` | verified at frozen snapshot | present |
| 12 | `01_Plans/dogfood/doc_kj_atlas_dogfood_r1.json` | `c6ae2f6635a30d94a5d7bd671785e6fa5e6f1acc` | present |
| 13 | `01_Plans/dogfood/doc_kj_atlas_dogfood_r2.json` | `27a00fddcf6717a0af1ba2bf67ef8faebc7f6985` | present |
| 14 | `01_Plans/dogfood/doc_kj_atlas_dogfood_r3.json` | `edb83ab819984f20052b644898613e1457a8a1f1` | present |
| 15 | `01_Plans/dogfood/doc_kj_atlas_dogfood_r4.json` | `8241de96cb8c7a6267fbdcba840a23d9be6b0950` | present |
| 16 | `01_Plans/dogfood/doc_kj_atlas_dogfood_r5.json` | `9aa694d334409ce3bf3c29fc8a84f61c9b64cf17` | present |
| 17 | `01_Plans/issues/issue-DOGFOOD-17-opposing-viewpoint-ignores-target-claim.md` | verified at frozen snapshot | present |
| 18 | `01_Plans/issues/issue-DOGFOOD-20-card-groups-not-theme-based.md` | verified at frozen snapshot | present |
| 19 | `01_Plans/issues/issue-DOGFOOD-31-two-hundred-card-scale-exceeds-ai-operation-limits.md` | verified at frozen snapshot | present |
| 20 | `01_Plans/issues/issue-DOGFOOD-32-one-line-heading-hierarchy-missing-for-large-canvases.md` | verified at frozen snapshot | present |

`verified at frozen snapshot` はpreflightで直接同commitを指定して内容取得まで確認したもの。次にsource bundleを機械生成する場合は、その時点でblob SHAもmanifestへ補完できるが、Case 001開始条件としてはcommit SHA + pathで一意に再取得できる。

## 3. Current-state / temporal conflict preflight

### T1 — R3 three-element alignment

古いR3 artifactには「issue templateに三要素整合欄がない」という問題提起がある一方、固定snapshotの現在のissue templateには三要素整合欄が存在することを確認済み。

評価時は古いカードを現在状態として採用しないことを見る。

### T2 — DOGFOOD-32 overclaim correction

DOGFOOD-32の同一issue memo内に、初期の「階層/一行表札が不足」という評価と、後段の「既存の `summaryView` / `hierarchyLevel` / `abstractMapView` 等を見落としており過大申告だった」という訂正が残っていることを確認した。

### T3 — DOGFOOD-31 grounding policy correction

DOGFOOD-31の同一issue memo内に、大規模入力への初期対応案と、後段で `groundingIds` 上限10を品質ガードとして維持する判断が残っていることを確認した。

T1〜T3はいずれも人工的な偽情報を仕込んだテストではなく、実際の開発履歴に自然発生した時間差・自己訂正を利用する。

## 4. InquiryJourney current-state check

固定snapshotの `DOMAIN-W-ITERATION-01` では、AC-1〜AC-13が完了し、Phase 2手動中核の主要機能が実装済みであることを確認した。

T9はPhase 2の**実使用後**に、Phase 3 proposal-only AI支援を別issueへ分けるか判断する項目として未完了。T10は別の外部トリガーを持つメニュー配置事項であり、T9とは分離する。

Case 001〜003のC/Dは、T9の実使用証拠にもなるが、単一runでT9を完了させない。

## 5. Arm order reproducibility

固定文字列:

```text
case-001|2232b3bb26647e5c4a083f55bdbf83c161698649|3988e12e5f7f316f377d3391e9486c8467a111d5
```

SHA-256:

```text
94d35b8cc3dc6af5a7fe83025ec8f0b1cdf3e6afcfc35af2a85386663ed97f44
```

先頭64bit:

```text
0x94d35b8cc3dc6af5 = 10724007559161629429
```

これをPython `random.Random(seed)` のseedとして `['A', 'B', 'C', 'D']` をshuffleすると:

```text
['C', 'D', 'B', 'A']
```

となる。よってCase 001 Round 1の実行順は **C → D → B → A** で固定する。

## 6. Contamination declaration

このpreflightとPR #2805を設計した会話/agent contextは、次を既知としている。

- provisional product-value hypothesis
- Case 0 audit findings
- M1〜M9 evaluation design
- cultural-substrate-weaving framework candidate notes
- Round 2 external manifest and competitor/research observations
- T1〜T3の評価意図

したがって、このcontextでCase 001の問いへ回答しても **Arm A/B/C/Dの有効runには数えない**。

有効runはoperator packどおり、各armをfresh contextで開始し、armに許された資料/方法だけを与える。

## 7. Preflight findings triage

| Finding | Triage | Reason |
|---|---|---|
| Round 1共通入力20件は固定commitで再取得可能 | evidence / no issue | 実験開始条件を満たす |
| T1〜T3は自然発生の時間差テストとして成立 | evidence / no issue | 新機能要求ではない |
| InquiryJourney Phase 2実使用をC/Dへ接続可能 | F1 existing issue | `DOMAIN-W-ITERATION-01` T9が既に実使用証拠を待っている |
| 現在の実験者contextはarmとして汚染済み | experiment constraint | KJ Atlas製品欠陥ではない |
| new ADR trigger | none | `ADR-0047` R-1〜R-4をまだ実測していない |
| new issue trigger | none | preflightだけではF2条件を満たす実利用課題がない |

## 8. Exit verdict

**P0 passed. Case 001はisolated-arm executionへ進める。**

次の実行はArm C。ただし、このpreflightを行ったcontext自体をArm Cとして再利用しない。
