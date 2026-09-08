# 継続dogfood R23 — 使われ続けた診断を、陽性証拠なしでrequired化しない

- Date: 2026-09-06
- Scope: 日常開発の自己分析。Case 001〜003の統制比較には含めない。
- Question: R22で追加したpre-merge stale-state診断は、その後の実開発で使われ続けたか。また、恒久required checkへ昇格させるだけの証拠は得られたか。
- Canvas: `doc_kj_atlas_dogfood_r23.json`
- Observation baseline: `main@a1474b5645c353c0ccbab748cbedddac5347c99c`
- Result class: 継続dogfoodの運用観察。formal Caseの結果、第三者価値実証、製品価値の証明には数えない。

## 1. 出発点

R22では、古いbranchそのものを禁止せず、`merge-base`からcurrent mainとbranchの双方が触れたpathを取り、状態の向きが逆転している強い候補だけをmerge前に絞る `check_stale_merge_reintroduction.py` を追加した。

`PROJECT-GOV-02` の完了境界は、script、synthetic test、R22 branch自身での実使用までだった。恒久required check化は明示的に対象外とし、**複数integrationで実際に使われるか、有益性と誤検知特性がどう見えるかを後から判断する**ことを残した。

したがってR23では、新しいstale判定ロジックを作らない。R22後のPR履歴から、診断が運用上使われた痕跡と、その結果だけを見る。

## 2. R22後の実使用

R22のPR #2899以降、少なくとも次の3件で `check_stale_merge_reintroduction.py --fail-on-strong` または同等のstale merge診断がbranch-only検証へ組み込まれた。

1. **PR #2902 — SaaS E2E台帳の同期**
   - planning/docs/triage検証と同じrunで診断を実行。
   - 結果は `strongCount=0`。
2. **PR #2961 — legacy Done旧root参照guard**
   - Issue lifecycle、planning、docs-check等とともに診断を実行。
   - 結果は `overlapCount=0 / strongCount=0 / findings=[]`。
3. **PR #2971 — Done配置READMEのpost-zero同期**
   - 同様にbranch-only検証へ診断を含めた。
   - 結果は `overlapCount=0 / strongCount=0 / findings=[]`。

対象はSaaS台帳、planning lifecycle回帰、運用文書同期と異なっている。したがって、R22のscriptがR22自身だけの自己検証で終わったとは言いにくい。

## 3. 「使われた」と「効いた」を分ける

ここで二つを混同しない。

- **使われ続けたか**: Yes。R22後の異なる変更で複数回、実際のbranch検証に入った。
- **実事故をmerge前に捕捉したか**: まだ観測できない。確認できた後続実使用はいずれもstrong finding 0件だった。

0件が続いたことは、少なくとも過剰なstrong判定で正常変更を毎回止めている様子がないこととは整合する。しかし、それだけで検出能力が実運用で実証されたとは言えない。

- branchが実際に健全だった可能性がある。
- path-level strong条件に該当する事故が起きなかった可能性がある。
- scriptが意味内部のstale再流入を対象外としているため、別種の事故は既存testや人間review側でしか見えない。

したがって、**negative runの反復は「無害に使える」側の証拠にはなるが、「事故を捕まえる」側の陽性証拠にはならない。**

## 4. current mainの統治境界

2026-09-06時点のmain branchはprotectedではなく、required status checkも設定されていない。直近の開発でも、必要な検証はbranch-onlyのone-shot workflowで実行し、成功後にworkflowを最終差分から削除する運用が繰り返されている。

この状況で、R23だけを理由に `PROJECT-GOV-02` を恒久required checkへ昇格すると、R22で意図的に分離した「低コストな補助診断」と「リポジトリ全体の恒久CI統治判断」を再び結びつけてしまう。

逆に、診断を使う価値がないとも言えない。#2902、#2961、#2971では既存のplanning/docs/test群と同居できており、追加のreview signalとして運用に馴染んでいる。

したがって現時点では、**optionalだが再利用されるpre-merge診断**という位置が最も証拠に合う。

## 5. KJ統合で立った中心構造

今回のカードを統合すると、中心に残ったのは次である。

> **「作ったか」ではなく「使われたか」を確認し、さらに「使われたか」と「事故を捕まえたか」も分ける。**

R22直後なら、scriptが一度動いたことしか分からなかった。R23では複数の異種PRで再利用されたため、運用上の生存は確認できた。一方、すべてnegative runであり、strong findingの実運用上の精度はまだ分からない。

ここでrequired化してしまうと、採用実績を検出実績へ読み替えることになる。逆に、positive hitがないから削除すると、低負担で世界像の交差を確認できる補助線を早く捨てすぎる。

現状は中間でよい。使い続け、陽性または誤検知の実例が出たときに次の判断材料へする。

## 6. Finding triage

### F0 — 生の観察として保持

- R22後、少なくとも3つの異なるPRでpre-merge stale-state診断が再利用された。
- 確認できた後続runはいずれもstrong finding 0件だった。
- 現在のmainはbranch protection / required status checkを持たない。

### F1 — `PROJECT-GOV-02`へ返す知見

- 「まず補助診断として実使用し、有益性と誤検知特性を見る」というR22の段階設計は、少なくとも再利用性の面では成立した。
- ただしstrong findingの実例がなく、required化を正当化する陽性証拠はまだない。

Done memoへ履歴を積み増す必要はない。PR #2902 / #2961 / #2971と本R23を後続運用証拠とし、Git/PRを実行履歴の正本にする。

### F2 — 新Issueなし

現時点では新しい欠陥を再現していない。`PROJECT-GOV-03`のようなrequired-check化Issueを先回りして起票しない。

次のF2候補は、たとえば次のどちらかが実際に観測されたときに初めて生じる。

- strong findingが実際のstale-state再流入をmerge前に捕捉し、通常reviewより前に意味のある停止点を作った。
- intentional changeをstrong findingとして頻繁に止め、無視される／運用負担になる誤検知が再現した。

### F3 — ADRなし

branch protection、required check、merge queue等の長期統治判断を変えるだけの証拠はまだない。

## 7. 次工程

1. branch-only検証を行う変更では、stale-state再流入の可能性があるときに既存scriptを引き続き使う。
2. `strong=0` は成功実績として数えるが、検出成功とは数えない。
3. strong findingが出た場合は、判定をそのまま正解扱いせずpathの意味差分を人間が確認する。
4. positive hit / false positiveのいずれかが実運用で得られた時点で、required化・条件調整・現状維持を再判断する。
5. formal Case 001 Arm Cの実行、AI-IRのnamed-provider測定、第三者価値実証を、この内部運用観察で代替しない。

R23は新しいguardを増やすラウンドではない。**既に作ったものが運用へ根付いたかを確かめ、証拠以上に制度化しないためのラウンド**とする。
