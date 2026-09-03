# AI入力IR — route別の必須意味とscale検証マトリクス

- Date: 2026-09-03
- Scope: `AI-IR-SCALE-01` の次段検討材料
- Status: Analysis input
- Related: `ADR-0069`, `llm_input_ir_spec.md`, `AI-IR-PROJECTION-01`, 継続dogfood R16

## 1. 目的

共有LLM入力IRに存在する情報を、すべてのAI routeへ毎回描画することは目的にしない。

scale時のcoverage不足は、次の順序で判定する。

1. routeが何を判断・提案するためのものかを確認する。
2. ADR、仕様、受入条件から、そのrouteで失ってはいけない意味を特定する。
3. source Document → IR → final prompt / deterministic guard の各段で、その意味が残るかを測る。
4. 必須意味が落ちた場合だけ、scale remediationの対象にする。
5. あるIRフィールドが当該routeで不要なら、promptへ描画されないこと自体は欠陥としない。

ここでは、現在IR移行済みの4 routeについて、**明示的な必須意味**と、**現実装では利用しているが現行ACだけからは必須とまでは言えない補助意味**を分ける。

## 2. 判定語彙

- **必須**: 現行ADR・仕様・受入条件・routeの成立条件から、失うと機能契約を満たせない。
- **条件付き必須**: 対象データが存在する場合に、その意味をrouteが利用することが仕様・ACで求められている。
- **補助**: 現実装では利用するが、現行ACから「必ず全件保持」とまでは導けない。
- **非要求**: 現行仕様が不要と明示している、またはrouteの判断材料にしない。

## 3. route別マトリクス

| 意味 | detect-contradiction | suggest-card-groups | generate-narrative | suggest-layout |
|---|---|---|---|---|
| 対象カード本文 | **必須**。比較対象2枚が必要 | **必須**。候補集合そのもの | **必須**。reading order上の内容を叙述する | **必須**。全カードを保持した配置案を返す現行契約 |
| 対象カードID | **必須** | **必須** | **必須** | **必須** |
| `hold_state` | 非要求 | **条件付き必須**。`held/pending/shelved` を候補から除外 | 補助 | 補助 |
| 既存島membership | 補助 | **条件付き必須**。既存島を再提案せず、既決構造を尊重する | reading orderが島を指す場合は実質必須。ただしreading order自体はDocument由来 | **条件付き必須**。島構造を配置判断へ渡す |
| `parent_island_id` | 補助 | **条件付き必須**。AC-2で明示 | 補助 | **条件付き必須**。確定済み階層構造として現行promptへ渡す |
| `placard_card_id` / island review state | 補助 | 補助 | 補助 | 補助。現行promptでは利用 |
| card relation `related` | 補助 | 補助〜条件付き。構造候補の材料 | 補助 | **条件付き必須**。論理的な近接の材料 |
| card relation `causal` / `negate` | 補助 | 補助 | **条件付き必須**。AC-3で叙述の骨格として明示 | **条件付き必須**。論理関係を配置へ反映する |
| `evidence_links` | **条件付き必須**。既存矛盾の再提示防止に使用 | 現行ACでは非要求 | 現実装では利用するが、現行ACでは補助 | 現行ACでは非要求 |
| `contradiction_state` | **条件付き必須**。`confirmed/held` はLLMを呼ばず抑止 | 非要求 | 補助 | 非要求 |
| `coordinates` | **非要求** | **非要求** | **非要求** | **必須**。仕様§2.2.1で唯一「要求」 |
| relation由来 `cluster_candidates` | 非要求 | 補助。構造観察として提示 | 非要求 | 非要求 |
| spatial `cluster_candidates` | 非要求 | 座標を要求しないため通常生成しない | 非要求 | route目的は直接coordinatesを使うため別概念 |
| `readingOrder` | 非要求 | 非要求 | **必須**。ただしIR外のDocument由来入力 | 非要求 |

### 3.1 detect-contradiction

このrouteは「文書全体を均等に見る」よりも、「利用者が指定した2カードについて矛盾を判定する」ことが先にある。

したがってscale時に最も重要なのは、**対象2カードをglobal rankingで落とさないこと**である。

現行の300カードfixtureは、`suggest-card-groups` / `suggest-layout` / `generate-narrative` を測っているが、このtarget-specific routeを直接測っていない。

次のケースを追加する価値が高い。

- 300カード文書を用意する。
- 比較対象を末尾側の `c298` / `c299` とする。
- global `MAX_CARDS=200` が作動しても、対象2カード本文・IDがIRへ残るかを見る。
- その2カード間に `evidence_links` と `contradiction_state=held` を置き、決定論的な再提示抑止が働くかを見る。

対象2カードがglobal selectionで落ちるなら、単なるcoverage率の問題ではなく、**routeが指定した主対象を失う契約違反**である。task-specific projectionで最優先保護すべき候補になる。

### 3.2 suggest-card-groups

このrouteの現行ACで強いのは、次の三点である。

- 既存島を知っていること。
- `parentIslandId` を含む階層を知っていること。
- `holdState` が保留中のカードを候補から除外すること。

現在の300×30 fixtureでは、200カード上限により後半10島がIR上で全メンバーを失う。これはevidenceがpromptへ出ないことより優先して評価すべきである。

追加fixtureでは、後半側の島にも通常候補カードと `hold_state` カードを混在させ、次を測る。

- 非空だった既存島がIR上で無言に空島へ変わらないか。
- 保留カードが切り詰め後の候補制御から漏れないか。
- 既存島のmembership / parent hierarchyが、候補生成に必要な範囲で保持されるか。

「300枚中200枚見える」という件数ではなく、**既決構造と保留判断を壊さないか**で合否を決める。

### 3.3 generate-narrative

現行AC-3が明示している必須意味は、`causal` / `negate` relationである。reading orderはIR外だが、最終promptの叙述骨格として必須である。

現在のscale fixtureは300 relationをすべて `related` としている。そのため `199/300 relation` という観測だけでは、AC-3で本当に守るべき `causal` / `negate` が失われるかを直接検証できていない。

追加fixtureでは、次を意図的に後半カードへ置く。

- reading order後半をつなぐ `causal` relation。
- 前後の主張を緊張させる `negate` relation。
- global ranking上は低くなりやすい孤立・少数カードから伸びるrelation。

合否は、カード総数やrelation総数ではなく、**reading orderの意味上の関節となるcausal/negateを黙って落とさないこと**で見る。

### 3.4 suggest-layout

このrouteは、現行仕様で唯一 `coordinates` を要求する。さらにStage 4では、card relationと島構造を「現在位置とは別の配置判断材料」として渡すことが明示されている。

現行300×30計測では、最終promptのlegacy Cards節に300カードすべてが残っていても、IR由来のrelative coordinatesは200/300、relationは199/300である。

したがって「全カード本文がpromptにある」ことを成功とはしない。

追加fixtureでは、後半100カード側にも次を配置する。

- 別の島に属する近接カード群。
- `causal` / `negate` relation。
- 島間関係を形成するcard relation。

合否は、**配置判断に必要な相対布置・関係・島構造が、全カードを返すという出力契約と整合する範囲で保持されること**で見る。

## 4. 現行300×30 fixtureから既に言えること

### 確認済み

- global `MAX_CARDS=200` は実際に発火する。
- `suggest-card-groups` では候補カード本文が200/300になる。
- 後半10島はIR上でmembershipを失い得る。
- relationは300件から199件へ減る。
- `suggest-layout` のrelative coordinatesは200/300になる。
- `generate-narrative` と `suggest-layout` は別経路のDocument情報を残すため、card textの見え方だけではIR coverageを判断できない。

### まだ言えない

- `detect-contradiction` の指定対象カードが常に保護されるか。
- `suggest-card-groups` で、scale時にも保留カードと既存島の意味が十分保護されるか。
- `generate-narrative` で、実際に必須な `causal` / `negate` がscale時に保護されるか。
- `suggest-layout` で、配置に効くrelation / relative coordinates / island relationをどの最小集合まで保持すべきか。
- named providerの正確なinput token予算。

## 5. 次に追加する決定論的fixture

一つの巨大fixtureへすべてを詰め込まず、routeの契約ごとに失敗を特定できる小さな代表シナリオを追加する。

| Scenario | 主に守る意味 | 期待する判定 |
|---|---|---|
| `detect-target-tail` | 指定2カード、pair evidence、held state | global capより対象指定を優先できるか |
| `groups-late-islands-and-holds` | 非空島membership、parent、hold_state | 後半島・保留判断が黙って消えないか |
| `narrative-late-causal-negate` | reading order後半のcausal/negate | 叙述骨格がglobal rankで落ちないか |
| `layout-late-structure` | relative coordinates、relation、derived island relation | 全カード出力に必要な構造文脈を保てるか |

これらのfixtureはproviderを呼ばない。まず現行投影を決定論的に実測し、どの必須意味が失われるかを固定する。

## 6. remediation候補を評価する順序

測定後は、全route共通のglobal cap引上げを先に決めない。

1. **target protection**
   - routeが明示的に対象指定したカード・島・relationを最優先で残す。
2. **human judgement protection**
   - `hold_state`、adjudicated contradictionなど、人間が既に与えた判断を優先する。
3. **structure protection**
   - 非空島を無言に空にしない。
   - routeの骨格となるrelationを優先する。
4. **task-specific projection**
   - routeに不要な意味は無理に全量送信しない。
5. **batch / hierarchical projection**
   - 一回のpromptへ収まらない場合に、島・区間単位へ分割する。
6. **global cap引上げ**
   - named providerの実token観測で余裕が確認できた場合に比較対象とする。

## 7. 完了条件

この分析文書自体は設計決定ではない。`AI-IR-SCALE-01` を完了するには、少なくとも次が必要である。

- route別fixtureで、現行実装の必須意味coverageを実測する。
- named providerでinput token数を観測する。
- 必須意味を黙って落とさない投影規則を仕様へ反映する。
- 決定論、SafeMode、structured-text-only、proposal-only境界を維持する。
- その後に `AI-IR-PROJECTION-01` Stage 5へ進む。

本マトリクスは、R16で得た「IR全体との差ではなくrouteの必要意味で判定する」という補正を、次の測定へ落とすための入力として扱う。
