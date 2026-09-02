# 継続dogfood記録 — 2026-09-02 第4ラウンド

## 位置づけ

この記録は、KJ Atlas自身を日常的な開発対象としてKJ法で検討する継続dogfoodの第4ラウンドである。

前ラウンドでは `VALUE-REALNESS-01` を対象とし、第三者価値実証について、検証手順はすでに準備されており、現在の律速は実際の第三者と資料という外部入力にあることを確認した。

今回は、もう一つのP0である `COGNITIVE-EVAL-01` を対象とし、認知比較実験が何を待っているのかを確認した。

Case 001〜003の統制比較そのものではない。この継続dogfoodは、比較設計、評価軸、自然発生した訂正履歴、R8/R9などの既知情報を含むため、A〜Dのどのarmにも数えない。生成AIの外部APIも使用していない。

## 今回の問い

> 認知比較実験を進めるうえで、いま不足しているのは比較設計、実験ハーネス、KJ Atlasの製品機能なのか。それとも、比較条件から隔離されたfresh contextと、C/DでKJ Atlasを実際に操作する実行入力なのか。

「まだ準備不足だから実験できない」と最初から決めず、正本Issue、凍結記録、実行計画、索引、UI runbook、validator群、受入条件を同じ場に置いて確認した。

## 用いた材料

- `01_Plans/issues/issue-COGNITIVE-EVAL-01-factorial-human-ai-cognitive-control-evaluation.md`
- `01_Plans/issues/issue-COGNITIVE-DOGFOOD-01-product-development-cognitive-workbench.md`
- `01_Plans/dogfood/cognitive-dogfood-case-portfolio-preregistration.md`
- `01_Plans/dogfood/cognitive-dogfood-case-portfolio-freeze.md`
- `01_Plans/dogfood/cognitive-dogfood-execution-plan.md`
- `01_Plans/dogfood/cognitive-dogfood-index.md`
- `01_Plans/dogfood/cognitive-dogfood-cd-ui-runbook.md`
- `01_Plans/dogfood/cognitive-dogfood-run-record-template.md`
- `01_Plans/dogfood/cognitive-dogfood-blind-review-protocol.md`
- `01_Plans/dogfood/validate_cognitive_launch_packets.py`
- `01_Plans/dogfood/validate_cognitive_arm_packages.py`
- `01_Plans/dogfood/validate_cognitive_run_records.py`
- `01_Plans/dogfood/build_cognitive_blind_package.py`
- `01_Plans/dogfood/test_validate_cognitive_arm_packages.py`
- `01_Plans/dogfood/test_validate_cognitive_run_records.py`
- `01_Plans/dogfood/test_build_cognitive_blind_package.py`

## KJキャンバス

正規データは次のDocumentV1に残した。

- `01_Plans/dogfood/doc_kj_atlas_dogfood_r10.json`

今回のカードもAIが作成した提案段階の材料なので、`textReviewed: false` としている。

## 島1 — 比較設計とハーネスは揃っているが、valid raw runはまだ得られていない

`COGNITIVE-EVAL-01` はP0かつIn Progressで、Case 001〜003をA〜Dの4条件で比較する設計を正本として持っている。

P0では、次がすでに固定・検査されている。

- Case 001〜003の問い。
- product snapshotとskill snapshot。
- A〜Dのtreatment。
- arm間で共通に要求する成果。
- product evidence bundle。
- B/Dだけへ渡すskill bundle。
- C/Dだけへ渡す空starter。
- run record。
- blind packageとblind review手順。

さらに、launch packet、arm package、run record、blind packageには専用validatorとcontract testがある。

一方、`cognitive-dogfood-index.md` の現在地は明確に次である。

> P1: Case 001 Arm C ready / raw run未取得

`COGNITIVE-EVAL-01` の受入条件でも、3ケースすべての4arm比較、M1〜M9の観察、blind review、C/DでのInquiryJourney実使用などは未完のままである。

したがって、実験準備が成熟していることと、比較証拠が得られていることは分けて扱う必要がある。

## 島2 — 現在の律速は隔離されたfresh contextとC/Dの実UI操作にある

比較設計では、各armを独立したコンテキストで開始し、他armの中間成果や評価者側の既知仮説を見せないことになっている。

これは形式的な手続きではない。

今回のような設計者側の継続dogfoodは、すでに次を知っている。

- 4armの狙い。
- M1〜M9。
- Case 001の自然発生した訂正履歴。
- Case 000の回顧監査。
- R8/R9で得た内部所見。
- どの失敗類型を観察するか。

このコンテキストでA〜Dの回答を作れば、方法そのものを知っていることがarmへ混入する。とくに「何を見落としてはいけないか」を知った状態では、通常チャット条件の基準線まで意図せず改善してしまう。

また、C/Dは単にKJ形式のJSONを成果物として持つ条件ではない。KJ Atlasキャンバス上でカードを外部化し、束ね、残差や対立を見ながら構造を動かし、必要な節目でInquiryJourneyを使う。その外部表象との往復自体がtreatmentである。

したがって、このチャット内でJSONを代理編集しても、C/Dを実施したことにはならない。

現在valid runを得るために不足している主入力は、次の二つである。

- 比較設計の既知情報から隔離されたfresh context。
- C/DでKJ Atlas UIを実際に扱うoperator execution。

## 島3 — 準備を増やすより、妥当性を保ったまま実行へ移る

ここで新しい実験schema、追加KPI、別の履歴API、さらに細かいpreflight文書を増やしても、fresh contextと実UI操作がない限りvalid比較証拠は増えない。

むしろ、準備を増やし続けると次の問題が起きる。

- 実験instrumentationが製品契約へ逆流する。
- operatorが実験設計を知る情報量がさらに増える。
- 「実行のための準備」が自己目的化する。
- 実際の比較結果がないまま、内部整合だけが高度化する。

逆に、隔離条件を緩めればすぐにA〜Dらしい成果物は作れる。しかし、それは実行を早める代わりに比較の意味を弱める。

このため、R10では「もっと自動化すべき」という方向へ進めない。

valid runの不足を、KJ Atlasの製品欠陥や `cultural-substrate-weaving` の方法欠陥へ読み替える証拠もない。

## 島4 — frozen snapshotの比較価値と現在mainへの一般化限界を同時に保持する

Case 001〜003は、arm間で同じ製品状態を比較するため、product snapshotを固定している。

これは比較実験には必要である。実行順の途中でcurrent mainへ追従すると、R7〜R9や初回価値体験の改善など、別の変更がarm間へ混入するためである。

一方、2026-09-02現在のmainは、その固定snapshotより先へ進んでいる。

したがって、Case 001〜003で得る結果には二つの読み方を混同しない。

- **有効な読み方**: 同じ固定状態で、通常文書/KJ Atlas、skillなし/ありの差がどう出たか。
- **過剰な読み方**: その結果を、その後の改善を含む現在main全体の絶対評価として扱うこと。

固定snapshotは古いから無効なのではなく、因果比較のために意図的に固定されている。ただし結果の一般化範囲には時点を明示する必要がある。

## 課題の振り分け

| 観察 | 判定 | 対応 |
| --- | --- | --- |
| 3ケース・4arm・固定snapshot・評価軸は定義済み | 解消済みの不確実性 | 比較設計を追加しない |
| bundle / package / run / blind reviewの検査系は存在する | 解消済みの不確実性 | 新しい実験schemaを作らない |
| Case 001 Arm Cはreadyだがraw run未取得 | 既存P0の未完 | `COGNITIVE-EVAL-01` をIn Progressのまま維持する |
| この設計者コンテキストはarmとして汚染済み | 既存境界 | valid runには使わない |
| C/Dは実UI外部表象の操作が必要 | treatment条件 | JSON代理編集を実走へ読み替えない |
| frozen snapshotとcurrent mainに時点差がある | 解釈上の境界 | 比較の内的妥当性と現在製品への一般化を分ける |
| さらにpreflightを増やしたくなる | instrumentation leakage候補 | raw run取得まで新規ハーネス追加を原則停止する |

## 今回の判断

R10で新しい製品P0欠陥は確認されなかった。

また、新しいADR、別issue、`cultural-substrate-weaving` 正本変更を起こす根拠も得られなかった。

`COGNITIVE-EVAL-01` を実質的に前進させる次の条件は、事前登録された順序に従い、Case 001の隔離されたArm C runを実際に取得することである。その後は同じくfreshなD、B、Aへ進み、static intakeを通したraw recordだけをblind reviewへ渡す。

この継続dogfood自体は、その比較結果の代替証拠にはしない。

## 残る未完

- Case 001 Arm Cのvalid raw run。
- 続くD、B、Aの独立run。
- Case 001のblind reviewとRound 2反証。
- Case 002/003の4arm比較。
- 3ケースを通じたKJ Atlas固有増分、skill固有増分、相互作用、負の相互作用の判定。
- `DOMAIN-W-ITERATION-01` T9へ返す実使用証拠。

これらは、内部準備文書を増やすことでは完了しない。
