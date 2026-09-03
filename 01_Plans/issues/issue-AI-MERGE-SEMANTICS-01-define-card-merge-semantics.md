# Issue: AI-MERGE-SEMANTICS-01 `suggest-merges` の意味境界と受入条件を定める

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Architecture / AI Integration
- Status: In Progress
- Source Issue: `AI-IR-STAGE5-SCOPE-01` Stage 5
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/backend/src/kj_atlas_api/models.py`, `03_Implement/backend/src/kj_atlas_api/llm_input_ir.py`, `03_Implement/frontend/src/domain/representative_merge.ts`, `03_Implement/frontend/src/domain/merge_suggestion_decisions.ts`, `03_Implement/frontend/src/domain/merge_traceability.ts`, `03_Implement/frontend/src/App.tsx`, `00_Prompt/domain.md`, `00_Prompt/kj_technique.md`, `00_Prompt/qualitative_card_quality_requirements.md`, `02_Architecture/api.md`
- Related ADR/Spec: `01_Plans/adr/ADR-0069-llm-input-ir-as-the-actual-ai-input-path.md`, `AI-IR-PROJECTION-01`, `AI-IR-STAGE5-SCOPE-01`
- Expected verification level: integration

## 課題

`POST /ai/suggest-merges` は現在、文書内の全カードについて `id` と `text` を並べ、「similar cards」のmerge候補を最大10件返すようLLMへ依頼している。応答は `groupId`、2件以上の `cardIds`、`mergedTextDraft`、任意の `rationale` から成る。

しかし、現行契約には「何をどのように統合するのか」がない。候補カードの `holdState`、`claimType`、島所属、直接の `negate` 関係、矛盾を表す `evidenceLinks`、既存のmerge系譜もAI入力や決定論的な後段検査に使っていない。そのため、語彙が近いだけの少数意見、反対意見、観察と仮説、保留中のカードまで一つへ丸める余地がある。

一方、kj-atlasではカード数そのものの維持を目的化しない。近接した類似カードは山浦氏の04ステップで整理でき、複数カードの核を保って一つの意味単位へ統合する必要がある場合は川喜田氏の核融合法も利用できる。重要なのは、どちらの方法でも異なる時点・主体・感触・条件・残差を安易に圧縮せず、元カードと来歴へ戻れることである。

したがって `suggest-merges` を単なる「重複除去」にも、逆に無制約な「意味融合」にもしない。**04ステップと核融合法を使い分けるproposal-onlyの統合支援**として意味境界を固定し、そのうえでAI実入力をIRへ移行する。

## 統合の二つの方法

### 1. 04ステップによる近接カードの整理

意味・主体・時点・条件・感触が十分に近く、各カードを別々に保持することによる増分が小さい場合に使う。

- 表現が違うだけで、中心的な訴えが同じ。
- 一方にしかない重要な条件や残差を統合後本文へ保持できる。
- 統合によって観察と推論、事実と仮説などの認識上の位置づけを混同しない。

単なる語彙類似や同一テーマは十分条件ではない。

### 2. 核融合法による意味核の統合

カード同士が完全な重複ではないが、複数カードを一緒に見たときに、それぞれを生かした共通の意味核を新しい一つのカードとして表現できる場合に使う。

- 各カードの訴えをいったん保ったまま、全体から意味核を立てる。
- 統合本文を元カードへ戻し、「これは自分が言っていたことか」を確認する。
- 統合でこぼれる条件・感触・異論・例外は残差として保持する。
- 元カードを物理削除せず、統合先・source・canonical/representation系譜から追跡可能にする。

核融合法は「違う内容をきれいな一文へ丸める」ための手段ではない。核を立てても元カードへ戻せない場合、または残差が大きい場合は統合しない。

### 方法の選択

04ステップを常に優先する、核融合法を常に優先する、と固定しない。候補カードの関係を見て、**意味保存性・残差の少なさ・元カードへの戻しやすさ**が高い方法を選ぶ。

現行 `MergeSuggestion` には方法を表すフィールドがないため、実装時には後方互換を保てる形で `mergeMethod`（例: `near_duplicate` / `kernel_fusion`）と、必要なら `residuals` を追加する。名称は実装前に既存API語彙へ合わせて確定する。

## KJ法のグループ編成との境界

カードを同じ島へ束ねることと、一枚の統合カードへまとめることは別である。

- `suggest-card-groups` / Island: 元カードを複数枚のまま近くに置き、束として読む。
- `suggest-merges`: 元カードを根拠として、新しい代表的な一枚へ統合できる場合だけ提案する。
- Placard: 島全体の訴えを代弁する上位文であり、個々のカードの統合とは別である。

一匹狼のカード、他と違う感触を持つカード、対立を担うカードを「島に入りにくい」「似た語がある」という理由でmergeしない。

`MergeSuggestion.groupId` はKJ法のGroup/Clusterを意味しない。あくまで一つのmerge提案を識別するproposal-local IDである。

## 統合を抑止する条件

次の条件は、LLMへの注意書きだけでなく実装側の決定論的なguardで保護する。

### 1. 保留状態

候補のいずれかに `holdState` (`held` / `pending` / `shelved`) がある場合、その組をmerge候補として返さない。

保留は「まだ畳まない」という人間の判断であり、AIの統合判断より優先する。

### 2. 明示的な対立・矛盾

候補カード間に次が存在する場合、その組をmerge候補として返さない。

- card-to-card の `negate` relation
- `type=contradicts` の `evidenceLink`

`contradictionState` が `confirmed` / `held` なら当然に保護する。`unconfirmed` でも、統合して対立の痕跡を消すより別カードとして残す側へ倒す。

### 3. 認識上の位置づけ

両方に `claimType` が設定され、その値が異なる場合はmerge候補として返さない。

観察・引用、解釈、仮説、問いなどの位置づけが異なる情報は、本文が似ていても同じ情報単位ではない。片方が未設定の場合は、それだけで同一とみなさない。

### 4. 既存merge系譜

`mergedIntoCardId`、`canonicalId`、`repOf` など既存の統合系譜を確認し、既に別カードへ統合済みのカードを独立した新規候補として再mergeしない。必要ならcanonicalな代表へ解決して候補集合を作る。

### 5. 同一応答内の競合提案

一枚のカードを同じ応答内の複数merge候補へ重複して含めない。

A+BとA+Cを同時に適用可能な候補として返すと、適用順序で意味と系譜が変わる。現行契約では重複をfail-closedにする。将来、相互排他的な代替案を表現する契約を追加した場合だけ別扱いとする。

## hard vetoにはしない文脈

### 島所属

異なる島にあることだけをmerge禁止にはしない。同じ観察が重複入力され、別々の島に置かれている場合もある。

ただし島の違いは、利用者が別の意味文脈で扱っている可能性を示す。IR移行時には島所属を文脈として渡し、語彙類似だけで跨島統合しないようにする。

### `equivalence` / `related`

`equivalence` は04ステップ型の統合を支持する材料になり得るが、それだけで統合を決定しない。`related` はさらに弱い補助情報に留める。

### 出典・sources

異なる出典から同じ内容が独立に得られている場合、その差自体に意味がある。出典差を機械的な禁止条件にも許可条件にもせず、統合後もsourceを失わない。

## 残差と来歴の不変条件

統合候補を採用しても、元カードを不可逆に消さない。

- source card IDを保持する。
- `sources` を失わない。
- `repOf` / `canonicalId` / `mergedIntoCardId` など、既存の系譜表現と整合させる。
- 統合本文へ入らなかった意味を残差として記録できるようにする。
- 統合結果から元カードへ戻して比較できる。
- AIが出典・残差・系譜を創作しない。

既存の適用経路がこの不変条件を満たしていない場合、AI提案側だけを完成扱いせず、適用経路の改修を同Issueの完了条件に含める。

## AI入力契約

本経路は `DocumentV1` 由来の構造が統合可否の判断に直接必要な **Document-backed structured task** である。ADR-0069 D5=Aに従い、generic Document IRまたはroute固有投影をprovider実入力の正本とする。

少なくとも次をprovider手前へ届ける。

- 候補対象カードの `id` / IR正規化後本文
- `holdState`
- `claimType`
- 人間が確定させた島所属
- card relation、特に `negate` / `equivalence`
- `evidenceLinks` と `contradictionState`
- 統合済みカードを再候補化しないために必要な系譜情報
- 方法選択と戻し検査に必要なsource/残差情報

全Documentを同じ重要度でpromptへ列挙することを目的にしない。大規模文書では、まず安全に比較できる候補集合を作り、その集合について必要意味をroute-requiredとして保護する。

IR上限により統合判断に必要な本文・relation・evidence・系譜が欠ける場合は、不完全な入力で統合を提案せずfail-closedにする。

SafeModeは既存のroute側検査を一次防御として残し、IRまたはroute固有入力ビルダー側の検査を第二層として維持する。

## promptと応答検査

promptには少なくとも次を要求する。

- similarity alone and same topic are not sufficient
- choose a near-duplicate/04-step-like consolidation only when material distinctions can be preserved
- choose kernel fusion only when a shared meaning kernel can be stated without erasing residual differences
- perform a return check against every source card before proposing
- leave held, contradictory, minority, lone, or materially different cards separate
- proposal only; never delete or overwrite source cards

LLM応答は信用せず、後段で決定論的に検査する。

- 未知ID、重複ID、2件未満、上限超過を拒否する。
- holdを含む候補を拒否する。
- `negate` / contradiction evidenceを含む候補を拒否する。
- 異なる既知 `claimType` を含む候補を拒否する。
- 既存merge系譜上の無効候補を拒否する。
- 同じカードが複数候補に出た応答をfail-closedにする。
- `mergedTextDraft` は提案本文に過ぎず、元カードを削除・上書きしない。

04ステップと核融合法のどちらが意味上適切かは、LLMの提案に含められるが、人間の採否判断を置き換えない。

## 実装方針

1. route-required meaningと統合禁止条件をintegration regressionで先に固定する。
2. `suggest-merges` 専用のIR投影または入力コンテキストビルダーを追加する。
3. promptを「similar cards」だけの契約から、04ステップ／核融合法を使い分ける意味保存契約へ更新する。
4. LLM応答後の決定論的merge guardを追加する。
5. 必要なら `MergeSuggestion` に統合方法と残差を後方互換な任意フィールドとして追加する。
6. `LLMRequest.inputs` とprovider promptが同じ正規化済み入力を使い、Document生本文から同じ意味を迂回送出しないことを回帰で固定する。
7. 実際のmerge適用経路が元カード・sources・残差・canonical/representation系譜を保持することを確認する。
8. API文書と `AI-IR-STAGE5-SCOPE-01` を実装結果へ同期する。
9. 内容・構造を確定した後、意味を変えず自然な日本語として全文を読み直す。

## 実装結果（2026-09-03）

AIへの入力と応答検査について、意味境界を実装へ反映した。

- `holdState` が付いたカードと `mergedIntoCardId` 済みカードは候補集合から除外し、候補が2枚未満ならproviderを呼ばず空提案を返す。
- 候補カードの本文は共有LLM入力IRで正規化し、`claimType`、全島所属、`canonicalId` / `repOf`、出典の同一性をroute固有の構造化入力として重ねる。
- `sources` の生値はproviderへ送らず、文書内で同じ出典を共有しているかだけを比較できる不透明なローカル参照へ変換する。
- 候補カード本文、候補間relation、候補間evidenceがIR上限によって欠ける場合は、不完全な入力で統合を提案せずfail-closedにする。
- SafeModeはroute側検査を一次防御、IR生成時の検査を第二層として維持し、PIIを含む候補本文もprovider呼出前に拒否する。
- provider promptは `LLMRequest.inputs` と同じroute固有入力から候補本文・relation・evidence・補助文脈を描画し、Document側の生本文を同じ意味の迂回入力として使わない。
- 応答後は既存の決定論的guardにより、hold、既merge、`negate`、`contradicts` evidence、異なる既知 `claimType`、同一カードを複数候補へ含める競合提案を拒否する。

一方、**提案を人間が採用した後の実merge適用経路**について、元カード・`sources`・残差・canonical/representation系譜が十分に保持されることは、この変更ではまだ完了根拠を得ていない。`mergeMethod` / `residuals` をresponse契約へ追加するかどうかも、適用経路の監査後に判断する。

## 適用経路監査（2026-09-03）

提案生成後のUIと既存の代表カード作成処理を追跡した結果、次を確認した。

- `MergeSuggestionsPanel` の `accept` / `partial` / `reject` / `defer` は、現状では `appendMergeSuggestionDecision()` と監査イベントを記録するところまでであり、`accept` や `partial` を選んでも代表カードの生成やsourceカードの系譜更新は行わない。
- 実際の代表カード作成には別経路の `createRepresentativeMerge()` が使われている。従来実装は元カード自体を残していたが、`repOf` / `mergedIntoCardId` 系と `sources` / `canonicalId` 系が分かれており、適用結果だけから全source系譜を一貫してたどるには弱かった。
- 従来の `rewireMembershipAndEdges` は、sourceカードの島所属を代表カードへ置き換え、既存edgeの端点も代表カードへ直接書き換えていた。このため、表示上は扱いやすくなる一方、統合前の島文脈や「どのsourceカードに付いていたrelationか」という原形を失う余地があった。

PR #2847 では、まず実merge関数そのものを意味保存側へ寄せる。

- sourceカードは物理削除せず、`mergedIntoCardId` と `canonicalId` を同じ代表カードへ向ける。
- 代表カードには直接の `repOf` に加え、過去の代表カードが持つ系譜を含めた `sources` を保持する。
- sourceカードの本文・`meta`・KA情報・既存系譜はそのまま残し、統合結果から戻して比較できるようにする。
- 指定sourceの一部欠落、hold、既に別代表へ統合済みのsource、候補間の `negate` / `contradicts`、異なる既知 `claimType` は適用時にもfail-closedにする。
- 同一の明示的 `claimType` が全sourceにある場合だけ代表カードへ引き継ぎ、未分類が混ざる場合は推測しない。
- rewireを選んだ場合も、元の島所属とedgeは削除・上書きせず、代表カードのmembershipと外部relationの投影を追加する。候補内部relationは代表カードのself-loopへ変換しない。

これにより、**実mergeのデータ変換自体**については元カード・source・主要なmerge/canonical系譜・元relationへ戻れる土台を作る。ただし、Issueはまだ完了させない。残る作業は次のとおり。

1. `accept` を実merge適用へ接続する際のトランザクション順序を決め、decision/auditの代表カードsnapshotが実際の代表カードを指すようにする。
2. `partial` は現契約に「採用するsourceの部分集合」がないため、意味を決めずに自動適用しない。必要なら `selectedCardIds` のUI/契約を明示してから適用する。
3. 残差を独立フィールドとして保持する必要があるか、元sourceカードを残すことを残差の一次記録とするかを、実適用UIの戻し比較と合わせて決める。AIが残差を創作する契約にはしない。
4. decision → merge apply → traceability → 保存／再読込までを一つのintegration regressionとして固定する。

## 受入条件

- [x] `suggest-merges` とKJ法のグループ編成・表札生成の違いを定義する。
- [x] 近接した類似カードには04ステップ、複数カードの意味核を保つ統合には核融合法を利用可能とし、方法を固定しない。
- [x] 元カードID・出典・残差・系譜・戻し検査を統合の不変条件として定義する。
- [x] hold、明示的対立・矛盾、異なる既知claimType、既存merge系譜、同一応答内の候補競合を保護対象として定義する。
- [x] 島所属・equivalence・出典差は単純なhard veto/許可ではなく、意味文脈として扱うと定義する。
- [x] ADR-0069 D5=Aに基づき、本経路をDocument-backed structured taskとして分類する。
- [x] 上記のroute-required meaningをintegration regressionとして固定する。
- [x] `suggest-merges` のprovider実入力をgeneric Document IRまたはroute固有投影へ移す。
- [x] promptを意味保存型の統合契約へ更新する。
- [x] LLM応答後の決定論的merge guardを実装する。
- [x] 同一カードが複数候補へ出た場合のfail-closedをテストで固定する。
- [ ] 元カード・sources・残差・merge/canonical系譜が採用後も追跡可能であることを、AI提案の採用から実適用・保存／再読込まで含むintegration regressionで確認する。
- [x] SafeMode二層、PII最小化、structured-text-only、IR上限のfail-closedを確認する。
- [x] `02_Architecture/api.md` と `AI-IR-STAGE5-SCOPE-01` を実装結果へ同期する。
- [ ] 最終成果物を自然な日本語として全文ドラフトし直す。

## 完了境界

このIssueは、単に `suggest-merges` をIR経由へ変えた時点では完了しない。

**04ステップと核融合法をカードの関係に応じて使い分けながら、元カードの意味・出典・残差・系譜を失わず、保留・対立・少数意見を統合から守り、provider実入力がその契約を迂回しないことをintegration regressionで固定するところまで**を完了条件とする。
