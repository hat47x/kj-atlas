# Issue: AI-MERGE-SEMANTICS-01 `suggest-merges` の意味境界と受入条件を定める

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Architecture / AI Integration
- Status: Done
- Source Issue: `AI-IR-STAGE5-SCOPE-01` Stage 5
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/backend/src/kj_atlas_api/merge_suggestion_ir.py`, `03_Implement/frontend/src/domain/representative_merge.ts`, `03_Implement/frontend/src/domain/merge_suggestion_decisions.ts`, `03_Implement/frontend/src/domain/merge_suggestion_apply.ts`, `03_Implement/frontend/src/domain/merge_traceability.ts`, `03_Implement/frontend/src/ui/MergeSuggestionsPanel.tsx`, `02_Architecture/api.md`
- Related ADR/Spec: `ADR-0069`, `AI-IR-PROJECTION-01`, `AI-IR-STAGE5-SCOPE-01`, `AI-MERGE-APPLY-01`, `AI-MERGE-PARTIAL-01`
- Verification level: backend integration / frontend unit / UI / E2E

## 課題

従来の `POST /ai/suggest-merges` は「similar cards」を探すことが中心で、何をどこまで同じ意味として統合してよいかが十分に定義されていなかった。

そのままでは、語彙が近いというだけで、少数意見、反対意見、観察と仮説、保留中のカード、既に別の代表カードへ統合されたカードまで一つへ丸める余地がある。

一方、kj-atlasではカード数を減らすこと自体を目的にしないが、意味が十分に近いカードを整理することまで禁止しない。近接した類似カードには山浦氏の04ステップを使え、複数カードを一緒に見たときに共通の意味核を立てられる場合には川喜田氏の核融合法も使える。

重要なのは、どちらの方法でも**元カードへ戻れること、異なる意味を消さないこと、人間の保留・矛盾・認識上の位置づけをAIより優先すること**である。

このため `suggest-merges` を、単なる重複削除でも無制約な意味融合でもなく、**意味保存型・proposal-onlyの統合支援**として定義する。

## 統合の二つの考え方

### 04ステップによる近接カードの整理

意味、主体、時点、条件、感触が十分に近く、別々に保持することによる増分が小さい場合に使う。

- 表現は異なっても中心的な訴えが同じである。
- 一方にしかない重要な条件を代表本文へ残せる。
- 観察と推論、事実と仮説など、認識上の位置づけを混同しない。

語彙が似ていることや、同じテーマに属することだけでは統合しない。

### 核融合法による意味核の統合

完全な重複ではない複数カードを一緒に見たとき、それぞれを生かした共通の意味核を新しい一枚として表現できる場合に使う。

- 各カードの訴えを消さずに意味核を立てる。
- 代表本文を元カードへ戻して読み、「元のカードが言っていたことを失っていないか」を確認する。
- 統合本文へ入り切らない条件、感触、異論、例外は、削除されず残る元カードから再確認できる。

核融合法は、異なるカードを整った一文へ丸めるための手段ではない。元カードへ戻したときに意味保存を確認できなければ統合しない。

### 方法を固定しない

04ステップを常に先に使う、核融合法を常に先に使う、と固定しない。カードの関係を見て、意味保存性、残差の少なさ、元カードへの戻しやすさが高い方法を選ぶ。

現在は方式によって実適用のデータ変換が分岐しないため、`mergeMethod` を機械可読の必須フィールドにはしない。方式名をAIに自己申告させるだけでは正本として弱い。将来、方式ごとにUI、戻し検査、適用規則が実際に変わる場合に別Issueで契約化する。

## グループ編成・表札との違い

- Island / `suggest-card-groups`: 元カードを複数枚のまま近くに置き、束として読む。
- `suggest-merges`: 元カードを残したまま、新しい代表カードを一枚作れる場合だけ提案する。
- Placard: 島全体の訴えを代弁する上位文であり、個々のカードの統合とは別である。

一匹狼、少数意見、他と違う感触を持つカード、対立を担うカードを、「島に入りにくい」「似た語がある」という理由で統合しない。

`MergeSuggestion.groupId` はKJ法のGroup/Clusterではなく、一つのmerge提案を識別するIDである。

## AIより優先する保護条件

次はprompt上の注意だけではなく、決定論的なguardで保護する。

### 保留

候補に `holdState` (`held` / `pending` / `shelved`) がある場合は統合候補にしない。保留は「まだ畳まない」という人間の判断である。

### 明示的な対立・矛盾

候補間に次がある場合は統合しない。

- card-to-card の `negate` relation
- `type=contradicts` の `evidenceLink`

`contradictionState` が未確定でも、対立の痕跡を統合で消すより別カードとして残す側へ倒す。

### 認識上の位置づけ

複数カードに既知の `claimType` があり、その値が異なる場合は統合しない。本文が似ていても、観察、引用、解釈、仮説、問いなどの位置づけが異なれば別の情報単位である。

### 既存のmerge系譜

`mergedIntoCardId` / `canonicalId` によって既に別の代表へ統合されたsourceを、新しい独立候補として再利用しない。

### 同一応答内の競合

同じカードを複数のmerge候補へ同時に含めない。A+BとA+Cを同時に適用可能な候補として返すと、適用順で意味と系譜が変わるためfail-closedにする。

## hard vetoにしない文脈

### 島所属

異なる島にあることだけでは統合禁止にしない。同じ観察が重複入力され、別の島へ置かれている場合もある。ただし、島の違いは異なる意味文脈を示す可能性があるため、AI入力には保持する。

### `equivalence` / `related`

`equivalence` は近接カード整理を支持する材料になり得るが、それだけで統合を決めない。`related` はさらに弱い補助情報として扱う。

### 外部元記録

外部元記録は `Card.meta.source` の責務であり、`Card.sources` とは分ける。外部元記録の違いは、それだけで統合を許可・禁止する条件にはしない。AI入力へ不要な生の外部元記録を露出しない。

## 来歴と残差の不変条件

統合を採用しても元カードを不可逆に消さない。

- sourceカード自体を残す。
- 代表カードは `repOf` / `sources` でmerge元カードIDを保持する。
- sourceカードは `mergedIntoCardId` / `canonicalId` から代表カードをたどれる。
- sourceカードの本文、`meta`、既存の島所属、relationを失わない。
- 必要な代表カード側の島所属・外部relationは、元構造の置換ではなく投影として追加する。
- AIが元記録、残差、系譜を創作しない。

`Card.sources` は外部出典ではなく、merge元カードIDの系譜である。外部元記録は `Card.meta.source` に保持する。

独立した自由記述 `residuals` は追加しない。統合本文へ入らなかった意味の一次記録は、削除されず残るsourceカードそのものとする。AI生成の残差文を別の正本として持つと、元カードとの差分が二重管理になるためである。

## AI入力契約

本経路は `DocumentV1` 由来の構造が統合可否へ直接関係するDocument-backed taskである。ADR-0069 D5=Aに従い、共有LLM入力IRとroute固有文脈をprovider実入力の正本とする。

provider手前では少なくとも次を扱う。

- 候補カードのIDとIR正規化後本文
- `holdState`
- `claimType`
- 島所属
- card relation、特に `negate` / `equivalence`
- `evidenceLinks` と `contradictionState`
- `canonicalId` / `mergedIntoCardId` / `repOf` / `sources` のmerge系譜

全Documentを同じ重要度でpromptへ複製することを目的にしない。必要な候補本文、relation、evidence、系譜がIR上限で欠ける場合は、不完全な入力のまま提案せずfail-closedにする。

SafeModeはroute側検査を一次防御、IR生成時の検査を第二層として維持する。provider promptと `LLMRequest.inputs` は同じ正規化済み入力から描画し、Document生本文を同じ意味の迂回入力として使わない。

## 提案・判断・適用を分ける

AI提案を直接Document変更へつなげない。

1. AIはmerge候補をproposalとして出す。
2. 人間が `accept` / `partial` / `reject` / `defer` を記録する。
3. `accept` または有効な `partial` の判断後、利用者が別の明示的な「適用」操作を行う。
4. 適用直前のDocumentを再検査してから代表カードを作る。
5. Document変更後も自動保存せず、既存の明示保存操作を使う。

判断後にholdや矛盾が追加された場合は、古いAI提案より現在のDocumentを優先して停止する。

## `partial` の意味

`partial` は、提案されたsourceカードの**真部分集合**だけを人間が明示的に採用する判断とする。

- 2枚以上、かつ候補全件未満を選択する。
- 全件を採用する場合は `accept` を使う。
- 1枚以下ではmergeを成立させない。
- 選択されなかったカードは実適用で変更しない。
- 新しい `partial` では `selectedCardIds` に人間が選んだ集合を保存する。
- 旧来の曖昧な `partial` は推測で実適用しない。

詳細は `AI-MERGE-PARTIAL-01` を正本とする。

## 実装結果（2026-09-03）

### 提案生成とAI入力

- `holdState` 付きカード、既merge/canonicalization済みカードを候補化しない。
- 共有LLM入力IRとmerge専用構造化文脈をproviderへ渡す。
- `claimType`、島所属、relation、evidence、人間の矛盾判断、merge系譜を統合判断へ使う。
- 必要意味がIR上限で欠ける場合はprovider呼出前に停止する。
- promptでは04ステップ型の近接整理と核融合法型の意味核統合を区別し、全sourceへ戻して読むことを要求する。
- provider応答後にもhold、対立・矛盾、`claimType` 差、既merge、候補競合を決定論的に拒否する。

### 実mergeとtraceability

- sourceカードは物理削除しない。
- 代表カードは直接sourceに加え、過去の代表カードが持つ系譜も `sources` に保持する。
- source側の `mergedIntoCardId` / `canonicalId` と代表側の `repOf` / `sources` を同じ代表カードへ接続する。
- rewire時も元の島所属・edgeを削除せず、代表カードへの投影を追加する。
- 同一の既知 `claimType` が全sourceにある場合だけ代表へ引き継ぎ、不明値が混じる場合は推測しない。

### 人間判断から実適用まで

- 記録済み `accept` だけを対象にするdomain transactionを追加した。
- UIでは `accept` と「採用した統合を適用」を別操作として維持した。
- `decision → apply → Save → reload` のE2Eで、代表カードとsource系譜が保存後も復元できることを確認した。
- Accept後にDocument変更処理が候補previewを消して適用へ進めない残差もE2Eで検出し、判断記録・明示適用の二経路に限って候補を保持するよう修正した。

### 部分採用

- `partial` は人間が選んだ2枚以上・全件未満の `selectedCardIds` を必須化した。
- 判断ログと監査イベントへ同じ選択集合を保持する。
- 実適用は選択sourceだけへ行い、非選択カードを変更しない。
- 旧来の曖昧な `partial` はfail-closedにする。
- 3枚候補から2枚だけを選ぶE2Eで、判断 → 適用 → Save → reloadまで同じsource集合を追跡できることを確認した。

## 検証

主な回帰は次で固定した。

- backend: merge意味guard、route固有IR、provider実入力経路
- frontend: `merge_suggestion_decisions`, `merge_suggestion_apply`, `representative_merge`, `merge_traceability`, decision audit
- UI: `MergeSuggestionsPanel`
- E2E: accept適用の保存・再読込、partial適用の保存・再読込
- i18n / frontend typecheck

一回限りの検証workflowは検証後に削除し、mainへ常設しない。

## 受入条件

- [x] `suggest-merges` とKJ法のグループ編成・表札生成の違いを定義する。
- [x] 近接した類似カードには04ステップ、複数カードの意味核を保つ統合には核融合法を利用可能とし、一方へ固定しない。
- [x] 元カードID・外部元記録・残差・merge/canonical系譜・戻し検査を統合の不変条件として定義する。
- [x] hold、明示的対立・矛盾、異なる既知 `claimType`、既存merge系譜、同一応答内の候補競合を保護する。
- [x] 島所属・`equivalence`・外部元記録差を単純な許可／禁止条件にしない。
- [x] ADR-0069 D5=Aに基づきDocument-backed structured taskとしてAI入力境界を固定する。
- [x] route-required meaningをintegration regressionで固定する。
- [x] provider実入力を共有IR＋route固有構造化文脈へ移す。
- [x] promptを意味保存型の統合契約へ更新する。
- [x] LLM応答後の決定論的merge guardを実装する。
- [x] 同一カードが複数候補へ出た場合のfail-closedを固定する。
- [x] 元カード・merge元ID・残差・merge/canonical系譜を、提案採用から実適用・保存・再読込まで追跡できることをE2Eで確認する。
- [x] `partial` の明示的な部分集合契約を判断・監査・適用・保存・再読込まで固定する。
- [x] SafeMode二層、PII最小化、structured-text-only、IR上限のfail-closedを維持する。
- [x] `mergeMethod` は実際に適用挙動が分岐するまで必須化しない。
- [x] 自由記述の `residuals` を新たな正本にせず、残るsourceカードを残差の一次記録とする。
- [x] API文書とStage 5計画文書へ実装結果を同期する。
- [x] 最終成果物を、意味を変えず自然な日本語として全文を読み直す。

## 完了境界

04ステップと核融合法を意味保存の考え方として使い分けつつ、元カード、人間判断、矛盾、来歴を失わず、AI提案から実適用・保存・再読込まで戻れることを回帰で固定した。

AIが自動的にmergeを確定・適用する経路は設けていない。部分採用も人間の明示選択を必須とした。以上をもって、本Issueを完了とする。
