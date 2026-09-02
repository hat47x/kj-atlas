# Issue: DOC-DOGFOOD-INDEX-01 継続dogfood記録を索引から脱落させない

- Type: Process / Documentation / Test
- Status: Done
- Source Issue: COGNITIVE-DOGFOOD-01
- Priority: P1
- Owner: Maintainer
- Scope: `01_Plans/dogfood/cognitive-dogfood-index.md`, `01_Plans/dogfood/validate_dogfood_docs.py`, `01_Plans/dogfood/cognitive-dogfood-continuous-*.md`
- Related ADR/Spec: `01_Plans/issues/issue-COGNITIVE-DOGFOOD-01-product-development-cognitive-workbench.md`
- Expected verification level: `docs-check`

## 課題

`cognitive-dogfood-index.md` は、認知dogfoodの意思決定、実行条件、回顧監査、実験入力、実行結果を混同せず辿るためのナビゲーション索引である。

しかし2026-09-03時点で、継続dogfoodの実体はR7〜R13まで存在する一方、索引の「継続dogfood — 日常開発の自己分析」にはR8〜R10しか掲載されていなかった。R7は最初から索引に載らず、R11〜R13も各ラウンドの成果物が追加された後に索引更新が追随していない。

索引が判断の正本ではないことと、索引の欠落を許容してよいことは別である。導線が欠けると、後続のdogfoodや引き継ぎで、既に観察・修正した摩擦を見落とし、同じ調査や判断を繰り返しやすくなる。

## dogfoodで観察した摩擦

R13を完了した後、次の作業候補を探すため `cognitive-dogfood-index.md` を読み直したところ、R11〜R13が索引に存在しなかった。さらにdogfoodディレクトリ全体と突合すると、最初の継続dogfoodであるR7も索引から欠けていた。

この問題は、個々の記録が壊れているのではない。記録ファイルとDocumentV1キャンバスは存在し、構造検査も通っている。それでも「どこから辿るか」を担う索引だけが手作業で更新されるため、成果物の追加と導線の更新が別々に進み、時間差が生じていた。

## 対応

1. `cognitive-dogfood-index.md` の継続dogfood欄へR7、R11、R12、R13、R14を追加し、R7〜R14を一続きで辿れるようにする。
2. `validate_dogfood_docs.py` に継続dogfood索引の被覆検査を追加する。
3. `cognitive-dogfood-continuous-*.md` が1件でも索引から欠けた場合はdocs contractを失敗させる。
4. 各継続dogfood記録から対応するDocumentV1キャンバスが参照され、そのキャンバスが実在することも検査する。
5. R14自身も索引へ載せ、今回だけの手修正ではなく「新しい継続dogfoodを追加する変更は、同じ変更で索引も更新する」という運用へ切り替える。

## 受入条件

- [x] R7〜R14の継続dogfood記録を索引から辿れる。
- [x] R7〜R14の対応する `doc_kj_atlas_dogfood_r*.json` を索引または各記録から辿れる。
- [x] `validate_dogfood_docs.py` が全 `cognitive-dogfood-continuous-*.md` を列挙する。
- [x] 継続dogfood記録が索引にない場合、検査が失敗する。
- [x] 継続dogfood記録が対応キャンバスを参照しない場合、検査が失敗する。
- [x] 参照されたキャンバスが存在しない場合、検査が失敗する。
- [x] Case 001〜003の凍結入力や比較条件には触れない。
- [x] 変更後の文書を、意味を変えず自然な日本語として読み直す。

## 非目標

- 索引を新しい意思決定の正本へ昇格すること。
- 継続dogfoodをCase 001〜003の比較結果として扱うこと。
- 過去ラウンドの内容を再評価・書き換えすること。
- ファイル名の履歴を一括で付け替えること。

## 検証

- `python 01_Plans/dogfood/validate_dogfood_docs.py`
- docs contract CI
- R7〜R14の記録・キャンバス・索引の相互参照を目視確認する。

## ロールバック

自動被覆検査が将来のdogfood記録方式と合わなくなった場合は、同等以上の機械検査へ置き換える。索引更新を完全な手作業へ戻すことは、今回確認した脱落を再発させるためロールバック先としない。

## 文書品質の仕上げ

課題、対応、検査境界を固めた後、意味を変えずに全文を読み直した。索引が「正本ではない」ことと「導線として完全であるべき」ことを混同しないよう、役割の違いが自然に読める表現へ整えた。
