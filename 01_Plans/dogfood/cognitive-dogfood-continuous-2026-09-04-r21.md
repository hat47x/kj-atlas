# 継続dogfood R21 — 凍結した比較と現在mainへの移送妥当性を分離する

- Date: 2026-09-04
- Scope: 日常開発の自己分析。Case 001〜003の統制比較には含めない。
- Question: formal Case 001〜003の製品snapshotを2026-08-27時点へ凍結したまま、急速に進む現在mainに対する検証価値をどう失わずに保つか。
- Canvas: `doc_kj_atlas_dogfood_r21.json`
- Result class: 継続dogfoodの実験運用記録。formal Caseの結果、第三者価値実証、製品価値の証明には数えない。

## 1. 出発点

formal Case 001〜003では、製品資料と比較条件を `hat47x/kj-atlas@2232b3bb26647e5c4a083f55bdbf83c161698649` へ凍結している。これは、Case 001の結果を見てからCase 002/003の入力や製品状態を有利に変更しないための内的妥当性の境界である。

一方、2026-09-04時点のmain `16136ef03d516facd82f438fd3f158c3fa9456f8` は、固定snapshotより986 commits先へ進んでいる。R7〜R20の継続dogfood、AI入力IR、merge意味論、SaaS関連の実装・検証などもこの期間に追加された。

この差を見て元のRound 1を現在mainへ差し替えると、事前登録した比較条件を自分たちで壊す。しかし、元の結果をそのまま「現在のKJ Atlasの結論」と呼べば、今度は時間経過による移送妥当性を過大評価する。

したがって問題は、**凍結を守るか、現在性を取るかの二者択一ではない**。

## 2. commit距離と意味ドリフトを分ける

986 commitsという距離は、現在性の警告にはなるが、それ自体を「資料が古い」尺度にはしない。

Case 001の固定20資料の一つ `README.md` は、固定manifest上のblob SHA `e9a98fd727d553739dbe404104793ace6e5c9cdf` と2026-09-04 mainのblob SHAが同一である。つまり、多数のcommitが積まれていても、その資料の意味が変わっていない場合がある。

逆に、ADR、Issue、AI入力経路、継続dogfoodのように、同じテーマでも後続実装・訂正・完了移動によって意味が変わる資料もある。

今後「現在性」を評価するときは、少なくとも次を分ける。

1. repository全体のcommit距離。
2. formal inputとして使った各資料の意味ドリフト。
3. そのCaseの問いに直接関係する製品契約の変化。
4. KJ Atlas runtime/UI contractの変化。
5. 元の結論が現在状態でも成立するかという移送結果。

## 3. evidence snapshotとruntimeを別概念として確認した結果

formal packageは、固定製品資料、Arm固有の`launch.md`、C/Dの空starter、B/Dの固定skill sourceを運ぶ。しかし、KJ Atlasの実行binaryやfrontend一式をartifactへ同梱していない。

そのため、packageだけを見ると「証拠は8月27日、UIは操作者がその時点で使える最新版」という読み方も技術的には可能だった。

ただし、既存のfreeze記録は「Case 001〜003は、同じKJ Atlas product commitを使用する」としている。C/D共通UI runbookも「製品runtimeの参照基準」を、各Caseで固定したproduct snapshotとpreflightで確認済みの同一UI contractとしている。

したがってformal Round 1の既存契約に最も整合する解釈は、次である。

> **製品について読む証拠だけでなく、C/Dで操作するKJ Atlas runtimeも `2232b3bb26647e5c4a083f55bdbf83c161698649` を基準にする。**

ここで不足していたのは新しいtreatmentではなく、その既存条件をoperator手順へ実行可能な形で明示することである。

## 4. 元のformal portfolioを再凍結しない

Case 001〜003の元のRound 1について、次は変更しない。

- fixed question。
- product source manifest。
- product snapshot `2232b3bb…`。
- skill snapshot `3988e12e…`。
- A/B/C/D treatment。
- required output。
- 実行順 C → D → B → A。
- Case実行順 001 → 002 → 003。

R7〜R20や2026-09-04 mainの新しい実装を、元のArmへ「現在性を上げるため」に追加しない。これらは元の比較では後発情報であり、混ぜれば別実験になる。

C/Dでは、可能な限り固定product commitのKJ Atlas runtimeを起動して操作する。current mainを代用して結果だけ元のformal Caseへ入れない。

固定runtimeを実際に起動できない、重大な安全上の理由で使用できない、または実験そのものが成立しない契約破損が判明した場合は、黙ってcurrent mainへ切り替えない。元runを`invalid / blocked`として理由を保存し、別revisionとして再設計する。

## 5. 現在mainへの問いは後段のtransfer checkにする

元のformal portfolioが答える問いは、次のように限定する。

> 2026-08-27に事前登録した同一の製品状態・資料状態において、A/B/C/Dの方法差はM1〜M9へどのような差を生んだか。

これを現在mainへ適用できるかは、別の問いである。

元のCase 001〜003を完了した後、必要性が残る場合に**current-state replication / transfer check**を別revisionとして行う。そこでは新しい共通snapshotを固定し、元の結果のうち何が生き残り、何が現在実装によって消え、何が新しく現れたかを比較する。

この後段検証は元Round 1を書き換えない。元の比較結果は内的妥当性の基準として残し、現在状態への一般化可能性だけを追加で調べる。

## 6. 継続dogfood R7〜R20の扱い

R7〜R20は、formal Caseを待つ間にも実際の開発判断へKJ的外部化を使い、訂正・契約同期・意味保存・Issue変換へつながった重要な実績である。

特にR15→R16では、同じ測定値を保持したまま解釈を訂正した。R18→R20では、merge方式という意味属性がbackendだけでなくfrontend、fallback、UI、人間判断、保存済みdecisionまで通らなければ「存在する」とは言えないことを実装へ戻した。

ただし、これらは比較条件を知った設計者コンテキストで行われ、通常文書/skill/KJ Atlasを分離した対照を持たない。したがって、formal Caseの認知増分を証明する材料には昇格させない。

役割は次のように分ける。

- 継続dogfood: 現在mainを改善し続ける実践証拠。
- 元formal portfolio: 方法差の内的比較。
- current-state replication: 元比較の現在mainへの移送可能性。
- 第三者価値実証: 開発者自己利用の外へ出た価値実在。

## 7. KJ統合で立った中心構造

今回のカードをまとめると、中心に残ったのは次の構造である。

> **比較の時計を止めることと、製品の時計を止めることは別である。**

formal portfolioでは比較可能性のために時計を止める。しかし製品開発は止めない。開発が進んだ事実を理由に過去の比較条件を更新するのではなく、元比較を完遂し、その後に現在状態へ橋を架ける。

この二段構えなら、凍結による内的妥当性と、進化する製品への移送妥当性を同じ一つのrunへ無理に背負わせずに済む。

## 8. Finding triage

### F0 — 継続dogfoodとして保持

- 986 commitsという距離だけではformal inputの陳腐化を判定できない。
- relevant source / contract単位で意味ドリフトを見る必要がある。
- R7〜R20は現在性の重要資料だが、元Arm入力には戻さない。

### F1 — 既存認知評価へ返す実行上の観察

- C/D runtimeも固定product commitを用いる、という既存freeze契約をoperator実行手順で明示する。
- 元portfolio完了後、現在mainへのtransfer checkが必要かを`COGNITIVE-EVAL-01`の結果解釈時に判断する。

### F2 / F3

新しい製品Issue、skill Issue、ADRは起票しない。

今回見つかったのは製品利用者の欠陥ではなく、比較実験の時間軸とoperator手順の解釈不足である。元portfolioを一度も実行していない段階で、新しい製品契約や長期ADRへ昇格させない。

## 9. 次工程

1. formal inputファイルは変更しない。
2. C/D operator手順に、KJ Atlas runtimeも固定product commitから起動することを明示する。
3. Case 001 Arm Cを、fresh context + frozen evidence + frozen runtimeで実走する。
4. C → D → B → A、Case 001 → 002 → 003の順序を維持する。
5. 元portfolioのblind review / unblind後に初めて、current-state replicationの必要性を判定する。
6. 第三者価値実証は別レーンのまま進める。

R21自身を、formal Caseをさらに延期する新しいpreflight gateにはしない。今回のruntime表記補正を終えたら、次の有効な証拠は引き続きCase 001 Arm Cの実走から得る。


## 10. 固定runtimeの実行可能性をsmoke確認

R21のruntime解釈をoperator手順へ戻した後、formal product commit `2232b3bb26647e5c4a083f55bdbf83c161698649` 自体を別checkoutとして起動可能かを、分析内容を与えない技術smokeで確認した。

branch-only one-shot workflowでは、固定commitのfrontend依存をそのcommit自身のtoolchain契約で導入し、次を実行した。

- TypeScript typecheck。
- Vite production build。
- Chromium installation。
- `first_run_document_entry.spec.ts`。
- `inquiry_handoff_review.spec.ts`。
- `inquiry_round_comparison.spec.ts`。

これらが成功したため、少なくともCase 001 Arm C/Dで必要なDocument読込、InquiryJourney開始、handoff、保存・再開、lineage、round比較、branch操作を含む代表UI contractは、固定runtime上で現在のGitHub Actions環境から再実行可能である。

このsmokeはformal Armの分析ではなくoperator/runtime setup検証であり、M1〜M9、T9、製品価値、第三者価値の証拠には数えない。また、成功を理由にformal sourceやtreatmentを変更しない。

したがってR21で想定した「固定runtimeが実行不能なら別revision」という分岐は、現時点では発火しない。次工程は予定どおりCase 001 Arm Cのfresh-context実走である。
