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

`AI-IR-PROJECTION-01` は、`detect-contradiction`、`suggest-card-groups`、`generate-narrative`、`suggest-layout` の4経路をLLM投入IRへ移行した後、Stage 5として「残りのエンドポイント」を残した。2026-08-31時点の棚卸しでは、prompt構築関数は11件、そのうちIR経由は4件、未移行は7件だった。2026-09-03に `suggest-island-summary` をStage 5の第1経路として移行し、現在は**5経路がIR経由、未移行は6経路**である。

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
| `suggest-island-summary` | `DocumentV1`、対象島、利用者の違和感 | 対象島の全直接メンバー、表札への異議、島の論理的位置、矛盾・根拠の有無 | **IR移行済み（2026-09-03）**。対象島に必要な意味をroute固有投影で保護し、欠落時はfail-closedにした |
| `propose-opposing-viewpoint` | `DocumentV1`、対象カード | 対象カード、根拠・矛盾、人間が既に判断した矛盾状態、関連する反対所見 | **IR移行候補。優先度高**。現行promptはevidence linkの種別だけを渡し、`contradictionState` を渡していない |
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

現在のpromptは対象島の**直接メンバーカード**だけを本文として渡し、`critiqueTags` と利用者の `critiqueText` を戻し検査へ使う。また、明示されたisland-to-island edgeをDocumentから直接渡す。

一方でpromptは「evidenceが弱い、疎である、矛盾している場合はwarningsを出す」と要求しているが、現在はcard-to-card relationや `evidenceLinks` を入力していない。つまり、警告を求める契約に対し、判断材料の一部が届いていない。

Stage 5では次を必要意味として検証する。

- 対象島の全直接メンバーカード。
- 対象島の確定構造（親島、表札、review state）。
- 対象島のメンバー間および外部との `causal` / `negate` など、表札の意味へ関わる関係。
- 対象メンバーに接続する根拠・矛盾リンク。
- `critiqueTags` / `critiqueText` は現行IRに無いため、task-local入力として維持する。

対象島のメンバーはroute固有の必須集合として扱える可能性が高い。ただし1島だけで `MAX_CARDS` を超える場合に黙って一部を落とすことは表札の戻し検査と両立しない。必要ならfail-closedまたは島内分割を別途検討する。

#### 実装結果（2026-09-03）

Stage 5の第1経路として `suggest-island-summary` をIRへ移行した。request / response、既存の表札検査、`critiqueTags` / `critiqueText`、明示的なisland-to-island edge、proposal-only wrapperは変更していない。追加したのは、AIへ渡す意味の保全層である。

- 対象島の全直接メンバーを必須カードとして保護する。
- 直接メンバーに接続するカード間relationとevidenceの両端も文脈用カードとして保護する。
- 外部の隣接カードは関係・根拠を理解するための文脈に限定し、`groundingIds` の許可範囲は対象島の直接メンバーから広げない。
- 親島、表札カード、review state、card relation、`contradictionState` をIR由来の構造としてpromptへ渡す。
- 必要なrelation / evidenceが共有IRの上限処理で欠けた場合は、存在しないものとして扱わず `required_relation_missing` / `required_evidence_missing` でfail-closedにする。必要カード集合そのものが上限を超える場合も、共有IRの `required_card_budget_exceeded` をそのまま利用する。
- SafeModeは従来のroute側検査を一次防御として残し、IR側検査を第二層として維持する。

専用回帰に加え、既存の表札prompt回帰とAI経路被覆テストを同時に実行し、`suggest_island_summary` をIR移行済みタスクへ移した状態で成功した。

### 3. `propose-opposing-viewpoint`

この経路は「対象カードに対する反対視点またはevidence gapを、文書内の根拠・矛盾構造から提案する」と明記している。現在も全カード本文と `evidenceLinks` は渡しているが、evidence linkの `contradictionState` はpromptに含めず、card relationも使っていない。

人間が既に `confirmed` / `held` とした矛盾を、新しい発見のように扱うことは避ける必要がある。ただし `detect-contradiction` と違い、この経路では既存の矛盾自体が「反対視点の根拠」として意味を持つ場合がある。したがって、既決矛盾を完全に除外するのではなく、**人間が判断済みであることを状態付きで渡し、新規発見と区別する**のが自然である。

対象カードを `required_card_ids` で保護することは妥当だが、反対所見候補として全300カードを同じ優先度で保持するかは別問題である。対象カードに接続するevidence/relationと、文書全体からの反対候補探索を分けて設計する。

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

1. `suggest-island-summary` — 2026-09-03に移行。対象島の必要意味をroute固有投影で保護し、grounding境界を維持した。

### 次にIR移行を具体化してよい

2. `propose-opposing-viewpoint`
3. `check-narrative` — ただしscale方式決定後

`propose-opposing-viewpoint` は対象カードという自然なfocusを持ち、`required_card_ids` とroute固有投影を利用しやすい。`check-narrative` は文書全体を扱うため、`AI-IR-SCALE-01` の結果を待つ。

### 受入条件を先に決める

4. `suggest-merges`

KJ上の「統合」の意味を決めず、IRにある情報を便利そうだから足すことをしない。

### ADR-0069の適用範囲を確認してから扱う

5. `summarize-island-relation`
6. `refine-card-text`
7. `suggest-document-title`

これらをgeneric document IRへ無理に寄せず、明示的な例外またはtask-local structured inputを許すかをADR-0069側で確認する。特にno-doc 2経路へ疑似Documentを作る実装は採らない。

## 推奨する実装順序

1. **完了: `suggest-island-summary` の必要意味をintegration regressionで固定し、同じ変更でIRへ配線した。** 対象島の全直接メンバー、島構造、関連するrelation/evidence、既存の戻し検査を同時に保持している。
2. **次: `propose-opposing-viewpoint` を状態付きevidenceへ移す。** 対象カードを保護し、`contradictionState` を新規発見と既決判断の区別に使う。
3. `summarize-island-relation` / no-doc 2経路について、ADR-0069の適用範囲を短い追補で明確にする。
4. `suggest-merges` の利用仕事と受入条件を決める。
5. `check-narrative` は `AI-IR-SCALE-01` のA2/B/C判断後に移行方式を決める。

この順序は「実装しやすい順」ではなく、現在のpromptと仕事のあいだに意味上の欠落が明確な順を優先している。

## 受入条件

- [x] Stage 5に残る7経路を現行コードから再棚卸しする。
- [x] 各経路について、Document-backed / 限定grounding / no-docの違いを記録する。
- [x] IRに存在する全情報を全経路へ渡すことを目的にしないと明記する。
- [x] `suggest-island-summary` で「矛盾・根拠を警告せよ」というpromptに対し、その材料が十分に届いていないことを記録する。
- [x] `propose-opposing-viewpoint` で `contradictionState` が現在provider手前へ届いていないことを記録する。
- [x] `summarize-island-relation` のgrounding allowlistをgeneric IR化で広げてはならないことを記録する。
- [x] no-doc経路へ疑似Documentや架空IDを作る案を採らない。
- [x] `suggest-island-summary` のroute-required meaningをintegration regressionとして固定し、IRへ配線する。— 対象島の直接メンバーと隣接するrelation/evidenceの意味を保護し、必要意味が投影上限で欠ける場合はfail-closedにした。
- [ ] `propose-opposing-viewpoint` のroute-required meaningをintegration regressionとして固定する。
- [ ] ADR-0069にDocument IRの適用範囲とtask-local structured inputの扱いを追補する。
- [ ] `suggest-merges` のmerge意味論と受入条件を別Issueまたは本Issueの追記で固定する。
- [ ] `check-narrative` のscale投影方式を `AI-IR-SCALE-01` の結果と整合させる。

## 完了境界

本Issueは、Stage 5を「未移行7件」という件数管理から、仕事ごとの意味要件と入力契約に基づく実装計画へ置き換えるところまでを扱う。

実際のIR配線は各routeのintegration regressionと同じPRで行う。ADR-0069の適用範囲を変える場合は、本Issueだけで決定済みとせずADR追補を正本とする。
