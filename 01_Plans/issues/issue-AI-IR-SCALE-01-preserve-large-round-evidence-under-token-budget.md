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
| `generate-narrative` | `readingOrder` の完全な順序、および叙述の論理骨格となるcard-to-cardの `causal` / `negate`。明示されたisland-to-island edgeも従来文脈として維持する | `readingOrder` とisland edgeはDocumentからpromptへ。card relationはIRからpromptへ入り、`causal` / `negate` はreading-order上の位置へ写像する | **必要な論理骨格は解消済み。** `AI-IR-NARRATIVE-SPINE-01` / PR #2887で、正規化可能なcard-to-card `causal` / `negate` の両端をrequired cardとして保護し、300カードの末尾関係までIRと最終promptへ残す回帰を固定した。required cardだけで上限を超える場合はfail-closedする。`MAX_RELATIONS` を超える規模やtoken予算は本Issueに残る |
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
  --model deepseek-chat
```

実token数を測る場合は、既存の安全な方法で `KJ_ATLAS_LLM_PROVIDER`、providerの認証情報、必要ならmodel設定を事前に構成する。認証情報をコマンドラインや成果物へ直接書かない。そのうえで次を実行する。

```bash
KJ_ATLAS_TOKEN_MEASUREMENT_OPT_IN=1 \
.venv/bin/python scripts/measure_ai_route_provider_tokens.py \
  --provider deepseek \
  --model deepseek-chat \
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
- `generate-narrative` では、`causal` / `negate` の両端カードやreading order上の論理骨格を先に確保する案が考えられる。ただし、文書全体の叙述骨格を守ろうとするとrequired集合が文書規模へ近づき、A2との差が小さくなる可能性がある。
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

`suggest-layout` はさらに難しい。batchごとに局所座標を出しても、それぞれの座標系が独立していれば全体配置にはならない。局所配置の後に、島・代表点・跨り関係を使って全体座標へ整合させる第2段階が必要になる。したがってlayoutの方式Cは、単純な分割処理ではなく階層配置として設計する。

### 実token計測後の判断基準

R20の測定値が得られたら、ルートごとに次の順で判断する。

1. 300カードを全量投影した場合でも、対象model/providerの入力上限に対して十分な余裕があるなら、まずA2を比較対象の基準にする。単純で追跡しやすく、意味を落とす規則も増やさずに済むためである。
2. 全量投影が入力予算へ近すぎる、または余裕が不足する場合は、BまたはCをルートごとに選ぶ。一つの方式を全AIルートへ強制しない。
3. `generate-narrative` はBで必要な論理骨格が十分小さく保てるかを先に検証し、文書規模へ膨らむならCを比較する。
4. `suggest-layout` は全体相対配置という性質上、Bだけで解くのが難しい。A2が安全でなければ、階層配置を伴うCを主な比較対象にする。
5. 方式を選んだ後に、その方式で実際に起こり得るcoverage lossの単位を定める。汎用的なloss metadataを先に作って設計を固定しない。

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

方式の比較条件はR21を正本とする。要約すると、A1（`MAX_CARDS` だけの引上げ）は候補から外し、A2（カード上限と文字数予算を整合して広げる）・B（ルート別意味保存）・C（分割・階層処理）を、R20の実token測定後にルートごとに比較する。

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
- [x] 300カード規模のroute-required regressionをテストスイートへ固定する。GitHub Actionsは現在無効のため、CIで実行成功済みとは扱わない。
- [ ] 上限値の変更を行う場合、named model/providerの実測根拠を記録する。

## 検証計画

- 自動確認:
  - `scripts/measure_llm_input_ir_scale.py`
  - `scripts/measure_ai_route_prompt_coverage.py`
  - `scripts/measure_ai_route_required_meaning.py`
  - `scripts/measure_ai_route_provider_tokens.py`
  - `scripts/measure_ai_ir_budget_pressure.py`
  - `tests/test_llm_input_ir_scale.py`
  - `tests/test_ai_route_prompt_coverage.py`
  - `tests/test_ai_route_required_meaning_scale.py`
  - `tests/test_ai_route_provider_token_measurement.py`
  - `tests/test_ai_ir_budget_pressure.py`
  - IR単体テスト、移行対象route統合テスト、backend全体回帰。
- 実使用/外部依存確認:
  - 明示的に選んだnamed model/providerで1回以上の代表規模requestを行い、provider-reported usageを保存する。
  - 外部LLMを呼ばない通常の回帰では、exact token countを捏造せず構造・prompt coverageだけを決定論的に検査する。

## 次の判断順序

1. **named provider/modelの実入力tokenを測る。** R20のハーネスを使い、`suggest-layout` 相当の最重量promptと、座標を使わない `generate-narrative` を同じmodel/providerで比較する。
2. その測定値をR21の判断基準へ当てはめ、A2/B/Cを**ルートごと**に比較する。A1（`MAX_CARDS` だけを300へ上げる案）は比較対象から外す。
3. `generate-narrative` の `causal` / `negate` 両端保護は `AI-IR-NARRATIVE-SPINE-01` で完了した。今後はrequired relationが `MAX_RELATIONS` を超える規模やtoken予算まで含めて、A2/B/Cのどれが必要かを実測後に判断する。
4. `suggest-layout` はA2が十分な余裕を持って使えない場合、局所配置と全体整合を分けた階層配置としてCを具体化する。
5. coverage-loss metadataは方式決定後に、その方式で本当に検証すべき欠落単位へ合わせて追加する。先に汎用メタデータだけを増やさない。

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
