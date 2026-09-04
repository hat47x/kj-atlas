# 継続dogfood R22 — 古いbranchを禁止せず、merge前に状態反転を見つける

- Date: 2026-09-04
- Scope: 日常開発の自己分析。Case 001〜003の統制比較には含めない。
- Question: 急速な並行開発の中で、古いbranch状態がcurrent mainへ再流入する事象を、正当な並行変更まで止めずにどう早期発見するか。
- Canvas: `doc_kj_atlas_dogfood_r22.json`
- Result class: 継続dogfoodの実行改善記録。formal Caseの結果、第三者価値実証、製品価値の証明には数えない。

## 1. 出発点

直近のmainでは、単一機能の不具合では説明しにくい「いったん正本から消えた、または更新された状態が後続branchから戻る」事象が複数の面で観測された。

1. `DX-CI-STALE-MERGE-ONESHOT-01`
   - mergeMethod実装時に成功後削除されたone-shot workflow/scriptが、後続mainへ再び残った。
2. `DOC-ISSUE-LIFECYCLE-REINTRODUCED-COPY-01`
   - `done/`へ整理済みのIssue旧コピーがactive rootへ再出現した。
3. `DX-FRONTEND-MERGE-METHOD-DRIFT-01`
   - 旧branch由来の再mergeで、`mergeMethod`のimport/field/parser blockが二重化し、古いfixtureとの不整合も重なってTypeScript typecheckが失敗した。

それぞれの局所guardは機能した。Issue lifecycle validatorやtypecheckは不整合を検出し、PR #2897では退役済みone-shot資産の**正確な10path**を再導入不可として回帰テストへ固定した。

したがって問いは「guardがない」ではない。

> **既知の事故を局所的に封じることに加えて、まだ名前の付いていない再流入候補をmerge前にどう見つけるか。**

## 2. `PROJECT-GOV-01`が解いたことと残差

既存`PROJECT-GOV-01`は、数千のremote branchをcanonical / duplicate / stale / unknownへ分類し、最新mainを正本入力とし、古いbranchからの再修正や二重ADRを避ける運用を整えた。

ただし、その受入条件と実装タスクは棚卸し・分類・削除推奨が中心である。merge直前に、branchが分岐後のmainで削除・更新されたpathをどう持っているかを機械診断する契約は持っていない。

そのため今回の残差は、既存Issueを作り直すことではなく、**棚卸し後も残る実際のintegration boundary**にある。

## 3. commit距離をstale判定にしない

R21で確認したとおり、branchとmainのcommit距離が大きいことは「現在性を確認すべき」という警告にはなるが、それ自体は意味ドリフトではない。

- mainが1000 commits進んでも、branchが触るpathと無関係なら統合可能な場合がある。
- mainとbranchが同じpathを変更していても、別行・別意味で正常に統合できる場合がある。
- 逆に、commit数が少なくても、mainで削除したpathをbranchが持ち戻せば強い再流入候補になる。

したがって、stale度の単一スコアや「N commits behindなら拒否」は採らない。

## 4. merge-baseから双方の世界像を見る

最小の診断単位は、`merge-base`からcurrent mainとbranchがそれぞれ何を変えたかである。

1. `merge-base..base` の変更pathを取る。
2. `merge-base..head` の変更pathを取る。
3. 双方が触れたpathをoverlapとして残す。
4. pathの現在存在状態も見る。

このうち、path-levelで特に強い状態反転は二つである。

- **main_deleted_branch_present**
  - mainはmerge-base以降にpathを削除した。
  - branchもそのpathへ変更を持ち、branch treeにはまだ存在する。
  - いったん退役したassetや旧文書が戻る候補になる。
- **branch_deletes_main_present**
  - mainはmerge-base以降にpathを変更し、現在も存在する。
  - branchはそのpathを削除している。
  - main側で育った正本を古いbranchの削除判断で落とす候補になる。

双方が同じpathを変更しただけなら`overlap_review`であり、自動失敗にはしない。

## 5. path-level診断で解けないこと

`DX-FRONTEND-MERGE-METHOD-DRIFT-01`のように、同じsource fileの中へ既存field/importを二重挿入する問題は、pathが存在するかだけでは意味まで判定できない。

したがって今回の診断は、次を置き換えない。

- TypeScript/Python等のtypecheck。
- unit / integration / E2E test。
- Issue lifecycle validator。
- PR #2897の既知退役path guard。
- 人間によるdiff review。

新しい診断は、その前段で「このbranchはcurrent mainとどこで世界像が交差しているか」を狭く知らせる役割に留める。

## 6. 実装

`PROJECT-GOV-02`をF2として起票し、次を追加した。

- `01_Plans/check_stale_merge_reintroduction.py`
  - base/head/merge-baseと両側commit数を表示。
  - 双方変更pathを列挙。
  - strong path-level状態反転を二分類。
  - `--json`で機械可読化。
  - `--fail-on-strong`を指定した場合だけstrong findingをexit 2へする。
- `01_Plans/test_check_stale_merge_reintroduction.py`
  - 非重複。
  - main削除→branch再出現。
  - 同一pathのbenign overlap。
  - main更新→branch削除。
  - commit距離だけ大きいケース。

恒久required checkにはまだしない。まずこのR22 branch自身をcurrent mainへ統合する前に実使用し、有用性と誤検知特性を見る。

## 7. KJ統合で立った中心構造

今回のカードをまとめると、中心に残ったのは次である。

> **古いbranchを問題にするのではなく、merge直前にbranchとcurrent mainの「状態の向き」が逆転している場所を見つける。**

branch ageを禁止規則へ変えると、独立した正当な作業まで止める。逆に、各テストが壊れてから直すだけでは、Issue・workflow・source codeという異なる面で同じ再流入を繰り返す。

既知pathは局所guardで強く守り、未知のpathはmerge-base診断で候補を絞り、意味内部は既存testと人間判断で確かめる。強度の異なるguardを重ねる方が、現在の並行開発には合う。

## 8. Finding triage

### F0 — 生の観察として保持

- stale state再流入はworkflow、Issue lifecycle、frontend sourceの3面で再現した。
- 各面の事後guardは実際に不整合を検出している。
- PR #2897により、既知one-shot 10pathの再出現は現在mainで直接guardされるようになった。

### F1 — `PROJECT-GOV-01`へ返す知見

- 「latest mainを入力にする」「stale/duplicate branchを分類する」という既存判断は妥当だった。
- ただし棚卸しだけでは、長寿命branchを後からmergeするintegration momentの差分確認まで担わないことが実使用で明らかになった。

### F2 — `PROJECT-GOV-02`

新Issue `PROJECT-GOV-02` を起票する。

対象はpre-merge diagnosticのみで、branch cleanupや全面禁止ではない。synthetic testとこのbranchでの実使用までをDone境界とし、恒久required check化は結果を見て別判断にする。

### F3 — ADRなし

長期的なbranch protection、merge queue、required checkの統治判断まではまだ証拠が足りない。まず診断を使い、誤検知・見逃し・人間のreview負荷を観察する。

## 9. 次工程

1. scriptとsynthetic testsをbranch-only one-shotで検証する。
2. planning/docs/triageを同じrunで確認する。
3. merge直前の最新mainに対し、本scriptを実使用する。
4. strong findingがあれば自動的に正誤を決めず、そのpathの意味差分を確認する。
5. 実使用結果を本R22と`PROJECT-GOV-02`へ戻す。
6. 有益でも、直ちに恒久CIへ昇格させない。複数integrationで再現する場合に次段を判断する。

R22はformal Case 001 Arm Cを代替しない。formal比較は引き続きfresh context + frozen runtimeで別レーンとして実走する。
