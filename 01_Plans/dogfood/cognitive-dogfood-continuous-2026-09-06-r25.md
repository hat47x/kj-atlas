# 継続dogfood R25 — 凍結座標を許すguardと、凍結manifestを守るguardは別に要る

- Date: 2026-09-06
- Scope: 日常開発の自己分析。Case 001〜003の統制比較には含めない。
- Question: R24でhistorical coordinateをlive stale referenceから分離したあとも、current lifecycle closeoutがfrozen manifest自身のpathを書き換える再発をどう防ぐか。
- Canvas: `doc_kj_atlas_dogfood_r25.json`
- Observation baseline: `main@6dacc1de9335d9b9a8486a5cd40ef92ef164fc76`
- Trigger: PR #3001 / merge commit `5dce7ac6754718f4661282ca24b9c076cc148695`
- Result class: R24直後の実運用で観測したfrozen experiment inputの陽性再改変。formal Case、第三者価値実証、AI-IR named-provider測定の結果には数えない。

## 1. R24のあとに実際に起きたこと

R24は、`01_Plans/issues/<name>`という同じ文字列でも、current repositoryを指すlive referenceと、`productCommit + path + blobSha`で過去を固定するhistorical coordinateは別の意味だと整理した。

その直後、PR #3001は`issue-AI-ROUTE-01-multi-model-routing-and-final-judgment-boundary.md`をcurrent mainで`01_Plans/issues/done/`へcloseoutした。同時に、Case 002 Round 1 source manifest内の同Issue pathも現在位置へ追随させた。

しかしCase 002 manifestでは、

- `productCommit = 2232b3bb26647e5c4a083f55bdbf83c161698649`
- `blobSha = 944acc723f8c0707ea322af7b28f830e5c7a3eaa`

が据え置かれていた。変更されたのはpathだけである。

frozen commit上でこのblobが存在した座標は、当時のactive-rootに置かれていた同Issueファイルであり、current `done/` pathではない。したがって#3001の変更はcurrent lifecycle参照としては自然でも、frozen snapshot coordinateとしては不正だった。

## 2. R24だけでは止められなかった理由

R24で追加したlegacy Done-root guardは、frozen source manifest自身を読み、構造条件を満たす旧root pathだけをstale-reference grepの例外として導出する。

これは「正しいhistorical coordinateをlive stale referenceと誤認しない」ためには有効である。

一方、そのmanifest自身が`done/`へ書き換わると、旧root pathはexception setから消える。つまりR24 guardはmutable manifestを例外判定の入力としているため、**例外対象そのもののimmutabilityを証明するguardではない**。

既存`validate_dogfood_docs.py`にはfull Git historyが利用できる場合、`productCommit:path`を実際に解決して`blobSha`と照合する検証が既にある。この検証を重複実装する必要はない。しかし通常のplanning testや履歴を持たない検証でも、凍結manifest自体が変わったことを即座に見えるようにする独立不変条件が不足していた。

## 3. 二層のguard契約

今回、R24のguardはそのまま残し、別の責務としてCase 001〜003 Round 1 source manifestのGit blob identityを固定する。

R24修復後の正本blobは次である。

- Case 001: `7e0284d69b9d3646b37a6fc1fb92481edbac0256`
- Case 002: `e888443feafd67d848d42f3ac5c0b8dc48050e47`
- Case 003: `4e819c3dfe1e2bae43eb644e4fbb94b89d5e45fc`

`01_Plans/tests/test_frozen_dogfood_manifest_identity.py`はGit historyを必要とせず、ファイルbytesからGit blob object idを再計算してこの3値と比較する。

これにより役割は次のように分かれる。

1. **R24 live-reference guard**: frozen historical coordinateをcurrent stale referenceとして誤検知しない。
2. **R25 manifest-identity guard**: current lifecycle変更がfrozen manifestそのものを書き換えたらfailする。
3. **既存dogfood validator**: full historyがある環境では`productCommit:path -> blobSha`まで実在照合する。

一つのguardへすべてを詰めず、三者が異なる失敗方向を受け持つ。

## 4. 実修正

Case 002 manifestは#3001以前かつR24修復後のblob `e888443f...`へ戻した。資料選択、blobSha、productCommit、問い、A/B/C/D条件は変更していない。

追加したplanning testでは、3 manifestの現在bytesが固定blob identityと一致することを確認する。またCase 002のAI-ROUTE pathを`issues/done/`へ一件だけ置換したbytesが固定identityと一致しないことをnegative controlとして明示する。

この固定は「今後manifestを一切増やせない」という意味ではない。Round 1を変更せず、新しい入力が必要ならlater roundの新manifestとして追加する。

## 5. KJ統合で立った中心構造

今回の中心は次にまとまる。

> **例外を正しく許すことと、その例外対象自体が書き換わらないことは別の契約である。**

R24では「historical pathを消さない」ために例外認識が必要だった。R25では、その例外の正本自身をcurrent stateへ追随させないために独立したimmutabilityが必要になった。

この二つは矛盾しない。むしろ、過去の座標を過去のまま読めることと、その座標が現在の都合で変形されないことがそろって初めてsnapshot identityになる。

## 6. Finding triage

### F0 — 生の観察として保持

- PR #3001でCase 002 frozen manifestのAI-ROUTE pathがcurrent `done/`位置へ実際に書き換わった。
- `productCommit`と`blobSha`は変わらず、pathだけがcurrent lifecycleへ追随した。
- R24直後に、R24が守ろうとしたhistorical-coordinate意味の逆方向破壊が実運用で再発した。

### F1 — 既存guard群へ返す

- Case 002 manifestをR24修復後のfrozen blobへ復元する。
- `01_Plans/tests`でCase 001〜003 Round 1 manifest blob identityを独立にpinする。
- full-history path/blob照合は既存dogfood validatorへ残し、重複させない。
- R24のlive stale-reference guardも変更せず、責務分離を維持する。

### F2 — 新Issueなし

既存のformal experiment freezeとplanning guardの不変条件を補う回帰であり、独立した製品機能や長期作業単位を必要としない。

### F3 — ADRなし

新アーキテクチャではなく、既存のsnapshot identity契約を実運用で守る検証補強である。

## 7. 実証境界と次工程

R25は陽性の内部回帰証拠だが、formal Case 001 Arm Cの結果ではない。Case 001〜003の比較結果、第三者価値実証、AI-IR named-provider evidenceへ加算しない。

修正後もformal mainlineは変わらない。Case 001 Arm Cは、既知仮説から隔離したfresh contextと、frozen KJ Atlas UIの実操作が可能になった時点で実走する。この設計者チャットで代替回答を生成しない。
