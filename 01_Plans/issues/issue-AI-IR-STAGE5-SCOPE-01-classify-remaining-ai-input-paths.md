# Issue: AI-IR-STAGE5-SCOPE-01 Stage 5の残存AI経路を意味要件で分類する

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Architecture / Investigation
- Status: In Progress
- Source Issue: `AI-IR-PROJECTION-01` Stage 5
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/backend/src/kj_atlas_api/routes/ai_relations.py`, `03_Implement/backend/src/kj_atlas_api/models_ai.py`, `02_Architecture/llm_input_ir_spec.md`, `01_Plans/adr/ADR-0069-llm-input-ir-as-the-actual-ai-input-path.md`
- Related ADR/Spec: `AI-IR-PROJECTION-01`, `AI-IR-SCALE-01`, `01_Plans/adr/ADR-0069-llm-input-ir-as-the-actual-ai-input-path.md`
- Expected verification level: integration

## 課題

`AI-IR-PROJECTION-01` は、`detect-contradiction`、`suggest-card-groups`、`generate-narrative`、`suggest-layout` の4経路をLLM投入IRへ移行した後、Stage 5として「残りのエンドポイント」を残した。2026-08-31時点の棚卸しでは、prompt構築関数は11件、そのうちIR経由は4件、未移行は7件だった。2026-09-03に `suggest-island-summary` をStage 5の第1経路、`propose-opposing-viewpoint` を第2経路として移行し、現在は**6経路がIR経由、未移行は5経路**である。

ただし、この7件を「同じ方法でIRへ移せばよい7件」と扱うのは適切ではない。実装を再確認すると、次の3種類が混在している。

1. `DocumentV1` を受け取り、現在のpromptが文書構造を十分に使えていない経路。
2. `DocumentV1` は受け取るが、すでに人間または呼出側が限定したgrounding集合を明示的に受け取る経路。
3. `DocumentV1` 自体を受け取らず、単一カードや要約済みの文字列だけを扱う経路。

現行IRは `DocumentV1` 由来のカード・関係・島・根拠リンクを安全かつ決定論的に投影するための契約である。Documentを持たない処理へ、架空のカードIDや疑似文書を作ってまで同じIRを通すと、「IRを使っている」という形式だけを満たし、入力契約の意味を弱めるおそれがある。

したがってStage 5では、実装件数を減らすことを目的にせず、各経路の仕事から必要な意味を逆算し、**IRへ移行する経路、受入条件を先に定める経路、明示的な例外または別の構造化入力契約として扱う候補**を分ける。

## Stage 5で棚卸しした7経路

| 経路 | 現在の入力 | 仕事上必要な意味 | 現時点の分類 |
| --- | --- | --- | --- |
| `check-narrative` | `DocumentV1`、narrative本文、reading order | narrativeとA型図解の往復照合、カード・島、reading order、叙述の根拠となる論理関係 | **IR移行候補**。ただし文書全体を扱うため `AI-IR-SCALE-01` と強く結合 |
| `suggest-island-summary` | `DocumentV1`、対象島、利用者の違和感 | 対象島の全直接メンバー、表札への異議、島の論理的位置、矛盾・根拠の有無 | **IR移行済み（2026-09-03、merge後監査完了）**。対象島に必要な意味をroute固有投影で保護し、直接メンバー本文もIRからprovider promptへ描画する。必要意味の欠落時はfail-closed |
| `propose-opposing-viewpoint` | `DocumentV1`、対象カード | 対象カード、根拠・矛盾、人間が既に判断した矛盾状態、関連する反対所見 | **IR移行済み（2026-09-03）**。対象カードと直接接続するrelation/evidenceを必須意味として保護し、人間の `contradictionState` を新規AI発見と区別する。対象カード本文もIRから最終promptへ描画する |
| `suggest-merges` | `DocumentV1`、全カード | 類似カード候補。既存の島・hold・対立関係を「mergeを避ける制約」として扱うべきかは未決 | **受入条件を先に定める**。IRに情報があるという理由だけでmerge判断へ使わない |
| `summarize-island-relation` | `DocumentV1` に加え、許可済みgrounding card/edgeとその本文 | 明示された2島、relation type、許可されたgrounding集合 | **別契約またはhybrid候補**。現在の限定済みgrounding集合をgeneric IRで広げない |
| `refine-card-text` | 単一カード本文、任意context。Documentなし | 元の意味を保った言い換え、レビュー状態 | **IR例外候補**。現行IRへ入れるには存在しないカードIDや疑似Documentを作る必要がある |
| `suggest-document-title` | 島タイトル列、カード本文サンプル、現在タイトル。Documentなし | 人間側で選ばれた概要情報から複数の同格タイトル候補を作る | **IR例外候補**。現在のtask-localな要約入力をDocument IRへ偽装しない |

## 経路ごとの分析

### 1. `check-narrative`

現在のpromptはnarrative本文、reading order、島とそのメンバー、全カード本文を渡し、A/B照合を両方向で行うよう要求している。一方、card-to-cardの `causal` / `negate`、`evidenceLinks`、人間が確定した島階層は直接使っていない。

この仕事では「文章に書かれた主張が図解に接地しているか」「図解にある重要な島を文章が落としていないか」を見るため、単なるカード本文一覧よりも論理骨格が意味を持つ。`generate-narrative` と対になる経路として、少なくとも `causal` / `negate` と確定島構造を評価対象に含める価値がある。

ただし、文書全体のA/B照合であるため、300カード規模では `generate-narrative` と同じscale問題を持つ。`AI-IR-SCALE-01` のA2/B/C判断より先にproduction移行しない。

### 2. `suggest-island-summary`

移行前のpromptは対象島の**直接メンバーカード**だけを本文として渡し、`critiqueTags` と利用者の `critiqueText` を戻し検査へ使っていた。また、明示されたisland-to-island edgeをDocumentから直接渡していた。

一方、promptは「evidenceが弱い、疎である、矛盾している場合はwarningsを出す」と要求していたが、card-to-card relationや `evidenceLinks` を入力していなかった。つまり、警告を求める契約に対し、判断材料の一部が届いていなかった。

Stage 5では次を必要意味として検証する。

- 対象島の全直接メンバーカード。
- 対象島の確定構造（親島、表札、review state）。
- 対象島のメンバー間および外部との `causal` / `negate` など、表札の意味へ関わる関係。
- 対象メンバーに接続する根拠・矛盾リンク。
- `critiqueTags` / `critiqueText` は現行IRに無いため、task-local入力として維持する。

対象島のメンバーはroute固有の必須集合として扱う。1島だけで共有IRの上限を超える場合も、意味を欠いた状態で表札を生成せずfail-closedにする。

#### 実装結果（2026-09-03）

Stage 5の第1経路として `suggest-island-summary` をIRへ配線した。request / response、既存の表札検査、`critiqueTags` / `critiqueText`、明示的なisland-to-island edge、proposal-only wrapperは変更していない。追加したのは、AIへ渡す意味の保全層である。

- 対象島の全直接メンバーと、それらへ直接つながるcard relation / evidenceの両端だけへsourceを縮約する。無関係な文書カードはIRにもpromptにも送らない。
- 外部の隣接カードは関係・根拠を理解するための文脈に限定し、`groundingIds` の許可範囲は対象島の直接メンバーから広げない。
- 親島は親子関係を保持するための構造だけを残し、親島のカード集合を表札候補の入力へ広げない。
- 親島、表札カード、review state、card relation、`contradictionState` をIR由来の構造としてpromptへ渡す。
- providerへ送る最終promptの直接メンバー本文もIR正規化後の同一カード本文から描画し、Document側の生本文を同じ入力箇所へ迂回させない。
- 必要カード集合そのものが上限を超える場合は共有IRの `required_card_budget_exceeded` を利用する。カード本文が `MAX_TEXT_CHARS` により240文字へ短縮される場合は `required_text_truncated`、必要relation / evidenceが欠ける場合は `required_relation_missing` / `required_evidence_missing` としてfail-closedにする。
- SafeModeは従来のroute側検査を一次防御として残し、IR側検査を第二層として維持する。
- helper単体とroute配線の回帰テスト、およびAI経路被覆テストを追加・更新した。**merge時点では当該headに対するpytest実行成功を確認できていなかったため、テスト成功は当該mergeの完了根拠には含めない。**

### 3. `propose-opposing-viewpoint`

この経路は「対象カードに対する反対視点またはevidence gapを、文書内の根拠・矛盾構造から提案する」と明記している。移行前のpromptには全カード本文と `evidenceLinks` を渡していたが、evidence linkの `contradictionState` は含まれず、card relationも使われていなかった。

人間が既に `confirmed` / `held` とした矛盾を、新しい発見のように扱うことは避ける必要がある。ただし `detect-contradiction` と違い、この経路では既存の矛盾自体が「反対視点の根拠」として意味を持つ場合がある。したがって、既決矛盾を完全に除外するのではなく、**人間が判断済みであることを状態付きで渡し、新規発見と区別する**のが自然である。

対象カードを `required_card_ids` で保護することは妥当だが、反対所見候補として全300カードを同じ優先度で保持するかは別問題である。対象カードに接続するevidence/relationと、文書全体からの反対候補探索を分けて設計する。

#### 実装結果（2026-09-03）

Stage 5の第2経路として `propose-opposing-viewpoint` をIRへ移行した。proposal-onlyの応答契約、UI側の人間判断、`Target card:` の行形式は変更していない。

- 対象カードを必須カードとして保護し、対象カードへ直接接続するcard relation / evidenceの両端も必須文脈として保護する。
- `confirmed` / `held` を含む `contradictionState` は、人間が既に行った判断としてprovider手前へ渡し、新しいAI発見として言い直さないようprompt上でも区別する。
- 直接接続していないカードは、IRに残った範囲だけを反例探索の補助文脈として扱う。対象周辺の必須意味と文書全体からの探索を同じ重要度にしない。
- providerへ送る `Target card:` の本文もIR正規化後の対象カード本文から描画し、Document側の生本文を中心入力へ迂回させない。merge前監査で同型の迂回を検出し、integration regressionを追加して解消した。
- 必須カード本文が共有IRの文字数上限で短縮される場合は `required_text_truncated`、必須relation / evidenceが上限処理で欠ける場合は `required_relation_missing` / `required_evidence_missing`、必須カード集合が上限を超える場合は `required_card_budget_exceeded` でprovider呼出前にfail-closedにする。
- SafeModeはroute側の一次検査とIR側の二次検査をともに維持し、座標は要求しない。

専用IR回帰、既存 `test_ai_oppose.py`、AI経路被覆テストで、production routeがpromptと `LLMRequest.inputs` の双方へ同じIR本文・構造を渡すことまで固定した。

### 4. `suggest-merges`

現在の契約は全カードの `id/text` から「似ているカードのmerge候補」を最大10件提案し、適用や削除は行わないというものだけである。

ここに既存島、hold、`negate` などを渡せば、例えば「似た語を使っていても意図的に対立として残した2枚」をmergeしにくくできる可能性がある。しかし、現行受入条件はその判断を要求していない。KJ法上の統合と単純な重複除去の境界も明示されていないため、先にIRを足すと仕様を実装側から作ることになる。

この経路は、次を先に決める。

- mergeとは重複除去なのか、核融合法・04ステップに近い意味統合まで含むのか。
- hold中カードを候補から外すのか。
- `negate` / 矛盾関係をmerge禁止条件とするのか、単なる注意情報とするのか。
- 同じ島・異なる島という所属をmerge判断へ使うのか。

受入条件が定まるまでIR移行を実装しない。

### 5. `summarize-island-relation`

この経路は `DocumentV1` を受け取るものの、AIへ自由に文書全体を見せる契約ではない。呼出側が `groundingCardIds` / `groundingEdgeIds` を明示し、それらに対応する `cardTexts` / `edgeTexts` だけをpromptへ渡す。応答側もgrounding IDが許可集合の部分集合であることを検査する。

この限定は安全境界であり、generic IRへ移すために文書全体をpromptへ広げてはならない。

候補は次の2つに限る。

- **現行のtask-local structured inputを明示的な例外として維持する。**
- **hybridにする。** IRはSafeMode・関係語彙・参照整合の検査に使うが、最終promptは現在の許可済みgrounding集合だけを描画する。

後者を採る場合も、IRで生成されるrelation idと、入力の永続edge idの対応が必要である。現在のIR relation idは `type:from:to` から生成されるため、`groundingEdgeIds` をそのまま置き換えられない。ここを曖昧にして実装しない。

### 6. `refine-card-text`

この経路は単一の `cardText` と任意の `context` だけを受け取り、カードIDもDocumentも持たない。レビュー状態はrequestの `textReviewed` でfail-closedに確認している。

現行IRの `cards[*].id` は空文字を禁止する。IRを使うためだけに架空IDを作ると、追跡可能性のためのIDに虚偽の識別子を持ち込むことになる。requestへ新しいID必須項目を追加するのも、言い換え処理のためだけなら契約を不必要に重くする。

したがって本経路は、ADR-0069が対象とする「Document由来の構造をAIへ届ける経路」とは性質が異なる。**明示的な例外とするか、document IRとは別のtask-local structured input契約を定義する候補**として扱う。

### 7. `suggest-document-title`

この経路もDocumentを受け取らず、最大50件の島タイトルとカード本文サンプルを受け取る。現在のpromptでは島タイトルを最大20件、カード本文を最大30件使う。

入力はすでに「文書全体」ではなく、呼出側が選んだ概要情報である。これをgeneric IRへ載せるには、島タイトルや匿名の本文断片を架空のカード・島として再構成する必要があり、元の契約より意味が不明瞭になる。

この経路も `refine-card-text` と同じく、**明示的な例外またはtask-local structured input候補**とする。もし「タイトル提案でも全Documentの構造を見せたい」という製品要件が生じるなら、先にrequest契約そのものをDocument-backedへ変更するIssueを起票する。

## Stage 5の暫定分類

### IR移行済み

1. `suggest-island-summary` — 2026-09-03にIR移行を完了。対象島の必要意味をroute固有投影で保護し、grounding境界を維持した。merge後監査で、provider promptの直接メンバー本文もIR正規化後本文から描画するよう是正した。mainでも再現する既知4件以外に新しいbackend回帰が無いことを確認し、`AI-IR-STAGE5-SUMMARY-PROMPT-01` は同監査で解消した。

2. `propose-opposing-viewpoint` — 2026-09-03にIR移行を完了。対象カードと直接接続するrelation/evidenceを必須意味として保護し、既決 `contradictionState` と対象カード本文をIR実入力として保持した。

### IR移行候補だがscale方式決定を待つ

3. `check-narrative`

`check-narrative` は文書全体を扱うため、`AI-IR-SCALE-01` の結果を待つ。

### 受入条件を先に決める

4. `suggest-merges`

KJ上の「統合」の意味を決めず、IRにある情報を便利そうだから足すことをしない。

### task-local structured inputとして境界確定

5. `summarize-island-relation` — caller-limited grounding task。`groundingCardIds` / `groundingEdgeIds` のallowlistを実効入力の上限とし、generic Document IRを併用しても最終promptを広げない。
6. `refine-card-text` — no-document task。疑似Documentや架空IDを作らず、単一本文＋任意contextのtask-local structured inputを正式契約とする。
7. `suggest-document-title` — no-document task。呼出側が選んだ島タイトル・本文サンプルのtask-local structured inputを正式契約とし、generic Document IRへ偽装しない。

ADR-0069 D5=Aの追補により、この3経路はgeneric Document IRの「未移行」ではなく、別の構造化入力契約を使うことが設計上の正解と確定した。SafeModeやレビュー状態などの共通境界保護は引き続き必要である。

## 推奨する実装順序

1. **完了: `suggest-island-summary` の必要意味をintegration regressionで固定し、AI実入力をIRへ揃えた。** merge後監査で専用回帰と関連回帰を実行し、二層SafeMode、provider promptと `LLMRequest.inputs` の直接メンバー本文一致、Document生本文の迂回送出防止を確認した。backend全体ではmainでも同じ4件が失敗することを別環境で再現し、その4件を除く全テストが成功することを確認した。
2. **完了: `propose-opposing-viewpoint` を状態付きevidenceへ移した。** 対象カードと直接接続する意味を保護し、`contradictionState` を新規発見と既決判断の区別に使う。対象カード本文もIRからprovider promptへ描画する。
3. **完了: `summarize-island-relation` / no-doc 2経路の適用境界をADR-0069 D5=Aで確定した。** generic Document IRを目的化せず、限定groundingはallowlistを維持し、no-doc経路はtask-local structured inputを正式契約とする。
4. **次: `suggest-merges` の利用仕事と受入条件を決める。**
5. `check-narrative` は `AI-IR-SCALE-01` のA2/B/C判断後に移行方式を決める。

この順序は「実装しやすい順」ではなく、現在のpromptと仕事のあいだに意味上の欠落が明確な順を優先している。

## 受入条件

- [x] Stage 5に残る7経路を現行コードから再棚卸しする。
- [x] 各経路について、Document-backed / 限定grounding / no-docの違いを記録する。
- [x] IRに存在する全情報を全経路へ渡すことを目的にしないと明記する。
- [x] `suggest-island-summary` で「矛盾・根拠を警告せよ」というpromptに対し、その材料が十分に届いていなかったことを記録する。
- [x] `propose-opposing-viewpoint` で `contradictionState` が現在provider手前へ届いていないことを記録する。
- [x] `summarize-island-relation` のgrounding allowlistをgeneric IR化で広げてはならないことを記録する。
- [x] no-doc経路へ疑似Documentや架空IDを作る案を採らない。
- [x] `suggest-island-summary` のroute-required meaningをintegration regressionとしてコードへ固定し、IRへ配線する。— 対象島の直接メンバーと隣接するrelation/evidenceだけへsourceを縮約し、必要意味が投影上限で欠ける場合はfail-closedにした。
- [x] `suggest-island-summary` の追加・既存回帰を実行し、結果を確認する。— 専用IR、既存prompt、経路被覆、関連SafeModeを実行して成功を確認した。backend全体はmainでも再現する既知4件を基準差分として切り分け、その4件を除く全回帰に新規失敗が無いことを確認した。`AI-IR-STAGE5-SUMMARY-PROMPT-01` の直接メンバー本文IR描画回帰も同時に確認した。
- [x] `propose-opposing-viewpoint` のroute-required meaningをintegration regressionとして固定し、IRへ配線する。— 対象カードと直接接続するrelation/evidenceを保護し、人間の `contradictionState` を状態付きで保持した。対象カード本文もIRから最終promptへ描画し、生本文の迂回を回帰で禁止した。
- [x] ADR-0069にDocument IRの適用範囲とtask-local structured inputの扱いを追補する。— D5=Aとして、Document-backed / caller-limited grounding / no-documentの3分類と実入力境界を確定した。
- [ ] `suggest-merges` のmerge意味論と受入条件を別Issueまたは本Issueの追記で固定する。
- [ ] `check-narrative` のscale投影方式を `AI-IR-SCALE-01` の結果と整合させる。

## 完了境界

本Issueは、Stage 5を「未移行7件」という件数管理から、仕事ごとの意味要件と入力契約に基づく実装計画へ置き換えるところまでを扱う。

実際のIR配線は各routeのintegration regressionと同じPRで行う。ADR-0069の適用範囲を変える場合は、本Issueだけで決定済みとせずADR追補を正本とする。
