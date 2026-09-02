# 継続dogfood R15 — IRに残った根拠は実際にAIへ届いているか

- Date: 2026-09-03
- Scope: 日常開発の自己分析。Case 001〜003の統制比較には含めない。
- Question: LLM入力IRに保持できた根拠・矛盾の関係は、移行済みrouteでproviderへ実際に届いているか。
- Canvas: `doc_kj_atlas_dogfood_r15.json`
- Result class: 継続dogfoodの内部所見。第三者価値実証や認知比較結果の代替証拠ではない。

## 1. このラウンドを始めた理由

R12では、一次利用仕事から「意味・根拠・異論・保留を守る変更を、受け渡しの便利さや構造上の整頓より先に置く」という優先順位軸を導いた。

R13では、その軸に直接関わる `AI-IR-PROJECTION-01` について、LLM入力IRの経路棚卸しが手作業へ戻らないよう、IR移行済み4経路とStage 5残債7経路をCI上の明示的な被覆契約へ変えた。

その後、`AI-IR-SCALE-01` のAC-10計測から、300カード・30島では共有IRが100カードを落とすことが分かった。PR #2820では測定をさらにproviderへ実際に渡る最終promptまで進めた。

R15では、その結果をKJ上で分け直す。とくに、共有IRの規模上限による欠落と、IRに残った情報をprompt rendererがさらに落とす欠落を同じ問題として扱わない。

## 2. 使用した材料

- `01_Plans/issues/issue-AI-IR-SCALE-01-preserve-large-round-evidence-under-token-budget.md`
- `01_Plans/issues/issue-AI-IR-PROJECTION-01-llm-input-ir-as-ai-input-path.md`
- `03_Implement/backend/scripts/measure_llm_input_ir_scale.py`
- `03_Implement/backend/tests/test_llm_input_ir_scale.py`
- `03_Implement/backend/scripts/measure_ai_route_prompt_coverage.py`
- `03_Implement/backend/tests/test_ai_route_prompt_coverage.py`
- `03_Implement/backend/src/kj_atlas_api/routes/ai.py`
- PR #2817
- PR #2820
- R12/R13で得た一次価値・IR被覆の判断

生成AIの外部APIは使用していない。#2820の計測も実際のprompt builderを決定論的に呼び出したもので、外部LLMへのrequestやmodel品質評価は行っていない。

## 3. KJキャンバス

正規データは次のDocumentV1に残した。

- `01_Plans/dogfood/doc_kj_atlas_dogfood_r15.json`

今回のカードも生成AIが作成した提案段階の材料なので、`textReviewed: false` としている。

## 4. 島1 — 共有IRの切り詰めと最終promptの欠落は、routeごとに別の形で現れる

300カード・30島・300 relationの代表入力では、共有LLM入力IRの `MAX_CARDS=200` により、カードは200/300、relationは199/300となる。30島自体はIRに残るが、後半10島はメンバーを失う。

しかし、共有IRの件数をそのままproviderへ見える情報量とみなすことはできない。移行済みrouteには、互換性や出力契約のためDocument由来の情報を別の節で描画しているものがある。

#2820の最終prompt計測では次の差が出た。

| route | card text | 完全な島membership | typed relation | 相対座標 |
| --- | ---: | ---: | ---: | ---: |
| `suggest-card-groups` | 200/300 | 20/30 | 199/300 | 対象外 |
| `suggest-layout` | 300/300 | 30/30 | 199/300 | 200/300 |
| `generate-narrative` | 300/300 | 30/30 | 199/300 | 対象外 |

`suggest-layout` や `generate-narrative` は全カード本文をproviderへ渡せているが、relationなどの構造文脈は共有IRの上限を受ける。したがって「全カード本文が見える」ことと「人間が育てた構造が見える」ことを同一視できない。

この結果から、規模対策は単一のcard countだけでは決められない。routeが何を判断するために、どの意味構造を必要とするかを見る必要がある。

## 5. 島2 — 30→20の規模損失と、20→0のrenderer欠落を分離する

さらに、各島に1件ずつ、計30件のheld contradiction evidence linkを加えた副シナリオを測定した。

共有IRでは、`MAX_CARDS` の結果としてevidence linkは20/30件が残る。ここまでは `AI-IR-SCALE-01` が扱う規模coverageの問題である。

一方、最終promptでは次の差が出た。

| route | source evidence | IRに残る | 最終promptで見える |
| --- | ---: | ---: | ---: |
| `suggest-card-groups` | 30 | 20 | **0** |
| `suggest-layout` | 30 | 20 | **0** |
| `generate-narrative` | 30 | 20 | **20** |

`generate-narrative` は `_narrative_relation_lines()` でIRのevidenceをtyped relationとして明示的に描画している。

それに対し、`suggest-card-groups` と `suggest-layout` は `LLMRequest.inputs` に同じ20件を保持していても、その20件を最終promptへ描画していない。provider transportが実際に送信する本体はpromptなので、inputsに存在するだけではモデルへ届いたことにはならない。

したがって、ここには二つの異なる損失層がある。

1. **30 → 20**: 共有IRの規模上限によるcoverage loss。
2. **20 → 0**: prompt rendererによる追加の意味欠落。

後者は、token予算や全体上限の判断を待たなくても、独立して修正できる。

## 6. 島3 — 本文だけ届いても、人間が与えた意味のつながりが落ちれば一次価値は守れない

KJ Atlasの一次利用仕事は、カード本文をAIへ大量に送ることではない。まとまりきらない観察を、根拠・異論・保留・人間の判断権を残したまま構造化し、後から根拠へ戻れる理解へ育てることにある。

そのため、人間が記録した `evidenceLinks` がIRまで来ているのにprovider promptの手前で消えることは、単なるprompt改善ではない。人間がキャンバス上で与えた意味の一部がAI支援へ伝わらない問題である。

一方、`generate-narrative` にはすでにtyped evidenceを描画する実装パターンがある。新しいスキーマやAI判断規則を作る必要はない。`suggest-card-groups` / `suggest-layout` も、IRに残ったevidenceを同じ意味表現でproviderへ渡せばよい。

## 7. 島4 — renderer欠落を先に直し、規模・token判断は別に残す

R15では、rendererによる追加欠落を `AI-IR-PROMPT-EVIDENCE-01` としてP1に切り出した。

このIssueの完了境界は明確に狭くする。

- IRへ残ったevidenceを、`suggest-card-groups` と `suggest-layout` の最終promptへ渡す。
- #2820のevidence scenarioで、3 routeすべてが `source 30 / IR 20 / prompt 20` になることを確認する。
- `MAX_CARDS` は変更しない。
- named providerのtoken予算は推定しない。
- Stage 5の残る7経路は増やさない。

これにより、rendererの不具合を直したことと、大規模入力で安全な投影方式が決まったことを混同しない。

30→20の問題は引き続き `AI-IR-SCALE-01` に残り、named providerの実token観測、意味保存型task別投影、batch/hierarchical投影などの比較を待つ。

## 8. 課題の振り分け

| 観察 | 判定 | 対応 |
| --- | --- | --- |
| routeごとに最終promptのcoverage形状が異なる | F1 | `AI-IR-SCALE-01` へ実測結果を戻す |
| groups/layoutでIRに残った20件のevidenceがpromptでは0件 | F2 / 再現可能な実装不具合 | `AI-IR-PROMPT-EVIDENCE-01` をP1で起票 |
| generate-narrativeは20件を20件とも描画する | 既存実装パターン | 新スキーマを作らず既存表現を再利用する |
| exact token数は未取得 | 外部依存の未完 | `AI-IR-SCALE-01` のnamed-provider観測を維持 |
| Case 001の有効run / 第三者価値実証 | 別系統の外部未完 | R15で代替しない |

## 9. 今回変更しないもの

- Case 001〜003の凍結入力、4-arm条件、実行順。
- `VALUE-REALNESS-01` の第三者価値実証条件。
- `MAX_CARDS` / `MAX_RELATIONS` / `MAX_TEXT_CHARS`。
- named provider/modelのtoken予算。
- `AI-IR-PROJECTION-01` Stage 5の残る7経路。
- SafeMode二層、structured-text-only、proposal-only境界。

## 10. 残る未完

- `AI-IR-PROMPT-EVIDENCE-01` のコード修正と回帰検証。
- `AI-IR-SCALE-01` のnamed provider token観測。
- 30→20のcoverage lossを防ぐ最小の意味保存型投影戦略の決定。
- その判断後のStage 5段階適用。
- `COGNITIVE-EVAL-01` Case 001 Arm Cの有効な生の実行記録。
- `VALUE-REALNESS-01` の第三者による実資料セッション。

## 11. 文書品質の仕上げ

内容、測定値、問題の境界、既存Issueへの戻し先を固めた後、意味を変えずに全文を読み直した。英語の識別子やAPI名は必要な箇所だけ残し、日本語だけでも「どこで何が失われるのか」を追える表現へ整えている。
