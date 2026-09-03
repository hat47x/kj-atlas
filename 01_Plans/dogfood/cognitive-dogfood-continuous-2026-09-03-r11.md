# 継続dogfood R17 — routeの必要意味からscale欠落を見直す

- Date: 2026-09-03
- Scope: 日常開発の自己分析。Case 001〜003の統制比較には含めない。
- Question: R16で導入した「routeごとの必要意味集合」という基準を適用すると、現在のscale測定から何が実際の欠陥として分離され、何がまだ測れていないか。
- Canvas: `doc_kj_atlas_dogfood_r17.json`
- Supporting map: `ai-ir-required-semantic-coverage-map-2026-09-03.md`
- Result class: 継続dogfoodの内部所見。第三者価値実証や認知比較結果の代替証拠ではない。

## 1. 出発点

R16では、IRに存在する全フィールドと最終promptの一致率をそのまま欠陥判定に使わず、routeの業務目的・ADR・仕様・受入条件が要求する必要意味を先に定めることにした。

R17ではこの基準を、IR移行済み4 routeへ実際に適用した。

対象は次のとおりである。

- `detect-contradiction`
- `suggest-card-groups`
- `generate-narrative`
- `suggest-layout`

外部LLMは使用していない。既存仕様、実装、テスト、PR #2820の決定論的な300枚測定を照合した。

## 2. 必要意味coverage対応表

routeごとの業務目的、明示された必要意味、300枚代表規模での測定状況を次へまとめた。

- `01_Plans/dogfood/ai-ir-required-semantic-coverage-map-2026-09-03.md`

この表では、実装が運んでいるというだけの情報を自動的に「必須」としない。ADR、仕様、既存ACが目的達成または人間判断の保護に必要だと明示したものを中心に判定した。

## 3. 島1 — detect-contradictionで人間の確定判断が切り詰められ得る

最も重要な発見は `detect-contradiction` にあった。

`AI-IR-PROJECTION-01` AC-1は、人間がすでに `confirmed` または `held` とした矛盾を新規発見として再提示しないことを要求している。routeはIR内の `evidence_links` / `contradiction_state` を `adjudicated_contradiction()` で調べ、該当すればLLMを呼ばずに返す。

しかし `_detect_contradiction_ir()` は、`cardA` / `cardB` がDocument内にすでに存在すると、その2枚を特別には保持しない。`build_llm_input_ir()` の `MAX_CARDS=200` は、中心性順位だけで残すカードを決める。

300枚のringで全カードの中心性が同順位なら、id昇順で `c000`〜`c199` が残る。ここで対象を `c250` / `c251` とすると、両カードはIRから落ちる。`_prune_references()` は参照整合を保つため、その2枚を結ぶevidence linkも除去する。

route入力の `cardA` / `cardB` 本文そのものはpromptに残り得る。しかし、人間の `confirmed` / `held` 判断だけがIRから消えるため、`adjudicated_contradiction()` は確定判断を見つけられず、LLM呼び出しへ進み得る。

これはR15で撤回した「IRにある情報は全部promptへ出すべき」という一般論ではない。AC-1が明示している、**このrouteが失ってはならない意味そのもの**である。

そのため、新しいP1として次を起票した。

- `01_Plans/issues/done/issue-AI-IR-FOCUS-PRESERVATION-01-preserve-focus-adjudication-under-truncation.md`

## 4. 島2 — suggest-card-groupsは既知のscale lossと未測定軸が混在する

PR #2820の300枚測定では、`suggest-card-groups` について次を確認済みである。

- candidate card text: 200/300
- 完全な島membership: 20/30
- typed relation: 199/300

これはrouteの主入力と既存島・relationに直接関わるため、必要意味のscale lossとして扱ってよい。

一方、AC-2が明示する次の2軸は、現在の300枚fixtureでは測れていない。

- `holdState`
- `parentIslandId`

小規模integration testで動作が固定されていることと、300枚規模で切り詰め後も意味が保持されることは別である。

したがって、次の代表規模fixture更新ではhold cardと島階層を含める必要がある。

## 5. 島3 — generate-narrativeの現scale測定は核心のrelation型を測っていない

`generate-narrative` のAC-3は、card-to-cardの `causal` / `negate` が叙述の骨格としてモデルへ届くことを要求している。実装の `_narrative_spine_lines()` も、この2型だけをreading order上の「節」として特別に扱う。

しかし現在の300枚代表fixtureは、300 relationすべてを `related` としている。

そのため現在の `typed relation 199/300` は、IR切り詰めで一般的な関係構造が失われることは示すが、AC-3の核心である `causal` / `negate` のscale coverageを直接測っていない。

次の測定更新ではrelation型を決定論的に混在させ、少なくとも次を個別に数える必要がある。

- source causal → IR causal → final prompt causal
- source negate → IR negate → final prompt negate

この測定がない状態で、narrative向けのscale戦略を決めたことにはしない。

## 6. 島4 — suggest-layoutは必要意味の欠落がすでに成立している

`suggest-layout` は、IR仕様でcoordinatesを唯一「要求」するrouteである。出力が配置そのものなので、現在位置から独立した相対布置が入力として意味を持つ。

300枚測定では、legacy `Cards:` 節に全300カードが残る一方、IR由来の正規化相対座標は200/300、typed relationは199/300だった。

全カード本文や絶対座標が見えることは、Stage 4で追加した構造意味が全量見えることを意味しない。

このため `suggest-layout` では、少なくとも次のscale lossは現在の測定だけで成立する。

- normalized relative coordinates: 200/300
- typed card relation: 199/300

一方、`parentIslandId`、placard/review state、derived island relationについては、代表規模で個別coverageをまだ数えていない。

## 7. 優先順位

R17では次の順序が妥当と判断した。

1. `AI-IR-FOCUS-PRESERVATION-01`
   - `detect-contradiction` のhuman adjudication保護は明示ACであり、token戦略全体より先に守る。
2. 代表規模fixtureを必要意味に合わせて更新する。
   - narrative: `causal` / `negate`
   - groups: `holdState` / `parentIslandId`
   - layout: island hierarchy / derived island relation
3. named model/providerでexact input tokenを実測する。
4. 必要意味を保つscale投影戦略を決める。
5. Stage 5の残る7 routeへ段階適用する。

## 8. 今回変更したもの

- route別の必要意味coverage対応表を追加した。
- `AI-IR-FOCUS-PRESERVATION-01` をP1で起票した。
- R17のKJキャンバスを追加した。
- 本継続dogfood記録を追加した。
- 認知dogfood索引へR17を追加する。

## 9. 今回変更しないもの

- `MAX_CARDS` / `MAX_RELATIONS` / `MAX_TEXT_CHARS`。
- provider token予算。
- R15の測定値。
- groups/layoutへのevidence全量描画。
- Stage 5の7 route。
- GitHub Actionsの無効化状態。
- Case 001〜003の凍結入力。
- 第三者価値実証条件。

## 10. 実装境界

`AI-IR-FOCUS-PRESERVATION-01` のproduction fixは、IRの切り詰めアルゴリズムと `detect-contradiction` routeの双方に触れる可能性が高い。

現在GitHub Actionsが別作業で無効化されており、このチャットで利用できるGitHub書込みは大規模Pythonファイルの部分patchを提供しない。R15で巨大な `ai.py` の全文再構成が余分な削除を生み、差分検査で破棄した経緯もある。

そのためR17では、仕様に反する迂回実装や、検証できない巨大ファイル全置換を行わない。再現条件、最小の修正方針、受入条件をP1へ固定し、コードを安全に部分編集・実行検証できる経路で修正する。

これは実装を不要と判断したという意味ではない。むしろAC-1違反として、scale全体判断から切り離して先に直す対象とした。

## 11. dogfoodとして得たこと

R16の補正は、単なる文書上の反省ではなかった。

「routeが本当に必要とする意味は何か」を先に置いたことで、R15では見えなかった `detect-contradiction` のfocus pair問題を発見できた。同時に、narrativeの既存scale testがAC-3の核心型を測れていないこと、groups/layoutにも測定済みと未測定の意味軸が混在していることを区別できた。

つまりcoverageの定義を厳密にした結果、問題を減らしたのではなく、**直すべき問題と、まだ判断できない問題をより正確に分けられるようになった**。

## 12. 文書品質の仕上げ

内容と境界を確定した後、意味を変えずに全文を読み直した。観測、仕様上の要求、推論、未測定事項、修正対象が混ざらないように自然な日本語へ整えた。
