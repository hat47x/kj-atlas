# Cognitive Dogfood Case 001: KJ Atlasの存在目的と一次利用仕事

- Status: Prepared
- Date prepared: 2026-08-29
- Related: `COGNITIVE-DOGFOOD-01`, `COGNITIVE-EVAL-01`, `PRODUCT-POSITION-01`, `VALUE-REALNESS-01`, `PRACTICE-CULTURE-01`
- External method: `hat47x/cultural-substrate-weaving`

## 固定する問い

> KJ Atlasは、既存のAIチャット、ホワイトボード、質的分析ツール、文書/issue管理では十分に満たしにくい、どの利用仕事のために存在するべきか。現在の設計・実装・dogfoodは、その価値をどこまで実現し、何をまだ実証できていないか。

このケースでは、最初から「KJ Atlasは認知環境である」「KJ法市場を狙う」等の結論を固定しない。

## 共通ソーススナップショット

正式実行開始時に、全armで同じcommit SHAを記録する。

最低限の材料:

- `README.md`
- `ROADMAP.md`
- `00_Prompt/kj_technique.md`
- `01_Plans/adr/ADR-0032-product-value-realization-model.md`
- `01_Plans/adr/ADR-0042-value-realness-validation-and-notice-exit.md`
- `01_Plans/adr/ADR-0047-design-decision-adr-saturation-and-execution-first.md`
- `01_Plans/adr/ADR-0057-w-type-cumulative-inquiry-model.md`
- `01_Plans/issues/issue-VALUE-MEASURE-01-measurement-harness-and-evidence-artifacts.md`
- `01_Plans/issues/issue-VR-ROADMAP-01-value-to-social-goal-phase-baseline.md`
- `01_Plans/dogfood/doc_kj_atlas_dogfood_r1.json`〜`r5.json`
- 代表的なDOGFOOD issue（意味接地、大規模カード、階層化等）
- PR #2805 の5 issue memo
- `cultural-substrate-weaving` PR #5 の評価プロトコル

外部競合・研究資料を追加する場合は、全armへ同一の資料一覧を渡す。

## 4 arm

### Arm A — 通常AI + 通常文書

- KJ Atlasキャンバスを使わない。
- `cultural-substrate-weaving` を使わない。
- 同一材料から問いへ回答し、課題・価値・提案をまとめる。

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
- 新しい外部資料が必要になった場合、そのarmだけで結論まで使い切らず「追加資料候補」として記録する。次ラウンドで全armへ同条件で追加する。
- 可能な場合、armの実行順を固定せず入れ替える。
- 最終成果の比較者にはarm名を伏せる。

## 共通成果物

各armは少なくとも次を返す。

1. KJ Atlasが解こうとしている利用者の仕事。
2. 既存手段で十分な領域と、不十分になり得る領域。
3. 現在のKJ Atlasが既に実現している価値。
4. 実証されていない価値仮説。
5. 最重要の反証または「KJ Atlasが不要かもしれない条件」。
6. 次に実施すべき検証/issue。
7. 主張ごとの主要根拠。

Arm C/Dは加えて、最終成果から原カードへ戻れる状態を保持する。

## 評価

`COGNITIVE-EVAL-01` の M1〜M9 を使用する。

本ケースでは特に次を重視する。

- M1 生存所見: 基準線になく、対象へ戻して残る重要所見。
- M2 根拠接地: 価値主張が実装/ADR/dogfood観察へ接地しているか。
- M3 異論・残差保持: 「KJ Atlasは不要かもしれない」材料を保持できるか。
- M4 早期収束耐性: 既存の価値原則を前提に結論を固定していないか。
- M5 AI依存校正: もっともらしい競合比較・市場一般論を根拠なしで採用していないか。
- M6 再訪・訂正可能性: 後の第三者実利用結果で価値定義を修正できるか。
- M8 決定への変換品質: `VALUE-REALNESS-01` 等の実行計画へ変換できるか。

## Case 0との関係

R1〜R5は既存の探索的ケース0として別途監査する。本Case 001の対照実験へ後付けで組み込まず、次を参考観察する。

- R1の問題提起がR5の具体策までどう変形したか。
- 実際に後続ADR/issue/実装へつながった所見。
- 後に訂正・撤回された所見。
- 現在まで残っている未解決カード。

Case 0の結果はCase 001のarm評価を変更する正解表として使用しない。

## 完了条件

- [ ] 共通ソースのcommit SHAと外部資料manifestを固定した。
- [ ] A〜Dを独立に実行した。
- [ ] 各armの生成果を保存した。
- [ ] arm名を伏せた比較レビューを実施した。
- [ ] M1〜M9の測定可否と結果を記録した。
- [ ] 製品 / skill / caller-domain / model-experiment の帰属を行った。
- [ ] 増分なし・悪化を含む結果をそのまま保存した。
- [ ] 新ADRは `ADR-0047` のトリガー成立時だけ起票した。
