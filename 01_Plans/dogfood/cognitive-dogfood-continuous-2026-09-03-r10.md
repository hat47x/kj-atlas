# 継続dogfood R16 — AI入力coverageをrouteの必要意味へ戻って判定する

- Date: 2026-09-03
- Scope: 日常開発の自己分析。Case 001〜003の統制比較には含めない。
- Question: AI入力のcoverage不足を、IR全体との差ではなく、routeごとの利用仕事に必要な意味が失われたかどうかで判定できているか。
- Canvas: `doc_kj_atlas_dogfood_r16.json`
- Result class: 継続dogfoodの内部所見。第三者価値実証や認知比較結果の代替証拠ではない。

## 1. このラウンドを始めた理由

R15では、PR #2820で得たroute別の最終prompt計測をKJ上で整理した。その際、30件のevidence linkが共有IRでは20件に減り、`suggest-card-groups` と `suggest-layout` の最終promptでは0件になることを、共有IRの規模上限とは別のrenderer欠落と判定した。

その判断を実装へ移す前に、`llm_input_ir_spec.md`、`ADR-0069`、`AI-IR-PROJECTION-01` の受入条件へ戻って照合した。その結果、R15は観測値自体ではなく、観測値から不具合へ進む推論に一段の飛躍があったことが分かった。

R16では、R15を消したり書き換えたりせず、何が事実として残り、どの判断を撤回するのかを分けて記録する。

## 2. 使用した材料

- `02_Architecture/llm_input_ir_spec.md`
- `01_Plans/adr/ADR-0069-llm-input-ir-as-the-actual-ai-input-path.md`
- `01_Plans/issues/issue-AI-IR-PROJECTION-01-llm-input-ir-as-ai-input-path.md`
- `01_Plans/issues/issue-AI-IR-SCALE-01-preserve-large-round-evidence-under-token-budget.md`
- `01_Plans/issues/done/issue-AI-IR-PROMPT-EVIDENCE-01-render-ir-evidence-in-provider-prompts.md`（R16開始時点のActiveメモ）
- `03_Implement/backend/scripts/measure_ai_route_prompt_coverage.py`
- `03_Implement/backend/tests/test_ai_route_prompt_coverage.py`
- R15の継続dogfood記録とKJキャンバス

生成AIの外部APIは使用していない。今回も、既存仕様・実装・決定論的な測定結果の照合だけで判断した。

## 3. KJキャンバス

正規データは次のDocumentV1に残した。

- `01_Plans/dogfood/doc_kj_atlas_dogfood_r16.json`

今回のカードも生成AIが作成した提案段階の材料なので、`textReviewed: false` としている。

## 4. 島1 — 測定値は正しいが、routeごとの必要意味を見ずに欠陥とは判定できない

PR #2820で観測したevidenceの件数は変更しない。

| route | source evidence | IRに残る | 最終promptで見える |
| --- | ---: | ---: | ---: |
| `suggest-card-groups` | 30 | 20 | 0 |
| `suggest-layout` | 30 | 20 | 0 |
| `generate-narrative` | 30 | 20 | 20 |

この表は、source Document、共有IR、最終promptの間でrouteごとに投影の形が違うことを示している。

しかし、`llm_input_ir_spec.md` はIRの全フィールドを全routeへ必ず送る契約ではない。座標だけを見ても、`suggest-layout` では要求し、`detect-contradiction`、`suggest-card-groups`、`generate-narrative` では要求しないと明示されている。

`evidence_links` も、IRに型として存在することと、すべてのAI taskで必要な判断材料であることは同じではない。仕様上の直接の導入理由は、`detect-contradiction` が既存の `evidenceLinks` と `contradictionState` を見られるようにすることだった。

既存の受入条件でも、`suggest-card-groups` は既存の島、`parentIslandId`、`holdState` を受け取り、保留カードを新規グループへ含めないことを要求している。`suggest-layout` は正規化座標、relation、島構造を扱う。どちらにも、evidence linkを全件provider promptへ描画することは要求されていない。

したがって、`20 -> 0` は再現可能な投影差ではあるが、それだけでは不具合と認定できない。

## 5. 島2 — 意味の保持と全taskへの全量送信を同一視した推論を訂正する

R15で誤ったのは、「意味を失わない」という一次価値の適用範囲だった。

KJ Atlasでは、人間が与えた根拠、異論、保留、判断をDocumentから失わず、後から戻れる形で保持することが重要である。IRも、AIへ意味構造を渡すための投影として、この価値を支える。

しかし、そこから「IRに保持したすべての意味を、すべてのAI taskのpromptへ毎回描画しなければならない」とは導けない。

Document/IRで意味を保持する境界と、あるtaskの推論材料として選ぶ境界は別である。後者は、そのtaskが何を判断するためのものか、どの意味が必要かという機能契約から決める必要がある。

R15では、この二つを暗黙に同一視した。そのため、promptで0件という観測から「一次価値を壊すrenderer不具合」という結論へ一段飛躍した。

一次価値を強く適用すること自体ではなく、一次価値から個別taskの入力要件を直接導いたことが問題だった。

## 6. 島3 — 誤起票は閉じるが、実在する規模coverage問題はP1として残す

`AI-IR-PROMPT-EVIDENCE-01` は、evidence描画コードを追加する実装課題としては成立しないと判断した。

このIssueは削除せず、次を記録した調査完了として `01_Plans/issues/done/` へ移す。

- `30 -> 20 -> 0` の測定値は残す。
- `20 -> 0` だけでは欠陥と判定できないことを記録する。
- `suggest-card-groups` / `suggest-layout` にevidenceが必要になる場合は、先に利用仕事と受入条件を明示する。
- 現行仕様に根拠がないままrendererを変更しない。

一方、`AI-IR-SCALE-01` はP1のまま残す。

300カード・30島の代表入力で、次は実際に起きている。

- 300カードのうち100カードがIRの構造文脈から外れる。
- 30島のうち後半10島がIR上でメンバーを失う。
- ring状の300 relationが199 relationへ減る。

これは「IRに不要なフィールドがある」問題ではない。routeが必要とするカード・島・relationまで規模上限で失われる可能性があるため、引き続き意味保存型のscale設計が必要である。

## 7. 島4 — routeの必要意味集合を先に定め、観測・推論・決定を分ける

今後の最終prompt coverageは、IR全体に対する一致率では評価しない。

次の順序を使う。

1. routeの業務目的を確認する。
2. ADR、仕様、受入条件から、そのrouteの判断に必要な意味集合を明示する。
3. source Document → IR → final promptの各段で、その必要意味がどれだけ保持されるかを測る。
4. 必要意味が落ちた場合にだけ、不具合またはscale remediation候補とする。
5. IRに存在しても当該taskに不要なフィールドがpromptへ現れないことは、単独では欠陥としない。
6. 新しい意味入力が必要だと判断した場合は、renderer変更より先に利用仕事と受入条件を更新する。

この順序なら、「情報をできるだけ保持する」という上位価値と、「taskごとに入力を選ぶ」という機能設計を対立させずに扱える。

## 8. 課題の振り分け

| 観察 | R16での判定 | 対応 |
| --- | --- | --- |
| evidenceがgroups/layoutではprompt 0件 | route別の投影差 | 測定値は保持するが、単独では不具合としない |
| evidenceがgenerate-narrativeでは20件描画される | route別の意味入力 | 既存実装として保持する |
| groups/layoutにevidence描画を求める現行ACがない | 仕様上の反証 | `AI-IR-PROMPT-EVIDENCE-01` を調査完了へ移す |
| 300→200カード、10島の空洞化、300→199 relation | 再現可能な規模coverage問題 | `AI-IR-SCALE-01` をP1で継続する |
| exact token数は未取得 | 外部依存の未完 | named provider観測を維持する |
| Case 001の有効run / 第三者価値実証 | 別系統の外部未完 | R16で代替しない |

## 9. 今回変更したもの

- `AI-IR-PROMPT-EVIDENCE-01` をActive P1から調査完了へ移した。
- `AI-IR-SCALE-01` のcoverage判定を、IR全体との差ではなくrouteごとの必要意味集合へ補正した。
- R16のKJキャンバスと継続dogfood記録を追加した。
- 継続dogfood索引へR16を追加する。

## 10. 今回変更しないもの

- PR #2820で得た測定値と回帰テスト。
- `MAX_CARDS` / `MAX_RELATIONS` / `MAX_TEXT_CHARS`。
- named provider/modelのtoken予算。
- `AI-IR-PROJECTION-01` Stage 5の残る7経路。
- SafeMode二層、structured-text-only、proposal-only境界。
- Case 001〜003の凍結入力、4-arm条件、実行順。
- `VALUE-REALNESS-01` の第三者価値実証条件。

## 11. 残る未完

- `AI-IR-SCALE-01` で、移行済みrouteごとの必要意味集合を既存仕様・ACへ対応づける。
- named providerでprovider-reported input token数を実測する。
- 300枚規模でもrouteの必要意味を黙って落とさない最小投影戦略を決める。
- その判断後に `AI-IR-PROJECTION-01` Stage 5を段階適用する。
- `COGNITIVE-EVAL-01` Case 001 Arm Cの有効な生の実行記録を得る。
- `VALUE-REALNESS-01` の第三者による実資料セッションを実施する。

## 12. dogfoodとして得たこと

R16で重要なのは、R15の誤判定を消さずに訂正できたことである。

R15には、測定値、そこから導いた推論、起票した課題が残っている。R16では、その測定値を保ったまま、仕様という反証材料を追加して推論だけを撤回した。

これは、AI提案や途中の判断を最終決定と同一視せず、後から根拠へ戻って採否を修正できる状態を保つというKJ Atlas自身の価値と一致する。dogfoodで検出すべきなのは製品の欠陥だけではなく、製品を使う側の判断過程の誤りも含まれる。

## 13. 文書品質の仕上げ

内容と判断境界を固めた後、意味を変えずに全文を読み直した。R15を否定する表現ではなく、「観測は残し、推論を訂正する」という関係が自然に追える日本語へ整えている。
