# 継続dogfood R24 — 同じpath文字列でも、現行参照と凍結座標を混同しない

- Date: 2026-09-06
- Scope: 日常開発の自己分析。Case 001〜003の統制比較には含めない。
- Question: frozen dogfood source manifestが保持する旧Issue root pathと、legacy Done-root reference guardが禁じる現行参照は、同じ文字列だから同じ意味として扱ってよいか。
- Canvas: `doc_kj_atlas_dogfood_r24.json`
- Observation baseline: `main@45515d94c5ef9b93ec655fffdaae836504077a50`
- Result class: 実際に現行mainのplanning unittest baseline failureとして露呈したguard契約回帰。formal Case、第三者価値実証、AI-IR named-provider測定の結果には数えない。

## 1. 出発点

PR #2994のbranch-only検証では、変更対象のfocused backend、docs contract、Issue lifecycle、diff hygieneはgreenだった一方、repository-wide planning unittest suiteをblocking対象から外した。

理由として、現行main自身に、#2993までに保存されたfrozen cognitive dogfood source manifestとlegacy Done-root reference guardの間の既知baseline failureがあることが明記された。

これは新しい事前検証の不足ではない。既に存在するguardが、既に存在する凍結manifestを誤ってfailureへ分類し、通常のplanning suiteを赤くしている実回帰である。

## 2. 二つのpathが同じ文字列になった経緯

PR #2961で追加されたlegacy Done-root reference guardは、R18でactive rootから`done/`へ移した58 memoについて、旧path `01_Plans/issues/<name>` がtracked fileへ再出現しないことを`git grep`で守るものだった。

このguardが守りたいものは、現在のrepositoryに対する**現行参照**である。完了memoへ現在アクセスする文書が、退役済みactive-root pathを指していれば参照切れまたはlifecycle driftになる。

一方、Case 001〜003のRound 1 source manifestでは、各sourceを次の組で固定している。

- `productCommit = 2232b3bb26647e5c4a083f55bdbf83c161698649`
- `commonSources[].path`
- `commonSources[].blobSha`

ここで`path`はcurrent mainへのリンクではない。固定commit上でそのblobが存在した**歴史座標**である。

R18後にIssue memoが`done/`へ移動しても、frozen commit上では旧active-root pathに存在していた。そのためmanifestだけを現在位置へ書き換えると、固定commit上に存在しないpathを記録することになり、凍結資料の再構成契約を壊す。

2026-09-06のcommit `0c5b67ec29089b2bf01af75c52778009af54efac` は、この理由でCase 001〜003 manifestの該当pathを`done/`からfrozen commit当時のactive-root pathへ戻した。blob SHAや資料選択は変えていない。

## 3. failureの本質

文字列だけを見ると、どちらも同じ `01_Plans/issues/<name>` である。

しかし意味は異なる。

- **現行参照**: 「今このrepositoryで、そのmemoへ行くにはここを見る」というnavigation/lifecycle上の参照。
- **凍結座標**: 「固定した過去commitのこのpathに、このblobがあった」というsnapshot identity。

legacy guardの最初のR18-specific testは、この二つを区別せずtracked file全体へ完全一致grepを行う。そのため、正しく保存されたfrozen coordinateまでstale live referenceとして数え、baseline failureになった。

ここでmanifestを再び`done/`へ変えるのは、テストをgreenにする代わりに実験の凍結性を壊す。逆に`dogfood/`全体をgrep対象外にすると、日常dogfood文書に本当にstaleなcurrent referenceが入った場合まで見逃す。

必要なのは、例外の範囲を**場所**ではなく**意味構造**で決めることである。

## 4. 修正契約

`test_legacy_done_root_references.py`へ、structured frozen source coordinateの判定を追加する。

例外として扱うには、少なくとも次をすべて満たす必要がある。

1. 対象ファイルが事前登録済みのCase 001〜003 Round 1 source manifestのいずれかである。
2. `schemaVersion=1`、`round=1`である。
3. `productCommit`がfrozen product commit `2232b3bb...` と完全一致する。
4. 対象文字列が`commonSources[].path`として存在し、同じentryに40桁の`blobSha`がある。
5. pathが旧`01_Plans/issues/<name>`である。
6. current mainでは同名memoが`done/<name>`に存在し、旧active-root fileは存在しない。

この条件から機械的にexception setを作る。

したがって、一般Markdown、通常JSON、current operational docs、別manifest、product commitが変わったmanifest等へ旧root pathが現れても自動では許可されない。

また、R15/R18等の非構造化されたdated provenanceは従来どおり明示allow-listでreviewする。Case 003 manifestに手書きされていた同種の例外だけはstructured判定へ吸収し、同じ概念を二重管理しない。

## 5. KJ統合で立った中心構造

今回のカードをまとめると、中心に残るのは次である。

> **同じpath文字列でも、「いまの場所を指す参照」と「過去の世界を固定する座標」は別の意味を持つ。**

pathを単なる文字列として正規化すると、lifecycle整合性を守るguardとsnapshot再現性を守るmanifestが互いを壊す。

これは「例外を増やす」問題ではない。どの世界・どの時点を指しているpathなのかを、周囲の契約から判別する問題である。

KJ Atlas自身が長期探究で時点差・訂正・系譜を重視している以上、開発guardでもcurrent stateとhistorical coordinateを同じ名前空間の一文字列へ潰さないことが重要になる。

## 6. Finding triage

### F0 — 生の観察として保持

- PR #2994でrepository-wide planning unittestの現行main baseline failureが明示された。
- failureはfrozen source manifestとlegacy Done-root guardの契約衝突から生じる。
- commit `0c5b67ec...`でfrozen manifest pathを正したこと自体は必要だった。

### F1 — 既存planning lifecycle guardへ返す

- legacy Done-root guardの目的は維持する。
- live current referenceとstructured frozen coordinateを分離する。
- frozen manifestをcurrent canonical pathへ書き換えてgreen化しない。
- dogfoodディレクトリ全体のblanket exemptionを作らない。

### F2 — 新Issueなし

原因と修正境界が既存のguard test内で完結し、別の製品/アーキテクチャ課題を必要としないため、新Issueは起票しない。

### F3 — ADRなし

新しい長期アーキテクチャ判断ではなく、既存の「current lifecycle整合」と「frozen experiment identity」の二契約を両立させるguard補正である。

## 7. 次の工程

- focused legacy Done-root testをgreenへ戻す。
- 可能ならrepository-wide planning unittestを再実行し、#2994で既知baseline failureとして除外された状態を解消する。
- strong false negativeを作らないよう、structured frozen coordinate以外の旧root referenceは従来どおりfailさせる。
- このR24をformal Case 001 Arm Cの代替実行にはしない。Arm Cは引き続きfresh contextで実走する。
