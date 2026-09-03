# 継続dogfood R18 — mergeの意味保存を利用経路の契約境界から見直す

- Date: 2026-09-04
- Scope: 日常開発の自己分析。Case 001〜003の統制比較には含めない。
- Question: 意味保存型mergeの主要実装が揃った現在、backend・frontend・ローカルfallback・判断記録は同じ契約境界を共有し、実際の利用経路として機能する状態になっているか。
- Canvas: `doc_kj_atlas_dogfood_r18.json`
- Result class: 継続dogfoodの内部所見。第三者価値実証や認知比較結果の代替証拠ではない。

## 1. 出発点

R18では、`suggest-merges` の意味設計だけをもう一度検討するのではなく、直近でmainへ入った一連の実装を「利用者が候補を取得し、人間が判断し、必要なら明示適用し、保存後に戻れる一続きの仕事」として照合した。

直近までに、少なくとも次が実装済みである。

- 保留、明示的な否定・矛盾、claim type、既存merge系譜を守る意味保存guard。
- route固有structured inputと `LLMRequest.inputs`。
- 元カード、代表カード、merge lineage/source provenanceの保持。
- acceptを記録するだけでは本文を変えず、明示的なapplyを別操作にする境界。
- apply後の保存・再読込まで含むE2E。

したがって、「mergeの意味保存はまだ設計だけで実装されていない」という見方は現在のmainには合わない。一方、実装済みの部品が同じ契約を見ているかは別問題である。

外部LLMは使用していない。backendのresponse modelとprompt schema、frontend API decoder、ローカルfallback、既存test、計画メモを照合した。

## 2. 島1 — 意味保存mergeの本流はすでに利用経路へ到達している

`AI-MERGE-SEMANTICS-01` で定めた「似ているから潰すのではなく、04ステップ型の近接整理または核融合法型の意味統合として提案し、人間判断と元カードへの戻り道を残す」という方向は、直近の実装でかなり具体化している。

特に重要なのは、acceptとapplyを分けたことである。採用判断を記録した時点ではDocumentを変更せず、人間が別操作でapplyして初めて統合が反映される。さらにsource lineageを保持し、保存・再読込後も追跡できることがE2Eで固定された。

このため、R18の焦点は「merge機能を増やすこと」ではなく、**既にある意味保存の経路が境界間の契約不一致で途切れていないか**へ移った。

## 3. 島2 — backendとfrontendの間で二つの契約が混ざっていた

照合すると、実利用を止めるP1の不整合が見つかった。

backendの `MergeSuggestion` 正本は、次の4項目である。

- `groupId`
- 2件以上の `cardIds`
- `mergedTextDraft`
- 任意の `rationale`

backendのLLM向けJSON schemaも同じ外形を要求している。

一方、frontendの `suggestMerges()` は、それらに加えて次を必須として検査していた。

- `targetCardId`
- `candidateCardIds`
- `scoreSummary`
- `reasonCodes`
- `snapshotVersion`

これら追加項目は、AI providerの出力契約ではない。providerが利用できない場合に使う、決定論的なローカル候補生成のStream B再現性メタデータである。

そのため、providerがbackend契約どおりの正常な200応答を返しても、frontendは `Invalid merge suggestions contract payload` として拒否し得た。

ここで重要なのは「backendとfrontendのどちらが正しいか」だけではない。**異なる仕事をする二つの表現を、一つの型へ早く畳んだことで意味境界が消えていた**ことにある。

## 4. 既存testも誤った前提を守っていた

さらに、frontendの既存contract testはこの不整合を検出するどころか、Stream B拡張形をremote responseの正しい形として固定していた。

テストが存在することと、正しい境界を守っていることは同じではない。局所的には整合した実装とtestでも、backend response model、frontend decoder、fallback生成器を横断して見なければ、誤った前提を長く保存できる。

これは今回のdogfoodで特に残すべき観察である。非退行テストは重要だが、何を正本として固定するかを誤れば、**回帰防止装置そのものが契約ドリフトの保存装置になる**。

## 5. 修正 — 共通契約と決定論派生契約を分ける

修正では、backendへ存在しないscoreやsnapshotを補作してfrontendへ合わせることをしなかった。

remote AI提案の共通 `MergeSuggestion` はbackend正本と同じ4項目に戻した。そのうえで、ローカルfallbackだけが持つStream B情報を `DeterministicMergeSuggestion` という派生型に分けた。

これにより、次の両方を保持できる。

- remote AI提案には、実際にproviderが返した意味だけを保持する。
- 決定論的ローカル候補には、候補生成を再現するためのscore、reason、snapshotを保持する。

どちらかへ正規化して情報を捨てるのではなく、責務の違いを型境界として表した。

P1修正は `AI-MERGE-CLIENT-CONTRACT-01` としてDone記録した。

- `01_Plans/issues/done/issue-AI-MERGE-CLIENT-CONTRACT-01-remote-merge-response-rejected-by-frontend.md`

GitHub Actions run `33775874060` で、focused frontend regression 49件、frontend typecheck、docs-check、dogfood validation、planning triage、whitespace検査を成功させた。外部LLMは呼んでいない。

## 6. 島3 — 計画正本にも時間差が残っている

実装面の照合と並行して `01_Plans/issues/issue-*.md` を機械走査したところ、ルート直下110件のうち58件が `Status: Done` だった。

現在のtriageはstatusを見ているため、これだけでactive優先順位が壊れているわけではない。しかし `README.md` が示す「完了メモは `done/` へ置く」という導線と、実際の配置にはかなりのlegacy差がある。

これを一括で58件移動すると参照先変更が大量に発生し、現在のP1修正を埋める。したがってR18ではP2として別Issueへ切り出し、まず今後の増加を止める方向とした。

- `01_Plans/issues/issue-DOC-ISSUE-LIFECYCLE-01-done-memos-remain-at-active-root.md`

同様に、`AI-IR-STAGE5-SCOPE-01` や `AI-MERGE-SEMANTICS-01` には、直近の実装完了後も古い「次の実装」記述が一部残っている。これらは今回のP1修正をmergeした後、方式の追跡性を含めて正本を同期する。

## 7. 島4 — 次に残るのは方式の追跡性であり、外部証拠ではない

remote契約不整合を直した後も、`AI-MERGE-SEMANTICS-01` には一つ重要な残差がある。

現在のpromptは04ステップ型と核融合法型の両方を使い分けるよう指示するが、`MergeSuggestion` 自体には「どちらの方法でこの提案を作ったか」を表す機械可読なフィールドがない。

これは単なる表示上の飾りではない。人間が採用理由を記録し、後から判断経路へ戻るなら、提案が近接整理として出たのか、複数カードから意味核を立てたのかは、判断文脈として残る価値がある。

一方、AI生成の `residuals` フィールドを先に増やす必要はない。現行のapplyは元カードとsource lineageを保持するため、残差そのものへ戻れる。まず方式の識別をどこまでproposal・decision・auditへ通すかを、既存の後方互換を崩さず決める方が小さい。

なお、`AI-IR-SCALE-01` のnamed-provider exact token測定や、`VALUE-REALNESS-01` の第三者実証、formal Case 001は別の境界である。R18の内部修正成功を、それら外部証拠の代替にはしない。

## 8. 今回変更したもの

- remote AI merge responseとfrontend decoderの契約不整合をP1として修正した。
- remote/common契約と決定論ローカル派生契約を分離した。
- backend正本に合わせてfrontend contract regressionを更新した。
- API文書にremote契約とStream B派生表現の境界を追記した。
- `AI-MERGE-CLIENT-CONTRACT-01` をDone記録した。
- Done-at-rootのlegacy差を `DOC-ISSUE-LIFECYCLE-01` としてP2へ切り出した。
- R18のKJキャンバスと継続dogfood記録を追加し、索引へ接続する。

## 9. 今回変更しないもの

- `MergeSuggestion` への `mergeMethod` 追加。
- 58件のDone-at-root一括移動。
- `MAX_CARDS` / `MAX_TEXT_CHARS` 等のscale上限。
- named provider/modelを使うtoken実測。
- Case 001〜003の凍結入力。
- 第三者価値実証条件。

## 10. dogfoodとして得たこと

今回の発見は、単にTypeScript型がbackendと違っていた、というだけではない。

意味保存を目的に、provider入力、guard、lineage、human-in-the-loop、apply、save/reloadを順に強化しても、その間にある一つのdecoderが別の仕事の契約を要求していれば、利用者は本流へ到達できない。

また、誤ったdecoderを既存testがきれいに固定していた。局所的なテスト密度を上げるだけでは、異なる正本の間にできたずれを必ずしも発見できない。

KJ法で実装済みの事実、利用経路、契約、fallback、test、計画メモを同じ場へ置くと、「未実装機能」ではなく**境界どうしの関係のずれ**が前景化した。今回直したのは、そのずれが実際にremote mergeを拒否するP1欠陥だった。

## 11. 文書品質の仕上げ

内容を確定した後、意味を変えずに全文を読み直した。backend対frontendという対立構図にせず、remote AI提案と決定論ローカル候補が異なる責務を持つこと、既存testも誤った前提を保存できること、内部dogfoodと外部価値実証を混同しないことが自然に読める日本語へ整えた。
