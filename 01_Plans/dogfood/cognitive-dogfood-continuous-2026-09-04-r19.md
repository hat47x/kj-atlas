# 継続dogfood R19 — merge方式の意味をproposalから判断記録まで追う

- Date: 2026-09-04
- Scope: 日常開発の自己分析。Case 001〜003の統制比較には含めない。
- Question: R18でremote提案と決定論fallbackの契約を分離した後も、利用者が統合候補を判断し、後からその判断へ戻るために必要な意味が途中で失われていないか。
- Canvas: `doc_kj_atlas_dogfood_r19.json`
- Result class: 継続dogfoodの内部所見。第三者価値実証や認知比較結果の代替証拠ではない。
- External LLM: 使用していない。

## 1. 出発点

R18では、remote AI提案と決定論ローカルfallbackが異なる責務を持つにもかかわらず、frontendで一つの契約へ畳まれていた問題を修正した。その後の残差として、merge promptが04ステップ型の近接整理と核融合法型の意味核統合を使い分けるよう要求している一方、provider応答にはその選択結果を表す欄がないことが残った。

R19では、方式フィールドを先に追加するのではなく、provider出力、frontend表示、採否記録、Document上の永続decision、決定論fallbackを同じ場に置き、「方式」が本当に独立して保存すべき意味かを確認した。

## 2. 島1 — promptでは方法を選ばせているが、応答契約で消えている

現行promptは、カードを似ているからまとめるのではなく、状況に応じて次の二方式を使い分けるよう求めている。

- 04ステップ型の近接整理。
- 核融合法型の意味核統合。

しかしR18時点の `MergeSuggestion` は `groupId`、`cardIds`、`mergedTextDraft`、任意 `rationale` だけであり、どちらの方法を選んだかを返せなかった。

これは表示上の不足だけではない。promptでモデルへ求めた判断の一部を、review境界へ渡す前に捨てている。したがって方式は、自由文の説明に埋める補足ではなく、proposalが持つ意味属性として扱う必要がある。

## 3. 島2 — rationale、人間理由、方式は別のものとして残せる

現行UIとdecision logは、AI側の `rationale` と、人間が採否時に書く理由をすでに分けている。

この構造なら、方式をどちらかの文字列へprefixとして埋め込む必要はない。

- `rationale`: AIがその候補を提案した理由。
- 人間の `note`: 採用・部分採用・却下・保留を決めた理由。
- `mergeMethod`: その候補がどの統合アプローチとして生成されたか。

三つを分離すれば、後から理由文を編集・翻訳しても方式が失われず、方式ラベルだけを人間判断の根拠として扱うことも避けられる。

## 4. 島3 — 決定論fallbackは `near_duplicate` と言えるが、核融合法とは言えない

frontendの決定論fallbackは、正規化本文一致またはtoken signature一致から候補を出す。これは近いカードを整理する候補探索であり、複数カードの差を保持しながら新しい意味核を立てる処理ではない。

したがって、fallbackについては `near_duplicate` を事実として付与できる。一方、fallbackが `kernel_fusion` を行ったと推測してはいけない。

remote AI提案とfallbackを再び同じ内部実装へ畳まず、共有するのは次の二値の意味語彙だけとする。

- `near_duplicate`
- `kernel_fusion`

## 5. 島4 — 新規記録を厳格にし、旧記録は推測しない

方式を導入するときに、過去のDocumentへ一律に `near_duplicate` を補うと履歴を創作することになる。古いdecisionは方式を保存していなかったため、そこから正確な方法を復元できない。

そこで境界を次のように分ける。

- 新しいremote provider応答: `mergeMethod` 必須。
- 新しいfrontend共通 `MergeSuggestion`: `mergeMethod` 必須。
- 新しいdecision書き込み: `mergeMethod` 必須。
- 決定論fallback: `near_duplicate` を明示。
- 保存済み旧decisionの読込み: `mergeMethod` はoptional。欠落を推測補完しない。

これは既存Documentを壊す破壊的migrationではない。新規のproposal/decision経路を厳格にしながら、過去記録は事実以上に補作しない加算的変更である。

## 6. 判断

R19では、`mergeMethod` を必要と判断した。`AI-MERGE-SEMANTICS-01` の既存意味境界に直接属するため、新しいIssueやADRへ分離せずF1として戻す。

実装契約は次のとおりとする。

1. 語彙は `near_duplicate | kernel_fusion` の2値。
2. provider応答とfrontend共通契約では必須。
3. fallbackは `near_duplicate`。
4. UIでAI理由と別に表示する。
5. 新規Document decisionへそのまま保存する。
6. 旧decisionの欠落は許容し、推測しない。
7. 軽量な短期audit eventへ同じ値を重複保存することは今回の必須条件にしない。
8. `residuals`、自動partial適用、自動確定へ範囲を広げない。

## 7. 今回変更しないもの

- Case 001〜003の凍結入力と比較条件。
- `VALUE-REALNESS-01` の第三者価値実証条件。
- `AI-IR-SCALE-01` のscale・token実測。
- mergeを自動採用・自動適用する権限拡張。
- 旧decisionへの方式推測補完。

## 8. dogfoodとして得たこと

R18では「異なる仕事の契約を一つへ畳むこと」が不具合を生んだ。R19では反対に、説明文へすべてを畳むと、判断の種類そのものが機械可読な履歴から消えることが見えた。

意味保存とは元カードを残すことだけではない。**どのような統合として提案され、人間が何を見て判断したかへ戻れること**も、判断を再訪する仕事の一部である。
