# 継続dogfood R40 — branch差分とcurrent mainへのnet tree effectを分ける

Date: 2026-09-07
Canvas: `doc_kj_atlas_dogfood_r40.json`

## 1. Trigger

R39統合後、QA closeout branch `docs/lane-c-qa-pub-closeout-20260907` がPR #3072として再度openされ、そのままmainへmergeされた。

このbranchは、すでにPR #3064で同じ `QA-PUB-01-I18N-03` closeoutをmainへ取り込んだときのheadと同一だった。PR画面ではactive memo→done memoのrenameなど3ファイル相当の差分が見えていたが、#3072 merge後に直前main `20995afeee5d4e2ba93491dda5422b0500a1a17b` とmerge commit `29ddd1668d9102506d4b117751f4b9b1f666e8a2` を比較すると、**changed filesは0件**だった。

つまり、PRのmerge-baseから見えるbranch差分は残っていた一方、current mainにはその意味内容がすでに取り込まれており、統合のnet tree effectは空だった。結果としてproduct/repository stateは壊れなかったが、内容を変えないmerge commitだけが履歴へ追加された。

## 2. KJで分けて見えたもの

### A. branchが「変更を持つ」ことと、current mainへ「新しい変更を与える」ことは別である

PR #3072のheadは、過去のmerge-baseから見ればcloseout差分を持っていた。そのため通常のPR diffは空ではない。

しかしcurrent mainには、等価なcloseoutがPR #3064のsquash mergeとしてすでに存在した。commit ancestryやpatchの形は同一でなくても、tree stateとして必要な結果は成立済みだった。

したがってmerge判断では、

1. branchがmerge-base以後に何を変更したか
2. current mainと統合した結果、treeへ何が新たに残るか

を分ける必要がある。

### B. R22のstrong inversionとalready-applied deltaは同じではない

R22の既存checkerは、mainで削除済みのpathをbranchが復活させる、またはbranchがmainの現存pathを削除する、といったstrong path-level state reversalを対象にしている。

#3072ではそうしたstate inversionは起きていない。merge後treeは直前mainと同一であり、repository stateの退行はなかった。

したがって#3072を `main_deleted_branch_present` や `branch_deletes_main_present` と同じstrong failureへ分類するのは過剰である。今回の問題は**state corruptionではなく、already-applied deltaを再統合する履歴ノイズ／無意味なmerge**である。

### C. prospective merge treeは「PR diff」と別の観測面になる

current baseとheadに対し、実際にmergeした場合のtreeを事前計算し、そのtree idがbase tree idと同一なら、少なくともtree stateへのnet effectはない。

`git merge-tree --write-tree <base> <head>` はworking treeを書き換えずにprospective merge treeを計算できる。clean mergeで得たtree idがbaseのtree idと等しい場合、branchには履歴上の差分があっても、current mainへ適用すべきtree差分は残っていない。

この観測はPR diffを置き換えない。PR diffはbranchの由来や変更意図を読むために必要であり、prospective treeは「いま統合するとtreeに何が残るか」を見る別surfaceである。

### D. tree-noopはreview signalであり、自動failureではない

tree-noop mergeには、履歴上意味のある意図的mergeや、将来の監査上commit relation自体を残したい特殊ケースもあり得る。またconflict時はprospective treeを安全に決められない。

そのためR40では `prospectiveTreeNoop` をreportへ追加するが、既存 `--fail-on-strong` の対象には含めない。

- strong inversion: stateを壊し得るため既存どおりfail候補
- prospective tree-noop: mergeの必要性を人間が再確認するreview signal
- merge-tree conflict/error: no-opとは判定せずunknown

と分離する。

## 3. 中心所見

**branchのmerge-base差分と、current mainへ統合したときのnet tree effectは別である。pre-merge診断は「branchが何を変えたか」だけでなく「いまmergeするとtreeへ何が新たに残るか」も分けて観測する。**

これにより、stale branchが過去の変更を持っているだけなのか、mainへ状態反転を持ち込むのか、すでに適用済みでtree-noopなのかを同じ概念へ潰さずに扱える。

## 4. R22との関係

R40はR22を置き換えない。

- R22: `main_deleted_branch_present` / `branch_deletes_main_present` というstrong path-level inversionを検出する。
- R40: strong inversionが0でも、prospective merge treeがbase treeと同一になる **already-applied delta** をreview signalとして分ける。

したがってpre-merge diagnosticsは、

1. commit distance（情報のみ）
2. changed-path overlap（review）
3. strong path inversion（strong）
4. prospective tree-noop（review）

という複数の観測軸を持つ。

#3072は4の実陽性であり、3ではない。

## 5. 実装修正

既存 `01_Plans/check_stale_merge_reintroduction.py` を狭く拡張した。

- report schemaを2へ更新
- base commitのtree idを `baseTree` として記録
- `git merge-tree --write-tree base head` のclean resultを `prospectiveMergeTree` として記録
- prospective treeとbase treeが同一なら `prospectiveTreeNoop=true`
- conflict/error時は `prospectiveMergeTree=null`, `prospectiveTreeNoop=null`
- text outputではtree-noopを `[tree-noop review]` として明示
- `--fail-on-strong` の意味は変更しない

focused regression testでは、同じrename/closeoutをmainとfeatureが別commitとして実施したdivergent historyを作り、strongCount=0のままprospectiveTreeNoop=trueになることを固定した。net-new fileを持つbranchではfalseになるnegative controlも置いた。

## 6. Finding triage

- F0: PR #3072が、すでに#3064でmainへ適用済みのcloseout branchを再度mergeし、直前main→merge commit比較でchanged files=0となった実運用陽性。
- F1: 既存 `check_stale_merge_reintroduction.py` へprospective tree-noop review signalを追加する。
- F2: 新Issueなし。既存R22 diagnosticの狭い拡張で閉じる。
- F3: 新ADRなし。merge policyの決定変更ではなく、観測軸の追加である。

## 7. 境界

R40はtree-noop mergeを全面禁止しない。commit relationそのものに意味がある場合まで自動拒否しない。

また、PR diffが非空なら必ずnet-newである、あるいはprospective treeが同じならPR内容を読む必要がない、とは主張しない。両者は目的の違う観測面である。

`prospectiveTreeNoop` を恒久required checkへ昇格しない。今回1件の実陽性で観測価値は確認できたが、意図的no-opやmerge strategy差によるfalse positive運用データはまだない。R22の既存方針どおり、まずreview signalとして蓄積する。

## 8. 非主張

R40はcontinuous/internal dogfoodであり、Case 001〜003のformal cognitive comparison、AI-IR named-provider evidence、第三者product-value validationを代替しない。

formal P1の現在地は変わらない。次の正式工程はfresh isolated context + frozen KJ Atlas UIでのCase 001 Arm C実走である。
