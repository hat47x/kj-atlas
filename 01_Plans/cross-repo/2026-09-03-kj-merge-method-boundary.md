# KJ Atlasの統合意味論と外部方法論・意味基盤の境界

更新日: 2026-09-03  
状態: Current cross-repository coordination note

## 1. 目的

`AI-MERGE-SEMANTICS-01`では、`POST /ai/suggest-merges`を単なる重複除去ではなく、04ステップによる近接カードの整理と、核融合法による意味核の統合を使い分けるproposal-onlyの統合支援として整理した。

この具体化はKJ Atlasの製品契約であり、関連リポジトリの方法論や意味契約を自動的に変更するものではない。本書は、その境界と相互参照先を明確にする。

## 2. KJ Atlas側で責任を持つこと

KJ Atlasは、統合候補の生成・表示・採否・系譜保持を製品として実現する。

現在の計画では、少なくとも次をKJ Atlas側の責務として扱う。

- 04ステップ型の近接整理と、核融合法型の意味核統合を区別できる提案契約。
- `holdState`、明示的な対立・矛盾、異なる既知`claimType`などを、人間判断より弱いAI提案が上書きしないための決定論的guard。
- source card、出典、残差、`repOf` / `canonicalId` / `mergedIntoCardId`等の系譜を失わないこと。
- 統合結果から元カードへ戻して照合できること。
- AI提案を自動適用せず、最終判断を人間に残すこと。

これらは`AI-MERGE-SEMANTICS-01`とADR-0069 D5=Aの範囲で扱う。

## 3. cultural-substrate-weavingとの境界

cultural-substrate-weavingの方法論正本は、材料から意味単位を立てる際の境界・核・戻し照合・残差保持などを扱う。一方、KJ Atlasの`mergeMethod`、API response、系譜field、UI操作は製品固有のRealizationである。

したがって、KJ Atlasで04ステップ／核融合法を製品機能として具体化したことだけを理由に、cultural-substrate-weavingの`src/<locale>/`へKJ Atlas固有のAPI語彙や操作手順を追加しない。

KJ Atlasの実使用で、方法そのものに再現性のある欠陥が見つかった場合は、cultural-substrate-weaving側の既存dogfood帰属ゲートを通して判断する。単一の製品実装上の問題は、まずKJ Atlas側へ帰属する。

参照:

- `hat47x/cultural-substrate-weaving:src/ja-JP/methods/integration.md`
- `hat47x/cultural-substrate-weaving:docs/ja/maintainers/kj-atlas-cognitive-coevolution.md`

## 4. SOZAとの境界

SOZAの`SOZA Cognitive Method Contract v1alpha1`は、Method Definition、Method Realization、Method Applicationを分離し、Applicationの`input_refs` / `output_refs` / `residual_refs`とSemantic Lineageを保持できる。

したがって、KJ Atlasで04ステップ／核融合法の使い分けや統合proposalの来歴表現が具体化しても、それだけでSOZAのUniversal Cognitive Method Contractを変更する必要はない。

SOZAへ渡す場合は、KJ Atlas固有のAPI fieldをUniversal fieldへ昇格させるのではなく、必要に応じてMethod Realization / Method Applicationの参照Artifactとして保持する。KJ Atlas側のsource・residual・lineageをSOZA取り込み時に失う具体的な不整合が観測された場合だけ、SOZA側のContract / Adapter課題として起票する。

参照:

- `hat47x/soza:contracts/cognitive-method/SOZA_COGNITIVE_METHOD_v1alpha1.md`

## 5. TEIとの境界

今回の変更はKJ Atlas内の認知支援・proposal・意味保持の契約であり、TEIのCapability、Binding、Runtime、Execution方式を変更しない。

したがって現時点ではTEI側の計画文書や実装へ対応変更を起こさない。将来、KJ Atlasの統合操作をTEI Capabilityとして呼び出す、または統合結果をTEIのCanonical Semanticへ受け渡す具体的要件が生じた場合に、その境界を別途確認する。

## 6. 横断変更の発火条件

今後、次のいずれかが観測された場合に相手リポジトリへ対応課題を起票する。

1. KJ Atlasの製品実装ではなく、04ステップ／核融合法そのものの方法上の欠陥が複数ケースで再現する。
2. KJ Atlasのsource / residual / lineageをSOZAの現行Reference / Method Applicationで損失なく表現できない。
3. KJ Atlasの統合操作をTEIのCapability / Binding / Runtime契約として公開する実要件が生じる。
4. 一方の変更が、他方の凍結実験条件や公開済みContractを暗黙に変えてしまう。

これらが無い限り、相互参照は維持しても、変更件数を揃えるためだけの対称的な改修は行わない。

## 7. 現在の判定

2026-09-03時点では、対応は次のとおりとする。

- KJ Atlas: `AI-MERGE-SEMANTICS-01`を継続し、製品固有の統合契約とguardを具体化する。
- cultural-substrate-weaving: 方法論正本は変更しない。KJ Atlas dogfoodの帰属境界として記録する。
- SOZA: Universal Cognitive Method Contractは変更しない。KJ Atlasの具体化はRealization / Application側で収容可能と判断する。
- TEI: 変更なし。Capability / execution境界へ影響する具体的要件は現時点でない。

この判定は「他リポジトリと無関係」という意味ではない。相互依存を明示したうえで、現在の正本がすでに受け止められる範囲では不要な変更を増やさない、という判断である。
