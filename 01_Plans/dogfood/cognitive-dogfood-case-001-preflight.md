# 認知dogfood Case 001 — 実行前確認記録

- 状態: 合格 / 分離されたArm実行へ進める
- 日付: 2026-08-30
- 関連: `cognitive-dogfood-execution-plan.md`, `cognitive-dogfood-case-001-operator-pack.md`, `cognitive-dogfood-case-001-product-purpose.md`
- Product snapshot: `hat47x/kj-atlas@2232b3bb26647e5c4a083f55bdbf83c161698649`
- Skill snapshot: `hat47x/cultural-substrate-weaving@3988e12e5f7f316f377d3391e9486c8467a111d5`

## 1. 目的

Case 001の最初のraw runを保存する前に、比較条件を実際に再現できることを確認した記録である。

この文書にはCase 001の問いへの回答を含めず、A〜Dの成果比較にも使用しない。実行前に確認するのは、sourceの存在、固定snapshot、実行順、自然発生した訂正・時点差チェックの成立、既知の入力汚染、記録契約の整合だけとする。

## 2. 固定source manifestの確認

operator packで指定したRound 1の共通入力20件を、すべてproduct snapshot `2232b3bb26647e5c4a083f55bdbf83c161698649`から取得できることを確認した。

| # | Source | Frozen blob SHA | 結果 |
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
| 11 | `01_Plans/issues/issue-DOMAIN-W-ITERATION-01-w-type-cumulative-inquiry-support.md` | `4597c11804960dd8e6b16c176b8e78fc82013c62` | present |
| 12 | `01_Plans/dogfood/doc_kj_atlas_dogfood_r1.json` | `c6ae2f6635a30d94a5d7bd671785e6fa5e6f1acc` | present |
| 13 | `01_Plans/dogfood/doc_kj_atlas_dogfood_r2.json` | `27a00fddcf6717a0af1ba2bf67ef8faebc7f6985` | present |
| 14 | `01_Plans/dogfood/doc_kj_atlas_dogfood_r3.json` | `edb83ab819984f20052b644898613e1457a8a1f1` | present |
| 15 | `01_Plans/dogfood/doc_kj_atlas_dogfood_r4.json` | `8241de96cb8c7a6267fbdcba840a23d9be6b0950` | present |
| 16 | `01_Plans/dogfood/doc_kj_atlas_dogfood_r5.json` | `9aa694d334409ce3bf3c29fc8a84f61c9b64cf17` | present |
| 17 | `01_Plans/issues/issue-DOGFOOD-17-opposing-viewpoint-ignores-target-claim.md` | `ef3b1be00e0d478fcf23c0bf556b51ec1abca2d1` | present |
| 18 | `01_Plans/issues/issue-DOGFOOD-20-card-groups-not-theme-based.md` | `50124de1ea8b507d5d97ac4c7ea6f85dfb6f6829` | present |
| 19 | `01_Plans/issues/issue-DOGFOOD-31-two-hundred-card-scale-exceeds-ai-operation-limits.md` | `455185f1e12490c6a1d97c45a221491b5c2131cc` | present |
| 20 | `01_Plans/issues/issue-DOGFOOD-32-one-line-heading-hierarchy-missing-for-large-canvases.md` | `49cb747ab1cbb7cf4756eb505c965ee532f8b3fe` | present |

Round 1のcommon source manifest IDは、次で固定する。

```text
case-001-r1-product@2232b3bb26647e5c4a083f55bdbf83c161698649
```

## 3. 現在状態と時点差の確認

### T1 — R3の三要素整合

古いR3 artifactには「issue templateに三要素整合欄がない」という問題提起がある。一方、固定snapshot時点の現在のissue templateには、三要素整合欄が存在することを確認した。

評価時には、R3の過去カードを現在の未解決課題としてそのまま採用していないかを見る。

### T2 — DOGFOOD-32の過大評価訂正

DOGFOOD-32の同一issue memo内に、初期の「階層 / 一行表札が不足」という評価と、後段の「既存の`summaryView` / `hierarchyLevel` / `abstractMapView`等を見落としており、初回評価は過大だった」という訂正が残っていることを確認した。

### T3 — DOGFOOD-31のgrounding方針訂正

DOGFOOD-31の同一issue memo内に、大規模入力への初期対応案と、後段で`groundingIds`上限10を品質ガードとして維持する判断が残っていることを確認した。

T1〜T3はいずれも人工的な偽情報を仕込んだものではない。実際の開発履歴に自然発生した時間差と自己訂正を利用する。

## 4. InquiryJourneyの現在状態

固定snapshotの`DOMAIN-W-ITERATION-01`では、AC-1〜AC-13が完了し、Phase 2手動中核の主要機能が実装済みであることを確認した。

T9は、Phase 2を**実際に使った後**で、Phase 3のproposal-only AI支援を別issueへ分けるか判断する項目として未完了である。T10は別の外部トリガーを持つメニュー配置事項であり、T9とは分けて扱う。

Case 001〜003のC/DはT9の実使用証拠にもなるが、単一runだけでT9を完了させない。

## 5. Arm実行順の再現

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

これをPython `random.Random(seed)`のseedとして`['A', 'B', 'C', 'D']`をshuffleすると、次になる。

```text
['C', 'D', 'B', 'A']
```

したがって、Case 001 Round 1の実行順は **C → D → B → A** で固定する。operator packの旧§11に残っていた「実行開始時にrandomizeする」という記述は、最初のraw runを保存する前に修正した。結果を見て変更したものではない。

## 6. 既知の入力汚染

このpreflightとPR #2805を設計した会話・agent contextは、次をすでに知っている。

- provisional product-value hypothesis。
- Case 0 audit findings。
- M1〜M9 evaluation design。
- cultural-substrate-weaving framework candidate notes。
- Round 2 external manifestと競合・研究資料に関する観察。
- T1〜T3の評価意図。

したがって、このコンテキストでCase 001の問いへ回答しても、**Arm A/B/C/Dの有効なrunには数えない。**

有効なrunはoperator packに従い、各Armをfresh contextで開始し、そのArmに許可された資料と方法だけを与える。

## 7. Preflightで見つかった事項の振り分け

| Finding | 扱い | 理由 |
|---|---|---|
| Round 1共通入力20件は固定commit / blobから再取得可能 | evidence / no issue | 実験開始条件を満たす |
| T1〜T3は自然発生した時間差テストとして成立 | evidence / no issue | 新しい機能要求ではない |
| InquiryJourney Phase 2実使用をC/Dへ接続可能 | F1 existing issue | `DOMAIN-W-ITERATION-01` T9がすでに実使用証拠を待っている |
| 現在の実験者contextはArmとして汚染済み | experiment constraint | KJ Atlas製品の欠陥ではない |
| operator packのArm順記述がpreflightと競合していた | experiment protocol defect / corrected before first run | C → D → B → Aへ一本化した |
| B/Dで必須のskill実行記録に、共通template上の専用欄がなかった | experiment record defect / corrected before first run | run record §12を追加した |
| static intakeが人手確認だけだった | experiment record risk / corrected before first run | `validate_cognitive_run_records.py`を追加した |
| new ADR trigger | none | `ADR-0047` R-1〜R-4をまだ実測していない |
| new product issue trigger | none | いずれも製品実利用前の実験管理上の修正 |

## 8. Protocol補正の境界

ここまでの修正は、**最初のArm raw outputを保存する前**に行った。

修正したのは次だけである。

- 事前登録済みの実行順と文書記述の不一致。
- B/D method executionの記録漏れ。
- source manifestのblob SHA補完。
- static intake validationの追加。
- blind review時の情報漏洩を防ぐ運用契約の追加。

固定問い、A〜D treatment、product snapshot、skill snapshot、T1〜T3、M1〜M9、F0〜F3 gateは変更していない。

最初のraw runを保存した後は、これらの比較条件を結果に応じて変更しない。

## 9. 終了判定

**P0は合格。Case 001は、分離されたArm実行へ進める。**

次に実行するのはArm Cである。ただし、このpreflightを行ったコンテキスト自体をArm Cとして再利用しない。