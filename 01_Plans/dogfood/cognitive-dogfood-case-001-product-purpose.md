# Cognitive Dogfood Case 001: KJ Atlasの存在目的と一次利用仕事

- Status: Prepared / input frozen
- Date prepared: 2026-08-29
- KJ Atlas product snapshot: `main@2232b3bb26647e5c4a083f55bdbf83c161698649`
- cultural-substrate-weaving method snapshot for B/D: `main@3988e12e5f7f316f377d3391e9486c8467a111d5`
- Related experiment governance: `COGNITIVE-DOGFOOD-01`, `COGNITIVE-EVAL-01`

## 固定する問い

> KJ Atlasは、既存のAIチャット、ホワイトボード、質的分析ツール、文書/issue管理では十分に満たしにくい、どの利用仕事のために存在するべきか。現在の設計・実装・dogfoodは、その価値をどこまで実現し、何をまだ実証できていないか。

このケースでは、最初から「KJ Atlasは認知環境である」「KJ法市場を狙う」「offline/self-hostが主価値である」等の結論を固定しない。

## 実験入力と評価資料を分離する

### Armへ渡す製品資料

全armへ、KJ Atlas `main@2232b3bb26647e5c4a083f55bdbf83c161698649` の同一資料を渡す。

最低限の共通材料:

- `README.md`
- `ROADMAP.md`
- `00_Prompt/kj_technique.md`
- `01_Plans/adr/ADR-0032-product-value-realization-model.md`
- `01_Plans/adr/ADR-0042-value-realness-validation-and-notice-exit.md`
- `01_Plans/adr/ADR-0047-design-decision-adr-saturation-and-execution-first.md`
- `01_Plans/adr/ADR-0057-w-type-cumulative-inquiry-model.md`
- `01_Plans/issues/TEMPLATE.md`
- `01_Plans/issues/issue-VALUE-MEASURE-01-measurement-harness-and-evidence-artifacts.md`
- `01_Plans/issues/issue-VR-ROADMAP-01-value-to-social-goal-phase-baseline.md`
- `01_Plans/dogfood/doc_kj_atlas_dogfood_r1.json`〜`r5.json`
- `01_Plans/issues/issue-DOGFOOD-17-opposing-viewpoint-ignores-target-claim.md`
- `01_Plans/issues/issue-DOGFOOD-20-card-groups-not-theme-based.md`
- `01_Plans/issues/issue-DOGFOOD-31-two-hundred-card-scale-exceeds-ai-operation-limits.md`
- `01_Plans/issues/issue-DOGFOOD-32-one-line-heading-hierarchy-missing-for-large-canvases.md`

### Armへ渡してはいけない資料

次は今回の問いに対する仮説・評価設計を含み、答えを先に教えるため、arm実行入力から除外する。

- PR #2805 で追加した `PRODUCT-POSITION-01`
- `VALUE-REALNESS-01`
- `PRACTICE-CULTURE-01`
- `COGNITIVE-DOGFOOD-01`
- `COGNITIVE-EVAL-01`
- `cognitive-dogfood-case-000-r1-r5-audit.md`
- 本ケース文書の評価節・判定基準
- cultural-substrate-weaving PR #5 の評価プロトコル

これらは実験運営者/評価者だけが参照し、armの分析内容には混入させない。

### B/Dだけが使用する方法資料

Arm B/Dには `cultural-substrate-weaving main@3988e12e5f7f316f377d3391e9486c8467a111d5` を方法として使用させる。

これは製品についての追加事実を与える資料ではなく、探索・KJ統合の方法条件として扱う。A/Cには見せない。

## 二段階の資料投入

### Round 1 — 内部証拠のみ

上記のKJ Atlas repository snapshotだけで分析する。

目的:

- 外部の市場カテゴリや競合の言い回しにアンカリングせず、KJ Atlas自身の設計・実装・dogfoodから利用仕事を立ち上げられるかを見る。
- repository内の時間差・訂正・矛盾を扱えるかを見る。

### Round 2 — 共通の外部資料を追加

Round 1を全armで固定した後、競合・研究・実践知の共通manifestを全armへ同一条件で追加する。

目的:

- Round 1の内部仮説が外部比較で維持/修正/棄却されるかを見る。
- 外部資料を最初から与えることで市場カテゴリへ早期固定される影響を避ける。

あるarmだけが見つけた外部資料は、そのarmの結論へ即時混入させず `Candidate source` として保留し、次の共通ラウンドで全armへ配る。

## 自然発生した矛盾・旧情報を評価資源として使う

本snapshotには、後から訂正された主張が意図せず含まれている。これはAI依存校正・時間的推論・根拠接地を測る自然なテストになる。

### Conflict T1 — 三要素チェック

- R3には「三要素牽制設計法はあるがissueテンプレートに三要素チェック欄がない」という当時の問題提起がある。
- 同snapshotの現在の `01_Plans/issues/TEMPLATE.md` には `ADR-0067` を参照する三要素整合欄が存在する。

評価:

- R3の過去カードを現在の未解決課題としてそのまま採用した場合は temporal/provenance failure とする。
- 「当時は問題だったが現在は契約へ反映済み」と時点を分けられた場合は正の証拠とする。

### Conflict T2 — 大規模階層UI

- `DOGFOOD-32` は初期記述で階層UI/ワークフローを未実装と評価した。
- 同issueの後段で、`summaryView`、`hierarchyLevel`、`abstractMapView` 等が既に実装済みであり、初回評価が過大申告だったと訂正されている。

評価:

- issueタイトル/前半だけを読み「現在も未実装」と結論した場合は anchoring / stale-evidence failure とする。
- 訂正を反映し、残課題を1000枚実規模E2E等へ縮小できた場合は M2/M4/M5 の正の証拠とする。

### Conflict T3 — groundingの全件化と10件品質ガード

- `DOGFOOD-31` の初期対応案には大規模島で全メンバー接地へ広げる案がある。
- 後段の実施結果では、10件上限を品質ガードとして維持し、代表的根拠への接地へ方針修正している。

評価:

- 初期案を現在契約として扱わない。
- 経緯を「要求→検討→修正された判断」として扱えるかを見る。

この3件は、偽情報を人工注入せず、実開発の訂正履歴からAI校正を測るための conflict-bearing source とする。

## 4 arm

### Arm A — 通常AI + 通常文書

- KJ Atlasキャンバスを使わない。
- `cultural-substrate-weaving` を使わない。
- 共通資料から問いへ回答し、課題・価値・提案をまとめる。
- 一般的な分析のための見出しやメモは使用可。ただしKJ固有のカード/束ね/表札手順を実験者側から要求しない。

### Arm B — 通常AI + cultural-substrate-weaving

- KJ Atlasキャンバスを使わない。
- `cultural-substrate-weaving` を明示適用する。
- 体系由来所見はremoval/substitution等を通し、対象側で生存したものだけ最終成果へ残す。

### Arm C — KJ Atlas + 通常AI

- KJ Atlasキャンバス上で生カード、束ね、表札、関係、空白、反対視点を扱う。
- `cultural-substrate-weaving` は使わない。
- AI提案はproposal-onlyとし、人間が採否を確定する。

### Arm D — KJ Atlas + cultural-substrate-weaving

- Arm Cの外部表象に加え、`cultural-substrate-weaving` を適用する。
- 文化的体系はカード分類器にせず、探索対象・空白・関係候補を供給する。
- 体系語を除去した後も対象側で生存する所見だけを最終成果へ残す。

## 実行汚染の防止

- 各armは独立コンテキストで開始する。
- 他armの中間成果を見せない。
- armを実行するモデルには、PR #2805で既に作成された価値仮説を渡さない。
- 新しい外部資料が必要になった場合、そのarmだけで結論まで使い切らず「追加資料候補」として記録する。次ラウンドで全armへ同条件で追加する。
- 可能な場合、armの実行順をケースごとに入れ替える。
- 最終成果の比較者にはarm名を伏せる。
- 運営者が既存仮説を知っていることによる期待効果を避けるため、blind reviewerには「どの答えが既存のPRODUCT-POSITION仮説に近いか」を評価させない。

## 共通成果物

各armは少なくとも次を返す。

1. KJ Atlasが解こうとしている利用者の仕事。
2. 既存手段で十分な領域と、不十分になり得る領域。
3. 現在のKJ Atlasが既に実現している価値。
4. 実証されていない価値仮説。
5. 最重要の反証または「KJ Atlasが不要かもしれない条件」。
6. 次に実施すべき検証/issue。
7. 主張ごとの主要根拠と、その根拠の時点。
8. 読んだ資料内で訂正・矛盾・旧情報と判定した箇所。
9. 判断を保留した箇所と、追加で必要な証拠。

Arm C/Dは加えて、最終成果から原カードへ戻れる状態を保持する。

## AI提案ログ

M5を測定できるよう、各armで少なくとも次を保存する。

- `proposal`: AIが提示した主張/分類/比較/判断。
- `evidence`: その提案が参照した資料。
- `human_action`: accept / modify / reject / defer。
- `reason`: 採否理由。
- `later_verdict`: 後続資料またはblind reviewで判明した妥当性。

通常チャットでも、最終成果だけでなく重要な中間提案をこの形式へ抽出する。

## 評価

`COGNITIVE-EVAL-01` の M1〜M9 を使用する。

本ケースでは特に次を重視する。

- M1 生存所見: 基準線になく、対象へ戻して残る重要所見。
- M2 根拠接地: 価値主張が実装/ADR/dogfood観察へ接地し、時点を区別しているか。
- M3 異論・残差保持: 「KJ Atlasは不要かもしれない」材料を保持できるか。
- M4 早期収束耐性: 既存の価値原則・issueタイトル・初期記述を前提に結論を固定していないか。
- M5 AI依存校正: Conflict T1〜T3を含む古い/訂正済み主張を適切に棄却・更新できるか。
- M6 再訪・訂正可能性: 後の第三者実利用結果で価値定義を修正できるか。
- M8 決定への変換品質: 実行可能な価値検証/issueへ変換できるか。

## Case 0との関係

R1〜R5は既存の探索的Case 0として `cognitive-dogfood-case-000-r1-r5-audit.md` で監査する。

Case 0の結果はCase 001の正解表として使用しない。Case 0から引き継ぐのは、対照条件、棄却履歴、不変provenance、摩擦観察が不足していたという**実験設計上の教訓**だけである。

## 完了条件

- [x] KJ Atlas共通ソースのcommit SHAを固定した。
- [x] B/D用のcultural-substrate-weaving commit SHAを固定した。
- [x] arm入力からPR #2805の回答仮説を除外した。
- [x] repository内の自然な訂正履歴をConflict T1〜T3として事前登録した。
- [ ] Round 1のA〜Dを独立に実行した。
- [ ] Round 1の生成果とAI提案ログを保存した。
- [ ] arm名を伏せた比較レビューを実施した。
- [ ] Round 2外部資料manifestを全arm共通で固定した。
- [ ] Round 2を実行し、内部仮説の維持/修正/棄却を比較した。
- [ ] M1〜M9の測定可否と結果を記録した。
- [ ] 製品 / skill / caller-domain / model-experiment の帰属を行った。
- [ ] 増分なし・悪化を含む結果をそのまま保存した。
- [ ] 新ADRは `ADR-0047` のトリガー成立時だけ起票した。