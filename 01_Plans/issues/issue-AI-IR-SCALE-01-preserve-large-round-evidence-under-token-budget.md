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
| `generate-narrative` | `readingOrder` の完全な順序、および叙述の論理骨格となるcard-to-cardの `causal` / `negate`。明示されたisland-to-island edgeも従来文脈として維持する | `readingOrder` とisland edgeはDocumentからpromptへ。card relationはIRからpromptへ入り、`causal` / `negate` はreading-order上の位置へ写像する | **必要な論理骨格は解消済み。** `AI-IR-NARRATIVE-SPINE-01` / PR #2887でrequired endpointを保護し、R22 / PR #2939でrequired relation自体も先に予約するようにした。300カードの末尾 `causal` / `negate` はIRと最終promptまで残り、required cardが200件またはrequired relationが400件を超える場合は黙って欠落せずfail-closedする。残るのはnamed provider/model上のtoken余裕と長期方式の判断である |
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
- `narrative-late-causal-negate`: R22後はreading orderに加えて末尾のrequired `causal` / `negate` も残る。required card / relation集合そのものがshared budgetを超える場合は黙って縮約せずfail-closedする。
- `layout-late-structure`: 全カードのlegacy表示は残るが、末尾相対座標と `causal` / `negate` は失われる。

このprobeを「全IRフィールドの一致率」ではなく、route契約に対するscale regressionのtripwireとして扱う。detectとnarrativeのrequired意味、groupsのhold判断は成功条件へ昇格している。一方、groupsの候補/島全coverageとlayoutのproduction構造coverageは未解決のままであり、R23以降のB/C候補はproduction採用ではなくcharacterizationとして扱う。

## R20: named providerの実token計測ハーネス

`AI-IR-SCALE-01` の次の判断に必要なtoken予算を、推定ではなくprovider自身のusageから取得するため、`scripts/measure_ai_route_provider_tokens.py` を追加する。対象は、同じ300カード・30島の合成入力から生成した次の2ルートである。

- `suggest-layout`: 正規化座標・関係・島構造を含む、移行済みルートの中で最も重いprompt。
- `generate-narrative`: 座標を使わない代表prompt。`suggest-layout` と同じ入力・同じmodelで比較する。

このハーネスは**入力token数の観測だけを目的とし、モデル品質の評価は行わない**。出力token上限はprovider層が受理する最小値の1に固定し、入力側の費用と構造を観測する。利用者の実文書は送らず、既存の `representative_document()` が生成する合成データだけを使う。

### 実行境界

1. 既定はdry-runとし、providerを生成せず、ネットワークにも接続しない。
2. 外部送信には `--execute` と `KJ_ATLAS_TOKEN_MEASUREMENT_OPT_IN=1` の**両方**を要求する。
3. `--provider` と `--model` を必須にし、現在設定されたproviderと明示名が一致しない場合は、送信前に停止する。
4. providerが返した `LLMResponse.input_tokens` だけを正確な入力token数として採用する。promptの文字数・UTF-8 byte数は診断情報として残すが、token数へ換算しない。
5. providerがusageを返さない場合は `provider-did-not-report-usage` と記録し、`measurement_complete=false` のまま終了する。別tokenizerによる推定で埋めない。
6. fallbackは使わない。計測対象として明示したprovider/modelそのもののusageを測る必要があり、別providerへのfallbackは測定の意味を変えるためである。

現行provider実装では、OpenAI chat-completions互換応答の `usage.prompt_tokens` / `usage.completion_tokens` を `LLMResponse.input_tokens` / `output_tokens` へ写像している。したがって、このusageを返すproviderでは正確な実測が可能である。一方、汎用のlocal/large-scale HTTP契約は現在usageを返さないため、この経路で `measurement_complete=false` になること自体を有効な観測として扱う。

### 実行手順

`03_Implement/backend` を作業ディレクトリとする。

ネットワークを使わず、代表promptとIRの規模だけを確認する場合:

```bash
.venv/bin/python scripts/measure_ai_route_provider_tokens.py \
  --provider deepseek \
  --model deepseek-v4-flash
```

実token数を測る場合は、既存の安全な方法で `KJ_ATLAS_LLM_PROVIDER`、providerの認証情報、必要ならmodel設定を事前に構成する。認証情報をコマンドラインや成果物へ直接書かない。そのうえで次を実行する。

```bash
KJ_ATLAS_TOKEN_MEASUREMENT_OPT_IN=1 \
.venv/bin/python scripts/measure_ai_route_provider_tokens.py \
  --provider deepseek \
  --model deepseek-v4-flash \
  --execute
```

`--provider` / `--model` は例であり、実測結果には実際に使用したprovider名・model idをそのまま残す。

### 回帰テスト

`tests/test_ai_route_provider_token_measurement.py` では、外部ネットワークを使わず次を固定する。

- 同じ300カード入力から、座標ありの `suggest-layout` と座標なしの `generate-narrative` を生成する。
- dry-runではproviderを必要とせず、正確なtoken数を主張しない。
- provider-reported usageをそのまま記録し、byte数からtoken数を推定しない。
- usageが返らない場合は未完了として扱う。
- provider名が一致しない場合は、1件も送信せず停止する。
- 外部実行には専用opt-in環境変数が必要である。

### `check-narrative` を加えたdry-run基準（2026-09-04）

Stage 5で最後に残る `check-narrative` を、R20のprovider token計測ハーネスへ第3の比較対象として追加した。現行production routeをそのまま再現し、IRへ縮約せず、Narrative本文・reading order・30島・300カードを全量promptへ載せる。合成Narrativeは30島を各1行で言及する決定論的な短文とし、Narrative本文だけを恣意的に膨らませない。

外部providerを呼ばないdry-runでは、同じ300カード・30島の代表入力について次の診断値になった。

| route | Unicode文字数 | UTF-8 bytes | 入力方式 |
| --- | ---: | ---: | --- |
| `suggest-layout` | 117,389 | 117,389 | Document + IR構造文脈 |
| `generate-narrative` | 89,321 | 89,322 | reading order + IR論理骨格 |
| `check-narrative` | 168,905 | 171,426 | 現行の全量prompt |

この表は**token数ではない**。文字数・byte数はprompt規模の診断情報としてのみ使い、model固有token数へ換算しない。正確な入力token数は、named provider/modelが返す `usage` だけを採用するというR20の境界を維持する。

`check-narrative` は末尾の `c299` と `i29` までpromptへ含み、現行方式では300カード・30島のcoverageを切り落としていない。一方、dry-runのUTF-8 byte数は比較3ルート中で最大だった。したがって、Stage 5完了のために固定IR上限へ無理に押し込むのではなく、named provider/modelで実token数を測ったうえで、全量を保つA2と、全体被覆を壊さない分割・階層処理Cを主な比較対象とする。実測前にproduction上限や `check-narrative` の入力方式は変更しない。

計測スクリプトはIssue本文に記載した直接CLI形式でも動くよう修正し、直接実行のdry-runを回帰テストへ追加した。外部送信には引き続き `--execute` と `KJ_ATLAS_TOKEN_MEASUREMENT_OPT_IN=1` の二重opt-inを要求する。

### `check-narrative` へのRelation追加後の再計測（2026-09-05）

`AI-IR-CHECK-NARRATIVE-RELATIONS-01` により、`check-narrative` のpromptへ全Edgeを列挙する `Relations:` 節を追加した（A型図解の論理接続をA/B双方向照合で使うため）。同じ300カード・30島の代表入力で、外部providerを呼ばないdry-runを再実行した結果は次のとおりである。

| route | Unicode文字数 | UTF-8 bytes | 入力方式 |
| --- | ---: | ---: | --- |
| `check-narrative` | 195,562 | 198,083 | 現行の全量prompt + 全Edge一覧 |

上記の表（Relation追加前）と比べ、UTF-8 bytesは171,426→198,083（+26,657）へ増えた。これは新たに追加した300 relationの列挙分であり、Narrative本文・reading order・全Card・全Islandの既存coverageは変更していない（回帰は `test_ai_check_narrative_required_meaning.py` で固定）。この値もtoken数ではなく診断情報であり、R20の「正確な入力token数はprovider-reported usageのみ」という境界は変わらない。実token計測・A2/B/C比較の判断順序自体もこの節では変更しない。

## 2026-09-04: named provider実測の実行可能性確認

R20のハーネスを実際のnamed providerへ送れるか確認するため、branch-onlyのGitHub Actions Run `33875031314` で `KJ_ATLAS_DEEPSEEK_API_KEY` の**有無だけ**を検査した。secretの値は取得・出力していない。結果は未設定だった。

このため、合成データであっても外部providerへのrequestは送っていない。provider-reported usageもまだ得られていないので、上記の文字数・UTF-8 byte数をtoken数へ読み替えず、最初の2つの受入条件は未完了のまま維持する。probe用workflowは同じ成功run内で削除した。

次に実測を行う条件は、計測対象として明示したprovider/modelの認証情報が安全な実行環境へ設定されていることである。その条件が満たされた後も、既存の `--execute` と `KJ_ATLAS_TOKEN_MEASUREMENT_OPT_IN=1` の二重opt-inを維持し、利用者データではなく決定論的な合成データだけを送る。

## R21: 上限引上げ・ルート別投影・分割処理の比較

実token計測を待つ間にも、現在の決定論的な上限と代表入力だけから確定できることがある。`scripts/measure_ai_ir_budget_pressure.py` で300カード・30島の代表入力を再計測した結果、1カードの正規化後本文は46文字、300カードの本文合計は13,800文字になる。現行の `MAX_TEXT_CHARS=12,000` を超える。

さらに、§5.2の固定240文字切り詰めは、この代表入力では1枚46文字しかないため何も短くしない。したがって、**`MAX_CARDS` だけを200から300へ引き上げても300枚を完全保持できない**。現行の文字数予算だけを当てはめると、46文字のカードは260枚で11,960文字、261枚で12,006文字となるため、少なくとも40枚はなお除外対象になる。

これはprovider token数の推定ではない。IR自身が持つ文字数上限と、既存の合成入力を突き合わせた決定論的なcharacterizationである。providerに実際に何token届くかはR20で別に測る。

### 方式A: global capを引き上げる

方式Aは一括して扱わず、次の2案に分ける。

- **A1: `MAX_CARDS` だけを300へ上げる**
  - **採用候補から外す。** 代表入力では `MAX_TEXT_CHARS` が次の上限になるため、問題を解消しない。
  - 上限を1つずつ場当たり的に広げると、別の上限へ問題を押し送るだけになる。
- **A2: `MAX_CARDS` と文字数予算を整合させて広げる**
  - 引き続き候補とする。
  - 実装が最も単純で、全カードを一度に見せる意味も保ちやすい。
  - ただし具体的な上限値は、R20で同じ300カード入力をnamed provider/modelへ送り、実入力token数と十分な余裕を確認してから決める。
  - byte数や文字数からmodelのtoken上限を逆算して数値を決めない。

### 方式B: ルート別・意味保存型の投影

全Documentを一律に残す代わりに、そのルートの仕事に必要な意味を先に確保する。

- `detect-contradiction` では、対象2カードと人間の既決矛盾だけをrequiredとして保護する方式が既に機能している。
- `suggest-card-groups` でも、今回の候補集合に含まれるhold判断を局所的に保護する方式が機能している。
- `generate-narrative` では、R22までに `causal` / `negate` のrequired relationと両端カードを先に確保する方式を実装済みである。required集合がshared budget内なら末尾骨格も保持し、集合自体が上限を超える場合はfail-closedする。named provider/model上でA2との差を比較する判断は残る。
- `suggest-layout` は全カードの相対位置が仕事そのものに近い。300カードすべてをrequiredにするだけでは現行 `MAX_CARDS=200` を超えてfail-closedするため、focus preservationをそのまま横展開する案にはしない。

方式Bは、対象が少数へ自然に絞れるルートでは有効だが、すべてのルートへ同じ形で適用する前提にはしない。

### 方式C: batch / hierarchical projection

一度のpromptへ全量を入れず、島・reading order・構造単位で決定論的に分割して処理し、最後に統合する。

利点は、1回あたりの入力予算を抑えながら全資料を処理対象にできることである。一方、単なる「何枚かずつ送る」実装では意味保存にならない。少なくとも次を設計する必要がある。

- 分割境界を同一入力から同一結果になるよう決定論的にする。
- batchをまたぐ `causal` / `negate`、島階層、少数意見、holdなどを境界で消さない。
- 各batchの出力を、そのまま確定結果へ昇格させずproposal-onlyのまま統合する。
- 「どの元カード・関係からどの中間結果が生じたか」を追跡できるようにする。

`generate-narrative` ではreading orderや島を自然な分割単位として使える可能性がある。ただしbatchをまたぐ因果・対立を明示的に橋渡しし、最終叙述で再接続する必要がある。

`suggest-layout` はさらに難しい。R25ではこの条件を30 island-local + 1 global alignmentへ具体化し、全300 card / 300 relationを欠落なくpartitionできるmeasurement-only C候補を固定した。R27では `final = global anchor + local offset` の合成契約をcharacterizeし、synthetic identityで300カードを誤差0.0で再構成できること、欠落・重複・未知ID・非有限値をfail-closedできることまで確認した。これはproduction採用ではなく、単純batchではない階層配置Cが構造的に閉じることの候補証拠である。

### 実token計測後の判断基準

後述の「次の判断順序」を正本とし、ここでは現在の6段階を要約する。

1. named provider/modelのprovider-reported input usageを取得し、保存reportをR32/R33/R35/R37系のidentity/provenance検証へ通す。`decision_ready=true` にならないdry-run・partial・stale・fallback/non-primary結果は比較根拠へ使わない。
2. 文書化されたcontext-window値とsourceを確認できる場合だけ、R39/R41の `input usage + 現行production output reserve` によるhard-fitを確認する。layout Cは31件aggregateではなく最大単一requestを使う。
3. hard-fitとR21の「十分な余裕」は分け、provider/model制約・実測値・必要なら実model品質を根拠にA2/B/Cを**ルートごと**に比較する。A1（`MAX_CARDS` だけを300へ上げる案）は比較対象から外す。
4. `generate-narrative` はR22までに `causal` / `negate` のendpoint/relation保護とbudget超過fail-closedを固定済みなので、named provider/model上のtoken余裕を見ながらA2/B/Cを比較する。
5. `suggest-layout` はR25/R27でCの決定論的partitionとlocal/global合成をmeasurement-only候補として固定済みであり、A2/B/Cのprovider-reported usageと、必要なら配置品質・latency・failure rateを比較してから方式を選ぶ。
6. coverage-loss metadataは方式決定後に、その方式で本当に監査すべき欠落単位へ合わせて追加する。汎用loss metadataを先に作らない。

現時点ではA2/B/Cのいずれも最終採択しない。R20の実測前にproduction上限やnarrative/layoutの投影方式を変更することもしない。

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
3. 少なくとも次をnamed model/providerで実測する。**R20で実測ハーネスを用意した。2026-09-04にGitHub Actionsの認証情報有無だけを確認したが、`KJ_ATLAS_DEEPSEEK_API_KEY` は未設定だったため、外部送信は行わず、実providerでの測定値そのものは未取得のままである。**
   - `suggest-layout` 相当: 座標・島・関係を含む最重量prompt。
   - 座標を使わない代表route。
4. 正確なinput token数は、既存のprovider-reported usageを用いてmodel名とともに記録する。IR bytesから架空のtoken数を推定しない。**R20のハーネスで機械的にこの境界を固定した。**
5. model/providerがusageを返さない場合は、その事実を記録し、別tokenizer導入を自動的な前提にしない。**R20では未完了結果として記録する。**
6. `MAX_CARDS` だけの緩和で300カードを保持できるか確認する。**完了。R21の文字数予算characterizationにより不十分と確定した。**

### 検討する方式

方式の比較条件はR21を正本とする。要約すると、A1（`MAX_CARDS` だけの引上げ）は候補から外し、A2（カード上限と文字数予算を整合して広げる）・B（ルート別意味保存）・C（分割・階層処理）を、R20系の実token測定後にルートごとに比較する。R29でA2の300カード下限fixture、R23でB、R25/R27でlayout Cをmeasurement-only候補として具体化済みである。

方式B/Cを採る場合でも、AIが勝手に「重要でないカード」を確定削除する設計にはしない。投影上の省略と、DocumentV1上の資料保持は別である。

## 受入条件

- [ ] 300カード・30島の代表規模について、少なくとも1つのnamed model/providerでprovider-reported input token数を記録できる。
- [ ] `suggest-layout` 相当の最重量promptと、座標を使わない代表routeのtoken/coverage差を記録できる。
- [x] `suggest-card-groups` / `suggest-layout` / `generate-narrative` について、IR切り詰めが最終promptのどの情報を失わせるかを区別して記録できる。
- [x] 移行済みrouteごとに、既存ADR・仕様・ACから「必要意味集合」を明示し、その集合に対する source → IR → final prompt のcoverageを評価できる。
- [x] 300カード代表入力では、`MAX_CARDS` だけを300へ広げても `MAX_TEXT_CHARS` により全カード保持にならないことを決定論的なcharacterizationで固定する。
- [ ] 300枚規模で、当該routeが必要とする非空島の意味構造がglobal selectionだけを理由に黙って失われない。失われる場合は、消費側がcoverage lossを明示的に判断できる契約を持つ。
- [ ] 保留・根拠・矛盾・少数/反対所見などのうち、routeの必要意味に含まれる人間確定情報を中心性順位だけで無差別に落とさない規則、またはそれらを確実に処理するbatch規則を仕様化する。
- [ ] 切り詰め時に、単なる `MAX_CARDS` だけでなく、少なくとも必要意味のcoverage欠落を後から検証できる情報を残す。
- [ ] 同一入力から同一投影/分割結果を得られる決定性を維持する。
- [ ] SafeMode二層、防PII、structured-text-only、proposal-onlyの既存境界を弱めない。
- [x] 300カード規模のroute-required regressionをテストスイートへ固定する。R22以降branch-only GitHub Actionsで関連回帰を繰り返し実行し、R48 run `33997380006` ではprovider/measurement/analyzerとR23〜R43近接回帰を含む129 test、compile check、fatal/static lint、`git diff --check` が成功した。provider実測reportについてもR32/R33/R35/R37でroute/task/provider/model/usage、canonical user prompt fingerprint、primary call provenanceに加え、DeepSeekでは実transportが送るsystem+user message content fingerprintまでfail-closed検証を固定し、R39ではmeasurementの `max_tokens=1` と現行production output reserveを分離したcontext hard-fit計算、R41ではcontext-window値と資料source provenanceの対、R43ではそのproduction output reserve前提と実route call siteの一致、R48ではDeepSeek V4の `thinking.type` request-mode provenanceを回帰で固定した。恒久workflowの有無とは分けて記録する。
- [ ] 上限値の変更を行う場合、named model/providerの実測根拠を記録する。

## 検証計画

- 自動確認:
  - `scripts/measure_llm_input_ir_scale.py`
  - `scripts/measure_ai_route_prompt_coverage.py`
  - `scripts/measure_ai_route_required_meaning.py`
  - `scripts/measure_ai_route_provider_tokens.py`
  - `scripts/analyze_ai_route_provider_measurement.py`
  - `scripts/measure_ai_ir_budget_pressure.py`
  - `scripts/measure_ai_route_projection_candidates.py`
  - `scripts/measure_ai_route_a2_candidate.py`
  - `scripts/measure_ai_layout_hierarchical_candidate.py`
  - `scripts/measure_ai_layout_hierarchical_composition.py`
  - `tests/test_llm_input_ir_scale.py`
  - `tests/test_ai_route_prompt_coverage.py`
  - `tests/test_ai_route_required_meaning_scale.py`
  - `tests/test_ai_route_provider_token_measurement.py`
  - `tests/test_ai_route_provider_measurement_analysis.py`
  - `tests/test_ai_route_production_output_budget_contract.py`
  - `tests/test_ai_route_provider_prompt_fingerprint.py`
  - `tests/test_ai_route_provider_call_provenance.py`
  - `tests/test_ai_route_provider_transport_input_provenance.py`
  - `tests/test_ai_ir_budget_pressure.py`
  - `tests/test_ai_route_projection_candidates.py`
  - `tests/test_ai_route_a2_candidate.py`
  - `tests/test_ai_layout_hierarchical_candidate.py`
  - `tests/test_ai_layout_hierarchical_composition.py`
  - IR単体テスト、移行対象route統合テスト、backend全体回帰。
- 実使用/外部依存確認:
  - 明示的に選んだnamed model/providerで1回以上の代表規模requestを行い、provider-reported usage、canonical user prompt SHA-256、primary call provenanceを含むmeasurement reportを保存する。DeepSeekの場合はさらに、実transportと同じbuilderから得たsystem+user message contentのprovider-input SHA-256と、実requestの `thinking.type` をprovider-generation provenanceとして保存する。production既定と比較するDeepSeek V4実測では `KJ_ATLAS_DEEPSEEK_THINKING_MODE=disabled` と CLIの `--deepseek-thinking-mode disabled` を一致させ、R48のpreflightを通った場合だけ外部送信する。保存reportは `scripts/analyze_ai_route_provider_measurement.py` を通し、route/task/provider/model/usage/user-prompt fingerprint、transport/requested_at/trace_id、fallbackなし、primary execution pathに加え、DeepSeekではprovider-input fingerprintと `thinking.type` が現在のtransport/期待modeと一致した場合だけ方式比較の入力にする。named model/providerの文書化されたcontext-window値を確認できる場合は `--context-window-tokens` と、その値を採ったprovider/model資料URL・文書ID等の `--context-window-source` を対で明示し、provider-reported input usageに現行production output reserveを加えた最低context必要量がhard-fitするかを別途確認する。sourceは監査用provenanceでありanalyzerが真正性・最新性を自動保証するものではない。hard-fitはR21の「十分な余裕」そのものとは扱わない。
  - 外部LLMを呼ばない通常の回帰では、exact token countを捏造せず構造・prompt coverageだけを決定論的に検査する。

### 外部実測runbook（R50）

R20〜R49で固定した実測契約を、外部送信前に同じ順序で再現できる最小runbookとして正本化する。以下は `03_Implement/backend` を作業ディレクトリとする。API keyは既存の安全な方法で `KJ_ATLAS_DEEPSEEK_API_KEY` に設定済みであることを前提とし、本runbookからsecret値を表示・保存・再確認しない。

1. **まずnetwork-free dry-runを実行する。** これはproviderを解決せず、6 routeのcanonical prompt/report形状だけを確認する。

   ```bash
   python scripts/measure_ai_route_provider_tokens.py \
     --provider deepseek \
     --model deepseek-v4-flash \
     --deepseek-thinking-mode disabled \
     > ai-ir-scale-deepseek-v4-flash-dry-run.json
   ```

   `executed=false`、6 route、`expected_deepseek_thinking_mode=disabled` を確認する。dry-runの `measurement_complete=false` は正常であり、token evidenceとして扱わない。

2. **明示的に外部実測を許可した場合だけ、production既定相当のcore 6 requestを送る。** `--execute` と `KJ_ATLAS_TOKEN_MEASUREMENT_OPT_IN=1` の二重opt-inに加え、provider/model/thinking modeを環境とCLIで一致させる。

   ```bash
   KJ_ATLAS_LLM_PROVIDER=deepseek \
   KJ_ATLAS_DEEPSEEK_MODEL=deepseek-v4-flash \
   KJ_ATLAS_DEEPSEEK_THINKING_MODE=disabled \
   KJ_ATLAS_TOKEN_MEASUREMENT_OPT_IN=1 \
   python scripts/measure_ai_route_provider_tokens.py \
     --provider deepseek \
     --model deepseek-v4-flash \
     --deepseek-thinking-mode disabled \
     --execute \
     > ai-ir-scale-deepseek-v4-flash.json
   ```

   この段階では既定6 requestだけを送り、A2/Cの追加requestは混ぜない。transport/usage契約が正常に成立することを最小call数で先に確認する。

3. **保存reportをanalyzerへ通す。** provider-reported input usage、prompt/provider-input fingerprint、primary call provenance、DeepSeek `thinking.type` が現在の契約と一致した場合だけ `decision_ready=true` になり得る。

   ```bash
   python scripts/analyze_ai_route_provider_measurement.py \
     ai-ir-scale-deepseek-v4-flash.json \
     > ai-ir-scale-deepseek-v4-flash-analysis.json
   ```

   context-windowのhard-fitも評価する場合だけ、provider/model資料で確認した正の値と監査可能なsourceを `--context-window-tokens` / `--context-window-source` の対で追加する。値を推測して埋めない。

4. **core 6が正常に測れた後でのみ、必要なら候補比較を拡張する。** groups A2は `--include-groups-a2` で計7 request、layout Cは `--include-layout-c` で計37 request、両方同時なら計38 requestとなる。追加call数・費用・latencyを理解したうえで明示的に選ぶ。layout A2はR29どおりroute-Bとprompt同一なので重複送信しない。

`--execute` だけを付け、`KJ_ATLAS_TOKEN_MEASUREMENT_OPT_IN=1` を付けない場合は `external-execution-not-opted-in` / exit 2でprovider解決前に停止する。R50のnetwork-free回帰でこの順序も固定する。

### 事前整備の完了境界（R50）

R20〜R49で、代表fixture、current/B/A2/C測定候補、provider-reported usage限定、prompt/provider-input/call provenance、production output reserve、context-window source、DeepSeek V4 model/thinking mode、fail-closed analyzerまで揃った。R50では上記runbookを実CLIでnetwork-free検証したため、**具体的な新欠陥が見つからない限り、外部実測前のscaffolding追加はここで止める**。

以後このIssueで意味のある次の進行は、明示的に許可されたnamed provider/model外部実測からprovider-reported input tokenを取得すること、その結果でhard-fit/十分な余裕/A2-B-Cをrouteごとに判断することである。認証情報や外部実行許可がない状態では、token値を推定せず、方式採択・production cap変更・汎用coverage-loss metadata追加へ先回りしない。

## 次の判断順序

1. **named provider/modelの実入力tokenを測り、保存reportをR32/R33/R35/R37/R39/R41/R48 analyzerへ通す。** R48まで拡張したR20ハーネスを使う。既定はgroups/layoutのcurrent/Bとnarrative/checkの6比較、groups A2も測る場合だけ `--include-groups-a2` で1件追加、layout Cも測る場合だけ `--include-layout-c` で31件追加する。layout A2はR29でroute-Bとrendered promptが完全一致したため、同じprovider/model/task/max_tokens条件では重複requestを送らず `suggest-layout-route-b` のusageを同一prompt観測として扱う。DeepSeek V4をproduction既定と比較する場合は、環境の `KJ_ATLAS_DEEPSEEK_THINKING_MODE=disabled` に加えて `--deepseek-thinking-mode disabled` を明示する。reportにはexact UTF-8 user promptのSHA-256とprimary provider call provenanceを含め、DeepSeekでは実transportが送るsystem+user message contentのSHA-256と実 `thinking.type` も含める。現在のcanonical builder/transport input/期待thinking modeと一致しないstale/legacy report、fallback/non-primary call、trace欠落reportは比較根拠へ使わない。
2. analyzerが `decision_ready=true` と判定したprovider-reported usageについて、named model/providerの文書化されたcontext-window値を確認できる場合はR39/R41の `--context-window-tokens` と `--context-window-source` を対で渡し、**input usage + 現行production output reserve** のhard-fitを確認する。layout Cは31件aggregateではなく最大単一requestを対象にする。context-window値またはその資料sourceが未確認ならhard-fitを推測しない。source参照は監査用であり、analyzerが資料の真正性・最新性を自動検証するものではない。
3. hard-fitを満たすこととR21の「十分な余裕」は分ける。安全余裕policyを後付けで捏造せず、provider/modelの制約・実測値・必要なら実model品質を根拠にA2/B/Cを**ルートごと**に比較する。ここでの `decision_ready` と `hard_context_fit` は方式採択そのものではない。A1（`MAX_CARDS` だけを300へ上げる案）は比較対象から外す。
4. `generate-narrative` の `causal` / `negate` はR22までにendpointとrelationの両方をrequired保護した。required card >200 / required relation >400は既にfail-closedであり、今後の判断対象は主にnamed provider/model上のtoken余裕と、文書規模でA2/B/Cのどれが妥当かである。
5. `suggest-layout` のCはR25/R27でmeasurement-only候補として、決定論的partitionとlocal/global合成まで具体化済みである。A2/B/Cの採択は、provider-reported token usageと、必要なら実model出力の配置品質・latency・failure rateを比較してから行う。
6. coverage-loss metadataは方式決定後に、その方式で本当に検証すべき欠落単位へ合わせて追加する。先に汎用メタデータだけを増やさない。

## 完了境界

本Issueの最低限の安全な投影戦略とtoken予算判断が得られるまで、`AI-IR-PROJECTION-01` Stage 5を7経路へ一括展開しない。

ただし、Stage 5の各route調査や、IRを使わない現行経路のbug修正を止めるものではない。routeの必要意味が実際にprovider手前で失われていることを仕様・AC・実測の三つで確認できた場合は、この規模判断と切り離して修正してよい。

`AI-IR-PROMPT-EVIDENCE-01` は、この条件を満たさないまま不具合判定した例として調査完了にした。将来evidenceがgroups/layoutの必要意味だと示される場合は、先にその利用仕事とACを明示して別課題として扱う。

## 補足

- 本Issueは `AI-IR-PROJECTION-01` AC-10が明示していた「上限値が現行規模に合わない場合は別issueへ切り出す」を実行したもの。
- route別最終prompt計測はPR #2820で追加した。R15ではevidenceのroute差を不具合と解釈したが、R16で仕様へ戻ってその判定を撤回した。測定値自体は変更していない。
- `detect-contradiction` のfocus pair / 人間の既決矛盾は #2827 でscale保護した。
- `suggest-card-groups` の要求対象に含まれるhold判断は #2830 でscale保護した。ただし候補集合全体や島全体のcoverageを解消したものではない。
- R20のtoken計測ハーネスは、正確なtoken数をprovider-reported usageだけに限定し、実providerがusageを返さない場合も推定値で埋めない。
- R21により、300カード代表入力では `MAX_CARDS` 単独引上げが不十分であることを固定した。production上限の変更はまだ行っていない。
- 現時点では長期アーキテクチャ判断を確定しないため、新ADRは起票しない。task別投影やbatchingが複数境界を横断する長期契約へ発展した場合にのみ `ADR-0047` のトリガーを評価する。


## R22 — required relation budget の fail-closed 化

named provider/model の token 実測待ちとは独立に、`generate-narrative` の論理骨格について `MAX_RELATIONS` 境界を詰めた。

- 従来は `causal` / `negate` の**端点カード**だけが `required_card_ids` として保護され、relation自体は `(type, from, to)` 順の先頭400件で通常切り詰めされていた。このため端点がIRに残っても、必要な論理接続だけが消える余地があった。
- shared IR builder に入力専用 `required_relation_ids` を追加した。正規化済みrelation IDだけを受け付け、欠落は `required_relation_missing`、required relation自体が400件を超える場合は `required_relation_budget_exceeded` でfail-closedする。
- required relationの両端点はrequired card集合へ自動的に合流させる。relationを残してendpointを捨てる状態を作らない。
- relation全体が400件を超える場合、required relationを先に予約し、残りだけを従来の決定論的順序で埋める。required指定が空の既存callerでは従来結果を変えない。
- `generate-narrative` は正規化可能な card-to-card `causal` / `negate` のrelation IDを明示的にrequired指定する。これにより「required endpoint <= 200 だが required logical relation > 400」のcharacterizationは、黙った欠落ではなく422で停止する契約になった。
- 回帰テストでは (1) optional relation圧力下で末尾のrequired `negate` が残ること、(2) required relationがendpoint cardも保護すること、(3) 欠落IDを反射せずfail-closedすること、(4) required relation 401件でfail-closedすること、(5) narrative route統合を固定する。

**非主張**: 本変更はproviderが報告するtoken数を測定したものではない。named provider/model実測は引き続き本Issueの別ゲートであり、A2/B/Cの最終選択をここでは行わない。

## R23 — route別B候補の300カードcharacterization

R20のnamed provider/model実測を待つ間に、production配線・shared IR上限を変えず、R19で定義したroute-required meaningだけを残す**測定専用の方式B候補**を300カード代表入力へ当てた。`scripts/measure_ai_route_projection_candidates.py` は既存prompt rendererを使い、source → current shared IR → route-B candidate のcoverageと最終prompt bytesを決定論的に比較する。candidate contextは方式比較用のIR-shaped fixtureであり、新しいproduction IR schemaではない。

### `suggest-card-groups`

| 指標 | current shared IR | route-B candidate |
| --- | ---: | ---: |
| projected requested card | 200/300 | 300/300 |
| providerへ提示可能なgrouping candidate | 199 | 299 |
| holdとして除外されるcard | 1 | 1 |
| requested 300枚のうちaccounted-for | 200 | 300 |
| 完全な島membership | 19/30 | 30/30 |
| 末尾島 `i29` のmember | 1/10 | 10/10 |
| final prompt UTF-8 bytes | 38,044 | 48,791 |

方式B候補では、候補card本文・hold state・確定島階層/membershipを保持し、R19でcompletion criterionではないrelation/derived clusterを外した。その結果、held `c298` を候補へ戻さず、299枚のgroupable cardと30島の完全membershipを同時に表現できた。これはshared `MAX_CARDS=200` を上げずにgrouping-required meaningを全量表現できる構造が存在するというcharacterizationであり、production採用やモデル品質の主張ではない。

### `suggest-layout`

| 指標 | current shared IR | route-B candidate |
| --- | ---: | ---: |
| relative coordinate | 200/300 | 300/300 |
| typed card relation | 199/300 | 300/300 |
| 完全な島membership | 20/30 | 30/30 |
| 末尾 `c298/c299` relative coordinate | 0/2 | 2/2 |
| 末尾 `causal/negate` | 0/2 | 2/2 |
| final prompt UTF-8 bytes | 117,389 | 128,562 |

layoutはlegacy `Cards:` 節が全300枚のid/text/raw座標を既に保持するため、方式B候補では重複するcard本文を増やさず、欠落していた全300枚の正規化相対座標・全card relation・確定島構造を補った。末尾のrelative coordinateと `causal` / `negate` も最終promptまで復元できた。layoutのBはtoken節約策というより、coverageをshared global selectionから分離する手段として評価すべきである。

### 判断への影響

- `suggest-card-groups`: Bは300カードのrequired meaningをglobal capから独立して保持できる具体候補になった。named provider/model実測後はA2とcompact Bを同一modelのprovider-reported usageで比較する価値がある。
- `suggest-layout`: Bでcoverageは回復するが、全体配置に必要な構造は文書規模へ比例する。A2/B/Cのtoken余裕比較は依然必要で、B採用済みとはしない。
- Unicode文字数・UTF-8 bytesをtoken数へ換算しない。正確なtoken数はR20どおりprovider-reported usageだけを採用する。
- production route、`MAX_CARDS/MAX_RELATIONS/MAX_TEXT_CHARS`、SafeMode/PII/structured-text/proposal-only境界は本characterizationでは変更していない。


## R24 — named provider実測をcurrent/B同一run比較へ拡張

R23で方式B候補のcoverageを構造的に比較できたため、R20のprovider token計測ハーネスへ同じ候補promptを接続した。production routeやshared IR上限は変えず、認証情報が利用可能になった時点で**同じnamed provider/modelへの1回の計測run**からcurrent/B差をprovider-reported usageで直接比較できるようにする。

| 比較対象 | UTF-8 bytes (dry-run) | provider-reported input tokens |
| --- | ---: | ---: |
| `suggest-card-groups` current | 38,044 | 実測待ち |
| `suggest-card-groups` route-B | 48,791 | 実測待ち |
| `suggest-layout` current | 117,389 | 実測待ち |
| `suggest-layout` route-B | 128,562 | 実測待ち |
| `generate-narrative` | 89,322 | 実測待ち |
| `check-narrative` | 198,083 | 実測待ち |

このbyte数は診断情報でありtoken推定には使わない。正確な入力token数として採用するのは従来どおりprovider自身が返したusageだけである。`--execute` と `KJ_ATLAS_TOKEN_MEASUREMENT_OPT_IN=1` の二重opt-in、provider/model一致確認、fallback禁止、usage非返却時の`measurement_complete=false`も変更しない。

R24により、認証情報が設定された後の作業は「currentだけを測ってからB用ハーネスを追加する」のではなく、groups/layoutのcurrent/Bとnarrative/checkを同一model上で一度に観測するところから開始できる。A2/B/Cの採択自体は引き続き実測後に行う。


## R25 — `suggest-layout` 階層C候補の決定論的characterization

R21で「A2が十分な余裕を持てない場合は、局所配置と全体整合を分けた階層配置Cを具体化する」としていたため、named provider/model実測を待つ間に **production変更を伴わない測定専用C候補**を300カード・30島・300 relationへ適用した。`scripts/measure_ai_layout_hierarchical_candidate.py` は、R23と同じ末尾 `causal` / `negate` を含む代表入力を、次の二段へ決定論的に分ける。

1. 30個の島内local batch: 各島の直接member 10枚と、両端が同じbatchに属するcard relationを保持する。
2. 1個のglobal alignment batch: 各島を1 nodeとして扱い、島境界を跨ぐcard relationを元のcard IDとrelation type付きbridgeとして保持する。

代表入力での結果は次のとおり。

| 指標 | one-shot route-B | hierarchical C candidate |
| --- | ---: | ---: |
| request数 | 1 | 31（local 30 + global 1） |
| card coverage | 300/300 | 300/300（各cardちょうど1 local batch） |
| relation coverage | 300/300 | 300/300（local 270 + global bridge 30） |
| island coverage | 30/30 | 30/30 |
| 1 request最大 UTF-8 bytes | 128,562 | 7,486 |
| local request UTF-8 bytes | — | 2,673〜2,674 |
| local 30 request合計 UTF-8 bytes | — | 80,219 |
| global alignment UTF-8 bytes | — | 7,486 |
| 全31 request合計 UTF-8 bytes | 128,562 | 87,705 |

末尾の `e298: c298 --causal--> c299` は同じ `i29` local batchへ残り、`e299: c299 --negate--> c000` は `i29 -> i00` を跨ぐglobal bridgeとして残った。したがって、batch境界を理由に論理接続を捨てず、全relationをlocalまたはglobalのどちらか一方へ**ちょうど一度**割り当てられることを固定した。

分割規則もcharacterization上のfail-closed境界を持つ。1枚のcardが複数の直接島membershipへ現れる場合は任意のownerを選ばず停止し、どの島にも属さないcardはsingleton local batchとして残す。sourceのcard / island / edge順を反転しても同じbatch・relation partition・promptを得る回帰を追加した。

**非主張**:
- 上記bytesはtoken数ではなく、providerの入力上限・費用を推定する値として使わない。
- 31回呼出しのモデル品質、出力token、latency、失敗率、local座標とglobal anchorの最終合成品質はまだ評価していない。
- Cをproduction方式として採択していない。R24のcurrent/B比較と同様、named provider/modelのprovider-reported usageが得られた後にA2/B/Cをrouteごとに比較する。
- production route、shared IR cap、SafeMode、防PII、structured-text-only、proposal-only境界は変更していない。


## R26 — layout C provider usage を明示opt-inで測定可能にする

R25で `suggest-layout` の階層C候補を30 local + 1 globalの31 requestとして具体化した。一方、R20/R24のnamed provider計測ハーネスは既定で6比較だけを送る契約であり、C候補を無条件に加えると、実測時のprovider call数・費用・待ち時間を6件から37件へ黙って増やしてしまう。そこで、C実測は**追加の明示opt-in**として接続した。

- `build_representative_requests()` / `measure()` は `include_layout_c=False` を既定とし、通常のdry-run/executeはR24の6比較を変えない。
- CLIへ `--include-layout-c` を追加した。このflagを指定した場合だけ `suggest-layout-c-local-01..30` と `suggest-layout-c-global` の31 requestを追加し、全体で37 requestになる。
- 外部送信には従来どおり `--execute` と `KJ_ATLAS_TOKEN_MEASUREMENT_OPT_IN=1` が必要であり、Cについてはさらに `--include-layout-c` を明示しなければ送られない。provider名/model id一致確認、fallback禁止、合成データ限定も維持する。
- Cの各requestはR25のmeasurement-only promptをそのまま使う。provider transportが送るのはpromptだけであり、この経路をproduction IR contractとして扱わない。
- `layout_c_summary` は、Cを含めた場合のrequest数、最大単一prompt bytes、全C prompt bytes合計を診断値として返す。dry-runではR25と同じ **31 request / 最大7,486 bytes / 合計87,705 bytes** を再現した。
- 実provider実行時の `aggregate_input_tokens` / `max_single_input_tokens` は、31件すべてが `input_tokens` をprovider-reported usageとして返した場合だけ集計する。1件でもusageが欠ければ両値を `None` のままにし、byte数から補完しない。

回帰では、既定6 requestが増えないこと、C付きだけ37 requestになること、direct CLI dry-runがnetwork-freeであること、fake providerのreported usageだけからC集計値を作ること、usage欠落時に未完了のまま止めることを固定した。R25/R23回帰を含む22 test、ruff、`git diff --check` はGitHub Actions run `33940160064` で成功した。

**非主張**: R26でも外部providerは呼んでいない。Cの31 requestに対する実token数、総費用、latency、failure rate、local/global出力を合成した最終配置品質は未測定である。A2/B/Cの採択はnamed provider/modelのprovider-reported usageを得た後に行う。


## R27 — layout C のlocal/global出力合成契約をcharacterizeする

R25でlayout Cの入力を30 local + 1 globalへ欠落なく分割し、R26でその31 promptを明示opt-in時だけnamed provider計測へ載せられるようにした。一方、Cを実方式として考えるには「31個のstage出力から、最終的に300カードを1つの座標空間へ戻せるか」という合成契約も必要である。これはprovider/model品質とは独立に決定論的に検証できるため、`scripts/measure_ai_layout_hierarchical_composition.py` で**測定専用のlocal/global合成器**をcharacterizeした。production `/ai/suggest-layout` は変更していない。

合成規則は単純に、各cardについて `finalX = batch.anchorX + card.dx`、`finalY = batch.anchorY + card.dy` とする。local stageはbatch自身の原点まわりのoffsetだけを返し、global stageはbatch anchorだけを返す。viewportのpan/zoomは階層処理が新しく発明せず、source Documentのtransformをそのまま保持する。

300カード・30島のR25代表入力に対して、元の各島centroidをglobal anchor、元座標からcentroidを引いた値をlocal offsetとするsynthetic identity responseを作り、合成した結果は次のとおりだった。

- card ID: 300/300を各1回保持。
- source座標の再構成: x/yとも最大絶対誤差 **0.0**。
- source transform: `panX=0, panY=0, zoom=1` をそのまま保持。
- global translation probe: 全anchorを `(x + 250, y - 125)` とすると、300/300 cardが同じvectorだけ移動し、期待座標との差はx/yとも **0.0**。
- local perturbation probe: `island:i29` 内の `c299` のlocal offsetだけを `(dx + 7.5, dy - 3.25)` とすると、移動したIDは **`c299` だけ**で、期待座標との差はx/yとも **0.0**。
- direct island membershipから外れたcardをR25規則でsingleton batchにした場合も、そのcardを含む300枚全量を再構成できる。

さらに、stage出力を「一部だけ都合よく採用」しないため、合成器は次をfail-closedで固定した。

- local response集合はplan上のbatch集合と完全一致しなければならない。
- 各local responseは、そのbatchのcardを全件・重複なし・未知IDなしでちょうど1回ずつ返さなければならない。
- global responseは全batch anchorを全件・重複なし・未知IDなしでちょうど1回ずつ返さなければならない。
- local offset / global anchor / composed coordinateは有限数だけを受け付ける。
- 最終compositionはsource card集合を全量・各1回覆わなければならない。
- source card / island / edge順を反転してもidentity composition結果は同一になる。

GitHub Actions run `33947383473` では、R27新規回帰にR25/R26/R23系を加えた **33 test**、ruff、`git diff --check` が成功した。一時workflowは成功後に自己削除済みである。

**非主張**: R27で使ったstage出力はすべてsynthetic fixtureであり、外部providerは呼んでいない。したがって、実modelが良いlocal offset / global anchorを返すか、31出力を用いた最終配置がone-shot Bより良いか、token費用・latency・failure rateが許容できるかは未評価である。R27が閉じたのは「有効なstage出力が揃ったなら、意味のある二段座標系を決定論的かつ完全に1配置へ合成できる」という構造契約までであり、Cのproduction採択やA2/B/Cの最終選択ではない。


## R28 — R22〜R27後のIssue正本整合

R22〜R27で実装・characterizationが進んだ一方、Issue前半には過去時点の「narrative末尾relationが失われる」「required relation >400は未整理」「layout Cは今後具体化」「GitHub Actionsは無効」という記述が残っていた。R28では**production状態や受入条件を前倒しせず**、これらを現在の事実へ同期した。

- narrativeはrequired endpointだけでなくrequired relation自体もR22で保護済みであり、shared budget超過時はsilent lossではなくfail-closedすることへ統一した。
- layout CはR25のpartition、R26の明示opt-in provider計測経路、R27のlocal/global合成までmeasurement-only候補として具体化済みであることを判断順序へ反映した。
- 検証計画へR23/R25/R27のcharacterization script/testを追加した。
- branch-only GitHub Actionsで関連回帰が成功している現在地へCI記述を更新した。ただし恒久workflowの存在やproduction完了を意味しない。
- provider-reported token usage未取得、groups/layoutのproduction scale strategy未採択、A2/B/C未決定という受入条件は変更していない。

**非主張**: R28は文書整合だけであり、production上限・route・IR schema・provider実行境界を変更しない。本IssueのStatusは引き続きIn Progressである。


## R29 — A2をproduction cap変更なしで代表入力へcharacterizeする

R23で方式B、R25/R27でlayout方式Cをmeasurement-only候補として具体化した一方、A2（card上限とtext予算を整合して広げる）はR21の判断基準だけで、同じ代表入力上の具体prompt比較がなかった。そこで `scripts/measure_ai_route_a2_candidate.py` を追加し、production定数を変更せずに、300カード代表入力がshared IRへ**ちょうど収まる下限fixture**をcharacterizeした。

下限fixtureは、sourceを正規化した結果から `MAX_CARDS=300`、`MAX_TEXT_CHARS=13,800` を一時的に適用し、`MAX_RELATIONS=400` は現行値のままとする。これは余裕を持ったproduction cap案ではなく、代表入力についてcard/text由来のtruncationを起こさないための下限に過ぎない。context manager終了時には例外発生時も含め、production定数 `200 / 12,000 / 400` が復元される回帰を固定した。

代表入力での結果は次のとおり。

| route | A2下限候補 | route-B候補 | 観測 |
| --- | ---: | ---: | --- |
| `suggest-card-groups` | 56,047 UTF-8 bytes | 48,791 UTF-8 bytes | 両方とも300/300候補、30/30島、held 1件を保持するがpromptは非同一。A2はshared IR由来の300 relationも保持し、BはR19で必須でないrelationを省く |
| `suggest-layout` | 128,562 UTF-8 bytes | 128,562 UTF-8 bytes | 300座標・300 relation・30島を両方とも保持し、**rendered promptは完全一致** |

A2下限候補はgroups/layoutとも `truncation=false` となり、groupsでは299 groupable + held 1、layoutでは末尾 `c298/c299` 座標と `causal` / `negate` も保持した。これによりA2が「300カードなら一律Bと同じ入力」ではないことが明確になった。groupsではBの意味選択がpromptを実際に小さくする一方、layoutではroute-required構造がほぼshared IR全量に近いため、この代表入力ではA2とBがproviderへ送るpromptとして同じになる。

このlayout同値性はtoken推定ではない。prompt文字列が同一で、既存provider transportが `LLMRequest.inputs` ではなくpromptを送るというR24/R26の測定契約上、同じprovider/model/task/max_tokensならlayout A2のinput token測定をBと別requestで重複させる必要がないことを示す。一方、groups A2はpromptが異なるため、exact token比較が必要ならnamed provider/modelで別途測る必要がある。

GitHub Actions run `33947860553` では、R29とR23/R24/R25/R27関連を含む **39 test**、ruff、`git diff --check` が成功した。一時workflow/patch helperは成功後に自己削除済みである。

**非主張**: `300 / 13,800` はproduction上限案ではなく、代表fixtureをちょうど収める下限値である。bytesはtoken数ではなく、providerの入力上限や費用へ換算しない。外部providerは呼んでおらず、A2/B/Cの採択も行っていない。productionの `MAX_CARDS=200 / MAX_TEXT_CHARS=12,000 / MAX_RELATIONS=400` は変更していない。


## R30 — groups A2のprovider usageを追加明示opt-inで測定可能にする

R29でA2下限候補をcharacterizeした結果、`suggest-card-groups` はA2とBでpromptが異なる一方、`suggest-layout` はA2とBのrendered promptが完全一致した。そこでnamed provider/model実測の公平性を高めつつ、不要なprovider callを増やさないよう、R20/R24/R26の計測ハーネスへ**groups A2だけを追加の明示opt-in**として接続した。

- 既定動作は従来どおり6 requestのまま変更しない。
- CLIへ `--include-groups-a2` を追加した。このflagを指定した場合だけ `suggest-card-groups-a2-lower-bound` を1 request追加し、7 requestになる。
- `--include-groups-a2 --include-layout-c` を両方指定した場合は、既定6 + groups A2 1 + layout C 31 = **38 request**になる。
- layout A2はR29でroute-Bとprompt文字列が完全一致しているため、`suggest-layout-a2-lower-bound` の重複provider requestは追加しない。layout A2のexact input usage比較には既存 `suggest-layout-route-b` のprovider-reported usageをそのまま同一prompt観測として使える。
- groups A2 promptを作る際だけR29のtemporary representative-fit budgetを使い、provider requestを構築する前にproduction定数 `MAX_CARDS=200 / MAX_TEXT_CHARS=12,000 / MAX_RELATIONS=400` へ復元する。
- 外部送信には従来どおり `--execute` と `KJ_ATLAS_TOKEN_MEASUREMENT_OPT_IN=1` が必要であり、groups A2を送るにはさらに `--include-groups-a2` が必要である。provider/model一致確認、fallback禁止、合成データ限定も維持する。
- groups A2の56,047 UTF-8 bytesはdiagnosticであり、provider usageへ換算しない。fake provider回帰では7件目に任意のreported usage `106` を返し、その値だけが `input_tokens` として記録されることを確認した。usage欠落時は `provider-did-not-report-usage` のままmeasurement incompleteになる。

GitHub Actions run `33948026246` では、既定6 / A2 7 / A2+C 38のdry-run件数、direct CLIのnetwork-free性、provider-reported usageのみを採用する境界、R23〜R29関連を含む **45 test**、ruff、`git diff --check` が成功した。一時workflow/patch helperは成功後に自己削除済みである。

**非主張**: R30でも外部providerは呼んでいない。groups A2のexact token数は未測定であり、layout B/A2やCの実token数も未測定である。A2/B/Cのproduction採択、shared IR cap変更、route変更は行っておらず、本Issueは引き続きIn Progressである。


## R31 — R29/R30後のprovider実測readiness同期

R29でA2下限fixtureをcharacterizeし、R30でgroups A2だけを追加明示opt-inとしてprovider計測ハーネスへ接続したため、Issue前半の方式要約・検証計画・次の判断順序を現在地へ同期した。

- A2/B/Cはいずれもproduction非変更のmeasurement-only候補として比較可能になったことを方式要約へ反映した。
- 検証計画へ `measure_ai_route_a2_candidate.py` / `test_ai_route_a2_candidate.py` を追加した。
- named provider/model実測手順を、既定6件、groups A2追加時7件、layout C追加時37件、両方追加時38件となるR30契約へ更新した。
- layout A2はR29でroute-Bとrendered promptが完全一致したため、重複provider requestを送らない判断を明記した。
- branch-only regressionの記録をR30 run `33948026246` の45 test成功へ更新した。

**非主張**: R31は正本同期のみであり、未完了の受入条件を完了扱いにしない。provider-reported usageは依然未取得で、production strategy、上限値、A2/B/Cの採択、本IssueのIn Progress状態は変更しない。

## R32 — provider実測結果のfail-closed検証・比較analyzer

R30まででnamed provider/modelへ実測する入力集合は揃ったが、保存したJSONをそのまま人手で読み、dry-runやpartial resultを誤って方式比較の根拠へ昇格させる余地が残っていた。そこで `scripts/analyze_ai_route_provider_measurement.py` と `tests/test_ai_route_provider_measurement_analysis.py` を追加し、R20/R24/R26/R30のmeasurement reportを**provider実測後の判断入力として使えるか**だけを機械的に検証する層を固定した。

- 正本scenario `300-cards-30-islands-ring` とmeasurement kindを要求する。
- 既定6 routeはすべて `status=measured`、expected/actual provider一致、expected/actual model一致、非負整数の `provider_reported.input_tokens` を要求する。dry-run、missing usage、provider/model mismatch、route欠落はfail-closedする。
- groups A2はR30の追加routeが存在するときだけ比較可能とし、current / B / A2のtoken差をprovider-reported値だけから算出する。prompt bytes/charsは一切tokenへ変換しない。
- layout A2はR29の「route-Bとrendered prompt完全一致」契約により、route-B usageを同一prompt観測として再利用することを明示する。重複provider requestは追加しない。
- layout Cが存在する場合はlocal 30 + global 1の**31件全部**がmeasuredでなければaggregate/max tokenを出さない。partial Cを31件相当へ補完・推定しない。
- Cの `max_single_input_tokens` は1 requestあたりの圧力、`aggregate_input_tokens` は31 request総量として別々に保持する。A2/Bの1 request値とC aggregateを同じ意味の数字として扱わない。
- analyzer自身はmodel context limitを知らず、A2/B/Cを選択しない。`decision_ready` は「少なくとも既定6 routeの実測reportが内部整合している」ことだけを表し、方式採択の判定ではない。

branch-only GitHub Actions run `33950682087` で初期54 test、hardening後のrun `33950879266` でR32とR23〜R30関連を含む **56 test**、ruff、`git diff --check` が成功した。後者ではcanonicalなlocal-01〜30 + globalのexact setとroute task identityも固定し、31件という件数だけを満たす改変reportをfail-closedする。workflowは各run内で自己削除した。テストではprompt byte値をprovider token値と意図的に無関係な数へ崩し、差分計算が `provider_reported.input_tokens` のみを使うことも固定した。

**非主張**: 外部providerは呼んでいない。実token値、modelの安全余裕、cost、latency、品質は未取得であり、A2/B/Cの採択・production cap・production routeは変更しない。本Issueは引き続きIn Progressである。

## R33 — provider usage と canonical prompt のfingerprint binding

R32で保存measurement JSONのroute/task/provider/model/usage整合はfail-closed化したが、そのusageが**現在のcanonical promptそのもの**を測った結果かは、route名だけでは後から証明できなかった。prompt実装が変わった後に古いusageを誤って再利用することを防ぐため、R33ではproviderへ送るexact UTF-8 promptにSHA-256 fingerprintを付与し、measurement harnessとresult analyzerを同じidentity contractで結んだ。

- `measure_ai_route_provider_tokens.py` は各routeの `prompt.sha256` と、top-level `prompt_fingerprint={algorithm: sha256, encoding: utf-8}` を記録する。hashはprompt identity専用でありtoken推定には使わない。
- `analyze_ai_route_provider_measurement.py` は保存reportのoptional A2/C構成を読み、同じmodel・canonical builderから現在のrequestを決定論的に再生成する。routeごとのSHA-256が一致しなければ `prompt-fingerprint-mismatch` でfail-closedする。
- fingerprint contract自体がない旧形式reportも `unsupported-or-missing-prompt-fingerprint` としてdecision-readyに昇格させない。prompt変更後は再測定が必要になる。
- canonical request集合にない余分なrouteも `unexpected-route` として拒否する。R32のexact task / exact C route-set検証と合わせ、route名・task・prompt本体の三層でmeasurement identityを固定する。
- SHA-256、UTF-8 byte数、文字数はいずれもtoken数へ変換しない。token値と差分は引き続きprovider-reported `input_tokens` のみを正本とする。

branch-only GitHub Actions run `33951131455` で、R23〜R33関連を含む **62 test**、ruff、`git diff --check` が成功した。38-request dry-runの全prompt fingerprint、1文字変更時のfingerprint変化、stale/legacy reportのfail-closedを回帰へ固定し、一時patch/workflowも同run内で自己削除した。

**非主張**: fingerprintはprovider responseの暗号学的署名ではなく、偶発的なstale/mismatched measurementを防ぐための再現可能なprompt identityである。外部providerは呼んでおらず、実token値・context余裕・cost・latency・品質、A2/B/C採択、production cap/routeは引き続き未変更である。

## R34 — R32/R33後のprovider実測readiness同期

R32/R33でprovider measurementの保存・検証境界が強化されたため、Issue前半の受入条件注記・検証計画・次の判断順序を現行実装へ同期した。named provider/model実測後は、usageを直接A2/B/C比較へ持ち込まず、canonical prompt fingerprintを含む保存reportをR32/R33 analyzerへ通し、route/task/provider/model/usage/prompt identityが現在のbuilderと一致した結果だけをR21の比較入力にする。

本同期はdocs-onlyであり、未完了ACを完了へ変更せず、provider実測・A2/B/C採択・production cap/route変更を行わない。

## R35 — provider usage に call provenance を結び付ける

R33まででprovider-reported usageをcanonical promptへSHA-256で結び付けたが、成功responseが**いつ・どのtransport・どのtrace・どのexecution pathで得られたか**という既存 `LLMCallMetadata` の監査情報はmeasurement reportへ保存していなかった。R35ではprovider実測時に `response.metadata.as_audit_fields()` を各routeへ保存し、usage値とcall provenanceを同じrowで追跡できるようにした。

- measurement reportはtop-level `provider_call_provenance={version: 1}` と、各routeの `provider_call` を持つ。dry-runでは `provider_call=null` のままであり、実測証拠へ昇格しない。
- measured routeでは `provider` / `provider_kind` / `model_id` / `transport` / `requested_at` / `trace_id` / `fallback_to_none` / `execution_path` を既存audit metadataからそのまま保存する。
- analyzerはprovider/model/kindの整合、非空のtransport/requested_at/trace_id、`fallback_to_none=false`、`execution_path=primary` を要求する。fallback・non-primary・trace欠落・provenance契約欠落はfail-closedする。
- prompt fingerprintとcall provenanceは役割を分ける。前者は「何を送ったか」、後者は「どのcallとして実行されたか」のローカル監査証跡であり、token値は引き続きprovider-reported `input_tokens` だけを正本とする。

branch-only GitHub Actions run `33952594490` で、R23〜R35関連を含む **68 test**、ruff、`git diff --check` が成功した。provider-call provenanceの保存、primary pathの正常系、fallback/non-primary、trace欠落、旧provenance契約欠落、dry-run非昇格を回帰へ固定し、一時patch/workflowも同run内で自己削除した。

**非主張**: `provider_call` はproviderが署名したreceiptではなく、KJ Atlas側の既存 `LLMCallMetadata` に基づく監査情報である。外部providerは呼んでおらず、実token値・context余裕・cost・latency・品質、A2/B/C採択、production cap/routeは未変更である。本Issueは引き続きIn Progressであり、未完了ACは完了扱いにしない。

## R36 — R35後のprovider実測readiness同期

R35でfuture provider measurementへcall provenance検証を追加したため、Issue前半の受入条件注記・検証計画・実使用確認・次の判断順序を現行実装へ同期した。今後のnamed provider/model実測reportは、provider-reported usageだけでなく、canonical prompt SHA-256とprimary call provenance（transport / requested_at / trace_id、fallbackなし、primary execution path）までanalyzerで整合した場合だけR21の方式比較入力にする。

本同期はdocs-onlyであり、外部provider実測・A2/B/C採択・production cap/route変更を行わず、未完了ACを完了へ変更しない。

## R37 — DeepSeek usage を exact chat input message content に結び付ける

R33のcanonical prompt SHA-256とR35のcall provenanceにより、provider-reported usageを「現在のuser prompt」と「primary callの監査情報」へ結び付けられるようになった。一方、DeepSeek/OpenAI-compatible chat transportが入力tokenとして実際に送るのはuser prompt単体ではなく、task由来のsystem messageとuser messageの組である。system message templateが将来変わった場合、R33だけでは古いusageを現在と同じtransport inputの観測として誤利用する余地が残るため、R37でこの境界を閉じた。

- `kj_atlas_api.llm.provider._openai_chat_messages()` を、DeepSeek/OpenAI-compatible transportが送るsystem+user message contentの単一source of truthとして切り出し、実transport自身が同helperを使う。
- DeepSeek実測responseでは、measurement reportに `provider_input={kind: openai-chat-messages-v1, sha256: ...}` を各routeへ保存する。SHA-256対象は同helperが返すmessage配列のcanonical JSON / UTF-8である。
- top-level `provider_input_provenance` はversion / kind / algorithm / encodingを固定する。dry-runではrouteの `provider_input=null` のままであり、provider実測証拠へ昇格しない。
- analyzerは `actual_provider_kind=deepseek` のrouteがある場合だけprovider-input provenance契約と、現在のcanonical requestから再生成したsystem+user message SHA-256との一致を要求する。missing / kind mismatch / stale hashはfail-closedする。
- generic providerのmeasurementにはDeepSeek固有のmessage契約を強制しない。R35までのprovider/model/prompt/call-provenance検証をそのまま維持する。
- 同一user promptでもtaskが異なればsystem messageが変わり、message fingerprintも変わることを回帰で固定した。

branch-only GitHub Actions run `33953053815` で、R23〜R37関連を含む **73 test**、ruff、`git diff --check` が成功した。一時patch/helper/workflowも同run内で自己削除した。

**非主張**: provider-input fingerprintはprovider署名receiptではなくKJ Atlas側の入力同一性証跡であり、tokenizerやtoken数を推定するものではない。外部providerは呼んでおらず、実token値・context余裕・cost・latency・品質、A2/B/C採択、production cap/routeは未変更である。本Issueは引き続きIn Progressであり、未完了ACは完了扱いにしない。

## R38 — R37後のprovider-input readiness同期

R37でDeepSeekのprovider-reported input token観測を、canonical user promptだけでなく実transportが送るsystem+user message contentへも結び付けたため、Issue前半の回帰証拠・検証計画・外部実測条件・次の判断順序を現行実装へ同期した。named DeepSeek実測reportは、R33のuser-prompt fingerprint、R35のprimary call provenance、R37のprovider-input fingerprintがすべて現在のbuilder/transportと一致した場合だけR21の方式比較入力へ進める。

本同期はdocs-onlyであり、外部provider実測・A2/B/C採択・production cap/route変更を行わず、未完了ACを完了へ変更しない。

## R39 — provider input usage と production output reserve を分離してcontext hard-fitを判定する

R20〜R38でnamed provider/modelの入力token実測・prompt/transport provenance・report整合性検証を準備したが、measurement requestは外部費用を抑えるため `max_tokens=1` で送る一方、現行productionの対象routeは `LLMRequest` の既定 `max_tokens=2000` を使う。この2つを混同すると、provider-reported input usageが得られても「productionでcontext windowへ収まるか」を1-token出力予約で過小評価する余地があった。

R39では `analyze_ai_route_provider_measurement.py` にcontext budget summaryを追加し、token推定や方式採択をせず次を固定した。

- measurement harnessのrequestは引き続き `max_tokens=1` であることをcanonical requestから検証し、driftしたreport/builderは比較準備に通さない。
- 現行productionのoutput reserveは数値を別途複製せず、`LLMRequest` の既定 `max_tokens` から取得する。現時点では **2000 tokens** である。
- routeごとの最低context必要量を `provider-reported input_tokens + current production output reserve` として算出する。input token値は従来どおりprovider自身のusageだけを使い、bytes/chars/hashから補わない。
- CLIの `--context-window-tokens` にoperatorがnamed model/providerの文書化されたcontext-window値を明示した場合だけ、残余tokenとhard fit (`minimum <= context window`) を算出する。context window自体をrepo側で推測・固定しない。
- layout Cの31 requestはaggregate input tokenを1つのcontext windowとみなさず、**最大単一requestのinput usage + output reserve** をhard-fit対象にする。aggregateはcost/throughput比較用の別観測として維持する。
- R21の「十分な余裕」はhard-fitと別の設計判断として残し、analyzerは安全余裕率・閾値を新たに発明しない (`sufficient_headroom_policy=null`)。hard-fitしただけでA2/B/Cを採択しない。

branch-only GitHub Actions run `33954945719` でR23〜R39関連を含む **77 test**、ruff、`git diff --check` が成功した。一時patch/workflowは同run内で自己削除した。

**非主張**: R39は実modelのcontext-window値を決めず、外部providerを呼ばず、実token値・cost・latency・品質・安全余裕policyを取得/決定していない。A2/B/C採択、production cap/route、SafeMode・防PII・structured-text-only・proposal-only境界は未変更であり、未完了ACは完了扱いにしない。

## R40 — R39後のcontext hard-fit手順をIssue前半へ同期

R39でprovider-reported input usageと現行production output reserveを分離し、operatorがnamed model/providerの文書化されたcontext-window値を明示した場合だけhard-fitを計算できるようになったため、Issue前半の受入条件注記・実使用確認・次の判断順序を現行実装へ同期した。

実測後の順序は、(1) R32/R33/R35/R37のmeasurement provenance/identity検証、(2) R39の `input + production output reserve` hard-fit確認、(3) R21の「十分な余裕」と方式比較、の三段階とする。layout Cではaggregate usageをcontext windowへ誤適用せず最大単一requestを使う。hard-fitと安全余裕policyは同一視しない。

本同期はdocs-onlyであり、外部provider実測、context-window値の推測、A2/B/C採択、production cap/route変更、未完了ACの完了化を行わない。

## R41 — context-window hard-fitへ資料source provenanceを必須化

R39でoperatorがnamed model/providerのcontext-window値を明示した場合だけhard-fitを算出できるようにしたが、その数値が**どのprovider/model資料を根拠にしたか**は結果へ残っておらず、後から値だけが独り歩きする余地があった。R41ではcontext-window値と資料sourceを対にして扱い、hard-fit判断の来歴を監査可能にした。

- `analyze_ai_route_provider_measurement.py` の `analyze(...)` / context budget summaryへ `context_window_source` を追加した。
- `context_window_tokens` を渡す場合、空でない `context_window_source` を必須とする。sourceなしの数値入力はfail-closedし、逆にtoken値なしでsourceだけを渡す組合せも拒否する。
- CLIに `--context-window-source` を追加し、provider/modelの公式ドキュメントURL、文書ID、版・日付を識別できる参照等を記録できるようにした。
- 出力ではsource文字列を正規化して保持し、`context_window_source_kind=operator-supplied-document-reference` と明示する。R39のhard-fit算術、production output reserve、layout Cのmax-single semantics、`sufficient_headroom_policy=null` は変更しない。
- sourceは**監査用provenance**であり、analyzer自身がURL先を取得して真正性・最新性・記載内容を自動検証するものではない。このため、sourceを添えただけでcontext-window値がproviderにより保証されたとは主張しない。
- CLIの引数不整合はstructured `context-window-argument-error:*` として非decision-readyで返す。measurement report自体のroute/task/provider/model/usage/prompt/provider-input/call provenance検証は従来どおりである。

branch-only GitHub Actions run `33955296602` でR23〜R41関連を含む **80 test**、ruff、`git diff --check` が成功した。一時patch/workflowは同run内で自己削除した。

**非主張**: R41は実modelのcontext-window値を取得・固定せず、外部providerを呼ばず、資料sourceの真正性を自動検証せず、安全余裕policy・A2/B/C採択・production cap/routeを決定しない。未完了ACとSafeMode・防PII・structured-text-only・proposal-only境界は未変更である。

## R42 — R41のcontext-window source手順をIssue前半へ同期

R41でcontext-window hard-fitへ資料source provenanceが必須になったため、Issue前半の回帰注記・実使用確認・次の判断順序を現行analyzerへ同期した。context-windowを使う場合は `--context-window-tokens` と `--context-window-source` を対で渡し、source欠落時はhard-fitを推測しない。sourceは監査用参照でありanalyzerが真正性・最新性を自動保証しない点も明記した。

併せてR40同期時に生じていた「次の判断順序」の番号崩れ（3の重複と5の欠落）を修正し、1〜6の連番へ戻した。これは表示上の整合修正であり判断内容の追加・削除ではない。

本同期はdocs-onlyであり、外部provider実測、実context-window値の取得、source資料の自動検証、安全余裕policy、A2/B/C採択、production cap/route変更、未完了ACの完了化を行わない。


## R43 — production output reserve前提の回帰固定

R39のcontext hard-fit計算は、provider実測時の `max_tokens=1` とは別に、現行production routeが確保するoutput token予算を加算する。R39時点では4つの測定対象production taskが `LLMRequest` の共通既定値を使うことを前提にしていたが、その前提と実call siteの間に恒久回帰はなかった。将来1 routeだけが `max_tokens` を個別指定すると、provider-reported input token自体は正しくてもhard-fitだけが黙って古いreserveで計算される余地があった。

R43ではproduction本体を測定都合で変更せず、`tests/test_ai_route_production_output_budget_contract.py` を追加して次を固定した。

- analyzerの `CORE_ROUTE_TASKS` が表すunique production taskは `suggest_card_groups` / `re_layout` / `generate_narrative` / `check_narrative` の4つであり、実production functionと一致する。
- 各production functionの実sourceを `inspect` + ASTで確認し、対象 `LLMRequest` がちょうど1件、期待task idを持つことを確認する。
- 現状4routeはいずれもroute固有 `max_tokens` overrideを持たず、`LLMRequest` 共通既定reserveを使う。analyzerの `CURRENT_PRODUCTION_OUTPUT_RESERVE_TOKENS` も同じ既定値から導出される。
- 将来どれかのrouteが個別 `max_tokens` を導入した場合、この回帰を単に緩めず、先にanalyzerをroute別reserveへ更新する必要がある。

GitHub Actions run `33963862577` でR23〜R43関連 **81 test**、ruff、`git diff --check` が成功した。one-shot workflowはrun内で自己削除済みである。

**非主張**: R43でも外部providerは呼んでいない。実input token、実model context-window、十分な安全余裕、費用、latency、品質は未測定であり、A2/B/Cの採択、production cap、route挙動は変更していない。


## R44 — current DeepSeek measurement model / context source の更新

2026-09-05時点のDeepSeek公式API資料を再確認したところ、R20作成時の例に残っていた `deepseek-chat` は現行のnamed measurement modelとして使えないことが判明した。公式Change Logは2026-04-24に `deepseek-chat` / `deepseek-reasoner` を2026-07-24で廃止すると告知しており、現在のQuick Startは `deepseek-v4-flash` / `deepseek-v4-pro` / `deepseek-v4-flash-vision-exp` を現行model IDとして列挙している。したがって、本IssueのDeepSeek実測例は **`deepseek-v4-flash`** へ更新する。productionの `KJ_ATLAS_DEEPSEEK_MODEL` 既定値そのものは本Issueで黙って変更せず、thinking/non-thinking semanticsを含む別issue `AI-DEEPSEEK-V4-MIGRATION-01` へ切り出す。

公式Models & PricingはV4 Flashのcontext lengthを `1M` と記載する。一方、DeepSeek自身のagent integration例ではPi/Oh My Piが `contextWindow: 1000000`、Codex/Crushが `1048576` を記載しており、公開資料だけから「APIの唯一の厳密な整数上限」を断定しない。R41のhard-fitを実行する場合は、過大評価を避けるため、公式Pi integrationが明示する小さい方の **1,000,000 token** を保守的な運用値として使用できる。これはAPIの厳密最大値が1,000,000であるという主張ではない。

保存済みprovider measurement reportにhard-fitを付加する例:

```bash
.venv/bin/python scripts/analyze_ai_route_provider_measurement.py measurement.json \
  --context-window-tokens 1000000 \
  --context-window-source https://api-docs.deepseek.com/quick_start/agent_integrations/pi_mono/
```

資料provenance（2026-09-05確認）:

- current model IDs / versions / `1M` context: `https://api-docs.deepseek.com/quick_start/pricing`
- legacy alias retirement: `https://api-docs.deepseek.com/updates`（2026-04-24 entry）
- conservative integer context value `1000000`: `https://api-docs.deepseek.com/quick_start/agent_integrations/pi_mono/`
- comparison evidence `1048576`: `https://api-docs.deepseek.com/quick_start/agent_integrations/codex/` / `crush/`

**非主張**: R44は公開公式資料の確認と実測手順の更新だけであり、DeepSeek APIを呼んでいない。provider-reported input tokenはまだ未取得で、A2/B/Cの採択、production cap、production model既定、thinking mode、SafeMode等の境界も変更していない。

## R47 — V4移行後の実測判断順序を前半要約へ同期

R42で後半の「次の判断順序」を1〜6へ同期していた一方、Issue前半の「実token計測後の判断基準」にはR21時点の旧い `1, 2, 4, 5, 5` の要約が残り、R32/R33/R35/R37のmeasurement identity/provenance、R39/R41のcontext hard-fit/source provenance、方式決定後にcoverage-loss metadataを設計する順序が反映されていなかった。R47では前半要約を後半の現行6段階へ揃え、判断手順の二重化によるdriftを解消した。

併せてR45/R46で `AI-DEEPSEEK-V4-MIGRATION-01` が完了し、productionのDeepSeek既定は `deepseek-v4-flash`、thinking mode既定は旧non-thinking挙動を保つ `disabled` へ移行済みであることを現在地として確認した。ただし、これはnamed provider/modelのprovider-reported input usageを取得したことを意味しない。R47でも外部providerは呼ばず、最初の2つの未完了AC、A2/B/C採択、production cap/route、十分な余裕policyは変更しない。


## R48 — DeepSeek V4 thinking modeをprovider測定provenanceへ固定

R45でDeepSeek V4へ移行した結果、`thinking.type=disabled|enabled` がprovider requestの明示的なgeneration modeになった。一方、R37までのDeepSeek measurement identityはsystem+user message contentを固定していたが、このmodeは保存reportに残らず、production既定の`disabled`で測った結果か、環境overrideで`enabled`になった結果かを後から区別できなかった。R48ではtoken推定とは切り離した**request-mode provenance**としてこの穴だけを閉じた。

- `LLMCallMetadata` にprovider固有の `thinking_mode` を追加し、DeepSeek/OpenAI-compatible transportが実際に送った `thinking.type` をresponse metadataへ残す。generic audit fieldsのR35契約は変更しない。
- measurement reportは `provider_generation_provenance={version: 1, deepseek_field: "thinking.type"}`、`expected_deepseek_thinking_mode`、各DeepSeek routeの `provider_generation.thinking_mode` を保存する。
- DeepSeekを実行する場合はexpected modeを必須とし、現在の `settings.deepseek_thinking_mode` と一致しなければ**provider call前**に停止する。これにより誤った環境overrideのまま6件/7件/37件/38件を送信しない。
- analyzerはDeepSeek reportについてgeneration provenance契約・expected mode・routeごとの実mode一致をfail-closedで検証する。modeはrequest provenanceであり、bytes/chars/hashと同様にtoken数へ換算しない。provider-reported `input_tokens` だけをtoken観測の正本とする。
- production既定 `deepseek-v4-flash` + `thinking.type=disabled`、A2/B/C候補、shared IR cap、SafeMode、防PII、structured-text-only、proposal-only境界は変更しない。

GitHub Actions run `33997380006` でDeepSeek transport metadata、measurement/analyzer provenance、R23〜R43近接回帰、compile check、R48対象のfatal/static lint、`git diff --check` を検証した。一時patch/workflowは同run内で自己削除する。

**非主張**: R48でも外部DeepSeek APIは呼んでおらず、provider-reported input tokenは未取得である。thinking modeを記録したこと自体はinput token差・品質差・費用差を意味せず、A2/B/C採択・十分な余裕policy・production cap/routeも変更しない。


## R49 — R48 thinking-mode実測手順をIssue前半へ同期

R48でDeepSeek V4の `thinking.type` をmeasurement reportのrequest-mode provenanceへ追加した一方、Issue前半の「実使用/外部依存確認」と「次の判断順序」はR37時点のprovider-input fingerprintまでしか記載しておらず、外部実測時に新必須引数を落とす余地が残っていた。R49ではproduction既定と比較するDeepSeek V4実測を `KJ_ATLAS_DEEPSEEK_THINKING_MODE=disabled` + `--deepseek-thinking-mode disabled` と明示し、保存report/analyzerのgeneration-mode検証まで前半手順へ同期した。

併せて、checked済みroute-required regressionの証拠行をR43の81 testからR48 run `33997380006` の129 testへ更新した。未完了ACは変更せず、外部provider実測、provider-reported token取得、A2/B/C採択、production cap/route、十分な余裕policyは変更しない。


## R50 — 外部実測runbookと事前整備完了境界を固定

R20〜R49の実測契約を、`dry-run -> core 6外部実測 -> analyzer -> 必要時だけA2/C追加` のrunbookへまとめた。GitHub Actions run `34001497304` では実際のCLIを用いてDeepSeek V4 production既定相当のdry-runが6 route・network-freeで成立することと、`--execute` だけでは `KJ_ATLAS_TOKEN_MEASUREMENT_OPT_IN=1` 不在によりprovider解決前にexit 2で停止することを確認した。

本runで外部providerは呼んでいない。R50を外部実測前scaffoldingの完了境界とし、具体的な欠陥が新たに見つからない限りprovenanceや候補実装を追加しない。未完了AC、provider-reported token、A2/B/C採択、production cap/route、十分な余裕policyは変更しない。
