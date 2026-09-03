# Issue: AI-IR-SCALE-01 大規模ラウンドでも意味を失わないLLM入力投影を設計する

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Architecture / Feature / Verification
- Status: In Progress
- Source Issue: `AI-IR-PROJECTION-01` AC-10
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/llm_input_ir.py`, `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/backend/scripts/`, `03_Implement/backend/tests/`, `02_Architecture/llm_input_ir_spec.md`
- Related ADR/Spec: `ADR-0069`, `ADR-0047`, `02_Architecture/llm_input_ir_spec.md` §5, `issue-DOGFOOD-31-two-hundred-card-scale-exceeds-ai-operation-limits.md`
- Expected verification level: integration

## R16での解釈補正

PR #2820で得たroute別の最終prompt計測値は、そのまま有効な観測として残す。ただしR15で行った「`suggest-card-groups` / `suggest-layout` では、IRに残ったevidenceが20件から0件になるためrendererの不具合である」という判定は撤回する。

`llm_input_ir_spec.md` と `AI-IR-PROJECTION-01` を再確認すると、LLM入力IRは全フィールドを全routeのpromptへ複製するための共通ペイロードではない。各routeは、業務目的と受入条件に必要な意味構造をIRから使う。したがって、今後のcoverageは**IR全体に対する一致率ではなく、routeごとに契約上必要な意味集合が source → IR → final prompt の各段でどれだけ保たれるか**で評価する。

この補正により、測定スクリプトや既存の数値を捨てる必要はない。変えるのは測定値から欠陥を判定する規則である。`AI-IR-PROMPT-EVIDENCE-01` は実装課題ではなく調査完了としてDoneへ移した。

## 課題

KJ Atlasは、数百枚のカードを扱うKJ実践を正常な利用規模としている。`DOGFOOD-31` では200枚の第1ラウンドを実走し、`suggest-card-groups` のリクエスト上限を100枚から1000枚へ緩和した。

一方、`AI-IR-PROJECTION-01` が導入したLLM入力IRには、現在次の全体上限がある。

- `MAX_CARDS = 200`
- `MAX_RELATIONS = 400`
- `MAX_TEXT_CHARS = 12000`

Stage 5へIR経由を広げる前のAC-10計測として、300カード・30島・300 relation の決定論的な代表入力を作り、現行投影を実行した。その結果、`MAX_CARDS` により次が再現した。

- 300カードのうち200カードだけがIRへ残り、100カードがIRの構造文脈から外れる。
- 30島そのものは保持されるが、後半10島はIR上で全メンバーを失って空島になる。
- ring状の300 relationはIR上で199 relationへ減る。
- `truncation.reason_codes` には `MAX_CARDS` が残るため、切り詰めが発生した事実は分かる。しかし、どの意味領域・島・異論・保留・根拠が失われたかまでは消費側から判断できない。

これは `DOGFOOD-31` の再発ではない。リクエスト自体は200枚超を受けられるようになっているが、その後のIR投影層に別のcoverage境界がある。

### IR coverage と実prompt coverageを分ける

IRから100カードが外れたことを、すべてのrouteで「provider promptから100カードが完全に消えた」と読み替えてはいけない。現在の移行済みrouteには、互換性や出力契約のためDocument由来情報を別経路でも描画しているものがある。

- `suggest-card-groups` は、IR内のカードから実際の候補カード列を描画するため、IRのcard coverageが候補集合へ直接影響する。
- `suggest-layout` は、全カードのid/text/現在座標を従来の `Cards:` 節へ残しつつ、IRから相対配置・relation・島構造を追加している。ここでのIR切り詰めは、カードの存在そのものより**構造文脈のcoverage**を失わせる。
- `generate-narrative` もreading order自体はDocument由来で保持する一方、card-to-cardの論理構造をIRから受ける。したがって失われる情報の種類は `suggest-card-groups` と同じではない。

このため、scale remediationはIR単体の件数だけでなく、**routeの業務目的に必要な意味が、最終promptまでどの程度残るか**を測って判断する。

### 2026-09-03 route別の最終prompt計測

PR #2820で、300カード・30島の同じ代表入力を、移行済み3 routeの実際のprompt builderへ通した。外部LLMは呼ばず、providerへ送られる描画済みpromptを決定論的に比較した。

| route | card text | 完全な島membership | typed relation | 相対座標 |
| --- | ---: | ---: | ---: | ---: |
| `suggest-card-groups` | 200/300 | 20/30 | 199/300 | 対象外 |
| `suggest-layout` | 300/300 | 30/30 | 199/300 | 200/300 |
| `generate-narrative` | 300/300 | 30/30 | 199/300 | 対象外 |

この表はPR #2820時点の**広いcoverage基準によるベースライン**として残す。その後のroute固有remediationによって「どの200枚が残るか」は変わり得るため、個別ACの現在値は後述の「routeごとの必要意味集合」と `measure_ai_route_required_meaning.py` を正本とする。

さらに、各島に1件ずつ計30件のheld contradiction evidence linkを加えた副シナリオでは、共有IRに20件が残った。その20件について最終promptを測ると次の差があった。

| route | source evidence | IRに残る | 最終promptで見える |
| --- | ---: | ---: | ---: |
| `suggest-card-groups` | 30 | 20 | 0 |
| `suggest-layout` | 30 | 20 | 0 |
| `generate-narrative` | 30 | 20 | 20 |

この表はrouteごとのprompt投影差を示す観測として残す。ただし、`suggest-card-groups` と `suggest-layout` にevidence描画を要求する現行ACはないため、`20 -> 0` だけでは不具合と判定しない。IRに存在する全フィールドを全routeへ描画することも要求しない。

一方、`30 -> 20` は共有IRの切り詰めによって参照可能な構造自体が減った結果である。そこで失われた情報が当該routeの必要意味に含まれる場合は、scale remediationの対象になる。

## R19: routeごとの必要意味集合

`AI-IR-PROJECTION-01` のAC、`llm_input_ir_spec.md`、各routeのintegration test、実際のprompt builderを突き合わせ、移行済み4 routeについて「欠落するとそのrouteの仕事または人間判断保護を壊す意味」と「IRに存在するだけでは必須としない情報」を分ける。

| route | 契約上必要な意味 | source → provider手前の経路 | 300カード規模の現在地 |
| --- | --- | --- | --- |
| `detect-contradiction` | 明示対象の `cardA` / `cardB`、およびその2枚について人間が `confirmed` / `held` とした contradiction state。既決判断は再提案しない | `payload.cardA/cardB` → `required_card_ids` → IR。pairの `evidence_links` → IR → `adjudicated_contradiction()`。未確定時はpair関連のrelation/evidenceをprompt文脈に使う | **AC-1に必要な意味は解消済み。** #2827で末尾pairを切り詰めから保護し、`confirmed` / `held` はLLMを呼ばず `alreadyRecorded=true`。座標は非要求 |
| `suggest-card-groups` | `payload.cards` で指定された候補集合、候補に対する人間の `holdState`、既に確定した島と `parentIslandId`。少なくともhold中の候補は新規グループへ入れず、既存島を無視して再分類しない | 候補本文・hold・島階層 → IR → candidate filter / prompt。`holdState` はprompt遵守ではなくコードで候補から除外する | **hold判断は解消済み、全coverageは未解消。** #2830で要求対象のheld cardだけをrequiredとして保護。末尾10枚島の例ではheld 1枚は残るが他9枚は残らず、島全体・候補集合全体を保持したとは扱わない |
| `generate-narrative` | `readingOrder` の完全な順序、および叙述の論理骨格となるcard-to-cardの `causal` / `negate`。明示されたisland-to-island edgeも従来文脈として維持する | `readingOrder` とisland edgeはDocumentからpromptへ。card relationはIRからpromptへ入り、`causal` / `negate` はreading-order上の位置へ写像する | **未解消。** 末尾島はreading orderに残る一方、そのカード間の `causal` / `negate` がIRで落ち、provider手前でも骨格が消える |
| `suggest-layout` | 全カードの出力対象としてのid/text/生の絶対座標、配置判断用の正規化相対座標、typed card relation、確定島階層とcard relationから派生するisland relation | 全カードと生座標は互換 `Cards:` 節でDocumentからpromptへ。相対座標・card relation・島階層はIR、島関係は `derived_island_relations()` からpromptへ | **未解消。** 末尾カード本文・生座標は見えるが、相対座標と末尾 `causal` / `negate` がIRで落ち、構造入力が欠ける。全カードを `required_card_ids` にするだけでは `MAX_CARDS=200` と衝突するため、focus保護の単純横展開はしない |

### 必須としないものの扱い

- `coordinates` は `suggest-layout` だけが要求する。`detect-contradiction` / `suggest-card-groups` / `generate-narrative` で「IRに座標がない」ことをcoverage欠落と数えない。
- `evidence_links` は `detect-contradiction` の既決判断保護には必須だが、現行ACでは `suggest-card-groups` / `suggest-layout` に全evidenceを描画することを要求していない。将来その仕事上の必要性が示された場合にACを先に追加する。
- `generate-narrative` ではevidenceを補助文脈として描画しているが、現行AC-3の最低限の骨格は `causal` / `negate` である。evidence全件coverageを理由にglobal capを変更しない。
- `suggest-card-groups` のrelationは補助文脈として有用だが、AC-2の人間判断保護の核心は候補・hold・既存島/階層である。relation全件一致をremediation完了条件にはしない。
- 「必須ではない」は「捨ててよい」という意味ではない。DocumentV1には保持し、当該routeのprovider入力の欠陥判定に自動的には使わないという区別である。

### route-required probeとの対応

`scripts/measure_ai_route_required_meaning.py` は、上表の意味を300カード・30島の末尾へ置き、source / IR / final prompt（またはLLM呼出前の決定論ガード）を分けて観測する。`tests/test_ai_route_required_meaning_scale.py` は現在次を固定している。

- `detect-target-tail`: focus pairとheld contradictionが残り、人間の既決判断を検出できる。
- `groups-late-islands-and-holds`: 要求対象のheld cardは残ってwithheldになるが、末尾島の全10枚を保持したとは扱わない。
- `narrative-late-causal-negate`: reading orderは残るが末尾の `causal` / `negate` は失われる。
- `layout-late-structure`: 全カードのlegacy表示は残るが、末尾相対座標と `causal` / `negate` は失われる。

このprobeを「全IRフィールドの一致率」ではなく、route契約に対するscale regressionのtripwireとして扱う。detect/groupsのように局所的なrequired意味を安全に保護できたrouteは成功条件へ昇格し、narrative/layoutのように未解決なものはcharacterizationとして残す。

## なぜ問題か

KJ Atlasの一次価値は、根拠・異論・保留・人間の判断を途中で失わず、後から判断の経路へ戻れる理解へ育てることにある。

現在のIR切り詰めは中心性順位を使うため決定論的ではあるが、300枚規模で「IRの3分の1を外し、島を空にする」ことを許す。中心性が低いカードが、少数意見、未決事項、反証、周辺観察である可能性はあるため、単に順序が決定論的であるだけでは意味保存を保証できない。

ただし、意味保存は「Document/IRにある全情報を、すべてのAI taskへ毎回送ること」と同義ではない。routeによって必要な関係・島構造・hold・evidence・座標は異なる。問題にするのは、**そのtaskが判断に必要とする意味が、規模上限のために黙って失われること**である。

また、上限を300や1000へ機械的に引き上げればよいとも限らない。provider transportが実際に送るのは描画済みpromptであり、正確なinput token数はmodel/provider固有である。IRのJSON bytesだけから共通の安全なtoken上限を決めることはできない。

## 三要素分析

| 次元 | 分析 | 他次元への制約 |
| --- | --- | --- |
| 業務設計 | 数百枚の生カードから少数意見・保留・残差を含む構造を育てる。大規模だから周辺の意味文脈を黙って捨てる運用は一次価値と衝突する | 速度や一回のprompt完結を、意味保存より上位に置かない。ただしtaskに不要な情報の全量送信も目的化しない |
| データ設計 | IRは全Documentの複製ではなくLLMへ渡す構造投影である。切り詰め後も「何を代表し、何を落としたか」が追える必要がある | island/evidence/hold等を一律必須とはせず、routeの必要意味に含まれる人間確定情報を中心性だけで無差別に消さない |
| 機能設計 | routeごとに従来promptとIRの役割分担が異なる。global cap引上げ、task別投影、島ごとの代表抽出、batch/hierarchical処理など複数方式がある | provider/modelのtoken予算とSafeMode、決定性、proposal-only境界を維持する |

## 対応方針

### 先に測ること

1. 300カード・30島の代表入力について、移行済みrouteの最終prompt coverageを比較する。**完了。PR #2820で決定論的な測定を追加した。**
   - `suggest-card-groups`: IR truncationが候補集合と、契約上必要な島・relation・holdへどう反映されるか。
   - `suggest-layout`: 全カード節を残したまま、契約上必要なrelation/island/relative-placement coverageがどこまで失われるか。
   - `generate-narrative`: reading orderと、叙述に必要なIR由来の論理構造のcoverage差。
2. routeごとの「必要意味集合」を既存ADR・仕様・ACから明示し、測定項目をその集合へ対応づける。**完了。R19の表と `measure_ai_route_required_meaning.py` / `test_ai_route_required_meaning_scale.py` を対応づけた。** IRに存在するという理由だけで測定項目を必須化しない。
3. 少なくとも次をnamed model/providerで実測する。
   - `suggest-layout` 相当: 座標・島・関係を含む最重量prompt。
   - 座標を使わない代表route。
4. 正確なinput token数は、既存のprovider-reported usageを用いてmodel名とともに記録する。IR bytesから架空のtoken数を推定しない。
5. model/providerがusageを返さない場合は、その事実を記録し、別tokenizer導入を自動的な前提にしない。

### 検討する方式

次を比較し、最初から一案へ固定しない。

- **A: global capを引き上げる**
  - 実測token予算に余裕があり、主要modelで安全に扱える場合。
- **B: task別・意味保存型の投影へする**
  - 各非空島から少なくとも代表カードを残す。
  - `hold_state`、根拠/矛盾リンク、少数・反対所見などのうち、**当該taskの必要意味に含まれるもの**を明示規則で残す。
  - taskに不要な情報を「保存のため」という理由だけでpromptへ全量複製しない。
- **C: batch / hierarchical projection**
  - 全量を一度にpromptへ入れず、島/ラウンド単位で分割し、最終提案へ統合する。

方式B/Cを採る場合でも、AIが勝手に「重要でないカード」を確定削除する設計にはしない。投影上の省略と、DocumentV1上の資料保持は別である。

## 受入条件

- [ ] 300カード・30島の代表規模について、少なくとも1つのnamed model/providerでprovider-reported input token数を記録できる。
- [ ] `suggest-layout` 相当の最重量promptと、座標を使わない代表routeのtoken/coverage差を記録できる。
- [x] `suggest-card-groups` / `suggest-layout` / `generate-narrative` について、IR切り詰めが最終promptのどの情報を失わせるかを区別して記録できる。
- [x] 移行済みrouteごとに、既存ADR・仕様・ACから「必要意味集合」を明示し、その集合に対する source → IR → final prompt のcoverageを評価できる。
- [ ] 300枚規模で、当該routeが必要とする非空島の意味構造がglobal selectionだけを理由に黙って失われない。失われる場合は、消費側がcoverage lossを明示的に判断できる契約を持つ。
- [ ] 保留・根拠・矛盾・少数/反対所見などのうち、routeの必要意味に含まれる人間確定情報を中心性順位だけで無差別に落とさない規則、またはそれらを確実に処理するbatch規則を仕様化する。
- [ ] 切り詰め時に、単なる `MAX_CARDS` だけでなく、少なくとも必要意味のcoverage欠落を後から検証できる情報を残す。
- [ ] 同一入力から同一投影/分割結果を得られる決定性を維持する。
- [ ] SafeMode二層、防PII、structured-text-only、proposal-onlyの既存境界を弱めない。
- [x] 300カード規模のroute-required regressionをテストスイートへ固定する。GitHub Actionsは現在無効のため、CIで実行成功済みとは扱わない。
- [ ] 上限値の変更を行う場合、named model/providerの実測根拠を記録する。

## 検証計画

- 自動確認:
  - `scripts/measure_llm_input_ir_scale.py`
  - `scripts/measure_ai_route_prompt_coverage.py`
  - `scripts/measure_ai_route_required_meaning.py`
  - `tests/test_llm_input_ir_scale.py`
  - `tests/test_ai_route_prompt_coverage.py`
  - `tests/test_ai_route_required_meaning_scale.py`
  - IR単体テスト、移行対象route統合テスト、backend全体回帰。
- 実使用/外部依存確認:
  - 明示的に選んだnamed model/providerで1回以上の代表規模requestを行い、provider-reported usageを保存する。
  - 外部LLMを呼ばない通常の回帰では、exact token countを捏造せず構造・prompt coverageだけを決定論的に検査する。

## 次の判断順序

1. **named provider/modelの実入力tokenを測る。** `suggest-layout` 相当の最重量promptと、座標を使わない代表routeを同じmodel/providerで比較する。
2. `generate-narrative` は、tailの `causal` / `negate` を守るために単純にrelation端点をrequired化してよいかを検討する。readingOrder上の全島・全relationへ広げるとrequired集合自体が大きくなるため、先にtoken予算とbatch候補を比較する。
3. `suggest-layout` は全カードに相対座標が必要な仕事であり、300枚を全て `required_card_ids` にすると `MAX_CARDS=200` を超えてfail-closedする。focus preservationの単純横展開は採らず、global cap・task別投影・batch/hierarchical projectionをtoken実測とともに比較する。
4. coverage-loss metadataは、narrative/layoutの投影方式が決まった後に、その方式で本当に後から検証すべき欠落単位を定めて追加する。先に汎用メタデータだけを増やさない。

## 完了境界

本Issueの最低限の安全な投影戦略とtoken予算判断が得られるまで、`AI-IR-PROJECTION-01` Stage 5を7経路へ一括展開しない。

ただし、Stage 5の各route調査や、IRを使わない現行経路のbug修正を止めるものではない。routeの必要意味が実際にprovider手前で失われていることを仕様・AC・実測の三つで確認できた場合は、この規模判断と切り離して修正してよい。

`AI-IR-PROMPT-EVIDENCE-01` は、この条件を満たさないまま不具合判定した例として調査完了にした。将来evidenceがgroups/layoutの必要意味だと示される場合は、先にその利用仕事とACを明示して別課題として扱う。

## 補足

- 本Issueは `AI-IR-PROJECTION-01` AC-10が明示していた「上限値が現行規模に合わない場合は別issueへ切り出す」を実行したもの。
- route別最終prompt計測はPR #2820で追加した。R15ではevidenceのroute差を不具合と解釈したが、R16で仕様へ戻ってその判定を撤回した。測定値自体は変更していない。
- `detect-contradiction` のfocus pair / 人間の既決矛盾は #2827 でscale保護した。
- `suggest-card-groups` の要求対象に含まれるhold判断は #2830 でscale保護した。ただし候補集合全体や島全体のcoverageを解消したものではない。
- 現時点では長期アーキテクチャ判断を確定しないため、新ADRは起票しない。task別投影やbatchingが複数境界を横断する長期契約へ発展した場合にのみ `ADR-0047` のトリガーを評価する。
